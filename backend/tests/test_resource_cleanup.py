from unittest.mock import MagicMock, Mock

import conftest as fixtures
from rag_app.adapters import postgres


def test_fixture_attempts_every_cleanup_after_dispose_failure():
    engine = Mock()
    admin = MagicMock()
    connection = admin.begin.return_value.__enter__.return_value
    engine.dispose.side_effect = RuntimeError("dispose-sentinel")
    connection.exec_driver_sql.side_effect = RuntimeError("drop-sentinel")
    admin.dispose.side_effect = RuntimeError("admin-sentinel")
    failures = fixtures.cleanup_test_database(
        engine, admin, "rag_test_" + "a" * 32, created=True,
    )
    assert len(failures) == 3
    connection.exec_driver_sql.assert_called_once_with(
        'DROP SCHEMA "rag_test_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" CASCADE',
    )
    admin.dispose.assert_called_once()


def test_fixture_never_drops_a_schema_it_did_not_create():
    admin = Mock()
    assert fixtures.cleanup_test_database(None, admin, "unused", created=False) == ()
    admin.begin.assert_not_called()
    admin.dispose.assert_called_once()


def test_database_operations_have_server_side_time_bounds(monkeypatch):
    creator = Mock()
    monkeypatch.setattr(postgres, "create_engine", creator)
    postgres.create_pg_engine("postgresql+psycopg://user@localhost/test_db")
    options = creator.call_args.kwargs["connect_args"]
    assert options["connect_timeout"] == 5
    assert "-cstatement_timeout=10000" in options["options"]
    assert "-clock_timeout=5000" in options["options"]
    assert "-cidle_in_transaction_session_timeout=15000" in options["options"]
