---
title: 文档解析研究：用户已确认 MinerU 云端 API
type: technical
topic: document-parsing
decision: 用户已确认首版采用 MinerU 云端 API 上传解析
source: native-run
status: complete
preset: standard
validation: normal
created: 2026-10-15
updated: 2026-10-15
claims_verified: 0
claims_unverified: 15
---

# 文档解析：用户已确认 MinerU 云端 API

**最终状态：用户已明确选择首版采用 MinerU 云端 API 上传解析，覆盖此前 A 路线建议。** 用户原话：“不用搞了，使用mineru就行，配置api可以上传识别的”。这里指云端 API，不是本地自托管 MinerU；不再开展 OCR 归因、候选比较或新实验，不再抛选型或样例问题。

下一步由实施工作配置 API 并接通上传解析。**当前尚未配置具体凭证/端点，未实际上传，图意、表格、章节/页引用质量均未验证**；没有用户已掌握或工程已完成的结论。保留原文件、云端任务/响应与来源元信息的设计要求，实际返回字段和处理规则在接入时据真实结果确定。

下文 TR 两项目实现事实、候选比较与旧实验记录保留为研究背景，凡“推荐 A”“CPU 对照”“选择问题”等早期建议均被本段最终决定覆盖，不再作为本期行动项。

**最新硬件边界：**John 于 2026-10-15 本机只读检查回报 i7-12700H、RTX 3060 Laptop GPU、6144 MiB 显存；覆盖先前“无 GPU”和用户口述“12600K”的假设。RAM 沿用用户 16GB、未复测。生产仍为 4C4GB Ubuntu 同机 Web/后端/数据库。本研究未做 OCR 或资源实测，不因有 GPU 改成电脑常驻解析服务。

## TR：两项目的真实链路

本轮固定提交：WeKnora **a37a1bc51ad85d096df341f6d3a098f60d586f52**；MaxKB **0fa9a0dae8850c1878f087f0d81c974c1d424b06**，均为 2026-10-15 快照。详细永久链接、行号和原始快照见 [实现 digest](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/digests/implementation-r1.md)。

| 环节 | WeKnora | MaxKB（限定所读标准 PDF 链路） |
| --- | --- | --- |
| 上传与普通解析 | 保存原件后进入任务、解析路由。PDF 默认 builtin：独立 Python docreader 用 pypdfium2 逐页分类、抽文字/图片；Office 在 anydoc 绑定可用时条件优先进程内处理，规则可覆盖。[1][2] | 保存原件、生成 source_file_id，再按 support 选本地 handle。PDF 使用 pypdf，依次尝试目录、内部链接、文字/字体规则分段。所读路径未见默认 OCR 或厂商解析 API 调用，不能外推为全产品无 OCR。[5] |
| OCR、图意与默认/可选 | docreader 输出文字/原图；多模态开启且模型配置满足条件后，Go 分别执行 OCR 与 caption，调用配置的 VLM Predict，不能写成固定 PaddleOCR。mineru/paddleocr_vl 自托管 endpoint 与 *_cloud 托管 API 分别注册、配置；支持不等于已启用。[1][3] | 标准回退分支能保存嵌图，但不能据此保证目录分支也都保存。另有可选 ImageUnderstand 工作流节点，输入图片、调用配置模型；不是上传 PDF 默认生成图意。模型在本地还是厂商 API 取决于配置。[6][7] |
| 章节与引用 | source_blocks 关联 Markdown 范围与来源；SourceLocator 含 PDF 页/bbox、其他格式结构位置。扫描页有页级定位，不等于每个 OCR 段有准确 bbox；结构位置不等于各格式物理页或完整章节树。[2][4] | TOC 分支用页/top 定边界，输出 title/content；所读输出及 Paragraph 未见 PDF 页/bbox。目录分段不能等同页级引用已保留，也不能推断全产品无定位能力。[6] |

复用宜借鉴契约与规则，通过自己的适配层实现：WeKnora 主仓 MIT，明确排除第三方组件；Python parser 不包含完整 Go 后处理、存储和来源绑定。[8] MaxKB 主仓 GPLv3，handle 耦合 Django、File ORM、SplitModel。[9] 直接抽一个 Python 文件不等于零成本集成，复制时须逐项核对代码、依赖和权重许可。

## TS：此前候选比较（已由用户选择覆盖）

约半个月、FastAPI+PostgreSQL+pgvector、独立 Python worker、一次一份文档，以及 API 优先偏好是决策约束。下表为研究者适配判断，不是实测排名。

| 路线 | 资源与工作量 | 引用、表格、OCR、图意 | 成本、耦合与许可 |
| --- | --- | --- | --- |
| **A：轻量本地 + 按需 API（早期推荐，已由最终决定覆盖）** | 本地校验、原件/页图保存、轻量原生文字提取及结果归一化；模型阶段交 API。实现超时、结果绑定和恢复。 | 页/章节/位置先保存；规则清楚的原生表格可轻量提取，扫描/复杂表格用结构 API；OCR 与视觉分别配置，跨页与关键数值仍校核。[10][13][14] | 按任务记录请求、页数、Token、重试和账单；内部结构隔离厂商字段。pypdf 为 BSD 3-Clause、pdfplumber 为 MIT；PyMuPDF 是 AGPL/商业许可双路径，不混写。[10] |
| **B：自托管模型解析服务** | Docling/MinerU 有 CPU 路线，并非一律必须 GPU；增加模型、服务、线程/缓冲与版本运维。共享 4GB 稳定性未知，不作为本期默认。 | Docling 的结构、OCR、表格、页图、图片描述是独立选项；解析完成不代表跨页表或工程图意正确。[12] | 观察资源及校核成本。Docling 代码 MIT，模型许可另查；当前 MinerU 许可有附加条件，不能简称普通 Apache 2.0 或套旧版印象。[12] |
| **C：整文优先外部解析 API** | 如阿里云文档解析大模型版，提交、查状态、取结果；本地模型负担少，仍做上传、轮询、存储、恢复。 | 可返回页号、层级、位置、页图、表格 HTML；字段不保证内容正确。图表解析不等于工程原理图语义，仍可能另需视觉 API。[13][14] | 绑定厂商任务、字段、计量。DocMind 完成后的查询窗口为 24 小时，须及时持久化响应；本地保留原 PDF/页图。[13] |

权重：交付运维 30%，引用校核 25%，目标覆盖 25%，成本可观察/可替换 15%，许可边界 5%。1–5 分越高越适配；分值是研究者判断，未获用户确认，不是性能或价格数字。

| 路线 | 交付运维 | 引用校核 | 内容覆盖 | 成本/替换 | 许可边界 | 加权参考 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 5 | 5 | 4 | 4 | 4 | 4.55 |
| B | 1 | 4 | 4 | 2 | 3 | 2.75 |
| C | 4 | 4 | 4 | 2 | 3 | 3.65 |

**最强反对理由：**A 的分流、章节、跨页表格和来源归一化仍由应用承担，轻量库不代表整体工作少。pdfplumber 不提供 OCR，对 OCR 文档表格支持有限。[10] 若真实资料主要是扫描/复杂版面，或很快积累大量专用规则，C 更合理；用同样例比较质量与实际调用成本。B 只留给用户将来主动选择本地实验，或出现明确部署约束且资源验证通过时再讨论。

## 此前对 John 建议的修正（历史背景，非最终路线）

1. 扫描 OCR、图意和需要模型的复杂解析 **API 优先**；本期不推进本地 OCR 对照或常驻服务，不依赖电脑长期开机。不要把 API 优先扩成所有纯文本都付费全文解析。
2. “普通表格本地”限定为可轻量提取且结构清楚的内容。扫描、错列、复杂/跨页表格使用结构 API 后，仍验表头、行列、数值、单位和各页来源。[10][13]
3. OCR、表格结构和图意分别验收。即使同一多模态模型承担多种任务，也分别保存任务/提示/结果；“问答模型接通”不能代替图片输入能力验证，“文字认对”不能代替看懂箭头/连接/条件。[3][7][14]

建议内部契约：原文件 hash、版本、物理页、章节路径、可得 bbox、原页/图键、文字/表格/图意结果、解析器/模型与配置版本、attempt、原始响应、修订记录。缺失定位显式为空，不伪造；成功和失败都保留，重处理形成新版本。这是 RAG_all 设计建议，不声称上游均已完整实现。

Qwen-OCR 可返回请求 ID、输入/输出/图像 Token 和截断状态，有助追溯；usage 不等于实际账单。[14] 本轮不报单价、内存估计或秒数。

## 旧 OCR 记录（背景，已停止继续归因）

**现在能判断：旧结果不能代表 PaddleOCR、MinerU 或千问的质量，也不能证明硬件不足。**本研究已补读父级定位的旧记录：2026-10-09 使用 Windows.Media.Ocr.OcrEngine，系统实际只列出并选用 zh-Hans-CN，输入是英文小字号教学图；1倍/2倍倍率下都未完整恢复两句预定规则。脚本优先选中文语言，属于已知测试配置；不能据此直接断言语言就是唯一根因。[旧环境](/E:/projectOfLearning/Agent学习/MeLearn/学习记录/parse-03-PDF与Word/P1-20261009/raw-ocr.json:3)，范围：3–10；[样本说明](/E:/projectOfLearning/Agent学习/MeLearn/学习记录/parse-03-PDF与Word/P1-20261009/实验观察.md:9)；[语言选择](/E:/projectOfLearning/Agent学习/MeLearn/学习记录/parse-03-PDF与Word/P1-20261009/Windows识字.ps1:20)，范围：20–25；[两次结果](/E:/projectOfLearning/Agent学习/MeLearn/学习记录/parse-03-PDF与Word/P1-20261009/实验结果.json:55)，范围：55–76。

只改变渲染倍率，没有模型对照，无法隔离输入、配置和引擎因素；RTX 3060 也不是这些假设的排除证据。John 已在用户停止指令前用相同图片与语言复跑，输出与旧记录一致，实际过程见 [历史检查记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/historical-ocr-check.md)。没有隔离根因、比较其他模型或调用 MinerU；用户要求停止后已停止，不给模型好坏排名。

先区分三层错误：文字本身错；文字正确但表格/阅读顺序错；文字正确但无法理解图中关系。后两类不能简单归为字符识别模型差。[10][14][15] 若只有文字错，再检查实际送入模型的分辨率/缩放、旋转、噪声/对比度、语言及版面配置，并记录模型版本。Tesseract 官方明确讨论分辨率、二值化、噪声、歪斜和分段对质量的影响；这是其具体引擎证据，不据此认定旧系统用了 Tesseract。[15] Qwen-OCR API 也有图片缩放/旋转控制，应核对实际请求而非只看原 PDF。[14]

若以后用户主动希望本地对照，应固定同一图和金标，先区分预处理与模型变化，再比较错误类型；当前不新增这项实施任务，最终按用户已确认的 MinerU 云端 API 路线执行。

## 此前拟定的验证观察（背景，未执行）

先用同一份真实手册的必要页，固定人工可核对的答案/单元格；不先跑整本，不新增本地 OCR 工程。

| 样例 | 通过观察 | 失败及处理 |
| --- | --- | --- |
| 一章原生文字、编号规则与单位 | 标注规则/值/单位正确；章节未串；引用回正确页 | 字序/乱码/定位错，保留失败并切目标页 API |
| 两页简单跨页表格 | 重复表头不成数据行；目标行列/值/单位正确；保留两页来源 | 错列/错值/错单位即失败；比较结构 API，不能按 Markdown 外观判成功 |
| 扫描与原生混合页 | 扫描页经 OCR API；原生文字不无故全量重识别；关键字段和页号正确 | 漏页、小数点/负号错、截断记成功：页级失败重处理 |
| 必须看连线/方向/图例的一道题 | 视觉 API 接收原图，答案符合金标，引用可回原图/原页 | 只列标签/捏造连接：标不足，保留原图，不承诺任意原理图 |
| 一次超时/中断、重试、修订 | 可恢复，不重复入库；任务 ID、旧产物可查，修订不被静默覆盖 | 盲目重提交/重复块/丢引用即修任务和版本逻辑 |

记录页数、阶段时长、worker 峰值内存、后端/数据库可用性、API 错误、任务 ID、usage、重试和账单。只有目标环境证据才能说明 4GB 的实际余量；API 优先不能免除上传/渲染的资源验证。

## 当前未验证范围与后续边界

- 未部署上游或候选库，未调用收费 API；本研究未新跑 OCR、跨页表格、图意、引用精度、时延、内存及费用实验。旧记录仅为上述具体 Windows OCR 教学样本。
- 未验证任意复杂手册、所有预览回跳或完整章节树；未审计 MaxKB 插件/企业扩展、所有依赖和权重许可。官方接口不等于目标资料质量保证。
- 用户已确认 MinerU 云端 API，不再保留选型或代表性资料问题。实际凭证/端点、上传识别、图意与表格/引用质量留实施阶段据实配置和验证；本研究不继续实验。

## 来源附录

访问日均为 **2026-10-15**。提交日是快照日期，不冒充文件修改日。产品特定主张为官方单一出版者证据，账本标 unverified，表示未完成独立出版者复核，并非未读取源码；设计推论已另标。详细检索事实见 [路线 digest](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/digests/selection-r1.md)。

| 编号 | 支持内容 | 官方来源 / publisher | 发布日期 | 置信度 |
| --- | --- | --- | --- | --- |
| [1] | WeKnora 保存、默认和服务区分 | Tencent：[原件/任务](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_create.go#L197-L262)、[默认](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/infrastructure/docparser/engines.go#L45-L65)、[配置门槛](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/infrastructure/docparser/engines.go#L202-L320) | 快照 2026-10-15 | medium |
| [2] | PDF 逐页分类、输出 | Tencent：[分类](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/parser/pdf_parser.py#L1608-L1652)、[输出](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/parser/pdf_parser.py#L1709-L1770) | 快照 2026-10-15 | medium |
| [3] | OCR/caption 模型与开关 | Tencent：[OCR](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/image_multimodal.go#L539-L551)、[分派](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/image_action_loop.go#L108-L122)、[开关](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/knowledgebase.go#L624-L633) | 快照 2026-10-15 | medium |
| [4] | 来源定位契约 | Tencent：[SourceLocator](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/source_locator.go#L9-L71) | 快照 2026-10-15 | medium |
| [5] | MaxKB 标准上传/PDF | 1Panel-dev：[上传路由](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1255-L1284)、[PDF](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L51-L99) | 快照 2026-10-15 | medium |
| [6] | 嵌图/TOC/定位边界 | 1Panel-dev：[嵌图](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L141-L158)、[TOC 输出](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L369-L390)、[Paragraph](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/models/knowledge.py#L251-L266) | 快照 2026-10-15 | medium |
| [7] | 可选图意节点 | 1Panel-dev：[模型调用](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/flow/step_node/image_understand_step_node/impl/base_image_understand_node.py#L135-L186)、[图片输入](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/flow/step_node/image_understand_step_node/impl/base_image_understand_node.py#L272-L301) | 快照 2026-10-15 | medium |
| [8] | WeKnora 许可/复用 | Tencent：[MIT 及例外](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/LICENSE#L1-L32)、[Python 依赖](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/pyproject.toml#L7-L29)；结合 [3][4] | 快照 2026-10-15 | medium |
| [9] | MaxKB 许可/耦合 | 1Panel-dev：[GPLv3](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/LICENSE#L1-L6)、[框架依赖](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L17-L25) | 快照 2026-10-15 | medium |
| [10] | 轻量库边界/许可 | 各项目官方：[pypdf 提取](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)、[BSD](https://github.com/py-pdf/pypdf/blob/main/LICENSE)、[pdfplumber](https://github.com/jsvine/pdfplumber/blob/stable/README.md)、[MIT](https://raw.githubusercontent.com/jsvine/pdfplumber/stable/LICENSE.txt)、[PyMuPDF 许可](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright) | 滚动；部分未知 | medium |
| [11] | CPU OCR 技术可选 | RapidAI：[RapidOCR](https://github.com/RapidAI/RapidOCR)、[安装](https://rapidai.github.io/RapidOCRDocs/main/en/install_usage/rapidocr/install/) | 未标示 | medium |
| [12] | 自托管能力/控制/许可 | 各项目官方：[Docling](https://github.com/docling-project/docling)、[pipeline](https://docling-project.github.io/docling/reference/pipeline_options/)、[资源控制](https://docling-project.github.io/docling/usage/advanced_options/)、[MinerU](https://github.com/opendatalab/MinerU)、[许可](https://raw.githubusercontent.com/opendatalab/MinerU/master/LICENSE.md) | 滚动；未知 | medium |
| [13] | 异步结构解析/定位/查询窗口 | 阿里云：[文档解析大模型版](https://help.aliyun.com/zh/document-mind/developer-reference/document-parsing-large-model-version) | 本轮未读出更新日 | medium |
| [14] | OCR/usage/视觉/图片控制 | 阿里云：[Qwen-OCR API](https://help.aliyun.com/en/model-studio/qwen-vl-ocr-api-reference)、[视觉理解](https://help.aliyun.com/zh/model-studio/vision-model/) | 动态文档；正文未显示更新日 | medium |
| [15] | 输入/分段影响 OCR，表格边界 | Tesseract 项目：[Improving quality](https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html) | 未标示 | medium |

## 时效与完成范围

账本/脚本时效见 [时效记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/staleness.md)：源码兼容性按一个月复查，已知最早 **2026-11-15**；无发布日期的接口和许可实际接入前重查。选型超过两个季度应刷新。

本轮官方取证已完成，最终决定为用户确认的 MinerU 云端 API。按最新要求停止 OCR 归因、候选研究与实验；未配置/调用 MinerU API，未生成 HTML、演示稿或工程成绩，未改 PRD。

