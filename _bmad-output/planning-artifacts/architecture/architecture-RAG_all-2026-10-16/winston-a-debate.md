# Winston A — 真实架构讨论

2026-10-16。A/B 初评先分别落盘后才交换。本文只记录真实交流；详细观点各自初评保留。

| 轮次/分歧 | A 的质疑 | B 的回应 | 处置 |
| --- | --- | --- | --- |
| D1 六或八模块 | 六模块把活动索引并入Library、会话并入Query，容易让profile/generation与turn成为两人都能写的共享状态；Query不能拥有次数，资产清理完成与ledger释放不能各自事务 | 接受八个代码模块，明确不是八服务；Query写operation/results，ledger写计账，conversation写turn；execution写asset/cleaned，library写来源 | 采用八模块+唯一写者表。A撤回任何暗示“模块数量越多越好”的读法，只为上述实体划责任 |
| D2 短事务仍会死锁 | B提出space→KB与KB→space各自短事务仍死锁的反例；A接受不靠分层自动解决 | 统一锁序和协调入口，repo不commit，外部等待无Session | AD-3与UoW矩阵绑定全部写入口；迟到成本仅锁call |
| D3 来源与快照谁拥有 | A要求不可让parser/UI/query分别解释坐标与offset；B要求catalog等于实际片段 | Library写归一SourceLocator/version/hash，Query写预算后的EvidenceSnapshot，conversation只引用ID | shared-contracts固定坐标、文本偏移、hash与版本语义；发布/答复契约样例由同一schema生成 |
| D4 同步上传是否真流式 | B指出普通UploadFile可能先无预算缓冲；A接受有限ASGI上传edge，不改变同步业务/ORM选择 | gateway禁上传request buffering，edge有界IPC向受监督writer施背压，应用完成短事务 | runtime companion明确上传edge与def普通路由、预算和所有写入者登记 |
| D5 child无master key仍需调用秘密 | A反驳仅allowlist env去主密钥不足：provider call仍需secret/签名URL，child不可获取所有provider秘密 | 待runtime最终稿核对单次grant私有IPC最小秘密与日志去敏 | 关闭条件：无DB/主密钥，单call最少秘密，经有限IPC注入，不写stdout/日志，不自主后续派发 |
| D6 撤权与派发锁反转 | B2提出查询先KB再主体、撤权先主体再KB的反例；A接受原AD3前缀不足 | 全部当前授权关键事务账号SH/spaceSH→KB；安全子表变更对应控制行EX；操作者/目标/新旧owner先排序全部ID，禁后序升级；库任务不回取用户 | AD3/C4/R3已实际一致；B实读关闭文档级反例，真实PG验证留S1。SH鉴权不得顺手写last_seen/rehash，C5补独立EX短UoW |
| D7 writer锁与备份冻结 | A指出R2控制器先SH与R3实际child持SH可能双持；多prefix无序会反转；关闭业务入口不等于安全/扫描/清理/迟到账停写 | B改controller只预占槽、child自己SH后IPC；prefix稳定序；备份先排空/fence unknown、全写入口冻结，紧急撤权中止包再重冻 | A实际读R1–R7接受，R2/R3/R5均已落盘；OS/FD与冻结故障仍S0/S6实测 |
| D8 五投影与有限管理seed | B指出仅说五状态仍可自造DTO，cursor/时间窗仅说有限不够；A接受 | C5补15min cursor/366d单窗，C7写五投影DTO/枚举/allowed_actions；TXT/MD本地有界结构符合MinerU精准主路官方格式边界 | B已实读C5/C7接受，不扩大额外格式/角色/外发邮件；具体运行门槛仍P0/S1 |
| D9 独立rubric账号总池反例 | 独立reviewer指出API/worker各按一个账号1RPS仍合计超额；A/B均接受 | AD2/3/11+C8由execution唯一写PG账号总池/用途子池、may_have_sent同UoW领call permit；远端未知不归还；响应/核对以唯一active→released同事务归还一次 | B同步R1/R3/R6与追溯；reviewer定向复核，原发现保留reviews，未把有PG表等同并发已验 |
| D10 恢复低计数与同一持久态 | B提出恢复旧包丢失备份后call/inflight，按旧计数重开池仍可超额；A接受新epoch不是供应方终态证明 | C8/R5全部共额pool先blocked_unverified；窗口届满只解除RPS/TPM，不解远端并发unknown；现行接入受托核后逐pool放行。B3另发现R5连字符拼法会让枚举分叉，A同意统一下划线 | A/B3已实读C8唯一release与R5恢复隔离并关闭该文档反例；新的轮询/异步task共额活性候选交fresh对抗镜头，不预授安全结论 |
| D11 正常满task池与恢复核对 | fresh对抗H1/H2构造每call都占新增task、整pool恢复blocked使原task无路核对；A/B均接受两High | 按真实动作/维度领组件，submit增task、原task poll不增task但仍过真实HTTP/RPS；HTTP结束不释task，组件一次归还；恢复逐维动作受控开放。最晚到达界未证仍unknown，P0必须证明正常满池poll，不以人工代正常闭环 | 原对抗已实际重读修后七件并追加PASS；原技术delta复核无技术矛盾，未解决material0。初审反例保留在reviews，不抹除历史 |
| D12 用户提高异步任务并发 | 用户明确要求增加异步上限，旧整文档单槽的技术seed已被本轮覆盖；A/B不将反例1当账号实况 | 两项独立全系统gate各默认4/可配1–4：active_job领取开始才占、业务终态一次释；remote task submit时占、unknown跨业务失败继续占。单重阶段槽1，有限轮转使远端工作真实重叠，due poll不被submit饿死；新增本地gate固定在provider pool前 | 上游现行contract原位同步，旧dialogue保留并追加override；原对抗/技术实际核新delta与七件语义快照均PASS。4档账号/RSS/满池poll仍待P0/S6，不冒充已测或上线 |

技术版本与实际适用性分开：采用官方核实的冷启动版本种子，S0解依赖、镜像digest与构建测试后锁实物；真实模型/维度D/账号限制仍在P0核定，不将新组件版本等同组合已运行。
