# Winston B 独立 CA 初评（封存）

日期：2026-10-16。封存时未读取 Winston A 的方案或初评。身份：Winston / CA，headless=true，initiative / build-substrate；不是历史 IR 标签的复用，也不是功能或运行验收。

## 输入与既定边界

已实际逐段通读现行 PRD、addendum、summary、technical-decisions-dialogue、implementation-contract、implementation-slices，以及现行 UX README、DESIGN、EXPERIENCE、page-contracts、handoff、handoff-check 和 key-surfaces。snapshots/baseline/imports 属历史；当前没有应用代码。

继承模块化单体、同步 SQLAlchemy 2/psycopg 3/Alembic、FastAPI def、PG/pgvector、PG 任务与独立 worker、MinerU 云、Vue/Router/Pinia/Element Plus、Compose 四服务、完整答复、K=5 与四场景，不重新选产品规则。默认 agent/workflow hooks 与 persistent_facts 为空；直接 Python resolver 已成功。

## 我提出的架构候选与取舍

| 候选 | 独立实现的风险 | 我的选择 |
| --- | --- | --- |
| 以 HTTP 页面/worker 为模块边界，各自直接写表 | Web、program、worker 会复制授权/终态/资产清理规则；不兼容且无法收敛 | 拒绝 |
| 六个业务模块加统一用例入口与事务协调，端口隔离外部副作用 | 需明确聚合拥有者及跨模块事务，开发成本较集中；部署/恢复简单 | 采用 |
| 拆微服务/独立队列与向量库 | 当前4GB/学习目标没有证据支持跨存储一致性成本 | 不采用；不得借架构悄改已选主栈 |

六个模块建议为：Access（身份/空间/成员/授权）；Library（文档/不可变版本/来源/活动索引）；Execution（上传/任务/attempt/受监督执行/清理）；Query（检索/会话/操作/答案及受控证据）；Accounting（原件预留/产品日桶/外部call事实）；Operations（配置/epoch/安全台账导出与恢复控制）。模块名可换，**唯一写者与调用方向不可空白**。

HTTP 两路仅认证与协议适配；worker 只驱动同一 application use case。领域代码不依赖 FastAPI/SQLAlchemy/HTTP 客户端。每个模块唯一拥有其状态模型；跨模块写由 application UoW 以同一短 PG 事务协调，repository 不自行 commit；边界不得为避免跨模块调用而复制状态/派发 HTTP 请求。等待外部服务、OS 锁、进程退出或删文件时无 DB Session。

## 必须新增或明确的架构决定

1. **事务协调所有权。** 发布、撤权/接管、上传原件转实占+建job、答案结果+依赖+轮次+计次、安全变化+台账必须分别只有一个用例协调入口；不只是“同事务”口号。使用全局固定锁序，成本迟到回填是独立只锁call路径。
2. **控制面/副作用分离。** 监督者持DB写资格，子执行者只能在已授予的单次传输/文件前缀执行并回有限结果，不能自己串接下一阶段。PG fence只能挡业务提交，停写证明/稳定OS锁才允许资产释放；不能让本机进程池跨attempt复用。
3. **共同线形与代码生成。** 一个后端 schema 包拥有 Web/program 共同业务载荷、HTTP envelope/error、三账和五条状态线；前端生成类型，不能分别手写状态枚举。模型 generation 子契约与公开业务 DTO 不同；catalog/元数据只由后端构建。S0先有公共形状，S1开始所有私有响应归属。
4. **无效输入与技术字段有限政策。** UX G-04/IA-10/12明确交给架构的管理名称/标签/反馈/账号/密码、凭证最长有效期、分页边界须出共享技术配置，不能由前端自行猜测；不允许把这类“未定schema”永久Deferred后给所有故事。可用有限默认+单一schema，P0运营限额保留验证门槛。
5. **逻辑槽与物理槽两种寿命。** query logic gate可因lease到期释放，已发阻塞传输者未停不能释放物理槽；API扫描与worker扫描不能双写同终态，条件更新必须只有一次效果。无持久排队查询，已受理同步链不得因浏览器断网偷偷变取消。
6. **查询钉快照与当前权限并存。** 版本/代/配置快照固定，授权/墓碑/epoch每阶段当前检查；授权成功DTO不是可以跨长等待复用的永久许可。历史evidence_snapshot必须有实际片段/offset/hash/源定位且独立于向量GC；模型可见catalog必须与预算后的片段完全相同。
7. **恢复的独立持久性。** epoch控制卷、break-glass登记与独立安全台账介质在部署拓扑内分别明确；“另存文件”不能误成与DB同备份回滚。恢复要控制面先隔离/新epoch/独立信任核验再逐范围放行，四服务部署必须配只读/挂载/秘密注入矩阵。
8. **适配器适用证据与停止点。** 选型和版本可核，不把“最新”当兼容性；P0产出真实profile及source映射、完整token预算、4GB/RSS/硬限制证据。S0/1可先做，S2/3/5/6有不同真实前置；不能以P0未测宣布全部不能开工，也不能以S0可开工称整计划已验证。

## 最强可合规却不兼容反例

- 文档工程师把job.state作为文档state，UI工程师只读status；双方“显示状态”却把旧生效版遮住。必须固定独立五状态形状。
- Accounting API先锁space，再访问Library KB；Library上传先锁KB再取space，双方都用事务却会死锁。必须全局锁序及协调入口。
- worker停止结果只是子进程PID不存在，清理者删前缀并释放；另一个缓冲/后代写入继续。必须监督注册所有写入者、稳定锁、有限IPC/缓冲预算。
- 前端仅由OpenAPI生成基本类型，但生成compact档与外层512字段混用，模型超128却UI裁短；须generation_contract_id与可见能力/校验/快照一致。
- 外部调用全部有call行，但适配器自动重定向/SDK重试形成第二次付费传输；须单次dispatch契约、关闭暗重试、允许重试新call+重过gate。

## 初步可实施判断

S0的需求前置充分，但架构交付仍需定下上述跨模块所有权/DTO/运行边界后才形成可复用substrate。全计划没有发现必须改产品范围的冲突；真实P0/4GB/恢复/质量是明确执行停止点，尚未运行。后续将逐项建立 FR/NFR/UX/切片→AD/companion→验收矩阵，并对实际最终合稿独立核对。
