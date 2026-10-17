# 独立对抗评审：异步调用 gate 与恢复引导

首审日期：2026-10-16。镜头：Reviewer Gate 配置的独立 adversarial reviewer；headless=true。本报告只改本文件，未读取其他 reviews，也未改主件。后续修订的定向关闭判定追加在末尾，不覆盖首审反例。

**首审 verdict：CHANGES_REQUIRED。** 两个 High 反例尚有实质未决，不能 PASS。已补的跨进程账号共池、唯一领取、唯一释放、迟到成本不退 permit 和恢复不沿旧低计数放额是明确约束；它们未单独消除异步任务占满后读不到终态、以及恢复时先解锁还是先核对的兼容性分歧。

## 实读范围与审时 SHA-256

实读以下五份完整主件，另定点实读现行上游实施契约 §2.5–2.7、§3.8、§4.1–4.4；未以追溯矩阵的既有关闭叙述代替实际条款。以下是首审所读内容的 hash；首审行号指这些版本，后续行号可能因修订移动。

| 文件 | SHA-256 |
| --- | --- |
| [ARCHITECTURE-SPINE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md) | FDEBF60B91BDA73099E9ADA8D74D64D1DB9A185D2416F3A8D3AD992C67D77D40 |
| [shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md) | 6C7EF981055BE260291386F252A9DBF7FCEFD654242FDBE656F5FF4D626B454D |
| [runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md) | A0A7B1F3C9A83F1DAFEE250F21F357973826D580F65E3D252644D36933B10912 |
| [technology-evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md) | F635D7366C9F409D6716C609A676693C4760219A467A8AD1AF1484D59332831A |
| [requirements-architecture-traceability.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md) | 7EAA054B4C62849F5D581D858642DB250616CCCB7AA4A208125E2A74805B1792 |
| [implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md) | C324FC9640DEBB90FA66D689660C2A96B62922A1E7E77A2551ADFD9680476900 |

门槛依据实读 [reviewer-gate.md](/E:/aaa-project/rag/.agents/skills/bmad-architecture/references/reviewer-gate.md)。这是文档反例评审，未执行 PG、Linux、供应方或恢复实测；以下验收项是待取得证据，均非通过声明。

## H1 — High：一个 generic concurrency permit 无法同时解释异步 submit 和 poll

**位置。** [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:131)，范围：131–135；[R1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:17)；[R2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:25)，范围：25–29。AD-7/11 及 C4 每次外传矩阵把所有 call 统一经过 gate，但 C8 的一个 permit 和一个 active→released 没固定“HTTP 请求并发”与“异步任务并发”及各动作的增量。

**两个下一层单位。**

1. execution gate 单位 G：按 C8 为每个 call 在真实账号总池和用途子池原子领一个并发 permit。可能已发且远端终态未明就保持 active，只有可验证远端终态才由 execution 独立短 UoW 唯一释放。所有请求都经过同一 gate，不拆账号额度副本。
2. MinerU 适配器/文档控制器单位 A：一次 submit 得到持久 task ID，远端尚 running；它保留原 call 的远端任务占用，随后用新的 call_id 单次 poll 原 task，先 prepared、临近发送重核 Fence 并领 gate，最多等原 deadline，到期终结本地但不冒称云任务已停。

两者逐字保留 AD-1 的共享用例/PG、AD-2 的 execution 唯一写者、AD-3 的锁序/事务外等待、AD-4 的当前权限、AD-5 的统一 schema、AD-6 的不误发布、AD-7 的一次 grant/禁暗重试、AD-8 的 unknown 成本与独立结算、AD-9 的 guard、AD-10 的预算、AD-11 的有界操作与独立物理槽、AD-12 的状态投影、AD-13 的隔离、AD-14 的 P0 前置。未涉及的路径可完全采用同一基线实现；分歧仅在 AD 未规定的 permit 维度效果。

**最小组合反例。** 已核供应方真正的异步任务并发上限=1，submit 领取 permit 后创建 task T；HTTP 已返回 T，但 T 未终态，所以 G 正确不按 child 退出释放。A 对 T 的正常 poll 是新 call；G 按“每次 call 原子领两层并发”拒绝，因为唯一 permit 已被 T 占用。G 只有看到 T 终态才释放，而 T 终态只能由此次 poll 观察。每个等待都有 deadline，故没有无限占用本地 Session；但每轮到期后都会回到相同状态，正常必需流程永久无法核对、无法释放。手工查厂商后台只能临时绕过该组合，不能作为正常异步任务完成流程的架构定义。反之，若另一适配器把 submit 的 200 当全部并发终态就提前释放，会与 G 保留异步任务并发的解释不兼容，也可能超额。

**最小修复。** 将每个 call 的 permit 定义为按真实限制维度和动作映射的一组组件，至少区分实际存在的 HTTP/request 并发与 async-task 并发；submit 创建 task 占用，poll 引用已持久登记原 task，不再新增该 task 占用，但仍领取其真实适用的 HTTP/RPS/TPM 等组件。按维度定义可验证释放事件及唯一转换；submit HTTP 响应不等于 task 终态。禁止为了活性拆出不存在的“免费核对池”。P0 若不能证明满任务占用时受控终态读取可行，也没有官方有限绝对完成证明，则该异步能力不得启用，不能把正常解析全部导向人工。

**关闭证据。** 文档明确动作→真实维度→增量/引用→终态/释放映射、组件归属与 execution 唯一写者；S0 真 PG 故障例证明各组件唯一释放；P0 真账号任务并发=1 时完整 submit→poll running→poll terminal→task 占用释放→下一次 submit 成功，并证明 poll 未绕过其真实 HTTP/RPS 等限制。重复响应、重复核对、扫描并发不得双退任何层/维度。

处理：**autofix（架构技术定义补全）**；不需要新增产品决策，不可 defer 到单个适配器自由选择。

## H2 — High：恢复的 pool 级 blocked_unverified 与逐动作只读核对未形成共同判定

**位置。** [C8 恢复段](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:137)；[R5 T4/T5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:81)，范围：81–82；上游 [实施契约 §4.2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:274)。pool 持久态统一已解决同名状态漂移，时间窗到期不释放远端任务 unknown 也已明确；仍缺“只读核对所需各维度已证，但其他维度未证”时的可执行放行条件。

**两个下一层单位。**

1. 恢复控制/gate 单位 R：旧包恢复后把全部共额 pool 设 blocked_unverified；独立受托人核完整账号未决调用后才逐 pool 放行；task unknown 不能仅凭窗口到期解除。R 把 pool 控制态作为所有 call admission 的前置条件。
2. 恢复核对用例单位 Q：按 T4/T5 为已核账号/资料范围和外部只读动作单独登记放行，绑定原持久 ID，创建有限 reconciliation 上下文；它仍由 execution gate 领取真实限额，不使用新账号/假池，也不复活原 job。Q 希望以该受控 poll 获得未决 task 的终态，作为 R 最终放开新增任务能力的依据。

R 与 Q 都遵守 AD-13 的独立信任/逐范围放行、AD-7 的每次 guard 与单 grant、AD-11 的同账号共池，以及 AD-2/3 的唯一写者与锁序；其余 AD 可完全保持同一实现。C8 未规定 blocked_unverified 是阻全部动作还是仅阻尚未证维度的新增消耗，R5 的“外部只读/付费分别放行”也没有定义对 C8 的效果，所以双方分别实现自己条款仍不能完成协议。

**最小组合反例。** 备份后有调用丢失，但原包内还保留可核对的 task T。身份/资料范围/key_id/真实共额域已独立核验；RPS 窗口已可证届满，HTTP 请求并发也已取得可信安全依据，任务维度仍 unknown。Q 的唯一读操作只引用 T，不新增异步任务，但 R 以整个 pool blocked_unverified 拒绝。若操作者直接把整个 pool 放开以准许 Q，又会同时使新增 submit 可使用备份里的旧低 task 计数。两种做法分别造成恢复引导环或突破未知任务占用的保护。当前稿说“分别放行”仍不足以让两个单位共享同一个判定。

**最小修复。** 在同一个真实 pool 内持久记录逐维度/动作的核验与放行清单，明示 admission 为所有实际适用组件的合取；已知原 task 的只读核对可在其实际 HTTP/RPS/费用等维度均已证且范围/动作被明确放行后执行，task unknown 只禁止会新增该 task 维度占用的动作。若 poll 自身也受某个尚未证的真实账号 HTTP 并发或同类 task 限制，仍不得放行。新 epoch、RPS/TPM 到期和已知某一个 T 的终态都不能自动证明备份后丢失的其他调用已终止。

**关闭证据。** 同一份共享动作/维度映射驱动 C8 与 R5：恢复旧低计数、有/无持久 ID、仅 RPS/TPM 窗口已证、HTTP 维度未证、已知 T 终态但其他丢失任务仍 unknown 等负例，逐个给出 read poll/new submit 的准许/拒绝及依据；S6 实际保存独立受托人、来源、时间、范围、动作/维度清单，证明只读放行不意外启用付费新任务。无法核清仍维持相应维度阻断，不虚构丢失 ID。

处理：**autofix（共享控制语义补全）**；可与 H1 使用同一动作/维度契约修复，首审保留为独立恢复反例。

## 边界检查：may_have_sent 与真正发送不原子，不据此要求零费用承诺

上游 [实施契约 §2.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:101)、AD-7 和 [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)已明确：提交可能已发后暂停，传输可能在取消/失租后到厂商，不能承诺撤销后零字节/零费用，不能将其补记 not_sent。故“取消后仍收费”本身是已声明边界，**不列第三个发现**。

但官方绝对执行上界的证明必须覆盖实际可能到达的时间：在 t0 提交 may_have_sent，child/grant 暂停到 t1 才到厂商，厂商“受理后最多 L 秒”只能证明 t1+L 后终态，不能自动证明 t0+L。若仅将 DB 窗口或任务占用锚在 t0 并在其届满时断言实际远端资源空闲，会超出“已证官方绝对执行上界”的条件。可接受证据应包含真实发送/受理时间上界或可证停止所有可能晚发者后再覆盖厂商有限余量；无证仍 unknown，不以业务 deadline 推厂商终态。RPS/TPM 的本地保守窗口也不能被表述成厂商永不 429 的保证。此边界需要纳入最终条款与故障验收，未进行实际暂停/恢复测试。

## 其他定点结论

- 唯一写者、固定锁序与迟到事实隔离：本轮未构造出让 ledger 合法反向取 pool 释放并发的反例；C8 明确 execution 独立短 UoW 与唯一 release_transition，迟到账只补事实，不据此退 permit。
- 来源与状态：C3 已固定不可变 UTF-8 hash、Unicode 标量偏移、PDF rotation/CropBox、实见 spans 和当前权限回看；本轮未发现允许两个合规适配器各选页基数/offset 的未决空间。没有把“未发现”写成实现已通过。
- P0/运行门：技术证据把公开文档、依赖安装和真实账号能力分开，待证明项均保留门槛。本报告未重复验证网络上的版本号，也不把五主件的自述视为运行成绩。

## 修后定向复核

尚待实读修后主件并追加关闭判定。在此之前维持 CHANGES_REQUIRED。

### 用户新增异步并发范围的定向记录（最终签署前）

首审后收到本轮明确用户变更：文档活跃 job 和外部异步 task 的全系统本地 gate 默认4、允许配置1–4，本机重阶段仍1。这是新增授权范围，首审并非针对该新策略。已实际读到 [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)，范围：135–145 的新定义，并向作者指出新增 gate 必须拥有独立领取/释放点与统一锁序；本轮实稿已补：

- queued 创建不占 doc_active_job；worker 条件领取开始处理的同一 UoW 占位，业务终态/到期 fence 按 job_id 一次归还，不刷新原2h期限。
- external_async_task 在 submit 的 may_have_sent 同 UoW 按原 call 唯一占位；只有可信 task 终态/可证上界才和对应厂商维度一次归还，job 终态不退未知 task。
- execution 是两个本地 PG gate 的唯一写者；本地 gate 位于空间账之后、provider pool 之前，释放也同序，不建立进程内第二份总额度。恢复本地 task gate 也先 blocked_unverified，独立核未决事实，不按旧低值重开。
- 有限轮转每活跃 job 每轮至多一个到期可执行阶段，到期 poll/reconciliation 先于新 submit；poll 不新增 job/task 名额但继续受真实 HTTP/RPS 与传输槽限制。
- accepted 后先持久保存原 ID/fence/deadline，确认本次 child 停写退出、FD 关闭及结果落盘后才返还本地物理槽、调其他 job。远端 pending 不持 Session/正文 buffer/每任务常驻线程或 child，因而能产生真正的远端重叠。

这些定义消除了本轮新增的占位时机、反序锁与调度公平性分歧；最终结论仍须以全部受影响主件和现行上游完成同步后的 hash 签署。运行验收必须分别验证1档和4档：满 task gate 的正常 poll；submit 占位提交前后故障；重复终态只退一次；取消/超期后 unknown 不退 task；普通重启不重复领/重发；备份恢复丢失 inflight 不放额；4个远端任务真实重叠且本机重阶段≤1；查询/上传同时存在时 RSS、FD、磁盘和阶段/全系统预算均不过界。未证4档不开4档，文档中的默认4不构成真实账号或4GB资源成绩。

### 最终定向关闭判定：PASS（架构文档镜头）

2026-10-16，作者明确五主件语义停止修改后，本 reviewer 再次完整实读五主件；另实读现行 [实施契约 §2.6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:107)，范围：107–115，以及 [历史技术对话本轮 override](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:238)。未读取其他 reviews 或仅依据作者的关闭结论。

**当前 verdict：PASS；本镜头未解决的 material finding=0，Critical=0、High=0、Medium=0。** 首审 H1/H2 的问题与反例保留为历史，以下实际新条款排除了它们；这不是 P0、S6 或应用运行通过。

| 定向项 | 实读后的关闭依据与边界 |
| --- | --- |
| H1：满异步 task 后 poll 自锁 | **CLOSED。** [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:131)，范围：131–143，已规定真实限制维度/动作、有限 permit_components、submit 才新增 task、已知原 task poll 只引用 task 组件且仍领实际 HTTP/RPS 等组件；HTTP 响应不释放 running task，每(call,dimension)唯一终态释放。满 task 池仍必须证明受控 poll 的活性；真实限制不支持且无可证通道/有限上界则不启该组合，不能只靠人工完成正常流程。R1/R6/R7 与 P0 门已同步，原 G/A 两单位不能再合法选择相反的 task 增量。 |
| H2：恢复整 pool 阻断只读核对 | **CLOSED。** [C8 恢复段](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:145)与 [R5 T4/T5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:85)，范围：85–86，现明定先 blocked_unverified，独立受托逐维度/动作核实、重建本地/账号/用途占用；只读 poll 在其所有实际适用维度已证且范围/动作放行后可执行，不再被“不新增 task”的未知 task 维度一概拦住；实际 HTTP 等维度未证仍拒绝。窗口到期/新 epoch/旧低计数均不解未知 task，未凭一次 T 终态断言丢失的全部调用已停。原 R/Q 单位必须共享这一判定。 |
| 延迟发送与官方上界 | **边界已明确。** [C8 组件释放](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:141)与 R1 明确上界须覆盖最晚可能实际到达，禁止直接从 may_have_sent 本地提交时间加厂商执行时长自证。仍保留网络非原子/撤销后可能收费边界，没有提出违反上游的零费用保证。 |
| 新增全系统 1–4 job/task 并发 | **本轮 delta CLOSED。** [AD-3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:71)、[AD-14](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:137)与 [C8 本地 gate](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)，范围：135–137，固定两个各默认4/可配1–4的全系统独立 gate，非每账号各4、非 job/task 元数据合计4；job 领取/终态与未知 task 的独立生命周期、唯一 transition、local gate→provider pool→call→component 锁序与恢复 blocked 均明确。有限轮转每 job 每轮至多一个到期阶段、到期 poll/reconciliation 先于新 submit；远端 pending 不持常驻 child/线程/正文/Session，停写关 FD 后才返单物理 stage，因此允许真正远端重叠。现行上游 §2.6、R1/R3/R5–7、技术 E4 与追溯矩阵已同步；历史对话追加 override 并保留当时记录。1/4 档资源、故障和公平性实证仍是停止门。 |
| task 单位与跨 job 批处理计数 | **定点确认。** [C8 调用映射](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:133)明确 submit 按官方实际新增/触发动作定义，不按 HTTP 方法/端点名猜；首版一文档 job 一个原 task，不跨 job 合批云解析，不允许一 call 新增 N task 却算1。未留计数粒度分歧。 |
| C7 空库 absence | **定点 CLOSED。** [index_generation DTO](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:120)允许空库 active_generation_id/profile_id 为 null，禁止伪造 ID；活动代必须绑定已证不可变 profile，rebuild 非 null 须有已证 target_profile。未知与不存在均有明确表示，未要求空库先虚构可用 profile。 |

最终审时字节 hash 如下。之后若仅 lifecycle/status/最终签署元数据变化，应由 gate 另记 hash delta，不能将新字节冒称与本表相同；任何语义变化须重新定向复核。

| 文件 | 最终审时 SHA-256 |
| --- | --- |
| [ARCHITECTURE-SPINE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md) | CEDF3465762A5D810499C3B33721574708F36BD44220617657DF1E6A6974343E |
| [shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md) | 9CE67591601EFAF1130197457D8A4894D3FF0919641074BE1219ECA70614187E |
| [runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md) | 70FA034F0A2255367F2830C6B90B55DA46138A4FB61687749D035DC2C850CD6C |
| [technology-evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md) | 6030578B6C16494BC46CC74C36BFD1437C8A3AC8ED71EAB7701A6702699819AF |
| [requirements-architecture-traceability.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md) | BE60629E093A4C558417C292BDF53CB3A027B3984045521269A4CF347C5C022F |
| [implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md) | 9695CAEC3D1505432AA1BA0999D501DB22B99F4F3EF8AB64BF42D9304B636D4F |
| [technical-decisions-dialogue.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md) | 73261E5C4995085B58EA3C46E34B85EFB399DFB8ECE33F05A5A631474A5CFAE7 |

本次仅形成文档审查证据。没有运行 PG/供应方/目标机或恢复测试；未知官方维度/额度、真实满池 poll、4档资源与恢复演练继续按 P0/S6 阻断，不能借此 PASS 开启未证能力。
