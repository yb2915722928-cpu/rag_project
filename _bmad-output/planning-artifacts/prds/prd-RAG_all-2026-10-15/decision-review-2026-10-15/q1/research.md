---
topic: Q1 FastAPI组织、数据库与访问控制
type: technical
decision: TR-explore-then-TS-select
source: official-source-native-run
status: complete
date: 2026-10-15
updated: 2026-10-15
claims_verified: 0
claims_unverified: 9
---

# Q1 决策研究

决定：模块化单体；同步SQLAlchemy2/psycopg3＋Alembic；显式RAG步骤；PG服务端Cookie会话＋Argon2id；用户绑定且仅存hash的随机只读API凭证；Web/API统一授权并在检索、上下文和完整返回前重新鉴权。

John的真实问题见[question.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/question.md:1)；实际答复见[answer.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/answer.md:1)；事实证据、定性比较、撤权边界与未知见[evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/evidence.md:1)。

TR结论：WeKnora与MaxKB都依赖服务端状态核查登录token；程序凭证分别偏空间/平台和应用，不能直接代替本人用户权限交集。[1][2] FastAPI支持模块路由与同步端点，SQLAlchemy明确并发Session边界，Alembic要求人工核验迁移候选。[3][4][5]

TS推理：当前固定RAG流程需要的是统一业务规则和授权状态，采用服务端会话与随机API密钥减少两套凭证逻辑；每请求/最终输出复核落实既定产品约束。该选择基于维护成本的受托判断，没有性能实测。OWASP支持服务端会话与逐请求授权；PG快照规则提示复核必须真正读取当前状态；LangChain官方定位不构成当前引入agent框架的必要条件。[6][7][8][9]

跨维度洞见：单一PG既存业务授权，也存会话、凭证和既定任务；省去新认证状态存储，但查库与连接生命周期成为必须验收的代价。参考源码的token存在撤销机制，仍不能证明它们满足本项目历史/在途输出的完整撤权规则。

反向证据：未运行红队。保留最强反对意见：同步长请求会占线程，集中PG会增加查询；必须实际测等待和连接占用，出现瓶颈再选择异步。没有实测不宣称此方案满足任何并发量。

建议绑定：交给John作本问题技术决定输入，后续架构记录和实现沿用已定角色/需求。未修改PRD。未解决项为运行配置、版本组合和验收，均可由实现完成，user_only_missing=无。

| 编号 | 支持范围 | 发布者与来源 | 发布日期 | 访问日期 | 置信度 |
| --- | --- | --- | --- | --- | --- |
| [1] | 固定实现：业务、数据库、token/key | [Tencent/WeKnora固定源码](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L1314-L1338) | 2026-10-15 | 2026-10-15 | 中，未独立验证 |
| [2] | MaxKB应用凭证删除user绑定 | [1Panel-dev/MaxKB迁移](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/migrations/0012_remove_applicationapikey_user.py#L12-L16) | 2026-10-15 | 2026-10-15 | 中，未独立验证 |
| [3] | 同步端点与线程池 | [FastAPI](https://fastapi.tiangolo.com/async/#path-operation-functions) | 未知 | 2026-10-15 | 中，未独立验证 |
| [4] | Session并发边界 | [SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks) | 2026-10-14 | 2026-10-15 | 中，未独立验证 |
| [5] | 迁移候选人工核验 | [Alembic](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect) | 未知 | 2026-10-15 | 中，未独立验证 |
| [6] | 服务端Cookie会话、随机token校验 | [OWASP Session](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) | 未知 | 2026-10-15 | 中，未独立验证 |
| [7] | 每请求授权 | [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html#validate-the-permissions-on-every-request) | 未知 | 2026-10-15 | 中，未独立验证 |
| [8] | PostgreSQL快照边界 | [PostgreSQL](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-READ-COMMITTED) | 未知 | 2026-10-15 | 中，未独立验证 |
| [9] | agent框架定位 | [LangChain](https://docs.langchain.com/oss/python/langchain/overview) | 未知 | 2026-10-15 | 中，未独立验证 |

时效：固定SHA实现事实不会随main变化；迁移到别的提交需重查。文档按本轮访问日建立重查清单，版本/兼容类一个月内在实现锁版前复核，模式类两年仅是最长窗口，不延后安全更新。机器计算结果另存staleness.json。来源编号与台账统计由脚本检查；无HTML输出。

时效工具最早复核日：2026-11-15（版本/兼容类，采用访问日保守起算；不代表文档发布日期）。Q1同题追问已完成，见[followup-answer.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/followup-answer.md:1)。
