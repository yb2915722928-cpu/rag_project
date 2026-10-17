# RAG_all 技术背景补充

本文保存技术背景、用户已选方向、本轮受托实现选择及待验证事项。功能要求以 PRD 为准，真实交流与取舍集中在 [John—Mary 技术选择与对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md)。

## 1. 用户提供的技术背景

- 融合候选：[Tencent/WeKnora](https://github.com/Tencent/WeKnora)、[1Panel-dev/MaxKB](https://github.com/1Panel-dev/MaxKB)。
- 用户技术栈以 Python 为主，已确认首版 FastAPI＋PostgreSQL＋pgvector；方案参考 WeKnora 与 MaxKB。本轮四个大问题的配套选择已由 Mary TR／TS 与 John 追问收口，见第 8 节；组件版本、具体抽取和环境表现仍待实施验证。
- 用户负责与 AI 核对实现方案和技术栈、深入理解 RAG 流程与项目，实际编码、集成、测试和开发问题记录交由 AI；目标周期约半个月。最新授权 John 自行提问，Mary 先 TR 核验两项目再 TS 受托选择，仅确需本人补充时才问用户。一个 John 大问题由同一 Mary 完成 TR、TS 和追问，闭环后换新 Mary；真实交流形成 [技术选择与对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md)。方案核对完成后在 AI 可用额度内推进，不按用户个人编码工时估算。
- 开发中真实遇到的问题统一记录到 [DEVELOPMENT_ISSUES.md](/E:/aaa-project/rag/DEVELOPMENT_ISSUES.md)，包含现象、定位、处理、验证与相关 RAG 原理，供用户查看和核对；不预填虚构故障或已解决结果。
- 可用资源：一台运行 Ubuntu 的 4 核 CPU、4 GB 内存服务器及一台用户提供为 16 GB 内存的电脑。2026-10-15 读取本机注册表 CPU 名称与 nvidia-smi，确认 i7-12700H、RTX 3060 Laptop GPU、6144 MiB 显存；修正此前“电脑无 GPU”和口述 CPU 型号，内存未复测。Web、后端和 PostgreSQL／pgvector 最终部署在服务器，电脑用于开发调试。用户已明确 API 优先，不依赖电脑持续在线承担模型解析；Ubuntu 具体版本、服务器磁盘与实际可用资源仍待核对。
- 学习与面试：用户未接触本次存储／检索技术，担心面试追问。AI 维护 [INTERVIEW_PREP.md](/E:/aaa-project/rag/INTERVIEW_PREP.md)，从基础原理、真实实现和问题记录逐步讲解，整理追问并练习，不以记住数据库名称或 AI 完成代码代替用户理解。
- 服务器访问计划：用户将安装连接 Netcatty 的 MCP，Netcatty 中已有服务器连接。该 MCP 用于开发部署和服务器操作，独立于产品对外程序 API；具体工具、实际连通及可用操作范围在接入时验证，不据此增加本期 Agent 能力。
- 开发用 AI 资源：用户有两个 ChatGPT Plus 账号、一个阶跃星辰 Pro 账号，并计划经中转 API 使用 DeepSeek；这些资源用于开发。用户仅计划把低重要性的开发任务交给阶跃星辰 Pro，属于其任务分工偏好，不据此判定模型的客观能力。DeepSeek 中转接入方和具体任务分工尚未指定。
- 项目运行与测试：用户选择千问小模型 API，需要使用时再确定具体型号、接入方式及账号并按需充值；本轮不填写固定预算。这与开发用 AI 资源分别记录，不推定开发账号已提供应用运行所需 API、接入额度或能力。
- 用户确认的复用方式：抽取两个项目的部分模块、参考其设计，组织成自己的 Python 项目。
- 项目同时交付 Web 系统和 API，先完成四个 RAG 场景，再扩展其他 Agent 能力。

## 2. 候选项目事实核验

核验日期：2026-10-15。仅检查官方文档及部分依赖文件，尚未运行项目或核验四个场景的完整支持程度。下列版本记录用于追溯资料，不代表已选定开发基线。

### WeKnora

- 核验快照：main 分支的 234aa948db29c10f5ed4b7939285c7b3711c5d4c。
- 核心后端为 Go；依赖包含 Gin。依据：[后端依赖](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/go.mod)。
- DocReader 为文档解析与处理的 gRPC 服务，其依赖文件声明 Python 运行环境。依据：[DocReader 说明](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/docreader/README.md)、[DocReader 依赖](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/docreader/pyproject.toml)。
- DocReader 说明指出，扫描 PDF 渲染后的 OCR/VLM 处理由 Go App 侧调用服务完成。因此，有 Python 解析组件不能证明复杂手册处理流程可直接作为独立 Python 库复用。
- 官方 README 描述混合检索、重排、父子分块与引用能力；实际场景适配及抽取成本需后续验证。依据：[项目说明](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/README.md)。
- 根许可证注明主体采用 MIT，第三方组件保留其各自许可证。依据：[许可证原文](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/LICENSE)。

### MaxKB

- 当前默认分支为 v2；核验快照为 44b438d77830ffdda50cbd88087af075b453e311。
- 官方 README 列出后端 Python / Django、前端 Vue、LLM 框架 LangChain、数据库 PostgreSQL + pgvector。依据：[项目说明](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/README.md)。
- 后端依赖可见 Django 与 Django REST Framework，前端依赖可见 Vue、TypeScript 和 Vite。Python 匹配主要指后端，前端定制仍需相应技能。依据：[后端依赖](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/pyproject.toml)、[前端依赖](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/ui/package.json)。
- 官方 README 描述文档上传、在线资料抓取、文本分段和向量化。这些能力的格式覆盖、接口边界和质量尚未实际验证。
- 源码抽查可见使用 pypdf 的 PDF 解析器与使用 python-docx 的 Word 解析器。存在这些实现，不等于复杂手册的表格、图片、跨页定位等任务已达到本项目要求。依据：[PDF 解析器](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/apps/common/handle/impl/text/pdf_split_handle.py)、[Word 解析器](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/apps/common/handle/impl/text/doc_split_handle.py)。
- 根许可证为 GPLv3。依据：[许可证原文](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/LICENSE)。此处只记录上游声明。

## 3. 已确认的复用方式

用户已选择：抽取 WeKnora 与 MaxKB 的部分模块、参考其设计，组织自己的 Python 项目。

后端方案已确认包含 FastAPI；本轮受托选择模块化单体、同步 SQLAlchemy／Alembic、显式 RAG、自建 Vue 页面及按需参考上游交互。具体代码抽取仍需逐项核验依赖、许可证和改造成本；未将任何上游文件认定为无需适配即可使用。

MaxKB 的 Python 后端与用户技术栈存在直接匹配；WeKnora 的 Go 主服务与 Python DocReader 需要分别评估。当前选择不构成对任一具体模块可直接复用的承诺。

## 4. 角色分析依据与受委托决策来源

用户最初要求采用 Mary 的业务用户与角色分析，随后逐项确认空间和授权方向；本轮进一步授权 John 的其余产品问题全部由 Mary 回答。原先“平台管理员创建团队并指定初始所有者”的候选方案因此转为受委托产品基线，不再标为待用户逐题确认。

角色分析保留以下依据：

- 业务岗位描述需要完成的任务，团队角色描述资源与动作权限；同一人可以兼任多个业务身份，在不同团队拥有不同角色。
- 团队角色、知识库访问范围与库负责人职责分别判定，不能把获授权维护资料解释成可管理该库授权。
- 平台建立团队与团队内部管理分开；平台身份与业务资料读取分开。首版采用所有者、知识维护者、知识使用者，不另建团队管理员角色。
- 个人空间仅本人使用，程序 API 是调用渠道，不能据此自动产生资料分享或独立服务身份。

现行业务用户与任务、角色能力、邀请加入、授权撤销、负责库接管和程序凭证规则统一以 [PRD](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md) 第 2、4 节及 FR-1 至 FR-5 为准。本补充文档保留分析依据和参照，不维护第二份权限规则。

### 官方参照

- WeKnora 将空间角色分为 Owner、Admin、Contributor、Viewer，并在空间与资源层处理授权：[空间与权限说明](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/website-docs/03-features/01-tenant-auth.md)。其文档中的角色名和实现约束不直接等同于本项目方案。
- WeKnora 的系统管理员独立于空间 Owner，跨空间数据访问另行控制：[平台管理说明](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/website-docs/03-features/20-platform-admin.md)。
- MaxKB 官方 X-Pack 文档区分系统管理员、工作空间管理员和普通用户，支持按空间设置角色成员：[角色管理说明](https://docs.fit2cloud.com/maxkb/user_manual/X-Pack/role/)。该文档用于能力参照，未据此认定开源版本具备全部同名功能。

## 5. 技术选型与验证交接

本轮完成产品基线和四个大问题的受托实现选择，尚未运行或验证 RAG_all 实现。上游核验覆盖官方资料、依赖与明确范围内的固定源码；快照、主语言和解析器存在性不等于模块可独立复用，不能把资料描述转成已实现成绩。

| 验证项 | 需要留下的证据 |
| --- | --- |
| 模块抽取边界 | 分别对文档解析、分块、检索、重排、引用定位评估原接口、依赖、能否在 Python 项目中独立使用及改造成本；不能预先把 WeKnora Go App 的能力算入 Python DocReader |
| 复杂手册 | 用规则表格、简单跨页表格、扫描页和含图意问题验证；记录人工校核过程与不支持页面，比较解析结果和引用定位，不能以纯文本通过替代 |
| 检索基线 | 冻结题目、证据单元、模型与版本，最终候选上限 K=5；分别记录检索、上下文组织和回答结果，改进与基线采用相同判定口径 |
| 权限与数据生命周期 | 检索、生成输出前、历史、引用和下载都须复核；验证凭证权限交集、降级与离队、版本切换、删除后关联清理，以及任务重启重试 |
| 运行条件 | 按 Web、后端和数据库同部署于 4 核、4 GB Ubuntu 服务器的目标，验证实际内存峰值和处理并发；补齐机器配置并验证计划中的 Netcatty MCP 连接，在实际接入前确定千问小模型具体型号、账号和充值金额。登记文件限制、超时和配额规则，测量延迟、用量与可取得费用，再确定绝对门槛；项目推理费用与开发用 AI 资源分别记录 |
| 复用与实际参与 | 逐模块留来源、依赖和使用条件核验，区分直接复用、接口适配、行为改造与自行实现；分别记录 AI 的实际实现和用户参与的方案、技术栈及结果核对，真实问题持续写入问题记录 |

当前技术组合和确认来源见第 6.2、8 节；解析采用用户已选 MinerU 云端 API，图意缺口以实际样例判断。选型已收口，具体模块适配、接入、质量和资源表现继续验证，不预先承诺直接抽取或已达标。

## 6. 参考两项目的 FastAPI 方案与本轮选择

用户要求方案包含 FastAPI，并明确参考 WeKnora 与 MaxKB。两项目分阶段研究快照各自保留来源；用户已确认 FastAPI＋PostgreSQL＋pgvector 及其他主栈。本轮最新受托选择以第 6.2、8 节和真实对话为准，历史候选不继续当作待答问题；选择不表示已经适配或测过资源。

### 6.1 实际源码依据与适配边界

| 项目 | 本轮源码核验事实 | 本项目可参考内容与改造边界 |
| --- | --- | --- |
| MaxKB | Python 后端使用 Django／DRF；向量持久化和检索依赖 Django ORM、项目模型及 SQL 模板；向量任务依赖 Celery、QueueOnce 和项目事件系统 | 参考文件上传、按类型解析、段落保存后向量化、检索结果携带来源的流程；切分算法及解析器是待验证抽取候选。数据库访问、任务入口、项目上下文与鉴权需适配 FastAPI 项目 |
| WeKnora | 主要业务、异步导入、分块、索引和问答编排位于 Go；Python DocReader 提供 gRPC 解析，扫描页渲染后由 Go 侧调用 OCR／VLM | 参考入口、业务服务、解析适配器、索引和检索生成的职责边界，保留来源定位。Python 解析器列为候选；Go 业务流程需要 Python 实现，抽取 DocReader 不等于得到完整 OCR／图意问答能力 |

MaxKB 的读取依据：[依赖](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/pyproject.toml)、[上传与文档保存](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/apps/knowledge/serializers/document.py#L995)、[向量存储](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/apps/knowledge/vector/pg_vector.py)、[向量任务](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/apps/knowledge/task/embedding.py)、[检索来源组装](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py)。

WeKnora 的读取依据：[导入业务](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/internal/application/service/knowledge_create.go#L165)、[解析与索引](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/internal/application/service/knowledge_process.go#L4089)、[DocReader 说明](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/docreader/README.md)、[问答流程](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/internal/application/service/session_knowledge_qa.go#L216)。

### 6.2 技术组合与确认来源

| 层次 | 方案与作用 | 确认状态 |
| --- | --- | --- |
| 后端接口 | FastAPI 普通 def 路由承接登录、空间、知识库、查询与程序凭证；模块化单体，HTTP、业务与持久化分开，Web／程序 API 共用核心服务 | FastAPI 用户已选，具体分层 Q1 受托选择；运行依赖版本实施时锁定 |
| 数据访问 | 同步 SQLAlchemy 2＋psycopg 3、Alembic 版本迁移，FastAPI 普通 def 路由；各数据库阶段独立短 Session，外部 API 等待不持连接，不跨线程传 Session | 本轮 Q1 经 Mary TR／TS 及 John 追问后受托选择，替换旧异步候选；连接池与并发参数待目标环境验证 |
| 数据库与检索 | PostgreSQL＋pgvector 同库；授权／活动版本／校核状态过滤后精确向量 B0，初选余弦距离；embedding 与索引独立版本配置 | PG／pgvector 与 B0 用户已选，具体链路 Q3 受托选择；中文关键词、融合、重排、ANN 仍按失败选择实验，效果与容量待测 |
| RAG 核心 | 模块化单体中的显式 Python 步骤，接口／业务／持久化分开，Web 与程序 API 及 worker 共用核心服务；MinerU、向量与问答使用适配边界，首版不引入 LangChain／LangGraph 编排 | Q1 与 Q3 已受托选择职责、分块和检索编排；上游具体代码抽取与适配仍待验证 |
| 文档任务 | PG 持久任务＋独立 Python worker；主线程处理一份文档，续租线程独立短 Session；SKIP LOCKED／租约／attempt 条件提交，失败有限重试、结果未知查原云任务 | 用户已选任务方向，Q2 受托细化；不引入 Redis／Celery，不承诺外部恰好一次或逐页／字节续传 |
| 前端 | Vue 3＋TypeScript＋Vite，配合 Router／Pinia／Element Plus 自建页面；参考两项目交互，电脑构建静态产物 | 主栈用户已选，配套与自建边界 Q4 受托选择；接口、权限及页面主流程待实现验证 |
| 文件与部署 | 受控本地原件／产物目录＋PG 归属；Compose 四服务：Nginx、API、worker、PG＋pgvector；同源代理，原件仅后端鉴权访问，停写一致备份与恢复演练 | Q4 受托选择；低配置初值见对话文档，目标机内存／容量／证书及恢复能力未验证 |
| 可信访问 | PG 服务端 Cookie 会话、Argon2id 密码、用户绑定且仅存 hash 的随机只读 Bearer 密钥；统一后端授权，放行前读当前状态 | Q1 受托选择，沿用既定产品角色与权限；不承诺网络放行与撤权全局原子 |
| 密钥、记录与测试 | 供应方密钥服务端加密／外置主密钥；JSON 运行日志＋PG 审计／用量；pytest、真实 PG 集成与故障、Playwright、独立 32 题评估 | Q4 受托选择，未配置／运行；未知费用不填零，12 份公开／模拟资料仅测试起点 |

这套组合的工程判断是减少独立服务数量，便于在 4 核、4 GB 机器上先做小规模基线；目前没有运行测试，不能据此认定内存和吞吐已经足够。解析峰值、数据库连接、并发与文件上限须实测后登记。

### 6.3 已选调用链与实施验证

- 导入：上传及库权限校验 → 保存原件与任务 → worker 直读文本或调用 MinerU 云端解析 → 保存原包、归一来源及程序校核 → 分块与向量化 → 完整候选原子切换生效。首次部分可用与不完整替换候选按 PRD FR-6、FR-8 区分。
- B0 问答：用户／凭证鉴权 → 限定当前空间、有权库、生效版本与可用来源 → 查询向量化 → 精确向量检索 → 合并并选取整请求最多五块 → 千问问答 API → 结构／引用 ID 与放行前权限检查 → 返回完整答案或可见失败。关键词、融合、重排和 ANN 不在 B0 必经链路，后续由失败样例触发实验。

FastAPI 负责接口与业务入口，RAG 核心模块负责各处理阶段，worker 承担耗时资料处理。持久化任务、恢复和有限重试需要本项目实现，不能把进程内的临时后台函数当作这些能力已经具备。

用户已确认文档任务方向，Q2 已受托细化为 PG 短事务领取、租约心跳、attempt 条件提交与有限重试，文档并发仍为 1。处理阶段、进度、失败原因和上游任务标识持久保存；未知结果进入待核对，不自动盲重交。当前有维护权者可继续核对，或在知情后显式重交；原关联和迟到守卫保留。上述机制待实现验证，不表示已具备恰好执行一次、PDF 逐页恢复或上传字节续传。

向量索引需记录模型标识、版本与维度，查询必须匹配索引使用的向量化配置；千问问答模型的选择不自动确定向量化、重排和图像处理能力。不同模型索引混用、中文型号与错误码分词、权限过滤、表格及图示引用都须用既定样例验证。

数据库队列已选 PostgreSQL SKIP LOCKED，具体锁、超时、恢复和幂等仍须实现测试。机制依据：[FastAPI](https://fastapi.tiangolo.com/)、[后台任务边界](https://fastapi.tiangolo.com/tutorial/background-tasks/)、[SQLAlchemy Session](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)、[Alembic 迁移](https://alembic.sqlalchemy.org/en/latest/)、[pgvector](https://github.com/pgvector/pgvector)、[PostgreSQL 队列锁](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE)、[Vite 构建](https://vite.dev/guide/static-deploy.html)、[Docker Compose](https://docs.docker.com/compose/)、[Nginx](https://nginx.org/en/docs/beginners_guide.html)。

### 6.4 检索基础版与逐轮优化（已确认方向）

用户确认先做基础检索版本，再慢慢优化，每次记录数据变化，用作面试数据支持。以基础向量检索形成 B0；后续根据失败样例选择优化实验，不将此前提出的中文关键词、混合融合和重排一次性视为已采纳的必做清单。每轮比较 B0、上一轮保留方案和本轮方案，保存实际变化及代价，包括无收益、退步和失败。

候选优化包括分块与来源组织、中文关键词召回、融合去重、重排、索引和查询参数；实际选择以问题与数据为依据，保持空间、知识库授权与有效版本约束。是否启用外部重排 API 以质量、时延和成本比较为依据，千问问答模型的选择不等于已选定向量化或重排模型。技术依据：[pgvector 混合检索说明](https://github.com/pgvector/pgvector#hybrid-search)、[PostgreSQL 全文检索与排序](https://www.postgresql.org/docs/current/textsearch-controls.html)。

MaxKB 的中文关键词实现使用预分词和 PostgreSQL 的 simple 配置；WeKnora 所读 PostgreSQL 关键词实现依赖 ParadeDB，不能仅安装 pgvector 就原样使用其 SQL。相关依据：[MaxKB 向量检索](https://github.com/1Panel-dev/MaxKB/blob/44b438d77830ffdda50cbd88087af075b453e311/apps/knowledge/vector/pg_vector.py)、[WeKnora PostgreSQL 检索](https://github.com/Tencent/WeKnora/blob/234aa948db29c10f5ed4b7939285c7b3711c5d4c/internal/application/repository/retriever/postgres/repository.go#L190)。

逐轮记录规范见 [OPTIMIZATION_LOG.md](/E:/aaa-project/rag/OPTIMIZATION_LOG.md)。开发集调优与冻结验收题分开，比较固定证据单元及 K=5 上限；模型、资料、题集或环境变化时登记并重跑可比基线。当前只有记录要求与模板，没有已完成优化或成绩。

### 6.5 Mary TR／TS 文档解析研究与 MinerU 云端选择（已确认）

用户要求 Mary 子智能体执行 TR，核验 WeKnora 与 MaxKB 的本地解析、自托管服务和外部 API 分工；执行 TS，结合当前资源推荐路线，并交回 John。研究请求不代表采纳方案。完整证据和最小验证计划见 [文档解析研究](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/research.md)。本轮只核验官方资料和固定提交源码，未部署或运行样例。

**最新决定覆盖此前推荐：**用户先补充 API 优先及本机配置，再明确“使用 mineru 就行，配置 api 可以上传识别的”。据此确认首版采用 MinerU 云端 API 上传文档获取解析结果，不采用自托管 MinerU，不继续本地 OCR 归因或多引擎对照。尚未配置凭证、实际上传或验证 MinerU 输出；实现仍须接入既定 PG 任务与 Python worker，并校核页码／原件、表格与图意。本文后附两项目事实作为研究背景，不将原推荐 A 继续列为待答问题。

**实现交接。** 首版围绕 MinerU 云端 API 组织上传、处理状态查询、解析结果持久化及失败恢复，具体请求协议与账号限额在接入时核对，不把自托管接口与云端接口混用。轻量文件校验、TXT／Markdown 等直接读取、原件保存、结果归一化、分块与向量化仍在应用侧完成，支持格式以实际验证登记，不能因选定 MinerU 就取消 PRD 的其余格式。

原文件、文档版本、任务与上游标识、解析结果及页／表图位置需要可追溯。表头、行列、关键数值与单位、简单跨页关系、扫描文字、必须看图才能答的题和引用定位继续按 FR-7 验收。若 MinerU 结果不能满足图意要求，形成真实缺口后再讨论补充 API，不提前认定其已覆盖或已失败。

**两项目事实。** 本轮读取的 WeKnora 提交为 `a37a1bc51ad85d096df341f6d3a098f60d586f52`，MaxKB 为 `0fa9a0dae8850c1878f087f0d81c974c1d424b06`，访问日为 2026-10-15。

| 项目 | 本地与服务分工 | OCR、图意与复用边界 |
| --- | --- | --- |
| WeKnora | 默认引擎随类型及配置选择；PDF 默认 builtin Python docreader，逐页处理文字、扫描图及来源信息。另有进程内解析，以及区分自托管 endpoint 与云 API 的可选引擎 | 扫描 OCR 与图片说明在 Go 侧分别调用已配置视觉模型，须启用多模态并配置模型；该模型后端不必然是厂商 API。抽出 Python parser 不自动获得 Go 侧的完整任务、图片存储与来源绑定。依据：[引擎路由](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/infrastructure/docparser/engines.go#L45-L65)、[PDF 逐页处理](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/parser/pdf_parser.py#L1608-L1652)、[OCR 调用](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/image_multimodal.go#L539-L551) |
| MaxKB | 所读标准 PDF 导入链采用本地 pypdf、目录／文字规则及自身分段逻辑，未见这条标准链默认调用 OCR 或厂商全文解析 API | 产品另有需配置模型的图像理解工作流节点，不等于上传 PDF 自动生成图意。解析代码依赖 Django、自身 File 模型和 SplitModel；主仓 GPLv3，复制模块前还须核对依赖与许可证。此结论不外推到未读插件或其他工作流。依据：[标准 PDF 链](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L51-L99)、[图像节点](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/flow/step_node/image_understand_step_node/impl/base_image_understand_node.py#L135-L186)、[许可证](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/LICENSE#L1-L6) |

**旧 OCR 记录的边界。** 已找到 2026-10-09 的 Windows.Media.Ocr 教学实验，语言为 zh-Hans-CN，输入是英文小字号图片；并非 MinerU 测试。本轮用原图片副本复跑，识别文字与旧记录相同，但没有隔离语言、图像和引擎因素。用户随后要求停止排查，已停止；详见 [历史检查记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/historical-ocr-check.md)。该结果不构成 RAG_all 实现成绩、MinerU 质量结论或用户掌握证明。

当前文档解析供应方与云端方向已确认，不再询问 A／B／C 路线。具体 API 配置与 FR-7 达标情况属于后续接入验证，资料规模仍待核对。

## 7. Mary 与 TS 的数据／检索选型比较

用户要求 Mary 和 TS 子智能体对比 PostgreSQL＋pgvector、Milvus、MongoDB，判断 John 原建议是否合理。TS 对应 Mary 菜单中的技术选型比较，采用 technical／select 研究形态。研究请求本身未视为采纳；用户补充电脑 16 GB 并要求重新推荐后，已接受首版 PG＋pgvector、服务器同部署的方案。

完整证据、部署形态、比较矩阵与验证计划记录在 [数据与检索比较报告](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/research-storage-comparison.md)。本轮核验日为 2026-10-15，未进行安装或压测；32 道效果验收题不代表文档、切片或向量数据量。

- Mary 从半个月目标、同机部署、授权与版本生命周期、工程学习价值评估，认为 PG 同库方案适合优先验证；实际难点仍包括复杂手册解析与引用，以及撤权、恢复和重试。
- TS 核验后认为 PG＋pgvector 可统一业务元信息与向量，减少独立存储同步工作；中文关键词、ANN 过滤和本机内存都需要验证，不能以同库代替应用鉴权。
- Milvus Standalone 官方 RAM 要求 8 GB、建议 16 GB，超出服务器的 4 GB 约束；16 GB 电脑使独立部署 Milvus 成为可评估候选，但须核对实际可用内存、服务器到电脑的可达性、开机状态和跨存储恢复。Milvus Lite 是不同路线，不能一概按 Standalone 排除。
- MongoDB Community 的自管理 Search／Vector Search 已于 2026-06-30 GA，不能沿用只能 Atlas 或仍仅预览的结论；自管理需匹配支持版本、副本集和 mongot 进程，资源与同步窗口另验。Atlas 属于托管路线，改变现有同机部署目标。
- 推荐先用代表性资料验证 PG 路线，并保留稳定切片 ID 与检索接口；若实测过滤召回、延迟或资源不满足目标，或用户明确以专用向量引擎为学习目标，再比较替代路线，不提前实现三套数据库。

原文件按 Q4 受托选择保存在受控文件目录；数据库讨论主要针对业务元信息、文本切片与向量，不能把“通用不同领域资料”直接等同于必须使用 MongoDB。Q4 拟由 AI 准备四场景各 3 份、共 12 份公开／明确模拟资料作测试起点，实际文档／页／块与字节统计在实施时登记，不要求用户凭空报企业规模，不能据此承诺容量。解析已选 MinerU 云端 API，具体适配和效果后续验证。

重新推荐仍为首版服务器运行 PG＋pgvector：电脑 Milvus 会让问答依赖电脑联网和在线，增加任务重试与业务库／向量库同步工作；用户的主要顾虑是知识基础和面试回答，可通过真实项目讲解、验证和演练补足，不必因此引入跨机依赖。用户已答“可以”，据此确认首版选型；电脑 Milvus 保留后续可选对照实验，不纳入当前必须交付范围。原定 4 GB 服务器仍需实测资源，没有因选型确认而视为已达标。

## 8. 本轮 John—Mary 四题受托选择

用户授权 John 提出问题、Mary 先 TR 查两项目实际实现，再 TS 为本项目选择；每个大问题使用新 Mary，同题追问回原 Mary。四题均已闭环，真实问题、回答、追问及来源保存在 [技术选择与对话](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/technical-decisions-dialogue.md)。本节是受托实现选择，不冒称用户逐项亲选，不改既定产品角色与验收门槛。

| 大问题 | 选择重点 | 原始答复与追问 |
| --- | --- | --- |
| Q1 应用与可信访问 | 模块化单体、同步短 Session／迁移、显式 RAG、Cookie 会话与用户只读密钥、统一授权 | [Q1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/answer.md)、[追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/followup-answer.md) |
| Q2 文档生命周期 | 租约与代次隔离迟到、先存云任务标识、原始产物与来源、完整候选切换、删除墓碑；首次部分可用与替换完整性分开 | [Q2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/answer.md)、[追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q2/followup-answer.md) |
| Q3 证据链与四场景 | 结构块／embedding 版本、过滤后精确 B0、全请求最终 K=5、对比固定名次轮转、场景 schema／引用白名单与追问重检索 | [Q3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/answer.md)、[追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q3/followup-answer.md) |
| Q4 页面与交付 | 自建薄前端、电脑构建、四服务部署、受控文件／解包／密钥、一致备份、轻量观测与风险测试、可调初值 | [Q4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/answer.md)、[追问](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/followup-answer.md) |

当前不需要用户补充才能确定上述方案。具体 API 凭证、服务器接入及证书条件在实际使用前再处理；模型型号、依赖版本、MinerU 返回契约和硬限制在实施时核验。低进程／连接／并发、文件与时间数字只是可调初值；代码、API、权限、格式质量、备份恢复及 4 GB 表现都尚未运行。首次基线后登记绝对性能与成本门槛，保留失败、退步和未知值，不生成成绩或用户掌握记录。

PRD 定稿时又完成版本／部分可用术语、各格式定位、外部结果未知的有权操作、配额成功／失败／重试计次和备份恢复验收的受托澄清，已落入 PRD，不再列为未决产品问题。[Mary 澄清](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/finalization/clarifications.md)、[定稿记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/finalization/completion-report.md)保留来源与处理结果。

## 9. 两位 John IR 后的实施契约

本轮用户要求独立 John IR 与主 John 对抗审查，需要实现对齐的事项分三题交新 Mary TR→TS、原 Mary 追问。初评 CONCERNS／全实施交接 FAIL 的历史保留，修订后两位 John 均确认可按切片开始实施；七项规划问题关闭，见 [最终 IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md)。

本节新增政策以 [实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md)和 PRD 最新对应 FR／NFR 为准，旧 Q1–Q4 原答保留为演进记录，不把其未细化边界当当前任意选择空间。

- **M1：** 产品容量按保留原件字节＋在途预留，和派生磁盘分开；原子预留／终态账本，清完归还。诊断 request_id 与逻辑幂等 Key 分开；规范输入与执行快照、并发／崩溃／跨日、成功丢回包／真失败、重放再授权和过期语义均已记录，实际外部成本始终独立。[答复与依据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m1/answer.md)。
- **M2：** 逐库 profile／活动索引代，同配置普通增量发布，重建 guard 保旧读／拒新写／删除与失败条件解锁；同维重建与变维维护迁移分开。有限对比 schema、全格四态／零候选／真实结构失败、最小校核和各格式回看有明确契约；图意／来源／资源探路在主要业务完善前。[答复与依据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/answer.md)。
- **M3：** 旧备份后的安全变更不能自动恢复；默认隔离，旧身份／凭据待核验或作废，独立受托与台账 gap／完整现存资料范围核验，新随机恢复 epoch 及未知账／任务放行。普通重启不换 epoch，不引新服务或承诺 RPO=0。[答复与依据](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/answer.md)。

接口、状态、错误、关键不变量和 UI 动作在契约中，执行依赖与逐切片验收在 [S0–S7／P0 计划](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md)。未生成已经运行的故事状态；未实测结果仍按阶段取得，不扩大 PASS 范围。
