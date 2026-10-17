"""Production DNS/TLS/HTTP egress adapters with no implicit retry or redirect."""

from __future__ import annotations

import math
import socket
import ssl
from collections.abc import Callable
from typing import BinaryIO

from rag_app.modules.execution.egress import (
    AddressFamily,
    EgressConnection,
    EgressConnector,
    EgressError,
    EgressErrorCode,
    EgressFailure,
    EgressPlan,
    EgressRequest,
    EgressResponse,
    ResolvedAddress,
)


_MAX_RESPONSE_HEADER_BYTES = 65_536
_MAX_RESPONSE_HEADERS = 100


def _dependency(failure: EgressFailure) -> EgressError:
    return EgressError(EgressErrorCode.DEPENDENCY_UNAVAILABLE, failure)


def _configuration(failure: EgressFailure) -> EgressError:
    return EgressError(EgressErrorCode.CONFIGURATION_INVALID, failure)


class SystemDnsResolver:
    """Collect every A and AAAA result for one explicit dispatch."""

    def resolve(self, host: str, port: int) -> tuple[ResolvedAddress, ...]:
        results = None
        failed = False
        try:
            results = socket.getaddrinfo(
                host,
                port,
                family=socket.AF_UNSPEC,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
                flags=0,
            )
        except Exception:
            failed = True
        if failed:
            raise _dependency(EgressFailure.DNS_FAILURE) from None

        addresses: list[ResolvedAddress] = []
        seen: set[tuple[str, str]] = set()
        invalid = False
        try:
            records = list(results)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            invalid = True
            records = []
        for record in records:
            if not isinstance(record, (tuple, list)) or len(record) != 5:
                invalid = True
                continue
            family, _socktype, _proto, _canonname, sockaddr = record
            if family not in {socket.AF_INET, socket.AF_INET6}:
                continue
            if (
                not isinstance(sockaddr, (tuple, list))
                or len(sockaddr) < 2
                or not isinstance(sockaddr[0], str)
            ):
                invalid = True
                continue
            address_family = (
                AddressFamily.IPV4 if family == socket.AF_INET else AddressFamily.IPV6
            )
            value = sockaddr[0]
            key = (address_family.value, value)
            if key in seen:
                continue
            seen.add(key)
            try:
                addresses.append(ResolvedAddress(address_family, value))
            except EgressError:
                invalid = True
        if invalid:
            raise _dependency(EgressFailure.DNS_FAILURE) from None
        return tuple(addresses)


class BoundTlsConnection:
    """One already-connected TLS socket bound to an approved address."""

    selected_address: ResolvedAddress
    server_hostname: str

    def __init__(
        self,
        wrapped_socket: ssl.SSLSocket,
        *,
        selected_address: ResolvedAddress,
        server_hostname: str,
    ) -> None:
        self._socket = wrapped_socket
        self.selected_address = selected_address
        self.server_hostname = server_hostname

    def sendall(self, data: bytes) -> None:
        self._socket.sendall(data)

    def makefile(self, mode: str) -> BinaryIO:
        return self._socket.makefile(mode)

    def close(self) -> None:
        self._socket.close()


class TlsBoundConnector:
    """Connect to one approved IP and verify the original hostname."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 10.0,
        ssl_context: ssl.SSLContext | None = None,
        socket_factory: Callable[[AddressFamily], socket.socket] | None = None,
    ) -> None:
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0
            or timeout_seconds > 3_600
        ):
            raise _configuration(EgressFailure.TIMEOUT_INVALID)
        context = ssl.create_default_context() if ssl_context is None else ssl_context
        if (
            getattr(context, "check_hostname", None) is not True
            or getattr(context, "verify_mode", None) != ssl.CERT_REQUIRED
            or not callable(getattr(context, "wrap_socket", None))
        ):
            raise _configuration(EgressFailure.TLS_CONFIGURATION_INVALID)
        if socket_factory is not None and not callable(socket_factory):
            raise _configuration(EgressFailure.ADAPTER_INVALID)
        self._timeout = float(timeout_seconds)
        self._context = context
        self._socket_factory = socket_factory or self._new_socket

    @staticmethod
    def _new_socket(family: AddressFamily) -> socket.socket:
        native = socket.AF_INET if family is AddressFamily.IPV4 else socket.AF_INET6
        return socket.socket(native, socket.SOCK_STREAM)

    @staticmethod
    def _close(value: object) -> None:
        close = getattr(value, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                pass

    def connect(self, plan: EgressPlan) -> BoundTlsConnection:
        if not isinstance(plan, EgressPlan):
            raise _configuration(EgressFailure.PLAN_INVALID)
        address = plan.connect_address
        family = socket.AF_INET if address.family is AddressFamily.IPV4 else socket.AF_INET6

        raw_socket = None
        failed = False
        try:
            raw_socket = self._socket_factory(address.family)
        except Exception:
            failed = True
        if failed:
            raise _dependency(EgressFailure.CONNECT_FAILURE) from None
        if (
            not callable(getattr(raw_socket, "connect", None))
            or not callable(getattr(raw_socket, "settimeout", None))
            or not callable(getattr(raw_socket, "close", None))
            or getattr(raw_socket, "family", family) != family
        ):
            self._close(raw_socket)
            raise _dependency(EgressFailure.CONNECT_FAILURE) from None

        failed = False
        try:
            raw_socket.settimeout(self._timeout)
            raw_socket.connect((address.address, plan.target.port))
        except Exception:
            failed = True
        if failed:
            self._close(raw_socket)
            raise _dependency(EgressFailure.CONNECT_FAILURE) from None

        wrapped = None
        failed = False
        try:
            wrapped = self._context.wrap_socket(
                raw_socket,
                server_hostname=plan.target.host,
                do_handshake_on_connect=True,
            )
        except Exception:
            failed = True
        if failed:
            self._close(raw_socket)
            raise _dependency(EgressFailure.TLS_FAILURE) from None

        if (
            not callable(getattr(wrapped, "sendall", None))
            or not callable(getattr(wrapped, "makefile", None))
            or not callable(getattr(wrapped, "close", None))
        ):
            self._close(wrapped)
            raise _dependency(EgressFailure.TLS_FAILURE) from None

        return BoundTlsConnection(
            wrapped,
            selected_address=address,
            server_hostname=plan.target.host,
        )


class OneShotHttpTransport:
    """Send one bounded HTTP/1.1 request and return the response as-is."""

    def __init__(
        self,
        connector: EgressConnector,
        *,
        max_response_bytes: int = 1_048_576,
    ) -> None:
        if not isinstance(connector, EgressConnector):
            raise _configuration(EgressFailure.ADAPTER_INVALID)
        if (
            type(max_response_bytes) is not int
            or max_response_bytes < 1
            or max_response_bytes > 67_108_864
        ):
            raise _configuration(EgressFailure.ADAPTER_INVALID)
        self._connector = connector
        self._max_response_bytes = max_response_bytes

    def _build_payload(self, plan: EgressPlan, request: EgressRequest) -> bytes:
        if request.api_authorization is not None and not plan.target.authorization_allowed:
            raise _configuration(EgressFailure.AUTHORIZATION_NOT_ALLOWED)

        lines = [
            f"{request.method} {plan.target.request_target} HTTP/1.1",
            f"Host: {plan.target.host_header}",
            f"Content-Length: {len(request.body)}",
            "Connection: close",
        ]
        lines.extend(f"{name}: {value}" for name, value in request.headers)
        if request.api_authorization is not None:
            lines.append(f"Authorization: {request.api_authorization}")
        head = ("\r\n".join(lines) + "\r\n\r\n").encode("ascii")
        return head + request.body

    def _read_body(
        self,
        reader: BinaryIO,
        *,
        method: str,
        status: int,
        headers: dict[str, list[str]],
    ) -> bytes:
        if method == "HEAD" or status in {204, 304}:
            return b""

        transfer_encoding = headers.get("transfer-encoding")
        content_length = headers.get("content-length")
        if transfer_encoding and content_length:
            raise _dependency(EgressFailure.RESPONSE_INVALID)
        if transfer_encoding:
            if (
                len(transfer_encoding) != 1
                or transfer_encoding[0].strip().lower() != "chunked"
            ):
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            return self._read_chunked(reader)
        if content_length:
            if (
                len(content_length) != 1
                or not content_length[0].isdigit()
                or len(content_length[0]) > 12
            ):
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            length = int(content_length[0])
            if length > self._max_response_bytes:
                raise _dependency(EgressFailure.RESPONSE_TOO_LARGE)
            body = reader.read(length)
            if not isinstance(body, bytes) or len(body) != length:
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            return body

        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = reader.read(65_536)
            if not chunk:
                break
            if not isinstance(chunk, bytes):
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            total += len(chunk)
            if total > self._max_response_bytes:
                raise _dependency(EgressFailure.RESPONSE_TOO_LARGE)
            chunks.append(chunk)
        return b"".join(chunks)

    def _read_chunked(self, reader: BinaryIO) -> bytes:
        chunks: list[bytes] = []
        total = 0
        while True:
            line = reader.readline(1_025)
            if not line or len(line) > 1_024 or not line.endswith(b"\n"):
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            size_text = line.strip().split(b";", 1)[0]
            if (
                not size_text
                or len(size_text) > 16
                or any(character not in b"0123456789abcdefABCDEF" for character in size_text)
            ):
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            size = int(size_text, 16)
            if size == 0:
                trailer_bytes = 0
                while True:
                    trailer = reader.readline(_MAX_RESPONSE_HEADER_BYTES + 1)
                    if not trailer or len(trailer) > _MAX_RESPONSE_HEADER_BYTES:
                        raise _dependency(EgressFailure.RESPONSE_INVALID)
                    trailer_bytes += len(trailer)
                    if trailer_bytes > _MAX_RESPONSE_HEADER_BYTES:
                        raise _dependency(EgressFailure.RESPONSE_INVALID)
                    if trailer in {b"\r\n", b"\n"}:
                        return b"".join(chunks)
            total += size
            if total > self._max_response_bytes:
                raise _dependency(EgressFailure.RESPONSE_TOO_LARGE)
            data = reader.read(size)
            if not isinstance(data, bytes) or len(data) != size:
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            chunks.append(data)
            separator = reader.readline(3)
            if separator not in {b"\r\n", b"\n"}:
                raise _dependency(EgressFailure.RESPONSE_INVALID)

    def _read_response(
        self, connection: EgressConnection, method: str,
    ) -> EgressResponse:
        reader = connection.makefile("rb")
        try:
            status_line = reader.readline(_MAX_RESPONSE_HEADER_BYTES + 1)
            if not status_line or len(status_line) > _MAX_RESPONSE_HEADER_BYTES:
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            if not status_line.endswith(b"\n"):
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            status_line = status_line.rstrip(b"\r\n")
            parts = status_line.split(b" ", 2)
            if (
                len(parts) < 2
                or not parts[0].startswith(b"HTTP/")
                or not parts[1].isdigit()
                or len(parts[1]) != 3
            ):
                raise _dependency(EgressFailure.RESPONSE_INVALID)
            status = int(parts[1])

            header_bytes = 0
            headers: list[tuple[str, str]] = []
            while True:
                line = reader.readline(_MAX_RESPONSE_HEADER_BYTES + 1)
                if not line or len(line) > _MAX_RESPONSE_HEADER_BYTES:
                    raise _dependency(EgressFailure.RESPONSE_INVALID)
                if not line.endswith(b"\n"):
                    raise _dependency(EgressFailure.RESPONSE_INVALID)
                header_bytes += len(line)
                if header_bytes > _MAX_RESPONSE_HEADER_BYTES:
                    raise _dependency(EgressFailure.RESPONSE_INVALID)
                line = line.rstrip(b"\r\n")
                if not line:
                    break
                if b":" not in line:
                    raise _dependency(EgressFailure.RESPONSE_INVALID)
                name, _, value = line.partition(b":")
                decoded_name = None
                decoded_value = None
                invalid = False
                try:
                    decoded_name = name.decode("ascii")
                    decoded_value = value.strip(b" \t").decode("latin-1")
                except UnicodeError:
                    invalid = True
                if (
                    invalid
                    or not decoded_name
                    or len(headers) >= _MAX_RESPONSE_HEADERS
                ):
                    raise _dependency(EgressFailure.RESPONSE_INVALID)
                headers.append((decoded_name, decoded_value))

            by_name: dict[str, list[str]] = {}
            for name, value in headers:
                by_name.setdefault(name.lower(), []).append(value)
            body = self._read_body(
                reader, method=method, status=status, headers=by_name,
            )
            return EgressResponse(status=status, headers=tuple(headers), body=body)
        finally:
            try:
                reader.close()
            except Exception:
                pass

    def send(self, plan: EgressPlan, request: EgressRequest) -> EgressResponse:
        if not isinstance(plan, EgressPlan) or not isinstance(request, EgressRequest):
            raise _configuration(EgressFailure.REQUEST_INVALID)

        payload = None
        error = None
        try:
            payload = self._build_payload(plan, request)
        except EgressError as exc:
            error = EgressError(exc.code, exc.failure)
        except Exception:
            error = _configuration(EgressFailure.REQUEST_INVALID)
        if error is not None:
            raise error from None

        connection = None
        result = None
        error = None
        try:
            connection = self._connector.connect(plan)
            connection.sendall(payload)
            result = self._read_response(connection, request.method)
        except EgressError as exc:
            error = EgressError(exc.code, exc.failure)
        except Exception:
            error = _dependency(EgressFailure.TRANSPORT_FAILURE)
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass
        if error is not None:
            raise error from None
        return result
