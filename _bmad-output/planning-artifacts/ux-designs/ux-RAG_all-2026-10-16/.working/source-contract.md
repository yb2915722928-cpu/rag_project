# 现行实施契约与切片：UX 来源提取

提取日期：2026-10-16。用途：供 Sally 恢复 UX 上下文；这是来源提取，不是设计决策、评审结论或已实现能力。以主目录的现行实施契约与切片为准，不以 final-convergence 或 round2 的 baseline 快照覆盖主文档。

## 1. 来源与权威顺序

- 主契约 `status: final`、更新 2026-10-16，明确继承唯一 PRD，角色、四场景、K=5、主栈不变；不存在实现或实测结果。[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:1)，范围：1–10。
- 切片是可拆故事的实施单元，非已运行冲刺；“可开始”不等于 P0、部署、质量或资源已验证。[实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:9)，范围：9–27、102–104。
- 配套现行 UI 契约已注明第二轮修订服从主契约。比较规范真实文件为 `mary-m2/schema.md`，不是 `comparison-schema.md`；后者仅见历史 baseline，未用作现行依据。[UI 契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:3)，范围：3–5；[比较规范](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:3)，范围：3–5。

## 2. 角色、权限与渠道

| 约束 | UX 必须保持的行为 | 来源 |
| --- | --- | --- |
| 平台与业务身份分离 | 平台管理能配置账号、接入、容量/次数、运行/审计；不由此获得正文、他人历史或业务证据读取权。恢复操作者也不自动获得业务读权 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:268)，及 323、380 行 |
| 所有者/维护者/使用者沿用 PRD | 空间、成员、邀请、授权、转让和负责人接管依 PRD 当前权限；普通使用者无管理写入口；不新增 worker 产品角色 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:310)，范围：310–312；[任务权限](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:115) |
| 状态可读与动作可写分开 | 降级但仍有库读权者可读本人受控任务状态；不再可重试、取消、管理校核；当前维护者看维护范围必要任务/错误；退出/撤库权者不能读改 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:315)，范围：315–320 |
| Web Cookie / 程序 Bearer | 双渠道同时携带整拒，即使同一人；不能认证失败后回退为更宽身份；服务端决定身份/角色 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:16)，范围：16–20 |
| 用户程序凭证只读白名单 | 明文只创建时显示；空间/库/动作/到期来自本人当前权限。程序仅检索、问答、比较、引用、本人导入任务状态；不提供写任务动作、任意 GET 通行、Agent 编排 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:321)，及 329–333 行 |
| 资源安全边界 | 选择单空间及显式非空不重复库集合；任一对象无权/不存在/越界/撤权则整请求失败；不静默删目标，不泄露标题/数量/存在性。“全部有权库”先解析为本次实际列表 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:19) |

## 3. 必须承载的页面与组件能力

以下是入口能力清单，尚非已获用户确认的导航布局：

- 登录/退出/改密、本人上下文、空间切换、个人/团队/成员/邀请/逐库授权、转让/负责人接管；逐库文档列表及处理详情；本人只读凭证；平台账号/接入/限额/运行/审计。[入口清单](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:310)，范围：310–323。
- 单空间显式范围的检索、企业查询、排障、手册问答及多文档比较；操作状态/网络恢复、同空间追问/历史、受控引用与原件回看。[查询入口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:324)，范围：324–344。
- 文档详情固定区分“当前生效版本 / 候选版本 / 本次任务”，分别显示版本/任务标识、错误和失败范围；无候选明示“无候选”；重建另显示生效 generation 与目标 profile。候选处理中不得覆盖旧版仍可查询的事实。[UI 状态表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:23)，范围：23–36。
- 校核对照有原件/提取内容明确标签、页/结构路径、表格图像和失败范围；不是通用 OCR/富文本编辑器；修正通过修订原件或合法参数产生新候选，不原地改历史。[主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:171)，范围：171–176。

## 4. 状态、动作与恢复规则

| 状态域 | 状态 / 可执行行为 / 禁止误导 | 来源 |
| --- | --- | --- |
| 上传 | 成功路径 awaiting_upload → uploading → original_committed；到期/放弃为 expired/cancelled；cleanup_pending/blocked/cleaned 独立呈现，业务终态不等于空间已释放。未 PUT、半传也须有限终结；原 ID 到期只返回原终态，新上传必须用户明确发起 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:75)，范围：75–83 |
| 首次导入 | 排队/处理中且无生效版时暂不可查询；程序完整校核后自动发布，没有逐份批准按钮；首次 partial 只查询通过且可定位范围，并持续明示不完整/失败范围 | [UI 状态表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:27)，范围：27–29 |
| 替换 | 旧版仍查询；候选不混入答案；仅完整 ready 自动切换。不完整候选可看原件/提取/失败范围，并按状态重试、取消或修订重交 | [UI 状态表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:30)，及 36 行 |
| 外部未知 | 显示待核对及可能费用；先查原任务，不自动重交付费；知情重交须用户显式动作，不抹掉原关联 | [UI 状态表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:31) |
| 到期后继续核对 | 当前维护者显式创建有界只读 reconciliation；仅查原持久已知任务/合法费用接口，输出观测和成本，不下载/解包/发布/新解析，不续活原 job 或截止 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:127)，范围：127–131 |
| 真正继续处理 | 另一个明确动作，新本地 job/attempt/deadline，必要时新候选，重新过当前授权/guard/预算；可复用仍保留且验证兼容产物；缺资产明确失败，不能 ready/URL 即视为可发布 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:133) |
| 同维重建 | 旧索引继续读；上传/替换/重处理整拒并说明原因/重试入口，不能隐形排队；删除仍允许并令候选失效。失败/取消/过期保留旧索引。guard 未清不得前端按时间自放行 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:147)，范围：147–157；[UI 状态表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:32)，范围：32–34 |
| 删除/撤权 | 立即挡正文/原件/引用/图像/下载，清理失败不恢复访问；仍计占用直到确认清完。合法读权的当前维护者可看必要清理状态 | [主契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:109)，范围：109–121；[UI 状态表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:34) |

正常问答/比较操作状态分 reserved/running、succeeded、failed/failed_unknown、过期。执行中同键只读状态或重传；成功重新鉴权后原时间/原版本重放且不重复计次；失败同键只回原失败，主动新请求才新 Key；过期 410 不转新提交。[操作状态表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:49)，范围：49–67。

## 5. 计次、容量与等待

- 三本账展示语义分开：“原件容量”包括保留版本/失败候选/清理中及在途预留；产品问答按受理上海日期结算；供应方真实调用/费用或 unknown 独立保留，失败不等于供应方零费用。批量逐文件受理，容量不足拒整份；替换先为新候选完整预留，不能先删旧版。[容量与账本](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:28)，范围：28–39。
- 正常不足/澄清/冲突均为正常结果计一次；纯检索不扣问答；受理前拒绝或依赖/期限/结构/权限失败释放预留，真实调用照记。取消浏览器请求不是业务取消或退款。[生成结算](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:63)，范围：63–67；[前端恢复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:397)。
- 首版正常首次问答等待固定截止，不流式、不展示未校验草稿；重复进行中可 202。全查询共用 gate，当前保护初值 active≤2/用户≤1，拿不到槽立即429，无持久等待查询队列；比较最多24路串行。以上是未实测初值，不宜作为产品质量承诺或真实排队进度。[查询入口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:325)；[限流](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:256)，范围：256–260。

## 6. 答案、比较、历史、引用与 trace / 导出边界

- 普通结果四态为 answered/insufficient/clarify/conflict；按场景表达企业的流程/材料/条件/负责人，排障的候选原因/检查顺序/版本日志限制，手册的型号版本/步骤/参数数值单位/限制。必要内容完整回答或明确 gap/澄清；未请求项不强填；事实引用本轮证据，冲突列同条件双方，不无据裁决。[答案语义](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:236)，范围：236–250。
- 比较初值2–4个当前文档、1–6条件、单条256/合计1024 Unicode码点、至多24格；从同一有效配置取上限。空、重复、越界/无权、超限整拒，不裁/合并冒充完整。接收时固定对象文档版本/generation，展示保留输入顺序，每格恰好一次。[比较输入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:11)，范围：11–17、37。
- 比较四态：满足/明确不满足各至少一个直接证据；不足写具体缺口，可空证据；冲突至少两个不同且分属互斥双方的证据，同格证据都属该对象固定版本。对象A与B的差异不等于同格冲突；普通问答仍须报告跨文档同事实同条件冲突。[比较四态](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:39)，范围：39–48。
- 全请求最终最多五块；catalog只列模型实际看见的片段（可以有未被结论引用项），不能塞TopN、邻块、全文、被预算裁掉内容。零候选须确实完整检索成功后得到0，服务器不调答案模型，正常返回全部不足格；预算裁空、依赖失败、截断/缺格/非法引用都失败，不能改称不足。[实见证据/失败](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:218)，范围：218–228；[比较目录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:78)，范围：78–92。
- 首版 compact128 是生成表达档，不删对象/格/证据字段，不裁返回文字；模型超子契约整答失败。质量不够需新配置/重预算/原质量验证，不降门槛。[有限输出](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:232)，范围：232–250。
- 会话单空间，一次只受理一个未终结轮次，父轮次忙/过旧明确冲突；成功只追加一对消息；跨空间新会话。历史每次重授权，辅助最多最近两条当前有权用户问题/合计2048码点，旧答案/旧证据不作新证据。成功重放标原版本/时间，不冒充新查询。[会话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:339)，范围：339–344；[历史输入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:194)；[重放](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:57)。
- 引用通过服务端 citation ID 解不可变版本和受控资源。PDF可靠bbox则真实物理页高亮；仅可靠页则预览+准确片段并标“无区域高亮”；DOCX/TXT/MD用真实章节/段落/字符位置及片段/授权原件下载，不编物理页。定位/hash/缺资产明确失败，不跳猜测位置；切版不改旧映射，删除立即挡访问。[引用回看](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:40)，范围：40–47。
- 本组来源未定义面向业务用户的模型思维链/推理 trace 视图、逐token流或比较结果CSV/PDF/JSON导出动作。已有可追溯字段是request/operation ID、原时间、执行快照、catalog及受控错误；不能把内部 budget_snapshot/普通日志当私有正文出口。安全台账独立导出是维护/恢复能力，不等于比较结果导出；结果导出是否已由 PRD 排除或允许交由 PRD 提取核对。[公共响应](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:344)；[内部预算快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:252)；[安全台账导出](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:270)。

## 7. 错误与前端响应归属

- 至少区分尚未受理、已受理等待、正常不足/澄清/冲突、业务失败/未知成本、成功但当前无权重读；不能浏览器超时即自动付费重提。错误按code/retry_mode决定：none、same_key_or_status、new_operation、manual_reconcile；该模式不是自动付费授权。[前端状态](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:399)，范围：399–400；[错误恢复模式](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:372)。
- 原件容量/文件限制/产品次数/并发分别解释；比较输入、模型输入/输出预算、上下文证据裁空、模型预算未证、截断、依赖故障、定位错误、epoch变化、存储压力及恢复隔离分别呈现可识别状态，不能一个“证据不足”抹平。[最小错误字典](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:350)，范围：350–372。
- 所有私有异步工作记录账号、登录实例、空间、epoch、适用会话/父轮次及operation/candidate。退出/换账号/切空间/确认epoch变化清私有缓存并递增代次；回包落视图前再核归属，Abort只是尽力。后台标签页恢复先取context并重核当前授权，不自动恢复正文；旧epoch/Key不可自动换新重送。[前端归属完整条款](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:395)，范围：395–401。
- 备份恢复旧会话/凭证作废、账号先unverified；只向已独立核验且有范围权者展示隔离/配额核对细节；普通重启不换epoch。逐范围开放不得称全站恢复，未知费用/gap保留。[恢复放行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:276)，范围：276–300；[隔离错误边界](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:368)，范围：368–370。

## 8. 切片到 UX / 验收的映射

| 切片 | UX 应交付的可观察行为 | 验收映射 / 来源 |
| --- | --- | --- |
| S0 / P0 | 工程/能力验证不假扮业务功能已通过；配置、未知成本、资源/定位问题可识别；P0是隔离样例探路，不暴露未完成鉴权业务入口 | FR-4/15/16、NFR-3/5/6；四场景最小完整载荷及格式/图意/来源/目标资源探路。[S0/P0](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:29)，范围：29–43 |
| S1 | 身份/空间/角色/库授权/凭证/计次容量；所有私有异步响应归属与上传意图有限终态从此开始 | FR-1–5、NFR-1/2/6、SM-6基础；权限/转让/撤权、双凭据、混合越界、并发最后配额。[S1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:45)，范围：45–51 |
| S2 | 无问答UI也能导入→看原件/解析/定位/索引→失败重试→完整发布；生效/候选/任务分栏及最小来源回看立即具备 | FR-6–8/15、NFR-1/2/6、SM-5/6/7导入部分；partial、不完整替换、上传/删除/清理/未知/重启竞态。[S2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:53)，范围：53–59 |
| S3 | SC-2企业查询、B0/K=5、引用、同空间追问/历史、只读API、原操作恢复与迟到回包隔离 | FR-5/9/11/14/16、NFR-1/3/4、SM-1–4开发检查；合法不足与依赖失败分开，失权不重放，不重复调用/扣次。[S3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:61)，范围：61–67 |
| S4 | SC-1排障环境/版本/日志、候选原因和检查顺序；SC-3完整比较矩阵与证据目录 | FR-9/10/12/14、NFR-1/4、SM-1–5开发题及SM-6；不执行命令、不把候选说定论、不把未找到说不支持、零候选全格。[S4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:69)，范围：69–75 |
| S5 | SC-4复杂手册、表格/OCR/真正图意、型号版本参数限制、人工对照；扩展S2回看而非推迟基本回看 | FR-7/9/13/14、SM-1/2/3/5/6；数值单位/表头行列/连接依据、无bbox回退、非PDF不编页、修正新候选。[S5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:77)，范围：77–83 |
| S6 | 同维重建/异维维护边界、目标部署、可信恢复/隔离/逐范围放行/真实账核对 | FR-3/4/8/15/16、NFR-1–6、SM-6/7；guard/并发删除、旧凭据失效、未核范围拒绝；无环境不声称上线。[S6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:85)，范围：85–91 |
| F0 / S7 | 首次调优前冻结32题及金标；四场景和关键题独立过关；结果/权限故障恢复/资源实际费用证据完整，不隐藏失败 | FR-1–16、NFR-1–6、SM-1–7与PRD8.2–8.4；开发题调优、原分母不改、优化退步也保留。[F0](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:17)；[S7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:93)，范围：93–104 |

## 9. 已确认来源性质与 UX 未定项

1. 契约明确这些是已接受方向、受托TS选择及两轮IR现行整合，并声明不替换既定角色/四场景/验收。这里不把受托可调保护初值说成用户逐项实测确认，也不重新访谈已定业务政策。[基线声明](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:10)，及 14、59、186 行；[UI来源性质](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:3)。
2. 本组来源没有指定品牌/颜色/字体/圆角/密度、既有UI组件系统、移动端支持范围、整体导航及关键页面精确布局。只能把它们标为待设计/待确认，不能伪装从上游继承；具体已定视觉/终端偏好由 PRD/最终收敛或用户其他证据核对。
3. 部署/真实账号/模型、有效配置与限额、实际图意/资源成绩、备份留存与可接受丢失窗口仍是后续执行登记事项，不是本次 UX 必须重新询问的产品选择。页面应能承载配置未证、能力不可用、unknown和隔离；不编数值成果。[探路](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:39)，范围：39–43；[恢复登记](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:300)。
4. 不新增：逐份发布审批、通用OCR/富文本编辑、自动重交付费、草稿流式、隐形查询队列、任意跨空间会话、平台业务越权、任意维度无停机迁移、模型思维链展示、比较结果导出承诺。最后两项在本组来源无授权，须与 PRD 范围核对后表述为“不在首期”或待决，不能只凭缺席自造全局禁令。
