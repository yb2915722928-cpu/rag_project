"""Framework-free provider fact values; facts are append-only observations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import hashlib
import json
import re
from typing import Literal


_FACT_LABEL = re.compile(r"[a-z][a-z0-9_.-]{0,63}\Z")
_CURRENCY = re.compile(r"[A-Z]{3}\Z")
_PROVIDER_REF = re.compile(r"[\x21-\x7e]{1,256}\Z")


def _aware(value: datetime, name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be an aware datetime")


def _optional_tokens(value: object, name: str) -> None:
    if value is None:
        return
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer or None")


def _provider_reference(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or _PROVIDER_REF.fullmatch(value) is None:
        raise ValueError("provider_ref has an invalid format")
    if "://" in value or "?" in value or "#" in value:
        raise ValueError("provider_ref cannot contain a URL or signature")
    return value


def _fact_label(value: object, name: str) -> str:
    if not isinstance(value, str) or _FACT_LABEL.fullmatch(value) is None:
        raise ValueError(f"{name} has an invalid format")
    return value


@dataclass(frozen=True)
class UsageFact:
    status: Literal["unknown", "reported"]
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    def __post_init__(self) -> None:
        if self.status not in {"unknown", "reported"}:
            raise ValueError("usage status must be unknown or reported")
        _optional_tokens(self.prompt_tokens, "prompt_tokens")
        _optional_tokens(self.completion_tokens, "completion_tokens")
        _optional_tokens(self.total_tokens, "total_tokens")
        if self.status == "unknown" and any(
            value is not None
            for value in (self.prompt_tokens, self.completion_tokens, self.total_tokens)
        ):
            raise ValueError("unknown usage cannot carry token values")
        if self.status == "reported" and all(
            value is None
            for value in (self.prompt_tokens, self.completion_tokens, self.total_tokens)
        ):
            raise ValueError("reported usage needs at least one token count")


@dataclass(frozen=True)
class CostFact:
    """Distinguishes an estimate from an actual billed amount."""

    kind: Literal["estimated", "actual"]
    amount: Decimal | None
    currency: str | None
    basis: str

    def __post_init__(self) -> None:
        if self.kind not in {"estimated", "actual"}:
            raise ValueError("cost kind must be estimated or actual")
        _fact_label(self.basis, "basis")
        if self.amount is None:
            if self.currency is not None:
                raise ValueError("a missing amount cannot carry a currency")
            return
        if not isinstance(self.amount, Decimal) or not self.amount.is_finite():
            raise ValueError("amount must be a finite Decimal or None")
        if self.amount < 0:
            raise ValueError("amount cannot be negative")
        if not isinstance(self.currency, str) or _CURRENCY.fullmatch(self.currency) is None:
            raise ValueError("currency must be a three-letter uppercase code")


@dataclass(frozen=True)
class ResultFact:
    outcome: Literal["responded", "known_failure"]
    provider_ref: str | None
    usage: UsageFact | None
    cost: CostFact | None
    at: datetime

    def __post_init__(self) -> None:
        if self.outcome not in {"responded", "known_failure"}:
            raise ValueError("result outcome must be responded or known_failure")
        _provider_reference(self.provider_ref)
        if self.usage is not None and not isinstance(self.usage, UsageFact):
            raise ValueError("usage must be a UsageFact or None")
        if self.cost is not None and not isinstance(self.cost, CostFact):
            raise ValueError("cost must be a CostFact or None")
        _aware(self.at, "at")


@dataclass(frozen=True)
class LateFact:
    """A trusted provider observation that may arrive after business termination."""

    provider_ref: str | None
    usage: UsageFact | None
    cost: CostFact | None
    source: str
    received_at: datetime

    def __post_init__(self) -> None:
        _provider_reference(self.provider_ref)
        if self.usage is not None and not isinstance(self.usage, UsageFact):
            raise ValueError("usage must be a UsageFact or None")
        if self.cost is not None and not isinstance(self.cost, CostFact):
            raise ValueError("cost must be a CostFact or None")
        _fact_label(self.source, "source")
        _aware(self.received_at, "received_at")
        if self.provider_ref is None and self.usage is None and self.cost is None:
            raise ValueError("a late fact needs a provider ref, usage or cost")


@dataclass(frozen=True)
class LateFactOutcome:
    disposition: Literal["appended", "duplicate", "conflict"]

    def __post_init__(self) -> None:
        if self.disposition not in {"appended", "duplicate", "conflict"}:
            raise ValueError("fact disposition must be appended, duplicate or conflict")


def _decimal_key(value: Decimal) -> str:
    if value.is_zero():
        return "0"
    return format(value.normalize(), "f")


def fact_digest(
    *, provider_ref: str | None, usage: UsageFact | None, cost: CostFact | None,
) -> str:
    """Identity of the factual observation; source and arrival time are provenance."""

    payload = {
        "provider_ref": provider_ref,
        "usage": None if usage is None else {
            "status": usage.status,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        },
        "cost": None if cost is None else {
            "kind": cost.kind,
            "amount": None if cost.amount is None else _decimal_key(cost.amount),
            "currency": cost.currency,
        },
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
