---
title: 'Story 1.1 C0 前端规范前置'
status: done
route: dispatch
baseline_commit: NO_VCS
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md
  - E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md
completion_record: E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md
---

## Intent

完成前端实现前强制的GitHub规范实查与版本/构建环境核验。B契约尚未完成，当前只做前置记录，不初始化或实现前端，不写平行类型。主会话已进入 bmad-build Step3，这是其中一项前置 handoff，不重复渲染工作流。

## 唯一归属

仅写 `docs/story-1-1-frontend-standards.md`。不得修改应用、测试、锁、公共规格/状态、backend/contracts/deploy。后续C实现由主会话读B交付后另发短规格，可复用本实例。

## Tasks & Acceptance

- [x] 确认当前工作区与已批栈：create-vue3.23.0、TS/Router/Pinia、Element Plus，浅色/系统字体/tokens服从DESIGN。技术seed列的版本是待运行核验对象，不以历史声明冒充新查。
- [x] 编码前到GitHub打开Vue/create-vue、Router、Pinia、Element Plus等官方或维护规范，记录准确URL、所读文件、tag或完整提交标识、查阅日期2026-10-17、拟采用规则及其对本Story的具体适用。只记实际读到内容，GitHub不可达原样留阻塞，不杜撰。
- [x] 核查官方create-vue3.23.0模板、依赖范围与peer、Node24.22.0官方工件及hash来源；不可得不静默换版。只做读取/来源查询，本阶段不安装构建依赖。
- [x] 报告后续C需从B导出的准确接口；当前无B生成物时明确等待，不自写业务类型。前端只骨架/健康状态，不提前身份、文档或问答业务。

Given已批设计与官方规范，when记录前置，then每条采用规则都有实际文件/版本证据且不覆盖产品契约。GivenGitHub或精确版本不可取得，when查询，then记录原始失败与影响，不宣称已参考。GivenB未完成，when前置结束，then交回记录等待C派发，不抢写应用。

## 环境

后续运行/构建/测试只走Netcatty Linux精确工具链。本阶段可只读现有连接；需命令且原session忙时可对同一host开独立任务terminal，结束关闭自建会话。未来远程C目录预留 `/opt/rag-story-1-1/frontend-work`，不要改其他目录/Compose或清理Docker。证据最终归档 `/fileOfRag/testOfRAG/metadata/story-1-1`。RTK沙箱拒绝按工具规则请求escalation。
