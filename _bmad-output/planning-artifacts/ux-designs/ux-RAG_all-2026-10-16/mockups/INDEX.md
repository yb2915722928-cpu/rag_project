# 可视参考与页面覆盖

更新：2026-10-16。交付状态：5 张静态 SVG 与对应 PNG，另有四屏总览。均为离线可看的设计产物，模拟资料不是真实业务证据，不包含应用功能。文字和行为以[EXPERIENCE](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md)与[逐页契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md)为准；视觉以[DESIGN](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md)为准。

![四个关键界面总览](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/overview.png)

| 页面 | 视觉交付 | 使用规则 |
| --- | --- | --- |
| IA-01 登录与账户 | 主文档组件表＋逐页契约 | 400px最大宽单列表单，永久标签；错误摘要与安全返回沿共享模式，无特殊布局需另选 |
| IA-02 空间与邀请 | 主文档组件表＋逐页契约 | 当前空间／团队／邀请分组列表，标准管理表单与确认；窄屏单列 |
| IA-03 库目录 | 主文档组件表＋逐页契约 | 顶部筛选＋创建（按权限），下方标准资料表格；授权与团队角色分别分组 |
| IA-04 资料详情 | [M2 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M2-document-task.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M2-document-task.svg) | 生效版／候选／任务不得混态；清理和重建独立说明 |
| IA-05 导入替换 | 主文档组件表＋逐页契约 | 先显示配置／容量，再文件区与逐文件字段／结果；系统版本只读、人可读版本标签分开 |
| IA-06 校核任务 | [M2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M2-document-task.png)＋[M4 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M4-source-check.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M4-source-check.svg) | 版本与任务头固定、原件／提取分区；核对与继续处理分动作 |
| IA-07 问答与历史 | [M1 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M1-answer-source.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M1-answer-source.svg)＋M5 | 一组导航与会话列表、中央阅读、底部输入、按需右侧来源 |
| IA-08 多文档核验 | [M3 PNG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M3-comparison.png)／[SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M3-comparison.svg) | 对象与条件保序，四态与全部格，选格后显示同版本依据 |
| IA-09 来源引用 | M1＋M4 | ≥1440px结果与400px来源并列；完整来源视图≥1200px原件／提取并列，其他宽度用标签切换 |
| IA-10 凭证与用量 | 主文档组件表＋逐页契约 | 范围／动作／期限表单；秘密一次性面板；三本账分组，用量不扮演资金余额 |
| IA-11 团队管理 | 主文档组件表＋逐页契约 | 成员、邀请、库访问与所有权操作分区，标准管理表格/表单/确认复用 |
| IA-12 平台管理 | 主文档组件表＋逐页契约 | 配置、验证、配额、运行元数据分组，复用管理表单；不增加业务正文工作台 |

上述标准页面由两位 Sally 在本轮委托下确定采用主文档与逐页表格交付；不需要另等一次布局选择。所有页面均有具体字段、初值、动作、错误／恢复与验收，原生 Element Plus 控件的普通实现由 Amelia 决定。不同断点的变换按 DESIGN 明确规则实施，静态图的1600px画布不是最小支持宽度。

## 关键替代状态

![等待、失联、失权与知情重交](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M5-critical-states.png)

[M5 SVG](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/mockups/M5-critical-states.svg)呈现等待不交草稿、断网先核原操作、无权不泄露来源、勾选知情说明后才能重交的可见层次。业务失败、正常不足和来源定位错误的语义分别沿逐页契约，不因共享灰色或红色而合并。

## 静态核对与用途限制

已检查 SVG XML、画布内文字边界，并实际查看总览、原件对照及关键状态 PNG；无外部字体或网络资源依赖。色对使用 DESIGN token。此核对只证明设计文件可读与结构一致，不证明产品键盘行为、权限隔离、模型质量、引用准确或响应式已经运行通过。真实运行证据按[验收契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md)执行。
