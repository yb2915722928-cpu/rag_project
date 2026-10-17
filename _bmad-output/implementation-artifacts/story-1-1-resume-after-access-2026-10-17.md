# Amelia：Story 1.1 访问条件恢复后的续接

当前唯一主会话：`01a14973-8555-7131-8fd2-e9eec12f53fe`，实际 `group/auto-gpt-6-1-sol / max`。本会话本身是 Amelia，后端/部署/RAG 交 DeepSeek 默认、前端 Kimi 默认、独立运行验证 Step 5 默认、独立审查全新 6.1 Sol/medium。

优先读取 [工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md:1)、当前 [AGENTS.md](/E:/aaa-project/rag/AGENTS.md:1) 和 [relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)。工作集、原始四项 AC 和完成门不一致时按工作集需回读条件加载原规格、epics 与架构，不无条件重读全部规划。

## 认领与版本

继续当前 Story 1.1，不提前开始 1.2，不创建替代 Story owner。恢复时以一次合并诊断读取实际 Git HEAD、暂存/工作区、同项目会话、relay 和实现认领；不要把本轮起始基线 `a52ae3090948e7eeea6df87590f15ce35351d247` 自动当作恢复时最新提交。主会话只维护规格、文档、集成协调和验收，代码修复交原作者或明确接替者。

本轮准备代码和静态预审尚不替代 Linux 开发者测试、独立运行验证或正式 Story 审查。原始静态发现和修订证据见 [预审报告](/E:/aaa-project/rag/docs/story-1-1-preparation-review.md:1)，当前静态处置及原作者 ID 见 [主控记录](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-amelia-control-2026-10-17.md:1)。hash 只能用于其对应字节内容，不能把旧 Windows 或 SFTP 工件成绩重标为新提交通过。

## 只在新触发条件出现后复核

- Git 写入认证或集成权限变化后，主会话统一提交并同步 GitHub/Gitee，同一明确 commit 后服务器仅从 Gitee 拉取；核 checkout 状态和源码内容 SHA-256。此前 GitHub空仓库/API403、Gitee无refs的证据保留，不在没有变化时重复认证探测。
- 准确批准镜像的完整工件或网络状态变化后，才复核 digest/平台/来源。不得用仅 manifest、占位 digest 或其他版本放行，不重复 Docker Hub/auth 超时探测。
- Netcatty 实际使用或重连时先 `get_environment`，以返回 session 为准。目标主机 `120.53.251.166`，活动工作目录 `/opt/rag-story-1-1`，测试/最终证据归档 `/fileOfRag/testOfRAG/{originals,derived,metadata}`；不改拼写，不在对象存储上假定 POSIX 锁/数据库语义。

## 恢复执行顺序

1. 本轮F1–F8及C1-NZ原缺陷已获独立静态修复确认；恢复时核对实际hash与工作区，新增源码变化或未关闭发现仍须交作者修。原index已另归档为补丁，不能把报告历史index当恢复时实时状态，不重复创建owner。
2. 在固定 Gitee checkout 和精确 CPython 3.12.8 上正常 `uv sync --locked`；完成 A2a runtime、B0a 公模、B0c HTTP 的开发者测试与相关回归。保存原始日志/JUnit/版本/hash，不以 skipped/unknown 替代。
3. B0a/B0c 门通过后正式执行 contracts 生成、`--check` 与正负样例；记录 OpenAPI/Schema/TypeScript 实际工件和内容一致性，再派 Kimi 做 C，编码前实查官方 GitHub 规范、版本和拟用规则，锁 peer 并完成真实浏览器/响应式证据。
4. 使用精确批准镜像、真实 PG18.6/pgvector0.8.7 和 Linux 本地文件系统完成 D：预检、迁移循环、六项 PG、namespace/回滚、Uvicorn/worker 与四服务启停/重启/干净重建。补 E 来源、许可证、原生层、完整 digest/hash。
5. 开发者测试完成后派 Step 5 独立运行验证，再派全新 6.1 Sol/medium 正式审查；问题交原作者修复、回归、独立复核。原四 AC 与 A/B/C/D/E 全部义务通过才更新完成门。
6. 全部完成门通过后，保存验收快照及下一 Story 短工作集/提示词，核同项目会话与唯一认领，在同一已保存 `rag` 项目创建一个本地 Amelia 新会话，显式 `group/auto-gpt-6-1-sol / max`，核实接手后原会话释放写入。循环当前 Sprint 至完成或用户停止。

如果仅剩相同外部阻塞而没有新可执行工作，保留状态并通知具体所缺条件；不循环建空会话，不把接力描述为后台定时自动化。
