from __future__ import annotations

import logging
import uuid
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import inspect, text

from rag_app.adapters.postgres import (
    BaselineRepository, ProbeRepository, create_uow, verify_versions,
)
from rag_app.contracts.errors import SafeError

pytestmark = pytest.mark.postgres
SENTINEL = "REAL_DRIVER_PASSWORD_BODY_SIGNED_URL_SENTINEL"


def migration_config() -> Config:
    return Config(str(Path(__file__).parents[1] / "alembic.ini"))


def assert_baseline(engine, schema):
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SHOW server_version_num").scalar_one() == "180006"
        assert connection.execute(text(
            "SELECT extversion FROM pg_extension WHERE extname='vector'"
        )).scalar_one() == "0.8.7"
        assert connection.execute(text(
            f'SELECT version_num FROM "{schema}".alembic_version'
        )).scalar_one() == "0001_baseline"
        columns = inspect(connection).get_columns("rag_uow_probe", schema=schema)
        assert {c["name"] for c in columns} == {"probe_id", "value"}
        assert all(not c["nullable"] for c in columns)
        # Cover the whole application namespace, not only the probe table.
        assert connection.execute(text(
            "SELECT count(*) FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid "
            "JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_type t ON t.oid=a.atttypid "
            "WHERE n.nspname=:schema AND a.attnum>0 AND NOT a.attisdropped "
            "AND t.typname IN ('vector','halfvec','sparsevec')"
        ), {"schema": schema}).scalar_one() == 0
        assert connection.execute(text(
            "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "JOIN pg_am am ON am.oid=c.relam WHERE n.nspname=:schema "
            "AND am.amname IN ('hnsw','ivfflat')"
        ), {"schema": schema}).scalar_one() == 0
        extension_schema = connection.execute(text(
            "SELECT n.nspname FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace "
            "WHERE e.extname='vector'"
        )).scalar_one()
        quoted = connection.dialect.identifier_preparer.quote_schema(extension_schema)
        assert connection.exec_driver_sql(
            f"SELECT {quoted}.vector_dims('[0.1,0.2,0.3]'::{quoted}.vector)"
        ).scalar_one() == 3


def test_real_migration_cycle(isolated_database):
    engine, schema = isolated_database
    config = migration_config()
    command.upgrade(config, "head")
    assert_baseline(engine, schema)
    command.downgrade(config, "base")
    with engine.connect() as connection:
        assert not inspect(connection).has_table("rag_uow_probe", schema=schema)
        assert connection.execute(text(
            f'SELECT count(*) FROM "{schema}".alembic_version'
        )).scalar_one() == 0
        assert connection.execute(text(
            "SELECT extversion FROM pg_extension WHERE extname='vector'"
        )).scalar_one() == "0.8.7"
    command.upgrade(config, "head")
    assert_baseline(engine, schema)


def test_real_rollback_and_repository_boundary(isolated_database):
    engine, schema = isolated_database
    command.upgrade(migration_config(), "head")
    with pytest.raises(SafeError) as caught:
        with create_uow(engine).transaction() as session:
            ProbeRepository(session, schema=schema).add(1, SENTINEL)
            # A second connection proves the repository did not commit.
            with engine.connect() as reader:
                assert reader.execute(text(
                    f'SELECT count(*) FROM "{schema}"."rag_uow_probe"'
                )).scalar_one() == 0
            raise RuntimeError(SENTINEL)
    assert str(caught.value.diagnostic_cause) == SENTINEL
    with engine.connect() as connection:
        assert connection.execute(text(
            f'SELECT count(*) FROM "{schema}"."rag_uow_probe"'
        )).scalar_one() == 0


def test_real_driver_error_is_private(isolated_database, caplog, capsys):
    engine, schema = isolated_database
    command.upgrade(migration_config(), "head")
    caplog.set_level(logging.DEBUG)
    with pytest.raises(SafeError) as caught:
        with create_uow(engine).transaction() as session:
            session.execute(text("SELECT CAST(:body AS integer)"), {"body": SENTINEL})
    assert caught.value.diagnostic_cause is not None
    assert SENTINEL not in str(caught.value) + caplog.text + "".join(capsys.readouterr())


def test_real_incompatible_version_is_read_only(isolated_database):
    engine, schema = isolated_database
    original = verify_versions

    def incompatible(connection, **kwargs):
        original(connection, **kwargs)
        raise SafeError("DATABASE_VERSION_MISMATCH")

    # Inject incompatibility at the real migration preflight without modifying shared extensions.
    with patch("rag_app.adapters.postgres.verify_versions", side_effect=incompatible):
        with pytest.raises(SafeError, match="DATABASE_VERSION_MISMATCH"):
            command.upgrade(migration_config(), "head")
    with engine.connect() as connection:
        assert inspect(connection).get_table_names(schema=schema) == []


def test_real_namespace_cannot_fall_back(
    isolated_database, isolated_peer_schema, monkeypatch,
):
    engine, uninitialized = isolated_database
    peer, peer_schema = isolated_peer_schema
    with monkeypatch.context() as scope:
        scope.setenv("RAG_DATABASE_SCHEMA", peer_schema)
        command.upgrade(migration_config(), "head")
    assert_baseline(peer, peer_schema)
    missing = "rag_test_" + uuid.uuid4().hex
    for target in (missing, uninitialized):
        # Deliberately supply a migrated fallback using only this test's own schemas.
        for repository in (BaselineRepository, ProbeRepository):
            with pytest.raises(SafeError):
                with create_uow(engine).transaction() as session:
                    session.execute(text(
                        f'SET LOCAL search_path TO "{target}", "{peer_schema}"'
                    ))
                    instance = repository(session, schema=target)
                    if repository is BaselineRepository:
                        instance.check()
                    else:
                        instance.add(1, SENTINEL)
    with peer.connect() as connection:
        assert connection.execute(text(
            f'SELECT count(*) FROM "{peer_schema}"."rag_uow_probe"'
        )).scalar_one() == 0
    with engine.connect() as connection:
        assert inspect(connection).get_table_names(schema=uninitialized) == []
        assert connection.execute(text(
            "SELECT count(*) FROM pg_catalog.pg_namespace WHERE nspname=:schema"
        ), {"schema": missing}).scalar_one() == 0


def test_real_downgrade_missing_probe_preserves_peer(
    isolated_database, isolated_peer_schema, monkeypatch,
):
    engine, schema = isolated_database
    peer, peer_schema = isolated_peer_schema
    command.upgrade(migration_config(), "head")
    with monkeypatch.context() as scope:
        scope.setenv("RAG_DATABASE_SCHEMA", peer_schema)
        command.upgrade(migration_config(), "head")
    with peer.begin() as connection:
        connection.execute(text(
            f'INSERT INTO "{peer_schema}"."rag_uow_probe" (probe_id,value) VALUES (1,:body)'
        ), {"body": SENTINEL})
    with engine.begin() as connection:
        connection.exec_driver_sql(f'DROP TABLE "{schema}"."rag_uow_probe"')
    # Simulate a dangerous inherited fallback on the actual migration connection.
    from rag_app.adapters.postgres import create_pg_engine as original_create
    from sqlalchemy import event

    def hostile_engine(*args, **kwargs):
        migration_engine = original_create(*args, **kwargs)

        @event.listens_for(migration_engine, "begin")
        def set_path(connection):
            connection.exec_driver_sql(
                f'SET LOCAL search_path TO "{schema}", "{peer_schema}"'
            )

        return migration_engine

    with patch("rag_app.adapters.postgres.create_pg_engine", side_effect=hostile_engine):
        with pytest.raises(SafeError, match="DATABASE_OPERATION_FAILED"):
            command.downgrade(migration_config(), "base")
    with engine.connect() as connection:
        assert not inspect(connection).has_table("rag_uow_probe", schema=schema)
        assert connection.execute(text(
            f'SELECT version_num FROM "{schema}"."alembic_version"'
        )).scalar_one() == "0001_baseline"
    assert_baseline(peer, peer_schema)
    with peer.connect() as connection:
        assert connection.execute(text(
            f'SELECT value FROM "{peer_schema}"."rag_uow_probe" WHERE probe_id=1'
        )).scalar_one() == SENTINEL

