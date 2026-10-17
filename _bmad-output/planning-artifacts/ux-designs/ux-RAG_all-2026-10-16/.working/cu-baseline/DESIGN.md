---
name: RAG_all
description: RAG_all 的 Element Plus 视觉首稿；以资料、证据和可辨识状态组织管理与问答界面。
status: draft
updated: 2026-10-16
sources:
  - ../../prds/prd-RAG_all-2026-10-15/prd.md
  - ../../prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md
  - ../../prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md
  - ../../prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md
  - ui-references.md
ui-system: Element Plus
decision-status: Sally设计提案；未获用户视觉确认
mode: light-proposal
colors:
  canvas: '#F2F3F5'
  surface: '#FFFFFF'
  surface-subtle: '#F5F7FA'
  text-primary: '#303133'
  text-secondary: '#606266'
  text-disabled: '#909399'
  border: '#DCDFE6'
  border-control: '#767A82'
  primary: '#409EFF'
  action: '#1D6CC0'
  action-hover: '#185BA1'
  action-active: '#144B85'
  on-action: '#FFFFFF'
  focus: '#1D6CC0'
  selection: '#ECF5FF'
  success: '#2F6F17'
  success-surface: '#F0F9EB'
  danger: '#B42318'
  danger-surface: '#FEF0F0'
  warning: '#8A5A00'
  warning-surface: '#FDF6EC'
  info: '#606266'
  info-surface: '#F4F4F5'
  source-highlight: '#FFF0B3'
typography:
  body:
    fontFamily: "'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif"
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  reading:
    fontFamily: '{typography.body.fontFamily}'
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.75'
    letterSpacing: '0'
  title:
    fontFamily: '{typography.body.fontFamily}'
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.4'
  section:
    fontFamily: '{typography.body.fontFamily}'
    fontSize: 16px
    fontWeight: '600'
    lineHeight: '1.5'
  meta:
    fontFamily: '{typography.body.fontFamily}'
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.6'
  code:
    fontFamily: "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.6'
rounded:
  sm: 2px
  md: 4px
  lg: 4px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 32px
  panel: 24px
  gutter: 16px
  page-narrow: 16px
  control: 32px
  touch-target: 44px
components:
  应用框架:
    background: '{colors.canvas}'
    foreground: '{colors.text-primary}'
    navigationBackground: '{colors.surface}'
    gap: '{spacing.panel}'
  范围选择器:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    border: '{colors.border-control}'
    focus: '{colors.focus}'
    radius: '{rounded.md}'
  资料表格:
    background: '{colors.surface}'
    headerBackground: '{colors.surface-subtle}'
    foreground: '{colors.text-primary}'
    divider: '{colors.border}'
    rowMinHeight: 48px
    cellPadding: '{spacing.3}'
  导入表单:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    gap: '{spacing.4}'
    radius: '{rounded.md}'
  处理状态条:
    background: '{colors.surface-subtle}'
    foreground: '{colors.text-secondary}'
    padding: '{spacing.3}'
    radius: '{rounded.md}'
  来源查看器:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    highlight: '{colors.source-highlight}'
    gap: '{spacing.gutter}'
    padding: '{spacing.4}'
  问题输入区:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    border: '{colors.border-control}'
    focus: '{colors.focus}'
    radius: '{rounded.md}'
  答案卡:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    fontSize: '{typography.reading.fontSize}'
    padding: '{spacing.panel}'
    radius: '{rounded.md}'
  对比矩阵:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    headerBackground: '{colors.surface-subtle}'
    divider: '{colors.border}'
    cellMinWidth: 220px
    cellPadding: '{spacing.4}'
  反馈条:
    background: '{colors.surface}'
    foreground: '{colors.text-secondary}'
    gap: '{spacing.2}'
  凭证面板:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    padding: '{spacing.panel}'
    radius: '{rounded.md}'
  用量面板:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    gap: '{spacing.gutter}'
    padding: '{spacing.panel}'
  管理表单:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    gap: '{spacing.4}'
    radius: '{rounded.md}'
  确认对话框:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    padding: '{spacing.panel}'
    radius: '{rounded.md}'
  状态反馈:
    background: '{colors.info-surface}'
    foreground: '{colors.info}'
    padding: '{spacing.3}'
    radius: '{rounded.md}'
  登录表单:
    background: '{colors.surface}'
    foreground: '{colors.text-primary}'
    gap: '{spacing.4}'
    radius: '{rounded.md}'
---

## Brand & Style

本稿为 **[Sally设计提案]**，用于用户评估，不代表用户已选品牌或批准实现。用户已说明暂无既定视觉偏好，允许参考 RAG 界面；已确认的只有上游功能范围与 Vue／Element Plus 基础。颜色、排版增量、布局和密度均按下文提案处理；角色、四场景和验收继续服从[现行 PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:428)。

界面以“能查资料、看依据、辨状态”为视觉重心：白色工作面、灰色分区、明确标题和少量功能色。结果正文留阅读空间，管理信息使用紧凑但可换行的表格。空间、范围和版本在当前工作区持续可见；成功样式只表达业务已确认的状态，不能靠视觉暗示候选已经生效。

继承 Element Plus 的组件形状、中性色、基础字号和控件尺度，只记录本产品的组合与可访问性增量，不引入第二套组件库。[ASSUMPTION] 首轮以桌面浏览器和浅色作为可评估基线，不新增深色模式承诺；未定义的系统视觉沿 Element Plus，不从其他产品复制品牌。视觉研究只用于比较布局，不改变产品权限或功能。

组合推导参见[官方 UI 参考](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/ui-references.md:1)：借 RAGFlow 的左会话/中答案/底输入维持连续阅读，借 MaxKB 的近邻来源和目录对照帮助核验，借 Dify 的阶段分区区分资料处理。它们分别落实到下文布局、来源查看器和处理状态条；不把参考图中的画布、Agent、语音或其他功能带入本项目。

本文件拥有视觉规则，[EXPERIENCE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md:1)拥有行为；将来线框、参考图与二者冲突时，以两份主文档各自职责为准。当前没有 HTML、已渲染原型或用户视觉定稿。

## Colors

下表区分系统继承与 **[Sally设计提案]**。系统映射于 2026-10-16 核对 [Element Plus 主题说明](https://element-plus.org/en-US/guide/theming)及[官方 theme-chalk 变量](https://raw.githubusercontent.com/element-plus/element-plus/dev/packages/theme-chalk/src/common/var.scss)，仅作为设计参考快照，实施时须对锁定版本复核。`colors` 为扁平 hex 对象；颜色角色不是权限或业务状态的替代品。

| Token | 值与用途 | 继承或增量 |
| --- | --- | --- |
| `{colors.canvas}` / `{colors.surface}` / `{colors.surface-subtle}` | 页面底 `#F2F3F5`、主工作面 `#FFFFFF`、表头/辅助区 `#F5F7FA` | 继承 EP 的 page / base / light fill |
| `{colors.text-primary}` / `{colors.text-secondary}` | 标题、事实、状态标签 `#303133`；元信息、帮助文字 `#606266` | 继承 EP primary / regular text；必要元信息统一用后者，避免浅灰 |
| `{colors.text-disabled}` | `#909399`，仅真正不可操作控件的弱化外观 | 提案；不可把失败原因、版本、时间、权限原因变淡 |
| `{colors.border}` / `{colors.border-control}` | `#DCDFE6` 结构分隔；`#767A82` 必须辨认的输入/选择边界 | 前者继承 EP；后者为可访问性提案 |
| `{colors.primary}` | `#409EFF`，保留 EP 默认蓝作非文字装饰或辅助选中标记 | 继承；不能直接作普通字号的白底链接或白字按钮 |
| `{colors.action}` / `{colors.action-hover}` / `{colors.action-active}` | `#1D6CC0` / `#185BA1` / `#144B85`；提交、主要链接和对应交互深度 | 提案；加深默认蓝，不把它声明为已选品牌 |
| `{colors.on-action}` / `{colors.focus}` / `{colors.selection}` | 白字 `#FFFFFF`；焦点 `#1D6CC0`；选中背景 `#ECF5FF` | 白与选中背景承接 EP；焦点为提案，选中仍配文字/边线 |
| `{colors.success}` / `{colors.success-surface}` | `#2F6F17` / `#F0F9EB`，就绪或“满足”标签 | 加深文字提案；浅底承接 EP success light-9 |
| `{colors.danger}` / `{colors.danger-surface}` | `#B42318` / `#FEF0F0`，失败、危险动作或“明确不满足” | 加深文字提案；依标题区分执行失败与正常业务结论 |
| `{colors.warning}` / `{colors.warning-surface}` | `#8A5A00` / `#FDF6EC`，待核对、部分可用或“资料冲突” | 加深文字提案；每处写明具体含义 |
| `{colors.info}` / `{colors.info-surface}` | `#606266` / `#F4F4F5`，“证据不足”、普通说明与未完成观测 | 提案；信息类不画成成功或错误 |
| `{colors.source-highlight}` | `#FFF0B3`，提取片段的当前引用位置 | 提案；原件区域用轮廓和定位标签，不涂掉原文字/图线 |

**对比目标 [Sally设计提案]：**普通文字、状态文字、帮助文字及链接至少 4.5:1；满足大字定义的标题至少 3:1；识别控件/状态所必需的边界和焦点指示与相邻色至少 3:1。可见焦点使用 `{colors.focus}` 的 2px 轮廓、2px 留白，并检验遮挡与键盘可见性。依据 [W3C 文字对比](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)、[非文字对比](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)与[可见焦点](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)。

以下是 hex 色值的静态相对亮度核算，不能当作页面已通过可访问性验收：正文/白底约 13.02:1，次文字/白底 6.11:1，主要操作白字/深蓝底 5.30:1，焦点/页面底 4.78:1，必要边界/白底 4.31:1；绿/红/棕/灰状态文字在对应浅底分别约 5.71 / 5.93 / 5.52 / 5.56:1。EP 原蓝/白底约 2.78:1、原 secondary text/白底约 3.08:1，因此不假定默认浅色系统自动合规；实现后还须核对悬停、选中、禁用、聚焦及组合背景。

## Typography

系统字体栈和 14px 基础继承 Element Plus；中文优先使用设备已有苹方/微软雅黑等字形，首轮不引入远程品牌字体。[Sally设计提案] 行高、阅读字号和字重形成产品排版增量。

| 角色 | Token | 用法 |
| --- | --- | --- |
| 主正文 | `{typography.body.fontSize}`，14px / 1.6 / 400 | 表单、表格、控制说明；颜色 `{colors.text-primary}` |
| 结果阅读 | `{typography.reading.fontSize}`，16px / 1.75 / 400 | 答案事实、排障步骤、手册解释；必要条件不缩小 |
| 页面标题 | `{typography.title.fontSize}`，20px / 1.4 / 600 | 每个工作区一个标题，避免展示型大字占用资料空间 |
| 分区标题 | `{typography.section.fontSize}`，16px / 1.5 / 600 | 当前生效版本、候选版本、本次任务、引用来源等组标题 |
| 元信息 | `{typography.meta.fontSize}`，13px / 1.6 / 400 | 版本、时间、定位和请求标识，仍用 `{colors.text-secondary}` |
| 日志/标识 | `{typography.code.fontSize}`，13px / 1.6 / 400 | 用户日志、错误码、任务ID；保留原始字符，长串可换行或局部滚动 |

文字可选择、可缩放。数值与单位保持相邻，型号/版本/条件不因窄屏被省略；表格标题可截断时必须有同等键盘可达的完整值。正文引用以有下划线的文本标记靠近事实，不用浅小上标藏起证据。粗体只强调事实层级或当前选中，不给推测结论制造“权威”外观。

## Layout & Spacing

**[Sally设计提案]** 使用 4 / 8 / 12 / 16 / 24 / 32px 节奏；相关标签与值间 8px，表单项间 16px，独立工作面内边距 `{spacing.panel}`，工作面之间 24px，局部分栏间距 `{spacing.gutter}`。32px 控件视觉高度沿 EP 默认，触控区域建议不小于 `{spacing.touch-target}`；放大点击范围不能覆盖邻接目标。

| 视口提案 | 布局和密度 |
| --- | --- |
| ≥1200px | 224px 左侧导航、56px 顶部空间/身份区；主区按内容伸展。问答中左区下部显示当前空间会话，中央答案、底部输入；阅读区建议 680–840px。来源需要对照且空间足够时在右侧并列，来源区建议 400px 起；不足以保持两边可读则转独立工作面 |
| 768–1199px | 导航折叠，正文优先；来源在独立工作面查看并保留返回上下文。资料详情的三组改纵向排列，不缩小字号 |
| <768px | [ASSUMPTION] 作为 Web 窄窗适配提案，16px 外边距，单列；管理表单逐项排列。来源/对比使用独立工作面，允许内容局部横向滚动，不承诺原生移动端 |

**资料详情的三栏：**“当前生效版本 / 候选版本 / 本次任务”各自独立有标题、标识、状态与时间；宽屏三栏并置，栏内先显示标题和关键状态，再显示详情。当前生效版可用中性主面配“可用于查询”的明确文字；候选为中性浅底并明示“不参与查询”；任务独立列阶段、错误、期限和动作。无候选也保留“无候选”，不用空白引导误解。清理与索引重建在所属组内独立行显示，不给整个文档一个混合状态。基础卡片内边距16px，组间24px；窄屏沿同顺序纵向排列。

**多文档对比：**矩阵用完整对象×条件二维结构，表头含文档标题与固定版本，首列为条件。单元格最小宽度220px，内边距16px、自动增高，正文使用14px且不裁事实；桌面可固定表头和首列，窄窗局部横滚并持续展示当前对象/条件。最多24格是可配置业务初值，不是允许视觉隐藏后续格子的理由。

**来源查看器：**宽屏原件和提取内容按同一定位并列；原件保持真实页/图比例，提取区使用阅读字号、16px 内边距。定位头部固定显示文档版本、页或结构路径、当前位置与回看限制；失败范围有文字清单。窄屏以明确标签切换原件/提取内容，不把二者都叫“原文”。没有可信区域只显示页级定位，非PDF只显示真实结构位置；布局不生成伪页码。

布局对应的[关键界面文字线框](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/wireframes/key-surfaces.md)包含 W1 问答与证据、W2 生效版／候选／任务、W3 完整对比矩阵、W4 来源校核。它们只说明区域及信息顺序，尚未渲染为 mock；本节的视觉规则仍为主文档。

## Elevation & Depth

继承 Element Plus 的浮层层级与默认轻阴影，不另造装饰性阴影体系。[Sally设计提案] 日常工作面以 `{colors.surface}`、`{colors.surface-subtle}` 和 `{colors.border}` 分区；答案、表格及版本栏不靠悬浮投影提升可信度。只有短时浮层和确认对话框使用系统默认阴影与遮罩；固定头部用边线分隔。

加载不通过闪烁大片渐变模拟。等待中的区域可显示系统加载指示和明确文字，未知进度不画伪百分比。减少动态效果时取消过渡，状态的文字、颜色和布局结果保持一致。

## Shapes

`{rounded.sm}` 为2px，`{rounded.md}` / `{rounded.lg}` 为4px，继承 EP 小/基础圆角；`{rounded.full}` 仅给小型状态标签或圆形标识，主表单和答案工作面不做胶囊形。[Sally设计提案] 一个工作面只保留一层边框，版本分栏用分隔和间距，避免层层卡片挤压事实。

图标沿 Element Plus 的一致线性图形，默认16px，并配文字标签；不能让图标单独承载“满足/明确不满足/证据不足/资料冲突”或危险操作。用户文档中的原图保持原样，不用装饰插画替代图意证据。

## Components

以下16项为与行为文档共用的组件名，都是已定能力的视觉组合。交互与权限以 [EXPERIENCE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md:1)为准；其余沿 Element Plus 基础样式。表内全部为 **[Sally设计提案]**。

| 名称 | 视觉结构与密度 | 重要状态外观 |
| --- | --- | --- |
| 应用框架 | 灰页面、白导航与主工作面；顶部持续显示当前空间/身份，活动入口有文字、选中边线和 `{colors.selection}`；按视口提案收拢导航 | 权限变化或隔离用有标题的状态区域，不显示空白工作面冒充无资料 |
| 范围选择器 | 标题含“当前空间”和已选库/文档；标签展示完整名称与数量；输入边界 `{colors.border-control}`，默认32px高，换行后增高 | 无选择有明确说明；不可用目标显示错误文字，不把目标悄悄移除；焦点轮廓 `{colors.focus}` |
| 资料表格 | 48px最小行高、40px表头、12px单元格内边距；标题与版本为主层，处理状态/失败范围为独立列，操作右对齐 | 文档状态与清理/重建分别标注；三栏详情沿上节布局；候选、旧版、生效版不共享一个“成功”徽记 |
| 导入表单 | 16px项间距；上传区先列生效格式/限制，再列逐文件结果与必要元信息；输入标签永久可见 | 容量不足/不支持等原因置于对应文件旁；部分文件受理不把整批画成全部失败或全部成功 |
| 处理状态条 | 浅底横条，阶段文字、任务标识和时间分组；12px内边距；详细错误按行展开，不挤在细进度线上 | 排队/处理中/待核对/就绪/部分可用/失败均有全称；未知不显示进度百分比；清理占用另写 |
| 来源查看器 | 版本及真实定位固定在内容上方；白底原件与提取内容分区，当前引用高亮且保留原图/表比例 | 无区域高亮、定位失败、来源删除/无权分别为明文；错误面不残留原件缩略图；失败范围可读 |
| 问题输入区 | 14px输入、16px项间距；问题与环境/版本/日志按场景分组，范围始终在同一工作区；主要动作使用 `{colors.action}` 白字 | 等待状态展示原操作信息；恢复连接与新请求的动作层级分开，不用旋转图标暗示已重提 |
| 答案卡 | 白面、24px内边距，16px/1.75事实正文；条件、结论、步骤、缺口、来源按内容顺序分段；请求/时间/版本用13px深灰 | 正常回答、资料不足、需澄清、资料冲突各有标题；依赖失败使用失败面，不能套“资料不足”样式 |
| 对比矩阵 | 固定版本表头、条件首列、≥220px格宽、16px内边距、自动增高；每格先状态、后理由/缺口/引用 | “满足”绿、“明确不满足”红、“证据不足”灰、“资料冲突”棕；每格全称+图标，不能只用色块/短横线；完整保留四态及各格 |
| 反馈条 | 答案后的次级区域，14px文字、8px间距；问题分类和已提交文字沿统一表单样式 | 已提交有文字确认，失败有原因；不覆盖原答案/引用，不用满意度颜色评价证据正确性 |
| 凭证面板 | 范围/动作/期限元信息优先；明文密钥为一次性独立区域，用等宽字体并允许长串安全换行；默认列表不展示秘密 | 创建、只显示一次、已撤销/到期均明示；撤销是有文字的危险动作，不靠红色小图标 |
| 用量面板 | “原件容量 / 产品问答次数 / 外部实际调用与费用”三组标题及单位；数值14px起，描述完整；不加未授权运营图表 | 原件包含预留和清理中；未知费用显示“待核对/未知”，不能0代替；上海日期明确，超额原因不混账 |
| 管理表单 | 继承EP标签/输入对齐；身份、授权对象和动作分组，16px项间距；角色与知识库范围分不同字段组 | 团队与平台入口视觉同系但标题明确；平台表单不出现由平台身份授予的正文预览；错误靠近字段 |
| 确认对话框 | 白面、4px圆角、24px内边距；标题写动作，对象与不可逆/费用影响为正文，确认/返回沿系统按钮结构 | 删除、撤权、转让、知情重交等使用各自完整措辞；高影响文字保持正文对比，不把后果缩为灰色脚注 |
| 状态反馈 | 12px内边距、14px正文，含标题、原因与当前可执行动作；系统提示按info/成功/警告/失败色对呈现 | 空、加载、失败、无权、断网、待核对和隔离均可用文字辨别；不能用空态插画遮住错误/权限原因 |
| 登录表单 | 单列白面，建议最大宽400px；永久标签、32px高输入、16px项间距；空间内容在认证完成前不展示 | 登录失败为表单级错误并保留非秘密输入；退出/切账号后的空白区不能残留上一账号标题或头像外的业务信息 |

组件内主要按钮视觉高度沿32px，必要时用系统40px大号；窄窗触控留出44px目标区域。表格内的文字链接使用 `{colors.action}` 并提供可见焦点；危险动作同时有文字和确认，不能借放大色彩把正常业务“不满足”变成执行错误。

## Do's and Don'ts

| 应做 | 避免 |
| --- | --- |
| 持续标明空间、范围、版本与结果性质 | 用候选处理成功暗示已替换生效版 |
| 普通文字/状态文字达到4.5:1，必要边界/焦点达到3:1并实测 | 把EP默认浅蓝、浅绿、浅红小字直接当AA通过 |
| 每种状态用完整文字，颜色和图标辅助识别 | 只靠红绿、空格、“—”或勾叉表达对比结论 |
| 来源保留真实页/结构/图表及版本，必要信息可换行 | 裁掉单位、条件、冲突一方或对比格来节省高度 |
| 管理信息紧凑、答案与来源留阅读空间 | 同一密度套在日志、长答案、扫描页和多格矩阵上 |
| 继承已定Element Plus并记录少量提案增量 | 为视觉效果换组件库或复制其他产品品牌 |
| 明示未知/待核对/清理占用及已确认动作 | 画伪进度、默认零费用或“自动恢复成功”成果 |
| 将首轮布局、颜色和主题标为设计提案 | 写成用户已确认、实现完成或可访问性已验收 |
