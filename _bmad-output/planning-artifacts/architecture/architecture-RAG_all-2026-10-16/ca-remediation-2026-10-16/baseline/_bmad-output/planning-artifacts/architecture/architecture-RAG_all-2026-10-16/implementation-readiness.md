---
title: RAG_all 再次深度审查后的当前实施就绪裁决
date: 2026-10-16
intent: readiness
gate: CONCERNS
scope: frozen-planning-documents
accepted_unique_behavior_findings: 4
clarification_items: 5
rebutted_behavior_candidates: 3
structural_suggestions: 4
implementation_started: false
design_modified_by_this_review: false
---

# 当前 IR：CONCERNS，S0 可开始，四处共享技术契约待补

根 Winston 根据两个新上下文 Winston 的独立审查、实际交叉质询和结构镜头反馈，重新裁决：**本轮保留四处具体技术契约缺口；上一轮 PASS 已保留为历史，当前采用 CONCERNS。** 它们不推翻既定四场景、两个全系统 gate 各默认4/配置1–4、本机重阶段1或 S0 独立开工条件；对应行为开放前必须补齐下列契约。当前不作整体上线、真实供应方、4C4GB、恢复或质量通过判断。

这是再次深度审查的交付，本轮保存发现、反驳与 IR 裁决；现行架构设计、实施契约和 UX 未改，没有应用代码、收费调用或测试成绩。[完整深审报告](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/review-report.md:1)保留全部镜头原始输出，[原始发现 JSON](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/review-findings.json:1)包含未被采纳的候选，不应将每条原始候选都视为当前缺陷。

## 四项确认发现与关闭条件

| 项目 | 具体触发、现有约束不足与后果 | 最小补充及阶段关闭条件 |
| --- | --- | --- |
| R01：迟发 grant 跨速率窗口（A01/B01，两镜独立重合） | [共享契约 C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:139)允许RPS/TPM窗口自然到期，[R2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:29)提交后给予一次grant。A在t=0领取后暂停，B在t=1.1获新窗口额度并发送，A在t=1.2仍可消费旧grant；各call只发一次、各自期限有效，却在同一实际本地发送窗口聚集。远端task终态的上界规则没有定义窗口占用与live grant的共同寿命。 | 明确仍可消费旧grant时的保守窗口占用、消费/丢弃及受监督停发证明；仅增加send-by或child读一次时钟不能处理读后暂停。S0固定暂停child跨窗口而另一槽继续的负例，**任何真实外发前关闭**；P0再核真实维度。目标限于可监督的本地发送窗口，不普遍强加所有网络的绝对到达界，也不承诺供应方永不429。 |
| R02：首次登录的CSRF前置循环（B02） | [C5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:91)要求所有Web写动作校验会话绑定token，但全新浏览器首次登录尚无认证会话/token；[登录验收](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:28)又要求未登录状态可达成功。Origin是并列检查，不会生成缺少的token，现稿未选择匿名引导或登录专用规则。 | 明确未认证登录的独立防护路径。例如精确同源Origin、JSON和固定自定义头、CORS关闭，拒绝缺失/null/跨源Origin及简单form；成功旋转认证会话与token。其他已认证Web写仍需会话绑定token。S1覆盖全新无Cookie登录及跨站/缺Origin拒绝，**身份入口开放前关闭**。这只是已讨论的最小方案，尚未改入设计。 |
| R03：私有响应的HTTP缓存边界（A09） | [C4私有读取](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:69)和[前端归属规则](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:399)控制到达后端的请求及组件状态，未固定HTTP缓存策略。合法响应被浏览器缓存后，换账号或撤权再访问同URL可直接命中副本，不触发后端鉴权；新请求的本地代次也不能证明缓存body归属。 | 私有API/状态/错误/引用/页图/原件统一no-store，gateway排除缓存；如支持304则先当前授权。历史恢复另做先遮蔽再重核，不用no-store自证bfcache已清。纳入共享HTTP及gateway规则，最迟在S2来源/原件、S3问答/历史相应入口开放前关闭；后续真实浏览器验收同URL换账号/撤权、条件请求与历史返回。不要求追回用户已合法显示或保存的字节。 |
| R04：原件与预览的媒体交付边界（A10） | [C7格式处理](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:127)禁止解析时执行HTML，[视图清洗](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:403)也不约束原始字节响应。合法TXT/MD可包含HTML示例；如果受控原件入口按text/html同源inline交付，解析与鉴权都可通过，浏览器却收到活动文档。 | 原件固定服务器格式白名单、准确MIME、安全文件名、attachment与nosniff；inline仅给明确安全的预览，不透传用户/上游主动类型。nosniff不能让明确的text/html变安全。最迟在S2资源入口开放前明确合同，并要求含HTML合法TXT/MD的下载/预览负例；若确需主动内容预览才另定隔离策略，不新增该产品能力。当前只确认规划缺交付规则，没有证明任何运行中的XSS。 |

四项均属现有产品范围内的技术契约，无需用户重新选择权限、场景或并发方向。所列测试/故障注入是实施时应取得的关闭证据，本轮没有为没有代码的项目制造测试成绩。

## 交叉质询后的其余候选

13条行为原始候选中accepted为5条（A01/B01重合，去重4项）、clarification-only为5条、rebutted为3条；原镜头重合保留，不删除或改写初评。处置依据见[A交叉报告](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/findings/winston-a-cross-check.md:1)与[B交叉报告](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/findings/winston-b-cross-check.md:1)。

- **明确化5项**：A02未承诺在线热改，配置激活机制可S0定；A03有限队列已强制，具体条数/领取机制可S0定；A06跨页准确定位已定，逐span DTO需要落实；A07图意绑定及标签已定，表示/追溯关系需要落实；A08接入验证可用现有泛型job/context承接，不强制新实体。
- **被反驳3项**：A04退出凭证失效与重加入不授库权已由PRD明定；A05并发管理保存冲突不覆盖已由UX明定；A11历史不得绕过当前授权进入生成已由PRD/契约明定。初评反例违反已有父规则，不是新的规划缺口；可以保留为实施负例。
- **结构建议4项**：前移权威/开工导航；完整PG锁序以C4为唯一维护点；将修复历史移出追踪正文；技术证据凝缩重复并发政策并引用现行规则。详见[结构镜头](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/findings/structure.md:1)。这些建议不改变既定行为，不单独阻止S0。

## 独立性、范围与当前效力

本轮三个镜头均以新上下文独立启动。A进行对抗兼容性审查，B先枚举路径/复查，再按规定读取claims；结构镜头独立检查权威与查找路径。A/B封存后才交换意见并直接质询，根代理只接收反馈及证据作IR裁决。没有用“双方同意”替代条款、具体时序或反驳理由，也没有为了凑发现数量保留已被原规则防住的候选。

[输入清单](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/input-manifest.json:1)冻结15份规划文档；[完整性核对](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/input-integrity.json:1)确认15/15 snapshot及canonical SHA-256一致。审查没有修改这些文件。上一轮当前IR已保存在[上一轮裁决快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/prior-implementation-readiness.md:1)。

P0供应方真实能力/预算/额度与1/4档验证、S6目标资源与可信恢复、F0冻结/S7原成功标准仍按既定门槛执行；未执行本身不重复报为本轮发现。当前CONCERNS须在四项对应边界补齐并复核后重新判断，不能继续仅引用上一轮PASS。