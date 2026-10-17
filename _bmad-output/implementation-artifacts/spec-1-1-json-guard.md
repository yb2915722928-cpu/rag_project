---
title: 'Story 1.1 B0b H 有界 JSON'
status: done
route: dispatch
baseline_commit: NO_VCS
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md
completion_record: E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md
---

## Intent

实现实施契约3.5的H协议防线，供后续维护HTTP入口调用。主会话已完成 bmad-build Step3；这是实现 handoff，不重新运行技能工作流。

## 文件归属与接口

仅写 `backend/src/rag_app/entrypoints/json_guard.py`、`backend/tests/test_json_guard.py`、`docs/story-1-1-json-guard-delivery.md`。不改API、配置、errors、锁、其他模型/测试/迁移。公开 `JsonLimits`、`BoundedJsonError`（有限code/message，不保存或外序列化原文）、`parse_json_bytes(raw, limits)`、`read_bounded_json(request, limits)`；HTTP后续映射有限错误并以公共Pydantic模型拒未知字段/版本。

## Tasks & Acceptance

- [x] 默认H：JSON实际流≤1048576字节、头≤16384字节；UTF-8、application/json可带UTF-8 charset、Content-Encoding缺省/identity；不只信Content-Length。
- [x] 单根object、深度≤8、节点≤8192、每object键≤64、每array项≤1024、每string≤65536标量、全部string≤131072标量。键也计入字符串预算，节点算法与深度定义写清；默认根object深度1，标量也是值节点。
- [x] 边读/词法解析边限界，在调用任何通用无界JSON加载前阻断结构/字符串超界；处理字符串转义/合法代理对、跨chunk多字节、重复键（含转义同键）、非法UTF-8/孤立surrogate/非有限数，拒尾随垃圾、超长数字或浮点溢出。不能先完整 json.loads 再数节点。
- [x] 明确1MiB只用于JSON入口，不作为原件二进制PUT入口中间件；累计读取有限，不回显请求体、原始异常、秘密或URL。
- [x] 覆盖各恰等上限/超一正负例、嵌套转义/非BMP/节点/重复键/错误编码/断流/实际字节越界；包括内容长度伪报与小chunk切边，验证有限错误及无日志泄漏。

Given 合法边界JSON，when 同步或流式解析，then 结果一致且保留原始解码值。Given 任何H超界或编码/结构错误，when 解析，then 在超界处有限失败且未调用无界后处理。Given 原件PUT，when 未调用此适配器，then 不受JSON界误伤。

## 环境与交付

运行只用Netcatty Linux精确3.12.8；同host可开独立任务terminal，不能争用忙session。独占 `/opt/rag-story-1-1/json-guard-work`，证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1`。A1正准备Python与有效锁，尚不可运行时可完成代码/上传并保留未执行，不换目标版本或本机运行。不操作其他Compose/目录。报告文件、运行命令、真实结果与未执行；RTK沙箱拒绝按工具规则请求escalation。

## 承接

H/HTTP接入、OpenAPI注册、错误投影、B导出与浏览器由后续协调；父Story四AC和所有验收分母不减。
