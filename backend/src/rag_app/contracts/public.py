"""Exportable C1/C2 DTOs; no business execution or authorization lives here."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .errors import MESSAGES
from .scalars import (
    FiniteDecimal, StableId, UtcDateTime, WireText, scalar_length,
    strict_json_loads, validate_wire_values,
)

NonnegativeInt = Annotated[int, Field(strict=True, ge=0)]
CapabilityVersion = Literal["answer.v1", "comparison.v1", "retrieval.v1", "operation.v1"]


class ContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=False, allow_inf_nan=False,
        frozen=True, revalidate_instances="always", hide_input_in_errors=True,
    )

    @model_validator(mode="before")
    @classmethod
    def check_wire_values(cls, value: Any) -> Any:
        return validate_wire_values(value)

    @classmethod
    def model_validate_json(cls, json_data: str | bytes | bytearray, **kwargs: Any):
        # Pydantic's JSON decoder accepts duplicate keys; reject before decoding.
        try:
            value = strict_json_loads(json_data)
        except (ValueError, UnicodeError):
            raise ValidationError.from_exception_data(cls.__name__, [{
                "type": "value_error", "loc": (), "input": None,
                "ctx": {"error": ValueError("invalid contract JSON")},
            }]) from None
        return cls.model_validate(value, **kwargs)


class Status(StrEnum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"


class Outcome(StrEnum):
    ANSWERED = "answered"
    INSUFFICIENT = "insufficient"
    CLARIFY = "clarify"
    CONFLICT = "conflict"


class OperationState(StrEnum):
    ACCEPTED = "accepted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_RECONCILIATION = "awaiting_reconciliation"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class RetryMode(StrEnum):
    NONE = "none"
    SAME_KEY_OR_STATUS = "same_key_or_status"
    NEW_OPERATION = "new_operation"
    MANUAL_RECONCILE = "manual_reconcile"


class Usage(ContractModel):
    input_tokens: NonnegativeInt | None
    output_tokens: NonnegativeInt | None
    unknown: bool = Field(strict=True)

    @model_validator(mode="after")
    def check_unknown(self) -> Usage:
        missing = self.input_tokens is None or self.output_tokens is None
        if self.unknown != missing:
            raise ValueError("unknown must identify missing usage")
        return self


class Money(ContractModel):
    amount: FiniteDecimal | None
    currency: Annotated[WireText, Field(pattern=r"^[A-Z]{3}$")] | None
    source: Literal["estimate", "bill", "unknown"]

    @model_validator(mode="after")
    def check_amount(self) -> Money:
        if self.source == "unknown":
            if self.amount is not None or self.currency is not None:
                raise ValueError("unknown money requires explicit null amount and currency")
        elif self.amount is None or self.currency is None:
            raise ValueError("known money requires an amount and currency")
        return self


# Finite public text, never messages copied from exceptions or provider bodies.
ERROR_POLICY: dict[str, tuple[str, int, RetryMode]] = {
    "AUTH_CHANNEL_CONFLICT": ("Conflicting authentication channels.", 400, RetryMode.NONE),
    "VALIDATION_ERROR": ("Invalid request.", 422, RetryMode.NONE),
    "AUTH_REQUIRED": ("Authentication required.", 401, RetryMode.NONE),
    "CREDENTIAL_INVALID": ("Invalid credentials.", 401, RetryMode.NONE),
    "ACTION_FORBIDDEN": ("Action unavailable.", 403, RetryMode.NONE),
    "RESOURCE_UNAVAILABLE": ("Resource unavailable.", 404, RetryMode.NONE),
    "METHOD_NOT_ALLOWED": ("Method not allowed.", 405, RetryMode.NONE),
    "INTERNAL_ERROR": ("Internal server error.", 500, RetryMode.NONE),
    "IDEMPOTENCY_CONFLICT": ("Idempotency key conflict.", 409, RetryMode.NONE),
    "OPERATION_EXPIRED": ("Operation expired.", 410, RetryMode.NEW_OPERATION),
    "REQUEST_BODY_LIMIT_EXCEEDED": ("Request body too large.", 413, RetryMode.NONE),
    "REQUEST_HEADERS_LIMIT_EXCEEDED": ("Request headers too large.", 431, RetryMode.NONE),
    "UNSUPPORTED_MEDIA_TYPE": ("Unsupported media type.", 415, RetryMode.NONE),
    "UNSUPPORTED_CONTENT_ENCODING": ("Unsupported content encoding.", 415, RetryMode.NONE),
    "REQUEST_STREAM_ERROR": ("Request stream unavailable.", 400, RetryMode.NONE),
    "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED": ("Invalid request structure.", 422, RetryMode.NONE),
    "INPUT_LIMIT_EXCEEDED": ("Input limit exceeded.", 422, RetryMode.NONE),
    "CONCURRENCY_LIMIT_EXCEEDED": ("Concurrency limit exceeded.", 429, RetryMode.SAME_KEY_OR_STATUS),
    "QUERY_RATE_LIMIT_EXCEEDED": ("Query rate limit exceeded.", 429, RetryMode.SAME_KEY_OR_STATUS),
    "DEPENDENCY_UNAVAILABLE": ("Dependency unavailable.", 502, RetryMode.NEW_OPERATION),
    "DEPENDENCY_TIMEOUT": ("Dependency timed out.", 504, RetryMode.NEW_OPERATION),
    "ANSWER_VALIDATION_FAILED": ("Answer validation failed.", 502, RetryMode.NEW_OPERATION),
    "ANSWER_TRUNCATED": ("Answer was truncated.", 502, RetryMode.NEW_OPERATION),
    "CONFIGURATION_INVALID": (MESSAGES["CONFIGURATION_INVALID"], 503, RetryMode.NONE),
    "DATABASE_VERSION_MISMATCH": (MESSAGES["DATABASE_VERSION_MISMATCH"], 503, RetryMode.NONE),
    "DATABASE_OPERATION_FAILED": (MESSAGES["DATABASE_OPERATION_FAILED"], 503, RetryMode.NONE),
    "DATABASE_CLEANUP_FAILED": (
        MESSAGES["DATABASE_CLEANUP_FAILED"], 503, RetryMode.MANUAL_RECONCILE,
    ),
    "ONLINE_VALIDATION_REQUIRED": (MESSAGES["ONLINE_VALIDATION_REQUIRED"], 503, RetryMode.NONE),
    "RUNTIME_VERSION_MISMATCH": (MESSAGES["RUNTIME_VERSION_MISMATCH"], 503, RetryMode.NONE),
    "DATABASE_REVISION_MISMATCH": (MESSAGES["DATABASE_REVISION_MISMATCH"], 503, RetryMode.NONE),
    "DATABASE_NAMESPACE_UNAVAILABLE": (
        MESSAGES["DATABASE_NAMESPACE_UNAVAILABLE"], 503, RetryMode.NONE,
    ),
    "STARTUP_DEPENDENCY_UNAVAILABLE": (
        MESSAGES["STARTUP_DEPENDENCY_UNAVAILABLE"], 503, RetryMode.NONE,
    ),
}
ErrorCode = Literal[
    "AUTH_CHANNEL_CONFLICT", "VALIDATION_ERROR", "AUTH_REQUIRED", "CREDENTIAL_INVALID",
    "ACTION_FORBIDDEN", "RESOURCE_UNAVAILABLE", "IDEMPOTENCY_CONFLICT",
    "OPERATION_EXPIRED", "REQUEST_BODY_LIMIT_EXCEEDED", "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED",
    "INPUT_LIMIT_EXCEEDED", "CONCURRENCY_LIMIT_EXCEEDED", "QUERY_RATE_LIMIT_EXCEEDED",
    "DEPENDENCY_UNAVAILABLE", "DEPENDENCY_TIMEOUT", "ANSWER_VALIDATION_FAILED",
    "ANSWER_TRUNCATED", "REQUEST_HEADERS_LIMIT_EXCEEDED", "UNSUPPORTED_MEDIA_TYPE",
    "UNSUPPORTED_CONTENT_ENCODING", "REQUEST_STREAM_ERROR",
    "CONFIGURATION_INVALID", "DATABASE_VERSION_MISMATCH", "DATABASE_OPERATION_FAILED",
    "DATABASE_CLEANUP_FAILED", "ONLINE_VALIDATION_REQUIRED", "RUNTIME_VERSION_MISMATCH",
    "DATABASE_REVISION_MISMATCH", "DATABASE_NAMESPACE_UNAVAILABLE",
    "STARTUP_DEPENDENCY_UNAVAILABLE", "METHOD_NOT_ALLOWED", "INTERNAL_ERROR",
]


class ErrorDetails(ContractModel):
    field: Literal["schema_version", "question", "operation_id", "targets", "body"] | None = None
    reason: Literal["invalid_format", "out_of_range", "unknown_field", "unavailable"] | None = None
    retry_after_seconds: Annotated[int, Field(strict=True, ge=0, le=86400)] | None = None


class PublicError(ContractModel):
    code: ErrorCode
    message: WireText
    http_status: Annotated[int, Field(strict=True, ge=400, le=599)]
    retry_mode: RetryMode
    details: ErrorDetails | None = None

    @model_validator(mode="after")
    def check_policy(self) -> PublicError:
        if (self.message, self.http_status, self.retry_mode) != ERROR_POLICY[self.code]:
            raise ValueError("error metadata must match the finite public policy")
        if self.code in {"AUTH_REQUIRED", "CREDENTIAL_INVALID", "ACTION_FORBIDDEN", "RESOURCE_UNAVAILABLE"} and self.details is not None:
            raise ValueError("identity and unavailable-target errors cannot expose details")
        return self

    @classmethod
    def from_code(cls, code: ErrorCode, *, details: ErrorDetails | None = None) -> PublicError:
        if code not in ERROR_POLICY:
            raise ValueError("unknown public error code")
        message, http_status, retry_mode = ERROR_POLICY[code]
        return cls(code=code, message=message, http_status=http_status,
                   retry_mode=retry_mode, details=details)


class EvidenceBlock(ContractModel):
    evidence_id: StableId
    chunk_id: StableId
    excerpt: Annotated[WireText, Field(min_length=1, max_length=4096)]
    start: NonnegativeInt
    end: Annotated[int, Field(strict=True, gt=0)]

    @model_validator(mode="after")
    def check_span(self) -> EvidenceBlock:
        if self.end - self.start != scalar_length(self.excerpt):
            raise ValueError("evidence span must match its Unicode scalar excerpt")
        return self


class RetrievalPayload(ContractModel):
    retrieval_execution_id: StableId
    deadline: UtcDateTime
    evidence_catalog: list[EvidenceBlock] = Field(max_length=5)

    @model_validator(mode="after")
    def check_catalog(self) -> RetrievalPayload:
        _unique([item.evidence_id for item in self.evidence_catalog])
        _unique([item.chunk_id for item in self.evidence_catalog])
        return self


def _unique(values: list[Any]) -> None:
    if len(values) != len(set(values)):
        raise ValueError("duplicate identifiers are not allowed")


class BaseResponse(ContractModel):
    schema_version: CapabilityVersion
    request_id: StableId
    status: Status


class AcceptedResponse(BaseResponse):
    schema_version: Literal["operation.v1"] = "operation.v1"
    status: Literal[Status.IN_PROGRESS] = Status.IN_PROGRESS
    operation_id: StableId
    operation_state: Literal[OperationState.ACCEPTED, OperationState.RUNNING]
    accepted_at: UtcDateTime
    status_url: Annotated[WireText, Field(pattern=r"^/operations/[A-Za-z0-9_-]{1,64}$")]
    retry_mode: Literal[RetryMode.SAME_KEY_OR_STATUS] = RetryMode.SAME_KEY_OR_STATUS

    @model_validator(mode="after")
    def check_status_url(self) -> AcceptedResponse:
        if self.status_url != f"/operations/{self.operation_id}":
            raise ValueError("status_url must point to this operation")
        return self


FactId = Annotated[WireText, Field(pattern=r"^f(?:[1-9]|1[0-6])$")]
FactKind = Literal[
    "process", "material", "condition", "owner", "cause", "check",
    "step", "parameter", "limitation",
]
GapField = Literal[
    "process", "material", "condition", "owner", "cause", "check",
    "step", "parameter", "limitation", "object_identity", "version",
    "environment", "log_context", "evidence", "source_locator",
]


class Summary(ContractModel):
    text: Annotated[WireText, Field(min_length=1, max_length=1024)]
    fact_ids: list[FactId] = Field(max_length=16)


class Quantity(ContractModel):
    value_text: Annotated[WireText, Field(min_length=1, max_length=64)]
    unit: Annotated[WireText, Field(min_length=1, max_length=32)]


class ConflictSides(ContractModel):
    side_a: list[StableId] = Field(min_length=1, max_length=5)
    side_b: list[StableId] = Field(min_length=1, max_length=5)


class Fact(ContractModel):
    id: FactId
    kind: FactKind
    order: Annotated[int, Field(strict=True, ge=1, le=16)]
    text: Annotated[WireText, Field(min_length=1, max_length=512)]
    applicability: Annotated[WireText, Field(max_length=256)]
    evidence_ids: list[StableId] = Field(min_length=1, max_length=5)
    quantity: Quantity | None
    conflict_sides: ConflictSides | None

    @model_validator(mode="after")
    def check_fact(self) -> Fact:
        _unique(self.evidence_ids)
        if self.kind == "parameter" and self.quantity is None:
            raise ValueError("parameter facts require a quantity")
        if self.conflict_sides is not None:
            a, b = self.conflict_sides.side_a, self.conflict_sides.side_b
            _unique(a)
            _unique(b)
            if set(a) & set(b) or set(a + b) != set(self.evidence_ids):
                raise ValueError("conflict sides must partition the fact evidence")
        return self


class Gap(ContractModel):
    field: GapField
    text: Annotated[WireText, Field(min_length=1, max_length=256)]


class AnswerPayload(ContractModel):
    outcome: Outcome
    summary: Summary
    facts: list[Fact] = Field(max_length=16)
    gaps: list[Gap] = Field(max_length=8)
    clarifications: list[Gap] = Field(max_length=4)

    @model_validator(mode="after")
    def check_answer(self) -> AnswerPayload:
        _unique([fact.id for fact in self.facts])
        _unique([(fact.kind, fact.order) for fact in self.facts])
        _unique(self.summary.fact_ids)
        ids = {fact.id for fact in self.facts}
        if not set(self.summary.fact_ids) <= ids:
            raise ValueError("summary references an unknown fact")
        conflicts = {fact.id for fact in self.facts if fact.conflict_sides is not None}
        if self.outcome is Outcome.ANSWERED:
            if not self.facts or not self.summary.fact_ids or self.gaps or self.clarifications or conflicts:
                raise ValueError("answered requires supported facts and no unresolved issues")
        if self.outcome is Outcome.INSUFFICIENT and not self.gaps:
            raise ValueError("insufficient requires an explicit gap")
        if self.outcome is Outcome.CLARIFY and not self.clarifications:
            raise ValueError("clarify requires an explicit question")
        if self.outcome is Outcome.CONFLICT and not conflicts & set(self.summary.fact_ids):
            raise ValueError("conflict requires a summary-referenced conflicting fact")
        return self


class CompletedResponse(BaseResponse, AnswerPayload):
    schema_version: Literal["answer.v1"] = "answer.v1"
    status: Literal[Status.COMPLETED] = Status.COMPLETED
    operation_id: StableId
    replayed: bool = Field(strict=True)
    accepted_at: UtcDateTime
    completed_at: UtcDateTime
    execution_snapshot_id: StableId
    evidence_catalog: list[EvidenceBlock] = Field(max_length=5)

    @model_validator(mode="after")
    def check_completion(self) -> CompletedResponse:
        if self.completed_at < self.accepted_at:
            raise ValueError("completed_at cannot precede accepted_at")
        _unique([item.evidence_id for item in self.evidence_catalog])
        _unique([item.chunk_id for item in self.evidence_catalog])
        known = {item.evidence_id for item in self.evidence_catalog}
        if any(not set(fact.evidence_ids) <= known for fact in self.facts):
            raise ValueError("facts may only reference the server evidence catalog")
        return self


class FailedResponse(BaseResponse):
    status: Literal[Status.FAILED] = Status.FAILED
    error: PublicError
    operation_id: StableId | None = None

    @model_validator(mode="after")
    def check_safe_id(self) -> FailedResponse:
        if self.error.code in {
            "AUTH_CHANNEL_CONFLICT", "AUTH_REQUIRED", "CREDENTIAL_INVALID",
            "ACTION_FORBIDDEN", "RESOURCE_UNAVAILABLE", "REQUEST_BODY_LIMIT_EXCEEDED",
            "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED", "VALIDATION_ERROR", "INPUT_LIMIT_EXCEEDED",
            "REQUEST_HEADERS_LIMIT_EXCEEDED", "UNSUPPORTED_MEDIA_TYPE",
            "UNSUPPORTED_CONTENT_ENCODING", "REQUEST_STREAM_ERROR",
            "METHOD_NOT_ALLOWED", "INTERNAL_ERROR",
        } and self.operation_id is not None:
            raise ValueError("pre-authorization errors cannot disclose private operation IDs")
        if self.schema_version == "retrieval.v1" and self.operation_id is not None:
            raise ValueError("retrieval does not create a generation operation")
        return self


class OperationResponse(BaseResponse):
    schema_version: Literal["operation.v1"] = "operation.v1"
    operation_id: StableId
    operation_state: OperationState
    error: PublicError | None

    @model_validator(mode="after")
    def check_state(self) -> OperationResponse:
        expected = {
            OperationState.ACCEPTED: Status.IN_PROGRESS,
            OperationState.RUNNING: Status.IN_PROGRESS,
            OperationState.COMPLETED: Status.COMPLETED,
            OperationState.FAILED: Status.FAILED,
        }[self.operation_state]
        if self.status != expected or (self.error is not None) != (self.operation_state is OperationState.FAILED):
            raise ValueError("status, operation_state and error must agree")
        if self.error is not None and self.error.code in {
            "AUTH_CHANNEL_CONFLICT", "AUTH_REQUIRED", "CREDENTIAL_INVALID",
            "ACTION_FORBIDDEN", "RESOURCE_UNAVAILABLE", "REQUEST_BODY_LIMIT_EXCEEDED",
            "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED", "VALIDATION_ERROR", "INPUT_LIMIT_EXCEEDED",
            "REQUEST_HEADERS_LIMIT_EXCEEDED", "UNSUPPORTED_MEDIA_TYPE",
            "UNSUPPORTED_CONTENT_ENCODING", "REQUEST_STREAM_ERROR",
            "METHOD_NOT_ALLOWED", "INTERNAL_ERROR",
        }:
            raise ValueError("use a safe failed response for authorization errors")
        return self


class RetrievalResponse(BaseResponse, RetrievalPayload):
    schema_version: Literal["retrieval.v1"] = "retrieval.v1"
    status: Literal[Status.COMPLETED] = Status.COMPLETED


PUBLIC_MODELS: dict[str, type[ContractModel]] = {
    model.__name__: model for model in (
        Usage, Money, ErrorDetails, PublicError, EvidenceBlock, RetrievalPayload,
        AcceptedResponse, Summary, Quantity, ConflictSides, Fact, Gap, AnswerPayload,
        CompletedResponse, FailedResponse, OperationResponse, RetrievalResponse,
    )
}
