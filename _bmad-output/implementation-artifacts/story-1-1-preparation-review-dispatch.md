# Story 1.1 源码准备独立静态预审

这次仅为冻结准备代码的独立静态预审，不是完成门审查，不得替代尚未执行的 Linux 开发者测试、Step 5 独立运行验证或父 Story 审查。

审查者为全新 `group/auto-gpt-6-1-sol / medium`，未参与需求分析或实现。只写 `docs/story-1-1-preparation-review.md`，不修改被审代码、测试、交付记录或主控台账。

先读取当前 AGENTS、Story 1.1 工作集、原 epics 中 Story 1.1 四项 AC、contracts/枚举真源/worker-reconcile 短规格。按需读取 C1/C2/H 真源，不加载全部历史规划。父 Story 仍 not_passed，固定 Gitee commit 与完整镜像尚缺。

## 首次冻结范围

比较当前工作文件与基线 `a52ae3090948e7eeea6df87590f15ce35351d247`，直接读取：

- `backend/src/rag_app/contracts/public.py` 的新增 PUBLIC_ENUMS 及原 PUBLIC_MODELS/枚举定义。
- `backend/tests/test_public_contracts.py`、`backend/tests/test_runtime_entrypoints.py` 的新增测试。
- `contracts/generate.py`、`verify_samples.py`、README、samples manifest 及其全部实际样例。
- 对应 HTTP/标量/H 真源、worker 原实现和两份新 delivery 文档作为契约及证据参考。

contracts 与 worker 作者已释放写入；deploy 作者尚在收尾，不提前读取其移动补丁。后续收到主会话冻结通知时可在同一静态预审中追加 D，但不延迟首次具体发现。

## 审查要求

检查确定性的运行/生成失败、schema/TS 引用与可重建一致性、未知字段/Unicode/null/有限错误/私有ID、样例误判与覆盖缺口、资源清理和 Linux 平台语义。区分可证缺陷与仅缺运行证据；不因缺运行证据假造代码缺陷，也不宣称未运行的代码通过。

只读取源码、Git diff 和元数据。不要在本机运行应用、导入、生成、编译、测试或构建；不要重试 Git/Netcatty/镜像/SFTP。无需查询自己模型，主会话已持有派发参数并将读取 turn_context。

输出按严重程度排序的可操作发现，精确文件/行号、触发条件、影响与修复建议；没有发现则明确说明静态范围和残留运行风险。记录被审文件 SHA-256、实际只读命令和全部未执行项，向主会话返回短报告。发现问题交回原作者，不自行修复。
