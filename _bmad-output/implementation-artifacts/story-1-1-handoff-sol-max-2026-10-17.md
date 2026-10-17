# Story 1.1 串行接力交接提示词：GPT-6.1 Sol / max

日期：2026-10-17，Asia/Shanghai。用户明确要求改主会话分工并交接新会话继续串行开发。本次为同一 Story 的主控转交，不是放行 Story 1.2。

## 可直接执行的提示词

接续 RAG_all Story 1.1。主会话必须是 `GPT-6.1 Sol / max`，创建时按 AGENTS.md 的模型映射传入对应工具 ID；不再要求 GPT-6 Astra、不自动切 ultra。主会话只做规格、契约、派发、协调和验收，不编写应用、测试、锁、实现脚本或部署。

先读 [当前工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md:1)，再读 [项目规则](/E:/aaa-project/rag/AGENTS.md:1)、[唯一认领](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1) 和 [最新模型/环境决定](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-model-environment-decision-2026-10-17.md:1)。其余完整材料按工作集的需回读条件加载，不无条件重读全部规划。

做一次合并只读诊断：读取自己实际 rollout 的最新 `turn_context.model` 和 `effort`、可读取的路由信息、同项目会话、relay owner、实现认领及已有环境摘要。`reasoning_effort` 为空时查看实际 `effort`，不要误报没有档位。运行记录是路由组证据，不冒称不可读的底层供应方身份。两个旧实现子智能体的真实记录均为 `GPT-6.1 Sol / medium`；原始路由 ID 保留在历史证据中。先前仅凭其自述判模型不可用的结论已纠正，不再派发“确认自己模型”的空任务。

项目为 `rag`，ID `61e1f316-4db1-4b50-a56e-62c5604d7d25`，目录 `E:/aaa-project/rag`，local；不创建 worktree。转出会话 `01a1489a-52c3-7590-9181-880dabdb3dd1` 只记录你的 threadId 并核实接手，不再派发实现。若 relay 未登记你的 ID，只做只读恢复；登记且 `handoff_source_write_released=true` 后，接受交接、更新唯一 owner 状态并继续。旧 Turing 已关闭，Laplace 已停止且无文件交付，无有效实现写入认领。

立即推进这些已授权工作：

1. 使用 bmad-build 恢复 in-progress Story 1.1。所有短规格达到1600-token风险线自动继续拆分，保持原四项AC和A/B/C/D/E分母，不重复请求常规批准。
2. 用户已把解释器从3.12.15改为精确CPython3.12.8。由后端实现者更新项目声明、解释器选择、runtime检查、有限错误与启动/门禁测试，并用真实3.12.8重算uv.lock，保留uvicorn0.37.0，执行--locked同步。代码尚未改，旧锁尚缺Uvicorn；不得声称已完成，不手改锁或用frozen绕过。同步当前规格对新授权的引用，保留旧失败/测试历史。
3. C1/C2/H后端真源前置仍未实现；派发前收敛短规格与唯一文件归属，再由复杂实现角色补最小公共模型/有限错误/有界维护HTTP入口和测试。只做当前Story所需契约，不实现未来业务。随后独占contracts/**导出OpenAPI/JSON Schema/TS及正负边界。
4. B通过后Kimi K3默认档位实现frontend/**，编码前识别栈、查GitHub官方/维护规范，记录来源/文档/版本或提交/日期/采用规则。D由复杂角色独占deploy/**，只含gateway/API/worker/PG。其余局部后端/常规RAG用5.6 Sol/high。
5. 代码运行、构建和测试走Netcatty Linux服务器120.53.251.166。MCP已连接过；真正使用时get_environment取得实际session，勿硬套旧ID。Engine29.8.2与Compose5.6.0已有证据；宿主Python3.12.3、无uv，准备隔离3.12.8环境或镜像，不要求用户修本机Docker或安装3.12.15。测试材料及证据放真实存储桶/fileOfRag/testOfRAG/{originals,derived,metadata}，不能建大小写不同路径。数据库和活动锁目录须核验本地文件系统语义，不把存储桶当POSIX保证。旧Docker已按用户授权清空，存储桶及宿主绑定目录保留；不得再全局清理。
6. 真实PG18.6/vector0.8.7、require-postgres六项必跑、迁移循环/namespace负例、Uvicorn进程和四服务Linux生命周期均待执行。保存源码/上传/镜像hash或digest对应、许可证与来源、E台账；DSN/秘密不进聊天、普通日志和证据正文。
7. 开发者先完成测试；Step5默认档位独立验证；全新6.1 Sol/medium独立审查，直接读需求/实际改动/验证证据。修复交回原实现者再回归和独立复核。未执行、skipped、unknown、只静态或只完成子规格均不放行。

本次交接后持续完成可执行工作。只有真实不可恢复阻塞才停并留证；不重复探测未满足复核触发条件的外部阻塞，不重复创建同一阻塞的空转会话。当前Sprint的串行接力已授权：只有父Story全部完成门通过，才更新Sprint/台账/relay、记录实际模型环境与文件hash，并自动在同一项目用6.1 Sol/max创建第一个依赖满足且未认领的下一Story会话，核实接手后释放写入。未过门始终续1.1，不提前开始1.2；Sprint全部通过后停止，不扩展别的Sprint，也不声称有定时自动化。

## 按需完整材料

工作集的“需回读条件”列有原始epics、A规格、后端契约前置、B规格、架构、重建证据和运行门入口。需要父Story矩阵时读 [交付计划](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-delivery-plan.md:1)；原始AC见 [epics](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:184)。最新决定优先于历史模型/3.12.15描述，原AC与安全不变量不缩减。
