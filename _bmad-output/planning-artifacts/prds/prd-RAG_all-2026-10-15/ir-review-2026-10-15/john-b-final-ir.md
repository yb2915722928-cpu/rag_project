# John B · 最终定点 IR

日期：2026-10-15。复核者仍为初评的同一位独立 John B。使用已载入的 bmad-agent-pm 与 bmad-sprint-planning readiness gate，意图为 readiness。本轮只复核 B1–B7、实际修订是否破坏已关闭政策，以及实施切片是否满足原关闭条件；不重新扩大审查。

**最终结论：PASS——判定对象仅为“可按排定切片开始实施”。** 原七项在规划／行为契约层面全部 CLOSED，当前无需要开发者另行发明的关键产品行为或跨模块契约。可先开始 S0，后续按各自前置条件推进。此结论不表示 P0、外部 API、4C4GB 资源、恢复演练、产品质量或任何完成指标已通过。

实际依据为修订后 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:151)、[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:12)、[实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:11)，以及 M3 的实际 answer、runbook 和 followup-answer。B1–B6 承接 [上一轮实际定点复核](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-m1-m2-check.md:1)，只确认后续改稿没有破坏其关闭条件。draft／complete 标签、父级机械检查计数均不构成本轮通过理由。

## 逐项结论

| 发现 | 最终状态 | 关闭依据及原触发场景的结果 |
| --- | --- | --- |
| B1 双凭据与显式目标 | CLOSED | [契约 §1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:16) 固定渠道、双凭据整拒、失败不回退；目标逐项全有权且同上级，否则统一资源不可用。鉴权在外部调用前，历史／引用／重放继续复核，不会静默少对象对比。 |
| B2 配额／幂等／崩溃 | CLOSED | [契约 §2.2–2.3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:41) 区分诊断、逻辑操作和 Key，固定输入与执行快照；租约／硬期限／attempt 终止迟到写入，结果与计次同事务。丢回包仍成功、终态失败跨日不重执行；过期 Key 不复活。[准入顺序](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:189) 也避免默认配置／可调上限变化误破既有重放。 |
| B3 原件容量与文件边界 | CLOSED | [契约 §2.1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:26) 明确所有保留原件＋预留、原子条件受理、双份替换、清理失败不释放、FS／PG 资产恢复及独立磁盘保护。[候选创建入口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:171) 又明确客户端先保留上传 ID，同输入只建一次候选与预留，覆盖首次创建回包丢失。 |
| B4 索引切换 | CLOSED | [契约 §3.1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:75) 有逐库不可变 profile、正常增量发布、重建写 guard、revision／覆盖集复核及失败／删除条件解锁。终结的取消／废弃不永久阻写，多库不兼容整拒。历史 evidence_snapshot 不依赖旧向量永久存在。 |
| B5 对比规模与四态 | CLOSED | [契约 §3.2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:95) 及 comparison.v1 固定输入上限、稳定对象／条件、全部格与证据基数；零候选正常不足与模型结构失败分开。K=5、原金标分母和关键冲突验收均保留。 |
| B6 校核与来源交互 | CLOSED | [契约 §3.3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:105) 及动作矩阵分开生效／候选／任务，修正形成新候选、历史不原地改。PDF 页／区域回退和非 PDF 结构片段＋受控原件明确，无需发明通用编辑器或 Word 服务。 |
| B7 旧备份恢复后的撤权／删除 | CLOSED | [PRD NFR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:291)、[契约 §4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:120) 与 [M3 runbook](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/runbook.md:15) 给出非循环信任起点、独立核验与现行受托链。新随机 epoch、旧账号 unverified／密码重置和旧凭据作废覆盖旧密码重新登录；gap 无法确认的范围隔离，已知墓碑拒绝优先；新日仅解配额冻结。 |

## B7 最终反例核对

已尝试“备份后撤 owner／停账号／撤 key／删资料，再恢复旧点”；旧 owner、旧密码、Cookie／Bearer、旧 epoch／Key、迟到 attempt 都有明确拒绝或 fence 路径。break-glass 只给必要元数据恢复能力，不授正文阅读；无法列全删除状态的库不能由备份 owner 自证开放。

“台账连续校验通过但尾段未导出”仍被明确视为 gap；不存在把完整性等同完整事件集的跳步。供应方密文、上游状态查询／接回、生成计次和费用各有独立放行门槛；无 ID／无主密钥时保留 unknown／阻断。普通重启不换 epoch，连续恢复同包则必须不同；恢复后查不到的旧 Key 不能按新单静默执行。这满足原 B7 关闭条件，不要求 RPO=0 或新增平台。

## 执行计划的就绪判定

1. [S0](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:17) 无需真实账号即可完成可启动／迁移的 PG 骨架、隔离适配器和可控假件；假件不会冒充供应方通过。不存在首步依赖未来尚未决定行为的循环。
2. [P0](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:25) 在适配器及真实凭据具备后尽早与 S1 并行，覆盖格式／来源／表格／OCR／真正图意和目标资源。图意不足有独立 API 验证分支，仍不足阻断 SC-4；账号或环境未具备时仅继续独立工作，不拿开发机或假件结果替代。
3. S1–S7 各有交付、前置、FR／NFR／SM 出处、可观察验收与失败停止点，逐步形成授权、生命周期、B0、排障／对比、复杂手册、索引／部署／恢复与最终评估。依赖已完成基础能力不违反独立验收；未达前置不声称该切片已开始验收。
4. [最小接口／页面／实体契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:160) 足以指导联调，包括安全错误边界、恢复状态、同会话单未终结轮次与 expected_parent CAS。具体 SQL、库版本、模型型号和精确响应模型可在实施中锁定，不再需要产品补造决定。
5. [S7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:81) 保留冻结验收／开发调优隔离、全部原始失败、独立权限及关键题门槛，首次资源成本基线后与优化比较前登记绝对目标。四场景、SM-1–SM-7、K=5、真实成本与 AI／用户实际参与边界未被降低。

没有真实 epics／sprint-status 不影响本次结论：这些有依赖、交付与验收的切片已经实质承担本轮所需的实施拆分；未假称其是已完成代码或已运行冲刺。约半个月仍是预期，4C4GB 仍须实测，不把其改写成已保证排期／容量。

## 结论演进与范围

[初评](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-initial-ir.md:1) 的 PRD CONCERNS／全计划 FAIL 是修订前事实，保留不覆盖；[真实争论答复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-debate-reply.md:1) 的关闭条件现已由实际稿件满足。最终剩余 material 规划问题为 0，无需再作本轮最小修正。

本轮只完成文档定点复核；没有运行产品测试、访问收费 API、部署服务器或执行恢复。之后若 P0 或实施结果暴露真实能力缺口，应按已排定失败分支修复／提出有证据的变更，不能用本 PASS 代替任何执行验收。
