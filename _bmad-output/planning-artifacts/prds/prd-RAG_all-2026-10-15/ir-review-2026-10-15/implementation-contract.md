---
title: RAG_all 实施契约
status: final
created: 2026-10-15
updated: 2026-10-16
---

# RAG_all 实施契约

本文件配套唯一需求基线 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md)，记录两轮 IR 的现行跨模块边界，不替换既定角色、四场景、K=5 或主栈。第二轮修订继续在此文件合并，不另维护一份并行政策；最终定点复核及范围见 [IR 报告](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md)。没有实现或实测结果。各题研究答复是选择来源，旧初评、旧规则与演进记录不覆盖本文件的现行条款。

## 1. 请求准入与唯一身份

以下落实 John A／John B 对 B1 已接受的修复方向，最终由 John B 按实际稿件复核。

- Web 管理／查询入口使用登录 Cookie，程序入口使用用户绑定 Bearer；不能因一种认证失败回退到另一种更宽的身份。
- 匿名登录 POST 使用独立防护：服务端只接受精确等于部署 scheme／host／port 的同源 Origin、`application/json` 与固定 `X-RAG-Login: 1`，CORS 关闭；missing／null／跨源 Origin、简单 form 或缺固定头均403拒绝且不创建会话，不以前置会话或会话 CSRF token 阻断首次登录。成功旋转会话并绑定 CSRF token，由受控且不缓存的登录响应交前端内存；重载后可经同源、当前认证的 no-store context GET 取本会话 token，不放 URL 或持久缓存；已有认证的 Web 写请求继续校验同源 Origin＋会话绑定 token。技术真源是 [C5 身份安全协议](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:79)。
- 同一受保护请求同时携带本应用的登录 Cookie 与 Bearer 时，整请求拒绝 `AUTH_CHANNEL_CONFLICT`，包括二者属于同一人的情况。其他无关 Cookie 不参与该判定。程序客户端不携带 Web 会话；浏览器程序调用示例须明确省略登录凭据。
- 认证后从服务端取得用户身份和渠道约束，不信请求体提供的用户、角色或权限。Web／程序 API 共用业务授权，程序动作还必须在只读白名单内。
- 客户端显式选择的空间、知识库与文档在查询向量化、检索和生成前逐项验证；任一越界、撤权、不存在或不属于所选上级，整请求失败，不静默缩减对比对象或查询范围。对无权／不存在资源统一返回资源不可用，不暴露其标题、数量或是否存在。`kb_ids` 必须是非空、无重复的显式集合；界面“全部有权库”先解析为本次实际列表，不使用省略范围代表无条件全库。
- 请求接收后的授权、上下文使用和答案放行检查沿用原规则；查询、引用、下载、历史、重放均不能复用旧授权结论。

## 2. 请求身份、配额和容量

来源：[Mary M1 TR／TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/answer.md)、[同题追问收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/followup-answer.md)、[官方源码依据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/evidence.md)。参考项目的先查后记、request_id 或 chat_record_id 不构成本项目所需的完整并发／防重保证。

### 2.1 三本账与容量受理

| 账 | 计量和唯一效果 | 不得混同 |
| --- | --- | --- |
| 原件容量 | 空间内各保留版本原件字节＋在途预留；当前／历史／候选／保留失败候选／清理中原件都计，同内容不同版本分别计 | UI 称“原件容量”，不是数据库、向量、图片与临时文件的总物理占用 |
| 产品问答次数 | 空间＋受理上海日期；每个逻辑操作只发生一次预留及一个终态结算或释放 | Web／程序 API 共用，正常不足／澄清／冲突仍是正常结果 |
| 外部实际调用 | 每个 call_id／attempt 记录发出与已知状态、供应方 request_id、用量及费用或待核对 | 产品失败不扣次数，不能抹去供应方调用；未知不填零 |

- 原子条件预留 `used_bytes + reserved_bytes + accepted_bytes <= limit_bytes`，不足整份拒绝；批量逐文件独立受理和返回，不回滚其他已受理文件。
- 更新须保留旧版并为新候选完整预留，不先抵扣旧版；满额时明确容量不足，不能以替换为名先删旧版。配额下调到已用／已预留之下，只阻止后续预留，不撤销已受理操作；合法查看、校核和删除仍可执行。
- Web 每文件先建 operation_id／候选及预留，再上传到该候选。实际流量逐段核对声明／预留；未知长度先预留单文件上限，超限立即中止。网络重传沿用候选，完成后同 hash 返回原结果，异 hash 冲突；未完成重传先 fence 原上传 attempt 并清其暂存，不自动新建版本。
- 原件落盘、校验并登记后在 PG 事务中预留转实占；失败若保留原件供重试，仍计占用。临时资产或已删除原件确认清完后才释放，清理失败不释放；状态改变不能重复计入／归还。
- 文件系统与 PG 不构成一个原子事务：受控临时路径、原子重命名、hash／资产清单与账本阶段用于恢复。崩溃后只能登记已校验且仍属当前有效候选的资产，或清理后释放，不能凭空把文件登记和 DB 提交当成同时成功。
- 解析、图片、向量、PG、原 ZIP、临时与备份不计原件配额，但受独立磁盘低水位、阶段写入预算及解包字节／文件数保护。阈值由实施预检登记为必填生效配置，未知时不宣称无限容量；磁盘不足显示可识别失败，不破坏旧生效版。

### 2.2 三种请求身份

- `request_id`：每次 HTTP 尝试的诊断标识；可与同一逻辑操作对应多个尝试。
- `operation_id`：服务器持久化的逻辑问答／对比操作。保存持有人、空间、能力、原受理日、状态、截止时间、执行快照、答案依赖和计次终态。
- `Idempotency-Key`：问答／对比 POST 必填，Web 自动生成、程序调用者提供；网络重传不得自动换 Key。唯一域为持有人用户＋空间＋能力＋Key 摘要，均非空。

客户端规范输入 HMAC 覆盖问题、明确目标、会话／轮次及显式参数；同 Key 换输入返回冲突。首次受理另固定执行快照：模型、索引／文档版本、检索与合并配置；平台默认配置后来改变，不暗中重跑原操作。HMAC 记录 key_id，旧校验键保留到对应有效期结束；缺键为可识别配置失败，不能当成新操作。

| 操作状态 | 同 Key 的响应 | 执行与产品次数 |
| --- | --- | --- |
| reserved／running | 202＋operation_id／受控状态地址 | 一个有效 claim_token／attempt；不再执行或重复预留 |
| succeeded | 重新鉴权和校验依赖后重放原结果；`replayed=true`，返回原时间／版本 | 不新检索、生成或扣次；旧版本按历史核验规则，不冒充新查询 |
| failed／failed_unknown | 返回原终态及错误，未知调用成本可见 | 不重新预留或付费；用户显式重试使用新 Key |
| 过期 | 410，不能默认为新提交 | 不执行、不预留；用户明确创建新逻辑操作才重新受理 |
| 同 Key 异规范输入 | 409 | 不执行、不改变原状态 |

每次状态读取、成功重放都重新检查当前账号、凭证、原目标与答案依赖；失权／删除后不返回原答、不自动再生成。被替换但合法保留的旧版属于原操作回看，必须标示原版本和原完成时间。

实现初值：Key 使用 UUIDv7；首次出现校验生成时间不早于 24h、未来偏差最多 5 分钟，已有操作按受理后 24h 限制重放；Key 摘要／HMAC／终态／日期最小墓碑保留 7d。墓碑删除后仍依据 Key 时间拒绝过旧值，不能变成新提交。数值是受托可调初值，不是效果或容量成绩；改变期限须同时保持“过期不执行”不变量。幂等表不复制私有问题／答案全文，仅存受控结果指针与必要元数据。

### 2.3 生成操作与崩溃恢复

执行问答／对比能力前短事务创建操作并条件预留；`已结算 + 预留 < 日限额` 才可受理。正常完整答复结算 1，含服务器确定性模板返回的合规零候选不足，即使没有调用 LLM；纯检索零结果不扣问答次数。受理前拒绝或业务依赖／期限／结构／权限失败释放预留，真实调用照记。

API 启动时扫描一次，此后周期轻维护扫描 PG，不增加服务。操作保存 hard_deadline、lease_until、claim_token、attempt，续租不可超过硬期限。恢复器只按当前代次条件终止过期操作并释放一次；完成提交必须同时满足 running、期限未到、租约有效、token／attempt 匹配。结果、依赖与计次终态同事务提交；迟到执行者不得改成成功、再扣次或创建重复历史。

业务成功以校核、当前权限检查通过后，结果＋依赖＋计次原子提交为界。HTTP 回包丢失或之后断网不回滚已完成成功，客户端可同 Key 重放；这不同于业务超时。成功后撤权／删除拒绝重放，但不撤销原成功结算。跨日终态失败同 Key 仍只回失败，新 Key 才按新受理日创建操作；不承诺网络发送与撤权全局原子。

必须唯一／条件更新：空间＋日桶、逻辑操作 ID、用户＋空间＋能力＋Key 摘要、逐文件 operation_id、版本＋阶段＋代次、call_id。具体 SQL 和索引在实现时落地，但不得更改上述业务唯一性与终态效果。

### 2.4 上传意图的期限与终态

来源：[第二轮Mary R2-M1 TR／TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/answer.md)、[原Mary追问收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/followup-answer.md)、[上传身份最终整合](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/integration-note.md)、[源码与官方依据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/evidence.md)。本节覆盖尚未创建worker执行任务的上传预留，不用任务lease假定它会自行消失。

- 建候选即保存upload_state、created_at、upload_start_by、首次started_at与upload_hard_deadline、attempt/token/lease、writer_owner、不可复用asset_prefix、预留字节及唯一quota_transition_id。`awaiting_upload → uploading → original_committed`是成功路径；到期/放弃为`expired/cancelled`，字节释放另有`cleanup_pending/blocked/cleaned`，不能用业务终态冒充清理完成。
- 保护初值：创建后15分钟内开始；首次开始后绝对总时限30分钟；无进展60秒；续租10秒/租约60秒；维护扫描30秒一批100条。DB时间判租约/截止，进程用单调时钟限时；心跳、零字节、重传或新attempt不延长原绝对期限。数值可调、未实测，受理时固定为快照。
- PUT开始、完成、显式放弃和过期扫描使用同一KB/候选短锁和条件状态；开始前检查当前维护权、父级、guard、截止与预算。完成提交再次核验attempt/token/lease/期限、父级和hash/长度，在PG同事务登记原件、预留转实占并创建任务。过期先胜则迟到完成拒绝/清理；完成先胜则扫描不能再释放已转实占。
- API启动和周期扫描都能终结从未PUT/永久半传的意图。已fence的expired/cancelled/discarded不再有发布资格，不永久阻重建；尚未实际清完仍占原件字节/物理预算，重建另受真实水位与阶段预算约束。无写入者且证明无资产才可立即释放；否则按§2.6停写/清理。
- 失败但保留供校核的候选不因上传TTL自动删除，当前维护者可重试或显式废弃；待核对上游也可显式废弃本地候选，原调用unknown独立保留、不继续获得写资格。任何过期/放弃后的原上传逻辑ID只返回原终态，不悄悄重建候选或预留；用户明确新上传才用新ID。

客户端每文件预生成UUIDv7 `upload_operation_id`，它就是POST候选创建Key，不另要求一份header Key；唯一域为用户+空间+KB+Key，绑定原规范输入摘要/版本（声明长度、可选客户端hash、类型、业务参数及替换目标）。首次Key时间不早于24h、未来最多5分钟；受理后24h内重传，最小终态墓碑7d，清除后按Key时间拒旧。服务端candidate_id/version_id为资源ID；PUT/GET只指已存在候选，未知/已过期ID永不创建资源。操作窗口到期不删除成功版本/历史原件/引用，不归还仍保留原件的实占。

取已完成原结果优先使用已认证GET，不带文件体，返回原candidate/version/hash/实际字节和replayed；它不声称校验另一份文件。实际带体重复PUT须先有当前维护权、仍在操作重传窗口、原记录存在、规范参数未变及有界上传验证槽/时间/字节预算：声明不同可早拒，声明相同仍须实际流式hash及长度匹配。最多读取原记录实际字节，上限外立刻中止；相同才重放原成功，不新建版本/预留/写原件，不同409。验证初值120秒且计入上传槽1；若框架会暂存先取得等量物理预算，预算不足拒收并给受控GET结果位置，不无预算接收整文件。

### 2.5 每次外部派发与迟到成本账

所有外部传输共用本节，包括纯检索的query embedding、文档/重建分批embedding、问答、图意、MinerU申请/PUT/轮询/下载。`call_id`标记一次可能的传输，不等于供应方保证的幂等键。HTTP/SDK自动重试和自动重定向默认关闭；允许的有限显式重试每次新建call_id并重新过资格门，不能在适配器里暗增费用。解析结果未知继续查原任务，不能按普通网络重试重交解析。

| 顺序/状态 | 持久行为与故障结果 |
| --- | --- |
| prepared | 在短事务内核当前身份/动作/资源（用户查询）或库任务资格、epoch、lease/deadline、attempt/token、取消/墓碑、guard及预算，先持久call_id和意图；DB不可用/守卫失败不派发 |
| may_have_sent | 临近唯一传输派发再次短事务复核并条件标记，提交后才允许发送一次；该行恢复后不得重发。提交后进程可能尚未发送，仍保守为可能已发 |
| responded/known_failure | 保存可得供应方ID、状态、usage、币种/费用及依据、实际时间；调用失败不抹账，缺usage/计价保持NULL+unknown |
| unknown | 可能已发但无确定响应；有已知ID按受控原任务查询，无ID待核对；不能记0或因业务已失败就重新派发旧call |
| not_sent | 仅prepared且受监督传输者确认从未获准/从未派发时可证明未调用；不能把may_have_sent无响应推断为not_sent |

call至少关联归属operation/job或纯检索执行上下文、持有人/空间、用途/阶段、attempt、epoch、执行配置指纹、request_hash、派发/响应时间、供应方ID、usage_status、费用来源和核对状态；不复制正文/密钥/签名URL到普通账/日志。纯检索无生成逻辑操作与产品预留，但仍有持久执行上下文和有限deadline，不能成为无守卫外发入口。

业务fence与成本事实分离：已经发出的响应在操作失败、候选删除、旧attempt或旧epoch后到达，可由受控账本入口按唯一call_id幂等追加可验证的供应方ID/usage/费用事实，不改业务终态、配额、会话、来源、候选、lease或guard。重复同事实无操作；冲突事实保留双方来源并标需核对，不任意覆盖；旧执行者无权借补账接口写业务数据或新建后续调用。供应方仅给估价/无账单时明确区分，不包装成实付账单。

**最后守卫与网络发送不是原子操作。** 在may_have_sent提交后暂停的传输可能在取消/失租之后才到厂商；已到达请求仍可能执行并收费。本项目阻止失效后获得新的阶段派发资格、盲重发和业务发布，不承诺取消提交后零字节/零费用。取消/超期后的真实调用继续记录unknown或补账，不以“应当未发”归零。

### 2.6 物理写入者、清理屏障与磁盘保护

每个版本/attempt/stage使用持久登记的唯一prefix/asset_id，禁止不同attempt共享可写目录、覆盖固定“当前版本路径”或复用旧prefix。原件/已发布来源不可变。prefix在启动写入者前登记，逐文件资产清单带hash/bytes/用途/归属/清理状态；文件已落盘但逐文件登记未提交时，恢复仍能按prefix发现孤儿。

2026-10-16用户明确要求增加异步任务并发上限，覆盖此前“整文档单处理槽”的技术起点：文档worker使用一个有限调度控制线程及独立心跳，全系统doc_active_job与external_async_task两个本地gate各默认4、可配置1–4，均所有账号合计最多4；另保留单本机下载／解包／校核／embedding重处理阶段槽1。doc_active_job在PG条件领取开始处理时占，queued不占，业务终态／到期fence同UoW一次归还；远端task组件在submit may_have_sent同UoW领取，业务失败／取消／重启仍占unknown，可信task终态的唯一release才同时归还本地taskgate及账号／用途本维。已受理远端等待只保留PG原ID、fence／原deadline与permit元数据，不持Session／正文缓冲，不为每个pending创建线程；submit获accepted且child完成本次传输、关闭FD并停止后返本地物理阶段槽，task组件继续占，调度器可提交下一job，使已核额度内最多4项远端工作真实重叠。单次HTTP／CPU／写入仍由本地槽串行；每轮每活跃job最多一个到期可执行阶段，due poll不被新submit无限压后，未到期不忙轮询。有效task并发取本地配置、已核真实账号总池／用途限额和已验资源界的较小值；未知不派发，4不是账号额度或4GB成绩。

阻塞外部传输／文件写入仍使用每物理执行槽一个本机受监督、有绝对期限且可等待停止的子进程；每个外部call的发送child必须退出后才能封口，同有效attempt内的child复用只限不持旧call发送能力的其他阶段，跨attempt不复用。上传初始并发1；API／框架／网关的缓冲、暂存同样纳入清单／预算，不留未登记的第二写入者。子执行者不自主串后续阶段、不持业务DB写资格；控制器每阶段重新过§2.5资格门，以有限IPC／受控暂存收结果和补账。超时不能只丢弃Python线程引用并宣称写入已停止。P0分别以任务池1和4验证满池poll、公平推进／取消／unknown／恢复、账与全部并存资源，未满足不启用对应并发；不增加常驻队列或外发代理服务。原job的2h绝对期限包含排队、远端等待和重试，不因调度释放本地槽而刷新。

清理顺序：①短事务撤销写资格/终结意图；②事务外停止并等待该prefix所有受控写入者/后代退出；③取得稳定生命周期排它锁后短事务复核终态/cleanup_token，再删除暂存、孤儿及无有效引用的资产，确认打开FD已关闭；④同锁保护下PG条件标cleaned并只释放一次对应原件字节/物理预算。各写入者在任何字节写入前先取得该稳定生命周期锁并重新核资格。锁文件放独立受控locks目录，不随资产目录删除/重建，不能只靠PID存活判断。所有入口协作遵守；不承诺隔离恶意本机进程。

不在持PG事务时等待OS锁、网络、子进程退出或大文件删除；取OS锁后开短事务复核。多KB按稳定ID升序；相关业务短事务统一按KB→候选/任务/操作→空间账行顺序取得锁，跨模块实现不得反序。外部等待不持SQLAlchemy Session。无法确认停写、文件清理失败或清理账提交失败时保留占用、显示cleanup_blocked并可重试；删除已生效，访问不能恢复。只有DB业务写意图终结可以解除重建阻塞，物理余账仍须另核预算。

细化全局锁序为：KB稳定ID升序→业务对象固定类别（文档/候选/任务/operation）及ID升序→空间容量/日桶按空间与日期升序→文档本地gate ID升序→provider pool ID升序→call ID升序→permit组件ID升序→asset ID升序，无该类则跳过。架构C4在此前统一加当前授权所需账号／space控制行前缀，只取需要锁且不逆向升级；组件独立释放也本地gate→pool→call→组件。迟到成本只锁call，不持call回取业务父锁／gate／pool。稳定OS锁覆盖可写生命周期，清理取排它锁；没有停写证明保持blocked，不能靠目录暂时为空或unlink成功释放打开FD占用。

原件完整登记/预留转实占/任务创建同事务提交前，上传仍按当前用户维护权检查；合法受理后任务是库的持久意图，提交者退出/降级/停用不隐式取消，当前维护者按既有动作管理。退出/撤库权者不能读改；降级但仍有库权者保留本人受控状态只读，不保留重试/取消/校核管理。worker不增加可登录产品角色；每阶段仍检查父级/墓碑/恢复隔离、candidate/guard、租约/绝对期限及预算。用户问答/对比的派发和输出仍复核当前用户/凭证及所有显式目标。

任务保护初值为原件合法受理时固定2h绝对deadline，不从重试/续租重置；云等待最多2h是子上限。每次传输/下载/解包/校核/embedding/图意限时取min（任务剩余、阶段上限、调用剩余），单传输初值120秒并按实际供应方协议锁定connect/read/total配置。到期上游仍running可见待核对，不再派发新业务，不把本地终止当云端已取消。

API启动及周期维护扫描过期上传/任务/guard、未结调用和清理记录；逐项按当前token条件处理。普通重启不换epoch、不因新boot_id就假定旧进程已死；确认旧写入者退出/取得稳定锁后才清理并复用执行槽。若不能停止，阻断该槽并由运维停止所属受控进程/容器核对；不伪造cleaned。清理重试初值30秒起、最多间隔5分钟；TERM等待5秒、KILL再等10秒仍未确认则blocked，均为未测可调初值。

物理预算包含PG/WAL、向量、原件、ZIP/解包/图片、框架暂存和备份。每阶段写入前预留有硬上限的预算，流式核实际字节；解包限制总字节/单项/文件数，拒绝路径逃逸/符号链接。必填生效配置包括磁盘低水位、PG与清理控制余量、阶段预算和备份独立空间；缺配置不放行新写，不宣称无限容量。触发压力时拒新上传/候选/重建/付费阶段，保留权限允许的本地读、取消、墓碑登记和清理；磁盘已被外部进程耗尽而无法提交时进入维护隔离，由运维释放安全临时/扩容后恢复，不能假称任何满盘状态都仍可写墓碑。不得提前删仍供有效操作/历史引用的旧来源腾空间。

### 2.7 原任务到期后的有限核对与本地继续

来源：[原Mary对B定点反例的补问收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/followup-2.md)。§2.5派发门按执行用途检查相应上下文，不要求只读核对复用已过期业务job的lease/deadline。

当前有维护权者显式继续核对，创建独立reconciliation_id，绑定原job/candidate/call、当前操作者/空间/KB/epoch、原持久已知供应方账号/配置与batch/task ID、用途白名单、lease/token和本次hard_deadline。初值整次120秒、最多一次已知任务状态读取；仅实际接入协议有独立费用查询接口时可另查一次原调用费用，否则保持unknown。重传/重启沿原上下文和deadline，不自动生成下一轮核对。动作使用UUIDv7 action_key按用户+任务+动作幂等匹配，沿24h重传/7d墓碑/时间拒旧，不混用原上传Key或原job attempt。

核对受理/每次派发/放行都复核当前账号与维护权、epoch、父级未删/未隔离、已知ID与配置归属、该上下文有效lease/deadline、槽位/预算；仍按每次call intent只派发一次。无原ID不猜data_id、不接受客户端任填上游ID、不换供应方账号。状态GET或程序只读凭证不能隐式创建核对上下文/外传。只读核对不取得重建写guard，不改原job终态/2h截止/attempt/预留/候选发布资格。

允许输出仅为经校验的running/ready/failed观测、时间/关联和可信成本事实。禁止下载ZIP/正文/图片、解包/向量化/发布、续业务、新申请或PUT；ready只记独立观测，不把临时URL直接外放。超期仍待核对，下一次须当前维护者显式新动作；在途费用继续按unknown边界留账。

真正继续处理须另行显式新本地job/attempt及新deadline，关联原核对/原调用；若旧候选已过期/取消/废弃则新候选，绝不复活旧创建Key。新受理重过当前维护权/父级/epoch、KB guard、候选有效性、配置/完整性、原件/物理预算和受监督槽。可复用仍保留、已验证且归属/配置兼容的原件/阶段产物；仅ready/URL不算已验证。需获取结果时在新job资格下下载原已知任务并校验，不自动重新申请解析/PUT。必要资产已清/不可取则明确缺失，需重新解析另走知情显式重交，费用不重复累计旧调用。原业务截止不因核对或继续动作刷新。

## 3. 索引、对比结果及校核交互

来源：[Mary M2 TR／TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/answer.md)、[同题追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/followup-answer.md)、[两项目证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/evidence.md)。以下将关键不变量集中记录，详细结构／交互分别使用该题的 schema 与动作契约。

### 3.1 逐库 profile、索引代和写入守卫

每库活动索引代绑定不可变 embedding_profile：供应方、端点／地域、模型与可得版本、维度、query/document 处理／前缀、归一化与距离策略。密钥引用可轮换，不因此改变向量空间。默认配置编辑只影响新库或显式重建，不能就地改旧库 profile。

不同库的兼容指纹须相同才能同次检索；不要求 profile_id 字面相同，不只按模型名比较。任一不兼容整请求拒绝 `EMBEDDING_PROFILE_INCOMPATIBLE`，不静默漏库、不融合不同向量空间分数。

不可变的是 generation 身份、profile 和初始发布快照；普通上传／替换可在同活动 profile 下原子发布合格块、向量与文档活动指针，并递增 docset_revision，不要求每上传一份全库重建。

| 阶段 | 有效行为与条件 |
| --- | --- |
| 接受同维重建 | 同 KB 短锁下，检查仍有执行/发布资格的未终结写意图（候选、有效在途上传、排队／运行／待核对任务），存在则拒绝，不先留悬空 guard；已过期/取消/废弃且fence的清理余账不算有效写意图，但继续计容量并占物理预算 |
| 取得 guard | 创建候选 generation，固定 docset_revision／活动文档版本集及 owner_job、attempt、token、lease；新上传也在同锁下先检查 guard，再登记预留／意图，避免并发漏检 |
| 重建执行中 | 旧索引继续读；上传／替换／重处理整体拒绝，不能暗排队。显式删除仍先墓碑、递增 revision、废弃候选并释放所属 guard；旧索引检索／输出仍过滤墓碑 |
| 失败／取消／租约过期 | 恢复器条件匹配 KB＋任务＋attempt＋token 后释放 guard；物理候选清理可异步，不能因清理未完永久阻写；旧 attempt 无权解新 guard |
| 发布 | 同 KB 锁下核对有效 attempt／lease、guard 归属、候选完整、父级与文档未删、revision 和覆盖活动版本集未变、向量数量／维度／profile 正确，才切指针并解锁；失败废弃候选，旧索引保留 |

切代后在途操作使用已钉住的旧快照，不暗中重检索新代；旧块／向量保留至对应操作终态或受理时固化的 hard_deadline，超期失败。保存的答案／历史须另有持久 evidence_snapshot（本轮实际片段、文档版本、原件哈希、来源定位与 ID 映射），不依赖旧向量继续存在；受控原件／定位资源按原版本历史核验规则保留。向量垃圾回收不能破坏已保存引用，实际占盘仍受水位约束。

首次接入验证后锁定部署维度 D，以迁移创建 vector(D) 存储。同 D 变更可按上述候选重建；不同 D 的在线请求拒绝 `EMBEDDING_DIMENSION_MIGRATION_REQUIRED`。变维须维护窗口、备份、显式 Alembic 创建隔离 D2 存储，完整重建受影响库并验证查询／授权／引用及失败退回后切换；保留旧存储供退回，应用不自动 DDL，不承诺任意维度在线双索引。维护期间停止受影响查询与写入，仍可登记删除墓碑，恢复服务前重放。

### 3.2 对比输入、四态和最终证据

权威细节与可解析示例见 [comparison.v1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md)。初值：对象 2–4 个文档、条件 1–6 条、单条 256 Unicode 码点、合计 1024 码点、子查询不超过 24；均可配置、未实测，前后端从同一有效配置读取。空值、重复对象／条件、越限／越权在外部调用前整拒，不截断伪装完整。

对象使用唯一 object_id＋document_id，条件使用唯一 condition_id＋text；受理后固定每对象的活动 doc_version／generation。每个对象×条件恰好一格：满足／明确不满足均需至少一个直接证据，冲突需不同且互斥的双方证据集合，不足允许空证据但须缺口说明。v1 每对象指一个所选文档版本，同格冲突须该版本的双方证据；不同对象差异不是冲突，跨文档同事实冲突继续由普通问答报告双方，不取消冲突验收。

检索沿用既定固定名次轮转，最终全请求最多五块。evidence_catalog 必须对应模型实际看到的最终候选，可含未被结论引用的候选，不能含额外块／邻块／全文。SM-2 按这些实际片段直接支撑的原金标事实计数；SM-3 只按实际结论与引用语义支撑计数，目录存在不计分。

最终零候选时服务器不调用答案模型，确定性返回 completed／insufficient，所有输入格保留、evidence_ids=[]、reason_code=NO_CANDIDATES；这是正常问答／对比结果计一次，纯检索零结果不扣问答。依赖错误不能伪装零候选。模型缺格、越界引用、非法四态或结构错误属于 ANSWER_VALIDATION_FAILED，整答失败、释放预留，不自动追加模型修复或静默降为正常不足。

### 3.3 最小校核与来源回看

权威动作矩阵和探路见 [M2 UI 契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md)。页面分开显示“当前生效版本／候选版本／任务”，索引重建另显示活动 generation 和目标 profile；不能用候选“处理中”覆盖旧版仍可查询的事实。

- 普通文档程序校核后自动发布，不增加逐份人工审批。首次 partial 只用通过且可定位范围并提示不完整；不完整替换候选不覆盖旧版。
- 当前有维护权者可对照原件、提取／结构、错误范围，按状态重试、取消、继续核对或知情显式重交。修正限修订原件重新上传，以及合法元信息／解析参数产生新候选；不内建通用 OCR／富文本编辑器，不原地改历史来源。
- PDF 有可信 bbox 则在服务器生成并校验的页图上高亮，无 bbox 但有页则该物理页图＋准确片段并标无区域高亮。DOCX／TXT／MD 显示真实章节／块／字符位置＋准确提取片段＋受控原件下载，标清原件与提取内容，不部署 Word 服务、不编页码。
- 定位／哈希／资源缺失要显示可识别错误，允许时下载原件人工核对，不猜位置；缺必要定位的候选不得假装通过。引用、页图、片段和下载每次重新授权／检查归属与墓碑，不用上游临时 URL 当可信用户入口。
- 原件一律受控 attachment 下载，不 inline；服务端生成安全且有界的 Content-Disposition（含 fallback、UTF-8 filename*，剔除 CRLF／路径／控制字符），按已验证 PDF／DOCX／TXT／MD 类型设置白名单 MIME 并加 `X-Content-Type-Options: nosniff`，不透传上游类型或头。inline 仅服务器生成并校验的 PNG／JPEG 页图或裁图；文本、MD、提取 JSON 用 textContent 或清洗渲染，禁止 HTML／SVG／上游 PDF 等主动文档 inline。精确 MIME、字段和资源响应真源是 [C7 格式分派](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:117)。这不新增主动内容预览能力。

### 3.4 外部能力探路前置

MinerU 主路的图文结构解析不等于已能理解图意。M2 选定公开 TI LM2596 手册连接图作为预探选材；原件、哈希、定位和必须依靠连线判断的金标事实须在实际调用前固定，目前没有制作金标或运行服务。

先检验 MinerU 产物／来源；图意不足只触发独立视觉 API 验证，将通过校核的说明绑定原图和定位后作为受控块，回答仍受 K=5。具体视觉型号与账号实际接入时选择。若仍无可核验依据，阻断 SC-4 完成，不更换 MinerU／默认重做本地 OCR，不降 SM 门槛或用平均分掩盖失败。

### 3.5 查询协议硬界与业务受理限制

来源：[第二轮Mary R2-M2 TR／TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/answer.md)、[官方与固定提交证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/evidence.md)。H为部署级协议安全硬界，B为新操作可调业务上限，M为实际模型适配器限制；新请求取三者交集，不能以调大B绕H/M。以下数字均未测，是受托保护初值。

| 层/入口 | 有限约束 |
| --- | --- |
| H：JSON查询/控制请求 | application/json、UTF-8、Content-Encoding identity；流式实际body≤1MiB、请求头≤16KiB，不只信Content-Length；边读/解析边限界，不无界解析后才校验 |
| H：结构 | 单根object、深度≤8、节点≤8192、每object键≤64、每array项≤1024、每string≤65536码点、所有string合计≤131072码点；拒重复JSON键、非法UTF-8/孤立surrogate/非有限数字、未知字段/版本；目标ID为1–64 ASCII字母/数字/下划线/连字符 |
| B：retrieval.v1/answer.v1 | 显式库≤64、可选文档≤128；question≤4096码点；型号/版本/环境/日志/参数等白名单字符串合计≤16384码点；单层结构，不以拆字段绕合计；纯检索同样限制 |
| B：comparison.v1 | 沿原2–4文档、1–6条件、单条256/合计1024码点、最多24子查询；不删条件/对象，不变四态证据语义 |
| 辅助历史 | 只取最多最近2条当前仍有权的用户问题，合计≤2048码点，整条纳入/剔除；旧答案/旧证据默认不送最终模型，不算新证据；指代不明则澄清 |

本H字节/编码边界不套到原件二进制PUT、下载、MinerU ZIP或模型上游响应，它们按独立文件/解包/适配器输入输出字节预算保护；原20MiB文件起点不被1MiB JSON限额取消。配置发布/元信息列表采用有限分页；模型不接收全部scope列表，只接必要对象/条件/证据映射，其动态schema和提示内容仍计token。

准入顺序：有界协议检查→渠道/当前身份与有限显式目标授权→已有Key按原normalization/schema和完整输入指纹匹配重放→仅新Key校验当前B/M、profile/guard、会话父轮次和执行配置→按§3.6对已知必超早判或固定为允许的“检索后分支”，取得查询逻辑槽后创建操作并原子预留，再检索/外传。对新的过大目标集合可在授权遍历前按H上限拒绝；不能先对无界列表查库。旧Key不因B下调重跑/重预留；紧急H下调可413拒这次大POST，仍可用本人已知的受控GET operation恢复，不返回未认证操作ID或逼客户端换Key。

仅比较条件等原有字段按其已登记NFC/去首尾空白规则规范化；question/日志及其他当前输入默认保留完整解码值，不新增全局NFC/trim/空白合并或换行重排，question全空白仅拒空，不改有效内容。HMAC按受理规范版本覆盖完整输入，不只覆盖被裁成的提示；当前输入绝不为预算暗删。

### 3.6 实际模型预算、实见证据与失败分支

本节按[原预算Mary同题追问收口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m2/followup-answer.md)合并，补正仅记录context_length的不足，不宣称实际千问型号/账号已验证。

每用途profile独立登记：供应方/地域/端点/型号/可得版本或alias、tokenizer工件/版本/hash、完整消息模板及SDK版本、prompt/schema/序列化指纹、计数依据/模式、I_max输入、O_max输出、C_max总上下文（适用时）、输出参数语义、思考关闭方式或有限R_think、封装/安全余量、请求/响应字节上限；embedding另有每条token、批条数/总token（若供应方有）、query/document用途及D。未知不填无限。图意用途另核实际图像输入/分辨率/字节及token规则，不从文本或问答型号推定。

P0优先选择已核支持非思考的千问模式，仅显式system/user文本、普通text响应，JSON要求写在可见提示，本地严格解析。n=1，tools/web/code/自动历史/内置检索、SDK暗重试、额外模型改写/修复均关闭；首版不依赖隐藏json_schema注入。实际模式的结构成功率仍须验证。

计数针对最终完整消息序列（含role/BOS/EOS、system、schema、动态白名单/模板），用匹配端点的精确计数器或有官方依据的保守上界。计数器只算content或另一产品/端点不能当完整计数；不凭字符除常数、样本平均或20%猜测隐藏封装。无需厂商私有权重/完整实现；可选择同一千问路线内可核的模式/计数能力、登记有限封装上界并收紧新受理范围。仍未证的候选为budget_unverified，只阻其生成阶段，不推断全部千问不可用。供应方若实际提供可用计数接口，核产品/端点/鉴权/计费后才选，不用OpenSearch计数文档冒充DashScope保证。

令S为完整system/schema/必要映射，M为当前完整用户输入/全部对象条件，H为合法有限用户历史，E为最终最多五块实见片段；对完整序列计算I，必须分别满足I≤I_max、R_answer+R_think≤O_max，若有总限制则I+R_answer+R_think+margin≤C_max。余量不能掩盖完全未知的framing。优先关闭思考，不能关闭时须明确有限且语义可靠的R_think，否则不选该模式。profile/SDK/alias或计数偏差超界时停止该profile新生成阶段，重核新配置，不给旧操作暗换模型重跑。

输出R证明的是完整规范紧凑JSON载荷有空间，不保证随机模型不乱写。按本次实际ID、全部格/有限数组、最大合法四态分支/证据字段、字符串上限和规范序列化字节上界，再以该tokenizer已证上界换算；不把字节当实测token或把系数凭空设1。可选择UTF-8非ASCII直接编码、拒非法surrogate及TAB/LF外C0控制字符，此时一个合法码点的规范字符串编码至多4字节（需转义字符至多2）；仍计全部结构/ID/分支。R不按平均长度、全不足单模板或省格推算；128码点紧凑档也不保证任意小模型能接24格。首个可用profile须在P0证明四场景最小完整有效载荷可容纳，并发布实际可支持输入/矩阵范围；必要事实表达不足须调新档/换同路线容量充分的已核模式后重验，不降SM。

首版无额外LLM改写/压缩。普通query embedding为固定模板+完整当前question+全部适用条件/日志+允许的完整用户历史；比较各路为固定模板+完整本条condition+允许辅助，文档对象由服务端过滤，不塞全文或全scope。每个实际字符串先展开/计数/留hash；不暗切成多个查询或删日志。每个query/document块和每批都过实际embedding限额，query批1/串行；文档超长按来源/结构分块形成候选，不原地改历史。历史只整条剔除，显式指代不可解就澄清，旧答/旧证据不进五块之外。

新Key通过H/B、当前授权、兼容/guard/父轮次、embedding预算与逻辑gate后，分支顺序固定：

1. 若已可靠判定当前M/完整输出R必超选定生成模式，尽早422拒绝、无预留/embedding费用。若生成profile只是未验证/不可用，而embedding已可执行，可以明确固定为“检索后分支”操作、原子预留一次后有界检索；202不是生成能力承诺。
2. 必须成功完成全部已登记子检索并合并后，原始最终候选确实为0，才用服务器完整确定性不足模板，无LLM调用，也不要求LLM最大输出证明。普通模板outcome=insufficient、summary仅缺口说明/fact_ids=[]、facts=[]、evidence gap、clarifications=[]、catalog=[]；比较保留全部格/NO_CANDIDATES。通过本地schema/响应字节和当前授权后正常结算1。检索未执行/依赖失败/子检索未完成不得走此分支。
3. 原始候选非0时必须通过实际生成profile及基础S/M/完整R预算；未证503，已知超限422，终态失败/一次释放，已发embedding成本照记。
4. 基础可容纳后固定原轮转最多五块次序，不换候选/加邻块/全文/旧答。超限先从旧到新剔除整条辅助用户问题；再按第5至第1逆优先缩短原块连续片段，只从尾部删登记段/句/表格行组，表头/单位/型号/适用条件随事实原子组保留。最小原子组装不下才移整块，不用LLM摘要。重算完整I，记录offset/hash/原因与有界正文读取。
5. 1–5块实见证据可逐格正常不足；原有候选因预算全裁成0则CONTEXT_EVIDENCE_BUDGET_EXHAUSTED失败，不能冒充第2步正常零候选。catalog只列实际传入片段及原来源映射，不以同chunk_id整块算覆盖。

length/截断/缺完整终止即使JSON碰巧可解析也整答ANSWER_TRUNCATED；正常终止但缺格/非法引用/生成子契约不符整答ANSWER_VALIDATION_FAILED。只做无语义去围栏/空白，不交草稿、不自动LLM补格或修复，失败一次释放，真实费用/unknown保留，同Key回原失败。

SM-2分子只认实见片段直接支撑的原金标单元，分母不变；调用前拒绝无模型上下文计0，不删题。发出生成后失败，SM-2仍按保存实见上下文如实计，但SM-1仍失败；空/失败事实答的SM-3分母0报N/A并另列失败，不算100%。原24可答/8不足、各场景/关键题/独立权限门槛全部保持，不能把预算失败改成不足题或扩大K。

### 3.7 有限生成载荷与响应语义

公共HTTP envelope有schema_version/request_id/status，问答/比较有operation_id/replayed/原时间/执行快照；模型不生成可信metadata或catalog。HTTP status=completed/in_progress/failed与业务outcome、operation_state分开。GET operation可HTTP200返回原state和安全原error.http_status，同Key终态POST用对应失败HTTP；失败不装成completed/insufficient。

comparison.v1外层仍是原全格四态、reason≤512、引用基数/所属版本/冲突互斥双方。首版生成子契约comparison-compact128要求reason为1–128码点，全部格/字段不减；generation_contract_id及限值在提示/本地校验/受理快照/能力配置一致。模型写超128整答失败，不裁返回值。提高新档≤512须新配置、重新预算与原质量验证，不暗改已受理档位。

普通answer.v1最小生成载荷如下，全部对象未知字段拒绝、码点有限、证据仅本轮白名单。首版answer-compact128将fact.text/applicability、gap/clarification.text收紧为≤128，summary.text≤256；外层上限保留，数组/语义不减。质量不够须显式新档重验，不漏必要事实。

| 字段/类型 | 外层约束 |
| --- | --- |
| outcome:string | answered/insufficient/clarify/conflict |
| summary:object | text为1–1024码点；fact_ids为0–16个唯一事实ID；事实性摘要须指向有直接证据的facts，空事实只可描述不足/澄清 |
| facts:object[] | 0–16项；id为唯一f1…f16；kind为process/material/condition/owner/cause/check/step/parameter/limitation；order整数1–16、同kind唯一/按步骤顺序；text为1–512、applicability为0–256码点；evidence_ids为1–5个唯一当前ID；quantity/conflict_sides显式null或下述对象 |
| quantity | {value_text:1–64码点,unit:1–32码点}；parameter必须非null，其他关键量值同样结构化；范围/关系完整，必要单位缺失进gaps，不补造单位 |
| conflict_sides | side_a/side_b各1–5个证据，双方互斥、并集恰为该fact引用、合计≤5且≥2不同ID；描述同适用条件的相反事实，不自行无据裁决 |
| gaps:object[] | 0–8项，field为上述kind或object_identity/version/environment/log_context/evidence/source_locator；text为1–256码点，只说明用户所求缺口，不补无据原因 |
| clarifications:object[] | 0–4项，同gaps字段枚举、text为1–256码点；只问本任务必要条件，不以条数上限漏必要缺口 |

enterprise限process/material/condition/owner；support限cause/check/condition/limitation；manual限step/parameter/limitation/condition。用户实际问到的流程/材料/条件/负责人、排障适用版本/日志限定/候选原因与检查顺序、手册型号/版本/步骤/数值单位/限制须完整回答或明确gap/澄清；未请求项不强填。定位来自相应catalog，结构合法不代表语义支撑已通过。

answered要求facts≥1、summary引用事实、必要事项齐全且无关键gap/clarification或冲突；insufficient要求gaps≥1，可有有证据的限定事实，不能以未命中判不支持；clarify要求clarifications≥1，不猜缺失型号/指代；conflict要求至少一个有合法双方证据的fact被summary引用，同条件矛盾完整，五块不够双方则不足并指明缺口。facts=0不成为事实回答或SM-3=100%的依据；原人工任务/引用验收继续有效。

budget_snapshot保存H/B版本、generation_contract_id、原规范输入hash、profile/tokenizer/template/prompt/schema/SDK指纹、输出档、I各部/最终总数、R/margin、embedding批计划、原五块次序/实见范围、call_ids/finish_reason/usage/错误；正文放受控业务快照，不复制进普通日志。模型/接口/SDK变化前重核参数语义、计数/完整终止、四态/引用/负例；不把alias不可完全冻结包装成可完全复现。

### 3.8 查询并发与调用限流

全部署retrieval/answers/comparisons共用PG条件逻辑gate，初值active_query≤2、每用户≤1、每逻辑查询subquery_inflight=1，比较最多24路串行、query embedding每批1条。不新增持久待执行查询队列，拿不到逻辑槽即429；此规则替代早期Q4“执行2/等待4”的查询等待初值。已受理操作内部调用可在原hard_deadline内有限等待rate gate，不能持Session等待/另开无界线程；查询总deadline仍以受理快照为准。

逻辑占位、产品预留和真实传输槽分开：租约过期可终结业务并释放产品预留，未确认旧传输者停止不得把其实际执行槽再借出。纯retrieval无问答产品次数，但须有持久执行上下文、scope/epoch/deadline、调用预算和call账，同样过当前身份/墓碑/派发守卫。不能以“不扣次数”绕付费限制。

query embedding全局≤2次/秒、每用户≤1次/秒仅为本地拟定起点，不是账号实况或当前生效额度；每用途/provider的TPM/RPS/并发生效值必须登记有限本地上限并与已核账号限制取较小者，未知不填无限、不派发该能力。生成/图意及将来显式计数或改写调用也不能绕账号调用gate/§2.5账本。文档embedding批次同时满足每条token、批条数/总token（若供应方有此项）、body字节上限，实际SDK不得自动拆批/暗重试。提高并发/批量前重新验证目标4GB、限流和故障负例。

所有可能发送的 grant 持久占 `send_open` charge，领取／send-by 窗口过期不自动退占。控制器须取得本 call 发送 child／全部受控后代已退出、全部传输写及发送 FD／IPC 已关闭、旧 grant 已销毁且不可再授予或恢复的监督证明，再取其后的 DB 时刻 `last_local_send_upper`，sealed charge 从该上界保留完整 W；准入合计 open charge 与 sealed 未满 W，不能只看 send-by、child 读钟、lease、业务终态或重启。无法证明停发则继续占用／阻塞对应维度。精确多维池锁序、条件更新和计量算法只在 [C8 共享 rate gate](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:145) 维护，[R2 派发](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:23) 约束本地监督执行；本地发送窗口不承诺远端到达时间或永无供应方 429。S0 暂停／失联／恢复假件通过后才允许任何真实外发，P0 再核真实接入。

## 4. 恢复与安全放行

来源：[Mary M3 TR／TS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/answer.md)、[同题追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/followup-answer.md)、[恢复动作表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/runbook.md)、[官方依据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/evidence.md)。数据库认证字段、账号 active 和程序密钥状态会随旧备份倒退；清会话不能阻止旧密码重新登录，PG 快照／PITR 也不自动补回恢复点后的安全事件或库外文件。

### 4.1 信任起点与安全台账

部署时独立登记恢复操作者、现行业务受托关系确认渠道及 break-glass 凭据，封存于独立受控介质，不取自恢复 DB。受控维护入口只处理必要身份／归属／稳定资源 ID／墓碑等元数据，不提供业务正文、原件或代登录；平台恢复权限不自动赋业务读权。

停用、成员移除／退出、角色／所有权变更、库撤权、用户密钥撤销、资料／库／团队删除，与业务变更同事务写最小安全台账。记录稳定事件／目标 ID、序号／前摘要、时间、操作者及必要权限元数据，不含正文或密钥；目标 ID 不重用。由现有维护动作将已提交连续区间及认证清单导出独立受控介质，不增加数据库／消息服务或自动外传。台账留存覆盖最旧可恢复备份。

清单可证明来源／连续区间／完整性，不能证明导出后没有发生事件。最后导出至故障冻结是明确 gap，不承诺 RPO=0。只重放可验证区间；缺口由独立身份核验的恢复操作者与当前明确受托的业务负责人，依据外部记录重新确认成员／角色／授权和完整现存资料白名单。负责人不能仅凭备份中的 owner 字段自证；个人空间同样要独立核验本人。已知墓碑／撤权取拒绝优先，不能因重新确认擦除。无法确认删除完整性的库／个人范围保持隔离。

### 4.2 恢复动作与放行

| 顺序 | 必需动作 | 无证据时的行为 |
| --- | --- | --- |
| 冻结／验包 | 关闭业务入口、停 worker 和外部调用，停止／fence 旧写入者；核同 snapshot_id 的 PG、原件／解析／引用资源、配置、密文与分离主密钥、版本及哈希 | 材料不匹配或旧写入者未隔离则不得开放；不调用供应方重新生成缺文件来伪装恢复 |
| 换纪元／封身份 | 新生成至少 128 位随机不可复用 recovery_epoch，记录 cutover；全部旧 Web 会话／用户 Bearer 作废，恢复账号全部 unverified，关闭正常登录／自助取回及旧邀请启用路径 | 不用 backup_epoch+1；旧密码不能换新会话，旧所有者不能自行解禁 |
| 核验／合并 | 通过独立 break-glass 核验受托链，重放已证安全事件、列明 gap，逐账号／空间／库／资料确认当前范围；账号重置密码后才启用 | 未确认继续 quarantine，平台无正文读权；维护入口仍可登记新的撤权／删除并立即纳入 deny 和台账 |
| 旧执行与账核对 | 旧 attempt 全 fence；已成功不重结算，旧 pending 生成终止并释放恢复的预留，原 key 不重跑。已知上游 ID 只有经该范围及查询动作放行后才查；无 ID 为 unknown | 不盲付费重交、不用未知费用填零。当前上海日计次无法核对则该空间冻结新增生成，可信核对或下一上海日才解额度冻结 |
| 逐范围放行 | 核验匹配密钥与现行供应方凭据，按账号、资料范围、业务读／写、外部查询／付费、worker 分别放行；保存确认依据、人员、时间与隔离清单 | 部分放行不称全站恢复；下一日仅解配额缺口，不解身份／资料／凭据隔离 |

普通应用重启／部署读取现行独立持久 epoch，不产生新值；只有备份恢复或明确安全重置产生新随机 epoch。独立控制记录与 DB／运行进程必须一致，矛盾即维护隔离，旧进程不能继续提交。

### 4.3 新操作与恢复后重放

本节是恢复情形对第 2 节重放规则的额外限制；普通重启不改变已受理操作及其 Key 窗口。

认证成功的上下文接口返回本人当前 epoch 与 server_time，供明确的新操作生成 Key。所有问答／对比新受理带 `X-Recovery-Epoch` 和 UUIDv7 Idempotency-Key；缺失／旧 epoch 返回 `RECOVERY_EPOCH_CHANGED`，不预留／执行，不自动给旧排队请求换 epoch 或 Key 重送。恢复后未见过的新 Key 时间不得早于 cutover，故备份后丢失的旧 Key 即使客户端手改 epoch 也不能重新当新单。

恢复点内可确认的 success 只能经受控 GET 在原重放窗口内读取，仍核验当前身份、范围、来源和墓碑，标原时间／版本／日桶，不新检索或结算。窗口外仅可按仍保留且有权的会话历史读取，不承诺幂等缓存无限保存。备份后已丢失的 success／任务 ID 不能承诺恢复其答案或状态。

供应方密文恢复不等于现行调用授权；由当前受托接入管理员确认／重新输入有效凭据并核对 key_id。主密钥缺失阻断该能力、日志不输出秘密；允许已核验范围的本地只读验证。历史未知费用与导出 gap 保留，不从旧低计数推断当日从零重新开放。

### 4.4 恢复演练与记录

首次上线前在隔离环境，从备份后再停用／撤权／撤 key／删除的场景恢复旧点；验证旧密码、旧 Cookie／Bearer、旧 owner、旧 key／epoch、迟到 attempt 均不能恢复访问／发布或重复结算。缺台账尾段、无法确认负责人、上游 ID 丢失和主密钥缺失须可见地保持隔离／unknown；连续恢复同包两次 epoch 必须不同，第一轮新凭据在第二轮失效。

保存恢复点、实际允许丢失窗口、snapshot_id、台账 gap、放行依据／范围／确认人、epoch、账与任务状态及失败记录。备份频率、留存、最大可用备份龄和可接受丢失窗口由首次部署登记，不冒称用户已接受某个丢失时长。备份存在、进程能启动或旧引用偶然能打开都不等于通过。

## 5. 最小接口、页面与实施切片

以下路径和字段为本项目最小联调契约，不声称与参考项目完全一致。正式请求／响应模型、OpenAPI 与数据库迁移按本节实现；精确依赖版本、真实模型和供应方限制在接入前锁定。接口只是渠道，不创造新权限。

### 5.1 入口和能力

| 入口族 | 最小能力／关键输入 | 输出与守卫 |
| --- | --- | --- |
| `/api/v1/web/auth` | 密码登录用独立同源 Origin＋JSON＋固定登录头防护，不要求已有会话 token；本人状态、退出、改密用 Cookie，认证写用同源 Origin＋会话绑定 CSRF token | 登录成功旋转会话／绑定 token，以不缓存受控响应交前端内存；不向前端暴露供应方密钥；登录与退出状态明确 |
| `/api/v1/web/spaces`、团队／成员／邀请／授权入口 | 按 PRD 的平台、所有者、维护者权限执行对应管理；授权输入使用主体 ID 与动作，不信客户端角色声明 | 转让与负责人接管事务性，当前权限为准，必要操作审计 |
| `/api/v1/web/knowledge-bases`、文档入口 | 创建库、资料列表，显示生效版／候选／任务／索引代；操作时校验当前空间和库权限 | 普通使用者没有管理写入口；候选不混进查询 |
| `POST /api/v1/web/document-candidates` | `upload_operation_id`、space_id、knowledge_base_id、可选替换 document_id、显示名／类型、声明字节或未知长度、处理配置版本 | Web 每文件预先生成并保留上传 operation ID；同用户／空间／库／ID 的同规范输入只建一个候选与预留，重传返回同 candidate_id／version_id；异输入冲突，先检查 KB guard 再预留 |
| `PUT /api/v1/web/document-candidates/{id}/original` | 仅当前有维护权者；同候选原件字节，实际流量与摘要校验 | 上传是本后端受控地址，不把 MinerU key／上传签名交给前端；阶段、attempt、清理与重复规则按第 2 节 |
| `GET /api/v1/web/document-candidates/{id}` | 当前有库维护权者读取原上传意图、候选、deadline、hash/字节、任务ID（若已创建）及清理元信息 | 无task的awaiting_upload也可见；不带文件体；只读原结果，不新建/执行；一般使用者的本人任务只读仍走task入口 |
| `POST /api/v1/web/document-candidates/{id}/abandon` | 当前有库维护权者显式放弃未发布候选，包括从未PUT、半传、保留失败或待核对 | 条件终结/fence写意图；可见清理中/失败并重试清理，不删除旧生效版；重复返回同终态，不假称远端已取消 |
| `GET /api/v1/web/tasks/{id}` | 本人且仍有库读权者可读受控状态；当前维护者可读其维护范围必要任务/错误详情 | 降级但仍有库权者保留本人状态只读，不暴露他人任务/私有运行日志；退出/撤库权/父级不可用拒读 |
| `/api/v1/web/tasks/{id}` 的动作入口 | 当前维护权者按状态重试／取消／继续核对／知情重交；重交显式确认潜在重复费用 | 写动作另校验任务/候选/父级/guard，原上游关联不抹掉；program入口不开放动作；到期后核对不刷新旧任务deadline |
| `POST /api/v1/web/tasks/{id}/reconciliations` | 当前维护者、action_key、只读核对原持久已知任务 | 新有界核对上下文，不能续活原job/下载/发布/新解析；受理/派发/放行当前授权 |
| `POST /api/v1/web/tasks/{id}/local-continuations` | 当前维护者、action_key、显式依据原已知结果继续本地处理 | 新job/attempt与deadline，候选无效则新候选；重过guard/预算/完整性，不盲重交上游；不足返回具体错误 |
| `/api/v1/web/credentials` | 本人创建限定空间／库／只读动作／到期，列元信息及撤销 | 明文仅创建显示；所选 scope 必须当前有权，持有人／团队所有者撤销按 PRD |
| `GET /api/v1/{web|program}/context` | 已认证本人上下文；Web 返回身份／空间，程序仅凭证许可范围，附有效输入限制、epoch／server_time | 元数据不赋新权限；恢复账号／资源未核验仍按第 4 节隔离，不能借接口重启旧操作 |
| `/api/v1/web/platform` | 账号／建团队、模型接入／默认配置、容量／次数、运行与审计 | 平台身份不隐式读取正文、他人历史或业务证据；服务密钥不回显 |
| `POST /api/v1/{web|program}/retrievals` | 单空间、显式 knowledge_base_ids、可选 documents、question／过滤条件 | `retrieval.v1`、最终至多五个当前候选和受控来源；无 logical 生成操作，不扣问答次数，embedding 成本仍记录 |
| `POST /api/v1/{web|program}/answers` | `answer.v1`、单空间／显式范围、question、scenario、可选会话／父轮次与适用条件；Idempotency-Key 必填 | 完整答复或整答失败；正常首次请求等待至固定 deadline，不流式；重复执行中可 202，身份和执行快照按第 2 节 |
| `POST /api/v1/{web|program}/comparisons` | comparison.v1 的对象、条件与范围；Idempotency-Key 必填 | 所有受理格、四态与实际五块 evidence_catalog；零候选正常不足和模型非法输出分开 |
| `GET /api/v1/{web|program}/operations/{id}` | 本人逻辑操作状态；认证渠道／原目标／当前 scope／答案依赖重新校验 | 只读、不启动新生成；成功结果仅按重放窗口及权限返回，过期／失权不交旧答 |
| `GET /api/v1/{web|program}/citations/{id}` 及受控资源入口 | 服务端 citation ID；不接受任意文件路径或模型 URL | 检查当前空间、库、文档版本、source_hash 与墓碑后返回位置／片段或允许的页图／原件 |
| `GET /api/v1/program/tasks/{id}` | 持有人本人在凭证空间／库内的导入任务 | 仅状态，不暴露别人的任务、写动作或未授权资源存在性 |

`{web|program}` 表示两个实际路由族，不能在一个请求中拼接多渠道身份。程序读取操作状态是完整问答的防重／网络恢复配套，只读、本人、原 scope 受限，不增加资料写入或 Agent 编排能力。

程序允许动作逐一登记为检索、问答、对比、引用读取、本人导入任务状态读取，不以HTTP GET代表获得全部只读动作。GET operation与同Key结果重放继承该操作原来的问答或对比动作，且检查原显式目标和结果依赖；不另签一个绕开原动作的“状态读取”通行权。同用户、原认证渠道的新合法凭证可以在覆盖原动作/目标/依赖时读取，不要求继续使用已撤销的原凭证；被撤旧凭证本身仍无效。citation是独立许可动作，有当前来源读取权限和citation scope即可按受控来源核验，不强加answers scope，也不因此交付他人的问题、答案或历史。

### 5.2 输入与结果的共同边界

所有私有 HTTP 响应（成功／错误、认证、context／状态、citation、页图／原件、答案／历史及程序入口）统一 `Cache-Control: no-store`；对应网关路由族 `proxy_cache off`、`proxy_no_cache 1`、`proxy_cache_bypass 1`，不得覆盖为可缓存。首版不发 ETag／Last-Modified／304，If-* 条件头仍完整重授权，不能绕授权返回任何 body。前端不将私有内容写入持久缓存。HTTP 响应的单一真源是 [C2 公共 HTTP](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:20)，网关部署真源是 [R4 四服务](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:51)；S1 首交公共设施，S2 资源、S3 历史入口各在开放前验证。

- 身份、角色、持有人 ID 由认证层确定。请求只提供目标；路径目标与 body 目标不一致拒绝。目标 ID 列表显式非空／去重校验，未知字段及 schema_version 不猜测。
- 准入顺序固定：校验渠道／当前身份、有限的结构与显式目标；查已有逻辑 Key 并按其规范化版本／原输入指纹处理重传；仅对新 Key 按当前受理限额、profile／guard、执行配置及配额创建操作。已受理同 Key 不因默认配置或可调输入上限后来变化而暗中变成新操作；但当前授权、墓碑、恢复纪元和固定截止仍必须检查。
- `answer.v1` 输入包括 space_id、knowledge_base_ids、可选 document_ids、question、scenario（enterprise／support／manual）、可选 conversation_id／expected_parent_turn_id、受限适用条件（型号／版本／环境／日志／参数）。问题初值上限 4096 Unicode 码点、适用条件文本合计 16384 码点；两者均可调有限配置，输入过大拒绝而非静默删日志。比较输入使用 M2 已选上限，不被这些通用初值放宽。
- 模型输入/输出/总上下文及完整输出预留须在P0按实际适配器核定。证据预算只裁已记录实见片段；当前输入本体/完整输出仍装不下则明确失败，不以裁证据代替。展示catalog与模型实见片段一致，裁掉证据不计覆盖，不偷偷增加候选；详见第3.5–3.8节。
- 同一会话一次只受理一个未终结问答／对比轮次；新逻辑键提交时检查 expected_parent_turn_id，忙或父轮次过旧返回明确冲突，不按另一轮完成顺序猜上下文。同键重传优先匹配原操作，不新建消息；成功一次只追加一对受控会话消息。跨空间必须新会话。
- 普通答复按场景分别输出流程／材料／负责人，候选原因／检查顺序，或型号／数值单位／限制；有事实的陈述都关联本轮 evidence_ids。总体状态为 answered／insufficient／clarify／conflict；不足或澄清可无证据，但不得夹带无据事实，冲突列双方来源。比较结果以 M2 的 comparison.v1 为准，不能替换四态或漏格。
- `evidence_catalog` 由服务器生成，模型只引用允许 ID；每项保存实际片段、库／文档／版本／块、来源定位与原件哈希，私有数据按空间保护。模型不决定可信文件 URL；原件／历史来源保留不依赖旧向量永久保存。
- 所有响应有 schema_version、request_id、status；问答／对比另有 operation_id。完成结果包含 replayed、accepted_at、completed_at、执行快照 ID 与受控 evidence_catalog；202 含状态位置，失败只含安全错误、ID 和恢复提示，不交半个答案。M2 JSON 展示比较条件／四态的能力载荷，实际 HTTP 包需补这些公共元信息，不能据示例省略。

### 5.3 最小错误字典

HTTP 状态与业务码一起使用；外部 message 不包含未授权目标的标题、是否存在、上游密钥／签名 URL 或私有原文。UI 与程序客户端按 code 和 retry_mode 行为，不以任意异常字符串作契约。

| 类别／HTTP | 业务码示例 | 明确行为 |
| --- | --- | --- |
| 400／422 输入 | AUTH_CHANNEL_CONFLICT、VALIDATION_ERROR、COMPARISON_LIMIT_EXCEEDED | 改正输入或渠道；不调用模型，不静默截断 |
| 401／403 身份／动作 | AUTH_REQUIRED、CREDENTIAL_INVALID、ACTION_FORBIDDEN | 登录或更换合法凭证；不回退身份 |
| 404 目标 | RESOURCE_UNAVAILABLE | 无权、不存在、失效目标按同一安全边界；不返回部分目标结果 |
| 202 操作未终结 | OPERATION_IN_PROGRESS | 只查状态或同 Key 重传，不自动换新 Key |
| 409 冲突 | IDEMPOTENCY_CONFLICT、CONVERSATION_BUSY、CONVERSATION_REVISION_CHANGED | 不改原操作；用户明确发起新操作前说明当前状态 |
| 410 过期 | OPERATION_EXPIRED | 旧 Key 不再执行，用户明确新请求才用新 Key |
| 409／410 上传 | UPLOAD_CONTENT_CONFLICT、UPLOAD_EXPIRED | 异实际hash/长度或过期上传不建任务、不新预留；GET可按权限读原元信息，清理未完不释放 |
| 409 配置／重建 | EMBEDDING_PROFILE_INCOMPATIBLE、EMBEDDING_DIMENSION_MIGRATION_REQUIRED、KB_REBUILD_IN_PROGRESS、KB_WRITE_IN_PROGRESS | 对齐配置／等待合法重试或维护；不得偷偷漏库、改维度或放行 guard |
| 413／429 限额 | FILE_LIMIT_EXCEEDED、ORIGINAL_CAPACITY_EXCEEDED、QUERY_QUOTA_EXCEEDED、CONCURRENCY_LIMIT_EXCEEDED | 文件／空间／次数／并发分别说明，不把未知当无上限；已受理操作按原规则终结 |
| 413／422 协议/业务输入 | REQUEST_BODY_LIMIT_EXCEEDED、PROTOCOL_STRUCTURE_LIMIT_EXCEEDED、INPUT_LIMIT_EXCEEDED | 原始body超限413，其余有限结构/新业务输入超限422；不受理/不预留/不外发，不泄露未认证旧操作 |
| 422 模型预算 | MODEL_INPUT_BUDGET_EXCEEDED、MODEL_OUTPUT_BUDGET_EXCEEDED、CONTEXT_EVIDENCE_BUDGET_EXHAUSTED | 已知基础必超尽早拒；已受理失败只释放一次，不发该失败阶段，已花embedding照记；不删日志/格/金标，不伪装NO_CANDIDATES |
| 503 模型预算未证 | MODEL_BUDGET_UNVERIFIED、MODEL_BUDGET_PROFILE_INVALID | 不发生成；允许的检索后真实零候选可确定性不足，候选非零失败释放；计数/模式须P0重核 |
| 502 截断 | ANSWER_TRUNCATED | length/无完整终止即使JSON可解析也失败，不交半答、不追加模型修复；实际usage/unknown保留 |
| 429 调用速率 | QUERY_RATE_LIMIT_EXCEEDED | 无逻辑槽受理前拒；已受理内部gate只在原deadline有限等，到期失败/一次释放，不无界排队 |
| 502／504 依赖 | DEPENDENCY_UNAVAILABLE、DEPENDENCY_TIMEOUT、ANSWER_VALIDATION_FAILED | 原操作失败／成本照记；用户显式新逻辑操作才新调用，文档上游未知走待核对 |
| 409 位置／纪元 | SOURCE_LOCATOR_UNAVAILABLE、RECOVERY_EPOCH_CHANGED | 明示位置不可用；旧 epoch 不执行，不自动改头重发旧操作 |
| 503 运行保护 | STORAGE_PRESSURE、RECOVERY_QUARANTINED | 磁盘压力／维护隔离明确失败，不伪装正常 |
| 403 身份未核验 | IDENTITY_UNVERIFIED | 恢复旧账号不能正常登录／换新凭据；不泄漏其他主体状态 |
| 423 恢复范围／配额 | RESOURCE_QUARANTINED、QUOTA_RECONCILIATION_REQUIRED | 仅向已独立核验并有范围权者展示；其余按认证失败／资源不可用边界，不泄露资源存在 |

retry_mode 使用 none／same_key_or_status／new_operation／manual_reconcile，意为操作恢复方式，不授权客户端无条件自动付费重试。具体错误子码可以增加，但不能改变这里的身份、计次、部分失败和目标集合语义。

### 5.4 必需实体与不变量

这是逻辑实体及约束，不强制一实体一物理表；实现迁移必须可验证相同不变量。

| 逻辑实体 | 关键约束与生命周期 |
| --- | --- |
| 用户／空间／成员／库授权／负责人 | 平台和业务身份分离，个人归本人；转让／接管、撤权和禁用使用事务性当前状态 |
| Web 会话／程序凭证 | 随机秘密仅 hash、到期／撤销／用户和 scope；恢复失效机制按第 4 节；供应方可恢复密钥另存加密配置 |
| 文档／版本／来源资产 | 唯一活动版本、明确候选终态、不可变来源；保留字节账，tombstone 优先于可读状态 |
| 块／向量／profile／索引代 | 文档版本与来源、profile／D／规范化兼容，活动指针与 docset_revision；历史证据不依赖向量寿命 |
| 持久任务／attempt／KB guard | 有界 lease、所有者／代次／token 条件写入；取消／删除／失败／过期释放本 guard，旧 attempt 无权改新状态 |
| 上传意图／写入者／资产清单 | 用户+空间+库+上传ID唯一；state/绝对截止/attempt/prefix持久化；有效写资格与清理余账分离，prefix/asset_id不可复用；停写证明和cleaned条件先于一次释放 |
| 逻辑操作／日桶／预留／调用 | 唯一请求指纹、hard_deadline／执行快照、结果依赖／终态；一次结算或释放，实际每次供应方调用独立留账 |
| 调用意图／成本事实 | call_id唯一、归属不可变、prepared→may_have_sent只派发一次；usage/cost未知为NULL并有状态；迟到事实幂等追加，冲突需核对，不能触发业务终态 |
| 会话／轮次／历史证据 | 单空间、预期父轮次、一次未终结操作、受控证据快照；每次回看和追问重授权 |
| 审计／恢复台账／配置版本 | 当前授权、删除与可信恢复依据可追溯；普通日志不充当敏感业务数据出口 |

纵向实施单元、依赖、前置探路与验收见 [实施切片](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md)。这些是可实施计划，不是已完成故事或冲刺状态。

迁移/仓储必须验证：稳定ID非空且不重用；子资源的space/KB/document/version归属一致（组合外键或等价同事务约束）；每文档唯一活动版本/当前候选指针；KB唯一活动代/有效guard；同会话唯一未终结生成轮次、父轮次条件追加；日桶/字节账非负，预留及终态转移用唯一transition ID，不能先读后写丢失更新；状态、引用归属和四态分支合法。未知外部usage不得被默认0或非空默认值抹去。运行SQL/迁移与真实PG并发负例在相应切片形成，文档不伪称这些约束已执行。

### 5.5 前端响应归属与网络恢复

- API客户端为每次异步工作保存本地上下文代次：账号、登录实例、空间、恢复epoch、会话/父轮次（适用时）和operation/candidate ID。退出、换账号、切空间或确认epoch变化时递增本地代次，清私有Pinia/组件缓存并尽力终止旧请求/轮询。取消网络请求不代表业务取消或退款。
- 响应落入视图或内存状态前核对上述归属；迟到回包只属于原操作，不能写进当前另一账号/空间的页面。AbortController只是尽力取消，回调归属检查仍必须执行。`pagehide` 时隐藏并清除私有 DOM；`pageshow`（含 bfcache／history restore）先遮蔽私有区域、清旧 context 并递增本地代次，再通过受控请求核当前本人 context／epoch 及欲显示内容的全部资源依赖，完成前不显示旧正文。后台标签页恢复也先重核；仅 context 成功不能恢复未经重授权的答案／引用／资源。
- 问答首次提交前保存Key和规范输入，等待/断网/202只查原operation或同Key重传；业务成功但回包丢失仍读原结果。终态失败明确呈现原失败，用户主动确认新请求才生成新Key；epoch改变不得给旧排队请求自动换epoch/Key。GET读取仍检查原动作和当前范围。
- 页面区分“尚未受理”“已受理等待”“正常不足/澄清/冲突”“业务失败/未知成本”“成功但当前无权重读”，不因浏览器超时将操作重置为可自动付费提交。上传取消/过期、候选失败保留、清理中/失败分别呈现，不能用清空页面伪装后端资产已释放。
- 联调必须用真实浏览器覆盖同 URL 换账号／撤权、If-* 条件请求、前进／后退及 bfcache 恢复，并覆盖迟到回包跨空间、多标签页旧请求、epoch变化、回包丢失和原上下文正常重放；检查网关和应用的 no-store 及无 304，旧正文不得先闪现。源Markdown／模型文本清洗渲染，受控引用与资源由后端授权，页面隐藏按钮不作为权限证明；不要求追回已经合法显示或下载的内容。
