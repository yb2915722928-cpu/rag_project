from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))


REQUIRED_POSTGRES = {
    "test_real_migration_cycle", "test_real_rollback_and_repository_boundary",
    "test_real_driver_error_is_private", "test_real_incompatible_version_is_read_only",
    "test_real_namespace_cannot_fall_back",
    "test_real_downgrade_missing_probe_preserves_peer",
}


def pytest_addoption(parser):
    parser.addoption("--require-postgres", action="store_true", help="Require all PG acceptance tests.")


def pytest_configure(config):
    config.addinivalue_line("markers", "postgres: real isolated PostgreSQL acceptance")
    config._postgres_passed = set()
    config._postgres_required_nodes = set()


def pytest_sessionstart(session):
    if session.config.getoption("--require-postgres"):
        from rag_app.bootstrap.runtime import require_python
        from rag_app.contracts.errors import SafeError
        try:
            require_python()
        except SafeError:
            raise pytest.UsageError("Acceptance requires CPython 3.12.8.") from None
        if not os.getenv("RAG_TEST_DATABASE_URL") or os.getenv("RAG_TEST_ALLOW_SCHEMA_CREATE") != "1":
            raise pytest.UsageError(
                "Acceptance requires RAG_TEST_DATABASE_URL and RAG_TEST_ALLOW_SCHEMA_CREATE=1."
            )


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(session, config, items):
    if config.getoption("--require-postgres"):
        selected = {item.originalname for item in items if item.get_closest_marker("postgres")}
        if not REQUIRED_POSTGRES <= selected:
            raise pytest.UsageError("Acceptance must collect every required PostgreSQL case.")
        config._postgres_required_nodes = {
            item.nodeid for item in items if item.get_closest_marker("postgres")
        }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    if item.config.getoption("--require-postgres") and item.get_closest_marker("postgres"):
        if report.when == "call" and report.passed:
            item.config._postgres_passed.add(item.nodeid)
        if report.skipped or report.failed:
            item.config._postgres_passed.discard(item.nodeid)


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    if config.getoption("--require-postgres"):
        if not config._postgres_required_nodes or (
            config._postgres_passed != config._postgres_required_nodes
        ):
            session.exitstatus = pytest.ExitCode.TESTS_FAILED


def cleanup_test_database(engine, admin, schema, *, created):
    failures = []
    if engine is not None:
        try:
            engine.dispose()
        except Exception as exc:
            failures.append(exc)
    if created:
        try:
            with admin.begin() as connection:
                connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        except Exception as exc:
            failures.append(exc)
    try:
        admin.dispose()
    except Exception as exc:
        failures.append(exc)
    return tuple(failures)


@pytest.fixture
def isolated_database(monkeypatch):
    from rag_app.adapters.postgres import create_pg_engine, verify_versions
    from rag_app.contracts.errors import SafeError

    value = os.getenv("RAG_TEST_DATABASE_URL")
    if not value or os.getenv("RAG_TEST_ALLOW_SCHEMA_CREATE") != "1":
        pytest.skip("Real PG not executed: URL and explicit schema-create authorization required.")
    schema = "rag_test_" + uuid.uuid4().hex
    admin = create_pg_engine(value)
    engine = None
    created = False
    failure = None
    try:
        with admin.connect() as connection:
            # Test environments provision shared infrastructure; tests never create/drop extensions.
            verify_versions(connection)
            connection.commit()
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
            connection.commit()
            created = True
        engine = create_pg_engine(value, schema)
        monkeypatch.setenv("RAG_DATABASE_URL", value)
        monkeypatch.setenv("RAG_DATABASE_SCHEMA", schema)
        yield engine, schema
    except Exception as exc:
        failure = exc
    finally:
        cleanup_errors = cleanup_test_database(engine, admin, schema, created=created)
        if failure is not None:
            code = failure.code if isinstance(failure, SafeError) else "DATABASE_OPERATION_FAILED"
            raise SafeError(
                code, diagnostic_cause=failure, cleanup_errors=cleanup_errors,
            ) from None
        if cleanup_errors:
            raise SafeError(
                "DATABASE_CLEANUP_FAILED", diagnostic_cause=cleanup_errors[0],
                cleanup_errors=cleanup_errors[1:],
            ) from None


@pytest.fixture
def isolated_peer_schema(isolated_database):
    from rag_app.adapters.postgres import create_pg_engine
    from rag_app.contracts.errors import SafeError

    original, _ = isolated_database
    schema = "rag_test_" + uuid.uuid4().hex
    admin = create_pg_engine(original.url)
    engine = None
    created = False
    failure = None
    try:
        with admin.begin() as connection:
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        created = True
        engine = create_pg_engine(original.url, schema)
        yield engine, schema
    except Exception as exc:
        failure = exc
    finally:
        cleanup_errors = cleanup_test_database(engine, admin, schema, created=created)
        if failure is not None:
            code = failure.code if isinstance(failure, SafeError) else "DATABASE_OPERATION_FAILED"
            raise SafeError(
                code, diagnostic_cause=failure, cleanup_errors=cleanup_errors,
            ) from None
        if cleanup_errors:
            raise SafeError(
                "DATABASE_CLEANUP_FAILED", diagnostic_cause=cleanup_errors[0],
                cleanup_errors=cleanup_errors[1:],
            ) from None

