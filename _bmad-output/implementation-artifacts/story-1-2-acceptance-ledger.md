# Story 1.2 原始验收与证据台账

原始分母是 [epics Story 1.2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197) 四条 AC 的全部实质子句。下表仅索引，不新增验收要求，也不把一行当成一个测试。当前状态均为 `not-executed`；开发者交付、独立实测与正式审查须分别记录。

| 原 AC | 必需结果 | 实现归属 | 当前证据 |
| --- | --- | --- | --- |
| AC1 | 独立持久 epoch 与 DB 镜像一致；普通重启不换 epoch | A | not-executed |
| AC1 | 缺失/损坏/矛盾隔离；旧 attempt/epoch/token/租约/期限不能提交业务 | A+C | not-executed |
| AC1 | 模型/解析/embedding/图意仅显式假件，无实际供应方外发 | C | not-executed |
| AC2 | prepared 前后、may_have_sent 后、响应前后崩溃/超时均沿真实路径注入 | A+C | not-executed |
| AC2 | 原 call 至多一次 grant，重启/重领不恢复重发，unknown 为 NULL+unknown | A+C | not-executed |
| AC2 | 真实 Linux 有界受监督 child/IPC、有限停止；未证退出/FD/IPC关闭不复用槽 | C | not-executed |
| AC2 | child 无业务 DB/主密钥/自主串阶段；秘密不入 argv/日志 | C | not-executed |
| AC3 | 配置/签名 URL 的 HTTPS、准确 host/port、有限长度、拒 userinfo/fragment | B | not-executed |
| AC3 | 全部 A/AAAA 任一非公网拒绝，实际连接绑定已核 IP，TLS 主机校验保留 | B | not-executed |
| AC3 | DNS变化无重解析绕过，redirect不跟随，API Authorization不转交下载host | B+C | not-executed |
| AC3 | URL/secret不入普通日志；目标守卫失败实际阻断 | B+C | not-executed |
| AC4 | 终结业务/旧epoch下可信迟到usage仅按call幂等追加 | A+C | not-executed |
| AC4 | 冲突保留双方来源，不改业务/产品次数/会话/许可 | A | not-executed |
| AC4 | 真实PG负例证明锁序，迟到账仅锁call，无网络/进程等待占事务 | A+C | not-executed |

开发者测试在主控提交同步后，从 Gitee 固定提交运行；服务器活动目录为本地 ext4 上 `/opt/rag-story-1-2`，原始材料归档 `/fileOfRag/testOfRAG/metadata/story-1-2`。首次只准备环境，尚无功能测试：两远端及服务器基线 `1c7aaf704f313b352125f7cf5e50999baafa4e39`；backend tree `610e5c112bdba71e11ce7c12c08ccd5aa2e5f6f1`，contracts tree `de2eab25188b7c935c978ea212f6a3c4e72d299b`；锁 SHA256 `7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed`。新独立开发 venv 使用精确 CPython 3.12.8，`uv sync --locked` 成功，Uvicorn 0.37.0。

Story 1.1 证据保持冻结。本 Story 迁移/启动受影响回归仍要执行；1.3 完整 C8 rate/permit/send_open证明、1.4 writer清理、1.5 S0汇总以及真实供应方/P0/S1/目标部署门均未到期，不借本条签署。无新增 Web 表面，不新增浏览器验收。
