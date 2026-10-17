---
title: 'Story 1.1 B0c 有界维护 HTTP 与 OpenAPI'
status: done
route: dispatch
baseline_commit: NO_VCS
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-backend-contract-source-dispatch.md
completion_record: E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md
---

## Intent

把后端公共模型与已测试H适配器接为仅隔离夹具使用的维护HTTP入口，并使create_app的OpenAPI可导出同一模型。主会话已在bmad-build Step3，不重新启动技能。

## 文件归属和接口

仅 `backend/src/rag_app/entrypoints/api.py`、新增 `entrypoints/contract_probe.py`、`backend/tests/test_contract_http.py`、`docs/story-1-1-contract-http-delivery.md`。不改其他模型/H解析器、配置、CLI、锁、迁移或其他测试；原A1的API测试必须继续通过。公模作者正补有限H/运行错误字典，变更由主会话协调。

在 `create_app(settings=None, *, contract_test_token=None)` 接收明确的内存SecretStr测试令牌；默认None时维护入口拒绝，不能从production配置隐式开启。注册 `POST /__maintenance/contracts/{model_name}`，从 `PUBLIC_MODELS` 仅选择含C2公共包的五种Response；Money/Usage等辅助DTO只导出schema与直接模型样例，不作为无公共包的HTTP响应。令牌从固定 `X-RAG-Contract-Test` 头核验（恒时比较），不授业务权限、不写库、不调用供应方。私有网关不得外放该路径。

## Tasks & Acceptance

- [x] JSON入口使用 `read_bounded_json`，先H有限协议再测试令牌/模型校验；不用request.json/body或框架先无界装载。未知字段/版本由单一公共模型拒绝。
- [x] 仅已授权夹具可校验/返回对应DTO；Accepted夹具202，Failed按error.http_status，Operation夹具200即使原error存在，其他200。未认证/未知路由/错误不回传私有operation ID。说明这是无业务副作用的DTO探针，不冒充真实operation服务。
- [x] H错误映射公模有限字典；ValidationError只投影有限码，不序列化exc.errors输入。保留既有SafeError有限code及503兼容性，补C2 envelope；意外异常也不泄秘密/正文/traceback。
- [x] 私有成功/失败/404/405等均no-store，删除私有验证器/304语义；每HTTP尝试新request_id，不信任客户端诊断ID。健康liveness现有返回兼容。
- [x] OpenAPI从PUBLIC_MODELS/后端model_json_schema生成components与维护入口请求/响应引用，不维护平行业务schema。create_app默认配置也能导出模型，schema不含令牌。
- [x] HTTP正负例含默认关闭、令牌缺失/错误、超界/重复键/编码/未知字段/版本、非BMP/null/202/失败/GET投影语义、无秘密日志/响应及新request_id。远程精确3.12.8运行开发者测试，未执行保留未执行。

Given隔离令牌和合法夹具，when通过HTTP，then返回契约一致且无DB/外发副作用。Given未授权或畸形输入，when请求，then有限错误/无私有ID/no-store。Given导出，when读取OpenAPI，then同一后端模型成为真源。

## 运行与承接

用户改为Git推送/服务器拉固定提交；主会话统一Git，本任务先本地实现，Git认证未就绪不重试SFTP或改通道。可只读复用H源；后续验证独占 `/opt/rag-story-1-1/contract-http-work`，证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1`。不能修改其他活动目录/Compose。开发者测试后才供B正式生成；父AC、PG、四服务与独立门不减。
