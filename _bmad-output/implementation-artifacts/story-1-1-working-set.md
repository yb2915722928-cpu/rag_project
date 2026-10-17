# Story 1.1 当前工作集

更新时间：2026-10-17（Asia/Shanghai）。只记录当前状态；不替代原 Story、AC、架构和验收证据。

## 目标与唯一认领

- 继续 Story 1.1；父 Story 四项 AC 与 A/B/C/D/E 均完成后才进入 1.2，当前完成门 `not_passed`。
- 项目 `rag`，目录 `E:/aaa-project/rag`，项目 ID `61e1f316-4db1-4b50-a56e-62c5604d7d25`；新会话使用 local。
- 唯一 owner 及交接目标以 [relay state](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1) 为准；转出会话 `01a1489a-52c3-7590-9181-880dabdb3dd1` 仅负责创建登记，交接后释放写入。
- 当前主控 `01a148e2-1e11-7322-9626-6cbafb956f12` 已接手，原会话已释放写入；旧 Turing/Laplace 无有效实现认领，不等待旧实例。
- 当前实现：Jason（`01a148e6-0fcd-7ff1-af01-c546f5146474`，6.1 Sol/medium）独占后端及 A1 交付记录；Arendt（`01a148e6-261a-7922-8c94-74f5ad661466`，6.1 Sol/medium）独占 deploy 及 D 交付记录。远程目录分别是 `/opt/rag-story-1-1/backend-work`、`/opt/rag-story-1-1/deploy`，不得互改。
- 后端认领排除新增 `contracts/public.py`、`scalars.py` 与专用测试（Schrodinger，`01a148e7-fe2c-7b22-a61a-1ed49999b7fa`，6.1 Sol/medium），以及 `entrypoints/json_guard.py` 与专用测试（Boyle，`01a148f1-834b-7920-82f2-bfa8a81d7ede`，6.1 Sol/medium）。二者分别独占 contract-models-work/json-guard-work 远程子目录。模型初稿已要求原作者修复；均未验收。
- 主会话使用 `GPT-6.1 Sol / max`；其他角色按 [AGENTS.md](/E:/aaa-project/rag/AGENTS.md:7) 的当前模型名称分工，工具调用仍使用映射后的稳定 ID。
- GitHub仓库 `yb2915722928-cpu/rag_project` 已建；用户最新约定改为服务器只从 Gitee `https://gitee.com/QAQsdsdsdsds/rag_project.git` 拉取，GitHub作为开发上传源。后续每个固定提交需同步到两个远端，服务器先核 commit/hash 再测试。现有本地检查点 `843b45af92241cc0603135b5a341605863df5ece` 尚未完成 GitHub/Gitee同步；此前服务器直接拉GitHub超时/缺认证的记录保留，不再作为服务器拉取路径重试。详见当前 [Git阻塞续接](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-handoff-git-auth-2026-10-17.md:1)。

## 用户最新决定与已有证据

完整增量和 hash 见 [模型与环境决定](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-model-environment-decision-2026-10-17.md:1)。

- Python精确3.12.8的A1声明/正常锁/locked同步及实际Uvicorn开发者证据已交付；不覆盖后增HTTP/worker代码或父Story全门。用户无需再安装3.12.15。远程与本地DockerHub IPv4/auth超时已补证，官方GHCR uv仅manifest可取，不等于完整镜像或全网不可用。
- 构建/运行/测试使用 Netcatty SSH 主机 `120.53.251.166`。已验证 Engine 29.8.2、Compose v5.6.0；宿主 Python 3.12.3、无 uv，需项目隔离的 3.12.8 环境或镜像。
- 实际存储桶挂载为 `/fileOfRag`，测试材料放 `/fileOfRag/testOfRAG/{originals,derived,metadata}`。不另建大小写不同的路径；活动数据库和 Linux 锁语义不得凭存储桶挂载推定。
- 用户授权的旧 Docker 清理已完成：无容器/镜像/卷/Compose 项目，默认网络和存储桶保留；宿主绑定目录未删除。
- 实际 turn_context 已证明主会话为 `GPT-6.1 Sol / max`，此前两次实现均为该模型 `medium`；原始 `turn_context.model` 路由 ID 保留在 relay 和历史证据中。已纠正先前仅凭子智能体自述作出的模型不可用结论；底层供应方身份未核。不再重复派发“确认自己模型”的空探测。

## 剩余分段

| 分段 | 状态与下一步 |
| --- | --- |
| A 后端 | A1正常lock/locked已过，73pass+1条件skip，真实3.12.3负例单跑1pass，Uvicorn实际进程通过；非PG原46工件hash对应，PG六项未跑。A2a可信bind/持久worker本地冻结，等Git固定提交验证；原作者Jason负责修复。 |
| B contracts | 公模与B0c HTTP本地冻结待Git同步/开发者测试；H开发者165pass，Step5独立259pass无skip（含9项取消），全新审查P2关闭/P3更正，未见解析器可证缺陷。B导出尚未开始，不提前判B完成。 |
| C frontend | C0官方create-vue/Router/Pinia/ElementPlus固定规范与Node SHASUMS已读，记录完成；仍等B再初始化frontend。Kimi原实例可续，未安装/生成前端。 |
| D 四服务 | Arendt交付骨架/静态/文件系统证据，partial-blocked。Docker Hub IPv4 registry/auth连接超时已有原始证据，不重复探测；精确digest和PG镜像仍未取得。等待B/C与后端bind/worker，实际构建/生命周期未执行。 |
| E 来源台账 | A1实际依赖/许可证metadata JSON已归档及下载，40第三方锁条目/38项Linux实际安装无版本差异，两项Windows marker未选；前端peer/完整原生与镜像层/digest/干净重建仍待补。 |

## 下一步与复核触发

接收会话先读本文件、项目规则、relay 及最新决定，合并核验实际模型/档位、同项目会话和唯一认领，取得职责后使用 bmad-build 恢复 1.1。先落实 Python 版本变更和后端契约前置，独立且文件不冲突的工作按契约调度。主会话不写应用、测试、锁或部署实现。

仍未关闭：Git HTTPS认证/私库读取、新模型/HTTP/worker的固定提交测试、B生成物、真实PG18.6/pgvector0.8.7、精确完整镜像与四服务生命周期、C/E、父Story全量独立验证/审查与回归。旧本机Docker故障不再阻塞指定远程路径；模型执行记录已核，不能用旧标签继续卡住可执行工作。H取消验证/审查已闭环，仅文档收尾；不创建同一外部阻塞的空转接续会话。

连接断开、实现交付、源文件变化、部署或测试需要、用户环境变更才复核相应环境；不重复枚举已有清理结果或重试 3.12.15。保存失败与 unknown，不将静态、skipped 或旧补充测试转为新运行门通过。

## 需回读条件

派发某分段、修改 AC/契约/架构、出现审查冲突或本工作集与实际不一致时，选择性读取 [父 Story 计划](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-delivery-plan.md:1)、[A 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-rebuildable-modular-project.md:1)、[后端契约前置](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-backend-contract-source-dispatch.md:1)、[B 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-contracts-dispatch.md:1)、[原始 epics](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:184) 及相关架构真源。验收时读取 [重建证据](/E:/aaa-project/rag/docs/rebuild-evidence.md:1)、[来源台账](/E:/aaa-project/rag/docs/dependency-manifest.md:1)、[Sprint](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-status.yaml:1) 和 [运行门](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/runtime-acceptance-status.yaml:1)。历史文件中的旧模型/3.12.15不覆盖本次授权，不无条件加载所有规划材料。
