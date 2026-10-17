---
title: R01–R04 修复的独立对抗兼容性复核
date: 2026-10-16
reviewer: independent-adversarial-reviewer
verdict: PASS
scope: three-canonical-architecture-documents
material_findings: 0
runtime_executed: false
canonical_modified_by_reviewer: false
---

# 独立对抗兼容性复核：PASS

在下面明确签署的三份现行架构文件中，R01–R04 的规划缺口已关闭。本次没有找到两个分别满足全部适用 AD/C/R 条款、组合后仍可复现原缺陷的单元。没有 material 新发现，也没有为满足发现数量保留违反现行条款的反例。

此 PASS 只表示所签三件的核心技术规则自洽、可交实现并有对应开放前停止点；不是十二件规划包的全面审阅、根 IR 裁决，也不是应用、真实供应方、Linux 停发、真实浏览器、目标机或上线通过记录。未执行应用、供应方外发、部署或产品测试，未修改 canonical。

## 输入与字节范围

独立 reviewer 未参与本轮写作。先实读现行三件，再读取原深审 IR 与 A/B 交叉处置，区分四项 accepted 与 clarification-only/rebutted 原候选。原深审中的四项确认是复核对象，原始候选并不自动成为现行缺陷。

签署范围以 [review-manifest.json](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/review-manifest.json:1) 的 round 1 为准。下列 SHA-256 从实际磁盘文件计算，并与该 manifest 三项一致。交付前还逐项计算了 manifest 全部十二件 canonical 与 snapshot：12/12 两者均匹配登记 SHA；此完整性检查不扩大实读/签署范围。运行文件末尾导航从历史 gate 转到本轮修复记录及现行 IR 的 delta 已重读；它不改变 R01–R04 规则。

| 完整实读的签署文件 | SHA-256 |
| --- | --- |
| [ARCHITECTURE-SPINE.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1) | f2562f959fceb22ec06f0328f39d1dcc28312494a2badcbcc08edeea75f389a2 |
| [shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:1) | 3cbeb99748de09e9f33e2daf97308b4c4ea6faef54c9b370ff7c40228e03af5b |
| [runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:1) | 54498a3c7aa600348cfc65dab8952f090b547ba2ed0b32f05b8103de508c1e68 |

| 完整实读的历史判读输入 | SHA-256 |
| --- | --- |
| [原深审 IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/implementation-readiness.md:1) | 54899824b23af175dcaf954f9fdee5237c9413846ef9646c1c064a96c9fcdcda |
| [Winston A 交叉处置](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/findings/winston-a-cross-check.md:1) | 8c9b9e54e716d17e5c9a10f82a1e9647fdf6bebb91da8ad4f0345c6ffc799ef9 |
| [Winston B 交叉判读](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/findings/winston-b-cross-check.md:1) | a8726dea490205ce95eceaa36304dc236b16c685c17af31cd84a03b28d264ea83 |

另读了 [链接重定位记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/link-relocation.json:1)，SHA-256 为 b7500f7988d36de054e7f00ec545091f8c351ce163eb1de95e6c36bac1842ffd。附后仅抽核实施与 UX 的新增匹配段落，不扩大本报告签署范围。

## 逐项裁定

| 项目 | 规划判定 | 关键现行证据 | 最早运行关闭门 |
| --- | --- | --- | --- |
| R01：迟发 grant 跨窗 | 关闭 | [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:155)，范围：155–165；[R2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:29)，范围：29–31 | [R7 R01](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:136)：S0 假件通过后才可任何真实外发，P0 再核真实维度 |
| R02：匿名首次登录 CSRF 循环 | 关闭 | [C5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:95)，范围：95–99；[AD-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:81) | [R7 R02](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:137)：S1 身份入口开放前 |
| R03：私有 HTTP/bfcache 缓存 | 关闭 | [C2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:35)、[C4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:77)、[R4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:66) | [R7 R03](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:138)：S1 公共设施、S2 资源、S3 历史分别开放前 |
| R04：原件/预览媒体 | 关闭 | [C7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:135)，范围：135–143；[AD-12](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:129) | [R7 R04](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:139)：S2 资源入口开放前 |

四项运行验收均未执行；现行 [R7 明示此限制](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:132)。未取得成绩本身不构成新规划缺陷。

## R01：两槽、停发证明与独立释放攻击

**攻击一：迟发跨窗及检查后暂停。** 设账号总池与用途子池均适用 RPS=1/s，API 槽 A 在 t=0 领取并提交 send_open，拿到 grant 后暂停；另一合规物理槽 B 在 t=1.1 请求许可，A 在 t=1.2 恢复。也分别把 A 的暂停点放在 child 读钟之后、部分请求字节写入之后。A 在这些位置暂停仍可满足一次传输和原 deadline；但 B 不能同时获 grant：C8 的准入总和无条件包含 send_open，不能因领取时间、send_stop_by、业务失败或窗口跨越清掉 A。若让 B 发出，则 B 明确违反现行 C8，无法成为“两单元均合规”的反例。

**攻击二：先自报消费，再 controller 封口。** A 已回报“写完/已消费”，controller 想先记 sealed，B 随后领取，A 又恢复发送。现行 C8 不接受 child 自报作为证明；必须确认本 call child 与全部受控发送者已停止、FD/IPC 关闭、未用 grant 销毁且不能恢复，才可封口。R2 还要求本外部 call 的发送 child 退出；同 attempt 可复用其他阶段不能复用旧发送能力。因此该危险封口不合规。

**攻击三：证明后的 DB 提交间隙。** A 在真实监督停止时刻 P 已丧失发送能力，controller 之后才以新短 UoW 写一次上界 U。即使 controller 在 P 后暂停很久，U 只会后移；B 须在 U+W 后才能使用该 charge 所占额度。若在 P 前、IPC 期间、P 后但事务提交前崩溃，持久 send_open 仍全额计入；若封口提交后崩溃，持久 U 仍保留完整 W。没有“先退占、稍后补 proof”的合法间隙。

在规定的 DB 时基包络下，若 A 最后可能本地发送为 S，监督证明后新事务取到保守上界 U，则 S≤U；只有当前 DB 时刻 t≥U+W 才可不计该 sealed charge，因此 S≤t−W。尚不能证明 S 已结束时，charge 始终计入。这个推理针对本机向传输栈提交请求应用字节的可能区间；没有借此证明远端接收滑窗，也不承诺厂商永无 429。DB 前跳/时基矛盾须按 C8 阻断并重建保守上界；实际时钟包络和检测属于 S0 必须落实的证明条件。

**攻击四：独立 HTTP/task release 或迟到 usage 越权退窗口。** A 的 HTTP 响应先到、task 后终态，release 单元按本维终态各退一次；同时封口/扫描单元维护 charge。C8 明确两类生命周期独立，HTTP/task release 与 usage 不能缩减 RPS/TPM charge，封口也不改变远端组件或成本事实。该 release 即使先于 sender 封口也不能使 B 获得 A 的窗口额度；封口+W 同样不能释放 unknown task。独立 release 的本地 gate→pool→call→组件序与封口的 pool→call→组件序没有要求向前回取已跳过锁；迟到成本只锁 call，不能反向取 pool 退 permit。

**攻击五：重启、丢失 call 的旧包恢复。** 普通 controller 重启不能重授原 call grant，已持久 open 先停旧 sender 再封口。旧备份可能漏掉后来发起的 A；即使备份显示计数为零，新 epoch 也不能直接许可 B：全部池先 blocked_unverified，须独立确认包括备份后缺失 call 在内的旧 sender 已停止/隔离、旧 grant 不可消费，以证明后的新 DB 上界重新保留各完整 W。远端 unknown 并发另核，不因 W 到期自动解禁。证据是 [C8 恢复条款](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:165)与 [T4/T5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:89)，范围：89–90。

合理限制：不能确认 child/FD/后代已停就持续占额和物理槽，可能降低活性；这与现行 fail-closed 选择一致，不是新的兼容性缺口。已知 task 的合法 poll 仍按真实适用 HTTP/RPS 维度有界开放；不能以“安全”为由无据封死不新增 task 的核对，也不能豁免未知适用维度。无可证核对通道/有限上界的异步组合保持不启用。

## R02：新浏览器、重载及旧 token 攻击

构造前端 L 与身份后端 I：L 无 Cookie、无 CSRF token，只发送受托精确同源 Origin、application/json 与固定 X-RAG-Login: 1；I 按 C5 执行匿名登录独立路径。I 不再要求不存在的前置会话/token，因此首次登录可达。成功后撤销携带的旧会话、建立新会话和绑定 token，经 no-store 响应交 L 内存；L 的后续认证写用精确 Origin 与该 token。

再构造重载：L 内存 token 丢失，但 Cookie 有效；同源、当前认证的 no-store context GET 可重新取得本会话 token。不存在“为取 token 必须先带该 token”的循环。跨源/null/缺 Origin、form/缺固定头登录均在建会话前 403；固定头不能替代退出/上传/改密/业务写的会话 token。旧会话 token 不能绑定新会话；Cookie+Bearer 仍整拒，不回退另一渠道。

合理限制：Origin 可信比较值来自受托部署的 scheme/host/port，不从任意 Host/转发头反推；CORS 关闭并不独自完成认证。S1 必须实际证明浏览器、代理与该路径配合正确，本文没有取得这项成绩。匿名独立路径不增自助注册或新的匿名状态服务。

## R03：应用重核之外的缓存攻击

构造资源服务 R 与 gateway G：R 正确当前鉴权，G 若缓存 A 的合法私有 body，B 后续访问同 URL 就可能绕过 R。但该 G 不满足现行 R4：私有路由须同时关闭 proxy cache、no-cache 与 bypass，不能继承上层缓存，不能经 error_page 回到可缓存路由。C2 的 no-store 覆盖 Web/program、成功/错误、认证/context、原件与引用，不能用“错误不是正文”保留缓存。首版不发 ETag/Last-Modified/304；If-None-Match/If-Modified-Since 仍到当前鉴权入口，不能以旧副本兜底。

再构造浏览器 UI U 与合法服务 R：A 页面进入 bfcache，另一标签页换为 B 或撤权；返回 A 页面时 context 仍可成功，但内容依赖已失权。C4 要求 pagehide 同步遮蔽/清私有 DOM、状态与 blob URL并废旧代次；pageshow 含 bfcache/普通历史恢复必须保持遮蔽、清旧 context、生成新代次，再取当前 context并逐项重核全部原依赖及资源，重新取数后才显示。只查 context 然后展示 A 快照，或让旧异步回包写新代次，都违反 C4/AD-12。no-store 没有被当作 bfcache 自动清空证明。

合理限制：目标是应用控制的后续读取/恢复，不追回用户已合法看到或保存的字节。旧浏览器历史的实际事件时序与 gateway 错误响应须用真实浏览器和网络记录验证，不能拿清 Pinia 或中间件单测替代资源/历史各入口的门槛。

## R04：合法主动语法、响应头及预览攻击

构造 parser P 与资源交付服务 D：合法 UTF-8 TXT/MD 含 HTML/脚本示例，P 不执行且提取视图清洗，但 D 想将原件按上游 text/html inline 返回。P 可合规，D 明确违反 C7：所有支持原件一律 attachment、nosniff，服务器按已校验格式映射准确 MIME，TXT 为 text/plain、MD 为 text/markdown；不能透传客户端/上游 Content-Type 或 Content-Disposition。PDF/DOCX 原件同样 attachment，因此不存在“只有文本下载安全、PDF 仍同源 inline”的合法分支。

换用恶意原文件名注入 CRLF、路径或重复 filename 参数也无合规分支：D 须产生稳定 ID+已核扩展名的有限 ASCII fallback，UTF-8 filename* 经规范编码器处理，移除控制字符与路径片段、限制长度，不拼原始 header。仅设置 nosniff 却保留主动类型并不足够，现稿要求类型与 attachment 同时满足。

构造 preview V：如果把原始 PDF/SVG/HTML 或上游响应直接嵌入，V 违反 C7；inline 只准本机解码/重编码并核格式、像素与字节上界的 PNG/JPEG，且映射可信 locator。文本/MD/提取走受控 JSON 字段和 textContent/既定清洗，不插原始 HTML或抓远程资源。R4 又禁止静态目录、任意 X-Accel-Redirect 或签名 URL 直出绕过应用规则。

合理限制：attachment 不承诺用户另存后在其他程序打开绝无主动行为；现行产品未新增主动内容预览，因此不要求再造隔离 origin/sandbox 产品。运行中是否真实执行了格式核验、重编码和安全响应头，仍须 S2 取得证据。

## 保留的不变量与有限同步抽核

三件仍保留四场景、K≤5与原质量门槛，见 [AD-10](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:117)。[C8 本地 gate](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:151)，范围：151–153，及 [R1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:15)，范围：15–17，继续规定两个独立全系统 gate 各默认4、允许1–4，本机重阶段槽1，原任务2h绝对 deadline 包括排队/等待/重试且不刷新。rate charge、未知远端组件、业务 gate 与物理槽没有被合成一个可一起释放的计数。

作为附加抽核，检索并阅读了本轮新增的 [实施契约登录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:17)、[停发窗口](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:266)、[HTTP](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:343)、[媒体](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:180)，[切片开放门](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md:52)，范围：52–70，以及 [EXPERIENCE 全局恢复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md:173)，范围：173–175、[页面共同规则](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:11)，范围：11–41、[AC-01](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:28)、[AC 媒体](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:109)及[AC 历史恢复](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:181)。所抽段落没有与签署三件相反的规则；完整十二件 reconcile 仍由其他独立镜头与根代理负责。

## 结论与适用限制

**PASS；material findings = 0。R01、R02、R03、R04 的规划修复可关闭。** 各项运行正负例和故障注入继续按已写入的 S0/S1/S2/S3/P0 门槛执行；不能用本报告替代成绩，不能据此开放尚未通过的真实外发、资源或身份入口。若实现时无法满足监督停发、时基包络、实际供应方维度或浏览器恢复门槛，应按现行停止点保留阻断，再处理对应实现/接入问题；不以放宽四场景、K、并发、原期限或质量标准消除失败。
