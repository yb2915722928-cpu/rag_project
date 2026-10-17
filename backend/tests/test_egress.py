"""EgressTarget contract tests; all DNS, TLS, and HTTP peers are fakes."""

from __future__ import annotations

import io
import logging
import socket
import ssl
import sys
import traceback

import pytest

from rag_app.adapters.egress import (
    OneShotHttpTransport,
    SystemDnsResolver,
    TlsBoundConnector,
)
from rag_app.modules.execution.egress import (
    AddressFamily,
    EgressError,
    EgressErrorCode,
    EgressFailure,
    EgressPlan,
    EgressProfile,
    EgressPurpose,
    EgressRequest,
    EgressResponse,
    EgressTarget,
    HostPort,
    ResolvedAddress,
    is_public_address,
    parse_config_target,
    parse_signed_target,
    resolve_egress_plan,
)


PUBLIC_V4 = ResolvedAddress(AddressFamily.IPV4, "93.184.216.34")
PUBLIC_V6 = ResolvedAddress(AddressFamily.IPV6, "2606:4700:4700::1111")

API = EgressProfile(
    EgressPurpose.API,
    frozenset({HostPort("api.example.com"), HostPort("api.example.com", 8443)}),
)
UPLOAD = EgressProfile(
    EgressPurpose.UPLOAD,
    frozenset({HostPort("upload.example.com")}),
)
DOWNLOAD = EgressProfile(
    EgressPurpose.DOWNLOAD,
    frozenset({HostPort("download.example.com")}),
)


class _Resolver:
    def __init__(self, result):
        self.result = result
        self.calls: list[tuple[str, int]] = []

    def resolve(self, host: str, port: int):
        self.calls.append((host, port))
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


class _Connection:
    def __init__(self, response: bytes, address: ResolvedAddress, hostname: str):
        self.selected_address = address
        self.server_hostname = hostname
        self.sent: list[bytes] = []
        self.response = response
        self.closed = 0
        self._stream = io.BytesIO(response)

    def sendall(self, data: bytes) -> None:
        self.sent.append(bytes(data))

    def makefile(self, mode: str):
        assert mode == "rb"
        return self._stream

    def close(self) -> None:
        self.closed += 1


class _Connector:
    def __init__(self, response: bytes = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok"):
        self.response = response
        self.plans: list[EgressPlan] = []
        self.connections: list[_Connection] = []

    def connect(self, plan: EgressPlan) -> _Connection:
        self.plans.append(plan)
        connection = _Connection(self.response, plan.connect_address, plan.target.host)
        self.connections.append(connection)
        return connection


class _FailingConnection(_Connection):
    def sendall(self, data: bytes) -> None:
        raise RuntimeError("SECRET_SENDALL_SENTINEL https://api.example.com/?token=SECRET_SENDALL_SENTINEL")


class _FailingConnector(_Connector):
    def connect(self, plan: EgressPlan) -> _Connection:
        self.plans.append(plan)
        connection = _FailingConnection(
            b"", plan.connect_address, plan.target.host,
        )
        self.connections.append(connection)
        return connection


class _FakeSocket:
    def __init__(self, family: int, *, connect_error: BaseException | None = None):
        self.family = family
        self.connect_error = connect_error
        self.connect_calls: list[tuple[str, int]] = []
        self.timeout = None
        self.closed = 0

    def settimeout(self, value: float) -> None:
        self.timeout = value

    def connect(self, address: tuple[str, int]) -> None:
        self.connect_calls.append(address)
        if self.connect_error is not None:
            raise self.connect_error

    def close(self) -> None:
        self.closed += 1


class _FakeWrapped:
    def __init__(self) -> None:
        self.sent: list[bytes] = []
        self.closed = 0

    def sendall(self, data: bytes) -> None:
        self.sent.append(bytes(data))

    def makefile(self, mode: str):
        return io.BytesIO(b"")

    def close(self) -> None:
        self.closed += 1


class _FakeContext:
    def __init__(
        self,
        *,
        check_hostname: bool = True,
        verify_mode=ssl.CERT_REQUIRED,
        wrap_error: BaseException | None = None,
    ) -> None:
        self.check_hostname = check_hostname
        self.verify_mode = verify_mode
        self.wrap_error = wrap_error
        self.wrap_calls: list[tuple[object, str, bool]] = []
        self.wrapped = _FakeWrapped()

    def wrap_socket(
        self,
        sock,
        *,
        server_hostname: str | None = None,
        do_handshake_on_connect: bool = True,
    ):
        self.wrap_calls.append((sock, server_hostname, do_handshake_on_connect))
        if self.wrap_error is not None:
            raise self.wrap_error
        return self.wrapped


def _api_target() -> EgressTarget:
    return parse_config_target("https://api.example.com/v1/items", API)


def _api_plan(addresses=(PUBLIC_V4,)) -> EgressPlan:
    return resolve_egress_plan(_api_target(), _Resolver(tuple(addresses)))


def _send(
    response: bytes,
    *,
    method: str = "GET",
    max_response_bytes: int = 1_048_576,
    request: EgressRequest | None = None,
):
    connector = _Connector(response)
    transport = OneShotHttpTransport(connector, max_response_bytes=max_response_bytes)
    result = transport.send(_api_plan(), request or EgressRequest(method))
    return result, connector


def _error_text(exc: BaseException) -> str:
    """Text an operator or log sink could see, including traceback chain."""

    try:
        rendered = "".join(traceback.format_exception(exc))
    except Exception:
        rendered = ""
    return " | ".join((
        str(exc),
        repr(exc),
        repr(exc.args),
        rendered,
        repr(getattr(exc, "code", None)),
        repr(getattr(exc, "failure", None)),
    ))


# --------------------------------------------------------------------------
# URL parsing and exact allowlists


def test_profile_is_an_exact_host_port_allowlist():
    target = parse_config_target("https://API.EXAMPLE.COM:8443/v1/items?x=1", API)
    assert target.host == "api.example.com"
    assert target.port == 8443
    assert target.request_target == "/v1/items?x=1"

    cases = (
        ("https://api.example.com.evil.test/v1", EgressFailure.HOST_NOT_ALLOWED),
        ("https://evil-api.example.com/v1", EgressFailure.HOST_NOT_ALLOWED),
        ("https://api.example.com:444/v1", EgressFailure.PORT_NOT_ALLOWED),
        ("https://api.example.com:80/v1", EgressFailure.PORT_NOT_ALLOWED),
    )
    for url, failure in cases:
        with pytest.raises(EgressError) as caught:
            parse_config_target(url, API)
        assert caught.value.code is EgressErrorCode.CONFIGURATION_INVALID
        assert caught.value.failure is failure


def test_signed_query_is_preserved_verbatim():
    url = (
        "https://upload.example.com/bucket/key"
        "?X-Amz-Signature=ab%2Fcd+ef"
        "&X-Amz-Credential=A%2FB"
        "&empty=&flag"
        "&X-Amz-Signature=duplicate"
    )
    target = parse_signed_target(url, UPLOAD)
    assert target.request_target == (
        "/bucket/key?X-Amz-Signature=ab%2Fcd+ef"
        "&X-Amz-Credential=A%2FB"
        "&empty=&flag"
        "&X-Amz-Signature=duplicate"
    )
    assert "X-Amz-Signature" not in repr(target)
    assert "ab%2Fcd+ef" not in repr(target)


def test_empty_path_and_trailing_question_mark_are_preserved():
    assert parse_config_target(
        "https://api.example.com", API,
    ).request_target == "/"
    assert parse_config_target(
        "https://api.example.com?x=1", API,
    ).request_target == "/?x=1"
    assert parse_signed_target(
        "https://upload.example.com/key?", UPLOAD,
    ).request_target == "/key?"
    assert parse_signed_target(
        "https://upload.example.com/key?x=%2f", UPLOAD,
    ).request_target == "/key?x=%2f"


def test_config_url_limit_is_2048_code_points():
    prefix = "https://api.example.com/"
    limit = prefix + "a" * (2_048 - len(prefix))
    assert len(limit) == 2_048
    target = parse_config_target(limit, API)
    assert target.request_target == "/" + "a" * (2_048 - len(prefix))

    with pytest.raises(EgressError) as caught:
        parse_config_target(limit + "a", API)
    assert caught.value.failure is EgressFailure.URL_TOO_LONG


def test_signed_url_limit_is_8192_utf8_bytes():
    prefix = "https://upload.example.com/"
    limit = prefix + "b" * (8_192 - len(prefix))
    assert len(limit.encode("utf-8")) == 8_192
    target = parse_signed_target(limit, UPLOAD)
    assert target.request_target == "/" + "b" * (8_192 - len(prefix))

    with pytest.raises(EgressError) as caught:
        parse_signed_target(limit + "b", UPLOAD)
    assert caught.value.failure is EgressFailure.URL_TOO_LONG


def test_non_ascii_wire_text_is_rejected_without_implicit_encoding():
    for url in (
        "https://api.example.com/m\u00fcnich",
        "https://m\u00fcnich.example.com/v1",
        "https://api.example.com/v1?q=\u00e9",
    ):
        with pytest.raises(EgressError) as caught:
            parse_signed_target(url, UPLOAD if "upload" in url else API)
        if "m\u00fcnich" in url:
            assert caught.value.failure is EgressFailure.URL_INVALID
        else:
            assert caught.value.failure in {
                EgressFailure.URL_INVALID,
                EgressFailure.HOST_NOT_ALLOWED,
            }


@pytest.mark.parametrize(
    ("url", "failure"),
    (
        ("http://api.example.com/v1", EgressFailure.SCHEME_NOT_HTTPS),
        ("ftp://api.example.com/v1", EgressFailure.SCHEME_NOT_HTTPS),
        ("https://user:pass@api.example.com/v1", EgressFailure.USERINFO_FORBIDDEN),
        ("https://api.example.com/v1#fragment", EgressFailure.FRAGMENT_FORBIDDEN),
        ("https://api.example.com/v1#", EgressFailure.FRAGMENT_FORBIDDEN),
        ("https:///v1", EgressFailure.HOST_INVALID),
        ("https://api.example.com:0/v1", EgressFailure.PORT_INVALID),
        ("https://api.example.com:65536/v1", EgressFailure.PORT_INVALID),
        ("https://api.example.com:/v1", EgressFailure.PORT_INVALID),
        ("https://api.example.com:abc/v1", EgressFailure.PORT_INVALID),
        ("https://api.example.com./v1", EgressFailure.HOST_INVALID),
        ("https://api example.com/v1", EgressFailure.URL_INVALID),
        ("https://api.example.com\\v1", EgressFailure.URL_INVALID),
        ("https://api.example.com/v1?x=<", EgressFailure.URL_INVALID),
        ("https://api.example.com/v1\nX: y", EgressFailure.URL_INVALID),
    ),
)
def test_invalid_wire_urls_fail_before_any_io(url, failure):
    with pytest.raises(EgressError) as caught:
        parse_config_target(url, API)
    assert caught.value.code is EgressErrorCode.CONFIGURATION_INVALID
    assert caught.value.failure is failure


def test_ipv6_literal_host_and_host_header():
    profile = EgressProfile(
        EgressPurpose.API,
        frozenset({HostPort("2606:4700:4700::1111")}),
    )
    target = parse_config_target("https://[2606:4700:4700::1111]/v1", profile)
    assert target.host == "2606:4700:4700::1111"
    assert target.host_header == "[2606:4700:4700::1111]"

    profile = EgressProfile(
        EgressPurpose.API,
        frozenset({HostPort("2606:4700:4700::1111", 8443)}),
    )
    target = parse_config_target(
        "https://[2606:4700:4700::1111]:8443/v1", profile,
    )
    assert target.host_header == "[2606:4700:4700::1111]:8443"


def test_profile_and_address_values_reject_invalid_inputs():
    with pytest.raises(EgressError) as caught:
        HostPort("bad host")
    assert caught.value.failure is EgressFailure.HOST_INVALID
    with pytest.raises(EgressError) as caught:
        HostPort("api.example.com", True)
    assert caught.value.failure is EgressFailure.PORT_INVALID
    with pytest.raises(EgressError) as caught:
        EgressProfile("bogus", frozenset())
    assert caught.value.failure is EgressFailure.PROFILE_INVALID
    with pytest.raises(EgressError) as caught:
        EgressProfile(EgressPurpose.API, frozenset({object()}))
    assert caught.value.failure is EgressFailure.PROFILE_INVALID
    with pytest.raises(EgressError) as caught:
        ResolvedAddress(AddressFamily.IPV4, "2606:4700:4700::1111")
    assert caught.value.failure is EgressFailure.ADDRESS_INVALID
    with pytest.raises(EgressError) as caught:
        ResolvedAddress("ipv9", "8.8.8.8")
    assert caught.value.failure is EgressFailure.ADDRESS_INVALID


# --------------------------------------------------------------------------
# DNS validation


def test_mixed_a_and_aaaa_are_all_retained_and_validated():
    resolver = _Resolver((PUBLIC_V4, PUBLIC_V6))
    plan = resolve_egress_plan(_api_target(), resolver)
    assert plan.addresses == (PUBLIC_V4, PUBLIC_V6)
    assert plan.connect_address == PUBLIC_V4
    assert resolver.calls == [("api.example.com", 443)]


def test_duplicate_dns_results_are_collapsed():
    resolver = _Resolver([PUBLIC_V4, PUBLIC_V4, PUBLIC_V6])
    plan = resolve_egress_plan(_api_target(), resolver)
    assert plan.addresses == (PUBLIC_V4, PUBLIC_V6)


@pytest.mark.parametrize(
    ("family", "address"),
    (
        (AddressFamily.IPV4, "0.0.0.0"),
        (AddressFamily.IPV4, "10.0.0.1"),
        (AddressFamily.IPV4, "100.64.0.1"),
        (AddressFamily.IPV4, "127.0.0.1"),
        (AddressFamily.IPV4, "169.254.169.254"),
        (AddressFamily.IPV4, "172.16.0.1"),
        (AddressFamily.IPV4, "192.0.2.1"),
        (AddressFamily.IPV4, "192.31.196.1"),
        (AddressFamily.IPV4, "192.52.193.1"),
        (AddressFamily.IPV4, "192.88.99.1"),
        (AddressFamily.IPV4, "192.175.48.1"),
        (AddressFamily.IPV4, "198.18.0.1"),
        (AddressFamily.IPV4, "198.51.100.1"),
        (AddressFamily.IPV4, "203.0.113.1"),
        (AddressFamily.IPV4, "224.0.0.1"),
        (AddressFamily.IPV4, "240.0.0.1"),
        (AddressFamily.IPV4, "255.255.255.255"),
        (AddressFamily.IPV4, "100.100.100.200"),
        (AddressFamily.IPV4, "168.63.129.16"),
        (AddressFamily.IPV6, "::"),
        (AddressFamily.IPV6, "::1"),
        (AddressFamily.IPV6, "::8.8.8.8"),
        (AddressFamily.IPV6, "::ffff:8.8.8.8"),
        (AddressFamily.IPV6, "::ffff:0:8.8.8.8"),
        (AddressFamily.IPV6, "::ffff:0:127.0.0.1"),
        (AddressFamily.IPV6, "::ffff:0:8.8.8.8"),
        (AddressFamily.IPV6, "64:ff9b::1"),
        (AddressFamily.IPV6, "64:ff9b:1::1"),
        (AddressFamily.IPV6, "100::1"),
        (AddressFamily.IPV6, "2001:db8::1"),
        (AddressFamily.IPV6, "2002::1"),
        (AddressFamily.IPV6, "2620:4f:8000::1"),
        (AddressFamily.IPV6, "3fff::1"),
        (AddressFamily.IPV6, "5f00::1"),
        (AddressFamily.IPV6, "fc00::1"),
        (AddressFamily.IPV6, "fd00:ec2::254"),
        (AddressFamily.IPV6, "fe80::1"),
        (AddressFamily.IPV6, "ff02::1"),
    ),
)
def test_any_unsafe_dns_address_blocks_the_whole_dispatch(family, address):
    unsafe = ResolvedAddress(family, address)
    resolver = _Resolver((PUBLIC_V4, unsafe))
    with pytest.raises(EgressError) as caught:
        resolve_egress_plan(_api_target(), resolver)
    assert caught.value.code is EgressErrorCode.DEPENDENCY_UNAVAILABLE
    assert caught.value.failure is EgressFailure.DNS_UNSAFE


def test_empty_dns_result_fails_closed():
    with pytest.raises(EgressError) as caught:
        resolve_egress_plan(_api_target(), _Resolver(()))
    assert caught.value.code is EgressErrorCode.DEPENDENCY_UNAVAILABLE
    assert caught.value.failure is EgressFailure.DNS_EMPTY


@pytest.mark.parametrize("result", (None, "8.8.8.8", (object(),)))
def test_malformed_dns_result_fails_closed(result):
    with pytest.raises(EgressError) as caught:
        resolve_egress_plan(_api_target(), _Resolver(result))
    assert caught.value.code is EgressErrorCode.DEPENDENCY_UNAVAILABLE
    assert caught.value.failure in {
        EgressFailure.DNS_FAILURE,
        EgressFailure.DNS_EMPTY,
    }


def test_plan_keeps_the_first_verified_address_and_never_resolves_again():
    class _ChangingResolver:
        def __init__(self):
            self.calls = 0

        def resolve(self, host, port):
            self.calls += 1
            if self.calls == 1:
                return (PUBLIC_V4,)
            return (ResolvedAddress(AddressFamily.IPV4, "127.0.0.1"),)

    resolver = _ChangingResolver()
    plan = resolve_egress_plan(_api_target(), resolver)
    assert resolver.calls == 1
    assert plan.connect_address == PUBLIC_V4

    sock = _FakeSocket(socket.AF_INET)
    connector = TlsBoundConnector(
        ssl_context=_FakeContext(), socket_factory=lambda family: sock,
    )
    connector.connect(plan)
    assert sock.connect_calls == [("93.184.216.34", 443)]
    assert resolver.calls == 1


def test_plan_requires_a_verified_member_as_connect_address():
    with pytest.raises(EgressError) as caught:
        EgressPlan(_api_target(), (PUBLIC_V4,), PUBLIC_V6)
    assert caught.value.failure is EgressFailure.PLAN_INVALID


# --------------------------------------------------------------------------
# Bound TLS connection and one-shot HTTP transport


def test_connector_connects_only_to_the_verified_ip_and_keeps_hostname():
    context = _FakeContext()
    created: list[_FakeSocket] = []

    def factory(family):
        sock = _FakeSocket(
            socket.AF_INET if family is AddressFamily.IPV4 else socket.AF_INET6,
        )
        created.append(sock)
        return sock

    connector = TlsBoundConnector(
        timeout_seconds=5, ssl_context=context, socket_factory=factory,
    )
    target = parse_config_target("https://api.example.com:8443/v1", API)
    plan = resolve_egress_plan(target, _Resolver((PUBLIC_V4, PUBLIC_V6)))
    bound = connector.connect(plan)

    assert created[0].connect_calls == [("93.184.216.34", 8443)]
    assert created[0].timeout == 5.0
    assert context.wrap_calls == [(created[0], "api.example.com", True)]
    assert bound.selected_address == PUBLIC_V4
    assert bound.server_hostname == "api.example.com"


def test_connector_uses_ipv6_socket_family_for_ipv6_plan():
    context = _FakeContext()
    created: list[_FakeSocket] = []

    def factory(family):
        assert family is AddressFamily.IPV6
        sock = _FakeSocket(socket.AF_INET6)
        created.append(sock)
        return sock

    target = parse_config_target("https://api.example.com:8443/v1", API)
    plan = resolve_egress_plan(target, _Resolver((PUBLIC_V6,)))
    TlsBoundConnector(
        ssl_context=context, socket_factory=factory,
    ).connect(plan)

    assert created[0].connect_calls == [("2606:4700:4700::1111", 8443)]


def test_connector_rejects_insecure_tls_context_and_invalid_timeouts():
    with pytest.raises(EgressError) as caught:
        TlsBoundConnector(ssl_context=_FakeContext(check_hostname=False))
    assert caught.value.failure is EgressFailure.TLS_CONFIGURATION_INVALID
    with pytest.raises(EgressError) as caught:
        TlsBoundConnector(ssl_context=_FakeContext(verify_mode=ssl.CERT_NONE))
    assert caught.value.failure is EgressFailure.TLS_CONFIGURATION_INVALID

    for timeout in (0, -1, True, "10", float("nan"), float("inf")):
        with pytest.raises(EgressError) as caught:
            TlsBoundConnector(timeout_seconds=timeout, ssl_context=_FakeContext())
        assert caught.value.failure is EgressFailure.TIMEOUT_INVALID

    with pytest.raises(EgressError) as caught:
        TlsBoundConnector(ssl_context=_FakeContext(), socket_factory=object())
    assert caught.value.failure is EgressFailure.ADAPTER_INVALID

    # Default construction must not disable certificate or hostname checks.
    TlsBoundConnector()


def test_connector_connect_failure_is_finite_and_closes_socket():
    sentinel = "SECRET_CONNECT_SENTINEL"
    sock = _FakeSocket(
        socket.AF_INET,
        connect_error=RuntimeError(
            f"{sentinel} https://api.example.com/?token={sentinel}"
        ),
    )
    connector = TlsBoundConnector(
        ssl_context=_FakeContext(), socket_factory=lambda family: sock,
    )
    with pytest.raises(EgressError) as caught:
        connector.connect(_api_plan())
    exc = caught.value
    assert exc.code is EgressErrorCode.DEPENDENCY_UNAVAILABLE
    assert exc.failure is EgressFailure.CONNECT_FAILURE
    assert sock.closed == 1
    assert sentinel not in _error_text(exc)


def test_connector_wrap_failure_is_finite_and_closes_raw_socket():
    sentinel = "SECRET_TLS_SENTINEL"
    sock = _FakeSocket(socket.AF_INET)
    context = _FakeContext(
        wrap_error=RuntimeError(
            f"{sentinel} https://api.example.com/?token={sentinel}"
        ),
    )
    connector = TlsBoundConnector(
        ssl_context=context, socket_factory=lambda family: sock,
    )
    with pytest.raises(EgressError) as caught:
        connector.connect(_api_plan())
    exc = caught.value
    assert exc.code is EgressErrorCode.DEPENDENCY_UNAVAILABLE
    assert exc.failure is EgressFailure.TLS_FAILURE
    assert sock.closed == 1
    assert sentinel not in _error_text(exc)


def test_connector_socket_factory_failure_is_finite():
    sentinel = "SECRET_FACTORY_SENTINEL"

    def factory(family):
        raise RuntimeError(f"{sentinel} https://api.example.com/?token={sentinel}")

    connector = TlsBoundConnector(
        ssl_context=_FakeContext(), socket_factory=factory,
    )
    with pytest.raises(EgressError) as caught:
        connector.connect(_api_plan())
    exc = caught.value
    assert exc.failure is EgressFailure.CONNECT_FAILURE
    assert sentinel not in _error_text(exc)


def test_transport_preserves_target_host_and_api_only_authorization():
    connector = _Connector(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
    target = parse_signed_target(
        "https://api.example.com/v1/items"
        "?X-Amz-Signature=ab%2Fcd+ef&dup=1&dup=2",
        API,
    )
    plan = resolve_egress_plan(target, _Resolver((PUBLIC_V4,)))
    response = OneShotHttpTransport(connector).send(
        plan,
        EgressRequest(
            "GET",
            headers=(("Accept", "application/json"),),
            api_authorization="Bearer api-sentinel",
        ),
    )

    assert response.status == 200
    assert response.body == b"ok"
    raw = connector.connections[0].sent[0]
    assert raw.startswith(
        b"GET /v1/items?X-Amz-Signature=ab%2Fcd+ef&dup=1&dup=2 HTTP/1.1\r\n"
    )
    assert b"\r\nHost: api.example.com\r\n" in raw
    assert b"\r\nAccept: application/json\r\n" in raw
    assert b"\r\nAuthorization: Bearer api-sentinel\r\n" in raw
    assert b"\r\nContent-Length: 0\r\n" in raw
    assert raw.endswith(b"\r\n\r\n")
    assert connector.connections[0].closed == 1
    assert len(connector.plans) == 1


def test_host_header_keeps_original_port_and_ipv6_brackets():
    profile = EgressProfile(
        EgressPurpose.UPLOAD,
        frozenset({HostPort("2606:4700:4700::1111", 8443)}),
    )
    target = parse_config_target(
        "https://[2606:4700:4700::1111]:8443/key", profile,
    )
    plan = resolve_egress_plan(target, _Resolver((PUBLIC_V6,)))
    connector = _Connector(b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n")
    OneShotHttpTransport(connector).send(plan, EgressRequest("PUT", body=b"data"))

    raw = connector.connections[0].sent[0]
    assert b"\r\nHost: [2606:4700:4700::1111]:8443\r\n" in raw
    assert b"\r\nContent-Length: 4\r\n" in raw
    assert raw.endswith(b"data")


@pytest.mark.parametrize("status", (301, 302, 303, 307, 308))
def test_transport_returns_redirect_without_following_or_retrying(status):
    response = (
        f"HTTP/1.1 {status} Redirect\r\n"
        "Location: https://evil.example/steal\r\n"
        "Content-Length: 0\r\n\r\n"
    ).encode("ascii")
    connector = _Connector(response)
    result = OneShotHttpTransport(connector).send(_api_plan(), EgressRequest("GET"))

    assert result.status == status
    assert len(connector.plans) == 1
    assert len(connector.connections) == 1
    assert b"evil.example" not in connector.connections[0].sent[0]


@pytest.mark.parametrize(
    ("profile", "url"),
    (
        (UPLOAD, "https://upload.example.com/key"),
        (DOWNLOAD, "https://download.example.com/key"),
    ),
)
def test_api_authorization_is_rejected_for_upload_and_download(profile, url):
    connector = _Connector()
    target = parse_config_target(url, profile)
    plan = resolve_egress_plan(target, _Resolver((PUBLIC_V4,)))
    with pytest.raises(EgressError) as caught:
        OneShotHttpTransport(connector).send(
            plan, EgressRequest("PUT", api_authorization="Bearer api-sentinel"),
        )
    assert caught.value.failure is EgressFailure.AUTHORIZATION_NOT_ALLOWED
    assert connector.plans == []


@pytest.mark.parametrize(
    "name",
    (
        "Authorization",
        "authorization",
        "Proxy-Authorization",
        "Host",
        "Content-Length",
        "Transfer-Encoding",
        "Connection",
        "Expect",
        "Cookie",
    ),
)
def test_reserved_request_headers_cannot_bypass_the_credential_boundary(name):
    with pytest.raises(EgressError) as caught:
        EgressRequest("GET", headers=((name, "x"),))
    assert caught.value.failure is EgressFailure.HEADER_INVALID


def test_duplicate_and_injected_request_headers_are_rejected():
    with pytest.raises(EgressError) as caught:
        EgressRequest(
            "GET", headers=(("X-Test", "a"), ("x-test", "b")),
        )
    assert caught.value.failure is EgressFailure.HEADER_INVALID
    with pytest.raises(EgressError) as caught:
        EgressRequest("GET", headers=(("X-Test", "a\r\nX-Evil: b"),))
    assert caught.value.failure is EgressFailure.HEADER_INVALID
    with pytest.raises(EgressError) as caught:
        EgressRequest("GET", headers=(("X-Test", " leading"),))
    assert caught.value.failure is EgressFailure.HEADER_INVALID
    with pytest.raises(EgressError) as caught:
        EgressRequest("TRACE")
    assert caught.value.failure is EgressFailure.REQUEST_INVALID
    with pytest.raises(EgressError) as caught:
        EgressRequest("GET", body="text")
    assert caught.value.failure is EgressFailure.REQUEST_INVALID
    with pytest.raises(EgressError) as caught:
        EgressRequest("GET", api_authorization="")
    assert caught.value.failure is EgressFailure.AUTHORIZATION_INVALID
    with pytest.raises(EgressError) as caught:
        EgressRequest("GET", api_authorization="Bearer\r\nX: y")
    assert caught.value.failure is EgressFailure.AUTHORIZATION_INVALID


@pytest.mark.parametrize(
    ("response", "method", "expected"),
    (
        (
            b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello",
            "GET",
            b"hello",
        ),
        (
            b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n"
            b"5\r\nhello\r\n0\r\n\r\n",
            "GET",
            b"hello",
        ),
        (b"HTTP/1.1 200 OK\r\n\r\nhello", "GET", b"hello"),
        (b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n", "HEAD", b""),
        (b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n", "GET", b""),
        (b"HTTP/1.1 205 Reset Content\r\nContent-Length: 0\r\n\r\n", "GET", b""),
        (b"HTTP/1.1 304 Not Modified\r\nContent-Length: 0\r\n\r\n", "GET", b""),
    ),
)
def test_transport_reads_bounded_response_bodies(response, method, expected):
    result, connector = _send(response, method=method)
    assert result.body == expected
    assert connector.connections[0].closed == 1


def test_transport_rejects_oversized_and_malformed_responses():
    cases = (
        (
            b"HTTP/1.1 200 OK\r\nContent-Length: 11\r\n\r\n",
            EgressFailure.RESPONSE_TOO_LARGE,
            10,
        ),
        (
            b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n"
            b"b\r\nhello world\r\n0\r\n\r\n",
            EgressFailure.RESPONSE_TOO_LARGE,
            10,
        ),
        (
            b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhi",
            EgressFailure.RESPONSE_INVALID,
            1_048_576,
        ),
        (
            b"HTTP/1.1 200 OK\r\nContent-Length: 1\r\n"
            b"Content-Length: 1\r\n\r\nx",
            EgressFailure.RESPONSE_INVALID,
            1_048_576,
        ),
        (
            b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n"
            b"Content-Length: 1\r\n\r\n0\r\n\r\n",
            EgressFailure.RESPONSE_INVALID,
            1_048_576,
        ),
        (b"garbage\r\n", EgressFailure.RESPONSE_INVALID, 1_048_576),
        (
            b"HTTP/1.1 200 OK\r\nBad Header: x\r\nContent-Length: 0\r\n\r\n",
            EgressFailure.RESPONSE_INVALID,
            1_048_576,
        ),
        (
            b"HTTP/1.1 199 Early\r\nContent-Length: 0\r\n\r\n",
            EgressFailure.RESPONSE_INVALID,
            1_048_576,
        ),
        (
            b"HTTP/1.1 600 Late\r\nContent-Length: 0\r\n\r\n",
            EgressFailure.RESPONSE_INVALID,
            1_048_576,
        ),
    )
    for response, failure, limit in cases:
        connector = _Connector(response)
        transport = OneShotHttpTransport(connector, max_response_bytes=limit)
        with pytest.raises(EgressError) as caught:
            transport.send(_api_plan(), EgressRequest("GET"))
        assert caught.value.code is EgressErrorCode.DEPENDENCY_UNAVAILABLE
        assert caught.value.failure is failure
        assert connector.connections[0].closed == 1


def test_transport_closes_connection_when_sending_fails():
    connector = _FailingConnector()
    with pytest.raises(EgressError) as caught:
        OneShotHttpTransport(connector).send(_api_plan(), EgressRequest("GET"))
    exc = caught.value
    assert exc.failure is EgressFailure.TRANSPORT_FAILURE
    assert connector.connections[0].closed == 1
    assert "SECRET_SENDALL_SENTINEL" not in _error_text(exc)


def test_transport_constructor_rejects_invalid_connector_and_bounds():
    with pytest.raises(EgressError) as caught:
        OneShotHttpTransport(object())
    assert caught.value.failure is EgressFailure.ADAPTER_INVALID
    for value in (0, -1, True, 67_108_865):
        with pytest.raises(EgressError) as caught:
            OneShotHttpTransport(_Connector(), max_response_bytes=value)
        assert caught.value.failure is EgressFailure.ADAPTER_INVALID


def test_response_and_request_repr_hide_headers_bodies_and_secrets():
    response = EgressResponse(
        200,
        (("Set-Cookie", "secret-cookie"),),
        b"secret-body",
    )
    assert "secret-cookie" not in repr(response)
    assert "secret-body" not in repr(response)

    request = EgressRequest(
        "GET",
        headers=(("X-Secret", "secret-header"),),
        body=b"secret-body",
        api_authorization="Bearer secret-auth",
    )
    rendered = repr(request)
    for value in ("secret-header", "secret-body", "secret-auth"):
        assert value not in rendered


# --------------------------------------------------------------------------
# System resolver fake and secret hygiene


def test_system_resolver_collects_all_a_and_aaaa_and_deduplicates(monkeypatch):
    records = [
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("93.184.216.34", 443)),
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("93.184.216.34", 443)),
        (
            socket.AF_INET6,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            ("2606:4700:4700::1111", 443, 0, 0),
        ),
    ]
    calls = []

    def fake_getaddrinfo(host, port, *, family=0, type=0, proto=0, flags=0):
        calls.append((host, port, family, type, proto, flags))
        return records

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    result = SystemDnsResolver().resolve("api.example.com", 443)
    assert result == (PUBLIC_V4, PUBLIC_V6)
    assert calls == [(
        "api.example.com",
        443,
        socket.AF_UNSPEC,
        socket.SOCK_STREAM,
        socket.IPPROTO_TCP,
        0,
    )]


def test_system_resolver_failure_is_finite(monkeypatch):
    sentinel = "SECRET_DNS_SENTINEL"

    def fake_getaddrinfo(*args, **kwargs):
        raise OSError(f"{sentinel} https://api.example.com/?token={sentinel}")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    with pytest.raises(EgressError) as caught:
        SystemDnsResolver().resolve("api.example.com", 443)
    exc = caught.value
    assert exc.failure is EgressFailure.DNS_FAILURE
    assert sentinel not in _error_text(exc)


def test_system_resolver_rejects_a_non_ip_result(monkeypatch):
    def fake_getaddrinfo(host, port, *, family=0, type=0, proto=0, flags=0):
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("not-an-ip", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    with pytest.raises(EgressError) as caught:
        SystemDnsResolver().resolve("api.example.com", 443)
    assert caught.value.failure is EgressFailure.DNS_FAILURE


def test_dns_exception_never_renders_the_original_secret(caplog):
    sentinel = "SECRET_DNS_RENDER_SENTINEL"
    resolver = _Resolver(
        RuntimeError(f"{sentinel} https://api.example.com/?token={sentinel}"),
    )
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(EgressError) as caught:
            resolve_egress_plan(_api_target(), resolver)
    exc = caught.value
    assert exc.code is EgressErrorCode.DEPENDENCY_UNAVAILABLE
    assert exc.failure is EgressFailure.DNS_FAILURE
    assert sentinel not in str(exc)
    assert sentinel not in repr(exc)
    assert sentinel not in _error_text(exc)
    assert sentinel not in caplog.text


def test_signed_url_failure_never_renders_the_secret(caplog, capsys):
    sentinel = "SECRET_URL_RENDER_SENTINEL"
    url = (
        "https://upload.example.com/object"
        f"?X-Amz-Signature={sentinel}"
        f"&X-Amz-Credential={sentinel}#fragment"
    )
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(EgressError) as caught:
            parse_signed_target(url, UPLOAD)
    exc = caught.value
    assert exc.code is EgressErrorCode.CONFIGURATION_INVALID
    assert exc.failure is EgressFailure.FRAGMENT_FORBIDDEN
    assert sentinel not in str(exc)
    assert sentinel not in repr(exc)
    assert sentinel not in _error_text(exc)
    assert sentinel not in caplog.text
    assert sentinel not in " ".join(sys.argv)
    captured = capsys.readouterr()
    assert sentinel not in captured.out + captured.err


@pytest.mark.parametrize(
    "address",
    (
        "8.8.8.8",
        "1.1.1.1",
        "93.184.216.34",
        "2606:4700:4700::1111",
        "2001:4860:4860::8888",
    ),
)
def test_public_address_predicate_accepts_global_unicast(address):
    assert is_public_address(address)


@pytest.mark.parametrize(
    "address",
    (
        "0.0.0.0",
        "10.0.0.1",
        "100.64.0.1",
        "127.0.0.1",
        "169.254.1.1",
        "172.16.0.1",
        "192.0.2.1",
        "192.31.196.1",
        "192.52.193.1",
        "192.88.99.1",
        "192.175.48.1",
        "198.18.0.1",
        "198.51.100.1",
        "203.0.113.1",
        "224.0.0.1",
        "240.0.0.1",
        "255.255.255.255",
        "100.100.100.200",
        "168.63.129.16",
        "::",
        "::1",
        "::8.8.8.8",
        "::ffff:8.8.8.8",
        "::ffff:0:8.8.8.8",
        "::ffff:0:127.0.0.1",
        "::ffff:0:8.8.8.8",
        "64:ff9b::1",
        "64:ff9b:1::1",
        "100::1",
        "2001:db8::1",
        "2002::1",
        "2620:4f:8000::1",
        "3fff::1",
        "5f00::1",
        "fc00::1",
        "fd00:ec2::254",
        "fe80::1",
        "ff02::1",
    ),
)
def test_public_address_predicate_rejects_non_public(address):
    assert not is_public_address(address)
