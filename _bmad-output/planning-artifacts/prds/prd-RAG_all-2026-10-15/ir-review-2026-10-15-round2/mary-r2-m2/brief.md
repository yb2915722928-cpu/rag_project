---
type: technical
shape: select
intent: run
mode: focused-headless
created: 2026-10-16
status: complete
---

# 研究简报

决策：选择请求／token／输出预算策略，并给 John 可直接合并的字段、固定算法与负例。此前生命周期与调用账选型不重开。

已授权计划：一个 focused 问题，straightforward，无子 agent，少量阿里云官方文档＋WeKnora `a37a1bc51ad85d096df341f6d3a098f60d586f52` 与 MaxKB `0fa9a0dae8850c1878f087f0d81c974c1d424b06` 固定源码。只查检索／历史／提示预算／输出 token 与截断；默认或自托管能力不移植成千问 API 保证。访问日期按 2026-10-16。网络检索与原始官方源码 GET 可用。

硬门槛：四场景保留；B0 纯向量；K=5；32 冻结题、原金标证据单元分母、SM 门槛不变；同步 FastAPI/ORM＋PG/pgvector 显式 RAG；4 核 4GB 同机四服务；MinerU 云 API；千问按用途实际接入型号尚未选定。项目文件只用来限定需求，不能作为上游能力事实。

候选：A 字符上限＋只裁证据；B 每次精确／可靠上界计数＋分层有限协议／业务限制＋完整输出预留（拟选）；C 由供应方自动截断或事后模型修复。必须先通过完整性与成本硬门，再比较实现复杂度和可逆性，不用虚假精确的性能／费用分数。

预算：单问题、单轮优先，最多追加一次仅为补齐决定性来源；无价格／性能研究，无实际收费调用。上游 API 单一发布者事实标注中等置信度，不以另找同厂商页面冒充独立验证。

交付：question.md、brief.md、evidence.md、answer.md、digests/budget-r1.md、research.md、.memlog.md；真实同题追问到达后另记 followup-question.md / followup-answer.md。主答优先，研究不阻塞 John 质疑。
