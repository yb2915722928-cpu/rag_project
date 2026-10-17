# Story 1.1 H 有界 JSON 独立审查记录

日期：2026-10-17（Asia/Shanghai）。

## 结论与处置

对冻结解析器**未发现可证缺陷**。发现一项待补的 P2 取消路径验证缺口；审查过程中发现的一项 P3 证据哈希抄录错误，已在落盘后的最终只读复核中确认由记录所有者更正，详见下文。已有通过结果保持有效，但不能据此将取消路径标为已运行通过。本审查不关闭 H 独立验证中尚缺的证据，也不关闭父 Story、HTTP、contracts、真实 PostgreSQL、锁定重建和四服务完成门。

本实例未参与该改动的分析或实现，直接读取需求、完整实现、完整开发者测试及原始运行证据。仅新增本审查记录；未修改实现、测试、验证者报告或公共状态，也未重新派发任务。派发要求为 `group/auto-gpt-6-1-sol / medium`；实际模型、推理档位及底层供应方核验由父会话按可读取的 turn_context 记录，本报告不以角色提示词代替运行身份证据。

## 问题

### R1 · P2 · 取消路径没有对应运行断言，断流测试不能证明任务取消行为

类型：验证缺口，不是已复现的解析器错误。

- 位置：[流式适配器](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:358)，范围：358–370；[开发者断流测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:355)，范围：355–368；[独立验证记录](/E:/aaa-project/rag/docs/story-1-1-json-guard-independent-validation.md:84)，范围：84–86。
- 触发类别：读取协程在等待下一块数据时被调用方取消，或流迭代器传播 `asyncio.CancelledError`。
- 实际：开发者测试注入 `RuntimeError`；独立探针注入 `RuntimeError` 和 `ConnectionResetError`。这些都走普通异常投影路径。独立记录却将该段命名为“流式与取消”。完整读取开发者测试、远程三份被收集的探针及其公共辅助文件后，未见 task.cancel()、CancelledError 或取消传播断言。本地后端源码和测试的对应检索也未发现此类测试。
- 预期：按照[独立验证派发](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-json-guard-independent-dispatch.md:1)补足取消验证，分别记录取消与普通断流。静态看当前 `except Exception` 没有主动吞取消的处理，但这不能充当运行证明。
- 影响：如果以后把处理改为捕获 BaseException 并投影为 REQUEST_STREAM_ERROR，现有这些测试仍可通过，取消却可能被改成普通业务失败。当前 250 项通过结果不能发现该回归。
- 安全最小复现/补测建议：仅在获授权的 Linux CPython 3.12.8 独立验证目录，用测试流先产生部分合法 body，然后设置一个就绪事件并等待另一个事件；测试等待就绪后取消 read_bounded_json 对应任务，断言等待任务时传播 CancelledError、任务为 cancelled、后续读取计数未增加。另可用直接抛 CancelledError 的流检查异常分支。不得把取消改成普通 Exception 来迎合现有断流测试。
- 修复归属：主会话交独立验证者补运行证据并修正文案；若补测暴露实现错误，再交原作者修复并复核。审查者没有改动任何测试或其期望。

检查过的远程探针为 [probe_encoding.py](/opt/rag-story-1-1/json-guard-validation/probe_encoding.py:1)、[probe_headers.py](/opt/rag-story-1-1/json-guard-validation/probe_headers.py:1)、[probe_limits.py](/opt/rag-story-1-1/json-guard-validation/probe_limits.py:1) 和 [probe_core.py](/opt/rag-story-1-1/json-guard-validation/probe_core.py:1)。这些链接指向 Netcatty 主机文件，不是本机路径。

### R2 · P3 · 独立验证记录中的测试哈希曾抄录错误（最终复核已更正）

类型：证据记录错误，不是实现工件不一致。

- 位置：[独立验证记录](/E:/aaa-project/rag/docs/story-1-1-json-guard-independent-validation.md:12)。
- 触发类别：主会话或后续审查者按报告表格精确核验测试工件。
- 首次实际：表格将测试哈希写成 `087e02881bfef96704669cbf076893893e33853c7f0dc87f0deaa4ba964423244d9`，多出一个 `893`，不是 64 位 SHA-256。紧随其后的“三处 hash 一致”文字没有体现这处抄录错误。
- 预期：应为 `087e02881bfef96704669cbf076893e33853c7f0dc87f0deaa4ba964423244d9`。本次本地 Get-FileHash、冻结派发、开发者归档及独立验证原始 [source-sha256.txt](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard-validation/source-sha256.txt:1) 都是这个值。
- 安全最小复现：对首次读取到的表格字符串与上述原始证据作比较，可直接观察多出的 `893`。此处无需执行应用或重新跑套件。
- 影响与建议：精确核验会将正确工件误判为不匹配。由验证记录所有者更正表格并保留原始证据；无需为此修改实现、重写工件或伪造历史提交。
- 最终复核：该表格已改成正确的 64 位哈希，与原始证据及本地冻结测试一致。本项记为已更正，不再作为待修复问题；本审查者没有编辑验证记录。

## 范围、基线与方法

完整读取了[本次审查派发](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-json-guard-review-dispatch.md:1)、[H 短规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-json-guard.md:1)、[实施契约 3.5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:188)、[项目规则](/E:/aaa-project/rag/AGENTS.md:1)、[实现](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:1)、[测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:1)、[开发者交付](/E:/aaa-project/rag/docs/story-1-1-json-guard-delivery.md:1)及随后出现的[独立验证记录](/E:/aaa-project/rag/docs/story-1-1-json-guard-independent-validation.md:1)。

采用 bmad-review 的边界路径与验证缺口方法，输出范围、严重度及唯一写入位置按用户派发执行。本次不启动开发工作流，也不在本机运行 Python 或技能解析脚本。已直接读取技能默认配置，未找到该技能的项目/个人覆盖文件。

本地两次计算冻结文件的 SHA-256，与开发者和独立验证的原始哈希文本一致：

| 工件 | SHA-256 |
| --- | --- |
| [解析器](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:1) | `6e7964607cfd6407c3fef08c5f6140f810da8dd07ae23341062ac602b15d373b` |
| [开发者测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:1) | `087e02881bfef96704669cbf076893e33853c7f0dc87f0deaa4ba964423244d9` |

按上述工件快照审查，未给它们补造历史 commit。本轮没有修改 Git 状态。

## 实现核对结果

| 检查面 | 代码及测试依据 | 审查判断 |
| --- | --- | --- |
| 有界增量读取 | [feed/decode](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:93)、[流式入口](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:349)、[提前停止测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:325) | 先计实际字节，再以最多 1024 输入字节解码；不累积完整 body、不调用通用 JSON 加载器。超限不继续读取。 |
| 根、深度、节点与容器项 | [值节点入口](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:132)、[容器状态](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:275)、[边界测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:100) | 根 object 深度 1，每个子值加一；容器和标量各一节点，键不计节点。空容器、等值与超一处理符合已声明定义。 |
| 字符串、UTF-8、转义与重复键 | [标量预算](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:122)、[词法状态机](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:189)、[字符串测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:133) | 键和值均计解码后的字符串预算；代理对合成一个标量，孤立代理拒绝；按解码后的键判重，保留空白与规范化形式。跨 chunk 解码状态保留。 |
| 数字、语法与结束条件 | [数字转换](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:173)、[数字词法限界](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:260)、[finish](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:114)、[数字测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:188) | 默认数字词元最多 256 字符；先词法验证再转换，拒浮点溢出和转换失败。未闭合容器/词元、尾随非空白和额外根均拒绝。 |
| 请求头与长度 | [头处理](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:312)、[HTTP 头测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:235) | 原始重复字段均计费；重复控制头拒绝；Content-Length 先以十进制串比较，实际流量仍独立计数，完成时检查声明一致性。 |
| 有限错误与泄漏 | [错误对象](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:34)、[异常投影](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:361)、[泄漏测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:355) | 固定公开 code/message；在异常处理块外新抛有限错误，不附原文/原始异常字段。没有日志调用。traceback 局部变量不属于安全序列化接口。 |
| 二进制隔离 | [模块约定](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:1)、[显式调用约定](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:349)、[隔离测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:372) | guard 本身不注册中间件。测试证明未调用适配器的处理器不受限制；不将该测试扩大解释为已通过真实二进制 HTTP 路由验证。 |

内存判断是静态有界性检查，不是实测峰值承诺：字符串 token、总字符串、节点、栈深、数字词元及解码临时量都有有限预算，但 Python 对象和字符串列表的开销会超过原始 JSON 字节数。ASGI 已分配的单个大 chunk 也不受 guard 的事前分配控制，不能将 1MiB body 预算当成进程 RSS 上限。

解码后不同的键，例如 `"a"` 与 `"a\u0000"`，按当前需求不是重复键；不能凭此认定解析器缺陷。是否收紧某业务对象的键集合应由公共模型/业务契约决定，不能在 guard 偷做裁剪或规范化。独立探针中以“原始 NUL”构造的重复键负例本身也是非法 JSON，它只能证明输入被拒；已有合法转义同键与非 BMP 同键测试承担真实判重验证。

## 运行证据与实际限度

本审查仅通过 Netcatty get_environment 确认现有 Linux 连接，并使用 SFTP 只读读取证据及探针。未抢占终端、运行应用/测试、安装依赖或修改远程活动目录。

直接读取的开发者原始证据为 [pytest 输出](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard/json-guard-pytest.txt:1)、[JUnit](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard/json-guard-junit.xml:1)、[运行版本](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard/runtime.txt:1)、[测试工具环境](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard/test-environment.txt:1)和[哈希](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard/json-guard-sha256.txt:1)。它们记载 Linux、CPython 3.12.8、pytest 8.4.2，165 passed in 3.69s；JUnit 为 tests=165、failures=0、errors=0、skipped=0。

直接读取的独立验证原始[运行输出](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard-validation/combined-output.txt:1)、[摘要](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard-validation/versions.txt:1)及[哈希](/fileOfRag/testOfRAG/metadata/story-1-1/json-guard-validation/source-sha256.txt:1)记载：CPython 3.12.8，165 项重跑 3.97s、85 项探针 1.57s，两次退出码均为 0，摘要分别记载 failures/errors/skipped 均为 0。本审查读取了探针实际断言，未只按报告标题判断覆盖。验证者报告后来增加的“250 项同一次合并运行”未在本审查已经读取的原始输出中出现，本报告只确认上述两次独立运行的合计，不为该额外运行背书。

独立验证归档的原始哈希正确，R2 仅针对本地报告曾有的抄录错误，最终复核已确认更正。既有通过结果不包含 R1 所要求的取消证明。审查者没有独立重跑套件，不将证据读取或静态检查写成亲自运行通过。

HTTP 接入由另一个文件承担。只为辨认消费边界，读取了[当前调用点](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/contract_probe.py:92)，范围：92–113；可见先调用 guard、捕获有限错误、随后进行公共模型验证。本次没有审查该文件的完整实现或宣布其 HTTP 集成通过，也不把冻结解析器的结论扩展到该并行交付。

后续 HTTP 验收应保留：只在 JSON 入口显式调用；未知字段/版本及 ID 约束由公共模型执行；所有 guard 错误映射到有限公共错误包；真实 ASGI/服务器头预算、请求取消、超时/停滞流和连接终止另留运行证据。头预算公式仅覆盖 ASGI 字段的 HTTP/1 风格序列化，不覆盖请求行、HTTP/2 帧或服务器预先分配。没有证据证明现有超时配置生效，本报告不作该保证。

本次没有探测 Docker/Git/PG 外部阻塞，没有更改验收分母。后续由主会话将 R1 交给相应所有者处理，再读取修正和运行证据做独立复核；R2 保留发现与已更正的审计记录。
