# Q3：RAG 最小共享链路

日期：2026-10-15。Mary 受 John 委托，headless 执行 technical/explore（TR）后 technical/select（TS），追问仍回本 Mary。

> 既然先做 B0，分块、向量化、检索、上下文、答案和引用应该如何衔接？WeKnora 与 MaxKB 的实际 RAG 链路哪些值得参考？请先 TR 再 TS，为本项目选择能覆盖企业查询、故障排查、对比核验、复杂手册的最小共享链路，并说明追问如何不绕过权限。不要把关键词、重排和 ANN 提前变成必做，不取消最终 K=5 与证据验收。

约束输入仅来自 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:193)，范围：193–284，及 Q1/Q2 已定边界。它们定义要求，不证明外部技术事实。Q2 增量由调用方交接：来源定位、完整候选 ready 后切 active、tombstone 阻断、旧版本仅鉴权回看、PG 租约队列。不得重开 OCR、身份或部署选型，不编码、不运行产品测试、不调用收费 API。

交付：首轮官方证据、TS 6–9 项、初学者复述、验证计划；所有未知显式保留。user_only_missing：无。

