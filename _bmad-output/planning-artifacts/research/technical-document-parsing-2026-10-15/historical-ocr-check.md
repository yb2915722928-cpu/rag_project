# 历史 OCR 与本机配置检查

日期：2026-10-15。性质：方案核对期间检查用户已有教学实验，非 RAG_all 产品实现或模型横评。用户随后明确停止检查并选择 MinerU 云端 API；本记录仅保存已经实际发生的观察，不安排后续 OCR 对照。

## 本机硬件读取

- CPU：从注册表 `HKLM/HARDWARE/DESCRIPTION/System/CentralProcessor/0` 的 ProcessorNameString 读取到 `12th Gen Intel(R) Core(TM) i7-12700H`。
- GPU：运行 `nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader`，返回 `NVIDIA GeForce RTX 3060 Laptop GPU, 6144 MiB, 592.00`。
- 本机不是按口述推定的 12600K，也不应套用桌面 RTX 3060 的显存。16 GB 内存沿用用户提供值，未复测；CIM 查询返回访问限制，没有将查询失败视为硬件不存在。
- GPU 存在不改变用户 API 优先偏好，生产仍为 4 核、4 GB Ubuntu，不依赖个人电脑长期在线。

## 找到的真实旧实验

旧实验日期为 2026-10-09。[实验观察](/E:/projectOfLearning/Agent学习/MeLearn/学习记录/parse-03-PDF与Word/P1-20261009/实验观察.md:9)记录输入是英文小字号教学图片；[原始环境](/E:/projectOfLearning/Agent学习/MeLearn/学习记录/parse-03-PDF与Word/P1-20261009/raw-ocr.json:3)记录引擎为 Windows.Media.Ocr.OcrEngine、可用且选定语言为 zh-Hans-CN。[脚本](/E:/projectOfLearning/Agent学习/MeLearn/学习记录/parse-03-PDF与Word/P1-20261009/Windows识字.ps1:20)优先选择中文语言。

[旧结果](/E:/projectOfLearning/Agent学习/MeLearn/学习记录/parse-03-PDF与Word/P1-20261009/实验结果.json:55)记录 1 倍和 2 倍均未完整恢复两条规则。不是 PaddleOCR、MinerU 或千问 OCR 测试；未找到证明当时实际运行这些替代引擎的结果。

| 输入 | 期望 | 历史 OCR 输出 |
| --- | --- | --- |
| 1 倍，600×800 | Disconnect power before maintenance. / Inspect every month. | Diconnect r 亿 阉 maintenance |
| 2 倍，1200×1600 | 同上 | Dxonnect malntenance. InsIEct e month. |

## 本轮复跑已经发生的观察

将旧脚本与两张原图片复制到工作区 [historical-replay](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/historical-replay/Windows识字.ps1)，不改旧实验文件。只读检查原 PDF 和 PNG 的 SHA256 与旧记录一致。

运行副本时 Windows.Storage.StorageFile 在打开图片阶段返回 E_ACCESSDENIED，识别尚未执行；前两次环境错误分别保存在 [第一次输出](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/historical-replay/raw-ocr-attempt1.json)及[阶段定位输出](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/historical-replay/raw-ocr-attempt2.json)。之后仅将图片加载方式改为普通文件读取相同字节，再写入 WinRT 内存流；未改变图片、语言或 OCR 引擎。

使用 Windows PowerShell 5.1 执行副本后，两张图片均返回 recognized，文字与上表旧输出相同；当前语言仍为 zh-Hans-CN，PowerShell 为 5.1.26100.9711。原始行、词和坐标保存在 [本轮输出](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/historical-replay/raw-ocr.json)。这证明原配置下的失败现象仍出现，不证明唯一根因。

## 判断与停止边界

没有换语言、换 OCR 引擎、对比更清晰输入、运行 GPU 模型或调用收费 API，未隔离图像、语言与引擎的贡献。因此不能结论为“电脑太差”“某模型一定差”或“MinerU 已经更准确”；也不能以 recognized 状态代替正确性。

用户明确选择 MinerU 云端 API 后，已停止旧 OCR 排查，不继续安装模型、跑对照或追问旧模型。MinerU 凭证、上传流程、返回结构、质量和实际费用均待开发接入时验证。保留本记录以免将历史 Windows OCR 失败误记为本项目或 MinerU 故障。
