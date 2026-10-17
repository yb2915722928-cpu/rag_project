# Story 1.1 A2a：运行入口交付记录

日期：2026-10-17（Asia/Shanghai）。

状态：本地实现与测试用例已准备，尚未执行。用户明确要求本段由主会话统一提交/推送，服务器拉取固定提交后验证；目前未收到待测提交号，不上传或覆盖 A1 活动快照。

## 修改与部署接口

- [config.py](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/config.py:1)：新增受托设置 `RAG_API_HOST` / `RAG_API_PORT`；默认 `127.0.0.1:8000`。host 只接受长度不超过 45 的合法 IP 字面量，不接受域名、URL、CIDR、端口混入或 IPv6 scope；port 严格限定整数 1–65535。错误沿既有 CONFIGURATION_INVALID，有原始私有诊断，不输出输入。
- [__main__.py](/E:/aaa-project/rag/backend/src/rag_app/__main__.py:1)：API 只创建一份 Settings，同时用于应用与 Uvicorn bind；保持精确 Python / Uvicorn 门。新增 `python -m rag_app worker`；原 check-database 与 migrate 行为保留。Uvicorn 的启动 SystemExit 转为有限安全码。
- [worker.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/worker.py:1)：新增持久空闲入口，使用现有 bootstrap 与 application 的短 DB 检查，UoW 结束后才等待。一个非阻塞 CLOEXEC self-pipe、一个 runtime、固定两个信号处理器；无业务调度、队列、额外表或供应方调用。TERM/INT 只更新退出标志，Python wakeup fd 唤醒 select，避免在信号处理器内取得线程锁；关闭 runtime、恢复原处理器和 wakeup fd、关闭两个 FD。原失败与关闭/恢复失败分别保存在 diagnostic_cause / cleanup_errors，仅 CLI 输出有限错误。
- [test_runtime_entrypoints.py](/E:/aaa-project/rag/backend/tests/test_runtime_entrypoints.py:1)：覆盖受托配置、非法输入、CLI 选择、有限启动错误、UoW 在等待前关闭、错误与清理诊断；包含真实 Linux 合成边界的 TERM/INT 子进程测试，以及需真实 PG 的事务空闲/连接清理测试。

交部署实现者的接口：

```text
API command:    python -m rag_app api
API env:        RAG_API_HOST=0.0.0.0
                RAG_API_PORT=8000
worker command: python -m rag_app worker
```

仅部署受托环境可选择 bind；不读取 HTTP Host / X-Forwarded-* 决定监听。API 绑定所有容器接口不表示允许宿主公网暴露，gateway、端口发布及 Compose 仍由部署者协调。

worker 必须连接通过现有精确版本、schema、迁移 revision 核验的 PG 才进入空闲状态。不会输出虚构 ready。一次性维护命令 check-database 仍应退出，不用于充当常驻 worker。

## 待固定提交后的验证

可用的 A1 环境与原成绩见 [A1 交付记录](/E:/aaa-project/rag/docs/story-1-1-python-3128-delivery.md:1)。真实 CPython 3.12.8 位于 `/root/.local/share/uv/python/cpython-3.12.8-linux-x86_64-gnu/bin/python3.12`；uv 0.13.1 位于 `/root/.local/bin/uv`。远程工作限于 `/opt/rag-story-1-1/backend-work`；新提交应在其独立检出目录运行，A1 的 run 目录保持原 hash。

需要主会话提供已推送的固定提交号，以及服务器获准读取私有仓库的实际认证方式。不得在日志、命令或交付文档中写 token / DSN。实现者不自行 git add、commit、push 或修改 remote。

固定提交检出、正常 `uv sync --locked --python 3.12.8` 后：

```sh
.venv/bin/python -m pytest tests/test_runtime_entrypoints.py -m 'not postgres' -ra
.venv/bin/python -m pytest -m 'not postgres' \
  --ignore=tests/test_public_contracts.py --ignore=tests/test_json_guard.py -ra
```

真实 PG 满足精确版本与 schema-create 授权后，连同父 Story 原六项执行：

```sh
.venv/bin/python -m pytest --require-postgres -ra
```

新增 PG 测试分别发 TERM / INT，使用 PGAPPNAME 区分实际 worker 连接，要求已完成 COMMIT、state=idle、xact_start=NULL；退出后有界核对连接消失。合成 runtime 的实际 Linux 信号测试只证明进程/信号/关闭路径，不代替 PG、gateway 互通或四服务通过。

当前未运行以上命令；没有把 A1 的 73 passed / 补充负例 1 passed 或旧进程成绩算作本段通过。A2a 的真实 PG、四服务与 gateway 访问也均未执行。

## 本地待提交工件

| 文件 | SHA-256 |
| --- | --- |
| [__main__.py](/E:/aaa-project/rag/backend/src/rag_app/__main__.py:1) | `2e409ae9932d9d1485c82e418e84834abcc642d6c6363bd77e47b6c17b744546` |
| [config.py](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/config.py:1) | `230dbff524437a35341948ef0c516f6fa6bcbfba57b324dd5111d20cb3596474` |
| [worker.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/worker.py:1) | `8456aac284db4b01ccb2eadcf6850f95e967bd2666bd6d7992a65cf22f9c5c28` |
| [test_runtime_entrypoints.py](/E:/aaa-project/rag/backend/tests/test_runtime_entrypoints.py:1) | `f2e1bc899df2bc610039e112dd65af68d39403b5baf5659b4a0d44e0fcf40e45` |

独立验证、全新实例审查与部署集成待主会话安排。本段不关闭父 Story 或 A2 原有 PG/迁移验收门。
