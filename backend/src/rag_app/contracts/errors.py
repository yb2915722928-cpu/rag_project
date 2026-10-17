"""Finite public errors; diagnostic objects must never be serialized or logged."""

MESSAGES = {
    "CONFIGURATION_INVALID": "Invalid PostgreSQL configuration.",
    "DATABASE_VERSION_MISMATCH": "PostgreSQL 18.6 and pgvector 0.8.7 are required.",
    "DATABASE_OPERATION_FAILED": "Database operation failed.",
    "DATABASE_CLEANUP_FAILED": "Database resource cleanup failed; reconcile before retry.",
    "ONLINE_VALIDATION_REQUIRED": "Migration requires an online version check.",
    "RUNTIME_VERSION_MISMATCH": "CPython 3.12.8 is required.",
    "DATABASE_REVISION_MISMATCH": "Database migration revision is not 0002_isolated_calls.",
    "DATABASE_NAMESPACE_UNAVAILABLE": "Configured database namespace is unavailable.",
    "STARTUP_DEPENDENCY_UNAVAILABLE": "Required API server dependency is unavailable or incompatible.",
}


# Internal guard codes are deliberately separate from public MESSAGES.  They
# never carry provider text, URLs, tokens or SQL and are mapped by the caller
# to the finite public policy at an API boundary.
GUARD_MESSAGES = {
    "EPOCH_CONTROL_MISSING": "The independent epoch control record is missing.",
    "EPOCH_CONTROL_NOT_READ": "The epoch control record was not read in this context.",
    "EPOCH_CONTROL_INVALID": "The independent epoch control record is invalid.",
    "EPOCH_MIRROR_MISSING": "The database epoch mirror is missing.",
    "EPOCH_MIRROR_MISMATCH": "The database epoch mirror contradicts the control record.",
    "CALL_FENCE_STALE": "Execution authority is no longer current.",
    "CALL_NOT_FOUND": "The call is unavailable.",
    "CALL_NOT_SENT": "The call was never authorized to send.",
    "CALL_STATE_CONFLICT": "The call is already in a contradictory terminal state.",
    "CALL_LOCK_ORDER_INVALID": "A lock was acquired out of the supported order.",
    "CALL_CONTEXT_MISSING": "The execution context is unavailable.",
    "CALL_INPUT_INVALID": "The execution call input is invalid.",
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


class GuardError(Exception):
    """Finite internal execution guard failure without diagnostic details."""

    def __init__(self, code: str) -> None:
        if code not in GUARD_MESSAGES:
            code = "CALL_STATE_CONFLICT"
        self.code = code
        super().__init__(f"{code}: {GUARD_MESSAGES[code]}")
