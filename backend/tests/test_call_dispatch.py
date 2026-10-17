"""Call dispatch integration: one grant, conservative unknown and fact paths.

All supervisor, DNS and capability effects in this module are explicit fakes.
The real Linux child and PostgreSQL matrices live in
``test_call_dispatch_postgres.py``.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from rag_app.application.call_dispatch import (
    CallDispatch,
    DispatchOutcome,
    EgressDispatch,
    build_egress_dispatch,
)
from rag_app.contracts.errors import GuardError
from rag_app.modules.execution.calls import CallGrant, ExecutionFence
from rag_app.modules.execution.egress import (
    AddressFamily,
    EgressError,
    EgressErrorCode,
    EgressFailure,
    EgressPlan,
    EgressProfile,
    EgressPurpose,
    EgressRequest,
    EgressTarget,
    HostPort,
    ResolvedAddress,
)
from rag_app.modules.execution.supervision import (
    ChildFailure,
    ChildIdentity,
    ChildLimits,
    ChildResult,
    ChildSlot,
    ChildStage,
    ChildSupervisionError,
    SendState,
    StopProof,
)
from rag_app.modules.ledger.facts import (
    CostFact, LateFact, LateFactOutcome, ResultFact, UsageFact,
)


BASE = datetime(2026, 10, 18, 8, 0, tzinfo=timezone.utc)
SECRET = "SECRET-dispatch-9a3f2c" + "-payload"
ADDRESS = ResolvedAddress(AddressFamily.IPV4, "93.184.216.34")


def profile(purpose=EgressPurpose.API) -> EgressProfile:
    return EgressProfile(
        purpose, frozenset({HostPort("api.example.com")}),
    )


def target(purpose=EgressPurpose.API) -> EgressTarget:
    return EgressTarget(
        profile(purpose), "api.example.com", 443,
        "/v1/run?signature=" + SECRET,
    )


def request() -> EgressRequest:
    return EgressRequest(
        method="POST",
        headers=(("Content-Type", "application/json"),),
        body=b'{"value":"' + SECRET.encode() + b'"}',
        api_authorization="Bearer " + SECRET,
    )


def plan(purpose=EgressPurpose.API) -> EgressPlan:
    return EgressPlan(
        target=target(purpose), addresses=(ADDRESS,), connect_address=ADDRESS,
    )


def dispatch_input(
    *, stop_after: float = 60.0, purpose=EgressPurpose.API,
) -> EgressDispatch:
    return EgressDispatch(
        plan=plan(purpose), request=request(),
        send_stop_by_monotonic=10.0 + stop_after,
    )


class ResolverSpy:
    def __init__(self, value=ADDRESS):
        self.value = value
        self.calls: list[tuple[str, int]] = []

    def resolve(self, host, port):
        self.calls.append((host, port))
        return (self.value,)


class LifecycleSpy:
    def __init__(self, events: list[str]):
        self.events = events
        self.prepared: list[dict] = []
        self.marked: list[dict] = []
        self.results: list[ResultFact] = []
        self.unknowns: list[dict] = []
        self.late: list[LateFact] = []
        self.prepare_error: Exception | None = None
        self.mark_error: Exception | None = None
        self.mark_none = False
        self.result_error: Exception | None = None
        self.unknown_error: Exception | None = None
        self.late_error: Exception | None = None
        self.grant_counter = 0

    def prepare(self, uow, **values):
        self.events.append("prepare")
        if self.prepare_error is not None:
            raise self.prepare_error
        self.prepared.append(values)
        return "call_" + "a" * 31 + str(len(self.prepared))

    def mark_may_have_sent(self, uow, **values):
        self.events.append("mark")
        if self.mark_error is not None:
            raise self.mark_error
        if self.mark_none:
            return None
        self.marked.append(values)
        self.grant_counter += 1
        self.last_grant = CallGrant(
            call_id=values["call_id"], attempt=values["fence"].attempt,
            boot_id=values["boot_id"],
            child_instance=values["child_instance"],
            grant_id="grant_" + "b" * 31 + str(self.grant_counter),
        )
        return self.last_grant

    def record_result(self, uow, **values):
        self.events.append("record_result")
        if self.result_error is not None:
            raise self.result_error
        self.results.append(values["result"])

    def record_unknown(self, uow, **values):
        self.events.append("record_unknown")
        if self.unknown_error is not None:
            raise self.unknown_error
        self.unknowns.append(values)

    def record_late_fact(self, uow, **values):
        self.events.append("record_late_fact")
        if self.late_error is not None:
            raise self.late_error
        self.late.append(values["fact"])
        return LateFactOutcome(disposition="appended")


def slot() -> ChildSlot:
    return ChildSlot(
        deployment_id="deployment-1", boot_id="boot-1",
        slot_id="slot-1", attempt=1,
    )


def fence(**overrides) -> ExecutionFence:
    values = {
        "epoch": "e" * 43,
        "owner_context_id": "context-1",
        "attempt": 1,
        "claim_token": "claim-token-abcdefghijklmnop",
        "lease_until": BASE + timedelta(seconds=60),
        "hard_deadline": BASE + timedelta(seconds=120),
    }
    values.update(overrides)
    return ExecutionFence(**values)


def identity(child="child-1") -> ChildIdentity:
    return ChildIdentity(
        slot=slot(), child_instance=child, pid=4242,
        process_group=4242, start_ticks=99,
    )


def proven(value: ChildIdentity, failure=None) -> StopProof:
    return StopProof(
        identity=value, exited=True, exit_code=0, process_group_empty=True,
        no_descendants=True, ipc_closed=True, send_fds_closed=True,
        grant_destroyed=True, proven_monotonic=50.0, failure=failure,
    )


class SupervisorSpy:
    def __init__(self, events: list[str]):
        self.events = events
        self.spawn_error: Exception | None = None
        self.prepare_error: Exception | None = None
        self.grant_error: Exception | None = None
        self.receive_error: Exception | None = None
        self.result: ChildResult | None = None
        self.stop_override: StopProof | None = None
        self.grants = []
        self.commands = []
        self.stops = []
        self.ident = identity()
        self.closed = 0

    def spawn(self, slot_value, limits):
        self.events.append("spawn")
        if self.spawn_error is not None:
            raise self.spawn_error
        return self.ident

    def prepare(self, value, command, *, timeout_s=5.0):
        self.events.append("child_prepare")
        if self.prepare_error is not None:
            raise self.prepare_error
        self.commands.append(command)

    def grant(self, value, grant):
        self.events.append("grant")
        if self.grant_error is not None:
            raise self.grant_error
        self.grants.append(grant)

    def receive(self, value, *, timeout_s=30.0):
        self.events.append("receive")
        if self.receive_error is not None:
            raise self.receive_error
        if self.result is not None:
            return self.result
        grant = self.grants[-1]
        return ChildResult(
            call_id=grant.call_id, grant_id=grant.grant_id,
            send_state=SendState.RESPONSE_RECEIVED, response_status=200,
            payload=b'{"provider_ref":"provider-1"}',
        )

    def stop(self, value, reason):
        self.events.append("stop")
        self.stops.append(reason)
        if self.stop_override is not None:
            return self.stop_override
        return proven(value)

    def inspect(self, value):
        return proven(value)

    def close(self):
        self.closed += 1
        return True


class Clock:
    def __init__(self, moments=None):
        self.moments = list(moments or ())
        self.calls = 0
        self.value = 0.0

    def __call__(self):
        self.calls += 1
        if self.moments:
            self.value = self.moments.pop(0)
        return self.value


def assemble(events, *, moments=None):
    lifecycle = LifecycleSpy(events)
    supervisor = SupervisorSpy(events)
    clock = Clock(moments)
    value = CallDispatch(
        lifecycle, lambda: object(), supervisor,
        clock=lambda: BASE, monotonic=clock,
    )
    return value, lifecycle, supervisor, clock


def execute(value, **overrides):
    arguments = {
        "slot": slot(), "limits": ChildLimits(),
        "fence": fence(), "holder_id": "holder-1", "space_id": "space-1",
        "purpose": "api", "stage": ChildStage.EGRESS,
        "config_fingerprint": "config:v1", "request_hash": "request-1",
        "egress": dispatch_input(),
    }
    arguments.update(overrides)
    return value.execute(**arguments)


def test_success_uses_one_grant_and_commits_after_proven_stop():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    outcome = execute(value)
    assert outcome.send_state is SendState.RESPONSE_RECEIVED
    assert outcome.response_status == 200
    assert outcome.fact_recorded is True
    assert outcome.stop_proof is not None and outcome.stop_proof.proven
    assert len(supervisor.grants) == 1
    grant = supervisor.grants[0]
    assert grant.call_id == outcome.call_id
    assert grant.grant_id == outcome.grant_id
    assert grant.boot_id == "boot-1"
    assert grant.child_instance == "child-1"
    assert lifecycle.results[0].provider_ref == "provider-1"
    assert events.index("stop") < events.index("record_result")
    assert events.count("grant") == 1
    assert supervisor.closed == 0


def test_prepare_rejection_dispatches_no_child():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    lifecycle.prepare_error = GuardError("CALL_FENCE_STALE")
    with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
        execute(value)
    assert "spawn" not in events
    assert supervisor.grants == []


def test_spawn_failure_leaves_the_call_prepared_and_not_sent():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    supervisor.spawn_error = ChildSupervisionError(ChildFailure.CHILD_EXITED)
    outcome = execute(value)
    assert outcome.send_state is SendState.NOT_SENT
    assert outcome.failure is ChildFailure.CHILD_EXITED
    assert lifecycle.marked == []
    assert lifecycle.unknowns == []
    assert "grant" not in events


def test_child_prepare_failure_stops_and_never_marks():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    supervisor.prepare_error = ChildSupervisionError(ChildFailure.IPC_PROTOCOL)
    outcome = execute(value)
    assert outcome.failure is ChildFailure.IPC_PROTOCOL
    assert outcome.stop_proof is not None
    assert lifecycle.marked == []
    assert "mark" not in events
    assert supervisor.stops[-1].value == "child_error"


def test_deadline_after_child_prepare_never_marks():
    events: list[str] = []
    # start=0, after prepare=100 (beyond send_stop_by=70).
    value, lifecycle, supervisor, _ = assemble(events, moments=[0.0, 100.0])
    outcome = execute(value)
    assert outcome.failure is ChildFailure.TIMEOUT
    assert lifecycle.marked == []
    assert "mark" not in events
    assert supervisor.stops[-1].value == "deadline"


def test_stale_persistent_fence_yields_no_local_grant():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    lifecycle.mark_none = True
    outcome = execute(value)
    assert outcome.send_state is SendState.NOT_SENT
    assert outcome.grant_id is None
    assert supervisor.grants == []
    assert lifecycle.unknowns == []
    assert supervisor.stops[-1].value == "controller_stop"


def test_mark_failure_stops_child_and_propagates_finite_guard():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    lifecycle.mark_error = GuardError("CALL_FENCE_STALE")
    with pytest.raises(GuardError, match="CALL_FENCE_STALE"):
        execute(value)
    assert supervisor.grants == []
    assert supervisor.stops[-1].value == "controller_stop"


def test_grant_delivery_failure_records_unknown_null_fact():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    supervisor.grant_error = ChildSupervisionError(ChildFailure.IPC_IO)
    outcome = execute(value)
    assert outcome.send_state is SendState.MAY_HAVE_SENT
    assert outcome.failure is ChildFailure.IPC_IO
    assert len(lifecycle.unknowns) == 1
    assert lifecycle.results == []
    assert outcome.fact_recorded is True


def test_receive_timeout_is_conservative_unknown_and_zero_facts():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    supervisor.receive_error = ChildSupervisionError(ChildFailure.TIMEOUT)
    outcome = execute(value)
    assert outcome.send_state is SendState.MAY_HAVE_SENT
    assert outcome.failure is ChildFailure.TIMEOUT
    assert len(lifecycle.unknowns) == 1
    assert lifecycle.results == []
    assert supervisor.stops[-1].value == "completed"


def test_child_not_sent_below_grant_floor_is_normalized_to_may_have_sent():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    original_receive = supervisor.receive

    def not_sent(value_identity, **kwargs):
        result = original_receive(value_identity, **kwargs)
        return ChildResult(
            call_id=result.call_id, grant_id=None,
            send_state=SendState.NOT_SENT, response_status=None,
            payload=b"",
        )

    supervisor.receive = not_sent
    outcome = execute(value)
    assert outcome.send_state is SendState.MAY_HAVE_SENT
    assert outcome.failure is ChildFailure.IDENTITY_MISMATCH
    assert len(lifecycle.unknowns) == 1
    assert lifecycle.results == []


def test_unproven_stop_after_response_keeps_unknown_and_appends_fact():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    supervisor.stop_override = proven(
        identity(), failure=ChildFailure.STOP_UNPROVEN,
    )
    outcome = execute(value)
    assert outcome.failure is ChildFailure.STOP_UNPROVEN
    assert outcome.send_state is SendState.RESPONSE_RECEIVED
    assert len(lifecycle.results) == 0
    assert len(lifecycle.unknowns) == 1
    assert len(lifecycle.late) == 1
    assert outcome.late_fact.disposition == "appended"
    assert outcome.fact_recorded is True


def test_result_commit_failure_is_unknown_plus_late_observation():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    lifecycle.result_error = GuardError("CALL_FENCE_STALE")
    outcome = execute(value)
    assert len(lifecycle.results) == 0
    assert len(lifecycle.unknowns) == 1
    assert len(lifecycle.late) == 1
    assert outcome.late_fact.disposition == "appended"
    assert events.index("record_unknown") < events.index("record_late_fact")


def test_known_failure_status_maps_to_known_failure_fact():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    original_receive = supervisor.receive

    def failed(value_identity, **kwargs):
        result = original_receive(value_identity, **kwargs)
        return ChildResult(
            call_id=result.call_id, grant_id=result.grant_id,
            send_state=SendState.RESPONSE_RECEIVED,
            response_status=500, payload=b"{}",
        )

    supervisor.receive = failed
    outcome = execute(value)
    assert outcome.response_status == 500
    assert lifecycle.results[0].outcome == "known_failure"
    assert outcome.fact_recorded is True


def test_fake_capability_trace_uses_real_supervisor_without_a_call():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    for stage in (
        ChildStage.MODEL, ChildStage.PARSE,
        ChildStage.EMBEDDING, ChildStage.VISION,
    ):
        def reply(identity_value, **kwargs):
            command = supervisor.commands[-1]
            return ChildResult(
                call_id=command.call_id, grant_id=None,
                send_state=SendState.NOT_SENT, response_status=None,
                payload=b'{"fake":"stage"}',
            )

        supervisor.receive = reply
        outcome = value.execute_fake_stage(
            slot=slot(), limits=ChildLimits(), stage=stage,
            payload=b"bounded-input",
        )
        assert outcome.capability is stage
        assert outcome.child_instance == "child-1"
        assert outcome.payload == b'{"fake":"stage"}'
        assert outcome.stop_proof is not None
        events.clear()
    assert lifecycle.prepared == []
    assert lifecycle.marked == []
    assert supervisor.grants == []


def test_fake_stage_rejects_egress_stage():
    events: list[str] = []
    value, _, _, _ = assemble(events)
    with pytest.raises(ChildSupervisionError) as caught:
        value.execute_fake_stage(
            slot=slot(), limits=ChildLimits(), stage=ChildStage.EGRESS,
        )
    assert caught.value.failure is ChildFailure.INVALID_ARGUMENT


def test_denied_download_authorization_fails_before_dns():
    resolver = ResolverSpy()
    download = EgressRequest(
        method="GET", api_authorization="Bearer " + SECRET,
    )
    with pytest.raises(EgressError) as caught:
        build_egress_dispatch(
            target(EgressPurpose.DOWNLOAD), resolver, download,
            send_stop_by_monotonic=60.0,
        )
    assert caught.value.code is EgressErrorCode.CONFIGURATION_INVALID
    assert caught.value.failure is EgressFailure.AUTHORIZATION_NOT_ALLOWED
    assert resolver.calls == []


def test_unsafe_dns_is_rejected_before_any_call():
    resolver = ResolverSpy(
        ResolvedAddress(AddressFamily.IPV4, "127.0.0.1"),
    )
    with pytest.raises(EgressError) as caught:
        build_egress_dispatch(
            target(), resolver, request(), send_stop_by_monotonic=60.0,
        )
    assert caught.value.failure is EgressFailure.DNS_UNSAFE


def test_purpose_mismatch_is_rejected_before_any_call():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    with pytest.raises(EgressError) as caught:
        execute(value, purpose="download")
    assert caught.value.failure is EgressFailure.PROFILE_INVALID
    assert events == []
    assert lifecycle.prepared == []
    assert supervisor.grants == []


def test_egress_dispatch_hides_url_body_and_authorization_from_repr():
    value = dispatch_input()
    assert SECRET not in repr(value)
    outcome = DispatchOutcome(
        call_id="call_" + "a" * 31, send_state=SendState.RESPONSE_RECEIVED,
        response_status=200, payload=SECRET.encode(),
        grant_id="grant_" + "b" * 31,
    )
    assert SECRET not in repr(outcome)


def test_custom_result_fact_keeps_usage_and_actual_cost_distinct():
    events: list[str] = []
    value, lifecycle, supervisor, _ = assemble(events)
    fact = ResultFact(
        outcome="responded", provider_ref="provider-9",
        usage=UsageFact("reported", 3, 4, 7),
        cost=CostFact("actual", Decimal("0.50"), "USD", "invoice"),
        at=BASE,
    )
    value = CallDispatch(
        lifecycle, lambda: object(), supervisor,
        clock=lambda: BASE, monotonic=Clock(),
        result_fact=lambda result, received_at: fact,
    )
    execute(value)
    assert lifecycle.results[0] == fact
    assert lifecycle.results[0].cost.kind == "actual"
