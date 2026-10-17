# IR 输入清单与判断范围

日期：2026-10-16；intent：readiness-only。读取冻结后的现行规划文档，不以历史目录文件数或旧PASS替代内容检查。

| 输入 | 当前作用 | IR检查 |
| --- | --- | --- |
| [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:1) | 既定四场景、角色/权限、FR-1–16、NFR-1–6、SM-1–7 | 本轮无业务范围/分母变更；技术规则须承接，不能下调验收 |
| [实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:1) | 请求、状态、三账、来源、预算、恢复与前端归属的现行跨模块边界 | R01–R04规则实写；架构摘要不得成为旁路 |
| [实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:13) | S0→S7、并行P0及首次调优前F0的纵向实施单元 | 已记录每片前置、交付、验收及停止条件；本次不生成冲刺跟踪 |
| [架构主干](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1) | 模块化单体、八模块唯一写者、14项共享不变量 | AD ID稳定，跨单元决定可执行，Deferred不遗漏跨界规则 |
| [共享契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:1) | C1–8协议、身份、当前权、来源、媒体及共享rate gate | 四个原反例能否在完全遵守规则时重现；共享字段/状态/时序有唯一选择 |
| [运行契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:1) | sender监督、停写/清理、四服务、缓存、恢复及运行证据门 | 正常/故障路径及R01–R04开放前验收完整；未测不冒称已通过 |
| [需求追踪](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md:1) | FR/NFR/SM、IA/G/23AC及切片到AD/C/R的承接索引 | 无孤立新规则或同步遗漏；§8补入本轮四项闭合 |
| [技术证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:1) | 冷启动seed证据和E5本轮HTTP/浏览器依据 | 本轮无新依赖/版本选择；标准支持、技术策略及未来实测分开 |
| [DESIGN](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md:1) | 视觉/组件规则 | 本轮不变；安全交互不引入未定义新产品表面 |
| [EXPERIENCE](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md:1) | 四场景与身份/状态/历史恢复体验 | 新登录、受控预览、恢复先遮蔽重核与后端一致 |
| [逐页契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:1) | 12个IA及共同G规则 | 首次登录可达、安全来源显示、缓存/回包归属无分叉 |
| [验收契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:1) | 原23AC及无编号R01技术补充 | 具体Given/When/Then与可观察后果；全部产品用例状态为未执行 |

现有交付形态为可拆成故事的纵向切片，尚无单独epic/story或运行冲刺文件；该事实不自动阻塞S0。IR检查开发者能否按现行单元实施而无需发明未记录的共享决定，不能仅因缺少某一文档类型生成缺陷。未来正式拆故事仍须引用本包的规则和对应验收，不能自行削弱。

P0依S0调用/限流/资产骨架及合法凭据，可与S1并行；S2依对应解析/来源/embedding实证，S3依真实完整预算，S5依真正图意，S6依目标环境/可信恢复，S7依原冻结材料与全部原SM。不存在要求S0先取得S7运行成绩的倒置前置。F0在首次调优前执行，不把普通功能实现等同调优。

独立rubric、对抗与技术镜头均已完成，material新发现0；根Winston已发布规划IR PASS，运行硬门仍未执行。12份实读设计文件与SHA记录在[review-manifest](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/review-manifest.json:1)，静态检查与产品运行证据分开保存。
