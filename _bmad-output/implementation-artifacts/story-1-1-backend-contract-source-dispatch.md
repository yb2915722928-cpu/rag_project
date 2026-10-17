# Story 1.1 后端契约真源前置规格

日期：2026-10-17。该规格是 Story 1.1 B contracts 的后端前置，不减少父 Story 的原始 AC、A/B/C/D/E 义务，也不把静态代码结果当成真实 PG/Linux 验收。

## 目标

补齐后端可导出的公共契约真源，使后续 `contracts/**` 能从后端模型和入口生成 OpenAPI、JSON Schema、TypeScript 与正负样例。公共模型必须来自后端源代码，不能让 `contracts/**` 另写一套业务 schema。

## 上下文

- 读取 `AGENTS.md`、A 段规格、父 Story 交付计划、`deferred-work.md`、`epic-1-context.md`、架构 `shared-contracts.md`、实施契约及现有 `backend/src/rag_app/**` 和测试。
- 当前只有 `/health`、`HealthStatus` 和二字段安全错误；缺少 C1/C2 公共响应模型、能力/operation/retrieval 的最小模型、有限错误字段和 H 有界 JSON 解析入口。

## 文件归属

- 唯一写入范围：`backend/src/rag_app/**` 及为该范围增加的 `backend/tests/**`。不得修改 `contracts/**`、`frontend/**`、`deploy/**`、`backend/uv.lock`、迁移或文档证据。
- 入口必须保持领域/应用不依赖框架和 ORM 的既有边界；不引入 SQLite、真实供应方、队列或业务持久表。

## 必须交付

1. 严格拒绝未知字段的 C1/C2 Pydantic 模型：稳定 ASCII ID、UTC RFC3339、Unicode 标量长度/半开偏移所需的校验边界、显式 null 与缺省、稳定序列化、有限状态枚举。
2. 公共 HTTP 包与安全错误模型：`schema_version`、`request_id`、`status`；operation 完成/202/失败/GET/retrieval 所需字段；`http_status`、有限 `retry_mode`、白名单 `details`；不回传秘密、正文、签名 URL、任意上游 body 或未认证私有 operation ID；私有响应 `Cache-Control: no-store`。
3. H 有界 JSON 请求解析能力，至少可配置并测试字节、UTF-8、深度、节点、重复键、非有限数字和未知字段边界；明确 1 MiB JSON 与原件 PUT 不同的入口语义。解析失败使用有限错误，不把原始异常/请求体写入响应或普通日志。
4. 为上述模型和入口补充后端单元/HTTP 测试；测试不能依赖真实 PG，真实 PG 门仍由 A 段单独执行。

## 验收

- 后端测试覆盖正负边界且通过；现有测试回归通过或明确报告未执行原因。
- `create_app()` 的 OpenAPI 可读取这些公共模型；不会通过第二套手写 schema 绕过后端真源。
- 仅修改允许范围；报告实际文件、命令、通过/未执行项和剩余真实 PG/Linux 环境门。
