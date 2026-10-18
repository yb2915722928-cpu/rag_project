# 通道恢复后续接 Story 1.2

本说明保存未完成工作，**不是已发送的新会话或后台定时任务**。2026-10-18 用户要求新派发使用 `deepseek-v4.1-flash`，去掉前缀；实际接口返回 `Unknown model`，没有创建实例。历史前缀通道两次502/EOF仍保留。当前需接口注册项/配置变化，不对同一拒绝创建空转会话。

作为同一rag项目Amelia主控，使用6.1Sol/max；只续Story1.2。先读[短工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-working-set.md:1)、[检查点](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-checkpoint-2026-10-18.md:1)、AGENTS与relay。1.1已done/passed，1.2未过；所有原AC不缩减，不先开1.3。

1. 用户此次去前缀授权已使用一次，原始拒绝及hash见[派发记录](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-bare-model-dispatch-2026-10-18.json:1)。仅在接口注册项/配置变化或用户改变路由后，合并一次只读模型/会话/relay/认领/环境诊断。确认当前主控唯一性；没有释放/匹配认领不要双写。既有A/B/C和独立基础证据不重探；Netcatty须先确认当前工具与实际session可用，原0d终端未重连不重试。
2. 使用精确 `model="deepseek-v4.1-flash"`，省略推理override，新建E窄修接替实例；不能把旧前缀ID当作该ID已获支持，不恢复已关闭Euclid/Faraday/Beauvoir/Ampere/Halley。父会话核实际turn_context后才放代码。按[E规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-e-dispatch-integration.md:1)只改三现有E文件和交付文档，修F2逻辑/传输purpose、成功/可信晚到测试、实际child kill+PGunknown/无二grant。A19/C4不改，真接口影响由主控协调。
3. 用DeepSeek完成[D必要部署回归](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-d-epoch-deploy.md:1)：固定源码同镜像、专属资源/随机schema、显式维护init、普通RO epoch、合法启动重启与缺失/不可读/矛盾负例。只当前门，不重跑1.1全套/不前移1.5工具；不改旧资源/不把health当资格。
4. 主控管理commit/两远端同提交，服务器只从Gitee取明确commit并核hash；运行/测试精确3.12.8，只在Netcatty Linux，目录/凭据/桶路径见工作集。源码server覆盖严格禁止，失败本地修→发布→固定提交相关回归。
5. 保留的Pascal Step5独立实例 `01a14b8d-7d2f-7b62-875b-a324944c561c` 仅补新E/D；其311+15基础不重跑。保留Pasteur正式审查 `01a14c16-28e7-7c61-8444-de4c9b2ad09e` 仅对E/D实质增量复核，不另开泛化轮，不凑问题。两者再次调用前由父会话读新turn_context确认原模型/档位仍符合；若实例已关闭，按原分工新建正确模型，不能默认恢复原配置。
6. 原四AC、拆分项、开发者/独立/正式审查和具体修复回归全部通过才更新done、保存验收快照及唯一待交接认领；再按用户长期授权同项目新建下一Amelia接首个依赖满足Story。当前未过不得放行；相同外部阻塞无新工作不创建空会话。

需求/公共契约/原规划仅按工作集需回读条件；禁止过度防御性审查与未来测试前置。原始错误/旧失败/覆盖草稿/真实受测hash不追溯改写。用户已授权当前Story常规阶段与修复，无需重新确认规格/继续；只有真实新阻塞或范围外必要输入才请求。
