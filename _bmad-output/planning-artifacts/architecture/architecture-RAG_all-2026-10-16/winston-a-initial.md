# Winston A 独立初评封存

时间：2026-10-16；模式：CA、headless、create、initiative、build-substrate。此稿在读取 B 初评前封存。不是产品/代码/部署验收。

## 输入盘点

现行输入是 PRD 主目录中的 prd/addendum/summary/technical-decisions-dialogue、ir-review-2026-10-15 下的 implementation-contract/implementation-slices，以及 ux-RAG_all-2026-10-16 的 README、DESIGN、EXPERIENCE、page-contracts、wireframes/key-surfaces、handoff、acceptance。上述全文已读取；snapshots/baseline/imports/.working 不作现行政策。根目录仅三份工程记忆材料，无应用代码，故 intent=create。resolver 成功；代理/CA hooks、persistent_facts、external_handoffs、on_complete 均为空。

## 独立判断

现行产品行为充分，主要架构风险是跨开发者实现缝隙，不能靠历史 PASS 消除。暂判 CA 草拟准备充分；交接尚未通过。

1. **High：事务与模块所有权仍未落架构。** 现行契约规定同事务发布、计账、安全台账，但开发者可能分别给文档服务和索引服务写 active_version、给任务和存储各写清理释放。需要一张唯一写者表，以及应用用例在单 UoW 中协调所有者的规则；禁止模块自主 commit 和跨模块写表。
2. **High：共享来源/执行快照/能力配置类型还可分歧。** 后端返回页坐标是像素还是归一化、清洗前后 offset、前端使用 generation 还是 version_id，都足以使分别合规的来源与 UI 不兼容。需要对 Locator、EvidenceSnapshot、AuthContext、ExecutionFence、effective_limits 设共同表示和版本。
3. **High：同步 HTTP 与受监督执行槽的物理关系未明确。** 不能用 FastAPI 默认线程池或线程超时当物理停止；需要定义 API 控制器、子执行者、worker 心跳、PG lease、OS 生命周期锁的进程边界和重启屏障。
4. **Medium：管理写、凭证显密和失败恢复需技术补齐。** 现行 UX 不自动重发，但密码长度、会话失效、管理乐观并发、有限列表、来源资源缓存策略仍需一个共享技术契约，避免双方随意选择。
5. **Medium：运行种子需核实。** 已定主栈与四服务不重选；精确版本和启动工具应官方核对后定冷启动种子，并与 S0 锁文件/目标镜像验证区分。未知运行模型/维度 D/账号限额属于 P0 有期限的实施 gate，不是假定无限或当前架构 blocker。

## 方向及现实备选

继承模块化单体；用例层依赖领域/端口、基础设施实现端口，HTTP 与 worker 只调用同一用例。拒绝引入事件总线/微服务/Celery，因为既定 PG 同事务及四服务可覆盖本期，不以增加服务掩盖一致性问题。也不把“全共享 ORM 任意写表”作为模块化方案：可保持单 DB，但每实体唯一模块写者，用例统一事务。

RAG 保持显式步骤；query/application 只组织证据与结果，不拥有资料/授权真源。documents 负责 active_version/candidate/墓碑；indexing 负责 profile/generation/vector；runtime 负责调用/槽/资产与物理停写；operations 负责逻辑幂等与次数终态。需要 B 反驳这些边界是否造成双写者或过度拆分。

前端采用官方 create-vue 的 TypeScript/Router/Pinia SPA 起点（先核实时下默认），保留 Element Plus。全栈 starter 若自带 React/异步 ORM/外部队列会冲突，后端以官方 FastAPI 最小应用起步而非改写既定技术。版本不凭训练记忆填写。

## 关闭条件

主干 AD 有 Binds/Prevents/Rule；每维度已决定/合理延后/真实 blocker；跨模块唯一写者、类型、事务和执行边界可执行；B 反例闭合；官方技术证据落盘；lint、rubric 与两条默认独立审查实际完成并核对最终修订。可实施范围严格为 S0 可独立开始，其余遵循 P0/S1–S7/F0/SM，不将架构交付当运行通过。
