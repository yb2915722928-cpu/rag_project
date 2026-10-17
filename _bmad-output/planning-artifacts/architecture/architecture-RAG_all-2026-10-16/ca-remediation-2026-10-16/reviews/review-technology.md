---
reviewer: independent-ca-technology-reviewer
lens: committed-technology-evidence-and-greenfield-starter
reviewed_at: 2026-10-16T14:19:16Z
verdict: PASS
material_findings: 0
scope: four-core-architecture-documents-and-ca-baseline-delta
---

# CA 修复独立技术证据复核

**PASS；本镜头发现 material finding 0。** R01–R04 的新增机制有可实现的契约和适当的一手依据，未将本地技术策略、标准支持、未测 seed 或历史审查冒充实际运行成绩。该结论只覆盖下列四份核心文档及其 CA baseline 差异，不签其他代理仍在同步的来源、追踪或 IR 文件，不表示 S0/P0/S6 或产品验收已通过。

本复核者未参与本轮 canonical 编辑，未修改四份核心文档。采用[架构技能配置的技术证据镜头](/E:/aaa-project/rag/.agents/skills/bmad-architecture/customize.toml:98)，实读四件全文、CA baseline 差异、既有 E1–E4 和既有独立官方版本核验记录；对本轮新增机制另实际浏览下列一手资料。未执行应用、供应方、部署或 Linux/PG 故障试验。

## 签署字节与基线

| 实读现稿 | SHA-256 |
| --- | --- |
| [ARCHITECTURE-SPINE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1) | F2562F959FCEB22EC06F0328F39D1DCC28312494A2BADCBCC08EDEEA75F389A2 |
| [shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:1) | 3CBEB99748DE09E9F33E2DAF97308B4C4EA6FAEF54C9B370FF7C40228E03AF5B |
| [runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:1) | 54498A3C7AA600348CFC65DAB8952F090B547BA2ED0B32F05B8103DE508C1E68 |
| [technology-evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:1) | F7B53DC1232FB0D518485479D99F79ED5767669F4346A688CF35C90966DA9DA8 |

比较对象为 [CA baseline 根](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/baseline/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1)下同名四件，文本比较忽略 CRLF/LF；上表 hash 则针对实际文件字节。对照结果如下：

| 文档 | 本轮实际变化 |
| --- | --- |
| 主干 | 新增现行契约导航；AD-4/7/12/13/14 承接 R01–R04 及其前置验收门。Stack 表和既定业务约束没有改变 |
| 共享契约 | C2 私有 no-store/条件请求；C4 历史恢复；C5 匿名登录与 token 引导；C7 媒体交付；C8 open charge、监督封口、时钟与恢复窗口 |
| 运行契约 | R1/R2 的 charge/封口监督；R4 私有代理缓存；R5 恢复窗口；R6 配置；R7 四项正负例及停止点；三处 C4/C8 链接机械重定位 |
| 技术证据 | E1–E4 文本与 baseline 一致，仅新增 E5。未新增依赖或修改精确版本 |

最终复读已包括[链接重定位记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/link-relocation.json:1)中的运行契约链接变更。早期读取时运行契约 hash 为 A16B4A99C2E21CED60DA1C8747D9BA45CD92EF79793ABC28F92706584711F4FA；上表为最终签署值，其他三件未变。

## 本轮实际核对的一手依据

以下均由本复核者于 **2026-10-16 实际打开/定位正文**。规范网页说明机制语义，不证明本项目实现、配置或浏览器已经符合。

| 一手来源 | 此次采用的事实与限制 |
| --- | --- |
| [Python 3.12 subprocess](https://docs.python.org/3.12/library/subprocess.html) | 支持参数数组、close_fds、start_new_session 及等待子进程；多线程父进程不宜使用 preexec_fn。这些是监督执行的构件，不能单独证明所有后代和 FD 已停 |
| [PostgreSQL 18 显式锁](https://www.postgresql.org/docs/18/explicit-locking.html) | 行锁可以串行化共享 pool 的条件变更；一致锁序降低死锁。所有领取/封口路径必须遵守相同锁序，数据库不会自动替应用保证整个协议 |
| [PostgreSQL 18 时间函数](https://www.postgresql.org/docs/18/functions-datetime.html#FUNCTIONS-DATETIME-CURRENT) | transaction_timestamp/now 是事务开始时间，clock_timestamp 是调用时刻的实际时间。DB 时间不是自动成立的单调计时器；实现仍须满足 C8 的证明后取上界和异常时基阻断 |
| [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#employing-custom-request-headers-for-ajaxapi) | AJAX 自定义头结合受限 CORS、拒简单类型可构成防伪请求机制；来源 origin 必须准确核对。XSS 会突破此类浏览器防护，不能把固定头当作身份秘密 |
| [RFC 9111 §5.2.2.5、§6](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.2.5) | no-store 约束 HTTP 缓存存储/复用；浏览器历史呈现是独立边界，也不追回已合法保存的副本 |
| [Nginx proxy 模块](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache)、[headers 模块](https://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header) | proxy_cache off 可关闭继承缓存；bypass/no_cache 分别防读取/保存；add_header 的 always 可覆盖非通常状态。真实 location 选择、头继承及自产错误仍需验收 |
| [HTML PageTransitionEvent](https://html.spec.whatwg.org/multipage/nav-history-apis.html#the-pagetransitionevent-interface) | pagehide/pageshow 与 persisted 描述页面历史生命周期。生命周期 API 存在不等于旧 DOM 已清，也不保证私有画面恢复前遮蔽的实际时序 |
| [RFC 6266 §4](https://www.rfc-editor.org/rfc/rfc6266.html#section-4) | attachment、ASCII filename fallback 与 UTF-8 filename* 有规范语义；文件名需防路径与控制字符，不能照抄上游头 |
| [Fetch：nosniff](https://fetch.spec.whatwg.org/#x-content-type-options-header) | nosniff 实施特定 MIME 检查，并非将主动 HTML 变为安全文本的通用沙箱。准确类型、attachment 和受控预览仍分别必需 |

## R01：监督封口与窗口算法

结论：**机制可实现，当前文字没有以领取时刻替代实际可能发送区间。** [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:155)，范围：155–165，要求先持久唯一 charge 再授予单次 grant；sender 尚可能发送时始终计额，确认该启动实例的全部受控发送者退出、发送 FD/IPC 关闭且旧 grant 不可再消费后，才持久 seal 与其后的 DB 上界。业务超时、读钟、kill 已发出、HTTP 响应或 usage 回填都不能代替证明。

其保守性可直接推导：设某 call 的任一本地发送事件发生于 u，监督封口上界为 s，且 s≥u。考察包含 u 的最近 W 窗口：未封口时 charge 持续存在；已封口时 t<u+W≤s+W，charge 仍被计入。因此，在同一 pool 锁下原子校验所有现存 charge 加新权重不超 L，就覆盖了每个本地发送滑窗。发送前暂停、读钟后暂停、部分写暂停不会令旧调用“过窗消失”。这是本地算法论证，不是公开标准或供应方验收成绩。

[R2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:27)与 C8 一致：每个外部 call 的发送 child 须退出后封口；普通非发送阶段的 child 复用不能保有旧 grant。若控制器崩溃或停发证明不完整，继续 open 并阻该额度；恢复也先独立停旧 sender，再从新 DB 上界等待完整 W，不能使用旧备份时间清额。

机制限制已经明确：本地向传输栈提交应用字节不等于远端接收；网络积压、远端执行/输出计量和供应方实际窗口不由此证明。封口不释放 HTTP/task unknown，也不保证永不 429。DB wall clock 的取值、时基异常检测与保守时间包络必须由实现完成；不能仅调用 now() 就声称已满足。C8 已规定异常阻断、R7 已规定跨窗/崩溃假件先于任何真实外发，因此这些未执行项是明确硬门，不是本轮新增漏决策。

## R02：匿名登录与 token 引导

结论：**可实现，消除了首次登录必须已有会话 token 的循环。** [C5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:95)，范围：95–99，采用受托配置的精确 scheme/host/port、application/json 和 X-RAG-Login: 1，缺失/null/跨源 Origin、form 或缺头一律拒绝；生产 CORS 关闭。普通跨站 form 无法满足该组合，自定义头的跨源脚本请求又受到浏览器预检与 origin 校验限制。

固定登录头是防护协议标记，不能作为密码或随机 token。登录成功另旋转会话并生成会话绑定随机 token；后续认证写使用当前 Origin 与 X-CSRF-Token，页面重载通过当前认证、no-store 的 context GET 获取 token，不放 URL 或持久缓存。旧/过期 Cookie 不要求先取得旧 token；双渠道仍整拒。准确 origin 序列化、拒伪代理来源、会话旋转和 token 失效应由 S1 正负例证明；标准网页不证明这些已发生。

## R03：私有 HTTP 缓存与页面恢复

结论：**防护覆盖 HTTP、gateway 和历史内存三个不同层次。** [C2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:35)覆盖私有成功/错误、Web/program、认证/context、引用和原件，规定 no-store、无私有验证器/304，并让条件请求经过当前鉴权后正常处理或拒绝；[R4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:65)明确禁止继承缓存及错误页回落，gateway 不直接服务私有资产。实现可以受控拒绝该路由族不支持的条件请求，不能因禁 304 而跳过当前授权。

[C4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:77)另禁止持久缓存私有 body，pagehide 同步清私有 DOM/状态与 blob URL，pageshow 保持遮蔽、作废旧代次，再以当前 context 和全部依赖重核后重取。它没有从 no-store 推断 bfcache 消失，也没有用 Abort 代替回包归属校验。实际浏览器的返回/前进、账号切换、撤权、非2xx与条件请求必须按 R7 验收；不能仅检查响应头即宣布 R03 通过。

## R04：原件、文件名与受控预览

结论：**交付类型与主动内容边界明确，符合所引标准的适用范围。** [C7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)，范围：135–143，将原件解析与浏览器交付分离：依据已核格式映射准确 MIME，全部原件 attachment 加 nosniff；服务器生成 fallback/filename* 并限制、清理文件名，不让客户端/上游控制响应头。

inline 只接受本机解码/重编码且校验像素/字节上界的 PNG/JPEG，关联可信 locator；原始 PDF/HTML/SVG 与上游任意内容不能 inline。文本经 JSON 文本字段和 textContent/既定 Markdown 清洗渲染，禁止原始 HTML 和远程资源。这一组合避免仅加 nosniff 就声称 TXT/MD 中的 HTML 不执行；也没有承诺用户保存后在其他程序打开仍安全。图像解码器资源限制、Markdown 清洗器具体配置、CRLF/路径文件名和伪类型必须由 S2 真正验证。

## 既有 Stack 与全部 committed decision 的证据判断

[E1–E4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:11)与 CA baseline 文本一致；既有[独立技术证据记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/reviews/review-technology.md:1)已逐一保存同日官方精确版本、starter 确切 tag、关键 peer 范围及能力边界的实查。此次按已核记录承接这些未变决定，没有把全版本重复检索当成新增机制验证。

| 决定范围 | 已核证据与本轮判断 |
| --- | --- |
| Python 3.12.15；FastAPI 0.143.2/Pydantic 2.14.1；SQLAlchemy 2.0.54/psycopg 3.3.6/Alembic 1.20.0 | E1 和既有独立核验给出精确发布/manifest，Python 与依赖范围无已记录直接冲突；同步短 Session/UoW、ASGI edge 分工不变。Python 监督接口本轮再次实际打开 |
| PostgreSQL 18.6/pgvector 0.8.7；HTTPX 0.28.1；argon2-cffi 25.1.0/cryptography 50.0.2 | E1/E3 及既有核验支持精确 cosine、受控传输、Argon2id、AESGCM 的路线。PG 共享锁/时间本轮再次实际打开。D、完整锁图、目标二进制、绝对期限和资源负载仍未测试 |
| create-vue 3.23.0；Vue 3.5.44/Vite 8.3.4/TS 6.0.3/Router 5.4.0/Pinia 4.0.2/Element Plus 2.14.7；Node 24.22.0 | E2 与既有核验包含 starter 确切 tag 的 base/TS/Router/Pinia 实际默认范围及 Pinia 非 optional devtools peer；选定 seed 在记录范围内。未把 manifest 范围当完整构建证明，未假称 SHASUMS 已核 |
| Nginx 1.30.6/Compose 5.6.0；Ubuntu 四服务 | E3 与既有核验覆盖版本存在及用途。本轮重开官方 proxy/headers 机制，新增规则不依赖新版本功能；宿主 Ubuntu/Engine/架构与目标部署仍归 S6 |
| AD-1/2/5：模块化单体、唯一写者、同源 schema | 项目内治理与组合选择；已明确八模块/四服务和端口适配器分工，没有把某框架默认值当作自动生成所有业务规则的证据 |
| AD-3/6/8/9/11：事务锁序、发布/三账/代次、幂等及独立 gate | PG 事务、唯一性和条件转换可以承载这些本地决定；现稿把独立实体、持久状态及同 UoW 效果写清。源码/迁移尚不存在，所以 S0 的真实 PG 并发与故障验收仍是硬门 |
| AD-4/7/12/13：身份、外传、私有交付和恢复 | R01–R04 本轮一手核对如上；既有合作锁、最少 secret 挂载、成套冻结备份的适用限度保留，未将其升格为已运行安全保证 |
| AD-10/14：RAG、预算、质量与放行门 | K=5、四场景、原 SM/F0 不变；MinerU/千问只确认路线存在，不伪造用途 profile、图意、计数/D 或账号额度。P0/S6 无成绩不能开对应能力，亦不阻独立 S0/S1 |

两个本地 gate 仍分别为全系统 doc_active_job≤4、未证终态 external_async_task≤4，各默认4、可配置1–4；本机重处理槽仍1。它们不是每账号复制额度，也不等于供应方已支持4。对该未测策略的限制和 1/4 档验收完整保留，未发现本轮顺带降低 K、场景、质量或资源门槛。

## 发现与有效边界

本镜头 findings：`[]`。没有需要在本轮改 canonical 的有依据 material finding。上面的时钟、监督、真实配置/浏览器、依赖组合与供应方边界是当前文档已经明确分派的未执行验证，不作为新缺陷重复开单。

本报告不证明依赖已安装/构建、镜像可运行、FD/后代受控、浏览器无闪现、供应方计量语义匹配、真实并发为4、4C4GB足够或可信恢复成功。R01 的 S0 假件先于任何真实外发，R02 的 S1 身份门、R03/R04 的资源/历史开放门和 P0/S6 真实证据要求继续有效；本 PASS 不能替代其中任何一项。四份核心文件后续字节若改变，应按 delta 重新确定本报告覆盖范围。
