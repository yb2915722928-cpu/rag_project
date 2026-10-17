# Story 1.2 A：持久执行与调用事实交付

状态：2026-10-18 A 开发者门已在固定提交 `af6ce5099166960e714a1e8b45f004cc8ac9f77a` 的干净 Linux 检出通过；A 源/测试继续冻结，父 Story 独立验证与正式审查由主控另行执行。

## 实现范围

| 归属 | 文件 | 内容 |
| --- | --- | --- |
| execution 模型/端口 | [calls.py](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/calls.py:1) | `Epoch`、`ExecutionFence`、`ExecutionContext`、`CallGrant`、`EpochControl`、`CallStore`/`CallStoreFactory`、`LockOrder` |
| ledger 事实 | [facts.py](/E:/aaa-project/rag/backend/src/rag_app/modules/ledger/facts.py:1) | `UsageFact`、`CostFact`（estimated/actual）、`ResultFact`、`LateFact`、`LateFactOutcome`、`fact_digest` |
| 用例 | [call_lifecycle.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_lifecycle.py:1) | 原五方法 + `initialize_context`/`advance_attempt`/`terminate_context` |
| PG 仓储 | [call_postgres.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/call_postgres.py:1) | `execution_context`/`execution_call`/`ledger_call_fact`，仅为调用行加锁 |
| epoch 控制 | [epoch_control.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/epoch_control.py:1) | 独立控制文件只读、显式初始化、镜像比较、维护写 |
| 迁移 | [0002_isolated_calls.py](/E:/aaa-project/rag/backend/migrations/versions/0002_isolated_calls.py:1) | `rag_epoch_mirror`/`execution_context`/`execution_call`/`ledger_call_fact`、约束、外键、可回滚 |
| 共享 | [errors.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/errors.py:1)、[postgres.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/postgres.py:15)、[runtime.py](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:1) | `GuardError` 有限码、HEAD revision、启动 epoch 核对 |

## C 集成入口

```python
from rag_app.bootstrap.runtime import build_call_lifecycle
from rag_app.adapters.epoch_control import FileEpochControl

control = FileEpochControl(path, schema=schema)          # 只读；缺失/损坏即 GuardError
lifecycle = build_call_lifecycle(control, schema)

context = lifecycle.initialize_context(
    uow, context_id=..., holder_id=..., space_id=..., purpose=...,
    config_fingerprint=..., attempt=1, claim_token=...,
    lease_until=..., hard_deadline=..., now=...,
)                                                        # 受控假件/受理入口
fence = context.fence()
call_id = lifecycle.prepare(uow, fence=fence, ...)
grant = lifecycle.mark_may_have_sent(uow, call_id=..., fence=fence, ...)
```

真实 PG 夹具：`call_persistence`（[conftest.py](/E:/aaa-project/rag/backend/tests/conftest.py:176)）提供已迁移 schema、独立 epoch 控制、镜像、`lifecycle`/`uow`/`engine` 和 `initialize_context(**values)`。

## 权威与隔离

- `prepare`/`mark_may_have_sent`/`record_result` 都先锁 `execution_context` 行，核 state/epoch/attempt/token 摘要/lease/deadline/归属/config，再锁 call；加锁后用仓储 `current_time()`（PG `clock_timestamp()`）复核期限，调用者 `now`/`result.at` 只是事件元数据，不能延长资格或回拨。
- `record_unknown` 与 `record_late_fact` 仅锁 call：前者是恢复终态观测，后者是迟到事实；二者都不重新取得发送资格、不改业务、gate、pool、会话。
- 迟到事实重复按 `(call_id, fact_digest)` 幂等；与已持久 provider ref/usage/cost 矛盾时保留双方并置 `reconciliation_status=required`。
- epoch 控制文件读取发生在短 PG 事务之前；镜像缺失/矛盾返回有限 GuardError，不自动补造或轮换 epoch。

## 验证记录

### 固定提交 `af6ce5099166960e714a1e8b45f004cc8ac9f77a`（canonical）

干净检出 `/opt/rag-story-1-2/repo-fixed`（origin 仅 Gitee，detach 该提交）、`/opt/rag-story-1-2/venv-fixed`（CPython 3.12.8，`uv sync --locked` 退出 0）。测试前后：HEAD 均为 `af6ce5099166960e714a1e8b45f004cc8ac9f77a`，`git status --porcelain` 为空，19 个 source SHA 对 `story-1-2-a-fix1-source-snapshot.json` 0 mismatch；测试过程未修改服务器源码。

| 组 | 结果 | 退出码 |
| --- | --- | --- |
| persistence/epoch/UoW/resource_cleanup/architecture/namespace/config/baseline/migrations/api/uvicorn（non-PG） | 88 passed | 0 |
| worker/runtime（non-PG） | 48 passed，2 deselected | 0 |
| `--require-postgres -m postgres`（旧 6 + worker 2 + A 新 7，含锁后 DB 时钟） | 15 passed，0 skipped | 0 |

证据目录 `/opt/rag-story-1-2/evidence/A-canonical-af6ce50/`，归档 `/fileOfRag/testOfRAG/metadata/story-1-2/A-canonical-af6ce50/`：rawlog、`unit.xml`/`runtime-nonpg.xml`/`pg.xml` JUnit、实际命令与退出码、前后 HEAD/status/python、`uv sync --locked` 日志及 `evidence-sha256.txt`。主控已核三份 JUnit 均 0 fail/error/skip。

### 先前 `52ccb1ff69b1d7f07d9f482b2035ca71e2db12ad`（失败，保留）

该固定提交的真实 PG 运行失败：`test_call_postgres.py` 7 failed，根因是 SQL 参数误传给 `text()` 而非 `execute()`。原始失败及服务器 overlay 草稿的7份文本日志保留在 `/fileOfRag/testOfRAG/metadata/story-1-2/A/` 和相应 evidence 目录；该目录没有JUnit，不补造。主控已逐一读取实际目录/hash并保存在[首次证据记录](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-a-first-attempt-evidence.json:1)。**这些 overlay 通过只作缺陷定位草稿，不是 `52ccb1f` 固定提交通过证据。** af6 canonical 的三份JUnit另见上一节。

### 遗留

父 Story 的独立验证、正式审查及问题修复尚未完成，本文件完成不代表父 Story 完成。A 源/测试保持冻结，供后续正式审查问题的最小修复使用。
