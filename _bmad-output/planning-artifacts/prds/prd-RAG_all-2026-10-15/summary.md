# RAG_all PRD 汇总

建立日期：2026-10-15；第二轮审查更新：2026-10-16。John 已将受托问题交由 Mary 回答并整理成产品基线。以下是需求和验收计划，不代表系统已经实现或指标已经达标。

**当前交接：产品基线可进入UX与架构设计。** 本轮新John/Winston独立检查并直接交流，只补设计交接导航，未新增产品问题或改变两轮IR/角色/场景/验收；本轮交接完成后等待用户启动下一阶段，不自动开始设计或实施。[本轮意见与最终版本复核](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md)与[PRD交接段](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md)说明具体边界，P0与运行验收均尚未执行。

**第二轮全面IR：PASS，可按已记录切片及前置门槛开始实施。** 原John B已复核实际完整合稿，四组问题全部关闭，剩余material规划阻塞0；独立初评、真实反驳/撤回和两题Mary原题追问均保留。最终范围见[IR报告](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md)及[原John B最终复核](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-b-final-ir.md)。[第一轮报告快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/baseline/previous-implementation-readiness.md)与前轮[需求定稿记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/finalization/completion-report.md)仅保留历史。账号、环境、实际接入和真实验收未自动通过。

## 1. 产品方向

建设支持用户导入不同领域资料的通用知识库，提供 Web 管理与问答界面，以及供后续 Agent 调用的 API。以 Python 为主，首版已确认后端 FastAPI＋PostgreSQL＋pgvector、前端 Vue 3＋TypeScript＋Vite，选择性抽取 WeKnora、MaxKB 模块并参考设计。本轮其余方案已通过四个大问题收口，取舍及真实问答见 [John—Mary 技术选择与对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md)，具体抽取和效果须实施验证。

Mary 与 TS 已完成 [PostgreSQL／Milvus／MongoDB 数据与检索比较](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/research-storage-comparison.md)。补充电脑 16 GB 后重新评估，用户已接受首版 PG＋pgvector 在服务器运行，电脑 Milvus 留为后续可选对照实验；4 GB 下的容量和表现仍须实测。

文档导入已确认采用 PostgreSQL 持久化任务＋独立 Python worker，初始同时处理一份文档，页面显示进度及失败原因，实现失败重试与重启后的任务恢复；相关恢复和幂等机制待实施验证。

定稿补齐的业务边界：候选不参加检索；首次部分可用需标明失败范围，不完整替换稿不覆盖旧版；PDF 保留物理页，DOCX 等无稳定页码时按实际结构定位。云端结果未知时显示待核对并查原任务，维护者可知情显式重交，只读凭证不获得写权限；自动程序校核不等于事实语义正确。

用户负责与 AI 核对实现方案和技术栈、理解 RAG 流程和项目；AI 负责实际编码、集成、测试及开发问题记录。预计用约半个月完成本期四类 RAG 场景，方案核对完成后在 AI 可用额度内推进，用于积累项目理解、求职和面对面面试，不计划现场演示；其他 Agent 能力随后扩展。

- 开发用 AI：两个 ChatGPT Plus 账号、一个阶跃星辰 Pro 账号，以及计划接入的 DeepSeek 中转 API；阶跃星辰 Pro 仅安排用户认为低重要性的开发任务。
- 项目运行／测试：千问小模型 API，实际使用前再定型号与接入，按需充值，当前不设定固定预算金额。

## 2. 空间与角色

| 身份 | 首版权限边界 |
| --- | --- |
| 个人空间本人 | 资料仅本人使用，不向其他用户或团队分享 |
| 平台管理员 | 创建账号与团队、指定初始团队所有者，管理模型、存储、配额和运行状态；平台身份不自动获得业务资料读取权 |
| 团队所有者 | 管理本团队成员、角色、全部知识库及授权，办理所有权转让和团队解散 |
| 知识维护者 | 创建知识库后自动负责，可管理负责库授权；可维护其他获授权库内的资料，但不能因此管理该库授权或团队成员 |
| 知识使用者 | 查询授权知识、对比文档、查看原文与引用、下载单个文件并反馈，不能修改资料 |

首版不开放自助注册或任意创建团队。所有者向已有账号发送站内邀请，接受后加入；普通成员入队不自动获得知识库访问权。维护者离队、降级或被撤销负责库访问时，由所有者接管，资料保留；撤权同步影响新问答、历史、引用、下载及凭证。

## 3. 四类 RAG 场景

| 场景 | 应交付的结果 |
| --- | --- |
| 技术支持与故障排查 | 根据版本、环境和日志给候选原因、检查顺序及引用；缺信息先澄清，不自动执行命令 |
| 企业内部知识查询 | 回答制度、流程、材料和有依据的负责人；缺失或冲突明确说明 |
| 多文档对比与能力核验 | 按条件逐格给满足、明确不满足、证据不足或资料冲突，附版本和证据；未找到不等于不支持 |
| 复杂产品手册问答 | 联合正文、规则及简单跨页表格、扫描 OCR、图意说明，保留型号、数值、单位及页码／表图定位 |

支持 Markdown、TXT、DOCX、文本型和扫描 PDF、中英文资料。新版本就绪前保留旧版，成功后切换；旧版仅供历史引用核验，版本对比使用分别导入的版本文档。删除先阻断访问，再关联清理。

查询限定同一空间内的授权知识库，不跨个人／团队或不同团队混搜。首版同步返回完整答案，不要求流式输出。程序 API 使用用户绑定、限空间与知识库、有期限且可撤销的只读凭证，提供检索、问答、对比、引用及本人导入任务状态。

## 4. 验收与工程证据

检索按用户确认的方式推进：先完成基础版，保留 B0，再根据实际问题逐轮优化。每次将配置、证据覆盖、回答结果、耗时、资源和费用的真实变化记录在 [OPTIMIZATION_LOG.md](/E:/aaa-project/rag/OPTIMIZATION_LOG.md)，形成可追溯的面试证据；无收益、退步和失败同样记录，具体优化手段按实测决定。

冻结 32 题：四场景各 6 条可回答、2 条资料不足。目标是可回答总体至少 21/24、每场景至少 5/6；不足题 8/8 正确表达不足；固定 K=5 的必要证据覆盖率至少 85%，事实结论引用支撑率至少 95%，引用定位可打开率 100%。表格、OCR、图意、冲突和版本差异各须有通过用例，权限专项独立测试且全部通过。

所有指标尚未实测，小样本结果不代表统计泛化。必须留下可运行代码、单元及集成测试、部署和 API 文档、原始评估记录、至少一次优化对比与异常复盘，以及上游来源、AI 实际改造和用户方案核对记录。真实开发问题统一写入 [DEVELOPMENT_ISSUES.md](/E:/aaa-project/rag/DEVELOPMENT_ISSUES.md)，包含定位、处理、验证和相关 RAG 原理，供用户回看。重试不能重复扣产品配额，但真实外部调用与费用必须如实记录。

问答配额按空间、Web／API 共用，生成前预留、正常答复结算；合规不足／澄清／冲突答复也计一次，拒绝与执行失败释放预留。同 ID 重试不重扣，归受理时上海日期；纯检索／引用／任务状态不扣问答次数，实际调用仍记账。备份须在干净隔离环境恢复匹配的 DB、原件与解析／引用资源、配置和密钥后，验证权限、删除状态与未完任务；备份文件存在不等于恢复通过。

用户此前未接触相关存储／检索技术，AI 负责维护 [项目理解与面试准备](/E:/aaa-project/rag/INTERVIEW_PREP.md)，先讲基础和项目取舍，再结合真实代码、实验与问题逐题练习。材料创建不等于用户已掌握，实现与实测结果形成后持续补充。

## 5. 实现顺序与未编造的信息

按“空间授权与导入 → 企业内部查询 → 故障排查 → 对比核验 → 复杂手册 → 统一评估”推进，四场景达到约定深度才算本期完成。

已确认 AI 负责实际开发、用户核对方案并理解项目，目标周期约半个月，按 AI 可用额度推进；Web、后端和 PostgreSQL／pgvector 部署目标仍为 4 核、4 GB Ubuntu。电脑内存用户提供 16 GB，本机读取 i7-12700H、RTX 3060 Laptop 6 GB；仅用于开发调试和前端构建，API 优先。Netcatty MCP、账号与证书条件实际接入前核验；千问模型按用途在使用前选，费用按需充值。本轮用户授权 John 提问、Mary TR 后 TS 受托选择；每个大问题完成再新建 Mary，同题追问找原 Mary，四题均已收口。没有现在必须询问用户的方案阻塞项，不追问每日工时或固定预算，不预填实现、理解或成绩。

Mary 已完成 TR／TS [文档解析研究](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/research.md)并交回 John；用户最终确认使用 MinerU 云端 API 上传解析，停止旧 OCR 排查与本地多引擎对照。轻量文件处理、原件与结果保存、分块和向量化仍由应用负责。API 凭证、具体请求、格式限制与 FR-7 的扫描／表格／图意／引用质量尚未接入验证，选型不等于已经跑通；细节见技术补充第 6.5 节。

本轮受托组合：模块化单体＋同步 SQLAlchemy 2／psycopg 3＋Alembic，PG 服务端 Cookie 会话／Argon2id／用户只读密钥与统一授权；任务租约／attempt、不可变候选版本与删除墓碑；结构分块与版本化 embedding、授权精确 B0、整请求最终五块及四场景 schema；Vue Router／Pinia／Element Plus 自建页面；Compose 部署 Nginx／API／worker／PG，受控文件、分离密钥、停写恢复备份、JSON 运行日志＋PG 审计／用量，pytest／真实 PG／Playwright 与独立评估。12 份公开／模拟资料是 AI 拟备测试起点，低并发／连接／文件限制是可调初值，所有接入、质量、容量、资源和成本仍待实际验证。

IR 追加选择：原件容量与物理磁盘保护分开、并发原子预留；诊断 request_id 与逻辑幂等 Key 分开，持久成功丢回包可重放且当前重新授权；显式目标整体校验、双凭据拒绝；逐库重建的写 guard／删除／失败释放、维度维护迁移；comparison.v1 全格四态和有限受理、最小校核／引用回看；恢复默认隔离、旧身份及凭据失效、新随机 epoch、独立现行受托与删除核验，未知账与上游任务不盲放行。实际政策、接口和切片分别在配套文件中，不依赖开发者临时发明。

## 6. 完整资料

第二轮补齐：未PUT/半传有有限期限/放弃/过期与一次清理释放，已完成重复PUT在预算下核实际hash而非只信声明；attempt隔离资产/稳定锁/停写证明，所有外发先持久意图和资格检查，迟到真实成本独立补账；库任务受理后归库继续，降级仍可合法只读本人状态。S2索引/最小校核、安全台账与前端归属已前移到首次需要它们的切片，模型总预算和截断分支同样写入现行契约；详情见当前IR，不作上游能力或运行成绩。

- [产品需求文档](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md)。
- [技术背景与验证交接](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md)。
- [讨论与决策记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md)。
- [技术选择与 John—Mary 真实对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md)。
- [PRD 定稿范围、复核与实施交接](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/finalization/completion-report.md)。
- [IR 实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md)、[纵向实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md)、[两位 John 对抗与最终 IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md)。
