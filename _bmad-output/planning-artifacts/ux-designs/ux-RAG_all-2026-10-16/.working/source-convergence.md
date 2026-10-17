# 最终收敛输入摘录

日期：2026-10-16。用途：恢复 UX 上下文与设计边界；不重新评审，不改源，不编码，不发起已定事项访谈。

## 权威来源及版本

- 唯一需求基线是当前 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:428)、配套现行[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:10)及[实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:9)。PRD定角色/场景/范围/验收，契约定跨模块现行语义，切片定首次交付、依赖和停止点；技术研究、旧审查、快照只解释演进，不覆盖当前条款，不另建可任选政策。
- 当前 PRD 为 428 行，SHA256 `0963d529922a6b3812c8f8311f29f5112a537a59ca62616f4dc45a245baaa299`；契约 `c324fc9640debb90fa66d689660c2a96b62922a1e7e77a2551adfd9680476900`；切片 `02e3d53ad13011fea172f58a8fb0a5b82d371ba91999421f672b28cd4aa6a352`。本次只读计算与[最终双人复核](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:73)一致。
- [input-manifest.json](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/input-manifest.json:7)是收敛前共同输入清单，其中 PRD hash 为旧基线 `84a5f9…`，不能当作当前 PRD hash；最终稿依据 [John 版本表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/john-final.md:23)及 [Winston 同版确认](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/winston-final.md:25)。契约/切片未变。

## 已关闭事项

- 最终收敛为可进入 UX/架构：新增已证实问题 0、剩余分歧 0、需用户现在裁决 0、设计阻塞 0；见[总报告](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:14)。用户本次已启动 UX，旧报告的“等待下一阶段”不再是当前 UX 行动禁令；用户仍明确禁止编码。
- B1–B7（身份/目标、幂等与配额/丢回包、原件容量、profile与重建、对比四态、校核来源、可信恢复）和 F1–F4（上传寿命、阶段副作用/迟到成本、模型输入输出预算、实施基础依赖）均规划关闭；不是运行通过，全部负例仍要执行，见[历史问题处置表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:26)。scope/冻结强指控维持撤回，不换名再报。
- J-S1 仅新增交接导航；既有 FR/角色/四场景/优先级/NFR/SM/契约/切片不变。架构只能在现行不变量内细化，不授予重选业务语义权限；见[本轮处置](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:39)。
- 不应再次询问工时、固定预算、现场演示、角色、主栈或四场景；见[Winston 明确边界](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/winston-final.md:49)。

## UX 必须继承

- 权限模型：个人空间仅本人；团队只有所有者、知识维护者、知识使用者。团队角色决定动作，逐库授权决定范围；知识库负责人是责任关系，不新增角色，创建者自动负责。所有者本团队全库；维护者可维护授权库/负责库、只管理负责库授权与整库删除；使用者只读与反馈。平台管理员独立、不自动读业务资料；加入团队不自动获库权限，普通用户不能自行建团队。见[角色表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:111)，范围：111–119。
- 四场景全部保留：SC-1 排障（条件/候选原因/步骤与逐步引用、缺条件先澄清、不执行命令）；SC-2 企业知识（版本/流程/负责人缺失和冲突来源）；SC-3 多文档对比（逐格满足/明确不满足/不足/冲突，找不到不等于不支持）；SC-4 复杂手册（型号/版本/数值/单位/条件、正文/表格/扫描/图意和可靠定位）。见[四项代表任务](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:62)，范围：62–67。业务岗位不是额外权限角色。
- 必须覆盖的对象与状态：个人/团队空间、逐库范围、导入/候选/生效/任务/清理分离；等待/重传/失败/不足/冲突/澄清；引用/历史/撤权反馈。允许设计信息结构、页面、表单/表格、引用回看、角色入口、状态提示，禁止用隐藏按钮代替授权、用取消网络代表业务取消、用旧回包串写空间；见[UX 交接行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:51)。
- 显式目标必须非空无重复；“全部有权库”转为本次实际选择清单。混合无权目标整拒，不静默删对象；无权/不存在统一资源不可用，不泄露标题/数量/存在性。Web Cookie 与程序 Bearer 同时出现整拒；见[请求准入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:16)，范围：16–20。
- 三账表达不可混：UI 称“原件容量”，包含当前/历史/候选/失败候选/清理中及在途预留；产品问答次数按逻辑操作与上海日期；实际外部调用失败/重试仍留成本，未知不填零。见[三账表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:28)，范围：28–35。
- 最小校核/来源回看与生效/候选/任务分栏在 S2 就交付；不能延后至复杂手册或重建管理。首次部分可用标明失败范围，不完整替换不能覆盖旧生效版本；见[S2 交付与验收](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:55)，范围：55–59。

## 技术和资源边界

- Python/FastAPI、同步 SQLAlchemy/psycopg/Alembic、PostgreSQL/pgvector、模块化单体/显式 RAG；Vue3/TS/Vite + Router/Pinia/Element Plus 自建前端；PG 持久任务 + 独立 Python worker，初始同时处理一份文档。MinerU 云 API；千问问答 API，embedding/必要图意另配验证。4 核 4GB Ubuntu 同机四服务，电脑开发构建，不持续在线承接生产。只读程序 API，不引入 Agent 编排或资料写入口。见[固定边界摘要](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:55)及[前端受托选择](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:135)。
- 完整答案一次返回、任务轮询；切空间/退出清理私有缓存；引用按后端 ID 解析，Markdown 清洗后渲染。UTC 保存，Asia/Shanghai 展示及配额日期；实际文件/页数/批量/超时限制由有效配置展示。见[前端组合](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:135)与[配置待办](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:409)。
- 产品目的为实际项目经验、理解与面试；AI 编码，用户核对方案与理解；半个月是预期，不是确定排期，不做现场演示。功能交付顺序不等于删减后三场景；见[项目目标](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:23)及[整期完成界限](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:357)。

## 可直接转为 UX 验收的依据

| 固定要求 | UX/设计验证应保留的可观察结果 | 权威依据 |
| --- | --- | --- |
| 32 题，四场景各 8，24 可答/8 不足；调优前冻结题目/资料/原证据单元/判定；最终候选 K=5 | 场景与测试映射可追踪；不删失败题、不改分母、不扩大 K、不以全面拒答达标 | [评估口径](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:320)，范围：320–326 |
| SM-1：总至少21/24、各场景至少5/6；SM-2 ≥85%；SM-3 ≥95%、定位打开100% | 必要事实/条件完整；引用直支撑结论并能回看；链接存在不能代替语义核验 | [SM-1–3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:334)，范围：334–336 |
| SM-4：8不足题全正确；SM-5 表格/OCR/图意/冲突/版本五类各有关键题通过 | 不足/澄清/限定结论与故障分开；冲突并列证据；表格单位/条件与版本可核 | [SM-4–5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:337)，范围：337–338 |
| SM-6 独立权限全部通过；SM-7 导入/替换/删除/重试及四场景 Web 完成 | 撤权/切空间/历史/引用/下载不泄露；流程失败有原因和当前角色可执行的动作 | [SM-6–7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:339)，范围：339–340 |
| S3/S4 的完整返回、故障、重放、四态与零候选语义 | 依赖失败不伪装资料不足；丢回包恢复不重复调用/扣次；缺格不显示成功；零候选保留全格 | [S3 验收](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:65)、[S4 验收](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:73) |
| S5 可靠来源/回退及修正范围 | 无 bbox 回退可靠页预览；非 PDF 不编物理页；定位损坏明确失败；修正生成新候选，不改历史；普通正常文档不逐份审批 | [S5 验收](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:81) |

以上全部是规定的验收目标/将来证据，当前无产品运行成绩；最终收敛的文档检查不替代任何产品测试，见[总报告限制](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:77)。

## 真正未定项与外观偏好

- 未发现需用户现在裁决的未决业务事项。UX 待决定的是信息架构、主导航与页面组织、不同角色入口、表单与表格密度、答案/对比/引用回看结构、状态/错误/空态文案、可访问性及响应方式；应在上述不变量内形成设计提案，而非重问角色/场景/验收。
- 已有外观相关输入只有“参考 WeKnora/MaxKB 设计/交互、自建页面、Element Plus 表单/表格/对话框”，并未确认品牌色、字体、深浅主题、页面布局或独立视觉风格。检索当前 PRD、技术补充、技术对话、汇总及最终收敛相关文档未找到这些明确偏好；不得把上游默认主题冒称用户确认。依据[用户技术与参考选择](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:25)与[前端 TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:135)。
- MinerU 格式/来源/表格/图意、各模型 profile/token/SDK/限流、4GB资源/成本、可信备份/频率/可丢失窗口、许可、实际质量及用户理解都仍待对应 P0/S6/S7 或引入前真实验证。已有负责人、触发和失败停止条件，均非 UX 前置争议；UX只能表达未验证/不可用/隔离/失败等状态，不代编实测和运营数字。见[非阻塞后续项](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/final-convergence-2026-10-16/convergence-report.md:59)，范围：59–69。
