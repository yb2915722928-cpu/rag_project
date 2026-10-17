"""Short-transaction call lifecycle; frameworks, OS and network stay outside."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from rag_app.application.uow import UnitOfWork
from rag_app.contracts.errors import GuardError
from rag_app.modules.execution.calls import (
    CallGrant, CallStoreFactory, Epoch, EpochControl, ExecutionContext,
    ExecutionFence, activity_label, bounded_identifier, claim_digest,
    evidence_fingerprint, fence_matches, stable_id,
)
from rag_app.modules.ledger.facts import (
    LateFact, LateFactOutcome, ResultFact, fact_digest,
)


def _new_call_id() -> str:
    import uuid

    return "call_" + uuid.uuid4().hex


def _new_grant_id() -> str:
    import uuid

    return "grant_" + uuid.uuid4().hex


def _now(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("now must be an aware datetime")
    return value


def _call_inputs(
    *, holder_id: str, space_id: str, purpose: str, stage: str,
    config_fingerprint: str, request_hash: str,
) -> None:
    try:
        stable_id(holder_id, name="holder_id")
        stable_id(space_id, name="space_id")
        activity_label(purpose, name="purpose")
        activity_label(stage, name="stage")
        evidence_fingerprint(config_fingerprint, name="config_fingerprint")
        evidence_fingerprint(request_hash, name="request_hash")
    except ValueError:
        raise GuardError("CALL_INPUT_INVALID") from None


def _run_guarded(uow: UnitOfWork, stores: Any, work: Any) -> Any:
    """Run work in one short UoW; UnitOfWork retains finite guard codes."""

    with uow.transaction() as session:
        return work(stores(session))


class CallLifecycle:
    """Use cases for prepared -> may_have_sent -> terminal and late facts."""

    def __init__(
        self, control: EpochControl, stores: CallStoreFactory,
    ) -> None:
        self._control = control
        self._stores = stores

    def _fresh_epoch(self) -> Epoch:
        # The control file/OS read is deliberately outside the PG transaction.
        return self._control.current()

    def prepare(
        self, uow: UnitOfWork, *, fence: ExecutionFence, holder_id: str,
        space_id: str, purpose: str, stage: str, config_fingerprint: str,
        request_hash: str, now: datetime,
    ) -> str:
        _now(now)
        _call_inputs(
            holder_id=holder_id, space_id=space_id, purpose=purpose,
            stage=stage, config_fingerprint=config_fingerprint,
            request_hash=request_hash,
        )
        epoch = self._fresh_epoch()
        if fence.epoch != epoch.epoch:
            raise GuardError("CALL_FENCE_STALE")
        call_id = _new_call_id()

        def work(store: Any) -> None:
            store.verify_epoch_mirror(self._control, epoch)
            # Current authority comes from the locked context row, never from
            # the caller-supplied fence or an older call snapshot.
            context = _lock_context(store, fence.owner_context_id)
            _require_authority(
                context, fence=fence, epoch=epoch, now=store.current_time(),
            )
            _require_scope(
                context, holder_id=holder_id, space_id=space_id,
                purpose=purpose, config_fingerprint=config_fingerprint,
            )
            # Store the persisted authority, never a caller-extended lease.
            authoritative = ExecutionFence(
                epoch=context["epoch"], owner_context_id=context["context_id"],
                attempt=context["attempt"], claim_token=fence.claim_token,
                lease_until=context["lease_until"],
                hard_deadline=context["hard_deadline"],
            )
            store.insert_call(
                call_id=call_id, fence=authoritative, holder_id=holder_id,
                space_id=space_id, purpose=purpose, stage=stage,
                config_fingerprint=config_fingerprint,
                request_hash=request_hash, now=now,
            )

        _run_guarded(uow, self._stores, work)
        return call_id

    def mark_may_have_sent(
        self, uow: UnitOfWork, *, call_id: str, fence: ExecutionFence,
        boot_id: str, child_instance: str, now: datetime,
    ) -> CallGrant | None:
        _now(now)
        try:
            bounded_identifier(boot_id, name="boot_id")
            bounded_identifier(child_instance, name="child_instance")
        except ValueError:
            raise GuardError("CALL_INPUT_INVALID") from None
        epoch = self._fresh_epoch()
        if fence.epoch != epoch.epoch:
            return None

        def work(store: Any) -> CallGrant | None:
            store.verify_epoch_mirror(self._control, epoch)
            context = store.lock_context(fence.owner_context_id)
            if context is None:
                return None
            record = store.lock_call(call_id)
            if record is None:
                raise GuardError("CALL_NOT_FOUND")
            # Locks may have waited past the lease; the caller's event time can
            # never authorize a grant.  Recheck with the DB clock after both
            # the context and call rows are held.
            if not _authority_ok(
                context, fence=fence, epoch=epoch, now=store.current_time(),
            ):
                return None
            if (
                not _fence_matches(record, fence)
                or record["holder_id"] != context["holder_id"]
                or record["space_id"] != context["space_id"]
                or record["purpose"] != context["purpose"]
                or record["config_fingerprint"] != context["config_fingerprint"]
                or record["state"] != "prepared"
            ):
                return None
            grant_id = _new_grant_id()
            if not store.mark_may_have_sent(
                record, grant_id=grant_id, boot_id=boot_id,
                child_instance=child_instance, now=now,
            ):
                return None
            return CallGrant(
                call_id=record["call_id"], attempt=record["attempt"],
                boot_id=boot_id, child_instance=child_instance,
                grant_id=grant_id,
            )

        return _run_guarded(uow, self._stores, work)

    def record_result(
        self, uow: UnitOfWork, *, call_id: str, fence: ExecutionFence,
        result: ResultFact,
    ) -> None:
        epoch = self._fresh_epoch()
        if fence.epoch != epoch.epoch:
            raise GuardError("CALL_FENCE_STALE")

        def work(store: Any) -> None:
            store.verify_epoch_mirror(self._control, epoch)
            context = _lock_context(store, fence.owner_context_id)
            record = store.lock_call(call_id)
            if record is None:
                raise GuardError("CALL_NOT_FOUND")
            # Both the context and call rows are held now; check current
            # authority with the DB clock rather than a pre-lock time.
            _require_authority(
                context, fence=fence, epoch=epoch, now=store.current_time(),
            )
            _apply_result(store, record, fence=fence, result=result)

        _run_guarded(uow, self._stores, work)

    def record_unknown(
        self, uow: UnitOfWork, *, call_id: str, fence: ExecutionFence,
        now: datetime,
    ) -> None:
        _now(now)
        def work(store: Any) -> None:
            # Recovery-safe terminal observation: lock only the addressed
            # call.  It can neither grant a send nor touch business state, so
            # an expired lease or a rotated epoch must not strand a call in
            # may_have_sent; the immutable call fence still proves ownership.
            record = store.lock_call(call_id)
            if record is None:
                raise GuardError("CALL_NOT_FOUND")
            _apply_unknown(store, record, fence=fence, now=now)

        _run_guarded(uow, self._stores, work)

    def record_late_fact(
        self, uow: UnitOfWork, *, call_id: str, fact: LateFact,
    ) -> LateFactOutcome:
        # Late facts deliberately skip epoch, fence, gate, pool and business
        # locks; they lock only the addressed call row.
        def work(store: Any) -> str:
            record = store.lock_call(call_id)
            if record is None:
                raise GuardError("CALL_NOT_FOUND")
            return _apply_late(store, record, fact)

        disposition = _run_guarded(uow, self._stores, work)
        return LateFactOutcome(disposition=disposition)

    def initialize_context(
        self, uow: UnitOfWork, *, context_id: str, holder_id: str,
        space_id: str, purpose: str, config_fingerprint: str, attempt: int,
        claim_token: str, lease_until: datetime, hard_deadline: datetime,
        now: datetime,
    ) -> ExecutionContext:
        """Controlled seam for accept/test fakes; no production auto-creation."""

        _now(now)
        epoch = self._fresh_epoch()
        value = ExecutionContext(
            context_id=context_id, epoch=epoch.epoch, holder_id=holder_id,
            space_id=space_id, purpose=purpose,
            config_fingerprint=config_fingerprint, attempt=attempt,
            claim_token=claim_token, lease_until=lease_until,
            hard_deadline=hard_deadline, state="active",
        )
        if now >= value.lease_until or now >= value.hard_deadline:
            raise GuardError("CALL_FENCE_STALE")

        def work(store: Any) -> None:
            store.verify_epoch_mirror(self._control, epoch)
            store.insert_context(
                context_id=value.context_id, epoch=value.epoch,
                holder_id=value.holder_id, space_id=value.space_id,
                purpose=value.purpose,
                config_fingerprint=value.config_fingerprint,
                attempt=value.attempt,
                claim_token_digest=claim_digest(value.claim_token),
                lease_until=value.lease_until,
                hard_deadline=value.hard_deadline,
            )

        _run_guarded(uow, self._stores, work)
        return value

    def advance_attempt(
        self, uow: UnitOfWork, *, context_id: str, attempt: int,
        claim_token: str, lease_until: datetime, hard_deadline: datetime,
        now: datetime,
    ) -> ExecutionContext:
        """Replace attempt/token; the prior token loses all current authority."""

        _now(now)
        epoch = self._fresh_epoch()
        if type(attempt) is not int or attempt < 2:
            raise GuardError("CALL_FENCE_STALE")
        if lease_until > hard_deadline or now >= lease_until or now >= hard_deadline:
            raise GuardError("CALL_FENCE_STALE")
        digest = claim_digest(claim_token)

        def work(store: Any) -> ExecutionContext:
            store.verify_epoch_mirror(self._control, epoch)
            context = _lock_context(store, context_id)
            if context["state"] != "active" or context["epoch"] != epoch.epoch:
                raise GuardError("CALL_FENCE_STALE")
            if context["attempt"] != attempt - 1:
                raise GuardError("CALL_FENCE_STALE")
            if not store.replace_attempt(
                context_id=context_id, attempt=attempt,
                claim_token_digest=digest, lease_until=lease_until,
                hard_deadline=hard_deadline,
            ):
                raise GuardError("CALL_FENCE_STALE")
            return ExecutionContext(
                context_id=context_id, epoch=context["epoch"],
                holder_id=context["holder_id"], space_id=context["space_id"],
                purpose=context["purpose"],
                config_fingerprint=context["config_fingerprint"],
                attempt=attempt, claim_token=claim_token,
                lease_until=lease_until, hard_deadline=hard_deadline,
                state="active",
            )

        return _run_guarded(uow, self._stores, work)

    def terminate_context(
        self, uow: UnitOfWork, *, context_id: str,
        state: str = "terminal",
    ) -> None:
        """End current authority; existing call facts stay immutable."""

        if state not in {"terminal", "isolated"}:
            raise GuardError("CALL_STATE_CONFLICT")
        epoch = self._fresh_epoch()

        def work(store: Any) -> None:
            store.verify_epoch_mirror(self._control, epoch)
            context = _lock_context(store, context_id)
            if context["state"] != "active":
                raise GuardError("CALL_FENCE_STALE")
            if not store.terminate_context(context_id=context_id, state=state):
                raise GuardError("CALL_FENCE_STALE")

        _run_guarded(uow, self._stores, work)


def _lock_context(store: Any, context_id: str) -> dict[str, Any]:
    context = store.lock_context(context_id)
    if context is None:
        raise GuardError("CALL_CONTEXT_MISSING")
    return context


def _authority_ok(
    context: dict[str, Any], *, fence: ExecutionFence, epoch: Epoch,
    now: datetime,
) -> bool:
    return (
        context["state"] == "active"
        and context["epoch"] == epoch.epoch
        and context["epoch"] == fence.epoch
        and context["context_id"] == fence.owner_context_id
        and context["attempt"] == fence.attempt
        and context["claim_token_digest"] == claim_digest(fence.claim_token)
        and now < context["lease_until"]
        and now < context["hard_deadline"]
    )


def _require_authority(
    context: dict[str, Any], *, fence: ExecutionFence, epoch: Epoch,
    now: datetime,
) -> None:
    if not _authority_ok(context, fence=fence, epoch=epoch, now=now):
        raise GuardError("CALL_FENCE_STALE")


def _require_scope(
    context: dict[str, Any], *, holder_id: str, space_id: str, purpose: str,
    config_fingerprint: str,
) -> None:
    if (
        context["holder_id"] != holder_id
        or context["space_id"] != space_id
        or context["purpose"] != purpose
        or context["config_fingerprint"] != config_fingerprint
    ):
        raise GuardError("CALL_FENCE_STALE")


def _fence_matches(record: dict[str, Any], fence: ExecutionFence) -> bool:
    return fence_matches(
        epoch=record["epoch"],
        owner_context_id=record["owner_context_id"],
        attempt=record["attempt"],
        claim_token_digest=record["claim_token_digest"],
        fence=fence,
    )


def _same_usage(record: dict[str, Any], usage: Any) -> bool:
    return (
        record["usage_status"] == ("unknown" if usage is None else usage.status)
        and record["prompt_tokens"] == (
            None if usage is None else usage.prompt_tokens
        )
        and record["completion_tokens"] == (
            None if usage is None else usage.completion_tokens
        )
        and record["total_tokens"] == (
            None if usage is None else usage.total_tokens
        )
    )


def _same_cost(record: dict[str, Any], cost: Any) -> bool:
    return (
        record["cost_kind"] == (None if cost is None else cost.kind)
        and record["cost_amount"] == (None if cost is None else cost.amount)
        and record["cost_currency"] == (None if cost is None else cost.currency)
        and record["cost_basis"] == (None if cost is None else cost.basis)
    )


def _apply_result(
    store: Any, record: dict[str, Any], *, fence: ExecutionFence,
    result: ResultFact,
) -> None:
    if not _fence_matches(record, fence):
        raise GuardError("CALL_FENCE_STALE")
    if record["state"] in {"responded", "known_failure"}:
        if (
            record["state"] == result.outcome
            and record["provider_ref"] == result.provider_ref
            and _same_usage(record, result.usage)
            and _same_cost(record, result.cost)
        ):
            return
        raise GuardError("CALL_STATE_CONFLICT")
    if record["state"] == "prepared":
        raise GuardError("CALL_NOT_SENT")
    if record["state"] != "may_have_sent":
        raise GuardError("CALL_STATE_CONFLICT")
    store.record_terminal(
        record, outcome=result.outcome, at=result.at,
        provider_ref=result.provider_ref, usage=result.usage, cost=result.cost,
    )
    _append_fact(
        store, record["call_id"], result.provider_ref, result.usage,
        result.cost, source="result", received_at=result.at,
        disposition="appended",
    )


def _apply_unknown(
    store: Any, record: dict[str, Any], *, fence: ExecutionFence,
    now: datetime,
) -> None:
    if not _fence_matches(record, fence):
        raise GuardError("CALL_FENCE_STALE")
    if record["state"] == "unknown":
        return
    if record["state"] == "prepared":
        raise GuardError("CALL_NOT_SENT")
    if record["state"] != "may_have_sent":
        raise GuardError("CALL_STATE_CONFLICT")
    store.record_terminal(
        record, outcome="unknown", at=now, provider_ref=None,
        usage=None, cost=None,
    )


def _append_fact(
    store: Any, call_id: str, provider_ref: Any, usage: Any, cost: Any, *,
    source: str, received_at: datetime, disposition: str,
) -> bool:
    return store.insert_fact(
        call_id=call_id,
        digest=fact_digest(provider_ref=provider_ref, usage=usage, cost=cost),
        provider_ref=provider_ref, usage=usage, cost=cost, source=source,
        received_at=received_at, disposition=disposition,
    )


def _apply_late(store: Any, record: dict[str, Any], fact: LateFact) -> str:
    digest = fact_digest(
        provider_ref=fact.provider_ref, usage=fact.usage, cost=fact.cost,
    )
    facts = store.list_facts(record["call_id"])
    if any(item["fact_digest"] == digest for item in facts):
        return "duplicate"
    known_refs = {
        ref for ref in [record["provider_ref"]]
        + [item["provider_ref"] for item in facts] if ref is not None
    }
    conflict = record["state"] == "prepared"
    if fact.provider_ref is not None and known_refs and (
        fact.provider_ref not in known_refs
    ):
        conflict = True
    if fact.usage is not None and fact.usage.status == "reported":
        if record["usage_status"] == "reported" and not _same_usage(
            record, fact.usage,
        ):
            conflict = True
        for item in facts:
            if (
                item["usage_status"] == "reported"
                and item["provider_ref"] in {None, fact.provider_ref}
                and not _same_usage(item, fact.usage)
            ):
                conflict = True
    if fact.cost is not None:
        if (
            record["cost_kind"] == fact.cost.kind
            and not _same_cost(record, fact.cost)
        ):
            conflict = True
        for item in facts:
            if (
                item["cost_kind"] == fact.cost.kind
                and item["provider_ref"] in {None, fact.provider_ref}
                and not _same_cost(item, fact.cost)
            ):
                conflict = True
    disposition = "conflict" if conflict else "appended"
    inserted = _append_fact(
        store, record["call_id"], fact.provider_ref, fact.usage, fact.cost,
        source=fact.source, received_at=fact.received_at,
        disposition=disposition,
    )
    if not inserted:
        return "duplicate"
    if conflict:
        store.require_reconciliation(record["call_id"])
    return disposition
