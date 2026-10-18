"""Framework-free session/credential value rules for the upload entrypoint.

Only digests are compared; plaintext secrets, CSRF tokens and cookie values
never reach a repository, log or error message.  The adapter stores these
digests and the account/space/KB facts; this module makes no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import re


_OPAQUE = re.compile(r"[A-Za-z0-9_-]{43,128}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")

SESSION_IDLE_LIMIT = 30 * 60
SESSION_ABSOLUTE_LIMIT = 12 * 60 * 60


class AuthenticationError(Exception):
    """Finite identity failure; the boundary maps it to the public policy."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def digest_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_secret(value: object) -> str:
    if not isinstance(value, str) or _OPAQUE.fullmatch(value) is None:
        raise AuthenticationError("CREDENTIAL_INVALID")
    return value


def validate_digest(value: object) -> str:
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        raise AuthenticationError("CREDENTIAL_INVALID")
    return value


def digests_equal(left: str, right: str) -> bool:
    try:
        return hmac.compare_digest(
            validate_digest(left).encode("ascii"),
            validate_digest(right).encode("ascii"),
        )
    except AuthenticationError:
        return False


def check_verified_identity(
    *, account_state: str, verification: str, account_epoch: str,
    current_epoch: str,
) -> None:
    """Recovered or disabled identities are not silently re-admitted."""

    if account_state != "active" or verification != "verified":
        raise AuthenticationError("IDENTITY_UNVERIFIED")
    if account_epoch != current_epoch:
        raise AuthenticationError("CREDENTIAL_INVALID")


def check_session(
    *, session_epoch: str, current_epoch: str, revoked_at: datetime | None,
    idle_expires_at: datetime, absolute_expires_at: datetime, now: datetime,
    account_state: str, verification: str,
) -> None:
    check_verified_identity(
        account_state=account_state, verification=verification,
        account_epoch=session_epoch, current_epoch=current_epoch,
    )
    if revoked_at is not None:
        raise AuthenticationError("CREDENTIAL_INVALID")
    if now >= idle_expires_at or now >= absolute_expires_at:
        raise AuthenticationError("CREDENTIAL_INVALID")


@dataclass(frozen=True, slots=True)
class AuthContext:
    """Server-derived identity for one request; no request field can set it."""

    account_id: str
    session_id: str
    csrf_digest: str
    epoch: str
    channel: str
    space_id: str
    knowledge_base_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.channel not in {"web", "program"}:
            raise AuthenticationError("CREDENTIAL_INVALID")
        if not self.account_id or not self.session_id:
            raise AuthenticationError("CREDENTIAL_INVALID")
        if not isinstance(self.epoch, str) or not 1 <= len(self.epoch) <= 64:
            raise AuthenticationError("CREDENTIAL_INVALID")
        if self.channel == "program":
            # Program credentials are read-only and can never create uploads.
            raise AuthenticationError("ACTION_FORBIDDEN")
        validate_digest(self.csrf_digest)


def check_csrf(context: AuthContext, supplied_token: str | None) -> None:
    """The header carries the raw session-bound token; only its digest is stored."""

    if supplied_token is None or not digests_equal(
        context.csrf_digest, digest_secret(supplied_token),
    ):
        raise AuthenticationError("ACTION_FORBIDDEN")
