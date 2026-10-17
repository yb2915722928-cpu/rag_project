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
