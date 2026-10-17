# Epic 1 Context: 安全开始开发与受控调用（S0）

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

实施者无需供应方凭据即可重建四服务工程，并以真实 PostgreSQL、Linux 与明确标注的可控假件证明事务、隔离派发、共享限流和资产守卫，为后续接入提供可核前置。规划已就绪；运行门仍待执行，启动成功不能代表真实供应方、目标资源或可信恢复通过。

## Stories

- Story 1.1: 启动可重建的模块化项目
- Story 1.2: 隔离执行并保存每次调用事实
- Story 1.3: 证明共享限流与双任务gate不会提前退额
- Story 1.4: 在真实停写后清理资产并释放预算
- Story 1.5: 签署S0本地门并交付隔离探路工具

## Requirements & Constraints

- 干净 Linux 环境可构建、迁移、回滚、启动和停止。锁实际依赖、peer、工件 hash 与镜像 digest，登记上游来源、许可证和改造边界；未核验内容不得记作已复用。真实 PG/pgvector 不以 SQLite 替代；embedding 维度未实测前只验扩展及隔离测试向量，不建正式 vector(D)。
- 所有外部调用先持久意图，禁止暗重试、自动重定向和原 call 重发；失败及未知成本保留，未知为 null + unknown。迟到可信事实仅幂等补账，不改变业务、配额或会话。
- 本地假件通过全部隔离、限流和资产负例，且逐能力真实限制已核，才能开展任何真实外发。维护测试入口不赋业务权限；后续身份、资源、历史与上线各保留独立开放门。
- 证据记录版本、环境、输入、预期/实际、副作用、关联 ID 和失败/阻塞；PG、Linux、供应方及目标机成绩分别标来源。普通日志不含正文、完整提示、秘密或签名 URL，合法样例与业务资料分离。

## Technical Decisions

- 采用模块化单体、端口适配器和八模块唯一写者：identity_access、library、indexing、execution、query、ledger、conversation、platform_ops。入口共用 application 用例；领域不导入框架、ORM 或 HTTP SDK。部署仅 gateway/API/worker/PG，PG 持久任务，不新增常驻队列或 Agent 编排。
- 后端沿已定 Python/FastAPI/Pydantic、同步 SQLAlchemy/psycopg/Alembic seed；前端使用 create-vue 3.23.0 的 TS/Router/Pinia 模板与 Element Plus。初始化必须核真实版本及组合，差异显式报告，不静默换版；Node 只用于构建。每故事增量建模和迁移，不预建全部业务表。
- application 独占短 UoW 的 begin/commit/rollback；仓储不 commit，Session 线程独立。全局锁序为账号→空间→KB→固定类别业务对象→容量/日桶→本地 gate→provider pool→call→permit 组件→asset，各组稳定排序。不持 PG 事务等待网络、OS 锁、进程或删除。
- 后端 contracts 单一导出 OpenAPI/JSON Schema/TS 及正负样例；稳定 ID、UTC 时间、十进制金额、Unicode 标量码点/半开偏移与确定性序列化跨端一致。公共响应扁平，状态/业务结果分开，错误有限且不泄私有 ID。JSON 入口在业务前流式限制字节、编码、深度、节点、重复键和未知字段；1MiB JSON 界不套原件 PUT。私有成功/错误均 no-store，gateway 禁私有缓存与私有资产静态直出。
- 独立持久 epoch 与 DB 镜像比较，缺失/矛盾即隔离，普通重启不换 epoch。控制器监督有限子执行者；child 无业务 DB/主密钥，不自主串阶段，最少秘密经有界私有 IPC 注入。每次出网核 HTTPS、准确 host/port、全部 A/AAAA 公共地址并绑定连接，保留 TLS 主机验证；不转发 API 凭据到下载 host。
- 共享限流跨 API/worker/账号密钥统一持久化。send_open 持续全量占额；只有监督证明全部 sender/后代停止、FD/IPC 关闭且旧 grant 销毁，才取随后 DB 上界并保留完整窗口。业务终态、期限或 usage 均不提前退额。HTTP、task 与窗口组件各按自身证据一次终结。
- 全系统 doc_active_job 与 external_async_task 为两个独立 gate，各默认4、可配1–4；有效值受真实账号与资源证据限制，本机重阶段槽仍1。queued 不占 job，unknown task 不随 job 结束返还；轮转公平推进到期 poll，等待不持 Session、正文或常驻 child，原2h期限不刷新。
- execution 独占唯一 prefix、writer/asset 清单和 cleaned；ledger 独占预算转换。实际 writer 自持稳定 Linux SH 生命周期锁；清理固定 fence→事务外停写→稳定 EX→复核→删除核验→cleaned/唯一释放。未证停写、FD 未关或提交失败继续占用/blocked；框架暂存、解包、图片和备份均纳入预算与低水位保护。

## UX & Interaction Patterns

前端骨架沿浅色、系统字体和既定语义 tokens；仅验当期新增表面，不提前交付业务页面。新增界面须明确空、失败、隔离与 unknown，遵守键盘/焦点、响应式和200%缩放要求；不得把假件、未知限制或未执行门画成成功。

## Cross-Story Dependencies

1.1 无前置；1.2 依赖 1.1；1.3 与 1.4 各依赖 1.2；1.5 汇总 1.3/1.4 的完整本地证据。S0 全门通过后，真实探路与身份切片可并行；格式/来源/维度、完整生成预算、图意和目标机验证分别约束后续能力。首次调优前才触发冻结验收资料的前置，不把未来质量成绩设为本 Epic 的开工条件。
