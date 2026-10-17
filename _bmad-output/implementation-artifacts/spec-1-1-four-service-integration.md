---
title: 'Story 1.1 D 四服务实际集成'
status: in-progress
route: dispatch
baseline_commit: abcd79beaa3997e78a37e49df69d14f867ed52cf
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-deploy.md
  - E:/aaa-project/rag/deploy/offline-images.md
---

## Intent 与归属

Mencius继续独占 `deploy/**`、`docs/story-1-1-deploy-delivery.md`、`docs/story-1-1-official-image-access.md`，完成父AC1/AC3四服务集成；不改backend/contracts/frontend，不自行Git发布。已有基础镜像、PG八项及B通过证据复用，不追加通用硬化、工具打磨或重复环境探测。

当前terminal时段归Singer，先做不占terminal的本地准备。前端正式dist/锁与commit交付后，主控提供准确版本及调用时段再运行。脚本改动仍由主控先发布到GitHub/Gitee，服务器仅从Gitee固定检出后执行。

## Tasks & Acceptance

- [ ] Given同一固定源码、C的dist/hash和已核准确基础镜像，when实际构建，thenAPI/worker同一镜像，gateway仅静态前端，PG为18.6/vector0.8.7，Python3.12.8/Uvicorn0.37.0；记录完整输入/镜像标识，不用浮动tag或占位digest。
- [ ] Given原四服务契约，when预检/迁移/启动，then秘密文件权限及非root应用入口正确，PG/活动锁用Linux本地FS，bucket只存材料/证据；不覆盖旧宿主目录、不删其他项目或桶，不预建后续业务表或生产vector(D)。
- [ ] Given当前已有入口与公开dist，when联调，then真实API/worker可运行，健康只证明liveness；网关阻断维护探针，私有及自产错误no-store，公开hash资源仅成功响应可immutable，条件请求/错误不泄秘密或私有资产。JSON/原件PUT预算按原分界验证，不要求后续未实现上传业务提前完成。
- [ ] Given实际进程/数据，when停止、重启并核持久性，then有限退出、连接/锁释放、当前数据保留且版本不变；只管理本任务资源。已有PG八项不重复，除非新配置或真实失败需要相关回归。
- [ ] Given固定Git/锁与工件，when在隔离干净Linux工作目录重建，then正常locked依赖与真实BuildKit/context检查可复现。缓存、秘密、无关材料不入构建输入；保留真实边界，不把FROM版本探针或pull=false当完整应用重建。
- [ ] Given实际运行依赖与工件，when补E来源记录，then发布方/缓存传输、许可证/上游改造边界、依赖/原生层及hash/digest准确；只记录当前确实使用的内容，不扩展未来供应方或目标性能验收。

## 交付

提交实际文件/hash、命令/退出码、四服务版本和生命周期、网关/构建输入证据及未完成项。活动与构建在 `/opt/rag-story-1-1` 本地FS，最终证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1`。完成这些已定义项目后交独立验证/全新审查，不自行再开额外审查轮。
