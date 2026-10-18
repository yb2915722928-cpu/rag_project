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

## 2026-10-18 E 固定提交增量复核（源码完成，运行待验）

本节接替原审查实例的相关增量复核，不重开正式审查或扩大范围。上文的原始 tree、diff hash、源码来源、历史 **0 新增**及当时未关闭状态全部保留；本节只更新已知 E 项的静态处置。D 及其运行门不在本次三源增量范围。

### 固定输入与身份

- 放行指令：`REVIEW_E_FROZEN_RELEASE`；开发者已明确三源 `SOURCE_FROZEN`。
- 增量基线：`e1966b489b84d0a0b53cf0a060f70b22916cb2a4`；固定受审提交：`f3f1caacc76cd9cf8bc72a8eba1fcd9bc246c36c`。仅审两者之间下列三源差异，共 150 行新增、23 行删除；上下文亦从固定提交读取，没有使用工作区源码。
- 主控核定本接替实例的实际 `turn_context`：`2026-10-18T00:59:02.447Z`、`group/auto-gpt-6-1-sol`、`effort=medium`。本实例未参与该修复的分析或实现；底层供应方身份不据此另作推断。
- GitHub/Gitee main 同值为主控本次提供的实测结果，本实例未自行联网复核。源码 SHA256 则由本实例直接读取固定提交的 Git blob 原始字节计算，并与该提交内[恢复记录](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-prefix-route-resume-2026-10-18.json:1)逐项核对，三项一致。

| 固定提交源码 | 本实例计算的 SHA256 |
| --- | --- |
| [call_dispatch.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:280) | `ae8f70488275cec3a88e96ba0e9eea883e8a3d783a2186001925a08045bdb848` |
| [test_call_dispatch.py](/E:/aaa-project/rag/backend/tests/test_call_dispatch.py:283) | `dda9fa70e386d6827628922370a7b6c737661ca055ef43487f0adacf3e509c7f` |
| [test_call_dispatch_postgres.py](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:113) | `3dc8ea2b5e38ebecaa76df557367f08a28b8118063b04142fab83a0d708078a4` |

以上链接方便定位；行号结论以固定提交的 `git show` 内容为准。追加前本报告 SHA256 为 `bc59f75da568c34f159ba8d37151e4f1228596712af08277f591bf7e0469e997`，用于标识保留的原报告字节来源，不替换上文原审查 diff hash。

### 已知项处置

| 已知项 | 本次固定源码核对 | 静态处置与运行边界 |
| --- | --- | --- |
| F2：业务用途与传输用途强制同值 | [execute](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:300)，范围：300–314，删除等值限制，将逻辑 `purpose` 原样交给 A；[PG helper](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:113)，范围：113–125，改用 `current.purpose`。单元成功路径同时断言 query 与 API；PG 成功路径检查持久化 query，新增错误业务用途拒绝及匹配 embedding context 成功路径。 | 原 F2 源码缺陷静态关闭；合法成功及错误用途拒绝的真实 PG 运行待验。 |
| E：正常成功断言错误 | [可信迟到重复/冲突用例](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:536)，范围：536–575，将正常成功后的 `fact_recorded` 改为 True，继续保留后续重复、冲突和原 call 状态不变断言。正常成功用例继续要求 True，并保留 unknown usage、NULL 数值及无第二次 grant 的断言。 | 原输入/断言不一致静态关闭；不表示该用例已运行通过。 |
| E：响应后记录失败缺可信事实输入 | [响应后记录失败用例](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:498)，范围：498–533，显式注入 `ResultFact(provider_ref="provider-stop-1", usage=UsageFact("reported",5,2,7), cost=None)`；断言 call unknown/NULL，追加事实含 provider_ref、reported usage、total=7 及 NULL cost。原事实非空约束未放松。 | 原空事实输入问题静态关闭；这是显式可信观察假件，不是实际供应方证据。真实 child + PG 迟到通路运行待验。 |
| E：真实 child 故障与 PG 同路径证据 | [StopAfterPrepare](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:408)，范围：408–437，先调用真实 prepare，再对实际 child 发 SIGSTOP 并观察 `/proc` 的 T 状态；[同路径用例](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:440)，范围：440–478，沿用真实 grant/receive/stop，要求真实超时、停止证明、退出码 -SIGKILL、PG unknown/NULL、无 fact 行及原 call 无第二次 grant。 | 原先只有异常包装、没有此同路径用例的源码缺口已补齐；真实 SIGSTOP/KILL、停止证明及 PG 持久化结果尚无本次运行证据，不能关闭运行门。 |

删除用途等值限制没有删除下载 Authorization 守卫：[EgressDispatch 与构造守卫](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:76)，范围：76–126，仍按目标传输用途拒绝凭据错配；[既有拒绝测试](/E:/aaa-project/rag/backend/tests/test_call_dispatch.py:517)，范围：517–529，仍要求 DNS 前拒绝。本次没有修改 grant 资格、停止等待与 UoW 的顺序或 call-only 迟到事实实现；复核仅确认新输入接入这些既有分支，没有给未改变实现追加新要求。

### 本次发现与未过门

本次限定增量 **0 新增发现**。已知项静态修复结论见上表，不将其转计为新问题，也不为零发现继续扩大审查。没有要求未来业务表、Story 1.3–1.5 功能或无关已过项重跑。

主控本次提供的新环境事实是：用户修复 Netcatty 后，official MCP `get_environment` 与会话 `94bede36-0e0e-444c-a8b7-f332d2542962` 的实际 execute 已恢复。历史“发现文件缺失/CLI 桥接拒绝连接”仍属于当时的 blocked 证据，不据此声称当前连接继续阻塞；连接恢复本身也不证明测试通过。

截至本次源码复核，尚未收到固定提交的开发者全部必需 PG/E 专题结果及对应独立验证证据，本实例没有运行应用、测试或部署。相关运行门保持 **not-executed / 待验**；若后续实际运行受阻，再按实际错误记录 blocked。原四 AC 的完整运行分母、D 门及独立验证要求保持有效，`fullrelease_gate=not-passed`，不签完整 Story PASS，不放行下一 Story。运行证据到达后仅核对本次相关节点、固定源码与原始结果，不自动扩新轮。

### 同次增量复核：首轮真实 PG 失败更新

主控随后提供 canonical `f3f1caacc76cd9cf8bc72a8eba1fcd9bc246c36c` 首轮 `--require-postgres -m postgres` 运行结果：28 项，**16 passed / 12 failed / 0 error / 0 skipped**。其中旧必需 PG 的 7+6+2=15 项全过，E 13 项为 **1 passed / 12 failed**。主控直接读取 XML 并用 PowerShell XML parser 解析，报告 XML SHA256 为 `870d458be241ab0d31656dabffcf4853c8313e6d429923ca4b658f746955196a`。这是主控核验后提供的运行证据；本实例未直接读取 XML、未自行重跑，也未收到逐节点原始失败明细或 XML 工件路径。

**已知 E 测试输入缺陷，未关闭：**[PG 假件 SECRET](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:58)含字面值 `{{SECRET_gtxjjq3p}}`，在[签名 request_target 构造](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:71)中未经编码直接拼入 query。主控报告绝大多数失败在 B 的合法 URI 字符守卫处被拒，尚未到达目标调用。该输入与固定源码相符；不能将这些早期拒绝当作 F2、可信迟到路径或 SIGSTOP/KILL 路径的运行验证，也不能未经逐节点证据便将 12 项失败全部归为同一根因。

前次静态复核未识别此假件编码缺陷；“0 新增发现”保留为当时静态检查结果，本节按实际失败修正 E 测试可执行性的判断。此问题已由主控回交原 E 实现者，属于当前 E 已知失败处置，不重复计数或扩大审查范围。拟议修复是在测试构造处使用 `quote(SECRET, safe='')` 编码 opaque query 值；不放松 B 的 URI/凭据守卫，不改 A/C。拟议补丁尚未作为新固定提交交给本实例，故本节不宣称修补已落盘、已静态通过或已运行通过。

运行状态据此由上节时间点的“未执行/待验”更新为本固定提交 **已执行、未通过（failed）**；目标调用路径中被输入拒绝挡住的断言仍未获验证。旧 15 项本轮通过成绩保留在 `f3f1caa` 来源下，不自动转为后续补丁提交通过。F2 及两处原输入/断言修复的窄静态判断保留，E 整体运行门不关闭。待收到小补丁的固定提交/差异及相关重跑原始证据后，继续同次限定增量复核；`fullrelease_gate=not-passed`，不签 E 运行或完整 Story PASS。

### d6e8a0d URI 补丁与 E 重跑处置

本次仅复核 `d6e8a0da94a88199e6c4795f3e10e26c821b454f` 相对 `f3f1caacc76cd9cf8bc72a8eba1fcd9bc246c36c` 的差异。固定提交可解析且差异仅为 [PG 测试文件](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:14) 引入 `urllib.parse.quote`，在[API 签名目标](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:69)和[下载拒绝目标](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:626)均以 `quote(SECRET, safe="")` 将 opaque 测试值编码为合法可见 ASCII URI。没有放松 B 的 URI 字符守卫、Authorization 守卫或目标匹配规则，也没有修改 A/C/应用源码。该补丁直接覆盖上一节记录的已知测试输入缺陷，未形成新增发现。

主控提供的 `d6e8a0d` 运行证据为：PG 选集 28 项全部 exit 0；指定非 PG 选集 232 项全部 exit 0。运行时精确 CPython `3.12.8`、`uvicorn==0.37.0`、locked sync 均已核实；前后 Git 与源码 hash 已核实；证据归档于 `/fileOfRag/testOfRAG/metadata/story-1-2/dispatch/E-d6e8a0d`。这些是主控提供的执行与归档事实，本实例未自行登录 Netcatty 或重跑测试，未把本地静态检查冒充运行证据。

据此，上一节 `f3f1caa` 的 SECRET 早期拒绝失败已由该测试输入小补丁处置；本次 E 相关运行结果更新为 **PG28/28、指定非 PG232/232 exit 0**。F2 用途分层、成功/可信迟到事实、真实 child SIGSTOP/KILL、PG unknown/NULL 及无二次 grant 等已知 E 项的运行门，以主控本次全选集通过证据视为关闭；其代码与测试归属仍按原报告记录。此结论仅覆盖本次 E 增量和主控明确提供的选集，不扩展 D 运行或未来 Story 门。

本次限定增量 **0 新增发现**。`fullrelease_gate` 是否转为整体通过仍不由本次审查单独裁定；本报告不审 D、不新增未来门，并保留原报告全部历史记录。后续如无新的 E 实质差异或当前证据矛盾，不再为该 URI 补丁追加审查轮。

### 原始 XML 直接核验：E13 PG、20 unit 与修复回归

本实例已直接读取并以 PowerShell XML parser 解析主控提供的两份原始 XML，同时直接计算文件 SHA256，与[canonical 运行索引](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-e-canonical-pass-d6e8a0d.json:1)及主控提供值一致：

| 原始工件 | 本实例计算的 SHA256 | XML 实际结果 |
| --- | --- | --- |
| [PG XML](/C:/Users/29157/AppData/Local/Temp/rag-story12-E-d6-pg.xml:1) | `56e0bac66a5eb2c78093a5e5ce40a475829a78354b5b23456e0389fde48e935d` | tests=28，failures=0，errors=0，skipped=0；其中 E PG 节点 13 个，逐项无 failure/error/skipped |
| [非 PG XML](/C:/Users/29157/AppData/Local/Temp/rag-story12-E-d6-nonpg.xml:1) | `9fb5827835ef43732a3ad31e7761e2c93b342875f5dda79a8385b2deeb285153` | tests=232，failures=0，errors=0，skipped=0；其中 E unit 节点 20 个，逐项无 failure/error/skipped |

E13 中直接核到了正常成功及 unknown usage、错误业务用途拒绝、终结/换 attempt/旧 epoch 拒绝、prepare/grant/response 故障、真实 SIGSTOP child unknown/NULL/无第二次 grant、响应后可信事实、迟到重复/冲突、四类显式假件、目标/下载凭据拒绝及 child 等待不占 PG 事务的对应节点。20 unit 中亦直接核到了用途独立、一次 grant、失败/超时、停止未证、结果记录失败转迟到观察、下载 Authorization 和不安全 DNS 拒绝等对应节点。以上是已执行节点的原始结果核验，没有复跑历史 311 基础集或扩展当前审查范围。

索引记录 canonical commit 为 `d6e8a0da94a88199e6c4795f3e10e26c821b454f`，PG/nonPG 精确命令、exit=0、执行前 Python 3.12.8 与 uvicorn 0.37.0、Git 前后值、locked sync 日志/退出码工件 hash 及归档桶位置均有记录。环境与退出码仍归属主控服务器采集证据；本实例直接核验的是索引内容、两份 XML 原始字节及以下固定提交 Git blob hash。没有自行运行应用或把 XML 当作环境版本证明。

| d6 固定源码 | 本实例计算的 Git blob SHA256，与运行前/后索引一致 |
| --- | --- |
| [派发实现](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:1) | `ae8f70488275cec3a88e96ba0e9eea883e8a3d783a2186001925a08045bdb848` |
| [E unit](/E:/aaa-project/rag/backend/tests/test_call_dispatch.py:1) | `1595bf6b9aba9b877ee8a4135b3006163226af3818752fbc21fd34b3a1de2450` |
| [E PG](/E:/aaa-project/rag/backend/tests/test_call_dispatch_postgres.py:1) | `bdc14b9117d4fbf194315463aa8c878f53ad41145dfe516fd49567e12606cb82` |

**前节范围描述纠正：**此前只查看 PG 文件 diff 就写成“差异仅为 PG 测试文件”，该描述不完整。本次对固定提交三源一起比较，实际为两个测试文件共 10 行新增、3 行删除；[unit 目标假件](/E:/aaa-project/rag/backend/tests/test_call_dispatch.py:64)同样引入 quote 并编码 query SECRET，PG 有两处同类编码，应用源码不变。unit 小补丁也已核对，仍只修合法 URI 输入，未放松 B 守卫；对应 20 unit 已由上述原始 XML 直接确认通过。这一说明修正审查记录，不改写此前历史内容。

本次 **0 新增代码发现**。URI 输入缺陷及既有 F2/E 项的开发者实现与相关运行修复已获上述原始证据支持，相关已知缺陷可关闭；这不代替独立执行验证。索引明确 `independent_E_D=pending`、`D_runtime=pending`、`parent_acceptance_gate=not-passed`，本实例保持这些状态，不审 D，不给父 Story 签 PASS。

### D 实际权限故障：91bac6e 窄静态增量复核

主控提供的实际故障为：d6 镜像 build 成功，但服务源码/配置继承服务器 Git checkout 的 umask 077，出现 root 所有的 0700 目录及 0600 配置；UID 65532 无法读取/遍历，真实维护操作 import `rag_app.adapters` 报 ModuleNotFoundError。此处保留主控的运行故障来源，本实例未自行复现。该实际失败触发本次 D 必要增量复核，不扩展配额或未来验收要求。

受审固定提交 `91bac6eb8e27ea399140eb9a1f3f89462cafa64d`，基线为 `d6e8a0da94a88199e6c4795f3e10e26c821b454f`。本实例直接读取固定提交源码及 diff，确认 backend/deploy 范围仅 [api.Dockerfile](/E:/aaa-project/rag/deploy/api.Dockerfile:26) 变化，增加 12 行；应用、E/A/B/C 与 Compose 无差异。本实例从 Git blob 原始字节计算 Dockerfile SHA256 为 `8044d7086d7ecba6874ca91771378a89237fbdb5dfc7d5160aa52a52f6120414`，与主控提供值一致；双远端同值为主控提供事实，本实例未联网重验。

静态核对结果：

- [归一化步骤](/E:/aaa-project/rag/deploy/api.Dockerfile:30)，范围：30–31，在源码/迁移/配置 COPY 后将镜像 `/app` 所有者归 root，以 `u+rwX,go+rX` 补足服务 UID 的文件读取与目录遍历权限。没有增加 group/other 写权限；原有[无 group/other write 检查](/E:/aaa-project/rag/deploy/api.Dockerfile:33)，范围：33–34，仍在归一化后执行，输入原有可写位不会因本次补权限而绕过该检查。
- [服务 UID 切换与检查](/E:/aaa-project/rag/deploy/api.Dockerfile:36)，范围：36–41，先执行 `USER 65532:65532`，再实际读取 pyproject、锁、Alembic 配置及迁移文件，并 import epoch_control、postgres、runtime、API、worker 等模块。任一读取/import 失败将使该构建步骤失败，覆盖原先只由 root import 而漏检的实际读取边界；不是仅检查权限字符串。
- 改动限定镜像构建产物 `/app`，没有修改宿主机 checkout、挂载卷或运行时秘密权限，也未修改依赖锁、解释器或已有应用接口。

本次限定静态增量 **0 新增发现**。已知权限故障的源码修补与对应服务 UID 检查已具备；本实例尚未收到该提交的新 build 及原 D 启动/重启/异常矩阵结果，因此只判定静态修复，不签运行通过。`D_runtime=pending`，相关独立验证仍 pending，父 Story `fullrelease_gate=not-passed`。E 原始成绩继续归属 d6，保留且不重跑、不重标为 91bac6e 运行成绩。后续仅核对此实际 D 修复及原 D 矩阵的新证据。

### 91bac6e 真实运行更新：worker helper 权限失败

主控随后提供 `91bac6eb8e27ea399140eb9a1f3f89462cafa64d` 实际运行结果：镜像 build 的最终 UID 检查已输出 `SERVICE_UID_IMPORT_OK`；schema 迁移、epoch 显式初始化/镜像核对、check-database 均 exit 0。API 和 worker 实际 running，API liveness 返回 200，并有 `DATABASE_BASELINE_OK`。这些结果支持 `/app` 内权限修复有效，但不代替 worker 健康检查或后续重启验收。

随后原 worker 健康脚本 `/usr/local/bin/rag-worker-healthcheck` 报 `Permission denied`，`health_before=2`；主控核实该 COPY 产物同样为 0600，位于 `/app` 之外，未受前节归一化覆盖。[Dockerfile helper COPY](/E:/aaa-project/rag/deploy/api.Dockerfile:24)是该产物来源。本次记录的是已实际发生、已回交 D 的具体缺陷；本实例未自行读取服务器日志或重跑。前次静态检查只确认了 `/app` 的补权限与服务 UID import，未识别该外部 helper 的读取缺口，现按真实失败补充处置记录，保留前次结论的范围和历史。

D 的当前修复归属仅为此具体 helper 可读权限及最终 UID 下实际读取检查。尚未收到修补后的固定提交，不宣称补丁已完成或已审查；不新增其他路径遍历检查或泛化要求。原 91 运行中已通过的步骤保留其提交来源，worker 健康阶段为 **failed**，重启仍 **not-executed**，D 完整运行门不通过，相关 D 独立验证仍待验。

主控另更新 E 与独立 E 已全部通过，本报告按该状态保留 E 成绩；本次没有重跑或重开 E。后续仅在收到新固定提交后复核 helper 权限小补丁及原 D 矩阵相关证据。父 Story `fullrelease_gate=not-passed`，不将 API liveness 或数据库检查的局部成功提升为 D/Story PASS。

### 0162cb52 helper 权限修补：限定静态复核

本实例直接复核固定提交 `0162cb52f4c49265d99777c82d854b3617941941` 相对 `91bac6eb8e27ea399140eb9a1f3f89462cafa64d` 的 Dockerfile 差异，8 行新增、1 行删除；backend/deploy 范围仅该文件变化。从固定提交 Git blob 原始字节计算 SHA256 为 `6e933822a60a317476e20dc77c2f9d882c4c55cc1fa958462edb0008273faf36`，与主控提供值一致。双远端同值为主控提供事实，本实例未联网重验。

[helper 专项权限步骤](/E:/aaa-project/rag/deploy/api.Dockerfile:37)，范围：37–38，只将 `/usr/local/bin/rag-worker-healthcheck` 设为 root:root、0555，补足服务 UID 读取权限且不给 group/other 写权限；原 `/app` 归一化与写权限检查保留。[最终服务 UID 检查](/E:/aaa-project/rag/deploy/api.Dockerfile:43)，范围：43–48，在 USER 65532:65532 后把该具体 helper 加入实际 `open(..., 'rb').read(1)` 清单，读取失败会导致构建失败。该检查覆盖上一节已发生的 helper 不可读缺陷，不等同于执行健康探针成功；探针实际结果仍须由原 D 运行矩阵证明。

本次限定静态增量 **0 新增发现**。helper 权限缺陷的源码修补静态确认，不扩展 PATH、其他资产或新验收门。主控报告 91 的 API/worker 已安全停止、epoch/schema 未变，新 tag 正在 build，之后使用新容器名和同一 epoch 继续原 D 矩阵；这些是主控提供的运行安排，本实例未执行服务器操作。91 的健康失败记录保留，0162cb52 新 build、健康、重启及其余原 D 必需项尚待真实证据，D 运行与独立验证门均不据此放行。

主控明确独立 E 的 20 unit + 28 PG 已通过；E 与独立 E 成绩保留原提交来源，不重测、不改标为本次 Dockerfile 提交运行成绩。父 Story `fullrelease_gate=not-passed`。后续仅根据本修补的新 build 与原 D 相关运行证据更新处置。

### 0162cb52 原始运行证据：两项权限缺陷关闭

本实例已直接读取以下本地工件并计算 SHA256，没有重跑构建、应用、E 或 D 矩阵：

| 直接读取工件 | 本实例计算的 SHA256 | 文件中可直接确认的结果 |
| --- | --- | --- |
| [016 build](/C:/Users/29157/AppData/Local/Temp/rag-story12-D-016-build.txt:1) | `95fff4b10b0b31839ade18fb69ef1e3f595c3976b88b5569096def6902c8e34b` | 具体 helper 的 root:root/0555 步骤成功；最终服务 UID 实际读取配置、迁移与 helper 并 import 成功，输出 `SERVICE_UID_IMPORT_OK`；镜像 tag 0162cb52 导出完成，`BUILD_DONE` |
| [016 start/restart 输出](/C:/Users/29157/AppData/Local/Temp/rag-story12-D-016-start-restart-output.txt:1) | `16103091406196e4505571c7c4b7ebcf28af87cd560d6d9b2357dfb7c7095694` | API/worker running，API liveness 200，两处 `DATABASE_BASELINE_OK`，`worker_health_before=0`，epoch 文件 hash check OK、`MIRROR_UNCHANGED`；末尾两个容器为 exited，保留 CID/image 并输出 `START_RESTART_016_DONE` |
| [D negative summary](/C:/Users/29157/AppData/Local/Temp/rag-story12-D-negative-summary.txt:1) | `e05691a995b770c3790e4a19cf77bc59ef6c668e221366b0b5c3b688e635f084` | 缺 env、缺 file、不可读、mirror 矛盾四项均 exit 2，有限错误 `STARTUP_DEPENDENCY_UNAVAILABLE`；恢复后 `DATABASE_BASELINE_OK`、epoch hash check OK、两次 mirror 值相同；server HEAD 为 0162cb52，Dockerfile hash 与受审 blob 一致，汇总 exit code 0 |

构建文件中的最终镜像 manifest list digest 为 `sha256:c2a1ebb49f1c23a8ba1bb29ac14288d214f587458e9af6df7681c27e3795cf55`，与 start/restart 输出中两个容器的 image 相同。负例汇总中的 epoch 文件 SHA256 为 `f5d6a325ed0a05a5bdeb6ceeaba93a634d5570a8faa0881408231f4afd784248`，恢复前后 mirror 行一致。上述是直接读到的证据内容，不把 API liveness 单独视为 epoch 资格验证。

主控另提供 build exit 0、start/restart job `job_mvd7dlzt_81edc545e2d9` exit 0、重启前后同 CID/image 且 StartedAt 改变、末尾仅 stop 保留，以及 server checkout clean 的核验结论。提供的本地 start/restart 文件没有展开重启前后 StartedAt 成对原始行，故该细节明确归属主控核验；本实例不宣称在此摘要中直接看到了该成对记录。远程分文件 raw 仍位于主控指定的 D-0162cb52 evidence 目录，桶 `epoch-deploy/D-*` 长 job 归档尚在核对，不标为本实例已直接核完。

**已知项处置更新：**`/app` 源码/配置不可读，以及外部 worker helper 不可读两项，均有最终 UID 构建读取/import 与实际服务 baseline/worker health=0 的运行证据支持，当前已知权限缺陷关闭。91 的失败及其提交来源完整保留，不重标为当时通过。本次无新增发现，不追加检查。

独立 D 仍 **pending**；主控安排 Step 5 使用同最终 image/newroot 验证，本实例不将“即将运行”记为已通过。父 Story `fullrelease_gate=not-passed`，不签完整 Story PASS；E 与独立 E 既有通过成绩保留且不重跑。

### D 开发者完成证据同步（不追加审查轮）

本实例已直接读取[D canonical 开发者通过索引](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-d-canonical-developer-pass-0162cb52.json:1)。最终提交 `0162cb52f4c49265d99777c82d854b3617941941`、image `sha256:c2a1ebb49f1c23a8ba1bb29ac14288d214f587458e9af6df7681c27e3795cf55`、Dockerfile SHA256 `6e933822a60a317476e20dc77c2f9d882c4c55cc1fa958462edb0008273faf36` 与既有受审证据对应。只同步现有修复处置，不重审旧源、不新跑或增加检查。

| 当前项 | 处置与证据 |
| --- | --- |
| `/app` 读取权限 | 关闭；最终 UID 实际读取/import 成功，最终镜像 API/worker baseline 通过。 |
| worker helper 读取权限 | 关闭；最终 UID 读取及真实 helper health=0 支持，启动/重启 job exit 0。 |
| D 开发者原必需矩阵 | 通过；build、维护初始化、启动/重启及负例 jobs 均 exit 0。初始化保留 91 来源和同一 schema/epoch；最终镜像真实重启同 CID/image、StartedAt 改变，epoch hash/mirror 不变；四负例均 exit 2 有限错误，恢复后 baseline/hash/mirror 不变。 |
| 桶归档 | 索引记录归档 job `job_mvd7o34w_d2cc9724dee5` exit 0，D-d6、D-91、D-016 三部分已核，附最终 manifest；此前“归档核对中”的状态据此更新为完成。 |
| 静态与历史 | 静态 **0 新增发现**保留；原 d6/91 失败和实际来源不改写，E/独立 E 既有成绩保留，不重跑。 |
| 独立 D / 父 Story | 最后一次精简独立 D 验证 pending，等待 Step5 最终结果后仅同步状态；父 Story 尚不签 PASS。未到期门不列为当前阻塞。 |

按用户指令停止追加审查轮和假设检查；本次已知两项权限修复及开发者真实运行证据处置完成。

### 最终状态同步：独立 D 已执行，审查门 passed

本实例已直接读取[独立 D 原日志](/C:/Users/29157/AppData/Local/Temp/rag-story12-independent-D-terminal.log:1)，对应主控提供的 job `job_mvd7vw3k_6868ce4ec440`。固定源码仍为 `0162cb52f4c49265d99777c82d854b3617941941`，image 仍为 `sha256:c2a1ebb49f1c23a8ba1bb29ac14288d214f587458e9af6df7681c27e3795cf55`。

| 现有处置项 | 最终同步 |
| --- | --- |
| 两项 D 权限缺陷 | 保持关闭；独立日志中正常 API 200、worker health exit 0、baseline exit 0，真实 restart 后相同检查再次通过。 |
| 独立 D 执行 | 已完成；epoch hash diff exit 0，mirror 前后一致；missing/unreadable/mismatch 三个独立副本负例均返回有限错误、exit 2，inspect 均为 exited 2；末尾 normal 仅 stop，epoch hash 保持。此前“待独立执行”状态据此更新。 |
| 当前原 AC 范围审查 | 无新增发现，`review_gate=passed`；不重审旧源，不新增审查或测试。base/tree/hash、历史失败及 E 既有证据来源全部保留。 |
| Step5 最终报告 / 父 Story | 独立执行结果已到，Step5 正在形成最终独立裁决；父 Story 是否 done 由主控结合该裁决决定，本报告不提前签父 Story PASS。 |
