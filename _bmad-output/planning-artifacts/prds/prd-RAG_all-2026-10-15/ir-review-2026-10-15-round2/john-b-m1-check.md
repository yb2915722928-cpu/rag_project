---
title: 第二轮 IR · John B 生命周期实际改稿中途复核
date: 2026-10-16
reviewer: John B
status: targeted-review-not-final-gate
---

# John B 中途复核

继续同一独立 John B 任务。独立初评与真实对抗稿保持封存；本稿只复核 A 已实际修改的权威 PRD／实施契约，以及原 Mary R2-M1 主答、同题追问和上传身份整合说明。未重新初评、未编码、未调用实际服务，未运行产品验证。

本次判定：**F1 上传意图有限寿命 CLOSED；F2 原主要反例已修复，尚有“原任务截止后继续核对”的派发上下文须对齐；F4 已关闭；F3 未合稿仍 OPEN。没有总体 PASS。** scope 和前端两项明确化不加 material 发现数量。

## F1：CLOSED，原反例已无法按现行规则永久占用

| 原关闭条件 | 实际权威落点 | 复核判断 |
| --- | --- | --- |
| 从未 PUT 也有期限、维护扫描、显式放弃 | [契约 §2.4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:75)，范围 75–79；[候选 GET／abandon](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:225)，范围 225–226 | awaiting_upload 独立于 worker task；开始窗口、首次开始后绝对期限、进展超时、扫描初值已记录，重传／心跳不延长。无 task 的候选可查看和放弃。 |
| 过期／完成／重传竞争只能一个业务效果 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:77) | 共 KB／候选锁和条件状态；完成须匹配 attempt／token／lease／期限／父级／hash／长度。登记原件、转实占、创建任务同事务；到期先胜不建任务，完成先胜不被扫描误释放。 |
| 终态与真实字节释放分离；清理失败不锁死重建 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:78)；[重建准入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:137) | expired／cancelled／discarded 且已 fence 即不再有发布资格；余账仍占容量／物理预算，受实际水位约束，不再作为有效写意图永久阻 guard。实际释放仍走停写清理屏障。 |
| 旧创建 ID／墓碑过期不能自动新建 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:81)；[Mary 最终命名整合](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/integration-note.md:5)，范围 5–9 | upload_operation_id 唯一作为客户端 UUIDv7 创建 Key，candidate／version 是服务端资源 ID，不再引入第二份上传 header Key。终态同 ID 只回终态；24h／7d 是操作窗口／墓碑，不是成功原件或历史来源 TTL；墓碑清除后按 Key 时间拒旧。 |
| 已完成 GET 重放和带体重复 PUT 不混为一谈 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:83)；[PRD FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:197) | GET 只查原结果，不声称验过新文件；实际 PUT 有当前维护权、原窗口、验证槽／120s／原实际字节上限、真实流式 hash／长度，不能只信客户端 Digest；不新建版本或原件预留，框架暂存另占物理预算。 |
| 不擅改失败保留政策 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:79) | 已完成原件且失败供校核的候选、成功历史原件不会因上传 TTL 被自动删。维护者显式废弃与自动清理未上传意图区分清楚。 |

“有界”指写资格到期与正常受控执行者可终结，并非磁盘／进程故障时凭空释放：停写或清理证据不足保持 cleanup_blocked，保留占用、可见重试，是正确失败分支。未执行的负例已保留在[原 Mary 主答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/answer.md:90)，范围 90–103，以及[追问负例](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/followup-answer.md:79)，范围 79–90。CLOSED 仅说明行为已可实施，不表示这些负例已经运行。

## F2：原主要缺口已落实；继续核对的有限执行上下文待明确

已核对并接受的实际修复如下。

- [全部外传门](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:87)，范围 87–101，明确涵盖纯检索 query embedding、文档／重建分批、答案、图意、MinerU 申请／PUT／轮询／下载。prepared 先持久意图，may_have_sent 临近派发二次条件核验；崩溃后不重发该意图，unknown 不记零，SDK 暗重试默认关闭。只限制新阶段资格，不假称网络与取消原子。
- [迟到成本例外](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:99)允许受控入口按 call_id 幂等追加可验证事实，冲突保双方并待核对，不改业务／配额／历史／guard。可信证据与事实去重的细节见[原 Mary 追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/followup-answer.md:53)，范围 53–57；任意旧 attempt 或前端提交数字不等于可信供应方账据。
- [物理资产与写入者](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:105)，范围 105–119，规定不可复用 prefix、阶段资产清单、每执行槽受监督有界子进程、有限 IPC、旧槽未停不复用；稳定生命周期锁不随资产目录删除，先撤资格→确认全部写入者退出→排它锁复核／清理→条件 cleaned／一次释放。明确 PG 事务不等 OS 锁、网络或进程，统一全局锁序，迟到成本仅锁自己的 call 账，不逆取父业务锁。
- [库任务与当前用户操作分开](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:115)及 [PRD FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:285)规定：原件登记和任务受理事务之前仍是当前维护者写动作；事务合法提交后任务归库，提交者退出／降级不隐式取消。阶段仍查墓碑／恢复隔离／candidate／guard／期限／预算；用户问答派发与输出仍查本人／凭证。降级且仍有库读权者仅能读本人受控任务状态，不保留管理能力。
- [物理压力](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:121)没有声称任何极端满盘状态都还能写墓碑：缺必填预算不新写、保留控制余量，已无法提交时维护隔离由运维恢复。4 GB 子进程峰值是 P0 必测，未伪称通过。

**待对齐 I-M1-01：截止后“继续核对”不能被原任务剩余时间为零堵死，也不能借它续命。**

- 原位置：[契约任务期限](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:117)规定任务自受理固定 2h、每传输取任务剩余最小值，截止后远端 running 进入待核对；[派发门](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:91)要求所有外传核资格／lease／deadline。与此同时 [PRD FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:283)与 [M2 动作表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:29)明确维护者可继续核对、先查原 batch。
- 触发：本地任务已超过 2h，供应方仍 running；有当前维护权者选择继续核对。若复用过期 job 的 lease／deadline，剩余为零而任何查询都不允许；若直接刷新 job deadline，又能违规重启后续下载／embedding／发布。
- 最小整合：明确一次独立、有当前动作授权和有限 deadline 的 reconciliation 执行上下文，只允许查询原已知供应方 ID、回填状态／可信成本，不重置原 job 截止、不新申请／PUT、不恢复业务执行或发布。无 ID 仍 unknown；必要的知情重交另走显式新操作及已有风险提示。它仍必须经过同一 call intent 和派发账本，不成为免守卫外发入口。
- 关闭证明：过期 job 继续核对可在独立上下文有限查询原 ID；原 job 保持终态／原 deadline、旧 attempt 不续租；查询返回成功也不能自动下载／向量化／发布；无 ID 不乱猜／重交；恢复隔离仍按范围及查询动作放行。

**另一个文字明确化：** [Web tasks／动作行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:227)仍统称按当前维护权检查，应将 GET 的本人受控状态只读与管理动作分开，避免挡住 §2.6／FR-15 明确保留的降级本人只读。程序本人的 task-only scope 仍不能读他人任务、候选管理详情或问答结果。这是保持同一政策的措辞整合，不增发现组。

上述两点已真实发给 A；F2 未因此换成一个新编号，也未要求重做研究或向用户访谈。

## 明确化与其他组的状态

- **A-01 收窄后的操作派生动作：CLOSED。** [契约动作规则](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:240)与 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:185)规定 GET operation／同 Key 重放继承原问答或对比动作，同人原渠道新合法凭证可覆盖原范围读取；citation 独立动作不强加 answers scope。没有把所有 GET 当授权，也未把撤旧凭证误当用户永远失去原结果。
- **A-05 前端响应归属：CLOSED。** [契约 §5.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:298)，范围 298–302，及 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:271)从所有私有异步页面开始核账号／登录实例／空间／epoch，落视图前核归属；Abort 非充分，后台恢复先读当前上下文，旧请求不自动换 Key／epoch。取消网络不退款，未承诺追回已合法显示的字节。切片先交身份基础再扩问答恢复，已在前次定点关闭中核验。
- **F4 依赖：保持 CLOSED。** S2 导入 profile／D／generation／revision／发布与最小回看，S1 同事务安全台账与前端身份归属、S0 epoch／调用／物理资产骨架，S6 才增重建管理与完整恢复；未见 P0 反向依赖未实现业务入口。F0 已依 B 的反驳澄清允许未提前调优时在 S7 首子步骤冻结，不要求 S0 前 32 题固定。
- **F3：OPEN。** 本次不复核尚未合稿的协议／token／output 预算，不以 F1／F2 进展覆盖它。

全部 CLOSED 是规划定点结论。当前 S0 可开始，后续 P0／切片前置和最终 SM／权限／故障／恢复都仍须真正执行。

## 原 Mary 补问与实际 §2.7 改稿后的追加复核

本节追加于 I-M1-01 已回到原 Mary 并实际落稿之后；上文保留问题提出时的状态。

**I-M1-01：CLOSED，F2 整组现为 CLOSED（规划层面）。** 我已读取[原 Mary 第二次追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/followup-2.md:15)，范围 15–42，并定点核对实际[实施契约 §2.7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:123)，范围 123–133：

- 核对使用独立 reconciliation_id、当前维护者／epoch／已知原供应方账号和任务 ID，初值整次 120s，最多一次状态查询；费用查询仅在实际协议存在该能力时增加一次，没有虚构供应方接口。
- action_key 按用户＋任务＋动作幂等匹配，重传／重启保原上下文和 deadline，不重发 may_have_sent、不刷新原业务任务 2h 截止；状态 GET／program 只读不能隐式外传。
- 受理、每次派发、放行均复核当前维护权和恢复隔离；无原 ID 不猜 data_id 或客户端任填 ID，不静默换供应方账号。仍用同一 call intent 门。
- ready 只是独立观测；明禁结果下载／解包／embedding／发布／新申请／PUT，不恢复候选／guard／旧任务租约或预留。因而原任务截止不会挡死合法只读核对，也不会被核对绕过。
- 真正本地继续须另行显式新 job／attempt／deadline，终态旧候选必须新候选，重过当前维护权、父级／epoch、KB guard、配置／完整性、原件与物理预算、受监督槽。只复用已验证且兼容、仍保留的产物，或在新资格下按已知原任务下载再校验；必要资产不在则明确失败，重新解析另走知情重交。未将 ready 或临时 URL 当成可发布产物。

[任务 GET 与动作入口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:239)，范围 239–242，也已实际分开：本人且仍有库读权者只读受控状态，当前维护者才执行管理动作；核对与本地继续有具体 POST 入口及 action_key。此前 Web tasks 行与降级本人只读的措辞冲突关闭。

到此 F1／F2／F4 均已定点 CLOSED，A-01／A-05 明确化也已关闭；F3 仍等原 budget Mary 与实际改稿。**仍没有总体 PASS，没有运行验证成绩。**
