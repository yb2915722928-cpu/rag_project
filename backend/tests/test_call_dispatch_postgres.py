"""Real PostgreSQL + real Linux child matrix for one supervised call.

The child only consumes an explicit local fake capability/egress plan; no
provider, DNS, TLS or HTTP peer is contacted.  Every assertion checks the
persisted call/fact rows, not just mock call counts.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sys
import threading
import time
import uuid

import pytest
from sqlalchemy import text

from rag_app.adapters.child_supervisor import LinuxChildSupervisor
from rag_app.application.call_dispatch import (
    CallDispatch,
    EgressDispatch,
    build_egress_dispatch,
)
from rag_app.contracts.errors import GuardError
from rag_app.modules.execution.egress import (
    AddressFamily,
    EgressProfile,
    EgressPurpose,
    EgressRequest,
    EgressTarget,
    HostPort,
    ResolvedAddress,
)
from rag_app.modules.execution.supervision import (
    ChildFailure,
    ChildLimits,
    ChildSlot,
    ChildStage,
    ChildSupervisionError,
    SendState,
)
from rag_app.modules.ledger.facts import (
    CostFact, LateFact, UsageFact,
)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        sys.platform != "linux",
        reason="Real child supervision is a Linux acceptance path.",
    ),
]

ADDRESS = ResolvedAddress(AddressFamily.IPV4, "93.184.216.34")
SECRET = "{{SECRET_gtxjjq3p}}"


def now() -> datetime:
    return datetime.now(timezone.utc)


def api_dispatch(*, stop_after: float = 120.0) -> EgressDispatch:
    profile = EgressProfile(
        EgressPurpose.API, frozenset({HostPort("api.example.com")}),
    )
    target = EgressTarget(
        profile, "api.example.com", 443,
        "/v1/run?signature=" + SECRET,
    )
    request = EgressRequest(
        method="POST",
        headers=(("Content-Type", "application/json"),),
        body=b'{"prompt":"bounded"}',
        api_authorization="Bearer " + SECRET,
    )

    class Resolver:
        calls = 0

        def resolve(self, host, port):
            type(self).calls += 1
            return (ADDRESS,)

    return build_egress_dispatch(
        target, Resolver(), request,
        send_stop_by_monotonic=time.monotonic() + stop_after,
    )


def slot() -> ChildSlot:
    nonce = uuid.uuid4().hex
    return ChildSlot(
        deployment_id="dispatch_test", boot_id="boot_" + nonce,
        slot_id="slot_" + nonce, attempt=1,
    )


def limits() -> ChildLimits:
    return ChildLimits(term_grace_s=0.5, kill_grace_s=2.0)


def assemblies(context, tmp_path):
    supervisor = LinuxChildSupervisor(state_root=tmp_path / "state")
    dispatch = CallDispatch(
        context.lifecycle, lambda: context.uow, supervisor,
        clock=now,
    )
    return dispatch, supervisor


def execute(dispatch, current, **overrides):
    arguments = {
        "slot": slot(), "limits": limits(), "fence": current.fence(),
        "holder_id": current.holder_id, "space_id": current.space_id,
        "purpose": "api", "stage": ChildStage.EGRESS,
        "config_fingerprint": current.config_fingerprint,
        "request_hash": "request-" + uuid.uuid4().hex,
        "egress": api_dispatch(),
    }
    arguments.update(overrides)
    return dispatch.execute(**arguments)


def call_rows(context):
    with context.engine.connect() as connection:
        return connection.execute(text(
            f'SELECT call_id, state, grant_id, usage_status, prompt_tokens, '
            f'completion_tokens, total_tokens, provider_ref, cost_kind, '
            f'cost_amount, reconciliation_status '
            f'FROM "{context.schema}".execution_call ORDER BY call_id'
        )).all()


def fact_rows(context):
    with context.engine.connect() as connection:
        return connection.execute(text(
            f'SELECT call_id, provider_ref, usage_status, prompt_tokens, '
            f'total_tokens, cost_kind, cost_amount, disposition '
            f'FROM "{context.schema}".ledger_call_fact ORDER BY fact_id'
        )).all()


def test_real_end_to_end_one_grant_and_unknown_usage(call_persistence, tmp_path):
    context = call_persistence
    current = context.initialize_context(context_id="context-success")
    dispatch, supervisor = assemblies(context, tmp_path)
    try:
        outcome = execute(dispatch, current)
        assert outcome.send_state is SendState.RESPONSE_RECEIVED
        assert outcome.response_status == 200
        assert outcome.stop_proof is not None and outcome.stop_proof.proven
        assert outcome.fact_recorded is True
        rows = call_rows(context)
        assert len(rows) == 1
        row = rows[0]
        assert row[0] == outcome.call_id and row[1] == "responded"
        assert row[2] == outcome.grant_id
        assert row[3] == "unknown" and row[4:7] == (None, None, None)
        facts = fact_rows(context)
        assert len(facts) == 1 and facts[0][0] == outcome.call_id
        assert facts[0][4] is None
        # A restarted controller cannot obtain a second grant for this call.
        assert context.lifecycle.mark_may_have_sent(
            context.uow, call_id=outcome.call_id, fence=current.fence(),
            boot_id="boot-2", child_instance="child-2", now=now(),
        ) is None
        assert len(call_rows(context)) == 1
        assert len(fact_rows(context)) == 1
    finally:
        assert supervisor.close() is True


def test_real_terminated_context_and_advanced_attempt_block_business(
    call_persistence, tmp_path,
):
    context = call_persistence
    current = context.initialize_context(context_id="context-stale")
    dispatch, supervisor = assemblies(context, tmp_path)
    try:
        context.lifecycle.terminate_context(
            context.uow, context_id=current.context_id,
        )
        with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
            execute(dispatch, current)
        assert call_rows(context) == []

        second = context.initialize_context(context_id="context-advance")
        replacement = "claim-token-0000000000000002"
        advanced = context.lifecycle.advance_attempt(
            context.uow, context_id=second.context_id, attempt=2,
            claim_token=replacement,
            lease_until=now() + timedelta(seconds=300),
            hard_deadline=now() + timedelta(seconds=600), now=now(),
        )
        with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
            execute(dispatch, second)
        assert call_rows(context) == []
        new_fence = advanced.fence()
        # The current attempt can prepare a new call, but the old attempt never
        # did and no business row was written.
        call_id = context.lifecycle.prepare(
            context.uow, fence=new_fence, holder_id=advanced.holder_id,
            space_id=advanced.space_id, purpose=advanced.purpose,
            stage="egress", config_fingerprint=advanced.config_fingerprint,
            request_hash="request-new", now=now(),
        )
        rows = call_rows(context)
        assert len(rows) == 1 and rows[0][0] == call_id
        assert rows[0][1] == "prepared"
    finally:
        assert supervisor.close() is True


def test_real_old_epoch_blocks_before_any_call(call_persistence, tmp_path):
    context = call_persistence
    current = context.initialize_context(context_id="context-epoch")
    dispatch, supervisor = assemblies(context, tmp_path)
    try:
        old_fence = current.fence()
        from rag_app.adapters.epoch_control import initialize_epoch_control

        replacement = tmp_path / "rotated-control.json"
        rotated = initialize_epoch_control(
            replacement, deployment_id="rotated",
        )
        assert rotated.epoch != old_fence.epoch
        # The DB mirror is untouched; current() already shows a new epoch.
        object.__setattr__(context.control, "_path", replacement)
        with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
            execute(dispatch, current)
        assert call_rows(context) == []
        # Restore for fixture teardown; no server source or DB state changed.
        object.__setattr__(
            context.control, "_path", context.control_path,
        )
        assert context.control.current().epoch == old_fence.epoch
    finally:
        assert supervisor.close() is True


class PrepareFails:
    def __init__(self, inner):
        self.inner = inner

    def spawn(self, *args, **kwargs):
        return self.inner.spawn(*args, **kwargs)

    def prepare(self, *args, **kwargs):
        raise ChildSupervisionError(ChildFailure.IPC_PROTOCOL)

    def grant(self, *args, **kwargs):
        return self.inner.grant(*args, **kwargs)

    def receive(self, *args, **kwargs):
        return self.inner.receive(*args, **kwargs)

    def stop(self, *args, **kwargs):
        return self.inner.stop(*args, **kwargs)

    def inspect(self, *args, **kwargs):
        return self.inner.inspect(*args, **kwargs)

    def close(self):
        return self.inner.close()


class GrantFails(PrepareFails):
    def prepare(self, *args, **kwargs):
        return self.inner.prepare(*args, **kwargs)

    def grant(self, *args, **kwargs):
        raise ChildSupervisionError(ChildFailure.IPC_IO)


class ReceiveTimesOut(PrepareFails):
    def prepare(self, *args, **kwargs):
        return self.inner.prepare(*args, **kwargs)

    def receive(self, *args, **kwargs):
        raise ChildSupervisionError(ChildFailure.TIMEOUT)


def test_real_prepare_crash_leaves_prepared_and_no_grant(
    call_persistence, tmp_path,
):
    context = call_persistence
    current = context.initialize_context(context_id="context-before-mark")
    inner = LinuxChildSupervisor(state_root=tmp_path / "state")
    dispatch = CallDispatch(
        context.lifecycle, lambda: context.uow, PrepareFails(inner), clock=now,
    )
    try:
        outcome = execute(dispatch, current)
        assert outcome.failure is ChildFailure.IPC_PROTOCOL
        assert outcome.send_state is SendState.NOT_SENT
        rows = call_rows(context)
        assert len(rows) == 1 and rows[0][1] == "prepared"
        assert rows[0][2] is None
        assert fact_rows(context) == []
        # No grant or business row was written by the failed controller.
        assert outcome.grant_id is None
    finally:
        assert inner.close() is True


def test_real_grant_delivery_crash_is_unknown_null(
    call_persistence, tmp_path,
):
    context = call_persistence
    current = context.initialize_context(context_id="context-after-mark")
    inner = LinuxChildSupervisor(state_root=tmp_path / "state")
    dispatch = CallDispatch(
        context.lifecycle, lambda: context.uow, GrantFails(inner), clock=now,
    )
    try:
        outcome = execute(dispatch, current)
        assert outcome.send_state is SendState.MAY_HAVE_SENT
        assert outcome.failure is ChildFailure.IPC_IO
        rows = call_rows(context)
        assert len(rows) == 1 and rows[0][1] == "unknown"
        assert outcome.grant_id == rows[0][2]
        assert rows[0][3] == "unknown" and rows[0][4:7] == (
            None, None, None,
        )
        assert fact_rows(context) == []
        assert context.lifecycle.record_unknown(
            context.uow, call_id=outcome.call_id, fence=current.fence(),
            now=now(),
        ) is None
        assert call_rows(context)[0][1] == "unknown"
        assert fact_rows(context) == []
    finally:
        assert inner.close() is True


def test_real_response_timeout_is_unknown_and_never_zero(
    call_persistence, tmp_path,
):
    context = call_persistence
    current = context.initialize_context(context_id="context-timeout")
    inner = LinuxChildSupervisor(state_root=tmp_path / "state")
    dispatch = CallDispatch(
        context.lifecycle, lambda: context.uow, ReceiveTimesOut(inner),
        clock=now,
    )
    try:
        outcome = execute(dispatch, current)
        assert outcome.send_state is SendState.MAY_HAVE_SENT
        assert outcome.failure is ChildFailure.TIMEOUT
        assert outcome.stop_proof is not None
        rows = call_rows(context)
        assert len(rows) == 1 and rows[0][1] == "unknown"
        assert rows[0][3] == "unknown" and rows[0][4:7] == (
            None, None, None,
        )
        assert fact_rows(context) == []
    finally:
        assert inner.close() is True


class ResultFails:
    def __init__(self, inner):
        self.inner = inner

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def record_result(self, *args, **kwargs):
        raise GuardError("CALL_FENCE_STALE")

    def record_unknown(self, *args, **kwargs):
        return self.inner.record_unknown(*args, **kwargs)

    def record_late_fact(self, *args, **kwargs):
        return self.inner.record_late_fact(*args, **kwargs)


def test_real_response_before_record_is_unknown_plus_late_fact(
    call_persistence, tmp_path,
):
    context = call_persistence
    current = context.initialize_context(context_id="context-after-response")
    inner = LinuxChildSupervisor(state_root=tmp_path / "state")
    lifecycle = ResultFails(context.lifecycle)
    dispatch = CallDispatch(
        lifecycle, lambda: context.uow, inner, clock=now,
    )
    try:
        outcome = execute(dispatch, current)
        assert outcome.send_state is SendState.RESPONSE_RECEIVED
        assert outcome.response_status == 200
        assert outcome.fact_recorded is False
        assert outcome.late_fact is not None
        rows = call_rows(context)
        assert len(rows) == 1 and rows[0][1] == "unknown"
        assert rows[0][3] == "unknown" and rows[0][4:7] == (
            None, None, None,
        )
        facts = fact_rows(context)
        assert len(facts) == 1 and facts[0][7] == "appended"
    finally:
        assert inner.close() is True


def test_real_late_usage_repeat_and_conflict_do_not_revive(
    call_persistence, tmp_path,
):
    context = call_persistence
    current = context.initialize_context(context_id="context-late")
    dispatch, supervisor = assemblies(context, tmp_path)
    try:
        outcome = execute(dispatch, current)
        assert outcome.fact_recorded is False
        before = call_rows(context)[0]
        late = LateFact(
            provider_ref=None,
            usage=UsageFact("reported", 7, 3, 10),
            cost=CostFact("actual", __import__("decimal").Decimal("0.25"),
                          "USD", "invoice"),
            source="reconciliation", received_at=now(),
        )
        first = context.lifecycle.record_late_fact(
            context.uow, call_id=outcome.call_id, fact=late,
        )
        assert first.disposition in {"appended", "conflict"}
        after = call_rows(context)[0]
        assert after[1] == before[1] and after[3:10] == before[3:10]
        repeat = context.lifecycle.record_late_fact(
            context.uow, call_id=outcome.call_id, fact=late,
        )
        assert repeat.disposition == "duplicate"
        conflicting = LateFact(
            provider_ref=None,
            usage=UsageFact("reported", 99, 1, 100),
            cost=None, source="reconciliation", received_at=now(),
        )
        conflict = context.lifecycle.record_late_fact(
            context.uow, call_id=outcome.call_id, fact=conflicting,
        )
        assert conflict.disposition == "conflict"
        final = call_rows(context)[0]
        assert final[1] == before[1] and final[3:9] == before[3:9]
        assert final[10] == "required"
        assert len(fact_rows(context)) == 3
    finally:
        assert supervisor.close() is True


def test_real_four_fake_capabilities_have_traceable_paths(
    call_persistence, tmp_path,
):
    context = call_persistence
    dispatch, supervisor = assemblies(context, tmp_path)
    try:
        traces = []
        for stage in (
            ChildStage.MODEL, ChildStage.PARSE,
            ChildStage.EMBEDDING, ChildStage.VISION,
        ):
            traces.append(dispatch.execute_fake_stage(
                slot=slot(), limits=limits(), stage=stage,
                payload=b"bounded-local-input",
            ))
        assert [trace.capability for trace in traces] == [
            ChildStage.MODEL, ChildStage.PARSE,
            ChildStage.EMBEDDING, ChildStage.VISION,
        ]
        assert all(trace.stop_proof.proven for trace in traces)
        assert all(trace.child_instance for trace in traces)
        assert all(b'"fake":"' + trace.capability.value.encode() in trace.payload
                   for trace in traces)
        # Explicit capability fakes create no provider call or send fact.
        assert call_rows(context) == []
        assert fact_rows(context) == []
    finally:
        assert supervisor.close() is True


def test_real_rejected_target_and_download_credential_never_dispatch(
    call_persistence, tmp_path,
):
    context = call_persistence
    current = context.initialize_context(context_id="context-reject")
    dispatch, supervisor = assemblies(context, tmp_path)
    try:
        from rag_app.modules.execution.egress import (
            EgressError, EgressFailure,
        )

        download_profile = EgressProfile(
            EgressPurpose.DOWNLOAD,
            frozenset({HostPort("download.example.com")}),
        )
        download = EgressTarget(
            download_profile, "download.example.com", 443, "/file?sig=" + SECRET,
        )
        with pytest.raises(EgressError) as caught:
            build_egress_dispatch(
                download,
                type("R", (), {"resolve": lambda self, h, p: (ADDRESS,)})(),
                EgressRequest(
                    method="GET", api_authorization="Bearer " + SECRET,
                ),
                send_stop_by_monotonic=time.monotonic() + 60,
            )
        assert caught.value.failure is EgressFailure.AUTHORIZATION_NOT_ALLOWED
        assert call_rows(context) == []
    finally:
        assert supervisor.close() is True


def test_real_no_pg_transaction_during_child_wait(
    call_persistence, tmp_path,
):
    context = call_persistence
    current = context.initialize_context(context_id="context-wait")
    inner = LinuxChildSupervisor(state_root=tmp_path / "state")
    entered = threading.Event()
    release = threading.Event()

    class BlockingReceive(PrepareFails):
        def prepare(self, *args, **kwargs):
            return self.inner.prepare(*args, **kwargs)

        def receive(self, identity, **kwargs):
            entered.set()
            assert release.wait(timeout=10)
            return self.inner.receive(identity, **kwargs)

    dispatch = CallDispatch(
        context.lifecycle, lambda: context.uow, BlockingReceive(inner),
        clock=now,
    )
    outcome = {}

    def run():
        outcome["value"] = execute(dispatch, current)

    worker = threading.Thread(target=run)
    worker.start()
    try:
        assert entered.wait(timeout=15)
        with context.engine.connect() as connection:
            idle = connection.execute(text(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE datname = current_database() "
                "AND usename = current_user AND pid <> pg_backend_pid() "
                "AND state = 'idle in transaction'"
            )).scalar_one()
        assert idle == 0
        release.set()
        worker.join(timeout=30)
        assert not worker.is_alive()
        assert outcome["value"].send_state is SendState.RESPONSE_RECEIVED
    finally:
        release.set()
        worker.join(timeout=10)
        assert inner.close() is True
