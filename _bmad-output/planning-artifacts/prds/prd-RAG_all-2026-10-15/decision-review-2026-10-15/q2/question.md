# Q2：文档从上传到可查询、更新与删除

日期：2026-10-15。Mary；先 TR technical/explore，再 TS technical/select；headless。

John 实际问题：已经决定使用 MinerU 云端 API，文档从上传到可查询、版本更新和删除应怎样完成？WeKnora 与 MaxKB 实际怎样安排解析、任务重试、来源定位和版本／清理？先 TR，再 TS 选择 PG 任务领取与恢复、MinerU 上传结果持久化、统一来源结构和版本切换机制。特别说明外部请求结果未知、旧 worker 迟到、文档在处理中被删除，如何避免重复生效或恢复失效资料。不得承诺外部调用恰好一次。

约束来自 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:164)，范围：164–186、232–236；约束不是外部技术事实证据。

- 沿用 PG 持久任务＋独立 Python worker，文档并发 1；同步 SQLAlchemy／psycopg 短 Session，远程等待不持事务。
- MinerU 云端上传解析；TXT／MD 直读。PDF／DOCX、FR-7 表格／扫描／图意／定位仍须验证，不安装模型、不调用收费 API。
- 新版就绪才原子切换；历史原版本鉴权只读且不参与新检索。删除先阻断检索、引用、下载，再可重试清理；迟到结果不得复活资料。
- 引用与原件共用当前授权；受控服务器目录仅为文件存储候选，部署题再定。

本轮只读固定 SHA 官方源码快照；缺口窄查官方 MinerU／PostgreSQL 文档。保留事实、方案推断、未测项的区别；不评价登录、前端或检索优化，不改 PRD。

TR 完成条件：两项目真实边界与 MinerU 协议足以支撑本题。TS 完成条件：给出 6–9 个明确选择、替代与代价，以及 3–5 项故障／质量验证；不以无意义评分填充。
