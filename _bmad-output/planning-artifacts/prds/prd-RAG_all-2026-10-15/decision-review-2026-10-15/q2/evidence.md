---
type: technical
shape: explore-then-select
topic: Q2 文档生命周期
status: complete
updated: 2026-10-15
claims_verified: 0
claims_unverified: 8
---

# Q2 证据与选择依据

本轮读取日：2026-10-15；未运行两项目、未调用 MinerU。项目需求只限定决策，外部事实仅来自本轮重读的一手协议与固定 SHA 源码。各产品内部实现均为单源观察；“官方原文已核对”不等于独立第二来源或端到端实测。

## 协议读取

1. MinerU 精准云 API 的本地文件路线使用 POST `/api/v4/file-urls/batch` 分配 batch_id 与上传链接；文件 PUT 完成后自动触发解析，以 GET `/api/v4/extract-results/batch/{batch_id}` 查询。协议列出 PDF、DOCX；结果有状态、data_id、full_zip_url、错误和进度。data_id 的说明是业务关联，没有把它定义为幂等键。所读页面未给出请求去重、按 data_id 找回任务或取消的承诺；这是文档覆盖边界，不能断言服务端绝无此能力。[1]
2. 云 API 仍描述 full.md、layout.json／content_list 等文件，但所链接的输出说明现已描述 4.0：它区分远端服务能力，给出 schema／schema_version、producer 版本与从 0 起的 page_idx。不能据此断言实际云包已经切到 4.0，更不能仅凭 model_version=vlm 推断输出结构／模型权重不可变。[1][2]
3. PostgreSQL 明确指出 SKIP LOCKED 可用于队列表的多消费者避锁，且会得到不一致视图；它不是租约、重试或远端调用去重协议。[9] 唯一约束配合 ON CONFLICT 能确定数据库插入冲突行为；事务提供一组数据库更新的整体提交／可见性，均不覆盖外部 HTTP。[10][11]

## 两项目的读取边界

固定源码的逐项事实、精确行号、补取原文及未找到项见 [源码摘要](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/digests/lifecycle.md)。以下只列决定本项目选择的事实：

- WeKnora 文档任务入口检查过时代次、删除／取消与已完成状态；非 manual 重解析先同步清理已有资源，再开启新 attempt 并重新排队。它提供可借鉴的防旧任务措施，但所读重解析路径不是本项目所需的“旧版本继续服务，等新版本就绪才切换”。[3]
- WeKnora 来源契约明确区分 1-based PDF 页、归一化 bbox、DOCX body block、文本范围、来源哈希，并可标记来源映射不完整；DOCX block 不是 Word 物理页。[5]
- MaxKB 标准分段上传保存原件并调用本地处理器；Paragraph 有内容、位置和 chunks 等，已读字段未见 PDF 页／bbox。内部用页计算 TOC 不足以证明引用保留了页号。[6][8]
- WeKnora 文件上传显式配置 MaxRetry(3)；删除先写 deleting，再清向量／chunks／graph，之后删记录和原件，原件删除失败仅记日志。MaxKB refresh 触发 QueueOnce（document_id 去重）的重向量化；单文档删除覆盖 File、段落、映射和向量再删文档。MaxKB 全局重试与并发删除防护未核验；不能把单次调用置于数据库事务等同跨存储的整体原子性。[4][6][7][12]

## TS 的约束与淘汰

硬门槛：PG 持久状态、单 Python 文档 worker、短 Session、云解析、新旧版本原子可见、删除立即阻断、当前统一鉴权、FR-7 全项校核。选择按满足门槛后尽量减少常驻组件与可恢复性排序；不编造评分、吞吐或费用。

- 进程内后台任务不能独立提供约定的 PG 持久恢复，因此不选；增加 Redis／Celery 不符合当前已定 PG 路线，也未证明首版需要。
- 远程等待期间持有行锁虽可排斥另一个领取者，却持有事务／连接，且仍不能解决 HTTP 结果未知，因此选择短领取＋租约＋代次校验；代价是需要显式心跳、超时回收与条件更新。
- 原地清旧块后重建会使更新失败损坏旧版，因此选择不可变版本＋候选产物＋活动版本指针；代价是新旧产物短期双份存储及清理任务。
- 仅 Markdown 入库丢失结构与定位可核验性，因此同时保留原件、原始结果包／响应与规范化来源；代价是产物占盘与适配器版本管理。服务器受控目录只是候选，后续部署题决定。

## 本项目机制（设计推断，尚未实现）

任务持久字段包括阶段、下次尝试时间、失败分类、上游操作记录、租约期限、领取者与单调 attempt。领取和回收使用数据库时间；短事务锁行后写新 attempt 再提交。每次心跳、阶段发布、失败／完成回写都带 expected attempt／owner；租约失效者不能继续提交。worker 不跨远程等待持有 Session，HTTP 有超时。选一个主处理线程和一个只续租的心跳线程：后者每次自行创建／关闭短 Session，不领取文档、不共享主线程 Session，文档并发仍为 1；续租失败／过期设置失效标记，最终提交仍须数据库条件检查，不能凭内存标记放行。

上传先完成原件落盘和校验，再在 PG 提交文档候选版本＋任务；文件与数据库不构成分布式事务，靠临时目录／已校验清单与孤儿清理恢复。任务创建、产品配额事件有业务唯一键，物理文件使用服务器生成的标识，不按用户文件名直接寻址。

每个可能产生外部效果的操作先落库 started，再发请求；响应先保存，后推进阶段。已得 batch_id 必须提交成功才可上传；一文档一批即可降低关联复杂度。保存 batch_id／task_id（若所用路径返回）、data_id、上传地址及失效信息、请求参数／配置哈希、原始状态响应、结果包清单与内容哈希；签名链接只作受控恢复数据，不进入普通日志。

若申请响应未知：没有已存上游 ID 不自动重新申请／付费提交，进入待核对；本设计未持久 ID 就不开始 PUT，因此不会由该 worker 接着上传到未知批次。若 PUT 结果未知：根据已存 batch_id 继续轮询，不能把 waiting-file 当作先前 PUT 一定失败。没有协议保证时不盲重 PUT；有限观察后明确显示待核对／人工重试。GET／结果下载的临时错误可有限退避；错误格式、凭证或不兼容结构直接转明确失败。经确认的重新提交建立独立外部操作记录，可能重复的调用及未知成本均保留；不承诺外部恰好一次。

阶段产物以文档版本＋配置版本＋阶段为业务身份，原始响应／ZIP、规范化结构、分块、向量分别落检查点。阶段行有唯一约束；共享正式产物只允许当前 attempt 登记，临时文件按 attempt 隔离。重试优先复用已校验产物，不重复激活版本。解析升级改变配置版本；不能在历史引用背后悄改来源内容。

统一来源含空间／库／文档／不可变版本、原件哈希、解析配置及可取得的上游生产版本、结构块 ID／类型、章节、原文片段、页区间、可用 bbox／坐标系、图表编号与关联正文、文本范围、映射完整度、原始结构 JSON 指针。PDF 对外统一 1-based；0-based 输入仅在已识别契约下转换并保留原值；跨页表格保留所有贡献页与区域。DOCX 无可信物理页时用段／表／图结构定位，若生成预览页须另存明确映射；不得伪造 PDF 页号。

提交阶段产物／激活版本时，同一短事务以固定顺序检查祖先空间／知识库、文档未删除、version 是当前 desired_version、task attempt／owner／租约仍有效且质量检查通过。正常文档通过自动校核后发布，不增加逐份人工审批。首次导入若部分失败范围明确，可显示“部分可用／部分失败”及通过／失败范围，仅检索校核通过范围并在引用／答案标记不完整；范围不明或必要定位不足则不发布。替换候选不完整时不自动覆盖旧版，只供维护者校核／修正／重试，达到完整就绪条件后再切换。版本切换与删除／替换共用同一文档行锁；库／空间删除也与发布共用祖先状态锁或等价串行门闩，避免“查过父状态后父已删除仍发布”。活动指针更新和任务完成一起提交；新检索只读 active_version。旧版本只通过带版本的引用入口鉴权读取，不提供旧版本检索入口。并发候选中，较旧的完成不能覆盖较新的 desired_version。更新失败只标记候选失败，活动旧版保留。

检查点复用仅指已验证阶段产物；不宣称 PDF 逐页断点、上传字节续传或外部恰好一次。John 同题追问的最终边界见 [收口答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/followup-answer.md)。

删除先事务写永久 tombstone、递增生命周期 generation、清空活动指针并作废任务／attempt。检索、输出前、历史引用及文件读取均核对文档和祖先 tombstone／当前授权；处理中返回也不能绕过。清理按资产清单幂等删除原件、解析图片／包、分块／向量，失败记录待重试；文件不存在视为已清。旧 worker 的临时产物与外部迟到结果只可被丢弃／归入孤儿清理，不能注册为有效产物。清理重试不能清 tombstone；取消外部任务不是安全前提，也不保证停止外部计费。处理中的库／空间删除同样适用。留存最小任务／代次墓碑以阻止迟到写入，详细保留期由部署与数据策略再定。

## 验证与未知

不把官方“支持格式／表格／图片”当成质量证据。实际接入时保存一组 PDF／DOCX 原包，确认字段与页号；逐项核对扫描、规则和简单跨页表格、必须依靠图意的题。图片路径或图注不等于图意；不足时记录受影响页，触发独立图意 API 的小样核验，不重新选 MinerU。

必须故障注入：外部提交／上传响应丢失、各检查点重启、租约过期后旧 worker 回来、候选更新乱序、发布与删除竞态、清理失败重试、历史引用撤权。期望是有效版本唯一／不回退、删除不复活、配额不重复、实际调用与未知成本不被抹掉；尚无测试成绩。

只读原文支撑的结论在技能台账记为单源未独立核验；不要求为供应商私有实现寻找不存在的第二发布者。活跃 API／结果结构在实际接入前再读官方说明；固定 SHA 结论只适用于该快照。

台账计数由技能脚本计算：8 条 load-bearing claim 为可信一手已读、未独立第二源／未实测，0 条被记为独立 verified，不把这个标记误读为“未读原文”。引用标记／来源表机械校验通过，无悬空或孤立引用；新上下文 spot-check 未发现 TR 实质不支持的断言。

时效检查用“本轮读取快照日”代替未知网页发布日期作为重读起点，未声称其为真实发布日期。技能脚本计算：MinerU API／输出契约最晚 2026-11-15 重读，实际接入／变更更早则提前；PG 模式检查日为 2028-10-15。固定 SHA 行为不会自动代表未来版本；升级需重新核验。本轮无待用户提供事项，无外部交接，不创建定时任务。

## 来源附录

所有来源本轮访问均为 2026-10-15。网页未标明发布日期则不猜，源码用已固定 SHA；confidence=medium 表示可信一手单源，非效果保证。

| 编号 | 支撑事项 | Publisher／官方来源 | 发布／快照 | 访问 | 信心 |
|---|---|---|---|---|---|
| [1] | 上传／轮询／格式／data_id／未知边界 | [MinerU 云 API](https://mineru.net/doc/docs/) | 未标发布日期 | 2026-10-15 | medium，单源 |
| [2] | 4.0 输出说明／0-based 页／远端契约边界 | [OpenDataLab 输出契约](https://opendatalab.github.io/MinerU/reference/output_files/) | 页面未标发布日期 | 2026-10-15 | medium，单源 |
| [3] | 任务状态／attempt／重解析先清理 | [Tencent：knowledge_process.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L2791-L3123) | a37a1bc，固定快照 | 2026-10-15 | medium，单源 |
| [4] | 删除调度及清理 | [Tencent：knowledge_delete.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_delete.go) | a37a1bc，固定快照 | 2026-10-15 | medium，单源 |
| [5] | 来源类型与基数／哈希 | [Tencent：source_locator.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/source_locator.go#L9-L80) | a37a1bc，固定快照 | 2026-10-15 | medium，单源 |
| [6] | 标准分段保存原件／refresh／删除 | [1Panel-dev：document.py](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py) | 0fa9a0d，固定快照 | 2026-10-15 | medium，单源 |
| [7] | 异步重向量化任务 | [1Panel-dev：embedding.py](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/task/embedding.py) | 0fa9a0d，固定快照 | 2026-10-15 | medium，单源 |
| [8] | Paragraph 字段及已读定位范围 | [1Panel-dev：knowledge.py](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/models/knowledge.py#L251-L266) | 0fa9a0d，固定快照 | 2026-10-15 | medium，单源 |
| [9] | SKIP LOCKED 队列语义 | [PostgreSQL：SELECT](https://www.postgresql.org/docs/18/sql-select.html#SQL-FOR-UPDATE-SHARE) | 18 文档 | 2026-10-15 | medium，单源 |
| [10] | 唯一约束冲突及 UPSERT | [PostgreSQL：INSERT](https://www.postgresql.org/docs/18/sql-insert.html#SQL-ON-CONFLICT) | 18 文档 | 2026-10-15 | medium，单源 |
| [11] | 数据库事务整体可见性 | [PostgreSQL：Transactions](https://www.postgresql.org/docs/18/tutorial-transactions.html) | 18 文档 | 2026-10-15 | medium，单源 |
| [12] | 文件上传任务有限重试 | [Tencent：knowledge_create.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_create.go#L219-L272) | a37a1bc，固定快照 | 2026-10-15 | medium，单源 |
