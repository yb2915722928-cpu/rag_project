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

# 原始镜头与处置记录

原始候选均保留。各镜头重合仅在IR中标明，不删除原项；初评不等于最终采纳。以下按镜头分组，不作严重度排序。

## 对抗镜头（11项原始候选）

# A01：延迟grant跨过RPS/TPM窗口

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:139)，C8；[runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:29)，R2。

现有守卫明确在may_have_sent同UoW取得组件，提交后给一次grant；RPS/TPM窗口自然过期。它又明确允许may_have_sent后延迟发送。C8第141行的“最晚可能实际到达”约束专用于远端并发组件终态证明，没有定义窗口组件如何覆盖尚未消费的grant。

反例：RPS=1/s，t=0.01为call-A领一次许可，child因调度停顿尚未消费grant。t=1.02原窗口过期，call-B取得新窗口许可并立即发送，A也在t=1.03恢复后发送；两个call各只发一次，都在120秒阶段期限内，却集中进入同一实际本地发送窗口。TPM同样可将上一分钟的预占带入下一分钟，与新预占叠加。这不是要求网络与PG原子或保证供应方永不429，而是本地窗口是否计入已经批准、仍有消费能力的旧grant。

最小修复：给grant有限且可监督的send_not_after/消费状态，窗口计数保守覆盖可能消费区间；过期不能发送旧grant。补跨1秒窗口及分钟窗口的故障注入，验证A暂停而B推进时实际发送数不超配置。单纯在child发送前读一次时钟仍须交代检查后暂停的处理边界。

# A02：配置降上限没有原子生效与占用债务规则

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)，C8；[runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:93)，R6；配置责任为[ARCHITECTURE-SPINE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:38)的platform_ops。

现有守卫有默认4/允许1–4、配置版本、受理快照、真实账号限额取小者和唯一领取/释放。C4用例矩阵没有“配置激活”事务，C8没有说明派发时使用哪个安全上限、降上限时如何表示已经超出新额的真实占用。受理快照用于业务预算不等于给旧操作永久保留旧安全限额。

反例：三个task运行、第四个job在本地等待；平台将task上限4改2，worker仍持旧受理快照4。实现甲把配置只用于新job，第四个旧job仍可submit；实现乙把gate行重写为新上限并保留active=3，从而拒绝新增。另一种有风险的实现是为满足新上限把active改2，之后真实释放会少计占用。现稿没有选定激活和超额语义，跨API/worker进程的配置缓存也无版本栅栏。

最小修复：配置激活与对应gate/pool在同一短UoW按既定锁序落地；不改写已取得组件，active可以暂高于新limit，新领取按现行limit判断；现行安全禁用/降额覆盖旧快照，业务输入、模型选择和原deadline仍保持受理语义。升额须附对应已取得验证的配置证据，不能只改数字。

# A03：queued队列缺独立有限准入契约

位置：[runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:17)，R1；[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:137)，C8；原件完成同UoW创建job见[implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:77)。

现有守卫将queued排除在active_job计数外，限制四项活跃job、四项未证终态task及单重阶段，规定原件受理后2h绝对期限；运行文档称“有限PG队列”。但R6的必填生效配置没有待处理job条数/空间份额，准入UoW也没有队列名额。活跃job轮转并不定义queued领取公平性。

反例：四个task在远端等待时，上传槽仍可连续接收很多很小的TXT文件。原件字节预留和物理字节预算均未超限，每次完成合法创建queued job；active_job一直不超4。实现甲对queued另设名额且先拒收，实现乙仅靠字节配额允许成千上万条排队，二者都可声称采用有限PG队列。后者在有限扫描速度下积压，2h后任务可能从未进入处理就过期；若领取只按反复重试更新的时间，新job还可压过旧job。

最小修复：明确全系统/空间有限待处理条数及其预占/释放、饱和拒绝点、稳定queued领取顺序与过期扫描。名额应在接原件前能够判断或预占；若已受理后才能拒绝，须定义该候选终态与清理责任。维持两个独立gate默认4和原2h，不能把排队时间从deadline中扣掉。

# A04：成员关系终结后的凭证/ACL可在重加入时复活

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:57)，C4；[prd.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:119)、[FR-2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:141)。

原需求明确加入本身不授库权，退出者团队访问与凭证失效。架构当前权限取交集足以阻断“仍不在团队”的阶段；C4安全变更矩阵只列权限/负责人/安全事件，没有规定成员关系终结与团队Bearer、遗留ACL的不可逆联系，凭证seed也只绑定稳定用户/空间/scope。

时序：用户U在团队S拥有库K授权和Bearer-T；退出/移除仅把membership置inactive，T本身仍未撤销、ACL行保留。退出期间所有当前校验均拒绝；U后来以使用者重新接受邀请，membership再次active。若服务端仍按稳定U/S查旧ACL及T，原访问恢复，而没有新逐库授予或新凭证。每次都读取当前DB事实，不能挡这个生命周期反例。实现甲退出时撤销凭证并清ACL，实现乙只做动态交集，行为不同。

最小修复：成员关系终结同事务永久撤销团队凭证并清理/封存旧ACL；或引入membership_generation，让旧凭证和旧授权永不匹配新关系。目标账号及space按既定锁序取得所需EX，接管和安全事件继续同UoW。补退出→重邀→旧Bearer/旧ACL的负例。

# A05：同UoW与action_key没有防止陈旧管理表单覆盖

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:68)，C4；action_key见[C5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:87)；[page-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:201)要求成员/权限同时改变时冲突不覆盖。

反例：所有者O与库负责人M打开相同旧ACL={A,B}。O撤B，提交当前鉴权、space EX、同事务台账均正确。M随后保存旧表单的新集合{A,B,C}，action_key与O不同，M仍有当前管理权；锁会让M在O之后执行，却不能识别B来自陈旧表单。结果B被静默恢复。按同样方式，平台两张配置页可把刚禁用的接入重新保存为旧配置。

现有guard为什么不足：行锁解决同时写入的互斥；action_key及指纹解决同一次动作的重传；二者都不判断一份新动作是不是基于过时状态。没有expected_revision/ETag，也没有将接口强制为不含无意旧值的显式增删操作。

最小修复：替换式ACL/角色/配置写入带expected_revision，以当前revision条件修改并递增；不匹配409，保留输入后重读，不覆盖。若采用细粒度授权变更，须明确请求只描述本次新增/撤销，不能由服务端把旧整表当当前意图。补两位现有合法管理者的交错保存负例。

# A06：跨页spans与逐片段locator的对应关系未定

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:42)，C3；跨页表格要求直接见[implementation-slices.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:81)和[AC-13](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:136)。

已有guard：C3要求跨页/不连续证据多个有序spans，拒假连续范围；PDF页和bbox各自严格验证，source_text片段及hash精确。问题是spans未给出对象schema，而SourceLocator PDF字段physical_page为单页、EvidenceSnapshot也只列一个source_locator，没有规定每个span对应哪个页/区域/资产。

反例：chunk-C的必要表头在第7页，数据在第8页。实见spans保存两个准确的文本范围和正确hash，唯一source_locator={physical_page:7,bbox:表头区域}合法。UI可按C3定位第7页，却无法从DTO知道数据应定位第8页；把locator改第8页又丢表头。实现甲给span另加locator，乙只沿公共字段保存单locator，二者对同样合法输入形成不兼容契约。单有“多个spans”没有排除乙。

最小修复：明确span/原子组结构，将每个实见范围绑定可信source_asset_id和locator，允许有序跨页locator并验证它与文本范围的映射。citation按具体片段定位或明确展示多页。它不要求多取chunk、不扩大K，也不把同一个chunk拆成额外候选。

# A07：图意派生说明缺可交付的来源类型与派生链

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:37)，C3；真实分支为[implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:184)；UX明确区别原件/提取/图意说明见[page-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:168)。

已有guard：图意API通过校核的说明绑定原图和定位后可成为受控块；C3登记original_sha256、source_text_hash、来源kind=pdf/structured，图表另绑定原资产/上下文定位；BudgetSnapshot保留生成用途指纹。这些没有一个字段表示“这段文字是视觉模型派生说明”，也没有将该说明的生成call/profile/校核记录直接绑定至这个来源表示。

反例：原图只画连线，视觉API返回“引脚2与输出节点相连”。实现甲把它追加为该版本source_text并用PDF的original_sha256和页/bbox建立合法定位；实现乙把它存成派生说明资产。两者文本/hash/归属/位置均可合法，但公共证据DTO只看kind=pdf时不能知道甲的excerpt不是原文/OCR摘录，UI无法可靠生成既定“图意说明”标签，随后独立核验也不能按来源记录找到生成该句的具体调用。这里不声称模型一定答错，缺口是来源表示丢失其形成方式。

最小修复：在来源块和EvidenceSnapshot增加有限representation_type，至少区分提取文本、表格表示、图意派生；派生资产不可变，保存原图/裁图hash+可信locator、生成call/profile/处理配置、校核状态及依据指针。模型看到的excerpt仍严格是所存表示的精确片段；用户看到明确派生标签并可回到原图。

# A08：平台接入验证没有统一执行归属

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:65)，C4；调用必需归属见[implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:97)；真实产品动作见[FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:159)和[page-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:211)。

原动作要求验证接入与保存配置分开，平台身份不取得任何库正文。全外传规则则按用户查询当前资格或库任务资格检查，call归属只列operation/job/retrieval execution；没有平台验证上下文、验证配置指纹与结果的条件绑定。R2的阶段重核也只展开用户查询和已受理库任务。P0隔离样例验证不能替代用户日常配置界面的这个行为。

反例：仅平台身份的管理员输入尚未保存的新key/model并点击验证。若实现甲直接调用供应方再把配置状态置“可用”，它无既有三类owner_context/fence，绕开call、共额和未知费用守卫；若实现乙强制创建问答operation，则会要求原本没有的业务空间/库权限，并可能取业务资料作为探测。即使用常量探测，验证A尚未返回时管理员保存B，若成功状态不以待验证指纹条件登记，A的结果可绿标B。

最小修复：给这个已有动作一个有限validation_context，绑定当前平台操作者/epoch/action_key、准确待验证配置指纹、一次或登记有限次数的常量探测、deadline/预算；同样prepared→may_have_sent、账号/用途permit与迟到账。验证成功仅条件更新匹配指纹的状态，不授业务读权，不自动保存或切默认配置。需要P0才可确定的计数/官方动作映射仍维持原停止点。

# A09：私有响应没有覆盖HTTP缓存的交付契约

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:69)，C4；[runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:51)，R4；[implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:399)，§5.5。

已有guard：每次来源/历史/结果请求当前鉴权；账号切换清Pinia/组件缓存、检查回包本地代次；gateway不挂私有原件。这些控制的是到达应用的请求和应用内存，没有私有响应Cache-Control、gateway缓存排除、条件304先鉴权或页面历史恢复的交付规则。

反例：A合法打开受控页图/原件，接口按文件响应提供Last-Modified/ETag但没有显式缓存限制；浏览器可缓存。随后A退出、B登录或A失去该库权限，再访问相同资源URL。若浏览器认为副本新鲜，它不发后端请求，所有后端当前鉴权都没有执行机会；如果应用已发fetch，返回的缓存body仍可带本次请求的新归属上下文，因此本地代次本身也不会识别其旧身份。实现甲私有资源统一no-store，乙只按服务端授权+普通文件响应，两者安全行为不同。另须区分浏览器历史恢复的快照，不把它误当普通fetch。

最小修复：私有API/状态/错误/引用/文件统一Cache-Control:no-store，gateway不缓存这些路由；条件请求如仍提供，先执行当前身份/墓碑检查再决定304。浏览器pagehide/pageshow历史恢复须先隔离原正文、重新核context，不能先恢复私有页面再隐藏。此处不要求追回用户已主动保存到外部的文件。

依据：[MDN Cache-Control](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control)说明未明确约束时可启发式缓存；private仍允许浏览器缓存，no-store禁止私有和共享缓存存储；历史导航又有独立恢复语义。该来源只支持HTTP行为，不证明本项目已有缓存漏洞。

# A10：原件与inline预览没有MIME/主动内容隔离规则

位置：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:127)，C7；[implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:330)，§5.1；同源部署见[C5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:91)。

已有guard：TXT/MD严格UTF-8、本地解析不执行HTML/脚本；模型/Markdown视图清洗；资源必须经受控后端并检查来源/权限；EgressTarget保护服务器出网。没有规定原件返回的Content-Type/Content-Disposition/nosniff、是否允许inline、预览主动内容的CSP/sandbox。解析时不执行不意味着浏览器收到原始字节时不会执行。

反例：合法TXT/MD文件本来就可以包含HTML示例。实现甲原件按attachment、服务器格式白名单和nosniff交付；实现乙为方便预览，按内容探测或透传上游Content-Type，以text/html在应用同源inline返回原始字节。乙可完全经过受控citation ID和当前授权，也没有让解析器执行脚本，却将用户字节交给浏览器作为本应用来源的活动文档。即使没有跨用户猜ID，已授权查看该库的管理者打开该来源也会暴露同源能力。Cookie HttpOnly只阻读取Cookie值，不能阻同源脚本发带Cookie请求。

最小修复：原件下载固定attachment、安全filename和服务器决定的类型，设X-Content-Type-Options:nosniff；inline只开放明确安全的服务器预览表示，HTML/SVG等主动内容要么拒绝inline，要么使用隔离来源及严格sandbox/CSP。不能把上游类型或用户文件名作为inline活动类型许可。补“含HTML的合法TXT/MD”原件响应与来源打开负例。

依据：[MDN Content-Disposition](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition)和[MDN X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options)分别解释attachment/inline及nosniff的浏览器语义；本发现是缺少交付规则，不是声称当前没有代码的项目已经存在XSS。

# A11：辅助历史的授权依赖没有进入每次外传重核集合

位置：[implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:196)，§3.5及[§3.6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:218)；[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:65)，C4；[runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:31)，R2。

已有guard：最多最近两条当前仍有权的用户问题，整条纳入/剔除；不送旧答案/旧证据；请求准入、派发、放行都重核当前用户与全部原显式目标。BudgetSnapshot保存历史实际正文及计数。缺口是没有规定辅助历史的原turn_id/原授权依赖成为新执行的授权依赖，派发矩阵和R2只明列“全部原显式目标”，它们可能与历史来自的库不同。

时序：同空间上一轮在库A提出带敏感背景的用户问题。新一轮显式仅查库B；受理时A/B都可读，取A轮用户问题作为合法辅助历史并固化消息快照。受理后撤销A，B仍合法。接着embedding或生成派发若只按新操作显式目标B检查，其当前用户/scope/fence/预算都通过，已缓存A历史仍外传。实现甲将旧轮次依赖A并入重核集合，乙只在历史选取时鉴权且之后核显式B；现行有限历史和“不用旧答案证据”并未使乙路径必然失效。这个反例只涉及服务端自动读取历史，不能以“用户自己也能重贴已知内容”豁免。

最小修复：执行快照保存history_turn_ids及每条历史的授权依赖集；每次使用/外传时按同一锁序当前重核。失效历史依既定预算规则整条剔除并重新计数，必要指代无法解析则返回澄清/受控失败，不继续发送缓存历史。若选择“所有辅助历史必须属于本次显式范围”，也须写成共享规则并在快照构建时验证，不能由不同入口自行选择。


## 边界路径镜头（2项原始发现）

# edge-case-hunter 独立路径审查

审查输入为本轮 manifest 指定的冻结 snapshot；链接定位 canonical 的同版行。没有应用代码或运行成绩。独立初评阶段未读取旧 IR、旧 reviews、其他镜头输出，也未读取 claims。

## Step 1–2：路径枚举及复查封存

主干、shared-contracts、runtime-operations、technology-evidence、requirements-architecture-traceability、implementation-contract、implementation-slices 均已全文读取；PRD 与 UX 按对应边界回查原文。下表仅记录完成枚举的路径族，不以已覆盖路径充当发现。

| 路径族 | 枚举边界 |
| --- | --- |
| 上传与版本 | 未 PUT、开始、半传、重复带体、完成与到期竞争、候选新旧、首次 partial、完整替换、墓碑、发布、清理 |
| job 与远端任务 | queued/active、submit/HTTP accepted、pending/unknown、poll/reconciliation、终态、到期、本地继续、重启与恢复 |
| gate 与调度 | 两个全系统 gate 各 4、本机重阶段 1、账号/用途池、按维度领还、满池 poll、公平轮转、配置改变、迟发 grant |
| 授权与外传 | 账号/空间 SH、变更 EX、锁集合与顺序、派发前与放行前重核、撤权晚于 grant、读写身份、未登录入口 |
| 三账与恢复 | 原件预留/实占/cleaned、原受理日产品计次、逐 call 成本、迟到事实、冲突事实、旧包低计数与独立 epoch |
| 检索与历史 | 多库兼容、版本/代次固定、重建与删除、K=5、实见 spans、历史证据 GC、来源当前读取 |
| 输入与配置 | H/B/M、码点/字节、完整输出预算、有限值、配置版本、热变、旧 Key/异输入/TTL/墓碑、会话父轮次 |

复查再次遍历上述状态转换与隐式分支后保留以下两条候选。Step 1–2 在读取 claims 前完成。Step 3：本次为完整文档而非 diff，删除检查跳过。

### 窗口释放后仍可消费旧 grant

定位：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:139)，关联 [runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:19) 与 [implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:101)。

精确反例：已核账号 RPS 为滚动 1 秒内 1 次、HTTP 并发至少 2。两个不同用户各持一个合法 API 查询物理槽。call A 在 t=0 的 may_have_sent UoW 领取 RPS、HTTP 组件并得到一次 grant；child 被调度暂停，尚未发送。t=1.1，该旧窗口按 DB 时间自然到期，call B 合法领取新窗口额度并发送。t=1.2，A 恢复并消费原 grant。两次发送都未过各自绝对 deadline、都只发送一次，账号却在同一实际 1 秒窗口收到两次请求。TPM 有同构路径。

现有 guard 为 may_have_sent 时原子领组件、滑窗保守实现、窗口自然到期；仅远端并发的终态上界明确要求覆盖最晚可能到达时刻。一次 grant 与 120 秒级 child deadline 没有将窗口占用延长至其仍可能发送的期间，也没有定义窗口过期后旧 grant 如何失效。这里不依赖撤权、盲重试、多个进程各自计额或上游未核额度。声明可能遭遇厂商 429 不会补上本项目自身迟发许可造成的超配路径。

实际后果：共享池已允许的新调用与迟发旧调用聚集，触发本可避免的供应方限流及已受理业务失败。

最小修复：将窗口到期证明与该 call 的最晚可能到达界绑定；无法证明旧 grant 已不能再发或请求已进入正确窗口时，不回收其 RPS/TPM 占用。若采用有限 send-by，须同时定义超期 grant 丢弃及到达界，不复发原 call。S0 加入暂停 child 跨窗口、其他槽继续派发的确定性负例。

### 首次登录没有会话绑定 CSRF 的可达前置

定位：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:91)，关联 [implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:312)、[page-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:28) 与 [acceptance.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:28)。

精确反例：有效账号在全新浏览器首次打开登录页，没有本应用登录 Cookie 或会话绑定 CSRF token。登录是 Web 写动作；C5 要求所有 Web 写动作同时通过 Origin 和会话绑定 CSRF token，但同段仅在登录成功后创建/旋转认证会话，输入包没有匿名会话或登录前 token 的签发/校验入口。UX 正例要求从未登录状态仅填账号密码可达成功。

现有 guard 没有区分未登录的登录 POST 与已有会话写动作。Origin 允许表只是并列条件，不会生成缺少的会话绑定 token；登录成功换会话也发生在该检查之后。所有 snapshot 中 CSRF/匿名/登录前分支已检索复查，未发现 bootstrap 或明确的登录专用规则。

实际后果：按统一守卫实施会拒绝首次登录；若实现者自行跳过全部登录防护，则安全边界由各自猜测产生分叉。

最小修复：明确登录前短寿命匿名 CSRF 上下文的取得、绑定和校验，登录成功销毁并旋转；或者明确登录专用的已选防护规则。已有认证会话的写动作继续用会话绑定 token。S1 覆盖无 Cookie 首次登录及伪造跨站登录两个分支。

## Step 4：claims

Step 1–2 上文落盘后才首次读取 claims。逐项按已追踪的切片前置、两个全局 gate、重阶段、poll、unknown、唯一领还、恢复与运行停止门进行证伪；没有额外的独立 claim finding。完整性叙述与上文反例的关系不重复计项。

封存：仅输出上文两条未处理分支，不读取同伴结果，不修改方案。


## 结构镜头（4项建议）

本架构包用于帮助实际实现团队在不重开产品决定的前提下，找到当前权威契约、按切片开工，并准确执行共享边界与停止条件。

结构模型：主干按Explanation（由概念到实现），共享/运行契约与追踪按Reference/Database（可随机查找、职责互斥、稳定模式）校准；读者为humans，风格为Microsoft Writing Style Guide。

| Pass | Original Text | Revised Text | Changes |
| --- | --- | --- | --- |
| structure | [架构主干](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:23)开头只有业务/UX来源与companion文件名；完整AD/C/R职责导航在[需求追踪§1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md:5)（232词），切片到强制条款的入口在[§6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md:142)。 | MOVE 将§1权威输入与承接索引移到主干目的之后、概念总览之前，并把现有切片门槛链接直接定位到§6；追踪矩阵保留回指。 | 触发：实现者第一次按S0或单一AD开工。现有companion清单没有说明去哪里查当前切片的完整C/R约束，AD14到主干后段才指向追踪；读者需自行拼接阅读路径，容易把摘要Rule作为完整契约。前移现有导航可先交代权威/查找方式，再进入八模块与依赖图。字数影响：移动232词，净减约0。 |
| structure | 完整PG锁序同时展开于[架构主干AD3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:71)（248词）、[运行契约R3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:47)（350词）、[实施契约§2.6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:113)，范围：113–115（377词）；[共享契约C4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:55)另有完整规范。 | MERGE 完整序列及其当前授权/后台任务例外收口到C4；其余三处保留用例事务、OS停写和清理语境，用定点链接引用C4/C8，不再逐项复制序列。 | 触发：后续增加锁类别或调整许可释放流程。虽然各处已链接C4，正文仍各自给出可直接实现的完整顺序；引用不能同步复制的列表，维护者需人工改四份，遗漏一处即可让不同模块依不同段落取锁。保留摘要与局部操作目的，集中机械序列即可消除平行维护面，不改变锁、权限或执行行为。字数影响：三处原975词，最小示意替换合计417词，预计净减558词。 |
| structure | [需求追踪§7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md:161)，范围：161–163（540词），混排B/A互审、B3/H1/H2修复过程、旧结论关闭及当前并发规则。 | MOVE 将两段修复沿革移入已有审查gate记录的历史部分；当前追踪只保留现行覆盖结论、未取得证据和历史入口链接，现行并发规则继续由实施契约/C8/R1承载。 | 触发：下一位实现者或维护者确认当前约束与未证门槛。§7同时承载现行摘要与按轮次叙述的修复史，且把“当前权威结论”再导向审查签署；即使已声明规划不等于实测，读者仍需筛掉已关闭反例并逐段区分规则与形成过程。历史完整保留在审查记录，可让实施包按当前状态收束。字数影响：移动540词，资料总量净减约0。 |
| structure | [技术证据E4末段](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:61)（185词）重述两项全系统gate、本机槽、等待资源、调度及P0/S6验收要求。 | CONDENSE 保留“用户授权的未测seed，不证明账号或4GB已通过”这一证据状态；完整并发取值/生命周期、调度与门槛改为引用实施契约§2.6、C8及R1/R6。 | 触发：并发配置、调度或验收步骤再次变化。该段没有新增官方证据，却在证据目录内维护一份完整动作契约；其链接和“未测”声明不能避免行为段落日后滞后，接入者仍须比较两份文字。凝缩后技术证据页负责来源与适用限度，规则继续从原权威位置读取，保留两个gate各默认4/范围1–4与本机重阶段1的既定行为。字数影响：185词改为56词示意引用，预计净减129词。 |

共4项建议：2项移动、1项合并、1项凝缩。按word_metrics实测，7份完整输入共57,396词；若采纳示意改法，预计净减687词（1.20%），另移动772词而不丢失资料。未给长度目标。计数采用脚本的CJK逐字符加空白token口径；改写节省为示意稿估计。保留模块概览/依赖图、Stack概览和按FR/IA/AC分组的追踪入口：它们分别服务心智模型、快速查表与不同检索入口，重复有理解价值。代价是机械规则需跳转一次，以定点链接补偿；不建议削减任何行为、权限、并发4、验收门或已明确责任/停止点的未执行证据。


## 两位Winston的最终处置

# Winston A 交叉质询处置

独立初评保留在[adversarial.json](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/findings/adversarial.json)及[adversarial.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/findings/adversarial.md)，没有覆盖。初评封存后才读B的[独立报告](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/findings/edge-case-hunter.md)。以下是A依据冻结条文重新裁定的建议，根代理保留IR裁决权。未改设计或快照；没有安装、收费调用、部署或虚构成绩。

| 候选 | 处置 | 条文与处置依据 |
| --- | --- | --- |
| A01 | accepted；与B01合并 | [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:139)让窗口自然到期，[R2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:29)允许提交后给grant；未给“尚能发送的旧grant”覆盖窗口规则。1秒RPS、两合法传输槽的迟发反例仍可复现。 |
| A02 | clarification-only | [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)已有现行有限gate、唯一领还与真实占用规则；[R6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:93)要求生效配置。没有承诺在线热改gate，S0可关闭新增受理后激活，不能把热更新假设当确定缺陷。 |
| A03 | clarification-only | [R1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:17)已经强制有限PG队列、公平轮转和原2h期限；具体队列条数/预占点可由S0确定。初评新增空间份额不应自动变产品要求。 |
| A04 | rebutted | [PRD119](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:119)明定加入本身不授库权，[PRD141](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:141)明定退出凭证失效。初评只做交集后让旧凭证复活的实现违反父规则，不是两种均合规实现。 |
| A05 | rebutted | [UX201](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:201)已经规定冲突不覆盖；expected_revision或差量动作是实现选择，初评的静默覆盖实现违反既定UX。 |
| A06 | clarification-only | [C3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:42)已要求可信定位、跨页多个spans；[S5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:81)要求跨页核验。逐span locator值得明确，但单页指针丢另一页不是可合规行为；尚无证据需新业务规则。 |
| A07 | clarification-only | [实施契约184](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:184)强制说明绑定原图定位，[UX168](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:168)强制原件/提取/图意标签。representation字段可由同一contracts所有者补全；不把初评全部call/profile派生字段提升新需求。 |
| A08 | clarification-only | [PRD159](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:159)已要求接入验证且禁止平台读正文；[实施契约97](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:97)允许job归属，[C4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:53)用泛型owner_context_id且guard适用时才加。平台验证job可以承接，不坚持必须新增实体。 |
| A09 | accepted，收窄为HTTP交付 | [C4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:69)的后端重核、[§5.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:399)的Pinia/组件清理没有规定原生HTTP缓存交付。缓存直接命中不会到后端，且缓存body可被本次新请求上下文接收。 |
| A10 | accepted，收窄为原始资源交付 | [C7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:127)的解析不执行HTML和[§5.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:403)的Markdown清洗没有约束原字节响应的媒体类型与inline处理。 |
| A11 | rebutted | [PRD277](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:277)明定历史消息不能绕授权进入生成；[实施契约196](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:196)只取当前仍有权的问题。初评失权仍外传违反已有行为，不能仅因授权依赖字段没重复列出算新缺陷。 |
| B01 | accepted；重复A01 | 独立复现相同窗口/迟发反例；保留两镜初评，IR只计一个缺口。 |
| B02 | accepted | [C5第91行](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:91)要求所有Web写同时校验Origin和会话绑定token；[AC01](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:28)要求未登录可密码登录。没有选定登录前绑定上下文或登录专用例外，出现具体前置循环。 |

## 保留缺口的最小方案与关闭条件

A01/B01：用RPS=1/s、HTTP并发≥2、两个合法查询槽；A在t=0领组件后暂停，B在t=1.1自然到期后领取并发送，A在t=1.2消费旧grant。两次均在原deadline内、均只发一次。最小补充是旧grant仍有未来本地发送能力时，其窗口占用不得已过期；从可信保守的最后可能本地发送时刻至少保留该维完整窗口。若采用send-by，必须有受监督停发/停止证据，不能只在可能再次暂停的child中读一次时钟。适用官方窗口若按接收计时，有已证到达界才用该界补充保守核算；不要将所有网络到达绝对上界普遍新增成RPS能力门，也不承诺厂商永不429。原call不重发；是否可新建调用仍受原业务、费用和unknown规则，不能盲重交解析。关闭条件：共享契约明确计时基点、live grant、消费/丢弃与窗口释放的关系，并将暂停child跨窗口且另一槽推进写入S0确定性负例。

A09：私有API/错误/状态/引用/页图/原件的HTTP响应由API和gateway共同执行no-store及禁缓存；如果仍实现条件响应，必须先当前授权再304。浏览器历史快照是另一层，不能拿no-store宣称已清bfcache；现有后台回前台重核context应明确涵盖历史恢复前遮蔽私有正文。关闭条件：公共HTTP与gateway规则及S1/S2跨账号/撤权缓存命中、条件请求、历史恢复验收要求都落在相应所有者，不能只在前端组件加清缓存代码。

此项不要求追回用户已经合法显示或主动保存的文件；也不要求将所有浏览器bfcache一概禁止。目标是应用控制的后续私有读取和页面恢复不在新身份下直接呈现旧缓存正文。

HTTP事实依据为[持久缓存标准RFC9111](https://www.rfc-editor.org/rfc/rfc9111.html)：§4.2.2允许一定条件下启发式新鲜度；§5.2.2.5约束私有/共享缓存存储和复用；§6区分历史机制。本建议不声称已运行浏览器或当前项目已发生泄漏。

A10：原件按服务器格式白名单返回准确类型、attachment、安全filename和nosniff；可信预览与原件下载使用明确不同的交付规则，禁止将用户/上游指定的HTML等主动类型作为本应用同源inline。nosniff不能将已声明text/html变安全，必须同时限制类型/inline；若确有主动内容预览才选择隔离来源或严格sandbox，首版无需新增该产品能力。关闭条件：受控资源合同明定上述规则，并要求合法TXT/MD含HTML示例的响应及来源打开负例；解析不执行、Markdown清洗、后端鉴权各自继续保留。

此项仅认定规划缺少交付规则；项目尚无应用代码，没有证实任何运行中的XSS。

类型处理依据：[RFC6266 §4.2](https://www.rfc-editor.org/rfc/rfc6266.html#section-4.2)规定attachment和inline处理区别；[WHATWG MIME Sniffing](https://mimesniff.spec.whatwg.org/)规定类型计算及脚本类型安全边界。标准只证明原字节交付与本地解析是不同层，不证明具体浏览器在任何Content-Type下都会执行脚本。

B02：最小技术方案选择登录专用规则，无须新增匿名状态GET：未认证登录POST不要求尚不存在的认证会话token，仍强制精确同源Origin（缺失/null/跨源拒绝）、application/json及有限固定自定义header，CORS保持关闭，拒简单form类型；登录成功生成/旋转认证会话与新CSRF token。已有会话的其他Web写动作仍用会话绑定token。选择该方案的目的只是消除现行具体守卫循环，不放宽一般写防护。

[OWASP官方CSRF指南](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)的Login Forms、Disallow simple content types、Custom Request Headers与Origin各节支持登录也需防护，以及明确选用上述防护构件。关闭条件：C5与登录接口共同写明例外及成功旋转，S1要求覆盖全新无Cookie浏览器的合法登录、缺/错Origin、跨源和form提交。无需当前没有代码时实跑或安装框架来关闭本轮规划缺口。

## 澄清项的实施关闭条件

- A02：S0记录离线激活或在线激活方式。选择在线时，现行limit与真实active/债务一致且不重写已取得组件；选择关闭新增受理后激活同样可。不得只改计数以满足新上限。
- A03：S0把既有“有限PG队列”落实为有限配置、饱和行为、稳定领取与过期扫描fixture；不强加每空间公平份额，2h含排队仍成立。
- A06：同一contracts所有者定义逐span locator或等价多页映射正负样例，覆盖第7页表头/第8页数据，可逐片核验，K仍≤5。
- A07：DTO至少有可靠的原件/提取/图意说明表示区分，满足UX标签并可回到绑定原图；处理指纹和调用关系用现有资产/job体系落实，不强制另造派生实体。
- A08：S0将无业务KB的有限平台验证job纳入统一执行/共额/逐call账，当前平台资格及准确配置指纹须条件关联；使用常量探测，不能读取业务正文。允许用现有job，不要求新validation_context实体。

真正未决项为根IR对A01/B01、A09、A10、B02是否接受及要求写入哪些现行契约的裁决；本轮不直接修设计。没有需要用户另选产品范围、角色、并发方向或付费方案的人类决策。


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
