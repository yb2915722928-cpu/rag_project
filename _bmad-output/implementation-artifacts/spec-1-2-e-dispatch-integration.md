---
title: '1.2 E 调用集成与完整故障矩阵'
type: feature
created: '2026-10-18'
status: in-progress
route: dispatch
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

接管C已写但未冻结的调用集成草稿，把A的当前epoch/context/一次grant、B的已核EgressPlan与C的真实Linux监督串为一条可验证单call路径，完成原Story1.2未交付的端到端与故障矩阵。原四AC全部子句保留，不另开Story。

## Boundaries & Constraints

唯一实现者为现有A Euclid，DeepSeek默认；C已完成初次草稿写入并返回completed，主控现明确转移以下文件，不允许C继续修改。A已过的19源保持冻结，若契约真需改变先回报主控；不得改C四源或D文件。

每次调用prepared/临近may_have_sent两次短UoW、当前持久context与epoch、DB锁后时钟；A的CallGrant提交后才映射C的SendGrant（call/attempt/boot/child绑定），原call不能重发。C监督构造必须指定共用本地绝对state_root，未证明停止不复用槽。DNS/OS/IPC/等待在PG事务外。

模型/解析/embedding/图意与网络均显式假件，不实际供应方外发；URL/secret/主密钥/DB凭据不入child argv/env/普通日志。可信迟到事实仅call幂等/留冲突，不改业务/次数/会话/许可。无未来业务表不冒充已验证，也不要求未来业务实现。

## Tasks & Acceptance

- [ ] 接管 [call_dispatch.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:1) 当前草稿，按[公共契约](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-public-contracts.md:1)完成A/B/C集成，保持应用层无ORM/框架。
- [ ] 唯一写入 [unit矩阵](/E:/aaa-project/rag/backend/tests/test_call_dispatch.py:1) 与 [PG矩阵](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:1)：prepared前后、may后、响应前后代表性崩溃/超时，旧call无再次grant；未知NULL+unknown。
- [ ] 真实PG配真实Linux child证明旧epoch/终结/换attempt token拒绝业务、可信usage只补事实、重复/冲突不复活。至少覆盖实际controller/child失联或崩溃路径，不只Mock调用计数；故障点按原AC逐项映射，不穷举无关组合。
- [ ] 证明拒绝目标/下载凭据错配无派发；四类显式能力假件有可追溯路径；操作等待/停止不持PG事务。
- [ ] [E交付](/E:/aaa-project/rag/docs/story-1-2-dispatch-delivery.md:1)记录节点/输入预期实际/副作用、固定提交hash、命令退出码、原始证据与未过项。

## Acceptance Criteria

- Given 当前合法context与已核目标，When 单call受监督执行，Then 至多一次grant，结果/unknown持久且秘密不泄露。
- Given 各原故障点/过期旧fence，When 崩溃/超时/重启或可信迟到回填，Then 不恢复重发、不提交旧业务，成本仅call保留/幂等/冲突；无等待占事务。

</frozen-after-approval>

## Code Map

复用A的build_call_lifecycle与call_persistence，后者initialize_context返回ExecutionContext.fence()；原五方法及显式initialize_context/advance_attempt/terminate_context稳定。C四源已发布`96c64fb`，B域与HTTP假件已有153专题通过。不要再调查全部规划。

## Implementation Notes

首阶段只读接管草稿并5行内ready，等待E_MODEL_RELEASE后写。保持原草稿来源；没有同文件并发写者。所有运行/测试只在Netcatty Linux，从Gitee固定提交，主控发布前不跑；绝不临改server源码，失败先本地修补再发布。当前C将持terminal，E只本地实现；证据归 `/fileOfRag/testOfRAG/metadata/story-1-2/dispatch`。

## Verification

当前E专题、全部必需PG门与必要回归；不重跑全仓/前端或1.3限流/1.4清理。开发者、Step5独立验证和全新6.1medium审查各自留真证据，子段完成不代表父Story完成。
