from pathlib import Path
from importlib.metadata import PackageNotFoundError
import os
import subprocess
import sys
import tomllib
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from rag_app import __main__ as cli
from rag_app.bootstrap.runtime import TARGET_PYTHON
from rag_app.contracts.errors import SafeError


def test_runtime_and_manifest_select_the_same_exact_patch():
    root = Path(__file__).parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["requires-python"] == "==3.12.8"
    assert (root / ".python-version").read_text(encoding="utf-8").strip() == "3.12.8"
    assert TARGET_PYTHON == (3, 12, 8)
    assert "uvicorn==0.37.0" in project["dependencies"]
    lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    assert lock["requires-python"] == project["requires-python"]
    packages = {package["name"]: package for package in lock["package"]}
    assert packages["uvicorn"]["version"] == "0.37.0"
    assert {"name": "uvicorn"} in packages[project["name"]]["dependencies"]


def test_api_cli_refuses_wrong_runtime_before_loading_server(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["rag_app", "api"])
    monkeypatch.setattr(
        cli, "require_python", Mock(side_effect=SafeError("RUNTIME_VERSION_MISMATCH")),
    )
    loader = Mock()
    monkeypatch.setattr(cli, "load_api_server", loader)
    assert cli.main() == 2
    loader.assert_not_called()
    assert "RUNTIME_VERSION_MISMATCH" in capsys.readouterr().err


@pytest.mark.parametrize("failure", ["missing", "wrong-version", "broken-import"])
def test_server_dependency_error_is_finite(monkeypatch, capsys, caplog, failure):
    sentinel = "STARTUP_PASSWORD_BODY_SIGNED_URL_SENTINEL"
    monkeypatch.setattr(sys, "argv", ["rag_app", "api"])
    monkeypatch.setattr(cli, "require_python", Mock())
    version = Mock(return_value="0.37.0")
    importer = Mock(side_effect=ImportError(sentinel))
    if failure == "missing":
        version.side_effect = PackageNotFoundError(sentinel)
    elif failure == "wrong-version":
        version.return_value = "0.36.0"
    monkeypatch.setattr(cli, "distribution_version", version)
    monkeypatch.setattr(cli, "import_module", importer)
    assert cli.main() == 2
    output = capsys.readouterr()
    assert "STARTUP_DEPENDENCY_UNAVAILABLE" in output.err
    assert "DATABASE_OPERATION_FAILED" not in output.err
    assert sentinel not in output.err + output.out + caplog.text
    assert "Traceback" not in output.err
    if failure != "broken-import":
        importer.assert_not_called()


def test_api_cli_invokes_pinned_server_with_shared_app(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["rag_app", "api"])
    monkeypatch.setattr(cli, "require_python", Mock())
    version = Mock(return_value="0.37.0")
    server = SimpleNamespace(run=Mock())
    importer = Mock(return_value=server)
    monkeypatch.setattr(cli, "distribution_version", version)
    monkeypatch.setattr(cli, "import_module", importer)
    from rag_app.entrypoints import api
    app = object()
    monkeypatch.setattr(api, "create_app", Mock(return_value=app))
    assert cli.main() == 0
    version.assert_called_once_with("uvicorn")
    importer.assert_called_once_with("uvicorn")
    server.run.assert_called_once_with(
        app, host="127.0.0.1", port=8000, access_log=False,
    )


def test_actual_cli_rejects_non_target_runtime():
    if sys.implementation.name == "cpython" and sys.version_info[:3] == TARGET_PYTHON:
        pytest.skip("This negative case applies only to a supplemental non-target runtime.")
    result = subprocess.run(
        [sys.executable, "-m", "rag_app", "api"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 2
    assert "RUNTIME_VERSION_MISMATCH" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("command", ["api", "check-database", "migrate"])
def test_cli_rejects_wrong_patch_without_disclosing_environment(command):
    sentinel = "WRONG_RUNTIME_PASSWORD_SENTINEL"
    env = os.environ.copy()
    env["RAG_DATABASE_URL"] = f"postgresql+psycopg://user:{sentinel}@localhost/example"
    script = (
        "import sys; from rag_app.__main__ import main; sys.version_info=(3,12,9); "
        "sys.exit(main())"
    )
    result = subprocess.run(
        [sys.executable, "-c", script, command],
        env=env, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 2
    assert result.stderr.strip() == "RUNTIME_VERSION_MISMATCH: CPython 3.12.8 is required."
    assert sentinel not in result.stderr + result.stdout
    assert "Traceback" not in result.stderr
