# Winston B 交叉质询判读

独立初评封存后才读取 A 的 11 项，并与 A 直接质询。判断仍以 manifest 冻结输入为准；以下 canonical 链接定位同版原条款。原始 A/B 发现未覆盖，基线与现行方案未改。当前没有应用代码，本次没有执行运行测试、收费调用或证明已经存在 XSS。

| 原项 | B 判读 | 合并或约束 |
| --- | --- | --- |
| A01 | accepted | 与 B01 同一窗口迟发反例，IR 只计一项 |
| A02 | clarification-only | 未承诺在线热改 gate，现行占用不得伪改 |
| A03 | clarification-only | 有限队列已定，数值/领取机制交 S0 |
| A04 | rebutted | PRD 已明确退出凭证失效、重新加入不授库权 |
| A05 | rebutted | UX 已明确冲突不覆盖，版本令牌只是实现选择 |
| A06 | clarification-only | 跨页准确定位已定，需在共享 schema 落实 |
| A07 | clarification-only | 图意绑定原图、表示标签已定，需在 DTO 落实 |
| A08 | clarification-only | 平台验证是已有合法动作，可用泛型 job/context 承接 |
| A09 | accepted | HTTP 缓存交付层未被应用缓存代次控制 |
| A10 | accepted | 原始字节的 MIME/inline 交付未被解析清洗控制 |
| A11 | rebutted | PRD 已禁止失权历史重新进入生成上下文 |
| B02 | accepted | 会话绑定 CSRF 与未登录首次登录存在前置循环 |

## A01／B01：窗口迟发

最强反例：账号滚动 RPS=1/s；A 在 t=0 获 may_have_sent 许可后 child 暂停，t=1.1 窗口自然到期使 B 获新许可并发送，A 在 t=1.2 恢复发送。两个 call 各一次、期限有效、物理槽也未复用，却在同一本地发送窗口有两次请求。

依据：[C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:139)、[R1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:19)、[R2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:29)。原子领取和单 grant 不控制领取后仍可消费的旧许可；现稿的最晚到达守卫只明确用于远端并发组件终态。

判读：accepted，A01 与 B01 合并。修复目标应精确为本项目能监督的最后可能本地发送时刻，而不是无条件要求所有 HTTP 供应方提供绝对网络到达界。应把尚可消费的 grant 算入未来窗口，直到可证明已不能再发；从保守最后可能本地发送时刻保留完整窗口。send-by 字段或 child 检查一次时钟不足以处理检查后暂停。若真实维度按接收计量且 P0 有可证到达界，再据此保守核算；仍不承诺厂商永不 429。

最小修与关闭：补有限 grant 消费/停发证明与窗口占用的共同规则，原 call 不复发；S0 故障注入暂停 child 跨 1 秒/分钟窗口并让另一槽继续前进，以实际本地发送记录证明不跨窗透支。独立初评中 B01 的“最晚到达”措辞以本段收窄解释，原始发现不改写。

## A02：配置降额

最强反例：已有三项 task、limit 从 4 改 2，第四个旧快照 job 仍尝试领取。若真实占用被重写为 2，或每进程按不同值放行，则会超配。

现有 guard：[C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)要求统一 PG gate、真实占用、有效值取交集；[组件唯一领还](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:141)禁止无终态证据退占用；[R6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:93)要求生效有限配置。[平台页](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:211)承诺接入/默认/空间配额编辑，没有承诺 job/task gate 的在线热变协议。

判读：clarification-only。不能把无证据改计数的实现视为遵守现稿；也不能把尚未承诺的在线热激活当作确定错误。S0 可选择关闭新增受理后激活并核对，具体锁列/发布方式属已有实施裁量。

最小澄清与关闭：S0 明示配置激活途径及“真实 active 可暂高于新 limit、只停新增直到回落”，业务预算快照不创造永久安全额度。以 3→2 的占用不丢失/不新领负例关闭；若未来支持在线热变，再使用现行 gate/pool 同序事务与版本栅栏。不要求自动取消已有 task 或新增产品交互。

## A03：queued 队列

最强反例：四个远端 pending 时不断上传很小的 TXT，queued 不占 active_job，可能累积很多元数据且未处理即到 2h。

现有 guard：[R1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:17)已要求有限 PG 队列、稳定游标及原 2h 包含排队；[物理预算](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:123)还含 PG/WAL、控制余量。无限入队并不符合“有限”；2h 到期也已有终结/停写责任，现稿没有保证任意负载下所有已排队任务必成功。

判读：clarification-only。缺少具体条数不等于缺少边界决定。新增逐空间份额和新的公平产品政策不是本轮必须的最小修。

最小澄清与关闭：S0 在配置/迁移中落实有限排队条数、饱和时可识别拒绝、稳定领取与过期扫描；fixture 覆盖小文件饱和及 queued 到期，期限不刷新，已持原件/清理账不消失。

## A04：退出后重加入

最强反例：只把 membership 置 inactive，旧 Bearer/ACL 保留；之后重邀使旧授权复活。

足够的现有 guard：[PRD 119](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:119)已定加入本身不授普通成员任何库权；[PRD 141](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:141)明确退出者团队访问与凭证失效；[UX 退出](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:48)同样要求停止团队凭证。仅动态取空交集、重加入即恢复违反上述真源。

判读：rebutted。永久撤销、清 ACL 或 membership 代次绑定是实现机制选择，不存在需重新选择的业务行为。

关闭条件：S1 实现现有规则并保留退出→重邀→旧 Bearer/旧 ACL 不恢复的负例；不新增架构缺陷或重复写一份政策。

## A05：陈旧表单覆盖

最强反例：O 撤 B 后，仍合法的 M 保存旧完整 ACL={A,B,C}，恢复 B；action_key 不同，space EX 仅串行。

足够的现有 guard：[UX 201](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:201)已经明确成员/权限同时改变以当前结果刷新、冲突不覆盖；[主干权威边界](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:23)继承该 UX 行为。自动恢复被撤授权不是一个合规实现分支。

判读：rebutted。expected_revision/If-Match 或精确差量动作是 S1 可选实现机制，action_key 的职责也无需改成乐观锁。

关闭条件：两名当前合法管理者的交错保存负例证明不覆盖；冲突响应与重读/保留输入按原 UX 实现。

## A06：多 spans 与跨页定位

最强反例：同 chunk 的表头在第 7 页、数据在第 8 页，只序列化一个合法 locator 使另一页不可知。

现有 guard：[C3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:45)已要求跨页/不连续用多个有序 spans，不得用假连续范围；[简单跨页表格](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:81)和 [来源核验](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:178)要求准确可回查。只保留其中一页不能满足既定准确性。

判读：clarification-only。C3 的 span 对象 schema 确需具体化，但契约已选定跨页必须能准确定位；不必新增来源业务规则。初次交流我倾向 accepted，复查父约束后收窄为共享 DTO 实施澄清。

最小澄清与关闭：同一 contracts 所有者把每个实见 span 绑定自己的可靠页/区域/资产 locator，citation 可逐片段或有序多页显示；正负 fixture 验证第 7/8 页对应文本，K 仍按 chunk≤5，不额外检索。

## A07：图意派生表示

最强反例：视觉生成句写入 source_text，只靠原 PDF hash 呈现成原文摘录，无派生标签。

现有 guard：[实施契约 184](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:184)要求校核后的说明绑定原图和定位成为受控块；[C3 图表绑定](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:44)要求原资产/上下文；[UX 168](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:168)明确原件、提取、表格/图意说明标签。无法区分的实现违反已定表示语义。

判读：clarification-only。kind=pdf/structured 是位置类型，不是表示类型；需 DTO/资产关系落实，但原规则已经选择了派生与原件分离的行为。初次交流中的 accepted 倾向据此收窄；完整 provenance 字段清单不是新的产品需求。

最小澄清与关闭：共享表示补有限类型及不可变派生资产→原图/locator 关联，利用已有 job/call/processing_config 的受控元数据追溯必要生成来源；S2/S5 fixture 同时验证标签、实际派生文本 hash、回原图与校核依据。

## A08：平台验证接入

最强反例：只有平台权的管理员验证未保存配置 A；A 的响应迟到时保存了 B，若无归属/指纹则可能绕 gate 或绿标 B。

现有 guard：[FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:159)与 [UX 211](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:211)已选独立验证、当前平台资格且不授库权；[ExecutionFence](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:53)含泛型 owner_context_id；[全传输统一守卫](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:87)不允许直接调用绕过。job/context 并非只能由业务问答创建，现稿不要求伪造业务读权。

判读：clarification-only。最小需要落实验证用 job/context 的当前平台资格、有限常量样例、待验证指纹与条件结果，不强制新增 validation_context 实体或业务规则。

关闭条件：S0/P0/S1 对平台验证 owner/fence、action_key、call/permit/迟到账形成 schema/负例；验证 A 迟于保存 B 时不能将 B 标已证，样例不读取业务库正文。

## A09：HTTP 缓存

最强反例：用户 A 合法取得带 Last-Modified/ETag 的页图/原件，无明确缓存限制；退出后 B 在同一浏览器访问相同 URL，HTTP cache 命中新鲜副本而未访问后端。新 fetch 持新本地代次也不能证明缓存 body 属 B。

现有 guard：[C4 私有读取](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:69)只对到达后端的读取重核；[前端归属](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:399)清 Pinia/组件及迟到回包，不控制原生 HTTP cache。[RFC 9111 §4.2.2/§5.2.2.5/§6](https://www.rfc-editor.org/rfc/rfc9111.html)支持在一定条件下启发式缓存、no-store 的私有/共享缓存语义，并区别历史机制。这不是已合法显示内容的追溯回收要求。

判读：accepted。需跨 gateway/API/浏览器的交付契约，不能由“后端当前鉴权正确”推出缓存命中也鉴权。

最小修与关闭：私有 API/资源/错误统一 no-store，gateway 排除这些路由；若保留条件请求，先当前鉴权再决定 304。页面历史恢复须先隔离正文并重核 context，no-store 本身不证明 bfcache 已受控。S1/S2 的真实浏览器负例覆盖同 URL 换账号、撤权、条件请求及历史返回，且不借应用缓存/网络关闭假件冒充 HTTP 行为。

## A10：原件 MIME 与主动内容

最强反例：合法 Markdown 含 HTML 示例/脚本语法，清洗后的提取视图安全，但原始字节经受控原件 URL 以 text/html 同源 inline 交付。浏览器处理活动文档，不需要解析器执行脚本。

现有 guard：[C7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:127)约束本地格式解析；[渲染清洗](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:403)约束页面渲染；受控 citation/当前鉴权也没有选择原始字节的媒体类型与 inline/attachment 行为。[RFC 6266 §4.2](https://www.rfc-editor.org/rfc/rfc6266.html#section-4.2)、[WHATWG Fetch §3.6](https://fetch.spec.whatwg.org/#x-content-type-options-header)、[MIME Sniffing §7](https://mimesniff.spec.whatwg.org/#determining-the-computed-mime-type-of-a-resource)支持交付边界的区别。nosniff 不能将明确声明为 text/html 的活动文档变为安全文本。

判读：accepted，范围限于已有单文件原件/预览交付。

最小修与关闭：原件使用服务器格式白名单、安全文件名、attachment 和 nosniff；inline 仅允许已核的安全预览表示。主动内容若确需预览，另以受限 sandbox/CSP/隔离 origin，不能透传上游类型。S2 的含 HTML 合法 TXT/MD、直接打开原件 URL、下载与预览负例须证实不会在应用来源执行主动内容。

## A11：辅助历史授权

最强反例：新轮只选 B，先合法取 A 轮问题；随后撤 A，若派发只查 B，缓存 A 问题被继续外传。

足够的现有 guard：[PRD 277](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:277)明确历史回看/追问重查、历史消息不得绕过授权重新进入生成；[实施契约 196](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:196)只允许当前仍有权的用户历史；[每实际字符串构建](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:218)不赋快照永久使用权。只有受理时检查而使用时绕过，不是合规实现。

判读：rebutted。把历史 turn 依赖纳入快照/当前授权端口是有用实现方法，但不能因矩阵未重复每种输入来源而认定父规则未处理。

关闭条件：S3 撤 A 后继续 B 轮的负例证明 A 历史不被外传；失效历史整条剔除并重算预算，指代不明按既定澄清规则。无新产品选择。

## B02：未登录 CSRF 引导

最强反例：[C5 91](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:91)要求所有 Web 写动作同时通过会话绑定 token，而 [未登录登录入口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:28)及 [AC01](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:28)要求全新浏览器只填账号密码可达成功。现有 Origin 并列检查、登录后换会话不能创造登录前的 token。

判读：accepted；A 对全文再次检索后未找出可关闭的匿名引导。[OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)给登录表单及 Origin/非简单请求防护依据；它不等于本项目已经选定例外。

最小修与关闭：可明确未认证登录 POST 的专用规则，采用精确同源 Origin（缺失/null 拒绝）、application/json、有界固定自定义头、关闭 CORS，拒简单跨站 form；已有认证会话写动作继续 token 绑定，登录成功旋转会话/token。无需加入匿名 GET 写状态或新增账户产品。S1 覆盖无 Cookie 首次登录可达、跨站/缺 Origin 被拒以及登录后写动作仍需要绑定 token。

## 当前 IR 建议

CONCERNS。去重后留下窗口迟发、首次登录 CSRF、HTTP 缓存、原件媒体交付四个具体技术契约；需要在对应共享边界选择规则并以反例关闭，不能仅用“有当前权”“有限”“后续实现时注意”替代。它们不推翻四场景、并发 4、重阶段 1 或 S0 可独立开始；P0/S6/F0/S7 的真实运行门仍未测但已有责任/停止点，不作新缺口。

阶段关闭条件：窗口派发规则由 S0 落实，任何真实外发前必须关闭，P0 再核真实维度；CSRF 在 S1 身份入口开放前关闭；HTTP 缓存与媒体交付规则纳入共享 HTTP/schema，最迟在 S2 来源/原件、S3 问答/历史相应入口开放前关闭，不能后置到 S6。所列 fixture/浏览器验证是后续实现验收条件，本轮未新增或运行代码测试。缓存修复不承诺追回用户已合法下载/保存的旧字节。

真正人类产品选择：不必需。上述最小方案在已有委托的技术/安全实现范围内，当前只讨论修复；统一裁决和任何现行稿修改仍由 root 后续处理。本判读不自动授权或启动新的设计/修复任务。
