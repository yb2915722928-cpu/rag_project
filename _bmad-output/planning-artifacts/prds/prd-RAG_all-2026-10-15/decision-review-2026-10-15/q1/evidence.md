# Q1 证据、选择依据与未知

日期：2026-10-15。TR=technical/explore；TS=technical/select；headless 原生 run。结论只来自本轮重新读取的官方固定源码与官方文档。PRD 仅作硬约束，不能证明外部技术事实。

## 证据定位与置信度

- WeKnora SHA：a37a1bc51ad85d096df341f6d3a098f60d586f52；MaxKB SHA：0fa9a0dae8850c1878f087f0d81c974c1d424b06。官方索引记录提交日期均为2026-10-15；文件各自发布日期未知。两仓库本轮经官方 GitHub connector 按SHA读取，非浮动main。[原索引](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/imports/implementation-r1/index.json.md:1)。
- [WeKnora事实与永久行号](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/digests/weknora-r1.md:1)。官方来源Tencent，访问2026-10-15；7项实现事实已逐段阅读。[1]
- [MaxKB事实与永久行号](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/digests/maxkb-r1.md:1)。官方来源1Panel-dev，访问2026-10-15；6项实现事实由独立子代理逐段阅读。[2]
- [官方机制摘要](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/digests/official-mechanisms-r1.md:1)。FastAPI、SQLAlchemy/Alembic、Psycopg、OWASP、Python、PostgreSQL、LangChain；均访问2026-10-15，发布日期除明确列出者外未知。[3][4][5][6][7][8][9]

**统一置信度：中。** 官方源码对“该提交写了什么”的直接支持充分；单一发布者静态证据，无独立发布者确认，不等于运行验收。MaxKB digest 的“高（静态源码）”描述仅指可直接读到实现，汇总按本run的单源规则降为中并标 `unverified`。这里的未独立验证不是未经阅读，也不是判定源码错误；不为填满两个来源而用别家项目去“验证”另一家的实现。

## TR关键边界

1. WeKnora路由是Gin，数据库GORM；迁移是golang-migrate而非Alembic。其自组pipeline并不证明全仓库没有任何大框架。密码bcrypt证据另见[用户登录 L249–258](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L249-L258)，JWT入库见[L1110–1172](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L1110-L1172)。
2. WeKnora凭证模型有KeyHash，但同时有APIKey列及条件AES-GCM加解密，所以不能写成“只存hash”。ExpiresAt可空，且存在full access/管理能力；本项目要求必填到期、只读、只创建显示，需自行收紧。tenant/platform凭证及合成API principal也不能冒称绑定本人用户。
3. MaxKB Web是签名token＋缓存有效性，不依据所读片段把它笼统说成“JWT无状态认证”；引用只支持后续认证检查/退出，不支持“所有在途请求均已即时中断”。应用key迁移移除了user外键；即使有应用、工作空间边界，也不同于本项目要求的本人用户权限交集。
4. 两项目的框架不构成本项目框架选择理由；共同可借鉴的是HTTP与业务分工、数据迁移、服务端token状态和有边界的RAG流程。[1][2]

## TS选择框架

硬门槛：既定FastAPI/PG/pgvector及独立worker；用户绑定只读凭证与当前权限交集；撤销覆盖检索、上下文、完整返回和历史/引用/下载；平台身份不隐含资料权。偏好按顺序为规则一致、学习/维护简单、少常驻依赖、后续能替换。没有负载数据，不赋数字权重、不做貌似客观的分数。

| 决定 | 选中与取舍 | 主要替代、何时改选 | 可逆边界 |
| --- | --- | --- | --- |
| 应用组织 | 按业务模块组织的单体；HTTP→业务→持久化/外部适配。服务负责事务与授权，持久化不发HTTP、不自行决定角色 | 微服务只在确有独立部署、扩缩需求时再评估；当前多进程仅API/串行worker既定边界 | 业务模块不导入HTTP对象；外部依赖适配 |
| RAG | 显式函数流程；B0向量检索先行；不引入LangChain/LangGraph作为主骨架 | 有复杂可恢复工具编排、多个模型/工具路由需求才重选；不能基于“参考项目用了”决定 | 模型、嵌入、MinerU、检索各有窄适配接口；不构造万能抽象 |
| 持久化 | SQLAlchemy2同步ORM＋psycopg3；普通def端点；短事务Session在同一执行线程局部创建/结束；参数绑定查询，检索可用SQLAlchemy Core表达式 | 全异步SQLAlchemy为备选，仅在实测线程等待或需更多并发I/O时采用；不宣称同步容量达标 | 业务接口不暴露ORM对象；不让依赖创建的Session跨线程传递 |
| 连接 | API/worker各进程初始化自己的engine与SQLAlchemy有界pool，限定overflow和等待；不叠psycopg_pool；外部模型调用前提交/关闭数据库事务并归还连接 | 多进程/更多worker将乘增连接数，实现时合计限制；暂不设无测量依据的固定池大小 | 配置化；不跨进程共享连接 |
| 迁移 | Alembic单条可追溯版本链；扩展/索引显式写迁移，人工检查自动生成结果，部署独立单次执行 | 原生SQL迁移也可，但会多维护一套映射；不用启动create_all代替升级 | 开发/验收用空库及旧库升级；数据破坏变更先备份，不承诺所有downgrade安全 |
| Web会话 | 同源部署；随机Cookie对应PG会话记录，存单向hash、user_id、创建/到期/撤销字段；每次读取账号状态；退出撤当前、改密/停用撤全部 | Bearer JWT需要签名/刷新与提前撤销状态，不会省掉当前权限查询；Cookie代价是CSRF防护 | Cookie只载随机凭据，非角色/资料范围快照；设安全属性、写请求CSRF token和Origin核验 |
| 密码 | Argon2id库管理salt；官方最低建议之一19MiB、t=2、p=1作起点，实际参数/并发限制目标机校准 | bcrypt可做遗留兼容，但当前无迁移包袱；不选快SHA-256存用户密码 | 采用带算法参数的编码hash，之后按需rehash |
| API key | 32随机字节secret，公开ID用于查找；只存SHA-256校验值，用恒时比较；创建响应一次显示。元信息有用户、单空间、指定KB集合、只读动作集合、必填expires_at、revoked_at | 可逆加密无找回需求；自含JWT仍需撤销和权限复核，增加机制 | 通过Authorization: Bearer传递；只读动作白名单，不能按GET/POST粗略判断；密钥遗失重建 |
| 统一授权与撤权 | 认证得不可变身份信息，服务按当前数据库状态重算授权；每个出口默认拒绝；PG是状态源，不另加Redis；检索先带授权过滤 | 散落在路由易漏历史/下载；RLS可作以后附加防线，首版不叠第二套权限语言 | 授权服务给出scope/拒绝原因；持久化接受已限定scope，不能发起全库搜索后才删越权结果 |

以上是受托设计推理，官方文档分别支持可用机制，并未替本项目作选择。[3]支持模块与同步端点；[4]支持同步驱动及Session边界；[5]支持迁移；[6][7]支持服务端状态、密码和逐请求授权；[8]支持新鲜数据库读取；[9]界定框架功能。

## 即时撤权的精确定义与实现边界

- 撤销、账号状态、成员/库权限、资源删除在同一业务事务完成相应变更，提交成功才响应管理操作成功。每次请求读当前用户有效性、空间/成员/库范围；API额外读凭证有效期/撤销和scope，再与用户权限求交集，不把创建时快照当永久权利。
- RAG开始时按server计算的空间、KB集合、允许文档版本查询；构造上下文前复核，模型返回后以**新的局部Session及数据库查询**复核全部依赖资料和凭证，再决定整份答案放行。等待模型期间不持事务，也不拿最初Session的identity map充当刷新；PG默认Read Committed不意味着ORM对象自动更新。[8]
- 最终放行检查是请求的授权决策时点：已在此检查前提交的撤权必须可见并阻止返回；之后提交的撤权约束后续请求/后续检查。已发到客户端的数据无法召回。不得宣称数据库提交能原子控制物理网络送达；并发验收用受控时序明确“撤权提交在最终检查之前”。不把事务跨模型调用维持数十秒来假造即时性。
- 历史记录保存回答依赖的KB/文档版本集合，包括用于上下文但未成为展示引用的资料。每次历史查询/追问复核整个依赖集合；任一失权可整体隐藏该回答，且不得进入后续上下文；多KB对比同样处理。原文/引用/下载走授权服务和代理，不发撤权后仍长期可用的公开链接。
- 到期/撤销/账号停用在最终检查也重新判断；到期判断采用一致UTC时间。授权查询失败时拒绝资料输出并返回依赖不可用，不把基础设施故障伪称“已撤权”。日志只记标识、动作、结果，不记密钥或业务全文。
- API任务状态查询还校验owner_user_id与凭证空间/KB范围；密钥只用于只读API路由，不准管理Web凭证或资料写接口。平台管理员必须另有正常业务身份才获得相应资料权限。

这些边界是落实FR1–FR5/FR14的方案，不是新增角色或替用户重新定权限。

## 未知与停止理由

没有运行两项目、迁移、登录、RAG、撤权或本地产品；没有4C4GB容量、延时、连接池、登录hash成本和并发测试数据。未证明参考项目所有权限路径/在途输出均合格。滚动文档不锁依赖兼容版本，具体版本组合在实现时锁定并验证。会话绝对/空闲时长、池大小及超时为可见运行配置，当前不捏造数值。

首轮已覆盖Q1选择所需事实；遵循John要求停止抓取，不扩成认证产品调研。缺失不是用户专有事实，`user_only_missing`=无。若未来改为大量并发等待或复杂agent编排，再针对触发点更新选择；当前不问新预算、账号或角色。

## 来源表

下列来源为上文编号引用的代表入口；具体支持句子、固定永久行号及更多官方文档在三个digest中逐项记录。访问日均为2026-10-15。

| 编号 | 支持范围 | 发布者与来源 | 发布日期 | 置信度 |
| --- | --- | --- | --- | --- |
| [1] | WeKnora实现组织/认证/凭证，窄源码见digest | [Tencent/WeKnora固定提交](https://github.com/Tencent/WeKnora/tree/a37a1bc51ad85d096df341f6d3a098f60d586f52) | 2026-10-15 | 中，未独立验证 |
| [2] | MaxKB实现组织/认证/应用key，窄源码见digest | [1Panel-dev/MaxKB固定提交](https://github.com/1Panel-dev/MaxKB/tree/0fa9a0dae8850c1878f087f0d81c974c1d424b06) | 2026-10-15 | 中，未独立验证 |
| [3] | APIRouter；同步def的线程池语义 | [FastAPI官方async说明](https://fastapi.tiangolo.com/async/#path-operation-functions) | 未知 | 中，未独立验证 |
| [4] | Session/AsyncSession并发边界；psycopg同步/异步见digest | [SQLAlchemy Session官方文档](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks) | 页面生成2026-10-14 | 中，未独立验证 |
| [5] | Alembic自动生成必须人工核验 | [Alembic官方autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect) | 未知 | 中，未独立验证 |
| [6] | 会话服务端状态、hash、Cookie、CSRF | [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) | 未知 | 中，未独立验证 |
| [7] | 最小权限、默认拒绝、每请求检查；密码等相关官方页见digest | [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html#validate-the-permissions-on-every-request) | 未知 | 中，未独立验证 |
| [8] | PostgreSQL事务快照与最新已提交状态 | [PostgreSQL官方事务隔离](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-READ-COMMITTED) | 未知 | 中，未独立验证 |
| [9] | LangChain agent与LangGraph定位 | [LangChain官方overview](https://docs.langchain.com/oss/python/langchain/overview) | 未知 | 中，未独立验证 |
