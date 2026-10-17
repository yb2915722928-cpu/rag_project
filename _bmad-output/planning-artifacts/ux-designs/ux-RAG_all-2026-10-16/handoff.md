# 给 Winston 与 Amelia 的 UX 交接

更新：2026-10-16。范围：设计文档与静态可视参考。设计的业务／视觉／验收决定均已落文档；没有需要实施者自行猜测或重新选择的关键规则。真实接入、资源、质量与恢复证据仍按既定切片执行，不能用设计核对结果代替。

## 阅读顺序与权威关系

1. [现行 PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:428)、[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:10)、[实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:9)：产品与跨模块业务真源、首次交付和停止点。[最终收敛](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:14)解释已关闭争议。
2. [EXPERIENCE](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md)与[DESIGN](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md)：分别确定行为与视觉，不能由示意图覆盖。
3. [逐页契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md)：实施某页时读取该页与共同契约；[验收契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md)给该页正负例与证明要求。
4. [覆盖映射](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/coverage.md)、[可视参考](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/INDEX.md)、[John 澄清](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/john-ux-clarifications.md)：分别检查闭合、定位布局和追溯口径；不另成可选业务政策。

上游约束优先；若实现中发现本 UX 与上游真有冲突，记录具体条款并修正 UX，不从两者任选。两份主文档各自职责内优先于 mock／文字线框／参考图；逐页契约与验收只细化这些规则。快照、旧稿和研究不是可替换政策。

## 不再需要猜的决定

| 方面 | 已确定结果 | 定位 |
| --- | --- | --- |
| 入口与范围 | 12类页面、业务／本人／团队／平台入口；单空间显式范围，默认enterprise仅组织输入与答复，不自动判类或强填未请求事实 | EXPERIENCE IA；逐页契约IA-01–12 |
| 权限 | 团队三角色、逐库范围、负责人职责分离；平台不自动读业务；邀请／转让／初始所有者资格分别写清 | 逐页契约IA-02／03／11／12；原PRD FR-1–5 |
| 资料与版本 | 资料标签／产品适用版本与不可变来源版本分名；生效版／候选／任务／清理／索引独立，正常完整资料自动发布 | 逐页契约IA-04–06；M2 |
| 恢复与费用 | 网络中断不等于业务失败；原Key恢复；查状态／到期继续核对／新本地处理／知情重交四动作的资格、副作用和停止点各明示 | 逐页契约G-05／06、IA-06；M5 |
| 答案与比较 | 首版非流式；不足／澄清／冲突与执行失败分开；对象×条件全格、四态、固定版本与证据门槛一致 | 逐页契约IA-07／08；M1／M3 |
| 来源 | PDF可靠物理页／区域、无区域回退；非PDF真实结构；历史重新授权，缺定位不能猜位置 | 逐页契约IA-09；M4 |
| 视觉 | 浅色、系统字体、深蓝操作、状态色对、明确尺寸／密度／断点；16组件与默认／悬停／焦点／禁用／错误规则 | DESIGN；五张可视稿 |
| 表单 | 初态、必填、错误定位、输入保留、危险确认与动作名称；凭证scope／到期／一次显密；三账分区 | 逐页契约共同规则与各字段表 |
| 验收 | 正负条件、页面结果、服务端副作用及证据分别描述；原SM／分母／F0／K=5保持 | acceptance；coverage |

## 允许自主决定的常规实现

Winston 可决定模块边界、接口与序列化的具体组织、持久化物理设计、部署实现和库选型；它们须满足已有业务不变量、安全约束及目标资源。Amelia 可决定路由地址、Vue组件拆分、Pinia内部结构、样式文件组织、网络封装、PDF渲染库、分页／虚拟化方式、合适的轮询间隔、自动化测试框架及fixture。页面可按合理复用实现，12类表面不等于必须12个URL或12个独立组件。

字段有限长度、密码技术规则等尚未被上游固定的技术政策，由架构定有效schema并让前端显示同一规则；不能变更合法角色、对比规范、授权、费用／计次语义或把未知限额当无限。部署生效的模型、文件、页数、时间和预算限制按同一配置展示和准入；不可把图中的模拟数字写死为运行配置。

不自行选择：新角色／跨空间混搜／逐份发布审批／通用OCR编辑器／自动付费重提／流式草稿／结果导出／工作流或Agent入口；这些不由“常规实现自由”授权。

## 仍须执行的证据，已有责任和触发

| 事项 | 责任与触发 | 未通过时 |
| --- | --- | --- |
| 实际格式、定位、图意、模型完整载荷与预算 | Winston定义探路及profile，Amelia在P0／对应切片用实际接入形成证据；S2／S3／S5按依赖消费 | 不把假件、纯文本或默认数值当通过；按原切片停止点处理 |
| schema与有效限制、组件版本 | Winston在架构与接入时锁定，Amelia在表单和请求准入中复用 | 缺有效限制阻止相应新受理；不猜无限或静默截断 |
| 4GB目标环境、重建、可信恢复与账本核对 | Winston落实方案与目标条件，Amelia在S6形成真实运行与反例证据 | 没有环境不称部署；隔离／unknown／gap按原契约保留 |
| 冻结题集与质量／权限专项 | F0首次调优前冻结；Amelia保留S7完整结果，按原SM判定，用户核对材料与理解 | 不删失败、不改分母、不以UI AC替代真实质量及权限成绩 |

这些是实施工作，不是待补访谈或未决产品规则。本轮设计不会提前填入“已接通／已上线／SM通过”。

## 交付检查记录

共同设计与John事实澄清中的纠偏已经回写：包括库负责人撤权只清该负责人授权、平台不凭运维身份重建任意库、既有团队转让对象必须已入队有效成员、双版本命名、未知任务禁用本地继续、知情重交明确复选确认。设计文件的机械核对与可视检查结果见[交付核对记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/handoff-check.md)。

本轮没有向Winston或Amelia所在聊天发送消息，也没有启动实现；本包已可作为他们下一阶段的输入。
