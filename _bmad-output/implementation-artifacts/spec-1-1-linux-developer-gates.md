---
title: 'Story 1.1 Linux 开发者运行门与正式契约生成'
status: in-progress
route: dispatch
baseline_commit: a269d492fb33b3b13d95265fa11589d39260c4e0
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-runtime-entrypoints.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-contract-models.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-contract-http.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-contracts-dispatch.md
---

## Intent

恢复 A2a/B0a/B0c 的开发者运行门，通过后交付正式 B。父 Story、PG、四服务、独立验证和审查义务保留。

## 归属与环境

DeepSeek 默认档位的新接替者独占 `backend/**`、`contracts/**`、`docs/story-1-1-linux-developer-gates.md`。其他文档和 Git 由主控维护。先等主控确认实际模型再写入；不恢复已关闭实例。

GitHub/Gitee main 已同为 baseline。Netcatty 目标 `120.53.251.166`，先 get_environment；服务器 `/opt/rag-story-1-1/repo` 已干净检出 baseline，来源只用 Gitee。解释器与 uv 位置见 A1 交付记录，必须精确 3.12.8，正常 `uv sync --locked`。活动数据留本地 Linux，证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1/linux-developer-gates`。不覆盖历史工件。

## Tasks & Acceptance

- [ ] Given 固定 checkout，when 测试前后核对 commit、源码 SHA-256、锁和实际解释器/Uvicorn，then 证据与当前字节绑定；新增文件也列清单。
- [ ] Given 既有 runtime/public/HTTP/H 实现，when 执行 Linux 非 PG 全量开发者回归，then 保存原始日志、JUnit、命令、退出码及每项失败/跳过/未执行分母。真实错误解释器负例独立执行；不能把 PG 条件筛除计通过。
- [ ] Given B0a/B0c 门全部通过，when 正式生成 OpenAPI/Schema/TypeScript、执行检查及52条样例，then 保存真实工件、计数、hash和一致性证据；延期的 comparison 业务仍按原分派。
- [ ] Given 运行失败，when 修复，then 仅在本地认领文件修改并报告主控；由主控发布新固定提交后服务器再从 Gitee 拉取回归。不得远程改源码或自行提交推送。契约变化先由主控协调。
- [ ] Given 正式 B，when 交付前端，then 列出准确接口和未通过门；不得提前标父 Story done。

## 交付

报告实际模型/环境、文件/hash、原始证据位置、测试计数与未完成项。主控确认运行门后再派 Kimi；本实现者不兼任独立验证或审查。
