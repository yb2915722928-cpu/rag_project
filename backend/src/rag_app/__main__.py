import argparse
from importlib import import_module
from importlib.metadata import version as distribution_version
from pathlib import Path
import sys

from rag_app.bootstrap.runtime import require_python
from rag_app.contracts.errors import SafeError


def load_api_server():
    try:
        if distribution_version("uvicorn") != "0.37.0":
            raise ValueError("uvicorn==0.37.0 is required")
        return import_module("uvicorn")
    except Exception as exc:
        raise SafeError("STARTUP_DEPENDENCY_UNAVAILABLE", diagnostic_cause=exc) from None


def main() -> int:
    parser = argparse.ArgumentParser(description="Story 1.1 backend entrypoints")
    parser.add_argument("command", choices=("api", "worker", "check-database", "migrate"))
    parser.add_argument("revision", nargs="?", default="head")
    parser.add_argument("--downgrade", action="store_true")
    args = parser.parse_args()
    try:
        require_python()
        if args.command == "api":
            uvicorn = load_api_server()
            from rag_app.bootstrap.config import Settings
            from rag_app.entrypoints.api import create_app
            settings = Settings()
            try:
                uvicorn.run(
                    create_app(settings), host=settings.api_host, port=settings.api_port,
                    access_log=False,
                )
            except SystemExit as exc:
                raise SafeError(
                    "STARTUP_DEPENDENCY_UNAVAILABLE", diagnostic_cause=exc,
                ) from None
        elif args.command == "worker":
            from rag_app.entrypoints.worker import run_worker
            run_worker()
        elif args.command == "check-database":
            from rag_app.entrypoints.worker import check_database
            check_database()
            print("DATABASE_BASELINE_OK")
        else:
            from alembic import command
            from alembic.config import Config
            config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
            (command.downgrade if args.downgrade else command.upgrade)(config, args.revision)
        return 0
    except Exception as exc:
        error = exc if isinstance(exc, SafeError) else SafeError(
            "DATABASE_OPERATION_FAILED", diagnostic_cause=exc,
        )
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
