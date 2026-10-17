"""Finite public errors; diagnostic objects must never be serialized or logged."""

MESSAGES = {
    "CONFIGURATION_INVALID": "Invalid PostgreSQL configuration.",
    "DATABASE_VERSION_MISMATCH": "PostgreSQL 18.6 and pgvector 0.8.7 are required.",
    "DATABASE_OPERATION_FAILED": "Database operation failed.",
    "DATABASE_CLEANUP_FAILED": "Database resource cleanup failed; reconcile before retry.",
    "ONLINE_VALIDATION_REQUIRED": "Migration requires an online version check.",
    "RUNTIME_VERSION_MISMATCH": "CPython 3.12.8 is required.",
    "DATABASE_REVISION_MISMATCH": "Database migration revision is not 0001_baseline.",
    "DATABASE_NAMESPACE_UNAVAILABLE": "Configured database namespace is unavailable.",
    "STARTUP_DEPENDENCY_UNAVAILABLE": "Required API server dependency is unavailable or incompatible.",
}


class SafeError(Exception):
    def __init__(
        self, code: str, *, diagnostic_cause: BaseException | None = None,
        cleanup_errors: tuple[BaseException, ...] = (),
    ) -> None:
        if code not in MESSAGES:
            code = "DATABASE_OPERATION_FAILED"
        self.code = code
        self.diagnostic_cause = diagnostic_cause
        self.cleanup_errors = cleanup_errors
        super().__init__(f"{code}: {MESSAGES[code]}")
