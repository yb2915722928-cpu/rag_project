"""Opt-in JSON input guard; never install this on binary original PUTs.

Root object depth is 1; every contained value (including scalars) adds a level.
Each object, array and scalar is one node. Keys are not nodes, but their decoded
Unicode scalars count against both string budgets. No normalization is applied.
"""
from __future__ import annotations

import codecs
import math
import re
from dataclasses import dataclass, fields
from typing import Any


@dataclass(frozen=True, slots=True)
class JsonLimits:
    max_body_bytes: int = 1_048_576
    max_header_bytes: int = 16_384
    max_depth: int = 8
    max_nodes: int = 8_192
    max_object_keys: int = 64
    max_array_items: int = 1_024
    max_string_scalars: int = 65_536
    max_total_string_scalars: int = 131_072
    max_number_chars: int = 256

    def __post_init__(self) -> None:
        if any(type(getattr(self, f.name)) is not int or getattr(self, f.name) <= 0
               for f in fields(self)):
            raise ValueError("JSON limits must be positive integers.")


_MESSAGES = {
    "VALIDATION_ERROR": "Invalid JSON input.",
    "REQUEST_BODY_LIMIT_EXCEEDED": "JSON body limit exceeded.",
    "REQUEST_HEADERS_LIMIT_EXCEEDED": "Request header limit exceeded.",
    "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED": "JSON structure limit exceeded.",
    "UNSUPPORTED_MEDIA_TYPE": "UTF-8 application/json is required.",
    "UNSUPPORTED_CONTENT_ENCODING": "Identity content encoding is required.",
    "REQUEST_STREAM_ERROR": "JSON request stream could not be read.",
}


class BoundedJsonError(ValueError):
    """Only a finite code and fixed public message; no input/exception fields."""

    def __init__(self, code: str = "VALIDATION_ERROR") -> None:
        self.code = code if code in _MESSAGES else "VALIDATION_ERROR"
        self.message = _MESSAGES[self.code]
        super().__init__(self.message)


def _invalid() -> None:
    raise BoundedJsonError()


def _structure() -> None:
    raise BoundedJsonError("PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")


@dataclass(slots=True)
class _Frame:
    value: dict[str, Any] | list[Any]
    state: str
    key: str | None = None
    count: int = 0


_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z")
_HEX = frozenset("0123456789abcdefABCDEF")
_ESCAPES = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
            "n": "\n", "r": "\r", "t": "\t"}
_WHITESPACE = " \t\r\n"


class _Parser:
    def __init__(self, limits: JsonLimits) -> None:
        self.limits = limits
        self.decoder = codecs.getincrementaldecoder("utf-8")("strict")
        self.byte_count = 0
        self.nodes = 0
        self.total_strings = 0
        self.stack: list[_Frame] = []
        self.result: dict[str, Any] | None = None
        self.mode = ""
        self.token: list[str] = []
        self.string_key = False
        self.string_size = 0
        self.hex_digits = ""
        self.high_surrogate = 0

    def feed(self, raw: bytes) -> None:
        if not isinstance(raw, bytes):
            _invalid()
        self.byte_count += len(raw)
        if self.byte_count > self.limits.max_body_bytes:
            raise BoundedJsonError("REQUEST_BODY_LIMIT_EXCEEDED")
        # Bound decoder temporaries even when the transport delivers one large chunk.
        for offset in range(0, len(raw), 1024):
            self._decode(raw[offset:offset + 1024], final=False)

    def _decode(self, raw: bytes, *, final: bool) -> None:
        failed = False
        try:
            text = self.decoder.decode(raw, final=final)
        except UnicodeDecodeError:
            failed = True
        if failed:
            _invalid()
        for char in text:
            self._char(char)

    def finish(self) -> dict[str, Any]:
        self._decode(b"", final=True)
        if self.mode == "number":
            self._number()
        if self.mode or self.stack or self.result is None:
            _invalid()
        return self.result

    def _scalar(self, char: str) -> None:
        if 0xD800 <= ord(char) <= 0xDFFF:
            _invalid()
        self.string_size += 1
        self.total_strings += 1
        if (self.string_size > self.limits.max_string_scalars
                or self.total_strings > self.limits.max_total_string_scalars):
            _structure()
        self.token.append(char)

    def _start_value(self, char: str) -> None:
        depth = len(self.stack) + 1
        self.nodes += 1
        if depth > self.limits.max_depth or self.nodes > self.limits.max_nodes:
            _structure()
        if self.stack and isinstance(self.stack[-1].value, list):
            self.stack[-1].count += 1
            if self.stack[-1].count > self.limits.max_array_items:
                _structure()
        if char in "{[":
            value: dict[str, Any] | list[Any] = {} if char == "{" else []
            self._accept(value)
            self.stack.append(_Frame(value, "key_or_end" if char == "{" else "value_or_end"))
        elif char == '"':
            self._start_string(key=False)
        elif char in "-0123456789":
            self.mode, self.token = "number", [char]
        elif char in "tfn":
            self.mode, self.token = "literal", [char]
        else:
            _invalid()

    def _accept(self, value: Any) -> None:
        if not self.stack:
            if self.result is not None or not isinstance(value, dict):
                _invalid()
            self.result = value
        else:
            frame = self.stack[-1]
            if isinstance(frame.value, dict):
                assert frame.key is not None
                frame.value[frame.key] = value
                frame.key = None
            else:
                frame.value.append(value)
            frame.state = "comma_or_end"

    def _start_string(self, *, key: bool) -> None:
        self.mode, self.token = "string", []
        self.string_key, self.string_size = key, 0

    def _number(self) -> None:
        token = "".join(self.token)
        if not _NUMBER.fullmatch(token):
            _invalid()
        failed = False
        try:
            value = float(token) if any(c in token for c in ".eE") else int(token)
        except (ValueError, OverflowError):
            failed = True
        if failed:
            _invalid()
        if isinstance(value, float) and not math.isfinite(value):
            _invalid()
        self.mode, self.token = "", []
        self._accept(value)

    def _char(self, char: str) -> None:
        if self.mode == "string":
            if char == '"':
                value = "".join(self.token)
                self.mode, self.token = "", []
                if self.string_key:
                    frame = self.stack[-1]
                    if value in frame.value:
                        _invalid()
                    frame.key, frame.state = value, "colon"
                else:
                    self._accept(value)
            elif char == "\\":
                self.mode = "escape"
            elif ord(char) < 0x20:
                _invalid()
            else:
                self._scalar(char)
            return
        if self.mode == "escape":
            if char == "u":
                self.mode, self.hex_digits = "unicode", ""
            elif char in _ESCAPES:
                self._scalar(_ESCAPES[char])
                self.mode = "string"
            else:
                _invalid()
            return
        if self.mode in ("unicode", "low_unicode"):
            if char not in _HEX:
                _invalid()
            self.hex_digits += char
            if len(self.hex_digits) == 4:
                value = int(self.hex_digits, 16)
                if self.mode == "low_unicode":
                    if not 0xDC00 <= value <= 0xDFFF:
                        _invalid()
                    self._scalar(chr(0x10000 + ((self.high_surrogate - 0xD800) << 10)
                                     + value - 0xDC00))
                    self.high_surrogate = 0
                    self.mode = "string"
                elif 0xD800 <= value <= 0xDBFF:
                    self.high_surrogate = value
                    self.mode = "low_backslash"
                elif 0xDC00 <= value <= 0xDFFF:
                    _invalid()
                else:
                    self._scalar(chr(value))
                    self.mode = "string"
            return
        if self.mode == "low_backslash":
            if char != "\\":
                _invalid()
            self.mode = "low_u"
            return
        if self.mode == "low_u":
            if char != "u":
                _invalid()
            self.mode, self.hex_digits = "low_unicode", ""
            return
        if self.mode == "literal":
            token = "".join(self.token)
            expected, value = {"t": ("true", True), "f": ("false", False),
                               "n": ("null", None)}[token[0]]
            if char != expected[len(token)]:
                _invalid()
            self.token.append(char)
            if len(self.token) == len(expected):
                self.mode, self.token = "", []
                self._accept(value)
            return
        if self.mode == "number":
            if char in "0123456789.eE+-":
                if len(self.token) >= self.limits.max_number_chars:
                    _structure()
                self.token.append(char)
                return
            self._number()
            # The delimiter belongs to the enclosing container.
        if char in _WHITESPACE:
            return
        if not self.stack:
            if self.result is not None or char != "{":
                _invalid()
            self._start_value(char)
            return
        frame = self.stack[-1]
        if frame.state in ("key_or_end", "key"):
            if char == "}" and frame.state == "key_or_end":
                self.stack.pop()
            elif char == '"':
                frame.count += 1
                if frame.count > self.limits.max_object_keys:
                    _structure()
                self._start_string(key=True)
            else:
                _invalid()
        elif frame.state == "colon":
            if char != ":":
                _invalid()
            frame.state = "value"
        elif frame.state in ("value", "value_or_end"):
            if char == "]" and frame.state == "value_or_end":
                self.stack.pop()
            else:
                self._start_value(char)
        elif frame.state == "comma_or_end":
            closing = "}" if isinstance(frame.value, dict) else "]"
            if char == closing:
                self.stack.pop()
            elif char == ",":
                frame.state = "key" if isinstance(frame.value, dict) else "value"
            else:
                _invalid()


def parse_json_bytes(raw: bytes, limits: JsonLimits = JsonLimits()) -> dict[str, Any]:
    """Parse bytes with the same limits and decoded values as the HTTP adapter."""
    parser = _Parser(limits)
    parser.feed(raw)
    return parser.finish()


def _headers(request: Any, limits: JsonLimits) -> int | None:
    # ASGI exposes field bytes, not request-line/wire framing. Count HTTP/1 field
    # serialization (name + ': ' + value + CRLF) and its final CRLF, duplicates included.
    total = 2
    selected: dict[bytes, bytes] = {}
    for name, value in request.scope.get("headers", []):
        total += len(name) + len(value) + 4
        if total > limits.max_header_bytes:
            raise BoundedJsonError("REQUEST_HEADERS_LIMIT_EXCEEDED")
        lowered = name.lower()
        if lowered in (b"content-type", b"content-encoding", b"content-length"):
            if lowered in selected:
                _invalid()
            selected[lowered] = value.strip()
    media = selected.get(b"content-type", b"").lower().split(b";")
    if media[0].strip() != b"application/json" or len(media) > 2:
        raise BoundedJsonError("UNSUPPORTED_MEDIA_TYPE")
    if len(media) == 2:
        charset = media[1].strip().split(b"=", 1)
        if (len(charset) != 2 or charset[0].strip() != b"charset"
                or charset[1].strip() not in (b"utf-8", b'"utf-8"')):
            raise BoundedJsonError("UNSUPPORTED_MEDIA_TYPE")
    if selected.get(b"content-encoding", b"identity").lower() != b"identity":
        raise BoundedJsonError("UNSUPPORTED_CONTENT_ENCODING")
    length = selected.get(b"content-length")
    if length is None:
        return None
    if not length or any(c < 48 or c > 57 for c in length):
        _invalid()
    # Compare decimal strings first: never convert an arbitrarily long header integer.
    digits = length.lstrip(b"0") or b"0"
    ceiling = str(limits.max_body_bytes).encode("ascii")
    if len(digits) > len(ceiling) or (len(digits) == len(ceiling) and digits > ceiling):
        raise BoundedJsonError("REQUEST_BODY_LIMIT_EXCEEDED")
    return int(digits)


async def read_bounded_json(request: Any, limits: JsonLimits = JsonLimits()) -> dict[str, Any]:
    """Read a Starlette-compatible request stream without body()/json() buffering.

    Invoke only for JSON routes. Unknown fields/schema versions belong to the
    caller's public Pydantic model; this adapter adds no routes or middleware.
    """
    declared = _headers(request, limits)
    parser = _Parser(limits)
    failure: str | None = None
    try:
        async for chunk in request.stream():
            parser.feed(chunk)
    except BoundedJsonError as exc:
        failure = exc.code
    except Exception:
        failure = "REQUEST_STREAM_ERROR"
    # Raise outside the handler: private transport exceptions are not chained.
    if failure is not None:
        raise BoundedJsonError(failure)
    if declared is not None and parser.byte_count != declared:
        _invalid()
    return parser.finish()
