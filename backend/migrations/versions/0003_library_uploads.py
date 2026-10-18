"""Add the finite library upload chain: identity rows, candidates, assets, jobs.

The physical file is never part of a database transaction.  These tables only
hold the bounded business facts needed to fence a writer, reserve capacity once
and register an immutable original after the file has been fsynced and hashed
outside PostgreSQL.
"""

from alembic import op
import sqlalchemy as sa

from rag_app.adapters.postgres import (
    application_schema, validate_schema, verify_namespace, verify_versions,
)

revision = "0003_library_uploads"
down_revision = "0002_isolated_calls"
branch_labels = None
depends_on = None


def _schema() -> str:
    schema = str(op.get_context().opts.get("version_table_schema", ""))
    validate_schema(schema)
    return schema


def upgrade() -> None:
    verify_versions(op.get_bind(), allow_missing_extension=True)
    schema = application_schema(_schema())
    verify_namespace(op.get_bind(), schema)

    op.create_table(
        "account",
        sa.Column("account_id", sa.String(length=64), primary_key=True),
        sa.Column("state", sa.String(length=16), nullable=False,
                  server_default="active"),
        sa.Column("verification", sa.String(length=16), nullable=False,
                  server_default="verified"),
        sa.Column("epoch", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "state IN ('active','disabled')", name="ck_account_state",
        ),
        sa.CheckConstraint(
            "verification IN ('verified','unverified')",
            name="ck_account_verification",
        ),
        schema=schema,
    )
    op.create_table(
        "web_session",
        sa.Column("session_id", sa.String(length=64), primary_key=True),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("space_id", sa.String(length=64)),
        sa.Column("secret_digest", sa.String(length=64), nullable=False, unique=True),
        sa.Column("csrf_digest", sa.String(length=64), nullable=False),
        sa.Column("epoch", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "idle_expires_at <= absolute_expires_at",
            name="ck_web_session_idle_within_absolute",
        ),
        sa.CheckConstraint(
            "absolute_expires_at > created_at",
            name="ck_web_session_absolute_after_creation",
        ),
        schema=schema,
    )
    op.create_table(
        "program_credential",
        sa.Column("credential_id", sa.String(length=64), primary_key=True),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("secret_digest", sa.String(length=64), nullable=False, unique=True),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("epoch", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        schema=schema,
    )
    op.create_table(
        "space_control",
        sa.Column("space_id", sa.String(length=64), primary_key=True),
        sa.Column("state", sa.String(length=16), nullable=False,
                  server_default="active"),
        sa.Column("epoch", sa.String(length=64), nullable=False),
        sa.Column("used_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("reserved_bytes", sa.BigInteger(), nullable=False,
                  server_default="0"),
        sa.Column("limit_bytes", sa.BigInteger(), nullable=False),
        sa.Column("physical_used_bytes", sa.BigInteger(), nullable=False,
                  server_default="0"),
        sa.Column("physical_reserved_bytes", sa.BigInteger(), nullable=False,
                  server_default="0"),
        sa.Column("physical_budget_bytes", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "state IN ('active','quarantined')", name="ck_space_control_state",
        ),
        sa.CheckConstraint(
            "used_bytes >= 0 AND reserved_bytes >= 0 AND limit_bytes >= 0 "
            "AND physical_used_bytes >= 0 AND physical_reserved_bytes >= 0 "
            "AND physical_budget_bytes >= 0",
            name="ck_space_control_nonnegative",
        ),
        # A lowered limit may legitimately sit below already-used/reserved
        # bytes.  Only new reservations are refused by a conditional UPDATE;
        # a table CHECK here would make the required reduction impossible.
        schema=schema,
    )
    op.create_table(
        "knowledge_base",
        sa.Column("knowledge_base_id", sa.String(length=64), primary_key=True),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False,
                  server_default="active"),
        sa.Column("guard", sa.String(length=24), nullable=False,
                  server_default="idle"),
        sa.Column("docset_revision", sa.BigInteger(), nullable=False,
                  server_default="0"),
        sa.Column("active_generation_id", sa.String(length=64)),
        sa.Column("embedding_profile_id", sa.String(length=64)),
        sa.CheckConstraint(
            "state IN ('active','deleting','deleted')",
            name="ck_knowledge_base_state",
        ),
        sa.CheckConstraint(
            "guard IN ('idle','write_in_progress')",
            name="ck_knowledge_base_guard",
        ),
        sa.CheckConstraint(
            "docset_revision >= 0", name="ck_knowledge_base_revision",
        ),
        sa.UniqueConstraint(
            "space_id", "knowledge_base_id", name="uq_kb_space_identity",
        ),
        schema=schema,
    )
    op.create_table(
        "kb_maintainer",
        sa.Column("knowledge_base_id", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint(
            "knowledge_base_id", "account_id", name="pk_kb_maintainer",
        ),
        schema=schema,
    )
    op.create_table(
        "space_member",
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("space_id", "account_id", name="pk_space_member"),
        sa.CheckConstraint(
            "role IN ('owner','maintainer','reader')", name="ck_space_member_role",
        ),
        schema=schema,
    )
    op.create_table(
        "document",
        sa.Column("document_id", sa.String(length=64), primary_key=True),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("knowledge_base_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        schema=schema,
    )
    op.create_table(
        "upload_operation",
        sa.Column("upload_row_id", sa.String(length=64), primary_key=True),
        sa.Column("upload_operation_id", sa.String(length=64), nullable=False),
        sa.Column("owner_account_id", sa.String(length=64), nullable=False),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("knowledge_base_id", sa.String(length=64), nullable=False),
        sa.Column("document_id", sa.String(length=64), nullable=False),
        sa.Column("candidate_id", sa.String(length=64), nullable=False),
        sa.Column("document_version_id", sa.String(length=64), nullable=False),
        sa.Column("input_version", sa.String(length=32), nullable=False),
        sa.Column("input_digest", sa.String(length=64), nullable=False),
        sa.Column("filename", sa.String(length=1024), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("format", sa.String(length=16), nullable=False),
        sa.Column("declared_bytes", sa.BigInteger(), nullable=False),
        sa.Column("client_sha256", sa.String(length=64)),
        sa.Column("asset_prefix", sa.String(length=96), nullable=False, unique=True),
        sa.Column("reserved_bytes", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("upload_start_by", sa.DateTime(timezone=True), nullable=False),
        sa.Column("upload_hard_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_started_at", sa.DateTime(timezone=True)),
        sa.Column("last_progress_at", sa.DateTime(timezone=True)),
        sa.Column("state", sa.String(length=24), nullable=False,
                  server_default="awaiting_upload"),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("claim_token_digest", sa.String(length=64)),
        sa.Column("lease_until", sa.DateTime(timezone=True)),
        sa.Column("writer_owner", sa.String(length=64)),
        sa.Column("original_sha256", sa.String(length=64)),
        sa.Column("original_bytes", sa.BigInteger()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "format IN ('txt','markdown')", name="ck_upload_operation_format",
        ),
        sa.CheckConstraint(
            "state IN ('awaiting_upload','uploading','original_committed',"
            "'expired','cancelled')",
            name="ck_upload_operation_state",
        ),
        sa.CheckConstraint(
            "declared_bytes > 0 AND reserved_bytes > 0",
            name="ck_upload_operation_positive_bytes",
        ),
        sa.CheckConstraint(
            "attempt >= 0", name="ck_upload_operation_attempt",
        ),
        sa.CheckConstraint(
            "upload_start_by <= upload_hard_deadline",
            name="ck_upload_operation_deadline_order",
        ),
        sa.CheckConstraint(
            "(state <> 'original_committed') OR "
            "(original_sha256 IS NOT NULL AND original_bytes > 0 "
            "AND completed_at IS NOT NULL)",
            name="ck_upload_operation_committed_shape",
        ),
        sa.CheckConstraint(
            "(client_sha256 IS NULL) OR "
            "client_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_upload_operation_client_sha",
        ),
        sa.UniqueConstraint(
            "owner_account_id", "space_id", "knowledge_base_id",
            "upload_operation_id", name="uq_upload_operation_scope_key",
        ),
        schema=schema,
    )
    op.create_table(
        "document_candidate",
        sa.Column("candidate_id", sa.String(length=64), primary_key=True),
        sa.Column("upload_row_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("document_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("document_version_id", sa.String(length=64), nullable=False,
                  unique=True),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("knowledge_base_id", sa.String(length=64), nullable=False),
        sa.Column("upload_state", sa.String(length=24), nullable=False),
        sa.Column("processing_state", sa.String(length=24)),
        sa.Column("upload_start_by", sa.DateTime(timezone=True), nullable=False),
        sa.Column("upload_hard_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retained_original_bytes", sa.BigInteger(), nullable=False,
                  server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "upload_state IN ('awaiting_upload','uploading',"
            "'original_committed','expired','cancelled')",
            name="ck_candidate_upload_state",
        ),
        sa.CheckConstraint(
            "processing_state IS NULL OR processing_state IN ("
            "'queued','running','awaiting_reconciliation','ready','partial',"
            "'failed','cancelled','expired','discarded')",
            name="ck_candidate_processing_state",
        ),
        sa.CheckConstraint(
            "retained_original_bytes >= 0", name="ck_candidate_retained_bytes",
        ),
        schema=schema,
    )
    op.create_table(
        "document_version",
        sa.Column("document_version_id", sa.String(length=64), primary_key=True),
        sa.Column("document_id", sa.String(length=64), nullable=False),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("knowledge_base_id", sa.String(length=64), nullable=False),
        sa.Column("format", sa.String(length=16), nullable=False),
        sa.Column("original_sha256", sa.String(length=64), nullable=False),
        sa.Column("original_bytes", sa.BigInteger(), nullable=False),
        sa.Column("asset_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "format IN ('txt','markdown')", name="ck_document_version_format",
        ),
        sa.CheckConstraint(
            "original_bytes > 0", name="ck_document_version_positive_bytes",
        ),
        schema=schema,
    )
    op.create_table(
        "source_asset",
        sa.Column("asset_id", sa.String(length=64), primary_key=True),
        sa.Column("asset_prefix", sa.String(length=96), nullable=False, unique=True),
        sa.Column("relative_path", sa.String(length=256), nullable=False),
        sa.Column("original_sha256", sa.String(length=64), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False),
        sa.Column("owner_row_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "state IN ('writing','committed','orphan')",
            name="ck_source_asset_state",
        ),
        sa.CheckConstraint("byte_size > 0", name="ck_source_asset_positive_bytes"),
        schema=schema,
    )
    op.create_table(
        "processing_job",
        sa.Column("job_id", sa.String(length=64), primary_key=True),
        sa.Column("candidate_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("document_id", sa.String(length=64), nullable=False),
        sa.Column("document_version_id", sa.String(length=64), nullable=False),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("knowledge_base_id", sa.String(length=64), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("job_state", sa.String(length=24), nullable=False),
        sa.Column("stage_code", sa.String(length=24), nullable=False),
        sa.Column("hard_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "job_state IN ('queued','running','awaiting_reconciliation',"
            "'succeeded','failed','cancelled','expired')",
            name="ck_processing_job_state",
        ),
        sa.CheckConstraint("stage_code = 'parse'", name="ck_processing_job_stage"),
        sa.CheckConstraint("attempt > 0", name="ck_processing_job_attempt"),
        schema=schema,
    )
    op.create_table(
        "capacity_transition",
        sa.Column("transition_id", sa.String(length=64), primary_key=True),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("operation", sa.String(length=16), nullable=False),
        sa.Column("originals_bytes", sa.BigInteger(), nullable=False),
        sa.Column("physical_bytes", sa.BigInteger(), nullable=False),
        sa.Column("reference_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "operation IN ('reserve','commit','release')",
            name="ck_capacity_transition_operation",
        ),
        sa.CheckConstraint(
            "originals_bytes >= 0 AND physical_bytes >= 0",
            name="ck_capacity_transition_nonnegative",
        ),
        sa.UniqueConstraint(
            "reference_id", "operation", name="uq_capacity_transition_once",
        ),
        schema=schema,
    )

    owner = _schema()
    for statement in (
        "ALTER TABLE {s}.web_session ADD CONSTRAINT fk_web_session_account "
        "FOREIGN KEY (account_id) REFERENCES {s}.account(account_id) "
        "ON DELETE RESTRICT",
        "ALTER TABLE {s}.program_credential ADD CONSTRAINT "
        "fk_program_credential_account FOREIGN KEY (account_id) "
        "REFERENCES {s}.account(account_id) ON DELETE RESTRICT",
        "ALTER TABLE {s}.kb_maintainer ADD CONSTRAINT fk_kb_maintainer_kb "
        "FOREIGN KEY (knowledge_base_id) "
        "REFERENCES {s}.knowledge_base(knowledge_base_id) ON DELETE RESTRICT",
        "ALTER TABLE {s}.kb_maintainer ADD CONSTRAINT fk_kb_maintainer_account "
        "FOREIGN KEY (account_id) REFERENCES {s}.account(account_id) "
        "ON DELETE RESTRICT",
        "ALTER TABLE {s}.space_member ADD CONSTRAINT fk_space_member_space "
        "FOREIGN KEY (space_id) REFERENCES {s}.space_control(space_id) "
        "ON DELETE RESTRICT",
        "ALTER TABLE {s}.space_member ADD CONSTRAINT fk_space_member_account "
        "FOREIGN KEY (account_id) REFERENCES {s}.account(account_id) "
        "ON DELETE RESTRICT",
        "ALTER TABLE {s}.document ADD CONSTRAINT fk_document_kb "
        "FOREIGN KEY (space_id, knowledge_base_id) "
        "REFERENCES {s}.knowledge_base(space_id, knowledge_base_id) "
        "ON DELETE RESTRICT",
        "ALTER TABLE {s}.upload_operation ADD CONSTRAINT fk_upload_operation_doc "
        "FOREIGN KEY (document_id) REFERENCES {s}.document(document_id) "
        "ON DELETE RESTRICT",
        "ALTER TABLE {s}.upload_operation ADD CONSTRAINT "
        "fk_upload_operation_candidate FOREIGN KEY (candidate_id) "
        "REFERENCES {s}.document_candidate(candidate_id) ON DELETE RESTRICT "
        "DEFERRABLE INITIALLY DEFERRED",
        "ALTER TABLE {s}.document_candidate ADD CONSTRAINT "
        "fk_candidate_upload FOREIGN KEY (upload_row_id) "
        "REFERENCES {s}.upload_operation(upload_row_id) ON DELETE RESTRICT "
        "DEFERRABLE INITIALLY DEFERRED",
        "ALTER TABLE {s}.document_version ADD CONSTRAINT fk_version_document "
        "FOREIGN KEY (document_id) REFERENCES {s}.document(document_id) "
        "ON DELETE RESTRICT",
        "ALTER TABLE {s}.processing_job ADD CONSTRAINT fk_job_candidate "
        "FOREIGN KEY (candidate_id) "
        "REFERENCES {s}.document_candidate(candidate_id) ON DELETE RESTRICT",
        "ALTER TABLE {s}.processing_job ADD CONSTRAINT fk_job_version "
        "FOREIGN KEY (document_version_id) "
        "REFERENCES {s}.document_version(document_version_id) "
        "ON DELETE RESTRICT",
    ):
        op.execute(statement.format(s=f'"{owner}"'))

    op.create_index(
        "ix_candidate_scope", "document_candidate",
        ["space_id", "knowledge_base_id"], schema=schema,
    )
    op.create_index(
        "ix_upload_operation_state", "upload_operation",
        ["state", "upload_hard_deadline"], schema=schema,
    )
    op.create_index(
        "ix_kb_maintainer_account", "kb_maintainer", ["account_id"], schema=schema,
    )


def downgrade() -> None:
    schema = application_schema(_schema())
    verify_namespace(op.get_bind(), schema)
    owner = _schema()
    # Break the intentional upload_operation <-> document_candidate cycle
    # before either table is dropped.
    op.execute(
        f'ALTER TABLE "{owner}".upload_operation DROP CONSTRAINT '
        "IF EXISTS fk_upload_operation_candidate"
    )
    op.execute(
        f'ALTER TABLE "{owner}".document_candidate DROP CONSTRAINT '
        "IF EXISTS fk_candidate_upload"
    )
    op.drop_index("ix_kb_maintainer_account", table_name="kb_maintainer",
                  schema=schema)
    op.drop_index("ix_upload_operation_state", table_name="upload_operation",
                  schema=schema)
    op.drop_index("ix_candidate_scope", table_name="document_candidate",
                  schema=schema)
    for name in (
        "capacity_transition", "processing_job", "source_asset",
        "document_version", "upload_operation", "document_candidate",
        "document", "kb_maintainer", "space_member", "knowledge_base", "space_control",
        "program_credential", "web_session", "account",
    ):
        op.drop_table(name, schema=schema)
