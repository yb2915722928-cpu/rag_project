import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

import conftest as gates
from rag_app.bootstrap import runtime
from rag_app.contracts.errors import SafeError


@pytest.mark.parametrize("version", [(3, 12, 3), (3, 12, 7), (3, 12, 9), (3, 12, 15), (3, 13, 8)])
def test_exact_interpreter_guard_rejects_other_versions(monkeypatch, version):
    monkeypatch.setattr(runtime.sys, "version_info", version)
    with pytest.raises(SafeError, match="RUNTIME_VERSION_MISMATCH"):
        runtime.require_python()


def test_exact_interpreter_guard_accepts_target(monkeypatch):
    monkeypatch.setattr(runtime.sys, "implementation", SimpleNamespace(name="cpython"))
    monkeypatch.setattr(runtime.sys, "version_info", (3, 12, 8))
    runtime.require_python()


def test_exact_interpreter_guard_rejects_other_implementation(monkeypatch):
    monkeypatch.setattr(runtime.sys, "implementation", SimpleNamespace(name="pypy"))
    monkeypatch.setattr(runtime.sys, "version_info", (3, 12, 8))
    with pytest.raises(SafeError, match="RUNTIME_VERSION_MISMATCH"):
        runtime.require_python()


def test_required_mode_refuses_wrong_interpreter_without_leaking(monkeypatch):
    sentinel = "INTERPRETER_ERROR_PASSWORD_SENTINEL"

    def reject():
        raise SafeError("RUNTIME_VERSION_MISMATCH", diagnostic_cause=RuntimeError(sentinel))

    monkeypatch.setattr(runtime, "require_python", reject)
    config = SimpleNamespace(getoption=lambda name: True)
    with pytest.raises(pytest.UsageError, match=r"Acceptance requires CPython 3\.12\.8\.") as error:
        gates.pytest_sessionstart(SimpleNamespace(config=config))
    assert sentinel not in str(error.value)


def test_required_mode_refuses_missing_authorization(monkeypatch):
    monkeypatch.setattr(runtime, "require_python", lambda: None)
    monkeypatch.delenv("RAG_TEST_DATABASE_URL", raising=False)
    monkeypatch.delenv("RAG_TEST_ALLOW_SCHEMA_CREATE", raising=False)
    config = SimpleNamespace(getoption=lambda name: True)
    with pytest.raises(pytest.UsageError, match="RAG_TEST_DATABASE_URL"):
        gates.pytest_sessionstart(SimpleNamespace(config=config))


@pytest.mark.parametrize("disposition", ["pass", "skip", "deselect"])
def test_required_mode_counts_passed_cases_and_rejects_skips(tmp_path, disposition):
    # A synthetic plugin subprocess proves the gate; it never connects to a database.
    (tmp_path / "conftest.py").write_text(
        Path(gates.__file__).read_text(encoding="utf-8"), encoding="utf-8",
    )
    cases = ["import pytest", "pytestmark = pytest.mark.postgres"]
    for index, name in enumerate(sorted(gates.REQUIRED_POSTGRES)):
        body = "pytest.skip('synthetic skip')" if disposition == "skip" and index == 0 else "pass"
        cases.extend([f"def {name}():", f"    {body}"])
    (tmp_path / "test_synthetic.py").write_text("\n".join(cases), encoding="utf-8")
    env = os.environ.copy()
    env["RAG_TEST_DATABASE_URL"] = "postgresql+psycopg://unused@localhost/unused"
    env["RAG_TEST_ALLOW_SCHEMA_CREATE"] = "1"
    script = (
        "from rag_app.bootstrap import runtime; runtime.require_python=lambda: None; "
        "import pytest,sys; sys.exit(pytest.main(sys.argv[1:]))"
    )
    args = [sys.executable, "-c", script, str(tmp_path), "--require-postgres", "-q"]
    if disposition == "deselect":
        args += ["-k", "test_real_migration_cycle"]
    result = subprocess.run(args, env=env, capture_output=True, text=True, timeout=25)
    assert (result.returncode == 0) == (disposition == "pass"), result.stdout + result.stderr


def test_migration_cli_config_error_does_not_leak_to_stderr(monkeypatch):
    sentinel = "CLI_PASSWORD_BODY_SIGNED_URL_SENTINEL"
    env = os.environ.copy()
    env["RAG_DATABASE_URL"] = f"sqlite:///{sentinel}"
    script = (
        "from rag_app.bootstrap import runtime; runtime.require_python=lambda: None; "
        "from rag_app.__main__ import main; import sys; sys.exit(main())"
    )
    result = subprocess.run(
        [sys.executable, "-c", script, "migrate"], env=env,
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 2
    assert "CONFIGURATION_INVALID" in result.stderr
    assert sentinel not in result.stderr + result.stdout
    assert "Traceback" not in result.stderr


def test_real_connection_failure_cli_does_not_leak_to_stderr():
    sentinel = "CONNECTION_PASSWORD_SIGNED_URL_SENTINEL"
    env = os.environ.copy()
    env["RAG_DATABASE_URL"] = f"postgresql+psycopg://user:{sentinel}@127.0.0.1:1/unused"
    script = (
        "from rag_app.bootstrap import runtime; runtime.require_python=lambda: None; "
        "from rag_app.__main__ import main; import sys; sys.exit(main())"
    )
    result = subprocess.run(
        [sys.executable, "-c", script, "check-database"], env=env,
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 2
    assert "DATABASE_OPERATION_FAILED" in result.stderr
    assert sentinel not in result.stderr + result.stdout
    assert "Traceback" not in result.stderr
