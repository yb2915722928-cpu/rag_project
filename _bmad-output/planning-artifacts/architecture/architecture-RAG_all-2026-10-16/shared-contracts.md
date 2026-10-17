---
title: RAG_all 共享契约
status: final
updated: 2026-10-16
binds: [AD-2, AD-3, AD-4, AD-5, AD-6, AD-8, AD-9, AD-10, AD-11, AD-12]
---

# 共享契约

这是后端contracts的冷启动规范，实施时由同一模型导出OpenAPI、JSON Schema、TypeScript及正负样例；不维护手写平行类型。[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md)仍为业务真源，[comparison.v1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md)仍为比较能力结构真源。

## C1：标识、时间、文本与序列化

- 资源ID为非空稳定ID且不复用，线协议均为1–64 ASCII字母/数字/下划线/连字符；客户端可生成UUIDv7逻辑Key，资源ID由服务器产生。Candidate.version_id与Evidence.document_version_id都是同一个DocumentVersion.id，字段别名不建立第二种版本实体。
- 时间在线路上为带Z的UTC RFC3339，服务端按DB时间判断lease/deadline；日桶显式存Asia/Shanghai受理日期。浏览器本地时间只展示。字节为整数，使用非负bigint；外部usage/费用未知为null且带unknown，不用0默认值。金额用十进制字符串+币种+估算/账单来源，不用浮点累计。
- 所有码点长度和文本偏移以Unicode标量值计（拒孤立surrogate），区间为半开[start,end)。Python与TS共享非BMP样例；TS的UTF-16 length/slice不能直接充当本契约码点实现。
- 当前question/日志等保留完整解码值，不全局NFC/trim/合并空白/改换行；全空question仅拒空。仅comparison条件按已登记版本NFC+去首尾空白，重复判定另合并连续空白；原值与规范值分开保存。HMAC覆盖规范版本、完整业务输入、显式目标、会话/父轮次和参数，不只覆盖实际提示片段。
- 规范对象序列化为UTF-8、键按规范顺序/稳定排序、无无义空白、禁重复键/NaN/Infinity；显式null与缺省值按schema区分。集合型KB/document ID先验证无重复再稳定排序参与指纹，展示型objects/conditions保持原序。所有schema拒未知字段/未知版本。

## C2：公共HTTP包与能力载荷

公共包使用扁平对象；能力字段与metadata同级，不再包装一个平行data对象。schema_version指能力schema（answer.v1/comparison.v1/retrieval.v1/operation.v1等），status仅completed/in_progress/failed；outcome、operation_state和job_state为不同字段/枚举。

| 场景 | 必需公共字段与规则 |
| --- | --- |
| 每次响应 | schema_version、request_id、status；HTTP尝试得到新request_id，重放不复用原诊断ID |
| 问答/比较完成 | operation_id、replayed、accepted_at、completed_at、execution_snapshot_id、能力载荷与服务器evidence_catalog；原时间/版本不改成重放时间 |
| 202 | operation_id、operation_state、受控status_url、retry_mode=same_key_or_status；无半答案 |
| 失败 | error={code,message,http_status,retry_mode,details}、安全可读ID与恢复提示；details仅白名单有限元数据，不含无权目标、正文、任意上游异常/URL |
| GET operation | HTTP200可返回安全原状态和error.http_status；同Key终态POST使用原对应失败HTTP。GET不启动执行、不刷新期限 |
| retrieval | 无生成operation或产品预留，但有持久retrieval_execution_id与deadline/call账；结果至多五块 |

retry_mode严格为none/same_key_or_status/new_operation/manual_reconcile，是恢复动作而非自动付费许可。错误码和HTTP以实施契约§5.3为底线；新增子码不能改变整目标拒绝、计账和保密语义。Path/body同一目标不一致422；未经认证不返回可恢复私有operation ID。普通answer载荷继承实施契约§3.7的facts/quantity/gaps/clarifications四态，比较继承全格四态；模型只生成能力子对象，可信metadata/catalog由服务器补齐。

所有私有HTTP响应固定`Cache-Control: no-store`，覆盖Web与program的认证/context、管理、状态/失败、问答/重放/历史、citation、页图/提取与原件，包含非2xx与gateway自产错误；不以Cookie、Bearer或GET/POST差异推定可缓存。首版私有路由不发ETag/Last-Modified，不返回304；带If-None-Match/If-Modified-Since也先当前鉴权，再返回正常受控响应或拒绝，不复用旧body。gateway必须关闭该路由族缓存且保留no-store，具体见R4。公开带内容hash的静态构建资源另行缓存，不能包括私有JSON或资产。no-store不证明旧副本或浏览器历史内存已清，历史恢复另守C4/AD-12。

## C3：SourceLocator与EvidenceSnapshot

Library持有不可变DocumentVersion、source_text和SourceLocator，原件hash=实际原件字节SHA-256。source_text_hash=精确不可变UTF-8提取文本字节SHA-256；抽取时采用哪种换行/规范化须入processing_config_id，此后不得再规范化同一source_text。

| 结构 | 规范字段与校验 |
| --- | --- |
| SourceLocator公共身份 | locator_schema_version、space_id、knowledge_base_id、document_id、document_version_id、source_asset_id、original_sha256、source_text_hash、kind；归属组合必须与版本一致 |
| PDF | kind=pdf；physical_page为1起物理页、在page_count内；bbox可null。bbox=[x0,y0,x1,y1]，有限数且0≤x0<x1≤1、0≤y0<y1≤1，原点为渲染后的可见页左上，x向右/y向下；坐标基于已应用页面rotation后的CropBox可见区域。适配器记录原页基数/坐标空间/rotation与转换版本，先验证再归一，UI不二次猜旋转 |
| PDF无bbox | 有可靠物理页可用page-only，明确无区域高亮；不能用空框/整页框伪造精确定位。bbox与页不可信则不可用，不猜页 |
| 非PDF | kind=structured；structure_path为有序真实标题/段落/表格/行列路径，block_id稳定，text_span可用[start,end)引用该不可变source_text；至少真实结构路径或可靠字符范围，不能编物理页；图表另绑定原资产和上下文定位 |
| 精确片段 | excerpt=source_text[start:end]；0≤start<end≤码点数，hash对应实际UTF-8片段；跨页/不连续证据用多个有序spans，不能用一个假连续范围包住未见中段 |

Query写EvidenceSnapshot：evidence_id（本结果局部白名单）、chunk_id、上述完整来源身份、原五块名次、实见spans及精确excerpt/hash、source_locator、预算裁减原因、execution_snapshot_id。同chunk的原文范围与模型实见范围分开；catalog精确列实见快照，最多五块，模型无法自填locator/URL/版本。citation_id为服务器保存映射的受控不透明ID，回看重新核当前身份/原动作或独立citation scope、父级、墓碑、hash和归属。历史答案不依赖向量永久存在。

PDF正负样例必须覆盖0起上游页→1起物理页、90/270度旋转、非零CropBox、越界/NaN bbox、页可靠但无框；文本样例覆盖CRLF、组合字符、中文和emoji，验证码点/字节/hash不混用。定位/资源损坏返回SOURCE_LOCATOR_UNAVAILABLE并可按权限原件下载；发布必需来源不可信则不能ready。

## C4：执行栅栏与同UoW矩阵

ExecutionFence携带epoch、owner_context_id、attempt、claim_token、lease_until、hard_deadline，适用时加candidate_id/job_id/guard_token；这些来自持久状态而非客户端可信声明。任何业务写与每次派发必须按当前代次条件更新；零受影响行即失效。call_id事实回填是唯一可不复活业务的独立通路。

所有需当前授权的关键短事务先按用户ID升序取所需全部账号控制行SH，再按space ID升序取空间控制行SH，继而KB稳定ID升序→业务类别(document/candidate/job/operation/conversation)及ID升序→空间容量/日桶→文档本地gate ID升序→provider rate pool ID升序→call ID升序→permit组件ID升序→asset ID升序；不需的类别跳过。安全变更在对应控制行取EX（SQL FOR UPDATE），授权读取取SH（FOR SHARE）；不能先SH后无序升级，提前按用例确定EX集合。涉及操作者/目标/新旧owner先解析稳定ID后一次排序取锁，space后禁止补账号锁，解析信息取锁后复核。后台已受理库任务只取space SH再KB，永不回取用户。持PG事务不等待OS/网络/进程/删除；OS锁先在事务外获得，再短事务复核。

账号控制行覆盖账号状态、会话/凭证撤销和到期、改密、恢复verified；空间控制行覆盖成员/角色/owner/邀请、逐库ACL/负责人、空间隔离/删除。所有修改这些子表的仓储必须先取得对应控制行EX，不能绕行；涉及账号行与space两者时仍账号在先。space锁后确定并重核全KB集合；锁集合改变则回滚重试，不反向加锁。用户发起整体删除仍先取操作者账号SH；不修改其他账号实体时不必锁全体成员账号EX，其业务范围写锁为space EX及相应KB。后台库任务的免用户前缀只适用于已合法受理意图，不能成为用户管理动作跳鉴权入口。只读放行在短事务内当前校验，释放锁后的网络传输与撤权不承诺全局原子。

| 用例事务 | 必须一次提交的效果 |
| --- | --- |
| 上传候选创建 | 当前维护权+KB guard→候选/上传意图+原件条件预留+物理预算承诺 |
| 原件完成 | 当前维护权+Fence/hash/实际长度→原件资产登记+预留转实占+job创建 |
| 普通版本发布 | 库资格/Fence/墓碑/guard/向量完整→active_version+块向量可见性+docset_revision+候选/job终态 |
| 查询受理 | 当前身份/全目标/父轮次+逻辑gate→operation/执行快照+日桶预留+会话未终结指针 |
| 每次外传 | 用户查询当前账号/渠道/scope或库任务资格+Fence/预算→prepared；may_have_sent另一次临近短事务重核且原子领账号总池/用途子池permit后提交，随后单grant |
| 查询成功 | 当前授权/全原目标及结果依赖+Fence→结果+EvidenceSnapshot+会话一对消息/父轮次+产品结算+逻辑槽终结 |
| 查询失败/恢复终止 | 当前Fence条件→原失败/unknown终态+产品释放+会话忙指针/逻辑占位释放；真实物理槽另等停写 |
| 删除/撤权/转让 | 控制行EX+当前权限→业务墓碑/权限/负责人+安全事件同事务；删除还增revision、废弃候选并条件释放本guard |
| 状态重放/历史/citation/download | 对应账号/space SH+当前渠道/原动作或独立citation动作+全部原依赖/墓碑/hash→受控投影；不创建新操作 |
| 清理完成 | 事务外停写证明+稳定OS EX锁+cleanup token复核→cleaned+一次原件/物理预算释放 |
| 迟到成本 | 仅call锁→唯一事实追加/冲突待核；不再取业务父锁、不改成功失败/配额/会话 |

迁移必须实现等价唯一性：非空稳定ID、组合归属约束、活动版本/当前候选指针、活动generation/有效guard、会话唯一未终结轮次、用户+空间+能力+Key摘要、逐文件Key域、容量/日桶非负、唯一quota_transition/call事实。具体表结构是S0/S1代码seed，不通过仓储私自降低约束。

私有读放行还必须遵守C2的no-store与条件请求规则。Web不将私有body、来源blob或认证context写入localStorage/IndexedDB/CacheStorage/service worker缓存；内存缓存仍须归属隔离。pagehide同步遮蔽并清除私有DOM/状态、撤销blob URL、作废旧异步代次；pageshow（含persisted/bfcache与普通历史恢复）在显示私有数据前保持遮蔽、清理旧context并生成新本地代次，重新取得当前context，再逐项重核原操作全部依赖及资源后才重新取数展示。失败保持空白安全状态/登录或无权提示，不显示旧快照兜底；不依赖unload必触发或no-store禁用bfcache。此边界不承诺追回已合法显示/保存的字节。

## C5：有限管理schema与身份技术seed

以下是受托实现初值，技术配置有版本、可调整但不得放宽上游权限/期限不变量；不是运行成绩。所有管理JSON也受H结构界，列表均有界，不把全部成员/库/审计导入页面后分页。

| 字段/入口 | 共同有限边界 |
| --- | --- |
| 展示名/标题 | 1–128码点，禁止全空和C0控制字符；不改来源原件名，文件显示名最长255码点、禁止路径分隔符作为存储路径 |
| 描述/反馈 | 描述≤2048，反馈≤4096码点；反馈绑定本人可读result_id，不能注入任意来源/他人历史 |
| 标识/登录名 | 登录名1–64 ASCII字母/数字/下划线/连字符，ASCII小写为唯一匹配键；展示名独立。技术上不推定邮箱/短信登录或自助注册 |
| 分页/筛选 | page_size默认20、最大100；不透明cursor带筛选/排序版本、范围与15分钟有效期，排序白名单+稳定ID末键；search≤256，sort≤1项，单次时间区间≤366d，过期cursor明确重取首屏；更长历史显式分窗，不静默省略 |
| 授权/管理集合 | 单请求主体ID/KB ID分别≤64，逐项校验/无重复，超过分批显式操作，不能部分成功暗漏目标；平台批次另受当前权限 |
| 配置 | 端点/模型/key_id等按单用途严格schema，URL≤2048且仅HTTPS、服务器允许的provider域；禁止任意内部URL/文件路径。secret≤8192字节只输入不回显；配置值缺失不取无限；unknown字段拒绝 |
| 通用动作 | retry/cancel/reconcile/local-continue等写动作带UUIDv7 action_key，按持有人+space+动作+目标唯一及规范输入指纹；同输入重传原结果、异输入409，不凭网络重发再付费。期限沿24h/7d墓碑原则，不改原job deadline |

密码12–128 Unicode码点、最多512 UTF-8字节，保留原值且不trim/截断。argon2id采用库RFC_9106_LOW_MEMORY参数档，hash内保存参数/盐；成功登录按新配置rehash，目标机核验延迟/RSS前验证并发≤1。失败登录统一安全错误；按登录名摘要和来源地址使用PG有界尝试桶，初值每15分钟5次失败后15分钟冷却，桶到期扫描；不得以IP限流替代账号桶或把原始登录名写普通日志。

Web会话是≥256位随机不透明secret，DB仅SHA-256摘要+用户/epoch/created/last_seen/absolute_expiry/revoked；初值空闲30分钟、绝对12小时，续活不越绝对期。登录成功换会话、退出撤销、改密撤销该用户全部会话及程序凭证（当前会话也要求重新登录），恢复epoch全失效；Cookie为Secure/HttpOnly/SameSite=Lax/Path=/且不用Domain扩大子域。生产同源，CORS关闭；程序Bearer不使用Cookie回退，同请求本应用Cookie+Bearer仍整拒。

匿名登录POST采用独立防护路径：Origin必须精确等于受托部署配置的scheme/host/port（不从任意Host/X-Forwarded-*推导），Content-Type必须为application/json（可带UTF-8 charset），固定自定义头`X-RAG-Login: 1`；拒缺失、null或跨源Origin、简单form类型与缺头请求，防护失败403且不创建会话。新浏览器不要求尚不存在的认证会话/CSRF token。成功时撤销请求携带的旧会话并建立全新会话和≥256位随机、会话绑定的CSRF token；token仅由C2 no-store的受控登录响应交前端内存。后续页面重载可经同源、当前认证的no-store context GET重新取得本会话token；不将token放URL或持久缓存。其他已认证Web写（含退出、改密、上传、管理及业务POST）必须同时校验精确同源Origin与`X-CSRF-Token`绑定当前会话，缺失/失配403；匿名登录的固定头不能替代该检查。登录无凭据/现有过期Cookie均不落入token前置循环，仍受密码校验、失败桶及恢复隔离规则约束。

普通鉴权SH事务只读，不能顺手写last_seen/rehash/失败登录桶或撤销状态。空闲续活、rehash、登录失败桶/撤销要么在用例开始确定账号EX，要么独立账号EX短UoW并重核状态/旧过期值；不得在持space/KB或account SH时升级回取。续活失败/已过期不授新资格，不能以异步触碰掩盖会话本应失效。

程序凭证明文仅创建显示，格式public_id+≥256位随机secret，DB存摘要与当前scope/expiry/revoked/epoch；必须显式到期且大于当前，技术最大365d、UI初值30d，范围仍只有本人一个空间/显式库/枚举只读动作。邀请使用一次性≥256位随机token摘要，初值7d，接受时当前空间/邀请者资格与被邀请主体重核；不引入外发邮件服务，链接交付方式依既有团队管理流程。

供应方secret为可恢复密文（cryptography AESGCM、随机96位nonce且同key不复用，AAD绑定deployment/provider/config/key_id）；主密钥外置secret只给需要的服务，不随普通DB导出。key_id与算法/格式版本保存，轮换先保留读旧能力、重加密后退役；缺密钥明确失败，不重置密文。Cookie/Bearer/邀请/CSRF明文和供应方secret不进入URL query、日志、审计或前端持久存储。此seed须S1与S6负例验收，不能包装为已获安全认证。

EgressTarget是所有适配器共同出网契约，覆盖配置端点和MinerU等上游返回的PUT/下载URL：仅HTTPS，拒userinfo/fragment，配置URL≤2048码点、签名URL≤8192 UTF-8字节；每用途profile登记已核准确host/port允许表，上传/下载域不因上游返回就自动信任，不用宽泛公共云后缀替代。每次派发解析全部A/AAAA并拒回环、私网、link-local、保留/元数据地址，实际连接绑定本次已核公共地址且保留正确TLS主机校验，不能检查后另一次任意DNS解析以绕过；自动redirect关闭，新的redirect也不隐式跟随。未知host在P0核登记新配置后才派发。签名query按实际URL原值保留作该call最少秘密，不写日志；API Authorization仅给已核API host，不转发到签名上传/下载host，不给child泛用网络凭据。失败安全返回DEPENDENCY_UNAVAILABLE或配置子码，不泄签名URL。URL许可/有限性不代替当前资格、预算和call guard。

## C6：限制与生成子契约单一真源

EffectiveLimits返回config_version、H/B有限数值、允许格式/字节/页数、矩阵可受理范围、有效用途profile状态与安全说明；不得回传provider secret、全部授权列表或隐藏不可用资源。H与B原数值和准入顺序完全继承实施契约§3.5；二进制PUT/下载/ZIP/模型响应各自独立字节预算，不套1MiB JSON体。

GenerationContract独立标识answer-compact128/comparison-compact128，与公共answer.v1/comparison.v1分离：初值比较每格reason1–128码点；普通fact.text/applicability、gap/clarification.text≤128，summary.text≤256，外层数组/全部格/四态证据语义不减。完整输出R按本次真实ID、最大合法分支/数组/转义和已证token上界预算；不能前端截断128、删格或以平均长度估R。提高新档须新generation_contract_id/config_version及P0预算与原SM质量重验。

检索排序继承[已定技术选择](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md:119)：各子路内部按cosine distance升序、稳定chunk_id升序；比较子路按条件原序、文档ID升序逐路取第1名再第2名，按同一不可变chunk_id跳重复，到五块或耗尽，不比较不同子路分数。普通B0同样以chunk_id解同分。各路只需取能影响最终五块的有界候选；候选正文再按实际预算有界读取，不能用无界TopN载入全部库。

BudgetSnapshot保存原规范输入hash、H/B版本、用途profile/tokenizer/template/prompt/schema/SDK指纹、generation_contract_id、I分部与最终完整计数、R/margin、embedding批计划、原五块顺序与实际spans、call_ids/finish_reason/usage/错误。完整输入/快照正文只在受控业务存储，日志仅hash/ID/数值；跨模块不能另造预算算法或把schema通过当语义支撑通过。

## C7：五投影最小DTO与格式分派

文档行/详情统一含document_id、space_id、knowledge_base_id、document_deleted和以下五个独立字段。null明确“无该对象”，不能用空字符串/总status代替。各投影带安全updated_at、error（可null）；未授权对象整请求按安全边界拒绝，不能靠部分null暗示其存在。

| 投影字段 | 最小DTO与有限枚举 |
| --- | --- |
| active_version | null或{document_version_id, availability:ready/partial, original_sha256, published_at, incomplete_ranges}；失败候选不改此对象 |
| candidate | null或{candidate_id, document_version_id, upload_state, processing_state, upload_start_by, upload_hard_deadline, retained_original_bytes, incomplete_ranges}；upload_state严格awaiting_upload/uploading/original_committed/expired/cancelled；processing_state为null或queued/running/awaiting_reconciliation/ready/partial/failed/cancelled/expired/discarded |
| job | null或{job_id, attempt, job_state, stage_code, hard_deadline, lease_until, progress}；job_state为queued/running/awaiting_reconciliation/succeeded/failed/cancelled/expired；progress为null或有限{completed,total,unit}，未知不假100% |
| index_generation | {active_generation_id:null或ID, embedding_profile_id:null或ID, docset_revision, rebuild:null或{job_id,candidate_generation_id,target_profile_id,state}}；新建空库可无活动代/未定profile，用null明确表示，不能伪造ID；有活动代必须绑定已证不可变profile，rebuild非null须有已证target_profile。rebuild.state用上述job_state，活动代和重建状态不互相覆盖 |
| cleanup | null或{asset_owner_id, cleanup_state, charged_original_bytes, retryable}；cleanup_state为cleanup_pending/cleanup_blocked/cleaned，cleaned前占用不归零；null仅未请求清理，不推断无资产 |

上述是公共投影枚举的唯一seed，不将上传状态塞成job状态。模块内部状态可以更细，但必须在contracts提供显式全覆盖映射与正负样例，未知状态是契约错误而非猜测为失败/ready。incomplete_ranges为按来源kind的有限区间列表，最多100项/分页详情；PDF物理页/非PDF真实结构且有原因，不用笼统“部分失败”掩盖不明范围。

文档/任务allowed_actions是服务器按当前权限和状态得出的有限集合：view_current/view_candidate/view_original/view_extraction/view_task/view_cleanup/replace/retry/cancel/abandon/reconcile/local_continue/resubmit_with_ack/delete/rebuild_index/cancel_rebuild；不返回任意路由/命令，UI仅映射已知动作。resubmit_with_ack必须再次明确潜在重复外部费用，allowed不替执行时当前授权。没有常规逐份approve_publish动作。其他身份/平台管理动作在各能力schema有自己的固定枚举，不借此文档动作表获得额外权限。

格式路由也是共享端口契约：文本/扫描PDF及DOCX使用MinerU精准API主路；TXT/Markdown用有界本地严格UTF-8解码与结构保留，记录BOM/换行处理配置、不抓取远程链接/图片、不执行HTML/脚本、不增加本地OCR；所有格式都产同一不可变SourceLocator并经相同完整性/来源/向量发布守卫。声明/探测格式矛盾明确拒绝，损坏/加密/非UTF-8不能猜编码后假成功。官方额外支持Doc/Ppt/Xls不扩首版承诺。P0逐个承诺格式、PDF页/bbox和DOCX结构的真实结果仍是S2前置。

资源交付与解析是两个边界。每次打开原件、提取或预览先执行C4当前授权/归属/hash核验，响应再遵守C2 no-store；客户端或上游的文件名、Content-Type、Content-Disposition不能原样成为响应头。

| 表示 | 服务器交付规则 |
| --- | --- |
| 五格式原件 | 一律`Content-Disposition: attachment`及`X-Content-Type-Options: nosniff`；服务器依据已校验格式映射MIME：PDF→application/pdf，DOCX→application/vnd.openxmlformats-officedocument.wordprocessingml.document，TXT→text/plain; charset=utf-8，MD→text/markdown; charset=utf-8。禁止text/html、SVG或用户/供应方指定主动类型；原件不inline，准确MIME与attachment须同时满足 |
| 下载文件名 | 服务器生成有限ASCII fallback（稳定ID+已核扩展名）及规范UTF-8 filename*；展示名经服务器移除CR/LF、其他控制字符、路径分隔/目录片段并限制255码点，无合法名则用fallback。使用规范header编码器，不拼接原始header、不接受重复filename参数或上游Disposition |
| inline预览 | 仅允许本机解码/重编码并核格式与像素/字节上界的image/png或image/jpeg页图/裁图，映射回可信locator；不得直接inline原始PDF、HTML、SVG、上游任意响应或有主动能力的文档。文本/MD/提取通过application/json受控文本字段交应用，用textContent/已定Markdown清洗渲染，不插入原始HTML、不抓远程资源 |

nosniff不能让明确的text/html变安全；原件下载也不承诺用户另存后在其他程序打开不会执行。首版不提供主动内容预览，若未来确需该能力再独立设计隔离origin/sandbox/CSP，不以开放iframe兜底。S2须有含HTML/脚本语法的合法UTF-8 TXT/MD、伪类型/扩展名、CRLF/路径文件名、预览不执行/不外抓及当前授权的正负验收。

## C8：跨进程共享调用rate gate

execution是共享RatePool/CallPermit唯一写者。pool身份为provider_account_id+region+rate_pool_id，profile/key_ref必须映射到真实账号限制范围；换密钥、API/worker、query/document/vision用途不能新建一个额度副本。每用途可有更紧子池；每个真实限制维度登记有限值、窗口和适用动作，包括RPS/TPM、在途HTTP、异步task并发，不能把厂商的task限制猜成所有HTTP限制或反向猜测。P0固定submit/poll/download等动作到真实维度的映射；未证范围/计数/适用性不得启用对应能力。

每个call_id唯一CallPermit，携带本动作实际适用的有限permit_components；账号总池及用途子池的全部适用组件在同一短UoW按pool ID升序原子校验/领取，与may_have_sent提交绑定。submit指官方协议实际新增/触发task的动作，不按HTTP方法或端点名称猜测；首版一文档job绑定一个原task，不跨job合批提交云解析，不能一call新增N个task却只算1。新增异步task由submit领取task组件，未知响应保留该组件；持久已知task的只读poll引用原归属，不重复领取新增task组件，但仍领取其实际适用的HTTP/RPS等账号与用途组件，不借“核对”绕过共额。下载同理按真实映射领取。不得重绑客户端任填task ID，也不得为活性拆出不符合官方共额域的假池。

本轮用户授权提高异步文档并发，覆盖旧“整文档并发1”技术seed：execution统一PG gate的doc_active_job_limit默认4、允许配置1–4；external_async_task_limit默认4、允许配置1–4，跨所有账号合计约束已提交/可能已提交且未证终态的task，不因job失败、重启、换密钥或旧task未知而返还。二者是全系统的独立上限，不是每账号各有4，也不是job与task元数据合计4；旧unknown task与新活跃job可各有最多4条元数据，但未知task未清前新submit仍被全局task gate阻断。每job至多一个未终态task；这两个本地gate独立于厂商共额域，不冒充真实账号池，新增task须与全部适用账号/用途组件同UoW领取。生效能力取本地配置、已核账号/用途限制和已验证资源包络的交集，未核账号不能实际派发。单机worker物理重处理阶段槽仍1；远端等待仅保留持久ID/期限/permit元数据，受控child停写并关闭FD、结果落盘后才能归还物理槽并调度另一job，不为四个pending各起常驻线程或常驻child。原task只读核对不另领新job/task新增名额，仍占其真实适用传输槽与HTTP/RPS维度；调度不得让pending占满后饿死必要poll。

两个本地gate也由execution独占、全系统共用PG控制行与唯一transition：queued job创建不占doc_active_job，worker条件领取并开始处理时同UoW领取，业务终态/到期fence时按job_id一次释放；原2h绝对deadline仍从原件受理起算，排队/调度/远端等待不延长。external_async_task在submit的may_have_sent同UoW按原call唯一领取，只有该task组件可信终态/可证上界才能与本维账号/用途组件同UoW一次归还；doc_active_job归还不顺带归还未知task。涉及这些gate的事务按C4本地gate→provider pool→call→permit组件锁序；恢复本地task计数也blocked_unverified并按独立未决事实重建，不能用备份旧低值放新task。控制器采用有限轮转：每个活跃job每轮最多一个已到期可执行阶段，stage完成停写后轮到其他job；到期poll/reconciliation在本轮先于新submit，poll遵守实际最小间隔、不忙等，不持Session或正文缓冲等待。

RPS/TPM采用持久的“未封口持续占用、封口后完整窗口”保守滑窗。may_have_sent同UoW为每个适用窗口组件创建唯一charge，`send_state=send_open`，绑定call/attempt/boot/child启动实例、有限send_stop_by及grant标识；先提交charge再经私有IPC给一次grant。RPS权重1；TPM权重为完整已证输入上界+最大输出（含思考上界，适用时），不按平均usage。对任意账号总池/用途子池维度d，窗口W_d、上限L_d、DB时刻t的准入计数为`sum(weight_d where send_open OR t < last_local_send_upper + W_d)`；含新call后仍≤L_d才原子领取全部组件，否则不发grant。未封口charge即使跨秒/分钟、业务失败、期限过期或重启也持续全量计入，不能凭may_have_sent时间+W移除。

本地发送计量边界是该call由受监督传输者向本机传输栈提交请求应用字节的可能区间，不是远端接收时刻。首版封口证明固定为控制器确认该启动实例的本call child及全部受控发送者已停止、发送FD/IPC已关闭、未消费grant已销毁且不可能再授予/恢复原grant；正常结果先有界落盘，再退出child，不能仅凭其“已消费/写完”自报。取得证明后，execution独立短UoW按pool→call→组件锁序，持久proof ID并用随后DB时间条件`send_open→send_sealed`，设置只写一次的last_local_send_upper；每维从该保守上界继续保留完整W才自然到期。重复封口/扫描零额外效果；成本账和远端组件终态不随封口修改。child复用仅限不持旧call发送能力的其他阶段；每个外部call的发送child必须先按此规则退出。

send_stop_by不晚于原阶段/业务hard_deadline，只触发拒发新grant、撤销未消费grant、TERM/KILL及等待停止证明；它和child发送前读钟均不是停发证明。检查后暂停、部分写后暂停、IPC失联但child仍活、controller崩溃/kill未确认时保持send_open并阻相应新额度；物理槽也不复用。已竞争发生的迟发仍由原charge覆盖，不声称到期瞬间网络绝对静默。DB时钟后退不提前到期，检测到超出已验证时钟包络的前跳/时基矛盾则阻断窗口、核当前sender后重新建立保守上界，不能用跳钟清额。prepared无rate permit，不能归还未领额度；usage回填只补事实，不缩减charge或反向取pool锁。此算法不承诺网络到达滑窗或厂商永不429。

供应方远端并发约束与本地物理槽分开，HTTP与异步task组件也分别终结：可信HTTP响应只证明本HTTP组件终态，不能释放仍running/unknown的task；原task终态由合法poll/官方查询证明，或本维已证官方绝对执行上界到期证明。上界证明必须覆盖该call最晚可能实际到达的时刻；may_have_sent后仍可延迟发送，不能只将该本地提交时间加厂商执行时长当终态证明。缺实际接收时刻或可证最晚到达界时保留unknown。child退出/超时不证明任一远端组件结束。许可释放由execution独立短UoW按适用本地gate ID升序→pool ID升序→call ID升序→permit组件ID升序取锁，核该维已持久可验证证据，以每(call_id,dimension_id)唯一release_transition_id条件active→released，同事务只归还相应账号总池/用途子池的本维并发一次；重复响应/核对零效果，CallPermit整体结束须全部适用组件均结束。无业务父锁、不复活业务，迟到成本入口本身不能释放许可。RPS/TPM组件独立遵守上述send_sealed后完整W到期，不能因HTTP/task release或usage回填提前返还。

P0必须实证task池满时原task的受控poll仍能在其真实适用限额内推进并取得终态，验证重启后的同任务路径与各组件独立一次释放；不能以人工处理替代正常异步流程。若真实厂商限制使必要poll也无法取得且无可证官方有限完成上界/受控核对通道，该能力保持不启用，先解决接入契约。异常无ID/未知终态只阻相关维度的新工作，按登记的官方只读核对或独立厂商核验通道处理，不盲重交。逻辑查询拿不到槽立即429；已受理内部等待仅在原hard_deadline内且无Session，不增加查询队列，期限届满保留原unknown与明确停止/核对动作。派发提交与网络依旧非原子，不能承诺调度暂停/撤销后远端零请求或厂商永不429；保留unknown与失败证据。

恢复旧包后全部共额pool先blocked_unverified；新epoch不证明备份后丢失call/远端inflight已终止，也不能按旧低计数重开额度。窗口放行前须独立确认全部旧本地sender已隔离/停止且旧grant不可消费，包括备份后缺失call；从该证明后的新DB上界保守等待各完整W，不能用旧备份中已到期的领取时间自证。证明缺失维持阻断。现行接入受托人再核真实维度/适用动作、额度及未决调用后逐维度、逐动作放行；已知原task的只读核对可在其真实适用HTTP/RPS等维度验证可用后受控开放，不因task新增维度仍blocked就禁止不新增task的合法poll，也不能豁免poll实际适用的未知维度。窗口封口+W只解RPS/TPM，不解远端并发unknown；无ID且无本维官方有限执行上界继续阻该维新工作并走登记的独立核验通道。普通重启对已持久send_open同样先停旧sender再封口，不清计数。不能借恢复清账，恢复控制按运行契约T4/T5执行。
