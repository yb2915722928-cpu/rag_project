---
intent: run
type: technical
shape: select
mode: headless
date: 2026-10-15
output_format: md
---

# 数据与检索技术选型研究委派

决策：比较 PostgreSQL＋pgvector、业务库＋Milvus Lite、业务库＋Milvus Standalone、自管理 MongoDB＋mongot、MongoDB Atlas，评估 John 的首版方案。

项目事实仅用于定研究问题，不充当技术证据：用户已确认 FastAPI，4 核 4 GB Ubuntu、Web/后端/数据库同机、无 GPU、约半个月 AI 辅助开发，重视实际工程理解与求职讲述。嵌入、重排、OCR 选型与文档量、切片数、维度、并发未知，32 题仅为评估集。

硬约束：本轮默认保留自管理部署目标；不得未经用户确认改用托管服务，不以未知规模作性能承诺。偏好权重为研究者提出、用户未确认：部署资源管理 30%、首版交付 25%、业务与索引一致性 25%、中文混合检索 10%、退出成本 10%。

采用 straightforward 单研究代理，已由主代理并行委派 Mary 产品视角和技术研究。遵循官方一手来源、两轮封顶，优先处理旧文档与当前版本冲突；不安装、不压测、不生成 HTML。技术数字必须区分最低值、建议值、组件与整机。

未得到第二独立发布者核验的厂商技术事实标为 medium / unverified，表示独立交叉验证未完成，不表示未经阅读。性能排名与容量不作结论。版本兼容性在采用前重新核验。

最终人读报告：[research-storage-comparison.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/research-storage-comparison.md)。运行源与过程文件留在本目录。
