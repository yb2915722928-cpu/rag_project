- source_spec: `E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-rebuildable-modular-project.md`
  summary: 导出公共 contracts 的 OpenAPI、JSON Schema、TypeScript 类型及正负边界样例
  evidence: Story 1.1 同时要求可重建服务骨架和完整契约交付；契约可独立生成、验证和评审，拆分后降低首轮规格上下文风险。
- source_spec: `E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-rebuildable-modular-project.md`
  summary: 建立依赖、镜像、上游样例、许可证、hash/digest 与改造边界的完整 provenance 台账
  evidence: Story 1.1 的运行骨架可先依赖锁文件和镜像摘要重建；完整来源与许可证证据是独立可审计交付，拆分后不阻塞本轮启动基线。
- source_spec: `E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-rebuildable-modular-project.md`
  summary: 创建 create-vue 3.23.0 的 TypeScript、Router、Pinia 前端 starter 并锁定 Node 依赖
  evidence: 前端 starter 可独立构建和评审；当前首轮聚焦后端、真实 PG/pgvector 与四服务部署，拆分后减少实现者同时处理两套工具链的上下文负担。
- source_spec: `E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-rebuildable-modular-project.md`
  summary: 交付 gateway、API、worker、PG 四服务 Compose 编排、最小权限挂载与完整启动停止生命周期
  evidence: 四服务部署可在后端基线完成后独立构建和验收；当前规格保留后端与真实 PG 迁移，延期部署可降低首轮实现范围。

## 2026-10-17 归属澄清（保留原拆分记录）

以上四项仍属于原 Story 1.1 的必需交付，不是可无限推后的范围排除。每项归属、依赖与验收门见 [父Story交付计划](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-delivery-plan.md:1)。原条目中的“当前轮包含四服务”是第一次拆分时的历史说明，后续拆分已改变实施批次，不改变父Story AC。四项未完成前不得标1.1完成或放行1.2。
