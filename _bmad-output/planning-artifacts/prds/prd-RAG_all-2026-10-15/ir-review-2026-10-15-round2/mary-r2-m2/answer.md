---
question: R2-M2
author: Mary
status: superseded_in_part_by_followup
updated: 2026-10-16
research: technical TR + select TS, focused headless
---

# R2-M2 主答：先证明完整请求可容纳，再发出调用

主答已被John同题追问检验；JSON入口范围、日志规范化、P0可实施计数路径、普通回答生成schema、零候选先后和无等待gate，以[同题收口条款](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/followup-answer.md:1)为准，避免从本稿孤立抽取旧表述。

选择“协议有限硬界＋新请求业务受理限制＋实际适配器 token 核算＋完整输出预留”。字符合法只代表通过一种检查；不能代表 embedding、生成输入或完整 24 格输出一定装得下。保留四场景、全请求最终 K=5、32 冻结题、原金标证据分母与 SM 门槛。此处是受托设计，没有实现／接入／压测／模型成绩。

## TR：本轮新取证得出的窄结论

WeKnora 固定提交把 MaxTokens／MaxCompletionTokens、system、历史和当前消息分别组装；MaxKB 固定提交按历史轮数与段落字符数处理，再拼 question。后者的 query embedding 还有独立实际输入。以上只说明这些路径需要联合审视，不能证明任一参考项目全仓没有预算机制。[W1–W3、X1–X3 的固定 SHA／行号及本轮副本见证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/evidence.md:7)。

阿里云官方说明 token 取决于实际 tokenizer；输入／输出限制、embedding 每条与批条数限制按型号区分；思考与答案的输出参数口径并不通用，length 表示过长停止。JSON 模式支持也不能一概假设。[模型用量](https://help.aliyun.com/zh/model-studio/model-usage-statistics)、[生成 API](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-dashscope)、[embedding API](https://help.aliyun.com/en/model-studio/text-embedding-synchronous-api)。这些是适配约束，不是已选千问型号／当前账号实测能力。

## TS：选择、替代与代价

硬门先筛：①当前输入／格子完整；②调用前能证明预算；③不靠截断或额外付费修复兜底；④重传与成本守恒。偏好权重仅用于通过硬门的方案：可审计完整性 50%、同步小栈实施负担 30%、迁移可逆性 20%。因只有 B 过硬门，不伪造评分或吞吐数字。

| 候选 | 硬门 | 选择／代价 |
|---|---|---|
| A 字符上限＋只裁证据 | 不过：当前输入或输出本身可能超限 | 拒选。可保留字符校验作为一层，不能替代 B |
| B 分层有限限制＋实际计数／已证明上界＋完整输出预留 | 契约上通过，实际 profile 仍待 P0 验证 | 选定。多一份版本化预算记录；部分字符合法输入仍会被明确拒绝；紧凑 reason 需验证是否足够表达必要事实 |
| C 自动截断／缺格转不足／额外模型修复 | 不过：不可控完整性／费用 | 拒选，repair_model_calls=0 |

有条件替代：若实际供应方提供可靠的完整请求计数接口，可替代 B 内部本地计数器，但它自己的请求、延时和已发生费用也受调用账管理；本轮不新增该调用。最便宜的退出点是统一 BudgetAdapter：不更换主栈，不把原问答型号自动用于 embedding／vision。

## 1. 三层限额与稳定受理顺序

以下均是**未实测的部署初值**，不表示 4 核 4GB 成绩。H 为协议安全硬界，部署级版本化；B 为可调业务上限；M 为实际模型适配器限制。新请求取三层交集，不能用提高 B 绕过 H／M。

| 层／检查 | 明确有限起点 |
|---|---|
| H：读取／解析前 | 仅 application/json、UTF-8、Content-Encoding identity；实际流式 body ≤1 MiB（含空白／转义），不只信 Content-Length；总请求头 ≤16 KiB。拒非法 UTF-8、重复 JSON 键、非有限数值、孤立 surrogate；单根 object、嵌套深度≤8、节点≤8192、每 object 键≤64、每 array 项≤1024；每 string≤65536 码点、所有 string 合计≤131072 码点。解析器必须在增长时限界，不能先整包无界解析后校验 |
| H：schema／ID | 未知字段／版本整拒；所有目标 ID 为 1–64 ASCII 字母／数字／下划线／连字符；scope 数组非空／无重复；业务数组不得超过 H。header Key 仍按现行 UUIDv7 契约，不改幂等生命周期 |
| B：retrieval.v1／answer.v1 | knowledge_base_ids≤64；可选 document_ids≤128；question≤4096 码点；型号／版本／环境／日志／参数等条件合计≤16384 码点，不得以拆字段绕过合计。retrieval 不因“不扣产品次数”放宽输入。当前条件使用单层白名单字符串字段，不接受任意嵌套对象 |
| B：comparison.v1 | 原 2–4 对象、1–6 条条件、单条256／合计1024码点、最多24子查询；所有格必须返回，不能截掉对象或条件 |
| B：辅助历史 | 最多最近2条合法的既有用户问题，合计≤2048码点，整轮纳入／剔除；默认不送旧答案／旧证据。它只帮助消解指代，绝不算本轮证据。必需上下文不可得就澄清，不凭截半句猜含义 |

字段的规范化保持现行 NFC／去首尾空白规则，原始请求和规范输入用途区分；日志内部空白、行序、数值、单位不做语义清洗。HMAC 覆盖完整规范输入而不是被裁成的提示。大 scope 集合不全量拼进 LLM；服务端以 ID 做授权与 SQL 过滤，模型只收本轮必要映射，动态 schema／提示因此增加的内容仍计数。

**顺序**：①执行 H 的有界读取与结构安全检查；②认证／渠道与显式目标当前授权；③按已有 Key 所记 normalization/schema 版本验证完整指纹并走原操作；④仅新 Key 校验当前 B、M、scope／guard、会话父轮次及执行配置；⑤通过基础预算与查询 gate 后，原子创建生成 operation、固定预算快照并预留一次，才做检索／外发。纯 retrieval 固定持久执行上下文和 deadline，不预留产品次数。

B 下调不重验已有操作为新单、不改原输入、不重预留。旧 Key 同输入只重放状态／原结果，异输入冲突。紧急 H 下调导致旧 POST 无法读取时可以 413 拒该 HTTP 尝试，但给本人受控 GET operation 的恢复方式；GET 不带原大 body、检查当前原动作／scope／依赖，不重执行。所有 H 变更也不能使旧 Key 成为新单。H 不是平台管理员可随意调大的业务滑块。

## 2. 适配器必须登记什么，怎样证明 token

每用途独立不可变 profile：provider、region/endpoint、模型 code、可得固定版本／alias、tokenizer 工件 ID／hash、chat template／框架与 SDK 版本、Unicode 与序列化策略、实际 schema/prompt hash、计数模式／证明依据、I_max（输入）、O_max（完整输出）、C_max（若为总上下文）、输出参数名称与语义、thinking 关闭方式或已证明的 R_think、安全余量、embedding 的 per_item_tokens／batch_items／batch_total_tokens（若厂商有该项）、HTTP body 上限、response byte 上限。未说明的限制为 unknown，绝不填“无限”。

计数优先精确：针对**最终将发出的** messages／system／schema／模板与 role framing，使用该 API 版本匹配的 tokenizer／chat template，记录每部分与总数；schema 若由 API 隐式加进输入，必须知道其计入口径。对单字符串分别 tokenize 后简单相加不自动等于完整消息的 token 数。

没有完全匹配的工具时，只允许经过证明的保守上界 U：例如已核实该 tokenizer 的每个 UTF-8 byte 最多生成 b 个 token，另有完整 chat/schema 封装上界 F，则 U=b×UTF8Bytes+F；b、F 不能凭经验取1或“每汉字一 token”。证明须涵盖 Unicode、特殊标记、模板注入的控制 token 和 schema 隐藏开销。只是用若干样本比对／加20%不构成对任意合法输入的证明。拿不到精确计数或可靠 U，profile 标记 budget_unverified，不放行该模型阶段。

真实 usage 用于校准与成本，不能倒过来把已发出的超限请求说成“调用前已验证”。若发现计数偏差突破登记余量，停用该 profile 的新付费阶段，记录 MODEL_BUDGET_PROFILE_INVALID，重核后发布新 profile；原 operation 不自动迁移／重跑。别名无法保证完全复现，应记录请求模型名、可得版本、响应标识与日期，明确剩余不确定性。

## 3. 两种调用各自核算

**Embedding**：先把全部子查询展开并登记最终字符串。普通 retrieval／answer：固定模板＋完整当前 question＋全部当前适用条件／日志；comparison：每个对象限定其固定文档版本，query 文本为固定 query 前缀＋完整本条 condition（不把全文文档或全部 scope ID 嵌入 query）。显式 scope 仍在服务器过滤。辅助历史若用于检索，要连同分隔符计入，不默认启动 LLM 改写／压缩。每个实际 query 或 document chunk 都单独验证 E_i≤E_item；入库正文过长按既定结构分块进入候选处理，不把用户查询暗切成多个付费查询。

首版 query embedding **batch_items=1、子检索串行**，至多24路，不用 SDK 自动拆批／重试；同一逻辑操作可少于24路，但优化复用必须显式记录真实调用和对应子查询，不能虚记24次成本。文档 embedding 批处理同时满足每条、条数、批总 token（若适用）、序列化 body 字节上限，并在派发前检查全部批项；不能认为 batch 合法就每项合法。不兼容 profile 仍按现行整请求拒绝。

**Generation**：完整当前输入及完整对象×条件为 M；S 是 system／固定模板／完整 schema／动态白名单；H 是合法辅助历史；E 是最多五块实见证据与所需定位元信息。对完整序列计数得到 I=Count(S,M,H,E)，不能只算 E。

必须同时成立：`I≤I_max`；`R=R_answer+R_think≤O_max`；若模型有总上下文限制，`I+R+margin≤C_max`。不同 API 的实际输入／总上下文定义分别登记，不能把模型列表中的一个数字同时当三个数字；独立输入限制也不能漏检。margin 为已证明封装误差上界＋登记安全余量，不能拿它掩饰未知 F。优先采用可明确关闭思考的模式；不支持关闭时必须有有限、可靠语义的 R_think，否则不接该 profile。使用哪个 max_tokens／max_completion_tokens 由适配器明确映射，不跨型号套用。

**基础预检先于 embedding／产品预留**：令 H=E=空，M 含所有当前用户内容，先检查最小完整输出和 `Count(S,M)+R+margin`。若已经装不下，直接拒绝；“把五块全裁掉”不能解决输入本体超限。选用的输出档位、上界和计数依据在受理时固定，后面不为装证据暗降输出档位。

## 4. 完整输出预留：24 格 ×512 是上限，不是写满指令

512 码点是 comparison.v1 的外层 reason 上限，并不要求每格写512。本轮选择首版 **compact-128** 生成契约：每格 reason 1–128 码点，仍是合法的 1–512；全部24格／ID／四态与各分支的证据字段保留，evidence_ids≤5，conflict 双方集合基数与归属不放宽。以 generation_contract_id 将该子集写入提示／模型 schema／本地校验／快照，API 能力配置明确显示128，不能先允许生成512再把结果截成128。不能在运行中自动降到更短、更少格或改成不足；本地生成契约超限则整答校验失败。

reason128 只是设计初值。若冻结题所需限定、冲突或数值事实不能在该档完整表达，应显式调高新配置到≤512并重算预算／重验，而不是删必要事实提高过关率。紧凑 reason 可能损伤表达，是本选择最强反对理由；实际评价不能用结构完整冒充语义完整。

R_answer 使用**规范输出的最坏合法长度上界**，而非“24×平均中文token”或只数一个全部不足模板。遍历冻结生成 schema：取每种四态分支最大结构，使用本次实际 object_id／condition_id、所有24格、每格最多128码点、最多五个短 evidence ID、最大合法 conflict_sides；静态标点／键名和所有可变数组也算。schema 外的 operation/catalog 公共包装由服务器生成，无需模型照抄，但其受控响应字节上限另验证。

证明方法：在规范紧凑 JSON 的字段/数组有限条件下，按 serializer 的最坏 escaping 算 B_out；例保守将每 Unicode 码点按至多12 ASCII字节计（含非BMP的 surrogate pair），则24格 reason 的单项部分上界为 `24×128×12=36864 bytes`，还需加全部结构／ID／分支。**这只是序列化字节上界，不是实际模型 token 数**。再使用该 tokenizer 经证明的 byte→token 上界和输出 framing 得到 U_out，R_answer≥U_out，并显式传给供应方。128未必能过所有模型；过保守但可证明的上界也可能拒绝本可生成的输入，可在新版本改用更精确且仍可靠的上界，不以采样平均替代。

没有有限 schema 就没有该证明。普通 answer.v1 同时补齐有限生成载荷：status 四态；summary≤1024码点；facts≤16（每条 kind 为流程／材料／条件／负责人／原因／检查／步骤／参数／限制等场景枚举，text≤512、applicability≤256、evidence_ids≤5，冲突分支有双方互斥证据）；gaps≤8×256；clarifications≤4×256。所有数组、枚举和字符串由实际响应模型约束，未知字段拒绝；按场景要求保留所需类别、步骤顺序、数值单位与条件。服务器元信息／catalog 不让模型编。该有限载荷也是未测初值，不能为达限漏事实；原普通答复验收语义仍有效。三种普通场景共用有限结构但逐场景核验，不取消任何场景。

容量证明只说明完整规范结果**有空间**，不保证随机生成器一定遵守长度、schema 或事实。无界空白／乱转义／无关废话仍可能用光 R；遇 length 一律失败。若 R 超过实际 O_max，或基础输入＋R 超 C_max，该模型／该请求组合明确拒绝；不得宣称“接入千问就能接受最大4×6矩阵”。profile 必须登记支持的形状／输入范围，业务上限发布不等于每个可切换模型都具备相同范围。

## 5. 固定证据裁剪顺序与评估

1. 按原条件顺序、文档 ID 升序做子检索，原固定名次轮转去重选定最多五个块，锁定次序。不得为预算失败重新取别的块、加邻块、拼整章／整表、旧答案或扩大块。
2. 基础预算既已通过，先尝试加入有界辅助历史与五个块的受控正文；超限先按从旧到新剔除**整条辅助用户问题**，不动当前输入。必需指代因此不明，返回明确澄清或预算错误，不能猜。
3. 仍超限按五块的逆优先序（第5到第1）缩短：只保留原文连续片段，按已登记的段落／句／表格行组边界从尾部删；表头、单位、型号版本和适用条件与其事实行作为一个原子组，不能留下失去限定的数值。一个最小原子组都不容纳就整块移除；不得用 LLM 摘要替代原文。记录 source offset／片段 hash／裁剪原因，确定性重算完整 I。每块待选正文还有有限字节上限，超大块不能先整段无界载入内存。
4. 无可用候选与“查到候选但预算不容纳任何实见片段”分开。前者仍走既定确定性 NO_CANDIDATES、完整全部格、正常计1；后者返回 CONTEXT_EVIDENCE_BUDGET_EXHAUSTED 整答失败，不冒充零候选或正常不足。有1–5块实见片段时可逐格正常不足，但不得把因截断生成而缺格当不足。
5. evidence_catalog **只**列模型真正看到的最终片段，逐片段保存源块／版本／定位／hash与裁剪范围。被裁掉的正文即使同 chunk_id 命中也不计证据；未引用的实见候选可在 catalog，但不会自动支撑事实。

SM-2 只按实见片段直接支撑的原金标证据单元作分子，分母原样保留；同一块可支撑多单元。预算拒绝、模型失败和 length 不删题、不移入8条不足题：可回答题在 SM-1 计失败；没有实际模型上下文的调用前拒绝 SM-2 分子为0。若发出生成后失败，SM-2仍按已保存实见上下文如实算，同时 SM-1失败，不能因覆盖率好宣称任务通过。SM-3按实际事实结论的引用语义检查；空／失败答不拿0分母充100%，另列失败。32题、24可答/8不足、SM-1≥21且每场景≥5/6、SM-2≥85%、SM-3≥95%及定位100%、SM-4/5等原门槛不变。

## 6. 错误、受理／计次和实际成本

| 情形／HTTP+code | 生成 operation／产品次数 | 供应方成本 |
|---|---|---|
| H raw body超限：413 REQUEST_BODY_LIMIT_EXCEEDED；结构深度／节点／字符串：422 PROTOCOL_STRUCTURE_LIMIT_EXCEEDED；schema／重复键等422 VALIDATION_ERROR | 受理前，无预留；旧 POST被H挡住不改变原operation，可受控GET | 不调用 |
| 新请求B超限：422 INPUT_LIMIT_EXCEEDED／COMPARISON_LIMIT_EXCEEDED | 无预留，改输入须用户显式新逻辑操作 | 不调用 |
| profile未知／计数不可靠：503 MODEL_BUDGET_UNVERIFIED | 基础预检无预留；已受理阶段发现则终态失败、条件释放一次 | 未发不记实际费用；先前已发照记 |
| 当前输入本体／单条embedding输入装不下：422 MODEL_INPUT_BUDGET_EXCEEDED；完整输出装不下：422 MODEL_OUTPUT_BUDGET_EXCEEDED | 尽量在基础预检整拒，无预留；受理后最终组合失败同样整答失败、释放一次 | 不发该失败阶段；先前embedding若已发仍登记实际usage／unknown |
| 候选存在但证据原子组均装不下：422 CONTEXT_EVIDENCE_BUDGET_EXHAUSTED | 已受理 operation failed，释放一次，不改正常不足 | 检索embedding照记 |
| length／流结束无完整终止帧／正文截断：502 ANSWER_TRUNCATED；缺格／非法state／引用／生成契约错误：502 ANSWER_VALIDATION_FAILED | 整答失败、不交草稿、不结算；同Key重放原失败，新Key仅用户明确发起 | 所有已发调用照记，usage未知保持unknown |
| 查询gate／调用预算不足：429 CONCURRENCY_LIMIT_EXCEEDED／QUERY_RATE_LIMIT_EXCEEDED | 受理前无预留；受理后期限内不能执行则明确失败、释放一次 | 不绕过gate派发；已有成本保留 |

错误响应包含安全 code、request_id、已有则operation_id、stage、retry_mode及受控恢复提示。已有operation的GET成功读取可HTTP200但内部 state=failed＋原 error.http_status；同步POST及同Key终态响应使用对应失败HTTP，不用 completed/insufficient 包装。额度与释放沿现行条件事务／唯一transition，无负数、无重复退款；真实call账完全沿现行§2.5，不重开生命周期。供应方非成功、网络未知与真正零候选必须分开。

供应方只接受 n=1、tool/web/code disabled、自动截断 disabled（若接口有此项）、SDK／HTTP自动重试／自动重定向关闭。只有完整终止＋合法reason＋完整JSON＋本地schema／跨字段／来源校验＋输出前当前授权都通过，才发布并结算。自定义stop串不能为了看似短输出来截断JSON。仅允许去围栏／空白等无语义规范化；extra_model_repairs=0，不自动多调用“补齐剩余格”。

## 7. 查询 gate 覆盖纯检索和全部子检索

所有 retrieval／answers／comparisons 共用全部署 PG 条件gate（不能每个API进程各自放2个）：初值 active_query≤2、每用户≤1、每逻辑查询 subquery_inflight=1、最大子查询24、无持久待执行查询队列，拿不到槽就429。operation的逻辑占位与网络实际执行槽分开：租约过期可终结业务，但未证明旧传输者停止，不把其实际槽立即再借出；复用现行受监督传输进程与停止屏障，不加服务。

纯检索有 request execution ID、归属、scope、deadline、调用预算和call_id，虽不预留问答次数，仍过同样付费／并发／身份／墓碑／期限守卫。query embedding另有全部署和每用户有限RPS/TPM窗口，受控初值为全局2次派发/秒、每用户1次/秒；TPM以必填有限配置取实际账号已核限制和本地保守上限较小者，未登记就不派发。comparison 24路按序等待gate计入同一hard_deadline，不开24线程；只用有限计时等待，不持Session。生成及可选将来的计数/改写请求同样不能绕call gate。更高并发或批处理须原P0/负例验证后发布新配置，不靠“不扣产品次数”放大付费检索。

## 8. 必要记录与验收负例（尚未执行）

budget_snapshot 至少保存 H/B版本、generation_contract_id、完整规范输入hash、实际profile/计数器/SDK/schema/prompt/template指纹、输出档位、I各部／最终总数、R_answer/R_think/margin、E_i和batch计划、选定五块次序及实见范围、call_id集合、finish_reason／usage／错误。正文在受控业务快照，不复制到普通诊断日志。配置／模型alias或SDK变化前重核参数语义与这些负例；既有受理快照保留，不能静默以新模型重跑。

必须覆盖：raw JSON大量空白／转义／分块无Content-Length；超深数组／大ID集／重复键；字符合法但包含高token Unicode／长日志导致本体超限；单条embedding超限而批条数合法；4×6每格完整conflict分支的输出上界；模型O_max小于R而输入很短；schema+system+用户本体已超限却证据为空；后5块表格裁剪保留表头单位；候选有但全裁无预算；length即使JSON恰好可解析仍失败；stop但缺格失败；修复调用为0；旧Key遇B下调或H紧急下调仍只读原操作；retrieval并发与24路比较不越gate；已发embedding后生成预算失败成本不归零；失败SM不删题。通过后才登记实际支持的型号／形状／输入限额。

这只是原P0实际接入与原验收的前置锁定／重核内容，不新增框架、服务、产品场景或模型效果承诺。user_only_missing：无。本主答先交John同题质疑，真实追问继续由本Mary收口。
