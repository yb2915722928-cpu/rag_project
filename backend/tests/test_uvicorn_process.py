"""Exercise the installed API server in a real Linux child process."""

import json
from importlib.metadata import version
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest

from rag_app.bootstrap.runtime import require_python


@pytest.mark.skipif(sys.platform != "linux", reason="Real process acceptance runs on Linux.")
def test_real_uvicorn_health_and_graceful_shutdown(tmp_path):
    require_python()
    assert version("uvicorn") == "0.37.0"
    sentinel = "UVICORN_PROCESS_PASSWORD_SENTINEL"
    env = os.environ.copy()
    env["RAG_DATABASE_URL"] = f"postgresql+psycopg://user:{sentinel}@127.0.0.1:1/unused"
    env["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
    log = tmp_path / "uvicorn.log"
    with socket.socket() as listener, log.open("w+", encoding="utf-8") as output:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "rag_app.entrypoints.api:create_app", "--factory",
                "--fd", str(listener.fileno()), "--no-access-log",
            ],
            env=env, pass_fds=(listener.fileno(),),
            stdout=output, stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                assert process.poll() is None, log.read_text(encoding="utf-8")
                try:
                    with urlopen(f"http://127.0.0.1:{port}/health", timeout=0.5) as response:
                        assert response.status == 200
                        assert json.load(response) == {
                            "status": "alive", "service": "rag-api", "check": "liveness",
                        }
                    break
                except (URLError, TimeoutError):
                    time.sleep(0.05)
            else:
                pytest.fail("Uvicorn did not become healthy within 15 seconds.")
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
                pytest.fail("Uvicorn did not shut down gracefully.")
        assert process.returncode in (0, -signal.SIGTERM)
    text = log.read_text(encoding="utf-8")
    assert "Application startup complete." in text
    assert "Application shutdown complete." in text
    assert sentinel not in text
    assert "Traceback" not in text
