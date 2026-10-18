# Story 1.2 E：调用集成交付说明

日期：2026-10-18（Asia/Shanghai）。
状态：**E 开发者门与 E 相关正式增量审查在固定提交 `d6e8a0da94a88199e6c4795f3e10e26c821b454f` 通过；父 Story 未完成。**
本文只记录 E 分段真实运行/审查证据，不替代独立验证或 D 部署门。

## 范围与文件归属

唯一写入范围为以下三源与本交付文档：

- [call_dispatch.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:1)：单 call 集成 A 的持久生命周期、B 的已核 plan 与 C 的真实 Linux child。
- [test_call_dispatch.py](/E:/aaa-project/rag/backend/tests/test_call_dispatch.py:1)：应用层单 call、崩溃/超时、purpose 分层、事实与秘密边界。
- [test_call_dispatch_postgres.py](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:1)：真实 PostgreSQL 与真实 Linux child 的端到端及故障矩阵。
- [本交付记录](/E:/aaa-project/rag/docs/story-1-2-dispatch-delivery.md:1)；它是运行后的补写文档，不含在 `d6e8a0d` 中。

未修改 A 的 19 源、B 的 egress 四件、C 的四 native 源、D 的部署两文件或迁移/共享错误模型。

## 集成行为

| 节点 | 预期输入 | 实际行为与副作用 |
| --- | --- | --- |
| A `prepare` | 当前持久 context/fence、逻辑 `purpose`、请求摘要 | 在短 UoW 内只插入一条 `prepared` call；不使用旧 fence 或调用者延长的期限 |
| child 启动 | 指定 `ChildSlot`、明确绝对 `state_root` | 真实 Linux child 以私有 socketpair 接收单个阶段；启动/prepare 失败不取得 grant |
| A `mark_may_have_sent` | prepared call、当前 context、boot/child 身份 | 在短 UoW 内原子转换一次并返回唯一 `CallGrant`；旧 attempt/token/epoch 或重复标记返回零 grant |
| C `SendGrant` | A 的 grant 身份、已核 B plan/request、stop-by | 每个 child 只消费一次；grant 写入后任何失败/EOF/超时保守为 `may_have_sent` |
| 接收完成 | child 的单次结果 | 必须先取得真实停止证明（退出、进程组空、无后代、IPC/FD 关闭、grant 销毁），之后才提交业务结果或 unknown |
| 业务结果 | 可信 `ResultFact` | 仅在当前权威仍有效时终结为 responded/known_failure，并追加事实；提交失败则先 unknown，再按 call-only 追加可信迟到事实 |
| unknown | may-have-sent call | 持久 `state=unknown`、`usage_status=unknown`、provider/usage/cost 全 NULL；不伪造零值 |
| 迟到事实 | 可信 provider ref/usage/cost | 只锁 call；重复幂等、冲突保留双方并要求 reconciliation，不恢复原业务、次数、会话或许可 |
| 拒绝与假件 | 未核 target、下载 Authorization、四类能力 | 目标/凭据错配在 DNS/派发前拒绝；model/parse/embedding/vision 只走显式本地假件，无供应方外发 |
| 等待 | child prepare/receive/stop | DNS、IPC、进程等待与 TERM/KILL 均在 PG 事务外；接收期间无 `idle in transaction` |

业务 `purpose` 与 B 的传输/凭据 `purpose` 是两个独立字段：前者原样交给 A，并由持久 context 的 scope 校验；后者独立决定 api/upload/download 与 Authorization 守卫。合法 `query` 或 `embedding` 业务用途可以与 `api` 传输用途共存；业务用途不匹配仍由 A 的真实持久 context 拒绝。

## 首轮真实失败与修复

### `f3f1caacc76cd9cf8bc72a8eba1fcd9bc246c36c`（失败，保留）

- PG 命令实际选择 28 项、750 deselected：16 passed、12 failed，退出码 1。
- 12 项失败均在测试假件构造 `EgressTarget` 时触发 `CONFIGURATION_INVALID:request_target_invalid`：测试 `SECRET` 含原始 `{}`，直接拼入签名 query，被 B 正确的可见 ASCII URI 守卫拒绝。
- 线程等待用例的 `entered.wait` 失败是该构造异常的次生结果；不是 E 调用逻辑或等待事务失败。
- 同提交 `tests/test_call_dispatch.py` 单独运行 20 passed、退出码 0。该结果不能覆盖 PG 矩阵失败。
- 未放松 B 守卫，未修改 A/C 源；只修正测试假件的 URI 编码。

### `d6e8a0da94a88199e6c4795f3e10e26c821b454f`（E 开发者门）

修复仅涉及两个测试文件：

- unit 的签名 target 使用 `quote(SECRET, safe="")`；
- PG 的 API 签名 target 使用同一编码；
- PG 下载错配用例的 `sig=` 同步编码；
- `SECRET` 隐私/repr 断言保留，B 的 URI/Authorization 校验未改；
- [call_dispatch.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:1) 与 `f3f1caa` 字节一致。

最终源 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| `call_dispatch.py` | `ae8f70488275cec3a88e96ba0e9eea883e8a3d783a2186001925a08045bdb848` |
| `test_call_dispatch.py` | `1595bf6b9aba9b877ee8a4135b3006163226af3818752fbc21fd34b3a1de2450` |
| `test_call_dispatch_postgres.py` | `bdc14b9117d4fbf194315463aa8c878f53ad41145dfe516fd49567e12606cb82` |

`backend/uv.lock` 保持 `7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed`。

## 固定提交与真实运行结果

提交：`d6e8a0da94a88199e6c4795f3e10e26c821b454f`，GitHub/Gitee 同一 main 实核；服务器仅从 Gitee fetch 后 `checkout --detach`，未覆盖源码。测试前后 Git 均为该提交且 `git status` 干净；三源与 lock hash 一致。

本文是在该提交运行完成之后由 E 补写的文档，不包含在 `d6e8a0d` 中；后续若仅发布本文档，三源仍与 `d6e8a0d` 相同，不改变上述已固定提交的运行结果。

环境：Linux，`/opt/rag-story-1-2/venv-fixed` 精确 CPython 3.12.8，Uvicorn 0.37.0；`uv sync --locked` 退出码 0（索引中的 `sync.exit` 与 `sync.log` hash 已由主控直接核读）。

### E 专题

```bash
/opt/rag-story-1-2/venv-fixed/bin/python -m pytest \
  tests/test_call_dispatch.py -q -p no:cacheprovider \
  --junitxml=/opt/rag-story-1-2/evidence/E-f3f1caa/unit.xml
```

`f3f1caa` 上先得 20 passed、退出码 0；`d6e8a0d` 未单独重跑该文件，其内容已包含在下述六模块非 PG 回归中并通过。

### 全部必需 PostgreSQL 选集

```bash
/opt/rag-story-1-2/venv-fixed/bin/python -m pytest \
  --require-postgres -m postgres -q -p no:cacheprovider \
  --junitxml=/opt/rag-story-1-2/evidence/E-d6e8a0d/pg.xml
```

`d6e8a0d` 结果：28 tests、0 failures、0 errors、0 skipped，退出码 0。构成为 E 的 13 个真实 PG/child 用例、A 的 7 个 call PG 用例（6 个必需门 + 1 个锁序回归）、6 个迁移/仓储必需门和 2 个 Linux runtime worker PG 用例；conftest 的 12 个 `--require-postgres` 必需节点全部 selected/passed，0 skipped。13 个 E 节点为：end-to-end 单 grant/unknown、终结与换 attempt、旧 epoch、wrong/valid business purpose、prepare 崩溃、grant 投递崩溃、响应超时、SIGSTOP/KILL、可信晚到事实、迟到冲突不复活、四类能力假件、下载凭据拒绝、等待不占事务。

### E 非 PG 专题与受影响回归

```bash
/opt/rag-story-1-2/venv-fixed/bin/python -m pytest \
  tests/test_call_dispatch.py tests/test_child_supervisor.py \
  tests/test_call_persistence.py tests/test_egress.py \
  tests/test_architecture.py tests/test_uow.py \
  -q -p no:cacheprovider \
  --junitxml=/opt/rag-story-1-2/evidence/E-d6e8a0d/nonpg.xml
```

`d6e8a0d` 结果：232 tests、0 failures、0 errors、0 skipped，退出码 0。构成：`test_call_dispatch` 20、`test_child_supervisor` 22、`test_call_persistence` 20、`test_egress` 153、`test_architecture` 3、`test_uow` 14。

未重跑全仓、前端、1.3 限流、1.4 资产清理或真实供应方套件；这些结果不外推。

## 证据位置与首轮元数据说明

- `f3f1caa` 证据：`/fileOfRag/testOfRAG/metadata/story-1-2/dispatch/E-f3f1caa`，保留 `pg.xml`/`pg.log`/`exit`、`unit.xml`/`unit.log`/`exit`、前后 Git/hash 与原始输出。
- `d6e8a0d` 证据：`/fileOfRag/testOfRAG/metadata/story-1-2/dispatch/E-d6e8a0d`。
- 可直接复核的 E 索引：[story-1-2-e-canonical-pass-d6e8a0d.json](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-e-canonical-pass-d6e8a0d.json:1)，记录精确命令、前后 Git/源 hash、`sync.exit=0`、`pg.exit=0`、`nonpg.exit=0`、PG `28/0/0/0`、非 PG `232/0/0/0`。`pg.xml` SHA-256 为 `56e0bac66a5eb2c78093a5e5ce40a475829a78354b5b23456e0389fde48e935d`，`nonpg.xml` 为 `9fb5827835ef43732a3ad31e7761e2c93b342875f5dda79a8385b2deeb285153`；对应日志 hash 分别为 `bcb1acd7…`、`50fa0788…`。
- 本地核对的原始 XML 为 `C:/Users/29157/AppData/Local/Temp/rag-story12-E-d6-pg.xml` 与 `rag-story12-E-d6-nonpg.xml`；逐节点复核上述 13 个 E PG 用例和 20 个 unit 用例均无 failure/error/skip。未再次经 MCP 拉取同一份证据或重测。
- 首轮 `pg-command.txt` 的主控包装命令文本含 `printf` 字面、`ragEDevDir` 与仅为记录命令的错误；真实 pytest 参数、XML、log 与 exit 正确。首轮原字节保留，元数据由主控纠正，不用文本修正替代运行结果。
- 上述计数来自固定提交实际运行的 JUnit/原始输出；本文不把静态检查、mock 计数或另一提交结果冒充本提交通过。

## 原 AC 到 E 的映射

本表只覆盖 E 归属的集成/故障矩阵。B 的 DNS/TLS/redirect 细节由 B 固定专题证明，A 的 epoch 镜像/迁移由 A 固定 PG 证明，C 的槽占用/IPC 细节由 C native 25 证明；此处不重标这些他域证据为 E 运行结果。E 正式审查增量已关闭，D 运行与独立验证仍未关闭。

| 原 AC 子句 | E 证据 | 当前状态 |
| --- | --- | --- |
| 当前合法 context/已核目标下单 call 受监督，至多一次 grant，结果/unknown 持久且秘密不泄露 | 真实 end-to-end、单 grant/重启否定、四能力路径、E repr 边界；child argv/env/import 另由 C 断言 | E 开发者已过；C 断言不重标为 E 运行 |
| prepared 前后、may 后、响应前后崩溃/超时沿真实路径；原 call 不恢复重发 | prepare/grant/receive 故障、SIGSTOP+真实 TERM/KILL、unknown 后无二 grant | E 开发者已过 |
| unknown 为 NULL+unknown；可信迟到 usage 仅按 call 幂等追加 | 真实 unknown 行、可信 `result_fact` 晚到、重复/冲突不复活、A 事实约束未放松 | E 开发者已过 |
| 终结/旧 epoch/换 attempt 后旧 fence 零业务写；拒绝目标/下载凭据无派发 | 真实 PG 负例、purpose 分层正反例、下载 Authorization 错配 | E 开发者已过 |
| 无网络/进程等待持 PG 事务 | 并发查询 `idle in transaction=0`、真实 child receive 阻塞窗口 | E 开发者已过 |
| child 无业务 DB/主密钥、不自主串阶段、secret 不入 argv/日志 | C native 固定件（22 child，含 argv/env/import 断言）；E 真实 end-to-end 复用同一 supervisor 与 entrypoint | C 已过；E 未重复该断言，只证明集成调用路径 |

## 仍未通过或未执行

- 独立 Step 5 验证尚未基于 `d6e8a0d` 完成；E 开发者测试不替代独立验证。
- 全新 `GPT-6.1 Sol / medium` 审查已在[正式审查报告](/E:/aaa-project/rag/docs/story-1-2-code-review.md:1)完成本次 E 相关增量复核：直接核对 `d6e8a0d` 三个固定 blob、两份原始 XML 的 E 13 个 PG 与 20 个 unit 节点，结果无 failure/error/skip，**0 新增代码发现**；F2、E 成功/可信迟到断言、真实 SIGSTOP/KILL 与 URI 输入缺陷均按真实证据关闭。该结论只覆盖 E 增量，不代替 D 运行或独立验证。
- D 的部署/启动/重启门未纳入本次 E 运行；主控已转 D。
- 真实供应方与目标部署环境属于后续 Story/实际接入环境门，尚未到期，不列为当前 Story 1.2 剩余验收阻塞；显式假件与本地 child 结果也不得外推为这些门的证据。
- 父 Story 1.2 当前仅剩 D 的启动/重启运行证据与独立/最终验收；E 开发者门与本次正式审查的 E 增量均已完成。本文件不签署父 Story 或整个 Sprint。

