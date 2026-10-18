"""Upload use cases: identity facts, idempotent intent and a fenced commit.

Every method owns one short ``UnitOfWork``.  No method reads a request body,
opens a file or waits for an OS lock while a transaction is open; the HTTP
entrypoint performs that work between calls and then asks this service to
record a fact.

Lock order (C4): account SH -> space SH -> knowledge base SH -> candidate ->
capacity.  A candidate's space/KB is resolved *before* the transaction's lock
set is taken, so no lock is ever acquired out of order and no parent lock is
requested after a child lock.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Protocol

from rag_app.application.uow import UnitOfWork
from rag_app.contracts.errors import SafeError
from rag_app.modules.library.sessions import (
    AuthContext, AuthenticationError, check_csrf, digest_secret,
)
from rag_app.modules.library.uploads import (
    JOB_ABSOLUTE_WINDOW, KeyExpired, UploadLimits, UploadState,
    canonical_upload_input, check_key_window, claim_digest,
    effective_hard_deadline, input_digest, new_asset_prefix, new_claim_token,
    new_row_id, parse_uuidv7,
)


class Repository(Protocol):
    def current_time(self) -> datetime: ...


class RepositoryFactory(Protocol):
    def __call__(self, session: Any) -> Any: ...


class OriginalStorePort(Protocol):
    def paths(self, prefix: str) -> dict[str, str]: ...

    def prepare_paths(self, prefix: str) -> dict[str, str]: ...

    def free_bytes(self) -> int: ...

    def discard_staging(self, staging: str) -> bool: ...


@dataclass(frozen=True, slots=True)
class UploadRequestInput:
    upload_operation_id: str
    space_id: str
    knowledge_base_id: str
    filename: str
    title: str
    format: str
    declared_bytes: int
    original_sha256: str | None


@dataclass(frozen=True, slots=True)
class BeginResult:
    record: dict[str, Any]
    attempt: int
    claim_token: str
    paths: dict[str, str]
    replay: bool
    max_bytes: int
    now: datetime
    hard_deadline: datetime


@dataclass(frozen=True, slots=True)
class UploadView:
    record: dict[str, Any]
    candidate: dict[str, Any]
    version: dict[str, Any] | None
    job: dict[str, Any] | None


def _business(code: str) -> SafeError:
    return SafeError(code)


class UploadService:
    def __init__(
        self, uow: UnitOfWork, stores: RepositoryFactory, *,
        store: OriginalStorePort, limits: UploadLimits,
    ) -> None:
        self._uow = uow
        self._stores = stores
        self._store = store
        self._limits = limits

    # -- identity --------------------------------------------------------

    def authenticate_session(self, secret: str) -> dict[str, Any]:
        """Resolve one opaque cookie secret to server-side session facts."""

        digest = digest_secret(secret)
        with self._uow.transaction() as session:
            store = self._stores(session)
            row = store.load_session(digest)
            if row is None:
                raise _business("CREDENTIAL_INVALID")
            now = store.current_time()
            valid = (
                row["revoked_at"] is None
                and now < row["idle_expires_at"]
                and now < row["absolute_expires_at"]
                and row["account_state"] == "active"
                and row["verification"] == "verified"
                and row["epoch"] == row["account_epoch"]
            )
            if not valid or row["space_id"] is None:
                raise _business("CREDENTIAL_INVALID")
            return {
                "account_id": row["account_id"],
                "session_id": row["session_id"],
                "space_id": row["space_id"],
                "csrf_digest": row["csrf_digest"],
                "epoch": row["epoch"],
            }

    @staticmethod
    def _require_account(account: dict[str, Any]) -> None:
        if account["state"] != "active" or account["verification"] != "verified":
            raise _business("IDENTITY_UNVERIFIED")

    @staticmethod
    def _require_space(space: dict[str, Any] | None) -> dict[str, Any]:
        if space is None or space["state"] != "active":
            raise _business("RESOURCE_UNAVAILABLE")
        return space

    @staticmethod
    def _require_kb(kb: dict[str, Any] | None, space_id: str) -> dict[str, Any]:
        if kb is None or kb["space_id"] != space_id or kb["state"] != "active":
            raise _business("RESOURCE_UNAVAILABLE")
        return kb

    @staticmethod
    def _scope_unlocked(store: Any, candidate_id: str) -> dict[str, Any] | None:
        return store.candidate_scope(candidate_id)

    # -- shared authorization -------------------------------------------

    def _authorize_scope(
        self, store: Any, context: AuthContext, *, account_id: str,
        space_id: str, knowledge_base_id: str,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Account SH, space SH, KB SH and current per-KB maintenance right."""

        if context.space_id != space_id:
            raise _business("RESOURCE_UNAVAILABLE")
        account = store.lock_account(account_id)
        if account is None:
            raise _business("AUTH_REQUIRED")
        self._require_account(account)
        space = self._require_space(store.lock_space(space_id))
        kb = self._require_kb(
            store.lock_knowledge_base(space_id, knowledge_base_id), space_id,
        )
        if not store.is_maintainer(account_id, space_id, knowledge_base_id):
            raise _business("RESOURCE_UNAVAILABLE")
        return account, space, kb

    def authorize_candidate(
        self, context: AuthContext, candidate_id: str,
    ) -> dict[str, Any]:
        """Current identity + KB right for one existing candidate."""

        with self._uow.transaction() as session:
            store = self._stores(session)
            scope = self._scope_unlocked(store, candidate_id)
            if scope is None or scope["owner_account_id"] != context.account_id:
                raise _business("RESOURCE_UNAVAILABLE")
            if scope["space_id"] != context.space_id:
                raise _business("RESOURCE_UNAVAILABLE")
            self._authorize_scope(
                store, context, account_id=context.account_id,
                space_id=scope["space_id"],
                knowledge_base_id=scope["knowledge_base_id"],
            )
            return scope

    def candidate_scope(self, candidate_id: str) -> dict[str, Any]:
        """Resolve only the persisted scope used to build request identity.

        The caller must still run ``authorize_candidate`` (or ``get`` /
        ``begin_writer``) under the resulting current session before any
        business response is produced.
        """

        with self._uow.transaction() as session:
            store = self._stores(session)
            scope = self._scope_unlocked(store, candidate_id)
            if scope is None:
                raise _business("RESOURCE_UNAVAILABLE")
            return scope

    # -- intent ----------------------------------------------------------

    def create_or_replay(
        self, context: AuthContext, request: UploadRequestInput,
    ) -> tuple[bool, UploadView]:
        canonical_id, key_time = parse_uuidv7(request.upload_operation_id)
        canonical = canonical_upload_input(
            space_id=request.space_id,
            knowledge_base_id=request.knowledge_base_id,
            filename=request.filename, title=request.title,
            format=request.format, declared_bytes=request.declared_bytes,
            original_sha256=request.original_sha256,
        )
        digest = input_digest(canonical)
        try:
            return self._create_once(context, request, canonical, digest, key_time)
        except SafeError as exc:
            cause = exc.diagnostic_cause
            if cause is None or type(cause).__name__ != "IntegrityError":
                raise
        # A concurrent first submission with the same key won the unique
        # constraint.  Re-read the winner instead of creating a second object.
        return False, self._replay_existing(context, request, canonical, digest)

    def _create_once(
        self, context: AuthContext, request: UploadRequestInput,
        canonical: dict[str, object], digest: str, key_time: datetime,
    ) -> tuple[bool, UploadView]:
        with self._uow.transaction() as session:
            store = self._stores(session)
            _, space, kb = self._authorize_scope(
                store, context, account_id=context.account_id,
                space_id=request.space_id,
                knowledge_base_id=request.knowledge_base_id,
            )
            now = store.current_time()
            record = store.lock_upload_by_key(
                owner_account_id=context.account_id,
                space_id=request.space_id,
                knowledge_base_id=request.knowledge_base_id,
                upload_operation_id=parse_uuidv7(request.upload_operation_id)[0],
            )
            if record is not None:
                # An existing key is matched before any limit or budget is
                # re-evaluated: a lowered limit never replaces the original.
                return False, self._replay_view(record, canonical, digest, store)
            if kb["guard"] != "idle":
                raise _business("UPLOAD_IN_PROGRESS")
            try:
                check_key_window(key_time, now)
            except KeyExpired:
                raise _business("UPLOAD_EXPIRED") from None
            if (
                not self._limits.configured
                or request.declared_bytes > self._limits.max_file_bytes
            ):
                raise _business("FILE_LIMIT_EXCEEDED")
            try:
                free = self._store.free_bytes()
            except Exception:
                raise _business("STORAGE_PRESSURE") from None
            if free < request.declared_bytes:
                raise _business("STORAGE_PRESSURE")
            if (
                space["used_bytes"] + space["reserved_bytes"]
                + request.declared_bytes > space["limit_bytes"]
            ):
                raise _business("ORIGINAL_CAPACITY_EXCEEDED")
            accepted_at = now
            start_by, hard_deadline = self._limits.acceptance_deadlines(accepted_at)
            prefix = new_asset_prefix()
            document_id = new_row_id("doc_")
            candidate_id = new_row_id("cand_")
            version_id = new_row_id("ver_")
            row_id = new_row_id("upload_")
            canonical_id = parse_uuidv7(request.upload_operation_id)[0]
            store.insert_intent(
                upload_row_id=row_id, upload_operation_id=canonical_id,
                owner_account_id=context.account_id,
                space_id=request.space_id,
                knowledge_base_id=request.knowledge_base_id,
                document_id=document_id, candidate_id=candidate_id,
                document_version_id=version_id,
                input_version=str(canonical["input_version"]),
                input_digest=digest, filename=request.filename,
                title=request.title, format=request.format,
                declared_bytes=request.declared_bytes,
                client_sha256=request.original_sha256,
                asset_prefix=prefix, reserved_bytes=request.declared_bytes,
                accepted_at=accepted_at, upload_start_by=start_by,
                upload_hard_deadline=hard_deadline,
            )
            try:
                store.reserve_capacity_once(
                    space_id=request.space_id,
                    reserved_bytes=request.declared_bytes,
                    reference_id=row_id,
                    transition_id=new_row_id("cap_"), now=now,
                )
            except Exception as exc:
                name = type(exc).__name__
                if name == "UploadConflict":
                    raise _business("ORIGINAL_CAPACITY_EXCEEDED") from None
                if name == "CapacityConflict":
                    raise _business("CAPACITY_LEDGER_CONFLICT") from None
                raise
            record = store.lock_upload_by_key(
                owner_account_id=context.account_id,
                space_id=request.space_id,
                knowledge_base_id=request.knowledge_base_id,
                upload_operation_id=canonical_id,
            )
            if record is None:
                raise _business("DATABASE_OPERATION_FAILED")
            return True, self._view(store, record)

    def _replay_existing(
        self, context: AuthContext, request: UploadRequestInput,
        canonical: dict[str, object], digest: str,
    ) -> UploadView:
        canonical_id = parse_uuidv7(request.upload_operation_id)[0]
        with self._uow.transaction() as session:
            store = self._stores(session)
            self._authorize_scope(
                store, context, account_id=context.account_id,
                space_id=request.space_id,
                knowledge_base_id=request.knowledge_base_id,
            )
            record = store.lock_upload_by_key(
                owner_account_id=context.account_id,
                space_id=request.space_id,
                knowledge_base_id=request.knowledge_base_id,
                upload_operation_id=canonical_id,
            )
            if record is None:
                raise _business("DATABASE_OPERATION_FAILED")
            return self._replay_view(record, canonical, digest, store)

    def _replay_view(
        self, record: dict[str, Any], canonical: dict[str, object],
        digest: str, store: Any,
    ) -> UploadView:
        if (
            record["input_digest"] != digest
            or record["input_version"] != canonical["input_version"]
        ):
            raise _business("IDEMPOTENCY_CONFLICT")
        return self._view(store, record)

    # -- read ------------------------------------------------------------

    def get(self, context: AuthContext, candidate_id: str) -> UploadView:
        with self._uow.transaction() as session:
            store = self._stores(session)
            scope = self._scope_unlocked(store, candidate_id)
            if scope is None or scope["owner_account_id"] != context.account_id:
                raise _business("RESOURCE_UNAVAILABLE")
            self._authorize_scope(
                store, context, account_id=context.account_id,
                space_id=scope["space_id"],
                knowledge_base_id=scope["knowledge_base_id"],
            )
            record = store.lock_upload_by_candidate(candidate_id)
            if record is None:
                raise _business("RESOURCE_UNAVAILABLE")
            now = store.current_time()
            if store.expire_if_due(upload_row_id=record["upload_row_id"], now=now):
                record = store.lock_upload_by_candidate(candidate_id)
                if record is None:
                    raise _business("RESOURCE_UNAVAILABLE")
            return self._view(store, record)

    # -- writer gate -----------------------------------------------------

    def begin_writer(
        self, context: AuthContext, candidate_id: str,
    ) -> BeginResult:
        """Fence the previous attempt, tighten the deadline and mint a token."""

        with self._uow.transaction() as session:
            store = self._stores(session)
            scope = self._scope_unlocked(store, candidate_id)
            if scope is None or scope["owner_account_id"] != context.account_id:
                raise _business("RESOURCE_UNAVAILABLE")
            if scope["space_id"] != context.space_id:
                raise _business("RESOURCE_UNAVAILABLE")
            self._authorize_scope(
                store, context, account_id=context.account_id,
                space_id=scope["space_id"],
                knowledge_base_id=scope["knowledge_base_id"],
            )
            record = store.lock_upload_by_candidate(candidate_id)
            if record is None:
                raise _business("RESOURCE_UNAVAILABLE")
            now = store.current_time()
            if store.expire_if_due(upload_row_id=record["upload_row_id"], now=now):
                raise _business("UPLOAD_EXPIRED")
            # The accepted operation keeps its original byte budget even if a
            # later configuration change lowers the global limit.
            max_bytes = record["declared_bytes"]
            paths = self._store.paths(record["asset_prefix"])
            if record["state"] == UploadState.ORIGINAL_COMMITTED.value:
                return BeginResult(
                    record=record, attempt=record["attempt"],
                    claim_token="", paths=paths, replay=True,
                    max_bytes=max_bytes, now=now,
                    hard_deadline=record["upload_hard_deadline"],
                )
            if record["state"] not in {
                UploadState.AWAITING_UPLOAD.value, UploadState.UPLOADING.value,
            }:
                raise _business("UPLOAD_EXPIRED")
            attempt = int(record["attempt"]) + 1
            token = new_claim_token()
            deadline = effective_hard_deadline(
                record["upload_hard_deadline"],
                record["first_started_at"] or now,
                self._limits,
            )
            if not store.begin_attempt(
                upload_row_id=record["upload_row_id"], attempt=attempt,
                claim_token_digest=claim_digest(token),
                writer_owner=context.session_id,
                lease_until=now + timedelta(seconds=self._limits.lease_s),
                now=now, hard_deadline=deadline,
            ):
                raise _business("UPLOAD_IN_PROGRESS")
            return BeginResult(
                record={**record, "attempt": attempt},
                attempt=attempt, claim_token=token, paths=paths,
                replay=False, max_bytes=max_bytes, now=now,
                hard_deadline=deadline,
            )

    # -- completion ------------------------------------------------------

    def complete(
        self, context: AuthContext, candidate_id: str, *, attempt: int,
        claim_token: str, original_sha256: str, original_bytes: int,
    ) -> tuple[bool, UploadView]:
        with self._uow.transaction() as session:
            store = self._stores(session)
            scope = self._scope_unlocked(store, candidate_id)
            if scope is None or scope["owner_account_id"] != context.account_id:
                raise _business("RESOURCE_UNAVAILABLE")
            if scope["space_id"] != context.space_id:
                raise _business("RESOURCE_UNAVAILABLE")
            self._authorize_scope(
                store, context, account_id=context.account_id,
                space_id=scope["space_id"],
                knowledge_base_id=scope["knowledge_base_id"],
            )
            record = store.lock_upload_by_candidate(candidate_id)
            if record is None:
                raise _business("RESOURCE_UNAVAILABLE")
            now = store.current_time()
            if record["state"] == UploadState.ORIGINAL_COMMITTED.value:
                if (
                    record["original_sha256"] != original_sha256
                    or record["original_bytes"] != original_bytes
                ):
                    raise _business("UPLOAD_CONTENT_CONFLICT")
                return True, self._view(store, record)
            if store.expire_if_due(upload_row_id=record["upload_row_id"], now=now):
                raise _business("UPLOAD_EXPIRED")
            if record["state"] != UploadState.UPLOADING.value:
                raise _business("UPLOAD_EXPIRED")
            if (
                record["attempt"] != attempt
                or record["claim_token_digest"] != claim_digest(claim_token)
            ):
                raise _business("UPLOAD_IN_PROGRESS")
            if original_bytes != record["declared_bytes"]:
                raise _business("UPLOAD_CONTENT_CONFLICT")
            if (
                record["client_sha256"] is not None
                and record["client_sha256"] != original_sha256
            ):
                raise _business("UPLOAD_CONTENT_CONFLICT")
            deadline = effective_hard_deadline(
                record["upload_hard_deadline"], record["first_started_at"],
                self._limits,
            )
            if now >= deadline:
                raise _business("UPLOAD_EXPIRED")
            if not store.commit_original(
                record, attempt=attempt,
                claim_token_digest=claim_digest(claim_token),
                original_sha256=original_sha256,
                original_bytes=original_bytes, now=now,
            ):
                raise _business("UPLOAD_IN_PROGRESS")
            asset_id = new_row_id("asset_")
            paths = self._store.paths(record["asset_prefix"])
            store.insert_asset(
                asset_id=asset_id, asset_prefix=record["asset_prefix"],
                relative_path=paths["relative"],
                original_sha256=original_sha256, byte_size=original_bytes,
                owner_row_id=record["upload_row_id"], now=now,
            )
            store.insert_version(
                document_version_id=record["document_version_id"],
                document_id=record["document_id"],
                space_id=record["space_id"],
                knowledge_base_id=record["knowledge_base_id"],
                format=record["format"], original_sha256=original_sha256,
                original_bytes=original_bytes, asset_id=asset_id, now=now,
            )
            store.transfer_reserved_to_used(
                space_id=record["space_id"], original_bytes=original_bytes,
                transition_id=new_row_id("cap_"),
                reference_id=record["upload_row_id"], now=now,
            )
            store.insert_job(
                job_id=new_row_id("job_"), candidate_id=candidate_id,
                document_id=record["document_id"],
                document_version_id=record["document_version_id"],
                space_id=record["space_id"],
                knowledge_base_id=record["knowledge_base_id"],
                hard_deadline=now + JOB_ABSOLUTE_WINDOW, now=now,
            )
            record = store.lock_upload_by_candidate(candidate_id)
            if record is None:
                raise _business("DATABASE_OPERATION_FAILED")
            return False, self._view(store, record)

    def record_abandoned_writer(
        self, candidate_id: str, *, attempt: int, claim_token: str,
    ) -> None:
        """Clear an unproven writer's lease; reserved bytes are never refunded."""

        with self._uow.transaction() as session:
            store = self._stores(session)
            scope = self._scope_unlocked(store, candidate_id)
            if scope is None:
                return
            record = store.lock_upload_by_candidate(candidate_id)
            if record is None:
                return
            if (
                record["attempt"] != attempt
                or record["claim_token_digest"] != claim_digest(claim_token)
            ):
                return
            store.clear_writer_lease(
                record["upload_row_id"], attempt=attempt,
                claim_token_digest=claim_digest(claim_token),
            )

    # -- projection ------------------------------------------------------

    @staticmethod
    def _view(store: Any, record: dict[str, Any]) -> UploadView:
        candidate = store.candidate_row(record["candidate_id"])
        if candidate is None:
            raise _business("RESOURCE_UNAVAILABLE")
        return UploadView(
            record=record, candidate=candidate,
            version=store.version_row(record["document_version_id"]),
            job=store.job_row(record["candidate_id"]),
        )
