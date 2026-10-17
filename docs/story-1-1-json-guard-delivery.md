# Story 1.1 B0b H 有界 JSON 交付说明

日期：2026-10-17（Asia/Shanghai）。
范围：仅限 JSON guard 实现交接；父 Story 未标记为完成。

## 依据与文件归属

实现前已完整读取[规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-json-guard.md:1)
及其 frontmatter 列出的两份上下文：
[AGENTS.md](/E:/aaa-project/rag/AGENTS.md:1) 和
[实施契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:1)。
本任务承接已派发的 Step 3 实现交接，未重新启动规格工作流。

本地 rollout 的实际 turn context 记录：模型为
`group/auto-gpt-6-1-sol`，推理强度为 `medium`，子智能体为 `Boyle`，
会话 ID 为 `01a148f1-834b-7920-82f2-bfa8a81d7ede`，
父会话 ID 为 `01a148e2-1e11-7322-9626-6cbafb956f12`。
未取得底层供应方身份的证据。本次实现仅写入以下三个文件：

- [解析器与流式适配器](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:1)。
- [开发者测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:1)。
- [本交付记录](/E:/aaa-project/rag/docs/story-1-1-json-guard-delivery.md:1)。

## 已交付行为

公开接口为 `JsonLimits`、`BoundedJsonError`、
`parse_json_bytes(raw, limits)`，以及异步接口
`read_bounded_json(request, limits)`。

默认上限：实际请求体 1,048,576 字节、请求头 16,384 字节、深度 8、
值节点 8,192 个、每个 object 64 个键、每个 array 1,024 项、
每个字符串 65,536 个解码后的 Unicode 标量，以及所有键和字符串值
合计 131,072 个标量。数字词法单元另有 256 个字符的有限上限，
符号、小数点和指数均计入。

- 根必须是 object，深度为 1；每层嵌套值（包括标量）增加一层深度。
  object、array 和标量各计一个节点，空容器也计入。键不计节点，
  但同时计入单字符串与总字符串预算。
- 使用迭代式增量解析，不调用通用 JSON 加载器。UTF-8 解码器每次操作
  最多处理 1,024 个输入字节。词法扫描过程中检查计数，在添加超限标量、
  键、数组元素或值之前失败，不拼接完整请求体。
- 字符串保留原始解码内容、空白及规范化形式，不额外进行规范化。
  合法转义代理对解码为一个非 BMP 标量。拒绝非法 UTF-8、孤立代理项、
  解码后重复键、非法语法、非有限数、浮点溢出、超长数字及尾随数据。
  运行时数字转换失败同样转换为有限错误。
- HTTP 接受 `application/json`，可带一个 UTF-8 charset 参数；
  Content-Encoding 可缺省或为 `identity`。请求头名称及媒体类型、
  编码标记不区分大小写。拒绝重复控制头和非法长度；声明超限在读取前
  拒绝，始终检查实际流式字节数，声明长度与实际长度不一致也失败。
- 请求头按 ASGI 原始字段字节计数，所有重复字段均计入：
  `2 + sum(len(name) + len(value) + 4)`，包含末尾 CRLF 及每行
  `name: value` 的分隔符与 CRLF。ASGI 不提供请求行或压缩后的
  HTTP/2 线上帧，因此传输层限制仍由服务器或网关负责。
- 失败后不继续排空请求流。传输层已交付的 chunk 可能超过剩余预算；
  适配器会在解码、保留请求体缓冲或进一步读取前拒绝。该 chunk 的初次
  内存分配由 ASGI 服务器负责。停滞或无限空传输事件仍由现有请求、
  服务器超时策略处理。
- 错误仅包含有限集合中的 `code` 和固定 `message`；公开错误字段及
  异常链不保存请求体、私有 URL、原始传输异常或原始解码异常。
  guard 不记录日志。调用方只可序列化公开字段，不可序列化 traceback
  栈帧的局部变量。
- 适配器由 JSON 入口显式调用，未注册到应用或中间件。
  原件二进制 PUT 保留其独立输入预算。

有限错误码为 `VALIDATION_ERROR`、`REQUEST_BODY_LIMIT_EXCEEDED`、
`REQUEST_HEADERS_LIMIT_EXCEEDED`、`PROTOCOL_STRUCTURE_LIMIT_EXCEEDED`、
`UNSUPPORTED_MEDIA_TYPE`、`UNSUPPORTED_CONTENT_ENCODING` 和
`REQUEST_STREAM_ERROR`。HTTP 状态码及响应包投影由后续 HTTP 交接处理。

## 验证证据

所有应用执行与测试均通过 Netcatty 在 Linux 主机 `120.53.251.166`
运行，独占活动目录为 `/opt/rag-story-1-1/json-guard-work`。
本任务单独打开终端，未争用忙会话。未在本地执行 Python，未操作其他
Compose、修改项目锁文件或改动其他实现目录。

运行环境：CPython 3.12.8、Linux 6.8.0-124-generic x86_64、glibc 2.39。
专用 venv 使用现有 uv 管理的精确版本解释器。原后端 venv 尚无 pytest，
因此在本任务独立 venv 安装了 `pytest==8.4.2`。首次从默认索引下载
超时，随后使用清华 PyPI 镜像成功安装隔离的测试工具。这些结果仅作为
开发者单元测试证据，不代表项目 `--locked` 同步或完整后端重建已通过。

在独占目录执行的原始命令：

```sh
.venv/bin/python -c 'import sys,platform; assert sys.version_info[:3] == (3,12,8); assert platform.python_implementation() == "CPython"; print(platform.platform()); print(sys.version)'
PYTHONPATH=src .venv/bin/python -m pytest tests/test_json_guard.py -q --junitxml=evidence/json-guard-junit.xml
sha256sum src/rag_app/entrypoints/json_guard.py tests/test_json_guard.py
```

最终原始结果：**165 passed in 3.69s**，退出码为 0，没有跳过的测试。
在补充解释器数字转换回归测试前，先前的 164 项测试也全部通过。

覆盖默认字节、请求头、深度、节点、键、数组、单字符串和总字符串预算
的恰等上限与超一边界；键与非 BMP 标量；所有转义状态及截断形式；
解码后重复键；非法编码和数字；双向伪报 Content-Length；声明长度较小
但实际请求体超限；断流与有限错误；无日志或异常链泄漏；各结构限制下
提前停止读取；禁止调用通用加载器；以及原件二进制 PUT 隔离。
确定性差分测试将 120 份生成文档分别编码为 ASCII 转义和直接 UTF-8，
使用随机流切边，与标准库解码结果比较；一个参数化实现的测试内共覆盖
240 份文档编码。

源码 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| 解析器 | `6e7964607cfd6407c3fef08c5f6140f810da8dd07ae23341062ac602b15d373b` |
| 测试 | `087e02881bfef96704669cbf076893e33853c7f0dc87f0deaa4ba964423244d9` |

证据已归档到实际存储桶挂载点下的
`/fileOfRag/testOfRAG/metadata/story-1-1/json-guard/`。
归档包含运行环境记录、pytest 输出、JUnit、源码哈希、已测试的解析器
和测试源码，以及本交付记录的首次英文版本。活动 venv 保留在 Linux
本地存储，不放入存储桶。

本次仅将本地交付说明整理为简体中文，原始命令、标识、测试结果和源码
哈希均保留。根据主会话要求，不再上传，因此远程原始证据保持原样。

## 集成交接与剩余验收门

主控后续可仅在指定 JSON 入口调用 `read_bounded_json`，通过公共
HTTP 错误响应包投影有限错误，再使用公共 Pydantic 模型验证结果。
未知字段、schema_version 及目标 ID 校验仍按规格由该层负责。
本子任务未修改路由、配置、errors 模块、模型、导出、依赖、迁移或
无关测试。

本子任务开发者测试已通过。主会话已派发 Step 5 独立验证，代码和测试
现已冻结供其核验；发现问题后由主会话交回原开发者修复。全新
6.1 Sol medium 独立审查、实际 HTTP/OpenAPI 注册及浏览器集成由
主控后续协调，本实现者未宣称这些步骤已执行或通过。父 Story AC、
真实 PG、锁定重建及四服务生命周期义务保持不变。

用户新增 Git 流程由主会话负责：已初始化 `main`，待 GitHub 登录后
创建 `rag_project`。后续子任务不自行执行 Git 操作或继续上传。
