---
title: RAG_all 数据与检索方案比较
type: technical
shape: select
decision: 评估 PostgreSQL＋pgvector 相对 Milvus 和 MongoDB 的首版适配性
source: 本轮直接读取的官方文档、代码仓库与发布包元数据
status: complete
created: 2026-10-15
updated: 2026-10-15
validation: normal
claims_verified: 0
claims_unverified: 5
decision_status: 用户已确认首版 PG＋pgvector；实际容量与效果待验证
---

# RAG_all 数据与检索方案比较

**结论：John 提出的 PostgreSQL＋pgvector 方案合理，适合作为首版优先验证的候选，但“4 GB 足够”和“检索效果达标”仍需验证。** 理由是本项目同时需要成员、知识库授权、文档版本、任务状态和检索；把这些数据与切片、向量放在一个事务数据库，可以减少组件、同步与恢复工作。这个判断服务于约半个月交付和工程学习，不意味着它在所有数据规模下性能最强。[1]

**两个纠正：Milvus Lite 不能与 Standalone 一概按大内存方案排除；MongoDB 自管理向量检索也不再是“只能用 Atlas”或“仍仅预览”。** Lite 3.x 已有发布物；MongoDB Community 的 Search/Vector Search 已于 2026-06-30 GA。[5][6][7]

本轮未安装、未压测。厂商能力事实已阅读一手来源，按研究流程均标 **medium / unverified**：未获不同发布者独立交叉验证。评分是工程判断，容量、吞吐和质量没有实测结论。

## 电脑 16 GB 后的重评与最终选型

用户随后补充电脑有 16 GB 内存，并提出把 Milvus 放在电脑。该信息使 Standalone 成为可评估的分机路线；下文原矩阵对 Standalone 的排除仅针对所有服务运行在 4 GB 服务器，不代表 16 GB 电脑必定不能部署。16 GB 是整机总内存，实际可分配资源仍需验证。[4]

分机部署还要验证服务器到电脑的可达性、电脑休眠或断网后的失败反馈、任务恢复及业务库与索引的同步。Netcatty 能从电脑操作服务器，不等于服务器已经可以访问电脑中的向量服务；Milvus 内部一致性也不等于与 PostgreSQL 的跨库事务。[12]

用户的主要顾虑是没有相关技术基础与面试材料。重评建议先完成服务器上的 PG＋pgvector RAG，用真实实现和验证建立理解，再把电脑 Milvus 作为可选对照实验，减少首版跨机依赖；这不是对两者性能优劣的实测判断。用户在重新推荐后答“可以”，首版 PG＋pgvector 因而成为已确认选型，学习与面试材料见 [INTERVIEW_PREP.md](/E:/aaa-project/rag/INTERVIEW_PREP.md)。

## 比较边界与五条路线

项目约束来自用户：FastAPI，4 核 4 GB Ubuntu，Web、后端、数据库同机，无 GPU，模型用 API；文档量、切片数、嵌入维度和并发未知。32 条题是评估集，不能据此推算数据规模。以下是整个项目所需组合，Milvus 并不自动取代业务事务库。

| 路线 | 一手来源所述事实 | 对本项目的工程判断 |
|---|---|---|
| PostgreSQL＋pgvector | 同库保存业务数据和向量，支持精确与 ANN 检索、事务与关联查询。[1] | 首选候选；组件较少，权限与文档状态更容易统一；4 GB 实际余量待测 |
| 业务库＋Milvus Lite | 当前发布包支持 HNSW、BM25、过滤与混合检索；面向本地与原型。[5] | 有效备选，适合专门学习 Milvus API；会增加业务库与索引同步工作 |
| 业务库＋Milvus Standalone | 官方 Standalone RAM 最低 8 GB、建议 16 GB；CPU 建议至少 4 核，默认组合包含 etcd、MinIO、嵌入消息队列。[4] | 超过当前整机 4 GB 约束，首版排除；不是“向量功能不适合” |
| 自管理 MongoDB＋mongot | Community 已 GA；mongot 是独立索引进程，需自行运维。[7][10] | 功能可行，不能因 4 GB 直接断言不能跑；部署与资源验证成本较高 |
| MongoDB Atlas | 由 Atlas 管理 mongot，保留文档、全文与向量检索能力。[10] | 托管备选；改变当前本机部署目标，须另核对预算、网络与部署选择 |

Standalone 的 8/16 GB 是 Milvus 部署的官方最低/建议值，不能当成“业务库＋Web＋worker”的整项目预算。MongoDB 的 mongot sizing 中，向量优先的 Low-CPU Small 建议 8–16 GB，High-CPU Small 建议 4–8 GB；这是搜索组件的建议起点，**不是启动最低值，也不是本项目 4 GB 可用性证明**。[4][11]

## 检索、权限与一致性

**PostgreSQL。** pgvector 默认精确检索；按需要引入 HNSW 或 IVFFlat。ANN 会用召回换速度；过滤条件在 ANN 扫描后应用可能导致结果不足，需要评估过滤列索引、迭代扫描等。HNSW 构建与查询都有内存成本，示例中的大内存参数不能照抄；连接池、work_mem、维护任务须与 FastAPI、worker 共用内存预算。嵌入模型还需匹配所用类型与 ANN 索引的维度上限。[1][2]

同库可在事务中切换当前文档版本、切片和向量，使删除与发布更易一致；嵌入 API 和文件系统仍在事务外，要有任务状态、幂等、失败重试与清理。这是推荐设计，不是选数据库后自动具备的行为。[1]

**Milvus。** Lite 3.2.2 的 PyPI 发布日为 2026-10-13，元数据仍标 Beta；已发布能力不能当成生产稳定性保证，也不能套用旧 2.4 的全部限制。其每个 data_dir 只能由一个进程使用，同一 collection 写入需串行，无内置认证/RBAC/TLS；独立导入 worker 与 Web 多进程应通过单一索引拥有者或本地服务协调，不能直接各自打开同一目录。[5][6]

Standalone 的 Strong、Bounded 等一致性级别管理 Milvus 内部数据可见性，默认 Bounded；即使选 Strong，也不产生与业务库的跨库事务。两条 Milvus 路线均需稳定切片 ID、版本号、幂等 upsert/delete、任务与补偿对账；向量库只是可重建检索索引，业务授权仍有明确事实来源。[12]

**MongoDB。** 当前官方矩阵列出 mongot 1.70.1+ 与 MongoDB Server 8.3 的配对；Linux 安装要求 Community 8.3+、已初始化 replica set 和 keyfile。不能照搬 2025 年 8.2 预览教程，也不能把普通 mongod 单进程安装当成已具备向量检索。mongot 经变更流维护独立搜索索引，业务数据写入和索引可查之间要考虑同步窗口；MongoDB 自动维护同步，仍须验证上传后可见、更新、删除及重建。atlas-local 单容器仅供开发评估，官方不将其列为生产目标。[8][9][10]

**共同授权边界。** 三者的过滤条件都不会自动理解“用户当前有权访问哪些知识库”。建议由后端依据当前授权计算库范围，向量与关键词两路都带限制；送入模型、展示引用、下载原文前检查有效版本与权限。撤权不能只等待向量库中的 ACL 副本更新；缓存、会话历史、任务和 API 同样要覆盖。这是本项目的实现要求推导，不能用厂商 RBAC 代替知识库级产品授权。

## 中文、型号与错误码

pgvector 管向量，不附送中文词法检索；PostgreSQL 全文检索依赖 parser、dictionary 与配置。可参考 MaxKB 的中文预分词思路，但候选实现需确保文档和查询切词一致，保留型号、版本和错误码的精确匹配字段；PG 原生相关性排序不能直接称为 BM25。[1][3]

Milvus 具备 BM25 与 jieba 分词配置，MongoDB Search 具有 smartcn 等中文分析器；这些能力减少部分自建工作，仍需验证技术术语、连字符和中英混排，不直接把 Standalone 分析器全部视为 Lite 已验证兼容能力。[5][13][14] 建议两路召回后融合、必要时重排，用相同资料和问题比较遗漏；换数据库不能补救扫描/OCR 错误或不合适分块。

## FastAPI、交付成本与选择矩阵

三者都有 Python 接入路径：pgvector-python 支持 SQLAlchemy、psycopg、asyncpg；Milvus 用 pymilvus；MongoDB 有 PyMongo Async 与官方 FastAPI 示例。FastAPI 本身不构成排除任何候选的理由。[5][15][16]

以下权重为研究建议，用户可重权衡；分数 1–5 越高越合适，衡量当前项目适配性，**不衡量实测速度、内存或产品优劣**。“部署资源管理”仅评组件、进程与运维安排的复杂度，不代表已测内存优势。Standalone 因部署约束、Atlas 因改变部署目标不参与本机方案排名。

| 方案 | 部署资源管理 30% | 半月交付 25% | 业务与索引一致性 25% | 中文词法 10% | 退出成本 10% | 加权 |
|---|---:|---:|---:|---:|---:|---:|
| PG＋pgvector | 4 | 5 | 5 | 3 | 4 | 4.40 |
| 业务库＋Lite | 3 | 3 | 3 | 4 | 4 | 3.20 |
| 自管理 MongoDB | 2 | 3 | 4 | 5 | 3 | 3.15 |

评分依据是上述组件数量、版本/进程限制、同库事务与词法能力，而非文档中的性能宣传。Lite 与 MongoDB 分差很小，不据此声称二者有显著优劣。[1][5][8][9][10][13]

本期总成本重点是运维、备份和恢复、双库同步及调试时间；未核定云价、商业支持费或月费，不给金额。PG 同库事务是首选的主要优势；其最强反对理由是中文词法要自己组织、ANN 过滤与小内存调优未必省事。**次选 Lite**：用户若将学习 Milvus 作为单独目标，能接受单索引拥有者和同步工作，可优先做该路线实验。已有 MongoDB 业务资产、确需丰富 Search 能力或愿改用托管时，MongoDB 权重会提高。

最便宜的可逆措施是保留清晰检索接口、稳定切片 ID、原文/版本、嵌入模型及维度元数据，不提前实现三套数据库。以后若真实数据证明 PG 的过滤召回、延迟或资源达不到目标，再用同一数据重测 Milvus/MongoDB；升级硬件后再考虑 Standalone。

Mary 的产品侧交叉核对同意优先验证 PG 路线：交付约束、权限与版本生命周期、可解释工程经验是主要考虑。她同时指出，复杂手册解析、OCR／图意与引用定位是本期主要实施风险，选择数据库不能代替这些验证；该意见不自动成为用户的最终选型。

## 最小验证计划与未决项

1. 先记录代表性资料量、解析后切片数、嵌入维度、目标并发与磁盘；千问生成 API 的选择不自动确定嵌入、重排、OCR。
2. 在实际 4 GB 整机上先验证 PG 候选，限制解析并发，测空闲、导入、建索引、查询、重建和重启后的内存/CPU/磁盘及 p95；以精确检索作为 ANN 召回对照。
3. 用四场景评估题补充中文术语、型号、错误码和严格权限过滤样例；单独验收跨用户/跨库隔离、撤权、删除、版本切换、重试与崩溃恢复。
4. 若首选不达标，或用户明确选择学习 Milvus/MongoDB，再在同数据、同模型、同条件下跑对照。记录真实结果后决定采用，不能先承诺可容纳多少切片。

## 来源与时效

技术来源均在本轮读取，访问日期统一为 **2026-10-15**；n.d. 表示页面未署发布日期。所有来源事实置信度为 medium，独立核验状态 unverified；本文工程建议另行标明，不冒充实测。

| 编号 | 支持内容 | 发布者与直接来源 | 发布日期 |
|---|---|---|---|
| [1] | PG向量、事务、ANN过滤与内存 | [pgvector维护者：README](https://github.com/pgvector/pgvector) | n.d. |
| [2] | PG资源与并发内存 | [PostgreSQL：Resource Consumption](https://www.postgresql.org/docs/current/runtime-config-resource.html) | n.d. |
| [3] | 全文检索配置 | [PostgreSQL：Configuration Example](https://www.postgresql.org/docs/current/textsearch-configuration.html) | n.d. |
| [4] | Standalone最低/建议资源与依赖 | [Milvus：Installation Requirements](https://milvus.io/docs/prerequisite-docker.md) | n.d. |
| [5] | Lite已发布能力、Beta、进程与写入限制 | [Milvus：PyPI 3.2.2](https://pypi.org/project/milvus-lite/3.2.2/) | 2026-10-13 |
| [6] | 3.x重写与正式发布记录 | [Milvus：Releases](https://github.com/milvus-io/milvus-lite/releases) | 3.2.1：2026-08-25 |
| [7] | Community Search GA | [MongoDB：Community GA公告](https://www.mongodb.com/products/updates/now-ga-mongodb-search-and-vector-search-for-community-edition/) | 2026-06-30 |
| [8] | 自管理版本与平台矩阵 | [MongoDB：Compatibility and Requirements](https://www.mongodb.com/docs/search/self-managed/current/deployment/compatibility-requirements/) | n.d. |
| [9] | Linux副本集与认证前提 | [MongoDB：Linux Installation](https://www.mongodb.com/docs/search/self-managed/current/installation/linux/) | n.d. |
| [10] | mongot同步架构、Atlas与local边界 | [MongoDB：Self-Managed Search](https://www.mongodb.com/docs/search/self-managed/current/) | n.d. |
| [11] | mongot资源建议起点 | [MongoDB：Sizing Quickstart](https://www.mongodb.com/docs/search/self-managed/current/resource-planning-sizing/quick-start/) | n.d. |
| [12] | Milvus一致性级别 | [Milvus：Consistency](https://milvus.io/docs/consistency.md) | n.d. |
| [13] | Mongo中文分析器 | [MongoDB：Language Analyzers](https://www.mongodb.com/zh-cn/docs/search/indexes/analyzers/language/) | n.d. |
| [14] | Milvus中文分析器配置 | [Milvus：Jieba](https://milvus.io/docs/jieba-tokenizer.md) | n.d. |
| [15] | PG Python生态 | [pgvector维护者：pgvector-python](https://github.com/pgvector/pgvector-python) | n.d. |
| [16] | Mongo异步FastAPI集成 | [MongoDB：PyMongo FastAPI Tutorial](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/integrations/fastapi-integration/) | n.d. |

版本/兼容性按 1 个月窗口复核；脚本按月份计算，动态页以本次访问月作为复核基线，得到 **2026-11-01**。GA 历史公告按 3 个月窗口已触发复核，本轮已用当前安装和支持矩阵再次检查其持续可用性。[8][9][10] 采用前及升级时重新核验；超过两个季度的选型结论整体刷新。
