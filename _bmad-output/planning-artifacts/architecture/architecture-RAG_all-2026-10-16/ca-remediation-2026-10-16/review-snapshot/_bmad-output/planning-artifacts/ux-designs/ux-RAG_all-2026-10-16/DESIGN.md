---
name: RAG_all
description: RAG_all 的 Element Plus 视觉交付契约；以资料、证据和可辨识状态组织管理与问答界面。
status: final
updated: 2026-10-16
sources:
  - ../../prds/prd-RAG_all-2026-10-15/prd.md
  - ../../prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md
  - ../../prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md
  - ../../prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md
  - ui-references.md
ui-system: Element Plus
decision-status: 两位Sally在用户明确委托下作出的交付设计决定
mode: light
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
    navigationWidth: 224px
    headerHeight: 56px
    mainMinWidthWithSource: 640px
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
    sideWidth: 400px
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
    criteriaWidth: 184px
    cellMinWidth: 240px
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

本稿为 **[Sally交付决定]**：用户本轮明确委托两位 Sally 将 UI 完善到 Winston 和 Amelia 不需猜关键规则的程度，因此本文件的浅色、字体、布局、密度和状态增量是可直接实施的规范，不再是等待选择的首稿假设。这是委托下的设计决定，并非声称用户逐项确认，也不启动编码。角色、四场景和验收继续服从[现行 PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:428)。

界面以“能查资料、看依据、辨状态”为视觉重心：白色工作面、灰色分区、明确标题和少量功能色。结果正文留阅读空间，管理信息使用紧凑但可换行的表格。空间、范围和版本在当前工作区持续可见；成功样式只表达业务已确认的状态，不能靠视觉暗示候选已经生效。

继承 Element Plus 的组件形状、中性色、基础字号和控件尺度，只记录本产品的组合与可访问性增量，不引入第二套组件库。交付基线为桌面优先的响应式 Web、浅色和系统字体；首版不增加主题切换。未定义的系统视觉沿 Element Plus，不从其他产品复制品牌。视觉研究只用于比较布局，不改变产品权限或功能。

组合推导参见[官方 UI 参考](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/ui-references.md)：借 RAGFlow 的左会话/中答案/底输入维持连续阅读，借 MaxKB 的近邻来源和目录对照帮助核验，借 Dify 的阶段分区区分资料处理。它们分别落实到下文布局、来源查看器和处理状态条；不把参考图中的画布、Agent、语音或其他功能带入本项目。

本文件拥有视觉规则，[EXPERIENCE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md)拥有行为；将来线框、参考图与二者冲突时，以两份主文档各自职责为准。关键屏由静态 SVG 与 PNG 示意承载；它们是设计参考，示例资料不是运行结果。本文提供可直接实施的视觉规则，未实现产品。

## Colors

下表区分系统继承与 **[Sally交付决定]**。系统映射沿用本轮已核对的 [Element Plus 主题说明](https://element-plus.org/en-US/guide/theming)及[官方 theme-chalk 变量](https://raw.githubusercontent.com/element-plus/element-plus/dev/packages/theme-chalk/src/common/var.scss)，作为系统来源；本文的字面 token 值为交付值，实施时锁定组件版本并保持这些结果。`colors` 为扁平 hex 对象；颜色角色不是权限或业务状态的替代品。

| Token | 值与用途 | 系统来源或交付增量 |
| --- | --- | --- |
| `{colors.canvas}` / `{colors.surface}` / `{colors.surface-subtle}` | 页面底 `#F2F3F5`、主工作面 `#FFFFFF`、表头/辅助区 `#F5F7FA` | 继承 EP 的 page / base / light fill |
| `{colors.text-primary}` / `{colors.text-secondary}` | 标题、事实、状态标签 `#303133`；元信息、帮助文字 `#606266` | 继承 EP primary / regular text；必要元信息统一用后者，避免浅灰 |
| `{colors.text-disabled}` | `#909399`，仅真正不可操作控件的弱化外观 | 交付增量；不可把失败原因、版本、时间、权限原因变淡 |
| `{colors.border}` / `{colors.border-control}` | `#DCDFE6` 结构分隔；`#767A82` 必须辨认的输入/选择边界 | 前者继承 EP；后者为可访问性增量 |
| `{colors.primary}` | `#409EFF`，保留 EP 默认蓝作非文字装饰或辅助选中标记 | 继承；不能直接作普通字号的白底链接或白字按钮 |
| `{colors.action}` / `{colors.action-hover}` / `{colors.action-active}` | `#1D6CC0` / `#185BA1` / `#144B85`；提交、主要链接和对应交互深度 | 交付增量；加深默认蓝，不把它声明为已选品牌 |
| `{colors.on-action}` / `{colors.focus}` / `{colors.selection}` | 白字 `#FFFFFF`；焦点 `#1D6CC0`；选中背景 `#ECF5FF` | 白与选中背景承接 EP；焦点为交付增量，选中仍配文字/边线 |
| `{colors.success}` / `{colors.success-surface}` | `#2F6F17` / `#F0F9EB`，就绪或“满足”标签 | 加深文字增量；浅底承接 EP success light-9 |
| `{colors.danger}` / `{colors.danger-surface}` | `#B42318` / `#FEF0F0`，失败、危险动作或“明确不满足” | 加深文字增量；依标题区分执行失败与正常业务结论 |
| `{colors.warning}` / `{colors.warning-surface}` | `#8A5A00` / `#FDF6EC`，待核对、部分可用或“资料冲突” | 加深文字增量；每处写明具体含义 |
| `{colors.info}` / `{colors.info-surface}` | `#606266` / `#F4F4F5`，“证据不足”、普通说明与未完成观测 | 交付增量；信息类不画成成功或错误 |
| `{colors.source-highlight}` | `#FFF0B3`，提取片段的当前引用位置 | 交付增量；原件区域用轮廓和定位标签，不涂掉原文字/图线 |

**对比目标 [Sally交付决定]：**普通文字、状态文字、帮助文字及链接至少 4.5:1；满足大字定义的标题至少 3:1；识别控件/状态所必需的边界和焦点指示与相邻色至少 3:1。可见焦点使用 `{colors.focus}` 的 2px 轮廓、2px 留白，并检验遮挡与键盘可见性。依据 [W3C 文字对比](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)、[非文字对比](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)与[可见焦点](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)。

以下是 hex 色值的静态相对亮度核算，不能当作页面已通过可访问性验收：正文/白底约 13.02:1，次文字/白底 6.11:1，主要操作白字/深蓝底 5.30:1，焦点/页面底 4.78:1，必要边界/白底 4.31:1；绿/红/棕/灰状态文字在对应浅底分别约 5.71 / 5.93 / 5.52 / 5.56:1。EP 原蓝/白底约 2.78:1、原 secondary text/白底约 3.08:1，因此不假定默认浅色系统自动合规；实现后还须核对悬停、选中、禁用、聚焦及组合背景。

## Typography

系统字体栈和 14px 基础继承 Element Plus；中文使用设备已有苹方/微软雅黑等字形，不引入远程品牌字体。[Sally交付决定] 行高、阅读字号和字重形成产品排版增量。

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

**[Sally交付决定]** 使用 4 / 8 / 12 / 16 / 24 / 32px 节奏；相关标签与值间 8px，表单项间 16px，独立工作面内边距 `{spacing.panel}`，工作面之间 24px，局部分栏间距 `{spacing.gutter}`。32px 控件视觉高度沿 EP 默认，细指针控件32px；粗指针使用40px视觉高度、至少 `{spacing.touch-target}` 目标区域及8px间距。放大点击范围不能覆盖邻接目标。

| 可用视口宽度 | 确定布局 |
| --- | --- |
| ≥1440 CSS px | 224px导航、56px顶部区、24px内容内边距；主结果区与400px来源区间隔24px，主结果至少640px。来源关闭时主区扩展，答案正文行宽上限840px并居中，不强制管理表格窄列。导航下部承载当前空间会话，不额外增加第二条常驻会话侧栏 |
| 1200–1439 CSS px | 保留224px导航与24px内边距；结果单区，来源转独立可返回视图，不能压缩出小于640px的主区。资料详情三区可并列，每区至少256px |
| 768–1199 CSS px | 导航改224px抽屉，由顶部可读按钮打开，遮罩不作为唯一关闭方式；主区24px内边距；资料详情三区纵排，来源独立视图，顶部保留空间与当前页面标题 |
| <768 CSS px | 导航抽屉宽度不超过视口减32px；主区16px内边距，表单单列。来源在完整独立视图以“原件／提取内容”标签切换；对比矩阵局部横滚、保留所有格。320 CSS px或200%缩放时控制区可换行，不能裁主操作／错误／条件 |


**资料详情的三栏：**“当前生效版本 / 候选版本 / 本次任务”各自独立有标题、标识、状态与时间；≥1200px三区并置，栏内先显示标题和关键状态，再显示详情。当前生效版可用中性主面配“可用于查询”的明确文字；候选为中性浅底并明示“不参与查询”；任务独立列阶段、错误、期限和动作。无候选也保留“无候选”，不用空白引导误解。清理与索引重建在所属组内独立行显示，不给整个文档一个混合状态。基础卡片内边距16px，组间24px；窄屏沿同顺序纵向排列。

**多文档对比：**矩阵用完整对象×条件二维结构，表头含文档标题与固定版本，首列为条件。条件首列184px，文档单元格最小宽度240px，内边距16px、自动增高，正文使用14px且不裁事实；≥768px固定表头和条件首列；<768px保留关联表头但不固定首列，以免遮住文档格。矩阵区域横滚，选格后标题显示当前对象、版本与条件，键盘焦点的单元格自动滚入可视范围。最多24格是可配置业务初值，不是允许视觉隐藏后续格子的理由。

**来源查看器：**完整来源视图≥1200px时原件和提取内容按同一定位并列；原件保持真实页/图比例，提取区使用阅读字号、16px 内边距。定位头部固定显示文档版本、页或结构路径、当前位置与回看限制；失败范围有文字清单。侧栏与<1200px独立视图以明确标签切换原件/提取内容，不把二者都叫“原文”。没有可信区域只显示页级定位，非PDF只显示真实结构位置；布局不生成伪页码。

布局对应的[关键界面文字线框](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/wireframes/key-surfaces.md)包含 W1 问答与证据、W2 生效版／候选／任务、W3 完整对比矩阵、W4 来源校核。它们只说明区域及信息顺序；静态可视稿覆盖这些结构和关键失败状态，本节的视觉规则仍为主文档。

### 可视参考与逐页覆盖

| 已渲染参考 | 落实的视觉规则 |
| --- | --- |
| [M1 问答与来源 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M1-answer-source.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M1-answer-source.svg) | IA-07／09，答案阅读层次、条件与缺口、近邻来源及非 PDF 原件入口 |
| [M2 文档与任务 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M2-document-task.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M2-document-task.svg) | IA-04／06，生效版、候选与任务三区；到期与仍可查询的旧版并存 |
| [M3 对比 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M3-comparison.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M3-comparison.svg) | IA-08／09，完整矩阵、四态、焦点格与同版本冲突双方 |
| [M4 来源校核 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M4-source-check.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M4-source-check.svg) | IA-06／09，原件与提取、参数单位、可信区域和定位回退 |
| [M5 关键状态 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M5-critical-states.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M5-critical-states.svg) | 共享等待／断网待确认／失权／知情重交确认，按钮可用性与焦点外观 |

完整视觉覆盖、其他页面采用的既定组件布局及为何不再单独出图见[视觉覆盖索引](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/INDEX.md)。PNG 和 SVG 表达同一设计，图中业务文本明确为模拟示例；不得将像素图当真实来源、质量成绩或服务端状态。界面中的事实与字段按逐页契约取真实数据。

## Elevation & Depth

继承 Element Plus 的浮层层级与默认轻阴影，不另造装饰性阴影体系。[Sally交付决定] 日常工作面以 `{colors.surface}`、`{colors.surface-subtle}` 和 `{colors.border}` 分区；答案、表格及版本栏不靠悬浮投影提升可信度。只有短时浮层和确认对话框使用系统默认阴影与遮罩；固定头部用边线分隔。

加载不通过闪烁大片渐变模拟。等待中的区域可显示系统加载指示和明确文字，未知进度不画伪百分比。减少动态效果时取消过渡，状态的文字、颜色和布局结果保持一致。

## Shapes

`{rounded.sm}` 为2px，`{rounded.md}` / `{rounded.lg}` 为4px，继承 EP 小/基础圆角；`{rounded.full}` 仅给小型状态标签或圆形标识，主表单和答案工作面不做胶囊形。[Sally交付决定] 一个工作面只保留一层边框，版本分栏用分隔和间距，避免层层卡片挤压事实。

图标沿 Element Plus 的一致线性图形，默认16px，并配文字标签；不能让图标单独承载“满足/明确不满足/证据不足/资料冲突”或危险操作。用户文档中的原图保持原样，不用装饰插画替代图意证据。

## Components

以下16项为与行为文档共用的组件名，都是已定能力的视觉组合。交互与权限以 [EXPERIENCE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md)为准；其余沿 Element Plus 基础样式。表内全部为 **[Sally交付决定]**。

| 名称 | 视觉结构与密度 | 重要状态外观 |
| --- | --- | --- |
| 应用框架 | 灰页面、白导航与主工作面；顶部持续显示当前空间/身份，活动入口有文字、选中边线和 `{colors.selection}`；按确定断点收拢导航 | 权限变化或隔离用有标题的状态区域，不显示空白工作面冒充无资料 |
| 范围选择器 | 标题含“当前空间”和已选库/文档；标签展示完整名称与数量；输入边界 `{colors.border-control}`，默认32px高，换行后增高 | 无选择有明确说明；不可用目标显示错误文字，不把目标悄悄移除；焦点轮廓 `{colors.focus}` |
| 资料表格 | 48px最小行高、40px表头、12px单元格内边距；标题与版本为主层，处理状态/失败范围为独立列，操作右对齐 | 文档状态与清理/重建分别标注；三栏详情沿上节布局；候选、旧版、生效版不共享一个“成功”徽记 |
| 导入表单 | 16px项间距；上传区先列生效格式/限制，再列逐文件结果与必要元信息；输入标签永久可见 | 容量不足/不支持等原因置于对应文件旁；部分文件受理不把整批画成全部失败或全部成功 |
| 处理状态条 | 浅底横条，阶段文字、任务标识和时间分组；12px内边距；详细错误按行展开，不挤在细进度线上 | 排队/处理中/待核对/就绪/部分可用/失败均有全称；未知不显示进度百分比；清理占用另写 |
| 来源查看器 | 版本及真实定位固定在内容上方；白底原件与提取内容分区，当前引用高亮且保留原图/表比例 | 无区域高亮、定位失败、来源删除/无权分别为明文；错误面不残留原件缩略图；失败范围可读 |
| 问题输入区 | 14px输入、16px项间距；问题与环境/版本/日志按场景分组，范围始终在同一工作区；主要动作使用 `{colors.action}` 白字 | 等待状态展示原操作信息；恢复连接与新请求的动作层级分开，不用旋转图标暗示已重提 |
| 答案卡 | 白面、24px内边距，16px/1.75事实正文；条件、结论、步骤、缺口、来源按内容顺序分段；请求/时间/版本用13px深灰 | 正常回答、资料不足、需澄清、资料冲突各有标题；依赖失败使用失败面，不能套“资料不足”样式 |
| 对比矩阵 | 固定版本表头、条件首列、≥240px格宽、16px内边距、自动增高；每格先状态、后理由/缺口/引用 | “满足”绿、“明确不满足”红、“证据不足”灰、“资料冲突”棕；每格全称+图标，不能只用色块/短横线；完整保留四态及各格 |
| 反馈条 | 答案后的次级区域，14px文字、8px间距；问题分类和已提交文字沿统一表单样式 | 已提交有文字确认，失败有原因；不覆盖原答案/引用，不用满意度颜色评价证据正确性 |
| 凭证面板 | 范围/动作/期限元信息优先；明文密钥为一次性独立区域，用等宽字体并允许长串安全换行；默认列表不展示秘密 | 创建、只显示一次、已撤销/到期均明示；撤销是有文字的危险动作，不靠红色小图标 |
| 用量面板 | “原件容量 / 产品问答次数 / 外部实际调用与费用”三组标题及单位；数值14px起，描述完整；不加未授权运营图表 | 原件包含预留和清理中；未知费用显示“待核对/未知”，不能0代替；上海日期明确，超额原因不混账 |
| 管理表单 | 继承EP标签/输入对齐；身份、授权对象和动作分组，16px项间距；角色与知识库范围分不同字段组 | 团队与平台入口视觉同系但标题明确；平台表单不出现由平台身份授予的正文预览；错误靠近字段 |
| 确认对话框 | 白面、4px圆角、24px内边距；标题写动作，对象与不可逆/费用影响为正文，确认/返回沿系统按钮结构 | 删除、撤权、转让、知情重交等使用各自完整措辞；高影响文字保持正文对比，不把后果缩为灰色脚注 |
| 状态反馈 | 12px内边距、14px正文，含标题、原因与当前可执行动作；系统提示按info/成功/警告/失败色对呈现 | 空、加载、失败、无权、断网、待核对和隔离均可用文字辨别；不能用空态插画遮住错误/权限原因 |
| 登录表单 | 单列白面，最大宽400px；永久标签、32px高输入、16px项间距；空间内容在认证完成前不展示 | 登录失败为表单级错误并保留非秘密输入；退出/切账号后的空白区不能残留上一账号标题或头像外的业务信息 |

组件内主要按钮视觉高度沿32px，必要时用系统40px大号；粗指针使用40px视觉控件并留出44px目标区域。表格内的文字链接使用 `{colors.action}` 并提供可见焦点；危险动作同时有文字和确认，不能借放大色彩把正常业务“不满足”变成执行错误。

### Element Plus 绑定与组件状态

以下绑定是输出外观的必要增量，具体样式组织方式由 Amelia 决定。主操作、链接、选中标记与焦点使用 `{colors.action}`／`{colors.focus}`；Element Plus 的主色语义绑定 `{colors.action}`，hover/active绑定 `{colors.action-hover}`／`{colors.action-active}`。`{colors.primary}` 仅保留原系统蓝来源，不用于带普通文字的浅蓝主按钮。普通与次要文字绑定本稿两级深色；输入的必要可辨边界使用 `{colors.border-control}`，结构分隔线使用 `{colors.border}`。状态标签的文字和浅底按同名成对 token 使用，不自动采用系统较浅的成功／警告文字。

| 控件状态 | 确定外观与可达性 |
| --- | --- |
| 默认／悬停 | 输入白底、必要边界；普通按钮白底深蓝文字。主按钮深蓝白字，悬停加深；悬停不作为操作出现或说明出现的唯一条件 |
| 焦点 | 2px `{colors.focus}` 轮廓与2px间隔；不能只更换原边框，不能被固定头遮挡；选格有完整轮廓且保留文字状态 |
| 选中 | 导航使用浅蓝底＋3px选中边线＋明确名称；标签页使用深蓝文字与2px下划线；checkbox/radio使用深蓝标记并提供可读状态 |
| 禁用 | 控件底使用浅灰、文字 `{colors.text-disabled}`；旁边用可读深灰写原因。必需原因、条件和错误不能跟随控件弱化 |
| 提交中 | 保持按钮与区域尺寸，用加载标识加“提交中／处理中”文字；阻止本表单重复触发，未知进度不画百分比 |
| 字段错误 | 输入危险色边界＋字段下方危险色文字；页首摘要可聚焦，不能只弹短提示或只涂红；合法输入保留 |
| 只读 | 用正文标签与值呈现系统事实；需复制的标识保留选择能力；不把不可变版本画成灰色不可读输入，也不伪装成可编辑 |

表单单列时标签在字段上方，标签到字段8px，字段与错误同组；≥1200px管理表单允许左标签120px、值区不超过560px，分组间24px。普通确认对话框宽560px、最大视口减32px；正文超出可用高度时在对话内部滚动，标题与动作始终可达。初始焦点为标题或安全返回动作；高影响确认不用危险按钮默认焦点。标签、表头、条件、理由、错误允许换行，省略只用于非关键名称且必须有可键盘打开的完整值。

列表分页首屏20条、可切20／50条；分页控件包含上一页／下一页、当前页与真实总数（若接口提供）。没有总数时明确当前页，不能伪造总数。页码、筛选与状态的业务规则见逐页契约，虚拟滚动／分页接口形式由 Amelia 决定，不能改变可观察选择与完整结果。

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
| 将委托形成的布局、颜色和主题明确写为交付决定 | 冒称用户逐项确认、实现完成或可访问性已验收 |
