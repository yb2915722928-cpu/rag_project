# Winston B3 接续记忆

2026-10-16；本文件是恢复记忆，不是最终gate或运行成绩。最新权威最终结论仍须读[winston-b-final-check.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/winston-b-final-check.md:1)。

- 工作区：[架构主干](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md:1)及四companion。A3独占主干/shared/technology/memlog，B3独占runtime/traceability/B-debate/B-final-check。B本轮获授权同时仅修现行上游实施契约的文档并发技术seed/相应锁序；A负责历史技术对话末段追加override，旧对话不改。
- 已激活架构师与架构技能、实际resolver成功：activation hooks与persistent facts均空；headless/create/initiative/build-substrate。工具用 `E:/government/python3.12.8/python.exe -B` 运行脚本，避免uv外缓存限制；命令直接 `& 'rg'`。
- 当前语义稿已冻结，A保存[semantic-snapshot.json](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/reviews/semantic-snapshot.json:1)含七件当时全文/hash，以便最终仅metadata差异可证。B不得继续改五主件/contract语义，除非reviewer有新实质发现并与A协调。
- 三独立镜头：rubric已PASS且其历史反例/追加重复release反例均关闭；技术完整审查已PASS/material0，待此次H1/H2+用户4档改动的原镜头delta；fresh对抗原H1/H2 High已实际修，当前正在正式修后实读/hash报告收尾。不能以旧PASS签新字节。
- H1：原task满池时poll又抢新增task名额造成无法正常终结。H2：恢复整pool blocked与逐动作只读放行不共判。现C8按真实RPS/TPM/HTTP/task等维度/动作映射到唯一permit组件；submit新增task，原ID poll不新增task但仍领实际HTTP/RPS等；accepted仅释HTTP，task终态才释task。恢复逐维/动作核验，未核task维仍禁新submit，已核原ID只读可开放；不假拆池，正常必需流程不能靠无限人工。P0不证满池活性/有限官方上界则不启能力。
- 每(call_id,dimension_id)唯一release_transition_id，原子只归还相应本地taskgate/账号/用途维度一次；ledger迟到事实不退permit。官方上界须覆盖call最晚实际到达时间，不能may_have_sent本地时间+厂商时长自证，缺收达依据继续unknown。
- 用户新增指令：提高异步任务并发。root IR已接受A/B方案：doc_active_job_limit与external_async_task_limit两个全系统独立PG gate各默认4、可配1–4，所有账号合计而非每账号各4。queued不占active_job；worker领取开始处理同UoW占，业务终态/fence一次归active_job；submit may_have_sent同UoW占task及真实适用组件，unknown跨job失败/取消/重启继续占。旧4个unknown可与新4个有限本地预处理job元数据共存，但第5个remote submit仍被global taskgate拒；计数并非job/task元数据合计4。
- 本机重阶段槽仍1（下载/解包/校核/embedding/单次HTTP），受控child/FD完成并退出后返本地槽；remote pending只存持久ID/fence/原deadline/permit，不持Session/正文/每任务常驻线程/child；有限轮转每job每轮一个到期阶段，due poll优先于新submit，未到期不忙轮询，因此真实远端可重叠4而非第1项terminal后才第2项。原2h从原件受理起算含排队/等待/重试不刷新。
- C4/AD3/R3锁序最新：账号控制行升序→space升序→KB升序→业务类别/ID→空间容量/日桶→文档本地gate ID→provider pool ID→call ID→permit组件ID→asset ID；不需类跳过；独立release也gate→pool→call→组件；迟到账仅call不反向取gate/pool。普通鉴权SH不顺带touch/rehash；整体用户删除仍actor SH，后台免actor仅已受理库意图。
- C7空库已明确active_generation_id/embedding_profile_id可null，不伪造尚未定profile；active代必须已证不可变profile，rebuild非null须有target profile。
- B已同步R1/R3/R5/R6/R7、矩阵§2.6/§3.8/§4.2/NFR4/AC22/S0/P0与§7；[互辩§6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/winston-b-debate.md:51)保存本轮事实（行号待最终核）。上游[实施契约§2.6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:107)已原位同步用户新seed；历史technical dialogue由A追加override。
- 语义稳定时B实际hash：runtime `70FA034F0A2255367F2830C6B90B55DA46138A4FB61687749D035DC2C850CD6C`，traceability `BE60629E093A4C558417C292BDF53CB3A027B3984045521269A4CF347C5C022F`，implementation-contract `9695CAEC3D1505432AA1BA0999D501DB22B99F4F3EF8AB64BF42D9304B636D4F`。这是语义稿不是最终metadata后hash；最终必须重新计算。
- B最新机械核：六文件（五主件+B-debate）本地绝对链接69个，缺目标/越行0；矩阵FR16/NFR6/SM7/IA12/G12/AC23行编号全齐无越号。这个检查不是实现/语义/独立gate通过。

## 下一步唯一顺序

1. 等A通知对抗正式修后PASS与原技术delta关闭；不抢签。
2. B将runtime/traceability的draft/working状态改final规划规范；将“最终gate待完成”现行措辞改指当前finalize-gate，历史演进留在B-debate/历史段，不改语义。先通知A完成，不先取最终hash。
3. A改主干/shared final，做最终lint、metadata-only diff及reviews/finalize-gate.md索引，然后明确五主件冻结。
4. B按冻结后当前字节实读五主件、当前三review权威末段、必要上游delta；更新B-final-check顶部为当前权威最终结论/范围/实际hash，保留pre-gate历史且清晰标历史。最终无新material才规划PASS。
5. B向root反馈：S0可独立开工、全计划规划PASS（若实际成立）、真实能力/上线未通过；P0供方/格式/来源/图意/token/R/D/额度、4GB并存、S6可信恢复与备份窗口/受托者、F0/S7原SM均未运行。无必须用户重选产品冲突。root只IR接反馈判最终，不以文档类型硬补epics。
