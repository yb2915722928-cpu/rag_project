---
title: 第二轮 IR · John B 预算实际改稿定点复核
date: 2026-10-16
reviewer: John B
status: targeted-review-not-final-gate
finding: F3
finding_status: CLOSED
---

# John B 对 F3 的实际定点复核

已读取现行实施契约第 3.5–3.8、5.2–5.3 节，以及同题原 Mary R2-M2 的主答、优先追问收口和取证说明；按原发现触发与关闭条件核对，没有开始新轮泛审。**F3：CLOSED（规划层面）。** 此时 F1／F2／F4 和两项明确化均已有前次实际定点关闭；完整合稿与最终 IR 尚待 A 通知，不把本稿直接当总体最终 PASS。

## 原反例与关闭证据

| 需关闭的具体反例 | 实际权威落点／判断 |
| --- | --- |
| 字符合法却使协议读取／大目标集合先放大；把文件上传误套 JSON 上限 | [契约 §3.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:186)，范围 186–196，区分部署 H、新操作 B、实际模型 M；JSON 流式 1MiB／结构有限，retrieval 与 answer 同受库／文档／问题／条件合计约束。第196行明确 H 不套二进制 PUT／下载／ZIP／上游响应，原20MiB起点继续有效，各自另有字节／磁盘／适配器保护。 |
| 旧 Key 遇业务上限下调被暗重做；认证前 413 泄露操作 | [准入与规范输入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:198)，范围 198–200，H先保护读取，认证／目标检查后旧 Key 按原规范化／schema和完整输入指纹匹配，新 Key 才用新 B/M。紧急 H 可拒旧大 POST，但无未认证操作ID回传，已知本人操作经受控 GET 恢复；不迫使换 Key，不重复预留。问题／日志内部空白、行序、数值和单位不被预算器暗清洗。 |
| 只算证据或另一端点的 tokenizer，未计模板／输出／思考 | [实际 profile 与计数](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:206)，范围 206–214，分用途登记模型／端点／tokenizer／完整模板／SDK／I/O/总上下文、输出语义和思考；S/M/H/E完整序列计数，R_answer/R_think与margin分开受限。不能字符除常数、猜20%封装或将字节称实测token。未知模式仅阻该模式生成；无需取得厂商私有权重，P0可选同千问路线内可核模式。 |
| 用 OpenSearch 接口代证 DashScope 完整消息计数 | [计数条款](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:210)与 [Mary 取证说明](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/evidence.md:21)明确产品／端点／鉴权不同，不据此增加 OpenSearch 或声称百炼能力已经证实。P0的待核能力没有被包装成已具备。 |
| query embedding 在生成前已偷偷截日志／暗拆批增费 | [实际 embedding 字符串](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:216)明确完整question／当前日志与适用条件、允许的完整有限用户历史，比较按完整本条condition。每条先展开／计数／留hash，query批1串行；实际每条和批限制都验，不暗拆当前输入或用额外LLM压缩。文档超长走来源结构分块与新候选，旧历史不原地改。 |
| 已知本体／完整输出装不下，却先花embedding费；未证生成能力被伪装为正常答案 | [固定分支顺序](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:218)，范围 218–224，可靠早判必超则422且无预留／外发；只是生成profile未证且embedding可执行时，可固定为有费用守卫的检索后分支，预留一次，202不承诺生成能力。候选非零时未证503／已知超限422，终态释放，已花embedding照记。 |
| 真实零候选要求先证明 LLM 最大输出，或预算裁空伪装 NO_CANDIDATES | [零候选与预算裁空](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:221)，范围 221–224，必须全部子检索成功且原始最终候选确为0，才用完整确定性普通不足／全格NO_CANDIDATES，不调用LLM且正常计1。未执行／部分失败不能此路。原候选有但预算裁至0属于CONTEXT_EVIDENCE_BUDGET_EXHAUSTED失败，不变成不足题。 |
| 不足五块或裁剪后仍把整块算金标命中 | [证据裁剪](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:223)，范围 223–224，固定原五块次序，不换块／加邻块／全文；整条辅助历史优先剔除，再按逆优先序从连续片段尾部删登记原子组，表头／单位／型号／条件随事实保留，不能造LLM摘要。catalog仅实见范围、offset／hash／原因，不以chunk_id整块冒充覆盖。 |
| 24格的完整输出无空间证明，或128档成为裁返值／漏条件的借口 | [输出证明与紧凑档](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:214)及 [comparison-compact128](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:234)，以本次实际ID、全部格／数组和最大合法四态分支计算规范完整载荷，再按已证tokenizer上界换算。外层512不变，128是提示／校验／快照一致的生成子契约；生成超128失败，绝不截返值；新档重预算重验，不减少必要事实或改原金标。未承诺任意小模型支持4×6。 |
| 普通回答结构不有限，靠空事实或遗漏量值凑完整 | [answer.v1有限生成载荷](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:236)，范围 236–250，给出summary、facts、quantity、conflict_sides、gaps、clarifications的有限类型、长度、数组及交叉约束；按场景保必要流程／原因／检查／型号／参数单位与限制，未知项明确gap。四态有非空分支要求，冲突有双方实见证据；空事实不是完成事实回答。生成子档不放宽原任务语义验收。 |
| length时JSON恰能解析就放行，或自动额外付费修复 | [结束与结构失败](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:226)明确length／截断／缺完整终止一律ANSWER_TRUNCATED；正常终止但缺格／非法引用／子契约不符为校验失败。均整答失败、一次释放、原费用／unknown保留，同Key回原失败，无LLM补格／修复。 |
| 失败改分母、空答案SM-3填100%、成本或计次混淆 | [SM条款](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:228)与 [错误字典](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:361)，范围 361–366，调用前拒绝无模型上下文则SM-2分子0，不删题；生成后失败按实见上下文记覆盖但SM-1仍失败；事实分母0报N/A并列失败。产品预留／释放与真实已发费用分开，不将预算失败移入8条不足题或减少必要金标。 |
| 纯检索／24子查询绕限流，旧“等待4”留下第二套并发语义 | [统一查询gate](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:256)，范围 256–260，retrieval／answers／comparisons共享部署active2／user1，query批1／串行最多24，逻辑槽不足直接429，无等待逻辑队列，明确替代旧等待4。已受理内部rate gate仅在原deadline内有限等，不持Session；物理槽须确认旧传输停止才可复用。RPS/TPM取有限配置与已核账号适用约束较小者，未知不派发；不把拟定2/s或1/s冒称账号额度。 |

## 关闭范围与真正停止点

原 B-R2-02 与 A-04 合并组需要的是明确的拒绝／失败／正常零候选／输出与计次政策，现已落到权威契约和错误字典，开发者无需自己发明分支。原 Mary 的[优先追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/followup-answer.md:89)保留了对应负例，全部未运行。

P0仍须实际验证匹配的模型／计数依据／消息封装／输出参数、完整最小四场景载荷通过同一预算及生成子契约、可发布的实际输入／矩阵范围，以及4GB资源与调用限额；不能将“规范结果最短可写出来”误当随机生成成功或最坏输出预算通过。紧凑档若表达不全，需要新档／容量充分的已核模式重验，保留失败，原SM门槛和K=5不降。若实际无法找到可用profile，对应能力和整期完成仍阻断，不能以本文CLOSED当运行通过。

本次无新的material规划发现，也未撤回前两份封存初评的原始判断。下一步仅按最终合稿做现有组与同步文件的收尾复核。
