---
type: technical
shape: explore -> select
accessed: 2026-10-15
status: complete
---

# 本轮 TR 证据

需求只用于设定问题边界：本轮仅复读 [FR-4/5/6/8/15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:151)，范围：151–199、245–251。以下竞品事实来自本轮实际读取的官方源码；没有将既有研究结论或项目计划当成事实。源码可证明所读实现，不证明其已经在本项目通过并发测试。

## WeKnora

发布者 Tencent；固定 SHA `a37a1bc51ad85d096df341f6d3a098f60d586f52`，GitHub commit API 本轮核对 committer 时间为 2026-10-15T07:19:23Z；访问 2026-10-15。

- W1：上传时先计算 hash、查询知识是否存在；相同文件/来源身份命中时返回已有知识及重复错误。随后读取 context 中租户 `StorageUsed >= StorageQuota` 拦截，并记录原件 FileSize。该处没有把“当前占用 + 本次原件大小”作原子预留。原件保存后才写知识行，写行失败会尝试删文件。官方 [knowledge_create.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_create.go#L92-L128)，范围：92–128、165–211；复读已有 [锁定快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/imports/implementation-r1/WeKnora/internal/application/service/knowledge_create.go.md:92)。这是文件重复检测，所读函数未证通用 HTTP 幂等协议。
- W2：处理中调用检索引擎 EstimateStorageSize 得到 embedding/index 估算大小，重新读租户后比较占用加估算值是否超额；超限标记失败并删未索引块。处理完成后把 totalStorageSize 记入文档并 AdjustStorageUsed。官方 [knowledge_process.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L698-L718)，范围：698–718、821–861；本轮复读 [快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/imports/implementation-r1/WeKnora/internal/application/service/knowledge_process.go.md:698)。因此所读计量是索引估算口径，不能称为全物理文件空间。
- W3：AdjustStorageUsed 使用事务及 FOR UPDATE 读租户、调整后保存；能串行化该次加减，函数本身没有配额上限条件。W2 的检查与 W3 的加账分开，不能由此推导“检查+预留”对并发安全。官方 [tenant.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/repository/tenant.go#L138-L154)；本轮新取 [源码](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/imports/weknora/internal/application/repository/tenant.go:138)。
- W4：批量删除先标 deleting，删除关联数据、知识行，再尝试移除原件；文件删除失败仅记日志，随后仍按 StorageSize 汇总减账。官方 [knowledge_delete.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_delete.go#L613-L643)；本轮新取 [源码](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/imports/weknora/internal/application/service/knowledge_delete.go:613)。此释放时机不符合本项目“保留原件/清理中原件均计”的选择，不能照抄。
- W5：QA 从 request context 取 request_id 作日志、事件和消息关联；仓储按 session_id + request_id 找消息。QA 另有 session 活跃 turn 冲突保护和消息回滚。所读路径未见“持有人+规范化输入摘要+Key”唯一绑定、完成结果重放、每日问答预留结算协议。官方 [qa.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/handler/session/qa.go#L1174-L1189)，范围：178–180、1174–1189、1290–1357；[message.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/repository/message.go#L344-L352)；本轮新取 [QA 源码](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/imports/weknora/internal/handler/session/qa.go:1174)。不将“未在这些路径看见”扩大成全项目不存在。

## MaxKB

发布者 1Panel-dev；固定 SHA `0fa9a0dae8850c1878f087f0d81c974c1d424b06`，GitHub commit API 本轮核对 committer 时间为 2026-10-15T07:16:05Z；访问 2026-10-15。独立事实助手本轮窄取官方 raw 源，详见 [MaxKB digest](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/maxkb-digest.md:1)，以下仅汇入决策相关事实。

- M1：知识库默认单文件上限 100×1024² 原件字节，Split 入口在解析前按 f.size 检查。所读 Knowledge/File、Document Split/Batch/原件保存与 OSS 序列化路径未证累计空间容量预留/释放。File.save 还会按原始 hash 复用文件，或把压缩后字节写入 file_size，因此不能把那个字段直接冒充原件大小。官方 [document.py](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1214-L1218)、[knowledge.py](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/models/knowledge.py#L387-L406)。
- M2：非 debug 的匿名/对话用户，按 application_id + chat_user_id 读统计并先比较 intraday_access_num；统计模型该组合为普通索引。简单应用 add_access_num 是读值 +1 后 save；正常及捕获异常路径均可走到递增调用，不能概括为仅成功扣次。官方 [前置校验](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/chat/serializers/chat.py#L306-L324)、[递增与调用](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py#L44-L58)，范围：44–58、163–206、763–805。
- M3：定义了 cron 00:00:00 的全表 intraday_access_num=0 清零任务并注册，未做部署注册成功/执行/时区验证。请求检查不按受理日期建独立桶。官方 [client_access_num_job.py](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/job/client_access_num_job.py#L18-L42)。
- M4：chat_record_id 是已有会话记录身份，普通聊天要求该记录存在；记录更新与计次独立。工作流复用记录后仍调用统计 +1；阻塞式简单生成在所读实现内新建 UUID。没有据此证明请求重放防重、并发预留或失败不扣产品次数。官方 [已有记录校验](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/chat/serializers/chat.py#L459-L478)、[工作流后处理](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/flow/i_step_node.py#L67-L103)。

两项目的不同计量和计次口径不是矛盾；它们回答的产品问题不同。本项目继承 FR-4/8/15 的约束，因此只借鉴对象关联、状态记录和数据库原语，不移植它们的业务扣量语义。本轮未运行任一项目，也未声称其完整能力或性能已验证。首轮已覆盖目标问题，停止扩搜。

## PostgreSQL 原语与结论边界

发布者 PostgreSQL Global Development Group；本轮读取官方当前 PostgreSQL 18 文档，访问 2026-10-15。官方 [唯一约束](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS)支持多列组合唯一，约束键应 NOT NULL；[显式锁](https://www.postgresql.org/docs/18/explicit-locking.html#LOCKING-ROWS)说明行锁协调并发修改。这些原语支持本项目的短事务条件预留、唯一逻辑操作和条件终态；它们本身不提供跨外部 API 的 exactly-once。

TS 将比较“先查后记/缓存计数”“PG 预留+终态账本”“跨外部 API 全局恰好一次”。选择第二项；第一项不能关闭检查到记账间的竞争窗口，第三项超出无上游幂等承诺下可证明的边界。仅选必须机制，不额外引入 Redis、支付系统或新服务。
