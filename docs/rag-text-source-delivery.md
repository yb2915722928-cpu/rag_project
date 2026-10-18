# U2a TXT/Markdown 来源解析分块交付

状态：2026-10-18 首轮固定提交 `c5a8cb2` 已实测（1 failed / 60 passed），失败为测试期望错误，已本地定向修正待再次发布；Linux 精确 CPython 3.12.8 的通过运行尚未完成。父 Story 4.2 与 P0 五格式、embedding、索引集成均未由本交付证明。

## 文件与 hash

| 归属 | 文件 | SHA-256 |
| --- | --- | --- |
| 核心 | [text_source.py](/E:/aaa-project/rag/backend/src/rag_app/modules/indexing/text_source.py:1) | `6E8F22B7395C4241FA08E05EC38DF0BAD7F2F2CD288CF4F62B5BF641DC47E60D` |
| 测试 | [test_text_source.py](/E:/aaa-project/rag/backend/tests/test_text_source.py:1) | `18AF053198C3C6CD7453CAE2EF8C83DA45924C9A89A10A824C9F9F954E742C90` |

hash 为本地工作区原文件 hash，随后续任何编辑失效；服务器测试前以主控发布的固定提交重新计算。

## 集成入口

```python
from rag_app.modules.indexing.text_source import (
    ParsedSource, SourceChunk, SourceSpan, StructureNode,
    TextSourceConfig, TextSourceError, parse_text_source,
)

parsed = parse_text_source(
    raw_bytes,                       # bytes | bytearray | memoryview
    document_version_id="doc-ver-1",
    source_format="markdown",        # "txt" | "markdown"
    config=TextSourceConfig(),       # 可选，默认 600/80/32MiB
)
```

`ParsedSource`：`source_format`、`document_version_id`、`original_sha256`（原始字节）、`source_text`、`source_text_hash`（处理后 UTF-8 文本）、`processing_config_id`、`target_chars`、`overlap_chars`、`chunks`。

`SourceSpan`：`start`、`end`、`excerpt`、`sha256`、`length`；恒有 `source_text[start:end] == excerpt`。

`SourceChunk`：`chunk_id`、`ordinal`、`kind`（`text|code|table|heading`）、`spans`（有序、互不重叠的真实切片）、`structure_path`、`text`（仅展示用，多 span 以单个换行拼接）。`chunk_id` 由 `document_version_id`、`processing_config_id`、kind、spans 范围/hash 与 structure_path 决定。

`StructureNode.kind`：`heading|paragraph|code|table_context|table_header|table_delimiter|table_unit|table_row`；只有 heading 带 1–6 级 `level`。

`TextSourceError.code` 有限：`SOURCE_INPUT_INVALID`、`SOURCE_FORMAT_UNSUPPORTED`、`SOURCE_TOO_LARGE`、`SOURCE_ENCODING_INVALID`、`SOURCE_CONFIG_INVALID`、`SOURCE_CHUNK_UNSATISFIABLE`。消息不含原文、字节、URL 或路径。

## 已实现行为

- 严格 UTF-8；仅移除一个前导 UTF-8 BOM；CRLF/CR/LF、组合字符、空白原样保留，不做 NFC/NFD 或换行归一。
- 读取前按 `max_source_bytes` 拒绝超界；行对象数另有 `MAX_LINES` 上限；不做编码猜测。
- 长度、重叠、span 范围全部按 Unicode 码点；`target_chars` 1–4000，`overlap_chars` 0–`target_chars-1`，`max_source_bytes` 1–64MiB。
- 分块边界不拆 CRLF、组合/间距组合标记、ZWJ 序列、emoji 修饰与变体选择符、区域指示符对；无法在目标内保住受保护簇时 `SOURCE_CHUNK_UNSATISFIABLE`，不静默拆坏字符。
- Markdown 识别 ATX/Setext 标题，标题层级来自真实标题；围栏代码内 `#`、表格语法不当作结构；表格见下。
- 表格块以“表头 + 分隔行（+ 单位行）”为不可丢弃原子组，每块各自引用真实行 span，不用连续范围包裹未提供内容；前置条件/说明段落随表进入同一原子组，超限时有限失败而不是删条件或表头。
- 正文不执行 HTML/脚本、不抓链接。

## 测试

`test_text_source.py` 共 29 个测试函数、58 个收集用例（6 组参数化）加 3 个架构边界用例，固定提交首轮共收集 61 个用例；覆盖规格 I/O 矩阵：

| AC / 矩阵 | 主要用例 |
| --- | --- |
| 合法输入精确原文/范围/hash、稳定块 ID | `test_txt_source_is_immutable_and_exact_across_crlf_bom_emoji_and_marks`、`test_only_one_leading_bom_is_removed`、`test_valid_source_is_deterministic_and_ids_bind_version_configuration_and_range`、`test_default_chunking_is_600_code_points_with_80_overlap`、`test_chunking_parameters_are_bounded_and_honoured` |
| 标题/围栏/长段/Unicode 不拆坏 | `test_markdown_headings_and_fenced_code_keeps_real_hierarchy`、`test_setext_heading_is_recognised_and_body_keeps_it_in_path`、`test_atx_heading_marker_requires_separating_whitespace`、`test_long_unicode_text_splits_on_code_points_without_breaking_clusters`、`test_crlf_pair_is_never_split_between_carriage_return_and_line_feed`、`test_spacing_combining_mark_stays_with_its_base_when_it_fits` |
| 表格结构/必要表头单位条件/有限失败 | `test_markdown_table_keeps_condition_header_unit_and_rows_as_real_spans`、`test_table_rows_split_without_losing_header_or_unit`、`test_unsatisfiable_table_groups_fail_without_dropping_headers`、`test_table_syntax_inside_fenced_code_is_not_a_table` |
| 异常输入有限失败、无外部调用 | `test_invalid_utf8_fails_finitely_without_echoing_bytes`、`test_unsupported_format_fails_before_reading_bytes`、`test_invalid_document_version_fails_finitely`、`test_config_bounds_are_finite`、`test_byte_limit_is_checked_before_decode_and_accepts_the_exact_limit`、`test_parse_rejects_non_bytes_input`、`test_html_and_links_are_inert_text_and_no_external_modules_are_imported` |
| 数据类不变量/伪造拒绝 | `test_span_structure_and_forged_chunk_invariants_are_enforced`、`test_text_source_errors_have_finite_codes_and_messages` |

测试辅助 `assert_exact` 对每个用例复核：span 与 structure node 均为 `source_text` 精确切片、UTF-8 SHA-256 一致、chunk 文本不超上限、ordinal 连号且 chunk_id 唯一；`assert_body_covered` 复核非空白正文无丢失。

## 本次对核心的改动

仅一处、由测试暴露的真实缺陷：`_EXTEND_CATEGORIES` 由 `{"Mn","Me"}` 扩为 `{"Mn","Mc","Me"}`（[text_source.py](/E:/aaa-project/rag/backend/src/rag_app/modules/indexing/text_source.py:72)）。原实现会把天城文等“基字 + 间距组合标记（Mc）”拆到两个 span，违反“禁止拆坏 Unicode 字符”；修复后 `क\u093e` 在 target=1 时有限失败，在 target=2 时整簇保留。除此之外未改核心签名、分块策略或既有行为。

未借鉴或复制 WeKnora/MaxKB 代码，无外部来源引用条目。

## 固定提交 `c5a8cb26bdf373d2f390cc2f2abda48c9fa56710` 实测（失败，保留）

服务器会话 `ea39f441-3b2e-452c-a491-5eccf1f57c96`（Netcatty），检出 `/opt/rag-fastapi-main/repo`，HEAD 为该 commit，`git status --porcelain` 为空；解释器 `/opt/rag-story-1-2/venv-fixed/bin/python` 为 CPython 3.12.8；两文件 sha256 与交付一致（`6e8f22b7...e60d` / `9b4a886a...1c327`）。

命令（工作目录 `/opt/rag-fastapi-main/repo/backend`）：

```bash
PYTHONPATH=/opt/rag-fastapi-main/repo/backend/src /opt/rag-story-1-2/venv-fixed/bin/python \
  -m pytest tests/test_text_source.py tests/test_architecture.py \
  -p no:cacheprovider -q --junitxml=.../junit.xml
```

结果：退出码 1，61 收集，1 failed / 60 passed，耗时 2.32s。唯一失败：

```text
FAILED tests/test_text_source.py::test_markdown_headings_and_fenced_code_keeps_real_hierarchy
At index 0 diff: ('# 一级标题', '引言') != ('# 一级标题',)
```

归类：测试期望错误。实现将段落自身作为 `structure_path` 末节点（`append_split(..., node_kind="paragraph")`），首段落路径应为 `('# 一级标题', '引言')`，末段落应为 `('# 一级标题','## 二级标题','### 三级标题','正文')`；实现行为符合“结构路径来自实际段落”，不是核心缺陷。已仅修正该期望，核心未改（hash 仍为 `6e8f22b7...e60d`）。修正后测试 hash 为 `18af0531...2c90`。

证据：`/fileOfRag/testOfRAG/metadata/rag-api-mainline/U2a/c5a8cb2/{env-before.txt,pytest.log,exitcode.txt,junit.xml}`。

## 未完成 / 未验证

- 修正后测试在固定提交上的 Linux 精确 CPython 3.12.8 通过运行：未执行，待主控再次发布。
- 独立验证与独立审查：未开始；本文件不构成 PASS 或验收结论。
- 父 Story 4.2 的上传表集成、embedding、索引、发布原子切换，以及 P0 五格式解析：未实现、未验证。
- 本地只做了 AST 语法解析与必要的静态一致性核对，未运行项目、未运行 pytest。
