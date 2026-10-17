# RAG_all 公共契约导出

本目录只保存**由后端真源生成**的公共契约工件，以及生成器和边界样例。它不维护第二套手写业务类型。

## 唯一真源

- `backend/src/rag_app/contracts/public.py` 的 `PUBLIC_MODELS` 与 `PUBLIC_ENUMS`
- `backend/src/rag_app/entrypoints/api.py` 的 `create_app().openapi()`
- `backend/src/rag_app/entrypoints/json_guard.py` 的有界 JSON 入口

生成器只导入这些现有入口，不复制字段、枚举或错误政策。枚举经 `PUBLIC_ENUMS` + Pydantic `TypeAdapter` 导出，TypeScript 仍只来自导出 schema。后端模型或 OpenAPI 改变后，重新生成并提交差异。

## 命令

以下命令必须在固定 Git commit、精确 CPython 3.12.8 的 Linux 环境执行。`--project backend` 使用后端已锁依赖，不另行安装生成依赖。

```bash
# 生成 OpenAPI、按模型拆分的 JSON Schema 和 TypeScript 类型
uv run --project backend --locked python contracts/generate.py

# 只校验磁盘工件是否与后端真源一致，不写文件
uv run --project backend --locked python contracts/generate.py --check

# 执行 C1/C2/H 正负样例
uv run --project backend --locked python contracts/verify_samples.py
```

`verify_samples.py` 的退出码：

- `0`：全部可执行样例通过。
- `1`：有样例失败。
- `2`：有 `blocked` 样例；即使其余样例通过，也不能视为 B 完成。

当前源码准备阶段没有 `blocked` 样例；`comparison.v1` 只记录为延期能力，不进入样例分母。

## 负例必须是合法对象的单点变异

每条 `reject` 用例都声明 `control`：把目标违规去掉后必须被同一入口接受（直接引用一份合法样例文件或 `raw_generate`）。`reject` 还会声明 `error`/`error_contains`，要求拒绝原因命中目标规则，而不是被无关的业务校验顺带拒绝。C1 的重复键、NaN、Infinity、孤立 surrogate、顶层/嵌套未知字段都由 `c2/completed.json` 的单点变异派生。

HTTP 样例额外要求：响应 `Content-Type` 为 `application/json`、正文是 JSON object、包含 `schema_version`/`request_id`/`status`、由用例声明的后端 Response 模型验证、`X-Request-ID` 存在且与正文 `request_id` 一致、`Cache-Control: no-store` 且无缓存验证器。声明 `expected_error` 的用例会与 `PublicError.from_code(...)` 的完整有限策略（code/message/http_status/retry_mode/details）比对，并要求 `error.http_status` 等于实际 HTTP 状态。`attempts>1` 的用例要求两次尝试的诊断 ID 不复用。

## 生成物布局

```text
contracts/
  openapi.json                         # create_app().openapi() 的稳定 JSON
  manifest.json                        # 后端源文件/生成物 SHA-256 与版本记录
  schemas/
    capabilities.json                  # 能力到模型/文件的索引及未生成说明
    enums/<Enum>.{validation,serialization}.schema.json
    answer.v1/<Model>.{validation,serialization}.schema.json
    retrieval.v1/<Model>.{validation,serialization}.schema.json
    operation.v1/<Model>.{validation,serialization}.schema.json
  typescript/
    contracts.ts                       # 由 serialization schema 生成
    contracts.input.ts                 # 由 validation schema 生成
  samples/
    manifest.json
    c1/*.json
    c2/*.json
    h/*.json
```

`schemas/` 和 `typescript/` 是生成物；首次在固定提交上运行生成命令后才存在。生成器不写时间戳、随机值或绝对路径，输出可逐字节重建。

`manifest.json` 记录 `PUBLIC_MODELS` 名称、能力分组、生成器/后端源文件 SHA-256、运行解释器与 FastAPI/Pydantic 版本，以及每个生成物的 SHA-256。`--check` 同时检查内容、缺失文件和 `schemas/`/`typescript/` 下的意外残留文件。

枚举同样只来自后端 `PUBLIC_ENUMS`，经 `TypeAdapter` 导出；生成器不复制枚举值表。`contracts.ts`/`contracts.input.ts` 中的枚举类型由这些 schema 生成。

## 必须区分的两侧 schema

Pydantic 的 `mode="validation"` 和 `mode="serialization"` 并不总是相同：

- 部分 `BeforeValidator`/`PlainSerializer` 注解会让模式约束只出现在一侧。例如 `EvidenceBlock.evidence_id` 的长度/字符模式、`Money.currency` 的 `^[A-Z]{3}$`、`AcceptedResponse.status_url` 的受控路径约束。
- 因此生成器对每个模型同时输出 `*.validation.schema.json` 和 `*.serialization.schema.json`，不把一个文件伪装成完整输入/输出契约。
- `contracts.ts` 表达服务端序列化输出；`contracts.input.ts` 表达可接受的验证输入。两者都只由 schema 生成。

JSON Schema 只表达结构和字段级约束，不能表达 Pydantic 模型的 `model_validator` 跨字段规则（例如 `status`/`operation_state`/`error` 一致性、`outcome` 与 `facts/gaps/clarifications` 的关系、证据 span 与 excerpt 码点长度一致）。运行时权威仍是后端 Pydantic 模型；样例覆盖这些跨字段边界。

## 当前未生成的能力

- `comparison.v1`：`PUBLIC_MODELS` 中不存在比较能力响应/载荷模型。本目录不手写替代 schema；等待后端真源补齐。
- `job_state`：由 `PUBLIC_ENUMS['JobState']` 导出，C2 样例验证其 wire 合法/非法值，不依赖 DTO 字段引用。

`comparison.v1` 属于未来业务能力，按原延期规则不生成；它在样例中不设 `blocked` 项，也不以静态声明冒充已实现。

## 安全边界

- OpenAPI 中包含隔离的 `POST /__maintenance/contracts/{model_name}` 测试探针。它不是业务入口，默认禁用，生产环境必须被网关阻断；生成物不包含测试令牌。
- 样例和 schema 不包含秘密、正文、签名 URL、任意上游 body 或未认证私有 operation ID。
- 所有私有 HTTP 响应继续要求 `Cache-Control: no-store`；样例只检查该投影，不替代真实授权、数据库或供应商调用。
- 1 MiB JSON 上限只属于 `json_guard` 的 JSON 入口；原件二进制 PUT、下载、ZIP 和上游响应各自使用独立预算。当前没有原件 PUT 路由可执行该边界，样例只记录分界，不伪造通过。
- 故意非法的字节样例（非法 UTF-8、尾随垃圾等）只以 manifest 的 `raw_base64` 内联表示，不落成 `.json` 文件，避免 CI 的通用 JSON 校验器把仓库误判为损坏。
