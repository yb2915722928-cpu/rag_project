# Story 1.1 B0a 公共模型交付

日期：2026-10-17。状态：模型/测试文件冻结，等待主会话 Git 同步和开发者测试；独立依赖环境安装成功，远程开发者测试尚未执行，不能标记 B0a 或完整 B 通过。

## 范围与入口

仅修改以下四个文件；未修改 API、现有 errors、配置、锁、迁移、其他测试或公共状态：

- [scalars.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:1)：`WireText`、`StableId`、`UtcDateTime`、`FiniteDecimal`，以及 `scalar_length`、`scalar_slice`、`stable_json_bytes`、`strict_json_loads`。
- [public.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/public.py:1)：全部公共 DTO、有限状态枚举及 `PUBLIC_MODELS`。
- [test_public_contracts.py](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:1)：正负 wire 样例、JSON 往返及 schema 导出检查。
- 本交付记录。

`PUBLIC_MODELS` 使用准确类名作为键：

`Usage`、`Money`、`ErrorDetails`、`PublicError`、`EvidenceBlock`、`RetrievalPayload`、
`AcceptedResponse`、`Summary`、`Quantity`、`ConflictSides`、`Fact`、`Gap`、`AnswerPayload`、
`CompletedResponse`、`FailedResponse`、`OperationResponse`、`RetrievalResponse`。

## H/HTTP 与导出者调用

```python
from rag_app.contracts.public import PUBLIC_MODELS, PublicError
from rag_app.contracts.scalars import stable_json_bytes

model = PUBLIC_MODELS["AcceptedResponse"]
schema = model.model_json_schema(mode="validation")
wire_schema = model.model_json_schema(mode="serialization")
dto = model.model_validate_json(raw_utf8_json)
wire_bytes = stable_json_bytes(dto.model_dump(mode="json", exclude_unset=True))
safe_error = PublicError.from_code("VALIDATION_ERROR")
```

HTTP 直接使用这些模型，不手写平行 schema。需要保留缺省与显式 null 差异时使用 `exclude_unset=True`，不能用 `exclude_none=True`；常规完整响应可用 `model_dump(mode="json")`。

原始 JSON 应走上述 `model_validate_json`，或先 `strict_json_loads` 再 `model_validate`。前者显式拒重复键、非有限数字和非法 UTF-8。直接调用 Pydantic `TypeAdapter.validate_json` 或框架自己的先行 JSON 解码不能假定继承这个重复键检查；H 层需接入原始字节边界。

UTC wire 字符串要求 RFC3339 Z，Python 服务端 aware datetime 可归一到 UTC；输出统一 Z。无时区、数字 epoch、日期而非时间、非 Z 字符串均拒绝。保留微秒精度，不裁剪业务文本，不做 trim/NFC/换行重排。Unicode 示例包含中文、组合字符、emoji 和 CRLF；emoji 的长度是 1。

`AcceptedResponse.status_url` 只允许 `/operations/{operation_id}`，必须与同一对象 ID 完全一致；拒绝其他路径、绝对 URL、query、fragment、编码或目录跳转。该路径是本 DTO 的维护契约，HTTP 承接者须据此接入。

`CompletedResponse` 为扁平 `answer.v1`，四态 `answered/insufficient/clarify/conflict` 与公共 status 分离，含原时间、快照和服务器 evidence_catalog。事实引用、冲突双方、参数 quantity、状态与时间须一致。`RetrievalResponse` 的 retrieval_execution_id、deadline、evidence_catalog 直接位于顶层，无 generation operation，catalog 至多五块。`OperationResponse` 对 status/state/error 交叉校验，保留原失败 http_status，HTTP GET 自身状态由后续适配器处理。

`Usage(input_tokens=None, output_tokens=None, unknown=True)` 表示全部未知；部分已知时保留已知数字，存在 null 就必须 unknown=True，不用零代替未知。`Money(amount=None, currency=None, source="unknown")` 表示未知金额；已知金额要求十进制字符串或 Decimal、币种和 source=`estimate`/`bill`。拒绝浮点、非有限和负金额，输出字符串，累计使用 Decimal。

`PublicError.from_code` 只生成固定字典的 code/message/http_status/retry_mode；传任意上游消息或未知错误码会失败。details 只允许有限 field/reason 枚举及有界 retry_after_seconds，不接收目标 ID、URL、正文。身份/目标不可用错误拒绝 details；前置认证/输入错误拒绝私有 operation_id，GET operation 不能承载这些错误来旁路安全投影。错误 DTO 不执行授权；HTTP 必须先完成当前权限判断，不能仅凭 DTO 校验宣称已获授权。

2026-10-17 H/HTTP 唯一协调增量已完成并重新冻结：`REQUEST_HEADERS_LIMIT_EXCEEDED`=431，`UNSUPPORTED_MEDIA_TYPE`/`UNSUPPORTED_CONTENT_ENCODING`=415，`REQUEST_STREAM_ERROR`=400，`RESOURCE_UNAVAILABLE` 保持404，均 retry_mode=none。四个新增 H 前置错误禁止携带私有 operation_id，也不能借 OperationResponse 暴露该 ID。

九种既有 SafeError 代码现均进入公共有限 policy，message 直接取现有 MESSAGES，HTTP 均503；仅 DATABASE_CLEANUP_FAILED 使用 manual_reconcile，其余使用 none。HTTP 接入者统一调用 PublicError.from_code，不传诊断/清理异常对象或任意正文字符串。专用测试新增九种错误的原 code/message/503 保持、C2 envelope 往返、诊断 sentinel 不泄露、伪造消息/元数据拒绝，以及 policy/Literal/导出 enum 完全对齐检查。此增量仅修改 public.py 和专用测试；未修改 errors.py、API、A1 或其他实现。以下 hash 已更新，但本增量测试仍待固定 Git 提交同步后运行。

后续唯一协调增量已补齐并再次冻结：METHOD_NOT_ALLOWED→405/none，固定安全文本 `Method not allowed.`；INTERNAL_ERROR→500/none，固定安全文本 `Internal server error.`。二者同步加入 policy、ErrorCode Literal、FailedResponse 前置无 operation_id 集合与 OperationResponse 拒绝集合；专用测试补充 C2 往返、固定文本/状态/重试模式、伪造正文/诊断拒绝以及 ID 不泄露。未修改 HTTP 文件。以下为本次最终冻结 hash，测试仍未执行。

## 开发者验证状态

已读取短规格的全部 frontmatter context，并核对其引用的公共答案四态与最小错误字典。主会话反馈的非法 bytes literal、emoji 反向断言、时间异常、版本/状态/平铺、金额、有限错误与 URL 六类问题均已在允许文件内修正，但这些是代码核对结论，不是运行通过证据。

Netcatty 已保存 host：120.53.251.166。本次环境核验 terminal 为 `7f1ad765-9317-4821-94d4-f9dda85bac18`，依赖安装和核验结束后已关闭释放；续接重新取得实际会话，不硬套旧 ID。此前只读核验 A1 的解释器为 CPython 3.12.8，A1 虚拟环境当时缺 pydantic，未修改该环境。

本任务独立依赖安装已成功：首次安装超出 terminal_execute 60s 上限，后改用 terminal_start；job `job_mvc4x28b_19c539fb4315` 最终 completed、exitCode=0，安装 10 个包。随后对本任务 venv 实际导入 pydantic、pytest 并断言解释器，命令 exitCode=0：

```text
implementation=CPython
version=3.12.8
executable=/opt/rag-story-1-1/contract-models-work/.venv/bin/python
base_prefix=/root/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu
pydantic=2.14.1
pytest=8.4.2
```

安装日志为服务器本任务目录下的 `/opt/rag-story-1-1/contract-models-work/dependency-install.log`，SHA-256 为 `4196fa13342cbaeb1ac336359696a9ad59f53e588e09f0f4dac0cd83a190a91a`。安装使用既定版本，没有改用其他版本或修改项目依赖锁；以上只证明隔离测试依赖可用，不是项目 `--locked` 重建或模型测试通过。

原调用 SFTP 时错误地未填参数，被自动审批拒绝。用户现已明确：不重试 SFTP、不绕过拒绝、不再索要同类传输批准；后续统一由主会话执行经过检查的 Git 提交/推送，服务器从同一仓库拉取。主会话最新告知已创建私有仓库 yb2915722928-cpu/rag_project 并设置 origin，CLI 设备登录遇到网络错误；本实现者未独立核验仓库状态，尚无可取固定提交，不声称已同步。

模型和测试三个文件保持冻结；本次仅更新本交付记录。等待主会话提供可取 Git 提交并重新唤起本任务后，先核对指定提交和下表 hash，再在本任务独占目录执行下列开发者测试，不抢占 A1 目录或环境：

```sh
cd /opt/rag-story-1-1/contract-models-work/backend
PYTHONPATH=src ../.venv/bin/python -m pytest tests/test_public_contracts.py -q
```

目标证据目录仍为 `/fileOfRag/testOfRAG/metadata/story-1-1`。当前 pytest 结果为 **not-executed**，独立验证/独立审查未执行；不能以本记录替代。

当前本地 SHA-256（待与远程运行副本核对）：

| 文件 | SHA-256 |
| --- | --- |
| public.py | bde6d8b50b7731b94204b285666ca9f337e836532a71c26a3c508c30bade5c69 |
| scalars.py | 872c527ade3bab00a6141e359b5d820601537dc871b59083fe2a6dad02bffb62 |
| test_public_contracts.py | 4fec1fc208558c08749168f4e6d5cd23c49a6df1175846c83e411228178a9a86 |

## 未到期门与续接

本 DTO 的 EvidenceBlock 是最小码点片段样例，不是完整 C3 来源定位/授权证明；HTTP 接入、H 限制入口、完整来源证据 DTO、comparison.v1 业务载荷、OpenAPI/JSON Schema/TypeScript 生成与验收由后续规格承接。公开枚举只覆盖 DTO 所需状态，不实现业务表、权限或供应方调用。全部父 Story AC、A/B/C/D/E、真实 PostgreSQL 和四服务运行门保持未完成。

下一步：等待主会话 Git 提交可取并唤起；从主会话指定仓库拉取指定提交到 contract-models-work 下的测试工作目录，核对冻结文件 hash 和精确 CPython 3.12.8 后执行开发者测试。当前不自行创建/推送仓库，不启动测试，不重试 SFTP，不采用替代传输。测试若失败，由主会话解除相应文件冻结并交回本实现者修复，随后重跑相关测试；保存提交 ID、命令、版本、退出码、文件 hash 和实际结果到桶内，再交回主会话继续独立验证/审查。
