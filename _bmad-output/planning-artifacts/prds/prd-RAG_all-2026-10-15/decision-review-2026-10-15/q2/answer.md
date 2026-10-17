---
type: technical
shape: explore-then-select
status: complete
updated: 2026-10-15
---

# Q2：上传、恢复、版本切换与删除

选择 PG 持久任务、分阶段产物和不可变文档版本。数据库约束保证本系统重复执行不重复生效；外部调用可能重复或结果未知，不承诺恰好一次。本轮仅静态核验，尚未实测。

**TR：实际实现与协议边界**

| 对象 | 本轮已证实的行为／边界 | 官方来源 |
|---|---|---|
| WeKnora | 上传任务有限重试；worker 不再执行旧代次、删除中或已完成的任务；非手工重解析先清旧资源，删除先标 deleting 再清理。 | [任务](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L3671-L3715)、[更新](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L2843-L2884)、[删除](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_delete.go#L475-L627) |
| MaxKB | 标准 split 保存原件后同步分段；refresh 是重向量化，QueueOnce 按文档去重；删除关联文件、段落、向量。未审全局重试。 | [分段](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1255-L1284)、[更新／删除](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L818-L877)、[队列](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/task/embedding.py#L61-L92) |
| MinerU | PDF／DOCX 可走申请链接→PUT→自动解析→batch_id 轮询；data_id 仅业务关联，未见幂等／按它找回任务承诺。 | [精准云 API](https://mineru.net/doc/docs/) |
| 来源 | WeKnora 有页／区域／结构块／哈希；MaxKB 已读段落字段不足以证明页级回跳。输出说明已更新，云包结构须实取核对。 | [来源契约](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/source_locator.go#L9-L80)、[MaxKB 字段](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/models/knowledge.py#L251-L266)、[输出契约](https://opendatalab.github.io/MinerU/reference/output_files/) |
| PG | SKIP LOCKED 适合领取队列行；事务与唯一约束只保证数据库内边界。 | [领取](https://www.postgresql.org/docs/18/sql-select.html#SQL-FOR-UPDATE-SHARE)、[冲突处理](https://www.postgresql.org/docs/18/sql-insert.html#SQL-ON-CONFLICT) |

**TS：本项目的八项选择**（方案推断，详细证据与状态机制见[依据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/evidence.md)）

1. **先存原件与任务，再分阶段处理**：TXT／MD 直读，PDF／DOCX 用 MinerU；解析、校核、分块、向量就绪后才可查询。正常文档自动校核；首次导入部分失败列明页／范围，只检索通过内容并标不完整；范围不明不发布。比“API 成功即就绪”多检查点，便于恢复。
2. **短事务领取＋租约心跳**：SKIP LOCKED 领取后提交，单 worker 串行文档；到期可回收，临时故障有限退避，永久错误明确失败。主线程等 HTTP 时不持 Session；独立续租线程每次自行开关短 Session，只心跳不领文档。比全程持锁多租约逻辑，避免长占连接。
3. **领取代次隔离旧 worker**：每次领取增加 attempt；心跳及产物／完成提交均核对当前代次、租约、文档／版本及父级状态；发布与删除共用锁。租约本身挡不住迟到者，代价是条件写入与失效分支。
4. **先落上游 ID 再上传**：保存请求意图、batch_id／可得 task_id、data_id、上传信息和响应；PUT 超时先查原 batch。无 ID 或无法判定的操作转待核对，不盲目重发。比无条件重试慢，但不掩盖重复外部调用风险。
5. **阶段产物幂等复用**：按版本＋配置＋阶段唯一登记，保存原始 ZIP／响应及哈希；只复用校验通过的阶段产物，不承诺 PDF 逐页恢复或字节续传。产品配额幂等计次，实际调用与未知费用单独留账。比整条重跑多存储与状态。
6. **统一来源结构**：版本、原件哈希、解析配置／可得生产版本、章节、段／表／图 ID、关联正文、页区间及可得坐标、原始 JSON 指针。PDF 页统一从 1 起，保留输入基数；DOCX 无可信物理页时用结构定位。比只存 Markdown 多适配工作。
7. **候选就绪后原子切换**：检查仍是当前待发布版本，在同一 PG 事务切活动指针并完成任务；迟到旧候选不得覆盖新候选。不完整候选不覆盖旧版，校核／重试至完整就绪再切换；历史引用鉴权只读旧版，新检索只用活动版。比先删后建多占临时双份空间。
8. **删除墓碑先阻断、清理可重试**：事务标删除并作废代次；检索、引用、下载统一复核当前授权与父级删除状态。按清单清原件、解析产物和索引；迟到结果丢弃／清孤儿，重试绝不清墓碑。代价是保留清理状态，不能靠取消外部请求保证安全。

**初学者复述**：把每次更新当作一份候选稿：后台可以重做，只有当前有效任务能登记成果。新稿准备好才换入口；删掉资料先封入口，再慢慢清文件。云端没回信时先查原任务，不能假定它没处理。图意、表格和定位要拿样例核对，上传成功不算验收通过。

**真正需要的五项验证**（尚未执行）：

- 在申请响应丢失、PUT 超时及每个检查点重启，验证可恢复或明确待核对，不盲重交、不重扣产品配额。
- 租约失效后恢复旧 worker、乱序完成两次更新，验证旧结果不能写成生效版。
- 处理中删除文档／库／空间并让清理失败，验证迟到结果不复活，重试后资产清完。
- 更新失败保旧版、成功后只检索新版；旧历史引用仍鉴权，删除／撤权后不可打开。
- 用 PDF／DOCX、扫描、规则与简单跨页表格、必需图意题核对原包、页号、数值／单位和引用；部分失败显示范围。图意不足列缺口再触发补 API 样测，不更换既定 MinerU 路线。

**user_only_missing：无。** 实际接入时再取得账号并核对返回包与配置，不阻塞本轮选择；文件存储位置留部署题决定。

John 同题追问已收口，见[追问答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/followup-answer.md)。
