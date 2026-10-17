---
title: RAG_all 技术选择与 John—Mary 对话
created: 2026-10-15
updated: 2026-10-15
status: complete
decision_basis: 用户既定选择及本轮明确授权的 Mary 受托实现选择
---

# RAG_all 技术选择与 John—Mary 对话

本文记录本轮真实发生的提问、研究回答和追问，便于理解为什么选择这些技术。对话正文整理表达并链接每轮原始问题与回答，不伪造此前未发生的讨论，也不将研究结论写成部署或测试结果。

用户授权 John 自行提问、Mary 先做 TR（核对两项目的实现事实），再做 TS（为本项目选择）。每完成一个 John 大问题再新建 Mary；同问题追问回原 Mary。只有账号、资源访问或个人偏好确需补充时才由用户作答。

## 阅读方法与已有边界

- **用户已选**：FastAPI＋PostgreSQL＋pgvector；Vue 3＋TypeScript＋Vite；PG 持久化任务＋独立 Python worker、文档并发 1；MinerU 云端 API；API 优先；基础向量 B0 后按真实失败优化。
- **本轮受托选择**：Mary 在上述约束内选择具体工程方案，John 核对是否满足 PRD；不冒称用户逐项亲选。
- **实施初值**：配置起点可以调整，不是性能、容量或成本承诺。
- **待验证**：需真实代码、资料、API 或服务器测量，研究不能代替。

生产目标仍为 4 核、4 GB Ubuntu 同机运行 Web、API 与数据库。电脑用于开发调试，用户提供 16 GB 内存，本机读取到 i7-12700H、RTX 3060 Laptop 6 GB。约半个月为预期，AI 实际开发，用户核对理解；不要求现场演示。本轮不开始开发，不配置账号或调用收费 API。

TR 的参照提交为 WeKnora `a37a1bc51ad85d096df341f6d3a098f60d586f52`、MaxKB `0fa9a0dae8850c1878f087f0d81c974c1d424b06`；仅用于追溯，不表示已选为开发基线。产品角色、四场景、冻结验收与 K=5 沿用 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md)。

## 本轮选择总表

| 方面 | 本轮选择 | 状态 |
| --- | --- | --- |
| 应用组织 | 模块化单体，HTTP、业务、持久化与显式 Python RAG 分开；暂不引入 LangChain／LangGraph | Q1 受托选择 |
| 数据访问 | 同步 SQLAlchemy 2＋psycopg 3；FastAPI 普通 def 路由；Alembic 管迁移 | Q1 受托选择 |
| 登录与程序凭证 | PG 服务端 Cookie 会话＋Argon2id；用户绑定、仅存 hash 的随机只读 Bearer 密钥 | Q1 受托选择 |
| 授权与撤权 | Web／API 共用当前授权规则，凭证范围与用户权限取交集；完整答案放行前复核 | Q1 受托选择 |
| 任务恢复 | PG 短事务领取、租约心跳、attempt 代次条件写入；单处理线程＋独立续租线程 | Q2 受托选择 |
| 外部解析与来源 | MinerU 云端上传，先存上游 ID 再上传；保存原包／响应并归一页、段、表、图来源 | MinerU 为用户已选；具体机制为 Q2 受托选择 |
| 版本与删除 | 不可变候选版本完整就绪后原子切换；删除先墓碑阻断，清理可重试 | Q2 受托选择 |
| 分块与向量 | 保留段／表／图结构与来源；embedding 独立配置、维度及索引版本；初选余弦距离 | Q3 受托选择，模型接入时定 |
| 检索与场景 | 授权范围＋活动版本过滤的精确向量 B0；四场景共用步骤、输出 schema 分开 | B0 与场景为用户既定；具体编排为 Q3 受托选择 |
| K=5 与输出 | 整请求最终最多五块；对比按固定名次轮转合并；引用 ID 白名单及后端鉴权定位 | Q3 受托选择，不修改验收门槛 |
| 前端配套 | Vue Router＋Pinia＋Element Plus，自建页面与 API 客户端，电脑构建静态产物 | Q4 受托选择，Vue 主栈为用户已选 |
| 部署与文件 | Compose 运行 Nginx、API、worker、PG＋pgvector；受控文件目录与后端授权读取 | Q4 受托选择 |
| 密钥与恢复 | 用户密钥只存 hash；供应方密钥服务端加密、主密钥分离；停写一致备份并做恢复演练 | Q4 受托选择，尚未配置 |
| 记录与验证 | JSON 运行日志＋PG 审计／调用用量，pytest／真实 PG／Playwright／独立评估；低初值后实测 | Q4 受托选择，尚未执行 |

四题已闭环。以上是既定范围内的受托实现选择；尚未开发、接通 API、部署或得到效果／性能成绩。原问题、TR／TS、追问和来源均保留，具体依赖版本与环境参数在实施时锁定核验。

## 问题一：应用骨架、数据库访问与可信访问

本题使用新 Mary，TR、TS 与追问都由该位 Mary 完成；已收口。[原问题](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/question.md)、[完整答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/answer.md)、[证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/evidence.md)。以下为真实交流的整理。

**John：** FastAPI 项目怎样组织接口、业务和 RAG 模块，怎样访问 PostgreSQL、管理表结构，并实现 Web 登录、用户绑定的只读 API 凭证及即时撤权？先说明两项目怎么做，再为本项目选择，不整套照搬或重定义角色。

**Mary／TR：** WeKnora 使用 Gin、GORM 和版本迁移，自组 RAG 事件流程；Web 使用 JWT，但仍查令牌撤销与账号状态。MaxKB 使用 Django／DRF、ORM 与 Django 迁移，聊天可走流水线或工作流，其 Web token 也依赖服务端状态。两项目的程序 key 归属分别围绕租户／平台或应用／工作空间，不能直接当作本项目“绑定本人用户”的凭证。[WeKnora 校验](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L1314-L1338)、[MaxKB 程序凭证迁移](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/migrations/0012_remove_applicationapikey_user.py#L12-L16)。

**Mary／TS：** 我选择以下组合，理由是先把规则做一致，再由实测判断扩展需求。

1. **模块化单体。** 接口负责接收与校验，业务服务管规则，持久化管数据库；Web、API、worker 共用核心业务和 RAG。少部署服务，代价是要守住模块边界。
2. **显式 RAG 步骤与模型适配器。** 解析、向量化、检索、上下文、生成、引用校验逐步可见。首版不引入大型编排框架，便于定位和学习；代价是自己维护这些步骤。
3. **同步 SQLAlchemy 2＋psycopg 3、Alembic。** FastAPI 使用普通 def 路由，每个数据库阶段独立短 Session。先减少并发编程复杂度；代价是外部调用等待会占请求线程，须设超时与并发限制，测到排队问题再评估异步。表结构使用显式迁移，不在应用启动时随意自动改表。[FastAPI 行为](https://fastapi.tiangolo.com/async/#path-operation-functions)、[Session 并发边界](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks)。
4. **PG 服务端会话。** Cookie 只带随机会话凭据，服务端保存 hash、用户与到期／撤销状态。退出、改密、停用容易统一失效；代价是逐次查库并做好 Cookie 属性及 CSRF／Origin 检查。密码使用成熟 Argon2id 实现，参数在目标机器校准。
5. **程序密钥独立于 Web 登录凭据。** 随机生成，仅创建时显示；数据库只存公开 ID、secret hash、绑定用户及 scope／到期／撤销。凭证遗失后重建，不能从数据库取回。
6. **统一后端授权。** API 不是新角色，有效动作取只读白名单、凭证 scope、当前用户权限的交集；检索、历史、引用、下载及完整输出前都按当前状态检查。多查库是代价，换取规则一致。

**John 追问：** 同步访问怎样保证模型等待不占数据库连接？Cookie 与 API key 怎样共用业务授权又不混淆只读限制？最后的权限检查是否意味着网络发送与撤权原子发生？[实际追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/followup-question.md)。

**Mary 回答：** 每段数据库工作在当前线程创建并关闭 Session，只向后续步骤传普通数据；调用模型前先释放连接，返回后另开 Session。Cookie 和 API key 各自认证成同一个用户身份，保留渠道和凭证限制，共用业务服务。最后复核只保证放行前读取当前已提交状态，不承诺网络发送与撤权构成全局原子操作，也不能收回已显示或下载内容。[原答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/followup-answer.md)。

**John 收口：** 采用本题组合。同步数据访问是本轮受托选择，替换技术补充中仍标为候选的异步建议；没有把撤权检查说成无法兑现的网络原子保证。后续题必须沿用短 Session 和统一授权。

**理解检查：** 接口像接待员，业务层决定能做什么，数据库层负责读写，RAG 只处理获准资料。程序密钥是绑定本人、范围更窄的通行证；登录成功不等于永远拥有资料权限。

## 问题二：文档导入、外部解析与生命周期

第一题闭环后另建 Mary，本题 TR、TS 与追问均已完成。[原问题](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/question.md)、[完整答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/answer.md)、[证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/evidence.md)。

**John：** 已选 MinerU 云端 API，文档从上传到可查询、版本更新和删除应怎样完成？请核对两项目的任务、来源和生命周期，再选择我们的恢复方案。外部结果未知、旧 worker 迟到或处理中被删除时，如何避免重复生效和资料复活？不要承诺外部调用恰好一次。

**Mary／TR：** WeKnora 有有限重试、attempt 与删除／完成状态守卫；部分重解析路径先清旧资源。MaxKB 标准分段保存原件，refresh 路径是重向量化，任务按文档去重；不能把两者直接当成我们所需的候选版本切换。MinerU 本地文件的云流程是申请上传链接、PUT 文件、自动解析，再按 batch_id 查询。data_id 是业务关联，不构成已证实的幂等或任务找回保证。[WeKnora 任务守卫](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L3671-L3715)、[MaxKB 队列](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/task/embedding.py#L61-L92)、[MinerU 官方 API](https://mineru.net/doc/docs/)。

**Mary／TS：** 我选择“PG 任务＋分阶段产物＋不可变文档版本”。

1. 原件和任务先落盘，再解析、校核、分块、向量化。TXT／Markdown 直接读，PDF／DOCX 走 MinerU；云输出先保存再归一，不能只留最后的 Markdown。
2. 用短事务及 SKIP LOCKED 领取任务，提交后才做耗时操作。租约失效允许回收；每次领取增加 attempt，心跳、产物写入、发布都核对当前代次与文档／父级状态。租约能判断失联，代次条件才能挡住迟到者。
3. 保存上游 batch_id 等标识后再上传；PUT 超时先查原 batch，确实无法判定则显示待核对，不无条件重交。数据库能保证自己的入库幂等，不能替外部厂商保证不重复调用。
4. 版本、配置、阶段共同标识已校验产物；重试可复用。原件哈希、响应／ZIP、解析配置、章节、段／表／图 ID、PDF 页及可得坐标都保留。PDF 页统一从 1 起，DOCX 无可靠物理页时使用结构位置，不编页码。
5. 新候选完整就绪且仍是当前待发布版本时，在一个 PG 事务里切活动指针。失败保旧版，迟到旧候选不能覆盖新候选；旧版本仅供历史引用鉴权回看。
6. 删除先写墓碑，检索、引用、下载立即按删除状态拒绝，再异步清理文件与索引。清理失败可重试；旧任务返回也不能清除墓碑或发布资料。

这些机制多出状态与暂存空间，换来可以解释、检查和恢复的过程；并不意味着本轮已经实现。

**John 追问：** 同步等待云接口时谁续租？部分页面失败如何发布，能否覆盖完整旧版？检查点恢复是否等于逐页断点或上传续传？[实际追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/followup-question.md)。

**Mary 回答：** 一个主处理线程只处理一份文档，另一个续租线程只用自己的短 Session 更新租约，不领取文档，因此文档并发仍为 1。首次导入只在失败范围明确、通过部分有可靠定位时发布部分可用内容，并标注不完整；不完整的替换候选不覆盖旧版，修正／重试至完整就绪才切换。正常文档自动校核发布，不加全量人工审批。检查点仅指复用已校验阶段产物，不承诺 PDF 逐页恢复、上传字节续传或外部恰好一次。[原答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/followup-answer.md)。

**John 收口：** 采用该机制。任务状态不能替代文档版本状态，API 返回成功不能替代质量校核；新版本和删除的发布守卫都要在后续真实故障测试里验证。

**理解检查：** 每次更新像一份候选稿。后台可以重做，但只有当前有效任务能登记成果；新稿完整才换入口。删除先封入口，再清资产。没有回信时先找原任务，不能假定云端没处理。

## 问题三：RAG 基线、四场景与证据

第二题闭环后另建 Mary，本题已完成真实追问并收口。[原问题](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/question.md)、[完整答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/answer.md)、[证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/evidence.md)。

**John：** 既然先做 B0，分块、向量化、检索、上下文、答案和引用怎样衔接？请先核对两项目，再选择覆盖四场景的最小共享链路，说明追问如何不绕过权限，不把关键词、重排和 ANN 提前变成必做。

**Mary／TR：** WeKnora 的块和索引关联来源位置，改写内容仍须关联原块引用；MaxKB 把检索、消息构造和生成分步，多库会检查 embedding 一致，检索带知识库和 active 条件。它的历史拼接方式不能自动满足我们撤权后隐藏旧回答的规则。[WeKnora 引用](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/chat_pipeline/citation_sources.go#L96-L191)、[MaxKB 检索步骤](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py#L35-L79)。

**Mary／TS：** 选择“结构块→API 向量→授权精确检索→最多五块上下文→结构化答案→后端引用”。

1. 正文按章节／段落组织，超长再拆；表格按行组拆并带表头、单位和适用条件，图意说明带图号、图注及原位置。约 600 中文字、重叠 80 字只是可调初值，仍受模型 token 上限约束，不是最佳参数或质量承诺。
2. 向量化单独配置供应商、型号、可得版本、维度、归一化策略和索引版本。查询与文档采用相同配置，拒绝异常向量；变更配置需要重建候选索引再切换，不能混用。初选余弦距离及一致 L2 策略，具体 API 型号使用前再定。
3. B0 在当前空间、授权库、active_version、未删除且校核通过的块中做精确向量排序。先建立可解释起点；代价是扫描耗时须测，后续才按失败考虑关键词、重排或 ANN。
4. 四场景共用证据链，但输出分别约束：企业流程／材料／条件／负责人；排障候选原因／检查步骤；对比每格四种状态及证据；手册型号／参数／单位／限制与页表图定位。缺少某格证据时不能靠整体 TopK 宣称整张表已核验。
5. 模型只输出本轮候选内的 evidence_ids；后端检查结构和 ID，再按当前权限解析原文位置，不信任模型生成的下载地址。合法 ID 仍可能配错事实，语义支撑要单独验收。
6. 追问只用有限、当前仍有权的同空间历史理解代词或改写；默认不把旧答案送给最终生成器。每轮仍重新检索和授权，历史不充当新证据，切空间新建会话。
7. 开发题调优、32 冻结题验收分开，逐题保留配置、覆盖、答案与引用、耗时、资源、真实用量和费用；未知费用不填成零，退步和失败不删。

**John 追问：** 对比的多个子查询如何固定取全局五块，避免跨查询分数误比？五个候选与金标证据单元是否同一个概念？JSON 错误或引用越界怎样处理？[实际追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/followup-question.md)。

**Mary 回答：** B0 按请求条件原序、对象文档 ID 升序组成固定子查询序列，各路内部按余弦距离和块 ID 排序；轮流取各路第 1 名、再第 2 名，跳过重复，合计到五块或耗尽，不比较跨查询分数。五块限制的是候选数量，一块可直接支撑多个原标注证据单元，SM-2 分母保持不变；裁掉的证据不计命中。五块不足就标具体缺口，但 SM-1 和每场景通过门槛照旧，不能靠全面拒答达标。首版仅做去 JSON 围栏／空白等无语义本地清理；仍不合 schema 或 ID 越界则整答可见失败，不自动追加模型修正调用。[原答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/followup-answer.md)。

**John 收口：** 采用以上 B0 和四场景编排。轮转属于可复现起点，不代表已证明是最佳分配；同一冻结口径下保留失败，再决定优化。格式正确、引用可打开、引用真正支撑事实是三项不同检查。

**理解检查：** 向量负责找相近证据，不负责判断事实。模型只拿服务器选出的最多五块回答；“我以前回答过”不能成为继续读取已失权资料的理由。

## 问题四：前端、部署与工程验证

第三题闭环后另建 Mary，本题已完成追问并收口。[原问题](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/question.md)、[完整答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/answer.md)、[证据与细节](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/evidence.md)。

**John：** Web 页面、文件保存和 4 核 4 GB 服务器部署怎样组织？先核对两项目的前端、文件访问、部署与记录，再选择页面、静态构建、同源代理、文件、备份、密钥、日志、测试和限额。区分实施初值与实测达标，不让用户凭空报规模或预算。

**Mary／TR：** WeKnora 使用 Vue／Vite、Router／Pinia 和 TDesign；前端在 Node 阶段构建，再由 Nginx 提供静态文件并代理请求，有本地文件卷、授权下载和可配置 logger。MaxKB 使用 Vue／TypeScript／Vite 与 Element Plus，其开发代理有文件入口，容器带数据卷与构建标识。本轮没有核实 MaxKB 完整存储和日志链，不能由这些配置推导它已满足我们的权限、审计或成本要求。[WeKnora 构建](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/frontend/Dockerfile#L26-L68)、[MaxKB 前端配置](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/ui/package.json)。

**Mary／TS：** 我选择以下交付组合。

1. **前端自建，组件复用。** Vue Router 管页面，Pinia 管身份／空间／界面状态，Element Plus 做表单、表格和对话框。参考两项目交互，不复制整套业务；切空间或退出清理私有缓存。任务轮询、答案一次返回，引用按后端 ID 解析，Markdown 清洗后渲染。代价是要独立联调，前端隐藏入口不代替后端授权。
2. **电脑构建，服务器运行四服务。** Compose 管 gateway（Nginx）、API、worker、PG＋pgvector；静态页面和 API 同源，仅 gateway 对外。服务器加载预构建产物，不在 4 GB 机器上跑 Node 构建。迁移单独执行，记录镜像／配置／迁移版本；退回旧镜像不等于数据库能自动回滚。HTTPS 使用 Nginx，域名与可信证书实际接入时落实。
3. **文件放受控目录。** 原件、MinerU 原响应／ZIP、归一结果按内部文档 ID 和不可变版本保存，PG 保存归属、哈希和定位关系。gateway 不挂载原件目录，下载经后端授权。流式落盘、临时文件校验后提交；ZIP 检查展开大小、文件数、绝对路径和路径穿越。
4. **备份先保证能恢复。** 先停写、等待或明确终止在途，再停应用写入者；同一备份号收集 DB、文件、必要角色、配置、发布与迁移清单。主密钥另行加密封存，数据保留受控离机加密副本；恢复演练检查数据、哈希、权限和未完成任务。代价是维护窗口。[PG 备份边界](https://www.postgresql.org/docs/17/backup-dump.html)。
5. **两种密钥两种保存办法。** 用户程序 token 只需校验，存 hash；千问／MinerU 密钥要用于调用，需服务端认证加密并能还原，外置主密钥按服务注入，不进 Git、镜像或前端。容器 secret 只是挂载机制，不自动加密宿主文件；旧备份也需要匹配的主密钥版本才能恢复。[Compose secret 机制](https://docs.docker.com/compose/how-tos/use-secrets/)。
6. **运行日志、审计和调用账分工。** JSON 日志串起请求／任务／阶段与错误；PG 审计记录权限、配置、资料操作，用量表逐次记录供应方调用与已知状态。未知 usage 不填零，估价不冒充账单，失败和重试不消失；不默认写私有全文，复现资料另放受控证据集。
7. **按风险测试。** pytest 验业务规则，真实 PG 验事务／领取／代次与撤权，独立权限与故障套件，Playwright 验 Web 主流程；32 冻结题独立验收。AI 先整理每场景 3 份、共 12 份公开或明确模拟资料作为测试起点，实施时统计页数、字数和块数，不当作用户真实负载。

**John 追问：** 配置表是否只是初值？单次 HTTP 超时是否等于整文处理时限？容器 secret 和备份是否已经落地？如何限制 ZIP、避免日志泄漏及保留独立验收？[实际追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/followup-question.md)。

**Mary 回答：** 所有数字都仅为实施起点，可按服务器和账号硬限制下调。单次读超时不等于 MinerU 整文时限，阶段等待、应用总 deadline 与代理超时需协调；未知状态查原任务，禁止无条件自动付费重试。离机备份仅是方案，本轮没有上传或创建定时自动化。恢复需要密文和对应主密钥；签名 URL、Cookie 和密钥不打日志。ZIP 和文件仍由后端限制与鉴权。12 份只是拟备样例，32 题继续冻结、独立验收。[原答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/followup-answer.md)。

**John 收口：** 采用本题组合；GPU 不改变 API 优先与服务器同部署方向。页面、文件与证据出口共享已有权限；低配置起步后必须测量，不能以限额相加宣称 4 GB 已经足够。

### 首次运行的可调起点

这是本轮受托选择的测试配置，**没有实施或实测**。依赖版本、云端硬限额、服务器实况及镜像支持在接入时核对；不足则下调，未经验证不对外承诺。

| 项目 | 初值 | 怎么理解 |
| --- | --- | --- |
| 进程与并发 | API 1 进程；问答执行 2、等待 4；文档 1＋续租线程 | 超量明确拒绝，仍要测排队与连接占用 |
| 数据库 | API 池 3、worker 池 2，overflow=0；池等待 5 秒，PG 上限 20 | 留管理余量，各池独立，外部等待不占连接 |
| 容器内存上限 | PG 1536、API 768、worker 768、gateway 128 MiB | 合计 3200 MiB 只是约束起点，仍可能 OOM |
| 文件 | 单份 20 MiB、每批 5 份；展开总量 256 MiB、最多 2000 文件 | 网关计入 multipart 开销，API 逐项再校验；超限不能截断伪装成功 |
| 时间 | 外连 5 秒、单次读 120 秒；问答总 180 秒、代理 200 秒 | 与阶段 deadline 协调，非 MinerU 整文总时限；日期 UTC 保存、上海时区展示及配额日界 |
| 日志与状态 | 每服务 20 MiB×3 轮转；任务可见时 3 秒轮询 | 页面后台退避／暂停，记录保留需求再据实调整 |

**理解检查：** 电脑把页面构建好，服务器负责发页面和处理业务。原件与证据锁在后台，点引用也重新查权限。可恢复备份是“在干净环境能恢复成功”，不是“产生了一个压缩包”。

## 本轮完成与后续事实

本轮四个大问题均完成 TR→TS 与原 Mary 追问，选择已收口；没有需要用户现在补充才能做出这些方案选择的事项。具体凭证和账号由实际接入时在安全配置入口填写，服务器访问与证书条件届时核验；不要求在聊天里提交密钥。

接下来实施需要留下的证据是：锁定依赖及镜像版本、迁移与配置；各格式实际 MinerU 响应及来源校核；权限／版本／恢复负例；四场景与 32 题原始输出；目标机资源与真实调用成本；一次可复现优化比较和异常复盘。未得到这些证据前，本文只支持解释“选了什么、为何这样选、还须验证什么”，不支持讲成已完成工程经验。

需求基线见 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md)，受托选择和来源总索引见 [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md)，逐轮真实优化记入 [OPTIMIZATION_LOG.md](/E:/aaa-project/rag/OPTIMIZATION_LOG.md)，开发问题记入 [DEVELOPMENT_ISSUES.md](/E:/aaa-project/rag/DEVELOPMENT_ISSUES.md)。阅读和复述检查由 [INTERVIEW_PREP.md](/E:/aaa-project/rag/INTERVIEW_PREP.md) 持续维护，不因文档完成就登记用户掌握。

## 把术语对应到本项目的问题

以下是前述真实问答的白话索引，机制和来源见各题证据；词表不代表已经实现或用户已掌握。

| 术语 | 在本项目里解决什么问题 |
| --- | --- |
| 模块化单体 | 部署少量进程，同时用代码边界分清账号、资料、RAG 和任务职责，便于定位问题 |
| ORM／SQLAlchemy | 用统一方式组织业务数据读写；仍需理解查询、事务和约束，不是不用学数据库 |
| 数据库 Session | 某一段数据库操作使用的工作单元；与“用户登录会话”是两个概念，不能跨模型等待长期占连接 |
| 事务 | 让活动版本指针和相关状态一起成功或一起失败，避免只切换一半 |
| Alembic 迁移 | 记录数据库表结构怎样逐版演进，让空库建立和已有库升级可追溯 |
| scope／有效权限交集 | 程序凭证比本人权限更窄；本人失权后，旧凭证不能保留失去的访问权 |
| 租约和心跳 | worker 在一段时间内领取任务，持续续租；过期允许回收，但不能据此认定旧进程一定停止 |
| attempt 代次 | 给每次任务领取编号，迟到的旧执行者即使拿到结果，也不能覆盖新执行者的状态 |
| 检查点 | 保存已经校验的阶段产物，重试时复用；不自动等于 PDF 逐页恢复或上传续传 |
| 活动版本／候选版本 | 当前查询入口与尚未发布的新稿分开，新稿不完整时旧版继续服务 |
| 删除墓碑 | 先标记资料已删除并拒绝访问，后台再清资产；清理失败不会让资料恢复可读 |
| embedding 配置 | 决定文本如何变成向量；文档和查询的型号、维度及处理规则必须匹配 |
| 候选块／证据单元 | 候选块是给模型的资料片段；证据单元是题目标注的必要事实，一块可支撑多个事实 |
| schema／引用白名单 | 检查答案结构和引用 ID 是否允许；不代替“事实是否真的被引用支持”的语义核验 |
| 产品配额／实际 API 成本 | 同一请求重试可不重复扣产品次数，但供应商实际产生的重试调用仍要逐次记录 |

## PRD 定稿追加澄清

四个技术大问题完成后，John 又向新建的定稿核对 Mary 发出业务定义追问；同一位 Mary 回答并收口。以下为本轮真实交流的整理，不改写前面四题的原始回答。[实际追问整理](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/finalization/clarifications-question.md)、[Mary 原答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/finalization/clarifications.md)。

**John：** 候选版本、部分可用、DOCX 无物理页、外部结果未知、失败配额和备份恢复怎样写成可验收的规则？能否在原范围内直接澄清，避免把实施验证误当作 PRD 未完成？

**Mary：** 可以。候选不检索；首次部分可用不放宽替换稿完整性。PDF 用物理页，DOCX 等无稳定页码时用实际结构；自动校核检查格式、完整性和来源，不证明每个字或事实正确。未知结果先查询原任务，维护者知情后可显式重交，原关联、迟到守卫和删除阻断不变。

**John：** 问答配额是否按成功结果结算，失败只留下真实外部成本？

**Mary：** 按空间预留并结算，正常答复含合规的不足／澄清／冲突计一次，拒绝和执行失败释放预留；同 ID 重试不重扣，跨日仍归受理时上海日期。纯检索、引用和任务状态不扣问答次数，全部实际调用／失败／未知费用仍记录，产品次数不能代替限流。恢复还必须拿到匹配的 DB、原件、解析／引用资源、配置和密钥，并在隔离环境验证引用、授权、删除和未完任务。

**John 落稿：** 这些澄清进入 FR-4、FR-6、FR-7、FR-15、NFR-5 与术语，旧的默认关键词链路和面试材料“所有优化待实现”措辞已修正。四场景、K=5、原金标分母与全部验收门槛不变；没有执行新 API 调用或产品测试。
