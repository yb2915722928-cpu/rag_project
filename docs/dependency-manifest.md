# RAG_all 依赖与工件 provenance 台账

状态：`partial`，2026-10-17 当前记录。A1 已在真实 Linux / CPython 3.12.8 正常生成并同步锁；前端、镜像和干净重建仍未完成。历史 3.12.15 结果见重建证据，不改写为新成绩。

## 后端直接依赖

| 组件 | 项目声明 | 当前锁/环境 | 来源 | 当前状态 |
| --- | --- | --- | --- | --- |
| Python | CPython 3.12.8 | 远程uv隔离解释器，宿主3.12.3未替换 | https://www.python.org/downloads/release/python-3128/ | 实际运行已核；A1记录保留精确路径/版本 |
| FastAPI | 0.143.2 | 新锁与Linux已安装版本一致 | https://pypi.org/project/fastapi/0.143.2/ | metadata及LICENSE文件hash已取 |
| Pydantic | 2.14.1 | 新锁与Linux已安装版本一致 | https://pypi.org/project/pydantic/2.14.1/ | metadata及LICENSE文件hash已取 |
| SQLAlchemy | 2.0.54 | 新锁与Linux已安装版本一致 | https://pypi.org/project/SQLAlchemy/2.0.54/ | metadata及LICENSE文件hash已取；真实PG仍未验 |
| psycopg[binary] | 3.3.6 | psycopg/psycopg-binary均与锁一致 | https://pypi.org/project/psycopg/3.3.6/ | 已安装/记录LGPL-3.0-only声明；真实服务与libpq组合门未关闭 |
| Alembic | 1.20.0 | 新锁与Linux已安装版本一致 | https://pypi.org/project/alembic/1.20.0/ | metadata已取；真实迁移循环未执行 |
| HTTPX | 0.28.1 | 新锁与Linux已安装版本一致 | https://pypi.org/project/httpx/0.28.1/ | 既定版本保留，旧TestClient warning不导致静默换版 |
| Uvicorn | 0.37.0 | 正常锁新增并在Linux安装 | https://pypi.org/project/uvicorn/0.37.0/ | A1实际进程/健康/关闭已测，容器跨网关门待验 |

## 数据库与部署工件

| 工件 | 声明 | 来源 | 当前状态 |
| --- | --- | --- | --- |
| PostgreSQL | 18.6 | https://www.postgresql.org/support/versioning/ | 远程Engine可用；Docker Hub IPv4超时，准确镜像/真实PG未取得 |
| pgvector | 0.8.7 | https://github.com/pgvector/pgvector | 精确要求保留，扩展/镜像digest未核 |
| Nginx | 1.30.6 | https://nginx.org/en/download.html | 部署声明已交；官方完整镜像和实际Nginx验收未取得 |
| Docker Compose | 5.6.0 | https://github.com/docker/compose/releases/tag/v5.6.0 | 远程实际版本已核；结构检查不代表构建/生命周期 |
| uv镜像 | 独立工具工件 | https://github.com/astral-sh/uv | 官方GHCR manifest已有去令牌证据，平台完整镜像层尚未取得 |

## 本轮后端实际依赖与许可证证据

源工件为 [uv.lock](/E:/aaa-project/rag/backend/uv.lock:1)，SHA-256 `7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed`。正常解析为41包（含项目自身）；原39版本不变，新增Uvicorn/Click。Linux安装、命令和46/46源码hash见 [A1交付](/E:/aaa-project/rag/docs/story-1-1-python-3128-delivery.md:1)。

主会话通过远程只读metadata诊断得到 [依赖明细](/E:/aaa-project/rag/docs/backend-dependency-inventory.json:1)，SHA-256 `e1b12a1c972b73583fc2e4b5d9c62f3ca4d2a1ae5fe204232a00ad787edc1b7f`，原件同hash保存在存储桶 `metadata/story-1-1/backend-dependency-inventory.json`。明细逐包保留锁版本、实际安装版本、来源、官方wheel锁hash、License-Expression/旧License/分类及实际LICENSE/NOTICE文件hash。

40项第三方锁记录中，38项Linux实际安装且版本无偏差。colorama与tzdata未安装：新锁仅以 `sys_platform == 'win32'` 引用，两项为平台条件未选中，不当作Linux缺依赖，也不伪称读取了它们的许可证工件。构建隔离依赖、原生捆绑库/镜像层、Windows条件工件仍须按实际发布平台补全。

已安装元数据包含MIT、MIT-0、BSD-2/3-Clause、PSF-2.0、Apache-2.0、MPL-2.0，以及psycopg/psycopg-binary的LGPL-3.0-only声明；cryptography为Apache-2.0 OR BSD-3-Clause，greenlet为MIT AND PSF-2.0。这里记录发布工件自身的声明与hash，不把包名或许可证字符串当成完整来源/分发边界已核。

## 仍未完成

- 前端starter/peer/npm锁与真实工件、全部镜像digest/完整层、干净Linux重建与真实PG门均未完成。
- 本轮没有把参考RAG项目登记为已复用；若引入上游抽取/样例，仍须固定来源提交、许可证、原始最小样例hash及本地改造diff。create-vue尚未实际生成，也不提前记为复用通过。
- 既有 [重建证据](/E:/aaa-project/rag/docs/rebuild-evidence.md:1) 保留历史3.12.15失败/补充测试；本轮当前A1证据按新交付单独记录。供应方、浏览器和4C4GB目标机未执行不推定通过。
