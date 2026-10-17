# 官方机制摘录

访问日期：2026-10-15。发布日期均未知；单一官方来源，confidence=medium，independently unverified。无基准性能结论、型号选择或价格结论。

1. [pgvector README：Querying / Indexing / Filtering](https://github.com/pgvector/pgvector#querying) 列出余弦距离 <=>、ORDER BY/LIMIT 查询；默认 exact nearest-neighbor；添加 HNSW/IVFFlat 则为 approximate nearest-neighbor；过滤示例带 WHERE，建议过滤列索引，近似索引过滤发生在索引扫描后。这里只支持 B0 可用精确模式及应用过滤的机制，不证明本项目正确授权或业务召回完美。其“perfect recall”指所选距离下精确近邻，不代表业务必要证据全部检出。
2. [阿里云 embedding 同步 API](https://www.alibabacloud.com/help/en/model-studio/text-embedding-synchronous-api) 定义独立 model/input/向量维度参数、返回 embedding 与 usage/request ID；说明模型输入与批量上限不同，并建议检索区分 query 和 document 用途。OpenAI 兼容接口使用 dimensions，DashScope HTTP 参数表使用 dimension，不能把两套字段拼成同一契约。该页未成为问答模型可当 embedding 的证据；也未据此假定输出已经 L2 归一化。
3. 本项目选余弦＋显式一致的归一化，属于设计决定；文档支持的是可用距离与 API 字段。API 输出实际维度、非空/有限数/非零以及提供商模型版本可观测程度必须接入验证。
4. 未采用网页展示的新模型名、价格、长度数值作为本项目承诺；具体型号/版本/维度/地域端点/账单在实际接入时再次核对。本轮未调用任何收费模型 API。

原网页已本轮打开，读到 Querying/Indexing/Filtering 与 embedding 参数、usage 的对应小节；没有网页发布日期就不以访问日期冒充发布时间。

