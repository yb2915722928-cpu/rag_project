---
title: 'Story 1.1 B0a 公共模型真源'
status: done
route: dispatch
baseline_commit: NO_VCS
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md
completion_record: E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md
---

## Intent

交付可导出的 C1/C2 最小公共模型，供后续 H/HTTP 和 contracts 导出使用，不实现未来业务。

执行上下文：主会话已成功渲染 bmad-build 并进入 Step 3；本任务是该步骤的实现 handoff，不再次启动技能工作流。RTK 沙箱拒绝应按工具规则请求 escalation。Netcatty 同一 session 只能有一个命令；忙碌时可在同一已保存 host 开本任务独立 terminal，核实际 ID，结束释放自己创建的会话。

## 唯一归属与接口

仅新增/修改 `backend/src/rag_app/contracts/public.py`、`scalars.py`、`backend/tests/test_public_contracts.py`、`docs/story-1-1-contract-models-delivery.md`。禁止改 API、errors、配置、锁、迁移、其他测试及公共状态。A1 同时修改其他后端文件。以 Pydantic 为线协议边界，不让领域导入框架。

`public.py` 公开 `PUBLIC_MODELS` 名称→模型映射和各模型；`scalars.py` 公开标量计数/切片、稳定序列化及必要注解类型。HTTP 后续读取该映射纳入 OpenAPI，不手写第二套 schema。

## Tasks & Acceptance

- [x] 稳定 ID 为1–64 ASCII字母数字下划线连字符；UTC Z时间；拒孤立 surrogate，码点计数/半开区间与非BMP一致；默认不 trim/NFC/换行重排；稳定 UTF-8 键序列化，禁非有限数字。
- [x] 全部公共模型拒未知字段/版本；按需显式区分缺省与 null。有限十进制金额、未知 usage 为 null+unknown，不用浮点累加。
- [x] 扁平公共包、有限错误（code/message/http_status/retry_mode/白名单details）、202/完成/失败/GET operation/retrieval 最小载荷；status、outcome、operation_state、job_state 分离；retrieval 至多五块；202 无半答案。
- [x] 仅建安全 DTO/样例，不编业务表/权限/供应方；完成/202/失败的字段与状态一致性必须校验，受控 status_url 不接受任意 URL。错误/未认证投影不泄私有 operation ID、无权目标或上游正文。
- [x] 增加正负模型测试，运行开发者测试并保存结果；给 H/导出者列准确模型名称及调用方法。

Given 中文/组合字符/emoji，when 跨端序列化或切片，then 标量长度和原值保持。Given 未知字段、孤立 surrogate、非法 ID、枚举或互斥字段组合，when 校验，then 有限失败。Given 安全错误，when 导出，then 仅有限白名单。

## 环境

运行仅 Netcatty Linux、精确3.12.8；先 get_environment。独占 `/opt/rag-story-1-1/contract-models-work`，不得修改其他远程目录/Compose。A1 正在准备锁/隔离解释器，未就绪可先交代码并报告等待，不能本地运行或静默换版本。证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1`。普通日志不含秘密/正文。

## 依赖与承接

本规格不依赖 A1 文件修改；HTTP 接入/H 与生成物由后续规格承接。父四AC及 A/B/C/D/E、真实PG和独立验证/审查全部保留，不将模型测试记成完整 B 通过。
