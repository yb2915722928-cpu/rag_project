# Q4｜证据、推导与实施边界

访问日期：2026-10-15。只使用本轮新取官方固定提交、官方指南，及明确标为本轮复读的 LICENSE 快照。需求交接用于限定方案，不证明外部事实。全部来源为官方单源，置信度 medium；“已核到”表示实际读到这些行，未做独立发布方交叉核验，未启动项目验证效果。

## TR：事实与来源

### W1–W3｜WeKnora（Tencent）

参照 SHA：a37a1bc51ad85d096df341f6d3a098f60d586f52；commit 日期未核取。

- **W1 前端与交付**：依赖声明含 Vue、TypeScript、Vite、Router、Pinia、TDesign；前端 Node builder 执行构建，将 dist 复制进 Nginx runtime。Nginx 有 SPA fallback、文件入口及 API 代理。来源：[package](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/frontend/package.json)、[构建](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/frontend/Dockerfile#L26-L68)、[代理](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/frontend/nginx.conf#L88-L126)，API代理范围204–208。
- **W2 文件与部署**：Compose 挂载本地数据文件卷并配置 local 存储，同时还有 Redis 等额外服务。原件下载 handler 先按其 Editor 规则取得有效上下文，再通过文件服务回传 private/no-store；预览则使用 Viewer。只借鉴“后端检查后取文件”，不复制其具体角色规则，也不从路由声明推定全系统授权可靠。来源：[Compose](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docker-compose.yml#L36-L49)，范围221–225、282–293；[下载](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/handler/knowledge.go#L2045-L2081)。
- **W3 运行记录**：logger 可配置级别／路径／格式，默认 stdout，可同时写文件；这不等于本项目所需业务审计和费用账已经具备。来源：[logger](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/logger/logger.go#L235-L278)。本轮复读的 [LICENSE 快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/imports/implementation-r1/WeKnora/LICENSE.md:1) 声明 MIT，另列第三方组件；来源[官方 LICENSE](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/LICENSE)。只报告文本，不作法律适用判断。

本轮[窄摘要](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/digests/weknora-r1.md:1)列有原文导入及失败取证边界。实际读取未解析锁文件，所以依赖范围不等于已安装版本。

### M1–M3｜MaxKB（1Panel-dev）

参照 SHA：0fa9a0dae8850c1878f087f0d81c974c1d424b06；日期未标。

- **M1 前端**：Vue、TypeScript、Vite 与 Element Plus，构建含类型检查；这里只证明配置声明。来源：[package](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/ui/package.json#L6)，范围6–15、34、57、73–89。
- **M2 文件访问**：Vite 开发代理把 OSS 文件／get_url 入口转发给后端。这是开发代理，不是已证明的生产 Nginx 规则或下载授权。本轮未核实后端存储介质与文件持久化实现：两个同名顶层 OSS 源文件仅占位，不能拿它们补全结论。来源：[Vite](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/ui/vite.config.ts#L63)，范围63–75、95–101。
- **M3 部署与记录**：Dockerfile 构建普通／chat 前端，声明数据卷，含版本、构建时间、提交标识；启动脚本创建权限700的日志目录。尚未核对实际日志写入、轮转、保留与完整启动调用链，不能声称已有审计或费用记录。来源：[Dockerfile](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/Dockerfile#L1)，范围1–7、27–42、54–57；[启动脚本](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/start-maxkb.sh#L3)，范围3–11、26。

本轮[MaxKB摘要与导入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/digests/maxkb-r1.md:1)保留源码行号。另本轮复读 [LICENSE 快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/imports/implementation-r1/MaxKB/LICENSE.md:1)，其文本为 GNU GPL Version 3；对应[固定提交 LICENSE](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/LICENSE)。不把“可作研究参照”解释为任意整项目复制许可。

### 官方部署／备份依据

| ref | 官方来源、发布者及本轮窄结论 |
|---|---|
| D1 | [Compose secrets](https://docs.docker.com/compose/how-tos/use-secrets/)，Docker Inc.：按服务授予并挂载文件，不自动证明宿主静态加密。 |
| D2 | [Compose services](https://docs.docker.com/reference/compose-file/services/)，Docker Inc.：可配置运行约束与健康依赖；deploy 支持是可选能力，要检查实际环境生效。 |
| N1 | [Nginx guide](https://nginx.org/en/docs/beginners_guide.html)，NGINX：静态目录与反向代理的直接依据。 |
| N2 | [HTTPS 配置](https://nginx.org/en/docs/http/configuring_https_servers.html)，NGINX：证书与私钥配置、限制私钥访问的依据；不是已经取得域名证书。 |
| P1 | [SQL dump](https://www.postgresql.org/docs/17/backup-dump.html)，PostgreSQL Global Development Group：数据库一致快照、单库 dump 不含全局角色；不是应用文件备份。 |

以上页面未标独立发布日期，访问日期均为2026-10-15，置信度均 medium，class=接口／机制。[提取记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/official-guides.md:1)保留支持范围。没有版本兼容、容量、售价或 SLO 的双源实证，不作相应声明。

## TS：本项目的具体取舍（受托设计，不是外部事实）

**选自建薄骨架。** 已确认 Vue，不再评框架分数。Element Plus 用在表单、表格、对话框；Router 负责页面与空间入口，Pinia 不充当权限库。服务器响应为准，路由隐藏只帮助界面。查询／对比保留输入、失败原因、引用和关联配置；重试由用户明确触发并作为新调用记账。私有结果不持久化进浏览器本地存储；切空间／退出清理缓存、取消旧请求，返回时核对当前空间。Markdown 禁止未经清洗的 HTML，图像／文件使用受控地址，不把模型输出当跳转目标。

**选静态发布和四服务。** 电脑锁定依赖／镜像标签或 digest，输出带提交和配置摘要的发布包。服务器加载预构建镜像及静态产物；gateway 不挂载原件卷，API 通过内网访问 DB，worker 和 API 使用各自凭据／池。数据库迁移作为单次发布步骤；迁移前备份，失败不开流量。保留上一发布包便于静态／应用回退，但数据回退须单独验证。上线时核查实际架构、磁盘、Docker／Compose 与扩展版本、有效限额；不为此现在安装或远程执行。选择 Nginx 终止 TLS，实际部署时决定可信证书取得及自动续期方法并验证续期；未有这些条件时只进行受限验收，不默认为已有公网生产 HTTPS。

**选受控本地文件。** 数据卷内按随机内部文档 ID／不可变版本区分原件、原始返回／ZIP、校验后产物、来源清单、候选临时文件。DB 映射真实归属、hash、状态、版本与对象关系，不信客户端文件路径。显示名与物理名分开；解析路径限制在根目录，拒绝穿越、符号链接逃逸、ZIP 绝对路径／穿越路径，初值最多2000个解包文件并限制总展开大小。上传、下载和解包流式处理；临时文件只在校验成功后提交。原始敏感材料不得进入静态目录、普通日志、错误响应。引用取当前有效来源并复核权限；删除先墓碑、清理可重试，沿用 Q2 的迟到结果禁复活。

**选停写一致备份。** 维护入口拒绝新业务请求，等待／明确终止在途，停所有应用写入者及清理工作，DB 保持运行导出；此时文件与DB不再变化。以同一个 snapshot_id 记录归档、文件哈希清单、必要角色授权、迁移版本、镜像／静态提交、非秘密配置、密文密钥及其 key_id。主密钥另用独立恢复口令加密封存，和数据备份分开保管，二者在清单中关联。保留用户控制介质中的离机加密副本，不自动上传外部存储、不创建自动化。恢复时先隔离外部调用及 worker，恢复匹配 PG／扩展、角色和数据、文件、密钥、配置；核验哈希／关联／授权，再恢复 lease 已过期任务，已有上游 ID 先查原任务。恢复演练覆盖未完成任务、删除墓碑、原件下载与服务密钥解密，不靠重新付费生成来补数据。备份频率／保留期在首次数据增长和可用磁盘基线后登记；首版上线前至少完成一次干净环境恢复。

**选两层密钥保存。** 用户程序 key 无需还原，只留 hash。供应方 key 需要还原调用，选择服务端 AEAD 加密（实施采用成熟库，随机 nonce、带 key_id 版本），主密钥与DB分离，只有API／worker按需读取；gateway无访问权。Compose secret 只是分发方式，宿主原文件仍需最小权限、不进Git／镜像／日志。UI只显示已配置与尾部脱敏标识，更新要重新输入，记录操作人／时间不记录明文。轮换要兼顾旧密文重加密和旧备份恢复；若主密钥丢失，DB密文不能凭空还原。

**选轻量记录而非大监控栈。** 运行日志只记必要 ID、阶段、时间、错误码、资源摘要；禁止 Authorization／Cookie／供应方key，错误体和URL查询串也需过滤。PG审计关联操作者、空间、动作、对象、允许／拒绝与请求ID；业务变更的成功审计尽量随同事务提交，失败审计与诊断按独立受限路径记录，落盘失败须可见。用量每个供应方 attempt 单独保存上游请求ID、是否发出／已知成功失败／结果未知、实际 usage／unknown、计价版本和估价。失败、取消、用户重试均不从账中消失；unknown 不填0，估价不称账单，外部账单另对账。不默认保存私有问题全文；确需复现实验的输入输出放受控证据集并标用途、来源及版本。

**初值的解释。** 主答六行是保护进程／文件／队列的测试起点，不是数据容量或响应时间目标。内存上限总计3200MiB，为系统留余量，但容器仍可能OOM，尤其解包和响应处理；要在有效配置与运行统计中核实，不能据加法保证4GB够用。PG初配 shared_buffers 256MiB、work_mem 4MiB 只在实施基线登记，单语句超时与外部HTTP超时分开；首轮发现检索超限就保留失败证据，不偷偷放大。上传网关请求体上限要略大于5份文件总和及multipart开销，并由API重新逐文件限额。超过文件初值明确拒绝，不能截断成“成功”；页数／块数、供应方上传／页数／速率／并发硬限制，实际接入时读取官方接口及账号限制自动核对后登记。本地队列／配额不得大于已确认上游硬限额。数据库时间存UTC，展示和每日配额日界线统一Asia/Shanghai，用户实际重试消耗新的调用记录；无上游返回不能编造usage／费用。测试真实供应方调用先串行、不开自动付费重试，再评是否扩大问答并发。

**测试起点与验收。** 12份只是AI可准备的公开／模拟最小包，不冒充用户真实企业规模：每场景3份，覆盖多格式、表格、扫描页、图意、版本替换、条件／对象对比；实际页数、字符、块数、上传／展开字节、来源及预期证据由实施生成清单。开发题与32冻结题分离。pytest按业务规则与边界测试，真实PG覆盖短事务／锁／租约条件／并发撤权／迁移；Playwright覆盖登录、导入、任务、问答对比、引用及失败页面。故障集覆盖超时未知、进程重启、磁盘满、损坏归档／缺文件、密钥缺失及恢复；权限安全套件独立，不因质量分通过而豁免。负载起步1路／2路问答并叠加1文档任务，固定数据、版本和配置，记录每次耗时、峰值RSS、DB连接、队列长度、失败、磁盘和真实用量。首基线后登记绝对时间／资源／费用门槛；样本少报告逐项和范围，不捏P95。当前均为待执行计划。

## 不确定与收敛

- 实际4GB承载能力、文档大小分布、解析产物膨胀、模型延迟／usage／费用、真实账号限额、服务器磁盘与证书条件均未知；具体基线测量或接入核对即可解决，不让用户凭空报数。
- MaxKB存储后端和完整日志链路未证，不作为采纳依据；整套复制的成本及第三方许可逐文件核对留到真正复用时。
- 本轮没有性能／价格数字结论，没有独立外部验证；不再追加搜集、评分矩阵或评审轮次。两项目核心事实与官方直接机制已经够支持选择。
- user_only_missing：无；实际部署时才需用户账号／访问权限及证书条件。
