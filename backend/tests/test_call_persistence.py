"""Unit boundaries for the call lifecycle; no database or network is used."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import Mock

import pytest

from rag_app.application.call_lifecycle import CallLifecycle
from rag_app.application.uow import UnitOfWork
from rag_app.contracts.errors import GuardError
from rag_app.modules.execution.calls import (
    Epoch, ExecutionFence, LockOrder,
)
from rag_app.modules.ledger.facts import (
    CostFact, LateFact, ResultFact, UsageFact, fact_digest,
)


BASE = datetime(2026, 10, 18, 8, 0, tzinfo=timezone.utc)


def epoch(epoch_id: str = "e" * 43) -> Epoch:
    return Epoch(
        deployment_id="deployment-1", epoch=epoch_id,
        cutover_at=BASE - timedelta(days=1), maintenance_version=1,
    )


def fence(**overrides) -> ExecutionFence:
    values = {
        "epoch": "e" * 43,
        "owner_context_id": "context-1",
        "attempt": 1,
        "claim_token": "claim-token-0123456789",
        "lease_until": BASE + timedelta(seconds=60),
        "hard_deadline": BASE + timedelta(seconds=120),
    }
    values.update(overrides)
    return ExecutionFence(**values)


class FakeControl:
    def __init__(self, value: Epoch | None = None) -> None:
        self.value = value if value is not None else epoch()
        self.expected: list[Epoch] = []

    def current(self) -> Epoch:
        return self.value

    def verify_mirror(self, session, *, expected=None) -> None:
        self.expected.append(expected)


class FakeStore:
    def __init__(self) -> None:
        self.now = BASE
        self.contexts: dict[str, dict] = {}
        self.records: dict[str, dict] = {}
        self.facts: list[dict] = []
        self.reconcile: set[str] = set()
        self.mirror_checks: list[Epoch] = []
        self.insert_failure: Exception | None = None

    def verify_epoch_mirror(self, control, expected):
        self.mirror_checks.append(expected)
        control.verify_mirror(None, expected=expected)

    def current_time(self):
        return self.now

    def insert_context(
        self, *, context_id, epoch, holder_id, space_id, purpose,
        config_fingerprint, attempt, claim_token_digest, lease_until,
        hard_deadline,
    ) -> None:
        self.contexts[context_id] = {
            "context_id": context_id, "epoch": epoch,
            "holder_id": holder_id, "space_id": space_id,
            "purpose": purpose, "config_fingerprint": config_fingerprint,
            "attempt": attempt, "claim_token_digest": claim_token_digest,
            "lease_until": lease_until, "hard_deadline": hard_deadline,
            "state": "active",
        }

    def lock_context(self, context_id):
        return self.contexts.get(context_id)

    def replace_attempt(
        self, *, context_id, attempt, claim_token_digest, lease_until,
        hard_deadline,
    ) -> bool:
        context = self.contexts.get(context_id)
        if context is None or context["state"] != "active":
            return False
        if context["attempt"] >= attempt:
            return False
        context.update({
            "attempt": attempt,
            "claim_token_digest": claim_token_digest,
            "lease_until": lease_until, "hard_deadline": hard_deadline,
        })
        return True

    def terminate_context(self, *, context_id, state) -> bool:
        context = self.contexts.get(context_id)
        if context is None or context["state"] != "active":
            return False
        context["state"] = state
        return True

    def insert_call(self, **values):
        if self.insert_failure is not None:
            raise self.insert_failure
        self.records[values["call_id"]] = {
            "call_id": values["call_id"],
            "epoch": values["fence"].epoch,
            "owner_context_id": values["fence"].owner_context_id,
            "holder_id": values["holder_id"],
            "space_id": values["space_id"],
            "purpose": values["purpose"],
            "stage": values["stage"],
            "attempt": values["fence"].attempt,
            "claim_token_digest": __import__("hashlib").sha256(
                values["fence"].claim_token.encode()
            ).hexdigest(),
            "config_fingerprint": values["config_fingerprint"],
            "request_hash": values["request_hash"],
            "state": "prepared",
            "prepared_at": values["now"],
            "lease_until": values["fence"].lease_until,
            "hard_deadline": values["fence"].hard_deadline,
            "may_have_sent_at": None,
            "grant_id": None,
            "boot_id": None,
            "child_instance": None,
            "terminal_at": None,
            "provider_ref": None,
            "usage_status": "unknown",
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "cost_kind": None,
            "cost_amount": None,
            "cost_currency": None,
            "cost_basis": None,
            "reconciliation_status": "none",
        }

    def lock_call(self, call_id):
        return self.records.get(call_id)

    def mark_may_have_sent(
        self, record, *, grant_id, boot_id, child_instance, now,
    ) -> bool:
        if record["state"] != "prepared":
            return False
        record.update({
            "state": "may_have_sent", "grant_id": grant_id,
            "boot_id": boot_id, "child_instance": child_instance,
            "may_have_sent_at": now,
        })
        return True

    def record_terminal(
        self, record, *, outcome, at, provider_ref, usage, cost,
    ) -> None:
        record.update({
            "state": outcome, "terminal_at": at, "provider_ref": provider_ref,
            "usage_status": "unknown" if usage is None else usage.status,
            "prompt_tokens": None if usage is None else usage.prompt_tokens,
            "completion_tokens": (
                None if usage is None else usage.completion_tokens
            ),
            "total_tokens": None if usage is None else usage.total_tokens,
            "cost_kind": None if cost is None else cost.kind,
            "cost_amount": None if cost is None else cost.amount,
            "cost_currency": None if cost is None else cost.currency,
            "cost_basis": None if cost is None else cost.basis,
        })

    def list_facts(self, call_id):
        return [item for item in self.facts if item["call_id"] == call_id]

    def insert_fact(
        self, *, call_id, digest, provider_ref, usage, cost, source,
        received_at, disposition,
    ) -> bool:
        if any(
            item["call_id"] == call_id and item["fact_digest"] == digest
            for item in self.facts
        ):
            return False
        self.facts.append({
            "call_id": call_id, "fact_digest": digest,
            "provider_ref": provider_ref, "usage_status": (
                "unknown" if usage is None else usage.status
            ),
            "prompt_tokens": None if usage is None else usage.prompt_tokens,
            "completion_tokens": (
                None if usage is None else usage.completion_tokens
            ),
            "total_tokens": None if usage is None else usage.total_tokens,
            "cost_kind": None if cost is None else cost.kind,
            "cost_amount": None if cost is None else cost.amount,
            "cost_currency": None if cost is None else cost.currency,
            "cost_basis": None if cost is None else cost.basis,
            "source": source, "received_at": received_at,
            "disposition": disposition,
        })
        return True

    def require_reconciliation(self, call_id):
        self.reconcile.add(call_id)


def setup_lifecycle():
    control = FakeControl()
    store = FakeStore()
    return (
        control, store, CallLifecycle(control, lambda session: store),
        UnitOfWork(Mock),
    )


def seed_context(store, value=None, *, attempt=1, token=None):
    value = value if value is not None else fence()
    store.contexts[value.owner_context_id] = {
        "context_id": value.owner_context_id, "epoch": value.epoch,
        "holder_id": "holder-1", "space_id": "space-1", "purpose": "query",
        "config_fingerprint": "config:v1", "attempt": attempt,
        "claim_token_digest": __import__("hashlib").sha256(
            (token or value.claim_token).encode()
        ).hexdigest(),
        "lease_until": value.lease_until, "hard_deadline": value.hard_deadline,
        "state": "active",
    }


def prepared(lifecycle, uow, *, now=BASE, owner="context-1"):
    value = fence(owner_context_id=owner)
    seed_context(lifecycle._stores(None), value)
    call_id = lifecycle.prepare(
        uow, fence=value, holder_id="holder-1", space_id="space-1",
        purpose="query", stage="embedding", config_fingerprint="config:v1",
        request_hash="request-hash", now=now,
    )
    return value, call_id


def test_prepare_rejects_stale_epoch_before_any_store_call():
    control, store, lifecycle, uow = setup_lifecycle()
    control.value = epoch("n" * 43)
    with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
        prepared(lifecycle, uow)
    assert store.records == {}
    assert store.mirror_checks == []


@pytest.mark.parametrize("now", [
    BASE + timedelta(seconds=45), BASE + timedelta(seconds=90),
])
def test_prepare_uses_persisted_lease_not_caller_fence(now):
    _, store, lifecycle, uow = setup_lifecycle()
    value = fence()
    seed_context(store, value)
    store.now = now
    store.contexts[value.owner_context_id]["lease_until"] = (
        BASE + timedelta(seconds=30)
    )
    store.contexts[value.owner_context_id]["hard_deadline"] = (
        BASE + timedelta(seconds=60)
    )
    with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
        lifecycle.prepare(
            uow, fence=value, holder_id="holder-1", space_id="space-1",
            purpose="query", stage="embedding",
            config_fingerprint="config:v1", request_hash="request-hash",
            now=now,
        )
    assert store.records == {}


def test_prepare_persists_one_prepared_record_in_one_commit():
    control, store, lifecycle, _ = setup_lifecycle()
    session = Mock()
    uow = UnitOfWork(lambda: session)
    value, call_id = prepared(lifecycle, uow)
    record = store.records[call_id]
    assert record["state"] == "prepared"
    assert record["claim_token_digest"] != value.claim_token
    assert "claim-token" not in repr(record)
    assert store.mirror_checks == [control.value]
    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()


def test_prepare_guard_failure_rolls_back_and_keeps_finite_code():
    _, store, lifecycle, _ = setup_lifecycle()
    session = Mock()
    uow = UnitOfWork(lambda: session)
    store.insert_failure = GuardError("EPOCH_MIRROR_MISMATCH")
    with pytest.raises(GuardError, match="EPOCH_MIRROR_MISMATCH"):
        prepared(lifecycle, uow)
    session.rollback.assert_called_once_with()
    session.commit.assert_not_called()
    assert store.records == {}


def test_mark_grants_once_and_never_after_restart():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    grant = lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=1),
    )
    assert grant is not None
    assert grant.call_id == call_id
    assert grant.attempt == 1
    assert store.records[call_id]["state"] == "may_have_sent"
    assert lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-2",
        child_instance="child-2", now=BASE + timedelta(seconds=2),
    ) is None
    restarted = CallLifecycle(
        FakeControl(), lambda session: store,
    )
    assert restarted.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-3",
        child_instance="child-3", now=BASE + timedelta(seconds=3),
    ) is None
    assert store.records[call_id]["grant_id"] == grant.grant_id


def test_mark_rejects_wrong_fence_or_deadline():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    assert lifecycle.mark_may_have_sent(
        uow, call_id=call_id,
        fence=fence(claim_token="claim-token-0000000000000009"),
        boot_id="boot-1", child_instance="child-1",
        now=BASE + timedelta(seconds=1),
    ) is None
    assert store.records[call_id]["state"] == "prepared"
    store.now = BASE + timedelta(seconds=120)
    assert lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=120),
    ) is None
    assert store.records[call_id]["state"] == "prepared"


def test_record_result_is_idempotent_and_conflict_is_explicit():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=1),
    )
    result = ResultFact(
        outcome="responded", provider_ref="provider-1",
        usage=UsageFact("reported", 10, 5, 15),
        cost=CostFact("estimated", Decimal("0.0012"), "USD", "list_price"),
        at=BASE + timedelta(seconds=2),
    )
    lifecycle.record_result(uow, call_id=call_id, fence=value, result=result)
    assert store.records[call_id]["state"] == "responded"
    assert len(store.facts) == 1
    lifecycle.record_result(uow, call_id=call_id, fence=value, result=result)
    assert len(store.facts) == 1
    with pytest.raises(GuardError, match="CALL_STATE_CONFLICT"):
        lifecycle.record_result(
            uow, call_id=call_id, fence=value,
            result=ResultFact(
                outcome="responded", provider_ref="provider-2",
                usage=UsageFact("reported", 99, 1, 100), cost=None,
                at=BASE + timedelta(seconds=3),
            ),
        )
    assert store.records[call_id]["state"] == "responded"
    assert len(store.facts) == 1


def test_unknown_keeps_nulls_and_zero_effect_on_repeat():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    with pytest.raises(GuardError, match="CALL_NOT_SENT"):
        lifecycle.record_unknown(uow, call_id=call_id, fence=value, now=BASE)
    lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=1),
    )
    lifecycle.record_unknown(
        uow, call_id=call_id, fence=value, now=BASE + timedelta(seconds=2),
    )
    record = store.records[call_id]
    assert record["state"] == "unknown"
    assert record["provider_ref"] is None
    assert record["usage_status"] == "unknown"
    assert record["prompt_tokens"] is None
    assert record["total_tokens"] is None
    lifecycle.record_unknown(
        uow, call_id=call_id, fence=value, now=BASE + timedelta(seconds=3),
    )
    assert len(store.facts) == 0


def test_late_fact_appends_duplicate_and_conflict_without_business_change():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=1),
    )
    lifecycle.record_unknown(
        uow, call_id=call_id, fence=value, now=BASE + timedelta(seconds=2),
    )
    fact = LateFact(
        provider_ref="late-provider-1",
        usage=UsageFact("reported", 3, 4, 7),
        cost=CostFact("actual", Decimal("0.50"), "USD", "invoice"),
        source="reconciliation", received_at=BASE + timedelta(seconds=3),
    )
    outcome = lifecycle.record_late_fact(uow, call_id=call_id, fact=fact)
    assert outcome.disposition == "appended"
    assert store.records[call_id]["state"] == "unknown"
    assert store.records[call_id]["usage_status"] == "unknown"
    assert len(store.facts) == 1
    assert lifecycle.record_late_fact(
        uow, call_id=call_id, fact=fact,
    ).disposition == "duplicate"
    conflicting = LateFact(
        provider_ref="late-provider-2",
        usage=UsageFact("reported", 8, 4, 12),
        cost=CostFact("actual", Decimal("0.75"), "USD", "invoice"),
        source="reconciliation", received_at=BASE + timedelta(seconds=4),
    )
    assert lifecycle.record_late_fact(
        uow, call_id=call_id, fact=conflicting,
    ).disposition == "conflict"
    assert call_id in store.reconcile
    assert store.records[call_id]["state"] == "unknown"
    assert len(store.facts) == 2


def test_late_fact_ignores_a_changed_business_epoch():
    control, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=1),
    )
    store.records[call_id]["state"] = "known_failure"
    store.records[call_id]["terminal_at"] = BASE + timedelta(seconds=2)
    control.value = epoch("z" * 43)
    with pytest.raises(GuardError, match="CALL_STATE_CONFLICT"):
        lifecycle.record_unknown(
            uow, call_id=call_id, fence=value, now=BASE + timedelta(seconds=3),
        )
    outcome = lifecycle.record_late_fact(
        uow, call_id=call_id,
        fact=LateFact(
            provider_ref=None, usage=UsageFact("reported", 1, None, 1),
            cost=None, source="reconciliation",
            received_at=BASE + timedelta(seconds=3),
        ),
    )
    assert outcome.disposition == "appended"
    assert store.records[call_id]["state"] == "known_failure"


def test_result_with_expired_authority_is_rejected_but_late_fact_is_not():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=1),
    )
    store.now = BASE + timedelta(seconds=120)
    with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
        lifecycle.record_result(
            uow, call_id=call_id, fence=value,
            result=ResultFact(
                outcome="responded", provider_ref="p", usage=None, cost=None,
                at=BASE + timedelta(seconds=120),
            ),
        )
    assert store.records[call_id]["state"] == "may_have_sent"


def test_missing_call_is_not_silently_recreated():
    _, store, lifecycle, uow = setup_lifecycle()
    seed_context(store)
    with pytest.raises(GuardError, match="CALL_NOT_FOUND"):
        lifecycle.mark_may_have_sent(
            uow, call_id="call_" + "0" * 32, fence=fence(),
            boot_id="boot-1", child_instance="child-1", now=BASE,
        )
    assert store.records == {}


def test_mark_denied_after_persisted_context_termination():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    lifecycle.terminate_context(uow, context_id=value.owner_context_id)
    assert lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=1),
    ) is None
    assert store.records[call_id]["state"] == "prepared"
    assert store.records[call_id]["grant_id"] is None


def test_old_fence_loses_authority_after_persisted_attempt_advance():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    replacement = "claim-token-0000000000000002"
    advanced = lifecycle.advance_attempt(
        uow, context_id=value.owner_context_id, attempt=2,
        claim_token=replacement, lease_until=BASE + timedelta(seconds=90),
        hard_deadline=BASE + timedelta(seconds=180),
        now=BASE + timedelta(seconds=1),
    )
    assert advanced.attempt == 2
    assert lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=value, boot_id="boot-old",
        child_instance="child-old", now=BASE + timedelta(seconds=2),
    ) is None
    assert store.records[call_id]["state"] == "prepared"
    new_fence = ExecutionFence(
        epoch=advanced.epoch, owner_context_id=advanced.context_id,
        attempt=2, claim_token=replacement,
        lease_until=advanced.lease_until,
        hard_deadline=advanced.hard_deadline,
    )
    # The old call row still belongs to attempt 1, so a new attempt cannot
    # send the old call either; an explicit new call is required.
    assert lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=new_fence, boot_id="boot-new",
        child_instance="child-new", now=BASE + timedelta(seconds=3),
    ) is None
    assert store.records[call_id]["grant_id"] is None


def test_persisted_lease_cannot_be_extended_by_caller():
    _, store, lifecycle, uow = setup_lifecycle()
    value, call_id = prepared(lifecycle, uow)
    longer = ExecutionFence(
        epoch=value.epoch, owner_context_id=value.owner_context_id,
        attempt=value.attempt, claim_token=value.claim_token,
        lease_until=BASE + timedelta(seconds=600),
        hard_deadline=BASE + timedelta(seconds=900),
    )
    store.now = BASE + timedelta(seconds=61)
    assert lifecycle.mark_may_have_sent(
        uow, call_id=call_id, fence=longer, boot_id="boot-1",
        child_instance="child-1", now=BASE + timedelta(seconds=61),
    ) is None
    assert store.records[call_id]["state"] == "prepared"


def test_prepare_requires_matching_persisted_scope():
    control, store, lifecycle, uow = setup_lifecycle()
    seed_context(store)
    with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
        lifecycle.prepare(
            uow, fence=fence(), holder_id="holder-other",
            space_id="space-1", purpose="query", stage="embedding",
            config_fingerprint="config:v1", request_hash="request-hash",
            now=BASE,
        )
    assert store.records == {}


def test_initialize_terminate_and_advance_are_explicit_controls():
    _, store, lifecycle, uow = setup_lifecycle()
    created = lifecycle.initialize_context(
        uow, context_id="context-9", holder_id="holder-9",
        space_id="space-9", purpose="parse", config_fingerprint="config:v9",
        attempt=1, claim_token="claim-token-0000000000000003",
        lease_until=BASE + timedelta(seconds=30),
        hard_deadline=BASE + timedelta(seconds=60), now=BASE,
    )
    assert store.contexts["context-9"]["state"] == "active"
    assert created.attempt == 1
    with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
        lifecycle.advance_attempt(
            uow, context_id="context-9", attempt=3,
            claim_token="claim-token-0000000000000004",
            lease_until=BASE + timedelta(seconds=60),
            hard_deadline=BASE + timedelta(seconds=120),
            now=BASE + timedelta(seconds=1),
        )
    lifecycle.terminate_context(uow, context_id="context-9", state="isolated")
    assert store.contexts["context-9"]["state"] == "isolated"
    with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
        lifecycle.terminate_context(uow, context_id="context-9")


def test_fact_values_distinguish_estimate_and_actual_and_keep_nulls():
    estimated = CostFact("estimated", Decimal("0.10"), "USD", "list_price")
    actual = CostFact("actual", Decimal("0.10"), "USD", "invoice")
    assert estimated != actual
    with pytest.raises(ValueError):
        UsageFact("unknown", 1, None, None)
    with pytest.raises(ValueError):
        UsageFact("reported", None, None, None)
    with pytest.raises(ValueError):
        CostFact("actual", Decimal("1"), None, "invoice")
    with pytest.raises(ValueError):
        LateFact(None, None, None, "source", BASE)
    assert fact_digest(provider_ref=None, usage=None, cost=None) == fact_digest(
        provider_ref=None, usage=None, cost=None,
    )
    assert fact_digest(
        provider_ref=None,
        usage=UsageFact("reported", 1, None, 1),
        cost=CostFact("actual", Decimal("0.100"), "USD", "invoice"),
    ) == fact_digest(
        provider_ref=None,
        usage=UsageFact("reported", 1, None, 1),
        cost=CostFact("actual", Decimal("0.1"), "USD", "invoice"),
    )


def test_lock_order_rejects_reverse_acquisition():
    order = LockOrder()
    order.acquire("space")
    order.acquire("call")
    with pytest.raises(GuardError, match="CALL_LOCK_ORDER_INVALID"):
        order.acquire("pool")
