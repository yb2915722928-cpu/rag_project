# Story 1.1 B 段公共契约交付规格

日期：2026-10-17。该规格只拆分实现上下文，不减少 Story 1.1 原始 AC；父 Story 的四项 AC、真实运行门和独立验证仍必须完成。

## 目标

在 `contracts/**` 交付后端单一来源导出的 OpenAPI、JSON Schema、TypeScript 类型和正负边界样例，供前端与 HTTP 验证复用。契约必须服从现有架构的 C1/C2、实施契约 3.5 和后端实际模型；不维护第二套手写业务类型。

## 输入与约束

- 读取 `AGENTS.md`、`spec-1-1-rebuildable-modular-project.md`、`story-1-1-delivery-plan.md`、`deferred-work.md`、`epic-1-context.md`、架构 `shared-contracts.md`、实施契约及现有 `backend/src/rag_app/**`。
- 唯一写入范围：`contracts/**`。不得修改 `backend/**`、`frontend/**`、`deploy/**`、测试、锁文件或迁移；若导出必须改后端，停止并报告所需接口，不自行越界。
- 保留未知字段拒绝、有限错误、私有 ID 保密、UTC RFC3339、十进制金额和 `no-store` 语义。1 MiB JSON 限制不适用于原件 PUT。

## 必须交付

1. 可复现的 OpenAPI 文档、按能力拆分的 JSON Schema、由导出结果生成的 TypeScript 类型和版本/生成说明。
2. C1 样例：中文、组合字符、emoji/非 BMP、孤立 surrogate 拒绝、标量码点长度与半开偏移、显式 null/缺省、稳定键序列化、重复键/NaN/Infinity/未知字段拒绝。
3. C2 样例：公共包扁平字段、`status`/`outcome`/`operation_state`/`job_state` 分离、202/失败/GET operation/retrieval 边界、有限 `error` 与 `retry_mode`，不得回传未认证私有 operation ID。
4. 实施契约 §3.5 的 H 正负边界：JSON 字节、深度、节点、重复键、编码和未知字段均有界；明确 1 MiB JSON 与原件 PUT 的分界，并提供有界 HTTP 测试入口或可执行样例。

## 验收

- 生成物可由仓库命令重建且互相一致；TypeScript 只能由 schema/导出结果生成。
- 正负样例覆盖上述边界，测试不会把 skipped、静态检查或假件当作真实 PG/Linux 验收。
- OpenAPI 与 JSON Schema 不泄露秘密、正文、签名 URL、任意上游 body 或无权目标；错误字段为有限白名单。
- 最终报告列出变更文件、生成/校验命令、通过与未执行项；提交前不修改本规格的原始 Story AC。
