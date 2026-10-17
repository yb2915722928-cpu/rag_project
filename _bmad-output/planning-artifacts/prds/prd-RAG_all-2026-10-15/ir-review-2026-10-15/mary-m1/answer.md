---
owner: Mary
question: M1
sequence: TR/explore -> TS/select
date: 2026-10-15
status: complete
user_only_missing: []
---

# M1 结论

采用 PG 原子预留和唯一终态账本；原件容量、问答产品计次、真实外部成本分别记账。诊断 request_id 不承担防重。

TR：本轮复读/窄取官方锁 SHA，访问 2026-10-15；只认所读路径，不推断完整产品能力。

| 项目 | 已证实现及边界 |
|---|---|
| WeKnora | [上传门禁与文件重复检测](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_create.go#L92-L128)；处理用[索引估算](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L698-L718)检查，完成后加账；[行锁加减](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/repository/tenant.go#L138-L154)与门禁分开。request_id 为消息/诊断关联，另有 session 活跃 turn 互斥；未证输入绑定与结果重放。 |
| MaxKB | [单文件大小检查](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1214-L1218)，所读路径未证累计容量预留；问答先检查、后[读值加一](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py#L44-L58)，正常及捕获异常路径均可能计次；[每日定时清零](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/job/client_access_num_job.py#L18-L42)。chat_record_id 复用不豁免后处理计次，未证请求重放保证。 |

TS：不选“先查后记”或承诺跨上游恰好一次。PG [组合唯一约束](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS)及[行锁](https://www.postgresql.org/docs/18/explicit-locking.html#LOCKING-ROWS)可支持本地账本；代价是多几张小表、终态恢复器及短暂预留占用。

**容量。** UI 称“原件容量：保留原件＋在途预留”，按每个保留版本的原件字节计，包括当前、历史、候选、保留的失败候选及清理中原件；同内容不同版本仍分别计。替换不抵扣旧版，不新增旧版清理功能。逐文件条件预留 `used+reserved+bytes≤limit`；未知长度先占单文件上限，超实际声明即中止。原件安全落盘并登记后，同事务预留转实占；流中止的临时资产或删除原件确认清完后才释放，清理失败继续占用。批量逐文件给结果。解析、图片、向量、PG、临时 ZIP 另受磁盘低水位、阶段资源预算、解压总字节/项数上限保护；不能把原件配额显示成总磁盘占用。

**请求身份。** 生成 POST 必须有独立 Idempotency-Key，Web 自动生成、API 调用者提供。唯一域是持有人用户＋空间＋能力＋Key 摘要；客户端规范输入 HMAC 含问题、显式参数和明确目标 scope，异内容返回 409。首次受理另钉住执行快照：模型、索引/文档版本、检索和融合配置；平台默认配置之后改变不改变原操作。同 Key 执行中返回 202 和状态位置；成功重放既存结果、无新检索、生成和扣次，标 `replayed`、原受理/完成时间和版本；终态失败重放原失败，用户点击重试才生成新 Key。网络重传不能自动换 Key。

每次重放先验证当前账号、凭证、原 scope 与答案依赖版本；任一越权或源已删除便拒绝，不回旧答也不重新生成。被替换而保留的原版本按 FR-8 历史核验规则处理，不混入新检索。实现初值：成功结果指针可重放 24h，Key/HMAC/终态/受理日最小墓碑保留 7d，私有问题和答案不复制进幂等表。Key 用 UUIDv7，首见由服务端校验生成时间未超过 24h、未来偏差至多 5 分钟；已有 Key 按受理后 24h 到期，过期一律 410。删除墓碑后仍用 Key 时间拒绝旧 Key，避免静默变成新提交。上述时长和偏差均为受托可调初值；带时间格式的复杂度用于让有限墓碑清除后仍可拒绝旧 Key。

| 必须唯一的业务键 | 状态及原子效果 |
|---|---|
| 空间＋受理日；逻辑操作 ID | `reserved→settled/released`；预留条件为已结算＋预留＜限额；同终态仅改一次 |
| 持有人＋空间＋能力＋Key 摘要（均非空） | `reserved→running→succeeded/failed/failed_unknown`；结果、计次终态同事务提交 |
| 空间＋逐文件 operation_id；版本＋阶段＋代次 | 上传重放不建新版本/预留；worker attempt/lease 只围绕同一操作，迟到结果受代次守卫 |
| 外部 call_id；对应操作＋attempt | 每次真正发出调用独立记录，未知 Token/金额记“待核对”，不能写 0 |

生成前短事务建操作并预留；正常完整答复含合规不足/澄清/冲突结算 1。拒绝、依赖失败、超时、校验失败、输出前失权释放；受理时 Asia/Shanghai 日期冻结，不跨桶。完成持久化、复核授权和结算提交后才输出。崩溃由 lease 到期恢复器条件终止并释放，fence 旧 attempt；已发送未知不自动重发，失败页说明外部成本可能存在。显式新逻辑请求成功可另计；检索/引用/状态不扣产品次数。下调限额只阻止后续预留，不撤销已受理操作；并发及调用限流独立。

故障验收：

1. 最后一份容量/次数被并发争抢，只有满足条件的一笔预留成功；批内超额仅该文件失败。
2. 提交后断网，同 Key 跨午夜重放不再调用或换日期桶；异内容 409、过期 410，墓碑清除后旧 Key 仍 410。
3. 上游已接收时进程崩溃：产品预留终态只释放一次，成本未知可见；迟到结果不恢复成功或再扣次。
4. 替换失败保留旧有效版，旧版仍占容量；删除立即禁访问，清理失败不释放原件字节，重跑清理只释放一次。
5. 输出前及成功重放前撤权/删除来源均拒绝旧答；前者释放、后者保留原成功结算且不新增费用。

本题无需用户补充业务答案；实际限额与磁盘阈值由实施登记为可见配置，故障用例仍待实现验证。

John 同题追问已收口，恢复器归属与 fence、业务成功与回包丢失、逐文件上传重传及 HMAC 轮换规则见 [M1 收口答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/followup-answer.md:1)；其中对含糊边界的明确规则优先。
