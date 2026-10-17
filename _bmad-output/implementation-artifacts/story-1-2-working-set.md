# Story 1.2 当前工作集

状态：实现中。B固定源码的Linux开发者169项通过，主控已核原始证据；A补齐I1当前context与锁后DB时钟后再次冻结19文件，待固定提交/实测；C修正已证I2/I3，初稿未发布。父Story全部完成门尚未通过。唯一主控 `01a14b42-689c-7533-90a3-9bd187d93039`，接力 ID `3dff3d78-c0f5-42cf-9860-fc2ad4250ab4`；2026-10-18已收到 `AMELIA_RELAY_RELEASE`。原主控及全部1.1写者已释放，唯一认领以 [relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1) 为准。

## 当前目标与下一步

- 只处理 [Story 1.2：隔离执行并保存每次调用事实](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197)，不在同一会话开始1.3。原AC与必要架构在规格分析时按需回读，工作集不替代验收分母。
- 依赖1.1已done/passed，见 [验收快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md:1)。不要重新开发或全量重验1.1；只有1.2实际变更影响到的回归才执行。
- 初始合并诊断已完成；实际 `turn_context` 为 `2026-10-17T19:06:47.666Z group/auto-gpt-6-1-sol effort=max`；仅核实路由记录，不宣称底层供应方身份。已核对 relay 的目标会话/Story/接力 ID 和 1.1 passed 门。无需重做相同诊断。
- 主会话已用bmad-build完成分析、公共契约和拆分；规格风险线1600自动拆分并保留父Story全部义务。主会话不编写应用/测试/部署实现。
- 当前剩余：原 AC1 epoch/fence；AC2 child/IPC/一次 grant/崩溃；AC3 EgressTarget；AC4 迟到事实/冲突/PG 锁序；全部开发者测试、独立验证和一次全新审查及修复。无新环境阻塞。
- [母规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-isolated-calls.md:1)已按预授权进入开发；A持久化、B目标守卫、C监督分段均低于1600 tokens，A/B/C公共签名已登记。
- A 唯一认领 Euclid `01a14b4b-3d07-7a12-a4ea-8ae0f9db0540`；B 唯一认领 Faraday `01a14b4b-41ea-7bd0-9b61-0e9475aadae8`；C 唯一认领 Heisenberg `01a14b57-dbf8-7e11-8a3f-f678f9146dd0`。均已按[公共契约](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-public-contracts.md:1)收到编码release。A额外唯一拥有共享errors.py的必要有限错误/revision文案；B/C不修改。C的PG组装/夹具等A实际交付，其余集成接口已开放。三者各按子规格文件集；实际路由均为 `zayuapi/deepseek-v4.1-flash / max`，未传推理覆盖。
- I1（原AC1）代码已补并冻结：持久context、3个受控入口、prepare/mark/result锁后DB时钟及实际PG跨lease等待负例，原5方法不变。主控已完整读初稿和所有增量；运行前不关闭I1。A源hash见[A快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-a-source-snapshot.json:1)，19文件仅test_call_persistence.py工作区CRLF→Git LF，双hash及纯换行映射保留，服务器按canonical sha256核对。当前index只含A19文件，C初稿已安全取消暂存、未动工作区。
- B三份源/测试已冻结，主控完整读取2201行实际diff，暂存/工作区均LF、hash见[B快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-b-source-snapshot.json:1)。固定提交 `78402858fb003dfd62d57ed481f4f131e69424bf`，两远端main实测一致；B在Linux3.12.8实测169 passed（专题153/架构3/UoW13），JUnit零失败/错误/跳过，源码hash一致且未修改。已归还terminal；[B交付](/E:/aaa-project/rag/docs/story-1-2-b-delivery.md:1)待主控核原始证据并纳入下一提交。
- C初次四文件已冻结并被主控读取实际差异，尚未发布/运行；原hash保留为草稿来源。I2（物理槽仅内存/按boot分离、proc未知/身份错绑停止）和I3（分段recv未保持绝对deadline）均属原AC2/R1，已交回C在原四文件修正并补对应Linux测试后再冻结。C的本地py_compile仅静态语法，不计Linux证据；调用集成/PG矩阵未冻结。B/C实例保留，不关闭重开。
- 独立验证Pascal `01a14b8d-7d2f-7b62-875b-a324944c561c`（实际stepfun/step-5-preview/high默认）只读ready，未给VERIFICATION_MODEL_RELEASE或terminal；最终固定源码与开发者测试稳定后才运行，原4AC全部子句为分母，不按表行计数。正式全新6.1Sol/medium审查尚未派发。

## 已核实可复用的基线

- 功能源码25232d0；本地和两远端交接基线 `96e7fb3ee94c025c3fae804ddabf8ad71d8b08d5`（只读查询两远端一致）。GitHub/Gitee正常无人值守push已成功，服务器只从Gitee拉固定提交并核源码。
- GitHub凭据已存keyring并绑定稳定 [gh.exe](/C:/Users/29157/.codex/tools/gh/2.102.0/gh.exe)。本机GitHub访问复用Windows现有代理的进程配置；代理地址变化时读当前设置，不重新设备登录。Gitee公开读取不需凭据，既有写凭据实测有效；不输出token/DSN。
- Netcatty主机120.53.251.166，实际使用先get_environment。应用/构建/测试只在Linux，精确CPython3.12.8/Uvicorn0.37.0、PG18.6/vector0.8.7。活动目录 `/opt/rag-story-1-1` 为本地FS，证据 `/fileOfRag/testOfRAG`，不换大小写、不把桶当DB/锁盘。
- 此次 `get_environment` 已核连接，首选 session `0d682d12-5a9c-4260-85b5-86713c7d4304`；发生重连才刷新。terminal按relay持有者互斥，B已归还，主控核原证据后分配C。
- 工具已实际拒绝含 `$(` 的命令替换，改为直接输出/分步核对后成功；这是已解决的命令语法限制，不是服务器/权限阻塞。后续RPC避免此语法。服务端uv绝对路径 `/root/.local/bin/uv`，默认PATH没有；开发venv为 `/opt/rag-story-1-2/venv-dev`。
- 四服务保留healthy，gateway为同机 `https://127.0.0.1:8443`；API/worker共用已验镜像，最终gateway含R1修复。隔离测试PG在127.0.0.1:55432，凭据只从既有0400文件加载（位置见已发布setup），不要打印。旧数据/镜像/缓存不因换Story自动删除。
- 原clean wrapper退出码未记录、测试浏览器缺CJK字体均已如实登记；前者有BuildKit完成与实际内容指纹直接证据，后者不改变1.1布局/交互结果。不因此重开1.1或循环空会话。

## 角色、并发与节流

- 遵守最新 [AGENTS.md](/E:/aaa-project/rag/AGENTS.md:1)：主控6.1Sol/max；全部后端/部署/RAG为DeepSeek默认；前端需要时Kimi默认；独立Step5默认；正式审查全新6.1Sol/medium。派发稳定ID，父会话核turn_context，不假定恢复关闭实例仍保留模型。
- 1.1的实现/审查实例均冻结关闭，不复用旧写者。1.2的新任务需明确范围/接口/依赖/验收/文件唯一归属，再并行无依赖实现。
- Netcatty terminal在整个外部chat互斥，独立terminal不能解决并发RPC。短批次分配工具时段，后台进程可保留运行后让出调用工具，不让下载等待阻塞其他独立工作。
- 用户长期禁止过度防御性审查：只当前明确AC/已证缺陷/必要回归；允许零发现，不凑问题、不追加泛化硬化或新门。未来任务缺代码按实际归属延期，当前已有缺陷仍最小修复。不以全部未来测试通过作为当前Story前置。
- 完成1.2全部原门后，同样保存短工作集/快照/提示词与唯一认领，自动新建下一Amelia接1.3，核实接手后释放写入；仅循环当前Sprint至完成或用户停止。没有定时自动化。

## 需回读条件

- 规格分析首次读取原 Story 1.2 和有效 Epic 1 缓存；确认公共接口时只补读 C4/C5、R1/R2、实施契约 §2.5 及对应验收分派。
- 只有实际契约/验收/文件归属变动才回读受影响原文。运行环境、认证和 1.1 基线无变化时复用既有证据，不重新全量探测。
