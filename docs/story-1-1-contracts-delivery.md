# Story 1.1 B 公共契约导出交付记录

日期：2026-10-17（Asia/Shanghai）。状态：**源码准备完成、文件冻结；正式生成与运行验证未执行**。

本记录不把静态代码、Windows 观测或文件 hash 当成本增量通过。完整 B0a/B0c 开发者测试、固定 Gitee commit 拉取、Linux 精确 CPython 3.12.8 执行、正式 OpenAPI/JSON Schema/TypeScript 生成、独立验证与独立审查仍未完成；B 与父 Story 1.1 均不得据此标记完成。

## 规格与认领

实现前已完整读取：

- [AGENTS.md](/E:/aaa-project/rag/AGENTS.md:1)
- [B 段公共契约交付规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-contracts-dispatch.md:1)
- [公共模型规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-contract-models.md:1)
- [枚举真源增量规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-contract-enum-source.md:1)
- [共享契约 C1/C2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:1)
- [实施契约 §3.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:188)
- [HTTP 交付记录](/E:/aaa-project/rag/docs/story-1-1-contract-http-delivery.md:1) 与现有 `backend/src/rag_app/**`

写入范围：

- 新建 `contracts/**`（本交付新增的仓库根目录）。
- 本记录 `docs/story-1-1-contracts-delivery.md`。
- 枚举增量正式扩展：`backend/src/rag_app/contracts/public.py`、`backend/tests/test_public_contracts.py` 仅新增 `PUBLIC_ENUMS` 及其测试。

未修改 `backend/` 其他源码、`frontend/**`、`deploy/**`、依赖锁、迁移、测试夹具、主控台账或 Sprint 文件。未执行 Git、SFTP、Docker 或外部网络探测。

## 实际修改

### 后端枚举真源（增量）

[public.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/public.py:411) 新增 `PUBLIC_ENUMS`，直接引用已存在的 `Status`、`Outcome`、`OperationState`、`JobState`、`RetryMode` 类对象，按类名索引：

```python
PUBLIC_ENUMS: dict[str, type[StrEnum]] = {
    enum.__name__: enum for enum in (
        Status, Outcome, OperationState, JobState, RetryMode,
    )
}
```

`JobState` 不再因没有 DTO 字段引用而无法导出。`PUBLIC_MODELS`、17 个 DTO、字段、校验规则、`create_app()`、维护探针与 HTTP 行为保持不变。

[test_public_contracts.py](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:531) 新增三项测试：

- 索引键与类名一致、值与后端原类同一身份、五组 wire 值未变、与 `PUBLIC_MODELS` 不混用、DTO 仍为 17 种。
- 每个枚举经 `TypeAdapter` 在 validation/serialization 两侧导出 `type=string`、`enum` 顺序与后端一致；合法值 round-trip，非法值拒绝。
- `status`/`outcome`/`operation_state`/`job_state` 四种语义互不混同，跨枚举值被拒绝。

复核修正：该测试使用显式 `字段 -> 后端枚举名`（`status -> Status`、`outcome -> Outcome`、`operation_state -> OperationState`、`job_state -> JobState`）映射，不把 wire 字段名直接当 `PUBLIC_ENUMS` 键；`RetryMode` 单独验证。

### 生成器与校验入口

- [generate.py](/E:/aaa-project/rag/contracts/generate.py:1)：只导入 `PUBLIC_MODELS`/`PUBLIC_ENUMS` 与 `create_app().openapi()`；为每个 DTO 生成 validation/serialization JSON Schema，为每个枚举经 `TypeAdapter` 生成 enum schema；由 schema 生成 `contracts.ts` 与 `contracts.input.ts`；生成 `schemas/capabilities.json`、稳定排序的 `openapi.json` 与带源文件/工件 SHA-256 的 `manifest.json`。`--check` 校验内容、缺失文件与意外残留。
- [verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:1)：执行 C1/C2/H 正负样例，使用后端原模型、`scalars.py`、`json_guard.py` 与隔离 HTTP 探针。1 MiB 请求体和 17KB 请求头由有限 `raw_generate`/`headers_generate` 参数合成，不在仓库保存超长字面量。

复核修正：`_run_enum_set` 先遍历全部五个字段，再统一结算；`reject` 用例必须声明 `invalid_fields`，并要求被拒字段集合与声明完全一致（当前为仅 `job_state`），其余字段仍合法，负例不会被第一个合法字段提前中断。
- [README.md](/E:/aaa-project/rag/contracts/README.md:1)：唯一真源、命令、退出码、生成物布局、两侧 schema 差异、安全边界与延期项。

### C1/C2/H 样例

[manifest.json](/E:/aaa-project/rag/contracts/samples/manifest.json:1) 共 52 个用例（含 F3/F4 修正新增的对照与用例）：

- C1：中文/组合字符/非 BMP、标量码点长度与半开切片、显式 null 与缺省、稳定键序列化、重复键/NaN/Infinity/孤立 surrogate/未知字段/绝对状态 URL 拒绝。
- C2：`AcceptedResponse` 202、扁平完成答案、授权后可带 operation ID 的失败、前置认证失败无 operation ID、私有 ID 泄露拒绝、GET operation 失败投影 200、retrieval 至多五块、六块拒绝、`outcome`/`status` 不一致拒绝、伪造 `retry_mode` 拒绝。
- C2 枚举：四种状态字段分离的合法组合，以及 `job_state` 取 `answered` 的跨枚举拒绝。
- H：单根 object、重复键、NaN、孤立 surrogate、非法 UTF-8、尾随数据、数字溢出、深度 8 恰等/9 拒绝、节点/数组上限、1 MiB 恰等/超一字节、未知字段、真实 ASGI HTTP 的 200/401/415/431/413/422 与 `no-store`、operation ID 缺失。
- 原件 PUT 分界只记录说明，不伪造执行；当前没有原件 PUT 路由。

`comparison.v1` 按规格延期，只在 `not_generated` 记录，不进入样例失败分母；`job_state` 不再是 blocked。

### F3：负例改为合法对象的单点变异

独立预审指出的“额外错误掩盖目标规则”已修复：

- 重复键、NaN、Infinity、孤立 surrogate、顶层未知字段样例都从 [c2/completed.json](/E:/aaa-project/rag/contracts/samples/c2/completed.json:1) 派生，且只改一处：分别重复 `outcome` 键、把 `completed_at` 写成 `NaN`/`Infinity`、把 `execution_snapshot_id` 写成孤立 surrogate、追加未知顶层字段。它们不再缺少必需字段，也不再带有 `summary.fact_ids` 指向不存在事实的额外错误。
- 新增 [nested-unknown-field.json](/E:/aaa-project/rag/contracts/samples/c1/nested-unknown-field.json:1)，在 `facts[0]` 内放未知字段，覆盖嵌套 `extra_forbidden`；顶层未知字段样例仍保留。
- H 的直接解析负例（根数组、重复键、NaN、孤立 surrogate、尾随数据、非法 UTF-8、数字溢出、深度、节点、数组、1 MiB）各自声明 `control`，引用去掉违规后必须被接受的合法输入，如 `h/valid-a1.json`、`h/valid-a2.json`、`h/valid-a-x.json`、`h/depth-exact.json`、`h/nodes-exact.json`。
- 全部 34 条 `reject` 用例都声明 `control` 和拒绝原因（`error`、`error_contains`、`invalid_fields` 或 `expected_error`）。校验器先运行对照并要求通过，再要求目标拒绝命中声明的原因。Pydantic 诊断串本身包含 `input_value`，因此模型层不再对违规子串做无意义的“泄漏”断言；泄漏检查只保留在 HTTP 响应层。

### F4：HTTP 样例校验完整公共包

[verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:279) 现在对每条 HTTP 用例要求：

- `Content-Type` 为 `application/json`，正文可解析为 JSON object，且含 `schema_version`/`request_id`/`status`；非 JSON 200 不再能通过。
- 由用例声明的 `response_model`（必须是 `PUBLIC_MODELS` 成员）验证正文；成功用例不能得到 `FailedResponse`。
- `X-Request-ID` 必须存在、为 32 位小写十六进制，并与正文 `request_id` 一致；`attempts=2` 的三条用例（`h.http.valid-retrieval`、`h.http.reject.unauthenticated`、`h.http.reject.unknown-field`）要求两次尝试不复用诊断 ID。
- 必须带 `Cache-Control: no-store`，不得出现 `ETag`/`Last-Modified`，304 直接失败。
- 声明 `expected_error` 的用例与 `PublicError.from_code(...)` 的完整有限策略逐字段比较（code/message/http_status/retry_mode/details），并要求 `error.http_status` 等于实际 HTTP 状态。

## 当前文件 SHA-256

以下为冻结时的本地文件内容 hash（小写十六进制），不是 Git 提交、Linux 运行或正式生成证据。

| 文件 | SHA-256 |
| --- | --- |
| `backend/src/rag_app/contracts/public.py` | `2a90008315939dae54a191ae929f67f76edca8eadcdb34e3fab6461e33ed58cb` |
| `backend/tests/test_public_contracts.py` | `9d6180d6e4eaeb4c565f74fccd4ec8868c9411006c29a506123f398f2f138177` |
| `contracts/generate.py` | `dd1fafc9008418ad09c5175d64029f1ff640e4092ab9d0894ab2219bad4e25e7` |
| `contracts/verify_samples.py` | `e41e6407efb4ceb486e6533017328d4f24f4cdb9a8cb882d878532c432280e19` |
| `contracts/README.md` | `d38f8164d68df330b5d76441671483712d30a47e2af096cf66060578586f6562` |
| `contracts/samples/manifest.json` | `df659d241696d5262cd344c606bfe997b0286c1ab2b0d2af073340135712a834` |

样例文件 hash 见附录；`docs/story-1-1-contracts-delivery.md` 自身的 hash 在写入后由主会话/后续会话按需重算，不在文件内自引用。

## 后续 Linux 命令（未执行）

必须先取得 GitHub/Gitee 指向同一固定 commit，服务器拉取该 commit 并核对源码 hash，且 B0a/B0c 开发者测试通过。

```bash
cd <fixed-commit-worktree>/backend
uv sync --locked --python 3.12.8
uv run --locked python -c 'import sys,platform; assert sys.version_info[:3]==(3,12,8); assert platform.python_implementation()=="CPython"'
uv run --locked python -m pytest tests/test_public_contracts.py tests/test_contract_http.py -q
cd ..
uv run --project backend --locked python contracts/generate.py
uv run --project backend --locked python contracts/generate.py --check
uv run --project backend --locked python contracts/verify_samples.py
```

正式生成产物、pytest 计数、JUnit、耗时和退出码均须保存到 `/fileOfRag/testOfRAG/metadata/story-1-1/contracts/` 下按固定提交区分的位置。

## 未执行项与风险

- `not-executed`：`contracts/generate.py` 正式生成、`--check`、`verify_samples.py`、`test_public_contracts.py` 及 HTTP 回归的全部运行。
- `not-executed`：固定 Gitee commit、Linux 精确 CPython 3.12.8、`uv sync --locked`、真实 ASGI HTTP 与浏览器。
- `not-executed`：独立 Step 5 验证、全新 `GPT-6.1 Sol / medium` 独立审查与修复回归。
- `blocked`：同一 Gitee commit 尚未可取；正式工件空位（`openapi.json`、`schemas/**`、`typescript/**`、`manifest.json`）等待生成，仓库当前只含生成器与样例。
- 风险：JSON Schema 不能表达 Pydantic `model_validator` 跨字段规则，运行时权威仍是后端模型；样例覆盖这些边界但不等于 schema 自身可表达。
- 风险：`validation` 与 `serialization` 模式确实不同；消费方必须按方向使用对应文件，不能把任一文件当双向完整契约。
- 风险：OpenAPI 暴露隔离维护探针路径；生产网关必须阻断，当前未验证部署侧阻断。

## 附录：样例文件 hash

| 文件 | SHA-256 |
| --- | --- |
| `contracts/samples/c1/duplicate-key.json` | `57fe30f5df0c97c5afbb5e2187c5a3398fced9b8f3d904d7f586f9bd3d7046c7` |
| `contracts/samples/c1/failed-absent.json` | `aead50591c6842cee1fa86ff0633d4130013a69166454aa3a9930b5419e5e794` |
| `contracts/samples/c1/failed-explicit-null.json` | `b156af33822cd5c45f92df854941bde304238c405db49e486dc31131f73ccc2e` |
| `contracts/samples/c1/infinity.json` | `f100e1ec7acdad60e2c9450fd804268afa1f5d12d8207b3cfd887302654b2fc0` |
| `contracts/samples/c1/lone-surrogate.json` | `7836d01999c5402c7861fd9b1fff2cc246cb816cfaa626e984cf080c13c08f52` |
| `contracts/samples/c1/nan.json` | `ff117a92f7c8b4b87142d2483a9fb297de0c5aeb4666f7deaf165e3cf6a4a0b8` |
| `contracts/samples/c1/nested-unknown-field.json` | `9f73ce33f58764e9eadcb4859eabd39d71675b7202af4eb28179432cce2b2445` |
| `contracts/samples/c1/scalar-span.json` | `b2b5f5f78038bb8392d318c5c151c1dd5d870a1a1c294a569ed6e3777a556155` |
| `contracts/samples/c1/stable-keys.json` | `9ce54c56fdf11db2d18b0c8d9778f3163b3c40ba87f4f2e2845a9ad6dd044b65` |
| `contracts/samples/c1/status-url-absolute.json` | `50d9b50bbffdf1ef6cbdced45a26ecb6740d540691b24b9ce8317e4e69d2e933` |
| `contracts/samples/c1/status-url-trailing-slash.json` | `2732cf59ba82ee9faa9d7f399e4c29c21b004cbfcc60a94c98c710aff6ae98f4` |
| `contracts/samples/c1/unicode-values.json` | `0c8a51524a2e008a20cd4ad12a1b2a4888874046f7e471785ecddb049d65d94d` |
| `contracts/samples/c1/unknown-field.json` | `9649e97a2ef4dc3e2c21b1c3ab6c315c760cb1a9acb3daea89834cd5afd7edb1` |
| `contracts/samples/c2/accepted.json` | `648d00e574fdbfcc0b4ac6359f398f8e92621226fcd0b7b9cb2da612b1eb6a4d` |
| `contracts/samples/c2/completed.json` | `27499494c5599b8d1b68e834886c20dbf27620876c45cfe632496b90daf20cdc` |
| `contracts/samples/c2/failed-authorized.json` | `0fe6e3872497cbe30ecd3bb34efccf16c59871160d6265d8c26b93604505f790` |
| `contracts/samples/c2/failed-pre-auth-with-id.json` | `72b50261df97644f5d9c24df1dec9129dfe42a24deaf47b87b769004a2c47537` |
| `contracts/samples/c2/failed-pre-auth.json` | `7bcab8e4932a7185491d30c6192e80a36e774924e5058c3e9d483ea62836e2f8` |
| `contracts/samples/c2/forged-retry.json` | `33ac8e09102e17ce4be03f700669a9d25fe72168db2c5d89d0e9d4036d85fdaa` |
| `contracts/samples/c2/job-state-invalid.json` | `31baa2b3a21a2fdd2fd2a24896df9cb0fa8240974b8cd72a8bc6731049c10e6e` |
| `contracts/samples/c2/operation-failed.json` | `569a2a462b1b6d810481098ab6cbcfac16c5e4f8ed6e9903233dcdf8504fc24d` |
| `contracts/samples/c2/outcome-mismatch.json` | `3af65f0c5b95f8675861a4308cac68c372e48519ea88d1f2318a48f871d33d18` |
| `contracts/samples/c2/public-error.json` | `9505c7436c8d926c704139647aeb6e2672ef81c50ed46b2ea109d427fe0e5e21` |
| `contracts/samples/c2/retrieval-failed-with-operation.json` | `72dad5b07a5e4968e2609535cc1f2c757372e0c0d0619aa3d083feb18ec61069` |
| `contracts/samples/c2/retrieval-six.json` | `08a10b6afc678ca2577ad6f8b76ff0fd0dc649131c8ea6f205399685f6930548` |
| `contracts/samples/c2/retrieval.json` | `e3e3670d71d8fa34c2bd3355ac3206383db4b8d6164897d805a82bedbc0b2e46` |
| `contracts/samples/c2/state-enums.json` | `6e29f98c9cb95f81fcc8894318b00ab0e2527337d0fa4d3b91636c1e655638d7` |
| `contracts/samples/h/array-three.json` | `8d349c562af62e82a07042946a210517bb141ddf85ee8093b43648bc266ceac7` |
| `contracts/samples/h/depth-exact.json` | `3ed61ed47d165a6f1f0bc91e6451863189f2e7cc052a63581daa97fb090f7b2d` |
| `contracts/samples/h/depth-over.json` | `588596f273352ab50b98822a7c4fa8281acc3e01e1766783b7a85038eba15a09` |
| `contracts/samples/h/duplicate-key.json` | `080d1d9d77d8a027954c972677c4ce62c352b878aa44fa10777601fbb0def0ac` |
| `contracts/samples/h/lone-surrogate.json` | `f6204181aef21b186fe1b240b341d53132203c579eb5a49ab8bf75239fc1b4b4` |
| `contracts/samples/h/nan.json` | `b9f2ee2f9d44d5e5857acddf5b66e92b64b75f2a6bc97c0ecc5aff597ef5b46d` |
| `contracts/samples/h/nodes-exact.json` | `459e40da32ea60f7dbd66f40ed00fc97b53b237ed6306d14b8388c9b4e753bd2` |
| `contracts/samples/h/nodes-over.json` | `415f7571ed5dc4a3ab538c18e246e593feb64e201526528ce9e3f2db8893f3b8` |
| `contracts/samples/h/number-overflow.json` | `41045e529ce6d23f8e90264588376aeb94ab152f5ed0122ea6617743b8fb0aea` |
| `contracts/samples/h/root-array.json` | `5239a7754876b9a70871c45e41f1bd9abbd91ed2de67af926c1cfcc9c9377d51` |
| `contracts/samples/h/unknown-field.json` | `9649e97a2ef4dc3e2c21b1c3ab6c315c760cb1a9acb3daea89834cd5afd7edb1` |
| `contracts/samples/h/valid-a-x.json` | `b98916c2cdff9fb1f04d6d83ab835aff91191f9349f569c79d57c2774954bd53` |
| `contracts/samples/h/valid-a1.json` | `ff57d51972c56df657d32f3901f226728943f67e0716df1de53a11ce240bd2ba` |
| `contracts/samples/h/valid-a2.json` | `d4f143869e9dedf3610951217569bc1a31d62ea1b317c73e7ddb59e2b060d162` |
| `contracts/samples/h/valid-min.json` | `c5c24f7ca1c946fa4dfd44407409c8e11ec6e41f0e1c7c45bf8381b42afb31f1` |

## 冻结后重算

上表与附录为复核修正后的冻结值。`docs/story-1-1-contracts-delivery.md` 自身不嵌入自身 hash，由主会话以 `sha256sum`/`Get-FileHash` 重算后冻结。非法字节样例只内联在 manifest 的 `raw_base64` 中，不额外保留文件。

提交收尾说明：上文局部hash属于对应静态交付/复核时点。其后仅清理少量源码/配置/文档的单个EOF空白行，字节前缀一致性已记录；原始wire输入保持原字节。最终源码与Git规范化内容hash以 [准备来源快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-preparation-source-hashes.json:1) 为准，EOF前后证明见 [收尾证据](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-eof-normalization.json:1)。这些均不构成任何运行通过。
