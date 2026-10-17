"""Entrypoint tests; synthetic lifecycle cases do not establish PG readiness."""

import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener
import uuid

import pytest

from rag_app import __main__ as cli
from rag_app.application.uow import UnitOfWork
from rag_app.bootstrap.config import Settings
from rag_app.bootstrap.runtime import require_python
from rag_app.contracts.errors import SafeError
from rag_app.entrypoints import worker


def test_bind_defaults_and_trusted_environment(monkeypatch):
    monkeypatch.delenv("RAG_API_HOST", raising=False)
    monkeypatch.delenv("RAG_API_PORT", raising=False)
    monkeypatch.setenv("HTTP_HOST", "UNTRUSTED_HOST_SENTINEL")
    monkeypatch.setenv("HTTP_X_FORWARDED_HOST", "UNTRUSTED_FORWARDED_SENTINEL")
    assert (Settings().api_host, Settings().api_port) == ("127.0.0.1", 8000)
    monkeypatch.setenv("RAG_API_HOST", "0.0.0.0")
    monkeypatch.setenv("RAG_API_PORT", "8123")
    assert (Settings().api_host, Settings().api_port) == ("0.0.0.0", 8123)


@pytest.mark.parametrize("host", ["127.0.0.1", "0.0.0.0", "::1", "::", "2001:db8::1"])
def test_bind_accepts_ip_literals(host):
    assert Settings(api_host=host).api_host == host


@pytest.mark.parametrize("host", [
    "", "localhost", "example.com", "https://127.0.0.1", "127.0.0.1:8000",
    "1.2.3.999", "127.0.0.1/8", "fe80::1%eth0", " 127.0.0.1", "x" * 46, 123,
])
def test_bind_rejects_non_literal_hosts_without_exposing_input(host):
    with pytest.raises(SafeError) as caught:
        Settings(api_host=host)
    assert str(caught.value) == "CONFIGURATION_INVALID: Invalid PostgreSQL configuration."


@pytest.mark.parametrize("port", [1, 65535, "8000"])
def test_bind_accepts_bounded_ports(port):
    assert Settings(api_port=port).api_port == int(port)


@pytest.mark.parametrize("port", [0, 65536, -1, True, 8.5, "8000.0", "+8000", " 8000", "８０００", "1" * 99])
def test_bind_rejects_invalid_ports(port):
    with pytest.raises(SafeError, match="CONFIGURATION_INVALID"):
        Settings(api_port=port)


def test_api_cli_passes_one_trusted_settings_object(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["rag_app", "api"])
    monkeypatch.setattr(cli, "require_python", Mock())
    server = SimpleNamespace(run=Mock())
    monkeypatch.setattr(cli, "load_api_server", Mock(return_value=server))
    monkeypatch.setenv("RAG_API_HOST", "0.0.0.0")
    monkeypatch.setenv("RAG_API_PORT", "8123")
    from rag_app.entrypoints import api
    app = object()
    factory = Mock(return_value=app)
    monkeypatch.setattr(api, "create_app", factory)
    assert cli.main() == 0
    settings = factory.call_args.args[0]
    assert (settings.api_host, settings.api_port) == ("0.0.0.0", 8123)
    server.run.assert_called_once_with(app, host="0.0.0.0", port=8123, access_log=False)


def test_api_cli_configuration_failure_is_finite(monkeypatch, capsys):
    sentinel = "BIND_PASSWORD_SENTINEL"
    monkeypatch.setattr(sys, "argv", ["rag_app", "api"])
    monkeypatch.setattr(cli, "require_python", Mock())
    server = SimpleNamespace(run=Mock())
    monkeypatch.setattr(cli, "load_api_server", Mock(return_value=server))
    monkeypatch.setenv("RAG_API_HOST", sentinel)
    assert cli.main() == 2
    server.run.assert_not_called()
    output = capsys.readouterr()
    assert "CONFIGURATION_INVALID" in output.err
    assert sentinel not in output.out + output.err
    assert "Traceback" not in output.err


def test_worker_cli_selects_persistent_entrypoint(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["rag_app", "worker"])
    guard = Mock()
    run = Mock()
    monkeypatch.setattr(cli, "require_python", guard)
    monkeypatch.setattr(worker, "run_worker", run)
    assert cli.main() == 0
    guard.assert_called_once_with()
    run.assert_called_once_with()


def test_worker_cli_refuses_wrong_interpreter_before_bootstrap(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["rag_app", "worker"])
    monkeypatch.setattr(cli, "require_python", Mock(side_effect=SafeError("RUNTIME_VERSION_MISMATCH")))
    run = Mock()
    monkeypatch.setattr(worker, "run_worker", run)
    assert cli.main() == 2
    run.assert_not_called()
    assert "RUNTIME_VERSION_MISMATCH" in capsys.readouterr().err


def install_synthetic_signals(monkeypatch):
    old = {signal.SIGTERM: object(), signal.SIGINT: object()}
    setter = Mock()
    monkeypatch.setattr(worker.signal, "getsignal", lambda signum: old[signum])
    monkeypatch.setattr(worker.signal, "signal", setter)
    monkeypatch.setattr(worker.signal, "set_wakeup_fd", Mock(return_value=-1))
    return old, setter


requires_linux_self_pipe = pytest.mark.skipif(
    sys.platform != "linux",
    reason="Worker self-pipe lifecycle is a Linux acceptance path; no Windows fallback.",
)


@requires_linux_self_pipe
def test_worker_closes_short_uow_before_idle_and_restores_handlers(monkeypatch):
    old, setter = install_synthetic_signals(monkeypatch)
    actual_pipe = worker.os.pipe2
    descriptors = []

    def create_pipe(flags):
        assert flags == os.O_NONBLOCK | os.O_CLOEXEC
        pair = actual_pipe(flags)
        descriptors.extend(pair)
        return pair

    monkeypatch.setattr(worker.os, "pipe2", create_pipe)
    session = Mock()
    uow = UnitOfWork(lambda: session)

    def check():
        with uow.transaction():
            pass

    runtime = Mock()
    runtime.check_database.side_effect = check
    def wait(readers, writers, errors, timeout):
        assert timeout == 60
        session.commit.assert_called_once()
        session.close.assert_called_once()
        runtime.close.assert_not_called()
        setter.call_args_list[0].args[1](signal.SIGTERM, None)
        return [], [], []

    monkeypatch.setattr(worker.select, "select", Mock(side_effect=wait))
    monkeypatch.setattr(worker, "build_runtime", Mock(return_value=runtime))
    worker.run_worker(Settings())
    runtime.check_database.assert_called_once()
    runtime.close.assert_called_once()
    assert [call.args for call in setter.call_args_list[-2:]] == list(old.items())
    wakeup = worker.signal.set_wakeup_fd.call_args_list
    assert wakeup[0].args == (descriptors[1],)
    assert wakeup[0].kwargs == {"warn_on_full_buffer": False}
    assert wakeup[-1].args == (-1,)
    for fd in descriptors:
        with pytest.raises(OSError):
            os.fstat(fd)


@requires_linux_self_pipe
@pytest.mark.parametrize("phase", ["build", "check", "check-raw", "close"])
def test_worker_preserves_private_failure_and_cleanup(monkeypatch, phase):
    _, setter = install_synthetic_signals(monkeypatch)
    primary = SafeError("DATABASE_VERSION_MISMATCH", diagnostic_cause=RuntimeError("PRIMARY_SENTINEL"))
    cleanup = RuntimeError("CLEANUP_SENTINEL")
    runtime = Mock()
    def wake(*args):
        setter.call_args_list[0].args[1](signal.SIGTERM, None)
        return [], [], []

    wait = Mock(side_effect=wake)
    monkeypatch.setattr(worker.select, "select", wait)
    build = Mock(return_value=runtime)
    monkeypatch.setattr(worker, "build_runtime", build)
    if phase == "build":
        build.side_effect = primary
    elif phase == "check":
        runtime.check_database.side_effect = primary
        runtime.close.side_effect = cleanup
    elif phase == "check-raw":
        runtime.check_database.side_effect = primary.diagnostic_cause
        runtime.close.side_effect = cleanup
    else:
        runtime.close.side_effect = cleanup
    with pytest.raises(SafeError) as caught:
        worker.run_worker(Settings())
    if phase == "close":
        assert caught.value.code == "DATABASE_CLEANUP_FAILED"
        assert caught.value.diagnostic_cause is cleanup
    elif phase == "check-raw":
        assert caught.value.code == "DATABASE_OPERATION_FAILED"
        assert caught.value.diagnostic_cause is primary.diagnostic_cause
        assert caught.value.cleanup_errors == (cleanup,)
        wait.assert_not_called()
    else:
        assert caught.value is primary
        wait.assert_not_called()
    if phase == "check":
        assert caught.value.cleanup_errors == (cleanup,)
    if phase == "build":
        runtime.close.assert_not_called()
    else:
        runtime.close.assert_called_once()
    assert "SENTINEL" not in str(caught.value)


@requires_linux_self_pipe
def test_worker_keeps_cleanup_failure_private_and_releases_resources(monkeypatch):
    old, setter = install_synthetic_signals(monkeypatch)
    actual_pipe = worker.os.pipe2
    descriptors = []

    def create_pipe(flags):
        pair = actual_pipe(flags)
        descriptors.extend(pair)
        return pair

    monkeypatch.setattr(worker.os, "pipe2", create_pipe)
    restore_failure = RuntimeError("WAKEUP_RESTORE_SENTINEL")
    monkeypatch.setattr(
        worker.signal, "set_wakeup_fd", Mock(side_effect=[-1, restore_failure]),
    )
    runtime = Mock()

    def wake(readers, writers, errors, timeout):
        setter.call_args_list[0].args[1](signal.SIGINT, None)
        return [], [], []

    monkeypatch.setattr(worker.select, "select", Mock(side_effect=wake))
    monkeypatch.setattr(worker, "build_runtime", Mock(return_value=runtime))
    with pytest.raises(SafeError) as caught:
        worker.run_worker(Settings())
    assert caught.value.code == "DATABASE_CLEANUP_FAILED"
    assert caught.value.diagnostic_cause is restore_failure
    assert caught.value.cleanup_errors == ()
    assert "SENTINEL" not in str(caught.value)
    runtime.close.assert_called_once()
    assert [call.args for call in setter.call_args_list[-2:]] == list(old.items())
    for fd in descriptors:
        with pytest.raises(OSError):
            os.fstat(fd)


def test_api_cli_converts_server_startup_exit_to_finite_error(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["rag_app", "api"])
    monkeypatch.setattr(cli, "require_python", Mock())
    server = SimpleNamespace(run=Mock(side_effect=SystemExit("PRIVATE_SERVER_SENTINEL")))
    monkeypatch.setattr(cli, "load_api_server", Mock(return_value=server))
    from rag_app.entrypoints import api
    monkeypatch.setattr(api, "create_app", Mock(return_value=object()))
    assert cli.main() == 2
    output = capsys.readouterr()
    assert "STARTUP_DEPENDENCY_UNAVAILABLE" in output.err
    assert "PRIVATE_SERVER_SENTINEL" not in output.out + output.err


@requires_linux_self_pipe
@pytest.mark.parametrize("failure", ["config", "connection"])
def test_real_worker_cli_failure_is_private(failure):
    require_python()
    sentinel = "WORKER_PASSWORD_SENTINEL"
    env = os.environ.copy()
    if failure == "config":
        env["RAG_DATABASE_URL"] = f"sqlite:///{sentinel}"
        expected = "CONFIGURATION_INVALID"
    else:
        env["RAG_DATABASE_URL"] = f"postgresql+psycopg://user:{sentinel}@127.0.0.1:1/unused"
        expected = "DATABASE_OPERATION_FAILED"
    result = subprocess.run(
        [sys.executable, "-m", "rag_app", "worker"], env=env,
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 2
    assert expected in result.stderr
    assert sentinel not in result.stdout + result.stderr
    assert "Traceback" not in result.stderr


def stop_child(process, signum=signal.SIGTERM):
    if process.poll() is None:
        try:
            process.send_signal(signum)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
        pytest.fail("Child failed to stop within the bounded shutdown window.")


@pytest.mark.skipif(sys.platform != "linux", reason="Linux process acceptance.")
@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGINT])
def test_synthetic_worker_process_signals_and_cleanup(tmp_path, signum):
    """Real Linux signals with a synthetic DB boundary; not a PG acceptance."""
    require_python()
    marker = tmp_path / "lifecycle"
    script = (
        "import sys; from pathlib import Path; from rag_app.entrypoints import worker; "
        "from rag_app.bootstrap.runtime import require_python; require_python(); "
        "p=Path(sys.argv[1]); "
        "R=type('R',(),{'check_database':lambda s:p.write_text('checked'),"
        "'close':lambda s:p.write_text('closed')}); "
        "worker.build_runtime=lambda settings:R(); worker.run_worker()"
    )
    with (tmp_path / "worker.log").open("w") as log:
        process = subprocess.Popen([sys.executable, "-c", script, str(marker)], stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                assert process.poll() is None
                if marker.exists() and marker.read_text() == "checked":
                    break
                time.sleep(0.05)
            assert marker.read_text() == "checked"
            time.sleep(0.2)
            assert process.poll() is None
        finally:
            stop_child(process, signum)
    assert process.returncode == 0
    assert marker.read_text() == "closed"


@pytest.mark.skipif(sys.platform != "linux", reason="Linux process acceptance.")
def test_real_api_cli_uses_trusted_bind_and_ignores_forwarded_host(tmp_path):
    require_python()
    with socket.socket() as candidate:
        candidate.bind(("127.0.0.1", 0))
        port = candidate.getsockname()[1]
    env = os.environ.copy()
    env.update(RAG_API_HOST="0.0.0.0", RAG_API_PORT=str(port), RAG_DATABASE_SCHEMA="public")
    env["RAG_DATABASE_URL"] = "postgresql+psycopg://unused@127.0.0.1:1/unused"
    opener = build_opener(ProxyHandler({}))
    with (tmp_path / "api.log").open("w") as log:
        process = subprocess.Popen([sys.executable, "-m", "rag_app", "api"], env=env, stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                assert process.poll() is None
                try:
                    request = Request(
                        f"http://127.0.0.1:{port}/health",
                        headers={"Host": "untrusted.example", "X-Forwarded-Host": "other.example"},
                    )
                    with opener.open(request, timeout=0.5) as response:
                        assert json.load(response)["status"] == "alive"
                    break
                except (URLError, TimeoutError):
                    time.sleep(0.05)
            else:
                pytest.fail("API failed to bind the trusted port.")
        finally:
            stop_child(process)
    assert process.returncode in (0, -signal.SIGTERM)
    text = (tmp_path / "api.log").read_text()
    assert f"0.0.0.0:{port}" in text
    assert "Application shutdown complete." in text
    assert "Traceback" not in text


@pytest.mark.postgres
@pytest.mark.skipif(sys.platform != "linux", reason="Real PG/Linux process acceptance.")
@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGINT])
def test_real_pg_worker_idle_has_no_transaction_and_exits(isolated_database, tmp_path, signum):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import text

    engine, schema = isolated_database
    command.upgrade(Config(str(Path(__file__).parents[1] / "alembic.ini")), "head")
    name = "rag_idle_" + uuid.uuid4().hex
    env = os.environ.copy()
    env.update(
        RAG_DATABASE_URL=os.environ["RAG_TEST_DATABASE_URL"],
        RAG_DATABASE_SCHEMA=schema, PGAPPNAME=name,
    )
    with (tmp_path / "worker-pg.log").open("w") as log:
        process = subprocess.Popen([sys.executable, "-m", "rag_app", "worker"], env=env, stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                assert process.poll() is None
                with engine.connect() as connection:
                    rows = connection.execute(text(
                        "SELECT state,xact_start,query FROM pg_catalog.pg_stat_activity "
                        "WHERE application_name=:name"
                    ), {"name": name}).all()
                if rows and all(
                    row.state == "idle" and row.xact_start is None
                    and row.query.strip().upper() == "COMMIT" for row in rows
                ):
                    break
                time.sleep(0.05)
            else:
                pytest.fail("Worker did not reach transaction-free idle after its PG check.")
            time.sleep(0.2)
            assert process.poll() is None
        finally:
            stop_child(process, signum)
    assert process.returncode == 0
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        with engine.connect() as connection:
            remaining = connection.execute(text(
                "SELECT count(*) FROM pg_catalog.pg_stat_activity WHERE application_name=:name"
            ), {"name": name}).scalar_one()
        if remaining == 0:
            break
        time.sleep(0.05)
    assert remaining == 0
    assert "Traceback" not in (tmp_path / "worker-pg.log").read_text()
