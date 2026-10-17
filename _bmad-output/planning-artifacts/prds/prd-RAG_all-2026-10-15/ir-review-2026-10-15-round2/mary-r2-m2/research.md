---
type: technical
shape: select
topic: finite-request-token-output-budget
decision: 选择分层限界与完整生成预算契约
source: official-documents-and-fixed-source
status: complete
created: 2026-10-16
updated: 2026-10-16
verified_claims: 1
unverified_claims: 3
---

# R2-M2 技术研究摘要

选择“协议有限硬界／可调业务受理／实际模型适配器三层＋调用前完整预算”，保留四场景、整请求K=5、全部比较格与原评估分母。字符合法仍可能不满足 token 或输出预算。两个固定提交的所读路径将历史／当前提示／输出参数分别处理，不能直接据其字符或轮数参数证明本项目完整请求可容纳。[1][2] 千问型号尚未选定；本报告没有模型调用或成绩。

## TR：足以支撑选择的发现

WeKnora 的指定函数分别赋 MaxTokens／MaxCompletionTokens，构造 system＋history＋当前 UserContent；MaxKB 的指定函数以 dialogue_number 控制历史、max_paragraph_char_number 控制段落，再拼问题。二者独立互证的是这些静态路径的拆分结构，不能推出全仓不存在其他预算控制，也不是性能对照。[1][2]

阿里云说明 token 由实际 tokenizer 决定，真实用量以 API 统计为准；字符数不能作为通用精确 token 数。[3] 生成参数对思考／答案的口径与型号支持不同，length 为过长停止；不能用同一 max_tokens 设置保证所有型号的完整输出。[4] embedding 每条和批条数限制亦按型号，不能从问答型号推导。[5] 以上厂商事实为单发布者、中等置信度；未作独立发布者核证，ledger 标 unverified。

## TS：硬门优先的选择

| 方案 | 完整当前输入／全部格 | 调用前证明预算 | 禁截断伪成功／隐性修复费 | 结论 |
|---|---|---|---|---|
| 字符限额＋只裁证据 | 不保证 | 不保证 | 无法闭合 | 不选 |
| 有限 H/B/M＋精确计数或已证明上界＋完整输出预留 | 明确保留 | 必须通过 | length／缺格整答失败，修复调用0 | 选定，适配器验证尚未完成 |
| 供应方自动裁剪／事后多次模型修复 | 不保证 | 不满足 | 不满足 | 不选 |

偏好权重为完整性／审计50%、小栈实施30%、可逆性20%；只有一个候选过硬门，不虚列打分。选择的代价是预算记录和部分合法字符请求的明确拒绝。最强反对理由是 compact-128 reason 可能难以表达完整限定；所以保留外层512上限、新配置可升档重算，质量仍过原SM门槛。可替代计数器只限实际可靠的完整请求计数工具；它不替代受理／权限／真实调用账。

跨维度结论：协议finite能约束解析成本，但模型预算必须连 system/schema、当前本体、辅助历史、实际五块和完整输出一起算；一个合法短问也可能因完整24格的输出上界失败。容量有证明也不保证模型遵守结构或语义，因此调用前预算与调用后校验不可互相替代。这是本项目设计推论，不是厂商效果承诺。

## 下游绑定与未证范围

可直接合并的字段、固定算法、HTTP／受理／释放语义及负例已写入 [主答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/answer.md:30)，经John八项真实追问，以[同题收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/followup-answer.md:1)修订条款优先，供现行实施契约§3.2／5.2与既有P0采用。JSON限界不覆盖原件媒体；日志无新全局trim；P0用非思考、无tools/web的显式JSON文本提示；真实零候选不依赖LLM最大输出证明。首版batch1、子检索串行、三查询入口共同全局gate，明确替代旧等待4；产品次数与实际API费用分开。只裁实见证据，不裁当前日志／条件／格，SM分母不变。

未证问题都属于实际接入验证：具体用途型号与账号限制；tokenizer／chat template／schema隐藏开销的匹配或可靠上界；SDK自动行为；alias无法完全固定的剩余不确定性；最大4×6输入是否能通过；4核4GB并发与全部SM质量。未接入前profile为未验证，不宣称足够。无 user_only_missing、无外部交接、无新增产品范围。

## 来源表

| ID | 支持范围 | Publisher | Pub date | Accessed | Confidence |
|---|---|---|---|---|---|
| [1] | W1–W3：模型options、system/history/current及finish reason记录 | [Tencent/WeKnora 固定common.go](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/chat_pipeline/common.go#L35-L101) | 固定SHA，日期未取到 | 2026-10-16 | 中；与[2]共同静态观察高 |
| [2] | X1：历史轮数＋段落字符与问题拼装；非全仓结论 | [1Panel-dev/MaxKB 固定消息构造](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/generate_human_message_step/impl/base_generate_human_message_step.py#L22-L71) | 固定SHA，日期未取到 | 2026-10-16 | 中；与[1]共同静态观察高 |
| [3] | 实际tokenizer与usage口径 | [Alibaba Cloud 模型用量](https://help.aliyun.com/zh/model-studio/model-usage-statistics) | 动态页，未显示 | 2026-10-16 | 中，unverified独立核证 |
| [4] | 输出参数／thinking／length／JSON型号差异 | [Alibaba Cloud DashScope API](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-dashscope) | 动态页 | 2026-10-16 | 中，unverified独立核证 |
| [5] | embedding每条／批与用途差异 | [Alibaba Cloud 同步embedding API](https://help.aliyun.com/en/model-studio/text-embedding-synchronous-api) | 动态页 | 2026-10-16 | 中，unverified独立核证 |

完整固定路径／行号／读取失败范围与原始副本校验见 [evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/evidence.md:1)。

## 重核时点

staleness工具按本轮观察日作为显式替代锚点计算，不伪造动态页发布日期：兼容性1个月，静态模式24个月；[输入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/staleness-input.json)与[计算结果](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/staleness-result.json)保留该日期口径。最早计划重核2026-11-16；任何首次实际接入、模型／alias／SDK／端点／schema变化更早触发立即重核。固定SHA事实不会随分支移动改变，切新SHA必须另核。选择报告超过两个季度再采用时应refresh。
