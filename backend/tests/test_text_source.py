from __future__ import annotations

import ast
import dataclasses
import hashlib
from pathlib import Path
import unicodedata

import pytest

from rag_app.modules.indexing.text_source import (
    DEFAULT_OVERLAP_CHARS,
    DEFAULT_TARGET_CHARS,
    MESSAGES,
    SourceChunk,
    SourceSpan,
    StructureNode,
    TextSourceConfig,
    TextSourceError,
    parse_text_source,
)


VERSION = "doc-version-1"
MODULE_PATH = (
    Path(__file__).parents[1]
    / "src/rag_app/modules/indexing/text_source.py"
)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse(
    raw,
    *,
    source_format="markdown",
    version=VERSION,
    config=None,
):
    return parse_text_source(
        raw,
        document_version_id=version,
        source_format=source_format,
        config=config,
    )


def reject(call, code):
    with pytest.raises(TextSourceError) as caught:
        call()
    error = caught.value
    assert error.code == code
    assert str(error).startswith(f"{code}: ")
    assert error.__cause__ is None
    return error


def assert_exact(parsed) -> None:
    assert parsed.source_text_hash == digest_text(parsed.source_text)
    for value in (
        parsed.original_sha256,
        parsed.source_text_hash,
        parsed.processing_config_id,
    ):
        assert len(value) == 64
        assert all(char in "0123456789abcdef" for char in value)

    seen: set[str] = set()
    for ordinal, chunk in enumerate(parsed.chunks):
        assert chunk.ordinal == ordinal
        assert len(chunk.chunk_id) == 64
        assert all(char in "0123456789abcdef" for char in chunk.chunk_id)
        assert chunk.chunk_id not in seen
        seen.add(chunk.chunk_id)
        assert chunk.spans
        assert len(chunk.text) <= parsed.target_chars

        previous_end = None
        for span in chunk.spans:
            assert parsed.source_text[span.start:span.end] == span.excerpt
            assert digest_text(span.excerpt) == span.sha256
            assert span.length == len(span.excerpt)
            if previous_end is not None:
                assert previous_end <= span.start
            previous_end = span.end

        for node in chunk.structure_path:
            assert parsed.source_text[node.start:node.end] == node.text
            assert len(node.text) == node.end - node.start


def assert_body_covered(parsed) -> None:
    covered: set[int] = set()
    for chunk in parsed.chunks:
        for span in chunk.spans:
            covered.update(range(span.start, span.end))
    missing = [
        index
        for index, value in enumerate(parsed.source_text)
        if not value.isspace() and index not in covered
    ]
    assert missing == [], missing[:10]


def is_combining(value: str) -> bool:
    return (
        unicodedata.category(value) in {"Mn", "Mc", "Me"}
        or unicodedata.combining(value) != 0
    )


def is_regional_indicator(value: str) -> bool:
    return 0x1F1E6 <= ord(value) <= 0x1F1FF


def assert_safe_boundary(text: str, position: int) -> None:
    if position <= 0 or position >= len(text):
        return
    value = text[position]
    previous = text[position - 1]

    assert not is_combining(value), position
    assert value != "\u200d" and previous != "\u200d", position
    assert not 0xFE00 <= ord(value) <= 0xFE0F, position
    assert not 0xE0100 <= ord(value) <= 0xE01EF, position
    assert not 0x1F3FB <= ord(value) <= 0x1F3FF, position
    assert not 0xE0020 <= ord(value) <= 0xE007F, position
    assert not (previous == "\r" and value == "\n"), position

    if is_regional_indicator(value):
        count = 0
        cursor = position - 1
        while cursor >= 0 and is_regional_indicator(text[cursor]):
            count += 1
            cursor -= 1
        assert count % 2 == 0, position


def test_txt_source_is_immutable_and_exact_across_crlf_bom_emoji_and_marks():
    text = "第一行 English\r\nemoji 👨‍👩‍👧‍👦 e\u0301\r\n第三行"
    raw = b"\xef\xbb\xbf" + text.encode("utf-8")

    parsed = parse(raw, source_format="txt")

    assert parsed.source_format == "txt"
    assert parsed.source_text == text
    assert parsed.original_sha256 == hashlib.sha256(raw).hexdigest()
    assert parsed.source_text_hash == digest_text(text)
    assert (parsed.target_chars, parsed.overlap_chars) == (
        DEFAULT_TARGET_CHARS,
        DEFAULT_OVERLAP_CHARS,
    )
    assert_exact(parsed)
    assert_body_covered(parsed)

    assert len(parsed.chunks) == 1
    chunk = parsed.chunks[0]
    assert chunk.kind == "text"
    assert chunk.spans[0].excerpt == text
    assert chunk.text == text
    assert chunk.structure_path[-1].kind == "paragraph"


def test_only_one_leading_bom_is_removed():
    raw = b"\xef\xbb\xbf\xef\xbb\xbfabc"
    parsed = parse(raw, source_format="txt")

    assert parsed.source_text == "\ufeffabc"
    assert parsed.original_sha256 == hashlib.sha256(raw).hexdigest()
    assert parsed.source_text_hash == digest_text("\ufeffabc")
    assert_exact(parsed)
    assert_body_covered(parsed)


@pytest.mark.parametrize(
    "raw",
    [
        b"\xff",
        b"abc\x80",
        b"\xed\xa0\x80",
    ],
)
def test_invalid_utf8_fails_finitely_without_echoing_bytes(raw):
    error = reject(
        lambda: parse(raw, source_format="txt"),
        "SOURCE_ENCODING_INVALID",
    )
    assert str(error) == (
        "SOURCE_ENCODING_INVALID: "
        + MESSAGES["SOURCE_ENCODING_INVALID"]
    )
    assert raw.hex() not in str(error)


@pytest.mark.parametrize("source_format", ["pdf", "docx", "", "MD", None, 123])
def test_unsupported_format_fails_before_reading_bytes(source_format):
    reject(
        lambda: parse(b"\xff", source_format=source_format),
        "SOURCE_FORMAT_UNSUPPORTED",
    )


@pytest.mark.parametrize(
    "version",
    ["", "bad version", "a" * 129, None, 1],
)
def test_invalid_document_version_fails_finitely(version):
    reject(
        lambda: parse(b"abc", version=version),
        "SOURCE_INPUT_INVALID",
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"target_chars": 0},
        {"target_chars": 4001},
        {"target_chars": True},
        {"target_chars": 1.0},
        {"target_chars": None},
        {"target_chars": 1},
        {"overlap_chars": -1},
        {"overlap_chars": 600},
        {"overlap_chars": True},
        {"overlap_chars": 1.5},
        {"max_source_bytes": 0},
        {"max_source_bytes": 64 * 1024 * 1024 + 1},
        {"max_source_bytes": True},
        {"max_source_bytes": 1.0},
    ],
)
def test_config_bounds_are_finite(overrides):
    reject(
        lambda: TextSourceConfig(**overrides),
        "SOURCE_CONFIG_INVALID",
    )


def test_config_accepts_its_finite_boundaries():
    default = TextSourceConfig()
    assert (default.target_chars, default.overlap_chars) == (
        DEFAULT_TARGET_CHARS,
        DEFAULT_OVERLAP_CHARS,
    )
    low = TextSourceConfig(
        target_chars=1,
        overlap_chars=0,
        max_source_bytes=1,
    )
    high = TextSourceConfig(
        target_chars=4000,
        overlap_chars=3999,
        max_source_bytes=64 * 1024 * 1024,
    )
    assert (low.target_chars, low.overlap_chars, low.max_source_bytes) == (
        1,
        0,
        1,
    )
    assert (
        high.target_chars,
        high.overlap_chars,
        high.max_source_bytes,
    ) == (4000, 3999, 64 * 1024 * 1024)


def test_parse_rejects_a_config_that_is_not_TextSourceConfig():
    reject(
        lambda: parse(b"abc", config={"target_chars": 1}),
        "SOURCE_CONFIG_INVALID",
    )
    reject(
        lambda: parse(b"abc", config=object()),
        "SOURCE_CONFIG_INVALID",
    )


def test_byte_limit_is_checked_before_decode_and_accepts_the_exact_limit():
    config = TextSourceConfig(
        target_chars=10,
        overlap_chars=0,
        max_source_bytes=4,
    )
    for raw in (b"12345", bytearray(b"12345"), memoryview(b"12345")):
        reject(
            lambda raw=raw: parse(
                raw,
                source_format="txt",
                config=config,
            ),
            "SOURCE_TOO_LARGE",
        )

    for raw in (b"1234", bytearray(b"1234"), memoryview(b"1234")):
        parsed = parse(raw, source_format="txt", config=config)
        assert parsed.source_text == "1234"
        assert parsed.original_sha256 == hashlib.sha256(b"1234").hexdigest()
        assert_exact(parsed)

    reject(
        lambda: parse(
            b"\xff\xff\xff\xff\xff",
            source_format="txt",
            config=config,
        ),
        "SOURCE_TOO_LARGE",
    )


@pytest.mark.parametrize("raw", ["text", None, 123, object()])
def test_parse_rejects_non_bytes_input(raw):
    reject(
        lambda: parse(raw, source_format="txt"),
        "SOURCE_INPUT_INVALID",
    )


def test_text_source_errors_have_finite_codes_and_messages():
    remapped = TextSourceError("NOT_A_CODE")
    assert remapped.code == "SOURCE_INPUT_INVALID"
    assert str(remapped) == (
        "SOURCE_INPUT_INVALID: "
        + MESSAGES["SOURCE_INPUT_INVALID"]
    )

    for code, message in MESSAGES.items():
        error = TextSourceError(code)
        assert error.code == code
        assert str(error) == f"{code}: {message}"


def test_valid_source_is_deterministic_and_ids_bind_version_configuration_and_range():
    raw = "# 标题\n\n正文".encode("utf-8")
    first = parse(raw, source_format="markdown")
    second = parse(raw, source_format="markdown")

    assert first == second
    assert [chunk.chunk_id for chunk in first.chunks] == [
        chunk.chunk_id for chunk in second.chunks
    ]
    assert first.original_sha256 == hashlib.sha256(raw).hexdigest()
    assert first.source_text_hash == digest_text(first.source_text)
    assert first.processing_config_id == second.processing_config_id
    assert_exact(first)
    assert_body_covered(first)

    changed_version = parse(
        raw,
        source_format="markdown",
        version="doc-version-2",
    )
    assert changed_version.processing_config_id == first.processing_config_id
    assert [chunk.chunk_id for chunk in changed_version.chunks] != [
        chunk.chunk_id for chunk in first.chunks
    ]

    changed_config = parse(
        raw,
        source_format="markdown",
        config=TextSourceConfig(target_chars=601, overlap_chars=0),
    )
    assert changed_config.processing_config_id != first.processing_config_id
    assert [chunk.chunk_id for chunk in changed_config.chunks] != [
        chunk.chunk_id for chunk in first.chunks
    ]

    changed_text = parse(
        "# 标题\n\n正文!".encode("utf-8"),
        source_format="markdown",
    )
    assert [chunk.chunk_id for chunk in changed_text.chunks] != [
        chunk.chunk_id for chunk in first.chunks
    ]

    changed_format = parse(raw, source_format="txt")
    assert changed_format.processing_config_id != first.processing_config_id
    assert [chunk.chunk_id for chunk in changed_format.chunks] != [
        chunk.chunk_id for chunk in first.chunks
    ]


def test_span_structure_and_forged_chunk_invariants_are_enforced():
    with pytest.raises(ValueError):
        SourceSpan(0, 1, "ab", digest_text("ab"))
    with pytest.raises(ValueError):
        SourceSpan(0, 1, "a", "A" * 64)
    with pytest.raises(ValueError):
        StructureNode("heading", "#", 0, 1)
    with pytest.raises(ValueError):
        StructureNode("paragraph", "ab", 0, 1)
    with pytest.raises(ValueError):
        StructureNode("paragraph", "a", 0, 1, level=1)

    span = SourceSpan(0, 1, "a", digest_text("a"))
    with pytest.raises(ValueError):
        SourceChunk("0" * 64, 0, "text", (span, span), ())

    parsed = parse(b"abc", source_format="txt")
    forged = dataclasses.replace(parsed.chunks[0], chunk_id="0" * 64)
    with pytest.raises(ValueError):
        dataclasses.replace(parsed, chunks=(forged,))
    with pytest.raises(ValueError):
        dataclasses.replace(parsed, source_text_hash="0" * 64)


def test_default_chunking_is_600_code_points_with_80_overlap():
    text = "a" * 2000
    parsed = parse(text.encode("utf-8"), source_format="txt")

    assert (parsed.target_chars, parsed.overlap_chars) == (600, 80)
    spans = [chunk.spans[0] for chunk in parsed.chunks]
    assert [span.start for span in spans] == [0, 520, 1040, 1560]
    assert [span.end for span in spans] == [600, 1120, 1640, 2000]
    assert all(span.length <= 600 for span in spans)
    assert_exact(parsed)
    assert_body_covered(parsed)


def test_chunking_parameters_are_bounded_and_honoured():
    text = "a" * 1000
    overlap = parse(
        text.encode("utf-8"),
        source_format="txt",
        config=TextSourceConfig(target_chars=100, overlap_chars=20),
    )
    starts = [chunk.spans[0].start for chunk in overlap.chunks]
    assert starts[:3] == [0, 80, 160]
    assert all(
        span.length <= 100
        for chunk in overlap.chunks
        for span in chunk.spans
    )
    assert_exact(overlap)
    assert_body_covered(overlap)

    no_overlap = parse(
        text.encode("utf-8"),
        source_format="txt",
        config=TextSourceConfig(target_chars=100, overlap_chars=0),
    )
    spans = [chunk.spans[0] for chunk in no_overlap.chunks]
    assert len(spans) == 10
    assert all(
        previous.end == current.start
        for previous, current in zip(spans, spans[1:])
    )
    assert "".join(span.excerpt for span in spans) == text
    assert_exact(no_overlap)
    assert_body_covered(no_overlap)


def test_long_unicode_text_splits_on_code_points_without_breaking_clusters():
    text = "👨‍👩‍👧‍👦" * 8 + "e\u0301" * 8 + "🇨🇳" * 4
    parsed = parse(
        text.encode("utf-8"),
        source_format="txt",
        config=TextSourceConfig(target_chars=10, overlap_chars=0),
    )

    assert parsed.source_text == text
    assert_exact(parsed)
    assert_body_covered(parsed)

    spans = [span for chunk in parsed.chunks for span in chunk.spans]
    assert "".join(span.excerpt for span in spans) == text
    assert all(span.length <= 10 for span in spans)
    for span in spans:
        assert_safe_boundary(text, span.start)
        assert_safe_boundary(text, span.end)


def test_crlf_pair_is_never_split_between_carriage_return_and_line_feed():
    text = "a" * 99 + "\r\n" + "b" * 99
    parsed = parse(
        text.encode("utf-8"),
        source_format="txt",
        config=TextSourceConfig(target_chars=100, overlap_chars=0),
    )

    spans = [span for chunk in parsed.chunks for span in chunk.spans]
    assert "".join(span.excerpt for span in spans) == text
    boundaries = {
        position
        for span in spans
        for position in (span.start, span.end)
    }
    assert 100 not in boundaries
    for position in boundaries:
        assert_safe_boundary(text, position)
    assert_exact(parsed)
    assert_body_covered(parsed)


def test_unsatisfiable_tiny_target_fails_finitely_for_protected_clusters():
    config = TextSourceConfig(target_chars=1, overlap_chars=0)
    for text in ("e\u0301", "👨‍👩‍👧‍👦", "🇨🇳", "क\u093e"):
        reject(
            lambda text=text: parse(
                text.encode("utf-8"),
                source_format="txt",
                config=config,
            ),
            "SOURCE_CHUNK_UNSATISFIABLE",
        )


def test_spacing_combining_mark_stays_with_its_base_when_it_fits():
    text = "क\u093e" + "ख"
    parsed = parse(
        text.encode("utf-8"),
        source_format="txt",
        config=TextSourceConfig(target_chars=2, overlap_chars=0),
    )

    assert parsed.source_text == text
    assert [
        span.excerpt
        for chunk in parsed.chunks
        for span in chunk.spans
    ] == ["क\u093e", "ख"]
    assert_exact(parsed)
    assert_body_covered(parsed)


def test_markdown_headings_and_fenced_code_keeps_real_hierarchy():
    text = (
        "# 一级标题\n\n"
        "引言\n\n"
        "## 二级标题\n\n"
        "```python\n"
        "# 这不是标题\n"
        "print('x')\n"
        "```\n\n"
        "### 三级标题\n\n"
        "正文\n"
    )
    parsed = parse(text.encode("utf-8"), source_format="markdown")

    assert_exact(parsed)
    assert_body_covered(parsed)

    headings = [chunk for chunk in parsed.chunks if chunk.kind == "heading"]
    assert [
        chunk.spans[0].excerpt for chunk in headings
    ] == ["# 一级标题", "## 二级标题", "### 三级标题"]
    assert [chunk.structure_path[-1].level for chunk in headings] == [1, 2, 3]
    assert [
        tuple(node.text for node in chunk.structure_path[:-1])
        for chunk in headings
    ] == [
        (),
        ("# 一级标题",),
        ("# 一级标题", "## 二级标题"),
    ]

    code_chunks = [chunk for chunk in parsed.chunks if chunk.kind == "code"]
    assert len(code_chunks) == 1
    code = code_chunks[0]
    assert code.spans[0].excerpt.startswith("```python")
    assert code.spans[0].excerpt.endswith("```")
    assert "# 这不是标题" in code.spans[0].excerpt
    assert code.structure_path[-1].kind == "code"
    assert all(
        node.kind != "heading" or node.text != "# 这不是标题"
        for chunk in parsed.chunks
        for node in chunk.structure_path
    )

    paragraphs = [chunk for chunk in parsed.chunks if chunk.kind == "text"]
    assert [
        chunk.spans[0].excerpt for chunk in paragraphs
    ] == ["引言", "正文"]
    assert [
        tuple(node.text for node in chunk.structure_path)
        for chunk in paragraphs
    ] == [
        ("# 一级标题",),
        ("# 一级标题", "## 二级标题", "### 三级标题"),
    ]


def test_markdown_paragraph_keeps_mixed_chinese_english_and_newline():
    text = "# Doc\n\nFirst line English\n第二行中文\n"
    parsed = parse(text.encode("utf-8"), source_format="markdown")

    paragraphs = [chunk for chunk in parsed.chunks if chunk.kind == "text"]
    assert len(paragraphs) == 1
    assert paragraphs[0].spans[0].excerpt == (
        "First line English\n第二行中文"
    )
    assert paragraphs[0].structure_path[0].text == "# Doc"
    assert_exact(parsed)
    assert_body_covered(parsed)


def test_setext_heading_is_recognised_and_body_keeps_it_in_path():
    text = "标题\n===\n\n正文"
    parsed = parse(text.encode("utf-8"), source_format="markdown")

    headings = [chunk for chunk in parsed.chunks if chunk.kind == "heading"]
    assert len(headings) == 1
    assert headings[0].spans[0].excerpt == "标题\n==="
    assert headings[0].structure_path[-1].level == 1

    body = [chunk for chunk in parsed.chunks if chunk.kind == "text"]
    assert len(body) == 1
    assert body[0].spans[0].excerpt == "正文"
    assert body[0].structure_path[0].text == "标题\n==="
    assert_exact(parsed)
    assert_body_covered(parsed)


def test_atx_heading_marker_requires_separating_whitespace():
    text = "#不是标题\n\n# 是标题"
    parsed = parse(text.encode("utf-8"), source_format="markdown")

    headings = [chunk for chunk in parsed.chunks if chunk.kind == "heading"]
    assert len(headings) == 1
    assert headings[0].spans[0].excerpt == "# 是标题"
    paragraphs = [chunk for chunk in parsed.chunks if chunk.kind == "text"]
    assert len(paragraphs) == 1
    assert paragraphs[0].spans[0].excerpt == "#不是标题"
    assert_exact(parsed)
    assert_body_covered(parsed)


def test_markdown_table_keeps_condition_header_unit_and_rows_as_real_spans():
    text = (
        "# 温度表\n\n"
        "适用条件：环境温度 0–40 °C。\n\n"
        "| 名称 | 温度 |\n"
        "| --- | --- |\n"
        "| 单位 | °C |\n"
        "| 室内 | 20 |\n"
        "| 室外 | 30 |\n"
    )
    parsed = parse(text.encode("utf-8"), source_format="markdown")

    assert_exact(parsed)
    assert_body_covered(parsed)

    table_chunks = [chunk for chunk in parsed.chunks if chunk.kind == "table"]
    assert len(table_chunks) == 1
    table = table_chunks[0]
    assert [span.excerpt for span in table.spans] == [
        "适用条件：环境温度 0–40 °C。",
        "| 名称 | 温度 |",
        "| --- | --- |",
        "| 单位 | °C |",
        "| 室内 | 20 |",
        "| 室外 | 30 |",
    ]
    assert table.structure_path[0].kind == "heading"
    assert table.structure_path[0].text == "# 温度表"
    assert [node.kind for node in table.structure_path[1:]] == [
        "table_context",
        "table_header",
        "table_delimiter",
        "table_unit",
        "table_row",
        "table_row",
    ]
    assert all(
        table.spans[index].end < table.spans[index + 1].start
        for index in range(len(table.spans) - 1)
    )
    assert all("\n" not in span.excerpt for span in table.spans)
    assert len(table.text) <= parsed.target_chars

    context_chunks = [chunk for chunk in parsed.chunks if chunk.kind == "text"]
    assert [
        chunk.spans[0].excerpt for chunk in context_chunks
    ] == ["适用条件：环境温度 0–40 °C。"]


def test_table_rows_split_without_losing_header_or_unit():
    text = (
        "| 名称 | 温度 |\n"
        "| --- | --- |\n"
        "| 单位 | °C |\n"
        "| 室内 | 20 |\n"
        "| 室外 | 30 |\n"
        "| 走廊 | 25 |\n"
        "| 阳台 | 28 |\n"
    )
    parsed = parse(
        text.encode("utf-8"),
        source_format="markdown",
        config=TextSourceConfig(target_chars=70, overlap_chars=0),
    )

    assert_exact(parsed)
    assert_body_covered(parsed)

    table_chunks = [chunk for chunk in parsed.chunks if chunk.kind == "table"]
    assert len(table_chunks) >= 2
    for chunk in table_chunks:
        assert [span.excerpt for span in chunk.spans[:3]] == [
            "| 名称 | 温度 |",
            "| --- | --- |",
            "| 单位 | °C |",
        ]
        assert chunk.structure_path[0].kind == "table_header"
        assert len(chunk.text) <= 70

    rows = [
        node.text
        for chunk in table_chunks
        for node in chunk.structure_path
        if node.kind == "table_row"
    ]
    assert rows == [
        "| 室内 | 20 |",
        "| 室外 | 30 |",
        "| 走廊 | 25 |",
        "| 阳台 | 28 |",
    ]


@pytest.mark.parametrize(
    ("text", "target"),
    [
        (
            "| 名称 | 温度 |\n"
            "| --- | --- |\n"
            "| 单位 | °C |\n"
            "| 室内 | 20 |\n",
            10,
        ),
        (
            "适用条件：" + "x" * 100 + "\n\n"
            "| 名称 | 温度 |\n"
            "| --- | --- |\n"
            "| 室内 | 20 |\n",
            60,
        ),
        (
            "| 名称 | 温度 |\n"
            "| --- | --- |\n"
            "| 室内 | " + "x" * 100 + " |\n",
            60,
        ),
    ],
)
def test_unsatisfiable_table_groups_fail_without_dropping_headers(text, target):
    reject(
        lambda: parse(
            text.encode("utf-8"),
            source_format="markdown",
            config=TextSourceConfig(
                target_chars=target,
                overlap_chars=0,
            ),
        ),
        "SOURCE_CHUNK_UNSATISFIABLE",
    )


def test_table_syntax_inside_fenced_code_is_not_a_table():
    text = "```md\n| a | b |\n| --- | --- |\n```\n"
    parsed = parse(text.encode("utf-8"), source_format="markdown")

    assert [chunk.kind for chunk in parsed.chunks] == ["code"]
    assert "| a | b |" in parsed.chunks[0].text
    assert_exact(parsed)
    assert_body_covered(parsed)


def test_whitespace_only_source_is_not_silently_empty():
    text = " \r\n\t\n"
    parsed = parse(text.encode("utf-8"), source_format="txt")

    assert parsed.source_text == text
    assert parsed.chunks
    assert all(chunk.kind == "text" for chunk in parsed.chunks)
    assert "".join(
        span.excerpt
        for chunk in parsed.chunks
        for span in chunk.spans
    ) == text
    assert_exact(parsed)


def test_html_and_links_are_inert_text_and_no_external_modules_are_imported():
    text = (
        "<script>alert('x')</script>\n"
        "[link](https://example.invalid/a)\n"
    )
    parsed = parse(text.encode("utf-8"), source_format="txt")

    assert parsed.source_text == text
    assert "<script>" in parsed.chunks[0].text
    assert_exact(parsed)
    assert_body_covered(parsed)

    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    assert names.isdisjoint(
        {
            "aiohttp",
            "fastapi",
            "httpx",
            "psycopg",
            "requests",
            "socket",
            "sqlalchemy",
            "subprocess",
            "urllib",
        }
    )
