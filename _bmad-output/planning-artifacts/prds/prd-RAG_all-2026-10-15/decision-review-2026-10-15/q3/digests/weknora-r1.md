# WeKnora Q3：分块、检索范围与引用来源的窄路径摘录

固定版本：`a37a1bc51ad85d096df341f6d3a098f60d586f52`。本轮只核实静态实现，不运行系统，不提出本项目设计。

证据获取：分块/索引部分读取任务指定的官方导入快照；检索和引用部分通过 GitHub connector 本轮直接读取固定 SHA。Q1 digest 仅用于定位官方仓库，不继承其事实或日期结论。共读四个源码文件，其中 parser facade 仅用于确认取证入口，未作为核心 claim。

| ID | 核心事实（严格限定所读代码） | 官方永久来源 | 来源元数据与限制 |
| --- | --- | --- | --- |
| WQ3-1 | Go 侧将 ChunkSize、ChunkOverlap、Separators、Strategy、TokenLimit、Languages 传给共享的 splitter 配置规范化函数；处理 ParsedChunk 时，将 Content、ContextHeader、序号、起止偏移和 SourceLocators 写入文本块对象，并绑定 TenantID、KnowledgeID、KnowledgeBaseID。这里证明配置与块对象的衔接，不证明所有格式实际使用同一种切分器。 | [knowledge_process.go L321–332](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L321-L332)、[L571–600](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L571-L600) | publisher=Tencent/WeKnora；提交日期/文件日期=未知；accessed=2026-10-15；confidence=medium / single primary source, independently unverified；本轮读指定导入快照，未重新校验文件哈希。 |
| WQ3-2 | 块先通过 CreateChunks 写入数据库；满足 NeedsEmbeddingModel 且模型可用的条件后，才为 textChunks 构造索引项，索引项以 chunk.ID 为 SourceID/ChunkID，并携带文档和知识库 ID。索引 Content 来自 buildKnowledgeIndexContent(knowledge, chunk.EmbeddingContent())；这使索引与原块存在显式 ID 衔接，不等于证明索引事务原子性或检索质量。 | [knowledge_process.go L640–695](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L640-L695) | publisher=Tencent/WeKnora；提交日期/文件日期=未知；accessed=2026-10-15；confidence=medium / single primary source, independently unverified；同上，静态实现。 |
| WQ3-3 | 受约束目标检索分支将 TagIDs、ScopeTagIDs、召回阈值、MatchCount 等装入 SearchParams；当目标类型为具体文档时再加入 KnowledgeIDs，然后把目标 KnowledgeBaseID 与这些参数传给 HybridSearch。该调用设置 SkipContextEnrichment=true。这里只证明过滤/范围参数被传递，尚未追读 HybridSearch 或底层存储如何实施过滤，也未核验权限覆盖。 | [search.go L557–583](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/chat_pipeline/search.go#L557-L583) | publisher=Tencent/WeKnora；提交日期/文件日期=未知；accessed=2026-10-15；confidence=medium / single primary source, independently unverified；本轮直接读取官方固定 SHA。 |
| WQ3-4 | 对已改写内容的结果，引用来源装配会筛掉禁用、不同文档/知识库、空内容以及 parent_text 块；选中的来源恢复原块 ID、正文、序号、SourceLocators、起止偏移等，再加入 CitationSources。展开函数按来源 ID 去重；若结果被改写而没有查到 CitationSources，会跳过该结果，避免把扩展上下文直接当成原始证据。这里证明引用来源的数据装配规则，不证明最终模型提示词/前端引用定位均正确。 | [citation_sources.go L96–164](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/chat_pipeline/citation_sources.go#L96-L164)、[L169–191](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/chat_pipeline/citation_sources.go#L169-L191) | publisher=Tencent/WeKnora；提交日期/文件日期=未知；accessed=2026-10-15；confidence=medium / single primary source, independently unverified；本轮直接读取官方固定 SHA。 |

可据此复述的局部衔接：ParsedChunk → 带位置/来源信息的 Chunk → 以块 ID 关联的索引项；目标检索把文档/标签范围传给 HybridSearch；引用装配把改写结果关联回带原块身份的 CitationSources。三段有显式数据字段衔接，但本轮没有跑通端到端链路，也没有追读上下文模板、底层过滤或重排实现。

停止边界：核心四条已有单一官方来源支撑；未穷尽检索器、重排、父子块，不外推权限全覆盖、性能、召回率或引用正确率。
