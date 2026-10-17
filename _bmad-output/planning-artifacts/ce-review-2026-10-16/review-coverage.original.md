复核结论：**现行需求覆盖与双向追踪可通过；必须修复的实质缺口 0 项，非阻塞歧义 1 项。** 未发现降低 K≤5、原金标分母、SM 质量门或独立权限门的条款，也未发现把尚未执行的运行验收写成已通过。

本报告只针对本次清单中的实际字节。全程只读，未修改文件、未启动其他智能体、未联网重选技术决策、未执行产品测试。

**实际读取范围**

直接读取以下 13 份现行输入全文，未以追踪矩阵摘要替代原文：

| 文件 | 实际读取范围 |
| --- | --- |
| [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:1) | 全文，1–428 行 |
| [实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:1) | 全文，1–409 行 |
| [实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:1) | 全文，1–109 行 |
| [架构主干](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1) | 全文，1–198 行 |
| [共享契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:1) | 全文，1–165 行 |
| [运行契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:1) | 全文，1–157 行 |
| [需求—架构追踪](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md:1) | 全文，1–176 行 |
| [技术证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:1) | 全文，1–76 行 |
| [DESIGN](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md:1) | 全文，1–333 行 |
| [EXPERIENCE](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md:1) | 全文，1–326 行 |
| [逐页契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:1) | 全文，1–228 行 |
| [UX 验收](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:1) | 全文，1–261 行 |
| [规划目录当前 IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md:1) | 全文，1–63 行 |

另外直接读取：

| 复核对象 | 实际读取范围 |
| --- | --- |
| [John CE 草稿](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:1) | 全文，1–697 行，41 个 Story |
| [Story 双向追踪](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/story-traceability.md:1) | 全文，1–222 行 |
| [审阅清单](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/review-manifest.json:1) | 全文，并重新计算全部 15 个文件的 SHA-256 |

15 个文件的实际 SHA-256 全部与清单一致。草稿 SHA-256 为 `e624fb4816d43d1d3ba1b02338d82b1cd441b07b0618481b1ac43db845d68512`；双向追踪为 `41516ece14be55c0e00e5b07eeb3d40cf55cd1c32767d1e618eb93b376acf890`。未用旧 baseline 或旧 IR 覆盖现行条款。没有查看文档链接所指的全部历史附件、原图或上游网站，因此本报告不扩张为这些材料的审阅签署。

**覆盖核对结果**

FR-1–16 与 NFR-1–6 均有实质承接。身份、团队生命周期、角色×逐库范围、本人凭证及三账落在 Stories 3.1–3.7；上传、程序校核、原子发布、替换、删除及三类恢复动作落在 Stories 4.1–4.5；B0、完整预算、原操作终态、历史与程序许可落在 Stories 5.1–5.6；SC-1/SC-3/SC-4 分别落在 Stories 6.1、6.2、7.1–7.2；重建、变维、目标部署与可信恢复落在 Stories 8.1–8.4。相应内容可从[故事正文](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:309)逐条核验，范围：309–636。

实施契约的主要实质边界并非只在来源编号中出现：单次 grant、迟到只补账、稳定 writer 锁及真实清理、两个全系统独立 gate、原 2h 截止、S2 首交索引/来源、完整预算与裁空失败、原动作 scope、两次新 epoch 可信恢复，均在相应 Story 的 Given/When/Then 中出现。具体见[基础执行故事](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:194)，范围：194–240；[查询预算故事](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:461)，范围：461–519；[恢复故事](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:625)，范围：625–636。

SM-1–7 保留原门槛：21/24 且各场景 5/6、原必要证据单元合并覆盖 85%、引用直接支撑 95% 与定位打开 100%、8/8 不足题、五类专项及独立权限全通过。冻结、防污染、开发题调优、B0/上一保留轮/本轮比较、真实异常复盘均有故事。见[Stories 9.1–9.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:642)，范围：642–697；对照[原 SM 定义](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:320)，范围：320–344，未见降级。

IA-01–12、G-01–12、原 AC-01–23、16 个同名组件及 UX-DR01–22 均能找到承接。16 个组件由 UX-DR02–17 对应，来源见[原组件表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md:89)，范围：89–106；草稿见[UX 清单](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:92)，范围：92–113。尤其[共同完成条件](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:174)明确要求运行原 UX AC 的完整正反例，并要求每个实际 Web 页面再验 G、无障碍、响应式和状态覆盖，因此不能把正文未逐字复写原用例当成遗漏。

R01–R04 均具体到可验证故事：

| 修复 | 实质承接 |
| --- | --- |
| R01 | [Story 1.3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:206)，范围：206–217：跨秒/分钟及部分写暂停、失联/崩溃、监督停发证明、随后 DB 上界和完整 W；[Story 1.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:231)阻断未合格真实外发；[Story 8.4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:633)承接旧包恢复 |
| R02 | [Story 3.1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:317)，范围：317–319：全新无 Cookie 登录、精确 Origin/JSON/固定头、会话/token 旋转、认证写拒绝负例；[Story 3.7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:391)设身份开放门 |
| R03 | [Story 3.2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:329)，范围：329–331，及[Story 4.3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:431)、[Story 5.4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:507)：设施、资源、历史分别真实浏览器验证，覆盖错误、条件头、bfcache、依赖重核和旧正文不闪现 |
| R04 | [Story 4.3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:430)：准确白名单 MIME、attachment、安全文件名、nosniff、已核 PNG/JPEG、含 HTML 的合法 TXT/MD、伪类型及恶意文件名负例，并阻资源开放 |

正向表分派的主责故事确有对应行为；反向 41 个 Story 均有现行来源，未发现无来源的新业务能力。正向表声明列的是首次实现/针对性验收主责，故部分反向来源没有逐一回列同一行，不据此判为追踪造假。见[正向表范围说明](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/story-traceability.md:3)及[反向表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/story-traceability.md:166)，范围：166–210。

**COV-01 — 凭证到期字段的 UI 初态存在源头歧义**

- **严重程度：P3，非阻塞建议；不是权限或有效期校验缺口。**
- **源条款证据：**[共享契约 C5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:101)写“技术最大365d、UI初值30d”；[逐页契约 IA-10](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:185)写“空，必填未来上海时区时间”。
- **草稿位置：**[Story 3.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:361)，范围：361–367，同时引用 C5、IA-10；验收只规定未来到期与现行 schema，未解释这两个初态。追踪表[反向对应行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/story-traceability.md:184)承接了同一组来源。
- **反例与影响：**开发者可以预填 30 天，也可以保持空值要求本人输入；两者都能满足草稿中的未来到期校验，却不能同时满足两份来源关于初态的字面要求。影响界面一致性及该字段初态验收，不扩大只读 scope，也不允许永不过期。
- **最小修正：**由来源维护者澄清“30d”是否仅为 schema 建议值，在 Story 3.5 中注明唯一 UI 初态及采用依据，并记录来源差异处置；不改变必须未来到期、有限最大期限及本人显式创建等既定边界。
- **误报风险：**如果项目已有未列入本次 13 份输入的明确裁决，规定 UX 字段初态优先且 C5 的 30d 不用于预填，则此项可关闭。当前草稿的一般职责分工能帮助推断，却未直接解释这组相反字面值，因此保留为非阻塞歧义，不升级为 material 缺口。

本轮未发现其他可证实的必须修复项。文档覆盖通过仅说明可以按现行门槛实施；所有产品运行状态继续保持未执行，依据[草稿状态](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:23)、[运行证据约定](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:176)及[当前 IR 的效力边界](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md:16)。
