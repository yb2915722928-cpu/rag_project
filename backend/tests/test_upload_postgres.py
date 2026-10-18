"""Real-PostgreSQL upload service and 0003 migration developer tests.

The HTTP/native-writer path lives in ``test_upload_api.py``.  This file owns
the transaction, fencing, capacity-ledger and migration facts that must be
proved against the isolated real schema rather than a mock.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import sys
from types import SimpleNamespace
import threading
import uuid

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import inspect, text

from rag_app.adapters.original_store import BoundedWriter, LocalOriginalStore
from rag_app.adapters.postgres import create_uow
from rag_app.adapters.upload_postgres import UploadRepository
from rag_app.application.upload_service import (
    UploadRequestInput, UploadService,
)
from rag_app.contracts.errors import SafeError
from rag_app.modules.library.sessions import AuthContext, digest_secret
from rag_app.modules.library.uploads import UploadLimits


pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        sys.platform != "linux",
        reason="Original storage and writer semantics require Linux.",
    ),
]

TABLE_0003 = {
    "account", "web_session", "program_credential", "space_control",
    "knowledge_base", "kb_maintainer", "space_member", "document",
    "upload_operation", "document_candidate", "document_version",
    "source_asset", "processing_job", "capacity_transition",
}
TABLE_0002 = {
    "rag_epoch_mirror", "execution_context", "execution_call",
    "ledger_call_fact",
}


def _uuid7() -> str:
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


def _config() -> Config:
    from pathlib import Path

    return Config(str(Path(__file__).parents[1] / "alembic.ini"))


def _limits(*, max_file_bytes: int = 4096) -> UploadLimits:
    return UploadLimits(
        max_file_bytes=max_file_bytes,
        start_window_s=60,
        total_window_s=60,
        no_progress_s=5,
        lease_s=5,
        renew_s=1,
        chunk_bytes=4096,
        slot_wait_s=0,
        stop_grace_s=1,
        page_bytes=0,
        replay_verify_s=1,
    )


def _seed(engine, schema: str, *, limit: int = 4096) -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    csrf = secrets.token_urlsafe(32)
    q = _quoted(schema)
    with engine.begin() as connection:
        connection.execute(text(
            f"INSERT INTO {q}.account "
            "(account_id, state, verification, epoch) "
            "VALUES ('acct-1', 'active', 'verified', 'epoch-1')"
        ))
        connection.execute(text(
            f"INSERT INTO {q}.space_control "
            "(space_id, state, epoch, used_bytes, reserved_bytes, limit_bytes, "
            "physical_used_bytes, physical_reserved_bytes, physical_budget_bytes) "
            "VALUES ('space-1', 'active', 'epoch-1', 0, 0, :limit, 0, 0, :limit)"
        ), {"limit": limit})
        connection.execute(text(
            f"INSERT INTO {q}.knowledge_base "
            "(knowledge_base_id, space_id, state, guard, docset_revision) "
            "VALUES ('kb-1', 'space-1', 'active', 'idle', 0)"
        ))
        connection.execute(text(
            f"INSERT INTO {q}.kb_maintainer "
            "(knowledge_base_id, account_id, granted_at) "
            "VALUES ('kb-1', 'acct-1', :now)"
        ), {"now": now})
        connection.execute(text(
            f"INSERT INTO {q}.space_member "
            "(space_id, account_id, role, joined_at) "
            "VALUES ('space-1', 'acct-1', 'owner', :now)"
        ), {"now": now})
        connection.execute(text(
            f"INSERT INTO {q}.web_session "
            "(session_id, account_id, space_id, secret_digest, csrf_digest, "
            "epoch, created_at, last_seen_at, idle_expires_at, "
            "absolute_expires_at) "
            "VALUES ('sess-1', 'acct-1', 'space-1', :secret, :csrf, 'epoch-1', "
            ":now, :now, :idle, :absolute)"
        ), {
            "secret": secrets.token_hex(32), "csrf": digest_secret(csrf),
            "now": now, "idle": now + timedelta(hours=1),
            "absolute": now + timedelta(days=1),
        })
    context = AuthContext(
        account_id="acct-1", session_id="sess-1",
        csrf_digest=digest_secret(csrf), epoch="epoch-1",
        channel="web", space_id="space-1", knowledge_base_ids=("kb-1",),
    )
    return SimpleNamespace(context=context)


@pytest.fixture
def upload_pg(isolated_database, tmp_path):
    engine, schema = isolated_database
    command.upgrade(_config(), "head")
    identity = _seed(engine, schema)
    root = tmp_path / "store"
    root.mkdir()
    store = LocalOriginalStore(root, page_bytes=0)
    uow = create_uow(engine)

    def repository(session):
        return UploadRepository(session, schema=schema)

    service = UploadService(
        uow, repository, store=store, limits=_limits(),
    )
    return SimpleNamespace(
        engine=engine, schema=schema, root=root, store=store, uow=uow,
        repository=repository, service=service, context=identity.context,
        limits=_limits(),
    )


def _request(
    operation_id: str | None = None, data: bytes = b"payload", *,
    declared: int | None = None, sha: str | None | object = ...,
    **overrides,
) -> UploadRequestInput:
    values = {
        "upload_operation_id": operation_id or _uuid7(),
        "space_id": "space-1", "knowledge_base_id": "kb-1",
        "filename": "notes.md", "title": "notes",
        "format": "markdown",
        "declared_bytes": len(data) if declared is None else declared,
        "original_sha256": _sha(data) if sha is ... else sha,
    }
    values.update(overrides)
    return UploadRequestInput(**values)


def _create(container, request: UploadRequestInput, *, service=None):
    return (service or container.service).create_or_replay(
        container.context, request,
    )


def _begin(container, candidate_id: str, *, service=None):
    return (service or container.service).begin_writer(
        container.context, candidate_id,
    )


def _write_final(container, begun, data: bytes):
    paths = container.store.prepare_paths(begun.record["asset_prefix"])
    with BoundedWriter(
        staging=paths["staging"], final=paths["final"],
        max_bytes=begun.max_bytes, page_bytes=0,
    ) as writer:
        writer.feed(data)
        return writer.finish()


def _one(engine, schema: str, statement: str, **parameters):
    with engine.connect() as connection:
        return connection.execute(
            text(statement.format(q=_quoted(schema))), parameters,
        ).mappings().one()


def _upload(container, operation_id: str):
    return _one(
        container.engine, container.schema,
        "SELECT * FROM {q}.upload_operation "
        "WHERE upload_operation_id = :operation_id",
        operation_id=operation_id,
    )


def _candidate(container, candidate_id: str):
    return _one(
        container.engine, container.schema,
        "SELECT * FROM {q}.document_candidate WHERE candidate_id = :candidate_id",
        candidate_id=candidate_id,
    )


def _counts(container) -> dict[str, int]:
    q = _quoted(container.schema)
    names = (
        "document", "upload_operation", "document_candidate",
        "document_version", "source_asset", "processing_job",
        "capacity_transition",
    )
    with container.engine.connect() as connection:
        return {
            name: connection.execute(
                text(f"SELECT count(*) FROM {q}.{name}")
            ).scalar_one()
            for name in names
        }


def _space(container):
    return _one(
        container.engine, container.schema,
        "SELECT * FROM {q}.space_control WHERE space_id = 'space-1'",
    )


def _transitions(container, upload_row_id: str) -> list[str]:
    with container.engine.connect() as connection:
        return [
            row[0] for row in connection.execute(text(
                f"SELECT operation FROM {_quoted(container.schema)}."
                "capacity_transition WHERE reference_id = :reference_id "
                "ORDER BY operation"
            ), {"reference_id": upload_row_id}).all()
        ]


def _job(container, candidate_id: str):
    return _one(
        container.engine, container.schema,
        "SELECT * FROM {q}.processing_job WHERE candidate_id = :candidate_id",
        candidate_id=candidate_id,
    )


def _asset(container, candidate_id: str):
    return _one(
        container.engine, container.schema,
        "SELECT a.* FROM {q}.source_asset AS a "
        "JOIN {q}.upload_operation AS u ON u.upload_row_id = a.owner_row_id "
        "JOIN {q}.document_candidate AS c ON c.upload_row_id = u.upload_row_id "
        "WHERE c.candidate_id = :candidate_id",
        candidate_id=candidate_id,
    )


def _version(container, candidate_id: str):
    return _one(
        container.engine, container.schema,
        "SELECT v.* FROM {q}.document_version AS v "
        "JOIN {q}.document_candidate AS c "
        "ON c.document_version_id = v.document_version_id "
        "WHERE c.candidate_id = :candidate_id",
        candidate_id=candidate_id,
    )


def _assert_no_processing(container, candidate_id: str) -> None:
    assert _counts(container)["processing_job"] == 0
    assert _counts(container)["source_asset"] == 0
    assert _counts(container)["document_version"] == 0
    assert _candidate(container, candidate_id)["processing_state"] is None


def test_real_concurrent_first_intent_creates_one_row_and_one_reservation(upload_pg):
    data = b"same-key"
    request = _request(data=data)
    barrier = threading.Barrier(2)
    results = []
    failures = []

    def worker():
        try:
            barrier.wait(timeout=5)
            results.append(_create(upload_pg, request))
        except BaseException as exc:
            failures.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
    assert all(not thread.is_alive() for thread in threads)
    assert not failures
    assert sorted(created for created, _ in results) == [False, True]
    candidates = {view.record["candidate_id"] for _, view in results}
    assert len(candidates) == 1
    counts = _counts(upload_pg)
    assert counts == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 0, "source_asset": 0, "processing_job": 0,
        "capacity_transition": 1,
    }
    upload = _upload(upload_pg, request.upload_operation_id)
    assert upload["state"] == "awaiting_upload"
    assert _transitions(upload_pg, upload["upload_row_id"]) == ["reserve"]
    space = _space(upload_pg)
    assert (space["used_bytes"], space["reserved_bytes"]) == (0, len(data))


def test_real_concurrent_completion_has_one_transfer_and_one_job(upload_pg):
    data = b"concurrent-completion"
    request = _request(data=data)
    created, view = _create(upload_pg, request)
    assert created is True
    candidate_id = view.candidate["candidate_id"]
    begun = _begin(upload_pg, candidate_id)
    size, digest = _write_final(upload_pg, begun, data)
    assert size == len(data)
    barrier = threading.Barrier(2)
    results = []
    failures = []

    def worker():
        try:
            barrier.wait(timeout=5)
            results.append(upload_pg.service.complete(
                upload_pg.context, candidate_id,
                attempt=begun.attempt, claim_token=begun.claim_token,
                original_sha256=digest, original_bytes=size,
            ))
        except BaseException as exc:
            failures.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
    assert all(not thread.is_alive() for thread in threads)
    assert not failures
    assert sorted(replayed for replayed, _ in results) == [False, True]
    upload = _upload(upload_pg, request.upload_operation_id)
    candidate = _candidate(upload_pg, candidate_id)
    assert upload["state"] == "original_committed"
    assert upload["original_sha256"] == digest
    assert candidate["processing_state"] == "queued"
    counts = _counts(upload_pg)
    assert counts == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 1, "source_asset": 1, "processing_job": 1,
        "capacity_transition": 2,
    }
    assert _job(upload_pg, candidate_id)["job_state"] == "queued"
    assert _asset(upload_pg, candidate_id)["byte_size"] == len(data)
    assert _version(upload_pg, candidate_id)["original_sha256"] == digest
    assert _transitions(upload_pg, upload["upload_row_id"]) == [
        "commit", "reserve",
    ]
    space = _space(upload_pg)
    assert (space["used_bytes"], space["reserved_bytes"]) == (len(data), 0)
    assert (
        upload_pg.root / "assets" / upload["asset_prefix"][:2]
        / upload["asset_prefix"] / "original"
    ).read_bytes() == data


def test_real_failed_completion_rolls_back_and_retry_has_no_duplicate(upload_pg):
    data = b"rollback-retry"
    request = _request(data=data)
    _, view = _create(upload_pg, request)
    candidate_id = view.candidate["candidate_id"]
    begun = _begin(upload_pg, candidate_id)
    size, digest = _write_final(upload_pg, begun, data)
    upload = _upload(upload_pg, request.upload_operation_id)
    conflict_id = "cap_" + uuid.uuid4().hex
    with upload_pg.engine.begin() as connection:
        connection.execute(text(
            f"INSERT INTO {_quoted(upload_pg.schema)}.capacity_transition "
            "(transition_id, space_id, operation, originals_bytes, "
            "physical_bytes, reference_id, created_at) "
            "VALUES (:transition_id, 'space-1', 'commit', :bytes, :bytes, "
            ":reference_id, clock_timestamp())"
        ), {
            "transition_id": conflict_id, "bytes": len(data),
            "reference_id": upload["upload_row_id"],
        })

    with pytest.raises(SafeError):
        upload_pg.service.complete(
            upload_pg.context, candidate_id,
            attempt=begun.attempt, claim_token=begun.claim_token,
            original_sha256=digest, original_bytes=size,
        )
    assert _upload(upload_pg, request.upload_operation_id)["state"] == "uploading"
    assert _candidate(upload_pg, candidate_id)["upload_state"] == "uploading"
    _assert_no_processing(upload_pg, candidate_id)
    space = _space(upload_pg)
    assert (space["used_bytes"], space["reserved_bytes"]) == (0, len(data))
    assert _transitions(upload_pg, upload["upload_row_id"]) == [
        "commit", "reserve",
    ]

    with upload_pg.engine.begin() as connection:
        connection.execute(text(
            f"DELETE FROM {_quoted(upload_pg.schema)}.capacity_transition "
            "WHERE transition_id = :transition_id"
        ), {"transition_id": conflict_id})
    replayed, _ = upload_pg.service.complete(
        upload_pg.context, candidate_id,
        attempt=begun.attempt, claim_token=begun.claim_token,
        original_sha256=digest, original_bytes=size,
    )
    assert replayed is False
    assert _upload(upload_pg, request.upload_operation_id)["state"] == (
        "original_committed"
    )
    assert _counts(upload_pg) == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 1, "source_asset": 1, "processing_job": 1,
        "capacity_transition": 2,
    }
    assert _transitions(upload_pg, upload["upload_row_id"]) == [
        "commit", "reserve",
    ]
    space = _space(upload_pg)
    assert (space["used_bytes"], space["reserved_bytes"]) == (len(data), 0)


def test_real_new_attempt_fences_old_completion_and_keeps_deadline(upload_pg):
    data = b"old-writer"
    request = _request(data=data)
    _, view = _create(upload_pg, request)
    candidate_id = view.candidate["candidate_id"]
    first = _begin(upload_pg, candidate_id)
    second = _begin(upload_pg, candidate_id)
    assert second.attempt == first.attempt + 1
    assert second.hard_deadline == first.hard_deadline
    size, digest = _write_final(upload_pg, first, data)
    with pytest.raises(SafeError) as caught:
        upload_pg.service.complete(
            upload_pg.context, candidate_id,
            attempt=first.attempt, claim_token=first.claim_token,
            original_sha256=digest, original_bytes=size,
        )
    assert caught.value.code == "UPLOAD_IN_PROGRESS"
    assert _upload(upload_pg, request.upload_operation_id)["state"] == "uploading"
    _assert_no_processing(upload_pg, candidate_id)

    replayed, _ = upload_pg.service.complete(
        upload_pg.context, candidate_id,
        attempt=second.attempt, claim_token=second.claim_token,
        original_sha256=digest, original_bytes=size,
    )
    assert replayed is False
    upload = _upload(upload_pg, request.upload_operation_id)
    assert upload["state"] == "original_committed"
    assert upload["attempt"] == 2
    assert _counts(upload_pg)["processing_job"] == 1
    assert _counts(upload_pg)["source_asset"] == 1


def test_real_expired_late_attempt_cannot_commit_and_keeps_bytes(upload_pg):
    data = b"expired-late"
    request = _request(data=data)
    _, view = _create(upload_pg, request)
    candidate_id = view.candidate["candidate_id"]
    begun = _begin(upload_pg, candidate_id)
    size, digest = _write_final(upload_pg, begun, data)
    upload = _upload(upload_pg, request.upload_operation_id)
    with upload_pg.engine.begin() as connection:
        connection.execute(text(
            f"UPDATE {_quoted(upload_pg.schema)}.upload_operation "
            "SET upload_hard_deadline = clock_timestamp() - interval '1 second' "
            "WHERE upload_row_id = :row_id"
        ), {"row_id": upload["upload_row_id"]})
    expired_deadline = _upload(
        upload_pg, request.upload_operation_id,
    )["upload_hard_deadline"]

    with pytest.raises(SafeError) as caught:
        upload_pg.service.complete(
            upload_pg.context, candidate_id,
            attempt=begun.attempt, claim_token=begun.claim_token,
            original_sha256=digest, original_bytes=size,
        )
    assert caught.value.code == "UPLOAD_EXPIRED"
    upload = _upload(upload_pg, request.upload_operation_id)
    candidate = _candidate(upload_pg, candidate_id)
    assert upload["state"] == "expired"
    assert candidate["upload_state"] == "expired"
    assert upload["claim_token_digest"] is None
    assert upload["upload_hard_deadline"] == expired_deadline
    _assert_no_processing(upload_pg, candidate_id)
    space = _space(upload_pg)
    assert (space["used_bytes"], space["reserved_bytes"]) == (0, len(data))
    assert (
        upload_pg.root / "assets" / upload["asset_prefix"][:2]
        / upload["asset_prefix"] / "original"
    ).read_bytes() == data

    with pytest.raises(SafeError) as caught:
        upload_pg.service.begin_writer(upload_pg.context, candidate_id)
    assert caught.value.code == "UPLOAD_EXPIRED"
    with pytest.raises(SafeError) as caught:
        upload_pg.service.complete(
            upload_pg.context, candidate_id,
            attempt=begun.attempt, claim_token=begun.claim_token,
            original_sha256=digest, original_bytes=size,
        )
    assert caught.value.code == "UPLOAD_EXPIRED"
    assert _upload(
        upload_pg, request.upload_operation_id,
    )["upload_hard_deadline"] == expired_deadline
    assert _counts(upload_pg)["processing_job"] == 0
    assert _counts(upload_pg)["source_asset"] == 0


def test_real_lowered_limits_preserve_accepted_intent_and_reject_new(upload_pg):
    data = b"accepted-before-lowering"
    request = _request(data=data)
    created, view = _create(upload_pg, request)
    assert created is True
    candidate_id = view.candidate["candidate_id"]
    with upload_pg.engine.begin() as connection:
        connection.execute(text(
            f"UPDATE {_quoted(upload_pg.schema)}.space_control "
            "SET limit_bytes = 1 WHERE space_id = 'space-1'"
        ))
    assert _space(upload_pg)["limit_bytes"] == 1

    lowered = UploadService(
        upload_pg.uow, upload_pg.repository, store=upload_pg.store,
        limits=_limits(max_file_bytes=4),
    )
    replayed, replayed_view = _create(upload_pg, request, service=lowered)
    assert replayed is False
    assert replayed_view.record["candidate_id"] == candidate_id
    with pytest.raises(SafeError) as caught:
        lowered.create_or_replay(
            upload_pg.context,
            _request(data=b"12345", declared=5),
        )
    assert caught.value.code == "FILE_LIMIT_EXCEEDED"
    with pytest.raises(SafeError) as caught:
        lowered.create_or_replay(
            upload_pg.context,
            _request(data=b"1234", declared=4),
        )
    assert caught.value.code == "ORIGINAL_CAPACITY_EXCEEDED"

    begun = lowered.begin_writer(upload_pg.context, candidate_id)
    assert begun.max_bytes == len(data)
    size, digest = _write_final(upload_pg, begun, data)
    replayed, _ = lowered.complete(
        upload_pg.context, candidate_id,
        attempt=begun.attempt, claim_token=begun.claim_token,
        original_sha256=digest, original_bytes=size,
    )
    assert replayed is False
    space = _space(upload_pg)
    assert space["limit_bytes"] == 1
    assert (space["used_bytes"], space["reserved_bytes"]) == (len(data), 0)
    assert _upload(upload_pg, request.upload_operation_id)["state"] == (
        "original_committed"
    )
    assert _counts(upload_pg)["processing_job"] == 1


def test_real_0003_cycle_with_intent_downgrades_and_reupgrades(upload_pg):
    data = b"migration-cycle"
    request = _request(data=data)
    created, view = _create(upload_pg, request)
    assert created is True
    candidate_id = view.candidate["candidate_id"]
    begun = _begin(upload_pg, candidate_id)
    size, digest = _write_final(upload_pg, begun, data)
    replayed, _ = upload_pg.service.complete(
        upload_pg.context, candidate_id,
        attempt=begun.attempt, claim_token=begun.claim_token,
        original_sha256=digest, original_bytes=size,
    )
    assert replayed is False
    assert _counts(upload_pg) == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 1, "source_asset": 1, "processing_job": 1,
        "capacity_transition": 2,
    }

    with upload_pg.engine.connect() as connection:
        tables = set(inspect(connection).get_table_names(schema=upload_pg.schema))
    assert TABLE_0003 <= tables

    command.downgrade(_config(), "0002_isolated_calls")
    with upload_pg.engine.connect() as connection:
        downgraded = set(inspect(connection).get_table_names(schema=upload_pg.schema))
        revision = connection.execute(text(
            f'SELECT version_num FROM "{upload_pg.schema}".alembic_version'
        )).scalar_one()
    assert TABLE_0002 <= downgraded
    assert not (TABLE_0003 & downgraded)
    assert revision == "0002_isolated_calls"

    command.upgrade(_config(), "head")
    with upload_pg.engine.connect() as connection:
        upgraded = set(inspect(connection).get_table_names(schema=upload_pg.schema))
        revision = connection.execute(text(
            f'SELECT version_num FROM "{upload_pg.schema}".alembic_version'
        )).scalar_one()
    assert TABLE_0003 <= upgraded
    assert revision == "0003_library_uploads"
    assert candidate_id.startswith("cand_")

    _seed(upload_pg.engine, upload_pg.schema)
    after = _request(data=b"after-cycle")
    created, after_view = _create(upload_pg, after)
    assert created is True
    assert after_view.candidate["candidate_id"].startswith("cand_")
    assert _counts(upload_pg) == {
        "document": 1, "upload_operation": 1, "document_candidate": 1,
        "document_version": 0, "source_asset": 0, "processing_job": 0,
        "capacity_transition": 1,
    }
