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
