"""Add the persistent epoch mirror, execution calls and append-only call facts."""

from alembic import op
import sqlalchemy as sa
from rag_app.adapters.postgres import (
    application_schema, validate_schema, verify_namespace, verify_versions,
)

revision = "0002_isolated_calls"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def _schema() -> str:
    schema = str(op.get_context().opts.get("version_table_schema", ""))
    validate_schema(schema)
    return schema


def _quoted(schema: str) -> str:
    return f'"{schema}"'


def upgrade() -> None:
    verify_versions(op.get_bind(), allow_missing_extension=True)
    schema = application_schema(_schema())
    verify_namespace(op.get_bind(), schema)
    owner = _schema()
    op.create_table(
        "rag_epoch_mirror",
        sa.Column("singleton", sa.Boolean(), primary_key=True, nullable=False),
        sa.Column("deployment_id", sa.String(length=64), nullable=False),
        sa.Column("epoch", sa.String(length=64), nullable=False),
        sa.Column("cutover_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("maintenance_version", sa.Integer(), nullable=False),
        sa.CheckConstraint("singleton", name="ck_epoch_mirror_singleton"),
        sa.CheckConstraint(
            "maintenance_version >= 1", name="ck_epoch_mirror_version",
        ),
        schema=schema,
    )
    op.create_table(
        "execution_context",
        sa.Column("context_id", sa.String(length=64), primary_key=True),
        sa.Column("epoch", sa.String(length=64), nullable=False),
        sa.Column("holder_id", sa.String(length=64), nullable=False),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=64), nullable=False),
        sa.Column("config_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("claim_token_digest", sa.String(length=64), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hard_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "state", sa.String(length=16), nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "state IN ('active','terminal','isolated')",
            name="ck_context_state",
        ),
        sa.CheckConstraint(
            "attempt > 0", name="ck_context_attempt_positive",
        ),
        sa.CheckConstraint(
            "lease_until <= hard_deadline",
            name="ck_context_lease_within_deadline",
        ),
        schema=schema,
    )
    op.create_table(
        "execution_call",
        sa.Column("call_id", sa.String(length=64), primary_key=True),
        sa.Column("epoch", sa.String(length=64), nullable=False),
        sa.Column("owner_context_id", sa.String(length=64), nullable=False),
        sa.Column("holder_id", sa.String(length=64), nullable=False),
        sa.Column("space_id", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=64), nullable=False),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("claim_token_digest", sa.String(length=64), nullable=False),
        sa.Column("config_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("prepared_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hard_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("may_have_sent_at", sa.DateTime(timezone=True)),
        sa.Column("grant_id", sa.String(length=64), unique=True),
        sa.Column("boot_id", sa.String(length=128)),
        sa.Column("child_instance", sa.String(length=128)),
        sa.Column("terminal_at", sa.DateTime(timezone=True)),
        sa.Column("provider_ref", sa.String(length=256)),
        sa.Column(
            "usage_status", sa.String(length=16), nullable=False,
            server_default="unknown",
        ),
        sa.Column("prompt_tokens", sa.Integer()),
        sa.Column("completion_tokens", sa.Integer()),
        sa.Column("total_tokens", sa.Integer()),
        sa.Column("cost_kind", sa.String(length=16)),
        sa.Column("cost_amount", sa.Numeric(precision=38, scale=12)),
        sa.Column("cost_currency", sa.String(length=3)),
        sa.Column("cost_basis", sa.String(length=64)),
        sa.Column(
            "reconciliation_status", sa.String(length=16), nullable=False,
            server_default="none",
        ),
        sa.CheckConstraint(
            "attempt > 0", name="ck_call_attempt_positive",
        ),
        sa.CheckConstraint(
            "lease_until <= hard_deadline", name="ck_call_lease_within_deadline",
        ),
        sa.CheckConstraint(
            "state IN ('prepared','may_have_sent','responded','known_failure','unknown')",
            name="ck_call_state",
        ),
        sa.CheckConstraint(
            "(state <> 'prepared') OR (grant_id IS NULL AND boot_id IS NULL "
            "AND child_instance IS NULL AND may_have_sent_at IS NULL)",
            name="ck_call_prepared_has_no_send",
        ),
        sa.CheckConstraint(
            "(state <> 'may_have_sent') OR (grant_id IS NOT NULL "
            "AND boot_id IS NOT NULL AND child_instance IS NOT NULL "
            "AND may_have_sent_at IS NOT NULL)",
            name="ck_call_sent_has_grant",
        ),
        sa.CheckConstraint(
            "(state NOT IN ('responded','known_failure','unknown')) "
            "OR terminal_at IS NOT NULL",
            name="ck_call_terminal_has_time",
        ),
        sa.CheckConstraint(
            "(state <> 'unknown') OR (provider_ref IS NULL "
            "AND usage_status = 'unknown' AND prompt_tokens IS NULL "
            "AND completion_tokens IS NULL AND total_tokens IS NULL "
            "AND cost_kind IS NULL AND cost_amount IS NULL "
            "AND cost_currency IS NULL AND cost_basis IS NULL)",
            name="ck_call_unknown_is_null",
        ),
        sa.CheckConstraint(
            "usage_status IN ('unknown','reported')", name="ck_call_usage_status",
        ),
        sa.CheckConstraint(
            "(prompt_tokens IS NULL OR prompt_tokens >= 0) "
            "AND (completion_tokens IS NULL OR completion_tokens >= 0) "
            "AND (total_tokens IS NULL OR total_tokens >= 0)",
            name="ck_call_tokens_nonnegative",
        ),
        sa.CheckConstraint(
            "(usage_status <> 'reported') OR (prompt_tokens IS NOT NULL "
            "OR completion_tokens IS NOT NULL OR total_tokens IS NOT NULL)",
            name="ck_call_reported_usage",
        ),
        sa.CheckConstraint(
            "(cost_kind IS NULL AND cost_amount IS NULL AND cost_currency IS NULL "
            "AND cost_basis IS NULL) OR (cost_kind IN ('estimated','actual') "
            "AND cost_basis IS NOT NULL "
            "AND ((cost_amount IS NULL AND cost_currency IS NULL) "
            "OR (cost_amount IS NOT NULL AND cost_amount >= 0 "
            "AND cost_currency IS NOT NULL)))",
            name="ck_call_cost_shape",
        ),
        sa.CheckConstraint(
            "reconciliation_status IN ('none','required')",
            name="ck_call_reconciliation",
        ),
        schema=schema,
    )
    op.create_table(
        "ledger_call_fact",
        sa.Column(
            "fact_id", sa.BigInteger(), sa.Identity(always=False),
            primary_key=True,
        ),
        sa.Column("call_id", sa.String(length=64), nullable=False),
        sa.Column("fact_digest", sa.String(length=64), nullable=False),
        sa.Column("provider_ref", sa.String(length=256)),
        sa.Column(
            "usage_status", sa.String(length=16), nullable=False,
            server_default="unknown",
        ),
        sa.Column("prompt_tokens", sa.Integer()),
        sa.Column("completion_tokens", sa.Integer()),
        sa.Column("total_tokens", sa.Integer()),
        sa.Column("cost_kind", sa.String(length=16)),
        sa.Column("cost_amount", sa.Numeric(precision=38, scale=12)),
        sa.Column("cost_currency", sa.String(length=3)),
        sa.Column("cost_basis", sa.String(length=64)),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("disposition", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "usage_status IN ('unknown','reported')", name="ck_fact_usage_status",
        ),
        sa.CheckConstraint(
            "(prompt_tokens IS NULL OR prompt_tokens >= 0) "
            "AND (completion_tokens IS NULL OR completion_tokens >= 0) "
            "AND (total_tokens IS NULL OR total_tokens >= 0)",
            name="ck_fact_tokens_nonnegative",
        ),
        sa.CheckConstraint(
            "(cost_kind IS NULL AND cost_amount IS NULL AND cost_currency IS NULL "
            "AND cost_basis IS NULL) OR (cost_kind IN ('estimated','actual') "
            "AND cost_basis IS NOT NULL "
            "AND ((cost_amount IS NULL AND cost_currency IS NULL) "
            "OR (cost_amount IS NOT NULL AND cost_amount >= 0 "
            "AND cost_currency IS NOT NULL)))",
            name="ck_fact_cost_shape",
        ),
        sa.CheckConstraint(
            "disposition IN ('appended','conflict')", name="ck_fact_disposition",
        ),
        sa.UniqueConstraint(
            "call_id", "fact_digest", name="uq_fact_call_digest",
        ),
        schema=schema,
    )
    op.create_index(
        "ix_fact_call_id", "ledger_call_fact", ["call_id"], schema=schema,
    )
    op.execute(
        f"ALTER TABLE {_quoted(owner)}.execution_call ADD CONSTRAINT "
        "fk_call_context FOREIGN KEY (owner_context_id) "
        f"REFERENCES {_quoted(owner)}.execution_context(context_id) "
        "ON DELETE RESTRICT"
    )
    op.execute(
        f"ALTER TABLE {_quoted(owner)}.ledger_call_fact ADD CONSTRAINT "
        "fk_fact_call FOREIGN KEY (call_id) "
        f"REFERENCES {_quoted(owner)}.execution_call(call_id) "
        "ON DELETE RESTRICT"
    )


def downgrade() -> None:
    schema = application_schema(_schema())
    verify_namespace(op.get_bind(), schema)
    owner = _schema()
    op.drop_index("ix_fact_call_id", table_name="ledger_call_fact", schema=schema)
    op.drop_table("ledger_call_fact", schema=schema)
    op.drop_table("execution_call", schema=schema)
    op.drop_table("execution_context", schema=schema)
    op.drop_table("rag_epoch_mirror", schema=schema)
