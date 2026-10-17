# Story 1.1 最终验收台账

父 Story：done / passed。最终功能源码：`25232d0bebc230c35837153b6fd572ff734977aa`，GitHub/Gitee已同步；文档提交不冒充新的运行测试。完整逐AC/模型/工件/限制见 [验收快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md:1)。

| 原AC/分段 | 最终结果 | 证据 |
| --- | --- | --- |
| AC1/A1 | passed | 精确CPython3.12.8、正常uv锁/locked、Uvicorn0.37.0；独立非PG514passed，条件skip由真实3.12.3负例另1passed补证 |
| AC2/A2 | passed | 开发者/独立者各8/8真实PG：六必跑及worker TERM/INT；PG18.6/vector0.8.7，迁移/回滚/namespace/清理0，未建生产vector(D) |
| AC4/B | passed | 51正式工件/check一致、17DTO/5枚举，开发者/独立各52/52正负样例；原44/8失败保留，HTTP信封实际修复闭环 |
| AC1/C | passed | 官方create-vue3.23.0 TS/Router/Pinia、真实锁/peer，Node24.22.0官方hash；dd18单元、252开发者/独立R1各14相关回归与type-check/build；真实gateway视口/键盘及真实200%页面缩放通过 |
| AC1+AC3/D | passed | 四服务healthy、原迁移/stop-start退出0、数据保留、网关缓存/维护探针/预算原边界通过；容器实际UID/权限、共享inode、flock互斥/释放和原子替换实测并独立核对 |
| AC3/E/干净重建 | passed | 来源/许可证声明/peer、发布方与实际缓存传输、层/归档hash登记；干净frontend dist一致，clean API/gateway Built及app/venv指纹同；252新gateway另有no-cache exit0 |
| 独立验证 | passed | Anscombe实际Step5/high（默认），Linux514、负例1、PG8、样例52、R1十四及新gateway；原始证据均索引至桶 |
| 正式审查/修复 | passed | 全新Cicero 6.1Sol/medium一轮发现R1/P2，原Kimi最小修复，相关回归及同实例窄复核关闭；无新增发现 |

原四AC、各拆分项与必需回归分母不变。未来comparison/业务上传/真实供应方/目标机及S0整体门按原Story到期，不由1.1提前放行。各历史测试只绑定其原提交/hash，不合并成虚构的一次全量结果。

明确保留两项记录限制：原clean后台shell包装退出码未记录（作业过期），不填假0；直接BuildKit完成日志/实际镜像/指纹支撑真实重建。Linux headless缺CJK字体影响截图字形，不声称该环境完成中文字形视觉评估；布局/实际页面缩放/交互已有真实证据。

原迁移/启停工具观察已脱敏归档 `deploy-integration/lifecycle-original-tool-observations.json`，SHA256 `daeed77fc05261b5e15398697a1a8bf548c841e7ca6ade68e5824e7e178990c3`；容器探针 `locks-assets-uid-probe.txt` SHA256 `f5ae1a320a71ae18a901e149cc5845a6cc6a95ea37c6d69d32f80436ffb072fd`。桶根为 `/fileOfRag/testOfRAG/metadata/story-1-1/`。
