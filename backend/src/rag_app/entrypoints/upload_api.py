"""Finite TXT/Markdown upload routes; authorization always precedes the body.

The binary PUT never enters the JSON guard and never calls ``Request.body`` or
``UploadFile``: the controller takes the physical slot first, then streams
bounded chunks to the supervised writer.  No PostgreSQL transaction or OS
lock is held while a chunk is read.
"""

from __future__ import annotations

import hmac
import hashlib
import time
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from rag_app.application.upload_service import (
    BeginResult, UploadRequestInput, UploadService, UploadView,
)
from rag_app.adapters.original_store import StoreUnavailable
from rag_app.contracts.errors import SafeError
from rag_app.contracts.upload import UploadResponse
from rag_app.entrypoints.contract_probe import failure_response
from rag_app.entrypoints.json_guard import BoundedJsonError, read_bounded_json
from rag_app.modules.library.sessions import (
    AuthContext, AuthenticationError, digest_secret, validate_secret,
)
from rag_app.modules.library.uploads import (
    LimitExceeded, UploadInputError, UploadLimits, UploadState,
    allow_actions_for, candidate_projection, index_generation_projection,
    job_projection, parse_uuidv7, validate_declared_bytes, validate_filename,
    validate_format, validate_sha256, validate_stable_id, validate_title,
)


CREATE_PATH = "/api/v1/web/document-candidates"
ITEM_PATH = "/api/v1/web/document-candidates/{candidate_id}"
ORIGINAL_PATH = "/api/v1/web/document-candidates/{candidate_id}/original"

SESSION_COOKIE = "rag_session"
CSRF_HEADER = "x-csrf-token"
ORIGIN_HEADER = "origin"


class RequestRejected(Exception):
    """A finite boundary rejection; the public code is the only payload."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _headers(request: Request) -> list[tuple[bytes, bytes]]:
    return list(request.scope.get("headers", []))


def _single(headers: list[tuple[bytes, bytes]], name: str) -> bytes | None:
    lowered = name.encode("ascii")
    found = [value for key, value in headers if key.lower() == lowered]
    return found[0] if len(found) == 1 else None


def _cookies(headers: list[tuple[bytes, bytes]]) -> dict[str, str]:
    values: dict[str, str] = {}
    for key, value in headers:
        if key.lower() != b"cookie":
            continue
        for part in value.decode("latin-1").split(";"):
            name, _, raw = part.strip().partition("=")
            if name:
                values.setdefault(name, raw)
    return values


def _channel(
    headers: list[tuple[bytes, bytes]],
) -> tuple[str, str, str | None]:
    """Return one channel and its secrets; both channels at once is a conflict."""

    cookie = _cookies(headers).get(SESSION_COOKIE)
    authorizations = [
        value for key, value in headers if key.lower() == b"authorization"
    ]
    if cookie and authorizations:
        raise RequestRejected("AUTH_CHANNEL_CONFLICT")
    if len(authorizations) > 1:
        raise RequestRejected("CREDENTIAL_INVALID")
    bearer = None
    if authorizations:
        parts = authorizations[0].decode("latin-1").split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
            raise RequestRejected("CREDENTIAL_INVALID")
        bearer = parts[1]
    if cookie:
        return "web", cookie, None
    if bearer:
        return "program", "", bearer
    raise RequestRejected("AUTH_REQUIRED")


def _require_origin(request: Request, expected: str | None) -> None:
    if not expected:
        raise RequestRejected("ACTION_FORBIDDEN")
    supplied = _single(_headers(request), ORIGIN_HEADER)
    if supplied is None:
        raise RequestRejected("ACTION_FORBIDDEN")
    if not hmac.compare_digest(supplied, expected.encode("utf-8")):
        raise RequestRejected("ACTION_FORBIDDEN")


def _binary_content_type(request: Request) -> None:
    headers = _headers(request)
    media = _single(headers, "content-type")
    encoding = _single(headers, "content-encoding")
    length = _single(headers, "content-length")
    transfer = _single(headers, "transfer-encoding")
    if media is None or media.strip().lower() != b"application/octet-stream":
        raise RequestRejected("UNSUPPORTED_MEDIA_TYPE")
    if encoding is not None and encoding.strip().lower() != b"identity":
        raise RequestRejected("UNSUPPORTED_CONTENT_ENCODING")
    if length is None and transfer is None:
        raise RequestRejected("REQUEST_BODY_LIMIT_EXCEEDED")
    if length is not None:
        if not length.isdigit():
            raise RequestRejected("VALIDATION_ERROR")
        if len(length) > 20:
            raise RequestRejected("REQUEST_BODY_LIMIT_EXCEEDED")


def _declared_length(request: Request) -> int | None:
    raw = _single(_headers(request), "content-length")
    if raw is None:
        return None
    return int(raw)


class _StreamBudget:
    """Monotonic bounded reader; stops on excess, deadline or disconnect."""

    def __init__(
        self, request: Request, *, declared: int, max_bytes: int,
        timeout_s: float,
    ) -> None:
        self._request = request
        self._declared = declared
        self._max_bytes = max_bytes
        self._deadline_s = timeout_s
        self._received = 0

    @property
    def received(self) -> int:
        return self._received

    def _limit(self) -> int:
        return min(self._declared, self._max_bytes)

    async def pump(self, sink: Any) -> None:
        started = time.monotonic()
        iterator = self._request.stream()
        while True:
            if time.monotonic() - started > self._deadline_s:
                raise RequestRejected("UPLOAD_EXPIRED")
            try:
                chunk = await iterator.__anext__()
            except StopAsyncIteration:
                return
            except SafeError:
                raise
            except Exception:
                raise RequestRejected("REQUEST_STREAM_ERROR") from None
            if not chunk:
                continue
            if self._received + len(chunk) > self._limit():
                raise RequestRejected("UPLOAD_CONTENT_CONFLICT")
            self._received += len(chunk)
            # The native writer applies backpressure; keep the event loop free.
            await run_in_threadpool(sink.feed, chunk)


def _job_projection(job: dict[str, Any] | None) -> dict[str, Any] | None:
    if job is None:
        return None
    return job_projection(
        job_id=job["job_id"], attempt=job["attempt"],
        job_state=job["job_state"], stage_code=job["stage_code"],
        hard_deadline=job["hard_deadline"],
        lease_until=job["lease_until"], updated_at=job["created_at"],
    )


def _response(
    request_id: str, *, replayed: bool, view: UploadView, status_code: int,
) -> JSONResponse:
    record = view.record
    candidate = view.candidate
    state = candidate["upload_state"]
    job = view.job
    dto = UploadResponse.model_validate({
        "schema_version": "upload.v1",
        "request_id": request_id,
        "status": (
            "completed"
            if state == UploadState.ORIGINAL_COMMITTED.value
            else "in_progress"
        ),
        "replayed": replayed,
        "upload_operation_id": record["upload_operation_id"],
        "document_id": record["document_id"],
        "accepted_at": record["accepted_at"],
        "original_sha256": record["original_sha256"],
        "original_bytes": record["original_bytes"],
        "original_url": (
            f"/api/v1/web/document-candidates/"
            f"{record['candidate_id']}/original"
        ),
        # Upload completion never publishes a ready/active version.
        "active_version": None,
        "candidate": candidate_projection(
            candidate_id=candidate["candidate_id"],
            document_version_id=candidate["document_version_id"],
            upload_state=state,
            processing_state=candidate["processing_state"],
            upload_start_by=candidate["upload_start_by"],
            upload_hard_deadline=candidate["upload_hard_deadline"],
            retained_original_bytes=candidate["retained_original_bytes"],
            updated_at=candidate["updated_at"],
        ),
        "job": _job_projection(job),
        "index_generation": index_generation_projection(),
        "cleanup": None,
        "allowed_actions": allow_actions_for(
            state, None if job is None else job["job_state"],
        ),
    })
    return JSONResponse(
        dto.model_dump(mode="json", exclude_none=False),
        status_code=status_code,
    )


def register_upload_routes(
    app: FastAPI, *, settings: Any,
) -> None:
    """Register the finite routes; each handler refuses unless explicitly open."""

    enabled = bool(getattr(settings, "uploads_enabled", False))

    def require_enabled() -> None:
        if not enabled:
            raise RequestRejected("RESOURCE_UNAVAILABLE")

    def runtime_of(request: Request) -> Any:
        runtime = getattr(request.app.state, "runtime", None)
        if runtime is None:
            raise RequestRejected("STARTUP_DEPENDENCY_UNAVAILABLE")
        return runtime

    def service_of(runtime: Any) -> UploadService:
        return UploadService(
            runtime.uow, runtime.upload_repository,
            store=runtime.original_store(), limits=runtime.upload_limits(),
        )

    def session_of(request: Request, runtime: Any) -> dict[str, Any]:
        """Identity and channel checks only; this runs before any request body."""

        kind, session_secret, bearer = _channel(_headers(request))
        if kind != "web":
            # Program credentials are read-only and cannot upload.
            raise RequestRejected("ACTION_FORBIDDEN")
        _require_origin(request, getattr(runtime.settings, "allowed_origin", None))
        csrf = _single(_headers(request), CSRF_HEADER)
        if csrf is None:
            raise RequestRejected("ACTION_FORBIDDEN")
        try:
            secret = validate_secret(session_secret)
        except AuthenticationError:
            raise RequestRejected("CREDENTIAL_INVALID") from None
        session = service_of(runtime).authenticate_session(secret)
        supplied = digest_secret(csrf.decode("latin-1"))
        if not hmac.compare_digest(session["csrf_digest"], supplied):
            raise RequestRejected("ACTION_FORBIDDEN")
        return session

    def context(
        session: dict[str, Any], *, space_id: str, knowledge_base_id: str,
    ) -> AuthContext:
        if session["space_id"] != space_id:
            raise RequestRejected("RESOURCE_UNAVAILABLE")
        return AuthContext(
            account_id=session["account_id"], session_id=session["session_id"],
            csrf_digest=session["csrf_digest"], epoch=session["epoch"],
            channel="web", space_id=space_id,
            knowledge_base_ids=(knowledge_base_id,),
        )

    def reject(exc: Exception, request_id: str) -> JSONResponse:
        if isinstance(exc, RequestRejected):
            return failure_response(request_id, exc.code)
        if isinstance(exc, SafeError):
            return failure_response(request_id, exc.code)
        return failure_response(request_id, "INTERNAL_ERROR")

    @app.post(CREATE_PATH, response_model=UploadResponse, tags=["uploads"])
    async def create_candidate(request: Request):
        request_id = request.state.request_id
        try:
            require_enabled()
            runtime = runtime_of(request)
            session = session_of(request, runtime)
            payload = await read_bounded_json(request)
            fields = _parse_create(payload, runtime.upload_limits())
            ctx = context(
                session, space_id=fields.space_id,
                knowledge_base_id=fields.knowledge_base_id,
            )
            created, view = service_of(runtime).create_or_replay(ctx, fields)
            return _response(
                request_id, replayed=not created, view=view,
                status_code=201 if created else 200,
            )
        except BoundedJsonError as exc:
            return failure_response(request_id, exc.code)
        except (RequestRejected, SafeError) as exc:
            return reject(exc, request_id)
        except (ValidationError, ValueError):
            return failure_response(request_id, "VALIDATION_ERROR")
        except Exception:
            return failure_response(request_id, "INTERNAL_ERROR")

    @app.get(ITEM_PATH, response_model=UploadResponse, tags=["uploads"])
    async def read_candidate(request: Request, candidate_id: str):
        request_id = request.state.request_id
        try:
            require_enabled()
            runtime = runtime_of(request)
            validate_stable_id(candidate_id, name="candidate_id")
            session = session_of(request, runtime)
            service = service_of(runtime)
            scope = service.candidate_scope(candidate_id)
            ctx = context(
                session, space_id=scope["space_id"],
                knowledge_base_id=scope["knowledge_base_id"],
            )
            view = service.get(ctx, candidate_id)
            return _response(
                request_id, replayed=True, view=view, status_code=200,
            )
        except (RequestRejected, SafeError) as exc:
            return reject(exc, request_id)
        except (UploadInputError, ValidationError, ValueError):
            return failure_response(request_id, "VALIDATION_ERROR")
        except Exception:
            return failure_response(request_id, "INTERNAL_ERROR")

    @app.put(ORIGINAL_PATH, response_model=UploadResponse, tags=["uploads"])
    async def upload_original(request: Request, candidate_id: str):
        request_id = request.state.request_id
        runtime = None
        slot = None
        writer = None
        begun: BeginResult | None = None
        try:
            require_enabled()
            runtime = runtime_of(request)
            validate_stable_id(candidate_id, name="candidate_id")
            session = session_of(request, runtime)
            service = service_of(runtime)
            scope = service.candidate_scope(candidate_id)
            ctx = context(
                session, space_id=scope["space_id"],
                knowledge_base_id=scope["knowledge_base_id"],
            )
            service.authorize_candidate(ctx, candidate_id)
            _binary_content_type(request)
            declared = _declared_length(request)
            store = runtime.original_store()
            limits: UploadLimits = runtime.upload_limits()
            slot = store.slot()
            await run_in_threadpool(slot.acquire, wait_s=limits.slot_wait_s)
            begun = await run_in_threadpool(
                service.begin_writer, ctx, candidate_id,
            )
            if begun.replay:
                await _verify_replay(
                    request, begun, declared,
                )
                view = await run_in_threadpool(service.get, ctx, candidate_id)
                return _response(
                    request_id, replayed=True, view=view, status_code=200,
                )
            await run_in_threadpool(
                store.prepare_paths, begun.record["asset_prefix"],
            )
            writer = _new_writer(
                begun, slot_fd=slot.fileno, limits=limits,
            )
            with writer:
                await _StreamBudget(
                    request, declared=begun.max_bytes,
                    max_bytes=begun.max_bytes,
                    timeout_s=max(1.0, float(limits.lease_s)),
                ).pump(writer)
                actual_bytes = await run_in_threadpool(writer.finish)
            if not writer.stop_proven:
                raise RequestRejected("UPLOAD_IN_PROGRESS")
            actual_length, actual_sha = actual_bytes
            if declared is not None and declared != actual_length:
                raise RequestRejected("UPLOAD_CONTENT_CONFLICT")
            _, view = await run_in_threadpool(
                service.complete, ctx, candidate_id,
                attempt=begun.attempt, claim_token=begun.claim_token,
                original_sha256=actual_sha, original_bytes=actual_length,
            )
            return _response(
                request_id, replayed=False, view=view, status_code=200,
            )
        except (RequestRejected, SafeError) as exc:
            await _abandon(runtime, candidate_id, begun, writer)
            return reject(exc, request_id)
        except StoreUnavailable as exc:
            await _abandon(runtime, candidate_id, begun, writer)
            return failure_response(request_id, exc.code)
        except (UploadInputError, ValidationError, ValueError):
            await _abandon(runtime, candidate_id, begun, writer)
            return failure_response(request_id, "VALIDATION_ERROR")
        except Exception:
            await _abandon(runtime, candidate_id, begun, writer)
            return failure_response(request_id, "INTERNAL_ERROR")
        finally:
            if writer is not None:
                try:
                    writer.abort()
                except Exception:
                    pass
            # The slot is released only after the writer has proven it stopped.
            if slot is not None and slot.held:
                if writer is None or writer.stop_proven:
                    slot.release()
                else:
                    # Drop this process's reference; the inherited descriptor
                    # keeps the same lock held while the child is still alive.
                    slot.close()


async def _verify_replay(
    request: Request, begun: BeginResult, declared: int | None,
) -> None:
    import codecs

    digest = hashlib.sha256()
    decoder = codecs.getincrementaldecoder("utf-8")("strict")
    length = 0
    iterator = request.stream()
    limit = begun.max_bytes
    async for chunk in iterator:
        if not chunk:
            continue
        length += len(chunk)
        if length > limit:
            raise RequestRejected("UPLOAD_CONTENT_CONFLICT")
        digest.update(chunk)
        try:
            decoder.decode(chunk, final=False)
        except UnicodeDecodeError:
            raise RequestRejected("UPLOAD_CONTENT_CONFLICT") from None
    try:
        decoder.decode(b"", final=True)
    except UnicodeDecodeError:
        raise RequestRejected("UPLOAD_CONTENT_CONFLICT") from None
    if declared is not None and declared != length:
        raise RequestRejected("UPLOAD_CONTENT_CONFLICT")
    if length != begun.record["original_bytes"]:
        raise RequestRejected("UPLOAD_CONTENT_CONFLICT")
    if digest.hexdigest() != begun.record["original_sha256"]:
        raise RequestRejected("UPLOAD_CONTENT_CONFLICT")


def _new_writer(begun: BeginResult, *, slot_fd: int, limits: UploadLimits):
    from rag_app.adapters.upload_supervisor import SupervisedUploadWriter

    return SupervisedUploadWriter(
        staging=begun.paths["staging"], final=begun.paths["final"],
        lifecycle_lock=begun.paths["lock"], slot_fd=slot_fd,
        max_bytes=begun.max_bytes, page_bytes=limits.page_bytes,
        chunk_bytes=limits.chunk_bytes,
        absolute_deadline_monotonic=(
            time.monotonic()
            + max(1.0, (begun.hard_deadline - begun.now).total_seconds())
        ),
        no_progress_s=float(limits.no_progress_s),
        stop_grace_s=float(limits.stop_grace_s),
    )


async def _abandon(
    runtime: Any, candidate_id: str, begun: BeginResult | None, writer: Any,
) -> None:
    """Keep reserved bytes; clear only a lease whose writer is not still live."""

    if runtime is None or begun is None or begun.replay:
        return
    if writer is not None and not writer.stop_proven:
        # An unproven writer keeps its claim; recovery must not pretend clean.
        return
    try:
        service = UploadService(
            runtime.uow, runtime.upload_repository,
            store=runtime.original_store(), limits=runtime.upload_limits(),
        )
        await run_in_threadpool(
            service.record_abandoned_writer, candidate_id,
            attempt=begun.attempt, claim_token=begun.claim_token,
        )
    except Exception:
        return


def _parse_create(
    payload: dict[str, Any], limits: UploadLimits,
) -> UploadRequestInput:
    allowed = {
        "upload_operation_id", "space_id", "knowledge_base_id", "filename",
        "title", "format", "declared_bytes", "original_sha256",
    }
    unknown = set(payload) - allowed
    if unknown:
        raise UploadInputError("unknown field")
    if "upload_operation_id" not in payload:
        raise UploadInputError("upload_operation_id is required")
    try:
        operation_id = payload["upload_operation_id"]
        canonical_id, _ = parse_uuidv7(operation_id)
        space_id = validate_stable_id(payload.get("space_id"), name="space_id")
        kb_id = validate_stable_id(
            payload.get("knowledge_base_id"), name="knowledge_base_id",
        )
        filename = validate_filename(payload.get("filename"))
        title = validate_title(payload.get("title"), filename=filename)
        upload_format = validate_format(payload.get("format"))
        declared = validate_declared_bytes(payload.get("declared_bytes"), limits)
        sha = validate_sha256(payload.get("original_sha256"))
    except LimitExceeded as exc:
        raise RequestRejected(exc.code) from None
    except UploadInputError:
        raise RequestRejected("VALIDATION_ERROR") from None
    return UploadRequestInput(
        upload_operation_id=canonical_id, space_id=space_id,
        knowledge_base_id=kb_id, filename=filename, title=title,
        format=upload_format, declared_bytes=declared, original_sha256=sha,
    )
