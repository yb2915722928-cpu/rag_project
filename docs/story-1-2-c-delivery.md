# Story 1.2 C：单 call 监督与集成交付说明

日期：2026-10-18（Asia/Shanghai）。
范围：C 分段的 Linux child/IPC 监督、物理槽持久占用与一次 grant；父 Story 的端到端调用集成、独立验证与正式审查不由本文件签署。

## 依据与文件归属

实现前已完整读取 [C 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-c-supervision.md:1) 及其指向的
[公共契约](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-public-contracts.md:1)、
[原 Story 1.2 AC2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197)、
[R1/R2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:5)
与 [实施契约 §2.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:86)。

C 最终唯一写入：

- [监督领域值/IPC](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/supervision.py:1)
- [Linux 监督适配器](/E:/aaa-project/rag/backend/src/rag_app/adapters/child_supervisor.py:1)
- [child 入口](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/call_child.py:1)
- [专题测试](/E:/aaa-project/rag/backend/tests/test_child_supervisor.py:1)
- [本交付记录](/E:/aaa-project/rag/docs/story-1-2-c-delivery.md:1)

文件归属调整后，`application/call_dispatch.py`、`tests/test_call_dispatch.py`、
`tests/test_call_dispatch_postgres.py` 已按 [spec-1-2-e-dispatch-integration.md](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-e-dispatch-integration.md:1)
转交 A/E；C 未再写入这三件。原 draft SHA `aee1099e9c401d7d408f3177d1e56bfdddb5115c8c30acd9ea13ac8dbe8f41a2` 作为未冻结草稿来源保留。
未修改 A/B 的源文件、依赖锁、共享错误文件或迁移。

## 实现模型证据

父会话已核本轮实际 `turn_context` 为 `2026-10-17T19:30:12Z zayuapi/deepseek-v4.1-flash / max`，未传推理覆盖；
本记录只保留路由记录，不宣称底层供应方身份，也不以历史会话自述替代运行证据。

## 已交付行为

### 监督边界

- `ChildLimits` 对帧、结果、stdout/stderr 与启动/TERM/KILL 等待给固定上界；
  `ChildSlot`、`ChildIdentity` 记录 deployment/boot/slot/attempt、child 启动实例、
  pid、进程组与 Linux `start_ticks`，不以可复用 PID 判断身份。
- `spawn` 使用参数数组、`shell=False`、`start_new_session=True`、`close_fds=True`、
  `pass_fds` 与显式环境 allowlist，不使用 `preexec_fn`；child 仅接收私有
  socketpair fd，argv 只有 `--ipc-fd`。
- IPC 为长度前缀有界帧；command、grant、result 各自单次发送。command 只含单阶段
  与有界 payload，不含 grant/秘密；child 不自主进入下一阶段。
- `SendGrant` 携带 controller 已解析并固定 IP 的 `EgressPlan` 与 `EgressRequest`，
  child 消费该 plan，不二次 DNS；`plan`/`request`/`grant_id` 均不出现在 `repr`。
- grant 写入之前的失败保持 `not_sent`；grant 写入之后（含部分写）的任何失败、EOF、
  超时或子进程退出都保守为 `may_have_sent`，保留 `grant_id`，不按 child 自述降回
  `not_sent`，也不补零成本。
- 重复 grant 返回 `GRANT_REUSED`；call/attempt/boot/child_instance 错绑返回
  `IDENTITY_MISMATCH`，均在写入 socket 前拒绝。
- 四个能力阶段 `model`/`parse`/`embedding`/`vision` 与 `egress` 均为显式本地假件；
  egress 假件只读取已核 plan/request 并回传摘要，不建立网络连接。

### 物理槽占用与停止证明

- 物理槽键为 `deployment_id + slot_id`，boot 不参与占用判定；新 boot 或新
  supervisor 实例不能绕过仍存活或停止未证的旧 child。
- `LinuxChildSupervisor` 必须显式传入绝对 `state_root`；清单位于
  `<state_root>/slots/<sha256(deployment+slot)>.json`，以同目录 `fcntl.flock`
  互斥，临时文件 fsync 后原子 `os.replace`。`state_root` 必须位于支持 flock 与
  原子 rename 的本地文件系统；桶/NFS/SMB 挂载不适用，且没有内存回退。
- `spawn` 在 Popen 前持久化 `starting` 认领，Popen 后立即持久化 pid；取得
  `start_ticks`/进程组后再次持久化。只观察不到身份时不发任何信号，认领保持不可
  释放；只有经核实停止才写 `released`，否则写 `blocked` 并跨实例持续阻断。
- `/proc` 不可读或不可核实一律视为 `unknown`：不再等价于“无进程/无后代”，
  也不作为空集证明。`StopProof.proven` 需同时满足 child 退出、进程组为空、
  后代缺失、IPC/发送 FD 关闭与 grant 销毁；缺一即 `STOP_UNPROVEN`。
- 信号只经 `_signal_verified`：仅当登记 pid 的 `start_ticks` 与进程组同时匹配
  身份时才 `killpg`；错绑/失联身份不接收任何信号，也不误杀复用 PID。
- `stop` 先关闭父端 IPC/grant 写端，再在 PG 事务外执行 TERM→有界等待→KILL→
  有界等待；超时或证明不完整时槽继续阻断。
- `inspect` 只返回已登记 handle 或最终证明；外部身份不推断退出，也不以远端
  controller 的观察替代本地 FD/IPC/grant 证明。

### IPC 绝对期限

- `read_frame`/`write_frame` 的截止时间是绝对单调时钟。`_recv_exact` 在每次
  `recv`（含 `InterruptedError` 重试）前重新计算剩余时间，持续小块输入不能重置
  相对 socket timeout；`write_frame` 同样按剩余期限分段 `send`，避免 `sendall`
  内部相对超时叠加。

## 首版草稿与修正后的受测版本

### 初次四文件草稿（未运行，仅来源保留）

| 文件 | SHA-256 |
| --- | --- |
| `modules/execution/supervision.py` | `58bdf7cd17a3f2522335fec0de63c61af7a850d0f838b41e24f24152764d05a0` |
| `adapters/child_supervisor.py` | `8a7611c3d89fb54eb688439c8838cbc7e19a9966db0039a2382900306e861015` |
| `entrypoints/call_child.py` | `522a673d90899fad5e31d351c7b3a0a8bd1e84a3987934e9902eeb98c339f89a` |
| `tests/test_child_supervisor.py` | `5e5ff252eae3eeaa1de569a8a48ea718aceb2eb38f598160528c679d9f508f70` |

该版本未在 Linux 运行。主控完整检查后指出两项原 AC2/R1 缺口，C 重开同四文件
最小修正：

- I2：物理槽仅内存且按 boot 分离，新 supervisor/新 boot 可绕开旧占用；
  停止证明把不可核实的 `/proc` 当成空集，且可能对错绑身份发信号。
- I3：`_recv_exact` 未按绝对期限重算剩余时间，持续小块 `recv` 可延长阶段。

修正未改变公开 `ChildSupervisor` 方法，也未新增 1.3 限流/1.4 资产范围。

### 修正后的草稿（尚未发布测试）

| 文件 | SHA-256 |
| --- | --- |
| `modules/execution/supervision.py` | `c3de6c829265f34305927b120bb66838644613af2640d147709c5bf0027c569a` |
| `adapters/child_supervisor.py` | `c647ecd9da5d94f9a3f9bd658c490d1adb9e20ad6fecc64f42b3b8ab86851d10` |
| `entrypoints/call_child.py` | `522a673d90899fad5e31d351c7b3a0a8bd1e84a3987934e9902eeb98c339f89a` |
| `tests/test_child_supervisor.py` | `392081b4fa772559a1e2456581c4c6778e90da890f8ff2c67f752cdaa6551c5a` |

主控复核发现 I3 用例的数据不足以区分旧实现：dribble 从帧第 0 字节开始每 0.12s
发送一个字节，4 字节 header 约 0.36s 完成，旧实现也会在 header 后发现 0.35s
期限已过；断言 `elapsed < 1.0` 仍会通过。C 仅改该用例：先一次
`sendall(frame[:4])`，再逐字节慢发正文 `frame[4:]`，保持原 deadline、`TIMEOUT`
断言、`elapsed < 1.0` 与有界关闭。此改动只影响测试数据，不触及 native 实现。

## 固定提交与环境

- 发布提交：`96c64fbab0fa8d3d824f2e592196c02570550c70`
  （`feat: supervise bounded child calls and wire shared epoch config`）。
- 服务器：`/opt/rag-story-1-2/repo-fixed`，origin 仅 Gitee
  `https://gitee.com/QAQsdsdsdsds/rag_project.git`；`git fetch` 后
  `git checkout --detach 96c64fbab0fa8d3d824f2e592196c02570550c70`。
- 测试前后 HEAD 均为该提交，`git status --porcelain` 为空；未从 GitHub 拉取，
  未使用旧 repo 或 `venv-dev`。
- 解释器 `/opt/rag-story-1-2/venv-fixed/bin/python`：CPython `3.12.8`；
  pytest `8.4.2`、pluggy `1.7.0`，插件 `cov-7.0.0`、`anyio-4.15.1`。
- 锁文件 `backend/uv.lock`：`7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed`。
- JUnit 记录的测试主机名为 `VM-0-16-ubuntu`；完整 uname 与 pip freeze 见
  `environment.txt`。

提交内 [story-1-2-cd-source-snapshot.json](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-cd-source-snapshot.json:1)
记录六个 canonical 文件；测试前逐一核对，0 mismatch：

| 归属 | 文件 | SHA-256（96c64fb 受测） |
| --- | --- | --- |
| C | `modules/execution/supervision.py` | `c3de6c829265f34305927b120bb66838644613af2640d147709c5bf0027c569a` |
| C | `adapters/child_supervisor.py` | `c647ecd9da5d94f9a3f9bd658c490d1adb9e20ad6fecc64f42b3b8ab86851d10` |
| C | `entrypoints/call_child.py` | `522a673d90899fad5e31d351c7b3a0a8bd1e84a3987934e9902eeb98c339f89a` |
| C | `tests/test_child_supervisor.py` | `95480b94297031367e921ee5a3d00c238a3bc31f37d906a24f64e22b89de94e4` |
| D | `deploy/compose.yaml` | `c05e4594a939432e87bba40dd57307d89e185176ecfa852da82efc2e168f77db` |
| D | `docs/story-1-2-epoch-deploy.md` | `26e7a07db095ccb712356cd98e6802f8f331a43a6ad23bffb9962c6263169377` |

测试后再核 HEAD、Git 洁净与上述六 hash，均未变化。

## 执行命令与结果

```bash
cd /opt/rag-story-1-2/repo-fixed/backend
PYTHONPATH=/opt/rag-story-1-2/repo-fixed/backend/src \
  /opt/rag-story-1-2/venv-fixed/bin/python -m pytest \
  tests/test_child_supervisor.py tests/test_architecture.py \
  -vv -rs --junitxml=/opt/rag-story-1-2/evidence/C-child-96c64fb/junit.xml
```

结果：退出码 `0`，`25 passed in 5.26s`；JUnit
`tests=25`、`failures=0`、`errors=0`、`skipped=0`。主控复核确认 C 的 JUnit
为 child 22 项 + architecture 3 项，无 `skip`。

### 通过的案例

`tests/test_child_supervisor.py`（22 项，真实 Linux 进程与本地目录）：

- 有界帧：超长、截断、额外字节拒绝；grant/result 线格式往返且 `repr` 不含秘密。
- child 源码静态边界：不导入 DB、bootstrap、application、供应方适配器。
- 四个显式假件阶段 `model`/`parse`/`embedding`/`vision`：单阶段执行、结果摘要、
  正常停止；egress 假件消费已解析 plan，不二次 DNS。
- 单 grant：第二次 grant 返回 `GRANT_REUSED`；boot/child_instance 错绑返回
  `IDENTITY_MISMATCH`，不写入 child。
- prepared 后无 grant：超时为 `not_sent`；grant 后 child 被杀：保守
  `may_have_sent`，保留 `grant_id`、状态与响应不归零。
- 跨 supervisor 同物理 slot：旧 child 活着时拒绝；换新 boot 仍拒绝；旧 child
  死亡但未经所有者证明时仍拒绝。
- 模拟 controller 崩溃留下的 `starting` 认领：新实例拒绝复用该 slot。
- 未证明停止持久化：跨 supervisor 实例仍阻断同一物理 slot。
- `/proc` 未知负例：不作为空进程组/空后代证明，保持 `STOP_UNPROVEN`。
- 身份错绑：不调用任何信号，返回未证明。
- 秘密边界：DB DSN、主密钥、秘密哨兵不进入 child argv/env/stdout/stderr。
- 取得完整停止证明后同一 slot 可再次 spawn；`start_ticks` 不匹配的伪造身份
  不能复用现有 child。
- 慢速分段正文：header 一次送达、正文逐字节慢发，仍在原绝对 deadline 内以
  `TIMEOUT` 有界退出（`elapsed < 1.0`）。

`tests/test_architecture.py`（3 项）：八模块边界存在、领域模块不导入框架/ORM、
application 不依赖框架且仓储不自行提交。

仅运行主控指定的两个文件；未执行 PG、迁移、四服务、dispatch 集成或全仓套件，
不把本结果扩展为父 Story 或全仓基线通过。

## 证据与归档

原始证据目录 `/opt/rag-story-1-2/evidence/C-child-96c64fb`，已复制归档到
`/fileOfRag/testOfRAG/metadata/story-1-2/C-child-96c64fb`；两份目录逐字节
`cmp` 一致：

| 文件 | SHA-256 |
| --- | --- |
| `junit.xml` | `006ec1258428d614f9bcec0d557ea71fc42af99af2f070da96609ad679907fe5` |
| `raw.log` | `8b493608d5be0a6b8ad9a213a60f9b7bb99c29ec227458f9b984cceb7fd72b95` |
| `environment.txt` | `1001de4cd08087cac367bcc91fe3c928001260a1856046d76aad28403256e2b9` |
| `result-summary.txt` | `0fd7d67ad411dcb359211a89b05b9548d45efec1f981198244dfe9997d13189b` |

`environment.txt` 记录提交、Git 状态、uname、解释器/pytest 版本与 pip freeze；
`result-summary.txt` 记录 HEAD、干净工作树、退出码、通过统计与上述证据 hash。
`raw.log` 含完整 `-vv -rs` 输出和 `pytest_exit=0`。

## 假件与网络边界

本专题的模型、解析、embedding、图意与 egress 全部为显式本地假件；egress 假件
只读取 controller 已核的 `EgressPlan`/`EgressRequest` 并回传摘要，没有 DNS、
TLS、HTTP 或任何真实外发。测试进程只启动本地 `call_child` 子进程并使用
socketpair 与本地 state 目录。

## 未完成与风险

- 父 Story 的 `CallDispatch` 端到端、真实 PG 故障矩阵、独立 Step 5 验证与
  全新 `GPT-6.1 Sol / medium` 审查未由本记录完成；三份 dispatch 文件已按
  E 规格转交 A/E。
- `state_root` 的 flock/原子 rename 已在 Linux 本地目录实测；tmpfs 上仅容忍
  目录 fsync 拒绝，仍依赖本地文件系统语义，不能外推到桶/NFS/SMB。
- 停止证明依赖 `/proc` 与进程组观察；不可核实时的保守阻断需在真实部署中
  按运维流程显式核对，不自动释放槽。
- 本专题未验证真实供应方、真实 DNS/TLS、真实限流或目标部署；这些属于后续
  Story 与父 Story 的门，不在 C 分段放行。
- 本文件仅补交付记录，不新增检查；四份 native 源与测试继续保持
  `96c64fbab0fa8d3d824f2e592196c02570550c70` 的冻结内容。
