# Story 1.2 A：持久执行与调用事实交付

状态：2026-10-18 代码冻结候选；Linux/真实 PG 证据待主控提交后在 Netcatty 运行。

## 实现范围

| 归属 | 文件 | 内容 |
| --- | --- | --- |
| execution 模型/端口 | [calls.py](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/calls.py:1) | `Epoch`、`ExecutionFence`、`ExecutionContext`、`CallGrant`、`EpochControl`、`CallStore`/`CallStoreFactory`、`LockOrder` |
| ledger 事实 | [facts.py](/E:/aaa-project/rag/backend/src/rag_app/modules/ledger/facts.py:1) | `UsageFact`、`CostFact`（estimated/actual）、`ResultFact`、`LateFact`、`LateFactOutcome`、`fact_digest` |
| 用例 | [call_lifecycle.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_lifecycle.py:1) | 原五方法 + `initialize_context`/`advance_attempt`/`terminate_context` |
| PG 仓储 | [call_postgres.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/call_postgres.py:1) | `execution_context`/`execution_call`/`ledger_call_fact`，仅为调用行加锁 |
| epoch 控制 | [epoch_control.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/epoch_control.py:1) | 独立控制文件只读、显式初始化、镜像比较、维护写 |
| 迁移 | [0002_isolated_calls.py](/E:/aaa-project/rag/backend/migrations/versions/0002_isolated_calls.py:1) | 三表 + epoch 镜像、约束、外键、可回滚 |
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

## 待执行验证

本地未运行任何测试。Linux CPython 3.12.8 与真实 PG 必跑：`test_real_call_lifecycle_and_single_grant`、`test_real_terminal_idempotency_and_late_facts`、`test_real_late_fact_does_not_take_parent_lock`、`test_real_failed_transaction_leaves_no_call`、`test_real_epoch_mirror_restart_and_contradiction`、`test_real_lease_expiry_under_held_context_lock_denies_old_now`，以及迁移 up/down/up、namespace/启动/UoW 回归。原始输出由主控归档到 `/fileOfRag/testOfRAG`。
