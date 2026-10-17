# RAG_all 运行、监督与恢复契约

日期：2026-10-16；状态：final-planning-contract。这是架构的实施 companion，尚无应用代码、供应方接通、目标部署或运行成绩。产品语义继承[现行实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:10)；不得据本文件放宽其状态、期限、计账或恢复规则。

## R1. 控制器与物理执行槽

四个部署服务仍为 gateway、API、worker、PG。API 内有普通同步 def 用例入口、轻维护扫描器和执行控制器；worker 有一个有限调度控制线程和独立续租线程，负责最多4个活跃业务文档job，另有全系统最多4个远端task组件，不为每个pending建线程。八个代码模块不是八个部署服务。HTTP 两认证渠道及 worker 共用 application 用例，不分别实现业务终态。

控制器持短 PG UoW、当前执行 fence、阶段预算与槽记录。阻塞外部传输/落盘/解包使用该槽所属的 Python 子执行者；同一有效 attempt 内可复用，跨 attempt 不复用。子执行者无业务 DB 凭据、Session、主密钥或自主调用下一阶段的权力；只接受单阶段有限命令和单次 call grant，回传有限结果/资产清单。

Linux 实现种子：使用 Python subprocess 的参数数组、shell=False、start_new_session=True、close_fds=True、明确 allowlist 环境；不用多线程父进程中的 preexec_fn。子执行者禁止自行派生后代；发现无法确认的后代或打开 FD 时阻断该槽，必要时停所属容器核对。启动用 init/reaper 清理僵尸不等于证明受控写入者已停止。控制器清单记录 deployment/boot/slot、process group、启动实例与 attempt，不能只凭可复用 PID 判断。

每次传输所需的供应方 secret 或预签 URL 由控制器在合法派发时经有界私有 IPC 注入该 call；子执行者不取得其他供应方密钥或整份服务环境。秘密不放 argv、stdout/stderr、普通日志、IPC 调试或持久命令快照；控制器只存 key_id/配置指纹。单次执行后清除内存引用，记录只保留受控调用元数据。这是协作代码边界，不承诺防御已入侵的同 UID 宿主进程。

逻辑 query 槽为 PG 条件 gate（全部署≤2、每用户≤1），retrieval/answer/comparison 共用，比较子检索串行、embedding 批1；无等待逻辑队列，取不到即429。物理传输槽寿命独立：初值 API 查询传输槽2、上传槽1、worker本机下载／解包／校核／embedding等重阶段槽1，每个逻辑操作/attempt最多一个在途受控子执行者。按2026-10-16用户增加异步并发的授权，全系统doc_active_job与external_async_task两个本地gate各默认4、可配置1–4，均为所有账号合计而非每账号各4；remote task有效值再取真实账号总池／用途限制与已验资源界的较小值，未知不外发。doc_active_job在PG条件领取开始处理时占，queued不占，在业务终态／到期fence的同UoW一次归还；远端task在submit may_have_sent同UoW领取，业务失败／取消／重启不归还unknown，可信task终态的唯一release才同时归还本地taskgate及账号／用途task组件。因此旧unknown task可以与新的有限本地预处理job共存，但不得发第5个远端任务。此4覆盖旧整文档单处理槽，不把本机重阶段槽加至4；4只是未测技术seed。业务 lease 失效可一次释放产品预留，未证旧child停止时**不释放物理槽**；P0并存RSS及账号核验后才生效。

调度器在有限PG队列中按稳定游标公平轮转活跃job，每轮每job最多执行一个到期可执行阶段，到期poll不被新submit无限压后、未到期不忙轮询。每次submit/poll只占一个本机阶段槽，远端accepted后保存原task ID／状态／permit/fence与原deadline，确认该次child退出、FD全关才返还物理槽并推进其他job。远端pending不持Session或正文缓冲，仍持原task组件；有账号／资源依据时最多4个远端工作可真实重叠，不能让第一job同步阻等到terminal再调第二个。任务原2h期限含排队／等待／重试不刷新；取消／到期先fence本地写资格，未证远端终止的task组件与成本unknown继续保留，不为给新job腾位假退并发。

跨API/worker的账号调用gate由execution唯一拥有PG共享池，以provider_account_id+region+rate_pool_id标识真实共额域；真实账号总池与用途子池共同约束，换secret/key_id不创建新额度池。profile按用途/动作登记实际适用的RPS、TPM、在途HTTP并发、异步task并发等维度，不能把它们统称一个并发计数。may_have_sent同一短UoW按call_id唯一原子取得全部适用维度的permit组件，不在各进程复制账号额度，也不为活性编造独立池。TPM适用时按已证完整输入+最大合法输出预留；RPS/TPM按C8的send_open持续计额、监督封口后完整W自然到期，不能按grant领取时间过窗；失败/usage回填不提前返还。

异步submit新增task组件并留在原call，收到accepted/HTTP响应仅能释放已证结束的HTTP组件，不能释放仍running的task组件。原持久已知task的只读poll/reconcile引用其原task组件，不再领取“新增task”额度；每次poll仍新建call并领取厂商真实适用的账号/用途HTTP、RPS等组件，全部外传仍过相同gate。每组件的可靠终态/官方绝对上界及[C8唯一release_transition](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:145)控制每(call_id,dimension_id)唯一active→released与适用本地taskgate／账号／用途本维一次归还；独立释放先本地gate再pool→call→组件，重复响应/核对/扫描零额外效果，ledger迟到账不退permit。上界须覆盖该call最晚可能实际到达时刻，不能用may_have_sent本地时间直接加厂商执行时长；无接收时刻或可证最晚到达界仍unknown。未知task保留原组件，停止child不证明远端task终止。若供应方真实把只读poll也计入已满且无法释放的同一维，P0必须证明可用核对通道或官方有限完成上界，否则不启用该异步组合；不以无限人工等待充正常处理闭环。

## R2. 有界入口与每次派发

JSON请求在认证/业务之前经过有界 UTF-8/H 协议解析；二进制 PUT 不套1MiB JSON界。上传专用有界 ASGI 传输适配层只处理流控和有限协议，不执行 ORM 或创造授权真源；它把认证/候选查询交同步用例，把小块数据通过有界 IPC 与背压交受监督 writer。普通业务路由继续 def 与同步短 Session。

gateway对二进制上传关闭request buffering并显式proxy_http_version=1.1，验证chunked/有限body/超时实际流式行为，禁止未计账的请求临时文件；API不使用在准入前自动物化整文件的默认UploadFile/SpooledTemporaryFile链。先获上传槽、候选当前资格与原件/物理预算，才读取实际body；框架、代理、IPC、子执行者所有缓冲须有上界并计预算。确需暂存时先登记独立prefix/资产预算再接收，不能“接完整文件后拒绝”。断网只终止输入，不推定业务终态/退款；重复PUT沿原候选有界核实际长度/hash，不新建版本。

执行顺序是：控制器预占真实物理槽与有限命令→实际子执行者取得所需稳定生命周期SH锁并IPC请求资格→控制器短UoW复核并记录prepared→临近传输短UoW复核并条件提交may_have_sent→一次grant（C8 send_open已持久）→子执行者一次传输→受控结果落盘→该call发送child退出/发送FD关闭与旧grant销毁→新短UoW封口和条件登记。不是控制器先代writer持一份锁；controller本身若读取源则作为独立读者持自己的SH。所需多个prefix按稳定prefix ID升序，锁集合提前确定，禁持后序再补前序。上述锁不在持PG事务时等待。SDK暗重试/自动重定向关闭；显式有限重试新call_id且重过资格门。may_have_sent后是否真正出网不能从本地失败推为not_sent，费用unknown保留。

grant绑定call、attempt、boot及child启动实例，经私有IPC单次消费；原call不得在重启/重领后再次给grant。send_stop_by到期只触发停止，读钟后暂停、部分写后暂停、控制器失联或TERM/KILL未确认均保持send_open；不能复用物理槽。正常结果也须发送child退出、发送FD/IPC关闭及未用grant销毁才由execution按C8原子封口，以取得证明后的DB时间保守留完整W。封口只结束本地发送可能性，不证明远端HTTP/task终态或成本为零；无需为此增外发代理服务。DB不可用/证明不完整持续占额，恢复依R5隔离旧sender，不能计数清零。

controller 每阶段重核当前epoch、父级墓碑/隔离、attempt/token/lease/deadline、候选/guard与预算；用户查询另核当前身份/凭证与全部原显式目标。合法受理文档任务归库继续，不因上传者后续降级自动取消；它仍受库资格和物理守卫约束。纯retrieval也有持久执行上下文、deadline和call账，不获得免费无限外发入口。

到期核对仅通过新 reconciliation 上下文读取原持久已知ID；不能复活原job或下载发布。真正本地继续用新job/attempt/deadline，重新获取候选/guard/预算；新解析PUT是另一个知情明确动作。三条路径不能在适配器共用“重试”分支。

## R3. 稳定锁、停写证明与清理

执行模块唯一拥有 asset_prefix、writer、资产清单和cleaned状态；ledger唯一拥有相应字节/预算转换。前缀按version/attempt/stage登记，永不复用，先登记再启动写入者；来源发布后不可变。文件落盘未完成逐文件登记的崩溃由prefix发现孤儿，不凭DB无记录断言磁盘无资产。

生产采用 Ubuntu 本地文件系统上同一宿主bind卷和 fcntl.flock；共享锁供读/写生命周期，排它锁供清理，锁文件在独立稳定locks根、与资产删除分离。API和worker看见同一锁文件 inode，不在容器各自临时目录建同名锁。禁止NFS/SMB替换而不重验语义。flock是合作锁，代码必须全部遵守；它不会自行检测死锁。

writer在任何字节前由**子执行者自己**取得SH锁，并在持锁时通过IPC请求controller复核；controller短UoW批准才写。锁由实际writer持有至关闭全部FD、停止该阶段写入；controller不得提前解锁。有效源读取也持SH到受控读取完成，使并发清理等待；打开流之前当前鉴权，已合法传出的字节不追溯回收。多prefix读/写/清理锁一律按稳定prefix ID升序取得，不能一边持锁一边补更小ID。禁止把SH升级EX；需释放后重新取EX并复核，不依赖锁升级原子性。

清理步骤固定：C1短事务终结/fence写意图；C2事务外停止并等待所有登记writer/进程组退出（TERM等5秒、KILL再等10秒仍未证则blocked）；C3事务外取得稳定EX锁；C4同锁下短UoW核终态/cleanup_token、资产引用和当前状态；C5无PG事务删除所属临时/孤儿/无有效引用资产并确认FD关闭；C6仍持EX时短UoW由execution标cleaned、ledger条件执行唯一transition释放字节/预算。不能在C5持事务，C4与C6间的发布/登记必须同锁且重核墓碑/fence，因此不会重获写权。

C5成功而C6提交失败保留占用，重试按资产实况和原token完成一次转换；C2/C3/C5失败显示cleanup_blocked、保留占用，删除访问阻断已经生效且不能回滚。已fence的业务终态不再阻重建，清理余账仍受物理预算。旧attempt无权释放新guard、标其资产cleaned或借成本回填写业务。

PG锁序统一为全部所需账号控制行ID升序→空间控制行ID升序→KB稳定ID升序→业务对象固定类别/ID→空间容量/日桶→文档本地gate ID升序→provider rate pool ID升序→call ID升序→permit组件ID升序→asset ID升序；无某类则跳过。组件独立释放的短UoW也按本地gate→pool→call→组件顺序；迟到成本只锁call、不回取gate/pool。当前鉴权取SH，安全变更在对应控制行取EX并覆盖子表。先确定整组主体/空间，解析信息取锁后重核，space后不补账号；多KB集合取space锁后确定并复核，变集合回滚重试。受理、每次派发、完成放行、重放/历史/来源/下载均同序；后台已受理库任务从space SH开始且永不回取用户。完整覆盖清单和同UoW矩阵见[共享契约C4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:53)，账号总池/用途子池及permit见[C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:145)。先取OS锁再开短PG事务；不持PG事务等待OS锁/网络/子进程退出/大文件删除。迟到可信成本只锁call追加，不反向取业务父锁/gate/pool/组件，不为退限流占用修改历史事实；冲突留核对。

## R4. 四服务、介质与最小权限

下表是挂载职责，不是已存在目录。S0将其转为Compose配置与权限验收；运行路径由配置指向，业务API不返回宿主绝对路径。容器非root、无Docker socket、无host PID/privileged；应用根只读，必要临时目录单独有限挂载。仅gateway公开HTTPS端口，PG/API/worker无公网监听；前端在开发电脑构建，服务器只运行锁定产物。

| 介质/内容 | gateway | API | worker | 维护操作者 |
| --- | --- | --- | --- | --- |
| 预构建Web静态资源 | RO | 无需 | 无需 | 发布替换 |
| 不可变原件/归一来源/派生资产、attempt暂存 | 不挂载 | 授权读取/受控上传RW | 受控阶段RW | 备份/恢复；不借维护入口浏览正文 |
| 稳定locks根 | 不挂载 | RW锁句柄 | RW锁句柄 | 停写核对；不删锁文件 |
| PG数据卷 | 不挂载 | 仅DB协议 | 仅DB协议 | PG容器独占RW；匹配逻辑dump/角色导出 |
| 独立epoch控制记录 | 不挂载 | RO | RO | 唯一维护写者，原子更新；不随DB旧备份覆盖 |
| 服务密钥/外置主密钥 | 仅TLS私钥RO | 各需秘密RO | 各需秘密RO | 分版本加密封存，单独授权 |
| break-glass及现行受托登记 | 不挂载 | 不挂载 | 不挂载 | 独立受控介质，必要时离线使用 |
| 安全台账已认证连续导出/备份副本 | 不挂载 | 不常驻挂载 | 不挂载 | 显式维护导出到独立加密离机介质 |

私有路由族覆盖认证/context、Web/program API、状态/错误、引用/来源/页图与原件；gateway必须proxy_cache off、proxy_no_cache 1、proxy_cache_bypass 1，不能从上级配置继承缓存或用error_page回落到可缓存路由。API及gateway自产错误均确保Cache-Control: no-store（含非2xx），不覆盖为public/max-age，不发私有ETag/Last-Modified/304，条件请求仍到当前授权入口。私有资产不由gateway静态目录、任意X-Accel-Redirect或上游签名URL直出，受控应用读取执行C4/C7并设置准确MIME、Disposition及nosniff。公开静态构建产物与私有路由显式分开，S0/S1验证路由/头部，S2/S3入口开放前验证实际资源/历史。

供应方密文配置在DB、主密钥在服务secret，两者分离；用户Cookie/Bearer只存hash不能恢复明文。Compose secret只提供按服务挂载，不承诺宿主文件自动加密。子执行者不常驻加载secret文件，按R1单call IPC获取。不同环境用不同数据库/卷/epoch/秘密与样例，开发假件不会自动成为生产可用profile。Windows开发可以使用Linux容器/隔离Ubuntu环境验证flock与进程组；原生Windows假件成绩不代替Linux物理停写验收。

epoch控制记录至少含部署标识、随机epoch、cutover、维护状态/版本；应用DB存镜像值，启动和每次持久转换/派发都比较当前控制值。记录缺失/损坏/不一致立即隔离，不按DB补造；普通重启读原epoch，恢复才由独立维护动作生成新至少128位随机值。控制记录可同主机独立卷持续存在，但必须有独立备份/权限与明确的恢复流程，不能在恢复旧应用数据包时一起回滚。

## R5. 启动、发布、成套备份与可信恢复

首次部署先登记独立恢复操作者、受托关系确认渠道、break-glass介质、备份频率/留存/最大可用备份龄与可接受丢失窗口；最后四项是上线前必须由部署方确认的运行配置，不在设计中冒填用户已接受的RPO/RTO。单机首版不承诺高可用、自动故障转移或零丢失。初始化创建独立随机epoch及DB镜像；后续普通重启只读现值。初始化完成后不得以缺失为由重新初始化生产控制记录。

普通启动顺序：①核锁定产物/配置版本、挂载权限、有限生效限制与epoch；②仅PG启动并健康，迁移由单一维护进程执行且失败即停止；③API以维护态启动，短事务核schema/epoch/配置、扫描旧上传/操作/job与资产；④启动worker控制器但未获派发资格前不处理；⑤仅为已核能力/范围开放gateway。健康检查分进程存活、DB/schema/epoch就绪、能力profile可用，不能拿HTTP 200证明供应方/图意/配额已核。秘密缺失只阻断所依赖能力，不把未验证范围开成可用。

发布先关闭新增受理，给现有操作有限排空窗口；超时按原fence/unknown/停写规则结束，不重置原deadline。迁移期间停业务写者；数据库变更按显式迁移实施，vector(D)变维必须维护迁移/新存储，不以改默认profile隐式DDL。发布失败只回到已证明与当前schema兼容的产物；否则保持维护并按可信恢复处理，禁止把旧镜像直接接回已不兼容数据。不得在4GB目标机同时构建前端/镜像。

备份采用**维护冻结的一致包**作为首版种子：关闭新增业务与外发，给既有操作有限排空；剩余操作先按Fence终结，may_have_sent未确定响应保留unknown，停止worker并证明全部受控写者退出；随后统一冻结全部应用写入，包括登录/会话、安全变更、扫描器、cleanup、发布与迟到成本回填。恢复维护入口在此短冻结窗口也不变更业务元数据；确有紧急撤权则先中止该备份、登记安全变化，重新冻结生成新包。取得PG逻辑dump与角色/必要全局配置、原件/解析/引用/资产清单、配置版本、密文及分别封存的匹配主密钥；同一snapshot_id登记schema/镜像/扩展版本、文件hash、台账连续区间/认证清单与时间。dump本身仅保证库内一致，不能把在线拷贝外部文件自动称成同一快照；包有缺件、hash不符或未证停写即不标可恢复。PG逻辑dump不替代日常生产备份策略评估，S6依据实测数据量/窗口验证此维护种子；超出可接受冻结窗口必须先调整方案并复演练。副本加密离机存放，恢复操作者与现行业务受托登记不靠应用旧包自证；独立epoch控制记录的现行值不被旧包覆盖。可验证安全台账导出从已提交连续区间产生，记录最后导出到故障冻结的gap，留存覆盖最旧可恢复包。

恢复严格按下表执行；每步保存操作者、依据、时间、snapshot_id和可复核结果，失败保留隔离并可重试，不自动跳步。

| 顺序 | 动作与完成证明 | 停止点 |
| --- | --- | --- |
| T1 冻结/验包 | 关闭业务、worker与外发，隔离全部旧进程；验证同包PG/文件/秘密/版本/hash与可读资产清单 | 旧写者未隔离、包不匹配或必需资产缺失，不开放也不付费重造缺文件 |
| T2 换纪元/封身份 | 独立维护写者生成全新至少128位随机epoch/cutover，与DB镜像一致；旧会话/Bearer全失效，账号全unverified，关正常登录/取回/旧邀请 | 不用旧epoch+1；不得以旧密码/owner字段解禁；控制矛盾保持维护 |
| T3 核验/合并 | 独立break-glass核受托链，重放可证台账；列gap并用外部现行记录逐账号/空间/库/资料核白名单，重置密码后启用账号 | 已知墓碑/撤权拒绝优先；删除完整性不明范围保持quarantine；平台无正文权限 |
| T4 执行/三账 | 旧attempt全fence；success不重结算，旧pending生成终止且一次释放恢复预留／doc_active_job占位，原Key不再跑；远端task本地gate与全部provider共额维度先blocked_unverified，不沿用旧低计数；现行未决task须独立核验后重建本地／账号／用途占用。已知上游ID仅在范围及只读核对动作放行后查 | 无ID为unknown，不重交；未知task不因旧job终态返还远端组件；当前上海日次数不明则冻结该空间新增生成，可信核对或次日仅解该配额缺口；备份后丢失call不凭新epoch断言远端已停 |
| T5 分步放行 | 现行接入受托人核凭据/key_id、匹配主密钥、真实共额域、各维未决调用与有限约束；按账号、资料范围、本地读/写、外部只读/付费、worker及pool维度/动作分别放行。全部旧本地sender独立隔离/停止且旧grant不可消费后，以新DB上界保守等待各完整W，HTTP容量亦已核时，仅放已知原task的有限只读核对，仍禁未知task占用下的新submit；task终态经可信证据后才一次释放原task组件 | 缺主密钥/凭据或未核适用维度阻该动作；无旧sender停发证明不得按备份时间放行窗口；封口后完整W届满不解task unknown，不为poll假拆池。无ID无本维官方有限上界仍阻新增task，上界须覆盖最晚可能到达时刻，不从本地may_have_sent计时自证；若poll也被同一满维阻断，按P0已证通道/上界处理，无证明不启能力。部分放行不称全站恢复，次日不解身份/资料隔离 |
| T6 负例与收尾 | 原Key/旧epoch/旧凭据/迟到attempt负例通过，备份gap/未知费用仍可见；归档实际丢失窗口和恢复耗时 | 不以进程启动/旧引用偶然打开通过；同包二次恢复必须新epoch并使第一轮新凭据失效 |

恢复后context只给当前合法本人epoch/server_time；新付费写操作要求现行epoch及cutover后UUIDv7，客户端不得自动改旧Key/epoch重送。恢复点内success仅经受控GET在原窗口回看，核当前身份/来源/墓碑且标原完成时间/版本/日桶；丢失于恢复点后的答案、任务、上游ID不承诺找回。普通重启不改Key窗口、不重新生成epoch。

## R6. 有界资源、观测与运行动作

上线生效配置必须含上传/JSON/响应字节、格式页数/批量、ZIP展开字节/文件数/单文件/比例、每阶段及全系统并存临时字节、磁盘低水位/保留余量、PG连接池及overflow/等待、各类deadline、日志轮转、全系统doc_active_job_limit与external_async_task_limit两个独立gate（各默认4、配置1–4，非每账号各4）、provider真实账号共额域/账号总池/用途子池的RPS/TPM/HTTP并发/异步task并发及适用动作、每call有限send_stop_by/监督停发证明与窗口charge持久配置、模型输入/输出/总token上限；不适用维度须有官方依据，未知必需项阻断对应派发，不用默认无限。设置须保存配置版本与受理快照，UI只显示服务器EffectiveLimits。原件空间额度、磁盘实占、产品次数、供应方额度和真实物理执行槽是五种独立保护，不相互替代。P0用API/worker共享账号的并发/跨用途负例验证总池与子池；以任务池1和4均验证满池submit→accepted→poll→terminal、公平推进／取消／unknown／重启恢复与组件一次领还，4档还须证明4项远端工作重叠且本机重阶段≤1、与查询／上传并存的RSS／FD／磁盘／预算不过界。未达到4档则不启4档，未证并发不声称4GB已达标。unknown不放新task但不无据封死已核只读核对；所有等待按原deadline有界，不另建查询等待队列。

4C4GB目标机以S0锁定镜像和P0真实负载测量：PG、gateway、API、worker与并存子执行者总RSS/峰值、cgroup/OOM事件、CPU、连接/事务时长、FD、磁盘余量/增长、调用延迟与失败。保守起点是单API业务进程、worker一个本机重阶段槽、有限调度≤4个远端等待context及独立心跳、无在线本地大模型/重排/前端构建；数值并发沿R1。PG池与容器内存须按实测总预算显式配置，不能把各容器各填4GB。先缩并发/批量/输入、使用流式与背压再复测；仍不满足原功能时停对应切片，记录变更提案，不能降验收。OOM后未证旧写者停止不借出其槽；磁盘低水位阻新写/付费受理，已有任务按预算安全终止，已核合法读和受控删除可保留。

默认结构日志只记时间、级别、服务/boot、request_id、受控operation/job/attempt/call/asset ID、epoch/配置指纹、阶段、条件转换结果、错误码和延迟；不同ID用途不得互代。普通日志不写问题/答案/原件正文、完整提示、密码/Token/主密钥、签名URL或原始供应方body。故障原包进入有权限、有限留存的独立诊断材料，使用时明确授权与脱敏，不能默开全量HTTP debug。用户只读program响应和平台运行投影仍受字段白名单；审计/调用账不是让平台搜索业务正文的新入口。

| 观测项 | 告警/动作 | 保留证明 |
| --- | --- | --- |
| epoch/schema/秘密/生效配置矛盾 | 立即隔离受影响范围/能力，禁止派发 | 首次发现时间、配置版本、隔离及放行依据，不输出秘密 |
| 失租/超期/扫描积压 | API启动及周期有界扫描；条件fence并一次释放产品预留，旧传输槽待停写 | 扫描游标/数量/最老年龄、各阶段终态、物理槽独立状态 |
| cleanup_blocked/孤儿prefix/磁盘压力 | 停新写、保留占用，按R3重试；未证停写则停所属执行容器核对 | writer身份/锁/FD/删除结果、唯一transition，不把unlink视为回收 |
| 费用unknown/事实冲突/限流 | 不填零、不盲重发，已知ID有界核对；本地用途gate与账号限制取小者 | call事实及来源、原业务终态、费用确认时间/未知原因 |
| 原件容量/日计次差异 | 冻结有争议新增预留，依据唯一账/资产/操作事实核对 | 上海日桶、预留/实占/结算/释放、差异范围；不删除旧账凑数 |
| 备份过龄/损坏/台账gap | 标不可作为已验证恢复点；修复导出/备份与演练 | snapshot_id/hash/连续区间/认证、最后验证与实际gap |
| 未授权访问/输出前撤权负例失败 | 停相应范围/切片，修复再跑独立SM-6 | 当前权及请求范围、去秘密HTTP和访问/未外发事实 |

查询使用者只看本人受控结果/状态；当前库维护者管理合法库任务；平台接入管理员管理接入/配额与去秘密运行元数据；独立恢复操作者仅恢复维护元数据。日常维护允许核对账/重试清理/导出可证台账/验证备份，禁止维护按钮隐式重交解析、换Key重问或代用户登录。运行告警不创建第五个常驻服务；首版由既有维护命令和API扫描产生指标/状态，部署方确认接收渠道后再接外部告警，不自动向第三方发送业务数据。

## R7. 分层验收与停止条件

本文件是待实现契约，以下均为必须取得的成绩而非已通过。每项记录版本/环境、输入、实际副作用、去秘密原始响应、关联ID、预期/实际与失败原因；真实PG/Linux/目标机/供应方成绩分别标来源。S0可在无供应方凭据时独立开始，全计划规划可行不等于上线可用。

| 门槛/责任 | 必须取得的可复核证据 | 不通过时停止点 |
| --- | --- | --- |
| S0／实现者 | 干净Linux环境迁移/启动/停止；epoch矛盾隔离；真实PG唯一性/UoW；prepared前后和may_have_sent后崩溃、迟到成本不改业务；任务池1/4假件满池poll、公平推进／取消／unknown／恢复、组件一次领还、远端重叠与本机重阶段≤1；有界上传、writer持锁、TERM/KILL/FD与cleanup账故障 | 不转SQLite或假件为PG/真实供应方/4GB成绩；未闭调用/资产守卫不开展真实外发 |
| S1／实现者 | 当前身份及双渠道；账号→space→KB一致锁序；安全变更同事务台账；最后一笔预留并发、同键/异输入/过期；前端账号/空间/epoch迟到回包隔离 | 任一越权、重复计账、反序锁/当前授权缺口不开放业务外发 |
| P0／接入实施者 | 真实MinerU格式/ZIP/来源、图意专项、embedding/profile维度；模型完整消息token与输出上界/compact128；SDK禁暗重试/重定向、真实维度/动作映射；任务池1/4满池poll、公平／取消／unknown／恢复、三账与组件、4项远端重叠但本机重阶段≤1，且查询／上传并存资源不过界 | 未具账号可继续独立S0/S1；无可证核对通道/有限完成上界不启异步组合，未证4档不开4档；缺定位阻S2相应格式，图意不达标阻S5/整期，非零未证预算不生成 |
| S2／实现者 | 首次部分/完整候选、替换失败保旧版、可定位来源/向量完整才发布；未PUT/半传/重传、删除/乱序/旧attempt、停写与清理失败；无需问答页的最小校核 | 旧版破坏、删除仍读、源/向量缺失假ready、无预算暂存均阻本片 |
| S3/S4/S5／实现者＋评估者 | 当前权精确B0、最终K≤5且catalog等于实见；完整预算；结果/依赖/会话/计次同UoW；丢回包只重放；四场景开发事实/四态完整矩阵与真实图意 | 预算裁空装不足、非法/截断/缺格/来源ID越界失败，不交草稿不LLM修复；未证明图意不称四场景完成 |
| F0／评估者 | 首次以结果选参前冻结32题、资料/hash、原金标证据单元与必要事实/判定；开发题分离 | 未冻结不得开始调优；不能换分母、删失败题或把P0开发题当留出题 |
| S6／部署/恢复操作者＋实现者 | 4C4GB并存RSS/连接/磁盘/故障；真PG重建/删除/guard竞态；同包恢复两次新epoch，独立受托核验、台账gap、旧密码/Cookie/Bearer/owner/Key/attempt负例、逐范围放行 | 无环境/秘密/备份频率与可接受窗口确认或可信恢复演练未过不上线；未知配额/身份/资料各守自身隔离 |
| S7／评估者 | 同冻结材料B0/上一保留轮/本轮输入输出/检索/引用/用量费用/失败；SM-1至7逐项及场景分报，独立权限专项 | 质量阈值、任一专项或权限失败不得被平均/漂亮UI抵消，不称整期完成 |

### 最新深审修复的运行关闭条件

以下四项的**规划条款已补，运行验收全部未执行**；不把文档审阅替代这些证据。

| 发现/最早门 | 必需正负例与可观察结果 | 硬停止点 |
| --- | --- | --- |
| R01 / S0→P0 | 共享池RPS=1/s、TPM完整一分钟预算：A领grant后暂停跨窗、读钟后暂停、部分写后暂停，B在另一槽尝试，A仍open时B不得超额发送；封口后完整W才可再领。controller在may_have_sent/IPC/封口前后崩溃、child失联仍活、kill未确认均继续计额；重复封口/扫描零效果，重启及旧包恢复不得清额。记录实际本地发送事件、PG charge/proof/DB时刻与全部池计数；P0再核真实维度和厂商行为 | S0假件未过不做任何真实外发；真实维度未证不开对应能力，不承诺远端到达窗或永不429 |
| R02 / S1 | 全新无Cookie浏览器可同源JSON+固定头登录，成功新会话/token可用于后续认证写；跨源/null/缺Origin、form/缺头不建会话，旧token/缺token认证写拒绝；context重载取当前token且no-store，双凭据仍整拒 | 未过不开放身份入口 |
| R03 / S1设施→S2资源→S3问答历史 | 真实浏览器同URL A读后退出换B、撤权后再读、If-*条件请求、history back/forward与bfcache恢复；所有私有成功/错误no-store且gateway不命中缓存，恢复前私有DOM/旧回包遮蔽作废、当前context及全部依赖重核后重取，失败无旧body | 各入口开放前分别验资源/原件、问答/重放/历史；no-store不自证bfcache已清 |
| R04 / S2 | 合法TXT/MD含HTML/脚本仍为attachment准确MIME，DOCX/PDF同样attachment；恶意CRLF/路径文件名、伪MIME/扩展和上游头不能改变交付；受控PNG/JPEG与文本预览无脚本/远程资源，拒inline主动文档 | 资源入口未通过不开放，不用nosniff单独证明text/html安全 |

R3清理与R5恢复的停止点为硬门，UI隐藏按钮、HTTP200、进程已重启或历史PASS都不替代它们。具体AC、需求与切片映射由[需求—架构追踪](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/requirements-architecture-traceability.md)维护；本轮四项修复、独立审查与最终字节范围由[CA修复记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/remediation-record.md:1)记录；当前效力以[现行IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md:1)为准。

## R8. 官方依据与适用限度

以下页面于2026-10-16实际打开核对。它们支持机制，不能证明本项目代码/目标机/供应方已经通过。

| 官方依据 | 本契约采用的事实与限度 |
| --- | --- |
| [Python 3.12 subprocess](https://docs.python.org/3.12/library/subprocess.html) | 参数数组、start_new_session、close_fds；多线程父进程不使用preexec_fn。进程组是受监督种子，退出/FD仍由R3实测证明 |
| [Linux flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html) | 合作锁与open-file-description寿命；锁释放/继承须按实际FD验证；本地Linux种子不外推NFS/SMB |
| [Docker Compose secrets](https://docs.docker.com/compose/how-tos/use-secrets/) | 按服务授予文件挂载，减少环境变量泄露；本项目另要求宿主/备份加密，不能从Compose声明推定自动加密 |
| [PostgreSQL 18 pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html) | 单库一致导出，不含全局roles；全局对象另导出。库外资产由成套冻结/hash配对，不从dump推定跨介质原子；生产备份策略还须验证 |
| [PostgreSQL 18 explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html) | 一致顺序降低死锁；本项目全局序必须覆盖控制行、业务与账，应用单独执行不会自动遵守 |
| [SQLAlchemy 2.0 Session](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) | 每线程独立Session与明确事务生命周期；不跨线程、网络/文件等待期间不持事务 |
| [Nginx proxy_request_buffering](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_request_buffering) | A本轮实际核官方说明：关闭请求缓冲且匹配代理HTTP版本；R2据此要求HTTP1.1及chunked真实验证，开关本身不证明所有暂存已纳预算 |

供应方/库版本的完整现行核验由A唯一维护的[技术证据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md)登记；不能把以上机制引用当作API能力或4GB成绩。
