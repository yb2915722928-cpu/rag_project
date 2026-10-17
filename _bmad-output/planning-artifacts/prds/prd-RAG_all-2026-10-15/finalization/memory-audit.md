# PRD 定稿记忆与当前文档调和核对

核对日期：2026-10-15。核对者：Mary（John 委托，只读恢复与调和）。本文只新增核对报告，不修改 PRD、补充、汇总、原始对话或 memlog；不重新研究技术、不编码、不发起访谈。下述行号对应本次读取的修订前快照，供 John 在定稿修订中逐项关闭。

已完整读取 [决策日志](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:1)、[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:1)、[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:1)、[汇总](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/summary.md:1)、[技术选择与真实对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:1)，并核对 [面试准备](/E:/aaa-project/rag/INTERVIEW_PREP.md:3)、[优化记录](/E:/aaa-project/rag/OPTIMIZATION_LOG.md:3)、[开发问题](/E:/aaa-project/rag/DEVELOPMENT_ISSUES.md:3) 的当前状态。为确认失败产品配额是否已经决定，额外仅检索了 Q4 原答及追问的相关段落，没有开展历史源码研究。

## 1. 决定已落地的位置

| 最新有效决定／约束 | 记录位置与调和结果 |
| --- | --- |
| 通用知识库；四场景完整交付；先 RAG 后 Agent；Web 与只读程序 API | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:15)，另见 38、54–59、63–78、152–160、302 行。四场景未缩成文本问答或只交企业查询，SC-4 仍须表格、OCR、图意与定位。 |
| 用户核对方案、技术栈与理解，AI 编码、集成、测试和真实问题记录；约半个月为预期，不承诺日期；面试不现场演示 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:17)，另见 302、316–326 行；[汇总](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/summary.md:13)。没有转为要求用户每日编码，也没有虚构独立编码经历。 |
| Python／FastAPI／PostgreSQL＋pgvector；Vue 3＋TypeScript＋Vite；部分抽取、参考 WeKnora／MaxKB | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:19) 与 [技术补充组合表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:98)。主栈是已选，不再等待用户重选；直接抽取可行性仍未宣称已通过。 |
| 个人仅本人；三类团队角色；逐库授权；创建者负责；平台身份不自动读资料；撤权及凭证交集 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:96)，范围：96–160。角色、负责人、资源范围与平台身份仍分清，Q1 没有改写产品角色。 |
| 生产为 4 核／4 GB Ubuntu；电脑开发调试；API 优先，不依赖电脑常开 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:25)、[汇总](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/summary.md:57)。电脑 16 GB 是用户自报；i7-12700H／RTX 3060 Laptop 6 GB 是已读取结果，没有把 GPU 变为生产依赖。 |
| MinerU 云端 API 上传解析；停止本地 OCR 归因与多引擎对照，不自托管 MinerU | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:23)、[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:137)，范围：137–156；[面试准备](/E:/aaa-project/rag/INTERVIEW_PREP.md:53)，范围：53–61。未将旧 Windows OCR 实验写成 MinerU 比较成绩。 |
| 开发账号与项目运行 API 分开；运行选千问小模型，具体接入按需，费用按需充值；不问固定预算 | [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:14)，范围：14–15；[PRD 待接入项](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:348)。没有把 Plus／Pro 开发账号写成项目 API 已接通。 |
| 最新受托方式：每个 John 大问题新建 Mary；同题 TR、TS、追问找原 Mary；常规选择不再访谈用户 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:32)、[对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:13)、[决策日志](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:88)，范围：88–93。四题均记录原始问题、答复、追问链接，未冒称用户逐项亲选。 |
| Q1：模块化单体；同步 SQLAlchemy 2／psycopg 3／Alembic；短 Session；PG Cookie／Argon2id／用户只读 token hash／统一授权 | [对话总表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:30)，范围：30–33；详见 57–68 行；[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:102)，范围：102–110。外部等待不持连接、Session 不跨线程，网络撤权非全局原子的限制一致。 |
| Q2：lease＋attempt；独立短 Session 心跳；先存云任务 ID；完整候选切换；墓碑；首次部分可用和替换完整性分开 | [对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:80)，范围：80–95；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:170)、[PRD 版本规则](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:184)，范围：184–190。未承诺外部恰好一次或逐页／字节续传。术语和结果未知的产品表述尚需下节最小澄清。 |
| Q3：结构分块／embedding 配置和索引版本；授权精确向量 B0；整请求最终五块；对比固定名次轮转；引用白名单；追问重检索 | [对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:107)，范围：107–121；[PRD K=5 口径](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:269)，范围：269–287。未改金标分母、四场景门槛或以全面拒答替代通过。关键词、重排、ANN 仍是失败触发实验。 |
| Q4：Vue Router／Pinia／Element Plus 自建页面；电脑构建；Compose Nginx／API／worker／PG；受控文件；供应方密钥可恢复加密且主密钥分离；停写备份；JSON＋PG 记录；pytest／PG／Playwright | [对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:133)，范围：133–147；[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:107)，范围：107–110；[汇总](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/summary.md:61)。用户 token hash 与供应方可恢复密文未混淆；离机备份只是方案，未执行上传或自动化。 |
| 12 份仅 AI 拟备测试起点；32 冻结题独立；低并发、连接、文件与时间是可调初值 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:350)，范围：350–352；[对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:141)，另见 145、149–160 行。未冒称客户负载、容量承诺、已测 SLO 或已有真实企业资料。 |
| B0 后逐轮真实优化，保留改善／持平／退步／失败；无实现、成绩、故障或掌握记录则留空 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:273)、[优化记录当前状态](/E:/aaa-project/rag/OPTIMIZATION_LOG.md:5)、[优化记录无实测条目](/E:/aaa-project/rag/OPTIMIZATION_LOG.md:40)、[开发问题当前状态](/E:/aaa-project/rag/DEVELOPMENT_ISSUES.md:5)、[面试准备当前状态](/E:/aaa-project/rag/INTERVIEW_PREP.md:7)。三份当前状态一致，没有预填成绩或用户掌握。 |

## 2. 被后续覆盖的历史

这些是时间顺序记录，不应删除历史或重新提出已关闭选择。

| 早期记录 | 当前有效覆盖与处理 |
| --- | --- |
| 现场演示假设；逐题 Coaching | [决策日志](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:14) 由 16 行明确覆盖；18、65 行访谈流程由 87–88 行最新授权覆盖。现行 PRD 17、32、342 行正确。 |
| 无 GPU、口述 CPU；两机部署未定 | [决策日志](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:67) 由 70、85 行覆盖；现行 PRD 25 行及技术补充 11 行明确修正，不把 16 GB 自报当作本机实测。 |
| 数据库、前端、任务仍候选；电脑 Milvus 作为主路线待评估 | [决策日志](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:72)，范围：72–80；由 78、79、80 行分别确认，现行 PRD 19–21、25 行一致。电脑 Milvus 是后续可选对照，不是生产依赖。 |
| 普通内容本地、OCR／图意按需 API 的第 6.5 节建议；本地 OCR 归因 | [决策日志](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:82)，范围：82–86；86 行用户决定与技术补充 141 行明确覆盖。TXT／Markdown 直接读取仍是应用职责，不等于恢复本地 OCR。 |
| 每个 TR／TS／追问分别建新 Mary 的解释 | [决策日志](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:87) 由 88 行明确覆盖，现行对话 13 行一致。 |
| 配套异步 ORM 候选、关键词／融合／重排建议 | Q1 同步选择见 [对话收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:68)；优化按失败选实验见 [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:131)。技术补充局部遗留措辞见下一节。 |

## 3. 需修正的冲突与最小澄清

以下由 John 在既有受托授权内处理即可。它们不要求重选技术或重开用户访谈。

| 编号 | 准确位置及影响 | 最小修订建议／已有依据 |
| --- | --- | --- |
| MA-01：候选版本术语 | [PRD 术语](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:89) 把文档版本定义为“一次成功生效”，但 [FR-8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:186) 和 Q2 已有未生效候选版本。这是同一文档内部的术语冲突。 | 文档版本改为一次不可变资料内容与对应产物的标识，可处于候选或已生效状态；仅活动版本参加新检索，历史版本只供仍有权者核验。沿用 [Q2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:85)，范围：85–87，不新增版本选择器。 |
| MA-02：定位规则未承接 | [FR-7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:176) 泛称“章节和页面定位”，与支持 DOCX 的 FR-6 组合后可能被理解为 DOCX 也必须有可靠物理页码。 | 在 FR-7 补一句：PDF 页从 1 起；DOCX 无可靠物理页时使用章节／段／表／图等结构定位，不编造页码。该规则已由 [Q2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:85) 决定，不是新增能力。 |
| MA-03：外部结果未知状态 | [FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:166) 状态清单没有“待核对”；[FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:238) 只写继续或可重试，未承接“未知时不可盲重交”。可能导致页面提供会重复付费的重新上传按钮，或永久显示处理中。 | 增加可识别的“上游结果未知／待核对”及请求标识，先查原云任务；仍不能判定时保留可见状态和原因。有权维护者可查询原任务、核查并在结果明确后继续或安全重试；未知未解除不得以普通重试重新提交。程序 API 仍只返回持有人本人且在 scope 内的任务状态，不获得处理写权限。依据 [Q2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:84) 与 [Q4 追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:145)。保留自动恢复路线，不引入逐份人工审批。 |
| MA-04：局部旧候选口径 | [技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:105) 仍称“具体分块／检索编排由后续问题细化”，但 Q3 已闭环；114 行仍叫“两条候选调用链”，117 行把“查询向量化及关键词处理”连为默认链；127 行仍以“候选方案”引导异步 SQLAlchemy 资料。读者可能误判已选方案仍待答，或误把关键词列为 B0 必做。 | 105 行指向已完成 Q3；6.3 改为当前已选链路或明确标为旧候选背景。当前问答链明确精确向量 B0，关键词／重排等按失败再实验。127 行将异步链接明确归为被 Q1 覆盖的历史参考，或仅引用已选同步 Session 来源。不改实际已选组件。 |
| MA-05：恢复验收承接不足 | [NFR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:258) 只要求干净启动及目标机核心流程；停写一致备份及恢复已由 [Q4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:138) 决定，但尚未进入主 PRD 可检验边界。 | NFR-5 或工程交付证据补一条恢复演练：停写形成一致备份，在干净环境使用数据库／受控文件／配置／密文及对应分离主密钥恢复，核验关联、文件哈希、授权和未完成任务；证据形成前不称“可恢复”。不搬入完整部署参数，也不声称离机上传或定时备份已执行。 |

## 4. 真正需要定稿前收口的产品规则

**MA-06：失败请求是否扣每日问答次数尚未定义。** [FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:150)、[FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:238) 已定义同一请求幂等计次、真实调用成本逐次累计；但依赖失败、超时、格式校验失败、输出前失权等可见失败是否消耗每日问答次数没有明确。[待补充表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:350) 将“失败计数”一起留为有效配置，无法给剩余次数验收确定的预期。

Q4 [原答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/answer.md:26)，范围：26–27，以及 [追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/followup-answer.md:1) 也只覆盖真实成本、初值及未知状态，不足以反推已选择了哪种产品失败计次政策。

建议由 John 按现有 Mary 受托授权采用一个明确且可检验的首版规则：认证／权限／参数／配额／过载等受理前拒绝不扣次数；执行请求按逻辑请求标识先预占，成功交付完整问答或对比才结算一次，最终失败释放预占；同标识重试不得重复结算，恢复和并发情况下也遵循原子预占及幂等。供应方已实际产生的调用、Token 和费用始终逐次累计，不能随产品配额释放而抹掉。该建议是本次最小行为补全，尚非本报告擅自认定的既有用户选择；John 收口并写入 FR-4／FR-15 即可，无需用户提供账号或新偏好。

此外，MA-03 的未知状态及有权操作需在定稿时承接既有 Q2 决定；其余 MA-01／02／04／05 是既有决定的术语、呈现和验收调和。没有发现需要重选主栈、删除场景或询问用户才能决定的 PRD 阻塞。将已有 status 从 final 改名不构成这些收口工作的完成证据。

## 5. 非阻塞的实施验证交接

| 验证事项 | Owner | 触发条件与完成证据 |
| --- | --- | --- |
| 依赖、镜像、迁移版本与模块来源／许可证边界 | AI 实施 | 首次锁定环境、引入依赖或抽取代码前，记录固定版本、来源、适配边界与最小样例。未验证不称上游模块已可直接使用。 |
| MinerU／千问／embedding 实际账号、凭证、API 协议、限额与计价 | AI 实施；仅确需本人提供账号、访问权或充值决定时请用户补充 | 首次实际接入前核对安全配置与接口，再以支持格式样例验证响应／任务／来源。缺凭证不是 PRD 不能定稿的理由，不重开 OCR 选型。 |
| 目标机 OS 细节、磁盘、剩余资源、Netcatty MCP、HTTPS 证书 | AI 实施；用户提供确需本人授予的访问 | 首次环境核查／部署接入时登记，按 4 核／4 GB Ubuntu 生产目标验证。不把电脑 GPU 或常驻电脑作为替代生产前提。 |
| 文件／页数／批量、超时、队列、连接、并发与存储配额有效值 | AI 实施 | 首个可运行配置与 API 契约前登记，结合云端硬限制和目标机验证；Q4 数字只是可调初值。产品失败计次政策先按 MA-06 收口，不能仅以可调数值代替。 |
| 解析结构、图意、扫描、简单跨页表格及引用定位质量 | AI 实施 | 接入最小样例后核验 FR-7；真实缺口才触发补充图意能力选择。选 MinerU 不等于质量通过，不能省略原定格式或 SC-4。 |
| 授权、候选切换、迟到 attempt、墓碑、未知结果与恢复 | AI 实施 | 相应功能实现时，用真实 PG 和故障注入验证；页面与程序 API 保持既定动作边界，不能以研究记录代替测试。 |
| 停写备份、分离主密钥与恢复 | AI 实施 | 首次部署和恢复演练时保留命令、备份清单、对应版本及核验结果；实施前只是已选方案，不声称已上传离机副本。 |
| 四场景资料、实际负载与 32 题 | AI 实施 | 首次准备样例时核验来源并统计文档／页／字／块／字节；12 份是测试起点，不是用户真实企业负载。开发题与冻结验收题分离。 |
| 资源、延迟、真实用量及费用绝对门槛 | AI 实施 | 固定环境与首次 B0 后、优化比较前登记门槛；保存全部失败和未知费用，不以缺实测阻止产品定稿，也不提前宣布项目完成。 |
| 用户理解、个人参与、真实故障与优化收益 | AI 实施并与用户阶段核对 | 工作和练习实际发生后更新根目录三份记录；文档完成／代码完成不等于用户已掌握。空表不是零分，未发生故障不编造条目。 |

结论：最新用户决定与 Q1–Q4 主要选择均有落地记录；主栈、角色、四场景、B0／K=5、API 优先和真实证据边界一致。定稿前按 MA-01 至 MA-06 完成最小文字调和和失败计次收口即可，未发现必须追加用户访谈的事项。
