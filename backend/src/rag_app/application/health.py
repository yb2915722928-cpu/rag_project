from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatus:
    status: str = "alive"
    service: str = "rag-api"
    check: str = "liveness"

