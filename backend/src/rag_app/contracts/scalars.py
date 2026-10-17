"""Unicode scalar, UTC and deterministic JSON wire primitives."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, PlainSerializer, WithJsonSchema


def scalar_text(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("text must be a string")
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise ValueError("surrogate code points are not allowed")
    return value


def scalar_length(value: str) -> int:
    return len(scalar_text(value))


def scalar_slice(value: str, start: int, end: int) -> str:
    """Slice a half-open range without normalization or UTF-16 indexing."""
    scalar_text(value)
    if type(start) is not int or type(end) is not int:
        raise ValueError("slice bounds must be integers")
    if not 0 <= start <= end <= len(value):
        raise ValueError("slice bounds are outside the scalar range")
    return value[start:end]


def validate_wire_values(value: Any) -> Any:
    """Check nested strings, including object keys, without changing values."""
    if isinstance(value, str):
        scalar_text(value)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite numbers are not allowed")
    elif isinstance(value, dict):
        for key, item in value.items():
            scalar_text(key)
            validate_wire_values(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            validate_wire_values(item)
    return value


def stable_json_bytes(value: Any) -> bytes:
    """Serialize JSON wire objects, preserving explicit null and array order."""
    validate_wire_values(value)
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON keys are not allowed")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise ValueError("non-finite JSON numbers are not allowed")


def strict_json_loads(value: str | bytes | bytearray) -> Any:
    if not isinstance(value, (str, bytes, bytearray)):
        raise ValueError("JSON input must be text or UTF-8 bytes")
    if isinstance(value, (bytes, bytearray)):
        value = bytes(value).decode("utf-8", errors="strict")
    return validate_wire_values(json.loads(
        value, object_pairs_hook=_unique_object, parse_constant=_reject_constant,
    ))


def utc_z(value: Any) -> datetime:
    """Parse RFC3339 Z strings, or normalize an aware server datetime to UTC."""
    if isinstance(value, str):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value):
            raise ValueError("wire timestamp must be an RFC3339 UTC Z string")
        try:
            value = datetime.fromisoformat(value[:-1] + "+00:00")
        except ValueError:
            raise ValueError("invalid UTC timestamp") from None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be an aware datetime or RFC3339 Z string")
    return value.astimezone(timezone.utc)


def decimal_amount(value: Any) -> Decimal:
    if not isinstance(value, (str, Decimal)):
        raise ValueError("money requires a decimal string or Decimal, never a float")
    if isinstance(value, str) and not re.fullmatch(r"\d+(?:\.\d+)?", value):
        raise ValueError("money must be a nonnegative finite decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError("invalid decimal amount") from None
    if not result.is_finite() or result < 0:
        raise ValueError("money must be nonnegative and finite")
    return result


WireText = Annotated[str, BeforeValidator(scalar_text)]
StableId = Annotated[
    WireText, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$"),
]
UtcDateTime = Annotated[
    datetime, BeforeValidator(utc_z),
    PlainSerializer(lambda value: value.isoformat().replace("+00:00", "Z"), return_type=str),
    WithJsonSchema({"type": "string", "format": "date-time", "pattern": r"Z$"}),
]
FiniteDecimal = Annotated[
    Decimal, BeforeValidator(decimal_amount),
    PlainSerializer(lambda value: format(value, "f"), return_type=str, when_used="json"),
    WithJsonSchema({"type": "string", "pattern": r"^\d+(?:\.\d+)?$"}),
]
