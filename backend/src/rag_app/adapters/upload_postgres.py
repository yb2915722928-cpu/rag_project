"""PostgreSQL facts for the finite upload chain; never owns a transaction.

Lock order follows C4: account (SH) -> space control (SH) -> knowledge base
(SH/EX) -> candidate/business -> capacity.  Repositories never commit,
roll back or close the caller's session, and no filesystem or network call
ever happens while these statements run.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text

from rag_app.adapters.postgres import validate_schema, verify_namespace


_UPLOAD_FIELDS = (
    "u.upload_row_id", "u.upload_operation_id", "u.owner_account_id",
    "u.space_id", "u.knowledge_base_id", "u.document_id", "u.candidate_id",
    "u.document_version_id", "u.input_version", "u.input_digest", "u.filename",
    "u.title", "u.format", "u.declared_bytes", "u.client_sha256",
    "u.asset_prefix", "u.reserved_bytes", "u.created_at", "u.accepted_at",
    "u.upload_start_by", "u.upload_hard_deadline", "u.first_started_at",
    "u.last_progress_at", "u.state", "u.attempt", "u.claim_token_digest",
    "u.lease_until", "u.writer_owner", "u.original_sha256",
    "u.original_bytes", "u.completed_at",
)


class UploadConflict(Exception):
    """A conditional write lost a race; callers re-read instead of guessing."""


class CapacityConflict(Exception):
    """Capacity ledger would go negative or disagree with the accepted facts."""


def _quoted(schema: str) -> str:
    return '"' + validate_schema(schema).replace('"', '""') + '"'


def _table(schema: str, name: str) -> str:
    return f"{_quoted(schema)}.{name}"


class UploadRepository:
    def __init__(self, session: Any, *, schema: str) -> None:
        self._session = session
        self._schema = validate_schema(schema)

    def _ready(self) -> None:
        verify_namespace(self._session, self._schema)

    def current_time(self) -> datetime:
        return self._session.execute(text("SELECT clock_timestamp()")).scalar_one()

    # -- locks -----------------------------------------------------------

    def lock_account(self, account_id: str) -> dict[str, Any] | None:
        self._ready()
        row = self._session.execute(text(
            "SELECT a.account_id, a.state, a.verification, a.epoch "
            f"FROM {_table(self._schema, 'account')} AS a "
            "WHERE a.account_id = :account_id FOR SHARE"
        ), {"account_id": account_id}).one_or_none()
        if row is None:
            return None
        return {
            "account_id": row[0], "state": row[1],
            "verification": row[2], "epoch": row[3],
        }

    def lock_space(self, space_id: str) -> dict[str, Any] | None:
        row = self._session.execute(text(
            "SELECT s.space_id, s.state, s.epoch, s.used_bytes, "
            "s.reserved_bytes, s.limit_bytes, s.physical_used_bytes, "
            "s.physical_reserved_bytes, s.physical_budget_bytes "
            f"FROM {_table(self._schema, 'space_control')} AS s "
            "WHERE s.space_id = :space_id FOR SHARE"
        ), {"space_id": space_id}).one_or_none()
        if row is None:
            return None
        names = (
            "space_id", "state", "epoch", "used_bytes", "reserved_bytes",
            "limit_bytes", "physical_used_bytes", "physical_reserved_bytes",
            "physical_budget_bytes",
        )
        return {name: row[index] for index, name in enumerate(names)}

    def lock_knowledge_base(
        self, space_id: str, knowledge_base_id: str,
    ) -> dict[str, Any] | None:
        row = self._session.execute(text(
            "SELECT k.knowledge_base_id, k.space_id, k.state, k.guard, "
            "k.docset_revision, k.active_generation_id, k.embedding_profile_id "
            f"FROM {_table(self._schema, 'knowledge_base')} AS k "
            "WHERE k.space_id = :space_id "
            "AND k.knowledge_base_id = :kb_id FOR SHARE"
        ), {"space_id": space_id, "kb_id": knowledge_base_id}).one_or_none()
        if row is None:
            return None
        names = (
            "knowledge_base_id", "space_id", "state", "guard",
            "docset_revision", "active_generation_id", "embedding_profile_id",
        )
        return {name: row[index] for index, name in enumerate(names)}

    def is_maintainer(
        self, account_id: str, space_id: str, knowledge_base_id: str,
    ) -> bool:
        found = self._session.execute(text(
            "SELECT 1 FROM " + _table(self._schema, "kb_maintainer")
            + " AS m WHERE m.knowledge_base_id = :kb_id "
            "AND m.account_id = :account_id AND m.revoked_at IS NULL"
        ), {
            "account_id": account_id, "kb_id": knowledge_base_id,
        }).scalar_one_or_none()
        return found == 1

    # -- sessions --------------------------------------------------------

    def load_session(self, secret_digest: str) -> dict[str, Any] | None:
        row = self._session.execute(text(
            "SELECT s.session_id, s.account_id, s.space_id, s.csrf_digest, s.epoch, "
            "s.idle_expires_at, s.absolute_expires_at, s.revoked_at, "
            "a.state, a.verification, a.epoch "
            f"FROM {_table(self._schema, 'web_session')} AS s "
            f"JOIN {_table(self._schema, 'account')} AS a "
            "ON a.account_id = s.account_id "
            "WHERE s.secret_digest = :digest"
        ), {"digest": secret_digest}).one_or_none()
        if row is None:
            return None
        names = (
            "session_id", "account_id", "space_id", "csrf_digest", "epoch",
            "idle_expires_at", "absolute_expires_at", "revoked_at",
            "account_state", "verification", "account_epoch",
        )
        return {name: row[index] for index, name in enumerate(names)}

    def load_program_credential(self, secret_digest: str) -> dict[str, Any] | None:
        row = self._session.execute(text(
            "SELECT c.credential_id, c.account_id, c.space_id, c.epoch, "
            "c.expires_at, c.revoked_at, a.state, a.verification, a.epoch "
            f"FROM {_table(self._schema, 'program_credential')} AS c "
            f"JOIN {_table(self._schema, 'account')} AS a "
            "ON a.account_id = c.account_id "
            "WHERE c.secret_digest = :digest"
        ), {"digest": secret_digest}).one_or_none()
        if row is None:
            return None
        names = (
            "credential_id", "account_id", "space_id", "epoch", "expires_at",
            "revoked_at", "account_state", "verification", "account_epoch",
        )
        return {name: row[index] for index, name in enumerate(names)}

    def space_role(
        self, account_id: str, space_id: str,
    ) -> dict[str, Any] | None:
        row = self._session.execute(text(
            "SELECT m.role, m.revoked_at "
            f"FROM {_table(self._schema, 'space_member')} AS m "
            "WHERE m.space_id = :space_id AND m.account_id = :account_id"
        ), {"space_id": space_id, "account_id": account_id}).one_or_none()
        if row is None:
            return None
        return {"role": row[0], "revoked_at": row[1]}

    # -- upload intent ---------------------------------------------------

    def lock_upload_by_key(
        self, *, owner_account_id: str, space_id: str, knowledge_base_id: str,
        upload_operation_id: str,
    ) -> dict[str, Any] | None:
        row = self._session.execute(text(
            f"SELECT {', '.join(_UPLOAD_FIELDS)} "
            f"FROM {_table(self._schema, 'upload_operation')} AS u "
            "WHERE u.owner_account_id = :owner AND u.space_id = :space_id "
            "AND u.knowledge_base_id = :kb_id "
            "AND u.upload_operation_id = :operation_id FOR UPDATE"
        ), {
            "owner": owner_account_id, "space_id": space_id,
            "kb_id": knowledge_base_id, "operation_id": upload_operation_id,
        }).one_or_none()
        return None if row is None else _upload_record(row)

    def lock_upload_by_candidate(
        self, candidate_id: str,
    ) -> dict[str, Any] | None:
        row = self._session.execute(text(
            f"SELECT {', '.join(_UPLOAD_FIELDS)} "
            f"FROM {_table(self._schema, 'upload_operation')} AS u "
            f"JOIN {_table(self._schema, 'document_candidate')} AS c "
            "ON c.candidate_id = u.candidate_id "
            "WHERE c.candidate_id = :candidate_id FOR UPDATE OF u"
        ), {"candidate_id": candidate_id}).one_or_none()
        return None if row is None else _upload_record(row)

    def candidate_scope(self, candidate_id: str) -> dict[str, Any] | None:
        """Unlocked scope resolution used only to order the C4 lock set."""

        row = self._session.execute(text(
            "SELECT c.candidate_id, c.space_id, c.knowledge_base_id, "
            "c.document_id, u.owner_account_id "
            f"FROM {_table(self._schema, 'document_candidate')} AS c "
            f"JOIN {_table(self._schema, 'upload_operation')} AS u "
            "ON u.candidate_id = c.candidate_id "
            "WHERE c.candidate_id = :candidate_id"
        ), {"candidate_id": candidate_id}).one_or_none()
        if row is None:
            return None
        return {
            "candidate_id": row[0], "space_id": row[1],
            "knowledge_base_id": row[2], "document_id": row[3],
            "owner_account_id": row[4],
        }

    def candidate_row(self, candidate_id: str) -> dict[str, Any] | None:
        row = self._session.execute(text(
            "SELECT c.candidate_id, c.document_version_id, c.space_id, "
            "c.knowledge_base_id, c.upload_state, c.processing_state, "
            "c.upload_start_by, c.upload_hard_deadline, "
            "c.retained_original_bytes, c.updated_at "
            f"FROM {_table(self._schema, 'document_candidate')} AS c "
            "WHERE c.candidate_id = :candidate_id"
        ), {"candidate_id": candidate_id}).one_or_none()
        if row is None:
            return None
        names = (
            "candidate_id", "document_version_id", "space_id",
            "knowledge_base_id", "upload_state", "processing_state",
            "upload_start_by", "upload_hard_deadline",
            "retained_original_bytes", "updated_at",
        )
        return {name: row[index] for index, name in enumerate(names)}

    def job_row(self, candidate_id: str) -> dict[str, Any] | None:
        row = self._session.execute(text(
            "SELECT j.job_id, j.attempt, j.job_state, j.stage_code, "
            "j.hard_deadline, j.lease_until, j.created_at "
            f"FROM {_table(self._schema, 'processing_job')} AS j "
            "WHERE j.candidate_id = :candidate_id"
        ), {"candidate_id": candidate_id}).one_or_none()
        if row is None:
            return None
        names = (
            "job_id", "attempt", "job_state", "stage_code", "hard_deadline",
            "lease_until", "created_at",
        )
        return {name: row[index] for index, name in enumerate(names)}

    def version_row(self, document_version_id: str) -> dict[str, Any] | None:
        row = self._session.execute(text(
            "SELECT v.document_version_id, v.document_id, v.space_id, "
            "v.knowledge_base_id, v.format, v.original_sha256, "
            "v.original_bytes, v.asset_id, v.committed_at "
            f"FROM {_table(self._schema, 'document_version')} AS v "
            "WHERE v.document_version_id = :version_id"
        ), {"version_id": document_version_id}).one_or_none()
        if row is None:
            return None
        names = (
            "document_version_id", "document_id", "space_id",
            "knowledge_base_id", "format", "original_sha256",
            "original_bytes", "asset_id", "committed_at",
        )
        return {name: row[index] for index, name in enumerate(names)}

    def insert_intent(
        self, *, upload_row_id: str, upload_operation_id: str,
        owner_account_id: str, space_id: str, knowledge_base_id: str,
        document_id: str, candidate_id: str, document_version_id: str,
        input_version: str, input_digest: str, filename: str, title: str,
        format: str, declared_bytes: int, client_sha256: str | None,
        asset_prefix: str, reserved_bytes: int, accepted_at: datetime,
        upload_start_by: datetime, upload_hard_deadline: datetime,
    ) -> None:
        self._ready()
        self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'document')} ("
            "document_id, space_id, knowledge_base_id, title, created_at"
            ") VALUES (:document_id, :space_id, :kb_id, :title, :accepted_at)"
        ), {
            "document_id": document_id, "space_id": space_id,
            "kb_id": knowledge_base_id, "title": title,
            "accepted_at": accepted_at,
        })
        self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'upload_operation')} ("
            "upload_row_id, upload_operation_id, owner_account_id, space_id, "
            "knowledge_base_id, document_id, candidate_id, document_version_id, "
            "input_version, input_digest, filename, title, format, "
            "declared_bytes, client_sha256, asset_prefix, reserved_bytes, "
            "created_at, accepted_at, upload_start_by, upload_hard_deadline, "
            "state, attempt"
            ") VALUES ("
            ":row_id, :operation_id, :owner, :space_id, :kb_id, :document_id, "
            ":candidate_id, :version_id, :input_version, :input_digest, "
            ":filename, :title, :format, :declared_bytes, :client_sha256, "
            ":asset_prefix, :reserved_bytes, :accepted_at, :accepted_at, "
            ":start_by, :hard_deadline, 'awaiting_upload', 0)"
        ), {
            "row_id": upload_row_id, "operation_id": upload_operation_id,
            "owner": owner_account_id, "space_id": space_id,
            "kb_id": knowledge_base_id, "document_id": document_id,
            "candidate_id": candidate_id, "version_id": document_version_id,
            "input_version": input_version, "input_digest": input_digest,
            "filename": filename, "title": title, "format": format,
            "declared_bytes": declared_bytes, "client_sha256": client_sha256,
            "asset_prefix": asset_prefix, "reserved_bytes": reserved_bytes,
            "accepted_at": accepted_at, "start_by": upload_start_by,
            "hard_deadline": upload_hard_deadline,
        })
        self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'document_candidate')} ("
            "candidate_id, upload_row_id, document_id, document_version_id, "
            "space_id, knowledge_base_id, upload_state, processing_state, "
            "upload_start_by, upload_hard_deadline, retained_original_bytes, "
            "created_at, updated_at"
            ") VALUES ("
            ":candidate_id, :row_id, :document_id, :version_id, :space_id, "
            ":kb_id, 'awaiting_upload', NULL, :start_by, :hard_deadline, 0, "
            ":accepted_at, :accepted_at)"
        ), {
            "candidate_id": candidate_id, "row_id": upload_row_id,
            "document_id": document_id, "version_id": document_version_id,
            "space_id": space_id, "kb_id": knowledge_base_id,
            "start_by": upload_start_by, "hard_deadline": upload_hard_deadline,
            "accepted_at": accepted_at,
        })

    def reserve_capacity_once(
        self, *, space_id: str, reserved_bytes: int, reference_id: str,
        transition_id: str, now: datetime,
    ) -> bool:
        """One conditional effect: reserve -> used only after a real commit."""

        inserted = self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'capacity_transition')} ("
            "transition_id, space_id, operation, originals_bytes, "
            "physical_bytes, reference_id, created_at"
            ") VALUES (:transition_id, :space_id, 'reserve', :bytes, :bytes, "
            ":reference_id, :now) ON CONFLICT (reference_id, operation) "
            "DO NOTHING"
        ), {
            "transition_id": transition_id, "space_id": space_id,
            "bytes": reserved_bytes, "reference_id": reference_id, "now": now,
        })
        if inserted.rowcount != 1:
            raise CapacityConflict("capacity was already reserved")
        updated = self._session.execute(text(
            f"UPDATE {_table(self._schema, 'space_control')} SET "
            "reserved_bytes = reserved_bytes + :bytes, "
            "physical_reserved_bytes = physical_reserved_bytes + :bytes "
            "WHERE space_id = :space_id AND state = 'active' "
            "AND used_bytes + reserved_bytes + :bytes <= limit_bytes "
            "AND physical_used_bytes + physical_reserved_bytes + :bytes "
            "<= physical_budget_bytes"
        ), {"space_id": space_id, "bytes": reserved_bytes})
        if updated.rowcount != 1:
            raise UploadConflict("capacity is insufficient")
        return True

    def begin_attempt(
        self, *, upload_row_id: str, attempt: int, claim_token_digest: str,
        writer_owner: str, lease_until: datetime, now: datetime,
        hard_deadline: datetime,
    ) -> bool:
        """A new attempt fences the previous token and tightens the deadline."""

        result = self._session.execute(text(
            f"UPDATE {_table(self._schema, 'upload_operation')} SET "
            "state = 'uploading', attempt = :attempt, "
            "claim_token_digest = :digest, writer_owner = :writer, "
            "lease_until = :lease, first_started_at = COALESCE("
            "first_started_at, :now), last_progress_at = COALESCE("
            "last_progress_at, :now), "
            "upload_hard_deadline = LEAST(upload_hard_deadline, :tightened) "
            "WHERE upload_row_id = :row_id "
            "AND state IN ('awaiting_upload','uploading') "
            "AND upload_start_by > :now AND upload_hard_deadline > :now "
            "AND attempt = :previous"
        ), {
            "row_id": upload_row_id, "attempt": attempt,
            "digest": claim_token_digest, "writer": writer_owner,
            "lease": lease_until, "now": now, "tightened": hard_deadline,
            "previous": attempt - 1,
        })
        if result.rowcount != 1:
            return False
        self._session.execute(text(
            f"UPDATE {_table(self._schema, 'document_candidate')} SET "
            "upload_state = 'uploading', updated_at = :now "
            "WHERE upload_row_id = :row_id"
        ), {"row_id": upload_row_id, "now": now})
        return True

    def renew_lease(
        self, *, upload_row_id: str, attempt: int, claim_token_digest: str,
        lease_until: datetime, progress_at: datetime,
    ) -> bool:
        result = self._session.execute(text(
            f"UPDATE {_table(self._schema, 'upload_operation')} SET "
            "lease_until = :lease, last_progress_at = :progress "
            "WHERE upload_row_id = :row_id AND state = 'uploading' "
            "AND attempt = :attempt AND claim_token_digest = :digest "
            "AND upload_hard_deadline > :progress"
        ), {
            "row_id": upload_row_id, "attempt": attempt,
            "digest": claim_token_digest, "lease": lease_until,
            "progress": progress_at,
        })
        return result.rowcount == 1

    def clear_writer_lease(
        self, upload_row_id: str, *, attempt: int, claim_token_digest: str,
    ) -> None:
        """Never release bytes here; only an unproven writer's lease is dropped."""

        self._session.execute(text(
            f"UPDATE {_table(self._schema, 'upload_operation')} SET "
            "claim_token_digest = NULL, writer_owner = NULL, lease_until = NULL "
            "WHERE upload_row_id = :row_id AND state = 'uploading' "
            "AND attempt = :attempt AND claim_token_digest = :digest"
        ), {
            "row_id": upload_row_id, "attempt": attempt,
            "digest": claim_token_digest,
        })

    def expire_if_due(
        self, *, upload_row_id: str, now: datetime,
    ) -> bool:
        """Expiry wins only while no committed original exists."""

        result = self._session.execute(text(
            f"UPDATE {_table(self._schema, 'upload_operation')} SET "
            "state = 'expired', claim_token_digest = NULL, writer_owner = NULL, "
            "lease_until = NULL "
            "WHERE upload_row_id = :row_id "
            "AND state IN ('awaiting_upload','uploading') "
            "AND (upload_hard_deadline <= :now OR ("
            "first_started_at IS NULL AND upload_start_by <= :now))"
        ), {"row_id": upload_row_id, "now": now})
        if result.rowcount != 1:
            return False
        self._session.execute(text(
            f"UPDATE {_table(self._schema, 'document_candidate')} SET "
            "upload_state = 'expired', updated_at = :now "
            "WHERE upload_row_id = :row_id "
            "AND upload_state <> 'original_committed'"
        ), {"row_id": upload_row_id, "now": now})
        return True

    def insert_asset(
        self, *, asset_id: str, asset_prefix: str, relative_path: str,
        original_sha256: str, byte_size: int, owner_row_id: str,
        now: datetime,
    ) -> None:
        self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'source_asset')} ("
            "asset_id, asset_prefix, relative_path, original_sha256, "
            "byte_size, state, owner_row_id, created_at"
            ") VALUES (:asset_id, :prefix, :path, :sha, :size, 'committed', "
            ":owner, :now)"
        ), {
            "asset_id": asset_id, "prefix": asset_prefix,
            "path": relative_path, "sha": original_sha256, "size": byte_size,
            "owner": owner_row_id, "now": now,
        })

    def insert_version(
        self, *, document_version_id: str, document_id: str, space_id: str,
        knowledge_base_id: str, format: str, original_sha256: str,
        original_bytes: int, asset_id: str, now: datetime,
    ) -> None:
        self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'document_version')} ("
            "document_version_id, document_id, space_id, knowledge_base_id, "
            "format, original_sha256, original_bytes, asset_id, committed_at"
            ") VALUES (:version_id, :document_id, :space_id, :kb_id, :format, "
            ":sha, :size, :asset_id, :now)"
        ), {
            "version_id": document_version_id, "document_id": document_id,
            "space_id": space_id, "kb_id": knowledge_base_id,
            "format": format, "sha": original_sha256, "size": original_bytes,
            "asset_id": asset_id, "now": now,
        })

    def insert_job(
        self, *, job_id: str, candidate_id: str, document_id: str,
        document_version_id: str, space_id: str, knowledge_base_id: str,
        hard_deadline: datetime, now: datetime,
    ) -> None:
        self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'processing_job')} ("
            "job_id, candidate_id, document_id, document_version_id, space_id, "
            "knowledge_base_id, attempt, job_state, stage_code, hard_deadline, "
            "lease_until, created_at"
            ") VALUES (:job_id, :candidate_id, :document_id, :version_id, "
            ":space_id, :kb_id, 1, 'queued', 'parse', :deadline, NULL, :now)"
        ), {
            "job_id": job_id, "candidate_id": candidate_id,
            "document_id": document_id, "version_id": document_version_id,
            "space_id": space_id, "kb_id": knowledge_base_id,
            "deadline": hard_deadline, "now": now,
        })

    def commit_original(
        self, record: dict[str, Any], *, attempt: int,
        claim_token_digest: str, original_sha256: str, original_bytes: int,
        now: datetime,
    ) -> bool:
        """Fenced completion; the caller checks the attempt/token again."""

        result = self._session.execute(text(
            f"UPDATE {_table(self._schema, 'upload_operation')} SET "
            "state = 'original_committed', original_sha256 = :sha, "
            "original_bytes = :size, completed_at = :now, "
            "claim_token_digest = NULL, lease_until = NULL, writer_owner = NULL "
            "WHERE upload_row_id = :row_id AND state = 'uploading' "
            "AND attempt = :attempt AND claim_token_digest = :digest "
            "AND upload_hard_deadline > :now"
        ), {
            "row_id": record["upload_row_id"], "sha": original_sha256,
            "size": original_bytes, "now": now, "attempt": attempt,
            "digest": claim_token_digest,
        })
        if result.rowcount != 1:
            return False
        self._session.execute(text(
            f"UPDATE {_table(self._schema, 'document_candidate')} SET "
            "upload_state = 'original_committed', processing_state = 'queued', "
            "retained_original_bytes = :size, updated_at = :now "
            "WHERE candidate_id = :candidate_id"
        ), {
            "candidate_id": record["candidate_id"], "size": original_bytes,
            "now": now,
        })
        return True

    def transfer_reserved_to_used(
        self, *, space_id: str, original_bytes: int, transition_id: str,
        reference_id: str, now: datetime,
    ) -> None:
        inserted = self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'capacity_transition')} ("
            "transition_id, space_id, operation, originals_bytes, "
            "physical_bytes, reference_id, created_at"
            ") VALUES (:transition_id, :space_id, 'commit', :bytes, :bytes, "
            ":reference_id, :now) ON CONFLICT (reference_id, operation) "
            "DO NOTHING"
        ), {
            "transition_id": transition_id, "space_id": space_id,
            "bytes": original_bytes, "reference_id": reference_id, "now": now,
        })
        if inserted.rowcount != 1:
            raise CapacityConflict("capacity was already committed")
        updated = self._session.execute(text(
            f"UPDATE {_table(self._schema, 'space_control')} SET "
            "reserved_bytes = reserved_bytes - :reserved, "
            "used_bytes = used_bytes + :bytes, "
            "physical_reserved_bytes = physical_reserved_bytes - :reserved, "
            "physical_used_bytes = physical_used_bytes + :bytes "
            "WHERE space_id = :space_id AND reserved_bytes >= :reserved "
            "AND physical_reserved_bytes >= :reserved"
        ), {
            "space_id": space_id, "reserved": original_bytes,
            "bytes": original_bytes,
        })
        if updated.rowcount != 1:
            raise CapacityConflict("reserved capacity is missing")

    def release_capacity_once(
        self, *, space_id: str, originals_bytes: int, physical_bytes: int,
        reference_id: str, transition_id: str, now: datetime,
    ) -> None:
        inserted = self._session.execute(text(
            f"INSERT INTO {_table(self._schema, 'capacity_transition')} ("
            "transition_id, space_id, operation, originals_bytes, "
            "physical_bytes, reference_id, created_at"
            ") VALUES (:transition_id, :space_id, 'release', :originals, "
            ":physical, :reference_id, :now) ON CONFLICT (reference_id, "
            "operation) DO NOTHING"
        ), {
            "transition_id": transition_id, "space_id": space_id,
            "originals": originals_bytes, "physical": physical_bytes,
            "reference_id": reference_id, "now": now,
        })
        if inserted.rowcount != 1:
            return
        self._session.execute(text(
            f"UPDATE {_table(self._schema, 'space_control')} SET "
            "reserved_bytes = reserved_bytes - LEAST(reserved_bytes, :originals), "
            "used_bytes = used_bytes - LEAST(used_bytes, :originals), "
            "physical_reserved_bytes = physical_reserved_bytes - LEAST("
            "physical_reserved_bytes, :physical), "
            "physical_used_bytes = physical_used_bytes - LEAST("
            "physical_used_bytes, :physical) "
            "WHERE space_id = :space_id"
        ), {
            "space_id": space_id, "originals": originals_bytes,
            "physical": physical_bytes,
        })


def _upload_record(row: Any) -> dict[str, Any]:
    names = (
        "upload_row_id", "upload_operation_id", "owner_account_id", "space_id",
        "knowledge_base_id", "document_id", "candidate_id",
        "document_version_id", "input_version", "input_digest", "filename",
        "title", "format", "declared_bytes", "client_sha256", "asset_prefix",
        "reserved_bytes", "created_at", "accepted_at", "upload_start_by",
        "upload_hard_deadline", "first_started_at", "last_progress_at",
        "state", "attempt", "claim_token_digest", "lease_until",
        "writer_owner", "original_sha256", "original_bytes", "completed_at",
    )
    return {name: row[index] for index, name in enumerate(names)}
