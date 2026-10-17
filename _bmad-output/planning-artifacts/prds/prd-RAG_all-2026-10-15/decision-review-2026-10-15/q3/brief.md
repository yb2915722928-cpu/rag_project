# 研究简报

- 决策：选择四场景共享、可解释并可逐题验收的 B0；参考项目为证据入口，不整体移植。
- 阶段：先 TR technical/explore；已获得足够静态事实后再 TS technical/select。
- 维度：结构块/embedding 一致性；授权精确检索；上下文与引用；历史与固定证据预算。
- 硬门槛：PG＋pgvector；Q1 短 Session/显式步骤/统一授权；Q2 active_version/tombstone/定位；四场景与最终 K=5；32 冻结题；真实成本。
- 偏好顺序：规则一致、学习与维护简单、少依赖、可替换。无负载数据，不虚构权重和分数。
- 候选：精确向量共享链路；向量＋关键词/重排；ANN；整套参考框架。后两类及额外召回器留到实测触发；不是预先断言无价值。
- 取证计划：首轮每项目 3–4 条事实，pgvector 与 embedding 官方机制补足；本轮读固定 SHA，而非宣称追踪最新全量。最多一轮足够即收敛，不做评分产品研究。
- 拓扑：窄幅并行；WeKnora 摘录子代理，Mary 负责 MaxKB/官方机制/TS。引用语义核对另用已完成子代理。
- 输出：仅本目录 Markdown；headless 省略交互 gate 和 HTML。Python 替 uv 已获调用方授权。外部来源访问能力为 GitHub connector 与 harness web。

