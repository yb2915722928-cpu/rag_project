# Story 1.2 B 共用 EgressTarget 交付说明

日期：2026-10-18（Asia/Shanghai）。
范围：仅限 B 分段（原 Story 1.2 AC3 的目标守卫与绑定连接端口）；父 Story 未完成。

## 依据与文件归属

实现前已完整读取[B 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-b-egress.md:1)
及其中列出的[公共契约](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-public-contracts.md:1)、
[C5 EgressTarget](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:105)
与[实施契约 §2.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ir-sp-review-2026-10-16/baseline/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:86)。
唯一写入的四件为：

- [领域值对象与端口](/E:/aaa-project/rag/backend/src/rag_app/modules/execution/egress.py:1)。
- [DNS/TLS/HTTP 适配器](/E:/aaa-project/rag/backend/src/rag_app/adapters/egress.py:1)。
- [专题测试](/E:/aaa-project/rag/backend/tests/test_egress.py:1)。
- [本交付记录](/E:/aaa-project/rag/docs/story-1-2-b-delivery.md:1)。

未修改依赖锁、入口、共享错误文件或其他实现者文件。

## 实现模型证据

实现会话 `01a14b4b-41ea-7bd0-9b61-0e9475aadae8`（Faraday，父会话
`01a14b42-689c-7533-90a3-9bd187d93039`）。主控已核并转告实际
`turn_context` 为 `zayuapi/deepseek-v4.1-flash`、`effort=max`，未传推理覆盖；
本记录只保留路由记录，不宣称底层供应方身份。

## 已交付行为

- `parse_config_target` 按 Unicode 码点限制 2048；`parse_signed_target`
  按 UTF-8 字节限制 8192。二者都只接受 `https`、可见 ASCII wire URL，
  拒绝 userinfo、fragment、控制字符、非法 host/port。
- `EgressProfile` 是精确 `host/port` 集合，不做后缀、子域或公共云通配；
  未知 host 或端口返回 `CONFIGURATION_INVALID`。
- `EgressTarget` 原样保留 path/query（含 `+`、`%2F`、重复参数、空值、
  末尾 `?`），不做解码、规范化或重编码。该字段 `repr=False`，仍是
  每次 call 的最少秘密，调用方不得写普通日志或持久账。
- `resolve_egress_plan` 每次只调用一次 resolver，保留全部 A/AAAA 并
  逐一检查；任一地址属于回环、私网、link-local、保留、文档/基准、
  metadata、IPv4-mapped、6to4、Teredo、NAT64、site-local 等，整次派发
  失败；空结果、resolver 异常、非法地址类型同样失败。
- `EgressPlan` 固定选定第一个已核地址；`TlsBoundConnector` 只连该 IP，
  不持有 resolver，不二次 DNS。TLS 以原准确 host 作 `server_hostname`，
  默认 `check_hostname=True`、`verify_mode=CERT_REQUIRED`；注入 context
  不满足时构造即拒绝。
- `OneShotHttpTransport` 单连接、单发送、单响应；HTTP/1.1，`Host` 由
  原 target 生成（默认 443 省略端口，IPv6 加方括号），`Connection: close`。
  3xx 原样返回，不读 `Location`、不跟随、不重试。
- `Authorization` 只能经 `EgressRequest.api_authorization` 提供，且仅
  `api` 用途允许；上传/下载在建立连接前拒绝。普通 headers 禁止
  `Authorization`、`Host`、framing 头、`Cookie` 等，禁止重复头与 CRLF 注入。
- 响应解析支持 `Content-Length`、`chunked`、无长度读至 EOF，以及
  HEAD/204/304 空体；响应头 64 KiB、100 项、body 默认 1 MiB 上界，
  超限或格式异常均为有限失败。
- 失败统一抛独立 `EgressError`，只含 `code`
  （`CONFIGURATION_INVALID`/`DEPENDENCY_UNAVAILABLE`）与有限 `failure`；
  不保存 URL、query、Authorization、响应 body 或原始异常对象，`str`/`repr`/
  traceback 链均无秘密。未修改共享 `SafeError`。

## 固定提交与环境

- 提交：`78402858fb003dfd62d57ed481f4f131e69424bf`
  （`feat: add guarded one-shot egress for Story 1.2`）。
- 服务器：Linux `VM-0-16-ubuntu` 6.8.0-124-generic x86_64，
  `/opt/rag-story-1-2/repo`，`origin` 仅 Gitee，`checkout --detach` 该提交。
- HEAD 复核一致，`git status --porcelain` 为空；未从 GitHub 拉取。
- 源码 SHA-256 与提交中的
  [source snapshot](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-b-source-snapshot.json:1)
  逐项一致：
  - `modules/execution/egress.py`：`6eb831c5ee88756797b76268ab11fb3a3af03efec2861a1218dd3863f30d757a`
  - `adapters/egress.py`：`de890142ea9f756d2fb218f5fafe685d2492683df858cb5761452e13620a00af`
  - `tests/test_egress.py`：`468099fbdc7aee2e51f2860c8b22a311313a4ebdd241763c99ba16b4e5e6a726`
- 锁文件 `backend/uv.lock`：`7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed`。
- 解释器 `/opt/rag-story-1-2/venv-dev/bin/python`：CPython 3.12.8，
  项目 `.python-version` 为 `3.12.8`，pytest 8.4.2，OpenSSL 3.0.15。

## 执行命令与结果

```bash
cd /opt/rag-story-1-2/repo/backend
env -i HOME=/root LANG=C.UTF-8 \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  /opt/rag-story-1-2/venv-dev/bin/python -m pytest \
  tests/test_egress.py tests/test_architecture.py tests/test_uow.py \
  -q -p no:cacheprovider \
  --junitxml=/opt/rag-story-1-2/evidence/B-7840285/junit.xml
```

结果：退出码 `0`，`169 passed in 1.24s`。

- 专题 `tests/test_egress.py`：153 项通过。
- 架构边界 `tests/test_architecture.py`：3 项通过。
- 共享 UoW/秘密边界 `tests/test_uow.py`：13 项通过。
- JUnit `tests=169`、`failures=0`、`errors=0`、`skipped=0`、`time=1.244`。

仅按主控指定的这 3 个文件运行；未执行 PG、迁移、四服务或全仓套件，
不把本结果扩展为父 Story 或全仓基线通过。

## 证据与归档

原始证据目录 `/opt/rag-story-1-2/evidence/B-7840285`，已复制归档到
`/fileOfRag/testOfRAG/metadata/story-1-2/B`：

| 文件 | SHA-256 |
| --- | --- |
| `junit.xml` | `c2d09fc9f41ace428717230569e84a0cb73b796fec02cc29a65fcf15218e3288` |
| `pytest.log` | `684dd59cb19f261b997e44dee2a7c0f2abea75c014c0c163d8ba20b876f37162` |
| `exit.txt` | `418a5c17f33c70e99b0cc0a07fce69191489cfedc94164bfa903785777c5bd4b` |
| `environment-and-source.txt` | `f5f1dde99ad08f317c960329ebd3e3265e003e89f2058120b6d612b367bef693` |

`environment-and-source.txt` 记录 UTC 时间、主机/内核、仅 Gitee 的 remote、
HEAD、干净工作树、上列源码与锁 hash、解释器/pytest/OpenSSL 版本及完整命令。

## 假件边界

本专题所有 DNS、TLS、HTTP 对端均为显式假件：`_Resolver`/`_FakeSocket`/
`_FakeContext`/`_Connector` 及 `monkeypatch` 的 `getaddrinfo`。
未向任何供应方、真实域名或公网地址发起连接，未读取真实证书或响应；
未验证真实供应方能力、真实限流或真实网络路径。

## 未完成与风险

- 父 Story 1.2 的 C 集成、真实 PG/child 链路、独立 Step 5 验证与全新
  `GPT-6.1 Sol / medium` 审查尚未执行；本分段不替代父 AC。
- 本文件尚未提交；三份源/测试文件自冻结后未再修改，服务器测试即对
  `78402858` 原样运行，无服务器侧改动。
- 未验证真实 DNS 轮转、真实证书链、真实代理/防火墙或大文件流式下载；
  这些属于实际接入阶段，不在本条假件范围。
