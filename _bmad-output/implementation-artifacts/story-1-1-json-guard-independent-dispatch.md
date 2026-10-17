# Story 1.1 H 独立验证任务

角色：Step5默认档位，仅独立测试验证，不实现/修复代码，不启动bmad-build。当前是父Story内的H子门，不代替后续HTTP/全Story验证。

先读 [H规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-json-guard.md:1)、[H实现](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/json_guard.py:1)、[开发者测试](/E:/aaa-project/rag/backend/tests/test_json_guard.py:1)、[交付与hash](/E:/aaa-project/rag/docs/story-1-1-json-guard-delivery.md:1)。按实施契约3.5核验，不以开发者自述当通过证据。

独占写 `docs/story-1-1-json-guard-independent-validation.md`；不修改源码/原测试/状态/公共文档。只在Netcatty Linux精确3.12.8运行，使用现有H目录的只读工件与单独证据/临时目录 `/opt/rag-story-1-1/json-guard-validation`；不改开发者venv或Compose。已授权同host独立terminal，先get_environment确认session。可复用已安装精确解释器，验证工具来源/版本如实记录；项目锁同步未完成的事实必须保留。

核对实际源/测试hash，独立重跑165项；再核计数定义、各默认等值/超一边界、跨chunk UTF-8和代理对、重复转义键、长数/浮点溢出、尾随输入、伪报长度、头预算、断流/取消、不读完余body、有限错误和无正文/秘密日志。不必为镜像/PG阻塞重复探测：本H测试不需要PG；二进制PUT不套H。

可在独占远程临时目录写额外验证脚本以尝试击穿边界，不能修改实现或期望迎合代码。发现问题给出输入类别/安全最小复现、实际与预期、证据；修复由原作者承担。报告165项pass/fail/skipped、额外负例、版本/命令/工件hash/副作用与真实限度，归档 `/fileOfRag/testOfRAG/metadata/story-1-1/json-guard-validation/`。DSN/secret不进输出。

本H开发者证据使用专用pytest工具环境，不能据此宣称完整backend `--locked` 重建或HTTP门通过；主会话统一裁决父Story。报告用简体中文并使用绝对可点击文件链接。
