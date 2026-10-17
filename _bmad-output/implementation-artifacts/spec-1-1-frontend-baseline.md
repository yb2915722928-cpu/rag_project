---
title: 'Story 1.1 C 可构建的前端基线'
status: draft
route: dispatch
baseline_commit: 0b576b65d3824e7f4319c39c38e80398caf08fb8
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/docs/story-1-1-frontend-standards.md
  - E:/aaa-project/rag/contracts/README.md
  - E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md
---

## Intent 与前置

交付AC1的Vue骨架、健康状态页及可复现构建。只有主控确认B正式生成、检查、52条样例和B0a/B0c通过后才派发本规格；当前draft不表示已满足依赖。

## 唯一归属

Kimi K3默认，独占 `frontend/**`、`docs/story-1-1-frontend-standards.md` 与 `docs/story-1-1-frontend-delivery.md`。不改backend/contracts/deploy或主控状态，不自行Git提交推送。后端DTO仅使用B的生成物。

## Tasks & Acceptance

- [ ] Given已批Vue栈，when编码前实读适配版本的GitHub官方规范，then补记URL、文件、tag/commit、日期及采用规则，保留原C0历史；GitHub不可达如实阻塞。
- [ ] Given官方create-vue3.23.0，when初始化frontend的TS/Router/Pinia骨架，then锁定技术seed实际依赖与非optional peer；Node24.22.0官方工件核hash，应用安装/构建/测试仅在Netcatty Linux。来源/许可证与脚手架改造边界可复核，不保留无关模板演示或提前业务页面。
- [ ] GivenB生成物，when前端类型检查，then覆盖 `contracts/typescript/*.ts` 并使用其公共类型，不写平行DTO。健康页只展示前端加载和同源 `/health` HTTP可达性；不得把HTTP200描述为数据库就绪或业务成功。
- [ ] Given首载或手动刷新，when请求成功、失败、超时或取消，then状态准确、无无限重试，控件可用且错误不展示原始私有正文/URL；必要状态有开发者测试。
- [ ] GivenDESIGN浅色系统字体/Element Plus与token，when真实浏览器在320/768/1440 CSS px、200%缩放及键盘操作，then主操作、错误和状态可读可达，无全页横溢；保存真实页面/控制台/网络证据，不以静态截图替代交互。
- [ ] Given本地完成的源码/锁，when主控统一发布两远端同一提交、服务器仅从Gitee固定检出并核源码hash，then执行锁定安装、类型检查、构建、测试，交付dist/hash给D。需返修则本地修改并由主控重新发布，不远程改源码后冒充固定提交通过。

## 环境与交付

Netcatty先get_environment，项目活动目录在 `/opt/rag-story-1-1` 的Linux本地文件系统；测试与最终证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1/frontend-baseline`。浏览器访问方式由主控协调，不改全局代理或公开额外服务。

报告准确commit、文件/hash、依赖/peer、Node/npm及官方来源、全部命令/计数、浏览器证据和未通过项。D四服务、真实PG、E及独立验证/审查仍保留。
