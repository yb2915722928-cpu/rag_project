"""Finite public errors; diagnostic objects must never be serialized or logged."""

MESSAGES = {
    "CONFIGURATION_INVALID": "Invalid PostgreSQL configuration.",
    "DATABASE_VERSION_MISMATCH": "PostgreSQL 18.6 and pgvector 0.8.7 are required.",
    "DATABASE_OPERATION_FAILED": "Database operation failed.",
    "DATABASE_CLEANUP_FAILED": "Database resource cleanup failed; reconcile before retry.",
    "ONLINE_VALIDATION_REQUIRED": "Migration requires an online version check.",
    "RUNTIME_VERSION_MISMATCH": "CPython 3.12.8 is required.",
    "DATABASE_REVISION_MISMATCH": "Database migration revision is not 0003_library_uploads.",
    "DATABASE_NAMESPACE_UNAVAILABLE": "Configured database namespace is unavailable.",
    "STARTUP_DEPENDENCY_UNAVAILABLE": "Required API server dependency is unavailable or incompatible.",
}

# Finite business failures.  These are not runtime/database failures, so they
# keep their own HTTP policy instead of the 503 policy above; both maps are
# projected through the same single public error dictionary.
BUSINESS_MESSAGES = {
    "UPLOAD_CONTENT_CONFLICT": "Uploaded content does not match the accepted input.",
    "UPLOAD_EXPIRED": "The upload operation is no longer executable.",
    "UPLOAD_IN_PROGRESS": "The upload operation is busy or its previous writer is unverified.",
    "ORIGINAL_CAPACITY_EXCEEDED": "Original capacity is insufficient.",
    "FILE_LIMIT_EXCEEDED": "The file exceeds an accepted limit.",
    "CAPACITY_LEDGER_CONFLICT": "Capacity ledger and asset facts disagree; reconcile before retry.",
    "STORAGE_PRESSURE": "Storage pressure blocks new writes.",
    "IDENTITY_UNVERIFIED": "This identity is not verified for the requested action.",
}

# Request-policy failures raised by application services still have to keep
# their finite code through UnitOfWork.  Keeping them out of MESSAGES also
# preserves the existing 503-only test for infrastructure failures.
POLICY_MESSAGES = {
    "AUTH_CHANNEL_CONFLICT": "Conflicting authentication channels.",
    "AUTH_REQUIRED": "Authentication required.",
    "CREDENTIAL_INVALID": "Invalid credentials.",
    "ACTION_FORBIDDEN": "Action unavailable.",
    "RESOURCE_UNAVAILABLE": "Resource unavailable.",
    "VALIDATION_ERROR": "Invalid request.",
    "IDEMPOTENCY_CONFLICT": "Idempotency key conflict.",
    "CONCURRENCY_LIMIT_EXCEEDED": "Concurrency limit exceeded.",
    "REQUEST_BODY_LIMIT_EXCEEDED": "Request body too large.",
}

ALL_MESSAGES = {**MESSAGES, **BUSINESS_MESSAGES, **POLICY_MESSAGES}


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
        if code not in ALL_MESSAGES:
            code = "DATABASE_OPERATION_FAILED"
        self.code = code
        self.diagnostic_cause = diagnostic_cause
        self.cleanup_errors = cleanup_errors
        super().__init__(f"{code}: {ALL_MESSAGES[code]}")


class GuardError(Exception):
    """Finite internal execution guard failure without diagnostic details."""

    def __init__(self, code: str) -> None:
        if code not in GUARD_MESSAGES:
            code = "CALL_STATE_CONFLICT"
        self.code = code
        super().__init__(f"{code}: {GUARD_MESSAGES[code]}")
