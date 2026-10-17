# Story 1.1 A2a/B0a/B0c Linux 开发者运行门交付记录

日期：2026-10-17（Asia/Shanghai）。规格：
[spec-1-1-linux-developer-gates.md](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-linux-developer-gates.md:1)。

状态：**B 开发者运行门在 `a70a7e2` 上通过**：非 PG 全量、B0a/B0c 专题、正式生成与
`--check`、52 条样例全部实测通过，51 个生成工件已回传本地 `contracts/**` 并逐项核对
`manifest` hash。真实 PG 八项、四服务、独立验证与独立审查仍未执行，父 Story 未完成。

历史：`a269d49` 首次运行时 52 条样例为 44 通过 / 8 失败（C2 信封 `status` 被
`exclude_unset` 抹除），原始日志原样保留，见“52 条样例的 8 项失败与根因”。

## 环境与固定提交

| 项目 | 实测值 |
| --- | --- |
| 主机 | `120.53.251.166`，Linux 6.8.0-124-generic x86_64 |
| 会话 | Netcatty `1eaffce6-3c45-45cb-84bd-18bd6fc84ea9`（本任务独占） |
| 通过基线 | Gitee `main` = `a70a7e250ffda803f1e69e5ae5ce61615a2c02b7` |
| 历史基线 | `a269d492fb33b3b13d95265fa11589d39260c4e0`（44/8 失败快照） |
| 检出 | `/opt/rag-story-1-1/repo`（detached，工作树干净） |
| 运行目录 | `/opt/rag-story-1-1/linux-developer-gates-work`（`/dev/vda2` ext4） |
| 解释器 | `/root/.local/share/uv/python/cpython-3.12.8-linux-x86_64-gnu` → venv 3.12.8 CPython |
| uv / Uvicorn / pytest | 0.13.1 / 0.37.0 / 8.4.2 |
| 宿主系统 Python | 3.12.3（仅用于真实错误解释器负例） |

锁与声明 hash（与本地一致）：

| 文件 | SHA-256 |
| --- | --- |
| `backend/pyproject.toml` | `1b5a7ecb3e0036e3d96a8548a4fa729c95901fcd38dfa9ed63fb7b15e6c34c1c` |
| `backend/uv.lock` | `7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed` |
| `backend/.python-version` | `db3ef967a80f30770e652243d4e8292c73ee214e182ada70ce045e91aab40fa7` |

源码绑定：`HEAD` = `origin/main` = `a70a7e2…`；`git status --porcelain` 为 0 行；
`git ls-tree -r HEAD -- backend contracts` 的 102 个路径与磁盘 `sha256sum` 清单逐项一致。
两个修复文件的实测 hash 与冻结值相同：
`contract_probe.py` = `079a9952…`，`test_contract_http.py` = `f3929ae7…`。

`b897f649b26db0b9519fc22169d68c4dceb884c0` 仅为主控文档增量；`backend`/`contracts`
相对 `a70a7e2` 的 diff 为 0 行，故不重测。

## 已执行命令与计数

全部在 `a70a7e2` + 精确 CPython 3.12.8 上执行，原始日志与 JUnit 位于
`/opt/rag-story-1-1/linux-developer-gates-work/evidence/a70a7e2/`，
已归档到 `/fileOfRag/testOfRAG/metadata/story-1-1/linux-developer-gates/a70a7e2/`。

| 检查 | 命令 | 计数 | 退出码 |
| --- | --- | --- | --- |
| 锁一致性 | `uv lock --check --python 3.12.8` | 41 解析 | 0 |
| 锁同步 | `uv sync --locked --python 3.12.8` | 39 安装 | 0 |
| 非 PG 全量 | `pytest -m 'not postgres'` | JUnit `tests=515 failures=0 errors=0 skipped=1` → 514 passed / 8 deselected（收集 523） | 0 |
| 非目标解释器负例 | 3.12.3 + `PYTHONPATH` 运行单例 | JUnit `tests=1` → 1 passed | 0 |
| B0a/B0c 专题 | `pytest test_public_contracts test_contract_http test_json_guard test_decimal_wire_zero` | JUnit `tests=395` → 395 passed | 0 |
| runtime 专题 | `pytest test_runtime_entrypoints test_uvicorn_process -m 'not postgres'` | JUnit `tests=47` → 47 passed / 2 deselected | 0 |
| 正式生成 | `contracts/generate.py` | 51 个文件 | 0 |
| 生成一致性 | `contracts/generate.py --check` | `contracts check OK (51 files)` | 0 |
| 52 条样例 | `contracts/verify_samples.py` | **passed=52 failed=0 blocked=0 notes=0** | 0 |

分母说明：唯一 skip 是“仅适用于非目标解释器”的负例，已用真实 3.12.3 单独执行为
1 passed，不计入 Linux 通过；8 条 PG 标记（6 项 PG 集成 + 2 项 worker PG 参数化）
保持未执行，不能由条件筛除记为通过。

## 52 条样例的 8 项历史失败与根因（`a269d49`）

失败项全部为 HTTP 失败路径：
`h.http.reject.unauthenticated`、`unknown-field`、`nested-unknown-field`、
`media-type`、`content-encoding`、`headers-over`、`body-over-1mib`、`duplicate-key`，
统一报 `private HTTP response lacks status`。其余 44 条（C1 标量/序列化、C2 202/失败/
GET 投影、H 解析边界、no-store 与 request_id 轮换）通过。

根因（主控已独立读取确认）：`failure_response()` 构造 `FailedResponse` 时未显式设置
`status`，该字段有模型默认值且非必填，随后 `exclude_unset=True` 序列化将其抹掉，
与共享契约 C2“每次响应必须含 `schema_version`/`request_id`/`status`”冲突。
属实现缺陷，不是样例或模型定义问题。

同一缺陷的同类残留：探针成功回显同样用 `exclude_unset=True`，客户端合法省略带默认值的
`schema_version`/`status` 时，200/202 响应会缺少 C2 信封字段。主控裁决按同一 AC 闭合，
选择“合法输入经原模型验证后，输出始终补齐这三个信封字段”。

## 修复（已随 `a70a7e2` 发布）

仅改原认领的两个文件，未新增拒绝规则、未改 17 个 DTO、未改输入默认值或缺省/显式 null
语义，其余字段继续 `exclude_unset`：

1. [contract_probe.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/contract_probe.py:26)：
   失败信封显式传 `status=Status.FAILED`；探针成功路径在 `exclude_unset` 结果上仅补齐
   `schema_version`/`request_id`/`status` 三个字段。
2. [test_contract_http.py](/E:/aaa-project/rag/backend/tests/test_contract_http.py:117)：
   `assert_failure` 先检查 wire 三元组与 `status='failed'`，再 `model_validate`；
   新增合法输入省略默认信封字段时对 Accepted/Completed/Retrieval/Operation/Failed
   五种响应的 wire 断言（`set(body)` 必须等于提交键并集三元组），并验证未补齐字段
   （`retry_mode`、`operation_id`）仍按原语义缺省。

| 文件 | 字节 | SHA-256（冻结） |
| --- | --- | --- |
| `backend/src/rag_app/entrypoints/contract_probe.py` | 8675 | `079a9952c487cada067b30ba70ad08f64e20dd93d4a2fce84997b870564dc545` |
| `backend/tests/test_contract_http.py` | 24218 | `f3929ae78d4d240403224b429b00619976a9077909ac13b28c526c88f6817526` |

`a269d49` 上本地仅做 `ast.parse` 与 `git diff` 审阅；修复后的真实运行证据全部来自
`a70a7e2` 的 Linux 精确 3.12.8，Windows 结果不作为证据。

## 51 个生成工件与本地冻结

生成于 `a70a7e2` 的独立 `git archive` 解包目录（不污染固定检出），经 HTTP 取回本地
`contracts/**`。`manifest.json` 声明 50 个工件、9 个源文件；本地逐项重算 **0 不匹配**，
且记录的 `contract_probe.py` hash 正是 `079a9952…`。

| 工件 | SHA-256 |
| --- | --- |
| `contracts/openapi.json` | `8f04bacde45ef4cb98c3f927cb76ab3f242c4706ced81b3fde5f0df3450368cf` |
| `contracts/manifest.json` | `ad877ebbaf7b56fe33e657d546240c0a34da368aacfc9a20f892db0e313a5515` |
| `contracts/schemas/capabilities.json` | `7752cc855d49f262856eb9ceb249f5b80dd7983da2f8221c1abb282166693d32` |
| `contracts/typescript/contracts.ts` | `9809d71003d740e5e42c5b8d3f3df484fbe65c77491a95ea6bca2d61053332dd` |
| `contracts/typescript/contracts.input.ts` | `9de305ce3e4c047934432810857d7a9a0f7447731ba6b0c9951b65e1823dbe48` |

结构：17 个 DTO、5 个枚举、OpenAPI 36 个 component、路径仅 `/health` 与
`/__maintenance/contracts/{model_name}`、无令牌；能力 `answer.v1` 8 / `operation.v1` 7 /
`retrieval.v1` 3；`comparison.v1` 为 `not_generated`。`contracts/` 本地共 97 个文件
（46 个既有输入/脚本 + 51 个生成物），全部 LF，无 CRLF、无二进制。

**前端消费方向**：`contracts.ts` 是服务端序列化输出类型，`contracts.input.ts` 是校验
输入类型，两者 schema 存在差异，不能互替。

## 真实 PostgreSQL 八项（`9da9af2`）

主控已按 `deploy/postgres-test/setup.sh`（blob `65dc2616…`，SHA-256
`0083b8f5d69cc968cd4da3fa8608dfb703ebbd3b92c5bf400ae6ff589226167a`）在 Gitee
固定提交 `9da9af209123e8f57b2650e14b98175f4aa5fefd` 上完成 setup，exit 0。
本段只复跑此前 `not-executed` 的 8 个 PG 节点，未重跑已通过的非 PG 与 B 套件。

| 项目 | 实测 |
| --- | --- |
| 提交 | `9da9af2…`；`origin/main` 同值；`git status --porcelain` 0 行 |
| `backend` 相对 `a70a7e2` 的 diff | **0 行**（仅新增 `contracts/**` 与 `deploy/postgres-test`） |
| 解释器 | CPython 3.12.8 venv，psycopg 3.3.6 |
| 服务端 | PostgreSQL `18.6 (Debian 18.6-1.pgdg12+2)`，`vector=0.8.7` |
| 容器 / 端口 | `rag-story-1-1-postgres-test`，`127.0.0.1:55432→5432` |
| 凭据装载 | 仅 `set -a; . <root 0400 env>`；只打印变量名与授权标志，未打印值或完整 DSN |
| 命令 | `pytest --require-postgres -q` + 显式 8 个 node id |
| JUnit | `tests=8 failures=0 errors=0 skipped=0` → **8 passed** |
| 退出码 | 0 |

覆盖节点：`test_real_migration_cycle`、`test_real_rollback_and_repository_boundary`、
`test_real_driver_error_is_private`、`test_real_incompatible_version_is_read_only`、
`test_real_namespace_cannot_fall_back`、`test_real_downgrade_missing_probe_preserves_peer`、
`test_real_pg_worker_idle_has_no_transaction_and_exits[15]`、`…[2]`。
`--require-postgres` 的会话级门保持启用：必须收集全部 8 个必需节点且逐一真实通过，
skip/fail 会使会话失败，因此本结果不是条件筛除得来的通过。

清理与共享资源：

| 检查 | 结果 |
| --- | --- |
| 测试前 `rag_test_%` schema 数 | 0 |
| 测试后 `rag_test_%` schema 数 | **0**（`leftover-schemas.txt` 为空） |
| `public` schema 表数 | 0（未被 fixture 触碰） |
| `vector` 扩展 | 仍在 `public`，`0.8.7`，未重建/未删除 |
| 凭据泄漏扫描 | 证据目录内无 DSN、密码或 `password` 字样 |

证据：`/fileOfRag/testOfRAG/metadata/story-1-1/linux-developer-gates/9da9af2-pg/`
（`junit.xml` `79991de0…`、`pytest.log` `0891054a…`、`schema-counts.txt` `4df7e0c7…`，
`archived-sha256.txt` 与源目录逐项一致）。

## 未执行与风险

- `not-executed`：四服务生命周期与干净重建、完整镜像/digest、浏览器与目标部署环境。
- `not-executed`：Step 5 独立运行验证、全新 `GPT-6.1 Sol / medium` 独立审查及修复回归。
- 已执行：修复后的 Linux 回归、51 工件重建与 `--check`、样例 52/52、
  真实 PostgreSQL 八项、证据归档。
- 风险：JSON Schema 不能表达 Pydantic 跨字段校验；运行时权威仍是后端模型。
- 风险：探针路径在 OpenAPI 中可见，生产网关必须阻断，部署侧尚未验证。

本记录不把开发者测试当独立验证，也不改变父 Story 的验收分母。
