# RAG_all UX 首轮覆盖与验收映射

日期：2026-10-16；状态：UX 设计验收映射草稿。
本文件把已定产品行为映射到预期 IA 表面与动作，不是代码测试、产品评审或运行验收结果；页面名称是设计归位名称，不新增路由或功能。
规划通过、UX 覆盖、代码完成及真实运行验收分别记录；上游 ready/final 不代表 P0、SM 或目标部署已通过。
来源：[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:123)；[切片性质](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:9)；[完成门槛](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:102)。

## 1. 四场景与具名主角保持原文

| 编号 / 原名 | 主角与任务高潮 | UX 必须交付 | FR / SM |
| --- | --- | --- | --- |
| UJ-1 / SC-1：技术支持与故障排查 | 技术支持小林提交 v2 升级后连接超时的日志与环境；核对有序检查步骤的逐步依据 | 版本/环境不足先澄清；候选原因与适用条件明确；不自动执行命令 | FR-9/10/14；SM-1–4/6/7 |
| UJ-2 / SC-2：企业内部知识查询 | 新员工小周查出差审批人与材料；看清流程、材料及其版本依据 | 不虚构负责人；制度冲突并列双方，不擅判一份更有效 | FR-9/11/14；SM-1–4/6/7 |
| UJ-3 / SC-3：多文档对比与能力核验 | 售前小陈选产品 A、B 授权文档核验离线部署、审计、批量导入；逐格核验 | 全部对象×条件格、四态、适用版本与引用；未检索到不能变成“不支持” | FR-9/12/14；SM-1–7 |
| UJ-4 / SC-4：复杂产品手册问答 | 实施工程师小赵查型号 M2 的 E17 故障、部件位置及参数限制；对照原页/表/图核验 | 保留型号/版本/数值/单位/条件；结构/扫描/图意不能由纯文本代替 | FR-7/9/13/14；SM-1–7 |

唯一旅程来源：[PRD 四场景](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:62)，范围：62–67；不重命名、合并或重新访谈这些场景。

## 2. 权限动作简表

| 身份 / 职责 | 资料范围 | 允许动作 | 必须保留的反例 |
| --- | --- | --- | --- |
| 个人空间本人 | 仅本人个人资料 | 自行管理、查询、核验、本人限定只读凭证 | 不能分享给其他用户/团队；同团队所有者与平台身份无权读取 |
| 团队所有者 | 本团队全部库，由角色固有授予 | 团队设置、成员/邀请/角色、全部库维护/授权、转让/解散、撤销本团队凭证 | 退出/停用前须交接；转让后不再保有原角色全库权；不得读取他人个人空间 |
| 知识维护者 | 逐库获授权及本人负责库 | 创建库；获授权库内所有资料上传/更新/删除/校核/重处理 | 能改他人上传资料≠能管理非负责库授权/删整库；不能管理团队成员/角色 |
| 负责人职责 | 本人负责的库；创建者自动负责 | 在维护动作之外，管理该库授权/删除整库 | 不是第四种团队角色；所有者撤销原负责人该库访问时，同步接管负责职责，并清除该原负责人在该库的全部授权；原负责人不能凭创建者身份恢复访问。依据：[FR-3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:149) |
| 知识使用者 | 逐库授权范围 | 检索/问答/比较、原文/引用、单文件下载、反馈 | 不可改资料；库授权不能提升角色；仍有库读权的降级者仅可读本人受控任务状态 |
| 平台管理员 | 平台配置及必要运行元数据 | 创建/停用账号、创建团队并指定所有者、接入验证、存储/配额/运行 | 不自动获得业务读权、代登录或全局资料搜索；兼具团队身份仍按业务权限 |

来源：[角色总表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:109)，范围：109–119；[FR-1–3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:127)，范围：127–153；[平台](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:159)，范围：159–171；[凭证](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:177)，范围：177–189；[降级任务只读](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:289)。

## 3. 预期 IA 表面 / 动作覆盖

| 预期页面或内嵌表面 | 动作 / 可观察交付 | FR | 最早切片 / SM | 关键负例与不变量 |
| --- | --- | --- | --- | --- |
| 账号入口与本人设置 | 密码登录/退出/改密、有效身份反馈 | FR-1/4 | S1；SM-6/7 | 停用不能登录；Cookie+Bearer 整拒；失败不回退身份 |
| 空间切换与当前范围 | 个人/团队、显式库与可选文档选择 | FR-1/3/5/9/14 | S1→S3；SM-6 | 加入团队不自动获库权；任一越界目标整体拒；无权/不存在同边界 |
| 团队成员/角色/邀请 | 角色邀请、接受/撤销、移除/退出、所有权交接 | FR-2/3/16 | S1；SM-6/7 | 未接受/撤销邀请无成员权；维护者不可管理团队；所有者不可直接退出 |
| 知识库列表/权限 | 创建库、负责人、逐库授权、整库删除 | FR-3/8/16 | S1→S2；SM-6/7 | 非负责库维护权不等于授权管理；负责人被撤权不能恢复；所有者接管 |
| 文档列表/上传 | 上传前展示有效格式/大小/页数/批量/原件容量限制；逐文件受理 | FR-4/6/15 | S2；SM-5/6/7 | 坏文件/加密/超限不标就绪；批量单文件拒绝不回滚他项；替换先保留旧版容量 |
| 文档详情/候选/任务 | 生效版/候选/任务独立状态、错误/失败范围、重试/取消/放弃 | FR-6/8/14/15 | S2；SM-5/6/7 | 处理中不遮旧版可用；首次partial持续提示；不完整替换不覆盖；未PUT也可放弃 |
| 解析校核/来源对照 | 原件与提取标签、页/结构/表图/错误范围，普通程序校核自动发布 | FR-6/7/8 | S2最小→S5复杂；SM-2/3/5/7 | 无必需定位/向量不ready；无逐份审批；修正新候选，不原地改历史 |
| 问答工作区 | 企业/排障/手册输入、适用条件、完整四态答案、事实引用、反馈 | FR-9/10/11/13/14/16 | S3企业→S4排障→S5手册；SM-1–7 | 不猜根因/负责人/型号/单位；不执行命令；不静默删日志；首版不流式 |
| 多文档比较工作区 | 对象/条件/有效上限、完整四态矩阵、版本及逐格证据 | FR-9/12/14 | S4；SM-1–7 | 重复/空/超限/越界整拒；不漏格；未找到≠不支持；对象差异≠同格冲突 |
| 引用核验表面 | PDF物理页/可信bbox或无区域高亮回退；非PDF结构片段/授权原件 | FR-7/8/9/14 | S2来源→S3引用→S5复杂；SM-2/3/5/6 | 不编页码/坐标；定位损坏可识别；原版本可核验不参加新检索；每次重授权 |
| 会话/历史 | 单空间追问、原完成时间/版本、父轮次冲突提示、受影响答复隐藏 | FR-3/8/9/14/15 | S3；SM-1/3/6/7 | 跨空间新会话；一次一未终结轮次；旧证据不成为新上下文；失权不重读旧答 |
| 操作状态/网络恢复 | 未受理/已受理等待/完整结果/失败/失权重读区分，沿原操作恢复 | FR-4/5/14/15 | S1归属→S3操作；SM-6/7 | 丢回包同Key不重扣；失败/过期不自动新Key；切账号/空间/epoch挡迟到回包 |
| 个人程序凭证 | 本人限定单空间/库/只读动作/到期，创建一次显密、元信息/撤销 | FR-5/16 | S1；S3查询联调；SM-6/7 | scope与当前权交集；凭证不能写资料；GET operation继承原动作；citation独立许可 |
| 知识库重建状态 | 生效generation/目标profile、重建/取消/失败、维护迁移提示 | FR-4/8/15/16 | S6；SM-6/7 | 有写意图拒重建；guard中拒上传/替换/重处理但允许删除；旧attempt不解新guard |
| 平台接入/配额/运行 | 接入验证/可用性、原件容量/产品次数/实际成本分账，受控运行/审计 | FR-4/15/16 | S1基础→S6部署恢复；SM-6/7 | 不暴露正文/秘密；unknown不填0；满额保合法查看/删除；缺配置不称无限 |
| 受控恢复状态/维护入口 | 身份待核、范围隔离/分步放行、台账gap/未知费用/配额待核可识别 | FR-4/8/15/16 | S6；SM-6/7 | 不从旧owner自证；旧凭据全失效；未确认范围不开放；部分恢复不称全站恢复 |

IA动作来源：[最小入口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:308)，范围：308–344；[Web表面](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:269)，范围：269–279。
状态与校核来源：[页面动作矩阵](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:23)，范围：23–47；[上传终态](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:75)，范围：75–83。
错误/归属来源：[错误字典](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:350)，范围：350–372；[前端响应归属](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:395)，范围：395–401。
恢复来源：[恢复动作与放行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:276)，范围：276–300。

## 4. 切片核对顺序与停止点

| 切片 | UX覆盖核对与后续真实验收条件 | 来源 |
| --- | --- | --- |
| S1 身份与准入 | 所有私有页面首先具备账号/登录实例/空间/epoch响应归属、当前授权、容量/次数有限预留；安全台账从首次行为开始 | [S1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:45)，范围：45–51 |
| S2 导入闭环 | 不能等待问答UI才有原件/解析/定位/索引回看；需P0对应真实格式/来源/embedding通过，最小回看不代替复杂质量 | [S2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:53)，范围：53–59 |
| S3 基线查询 | SC-2、B0、K=5、引用/历史/API/操作恢复；真实预算/身份/终态闭环，开发题成绩不冒充冻结验收 | [S3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:61)，范围：61–67 |
| S4 排障与比较 | SC-1/SC-3、日志条件/检查顺序、完整矩阵和证据；零候选与失败分离；24路串行不伪造排队/进度 | [S4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:69)，范围：69–75 |
| S5 复杂手册 | SC-4及规则/跨页表格/OCR/真正图意人工核验；任何专项失效不以平均分抵消 | [S5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:77)，范围：77–83 |
| S6 重建与恢复 | 目标环境真实部署、重建/删除竞态、可信旧备份恢复反例；没有实际环境/凭据不得声称上线 | [S6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:85)，范围：85–91 |
| S7 固定验收 | 同冻结资料/题集/口径下B0/上一保留轮/本轮完整记录；权限、关键题、费用、失败均保留 | [S7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:93)，范围：93–104 |

S0/P0仍是独立工程及真实能力前置；未接入不是 UX 缺访谈，不得用假件成绩填补真实验证。F0必须发生于首次调优前，题目与开发题隔离。[先后关系/F0](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:15)，范围：15–25；[P0](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:37)，范围：37–43。

## 5. 原验收数值与分母锁定

| 原门槛 | UX稿、原型及后续实现不可降低的要求 | 来源 |
| --- | --- | --- |
| K=5 | 整次请求最终候选至多五块，全部子检索合并后同限；无邻块/全文/旧答暗加；原证据单元分母不随分块/裁剪改变 | [固定样例口径](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:324)，范围：324–326 |
| 32题 | 四场景各8题：各6可回答+2不足；共24可回答、8不足；首次调优前冻结题/资料/证据/事实/判定 | [题集](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:320)，范围：320–322 |
| SM-1：21/24且各场景5/6 | 必要事实齐全、无关键错误、结论引用一致；比较逐格不足不降低原任务门槛 | [SM-1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:334) |
| SM-2：≥85% | 24可回答题合并统计原金标必需证据单元，按场景另报；catalog存在不自动算命中 | [SM-2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:335) |
| SM-3：≥95%且定位100% | 事实性结论由所附引用直接支撑，语义人工核验；引用定位100%可打开，链接存在不等于支撑 | [SM-3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:336) |
| SM-4：8不足全部正确 | 正确不足/澄清/限定；不可把本可回答题的预算/依赖失败改标不足，不得全面拒答刷分 | [SM-4/反向约束](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:337)，及342行 |
| SM-5：五类专项各通过 | 表格、扫描OCR、图意、资料冲突、版本差异各至少一条；简单跨页表格人工一致；不可其他分数补偿 | [SM-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:338) |
| SM-6：独立权限全通过 | 个人/跨团队/库/非负责库管理/撤负责人/降级/移除/凭证/历史引用下载/输出前撤权；独立于32题报告分母 | [SM-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:339) |
| SM-7：工程实践证据 | 导入/替换/删除/重试及四场景Web流程，API原始结果、真实改进实验和异常复盘；退步/无收益如实保留 | [SM-7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:340) |

## 6. 首轮设计时必须看见的易错交互

1. 等待/断网/202保存原Key与规范输入，查原操作；成功丢回包不重生成，终态失败/过期只显式新操作；取消网络≠取消业务/退款。[网络恢复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:397)，范围：397–400。
2. 到期“继续核对”是新有界只读上下文；ready只观测；真正下载/校验/向量化/发布另显式新本地任务并重新核授权/guard/预算。[动作分界](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:127)，范围：127–133。
3. 首次partial可查已通过可定位范围；替换partial不能盖旧版；业务终态/删除生效与物理清理/容量释放分别显示。[候选边界](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:201)；[替换](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:219)；[容量](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:167)。
4. 比较每格四态与证据门槛不可被布局省略；全部真实零候选才正常不足，预算裁空/截断/缺格/非法引用整答失败，不交草稿。[比较四态](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:35)，范围：35–48；[失败分支](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:218)，范围：218–226。
5. 历史合法保留≠当前有权；切空间/账号/epoch后的迟到回包不重新灌入私有缓存，后台页恢复先核context。[响应归属](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:397)，范围：397–401。

## 7. 交付判读

- UX覆盖：后续对照体验文档逐行标记已承载/仍待设计；当前表格不宣称所有表面已有定稿或原型。
- 运行验收：由对应切片形成真实证据后再判断；本文件不填通过率、费用、P95、部署完成或专项通过成绩。
- 范围纪律：不新增逐份审批、OCR编辑器、自动付费重交、流式草稿、隐形查询队列或任意维度无停机迁移；不以视觉稿改写行为契约。
- 本轮只形成设计验收映射，未编码、未生成HTML、未启动独立评审。

本表使用现行主契约与切片；历史 baseline 不覆盖主文档。详细交互来源提取见 [source-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/.working/source-contract.md:1)。
本表覆盖范围不替代视觉偏好确认，也不把未规定的品牌色、字体或布局假称用户已定；UI组件系统已定为Element Plus，依据：[前端选型](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:107)。
