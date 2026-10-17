## TR：两个项目实际怎么做

截至 2026-10-15，只读固定提交；下表是实现事实，未运行验证。WeKnora= a37a1bc，MaxKB= 0fa9a0d。

| 方面 | WeKnora | MaxKB |
| --- | --- | --- |
| HTTP与业务 | Gin路由、handler/service/repository分工；[接线源码](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/container/container.go#L42-L76) | Django/DRF业务模块、View交给Serializer；[模块](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/maxkb/settings/base/web.py#L30-L47)、[入口](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/chat/views/chat.py#L167-L189) |
| PG与表结构 | GORM连接PG、golang-migrate版本迁移；[连接](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/container/container.go#L834-L845)、[迁移](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/database/migration.go#L100-L141) | Django ORM与参数化SQL、Django迁移；[连接配置](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/maxkb/conf.py#L24-L30)、[SQL](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/db/sql_execute.py#L21-L25)、[迁移](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/migrations/0001_initial.py#L133-L149) |
| RAG | 自组事件流水线；[检索到生成](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/session_knowledge_qa.go#L215-L246) | 简单流水线或Workflow；[流水线](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/chat/serializers/chat.py#L350-L360)、[分支](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/chat/serializers/chat.py#L479-L487) |
| Web认证 | bcrypt、Bearer JWT；token入库并查撤销/账号状态；[密码](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L249-L258)、[签发入库](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L1110-L1172)、[校验](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L1314-L1338) | 签名token写缓存；认证查缓存/账号，退出删缓存；[登录](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/users/serializers/login.py#L149-L180)、[校验](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/auth/handle/impl/user_token.py#L300-L318)、[退出](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/users/views/login.py#L67-L82) |
| 程序凭证 | tenant/platform范围、能力与KB、可空到期/撤销；另存可恢复secret；[模型](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/tenant_api_key.go#L18-L38)、[加解密](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/tenant_api_key.go#L245-L265) | 应用/工作空间key；迁移删除用户外键；[模型](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/models/application_api_key.py#L11-L22)、[迁移](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/migrations/0012_remove_applicationapikey_user.py#L12-L16) |

因此可借鉴分层、迁移与服务端复核；两种程序凭证均不能直接视为本项目的“用户当前权限交集”。

## TS：本项目选择

以下是受托设计，沿用既定角色；优先规则一致、容易理解和核验，没有性能评分。

1. **模块化单体。** 按账号/空间授权/知识资料/问答历史/任务/平台配置分业务；HTTP只做校验与调用，业务管规则，持久化管查询。Web与只读API分路由、共用业务服务。[APIRouter依据](https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter)。比微服务少部署边界，代价是须守住模块依赖。
2. **RAG用显式Python步骤。** 授权范围→向量检索→上下文→模型→引用校验；MinerU、向量化、问答各留适配边界。首版不引入LangChain/LangGraph大框架；需要复杂工具编排再评估，代价是自行维护少量流程。[框架边界](https://docs.langchain.com/oss/python/langchain/overview)。
3. **同步SQLAlchemy 2＋psycopg 3。** API用普通def，worker同一访问风格；每次业务短事务独立Session，API/worker各建有界连接池，等待模型时释放连接。比全异步少一套并发约束；代价是长等待占线程，设超时/并发限制，实测排队后再考虑异步。[FastAPI](https://fastapi.tiangolo.com/async/#path-operation-functions)、[Session](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks)。
4. **Alembic管表结构。** 显式版本迁移含pgvector扩展/索引；自动生成后人工核对，部署单独执行。比启动自动改表可追溯，代价是维护迁移文件。[官方限制](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)。
5. **Web选PG服务端会话＋随机Cookie。** 只存会话hash、用户、到期/撤销状态；Cookie设Secure、HttpOnly、SameSite，写请求加CSRF/Origin检查；退出、改密和停用撤销会话。相比JWT，少签名/刷新/拒绝列表组合，代价是每次查PG及CSRF防护。[会话](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)、[JWT撤销](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html#jwt)。
6. **密码选Argon2id。** 使用成熟库管理salt和验证；先按官方最低建议配置，目标机器校准。比普通SHA-256抵抗猜解，代价是登录CPU/内存和限流。[OWASP依据](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#introduction)。
7. **API用随机Bearer密钥。** 32随机字节，仅创建返回；PG存公开ID＋secret的SHA-256及用户、单空间、KB、只读动作、必填到期、撤销时间，恒时比较；不存可恢复密钥。本人创建、本人/团队所有者按已定规则撤销。比JWT或可逆加密易吊销，代价是遗失后重建及逐次查库。[随机数](https://docs.python.org/3/library/secrets.html)、[单向token校验](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#server-side-session-token-storage)。
8. **统一授权。** Web/API认证后进入同一授权服务，默认拒绝；API范围＝凭证∩当前用户范围，动作也取交集。检索SQL先限空间/KB再取候选；凭证只进只读动作白名单，平台身份不赋资料读权。比散落路由检查多一个共同入口，代价是必须覆盖所有资源出口。[每请求授权依据](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html#validate-the-permissions-on-every-request)。
9. **撤权直接读当前状态。** 撤销事务提交后生效，不缓存授权结论；检索前、模型上下文使用前、完整结果放行前用新Session重查账号/凭证/资源权限。失权丢弃整份待发答案；历史保存依赖资料集合，回看/追问重新鉴权，失权回答整体隐藏；引用/下载经鉴权代理。比初次检查多查库，换取进行中请求和旧入口的一致性。[PG快照依据](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-READ-COMMITTED)。

## 初学者复述（200字以内）

接口是接待员，业务层决定能做什么，数据库层负责读写，RAG只处理获准资料。密码换Web会话；程序密钥是绑定本人且范围更窄的通行证。两者每次都查当前权限。生成等待时不占数据库连接，返回答案前再核一次；撤权后旧会话、引用和下载也不能通行。表结构用迁移逐步升级。

## 实现验证清单（尚未执行）

- Web/API同一身份同一动作权限一致；平台管理员、跨空间/跨库、只读密钥写入均拒绝。
- 模型等待时撤KB权、撤密钥、到期或停用；随后完整输出和旧历史/追问/引用/下载不泄露资料。
- 登录/退出/改密、Cookie属性与CSRF；密钥仅显示一次，数据库与日志无原密钥；凭证任务状态仅本人且在scope内。
- 空库迁移与已有数据升级；API/worker各自连接池，模型等待不持连接；记录真实超时/资源数据再调并发。

`user_only_missing`：无。连接池大小、会话时长、hash参数和依赖版本在实现时配置与验证，不需要用户重选产品规则。
