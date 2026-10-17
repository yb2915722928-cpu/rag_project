# Story 1.1 H 有界 JSON 独立验证记录

日期：2026-10-17（Asia/Shanghai）。验证角色：Step 5 默认档位，仅独立测试验证。
未参与实现，未修改源码、原测试、状态或公共文档，未启动 bmad-build。
本记录只覆盖 H 子门，不代替父 Story 的 HTTP 入口、OpenAPI、错误投影、B 导出与浏览器验证。

## 1. 被验证对象与 hash 核对

| 文件 | SHA-256 | 字节数 |
| --- | --- | --- |
| [json_guard.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:1) | `6e7964607cfd6407c3fef08c5f6140f810da8dd07ae23341062ac602b15d373b` | 13793 |
| [test_json_guard.py](/E:/aaa-project/rag/backend/tests/test_json_guard.py:1) | `087e02881bfef96704669cbf076893e33853c7f0dc87f0deaa4ba964423244d9` | 15395 |

本地工作区与远程 `/opt/rag-story-1-1/json-guard-work/src`、`tests` 三处 hash 一致，
与 [交付记录](/E:/aaa-project/rag/docs/story-1-1-json-guard-delivery.md:1) 中登记的 hash 一致。
验证副本取自该目录，未做任何修改；验证前后再次计算 hash，实现未被改动。

## 2. 运行环境（实际证据）

- 主机：Linux `120.53.251.166`，内核 `6.8.0-124-generic`，glibc 2.39，x86_64。
- 解释器：CPython `3.12.8 (main, Jan 14 2025, 22:49:14) [Clang 19.1.6]`，
  路径 `/root/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin/python3.12`，
  由 `uv 0.13.1` 管理，验证目录 `.venv` 复用它创建。
- pytest `8.4.2`，附带 `iniconfig 2.3.1`、`packaging 26.3`、`pluggy 1.7.0`、`pygments 2.21.0`；
  全部来自本机已有 `uv` 缓存（`uv pip install --offline`），未访问外网。
- 独占目录：`/opt/rag-story-1-1/json-guard-validation`。未触碰开发者 venv、Compose、其他 Story 目录。
- 存储桶：`/fileOfRag` 实际挂载为 `cosfs (fuse.cosfs)`，证据写入
  `/fileOfRag/testOfRAG/metadata/story-1-1/json-guard-validation/`。

命令（均在独占目录内）：

```sh
uv venv --python 3.12.8 .venv
uv pip install --python .venv/bin/python --offline pytest
PYTHONPATH=src:. .venv/bin/python -m pytest tests/test_json_guard.py -q \
  --junitxml=evidence-independent-junit.xml
PYTHONPATH=src:. .venv/bin/python -m pytest probe_limits.py probe_encoding.py probe_headers.py -q \
  --junitxml=evidence-probe-junit.xml
sha256sum src/rag_app/entrypoints/json_guard.py tests/test_json_guard.py
```

## 3. 测试结果（实际运行）

| 运行 | 结果 | 退出码 |
| --- | --- | --- |
| 开发者 165 项套件，独立重跑 | **165 passed / 0 failed / 0 error / 0 skipped**，3.97s | 0 |
| 验证者自写对抗探针 | **85 passed / 0 failed / 0 skipped**，1.57s | 0 |
| 四份文件同一次合并运行 | **250 passed / 0 failed / 0 skipped**，5.42s | 0 |

JUnit XML 属性核验：`tests=165, failures=0, errors=0, skipped=0` 与
`tests=85, failures=0, errors=0, skipped=0`；无 `xfail`、无 `skip` 标记节点。

## 4. 独立重跑覆盖与计数定义复核

独立探针不复用开发者的复算方式，按规格逐项重新推导边界：

- 默认值：body 1048576、header 16384、depth 8、nodes 8192、keys/object 64、
  items/array 1024、string 65536、total string 131072、number token 256，逐一比对通过。
- 根必须是 object；`[]`、`null`、`true`、`0`、`"x"`、空输入、纯空白均以 `VALIDATION_ERROR` 拒绝。
- 深度定义：根 object 为第 1 层，每个内层值（含标量、含空容器）加一层；
  `{"a":`×7 + `1` 通过，×8 拒绝；`{"a":` + `[`×7 通过、×8 拒绝。
- 节点定义：object/array/标量各算 1 个节点，键不算节点。用「根 + 8 个 array + 标量总数」
  形状二分求得实际上限恰为 8192 个节点（8183 标量 + 8 数组 + 1 根），加一即拒。
- 键/数组预算为「每个容器」，非全局：同一份文档两个 object 各 64 键通过；
  一个 array 1024 项加另一个 1 项也通过；单 array 1025 项拒绝。
- 字符串预算按解码标量计：65536 个非 BMP 字符用 `\ud83d\ude80` 转义写入仍通过，
  65537 拒；单值 65536 与 131072 总预算的关系按 1(键)+65536 复核。
- 数字预算是词法长度：256 词元通过、257 拒；整数、小数、负号、指数四种形态分别命中。
- 转义/代理对：合法 8 种简单转义、`\u0000`–`\u001f`、`\u007f` 通过；孤立高低代理、
  高代理后接非低代理、`\ud800` 后接普通字符、截断 `\u` 全部拒绝。
- 非法 UTF-8：overlong、surrogate 编码区、>U+10FFFF、截断多字节序列逐一拒绝；
  合法 4 字节 `\U0001f680` 直写通过。
- 重复键按解码后判定：`"x"` 与 `"\u0078"`、`\ud83d\ude80` 与直写 emoji、
  `a\/b` 与 `a/b`、`a\u0000b` 与直写 NUL、嵌套 object 内重复均拒绝；
  解码后确实不同的键（如 `"a"` 与 `"a\u0000"`）不误判。
- 尾随输入：`junk`、`{}{}`、`[]`、`null`、`,`、`]`、BOM、NBSP 全部拒绝；
  合法尾部空白（空格/`\n`/`\t`/`\r`）接受。
- 结构语法：约 40 条畸形输入（逗号、冒号、括号错配、`01`、`+1`、`.1`、`1.`、`1e`、
  `--1`、`NaN`、`Infinity`、坏转义等）全部以有限错误拒绝。
- 数字溢出：`2e308`、`1e309`、`-1e309`、`1.7976931348623159e308` 拒绝；`1e-999`
  按 IEEE 754 饱和为 0.0，与 `json.loads` 行为一致，接受。
- 跨 chunk：同一文档在 1–39 全部字节切分及 1023/1024/1025/4096 下结果一致；
  另加 200 组随机生成文档 × 4 种随机切分，含非 BMP、组合字符、转义与长整数。
- 流式与取消：断流（body 后抛 `RuntimeError`）、首 chunk 前抛 `ConnectionResetError`
  均为 `REQUEST_STREAM_ERROR`，异常链 `__cause__/__context__` 为 `None`，
  `vars()` 仅含 `code`/`message`，私有 URL/秘密不出现在 `str`/`repr`/`vars` 中。
- 头预算：`2 + Σ(len(name)+len(value)+4)`，恰等 16384 通过、+1 拒绝，重复头一并计入；
  自定义小限额同样验证恰等与超一。
- 媒体/编码：`application/json` 大小写、`charset=utf-8` 带引号/大小写、缺省与
  `identity` 大小写通过；`text/json`、`charset=latin1`、多参数、`charset` 无值、
  `gzip`/`deflate`/`br`/空 `content-encoding` 拒绝。
- Content-Length：不信任。声明超限在读取前拒绝（`req.reads == 0`）；
  声明小于实际字节时按实际字节拒绝；声明与实际不符（含 `0`/`1`/`3`/`1048576` vs 2 字节）
  以 `VALIDATION_ERROR` 拒绝；`-1`、`2,2`、`+2`、`2.0`、`0x2`、`1e3`、空值、
  5000 位长数字分别按有限错误或 body 上限拒绝，且不做任意精度整数转换。
- 重复控制头：`content-type`/`content-length`/`content-encoding` 任意一项重复
  （大小写变体）一律 `VALIDATION_ERROR`。
- 早停：对 depth/array/keys/nodes/number/total-string 六个限额逐项构造超界文档，
  断言 `req.reads < len(raw)`，确认未读完余下 body。
- 禁无界加载：monkeypatch `json.loads`/`json.load`/`JSONDecoder.decode` 为必失败函数后，
  正常与超界文档都不触发调用。
- 不调用 `request.json()`/`request.body()`：探针 `Request` 对这两个方法记账，全程为 0 次。
- 二进制 PUT 隔离：未挂适配器时 `application/octet-stream` 的 1048577 字节原件
  由原处理器完整读走，数量一致；H 不存在任何应用注册或中间件挂载。
- 无日志泄漏：`caplog` 设 DEBUG 级后跑正常、畸形与断流路径，秘密串不出现在日志文本中。
- 幂等：同一输入两次解析结果相等，无隐藏状态。

## 5. 探针过程中修正的自身预期（非实现缺陷）

以下 6 处最初由验证者写错的预期，经复核规格与 CPython/标准库行为后改正，均非实现问题：

- 数组预算是「每 array」，两个 array 共 1025 项合法。
- 单字符串值 65536 标量在 131072 总预算内合法。
- `\ud83d\ude00` 在 `max_string_scalars=1` 下合法（代理对算 1 个标量）。
- 数字词法预算以词元长度计，不是整段原始长度；`1e309` 属浮点溢出而非词元超长。
- 节点上限用「根 + 8 array + 标量」形状实测为 8192，符合「容器+标量、键不计」定义。
- `charset = utf-8` 中 `=` 两侧空格被容忍（实现按 `split(b"=")` 后 `strip()` 处理）。

另记录一条**规格未定义、实现已自行取舍**的行为，交由父 Story 裁决，不算缺陷：

- 解码后确实不同的键不判重，例如 `{"a":1,"a\u0000":2}` 得到两个键
  `'a'` 与 `'a\x00'`。规格只要求「重复键（含转义同键）」拒绝，未规定含 NUL 等
  控制字符的键是否应拒绝。当前行为与 `json.loads` 一致，但建议父 Story 在
  HTTP 契约里明确是否允许控制字符键。

## 6. 未执行项与真实限度

- 未跑完整 backend `--locked` 重建：本项目锁同步尚未完成，本 H 只使用独立
  `uv` 缓存中的 pytest，属开发者单元测试证据，不能当作 backend `--locked` 通过。
- 未做 HTTP 层验证：未挂接到任何路由/ASGI 应用，未验证状态码、错误信封、
  OpenAPI 注册、未知字段与版本号拒绝（那是后续 HTTP handoff）。
- 未做真实 PostgreSQL、pgvector、四服务生命周期验证；本 H 不需要 PG。
- 未验证二进制 PUT 经由中间件时的行为：规格明确 1MiB 只用于 JSON 入口，
  探针只确认「未调用适配器即不受影响」这一消极命题。
- 未覆盖：ASGI 真实服务器（uvicorn 实际进程）下的头预算语义。规格与实现都说明
  ASGI 只暴露头字段字节，不含请求行与 HTTP/2 帧，传输层由服务器/网关负责；
  探针只能验证 `scope["headers"]` 层面的计数公式。
- 未覆盖：慢速/停滞流。实现未提供读取超时，依赖既有请求/服务器超时策略，
  探针无法在无真实服务器的情况下证伪或证实。
- Netcatty 工具侧：执行期间出现过同 session 忙与全局 chat session 占用提示，
  已按规则改为单次短命令完成，未把工具忙记为测试通过；上述结果均为实际退出码 0 的运行。

## 7. 结论

H 子门在冻结 hash `6e796460…373b` / `087e0288…44d9` 下，于 Linux 精确 CPython 3.12.8
实测 **250 passed / 0 failed / 0 skipped**（165 项开发者套件独立重跑 + 85 项验证者对抗探针），
退出码均为 0。未发现实现缺陷；发现 1 条规格未定义行为（含 NUL 的键不判重）需父 Story 裁决。
父 Story 四项 AC、HTTP 接入、真实 PG、`--locked` 重建与四服务生命周期义务不变，
本记录不放行这些门。

证据归档：`/fileOfRag/testOfRAG/metadata/story-1-1/json-guard-validation/`
（`combined-output.txt`、`versions.txt`、`evidence-independent-junit.xml`、
`evidence-probe-junit.xml`、`source-sha256.txt`）。输出中不含 DSN 或任何秘密。
