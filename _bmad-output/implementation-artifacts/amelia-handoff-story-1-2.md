# 新 Amelia 接手 Story 1.2

你是用户明确要求创建的新Amelia主会话，本会话只负责一个完整Story1.2。目标模型 `group/auto-gpt-6-1-sol / max`，同一已保存rag项目 `61e1f316-4db1-4b50-a56e-62c5604d7d25`，local，`E:/aaa-project/rag`。不建worktree、不把整个Story交给一个同名子智能体。

先读 [Story1.2工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-working-set.md:1)、[AGENTS.md](/E:/aaa-project/rag/AGENTS.md:1) 和 [relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)。1.1已完成，证据见其验收快照；完整规划/架构只按工作集需回读条件读取。

**初始只读接手阶段**：原主控正在通过create_thread创建你。先做一次合并诊断，确认实际模型/档位、当前Git/同项目会话/relay和运行环境，回复ready；在收到原主控的 `AMELIA_RELAY_RELEASE` 前，不编辑文件、不操作Git写入、不派实现任务。不要问用户确认，也不要把此协调阶段误判为环境阻塞。原主控会自动登记你实际返回的threadId、发布交接并发送该信号。

**收到启动信号后**：重读relay，只有next_thread_id匹配你、next_story_key为 `1-2-隔离执行并保存每次调用事实` 且1.1完成门passed时，认领Story1.2、更新relay/自己的短工作集，并回报接手。随后直接执行bmad-build的分析、公共契约、1600风险线自动拆分、指定模型实现、开发者测试、独立验证和一次全新审查/相关修复。主控只编排/文档/验收，不编写应用或测试代码。不要等用户再次说“继续”。

用户已授权当前Sprint的逐Story串行接力和常规阶段自动推进，包括技能、模型派发、修复、提交、GitHub/Gitee同步及下一Amelia会话创建；授权以当前AGENTS和relay记录为准。最新长期偏好是禁止过度防御性审查：不要求未来业务测试先通过，不凑最低问题数，不追加泛化硬化/新门；有具体证据的当前缺陷才最小修复并相关回归。

GitHub本机授权与Gitee读写已恢复。不要重试旧空仓库/API403/设备登录阻塞。服务器代码只经Gitee固定提交，运行只在Netcatty Linux；现有四服务/测试PG/Node/浏览器/官方镜像和桶证据可复用，不清理其他项目/旧数据。不重开1.1，不重跑未受当前变更影响的套件。

1.2完成后，按同样协议为第一个依赖满足且无认领的下一Story创建新的本地Amelia（明确6.1Sol/max），核实接手后本会话停止写入。接力仅当前sprint-status.yaml，不扩其他Sprint；相同外部阻塞无新工作时保存真实阻塞并停止空转。不要声称已创建定时后台自动化。
