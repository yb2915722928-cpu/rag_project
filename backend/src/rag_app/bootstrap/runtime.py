from dataclasses import dataclass
from functools import partial
import sys

from sqlalchemy.engine import Engine

from rag_app.adapters.postgres import BaselineRepository, create_pg_engine, create_uow
from rag_app.application.baseline import check_baseline
from rag_app.application.uow import UnitOfWork
from rag_app.bootstrap.config import Settings
from rag_app.contracts.errors import SafeError

TARGET_PYTHON = (3, 12, 8)


def require_python() -> None:
    if sys.implementation.name != "cpython" or sys.version_info[:3] != TARGET_PYTHON:
        raise SafeError("RUNTIME_VERSION_MISMATCH")


@dataclass
class Runtime:
    engine: Engine
    uow: UnitOfWork
    schema: str

    def check_database(self) -> None:
        check_baseline(self.uow, partial(BaselineRepository, schema=self.schema))

    def close(self) -> None:
        try:
            self.engine.dispose()
        except Exception as exc:
            raise SafeError("DATABASE_CLEANUP_FAILED", diagnostic_cause=exc) from None


def build_runtime(settings: Settings) -> Runtime:
    engine = create_pg_engine(settings.database_url.get_secret_value(), settings.database_schema)
    return Runtime(engine, create_uow(engine), settings.database_schema)
