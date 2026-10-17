"""C1-NZ: native Decimal negative zero must serialize as unsigned wire zero."""

from decimal import Decimal
import re

import pytest
from pydantic import TypeAdapter, ValidationError

from rag_app.contracts.public import Money
from rag_app.contracts.scalars import (
    FiniteDecimal, decimal_amount, decimal_wire_text, strict_json_loads,
)


AMOUNT_PATTERN = r"^\d+(?:\.\d+)?$"


def _money(amount: Decimal, source: str = "bill") -> Money:
    return Money(amount=amount, currency="CNY", source=source)


@pytest.mark.parametrize("amount,wire", [
    (Decimal("-0"), "0"),
    (Decimal("-0.0"), "0.0"),
    (Decimal("-0.00"), "0.00"),
    (Decimal("-0.000000"), "0.000000"),
])
def test_native_negative_zero_serializes_unsigned_and_reloads(amount, wire):
    money = _money(amount)
    assert money.amount == Decimal("0")
    assert not money.amount.is_signed()
    dumped = money.model_dump(mode="json")
    assert dumped["amount"] == wire
    assert dumped["amount"].startswith("-") is False

    reloaded = Money.model_validate_json(money.model_dump_json())
    assert reloaded == money
    assert reloaded.model_dump(mode="json")["amount"] == wire
    json_text = money.model_dump_json()
    assert strict_json_loads(json_text)["amount"] == wire


@pytest.mark.parametrize("source", ["estimate", "bill"])
def test_negative_zero_is_unsigned_for_both_known_money_sources(source):
    money = _money(Decimal("-0.00"), source=source)
    assert money.model_dump(mode="json")["amount"] == "0.00"
    assert Money.model_validate_json(money.model_dump_json()) == money


@pytest.mark.parametrize("amount,wire", [
    (Decimal("0"), "0"),
    (Decimal("0.0"), "0.0"),
    (Decimal("0.00"), "0.00"),
    (Decimal("1"), "1"),
    (Decimal("1.20"), "1.20"),
    (Decimal("0.100"), "0.100"),
    (Decimal("12345.678900"), "12345.678900"),
])
def test_unsigned_zero_and_positive_amounts_keep_precision(amount, wire):
    money = _money(amount)
    dumped = money.model_dump(mode="json")
    assert dumped["amount"] == wire
    assert not dumped["amount"].startswith("-")
    assert Money.model_validate_json(money.model_dump_json()) == money


def test_decimal_wire_text_matches_exported_schema_pattern():
    for value in ["-0", "-0.00", "0", "0.00", "1.20"]:
        text = decimal_wire_text(Decimal(value))
        assert text is not None
        assert re.fullmatch(AMOUNT_PATTERN, text) is not None, text
        assert TypeAdapter(FiniteDecimal).validate_json(f'"{text}"') == Decimal(text)


@pytest.mark.parametrize("value", ["-0", "-0.00", "-0.0"])
def test_negative_zero_wire_strings_are_still_rejected(value):
    assert re.fullmatch(AMOUNT_PATTERN, value) is None
    with pytest.raises(ValidationError):
        _money(value)
    with pytest.raises(ValueError):
        decimal_amount(value)


@pytest.mark.parametrize("value", [
    Decimal("-0.01"), Decimal("-1"), "-0.01", "-1.00",
])
def test_real_negative_amounts_are_still_rejected(value):
    with pytest.raises(ValidationError):
        _money(value)


@pytest.mark.parametrize("value", [
    Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity"),
    "NaN", "Infinity", 0.0, -0.0, 0, 1, True, None,
])
def test_nonfinite_float_and_nonstring_inputs_remain_rejected(value):
    with pytest.raises(ValidationError):
        _money(value)


def test_unknown_money_keeps_null_and_never_zero():
    money = Money(amount=None, currency=None, source="unknown")
    dumped = money.model_dump(mode="json")
    assert dumped == {"amount": None, "currency": None, "source": "unknown"}
    assert Money.model_validate_json(money.model_dump_json()) == money


def test_negative_zero_does_not_change_schema_or_accepted_positive_values():
    schema = Money.model_json_schema()
    amount_schema = schema["properties"]["amount"]
    assert {"type": "string", "pattern": AMOUNT_PATTERN} in amount_schema["anyOf"]
    assert set(schema["required"]) == {"amount", "currency", "source"}
    for value in ["0", "0.00", "1.20"]:
        dto = _money(value)
        assert dto.model_dump(mode="json")["amount"] == value
