# edge-case-hunter 独立路径审查

审查输入为本轮 manifest 指定的冻结 snapshot；链接定位 canonical 的同版行。没有应用代码或运行成绩。独立初评阶段未读取旧 IR、旧 reviews、其他镜头输出，也未读取 claims。

## Step 1–2：路径枚举及复查封存

主干、shared-contracts、runtime-operations、technology-evidence、requirements-architecture-traceability、implementation-contract、implementation-slices 均已全文读取；PRD 与 UX 按对应边界回查原文。下表仅记录完成枚举的路径族，不以已覆盖路径充当发现。

| 路径族 | 枚举边界 |
| --- | --- |
| 上传与版本 | 未 PUT、开始、半传、重复带体、完成与到期竞争、候选新旧、首次 partial、完整替换、墓碑、发布、清理 |
| job 与远端任务 | queued/active、submit/HTTP accepted、pending/unknown、poll/reconciliation、终态、到期、本地继续、重启与恢复 |
| gate 与调度 | 两个全系统 gate 各 4、本机重阶段 1、账号/用途池、按维度领还、满池 poll、公平轮转、配置改变、迟发 grant |
| 授权与外传 | 账号/空间 SH、变更 EX、锁集合与顺序、派发前与放行前重核、撤权晚于 grant、读写身份、未登录入口 |
| 三账与恢复 | 原件预留/实占/cleaned、原受理日产品计次、逐 call 成本、迟到事实、冲突事实、旧包低计数与独立 epoch |
| 检索与历史 | 多库兼容、版本/代次固定、重建与删除、K=5、实见 spans、历史证据 GC、来源当前读取 |
| 输入与配置 | H/B/M、码点/字节、完整输出预算、有限值、配置版本、热变、旧 Key/异输入/TTL/墓碑、会话父轮次 |

复查再次遍历上述状态转换与隐式分支后保留以下两条候选。Step 1–2 在读取 claims 前完成。Step 3：本次为完整文档而非 diff，删除检查跳过。

### 窗口释放后仍可消费旧 grant

定位：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:139)，关联 [runtime-operations.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:19) 与 [implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:101)。

精确反例：已核账号 RPS 为滚动 1 秒内 1 次、HTTP 并发至少 2。两个不同用户各持一个合法 API 查询物理槽。call A 在 t=0 的 may_have_sent UoW 领取 RPS、HTTP 组件并得到一次 grant；child 被调度暂停，尚未发送。t=1.1，该旧窗口按 DB 时间自然到期，call B 合法领取新窗口额度并发送。t=1.2，A 恢复并消费原 grant。两次发送都未过各自绝对 deadline、都只发送一次，账号却在同一实际 1 秒窗口收到两次请求。TPM 有同构路径。

现有 guard 为 may_have_sent 时原子领组件、滑窗保守实现、窗口自然到期；仅远端并发的终态上界明确要求覆盖最晚可能到达时刻。一次 grant 与 120 秒级 child deadline 没有将窗口占用延长至其仍可能发送的期间，也没有定义窗口过期后旧 grant 如何失效。这里不依赖撤权、盲重试、多个进程各自计额或上游未核额度。声明可能遭遇厂商 429 不会补上本项目自身迟发许可造成的超配路径。

实际后果：共享池已允许的新调用与迟发旧调用聚集，触发本可避免的供应方限流及已受理业务失败。

最小修复：将窗口到期证明与该 call 的最晚可能到达界绑定；无法证明旧 grant 已不能再发或请求已进入正确窗口时，不回收其 RPS/TPM 占用。若采用有限 send-by，须同时定义超期 grant 丢弃及到达界，不复发原 call。S0 加入暂停 child 跨窗口、其他槽继续派发的确定性负例。

### 首次登录没有会话绑定 CSRF 的可达前置

定位：[shared-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:91)，关联 [implementation-contract.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:312)、[page-contracts.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/page-contracts.md:28) 与 [acceptance.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/acceptance.md:28)。

精确反例：有效账号在全新浏览器首次打开登录页，没有本应用登录 Cookie 或会话绑定 CSRF token。登录是 Web 写动作；C5 要求所有 Web 写动作同时通过 Origin 和会话绑定 CSRF token，但同段仅在登录成功后创建/旋转认证会话，输入包没有匿名会话或登录前 token 的签发/校验入口。UX 正例要求从未登录状态仅填账号密码可达成功。

现有 guard 没有区分未登录的登录 POST 与已有会话写动作。Origin 允许表只是并列条件，不会生成缺少的会话绑定 token；登录成功换会话也发生在该检查之后。所有 snapshot 中 CSRF/匿名/登录前分支已检索复查，未发现 bootstrap 或明确的登录专用规则。

实际后果：按统一守卫实施会拒绝首次登录；若实现者自行跳过全部登录防护，则安全边界由各自猜测产生分叉。

最小修复：明确登录前短寿命匿名 CSRF 上下文的取得、绑定和校验，登录成功销毁并旋转；或者明确登录专用的已选防护规则。已有认证会话的写动作继续用会话绑定 token。S1 覆盖无 Cookie 首次登录及伪造跨站登录两个分支。

## Step 4：claims

Step 1–2 上文落盘后才首次读取 claims。逐项按已追踪的切片前置、两个全局 gate、重阶段、poll、unknown、唯一领还、恢复与运行停止门进行证伪；没有额外的独立 claim finding。完整性叙述与上文反例的关系不重复计项。

封存：仅输出上文两条未处理分支，不读取同伴结果，不修改方案。
