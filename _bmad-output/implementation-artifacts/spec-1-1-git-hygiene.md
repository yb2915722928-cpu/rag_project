---
title: 'Story 1.1 Git 初次提交范围'
status: in-progress
route: dispatch
baseline_commit: NO_VCS
context:
  - E:/aaa-project/rag/AGENTS.md
---

## Intent

用户2026-10-17明确授权本地开发、推送新仓库rag_project、服务器拉代码。主会话已初始化main，远端待GitHub登录；本任务只准备忽略和首提交范围，不操作Git元数据、不提交或推送。

## 唯一文件归属

仅修改根 `.gitignore` 并新增 `docs/story-1-1-git-publish-scope.md`。主会话维护项目规则及relay，其他实现者修改后端/部署/公共模型。无需重启bmad-build；不写应用/测试/部署脚本。

## Tasks & Acceptance

- [ ] 阅读现有忽略文件与文件清单，为虚拟环境、uv/npm缓存、node_modules、测试临时输出、生成渲染目录和本地秘密材料（.env、凭据、私钥、pgpass等）补精确忽略规则；保留合法示例、依赖锁、源代码和必要部署声明。
- [ ] 只读检查将被纳入Git的候选文件；不输出任何疑似秘密值。用文件名/分类报告，必要时说明缺乏真实秘密扫描证据。不要删除/移动现有文件或修改别的配置。
- [ ] 在交付文档列首提交建议allowlist和实际 `git check-ignore` 核对结果；根个人学习/访谈材料与无关用户资料不自动上传，源/锁/项目规格/必要规划及开发证据按实际范围列出。仅忽略构建产物，不用规则掩盖未交付的源码。

Given本地开发文件，when检查初次提交范围，then缓存/运行环境/秘密不被候选包含，锁与源码仍可版本化。Given明确来源/凭据问题，when报告，then只输出安全元信息，不声称仓库已经创建或推送。

## 验证与限制

这是低风险维护，不新增测试；只运行本地只读Git/文件检查。RTK沙箱拒绝按工具要求escalation。GitHub账户创建、认证与git init/commit/push由主会话负责，本任务不碰远端或运行项目代码。交付列实际文件、检查与剩余项，不改Story完成门。
