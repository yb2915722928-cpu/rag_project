---
title: 'Story 1.1 官方准确镜像获取恢复'
status: in-progress
route: dispatch
baseline_commit: a269d492fb33b3b13d95265fa11589d39260c4e0
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-deploy.md
  - E:/aaa-project/rag/deploy/offline-images.md
---

## Intent

为 D 获取可信的准确完整镜像，不以网络恢复替代部署验收。

## 归属与边界

DeepSeek 默认档位的新部署接替者独占 `deploy/**`、`docs/story-1-1-official-image-access.md`，不改 backend/contracts/frontend、主控状态或 Git。先等主控确认实际模型再写入。

本次新触发条件：Windows 已有系统代理 `http://127.0.0.1:65532`；仅 gh 进程设置 HTTP(S)_PROXY 后，官方 GitHub 授权及推送成功。此前 Docker 源超时记录保留。可复用现有代理做官方工件获取的进程级访问；不改全局代理/Docker、不新建主机、收费仓库、网络服务或传输通道。代码只能经 GitHub/Gitee，由主控发布；镜像工件不冒充代码同步。所有运行/构建/测试只在 Netcatty Linux。

## Tasks & Acceptance

- [ ] Given 新网络证据，when 查核官方仓库/发布源，then 确认 Python3.12.8、Nginx1.30.6、PG18.6、pgvector0.8.7、uv候选的真实可用版本及linux/amd64；不存在的准确版本如实阻塞，不能自行换版。
- [ ] Given 官方镜像，when 取完整工件，then 分别保存 index/platform digest、完整层、image ID、版本及归档SHA-256；只有manifest不能通过。
- [ ] Given 服务器，when 使用Netcatty，then先get_environment；仅操作项目资源，活动目录在 `/opt/rag-story-1-1`，最终证据在 `/fileOfRag/testOfRAG/metadata/story-1-1/official-image-access`；不删除其他项目或桶。
- [ ] Given 获取不可行，when 报告，then区分网络、授权、准确tag/源码不存在、缺层与未获准通道；保存一次有效诊断及触发条件，不空转探测。

## 交付

写明实际修改、官方来源、原始失败或完整工件证据、未通过项和下一可执行动作。D的真实PG/生命周期/干净重建与E来源门仍须另行执行；不提前启动依赖C的构建。
