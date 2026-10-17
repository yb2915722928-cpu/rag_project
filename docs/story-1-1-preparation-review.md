# Story 1.1 源码准备独立静态预审

日期：2026-10-17，Asia/Shanghai。性质：准备代码静态预审；不是父 Story 完成门审查。父 Story 保持 `not_passed`。本报告没有运行通过结论。

首次报告状态：**冻结，F1–F7 均待原作者修复后另行复核**。主会话已确认收悉全部七项：F1–F4 交 B 作者，F5–F7 交 D 作者；本审查不因此把任何发现标为已解决，不等待作者交付，不读取其移动修订来替换原始证据。

| 严重程度 | 发现 | 原始版本结论 |
| --- | --- | --- |
| P1 | F1：状态测试混用两套索引键 | 静态可证失败路径 |
| P1 | F2：非法 job_state 样例提前失败 | 静态可证失败路径 |
| P1 | F5：Nginx 正则未引用花括号 | 静态配置解析缺陷，未运行语法检查 |
| P2 | F3：负例存在其他错误，掩盖回归 | 静态可证验证缺口 |
| P2 | F4：HTTP 校验接受非 JSON 成功响应 | 静态可证误判路径 |
| P2 | F6：权限预检接受不可用权限 | 静态可证准入缺口 |
| P2 | F7：hash 资源错误响应可带 immutable | 静态可证缓存策略缺口 |

## 被审版本与范围

- 比较基线：`a52ae3090948e7eeea6df87590f15ce35351d247`，只读 `git rev-parse HEAD` 返回同值。
- B/worker 原始冻结版本：Git index。用户通知 B 作者开始修订后，只以 `git show :<path>` 读取原始冻结内容；本报告 F1–F4 属于原始版本，不能套用到移动工作文件，也没有判定修订已解决。
- 初读工作文件用于定位；冻结 index 中的两个关键缺陷已再次直接读取确认。全部 B/worker index 工件的 blob ID、SHA-256 记录见后续附录，hash 不代表远端 commit 或运行验证。
- 首次范围包括公模枚举增量、两份专用测试增量、契约生成器/校验器/说明、manifest 与全部实际样例，以及 HTTP/标量/H/worker 真源和两份交付记录。HTTP、H 与原 worker 作为依赖参考，不冒充此次新增实现。
- 用户追加授权 D：当前冻结的部署工作文件和部署交付记录末尾“收敛增量”。D 使用工作文件 SHA-256 标识，与 B/worker index 版本分别登记。
- 未查询自身模型；派发参数及实际 turn_context 由主会话核验。本报告不自证实际模型或推理档位。

## 原始 B 冻结版本的具体发现

### F1 [P1] 新增状态分离测试混用 wire 字段名与类名索引，必然在首个断言失败

位置：[test_public_contracts.py](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:597)，范围：590–599；真源：[public.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/public.py:411)，范围：411–415。

触发条件：后续在规定 Linux 环境执行新增的 `test_c2_state_meanings_are_indexed_separately`。`wire` 的键是 `status/outcome/operation_state/job_state`，`PUBLIC_ENUMS` 的键则是 `Status/Outcome/OperationState/JobState/RetryMode`。两个集合没有相同元素，子集断言恒为假；即便删去断言，后续以 wire 键查索引仍会 `KeyError`。

影响：新增测试阻断 B0a 开发者测试门，且未验证声称的状态分离。此结论来自字面集合及查表关系，不是一次已执行的 pytest 结果。

建议交回 B 原作者：保持批准的类名索引接口，测试中显式映射 wire 字段到原枚举类或类名；随后在固定提交的 Linux 上执行该用例及枚举回归。不要为迁就错误测试把第二套 wire 索引混入真源。

### F2 [P1] 非法 job_state 样例会在合法 status 上失败，无法检查目标非法值

位置：[verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:193)，范围：193–203；样例：[job-state-invalid.json](/E:/aaa-project/rag/contracts/samples/c2/job-state-invalid.json:2)，范围：2–6；登记：[manifest.json](/E:/aaa-project/rag/contracts/samples/manifest.json:203)，范围：203–208。

触发条件：执行 `c2.reject.job-state-cross-enum`。该样例只有 `job_state="answered"` 非法，首个 `status="in_progress"` 合法。循环逐字段验证后，只要全局 `expect=="reject"` 就立即在合法字段处抛出 `AssertionError`，循环到不了 job_state。

影响：现有样例固定失败，校验器退出非零；这不是后端 JobState 拒绝规则有缺陷。把所有字段都改非法虽可能让循环完成，却会破坏单点跨枚举负例的证明。

建议交回 B 原作者：明确声明预期失败字段；合法字段必须通过，指定非法字段必须由正确后端枚举拒绝，并核对失败集合。补全“只有一个字段非法”的正负对照后在 Linux 执行。

### F3 [P2] 多个负例本身存在额外错误，目标规则失效时仍可能被误判通过

位置：[duplicate-key.json](/E:/aaa-project/rag/contracts/samples/c1/duplicate-key.json:2)，范围：2–4；[unknown-field.json](/E:/aaa-project/rag/contracts/samples/c1/unknown-field.json:11)，范围：11–17；[unknown-field.json](/E:/aaa-project/rag/contracts/samples/h/unknown-field.json:11)，范围：11–17；[verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:111)，范围：111–119。

触发与静态反例：

- 重复键样例仅提供版本和 request_id，缺少完成响应的多数必需字段。即使重复键校验被移除、普通解码保留最后一个版本，模型仍会因必需字段缺失抛出同类 `ValidationError`，样例仍被算作 PASS。
- 两份未知字段样例都令 `summary.fact_ids=["f1"]`，同时 `facts=[]`。即使未知字段被忽略，仍违反现有摘要引用及 answered 载荷规则。HTTP 负例也会继续返回预期 422，不能单独证明未知字段拒绝仍有效。
- C1 NaN/Infinity 样例还把特殊数值放在未知 `unknown_number` 字段，且保留上述无事实 answered 结构；孤立 surrogate 样例也保留该非法结构。异常类型相同不足以区分目标拒绝原因。

影响：可执行样例的防回归证明被削弱；不能把这些用例计数当成目标规则得到独立验证。现有 H 直接解析负例另有覆盖，因此不声称整个项目完全没有重复键或非有限数测试。

建议交回 B 原作者：从一个真正合法的完整对象派生每个单点负例，并提供移除目标违规后必须接受的对照；对于解析层规则优先直接检查对应解析入口和有限错误。未知字段同时覆盖顶层/嵌套，不能依靠无关业务错误得到预期失败。

### F4 [P2] HTTP 样例校验器允许非 JSON 200 响应通过，并未要求公共包和诊断 ID 存在

位置：[verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:238)，范围：238–261。

触发条件：合法 retrieval 样例收到状态 200、`Cache-Control: no-store`，但正文变成非 JSON 文本。`response.json()` 异常被转为 `payload=None`；随后只在 payload 是字典且 status 为 failed 时拒绝，因此此响应可被判为 PASS。移除 `X-Request-ID` 也会绕过目前仅“存在时检查格式”的分支；缺少 schema_version/request_id/status 同样没有必需字段检查。

影响：校验入口可在 C2 公共响应包已损坏时仍报告通过。失败侧只核对 code，也不核对有限 message/http_status/retry_mode 和响应体/头 ID 一致性。

建议交回 B 原作者：HTTP 响应必须为 JSON object，并由后端指定 Response 模型验证；比较允许替换 request_id 后的业务投影，要求服务器诊断头/体一致且不同尝试不复用，失败元数据与原有限策略一致。该建议不要求实现业务 GET operation。

边界：既有 [test_contract_http.py](/E:/aaa-project/rag/backend/tests/test_contract_http.py:109)，范围：109–147，已有更强的公共包/状态码/诊断 ID 断言；本发现只针对新样例校验入口，不能解释为整个 HTTP 测试套件缺少这些断言。上述既有测试本次未运行。

## 首次静态观察与未执行边界

- `PUBLIC_ENUMS` 直接索引原类，未发现另建 wire 枚举或修改原 DTO 索引的代码。生成器读取后端 schema/枚举并区分 validation/serialization；本次未发现可证的现有 schema 引用或 TS 生成失败，但未生成任何工件，不代表引用解析、TS 编译或可重建性已通过。
- worker 与基线净差异为零；新增 Linux 标记和 wakeup/清理测试的源码路径未发现可证缺陷。恢复 wakeup、恢复 handler、关闭各 FD 的清理彼此独立。mock 清理用例不能代替真实 Linux 信号、进程退出和 PG 无活动事务证据。
- C2 的 202 与失败 operation 投影在样例 manifest 中使用 DTO 校验，不执行对应 HTTP 状态检查；既有 HTTP 测试另行覆盖，仍需实际运行。样例名称和交付说明不得被解释为已执行 HTTP202/GET operation。
- C1 Unicode 和 null/缺省样例目前主要检查接受，不检查 DTO 序列化后的精确原值/字段存在性；稳定键测试检查的是一个通用对象。跨端 round-trip 与 TS 码点语义仍待后续验证。
- 只读源码及元数据；未启动 Python、未导入应用、未做 AST/编译、未生成 OpenAPI/schema/TS、未执行 `--check` 或样例、pytest、构建、HTTP、浏览器、容器、迁移或进程测试。
- 未访问 Netcatty、GitHub/Gitee、镜像源或 SFTP；没有认证重试、推送、服务器拉取或替代传输。
- 固定 Gitee commit、完整镜像、真实 PG18.6/pgvector0.8.7、Linux 精确 CPython3.12.8、有效锁同步、Uvicorn 实际进程、四服务生命周期、独立 Step 5 和父 Story 审查均未由本次证明。旧运行记录不重标到当前文件或提交。
- 发现全部保留待原作者处理；本次仅写本审查文档，不改实现、测试、交付记录、主控台账或 Git index。

## D 追加静态预审

以下针对用户追加授权的 D 冻结工作文件。合并严重程度顺序为：P1 的 F1/F2/F5，然后 P2 的 F3/F4/F6/F7；各段内保持原始发现编号，便于原作者处理。

### F5 [P1] Nginx 两处含花括号的正则未引用，会被配置词法解析为块边界

位置：[nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:27)，以及 [nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:82)。

触发条件：读取当前配置。map 的正则中含 `{8,}`，原件路径正则中含 `{1,64}`，整个参数都没有加引号。Nginx 配置词法将未引用的 `{` 用作配置块起始，正则量词因而不再是完整参数；这在进入实际请求匹配之前就会产生配置错误。

影响：即使未来取得正确镜像、证书与前端产物，gateway 仍无法正常加载该配置，阻断启动和健康门。这里给出的是静态配置语法判断；未执行 `nginx -t`，不编造具体错误文本或退出码。基线中另有类似的未引用 location 正则，本次新 map 和新原件路径仍须在当前交付中一并修正。

建议交回 D 原作者：将含量词的完整正则参数引用，检查配置内其余特殊字符；随后在精确镜像上执行语法检查和实际原件/公开资源路由测试。

### F6 [P2] preflight 权限判断接受不可用的 secret 和目录

位置：[preflight.py](/E:/aaa-project/rag/deploy/preflight.py:151)，范围：140–163；[preflight.py](/E:/aaa-project/rag/deploy/preflight.py:88)，范围：88–91。

触发与静态反例：

- `secret_mode_failures` 只禁止 group/other 位并检查属主，不要求 owner read，也不限定到交付声称的 0400/0600。正确属主、模式 0000 或 0200 的普通 secret 文件不会被此函数拒绝。在具备 stat/目录遍历权限的预检调用者下，其余条件满足时可得到 ready-for-build，但非 root 容器不能读取 TLS 私钥或 PostgreSQL 密码/pgpass。
- 目录使用 `not mode & 0o500`，只要 read/search 任一位存在就接受。正确属主且模式 0600 的 assets/locks/PG 根目录同时满足 owner write 和这个“read/traverse”检查，却没有 execute/search 位，容器无法遍历。模式 0300 则没有 read 位也能通过。

影响：预检的 ready 结论不能支持交付所承诺的权限准入，后续容器可能在启动或文件访问处失败。未实测容器权限，不把宿主 stat 当成运行通过证据。

建议交回 D 原作者：secret 明确要求 owner 可读并检查批准的精确 mode；目录分别检查所需完整位集，至少确保 search，需列目录时还须 read。针对 PG 的 0700 与其他目录的批准权限明确判定，添加只读元数据级的反例验证后再做目标容器验证。本审查不执行 chmod/chown 或创建实际秘密。

### F7 [P2] hash 资源的 immutable 缓存仅按 URI 决定，也覆盖错误响应

位置：[nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:25)，范围：25–28；[nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:43)，范围：43–46。

触发条件：修复 F5 后，请求形如 `/assets/app-abcdefgh.js` 的 hash 命名路径，但产生 403、405 等非 404 错误。map 只看 `$uri`，仍选择 `public, max-age=31536000, immutable`；location 又用 `add_header ... always`，错误响应仍携带该缓存声明。404 会走专用 named location 设置 no-store，因此本发现不把已处理的 404 算作反例。

影响：与“只有公开 hash 静态资源成功响应可缓存、gateway 错误 no-store”的约定冲突，可能长期缓存临时拒绝或方法错误。配置现在先受 F5 阻断，本项是修复语法后仍存在的独立策略缺陷。

建议交回 D 原作者：同时根据 URI 与最终响应状态判定缓存，只允许批准的成功静态响应 immutable，其他状态统一 no-store；在目标镜像验证 200、404、403/405 及代理自产错误。

### D 其余核对及边界

- Compose 仍为四服务；API/worker 共用构建定义和镜像标签，API bind 与 upstream/health 的 8000 端口一致。未发现本次新增端口漂移。
- 主 backend context 有 Dockerfile-specific ignore；gateway context 限在自身目录，前端与 worker health 通过独立 named context 复制。只核对了相对路径、文件存在性及 COPY 关系，未实际运行 BuildKit；没有宣称 named context 的过滤/权限行为已经验证。
- file secrets 去掉不可靠的 uid/gid/mode 声明，改为宿主权限约束；TLS/pgpass/PG 密码路径外置且 `create_host_path:false`。F6 是宿主预检的可证缺口，真实挂载后的 owner/mode/可读性仍为未执行门。
- gateway 维护前缀显式拒绝、JSON 与原件路由分别限 1MiB/20MiB、代理关闭缓冲与重试、固定 no-store 及清除验证头，均有可读取配置。Nginx large header buffers 的近似 16KiB 配置不能替代后端准确字节计数；不能据此认定所有协议头边界已实测。
- API health 是 liveness；worker 的 `/proc` 检查仅判断目标命令进程存在且非 Z/T/t，不证明数据库/业务 ready。gateway health 跳过 TLS 证书校验，不能证明链/主机名正确；所选镜像内 wget、mime.types 与 CMD/entrypoint 的实际兼容性未核实。
- PostgreSQL 数据布局、真实 UID/GID、PG/pgvector 精确版本、Linux 锁与原子操作、运行时资源约束、停止/重启均未实测。可读取的 Compose 值、非 root、tmpfs 和本地文件系统白名单不替代这些证据。
- 已读部署交付文档末尾本轮增量及历史说明；旧 JSON/旧传输包/中间修订 Compose 结构观测不转为此次冻结代码通过。未读取秘密文件内容，也未尝试镜像来源、Netcatty 或 Git 网络诊断。
- 版本证据差异：部署交付文档登记 preflight 的 SHA-256 为 `1c83590dbdb877827a934f58ebf33bd9b932de36964d72a8ab75c8940dc41418`，此次实际文件元数据读取为 `cedda5af4d598f5a4058aac9b92625d583f3a8c27fe3147e31225c1abce7a0e1`。不把二者合并，不把文档 hash 当成实际被审文件 hash，也不凭此差异推断变更作者或发生时刻。F6 定位上述实际读到的权限判断；后续必须用作者新冻结版本重新复核。

## 实际只读证据与命令

本节记录实际使用的命令类别及目标；同类批量读取合并列出，行号通过 PowerShell 文本编号取得。没有将待执行命令或作者执行记录当成本次命令。

| 实际命令/操作 | 目标或输出 |
| --- | --- |
| `Get-Content -Raw -LiteralPath` | 完整读取派发文档、RTK、AGENTS、工作集、B/枚举/worker/HTTP 短规格；阅读审查技能说明和 customize 配置，但未执行技能解析器或启动其工作流 |
| `rg --files`，带 `-g` 或 `--hidden` | 定位源码、contracts 全部实际文件、当前短规格及部署文件；文件列表不是执行证据 |
| `Get-Content`、`Select-Object -Skip/-First/-Last`、`ForEach-Object` 文本编号 | 读取生成器、校验器、全部 35 个实际样例 JSON、manifest、两份交付、真源与相关测试；读取原 epics 的四项 AC、共享契约 C1/C2、实施契约 §3.5；D 的 Compose/Dockerfile/ignore/health/preflight/env/offline/README 及交付末尾增量 |
| `rg -n` | 定位 C1/C2/H 约束及既有 HTTP 测试断言，没有运行测试 |
| `git status --short` | 识别既有 dirty/untracked 文件，不修改或回退其内容 |
| `git rev-parse HEAD` | 返回基线 `a52ae3090948e7eeea6df87590f15ce35351d247` |
| `git diff a52ae3090948e7eeea6df87590f15ce35351d247 -- <scope>` | 初次核对公模/测试/worker 与追加 D 的基线差异；worker 无净变化；未追读作者修订 |
| `git diff --cached --stat` 与 `git diff --cached a52ae3090948e7eeea6df87590f15ce35351d247 -- <scope>` | 确认 B/worker 原始暂存范围和测试增量 |
| `git show :<path>` | 用户通知 B 开始修订后，读取原 index 中测试、校验器、生成器、manifest 与负例；仅审原始固定快照 |
| `git ls-files --stage -- <scope>` | 记录原 index stage-0 blob ID |
| `Get-FileHash -Algorithm SHA256 -LiteralPath <path>` | 读取 D 冻结工作文件哈希，实际输出见附录；未运行部署或预检 |
| Git 标准输出原始字节 + .NET `SHA256.ComputeHash` | 对原 index 的 `git show :<path>` 原始字节计算 SHA-256，无临时源码落盘、无 Python、无应用导入 |

一次对不存在的报告文件执行 `Get-Item -ErrorAction SilentlyContinue` 返回未找到，整批命令退出 1；不是应用或测试失败。长输出曾被工具截断，关键源码已分段重读；未把被截断输出视为完整执行结果。

仅写本报告：用 `apply_patch` 生成正文，随后通过 .NET 文本写入追加哈希附录。未写临时 diff、脚本、工作集、其他文档或 index。

## 复核交接

首次结论为 3 项 P1、4 项 P2，均为静态发现。原作者修复、开发者测试、独立运行验证和修订静态复核均未由本报告完成。主会话后续通知最终冻结版本时，逐项比较 F1–F7、记录新 hash 与必要回归；原始证据不覆盖、不重标。没有自行创建新会话、派发任务或发送其他会话消息。

## 附录 A：B/worker 原始 index 字节指纹

SHA-256 针对 git show :<path> 返回的原始 blob 字节计算，不经过 PowerShell 文本换行转换；blob ID 来自 stage 0。它们标识暂存快照，不是整体 commit。

| 文件（index） | Git blob ID | SHA-256 |
| --- | --- | --- |
| [backend/pyproject.toml](/E:/aaa-project/rag/backend/pyproject.toml:1) | ea43e910140ceb5daa70d8d3280163f5ac388bea | 1b5a7ecb3e0036e3d96a8548a4fa729c95901fcd38dfa9ed63fb7b15e6c34c1c |
| [backend/src/rag_app/contracts/errors.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/errors.py:1) | 30b23add1b5032a331a08cc20c6b8851cd144ba1 | ad239632bb857f2d11dae6843784118e04d754fc4dfa045abe3370a533d6b97c |
| [backend/src/rag_app/contracts/public.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/public.py:1) | 0ec48db7d78a1923571e581a74c4445d75023480 | 2a90008315939dae54a191ae929f67f76edca8eadcdb34e3fab6461e33ed58cb |
| [backend/src/rag_app/contracts/scalars.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:1) | 7d8ae95fd429e70c16eec8e46e3666cf59a76e76 | 872c527ade3bab00a6141e359b5d820601537dc871b59083fe2a6dad02bffb62 |
| [backend/src/rag_app/entrypoints/api.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/api.py:1) | 45b1199ed736bb2b9adf327d5bf9fc249fa8051a | a98f78c228b61f272a46dcb4e16970a0afe726e99879a970ae6ac7277d47ada3 |
| [backend/src/rag_app/entrypoints/contract_probe.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/contract_probe.py:1) | 7c5d12719cb38c65c12a577baa100e40f333879b | 0a6b4bc23436fb276a82ff94f02f32b19755221ade614500e2e1a6b1f47e7f98 |
| [backend/src/rag_app/entrypoints/json_guard.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:1) | 2037016b4f62fff645f10e1878ecb134b68cb454 | 6e7964607cfd6407c3fef08c5f6140f810da8dd07ae23341062ac602b15d373b |
| [backend/src/rag_app/entrypoints/worker.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/worker.py:1) | 9f7dec06cc2bfd8554e71f11e20c18e07203ffbd | 8456aac284db4b01ccb2eadcf6850f95e967bd2666bd6d7992a65cf22f9c5c28 |
| [backend/tests/test_contract_http.py](/E:/aaa-project/rag/backend/tests/test_contract_http.py:1) | dc02e87995952a6735d6ddc83f105c81d552c0f7 | 555b184ceb8cadd6b73ad3bcac8f096241c59eb1c55c78091f0ed008c3010ec6 |
| [backend/tests/test_public_contracts.py](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:1) | 6cc0384ced0d2f57133f3027cba96da4ba91bd40 | cf42fb252c86e58bf52cebcbd332378c0dae80a5869ba2ab42a2d65c83e8b3dc |
| [backend/tests/test_runtime_entrypoints.py](/E:/aaa-project/rag/backend/tests/test_runtime_entrypoints.py:1) | dd05e6139481b9fae7af330364f0d308f9e99733 | c98906113e1fc581bb6920366bbe71228d9ce7f9d3efd20cbce1ec0fbd8e5864 |
| [contracts/generate.py](/E:/aaa-project/rag/contracts/generate.py:1) | 58f0122705e5db1d4632acf8141dc1ba2323eed3 | dd1fafc9008418ad09c5175d64029f1ff640e4092ab9d0894ab2219bad4e25e7 |
| [contracts/README.md](/E:/aaa-project/rag/contracts/README.md:1) | 4847203ed6b9e9bf7e98d55e46e8e76eee51b78f | 69395c44f83053971aa0e3e60943f89e26179c08f78aceada2de035ca9298e3d |
| [contracts/samples/c1/duplicate-key.json](/E:/aaa-project/rag/contracts/samples/c1/duplicate-key.json:1) | 88532afe64f8529ac66c103f12fee8450c554c96 | acb36864e5f9d24716c34f03d5a711bfe46f985562a1a860ce51d87d0b612fa1 |
| [contracts/samples/c1/failed-absent.json](/E:/aaa-project/rag/contracts/samples/c1/failed-absent.json:1) | eeef9dc5b02a2a293dedc839c5d7351f2a1e16da | aead50591c6842cee1fa86ff0633d4130013a69166454aa3a9930b5419e5e794 |
| [contracts/samples/c1/failed-explicit-null.json](/E:/aaa-project/rag/contracts/samples/c1/failed-explicit-null.json:1) | 1c22d3637fab5bd61225db1994642f3b67680040 | b156af33822cd5c45f92df854941bde304238c405db49e486dc31131f73ccc2e |
| [contracts/samples/c1/infinity.json](/E:/aaa-project/rag/contracts/samples/c1/infinity.json:1) | b9dd0424f2020e72dc9faa6b5adc8e4bdb7fc71c | e2d143ea85a6c70ee2798bdf34a2f6b9ef343f3a6d05b612006f4b6ac63c05ad |
| [contracts/samples/c1/lone-surrogate.json](/E:/aaa-project/rag/contracts/samples/c1/lone-surrogate.json:1) | 9e5359b378eba96a06b488bdab3f7d200cb636a6 | ae76b00760e2766331ae31d5d0f827231678f81923ba1355ca77628f228b7f99 |
| [contracts/samples/c1/nan.json](/E:/aaa-project/rag/contracts/samples/c1/nan.json:1) | 2fb7bde4da8850e78960431a75ccfda5aeb65293 | b737cd45e3b07e420c402eeca9ad12fb7e1386ad21f96f1eb4905e9f7b7706eb |
| [contracts/samples/c1/scalar-span.json](/E:/aaa-project/rag/contracts/samples/c1/scalar-span.json:1) | df4421af4acb14a05705fcb4f73fd37e0053a175 | b2b5f5f78038bb8392d318c5c151c1dd5d870a1a1c294a569ed6e3777a556155 |
| [contracts/samples/c1/stable-keys.json](/E:/aaa-project/rag/contracts/samples/c1/stable-keys.json:1) | ee937e71c664eb0908ce605111fea956e614871f | 9ce54c56fdf11db2d18b0c8d9778f3163b3c40ba87f4f2e2845a9ad6dd044b65 |
| [contracts/samples/c1/status-url-absolute.json](/E:/aaa-project/rag/contracts/samples/c1/status-url-absolute.json:1) | 5fbe964a61b000f42f375037589e20a96fb7773d | 08f7b30bddd2c918208b6fb5398fde0359b06706f761a992c545c02516a08d0f |
| [contracts/samples/c1/unicode-values.json](/E:/aaa-project/rag/contracts/samples/c1/unicode-values.json:1) | 48900cc3a55f4822930a9c7c8784556bf3ffdc29 | 0c8a51524a2e008a20cd4ad12a1b2a4888874046f7e471785ecddb049d65d94d |
| [contracts/samples/c1/unknown-field.json](/E:/aaa-project/rag/contracts/samples/c1/unknown-field.json:1) | 4a3dfe177f733b8d0b8e307b501c26cd6e6a240e | 8ac15b250ccb14fa9cba732e6cd7ad67858e5328e186bf2533a138ea450c3c26 |
| [contracts/samples/c2/accepted.json](/E:/aaa-project/rag/contracts/samples/c2/accepted.json:1) | c1613063c88fad03d0b9ee2d0d1dc4a51f30781d | 648d00e574fdbfcc0b4ac6359f398f8e92621226fcd0b7b9cb2da612b1eb6a4d |
| [contracts/samples/c2/completed.json](/E:/aaa-project/rag/contracts/samples/c2/completed.json:1) | 385b24b5369ae5e453150d76a1db37ad66e37a86 | 27499494c5599b8d1b68e834886c20dbf27620876c45cfe632496b90daf20cdc |
| [contracts/samples/c2/failed-authorized.json](/E:/aaa-project/rag/contracts/samples/c2/failed-authorized.json:1) | 8fd289decd394c40f8c7986d2ae74087eaab0507 | 0fe6e3872497cbe30ecd3bb34efccf16c59871160d6265d8c26b93604505f790 |
| [contracts/samples/c2/failed-pre-auth-with-id.json](/E:/aaa-project/rag/contracts/samples/c2/failed-pre-auth-with-id.json:1) | a02d5b20e61245c77ef9a7389d2491bcf6c768c8 | 72b50261df97644f5d9c24df1dec9129dfe42a24deaf47b87b769004a2c47537 |
| [contracts/samples/c2/failed-pre-auth.json](/E:/aaa-project/rag/contracts/samples/c2/failed-pre-auth.json:1) | 28a2f908be0771e84529d3323a362ce91b14ed6e | 7bcab8e4932a7185491d30c6192e80a36e774924e5058c3e9d483ea62836e2f8 |
| [contracts/samples/c2/forged-retry.json](/E:/aaa-project/rag/contracts/samples/c2/forged-retry.json:1) | 4a4ba3fda413fe8c7533c9ecf892adbc45bef146 | 33ac8e09102e17ce4be03f700669a9d25fe72168db2c5d89d0e9d4036d85fdaa |
| [contracts/samples/c2/job-state-invalid.json](/E:/aaa-project/rag/contracts/samples/c2/job-state-invalid.json:1) | 137a699f81a6a218ba8405926f80b1e85ec85397 | 31baa2b3a21a2fdd2fd2a24896df9cb0fa8240974b8cd72a8bc6731049c10e6e |
| [contracts/samples/c2/operation-failed.json](/E:/aaa-project/rag/contracts/samples/c2/operation-failed.json:1) | 6fa4fa85ddc9aec53a883ccf7215937194be1853 | 569a2a462b1b6d810481098ab6cbcfac16c5e4f8ed6e9903233dcdf8504fc24d |
| [contracts/samples/c2/outcome-mismatch.json](/E:/aaa-project/rag/contracts/samples/c2/outcome-mismatch.json:1) | 74d06d30ef83f9e1f5cb52b8458fbbd6f71af6b4 | 3af65f0c5b95f8675861a4308cac68c372e48519ea88d1f2318a48f871d33d18 |
| [contracts/samples/c2/retrieval-six.json](/E:/aaa-project/rag/contracts/samples/c2/retrieval-six.json:1) | a8c75fdc5a17f6ca71edb8126c5b2a4fdec57314 | 08a10b6afc678ca2577ad6f8b76ff0fd0dc649131c8ea6f205399685f6930548 |
| [contracts/samples/c2/retrieval.json](/E:/aaa-project/rag/contracts/samples/c2/retrieval.json:1) | d87f1838d86813bcc9012cf6d8e211d385321ed1 | e3e3670d71d8fa34c2bd3355ac3206383db4b8d6164897d805a82bedbc0b2e46 |
| [contracts/samples/c2/state-enums.json](/E:/aaa-project/rag/contracts/samples/c2/state-enums.json:1) | 09531ceb399706e75c3d5026157e272a24a8783f | 6e29f98c9cb95f81fcc8894318b00ab0e2527337d0fa4d3b91636c1e655638d7 |
| [contracts/samples/h/array-three.json](/E:/aaa-project/rag/contracts/samples/h/array-three.json:1) | 124dc7ea29247eba4bdfdffc909dc97562a44f34 | 8d349c562af62e82a07042946a210517bb141ddf85ee8093b43648bc266ceac7 |
| [contracts/samples/h/depth-exact.json](/E:/aaa-project/rag/contracts/samples/h/depth-exact.json:1) | 5879017dfa82b9516749143429eca4366b592faa | 3ed61ed47d165a6f1f0bc91e6451863189f2e7cc052a63581daa97fb090f7b2d |
| [contracts/samples/h/depth-over.json](/E:/aaa-project/rag/contracts/samples/h/depth-over.json:1) | a6b67192102219b3b73a5617f316591f1c66fcd2 | 588596f273352ab50b98822a7c4fa8281acc3e01e1766783b7a85038eba15a09 |
| [contracts/samples/h/duplicate-key.json](/E:/aaa-project/rag/contracts/samples/h/duplicate-key.json:1) | 514ca9509f749da850c9e278f408331b21ce0d72 | 080d1d9d77d8a027954c972677c4ce62c352b878aa44fa10777601fbb0def0ac |
| [contracts/samples/h/lone-surrogate.json](/E:/aaa-project/rag/contracts/samples/h/lone-surrogate.json:1) | cd12725a762b1486dcf92af6909b1a13e0d321cd | f6204181aef21b186fe1b240b341d53132203c579eb5a49ab8bf75239fc1b4b4 |
| [contracts/samples/h/nan.json](/E:/aaa-project/rag/contracts/samples/h/nan.json:1) | 371dcb08d5cebe743604aedf67a5f00708fd7472 | b9f2ee2f9d44d5e5857acddf5b66e92b64b75f2a6bc97c0ecc5aff597ef5b46d |
| [contracts/samples/h/nodes-exact.json](/E:/aaa-project/rag/contracts/samples/h/nodes-exact.json:1) | 25ddf2a4de4e3e570b25bf56de5df8c09de8e80f | 459e40da32ea60f7dbd66f40ed00fc97b53b237ed6306d14b8388c9b4e753bd2 |
| [contracts/samples/h/nodes-over.json](/E:/aaa-project/rag/contracts/samples/h/nodes-over.json:1) | 4d0f8bb7ade124eed75bf85fa5243de3767be532 | 415f7571ed5dc4a3ab538c18e246e593feb64e201526528ce9e3f2db8893f3b8 |
| [contracts/samples/h/number-overflow.json](/E:/aaa-project/rag/contracts/samples/h/number-overflow.json:1) | 4f4020b17b33836bd5a6b86f95290b1ace1cd802 | 41045e529ce6d23f8e90264588376aeb94ab152f5ed0122ea6617743b8fb0aea |
| [contracts/samples/h/root-array.json](/E:/aaa-project/rag/contracts/samples/h/root-array.json:1) | 7dd4387521924cdacfc5aa3714bc73771f0bce85 | 5239a7754876b9a70871c45e41f1bd9abbd91ed2de67af926c1cfcc9c9377d51 |
| [contracts/samples/h/unknown-field.json](/E:/aaa-project/rag/contracts/samples/h/unknown-field.json:1) | 7a3bd00a8ca6cd0656a909c62e7722757f6b6a16 | 145072755ff84f8f457cc7949c87610b799a8d55c14cab16ee4db1a819d4a372 |
| [contracts/samples/h/valid-min.json](/E:/aaa-project/rag/contracts/samples/h/valid-min.json:1) | 311847daa5a050a215b149561e1e00c818f5b03b | c5c24f7ca1c946fa4dfd44407409c8e11ec6e41f0e1c7c45bf8381b42afb31f1 |
| [contracts/samples/manifest.json](/E:/aaa-project/rag/contracts/samples/manifest.json:1) | 259b5abd14f664d89ecd9904553f261b21083cc2 | 5cb6585c15adb695994c0a2773b4e439fd9d6d6fb819d886ce388a58e9058c1d |
| [contracts/verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:1) | b3dfa3bd3893dd07c7a8891372c5c666549b7d13 | 107cf8c842779067442c9d737e857a6c712f8bc229d9e54ae03eeb2a12c7c88d |
| [docs/story-1-1-contract-http-delivery.md](/E:/aaa-project/rag/docs/story-1-1-contract-http-delivery.md:1) | 079c0057f26738bc4ae1f7b25149cbaa2b6b1bdc | 18711b2e7d06cbb73175f66b2c79452dff0825ae09644aad55cd62bb2b96bb58 |
| [docs/story-1-1-contracts-delivery.md](/E:/aaa-project/rag/docs/story-1-1-contracts-delivery.md:1) | 31cde535e2803fb2320ccaeb66aa20529cf1da35 | 08e0cb67a02cedba99289e18bfcaa0e835077e5a911a478e4b6ab1f4198be6d0 |
| [docs/story-1-1-worker-reconcile-delivery.md](/E:/aaa-project/rag/docs/story-1-1-worker-reconcile-delivery.md:1) | 2dabe345f3891d194463bfcd04a531603d309a6d | 5990411452d86e76a188767f8912dd84b86878dcdc144a97268ee1006372d1e7 |

## 附录 B：D 首次读取的工作文件指纹

以下逐项复制自审查期间已返回的 Get-FileHash 输出。主会话通知作者修复后没有重新读取 D 移动工作文件，也没有用新值替换本表。

| 文件（首次 D 工作文件） | SHA-256 |
| --- | --- |
| [deploy/.env.example](/E:/aaa-project/rag/deploy/.env.example:1) | feff1d95291a049c03d1940d018f4d1eadb005c5b7afa01f7f95722f4d54ce2c |
| [deploy/api.Dockerfile](/E:/aaa-project/rag/deploy/api.Dockerfile:1) | 38876b71ec93a603f04a2533e3254895acd39569d3c84deb0b38dd5058399348 |
| [deploy/api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1) | 4185b2288406dcf9c5c2e2651fe6ae0f4adff7ab88c3b60e13b7aa362f9ecc01 |
| [deploy/compose.yaml](/E:/aaa-project/rag/deploy/compose.yaml:1) | 2e438b05f9510b53c811256f2ac237d9e22f3f8096af462dbf30128c157d452e |
| [deploy/evidence/README.md](/E:/aaa-project/rag/deploy/evidence/README.md:1) | 93a90f7e71290ebea20c31ac6c69ff14bd346c68655a5ebae76c72b90541df12 |
| [deploy/gateway/.dockerignore](/E:/aaa-project/rag/deploy/gateway/.dockerignore:1) | 5229701e01dd1b3e4977aa480866c60ecea91fe8071cfccb87c0b4066f7593bc |
| [deploy/gateway/Dockerfile](/E:/aaa-project/rag/deploy/gateway/Dockerfile:1) | 984d4fa5924a8908f4ba356ff7bee847f594141f8252bcb3a4b988ec7a6a79b6 |
| [deploy/gateway/nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:1) | 9d2f0358eb7663f2b20da9f8df7c7632ab500168e2204862a1b2c1930efdc764 |
| [deploy/preflight.py](/E:/aaa-project/rag/deploy/preflight.py:1) | cedda5af4d598f5a4058aac9b92625d583f3a8c27fe3147e31225c1abce7a0e1 |
| [deploy/worker/.dockerignore](/E:/aaa-project/rag/deploy/worker/.dockerignore:1) | 7b2750f36a60aff1e210a1bfe7cce72aca6c9cb76867ff2137fd1a6bbf55d007 |
| [deploy/worker/healthcheck.py](/E:/aaa-project/rag/deploy/worker/healthcheck.py:1) | cb38351da6c9f8f50a144d4dd741de547c04ff0ffc363543ccc5d5a832f9240a |

元数据边界：部署交付文档末尾与 offline-images 作为说明材料阅读，但未在首次读取时取得文档自身 hash；此时作者已开始修订，不补填移动版本 hash。AGENTS/工作集/派发/原 AC 与短规格亦属需求参考，不是本轮冻结代码工件。报告保留读取范围及上述 preflight 登记差异，不声称材料均已具备原始字节指纹。

## 追加复核 R1：D 的 F5/F6/F7（2026-10-17）

本节仅追加于首次冻结报告之后；上方原始发现、原始哈希和未执行记录均保留。本次只复核用户指定的 D 冻结工作文件及对应 Git diff，不对 B 的 F1–F4 作修订结论。

### 被审修订与实际哈希

以下为本次实际 `Get-FileHash -Algorithm SHA256` 结果，三项均与用户指定值完全相同。源码检查采用工作文件，比较对象采用原 index；这些值不代表运行通过、远端 commit 或镜像 digest。

| 本次冻结文件 | 实际 SHA-256 |
| --- | --- |
| [nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:1) | `cd167d3f87a7263fd0903b151201dae653200c7f5bd8c446eca112a59181ab34` |
| [preflight.py](/E:/aaa-project/rag/deploy/preflight.py:1) | `cedda5af4d598f5a4058aac9b92625d583f3a8c27fe3147e31225c1abce7a0e1` |
| [D 交付文档](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:1) | `993c486100a8c711a9327d9729e3c5116aa366f3bf6c44e8bc084ec5d1c64b46` |

比较对象的 stage-0 blob ID：

| 原 index 文件 | Git blob ID |
| --- | --- |
| [nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:1) | `5fcb4ced206bbd3dad1948e5a339945b9d84c865` |
| [preflight.py](/E:/aaa-project/rag/deploy/preflight.py:1) | `e18c54c2f9ed126dc0fc532541e6717ddb6d34f6` |
| [D 交付文档](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:1) | `37437cf447b0a9f5872083222c2e69468ee1bca6` |

### 逐项复核结论

| 原发现 | 本次结论 | 当前源码证据与剩余边界 |
| --- | --- | --- |
| F5 / P1 | 原缺陷已静态消除；语法/启动未执行 | [nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:29) 的完整 map 正则已加引号；[原件 location](/E:/aaa-project/rag/deploy/gateway/nginx.conf:84) 的完整 `{1,64}` 正则也已引用。含量词的参数不再以未引用花括号出现。方法正则亦已引用。未运行 Nginx 配置解析，不能据此写成 `nginx -t` 或 gateway 启动通过。 |
| F6 / P2 | 原两处权限逻辑缺口已静态消除；权限运行验证未执行 | [目录权限](/E:/aaa-project/rag/deploy/preflight.py:88)，范围：88–91，明确要求可写目录的 owner write 位、所有目录的 owner read+execute 完整位集；0600/0300 目录分别缺 execute/read，均会进入失败分支。[secret 权限](/E:/aaa-project/rag/deploy/preflight.py:151)，范围：151–153，只接受普通权限位中的 0400/0600；原反例 0000/0200/0100 及存在 group/other 位的模式均不能满足条件。这里只按表达式分析反例，没有运行脚本、创建文件或改变权限。 |
| F7 / P2 | 原按 URI 给错误响应 immutable 的缺陷已静态消除；HTTP 行为未执行 | [缓存 map](/E:/aaa-project/rag/deploy/gateway/nginx.conf:27)，范围：27–30，输入改为 `status:uri`，仅 `200` 与 hash 资源路径共同匹配时返回 immutable，其他组合默认 no-store。[资产响应头](/E:/aaa-project/rag/deploy/gateway/nginx.conf:45)，范围：45–48，仍使用该映射；403/405/5xx 不再满足 `^200:`。404 仍有专用 no-store 错误 location。未发送 HTTP 请求，不宣称真实最终状态/头部已经验证。 |

本次在 F5/F6/F7 的修订范围内未发现新的可证阻断缺陷。该判断没有扩大到整套 D、Compose、镜像、真实 PG、部署权限或父 Story 完成门。

### F6 原始证据对应关系的追加更正

本次直接读取原 index 的 preflight，确认其中仍为原报告 F6 所描述的旧逻辑：目录使用 `not st_mode & 0o500`，secret 仅拒绝 group/other 位。对 `git show :deploy/preflight.py` 的原始字节计算 SHA-256，结果为：

`1c83590dbdb877827a934f58ebf33bd9b932de36964d72a8ab75c8940dc41418`

当前工作文件 `cedda5af...` 则包含已经修复的完整位集及 0400/0600 检查。因此，首次报告附录 B 的 `cedda5af...` 数值虽为当时实际采集值，却不能作为 F6 缺陷源码的指纹；首次正文中将 F6 定位于该数值的表述不准确。准确对应为：**F6 旧逻辑 = 原 index `1c83590d...`；F6 修复逻辑 = 当前工作文件 `cedda5af...`**。不能声称同一 `cedda5af...` 字节内容先存在、后消除了原缺陷。

这是首次审查中源码读取与稍后哈希采集未绑定到同一快照造成的证据对应错误。原报告不回写，本节明确更正，旧文档登记值也不再仅解释为无从确认的登记差异。当前交付文档已登记修复哈希，本次取得其自身哈希；该新文档不能反向补作首次文档哈希。

### 本次实际命令及未执行项

实际只读命令：三文件 `Get-FileHash -Algorithm SHA256 -LiteralPath`；指定三文件的 `git diff --`；`Get-Content` 和 PowerShell 文本编号/`Select-Object` 分段读取两份源码、交付末尾与原报告；`git show :deploy/preflight.py`；`git ls-files --stage --` 指定三文件；Git 原始标准输出配合 .NET SHA256 对旧 preflight blob 计算哈希。长输出被截断后，对 F6 相关行与原 index 对应行进行了分段重读。Git 提示后续可能转换 LF/CRLF，仅作为提示记录；本次没有执行转换、暂存或提交。

唯一写入是本报告末尾追加。追加前原报告完整文件 SHA-256 为 `d1972a8eac62aa7742a02bdc902f5622afb8de44cf5b14e3f05d351bdef201fa`；追加后以相同原字节长度验证前缀哈希保持该值，确认原始正文和哈希证据未被改写。

未执行任何应用导入、Python/AST/语法检查、Nginx 语法检查、preflight 运行、权限反例实验、HTTP、pytest、构建、Compose、容器、Netcatty、网络或认证探测。未修改部署实现、交付、测试、B 移动文件或 Git index。

复核状态只更新为 F5/F6/F7 的**静态修复已确认、运行验证仍 not-executed**；F1–F4 未复核，原发现及待修状态保留。D 和父 Story 正式验收仍未通过。

## 追加复核 R2：B 的 F1–F4（2026-10-17）

本节只追加本次冻结工作文件的独立静态复核，不改上方首次报告、R1 或原 index。F8/移动 ignore 不在范围内，未读取或判断。四份用户指定工件的实际哈希在初读与追加前均与指定值一致。

### 逐项判断

| 原发现 | 本次结论 | 当前源码依据 |
| --- | --- | --- |
| F1 / P1 | 原索引混用缺陷已静态消除 | [test_public_contracts.py](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:590)，范围：590–620，新增 wire 字段到类名的显式映射，先验证映射值属于 PUBLIC_ENUMS，再按类名取原枚举。原恒假子集断言及后续 wire 键查表均已移除；四个合法状态值与真源相容，RetryMode 另行验证，跨枚举负例保留。 |
| F2 / P1 | 原提前失败缺陷已静态消除 | [verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:223)，范围：223–272，遍历五字段并收集 ValidationError，最后检查实际失败集合。当前 [manifest](/E:/aaa-project/rag/contracts/samples/manifest.json:319)，范围：319–329，明确 `invalid_fields=[job_state]`；首个合法 status 不再导致 reject 用例提前失败。job_state 若被错误接受会失败，若额外合法字段被拒也会集合不匹配。 |
| F3 / P2 | 原样例无关错误掩盖拒绝原因的缺口已静态消除 | 原重复键负例已补齐完整完成对象并仅重复 outcome；NaN/Infinity 不再使用未知字段，改在 completed_at 单点变异；surrogate 仅替换 execution_snapshot_id；顶层/H 未知字段和新增嵌套未知字段负例均保留有效 facts/summary/catalog。各模型负例还通过 `error_contains` 限定拒绝原因，不能仅凭一个无关 ValidationError 计为通过。见下方 control 与样例核对。 |
| F4 / P2 | 原 HTTP 公共包误判路径已静态消除 | [verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:308)，范围：308–374，要求 JSON media type、可解析的 object、公共必需字段、指定后端模型验证、必需且合法的诊断头、头体相等、no-store、无 ETag/Last-Modified、拒 304；expected_error 通过 PublicError.from_code 对完整有限模型相等并检查 HTTP 状态。原非 JSON 200/无诊断头/缺公共字段的通过路径均已阻断，多次尝试会检查 ID 不复用。 |

F1–F4 的原缺陷均可在本次文本范围记为“静态修复已确认”；没有发现需要继续保留为未消除的原代码缺陷。该判断不是开发者测试、样例运行或整体 B 验收通过。

### F3 样例与 control 的实际核对

本次读取了全部变更样例（包括未暂存的新文件）、完整 manifest、校验器修订及其调用路径，并回读关键合法对照和后端真源。核对结果：

- [重复键](/E:/aaa-project/rag/contracts/samples/c1/duplicate-key.json:35) 现在与合法 completed 对照保持完整结构，只增加一个相同 outcome 键；普通“后值覆盖”不再因原缺字段得到无关失败。
- [NaN](/E:/aaa-project/rag/contracts/samples/c1/nan.json:8)、[Infinity](/E:/aaa-project/rag/contracts/samples/c1/infinity.json:8)、[surrogate](/E:/aaa-project/rag/contracts/samples/c1/lone-surrogate.json:9) 均由完整合法对象派生。由于所在字段也有时间/ID 类型约束，manifest 进一步要求 `invalid contract JSON`，可避免仅凭下游字段类型失败算目标解析拒绝通过；本次未执行该异常串断言。
- [顶层未知字段](/E:/aaa-project/rag/contracts/samples/c1/unknown-field.json:35)、[H 未知字段](/E:/aaa-project/rag/contracts/samples/h/unknown-field.json:35) 和 [嵌套未知字段](/E:/aaa-project/rag/contracts/samples/c1/nested-unknown-field.json:22) 的事实引用已有效，目标错误限定为 extra_forbidden；不再依靠 answered 缺事实顺带失败。HTTP 层仍保留哨兵泄漏检查，模型层诊断检查与 HTTP 保密投影分开。
- 新增 trailing slash、PublicError 合法对照、retrieval 失败带 operation ID 负例，以及 H 的 valid-a1/valid-a2/valid-a-x 对照文件均存在并已直接阅读；路径、模型名与相应 manifest 定义相容。
- [control 调用](/E:/aaa-project/rag/contracts/verify_samples.py:380)，范围：380–391，确实递归进入同一分发函数，强制 expect=accept，且 outcome 非 passed 会阻断父用例；不是只读取 control 声明。当前 34 条 reject 均具备 control。这里的“执行路径存在”不表示本审查或作者已经在指定环境实际执行 control。
- [manifest](/E:/aaa-project/rag/contracts/samples/manifest.json:1) 通过 PowerShell 作为静态 JSON 数据读取，确认 52 条顶层定义、34 条 reject、reject 无 control 数为 0、3 条 attempts=2；所有用例/request/control 的文件引用均存在。52 是定义数，不是测试通过数；control 是内部步骤，不另冒充 34 条独立通过结果。
- C1 的 Unicode 精确原值和显式 null/缺省新增了序列化输出字段断言，校验器在模型接受后读取 dump 检查；这些也只是待运行断言。跨端 TS/浏览器行为仍未验证。

### 非阻断说明与保留边界

当前 [B 交付记录](/E:/aaa-project/rag/docs/story-1-1-contracts-delivery.md:86) 称 attempts=2 有“两条”，实际 manifest 为三条：valid-retrieval、reject.unauthenticated、reject.unknown-field。建议原作者将文字更新为三条；这不改变 F4 当前代码路径已修复的结论，也不要求为该文字差异重跑应用。

交付中“reject 枚举用例必须声明 invalid_fields”的文字比通用函数约束更强：函数允许空 invalid_fields，但当前唯一 reject 枚举定义明确指定了 job_state，因此当前 F2 已闭环；本次不承诺未来任意新增 manifest 都会自动强制完整声明。

HTTP 成功样例现已验证 Response 模型，但没有逐字段比较全部返回业务值与请求夹具相等；本次只确认原 F4 的公共包/诊断/有限策略缺口消除，不扩大为任意业务响应内容正确性的证明。原 202/operation HTTP 投影、正式生成与可重建性等运行边界仍保留。

### 被审版本与只读证据

四个原 index blob 与首次记录一致：测试 `6cc0384ced0d2f57133f3027cba96da4ba91bd40`，校验器 `b3dfa3bd3893dd07c7a8891372c5c666549b7d13`，manifest `259b5abd14f664d89ecd9904553f261b21083cc2`，B delivery `31cde535e2803fb2320ccaeb66aa20529cf1da35`。工作文件与这些原始快照分开，未暂存、提交或改写 index。

实际命令：限定 B 路径的 Get-FileHash、git diff --stat/git diff --、git status --short、git ls-files --stage；Get-Content/Select-Object/文本编号读源码和全部变更样例；git show 只读后端公模参考；Select-String 统计顶层 ID；ConvertFrom-Json 只解析 manifest 元数据并以 Test-Path 核对引用，没有加载样例应用或执行断言。截断的头部 manifest 和关键代码随后分段重读。

以下哈希表覆盖四个指定工件、README 和全部当前实际样例 JSON，保证新增/变更样例与合法对照均有工作文件指纹。它们不是 commit 或运行证据。原始表完全保留。

| 本次工作文件 | SHA-256 |
| --- | --- |
| [backend/tests/test_public_contracts.py](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:1) | 9d6180d6e4eaeb4c565f74fccd4ec8868c9411006c29a506123f398f2f138177 |
| [contracts/README.md](/E:/aaa-project/rag/contracts/README.md:1) | d38f8164d68df330b5d76441671483712d30a47e2af096cf66060578586f6562 |
| [contracts/samples/c1/duplicate-key.json](/E:/aaa-project/rag/contracts/samples/c1/duplicate-key.json:1) | 57fe30f5df0c97c5afbb5e2187c5a3398fced9b8f3d904d7f586f9bd3d7046c7 |
| [contracts/samples/c1/failed-absent.json](/E:/aaa-project/rag/contracts/samples/c1/failed-absent.json:1) | aead50591c6842cee1fa86ff0633d4130013a69166454aa3a9930b5419e5e794 |
| [contracts/samples/c1/failed-explicit-null.json](/E:/aaa-project/rag/contracts/samples/c1/failed-explicit-null.json:1) | b156af33822cd5c45f92df854941bde304238c405db49e486dc31131f73ccc2e |
| [contracts/samples/c1/infinity.json](/E:/aaa-project/rag/contracts/samples/c1/infinity.json:1) | f100e1ec7acdad60e2c9450fd804268afa1f5d12d8207b3cfd887302654b2fc0 |
| [contracts/samples/c1/lone-surrogate.json](/E:/aaa-project/rag/contracts/samples/c1/lone-surrogate.json:1) | 7836d01999c5402c7861fd9b1fff2cc246cb816cfaa626e984cf080c13c08f52 |
| [contracts/samples/c1/nan.json](/E:/aaa-project/rag/contracts/samples/c1/nan.json:1) | ff117a92f7c8b4b87142d2483a9fb297de0c5aeb4666f7deaf165e3cf6a4a0b8 |
| [contracts/samples/c1/nested-unknown-field.json](/E:/aaa-project/rag/contracts/samples/c1/nested-unknown-field.json:1) | 9f73ce33f58764e9eadcb4859eabd39d71675b7202af4eb28179432cce2b2445 |
| [contracts/samples/c1/scalar-span.json](/E:/aaa-project/rag/contracts/samples/c1/scalar-span.json:1) | b2b5f5f78038bb8392d318c5c151c1dd5d870a1a1c294a569ed6e3777a556155 |
| [contracts/samples/c1/stable-keys.json](/E:/aaa-project/rag/contracts/samples/c1/stable-keys.json:1) | 9ce54c56fdf11db2d18b0c8d9778f3163b3c40ba87f4f2e2845a9ad6dd044b65 |
| [contracts/samples/c1/status-url-absolute.json](/E:/aaa-project/rag/contracts/samples/c1/status-url-absolute.json:1) | 50d9b50bbffdf1ef6cbdced45a26ecb6740d540691b24b9ce8317e4e69d2e933 |
| [contracts/samples/c1/status-url-trailing-slash.json](/E:/aaa-project/rag/contracts/samples/c1/status-url-trailing-slash.json:1) | 2732cf59ba82ee9faa9d7f399e4c29c21b004cbfcc60a94c98c710aff6ae98f4 |
| [contracts/samples/c1/unicode-values.json](/E:/aaa-project/rag/contracts/samples/c1/unicode-values.json:1) | 0c8a51524a2e008a20cd4ad12a1b2a4888874046f7e471785ecddb049d65d94d |
| [contracts/samples/c1/unknown-field.json](/E:/aaa-project/rag/contracts/samples/c1/unknown-field.json:1) | 9649e97a2ef4dc3e2c21b1c3ab6c315c760cb1a9acb3daea89834cd5afd7edb1 |
| [contracts/samples/c2/accepted.json](/E:/aaa-project/rag/contracts/samples/c2/accepted.json:1) | 648d00e574fdbfcc0b4ac6359f398f8e92621226fcd0b7b9cb2da612b1eb6a4d |
| [contracts/samples/c2/completed.json](/E:/aaa-project/rag/contracts/samples/c2/completed.json:1) | 27499494c5599b8d1b68e834886c20dbf27620876c45cfe632496b90daf20cdc |
| [contracts/samples/c2/failed-authorized.json](/E:/aaa-project/rag/contracts/samples/c2/failed-authorized.json:1) | 0fe6e3872497cbe30ecd3bb34efccf16c59871160d6265d8c26b93604505f790 |
| [contracts/samples/c2/failed-pre-auth-with-id.json](/E:/aaa-project/rag/contracts/samples/c2/failed-pre-auth-with-id.json:1) | 72b50261df97644f5d9c24df1dec9129dfe42a24deaf47b87b769004a2c47537 |
| [contracts/samples/c2/failed-pre-auth.json](/E:/aaa-project/rag/contracts/samples/c2/failed-pre-auth.json:1) | 7bcab8e4932a7185491d30c6192e80a36e774924e5058c3e9d483ea62836e2f8 |
| [contracts/samples/c2/forged-retry.json](/E:/aaa-project/rag/contracts/samples/c2/forged-retry.json:1) | 33ac8e09102e17ce4be03f700669a9d25fe72168db2c5d89d0e9d4036d85fdaa |
| [contracts/samples/c2/job-state-invalid.json](/E:/aaa-project/rag/contracts/samples/c2/job-state-invalid.json:1) | 31baa2b3a21a2fdd2fd2a24896df9cb0fa8240974b8cd72a8bc6731049c10e6e |
| [contracts/samples/c2/operation-failed.json](/E:/aaa-project/rag/contracts/samples/c2/operation-failed.json:1) | 569a2a462b1b6d810481098ab6cbcfac16c5e4f8ed6e9903233dcdf8504fc24d |
| [contracts/samples/c2/outcome-mismatch.json](/E:/aaa-project/rag/contracts/samples/c2/outcome-mismatch.json:1) | 3af65f0c5b95f8675861a4308cac68c372e48519ea88d1f2318a48f871d33d18 |
| [contracts/samples/c2/public-error.json](/E:/aaa-project/rag/contracts/samples/c2/public-error.json:1) | 9505c7436c8d926c704139647aeb6e2672ef81c50ed46b2ea109d427fe0e5e21 |
| [contracts/samples/c2/retrieval-failed-with-operation.json](/E:/aaa-project/rag/contracts/samples/c2/retrieval-failed-with-operation.json:1) | 72dad5b07a5e4968e2609535cc1f2c757372e0c0d0619aa3d083feb18ec61069 |
| [contracts/samples/c2/retrieval-six.json](/E:/aaa-project/rag/contracts/samples/c2/retrieval-six.json:1) | 08a10b6afc678ca2577ad6f8b76ff0fd0dc649131c8ea6f205399685f6930548 |
| [contracts/samples/c2/retrieval.json](/E:/aaa-project/rag/contracts/samples/c2/retrieval.json:1) | e3e3670d71d8fa34c2bd3355ac3206383db4b8d6164897d805a82bedbc0b2e46 |
| [contracts/samples/c2/state-enums.json](/E:/aaa-project/rag/contracts/samples/c2/state-enums.json:1) | 6e29f98c9cb95f81fcc8894318b00ab0e2527337d0fa4d3b91636c1e655638d7 |
| [contracts/samples/h/array-three.json](/E:/aaa-project/rag/contracts/samples/h/array-three.json:1) | 8d349c562af62e82a07042946a210517bb141ddf85ee8093b43648bc266ceac7 |
| [contracts/samples/h/depth-exact.json](/E:/aaa-project/rag/contracts/samples/h/depth-exact.json:1) | 3ed61ed47d165a6f1f0bc91e6451863189f2e7cc052a63581daa97fb090f7b2d |
| [contracts/samples/h/depth-over.json](/E:/aaa-project/rag/contracts/samples/h/depth-over.json:1) | 588596f273352ab50b98822a7c4fa8281acc3e01e1766783b7a85038eba15a09 |
| [contracts/samples/h/duplicate-key.json](/E:/aaa-project/rag/contracts/samples/h/duplicate-key.json:1) | 080d1d9d77d8a027954c972677c4ce62c352b878aa44fa10777601fbb0def0ac |
| [contracts/samples/h/lone-surrogate.json](/E:/aaa-project/rag/contracts/samples/h/lone-surrogate.json:1) | f6204181aef21b186fe1b240b341d53132203c579eb5a49ab8bf75239fc1b4b4 |
| [contracts/samples/h/nan.json](/E:/aaa-project/rag/contracts/samples/h/nan.json:1) | b9f2ee2f9d44d5e5857acddf5b66e92b64b75f2a6bc97c0ecc5aff597ef5b46d |
| [contracts/samples/h/nodes-exact.json](/E:/aaa-project/rag/contracts/samples/h/nodes-exact.json:1) | 459e40da32ea60f7dbd66f40ed00fc97b53b237ed6306d14b8388c9b4e753bd2 |
| [contracts/samples/h/nodes-over.json](/E:/aaa-project/rag/contracts/samples/h/nodes-over.json:1) | 415f7571ed5dc4a3ab538c18e246e593feb64e201526528ce9e3f2db8893f3b8 |
| [contracts/samples/h/number-overflow.json](/E:/aaa-project/rag/contracts/samples/h/number-overflow.json:1) | 41045e529ce6d23f8e90264588376aeb94ab152f5ed0122ea6617743b8fb0aea |
| [contracts/samples/h/root-array.json](/E:/aaa-project/rag/contracts/samples/h/root-array.json:1) | 5239a7754876b9a70871c45e41f1bd9abbd91ed2de67af926c1cfcc9c9377d51 |
| [contracts/samples/h/unknown-field.json](/E:/aaa-project/rag/contracts/samples/h/unknown-field.json:1) | 9649e97a2ef4dc3e2c21b1c3ab6c315c760cb1a9acb3daea89834cd5afd7edb1 |
| [contracts/samples/h/valid-a-x.json](/E:/aaa-project/rag/contracts/samples/h/valid-a-x.json:1) | b98916c2cdff9fb1f04d6d83ab835aff91191f9349f569c79d57c2774954bd53 |
| [contracts/samples/h/valid-a1.json](/E:/aaa-project/rag/contracts/samples/h/valid-a1.json:1) | ff57d51972c56df657d32f3901f226728943f67e0716df1de53a11ce240bd2ba |
| [contracts/samples/h/valid-a2.json](/E:/aaa-project/rag/contracts/samples/h/valid-a2.json:1) | d4f143869e9dedf3610951217569bc1a31d62ea1b317c73e7ddb59e2b060d162 |
| [contracts/samples/h/valid-min.json](/E:/aaa-project/rag/contracts/samples/h/valid-min.json:1) | c5c24f7ca1c946fa4dfd44407409c8e11ec6e41f0e1c7c45bf8381b42afb31f1 |
| [contracts/samples/manifest.json](/E:/aaa-project/rag/contracts/samples/manifest.json:1) | df659d241696d5262cd344c606bfe997b0286c1ab2b0d2af073340135712a834 |
| [contracts/verify_samples.py](/E:/aaa-project/rag/contracts/verify_samples.py:1) | e41e6407efb4ceb486e6533017328d4f24f4cdb9a8cb882d878532c432280e19 |
| [docs/story-1-1-contracts-delivery.md](/E:/aaa-project/rag/docs/story-1-1-contracts-delivery.md:1) | a874c4e05d5a527189706a3a2baf2680dd83455ce9a6214224a538c184117984 |

追加前报告完整 SHA-256 为 `7425ab960bcddacc716a93a1c35ad6b151691c2842105d1f519a63f9d4851ca1`；追加后验证原字节长度的前缀哈希不变。仅追加本审查文档，未修改实现/测试/交付或 index；未读取移动 ignore，对 F8 无结论。

未运行任何 Python、应用导入、语法/编译、样例/control、pytest、HTTP、生成器/--check、构建或部署命令，未做网络/Netcatty/认证探测。本次无执行通过数。F1–F7 各自的静态复核与正式运行门分开；B、D 和父 Story 仍不得依据静态修复放行。

## 追加 C1 依赖发现 C1-NZ：原生 Decimal 负零破坏金额线协议（2026-10-17）

### C1-NZ [P2] 原生 Decimal 负零被接受，但序列化结果不符合自身 schema，无法 round-trip

这是用户单独指定的依赖真源候选，不并入 F1–F4 的作者修复范围，也不撤销 R2 对原四项静态修复的结论。不占用 F8 编号；未读取移动 ignore。此项保持待协调修复，主会话可交给相应后端作者，本审查不认领或修改实现。

位置：[scalars.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:99)，范围：99–110；同文件 [FiniteDecimal](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:122)，范围：122–126；使用方 [Money](/E:/aaa-project/rag/backend/src/rag_app/contracts/public.py:94)，范围：94–106。

触发条件：服务端用原生 `Decimal('-0')` 或 `Decimal('-0.00')` 构造 `Money(amount=..., currency='CNY', source='bill')`（estimate 同样适用）。不是传入字符串 `'-0'`，也不是 source=unknown；字符串负号已被现有正则拒绝，unknown 搭配非 null 金额还会被 Money 校验拒绝。

源码推导如下，未执行任何示例：

1. Money 的 before wire 检查不会改写 Decimal；decimal_amount 明确接受原生 Decimal，而数字格式正则只应用于 str。`Decimal(value)` 没有显式去符号或零规范化。
2. Decimal 的带符号零是有限数，数值等于零，因此 `result < 0` 不成立；当前判断只排除非有限数和严格小于零的数，不排除负零。这里不存在“负零必然小于零”的逻辑依据。
3. 后续 FiniteDecimal 没有增加符号约束。其 JSON PlainSerializer 直接 `format(value, 'f')`，保留带符号零的负号及小数位，分别得到 `'-0'` 和 `'-0.00'`。Money 的跨字段检查只检查金额/币种的 null 关系，不会规范化金额。
4. WithJsonSchema 声明金额为 string、pattern 为 `^\d+(?:\.\d+)?$`，两个带负号输出均不匹配。JSON 模式 dump 返回包含这种 amount 字符串的对象；对应具体 API 是 `model_dump(mode='json')`，编码后的 JSON 则用 `model_dump_json()`。
5. 再调用 `Money.model_validate_json(...)` 时，JSON 中的 amount 已变为字符串；它在 decimal_amount 的 str 正则分支被拒绝。因此同一模型接受的服务端值可产生自身声明不允许、再读取时也不接受的 wire 值。无需假设金额累计发生了负数业务行为，单次合法构造入口即暴露该不一致。

影响：破坏 C1 金额序列化/schema 一致性与 round-trip；消费方按导出 schema 验证或重新读入金额时可能失败。JSON Schema 只是声明，不会自动修正 PlainSerializer 输出。本次没有声称项目当前已实际产生负零、某个生成工件已经运行失败，或发生计费/数据损失。

建议：由原作者在唯一真源明确选择“拒绝带符号零”或“按既定规则把零规范化为无负号金额”。如拒绝，应识别 zero+signed；如规范化，应明确是否保留原小数位，避免未授权地改变金额精度表示。选择后验证原生 Decimal('-0')/('-0.00')、正零、普通正金额、负数、非有限数，以及 JSON 输出匹配 schema 和重新输入的一致性；不要只修改 schema 放宽负号绕过现有非负 wire 约定。本次仅建议，没有改代码或添加/运行测试。

[现有金额测试](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:240)，范围：240–256，覆盖正数 Decimal round-trip、负数与非有限数拒绝，但该已读用例集合没有原生负零。该观察不声称全仓库已穷尽搜索，也不把未运行测试写为通过。

### 本次版本、实际命令与未执行边界

| 被读取文件 | 实际 SHA-256 |
| --- | --- |
| [scalars.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:1) | `872c527ade3bab00a6141e359b5d820601537dc871b59083fe2a6dad02bffb62` |
| [public.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/public.py:1) | `2a90008315939dae54a191ae929f67f76edca8eadcdb34e3fab6461e33ed58cb` |
| [test_public_contracts.py](/E:/aaa-project/rag/backend/tests/test_public_contracts.py:1)（仅金额相关段落作参考） | `9d6180d6e4eaeb4c565f74fccd4ec8868c9411006c29a506123f398f2f138177` |

实际只读命令：Get-FileHash；Get-Content 配合行号/Select-Object 读取上述相关段落及报告末尾；git diff -- 指定 scalars（无工作文件相对 index 差异）；git ls-files --stage 指定 scalars，stage-0 blob 为 `7d8ae95fd429e70c16eec8e46e3666cf59a76e76`；rg -n 仅在已指定测试文件中定位 Decimal/Money 相关代码。

结论类别：**源码推导成立，待修复；运行未执行**。没有运行 Decimal/format/正则实验、模型导入、dump/validate、schema 生成/验证或测试。未访问外部来源，未扩大为其他金额、依赖或业务模块审查。

本次只追加本报告。追加前完整报告 SHA-256 为 `642488f41c28de9123596bf957378a6a459ee3bb13ff302b22bc1f849ad87447`；追加后验证原字节前缀不变。原报告、R1/R2、原始哈希和 index 均未改写；没有关闭 B、C1 或父 Story 的正式验收门。

## 追加复核 R3：F8 与 C1-NZ 最终窄静态复核（2026-10-17）

本节追加于原报告、R1/R2 及 C1-NZ 原发现之后，全部旧文本、哈希和状态历史保留。仅审用户本次指定的冻结工件及直接相关差异；未重新放行 F1–F7、运行门或 Story 完成门。

### 结论

| 问题 | 本次静态判断 | 结论限度 |
| --- | --- | --- |
| F8：allowlist 重新纳入源码/迁移树下缓存、字节码和敏感工件 | 原问题在规则文本层已消除；本次修订未见可证的新阻断问题 | Docker/BuildKit context 的实际包含/排除结果仍未执行；不能写为真实上下文隔离或干净镜像通过 |
| C1-NZ：原生 Decimal 负零输出不符合 schema 且不能回读 | 原触发链已静态消除；新测试源码覆盖关键行为，未见可证的新确定性失败 | Decimal/Pydantic/pytest/JSON round-trip 和 schema 实际验证全部未执行 |
| R2 的 attempts 文档统计差异 | 当前文案已修正为三条并列出实际用例名称 | 仅关闭该文字差异，不改变三条 HTTP 用例均未运行的事实 |

### F8：规则顺序、构建消费与来源边界

F8 来自主会话集成核对，不是本独立预审首次发现；本次独立判断其最终修订。用户已确认接替作者 Russell 为指定 DeepSeek，交付文档也保留其派发 ID/turn_context 自述。本审查未另查模型或底层供应方，不将作者声明改写为审查者独立运行身份核验。

直接读取当前 [api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1) 全文并与原 index 比较：

- [allowlist](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:6)，范围：6–14，仍只恢复四份根配置和 src/migrations 两个子树，与 [Dockerfile COPY](/E:/aaa-project/rag/deploy/api.Dockerfile:15)，范围：15–24，对应；worker health 仍来自独立 named context，不依赖把其他仓库目录重新放入 backend context。
- [环境文件](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:19)，范围：19–29，在 allowlist 后排除 `.env`/`.env.*`/`.envrc`/`.direnv`。三种 dotenv 示例例外只恢复 src/migrations 子树内的指定示例文件，不像旧草案恢复 backend 根范围。
- [证书密钥](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:33)，范围：33–46，在恢复源码后再次排除已枚举证书/私钥/密钥库和 SSH 私钥名；没有保留 `.example.pem/.sample.key` 这类按文件名豁免密钥的草案规则。
- [凭据与目录](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:51)，范围：51–70，覆盖 pgpass/netrc、secrets/.secrets 目录及递归内容；凭据/service-account 规则限定于 JSON/YAML 载荷扩展，普通 credentials.py、secrets.py、service_account_client.py 不命中这些凭据扩展排除规则。未声称 glob 能识别任意命名或藏在普通源码中的秘密。
- [缓存字节码](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:76)，范围：76–81，位于全部恢复规则之后，明确排除 __pycache__ 本身及内容、pyc/pyo/pyd；因此原“先排除后被 !src/**/!migrations/** 恢复”的规则顺序缺口已修正。

以上为读取配置和按规则结构作静态判断，没有执行 Docker matcher、正则模拟、上下文打包或构建。作者交付里记载的 47 路径模拟属于作者的补充记录，本次没有重跑，也不把它提升为 BuildKit 通过。

[部署交付文档](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:154) 区分了首次 hash、错路由草案和最终值；[历史草案原文](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:201)，范围：201–248，仍以非生效文本保留，没有被本审查删除或改写。草案的 937 字节/历史 SHA 属作者记录，本次未重建原始草案字节或再算草案 hash；当前实际 ignore 的 hash 独立登记如下。

### C1-NZ：原触发链与修订测试

[decimal_amount](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:99)，范围：99–115，保留先前字符串正则和非有限/负值拒绝，随后仅对 zero+signed 执行 copy_abs。它去掉原生负零符号，保留 Decimal 指数，不引入 float、舍入或对普通正金额的规范化。因此原 `Decimal('-0')` 与 `Decimal('-0.00')` 不再以带符号零进入正常已验证模型。

[decimal_wire_text](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:118)，范围：118–126，在序列化路径再作负零去符号；[FiniteDecimal](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:138)，范围：138–142，已接入该函数，schema 的字符串类型与无负号 pattern 未变。原生负零在这条路径会得到 `0`/`0.00`，可进入原字符串校验规则，原缺陷的“已接受模型输出无效 wire”路径不再成立。这是静态推导，不是实际 dump 或 reload 结果。

修订只扩展了负零的明确处理，没有放宽 wire `'-0'`、真实负金额或非有限数的验证入口。serializer 面向已经验证的 Decimal；本次不把未经验证构造/手工绕过校验的任意值作为已批准输入域。

完整读取新增 [test_decimal_wire_zero.py](/E:/aaa-project/rag/backend/tests/test_decimal_wire_zero.py:1)，源码检查覆盖：

- [原生负零回读](/E:/aaa-project/rag/backend/tests/test_decimal_wire_zero.py:22)，范围：22–47：四种负零精度、model_dump(mode=json)、model_dump_json→model_validate_json、两种已知来源。
- [正零/正金额](/E:/aaa-project/rag/backend/tests/test_decimal_wire_zero.py:50)，范围：50–72：保留 0.100/1.20 等精度、无负号输出、TypeAdapter 再读取和 pattern 断言。
- [拒绝边界](/E:/aaa-project/rag/backend/tests/test_decimal_wire_zero.py:75)，范围：75–98：带负号 wire 零、真实负金额、非有限 Decimal、float/int/bool 等；其中 None 在 source=bill/currency=CNY 的已知金额组合下被 Money 跨字段规则拒绝，不是宣称 Money 所有场景都不允许 null。
- [unknown/schema](/E:/aaa-project/rag/backend/tests/test_decimal_wire_zero.py:101)，范围：101–115：unknown 保持 null，schema amount pattern/必需字段及普通正字符串表示不变。

未在这些新断言中发现可由源码直接确认的固定失败；没有收集 pytest 参数化用例数或执行断言。对照 [负零短规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-decimal-zero.md:1)，该修订选择“去负号且保留小数位”，没有通过扩大 schema 接受负号来掩盖问题。

[金额交付](/E:/aaa-project/rag/docs/story-1-1-decimal-zero-delivery.md:70) 明确保留未运行边界；[B 文档统计](/E:/aaa-project/rag/docs/story-1-1-contracts-delivery.md:86) 已由“两条”改为三条及其名称，与 R2 核对结果相同。依赖真源改变后，未来正式契约导出和相关回归仍须按固定提交重新执行，旧生成/测试证据不能重标为本次修订通过。

### 本次冻结 SHA-256

下表六份用户指定工件在读取时和追加前均与用户指定值一致；Dockerfile 为只读消费关系参考。没有用它们覆盖原表或旧发现的 hash。

| 本次工件 | 实际 SHA-256 |
| --- | --- |
| [backend/src/rag_app/contracts/scalars.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:1) | 20891e0360637ff38b289735d879ac805fdefc0d4f6eb99ba277783d77ed4fd6 |
| [backend/tests/test_decimal_wire_zero.py](/E:/aaa-project/rag/backend/tests/test_decimal_wire_zero.py:1) | fda17b643bb72a553943a2772ff9556d76fb8b4170d73f89d6d12fe1bfc32612 |
| [deploy/api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1) | f5d289eb6cd40dff4141937cc1dd7a794024a7bad5df79318d1b1f93ad9fa3ae |
| [docs/story-1-1-contracts-delivery.md](/E:/aaa-project/rag/docs/story-1-1-contracts-delivery.md:1) | 4f77889124e1b11a27e4ccb4032e89fa33a81cfd2f4094e0789e347ad8fe1b8f |
| [docs/story-1-1-decimal-zero-delivery.md](/E:/aaa-project/rag/docs/story-1-1-decimal-zero-delivery.md:1) | c5bc8e1e135ad2067b7e4da5714830f3463d4e72319d8e237add4fdded316189 |
| [docs/story-1-1-deploy-delivery.md](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:1) | bf28b8ce6b8f2c2810e3829835050e61a2358661d21a89982cf638c2649c8084 |
| [api.Dockerfile](/E:/aaa-project/rag/deploy/api.Dockerfile:1)（只读参考） | 38876b71ec93a603f04a2533e3254895acd39569d3c84deb0b38dd5058399348 |

### 实际命令、追加完整性及未执行项

实际只读命令：Get-FileHash；Get-Content/行号/Select-Object 读取 ignore、scalars、新测试、两份交付和 B 统计行、负零短规格、Dockerfile；限定路径的 git diff --/--numstat；rg --files 定位新交付与测试，并仅列出 src/migrations 下指定扩展名称；rg -n 在 D 交付定位 F8/来源/规则段；git ls-files --stage 与限定路径 git status --short。名称列表默认遵守 rg 忽略规则，不冒充完整 context 清单。未读取任何秘密文件内容。

原 index 仍包含未改写的旧 scalars blob `7d8ae95fd429e70c16eec8e46e3666cf59a76e76` 和旧 API ignore blob `01eef9739807546f2223e419f632145b11424e8a`；新增金额测试/交付仍未跟踪，不能据此认为已包含于任一提交。作者错路由历史与原始证据不回写。

追加前报告完整 SHA-256 为 `2c8132db903461e09771602eb8200d09902065065f4d556ee544c0eb94e9fd08`；追加后验证原字节长度前缀相同，原始正文、F1–F7 历史、R1/R2 和 C1-NZ 初次发现均保留。仅追加本报告，不改应用、测试、构建实现、交付或 index。

未执行任何 Python/应用导入、语法/编译、matcher 或模拟匹配、Decimal/format 实验、pytest、模型/样例/control、HTTP、生成器、--check、Docker/BuildKit/Compose、Netcatty、网络或认证探测。没有本次运行通过数、镜像内容证据或真实 Linux 权限证据。

最终窄静态结论：F8 与 C1-NZ 的原缺陷在上述文本版本中均已消除，本次修订未发现新的确定性问题；静态修复已确认，运行仍 not-executed。此前 F1–F7 的复核仅沿用其各自版本和边界；不宣称全工作区全面无缺陷，也不关闭正式运行、B/D 或父 Story 完成门。
