# John — 产品上下文恢复与 UX 细化澄清

日期：2026-10-16。身份：John／产品经理；本轮职责是恢复既有产品记忆，给两位 Sally 提供可追溯的口径与细化清单。不是新一轮 IR、产品评审或重新访谈；未改变 PRD、实施契约、切片、角色、四场景及 SM，未编码或调用外部服务。

## 已恢复的上下文

- 目标是实际完成通用知识库 RAG 项目、理解工程实现并用于求职面试；通用指可导入不同领域资料。本期交付 Web＋用户绑定的只读程序 API；先 RAG 后 Agent，不执行工具／命令。依据：[产品目标](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:21)，范围：21–31、42–46。
- 用户直接确认的角色／逐库授权／个人不分享等规则，及 Mary 经用户委托形成的产品基线均已收敛。后来的记忆追加覆盖早期候选，不能把旧讨论当成待确认选择。依据：[决策来源](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:33)，范围：33–40；[记忆中的受托基线](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:49)，范围：49–61。
- 已读当前 PRD、汇总、完整实施契约与切片、PRD 记忆、最终收敛／John 最终复核及真实交叉讨论；并核对当前 UX 的 DESIGN、EXPERIENCE、逐页契约、覆盖及验收文件。最终收敛结论是可进入设计、无当时必须由用户裁决的产品阻塞；不等于真实接入、4 GB、恢复或质量已通过。依据：[最终 John 复核](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/john-final.md:15)、[本轮设计交接](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:426)，范围：426–428。

## 必须写清的细化项

优先级“先闭合／随后核对”只表示本轮 UX 编辑顺序，不是上游真实能力探路 P0，也不新增实施门槛。现有逐页契约和验收已覆盖下表多数事项，重点是消除不同文件、示意及按钮之间的歧义。

| 项目 | 已定规则与 UX 应明确的结果 | 优先级／边界 |
| --- | --- | --- |
| J-01 默认 SC-2 与通用定位 | `answer.v1` 的场景已为 enterprise／support／manual；enterprise 事实类型为流程／材料／条件／负责人，且“未请求项不强填”。默认 SC-2 可作为 Sally 的输入初态；应明说这不是系统自动判类，不强迫每题填齐企业字段或输出四类空栏目。不得新增 general 枚举、第五场景或任意事实类型承诺。依据：[输入场景](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:339)、[场景事实与未请求项](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:248)。 | 先闭合；不用重开产品选择。 |
| J-02 业务版本标签与技术版本 | 服务器生成的不可变 `version_id` 是证据身份；适用产品／资料版本标签是给人看的业务元信息，不能互相替代。表单、列表、矩阵及引用要分名呈现；业务标签缺失明示“未标注”，不从技术 ID 推断 v1/v2、型号或适用条件。版本差异比较仍须分别导入并标明版本的不同文档；被替换旧版仅供历史引用核验。依据：[资料元信息](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:195)、[版本及比较](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:217)，范围：217–219、255–257；[受理后技术 ID](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:81)。 | 先闭合；标签具体名称由 Sally 定，不能让用户填写技术 ID。 |
| J-03 邀请、所有权与平台建团队 | 邀请对象是已有有效账号，角色仅维护者／使用者，接受后才入队，入队不自获库权。平台新建团队从有效账号指定唯一初始所有者；已有团队所有权转让／办理变更，接任者限定本团队已加入且有效成员。旧所有者变维护者，仅保留原逐库／负责库范围。UX 要把“创建时指定”和“已有团队变更”分字段说明，不留“符合业务资格”给实施者猜。依据：[FR-2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:135)，范围：135–141；[转让资格收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/.memlog.md:60)。 | 先闭合；不新增邀请拒绝／自动过期、公开加入或申请审批政策。 |
| J-04 创建与管理表单 | 创建库应有名称、当前空间、创建者自动负责；创建团队有名称及有效初始所有者；邀请有已有有效账号及目标角色；转让有当前团队有效成员；平台账号有账号及初始密码；配额有目标空间、单位、日桶和有限值。编辑只呈现本期已有字段。角色、库访问和负责职责分开，不增任意负责人转派功能。依据：[创建与授权](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:145)，范围：145–153；[平台账号及配额](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:159)，范围：159–171。 | 先闭合；初态、必填、提交／未知结果、错误定位由 Sally 明确。 |
| J-05 未知解析与四类动作 | “查原任务”沿原关联；原业务到期后的“继续核对”是显式新建、初值120秒的有界只读核对，只用已知原上游 ID，不下载／向量化／发布，不续旧2小时任务；ready仅观测。“继续本地处理”须另显式新 job／attempt／deadline，重过当前资格／guard／预算，候选无效则新候选，复用须已验证兼容；不自动重交解析。“重新提交解析”才是可能重复调用／费用的知情显式动作，保留原关联；无ID／资产缺失保持未知或明确失败。依据：[原任务期限](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:117)、[核对与本地继续](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:123)，范围：123–133。 | 先闭合；按钮全称、状态提示及正负验收保持一致。 |
| J-06 凭证 scope 与到期 | 本人签发、单空间、指定库、五类只读动作逐一选择，必设到期，仅创建时显明文；有效范围为 scope 与本人当前权限交集。问答／对比操作 GET 继承原动作，不因 GET 绕权；citation 是独立许可，不强加 answers。团队所有者仅能撤本团队凭证，不能替别人创建或读明文。依据：[凭证规则](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:177)，范围：177–189；[程序动作枚举](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:333)。 | 先闭合；到期初态空、动作不预选等是 Sally 可决定的表单规范。 |
| J-07 反馈分类 | 上游仅要求“错误、缺失依据、引用问题”，并与答案／对象关联；普通用户不能读他人反馈／全局日志。当前三类足够，不添加满意度数值、自动改答案或工单处理流。单选／多选、可选说明、重复提交提示可由 Sally 统一决定并写入验收。依据：[FR-16](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:295)，范围：295–303。 | 随后核对；属于呈现闭合，不是缺访谈。 |
| J-08 空态、失败与权限 | 空集合仅在成功读取后使用；不得将请求失败、预算裁空、上游未知或失权说成资料不足。范围任一不可用整拒，不静默缩减；历史重授权，受影响答案可整体隐藏；正常不足／澄清／冲突计一次，执行失败释放预留但真实成本保留。依据：[配额及原操作](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:165)，范围：165–169；[预算失败分支](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:218)，范围：218–228；[前端归属](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:395)，范围：395–401。 | 随后核对；视觉图、页契约和 AC 不得说不同的话。 |

## Sally 可直接决定；Winston／Amelia 可自行落实

Sally 可在本轮委托下定浅色基线、颜色／字体／尺寸／间距、断点、12类页面的信息分组、默认选项、表单初态、确认措辞、危险动作的额外名称确认、空态／错误／焦点、对比矩阵与来源布局及可访问性目标。应写为“本轮委托形成的设计决定”，不是“等待用户逐项确认”，也不冒称可访问性已实测。现 [DESIGN 交付决定](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md)，已采用这一口径。

Winston／Amelia 可决定路由、组件拆分、服务端 schema 类与序列化、状态管理组织、网络封装、轮询、分页实现、数据库物理表／索引、测试框架与 fixture。管理字段的有限长度、密码技术规则等应在有效 schema 中给前端同一提示，不能据此重选合法角色、扩大范围或改原输入语义。常规细节无需再次问用户；页面依当前有限配置受理，未知不当无限。参见[逐页契约实现自由](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md)。

## 阶段验收与整期 SM 必须分开

- S1 先交身份／权限及前端回包归属；S2 已须交最小校核／来源／索引发布；S3 才新增 SC-2 与 B0 查询；S4 排障和比较；S5 复杂质量；S6 重建／部署／恢复；S7 全部固定验收。不能把最小回看推到 S5，不能以 S3 企业查询完成称四场景完成。依据：[切片依赖](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:19)，范围：19–25、45–100。
- 首次调优前 F0 冻结32题；四场景各6可答＋2不足，K=5是整次请求最终候选上限。SM-1 至少21/24且各场景5/6；SM-2 原必要证据分母≥85%；SM-3 引用语义支撑≥95%及定位100%；SM-4 不足8/8；SM-5 五类关键题各通过且跨页表人工一致；SM-6 独立权限全通过；SM-7 主流程/API/真实优化对比/异常证据。不能用界面 AC 取代这些分母。依据：[F0](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:17)、[SM-1–7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:330)，范围：330–344。
- UX 应交正负例及“预期页面＋服务端副作用＋证据”，当前运行状态全部“未执行”。现 [验收契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md)，已清楚区分设计核对与实际运行。P0账号／实际模型／目标环境等仍按原触发和停止点验证，无须现在再次访谈。

本轮澄清未发现需要重开既定产品选择的理由。两位 Sally 可据上述口径完成文档、静态设计参考及正负验收一致性，交由 Winston 和 Amelia 在现行不变量内设计和实施。
