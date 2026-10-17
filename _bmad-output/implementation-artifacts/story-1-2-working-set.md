# Story 1.2 当前工作集

状态：B169和A canonical151（88+48非PG/15PG）开发者通过且主控核原始证据；C四源+D两文件已冻待发布/实测，C调用集成未冻；父Story完成门未过。唯一主控 `01a14b42-689c-7533-90a3-9bd187d93039`，实际 `group/auto-gpt-6-1-sol / max`；接力ID `3dff3d78-c0f5-42cf-9860-fc2ad4250ab4` 已认领。[relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)为当前事实。

## 当前目标与唯一认领

只完成原 [Story 1.2 四条AC全部实质子句](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197)，不在此会话启动1.3。行数不是验收分母。主控只编排/文档/提交/验收，不改应用、测试或部署实现。

| 认领 | 实例 | 范围与状态 |
| --- | --- | --- |
| A Euclid | `01a14b4b-3d07-7a12-a4ea-8ae0f9db0540` | [A规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-a-persistence.md:1)开发者151已过；source冻结、只补交付文档，terminal归还 |
| B/D Faraday | `01a14b4b-41ea-7bd0-9b61-0e9475aadae8` | B出网源冻结；[D规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-d-epoch-deploy.md:1)Compose+部署说明已冻待启动回归 |
| C Heisenberg | `01a14b57-dbf8-7e11-8a3f-f678f9146dd0` | [C规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-c-supervision.md:1)I2/I3四源已冻待Linux；call_dispatch/PG矩阵继续 |
| 独立验证 Pascal | `01a14b8d-7d2f-7b62-875b-a324944c561c` | [验证规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-independent-verification.md:1)，只读ready，未release/未分terminal |

A/B/C实际路由均已核 `zayuapi/deepseek-v4.1-flash / max`，未传推理覆盖；Pascal实际 `stepfun/step-5-preview / high`默认。角色实例均未关闭，不恢复旧1.1写者。正式审查尚未派发，须全新6.1Sol/medium，零发现允许。

## 剩余工作与已证问题

- [公共契约](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-public-contracts.md:1)已固定A原5方法+3受控context入口、B EgressPlan、C grant消费已核plan。各实现者文件集不重叠；共享契约变更由主控协调。
- I1与SQL绑定F1已按af6 canonical开发者151和主控原始证据关闭，待父Story独立门；代码为持久context/context→call锁后DB时钟。52ccb1f失败及覆盖草稿不重标通过，非冲突测试使用相同usage且冲突测试保留。
- A违反固定提交指令直接覆盖旧server repo两源，覆盖后7PG/722后端通过仅草稿，不作52ccb1f或新提交通过。7原始日志/实际dirty状态/hash在relay及桶中保留。旧 `/opt/rag-story-1-2/repo`、`venv-dev`只保留草稿，禁止再运行或重置/删除它们。
- I2/I3代码已修并由主控完整读增量：`LinuxChildSupervisor(state_root=...)`明确共用本地绝对根、deployment+slot持久占用、proc未知/错绑无证明无信号、逐段收发绝对deadline；慢发测试先完整header再慢正文可检出旧错。四文件当前snapshot见[CD快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-cd-source-snapshot.json:1)，待Linux后关闭。旧草稿tree `7d9f05959370f17ae4a3532d882b2e11100b1c0d`保留、不计运行。
- D：现有Compose未传新epoch文件导致新worker隔离，补当前必要启动接线/首次显式init说明并验受影响启动重启。普通epoch目录0550、文件0400服务UID；不前移1.5完整S0资格/探路工具，不改旧1.1资源。
- 父AC2崩溃矩阵、AC4真实PG/迟到事实、C集成、D当前回归、独立验证、一次正式审查及具体修复尚未全部通过；不以子规格完成替代父Story。

## 当前固定源码与运行时段

- 最新发布 `af6ce5099166960e714a1e8b45f004cc8ac9f77a`，GitHub/Gitee main实测一致；服务器只从Gitee拉固定提交。[A修补快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-a-fix1-source-snapshot.json:1)含19 canonical源码SHA。主控已实际建干净 `/opt/rag-story-1-2/repo-fixed`，核HEAD/19 hash/锁与新venv精确3.12.8；后续只用此canonical根。
- Netcatty session `0d682d12-5a9c-4260-85b5-86713c7d4304`、主机120.53.251.166。A已归还，主控发布CD后分配C，其他角色无租约不得并发terminal RPC；只重连刷新环境。源码前后必须Git干净/hash不变；失败只本地修补→主控双远端发布→固定提交重测，禁临改server源。
- CPython3.12.8/PG18.6/vector0.8.7；venv `/opt/rag-story-1-2/venv-fixed`，uv `/root/.local/bin/uv`（默认PATH没有）。PG测试凭据仅source既有0400文件，位置见已发布setup；不输出DSN。活动目录在ext4，证据归 `/fileOfRag/testOfRAG/metadata/story-1-2`，大小写不能换。
- Netcatty已实际拒绝 `$(` 命令替换，改直接输出/分步核对已成功；这是已解决的命令语法限制，不是环境阻塞。

## 已核证据与下一步

- B在固定 `78402858fb003dfd62d57ed481f4f131e69424bf`：169通过（153出网/3架构/13 UoW），0失败/错误/跳过；主控直接读过桶中JUnit、exit、source记录及hash。[B交付](/E:/aaa-project/rag/docs/story-1-2-b-delivery.md:1)保持原工件来源，不重标到后续共享UoW变更。
- A canonical证据根 `/fileOfRag/testOfRAG/metadata/story-1-2/A-canonical-af6ce50`：主控已核3份JUnit/退出码/15具体PG节点/HEAD/status/19hash。原`/A`七日志保留失败/覆盖。下一步发布CD并给C Linux child时段；D可随后跑最小新后端启动回归，C完成剩余调用集成/PG矩阵。
- 所有开发者当前必需项稳定后，给Pascal最终固定提交/时段；再派全新6.1Sol/medium读原AC、真实diff、证据审查。只具体当前缺陷/必要回归，不凑数量、不自动追加泛化轮；适度检查通过后停止补强。
- 1.1已done/passed，见[验收快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md:1)，不重开全套。当前完成后保存快照/工作集/唯一认领，自动在同一项目创建下一Amelia接首个依赖满足Story；未全部完成不能放行。无定时自动化，无外部阻塞空转交接。

## 需回读条件

先读本工作集；只有契约/AC/归属/实际代码或环境变化才按需回读原Story、C4/C5、R1/R2、实施契约§2.5及对应分派。不重复加载全部规划，不重探已核且未触发变化的外部环境。无新触发时复用relay中的实际模型/环境证据。
