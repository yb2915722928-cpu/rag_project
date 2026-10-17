"""Framework-free execution identity, fence and single-call grant values."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import re
from typing import Any, Protocol

from rag_app.contracts.errors import GuardError


_LABEL = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
_IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
_ROLE = re.compile(r"[a-z][a-z0-9_.-]{0,63}\Z")
_FINGERPRINT = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")
_TOKEN = re.compile(r"[\x21-\x7e]{16,512}\Z")


def _aware(value: datetime, name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be an aware datetime")


def _match(value: object, pattern: re.Pattern[str], name: str) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ValueError(f"{name} has an invalid format")
    return value


def stable_id(value: object, *, name: str = "identifier") -> str:
    return _match(value, _LABEL, name)


def bounded_identifier(value: object, *, name: str = "identifier") -> str:
    return _match(value, _IDENT, name)


def activity_label(value: object, *, name: str = "label") -> str:
    return _match(value, _ROLE, name)


def evidence_fingerprint(value: object, *, name: str = "fingerprint") -> str:
    return _match(value, _FINGERPRINT, name)


def claim_token(value: object) -> str:
    return _match(value, _TOKEN, "claim_token")


def claim_digest(token: str) -> str:
    """Store only a digest; raw claim tokens never reach persistence or logs."""

    claim_token(token)
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def fence_matches(
    *, epoch: str, owner_context_id: str, attempt: int,
    claim_token_digest: str, fence: ExecutionFence,
) -> bool:
    return (
        epoch == fence.epoch
        and owner_context_id == fence.owner_context_id
        and attempt == fence.attempt
        and claim_token_digest == claim_digest(fence.claim_token)
    )


@dataclass(frozen=True)
class Epoch:
    """Independent recovery epoch record; never derived from a restore DB."""

    deployment_id: str
    epoch: str
    cutover_at: datetime
    maintenance_version: int

    def __post_init__(self) -> None:
        stable_id(self.deployment_id, name="deployment_id")
        stable_id(self.epoch, name="epoch")
        _aware(self.cutover_at, "cutover_at")
        if type(self.maintenance_version) is not int or self.maintenance_version < 1:
            raise ValueError("maintenance_version must be a positive integer")


@dataclass(frozen=True)
class ExecutionFence:
    """Persisted execution authority carried by every business dispatch step."""

    epoch: str
    owner_context_id: str
    attempt: int
    claim_token: str = field(repr=False)
    lease_until: datetime
    hard_deadline: datetime

    def __post_init__(self) -> None:
        stable_id(self.epoch, name="epoch")
        stable_id(self.owner_context_id, name="owner_context_id")
        if type(self.attempt) is not int or self.attempt < 1:
            raise ValueError("attempt must be a positive integer")
        claim_token(self.claim_token)
        _aware(self.lease_until, "lease_until")
        _aware(self.hard_deadline, "hard_deadline")
        if self.lease_until > self.hard_deadline:
            raise ValueError("lease_until cannot be later than hard_deadline")


@dataclass(frozen=True)
class ExecutionContext:
    """Persisted current authority; read from its row, never from a caller claim."""

    context_id: str
    epoch: str
    holder_id: str
    space_id: str
    purpose: str
    config_fingerprint: str
    attempt: int
    claim_token: str = field(repr=False)
    lease_until: datetime
    hard_deadline: datetime
    state: str

    def __post_init__(self) -> None:
        stable_id(self.context_id, name="context_id")
        stable_id(self.epoch, name="epoch")
        stable_id(self.holder_id, name="holder_id")
        stable_id(self.space_id, name="space_id")
        activity_label(self.purpose, name="purpose")
        evidence_fingerprint(self.config_fingerprint, name="config_fingerprint")
        if type(self.attempt) is not int or self.attempt < 1:
            raise ValueError("attempt must be a positive integer")
        claim_token(self.claim_token)
        _aware(self.lease_until, "lease_until")
        _aware(self.hard_deadline, "hard_deadline")
        if self.lease_until > self.hard_deadline:
            raise ValueError("lease_until cannot be later than hard_deadline")
        if self.state not in {"active", "terminal", "isolated"}:
            raise ValueError("context state must be active, terminal or isolated")

    def fence(self) -> ExecutionFence:
        return ExecutionFence(
            epoch=self.epoch, owner_context_id=self.context_id,
            attempt=self.attempt, claim_token=self.claim_token,
            lease_until=self.lease_until, hard_deadline=self.hard_deadline,
        )


@dataclass(frozen=True)
class CallGrant:
    """The one persisted send authority for a call; grant_id is not logged."""

    call_id: str
    attempt: int
    boot_id: str
    child_instance: str
    grant_id: str = field(repr=False)

    def __post_init__(self) -> None:
        stable_id(self.call_id, name="call_id")
        if type(self.attempt) is not int or self.attempt < 1:
            raise ValueError("attempt must be a positive integer")
        bounded_identifier(self.boot_id, name="boot_id")
        bounded_identifier(self.child_instance, name="child_instance")
        stable_id(self.grant_id, name="grant_id")


class SQLSession(Protocol):
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...


class EpochControl(Protocol):
    """Reads the independent control record and compares the DB mirror."""

    def current(self) -> Epoch: ...

    def verify_mirror(
        self, session: SQLSession, *, expected: Epoch | None = None,
    ) -> None: ...


class CallStore(Protocol):
    """Persistence port; one short transaction, never commits on its own."""

    def verify_epoch_mirror(
        self, control: EpochControl, expected: Epoch,
    ) -> None: ...

    def current_time(self) -> datetime:
        """Current authoritative DB time, read after the required locks."""

    def insert_call(self, **values: Any) -> None: ...

    def lock_context(self, context_id: str) -> dict[str, Any] | None: ...

    def insert_context(self, **values: Any) -> None: ...

    def replace_attempt(self, **values: Any) -> bool: ...

    def terminate_context(self, **values: Any) -> bool: ...

    def lock_call(self, call_id: str) -> dict[str, Any] | None: ...

    def mark_may_have_sent(
        self, record: dict[str, Any], **values: Any,
    ) -> bool: ...

    def record_terminal(self, record: dict[str, Any], **values: Any) -> None: ...

    def list_facts(self, call_id: str) -> list[dict[str, Any]]: ...

    def insert_fact(self, **values: Any) -> None: ...

    def require_reconciliation(self, call_id: str) -> None: ...


class CallStoreFactory(Protocol):
    def __call__(self, session: SQLSession) -> CallStore: ...


LOCK_ORDER = (
    "account", "space", "kb", "business", "capacity", "gate", "pool",
    "call", "permit", "asset",
)


class LockOrder:
    """Rejects a re-acquisition of an earlier C4 category in the same unit.

    PostgreSQL enforces the actual row locks; this guard catches the code path
    that would otherwise deadlock by asking for a parent after a call lock.
    """

    def __init__(self) -> None:
        self._last = -1

    def acquire(self, category: str) -> None:
        try:
            rank = LOCK_ORDER.index(category)
        except ValueError:
            raise GuardError("CALL_LOCK_ORDER_INVALID") from None
        if rank < self._last:
            raise GuardError("CALL_LOCK_ORDER_INVALID")
        self._last = rank
