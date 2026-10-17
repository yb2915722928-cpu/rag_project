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
