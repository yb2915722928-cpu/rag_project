# John B 独立 IR 初评

日期：2026-10-15。身份：按用户要求新建的独立 John／产品经理。意图：`readiness`；使用 bmad-agent-pm、bmad-sprint-planning 的 readiness gate。先独立读完当前 PRD、技术补充、技术对话，再检查其引用的 Q1–Q4 决策细节；未读取本轮另一位 John 的发现。上一轮定稿报告只用于识别结论边界，不作为本轮通过证据。

**当前 PRD 及配套决策：CONCERNS。** 主方向、角色、四场景和主要技术路线已经充分记录，但还有 7 处需要最小澄清或补足跨模块契约；其中 B1、B3 含真正产品行为缺口，其余以实施契约为主。

**全实施计划：FAIL。** 当前能进入有边界的架构／契约收口与工作拆分，尚不能把全部需求作为无需发明关键行为的实施交接。此结论不是因为缺少某种 BMAD 文件名；已有技术对话实质承担了一部分架构与 UX 约束，但以下触发场景仍存在多个合理且行为不同的实现。

本轮不要求换栈、不要求先取得收费账号、不降低 K=5 或四场景验收、不生成 sprint-status，不编码或部署。未测得的 API 质量、资源峰值、延迟和费用继续保留未知。

## 材料盘点与结论边界

- 主需求是 [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:15)。[addendum.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:98) 和 [technical-decisions-dialogue.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:26) 实质记录主架构、鉴权、任务、索引、前端及部署决策，不能当成“没有架构”。
- Q1–Q4 的 answer／evidence／followup-answer 包含比汇总更精确的契约。例如，多库 embedding 不兼容时拒绝，已明确记录于 [Q3 evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/evidence.md:46)，本轮不把它报成未决定。
- 已按内容扫描 planning-artifacts 与仓库根目录。没有真实的 epics／stories 或完整页面交互合同；现有根目录三份材料是开发问题记录、面试理解材料、优化记录，不是实施故事。页面范围和部分状态有实质记录，故不机械要求新写完整 UX 模板。
- [completion-report.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/finalization/completion-report.md:13) 仅宣告产品文档定稿；其末尾明确 UX、架构、故事与产品实现仍属下一阶段。这不等于整份实施计划已通过 IR。

## B1 · High · 请求准入缺少双凭据与选定范围的失败语义

**准确位置：** [PRD FR-3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:145)、[FR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:163)、[FR-9](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:205)；[Q1 followup-answer.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/followup-answer.md:4)。

**触发：** 同一请求携带用户甲的 Cookie 和用户乙的 Bearer；或者持有人可查 A、B，但 key 只有 A，客户端提交 `A+B` 的对比；或者旧页面仍提交已经撤权的 B。现有“认证后归一身份、权限取交集”没有规定双凭据拒绝／渠道优先，也没有规定显式目标不全部合法时整请求失败还是悄悄缩成 A。

**后果：** 两种合理实现会得到不同身份或不同对比对象。静默缩小目标后正常返回，会把“没有实际核验 B”误呈现为证据不足；认证回退也可能绕过较窄凭证。已有默认拒绝和权限复核不自动回答“哪个请求应当被接受”。

**最小修复：** 记录按路由限定认证渠道；双凭据的确定处理规则，禁止失败后回退到更宽身份。对显式空间／库／文档逐项验收，任一越界、失权或不存在时整请求拒绝，不静默删目标；外部错误不泄露未授权目标是否存在。补两类负例即可。

**归类／下一步：** 真正 PRD 行为澄清＋共享准入契约。产品经理可直接澄清；如选择另一策略，应由同一 Mary 解释其产品后果。无需重新 TR，也无需等账号。修复技能：bmad-prd，必要时 bmad-architecture。

## B2 · High · 问答配额的崩溃恢复与同 ID 重试尚未形成可实现的生命周期

**准确位置：** [PRD FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:157)、[FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:247)；[Q3 evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/evidence.md:55)。

**触发：** 23:59 已原子预留，生成成功但持久化／回包前 API 进程退出；次日两客户端同时用原 ID 重试。另一个请求复用该 ID 却更换问题、空间或文档。文档任务有租约与 attempt；同步问答目前没有对应的持久预留回收、执行互斥、请求指纹或成功结果重放规则。

**后果：** 预留可能永久占用；并发重试可能再次执行并结算；ID 被另一 payload 复用时可能错误共享结果或计次。把跨日桶钉在受理日只能决定日期，不能闭合失败后是否再次预留、预留多久、谁允许重执行。

**最小修复：** 记录用户／空间／渠道合适作用域内的幂等 ID 和规范化 payload 指纹；同 ID 不同 payload 冲突、同 ID 并发只允许运行一次；持久 pending／succeeded／failed 与原日期、预留和结算关联。规定过期 pending 的回收条件、失败后同 ID 能否重执行、成功重放须重新鉴权。区分系统重传原 ID与用户显式新请求，不能把 Q3“用户可新请求重试”误读为所有失败都必须换 ID。

**归类／下一步：** 记录不足的跨模块实施契约；FR-4 的计次产品决定保留。Mary TS 或架构收口即可，TR 仅在需引用 PG 事务机制时补，不需要外部供应商支持幂等。实测要求：进程中断、双重试、跨日与指纹冲突。修复技能：bmad-architecture，产品文字由 bmad-prd 同步。

## B3 · High · 容量配额没有定义计量对象、预留与释放边界

**准确位置：** [PRD FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:153)、[FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:177)、[FR-8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:197)；[技术对话文件初值](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:158)。

**触发：** 空间剩余容量只够一个文件，却同时上传两份；满额文档要保旧版并导入替换候选；20 MiB 原件产生更大的原 ZIP、解包图像与向量；资料已逻辑删除但物理清理失败。

**后果：** 不同开发者可分别只计活动原件、全部版本原件，或所有产物，都会自认为符合“容量”。并发检查可超额；删除立即释放逻辑配额却仍占磁盘；容量满后能否替换旧版也没有确定体验。单文件及 ZIP 防护不能替代空间容量口径与全盘保护。

**最小修复：** 明确容量产品单位及纳入／不纳入的资产，候选和历史版本的计入规则；上传原子预留与失败释放、替换的暂存预算、清理失败何时归还。另记录服务器全盘低水位保护与临时／解包／备份空间分开限额，避免产品配额被当成磁盘承诺。具体容量数字在目标机实测后填，当前不需伪造。

**归类／下一步：** 真正 PRD 计量行为澄清＋文件／PG 资源实施契约。Mary 受托 TS 可选最小方案，无需新选栈或真实企业容量。实测包括并发上传、满额替换、超展开和清理失败。修复技能：bmad-prd＋bmad-architecture。

## B4 · Medium · embedding 重建的切换范围与并行写入政策仍不明确

**准确位置：** [技术对话 Q3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:110)、[Q3 evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/evidence.md:46)、[PRD FR-4 配置变更](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:155)。

**触发：** 平台改 embedding 配置，A 库重建完成、B 尚未完成；期间上传／替换文档。已有“多库不一致应拒绝”和“候选 ready 后切换”是有效决定，但未指明活动配置／切换以全平台、空间还是库为单位，新资料按哪个配置处理，以及重建快照怎样涵盖期间的活动版本变化。

**后果：** 实现者需要自行选择全站停用、逐库可用、双写或冻结写入等不同产品行为；新旧活动配置可在查询入口与 worker 之间脱节。不能只靠记录模型名与维度解决。

**最小修复：** 选一种最小作用域，例如逐库不可变 active index/config 指针、重建中旧索引继续服务；明确重建时新导入／替换允许、排队或拒绝的规则，以及切换前对快照版本变化的检测。沿用已有跨库不兼容整请求拒绝，不要求实现零停机全局双写。

**归类／下一步：** 记录不足的实施／可用性契约，Mary TS／架构补足即可；实际 embedding 型号、维度和费用仍留接入验证。修复技能：bmad-architecture，必要的用户可见状态回写 bmad-prd。

## B5 · Medium · 对比的输入边界与不足结果的最小结构契约未落定

**准确位置：** [PRD FR-12](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:225)、[Q3 evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/evidence.md:51)、[Q3 的 schema 失败规则](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/evidence.md:55)。

**触发：** 客户端提交数百文档×数百条件；或提交空条件、重复对象；或最终零候选，却需要返回可机器处理的逐格“证据不足”。“对象×条件展开子检索”和“schema 检查”已选定，但接受规模、对象／条件标识、四态证据基数及无证据合法输出没有实际定义。

**后果：** K=5 限生成上下文，不限制前置查询放大；整体超时不能替代可预见的输入受理规则。前后端／程序调用者会各自发明条件身份和空证据表现；合法无证据可能被 schema 当失败，或模型结构错误被当不足成功结算。

**最小修复：** 给出可见、可配置的对象数／条件数／文本长度／子检索总量上限及超限整请求拒绝；数值可作为标注初值，不宣称质量能力。补一个版本化最小输入／结果实例：稳定对象与条件 ID、每格四态、允许不足无证据，满足／明确不满足须引用，冲突须双方证据；明确零候选的受控不足路径和结构失败路径不同。无需预先写完所有 API 字段或改变 K=5。

**归类／下一步：** 产品输入范围澄清＋最小 API 契约。John 可作范围决策，Mary TS 核对成本与接口，最终 K=5 对复杂任务的覆盖效果留实测，不能先宣布必然失败。修复技能：bmad-prd＋bmad-architecture。

## B6 · Medium · 校核／修正及来源回看的最小交互仍需要发明

**准确位置：** [PRD FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:175)、[FR-7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:185)、[FR-8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:195)、[FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:249)、[Q4 页面选择](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/answer.md:19)。

**触发：** 替换候选“部分失败、待修正”而旧版继续生效；维护者点校核，究竟允许修改归一文本、只重试，还是另传修正原件？用户打开 DOCX／TXT 的结构引用时，浏览器无稳定物理页，究竟显示哪份受控原文及怎样核验该位置？

**后果：** 团队可能实现一个复杂解析编辑器，也可能只放下载按钮，两者成本和 FR-7 体验差异很大。任务状态、文档可用性和候选状态容易被前端合成一个“处理中”，导致使用者误以为旧版不可查询或候选已生效。

**最小修复：** 一张精简状态／动作矩阵：分别显示当前生效版本、候选与任务，标明哪些角色可看产物、重试、继续核对、知情重交及修正。明确首版“修正”是否仅重新上传修订原件／改元信息并重处理，不默认要求人工编辑解析内容。引用规定 PDF 页预览／缺坐标回退，以及非 PDF 的结构标题＋准确片段＋受控原件下载等最小行为；不用生成完整视觉设计。

**归类／下一步：** 记录不足的 UX／产品操作契约。bmad-ux 或 bmad-prd 可最小收口；供应方实际定位字段留接入验证，不要求自托管 Word 预览或更换 MinerU。

## B7 · Medium · 恢复点之后的撤权与删除是否可能复活，缺少明示边界

**准确位置：** [PRD NFR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:269)、[Q4 备份选择](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:138)、[恢复澄清](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:204)。

**触发：** 备份后发生账号停用、凭证撤销或资料删除，随后生产损坏，从较旧匹配快照恢复。匹配 DB／文件只能恢复备份点状态，不能自动知道备份点后的权限与墓碑。

**后果：** “核验当前权限、删除状态后再恢复服务”可能被错误实现为“备份中引用能打开即通过”，从而重新放行已撤凭证或已删除资料。这里不要求零数据丢失，但必须明确数据丢失和安全恢复的边界。

**最小修复：** 明确可接受恢复点／丢失窗口在首次部署时登记；恢复默认隔离停服，重新核验到期与账号／凭证状态。选择最小的后备份撤权／删除重放或人工核对清单机制；无法确认的主体／资源保持禁止对外访问，获得受控确认后开放。演练包含“备份后撤权／删除再恢复”的样例，不能只用备份前已删对象。

**归类／下一步：** 记录不足的恢复实施契约；Mary TS／架构收口，窗口数字可留部署时定。不是要求增加另一数据库或承诺 RPO=0。修复技能：bmad-architecture，产品边界由 bmad-prd 同步。

## 已尝试反例、目前不另报缺口

- 旧 worker 租约失效后返回、发布与父级删除竞态、清理重试导致复活：Q2 已有 attempt、父级守卫、永久墓碑和幂等清理机制；应做故障测试，不重新要求选型。
- 首次部分可用与不完整替换稿：已明确首次可发布可定位范围、替换稿完整才切换，不能报成同一规则冲突。
- 多库 embedding 不兼容、模型 JSON 失败与非法引用：Q3 已分别选择拒绝、可见整答失败及无自动模型修复；B4／B5 只补剩余边界，不否定已有决定。
- 评估泄漏：PRD 与根目录优化记录合读，已明确开发题调优、配置冻结后验收、暴露记录和另备留出题；不能仅凭“每轮同口径”认定泄漏。需要真实执行证据，不需要再编一套分数。
- 半个月、4C4GB 和复杂解析：没有证据证明可达，也没有证据支持必然不可达。第 9 节已经要求复杂样例先验证；拆分实施时应把格式／图意／资源探针前置于业务完善，避免误把第 8 节业务完成顺序当作风险首次验证顺序。当前不因无账号、无目标机测量而阻止设计，也不把该顺序建议另凑成第 8 个物质问题。

## 对父级 John 的首轮交接

优先闭合 B1、B3 的产品行为，再让同一问题的 Mary 补 B2／B4／B7 所需契约。B5／B6 用一份小型行为与 API 交接表即可解决，不需追求完整模板。每项修复后用上述触发场景定点复核；全部需求仍须映射到有依赖与验收的实施单元，但不要求现在生成 sprint-status。

下一轮只讨论父级 John 的实质反驳和具体修复，保留真实争论；不会因对方引用 final 标签、上一轮 PASS 或“实施时会做”就撤回发现。
