---
title: RAG_all 第二轮对抗性实施准备审查
date: 2026-10-16
intent: readiness
gate: PASS
scope: recorded-implementation-slices-only
material_findings_open: 0
implementation_started: false
---

# 第二轮最终 IR：PASS

**John A与原独立John B修订后均给出PASS：可按已记录切片及前置门槛开始实施。** 四组缺口已实际改入现有PRD/契约/切片，原B已逐项和全包复核，全部CLOSED，剩余material规划阻塞0，无本轮material延期或未处置项；本结论未沿用旧PASS。S0可独立开始，后续仍必须满足P0/前置/验收。**没有项目开发、收费API、部署、压测、恢复演练或质量成绩。**

完整交付为[PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md)、[现行实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md)和[实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md)，继续原位维护；[技术补充](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md)与[汇总](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/summary.md)已同步。[上一轮报告快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/baseline/previous-implementation-readiness.md)只保留历史，不作为本轮通过依据。

## 独立性、真实反驳与去重

John A使用PM＋IR；新建John B以独立上下文只接任务和资料路径，同样使用PM＋IR。两份初评先封存，双方才交换并首次读旧IR。原位置行号以round2/baseline快照为准，最终复核针对现行稿。没有重启访谈、另建侧边栏聊天或向其他聊天/外部人员发消息。

- [A独立初评](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-a-initial.md)列六类候选；[B独立初评](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-b-initial.md)列三项，均为CONCERNS，承认S0可以独立开始。
- A接受B指出S2索引/最小回看前置错位、完整token/输出预算、派发意图/迟到成本；B接受无task未PUT的有限寿命、前端迟到回包和安全台账基础前移。重复反例合并，不把上一轮三账/幂等/scope/恢复同义改写重新计数。
- **B反驳并促成A撤回：** 原Q1已有动作scope交集，不能宣称产品未定义动作授权；GET operation继承原生成动作只作明确化，citation独立scope不被过度加answers限制。同人新合法凭证可覆盖原动作/范围读取，撤旧凭证不等于永久删除本人结果。
- **B反驳并促成A撤回：** 原S7同句先冻结再优化，不能断言它已经决定先调优。F0只防漂移：首次调优前冻结，若此前未调优可S7首子步骤完成，不要求S0前选32题。
- A/B共同要求迟到可信费用能补账而旧业务不能复活；A追问OS/PG反向等待、重复PUT不可信客户端hash、上传Key双命名、规范化不能删日志。B实际读改稿再指出“原job到期后继续核对被零剩余堵死”，回原Mary补成独立有界只读上下文；没有换新编号增加发现数量。

真实交流：[A挑战/接受/撤回](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-a-debate.md)、[B反驳/切片定点](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-b-debate.md)、[B生命周期实际改稿核对](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-b-m1-check.md)。这些是实际沟通整理，不虚构历史或测试。

## 四组发现及实际处理

下列每组均可追溯到两份封存初评的逐条“原位置、触发、现有约束为何挡不住、后果、最小修复、关闭条件”。F1补上传生命周期行为，F2/F3补跨模块契约，F4补实施顺序；没有新增角色、场景或企业级功能范围。

| 组/原始ID | 准确原位置、触发与后果 | 最小实际修复与可验证关闭条件 | 状态 |
| --- | --- | --- | --- |
| F1=A-02 | [原契约36行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/baseline/implementation-contract.md:36)，另85行guard：POST预留后永不PUT/半传永久离线，无task lease可回收，容量和库重建可被永久占用 | 现行§2.4/2.6：开始/硬截止、扫描/abandon、旧Key不复活、终态与停写清理释放分离；负例无PUT/半传、完成-过期竞争、清理失败、墓碑后旧ID、重复PUT实际hash均有确定结果 | CLOSED（B已定点） |
| F2=A-03+B-R2-03 | [原契约32行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/baseline/implementation-contract.md:32)，另65行最终提交fence：旧attempt可继续发下一批/写共享路径；先发后记崩溃漏费用，全面禁止旧写又丢真实usage | 现行§2.5–2.7：prepared→may_have_sent、当前资格、隔离prefix/监督槽/稳定锁/停写清理、可信迟到事实幂等补账；发送前后/取消/删除/epoch/清物理后崩溃有结果；到期只读核对独立120s，不续旧job，真正继续须新本地job/当前guard预算 | CLOSED（B含补问已定点） |
| F3=A-04+B-R2-02 | [原契约190行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/baseline/implementation-contract.md:190)，及[原schema35行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/baseline/comparison-schema.md:35)：字符合法但输入本体/五块/24格输出超模型，ID集合/JSON可在准入前放大资源 | 现行§3.5–3.8/5.3：H/B/M分层、原Key版本、完整S/M/H/E+R、紧凑生成子集但不删事实/格、确定裁片/实见catalog、真零候选与裁空/未证/length分支、统一gate；高token/大ID/输出不足/截断/旧Key下调/零与非零未证负例可区分调用与结算 | CLOSED（B定点及全包复核） |
| F4=B-R2-01+A-06安全基础 | [原切片43行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/baseline/implementation-slices.md:43)，另54/70/78行：S2发布却等S3索引/S5最小回看，S1/S2已撤权删资料却S6才列安全依据 | S0调用/epoch/资产骨架；S1安全事件同事务与私有响应归属；S2 profile/D/generation/revision/块向量发布及最小回看；S3查询/S5复杂质量/S6重建管理与演练。B核过P0只需S0/凭据、P0定D后S2迁移，无循环依赖 | CLOSED（B已定点） |

其他初评逐项处置：A-01强指控WITHDRAWN，派生动作明确化CLOSED；A-05作为前端响应归属明确化CLOSED，不另计material；A-06冻结强指控WITHDRAWN，F0防漂移明确化CLOSED。B三项分别并入F4/F3/F2，没有遗漏也不加倍。没有以“未运行”创建新发现；没有明确延期的本轮material发现。

## Mary分题TR→TS、追问与代价

一个大问题完成才新建下一Mary，同题所有补问回原Mary。两项目均固定WeKnora a37a1bc51ad85d096df341f6d3a098f60d586f52、MaxKB 0fa9a0dae8850c1878f087f0d81c974c1d424b06，并在本轮重取标明范围源码/官方文档；只对所读路径下结论，默认/可选/自托管与厂商API分开，不从未找到外推全仓没有。

| 题 | TR边界/TS选择/代价 | 真实资料 |
| --- | --- | --- |
| R2-M1生命周期 | 本地文件/入口代次/QueueOnce不证明本项目闭包，MinerU data_id未证幂等/反查/取消；选PG代次+attempt隔离资产+有界监督槽+稳定锁/停写清理+逐传输意图。增加少量IPC/监督/清理状态；不能保证已发云请求立即停止/免费，4GB峰值仍须P0 | [主答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/answer.md)、[证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/evidence.md)、[真实追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/followup-question.md)、[原Mary收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/followup-answer.md)、[上传Key整合](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/integration-note.md)、[B反例后的原题补问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/followup-2.md) |
| R2-M2有限输入/预算 | 两项目消息/历史/字符/输出参数与阿里云token/finish_reason/embedding口径需分开核，未证全部云端模式；选H协议/B业务/M实际profile、完整预算、answer与comparison紧凑生成子集、实见证据、截断失败/零修复。部分字符合法输入会拒绝；compact表达须实测，不降原质量。计数未证保留候选P0 gate，不要求私有权重/新平台，也不拿OpenSearch计数接口冒充DashScope | [主答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/answer.md)、[证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/evidence.md)、[八项真实追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/followup-question.md)、[同Mary收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/followup-answer.md) |

上游事实与选择均有来源/访问日/未证范围，静态源码置信度不冒充项目运行验证。没有配置收费API或把研究写成费用、性能、用户掌握情况。

## 覆盖与执行停止点

[跨模块验证矩阵](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/verification-matrix.md)覆盖身份/双凭据/目标/scope/撤权/历史出口、请求/重传/重试/幂等/并发会话/丢回包、三账/跨日/崩溃、容量/派生/临时/满盘、租约/代次/未知/取消/删除清理、文档版本/索引代/profile/guard/维度/引用、比较/上下文/四态/评估、解析修正/定位/图意、可信恢复/台账gap/旧凭据/旧操作/日账/分范围放行、前端/API/DB约束/依赖及4GB/接口/耦合/许可。正常、重复、并发、超时、崩溃、权限/版本变化、删除和恢复按流程组合；不机械凑表。

纯GET不创建生成预留/运行模型，故无“重复结算/模型重试”分支，但仍查撤权/删除/恢复和前端归属；许可证是引入前静态门槛，接口/依赖升级才重核。网络与撤权、厂商接收与PG提交不构成全局原子，已合法显示/下载不可追溯收回。

| 分类 | 负责人/触发/状态 | 实施影响 |
| --- | --- | --- |
| 已记录待执行验证 | AI实施；S0适配器可用且真实凭据/目标机具备时P0：实际MinerU格式/定位/图意、独立embedding/问答/视觉配置、token/SDK/限流、服务并存RSS/连接/磁盘；全部未运行 | 未过对应前置不得完成S2/S3/S5；图意不达标阻SC-4，不降场景/金标/SM |
| 逐片负例/最终完成 | AI实施；每片首次交付即跑对应权限/任务/成本/文件/前端/预算负例，S6恢复与S7全SM/优化综合复跑；未运行 | 文档CLOSED不当产品通过，F0首次调优前冻结，四场景全部达到原SM才本期完成 |
| 实际账号/环境/备份事实 | AI先核，接入/首次部署时确需本人信息才补；主机Ubuntu/磁盘/证书、有效模型/凭据、独立受托/备份介质/频率/留存/可丢失窗口 | 暂缺只做独立基础；不让旧owner自证、不冒称RPO=0或已接受某丢失窗口 |
| 引入/升级前门槛 | AI实施；样例/模块引入或依赖/API升级前核源码固定SHA、许可/依赖/适配/接口变化并留档 | 未核不抽取/发布；WeKnora主体MIT/第三方各许可、MaxKB GPLv3不混同；复用失败可重划边界/自实现，不假定可直接抽取 |
| 明确延期/可选增强 | AI实施/规划；关键词/融合/重排/ANN在真实开发题失败时择优，电脑Milvus后续可选对照，其他Agent在RAG完成后 | 不把它们全列必做；仍须B0和至少一次真实改进对比，无收益/失败照记 |
| 本期范围外 | AI规划；通用OCR编辑器/Word服务/本地MinerU本期不做；新目标须用户明确变更 | 不加入当前依赖，也不依赖电脑长期开机 |

原四场景、角色/权限、MinerU云路线、同步主栈、整请求K=5、32题/金标/SM门槛均未降低。约半个月仍为预期，AI实际编码/用户核对理解不改，未伪造开发问题或掌握成绩。项目完成还必须取得实际功能、独立权限、故障、4GB、恢复、质量、成本和工程证据；本轮只交付可实施规划。

## 最终复核与机械检查

最终独立判断：[John A修订后IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-a-revised-ir.md)、[原John B最终IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-b-final-ir.md)。B实际读五主文/本报告/schema/UI/矩阵/两Mary收口，未发现新的整合矛盾；最终只同步其结论标签/日期/链接，不追加新政策。四组和明确化逐项定点见[B预算核对](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/john-b-m2-check.md)及前述生命周期核对。

最终文档机械核验见[原始结果](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/document-check.json)：覆盖实际文件/本地链接与行号界限、代码围栏、JSON示例、FR/NFR/SM连续编号和必要过程产物；PRD第4节角色与第7节验收相对修订前基线逐字保留。机械通过不替代产品负例、模型实测或性能/恢复/费用成绩。
