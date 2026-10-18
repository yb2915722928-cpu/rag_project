"""Framework-free TXT/Markdown parsing with exact, citable source spans.

The module deliberately depends only on the Python standard library.  It takes
bytes that were already accepted by the upload boundary, decodes them as strict
UTF-8, and produces immutable source text plus bounded chunks.  A chunk never
carries a fabricated continuous range: every chunk is an ordered tuple of real
source spans, and every span is an exact slice of the immutable source text.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import re
import unicodedata
from typing import Final, Literal


TextSourceFormat = Literal["txt", "markdown"]
StructureKind = Literal[
    "heading",
    "paragraph",
    "code",
    "table_context",
    "table_header",
    "table_delimiter",
    "table_unit",
    "table_row",
]
ChunkKind = Literal["text", "code", "table", "heading"]

DEFAULT_TARGET_CHARS: Final = 600
DEFAULT_OVERLAP_CHARS: Final = 80
DEFAULT_MAX_SOURCE_BYTES: Final = 32 * 1024 * 1024
MAX_TARGET_CHARS: Final = 4000
MAX_SOURCE_BYTES_CEILING: Final = 64 * 1024 * 1024
MAX_LINES: Final = 200_000
PROCESSING_SCHEMA: Final = "rag-text-processing.v1"
CHUNKER_VERSION: Final = "rag-text-chunker.v1"

MESSAGES: Final[dict[str, str]] = {
    "SOURCE_FORMAT_UNSUPPORTED": "Only TXT and Markdown text sources are supported.",
    "SOURCE_INPUT_INVALID": "The text source input is invalid.",
    "SOURCE_TOO_LARGE": "The text source exceeds the configured byte limit.",
    "SOURCE_ENCODING_INVALID": "The text source is not valid UTF-8.",
    "SOURCE_CONFIG_INVALID": "The text source configuration is invalid.",
    "SOURCE_CHUNK_UNSATISFIABLE": (
        "A required source group cannot fit within the configured chunk limit."
    ),
}

_FORMATS: Final = frozenset({"txt", "markdown"})
_STRUCTURE_KINDS: Final = frozenset(
    {
        "heading", "paragraph", "code", "table_context",
        "table_header", "table_delimiter", "table_unit", "table_row",
    }
)
_CHUNK_KINDS: Final = frozenset({"text", "code", "table", "heading"})
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_VERSION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
_SETEXT_RE = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
_LIST_OR_QUOTE_RE = re.compile(
    r"^ {0,3}(?:[-+*](?:[ \t]+|$)|\d{1,9}[.)](?:[ \t]+|$)|>)"
)
_DELIMITER_CELL_RE = re.compile(r":?-+:?\Z")
_BOUNDARY_CHARS: Final = frozenset(" \t\r\n。！？；，、.!?;,:)]}）】」』")
_EXTEND_CATEGORIES: Final = frozenset({"Mn", "Mc", "Me"})
_UNIT_LABELS: Final = frozenset(
    {"单位", "计量单位", "unit", "units", "uom", "unit of measure"}
)
_CONDITION_MARKERS: Final = (
    "适用", "条件", "前提", "注意", "注", "说明", "限制", "范围",
    "环境", "温度", "湿度", "applicable", "condition", "note", "caution",
    "limit", "constraint", "assumption", "requirement",
)


class TextSourceError(ValueError):
    """Finite domain failure; messages never contain source content."""

    def __init__(self, code: str) -> None:
        if code not in MESSAGES:
            code = "SOURCE_INPUT_INVALID"
        self.code = code
        super().__init__(f"{code}: {MESSAGES[code]}")


@dataclass(frozen=True)
class TextSourceConfig:
    """Bounded parsing and chunking settings.

    ``target_chars`` and ``overlap_chars`` are Unicode code-point counts, not
    UTF-8 byte counts.  A CRLF pair and a grapheme cluster are never split; a
    target too small for the current cluster fails finitely instead of
    corrupting source identity.  Overlap must leave forward progress.
    """

    target_chars: int = DEFAULT_TARGET_CHARS
    overlap_chars: int = DEFAULT_OVERLAP_CHARS
    max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES

    def __post_init__(self) -> None:
        if type(self.target_chars) is not int or not (
            1 <= self.target_chars <= MAX_TARGET_CHARS
        ):
            raise TextSourceError("SOURCE_CONFIG_INVALID")
        if type(self.overlap_chars) is not int or not (
            0 <= self.overlap_chars < self.target_chars
        ):
            raise TextSourceError("SOURCE_CONFIG_INVALID")
        if type(self.max_source_bytes) is not int or not (
            1 <= self.max_source_bytes <= MAX_SOURCE_BYTES_CEILING
        ):
            raise TextSourceError("SOURCE_CONFIG_INVALID")


@dataclass(frozen=True)
class StructureNode:
    """A real source slice identifying one structural part of a chunk."""

    kind: StructureKind
    text: str
    start: int
    end: int
    level: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or self.kind not in _STRUCTURE_KINDS:
            raise ValueError("structure kind must be finite")
        if not isinstance(self.text, str):
            raise ValueError("structure text must be a string")
        if type(self.start) is not int or self.start < 0:
            raise ValueError("structure start must be a nonnegative integer")
        if type(self.end) is not int or self.end < self.start:
            raise ValueError("structure end must not precede start")
        if len(self.text) != self.end - self.start:
            raise ValueError("structure text must match its code-point range")
        if self.kind == "heading":
            if type(self.level) is not int or not 1 <= self.level <= 6:
                raise ValueError("heading level must be between one and six")
        elif self.level is not None:
            raise ValueError("only a heading carries a level")


@dataclass(frozen=True)
class SourceSpan:
    """One exact ``source_text[start:end]`` slice and its UTF-8 SHA-256."""

    start: int
    end: int
    excerpt: str
    sha256: str

    def __post_init__(self) -> None:
        if type(self.start) is not int or self.start < 0:
            raise ValueError("span start must be a nonnegative integer")
        if type(self.end) is not int or self.end <= self.start:
            raise ValueError("span end must be greater than start")
        if not isinstance(self.excerpt, str):
            raise ValueError("span excerpt must be a string")
        if len(self.excerpt) != self.end - self.start:
            raise ValueError("span excerpt must match its code-point range")
        if not _is_sha256(self.sha256):
            raise ValueError("span hash must be lowercase SHA-256")

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class SourceChunk:
    """An ordered set of real spans; never a fabricated continuous range."""

    chunk_id: str
    ordinal: int
    kind: ChunkKind
    spans: tuple[SourceSpan, ...]
    structure_path: tuple[StructureNode, ...]

    def __post_init__(self) -> None:
        if not _is_sha256(self.chunk_id):
            raise ValueError("chunk id must be lowercase SHA-256")
        if type(self.ordinal) is not int or self.ordinal < 0:
            raise ValueError("chunk ordinal must be a nonnegative integer")
        if not isinstance(self.kind, str) or self.kind not in _CHUNK_KINDS:
            raise ValueError("chunk kind must be finite")
        if not isinstance(self.spans, tuple) or not self.spans:
            raise ValueError("a chunk needs at least one span")
        previous: SourceSpan | None = None
        for span in self.spans:
            if not isinstance(span, SourceSpan):
                raise ValueError("chunk spans must be SourceSpan values")
            if previous is not None and previous.end > span.start:
                raise ValueError("chunk spans must be ordered and non-overlapping")
            previous = span
        if not isinstance(self.structure_path, tuple):
            raise ValueError("structure path must be a tuple")
        previous_node: StructureNode | None = None
        for node in self.structure_path:
            if not isinstance(node, StructureNode):
                raise ValueError("structure path must contain StructureNode values")
            if previous_node is not None and previous_node.start > node.start:
                raise ValueError("structure path must be ordered")
            previous_node = node

    @property
    def text(self) -> str:
        """Presentation text derived from real spans.

        Single-span chunks return the exact excerpt.  Multi-span table chunks
        join the exact excerpts with one newline; the ``spans`` remain the
        authoritative citation ranges and no continuous source range is implied.
        """

        return "\n".join(span.excerpt for span in self.spans)


@dataclass(frozen=True)
class ParsedSource:
    """Immutable source text and its bounded chunks."""

    source_format: TextSourceFormat
    document_version_id: str
    original_sha256: str
    source_text: str
    source_text_hash: str
    processing_config_id: str
    target_chars: int
    overlap_chars: int
    chunks: tuple[SourceChunk, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_format, str)
            or self.source_format not in _FORMATS
        ):
            raise ValueError("source format must be txt or markdown")
        if (
            not isinstance(self.document_version_id, str)
            or _VERSION_RE.fullmatch(self.document_version_id) is None
        ):
            raise ValueError("document version id has an invalid format")
        if not _is_sha256(self.original_sha256):
            raise ValueError("original hash must be lowercase SHA-256")
        if not isinstance(self.source_text, str):
            raise ValueError("source text must be a string")
        if not _is_sha256(self.source_text_hash):
            raise ValueError("source text hash must be lowercase SHA-256")
        if self.source_text_hash != _sha256_text(self.source_text):
            raise ValueError("source text hash does not match source text")
        if not _is_sha256(self.processing_config_id):
            raise ValueError("processing config id must be lowercase SHA-256")
        if type(self.target_chars) is not int or not (
            1 <= self.target_chars <= MAX_TARGET_CHARS
        ):
            raise ValueError("target_chars is invalid")
        if type(self.overlap_chars) is not int or not (
            0 <= self.overlap_chars < self.target_chars
        ):
            raise ValueError("overlap_chars is invalid")
        expected_config = _processing_config_id(
            self.source_format, self.target_chars, self.overlap_chars
        )
        if self.processing_config_id != expected_config:
            raise ValueError("processing config id does not match configuration")
        if not isinstance(self.chunks, tuple):
            raise ValueError("chunks must be a tuple")

        source_length = len(self.source_text)
        seen_ids: set[str] = set()
        for index, chunk in enumerate(self.chunks):
            if not isinstance(chunk, SourceChunk):
                raise ValueError("chunks must contain SourceChunk values")
            if chunk.ordinal != index:
                raise ValueError("chunk ordinals must match tuple order")
            if chunk.chunk_id in seen_ids:
                raise ValueError("chunk ids must be unique")
            seen_ids.add(chunk.chunk_id)
            if chunk.chunk_id != _chunk_id(
                document_version_id=self.document_version_id,
                processing_config_id=self.processing_config_id,
                kind=chunk.kind,
                spans=chunk.spans,
                structure_path=chunk.structure_path,
            ):
                raise ValueError("chunk id does not match its source identity")
            if len(chunk.text) > self.target_chars:
                raise ValueError("chunk text exceeds the configured target")
            for span in chunk.spans:
                if span.start > source_length or span.end > source_length:
                    raise ValueError("chunk span is outside source text")
                if self.source_text[span.start:span.end] != span.excerpt:
                    raise ValueError("chunk span is not an exact source slice")
                if _sha256_text(span.excerpt) != span.sha256:
                    raise ValueError("chunk span hash does not match excerpt")
            for node in chunk.structure_path:
                if node.start > source_length or node.end > source_length:
                    raise ValueError("structure node is outside source text")
                if self.source_text[node.start:node.end] != node.text:
                    raise ValueError("structure node is not an exact source slice")


def parse_text_source(
    raw: bytes | bytearray | memoryview,
    *,
    document_version_id: str,
    source_format: TextSourceFormat | str,
    config: TextSourceConfig | None = None,
) -> ParsedSource:
    """Parse already-uploaded TXT or Markdown bytes into bounded source chunks.

    The original bytes are never mutated.  Strict UTF-8 decoding is used, and
    only one leading UTF-8 BOM code point is removed.  CRLF, lone CR/LF,
    combining characters and all other whitespace remain exactly as extracted.
    ``original_sha256`` covers the raw bytes; ``source_text_hash`` covers the
    processed immutable UTF-8 text.
    """

    if (
        not isinstance(document_version_id, str)
        or _VERSION_RE.fullmatch(document_version_id) is None
    ):
        raise TextSourceError("SOURCE_INPUT_INVALID")
    if not isinstance(source_format, str) or source_format not in _FORMATS:
        raise TextSourceError("SOURCE_FORMAT_UNSUPPORTED")
    if config is None:
        config = TextSourceConfig()
    elif not isinstance(config, TextSourceConfig):
        raise TextSourceError("SOURCE_CONFIG_INVALID")

    source_format_value: TextSourceFormat = (
        "txt" if source_format == "txt" else "markdown"
    )
    data = _read_bytes(raw, config.max_source_bytes)
    original_sha256 = hashlib.sha256(data).hexdigest()
    try:
        decoded = data.decode("utf-8")
    except UnicodeDecodeError:
        raise TextSourceError("SOURCE_ENCODING_INVALID") from None
    text = decoded[1:] if decoded.startswith("\ufeff") else decoded
    processing_config_id = _processing_config_id(
        source_format_value, config.target_chars, config.overlap_chars
    )
    chunks = _build_chunks(
        text=text,
        source_format=source_format_value,
        document_version_id=document_version_id,
        processing_config_id=processing_config_id,
        target_chars=config.target_chars,
        overlap_chars=config.overlap_chars,
    )
    return ParsedSource(
        source_format=source_format_value,
        document_version_id=document_version_id,
        original_sha256=original_sha256,
        source_text=text,
        source_text_hash=_sha256_text(text),
        processing_config_id=processing_config_id,
        target_chars=config.target_chars,
        overlap_chars=config.overlap_chars,
        chunks=chunks,
    )


def _read_bytes(
    raw: bytes | bytearray | memoryview, limit: int
) -> bytes:
    if isinstance(raw, memoryview):
        try:
            size = raw.nbytes
        except (TypeError, ValueError):
            raise TextSourceError("SOURCE_INPUT_INVALID") from None
    elif isinstance(raw, (bytes, bytearray)):
        size = len(raw)
    else:
        raise TextSourceError("SOURCE_INPUT_INVALID")
    if size > limit:
        raise TextSourceError("SOURCE_TOO_LARGE")
    try:
        return raw.tobytes() if isinstance(raw, memoryview) else bytes(raw)
    except (TypeError, ValueError):
        raise TextSourceError("SOURCE_INPUT_INVALID") from None


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _processing_config_id(
    source_format: TextSourceFormat, target_chars: int, overlap_chars: int
) -> str:
    payload = {
        "schema": PROCESSING_SCHEMA,
        "format": source_format,
        "bom_policy": "strip_utf8_bom",
        "newline_policy": "preserve",
        "unicode_policy": "none",
        "chunker": CHUNKER_VERSION,
        "target_chars": target_chars,
        "overlap_chars": overlap_chars,
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _chunk_id(
    *,
    document_version_id: str,
    processing_config_id: str,
    kind: ChunkKind,
    spans: tuple[SourceSpan, ...],
    structure_path: tuple[StructureNode, ...],
) -> str:
    payload = {
        "schema": CHUNKER_VERSION,
        "document_version_id": document_version_id,
        "processing_config_id": processing_config_id,
        "kind": kind,
        "spans": [[span.start, span.end, span.sha256] for span in spans],
        "structure_path": [
            [node.kind, node.level, node.text, node.start, node.end]
            for node in structure_path
        ],
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class _Line:
    index: int
    start: int
    content_end: int
    end: int
    text: str


@dataclass(frozen=True)
class _Fence:
    char: str
    length: int


@dataclass(frozen=True)
class _Table:
    header: _Line
    delimiter: _Line
    unit: _Line | None
    rows: tuple[_Line, ...]
    context_index: int | None
    start: int
    end: int
    next_index: int


@dataclass(frozen=True)
class _Block:
    kind: Literal["heading", "paragraph", "code", "table"]
    start: int
    end: int
    line: _Line | None = None
    lines: tuple[_Line, ...] = ()
    level: int | None = None
    table: _Table | None = None


def _iter_lines(text: str) -> list[_Line]:
    lines: list[_Line] = []
    start = 0
    index = 0
    length = len(text)
    while start < length:
        if index >= MAX_LINES:
            # A byte bound alone still permits millions of tiny line objects.
            # Refuse a pathological line count instead of allocating without a
            # useful finite bound.
            raise TextSourceError("SOURCE_TOO_LARGE")
        position = start
        while position < length and text[position] not in "\r\n":
            position += 1
        content_end = position
        if position < length:
            if (
                text[position] == "\r"
                and position + 1 < length
                and text[position + 1] == "\n"
            ):
                end = position + 2
            else:
                end = position + 1
        else:
            end = length
        lines.append(
            _Line(
                index=index,
                start=start,
                content_end=content_end,
                end=end,
                text=text[start:content_end],
            )
        )
        index += 1
        start = end
    return lines


def _is_blank(line: _Line) -> bool:
    return line.text.strip() == ""


def _heading(line_text: str) -> tuple[int, str] | None:
    match = _HEADING_RE.fullmatch(line_text)
    if match is None:
        return None
    after = line_text[match.end(1):]
    if after and after[0] not in " \t":
        # CommonMark: an ATX heading needs whitespace or end-of-line after the
        # opening sequence, so "#hashtag" is ordinary body text.
        return None
    return len(match.group(1)), match.group(2) or ""


def _setext_underline(line_text: str) -> int | None:
    match = _SETEXT_RE.fullmatch(line_text)
    if match is None:
        return None
    if match.group(1)[0] == "=":
        return 1
    # A lone "-" or "--" is not a setext underline; it must be at least two.
    return 2 if len(match.group(1)) >= 2 else None


def _fence_start(line_text: str) -> _Fence | None:
    match = _FENCE_OPEN_RE.fullmatch(line_text)
    if match is None:
        return None
    marker = match.group(1)
    if marker[0] == "`" and "`" in match.group(2):
        # CommonMark: a backtick fence's info string cannot contain backticks.
        return None
    return _Fence(char=marker[0], length=len(marker))


def _fence_close(line_text: str, opening: _Fence) -> bool:
    match = _FENCE_CLOSE_RE.fullmatch(line_text)
    if match is None:
        return False
    marker = match.group(1)
    return marker[0] == opening.char and len(marker) >= opening.length


def _split_table_row(value: str) -> tuple[str, ...] | None:
    cells: list[str] = []
    buffer: list[str] = []
    saw_pipe = False
    in_code = False
    code_run = 0
    position = 0
    length = len(value)
    while position < length:
        char = value[position]
        if char == "\\" and position + 1 < length:
            buffer.append(value[position:position + 2])
            position += 2
            continue
        if char == "`":
            run = 1
            while position + run < length and value[position + run] == "`":
                run += 1
            if not in_code:
                in_code = True
                code_run = run
            elif run == code_run:
                in_code = False
            buffer.append(value[position:position + run])
            position += run
            continue
        if char == "|" and not in_code:
            saw_pipe = True
            cells.append("".join(buffer))
            buffer = []
            position += 1
            continue
        buffer.append(char)
        position += 1
    if not saw_pipe:
        return None
    cells.append("".join(buffer))
    trimmed = [cell.strip() for cell in cells]
    if trimmed and trimmed[0] == "" and value.lstrip().startswith("|"):
        trimmed = trimmed[1:]
    if trimmed and trimmed[-1] == "" and value.rstrip().endswith("|"):
        trimmed = trimmed[:-1]
    if not trimmed:
        return None
    return tuple(trimmed)


def _is_delimiter_cell(value: str) -> bool:
    return _DELIMITER_CELL_RE.fullmatch(value) is not None


def _is_table_pair(header: _Line, delimiter: _Line) -> bool:
    if _is_blank(header) or _is_blank(delimiter):
        return False
    header_cells = _split_table_row(header.text)
    delimiter_cells = _split_table_row(delimiter.text)
    if header_cells is None or delimiter_cells is None:
        return False
    if not header_cells or len(header_cells) != len(delimiter_cells):
        return False
    if not any(header_cells):
        return False
    return all(_is_delimiter_cell(cell) for cell in delimiter_cells)


def _is_unit_row(cells: tuple[str, ...]) -> bool:
    label = next((cell for cell in cells if cell), "")
    normalized = label.strip("*_`~").strip().casefold().rstrip(":：").strip()
    return normalized in _UNIT_LABELS


def _looks_like_condition(value: str) -> bool:
    """Recognise a lead-in condition/note without inventing source content.

    This only decides whether a blank-line separated preceding paragraph is
    kept as table context.  It never changes, trims or synthesises any text.
    """

    normalized = value.strip().lstrip(">*-+ \t").casefold()
    if any(normalized.startswith(marker) for marker in _CONDITION_MARKERS):
        return True
    if normalized.rstrip().endswith((":", "：")):
        return True
    return any(
        token in normalized
        for token in ("下表", "下列", "以下表格", "following table", "table below")
    )


def _parse_table(lines: list[_Line], index: int) -> _Table | None:
    if index + 1 >= len(lines):
        return None
    header = lines[index]
    delimiter = lines[index + 1]
    if not _is_table_pair(header, delimiter):
        return None
    rows: list[_Line] = []
    unit: _Line | None = None
    cursor = index + 2
    if (
        cursor < len(lines)
        and not _is_blank(lines[cursor])
        and _fence_start(lines[cursor].text) is None
        and _heading(lines[cursor].text) is None
    ):
        cells = _split_table_row(lines[cursor].text)
        if cells is not None and _is_unit_row(cells):
            unit = lines[cursor]
            cursor += 1
    while cursor < len(lines):
        candidate = lines[cursor]
        if _is_blank(candidate):
            break
        if _fence_start(candidate.text) is not None:
            break
        if _heading(candidate.text) is not None:
            break
        if cursor + 1 < len(lines) and _is_table_pair(candidate, lines[cursor + 1]):
            break
        if _split_table_row(candidate.text) is None:
            break
        rows.append(candidate)
        cursor += 1
    end_line = rows[-1] if rows else (unit if unit is not None else delimiter)
    return _Table(
        header=header,
        delimiter=delimiter,
        unit=unit,
        rows=tuple(rows),
        context_index=None,
        start=header.start,
        end=end_line.content_end,
        next_index=cursor,
    )


def _parse_plain_blocks(lines: list[_Line]) -> list[_Block]:
    blocks: list[_Block] = []
    index = 0
    total = len(lines)
    while index < total:
        if _is_blank(lines[index]):
            index += 1
            continue
        first = index
        index += 1
        while index < total and not _is_blank(lines[index]):
            index += 1
        last = lines[index - 1]
        blocks.append(
            _Block(
                kind="paragraph",
                start=lines[first].start,
                end=last.content_end,
                lines=tuple(lines[first:index]),
            )
        )
    return blocks


def _parse_blocks(text: str, *, markdown: bool) -> list[_Block]:
    lines = _iter_lines(text)
    if not markdown:
        return _parse_plain_blocks(lines)
    blocks: list[_Block] = []
    index = 0
    total = len(lines)
    while index < total:
        line = lines[index]
        if _is_blank(line):
            index += 1
            continue
        fence = _fence_start(line.text)
        if fence is not None:
            first = index
            index += 1
            while index < total:
                closes = _fence_close(lines[index].text, fence)
                index += 1
                if closes:
                    break
            last = lines[index - 1]
            blocks.append(
                _Block(
                    kind="code",
                    start=lines[first].start,
                    end=last.content_end,
                    lines=tuple(lines[first:index]),
                )
            )
            continue
        heading = _heading(line.text)
        if heading is not None:
            level, _title = heading
            blocks.append(
                _Block(
                    kind="heading",
                    start=line.start,
                    end=line.content_end,
                    line=line,
                    level=level,
                )
            )
            index += 1
            continue
        if (
            line.text.strip()
            and not _LIST_OR_QUOTE_RE.match(line.text)
            and index + 1 < total
        ):
            setext_level = _setext_underline(lines[index + 1].text)
            if setext_level is not None and not _is_blank(lines[index + 1]):
                # Setext headings are real headings in Markdown; the title and
                # underline stay separate exact spans so neither is invented.
                blocks.append(
                    _Block(
                        kind="heading",
                        start=line.start,
                        end=lines[index + 1].content_end,
                        line=line,
                        lines=(line, lines[index + 1]),
                        level=setext_level,
                    )
                )
                index += 2
                continue
        table = _parse_table(lines, index)
        if table is not None:
            context_index: int | None = None
            if blocks and blocks[-1].kind == "paragraph":
                previous = blocks[-1]
                last_line = previous.lines[-1] if previous.lines else None
                if last_line is not None:
                    gap = table.header.index - last_line.index
                    if gap == 1 or (
                        gap == 2
                        and _looks_like_condition(
                            text[previous.start:previous.end]
                        )
                    ):
                        context_index = len(blocks) - 1
            table = replace(table, context_index=context_index)
            blocks.append(
                _Block(
                    kind="table",
                    start=table.start,
                    end=table.end,
                    table=table,
                )
            )
            index = table.next_index
            continue
        first = index
        index += 1
        while index < total:
            candidate = lines[index]
            if _is_blank(candidate):
                break
            if _fence_start(candidate.text) is not None:
                break
            if _heading(candidate.text) is not None:
                break
            if _parse_table(lines, index) is not None:
                break
            index += 1
        last = lines[index - 1]
        blocks.append(
            _Block(
                kind="paragraph",
                start=lines[first].start,
                end=last.content_end,
                lines=tuple(lines[first:index]),
            )
        )
    return blocks


def _is_extend(value: str) -> bool:
    if value in {"\u200c", "\u200d"}:
        return True
    if unicodedata.combining(value) != 0:
        return True
    if unicodedata.category(value) in _EXTEND_CATEGORIES:
        return True
    code = ord(value)
    if 0xFE00 <= code <= 0xFE0F:
        return True
    if 0xE0100 <= code <= 0xE01EF:
        return True
    if 0x1F3FB <= code <= 0x1F3FF:
        return True
    if 0xE0020 <= code <= 0xE007F:
        return True
    return False


def _is_regional_indicator(value: str) -> bool:
    return 0x1F1E6 <= ord(value) <= 0x1F1FF


def _is_cluster_boundary(text: str, position: int) -> bool:
    """Whether a chunk may start or end at ``position`` without corruption.

    This is intentionally narrower than full Unicode grapheme segmentation:
    it protects combining marks, ZWJ sequences, emoji modifiers/variation
    selectors, regional-indicator pairs and CRLF.  It never accepts a split
    that the supported source matrix could observe as a broken character.
    """

    if position <= 0 or position >= len(text):
        return True
    value = text[position]
    if _is_extend(value):
        return False
    if text[position - 1] == "\u200d":
        return False
    if text[position - 1] == "\r" and value == "\n":
        return False
    if _is_regional_indicator(value):
        count = 0
        cursor = position - 1
        while cursor >= 0 and _is_regional_indicator(text[cursor]):
            count += 1
            cursor -= 1
        if count % 2 == 1:
            return False
    return True


def _find_boundary(text: str, start: int, limit: int) -> int | None:
    lower = start + max(1, (limit - start) // 2)
    for position in range(limit - 1, lower - 1, -1):
        value = text[position]
        if value not in _BOUNDARY_CHARS:
            continue
        if (
            value == "\r"
            and position + 1 < len(text)
            and text[position + 1] == "\n"
        ):
            return position
        if value == "\n" and position > 0 and text[position - 1] == "\r":
            return position - 1
        return position + 1
    return None


def _safe_end(text: str, start: int, limit: int, end: int) -> int:
    if limit >= end:
        return end
    while start < limit < end and not _is_cluster_boundary(text, limit):
        limit -= 1
    return limit


def _safe_start(text: str, start: int, cursor: int, end: int) -> int:
    while start < cursor < end and not _is_cluster_boundary(text, cursor):
        cursor -= 1
    return cursor


def _split_span(
    text: str, start: int, end: int, target: int, overlap: int
) -> tuple[tuple[int, int], ...]:
    if end <= start:
        return ()
    result: list[tuple[int, int]] = []
    cursor = start
    while cursor < end:
        limit = min(cursor + target, end)
        if limit < end:
            boundary = _find_boundary(text, cursor, limit)
            if boundary is not None and boundary > cursor:
                limit = boundary
        limit = _safe_end(text, cursor, limit, end)
        if limit <= cursor:
            # The target window lies entirely inside one protected cluster.
            # Splitting it would corrupt source identity; fail finitely.
            raise TextSourceError("SOURCE_CHUNK_UNSATISFIABLE")
        result.append((cursor, limit))
        if limit >= end:
            break
        if overlap:
            next_cursor = max(cursor + 1, limit - overlap)
        else:
            next_cursor = limit
        next_cursor = _safe_start(text, cursor, next_cursor, end)
        if next_cursor <= cursor:
            next_cursor = limit
        if next_cursor > end:
            next_cursor = end
        cursor = next_cursor
    return tuple(result)


def _node(
    kind: StructureKind,
    text: str,
    start: int,
    end: int,
    *,
    level: int | None = None,
) -> StructureNode:
    return StructureNode(
        kind=kind, text=text[start:end], start=start, end=end, level=level
    )


def _span(text: str, start: int, end: int) -> SourceSpan:
    excerpt = text[start:end]
    if not excerpt:
        raise TextSourceError("SOURCE_CHUNK_UNSATISFIABLE")
    return SourceSpan(
        start=start, end=end, excerpt=excerpt, sha256=_sha256_text(excerpt)
    )


def _make_chunk(
    *,
    document_version_id: str,
    processing_config_id: str,
    kind: ChunkKind,
    spans: tuple[SourceSpan, ...],
    structure_path: tuple[StructureNode, ...],
    ordinal: int,
) -> SourceChunk:
    return SourceChunk(
        chunk_id=_chunk_id(
            document_version_id=document_version_id,
            processing_config_id=processing_config_id,
            kind=kind,
            spans=spans,
            structure_path=structure_path,
        ),
        ordinal=ordinal,
        kind=kind,
        spans=spans,
        structure_path=structure_path,
    )


def _table_chunks(
    *,
    table: _Table,
    blocks: list[_Block],
    text: str,
    heading_path: tuple[StructureNode, ...],
    document_version_id: str,
    processing_config_id: str,
    target_chars: int,
    start_ordinal: int,
) -> tuple[list[SourceChunk], int]:
    # The header, delimiter and unit row are the non-droppable atomic base of
    # every chunk for this table.  They are cited as separate real spans so no
    # continuous range can imply text that the model did not receive.
    base_spans: list[SourceSpan] = [
        _span(text, table.header.start, table.header.content_end),
        _span(text, table.delimiter.start, table.delimiter.content_end),
    ]
    extra_path: list[StructureNode] = [
        _node("table_header", text, table.header.start, table.header.content_end),
        _node(
            "table_delimiter", text,
            table.delimiter.start, table.delimiter.content_end,
        ),
    ]
    if table.unit is not None:
        base_spans.append(_span(text, table.unit.start, table.unit.content_end))
        extra_path.append(
            _node("table_unit", text, table.unit.start, table.unit.content_end)
        )

    base_text_length = sum(span.length for span in base_spans) + max(
        0, len(base_spans) - 1
    )
    if base_text_length > target_chars:
        raise TextSourceError("SOURCE_CHUNK_UNSATISFIABLE")

    context_span: SourceSpan | None = None
    context_node: StructureNode | None = None
    if table.context_index is not None:
        context = blocks[table.context_index]
        context_length = context.end - context.start
        available = target_chars - base_text_length - 1
        if context_length <= available:
            context_span = _span(text, context.start, context.end)
            context_node = _node(
                "table_context", text, context.start, context.end
            )
        else:
            # The applicable condition is part of the table's atomic source
            # group.  A truncated condition can invert its meaning, so refuse
            # instead of deleting the condition or splitting it across chunks.
            raise TextSourceError("SOURCE_CHUNK_UNSATISFIABLE")
    if context_span is not None:
        base_spans.insert(0, context_span)
    if context_node is not None:
        extra_path.insert(0, context_node)
    base_text_length = sum(span.length for span in base_spans) + max(
        0, len(base_spans) - 1
    )
    if base_text_length > target_chars:
        raise TextSourceError("SOURCE_CHUNK_UNSATISFIABLE")
    base_path = heading_path + tuple(extra_path)
    chunks: list[SourceChunk] = []

    def emit(rows: list[_Line]) -> None:
        nonlocal start_ordinal
        spans = tuple(base_spans) + tuple(
            _span(text, row.start, row.content_end) for row in rows
        )
        path = base_path + tuple(
            _node("table_row", text, row.start, row.content_end) for row in rows
        )
        chunks.append(
            _make_chunk(
                document_version_id=document_version_id,
                processing_config_id=processing_config_id,
                kind="table",
                spans=spans,
                structure_path=path,
                ordinal=start_ordinal,
            )
        )
        start_ordinal += 1

    if not table.rows:
        emit([])
        return chunks, start_ordinal

    current: list[_Line] = []
    current_length = base_text_length
    for row in table.rows:
        row_length = row.content_end - row.start
        candidate_length = current_length + 1 + row_length
        if current and candidate_length > target_chars:
            emit(current)
            current = []
            current_length = base_text_length
            candidate_length = base_text_length + 1 + row_length
        if candidate_length > target_chars:
            raise TextSourceError("SOURCE_CHUNK_UNSATISFIABLE")
        current.append(row)
        current_length = candidate_length
    if current:
        emit(current)
    return chunks, start_ordinal


def _build_chunks(
    *,
    text: str,
    source_format: TextSourceFormat,
    document_version_id: str,
    processing_config_id: str,
    target_chars: int,
    overlap_chars: int,
) -> tuple[SourceChunk, ...]:
    blocks = _parse_blocks(text, markdown=source_format == "markdown")
    chunks: list[SourceChunk] = []
    heading_stack: list[StructureNode] = []
    ordinal = 0

    def append_split(
        kind: ChunkKind,
        block: _Block,
        path: tuple[StructureNode, ...],
        node_kind: StructureKind | None = None,
        level: int | None = None,
    ) -> None:
        nonlocal ordinal
        for span_start, span_end in _split_span(
            text, block.start, block.end, target_chars, overlap_chars
        ):
            piece_path = path
            if node_kind is not None:
                piece_path = path + (
                    _node(
                        node_kind, text, span_start, span_end, level=level
                    ),
                )
            chunks.append(
                _make_chunk(
                    document_version_id=document_version_id,
                    processing_config_id=processing_config_id,
                    kind=kind,
                    spans=(_span(text, span_start, span_end),),
                    structure_path=piece_path,
                    ordinal=ordinal,
                )
            )
            ordinal += 1

    for index, block in enumerate(blocks):
        if block.kind == "heading":
            if block.level is None or block.line is None:
                raise ValueError("heading block is incomplete")
            while (
                heading_stack
                and (heading_stack[-1].level or 0) >= block.level
            ):
                heading_stack.pop()
            heading_stack.append(
                _node(
                    "heading",
                    text,
                    block.start,
                    block.end,
                    level=block.level,
                )
            )
            # A heading is real source text as well as structure.  Emitting it
            # as its own span guarantees that no title is lost when the block
            # after it is a table that consumes a preceding condition paragraph.
            append_split(
                "heading",
                block,
                tuple(heading_stack[:-1]),
                node_kind="heading",
                level=block.level,
            )
            continue
        path = tuple(heading_stack)
        if block.kind == "paragraph":
            append_split("text", block, path, node_kind="paragraph")
        elif block.kind == "code":
            append_split("code", block, path, node_kind="code")
        elif block.kind == "table":
            if block.table is None:
                raise ValueError("table block is incomplete")
            table_chunks, ordinal = _table_chunks(
                table=block.table,
                blocks=blocks,
                text=text,
                heading_path=path,
                document_version_id=document_version_id,
                processing_config_id=processing_config_id,
                target_chars=target_chars,
                start_ordinal=ordinal,
            )
            chunks.extend(table_chunks)
    if not chunks and text:
        # Whitespace-only or otherwise structure-free body still has source
        # content.  Emit bounded exact spans instead of silently returning an
        # empty index for a non-empty immutable text.
        append_split(
            "text",
            _Block(kind="paragraph", start=0, end=len(text)),
            (),
            node_kind="paragraph",
        )
    return tuple(chunks)


__all__ = [
    "CHUNKER_VERSION",
    "DEFAULT_MAX_SOURCE_BYTES",
    "DEFAULT_OVERLAP_CHARS",
    "DEFAULT_TARGET_CHARS",
    "MAX_SOURCE_BYTES_CEILING",
    "MAX_LINES",
    "MAX_TARGET_CHARS",
    "MESSAGES",
    "PROCESSING_SCHEMA",
    "ParsedSource",
    "SourceChunk",
    "SourceSpan",
    "StructureKind",
    "StructureNode",
    "TextSourceConfig",
    "TextSourceError",
    "TextSourceFormat",
    "ChunkKind",
    "parse_text_source",
]
