# 官方来源摘要

访问日统一为 2026-10-15。仅列本轮直接读取的一手来源；无独立发布者交叉验证，confidence=medium、verification=unverified。动态文档未署发布日期的填 n.d.，不能用访问日伪造发布日期。

| ref | claim | source | publisher | pub_date | class |
|---|---|---|---|---|---|
| 1 | pgvector支持精确检索、HNSW/IVFFlat及同库ACID；ANN过滤可能少返回；HNSW内存与维度限制须检查 | https://github.com/pgvector/pgvector | pgvector维护者 | n.d. | compatibility |
| 2 | PG工作内存按操作/并发分配，不能把单机内存全分数据库 | https://www.postgresql.org/docs/current/runtime-config-resource.html | PostgreSQL | n.d. | patterns |
| 3 | PG全文检索需配置parser/dictionary，配置与切词影响词法检索 | https://www.postgresql.org/docs/current/textsearch-configuration.html | PostgreSQL | n.d. | patterns |
| 4 | Milvus Standalone最低8GB、建议16GB，CPU建议4核；默认依赖etcd/MinIO及嵌入消息队列 | https://milvus.io/docs/prerequisite-docker.md | Milvus | n.d. | compatibility |
| 5 | Lite3.2.2已于2026-10-13发布，PyPI标Beta；支持HNSW、BM25、混合检索、过滤，但每data_dir单进程、写入串行、无RBAC/TLS | https://pypi.org/project/milvus-lite/3.2.2/ | Milvus发布包元数据 | 2026-10-13 | compatibility |
| 6 | GitHub发布记录确认3.0纯Python重写，3.2.1已发布，不能只从main推断发布能力 | https://github.com/milvus-io/milvus-lite/releases | Milvus | 2026-08-25 | compatibility |
| 7 | Community Search/Vector Search于2026-06-30 GA，2025年仅预览的说法已过时 | https://www.mongodb.com/products/updates/now-ga-mongodb-search-and-vector-search-for-community-edition/ | MongoDB | 2026-06-30 | compatibility |
| 8 | 当前mongot1.70.1+支持矩阵列MongoDB8.3，8.2不再受支持 | https://www.mongodb.com/docs/search/self-managed/current/deployment/compatibility-requirements/ | MongoDB | n.d. | compatibility |
| 9 | Linux安装需MongoDB Community8.3+、已初始化replica set与keyfile | https://www.mongodb.com/docs/search/self-managed/current/installation/linux/ | MongoDB | n.d. | compatibility |
| 10 | mongot独立索引进程从mongod变更流同步；Atlas代管；atlas-local仅开发评估 | https://www.mongodb.com/docs/search/self-managed/current/ | MongoDB | n.d. | patterns |
| 11 | mongot低CPU Small建议8-16GB，高CPU Small建议4-8GB，均非4GB整项目最低值 | https://www.mongodb.com/docs/search/self-managed/current/resource-planning-sizing/quick-start/ | MongoDB | n.d. | sizing |
| 12 | Milvus有四种一致性级别，默认Bounded，Strong才保证最新可见；不等于跨业务库事务 | https://milvus.io/docs/consistency.md | Milvus | n.d. | patterns |
| 13 | Mongo语言分析器包含lucene.smartcn中文分析 | https://www.mongodb.com/zh-cn/docs/search/indexes/analyzers/language/ | MongoDB | n.d. | compatibility |
| 14 | Milvus支持jieba分词，可配置并run_analyzer核验；不直接外推Lite每个分析器均兼容 | https://milvus.io/docs/jieba-tokenizer.md | Milvus | n.d. | compatibility |
| 15 | pgvector-python支持SQLAlchemy、psycopg、asyncpg等Python接入 | https://github.com/pgvector/pgvector-python | pgvector维护者 | n.d. | compatibility |
| 16 | PyMongo官方FastAPI集成使用AsyncMongoClient | https://www.mongodb.com/docs/languages/python/pymongo-driver/current/integrations/fastapi-integration/ | MongoDB | n.d. | compatibility |

冲突处理：不沿用Milvus2.4文档约束评估3.x发布物；不把Lite3.2.2发布物等同稳定生产支持；不沿用Mongo2025预览教程排除2026自管理能力。未查到适用于本项目工作负载的独立性能或4GB整机容量证据。

两轮在版本、部署、检索与同步边界达到覆盖后停止。未解决：实际4GB峰值、索引过滤召回、OCR进程峰值、Python包与目标Ubuntu兼容性，均需后续原型测量。
