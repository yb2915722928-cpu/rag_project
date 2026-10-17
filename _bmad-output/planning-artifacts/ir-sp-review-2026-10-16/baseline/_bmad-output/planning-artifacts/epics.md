---
title: RAG_all Epics 与 Stories
status: final
created: 2026-10-16
updated: 2026-10-16
author: John
workflow: bmad-create-epics-and-stories
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
inputDocuments:
  - prds/prd-RAG_all-2026-10-15/prd.md
  - prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md
  - prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md
  - architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md
  - architecture/architecture-RAG_all-2026-10-16/shared-contracts.md
  - architecture/architecture-RAG_all-2026-10-16/runtime-operations.md
  - architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md
  - architecture/architecture-RAG_all-2026-10-16/technology-evidence.md
  - ux-designs/ux-RAG_all-2026-10-16/DESIGN.md
  - ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md
  - ux-designs/ux-RAG_all-2026-10-16/page-contracts.md
  - ux-designs/ux-RAG_all-2026-10-16/acceptance.md
  - implementation-readiness.md
implementation_started: false
runtime_acceptance: not-executed
---

# RAG_all — Epics 与 Stories

## 范围、权威与使用方式

本轮只将现行 S0/P0/F0/S1–S7 细化为开发可领取的故事；不重选业务、技术栈、角色、状态、限流算法或质量口径。最新[IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md:1)的 PASS 仅是规划可实施判断。下列故事全部待实现，四项修复的运行门全部未执行，不生成冲刺状态、工时或交付日期。

业务真源为[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:1)、[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:1)与[切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:1)；跨模块技术由[架构主干](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1)、[共享契约 C1–C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:1)与[运行契约 R1–R8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:1)约束。组件视觉遵循[DESIGN](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md:1)，行为遵循[EXPERIENCE](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md:1)、[逐页 IA/G](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:1)与[原 AC-01–23](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:1)。原[需求—架构追踪](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md:1)继续有效；本文件增加到 Story 的最后一跳。精确版本与 starter 继承[技术证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:1)，实施时核依赖，不借 CE 重选。

用户明确授权“完成草稿、两位全新上下文只读复核、核实修订并定稿”，因此按 CE 四步顺序连续完成，不逐步请求 C。输出语言中文；项目 RAG_all。每条来源与正向分派详见[Story双向追踪](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/story-traceability.md:1)，独立复核及主John处置见[复核记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/review-record.md:1)。

## Requirements Inventory

以下为可追踪摘要，所有被引用原条款及正反例都是强制验收，不以摘要取代细则。

### Functional Requirements

| ID | 可检验要求 |
| --- | --- |
| FR-1 | 个人空间仅本人；同账号跨团队角色分别生效；普通用户不能建团队。 |
| FR-2 | 平台建团队与有效唯一所有者；站内邀请接受才入队；转让、退出、停用先交接；降级/移除职责接管；解散先阻断访问。 |
| FR-3 | 角色决定动作、逐库授权决定范围；创建者自动负责；非负责维护者不能管授权/删整库；撤负责人权同步接管且不能自恢复；派发/输出/回看重核当前权。 |
| FR-4 | 平台与业务读取分离；账号、模型/存储验证、原件容量及上海日问答配额；不可变 profile、显式重建；三账独立、原子预留/唯一结算、幂等及失败成本保留。 |
| FR-5 | 本人单空间/明确库/只读动作/到期凭证；密钥仅创建显示；Cookie+Bearer 整拒；全目标整拒；operation 继承原动作、citation 独立许可；无写 API。 |
| FR-6 | 五类格式逐文件上传及有限可见限制；同上传 ID/真实 hash 重传；未 PUT/半传有期限；程序校核、可靠范围 partial 与明确失败。 |
| FR-7 | 规则及简单跨页表格、扫描 OCR、真正图意；PDF 物理页/可信 bbox、非 PDF 实际结构；原件/提取/失败范围最小对照；修正形成新候选。 |
| FR-8 | 完整替换原子生效、失败保旧版、迟到不覆盖；历史只供引用核验；删除先阻访问再清理，清理失败不复活/不早释放容量。 |
| FR-9 | 单空间显式授权 B0、全请求 K≤5、完整答案一次返回；不足/澄清/冲突与失败区分；完整 token 预算、catalog 等于实见、注入不越权。 |
| FR-10 | SC-1 版本/环境/日志、候选原因及顺序检查逐步引用；缺条件澄清，不执行命令、不声称已修复。 |
| FR-11 | SC-2 有据流程/材料/条件/负责人；缺负责人明示，制度冲突并列双方来源。 |
| FR-12 | SC-3 固定文档版本、完整对象×条件四态矩阵；2–4对象/1–6条件等有限配置、最多24路串行、证据语义及 compact128；非法/缺格整答失败。 |
| FR-13 | SC-4 型号/版本/故障码/参数、表/OCR/图意组合，保数值单位条件及可靠来源，不拼不兼容参数。 |
| FR-14 | Web 管理与四场景、同空间会话/父轮次/单未终结轮次、历史/来源/反馈；账号/登录实例/空间/epoch/代次隔离迟到回包，原操作恢复。 |
| FR-15 | 上传/任务/清理有界恢复、原2h期限不刷新；unknown 不盲重交；原任务核对、新本地继续、知情解析重交分离；已受理库任务不随上传者降级自动取消。 |
| FR-16 | 管理审计、安全变更同事务稳定 ID 台账、调用/成本与阶段观测、本人答案反馈；普通日志不含正文秘密，失败及 unknown 不消失。 |

### NonFunctional Requirements

| ID | 必须保持的验证边界 |
| --- | --- |
| NFR-1 | 全入口统一当前授权；独立权限专项全通过，不能用质量分抵消。 |
| NFR-2 | 真实 PG 条件更新及故障恢复不重复有效版本/计账；删除先断访问。 |
| NFR-3 | request/operation/job/call 安全关联及阶段耗时、依赖错误、用量；日志无正文秘密。 |
| NFR-4 | 固定环境/数据/配置/并发测 median、导入耗时、成功率、调用/费用及4C4GB峰值；样本不足20不报有代表性P95；基线后、优化前登记绝对目标。 |
| NFR-5 | 干净环境及目标 Ubuntu 验证；一致备份、独立受托信任、旧身份失效、两次新 epoch 与逐范围恢复，不把启动视为恢复通过。 |
| NFR-6 | 公开/获许可或明确模拟脱敏资料；密钥不入仓库/普通日志/文档样例；测试证据与业务资料分离。 |

### Additional Requirements

- AR-01：八模块唯一写者、向内依赖、同 application 用例；四服务 gateway/API/worker/PG，PG 持久任务；不新增队列或 Agent 编排。
- AR-02：AD-3/C4 的全局锁序、短同步 Session、同 UoW 效果；按每故事需要增量迁移，不预建全系统表。真实 PG/pgvector 不用 SQLite 替代。
- AR-03：独立持久 epoch、配置矛盾隔离；先持久 call intent、一次 grant、unknown 及迟到只补账；OS/网络等待不持 PG 事务。
- AR-04：R01 的 send_open→监督停发证明→随后 DB 上界→完整 W；跨秒/分钟、读钟后及部分写暂停、失联/崩溃/重启/旧包恢复全部在任何真实外发前验。
- AR-05：doc_active_job 与 external_async_task 两个全系统独立 gate 各默认4/允许1–4；全部账号合计，本机重阶段1；HTTP/task/窗口许可分维领取释放，原2h含排队/等待不刷新。
- AR-06：writer 自持稳定 Linux 生命周期锁、唯一 prefix/资产预算、fence→停写→EX锁→删除核验→cleaned/唯一释放；不以 PID/线程引用或 unlink 自证。
- AR-07：S2 首交 profile/vector(D)/generation/revision、块/向量/来源及原子发布；S3 复用查询；S6 才扩重建管理/变维维护。
- AR-08：H/B/M、严格有限 schema/错误/生成子契约，后端统一导出 TS/OpenAPI；完整输入不暗裁、完整输出 R 与 catalog 实见一致。
- AR-09：S1 首次安全变更同事务台账及独立导出能力；S6 独立受托、gap/已知拒绝优先、两次随机新 epoch 和旧凭据/任务拒绝。
- AR-10：P0 真凭据/合法样例/官方实际限制逐用途取证；格式/来源/embedding、预算、图意、资源分别守后续门；假件不代真实能力。
- AR-11：F0 首次调优前冻结32题/资料版本hash/原金标/判定/时间访问记录，开发题隔离；S7 不选易过题、不改分母。
- AR-12：S0 Story 1.1 使用已定 create-vue 3.23.0 starter（TS/Router/Pinia）及技术证据中的精确 seed，锁实际依赖/镜像 digest 并验证组合、来源许可证与改造边界。

### UX Design Requirements

| ID | 具体工作与可测行为 |
| --- | --- |
| UX-DR01 | 绑定 DESIGN 浅色语义 tokens、系统字体、字号/行高/间距/边框/焦点；文字4.5:1、大字3:1、必要边界/焦点3:1。 |
| UX-DR02 | 应用框架：持续标身份/空间；224导航、抽屉及私有视图代次；pagehide 清/遮蔽、pageshow 重核全部依赖再取数。 |
| UX-DR03 | 范围选择器：单空间显式清单、全部展开、摘要可核；空/重复/不可用整拒。 |
| UX-DR04 | 资料表格：有界分页/白名单排序/筛选，生效/候选/任务三组，另列索引与清理，不隐藏旧版可用性。 |
| UX-DR05 | 导入表单：实际限制/容量、逐文件受理、元信息初值及原上传 ID/期限恢复。 |
| UX-DR06 | 处理状态条：五投影、真实阶段/截止/失败范围、allowed_actions；unknown 不画伪百分比。 |
| UX-DR07 | 来源查看器：版本/hash/真实页或结构、原件与提取标签、可信框/无框回退；受控安全下载/PNG-JPEG预览及来源返回焦点。 |
| UX-DR08 | 问题输入区：SC 原名和字段、默认企业仅分组；纯检索与问答分动词；保完整输入及原操作恢复。 |
| UX-DR09 | 答案卡：完整四 outcome 一次显示，事实/单位/适用条件/双方证据就近，无失败草稿。 |
| UX-DR10 | 对比矩阵：完整对象×条件、四态文字/理由/证据、原顺序和版本，局部横滚及格表头朗读/返回焦点。 |
| UX-DR11 | 反馈条：错误/缺依据/引用问题必选一项，绑定本人可读答案，失败保输入、不新生成。 |
| UX-DR12 | 凭证面板：显式空间/库/动作/未来期限，明文仅创建一次，丢回包先读元信息/明确撤销重建。 |
| UX-DR13 | 用量面板：原件容量/产品次数/实际调用费用三组，预留/清理中/上海原日桶/unknown 分清。 |
| UX-DR14 | 管理表单：角色/范围分开，当前事实、不乐观安全成功；平台不提供正文/代登录。 |
| UX-DR15 | 确认对话框：安全焦点/圈定 Tab/Esc 返回；整库/解散/转让输入可见名称；解析重交知情复选默认未勾。 |
| UX-DR16 | 状态反馈：空/加载/错误/无权/离线/待核对/隔离均可辨，错误摘要关联字段，轮询不抢焦点、不用0替unknown。 |
| UX-DR17 | 登录表单：真实标签/粘贴/密码管理器、首次无Cookie可达；精确 Origin+JSON+固定头，后续认证写继续绑定token。 |
| UX-DR18 | 每新页面覆盖冷加载/成功空态/读取失败/权限变化/离线恢复/焦点，GET 无付费副作用。 |
| UX-DR19 | 1440/1280/1024/767/375 CSS px及200%缩放实测；≥1440主区min640+来源400，<1200抽屉/资料纵排，<768单列/tabs/矩阵局部横滚。 |
| UX-DR20 | 键盘/辅助技术可完成合法全流程，标签/表头/错误/状态播报可读；细指针控件32、粗指针视觉40/目标44/间距8；减少动效。 |
| UX-DR21 | R03：所有私有成功/错误no-store、gateway禁缓存，无验证器/304，If-*重授权；S1设施/S2资源/S3历史各在开放前真实浏览器验证。 |
| UX-DR22 | R04：原件准确白名单MIME+attachment+安全有界fallback/filename*+nosniff；仅已核PNG/JPEG inline，文本/MD安全渲染、不执行/不抓远程资源。 |

### FR Coverage Map

| FR | Epic（首次主责；后续增量） |
| --- | --- |
| FR-1 | E3 身份/空间/角色 |
| FR-2 | E3 邀请/转让/接管 |
| FR-3 | E3 库范围；E4/E5 当前资源/输出检查 |
| FR-4 | E1/E2 调用保护；E3 准入/配额；E5 计次；E8 重建/运行恢复 |
| FR-5 | E3 凭证；E5 只读能力；E6 比较 API |
| FR-6 | E2 格式证据；E3 意图/预留；E4 上传处理 |
| FR-7 | E2 探路；E4 最小来源/索引；E7 复杂质量 |
| FR-8 | E4 替换/删除/历史源；E5 历史答案；E8 索引/恢复 |
| FR-9 | E5 授权B0/预算/完整回答；E6/E7 场景增量 |
| FR-10 | E6 排障 |
| FR-11 | E5 企业知识 |
| FR-12 | E6 完整比较 |
| FR-13 | E7 复杂手册 |
| FR-14 | E3 基础归属；E4 资料/来源；E5 会话；E6/E7 场景 |
| FR-15 | E1 隔离执行；E4 恢复三动作；E5 操作恢复；E8 可信恢复 |
| FR-16 | E1 观测/账；E3 首日起安全台账；E5 反馈；E8 运行；E9 工程证据 |

## Epic List

| Epic | 原切片 | 可独立验收的结果 | FR 范围 |
| --- | --- | --- | --- |
| E1 安全开始开发与受控调用 | S0 | 实施者无供应方账号也能启动真实PG骨架，证明隔离、调用、限流与资产守卫；不给业务入口假成绩 | FR-4/15/16，NFR-2/3/5/6 |
| E2 用真实证据确认外部能力 | P0 | 接入者取得分别可消费的格式/来源/维度、预算、图意、限额/资源证据，缺口明确阻断相应能力 | FR-4/6/7/9/13/15/16 |
| E3 用户能安全进入并管理授权范围 | S1 | 用户登录、选空间、协作授权、管理本人凭证/用量，平台分权；准入设施可独立测试 | FR-1/2/3/4/5/6/14/16 |
| E4 维护者完成资料全生命周期并核查来源 | S2 | 无问答页面也能导入、查看原件/提取/索引、替换、删除和恢复任务 | FR-3/4/6/7/8/14/15/16 |
| E5 员工获得有据企业答案并安全恢复历史 | S3 | SC-2 完整查询/答案/引用/会话/反馈与只读API，原操作恢复不重复计费 | FR-3/4/5/8/9/11/14/15/16 |
| E6 支持人员排障与售前逐格核验 | S4 | SC-1 有条件排障、SC-3 全格四态比较，Web/API 一致 | FR-5/9/10/12/14 |
| E7 工程师核验复杂手册事实 | S5 | SC-4 表格/OCR/真正图意有可靠依据、型号/单位/条件完整 | FR-7/9/13/14 |
| E8 维护者安全变更索引并在目标机可信运行 | S6 | 有权维护者重建/显式变维；部署方验证4C4GB、TLS、一致备份与独立可信恢复 | FR-3/4/8/15/16，全部NFR |
| E9 用冻结验收与真实工程证据判定完成 | F0/S7 | 冻结防污染、开发题实验、原SM全门与交付/理解证据完整 | 全部FR/NFR/SM |

E1/E2是原切片强制的工程/风险使能，不拆成数据库/API/前端横向 Epic。E3–E8每个故事包含所需数据、用例、入口和对应界面；共享模块的后续增量由原唯一写者端口扩展。E4最小来源和E7复杂质量、E4增量索引和E8重建、E1骨架和E8真实恢复的边界已由现行切片固定，保留这些风险门而不合并成不可验收的大故事。

## 执行顺序与开放门

业务主线保持 **E1/S0 → E3/S1 → E4/S2 → E5/S3 → E6/S4 → E7/S5 → E8/S6 → E9/S7**。E2/P0在S0全部本地硬门通过、合法样例/凭据具备后尽早开展，可与E3并行；不依赖S1身份开放，不向业务用户暴露探路入口。P0仅消费S0隔离工具，不依赖S2/S3/S5页面。

P0各真实调用先核对应官方共额域/维度/动作与有限配置，首次小调用也不能先发后核；再形成格式/来源/embedding（S2门）、完整预算（S3门）、真图意（S5门）及池1/4/目标资源证据。账号/环境缺失可做独立S0/S1工作；只开放已验证能力和档位，未证4不开4，不将未证目标资源写成已通过。

F0是Story 9.1的**条件前置**，可独立前移到任意首次调优之前，不受Epic编号或S6约束；此前未调优时才在S7首步执行。普通功能实现不一概算调优，P0开发题不得再冒充未暴露冻结题。S7运行成绩从不作为S0前置。

| 门 | 必须完成/证据 | 停止点 |
| --- | --- | --- |
| S0→任意真实外发 | E1全部本地PG/Linux/假件、R01及恢复/资产守卫通过；逐能力真实限制已核 | 任一未过禁止真实外发，包括探路/接入验证 |
| S1身份入口 | R02首次登录、认证写token、R03公共设施；安全变更台账与授权/账反例 | 不开放身份/业务写入口 |
| S2资源入口 | 对应P0真实格式/来源/embedding；R03资源+R04媒体；索引/来源首次交付 | 不以S3/S5未来能力补当期；未过不开放资源 |
| S3问答/历史入口 | P0完整预算，R03问答/重放/历史真实浏览器负例 | 非零预算未证不生成；入口负例未过不开放 |
| S5/SC-4 | P0真图意与表/OCR专项及复杂质量 | 缺图意阻本片/整期，不降SM |
| S6上线 | 目标机、真实并存资源、TLS/秘密、部署方确认备份窗口、两次新epoch可信恢复 | 无证不上线 |
| F0/S7完成 | 首次调优前冻结，原SM-1–7全门、失败/费用unknown/独立权限分母完整 | 任一原门未过不称整期完成 |

## 故事共同完成条件

每个故事只新增自身所需实体/迁移，以先前已验故事为基础；“依赖”表示完成验收后方可使用，不能用仅有代码或旧PASS替代。Epic编号是归类，不把E2排在E3前形成全P0串行屏障。相同Epic内只依赖更早故事；F0例外前移已显式列出。一次开发上下文处理一条故事，运行资源不足则记阻塞，不把多个故事合成一次大任务。

每条故事的 AC 编号为 Story ID-ACn，按下列条目顺序计。故事引用的原UX AC是来源及持续约束；本条必须完整执行[验收子例分派](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/acceptance-allocation.md:1)分配给它的正反子例及相关条款。跨故事原AC按子例逐步闭合，不能把未来页面或演练的整组AC作为本条完成前置，也不能将未分配/未执行子例写成已通过。切片开放门必须汇总该片应完成的全部子例，9.4再全流程复验原AC-01–23及原SM，保留原分母和四修复最早门。

所有Web故事同时验**自身新增/修改页面**的UX-DR01/18/19/20、G-01–G-12、AC-21/23子例：真实键盘/辅助技术、1440/1280/1024/767/375与200%截图、对比度/触控/焦点、冷加载/空/失败/失权/离线、无秘密/正文持久缓存；尚无某表面的早期故事不负责其未来交互。组件按首次故事落地、后续复用并验证本页，不留统一“最后美化”故事。

每条运行证据记录版本/环境、输入与当前限制、主体/范围、动作、预期/实际、HTTP及DB/资产/调用副作用、关联ID、脱敏原始证据和通过/失败/阻塞；真实PG、Linux、浏览器、供应方、目标机分别标来源。失败与unknown原样保留。默认状态全部未执行；文档静态通过不改变运行状态。

## Epic 1：安全开始开发与受控调用（S0）

实施者能在无供应方凭据时独立证明基础守卫。主责FR-4/15/16、NFR-2/3/5/6；AR-01–06/12。仅对隔离假件开放的维护测试入口不赋业务权限。

### Story 1.1：启动可重建的模块化项目

As a 实施者，I want 在干净环境启动锁定的四服务骨架，So that 后续功能使用相同可复现基线。

**依赖：** 无。**来源：** NFR-3/5/6；AR-01/02/12；AD-1/2/3/5/13；C1/C2；运行R4；技术证据E1–E3。

**Acceptance Criteria:**

- **Given** 空项目与现行技术seed，**When** 初始化后端及create-vue 3.23.0的TS/Router/Pinia模板，**Then** 锁实际依赖、peer和镜像digest，四服务可构建/启动/停止；不复制React整栈模板，不预建后续全部业务表。
- **Given** 真实PG/pgvector与短UoW示例，**When** 迁移/回滚和制造事务失败，**Then** 版本、扩展及原子回滚可核；领域不导入框架/ORM，仓储不commit，配置/秘密不入日志。D未证前仅验扩展与隔离测试向量，不建立正式生产vector(D)。
- **Given** 上游抽取或样例拟引入，**When** 登记来源/许可证/依赖边界/最小样例与改造，**Then** 未核验内容不当已复用；构建记录可在干净Linux环境复现。
- **Given** 共同contracts与有界HTTP测试入口，**When** 导出OpenAPI/JSON Schema/TS及正负样例，**Then** C1标量码点/非BMP/序列化、C2公共包/错误与实施契约§3.5的H字节/深度/节点/重复键/编码/未知字段边界一致，按需增量schema而非手写平行类型；1MiB JSON不误套原件PUT，未认证不回私有operation ID。

### Story 1.2：隔离执行并保存每次调用事实

As a 接入实施者，I want 用可控假件经过epoch与单call派发，So that 超时或崩溃不会静默重发或丢成本。

**依赖：** 1.1。**来源：** FR-4/15/16；NFR-2/3/5/6；AR-03；AD-3/7/8/13；C4/C5；实施契约§2.5；运行R1/R2。

**Acceptance Criteria:**

- **Given** 独立持久epoch与DB镜像，**When** 普通重启/缺失/矛盾或旧attempt回报，**Then** 重启不换epoch，矛盾隔离且失效执行者不能提交业务；模型/解析/embedding/图意端口仅用显式假件，不实际外发。
- **Given** 有界受监督child及有限IPC，**When** 在prepared前后、may_have_sent后、响应前后注入崩溃/超时，**Then** 原call只获一次grant、不恢复重发，未知保留NULL+unknown；child无业务DB/主密钥、不自主串阶段，secret不入argv/日志。
- **Given** 配置端点/上游签名URL、redirect和DNS变化假件，**When** 准备出网，**Then** S0即交付C5 EgressTarget：仅HTTPS、有限准确host/port、拒userinfo/fragment与私网/回环/link-local/保留/metadata全部A/AAAA，连接绑定已核公共IP并保持TLS主机校验；禁止重解析绕过/自动redirect，API Authorization不转交下载host，URL/secret不写日志。任何未过目标守卫的真实调用均阻断。
- **Given** 业务已终结/旧epoch与可信迟到usage，**When** 重复或冲突补账，**Then** 仅按call幂等补事实/留冲突，不改业务、产品次数、会话或许可；PG真实负例证明锁序，无网络/进程等待占事务。

### Story 1.3：证明共享限流与双任务gate不会提前退额

As a 接入实施者，I want 在可暂停传输下验证C8，So that 迟发、unknown和重启仍被共享额度覆盖。

**依赖：** 1.2。**来源：** FR-4/15/16；NFR-1/2/4/6；AR-04/05；AD-7/11/14；C8；运行R1/R2/R7-R01；UX补充R01。

**Acceptance Criteria:**

- **Given** 真实PG、RPS=1/s和完整分钟TPM假件，**When** A领grant后跨秒/分钟暂停、读钟后暂停或部分写暂停，B另一槽请求，**Then** A持续send_open全量计占，B不超额；不因send-by/lease/业务终态/usage退额。
- **Given** 正常退出、child失联仍活、controller在may_have_sent/IPC/seal前后崩溃、kill未确认，**When** 封口/重复封口/重启或恢复旧包，**Then** 只有证明本call全部sender/后代停发、FD/IPC关闭及旧grant销毁后才取随后DB上界、保留完整W；缺证明保持阻断，跳钟异常不清额。
- **Given** 两本地gate各1档/4档及账号总池/用途子池，**When** 假件满池submit→accepted→poll→terminal、公平轮转/取消/unknown/恢复，**Then** queued不占job、job终态仅还job、unknown task不还task；本地gate→pool→call→组件同UoW一次领还，poll不新增task但过适用HTTP/RPS，窗口/HTTP/task独立终结。
- **Given** 4档远端等待，**When** 轮转到期阶段，**Then** 四远端假件可重叠且本机重阶段≤1、pending不持Session/正文/常驻child、due poll不饥饿；原2h含排队/等待/重试不刷新。此成绩不证明真实账号或4GB。

### Story 1.4：在真实停写后清理资产并释放预算

As a 维护实施者，I want 资产具有唯一归属和可验证停写屏障，So that 清理不会删除活跃文件或虚报回收。

**依赖：** 1.2。**来源：** FR-4/8/15；NFR-2/5/6；AR-06；AD-6/7/8；C4；实施契约§2.6；运行R2/R3/R6。

**Acceptance Criteria:**

- **Given** 独立attempt/stage前缀和真实Linux共卷锁，**When** writer写入或源读取，**Then** 实际child自持稳定SH至FD关闭，先登记prefix/预算再接字节；多prefix稳定排序，不持PG事务等OS锁。
- **Given** TERM/KILL失败、存活后代/FD、C5删除成功但C6提交失败，**When** 清理/重试，**Then** 依次fence→事务外停写→EX→复核→删核→cleaned/唯一账转换；未证停写或提交失败继续占用/blocked，不复用槽或旧prefix。
- **Given** 上传代理/框架、ZIP/解包/图片/备份及PG余量预算，**When** 流式超界、路径逃逸/符号链接或低水位，**Then** 有界拒绝对应新写/付费、保留合法读/受控清理；不产生未登记暂存，不早删历史来源腾空间。

### Story 1.5：签署S0本地门并交付隔离探路工具

As a 接入实施者，I want 可执行的S0资格报告与隔离命令，So that 真实探路有明确可核前置。

**依赖：** 1.3、1.4。**来源：** FR-4/15/16；NFR-2/3/5/6；AR-10；AD-14；运行R7-S0；最新IR。

**Acceptance Criteria:**

- **Given** 1.1–1.4完整产物，**When** 在干净Linux+真实PG运行本地验收，**Then** 留启动/迁移、epoch、调用/迟到账、C8-R01、双gate、writer/预算/清理的完整正负例；任一失败不出具可外发资格。
- **Given** 无凭据/真实限制未核或本地门未过，**When** 调探路/接入验证命令，**Then** 不外发；合格时工具可独立使用维护隔离空间及假业务上下文，不依赖S1/S2页面，不向业务用户开放。

## Epic 2：用真实证据确认外部能力（P0）

接入者按用途取得实际证据。本Epic与E3可并行，各子门独立消费；每次调用均继承S0而不绕过限流/成本/资产控制。主责FR-4/6/7/9/13/15/16，AR-10。

### Story 2.1：核定真实共额域与安全调用配置

As a 接入实施者，I want 在首个真实请求前核官方限制和合法凭据，So that 探路本身也遵守有效边界。

**依赖：** 1.5；合法运行凭据/获许可资料。**来源：** FR-4/15/16；NFR-4/6；AR-05/10；AD-7/14；C8；技术证据E4。

**Acceptance Criteria:**

- **Given** 实际供应方账号/地域/用途及官方协议，**When** 建profile，**Then** 留许可/数据外传条件、submit/poll/download适用的RPS/TPM/HTTP/task维度、有限值/窗口及共额映射；未知项保持禁用，不用开发AI账号或换key复制额度。
- **Given** 已核动作与S0门通过，**When** 最小受控请求/SDK检查，**Then** 实际无暗重试/重定向，每call有账/permit/停发证明；HTTP响应不释放远端unknown task，保留本地发送/可得远端结果/429，不承诺远端到达窗口。
- **Given** 实际poll与满池限制不兼容，**When** 核正常异步闭环，**Then** 必须找到并证明合法核对通道/官方有限上界（含最晚到达界）；无证不启该异步组合，未知费用不填零。

### Story 2.2：验证五格式来源与embedding维度

As a 资料接入者，I want 固定原件到结构/来源/向量的真实探路证据，So that S2按已证格式实施导入。

**依赖：** 2.1。**来源：** FR-6/7；NFR-5/6；AR-07/10；AD-5/9；C3/C7；实施契约§3.3/3.4。

**Acceptance Criteria:**

- **Given** 固定版本/hash的PDF文本/扫描、DOCX、TXT、MD，**When** PDF/DOCX经真实MinerU、TXT/MD经本地有界严格UTF8路由，**Then** 留真实响应/ZIP、规则及简单跨页表格/扫描结果和来源校验；不扩Doc/Ppt/Xls、不抓远程资源，不以假件替代真实上游格式。
- **Given** 页0/1基数、旋转90/270、CropBox、无bbox和非PDF真实结构样例，**When** 归一并人工核对，**Then** C3页/区域/码点/hash对应原件，坏定位明确失败；不猜页/坐标。
- **Given** 实际embedding query/document配置，**When** 验每条/每批token、字节、D及兼容指纹，**Then** 发布已证profile和S2所需D迁移输入；各格式/来源/embedding子门分列通过/失败，未证格式不开放，不将局部通过算五格式全过。

### Story 2.3：证明四场景完整生成预算

As a RAG实施者，I want 用实际用途profile核完整输入和最大合法输出，So that 受理范围能容纳完整答案或矩阵。

**依赖：** 2.1。**来源：** FR-9/12；NFR-4；AR-08/10；AD-10；C6；实施契约§3.5–3.7。

**Acceptance Criteria:**

- **Given** 已定千问路线的候选模式，**When** 核实际端点/SDK/模型/alias/tokenizer及完整消息framing，**Then** 登记I_max/O_max/C_max、普通文本JSON、思考关闭或有限R_think、响应字节与可靠计数依据；不从另一产品计数接口推定可用。
- **Given** 实际ID、四场景最小完整载荷及最大合法分支，**When** 预算S/M/H/E与完整输出R，**Then** 首个可用profile证明最小载荷可容纳，最大输入/24格仅通过的组合可受理；compact128不删格/必要事实，未知保持budget_unverified。
- **Given** 高token输入、输出上界/length/非法JSON/计数偏差，**When** 执行正负探路，**Then** 保存实际调用/费用或unknown，截断/非法整答失败，偏差超界停profile新生成；禁tools/自动历史/内置检索/额外LLM修复，明确零候选服务器模板与非零未证失败分支。

### Story 2.4：验证必须理解连接关系的真正图意

As a 手册实施者，I want 对固定原图连接题核真实依据，So that SC-4不以OCR识字冒充图意。

**依赖：** 2.2；所用视觉用途另完成2.1限制核验。**来源：** FR-7/13；SM-5；NFR-6；AR-10；AD-10/14；C3；实施契约§3.4。

**Acceptance Criteria:**

- **Given** 已选LM2596连接图原件/hash/定位及调用前固定的开发金标事实，**When** 核MinerU实际产物，**Then** 问题必须依赖图中连线，图注/纯识字不算通过，保留人工对照与失败。
- **Given** 主路图意不足，**When** 接受独立视觉API验证，**Then** 另核图像字节/分辨率/token与真实限制，说明绑定原图/来源后受控入块；保留MinerU主路。仍无有效依据阻S5/整期，不降SM、不默认改本地OCR。

### Story 2.5：验证真实任务池活性与资源包络

As a 运行实施者，I want 在1档和4档验证共享限流/公平推进及并存资源，So that 只启用有证据的档位。

**依赖：** 2.2（含2.1）；本条只验文档任务，不依赖2.3生成预算；目标机部分需合法环境访问。**来源：** FR-4/15/16；NFR-2/4/5；AR-05/10；AD-7/14；C8；运行R6/R7。

**Acceptance Criteria:**

- **Given** S0隔离探路工具与真实账号，**When** 1/4档满池submit→accepted→poll→terminal、取消/unknown/重启，**Then** 原task可有限推进，组件只归还一次；4档证四远端工作重叠且本机重阶段≤1，无pending常驻线程/Session，原deadline不刷新。
- **Given** 已证文档用途与受控上传/纯检索embedding形状负载，**When** 与worker远端等待/重阶段并存，**Then** 记录RSS/FD/连接/磁盘/预算/延迟及每call真实费用，不要求答案生成/业务页；目标4C4GB结果与开发机结果分列。
- **Given** 1档或4档各自的真实限制/活性/所用环境资源证据，**When** 发布P0-DOC-1/P0-DOC-4子门，**Then** 两档可分别消费，未证档保持禁用，S2仅消费所启用文档档位子门，2.3未完成不阻此子门；目标机结果仍须S6补齐，不以开发机成绩声称4GB通过。

### Story 2.6：补验真实生成与文档任务并存资源

As a 运行实施者，I want 在生成预算已证后核查询/上传与文档任务并存，So that 完整业务负载只启用有证据的档位。

**依赖：** 2.3、2.5对应文档档位；目标机部分需合法环境访问。**来源：** FR-4/9/15/16；NFR-4/5；AR-05/10；AD-14；C8；运行R6/R7。

**Acceptance Criteria:**

- **Given** P0-DOC-1/4与实际生成profile，**When** 隔离工具运行真实问答/embedding、上传与文档等待/重阶段并存，**Then** 保存P0-MIX-1/P0-MIX-4的真实共额/活性/RSS/FD/磁盘/延迟/成本证据，四远端重叠仍本机重阶段≤1；不依S3页面。
- **Given** MIX未证或目标环境暂缺，**When** 输出清单，**Then** 只阻对应并存组合/档位，S2所用已证DOC子门不被2.6整包状态反向阻断；S3开放实际组合前取相应MIX证据，S6上线前必须补齐目标4C4GB实测。

## Epic 3：用户能安全进入并管理授权范围（S1）

用户可登录、管理空间/团队/库授权和本人只读凭证；平台与业务分权。主责FR-1–5/14/16，承接FR-6准入；此阶段不依赖真实模型调用。

### Story 3.1：首次登录、账户生命周期与首日起安全台账

As a 有效账号用户，I want 首次登录和改密退出均有一致安全边界，So that 我能进入本人空间且旧凭据不能继续用。

**依赖：** 1.5。**来源：** FR-1/4/5/16；NFR-1/3/6；AR-09；UX-DR17；AD-3/4/13；C4/C5；IA-01；AC-01；R02。

**Acceptance Criteria:**

- **Given** 初始化管理员与有效账号、全新无Cookie/无token浏览器，**When** 精确部署Origin+JSON+X-RAG-Login:1登录，**Then** 成功旋转会话/token、no-store响应交内存，context重载可取当前token；登录不被会话token前置阻断。
- **Given** missing/null/跨源Origin、form/缺固定头、停用/未核验账号，**When** 登录或已认证写缺/错/旧token，**Then** 依C5拒绝、不建会话/不返正文、CORS关闭；双凭据整拒，密码/会话/失败桶及账号EX规则按C5，不泄露额外账号事实。
- **Given** 本人改密/退出或平台停用，**When** 提交，**Then** 依C5撤销会话/凭证（改密后重登录）；自本条首次安全变更即与稳定ID最小安全事件同事务，失败全回滚，提供连续区间认证导出及gap信息的基础命令；不留S6补造早期事件。

### Story 3.2：选择空间并隔离私有视图恢复

As a 已登录用户，I want 清楚看到当前空间并安全切换/恢复页面，So that 旧账号或旧空间内容不会混入当前视图。

**依赖：** 3.1。**来源：** FR-1/14；NFR-1；UX-DR01/02/03/15/16/18/19/20/21；AD-12；C2/C4；IA-01/02；G-01–12；AC-18/21/23；R03。

**Acceptance Criteria:**

- **Given** 首次上下文或当前合法上下文，**When** 选空间/有未提交输入时切换，**Then** 初次默认个人空间、显式显示身份/空间、确认清空后新空间新会话；导航/范围/状态/确认组件采用DESIGN tokens与断点，未授权列表不加载。
- **Given** 私有成功/错误/认证/context/状态和gateway自产错误，**When** 同URL换账号/撤权、If-*与history/bfcache恢复，**Then** 应用/网关no-store、禁缓存、无ETag/Last-Modified/304；pagehide清/遮蔽DOM和blob，pageshow先清context/代次，再重核当前context及全部欲显示依赖，无旧正文闪现。
- **Given** 退出/切空间/epoch变化/后台页恢复及Abort失败的旧回包，**When** 响应到达，**Then** 归属代次阻落新store/视图；无localStorage/IndexedDB/CacheStorage/SW私有body。真实浏览器、键盘/辅助技术及五宽度/200%证据通过才开放公共设施。

### Story 3.3：邀请成员、交接所有权并退出团队

As a 团队所有者，I want 在明确角色与责任下管理成员，So that 团队始终有有效所有者且失权及时生效。

**依赖：** 3.2。**来源：** FR-1/2/16；NFR-1/2；UX-DR14/15/16；AD-3/4；C4/C5；IA-02/11/12；AC-02/03。

**Acceptance Criteria:**

- **Given** 平台/所有者与已有有效账号，**When** 建团队指定初始owner、发带角色邀请并由目标接受，**Then** 每团队一个有效owner、接受才入队且普通成员初始无库权；未接受/撤销/过期及普通自建/成员管理反例拒绝。
- **Given** 当前owner与有效团队接任者，**When** 转让/退出/停用/降级/移除/解散，**Then** 先交接、旧owner转维护者不新增库授权，负责库接管且资料保留；解散先阻访问并登记关联清理意图；全部安全事件同事务。
- **Given** 该片尚未交付建库页面，**When** 验证负责库交接，**Then** 本条同步交付接管所需最小库归属/负责人持久模型与端口，以无文档负载的受控库夹具实证职责转移；3.4增量实现创建/授权和已有库联调，不作为3.3完成前置，不提前实现文档管线。
- **Given** 名称确认/默认空角色和管理丢回包，**When** 提交或恢复，**Then** 完整影响/安全焦点/Tab/Esc可用，未知先读当前邀请/成员/owner不自动重写；平台办理交接不获正文读权。

### Story 3.4：创建知识库并管理逐库授权与负责人

As a 有权维护者或所有者，I want 明确库范围与负责人职责，So that 维护、授权管理和普通读取不会混淆。

**依赖：** 3.3。**来源：** FR-1/3/5/16；NFR-1/2；UX-DR03/04/14/15；AD-3/4；C4/C5；IA-03/11；AC-03/04/05。

**Acceptance Criteria:**

- **Given** 个人本人/团队owner/维护者，**When** 建库/列有权库及编辑授权，**Then** 创建者自动负责，角色×逐库范围共同判定；分页/排序/筛选按IA-03和C5，不加载全库再前端分页，不伪造总数。
- **Given** 非负责库维护者或使用者，**When** 直调管ACL/删整库/维护，**Then** 无相应动作拒绝；撤负责人库权同步owner接管并清该人全部该库授权，旧创建者不能自恢复，owner固有范围不按单库撤销。
- **Given** 个人/跨团队/混合合法与非法目标或无权/不存在深链，**When** 请求，**Then** 当前锁序重核、整体安全拒绝不泄存在性/部分结果；删库先墓碑/台账/关联清理意图，不依赖未来文档清理才断读。

### Story 3.5：创建并撤销本人只读程序凭证

As a 程序调用者，I want 显式限定凭证范围和期限，So that 程序仅使用本人当前有权能力。

**依赖：** 3.4。**来源：** FR-4/5/14/16；NFR-1/6；UX-DR12/15；AD-4/5；C4/C5；IA-10；AC-19。

**Acceptance Criteria:**

- **Given** 当前本人空间/授权库，**When** 显式选单空间、非空库/动作与未来到期创建，**Then** 有效范围取scope与当前权交集，密钥仅创建显示（默认遮罩、显式复制），后续只有元信息；改变空间清库/动作，到期字段按IA-10初态为空、必填未来上海时区时间且遵守C5最大365d，未填不提交。C5的30d技术seed不用于表单预填或服务器默补到期；此按UX管字段初态的既有分工协调来源字面差异，不改变期限/权限边界。
- **Given** 本人或本团队owner撤销、停用/到期/移除/撤库权，**When** 访问受控context/状态，**Then** 立即失效或缩窄；Cookie+Bearer、越库、写/他人任务等拒绝，无身份回退；变更同事务台账。
- **Given** 创建回包丢失或关闭秘密面板，**When** 恢复，**Then** 先读元信息、不再次取明文或自动新建，明确撤销后可由本人新建；秘密不持久保存/自动播报。

### Story 3.6：原子预留容量/次数并终结有限上传意图

As a 空间管理者，I want 可解释的原件容量、日配额及上传期限，So that 并发和中断不会超额或永久占用。

**依赖：** 3.4。**来源：** FR-4/6/15/16；NFR-2/3；UX-DR05/06/13；AD-6/8/11；C1/C4/C5；实施契约§2.1–2.4；AC-06/07/20。

**Acceptance Criteria:**

- **Given** 空间最后一笔容量或上海日次数，**When** 真实PG并发预留/降额，**Then** 仅一笔成功、账不为负，下调不撤已受理；原件含保留版本/失败/清理中+预留，替换须双份；物理预算独立。
- **Given** upload_operation_id同输入/异输入/过旧或从未PUT/半传，**When** 建意图/重传/放弃/启动及周期扫描，**Then** 唯一候选/预留、原开始/总/无进展deadline及24h/7d规则按契约；未清资产不释放，失败保留候选/成功历史不因TTL删除。本故事可用S0 writer假件独立验，不以S2文件管线为前置。
- **Given** 日桶/容量transition与问答操作测试上下文，**When** 重复结算/释放、跨日终态或崩溃恢复，**Then** 原受理日一次效果、unknown成本独立，不造完整问答能力；真实PG唯一性与前端有限限制/三账投影均留证。

### Story 3.7：平台配置与S1身份准入开放门

As a 平台管理员，I want 配置和运行元数据与业务资料分权，So that 我能管理接入和配额而不能读取他人正文。

**依赖：** 3.5、3.6。**来源：** FR-1–5/16；NFR-1/3/6；UX-DR13/14/16；AD-4/8/9/13；C5/C6；IA-12；AC-01–05/18/19/20；R02/R03。

**Acceptance Criteria:**

- **Given** 平台身份，**When** 配账号/团队、模型/存储/配额与验证状态，**Then** 严格schema/HTTPS白名单/secret只输入不回显，unknown不标可用；改默认不覆盖已有profile、不暗迁移/DDL/充值；纯平台直读个人/团队正文、他人历史/代登录拒绝。
- **Given** 供应方secret配置/留空/替换/轮换或主密钥缺失，**When** 保存/读取/验证，**Then** 留空保持旧值、清除须独立确认、保存与验证分开；按C5 AESGCM/唯一96位nonce/AAD绑定deployment/provider/config/key_id加密，主密钥外置，保旧读能力后重加密退役，缺钥明确阻能力不重置密文、不回显秘密。
- **Given** S0门、已核P0对应动作及凭据齐备，**When** 显式接入验证，**Then** 通过统一call/gate/账；未具备时只显示不可验证/原因，不为完成本故事强求真实模型账号；与E2证据按用途合并使用。
- **Given** S1全部故事，**When** 运行R02首次登录/认证写、R03设施、角色/范围/凭证/末笔预留/锁序/台账正反例，**Then** 任何越权、重复记账或浏览器旧正文闪现均阻身份及业务入口；记录S1门，不把运行未执行变成PASS。

## Epic 4：维护者完成资料全生命周期并核查来源（S2）

无需问答UI即可完成导入、校核、原子发布、替换、删除和恢复。主责FR-6–8/15，涵盖当前资源权限、容量、审计、Web。**Epic入口：** S1门通过，P0对应格式/来源/embedding子门已证，实际档位有自身限额/资源依据；不要求P0图意/答案预算全过。

### Story 4.1：逐文件上传并可靠登记原件

As a 当前库维护者，I want 有限上传/替换入口与原候选恢复，So that 批次局部失败和重传不制造重复版本。

**依赖：** 3.7、2.2对应格式/来源/embedding子门、2.5的P0-DOC-1或P0-DOC-4所启用档位；不依赖2.3/2.6整体完成。**来源：** FR-4/6/15；NFR-1/2/6；UX-DR05/06；AD-6/7/8；C4/C7；运行R2/R3；IA-04/05；AC-06/07。

**Acceptance Criteria:**

- **Given** 当前维护权及有效限制，**When** 批量提交合法与坏/加密/超界文件，**Then** 逐文件独立ID/候选/预留/原因，标题等初值按IA-05，限制未知拒相应新受理，不先删旧版/发供应方签名给前端。
- **Given** 未PUT/半传/重复PUT、同声明但实际异hash，**When** 原ID恢复/完成，**Then** 原期限不刷新，先有界槽/预算再流式读取，实际hash/长度相符才重放；完成核当前权/fence/guard并同事务原件登记+预留转实占+job。
- **Given** 超期先胜/完成先胜、旧writer及断网，**When** 竞态或清理，**Then** 迟到不能复活候选/重复任务，真实停写后一次释放；UI保原ID和明确状态，上传完成不标ready。

### Story 4.2：处理资料并原子发布索引与可靠来源

As a 库维护者，I want 查看可查询版本与候选/任务的独立事实，So that 普通文档可自动就绪且失败不会伪装成功。

**依赖：** 4.1。**来源：** FR-6/7/8/14/15；NFR-1/2；AR-07；UX-DR04/06；AD-6/9/12；C3/C4/C7/C8；IA-04/06；AC-08/10。

**Acceptance Criteria:**

- **Given** 2.2已证profile/D与原件，**When** 执行显式vector(D)迁移、建活动generation/revision、结构分块/向量化，**Then** 所有格式走C7路由与C3来源，块/向量维度/数量/profile/来源校验齐才同UoW发布；S3不再首次补索引。
- **Given** 首次完整/可靠范围partial、未知失败范围/缺来源/缺向量，**When** 程序校核，**Then** 完整自动ready、合法partial仅发布可靠部分并持续不完整提示；不合格不发布，无人工逐份批准动作。
- **Given** 正常/失败/重启/乱序attempt，**When** 查看列表/详情/任务或完成发布，**Then** 三栏及generation/cleanup五投影、allowed_actions严格映射，旧执行不能发布；双gate/公平poll/2h原期限由S0复用，后台归库任务不随上传者降级取消。

### Story 4.3：安全核查原件、提取与引用位置

As a 有权维护者或读者，I want 核对真实版本来源并安全下载原件，So that 位置可信且预览不执行资料中的主动内容。

**依赖：** 4.2。**来源：** FR-3/5/7/8/14；NFR-1/6；UX-DR07/21/22；AD-5/12；C2/C3/C4/C7；IA-06/09；AC-10/16/18/21；R03/R04。

**Acceptance Criteria:**

- **Given** 可靠PDF页/bbox、仅页、非PDF结构及中英文/emoji/CRLF样例，**When** 校核/引用/翻页，**Then** 可信PNG/JPEG高亮或页级回退、物理页1起、准确片段/hash；非PDF结构不编页，坏hash/locator明确不可用、不猜首页，原件/提取身份与返回焦点明确。
- **Given** PDF/DOCX/TXT/MD原件及恶意CRLF/路径/控制/超长名、伪MIME/扩展/上游头，**When** 下载/预览，**Then** 一律attachment+精确白名单MIME+nosniff，服务器有界fallback/UTF8 filename*；inline仅已核PNG/JPEG，含HTML的合法TXT/MD与提取仅受控文本/清洗，不执行脚本/不抓远程资源。
- **Given** 同URL换账号/撤权、If-*、back/forward/bfcache及资源错误，**When** 在真实浏览器读取原件/页图/提取/citation，**Then** 每次当前授权/归属/墓碑/hash重核，no-store/无304，恢复先遮蔽及依赖重核、无旧body；R03/R04未过不开放资源入口，不能只引用S1设施成绩。

### Story 4.4：替换完整版本并删除后真实清理

As a 维护者，I want 新版完整就绪才切换、删除先断访问，So that 更新或清理故障不损坏现行资料边界。

**依赖：** 4.3。**来源：** FR-3/4/8/15/16；NFR-1/2；UX-DR04/06/15；AD-3/6/8/9；C4；运行R3；IA-03/04；AC-07/08/16。

**Acceptance Criteria:**

- **Given** v1生效、v2候选完整/partial/失败及更晚候选，**When** 完成/乱序发布，**Then** 仅当前完整候选与合格索引同事务切active/revision，失败/partial保v1；新检索只v2，合法历史v1仍受控核验。
- **Given** 文档/库/团队删除或清理失败，**When** 墓碑提交/旧worker迟到/直接读资源，**Then** 访问与检索立即阻断、revision变更及安全台账同事务，旧任务不复活；停写真实清完才一次返容量/物理预算，失败显示blocked并可受控重试。
- **Given** 满额替换/删除与上传并发，**When** 操作，**Then** 不先抵旧版、不双退/漏计；名称确认/焦点/列表返回按UX，清理失败不回滚访问阻断，原件留存不因操作TTL消失。

### Story 4.5：分别执行原任务核对、本地继续和知情重交

As a 当前维护者，I want 看清unknown与三类恢复动作，So that 我可恢复处理而不会不知情重复外发。

**依赖：** 4.4。**来源：** FR-4/5/6/15/16；NFR-1/2/3；UX-DR06/15/16；AD-7/11/12；C4/C5/C8；实施契约§2.7；IA-06；AC-04/09。

**Acceptance Criteria:**

- **Given** 上游known ID而原job到期，**When** 当前维护者显式action_key核对，**Then** 新120秒有界只读上下文只读原状态（仅实际有接口才另核原费），不猜ID/换账号/下载/发布/续原job；ready仅观测，GET/program不隐式发起核对。
- **Given** 已验证兼容资产或仅ready URL，**When** 显式本地继续，**Then** 新job/attempt/deadline重核当前权/guard/预算/资产，失效候选则新候选，不复活旧Key；必要时在新资格下下载原任务结果，不自动申请/PUT解析。
- **Given** 解析需重新提交或旧结果迟到，**When** 默认未勾知情复选/明确勾选确认，**Then** 未确认不外发，合法确认才新call并保原关联/unknown；旧成果不能盖当前候选，原2h不刷新。降级但仍读权者仅本人状态，离队/撤库权者不可读改。

## Epic 5：员工获得有据企业答案并安全恢复历史（S3）

交付SC-2、共享完整预算/操作与只读API。**入口：** S2全部门通过；P0实际embedding与完整问答预算通过。主责FR-9/11/14及计次/历史/反馈。

### Story 5.1：在当前授权内执行精确B0检索

As a 用户，I want 显式选范围仅检索资料，So that 我能核验最多五个当前证据候选。

**依赖：** 4.5、2.3；实际开放的查询/文档并存组合另取2.6对应MIX子门。**来源：** FR-3/5/9/14；NFR-1/3/4；UX-DR03/08；AD-9/10/11；C1/C3/C6/C8；IA-07/09；AC-03/15。

**Acceptance Criteria:**

- **Given** 单空间显式非空无重复目标及兼容S2索引，**When** 请求纯检索，**Then** 外发前逐目标授权、PG内先过滤权限/墓碑/固定版本代次后精确cosine+chunk_id排序，最终≤5；混合无权/不存在整拒且不外发，不静默漏库。
- **Given** 纯检索执行上下文与实际完整query embedding预算，**When** 无逻辑槽/依赖失败/零候选，**Then** 全局2/用户1/子路1、无等待查询队列；有持久deadline/fence/call账但无产品问答预留，零结果空态，不自动生成。
- **Given** UI输入和引用，**When** 键盘提交“仅检索资料”及来源返回，**Then** 原输入不裁剪，显式说明不扣问答但可能有调用；有界取候选/正文，不加ANN/关键词/重排/邻块。

### Story 5.2：持久受理问答并只结算一个逻辑终态

As a 问答用户，I want 同一操作安全恢复状态与结果，So that 断网重传不会重复调用或扣次。

**依赖：** 5.1。**来源：** FR-4/5/9/14/15；NFR-1/2/3；UX-DR08/16；AD-3/8/11；C1/C2/C4；实施契约§2.2/2.3；AC-15/18。

**Acceptance Criteria:**

- **Given** 新/已有Key及原规范输入HMAC，**When** POST重传/异输入/B下调/H急降/过期，**Then** 已有Key先匹配、执行中202、异输入409、失败回原失败、过期410，不自动新单；H急降仍可当前授权GET恢复，24h/7d和key_id按原规则。
- **Given** 成功完成全部子检索且原始最终零候选，**When** 本地不足模板通过schema与当前权，**Then** 不调LLM且结果/依赖/会话消息指针及原上海日结算同UoW；非零暂未生成路径可控失败释放，不以未来5.3为本条验收前置。
- **Given** 预留/成功提交前后/丢回包/跨日/超期/迟到attempt，**When** 真实PG故障与原Key/operation恢复，**Then** 只一对消息/一次结算或释放、原时间版本保留、旧执行不能成功；业务失败不抹实际费用。网络Abort不宣称取消/退款。

### Story 5.3：在实际完整预算内回答企业问题

As a 新员工小周，I want 获得有版本依据的流程与材料，So that 我可按制度做事并知道负责人或冲突缺口。

**依赖：** 5.2。**来源：** FR-9/11；NFR-1/4；UX-DR08/09；AD-5/10；C3/C6；实施契约§3.5–3.7；IA-07；AC-12/15/21。

**Acceptance Criteria:**

- **Given** 2.3已证profile与合法输入，**When** 计算完整S/M/H/E和R，**Then** 当前输入完整保留，先剔整条辅助历史再按第5至第1缩来源原子组，保表头/单位/型号/条件；catalog只等于实见spans/hash，最多五块，不塞全文/旧答/邻块。
- **Given** 基础预算必超、非零未证、预算裁空、length或非法JSON/ID/子契约，**When** 调用前后校验，**Then** 分别按原422/503/502等失败与一次释放，不装正常不足、不交草稿/暗裁返回/额外LLM修复；budget_snapshot可核完整计数/输出档/终止/usage。
- **Given** SC-2开发样例及负责人缺失/同条件制度冲突，**When** 正常完整生成，**Then** enterprise仅process/material/condition/owner，必要事实/适用条件/引用齐，无人名编造/未问字段强填，四outcome合法且冲突双方有据，完整一次显示；输出前当前权失败整答拒绝。

### Story 5.4：同空间追问并安全回看历史与原结果

As a 用户，I want 同空间连续提问和核验历史原版本，So that 会话不会绕过当前权限或混入旧证据。

**依赖：** 5.3。**来源：** FR-3/5/8/9/14/15；NFR-1/2；UX-DR02/07/08/09/21；AD-11/12；C2/C3/C4；IA-07/09；AC-15/16/18；R03。

**Acceptance Criteria:**

- **Given** 同空间会话与expected_parent_turn，**When** 并发新轮次/过旧父轮次/切空间，**Then** 一未终结轮次、冲突保输入重新读后本人显式提交；跨空间新会话，最多两条合法用户历史整条纳入/剔除，旧答案/证据不作新证据。
- **Given** v1已答后切v2、GC旧向量或撤权/删来源，**When** 历史/原operation读回，**Then** 合法v1按EvidenceSnapshot/hash仍核验且标原时间版本，失权则隐藏整答；新查询只活动版，GET继承原动作/目标/全部依赖，不生成。
- **Given** 真实浏览器答案/历史/operation成功与失败路由，**When** 同URL换账号/撤权、If-*、前进后退/bfcache/后台恢复及迟到回包，**Then** 重做R03：no-store、gateway不缓存、无验证器/304、先遮蔽清代次再重核全部依赖重取，无旧正文闪现；此入口未过不得开放，S1成绩不代本条。

### Story 5.5：通过同一用例提供受scope限制的只读API

As a 应用开发者，I want 用本人凭证检索/问答/取引用与状态，So that 程序可复用RAG且不会获得Web管理权。

**依赖：** 5.4。**来源：** FR-3/5/9/14/15；NFR-1/5；UX-DR12；AD-1/4/5；C2/C4/C5；实施契约§5.1；AC-19。

**Acceptance Criteria:**

- **Given** 当前合法本人Bearer，**When** 调检索/问答/原operation/citation/本人导入task状态，**Then** Web/program共享application与schema，返回安全ID/版本/定位；无资料写/成员/授权/核对动作，不读他人任务/历史。
- **Given** 原凭证撤销、同人同渠道新合法凭证或仅citation动作，**When** 取原结果/来源，**Then** 新凭证覆盖原动作/原目标/依赖才取operation，旧凭证拒绝；独立citation有当前来源权即可，不强加answers也不交他人答案。
- **Given** scope混合越界、过期/当前失权、Cookie+Bearer，**When** 调用，**Then** 整拒无回退/无部分结果/无额外外发，错误/原结果no-store；OpenAPI和无Cookie程序请求样例可复现。comparison API在6.2增量。

### Story 5.6：反馈答案并核对三类用量

As a 用户或授权管理者，I want 对当前答案反馈并分清配额与调用费用，So that 我能报告证据问题且不把失败调用当免费。

**依赖：** 5.5。**来源：** FR-4/14/16；NFR-1/3/6；UX-DR11/13/16；AD-8/12/13；C1/C5；IA-07/10/12；AC-20/21。

**Acceptance Criteria:**

- **Given** 本人可读result，**When** 选择错误/缺依据/引用问题并提交有限说明，**Then** 绑定当前答案、确认成功/失败保输入，不重生成/不扣问答，普通用户不可读他人反馈或全局日志。
- **Given** 原件容量、上海日次数、逐call成本账及迟到/冲突事实，**When** 授权查看统计，**Then** 三组标题/单位/范围/时间/预留/清理中分明，失败调用保留、unknown不填0、估价不装账单；平台只有去秘密元数据，正文/密钥不入日志。

## Epic 6：支持人员排障与售前逐格核验（S4）

SC-1/SC-3复用已验S3管线，不增加候选上限或查询等待队列。

### Story 6.1：按版本环境给出有据排障顺序

As a 技术支持小林，I want 结合日志与版本核对候选原因和检查步骤，So that 我能人工排查而不会误信系统已确定根因。

**依赖：** 5.6。**来源：** FR-9/10/14；NFR-1/4；UX-DR08/09；AD-10；C6；IA-07/09；AC-11。

**Acceptance Criteria:**

- **Given** v2升级连接超时日志/环境及有权资料，**When** support问答，**Then** 候选原因、适用条件、检查顺序和逐步引用齐全，仅cause/check/condition/limitation合法facts，日志完整进入预算。
- **Given** 缺版本/环境、版本不匹配、证据不足或依赖/预算失败，**When** 返回，**Then** 澄清/限定与执行失败分开，不给无条件步骤、不执行命令/声称修复；相同Web/API语义和原Key恢复/当前授权继续成立。

### Story 6.2：固定版本并返回完整四态比较矩阵

As a 售前小陈，I want 对A/B文档逐条件查看四态和来源，So that 我能区分明确不支持与尚无依据。

**依赖：** 6.1。**来源：** FR-5/9/12/14；NFR-1/4；UX-DR03/10/11；AD-5/9/10/11；C1/C2/C3/C6/C8；IA-08/09；AC-14/15/18/19/21/23。

**Acceptance Criteria:**

- **Given** 2–4对象/1–6条件、256单条/1024合计/≤24路有效配置及真实M预算，**When** 编辑/上移下移/提交，**Then** 空/重复/越限/任一越权外发前整拒，不裁对象条件；受理固定每文档活动版本，历史替换版不可新选，版本对比用分别导入文档。
- **Given** 条件原序、文档ID序的串行子检索，**When** 固定名次轮转合并，**Then** 全请求≤5去重实见块、每对象×条件恰一格；满足/明确不满足直接有据、同格冲突来自固定版本互斥双方，不同对象差异不误冲突；不足有缺口。
- **Given** 真零候选或缺格/截断/越界证据/缺冲突一边/reason超compact128，**When** 完成，**Then** 零候选完整全格不足计1；其余整答失败/一次释放/费用保留，无草稿/前端裁返回/LLM修复，原Key复用与API scope一致。
- **Given** 窄屏/键盘/屏幕阅读器，**When** 逐格查证/返回，**Then** 完整矩阵局部横滚、表头关系/四态文字/理由/否定/条件不省略，焦点滚入可视并回原格；反馈绑定整次结果。

## Epic 7：工程师核验复杂手册事实（S5）

SC-4在S2最小校核/来源之上扩质量，不后补基础回看。主责FR-7/13。

### Story 7.1：把表格、扫描及图意转成可核验事实

As a 手册维护者，I want 人工对照结构与图意并形成可靠候选，So that 检索证据保留型号、单位和适用关系。

**依赖：** 6.2、2.4；2.2表格/扫描子门。**来源：** FR-7/8/13；SM-5；NFR-1/6；UX-DR06/07；AD-5/6/10；C3/C7；IA-06/09；AC-08/10/13。

**Acceptance Criteria:**

- **Given** 规则/简单跨页表、扫描页与必须读连线的图，**When** 人工对照/结构化入块，**Then** 表头/行列/数值单位一致、OCR标注事实可答、图意有直接依据并绑定原图/定位/上下文，不仅贴图或图注。
- **Given** 无可信bbox、非PDF结构/复杂不支持区或修正，**When** 查看/重新处理，**Then** 沿S2页级/真实结构回退和安全媒体，不猜页，失败范围明确；修订原件/合法参数建新候选，不原地改历史、不加逐份审批/OCR编辑器。

### Story 7.2：按型号版本回答复杂手册问题

As a 实施工程师小赵，I want 核验M2/E17的步骤、部件和参数，So that 我能确认数值单位与限制实际适用。

**依赖：** 7.1。**来源：** FR-7/9/13/14；SM-1/2/3/5；NFR-1/4；UX-DR08/09；AD-10/12；C3/C6；IA-07/09；AC-13。

**Acceptance Criteria:**

- **Given** M2/E17开发问题含正文/表/OCR/图意必要事实，**When** manual回答，**Then** step/parameter/limitation/condition按序呈现，量值结构value_text+unit、型号版本条件/原表图来源完整，仍只用全请求≤5实见块与完整预算。
- **Given** 型号不明/单位缺失/不兼容片段或图意无依据，**When** 校核，**Then** 澄清/限定、不拼参数/捏造图意；关键表/OCR/图意失败阻本片和整期，纯文本正确或平均分不能替代。P0/开发成绩不直接算冻结SM通过。

## Epic 8：维护者安全变更索引并在目标机可信运行（S6）

目标机访问、独立恢复操作者/介质为外部前提。S0/S1已有epoch/台账/资产骨架，S2已有索引；本Epic只扩管理与真实演练。

### Story 8.1：同维重建期间安全查询并允许删除

As a 当前库维护者，I want 显式重建索引且看到写限制，So that 索引变化不会切错资料集或永久锁库。

**依赖：** 7.2。**来源：** FR-3/4/8/15；NFR-1/2；UX-DR04/06/14；AD-3/9；C4；实施契约§3.1；IA-04/12；AC-17/20。

**Acceptance Criteria:**

- **Given** 当前维护权且无有效写意图，**When** 显式同维重建，**Then** 同锁建候选代固定revision/版本集和owner_job/attempt/token；旧代可读，新上传/替换/重处理拒绝不暗排队；平台仅有平台身份不能操作库重建。
- **Given** 重建与上传/删除/失败/取消/过期/旧attempt，**When** 真实PG并发，**Then** 删除仍墓碑并改revision/废候选，只有本guard可条件释放；集变化/不完整/维度profile错不切代，旧attempt不解新锁，清理余账不永久阻写。
- **Given** 切代与旧在途/历史引用，**When** 固定快照读/GC，**Then** 不暗换代，旧向量保留到原终态/期限，历史EvidenceSnapshot/原来源不被GC破坏；状态/维护说明可见。

### Story 8.2：显式维护迁移embedding维度

As a 部署维护者，I want 在维护窗口验证变维和退回，So that 模型变更不会混查向量空间。

**依赖：** 8.1；新profile另有P0实证。**来源：** FR-4/8/15；NFR-2/5；AD-9；C4/C6；实施契约§3.1；AC-17/20。

**Acceptance Criteria:**

- **Given** 新D2与旧D不兼容，**When** 在线请求/平台改默认，**Then** 原库不被覆盖、整请求明确需迁移，无自动DDL/混查/在线任意切换。
- **Given** 显式维护窗口及匹配备份，**When** Alembic建隔离D2存储/完整重建/授权引用验证并切换或注入失败退回，**Then** 保留可恢复旧存储；受影响读写暂停，删除墓碑仍可登记并在恢复前重放，失败不破旧索引。用受控两维profile夹具可验迁移机制，不冒充第二真实型号已接通。

### Story 8.3：在4C4GB目标机验证部署与一致备份

As a 部署方，I want 核实真实环境和四服务并存保护，So that 运行不依赖开发电脑且备份材料可核。

**依赖：** 8.2、2.5/2.6目标机证据补齐；合法环境/TLS/秘密/操作者。**来源：** FR-4/15/16；NFR-3/4/5/6；AR-09/10；AD-13/14；C8；运行R4/R6；AC-05/20/22。

**Acceptance Criteria:**

- **Given** 实际Ubuntu/Engine/磁盘/域名TLS，**When** 部署锁定gateway/API/worker/PG，**Then** 仅gateway公开HTTPS，卷/锁/epoch/服务secret最小权限、非root只读根，无私有静态直出，前端预构建；实际配置/网络/秘密检查留证。
- **Given** P0真实负载与查询/上传/重处理并存，**When** 测1/4档RSS/峰值/OOM/CPU/FD/连接/事务/磁盘/延迟，**Then** 按总4GB配置各预算并只启已验档位；不足先收并发/流式/批量/输入重测，仍不满足记录变更，不降低功能门槛。
- **Given** 部署方确认备份频率/留存/最大备份龄/可丢失窗口和现行受托登记，**When** 停写制作同snapshot_id的PG/roles/原件解析引用/配置/密文/独立密钥恢复材料与台账认证区间，**Then** hash/可读性核验、独立受控介质及gap可追溯；未确认窗口或介质不签上线，备份存在不等于恢复通过。
- **Given** 普通启动/发布/备份与schema不兼容失败，**When** 有限排空后迁移或冻结一致包，**Then** 启动按R5核schema/epoch/能力再逐范围开放，发布不重置deadline、不在目标机构建；备份冻结全部应用写入含会话/安全事件/扫描/cleanup/迟到账，紧急撤权中止包后重做，失败只回已证schema兼容产物，否则维护隔离并走可信恢复，不把在线文件拷贝自称一致。

### Story 8.4：从旧备份隔离恢复并逐范围放行

As a 独立恢复操作者，I want 用现行受托证据恢复和核验，So that 旧密码/权限/任务不会从备份复活。

**依赖：** 8.3。**来源：** FR-3/4/8/15/16；NFR-1/2/5/6；UX-DR02/13/14/16；AD-13/14；C8；实施契约§4.1–4.4；运行R5-T1–T6；IA-12；AC-22；R01/R03。

**Acceptance Criteria:**

- **Given** 备份后再停用/撤权/撤key/删除的旧包及独立受托链，**When** T1–T3恢复，**Then** 先停旧sender/业务并验包，全新≥128位随机epoch、旧会话/Bearer无效、账号unverified；独立核验/重置密码、已知拒绝优先、gap逐范围外部确认，不从旧owner自证，无明确信息保持隔离。
- **Given** 旧pending/success/丢失call/unknown task/当日配额不明，**When** T4–T5核对，**Then** fence旧attempt、success不重结算、旧pending一次释放恢复预留；pool与taskgate先blocked_unverified，全部旧sender/grant独立隔离后新DB上界等完整W仅解窗口，不解task未知；按已核维度/动作可放原ID只读poll，不假拆池或盲重交。
- **Given** 已核/未核资源、旧Key/epoch/密码/owner与主密钥缺失，**When** 分范围读写/付费/worker放行，**Then** 各守独立隔离，次日仅解当日配额缺口，新Key不得早于cutover；恢复点内success仅原窗受控GET，未证范围无旧body，未知成本保留。
- **Given** 同包连续两次恢复，**When** T6负例/收尾，**Then** epoch不同且第一轮新凭据第二轮失效；保存snapshot/gap/真实丢失窗/耗时/确认人/失败和放行证据。未完成真实演练不得上线。

## Epic 9：用冻结验收与真实工程证据判定完成（F0/S7）

不因故事勾完即认为四场景完成；按原门槛保存全部结果。Story 9.1可在任意首次调优前独立执行，其余按S7前置。

### Story 9.1：首次调优前冻结原32题与金标（F0）

As a 评估者，I want 把开发题与冻结验收隔离，So that 调参不会污染整期成绩。

**依赖：** 无代码/无S6前置；需合法资料及标注完成。**来源：** 全部FR；NFR-5/6；SM-1–7；AR-11；AD-10/14；实施契约§3.6；PRD§7.1；运行R7-F0。

**Acceptance Criteria:**

- **Given** 首次任何基于结果选参尚未开始，**When** 冻结，**Then** 32题四场景各6可答+2不足、原件版本/hash、必要事实/原证据单元/判定规则/时间和访问记录齐，独立开发题分开；至少两领域/中英文、模拟脱敏身份及资料许可明确。
- **Given** P0图意题曾用于调优或冻结题暴露/来源变更，**When** 记录，**Then** 不再伪装未暴露留出题，保旧版/污染事实并另备留出验证，不删失败题/改分母。未冻结禁止调优，但不阻普通S0实现。

### Story 9.2：固定运行基线并登记性能成本门槛

As a 评估者，I want 在优化前保存B0及运行条件，So that 后续比较可复核且绝对目标不事后移动。

**依赖：** 8.4、9.1。**来源：** 全部FR；NFR-3/4/5/6；SM-2/7；AD-14；PRD§7/10；运行R6/R7。

**Acceptance Criteria:**

- **Given** 四场景开发检查与全部真实前置通过，**When** 固定环境/模型/数据/分块/检索合并/并发配置运行B0，**Then** 保存题目输入、全部输出/实见候选/引用/耗时/资源/call费用unknown，不删失败；最初12份四场景各3份样例的页/字/块/字节另报，不当客户容量。
- **Given** 首次资源/成本基线，**When** 在优化比较前登记绝对门槛与前提，**Then** 报median/导入/成功率/实际调用量，n<20不报有代表性P95、无价只报调用量不称免费；目标不可达留真实差距，不预填达标。

### Story 9.3：只用开发题选择优化并保留三方比较

As a RAG实施者，I want 按失败证据提出并验证一个改动假设，So that 改进或无收益都有真实工程依据。

**依赖：** 9.2。**来源：** FR-9/16；NFR-4/5；SM-7；AR-11；AD-10/14；PRD§7.1/8.2。

**Acceptance Criteria:**

- **Given** 独立开发题与B0失败证据，**When** 选择主要改动并锁方案，**Then** 调优只据开发题，不用冻结题逐题反馈选参；新增机制若越过主干边界先记录真实变更提案，不借故事重开已定决策。
- **Given** 锁定配置和同冻结材料，**When** 比B0/上一保留轮/本轮，**Then** 保存逐题/按场景质量、实见覆盖、引用语义、耗时资源、成本与全部失败/持平/退步，无收益也保留；原K/金标分母/权限不变，记录至[OPTIMIZATION_LOG.md](/E:/aaa-project/rag/OPTIMIZATION_LOG.md:1)。

### Story 9.4：执行原SM全部门并裁决四场景完成

As a 产品验收者，I want 对照原分母和独立权限套件逐项判定，So that 局部高分不能遮盖专项失败。

**依赖：** 9.3。**来源：** 全部FR/NFR；SM-1–7；AD-14；全部IA/G/AC及R01–R04；PRD§7.2；运行R7。

**Acceptance Criteria:**

- **Given** 同冻结32题，**When** 评判，**Then** SM-1≥21/24且各场景≥5/6，SM-2原必要单元合并覆盖≥85%按场景另报，SM-3事实引用直接支撑≥95%/定位打开100%，SM-4为8/8；人工核语义而非只验链接/JSON。
- **Given** 表格/扫描OCR/真正图意/冲突/版本五类关键题及独立权限套件，**When** 验SM-5/6，**Then** 五类各至少1通过、简单跨页表格人工一致；个人/团队/库/负责人/降级/移除/凭据/历史引用下载/输出前撤权专项全部通过且分母独立于32题。
- **Given** 预算失败/无事实/拒答或UI/恢复未过，**When** 汇总，**Then** 保失败/可答拒答数，SM-3分母0为N/A另列失败，不删题/扩K/漏成本或全面拒答刷分；SM-7含四场景Web/导入替换删除重试/API原始证据。任一原门失败不称整期完成，R01–R04按各最早门运行证据归档。

### Story 9.5：交付可复现材料与真实问题、理解记录

As a 项目所有者，I want 拿到可运行项目和有证据的解释材料，So that 我能核对实现与面试叙述。

**依赖：** 9.4；未通过时仍交付真实失败/差距记录，不标完成。**来源：** 全部FR/NFR；SM-7；PRD§8.2–8.4/10。

**Acceptance Criteria:**

- **Given** 实际代码/运行记录，**When** 交付，**Then** 配置样例/部署/API/启动恢复说明、关键权限版本单元测试和导入检索引用API集成测试的代码/命令/原始结果、样例许可/版本/评估及全部失败材料可复现；不包含秘密/业务正文公开泄漏。
- **Given** 至少一次真实异常与真实改进实验，**When** 整理，**Then** 异常有复现/证据/原因或未确认假设/处理/实际验证，持续写[DEVELOPMENT_ISSUES.md](/E:/aaa-project/rag/DEVELOPMENT_ISSUES.md:1)；无实际故障不伪造复盘，待具备前不通过。
- **Given** 用户方案核对/项目理解的实际参与，**When** 更新[INTERVIEW_PREP.md](/E:/aaa-project/rag/INTERVIEW_PREP.md:1)，**Then** 解释原理、实现选择/替代/失败验证/追问，并分别记录已讲解/待练习/能解释/缺口；AI实现不冒称用户独立编码，JD覆盖RAG与后续Agent边界明确。
