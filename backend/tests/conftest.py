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
    "test_real_call_lifecycle_and_single_grant",
    "test_real_terminal_idempotency_and_late_facts",
    "test_real_late_fact_does_not_take_parent_lock",
    "test_real_failed_transaction_leaves_no_call",
    "test_real_epoch_mirror_restart_and_contradiction",
    "test_real_lease_expiry_under_held_context_lock_denies_old_now",
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


@pytest.fixture
def call_persistence(isolated_database, tmp_path):
    """Real-PG context reused by the C integration: migrated schema, control, lifecycle."""

    from types import SimpleNamespace

    from alembic import command
    from alembic.config import Config

    from rag_app.adapters.epoch_control import (
        FileEpochControl, initialize_epoch_control, mirror_epoch,
    )
    from rag_app.adapters.postgres import create_uow
    from rag_app.bootstrap.runtime import build_call_lifecycle

    engine, schema = isolated_database
    command.upgrade(Config(str(Path(__file__).parents[1] / "alembic.ini")), "head")
    control = initialize_epoch_control(
        tmp_path / "epoch-control.json", deployment_id="test_deployment",
    )
    mirror_epoch(create_uow(engine), control, schema=schema)
    reader = FileEpochControl(tmp_path / "epoch-control.json", schema=schema)
    context = SimpleNamespace(
        engine=engine, schema=schema, uow=create_uow(engine),
        control=reader, epoch=control,
        lifecycle=build_call_lifecycle(reader, schema),
        control_path=tmp_path / "epoch-control.json",
    )
    context.initialize_context = lambda **values: _seeded_context(
        context, **values,
    )
    return context


def _seeded_context(
    context, *, context_id="context-1", holder_id="holder-1",
    space_id="space-1", purpose="query", config_fingerprint="config:v1",
    claim_token="claim-token-0000000000000001",
    lease_seconds=300, deadline_seconds=600,
):
    """C/test seam: create current authority against the migrated real schema."""

    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    return context.lifecycle.initialize_context(
        context.uow, context_id=context_id, holder_id=holder_id,
        space_id=space_id, purpose=purpose,
        config_fingerprint=config_fingerprint, attempt=1,
        claim_token=claim_token,
        lease_until=now + timedelta(seconds=lease_seconds),
        hard_deadline=now + timedelta(seconds=deadline_seconds), now=now,
    )

