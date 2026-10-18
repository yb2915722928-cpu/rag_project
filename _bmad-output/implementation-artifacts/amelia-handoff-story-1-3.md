# Amelia 自动接力 Story 1.3

你是同一已保存rag项目的新Amelia主控，仅接续1.3。用户已授权当前Sprint逐Story开发、例行阶段/修复/验收及自动新会话接力，不需再次确认。实际主模型须为 `group/auto-gpt-6-1-sol / max`；不直接写应用、测试、部署实现。

先读[1.3短工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-3-working-set.md:1)、[AGENTS](/E:/aaa-project/rag/AGENTS.md:1)、[relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)。唯一handoff `88707639-db55-47b4-b72e-f7185237eec5`，源owner `01a14b42-689c-7533-90a3-9bd187d93039`。先合并一次模型/会话/认领诊断，匹配待交接thread后写owner为本ID、handoff_accepted=true及实际context，再开发1.3；不新建第二owner，不重开1.2。

1.2原四AC全过，[验收快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-final-acceptance.json:1)、独立与审查报告均passed，无遗留实现写者。源主控在你接手后释放，不与你并行写。1.3唯一依赖1.2已满足。

使用bmad-build；后端/全部RAG明确 `zayuapi/deepseek-v4.1-flash` 默认，独立Step5默认，审查新6.1Sol/medium。按[原1.3 AC](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:210)完成一个完整Story；全过再同项目新Amelia接1.4，继续用户授权的Sprint，不把普通阶段当停点。

用户最新要求：可借鉴WeKnora/MaxKB源码，不要求从零写；记录实际采用来源。加快推进，禁止多轮READY/反复确认/长方案等待及泛化检查；复用未变证据，只运行必需AC与实际缺陷相关回归。独立验证可复用专属资源，不为形式重建整套环境；通过后一次验收记录与交接。

运行只经Netcatty Linux、精确3.12.8，先get_environment确认session。工具命名空间未暴露时，已配置的官方stdio启动器也可用：只读 `C:/Users/29157/.codex/config.toml` 的netcatty-external选定字段，使用配置的discovery文件和官方MCP脚本，勿输出凭据/改用直接SSH。本地只开发文档；双远端同commit后服务器仅Gitee固定提交，禁止server覆盖。

按需回读：1.3原epics、架构C8/R1/R2/R7-R01、UX补充R01、相关源码；1.2完整文档只在实际接口/回归依赖变化时读。旧失败、受测commit/hash及未来边界保留，不重标。
