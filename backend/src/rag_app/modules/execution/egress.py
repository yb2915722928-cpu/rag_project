"""Framework-free egress values and ports.

This module performs no I/O. It validates wire URLs, applies an exact
host/port profile, and turns one DNS observation into a plan whose later
connections are bound to the addresses approved for this dispatch.

Signed request targets are per-call secrets. They are held in an attribute
that is hidden from the default repr and must not be logged or persisted.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import BinaryIO, Protocol, runtime_checkable


MAX_CONFIG_URL_CODE_POINTS = 2_048
MAX_SIGNED_URL_UTF8_BYTES = 8_192
HTTPS_DEFAULT_PORT = 443

_MAX_REQUEST_HEADERS = 100
_MAX_REQUEST_HEADER_BYTES = 65_536
_MAX_REQUEST_HEADER_VALUE = 8_192
_MAX_AUTHORIZATION_VALUE = 8_192
_MAX_RESPONSE_HEADERS = 100
_MAX_RESPONSE_HEADER_BYTES = 65_536

# Visible ASCII URI characters. Backslash, space, controls, and non-ASCII
# are rejected so the wire request target is exactly the configured value.
_URI_CHARS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "-._~:/?#[]@!$&'()*+,;=%"
)
_URI_TARGET_CHARS = _URI_CHARS - {"#"}
_HEADER_NAME = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")
_DNS_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

_ALLOWED_METHODS = frozenset({"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"})
_FORBIDDEN_REQUEST_HEADERS = frozenset({
    "authorization",
    "proxy-authorization",
    "host",
    "content-length",
    "transfer-encoding",
    "connection",
    "keep-alive",
    "proxy-connection",
    "te",
    "trailer",
    "upgrade",
    "expect",
    "cookie",
})

_DENY_V4 = tuple(ipaddress.ip_network(value) for value in (
    "0.0.0.0/8",
    "100.64.0.0/10",
    "192.0.0.0/24",
    "192.0.2.0/24",
    "192.31.196.0/24",
    "192.52.193.0/24",
    "192.88.99.0/24",
    "192.175.48.0/24",
    "198.18.0.0/15",
    "198.51.100.0/24",
    "203.0.113.0/24",
    "240.0.0.0/4",
    "255.255.255.255/32",
))
_DENY_V6 = tuple(ipaddress.ip_network(value) for value in (
    "::/96",
    "::ffff:0:0:0/96",
    "64:ff9b::/96",
    "64:ff9b:1::/48",
    "100::/64",
    "2001::/23",
    "2001:db8::/32",
    "2002::/16",
    "2620:4f:8000::/48",
    "3fff::/20",
    "5f00::/16",
))
_METADATA_ADDRESSES = frozenset(ipaddress.ip_address(value) for value in (
    "100.100.100.200",
    "168.63.129.16",
    "169.254.169.253",
    "169.254.169.254",
    "169.254.170.2",
    "fd00:ec2::254",
))


class EgressPurpose(StrEnum):
    API = "api"
    UPLOAD = "upload"
    DOWNLOAD = "download"


class AddressFamily(StrEnum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"


class EgressErrorCode(StrEnum):
    CONFIGURATION_INVALID = "CONFIGURATION_INVALID"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"


class EgressFailure(StrEnum):
    URL_TOO_LONG = "url_too_long"
    URL_INVALID = "url_invalid"
    SCHEME_NOT_HTTPS = "scheme_not_https"
    USERINFO_FORBIDDEN = "userinfo_forbidden"
    FRAGMENT_FORBIDDEN = "fragment_forbidden"
    HOST_INVALID = "host_invalid"
    HOST_NOT_ALLOWED = "host_not_allowed"
    PORT_INVALID = "port_invalid"
    PORT_NOT_ALLOWED = "port_not_allowed"
    PROFILE_INVALID = "profile_invalid"
    REQUEST_TARGET_INVALID = "request_target_invalid"
    REQUEST_INVALID = "request_invalid"
    HEADER_INVALID = "header_invalid"
    AUTHORIZATION_INVALID = "authorization_invalid"
    AUTHORIZATION_NOT_ALLOWED = "authorization_not_allowed"
    ADDRESS_INVALID = "address_invalid"
    ADDRESS_UNSAFE = "address_unsafe"
    PLAN_INVALID = "plan_invalid"
    DNS_EMPTY = "dns_empty"
    DNS_UNSAFE = "dns_unsafe"
    DNS_FAILURE = "dns_failure"
    CONNECT_FAILURE = "connect_failure"
    TRANSPORT_FAILURE = "transport_failure"
    TLS_FAILURE = "tls_failure"
    TLS_CONFIGURATION_INVALID = "tls_configuration_invalid"
    TIMEOUT_INVALID = "timeout_invalid"
    ADAPTER_INVALID = "adapter_invalid"
    RESPONSE_INVALID = "response_invalid"
    RESPONSE_TOO_LARGE = "response_too_large"


class EgressError(Exception):
    """Finite egress failure without the URL, secret, or original exception."""

    __slots__ = ("code", "failure")

    def __init__(self, code: EgressErrorCode, failure: EgressFailure) -> None:
        if not isinstance(code, EgressErrorCode) or not isinstance(failure, EgressFailure):
            raise ValueError("invalid egress error")
        self.code = code
        self.failure = failure
        super().__init__(f"{code.value}:{failure.value}")


def _configuration(failure: EgressFailure) -> EgressError:
    return EgressError(EgressErrorCode.CONFIGURATION_INVALID, failure)


def _dependency(failure: EgressFailure) -> EgressError:
    return EgressError(EgressErrorCode.DEPENDENCY_UNAVAILABLE, failure)


def _normalize_host(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > 253:
        raise _configuration(EgressFailure.HOST_INVALID)
    if not all(0x21 <= ord(character) <= 0x7E for character in value):
        raise _configuration(EgressFailure.HOST_INVALID)
    if "%" in value:
        raise _configuration(EgressFailure.HOST_INVALID)

    if ":" in value:
        parsed_v6 = None
        try:
            parsed_v6 = ipaddress.IPv6Address(value)
        except ValueError:
            parsed_v6 = None
        if parsed_v6 is None:
            raise _configuration(EgressFailure.HOST_INVALID)
        return str(parsed_v6)

    if value.endswith("."):
        raise _configuration(EgressFailure.HOST_INVALID)
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        address = None
    if address is not None:
        if address.version != 4:
            raise _configuration(EgressFailure.HOST_INVALID)
        return str(address)

    host = value.lower()
    if any(character in host for character in "\\/@?#[]:"):
        raise _configuration(EgressFailure.HOST_INVALID)
    labels = host.split(".")
    if not labels or any(not _DNS_LABEL.fullmatch(label) for label in labels):
        raise _configuration(EgressFailure.HOST_INVALID)
    return host


def _normalize_port(value: object) -> int:
    if type(value) is not int or not 1 <= value <= 65_535:
        raise _configuration(EgressFailure.PORT_INVALID)
    return value


def _is_uri_text(value: str) -> bool:
    return bool(value) and all(character in _URI_CHARS for character in value)


def _normalize_request_target(value: object) -> str:
    if not isinstance(value, str) or not value.startswith("/"):
        raise _configuration(EgressFailure.REQUEST_TARGET_INVALID)
    try:
        encoded_length = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        encoded_length = -1
    if encoded_length < 0:
        raise _configuration(EgressFailure.REQUEST_TARGET_INVALID)
    if encoded_length > MAX_SIGNED_URL_UTF8_BYTES:
        raise _configuration(EgressFailure.REQUEST_TARGET_INVALID)
    if any(character not in _URI_TARGET_CHARS for character in value):
        raise _configuration(EgressFailure.REQUEST_TARGET_INVALID)
    return value


def _valid_header_name(value: object) -> bool:
    return (
        isinstance(value, str)
        and 0 < len(value) <= 256
        and _HEADER_NAME.fullmatch(value) is not None
    )


def _valid_request_header_value(value: object) -> bool:
    if not isinstance(value, str) or len(value) > _MAX_REQUEST_HEADER_VALUE:
        return False
    if value != value.strip(" \t"):
        return False
    return all(character == "\t" or 0x20 <= ord(character) <= 0x7E for character in value)


def _valid_response_header_value(value: object) -> bool:
    if not isinstance(value, str) or len(value) > _MAX_REQUEST_HEADER_VALUE:
        return False
    for character in value:
        code = ord(character)
        if character == "\t" or 0x20 <= code <= 0x7E or 0x80 <= code <= 0xFF:
            continue
        return False
    return True


@dataclass(frozen=True, slots=True)
class HostPort:
    host: str
    port: int = HTTPS_DEFAULT_PORT

    def __post_init__(self) -> None:
        object.__setattr__(self, "host", _normalize_host(self.host))
        object.__setattr__(self, "port", _normalize_port(self.port))

    @property
    def authority(self) -> str:
        host = f"[{self.host}]" if ":" in self.host else self.host
        return host if self.port == HTTPS_DEFAULT_PORT else f"{host}:{self.port}"


@dataclass(frozen=True, slots=True)
class EgressProfile:
    purpose: EgressPurpose
    allowed_targets: frozenset[HostPort]

    def __post_init__(self) -> None:
        purpose = None
        try:
            purpose = EgressPurpose(self.purpose)
        except (TypeError, ValueError):
            purpose = None
        if purpose is None:
            raise _configuration(EgressFailure.PROFILE_INVALID)
        targets = None
        try:
            targets = frozenset(self.allowed_targets)
        except TypeError:
            targets = None
        if targets is None:
            raise _configuration(EgressFailure.PROFILE_INVALID)
        if not all(isinstance(target, HostPort) for target in targets):
            raise _configuration(EgressFailure.PROFILE_INVALID)
        object.__setattr__(self, "purpose", purpose)
        object.__setattr__(self, "allowed_targets", targets)

    def allows(self, host: str, port: int) -> bool:
        try:
            normalized_host = _normalize_host(host)
            normalized_port = _normalize_port(port)
        except EgressError:
            return False
        return any(
            target.host == normalized_host and target.port == normalized_port
            for target in self.allowed_targets
        )

    def has_host(self, host: str) -> bool:
        try:
            normalized_host = _normalize_host(host)
        except EgressError:
            return False
        return any(target.host == normalized_host for target in self.allowed_targets)


@dataclass(frozen=True, slots=True)
class EgressTarget:
    profile: EgressProfile
    host: str
    port: int
    request_target: str = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.profile, EgressProfile):
            raise _configuration(EgressFailure.PROFILE_INVALID)
        host = _normalize_host(self.host)
        port = _normalize_port(self.port)
        request_target = _normalize_request_target(self.request_target)
        object.__setattr__(self, "host", host)
        object.__setattr__(self, "port", port)
        object.__setattr__(self, "request_target", request_target)
        if not self.profile.allows(host, port):
            failure = (
                EgressFailure.PORT_NOT_ALLOWED
                if self.profile.has_host(host)
                else EgressFailure.HOST_NOT_ALLOWED
            )
            raise _configuration(failure)

    @property
    def authorization_allowed(self) -> bool:
        return self.profile.purpose is EgressPurpose.API

    @property
    def host_header(self) -> str:
        host = f"[{self.host}]" if ":" in self.host else self.host
        return host if self.port == HTTPS_DEFAULT_PORT else f"{host}:{self.port}"


@dataclass(frozen=True, slots=True)
class ResolvedAddress:
    family: AddressFamily
    address: str

    def __post_init__(self) -> None:
        family = None
        try:
            family = AddressFamily(self.family)
        except (TypeError, ValueError):
            family = None
        if family is None:
            raise _configuration(EgressFailure.ADDRESS_INVALID)
        if not isinstance(self.address, str) or not self.address or "%" in self.address:
            raise _configuration(EgressFailure.ADDRESS_INVALID)
        parsed = None
        try:
            parsed = ipaddress.ip_address(self.address)
        except ValueError:
            parsed = None
        if parsed is None:
            raise _configuration(EgressFailure.ADDRESS_INVALID)
        if (parsed.version == 4) != (family is AddressFamily.IPV4):
            raise _configuration(EgressFailure.ADDRESS_INVALID)
        object.__setattr__(self, "family", family)
        object.__setattr__(self, "address", str(parsed))


def is_public_address(address: str) -> bool:
    """Return True only for a globally routable, non-metadata IP literal."""

    if not isinstance(address, str) or not address or "%" in address:
        return False
    try:
        value = ipaddress.ip_address(address)
    except ValueError:
        return False
    if getattr(value, "scope_id", None) is not None:
        return False
    if value.version == 6:
        if value.ipv4_mapped is not None or value.is_site_local:
            return False
        if any(value in network for network in _DENY_V6):
            return False
    else:
        if any(value in network for network in _DENY_V4):
            return False
    if value in _METADATA_ADDRESSES:
        return False
    return not (
        value.is_private
        or value.is_loopback
        or value.is_link_local
        or value.is_reserved
        or value.is_multicast
        or value.is_unspecified
        or not value.is_global
    )


@dataclass(frozen=True, slots=True)
class EgressPlan:
    target: EgressTarget
    addresses: tuple[ResolvedAddress, ...]
    connect_address: ResolvedAddress

    def __post_init__(self) -> None:
        if not isinstance(self.target, EgressTarget):
            raise _configuration(EgressFailure.PLAN_INVALID)
        try:
            addresses = tuple(self.addresses)
        except TypeError:
            addresses = None
        if addresses is None:
            raise _configuration(EgressFailure.PLAN_INVALID)
        if not addresses or not all(
            isinstance(address, ResolvedAddress) for address in addresses
        ):
            raise _configuration(EgressFailure.PLAN_INVALID)
        if any(not is_public_address(address.address) for address in addresses):
            raise _configuration(EgressFailure.ADDRESS_UNSAFE)
        if (
            not isinstance(self.connect_address, ResolvedAddress)
            or self.connect_address not in addresses
        ):
            raise _configuration(EgressFailure.PLAN_INVALID)
        object.__setattr__(self, "addresses", addresses)


@dataclass(frozen=True, slots=True)
class EgressRequest:
    method: str
    headers: tuple[tuple[str, str], ...] = field(default=(), repr=False)
    body: bytes = field(default=b"", repr=False)
    api_authorization: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.method, str):
            raise _configuration(EgressFailure.REQUEST_INVALID)
        method = self.method.upper()
        if method not in _ALLOWED_METHODS:
            raise _configuration(EgressFailure.REQUEST_INVALID)

        try:
            headers = tuple(self.headers)
        except TypeError:
            headers = None
        if headers is None:
            raise _configuration(EgressFailure.HEADER_INVALID)
        if len(headers) > _MAX_REQUEST_HEADERS:
            raise _configuration(EgressFailure.HEADER_INVALID)

        normalized_headers: list[tuple[str, str]] = []
        seen: set[str] = set()
        total_bytes = 0
        for header in headers:
            if not isinstance(header, (tuple, list)) or len(header) != 2:
                raise _configuration(EgressFailure.HEADER_INVALID)
            name, value = header
            if not _valid_header_name(name) or not _valid_request_header_value(value):
                raise _configuration(EgressFailure.HEADER_INVALID)
            lower_name = name.lower()
            if lower_name in _FORBIDDEN_REQUEST_HEADERS or lower_name in seen:
                raise _configuration(EgressFailure.HEADER_INVALID)
            seen.add(lower_name)
            total_bytes += len(name) + len(value)
            if total_bytes > _MAX_REQUEST_HEADER_BYTES:
                raise _configuration(EgressFailure.HEADER_INVALID)
            normalized_headers.append((name, value))

        if not isinstance(self.body, bytes):
            raise _configuration(EgressFailure.REQUEST_INVALID)
        authorization = self.api_authorization
        if authorization is not None:
            if (
                not isinstance(authorization, str)
                or not authorization
                or len(authorization) > _MAX_AUTHORIZATION_VALUE
                or authorization != authorization.strip(" \t")
                or not all(0x20 <= ord(character) <= 0x7E for character in authorization)
            ):
                raise _configuration(EgressFailure.AUTHORIZATION_INVALID)

        object.__setattr__(self, "method", method)
        object.__setattr__(self, "headers", tuple(normalized_headers))


@dataclass(frozen=True, slots=True)
class EgressResponse:
    status: int
    headers: tuple[tuple[str, str], ...] = field(repr=False)
    body: bytes = field(repr=False)

    def __post_init__(self) -> None:
        if type(self.status) is not int or not 200 <= self.status <= 599:
            raise _dependency(EgressFailure.RESPONSE_INVALID)
        try:
            headers = tuple(self.headers)
        except TypeError:
            headers = None
        if headers is None:
            raise _dependency(EgressFailure.RESPONSE_INVALID)
        if len(headers) > _MAX_RESPONSE_HEADERS:
            raise _dependency(EgressFailure.RESPONSE_INVALID)
        normalized: list[tuple[str, str]] = []
        total_bytes = 0
        for header in headers:
            if not isinstance(header, (tuple, list)) or len(header) != 2:
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            name, value = header
            if not _valid_header_name(name) or not _valid_response_header_value(value):
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            total_bytes += len(name) + len(value)
            if total_bytes > _MAX_RESPONSE_HEADER_BYTES:
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            normalized.append((name, value))
        if not isinstance(self.body, bytes):
            raise _dependency(EgressFailure.RESPONSE_INVALID)
        object.__setattr__(self, "headers", tuple(normalized))


@runtime_checkable
class DnsResolver(Protocol):
    def resolve(self, host: str, port: int) -> tuple[ResolvedAddress, ...]:
        ...


@runtime_checkable
class EgressConnection(Protocol):
    selected_address: ResolvedAddress
    server_hostname: str

    def sendall(self, data: bytes) -> None:
        ...

    def makefile(self, mode: str) -> BinaryIO:
        ...

    def close(self) -> None:
        ...


@runtime_checkable
class EgressConnector(Protocol):
    def connect(self, plan: EgressPlan) -> EgressConnection:
        ...


def _parse_port(value: str) -> int:
    if not value or not value.isascii() or not value.isdigit() or len(value) > 5:
        raise _configuration(EgressFailure.PORT_INVALID)
    return _normalize_port(int(value))


def _parse_authority(authority: str) -> tuple[str, int]:
    if authority.startswith("["):
        close = authority.find("]")
        if close < 0:
            raise _configuration(EgressFailure.HOST_INVALID)
        host_text = authority[1:close]
        remainder = authority[close + 1:]
        if not host_text:
            raise _configuration(EgressFailure.HOST_INVALID)
        if not remainder:
            return host_text, HTTPS_DEFAULT_PORT
        if not remainder.startswith(":"):
            raise _configuration(EgressFailure.HOST_INVALID)
        return host_text, _parse_port(remainder[1:])

    if ":" in authority:
        if authority.count(":") != 1:
            raise _configuration(EgressFailure.HOST_INVALID)
        host_text, port_text = authority.split(":", 1)
        if not host_text:
            raise _configuration(EgressFailure.HOST_INVALID)
        return host_text, _parse_port(port_text)
    return authority, HTTPS_DEFAULT_PORT


def _parse_https_url(url: str, profile: EgressProfile) -> EgressTarget:
    if "#" in url:
        raise _configuration(EgressFailure.FRAGMENT_FORBIDDEN)
    if not _is_uri_text(url):
        raise _configuration(EgressFailure.URL_INVALID)

    marker = url.find("://")
    if marker <= 0:
        raise _configuration(EgressFailure.URL_INVALID)
    scheme = url[:marker]
    if (
        not scheme
        or not scheme.isascii()
        or not all(character.isalnum() or character in "+-." for character in scheme)
    ):
        raise _configuration(EgressFailure.URL_INVALID)
    if scheme.lower() != "https":
        raise _configuration(EgressFailure.SCHEME_NOT_HTTPS)

    authority_start = marker + 3
    authority_end = len(url)
    for index in range(authority_start, len(url)):
        if url[index] in "/?":
            authority_end = index
            break
    authority = url[authority_start:authority_end]
    remainder = url[authority_end:]
    if not authority:
        raise _configuration(EgressFailure.HOST_INVALID)
    if "@" in authority:
        raise _configuration(EgressFailure.USERINFO_FORBIDDEN)

    host_text, port = _parse_authority(authority)
    request_target = remainder or "/"
    if request_target.startswith("?"):
        request_target = "/" + request_target
    return EgressTarget(
        profile=profile,
        host=host_text,
        port=port,
        request_target=request_target,
    )


def parse_config_target(url: str, profile: EgressProfile) -> EgressTarget:
    if not isinstance(url, str):
        raise _configuration(EgressFailure.URL_INVALID)
    if len(url) > MAX_CONFIG_URL_CODE_POINTS:
        raise _configuration(EgressFailure.URL_TOO_LONG)
    return _parse_https_url(url, profile)


def parse_signed_target(url: str, profile: EgressProfile) -> EgressTarget:
    if not isinstance(url, str):
        raise _configuration(EgressFailure.URL_INVALID)
    try:
        encoded_length = len(url.encode("utf-8"))
    except UnicodeEncodeError:
        raise _configuration(EgressFailure.URL_INVALID) from None
    if encoded_length > MAX_SIGNED_URL_UTF8_BYTES:
        raise _configuration(EgressFailure.URL_TOO_LONG)
    return _parse_https_url(url, profile)


def resolve_egress_plan(target: EgressTarget, resolver: DnsResolver) -> EgressPlan:
    if not isinstance(target, EgressTarget) or not callable(getattr(resolver, "resolve", None)):
        raise _configuration(EgressFailure.PLAN_INVALID)

    raw = None
    code = None
    failure = None
    try:
        raw = resolver.resolve(target.host, target.port)
    except EgressError as exc:
        code = exc.code
        failure = exc.failure
    except Exception:
        code = EgressErrorCode.DEPENDENCY_UNAVAILABLE
        failure = EgressFailure.DNS_FAILURE
    if code is not None:
        raise EgressError(code, failure) from None

    try:
        candidates = tuple(raw)  # type: ignore[arg-type]
    except Exception:
        candidates = ()
        failed = True
    else:
        failed = False
    if failed:
        raise _dependency(EgressFailure.DNS_FAILURE) from None
    if not candidates:
        raise _dependency(EgressFailure.DNS_EMPTY)

    addresses: list[ResolvedAddress] = []
    seen: set[tuple[AddressFamily, str]] = set()
    for candidate in candidates:
        if not isinstance(candidate, ResolvedAddress):
            raise _dependency(EgressFailure.DNS_FAILURE)
        if not is_public_address(candidate.address):
            raise _dependency(EgressFailure.DNS_UNSAFE)
        try:
            parsed = ipaddress.ip_address(candidate.address)
        except ValueError:
            raise _dependency(EgressFailure.DNS_UNSAFE) from None
        if (parsed.version == 4) != (candidate.family is AddressFamily.IPV4):
            raise _dependency(EgressFailure.DNS_UNSAFE)
        key = (candidate.family, candidate.address)
        if key not in seen:
            seen.add(key)
            addresses.append(candidate)
    if not addresses:
        raise _dependency(EgressFailure.DNS_EMPTY)

    # The addresses were checked above, so the plan can be built directly.
    # Re-validating here would turn a programming defect into a DNS failure.
    return EgressPlan(
        target=target,
        addresses=tuple(addresses),
        connect_address=addresses[0],
    )
