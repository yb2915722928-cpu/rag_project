# Story 1.1 A2a worker 临时改动归位：交付记录

日期：2026-10-17（Asia/Shanghai）。

规格：[spec-1-1-worker-reconcile.md](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-worker-reconcile.md:1)。
基线 commit：`a52ae3090948e7eeea6df87590f15ce35351d247`。

状态：源码与测试准备完成；Linux 精确 CPython 3.12.8 运行证据 `not-executed`，本段不关闭父 Story、A2a 其余门或任何 PG/四服务门。

## 判断结论

主会话本轮误加的 `_make_wakeup_pipe()` 是 Windows 兼容 fallback：`os.pipe2` 缺失时退回 `os.pipe()` + `os.set_blocking()`。该 fallback 改变不了以下事实：

- 原实现的目标平台只有 Linux，`os.pipe2(O_NONBLOCK | O_CLOEXEC)` 在 CPython 3.12.8 / Linux 上可用，原逻辑没有产品缺陷。
- `os.pipe()` + `set_blocking()` 与 `os.pipe2()` 的差异不在 fd 可继承性：`os.pipe()` 自 Python 3.4 起默认返回 non-inheritable 描述符。撤销理由是目标平台与信号/等待机制：worker 的 `select` 等待、`signal.set_wakeup_fd` 写端唤醒和 SIGTERM/SIGINT 语义只在 Linux 目标上成立，Windows 兼容性从未验证，mock 通过不等于真实 Windows 进程可用。
- 若保留 fallback，等于在未获授权的情况下扩大平台支持面，并让测试用非目标平台行为替代 Linux 语义。

因此选择最小修正：**撤销该 fallback**，恢复 `os.pipe2` 唯一路径，不新增任何 Windows 运行支持、业务调度、队列或外部调用。

## 实际修改

### 1. [worker.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/worker.py:1)

删除 `_make_wakeup_pipe()`，恢复第 50 行 `pipe = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)`。

该文件与基线 commit 内容完全一致，`git diff` 净变化为 0：

| 文件 | SHA-256 |
| --- | --- |
| [worker.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/worker.py:1) | `8456aac284db4b01ccb2eadcf6850f95e967bd2666bd6d7992a65cf22f9c5c28` |

该 hash 与 [A2a 交付记录](/E:/aaa-project/rag/docs/story-1-1-runtime-delivery.md:1)登记的 worker.py 完全一致，可佐证本轮误加的行已被完整撤销、交付工件回到 A2a 原样。

保留的既有语义（未改动）：

- self-pipe 以 `O_NONBLOCK | O_CLOEXEC` 原子创建，作为 `signal.set_wakeup_fd` 的写端；信号处理器只翻转 `stopping` 标志，不取锁、不做 IO。
- `runtime.check_database()` 的短 UoW 在 `select` 等待之前结束；空闲期间无 Session、无事务。
- `finally` 依次释放 runtime（dispose engine）、恢复原 wakeup fd、恢复 SIGTERM/SIGINT 原 handler、关闭两个描述符；每步失败都独立记录，不因前一步失败而跳过后续清理。
- build/check 失败时保留主 `SafeError`；非 `SafeError` 的主异常包装为 `DATABASE_OPERATION_FAILED` 并保留原始 `diagnostic_cause`；清理失败进入 `cleanup_errors`；仅当没有主失败时才升级为 `DATABASE_CLEANUP_FAILED`。CLI 只打印 `code: message`，不输出诊断对象或输入。

### 2. [test_runtime_entrypoints.py](/E:/aaa-project/rag/backend/tests/test_runtime_entrypoints.py:1)

净新增 51 行，未删除或改写既有断言：

| 变更 | 位置 | 目的 |
| --- | --- | --- |
| 新增 `requires_linux_self_pipe` 标记 | 第 126–129 行 | worker 生命周期用例只在 Linux 执行；非目标平台显式 skip，不把平台缺失转成"业务失败"或"通过" |
| 标记 `test_worker_closes_short_uow_before_idle_and_restores_handlers` | 第 132 行 | 同上 |
| `create_pipe` 断言 flags 为 `os.O_NONBLOCK \| os.O_CLOEXEC` | 第 139 行 | 防止 flag 被静默削弱（原子性与非阻塞语义） |
| 新增 wakeup fd 恢复断言 | 第 168–171 行 | 首调写端 + `warn_on_full_buffer=False`；末调恢复为 `-1` |
| 标记参数化 `test_worker_preserves_private_failure_and_cleanup` | 第 177 行 | 同平台约束 |
| 新增 `test_worker_keeps_cleanup_failure_private_and_releases_resources` | 第 224–258 行 | 覆盖 wakeup fd 恢复失败：`DATABASE_CLEANUP_FAILED` + 私密 cause，engine 仍关闭，handler 仍恢复，两个描述符仍关闭 |
| 标记参数化 `test_real_worker_cli_failure_is_private` | 第 274 行 | 真实 worker CLI 负例依赖 Linux self-pipe 路径 |

测试文件 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| [test_runtime_entrypoints.py](/E:/aaa-project/rag/backend/tests/test_runtime_entrypoints.py:1) | `c98906113e1fc581bb6920366bbe71228d9ce7f9d3efd20cbce1ec0fbd8e5864` |

未改动：CLI、公共模型、其他测试、锁、部署、主控台账、`docs/story-1-1-runtime-delivery.md`。

## 逐项状态

| 规格验收项 | 状态 | 依据 |
| --- | --- | --- |
| 判断原 Linux self-pipe / signal wakeup / 有限关闭语义，选择最小修正，不以 Windows 缺 `pipe2` 判定 Linux 缺陷 | `source-prepared` | fallback 已撤销；`worker.py` 与基线零差异；不存在以 mock 宣称 Windows 可用的路径 |
| Given Linux 3.12.8，worker 空闲与 SIGTERM/SIGINT：事务已结束、持久空闲、有限退出，恢复 handler/wakeup fd、关闭描述符与 engine | `not-executed` | 用例已就绪（既有 Linux 子进程用例 + 新增 wakeup fd 断言），需固定 commit 在 Linux 3.12.8 运行 |
| Given build/check/close 等错误，保留主 SafeError、私密 cause 与 cleanup errors，CLI 只输出有限消息 | `not-executed`（源码已具备，新增 cleanup 失败用例） | 既有 `test_worker_preserves_private_failure_and_cleanup` 覆盖 build/check/check-raw/close；新增用例覆盖 wakeup fd 恢复失败；均待 Linux 运行 |
| 维护可审阅测试变化与交付记录 | `done` | 本文档；`git diff` 可审阅 |
| 仅 Netcatty Linux 运行测试；无相同可取的 GitHub/Gitee commit 时只做源码准备并记录 `not-executed` | `done` | 未本地运行、未提交、未推送、未重试认证/SFTP/镜像 |

## 未运行及原因

未执行任何应用运行、构建或测试。原因按规格与 [AGENTS.md](/E:/aaa-project/rag/AGENTS.md:1)：

1. 运行/测试只允许在 Netcatty 连接的 Linux 主机、精确 CPython 3.12.8 环境执行；本机 Windows 结果不作为证据。
2. 服务器只从 Gitee 拉取固定提交并核对 commit 与源码 hash。当前 GitHub 为空、Gitee `ls-remote` 无 refs（见 [工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md:1)），没有可拉取的对应 commit。
3. 规格明确要求本轮不提交、不推送、不重试认证/SFTP/镜像。

因此本段的 hash 只是本地工作副本 hash，不能标为任何远端 commit 通过。

唯一在本地执行的检查是 `ast.parse()` 静态语法解析（读取两个文件的文本，不导入 `rag_app`、不执行测试、不启动流程），结果 `SYNTAX_OK`。它只能排除语法错误，不构成任何运行或平台证据。

旧 Windows `466 passed / 13 skipped` 仅作补充观测，与本段无关，不构成 Linux 或 PG 证据。

## 固定提交后所需执行

主会话完成 GitHub/Gitee 同一 commit 同步并提供 commit 号后，服务器在独立检出目录核对 commit 与上表 hash，执行：

```sh
uv sync --locked --python 3.12.8
.venv/bin/python -m pytest tests/test_runtime_entrypoints.py -m 'not postgres' -ra
.venv/bin/python -m pytest -m 'not postgres' \
  --ignore=tests/test_public_contracts.py --ignore=tests/test_json_guard.py -ra
```

真实 PG 与本 Story 原六项门、四服务生命周期另行按 A2a 规格执行：

```sh
.venv/bin/python -m pytest --require-postgres -ra
```

新增/加固用例在 Linux 上的预期：`test_worker_closes_short_uow_before_idle_and_restores_handlers` 断言 UoW 先提交关闭、wakeup fd 先设后恢、两个描述符关闭；新用例断言 wakeup 恢复失败时仍完成 engine/handler/FD 清理并只暴露有限错误码。

## 风险与边界

- `not-executed`：全部 Linux 与 PG 证据缺失，父 Story、A2a 其余门、四服务门均未通过。
- 非目标平台：`os.pipe2` 在 Windows 不存在，`python -m rag_app worker` 会以有限错误退出（CLI 捕获 `Exception` 并输出 `DATABASE_OPERATION_FAILED`），不会 traceback；这是非目标平台的已知行为，不是新增支持，也不作为验收对象。
- `requires_linux_self_pipe` 使相关用例在非 Linux 上 skip；该 skip 不能计入任何通过分母，Linux 未跑完即保持未通过。
- 新增测试断言未在目标环境执行，存在语法或平台行为未验证风险，需由固定提交后的 Linux 运行消除。
- 若 Linux 运行暴露 wakeup fd 或清理顺序问题，按规格交回实现者修复，不在本段扩大修改范围。
