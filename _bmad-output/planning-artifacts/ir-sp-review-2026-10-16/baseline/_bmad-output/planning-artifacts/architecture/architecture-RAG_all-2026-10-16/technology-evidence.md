---
title: 技术核验与冷启动版本证据
checked_at: 2026-10-16
status: verified-seed-not-installed
---

# 技术核验与冷启动版本证据

Winston A2本轮实际打开以下官方发布页/仓库/模板，不把前代记忆当作复核结果。选取维护线和模板兼容线的明确版本；不是“全用最新”、依赖安装成功、目标机兼容或真实供应方通过证明。S0生成含传递依赖的锁文件、镜像digest和构建记录后由代码接管。官方页面随时间变化，实施者把本表版本、来源、解析时间及实际工件hash一并保存。

## E1：运行与持久化seed

| 组件/选择 | 本轮实查证据与适用边界 |
| --- | --- |
| Python 3.12.15 | [Python官方发布表](https://www.python.org/downloads/)列3.12安全维护至2028-10及3.12.15（2026-09-30）；采用已在本机脚本环境使用的3.12线，非主张最新主版本。生产容器升级补丁；当前运行文档脚本用3.12.8不等于生产工件 |
| FastAPI 0.143.2 | [项目PyPI](https://pypi.org/project/fastapi/0.143.2/)列2026-10-15工件；用于HTTP/OpenAPI，普通def入口和有界ASGI上传edge分开；ASGI服务器及Starlette等传递依赖在S0解算并锁定 |
| Pydantic 2.14.1 | [项目PyPI](https://pypi.org/project/pydantic/2.14.1/)列2026-10-11工件；contracts的strict/额外字段拒绝和跨字段规则须显式配置，不能以库名代替业务校验 |
| SQLAlchemy 2.0.54 | [明确版本PyPI](https://pypi.org/project/SQLAlchemy/2.0.54/)列2026-09-15且标另有2.1.4；这里有意选2.0维护线。使用同步短Session与显式UoW，不盲升2.1 |
| psycopg 3.3.6 | [项目PyPI](https://pypi.org/project/psycopg/3.3.6/)列2026-09-18工件；SQLAlchemy同步PG驱动，目标Linux二进制/libpq组合与pool在S0验，不采用asyncpg平行路线 |
| Alembic 1.20.0 | [项目PyPI](https://pypi.org/project/alembic/1.20.0/)列2026-09-11；显式迁移与单维护进程执行，生成DDL须人工/测试核对，不在请求内动态改vector维度 |
| PostgreSQL 18.6 | [官方支持表](https://www.postgresql.org/support/versioning/)列18.6及18线支持至2030-11-14；支持表不是4GB容量保证。S0核锁定镜像实际SHOW server_version，不把tag浮动当补丁已锁 |
| pgvector 0.8.7 | [官方仓库](https://github.com/pgvector/pgvector)当前安装示例指定v0.8.7、支持PG13+并列0.8.7-pg18镜像tag；支持精确搜索、cosine和固定vector(D)。S0构建/查询核扩展版本；D仍须P0真实embedding后显式迁移，B0不建ANN索引 |
| HTTPX 0.28.1 | [项目PyPI](https://pypi.org/project/httpx/0.28.1/)有明确工件；统一受控HTTP适配器，显式timeout、follow_redirects=False、transport retries=0；HTTPX读超时不是绝对total，仍由监督子执行者deadline封顶 |
| argon2-cffi 25.1.0 | [项目PyPI](https://pypi.org/project/argon2-cffi/25.1.0/)和[官方API](https://argon2-cffi.readthedocs.io/en/stable/api.html)支持Argon2id及RFC_9106_LOW_MEMORY档；凭据验证并发/目标RSS实测后生效，不以默认参数代表4GB已验证 |
| cryptography 50.0.2 | [项目PyPI](https://pypi.org/project/cryptography/50.0.2/)列2026-09-30 Linux/Windows工件；[官方AEAD文档](https://cryptography.io/en/latest/hazmat/primitives/aead/)支持AESGCM并强调nonce不得同key复用。本项目选AESGCM功能子集，非采用其51-dev文档全部新API |

## E2：前端starter与构建seed

采用Vue官方create-vue，而非从零手写工具链。已实际打开[create-vue v3.23.0发布](https://github.com/vuejs/create-vue/releases/tag/v3.23.0)；S0用此确切版本选择TypeScript/Router/Pinia，测试工具按切片需要选择，不引入SSR服务。模板范围与选定精确补丁分别记录，前者不冒充锁文件。

| 组件/选择 | 实查官方依据 |
| --- | --- |
| create-vue 3.23.0 | [base模板](https://raw.githubusercontent.com/vuejs/create-vue/v3.23.0/template/base/package.json)实际为vue^3.5.40、vite^8.1.5、plugin-vue^6.0.8、Node ^22.18.0或≥24.12.0；不是旧Vite模板记忆 |
| Vue 3.5.44 | [官方release](https://github.com/vuejs/core/releases/tag/v3.5.44)；属于模板^3.5.40范围 |
| Vite 8.3.4 | [官方release](https://github.com/vitejs/vite/releases/tag/v8.3.4)；属于模板^8.1.5范围 |
| TypeScript 6.0.3 | [官方release](https://github.com/microsoft/TypeScript/releases/tag/v6.0.3)；[TS模板](https://raw.githubusercontent.com/vuejs/create-vue/v3.23.0/template/config/typescript/package.json)是~6.0.0、vue-tsc^3.3.7，故沿6.0线，不猜最新主版兼容 |
| Vue Router 5.4.0 | [官方release](https://github.com/vuejs/router/releases/tag/v5.4.0)；S0核starter路由样例与此版构建，不以旧Router4 API记忆实现 |
| Pinia 4.0.2 | [starter Pinia模板](https://raw.githubusercontent.com/vuejs/create-vue/v3.23.0/template/config/pinia/package.json)为^4.0.2；[Pinia确切package](https://raw.githubusercontent.com/vuejs/pinia/v4.0.2/packages/pinia/package.json)要求Vue^3.5.11、TS≥5.6，并有非optional的@vue/devtools-api^8.1.5 peer；S0须解析/锁此peer，不能删掉后声称模板可构建 |
| Element Plus 2.14.7 | [官方release](https://github.com/element-plus/element-plus/releases/tag/2.14.7)；用于表格/表单/弹层，视觉tokens遵循UX，键盘/窄屏须验；不默认组件库自带全部业务交互 |
| Node 24.22.0 | [官方版本表](https://nodejs.org/en/about/previous-releases)列24为LTS并显示24.22.0 Latest LTS，满足starter Node范围；本轮SHASUMS地址工具不可访问，未声称验签/下载，S0核官方工件hash。仅开发/CI构建，不作为第五个生产服务 |

没有采用FastAPI整栈模板：[官方整栈仓库](https://github.com/fastapi/full-stack-fastapi-template)当前组合React/SQLModel/Tailwind/shadcn，和已定Vue/SQLAlchemy/Element Plus不合；只用框架最小组合与官方Vue starter，不复制它的权限/队列/业务模型。

## E3：部署与实际适用性

| 组件/选择 | 官方依据与未证部分 |
| --- | --- |
| Nginx 1.30.6 | [官方下载页](https://nginx.org/en/download.html)列stable1.30.6（另有mainline1.31.7）；只做TLS/静态文件/受控反代，上传buffering显式关闭，静态资源不能挂载私有原件 |
| Docker Compose 5.6.0 | [官方release](https://github.com/docker/compose/releases/tag/v5.6.0)；四服务与secrets语义按[运行契约R4/R8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md)。目标Ubuntu/Engine/架构包版本尚未确认，S6先核受支持发行版/Engine，S0不伪填宿主版本 |

[SQLAlchemy Session官方说明](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)明确Session是可变有状态、线程独立；支持AD-3的每线程短Session但不自动提供全局锁序。[HTTPX transports](https://www.python-httpx.org/advanced/transports/)和[timeouts](https://www.python-httpx.org/advanced/timeouts/)区分传输重试和connect/read/write/pool超时，故单call禁暗重试与进程绝对deadline是本项目必须显式实现的组合。Linux进程组、flock合作锁、Compose secrets和一致备份的官方核对由B在运行契约R8提供；它们仍需真实PG/Linux故障验收。

## E4：接入前真实门槛

MinerU与千问路线为上游已采用约束，不在此虚构型号/最新API/账号额度；业务研究已给接口方向，实际用例依P0固定真实用途profile。P0必须再次核官方API版本/许可/数据保留与外传边界、原件格式和页/bbox基数、图意支撑、可得权重版本/alias、完整消息计数与有限输出/总token、embedding维度D及账号TPM/RPS。还须逐动作核真实在途HTTP/异步task等并发限制及计数范围，实证新增task满额时原task轮询可按真实适用额度推进；HTTP响应与task终态分维度取证，不能假设厂商均同一种并发。最晚到达/官方执行上界未证不用于释放unknown。未证项保持budget_unverified或对应能力不可用，不派发真实收费来“顺便确认”。本次仅浏览公开文档；未安装依赖、未下载模型、未调用供应方、未部署。profile详情在接入后保存官方链接/日期与去秘密实际响应，不能将本表开源组件证据移花接木为模型能力成绩。

本轮另实开[MinerU官方接口](https://mineru.net/apiManage/docs)：精准v4提供异步提交/轮询、申请上传URL，文档支持类型列PDF/DOCX等而无TXT/MD；不采用免Token的Agent轻量接口替代有凭据精准主路。故[C7格式分派](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md)明确PDF/DOCX走MinerU、TXT/MD本地有界结构保留；不能照抄官方curl自动跟随重定向或把官方额外格式纳为承诺。[阿里云官方embedding文档](https://www.alibabacloud.com/help/en/model-studio/embedding)仍提供文本embedding及可配置维度，但地域/型号/每条及批量限制不同；本次只确认路线存在，不把网页当前推荐型号/默认D或价目表变为本项目已选profile或账号实况。已打开Qwen英文API入口但工具仅得到目录壳；生成模式/完整计数证据仍归P0，不假称已读到参数保证。

[FastAPI并发说明](https://fastapi.tiangolo.com/async/)确认普通def在外部线程池运行而直接调用的普通函数不自动卸载；上传edge不能在async内直接跑同步ORM。[Nginx官方request buffering](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_request_buffering)说明关闭缓冲才即时向上游传，chunked传输还须匹配代理HTTP版本；S0须设并验证proxy_http_version=1.1、request buffering off及受控体/超时，不能只改一开关就断言没有临时文件。

用户本轮要求增加异步任务并发：本地doc_active_job_limit与external_async_task_limit选择默认4、可配置1–4的未测seed，覆盖旧整文档并发1；本机重处理物理stage仍1，远端pending只存有限持久元数据，阶段child停写/关FD/落盘后调度其他job。此为本地资源策略，不声称MinerU/千问账号支持4。P0须同时证明四个在途文档与查询/上传并存时的真实限额、满池原task轮询与有限公平调度，S6再验目标机RSS/CPU/连接/磁盘；不通过时不启用该档，不能只提高配置跳过验证。依赖版本未因此变化。

## E5：本轮CA修复采用的HTTP与浏览器依据

2026-10-16针对R02–R04实际打开以下标准/官方文档；本轮不变更Stack精确版本，不重新宣称依赖安装或产品验收通过。标准支持机制，以下具体收紧取值是本项目技术决定。

| 依据 | 采用规则及适用限度 |
| --- | --- |
| [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#employing-custom-request-headers-for-ajaxapi) | 自定义头配合同源/CORS约束可用于AJAX及登录防护；C5另强制精确部署Origin、JSON、固定登录头，其他认证写继续用会话token。SameSite不替代这些守卫 |
| [RFC 9111 §5.2.2.5、§6](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.2.5) | no-store控制HTTP缓存存储/复用；历史呈现是另一边界。C2/C4要求gateway禁缓存及历史恢复先遮蔽重核，不从该头推定bfcache/已保存内容被清除 |
| [Nginx proxy cache](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache) | R4显式关闭私有路由缓存并设置no_cache/bypass，禁止上级继承或错误页回落。实际配置与自产错误响应头仍须S0/S1验证 |
| [HTML PageTransitionEvent](https://html.spec.whatwg.org/multipage/nav-history-apis.html#the-pagetransitionevent-interface) | pageshow/pagehide与persisted可描述页面历史生命周期；C4要求所有恢复先遮蔽再重新context，不假设unload一定触发。实际浏览器画面/回包隔离由S2/S3验 |
| [RFC 6266 §4](https://www.rfc-editor.org/rfc/rfc6266.html#section-4) | attachment、filename与UTF-8 filename*有规范语义；C7采用服务器编码的安全文件名，不复制上游头。准确媒体类型与下载边界由本项目同时强制 |
| [Fetch：X-Content-Type-Options](https://fetch.spec.whatwg.org/#x-content-type-options-header) | nosniff用于类型检查，不把声明为HTML的响应转为惰性文本。C7另外限制MIME/attachment与inline表示，不能只加该头声称无执行 |

R01是现有PG共享gate、受监督child与C8的本地保守调度算法，无新技术依赖；证明依据是“每个可能发送区间都被open charge覆盖，封口后完整W覆盖每个剩余滑窗”。S0必须用可控暂停/崩溃假件验证，P0再核真实限额；不从公开标准推断供应方永不429或远端到达界。
