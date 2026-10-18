# RAG 主链 U2b：embedding 与向量完整性核心交付记录

状态：首轮固定提交 Linux 开发者测试 4 项失败已定位为测试期望错误并修复在本地工作区；等待主控以新 commit 双远端发布后重跑。本文件不代表 U2b 验收通过。

## 范围

| 归属 | 文件 | 内容 |
| --- | --- | --- |
| 领域核心 | [embedding.py](/E:/aaa-project/rag/backend/src/rag_app/modules/indexing/embedding.py:1) | 不可变 profile 与指纹、有限批计划、`TokenCounter`/`EmbeddingProvider` 协议、共享向量空间与 provider 绑定校验、统一结果校验与稳定 L2 归一化 |
| 开发者测试 | [test_embedding_core.py](/E:/aaa-project/rag/backend/tests/test_embedding_core.py:1) | 上表全部规则的矩阵用例（合成计数器与合成向量） |

仅标准库；无网络、无重试、无隐式截断；错误只带有限码，不含正文、端点或凭据。未新增依赖、迁移、公共 DTO、配置或 HTTP 客户端。未借鉴外部仓库实现，无来源引用需要登记。

## 入口签名

```python
EmbeddingLimits(
    *, max_tokens_per_item: int, max_tokens_per_batch: int,
    max_utf8_bytes_per_item: int, max_utf8_bytes_per_batch: int,
    max_items_per_batch: int,
)

EmbeddingProfile(
    *, profile_id: str, provider: str, model: str, deployment: str,
    dimension: int, tokenizer: str, preprocessing: str,
    normalization: Literal["l2", "none"],
    purpose: Literal["query", "document"], input_prefix: str,
    limits: EmbeddingLimits, verified: bool, evidence_ref: str | None,
)

plan_embedding_batches(
    *, profile: EmbeddingProfile, purpose: Literal["query", "document"],
    texts: Sequence[str], counter: TokenCounter,
) -> EmbeddingBatchPlan

validate_shared_vector_space(
    *, query_profile: EmbeddingProfile, document_profile: EmbeddingProfile
) -> str

validate_provider_binding(
    *, provider: EmbeddingProvider, plan: EmbeddingBatchPlan
) -> None

validate_embedding_results(
    *, profile: EmbeddingProfile, plan: EmbeddingBatchPlan,
    results: Sequence[EmbeddingResult],
) -> tuple[tuple[float, ...], ...]
```

`EmbeddingBatchPlan` 暴露 `items`（权威有序输入，`ordinal` 为全局序号）、`batches`（保序划分）、`ordinals`、`item_count` 及四个指纹；`EmbeddingPlanItem` 同时保留原始 `text` 与含 `input_prefix` 的 `provider_text`。`EmbeddingProvider` 仅约定 `profile` 属性与 `embed_batch(batch)`，由后续受监督 adapter 在现有 call/egress 与共享 gate 后实现。

## 规则落实

- 指纹分层：`space_fingerprint`（provider/model/deployment/dimension/tokenizer/preprocessing/normalization，供 query/document 共用空间校验）、`compatibility_fingerprint`（再加 purpose 与精确 `input_prefix`）、`fingerprint`（再加 `profile_id`、全部限额、`verified`、`evidence_ref`）。四类指纹任一输入变化即变化，不把不兼容配置混同。
- 计划：显式 purpose 必须等于 profile 用途；未证 profile 直接拒绝；每项先核 UTF-8 字节再计 token；每条/每批同时受 token、字节、条数限制，超单条即有限失败；不 trim、不截断、不丢条、不调 provider、不重试；计数器 tokenizer 标识必须与 profile 完全一致，`bool`/非整数计数被拒。
- 结果：按全局序号重排合法乱序；拒重复/缺失/越界序号、数量不符、非 `EmbeddingResult`、bool/非数值/NaN/Infinity、维度不符、零向量；`l2` 先按最大幅值缩放再求和开方，极大/极小有限量级下仍有限且范数为 1；`none` 原值保留。
- 错误：`EmbeddingError.code` 为有限枚举，消息不含输入文本、URL 或密钥。

## 验证状态

| 项 | 当前状态 |
| --- | --- |
| 规格矩阵用例（开发者测试源码） | 已修复 4 项错误期望，待新固定提交执行 |
| Linux CPython 3.12.8 `test_embedding_core.py` | 首轮失败（4 failed / 49 passed），修复后未重跑 |
| 架构边界（`test_architecture.py`） | 首轮 3 项全部通过 |

### 首轮固定提交 `dc1d0676d341292f4a0eae38e0c520d9945de90a`

环境：`/opt/rag-fastapi-main/repo`（Gitee 检出、detach 该提交、工作区 clean），`PYTHONPATH=/opt/rag-fastapi-main/repo/backend/src`，`/opt/rag-story-1-2/venv-fixed/bin/python`（CPython 3.12.8）。测试前后源码 SHA256 与主控给定值一致：`embedding.py c16916b…d489`、`test_embedding_core.py be05a1a…337f`。命令与原始日志/JUnit 归档于 `/fileOfRag/testOfRAG/metadata/rag-api-mainline/U2b/first-run-dc1d067/`。

实际结果：`4 failed, 49 passed`，失败全部位于 `test_embedding_core.py`，实现 `embedding.py` 无需改动。

| 失败用例 | 根因（测试期望错误） | 修复 |
| --- | --- | --- |
| `test_profile_fingerprints_change_for_every_compatibility_input` | 断言 `purpose`/`input_prefix`/限额/`profile_id`/`evidence_ref`/`verified` 变化也会改 `space_fingerprint`；按规格这些只属于 compatibility/profile 指纹，向量空间指纹必须保持不变（query/document 共用空间依赖此性质） | 拆为三组：空间级输入改 space+compatibility+profile；用途/前缀只改 compatibility+profile；profile 级只改 profile |
| `test_plan_respects_item_and_batch_token_byte_and_count_boundaries` | 期望 `[(0,1,2),(3,4)]` 与每批 10 token 上限矛盾（前三条 1+2+3=6，已无法再加 4）；`max_items_per_batch=2` 也限制单批 2 条 | 改为 `[(0,1),(2,3),(4,)]`，批计数 `3,7,5` |
| `test_plan_byte_limit_can_split_before_token_limit` | 期望每批仅 2 条，但 `max_items_per_batch=10`、每批字节上限 8，正确包装应 4 条凑满 8 字节 | 改为 `[(0,1,2,3),(4,)]`，字节 `8,2` |
| `test_l2_normalization_is_stable_for_extreme_finite_magnitudes` | 输入 `(5e-324, 1e-323, -5e-324)` 首元素为正，却断言 `tiny[0] < 0 < tiny[1]` | 按符号断言 `tiny[0] > 0`、`tiny[1] > 0`、`tiny[2] < 0` |

失败日志与原始 JUnit 保留，未覆盖。修复只改测试断言，不改实现、限额语义或错误码。

执行条件：主控以新 commit 完成 GitHub/Gitee 同提交发布后，从 Gitee 拉取该提交重跑同一命令；二次运行证据归档到 `/fileOfRag/testOfRAG/metadata/rag-api-mainline/U2b/` 下的新目录。合成计数器/向量只证明领域规则。

## 未完成与待验

- 真实 embedding 供应方 profile（模型/部署/revision、维度、tokenizer、限额）与其证据引用未核实；U2b 不发布任何已证 profile，`verified=False` 的 profile 不能生成可派发计划。
- 受监督 provider adapter、实际调用记账/permit、真实网络行为属于后续共享 gate 与 egress 范围，本单元未实现、未验证。
- Linux 开发者测试与架构边界、独立 Step5 验证、全新 GPT-6.1 Sol medium 审查均未发生。
