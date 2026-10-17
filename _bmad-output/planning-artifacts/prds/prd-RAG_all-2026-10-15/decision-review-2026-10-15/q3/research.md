---
type: technical
topic: Q3 RAG B0 shared pipeline
decision: TR explore then TS select
source: native-run
status: complete
created: 2026-10-15
updated: 2026-10-15
claims_verified: 0
claims_unverified: 4
---

# Q3 研究报告

选择结构块＋API embedding＋当前授权范围内精确向量检索＋整次最多五块上下文＋结构化答案/后端引用；四场景共享步骤，分别约束输入与输出。完整决定见 [回答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/answer.md:1)，细节和限制见 [证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/evidence.md:1)。

## TR：证据支持的内容

WeKnora 将来源定位保留到块，索引用块身份关联原文，改写检索内容回到原块引用来源；仅核实局部衔接，不外推完整权限验收。[1]

MaxKB 有结构切分工具，检索检查多库 embedding 一致、传库/active 范围，并将检索、消息和生成分步；历史消息拼装本身不等于当前权限复核。[2]

pgvector 支持余弦和带 WHERE 的精确向量查询，默认精确检索；“精确”仅指所用向量距离排序，不代表任务证据必然充分。[3] 阿里云 embedding 是独立 API 能力，维度、query/document 用途及用量字段须按实际接口核对，不由问答模型名推定。[4]

各主张均为本轮读取的单一官方来源，置信度中、未独立发布者验证；尚无运行成绩。

## TS：收敛与取舍

八项选择包括结构块、embedding/索引配置一致、授权精确B0、全请求K=5、四场景schema、证据白名单/resolve、追问重检索重授权、逐题冻结评估。理由为既定 PG/显式步骤下便于解释和核验；代价为纯向量术语召回、扫描耗时和复杂比较五块覆盖仍可能失败。关键词、重排、ANN 留待开发题中具体失败假设触发。

同题追问已修正合并：按固定子查询序列作名次轮转，不直接比较跨子查询余弦分数。K 限候选块，SM-2分母仍为原标注证据单元；结构/ID不合法采取可见整答失败，不自动追加模型修正。见 [追问答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/followup-answer.md:1)。

## 组合判断与边界

共同值得借鉴的是“检索结果可回到原始证据”的数据身份和步骤分工；本项目仍必须自行实施 active_version、删除阻断和当前授权。最强反对理由是复杂任务可能被五块预算限制，不能通过删事实、全拒答、扩大块或偷塞上下文获表面通过。本文不提出另一套评分体系。

未开 red-team 研究扩查。四场景、SM-1与每场景5/6、原 SM-2口径保持。32 冻结题独立于开发题；权限负例单列。没有代码、产品测试或收费 API 调用。

## 未知与停止

模型实际型号/维度/可观察版本、图意产物、分块与轮转初值效果、4C4GB耗时/内存和真实API成本未测。均为接入验证，不是 user-only 缺口。user_only_missing=无。首轮已覆盖选择，停止扩大取证；John同题追问已闭环，Q3收口。

## 来源表

访问日均为2026-10-15；文件发布日期未知，不把访问日当发布日期。固定源码3–4条核心事实及永久行号保存在digests。

| 编号 | 支持范围 | 发布者与来源 | 发布日期 | 置信度 |
| --- | --- | --- | --- | --- |
| [1] | 块/索引/检索参数/引用来源 | [Tencent/WeKnora 固定提交](https://github.com/Tencent/WeKnora/tree/a37a1bc51ad85d096df341f6d3a098f60d586f52) | 未知 | 中，未独立验证 |
| [2] | 切分/模型一致/过滤/消息步骤 | [1Panel-dev/MaxKB 固定提交](https://github.com/1Panel-dev/MaxKB/tree/0fa9a0dae8850c1878f087f0d81c974c1d424b06) | 未知 | 中，未独立验证 |
| [3] | 精确向量/余弦/过滤 | [pgvector README](https://github.com/pgvector/pgvector#querying) | 未知 | 中，未独立验证 |
| [4] | 独立embedding API参数与用量 | [阿里云同步embedding API](https://www.alibabacloud.com/help/en/model-studio/text-embedding-synchronous-api) | 未知 | 中，未独立验证 |

## 时效

已运行 recon_kit staleness：来源发布日期不可核实，故不虚构日期输入，已知日期清单为空，earliest_recheck=null；这不代表来源永不过期。固定 SHA 描述的是该版本历史实现；实际集成前重新读具体版本与API契约。若超过两季度才实施，TS必须刷新。滚动API/兼容性类按技术包1个月窗口复核，但因发布日期未知目前不能由脚本算出可靠日历期限。

