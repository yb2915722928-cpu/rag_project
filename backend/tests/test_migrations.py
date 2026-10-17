import importlib.util
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest

from rag_app.adapters.postgres import verify_versions
from rag_app.contracts.errors import SafeError


@pytest.mark.parametrize("server,installed,available", [
    ("180005", "0.8.7", True), ("180006", "0.8.6", True),
    ("180006", None, False),
])
def test_incompatible_versions_fail_before_any_ddl(server, installed, available) -> None:
    connection = Mock()
    connection.exec_driver_sql.return_value.scalar_one.return_value = server
    connection.execute.return_value.scalar_one_or_none.return_value = installed
    connection.execute.return_value.scalar.return_value = available
    with pytest.raises(SafeError, match="DATABASE_VERSION_MISMATCH"):
        verify_versions(connection, allow_missing_extension=True)
    sql = [str(call.args[0]).upper() for call in connection.execute.call_args_list]
    assert not any(word in statement for statement in sql for word in ("CREATE ", "DROP ", "ALTER "))


def test_downgrade_only_drops_owned_table(monkeypatch) -> None:
    path = Path(__file__).parents[1] / "migrations/versions/0001_baseline.py"
    spec = importlib.util.spec_from_file_location("baseline", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    operations = Mock()
    operations.get_context.return_value.opts = {"version_table_schema": "target"}
    monkeypatch.setattr(module, "op", operations)
    monkeypatch.setattr(module, "verify_namespace", Mock())
    module.downgrade()
    operations.drop_table.assert_called_once_with("rag_uow_probe", schema="target")
    operations.execute.assert_not_called()


def test_upgrade_qualifies_owned_table(monkeypatch):
    path = Path(__file__).parents[1] / "migrations/versions/0001_baseline.py"
    spec = importlib.util.spec_from_file_location("baseline_qualified", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    operations = Mock()
    operations.get_context.return_value.opts = {"version_table_schema": "select"}
    monkeypatch.setattr(module, "op", operations)
    monkeypatch.setattr(module, "verify_versions", Mock())
    monkeypatch.setattr(module, "verify_namespace", Mock())
    module.upgrade()
    schema = operations.create_table.call_args.kwargs["schema"]
    assert schema == "select"
    assert schema.quote is True


def test_downgrade_requires_explicit_namespace(monkeypatch):
    path = Path(__file__).parents[1] / "migrations/versions/0001_baseline.py"
    spec = importlib.util.spec_from_file_location("baseline_no_namespace", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    operations = Mock()
    operations.get_context.return_value.opts = {}
    monkeypatch.setattr(module, "op", operations)
    with pytest.raises(SafeError, match="CONFIGURATION_INVALID"):
        module.downgrade()
    operations.drop_table.assert_not_called()


def test_upgrade_checks_compatibility_before_owned_ddl(monkeypatch):
    path = Path(__file__).parents[1] / "migrations/versions/0001_baseline.py"
    spec = importlib.util.spec_from_file_location("baseline", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    operations = Mock()
    monkeypatch.setattr(module, "op", operations)
    monkeypatch.setattr(
        module, "verify_versions", Mock(side_effect=SafeError("DATABASE_VERSION_MISMATCH")),
    )
    with pytest.raises(SafeError, match="DATABASE_VERSION_MISMATCH"):
        module.upgrade()
    operations.create_table.assert_not_called()
    operations.execute.assert_not_called()


def test_downgrade_compiles_qualified_drop_without_if_exists(monkeypatch):
    path = Path(__file__).parents[1] / "migrations/versions/0001_baseline.py"
    spec = importlib.util.spec_from_file_location("baseline_sql", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = StringIO()
    context = MigrationContext.configure(
        dialect_name="postgresql",
        opts={"as_sql": True, "output_buffer": output, "version_table_schema": "select"},
    )
    monkeypatch.setattr(module, "op", Operations(context))
    monkeypatch.setattr(module, "verify_namespace", Mock())
    module.downgrade()
    sql = output.getvalue()
    assert 'DROP TABLE "select".rag_uow_probe' in sql
    assert "public" not in sql
    assert "IF EXISTS" not in sql
