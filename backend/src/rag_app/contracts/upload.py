"""Exportable upload.v1 DTOs; C2 envelope plus the five C7 projections."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .public import ContractModel, NonnegativeInt
from .scalars import StableId, UtcDateTime, WireText


UploadState = Literal[
    "awaiting_upload", "uploading", "original_committed", "expired", "cancelled",
]
ProcessingState = Literal[
    "queued", "running", "awaiting_reconciliation", "ready", "partial",
    "failed", "cancelled", "expired", "discarded",
]
JobState = Literal[
    "queued", "running", "awaiting_reconciliation", "succeeded", "failed",
    "cancelled", "expired",
]
CleanupState = Literal["cleanup_pending", "cleanup_blocked", "cleaned"]
DocumentAction = Literal[
    "view_current", "view_candidate", "view_original", "view_extraction",
    "view_task", "view_cleanup", "replace", "retry", "cancel", "abandon",
    "reconcile", "local_continue", "resubmit_with_ack", "delete",
    "rebuild_index", "cancel_rebuild",
]
UploadFormat = Literal["txt", "markdown"]


class IncompleteRange(ContractModel):
    kind: Literal["pdf", "structured"]
    start: NonnegativeInt
    end: Annotated[int, Field(strict=True, gt=0)]
    reason: Annotated[WireText, Field(min_length=1, max_length=128)]

    @model_validator(mode="after")
    def check_span(self) -> IncompleteRange:
        if self.end <= self.start:
            raise ValueError("incomplete range must be a nonempty half-open span")
        return self


class ActiveVersion(ContractModel):
    document_version_id: StableId
    availability: Literal["ready", "partial"]
    original_sha256: Annotated[WireText, Field(pattern=r"^[0-9a-f]{64}$")]
    published_at: UtcDateTime
    incomplete_ranges: list[IncompleteRange] = Field(max_length=100)


class Candidate(ContractModel):
    candidate_id: StableId
    document_version_id: StableId
    upload_state: UploadState
    processing_state: ProcessingState | None
    upload_start_by: UtcDateTime
    upload_hard_deadline: UtcDateTime
    retained_original_bytes: NonnegativeInt
    incomplete_ranges: list[IncompleteRange] = Field(max_length=100)
    updated_at: UtcDateTime

    @model_validator(mode="after")
    def check_deadlines(self) -> Candidate:
        if self.upload_start_by > self.upload_hard_deadline:
            raise ValueError("upload_start_by cannot follow the hard deadline")
        return self


class Progress(ContractModel):
    completed: NonnegativeInt
    total: Annotated[int, Field(strict=True, gt=0)]
    unit: Annotated[WireText, Field(min_length=1, max_length=32)]

    @model_validator(mode="after")
    def check_bounds(self) -> Progress:
        if self.completed > self.total:
            raise ValueError("progress cannot exceed its total")
        return self


class Job(ContractModel):
    job_id: StableId
    attempt: Annotated[int, Field(strict=True, ge=1)]
    job_state: JobState
    stage_code: Annotated[WireText, Field(min_length=1, max_length=64)]
    hard_deadline: UtcDateTime
    lease_until: UtcDateTime | None
    progress: Progress | None
    updated_at: UtcDateTime

    @model_validator(mode="after")
    def check_lease(self) -> Job:
        if self.lease_until is not None and self.lease_until > self.hard_deadline:
            raise ValueError("job lease cannot exceed the hard deadline")
        return self


class Rebuild(ContractModel):
    job_id: StableId
    candidate_generation_id: StableId
    target_profile_id: StableId
    state: JobState


class IndexGeneration(ContractModel):
    active_generation_id: StableId | None
    embedding_profile_id: StableId | None
    docset_revision: NonnegativeInt
    rebuild: Rebuild | None

    @model_validator(mode="after")
    def check_profile(self) -> IndexGeneration:
        if self.active_generation_id is not None and self.embedding_profile_id is None:
            raise ValueError("an active generation requires an immutable profile")
        return self


class Cleanup(ContractModel):
    asset_owner_id: StableId
    cleanup_state: CleanupState
    charged_original_bytes: NonnegativeInt
    retryable: bool = Field(strict=True)


class OriginalLocation(ContractModel):
    relative_path: Annotated[WireText, Field(pattern=r"^assets/[a-z0-9/]+$")]


class UploadResponse(ContractModel):
    """POST 201/200 and PUT 200 share one flat upload.v1 envelope."""

    schema_version: Literal["upload.v1"] = "upload.v1"
    request_id: StableId
    status: Literal["in_progress", "completed"]
    replayed: bool = Field(strict=True)
    upload_operation_id: StableId
    document_id: StableId
    accepted_at: UtcDateTime
    original_sha256: Annotated[WireText, Field(pattern=r"^[0-9a-f]{64}$")] | None
    original_bytes: NonnegativeInt | None
    original_url: Annotated[
        WireText,
        Field(pattern=r"^/api/v1/web/document-candidates/[A-Za-z0-9_-]{1,64}/original$"),
    ]
    active_version: ActiveVersion | None
    candidate: Candidate
    job: Job | None
    index_generation: IndexGeneration
    cleanup: Cleanup | None
    allowed_actions: list[DocumentAction] = Field(max_length=16)

    @model_validator(mode="after")
    def check_projection(self) -> UploadResponse:
        if self.original_url != (
            f"/api/v1/web/document-candidates/{self.candidate.candidate_id}/original"
        ):
            raise ValueError("original_url must address this candidate")
        if len(set(self.allowed_actions)) != len(self.allowed_actions):
            raise ValueError("allowed_actions must be unique")
        if self.candidate.upload_state == "original_committed":
            if self.status != "completed":
                raise ValueError("a committed original is completed, never ready")
            if self.original_sha256 is None or self.original_bytes is None:
                raise ValueError("a committed original reports its actual facts")
            if self.active_version is not None:
                raise ValueError("upload completion cannot publish an active version")
        else:
            if self.original_sha256 is not None or self.original_bytes is not None:
                raise ValueError("an uncommitted candidate has no original facts")
            if self.job is not None:
                raise ValueError("an uncommitted candidate has no processing job")
            if self.status != "in_progress":
                raise ValueError("an uncommitted candidate stays in progress")
        return self


UPLOAD_MODELS: dict[str, type[ContractModel]] = {
    model.__name__: model for model in (
        IncompleteRange, ActiveVersion, Candidate, Progress, Job, Rebuild,
        IndexGeneration, Cleanup, OriginalLocation, UploadResponse,
    )
}
