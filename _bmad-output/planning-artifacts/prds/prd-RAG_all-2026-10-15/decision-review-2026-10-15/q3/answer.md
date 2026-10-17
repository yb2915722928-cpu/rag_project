# Q3 回答：先把证据链闭合，再凭实测优化

TR→TS 已完成。选择“结构块→API 向量→授权精确检索→最多五块上下文→结构化答案→后端引用”。这是受托设计，尚无质量、延时或费用实测。

## TR：首轮足够支持选择的事实

| 参考 | 已核实及可借鉴点 | 官方来源 |
| --- | --- | --- |
| WeKnora 分块 | 块保存来源位置；索引以块 ID 关联原文，适合把检索与核验衔接。 | [处理与索引](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L571-L695) |
| WeKnora 引用 | 检索传文档/标签范围；改写内容须关联原块引用来源。未证明完整权限覆盖。 | [检索](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/chat_pipeline/search.go#L557-L583)、[引用](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/chat_pipeline/citation_sources.go#L96-L191) |
| MaxKB 检索 | 多库检查 embedding 一致；查询带库和 active 条件，结果回取段落。 | [检索步骤](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py#L35-L79)、[过滤](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/vector/pg_vector.py#L149-L196) |
| MaxKB 上下文 | 检索→消息→生成分步；段落上下文按字符参数截取，另拼历史，不能照搬其历史权限假设。 | [流水线](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/chat/serializers/chat.py#L340-L360)、[消息构造](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/generate_human_message_step/impl/base_generate_human_message_step.py#L22-L72) |
| 官方机制 | pgvector 默认精确检索；embedding 是独立 API 能力，维度与查询/文档用途需单独配置。 | [pgvector](https://github.com/pgvector/pgvector#querying)、[embedding API](https://www.alibabacloud.com/help/en/model-studio/text-embedding-synchronous-api) |

## TS：选定的八项衔接

1. **块先保持结构。** 章节路径作前缀，正文按段落；初值约 600 中文字、重叠 80 字，仅是可调起点，且受实际模型 token 上限约束。超长正文再按句拆；表格按行组拆并重复表头、单位与适用条件；图意说明连图号、图注和来源位置成块，没通过图意校核就标缺陷。不得把整章塞成一块规避预算。
2. **embedding 独立版本化。** 块保存文档版本、分块配置、定位；向量绑定 embedding 配置 ID、供应商/型号与可得模型版本、维度、归一化策略及索引版本。初选余弦距离、两端同一 L2 归一化策略；拒绝空/零/维度异常向量。具体型号接入时定，变更则重建候选索引后切换，不能混查。
3. **B0 只做精确向量。** 显式步骤先取当前授权空间/库交集，再查询其 active_version、未删除且校核通过的块，按余弦距离排序。旧版只供有权引用回看。Q1 短 Session 与输出前复核沿用；代价是精确扫描耗时待测。关键词、重排、ANN 均待失败证据触发。
4. **五块是整次请求上限。** 普通问答一次检索；对比按显式“对象×条件”做子检索。条件按请求原序、对象按文档 ID 升序，各路内部按距离/块 ID 排序，轮流取第1名、再第2名，去重直至五块或耗尽，不比较跨查询分数。开发可观察更多候选，只有最终五块进入生成和覆盖统计；不得追加邻块、整表或旧回答，缺证据逐格报不足。
5. **四场景共用步骤、区分 schema。** 企业查询输出流程/材料/条件/负责人；排障接收版本/环境/日志，输出候选原因/检查顺序；对比每格输出满足、直接证据支持的明确不满足、不足或冲突，并挂证据；手册接收型号/参数，输出步骤/数值单位/限制及页表图定位。逐格检查证据，不能凭一个 TopK 宣称全表核验完成。
6. **生成与引用受证据约束。** 上下文只含最终块原文和必要元信息；资料指令视为数据。输出事实及本轮白名单 evidence_ids；后端验证归属、状态和定位，原件由 resolve 再授权打开，不信模型下载地址。仅本地无语义规范化，仍不合结构或 ID 越界则整答可见失败，不自动修正或展示草稿；语义支撑仍须验收。
7. **追问仍是一轮新查询。** 仅有限同空间、复核依赖后可见的历史辅助消解代词和改写，默认不把旧答案交给最终生成器；历史不算新证据。重新检索、上下文前及返回前重新授权，失权/删除的回答整体隐藏；改写不能扩大库、恢复旧版，跨空间新建会话。
8. **逐轮留真实证据。** 首次调优前冻结 32 题（每场景 6 可答、2 不足）和必要证据单元，开发题独立。固定最终 K=5，记录逐题 B0/上一保留轮/本轮的覆盖、事实与引用、任务通过、耗时、资源和每次 API 用量/真实费用；失败、重试、持平与退步全部保留，没有计价只报用量。

## 初学者复述

先把资料切成带版本和位置的小证据，向量负责找相近内容。服务器先限定你当前能看的范围，最多给模型五块；模型回答时只能引用这些块。追问可借历史理解“它”是谁，但仍重新查资料、查权限。没找到、结构没解析好或五块装不下，都明确说缺什么。

## 验证安排（尚未执行）

- 核对章节、超长表格/单位、OCR及真正图意题，检查每块可回到原位置。
- 跑 32 冻结题与 SM-1～SM-5，核对五块必要证据覆盖和引用语义；不足/冲突逐格检查。
- 单列权限负例：跨空间/库、旧版、tombstone、撤权历史/追问/引用，以及生成期间撤权。
- 检查多次子检索最终合计≤5、未知引用 ID 被拒、embedding 配置不一致被拒及真实失败成本记录。

首轮证据已够，停止扩查。静态源码单源置信度为中；模型、预算初值与质量效果待接入验证。user_only_missing：无。后续追问继续由本 Mary 闭环。

