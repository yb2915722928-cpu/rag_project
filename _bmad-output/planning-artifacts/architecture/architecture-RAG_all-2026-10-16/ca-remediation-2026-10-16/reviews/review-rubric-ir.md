# 独立 rubric、输入 reconcile 与实施就绪复核

日期：2026-10-16。审查者：新上下文独立 reviewer，未参与本轮修订。范围：冻结的12份现行规划文档；只写本报告，未修改 canonical。方法：实读全部12件、最新深审四项 accepted 的原始反例、架构 reviewer gate 和 readiness gate；校验修改前15件 manifest/baseline，核对主干变更及受影响规则，重新计算文件哈希并独立运行 spine lint。

**结论：建议 PASS（recorded implementation readiness）。新增 material 规划缺陷0；R01–R04的规划规则和对应开放前验收均关闭。S0可以开始，其余切片依已记录前置推进。** 这不表示P0、真实供应方、目标4C4GB、可信恢复、F0或SM运行验收已通过；它们均仍为未来硬门。

## 1. 冻结范围与完整性

冻结真源为[review-manifest](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/review-manifest.json:1)。以下每行均重新计算 canonical 和 snapshot，二者与 manifest 的完整 SHA-256 一致，合计 **12/12**。

| 文件 | SHA-256 | canonical / snapshot |
| --- | --- | --- |
| [ARCHITECTURE-SPINE](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1) | f2562f959fceb22ec06f0328f39d1dcc28312494a2badcbcc08edeea75f389a2 | MATCH / MATCH |
| [shared-contracts](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:1) | 3cbeb99748de09e9f33e2daf97308b4c4ea6faef54c9b370ff7c40228e03af5b | MATCH / MATCH |
| [runtime-operations](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:1) | 54498a3c7aa600348cfc65dab8952f090b547ba2ed0b32f05b8103de508c1e68 | MATCH / MATCH |
| [requirements-architecture-traceability](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md:1) | 4e31b70cd804c350a20b2c81fe914ac98eeb62180991be632de1c40bd501d27c | MATCH / MATCH |
| [technology-evidence](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:1) | f7b53dc1232fb0d518485479d99f79ed5767669f4346a688cf35c90966da9da8 | MATCH / MATCH |
| [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:1) | 0963d529922a6b3812c8f8311f29f5112a537a59ca62616f4dc45a245baaa299 | MATCH / MATCH |
| [implementation-contract](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:1) | 1482841f4c780cf79402c80f7f06e45c1579dbe73c9929f749f54fa1cc18e0c7 | MATCH / MATCH |
| [implementation-slices](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:1) | 21c2b54c797755689d70f1fcef22b6504301073ecf16b631fd3a823c473f834c | MATCH / MATCH |
| [DESIGN](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md:1) | 179cfc6eccdeb58ed3fb9ee8ec3abb400f9ac7e7e49b8e197596a256ffaefc48 | MATCH / MATCH |
| [EXPERIENCE](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md:1) | 67d0b4d412eba225b2e13a6578c89c69237c303df26c5707e3863f35eb8a28a2 | MATCH / MATCH |
| [page-contracts](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:1) | f1e8cfd2588e63188aefbf779aa7af4c054460cc03246ff820a7c8627706d2b1 | MATCH / MATCH |
| [acceptance](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:1) | 68ba6634d6714fe1185ebe62c4e90f0ad32dd0d8a8aae88777d5ed71d5fe6ebb | MATCH / MATCH |

[修改前input-manifest](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/input-manifest.json:1)的15份 baseline 亦重新计算，15/15匹配。比较新旧主干，AD标题及ID集合完全不变，仍为AD-1–AD-14，Stack段逐字不变。PRD和DESIGN的哈希与修改前相同。本次未依据现行IR的旧结论投票；最终IR由根审查者在各独立镜头结束后发布。

独立执行 [lint_spine.py](/E:/aaa-project/rag/.agents/skills/bmad-architecture/scripts/lint_spine.py:1)，workspace为[现行架构目录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16)，exit 0、ok=true、total_findings=0。此结果只检查主干机械结构；下文语义判断独立作出。

## 2. 输入 reconciliation

权威关系可执行：[主干23–27行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:23)要求实施同时读取业务输入、UX、C1–C8及R1–R8；AD是摘要，不是绕过companion的替代。下表是本镜头实读输入后逐项核对的结果，并非把原追踪表的覆盖数量当成证明。

### 2.1 PRD 的 FR、NFR 与 SM

FR来源为[PRD功能需求](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:121)，范围：121–303；对应切片和正负例来自现行实施切片及验收契约。

| 输入 | 独立核对的非平凡规则 | 架构 / 切片 / AC | 结果 |
| --- | --- | --- | --- |
| FR-1 | 个人隔离、同人跨团队异角色、普通身份不能自建团队 | AD2/4；C4/5；S1；AC01/03/05 | 一致 |
| FR-2 | 邀请接受才入队、唯一有效owner、先交接、降级/离队负责人接管 | AD2/3/4/13；C4；S1；AC02/04 | 一致 |
| FR-3 | 角色决定动作、逐库决定范围、负责人撤权同步清授权接管、当前权复核 | AD3/4；C4；S1→S3；AC03/04/16 | 一致 |
| FR-4 | 平台不读正文、三账、替换双份容量、同Key/跨日/零候选计次 | AD4/8/9/11/13；C1/4/8；S1→S6；AC05/15/20 | 一致 |
| FR-5 | 本人单空间只读凭证、双渠道整拒、任一显式目标不可用整拒、原动作scope | AD1/4/5/11；C2/4/5；S1→S3；AC19 | 一致 |
| FR-6 | 五格式、逐文件受理、有限上传、首次partial有范围、正常自动发布 | AD5/6/7/8/12；C3/4/7；P0→S2；AC06–08 | 一致 |
| FR-7 | 真表格/OCR/图意、PDF物理页/可靠bbox、非PDF真实结构、新候选修正 | AD5/6/10/12；C3/7；P0/S2/S5；AC10/13 | 一致 |
| FR-8 | 新版失败保旧版、替换partial不盖旧版、迟到不能复活、历史只核验 | AD3/6/9/12；C3/4；R3；S2→S6；AC08/16/17 | 一致 |
| FR-9 | 当前权精确B0、K5、完整预算、零原始候选与预算裁空分开 | AD4/5/10/11；C1–4/6；S3；AC12/15/16 | 一致 |
| FR-10 | 完整日志/环境、候选原因、顺序检查、必要澄清、不执行命令 | AD10；C2/3/6；S4；AC11 | 一致 |
| FR-11 | 流程/材料/真实负责人、缺失不编、冲突双方 | AD10；C2/3/6；S3；AC12 | 一致 |
| FR-12 | 固定文档版本、全格四态、直接证据、互斥双方、compact128整答验证 | AD5/9/10/11；C1–3/6；S4；AC14 | 一致 |
| FR-13 | 型号/版本/数值单位/表头适用条件原子保留、真图意专项不能平均抵消 | AD5/6/10/12；C3/6；P0→S5；AC13 | 一致 |
| FR-14 | 单空间会话/父轮次、五投影、完整一次呈现、历史重核、异步归属 | AD4/5/11/12；C2/3/4/7；S2→S5；AC16/18/21/23 | 一致 |
| FR-15 | 有界任务、归库继续、原ID核对/新本地继续/知情重交分开、清理独立 | AD6/7/11/13；R1–7；S0→S6；AC07/09/22 | 一致 |
| FR-16 | 同事务安全台账、默认日志无正文秘密、逐call真实成本/unknown、反馈 | AD2/8/13/14；R6/7；S1→S7；AC05/20 | 一致 |

NFR与SM来源为[PRD质量与成功指标](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:305)，范围：305–344。

| 输入 | 独立核对结果与承接 |
| --- | --- |
| NFR-1 | Web/program/worker派发及私有资源共用当前权；AD1/3/4/12、C4和独立SM6同义。 |
| NFR-2 | 条件发布/唯一效果、旧attempt失效、先墓碑后清理；AD3/6–9/11、R1–3有竞态及故障门。 |
| NFR-3 | request/operation/job/call不混用、结构日志/安全台账/业务快照分开；AD5/7/8/13、R6无正文默认日志。 |
| NFR-4 | 独立物理/逻辑/账号限额、并存资源预算、目标机峰值、少于20样本不包装P95；AD7/10/11/14、C8、R6/7未冒称成绩。 |
| NFR-5 | 干净环境、匹配一致包、新随机epoch、独立受托链/台账gap、逐范围放行、同包两次恢复；AD13/14、R4/5/7落实。 |
| NFR-6 | 合法样例/秘密隔离、最少IPC秘密、诊断材料受控；AD4/7/13、R1/4/6落实。 |
| SM-1 | 原24可答≥21且每场景≥5/6未变；AD10/14、R7、F0/S7、AC原门槛保留。 |
| SM-2 | 原必要证据单元合并≥85%，只认实见片段；C3/6与预算快照未换分母。 |
| SM-3 | 事实直接支撑≥95%、引用可打开100%；失败/空事实不能算100%，HTTP200不证明语义。 |
| SM-4 | 原8/8不足题全过；预算/依赖故障不改不足题，禁止全面拒答刷分。 |
| SM-5 | 表格、OCR、真图意、冲突、版本差异五类专项和简单跨页表格人工一致均保留。 |
| SM-6 | 独立于32题的全部权限专项，含输出前撤权/历史/引用/下载/负责人，分母独立保留。 |
| SM-7 | 四场景Web与原API、导入替换删除重试、真实改进对比与异常复盘；退步/失败记录仍必需。 |

### 2.2 实施契约全部实质章节

| 输入章节 | 与AD/C/R的独立核对 |
| --- | --- |
| §1 | 当前身份、目标整拒和新匿名登录路径与AD4、C4/5一致；首次无会话token可达。 |
| §2.1 | 三账和原件容量、物理预算分开；AD6–8、C4和R2/3不提前释放。 |
| §2.2 | request/operation/Key分离、原规范HMAC、24h/7d、终态不重跑；AD11、C1/2一致。 |
| §2.3 | lease/token/deadline条件、结果/依赖/历史/计次一次提交；AD3/8/11、C4一致。 |
| §2.4 | 未PUT/半传独立寿命、实际重复hash验证、cleaned独立；AD6/7、R2/3一致。 |
| §2.5 | 每call一次prepared/may_have_sent、网络非原子、迟到只补成本；AD7/8、C4、R2一致。 |
| §2.6 | 两个全系统独立gate、单重阶段、原2h期限、writer自持锁/清理顺序；C4/8、R1–3无反序政策。 |
| §2.7 | 独立有限只读核对、新本地job、另行知情解析重交；R2和五投影动作无合并。 |
| §3.1 | 不可变profile/兼容指纹、generation/revision、guard、历史证据独立；AD9、C3/4、R5一致。 |
| §3.2 | 全格四态、固定版本、轮转K5、真正零候选模板；AD10、C2/3/6一致。 |
| §3.3 | S2最小来源回看、PDF安全页图/非PDF真结构、原件attachment；C3/7和UX一致。 |
| §3.4 | P0固定图意样例，缺口仅触发独立视觉验证且保MinerU主路；AD10/14、R7一致。 |
| §3.5 | H/B/M交集、有界解析、已有Key先匹配、完整当前输入不裁；AD5/10/11、C1/2/6一致。 |
| §3.6 | 完整消息I及最大合法R、剔整条历史/按原名次裁原子组、catalog=实见、失败分支；AD10、C3/6一致。 |
| §3.7 | 公共DTO和generation子契约分开、四态/量值/冲突语义、截断失败；AD5/10、C2/6一致。 |
| §3.8 | 查询逻辑2/用户1/子路1、无等待队列、多维账号共池与窗口open/sealed；AD11、C8、R1/2一致。 |
| §4.1–4.4 | 独立恢复信任、安全事件同UoW、旧身份失效、gap/unknown保留、逐维放行和两次新epoch；AD13、R4/5/7细化且未放宽。 |
| §5.1 | 入口能力不创造新权限；GET无副作用、原动作scope/citation独立、资源受控；AD1/4/12、C2/4/7一致。 |
| §5.2 | 私有no-store/无304、统一schema及完整返回、单会话忙指针；C2/4、AD5/11/12一致。 |
| §5.3 | HTTP+error+retry_mode，失败不能装不足，unknown不填0；C2、R6一致。 |
| §5.4 | 逻辑实体归属、非负、唯一Key/transition/活动指针；AD2/3/5/8/9/11、C4一致。 |
| §5.5 | 响应归属、pagehide/pageshow/后台恢复先遮蔽重核全部依赖、原操作网络恢复；AD12、C4和UX一致。 |

§2.6由现行[实施契约108行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:108)明确覆盖旧整文档并发1种子，因此未把PRD旧描述推成新的产品冲突。§2.6的锁序后缀由[116行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:116)明确补入架构C4账号/space前缀，未形成第二套反向锁序。

### 2.3 UX 的视觉、IA、G 与AC

[DESIGN](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md:185)的16同名组件、浅色Element Plus、字体/tokens、断点、矩阵局部滚动、来源布局、键盘/对比目标由AD12完整继承；安全页图/attachment不另创视觉体系。视觉中“原件”区通过已记录的“原件页图/原件下载”标签承接，不要求浏览器inline原始PDF。未改DESIGN不构成R04遗漏。

| IA | 实读页面规则 / 原验收 | 架构承接 |
| --- | --- | --- |
| IA-01 | 全新无Cookie登录、认证写token、当前本人；AC01/18 | AD4/12；C2/4/5；S1 |
| IA-02 | 邀请接受、切空间清私有输入/新会话；AC02/03/18 | AD2/4/11/12；C4；S1 |
| IA-03 | 角色×库权/负责人、显式范围/删除；AC03/04/05 | AD2/4/6/12；C4/5；S1 |
| IA-04 | 五投影、旧版可用、墓碑清理/重建；AC06–08/17 | AD6/9/12；C7；R3 |
| IA-05 | 每文件Key/预留、双份预算、原期限；AC06–08 | AD6–8/12；R2/3 |
| IA-06 | 最小校核、三条继续动作、本人与维护者区别；AC08–10 | AD4/6/7/12；C3/7；R2 |
| IA-07 | 三场景受控facts、原Key/父轮次/反馈；AC11–13/15/18 | AD10/11/12；C2/3/6 |
| IA-08 | 完整四态矩阵、固定版本、compact128；AC14/15 | AD5/9/10/11/12；C1–3/6 |
| IA-09 | PDF安全页图、非PDF真结构、attachment、每读重核；AC10/16/18/21 | AD4/5/6/12；C2/3/4/7 |
| IA-10 | 本人凭证一次显密、单空间scope、三账；AC15/19/20 | AD4/8/11/12；C1/4/5 |
| IA-11 | owner/邀请/负责职责、冲突不覆盖；AC02–04 | AD2/3/4/12/13；C4 |
| IA-12 | 平台无正文、配置/运行元数据、受控恢复；AC05/17/20/22 | AD4/8/9/13；R4–7 |

| 共同G | 逐项核对结果 |
| --- | --- |
| G-01 | 身份/登录实例/空间/epoch/代次及页面恢复重核与AD12/C4一致。 |
| G-02 | 初值/显式资源/版本身份和必填呈现由UX拥有，AD5/12不另造默认。 |
| G-03 | 服务器EffectiveLimits、未知阻新单、旧Key快照与C6/R6一致。 |
| G-04 | 当前输入不裁、同schema有限校验、字段焦点与AD5/10/12/C1一致。 |
| G-05 | 显式一次动作、GET无写/外发与AD7/11/C4一致。 |
| G-06 | 原Key/operation恢复、Abort不退款与AD8/11/12/C2一致。 |
| G-07 | 单空间显式全集、任一不可用整拒与AD4/C4一致。 |
| G-08 | 同上下文内存保留、切换清空、受理快照固定与AD11/12一致。 |
| G-09 | 确认不代鉴权、知情重交默认未勾与AD4/6/7/R2一致。 |
| G-10 | 原格/行返回、焦点圈、轮询不抢焦点由AD12继承。 |
| G-11 | 正常四态/失败、unknown/0、原上海日桶与AD5/8/11一致。 |
| G-12 | citation受控解析、清洗/安全页图/原件attachment、无私有持久cache与C2/3/7、AD12一致。 |

AC01–23逐项复核结果均一致：01身份→C5；02邀请owner→C4；03角色范围→C4；04负责人/降级→C4；05平台→AD4/13；06容量→AD8/R2；07上传清理→R2/3；08发布五状态→C7；09核对/继续→R2；10来源/媒体→C3/7；11排障→AD10；12企业→AD10；13手册→C3/AD10；14全格比较→C1–3/6；15网络计次→AD8/11；16历史删除→C3/4；17重建→AD9/C4；18归属缓存→C2/4/R4；19程序scope→C4/5；20三账接入→AD8/R6；21键盘/清洗→AD12/C7；22恢复→R4/5；23响应式→AD12继承DESIGN/EXPERIENCE。原23个AC编号未删除或被R01补充替代，原正反用例仍是必需运行证据。

## 3. R01–R04原始反例逐项关闭

原始 accepted 及具体时序来自[最新深审实施就绪裁决](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/implementation-readiness.md:21)，范围：21–30。下列“关闭”只指规划缺口关闭。

### R01：迟发grant跨窗口

原反例是A在t=0领grant后暂停，B于t=1.1凭新窗口额度发送，A于t=1.2才用旧grant，使一次发送窗口聚集；单次grant、send-by或child读钟不能防住。

[C8的155–161行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:155)给出唯一算法：may_have_sent原子创建send_open charge；任意时刻准入计全部open和封口后尚未满W的sealed charge；只有监督证明本call发送child/受控发送者已停、FD/IPC已闭、旧grant已毁且不可恢复，才持久一次proof并取随后DB上界，继续留完整W。A仍可发送时始终占额，因此B不能以领取时刻过窗取得同份额度。读后暂停、部分写、controller崩溃、失联child、未确认kill、时钟异常、普通重启和旧包恢复均明确保守阻断；HTTP/task终态和usage不提前退窗口额。该规则保住本地发送窗口，未误承诺网络到达窗或厂商永不429。

同步已落入AD7/11/14、R1/2/5、实施契约§3.8及S0/P0。[S0门](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:34)、[R7 R01](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:136)和[补充验收R01](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:231)要求秒/分钟跨窗、检查后暂停、部分写、重复seal/重启/恢复及另一槽推进的可观察负例，且**任何真实外发前**先通过本地假件。原反例若重现必违反现行准入公式；规划关闭。

### R02：匿名首次登录的会话token前置循环

[C5的97行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:97)明确选择独立匿名登录路径：精确受托部署Origin、JSON和X-RAG-Login:1，CORS关闭，拒missing/null/跨源Origin、form/缺头；首次不要求尚不存在的认证会话token。成功新建会话和绑定token，受控no-store响应交内存，重载可经当前认证context取token；其余已认证Web写仍精确Origin+会话token，固定登录头不能替代。现有过期Cookie亦不会重新进入前置循环。

实施契约§1/§5.1、S1、EXPERIENCE登录组件/Flow7、IA01和[AC01](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:24)均承接正负例；[R7 R02](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:137)将其设为身份入口开放前硬门。新浏览器可以依现行规则成功登录，跨站请求不能借此免防护；规划关闭。

### R03：HTTP缓存绕过当前授权与历史内存恢复

[C2的35行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:35)覆盖所有私有Web/program成功与错误、context/状态/历史/页图/原件：no-store，不发ETag/Last-Modified、不返回304，条件请求仍当前授权。[R4的66行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:66)显式关闭私有proxy_cache/no_cache/bypass，覆盖网关错误，禁止私有静态直出及可缓存错误回落。A的已授权同URL响应不再是B可合法复用的HTTP缓存body。

[C4的77行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:77)另管私有持久缓存、pagehide、pageshow及bfcache；恢复先遮蔽/清旧context/变更代次，再核当前context及全部显示依赖，失败无旧快照兜底。没有用no-store自证bfcache清除，也没有承诺追回已合法显示/保存字节。

实施契约§5.2/5.5、S1设施/S2资源/S3历史、EXPERIENCE、G01/12、IA09及[AC18](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:177)明确真实浏览器同URL换账号/撤权、If-*、back/forward/bfcache及迟到回包负例。各入口开放前分别验，S1中间件通过不能替代S2/S3。原反例若重现必违反C2/R4或C4；规划关闭。

### R04：合法TXT/MD被当同源主动文档inline

[C7的135–143行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)明确原件和预览两边界：原件按已核PDF/DOCX/TXT/MD映射准确MIME，同时attachment+nosniff；安全有界filename/fallback/filename*，不透传客户端或上游头。inline仅本地解码/重编码并核字节/像素的PNG/JPEG，文本/MD/提取走受控文本字段清洗渲染；不inline原始PDF/HTML/SVG，不抓远程资源。规则明确nosniff不能令text/html惰性，也未增加主动内容预览能力。

实施契约§3.3、S2资源门、EXPERIENCE来源组件、G12/IA09及[AC10](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:105)同步含HTML/脚本的合法UTF8 TXT/MD、伪MIME/扩展、恶意CRLF/路径文件名、真实浏览器无执行/无头注入及no-store/当前权。R7 R04要求S2资源入口开放前通过；原合法文件可继续合法下载/安全文本呈现，不能按原反例主动inline，规划关闭。

本镜头实际打开并核对了[OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)、[RFC9111 no-store与应用历史边界](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.2.5)、[HTML PageTransitionEvent](https://html.spec.whatwg.org/multipage/nav-history-apis.html#the-pagetransitionevent-interface)和[RFC6266 disposition/filename](https://www.rfc-editor.org/rfc/rfc6266.html#section-4)。它们支持所用机制；具体严格取值由本项目决定，不能据此推定真实浏览器/部署已通过。

## 4. Good-spine rubric

依据[Reviewer Gate](/E:/aaa-project/rag/.agents/skills/bmad-architecture/references/reviewer-gate.md:13)。每个AD均有Binds、具体Prevents及可落为代码/迁移/运行负例的Rule；以下复核“规则确实阻止所称分歧”，未只检查格式。

| AD | 可执行性与所防分歧 | 结果 |
| --- | --- | --- |
| 1 | 同用例、依赖方向、八模块/四服务及禁平行队列限制入口复制业务。 | PASS |
| 2 | 唯一状态写者和同UoW端口明确，区分library来源/query实见证据/execution清理/ledger账。 | PASS |
| 3 | 账号→space→KB→业务→账→gate→pool→call→组件→asset固定顺序；SH/EX及不得持事务等待可验证。 | PASS |
| 4 | 当前权/显式全集/渠道、匿名登录和私有缓存边界共同阻越权与前置循环。 | PASS |
| 5 | 单schema导出、码点/hash/locator/模型子契约分离，避免前后端和parser自造表示。 | PASS |
| 6 | 唯一上传/候选、完整原子切版、首次partial条件、墓碑/迟到/cleaned独立。 | PASS |
| 7 | 受监督子执行者、一次grant、open/sealed、稳定writer锁/清理证明确保停写与派发可核。 | PASS |
| 8 | 三账唯一所有权和transition、unknown非0、迟到只补账避免重复及早释放。 | PASS |
| 9 | profile指纹/D迁移/generation/revision/guard、持久证据与向量GC分离，防混空间及历史破坏。 | PASS |
| 10 | 精确B0/固定轮转K5、完整I/R、实见catalog及分支，防偷扩/伪不足/截断假成功。 | PASS |
| 11 | request/Key/operation、原日桶/执行快照、结果历史计次原子、三类独立槽及会话串行。 | PASS |
| 12 | 五投影、回包归属、HTTP缓存/历史恢复、安全媒体与UX继承均有可观察约束。 | PASS |
| 13 | 四服务/挂载/秘密、独立epoch与恢复信任、台账gap和逐范围放行避免旧包自证。 | PASS |
| 14 | S0/P0/F0/S1–S7及新增修复最早门，明确未测不启用，不冒称官方版本=安装成功。 | PASS |

真实分歧点未见遗漏：身份/授权、持久状态所有权、事务锁序、文件与PG协调、逻辑/物理/供应方槽、调用事实、索引代、预算/来源、网络恢复、UX投影、运维恢复均已决策。一般表列/目录/组件实现无需同级功能各发明一份政策；它们在同一个S0/S1基础单元受共享约束，不是未记录的跨模块决定。

Deferred逐项复核：具体表列/SQL/池与容器预算由S0统一落实且不能弱化C4；真实供应方/model/D/图意/额度由P0实证并按能力停行；目标Ubuntu/Engine/TLS/备份窗由S6部署方确认；F0明确首次调优前；ANN/重排/对象存储/HA/多重阶段槽首版不启；UI内部与维护排版继承既有语义。没有将身份、计账、K、停止证明、跨模块数据约定或恢复信任藏入Deferred。

命名技术：Stack精确版本与baseline完全相同，现行[技术证据E1–E4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:11)保留当日官方链接、明确维护线/模板兼容线和未证组合；E5新增标准机制证据。本镜头核对该证据链及无新增版本，未将它包装成安装/目标机兼容成绩。S0锁全依赖/工件并核组合，P0核真实用途及官方接口，仍是硬门。仓库当前无应用代码，现有少量Python文件属于BMAD工具，因此没有已存在应用代码被该主干推翻；未来代码出现后按主干约束与代码事实更新。

运维/环境未静默：R4逐服务挂载与非root/只读根/仅gateway公网；环境分数据库/卷/epoch/秘密；Ubuntu本地卷/flock边界明确，Windows假件不能替代Linux；R5定义启动/迁移/发布/一致包/恢复/回退；R6覆盖有限资源、日志秘密、告警动作、unknown及压力；R7指定责任/证据/停止点。宿主精确版本、运行窗和通知渠道保留明确触发/责任，未假填RPO/RTO或增加常驻服务。

## 5. 独立 implementation-readiness 判断

依据[Readiness Gate](/E:/aaa-project/rag/.agents/skills/bmad-sprint-planning/references/readiness-gate.md:1)的核心问题：“开发者能否实施而无需发明未记录的决定？”本包的答案是**能，依已记录切片和硬门推进**。

| 单元 | 当前已记录的可独立完成边界 / 前置 |
| --- | --- |
| S0 | 无真实凭据亦可实现工程/PG/epoch/call/资产/限流监督基础；R01假件未过禁止真实外发。 |
| P0 | S0调用/限流/资产骨架+合法凭据后隔离探路，可并行S1；格式/来源/D/预算/图意/真实额度分别形成后续门。 |
| F0 | 首次以结果选参之前冻结32题/hash/原金标/判定并隔离开发题，不要求普通实现前假造冻结。 |
| S1 | S0后交当前身份、权限、账与私有设施；R02和基础缓存/浏览器恢复验收先于开放身份。 |
| S2 | S1+P0对应格式/来源/embedding；首次交索引原子发布及最小来源，资源开放先验R03/R04。 |
| S3 | S2+真实问答预算；新增精确B0、完整结果/历史/原Key，历史入口独立验R03。 |
| S4 | S3后排障和全格比较复用已有基础，无未来S5首次提供的来源依赖。 |
| S5 | S4+P0真图意；扩复杂手册质量，不能用已完成纯文本掩盖图意缺口。 |
| S6 | S5+目标环境/操作者/介质；重建、4C4GB并存、TLS/秘密、一致包恢复两次新epoch。 |
| S7 | S6+F0及真实前置；固定原SM、B0/上一保留轮/本轮与全部失败/unknown，不到此才挑题。 |

没有单独epic/story文件不构成缺陷：[实施切片9行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:9)已声明这些是可拆故事的实施单元，并逐片记录前置/交付/验收/失败处理。本次为readiness-only，不需要生成tracking。故事再细拆须保留现有依赖和验收，不自行重选共享政策。

四场景、K=5、原SM分母/阈值未变。doc_active_job_limit与external_async_task_limit仍是**两个独立全系统gate**，各默认4/可配1–4，全部账号合计；本机重阶段仍1。未知远端task不随job终态释放，原task poll不新增task占用但仍受真实HTTP/RPS维度；原2h job deadline、上传15分钟开始/开始后30分钟/无进展60秒、Key24h/墓碑7d及已有业务期限均未被本轮修复延长。R01仅增加不晚于原期限的有限send_stop_by及停发后保守W，不将它当新的业务续期。

尚未取得的供应方、资源、恢复与质量成绩都有责任人/触发/停止点，不需要开发者发明产品或跨模块规则；未执行本身不是规划缺陷。若以后真实P0证明既定组合不可用，应保留失败并按既定分支/变更流程处理，不能为了本次PASS跳过。

## 6. Material findings 与非阻塞建议

**新增 material findings：0。** 本镜头未能给出“完全遵守现行条款仍重现R01–R04”或使当前切片必须发明跨模块决定的具体反例，因此不将假设风险、正常未来运行门或文档类型缺失升级为CONCERNS。

非阻塞建议N1（低，后续例行文档整理）：[PRD27行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:27)仍保留旧“初始同时处理一份文档”，[PRD17行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:17)保留先前PRD轮次的PASS说明。现行实施契约§2.6已明确覆盖旧并发seed，主干导航明确当前IR唯一发布处，故不构成行为矛盾或本轮阻塞；可在以后整理时加“历史种子/以当前契约与IR为准”的短导航，降低只读PRD前言者的查找成本。本报告未改冻结文件，也不要求为本建议重新访谈用户。

**独立建议：PASS。** 采纳范围限于本轮12件冻结规划及可按切片开始实施；根审查者仍须结合其他独立镜头并处理其有效发现后发布当前IR。运行验收继续全部未执行，不用本报告代替任何开放前证据。
