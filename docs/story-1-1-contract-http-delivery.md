# Story 1.1 B0c 有界维护 HTTP 与 OpenAPI 交付记录

日期：2026-10-17（Asia/Shanghai）。
状态：`in-progress`，本地实现形成可读取快照，尚未运行开发者测试或通过验收。
本记录不将代码落盘、静态核对或 H 的历史结果视为本次 HTTP 测试通过。

## 规格与职责

已完整读取[当前短规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-contract-http.md:1)
及其 frontmatter 的两份 context：
[项目规则](/E:/aaa-project/rag/AGENTS.md:1)、
[后端契约真源交接](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-backend-contract-source-dispatch.md:1)。
随后重新完整读取了主会话更新后的短规格，按其五种 Response 限制调整实现。
本任务承接主会话已完成的 bmad-build Step 3，不重新启动规格工作流。

沿用本实现会话已核实的角色：`group/auto-gpt-6-1-sol / medium`，
会话 `01a148f1-834b-7920-82f2-bfa8a81d7ede`，父会话
`01a148e2-1e11-7322-9626-6cbafb956f12`。
没有新增模型或底层供应方身份核验结论。

唯一写入范围：

- [API 集成](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/api.py:1)。
- [维护探针与公共 HTTP 投影](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/contract_probe.py:1)。
- [专用 HTTP 测试](/E:/aaa-project/rag/backend/tests/test_contract_http.py:1)。
- [本交付记录](/E:/aaa-project/rag/docs/story-1-1-contract-http-delivery.md:1)。

未修改公模、H、配置、CLI、依赖锁、迁移或其他测试。
主会话授权的公模作者补充错误政策后，本任务仅只读集成其结果。

## 实现内容

`create_app(settings=None, *, contract_test_token=None)` 仅接受显式传入的
内存 `SecretStr` 测试令牌。缺省 `None` 时拒绝维护探针；不从环境或
配置读取令牌。`settings.environment == "production"` 时，即使显式传入
令牌也保持禁用。测试令牌只保存在闭包中，不进入配置、应用状态或 OpenAPI。

入口为 `POST /__maintenance/contracts/{model_name}`。模型查表从
`PUBLIC_MODELS` 筛选含 `schema_version`、`request_id`、`status`
的现有五种 Response，不另维护业务模型或字段定义：

| 模型 | HTTP 行为 |
| --- | --- |
| `AcceptedResponse` | 202 |
| `CompletedResponse` | 200 |
| `FailedResponse` | 使用其 `error.http_status` |
| `OperationResponse` | 200，包括含原失败 `error` 的状态夹具 |
| `RetrievalResponse` | 200 |

所有 HTTP 探针成功响应均使用相应 C2 公共包。`Money`、`Usage` 等 helper
只导出 OpenAPI schema，由 B 直接验证模型样例；授权后以其名称访问探针
返回 `RESOURCE_UNAVAILABLE`（404），未授权时仍返回 `AUTH_REQUIRED`，
不借 helper 名称探测绕过令牌。helper 不作为裸 HTTP 响应。

请求处理顺序为 H 有界协议读取、令牌校验、模型名称校验、公共模型校验。
令牌取固定 `X-RAG-Contract-Test` 原始请求头，拒绝缺失、重复或错误令牌，
使用 `secrets.compare_digest` 比较字节。不调用 `request.json()` 或
`request.body()`，不让框架预先装载请求体。未知字段和版本由公共模型拒绝。

探针仅验证并返回隔离 DTO 夹具，不创建或执行 operation，不授予业务权限，
不访问数据库或供应方。`status_url` 中的 `/operations/...` 只是既有 DTO
约束；没有注册业务 GET operation 路由。私有网关对 `/__maintenance`
的阻断由主会话与 D 协调，本任务未修改网关。

所有有限错误均通过 `PublicError.from_code` 投影为 `FailedResponse`。
沿用公模中的消息、状态码及 `retry_mode`，不维护平行错误政策：

- H 错误按其有限 code 投影。
- Pydantic `ValidationError` 和框架 `RequestValidationError` 只返回
  `VALIDATION_ERROR`，不序列化异常输入、`exc.errors()` 或原始异常。
- 九种既有 `SafeError` 保留原 code、固定消息及 503。
- 405 使用 `METHOD_NOT_ALLOWED`（405 / `none`）。
- 意外本地异常使用 `INTERNAL_ERROR`（500 / `none`），不误归类为供应方失败。
- 未授权、路由不存在、方法错误及模型校验失败的错误包不含私有 operation ID。

ASGI 中间件为每次 HTTP 尝试生成新的服务器 `request_id`，忽略客户端诊断 ID。
返回 DTO 的 `request_id` 替换为当前尝试 ID，同时设置 `X-Request-ID` 响应头。
成功、失败及框架 404/405 均设置 `Cache-Control: no-store`，移除 ETag、
Last-Modified、Expires、Age 及客户端或端点伪造的诊断头。私有 304 被拒绝，
不复用旧响应体。现有 `/health` liveness 响应体保持兼容。

OpenAPI 使用 `PUBLIC_MODELS` 和 Pydantic `models_json_schema` 同时生成
validation / serialization components，维护路径的 enum 和请求 `oneOf`
仅引用五种 Response；200、202 和失败响应也引用后端模型生成的 components。
全部 helper 仍生成 components。默认 `create_app()` 可导出相同 schema，
schema 不包含测试令牌值，不创建第二套手写业务 schema。

## 本地安全快照

以下三份代码与测试已停止修改，供主会话统一创建首次 Git 检查点。
状态仍为 `in-progress`；主会话明确交回修复前不继续改写。
本交付记录可继续补充固定提交号和真实运行证据。

| 文件 | SHA-256 |
| --- | --- |
| `api.py` | `a98f78c228b61f272a46dcb4e16970a0afe726e99879a970ae6ac7277d47ada3` |
| `contract_probe.py` | `0a6b4bc23436fb276a82ff94f02f32b19755221ade614500e2e1a6b1f47e7f98` |
| `test_contract_http.py` | `555b184ceb8cadd6b73ad3bcac8f096241c59eb1c55c78091f0ed008c3010ec6` |

只读集成的冻结公模：
[public.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/public.py:1)，
SHA-256 为 `bde6d8b50b7731b94204b285666ca9f337e836532a71c26a3c508c30bade5c69`，
与主会话提供的冻结值一致。

H 源和测试保持冻结，读取时哈希未变：

| 文件 | SHA-256 |
| --- | --- |
| [H 源](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:1) | `6e7964607cfd6407c3fef08c5f6140f810da8dd07ae23341062ac602b15d373b` |
| [H 测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:1) | `087e02881bfef96704669cbf076893e33853c7f0dc87f0deaa4ba964423244d9` |

## 实际执行与未执行

本次实际执行：完整读取规格和 context、只读核对公模/原 API/H 接口、
实现指定文件、静态阅读集成路径、读取并比对 SHA-256。
未执行 Python、导入、编译、pytest、HTTP 请求或 OpenAPI 导出；
因此没有可报告的本次运行通过数、耗时、JUnit 或运行产物。

主会话已报告 Git 认证存在真实网络阻塞；本实现者未重新探测认证、
执行 Git 操作、推送、服务器拉取、SFTP 或其他替代传输。
待主会话取得授权凭据、统一提交推送并在服务器拉取明确提交后，
才能运行下述开发者验证。H 的历史 `165 passed` 不自动归属于
本次 B0c，也不代表任何新 Git 提交已验证。

专用测试已编写以下检查，但均为 `not-executed`：

- 五个 Response 正例、202/失败/operation 状态语义，helper 名安全 404。
- 默认及生产禁用、令牌缺失/错误/重复、恒时比较、H 先于认证和模型校验。
- 请求体/头/结构超限、重复键、非法 UTF-8/代理项/非有限数、
  内容长度伪报、未知字段/版本。
- 非 BMP、组合字符、CRLF、显式 null 与缺省区别、新服务器诊断 ID。
- 真实 ASGI 小 chunk 切边与断流 `REQUEST_STREAM_ERROR` 投影。
- no-store、404/405、条件请求、清除私有验证器和禁止 304。
- 九种 SafeError 的 503、意外异常的 500、框架与模型错误的有限投影，
  响应、日志和捕获输出无哨兵秘密。
- 禁止调用无界请求装载器、测试中禁止外部 HTTP transport、
  隔离运行时不调用 UoW/数据库检查。
- 默认可导出且无令牌的 OpenAPI、五模型 enum/引用、
  全部公模 components 和所有 `$ref` 可解析。

## 固定提交到位后的测试步骤

由主会话统一安排 Git；在服务器独占
`/opt/rag-story-1-1/contract-http-work` 拉取明确提交。
执行前记录真实提交号、工作树状态和上述工件哈希；未拉到目标提交
不得运行另一个目录冒充。不要改动其他活动目录或 Compose。

以下为待执行命令，不是已运行证据。假定固定提交位于上述目录，
并使用精确 CPython 3.12.8：

```sh
cd /opt/rag-story-1-1/contract-http-work/backend
set -euo pipefail
mkdir -p evidence/contract-http
uv sync --locked --python 3.12.8
uv run --locked python -c 'import sys,platform; assert sys.version_info[:3] == (3,12,8); assert platform.python_implementation() == "CPython"; print(platform.platform()); print(sys.version)' \
  | tee evidence/contract-http/runtime.txt
uv run --locked python -m pytest \
  tests/test_contract_http.py tests/test_api.py tests/test_public_contracts.py tests/test_json_guard.py \
  -q --junitxml=evidence/contract-http/junit.xml \
  2>&1 | tee evidence/contract-http/pytest.txt
sha256sum src/rag_app/entrypoints/api.py \
  src/rag_app/entrypoints/contract_probe.py tests/test_contract_http.py \
  src/rag_app/contracts/public.py \
  src/rag_app/entrypoints/json_guard.py tests/test_json_guard.py \
  | tee evidence/contract-http/sha256.txt
```

`uv sync --locked`、导入或收集失败也须保留真实结果，不修改锁、不更换
解释器、不另建传输通道绕过。测试结果连同提交号、环境、哈希与 JUnit
最终归档到 `/fileOfRag/testOfRAG/metadata/story-1-1/contract-http/`
下按固定提交区分的证据目录；归档操作由主会话授权的执行者完成。

## 剩余边界与验收

当前阻塞是尚无可在服务器验证的固定 Git 提交；本子任务未通过开发者
测试门，更未通过独立验证、全新实例独立审查或后续 B 正式生成门。
测试发现的问题交回本实现者，修复后重新记录快照并执行相关回归。

中间件的 500 投影针对响应头尚未发送时的异常；本入口在发送响应头前
完成模型校验和 JSON 序列化。若未来加入流式端点，响应开始后的异常
不能重新投影为完整错误包，须单独设计与验证，不以当前探针证明流式恢复。
同样，本任务不处理 lifespan 启动/关闭错误的 HTTP 投影。

后续公开 GET operation 服务、业务授权、真实数据库与供应方、副作用、
网关规则、B 导出与浏览器由相应 Story/分段继续承担。
父 Story 四项 AC、真实 PG、锁定重建、四服务与全部独立验收门保持不变。
