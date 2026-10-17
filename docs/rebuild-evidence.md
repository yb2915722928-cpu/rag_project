# Story 1.1 修复与重建证据

2026-10-17。本轮只修改后端和本文件，没有操作容器、启动其他 agent，或修改项目规则、规格、Sprint、review/relay 记录。验收由主会话负责。

**当前不能宣称 Story 验收通过。** 本机补充测试使用 CPython 3.12.8；目标 CPython 3.12.15 和真实 PostgreSQL 18.6 / pgvector 0.8.7 验收均未执行。旧锁文件尚未重新解算，不能作为本轮新声明的有效锁。

## 修复内容

1. [迁移](/E:/aaa-project/rag/backend/migrations/versions/0001_baseline.py:1) 将 vector 作为数据库设施：upgrade 先核精确版本，缺失时仅安装明确的 0.8.7；downgrade 只删除本迁移拥有的探针表，保留共享扩展。[迁移环境](/E:/aaa-project/rag/backend/migrations/env.py:1) 在 Alembic 创建版本表之前核服务/扩展版本和目标 schema，拒绝不能在线核版本的离线迁移。
2. [PG 测试夹具](/E:/aaa-project/rag/backend/tests/conftest.py:1) 只在同时提供测试 DSN 和 `RAG_TEST_ALLOW_SCHEMA_CREATE=1` 后执行。共享扩展必须由环境准备者预置为 0.8.7。每个用例生成新的 `rag_test_<uuid>` schema；只有成功创建后才清理该 schema。移除了固定 9001 的删除和一切用户既有行操作。
3. [真实 PG 用例](/E:/aaa-project/rag/backend/tests/test_postgres_integration.py:1) 包含 base→head→base→head、revision、精确服务/扩展版本、列非空、降级保留扩展、整个应用 schema 无向量列/ANN、临时向量表达式、仓储不提交和异常回滚、真实驱动错误保密。版本负例在独立 schema 中注入预检失败，检查没有持久表；服务/扩展不匹配的具体数值另有单元负例。
4. [验收门禁](/E:/aaa-project/rag/backend/tests/conftest.py:1) 的 `--require-postgres` 要求 CPython 3.12.15、环境授权、六个必需用例全部被收集且全部通过。缺环境、筛掉用例或必需用例 skipped 都返回非零。普通测试退出 0 不代表真实 PG 验收通过。六个用例包含本文件末尾新增的 namespace 专项负例。
5. [配置](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/config.py:1) 与 [PG 适配器](/E:/aaa-project/rag/backend/src/rag_app/adapters/postgres.py:1) 只接受 `postgresql+psycopg`，使用 SecretStr、有限配置错误和 `hide_parameters=True`，关闭本适配器 SQL 日志。SQL/驱动异常和清理异常只保留为内部诊断对象，不序列化、不写普通日志。
6. [API](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/api.py:1) 接入 Settings，在 lifespan 中创建并释放 engine；`/health` 只声明 liveness，不连接数据库、不声明 ready。API 和 [worker 单次检查入口](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/worker.py:1) 共用 [bootstrap](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:1) 和 [application 检查用例](/E:/aaa-project/rag/backend/src/rag_app/application/baseline.py:1)。
7. [UoW](/E:/aaa-project/rag/backend/src/rag_app/application/uow.py:1) 的 session 创建、业务和 commit 失败均走安全边界；尽力 rollback、必尝试 close，原始失败保存在 `diagnostic_cause`，清理失败保存在 `cleanup_errors`。成功提交后的 close 失败单独报告，不声称回滚成功。仓储只拿执行接口，单元/静态检查和待执行的真实 PG 用例共同约束仓储不提交。
8. [.python-version](/E:/aaa-project/rag/backend/.python-version:1) 与 [项目声明](/E:/aaa-project/rag/backend/pyproject.toml:1) 都固定 3.12.15；CLI 和必跑 PG 模式另做精确解释器校验。3.12.8 只用于本地补充单元测试。

前端、四服务 Compose、完整 contracts 导出、provenance 台账、后续业务表、正式 vector(D)/ANN 均未实现。

## 实际运行命令与结果

工作目录均为 `E:\aaa-project\rag`。下列通过项只代表列出的测试，不代表未执行的 PG 用例。

| 命令/阶段 | 结果 |
| --- | --- |
| 首轮运行新 UoW/config/migrations/API 测试 | 4 个 collection errors：新边界尚未实现；先红后修复 |
| 首次 HTTP lifespan 测试 | 沙箱中阻塞于 Windows asyncio `_fallback_socketpair`；中断本次启动的三个测试会话，沙箱外重跑 |
| 早期临时目录检查 | 27 passed、3 errors；系统 pytest 临时目录拒绝访问，随后改用后端专用临时目录 |
| 本地最终针对性测试命令 A | **41 passed、0 failed、0 skipped、1 warning**；CPython 3.12.8 |
| 最后迁移前置条件回归命令 B | **6 passed、0 failed、0 skipped**；包含后来新增的升级前置条件用例 |
| 普通 PG 命令 C | **0 passed、0 failed、4 skipped**；两个必需环境项均未配置，未连接数据库 |
| 必跑 PG 命令 D | **退出码 4**；`ERROR: Acceptance requires CPython 3.12.15.`，未运行 PG 用例 |
| `backend/.venv/Scripts/python.exe -m compileall -q backend/src/rag_app backend/migrations backend/tests` | **退出码 0**；仅语法编译检查 |

命令 A：

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests/test_uow.py backend/tests/test_config.py backend/tests/test_migrations.py backend/tests/test_api.py backend/tests/test_architecture.py backend/tests/test_acceptance_gate.py backend/tests/test_worker.py backend/tests/test_baseline.py --basetemp backend/.test-runs/review-fixes-03 -q
```

命令 B：

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests/test_migrations.py backend/tests/test_acceptance_gate.py::test_migration_cli_config_error_does_not_leak_to_stderr -q
```

命令 C：

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests/test_postgres_integration.py -q
```

命令 D：

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests/test_postgres_integration.py --require-postgres -q
```

[门禁自测](/E:/aaa-project/rag/backend/tests/test_acceptance_gate.py:1) 使用独立子进程和明确的合成用例，临时替换解释器校验，仅测试门禁的 pass/skip/deselect 分支；这些成绩不是 Python 3.12.15 或真实 PG 证据。同文件还执行无效配置的迁移入口和真实 psycopg 连接拒绝路径，断言 stderr 无密码/正文/签名 URL 哨兵和原始 traceback；后者连接的是本机端口 1，不是一次 PG 服务验收。

[HTTP 错误用例](/E:/aaa-project/rag/backend/tests/test_api.py:1) 注入会话执行异常并经过实际 HTTP handler，断言有限 503/no-store 和 caplog/capsys 无哨兵。[真实驱动 SQL 错误用例](/E:/aaa-project/rag/backend/tests/test_postgres_integration.py:1) 尚未执行，不能记为 pass。

现存 warning 是 Starlette TestClient 对 HTTPX 的弃用提示。未为消除 warning 更换已定 HTTPX。

## 解释器和锁文件阻塞

此前真实执行：

```text
uv python install 3.12.15
error: No download found for request: cpython-3.12.15-windows-x86_64-none
```

本轮真实执行：

```text
uv lock --project backend --python E:/government/python3.12.8/python.exe --no-python-downloads
Using CPython 3.12.8 interpreter at: E:\government\python3.12.8\python.exe
error: The requested interpreter resolved to Python 3.12.8, which is incompatible with the project's Python requirement: `==3.12.15` (from `project.requires-python`)
```

后续官方工件清单旧路径查询返回 HTTP 404，官方仓库目录查询返回 GitHub API rate limit exceeded；没有取得新的目标工件。

**锁文件状态：未完成。** [现存 uv.lock](/E:/aaa-project/rag/backend/uv.lock:1) 是上一轮 39 包的旧锁，本轮没有伪造或手改锁文件。项目新增明确的 `uvicorn==0.37.0` 最小 ASGI 启动依赖，旧锁尚不包含它；目标解释器可用后必须重新 `uv lock`，再 `uv sync --locked`。当前不能声称依赖重建通过，也不能使用 frozen 安装绕过这个差异。Uvicorn 实际启动、目标版本环境中的构建均为 `not-executed`。

## 主会话准备环境后的精确入口

先提供 CPython 3.12.15、PostgreSQL 18.6、已安装的 pgvector 0.8.7，及明确允许创建/删除隔离 schema 的测试 DSN。测试账号只在指定测试库内操作；测试不负责创建/删除容器或共享扩展。不要将 DSN 输出到日志或文档。

```powershell
uv lock --project backend --python 3.12.15
uv sync --project backend --python 3.12.15 --locked
# 主会话以安全方式设置 RAG_TEST_DATABASE_URL；不在文档填写实际值。
$env:RAG_TEST_ALLOW_SCHEMA_CREATE = '1'
uv run --project backend --python 3.12.15 --locked python -m pytest backend/tests/test_postgres_integration.py --require-postgres -q
```

生产/维护连接由 `RAG_DATABASE_URL` 和 `RAG_DATABASE_SCHEMA` 提供；默认 schema 为 public，迁移前必须已存在。迁移不在请求或 worker 中自动运行。以下命令尚未在目标环境执行：

```powershell
uv run --project backend --python 3.12.15 --locked python -m rag_app migrate head
uv run --project backend --python 3.12.15 --locked python -m rag_app check-database
uv run --project backend --python 3.12.15 --locked python -m rag_app api
# 仅在经授权的回退环境执行；普通 downgrade 保留 vector 扩展。
uv run --project backend --python 3.12.15 --locked python -m rag_app migrate base --downgrade
```

## 剩余验收

- 真实 PG 迁移循环、rollback/仓储不提交、扩展保留、SQL 错误保密和版本不兼容前置条件：`not-executed`。
- 目标 Python 3.12.15、锁文件重算/同步、Uvicorn 进程启动：`not-executed`。
- commit 确认丢失时不能从异常推断事务一定未提交；本边界返回失败，不自动重试，也不宣称回滚已经证明持久结果。
- Linux、目标机、浏览器和供应方验收：`not-executed`；本轮没有取得这些环境的新证据。
- 不更新 Story 的状态或完成勾选；本文件交回主会话验收。

## 最近安全点后的继续修复

仍只修改后端与本文件，没有改动跨 Story 接力规则或状态，也没有操作 Docker。

- [夹具清理](/E:/aaa-project/rag/backend/tests/conftest.py:1) 改为独立尝试测试 engine 释放、自建 schema 删除、管理 engine 释放；某一步失败不再跳过后续步骤，原始失败与各清理失败保留在安全错误内部。
- [worker](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/worker.py:1) 保留主失败后的清理错误；[CLI](/E:/aaa-project/rag/backend/src/rag_app/__main__.py:1) 的意外异常也保留内部诊断对象。
- [PG 适配器](/E:/aaa-project/rag/backend/src/rag_app/adapters/postgres.py:1) 设置连接 5 秒、语句 10 秒、锁等待 5 秒、空闲事务 15 秒上限，限制连接和测试 schema 清理等待。真实服务端超时效果仍待 PG 环境执行，单元测试只证明装配参数。
- 新增 [资源清理测试](/E:/aaa-project/rag/backend/tests/test_resource_cleanup.py:1)，加强 [worker 测试](/E:/aaa-project/rag/backend/tests/test_worker.py:1)。新测试首轮 4 failed、1 passed，其中一个失败来自测试模拟对象不支持上下文管理器，已更正并修复实现。

本次外部检查都由 `subprocess.run(timeout=...)` 设置硬超时，命令均已结束，没有等待中的 session：

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_resource_cleanup.py','backend/tests/test_worker.py','backend/tests/test_config.py','backend/tests/test_acceptance_gate.py','--basetemp','backend/.test-runs/progress-fixes-01','-q'],timeout=45); sys.exit(result.returncode)"
```

结果：**19 passed、0 failed、0 skipped**，9.97 秒。覆盖夹具清理、连接配置、worker、安全错误和门禁子进程；CPython 3.12.8 补充证据。

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_api.py','backend/tests/test_baseline.py','-q'],timeout=25); sys.exit(result.returncode)"
```

结果：**5 passed、0 failed、0 skipped、1 warning**，0.80 秒。覆盖使用同一适配器的 API 生命周期和 baseline application 用例。

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run(['uv','python','list','--only-installed'],timeout=20); sys.exit(result.returncode)"
```

已申请 escalation 后成功读取缓存，退出码 0；清单仍只有 3.12.8、3.12.7、3.11.16，没有 3.12.15。未重复安装探测、未放宽版本、未伪造锁文件。目标解释器、锁文件重算与真实 PG 验收的阻塞仍然存在。

## 二次审查：namespace 定点修复

本节是本轮增量，没有修改规则、规格、Sprint，没有操作 Docker 或启动 agent。

- [PG 适配器](/E:/aaa-project/rag/backend/src/rag_app/adapters/postgres.py:1) 将连接搜索路径限制为 `pg_catalog`，不再把 public 或配置 schema 放入应用表回退链。仓储必须显式接收 schema，先核 namespace 存在和当前账号 USAGE，再使用 SQLAlchemy Core 的带安全引号 schema/table 对象。探针 INSERT 与版本 SELECT 均显式限定 schema，缺表会失败，不能读写旁路同名表。系统目录查询也显式使用 pg_catalog。
- [runtime](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:1) 保留配置 schema 并将它传给仓储工厂；API/worker 继续共用此装配。namespace 不可用使用新增的有限安全错误码 `DATABASE_NAMESPACE_UNAVAILABLE`。
- [迁移环境](/E:/aaa-project/rag/backend/migrations/env.py:1) 验证目标 namespace 的存在与 USAGE，并显式配置安全引用的版本表 schema。[upgrade/downgrade](/E:/aaa-project/rag/backend/migrations/versions/0001_baseline.py:1) 从该明确配置取得 schema，CREATE/DROP 都限定目标 schema。缺少明确配置即拒绝；DROP 不使用 IF EXISTS，目标缺表时安全失败，保留错误和原 revision。vector 扩展降级保留规则不变；隔离测试的 vector 类型和函数仍按查询到的实际扩展 schema 限定。
- 新增 [namespace 单元测试](/E:/aaa-project/rag/backend/tests/test_namespace.py:1)，并在 [迁移测试](/E:/aaa-project/rag/backend/tests/test_migrations.py:1) 中补实际 Alembic DROP SQL 编译断言，覆盖缺 namespace、无 USAGE、安全引号、装配传递和拒绝不明确的迁移目标。
- [真实 PG 测试](/E:/aaa-project/rag/backend/tests/test_postgres_integration.py:1) 新增 `test_real_namespace_cannot_fall_back` 和 `test_real_downgrade_missing_probe_preserves_peer`，都只使用夹具创建的随机 schema，不修改 public 或其他既有对象。前者验证目标缺失/未迁移且旁路已迁移时仓储仍失败；后者在目标版本为 head 但探针表丢失时设置危险旁路搜索路径，验证 downgrade 失败、目标 revision 不前进、旁路表及数据保留。[夹具与门禁](/E:/aaa-project/rag/backend/tests/conftest.py:1) 为旁路 schema 提供独立归属/清理，并把两个负例加入六项必跑清单。

红灯命令（60 秒硬超时）：

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_namespace.py','backend/tests/test_migrations.py','-q'],timeout=60); sys.exit(result.returncode)"
```

结果：**11 failed、4 passed、0 skipped**。失败覆盖回退路径、仓储没有 schema 参数、runtime 未传 schema、迁移 DDL 未限定目标。

首轮绿灯及相关调用方回归（HTTP 在沙箱外）：

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_namespace.py','backend/tests/test_migrations.py','backend/tests/test_baseline.py','backend/tests/test_uow.py','backend/tests/test_config.py','backend/tests/test_resource_cleanup.py','backend/tests/test_acceptance_gate.py','backend/tests/test_api.py','backend/tests/test_worker.py','--basetemp','backend/.test-runs/namespace-fix-01','-q'],timeout=60); sys.exit(result.returncode)"
```

结果：**52 passed、0 failed、0 skipped、1 条既有 TestClient warning**，10.27 秒；是 Python 3.12.8 补充单元/HTTP 证据。

最后 SQL 编译断言及 PG 用例收集检查：

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_namespace.py','backend/tests/test_migrations.py','backend/tests/test_postgres_integration.py','-q'],timeout=60); sys.exit(result.returncode)"
```

结果：**16 passed、0 failed、6 skipped**，0.96 秒。六个 skipped 均因没有测试 DSN/建 schema 显式授权，新增两个真实 PG 负例为 `not-executed`。本命令与前一命令存在重叠，不相加统计通过数。

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_postgres_integration.py','--require-postgres','-q'],timeout=60); print('require_postgres_exit='+str(result.returncode)); sys.exit(result.returncode)"
```

子进程退出码 **4**，输出 `ERROR: Acceptance requires CPython 3.12.15.`，没有将普通 skipped/退出 0 当作验收通过。本轮没有重新尝试安装解释器或修改旧锁；Python 3.12.15、旧锁重算、真实 PG 及实际服务器超时效果仍未完成。所有上述命令已经结束，没有待等待 session。

## 父 Story 1.1 A 段收尾：解释器、锁与 API 入口

本节仅记录本轮增量；没有修改父 Story 状态、任务勾选、规则、规格、Sprint 或 relay 记录，没有操作 Docker、启动其他 agent。

### 精确一致性现状

| 项目 | 实际状态 |
| --- | --- |
| [项目声明](/E:/aaa-project/rag/backend/pyproject.toml:1) | 保持 `requires-python ==3.12.15`，直接依赖保持 `uvicorn==0.37.0`，没有放宽 |
| [解释器选择](/E:/aaa-project/rag/backend/.python-version:1) | 保持 3.12.15 |
| [运行时校验](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:1) | 保持 CPython 且精确为 3.12.15 |
| 本地补充环境 | CPython 3.12.8，未安装 Uvicorn；不作为目标环境成绩 |
| [现存锁文件](/E:/aaa-project/rag/backend/uv.lock:1) | 仍是旧的 39 包、`requires-python ==3.12.*`，没有 Uvicorn；**未完成** |
| 旧锁 SHA-256 | `79c607d20f9c2308e7b7edefab73f7127e6c1efe4053ca14d9bf6ff5ba976b4f`；本轮未改动 |

本轮读取的 uv 版本是 0.12.9，已安装解释器清单仍不含 3.12.15。以下两条尝试均由外部控制器设置每条 45 秒硬超时，已经结束：

```text
uv python install 3.12.15 --install-dir backend/.test-runs/cpython-target --no-bin --no-registry --no-cache
error: No download found for request: cpython-3.12.15-windows-x86_64-none
EXIT=2

uv lock --project backend --python 3.12.15 --no-python-downloads
error: No interpreter found for Python 3.12.15 in managed installations, search path, or registry
EXIT=2
```

这只说明当前 uv 的可用工件/本地查找结果，不能据此宣称所有渠道均不存在 3.12.15。本轮没有无限探测、升级全局工具、使用其他补丁解算或手改锁文件；没有取得目标解释器，因此精确锁重算、锁同步及真实 Uvicorn 启动仍为 `not-executed`，A 段不能据此验收通过。

### API 启动依赖边界

[CLI](/E:/aaa-project/rag/backend/src/rag_app/__main__.py:1) 在精确解释器校验之后，检查已安装 Uvicorn distribution 必须为 0.37.0，然后才导入并调用其服务器。缺包、版本不符或依赖导入失败返回有限的 `STARTUP_DEPENDENCY_UNAVAILABLE`，原始异常只保留为内部诊断，不再误报为数据库错误。[错误定义](/E:/aaa-project/rag/backend/src/rag_app/contracts/errors.py:1) 没有增加原始异常/路径/秘密字段。

[新增启动测试](/E:/aaa-project/rag/backend/tests/test_startup.py:1) 覆盖：

- 项目声明、解释器选择、运行时常量的精确补丁一致，以及 Uvicorn 的直接依赖声明；
- 非目标解释器在加载服务器之前被拒绝；
- 缺包、版本不符、导入失败时的有限错误与日志/输出哨兵保密；
- 用假服务器证明 CLI 将共享 create_app 的产物交给启动入口；
- 在实际 3.12.8 子进程执行模块入口，确认拒绝，而非伪装目标启动成功。

红灯命令（30 秒硬超时）：

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_startup.py','-q'],timeout=30); sys.exit(result.returncode)"
```

结果：**5 failed、2 passed、0 skipped**，新增依赖加载边界尚不存在。

绿灯及受影响入口回归（60 秒硬超时，HTTP 在沙箱外）：

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_startup.py','backend/tests/test_api.py','backend/tests/test_acceptance_gate.py','--basetemp','backend/.test-runs/a-closeout-01','-q'],timeout=60); sys.exit(result.returncode)"
```

结果：**17 passed、0 failed、0 skipped、1 条既有 TestClient warning**，10.69 秒；仍是 CPython 3.12.8 补充证据。假服务器调用不是真实 Uvicorn 进程启动，HTTP TestClient 不代替 Uvicorn 进程验收。

另实际执行入口负例：

```powershell
& backend/.venv/Scripts/python.exe -c "import subprocess,sys; result=subprocess.run([sys.executable,'-m','rag_app','api'],timeout=10); print('api_cli_exit='+str(result.returncode)); sys.exit(result.returncode)"
```

结果：子进程退出 **2**，输出 `RUNTIME_VERSION_MISMATCH: CPython 3.12.15 is required.`，服务器没有启动。

### 真实 3.12.15 可用后的执行路径

主会话取得受信的真实 CPython 3.12.15 可执行文件后，可直接指定其绝对路径，不依赖当前旧 uv 内置的下载清单。每个安装/解算/验证命令须由调用方设置不超过 60 秒的硬超时；失败或超时即停止，不手改锁、不使用 frozen 绕过差异。

```powershell
# targetPython 必须指向真实 CPython 3.12.15；此处不填写一个虚构路径。
& $targetPython -c "import sys; assert sys.implementation.name == 'cpython' and sys.version_info[:3] == (3,12,15); print(sys.version)"
uv lock --project backend --python "$targetPython" --no-python-downloads
uv sync --project backend --python "$targetPython" --no-python-downloads --locked
```

Windows 上执行同步时，控制命令不要运行在将被 uv 替换的旧项目虚拟环境解释器中。完成同步后，用新环境检查实际解释器、distribution 和重新生成的锁：

```powershell
& backend/.venv/Scripts/python.exe -c "import sys,tomllib; from pathlib import Path; from importlib.metadata import version; assert sys.implementation.name == 'cpython' and sys.version_info[:3] == (3,12,15); assert version('uvicorn') == '0.37.0'; lock=tomllib.loads(Path('backend/uv.lock').read_text()); assert lock['requires-python'] == '==3.12.15'; assert any(p['name']=='uvicorn' and p['version']=='0.37.0' for p in lock['package']); print('EXACT_RUNTIME_AND_LOCK_OK')"
```

随后在有界的独立进程中运行 `python -m rag_app api`，检查实际进程存活、`/health` 的 liveness 响应及进程结束/资源释放，再记录 Uvicorn 进程启动证据。没有这些实际结果，不标启动通过。PG 六项必跑验收仍单独执行，本轮没有修改 schema 隔离、扩展归属、版本前置、UoW 清理或 require-postgres 门禁。

