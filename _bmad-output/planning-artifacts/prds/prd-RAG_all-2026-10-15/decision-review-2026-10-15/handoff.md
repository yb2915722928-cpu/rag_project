# 新 Mary 的短交接

日期：2026-10-15。每个 John 大问题由一位新 Mary 完成 TR→TS，追问回原 Mary；收口后再开下一题。不需要读取所有前轮对话，只读本交接与当前问题指定的证据。

## 用户与产品约束

- 用户求职学习、不现场演示；AI 实际编码集成测试文档，用户核对并理解，约半月预期；当前仍为方案阶段，不开始编码、安装模型或调用收费 API。
- 后端 FastAPI＋PostgreSQL＋pgvector；前端 Vue 3＋TypeScript＋Vite；PG 持久任务＋独立 Python worker，文档并发 1。生产 4C4GB Ubuntu 同机 Web/API/DB；电脑 16GB、自查 i7-12700H＋RTX3060 Laptop6GB，仅开发；API 优先。
- 用户已选 MinerU 云端 API 上传解析，不自托管，不继续旧 OCR 排查／本地多引擎实验。TXT／Markdown 可直接读；格式、来源、表格、图意必须按 PRD 验证，不因 API 成功就视为通过。
- 千问小模型问答按需充值，具体型号／账号实际使用前确定。向量、重排、图意是各自能力，不能由问答型号推定；不追问固定预算或每日编码工时。
- 权限：个人／团队空间及逐库授权；平台身份无自动业务读权；程序 API 绑定用户、单空间、指定库、只读、必到期、可撤销、仅创建显示密钥；有效范围为密钥与用户当前权限交集；检索、输出前、历史、追问、引用、下载均复核。
- 四场景全部交付；先纯向量 B0，最终 K=5；开发题与32冻结验收题分开，按实测选优化，不把关键词／重排／ANN 都算必做；真实成本、失败与退步留证。
- 不编造容量、测量、用户掌握；公共/明确模拟资料可由 AI 整理，不要求用户凭空报企业负载。账号、外部访问权限等到实际接入才需用户。

## 本轮 Q1 已收口的边界

1. 模块化单体；HTTP入口、业务规则、持久化与显式RAG步骤分开，API/worker共用核心模块；首版不引入LangChain/LangGraph编排。
2. 同步 SQLAlchemy 2＋psycopg 3，FastAPI def 路由，短事务/独立Session；Alembic版本迁移。API/worker分设有界连接池；外部HTTP等待不持DB连接，不跨线程传Session。
3. PG服务端随机Cookie会话，Secure/HttpOnly/SameSite并加写请求CSRF/Origin检查；Argon2id密码验证，具体参数目标环境校准。
4. 用户绑定随机只读Bearer密钥，公开ID＋secret hash与范围/到期/撤销状态；不存可恢复密钥；Web/API认证入口分开，共用当前授权服务。
5. 查询/上下文使用/完整放行前读当前权限；历史保留证据依赖集合并复核。最终检查不是网络发送与撤权的全局原子事务，也不追溯收回已显示内容。

上述是本轮受托技术选择，不是用户逐项亲选，也没有实测。后续题发现冲突要反馈 John，不静默推翻。

## Q2／Q3 增量

Q2 追加交接：PG 短事务 SKIP LOCKED 领取＋租约／attempt 条件写入；主线程处理一份文档，续租线程使用独立短 Session，不在 HTTP 等待持连接。MinerU 上游 ID 先持久化再上传，超时查原 batch，未知状态不盲重交；已校验阶段产物按版本／配置复用。统一页／段／表／图来源；PDF 页 1 起，DOCX 无可信页则结构定位。候选完整就绪才原子切 active；首次可定位的部分通过内容可查询且标不完整，不完整替换候选不覆盖旧版。删除墓碑先阻断，迟到结果不可复活；清理可重试。不声称外部恰好一次、逐页断点或字节续传。

Q3 追加交接：保留段／表／图来源的结构块，600中文字／80重叠仅初值；embedding 独立配置／维度／索引版本，初选余弦与一致归一化策略；授权空间库、active_version、未删除通过块中做精确 B0。最终整请求最多五块，对比子查询按条件原序和对象ID固定顺序、各路名次轮转合并去重，不比较跨query分数，不隐塞邻块／全文／旧答案。金标证据单元不等于候选块，SM2分母不改。四场景共用链路不同schema，引用ID白名单＋后端鉴权resolve；追问历史仅辅助改写，重新检索授权。JSON仅做无语义清理，结构或ID不合法整答可见失败，不自动追加模型修正，真实重试费用保留。

## 证据入口

- 需求唯一基线：[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md)。本交接不是外部技术事实证据。
- WeKnora 研究SHA：`a37a1bc51ad85d096df341f6d3a098f60d586f52`；MaxKB：`0fa9a0dae8850c1878f087f0d81c974c1d424b06`。同日研究参照，不当开发基线。
- 已读官方源码快照：[实现摘要](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/digests/implementation-r1.md)，同目录 imports 保存部分原文；可本轮重读，缺的再窄取官方源码。
- Q1：[回答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/answer.md)，[证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/evidence.md)。
