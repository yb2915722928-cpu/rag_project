# PRD → UX 输入提取

提取日期：2026-10-16。范围仅为现行 PRD、summary 和 addendum；本文件不新增产品需求，不把既定事项重新列为访谈问题。实施契约、切片和最终收敛记录由其他输入摘要承接。

## 权威状态与产品目的

- PRD 现为 final、implementation-ready、readiness PASS，设计交接 ready；这表示规划准备度，不表示开发、API 接入、4 GB／恢复／质量验收已经完成。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:1)，范围：1–17。
- 产品是通用知识库，交付 Web 管理与问答及只读程序 API；用户须能找到依据、核验适用条件，并识别证据缺失与冲突。项目用于实际 RAG 理解及面试讲述，不计划现场演示。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:19)，范围：19–25。
- UX 只在既定用户、角色与范围内细化信息结构、页面和状态反馈，不借设计重选业务语义或降低验收。当前用户本轮已明确启动 UX，未授权编码。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:426)，范围：426–428。

## 已定角色与权限语义

业务岗位说明任务，团队角色决定动作，知识库授权决定资源范围，负责人职责另判；同账号可在不同团队拥有不同角色。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:48)，范围：48–60；[addendum.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:49)，范围：49–60。

| 身份 | 已确认范围与界面边界 | 来源 |
| --- | --- | --- |
| 个人空间本人 | 仅本人使用及管理，不向其他用户或团队分享 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:113) |
| 团队所有者 | 本团队全部库；成员／角色、授权、设置、转让与解散；每团队恰一名有效所有者，先交接后退出 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:114)；[FR-2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:133)，范围：133–141 |
| 知识维护者 | 逐库授权范围内维护全部资料；创建者自动负责，仅负责库可管授权和删整库；不能管成员／团队角色 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:115)；[FR-3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:143)，范围：143–149 |
| 知识使用者 | 授权库查询、对比、原文／引用、单文件下载与反馈；不能修改资料 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:116)；[FR-3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:147) |
| 平台管理员 | 建账号与团队并指定初始所有者，管理模型、存储、配额与运行；平台身份不授业务资料读取权，不提供代登录／全局资料搜索 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:117)；[FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:157)，范围：157–161 |

所有者向已有有效账号发站内邀请，接受后才入队；普通成员入队不自动获得库授权。维护者离队、降级或被撤负责库访问时所有者接管，资料保留；降级保留原逐库读权，失去维护／授权管理权。撤权影响新请求、等待输出、历史、追问、引用、下载及凭证；已显示或下载内容不追溯回收。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:135)，范围：135–153。

## 四场景：必须逐字沿用的名称、主角、目标与验收

这四位是 Mary 受托设计的代表性任务人物，并非真实用户访谈对象。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:35)，范围：35–37、62–67。

| 场景与主角 | 原始目标与行为约束 | 具体可检验结果 |
| --- | --- | --- |
| UJ-1 / SC-1：技术支持与故障排查。技术支持小林 | 在已登录团队空间选择有权库，提交 v2 升级后连接超时的日志及环境；得到适用条件、候选原因、顺序检查和逐步引用；缺版本／环境先澄清，证据不足不定根因，不自动执行命令。[原任务](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:64) | 不无条件推荐版本不匹配步骤；每步来源可核验；不声称执行或修复成功。[FR-10](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:241)，范围：241–245 |
| UJ-2 / SC-2：企业内部知识查询。新员工小周 | 在授权制度库问出差审批人和材料，得到有版本和出处的流程；负责人未提供明确缺失，制度冲突并列来源，不自行裁定有效性。[原任务](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:65) | 模拟出差制度可答有据流程／材料；不虚构负责人；冲突显示双方证据，样例标模拟或脱敏。[FR-11](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:247)，范围：247–251 |
| UJ-3 / SC-3：多文档对比与能力核验。售前小陈 | 选同空间 A、B 授权文档，核验离线部署、审计和批量导入；逐格四态：满足、明确不满足、证据不足、资料冲突，附版本／证据；未检索到不等于不支持。[原任务](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:66) | 有依据为满足，无依据为证据不足；矛盾来源显示冲突；Web/API语义一致。显式版本比较须分别导入为不同文档，不能选择替换后仅留作历史核验的旧版。[FR-12](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:253)，范围：253–261 |
| UJ-4 / SC-4：复杂产品手册问答。实施工程师小赵 | 查 M2 型号 E17 故障、部件位置及参数限制，联合正文、规则表格、扫描页、图意；保型号／版本／数值／单位／条件，定位页码／表／图；型号不明、单位缺失或解析不足则澄清／限定结论。[原任务](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:67) | 规则及简单跨页表格、扫描页、图意题均可核验；不拼接不兼容参数；纯文本问答通过不能宣称 SC-4 完成。[FR-13](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:263)，范围：263–267 |

## 确定的平台、组件基础与来源偏好

- 交付形态为 Web 和程序 API；前端 Vue 3＋TypeScript＋Vite，Router／Pinia／Element Plus 自建页面，参考两项目交互。这是现成 UI 基础，不必重新选择另一套 UI 系统。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:21)，范围：21–25；[addendum.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:107)。
- 资料支持中英文；本轮并未要求界面双语。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:77)。
- 首版同步完整答案，一次返回；等待／成功／失败与可见超时，不要求流式。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:233)，范围：233–237。
- 所读三份输入未定义品牌、主色、字体、圆角、阴影、密度、深浅模式、移动端优先或明确响应式断点。不可将 Element Plus 基础视觉自动说成用户个人偏好；视觉细化应标未定／沿系统基础，而非冒充已确认决策。

## 已定页面与反馈能力（供 IA 闭合）

- Web 必有：空间切换、知识库与资料管理、处理结果预览、问答与对比、原文／引用、反馈、凭证管理；团队／平台入口按角色；会话绑定单空间，换空间须新会话。[FR-14](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:269)，范围：269–279。
- 每问显式选单空间和非空、不重复的库／文档集合；“全部有权库”须解析为本次实际列表，任一无权或不可用目标整体拒绝，不能静默缩减再答。[FR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:179)；[FR-9](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:229)，范围：229–239。
- 资料元信息包括标题、所属库、版本和可选型号／适用条件；批量格式 Markdown、TXT、DOCX、文本和扫描 PDF；上传前显示部署生效的文件／页数／批量／容量限制，坏文件、加密／不支持／超限给明确原因。[FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:193)，范围：193–203。
- 处理状态：排队、处理中、待核对、就绪、部分可用（部分失败）、失败；显示失败范围、原因和处理／索引结果。上传开始、硬截止和进展超时对用户可见；网络重传不新建版本／重置期限。[FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:195)，范围：195–201。
- 资料界面分开当前生效版、候选、任务和索引重建状态；候选不参加查询。首次可用部分可发布时必须提示不完整；替换候选不完整不得覆盖旧版；新就绪前旧版仍可查，历史仅核验，不新检索。[术语](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:97)，范围：97–104；[FR-8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:215)，范围：215–223；[FR-14](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:273)。
- 校核页：原件、提取／结构内容、失败范围和位置对照。PDF 物理页从 1 起；可信区域高亮，无区域但可靠页则页预览并提示。非 PDF 用实际结构路径、准确提取片段和受控原件下载，不编造页码，不把提取内容冒充原件。不内建 OCR／富文本编辑器或 Word 预览服务；通过修订原件、允许的元信息／解析参数形成新候选。程序校核不等于语义正确。[FR-7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:205)，范围：205–213。
- 删除先停止检索／引用／下载，再清理；有权管理者看清理中／完成／失败并重试，失败不复活资料；历史引用提示来源已删除。[FR-8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:221)，范围：221–223。
- 外部解析结果未知：待核对、有限查询原任务、超阈值需处理。当前维护者可核对，或知悉可能重复调用／费用后显式重交；只读 API 仅本人范围内状态读取。原任务过硬期限后，继续核对与真正继续处理是不同操作，不能暗中新申请／上传。[FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:283)，范围：283–293。
- 浏览器断网或 Abort 不等于业务失败；等待／丢回包查原操作或同 Key 重传，不自动变新付费操作。单会话只受理一个未终结生成轮次。账号／登录／空间切换后旧异步回包不能写回清空的私有视图；失权历史回答可整体隐藏并说明原因。[FR-14](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:273)，范围：273–279。
- 对比受理初值可配置且可见：2–4 文档、1–6 条件、单条 256 码点、合计 1024、最多 24 子检索；空值／重复／超限／越权整体拒绝，不删格子。每受理格恰一次，四态及证据要求明确。[FR-12](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:255)，范围：255–261。
- 只读凭证绑定本人、单空间、指定库／动作且有期限，密钥只创建时显示，可列元信息与撤销；不提供上传、删除、成员或授权管理；平台身份不扩读权。[FR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:175)，范围：175–189。
- 用量展示区分“原件容量”与物理磁盘，以及共享每日问答计次与真实外部调用／费用。合规不足／澄清／冲突答复计次；受理拒绝／执行失败释放，纯检索／引用／任务状态不扣问答；同逻辑重放不重复扣。配额日期与展示用 Asia/Shanghai，未知费用不填零。[FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:165)，范围：165–173；[实施待补项](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:409)。

## MVP 范围与不扩展边界

必须交付账号／空间／团队／库授权／平台基础管理，文档上传、校核、索引、替换、删除、失败重试、引用，同空间问答／追问／对比及四场景、只读 API 与评估；中英文资料、至少两领域样例。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:71)，范围：71–77。

首版不含个人分享、自助注册／任意建团队、独立团队管理员、公开加入链接、申请审批、SSO、邮件／短信、文档级权限、跨空间混搜、整库批量导出、回收站、计费充值、自动存储迁移、企业自动同步、工具执行或其他 Agent 编排／长期记忆。非通用复杂原理图理解也不取消 SC-4 最低深度。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:79)，范围：79–86。

实施先空间授权导入→SC-2→SC-1→SC-3→SC-4→统一评估；先后顺序不是删减后三场景，四场景全达到要求才完成。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:348)，范围：348–361。

## 不得降低的验收

| 验收 | 已定门槛与 UX 含义 | 来源 |
| --- | --- | --- |
| 固定题集 | 32 题，四场景各 6 可答＋2 不足；首次调优前冻结，保留失败结果 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:318)，范围：318–328 |
| SM-1 | 总体至少 21/24，每场景至少 5/6；必要事实齐全，无关键错误，结论引用一致 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:334) |
| SM-2 | 整次请求最终 K=5 必要证据覆盖 ≥85%，不能扩块／加候选规避 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:324)，范围：324–326、335 |
| SM-3 | 事实结论引用支撑 ≥95%，引用定位可打开 100%，人工核语义 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:336) |
| SM-4 | 8/8 不足题均正确不足／澄清／限定，不编造 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:337) |
| SM-5 | 表格、OCR、图意、冲突、版本差异五类各至少一条通过，不能他项补分 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:338) |
| SM-6 | 隔离、撤权、降级、移除、越界、历史／引用／下载、输出前撤权等独立专项全通过 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:339) |
| SM-7 | 导入／替换／删除／重试及四场景 Web 主流程可完成；API 结果可复核；优化与异常有真实证据 | [prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:340) |

以上均尚未实测；不可少引用／事实、全面拒答、放宽权限、扩大候选或漏计成本换成绩。[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:330)，范围：330–344。

## 仅属 UX 未细化项

以下是所读输入没有规定的设计细化，不是新产品问题：品牌视觉及 tokens、页面布局与密度、导航呈现、各角色入口组织、组件交互细节、键盘与屏幕阅读器行为、响应式断点、深浅模式策略、动效及通知呈现、四场景输入分组与结果信息层次。须服从既定 Element Plus 基础、角色、范围、契约及上述验收；不得重新询问已定角色／场景／权限／计次／版本语义。

