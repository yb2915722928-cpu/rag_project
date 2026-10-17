---
title: 'Story 1.1 A1 精确 Python 3.12.8'
status: in-progress
route: dispatch
baseline_commit: NO_VCS
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-model-environment-decision-2026-10-17.md
---

## Intent

将现有后端迁移到用户批准的精确 CPython 3.12.8，并以正常生成的锁实现可重建安装。父 Story 四项 AC 不变。

执行上下文：主会话已成功渲染 bmad-build 并进入 Step 3；本任务是该步骤的实现 handoff，不是再次启动 Story 工作流，不重新运行技能渲染器。RTK 包装器被沙箱拒绝时按工具规则请求 escalation，不将工具权限误作模型阻塞。Netcatty 同一 session 不支持并发命令；忙碌时可对同一已保存 host 开独立任务 terminal，先核实际 ID，结束释放自己创建的会话。

## 文件归属与接口

唯一写者独占既有 `backend/**`，但排除其他实现者新增的 `src/rag_app/contracts/public.py`、`src/rag_app/contracts/scalars.py`、`tests/test_public_contracts.py`、`src/rag_app/entrypoints/json_guard.py`、`tests/test_json_guard.py`；交付记录仅写 `docs/story-1-1-python-3128-delivery.md`。不改其他目录。C1/C2/H可并行，HTTP由主会话后续协调。旧 A 规格及审查记录作为历史，不把其中 3.12.15 当当前目标；既有 namespace、UoW、安全错误修复不得退回。

## Tasks & Acceptance

- [ ] 同步项目声明、解释器选择、runtime、安全错误和门禁/启动测试为精确 3.12.8；保留其他锁定依赖及 `uvicorn==0.37.0`。
- [ ] 经 Netcatty Linux 的项目隔离环境使用真实 3.12.8 正常重算 `backend/uv.lock`，执行 `uv sync --locked`；不手改锁、不用 frozen、不替换系统 Python。
- [ ] 运行开发者非 PG 回归和 Uvicorn 实际进程验证，保留历史结果；真实 PG 六项/迁移循环留后续 A2，不将 skipped 算通过。

Given 精确解释器，when 锁同步及启动，then 声明、实际版本、锁和进程一致。Given 其他版本，when 启动，then 有限拒绝且不泄秘密。Given 锁或源不可用，when 正常解算失败，then 保存原始错误与可核来源，不改用未授权版本。

## 环境与交付

运行与构建仅用 Netcatty；先 get_environment 取得现有会话。部署实现者并行独占远程 `/opt/rag-story-1-1/deploy` 及其 Compose；本任务只用 `/opt/rag-story-1-1/backend-work`，不修改部署资源。测试材料与证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1`，活动锁和虚拟环境用本地文件系统并核验。报告本地/远程工件 hash、命令、结果、未执行项；不得输出 DSN 或凭据。可直接修改授权文件并自行上传测试，主会话不代写实现。

## 拆分与承接

旧 A 长规格超风险线，自动 Split again。本规格只接 A1；A2 承接真实 PG/迁移/Uvicorn门，B0 承接公共模型与 H，B 承接生成物，C/D/E 各保留父计划归属。低于风险线即执行，不等待常规确认。
