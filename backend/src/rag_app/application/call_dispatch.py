"""One supervised external call assembled from A persistence and B egress.

The controller resolves and validates the entire egress plan before entering
this use case.  A's persistent grant is the only send authority; this module
maps it to one local SendGrant, gives it to one child instance at most once,
and keeps every TERM/KILL wait outside a database transaction.
"""

from __future__ import annotations

import json
import math
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rag_app.application.uow import UnitOfWork
from rag_app.contracts.errors import GuardError, SafeError
from rag_app.modules.execution.calls import CallGrant, ExecutionFence
from rag_app.modules.execution.egress import (
    DnsResolver,
    EgressError,
    EgressErrorCode,
    EgressFailure,
    EgressPlan,
    EgressRequest,
    EgressTarget,
    resolve_egress_plan,
)
from rag_app.modules.execution.supervision import (
    ChildFailure,
    ChildIdentity,
    ChildLimits,
    ChildResult,
    ChildSlot,
    ChildStage,
    ChildSupervisionError,
    ChildSupervisor,
    SendGrant,
    SendState,
    StageCommand,
    StopProof,
    StopReason,
)

if TYPE_CHECKING:
    from rag_app.application.call_lifecycle import CallLifecycle
    from rag_app.modules.ledger.facts import LateFactOutcome, ResultFact


_MAX_PROVIDER_REF = 256
_FAKE_STAGES = frozenset({
    ChildStage.MODEL,
    ChildStage.PARSE,
    ChildStage.EMBEDDING,
    ChildStage.VISION,
})


@dataclass(frozen=True, slots=True)
class EgressDispatch:
    """An already-resolved plan and one bounded request.

    Resolution happens in :func:`build_egress_dispatch`, strictly outside every
    unit of work.  The child consumes ``plan`` without a second DNS lookup.
    """

    plan: EgressPlan
    request: EgressRequest
    send_stop_by_monotonic: float

    def __post_init__(self) -> None:
        if not isinstance(self.plan, EgressPlan) or not isinstance(
            self.request, EgressRequest,
        ):
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        if (
            self.request.api_authorization is not None
            and not self.plan.target.authorization_allowed
        ):
            raise EgressError(
                EgressErrorCode.CONFIGURATION_INVALID,
                EgressFailure.AUTHORIZATION_NOT_ALLOWED,
            )
        value = self.send_stop_by_monotonic
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or not float(value) > 0
        ):
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)


def build_egress_dispatch(
    target: EgressTarget,
    resolver: DnsResolver,
    request: EgressRequest,
    *,
    send_stop_by_monotonic: float,
) -> EgressDispatch:
    """Resolve every A/AAAA result and fix one IP outside any transaction."""

    if not isinstance(target, EgressTarget) or not isinstance(
        request, EgressRequest,
    ):
        raise EgressError(
            EgressErrorCode.CONFIGURATION_INVALID, EgressFailure.REQUEST_INVALID,
        )
    # Reject a credential that does not belong to this purpose before any DNS
    # work.  This keeps an unauthorised signed URL from becoming a dispatch at
    # all, even if a resolver would accept it.
    if (
        request.api_authorization is not None
        and not target.authorization_allowed
    ):
        raise EgressError(
            EgressErrorCode.CONFIGURATION_INVALID,
            EgressFailure.AUTHORIZATION_NOT_ALLOWED,
        )
    plan = resolve_egress_plan(target, resolver)
    return EgressDispatch(
        plan=plan,
        request=request,
        send_stop_by_monotonic=send_stop_by_monotonic,
    )


@dataclass(frozen=True, slots=True)
class DispatchOutcome:
    call_id: str
    send_state: SendState
    response_status: int | None
    payload: bytes = field(repr=False)
    failure: ChildFailure | None = None
    grant_id: str | None = None
    stop_proof: StopProof | None = None
    fact_recorded: bool = False
    late_fact: LateFactOutcome | None = None
    fact_error: str | None = None


@dataclass(frozen=True, slots=True)
class FakeStageOutcome:
    """Trace of one explicit local capability fake; it is not a provider call."""

    capability: ChildStage
    local_call_id: str
    child_instance: str | None
    response_status: int | None
    payload: bytes = field(repr=False)
    failure: ChildFailure | None = None
    stop_proof: StopProof | None = None


def _default_result_fact(result: ChildResult, received_at: datetime) -> ResultFact:
    from rag_app.modules.ledger.facts import ResultFact

    status = result.response_status
    return ResultFact(
        outcome=(
            "responded"
            if status is None or status < 400
            else "known_failure"
        ),
        provider_ref=_provider_ref(result.payload),
        usage=None,
        cost=None,
        at=received_at,
    )


def _provider_ref(payload: bytes) -> str | None:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    if not isinstance(value, dict):
        return None
    provider_ref = value.get("provider_ref")
    if (
        not isinstance(provider_ref, str)
        or not provider_ref
        or len(provider_ref) > _MAX_PROVIDER_REF
        or "://" in provider_ref
        or "?" in provider_ref
        or "#" in provider_ref
        or any(not 0x21 <= ord(character) <= 0x7E for character in provider_ref)
    ):
        return None
    return provider_ref


def _default_late_fact(
    fact: ResultFact, received_at: datetime,
) -> LateFact:
    from rag_app.modules.ledger.facts import LateFact

    return LateFact(
        provider_ref=getattr(fact, "provider_ref", None),
        usage=getattr(fact, "usage", None),
        cost=getattr(fact, "cost", None),
        source="child_supervisor",
        received_at=received_at,
    )


def _finite_code(error: BaseException) -> str:
    if isinstance(error, SafeError) or isinstance(error, GuardError):
        return error.code
    if isinstance(error, EgressError):
        return error.code.value
    if isinstance(error, ChildSupervisionError):
        return error.failure.value
    return "INTERNAL_ERROR"


def _normalize_dispatch_result(
    result: ChildResult, grant: SendGrant,
) -> ChildResult:
    """The supervisor's conservative state is the floor for the result."""

    if result.call_id != grant.call_id or result.grant_id != grant.grant_id:
        return ChildResult(
            call_id=grant.call_id,
            grant_id=grant.grant_id,
            send_state=SendState.MAY_HAVE_SENT,
            response_status=None,
            payload=b"",
            failure=ChildFailure.IDENTITY_MISMATCH,
        )
    if result.send_state is SendState.RESPONSE_RECEIVED:
        return result
    return replace(result, send_state=SendState.MAY_HAVE_SENT)


class CallDispatch:
    """Assemble A's persistent lifecycle around one supervised child call."""

    def __init__(
        self,
        lifecycle: CallLifecycle,
        uow_factory: Callable[[], UnitOfWork],
        supervisor: ChildSupervisor,
        *,
        clock: Callable[[], datetime],
        monotonic: Callable[[], float] = time.monotonic,
        result_fact: Callable[[ChildResult, datetime], ResultFact] = _default_result_fact,
        late_fact_factory: Callable[[ResultFact, datetime], LateFact] = _default_late_fact,
    ) -> None:
        self._lifecycle = lifecycle
        self._uow_factory = uow_factory
        self._supervisor = supervisor
        self._clock = clock
        self._monotonic = monotonic
        self._result_fact = result_fact
        self._late_fact_factory = late_fact_factory

    def close(self) -> bool:
        close = getattr(self._supervisor, "close", None)
        if close is None:
            return True
        try:
            return bool(close())
        except Exception:
            return False

    def execute(
        self,
        *,
        slot: ChildSlot,
        limits: ChildLimits,
        fence: ExecutionFence,
        holder_id: str,
        space_id: str,
        purpose: str,
        stage: ChildStage,
        config_fingerprint: str,
        request_hash: str,
        payload: bytes = b"",
        egress: EgressDispatch | None = None,
        prepare_timeout_s: float = 5.0,
        result_timeout_s: float = 30.0,
    ) -> DispatchOutcome:
        if not isinstance(stage, ChildStage) or stage is not ChildStage.EGRESS:
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        if not isinstance(egress, EgressDispatch):
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        if slot.attempt != fence.attempt:
            raise ChildSupervisionError(ChildFailure.IDENTITY_MISMATCH)
        # No call is prepared after a known deadline.  This check is before the
        # first UoW and is repeated after spawn/prepare and after the grant.
        if self._monotonic() >= egress.send_stop_by_monotonic:
            raise ChildSupervisionError(ChildFailure.TIMEOUT)

        # The logical business purpose and B's transport/credential purpose
        # are independent fields.  A checks this value against its persistent
        # execution context; B's plan separately enforces the API/upload/
        # download credential rules, including the Authorization guard.
        call_id = self._lifecycle.prepare(
            self._uow_factory(),
            fence=fence,
            holder_id=holder_id,
            space_id=space_id,
            purpose=purpose,
            stage=stage.value,
            config_fingerprint=config_fingerprint,
            request_hash=request_hash,
            now=self._clock(),
        )
        outcome = DispatchOutcome(
            call_id=call_id,
            send_state=SendState.NOT_SENT,
            response_status=None,
            payload=b"",
        )
        identity: ChildIdentity | None = None
        try:
            identity = self._supervisor.spawn(slot, limits)
        except ChildSupervisionError as exc:
            return self._with_failure(outcome, exc.failure)

        command = StageCommand(
            call_id=call_id, attempt=fence.attempt, stage=stage, payload=payload,
        )
        try:
            self._supervisor.prepare(
                identity, command, timeout_s=prepare_timeout_s,
            )
        except ChildSupervisionError as exc:
            proof = self._stop(identity, StopReason.CHILD_ERROR)
            return self._with_failure(outcome, exc.failure, proof)

        if self._monotonic() >= egress.send_stop_by_monotonic:
            proof = self._stop(identity, StopReason.DEADLINE)
            return self._with_failure(outcome, ChildFailure.TIMEOUT, proof)

        try:
            persistent = self._lifecycle.mark_may_have_sent(
                self._uow_factory(),
                call_id=call_id,
                fence=fence,
                boot_id=slot.boot_id,
                child_instance=identity.child_instance,
                now=self._clock(),
            )
        except BaseException:
            self._stop(identity, StopReason.CONTROLLER_STOP)
            raise
        if persistent is None:
            proof = self._stop(identity, StopReason.CONTROLLER_STOP)
            return self._with_failure(outcome, None, proof)
        if not self._grant_matches(
            persistent, call_id=call_id, fence=fence, slot=slot,
            child_instance=identity.child_instance,
        ):
            proof = self._stop(identity, StopReason.CONTROLLER_STOP)
            outcome = DispatchOutcome(
                call_id=call_id,
                send_state=SendState.MAY_HAVE_SENT,
                response_status=None,
                payload=b"",
                grant_id=getattr(persistent, "grant_id", None),
            )
            outcome = self._record_unknown(outcome, fence)
            return self._with_failure(
                outcome, ChildFailure.IDENTITY_MISMATCH, proof,
            )

        outcome = DispatchOutcome(
            call_id=call_id,
            send_state=SendState.MAY_HAVE_SENT,
            response_status=None,
            payload=b"",
            grant_id=persistent.grant_id,
        )
        if self._monotonic() >= egress.send_stop_by_monotonic:
            proof = self._stop(identity, StopReason.DEADLINE)
            outcome = self._record_unknown(outcome, fence)
            return self._with_failure(outcome, ChildFailure.TIMEOUT, proof)

        try:
            send_grant = SendGrant(
                grant_id=persistent.grant_id,
                call_id=call_id,
                attempt=persistent.attempt,
                boot_id=persistent.boot_id,
                child_instance=persistent.child_instance,
                send_stop_by_monotonic=egress.send_stop_by_monotonic,
                plan=egress.plan,
                request=egress.request,
            )
        except BaseException:
            self._stop(identity, StopReason.CONTROLLER_STOP)
            outcome = self._record_unknown(outcome, fence)
            raise

        try:
            self._supervisor.grant(identity, send_grant)
        except ChildSupervisionError as exc:
            proof = self._stop(identity, StopReason.CHILD_ERROR)
            outcome = self._record_unknown(outcome, fence)
            return self._with_failure(outcome, exc.failure, proof)
        except BaseException:
            self._stop(identity, StopReason.CONTROLLER_STOP)
            self._record_unknown(outcome, fence)
            raise

        try:
            result = self._supervisor.receive(
                identity, timeout_s=result_timeout_s,
            )
            received_at = self._clock()
        except ChildSupervisionError as exc:
            result = ChildResult(
                call_id=call_id,
                grant_id=send_grant.grant_id,
                send_state=SendState.MAY_HAVE_SENT,
                response_status=None,
                payload=b"",
                failure=exc.failure,
            )
            received_at = self._clock()
        except BaseException:
            self._stop(identity, StopReason.CONTROLLER_STOP)
            self._record_unknown(outcome, fence)
            raise

        result = _normalize_dispatch_result(result, send_grant)
        # The child must be stopped and its send capability closed before any
        # result/unknown fact is committed.
        proof = self._stop(identity, StopReason.COMPLETED)
        outcome = DispatchOutcome(
            call_id=call_id,
            send_state=result.send_state,
            response_status=result.response_status,
            payload=result.payload,
            failure=result.failure,
            grant_id=send_grant.grant_id,
            stop_proof=proof,
        )
        if result.send_state is SendState.RESPONSE_RECEIVED:
            if proof is None or not proof.proven:
                # R2: a normal result may be sealed only after the child exit,
                # IPC/FD closure and old grant destruction are proven.  Keep
                # the business terminal unknown and retain the received
                # observation as an append-only fact.
                outcome = self._record_unknown(outcome, fence)
                outcome = self._append_observation(
                    outcome, result, received_at,
                )
                return self._with_failure(
                    outcome,
                    (
                        proof.failure if proof is not None
                        and proof.failure is not None
                        else ChildFailure.STOP_UNPROVEN
                    ),
                    proof,
                )
            return self._record_result(outcome, fence, result, received_at)
        return self._record_unknown(outcome, fence)

    def execute_fake_stage(
        self,
        *,
        slot: ChildSlot,
        limits: ChildLimits,
        stage: ChildStage,
        payload: bytes = b"",
        prepare_timeout_s: float = 5.0,
        result_timeout_s: float = 30.0,
    ) -> FakeStageOutcome:
        """Run one explicit local capability fake through the real supervisor.

        This path deliberately creates no persistent provider call and no send
        grant.  It is the traceable S0 substitute for model/parse/embedding/
        vision adapters.
        """

        if stage not in _FAKE_STAGES:
            raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
        local_call_id = "local_" + uuid.uuid4().hex
        identity: ChildIdentity | None = None
        try:
            identity = self._supervisor.spawn(slot, limits)
        except ChildSupervisionError as exc:
            return FakeStageOutcome(
                capability=stage,
                local_call_id=local_call_id,
                child_instance=None,
                response_status=None,
                payload=b"",
                failure=exc.failure,
            )
        command = StageCommand(
            call_id=local_call_id, attempt=slot.attempt, stage=stage,
            payload=payload,
        )
        try:
            self._supervisor.prepare(
                identity, command, timeout_s=prepare_timeout_s,
            )
        except ChildSupervisionError as exc:
            proof = self._stop(identity, StopReason.CHILD_ERROR)
            return FakeStageOutcome(
                capability=stage,
                local_call_id=local_call_id,
                child_instance=identity.child_instance,
                response_status=None,
                payload=b"",
                failure=exc.failure,
                stop_proof=proof,
            )
        try:
            result = self._supervisor.receive(
                identity, timeout_s=result_timeout_s,
            )
        except ChildSupervisionError as exc:
            result = ChildResult(
                call_id=local_call_id,
                grant_id=None,
                send_state=SendState.NOT_SENT,
                response_status=None,
                payload=b"",
                failure=exc.failure,
            )
        proof = self._stop(identity, StopReason.COMPLETED)
        return FakeStageOutcome(
            capability=stage,
            local_call_id=local_call_id,
            child_instance=identity.child_instance,
            response_status=result.response_status,
            payload=result.payload,
            failure=result.failure,
            stop_proof=proof,
        )

    @staticmethod
    def _grant_matches(
        grant: Any, *, call_id: str, fence: ExecutionFence, slot: ChildSlot,
        child_instance: str,
    ) -> bool:
        try:
            return (
                isinstance(grant, CallGrant)
                and grant.call_id == call_id
                and grant.attempt == fence.attempt
                and grant.boot_id == slot.boot_id
                and grant.child_instance == child_instance
            )
        except (AttributeError, TypeError):
            return False

    def _stop(
        self, identity: ChildIdentity | None, reason: StopReason,
    ) -> StopProof | None:
        if identity is None:
            return None
        try:
            return self._supervisor.stop(identity, reason)
        except Exception:
            return None

    def _record_unknown(
        self, outcome: DispatchOutcome, fence: ExecutionFence,
    ) -> DispatchOutcome:
        try:
            self._lifecycle.record_unknown(
                self._uow_factory(),
                call_id=outcome.call_id,
                fence=fence,
                now=self._clock(),
            )
        except (SafeError, GuardError) as exc:
            return self._fact_failure(outcome, _finite_code(exc))
        return self._with_fact_recorded(outcome)

    def _record_result(
        self,
        outcome: DispatchOutcome,
        fence: ExecutionFence,
        result: ChildResult,
        received_at: datetime,
    ) -> DispatchOutcome:
        fact = self._result_fact(result, received_at)
        try:
            self._lifecycle.record_result(
                self._uow_factory(),
                call_id=outcome.call_id,
                fence=fence,
                result=fact,
            )
        except (SafeError, GuardError) as exc:
            # The business terminal could not be committed under current
            # authority.  Close the call conservatively as unknown first;
            # the observation remains append-only and never revives business.
            try:
                self._lifecycle.record_unknown(
                    self._uow_factory(),
                    call_id=outcome.call_id,
                    fence=fence,
                    now=self._clock(),
                )
            except (SafeError, GuardError):
                pass
            try:
                late = self._late_fact_factory(fact, received_at)
            except (TypeError, ValueError):
                return self._fact_failure(
                    outcome, "LATE_FACT_UNAVAILABLE",
                )
            try:
                late_outcome = self._lifecycle.record_late_fact(
                    self._uow_factory(), call_id=outcome.call_id, fact=late,
                )
            except (SafeError, GuardError) as late_error:
                return self._fact_failure(
                    outcome, _finite_code(late_error),
                )
            return DispatchOutcome(
                call_id=outcome.call_id,
                send_state=outcome.send_state,
                response_status=outcome.response_status,
                payload=outcome.payload,
                failure=outcome.failure,
                grant_id=outcome.grant_id,
                stop_proof=outcome.stop_proof,
                fact_recorded=False,
                late_fact=late_outcome,
                fact_error=None,
            )
        return self._with_fact_recorded(outcome)

    def _append_observation(
        self,
        outcome: DispatchOutcome,
        result: ChildResult,
        received_at: datetime,
    ) -> DispatchOutcome:
        """Append a received observation through the call-only late path."""

        try:
            fact = self._result_fact(result, received_at)
            late = self._late_fact_factory(fact, received_at)
        except (TypeError, ValueError):
            return self._fact_failure(outcome, "LATE_FACT_UNAVAILABLE")
        try:
            late_outcome = self._lifecycle.record_late_fact(
                self._uow_factory(), call_id=outcome.call_id, fact=late,
            )
        except (SafeError, GuardError) as exc:
            return self._fact_failure(outcome, _finite_code(exc))
        return DispatchOutcome(
            call_id=outcome.call_id,
            send_state=outcome.send_state,
            response_status=outcome.response_status,
            payload=outcome.payload,
            failure=outcome.failure,
            grant_id=outcome.grant_id,
            stop_proof=outcome.stop_proof,
            fact_recorded=outcome.fact_recorded,
            late_fact=late_outcome,
            fact_error=None,
        )

    @staticmethod
    def _with_fact_recorded(outcome: DispatchOutcome) -> DispatchOutcome:
        return DispatchOutcome(
            call_id=outcome.call_id,
            send_state=outcome.send_state,
            response_status=outcome.response_status,
            payload=outcome.payload,
            failure=outcome.failure,
            grant_id=outcome.grant_id,
            stop_proof=outcome.stop_proof,
            fact_recorded=True,
            late_fact=outcome.late_fact,
            fact_error=None,
        )

    @staticmethod
    def _fact_failure(
        outcome: DispatchOutcome, code: str,
    ) -> DispatchOutcome:
        return DispatchOutcome(
            call_id=outcome.call_id,
            send_state=outcome.send_state,
            response_status=outcome.response_status,
            payload=outcome.payload,
            failure=outcome.failure,
            grant_id=outcome.grant_id,
            stop_proof=outcome.stop_proof,
            fact_recorded=False,
            late_fact=outcome.late_fact,
            fact_error=code,
        )

    @staticmethod
    def _with_failure(
        outcome: DispatchOutcome,
        failure: ChildFailure | None,
        proof: StopProof | None = None,
    ) -> DispatchOutcome:
        return DispatchOutcome(
            call_id=outcome.call_id,
            send_state=outcome.send_state,
            response_status=outcome.response_status,
            payload=outcome.payload,
            failure=failure if failure is not None else outcome.failure,
            grant_id=outcome.grant_id,
            stop_proof=proof if proof is not None else outcome.stop_proof,
            fact_recorded=outcome.fact_recorded,
            late_fact=outcome.late_fact,
            fact_error=outcome.fact_error,
        )


def build_linux_call_dispatch(
    lifecycle: CallLifecycle,
    uow_factory: Callable[[], UnitOfWork],
    *,
    state_root: str | Path,
    clock: Callable[[], datetime],
    monotonic: Callable[[], float] = time.monotonic,
    child_executable: str | None = None,
    result_fact: Callable[[ChildResult, datetime], ResultFact] = _default_result_fact,
    late_fact_factory: Callable[[ResultFact, datetime], LateFact] = _default_late_fact,
) -> CallDispatch:
    """Assemble the real Linux supervisor with an explicit absolute state root."""

    root = Path(state_root)
    if not root.is_absolute():
        raise ChildSupervisionError(ChildFailure.INVALID_ARGUMENT)
    # Import lazily: the Linux adapter uses fcntl and must not be imported by
    # platform-neutral application tests or by a Windows developer shell.
    from rag_app.adapters.child_supervisor import LinuxChildSupervisor

    supervisor = LinuxChildSupervisor(
        state_root=root, child_executable=child_executable,
    )
    return CallDispatch(
        lifecycle, uow_factory, supervisor,
        clock=clock, monotonic=monotonic,
        result_fact=result_fact, late_fact_factory=late_fact_factory,
    )
