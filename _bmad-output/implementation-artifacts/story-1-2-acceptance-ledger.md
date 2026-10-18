# Story 1.2 原始验收与证据台账

原始分母是 [epics Story 1.2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197) 四条 AC 的全部实质子句。下表仅索引，不新增验收要求，也不把一行当成一个测试。B169、A干净af6开发者88+48非PG/15PG、C native25及E canonical d6的28真实PG/232非PG均已由主控核原始证据；独立base96c已过311非PG/15PG。E相关增量审查0新增；新E/D独立、D启动及父Story最终门全部通过。各层成绩保留具体源码来源。

| 原 AC | 必需结果 | 实现归属 | 当前证据 |
| --- | --- | --- | --- |
| AC1 | 独立持久 epoch 与 DB 镜像一致；普通重启不换 epoch | A+D | A/base独立已过；D016启动/重启与Step5独立通过 |
| AC1 | 缺失/损坏/矛盾隔离；旧 attempt/epoch/token/租约/期限不能提交业务 | A+C+E+D | A canonical已过；E d6真实context终结/换attempt/旧epoch拒绝开发者通过，独立增量通过；D016运行负例及独立通过 |
| AC1 | 模型/解析/embedding/图意仅显式假件，无实际供应方外发 | C+E | C native/base独立及E d6显式四能力用例已过；E独立增量通过 |
| AC2 | prepared 前后、may_have_sent 后、响应前后崩溃/超时均沿真实路径注入 | A+C+E | E d6开发者13PG/20unit相关节点通过，含真实SIGSTOP/KILL；独立增量通过 |
| AC2 | 原 call 至多一次 grant，重启/重领不恢复重发，unknown 为 NULL+unknown | A+C+E | E d6真实PGunknown/NULL/原call无二grant通过；独立增量通过 |
| AC2 | 真实 Linux 有界受监督 child/IPC、有限停止；未证退出/FD/IPC关闭不复用槽 | C+E | C native25/base独立与E d6真实停止矩阵已过；E独立增量通过 |
| AC2 | child 无业务 DB/主密钥/自主串阶段；秘密不入 argv/日志 | C+E | C真实child argv/env/单阶段/base独立与E d6开发者矩阵已过；E独立增量通过 |
| AC3 | 配置/签名 URL 的 HTTPS、准确 host/port、有限长度、拒 userinfo/fragment | B | B开发者及base96c独立通过；E d6相关回归未改B |
| AC3 | 全部 A/AAAA 任一非公网拒绝，实际连接绑定已核 IP，TLS 主机校验保留 | B | B显式DNS/TLS假件开发者及base独立通过 |
| AC3 | DNS变化无重解析绕过，redirect不跟随，API Authorization不转交下载host | B+C+E | B/base独立通过；E d6凭据/目标实际拒绝通过，E独立增量通过 |
| AC3 | URL/secret不入普通日志；目标守卫失败实际阻断 | B+C+E | B/base独立及E d6开发者通过；E独立增量通过 |
| AC4 | 终结业务/旧epoch下可信迟到usage仅按call幂等追加 | A+C+E | A canonical/base独立已过；E d6可信迟到/终结真实PG通过，E独立增量通过 |
| AC4 | 冲突保留双方来源，不改业务/产品次数/会话/许可 | A+E | A/base独立与E d6真实幂等/冲突不复活通过；E独立增量通过，未来业务表不伪造已验 |
| AC4 | 真实PG负例证明锁序，迟到账仅锁call，无网络/进程等待占事务 | A+C+E | A15PG/base独立已过；E d6真实PG等待事务外通过，E独立增量通过 |

开发者测试在主控提交同步后，从 Gitee 固定提交运行；服务器活动目录为本地 ext4 上 `/opt/rag-story-1-2`，原始材料归档 `/fileOfRag/testOfRAG/metadata/story-1-2`。首次只准备环境，尚无功能测试：两远端及服务器基线 `1c7aaf704f313b352125f7cf5e50999baafa4e39`；backend tree `610e5c112bdba71e11ce7c12c08ccd5aa2e5f6f1`，contracts tree `de2eab25188b7c935c978ea212f6a3c4e72d299b`；锁 SHA256 `7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed`。新独立开发 venv 使用精确 CPython 3.12.8，`uv sync --locked` 成功，Uvicorn 0.37.0。

Story 1.1 证据保持冻结。本 Story 迁移/启动受影响回归仍要执行；1.3 完整 C8 rate/permit/send_open证明、1.4 writer清理、1.5 S0汇总以及真实供应方/P0/S1/目标部署门均未到期，不借本条签署。无新增 Web 表面，不新增浏览器验收。

B开发者固定源码为 `78402858fb003dfd62d57ed481f4f131e69424bf`：169 passed / 0 failed / 0 error / 0 skipped（153专题、3架构、13 UoW）。[B交付](/E:/aaa-project/rag/docs/story-1-2-b-delivery.md:1)与桶中JUnit/rawlog/source记录已由主控直接读取；JUnit SHA256 `c2d09fc9f41ace428717230569e84a0cb73b796fec02cc29a65fcf15218e3288`。后续A的共享UoW实质变更须执行其相关回归，不把此旧提交169自动重标为新提交结果。

A canonical固定源码 `af6ce5099166960e714a1e8b45f004cc8ac9f77a`：88专题/相关非PG、48runtime非PG、15真实PG全部通过，0失败/错误/跳过。主控直接核JUnit、命令/退出码、15节点名、前后HEAD/status及19源hash零变化。证据根 `/fileOfRag/testOfRAG/metadata/story-1-2/A-canonical-af6ce50`。旧52ccb1f七PG失败与server覆盖试跑7/722通过保留在原`A`目录，后者不计任何固定提交通过。

C native固定源码 `96c64fbab0fa8d3d824f2e592196c02570550c70`：22 child +3架构=25通过，0失败/错误/跳过、退出0；主控核原始JUnit/summary/environment、HEAD/Git clean及六hash零变化。JUnit SHA256 `006ec1258428d614f9bcec0d557ea71fc42af99af2f070da96609ad679907fe5`。原call_dispatch草稿及unit/PG矩阵转A/E完整承接，不视作已通过。

E canonical固定源码 `d6e8a0da94a88199e6c4795f3e10e26c821b454f`：28真实PG（E13+旧必需15）与232非PG（E20/child22/persistence20/egress153/architecture3/UoW14）全部0fail/error/skip、exit0。前后Git clean与三E源/lock hash一致；精确3.12.8/uvicorn0.37/locked sync已核。主控亲读原XML/log及命令/退出码，证据索引见[E canonical记录](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-e-canonical-pass-d6e8a0d.json:1)。首轮f3的16pass/12fail与unit20pass独立保留在[首轮记录](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-e-first-canonical-pg.json:1)，不重标。

独立base96c的311非PG/15PG及对应源码hash不重复验；此次只增量独立E/D。相关正式审查已直接核d6补丁及原始E13PG/E20unit，0新增代码发现，已知E修复具运行证据。D016新镜像/启动重启/负例、Step5独立及相关正式审查均已通过，父Story标记done/passed，依赖1.2的1.3可以接续。
