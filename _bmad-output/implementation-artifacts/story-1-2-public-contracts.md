# Story 1.2 公共契约

由主控统一登记；语义来自原 Story 1.2、C4/C5、R1/R2 和实施契约 §2.5。实现者只修改其唯一归属文件；契约变更先回报主控。本文是接口决定，不是应用代码。

## B：EgressTarget

2026-10-18 采纳 Faraday 只读阶段提出的接口：

- [领域接口](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/egress.py:1)：`EgressPurpose`（api/upload/download）、`HostPort(host, port=443)`、`EgressProfile(purpose, allowed_targets)`、`EgressTarget(profile, host, port, request_target)`、`ResolvedAddress(family, address)`、`EgressPlan(target, addresses, connect_address)`、`EgressRequest(method, headers, body, api_authorization)`、`EgressResponse(status, headers, body)`。
- 同文件提供 `parse_config_target(url, profile)`、`parse_signed_target(url, profile)`、`resolve_egress_plan(target, resolver)`；端口 `DnsResolver.resolve(host,port)`、`EgressConnector.connect(plan)`、`EgressConnection.sendall/makefile/close`。
- [适配器](/E:/aaa-project/rag/backend/src/rag_app/adapters/egress.py:1)：`SystemDnsResolver`、`TlsBoundConnector(timeout_seconds=10, ssl_context=None, socket_factory=None)`、`OneShotHttpTransport(connector,max_response_bytes=1048576).send(plan,request)`。TLS 注入 context 仍须 hostname 校验及 CERT_REQUIRED；选定一个已核地址，不自动回退/重试。
- `EgressError(Exception)` 独立于现有 SafeError，只有有限 code（CONFIGURATION_INVALID/DEPENDENCY_UNAVAILABLE）和 failure 枚举，不保留原异常/URL/秘密；C 在调用结果边界传递有限 code。B 不修改共享错误文件，避免并发写。
- 配置/签名 URL 的可见 ASCII wire 格式保留 path/query 原值；原始 Unicode 由配置来源进行明确 percent-encoding，守卫不隐式重编码或改写签名。准确 hostname/端口匹配，不用子域通配。长度仍按原 C5 两种单位验证。
- 全部 DNS 地址验证后固定选一个，直接连接其 IP；TLS SNI/证书和 HTTP Host 仍是原准确 host。一次传输不跟随 3xx。Authorization 仅 API 用途，上传/下载拒绝；普通 headers 不得绕入保留的鉴权/Host/HTTP framing 头。
- C 复用 B 的守卫与 OneShotHttpTransport 接口；当前只有显式网络假件，真实供应方运行 gate 保持关闭。未来大文件流式处理属于实际文档管线，不为本条增加新下载要求。

B 唯一写入：[领域接口](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/egress.py:1)、[适配器](/E:/aaa-project/rag/backend/src/rag_app/adapters/egress.py:1)、[专题测试](/E:/aaa-project/rag/backend/tests/test_egress.py:1)、[交付文档](/E:/aaa-project/rag/docs/story-1-2-b-delivery.md:1)。规格/台账由主控维护。

## C：child 监督

2026-10-18 采纳 Heisenberg 只读签名，领域接口写入 [supervision.py](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/supervision.py:1)，适配器为 [child_supervisor.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/child_supervisor.py:1)，子入口为 [call_child.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/call_child.py:1)：

- `ChildLimits(max_frame_bytes=1048576,max_result_bytes=1048576,max_stdout_bytes=65536,max_stderr_bytes=65536,startup_s=5,term_grace_s=5,kill_grace_s=10)`；`ChildSlot(deployment_id,boot_id,slot_id,attempt)`；`ChildIdentity(slot,child_instance,pid,process_group,start_ticks)`，启动实例与 Linux start_ticks 避免 PID 复用误判。
- `StageCommand(call_id,attempt,stage,payload)` 只传一个有界阶段，无 grant/secret。`ChildStage` 为 model/parse/embedding/vision/egress，当前全部显式假件；child 不自主进入下一阶段。
- `SendGrant(grant_id,call_id,attempt,boot_id,child_instance,send_stop_by_monotonic,plan=None,request=None)`。**采用 EgressPlan 而非未解析 EgressTarget**：controller 在 PG 事务外用 B 的守卫解析全部 DNS并固定地址，child 消费该 plan，不二次 DNS。request/plan 的秘密字段不打印。
- `ChildResult(call_id,grant_id,send_state,response_status,payload,failure=None)`；SendState 为 not_sent/may_have_sent/response_received。grant 写入之后的失败/EOF/超时均保守为 may_have_sent，不根据 child 自述降回 not_sent。
- `ChildSupervisor.spawn(slot,limits)`、`prepare(identity,command,timeout_s=...)`、`grant(identity,grant)`、`receive(identity,timeout_s=...)`、`stop(identity,reason)`、`inspect(identity)`；身份错绑/重复grant有限失败，不静默消费。
- `StopProof(identity,exited,exit_code,process_group_empty,no_descendants,ipc_closed,send_fds_closed,grant_destroyed,proven_monotonic,failure=None).proven` 仅在全部必要证明满足时为真。期限和仅 PID 消失不证明停止；未知保持槽阻断。stop/等待/IPC 均不在 PG 事务内。
- 参数数组、shell=False/start_new_session/close_fds/pass_fds 和环境 allowlist；只有私有 socketpair 的有限长度帧承担 command/grant/result。秘密不入 argv/env/stdout/stderr/普通日志。

C 先写无 A 依赖的监督/child/专题测试；A 的调用集成签名登记后再写 [call_dispatch.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:1) 及其测试，不重写 A/B。

### C 当前完成门纠正

2026-10-18 完整差异检查确认以下原AC2/R1义务尚未实现，交回C，不涉及1.3 rate/permit或1.4资产清理：

- I2：实际物理槽身份是deployment+slot，不能以新boot绕开旧占用。占用/启动实例清单须在合适本地FS持久并跨控制器/监督实例共用，尚未证明旧child/FD/IPC/grant停止时保持阻断。spawn失败后未经确认的存活者也不能因删除pending而失去认领；新实例/新boot测试必须在旧child仍活或停止未证时拒绝同一槽。明确state_root和组装入口由C给出。
- I2同一停止证明边界：`/proc`不可读取/无法核实不能当成“无进程/无后代”；stop未知或启动标识不匹配的身份，不得向可复用PID/进程组发信号。恢复只操作所属已登记且身份核实的child，缺证持续STOP_UNPROVEN。
- I3：IPC deadline是绝对时间。分段recv或InterruptedError之后重新计算剩余时间；不能只设置一次socket timeout让持续小块输入无限延长阶段。Linux socketpair慢速分段输入须在原deadline有限超时。
- 初次四文件冻结hash保留为未运行草稿来源；C重新打开自己的四文件完成上述修正、补必要测试后再次冻结。无需新增外部服务或泛化防护；公开ChildSupervisor方法不变。此处只修正已有明确义务。

## A：持久调用

2026-10-18 采纳 Euclid 的最小签名：

- [execution/calls.py](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/calls.py:1)：`Epoch(deployment_id,epoch,cutover_at,maintenance_version)`、`ExecutionFence(epoch,owner_context_id,attempt,claim_token,lease_until,hard_deadline)`、`CallGrant(call_id,attempt,boot_id,child_instance,grant_id)`。
- [ledger/facts.py](/E:/aaa-project/rag/backend/src/rag_app/modules/ledger/facts.py:1)：`UsageFact(status,prompt_tokens,completion_tokens,total_tokens)`；`CostFact(kind,amount,currency,basis)` 的 kind 为 estimated/actual；`ResultFact(outcome,provider_ref,usage,cost,at)` 的 outcome 为 responded/known_failure；`LateFact(provider_ref,usage,cost,source,received_at)`；`LateFactOutcome(disposition)` 为 appended/duplicate/conflict。缺失数值为 None，不转零。
- [call_lifecycle.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_lifecycle.py:1) 的 `CallLifecycle` 提供以下方法；每个 uow 由 application 管理，返回后事务已关闭，仓储不提交：

| 方法 | 参数（除 self 外） | 返回 |
| --- | --- | --- |
| prepare | uow；关键字 fence,holder_id,space_id,purpose,stage,config_fingerprint,request_hash,now | call_id 字符串 |
| mark_may_have_sent | uow；关键字 call_id,fence,boot_id,child_instance,now | CallGrant 或 None |
| record_result | uow；关键字 call_id,fence,result | None |
| record_unknown | uow；关键字 call_id,fence,now | None |
| record_late_fact | uow；关键字 call_id,fact | LateFactOutcome |

上述类型均为 frozen dataclass。`EpochControl.current()->Epoch`；`verify_mirror(session)->None`；独立控制读取/OS等待不跨PG事务。先读取控制值再用短事务核镜像，缺失/矛盾隔离，不自动补造或轮换。

`prepare` 和 `mark_may_have_sent` 均核当前 fence 与归属/配置；mark 仅 prepared 原子转换一次且提交后返回grant，重复/旧fence无grant。C 将 A 的 CallGrant 身份字段转换为其 SendGrant，补本地有界stop-by和已核plan/request；不得自行生成第二次grant资格。旧fence的业务发布失败，可信迟到结果转 record_late_fact，保持原业务/许可不变。

A 的仓储与 epoch 适配器组装细节自行实现并在交付中给出构造/夹具入口，C 不提前猜测；这些不改变上表。A 唯一拥有上述文件、其余非egress/非supervision的execution/ledger持久端口、[call_postgres.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/call_postgres.py:1)、[epoch_control.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/epoch_control.py:1)、新0002迁移、bootstrap、必要旧迁移/revision测试、conftest和[errors.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/errors.py:1)中所需有限错误。B/C不修改这些文件。A负责准备C可复用的真实PG配置/上下文夹具入口，禁止自动建立生产epoch。

A已报告必要共享变更 [uow.py](/E:/aaa-project/rag/backend/src/rag_app/application/uow.py:1)：回滚/清理成功后保留有限GuardError；有cleanup失败时仍走原有限数据库错误路径。主控读取实际差异后接受此窄事务边界兼容修正，归属仅A；原UoW/资源清理回归须运行。

已落盘组装入口为 [build_call_lifecycle(control,schema)](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:67)，返回 `CallLifecycle(control,stores)`；[call_persistence夹具](/E:/aaa-project/rag/backend/tests/conftest.py:176)提供 engine/schema/uow/control/epoch/lifecycle/control_path。

### 当前上下文权威核对

2026-10-18 集成检查确认：现有 prepare 仅持久传入fence、后续仅与call快照比较，尚不能证明终结/替换attempt后旧fence失效。这是原AC1/C4/R2的必需补齐，不新增未来身份/预算/gate功能：

- A 在本条0002中加入最小持久执行上下文，保存当前owner_context_id/epoch/attempt/token摘要/lease/deadline、active/terminal/isolated状态、holder/space及配置归属。
- prepare、mark与有当前资格要求的业务转换从当前上下文读取并复核，按context业务锁→call锁；不能将传入快照或call旧快照当成当前权威。当前lease/deadline必须来自持久行，不允许调用者延长期限。
- A 提供供显式假件受理/测试使用的受控上下文初始化/终结/换attempt入口，交付精确签名给C；现有五个调用方法不变。PG负例须先在持久上下文终结/更换token或attempt，再验证旧fence零grant/零业务写；不能仅构造不同入参来证明。
- 迟到可信事实仍只锁call，不读取该上下文、不因其终结或旧epoch而拒绝，也不改变上下文/产品/会话/许可。上下文表只承担本条最小执行权威，后续真实业务继续由所属模块提供资格。

I1受控初始化接口已落盘，供C集成，均位于上述CallLifecycle；仅显式受理/维护假件调用，不由缺失context自动触发：

- `initialize_context(uow, *, context_id,holder_id,space_id,purpose,config_fingerprint,attempt,claim_token,lease_until,hard_deadline,now) -> ExecutionContext`。
- `advance_attempt(uow, *, context_id,attempt,claim_token,lease_until,hard_deadline,now) -> ExecutionContext`；只有active且当前attempt恰为新attempt-1时可转换。
- `terminate_context(uow, *, context_id,state="terminal") -> None`；state为terminal/isolated。

C以返回的epoch/context_id/attempt/token/lease/deadline构造既有ExecutionFence，或读取ExecutionContext提供的fence投影。真实PG夹具仍为call_persistence，组装函数及原五方法不变。I1仅完成代码补齐，运行负例通过前不关闭。

I1差异检查补充：当前prepare/mark仍以进入事务前的传入now判断租约，record_result以事实result.at判断；等待context/call行锁时实际期限可能已过。取所需锁后用新鲜权威当前时间复核，真实PG适配器提供DB当前时刻，参数now/result.at只用于事件/事实元数据，不能回拨资格时钟。补一个真实PG持锁等待越过lease/deadline、传入旧now仍零grant/当前业务写的负例；迟到可信事实通路不受影响。原公开五方法不变，不扩展1.3窗口/跳钟测试。
