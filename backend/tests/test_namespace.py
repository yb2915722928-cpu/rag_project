from unittest.mock import Mock

import pytest
from sqlalchemy.dialects import postgresql

from rag_app.adapters import postgres
from rag_app.bootstrap import runtime as bootstrap
from rag_app.bootstrap.config import Settings
from rag_app.contracts.errors import SafeError


def test_engine_has_no_application_search_path_fallback(monkeypatch):
    creator = Mock()
    monkeypatch.setattr(postgres, "create_engine", creator)
    postgres.create_pg_engine("postgresql+psycopg://user@localhost/db", "target")
    options = creator.call_args.kwargs["connect_args"]["options"].split()
    assert "-csearch_path=pg_catalog" in options
    assert not any("public" in option or "target" in option for option in options)


@pytest.mark.parametrize("available", [None, False])
@pytest.mark.parametrize("repository", [postgres.BaselineRepository, postgres.ProbeRepository])
def test_missing_or_inaccessible_namespace_fails_before_application_sql(
    repository, available, monkeypatch,
):
    session = Mock()
    session.execute.return_value.scalar_one_or_none.return_value = available
    monkeypatch.setattr(postgres, "verify_versions", Mock())
    with pytest.raises(SafeError, match="DATABASE_NAMESPACE_UNAVAILABLE"):
        instance = repository(session, schema="target")
        instance.check() if repository is postgres.BaselineRepository else instance.add(1, "body")
    assert session.execute.call_count == 1
    assert "pg_namespace" in str(session.execute.call_args.args[0])


@pytest.mark.parametrize("repository", [postgres.BaselineRepository, postgres.ProbeRepository])
def test_application_sql_uses_explicit_quoted_schema(repository, monkeypatch):
    session = Mock()
    session.execute.return_value.scalar_one_or_none.return_value = True
    session.execute.return_value.scalar_one.return_value = "0001_baseline"
    monkeypatch.setattr(postgres, "verify_versions", Mock())
    instance = repository(session, schema="select")
    instance.check() if repository is postgres.BaselineRepository else instance.add(1, "body")
    statement = session.execute.call_args.args[0]
    sql = str(statement.compile(dialect=postgresql.dialect()))
    expected = '"select"."alembic_version"' if repository is postgres.BaselineRepository else (
        '"select"."rag_uow_probe"'
    )
    assert expected in sql
    assert "public" not in sql
    assert str(statement.schema if hasattr(statement, "schema") else "") != "public"


def test_bootstrap_passes_configured_namespace_to_repository(monkeypatch):
    engine = Mock()
    session = Mock()
    uow = Mock()
    uow.transaction.return_value.__enter__ = Mock(return_value=session)
    uow.transaction.return_value.__exit__ = Mock(return_value=False)
    repository = Mock()
    factory = Mock(return_value=repository)
    monkeypatch.setattr(bootstrap, "create_pg_engine", Mock(return_value=engine))
    monkeypatch.setattr(bootstrap, "create_uow", Mock(return_value=uow))
    monkeypatch.setattr(bootstrap, "BaselineRepository", factory)
    runtime = bootstrap.build_runtime(Settings(database_schema="target"))
    assert runtime.schema == "target"
    runtime.check_database()
    factory.assert_called_once_with(session, schema="target")
