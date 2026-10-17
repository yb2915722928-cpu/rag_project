# Story 1.1 C1-NZ 原生负零金额交付记录

日期：2026-10-17（Asia/Shanghai）。性质：源码准备；**未运行任何 Python 或测试**。

本记录不开启 Linux 开发者测试、正式契约生成或父 Story 完成门。B、C1-NZ 与 Story 1.1 均不得据此判定通过。

## 规格与认领

已完整读取：

- [AGENTS.md](/E:/aaa-project/rag/AGENTS.md:1)
- [C1 原生负零规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-decimal-zero.md:1)
- 其 context：[公共模型规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-contract-models.md:1)
- [独立预审 C1-NZ 段](/E:/aaa-project/rag/docs/story-1-1-preparation-review.md:389)

规格允许的写入范围为：

- [scalars.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:1) 的金额处理与序列化。
- 新增 [test_decimal_wire_zero.py](/E:/aaa-project/rag/backend/tests/test_decimal_wire_zero.py:1)。
- 本交付记录。
- [story-1-1-contracts-delivery.md](/E:/aaa-project/rag/docs/story-1-1-contracts-delivery.md:1) 中 `attempts=2` 的统计文字。

未修改 `public.py`、`PUBLIC_MODELS`/`PUBLIC_ENUMS`、其他测试、HTTP/H/worker/deploy、锁、迁移、主控台账或 Git index。

## 缺陷与选择

C1-NZ：`decimal_amount` 接受原生 `Decimal`；`Decimal('-0')`/`('-0.00')` 是有限数且不 `< 0`，因此通过非负校验；`FiniteDecimal` 的 `format(value, "f")` 输出 `-0`/`-0.00`，既不匹配自身 schema `^\d+(?:\.\d+)?$`，也无法被 `Money.model_validate_json` 重新读入。

本修复按规格允许的第二条路径处理：**把带符号零规范化为无负号零，保留原小数位**；不放宽 schema 接受负号，也不拒绝合法零值。

## 最小修改

[scalars.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:94)：

1. `decimal_amount` 在既有有限性/非负校验后增加 `result.is_zero() and result.is_signed()` 分支，用 `copy_abs()` 去掉原生负零符号。字符串负号仍在正则处被拒；真实负数、非有限数、float、非字符串规则未变。
2. 新增 `decimal_wire_text(value: Decimal) -> str`：拒绝非 Decimal 和非有限值，对带符号零再次 `copy_abs()`，再 `format(value, "f")`，保证序列化不输出负号且保留精度（`Decimal('1.20')` → `"1.20"`，`Decimal('0.100')` → `"0.100"`）。
3. `FiniteDecimal` 的 `PlainSerializer` 改用该函数；schema 的 `type: string`、`pattern: ^\d+(?:\.\d+)?$` 与注释均未改。

未改 `Money` DTO：它已直接使用 `FiniteDecimal`，`PUBLIC_MODELS`/`PUBLIC_ENUMS` 与 schema 形状不变。

## 新测试源码

[test_decimal_wire_zero.py](/E:/aaa-project/rag/backend/tests/test_decimal_wire_zero.py:1) 覆盖：

- `Decimal('-0')`、`'-0.0'`、`'-0.00'`、`'-0.000000'` → `"0"`、`"0.0"`、`"0.00"`、`"0.000000"`，`money.amount` 无符号，`model_dump(mode="json")` 与 `model_dump_json()` 均可被 `Money.model_validate_json` 读回。
- `estimate`/`bill` 两种已知来源。
- 无符号零与正金额（`0.100`、`1.20`、`12345.678900`）精度保持。
- `decimal_wire_text` 输出匹配导出 schema 的 pattern，并可用 `TypeAdapter(FiniteDecimal)` 重新读入。
- `"-0"`/`"-0.00"`/`"-0.0"` wire 字符串仍被拒绝。
- 真实负数（`Decimal("-0.01")`、`"-1.00"` 等）仍被拒绝。
- 非有限 Decimal、float、`-0.0`、int、bool、None 仍被拒绝。
- `source="unknown"` 仍输出 `amount: null`，不以 0 代替未知。
- `Money` schema 的 amount pattern 与 required 字段不变。

## 交付文档统计更正

[story-1-1-contracts-delivery.md](/E:/aaa-project/rag/docs/story-1-1-contracts-delivery.md:86) 原写 `attempts=2` 为“两条用例”，实际 manifest 中为三条：`h.http.valid-retrieval`、`h.http.reject.unauthenticated`、`h.http.reject.unknown-field`。已改为“三条用例”并列出名称；未改其他统计。

## 当前 SHA-256

以下为冻结时本地内容 hash，不是提交或运行证据。

| 文件 | SHA-256 |
| --- | --- |
| `backend/src/rag_app/contracts/scalars.py` | `20891e0360637ff38b289735d879ac805fdefc0d4f6eb99ba277783d77ed4fd6` |
| `backend/tests/test_decimal_wire_zero.py` | `fda17b643bb72a553943a2772ff9556d76fb8b4170d73f89d6d12fe1bfc32612` |
| `docs/story-1-1-contracts-delivery.md` | `4f77889124e1b11a27e4ccb4032e89fa33a81cfd2f4094e0789e347ad8fe1b8f` |
| `docs/story-1-1-decimal-zero-delivery.md` | 本文件不嵌入自身 hash |

## 未执行与风险

- **未执行**：任何 Python 导入、pytest、`test_decimal_wire_zero.py`、`test_public_contracts.py`、HTTP、生成器、`--check`、样例执行。
- **未执行**：固定 Gitee commit、Linux 精确 CPython 3.12.8、`uv sync --locked`、正式 OpenAPI/schema/TS、独立 Step 5 与独立审查。
- 风险：`decimal_wire_text` 在反序列化时已归一化，但仍做一次防御性检查；若未来允许未经验证的 Decimal 直接进入序列化，这里会拒绝非有限值。
- 风险：保留小数位意味着 `"-0.00"` 输出 `"0.00"` 而不是 `"0"`；这是规格要求的精度保持，消费方不应假设固定两位。
- 风险：本修复不改 JSON Schema 表达力；跨字段 `Money` 规则仍由 Pydantic 运行时校验，schema 只声明结构与 pattern。
- 冻结后原预审文件 F1–F4 结论不变，不能把本次修复当作 B 或父 Story 通过。

提交收尾说明：上文局部hash属于对应静态交付/复核时点。其后仅清理少量源码/配置/文档的单个EOF空白行，字节前缀一致性已记录；原始wire输入保持原字节。最终源码与Git规范化内容hash以 [准备来源快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-preparation-source-hashes.json:1) 为准，EOF前后证明见 [收尾证据](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-eof-normalization.json:1)。这些均不构成任何运行通过。
