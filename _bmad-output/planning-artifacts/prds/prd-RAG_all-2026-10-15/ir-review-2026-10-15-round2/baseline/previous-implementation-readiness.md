---
title: RAG_all 两位 John 对抗审查与实施准备报告
date: 2026-10-15
intent: readiness
gate: PASS
scope: 可按已排定的实施切片开始
material_findings_open: 0
implementation_started: false
---

# RAG_all 最终 IR：PASS

**主 John 与独立 John 的修订后 IR 均通过，范围是“可按已排定切片开始实施”。** 七项规划发现已关闭，当前不需要用户补充才能确定的产品／契约阻塞为 0。S0 可独立开始，后续按 P0、依赖及验收推进；外部接入、4C4GB 承载、恢复演练与产品验收仍未运行，不能将 PASS 扩大成已达标。

最终交付是 [完整 PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md)及其中明确链接的 [实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md)、[纵向切片与前置门槛](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md)。角色、四场景、主栈、MinerU 云端方向、B0、K=5 与原验收门槛保持。

## 实际过程与结论演进

1. 主 John 执行 bmad-sprint-planning 的 readiness gate，独立列出六项反例，初评 CONCERNS；另新建一位 John，同样使用 PM＋IR，先独立评估，不看主 John 的发现。
2. 独立 John 对当前 PRD／配套给 CONCERNS，对当时缺关键实施契约的全实施交接给 FAIL，列 B1–B7；没有因为缺模板文件名或没有账号就判失败。
3. 两位 John 交换真实反驳与修复条件。主 John 撤回“多库不兼容没有决定”的误报：旧 Q3 已记录拒绝，真正缺口是重建范围和写政策；也不为凑数量另加“无实测即失败”。
4. 按三个大问题分别新建 Mary，先 TR 查两项目实际实现，再 TS 选择，同题追问由原 Mary 收口。每题原问题、证据、回答、追问均保存，未将方案当成测试成绩。
5. 主 John 将规则落实到 PRD 和完整实施契约，并补 S0–S7／P0；独立 John 先定点确认 B1–B6，再检查 B7 和全部切片，最终逐项 CLOSED、PASS。

这次审查是前轮“需求已定稿”之后的另一种检查：开发者能否按记录实施，而不再发明关键跨模块政策。初评、反驳和最终判断都保留，不改写为从未有过缺口。

## 两位 John 的真实对抗要点

以下为实际交流的整理，完整提问／回应见链接；不是虚构此前未发生的历史或隐藏推理。

**John A：** 配额、容量和重复请求虽有原则，但并发、失败、跨日和结果重放还会有不同实现。我还怀疑多库向量不兼容的行为没有决定。

**John B：** 前三项成立；多库不兼容在 Q3 原证据已有拒绝，不应重复报缺口。请补重建期间的作用域／写入和切换政策。恢复时也不能由旧备份里的所有者证明自己当前仍有权。

**John A：** 接受这项纠正。我们按独立幂等操作、原件容量账、逐库写 guard 和独立可信恢复收口；每项给具体状态、错误、负例及切片，不用“实施时再决定”代替。

**John B：** 方向可以，但关闭条件要落稿：旧 attempt 不得迟到结算／解新锁；失败跨日不能用已释放额度免费重执行；恢复纪元不能只是旧值加一；台账校验不能证明尾段没有新撤权。实际契约与切片满足后，才可改判。

**John A：** 三题 Mary 已完成 TR→TS 和追问，相关规则、schema／动作表／恢复顺序及 P0／切片已落实，请按实际稿件复核。

**John B 最终：** B1–B7 全部 CLOSED；可按排定切片开始实施，剩余 material 规划问题 0。外部验证、恢复与产品验收不在该 PASS 内。

原始记录：[John A 初评](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-a-initial-ir.md)、[John B 独立初评](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-initial-ir.md)、[A 实际挑战](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-a-challenge.md)、[B 实际回应](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-debate-reply.md)、[B 中途定点核对](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-m1-m2-check.md)、[A 修订后 IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-a-revised-ir.md)、[B 最终 IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-final-ir.md)。

## 七项关闭结果

分级沿用独立 John 初评，用来说明初始影响，不重新计重复发现。以下均已在实际稿件闭环。

| ID／初始影响 | 反例 | 采用的最小规则 | 权威落点／状态 |
| --- | --- | --- | --- |
| B1／High | Cookie 与 Bearer 冲突，或显式对比范围含越权对象 | 路由限定渠道、双本应用凭据拒绝不回退；显式集合逐项合法，不静默删目标，不泄露存在性 | PRD FR-5／9，实施契约第 1 节；CLOSED |
| B2／High | 预留后崩溃、跨日双重试、同 ID 换问题、成功丢回包 | trace 与逻辑 Key 分开；输入指纹／执行快照、状态／截止／代次，成功提交重放、终态失败不重执行、过期拒绝；产品次数与实际成本分开 | PRD FR-4／15，契约第 2 节；CLOSED |
| B3／High | 并发上传超额、满额替换、失败保原件或清理失败 | 产品原件字节＋在途原子预留，保留版本均计、实际清完归还；替换不先抵扣旧版；派生磁盘另保护 | PRD FR-4／6／8，契约第 2 节；CLOSED |
| B4／Medium | A 库切了模型而 B 未切，重建中上传／删除／旧任务迟到 | 不可变 profile、逐库活动索引代；旧索引服务，重建 guard 拒新写、删除失效候选、条件释放；异维维护迁移，当前多库不兼容拒绝 | PRD FR-4，契约第 3.1 节；CLOSED |
| B5／Medium | 对比输入无限放大、零证据被当模型失败、结果漏格 | 有限输入、稳定对象／条件、全格四态和证据基数；确定性零候选正常不足，真实 schema 失败整答失败；K=5 与金标分母保留 | PRD FR-9／12，契约第 3.2 节与 comparison.v1；CLOSED |
| B6／Medium | 修正被做成重编辑器或原地改来源；非 PDF 回看不一致 | 生效／候选／任务分别显示，角色动作明确；修订原件／合法参数新候选；PDF 真实页／区域、非 PDF 真实结构＋片段／受控原件 | PRD FR-7／14，契约第 3.3 节与动作表；CLOSED |
| B7／Medium | 旧备份恢复账号／授权／删除，旧 owner 自证，未知账重开额度 | 隔离、旧凭据作废、账号待独立核验、新随机 epoch；独立台账／受托与白名单确认，未知范围不放行，旧任务与当日缺口账安全恢复 | PRD NFR-5／FR-16，契约第 4 节与恢复动作表；CLOSED |

## Mary 的 TR→TS 选择依据

参照提交为 WeKnora `a37a1bc51ad85d096df341f6d3a098f60d586f52` 与 MaxKB `0fa9a0dae8850c1878f087f0d81c974c1d424b06`；只核对标明路径，不把“未证”扩成“全产品没有”。来源细节保留在各题 evidence 文件。

| 大问题 | TR 查明的边界 | TS 为本项目选择／代价 | 真实答复与追问 |
| --- | --- | --- | --- |
| M1 请求、计次与容量 | 所读 WeKnora 门禁／索引估算／行锁加减不是原子上传预留；两项目的 request_id／chat_record_id 不证明我们的完整幂等语义，MaxKB 所读日计次规则也不同 | PG 条件预留与终态账本、原件容量分账、逻辑 Key／执行快照；多状态和短暂预留占用是代价 | [TR／TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/answer.md)、[追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/followup-answer.md)、[证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/evidence.md) |
| M2 索引、对比与校核 | 两项目可参考 KB 模型／来源、兼容检查和分步处理，不能直接推出完整切代／异维在线迁移；来源与图意各有边界 | 逐库 guard、同维切代／异维维护；对比有限 schema 与最小校核页；重建期不能新增资料、纠错需重处理、候选多占空间 | [TR／TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/answer.md)、[追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/followup-answer.md)、[schema](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md)、[UI](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md) |
| M3 恢复放行 | 两项目认证状态可随 DB 回退，清 token 不挡旧 active 密码登录；PG 快照／PITR 不自动补恢复点后安全事件或库外文件 | 隔离恢复、独立可信核验、最小安全台账与随机 epoch、按范围放行；无可信依据会停服较久，不承诺 RPO=0 | [TR／TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/answer.md)、[追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/followup-answer.md)、[恢复表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/runbook.md) |

## 为什么可以开始实施

- 现有 PRD 与技术记录已经有实质架构／交互约束；本轮又补请求／状态／错误、容量／配额、schema／动作／来源、恢复、关键实体不变量与前后依赖。正式 OpenAPI、SQL 迁移和代码要照这些政策实现，不能再任意选择不同业务行为。
- 没有独立命名的完整 UX／架构／epics 文档，但缺文件名不等于缺决定。S0–S7 有输出、前置、FR／NFR／SM 出处、验收和失败停止点，足以作为当前 gate 的实施单元；未生成虚构 sprint-status。
- P0 前置真实格式／位置／图意／资源探路，MinerU 图意不足只触发独立视觉能力验证；仍失败则阻断 SC-4，不降四场景或 K=5／SM 门槛。
- S0 可不依赖真实账号开始，P0 在凭据具备后尽早与 S1 并行；后续阶段不允许用假件替代真实探路和验收。半个月仍为预期，不分配假工时或保证日期。

## 实施时才取得的证据

账号／凭据、服务器访问与证书条件在实际接入前处理；依赖版本、真实型号／维度／接口限制要锁定；4 GB 常驻／峰值、磁盘、时延、真实费用、质量／权限／故障／恢复和全部冻结评估仍需运行。配额与输入数字、Key 窗口都是受托可调初值，不是测得的容量或 SLO。

恢复频率／留存／允许丢失窗口和独立可信介质在首次部署登记，不能假称用户已接受某个数据丢失时长；没有可信恢复依据时按契约保持隔离。没有绕过这些前置或把缺账号变成重新访谈技术偏好的理由。

本轮仅改规划与文档，没有项目编码、付费 API 调用、真实部署／恢复或模型测量。用户学习与实际贡献记录仍以真实解释和实施证据为准。

## 文档核验边界

实际机械检查覆盖本轮 Markdown 链接、代码围栏、三份 JSON 示例、FR-1–FR-16／NFR-1–NFR-6／SM-1–SM-7 连续唯一，以及三题实际问题／证据／回答／追问齐全。机械通过只说明文件／示例一致性；七项关闭依据是两位 John 对具体触发场景的定点复核，不是运行了产品测试。

本轮最终检查实际结果为 PASS：35 份文档、255 个本地链接、3 份 JSON 示例及三题原始追问齐全，问题列表为空；原始记录见 [document-check.json](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/document-check.json)。该数值描述本次检查时的文件集合，不是产品覆盖率或服务性能。
