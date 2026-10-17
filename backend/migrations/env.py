from alembic import context

from rag_app.adapters.postgres import application_schema, create_pg_engine, verify_namespace, verify_versions
from rag_app.bootstrap.config import Settings
from rag_app.contracts.errors import SafeError

config = context.config


def migrate(connection, schema: str) -> None:
    # Check before Alembic creates even its own version table.
    verify_versions(connection, allow_missing_extension=True)
    verify_namespace(connection, schema)
    connection.commit()
    context.configure(
        connection=connection, version_table_schema=application_schema(schema), transactional_ddl=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run() -> None:
    if context.is_offline_mode():
        raise SafeError("ONLINE_VALIDATION_REQUIRED")
    engine = None
    failure = None
    try:
        settings = Settings()
        engine = create_pg_engine(settings.database_url.get_secret_value(), settings.database_schema)
        with engine.connect() as connection:
            migrate(connection, settings.database_schema)
    except Exception as exc:
        failure = exc
    finally:
        if engine is not None:
            try:
                engine.dispose()
            except Exception as exc:
                if failure is None:
                    failure = exc
    if failure is not None:
        if isinstance(failure, SafeError):
            raise failure from None
        raise SafeError("DATABASE_OPERATION_FAILED", diagnostic_cause=failure) from None


run()

