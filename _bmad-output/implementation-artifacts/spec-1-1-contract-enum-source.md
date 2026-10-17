---
title: 'Story 1.1 B 枚举真源与准备闭合'
status: done
route: dispatch
baseline_commit: a52ae3090948e7eeea6df87590f15ce35351d247
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-contracts-dispatch.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-contract-models.md
completion_record: E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md
---

## Intent

完成 B 生成器的源码准备，使 C2 的 `status/outcome/operation_state/job_state` 区分可验证，保持后端为唯一真源。只准备，不绕过固定提交的 Linux 开发者测试、正式生成或父 Story 门。

## 归属与接口

当前 Boole 为唯一作者，模型 DeepSeek 默认。继续独占 `contracts/**` 与 `docs/story-1-1-contracts-delivery.md`；本次额外只认领 [public.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/public.py:1)、[test_public_contracts.py](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:1)。二者历史作者已释放，无其他当前写者。

后端保留原 `PUBLIC_MODELS`、17种 DTO、校验与 HTTP 兼容性。在同一真源提供 `PUBLIC_ENUMS` 索引，直接引用已存在的 Status、Outcome、OperationState、JobState、RetryMode 类型；不再定义一套枚举，不把 enum 塞入依赖 `model_fields` 的 DTO 索引。生成器读取 DTO 索引及枚举索引，通过 Pydantic schema/TypeAdapter 导出，TypeScript 仍由生成 schema 得到。

## Tasks & Acceptance

- [x] Given 后端现有枚举，when 读取 PUBLIC_ENUMS，then 类型身份与原类一致，wire值不变；保持 PUBLIC_MODELS 及五种维护 HTTP Response 选择不变。
- [x] Given 导出准备和样例，when 后续在固定 Linux commit 执行，then JobState wire合法/非法样例可由后端原枚举验证，TS/schema不复制枚举值；四类状态含义不混同。
- [x] `comparison.v1` 业务载荷按原按需增量规则延期，不伪造通过，也不因未来 Story 尚无业务模型而让本条必需样例永久失败。job_state、非BMP、HTTP错误及H等本条必需样例不能按此规则延期。
- [x] 引用的样例文件、索引和后续命令完整可审阅；正式 OpenAPI/schema/TS 尚未生成需写清楚。未获同一 Gitee commit 前不执行应用导入、测试或生成，不提交、不重试外部阻塞。

## 交付

交付列出文件/hash、真实修改、未执行项、后续 Linux 命令与缺失条件。主会话冻结补丁后组织独立复核；此前 Windows 观测不覆盖本增量，完整 B0a/B0c 及父 Story 验收分母不变。
