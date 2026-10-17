"""Create the minimal PG/pgvector verification boundary."""

from alembic import op
import sqlalchemy as sa
from rag_app.adapters.postgres import application_schema, verify_namespace, verify_versions

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    verify_versions(op.get_bind(), allow_missing_extension=True)
    schema = application_schema(op.get_context().opts.get("version_table_schema"))
    verify_namespace(op.get_bind(), schema)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public VERSION '0.8.7'")
    op.create_table(
        "rag_uow_probe",
        sa.Column("probe_id", sa.Integer(), primary_key=True),
        sa.Column("value", sa.String(length=128), nullable=False),
        schema=schema,
    )


def downgrade() -> None:
    schema = application_schema(op.get_context().opts.get("version_table_schema"))
    verify_namespace(op.get_bind(), schema)
    op.drop_table("rag_uow_probe", schema=schema)

