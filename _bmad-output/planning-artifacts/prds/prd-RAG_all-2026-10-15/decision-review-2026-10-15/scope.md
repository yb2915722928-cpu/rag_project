---
title: RAG_all 剩余实现决策范围
date: 2026-10-15
role: Mary
stage: scope-only
status: complete
evidence_boundary: 项目文档仅用于提取需求约束；本文件未核验外部能力
---

# RAG_all 剩余实现决策范围

本阶段完整读取了 PRD、技术补充、汇总和讨论记录，只分类剩余事项，尚未进行 TR、TS、编码或实测。下表的“现在需决定”是后续研究与受托选择的题目，不是本阶段已经采纳的方案。

按 John 转达的最新用户澄清，阶段单位是**一个 John 大问题**：该问题由同一位新建 Mary 连续完成 TR→TS，并接受同问题追问；完成后再为下一个大问题新建 Mary。不是每次 TR、TS 分别换人，也不并行开启多个大问题。此口径覆盖本次读取的 [讨论记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:87) 中较早的阶段解释。

## 1. 已有选择与产品基线

| 分类 | 已经确定，后续直接继承 | 需求证据 |
| --- | --- | --- |
| 用户已选技术与部署 | Python；FastAPI＋PostgreSQL＋pgvector；Vue 3＋TypeScript＋Vite；Web、API、DB 同部署于 4C4GB Ubuntu；电脑用于开发调试，API 优先；电脑 Milvus 仅为后续可选实验 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:19)，范围：19–25 |
| 用户已选任务与解析方向 | PG 持久化任务＋独立 Python worker，初始同时处理一份文档，进度、失败、重试、重启恢复；MinerU 云端 API 上传解析，不自托管，不继续旧 OCR 或多引擎对照 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:21)，范围：21–23；[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:139) |
| 产品权限基线 | 个人／团队空间、三类团队角色、逐库授权、负责库职责；平台身份不自动获得业务资料；Web 受控写入，程序 API 为用户绑定、单空间、指定知识库、有期限可撤销的只读凭证；撤权覆盖输出前、历史、引用和下载。含用户直接确认与此前受托产品选择，不能统称用户逐条亲选 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:29)，范围：29–32；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:96)，范围：96–160 |
| RAG 与验收基线 | 四场景全部交付；先纯向量 B0，按失败逐轮优化；32 冻结题与独立开发题分开，最终 K=5；权限独立全通过；复杂表格、OCR、图意与引用要求不变；不锁死关键词、融合或重排 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:259)，范围：259–281；[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:127)，范围：127–133 |
| 工作与教学目标 | 约半月为预期；用户核对方案、技术栈并理解项目，AI 实际编码、集成、测试、文档；求职经验讲述而非现场演示；不再问每日编码工时；真实问题与真实优化持续记录 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:17)；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:296)；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:308)，范围：308–320 |

## 2. 八个主题：现在需决定与实施验证分开

“现在需决定”由后续 Mary 在既有约束内先 TR、再 TS，形成受托实现选择；常规工程事项不转给用户作答。“实施验证”需要代码、样例、故障注入或目标环境数据，不能以研究建议替代。

| 主题 | 现在需决定：后续 TR／TS 题目 | 实施验证：不得写成已通过 | 项目约束证据 |
| --- | --- | --- | --- |
| 1. 应用分层、数据访问与模型适配 | HTTP 入口、业务服务、RAG 模块、worker 的最小边界；是否采纳 SQLAlchemy 异步访问＋Alembic；事务与数据库会话归属；模型 SDK 直接适配或轻量封装的边界；可实际抽取的上游模块 | 独立导入与依赖边界、迁移可重放、事务回滚、模型配置与失败映射；核验依赖和许可证，不以语言一致推定模块可搬 | [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:100)，范围：100–117；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:326) |
| 2. Web 登录、只读凭证与后端授权 | 账号密码的存储与 Web 会话机制；程序密钥存储、识别和撤销；统一后端授权入口；检索前、生成返回前、历史与文件读取如何复核当前权限 | 会话失效、账号停用、凭证到期／撤销、范围交集、跨空间／跨库、历史／下载、进行中问答撤权等负例；前端入口隐藏不能替代授权 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:138)；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:146)，范围：146–160；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:224)，范围：224–228 |
| 3. PG 任务与外部调用恢复 | 原子领取、租约／心跳、失联回收、重试上限、幂等标识与阶段落盘；导入和清理共用 worker 的边界；外部 API 请求已发送但结果未知时如何避免盲目重复付费和重复生效 | 重启、超时、断连、重复领取、旧 worker 迟到提交、解析或清理失败；产品配额幂等与真实外部调用逐次记账；不声称恰好执行一次或断点续传 | [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:106)；[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:119)；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:232)，范围：232–244 |
| 4. MinerU 适配、来源与文档生命周期 | 云端上传、轮询、结果下载和上游标识的持久化；TXT／Markdown 等直接读取的边界；统一解析结果结构；原件、页码、表格／图块、图意与分块关联；版本生效和删除清理边界 | 所有承诺格式逐项导入；实际 API 字段和限制；扫描、表格数值单位、简单跨页关系、图意及引用定位人工核验；新版本失败保旧、成功切换、旧引用可查、删除先阻断；只有实际图意缺口出现才另议补充 API | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:164)，范围：164–186；[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:148)，范围：148–154 |
| 5. B0、引用与四场景编排 | B0 的初始分块和来源单元组织、embedding 配置／维度与索引版本记录、过滤与检索接口、上下文及结构化引用校验；四场景共享流程与差异化输出；追问上下文的权限边界 | 固定 K=5 与同口径证据覆盖；型号／版本／单位不混用；证据不足／冲突正确表达；四场景验收和权限套件；后续关键词、重排、索引优化由实际失败驱动，不在本轮预选必做 | [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:121)；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:190)，范围：190–228；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:261)，范围：261–281 |
| 6. Vue 前端与上游参考模块 | 自建页面骨架与可选择参考／抽取的交互模块；前端 API 客户端、空间／会话状态、等待／失败、任务与解析校核、引用查看、角色入口组织 | 上游组件真实依赖、接口改造与许可；构建产物；四场景、任务重试、版本、失权历史、引用和下载的 Web 主流程；不预设 MaxKB 页面无改造可用 | [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:107)；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:222)，范围：222–228；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:300)，范围：300–305 |
| 7. 受控文件、部署与恢复 | 是否采纳受控本地目录、Compose、Nginx 同源代理；原件／产物路径与后端鉴权读取；API／worker／DB 的低连接初值、资源配置；备份范围、一致性和恢复步骤 | 目标 Ubuntu 干净启动与核心流程、实际资源峰值、API 连通、连接耗尽与重启；文件与 DB 一致恢复；服务器磁盘实际余量；不以 4GB 已选定推定容量可行 | [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:108)，范围：108–110；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:250)，范围：250–255；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:341) |
| 8. 可观察性、测试、负载与限额 | 请求／任务标识、分阶段耗时、调用与费用记录、审计事件、错误映射；单元／集成／权限／故障／评估组织；由 AI 整理公开或模拟样例和测试负载；文件、批次、超时、配额时区等可配置初值 | 首次固定环境测得耗时、资源、成功率与成本后再定绝对门槛；32题不等于语料规模；样本少于20次不报告有代表性的P95；配额幂等与实际失败重试成本分开；检查日志无正文与密钥泄露 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:238)，范围：238–255；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:344)，范围：344–347 |

备份恢复、会话形式、任务租约等是本次大问题要求核对的实现题目，不冒称 PRD 已逐项指定了具体机制。任何数值实现参数均须标为可调初值或建议测试负载，不能写成客户容量、已达 SLO 或 API 价格。

## 3. 真正只有用户能提供的事实

| 用户事实或操作前提 | 何时才需要用户介入 | 可先由 AI 自主完成的工作 |
| --- | --- | --- |
| 具体起止日期，以及是否有新的硬约束或偏好 | 用户确实要求固定日期、改变范围或补充限制时；约半月预期不重新追问每日工时 | 依据已定范围形成阶段顺序、记录实测阻碍与实际进度。[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:340) |
| 千问和 MinerU 实际账号、可用凭证、充值决定及用户允许处理的非公开资料 | 实际接入、付费调用或使用该资料之前；本阶段不配置账号、不收费上传 | 阅读公开官方协议；提出适配与最小样例方案。具体生成、embedding 或视觉型号仍需按用途选择，不能从“千问小模型”推定一体适用。[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:342)；[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:148) |
| 服务器连接权限、实际账号可执行范围，以及没有只读查询途径的环境事实 | 后续真正接通环境、权限不足或无法自查时；当前不操作服务器 | 获授权接通后，Ubuntu 版本、磁盘、资源与连通性原则上可由 AI 只读核查，不必要求用户凭记忆填表。[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:341) |
| 用户实际掌握程度、已做过的经历与反馈 | 教学核对和练习时，由真实回答判断；不得代编 | 准备原理与取舍讲解、代码证据和追问题，按实际更新理解记录。[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:318)，范围：318–320 |

用户没有承诺拥有企业数据或已知生产文档规模，不能将“先交企业资料／先报容量”设为当前研究的前置条件。公开可用资料和明确标注的模拟内部制度可由 AI 搜集、核验使用条件并形成样例；若以后出现真实语料，再记录其统计及适用边界。依据：[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:69)、[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:255)、[讨论记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:17)。

## 4. 下一阶段证据交接边界

- TR 的两项目参照锁定 WeKnora `a37a1bc51ad85d096df341f6d3a098f60d586f52`、MaxKB `0fa9a0dae8850c1878f087f0d81c974c1d424b06`；它们是研究快照，不是本项目已选开发基线。既有登记见 [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:141)。
- 新 Mary 可重读已有官方源码快照并注明本轮复读；本文件及 PRD 不能充当上游能力证据。TR 需给出实际调用链、永久源码链接和行号，再由 TS 做本项目选择。
- 每个大问题的真实提问、实际回答和追问分别落盘；本阶段没有编写未来的 John 回应，也没有产出研究结论或选择。
- 原始 PRD 四文件未修改；本阶段没有派出 TR 助手。
