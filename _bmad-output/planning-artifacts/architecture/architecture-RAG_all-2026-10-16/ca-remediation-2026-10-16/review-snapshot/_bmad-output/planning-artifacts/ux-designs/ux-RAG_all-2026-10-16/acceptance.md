# RAG_all — UX 交付验收与实现验收契约

状态：ready-for-handoff；更新：2026-10-16。设计规则已收敛，**下列产品运行用例全部未执行**；不填写虚构的通过率、费用、P95、真实接入或部署成绩。

权威输入：[PRD FR/SM](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:123)、[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:10)、[实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:9)。设计入口：[EXPERIENCE](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md)、[逐页交互契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md)、[视觉规范](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md)。

## 两类验收的不同证据

| 层级 | 检查什么/需要什么证据 | 可以据此说什么 |
| --- | --- | --- |
| D：设计交付 | 文档/参考图逐项核对业务不变量、12 IA字段及状态、视觉tokens、组件、四场景、正负用例与来源映射；本轮由两位Sally互相核对 | 设计足以交给Winston/Amelia；所有设计规则有出处或本轮委托决定。不能说产品通过SM/P0/部署验收 |
| R：实现与运行 | 真实API/Web、数据库状态/安全台账、真实供应方调用、受控故障注入、目标机及冻结评估数据；每用例记录输入、前置、操作、可见结果、后端副作用与原始证据 | 对应切片完成且有运行证据后才判定通过；mock/API假件只证明其测试范围，不能替代外部接入/资源/恢复/语义质量 |

D层交付逐项：D-01 来源及业务规则可追踪；D-02 12 IA有字段初态/校验/动作/权限/错误恢复；D-03 两主文档tokens/组件同名、断点/状态文字一致；D-04 每原场景有原主角/编号步骤/高潮/失败路径；D-05 四关键屏参考与其余表面组件规则覆盖；D-06 下列AC有正反用例、上游/切片对应。设计核对由交接记录列实际发现与修复，不能把“有表格”写成可用性实测通过。

## 运行用例共同执行约定

- 准备个人P、团队A/B、平台身份、所有者、维护者、使用者，至少两库与多文档、已知可答/不足/冲突资料。四场景样例用上游原人物；支持流程人物仅帮助走查，不新增权限角色。
- 每组用例同时观察页面和服务器响应/副作用；禁止只看按钮隐藏证明鉴权。未知/不存在目标取等价响应，不以响应中漏掉目标或返回部分内容视为通过。
- “Then”均为实现必须达到的结果。运行记录的默认状态是**未执行**；失败保留原结果、实际调用与未知成本，不重复执行到成功后删掉失败。
- 资料正文/秘密不得进入公开测试报告；凭证/调用/审计证据使用必要脱敏标识，仍保留可核对关联。
- 完整S7仍须原32题/五类专项/独立权限专项，以下用例只是UI与契约的可执行入口，不缩减原验收分母。

## AC-01 — 身份入口与本人账户

映射：IA-01；FR-1/4/5；SM-6/7；S1。依据：[账号与认证](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:159)、[双渠道边界](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:16)。

- **正例：** Given有效账号且全新浏览器无Cookie／无会话CSRF token，When以精确部署scheme／host／port的同源Origin、application/json与X-RAG-Login: 1提交匿名登录，Then可完成首次登录，不被会话token前置阻断；成功旋转会话／绑定CSRF token，经不缓存受控响应交前端内存，先取本人context再加载授权页面；重载后可经同源当前认证的no-store context GET取本会话token，不放URL或持久缓存。再以同源Origin＋会话绑定token修改本人密码，明确成功后清秘密字段，旧会话行为按当前服务端状态；无自助注册／代登录入口。
- **反例：** Given匿名登录缺Origin、Origin为null／cross-origin（含部署scheme／host／port任一不符）、简单form／非JSON或缺固定登录头，When提交，Then403拒绝且CORS关闭，不创建会话／不返回受保护正文；既有认证Web写缺／错会话token或非同源Origin也拒绝。停用／未核验身份、受保护请求同时含本应用Cookie和Bearer，仍按原安全错误整拒，不回退另一凭据；密码错误／断网不冒充账号不存在或改密成功，丢回包不自动再次改密。

证据：全新无Cookie正例及各Origin／form／header负例原始请求响应、会话旋转与绑定token事实（报告脱敏）、认证写token正反例、no-store／CORS配置、前端内存与秘密清除、无越权读写记录。技术真源：[C5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:79)；状态：未执行。

## AC-02 — 邀请、加入、退出与所有权

映射：IA-02/11/12；FR-1/2；SM-6/7；S1。依据：[FR-2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:133)，范围：133–141。

- **正例：** Given所有者邀请已有有效账号并指定使用者角色，When目标接受，Then才成为成员，初态无逐库授权；后续转让给已有有效成员，旧所有者变维护者且仅保留原逐库/负责库范围；退出时负责职责由所有者接管，资料保留。
- **反例：** Given邀请未接受/已撤销，When访问团队，Then不能进入；Given所有者尚未交接，When退出/停用，Then拒绝且给交接入口/说明；Given维护者/使用者，When直接请求成员管理或普通建团队，Then拒绝。回包丢失先核实际成员状态，不生成重复邀请/转让。

证据：成员/角色/负责人前后事实、邀请状态、转让/退出事务结果及旧身份重读反例。

## AC-03 — 团队角色与逐库范围分离

映射：IA-02/03/04/07/08/11；FR-1/3/5/9/14；SM-6/7；S1→S3。依据：[角色与范围](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:111)，范围：111–119、143–153。

- **正例：** Given同账号在A为维护者、B为使用者，When分别进入两团队的授权库，ThenA按维护范围操作全部资料，B仅读/反馈；个人空间仅本人可见。创建库的所有者/维护者自动成为负责人。
- **反例：** Given未授权库或混合合法+非法目标，When目录深链/检索/问答/比较/来源/下载，Then整体拒绝且无部分结果；无权和不存在对外不泄露名称/数量/存在性。给使用者库授权不提升维护角色，同团队所有者/平台身份不能读他人个人资料。

证据：分账号/团队的可见目录与直接接口结果、整拒外发次数为零、资源边界响应。

## AC-04 — 负责人职责、撤权与降级

映射：IA-03/04/06/11；FR-2/3/15；SM-6/7；S1→S2。依据：[负责人接管](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:147)，范围：147–153；[任务归库](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:115)。

- **正例：** Given维护者能维护非负责授权库且有已合法受理任务，When被降为使用者但保留该库读权，Then失去维护/授权管理，仍可读本人受控任务状态；库任务不因提交者降级自动取消，当前维护者可管。
- **反例：** Given非负责库维护者，When尝试管理库授权/删整库，Then拒绝；Given所有者撤负责人该库访问，Then所有者同步接管且清该成员该库全部授权，原创建者不能恢复；撤库权/退出者不可看本人旧任务，降级者不可读他人私有任务/候选管理产物。所有者固有全库权不通过单库撤销。

证据：负责人/授权前后状态、直接管理接口反例、任务继续及受控读取结果。

## AC-05 — 平台权限与业务资料隔离

映射：IA-03/12；FR-1/4/5/16；SM-6/7；S1、S6。依据：[平台隔离](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:157)，范围：157–161。

- **正例：** Given仅平台身份，When配置账号/团队初始所有者、接入、配额并查看必要运行元数据，Then显示相应平台事实，建团队恰一有效所有者，已建团队所有者变更只能选本团队已加入且有效成员；兼具业务身份时另按该身份当前范围进业务库。
- **反例：** Given仅平台身份，When请求业务正文/他人会话/全局业务搜索/库重建写动作，Then拒绝且不加载正文预览；运行/审计不泄露原文、秘密、供应方临时URL，办理所有者变更不增加资料权。

证据：平台入口及直接接口返回、日志/审计脱敏、兼身份分权反例。

## AC-06 — 批量导入、容量与受理

映射：IA-04/05/10/12；FR-4/6/15；SM-5/6/7；S2。依据：[原件容量](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:167)、[FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:193)。

- **正例：** Given当前合法有限限制及足够容量，When批量提交一合规文件和一明确坏/加密/超限文件，Then逐文件给受理/拒绝及原因，合规项有独立operation/candidate/version、原期限；一项拒绝不回滚他项，上传完成不等于资料就绪。
- **反例：** Given满额或替换需双份预算，When提交替换，Then不先抵扣旧版/删旧版、不超额预留；限制未知不能按无限受理。保留历史/失败候选/清理中原件继续计容量；同内容不同版本分别计。文件名/标题不可冒充来源版本身份。

证据：生效配置、逐文件候选与容量预留账、格式错误、无越限任务/外发事实。

## AC-07 — 上传中断、放弃、期限与清理

映射：IA-04/05；FR-4/6/8/15；SM-6/7；S2。依据：[上传寿命与动作](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:75)，范围：75–83、312–320。

- **正例：** Given尚未PUT/半传的有效候选，When断网再恢复读取原候选或同输入重传，Then相同candidate/version/预留与原deadline；显式放弃条件终结写意图，旧生效版不受影响，显示真实清理状态。
- **反例：** Given同ID异内容/实际hash或长度不符、上传到期、旧writer迟到，When继续上传，Then不新建任务/预留、不覆盖/复活候选；原件/临时资产未真实清完或写入者未停止不得报容量已释放。失败候选供合法校核时保留，不因操作窗口结束自动删成功历史。

证据：原ID/期限/字节hash前后、状态与写入者fence、资产/容量清理记录；页面“清理失败”持续可见。

## AC-08 — 生效版、候选、任务及自动发布

映射：IA-04/05/06；FR-6/7/8/14/15；SM-5/6/7；S2最小→S5复杂。依据：[UI动作状态表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:23)。

- **正例：** Given首次完整文档完成程序校核，Then自动发布且无逐份批准；Given首次partial只可靠范围通过，Then持续显不完整/失败范围并仅查询通过范围；Givenv1生效且v2候选处理中，Then三对象独立呈现且v1仍查得到。
- **反例：** Given替换候选partial/失败或缺必需来源定位/向量，When任务结束，Then不盖旧生效版、不标完整ready；候选不进入查询，迟到旧候选不覆盖新候选；人可读业务版本未标注时显示“未标注”，不得以技术version_id推断产品适用版本。对照修正必须新候选/合法attempt，不能原地改历史。

证据：三栏截图、活动指针/候选/任务事实、新旧查询及历史引用结果；程序校核通过不当人工语义正确证明。

## AC-09 — 外部未知、继续核对与继续本地处理

映射：IA-04/06/10；FR-4/6/15；SM-6/7；S2。依据：[有界核对/本地继续](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:123)，范围：123–133。

- **正例：** Given原任务外部结果未知且业务已到期，When当前维护者显式“继续核对原任务”，Then新有界只读核对仅查持久已知原任务，ready仅为观测；若本人再显式“继续本地处理”，Then新本地job/attempt/deadline重新核权/guard/预算/资产，不自动重交上游。
- **反例：** Given只读状态GET/程序凭证、已无维护权或未知上游ID，When读取/核对，Then不隐式新建核对、不猜ID/换供应方账号、不下载发布/续原job；重新提交解析须勾选默认未选的“我已知悉可能重复调用与费用”，勾选且资格合法后“确认并重新提交解析”才启用，未确认不外发，重交后不删原关联。继续本地处理不等于已验证可复用资产。

证据：action_key/reconciliation/job/call关联、外发清单、原截止不变、未知费用、ready未发布/未下载反例。

## AC-10 — 校核/来源对照与最小回看

映射：IA-06/09；FR-6/7/8/13；SM-2/3/5/7；S2最小→S5复杂。依据：[FR-7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:205)，范围：205–213。

- **正例：** GivenPDF可信bbox、PDF仅可靠页、DOCX／TXT／MD实际结构样例，When打开校核／引用，Then在服务器生成并校验的PNG／JPEG页图上高亮真实区域或展示可靠物理页＋“无区域高亮”；非PDF为结构路径＋准确片段＋授权原件attachment下载。PDF物理页从1起，原件／提取身份清楚；原件响应的安全Content-Disposition含服务端fallback及UTF-8 filename*、准确白名单MIME及nosniff，PDF为application/pdf、DOCX为application/vnd.openxmlformats-officedocument.wordprocessingml.document、TXT为text/plain;charset=utf-8、MD为text/markdown;charset=utf-8。
- **反例：** Given合法TXT／MD包含HTML／脚本、伪扩展／伪MIME文件、含CRLF／路径／控制字符／超长名的恶意filename，When读取／下载／预览，Then文本／MD／提取JSON仅textContent或清洗渲染，原件不inline、头不注入、文件名有界，不透传上游类型／header；HTML／SVG／上游PDF等主动文档不inline、不执行脚本。坏locator／hash不符／缺资产或无必需定位候选明确不可用，不猜首页／坐标、不编DOCX物理页、不假ready；当前有权且原件存在可单独下载。无OCR编辑器／Word服务或新主动预览能力。

证据：原件hash／定位元数据、四类准确响应头与恶意filename结果、含HTML的合法TXT／MD和伪类型样本、真实浏览器无执行／无主动文档inline、PDF／非PDF对照及故障响应。逐一核资源与错误的no-store、If-*仍授权、无304及同URL换账号／撤权／history恢复（见AC-18）；S2资源开放前须通过，不能等S5才交付。真源：[C7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:117)；状态：未执行。

## AC-11 — SC-1：技术支持与故障排查

映射：IA-07/09；原主角技术支持小林；FR-9/10/14；SM-1–4/6/7；S4。依据：[SC-1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:64)、[FR-10](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:241)。

- **正例：** Given小林选授权库并提供v2升级连接超时日志/环境，When提交完整问答，Then答案保留适用条件、候选原因、顺序检查及逐步可核验版本引用；小林可把首项检查同日志现象/原文对齐。
- **反例：** Given缺版本/环境或来源版本不匹配，When提交，Then先澄清/限定，不定根因、不推荐无条件步骤；不执行命令或声称修复完成，不为预算删日志。依赖/预算失败按失败而非正常不足。

证据：原始输入/完整结果/引用打开、必要事实人工核验、澄清与执行失败分离；不以漂亮答案替代SM评估。

## AC-12 — SC-2：企业内部知识查询

映射：IA-07/09；原主角新员工小周；FR-9/11/14；SM-1–4/6/7；S3。依据：[SC-2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:65)、[FR-11](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:247)。

- **正例：** Given小周已获制度库权，When询问出差审批人/流程/材料，Then完整答案列有据流程/材料、制度版本/适用条件与引用；模拟/脱敏样例身份清晰。
- **反例：** Given资料没负责人或同条件制度冲突，When回答，Then明确负责人缺失或并列双方版本/证据，不虚构姓名、不擅定哪份有效；未请求的流程/材料/条件/负责人分组不强填，默认enterprise不扩成generic或任意第五类事实；仅入队无库权不能查询全部团队资料。

证据：原答案/双方来源/人工语义核验、无权场景及零候选边界。

## AC-13 — SC-4：复杂产品手册问答

映射：IA-07/09；原主角实施工程师小赵；FR-7/9/13/14；SM-1–7；S5。依据：[SC-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:67)、[FR-13](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:263)。

- **正例：** GivenM2/E17手册含正文、规则/简单跨页表格、扫描页和真正依赖图意的事实，When小赵查询故障/位置/参数，Then保留型号/版本/数值/单位/表头条件并可核对表/图/物理页；图意用可读说明加图号/条件，不能只贴图片。
- **反例：** Given型号不明/单位缺失/解析范围不足或不兼容型号片段，When回答，Then澄清/限定、不拼参数、不捏造图意；纯文本题通过不证明SC-4完成，图意失败不得靠其他场景平均分抵消。

证据：原页/表/图/扫描、冻结必要事实、人工核对与失败结果；图意/模型实际能力由P0验证。

## AC-14 — SC-3：完整四态比较

映射：IA-08/09；原主角售前小陈；FR-9/12/14；SM-1–7；S4。依据：[SC-3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:66)、[比较结构/四态](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:9)。

- **正例：** GivenA/B当前可查询文档和离线/审计/批量导入条件，When小陈开始对比，Then固定每文档受理版本，按输入顺序显示完整对象×条件格，每格四态文字/理由/证据。满足/明确不满足有直接证据，不足说明缺口，冲突是该对象固定版本内互斥双方证据。
- **反例：** Given空/重复/超限条件或对象、历史替换版/越权目标，When提交，Then外发前整拒不裁格；Given缺格/截断/非法ID/冲突缺边/理由超compact128，Then整答失败不展示草稿/不追加LLM修复。A满足B不满足不误标同格冲突，未找到不标明确不满足。

证据：输入规范化/有效限制/完整矩阵/固定版本/实际evidence_catalog≤5；每格人工语义核验，结构通过不能代替SM-1/3。

## AC-15 — 查询结果、计次、零候选与网络恢复

映射：IA-07/08/10；FR-4/5/9/12/14/15；SM-4/6/7；S3→S4。依据：[三账及幂等](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:28)、[前端恢复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:403)。

- **正例：** Given执行成功但回包丢失/跨上海午夜，When按原Key或原operation恢复，Then原结果/原完成时间/版本、只追加一次轮次/只按原日计一次，不新检索生成。真正检索成功零候选可跳LLM，问答正常不足/比较全格不足仍计一次；纯检索/引用/任务状态不扣问答。
- **反例：** Given202/断网/Abort，Then不能自动新Key或宣称取消/退款；同Key异输入冲突、failed同Key只回原失败、expired不执行。预算裁空/未证模型预算且非零候选/截断/依赖失败/输出前撤权不伪装不足，按契约一次释放问答预留，真实已花embedding/调用保留且未知费用不为0。显示“发起新请求”必须本人显式选择。

证据：operation/Key/快照/日桶/预留结算、原始HTTP与外发call、丢回包故障；实际调用费和问答次数分开报告。

## AC-16 — 历史、切版、删除与当前重授权

映射：IA-04/07/08/09；FR-3/5/8/9/14；SM-3/6/7；S2→S3。依据：[版本/删除](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:215)，范围：215–223；[历史引用](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:40)。

- **正例：** Givenv1已答并替换成v2，When回看历史引用，Then仍核验不可变v1来源、标历史版本；新查询只用v2。旧向量回收不破坏已保留来源/证据快照；来源返回保留原格/引用位置。
- **反例：** Given撤库权/移除/停用/删除/团队解散发生在历史读取、引用下载或答案输出前，When访问，Then复核并隐藏整个受影响答案/矩阵，不用旧缓存兜底。删除先阻断访问再清理，清理失败不复活；历史旧证据不自动加入新追问上下文，已合法显示/下载内容不追溯回收。

证据：历史版本/hash映射、删除墓碑与输出前竞态、直接原件/页图/引用接口结果。

## AC-17 — 同维重建、写guard与删除竞态

映射：IA-04/12；FR-4/8/15；SM-6/7；S6。依据：[重建守卫](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:138)，范围：138–155。

- **正例：** Given当前库维护者且无有效未终结写意图，When显式同维重建，Then显示旧活动generation/目标profile/当前guard，旧索引可查询；失败/取消/过期释放本attempt的guard，合法写入口随后可用。
- **反例：** Given候选/在途上传/待核对等仍有执行资格的写意图，When重建，Then整拒不悬空锁；guard中上传/替换/重处理整拒且不预留/暗排队，但显式删除仍先墓碑并使候选失效。旧attempt不能解新guard；revision/版本集变化或不完整不能发布；跨库profile不兼容整拒；变维不假称在线切换/前端倒计时放行。

证据：真实PG并发/guard归属/活动指针与revision、界面限制及删除后查询；仅页面锁按钮不算竞态通过。

## AC-18 — 响应归属、离线、多标签页与会话串行

映射：IA-01–12；FR-1/3/4/5/9/14/15；SM-6/7；S1基础→S3联调。依据：[前端响应归属](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:403)。

- **正例：** Given原上下文仍合法，When重连／后台回前台／前进后退或pageshow（含bfcache／history restore），Then先遮蔽私有区、清旧context并变更本地代次；受控核当前context／epoch及欲显示内容的全部依赖后才恢复原状态／结果，pagehide已隐藏清私有DOM。所有私有HTTP响应含成功、认证、错误、context／状态、citation／页图／原件、答案／历史及程序入口均Cache-Control:no-store，网关proxy_cache off／proxy_no_cache 1／proxy_cache_bypass 1且不覆盖，前端无持久私有缓存。单会话忙时下一生成禁发；父轮次冲突保留输入、重取历史，用户核对后才明确提交。
- **反例：** Given真实浏览器已访问私有同URL，When换账号／另一标签页撤权后重访、携If-None-Match／If-Modified-Since等条件头或从history／bfcache恢复，Then首版不发ETag／Last-Modified／304，条件头仍完整当前授权，不能返回旧body或先闪旧正文，context成功不能替代全部内容依赖重核。请求在途切空间／退出换账号／epoch变更时旧回包和轮询不得灌入新内存；Abort失败仍挡迟到回包。旧写／付费不自动换epoch／Key恢复，不跨空间续会话。

证据：真实浏览器同URL换账号／撤权、条件请求及前进后退／bfcache录屏与网络原始响应；应用与网关no-store／禁缓存配置、无验证器／304、pagehide／pageshow与私有DOM／store／持久存储检查、延迟乱序多页操作、服务端原操作事实与新身份直接请求。S1交付公共设施，S2资源及S3历史各在入口开放前重做对应负例。真源：[C2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:20)／[R4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:51)；状态：未执行。

## AC-19 — 程序凭证与独立动作scope

映射：IA-10；FR-4/5；SM-6/7；S1→S3。依据：[只读程序许可](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:175)，范围：175–189；[原动作继承](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:334)。

- **正例：** Given本人选单空间/指定库/逐一只读动作/未来期限，When创建，Then密钥仅本次显示、列表只有元信息；本人或团队所有者在本团队范围撤销后立即无效。本人当前权缩小时有效scope取交集。
- **反例：** Given凭证只选A或仅citation动作，When请求B/资料写/成员管理/他人任务/问答operation，Then拒绝；GET operation与同Key重放继承原问答/比较动作、目标/依赖，不因GET绕scope。citation许可可核当前合法来源、不强加answers许可，但不交他人历史。创建丢回包不再造明文/新密钥；可列元信息并明确撤销后新建。

证据：scope/到期/撤销响应、仅本次显密录屏、原渠道新合法凭证读原操作正例及旧撤销凭证拒绝反例。

## AC-20 — 配置、三账、配额与真实成本

映射：IA-05/10/12；FR-4/15/16；SM-6/7；S1基础→S6。依据：[FR-4三账](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:163)，范围：163–173；[运行元数据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:28)。

- **正例：** Given平台有合法接入/配额配置，When验证/改默认/下调额度，Then验证状态明确，默认只影响新库或显式重建，不改已使用profile；下调不取消已受理操作而阻超额新预留。用量显示范围/上海日桶/最后确认时间，原件容量、产品问答次数、实际调用/Token/费用分列。
- **反例：** Given验证失败/缺必需配置/满额/磁盘压力/费用unknown，When新受理相应操作，Then明确拒绝/隔离，不写已接通/无限/免费；允许的本地读/删除等遵服务端保护事实。失败/重试真实调用仍留账，迟到可信费用可幂等补账但不复活答案/计次；不自动存储迁移、变维DDL或充值计费。

证据：配置版本/验证响应、最后一笔预留并发/跨日/降额/清理失败账、实际call intent与unknown/迟到费用事实；不拿UI数值替代账本证明。

## AC-21 — 键盘、屏幕阅读器与受控内容

映射：IA-01–12；FR-7/9/12/14、SM-3/6/7；各切片Web完成条件；本轮UX设计决定。依据：[EXPERIENCE无障碍](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md)。

- **正例：** Given只用键盘/屏幕阅读器，When完成登录、范围/条件编辑、提交、逐格来源、反馈、管理确认，Then标签/表头关系/错误摘要可读，焦点可见且不被遮挡；Esc只关未提交对话/来源，回触发处；多行Enter换行，显式按钮才提交；关键状态变化适度播报，密码/密钥不朗读。
- **反例：** Given资料文本/模型返回有脚本或任意资源URL，When渲染/引用，Then清洗且仅受控citation解析，不执行注入/泄露秘密；不得只靠颜色/悬停/拖拽操作。轮询不抢焦点/重复播报，资料单位/否定/条件不能被截断或只藏tooltip。

证据：键盘全流程与辅助技术录屏、DOM语义/焦点顺序、内容清洗与受控资源反例；目标为WCAG2.2 AA相关交互/对比要求，未实测不得宣称认证合规。

## AC-22 — 可信恢复与分步放行

映射：IA-01/04/10/12；FR-4/8/15/16；SM-6/7；S6。依据：[恢复契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:266)，范围：266–300。

- **正例：** Given按主契约可信恢复后新epoch、身份独立核验及特定范围/配额已核对，When操作者查看当前状态，Then只在其当前合法范围显示已核验/已放行事实，其他范围仍隔离；页面可分辨台账gap/费用unknown/配额待核，不把进程启动或备份存在当全站恢复。
- **反例：** Given旧owner/账号/会话/凭证或未独立核验资源、未知配额，When登录/读/写/重发旧请求，Then按主契约拒绝且不从旧备份自证、不自动换epoch/Key或恢复旧授权；隔离细节仅向已核验且有范围权者披露，其他人走安全认证/资源不可用边界。

证据：目标环境恢复演练、可信依据/台账、旧凭据负例、分范围放行、未知费用/配额核对记录；UX不新造一键恢复器，Winston落实执行链。

## AC-23 — 视觉、响应式与密度

映射：IA-01–12；FR-14及四场景可完成性；SM-7；各切片Web交付条件；本轮委托下设计决定。依据：[DESIGN](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md)、[EXPERIENCE响应式](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md)。

- **正例：** Given1440/1280/1024/767/375 CSS px及200%缩放，When查看12 IA和来源，Then依规范浅色/系统字体/tokens：≥1440导航224且主结果min640+来源400可并列；1200–1439导航224且来源独立返回；<1200导航抽屉；<768边距16/单列表单/原件与提取tabs/矩阵局部横滚。资料详情≥1200三区并列、其下纵排。
- **反例：** Given窄屏/触屏/长中英文/长条件，Then不把全页压小字号、不隐藏矩阵格/失败范围/旧版可用性/单位与费用说明；细指针视觉控件≥32px，粗指针40px视觉控件但目标≥44px且间距≥8px；正文/背景/焦点对比按DESIGN目标实测，不以默认Element Plus必然合格作证。

证据：各宽度/缩放截图、实际颜色对比计算、触控命中与焦点检查；四关键屏静态图是设计参考，不能替代此运行检查。

## 架构补充验收 R01 — 共享调用窗口、停发证明与恢复

映射：IA-05／06／07／08／12的全部外部调用；FR-4／15／16、NFR-1／2／6；S0本地假件先行、P0真实核验。技术单一真源：[C8共享rate gate](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:145)、[R2受监督派发](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:23)。状态：未执行，不构成真实服务或资源成绩。

- **正例：** Given真实PG＋可控传输假件，When逐一暂停grant跨秒／分钟、检查后暂停并让另槽推进，再完成正常／强制退出的受监督停发，Then grant的send_open charge在领取窗口过期后仍计占；控制器证明本call发送child／后代退出、全部发送FD／IPC关闭且旧grant销毁后，才取随后DB时刻last_local_send_upper并保留完整W。准入同时计open与sealed未满W，多维charge及关联call可核对；重复seal／控制器重启不提前释放、不重复计量。
- **反例：** Givenchild失联／暂停、旧grant或FD仍可能发送、无监督停发证明，When send-by／lease到期、业务取消／终态或进程重启，Then对应维度继续占用／阻塞；不能靠child读钟、暂未观测到字节、跨窗口或业务结束就重新借额度。S0全部负例通过前任何真实外发均禁止；P0使用真实账号核有效限额与实际SDK发送账，不承诺远端到达窗口或永无429。

证据：各暂停点与另一槽推进时间线、PG grant／open／seal／last_local_send_upper／维度汇总、child／后代退出及FD／IPC／grant销毁的监督证明、重复seal／重启前后账和准入结果；P0另存真实调用／供应方响应及429，未知仍unknown。两个任务gate各默认4、可配1–4且全部账号合计最多4，本机重处理槽1、四场景／K=5及原deadline保持既定约束。

## 原SM/F0/S0/P0/S7门槛不变

| 锁定项目 | 实现/验收记录必须保留 |
| --- | --- |
| F0/固定题集 | 首次调优前冻结32题，四场景各6可答+2不足，资料/原证据单元/必要事实/判定不因后续分块或结果改变；开发题与冻结验收隔离 |
| K=5 | 全请求所有子检索合并后最终至多五块；catalog与实际模型实见片段一致，不补邻块/全文/旧答；分母仍原金标证据单元 |
| SM-1 | 至少21/24可答题且各场景至少5/6，必要事实齐全、无关键错、结论引用一致 |
| SM-2 | 原必需证据单元合并覆盖≥85%，按场景另报；catalog存在不自动算覆盖 |
| SM-3 | 事实结论引用直接支撑≥95%，引用定位可打开100%；人工核语义，链接存在/HTTP200不等于支撑 |
| SM-4 | 8/8不足题全部正确不足/澄清/限定，不全面拒答刷分，不把可答题故障改不足 |
| SM-5 | 表格、扫描OCR、图意、资料冲突、版本差异五类各至少一条通过；专项失败不可被平均分抵消 |
| SM-6 | 独立于32题的权限反例专项全通过，含输出前撤权/历史/引用/下载/凭证/负责人/降级/移除 |
| SM-7 | 导入/替换/删除/重试及四场景Web主流程、API原始可复核结果、真实改进实验与异常复盘；退步/无收益/失败如实留存 |
| P0/S0/S6/S7 | 真实格式/来源/图意/embedding及模型预算接入在P0；工程基础按S0；4C4GB目标机/重建竞态/可信恢复在S6；S7同冻结材料保留B0/上一保留轮/本轮完整记录。不能用设计或mock通过替代 |

来源：[固定题集与SM-1–7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:318)，范围：318–344；[切片依赖与门槛](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:15)，范围：15–25、37–43、85–104。

## Winston/Amelia记录模板与停止条件

每条AC运行记录至少含：AC编号、需求/切片、版本/环境、前置主体及权限、输入及当前有效限制、动作序列、预期/实际页面与HTTP结果、operation/candidate/job/call等安全关联、实际副作用、证据位置、通过/失败/阻塞及原因。自动化方式、fixture组织与物理测试框架由实现方决定；必须能复现上述正负例。

任何权限泄露、目标集合静默缩减、完整矩阵缺格、无据事实、定位损坏假成功、未授权自动新调用/重复扣次、旧回包串账号/空间、恢复未核验放行均不得作为“视觉已完成”跳过。先停止对应切片/范围，按原契约修复并保留失败证据；不降低FR/SM、不重开已定角色与场景。
