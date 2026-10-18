from __future__ import annotations

from ipaddress import ip_address
import os

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
    epoch_control_file: str | None = None
    # Upload is an isolated development entry until S1/P0 open production.
    uploads_enabled: bool = False
    upload_root: str | None = None
    upload_max_file_bytes: int = Field(default=0, ge=0, le=8 * 1024**3)
    upload_start_window_s: int = Field(default=900, ge=60, le=86_400)
    upload_total_window_s: int = Field(default=1800, ge=60, le=86_400)
    upload_no_progress_s: int = Field(default=60, ge=5, le=600)
    upload_lease_s: int = Field(default=60, ge=5, le=900)
    upload_renew_s: int = Field(default=10, ge=1, le=300)
    upload_chunk_bytes: int = Field(default=256 * 1024, ge=4096, le=1024**2)
    upload_slot_wait_s: int = Field(default=5, ge=0, le=120)
    upload_stop_grace_s: int = Field(default=15, ge=1, le=300)
    upload_page_bytes: int = Field(default=0, ge=0, le=8 * 1024**3)
    upload_replay_verify_s: int = Field(default=120, ge=1, le=600)
    allowed_origin: str | None = None

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

    @field_validator("epoch_control_file")
    @classmethod
    def epoch_control_path(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if len(value) > 4096 or "\x00" in value:
            raise ValueError("epoch control path is invalid")
        return value

    @field_validator("upload_root")
    @classmethod
    def upload_root_path(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if len(value) > 4096 or "\x00" in value or not os.path.isabs(value):
            raise ValueError("upload root must be an absolute local path")
        return value

    @field_validator("allowed_origin")
    @classmethod
    def exact_origin(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if len(value) > 2048 or "\x00" in value:
            raise ValueError("origin is invalid")
        parts = value.split("://", 1)
        if len(parts) != 2 or parts[0] not in {"http", "https"}:
            raise ValueError("origin must be an exact scheme://host[:port]")
        if not parts[1] or any(character in parts[1] for character in "/?#@"):
            raise ValueError("origin must not contain a path, query or userinfo")
        return value

