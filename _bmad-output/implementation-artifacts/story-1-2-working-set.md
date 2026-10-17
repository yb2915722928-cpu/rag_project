# Story 1.2 当前工作集

状态：依赖已满足，等待新 Amelia 接手；实现尚未开始。唯一认领与启动信号以 [relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1) 为准。

## 当前目标与下一步

- 只处理 [Story 1.2：隔离执行并保存每次调用事实](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197)，不在同一会话开始1.3。原AC与必要架构在规格分析时按需回读，工作集不替代验收分母。
- 依赖1.1已done/passed，见 [验收快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md:1)。不要重新开发或全量重验1.1；只有1.2实际变更影响到的回归才执行。
- 新会话开始先只读合并诊断与确认ready。原主控登记返回threadId、发布交接并发送 `AMELIA_RELAY_RELEASE` 后，新会话核对relay身份/认领再写入，避免同一relay双写；无需向用户再次确认。
- 接手后主会话完成当前Story分析、公共契约和拆分，用bmad-build；规格风险线1600自动拆分并保留父Story全部义务。主会话不编写应用/测试/部署实现。

## 已核实可复用的基线

- 功能源码25232d0；后续完成/交接提交仅元数据，启动读实际Git HEAD与两远端refs，不把旧记录当最新ref。GitHub/Gitee正常无人值守push已多次成功，服务器只从Gitee拉固定提交并核源码。
- GitHub凭据已存keyring并绑定稳定 [gh.exe](/C:/Users/29157/.codex/tools/gh/2.102.0/gh.exe)。本机GitHub访问复用Windows现有代理的进程配置；代理地址变化时读当前设置，不重新设备登录。Gitee公开读取不需凭据，既有写凭据实测有效；不输出token/DSN。
- Netcatty主机120.53.251.166，实际使用先get_environment。应用/构建/测试只在Linux，精确CPython3.12.8/Uvicorn0.37.0、PG18.6/vector0.8.7。活动目录 `/opt/rag-story-1-1` 为本地FS，证据 `/fileOfRag/testOfRAG`，不换大小写、不把桶当DB/锁盘。
- 四服务保留healthy，gateway为同机 `https://127.0.0.1:8443`；API/worker共用已验镜像，最终gateway含R1修复。隔离测试PG在127.0.0.1:55432，凭据只从既有0400文件加载（位置见已发布setup），不要打印。旧数据/镜像/缓存不因换Story自动删除。
- 原clean wrapper退出码未记录、测试浏览器缺CJK字体均已如实登记；前者有BuildKit完成与实际内容指纹直接证据，后者不改变1.1布局/交互结果。不因此重开1.1或循环空会话。

## 角色、并发与节流

- 遵守最新 [AGENTS.md](/E:/aaa-project/rag/AGENTS.md:1)：主控6.1Sol/max；全部后端/部署/RAG为DeepSeek默认；前端需要时Kimi默认；独立Step5默认；正式审查全新6.1Sol/medium。派发稳定ID，父会话核turn_context，不假定恢复关闭实例仍保留模型。
- 1.1的实现/审查实例均冻结关闭，不复用旧写者。1.2的新任务需明确范围/接口/依赖/验收/文件唯一归属，再并行无依赖实现。
- Netcatty terminal在整个外部chat互斥，独立terminal不能解决并发RPC。短批次分配工具时段，后台进程可保留运行后让出调用工具，不让下载等待阻塞其他独立工作。
- 用户长期禁止过度防御性审查：只当前明确AC/已证缺陷/必要回归；允许零发现，不凑问题、不追加泛化硬化或新门。未来任务缺代码按实际归属延期，当前已有缺陷仍最小修复。不以全部未来测试通过作为当前Story前置。
- 完成1.2全部原门后，同样保存短工作集/快照/提示词与唯一认领，自动新建下一Amelia接1.3，核实接手后释放写入；仅循环当前Sprint至完成或用户停止。没有定时自动化。
