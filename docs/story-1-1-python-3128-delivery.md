# Story 1.1 A1：CPython 3.12.8 交付记录

日期：2026-10-17（Asia/Shanghai）。依据当前 A1 短规格执行；父 Story 与 A2 的验收分母保持不变。

## 范围与修改

- 项目 Python 声明、解释器选择、运行门、安全错误及测试门统一要求精确 CPython 3.12.8。
- 正常解算 uv.lock，保留原有 39 个包的版本，仅新增 Uvicorn 0.37.0 与 Click 8.5.0；没有手改锁或使用 frozen。
- 增加其他补丁版本、非 CPython、有限启动拒绝与敏感信息隔离测试；增加真实 Linux Uvicorn 子进程的健康与优雅退出测试。
- C1/C2/H 的 public.py、scalars.py、test_public_contracts.py、json_guard.py、test_json_guard.py 不属于本交付，不计为已验证。
- 不修改 API bind、worker 行为、部署资源、迁移、namespace 或 UoW 实现。历史测试结果保持原样。

## 可复用远程环境

通过 Netcatty 的现有已保存主机建立任务 terminal；get_environment 核实实际连接后使用 session `ea7998df-8be2-4b96-9103-f2871ad49376`。host_open 初始返回的临时 ID 不可用，未用它执行任何远程操作。

| 项目 | 实际位置或结果 |
| --- | --- |
| 主机 | `120.53.251.166`，Linux x86_64 |
| uv | `/root/.local/bin/uv`，0.13.1 |
| 隔离 CPython | `/root/.local/share/uv/python/cpython-3.12.8-linux-x86_64-gnu/bin/python3.12` |
| 活动项目目录 | `/opt/rag-story-1-1/backend-work/run` |
| 项目虚拟环境 | `/opt/rag-story-1-1/backend-work/run/.venv` |
| 活动日志 | `/opt/rag-story-1-1/backend-work/run/evidence` |
| 证据归档目标 | `/fileOfRag/testOfRAG/metadata/story-1-1/a1-python-3128` |
| 活动文件系统 | `/dev/vda2`，ext4；不是存储桶 |
| 存储桶 | `/fileOfRag`，cosfs / fuse.cosfs |
| 系统 Python | `/usr/bin/python3`，原有 3.12.3；未替换 |

不要复用即将关闭的任务 session ID；其他任务自行核实其可用 terminal。可以直接使用上表解释器和 uv，但应创建各自的项目虚拟环境与活动目录。

验证与归档完成后，本任务创建的 session 已成功关闭；保留的远程项目和证据目录未删除。

## 命令与当前结果

所有项目运行、构建与测试均经 Netcatty 在 Linux 执行。本地只编辑文件、计算 hash、打包与上传。

```sh
/root/.local/bin/uv python install 3.12.8
cd /opt/rag-story-1-1/backend-work/run
/root/.local/bin/uv lock --python 3.12.8
/root/.local/bin/uv sync --locked --python 3.12.8
```

- 解释器安装：已通过，真实 3.12.8。
- 正常 lock：已通过；生成的锁已通过 SFTP 回传本地。
- locked 同步：退出码 0，安装 39 个包；正常锁包含 41 个跨平台解析项。实际虚拟环境解释器返回 3.12.8，Uvicorn 返回 0.37.0。
- 非 PG 回归：真实 Linux / Python 3.12.8，73 passed、1 skipped、6 deselected。条件 skip 是只适用于非目标解释器的负例；它随后在真实系统 3.12.3 上单独运行，1 passed。skip 不计通过；六项 PG 未执行。
- 真实 Uvicorn 子进程：test_uvicorn_process.py 的健康响应、启动/关闭、有限日志测试已运行并通过。它仅证明当前 liveness/进程，不证明数据库就绪或四服务。
- 文件系统与 hash：跨进程 flock、原子替换、46/46 输入 hash 均通过；验证结束时再次核对原清单一致。
- 归档：退出码 0，完整 evidence 已保存到 `/fileOfRag/testOfRAG/metadata/story-1-1/a1-python-3128`。
- 一条依赖警告：锁定的 Starlette 提示 TestClient 使用 httpx 的兼容方式已弃用。遵守当前依赖 pin，没有为消除警告新增 httpx2。
- 两次短命令达到工具的 60 秒超时；随后改用 terminal_start。第一次长任务在下载期间主动停止，改为 `UV_NO_PROGRESS=1` 并将日志写入 evidence。没有因此改版本或更换依赖源。

## 工件与一致性

正常解算后的锁 SHA-256：`7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed`。

归档源码包 source-a1.zip SHA-256：`dffe30dda8a0f2706de23c049122d5fd201a34d6a9434be1680092779941dcf3`。它只包含 46 个既有输入及 A1 新测试，排除缓存、虚拟环境、并行 C1/C2/H 文件。

本地工件清单已上传至 evidence/local-manifest.json（本轮修改的九个文件）和 evidence/all-inputs-local.json（完整的 46 项 A1 输入）。远程真实 3.12.8 已逐项核对，46/46 hash 一致；结果保存在 evidence/all-inputs-remote.json 和 evidence/preflight.json。跨进程排他 flock 与 os.replace 检查均通过；findmnt 原始结果保存在 evidence/filesystem.log。

| 本轮文件（相对 backend） | 本地 SHA-256 |
| --- | --- |
| [pyproject.toml](/E:/aaa-project/rag/backend/pyproject.toml:1) | `1b5a7ecb3e0036e3d96a8548a4fa729c95901fcd38dfa9ed63fb7b15e6c34c1c` |
| [.python-version](/E:/aaa-project/rag/backend/.python-version:1) | `db3ef967a80f30770e652243d4e8292c73ee214e182ada70ce045e91aab40fa7` |
| [uv.lock](/E:/aaa-project/rag/backend/uv.lock:1) | `7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed` |
| [runtime.py](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:1) | `91ba02a7a87d95ac376ee2f22d99156afe0cdd4830d1b66b801be29dbb7de4a6` |
| [errors.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/errors.py:1) | `ad239632bb857f2d11dae6843784118e04d754fc4dfa045abe3370a533d6b97c` |
| [conftest.py](/E:/aaa-project/rag/backend/tests/conftest.py:1) | `33eb9c162c9475b9b88df7de41fca1e6f1fb4437779c453ef4c37a8a87e7d384` |
| [test_startup.py](/E:/aaa-project/rag/backend/tests/test_startup.py:1) | `4d46dc5b3fd215c7d376f436a768869bc6f22bbb0fafc537d62c8c5ff536e242` |
| [test_acceptance_gate.py](/E:/aaa-project/rag/backend/tests/test_acceptance_gate.py:1) | `b5dfe28f802dd533c6d905edc5f409c490f4341852a3f6c1f08bec6264d3ec65` |
| [test_uvicorn_process.py](/E:/aaa-project/rag/backend/tests/test_uvicorn_process.py:1) | `ddbb33d31c5e3648ee7275db2fd9e117348c2be719a8214ddea5a2f312b75f24` |

源探测使用锁内 Pygments 官方 URL：64 KiB Range 请求返回 HTTP 206；完整请求返回 HTTP 200，但在 30 秒读到 604,037 字节后 curl 以 28 退出。原始 headers、URL 与输出保存在 evidence/source-probe-*、evidence/source-full*，不将不完整文件作为可安装工件。低并发正常同步使用 `UV_CONCURRENT_DOWNLOADS=2`，先前日志保留为 evidence/sync-attempt-high-concurrency.log。

本轮后续运输方式由用户调整为主会话统一 Git 提交/推送、服务器拉取固定提交。此次先完成已经上传的同一 hash 工件验证；不为运输方式变更重跑。本实现者不执行 git add、commit 或 remote 变更。原 NO_VCS 是启动时历史基线，不改写。

## 验证命令与证据索引

活动目录中执行以下命令；原脚本及原始日志均已归档。

```sh
.venv/bin/python -m pytest -m 'not postgres' \
  --ignore=tests/test_public_contracts.py --ignore=tests/test_json_guard.py \
  --junitxml=evidence/non-pg.xml -ra
PYTHONPATH="$PWD/src:$PWD/.venv/lib/python3.12/site-packages" \
  /usr/bin/python3 -m pytest \
  tests/test_startup.py::test_actual_cli_rejects_non_target_runtime \
  --junitxml=evidence/non-target.xml -ra
```

归档目录内：

- lock.log、sync.log：正常解算与 locked 安装的原始结果。
- runtime.log、verification-status.json：实际解释器、Uvicorn、uv 与命令退出码。
- non-pg.log / non-pg.xml、non-target.log / non-target.xml：开发者回归及真实错误解释器负例。
- preflight.json、filesystem.log、all-inputs-local.json / all-inputs-remote.json、local-manifest.json：文件系统语义及本地/远程逐项 hash。
- source-a1.zip、original-uv.lock、verify-a1.sh 与 source 探测原包：原始快照、旧锁、验证命令及网络证据。

用户随后授权在本地开始 A2a 运行入口实现。A1 的活动快照未更新；本记录及归档的 46 项清单仅绑定 A1 原快照。后续本地 CLI/config/worker 改动不自动继承这些成绩，应绑定主会话统一发布的 Git 固定提交另行验证。

## 未纳入本段验收

真实 PostgreSQL 18.6 / pgvector 0.8.7 六项、迁移循环与依赖数据库的进程门留 A2；未执行不计通过。完整四服务生命周期、可信 bind、持久 worker、并行公共契约与 H/HTTP 由主会话依赖协调。独立验证与全新实例审查由主会话后续安排，本开发者记录不能替代。
