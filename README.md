# rag_project

RAG_all 模块化项目。当前正在实现 Story 1.1；仓库快照不代表父 Story 验收通过。

## 开发与验证

代码在本地开发并推送本仓库，Netcatty 连接的 Linux 服务器拉取明确提交后安装、构建和测试。使用精确 CPython 3.12.8；后端依赖由 `backend/uv.lock` 锁定。

```sh
cd backend
uv sync --locked --python 3.12.8
uv run --locked python -m pytest tests -q
```

普通测试成功不能替代真实 PostgreSQL 验收。数据库门要求 PostgreSQL 18.6、pgvector 0.8.7 与明确授权的隔离测试库：

```sh
uv run --locked python -m pytest tests/test_postgres_integration.py --require-postgres -q
```

测试 DSN、密码、TLS 私钥和其他秘密由运行环境提供，不放入仓库。缺必需环境、必跑测试被跳过或未收集时，真实数据库门不通过。

## 当前材料

- `backend/`：八模块后端、UoW、迁移、公共模型与有界 JSON 输入。
- `deploy/`：gateway/API/worker/PostgreSQL 四服务声明及预检；准确镜像与真实生命周期仍待验证。
- `docs/`：各分段实际交付、命令、来源及通过/未执行记录。
- `_bmad-output/implementation-artifacts/`：当前工作集、短规格、Sprint 与验收台账。
- `AGENTS.md`：模型、唯一文件归属、远程验证和串行接力约定。

前端与契约导出按 Story 1.1 依赖顺序实现；不以占位页面或静态检查代替运行证据。存储桶测试材料与归档路径是 `/fileOfRag/testOfRAG`；数据库及活动锁使用经核验的 Linux 本地文件系统。
