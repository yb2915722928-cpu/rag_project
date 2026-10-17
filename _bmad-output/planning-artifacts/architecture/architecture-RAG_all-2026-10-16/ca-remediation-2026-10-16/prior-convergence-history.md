# 上轮架构修复沿革（历史）

以下内容从需求追踪原§7归档，仅保留形成过程；本轮现行规则与IR以canonical文档为准。

本轮B新发现的控制行锁前缀反例已在实际AD3/C4/R3关闭；无产品选择冲突。A互审后runtime修复了child持锁/多prefix顺序、冻结包写入范围；真实PG/Linux成绩仍留原门。五状态最小DTO与有限cursor/时间窗已由A实际补C5/C7，B逐项核对关闭其规划缺口。独立rubric发现共享provider账号分进程限流可超额，A接受并补AD2/3/11与C8，B已实际读C8并同步R1/3/6；session续活等不能SH升级也已实际补C5。B3再次实读C8唯一release_transition_id与R5恢复未决调用规则，确认响应/核对只一次归还、ledger迟到账不退permit，以及恢复pool持久态统一blocked_unverified、窗口到期不解远端并发unknown，规划反例关闭。本轮独立review、修后复核与最终字节范围见[最终gate索引](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/reviews/finalize-gate.md:1)，B的当前权威结论见[最终实际稿核对](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/winston-b-final-check.md:1)；这些均为规划层证据。

本轮对抗H1/H2进一步发现异步task已满后poll再抢新增task名额、恢复整pool阻断已知原task核对会使必要流程无法推进；现C8/R1/R5按真实适用维度/动作、每(call,dimension)唯一组件终态及恢复逐维放行收口，不假拆池；官方上界须覆盖最晚实际到达时刻。用户随后明确提高异步并发，现行实施契约§2.6原位采用doc_active_job与external_async_task两个全系统独立gate各默认/上限4（可配1–4），本机重阶段仍1，原2h含排队/等待。job终态只释放active_job，未知task跨失败/重启仍占taskgate阻第5项；4个远端pending可与有限新本地预处理元数据共存，不各持线程/正文/Session。S0假件与P0任务池1/4的满池poll/公平/取消/unknown/恢复/三账/并存资源为必需证据，4不是账号额度或4GB已验；独立delta及最终实稿仍以最终gate/检查为准。

