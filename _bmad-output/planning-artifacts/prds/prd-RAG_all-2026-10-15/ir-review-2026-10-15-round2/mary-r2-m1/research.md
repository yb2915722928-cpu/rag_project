---
type: technical
shape: select
topic: R2-M1生命周期闭包
decision: PG代次加本机有界执行者和清理屏障、调用意图
source: 本轮官方文档与固定SHA源码
status: complete
created: 2026-10-15
updated: 2026-10-15
verified_claims: 0
unverified_claims: 10
---

# 决策摘要

选择PG短事务/代次、独占attempt资产、有界可停止写入者、清理后释放、发送前持久意图的组合。它填补四个具体边界，不更换既有同步FastAPI栈、单文档worker或云MinerU路线；不增加队列服务和外发代理。机制、初值、字段、条件提交和负例已在[主答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/answer.md:1)，供John评审后整合。

主要限制：PG条件提交只约束DB。[2] 本机超时不代表执行者已经退出；文件名消失不代表占用释放。[3][5] MinerU在PUT后自动解析，本地取消不能据所读协议推为远端取消。[1] 所选方案明确保留近网络检查后的竞态和unknown成本，不宣称exactly-once。所有能力均未实施/实测。

## 协议与实现现实

MinerU精准API为厂商托管异步提交/查询；官方所读data_id描述是业务关联标识，未给本题所需的去重/反查/取消保证。默认pipeline和可选vlm、另一个Agent轻量API属于不同协议选择，不能把本地开源MinerU或轻量API能力移植到本项目精准云API上。[1]

WeKnora所读上传入口先SaveFile再DB创建并入队；local文件实现不等于全部部署的默认文件后端。[6] 已读任务按attempt和删除/取消状态跳过，删除先标deleting并尽力出队；这只证明所读路径，不能推出每次外发或物理写入都被强隔离。[7] span可记录阶段，但写入失败路径并非必须阻止发送的计费门。[8]

MaxKB所读文档路径保存原件再分段，文件压缩写PG large object，QueueOnce按document_id去重，删除关联数据。[9] 所读模型调用路径返回后才算token写context；流式token估计异常有设0分支；不能把这当本项目真实未知成本规则。[10] 两仓自托管实现均不是厂商API的幂等承诺，未做全仓审计或运行故障结论。

## 机制边界与组合推论

PG行锁可串行过期、取消、完成、容量转换及guard判断，SKIP LOCKED可分批扫描队列行；它不自动约束进程文件和HTTP。[2] Python提供进程终止/等待手段；flock提供本机协作屏障但可被有权限者绕过，需要所有入口遵守稳定锁文件协议。[3][4] 因此最小方案同时需要业务撤资格、可确认停止的写入者和独占资产路径；仅重复查询状态或多清扫几次无法推出清理闭包。这是针对需求的设计推断，未称上游项目已经采用。

## 方案选择与代价

硬门槛由已授权需求设定。主答矩阵权重50/30/20：仅DB/清扫方案2.4且不通过硬门槛；本机闭包3.7；新队列/对象存储/统一外发代理3.1。评分是设计判断。选择本机闭包，增加有限子进程监督、调用意图和资产回收状态；额外RSS与目标主机总预算必须在P0测。runner-up只有在未来多主机/吞吐确需时才重新评估，不能把新增代理当网络原子性解决方案。

建议绑定：实施契约§2上传TTL/调用意图/回收条件；§3的guard写意图与物理预算分离；S0本机监督及暂存范围；S2竞态验收。保留旧版、历史来源、真实未知成本、四场景、K=5、32题门槛不变。

## 反向证据与未证范围

本轮未启用独立red-team或fanout，遵从明确focused run。最强反对理由是子进程监督增加复杂度，且取消至实际停止存在时间窗；主答要求停写证据失败时阻断清理释放，不伪装零费用或永远无残留。没有证据证明本项目在4GB内已可运行。

未证：MinerU去重/反查/取消/删除、费用回填与结果保留期限；具体千问SDK重试/usage；上传框架/代理暂存是否均纳入监督；Ubuntu真实回收、磁盘峰值与RSS。S0假件和P0真实调用验证这些条件。此处是已选可验证方案，不以协议空白要求用户再次预算或确认。

## 来源索引

访问均2026-10-15。源码行号与快照哈希详见[evidence](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/evidence.md:1)及其manifest。verified按技能严格含独立发布者复核，故同一官方/源码发布者的事实均诚实记unverified、中置信度，不意味着伪造来源。

| 编号 | 支持内容 | 发布者与链接 | 发布/版本 | 访问 | 置信度 |
|---|---|---|---|---|---|
| [1] | 精准云API上传、自动解析和标识边界 | [MinerU](https://mineru.net/doc/docs/) | 发布日期未标 | 2026-10-15 | 中，unverified |
| [2] | DB行锁和SKIP LOCKED边界 | [PostgreSQL SELECT](https://www.postgresql.org/docs/18/sql-select.html#SQL-FOR-UPDATE-SHARE)、[行锁](https://www.postgresql.org/docs/18/explicit-locking.html#LOCKING-ROWS) | PG18文档 | 2026-10-15 | 中，unverified |
| [3] | 本机进程超时、停止、等待 | [Python subprocess](https://docs.python.org/3.12/library/subprocess.html#subprocess.Popen.communicate) | 3.12，页更新2026-10-01 | 2026-10-15 | 中，unverified |
| [4] | 协作锁/FD生命周期 | [Linux man-pages flock](https://man7.org/linux/man-pages/man2/flock.2.html) | 6.19，页2026-02-08 | 2026-10-15 | 中，unverified |
| [5] | unlink后的打开FD占用 | [Linux man-pages unlink](https://man7.org/linux/man-pages/man2/unlink.2.html) | 访问版本，日期未摘 | 2026-10-15 | 中，unverified |
| [6] | 上传和local文件 | [Tencent/WeKnora create](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_create.go#L165-L245)、[local](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/file/local.go#L48-L96) | 固定a37a1bc，提交日期未查 | 2026-10-15 | 中，unverified |
| [7] | 任务和删除入口 | [Tencent/WeKnora process](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L3651-L3715)、[delete](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_delete.go#L483-L630) | 固定a37a1bc，提交日期未查 | 2026-10-15 | 中，unverified |
| [8] | span阶段记录路径 | [Tencent/WeKnora span](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_span_tracker.go#L422-L490) | 固定a37a1bc，提交日期未查 | 2026-10-15 | 中，unverified |
| [9] | 原件/文件/向量任务/删除路径 | [1Panel-dev/MaxKB document](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1255-L1284)、[File](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/models/knowledge.py#L367-L434)、[embedding](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/task/embedding.py#L61-L92) | 固定0fa9a0d，提交日期未查 | 2026-10-15 | 中，unverified |
| [10] | 模型调用后token记录 | [1Panel-dev/MaxKB base_chat_step](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/chat_pipeline/step/chat_step/impl/base_chat_step.py#L725-L753) | 固定0fa9a0d，提交日期未查 | 2026-10-15 | 中，unverified |

## 复查时效

见[机械生成复查表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/staleness.json)。无发布日期的来源用**本次观测日期**安排复查，未把访问日期伪装成发表日期：云API最早2026-11-15或P0接入前（取较早）；固定源码结论只绑定SHA，不自动声称代表新版；本选择超过两个季度需刷新。Refresh/Deepen沿本目录进行。
