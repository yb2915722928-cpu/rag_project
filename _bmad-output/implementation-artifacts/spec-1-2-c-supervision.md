---
title: '1.2 C 单 call 监督与集成'
type: feature
created: '2026-10-18'
status: in-progress
route: dispatch
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

用真实 Linux 子进程和显式能力假件集成 A 的持久调用与 B 的 EgressTarget，完成原 Story 1.2 AC2 及全部 AC 的调用路径。不得以线程取消代替 child 停止。

## Boundaries & Constraints

子进程参数数组/shell=False/start_new_session/close_fds/环境 allowlist，不用 preexec_fn。child 无业务 DB/主密钥/自主下一阶段权力，只接受有大小/时间/条数上界的私有 IPC 单阶段命令和一次 grant；最少秘密不入 argv/环境/普通日志/持久命令。

控制器记录 boot/slot/启动实例/进程组/attempt，不只 PID。prepared 与 may_have_sent 两次短 UoW 后才给绑定 call/attempt/boot/child 的一次 grant；同 call 重启/重领不再给 grant。may_have_sent 后不明结果保守 unknown/NULL，不变 not_sent 或零成本。显式重试须新 call 重新守卫。

期限/失联触发有界停止与退出/FD/IPC 核实，未证停止不能复用槽；TERM/KILL 等待在 PG 事务外。禁止后代，发现无法证明的后代阻塞。只用模型/解析/embedding/图意显式假件；无真实外发或新增 Web 页面。1.3 完整 C8 窗口/permit 与 1.4 writer 清理仍保留。

## Tasks & Acceptance

- [ ] `modules/execution/supervision.py`、`adapters/child_supervisor.py`、`entrypoints/call_child.py`：有限 IPC 与真实 Linux 监督。
- [ ] `application/call_dispatch.py`：按主控登记的 A/B 公共签名装配，复核资格、持久状态、目标守卫、单 grant/响应事实。
- [ ] `tests/test_child_supervisor.py`、`test_call_dispatch.py`、`test_call_dispatch_postgres.py`：故障矩阵和集成；`docs/story-1-2-c-delivery.md`。

## Acceptance Criteria

- Given 有界 child，When prepared 前后、may_have_sent 后、响应前后崩溃/超时，Then 原 call 最多一次 grant、恢复不重发、未知不归零。
- Given child/秘密哨兵，When 执行四类假件，Then 无 DB/主密钥/自主阶段，IPC/输出有界且 argv/log 不泄秘密。
- Given 旧 fence/拒绝目标/未确认停止，When 再派发或复用槽，Then 无业务提交/网络调用/槽复用。
- Given 真实 PG，When child 等待或停止，Then 没有 PG 事务跨等待；迟到响应只走 A 的事实端口。

</frozen-after-approval>

## Code Map

复用 A 的 `application/call_lifecycle.py` 与 B 的 `modules/execution/egress.py`/`adapters/egress.py`；调用集成前主控确认具体签名。不得修改 A/B 文件；契约问题回报主控。

## Implementation Notes

唯一 DeepSeek 默认；文件归属仅 Tasks 所列八件。先只读提出监督端口简短签名，等待 `IMPLEMENTATION_MODEL_RELEASE` 后开始无依赖的 child/IPC/监督部分；A 持久端口登记前不写依赖 A 的调用集成。B/C 端口已登记于 [公共契约](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-public-contracts.md:1)，grant 使用已核 EgressPlan，不能在 child 重新 DNS。主控核实际模型才写入。只在主控分配的 Netcatty 时段从 Gitee 固定提交运行；原始证据存桶。无意图空缺。

## Spec Change Log

## Review Triage Log

## Verification

开发者 Linux/PG 故障矩阵及相关回归；父 Story 再执行独立 Step 5 验证和全新审查，不以本子规格完成替代父 AC。
