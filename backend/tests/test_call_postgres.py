"""Real PostgreSQL negatives for current context authority, grants and facts."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import threading

import pytest
from sqlalchemy import text

from rag_app.adapters.call_postgres import CallRepository
from rag_app.contracts.errors import GuardError
from rag_app.contracts.errors import SafeError
from rag_app.modules.execution.calls import ExecutionFence, LockOrder
from rag_app.modules.ledger.facts import (
    CostFact, LateFact, ResultFact, UsageFact,
)

pytestmark = pytest.mark.postgres


def now() -> datetime:
    return datetime.now(timezone.utc)


def count_calls(context) -> int:
    with context.engine.connect() as connection:
        return connection.execute(text(
            f'SELECT count(*) FROM "{context.schema}".execution_call'
        )).scalar_one()


def call_state(context, call_id: str):
    with context.engine.connect() as connection:
        return connection.execute(text(
            f'SELECT state, grant_id, usage_status, prompt_tokens, '
            f'provider_ref, reconciliation_status '
            f'FROM "{context.schema}".execution_call WHERE call_id=:call_id'
        ), {"call_id": call_id}).one()


def prepare(context, current, *, stage="embedding", request_hash="request-1"):
    return context.lifecycle.prepare(
        context.uow, fence=current.fence(), holder_id=current.holder_id,
        space_id=current.space_id, purpose=current.purpose, stage=stage,
        config_fingerprint=current.config_fingerprint,
        request_hash=request_hash, now=now(),
    )


def test_real_call_lifecycle_and_single_grant(call_persistence):
    context = call_persistence
    current = context.initialize_context(context_id="context-a")
    call_id = prepare(context, current)
    grant = context.lifecycle.mark_may_have_sent(
        context.uow, call_id=call_id, fence=current.fence(),
        boot_id="boot-1", child_instance="child-1", now=now(),
    )
    assert grant is not None and grant.call_id == call_id
    assert call_state(context, call_id)[0] == "may_have_sent"
    assert context.lifecycle.mark_may_have_sent(
        context.uow, call_id=call_id, fence=current.fence(),
        boot_id="boot-2", child_instance="child-2", now=now(),
    ) is None

    pending = prepare(context, current, request_hash="request-2")
    context.lifecycle.terminate_context(
        context.uow, context_id=current.context_id,
    )
    # The physical context row is terminal; the old fence proves no more grant.
    assert context.lifecycle.mark_may_have_sent(
        context.uow, call_id=pending, fence=current.fence(),
        boot_id="boot-3", child_instance="child-3", now=now(),
    ) is None
    assert call_state(context, pending) == (
        "prepared", None, "unknown", None, None, "none",
    )

    # A restart constructs a fresh lifecycle over the same persisted state.
    from rag_app.bootstrap.runtime import build_call_lifecycle

    restarted = build_call_lifecycle(context.control, context.schema)
    assert restarted.mark_may_have_sent(
        context.uow, call_id=pending, fence=current.fence(),
        boot_id="boot-4", child_instance="child-4", now=now(),
    ) is None
    assert count_calls(context) == 2
    assert call_state(context, pending)[1] is None


def test_real_terminal_idempotency_and_late_facts(call_persistence):
    context = call_persistence
    current = context.initialize_context(context_id="context-b")
    call_id = prepare(context, current)
    context.lifecycle.mark_may_have_sent(
        context.uow, call_id=call_id, fence=current.fence(),
        boot_id="boot-1", child_instance="child-1", now=now(),
    )
    result = ResultFact(
        outcome="responded", provider_ref="provider-1",
        usage=UsageFact("reported", 10, 5, 15),
        cost=CostFact("estimated", Decimal("0.0025"), "USD", "list_price"),
        at=now(),
    )
    context.lifecycle.record_result(
        context.uow, call_id=call_id, fence=current.fence(), result=result,
    )
    before = call_state(context, call_id)
    context.lifecycle.record_result(
        context.uow, call_id=call_id, fence=current.fence(), result=result,
    )
    assert call_state(context, call_id) == before
    with context.engine.connect() as connection:
        assert connection.execute(text(
            f'SELECT count(*) FROM "{context.schema}".ledger_call_fact '
            "WHERE call_id=:call_id"
        ), {"call_id": call_id}).scalar_one() == 1

    conflicting = LateFact(
        provider_ref="provider-2",
        usage=UsageFact("reported", 99, 1, 100),
        cost=CostFact("actual", Decimal("0.75"), "USD", "invoice"),
        source="reconciliation", received_at=now(),
    )
    outcome = context.lifecycle.record_late_fact(
        context.uow, call_id=call_id, fact=conflicting,
    )
    assert outcome.disposition == "conflict"
    after = call_state(context, call_id)
    assert after[0] == before[0]
    assert after[2:5] == before[2:5]
    assert after[5] == "required"

    duplicate = context.lifecycle.record_late_fact(
        context.uow, call_id=call_id, fact=conflicting,
    )
    assert duplicate.disposition == "duplicate"
    with context.engine.connect() as connection:
        assert connection.execute(text(
            f'SELECT count(*) FROM "{context.schema}".ledger_call_fact '
            "WHERE call_id=:call_id"
        ), {"call_id": call_id}).scalar_one() == 2

    # Rotating the independent epoch does not block the late-fact path.
    from rag_app.adapters.epoch_control import initialize_epoch_control

    replacement = context.control_path.with_name("rotated.json")
    initialize_epoch_control(replacement, deployment_id="rotated")
    context.control._path = replacement
    late = LateFact(
        # Same reported usage as the terminal call, no new provider reference:
        # a genuinely non-conflicting observation that must survive rotation.
        provider_ref=None, usage=UsageFact("reported", 10, 5, 15),
        cost=None, source="reconciliation", received_at=now(),
    )
    assert context.lifecycle.record_late_fact(
        context.uow, call_id=call_id, fact=late,
    ).disposition == "appended"
    assert call_state(context, call_id)[2:5] == before[2:5]


def test_real_late_fact_does_not_take_parent_lock(call_persistence):
    context = call_persistence
    current = context.initialize_context(context_id="context-c")
    call_id = prepare(context, current)
    context.lifecycle.mark_may_have_sent(
        context.uow, call_id=call_id, fence=current.fence(),
        boot_id="boot-1", child_instance="child-1", now=now(),
    )
    release = threading.Event()
    outcome = {}

    def late_writer():
        outcome["value"] = context.lifecycle.record_late_fact(
            context.uow, call_id=call_id,
            fact=LateFact(
                provider_ref=None, usage=UsageFact("reported", 2, None, 2),
                cost=None, source="reconciliation", received_at=now(),
            ),
        )

    with context.engine.connect() as blocker:
        blocker.begin()
        blocker.execute(text(
            f'SELECT context_id FROM "{context.schema}".execution_context '
            "WHERE context_id=:context_id FOR UPDATE"
        ), {"context_id": current.context_id})
        worker = threading.Thread(target=late_writer)
        worker.start()
        try:
            worker.join(timeout=5)
            assert not worker.is_alive(), "late fact waited on the parent context"
            assert outcome["value"].disposition == "appended"
        finally:
            release.set()
            blocker.rollback()
            worker.join(timeout=5)


def test_real_failed_transaction_leaves_no_call(call_persistence):
    context = call_persistence
    current = context.initialize_context(context_id="context-d")
    call_id = "call_" + "f" * 32
    with pytest.raises(SafeError):
        with context.uow.transaction() as session:
            CallRepository(session, schema=context.schema).insert_call(
                call_id=call_id, fence=current.fence(),
                holder_id=current.holder_id, space_id=current.space_id,
                purpose=current.purpose, stage="embedding",
                config_fingerprint=current.config_fingerprint,
                request_hash="request-failed", now=now(),
            )
            raise RuntimeError("injected after insert")
    assert count_calls(context) == 0
    with context.engine.connect() as connection:
        assert connection.execute(text(
            f'SELECT count(*) FROM "{context.schema}".execution_call '
            "WHERE call_id=:call_id"
        ), {"call_id": call_id}).scalar_one() == 0

    prepared = prepare(context, current, request_hash="request-ok")
    with pytest.raises(SafeError):
        with context.uow.transaction() as session:
            repository = CallRepository(session, schema=context.schema)
            record = repository.lock_call(prepared)
            repository.mark_may_have_sent(
                record, grant_id="grant_" + "e" * 32,
                boot_id="boot-1", child_instance="child-1", now=now(),
            )
            raise RuntimeError("injected after mark")
    assert call_state(context, prepared) == (
        "prepared", None, "unknown", None, None, "none",
    )


def test_real_epoch_mirror_restart_and_contradiction(call_persistence, monkeypatch):
    context = call_persistence
    first = context.control.current()
    second = context.control.current()
    assert first.epoch == second.epoch

    from rag_app.bootstrap.config import Settings
    from rag_app.bootstrap.runtime import build_runtime

    monkeypatch.setenv(
        "RAG_EPOCH_CONTROL_FILE", str(context.control_path),
    )
    runtime = build_runtime(Settings())
    try:
        runtime.check_database()
        assert context.control.current().epoch == first.epoch
    finally:
        runtime.close()

    current = context.initialize_context(context_id="context-e")
    before = count_calls(context)
    with context.engine.begin() as connection:
        connection.execute(text(
            f'UPDATE "{context.schema}".rag_epoch_mirror '
            "SET epoch=:epoch"
        ), {"epoch": "z" * 43})
    with pytest.raises(GuardError, match="EPOCH_MIRROR_MISMATCH"):
        context.lifecycle.prepare(
            context.uow, fence=current.fence(), holder_id=current.holder_id,
            space_id=current.space_id, purpose=current.purpose,
            stage="embedding", config_fingerprint=current.config_fingerprint,
            request_hash="request-mirror", now=now(),
        )
    assert count_calls(context) == before
    with context.engine.begin() as connection:
        connection.execute(text(
            f'DELETE FROM "{context.schema}".rag_epoch_mirror'
        ))
    with pytest.raises(GuardError, match="EPOCH_MIRROR_MISSING"):
        context.lifecycle.prepare(
            context.uow, fence=current.fence(), holder_id=current.holder_id,
            space_id=current.space_id, purpose=current.purpose,
            stage="embedding", config_fingerprint=current.config_fingerprint,
            request_hash="request-missing", now=now(),
        )
    assert count_calls(context) == before


def test_real_reverse_lock_order_is_rejected(call_persistence):
    context = call_persistence
    current = context.initialize_context(context_id="context-f")
    call_id = prepare(context, current)
    with context.uow.transaction() as session:
        repository = CallRepository(
            session, schema=context.schema, lock_order=LockOrder(),
        )
        assert repository.lock_call(call_id) is not None
        with pytest.raises(GuardError, match="CALL_LOCK_ORDER_INVALID"):
            repository.lock_context(current.context_id)


def test_real_lease_expiry_under_held_context_lock_denies_old_now(
    call_persistence,
):
    context = call_persistence
    current = context.initialize_context(
        context_id="context-g", lease_seconds=2, deadline_seconds=30,
    )
    call_id = prepare(context, current)
    stale_now = datetime.now(timezone.utc)
    outcome = {}

    def attempt():
        outcome["grant"] = context.lifecycle.mark_may_have_sent(
            context.uow, call_id=call_id, fence=current.fence(),
            boot_id="boot-1", child_instance="child-1", now=stale_now,
        )

    with context.engine.connect() as blocker:
        blocker.begin()
        blocker.execute(text(
            f'SELECT context_id FROM "{context.schema}".execution_context '
            "WHERE context_id=:context_id FOR UPDATE"
        ), {"context_id": current.context_id})
        worker = threading.Thread(target=attempt)
        worker.start()
        try:
            # The worker blocks on the real context row until the lease has
            # actually expired; its pre-lock 'now' is still early.
            worker.join(timeout=3.5)
        finally:
            blocker.rollback()
            worker.join(timeout=5)
    assert not worker.is_alive()
    assert outcome["grant"] is None
    assert call_state(context, call_id) == (
        "prepared", None, "unknown", None, None, "none",
    )
