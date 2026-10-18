"""C1/C2 positive and negative wire examples; no database or provider calls."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from itertools import product
from typing import get_args

import pytest
from pydantic import TypeAdapter, ValidationError

from rag_app.contracts.errors import MESSAGES, SafeError
from rag_app.contracts.public import (
    ERROR_POLICY, PUBLIC_ENUMS, PUBLIC_MODELS, AcceptedResponse, AnswerPayload,
    CompletedResponse, ErrorCode, ErrorDetails, EvidenceBlock, FailedResponse,
    JobState, Money, OperationResponse, OperationState, Outcome, PublicError,
    RetrievalResponse, RetryMode, Status, Usage,
)
from rag_app.contracts.scalars import (
    StableId, UtcDateTime, scalar_length, scalar_slice, stable_json_bytes,
    strict_json_loads,
)

NOW = "2026-10-17T08:00:00Z"
LATER = "2026-10-17T08:01:00Z"
TEXT = "A\u0301 \u4e2d\u6587 \U0001f600\r\n"


def evidence(index=1):
    return {
        "evidence_id": f"e{index}", "chunk_id": f"c{index}",
        "excerpt": "\U0001f600", "start": 0, "end": 1,
    }


def accepted():
    return {
        "schema_version": "operation.v1", "request_id": "req-1", "status": "in_progress",
        "operation_id": "op-1", "operation_state": "accepted",
        "accepted_at": NOW, "status_url": "/operations/op-1",
        "retry_mode": "same_key_or_status",
    }


def fact():
    return {
        "id": "f1", "kind": "step", "order": 1, "text": TEXT,
        "applicability": "", "evidence_ids": ["e1"],
        "quantity": None, "conflict_sides": None,
    }


def completed():
    return {
        "schema_version": "answer.v1", "request_id": "req-1", "status": "completed",
        "operation_id": "op-1", "replayed": False, "accepted_at": NOW,
        "completed_at": LATER, "execution_snapshot_id": "snapshot-1",
        "outcome": "answered", "summary": {"text": TEXT, "fact_ids": ["f1"]},
        "facts": [fact()], "gaps": [], "clarifications": [],
        "evidence_catalog": [evidence()],
    }


def retrieval():
    return {
        "schema_version": "retrieval.v1", "request_id": "req-1", "status": "completed",
        "retrieval_execution_id": "retr-1", "deadline": LATER,
        "evidence_catalog": [evidence()],
    }


def failed():
    return {
        "schema_version": "operation.v1", "request_id": "req-1", "status": "failed",
        "error": PublicError.from_code("DEPENDENCY_UNAVAILABLE").model_dump(mode="json"),
    }


def operation():
    return {
        "schema_version": "operation.v1", "request_id": "req-1", "status": "in_progress",
        "operation_id": "op-1", "operation_state": "running", "error": None,
    }


RESPONSE_EXAMPLES = [
    (AcceptedResponse, accepted), (CompletedResponse, completed),
    (RetrievalResponse, retrieval), (FailedResponse, failed),
    (OperationResponse, operation),
]


def test_unicode_scalar_rules_and_stable_json():
    assert scalar_length(TEXT) == 9
    assert scalar_slice(TEXT, 0, 3) == "A\u0301 "
    assert scalar_slice(TEXT, 6, 7) == "\U0001f600"
    assert scalar_slice(TEXT, 7, 9) == "\r\n"
    assert scalar_slice(TEXT, 9, 9) == ""
    value = {"b": 1, "a": "\u4e2d\u6587"}
    assert stable_json_bytes(value) == '{"a":"\u4e2d\u6587","b":1}'.encode("utf-8")
    assert stable_json_bytes({"x": None}) != stable_json_bytes({})
    assert strict_json_loads(stable_json_bytes({"x": TEXT})) == {"x": TEXT}
    assert EvidenceBlock(**evidence()).excerpt == "\U0001f600"


@pytest.mark.parametrize("start,end", [(-1, 1), (0, 10), (2, 1), (True, 1), (0, 1.0)])
def test_scalar_slice_rejects_invalid_half_open_ranges(start, end):
    with pytest.raises(ValueError):
        scalar_slice(TEXT, start, end)


@pytest.mark.parametrize("text", ["\ud800", "\udfff", "x\ud800y"])
def test_surrogates_rejected_by_all_scalar_entrypoints(text):
    for call in [
        lambda: scalar_length(text), lambda: scalar_slice(text, 0, 1),
        lambda: stable_json_bytes({"x": text}), lambda: stable_json_bytes({text: "x"}),
    ]:
        with pytest.raises(ValueError):
            call()


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_stable_json_rejects_nonfinite_numbers(value):
    with pytest.raises(ValueError):
        stable_json_bytes({"nested": [value]})


@pytest.mark.parametrize("value", [
    '{"x":1,"x":2}', '{"x":{"a":1,"a":2}}', '{"x":NaN}',
    '{"x":Infinity}', '{"x":1e9999}', '{"x":"\\ud800"}', b'{"x":"\xff"}',
])
def test_json_decoder_rejects_duplicate_keys_nonfinite_and_invalid_utf8(value):
    with pytest.raises(ValueError):
        strict_json_loads(value)


@pytest.mark.parametrize("value", ["a", "A_0-9", "a" * 64])
def test_stable_ids_positive(value):
    assert TypeAdapter(StableId).validate_python(value) == value


@pytest.mark.parametrize("value", ["", "a" * 65, "\u4e2d", "a b", "a/b", "x\n", "\ud800", 1, None])
def test_stable_ids_negative(value):
    with pytest.raises(ValidationError):
        TypeAdapter(StableId).validate_python(value)


def test_utc_z_json_parse_normalization_and_export():
    adapter = TypeAdapter(UtcDateTime)
    assert adapter.validate_json(f'"{NOW}"').tzinfo == timezone.utc
    local = datetime(2026, 10, 17, 16, tzinfo=timezone(timedelta(hours=8)))
    assert adapter.dump_json(adapter.validate_python(local)) == f'"{NOW}"'.encode()
    dto = AcceptedResponse.model_validate_json(stable_json_bytes(accepted()))
    assert dto.model_dump(mode="json")["accepted_at"] == NOW
    assert strict_json_loads(dto.model_dump_json())["accepted_at"] == NOW


@pytest.mark.parametrize("value", [
    None, 0, 1.2, {}, [], "2026-10-17", "2026-10-17T08:00:00",
    "2026-10-17T08:00:00+00:00", "2026-02-30T08:00:00Z",
    datetime(2026, 10, 17, 8), "\ud800",
])
def test_utc_z_invalid_inputs_are_validation_errors(value):
    with pytest.raises(ValidationError):
        TypeAdapter(UtcDateTime).validate_python(value)


@pytest.mark.parametrize("model,factory", RESPONSE_EXAMPLES)
def test_response_wire_roundtrip_and_unknown_fields(model, factory):
    data = factory()
    dto = model.model_validate_json(stable_json_bytes(data))
    assert model.model_validate_json(dto.model_dump_json()) == dto
    with pytest.raises(ValidationError):
        model.model_validate({**data, "upstream_body": "private"})
    with pytest.raises(ValidationError):
        model.model_validate({**data, "schema_version": "unknown.v9"})
    with pytest.raises(ValidationError):
        model.model_validate({**data, "schema_version": None})
    with pytest.raises(ValidationError):
        model.model_validate({**data, "request_id": "\ud800"})
    with pytest.raises(ValidationError):
        model.model_validate_json(
            stable_json_bytes(data).decode()[:-1] + ',"request_id":"duplicate"}'
        )


@pytest.mark.parametrize("field,value", [
    ("status", "completed"), ("operation_state", "completed"),
    ("retry_mode", "new_operation"), ("answer", "half an answer"),
    ("facts", []), ("evidence_catalog", []),
])
def test_accepted_forbids_half_answers_and_inconsistent_state(field, value):
    with pytest.raises(ValidationError):
        AcceptedResponse.model_validate({**accepted(), field: value})


@pytest.mark.parametrize("path", [
    "https://evil.test/operations/op-1", "//evil.test/op-1", "/admin",
    "/operations/op-2", "/operations/op-1?token=secret", "/operations/op-1#x",
    "/operations/../op-1", "/operations/%6fp-1", "/operations/op-1/",
    "/operations/op-1\n", "/operations/op-1\\x",
])
def test_status_url_matches_exact_operation_route(path):
    with pytest.raises(ValidationError):
        AcceptedResponse.model_validate({**accepted(), "status_url": path})


@pytest.mark.parametrize("state,status", list(product(
    ["accepted", "running", "completed", "failed"],
    ["in_progress", "completed", "failed"],
)))
def test_get_operation_state_status_error_matrix(state, status):
    data = {**operation(), "operation_state": state, "status": status}
    if state == "failed":
        data["error"] = PublicError.from_code("DEPENDENCY_TIMEOUT")
    expected = {"accepted": "in_progress", "running": "in_progress",
                "completed": "completed", "failed": "failed"}[state]
    if expected == status:
        dto = OperationResponse.model_validate(data)
        if dto.error:
            assert dto.error.http_status == 504
    else:
        with pytest.raises(ValidationError):
            OperationResponse.model_validate(data)


def test_get_operation_error_null_is_explicit_and_terminal_error_required():
    data = operation()
    del data["error"]
    with pytest.raises(ValidationError):
        OperationResponse.model_validate(data)
    with pytest.raises(ValidationError):
        OperationResponse.model_validate({**operation(), "error": PublicError.from_code("DEPENDENCY_TIMEOUT")})
    with pytest.raises(ValidationError):
        OperationResponse.model_validate({
            **operation(), "operation_state": "failed", "status": "failed", "error": None,
        })


def test_money_decimal_arithmetic_and_string_wire_format():
    one = Money(amount="0.10", currency="CNY", source="estimate")
    two = Money(amount=Decimal("0.20"), currency="CNY", source="bill")
    assert one.amount + two.amount == Decimal("0.30")
    assert one.model_dump(mode="json")["amount"] == "0.10"
    assert Money.model_validate_json(two.model_dump_json()) == two
    assert Money(amount=None, currency=None, source="unknown").model_dump()["amount"] is None


@pytest.mark.parametrize("amount", [
    0.1, 1, True, float("nan"), float("inf"), "-1", "NaN", "Infinity",
    Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-0.01"),
    "", " 1", "1e3", "\ud800",
])
def test_money_rejects_float_nonfinite_negative_and_nonstrings(amount):
    with pytest.raises(ValidationError):
        Money(amount=amount, currency="CNY", source="bill")


@pytest.mark.parametrize("data", [
    {"amount": None, "currency": None, "source": "bill"},
    {"amount": "1.00", "currency": "CNY", "source": "unknown"},
    {"amount": "1.00", "currency": "CNY", "source": "vendor body"},
    {"amount": "1.00", "currency": "CNY"},
    {"amount": "1.00", "currency": "cny", "source": "bill"},
])
def test_money_source_and_null_consistency(data):
    with pytest.raises(ValidationError):
        Money.model_validate(data)


def test_usage_preserves_unknown_null_zero_and_missing_distinctions():
    assert Usage(input_tokens=None, output_tokens=None, unknown=True).input_tokens is None
    assert Usage(input_tokens=12, output_tokens=None, unknown=True).input_tokens == 12
    assert Usage(input_tokens=0, output_tokens=0, unknown=False).input_tokens == 0
    for data in [
        {}, {"unknown": True}, {"input_tokens": None, "output_tokens": None, "unknown": False},
        {"input_tokens": 0, "output_tokens": 0, "unknown": True},
        {"input_tokens": -1, "output_tokens": 0, "unknown": False},
        {"input_tokens": True, "output_tokens": 0, "unknown": False},
    ]:
        with pytest.raises(ValidationError):
            Usage.model_validate(data)


@pytest.mark.parametrize("patch", [
    {"code": "SOME_UPSTREAM_BODY"}, {"message": "private document body"},
    {"http_status": 200}, {"http_status": 503}, {"retry_mode": "automatic"},
    {"retry_mode": "none"}, {"details": {"target_id": "private-id"}},
    {"details": {"reason": "private document body"}},
    {"details": {"field": "private document title"}}, {"message": "\ud800"},
])
def test_public_errors_reject_arbitrary_metadata(patch):
    data = PublicError.from_code("DEPENDENCY_UNAVAILABLE").model_dump(mode="json")
    with pytest.raises(ValidationError):
        PublicError.model_validate({**data, **patch})


def test_safe_error_projection_and_finite_details():
    dto = PublicError.from_code(
        "VALIDATION_ERROR",
        details=ErrorDetails(field="question", reason="out_of_range"),
    )
    assert set(dto.model_dump()) == {"code", "message", "http_status", "retry_mode", "details"}
    with pytest.raises(ValidationError):
        ErrorDetails(retry_after_seconds=86401)
    with pytest.raises(ValueError):
        PublicError.from_code("UNREGISTERED")


@pytest.mark.parametrize("code,http_status", [
    ("REQUEST_HEADERS_LIMIT_EXCEEDED", 431),
    ("UNSUPPORTED_MEDIA_TYPE", 415),
    ("UNSUPPORTED_CONTENT_ENCODING", 415),
    ("REQUEST_STREAM_ERROR", 400),
    ("RESOURCE_UNAVAILABLE", 404),
    ("METHOD_NOT_ALLOWED", 405),
    ("INTERNAL_ERROR", 500),
])
def test_h_errors_have_finite_status_and_c2_envelope(code, http_status):
    error = PublicError.from_code(code)
    assert error.http_status == http_status
    assert error.retry_mode == "none"
    dto = FailedResponse.model_validate({**failed(), "error": error})
    wire = strict_json_loads(dto.model_dump_json())
    assert wire["schema_version"] == "operation.v1"
    assert wire["status"] == "failed"
    assert wire["request_id"] == "req-1"
    assert wire["error"]["code"] == code
    assert wire["error"]["http_status"] == http_status
    assert PublicError.model_validate_json(error.model_dump_json()) == error
    with pytest.raises(ValidationError):
        PublicError.model_validate({
            **error.model_dump(mode="json"), "message": "PRIVATE_UPSTREAM_BODY",
        })


@pytest.mark.parametrize("code", sorted(MESSAGES))
def test_existing_safe_errors_keep_original_message_code_and_503(code):
    sentinel = "PRIVATE_PASSWORD_BODY_SIGNED_URL_SENTINEL"
    original = SafeError(
        code, diagnostic_cause=RuntimeError(sentinel),
        cleanup_errors=(RuntimeError(sentinel),),
    )
    error = PublicError.from_code(original.code)
    assert error.code == code
    assert error.message == MESSAGES[code]
    assert error.http_status == 503
    expected_retry = "manual_reconcile" if code == "DATABASE_CLEANUP_FAILED" else "none"
    assert error.retry_mode == expected_retry
    dto = FailedResponse.model_validate({**failed(), "error": error})
    wire = strict_json_loads(dto.model_dump_json())
    assert wire["error"]["code"] == code
    assert wire["error"]["message"] == MESSAGES[code]
    assert wire["error"]["http_status"] == 503
    assert sentinel not in dto.model_dump_json()
    assert "diagnostic_cause" not in dto.model_dump_json()
    assert "cleanup_errors" not in dto.model_dump_json()
    assert FailedResponse.model_validate_json(dto.model_dump_json()) == dto
    for patch in [
        {"message": sentinel}, {"diagnostic_cause": sentinel},
        {"cleanup_errors": [sentinel]}, {"details": {"body": sentinel}},
        {"http_status": 500},
    ]:
        with pytest.raises(ValidationError):
            PublicError.model_validate({**error.model_dump(mode="json"), **patch})


@pytest.mark.parametrize("code,http_status,message", [
    ("METHOD_NOT_ALLOWED", 405, "Method not allowed."),
    ("INTERNAL_ERROR", 500, "Internal server error."),
])
def test_http_fallback_errors_only_export_fixed_safe_metadata(code, http_status, message):
    error = PublicError.from_code(code)
    assert error.message == message
    assert error.http_status == http_status
    assert error.retry_mode == "none"
    for patch in [
        {"message": "PRIVATE_EXCEPTION_BODY"},
        {"diagnostic_cause": "PRIVATE_EXCEPTION_BODY"},
        {"details": {"body": "PRIVATE_EXCEPTION_BODY"}},
        {"retry_mode": "new_operation"},
        {"http_status": 503},
    ]:
        with pytest.raises(ValidationError):
            PublicError.model_validate({**error.model_dump(mode="json"), **patch})


def test_error_policy_literal_and_exported_enum_are_exactly_aligned():
    assert set(get_args(ErrorCode)) == set(ERROR_POLICY)
    assert set(MESSAGES) <= set(ERROR_POLICY)
    assert set(PublicError.model_json_schema()["properties"]["code"]["enum"]) == set(ERROR_POLICY)
    for code in ERROR_POLICY:
        assert PublicError.from_code(code).code == code
    for code in ["unregistered", "PRIVATE_UPSTREAM_BODY", "DATABASE_NEW_UNKNOWN"]:
        with pytest.raises(ValueError):
            PublicError.from_code(code)


@pytest.mark.parametrize("code", [
    "AUTH_CHANNEL_CONFLICT", "AUTH_REQUIRED", "CREDENTIAL_INVALID", "ACTION_FORBIDDEN",
    "RESOURCE_UNAVAILABLE", "REQUEST_BODY_LIMIT_EXCEEDED", "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED",
    "REQUEST_HEADERS_LIMIT_EXCEEDED", "UNSUPPORTED_MEDIA_TYPE",
    "UNSUPPORTED_CONTENT_ENCODING", "REQUEST_STREAM_ERROR",
    "METHOD_NOT_ALLOWED", "INTERNAL_ERROR",
])
def test_pre_authorization_errors_reject_private_operation_ids(code):
    data = {**failed(), "error": PublicError.from_code(code)}
    assert FailedResponse.model_validate(data).operation_id is None
    assert FailedResponse.model_validate({**data, "operation_id": None}).operation_id is None
    with pytest.raises(ValidationError):
        FailedResponse.model_validate({**data, "operation_id": "private-op"})
    if code in {"AUTH_REQUIRED", "CREDENTIAL_INVALID", "ACTION_FORBIDDEN", "RESOURCE_UNAVAILABLE"}:
        with pytest.raises(ValidationError):
            PublicError.from_code(code, details=ErrorDetails(reason="unavailable"))
        with pytest.raises(ValidationError):
            OperationResponse.model_validate({
                **operation(), "status": "failed", "operation_state": "failed",
                "error": PublicError.from_code(code),
            })


def test_input_errors_do_not_expose_operation_ids():
    for code in [
        "VALIDATION_ERROR", "INPUT_LIMIT_EXCEEDED", "REQUEST_HEADERS_LIMIT_EXCEEDED",
        "UNSUPPORTED_MEDIA_TYPE", "UNSUPPORTED_CONTENT_ENCODING", "REQUEST_STREAM_ERROR",
        "METHOD_NOT_ALLOWED", "INTERNAL_ERROR",
    ]:
        with pytest.raises(ValidationError):
            FailedResponse.model_validate({
                **failed(), "error": PublicError.from_code(code), "operation_id": "private",
            })
        with pytest.raises(ValidationError):
            OperationResponse.model_validate({
                **operation(), "status": "failed", "operation_state": "failed",
                "error": PublicError.from_code(code),
            })


def test_absent_and_null_optional_fields_remain_distinguishable():
    absent = FailedResponse.model_validate(failed())
    explicit = FailedResponse.model_validate({**failed(), "operation_id": None})
    assert "operation_id" not in absent.model_dump(mode="json", exclude_unset=True)
    assert explicit.model_dump(mode="json", exclude_unset=True)["operation_id"] is None
    with pytest.raises(ValidationError):
        FailedResponse.model_validate({**failed(), "error": None})
    with pytest.raises(ValidationError):
        CompletedResponse.model_validate({**completed(), "facts": None})


@pytest.mark.parametrize("key,value", [
    ("excerpt", "\ud800"), ("end", 2), ("end", 0), ("start", -1), ("start", True),
    ("chunk_id", "c1/path"),
])
def test_evidence_span_and_id_negative(key, value):
    with pytest.raises(ValidationError):
        EvidenceBlock.model_validate({**evidence(), key: value})


def test_retrieval_flatness_five_block_bound_and_no_generation_operation():
    dto = RetrievalResponse.model_validate(retrieval())
    assert "retrieval" not in dto.model_dump()
    assert dto.retrieval_execution_id == "retr-1"
    assert len(RetrievalResponse.model_validate({
        **retrieval(), "evidence_catalog": [evidence(i) for i in range(5)],
    }).evidence_catalog) == 5
    for patch in [
        {"operation_id": "op-1"}, {"retrieval": retrieval()},
        {"evidence_catalog": [evidence(i) for i in range(6)]},
        {"evidence_catalog": [evidence(), evidence()]},
    ]:
        with pytest.raises(ValidationError):
            RetrievalResponse.model_validate({**retrieval(), **patch})


@pytest.mark.parametrize("patch", [
    {"completed_at": "2026-10-17T07:00:00Z"}, {"outcome": "succeeded"},
    {"status": "failed"}, {"facts": []}, {"evidence_catalog": []},
    {"summary": {"text": "x", "fact_ids": ["f2"]}},
    {"summary": {"text": "\ud800", "fact_ids": ["f1"]}},
    {"facts": [fact(), fact()]}, {"gaps": [{"field": "evidence", "text": "missing"}]},
])
def test_completed_response_consistency(patch):
    with pytest.raises(ValidationError):
        CompletedResponse.model_validate({**completed(), **patch})


@pytest.mark.parametrize("outcome", ["insufficient", "clarify", "conflict"])
def test_positive_business_outcomes_are_separate_from_http_status(outcome):
    data = completed()
    data["outcome"] = outcome
    if outcome == "insufficient":
        data.update(facts=[], summary={"text": "Not enough evidence.", "fact_ids": []},
                    gaps=[{"field": "evidence", "text": "Missing evidence."}])
    elif outcome == "clarify":
        data["clarifications"] = [{"field": "version", "text": "Which version?"}]
    else:
        data["facts"][0].update(evidence_ids=["e1", "e2"],
                                conflict_sides={"side_a": ["e1"], "side_b": ["e2"]})
        data["evidence_catalog"].append(evidence(2))
    assert CompletedResponse.model_validate(data).status == "completed"
    assert CompletedResponse.model_validate_json(stable_json_bytes(data)).outcome == outcome


def test_quantity_and_conflict_partitions_are_explicit():
    data = completed()
    data["facts"][0]["kind"] = "parameter"
    with pytest.raises(ValidationError):
        CompletedResponse.model_validate(data)
    data["facts"][0]["quantity"] = {"value_text": "5", "unit": "V"}
    CompletedResponse.model_validate(data)
    for sides in [
        {"side_a": ["e1"], "side_b": ["e1"]},
        {"side_a": ["e1"], "side_b": ["e2"]},
    ]:
        invalid = deepcopy(data)
        invalid["facts"][0]["conflict_sides"] = sides
        with pytest.raises(ValidationError):
            CompletedResponse.model_validate(invalid)


def test_models_are_exportable_and_nested_objects_forbid_unknown_fields():
    for name, model in PUBLIC_MODELS.items():
        assert name == model.__name__
        for mode in ("validation", "serialization"):
            schema = model.model_json_schema(mode=mode)
            assert schema["additionalProperties"] is False
            assert isinstance(stable_json_bytes(schema), bytes)
    schema = Money.model_json_schema()
    assert {"type": "string", "pattern": r"^\d+(?:\.\d+)?$"} in schema["properties"]["amount"]["anyOf"]
    data = completed()
    data["summary"]["body"] = "private"
    with pytest.raises(ValidationError):
        CompletedResponse.model_validate(data)
    assert "awaiting_reconciliation" in {state.value for state in JobState}


def test_public_enums_index_keeps_original_identity_and_wire_values():
    assert PUBLIC_ENUMS == {
        "Status": Status,
        "Outcome": Outcome,
        "OperationState": OperationState,
        "JobState": JobState,
        "RetryMode": RetryMode,
    }
    assert {name: enum.__name__ for name, enum in PUBLIC_ENUMS.items()} == {
        name: name for name in PUBLIC_ENUMS
    }
    assert {state.value for state in Status} == {
        "completed", "in_progress", "failed",
    }
    assert {result.value for result in Outcome} == {
        "answered", "insufficient", "clarify", "conflict",
    }
    assert {state.value for state in OperationState} == {
        "accepted", "running", "completed", "failed",
    }
    assert {state.value for state in JobState} == {
        "queued", "running", "awaiting_reconciliation",
        "succeeded", "failed", "cancelled", "expired",
    }
    assert {mode.value for mode in RetryMode} == {
        "none", "same_key_or_status", "new_operation", "manual_reconcile",
    }
    assert set(PUBLIC_ENUMS) & set(PUBLIC_MODELS) == set()
    # upload.v1 joins the same generated catalog; its five projections and
    # envelope are neither enums nor a second hand-written contract.
    assert len(PUBLIC_MODELS) == 27
    assert {"UploadResponse", "Candidate", "IndexGeneration"} <= set(PUBLIC_MODELS)


@pytest.mark.parametrize("name,enum", sorted(PUBLIC_ENUMS.items()))
def test_public_enums_export_validation_and_serialization_schemas(name, enum):
    adapter = TypeAdapter(enum)
    expected = [item.value for item in enum]
    assert set(PUBLIC_ENUMS[name]) == set(enum)
    for mode in ("validation", "serialization"):
        schema = adapter.json_schema(mode=mode)
        definitions = schema.get("$defs", {})
        target = definitions.get(name, schema)
        assert target["type"] == "string"
        assert target["enum"] == expected
        assert isinstance(stable_json_bytes(schema), bytes)
    for value in expected:
        assert adapter.validate_python(value) is enum(value)
        assert adapter.validate_json(stable_json_bytes(value)) is enum(value)
    for value in ["paused", "unknown", "", "RUNNING", 1, None]:
        if value in expected:
            continue
        with pytest.raises(ValidationError):
            adapter.validate_python(value)


def test_c2_state_meanings_are_indexed_separately():
    field_enums = {
        "status": "Status",
        "outcome": "Outcome",
        "operation_state": "OperationState",
        "job_state": "JobState",
    }
    wire = {
        "status": "in_progress",
        "outcome": "answered",
        "operation_state": "running",
        "job_state": "succeeded",
    }
    assert set(wire) == set(field_enums)
    assert set(field_enums.values()) <= set(PUBLIC_ENUMS)
    for field, enum_name in field_enums.items():
        enum = PUBLIC_ENUMS[enum_name]
        assert enum.__name__ == enum_name
        assert TypeAdapter(enum).validate_python(wire[field]).value == wire[field]
    assert "RetryMode" not in field_enums.values()
    assert TypeAdapter(PUBLIC_ENUMS["RetryMode"]).validate_python(
        "same_key_or_status",
    ).value == "same_key_or_status"
    with pytest.raises(ValidationError):
        TypeAdapter(Status).validate_python("succeeded")
    with pytest.raises(ValidationError):
        TypeAdapter(Outcome).validate_python("completed")
    with pytest.raises(ValidationError):
        TypeAdapter(JobState).validate_python("answered")
    with pytest.raises(ValidationError):
        TypeAdapter(RetryMode).validate_python("automatic")


def test_all_nested_wire_strings_reject_surrogates():
    for path in ["text", "applicability"]:
        data = completed()
        data["facts"][0][path] = "\udfff"
        with pytest.raises(ValidationError):
            CompletedResponse.model_validate(data)
    data = completed()
    data["facts"][0]["quantity"] = {"value_text": "\udfff", "unit": "V"}
    with pytest.raises(ValidationError):
        CompletedResponse.model_validate(data)
    with pytest.raises(ValidationError):
        AnswerPayload.model_validate({"outcome": "\ud800"})
