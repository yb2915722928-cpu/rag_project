# Story 1.2 独立运行验证报告（required verification passed / D016）

状态：`required verification passed` — Story 1.2 必需独立验证项已全部取得真实运行证据：base96c 的 A/B/C 基础（第 1–6 节）、E 调用集成与完整故障矩阵（第 7 节，固定 `d6e8a0da...`）、D epoch 启动/重启与缺失/不可读/矛盾负例（第 9 节，固定 `0162cb52f4c49265d99777c82d854b3617941941`）。本条只代表独立验证门，最终 Story 验收由主会话裁决；未到期门（1.3/1.4/1.5、真实供应方、P0/目标部署）不由本条签署。

> 增量补充（2026-10-18）：E 分段已在固定提交 `d6e8a0da94a88199e6c4795f3e10e26c821b454f` 完成独立运行验证（第 7 节）；D 分段已在固定提交 `0162cb52f4c49265d99777c82d854b3617941941` 完成独立运行验证（第 9 节）。第 1–6 节 base96c 基础证据原样保留、不重跑不改标。

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

## 7. E 调用集成增量独立验证（固定提交 `d6e8a0d`）

本节为在固定提交 `d6e8a0da94a88199e6c4795f3e10e26c821b454f` 上对 E 分段（[call_dispatch.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:1) 与 [test_call_dispatch.py](/E:/aaa-project/rag/backend/tests/test_call_dispatch.py:1)、[test_call_dispatch_postgres.py](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:1)）的独立增量验证。RPC 由主会话经官方 Netcatty MCP 串行转发，本验证未自行发起远程调用、未与 D 并发；第 1–6 节 base96c 证据原样保留。

### 7.1 基线与环境

| 项 | 预期 | 实际（回传证据） | 结果 |
| --- | --- | --- | --- |
| 固定提交 | `d6e8a0da...` | `environment-before`/`git-after` 均 `d6e8a0da94a88199e6c4795f3e10e26c821b454f` | 一致 |
| 独立根/venv | `/opt/rag-story-1-2/independent/{repo,venv}` | 命令路径同左 | 一致 |
| CPython | 精确 3.12.8 | `environment-before` = `3.12.8 0.37.0` | 一致 |
| uvicorn | 0.37.0 | 同左 | 一致 |
| `uv sync --locked` | exit 0 | `sync.exit` = 0 | 通过 |
| 远端来源 | 仅 Gitee | `origin` URL 为 Gitee、fetch main 后 detach 至 d6e8a0d（主控实读转发） | 主控转发 |

- 四源运行前后 `sha256sum` 逐行相同（`source-before` == `source-after`）：`call_dispatch.py`=`ae8f7048...b848`、`test_call_dispatch.py`=`1595bf6b...2450`、`test_call_dispatch_postgres.py`=`bdc14b91...cb82`、`uv.lock`=`7ad33ac0...8ed`，并与本机对 `d6e8a0d` blob 的重算值一致。
- 留证说明：`git fetch/checkout` 原始 stdout 与 `git status --porcelain` 行未包含在主控打包 JSON 内；HEAD 前后相等、四源 hash 逐行相同由打包件直接证明，detach  mechanics 与 clean 状态据主控转发。归档 `evidence-sha256.txt` 逐项列明各文件 SHA-256。

### 7.2 实际运行命令与结果

命令（`commands.txt` 原样，工作目录 `backend/`）：

```bash
/opt/rag-story-1-2/independent/venv/bin/python -m pytest tests/test_call_dispatch.py -q -p no:cacheprovider --junitxml=/opt/rag-story-1-2/independent/evidence/E-d6e8a0d/unit.xml
/opt/rag-story-1-2/independent/venv/bin/python -m pytest --require-postgres -m postgres -q -p no:cacheprovider --junitxml=/opt/rag-story-1-2/independent/evidence/E-d6e8a0d/pg.xml
```

本验证直接解析回传原始 XML（不采信摘要计数）：

- `unit.xml`：`tests=20 failures=0 errors=0 skipped=0 time=0.135`，timestamp `2026-10-18T09:55:56.711888+08:00`，exit 0；20 个 case 全部无 failure/error/skipped。
- `pg.xml`：`tests=28 failures=0 errors=0 skipped=0 time=14.261`，timestamp `2026-10-18T09:55:57.207249+08:00`，exit 0；28 个 case 全部 passed，750 deselected（不计入执行数）。
- XML SHA-256：unit `a2d0558b...f6a0`、pg `a394c47d...3eee`，与本机对回传 `.txt` 的重算值一致。
- `--require-postgres` 门生效：exit 0 证明 conftest 的 12 个必需 PG 节点全部 collected 且 passed（否则 `pytest_sessionfinish` 会置 `TESTS_FAILED`）。

### 7.3 E PG 13 节点（按 classname 拆分逐条核对）

PG 批次按 classname 拆分为 `test_call_dispatch_postgres` 13、`test_call_postgres` 7、`test_postgres_integration` 6、`test_runtime_entrypoints` 2 = 28；其中 E 归属 13 项全部 passed，并与 [E 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-e-dispatch-integration.md:1) 的验收映射一致：

| E 节点 | 对应原 AC 子句 | 结果 |
| --- | --- | --- |
| `test_real_end_to_end_one_grant_and_unknown_usage` | AC1/AC2 单 call 至多一次 grant、unknown 持久且秘密不泄露 | passed |
| `test_real_terminated_context_and_advanced_attempt_block_business` | AC1 终结/旧 fence 不提交业务；AC4 迟到不复活 | passed |
| `test_real_old_epoch_blocks_before_any_call` | AC1 旧 epoch 调用前阻断 | passed |
| `test_real_wrong_business_purpose_is_rejected_by_context` | 用途分层：错误业务用途由真实 context 拒绝，query+api 传输可共存 | passed |
| `test_real_prepare_crash_leaves_prepared_and_no_grant` | AC2 prepared 崩溃留 prepared、无 grant | passed |
| `test_real_grant_delivery_crash_is_unknown_null` | AC2 grant 投递崩溃 unknown=NULL | passed |
| `test_real_response_timeout_is_unknown_and_never_zero` | AC2 响应超时 unknown、不伪造零值 | passed |
| `test_real_sigstop_child_unknown_null_and_no_second_grant` | AC2 真实 child SIGSTOP+真实 TERM/KILL、unknown、无二 grant | passed |
| `test_real_response_before_record_is_unknown_plus_late_fact` | AC2/AC4 记录前响应 unknown+可信迟到事实 | passed |
| `test_real_late_usage_repeat_and_conflict_do_not_revive` | AC4 迟到 usage 幂等、冲突保留双方、不复活 | passed |
| `test_real_four_fake_capabilities_have_traceable_paths` | AC1 四类能力显式假件、可追溯、无实际外发 | passed |
| `test_real_rejected_target_and_download_credential_never_dispatch` | AC3 拒绝目标/下载凭据错配无派发 | passed |
| `test_real_no_pg_transaction_during_child_wait` | AC4 无网络/进程等待占 PG 事务 | passed |

- E unit 20 项与 PG 13 项在同一提交同源运行，覆盖同一批 AC 子句的应用层与真实 Linux/PG/child 端到端两层。
- 独立性与留证：本验证未修改任何实现/测试/部署/Git；未自行发起 RPC（所有远程命令由主会话串行请求转发）；无并发 RPC、无同文件修改，使用独立检出 `/opt/rag-story-1-2/independent/repo` 与独立虚拟环境 `/opt/rag-story-1-2/independent/venv`。实际执行发生在 D 后台镜像下载等待期间，操作系统进程时间上曾有重叠，但工作目录不同、PG 使用各自随机独占 schema，互不修改对方资源。原始 JUnit/log/env/命令/hash 归档于 `/fileOfRag/testOfRAG/metadata/story-1-2/independent/E-d6e8a0d`，本报告为本次唯一本地写入。

## 8. 更新后的总体状态（E 已过 / D 已过）

- **E 分段（调用集成与完整故障矩阵）**：在固定提交 `d6e8a0da94a88199e6c4795f3e10e26c821b454f` 已由本独立验证真实运行通过——unit 20 + 完整必需 PG 28（含 E 13）全部 0 fail/error/skip、exit 0，前后提交与四源 hash 一致；E 归属 AC 子句取得真实 Linux + 真实 PG + 真实 child 证据。
- **D（epoch 启动/重启与缺失/不可读/矛盾负例）：独立验证已通过**，见第 9 节（固定提交 `0162cb52f4c49265d99777c82d854b3617941941`）。
- **Story 1.2 必需独立验证门：`required verification passed`。** A/B/C 基础、E、D 三段均取得真实 Linux/真实 PG 运行证据；最终 Story 验收、正式审查增量以及未到期门（1.3 限流/C8、1.4 writer 清理、1.5 S0 汇总/真实供应方/P0/目标部署）均不由本条签署。真实供应方外发不构成本 Story 新增前置，按原后续 Story 归属保留。
- base96c 的 311 非 PG + 15 PG 基础证据保留原来源与 hash，不因本次 E/D 增量重标或外推。

## 9. D epoch 启动/重启与负例增量独立验证（固定提交 `0162cb52`）

本节为对 D 分段（[compose.yaml](/E:/aaa-project/rag/deploy/compose.yaml:1) 的 `RAG_EPOCH_CONTROL_FILE` 接线与 [api.Dockerfile](/E:/aaa-project/rag/deploy/api.Dockerfile:37) 的 service-UID 可读性修正）的独立运行验证。RPC 由主会话经官方 Netcatty MCP 串行转发；本验证未自行发起远程调用、未与任何角色并发、未新增 schema/初始化或重建镜像，只对开发者已交付的最终 D 专属实例做一次独立复核。

### 9.1 基线与实例

| 项 | 实际（原始输出） | 结果 |
| --- | --- | --- |
| 固定提交 | `git rev-parse HEAD` = `0162cb52f4c49265d99777c82d854b3617941941` | 一致 |
| 工作区 | `git status --porcelain` 无输出 | 干净 |
| 镜像 ID | `sha256:c2a1ebb49f1c23a8ba1bb29ac14288d214f587458e9af6df7681c27e3795cf55` | 与交付一致 |
| 实例镜像 | API/worker 均 `rag-story-1-2-api:0162cb52` | 一致 |
| 控制文件 | `f5d6a325ed0a05a5bdeb6ceeaba93a634d5570a8faa0881408231f4afd784248` | 记为 before |
| 控制目录/文件权限 | 目录 `550`、文件 `400`（`stat` 显示 `UNKNOWN:UNKNOWN`，宿主无 UID→名称映射；属主为开发者已核的 numeric `65532`，本验证不新增名称映射门） | 模式符合 |

原始输出：terminal.log（SHA-256 `06d784fee3bfdc9307112288fc8584c1f17a21abf54b239405e1111aaa36261e`）与 command.sh 归档于 `/fileOfRag/testOfRAG/metadata/story-1-2/independent/D-0162cb52`；回传日志与本机重算 hash 一致。

### 9.2 普通启动与重启（原 AC1 合法配置可重启且不轮换）

- `docker start` 后两容器 `running`；`api_health 200`（仅 liveness 陈述）；`worker_hc_exit=0`（helper 可被服务 UID 读取执行）；`check-database` 输出 `DATABASE_BASELINE_OK`、`baseline_exit=0`。
- 重启后同样 `running`、`api_health_after_restart 200`、`worker_hc_exit_after_restart=0`、`DATABASE_BASELINE_OK`、`baseline_exit_after_restart=0`。
- 控制文件 hash 在 before / after-start / after-restart / after-stop 四次均为 `f5d6a325...4248`，`epoch_hash_diff_exit=0`，即重启未轮换或重写控制记录。
- `rag_epoch_mirror` 前后两次均为 `mirror_rows 1 rag-story-1-2 j4DqwH13...Jxg 1`：单行，deployment_id/epoch/maintenance_version 与启动前完全一致，证明普通重启不重建镜像、不换 epoch。

### 9.3 三类负例（原 AC1 缺失/不可读/矛盾隔离）

| 负例 | 实际输出 | 退出码 | 裁决 |
| --- | --- | --- | --- |
| 控制文件缺失（`absent.json`） | `STARTUP_DEPENDENCY_UNAVAILABLE`，inspect `exited 2` | 2 | 有限失败 |
| 服务 UID 不可读（副本 `root:root 0600`） | `STARTUP_DEPENDENCY_UNAVAILABLE`，inspect `exited 2` | 2 | 有限失败 |
| 与既有镜像矛盾（独立副本不同 epoch：`MISMATCH_CONTROL_OK YA17eGAs...em4` ≠ 镜像 epoch） | `STARTUP_DEPENDENCY_UNAVAILABLE`，inspect `exited 2` | 2 | 有限失败 |

- 三类均未自动初始化、未用 DB 补造控制文件，未改写 D 正常控制记录；矛盾用例只新建独立副本，DB 镜像与正常控制文件保持原值（before/after-stop hash 不变即证）。
- 负例容器以 `--user 65532:65532` 运行，失败发生在服务 UID 的真实启动检查路径上，而非 root 特权环境。

### 9.4 复原与归档

- 结尾仅 `docker stop` 两个 D 专属容器，inspect 显示 `exited`；控制文件 hash 与 before 一致，DB 镜像未被本验证修改。
- 归档：`/fileOfRag/testOfRAG/metadata/story-1-2/independent/D-0162cb52`（terminal.log、command.sh、result.json 与 epoch-hash 文件）；无 `--rm`/`rm` 删除，未触碰 1.1 资源或开发者 schema/epoch。

### 9.5 D 三 AC 独立裁决

| D AC | 独立证据 | 裁决 |
| --- | --- | --- |
| 已迁移 PG 与显式初始化独立 epoch 下，新源码 API/worker 同配置启动/重启可运行且不轮换/重建控制值，secret 不泄露 | 9.1–9.2 真实 start/restart、两次 baseline OK、四次同 hash、镜像行前后一致、`/health` 仅 liveness | 支持 |
| 缺失或矛盾控制值时新 worker 启动保持隔离、有限失败，不自动初始化或用 DB 补造 | 9.3 三类负例全部 exit 2 且有限公开码，正常记录未被改写 | 支持 |
| 既有 1.1 资源不受影响，只使用本 Story 专属测试资源/独占 schema | 9.1/9.4 只操作 D 专属实例、独立副本目录与专属 schema `d_story12_d6e8a0da`；未触碰 1.1 容器/目录/桶 | 支持 |

D 门：**独立验证通过**。开发者交付与其 D 门结果保留原来源，本条为独立复核，不互相替代。

## 10. 未到期门与后续（不作为当前阻塞）

- Story 1.3 限流/C8、Story 1.4 writer 清理、Story 1.5 S0 汇总与真实供应方/P0/目标部署门未到期，按原规划归属，不构成本条阻塞。
- 正式审查增量复核（全新 `GPT-6.1 Sol / medium`）由主会话安排，其结论不属于本独立验证报告。
- 最终 Story 1.2 验收由主会话统一裁决；本报告只声明必需独立验证项已通过。

