---
title: '1.2 B 共用 EgressTarget'
type: feature
created: '2026-10-18'
status: in-progress
route: dispatch
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

交付原 Story 1.2 AC3 的可复用目标守卫及绑定连接端口，只用显式 DNS/TLS/HTTP 假件证明，不向供应方实际外发。权威为共享 C5 最后一段，禁止假件结果被当成真实能力准入。

## Boundaries & Constraints

仅 HTTPS，拒 userinfo/fragment；配置 URL≤2048 码点、签名 URL≤8192 UTF-8 字节。用途 profile 使用精确 host/port 允许表，不用后缀信任上游返回域。每次派发取全部 A/AAAA，任何非公网/回环/私网/link-local/保留/metadata 地址均拒绝；空 DNS 失败。连接只用本次已核 IP，不二次 DNS，TLS 使用原准确 hostname 校验/证书验证，HTTP Host 正确。

禁自动重试/redirect；3xx 不跟随。签名 query 原样保留但不写普通日志/账；API Authorization 只用于已核 API host，不转交上传/下载 host。child 只能取得该 call 所需有限秘密。异常有限为 DEPENDENCY_UNAVAILABLE 或配置子码，无完整 URL/secret/响应 body 泄漏。

## Tasks & Acceptance

- [ ] [领域egress](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/egress.py)定义无框架值对象和端口；[egress适配器](/E:/aaa-project/rag/backend/src/rag_app/adapters/egress.py)实现解析、DNS校验和绑定连接；对外接口先回报主控供C使用。
- [ ] [test_egress.py](/E:/aaa-project/rag/backend/tests/test_egress.py)覆盖准确允许表、长度、混合A/AAAA、DNS变化、TLS主机和地址绑定、redirect、凭据分域/秘密哨兵。
- [ ] [B交付文档](/E:/aaa-project/rag/docs/story-1-2-b-delivery.md)记录命令、固定提交/hash、假件边界与结果。

## Acceptance Criteria

- Given 合法配置/签名 URL 与公网 DNS，When 验证并连接，Then query 保留、仅已核 IP 被使用且 TLS/Host 为原 host。
- Given 非法 scheme/host/port、userinfo/fragment、超界 URL 或任一不安全 DNS，When 派发，Then 无连接并安全失败。
- Given 检查后 DNS 改变、redirect 到其他 host、签名下载，When 传输，Then 不重解析/不跟随/不转发 API Authorization。
- Given 带哨兵 URL/secret 的失败，When 捕获 argv/log/异常输出，Then 无秘密；受守卫失败的真实调用始终阻断。

</frozen-after-approval>

## Code Map

有限错误遵守 [errors.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/errors.py)的既有边界，B按公共契约使用独立EgressError；领域不导入框架/HTTP SDK。C4资格与调用账由A/C负责，目标守卫不能绕过它们。

## Implementation Notes

唯一 DeepSeek 默认；只写 Tasks 列举的四个文件，不改依赖锁/入口/其他实现者文件。第一阶段只读并回报对外签名，等待主控核实际模型后发送 `IMPLEMENTATION_MODEL_RELEASE` 才写入。接口需让 C 的受监督单 call 使用；可以实现生产连接构件，但 S0 运行入口显式禁真实供应方。主控同步 GitHub/Gitee 后，分配 Netcatty Linux 开发者测试时段。

主控已核实际模型并登记 [公共契约](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-public-contracts.md:1)：独立有限 EgressError、不修改共享错误文件；可见ASCII wire URL、原样query；选定一个已核IP、无自动回退；C复用OneShotHttpTransport。收到release后直接编码，代码冻结后等待主控发布固定提交；本地不运行应用/测试。

## Spec Change Log

## Review Triage Log

## Verification

Linux 运行本专题与架构/秘密相关回归；验证 DNS 与网络边界用可控假件，不联网探测实际供应方。本规格完成仍须父 Story 集成、独立验证与审查。
