# MaxKB Q3 窄路径摘录

固定 SHA：0fa9a0dae8850c1878f087f0d81c974c1d424b06；publisher=1Panel-dev/MaxKB；文件与提交发布日期未知；accessed=2026-10-15；confidence=medium / single primary source，独立验证状态 unverified。仅证明静态实现，不是端到端运行或权限验收。

| ID | 事实与来源 | 限制 |
| --- | --- | --- |
| M1 | [切分工具](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/utils/split_model.py#L249-L295) 将树中的 block 转成带祖先标题的段落；post_handler_paragraph 先按换行累计，超限再按字符长度拆。此轮重读既有官方快照，未另校验哈希。 | 是所读工具的行为，不能推断每种文档均走此函数，也未证明表格关系均保留。 |
| M2 | [检索步骤](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py#L35-L79) 要求多知识库 embedding_model_id 一致，核验模型类型为 EMBEDDING；将改写问题或原问题向量化，再传库/文档排除/段落排除/top_n 等给 VectorStore。授权库函数是有条件的可选钩子。 | 不证明所有用户类型的实时权限均受此钩子保护。 |
| M3 | [pg_vector 查询](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/vector/pg_vector.py#L149-L196) 为每库构造 knowledge_id、is_active 过滤，可限定/排除文档与段落；多库结果按相似度合并取 top_n。检索步骤再以 paragraph_id 回查段落并装配文档/库名称等。 | is_active 不是本项目 active_version 协议的直接替代；此处未证明空间或 tombstone 逻辑。 |
| M4 | [简单应用流水线](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/chat/serializers/chat.py#L340-L360) 顺序添加 SearchDataset、GenerateHumanMessage、Chat；[消息构造](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/generate_human_message_step/impl/base_generate_human_message_step.py#L22-L72) 拼有限对话历史，把段落 title/content 放进 data 标签并受字符参数约束。 | 未核验最终引用展示；不能由该消息拼装断言历史重授权，也不照搬其字符截取写法。 |

本轮经官方 connector 导入 [检索片段](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/imports/maxkb-search.py.md:1)、[向量片段](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/imports/maxkb-vector.py.md:1)、[消息片段](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/imports/maxkb-message.py.md:1)、[流水线片段](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/imports/maxkb-pipeline.py.md:1)。各片段首行记录原来源，局部导入行号不冒充原文件行号。

停止：足够确认分工、模型一致与过滤参数；未穷尽搜索模式、重排、引用实现或框架依赖。

