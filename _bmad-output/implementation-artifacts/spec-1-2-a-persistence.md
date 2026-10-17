---
title: '1.2 A 持久执行与调用事实'
type: feature
created: '2026-10-18'
status: in-progress
route: dispatch
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

实现原 Story 1.2 AC1/AC4 和 AC2 的持久状态。execution 独占上下文/call 状态，ledger 独占事实及冲突；application 管短事务。权威为 C4、R1/R2、实施契约 §2.5；全部父 AC 保留。

## Boundaries & Constraints

普通启动只读取独立 epoch 控制记录并比较 DB 镜像，缺失/损坏/矛盾隔离，禁止按 DB 自动补造。首次初始化是显式维护动作，不覆盖既有记录。控制记录含 deployment/随机 epoch/cutover/维护版本；不随 DB 回滚。

每次 prepared/授权派发/业务提交复核 epoch、attempt/token、lease/deadline、终态/隔离。call 保存归属、用途/阶段、配置指纹、request_hash、时间和供应方事实元数据；无正文/秘密/签名 URL。may_have_sent 条件转换仅一次；恢复不可再次派发。unknown 为 NULL+unknown。

迟到可信事实仅锁 call，不回取业务/gate/pool，不改产品次数/会话/业务/许可。重复无效果，冲突保留双方来源待核对，估价与实付区分。仓储不 commit；事务内不等 OS/进程/网络。锁序遵守 C4，可用当前最小实体证明真实 PG 反例，不提前建设未来身份业务。

## Tasks & Acceptance

- [ ] 在 `modules/execution/`、`modules/ledger/` 增加无框架模型/端口；`application/call_lifecycle.py` 实现用例；`adapters/call_postgres.py`、`adapters/epoch_control.py` 实现持久化。
- [ ] 新增 `migrations/versions/0002_isolated_calls.py`；必要时修改 `adapters/postgres.py`、bootstrap 和相关旧测试，使 revision/启动校验可集成，不回退旧迁移义务。
- [ ] 新增 `tests/test_call_persistence.py`、`test_call_postgres.py`、`test_epoch_control.py`，必要时维护 conftest 的必跑集合；交付 `docs/story-1-2-a-delivery.md`。

## Acceptance Criteria

- Given epoch/镜像，When 重启、缺失/矛盾及旧 fence 提交，Then epoch 不轮换、非法隔离、业务零写。
- Given call，When 重复 may_have_sent/恢复，Then 唯一 grant 资格不可重复，失败未知不变零。
- Given 已终结/旧 epoch call，When 重复/冲突可信事实，Then 幂等/冲突保留且其他账和状态不变。
- Given 真实 PG，When 故障回滚、反向取锁或迟到账遭父锁阻塞场景，Then 无半写、反序拒绝、迟到账不取父锁；等待发生在事务外。

</frozen-after-approval>

## Code Map

复用 `application/uow.py`、`adapters/postgres.py` 的 engine/namespace、既有独占 schema 夹具和 Alembic；不预建正式向量表。所有路径以本项目 backend 为根。

## Implementation Notes

唯一实现者 DeepSeek 默认；独占本规格列举的源/测试/交付文档。其他实现者拥有 egress/supervisor 文件，不得修改。第一阶段仅只读，向主控返回供 C 集成的精确模型/方法签名并等待 `IMPLEMENTATION_MODEL_RELEASE`；主控核实际模型及契约后才写入。不启动 C 的工作。代码先冻结、主控提交同步，随后分配 Netcatty 时段运行开发者测试。

## Spec Change Log

## Review Triage Log

## Verification

Linux 精确 Python 与真实 PG，迁移 up/down/up 和相关 namespace/启动回归；父 Story 的独立验证/审查另行执行。本规格完成不代表父 Story 完成。
