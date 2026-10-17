---
title: 'Story 1.1 A2a worker 临时改动归位'
status: in-progress
route: dispatch
baseline_commit: a52ae3090948e7eeea6df87590f15ce35351d247
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-runtime-entrypoints.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-amelia-control-2026-10-17.md
---

## Intent

保持原 A2a 的 Linux worker 生命周期，在不新增 Windows 运行支持的前提下处理主会话误加的 pipe fallback 与测试改动。本子规格不替代原 A2a、父 Story 四项 AC 或 PG/Linux 门。

## Code Map 与归属

唯一实现者使用 `zayuapi/deepseek-v4.1-flash`，不传推理覆盖。只允许修改 [worker.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/worker.py:1)、[test_runtime_entrypoints.py](/E:/aaa-project/rag/backend/tests/test_runtime_entrypoints.py:1) 和新增对应交付记录 `docs/story-1-1-worker-reconcile-delivery.md`。

从 `git diff` 识别主会话新增 `_make_wakeup_pipe()` 及测试工厂替换；可以修正或撤销这几行本轮临时改动，不能回退用户或其他作者修改。CLI、公共模型、其他测试、锁、部署及主控台账均只读。

## Tasks & Acceptance

- [ ] 先判断原 Linux self-pipe、signal wakeup 和有限关闭语义，不以 Windows 缺少 `pipe2` 判定 Linux 产品缺陷。选择最小修正；任何保留的 fallback 必须真正满足目标语义，不能靠 mock 宣称 Windows 真实进程可用。
- [ ] Given Linux 精确 CPython 3.12.8 和已通过库检查，when worker 空闲及收到 SIGTERM/SIGINT，then 检查事务已结束、进程持久空闲并有限退出，恢复 handler/wakeup fd、关闭描述符和 engine。不得增加业务调度。
- [ ] Given build/check/close 等错误，when 清理发生，then 保留主 SafeError、私密 diagnostic cause 与 cleanup errors，CLI 只输出有限消息。测试不能把目标平台以外的失败改为错误业务结论。
- [ ] 维护可审阅测试变化与交付记录。所有应用运行/测试按 AGENTS 仅在 Netcatty Linux；GitHub/Gitee 未有相同可取 commit 时只完成源码准备，记录 `not-executed`。不本地运行、不重试认证/SFTP/镜像、不提交或推送。

## 依赖与交付

主会话已进入 bmad-build Step 3；无需重新渲染。远程正式执行等待主会话提供经 Gitee 拉取和源码 hash 核对的固定 commit。旧 Windows `466 passed / 13 skipped` 仅补充观测。

交付需列出实际修改、逐项状态、准确 hash、未运行原因和所需触发条件；主会话随后组织 Step 5 独立验证及全新 6.1 Sol/medium 审查。发现需越界修复时报告接口问题，由主会话协调。
