---
title: 'Story 1.1 A2a 四服务运行入口'
status: in-progress
route: dispatch
baseline_commit: NO_VCS
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-python-3128.md
  - E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md
---

## Intent

使同一后端工件可在四服务部署中持续运行并有限停止。当前 check-database 仍保留一次性维护语义；新增仅空闲骨架worker，不实现后续job/供应方/任务调度。主会话已进入bmad-build Step3，本任务无需重启技能。

## 文件归属与接口

前置A1交付且其写者释放后，原作者继续独占 `backend/src/rag_app/__main__.py`、`entrypoints/worker.py`、`bootstrap/config.py`、`backend/tests/test_runtime_entrypoints.py` 和 `docs/story-1-1-runtime-delivery.md`。不改公共模型、json_guard、API、锁、迁移、其他测试、deploy。

新增CLI命令 `python -m rag_app worker`。API默认loopback；显式受托设置 `RAG_API_HOST` 和 `RAG_API_PORT` 供Compose选择 `0.0.0.0:8000`。host只接受有限合法IP，port1–65535，错误使用既有有限配置错误。配置来源不从任意HTTP Host/X-Forwarded-*推导。

## Tasks & Acceptance

- [ ] API使用受托绑定设置，仍校验精确Python/Uvicorn；默认保持安全loopback。Compose所需设置交主会话协调部署者。
- [ ] worker启动使用同一bootstrap/application做短DB检查，之后有限内存空闲等待，SIGTERM/SIGINT唤醒并释放runtime；不持Session/事务等待，不建额外业务表/后台队列，不做外部调用。
- [ ] 启动失败/DB失败/关闭失败保留原失败与清理诊断，仅输出有限安全码；现有check-database语义/测试保持。
- [ ] 验证配置正负例、CLI选择、实际Linux子进程启动/存活/TERM/INT退出与资源清理；PG检查未能实际执行时明确未执行，不以mock证明四服务通过。

Given受托bind配置，when启动API，then监听地址/端口与配置一致并可由同网关访问。Given合法DB与worker，when启动并TERM/INT，then持续运行后有限退出，等待间无活动事务。Given不兼容环境，when启动，then安全失败且不伪造ready。

## 环境与承接

只用Netcatty Linux精确3.12.8及A1有效锁，远程沿用原作者 `/opt/rag-story-1-1/backend-work`。测试证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1`。当前PG18.6/vector0.8.7若不可用，仍完成代码/可运行非PG测试，保留真实PG/四服务门。其他目录/Compose不动，缺部署接口报告主会话。本规格不关闭父AC或A2其余六项PG/迁移门。
