---
title: RAG_all 第二轮独立 IR · John B 初评
reviewer: John B
date: 2026-10-15
status: independent-initial-sealed
verdict: CONCERNS
scope: recorded-implementation-slices-only
---

# John B 独立初评

本稿在未读取 John A 本轮任何产物、未读取上一轮 implementation-readiness.md 的情况下形成。已经读完委派的 PRD、实施契约、实施切片、addendum、memlog、技术对话、summary、JD 和根目录三份工程／理解记录；另展开契约指定的 M1 主答／追问、M2 schema／UI 契约以及 Q2 主答／追问，用于撤回已被细节覆盖的怀疑。没有编码、部署、真实外部调用或运行验收。

采用 bmad-agent-pm＋bmad-sprint-planning readiness gate。RTK 启动解析脚本时拒绝访问，先按技能允许的路径手读 customization／config；其后用已有绝对 Python 解释器成功执行两份 customization 和 config 解析，确认 Chinese、中文文档、John 📋，所有前后置步骤与持久事实为空。判定问题是：开发者能否按已记录的前后关系实施，无需自行决定尚未记录的业务失败语义。

**结论：CONCERNS。S0 可开始；三项契约／顺序问题须在其影响的切片或真实探路前澄清。** 本结论不否定已有产品定义，也不把账号、4 GB、图意或恢复尚未实际验证本身列为规划缺陷。没有发现必须重新访谈用户或降低四场景、K=5、32 题／金标和 SM 门槛的理由。

## 1. 待对抗发现

### B-R2-01 · P1 · S2 的完成条件依赖 S3／S5 才交付的基础能力

- **分类：** 契约／实施顺序缺口；不是新增产品范围。
- **准确原位置／引用：** [实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:15)规定“S0 → S1 → S2 → S3 → S4 → S5 → S6 → S7”；同文件 [S2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:43)，范围 43–49，要求导入、部分可用、候选切换、任务与来源验收；[S3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:54)才交付“结构化分块、独立 embedding profile 与同维存储”；[S5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:70)才交付“校核对照页和 PDF／非 PDF 最小回看”。但 [PRD FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:188)，范围 188–204，要求查看解析／索引结果、有权者校核重试，且就绪不是只保存解析包；[UI 契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:7)要求同活动 profile 准备新块／向量并原子发布。
- **具体触发：** 按顺序做到 S2，导入一份完整 PDF 或 TXT，尝试把候选标为就绪并完成 S2 验收。若 profile／vector(D)／结构块到 S3 才存在，S2 无法判断完整索引可发布；若来源对照与结构回看到 S5 才有，维护者在 S2 无法完成本切片承诺的校核／定位／重试闭环。
- **已有约束为何挡不住：** 全局契约已经规定应怎样正确发布和回看，挡得住“只保存文件就假装 ready”，却没有把这些前置能力分配到更早交付单元。S0 的通用迁移和 P0 的真实 embedding 配置／维度探路不等于交付 S2 所需的业务 profile、索引写入和最小校核页面。开发者仍须自行把未来切片的一部分前移，或者违规延后 S2 验收。
- **后果：** 顺序计划存在不可兑现的 S2 完成状态；实现可能先造一套临时索引／页面再重做，或把无向量／无来源校核的状态当作就绪，且 S2 已完成不能成为 S3 的可靠前置。
- **最小修复：** 明列 S2 包含导入所需的 profile／维度存储、结构块／向量写入与原子发布基础，以及原件／提取／失败范围的最小校核回看；S3 在此之上交付查询 B0、历史与操作，S5 扩展复杂表格／扫描／图意质量与交互。也可正式拆成更小前置切片，但不降低原验收。S6 的索引重建管理可以继续后置，普通文档发布所需的 generation／revision 基础不能等 S6 才建立。
- **可验证关闭条件：** 修订交付／前置表，逐项给出 S2 就绪发布与维护者校核使用的已完成能力；S2 可在尚未实现 S3 问答与 S5 复杂手册功能时独立完成“导入完整文档→查看来源／解析→失败重试→完整发布”的验收，且不会假称 S5 的复杂质量已经通过。
- **允许撤回的依据：** 若能指出当前已生效文件明确将上述导入基础和最小回看交给 S0／S1／S2，且 S3／S5 只是扩展而非首次交付，本项撤回。不能仅以开发者自然会提前做作答。

### B-R2-02 · P1 · 已记录 K=5 与字符上限，但总 token／输出预算装不下时的产品分支未封口

- **分类：** 契约缺口；实际型号／token 限额数值仍是已登记的接入验证，不能捏造。
- **准确原位置／引用：** [实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:190)，范围 190–195，给出问题 4096 Unicode 码点、适用条件合计 16384 码点，不可静默删日志；要求 P0 登记模型上下文长度，“若超预算只传记录后的受控片段”，catalog 等于模型实见片段。[对比 schema](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:35)，范围 35–44，要求完整矩阵且每格 reason 最多 512 码点；[契约四态](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:97)，范围 97–103，允许 24 格、缺格整答失败且不追加 LLM 修复。[PRD 评估约束](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:307)禁止加入旧答／全文或扩大块规避 K。
- **具体触发：** 在已选小模型实测后，合法问题＋长环境日志＋系统／schema 提示本身已接近或超过输入预算；或对比 4×6 格在加入最终五块后，没有给完整 JSON 和全部格保留足够输出空间。即使只剩一块甚至零块，输入本体也可能装不下。另一触发是供应方返回 length／截断但 JSON 碰巧仍可解析成某种结果。
- **已有约束为何挡不住：** K 和 Unicode 字符上限不等于实际模型 tokenizer 的总上下文。当前“只传受控片段”规定了证据不得偷增和必须如实计分，未规定系统、当前输入、必要历史改写、证据、预留输出怎样合计，也未规定输入本身装不下或输出预算不足时拒绝／释放／计次的行为。答案校验能挡缺格，却是在外部费用已经产生之后，不能替代可预测超预算的准入规则。
- **后果：** 实现者可能静默删用户日志、截证据后仍把整块计命中、遗漏输出格，或让可预测失败持续消耗真实费用；几种实现会产生不同的配额、费用与评估口径。
- **最小修复：** P0 的实际模型配置一并登记输入／输出／总 token 边界与计数办法；调用前对 system＋受理输入＋必要辅助上下文＋实际证据片段＋输出保留量做统一预算。明确证据可按已记录规则形成受控实见片段并同步 catalog／SM-2；当前问题／日志不能偷偷裁。仍装不下或无法留足输出时给固定可识别错误，不调用模型、未受理不预留／已受理只释放一次；供应方截断或长度终止不能伪装完整正常不足。24 格上限和其他限额仍是可调初值，由 P0 实测决定生效值，不能修改冻结金标换取通过。
- **可验证关闭条件：** 增加精确行为与切片负例：合法字符输入但 token 超限；五块合计超限；最小必要输入本身超限；24 格输出被截断；裁剪后的 catalog／SM-2 只计模型实见事实。对每种情况注明是否发生真实调用、逻辑终态、产品计次／释放以及错误码，且正常完整矩阵仍受原 SM 门槛验收。
- **允许撤回的依据：** 若现行记录已有覆盖全部 token 项、输出保留和“不可容纳”分支的明确契约，本项撤回。仅登记某个模型 context_length 数值不足以关闭。

### B-R2-03 · P1 · 外部调用的发出前守卫与迟到用量回填，尚未与业务 fence 明确分开

- **分类：** 契约缺口；不要求外部恰好一次，不要求追回已发出的调用。
- **准确原位置／引用：** [实施契约三本账](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:32)要求每个 call_id／attempt 记录发出、供应方 request_id 和已知成本；[生成恢复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:65)，范围 65–69，规定结果提交的 lease／token／attempt 条件；[Q2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/answer.md:26)，范围 26–31，规定心跳、产物／完成提交守卫，并且 MinerU 明确“保存请求意图”、先存 batch_id 再 PUT、迟到结果丢弃／清孤儿。[PRD FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:270)，范围 270–272，要求成本如实累计且未知不盲重交。
- **具体触发：** ①查询 embedding 或答案 API 已被供应方接收，进程在本地补写 call 行之前崩溃，恢复器只找到逻辑操作；②文档重建／批量 embedding 的旧 attempt 在暂停后恢复，下一批付费调用开始前已取消、删资料、失租或换 recovery_epoch，但它只在回写时检查 token；③已有调用的迟到响应给出 request_id／usage，此时业务操作已 failed_unknown 或任务旧代失效，通用“迟到结果丢弃”同时丢掉可补正的成本。
- **已有约束为何挡不住：** 当前能明确阻止旧执行者发布、重复结算或恢复访问，也已为 MinerU 的申请／PUT 记录请求意图；但没有将所有生成／检索／embedding／重建的调用统一要求为“调用意图持久化后才发出”，未把“发起下一次调用前仍须有效”写成独立守卫，也未明确迟到成本元信息可回填而业务结果不可提交。最终提交 fence 无法撤销在它之前新发出的外部调用；每次成本要记录的目标不能单独决定跨崩溃窗口的写入次序。
- **后果：** 可能出现完全找不到的真实外部费用、取消后继续发新批次，或只能永久显示 unknown 却丢弃了已拿到的用量。若用“禁止旧 attempt 任何写入”粗暴修补，又会和真实成本逐次留账冲突。
- **最小修复：** 写明每次可能产生外部调用前，先持久化稳定 call_id、归属操作／任务／attempt、能力、计划阶段和状态；再在临近派发处核验有效 lease／deadline／epoch／取消及父级墓碑，并记录派发边界。供应方接收后响应丢失只能保守为 unknown，不自动重交。已发出调用的迟到 request_id／usage／费用允许按唯一 call_id 幂等补正，不改业务终态、结果、配额、候选或 guard；失效执行者不得再开启新的外部调用。仍承认检查与实际网络派发之间存在小窗口，不能承诺撤权或取消与外部网络原子。
- **可验证关闭条件：** 故障注入矩阵至少区分“意图提交前、提交后未发送、供应方接收后未记响应、业务 fence 后响应到达、下一批发送前取消／删除／换 epoch”。验证每个已可能发出的调用均有可追溯记录；unknown 不冒充零或确定未调用；旧代不发起后续新批次；迟到用量仅补调用账，不复活业务成功、不重扣产品次数、不解新 guard。
- **允许撤回的依据：** 若现有权威记录把 MinerU 的请求意图顺序明确推广到每种外部调用，并已有上述派发／迟到账本例外，本项撤回；不能把只限制本地发布解释成已经限制下一次外部调用。

## 2. 已覆盖而不另报缺口的组合检查

以下不是运行 PASS。含义仅是已有可执行的规划规则；真正测试仍必须按切片完成。

| 检查组合 | 现有准确位置与已覆盖行为 | 本轮分类／结论 |
| --- | --- | --- |
| 身份双凭据、目标集合、凭证 scope、撤权、历史引用 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:16)，范围 16–20；[PRD FR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:172)，范围 172–182；[契约操作读取](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:180)。同时携带 Cookie／Bearer 即使同人也拒绝；显式库非空／去重，任一越界／不存在整拒，范围为凭证与当前权限／动作交集；状态、历史、引用再次授权。 | 已覆盖；不把共用业务服务误读成认证回退。不另要求文档级权限或服务账号。操作读取需沿用当前 scope 的既有规则，未独立扩大动作。 |
| 重传、重试、并发、回包丢失、跨日 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:43)，范围 43–69；[M1 追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/followup-answer.md:13)。独立逻辑键、规范输入 HMAC、原执行快照、202／原成功／原失败／410，业务成功提交后掉回包不释放；受理日固定，不跨桶重计，上传同候选同 hash 重放。 | 已覆盖；已记录待执行。客户端手动新 Key 是显式新逻辑操作，不能要求阻止所有相同问题重复提交。 |
| 产品次数预留／结算／释放、崩溃、真实外部成本 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:28)，范围 28–32、63–69。最后一次额度原子预留，零候选正常不足也计一次；依赖／权限／期限／结构失败释放；迟到者不能重复终态。 | 产品计次已有覆盖；外部派发和成本回填的组合细节单列 B-R2-03，不重报“没有幂等账本”。 |
| 原件容量在途／历史／候选、派生／临时／磁盘 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:30)，范围 30–39；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:164)。保留版本与预留计费；替换不先抵扣旧版；清完才释放；跨文件系统恢复阶段，派生和解包另设必填水位／写入预算。 | 已覆盖。阈值未知已明确为实施登记，不能将其本身误报成产品缺口；没有要求本期增加历史版本清理器。 |
| 租约／代次、取消、未知上游、迟到、删除清理 | [Q2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/answer.md:25)，范围 25–31；[Q2 追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/followup-answer.md:3)；[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:272)。独立心跳短 Session，失租拒提交，先持久云 ID、超时查原任务；未知由有维护权者知情重交保留原关联；墓碑优先，孤儿清理不恢复访问。 | 本地发布／清理安全已有覆盖；取消后新派发等细分纳入 B-R2-03。云端已发出的任务无法保证取消是既定边界，不另报产品不完整。 |
| 版本、索引代、embedding profile、guard、删除、维度迁移、历史 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:77)，范围 77–93；[M2 UI 契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:7)，范围 7–17。上传写意图与重建共 KB 锁，guard 阻新写保旧读，删除废弃候选、条件解锁，revision／版本集守卫；异维维护停服迁移；旧在途快照有 deadline，历史 evidence_snapshot 不依赖向量存活。 | 已覆盖；S2 与 S3／S6 的实现落点顺序是 B-R2-01，不重报缺少 profile 或所有上传必须全库重建。 |
| 对比放大、逐格四态、零候选、结构错误、证据预算与评估 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:97)，范围 97–103；[schema](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:11)，范围 11–15、35–46、78–90；[技术对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:119)。2–4 文档／1–6 条／最多 24 子检索，固定名次轮转，全请求最多五块；格绑定文档版本，同格冲突双方证据，零候选保全格并正常计次，结构错误整答失败。 | 已覆盖；token／输出预算装不下分支为 B-R2-02。不能因为最多五块就断言必要证据最多五单元，也不能扩大 K 或降低金标分母。 |
| 解析校核、修正、PDF／非 PDF、真正图意探路 | [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:192)，范围 192–204；[契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:109)，范围 109–118；[P0](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:29)。正常自动程序校核、首次 partial 与替换分开；修正新候选不改历史；PDF 可靠页／bbox 回退，非 PDF 真结构与原件下载；图意金标调用前固定，MinerU 不足才走独立视觉 API，再失败阻断 SC-4。 | 行为已覆盖；真实格式、来源和图意属于明确待执行验证。最小回看交付顺序为 B-R2-01，不要求增加 OCR 编辑器、Word 服务或自部署 MinerU。 |
| 旧备份、可信身份、安全台账 gap、旧凭据／操作、未知配额与分范围放行 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:126)，范围 126–158。独立 break-glass 与现行受托核验；台账不伪称无 gap；全部旧会话／Bearer 作废、旧密码不能正常登录，恢复账号待核验；随机 epoch／cutover 拒旧 Key，旧 pending 终止，未知日账冻结，按身份／资源／读写／外部调用／worker 分范围开放。 | 已覆盖；不能以“备份 owner 自证”、次日额度解冻或旧引用打开为全面恢复。真实恢复演练仍未执行，不重复要求 RPO=0。 |
| 前端、API、数据库约束与完成门槛 | [契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:168)，范围 168–232；[切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:35)，范围 35–94。最小路由、错误码、重试方式、逻辑实体与唯一终态有记录；前端按钮不代替权限，既有 Key 优先于配置变化，同会话 expected_parent 防混写，S7 全 SM 完成门槛。 | 总体已有记录；顺序缺口单列 B-R2-01。没有为凑文档类型要求另写完整 UX 或 architecture 才准 S0 开始。 |
| 4 GB、接口变化、复用与许可证、真实参与 | [技术对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:135)，范围 135–160；[PRD 待办](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:385)，范围 385–392；[addendum](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:74)，范围 74–79。版本／实际 API／硬限制／目标机资源在接入前核验；来源、依赖与许可在抽取前留档，复用失败允许重划模块或自实现；4 GB 测服务并存峰值，不拿内存限额相加当成绩。 | 已记录待执行验证。MaxKB GPLv3 声明不是本轮法律结论；不调用收费 API 验证、不重问预算／工时。AI 编码、用户核对理解与实际记录边界清楚。 |

## 3. 已记录待执行、延期与可选事项

- **待执行且会阻断后续切片／完成：** P0 的真实解析／来源／图意、embedding 与答案模型、实际上下文限制；目标 4C4GB 的峰值／磁盘／连接；正常、并发、超时、崩溃、权限／版本变化、删除、旧备份恢复的正反例；冻结 32 题与独立权限验收；实际基线和优化对比、真实异常复盘。记录“未运行”是正确状态，不构成缺少成绩的规划发现。
- **接入时才补充的事实：** 运行侧凭据、千问具体型号、目标机连通／Ubuntu／磁盘、证书、供应方限制、依赖／镜像版本和生效配置。已有负责人及触发条件，无须重新访谈已确认角色、时间投入或固定充值预算。
- **可选／延期：** 中文关键词、混合融合、重排、ANN 按失败触发；电脑 Milvus 仅后续对照；其他 Agent 能力在四场景 RAG 之后。本期不新增任意历史检索选择器、通用 OCR／富文本编辑器、Word 预览服务、消息队列或本地 MinerU。

## 4. 下一轮对抗与改判规则

本稿现已封存，供与 John A 交换；三项属于可针对原稿修补的交接边界，不据此改写用户既定选择。请 A 逐项以现行原文反驳或给出最小修订，尤其核对 B-R2-03 是否已经由既有“请求意图”明确覆盖全部外部调用。若已有充分约束，直接撤回；若接受，必须在实际权威契约／切片中改稿，再由 B 复核准确行文、负例及结束条件。没有实际修订或明确原文依据，不把口头同意当 CLOSED。

后续任何 PASS 仅表示可以按记录的切片开始实施；P0、部署、4 GB、权限故障、恢复与产品 SM 的真实验证都不能因此自动通过。
