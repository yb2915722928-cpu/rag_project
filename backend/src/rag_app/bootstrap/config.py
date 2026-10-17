from __future__ import annotations

from ipaddress import ip_address

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from rag_app.adapters.postgres import validate_database_url, validate_schema
from rag_app.contracts.errors import SafeError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RAG_", extra="ignore", hide_input_in_errors=True,
    )
    environment: str = "development"
    database_url: SecretStr = SecretStr("postgresql+psycopg://rag@localhost/rag")
    database_schema: str = "public"
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)

    def __init__(self, **values):
        try:
            super().__init__(**values)
        except (ValidationError, ValueError) as exc:
            raise SafeError("CONFIGURATION_INVALID", diagnostic_cause=exc) from None

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value: SecretStr) -> SecretStr:
        validate_database_url(value.get_secret_value())
        return value

    @field_validator("database_schema")
    @classmethod
    def schema_identifier(cls, value: str) -> str:
        return validate_schema(value)

    @field_validator("api_host", mode="before")
    @classmethod
    def api_ip_literal(cls, value: object) -> str:
        if not isinstance(value, str) or len(value) > 45 or "%" in value:
            raise ValueError("API host must be an IP literal.")
        return str(ip_address(value))

    @field_validator("api_port", mode="before")
    @classmethod
    def api_tcp_port(cls, value: object) -> int:
        if isinstance(value, bool):
            raise ValueError("API port must be an integer.")
        if isinstance(value, str):
            if not 1 <= len(value) <= 5 or not value.isascii() or not value.isdecimal():
                raise ValueError("API port must be an integer.")
            return int(value)
        if not isinstance(value, int):
            raise ValueError("API port must be an integer.")
        return value

