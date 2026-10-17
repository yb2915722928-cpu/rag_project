# Story 1.2 独立运行验证报告（partial / base96c）

状态：`partial` — 仅覆盖稳定基础提交 `96c64fbab0fa8d3d824f2e592196c02570550c70` 上已发布的 A/B/C 基础范围。
E（本地未发草稿 F2 修订）与 D（既有 Compose epoch 接线回归）**未验证**，本条不构成 Story 1.2 全量通过。

- 执行角色：Step 5 Preview，实际模型 `stepfun/step-5-preview` / `high`（主控核，未传推理覆盖）；未参与实现。
- 执行时间（以归档 JUnit 的 `timestamp`/`time` 属性为准）：非 PG 批次 `2026-10-18T06:46:41.642521+08:00`，`time=13.464`；PG 批次 `2026-10-18T06:47:51.569293+08:00`，`time=9.034`（Asia/Shanghai）
- Netcatty session：`94bede36-0e0e-444c-a8b7-f332d2542962`（120.53.251.166），独占时段；执行后归还 RPC。
- 归档目录：`/fileOfRag/testOfRAG/metadata/story-1-2/independent/base96c`

## 1. 环境与固定提交核对

| 项 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 固定提交 | `96c64fbab0fa8d3d824f2e592196c02570550c70` | 同左，`git status --porcelain` 空 | 一致 |
| 提交说明 | — | `feat: supervise bounded child calls and wire shared epoch config` | — |
| CPython | 精确 3.12.8 | 3.12.8 (main, Jan 14 2025, 22:49:14) [Clang 19.1.6] | 一致 |
| uvicorn | 0.37.0 | 0.37.0 | 一致 |
| uv sync | `--locked` | `Resolved 41 packages` / `Checked 39 packages`，exit 0 | 通过 |
| `backend/uv.lock` sha256 | `7ad33ac0...a408ed` | 同左 | 一致 |
| PG test 服务 | 127.0.0.1:55432, PG18.6/vector0.8.7 | `rag-story-1-1-postgres-test Up 8 hours`，端口一致 | 一致 |

最终 venv 由 `uv venv --python /root/.local/share/uv/python/cpython-3.12.8-linux-x86_64-gnu/bin/python3.12` 显式指定 managed 路径创建，运行证据为 `Python 3.12.8 (main, Jan 14 2025, 22:49:14) [Clang 19.1.6]`。最初按默认 `cpython-3.12` 别名创建的 venv 未取得 `sys.version` 原始证据，已弃用且不计入本报告证据，不断言其小版本。PG 连接仅 source 既有 `0400` 文件 `/opt/rag-story-1-1/postgres-test/secrets/test-database.env`，未打印 DSN 或口令。

## 2. 源码 snapshot 与 hash 核对

- A-fix1：19 个文件全部匹配 [story-1-2-a-fix1-source-snapshot.json](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-a-fix1-source-snapshot.json:1) 索引 sha256。
- B：`backend/src/rag_app/modules/execution/egress.py`、`backend/src/rag_app/adapters/egress.py`、`backend/tests/test_egress.py` 全部匹配 [story-1-2-b-source-snapshot.json](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-b-source-snapshot.json:1)。
- C（四源）与 D（两文件）：匹配 [story-1-2-cd-source-snapshot.json](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-cd-source-snapshot.json:1)；其中 C 四源按已再冻版本核对，`call_dispatch` 与单元/PG 集成仍未冻结，本报告不据此下运行结论。
- `test_call_persistence.py` 在快照中记录为 CRLF-to-LF 归一化差异，本检出为 git LF 版本，与索引 `9509af48...6b09` 一致。
- 运行前后两次 `sha256sum`（28 个唯一 snapshot 文件 + `backend/uv.lock` = 29 项）完全一致，见归档 `base96c-source-hashes.txt`；实现、测试、Git 状态均未由本验证修改。

## 3. 实际运行结果

### 3.1 非 PG 合并批次

命令（工作目录 `backend/`）：

```bash
python -m pytest tests/test_egress.py tests/test_call_persistence.py tests/test_epoch_control.py \
  tests/test_child_supervisor.py tests/test_uow.py tests/test_resource_cleanup.py \
  tests/test_architecture.py tests/test_namespace.py tests/test_config.py tests/test_baseline.py \
  tests/test_migrations.py tests/test_api.py tests/test_uvicorn_process.py tests/test_worker.py \
  tests/test_runtime_entrypoints.py -m "not postgres" -q --junitxml=base96c-junit-nonpg.xml
```

- 结果：`311 passed, 2 deselected, 1 warning in 13.47s`，exit 0（主控直接解析原始XML：`tests=311`、`failures=0`、`errors=0`、`skipped=0`，`time=13.464`；deselected不计入XML执行数）。
- 2 个 deselect 来自 `tests/test_runtime_entrypoints.py::test_real_pg_worker_idle_has_no_transaction_and_exits[15]` 与 `[2]` 两个真实 worker 参数（postgres 标记，非 PG 批次按设计排除），属正确归类，非缺口。
- 日志 sha256 `aa0a5667...89758`，JUnit sha256 `13b55c51...c14fd`。

### 3.2 真实 PG 批次

命令（工作目录 `backend/`，已 source 既有 `0400` env）：

```bash
python -m pytest tests/ -m "postgres" --require-postgres -q --junitxml=base96c-junit-pg.xml
```

- 结果：`15 passed, 730 deselected, 20 warnings in 8.70s`，exit 0（XML：`tests=15`、`failures=0`、`errors=0`、`skipped=0`，`time=9.034`）。
- 15 项节点与主控所述「旧6 + worker2 + 新7」一致，逐项 `PASSED`，无 skipped/failed/error。
- 日志 sha256 `d07373ae...fc9ac`，JUnit sha256 `2b91af24...a3a`。

### 3.3 PG 15 项节点明细

`test_call_postgres.py`（7）：`test_real_call_lifecycle_and_single_grant`、`test_real_terminal_idempotency_and_late_facts`、`test_real_late_fact_does_not_take_parent_lock`、`test_real_failed_transaction_leaves_no_call`、`test_real_epoch_mirror_restart_and_contradiction`、`test_real_reverse_lock_order_is_rejected`、`test_real_lease_expiry_under_held_context_lock_denies_old_now`

`test_postgres_integration.py`（6）：`test_real_migration_cycle`、`test_real_rollback_and_repository_boundary`、`test_real_driver_error_is_private`、`test_real_incompatible_version_is_read_only`、`test_real_namespace_cannot_fall_back`、`test_real_downgrade_missing_probe_preserves_peer`

`test_runtime_entrypoints.py`（2）：`test_real_pg_worker_idle_has_no_transaction_and_exits[15]`、`test_real_pg_worker_idle_has_no_transaction_and_exits[2]`

## 4. 与原 AC 子句的对应（仅本报告实际运行覆盖部分）

验收分母为 [epics Story 1.2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197) 四条 AC 的全部实质子句；下表只列本报告有真实运行证据的子句，未列即未验。

| 原 AC 子句 | 对应实际节点/证据 | 状态 |
| --- | --- | --- |
| AC1 独立持久 epoch 与 DB 镜像一致；普通重启不换 epoch | `test_epoch_control.py` 19 项非 PG（XML case 数）+ `test_real_epoch_mirror_restart_and_contradiction` | 已验 |
| AC1 缺失/损坏/矛盾隔离 | `test_missing_control_is_isolated_and_never_synthesized`、`test_mirror_missing_or_contradictory_is_isolated`、`test_damaged_control_is_invalid`、`test_environment_without_control_fails_finite` | 已验 |
| AC1 旧 attempt/epoch/token/租约/期限不能提交业务 | `test_old_fence_loses_authority_after_persisted_attempt_advance`、`test_mark_rejects_wrong_fence_or_deadline`、`test_result_with_expired_authority_is_rejected_but_late_fact_is_not`、`test_real_lease_expiry_under_held_context_lock_denies_old_now` | 已验 |
| AC1 四类能力端口仅用显式假件，无实际外发 | `test_child_runs_one_explicit_fake_stage_and_exits[MODEL/PARSE/EMBEDDING/VISION]`、`test_egress_consumes_the_resolved_plan_and_receives_one_grant`（本地假件，connect_address 为文档常量 `93.184.216.34`）；`test_child_source_has_no_database_or_provider_adapter_imports` | 已验（假件边界） |
| AC2 may_have_sent 后 / 未 grant 超时 / IPC 绝对 deadline（部分） | `test_child_exit_after_grant_is_conservative_may_have_sent`、`test_egress_without_grant_times_out_as_not_sent`、`test_slow_fragmented_ipc_cannot_extend_the_absolute_deadline` | 部分已验 |
| AC2 prepared 事务前后 / 响应前后的完整故障矩阵端到端 | 无对应已发布 E 端到端节点 | 未验（E 未发布） |
| AC2 原 call 至多一次 grant，重启/重领不恢复重发，unknown 为 NULL+unknown | `test_mark_grants_once_and_never_after_restart`、`test_second_grant_is_finite_and_never_consumed`、`test_misbound_grant_is_rejected_before_the_child_sees_it`、`test_unknown_keeps_nulls_and_zero_effect_on_repeat`、`test_real_call_lifecycle_and_single_grant` | 已验 |
| AC2 真实 Linux 有界受监督 child/IPC、有限停止；未证退出/FD/IPC 关闭不复用槽 | `test_live_child_in_another_supervisor_blocks_the_same_physical_slot`、`test_proc_unknown_is_never_proof_of_absence`、`test_foreign_identity_is_never_signalled`、`test_identity_reuse_with_a_stale_start_token_is_not_the_same_child`、`test_unreleased_starting_claim_from_crashed_spawn_blocks_the_slot`、`test_stop_unproven_persists_across_supervisor_instances`、`test_proven_stop_allows_the_same_slot_to_spawn_again`、`test_frame_bound_rejects_oversize_and_truncation` | 已验（C 四源已再冻版本） |
| AC2 child 无业务 DB/主密钥/自主串阶段；秘密不入 argv/日志 | `test_child_source_has_no_database_or_provider_adapter_imports`、`test_secret_is_not_in_child_argv_environment_or_logs`、`test_grant_and_result_wire_round_trip_hides_secrets_from_repr`、`test_child_runs_one_explicit_fake_stage_and_exits` | 已验 |
| AC3 HTTPS、准确 host/port、有限长度、拒 userinfo/fragment | `test_profile_is_an_exact_host_port_allowlist`、`test_config_url_limit_is_2048_code_points`、`test_signed_url_limit_is_8192_utf8_bytes`、`test_invalid_wire_urls_fail_before_any_io`、`test_empty_path_and_trailing_question_mark_are_preserved`、`test_signed_query_is_preserved_verbatim`、`test_host_header_keeps_original_port_and_ipv6_brackets`、`test_ipv6_literal_host_and_host_header` | 已验 |
| AC3 全部 A/AAAA 任一非公网拒绝，实际连接绑定已核 IP，TLS 主机校验保留 | `test_any_unsafe_dns_address_blocks_the_whole_dispatch`、`test_public_address_predicate_rejects_non_public`（含 `::1`、`::ffff:127.0.0.1`、`fe80::1`、`fc00::1`、`fd00:ec2::254`、`ff02::1`、`2002::1`、`64:ff9b::` 等）、`test_mixed_a_and_aaaa_are_all_retained_and_validated`、`test_connector_connects_only_to_the_verified_ip_and_keeps_hostname`、`test_plan_requires_a_verified_member_as_connect_address`、`test_connector_uses_ipv6_socket_family_for_ipv6_plan`、`test_connector_rejects_insecure_tls_context_and_invalid_timeouts` | 已验 |
| AC3 DNS 变化无重解析绕过，redirect 不跟随，API Authorization 不转交下载 host | `test_plan_keeps_the_first_verified_address_and_never_resolves_again`、`test_transport_returns_redirect_without_following_or_retrying`、`test_api_authorization_is_rejected_for_upload_and_download`、`test_transport_preserves_target_host_and_api_only_authorization`、`test_reserved_request_headers_cannot_bypass_the_credential_boundary`、`test_duplicate_and_injected_request_headers_are_rejected` | 已验 |
| AC3 URL/secret 不入普通日志；目标守卫失败实际阻断 | `test_dns_exception_never_renders_the_original_secret`、`test_signed_url_failure_never_renders_the_secret`、`test_response_and_request_repr_hide_headers_bodies_and_secrets`、`test_empty_dns_result_fails_closed`、`test_malformed_dns_result_fails_closed`、`test_system_resolver_failure_is_finite`、`test_system_resolver_rejects_a_non_ip_result` | 已验 |
| AC4 终结业务/旧 epoch 下可信迟到 usage 仅按 call 幂等追加（机制层） | `test_late_fact_appends_duplicate_and_conflict_without_business_change`、`test_late_fact_ignores_a_changed_business_epoch`、`test_real_terminal_idempotency_and_late_facts` | 已验（机制） |
| AC4 冲突保留双方来源（机制层） | `test_record_result_is_idempotent_and_conflict_is_explicit`、`test_fact_values_distinguish_estimate_and_actual_and_keep_nulls` | 已验（机制） |
| AC4 不改业务/产品次数/会话/许可 | 当前通过节点仅证明call-only机制、上下文与源码写入边界；未来产品计次/会话/permit业务联调没有执行，按后续实际业务Story归属保留，不新增其实现为本条前置 | 当前机制已验；E迟到上下文不复活端到端待验；未来联调不记PASS |
| AC4 真实 PG 负例证明锁序；迟到账仅锁 call，反锁序被拒 | `test_lock_order_rejects_reverse_acquisition`、`test_real_reverse_lock_order_is_rejected`、`test_real_late_fact_does_not_take_parent_lock`、`test_real_failed_transaction_leaves_no_call` | 已验 |
| AC4 无网络/进程等待占事务（E child 等待跨事务） | 无对应已发布 E 端到端节点 | 未验（E 未发布） |
| AC4 迁移 up/down/up 及本条影响的 namespace/启动回归 | `test_real_migration_cycle`、`test_real_rollback_and_repository_boundary`、`test_real_namespace_cannot_fall_back`、`test_real_pg_worker_idle_has_no_transaction_and_exits[2/15]`、非 PG `test_migrations.py`/`test_namespace.py`/`test_worker.py`/`test_uvicorn_process.py`/`test_runtime_entrypoints.py` | 已验 |

上述「已验」均指本报告 3.1/3.2 实际运行节点通过；「部分已验」「未验」行的缺口不因基础批次通过而关闭。

主控证据校正：原始XML由主控直接解析，非PG为311，PG为15，source为28个唯一快照文件加锁文件；不得把deselect加入执行数。上述未来业务联调范围按项目AGENTS的Story归属规则处理，不以不存在的未来业务表阻塞当前实现；当前E故障/迟到事实端到端义务完整保留。

补充非 PG 支撑（按归档 XML 实际 case 数，已随 3.1 通过）：`test_call_persistence.py` 20 项、`test_egress.py` 153 项、`test_child_supervisor.py` 22 项、`test_epoch_control.py` 19 项，以及 `test_uow.py`、`test_resource_cleanup.py`、`test_architecture.py`、`test_namespace.py`、`test_config.py`、`test_baseline.py`、`test_migrations.py`、`test_api.py`、`test_uvicorn_process.py`、`test_worker.py`、`test_runtime_entrypoints.py`。

## 5. 未通过 / 未执行项（不缩分母）

- **E（本地未发草稿 F2 修订）：未验证。** 未发布源码未运行；不把本地草稿计入本条通过。
- **D（既有 Compose epoch 接线回归）：未验证。** 未跑普通部署；`/health` 只算 liveness，不作为业务就绪证据。
- **C 的 `call_dispatch` 与单元/PG 集成：未冻结、未运行。** 本报告仅核 C 四源已再冻版本在其既有测试节点上的实际通过，不对未发布部分下结论。
- **Story 1.5 总资格工具、Story 1.3 限流/C8、Story 1.4 writer 清理、真实供应方/P0/目标部署门：未到期，不由本条签署。**
- **此前 `52ccb1f` 的 SQL 绑定失败及两文件 server overlay 试跑：单列保留，不计入本报告通过证据。**
- **Story 1.2 全量结论：`not-passed`（partial）。** 原四条 AC 的实质子句中，E/D 归属部分仍缺真实 Linux 运行证据。

## 6. 独立性与留证

- 未修改任何实现、测试、部署、Git 状态；未在分配的 Netcatty 时段外操作；未与其他角色并发 terminal RPC。
- PG 使用既有隔离 test 服务与独占 schema；未清其他项目资源，未新建大小写不同的挂载路径。
- 本报告为本次验证唯一本地写入。原始日志/JUnit/源码 hash 归档于 `/fileOfRag/testOfRAG/metadata/story-1-2/independent/base96c`。
- 工具限制记录：终端 RPC 拒绝含 `$(` 的命令替换与 `rm -rf` 模式，已改用直接输出与 `mv` 替代；此为命令语法限制，非环境阻塞。
- 发现的问题：本报告范围内无未关闭缺陷，实际运行节点全部 passed。E/D 与 C 未冻结部分的缺口按归属报告主控转原开发者，不由本验证修复。

