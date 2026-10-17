---
title: 'Story 1.1 D F8 构建输入隔离'
status: in-progress
route: dispatch
baseline_commit: a52ae3090948e7eeea6df87590f15ce35351d247
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-deploy.md
---

## Intent 与归属

只修 F8：API Dockerfile 的源码/迁移白名单重新纳入实际存在的 Python 缓存，破坏构建输入隔离。本轮运行和正式 Story 门仍未通过。

Russell 为唯一接替实现者，显式 `zayuapi/deepseek-v4.1-flash`，不传强度。只写 [api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1) 与 [D交付记录](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:1)。其他代码、测试、部署文件、Git index 和主控台账只读。旧 Bohr 已停止并关闭。

错误路由的恢复实例曾写入这两份草案，不能标为 DeepSeek 有效交付；主会话已保存模型和 hash。接替者须审阅实际内容并独立决定采纳或最小修正，保留来源说明，不删除用户或其他分段代码。

## Tasks & Acceptance

- [ ] Given `!src/**` 和 `!migrations/**`，when 目标源码树包含已观测的 `__pycache__`/`*.py[cod]`，then 后续 ignore 规则排除这些缓存和字节码，不影响批准的 Python 源码、锁、声明和迁移。
- [ ] Given 源码树中出现环境文件、私钥、pgpass、secrets 或 credential 工件，when 构建上下文匹配，then 精确排除真实敏感工件，保留合法 `.env.example/.sample/.template` 等示例；不读取真实秘密、不新增依赖或业务能力。
- [ ] 文档只追加 F8 当前作者、来源、规则和最终 hash/未执行项，不把 F5–F7 已静态复核或任何旧证据重标为新运行通过。
- [ ] 不删除本机缓存、不执行本机应用/导入/构建/测试或网络探测。固定 Gitee 提交/镜像缺失，真实 Docker context 与干净 Linux 重建保留 `not-executed`；交付后冻结并释放唯一写入。

不重新渲染 BMad。主会话随后安排独立静态复核；源码准备、静态复核与最终运行门分别记录，不替代父 Story 四 AC、A/B/C/D/E 或原完成分母。
