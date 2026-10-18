"""Framework-free upload intent, deadline and idempotent-input rules.

This module owns the finite wire enums so the exportable contract and the
database checks have one source.  It performs no I/O: PostgreSQL, the local
filesystem and the supervised writer live in adapters.

Deadline facts are fixed at acceptance and are never refreshed by a retry,
heartbeat or zero-byte attempt:

* ``upload_start_by = accepted_at + start_window``
* ``upload_hard_deadline = accepted_at + start + total``
* on first start the hard deadline tightens to ``first_started + total``
  through a conditional ``LEAST(...)`` update, so it can only decrease.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import hashlib
import json
import re
import secrets
import uuid


UPLOAD_INPUT_VERSION = "upload-input.v1"
REPLAY_WINDOW = timedelta(hours=24)
KEY_FUTURE_SKEW = timedelta(minutes=5)
TOMBSTONE_RETENTION = timedelta(days=7)
JOB_ABSOLUTE_WINDOW = timedelta(hours=2)

MAX_FILENAME_SCALARS = 255
MAX_TITLE_SCALARS = 128
MAX_DOCUMENT_TITLE_SCALARS = 512
HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SAFE_PREFIX = re.compile(r"[a-z0-9]{1,96}\Z")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_STABLE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")


class UploadState(StrEnum):
    AWAITING_UPLOAD = "awaiting_upload"
    UPLOADING = "uploading"
    ORIGINAL_COMMITTED = "original_committed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ProcessingState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_RECONCILIATION = "awaiting_reconciliation"
    READY = "ready"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    DISCARDED = "discarded"


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_RECONCILIATION = "awaiting_reconciliation"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class UploadFormat(StrEnum):
    TXT = "txt"
    MARKDOWN = "markdown"


class DocumentAction(StrEnum):
    """C7 finite action set; only actions this unit can actually serve are sent."""

    VIEW_CURRENT = "view_current"
    VIEW_CANDIDATE = "view_candidate"
    VIEW_ORIGINAL = "view_original"
    VIEW_EXTRACTION = "view_extraction"
    VIEW_TASK = "view_task"
    VIEW_CLEANUP = "view_cleanup"
    REPLACE = "replace"
    RETRY = "retry"
    CANCEL = "cancel"
    ABANDON = "abandon"
    RECONCILE = "reconcile"
    LOCAL_CONTINUE = "local_continue"
    RESUBMIT_WITH_ACK = "resubmit_with_ack"
    DELETE = "delete"
    REBUILD_INDEX = "rebuild_index"
    CANCEL_REBUILD = "cancel_rebuild"


@dataclass(frozen=True, slots=True)
class UploadLimits:
    """Finite effective configuration; ``max_file_bytes == 0`` closes the door."""

    max_file_bytes: int = 0
    start_window_s: int = 15 * 60
    total_window_s: int = 30 * 60
    no_progress_s: int = 60
    lease_s: int = 60
    renew_s: int = 10
    chunk_bytes: int = 256 * 1024
    slot_wait_s: int = 5
    stop_grace_s: int = 15
    page_bytes: int = 0
    replay_verify_s: int = 120

    def __post_init__(self) -> None:
        bounds = {
            "max_file_bytes": (self.max_file_bytes, 0, 8 * 1024 * 1024 * 1024),
            "start_window_s": (self.start_window_s, 60, 24 * 60 * 60),
            "total_window_s": (self.total_window_s, 60, 24 * 60 * 60),
            "no_progress_s": (self.no_progress_s, 5, 600),
            "lease_s": (self.lease_s, 5, 900),
            "renew_s": (self.renew_s, 1, 300),
            "chunk_bytes": (self.chunk_bytes, 4 * 1024, 1024 * 1024),
            "slot_wait_s": (self.slot_wait_s, 0, 120),
            "stop_grace_s": (self.stop_grace_s, 1, 300),
            "page_bytes": (self.page_bytes, 0, 8 * 1024 * 1024 * 1024),
            "replay_verify_s": (self.replay_verify_s, 1, 600),
        }
        for name, (value, low, high) in bounds.items():
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} is outside its finite range")
        if self.renew_s >= self.lease_s:
            raise ValueError("renew interval must be shorter than the lease")
        if self.total_window_s < self.start_window_s:
            raise ValueError("total window must cover the start window")

    @property
    def configured(self) -> bool:
        return self.max_file_bytes > 0

    def acceptance_deadlines(
        self, accepted_at: datetime,
    ) -> tuple[datetime, datetime]:
        return (
            accepted_at + timedelta(seconds=self.start_window_s),
            accepted_at + timedelta(
                seconds=self.start_window_s + self.total_window_s,
            ),
        )


class LimitExceeded(ValueError):
    """Finite business limit with the exact public code to project."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class KeyExpired(ValueError):
    """A client key outside the finite 24h/5min acceptance window."""


class UploadInputError(ValueError):
    """Strict-schema rejection; mapped to VALIDATION_ERROR at the boundary."""


class CapacityUnavailable(Exception):
    """A conditional reservation saw used+reserved+new above the limit."""


class CapacityLedgerConflict(Exception):
    """The unique capacity transition or its expected counters disagree."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def require_aware(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be an aware datetime")
    return value


def scalar_count(value: str) -> int:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise UploadInputError("surrogate code points are not allowed")
    return len(value)


def validate_filename(value: object) -> str:
    if not isinstance(value, str):
        raise UploadInputError("filename must be text")
    if not 1 <= scalar_count(value) <= MAX_FILENAME_SCALARS:
        raise UploadInputError("filename length is outside 1..255")
    if _CONTROL.search(value):
        raise UploadInputError("filename must not contain control characters")
    if "/" in value or "\\" in value or value in {".", ".."}:
        raise UploadInputError("filename must not contain path segments")
    return value


def validate_title(value: object, *, filename: str) -> str:
    if value is None:
        candidate = filename
        if scalar_count(candidate) > MAX_TITLE_SCALARS:
            candidate = candidate[:MAX_TITLE_SCALARS]
    elif isinstance(value, str):
        candidate = value
    else:
        raise UploadInputError("title must be text or absent")
    if not 1 <= scalar_count(candidate) <= MAX_TITLE_SCALARS:
        raise UploadInputError("title length is outside 1..128")
    if not candidate.strip() or _CONTROL.search(candidate):
        raise UploadInputError("title must be non-blank without control characters")
    return candidate


def validate_format(value: object) -> str:
    if not isinstance(value, str):
        raise UploadInputError("format must be text")
    try:
        return UploadFormat(value).value
    except ValueError:
        raise UploadInputError("format must be txt or markdown") from None


def validate_declared_bytes(value: object, limits: UploadLimits) -> int:
    if type(value) is not int or value <= 0:
        raise UploadInputError("declared_bytes must be a positive integer")
    if not limits.configured:
        raise LimitExceeded("FILE_LIMIT_EXCEEDED")
    if value > limits.max_file_bytes:
        raise LimitExceeded("FILE_LIMIT_EXCEEDED")
    return value


def validate_sha256(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or HEX_SHA256.fullmatch(value) is None:
        raise UploadInputError("original_sha256 must be 64 lowercase hex characters")
    return value


def validate_stable_id(value: object, *, name: str) -> str:
    if not isinstance(value, str) or _STABLE_ID.fullmatch(value) is None:
        raise UploadInputError(f"{name} must be a 1..64 character stable ID")
    return value


def parse_uuidv7(value: object) -> tuple[str, datetime]:
    """Return the canonical dashed form and its embedded millisecond time."""

    if not isinstance(value, str) or not 32 <= len(value) <= 36:
        raise UploadInputError("upload_operation_id must be a UUIDv7")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        raise UploadInputError("upload_operation_id must be a UUIDv7") from None
    if parsed.version != 7 or parsed.variant != uuid.RFC_4122:
        raise UploadInputError("upload_operation_id must be a UUIDv7")
    try:
        # The leading 48 bits are Unix milliseconds, not seconds.
        milliseconds = parsed.int >> 80
        embedded = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(
            milliseconds=milliseconds,
        )
    except (OverflowError, ValueError):
        raise UploadInputError("upload_operation_id time is out of range") from None
    return str(parsed), embedded


def check_key_window(embedded: datetime, now: datetime) -> None:
    """First appearance is 24h past / 5min future; replay stays inside 24h."""

    require_aware(embedded, "embedded")
    require_aware(now, "now")
    if embedded > now + KEY_FUTURE_SKEW or embedded < now - REPLAY_WINDOW:
        raise KeyExpired("upload key is outside the acceptance window")


def canonical_upload_input(
    *, space_id: str, knowledge_base_id: str, filename: str, title: str,
    format: str, declared_bytes: int, original_sha256: str | None,
) -> dict[str, object]:
    # Original values are preserved verbatim: no trim, NFC or whitespace merge.
    return {
        "declared_bytes": declared_bytes,
        "filename": filename,
        "format": format,
        "input_version": UPLOAD_INPUT_VERSION,
        "knowledge_base_id": knowledge_base_id,
        "original_sha256": original_sha256,
        "space_id": space_id,
        "title": title,
    }


def input_digest(value: dict[str, object]) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def new_asset_prefix() -> str:
    """Server-generated and non-reusable; never derived from a display name."""

    return "u" + uuid.uuid4().hex


def validate_asset_prefix(value: object) -> str:
    if not isinstance(value, str) or _SAFE_PREFIX.fullmatch(value) is None:
        raise ValueError("asset prefix is invalid")
    return value


def new_claim_token() -> str:
    return secrets.token_urlsafe(48)


def claim_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_row_id(prefix: str) -> str:
    return prefix + uuid.uuid4().hex


def effective_hard_deadline(
    upload_hard_deadline: datetime, first_started_at: datetime | None,
    limits: UploadLimits,
) -> datetime:
    if first_started_at is None:
        return upload_hard_deadline
    return min(
        upload_hard_deadline,
        first_started_at + timedelta(seconds=limits.total_window_s),
    )


def is_expired(
    now: datetime, *, upload_start_by: datetime, hard_deadline: datetime,
    first_started_at: datetime | None,
) -> bool:
    if now >= hard_deadline:
        return True
    return first_started_at is None and now >= upload_start_by


def allow_actions_for(upload_state: str, job_state: str | None) -> list[str]:
    """Only actions with a real server route in this unit are advertised."""

    if upload_state == UploadState.ORIGINAL_COMMITTED.value:
        actions = [DocumentAction.VIEW_CANDIDATE.value]
        if job_state is not None:
            actions.append(DocumentAction.VIEW_TASK.value)
        return actions
    if upload_state in {
        UploadState.AWAITING_UPLOAD.value, UploadState.UPLOADING.value,
    }:
        return [DocumentAction.VIEW_CANDIDATE.value]
    return []


def candidate_projection(
    *, candidate_id: str, document_version_id: str, upload_state: str,
    processing_state: str | None, upload_start_by: datetime,
    upload_hard_deadline: datetime, retained_original_bytes: int,
    updated_at: datetime,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "document_version_id": document_version_id,
        "upload_state": upload_state,
        "processing_state": processing_state,
        "upload_start_by": upload_start_by,
        "upload_hard_deadline": upload_hard_deadline,
        "retained_original_bytes": retained_original_bytes,
        "incomplete_ranges": [],
        "updated_at": updated_at,
    }


def job_projection(
    *, job_id: str, attempt: int, job_state: str, stage_code: str,
    hard_deadline: datetime, lease_until: datetime | None, updated_at: datetime,
) -> dict[str, object]:
    return {
        "job_id": job_id,
        "attempt": attempt,
        "job_state": job_state,
        "stage_code": stage_code,
        "hard_deadline": hard_deadline,
        "lease_until": lease_until,
        "progress": None,
        "updated_at": updated_at,
    }


def index_generation_projection() -> dict[str, object]:
    """An empty library has no active generation and no chosen profile."""

    return {
        "active_generation_id": None,
        "embedding_profile_id": None,
        "docset_revision": 0,
        "rebuild": None,
    }


UPLOAD_STATES = tuple(item.value for item in UploadState)
PROCESSING_STATES = tuple(item.value for item in ProcessingState)
JOB_STATES = tuple(item.value for item in JobState)
UPLOAD_FORMATS = tuple(item.value for item in UploadFormat)
DOCUMENT_ACTIONS = tuple(item.value for item in DocumentAction)
