# Story 1.2 唯一正式源码快照审查

日期：2026-10-18（Asia/Shanghai）。受审快照审查完成；新增发现 **0**。已知 F2、E 测试对齐及故障矩阵、D 运行验证仍未关闭。`fullrelease_gate=not-passed`，实现推进状态为 `implementation_blocked`。本报告不授予 release PASS，不放行 Story 1.3。

## 有效发现：已知未关闭项

以下沿用派发前已登记的问题，不计作新增发现。源码定位均对应本报告指定的不可变 tree；链接打开的工作区若后来变化，须用同一 tree 的 `git show` 核对本报告行号。

### F2_PURPOSE_DIMENSIONS：合法业务用途与传输用途被强制等值

- 位置：[call_dispatch.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:296)，范围：296–303；[PG 执行 helper](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:112)，范围：112–122；[持久上下文夹具](/E:/aaa-project/rag/backend/tests/conftest.py:210)，范围：210–227。
- 具体输入与可达路径：持久上下文的业务用途为 `query`，出网目标为合法 API profile，已核公共 IP、请求与当前 fence 均合法；调用 `CallDispatch.execute(purpose="query", stage=EGRESS, egress=API计划)`。
- 实际代码结果：296–303 行把 `query` 与 `api` 比较，抛出 `CONFIGURATION_INVALID:profile_invalid`，尚未进入 prepare，也不启动 child。该合法输入不能走完单 call 路径。
- 同一问题的测试接线表现：PG helper 硬传 `purpose="api"`，而夹具默认持久化 `query`。即使绕过派发层的等值限制，A 的[持久 scope 守卫](/E:/aaa-project/rag/backend/src/rag_app/application/call_lifecycle.py:352)，范围：352–362，仍会因业务用途不匹配抛 `CALL_FENCE_STALE`。上游守卫确实拒绝该路径；没有据此报告越权或绕过。
- 对应原 AC：AC1 的合法假件执行及当前执行资格，AC2 的持久 call 与一次 grant 集成。业务用途应交由持久 context 核对；传输用途继续独立承担 API/upload/download 凭据守卫。
- 状态：未关闭。须由原实现角色修复并提交对应合法 `query + API` 的相关验证证据；本审查未写修补代码。

### E_TEST_ALIGNMENT：成功/可信迟到输入与断言不一致，真实崩溃集成证据未齐

这是已登记 E 问题的源码核对，不把同一问题拆成多个新增发现。当前 F2 会先阻断相关 PG 执行；以下是修通用途接线后仍可由代码确定的后续失败，**不是本次实测结果**。

1. [迟到 usage 测试](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:406)，范围：406–445，先正常执行真实 child，414 行却断言 `fact_recorded is False`。正常响应且停止证明通过时，[派发结果分支](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:451)，范围：451–471，进入正常结果记录；[成功记录返回](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:642)及[记录标志构造](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:676)，范围：676–689，将其设为 `True`。该断言与该测试的成功输入不一致，会在后续迟到 usage 断言前失败。不能将正常结果都要求为 False；同文件[正常成功测试](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:144)，范围：144–169，期望 True 是一致的。
2. [响应后记录失败测试](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:379)，范围：379–401，注入 `record_result` 失败，却未注入携带可信 provider_ref/usage/cost 的结果工厂。[真实假件响应](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/call_child.py:69)，范围：69–87，不包含这些事实；[默认结果工厂](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:161)，范围：161–175，得到三项均为 None。转入[迟到记录构造](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:616)，范围：616–621，会被 [LateFact 非空事实约束](/E:/aaa-project/rag/backend/src/rag_app/modules/ledger/facts.py:126)，范围：126–135，拒绝，返回 `fact_error=LATE_FACT_UNAVAILABLE`、`late_fact=None`，而不是该测试期望的追加事实。需要可信事实输入，不能放松事实约束或把不存在的 usage 记为零。
3. E 的[prepare/grant/receive 故障包装](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:242)，范围：242–281，只抛协议、IPC 或超时异常；其后 PG 断言不能单独证明实际 child 在该故障点崩溃。已有 C 的[真实 SIGSTOP/SIGKILL 用例](/E:/aaa-project/rag/backend/tests/test_child_supervisor.py:351)，范围：351–376，确实覆盖 native child 退出后的保守发送态，保留其通过证据；它没有 PG call 行断言，不能代替 E 已要求的真实 child kill 与 PG `unknown + NULL`、原 call 无第二次 grant 的同路径证据。

对应原 AC：AC2 的 prepared 前后、may_have_sent 后、响应前后故障矩阵与不恢复重发；AC4 的可信迟到 usage 幂等/冲突及等待在事务外。状态：未关闭。当前树的 E 矩阵没有完整开发者和独立运行通过证据，不能以 A/B/C 基础成绩替代。

### D：新 epoch 接线的镜像、启动/重启与负例未运行

- 源码位置：[API epoch 配置](/E:/aaa-project/rag/deploy/compose.yaml:95)，范围：95–98；[worker epoch 配置](/E:/aaa-project/rag/deploy/compose.yaml:147)，范围：147–149；[API healthcheck](/E:/aaa-project/rag/deploy/compose.yaml:125)，范围：125–130。
- 当前可见行为：API/worker 已接同一控制文件设置，普通服务使用只读 epoch 挂载。[运行检查](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:32)，范围：32–47，具有缺失控制和镜像不一致时的有限失败路径。接线存在不等于受影响部署已经运行通过。
- 缺口与实际后果：本次收到的证据不包含新镜像下首次显式初始化、普通启动/重启的 epoch 保持，以及缺失、不可读、镜像矛盾负例的完整运行结果；因此尚不能签署 AC1 的部署层结果。这里报告的是**未执行/未验**，不臆断这些操作已经失败。
- API `/health` 的成功只证明 liveness，不能替代 epoch 资格核对。该已知边界也在[部署说明](/E:/aaa-project/rag/docs/story-1-2-epoch-deploy.md:130)，范围：130–145，明确说明；不据此追加新的 readiness 功能要求。
- 对应原 AC：AC1 的独立 epoch、普通重启不轮换、异常隔离，以及本条改动所必需的启动回归。状态：未关闭。后续只需补当前 D 的相关运行证据，不重开 Story 1.1 全套门。

## 新增发现

**0。** 在指定差异、原四 AC 与现有证据范围内，未形成另一个具备具体输入、可达调用路径、源码位置和坏结果的新增问题。没有将已关闭 I1/I2/I3/F1 重新计数，也没有因零新增继续扩大审查。

## 不可变输入与独立性

| 项目 | 本次使用值或核对结果 |
| --- | --- |
| Git 基线 | `96e7fb3ee94c025c3fae804ddabf8ad71d8b08d5` |
| 受审 Git tree | `1eff8cf456f705b8c5e0b21985b87ad9d6a846d2` |
| 统一实现 diff | [指定 snapshot diff](/C:/Users/29157/AppData/Local/Temp/rag-story-1-2-independent-review-snapshot.diff:1)，30 个实现/测试/Compose 文件 |
| diff SHA256 | `b9a19d5beab26888cce9edc7f75cffb74eb90ec87a70fe8849e66b0b8ad79e21`；本实例读取文件计算，一致 |
| diff 与 Git 对应 | 30 个差异文件的旧/新 blob 索引逐项核对基线与指定 tree，0 mismatch |
| 与已独立实测 `96c64fbab0fa8d3d824f2e592196c02570550c70` 对应 | 上述 30 文件中仅 E 的[派发实现](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:1)、[单元矩阵](/E:/aaa-project/rag/backend/tests/test_call_dispatch.py:1)、[PG 矩阵](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:1)不同；其余 27 文件 blob 相同 |
| 需求分母 | [原 Story 四 AC](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:205)，范围：205–208；相关 C4/C5、R1/R2 及[公共契约](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-public-contracts.md:1) |
| 审查者运行身份 | 主控直接核定 `2026-10-17T22:58:04.779Z`、`group/auto-gpt-6-1-sol`、`effort=medium`；本实例未参与此前分析或实现，不自行宣称底层供应方身份已核 |

源码读取使用指定 tree 的 `git show <tree>:<path>`，审查没有混入后续工作区实现或新重试输出。工作集、台账、relay 和独立验证报告用于需求及既有证据归属；这些说明材料不替代不可变源码。本实例只做本地只读 Git/文件诊断与报告写入，没有运行应用、测试、部署、联网外发、再派角色或修改 Git。唯一本地写入为本报告。

## 已有运行证据及其边界

本审查读取[验收台账](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-acceptance-ledger.md:26)，范围：26–30、[独立验证报告](/E:/aaa-project/rag/docs/story-1-2-independent-verification.md:33)，范围：33–69，以及[relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)中的主控原始证据核对记录。以下是既有真实运行结果；本实例没有重新访问服务器 XML 或复跑测试。

| 证据归属 | 固定源码与成绩 | 本次如何使用 |
| --- | --- | --- |
| B 开发者 | `78402858fb003dfd62d57ed481f4f131e69424bf`；169 passed，0 failed/error/skipped | 保留原提交来源；不把旧成绩重标为新 tree 全量通过 |
| A canonical 开发者 | `af6ce5099166960e714a1e8b45f004cc8ac9f77a`；88 相关非 PG + 48 runtime 非 PG + 15 真实 PG；主控核 19 源 hash 无变化 | 支撑当前上下文权威、锁后 DB 时钟、一次 grant、迟到事实与必要回归 |
| C native 开发者 | `96c64fbab0fa8d3d824f2e592196c02570550c70`；22 child + 3 架构 = 25 passed；主控核六源 hash 无变化 | 支撑真实 Linux child、跨实例物理槽、未知停止阻断与绝对 IPC deadline；不代替 E 的 PG 集成 |
| Step 5 独立基础验证 | 同一 `96c`；311 非 PG + 15 PG，0 failed/error/skipped；主控已核 XML、Git 与 28 个唯一 snapshot 源 hash，0 mismatch | 只覆盖稳定 A/B/C 基础与已运行必要回归；不包含 E 完整矩阵或 D 部署验证 |

非 PG 的两个 worker PG 参数节点是 deselected，不计入 XML 执行数，不当作 skipped 或新增缺口。采用已校正的 311 执行数。旧 `52ccb1f` SQL 绑定失败和 server overlay 试跑保留历史来源，不计任何固定源码验收通过。

源码核对与上述证据一致的关键边界包括：A 先锁当前 context 再锁 call，并在取得锁后使用 DB 当前时间；迟到事实只锁 call，保留业务终态与冲突事实；B 核全部 A/AAAA 后绑定选定 IP，保留 TLS hostname 校验，不自动 redirect，下载/上传拒 API Authorization；C 的 child 仅显式假件且无 DB/主密钥环境，grant 单次消费，停止未证持续占槽，分段 IPC 共用绝对 deadline。这些结论只用于当前四 AC，不扩展到未来业务资格。

## 原四 AC 的当前裁决

| 原 AC | 本次审查裁决 |
| --- | --- |
| AC1 | A 的 epoch/context 权威及 C 显式能力假件基础证据保留；F2 阻断合法集成，D 受影响部署尚未实测，不能整条通过 |
| AC2 | A 一次 grant 与 C native 监督成绩保留；E 输入/断言和真实故障同路径持久化矩阵未关闭，不能整条通过 |
| AC3 | B 的目标守卫及独立基础成绩保留，本次无新增源码发现；E 集成拒绝路径仍随其相关矩阵验证，不重开 B 已过且未变化的无关门 |
| AC4 | A 的 call-only 追加、幂等/冲突、真实 PG 锁序证据保留；E 的可信迟到事实与 child 等待在事务外的集成证据未齐，不能整条通过 |

不把尚无未来业务表的事实变成要求先实现未来业务的新门；当前仍须证明既有 context/call/fact 不因迟到观察被复活或错误改写。Story 1.3 rate/permit/C8、1.4 资产清理、1.5 汇总、真实身份/供应方及目标硬件均不在本次新增验收范围。

## 实现阻塞与后续增量复核

主控在本次审查期间提供的事实更新：E 继任 9d40 与唯一同模型重试 Halley 都实际报 `502 / DeepSeek chat/completions EOF`，均已关闭；主控核对接替快照后，五份 E/D 源码 hash 无变化。该状态已记入 relay。本实例按主控更新记录实现通道阻塞，未自行探测通道，也未以错误状态推断 D 本身发生同一调用错误。

因此本次源码快照审查已完成，可以保存检查点；`fullrelease_gate=not-passed`，`implementation_blocked`。通道错误不改变受审 tree，不等待修补才交报告，不换模型、不由主控或审查者代写，也不再派同类探测。

后续沿用本唯一审查实例，只复核 E/D 的实质增量与相关真实运行证据：F2 用途分层、E 已列输入/断言与故障矩阵、D 本条启动/重启及负例。若影响公共契约，再核受影响边界；没有实质影响则不追加泛化轮或重跑无关已过项。原四 AC 全部必需子句及相应独立验证未齐之前，完整 Story 仍不得放行。
