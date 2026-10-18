"""Developer HTTP acceptance for the real TXT/Markdown upload chain.

These cases run against the real ASGI app, the isolated PostgreSQL schema
created by ``conftest.py`` and the native Linux writer subprocess.  They are
not a replacement for the independent verifier and they never run on Windows:
the writer, upload slot and ext4 path semantics are Linux facts.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import re
import secrets
import sys
from types import SimpleNamespace
import uuid

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text
from starlette.requests import Request

from rag_app.bootstrap.config import Settings
from rag_app.contracts.public import PublicError
from rag_app.contracts.upload import UploadResponse
from rag_app.entrypoints.api import create_app
from rag_app.modules.library.sessions import digest_secret


pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        sys.platform != "linux",
        reason="The upload slot and native writer are Linux acceptance paths.",
    ),
]

CREATE = "/api/v1/web/document-candidates"
ORIGIN = "https://app.test"
UPLOAD_ROOT_LIMIT = 4096


def _uuid7() -> str:
    """Build a valid RFC 4122 UUIDv7 without relying on Python 3.13."""

    milliseconds = int(datetime.now(timezone.utc).timestamp() * 1000)
    raw = bytearray(secrets.token_bytes(16))
    raw[0:6] = (milliseconds & ((1 << 48) - 1)).to_bytes(6, "big")
    raw[6] = (raw[6] & 0x0F) | 0x70
    raw[8] = (raw[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(raw)))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _quoted(schema: str) -> str:
    return '"' + schema.replace('"', '""') + '"'


def _migration_config() -> Config:
    from pathlib import Path

    return Config(str(Path(__file__).parents[1] / "alembic.ini"))


def _seed(engine, schema: str) -> SimpleNamespace:
    """Create real identity, space, KB and maintenance rows in the isolated schema."""

    now = datetime.now(timezone.utc)
    secret = secrets.token_urlsafe(48)
    csrf = secrets.token_urlsafe(32)
    second_secret = secrets.token_urlsafe(48)
    second_csrf = secrets.token_urlsafe(32)
    q = _quoted(schema)
    with engine.begin() as connection:
        connection.execute(text(
            f"INSERT INTO {q}.account "
            "(account_id, state, verification, epoch) "
            "VALUES (:account_id, 'active', 'verified', :epoch)"
        ), {"account_id": "acct-1", "epoch": "epoch-1"})
        connection.execute(text(
            f"INSERT INTO {q}.account "
            "(account_id, state, verification, epoch) "
            "VALUES (:account_id, 'active', 'verified', :epoch)"
        ), {"account_id": "acct-2", "epoch": "epoch-1"})
        for space_id in ("space-1", "space-2"):
            connection.execute(text(
                f"INSERT INTO {q}.space_control "
                "(space_id, state, epoch, used_bytes, reserved_bytes, "
                "limit_bytes, physical_used_bytes, physical_reserved_bytes, "
                "physical_budget_bytes) "
                "VALUES (:space_id, 'active', :epoch, 0, 0, :limit, 0, 0, :limit)"
            ), {
                "space_id": space_id, "epoch": "epoch-1",
                "limit": UPLOAD_ROOT_LIMIT,
            })
        for space_id, knowledge_base_id in (
            ("space-1", "kb-1"), ("space-2", "kb-2"),
        ):
            connection.execute(text(
                f"INSERT INTO {q}.knowledge_base "
                "(knowledge_base_id, space_id, state, guard, docset_revision) "
                "VALUES (:kb_id, :space_id, 'active', 'idle', 0)"
            ), {"kb_id": knowledge_base_id, "space_id": space_id})
        for account_id, space_id, knowledge_base_id in (
            ("acct-1", "space-1", "kb-1"),
            ("acct-2", "space-1", "kb-1"),
        ):
            connection.execute(text(
                f"INSERT INTO {q}.kb_maintainer "
                "(knowledge_base_id, account_id, granted_at) "
                "VALUES (:kb_id, :account_id, :now)"
            ), {
                "kb_id": knowledge_base_id, "account_id": account_id,
                "now": now,
            })
        for account_id in ("acct-1", "acct-2"):
            connection.execute(text(
                f"INSERT INTO {q}.space_member "
                "(space_id, account_id, role, joined_at) "
                "VALUES ('space-1', :account_id, 'maintainer', :now)"
            ), {"account_id": account_id, "now": now})
        connection.execute(text(
            f"INSERT INTO {q}.web_session "
            "(session_id, account_id, space_id, secret_digest, csrf_digest, "
            "epoch, created_at, last_seen_at, idle_expires_at, "
            "absolute_expires_at) "
            "VALUES (:session_id, :account_id, 'space-1', :secret_digest, "
            ":csrf_digest, :epoch, :now, :now, :idle, :absolute)"
        ), {
            "session_id": "sess-1", "account_id": "acct-1",
            "secret_digest": digest_secret(secret),
            "csrf_digest": digest_secret(csrf), "epoch": "epoch-1",
            "now": now, "idle": now + timedelta(hours=1),
            "absolute": now + timedelta(days=1),
        })
        connection.execute(text(
            f"INSERT INTO {q}.web_session "
            "(session_id, account_id, space_id, secret_digest, csrf_digest, "
            "epoch, created_at, last_seen_at, idle_expires_at, "
            "absolute_expires_at) "
            "VALUES (:session_id, :account_id, 'space-1', :secret_digest, "
            ":csrf_digest, :epoch, :now, :now, :idle, :absolute)"
        ), {
            "session_id": "sess-2", "account_id": "acct-2",
            "secret_digest": digest_secret(second_secret),
            "csrf_digest": digest_secret(second_csrf), "epoch": "epoch-1",
            "now": now, "idle": now + timedelta(hours=1),
            "absolute": now + timedelta(days=1),
        })
    return SimpleNamespace(
        secret=secret, csrf=csrf,
        second_secret=second_secret, second_csrf=second_csrf,
    )


def _headers(secret: str, csrf: str) -> dict[str, str]:
    return {
        "Cookie": f"rag_session={secret}",
        "Origin": ORIGIN,
        "X-CSRF-Token": csrf,
    }


def _assert_private(response) -> None:
    assert response.headers.get("cache-control") == "no-store"
    assert "etag" not in response.headers
    assert re.fullmatch(r"[a-f0-9]{32}", response.headers.get("x-request-id", ""))


def _assert_failure(response, code: str) -> None:
    _assert_private(response)
    expected = PublicError.from_code(code)
    assert response.status_code == expected.http_status
    body = response.json()
    assert body["status"] == "failed"
    assert body["error"]["code"] == code
    assert body["error"]["message"] == expected.message
    assert body["request_id"] == response.headers["x-request-id"]


def _assert_upload(response) -> UploadResponse:
    _assert_private(response)
    dto = UploadResponse.model_validate(response.json())
    assert dto.request_id == response.headers["x-request-id"]
    return dto


def _payload(
    operation_id: str, data: bytes, *, declared: int | None = None,
    sha: str | None | object = ..., **overrides,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "upload_operation_id": operation_id,
        "space_id": "space-1",
        "knowledge_base_id": "kb-1",
        "filename": "笔记 1.md",
        "format": "markdown",
        "declared_bytes": len(data) if declared is None else declared,
    }
    if sha is not ...:
        if sha is not None:
            payload["original_sha256"] = sha
    else:
        payload["original_sha256"] = _sha(data)
    payload.update(overrides)
    return payload


def _post(container, payload: dict[str, object], *, headers=None):
    return container.client.post(
        CREATE, json=payload,
        headers=container.headers if headers is None else headers,
    )


def _get(container, candidate_id: str, *, headers=None):
    return container.client.get(
        f"{CREATE}/{candidate_id}",
        headers=container.headers if headers is None else headers,
    )


def _put(
    container, candidate_id: str, body: bytes, *, headers=None,
    extra_headers: dict[str, str] | None = None,
):
    selected = dict(container.headers if headers is None else headers)
    selected["Content-Type"] = "application/octet-stream"
    if extra_headers:
        selected.update(extra_headers)
    return container.client.put(
        f"{CREATE}/{candidate_id}/original",
        content=body, headers=selected,
    )


def _new_candidate(
    container, data: bytes = b"hello", *, sha=..., **overrides,
) -> tuple[dict[str, object], UploadResponse, str]:
    operation_id = _uuid7()
    payload = _payload(operation_id, data, sha=sha, **overrides)
    response = _post(container, payload)
    assert response.status_code == 201, response.text
    dto = _assert_upload(response)
    assert dto.status == "in_progress"
    assert dto.replayed is False
    assert dto.candidate.upload_state == "awaiting_upload"
    assert dto.job is None
    assert dto.active_version is None
    return payload, dto, dto.candidate.candidate_id


def _counts(engine, schema: str) -> dict[str, int]:
    q = _quoted(schema)
    names = (
        "document", "upload_operation", "document_candidate",
        "document_version", "source_asset", "processing_job",
        "capacity_transition",
    )
    with engine.connect() as connection:
        return {
            name: connection.execute(
                text(f"SELECT count(*) FROM {q}.{name}")
            ).scalar_one()
            for name in names
        }


def _one(engine, schema: str, statement: str, **parameters):
    with engine.connect() as connection:
        return connection.execute(
            text(statement.format(q=_quoted(schema))), parameters,
        ).mappings().one()


def _upload(engine, schema: str, operation_id: str):
    return _one(
        engine, schema,
        "SELECT * FROM {q}.upload_operation "
        "WHERE upload_operation_id = :operation_id",
        operation_id=operation_id,
    )


def _candidate(engine, schema: str, candidate_id: str):
    return _one(
        engine, schema,
        "SELECT * FROM {q}.document_candidate WHERE candidate_id = :candidate_id",
        candidate_id=candidate_id,
    )


def _job(engine, schema: str, candidate_id: str):
    return _one(
        engine, schema,
        "SELECT * FROM {q}.processing_job WHERE candidate_id = :candidate_id",
        candidate_id=candidate_id,
    )


def _asset(engine, schema: str, candidate_id: str):
    return _one(
        engine, schema,
        "SELECT a.* FROM {q}.source_asset AS a "
        "JOIN {q}.upload_operation AS u ON u.upload_row_id = a.owner_row_id "
        "JOIN {q}.document_candidate AS c ON c.upload_row_id = u.upload_row_id "
        "WHERE c.candidate_id = :candidate_id",
        candidate_id=candidate_id,
    )


def _version(engine, schema: str, candidate_id: str):
    return _one(
        engine, schema,
        "SELECT v.* FROM {q}.document_version AS v "
        "JOIN {q}.document_candidate AS c "
        "ON c.document_version_id = v.document_version_id "
        "WHERE c.candidate_id = :candidate_id",
        candidate_id=candidate_id,
    )


def _space(engine, schema: str, space_id: str = "space-1"):
    return _one(
        engine, schema,
        "SELECT * FROM {q}.space_control WHERE space_id = :space_id",
        space_id=space_id,
    )


def _transitions(engine, schema: str, upload_row_id: str) -> list[str]:
    with engine.connect() as connection:
        return [
            row[0] for row in connection.execute(text(
                f"SELECT operation FROM {_quoted(schema)}.capacity_transition "
                "WHERE reference_id = :reference_id ORDER BY operation"
            ), {"reference_id": upload_row_id}).all()
        ]


def _store_file(root, prefix: str):
    return root / "assets" / prefix[:2] / prefix / "original"


def _staging_file(root, prefix: str):
    return root / "staging" / (prefix + ".part")


@pytest.fixture
def upload_api(isolated_database, tmp_path):
    engine, schema = isolated_database
    command.upgrade(_migration_config(), "head")
    identities = _seed(engine, schema)
    root = tmp_path / "upload-store"
    root.mkdir()
    settings = Settings(
        database_url=os.environ["RAG_TEST_DATABASE_URL"],
        database_schema=schema,
        uploads_enabled=True,
        upload_root=str(root),
        upload_max_file_bytes=UPLOAD_ROOT_LIMIT,
        allowed_origin=ORIGIN,
        upload_slot_wait_s=0,
        upload_stop_grace_s=1,
        upload_no_progress_s=5,
        upload_lease_s=5,
        upload_renew_s=1,
        upload_chunk_bytes=4096,
        upload_page_bytes=0,
    )
    app = create_app(settings)
    with TestClient(app) as client:
        runtime = client.app.state.runtime
        container = SimpleNamespace(
            client=client, app=app, runtime=runtime, engine=engine,
            schema=schema, root=root, settings=settings,
            headers=_headers(identities.secret, identities.csrf),
            headers2=_headers(
                identities.second_secret, identities.second_csrf,
            ),
            csrf=identities.csrf,
            secret=identities.secret,
        )
        yield container


def test_create_stream_put_get_registers_real_original_once(upload_api):
    data = "标题\n正文\n".encode("utf-8")
    payload, created, candidate_id = _new_candidate(upload_api, data)
    operation_id = str(payload["upload_operation_id"])

    body = _assert_upload(_post(upload_api, payload))
    assert body.status == "in_progress"
    assert body.original_sha256 is None
    assert body.original_bytes is None
    assert body.original_url == f"{CREATE}/{candidate_id}/original"
    assert body.active_version is None
    assert body.job is None
    assert body.index_generation.active_generation_id is None
    assert body.index_generation.embedding_profile_id is None
    assert body.cleanup is None
    assert body.allowed_actions == ["view_candidate"]

    upload = _upload(upload_api.engine, upload_api.schema, operation_id)
    assert upload["state"] == "awaiting_upload"
    assert upload["reserved_bytes"] == len(data)
    assert upload["client_sha256"] == _sha(data)
    assert upload["attempt"] == 0
    assert upload["claim_token_digest"] is None
    candidate = _candidate(upload_api.engine, upload_api.schema, candidate_id)
    assert candidate["upload_state"] == "awaiting_upload"
    assert candidate["processing_state"] is None
    assert candidate["retained_original_bytes"] == 0
    assert _counts(upload_api.engine, upload_api.schema) == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 0, "source_asset": 0, "processing_job": 0,
        "capacity_transition": 1,
    }
    assert _transitions(
        upload_api.engine, upload_api.schema, upload["upload_row_id"],
    ) == ["reserve"]
    space = _space(upload_api.engine, upload_api.schema)
    assert (space["used_bytes"], space["reserved_bytes"]) == (0, len(data))

    current = _get(upload_api, candidate_id)
    assert current.status_code == 200
    assert _assert_upload(current).status == "in_progress"

    committed = _put(upload_api, candidate_id, data)
    assert committed.status_code == 200, committed.text
    completed = _assert_upload(committed)
    assert completed.status == "completed"
    assert completed.replayed is False
    assert completed.original_sha256 == _sha(data)
    assert completed.original_bytes == len(data)
    assert completed.active_version is None
    assert completed.candidate.upload_state == "original_committed"
    assert completed.candidate.processing_state == "queued"
    assert completed.candidate.retained_original_bytes == len(data)
    assert completed.job is not None
    assert completed.job.job_state == "queued"
    assert completed.job.stage_code == "parse"
    assert completed.job.attempt == 1
    assert completed.allowed_actions == ["view_candidate", "view_task"]
    assert completed.cleanup is None

    payload_replay = _post(upload_api, payload)
    payload_replay_dto = _assert_upload(payload_replay)
    assert payload_replay.status_code == 200
    assert payload_replay_dto.replayed is True
    assert payload_replay_dto.status == "completed"
    assert payload_replay_dto.candidate.candidate_id == candidate_id

    changed = dict(payload)
    changed["title"] = "另一个标题"
    _assert_failure(_post(upload_api, changed), "IDEMPOTENCY_CONFLICT")

    replay_put = _put(upload_api, candidate_id, data)
    replayed = _assert_upload(replay_put)
    assert replay_put.status_code == 200
    assert replayed.replayed is True
    assert replayed.status == "completed"
    assert replayed.job is not None

    different_data = data[:-1] + b"!"
    assert len(different_data) == len(data)
    _assert_failure(
        _put(upload_api, candidate_id, different_data),
        "UPLOAD_CONTENT_CONFLICT",
    )

    upload = _upload(upload_api.engine, upload_api.schema, operation_id)
    candidate = _candidate(upload_api.engine, upload_api.schema, candidate_id)
    job = _job(upload_api.engine, upload_api.schema, candidate_id)
    asset = _asset(upload_api.engine, upload_api.schema, candidate_id)
    version = _version(upload_api.engine, upload_api.schema, candidate_id)
    assert upload["state"] == "original_committed"
    assert upload["original_sha256"] == _sha(data)
    assert upload["original_bytes"] == len(data)
    assert upload["claim_token_digest"] is None
    assert upload["lease_until"] is None
    assert candidate["upload_state"] == "original_committed"
    assert candidate["processing_state"] == "queued"
    assert candidate["retained_original_bytes"] == len(data)
    assert job["job_state"] == "queued"
    assert job["attempt"] == 1
    assert version["original_sha256"] == _sha(data)
    assert version["original_bytes"] == len(data)
    assert version["asset_id"] == asset["asset_id"]
    assert asset["byte_size"] == len(data)
    assert asset["relative_path"] == (
        f"assets/{upload['asset_prefix'][:2]}/{upload['asset_prefix']}/original"
    )
    path = _store_file(upload_api.root, upload["asset_prefix"])
    assert path.read_bytes() == data
    assert hashlib.sha256(path.read_bytes()).hexdigest() == _sha(data)
    assert not _staging_file(upload_api.root, upload["asset_prefix"]).exists()
    assert _transitions(
        upload_api.engine, upload_api.schema, upload["upload_row_id"],
    ) == ["commit", "reserve"]
    space = _space(upload_api.engine, upload_api.schema)
    assert (space["used_bytes"], space["reserved_bytes"]) == (len(data), 0)
    counts = _counts(upload_api.engine, upload_api.schema)
    assert counts == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 1, "source_asset": 1, "processing_job": 1,
        "capacity_transition": 2,
    }

    read_back = _get(upload_api, candidate_id)
    read_dto = _assert_upload(read_back)
    assert read_back.status_code == 200
    assert read_dto.candidate.upload_state == "original_committed"
    assert read_dto.active_version is None
    assert str(upload_api.root) not in read_back.text
    assert "staging" not in read_back.text.lower()
    assert "csrf" not in read_back.text.lower()
    assert "rag_session" not in read_back.text.lower()

    # An expired/unknown candidate is never synthesized by GET.
    before = _counts(upload_api.engine, upload_api.schema)
    assert _assert_failure(
        _get(upload_api, "cand_unknown"), "RESOURCE_UNAVAILABLE",
    ) is None
    assert _counts(upload_api.engine, upload_api.schema) == before


def test_lowered_global_limit_rejects_new_intent_but_not_accepted_put(upload_api):
    data = b"x" * 16
    payload, _, candidate_id = _new_candidate(upload_api, data)
    upload = _upload(
        upload_api.engine, upload_api.schema,
        str(payload["upload_operation_id"]),
    )
    upload_api.runtime.settings.upload_max_file_bytes = 4
    new_payload = _payload(_uuid7(), b"12345")
    _assert_failure(_post(upload_api, new_payload), "FILE_LIMIT_EXCEEDED")
    assert _counts(upload_api.engine, upload_api.schema)["upload_operation"] == 1

    response = _put(upload_api, candidate_id, data)
    assert response.status_code == 200, response.text
    dto = _assert_upload(response)
    assert dto.status == "completed"
    assert dto.original_bytes == len(data)
    assert _upload(
        upload_api.engine, upload_api.schema,
        str(payload["upload_operation_id"]),
    )["state"] == "original_committed"
    assert upload["reserved_bytes"] == len(data)


def test_replay_after_lowered_limit_uses_accepted_input(upload_api):
    """The existing key must win before the newly lowered file limit."""

    data = b"y" * 16
    payload, _, candidate_id = _new_candidate(upload_api, data)
    upload_api.runtime.settings.upload_max_file_bytes = 4
    response = _post(upload_api, payload)
    assert response.status_code == 200, response.text
    dto = _assert_upload(response)
    assert dto.replayed is True
    assert dto.candidate.candidate_id == candidate_id
    assert _counts(upload_api.engine, upload_api.schema)["upload_operation"] == 1


def test_lowered_space_limit_rejects_new_reservation_but_completes_accepted(
    upload_api,
):
    data = b"z" * 8
    payload, _, candidate_id = _new_candidate(upload_api, data)
    upload = _upload(
        upload_api.engine, upload_api.schema,
        str(payload["upload_operation_id"]),
    )
    with upload_api.engine.begin() as connection:
        connection.execute(text(
            f"UPDATE {_quoted(upload_api.schema)}.space_control "
            "SET limit_bytes = 1 WHERE space_id = 'space-1'"
        ))
    assert _space(upload_api.engine, upload_api.schema)["limit_bytes"] == 1
    _assert_failure(
        _post(upload_api, _payload(_uuid7(), b"1")),
        "ORIGINAL_CAPACITY_EXCEEDED",
    )
    assert _counts(upload_api.engine, upload_api.schema)["upload_operation"] == 1

    response = _put(upload_api, candidate_id, data)
    assert response.status_code == 200, response.text
    assert _assert_upload(response).status == "completed"
    space = _space(upload_api.engine, upload_api.schema)
    assert space["limit_bytes"] == 1
    assert (space["used_bytes"], space["reserved_bytes"]) == (len(data), 0)
    assert upload["reserved_bytes"] == len(data)


def test_identity_channel_origin_and_csrf_reject_before_binary_body(
    upload_api, monkeypatch,
):
    _, _, candidate_id = _new_candidate(upload_api)
    before = _counts(upload_api.engine, upload_api.schema)

    def forbidden(*args, **kwargs):
        raise AssertionError("request body was read before authorization")

    with monkeypatch.context() as scope:
        scope.setattr(Request, "stream", forbidden)
        # No identity at all: POST must not enter read_bounded_json.
        _assert_failure(
            upload_api.client.post(
                CREATE, json=_payload(_uuid7(), b"body"),
                headers={"Origin": ORIGIN, "X-CSRF-Token": upload_api.csrf},
            ),
            "AUTH_REQUIRED",
        )
        # No identity for a candidate PUT: never touch its binary body.
        _assert_failure(
            upload_api.client.put(
                f"{CREATE}/{candidate_id}/original", content=b"body",
                headers={
                    "Content-Type": "application/octet-stream",
                    "Origin": ORIGIN,
                    "X-CSRF-Token": upload_api.csrf,
                },
            ),
            "AUTH_REQUIRED",
        )
        _assert_failure(
            upload_api.client.put(
                f"{CREATE}/{candidate_id}/original", content=b"body",
                headers={
                    **upload_api.headers,
                    "Authorization": "Bearer not-a-web-session",
                    "Content-Type": "application/octet-stream",
                },
            ),
            "AUTH_CHANNEL_CONFLICT",
        )
        _assert_failure(
            _get(upload_api, candidate_id, headers={}),
            "AUTH_REQUIRED",
        )
        # Cookie and Bearer are mutually exclusive.
        _assert_failure(
            upload_api.client.post(
                CREATE, json=_payload(_uuid7(), b"body"),
                headers={
                    **upload_api.headers,
                    "Authorization": "Bearer not-a-web-session",
                },
            ),
            "AUTH_CHANNEL_CONFLICT",
        )
        # A program credential is read-only; it cannot create an upload.
        _assert_failure(
            upload_api.client.post(
                CREATE, json=_payload(_uuid7(), b"body"),
                headers={"Authorization": "Bearer program-only"},
            ),
            "ACTION_FORBIDDEN",
        )
        # X-User is never an identity source.
        _assert_failure(
            upload_api.client.post(
                CREATE, json=_payload(_uuid7(), b"body"),
                headers={"X-User": "acct-1"},
            ),
            "AUTH_REQUIRED",
        )

    _assert_failure(
        _post(
            upload_api, _payload(_uuid7(), b"body"),
            headers={**upload_api.headers, "Origin": "https://evil.test"},
        ),
        "ACTION_FORBIDDEN",
    )
    _assert_failure(
        _post(
            upload_api, _payload(_uuid7(), b"body"),
            headers={**upload_api.headers, "X-CSRF-Token": "wrong"},
        ),
        "ACTION_FORBIDDEN",
    )
    missing_csrf = dict(upload_api.headers)
    missing_csrf.pop("X-CSRF-Token")
    _assert_failure(
        _post(upload_api, _payload(_uuid7(), b"body"), headers=missing_csrf),
        "ACTION_FORBIDDEN",
    )
    _assert_failure(
        _put(
            upload_api, candidate_id, b"body",
            headers={**upload_api.headers, "Origin": "https://evil.test"},
        ),
        "ACTION_FORBIDDEN",
    )
    _assert_failure(
        _put(
            upload_api, candidate_id, b"body",
            headers={**upload_api.headers, "X-CSRF-Token": "wrong"},
        ),
        "ACTION_FORBIDDEN",
    )
    assert _counts(upload_api.engine, upload_api.schema) == before


def test_content_type_and_encoding_are_rejected_before_body(upload_api, monkeypatch):
    payload, _, candidate_id = _new_candidate(upload_api)
    before = _counts(upload_api.engine, upload_api.schema)

    def forbidden(*args, **kwargs):
        raise AssertionError("binary body was read before the media check")

    with monkeypatch.context() as scope:
        scope.setattr(Request, "stream", forbidden)
        _assert_failure(
            _put(
                upload_api, candidate_id, b"body",
                extra_headers={"Content-Type": "text/plain"},
            ),
            "UNSUPPORTED_MEDIA_TYPE",
        )
        _assert_failure(
            _put(
                upload_api, candidate_id, b"body",
                extra_headers={
                    "Content-Type": "multipart/form-data; boundary=example",
                },
            ),
            "UNSUPPORTED_MEDIA_TYPE",
        )
        _assert_failure(
            _put(
                upload_api, candidate_id, b"body",
                extra_headers={"Content-Encoding": "gzip"},
            ),
            "UNSUPPORTED_CONTENT_ENCODING",
        )
    assert _counts(upload_api.engine, upload_api.schema) == before


def test_scope_owner_and_current_maintenance_right_are_rechecked(upload_api):
    _, _, candidate_id = _new_candidate(upload_api)
    before = _counts(upload_api.engine, upload_api.schema)

    second_payload = _payload(_uuid7(), b"space")
    second_payload["space_id"] = "space-2"
    second_payload["knowledge_base_id"] = "kb-2"
    _assert_failure(_post(upload_api, second_payload), "RESOURCE_UNAVAILABLE")

    cross_kb = _payload(_uuid7(), b"kb")
    cross_kb["knowledge_base_id"] = "kb-2"
    _assert_failure(_post(upload_api, cross_kb), "RESOURCE_UNAVAILABLE")

    _assert_failure(_get(upload_api, "cand_unknown"), "RESOURCE_UNAVAILABLE")
    _assert_failure(
        _get(upload_api, candidate_id, headers=upload_api.headers2),
        "RESOURCE_UNAVAILABLE",
    )

    with upload_api.engine.begin() as connection:
        connection.execute(text(
            f"UPDATE {_quoted(upload_api.schema)}.kb_maintainer "
            "SET revoked_at = clock_timestamp() "
            "WHERE account_id = 'acct-1' AND knowledge_base_id = 'kb-1'"
        ))
    _assert_failure(_get(upload_api, candidate_id), "RESOURCE_UNAVAILABLE")

    def forbidden(*args, **kwargs):
        raise AssertionError("revoked binary writer read the body")

    with monkeypatch.context() as scope:
        scope.setattr(Request, "stream", forbidden)
        _assert_failure(_put(upload_api, candidate_id, b"body"), "RESOURCE_UNAVAILABLE")
    assert _counts(upload_api.engine, upload_api.schema) == before


def test_invalid_create_schema_never_creates_a_candidate(upload_api):
    before = _counts(upload_api.engine, upload_api.schema)
    cases = [
        {"declared_bytes": 0},
        {"declared_bytes": True},
        {"original_sha256": "a" * 63},
        {"original_sha256": "A" * 64},
        {"format": "pdf"},
        {"filename": "bad\nname"},
        {"filename": "x" * 256},
        {"title": "x" * 129},
        {"unknown_field": "value"},
        {"upload_operation_id": "not-a-uuid"},
    ]
    for overrides in cases:
        payload = _payload(_uuid7(), b"body")
        payload.update(overrides)
        _assert_failure(_post(upload_api, payload), "VALIDATION_ERROR")
    missing_space = _payload(_uuid7(), b"body")
    missing_space.pop("space_id")
    _assert_failure(_post(upload_api, missing_space), "VALIDATION_ERROR")
    over_limit = _payload(_uuid7(), b"body")
    over_limit["declared_bytes"] = UPLOAD_ROOT_LIMIT + 1
    _assert_failure(_post(upload_api, over_limit), "FILE_LIMIT_EXCEEDED")
    assert _counts(upload_api.engine, upload_api.schema) == before


def test_bad_utf8_keeps_reservation_and_retry_completes_without_refresh(upload_api):
    payload, _, candidate_id = _new_candidate(upload_api, declared=1, sha=None)
    operation_id = str(payload["upload_operation_id"])
    first = _upload(upload_api.engine, upload_api.schema, operation_id)
    initial_deadline = first["upload_hard_deadline"]

    _assert_failure(_put(upload_api, candidate_id, b"\xff"), "UPLOAD_CONTENT_CONFLICT")
    failed_upload = _upload(upload_api.engine, upload_api.schema, operation_id)
    assert failed_upload["state"] == "uploading"
    assert failed_upload["attempt"] == 1
    assert failed_upload["claim_token_digest"] is None
    assert failed_upload["lease_until"] is None
    assert failed_upload["upload_hard_deadline"] <= initial_deadline
    failed_deadline = failed_upload["upload_hard_deadline"]
    assert _counts(upload_api.engine, upload_api.schema) == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 0, "source_asset": 0, "processing_job": 0,
        "capacity_transition": 1,
    }
    assert _transitions(
        upload_api.engine, upload_api.schema, failed_upload["upload_row_id"],
    ) == ["reserve"]
    space = _space(upload_api.engine, upload_api.schema)
    assert (space["used_bytes"], space["reserved_bytes"]) == (0, 1)
    assert not _staging_file(
        upload_api.root, failed_upload["asset_prefix"],
    ).exists()
    assert not _store_file(
        upload_api.root, failed_upload["asset_prefix"],
    ).exists()

    response = _put(upload_api, candidate_id, b"a")
    assert response.status_code == 200, response.text
    assert _assert_upload(response).status == "completed"
    completed_upload = _upload(upload_api.engine, upload_api.schema, operation_id)
    assert completed_upload["state"] == "original_committed"
    assert completed_upload["attempt"] == 2
    assert completed_upload["upload_hard_deadline"] == failed_deadline
    assert _counts(upload_api.engine, upload_api.schema)["processing_job"] == 1
    assert _counts(upload_api.engine, upload_api.schema)["source_asset"] == 1
    assert _store_file(
        upload_api.root, completed_upload["asset_prefix"],
    ).read_bytes() == b"a"
    assert _transitions(
        upload_api.engine, upload_api.schema, completed_upload["upload_row_id"],
    ) == ["commit", "reserve"]


def test_client_hash_mismatch_keeps_real_file_but_registers_no_asset(upload_api):
    data = b"hash-mismatch"
    wrong = _sha(data[:-1] + b"X")
    payload, _, candidate_id = _new_candidate(upload_api, data, sha=wrong)
    operation_id = str(payload["upload_operation_id"])
    _assert_failure(_put(upload_api, candidate_id, data), "UPLOAD_CONTENT_CONFLICT")

    upload = _upload(upload_api.engine, upload_api.schema, operation_id)
    assert upload["state"] == "uploading"
    assert upload["attempt"] == 1
    assert upload["claim_token_digest"] is None
    assert upload["lease_until"] is None
    assert _counts(upload_api.engine, upload_api.schema) == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 0, "source_asset": 0, "processing_job": 0,
        "capacity_transition": 1,
    }
    space = _space(upload_api.engine, upload_api.schema)
    assert (space["used_bytes"], space["reserved_bytes"]) == (0, len(data))
    path = _store_file(upload_api.root, upload["asset_prefix"])
    assert path.read_bytes() == data
    assert _versions_and_assets_absent(upload_api, candidate_id)


def _versions_and_assets_absent(container, candidate_id: str) -> bool:
    q = _quoted(container.schema)
    with container.engine.connect() as connection:
        versions = connection.execute(text(
            f"SELECT count(*) FROM {q}.document_version AS v "
            "JOIN {q}.document_candidate AS c "
            "ON c.document_version_id = v.document_version_id "
            "WHERE c.candidate_id = :candidate_id"
        ), {"candidate_id": candidate_id}).scalar_one()
        assets = connection.execute(text(
            f"SELECT count(*) FROM {q}.source_asset AS a "
            "JOIN {q}.upload_operation AS u ON u.upload_row_id = a.owner_row_id "
            "JOIN {q}.document_candidate AS c "
            "ON c.upload_row_id = u.upload_row_id "
            "WHERE c.candidate_id = :candidate_id"
        ), {"candidate_id": candidate_id}).scalar_one()
    return versions == 0 and assets == 0


@pytest.mark.parametrize(
    "declared,body,final_exists",
    [
        (1, b"", False),
        (1, b"ab", False),
        (5, b"abc", True),
    ],
)
def test_bounded_length_and_zero_byte_failures_do_not_register(
    upload_api, declared, body, final_exists,
):
    payload, _, candidate_id = _new_candidate(
        upload_api, declared=declared, sha=None,
    )
    operation_id = str(payload["upload_operation_id"])
    _assert_failure(_put(upload_api, candidate_id, body), "UPLOAD_CONTENT_CONFLICT")
    upload = _upload(upload_api.engine, upload_api.schema, operation_id)
    assert upload["state"] == "uploading"
    assert _counts(upload_api.engine, upload_api.schema) == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 0, "source_asset": 0, "processing_job": 0,
        "capacity_transition": 1,
    }
    space = _space(upload_api.engine, upload_api.schema)
    assert (space["used_bytes"], space["reserved_bytes"]) == (0, declared)
    assert _store_file(
        upload_api.root, upload["asset_prefix"],
    ).exists() is final_exists
    assert not _staging_file(upload_api.root, upload["asset_prefix"]).exists()


def test_disconnect_is_finite_and_keeps_reserved_bytes(upload_api):
    payload, _, candidate_id = _new_candidate(upload_api, declared=10, sha=None)
    operation_id = str(payload["upload_operation_id"])
    app = upload_api.app
    path = f"{CREATE}/{candidate_id}/original"
    headers = [
        (b"cookie", f"rag_session={upload_api.secret}".encode("latin-1")),
        (b"origin", ORIGIN.encode("ascii")),
        (b"x-csrf-token", upload_api.csrf.encode("latin-1")),
        (b"content-type", b"application/octet-stream"),
        (b"content-length", b"10"),
    ]
    calls = 0
    messages = []

    async def receive():
        nonlocal calls
        calls += 1
        if calls == 1:
            return {"type": "http.request", "body": b"abc", "more_body": True}
        return {"type": "http.disconnect"}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "server": ("testserver", 80), "client": ("testclient", 1),
        "scheme": "http", "method": "PUT", "root_path": "",
        "path": path, "raw_path": path.encode("ascii"),
        "query_string": b"", "headers": headers,
    }
    asyncio.run(app(scope, receive, send))
    start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    body = b"".join(
        message.get("body", b"") for message in messages
        if message["type"] == "http.response.body"
    )
    assert start["status"] == 400
    assert json.loads(body)["error"]["code"] == "REQUEST_STREAM_ERROR"

    upload = _upload(upload_api.engine, upload_api.schema, operation_id)
    assert upload["state"] == "uploading"
    assert upload["reserved_bytes"] == 10
    assert _counts(upload_api.engine, upload_api.schema)["processing_job"] == 0
    assert _counts(upload_api.engine, upload_api.schema)["source_asset"] == 0
    assert not _store_file(upload_api.root, upload["asset_prefix"]).exists()
    assert not _staging_file(upload_api.root, upload["asset_prefix"]).exists()
    space = _space(upload_api.engine, upload_api.schema)
    assert (space["used_bytes"], space["reserved_bytes"]) == (0, 10)
