"""PostgreSQL persistence for execution calls and append-only call facts.

The repository never commits, rolls back or closes the caller's session.  It
only locks the addressed call row, matching the C4 order; late facts never
acquire a business, gate or pool lock.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text

from rag_app.adapters.postgres import validate_schema, verify_namespace
from rag_app.modules.execution.calls import (
    ExecutionFence, LockOrder, claim_digest,
)


CALL_COLUMNS = (
    "c.call_id, c.epoch, c.owner_context_id, c.holder_id, c.space_id, "
    "c.purpose, c.stage, c.attempt, c.claim_token_digest, "
    "c.config_fingerprint, c.request_hash, c.state, c.prepared_at, "
    "c.lease_until, c.hard_deadline, c.may_have_sent_at, c.grant_id, "
    "c.boot_id, c.child_instance, c.terminal_at, c.provider_ref, "
    "c.usage_status, c.prompt_tokens, c.completion_tokens, c.total_tokens, "
    "c.cost_kind, c.cost_amount, c.cost_currency, c.cost_basis, "
    "c.reconciliation_status"
)

CALL_FIELDS = (
    "call_id", "epoch", "owner_context_id", "holder_id", "space_id",
    "purpose", "stage", "attempt", "claim_token_digest", "config_fingerprint",
    "request_hash", "state", "prepared_at", "lease_until", "hard_deadline",
    "may_have_sent_at", "grant_id", "boot_id", "child_instance", "terminal_at",
    "provider_ref", "usage_status", "prompt_tokens", "completion_tokens",
    "total_tokens", "cost_kind", "cost_amount", "cost_currency", "cost_basis",
    "reconciliation_status",
)

FACT_FIELDS = (
    "fact_digest", "provider_ref", "usage_status", "prompt_tokens",
    "completion_tokens", "total_tokens", "cost_kind", "cost_amount",
    "cost_currency", "cost_basis", "source", "received_at", "disposition",
)


def call_record(row: Any) -> dict[str, Any]:
    return {name: row[index] for index, name in enumerate(CALL_FIELDS)}


def _quoted_schema(schema: str) -> str:
    return '"' + validate_schema(schema).replace('"', '""') + '"'


def _call_table(schema: str) -> str:
    return f"{_quoted_schema(schema)}.execution_call"


def _context_table(schema: str) -> str:
    return f"{_quoted_schema(schema)}.execution_context"


def _fact_table(schema: str) -> str:
    return f"{_quoted_schema(schema)}.ledger_call_fact"


class CallRepository:
    """One short-transaction repository; it never owns transaction lifetime."""

    def __init__(
        self, session: Any, *, schema: str, lock_order: LockOrder | None = None,
    ) -> None:
        self._session = session
        self._schema = schema
        self._lock_order = lock_order

    def _ready(self) -> None:
        verify_namespace(self._session, self._schema)

    def verify_epoch_mirror(self, control: Any, expected: Any) -> None:
        control.verify_mirror(self._session, expected=expected)

    def current_time(self) -> datetime:
        """DB clock authority for a fresh lease/deadline check after locking."""

        return self._session.execute(
            text("SELECT clock_timestamp()")
        ).scalar_one()

    def insert_call(
        self, *, call_id: str, fence: ExecutionFence, holder_id: str,
        space_id: str, purpose: str, stage: str, config_fingerprint: str,
        request_hash: str, now: datetime,
    ) -> None:
        self._ready()
        self._session.execute(text(
            f"INSERT INTO {_call_table(self._schema)} ("
            "call_id, epoch, owner_context_id, holder_id, space_id, purpose, "
            "stage, attempt, claim_token_digest, config_fingerprint, "
            "request_hash, state, prepared_at, lease_until, hard_deadline"
            ") VALUES ("
            ":call_id, :epoch, :owner_context_id, :holder_id, :space_id, "
            ":purpose, :stage, :attempt, :claim_token_digest, "
            ":config_fingerprint, :request_hash, 'prepared', :prepared_at, "
            ":lease_until, :hard_deadline)"
        ), {
                "call_id": call_id, "epoch": fence.epoch,
                "owner_context_id": fence.owner_context_id,
                "holder_id": holder_id, "space_id": space_id,
                "purpose": purpose, "stage": stage, "attempt": fence.attempt,
                "claim_token_digest": claim_digest(fence.claim_token),
                "config_fingerprint": config_fingerprint,
                "request_hash": request_hash, "prepared_at": now,
                "lease_until": fence.lease_until,
                "hard_deadline": fence.hard_deadline,
        })

    def lock_call(self, call_id: str) -> dict[str, Any] | None:
        self._ready()
        if self._lock_order is not None:
            self._lock_order.acquire("call")
        row = self._session.execute(text(
            f"SELECT {CALL_COLUMNS} FROM {_call_table(self._schema)} AS c "
            "WHERE c.call_id = :call_id FOR UPDATE"
        ), {"call_id": call_id}).one_or_none()
        return None if row is None else call_record(row)

    def lock_context(self, context_id: str) -> dict[str, Any] | None:
        self._ready()
        if self._lock_order is not None:
            self._lock_order.acquire("business")
        row = self._session.execute(text(
            "SELECT context_id, epoch, holder_id, space_id, purpose, "
            "config_fingerprint, attempt, claim_token_digest, lease_until, "
            "hard_deadline, state "
            f"FROM {_context_table(self._schema)} "
            "WHERE context_id = :context_id FOR UPDATE"
        ), {"context_id": context_id}).one_or_none()
        if row is None:
            return None
        names = (
            "context_id", "epoch", "holder_id", "space_id", "purpose",
            "config_fingerprint", "attempt", "claim_token_digest",
            "lease_until", "hard_deadline", "state",
        )
        return {name: row[index] for index, name in enumerate(names)}

    def insert_context(
        self, *, context_id: str, epoch: str, holder_id: str, space_id: str,
        purpose: str, config_fingerprint: str, attempt: int,
        claim_token_digest: str, lease_until: datetime,
        hard_deadline: datetime,
    ) -> None:
        self._ready()
        self._session.execute(text(
            f"INSERT INTO {_context_table(self._schema)} ("
            "context_id, epoch, holder_id, space_id, purpose, "
            "config_fingerprint, attempt, claim_token_digest, lease_until, "
            "hard_deadline, state"
            ") VALUES ("
            ":context_id, :epoch, :holder_id, :space_id, :purpose, "
            ":config_fingerprint, :attempt, :claim_token_digest, :lease_until, "
            ":hard_deadline, 'active')"
        ), {
                "context_id": context_id, "epoch": epoch,
                "holder_id": holder_id, "space_id": space_id,
                "purpose": purpose, "config_fingerprint": config_fingerprint,
                "attempt": attempt, "claim_token_digest": claim_token_digest,
                "lease_until": lease_until, "hard_deadline": hard_deadline,
        })

    def replace_attempt(
        self, *, context_id: str, attempt: int, claim_token_digest: str,
        lease_until: datetime, hard_deadline: datetime,
    ) -> bool:
        result = self._session.execute(text(
            f"UPDATE {_context_table(self._schema)} SET attempt = :attempt, "
            "claim_token_digest = :claim_token_digest, "
            "lease_until = :lease_until, hard_deadline = :hard_deadline, "
            "state = 'active' "
            "WHERE context_id = :context_id AND state = 'active' "
            "AND attempt < :attempt"
        ), {
                "context_id": context_id, "attempt": attempt,
                "claim_token_digest": claim_token_digest,
                "lease_until": lease_until, "hard_deadline": hard_deadline,
        })
        return result.rowcount == 1

    def terminate_context(
        self, *, context_id: str, state: str,
    ) -> bool:
        result = self._session.execute(text(
            f"UPDATE {_context_table(self._schema)} SET state = :state "
            "WHERE context_id = :context_id AND state = 'active'"
        ), {"context_id": context_id, "state": state})
        return result.rowcount == 1

    def mark_may_have_sent(
        self, record: dict[str, Any], *, grant_id: str, boot_id: str,
        child_instance: str, now: datetime,
    ) -> bool:
        result = self._session.execute(text(
            f"UPDATE {_call_table(self._schema)} SET state = 'may_have_sent', "
            "grant_id = :grant_id, boot_id = :boot_id, "
            "child_instance = :child_instance, may_have_sent_at = :now "
            "WHERE call_id = :call_id AND state = 'prepared'"
        ), {
                "call_id": record["call_id"], "grant_id": grant_id,
                "boot_id": boot_id, "child_instance": child_instance,
                "now": now,
        })
        return result.rowcount == 1

    def record_terminal(
        self, record: dict[str, Any], *, outcome: str, at: datetime,
        provider_ref: str | None, usage: Any, cost: Any,
    ) -> None:
        self._session.execute(text(
            f"UPDATE {_call_table(self._schema)} SET state = :outcome, "
            "terminal_at = :at, provider_ref = :provider_ref, "
            "usage_status = :usage_status, prompt_tokens = :prompt_tokens, "
            "completion_tokens = :completion_tokens, "
            "total_tokens = :total_tokens, cost_kind = :cost_kind, "
            "cost_amount = :cost_amount, cost_currency = :cost_currency, "
            "cost_basis = :cost_basis "
            "WHERE call_id = :call_id AND state = 'may_have_sent'"
        ), {
                "call_id": record["call_id"], "outcome": outcome, "at": at,
                "provider_ref": provider_ref,
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

    def list_facts(self, call_id: str) -> list[dict[str, Any]]:
        rows = self._session.execute(text(
            "SELECT " + ", ".join(FACT_FIELDS)
            + f" FROM {_fact_table(self._schema)} WHERE call_id = :call_id "
            "ORDER BY fact_id"
        ), {"call_id": call_id}).all()
        return [
            {name: row[index] for index, name in enumerate(FACT_FIELDS)}
            for row in rows
        ]

    def insert_fact(
        self, *, call_id: str, digest: str, provider_ref: str | None,
        usage: Any, cost: Any, source: str, received_at: datetime,
        disposition: str,
    ) -> bool:
        result = self._session.execute(text(
            f"INSERT INTO {_fact_table(self._schema)} ("
            "call_id, fact_digest, provider_ref, usage_status, prompt_tokens, "
            "completion_tokens, total_tokens, cost_kind, cost_amount, "
            "cost_currency, cost_basis, source, received_at, disposition"
            ") VALUES ("
            ":call_id, :fact_digest, :provider_ref, :usage_status, "
            ":prompt_tokens, :completion_tokens, :total_tokens, :cost_kind, "
            ":cost_amount, :cost_currency, :cost_basis, :source, :received_at, "
            ":disposition) ON CONFLICT (call_id, fact_digest) DO NOTHING"
        ), {
                "call_id": call_id, "fact_digest": digest,
                "provider_ref": provider_ref,
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
                "source": source, "received_at": received_at,
                "disposition": disposition,
        })
        return result.rowcount == 1

    def require_reconciliation(self, call_id: str) -> None:
        self._session.execute(text(
            f"UPDATE {_call_table(self._schema)} SET "
            "reconciliation_status = 'required' WHERE call_id = :call_id"
        ), {"call_id": call_id})
