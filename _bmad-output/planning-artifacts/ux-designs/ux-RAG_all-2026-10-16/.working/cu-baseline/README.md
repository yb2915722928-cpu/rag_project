# RAG_all UX 首轮设计

日期：2026-10-16。设计师：Sally。状态：首稿，供审阅与继续设计；不代表视觉方向已确认、产品已实现或验收已通过。

## 从这里看

| 文档 | 内容 |
| --- | --- |
| [UI 参考与取舍](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/ui-references.md) | RAGFlow、MaxKB、Dify 的官方界面和本项目取舍，含截图 |
| [DESIGN.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md) | 视觉层次、设计 tokens、组件外观；采用既定 Element Plus 基础，明确标注首轮假设 |
| [EXPERIENCE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md) | 信息架构、角色入口、组件行为、状态、恢复、无障碍、四场景旅程 |
| [关键界面文字线框](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/wireframes/key-surfaces.md) | 问答与引用、资料状态、比较矩阵、来源校核的结构提案；尚无渲染 mock |
| [覆盖与验收映射](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/coverage.md) | 页面／动作与 FR、切片、SM、权限及关键负例之间的对应 |

## 本轮继承的基线

| 资料 | 本轮用途 |
| --- | --- |
| [最新 PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:428) | 角色、四场景、范围、验收的唯一产品基线 |
| [现行实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:10) | 权限、版本、任务、引用、幂等、费用与恢复的跨模块语义 |
| [现行实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:9) | 首次交付、依赖、负例与停止点；特别是 S2 即交付最小校核与来源回看 |
| [最终收敛记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:14) | 已关闭争议、无设计阻塞、剩余执行验证事项与交接边界 |

当前 PRD 的 SHA256 为 `0963d529922a6b3812c8f8311f29f5112a537a59ca62616f4dc45a245baaa299`。收敛目录中的 input-manifest 是收敛前共同输入；本轮采用最终主文档，未用 baseline 或 snapshots 覆盖它。

提取证据：[PRD 摘录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/.working/source-prd.md)、[契约与切片摘录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/.working/source-contract.md)、[最终收敛摘录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/.working/source-convergence.md)。它们用于追溯，不取代上游正文。

## 已定事项直接沿用

- SC-1 技术支持与故障排查／小林；SC-2 企业内部知识查询／小周；SC-3 多文档对比与能力核验／小陈；SC-4 复杂产品手册问答／小赵。
- 团队所有者、知识维护者、知识使用者及独立平台管理员的既有边界；负责人是责任关系，业务岗位是任务背景。平台身份不自动授予业务读权。
- Vue 3／TypeScript／Vite 与 Router／Pinia／Element Plus；首版完整答案一次返回；只读程序 API。
- 32 题、四场景独立门槛、最终 K=5、引用与复杂题、权限专项及全部验收标准；没有因设计删改或弱化。

## 本轮提出的设计

**[Sally 设计提案]** 持续可见的当前空间与本次资料范围、中央任务区、按需展开的来源区。问答与对比分开组织，资料详情将当前生效版、候选和任务分别表达；四态结论、执行失败、未知状态分别呈现。具体规则见两份主文档。

**[ASSUMPTION]** 桌面浏览器优先的布局、浅色审阅基线、系统字体与密度是可调整的首稿假设；不是新增平台要求或用户已选的品牌风格。用户暂无额外视觉偏好，已授权研究 RAG 界面；最终主题与品牌尚未定稿。

## 本轮边界与后续收口

本轮只写设计文档，没有启动应用编码、部署、模型调用或产品测试。官方参考图已查看；文字线框与设计规则尚未变成渲染 mock，逐页面布局也尚未获得用户确认。

进入定稿前还需完成视觉方向选择、关键界面可视稿及逐页面 mock 覆盖取舍。独立 UX 验证按 bmad-ux 的 opt-in gate 再选择镜头，本轮只做来源、链接与首稿覆盖核对，不将未运行的评审或产品验收记为通过。由于尚处首稿，两份契约保持 `status: draft`。
