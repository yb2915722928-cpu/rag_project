# Story 1.1 串行接力续接提示词：GPT-6.1 Sol / max，Gitee 服务器源

日期：2026-10-17，Asia/Shanghai。用户明确要求创建新会话继续当前 Sprint 的串行接力开发，并授权在接下来约12小时持续推进；这不是定时自动化，也不代表后台无人值守。除非出现必须由用户决定的重大需求冲突、不可逆外部操作授权、凭据/权限缺失或连续确认后仍不可恢复的外部阻塞，常规规格拆分、派发、实现、测试、审查、修复、回归、提交和阶段切换均自动继续，不要因普通中间结果询问“是否继续”。

## 立即读取与唯一认领

先完整读取 [当前工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md:1)、[项目规则](/E:/aaa-project/rag/AGENTS.md:1)、[relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)、[最新模型/环境决定](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-model-environment-decision-2026-10-17.md:1) 和本文件。其余规格按工作集“需回读条件”选择性读取，不无条件加载全部规划。

这是同一 Story 1.1 的唯一主控续接，不是 Story 1.2。新会话接手后，原会话 `01a148e2-1e11-7322-9626-6cbafb956f12` 释放应用代码写入职责；不要创建第二个 Story 1.1 owner，不与旧会话或旧实现者并行修改同一文件。主会话只维护规格、契约、文档、relay、验收和协调；应用、测试、锁、实现脚本、部署实现交给对应实现子智能体。

## 模型配置

当前模型展示名称与工具 ID 映射以 [AGENTS.md](/E:/aaa-project/rag/AGENTS.md:7) 为准：主会话使用 `GPT-6.1 Sol / max`，实际创建参数使用 `group/auto-gpt-6-1-sol` 和 `max`；复杂后端/部署/独立审查使用 `GPT-6.1 Sol / medium`，简单后端/常规 RAG 使用 `GPT-5.6 Sol / high`，前端使用 `Kimi K3` 默认档位，独立验证使用 `Step 5 Preview` 默认档位。历史 `turn_context.model` 原始 ID 是证据，不要改写。

## 当前真实状态

- 本地最新提交是 `a52ae3090948e7eeea6df87590f15ce35351d247`，工作区在交接前应保持干净；父 Story 完成门仍 `not_passed`。
- A1：精确 CPython 3.12.8、正常生成 `uv.lock`、`uv sync --locked`、A1 非 PG 回归和 Uvicorn 开发者证据已交付；这不覆盖后增 A2a/HTTP。
- A2a：可信 API bind 和持久空闲 worker 已本地冻结，但固定提交后的远程开发者测试尚未完成。
- B0a：C1/C2 公共模型和有限错误策略已本地冻结，固定提交后的开发者测试尚未完成。
- H：开发者 165 项通过；Step 5 独立验证最终 259 passed / 0 failed / 0 skipped（含真实 task.cancel() 取消探针）；全新 `GPT-6.1 Sol / medium` 审查未发现解析器可证缺陷，P2/P3 已处置。H 结论不替代 HTTP 或父 Story。
- B0c：维护 HTTP/OpenAPI 本地代码与19个专用测试已冻结，但尚未在精确 3.12.8 的固定服务器快照运行。
- C0：create-vue、Router、Pinia、Element Plus 官方规范和 Node 24.22.0 SHASUMS 已记录；B导出未完成，不能初始化前端业务代码。
- D：四服务 Compose/网关/预检骨架和 ext4 探针已交；完整镜像 digest、真实 PG、构建、生命周期和干净重建未通过。不要以静态 Compose 代替运行门。
- E：A1依赖/许可证 metadata 已归档；前端 peer、完整原生/镜像层、digest、干净 Linux 重建仍待补。

## Git 与服务器来源

开发者代码上传源为 GitHub `https://github.com/yb2915722928-cpu/rag_project.git`；服务器唯一拉取源为 Gitee `https://gitee.com/QAQsdsdsdsds/rag_project.git`。不要让服务器直连 GitHub。每次服务器测试前核对 Gitee 固定 commit 和源码 hash；GitHub/Gitee 若不同步，保留阻塞并使用明确授权的 Netcatty 文件上传/归档方式运行当前固定本地提交，不把临时归档伪称远端同步。

当前 GitHub 推送曾因本机 HTTPS 凭据不可用失败，Gitee 匿名 `ls-remote` 已能连通但当前 ref/commit 必须重新核实。不要反复探测已知无凭据的 GitHub路径。Netcatty 先调用 `get_environment` 取得实际 session；不要硬套旧 session ID。测试材料和证据归档 `/fileOfRag/testOfRAG/{originals,derived,metadata}`；活动数据库、锁和构建目录使用 `/opt/rag-story-1-1` 下核验过的 Linux 本地文件系统。

## 立即执行顺序

1. 做一次合并只读诊断：当前 turn_context、同项目会话、relay owner/写入释放、Gitee ref、工作区状态和已知外部阻塞。已有相同阻塞没有触发变化时不重复空探测。
2. 使用当前本地固定提交和 Gitee 服务器源准备唯一 staging；核对归档 SHA-256、commit 和关键源码 hash。先跑精确 CPython 3.12.8 下 A2a runtime entrypoint、B0a public contracts、B0c HTTP/OpenAPI 专用开发者测试。测试失败交回原实现者修复，不把旧 SFTP/A1 结果重标为新提交通过。
3. B0a/B0c开发者测试通过后，由复杂实现者独占 `contracts/**` 生成 OpenAPI、JSON Schema、TypeScript 和正负样例；生成物必须来自后端 `PUBLIC_MODELS`，不能手写第二套业务类型。然后才能派 `Kimi K3` 继续前端骨架/健康状态，编码前遵守 C0 GitHub 规范记录。
4. C/B完成后，复杂实现者继续 D 四服务集成：只使用 Gitee/固定本地工件，核精确 Python、Uvicorn、PG18.6、pgvector0.8.7、准确镜像 digest、PG UID/GID、TLS/secret 和 ext4；运行迁移循环、PG 六项必跑、namespace 负例、回滚、Uvicorn、gateway/API/worker/PG 启停/重启/干净重建。禁止全局 Docker 清理、替换版本或把 cosfs 当活动锁盘。
5. 各实现者完成开发者测试后，派 `Step 5 Preview` 做独立联调/异常/回归和必要部署验证；再派全新 `GPT-6.1 Sol / medium` 做独立审查。问题必须交回原作者修复，再做相关回归和独立复核。`skipped`、`not-executed`、unknown、只静态检查或只完成子规格均不能放行。
6. 主会话持续更新工作集、验收台账、runtime 状态、来源台账和 relay；每个阶段保留实际模型、命令、版本、环境、hash、输入/预期/实际、副作用、证据位置和未执行门。不要把12小时描述成自动化后台任务。

## 完成与下一步

只有父 Story 1.1 原始四项 AC、A/B/C/D/E 全部义务、真实 PG/Linux/browser/deploy 证据、开发者测试、Step 5 独立验证、全新审查和修复回归全部通过，才将 `acceptance_gate` 改为通过并选择当前 Sprint 第一个依赖满足且未认领的 Story。完成前始终续接 1.1，不提前开始 1.2。完成门通过后，保存完整验收快照和下一 Story 提示词，再在同一 `rag` 项目用 `GPT-6.1 Sol / max` 创建唯一下一会话并核实接手；若门未通过或只有相同外部阻塞，不循环创建空会话。
