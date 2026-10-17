# R2-M1 证据与覆盖审计

访问日期均为 **2026-10-15**。项目文档用于界定需求，以下官方来源用于上游事实；源码均在本轮重新从固定提交的 raw.githubusercontent.com 读取。原始文本在本目录 imports，行号按该文本的一基行。未运行项目或厂商 API。

## 已有规则，不能重算本轮发现

[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:28)，范围28–39，已明确三本账、完整候选预留、清理确认后释放、临时物理预算；[同文件](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:63)，范围63–69，已明确问答租约、条件提交及维护扫描；[同文件](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:85)，范围85–91，已明确全部未终结写意图、guard归属和历史证据快照。Q2 已选择旧 attempt 检查、阶段复用、待核对与删除墓碑，见[Q2主答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/answer.md:24)和[追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/followup-answer.md:3)。

新增缺口是：未开始上传的专属截止时间和终态、全生命周期写入者屏障、每次实际网络发送前持久意图、过期扫描与准入的同锁竞争。原稿没有把这些机制明确到可证伪的条件。

## 官方文档

| ID | 本轮读到的范围与能够支持的结论 | 来源／发布日期／置信度 |
|---|---|---|
| S1 | 精准解析是厂商云API，申请链接后PUT自动触发解析；链接24h；返回batch_id并按其查询；data_id说明是业务标识，所读接口未承诺幂等、按data_id找回、取消或删除。轻量Agent接口是另一产品分支，不能替代。 | [MinerU精准API](https://mineru.net/doc/docs/)，页面行251–410、批量查询节；未标发布日期；单官方源、中、unverified |
| S2 | SKIP LOCKED适于队列式多消费者；行锁到事务终结释放。数据库锁的描述不能证明隔离文件与厂商调用。 | [PG18 SELECT](https://www.postgresql.org/docs/18/sql-select.html#SQL-FOR-UPDATE-SHARE)，网页行384–407；[显式锁](https://www.postgresql.org/docs/18/explicit-locking.html#LOCKING-ROWS)，行94–113；版本18，发布日期未单列；官方单发布者、中、unverified |
| S3 | Popen的communicate超时不会杀子进程，需显式kill并等待；可用start_new_session，不应在线程中使用preexec_fn。此为本地进程停止工具，不等于撤销远端请求。 | [Python3.12 subprocess](https://docs.python.org/3.12/library/subprocess.html#subprocess.Popen.communicate)，网页行261–290、395–455；页面更新2026-10-01；单官方源、中、unverified |
| S4 | Linux flock绑定open-file-description，所有相关FD关闭才释放；是协作锁，有权限者可绕过。不得删锁文件再建同名锁，否则可能锁在不同inode上。 | [Linux man-pages flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html)，网页行25–66、135–160；man-pages6.19，页日期2026-02-08；Linux接口维护文档、中、unverified |
| S5 | unlink掉名称不等于释放已有打开FD占用；最后链接消失且没有进程打开文件才释放空间。 | [Linux man-pages unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html)，DESCRIPTION；man-pages版本见页面；单源、中、unverified |

同类语义由PG、Python、Linux不同发布者交叉约束，但不能将不同层的文档合并成“已验证本项目闭环”。未知API协议与目标主机表现仍未知。

## 固定提交源码，只限所读路径

| ID | 精确范围及结论 | 不支持的外推 |
|---|---|---|
| S6 | WeKnora [创建](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_create.go#L165-L245)：先SaveFile，再DB创建，DB失败尝试删文件，然后入队；[本地文件](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/file/local.go#L48-L96)按租户/knowledge目录与唯一文件名写，删除137–154调用os.Remove。KB可配置存储引擎，local是该实现，不声称所有部署默认都local。 | 该入口不是本项目“两段POST→PUT”预留；未证明跨文件与DB原子、无孤儿、停写屏障或本项目原件账。 |
| S7 | WeKnora [任务](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L3651-L3715)：重试元数据兼容Asynq和Lite，检查旧attempt、deleting、cancelled、completed；[删除](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_delete.go#L483-L630)先deleting，尽力出队，清向量等，DB行先删除再删物理文件。 | 只证明已读入口检查；未追全调用图，不声称每次外发和所有文件写入都有实时fence。非手工reparse 2843–2884会先清旧资源，不抄成本项目替换方案。 |
| S8 | WeKnora [span记录](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_span_tracker.go#L422-L490)：按attempt记录running子span和done，写入失败记录warn并返回nil。 | span是处理轨迹；未证明每次真实发送前必须成功持久intent，未证明计费账或exactly-once。 |
| S9 | MaxKB [上传分段](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1255-L1284)先保存原件再split；[文件模型](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/models/knowledge.py#L367-L434)本路径为压缩后PG large object并按hash复用；[任务](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/task/embedding.py#L61-L92)QueueOnce按document_id去重；[删除](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L818-L877)事务删除关联数据并可刷新向量。 | 这些是此固定源码中的自托管实现路径，不是MinerU云端保证；未核验所有large object回收信号或所有部署文件后端；QueueOnce不证明租约、物理清理屏障或网络恰好一次。 |
| S10 | MaxKB [模型调用与token上下文](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py#L725-L753)：get_block_result后计算token再写context；普通invoke在696；流式151–162有token估计异常设0分支。 | 仅说明该记录路径，不等于厂商账单、全仓没有其他记录，亦不证明每次发送前持久记录；本项目不能照搬未知为0。 |

源码发布日期未另查提交日期；按固定SHA作版本事实。事实置信度为单可信源码、中、unverified（未独立发布者复核），不将源码静态阅读叫运行验证。原始文本SHA256随[源码清单](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/imports/source-manifest.json)保存。

## 停止条件及未证范围

聚焦问题的协议与机制边界已经覆盖，停止TR，不扩大到全仓审计。未证：MinerU按data_id去重／反查／取消／删除及费用回填能力；云解析结果的保留期限；千问具体型号SDK内部重试与usage字段；Ubuntu进程回收、资源水位、真实RSS和存储峰值。以上通过S0假件＋P0真实能力探路核验，不能在此宣布通过。
