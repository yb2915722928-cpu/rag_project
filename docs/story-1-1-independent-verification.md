# Story 1.1 独立运行验证记录

| 项 | 值 |
| --- | --- |
| 状态 | AC1/AC2/AC3/AC4 均取得可复算实测证据；AC3 缺项（UID/挂载/共享锁/原子替换）已闭合，生命周期原始工具观测已归档登记 |
| 规格 | `_bmad-output/implementation-artifacts/spec-1-1-independent-verification.md` |
| 源码基线（本轮运行） | `dd44834383de2bd9af9768a6ecc7fe2c48427eff`（Gitee 固定检出，HEAD = origin/main，工作树 0 行） |
| R1 修复发布 | `25232d0bebc230c35837153b6fd572ff734977aa`（仅 frontend helper/test 两应用文件；backend/contracts/deploy 及锁未变，已核） |
| 验证角色 | `stepfun/step-5-preview / high`（派发未传强度，主控已核实 turn_context） |
| 更新 | 2026-10-18，Asia/Shanghai |

## 0. 身份、范围与边界

- 验证角色：`stepfun/step-5-preview / high`。未参与 A/B/C/D/E 任何实现，未修改主控状态或 Git；本文件是本次唯一写入口。**例外（如实记录）**：为证明 R1 新测试不是空断言，曾在**隔离验证目录** `/opt/rag-story-1-1/independent-verify/r1/repo-252/frontend/` 内把 `src/api/health.ts` 临时换回 `dd44834` 版本做一次反向探针，随后 `git checkout --` 恢复，最终工作树干净、与 252 提交一致。该项目检出副本之外的仓库源码、测试、锁、部署均未被改动。
- 本轮**已由本验证者实际独立运行一次**：后端非 PG 全套、`--require-postgres` 八节点、真实 3.12.3 负例、`contracts generate --check` 与 52 样例、真实 gateway 基本交互与缓存边界、真实 200% 页面缩放布局/控件核对。不追加通用硬化、假设性风险或未来业务矩阵，不重跑开发者 build/生命周期全部套件。
- 运行环境：Netcatty Linux `120.53.251.166`（`VM-0-16-ubuntu`，`6.8.0-124-generic` x86_64），独立工作目录 `/opt/rag-story-1-1/independent-verify`，独立 venv `venv-iv`。凭据只 `source` 既有 root 0400 文件（路径见已发布 `deploy/postgres-test/setup.sh`），未打印 DSN 或密码值。
- 前端：只独立跑 R1 相关的 `health.spec.ts` **14 例**（通过），未重跑旧 18 套件全量与完整矩阵；其余六个未改前端用例原证据保留，不扩大范围。
- 干净重建后台 job 只核原输出，不另开第三轮 build；wrapper 回显缺失（Background job not found）如实记录，不另加为新重建门，不填假 0。

## 1. 独立运行：A1 解释器 / 锁 / Uvicorn / 非 PG 全套

命令（独立 venv `venv-iv`，目录 `/opt/rag-story-1-1/independent-verify/repo-iv/backend`）：

```sh
uv venv --python 3.12.8 /opt/rag-story-1-1/independent-verify/venv-iv
uv sync --locked --python 3.12.8
python -m pytest -m "not postgres" --junitxml=evidence/non-pg/junit.xml
```

| 项 | 独立运行结果 | 证据 |
| --- | --- | --- |
| 解释器 | **通过**。`Python 3.12.8`，`sys.implementation.name = cpython` | 运行输出 |
| 锁与依赖 | **通过**。`uv sync --locked` 完成；`uvicorn 0.37.0`、`pytest 8.4.2`、`fastapi 0.143.2`、`pydantic 2.14.1` | 运行输出 |
| 非 PG 全量 | **通过**。`514 passed, 1 skipped, 8 deselected`，exit 0；JUnit `tests="515" errors="0" failures="0" skipped="1"`，用时 17.622s | `evidence/non-pg/pytest.log`、`junit.xml` |
| 唯一 skip | **符合预期**。`SKIPPED [1] tests/test_startup.py:87: This negative case applies only to a supplemental non-target runtime` | 同上 |
| 非目标解释器负例 | **通过**。真实 `/usr/bin/python3` = `Python 3.12.3` 上单跑 `tests/test_startup.py::test_actual_cli_rejects_non_target_runtime`：`1 passed`，exit 0，JUnit `tests="1" skipped="0"` | `evidence/non-target/pytest.log`、`junit.xml`、`interpreter.txt` |
| 声明一致性 | **一致**。`backend/.python-version` = `3.12.8`；`pyproject.toml` `requires-python = "==3.12.8"`；`uv.lock` SHA-256 `7ad33ac0…` 与本地相同 | 本地 + 运行实测 |

## 2. 独立运行：A2 / PG 八项（`--require-postgres`）

命令：

```sh
set -a; . /opt/rag-story-1-1/postgres-test/secrets/test-database.env; set +a   # 既有 root 0400，仅 source
python -m pytest --require-postgres --junitxml=evidence/pg-8/junit.xml \
  tests/test_postgres_integration.py::test_real_migration_cycle \
  tests/test_postgres_integration.py::test_real_rollback_and_repository_boundary \
  tests/test_postgres_integration.py::test_real_driver_error_is_private \
  tests/test_postgres_integration.py::test_real_incompatible_version_is_read_only \
  tests/test_postgres_integration.py::test_real_namespace_cannot_fall_back \
  tests/test_postgres_integration.py::test_real_downgrade_missing_probe_preserves_peer \
  "tests/test_runtime_entrypoints.py::test_real_pg_worker_idle_has_no_transaction_and_exits[15]" \
  "tests/test_runtime_entrypoints.py::test_real_pg_worker_idle_has_no_transaction_and_exits[2]"
```

| 项 | 独立运行结果 | 证据 |
| --- | --- | --- |
| 运行前基线 | `rag_test_%` schema = **0**；`public` 表 = **0**；`vector` = **0.8.7**；`server_version_num` = **180006** | `evidence/pg-8/schemas-before.txt`、`public-tables-before.txt`、`vector-before.txt`、`server-version-num.txt` |
| 八项结果 | **8 passed**，exit 0；JUnit `tests="8" errors="0" failures="0" skipped="0"`，用时 3.252s | `evidence/pg-8/junit.xml`、`pytest.log`、`exit-code.txt` |
| 覆盖节点 | 6 个 `test_postgres_integration` 必跑 + `test_real_pg_worker_idle_has_no_transaction_and_exits[15]` / `[2]`，与 `REQUIRED_POSTGRES` 一致 | `junit.xml` testcase 名 |
| 会话级门 | **未被动过**。`--require-postgres` 下 `pytest_sessionfinish` 要求 `_postgres_passed == _postgres_required_nodes`，skip/fail 即使会话失败；本次 0 skip | [conftest.py](/E:/aaa-project/rag/backend/tests/conftest.py:69) + 运行结果 |
| 运行后清理 | `rag_test_%` schema = **0**；`public` 表 = **0**；`vector` 仍 **0.8.7**（未重建/未删除） | `evidence/pg-8/schemas-after.txt`、`public-tables-after.txt`、`vector-after.txt` |
| 凭据处理 | 仅 `set -a; . <root 0400 env>; set +a`；只记录变量名与授权标志，未打印 DSN 或密码 | `evidence/pg-8/env-check.txt` |
| 秘密泄漏扫描 | 证据目录内无真实 DSN 凭据、无 48 位以上十六进制秘密（命中的长十六进制均为测试夹具哨兵如 `aaaa…`/`1111…`） | 独立 grep 扫描 |
| 服务端版本 | `PostgreSQL 18.6 (Debian 18.6-1.pgdg12+2)`，`vector 0.8.7`，容器 `rag-story-1-1-postgres-test` | 运行实测 |

## 3. 独立运行：B 契约（AC4）

命令：

```sh
python contracts/generate.py            # 正式生成
python contracts/generate.py --check    # 生成一致性
python contracts/verify_samples.py      # 52 样例
```

| 项 | 独立运行结果 | 证据 |
| --- | --- | --- |
| 固定提交与干净树 | **通过**。Gitee 检出 `dd44834383de2bd9af9768a6ecc7fe2c48427eff`，`HEAD` = `origin/main`，`git status --porcelain` = 0 行 | 运行实测 |
| 正式生成 | **通过**。`generated 51 contract files`，exit 0 | `evidence/contracts/generate.log`、`generate-exit.txt` |
| 生成一致性 | **通过**。`contracts check OK (51 files)`，exit 0 | `evidence/contracts/check.log`、`check-exit.txt` |
| 52 样例 | **通过**。`RESULT passed=52 failed=0 blocked=0 notes=0`，exit 0；日志内 `PASS` 行 **52**、`FAIL` 行 **0** | `evidence/contracts/verify-samples.log`、`verify-samples-exit.txt` |
| 生成后工作树 | **仍为 0 行差异**（51 工件逐字节复现，未产生漂移） | 运行实测 |
| 历史 44/8 与根因 | **已闭合**。`a269d49` 的 8 个 `FAIL … private HTTP response lacks status` 全部为 HTTP 失败路径；本次同一 8 项均 PASS | `a269d49-prefix-44of52/verify-samples.log` + 本次日志 |
| 分母独立重算 | **一致**。本地 `contracts/samples/manifest.json` 实读 `cases` = **52**（C1 15 / C2 16 / H 21），与本次日志逐条 id 对应 | 本地 manifest |
| 51 工件自洽 | **一致**。`manifest.json`：`artifacts` 50 项、`source_files` 9 项，逐项 SHA-256 **0 不匹配**；`generator.sha256` 与磁盘 `generate.py` 一致 | 本地重算 |
| 结构声明 | **一致**。17 个 DTO、5 个枚举、OpenAPI 36 个 component、路径仅 `/health` 与 `/__maintenance/contracts/{model_name}`、`securitySchemes` 为空、顶层无 `security`；`comparison.v1` 为 `not_generated` | 本地 `openapi.json`、`manifest.json` |
| B0a/B0c 专题 | 开发者原始证据 **395 passed / 1 warning**，exit 0；本轮非 PG 全套已覆盖 `test_contract_http` 等同类路径，未重复单跑 | `a70a7e2/contracts/pytest-b0a-b0c.log` |
| runtime 专题 | 开发者原始证据 **47 passed / 2 deselected**，exit 0；本轮 PG 八项已覆盖 worker PG 参数化两节点 | `a70a7e2/contracts/pytest-runtime.log` |
| comparison.v1 归属 | **按原规划延期**，未纳入当前验收分母，未记为失败也未记为通过 | `manifest.json` `not_generated` |

## 4. C 前端（AC1）：锁与构建（旧 18 套件未重跑）

| 项 | 独立核对结果 | 证据 |
| --- | --- | --- |
| 正式锁 hash | **一致**。`frontend/package-lock.json` SHA-256 `4b6d69e7…`；服务器 `repo-dd44834` 与 `repo-dd44834-clean` 两处字节数均为 157722 | 本地实测 + SFTP 尺寸 |
| 锁内容独立重算 | **一致**。`lockfileVersion=3`，312 个 package 条目；vue 3.5.44、vite 8.3.4、typescript 6.0.3、vue-router 5.4.0、element-plus 2.14.7、pinia 4.1.0、`@vue/devtools-api` 8.2.1、vitest 4.1.11、vue-tsc 3.3.13 | 本地 `package-lock.json` 解析 |
| peer 关系 | **一致且满足**。pinia peer `@vue/devtools-api ^8.2.1`（`optional:false`）→ 实际 8.2.1；我方声明 `^8.1.5` 同时满足；`@pinia/colada` 等为 optional 未安装；element-plus peer 仅 `vue ^3.3.7` | 同上 |
| 干净 `npm ci` | 开发者原始证据：`added 286 packages in 7s` | `clean-npm-ci.log` |
| 干净 type-check + build | 开发者原始证据：`vue-tsc --build` 与 `vite build` 通过，`1598 modules transformed`、`built in 1.02s`；唯一提示为单 chunk 1,019.39 kB 超 500 kB，非错误 | `clean-build.log` |
| 干净 dist 与首次一致 | **一致**。`repo-dd44834-clean/frontend/dist` 四件尺寸 448 / 364336 / 1019395 / 4286（合计 1,388,465 B）与首次交付逐一相同 | SFTP 尺寸 |
| 单元测试计数 | 开发者原始证据：4 文件 18 个 `it()`（health.spec.ts 12、HealthView.spec.ts 3、contracts.spec.ts 2、App.spec.ts 1） | 本地源码计数 |
| 本轮是否重跑旧 18 套件 | **未重跑**（主控指示）。R1 只改 frontend helper/test 两文件，等 Kimi 交新 dist 后只独立验 R1 相关 + 当前 gateway 一次；其余六个未改用例原证据保留 | 主控指示 |
| 规范前置（GitHub 实读） | **一致**。C0 与 7.1 记录 create-vue v3.23.0 / Vue Router 5.4.0 / Pinia 4.0.2 / Element Plus 2.14.7 的 URL、所读文件、版本标识与拟采用规则，含 Node 24.22.0 官方 SHASUMS256 行 | [frontend-standards.md](/E:/aaa-project/rag/docs/story-1-1-frontend-standards.md:1) |

## 5. D 四服务（AC1+AC3）

### 5.1 镜像来源与版本（只读核对通过）

| 项 | 结果 | 证据 |
| --- | --- | --- |
| 发布方 digest | **一致**。python `sha256:2199a628…`、nginx `sha256:97036422…`、pgvector `sha256:2358fcba…`、uv `sha256:8b940d3a…`，并各有 platform manifest 与 config digest | `official-image-access/image-digest-crosscheck.json`、4 份 receipt |
| 容器内版本事实 | **一致**。CPython `3.12.8 … cpython`、`nginx/1.30.6`、`PostgreSQL 18.6 (Debian 18.6-1.pgdg12+2)`、`extversion=0.8.7`、`uv 0.12.9` | `deploy/offline-images.md` 版本事实表 |
| 离线 FROM 探针 | **一致**。`--network none --pull=false --no-cache` 下四个 index digest 均解析并输出版本 | `official-image-access/from-digest-build-probes.txt` |
| 归档内容一致性 | **一致**。load 后 config digest、层顺序、层 blob hash、`rootfs.diff_ids` 与归档逐项相同 | `official-image-access/post-load-content-identity.txt` |
| daemon 侧映射 | **一致且如实记录**。python/nginx/pgvector 的 daemon image ID 等于发布方 index digest；uv 的 daemon ID 与 index 不同（`537416e3…`），未把新 ID 写成发布方 digest | `image-digest-crosscheck.json` 各条 `daemon_id_equals_official_index` |

### 5.2 构建、预检与四服务运行

| 项 | 结果 | 证据 |
| --- | --- | --- |
| 预检 | **通过**。`{"status": "ready-for-build", "failures": []}` | `/opt/rag-story-1-1/preflight-out.json` |
| dd44834 构建 | **exit 0**。api 与 gateway 均 `Built`；api 内断言 `sys.version_info[:3]==(3,12,8)` 与 `uvicorn==0.37.0`，`uv sync --locked --no-dev` 安装 31 包；`! find /app -xdev -perm /022` 通过 | `/opt/rag-story-1-1/build.log` |
| API/worker 同镜像 | **一致**。`build.log` 中 api 与 worker 两目标 `manifest list sha256:75a1e1bc…` 相同；gateway 为 `145a459118af…` | `build.log` |
| 四服务状态（本轮实测） | **通过**。`gateway` / `api` / `worker` / `postgres` 全部 `Up (healthy)`；`127.0.0.1:8443->8443/tcp` | 运行实测 `docker ps` |
| 迁移 / check-database / stop / start | **原始工具观测已归档**（`migrate_exit=0`、`DATABASE_BASELINE_OK`、`stop_exit=0`、`start_exit=0`；PG 数据 1281 文件保留、重启后 `180006|0.8.7|0001_baseline`、`gateway_health=200`）。未重新执行迁移/启停 | `deploy-integration/lifecycle-original-tool-observations.json` |

### 5.3 网关负例（本轮实测）

| 项 | 独立运行结果 | 证据 |
| --- | --- | --- |
| `GET /health` | **通过**。`HTTP/1.1 200 OK`，`Cache-Control: no-store`，`X-Content-Type-Options: nosniff`，`x-request-id` 存在；body `{"status":"alive","service":"rag-api","check":"liveness"}` | `evidence/gateway/health-headers.txt`、`health-body.json` |
| 维护探针 | **通过**。`POST /__maintenance/contracts/RetrievalResponse` → `404`（生产网关阻断） | 运行实测 |
| hash 资产 | **通过**。`/assets/index-AMOFkByE.css` → `200` + `Cache-Control: public, max-age=31536000, immutable` | `evidence/gateway/asset-headers.txt` |
| 未 hash 路径 | **通过**。`/index.html` → `200` + `Cache-Control: no-store` | `evidence/gateway/unhashed-headers.txt` |
| 2 MiB JSON → 413、20 KB 头 → 400、条件请求无 304、原件 1.5 MiB → 404 | 主控增量已观测；静态规则与 `nginx.conf` 一致（`client_max_body_size 1m`、`large_client_header_buffers 2 8k`、清空条件头、`etag off`）。原件 404 因上传路由未实现，**不纳为当前缺陷** | 主控增量 + `nginx.conf` |

### 5.4 浏览器：真实 200% 页面缩放口径核对（原有验收行语义）

**发现**：C 归档的 `200zoom` 行**不是页面 200% 缩放**。原始脚本把该场景参数用作 `deviceScaleFactor: 2`，没有任何页面缩放调用；其 `run.json` 记录 `clientWidth: 768`，而真实 200% 缩放下 CSS 布局视口应为 384。`DPR=2` / 高清截图不能称为页面 200% 缩放。

**两种方法实测对照**（同一真实 gateway `https://127.0.0.1:8443`）：

| 方法 | devicePixelRatio | CSS 布局视口 | panel 宽度 |
| --- | --- | --- | --- |
| 复现 C 的做法（viewport 768 + DSR 2） | 2 | **768**（未变） | 720 CSS px |
| 真实 200% 页面缩放（viewport 384 + DSR 1） | 1 | **384**（减半） | 352 CSS px |

**在真实 200% 页面缩放下补做的布局/控件检查**（单次，未重跑 3 视口矩阵，未改应用）：

| 检查项 | 结果 |
| --- | --- |
| 方法（已固化在 run.json） | context viewport 384x450 CSS px + `deviceScaleFactor: 1`，即 768 px 页面在 200% 缩放时的 CSS 布局视口；`devicePixelRatio` 断言为 1 |
| goto | 200 |
| devicePixelRatio | 1（排除与高清截图混淆） |
| 横向溢出 | `scrollWidth` 384 = `clientWidth` 384，`horizontalOverflow = false`，`overflowingElements = []` |
| 触达目标 | `el-tag` 59.6 x **44** CSS px；`button` 64 x 32（宽 ≥ 44） |
| 布局包裹 | `.status-line` `flex-wrap: wrap` |
| 文案 | `接口可达`；固定说明"不代表数据库已就绪"存在；HTTP 状态 `200` |
| 键盘 | Tab 焦点 = `BUTTON "重新检查"`，轮廓 `2px solid` |
| 键盘激活 | Enter 触发 **1** 个新 `/health` 请求（单 flight，无自动重试） |
| console / pageErrors | 0 / 0 |
| 截图 | `01-real-200pct-loaded.png`、`02-real-200pct-after-keyboard.png` |

**环境限制（如实记录）**：chrome-headless-shell 缺 CJK 字体，截图中中文呈缺字形。这是测试环境限制，不是应用缺陷；本核对不为它下载大字体或重开整套，以上述 DOM 测量与文本断言为判定依据。

完整方法与数据：`/fileOfRag/testOfRAG/metadata/story-1-1/independent-verification/browser-200zoom-method.txt`；本机实测 JSON：`/opt/rag-story-1-1/independent-verify/evidence/browser-200zoom/A-dpr2-only-as-C-did.json`、`B-real-200pct-page-zoom.json`、`run.json`，脚本 `zoom-check.js`、`zoom-controls.js`，截图 `01-real-200pct-loaded.png`、`02-real-200pct-after-keyboard.png`。

### 5.5 干净重建：镜像内容可复现性

| 项 | 独立核对结果 | 证据 |
| --- | --- | --- |
| frontend 干净重建 | **通过**。干净 `npm ci` 286 包、`vue-tsc` + `vite build` 通过、1598 模块；两次独立检出 dist 四件尺寸完全一致 | `clean-npm-ci.log`、`clean-build.log` + SFTP 尺寸 |
| 镜像 image ID | 两次不同：api `75a1e1bc5f99…` vs `a8389949fcf0…`；gateway `145a459118af…` vs `18161db2d220…`；层数均为 13 | `evidence/reproducibility.txt` |
| 层 diff_id 比对 | 层 1-5、13 相同；层 6-12 不同 | 同上 |
| `/app` 内容指纹 | 两次均为 `sha256:9e032052d7d43ee26720e04d3ad96882e01e8e7857d3bdac135c2563e6d8b308` → **相同** | 同上 |
| `/opt/venv` 内容指纹 | 两次均为 `sha256:575057c63dcacbcb41e1a53cde4cb184a4a9cdc17c9541040ba1b4bc262c4af9` → **相同** | 同上 |
| `/opt/venv` dist-info 元数据指纹 | 两次均为 `sha256:abcfa6a9d4df344d1781bc2560b5e4cdcae08b39ed303063535e7e1e926a304a` → **相同** | 同上 |
| 容器内版本 | Python 两次均 `3.12.8`；uvicorn 两次均 `0.37.0`；site-packages 目录列表相同 | 同上 |
| 差异来源（已定位） | 含 `stat` 的完整指纹不同；逐行 diff 显示唯一差异字段是 **mtime**（app 目录 1792257394 vs 1792258697），size / mode / owner / 内容 hash 全部一致 | 同上 |
| 判定 | **内容可复现成立**；镜像 image ID 因 BuildKit 时间戳/attestation 不同而不同，属已知非可复现构建元数据，不作为内容偏差，也不冒充字节级可复现 | 同上 |
| clean job 标识 | `job_mvcoe2a7_47c17b71d8ce`（后台，未 kill、未重复 build） | 主控提供的 job id |
| clean job 最终状态 | **三目标均 `Built`**（`rag-story-1-1-api:clean-dd44834`、`rag-story-1-1-gateway:clean-dd44834`）；**未取得 `CLEAN_BUILD_EXIT` 退出码**——`/opt/rag-story-1-1/` 下无退出码文件，本记录只读核对原日志，未重跑、未另行构建 | `/opt/rag-story-1-1/clean-build-images.log`（8929 B，最后修改 2026-10-17 17:38:25） |

## 6. E 来源与许可证（AC3）

- 后端：`backend-dependency-inventory.json` 已归档（47,516 B），覆盖 `gen-sync.log` 中 41 个解析 / 39 个安装包的版本清单。
- 镜像：见 5.1 四项 receipt（发布方 digest + 版本事实 + 层核对）。
- 前端：锁文件 312 条目与 18 个关键包版本已独立重算（第 4 节）。
- **未齐**：四服务实际 UID/权限与锁/原子操作实测、最终运行镜像 digest 登记；本轮未扩范围。

## 7. 逐 AC 结论

| AC | 结论 | 依据 |
| --- | --- | --- |
| AC1 精确 3.12.8 / 锁 / Uvicorn / 前端可重建 | **独立运行通过**（A1 全套、C 锁/构建、R1 health 14 例、新 gateway 产物与交互） | 第 1、4、12 节 |
| AC2 PG 18.6 / pgvector 0.8.7 / 六项必跑 / 迁移循环 / namespace / 回滚 / 无生产向量 | **独立运行通过** | 第 2 节：8/8 真实通过、0 skip、清理后 0 schema、vector 未动 |
| AC3 来源/许可证/依赖边界/hash/digest | **passed** | 第 5.1、5.5、6、12、13、14 节：后端/镜像/前端版本与 hash 已核、干净重建两镜像 `Built` 且应用与 venv 指纹相同、新 gateway 镜像 ID 与 index/JS 哈希均实测一致、四容器实际 UID 与挂载权限已实测、**跨 API/worker 共享 inode / flock / 原子替换已实测通过**；仍保留 clean wrapper 退出码未记录的限制（不另加为新重建门） |
| AC4 公共契约 C1/C2 + H 边界 + HTTP 信封 + OpenAPI/Schema/TS/样例 | **独立运行通过** | 第 3 节：51 工件 `--check` 通过、52/52 样例、8 个历史 HTTP 失败全部转 PASS |
| AC1+AC3 四服务 Linux 生命周期与干净重建 | **passed**（构建/运行/权限/锁/原子替换/迁移/停止重启，原始工具观测已归档） | 第 5.2、5.3、5.5、14、15 节 |

## 8. 独立发现的问题（只记可证影响）

1. **C 的"200%"不是页面缩放（原有验收行语义偏差，已补证）**：`browser-test/run-evidence.js` 的 `200zoom` 场景把参数用作 `deviceScaleFactor: 2`，没有任何页面缩放调用；其 `run.json` 记录 `clientWidth: 768`，而真实 200% 缩放下 CSS 布局视口应为 384。`DPR=2` / 高清截图不能称为页面 200% 缩放。
   - 影响：该验收行的语义不成立；已在真实 200% 页面缩放下补做布局/控件检查并通过（见 5.4），方法已固化。
   - 归属：前端原作者更正表述；本验证不改应用、不重跑 3 视口矩阵、不新增验收范围。
2. **生成 Schema 的 constraint 差异确实存在（本验证早期推断已更正）**：23 组 validation/serialization schema 对**全部不同**；8 组 serialization 侧含 `"pattern"` 而 validation 侧无，4 组 validation 侧含 `"maxLength"` 而 serialization 侧无。实例：[FailedResponse.serialization.schema.json](/E:/aaa-project/rag/contracts/schemas/operation.v1/FailedResponse.serialization.schema.json:1) 用 `^[A-Za-z0-9_-]+$`，[FailedResponse.validation.schema.json](/E:/aaa-project/rag/contracts/schemas/operation.v1/FailedResponse.validation.schema.json:1) 用 `minLength 1` / `maxLength 64`。
   - 影响：本验证早期据"两个 `.ts` 只差注释"推断 schema 无差异，该推断**不成立**并已更正。TypeScript 只投影模型结构，不表达 pattern/长度/跨字段校验，因此 `.ts` 结构相同不能否定 schema 差异；交付记录"两方向用途不同、不能互替"的表述成立。
   - 归属：验证者自身推断错误，已如实记录；不改生成器、不做前端适配。
3. **文档登记与工作区源码不一致（deploy 四服务段）**：[story-1-1-deploy-delivery.md](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:364) 登记的 `compose.yaml` hash `5e392575…` 与工作区实际 `64c48784…` 不符；该段声称的 `pull_policy: never` 在当前 [compose.yaml](/E:/aaa-project/rag/deploy/compose.yaml:1) 中**不存在**，`RAG_PGDATA_ROOT` 默认值仍为 `/opt/rag-story-1-1/postgres`（文档写 `postgres-d`），文档引用的 `deploy/integration.env.example` 文件**不存在**。
   - 影响：该段自称的"冻结观察值"与执行模板与工作区字节、实际执行方式不符；服务器实际使用仓库外 `/opt/rag-story-1-1/deploy-integration.env`。不影响已取得的构建/预检/迁移/生命周期运行证据。
   - 归属：文档登记问题，由原作者修正登记，不在本轮运行门内。
4. **待最终发布项（非缺陷）**：`deploy/tools/acquire_official_images.py`、`deploy/offline-images.md` 的 78 行新增、`docs/story-1-1-frontend-delivery.md`、`docs/story-1-1-official-image-access.md`、`docs/frontend-dependency-inventory.json` 已如实声明尚未发布。
   - 影响：**无**。dirty 工作区只表示待最终发布，不等于两远端 commit 不一致，也不构成源码缺陷；GitHub/Gitee 仍同为 `dd44834`，服务器固定检出亦为该提交。
   - 归属：主控统一发布职责，验证者不改 Git，不要求工具或 `__pycache__` 入库，不新增安全扫描或审查门。

## 9. 未执行与风险（如实保留）

- **clean job wrapper 退出码未记录（保留的限制，不追加重建门）**：`job_mvcoe2a7_47c17b71d8ce` 现已 `Background job not found`，wrapper 退出码未记录，**不填假 0**，也不因此另加新的重建门。可用的直接重建证据是：BuildKit 完整两镜像 + worker 共用目标均 `Built`、实际 clean 镜像存在、两次构建的 `/app` 与 `/opt/venv` 内容指纹相同、逐层 diff_id 已由 `clean-rebuild-fingerprint.txt` 记录。`GATEWAY_BUILD_EXIT=0` 已由 D 提供并归档。
- **前端未重跑项**：旧 18 套件全量与完整前端矩阵未重跑；其余六个未改前端用例沿用原证据。R1 只核 `health.spec.ts` 14 例 + 新 gateway。
- **AC3 唯一缺项已闭合**：`locks-assets-uid-probe.txt` 已实测容器实际 UID、挂载权限、共享 inode（674851/674852 三处一致）、跨容器 flock 互斥（worker 持锁 12s 期间 API `EWOULDBLOCK`，释放后 API 取得）与 `os.replace` 原子替换（API 见 `atomic-replace-v2`、tmp 消失），详见第 14 节。
- **已归档（不再是限制）**：迁移 exit 0 与 `DATABASE_BASELINE_OK`、stop/start 原始命令与退出码、1281 文件保留与重启后版本不变，均已由 `deploy-integration/lifecycle-original-tool-observations.json` 归档（见第 15 节）。
- **not-executed（不属当前 Story 必需）**：original 上传路由本体（1.5 MiB 走 404 是路由未实现的结果，不是当前缺陷）、comparison.v1 业务、目标部署环境 4C4G 与外发上传。
- **未由本记录放行**：全新 `6.1 Sol / medium` 正式代码审查及其修复回归；本验证不替代该门。
- 既有风险（非本轮新增）：JSON Schema 不能表达 Pydantic 跨字段校验，运行时权威仍是后端模型；探针路径必须由生产网关阻断（已实测 `404`）。

## 10. 证据索引

本次独立运行（`/opt/rag-story-1-1/independent-verify/`）：

- `repo-iv/`：Gitee 固定检出 `dd44834383de2bd9af9768a6ecc7fe2c48427eff`（HEAD = origin/main，工作树 0 行）
- `source-hashes.txt`：16 个关键文件 SHA-256，与本地逐一相符
- `venv-iv/`：独立 venv（Python 3.12.8 / uvicorn 0.37.0 / pytest 8.4.2）
- `evidence/non-pg/{pytest.log,junit.xml}`：514 passed / 1 skipped / 8 deselected
- `evidence/non-target/{interpreter.txt,pytest.log,junit.xml}`：真实 3.12.3 上 1 passed
- `evidence/pg-8/{pytest.log,junit.xml,exit-code.txt,env-check.txt,schemas-before.txt,schemas-after.txt,public-tables-before.txt,public-tables-after.txt,vector-before.txt,vector-after.txt,server-version-num.txt}`：8 passed / 0 skip
- `evidence/contracts/{generate.log,generate-exit.txt,check.log,check-exit.txt,verify-samples.log,verify-samples-exit.txt}`：51 工件、check OK、52/52
- `evidence/gateway/{health-headers.txt,health-body.json,asset-headers.txt,unhashed-headers.txt}`
- `evidence/browser-200zoom/`：`A-dpr2-only-as-C-did.json`、`B-real-200pct-page-zoom.json`、`run.json`、两张截图
- `evidence/reproducibility.txt`：干净重建内容可复现性核对
- `zoom-check.js`、`zoom-controls.js`：缩放口径核对脚本
- `r1/repo-252/`：Gitee 固定检出 `25232d0bebc230c35837153b6fd572ff734977aa`（HEAD = origin/main，工作树 0 行）
- `r1/npm-ci.log`：`added 286 packages in 7s`，exit 0
- `r1/health-spec.log`：14 passed / 14，exit 0
- `r1/health-spec-on-old-helper.log`：反向验证 `2 failed / 12 passed (14)`
- `r1/gw-index.html`、`gw-index-CDataiw2.js`、`gw-index-headers.txt`、`gw-js-headers.txt`、`gw-health-headers.txt`、`gw-health-body.json`、`gw-unhashed.txt`
- `r1/gw-browser/run.json`、`gw-smoke.js`：真实浏览器基本交互

归档（`/fileOfRag/testOfRAG/metadata/story-1-1/independent-verification/`）：

- `run-summary.txt`：本次实际运行汇总（原始命令 / exit / JUnit 计数）
- `reproducibility.txt`：干净重建镜像内容可复现性
- `browser-200zoom-method.txt`：200% 缩放口径语义核对与方法
- `clean-job-final-status.txt`：clean job 最终状态（三目标 Built，退出码未取得）
- `r1-health-and-new-gateway.txt`：R1 health 14 例 + 新 gateway 核验
- `ac3-final-closure.txt`：AC3 最终缺项（UID/挂载/共享锁/原子替换）闭合核对

D 归档（只读核对，本次未运行）：`/fileOfRag/testOfRAG/metadata/story-1-1/deploy-integration/` 共 **20 个文件**（D 交付记录冻结于 `80282789…`，其他源码未变），新增 `lifecycle-original-tool-observations.json`（SHA `daeed77f…`，见第 15 节） —— `container-identity.txt`、`compose-ps.txt`、`gateway-252-build.log`、`gateway-252-inspect.json`、`gateway-container-dist.txt`、`clean-rebuild-fingerprint.txt`、`clean-build-images.log`、`clean-build.log`、`clean-npm-ci.log`、`build.log`、`preflight-out.json`、`pg-versions.txt`、`http-health-headers.txt`、`http-health-body.json`、`http-new-index-headers.txt`、`http-new-js-headers.txt`、`deploy-integration.env.keys.txt`、`SHA256SUMS.bucket.txt`。

复用既有证据（未重跑）：`/fileOfRag/testOfRAG/metadata/story-1-1/linux-developer-gates/{a70a7e2,a269d49-prefix-44of52,9da9af2-pg}/`、`official-image-access/`、`a1-python-3128/`；`/opt/rag-story-1-1/{build.log,clean-build-images.log,clean-build.log,clean-npm-ci.log,preflight-out.json}`。

## 11. 结论

本次已由本验证者在 Netcatty Linux 上对固定提交 `dd44834383de2bd9af9768a6ecc7fe2c48427eff` **实际独立运行一次**：

- 后端非 PG 全套：**514 passed / 1 skipped / 8 deselected**，exit 0（JUnit `tests=515 errors=0 failures=0 skipped=1`）
- 真实 3.12.3 负例：**1 passed**，exit 0（JUnit `tests=1 skipped=0`）
- PG 八项 `--require-postgres`：**8 passed / 0 failed / 0 error / 0 skipped**，exit 0；运行前后 `rag_test_%` schema 均为 0、`public` 表 0、`vector` 仍 0.8.7
- contracts：`generated 51` / `check OK (51 files)` / 样例 `passed=52 failed=0 blocked=0 notes=0`，三项均 exit 0
- 真实 gateway：`/health` 200 + `no-store`、`/__maintenance/` 404、hash 资产 `immutable`、未 hash 路径 `no-store`
- 真实 200% 页面缩放：无横向溢出、44px 触达、2px 焦点环、Enter 触发 1 次请求、0 console/page error
- R1 健康路径：`health.spec.ts` **14 passed**，exit 0；反向验证（旧 helper）`2 failed | 12 passed`，证明新测试有效
- 新 gateway：镜像 ID `6ae64cf42fc2…`、`index.html` `4bd67fe3…`、`fade5263…` 均与提供值一致；浏览器手动 refresh 新增 1 次 `/health`，0 console/page error

**AC1、AC2、AC3、AC4 均已取得可复算的实测证据**：AC1（A1 全套、C 锁/构建、R1 health 14 例、新 gateway 产物与交互）、AC2（PG 八项 8/8、0 skip、清理后 0 schema、vector 未动）、AC4（51 工件 check OK、52/52 样例、8 个历史 HTTP 失败全部转 PASS）、AC3（来源/版本/hash/digest、干净重建层指纹、四容器 UID、挂载权限、共享 inode、跨容器 flock 互斥、原子替换全部实测通过）。

父 Story 完成门仍未通过，未放行 Story 1.2。**父 Story 是否完成由主控作最终裁决**；本记录只提供独立核验证据与未记录限制。
## 12. R1 修复（`25232d0b`）健康路径 + 新 gateway 独立核验

### 12.1 变更范围核对

`git diff --name-status dd44834 25232d0b`：应用文件仅两项 —— `frontend/src/api/health.ts`（+10/-2）与 `frontend/src/__tests__/health.spec.ts`；其余为 `AGENTS.md` 与 `_bmad-output` 文档/状态。

`backend` / `contracts` / `deploy` / `frontend/package.json` / `frontend/package-lock.json` 的 `git diff --numstat` 为**空**；`package-lock.json` SHA-256 仍为 `4b6d69e7…`。因此第 1-3 节的后端 / PG / contracts 独立运行结果**不因新 commit 重复**。

### 12.2 修复内容与反向验证

原实现 `} catch { json = undefined }` 吞掉正文读取阶段的一切异常；修复后只有 `SyntaxError` 映射为 `invalid-body`，正文阶段的 `AbortError`（超时或调用方取消）与传输错误向上传播，由外层保持 `timeout` / `network-error` 分类。

**反向验证（补充证据，仅此一次）**：在隔离验证目录 `/opt/rag-story-1-1/independent-verify/r1/repo-252/frontend/` 内把 `src/api/health.ts` 临时换回 `dd44834` 版本后重跑同一 14 例，结果为 `2 failed | 12 passed (14)`，失败的正是两条 R1 新增用例；随后 `git checkout --` 恢复 252 版本，最终工作树干净。说明新测试不是空断言。该反向探针是对隔离检出副本的临时改动并已恢复干净，不构成对仓库源码的修改，也不重开或重跑。

### 12.3 独立运行：`health.spec.ts` 14 例

```sh
npm ci --no-audit --no-fund     # added 286 packages in 7s, exit 0
npx vitest run src/__tests__/health.spec.ts --reporter=verbose
```

| 项 | 结果 |
| --- | --- |
| vitest | v4.1.11 |
| Test Files | **1 passed (1)** |
| Tests | **14 passed (14)** |
| Duration | 1.11s |
| 退出码 | **0** |
| 用例计数 | `health.spec.ts` 内 `it()` = 14，与运行数一致 |
| 其中 R1 新增 | `classifies body-phase timeout as FetchTimeoutError after 200 headers`、`propagates caller abort during body read, not as invalid-body` |

### 12.4 新 gateway 产物与运行核验

| 项 | 独立核验结果 | 证据 |
| --- | --- | --- |
| gateway 容器 | `rag-story-1-1-gateway-1` `Up (healthy)` | 运行实测 |
| gateway 镜像 ID | `sha256:6ae64cf42fc2a0edc2b145b1a09f5e9c5541453318e21a7d0043afd922923ffa`，与主控提供的当前 gateway 镜像**一致** | 运行实测 |
| `index.html` | 200，448 B；SHA-256 `4bd67fe33d6d6a226846e2c1b4c37931f02159f4f158319d313d2e124fe5817f`，与主控提供值**一致** | 运行实测 |
| 引用资产 | `/assets/index-CDataiw2.js` + `/assets/index-AMOFkByE.css` | 同上 |
| 新 JS | 200，1,019,439 B，`Cache-Control: public, max-age=31536000, immutable`；SHA-256 `fade5263dc4a33deba1bc7de956fc2497fc1f1d343ce2de0acdb781f8de9348a`，与主控提供值**一致** | 运行实测 |
| `/health` | 200，`Cache-Control: no-store`、`X-Content-Type-Options: nosniff`、`x-request-id` 存在；body `{"status":"alive","service":"rag-api","check":"liveness"}` | 运行实测 |
| 维护探针 | `POST /__maintenance/contracts/RetrievalResponse` → **404** | 运行实测 |
| 未 hash 路径 | `GET /index.html` → 200 + `Cache-Control: no-store` | 运行实测 |

### 12.5 真实浏览器一次基本交互

| 检查项 | 结果 |
| --- | --- |
| goto | 200 |
| 首屏 | `接口可达` / HTTP 状态 `200` |
| 实际加载的 script | `/assets/index-CDataiw2.js`（确认是新产物） |
| 手动点击"重新检查" | 新增 `/health` 请求 **1** 次（单 flight，无自动重试） |
| 刷新后 | `接口可达` / `200` |
| `/health` 请求 | 2 次，均 200 |
| console / pageErrors | 0 / 0 |

完整记录：`/fileOfRag/testOfRAG/metadata/story-1-1/independent-verification/r1-health-and-new-gateway.txt`。

## 13. D18 部署集成归档证据（只读核对）

Mencius 将 D 四服务集成证据归档到 `/fileOfRag/testOfRAG/metadata/story-1-1/deploy-integration/`，共 **18 个文件**（清单见 `SHA256SUMS.bucket.txt`）。本验证者只读核对了全部 18 个文件，未运行任何命令。

### 13.1 已核对的证据

| 文件 | 内容 | 与 AC3 的关系 |
| --- | --- | --- |
| `container-identity.txt` | 四容器 id / image / **user** / status / health：api `c2b1db78…` user `65532:65532`；worker `a8dc8911…` user `65532:65532`；gateway `999aca6a…` user `65532:65532`；postgres `ea70ab2d…` user `999:999`；四者均 `running` / `healthy` | **容器实际 UID 已记录**（补上原 D 待实测项的一部分） |
| `compose-ps.txt` | `docker compose ps` 原始输出：四服务 `Up (healthy)`，api/worker 同镜像 `rag-story-1-1-api:local`，gateway `127.0.0.1:8443->8443/tcp` | 四服务运行状态 |
| `gateway-252-build.log` | `rag-story-1-1-gateway:local Built`；`manifest list sha256:6ae64cf42fc2…`；nginx 基础 `nginx:1.30.6-alpine@sha256:35b34a15…` | 新 gateway 构建 |
| `gateway-252-inspect.json` | 镜像 `Id` = `sha256:6ae64cf42fc2…`，`Config.User` = `65532:65532`，`NGINX_VERSION=1.30.6`，`RootFS.Layers` 11 层，`Os/Architecture` = `linux/amd64` | 新 gateway 身份与非 root |
| `gateway-container-dist.txt` | 容器内 `/usr/share/nginx/html/` 三件 SHA-256：css `9a485ada…`、js `fade5263…`、`index.html` `4bd67fe3…` | 容器内产物哈希 |
| `clean-rebuild-fingerprint.txt` | api clean `a8389949…`（13 层，逐层 diff_id 列出）、gateway clean `18161db2…`（11 层，逐层 diff_id 列出）、api local `75a1e1bc…`、gateway local `6ae64cf42fc2…` | 干净重建层指纹 |
| `clean-build-images.log` / `clean-build.log` / `clean-npm-ci.log` | 干净构建三份原始日志 | 干净重建 |
| `build.log` | 首次四服务构建原始日志 | 构建 |
| `preflight-out.json` | `{"status": "ready-for-build", "failures": []}` | 预检 |
| `pg-versions.txt` | `180006|0.8.7|0001_baseline` | PG 版本与迁移版本 |
| `http-health-headers.txt` / `http-health-body.json` | 200 + `Cache-Control: no-store` + `X-Content-Type-Options: nosniff` + `x-request-id`；body `{"status":"alive","service":"rag-api","check":"liveness"}` | 网关 health |
| `http-new-index-headers.txt` | 200，448 B，`Cache-Control: no-store` | 未 hash 路径 |
| `http-new-js-headers.txt` | 200，1,019,439 B，`Cache-Control: public, max-age=31536000, immutable` | hash 资产 |
| `deploy-integration.env.keys.txt` | 23 个变量名，值全部 `<redacted>` | 凭据未泄漏 |
| `SHA256SUMS.bucket.txt` | 18 个文件的 SHA-256 清单 | 归档完整性 |

### 13.2 D18 当时的缺项（已由第 14 节闭合）

- **容器实际 UID/挂载权限**：`container-identity.txt` 已记录四容器的 `user`（api/worker/gateway `65532:65532`，postgres `999:999`），但**挂载点在容器内的实际属主/模式、以及跨 API/worker 共享 `assets`/`locks` 目录的可读写结果尚未实测**。
- **跨 API/worker 共享 inode / flock / 原子替换**：D18 归档时（18 个文件）该项**尚无**诊断文件；其后 Mencius 补测并归档 `locks-assets-uid-probe.txt`，实测结论见第 14 节，该项已闭合。
- AC3 的该项缺口**已由第 14 节闭合**；clean wrapper 退出码未记录，作为已记录限制保留，不追加重建门。

> 该缺项已由 Mencius 完成并归档为 `locks-assets-uid-probe.txt`，本验证者只读核对后已在第 14 节闭合 AC3 该项；不重跑自身后端/前端，不新扩矩阵。

## 14. AC3 最终缺项实测：UID / 挂载权限 / 共享锁 / 原子替换

Mencius 已完成原 D 唯一缺项并归档：`/fileOfRag/testOfRAG/metadata/story-1-1/deploy-integration/locks-assets-uid-probe.txt`（2885 B，SHA-256 `f5ae1a320a71ae18a901e149cc5845a6cc6a95ea37c6d69d32f80436ffb072fd`，与 `SHA256SUMS.bucket.txt` 记录值一致）。本验证者只读核对该原始诊断，未运行任何命令。桶目录现为 **19 个文件** + `SHA256SUMS.bucket.txt`（SHA `280d593e…`，比此前 18 件多出本探针文件）。

### 14.1 容器实际 UID 与挂载权限

| 检查项 | 实测结果 |
| --- | --- |
| api 容器内身份 | `uid=65532 gid=65532 groups=65532` |
| worker 容器内身份 | `uid=65532 gid=65532 groups=65532` |
| gateway 容器内身份 | `uid=65532 gid=65532 groups=65532` |
| postgres 容器内身份 | `uid=999(postgres) gid=999(postgres) groups=999(postgres)` |
| 宿主目录 | `assets` `750 65532:65532`；`locks` `750 65532:65532`；`epoch` `550 65532:65532`；`secrets` `700 0:0` |
| 宿主秘密文件 | `postgres-pgpass` `400 65532:65532`；`tls-cert.pem` `400 65532:65532`；`tls-key.pem` `400 65532:65532`（未读值） |
| api 挂载 | `assets`→`/var/lib/rag/assets` **rw=true**；`locks`→`/var/lib/rag/locks` **rw=true**；`epoch`→`/var/lib/rag/epoch` **rw=false**；`postgres_pgpass`→`/run/secrets/` **rw=false** |
| worker 挂载 | 与 api 完全一致（`assets`/`locks` rw=true，`epoch`/`pgpass` rw=false） |
| gateway 挂载 | `tls-cert.pem`/`tls-key.pem` → `/run/tls/` **rw=false** |
| api 容器内 stat | `assets` `750 65532:65532`；`locks` `750 65532:65532`；`epoch` `550 65532:65532`；`postgres_pgpass` `400 65532:65532` |
| worker 容器内 stat | `assets` `750 65532:65532`；`locks` `750 65532:65532` |
| gateway 容器内 stat | `tls-cert.pem` `400 65532:65532`；`tls-key.pem` `400 65532:65532` |
| 文件系统 | api 与 worker 均为 `ext4 /dev/vda2 /`（非对象存储） |

宿主声明的属主/模式与容器内实际看到的一致，跨 API/worker 的 `assets`/`locks` 为同一绑定且可读写，`epoch` 只读，秘密文件只读且模式 `400`。

### 14.2 共享 inode 一致性

| 探针文件 | host inode | api inode | worker inode | 模式/属主 |
| --- | --- | --- | --- | --- |
| `locks/ragprobe20261018a.lock` | **674851** | **674851** | **674851** | `640 65532:65532` |
| `assets/ragprobe20261018a.final` | **674852** | **674852** | **674852** | `640 65532:65532` |

host / api / worker 三处 inode 逐一相同，证明 API 与 worker 看到的是同一文件系统实体，不是各自副本——这是共享锁与原子替换有意义的前提。

### 14.3 跨进程 flock 互斥

| 步骤 | 实测结果 |
| --- | --- |
| worker | `LOCK_EX acquired, held 12s` |
| worker 持锁期间的 api | `LOCK_EX \| LOCK_NB` → `BlockingIOError (EWOULDBLOCK)`，**未获取** |
| worker 释放后的 api | `LOCK_EX acquired then released` |

即真实跨容器 flock 互斥成立：worker 持锁时 API 的非阻塞取锁立即失败，释放后 API 能取得。

### 14.4 原子替换

| 步骤 | 实测结果 |
| --- | --- |
| worker | 写 `ragprobe20261018a.tmp` 后 `os.replace` → `ragprobe20261018a.final` |
| api 读 final | `atomic-replace-v2`（看到替换后的完整内容） |
| api 检查 tmp | `ls: cannot access .../ragprobe20261018a.tmp: No such file or directory` → `gone` |

原子替换在同一 ext4 绑定上跨容器生效，读者不会看到半写状态，临时文件不残留。

### 14.5 清理与影响面

- 只清理本次 3 个新探针文件（`ragprobe20261018a.lock`、`.tmp`、`.final`）；未删除既有宿主目录、锁文件或存储桶内容。
- 四服务在探针后仍 `healthy`（与原 D 记录一致）。
- 秘密文件只记录模式/属主，未读取值；`deploy-integration.env.keys.txt` 中 23 个变量值全部 `<redacted>`。

### 14.6 对 AC3 的意义

原 D 交付记录第 26/43/144 行列为待实测的三项——容器挂载权限、跨 API/worker 共享 inode、flock 与原子替换——现已全部取得真实 Linux 实测证据。`ext4` 名称本身不证明这些语义，但本次是在真实容器对内实测的，因此 AC3 的该缺口闭合。

## 15. 生命周期原始工具观测（归档登记）

归档文件：`/fileOfRag/testOfRAG/metadata/story-1-1/deploy-integration/lifecycle-original-tool-observations.json`（8050 B）

SHA-256：`daeed77fc05261b5e15398697a1a8bf548c841e7ca6ade68e5824e7e178990c3`（远程实测与主控提供的本地值一致）

来源：主控从已关闭 D 的真实 rollout 按 `call_id` 导出 3 条既有 Netcatty `terminal_execute` 观测（actor `01a14a3e-ba7c-74e3-a162-b8f092a80308`），连接串与 token 模式已脱敏；**未重新执行**迁移/启停。本验证者只读核对该归档，未运行任何命令。

### 15.1 三条记录

| call_id | 观测时间 (UTC) | 内容 | 结果 |
| --- | --- | --- | --- |
| `call_00_LjeO6siPV7V7qrR7RgWe6343` | 2026-10-17T17:26:21.228Z（输出 17:26:29.446Z） | `docker compose run --rm --no-deps --pull never api python -m rag_app migrate head` + `check-database` + schema/extension 查询 | `migrate_exit=0`、`DATABASE_BASELINE_OK`、`check_exit=0`；`vector 0.8.7`、`alembic_version 0001_baseline`、表 `alembic_version` 与 `rag_uow_probe` |
| `call_00_EfCUn0gkPn2RUiD3M6UQ4635` | 2026-10-17T17:30:54.884Z | 首条 stop/start 尝试 | **被工具安全策略拦截**（命令内含 `$(`），原始失败如实保留，不冒充通过 |
| `call_00_iDRrP3huvUunKpjw9Vqg4902` | 2026-10-17T17:31:09.005Z（输出 17:31:46.564Z） | `docker compose stop --timeout 20` + `start` + 健康/版本/数据查询 | `stop_exit=0`、`start_exit=0`；stop 后四容器 `Exited`（api 143 = SIGTERM），PG 数据 **1281 文件仍在**；start 后四服务全部 `Up (healthy)`，`gateway_health=200`，版本 `180006|0.8.7|0001_baseline`，`rag_uow_probe` 行数 0 |

### 15.2 对原限制的更正

本报告此前将"迁移 exit 0 / `DATABASE_BASELINE_OK` / stop/start 原始命令与退出码 / 1281 文件保留 / 重启版本不变"列为**原始未归档**限制。该表述**已过时**：上述内容现已由 `lifecycle-original-tool-observations.json` 归档，索引与哈希如上。

因此第 5.2、7、9、13.2 节中相应限制表述以本节为准。

### 15.3 仍保留的限制

- **clean job wrapper 退出码未记录**：`job_mvcoe2a7_47c17b71d8ce` 已 `Background job not found`，未填假 0，不因此另加新的重建门；直接重建证据为 BuildKit 两镜像 + worker 共用目标均 `Built`、clean 镜像存在、`/app` 与 `/opt/venv` 内容指纹相同、逐层 diff_id 已记录。
- **CJK 字体缺项**：chrome-headless-shell 测试环境无中文字体，截图中中文呈缺字形；属测试环境限制，非应用缺陷，不为它下载大字体或重开整套。
- **旧 18 前端套件与完整矩阵未重跑**：R1 只核 `health.spec.ts` 14 例 + 新 gateway；其余六个未改前端用例沿用原证据。
