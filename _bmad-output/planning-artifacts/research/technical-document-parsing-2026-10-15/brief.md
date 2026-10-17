# 文档解析分工研究 brief

> 最终决定：用户已确认首版采用 MinerU 云端 API 上传解析。覆盖本 brief 与此前路线建议；停止扩展研究/实验，不再抛选择或样例问题。凭证、端点、实际上传、图意/表格/引用质量尚未配置验证。

> 最终约束更新：用户明确 API 优先；本地 OCR/模型服务不作为本期推进项，只保留未来主动实验候选。John 2026-10-15 本机只读检查回报 i7-12700H、RTX 3060 Laptop GPU 6144MiB，覆盖下文初始“无 GPU”假设；RAM 16GB 未复测。生产 4C4GB 约束不变。最终建议以 research.md 为准，不根据初始 brief 启动 CPU OCR。

- 日期：2026-10-15（Asia/Shanghai）；研究者：Mary；委托方：John。
- Intent：Run；TR：technical/explore；TS：technical/select；headless：plan-and-proceed。
- 决策：理解 WeKnora 与 MaxKB 的实际解析边界，为 RAG_all 选择本地解析、独立自托管解析服务与厂商 API 的分工。
- 约束来源：本轮任务 brief（项目约束只用于决策，不作为外部技术事实证据）。约半个月，AI 实施、用户核对学习；FastAPI、PostgreSQL+pgvector、Vue3；PG 持久任务+独立 Python worker；初始一份文档。4C4GB Ubuntu 承载后端和数据库，开发机 16GB 无 GPU；模型 API、按需充值。保留章节与页引用、扫描 OCR、简单跨页表格及至少一道图意问答、原图与重新处理能力。
- 硬门槛：不得凭空声称实现质量、性能和资源占用；本轮只读源代码及官方文档，不部署测试。区分本地库、独立自托管服务、商业外部 API；区分支持能力、默认配置和本轮验证。
- 研究 topology：breadth-first，两名 fresh-context 研究者分别核对上游实现与候选路线，Mary 统筹证据核验和决策综合。
- effort：standard，最多 2 轮，每维约 8 个来源；validation=normal；red_team=off；不额外输出页面、演示稿或市场报告。用户已授权研究，跳过交互 gate。
- 搜索面：官方 GitHub 源码、官方文档、官方模型/产品与许可证说明；通过本轮互联网检索，不以训练知识或项目旧报告作证据。
- 选择权重（研究者判断，非用户已确认）：交付与运维 30%，引用与可校核 25%，目标表格/OCR/图意覆盖 25%，成本可观察与可替换 15%，许可边界 5%。评分只是约束下的适配判断，无性能或成本数字。
- 预期产物：digests/、research.md、.memlog.md；交回 John，不向其他 Codex 聊天发送消息。
