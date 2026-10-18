---
title: 'Story 1.2 隔离执行与调用事实'
type: feature
created: '2026-10-18'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: '96e7fb3ee94c025c3fae804ddabf8ad71d8b08d5'
story_key: '1-2-隔离执行并保存每次调用事实'
review_snapshot_tree: '1eff8cf456f705b8c5e0b21985b87ad9d6a846d2'
review_gate: 'passed'
---

<frozen-after-approval>

## Intent

用显式假件证明每次调用经过持久 epoch、当前执行栅栏、受监督 child 和一次 grant；崩溃不重发，未知和迟到成本可追溯。验收分母为原 [Story 1.2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197) 四条 AC 全部子句。

## Boundaries & Constraints

保持八模块唯一写者、application 短 UoW、既有公开契约。child 无业务 DB/主密钥/自主后续阶段；secret 只经有界私有 IPC。本 Story 不实际调用供应方；未完成 1.3/1.4/1.5 不开放真实外发。运行只在 Netcatty Linux，精确 Python 3.12.8/PG18.6；源码先同步 GitHub/Gitee，再从 Gitee 拉固定提交并核 hash。主控只维护文档/集成协调。

## Tasks & Acceptance

- [x] A：持久 epoch/fence/call 和 ledger，依 [A 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-a-persistence.md:1)。开发者canonical151通过，父独立/审查另列。
- [x] B：共用 EgressTarget 与绑定连接，依 [B 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-b-egress.md:1)。开发者169通过，父独立/审查另列。
- [x] C：child/IPC/监督及调用用例集成，依 [C 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-c-supervision.md:1)，原集成义务由E完整交付。
- [x] 开发者测试、Step 5 独立实测、全新 6.1 Sol/medium 审查及真实问题的最小修复/相关回归；原必需门全部通过。

## Acceptance Criteria

- Given 独立 epoch 与 DB 镜像，When 重启/缺失/矛盾/旧 attempt 回报，Then 普通重启不换 epoch、矛盾隔离、失效执行者不能写业务；四类能力端口仅显式假件。
- Given 有界 child/IPC，When prepared 前后、may_have_sent 后及响应前后崩溃/超时，Then 原 call 最多一次 grant 且不恢复重发，未知为 NULL+unknown，child 权限与秘密满足原 AC2。
- Given 配置端点/签名 URL、redirect/DNS 假件，When 准备传输，Then HTTPS/精确 host-port/全部公网 A-AAAA/绑定 IP 与 TLS 主机校验、凭据分域、无自动 redirect 均符合 C5；失败阻断且不泄 URL/secret。
- Given 终结业务/旧 epoch 与可信迟到事实，When 重复/冲突回填，Then 只按 call 幂等补事实或留冲突，业务/次数/会话/许可不变；真实 PG 负例证明锁序与事务外等待。

</frozen-after-approval>

## Code Map

- [uow.py](/E:/aaa-project/rag/backend/src/rag_app/application/uow.py:18)：复用事务与有限错误边界。
- [postgres.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/postgres.py:17)：复用 namespace/版本/engine；新迁移须同步 revision 校验。
- [运行契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:5)：R1/R2；C4/C5 与实施契约 §2.5 为权威补充。

## Implementation Notes

无需求空缺。迁移仅新建本 Story 最小表并可回滚；测试使用独占 schema，不改既有四服务数据。A/B 无文件依赖可并行；C 的 child/IPC 可独立开始，依赖 A 的调用集成等公共端口登记后开始；全部后端为 DeepSeek 默认。无前端表面。

2026-10-18 已按既有用户预授权批准并进入开发。tiktoken o200k 编码完整规格计数：母规格1089、A931、B827、C878，均低于1600风险线；不需长度门确认。分段仅控制上下文，四项原AC不延期。

实际调用路径确认新增必要回归D：[epoch启动接线](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-d-epoch-deploy.md:1)。已有Compose未提供新的epoch文件配置，新worker必隔离；只补最小配置/首次显式维护说明并验证受影响启动/重启，1.5完整S0资格工具不前移。

C完成native四源后，主控将未冻结的call_dispatch及unit/PG矩阵明确移交现有A按[E集成规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-e-dispatch-integration.md:1)并行接管；没有重复写者，C原端到端义务完整转入E，父四AC分母不变。

## Spec Change Log

## Review Triage Log

唯一全新6.1Sol/medium已完成tree1eff8cf审查，新增0；[完整报告](/E:/aaa-project/rag/docs/story-1-2-code-review.md:1)。

| 项 | 裁决/路由 |
| --- | --- |
| 已知F2 | 已关闭；d6用途分层经开发者、Step5独立及medium增量审查通过 |
| 已知E矩阵 | 已关闭；d6真实child/PG/迟到与URI假件修复均有运行证据 |
| D运行 | 016镜像权限修复、启动重启/三负例、独立复核及审查通过；历史失败保留 |

## Verification

原四条 AC 逐项映射 Linux/PG 证据，原始输入/输出存桶。只运行当前必要测试与受影响回归；1.3 限流、1.4 清理、1.5 汇总及后续业务不记为本条通过。
