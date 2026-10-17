---
question: R2-M2
status: closed_after_john_followup
updated: 2026-10-16
---

# R2-M2 同题收口：可合并条款

以下修订优先于本题主答相应段落；未改动的五块轮转、逐调用成本账、HTTP／预留释放／SM口径继续有效。只有文档设计，无实现或成绩。四场景、最终K=5、32冻结题、原金标分母和全部SM门槛均不变。

## 1. 有限边界、规范化与旧请求

主答 H 的1 MiB raw body、JSON深度／节点／数组／字符串等限制，**仅适用于 JSON 查询与控制请求**。二进制PUT／原件上传／解析结果下载／受控原件下载分别沿现行上传、20 MiB原件初值、流式字节与磁盘预算契约；不得套成全站1 MiB。header限界可以按HTTP入口登记，不改变媒体body上限。H初值仍须P0核对解析器／网关实际行为；B可为新请求收紧，不能追溯改旧受理快照。

规范输入按字段定义：comparison.conditions.text 沿原NFC＋首尾trim及重复检测规则；question、log与其他当前输入默认保存其**完整解码值**，不新增全局NFC、trim、内部空白合并、换行重排或前缀删除。question只有全空白时拒空，不因此改写有效问题；日志空白本身也不删。模板序列化可转义而不改内容，计数与HMAC分别按固定序列化／规范化版本；旧Key用其受理版本验指纹。任何语义缩减须用户明确修改成新输入，不能在预算器中暗做。

H先保护读取，所以旧POST可能在认证前被安全413挡住：外部只给通用code/request_id和“认证后查看原操作”的固定提示，**不查出或回传未认证的operation_id／目标信息**。客户端原先保存的operation_id可在认证后受控GET；只有已认证并覆盖原动作／scope者才取得本人状态位置。B下降、默认模型变化或H拒本次HTTP均不把旧Key改成新操作／重复预留。

## 2. P0先锁一种简单且有计数依据的生成接入

首选有限、明确支持非思考的千问API模式；只传显式system＋user文本消息，JSON结构要求写在可见提示中，response_format使用普通text；n=1、tools/web/code disabled、无自动改写／修复／额外tool调用。首版不依赖供应方json_schema隐藏注入或自动历史／内置检索。仍在本地严格解析与验证JSON；文本模式的结构失败率必须实测，不能以“支持JSON”代替通过。

按实际用途型号／端点取得可用精确tokenizer／完整消息计数能力，或依据官方公开的tokenization／消息封装说明登记**完整序列**保守上界；明确普通文本模板有多少固定role／BOS/EOS等开销。无需取得私有模型权重或内部完整实现。公开计数工具若只数content、只支持别的端点或不含role framing，不能标成完整准确。已知有限封装开销可据文档取保守上界并收紧新业务输入；完全未知的封装不能单靠20%余量或样本通过升级为保证。

P0可选择同一既定千问路线内、已核计数／模式／I/O限制的可用型号，并在H/B内发布可证明的输入／矩阵支持范围；不要求所有可选型号都接最大4×6。若某候选仍无计数或封装依据，只把该候选留在MODEL_BUDGET_UNVERIFIED的P0 gate，不宣称所有千问不可用、不另加自托管／新平台。

**唯一补查结果**：本轮官方线索找到的是[阿里云OpenSearch的Token计算接口](https://help.aliyun.com/zh/open-search/token-calculation)，其服务地址、产品和鉴权属于OpenSearch；不能拿来证明本项目百炼DashScope端点存在等价完整计数能力，也不据此新增OpenSearch接入。本轮没有证实百炼任意型号的完整消息计数接口可用，保留实际适配器P0验证，至此停止网络扩查。

## 3. 输出空间证明与生成子契约

输出证明只表示：**包含全部必需字段、全部格子和有限字符串的规范紧凑JSON有空间**；不保证随机生成器不乱写空白／转义／漏字段。首版comparison生成子契约reason为1–128码点，外层comparison.v1的≤512仍成立；128在schema／提示／本地校验中一致，超出子契约整答失败，绝不裁返回值或改成不足。换更高档位≤512须新配置、重算、重验，不在已受理请求中自动改档。

输出上界无需永远按全部\uXXXX最坏转义估计：优先规范UTF-8紧凑JSON、非ASCII直接编码；若字符串拒绝除TAB/LF之外的C0控制字符和非法surrogate，则一个合法码点的规范编码至多4字节（引号／反斜杠／TAB/LF转义至多2字节）。24×128的reason部分因此≤12288字节，仍须加全部键名／标点／本次实际ID／最大合法四态分支与证据数组。该字节上界再用已证明的实际tokenizer上界换算token；**不能把12288字节称为12288实测token**，也不假定byte→token系数必为1。若使用其他序列化策略，使用其自己的正确上界。

普通回答也选一个有限生成子集，免于默认按16×512支出预留：首版answer-compact128令每条事实text≤128、applicability≤128、summary.text≤256、gap／clarification.text≤128；外层对应text≤512、applicability≤256、summary≤1024、gap／clarification≤256仍保留。全部数组基数与必需语义不削弱。P0若保守R仍超O_max，须选容量足够的已核模式或提高计数精度／调整**新受理**档位后重验；不能标记该模型支持却让全部普通问题注定失败。首个可用profile至少验证四场景的完整最小有效结果可容纳；最大输入／24格只有通过预算的组合才受理。未验证不假称可达。

## 4. answer.v1最小有限生成载荷

这只是最小响应载荷，公共metadata／catalog由服务器生成；不另生成完整OpenAPI。所有对象unknown字段拒绝；字符串长度均为码点、拒非法Unicode；模型只输出白名单ID。生成子集使用上一节的更紧上限，本地必须同时验证外层和已受理生成子契约。

| 字段／类型 | 外层有限约束与必须语义 |
|---|---|
| outcome:string | answered／insufficient／clarify／conflict；与HTTP公共status区分 |
| summary:object | text:string 1–1024；fact_ids:string[] 0–16、唯一、全部对应facts.id。事实性摘要必须有对应事实及直接证据；无事实分支仅描述不足／待澄清，不加事实结论 |
| facts:object[] | 0–16；每项id为f1…f16、唯一；kind为process／material／condition／owner／cause／check／step／parameter／limitation；order为1–16整数、同kind内唯一并按执行顺序展示；text:string 1–512；applicability:string 0–256；evidence_ids为本轮白名单ID数组1–5、唯一；quantity:null或下述object；conflict_sides:null或下述object |
| facts.quantity | null，或{value_text:string 1–64,unit:string 1–32}；parameter类必须非null。数值／范围／关系写完整value_text，单位不能凭空补；必要单位未知进gaps，不能冒充参数已回答。其他含关键量值的事实同样给quantity，不能只让展示层猜单位 |
| facts.conflict_sides | null，或{side_a:string[] 1–5,side_b:string[] 1–5}；双方互斥、并集恰为该fact.evidence_ids、合计仍≤5且有≥2不同证据；text描述同一适用条件下两方矛盾，不替用户无据裁决 |
| gaps:object[] | 0–8；{field:枚举同kind或object_identity／version／environment／log_context／evidence／source_locator,text:string 1–256}；指出用户所求的缺口，不能写无据原因。有限条数不授权合并遗漏必要缺口 |
| clarifications:object[] | 0–4；{field:与gaps相同枚举,text:string 1–256}；问清执行任务所需的型号／版本／条件等；不要求提供无关信息 |

kind按scenario限域：enterprise可process/material/condition/owner，support可cause/check/condition/limitation，manual可step/parameter/limitation/condition。必要内容按用户本轮任务确定，不强行给只问负责人的问题塞流程；但请求涉及的以下项不得漏：企业的流程、材料、适用条件及负责人；排障的适用版本／环境／日志限定、带证据的候选原因和有序检查；手册的型号／版本、步骤、数值单位／限制及页表图定位（定位由相应catalog提供）。未请求项可无，不可证的请求项必须明确gap／澄清，不能用空数组默认为回答完成。结构校验不理解全部语义，原人工任务／引用验收仍必须通过。

| outcome | 必须满足 |
|---|---|
| answered | facts≥1，全部事实直接有证据；用户本轮必要事项完整、无关键gap／clarification，无冲突分支；summary.fact_ids≥1。来源中明确的不支持／否定仍需直接证据 |
| insufficient | gaps≥1；可有0–16条有证据的限定事实，不能用未命中推断事实否定；summary只陈述已支持部分／缺口，不把完整任务标已完成 |
| clarify | clarifications≥1；显式指代／型号等不明时使用；允许有直接证据的限定事实，但不能假定缺失条件或生成猜测性参数 |
| conflict | 至少1条fact有合法conflict_sides并被summary.fact_ids引用；双方实见来源、相同适用条件与矛盾内容完整，其余事实仍须直接证据；五块不够双方时只能insufficient并指明缺口 |

gaps／clarifications有上限不允许删事实凑长度；表达不完整的结果不通过任务验收。facts=0时不算有引用支撑的事实答案，SM-3分母0报N/A并单列，不能填100%；可答题即使返回结构合法insufficient／clarify也按原任务事实完整性判断，不能靠拒答达SM-1。

## 5. 当前输入、辅助历史与查询预算

首版**不做任何额外LLM改写／压缩**。普通query embedding的实际字符串就是版本化固定模板＋当前完整question＋全部当前适用条件／日志＋允许的完整用户历史辅助；comparison仍用完整condition＋该操作允许的辅助，文档对象通过服务器固定scope过滤。每条实际字符串与批计划先展开、计数、记hash，不先截日志再说合法。最多2条用户历史／合计2048、同空间及当前授权／依赖复核，不能拼半轮或加旧答／旧证据。剔除历史后显式指代不能消解则clarify，不猜主体；clarify可由确定性模板形成，也须完整合法，不能伪称检索已取得依据。

当前用户内容是必保M，S完整可见system／schema／动态白名单，H有限辅助，E实际最多五块；最终对完整S/M/H/E序列计数，保留完整输出R及margin，分别核I_max/O_max/C_max。辅助历史先整轮从旧到新删，再按已选五块逆优先序裁原子组；表头／单位／适用条件随事实保留，不追加新块／邻块／旧答。只计最终实见片段，裁去证据不计SM2。

## 6. 分支顺序：真实零候选无需证明LLM最大输出

新Key通过H/B、当前授权、profile兼容、单条embedding预算、scope／guard／父轮次与查询gate后，分两类配置判断：

- **已可靠判定**选定生成profile对当前完整M／输出R必定不容纳：422输入／输出预算错误，受理前拒绝，不花embedding费用；不能把明知不能生成的输入先包装成正常不足。
- 生成profile仅**尚未证实／不可用**，且查询embedding阶段已具备可执行资格：允许受理为一个有费用守卫的“检索后分支”操作，原子预留一次并固定此事实；202只代表接受处理，不保证会调用生成。可选执行完整有界检索，真实query embedding照记。未验证LLM不提前当成已经成功，也不妨碍后续真实零候选模板。

检索须成功完成全部已登记子检索并合并：①最终原始候选确实0：不调用LLM，服务器构造**全部格／普通四态的完整确定性不足**，验证本地schema及有限响应字节，正常结算1；不要求R_answer/O_max或LLM tokenizer可用。②候选非0：此时必须通过生成profile／基础本体及完整输出预算；未验证返回503 MODEL_BUDGET_UNVERIFIED，已知超限返回422，均终态失败、释放一次，已花embedding照记。③基础预算通过后裁E至0：422 CONTEXT_EVIDENCE_BUDGET_EXHAUSTED失败，不能走①。检索依赖失败／未跑／部分子检索未完成绝不走①。

普通零候选模板：outcome=insufficient、summary为无依据提示且fact_ids=[]、facts=[]、gaps含evidence缺口、clarifications=[]、catalog=[]。比较模板保留每个对象×条件并全部NO_CANDIDATES。零候选是依据明确成功检索的分支，不让不可用LLM状态充当零候选；所有状态读取／发布仍复核权限。此顺序替换主答“所有生成预算均先于任何embedding”的过强表述；能可靠早判的预算失败仍尽早拒绝。

## 7. 查询gate替代旧等待4

首版新权威初值：全部署active_query≤2、每用户≤1；retrieval/answers/comparisons共用，batch1、子检索串行、最多24。**明确替代原Q4的执行2／等待4：不保留4个等待逻辑请求槽，无持久队列；拿不到逻辑执行槽直接429，无operation预留。** 已受理操作内的外部调用rate gate可在其hard_deadline内有限等待，等待不持ORM Session；deadline到明确失败，不新增执行资格。

逻辑lease与实际传输槽分开，lease过期不能在旧传输者未证明停止时重复借槽；沿现有监督／停止屏障。RPS/TPM须有有限部署配置并核实际账号／端点约束，取适用约束较小者；主答2/s与1/s仅可作为本地拟定初值，**不是账号额度**，本轮不强定为生效值。未登记可靠rate／TPM预算不派发对应付费阶段；已经发出的usage仍未知照unknown。纯检索不扣产品次数，但照常占gate、受调用预算、留call账。

## 8. 合并与验证

现行实施契约只需吸收以上：JSON与上传分界、字段规范化、P0简单生成模式及计数依据、有限answer生成载荷、零候选分支、compact档、统一无等待查询gate；主答其余HTTP、一次预留／释放、length／缺格整答失败／repair=0、实见catalog与SM口径继续有效。长度错误即使JSON恰能解析也失败；stop但缺格同样失败，不交半答。所有旧Key只恢复原操作，实际费用不因业务失败消失。

必补负例：二进制20MiB上传不被JSON1MiB挡；未认证413不泄露operation；带前后空白／换行／前缀日志指纹稳定；旧Key配置下降；小模型O_max不足的早判拒绝；生成profile未验证＋真实零候选正常模板／非零候选失败两分支；子检索未完不得零候选；全部证据被预算裁空失败；answer各场景必要字段／四态／量值单位；空facts不填SM3=100%；无等待4且旧传输槽未停不复借。全部尚未执行，沿原P0和原验收，不新增服务、收费调用或产品范围。

user_only_missing：无。John八项追问已逐项闭环，本题停止研究。
