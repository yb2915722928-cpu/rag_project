---
title: 'Story 1.1 D 四服务 Linux 骨架'
status: in-progress
route: dispatch
baseline_commit: NO_VCS
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/epic-1-context.md
  - E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-model-environment-decision-2026-10-17.md
---

## Intent

以锁定工件重建 gateway/API/worker/PostgreSQL 四服务，仅交骨架，不增加业务、队列或生产向量表。

执行上下文：主会话已成功渲染 bmad-build 并进入 Step 3；本任务是该步骤的实现 handoff，不再次启动技能工作流。RTK 沙箱拒绝应按工具规则请求 escalation。Netcatty 同一 session 只能有一个命令；忙碌时可在同一已保存 host 开本任务独立 terminal，核实际 ID，结束释放自己创建的会话。

## 文件归属与公共接口

唯一写入 `deploy/**` 与 `docs/story-1-1-deploy-delivery.md`；后端、前端、contracts、其他证据由各自写者维护。读取现有 API/worker/配置入口后使用，不自行修后端。后端精确 CPython 3.12.8、Uvicorn 0.37.0；PG 18.6、pgvector 0.8.7。前端静态构建来自后续 `frontend/**`，Node 只构建。需要接口调整时向主会话报告。

## Tasks & Acceptance

- [ ] 在 Netcatty Linux 查证批准的镜像/软件版本可用性与来源，保存准确 digest；不可取得时保存原始错误，不静默换版。
- [ ] 创建项目专属 Dockerfile/Compose/gateway 配置和可复现命令；私有成功及网关自产错误均 no-store、无条件缓存/静态私有资产直出；公开 hash 静态资源独立缓存。
- [ ] PostgreSQL 数据和活动锁使用经核验的本地文件系统，最小权限挂载；不将对象存储当 POSIX。服务有限关闭，API/worker 使用相同 application 与锁依赖。
- [ ] 后端/前端交付后进行构建、迁移、启动、健康、真实 Uvicorn/worker、停止/重启和干净 Linux 重建，记录实际副作用、hash/digest。未执行保持未执行。

Given 已锁四服务，when 构建/启动/停止，then 各进程和 PG 扩展版本可核且无额外常驻服务。Given 私有或失败响应，when 经过 gateway，then 不缓存也不泄秘密。Given 依赖未交付或上游版本不可取得，when 验证，then 明确阻塞而不伪装通过。

## 运行归属

先 get_environment 使用现有 `120.53.251.166` 会话。本地开发、远程构建；仅管理远程 `/opt/rag-story-1-1/deploy` 与 Compose 项目 `rag-story-1-1`，不要全局清理 Docker 或触碰其他项目。后端开发者独占 `/opt/rag-story-1-1/backend-work`。测试输入/输出/证据归档 `/fileOfRag/testOfRAG/{originals,derived,metadata}` 下本 Story 子目录，不删除存储桶或既有宿主目录。公共健康/进程接口以当前后端真源为准；迁移与 PG 测试用项目专属临时库/schema。

## 拆分

这是父 Story D 的短规格，B/C 依赖在对应构建步骤等待，独立准备可并行；不减少 A/B/C/E 和独立验证、审查的完成门。
