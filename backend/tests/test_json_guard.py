from __future__ import annotations

import asyncio
import json
import logging
import random
import sys
from dataclasses import replace

import pytest

from rag_app.entrypoints.json_guard import (
    BoundedJsonError, JsonLimits, parse_json_bytes, read_bounded_json,
)


DEFAULT = JsonLimits()


class Request:
    def __init__(self, body=b"{}", *, headers=None, chunk_size=0, failure=None):
        self.scope = {"headers": headers if headers is not None else [
            (b"content-type", b"application/json"),
        ]}
        self.raw_body = body
        self.chunk_size = chunk_size or max(1, len(body))
        self.failure = failure
        self.reads = 0

    async def stream(self):
        for start in range(0, len(self.raw_body), self.chunk_size):
            self.reads += 1
            yield self.raw_body[start:start + self.chunk_size]
        if self.failure:
            raise self.failure

    async def json(self):
        raise AssertionError("unbounded JSON access")

    async def body(self):
        raise AssertionError("unbounded body access")


def stream(raw, limits=DEFAULT, **kwargs):
    return asyncio.run(read_bounded_json(Request(raw, **kwargs), limits))


def both(raw, limits=DEFAULT):
    actual = parse_json_bytes(raw, limits)
    assert stream(raw, limits, chunk_size=1) == actual
    return actual


def reject(raw, code="VALIDATION_ERROR", limits=DEFAULT):
    for call in (lambda: parse_json_bytes(raw, limits),
                 lambda: stream(raw, limits, chunk_size=1)):
        with pytest.raises(BoundedJsonError) as caught:
            call()
        assert caught.value.code == code
        assert caught.value.__cause__ is None
        assert caught.value.__context__ is None


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def test_defaults_and_original_decoded_values():
    assert DEFAULT == JsonLimits(1048576, 16384, 8, 8192, 64, 1024, 65536, 131072, 256)
    value = {"q": " \r\nA\u0301\t\U0001f680 ", "x": [None, True, False, -3, 1.25, {}]}
    assert both(encode(value)) == value
    assert both(b'{"\\u0061":"\\uD83D\\uDE80","x":"\\\\\\"\\/\\b\\f\\n\\r\\t"}') == {
        "a": "\U0001f680", "x": '\\\"/\b\f\n\r\t',
    }


@pytest.mark.parametrize("field", list(JsonLimits.__dataclass_fields__))
@pytest.mark.parametrize("bad", [0, -1, True, 1.5, None])
def test_invalid_limits_are_finite(field, bad):
    with pytest.raises(ValueError, match="positive integers"):
        JsonLimits(**{field: bad})


def test_body_exact_default_and_plus_one():
    raw = b"{}" + b" " * (DEFAULT.max_body_bytes - 2)
    assert parse_json_bytes(raw) == {}
    assert stream(raw, chunk_size=997) == {}
    for call in (lambda: parse_json_bytes(raw + b" "),
                 lambda: stream(raw + b" ", chunk_size=997)):
        with pytest.raises(BoundedJsonError, match="body limit") as caught:
            call()
        assert caught.value.code == "REQUEST_BODY_LIMIT_EXCEEDED"


def test_small_body_limit():
    assert both(b"{}", replace(DEFAULT, max_body_bytes=2)) == {}
    reject(b"{} ", "REQUEST_BODY_LIMIT_EXCEEDED", replace(DEFAULT, max_body_bytes=2))


def test_depth_exact_and_plus_one_including_scalar_values():
    raw = b'{"a":' * 7 + b"0" + b"}" * 7
    both(raw)
    reject(b'{"a":' * 8 + b"0" + b"}" * 8, "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")
    both(b'{"a":' * 7 + b"{}" + b"}" * 7)
    reject(b'{"a":' * 8 + b"{}" + b"}" * 8, "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")
    both(b'{"a":[[[[[[0]]]]]]}')


def node_document(last_count):
    # root + 8 arrays + 7*1024 scalar items + last_count = 8192 at 1015.
    return encode({str(i): [None] * (1024 if i < 7 else last_count) for i in range(8)})


def test_node_default_exact_and_plus_one():
    both(node_document(1015))
    reject(node_document(1016), "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")
    assert both(b'{"a":0}', replace(DEFAULT, max_nodes=2)) == {"a": 0}
    reject(b'{"a":[0]}', "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED", replace(DEFAULT, max_nodes=2))


def test_keys_default_exact_and_plus_one_per_object():
    both(encode({str(i): None for i in range(64)}))
    reject(encode({str(i): None for i in range(65)}), "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")
    both(encode({"x": {str(i): None for i in range(64)},
                 "y": {str(i): None for i in range(64)}}))


def test_arrays_default_exact_and_plus_one_per_array():
    both(encode({"x": [False] * 1024, "y": [None] * 1024}))
    reject(encode({"x": [False] * 1025}), "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")


@pytest.mark.parametrize("as_key", [False, True])
@pytest.mark.parametrize("char", ["x", "\U0001f680"])
def test_string_default_exact_and_plus_one(as_key, char):
    def document(size):
        text = char * size
        return encode({text: 0} if as_key else {"": text})
    both(document(65536))
    reject(document(65537), "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")


def test_total_string_default_exact_and_plus_one_including_keys():
    # Key scalars are included: 1 + 65535 + 1 + 65535 = 131072.
    both(encode({"a": "x" * 65535, "b": "y" * 65535}))
    reject(encode({"a": "x" * 65536, "b": "y" * 65535}),
           "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")
    both(b'{"a":"\\uD83D\\uDE80"}', replace(DEFAULT, max_total_string_scalars=2))
    reject(b'{"a":"\\uD83D\\uDE80x"}', "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED",
           replace(DEFAULT, max_total_string_scalars=2))


def test_escaped_scalar_count_not_lexical_length():
    raw = b'{"":"\\ud83d\\ude80\\u0061"}'
    assert both(raw, replace(DEFAULT, max_string_scalars=2)) == {"": "\U0001f680a"}
    reject(raw, "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED",
           replace(DEFAULT, max_string_scalars=1))


@pytest.mark.parametrize("raw", [
    b"", b" ", b"[]", b"null", b"true", b'"object"', b"42",
    b'{"x":1}junk', b"{}{}", b'{"x":1,}', b'{"x":[1,]}',
    b'{"x" 1}', b'{"x":}', b'{"x":[}', b'{"x":tru}',
    b'{"x":True}', b'{"x":undefined}', b'{"x":NaN}', b'{"x":Infinity}',
    b'{"x":-Infinity}', b'{"x":01}', b'{"x":+1}', b'{"x":.1}',
    b'{"x":1.}', b'{"x":1e}', b'{"x":1e+}', b'{"x":--1}',
    b'{"x":1e309}', b'{"x":-1e309}', b'{"x":1e9999999}',
    b'{"x":"\\uD800"}', b'{"x":"\\uDC00"}', b'{"x":"\\uD800\\u0041"}',
    b'{"x":"\\uD800x"}', b'{"x":"\\uD800\\x"}', b'{"x":"\\u123g"}',
    b'{"x":"\\x"}', b'{"x":"\x00"}', b'{"x":"\n"}',
    b'{"x":"\xff"}', b'{"x":"\xc0\xaf"}', b'{"x":"\xed\xa0\x80"}',
    b'{"x":"\xf4\x90\x80\x80"}', b'{"x":"\xe2\x82',
    b'\xef\xbb\xbf{}', b'{"x":1}\xc2\xa0',
    b'{"x":1,"x":2}', b'{"x":1,"\\u0078":2}',
    b'{"\\ud83d\\ude80":1,"\xf0\x9f\x9a\x80":2}',
    b'{"x":{"a":1,"a":2}}',
])
def test_malformed_json_encoding_and_duplicate_keys(raw):
    reject(raw)


@pytest.mark.parametrize("raw", [b'{"x":"', b'{"x":"\\', b'{"x":"\\u',
                                      b'{"x":"\\ud800', b'{"x":tru', b'{"x":['])
def test_truncated_tokens(raw):
    reject(raw)


def test_number_boundaries():
    raw = b'{"x":' + b"9" * 256 + b"}"
    assert both(raw)["x"] == int("9" * 256)
    reject(b'{"x":' + b"9" * 257 + b"}", "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED")
    both(b'{"x":1.7976931348623157e308,"n":-0.0,"tiny":1e-999}')
    reject(b'{"x":1.7976931348623159e308}')


def test_interpreter_number_conversion_failure_is_finite():
    old_limit = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(640)
        reject(b'{"x":' + b"9" * 641 + b"}",
               limits=replace(DEFAULT, max_number_chars=642))
    finally:
        sys.set_int_max_str_digits(old_limit)


def test_deterministic_differential_decoding():
    rng = random.Random(1100)

    def value(depth):
        scalars = [None, True, False, 0, -15, 1.25, -0.0,
                   "", "a\\b\n\t\"/\U0001f680", " A\u0301 "]
        if depth == 3:
            return rng.choice(scalars)
        kind = rng.randrange(4)
        if kind == 0:
            return [value(depth + 1) for _ in range(rng.randrange(4))]
        if kind == 1:
            return {str(i): value(depth + 1) for i in range(rng.randrange(4))}
        return rng.choice(scalars)

    for _ in range(120):
        expected = {"x": value(0), "y": value(0)}
        for ascii_only in (True, False):
            raw = json.dumps(expected, ensure_ascii=ascii_only).encode()
            assert parse_json_bytes(raw) == json.loads(raw) == expected
            assert stream(raw, chunk_size=rng.randrange(1, 12)) == expected


@pytest.mark.parametrize("chunk_size", [1, 2, 3, 4, 7, 1023, 1024])
def test_chunk_cuts_preserve_utf8_escapes_and_numbers(chunk_size):
    raw = b'{"a":"\xf0\x9f\x9a\x80\\uD83D\\uDE80\\n","b":[true,false,null,-1.25e+2]}'
    assert stream(raw, chunk_size=chunk_size) == parse_json_bytes(raw)


@pytest.mark.parametrize("media", [
    b"application/json", b"Application/JSON",
    b"application/json; charset=UTF-8", b'application/json;charset="utf-8"',
])
@pytest.mark.parametrize("encoding", [None, b"identity", b"IDENTITY"])
def test_valid_http_headers(media, encoding):
    headers = [(b"content-type", media), (b"content-length", b"0002")]
    if encoding is not None:
        headers.append((b"content-encoding", encoding))
    assert stream(b"{}", headers=headers) == {}


@pytest.mark.parametrize("headers,code", [
    ([], "UNSUPPORTED_MEDIA_TYPE"),
    ([(b"content-type", b"text/json")], "UNSUPPORTED_MEDIA_TYPE"),
    ([(b"content-type", b"application/json;charset=latin1")], "UNSUPPORTED_MEDIA_TYPE"),
    ([(b"content-type", b"application/json;charset=utf-8;foo=bar")], "UNSUPPORTED_MEDIA_TYPE"),
    ([(b"content-type", b"application/json;")], "UNSUPPORTED_MEDIA_TYPE"),
    ([(b"content-type", b"application/json"), (b"content-encoding", b"gzip")],
     "UNSUPPORTED_CONTENT_ENCODING"),
    ([(b"content-type", b"application/json"), (b"content-encoding", b"")],
     "UNSUPPORTED_CONTENT_ENCODING"),
    ([(b"content-type", b"application/json"), (b"content-length", b"-1")],
     "VALIDATION_ERROR"),
    ([(b"content-type", b"application/json"), (b"content-length", b"2,2")],
     "VALIDATION_ERROR"),
    ([(b"content-type", b"application/json"), (b"content-length", b"9" * 5000)],
     "REQUEST_BODY_LIMIT_EXCEEDED"),
])
def test_invalid_http_headers_before_read(headers, code):
    req = Request(headers=headers)
    with pytest.raises(BoundedJsonError) as caught:
        asyncio.run(read_bounded_json(req))
    assert caught.value.code == code
    assert req.reads == 0


@pytest.mark.parametrize("name,value", [
    (b"content-type", b"application/json"), (b"content-length", b"2"),
    (b"content-encoding", b"identity"),
])
def test_duplicate_control_headers(name, value):
    headers = [(b"content-type", b"application/json")]
    if name != b"content-type":
        headers.append((name, value))
    headers.append((name.upper(), value))
    with pytest.raises(BoundedJsonError) as caught:
        stream(b"{}", headers=headers)
    assert caught.value.code == "VALIDATION_ERROR"


def test_headers_exact_default_and_plus_one_including_duplicates():
    headers = [(b"content-type", b"application/json"), (b"x", b"a"), (b"x", b"")]
    baseline = 2 + sum(len(k) + len(v) + 4 for k, v in headers)
    headers[-1] = (b"x", b"a" * (16384 - baseline))
    assert stream(b"{}", headers=headers) == {}
    headers[-1] = (b"x", headers[-1][1] + b"a")
    req = Request(headers=headers)
    with pytest.raises(BoundedJsonError) as caught:
        asyncio.run(read_bounded_json(req))
    assert caught.value.code == "REQUEST_HEADERS_LIMIT_EXCEEDED"
    assert req.reads == 0


@pytest.mark.parametrize("declared", [b"0", b"1", b"3", b"1048576"])
def test_false_content_length(declared):
    with pytest.raises(BoundedJsonError) as caught:
        stream(b"{}", headers=[(b"content-type", b"application/json"),
                              (b"content-length", declared)])
    assert caught.value.code == "VALIDATION_ERROR"


def test_actual_stream_limit_despite_false_small_content_length():
    req = Request(b"{}" + b" " * 50, chunk_size=3, headers=[
        (b"content-type", b"application/json"), (b"content-length", b"2")])
    with pytest.raises(BoundedJsonError) as caught:
        asyncio.run(read_bounded_json(req, replace(DEFAULT, max_body_bytes=8)))
    assert caught.value.code == "REQUEST_BODY_LIMIT_EXCEEDED"
    assert req.reads == 3


def test_declared_over_limit_rejected_without_reading():
    req = Request(headers=[(b"content-type", b"application/json"),
                           (b"content-length", b"1048577")])
    with pytest.raises(BoundedJsonError) as caught:
        asyncio.run(read_bounded_json(req))
    assert caught.value.code == "REQUEST_BODY_LIMIT_EXCEEDED"
    assert req.reads == 0


@pytest.mark.parametrize("raw,limits", [
    (b'{"a":{"b":null}}', replace(DEFAULT, max_depth=2)),
    (b'{"a":[0,1,2,3,4]}', replace(DEFAULT, max_array_items=2)),
    (b'{"a":0,"b":1,"c":2}', replace(DEFAULT, max_object_keys=1)),
    (b'{"a":[0,1,2,3]}', replace(DEFAULT, max_nodes=3)),
    (b'{"a":123456789}', replace(DEFAULT, max_number_chars=3)),
    (b'{"a":"long private text"}', replace(DEFAULT, max_total_string_scalars=2)),
])
def test_each_structural_limit_stops_stream_before_end(raw, limits):
    req = Request(raw, chunk_size=1)
    with pytest.raises(BoundedJsonError) as caught:
        asyncio.run(read_bounded_json(req, limits))
    assert caught.value.code == "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED"
    assert req.reads < len(raw)


def test_early_structural_failure_never_reads_rest_or_calls_general_loader(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("unbounded parser called")
    monkeypatch.setattr(json, "loads", forbidden)
    monkeypatch.setattr(json, "load", forbidden)
    raw = b'{"x":"' + b"a" * 100 + b'"}'
    req = Request(raw, chunk_size=1)
    with pytest.raises(BoundedJsonError) as caught:
        asyncio.run(read_bounded_json(req, replace(DEFAULT, max_string_scalars=3)))
    assert caught.value.code == "PROTOCOL_STRUCTURE_LIMIT_EXCEEDED"
    assert req.reads == 10
    assert parse_json_bytes(b'{"x":[1,true,"ok"]}') == {"x": [1, True, "ok"]}


def test_error_and_disconnect_do_not_expose_body_exception_or_logs(caplog):
    secret = "secret-private-token https://private.example/signed"
    caplog.set_level(logging.DEBUG)
    req = Request(b'{"safe":1}', failure=RuntimeError(secret))
    with pytest.raises(BoundedJsonError) as caught:
        asyncio.run(read_bounded_json(req))
    error = caught.value
    assert error.code == "REQUEST_STREAM_ERROR"
    assert error.__context__ is None and error.__cause__ is None
    assert set(vars(error)) == {"code", "message"}
    assert secret not in str(error) + repr(error) + repr(vars(error)) + caplog.text
    with pytest.raises(BoundedJsonError) as malformed:
        stream(encode({"q": secret})[:-1])
    assert secret not in str(malformed.value) + repr(malformed.value) + caplog.text
    assert BoundedJsonError(secret).code == "VALIDATION_ERROR"


def test_binary_original_put_is_not_affected_without_adapter():
    # No app/middleware hook: an unrelated binary handler retains its own budget.
    raw = b"\x00" * (1048576 + 1)
    req = Request(raw, headers=[(b"content-type", b"application/octet-stream")])

    async def original_put(request):
        count = 0
        async for chunk in request.stream():
            count += len(chunk)
        return count

    assert asyncio.run(original_put(req)) == len(raw)
