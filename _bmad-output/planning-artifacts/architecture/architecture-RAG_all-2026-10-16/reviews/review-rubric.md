# 架构主干独立评审：Good-spine rubric

评审日期：2026-10-16。评审对象为 initiative 层 draft 及其四份 companion；只写本报告，未修改主干。未阅读作者初评、讨论或 handoff。评审期间已纳入共享契约 C7、C5 分页边界及技术证据 E4 的当次更新。作者随后表示将修订 RUB-01；以下发现保留其被检出时的证据，不能当作修订后复验通过记录。

**判定：需定向修正后定稿。无 Critical；1 High、1 Medium。S0 独立工程骨架可以开始；供应方账号共享限流契约应在真实外发前固定，删除锁例外应在 S1 权限实现前澄清。**

## 审查范围与尺度

采用 [Good-spine checklist](/E:/aaa-project/rag/.agents/skills/bmad-architecture/references/reviewer-gate.md:13)。已读 [架构主干](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1)、[共享契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:1)、[运行契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:1)、[技术证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:1)和[需求追踪](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md:1)，并按需核对现行 PRD、实施契约和实施切片。未发现可据以 ratify 的应用代码；本评审不制造运行成绩，也不将 P0/S6 尚未实测算作架构本身失败。

## 需处理的发现

### RUB-01 — High：账号总限流缺少跨进程共享状态的唯一所有者与池身份

**证据。** [模块所有权表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:29)明确 execution 的物理槽和 ledger 的逐 call 意图，但未分配供应方 rate gate 的写所有权。[运行契约 R1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:15)区分物理槽与账号限额；[R6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:87)要求单用途 provider 并发/TPM/RPS，[观测行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:98)说用途 gate 与账号限制取小；然而 [C4 每次外传事务](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:65)只有资格、Fence、预算和 call 状态，没有共享账号 permit 的原子领取、聚合键或锁序位置。上游已经要求所有用途不能绕过账号 gate，见 [实施契约 §3.8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:260)。

**具体反例。** API 的 query embedding 与 worker 的 document embedding 使用两个配置或轮换后的两个凭据，但实际共用一个供应方账号/地域配额池，已核账号上限为每秒 1 次。两组实现者分别在 API、worker 内建用途 gate，或按 config_id 建 PG 桶；每路都采用 min(本地 1 RPS, 已核账号 1 RPS)，同一秒各合法领取一次，再各自完成 prepared→may_have_sent→grant。各调用都满足当前描述的单路阈值和每 call 一次规则，账号合计却发出 2 次；同样的问题会出现在共享 TPM 和远端并发。把两个本地数字都写成 1 并不能实现一个共享账号总池。

**为什么属于本层。** 这里缺的不是 P0 才能测出的额度数字，而是 API/worker、查询/导入/图意/计数等独立功能必须共用的状态边界。AD-2 的“每份状态只有一个写者”尚未覆盖这份状态；不能把它作为某个适配器内部实现或等接通后才临时决定。

**最小修复（autofix）。** 指定一个领域模块独占 PG 共享调用 gate；登记稳定的 provider 账号/地域/实际配额池身份，明确换密钥不重置池，同池跨用途/进程聚合。每用途子限额与账号总池须在一次短 UoW 中为 call_id 原子领取唯一 permit，并给出它在全局锁序的位置、领取失败的有界等待/拒绝动作。规定 RPS/TPM/远端并发的保守占用依据，以及 may_have_sent/unknown 不因本地 child 停止而虚假归零；池范围或必要计数未证则不派发。具体窗口算法与 SQL 可留实现。

**完成证明。** 真 PG 并发测试使用 API 与 worker 两控制器、同池不同 config/key，断言账号总额只有一方取得 permit；重启、凭据轮换和 unknown 不增加额度。证明用途子限额仍受总池约束，gate 等待不持 Session、不增加查询等待队列。修复阻断真实共同账号派发，不要求等待完整 P0 或停止其他 S0/S1 工作。

### RUB-02 — Medium：整体删除“仅 space EX”可被误读为豁免操作者账号锁

**证据。** [C4 通用规则](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:55)要求所有需当前授权事务按账号 SH→space→KB；紧接着 [覆盖说明](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:57)又写“只改space的整体删除可仅space EX”。这里没有说明“仅”是只省去 KB/子资源锁，还是允许省去操作者账号 SH。后者与 [AD-3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:67)和 [AD-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:73)的当前账号串行化原则不一致。

**具体反例。** 删除团队的实现者把专门一句视作通用锁规则的例外：读取操作者仍 active 后只持 space EX，准备提交墓碑。平台停用账号事务只需该账号 EX，能够先完成停用/撤凭据；删除事务仍可按先前读取的账号状态提交。另一实现者保留 actor SH→space EX，则停用与删除有明确串行次序。两种实现对撤权生效边界产生不同结果。此处是可执行的歧义反例，不声称当前已有漏洞或作者必然采用了前一种解释。

**最小修复（autofix）。** 把该句限定为：“用户发起的整体删除仍先持操作者账号 SH，再持 space EX；若仅登记父级墓碑可省略 KB/子资源锁。只有已明确授权且不依赖当前用户的后台/恢复用例才适用无用户锁路径。”同时保留账号→space 的统一顺序，不能取 space 后补 actor。

**完成证明。** S1 用两个 PG 事务覆盖账号停用/凭据撤销与用户发起整体删除，断言删除要么在安全变更前完成授权提交，要么在其后重新校验并拒绝；不得出现只锁 space 后引用过期账号判断的分支。该澄清不阻 S0。

## 逐项 rubric 结果

| 检查维度 | 结果与依据 |
| --- | --- |
| Initiative 层是否固定真实分歧点 | 基本充分。八模块、四服务、唯一状态所有权、同 UoW、当前权、三账、版本/代次、执行物理槽、来源和有限生成均已固定；RUB-01 是剩余共享控制状态缺口。 |
| AD-1 / AD-2 | 可执行。入口共用 application、向内依赖、仓储写能力边界能直接转为导入/仓储约束；AD-2 需补账号 gate 所有权。 |
| AD-3 / AD-4 | 可执行。账号/space 控制行与全部子表写入覆盖、防反向锁及当前鉴权已有实质规则；RUB-02 应消除局部例外歧义。 |
| AD-5 / AD-12 | 可执行。唯一 schema、TS 导出、Unicode 标量偏移、SourceLocator、五独立投影、有限 allowed_actions、响应归属与 UI 不裁128均有对应契约；新 C7 已补公共状态表示。 |
| AD-6 / AD-7 / AD-8 | 可执行。上传意图、原件预留转实占、FS/PG 恢复、prepared/may_have_sent、实际 writer 持锁、cleaned 与唯一账转换有可测试顺序。没有把进程已重启/仅 unlink 当停写证明。 |
| AD-9 / AD-10 / AD-11 | 可执行。不可变 profile、D 显式迁移、generation/revision/guard、固定快照、K≤5、实见 catalog、零候选与预算裁空分支、原 Key 重放、会话父轮次与单未终结指针均能防止所列分歧。 |
| AD-13 / AD-14 | 可执行。独立 epoch/受托链、成套备份、逐范围隔离放行、S0/P0/F0/S6/S7 的不同停止点已列出；没有把文档完成或官方组件版本当真实运行通过。 |
| Deferred 是否藏共享契约 | 表列/SQL/内存数值、宿主补丁与证书、真实用途 profile、冻结题实施等可后置，均有触发/停止点；账号 gate 的所有权和共享池身份不能随额度数字一同后置。未见其他已明确留给各功能独立选择的共享语义。 |
| 结构与运行整维缺失 | 未发现。代码/服务结构、部署和环境、持久介质与权限、启动迁移/失败回退、资源保护、观测、运维、备份/可信恢复均已决定或显式设门。单机非 HA 是显式边界。 |
| 能力覆盖 | 追踪覆盖 FR-1–16、NFR-1–6、SM-1–7、实施契约各节及 UX IA/G/AC；抽核四场景、原件/来源、图意专项、程序只读、历史/引用、恢复与实验冻结，未发现整项能力脱落。追踪表不是成绩，这一点表述正确。 |
| 技术证据 | 有明确冷启动版本、官方来源和安装/组合验证停止点。独立抽开 PostgreSQL 支持表、pgvector 仓库、Pydantic 2.14.1 及 Vue Router 5.4.0 发布页，与表述一致；未声称本评审重复安装或逐一实测所有组件。 |
| Brownfield / 父级继承 | 文档明示当前无应用代码，搜索未发现排除规划/技能目录后的应用源码；因此没有用新主干覆盖现实代码。上游实施契约被声明为业务真源，未发现需要重新决定产品权限、K、计账或 SM 的冲突。 |

官方抽核依据：[PostgreSQL versioning](https://www.postgresql.org/support/versioning/)、[pgvector 官方仓库](https://github.com/pgvector/pgvector)、[Pydantic 2.14.1 工件](https://pypi.org/project/pydantic/2.14.1/)、[Vue Router v5.4.0 发布](https://github.com/vuejs/router/releases/tag/v5.4.0)。这些链接只支持存在的版本/机制，不支持本项目组合已安装、4GB 已通过或供应方能力已验证。

## 处理建议与边界

RUB-01、RUB-02 均可由作者直接补契约后定点复核；不需要新增产品决策、服务、队列或批准流程。不应将 MinerU/Qwen 用途能力、D、许可外传边界、TPM/RPS 数字、目标机资源和可信恢复尚未实测重新包装成设计阻塞：现稿已保留对应停止点，后续必须依真实证据执行。修订后的主干是否已满足本报告，需要另一次针对修订内容的确认，本报告没有预先授予 PASS。

## 2026-10-16 定向修订复核

仅复核 RUB-01、RUB-02 的实际修订，不重新审查全包；原发现保留为审查历史。

**RUB-02：关闭。** [C4 当前文字](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:57)已经明确用户整体删除先持操作者账号 SH；不必锁全体成员账号 EX 不再等于免操作者鉴权，后台免用户路径只限已合法受理库意图。原“删除与停用无共同账号锁”的反例不再符合当前契约。

**RUB-01：主要缺口已关闭，剩余远端并发许可一次释放需一句明确约束。** 已实际核对 [execution 写所有权](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:34)、[AD-3 锁序](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:71)、[AD-11](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:119)、[C4 派发 UoW](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:65)、[C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:125)及 [R1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:17)/[R3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:43)/[R6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:89)。确认内容为：

- execution 独占 RatePool/CallPermit；provider_account_id+region+rate_pool_id 映射真实共额域，换 key/配置/用途/进程不能复制额度。
- may_have_sent 同一短事务按 pool 升序原子领取账号总池及用途子池，call_id 唯一 permit；未知账号范围或限额不派发。
- 持久 DB 时间窗口不因重启重置；TPM 采用完整输入和最大输出/思考上界；may_have_sent/unknown 保守计占，迟到 usage 只补事实，不反向取 pool 退保守窗口。
- 逻辑产品预留、物理 child 槽与远端并发分离；child 停止不构成远端结束，未知终态且无官方有限上界则 pool 阻断。内部等待仍受原 deadline 限制且不持 Session。

这些已排除了原来“两进程各发一份账号额度”的反例，确认依据不限于存在 PG 表。

**窄残留（Medium，RUB-01 的释放子问题）。** C8 对 prepared 永未发明确“唯一条件释放”，对已发远端并发只说未知时不得归还；R1 允许可信终态后“条件调整”，尚未明确该 permit 只能归还一次。若迟到可信响应和显式核对均观察到同一远端 terminal，两条执行路径可能各减一次池计数；“唯一发一个 permit”本身不能证明“只释放一次”。最小补句为：execution 独立短 UoW 按 pool 升序再锁 permit/call，仅在可信终态或可证官方上界到期后条件将 active→released，同事务归还账号/用途并发；重复响应、重复核对或重复到期扫描零效果；ledger 迟到事实入口仍只锁 call，不直接退 permit。该残留属于设计文字明确性，不是要求现在提交运行测试成绩。

**本次定向判定：RUB-02 已关闭；RUB-01 原 High 的共享池主体设计已修复，剩余上述 Medium 一次释放约束，补齐后可关闭这两项。** 实现阶段仍需原报告的真 PG 并发、重复响应/核对、重启/轮换与 unknown 负例；文档复核不代表它们已运行通过。

### 定向补句确认：两项关闭

已再次读取实际 [C8 第131行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:131)：现稿明确由 execution 独立短 UoW 按 pool→permit/call 锁序处理；须有已持久、可验证的远端终态或已证官方绝对执行上界到期，使用唯一 release_transition_id 条件 active→released，并同事务只归还一次账号总池及用途子池并发，重复响应/核对零效果。迟到成本入口不能释放许可，RPS/TPM 仅自然到期，不提前返还。[第129行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:129)也已澄清 prepared 尚无 rate permit，不能归还未领取额度。

该补句使“同一远端终态经响应与核对两次观察”的反例只能第一次改变许可及两层计数，第二次条件更新零效果；原窄残留关闭。

**当前修后判定：PASS（本 reviewer 的 Good-spine rubric 及两项定向复核范围）；RUB-01、RUB-02 均已关闭，无残留发现。** 原报告中的需修判定和中间残留是历史记录，以本段当前判定为准。此 PASS 允许设计定稿与按门槛实施；P0/S1/S6 等真实并发、供应方及运行验证仍按既定停止点执行，不视为已经通过。
