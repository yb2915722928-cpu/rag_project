from __future__ import annotations

import logging
import re
from typing import Any, Protocol

from sqlalchemy import Integer, String, column, create_engine, select, table, text
from sqlalchemy.engine import Connection, Engine, URL, make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import quoted_name

from rag_app.application.uow import UnitOfWork
from rag_app.contracts.errors import SafeError

HEAD_REVISION = "0002_isolated_calls"


def validate_database_url(value: str) -> URL:
    try:
        url = make_url(value)
        if (
            url.drivername != "postgresql+psycopg" or not url.host or not url.database
            or url.port == 0
            or any(key not in {"sslmode", "connect_timeout"} for key in url.query)
        ):
            raise ValueError("unsupported configuration")
        return url
    except Exception as exc:
        raise SafeError("CONFIGURATION_INVALID", diagnostic_cause=exc) from None


def validate_schema(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", value):
        raise SafeError("CONFIGURATION_INVALID") from None
    return value


def create_pg_engine(database_url: str, schema: str = "public") -> Engine:
    url = validate_database_url(database_url)
    schema = validate_schema(schema)
    try:
        # Do not emit SQL text or driver details even when parent logging is DEBUG.
        logging.getLogger("sqlalchemy.engine.Engine.rag").disabled = True
        return create_engine(
            url, hide_parameters=True, echo=False, logging_name="rag",
            connect_args={
                "connect_timeout": 5,
                "options": (
                    "-csearch_path=pg_catalog -cstatement_timeout=10000 "
                    "-clock_timeout=5000 -cidle_in_transaction_session_timeout=15000"
                ),
            },
        )
    except Exception as exc:
        raise SafeError("CONFIGURATION_INVALID", diagnostic_cause=exc) from None


def create_uow(engine: Engine) -> UnitOfWork:
    return UnitOfWork(sessionmaker(bind=engine, class_=Session, expire_on_commit=False))


def verify_versions(connection: Connection, *, allow_missing_extension: bool = False) -> None:
    if str(connection.exec_driver_sql("SHOW server_version_num").scalar_one()) != "180006":
        raise SafeError("DATABASE_VERSION_MISMATCH")
    installed = connection.execute(
        text("SELECT extversion FROM pg_catalog.pg_extension WHERE extname = 'vector'")
    ).scalar_one_or_none()
    if installed == "0.8.7":
        return
    if installed is None and allow_missing_extension:
        available = connection.execute(text(
            "SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_available_extension_versions "
            "WHERE name = 'vector' AND version = '0.8.7')"
        )).scalar()
        if available:
            return
    raise SafeError("DATABASE_VERSION_MISMATCH")


class ExecuteOnly(Protocol):
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...


def application_schema(schema: str) -> quoted_name:
    return quoted_name(validate_schema(schema), quote=True)


def verify_namespace(executor: ExecuteOnly, schema: str) -> None:
    available = executor.execute(text(
        "SELECT pg_catalog.has_schema_privilege(n.oid, 'USAGE') "
        "FROM pg_catalog.pg_namespace AS n WHERE n.nspname = :schema"
    ), {"schema": validate_schema(schema)}).scalar_one_or_none()
    if available is not True:
        raise SafeError("DATABASE_NAMESPACE_UNAVAILABLE")


def probe_table(schema: str):
    return table(
        quoted_name("rag_uow_probe", quote=True),
        column("probe_id", Integer()), column("value", String(128)),
        schema=application_schema(schema),
    )


class ProbeRepository:
    """Migration probe only; owns neither transactions nor session lifetime."""

    def __init__(self, session: ExecuteOnly, *, schema: str) -> None:
        self._session = session
        self._table = probe_table(schema)
        self._schema = validate_schema(schema)

    def add(self, probe_id: int, value: str) -> None:
        verify_namespace(self._session, self._schema)
        self._session.execute(
            self._table.insert(), {"probe_id": probe_id, "value": value},
        )


class BaselineRepository:
    def __init__(self, session: ExecuteOnly, *, schema: str) -> None:
        self._session = session
        self._schema = validate_schema(schema)
        self._version = table(
            quoted_name("alembic_version", quote=True), column("version_num", String(32)),
            schema=application_schema(schema),
        )

    def check(self) -> None:
        verify_namespace(self._session, self._schema)
        verify_versions(self._session.connection())
        revision = self._session.execute(select(self._version.c.version_num)).scalar_one()
        if revision != HEAD_REVISION:
            raise SafeError("DATABASE_REVISION_MISMATCH")

