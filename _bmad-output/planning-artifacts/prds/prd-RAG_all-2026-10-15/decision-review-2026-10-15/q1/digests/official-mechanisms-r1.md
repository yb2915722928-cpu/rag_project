# Q1 官方机制 digest

访问日期统一为 2026-10-15。发布日期未标注的写未知；滚动文档不是版本锁定或运行证据。均为官方发布者的一手文档，单源置信度中；所述机制已核对，但未作独立发布者交叉验证。下面的本项目选择是受托设计，不能冒称外部来源直接推荐了本项目方案。

| 官方来源 | 本轮直接读取的事实 | Q1意义 |
| --- | --- | --- |
| [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter)，publisher=FastAPI，pub_date=未知 | APIRouter 将相关路由分组；可统一附加 dependencies。 | 支持按业务组织入口、共用认证；不规定全部服务层设计。 |
| [FastAPI async](https://fastapi.tiangolo.com/async/#path-operation-functions)，publisher=FastAPI，pub_date=未知 | 普通 def 路由及依赖由线程池执行；直接调用的普通辅助函数不会自动转线程。 | 同步DB和SDK可配普通def；不能在async def直接阻塞。 |
| [SQLAlchemy Session并发](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks)，publisher=SQLAlchemy，页面生成2026-10-14 | Session per thread、AsyncSession per task；建议在任务顶层以局部context manager限定生命周期。 | Session不能跨请求、线程、任务共享。 |
| [SQLAlchemy psycopg](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg)，publisher=SQLAlchemy，pub_date=未知 | psycopg dialect按engine创建方式支持同步或异步；驱动pool可替代SQLAlchemy pool。 | 本项目选同步并只保留一层SQLAlchemy连接池，不双层叠加。 |
| [Psycopg并发](https://www.psycopg.org/psycopg3/docs/advanced/async.html)，publisher=Psycopg，pub_date=未知 | 连接不能跨进程共享；同连接查询串行、共享事务；支持sync与async。 | API与worker各自创建engine/pool；不把async当数据库并行保证。 |
| [Alembic autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)，publisher=SQLAlchemy/Alembic，pub_date=未知 | autogenerate输出候选迁移，必须人工检查修正；alembic check可检查是否有新schema差异。 | 表结构迁移显式执行、纳入版本管理；不依赖启动时create_all改表。 |
| [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#server-side-session-token-storage)，publisher=OWASP，pub_date=未知 | 会话语义保存在服务端；随机token可存单向校验值，split identifier+secret可用SHA-256及constant-time comparison；Secure/HttpOnly/SameSite，SameSite不替代CSRF token。 | Web cookie仅载随机会话凭据；PG保存hash与状态；随机凭据不能类比低熵密码。 |
| [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#introduction)，publisher=OWASP，pub_date=未知 | 新密码使用慢hash；Argon2id最低建议之一为19MiB、t=2、p=1，参数需目标机器校准；库一般管理salt。 | 使用Argon2id；参数及并发限额仍需实现阶段验证，不预设登录容量。 |
| [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html#validate-the-permissions-on-every-request)，publisher=OWASP，pub_date=未知 | 默认拒绝、最小权限、每次请求检查授权，并集中配置以减少漏检。 | 统一授权入口是本项目设计；具体角色规则仍来自已确认PRD。 |
| [OWASP REST Security JWT](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html#jwt)，publisher=OWASP，pub_date=未知 | JWT可能与当前会话状态脱节；提前终止需服务端拒绝列表直到过期。 | JWT本身不能代替立即撤销；本项目已有PG，不必再维护JWT+状态双机制。 |
| [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)，publisher=OWASP，pub_date=未知 | 状态改变请求应受CSRF保护，SameSite是附加防御。 | Cookie会话需要CSRF token和Origin检查；不能只选Cookie而略去这项代价。 |
| [Python secrets](https://docs.python.org/3/library/secrets.html)，publisher=Python Software Foundation，pub_date=未知 | 提供用于密码、token等的密码学安全随机数与compare_digest；token_bytes可指定字节数。 | 受托设计API secret为32随机字节，随机secret用SHA-256；不是密码hash替代。 |
| [PostgreSQL Read Committed](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-READ-COMMITTED)，publisher=PostgreSQL，pub_date=未知 | 默认Read Committed每条语句看到开始时已提交状态；Repeatable Read可继续看到旧快照。 | 撤销确认以事务提交为边界，检索与返回前需新会话/新查询，不拿初次ORM对象代替重鉴权。 |
| [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)，publisher=LangChain，pub_date=未知 | 当前create_agent提供模型/工具/提示/中间件组合；agent构建在LangGraph上。 | 现有固定RAG流程无须采用agent运行框架；不声称框架一定慢或耗多少内存。 |

未获取性能、内存、容量、定价或目标机器压测数据；不据此作任何量化结论。固定源码有效性与库版本锁定分别处理。
