# 文档解析技术路线选择：本轮证据摘要

> 时序说明：本 digest 保留首轮研究原貌。此后用户明确 API 优先，且 John 实查本机有 RTX 3060 Laptop GPU 6GB；最终路线见 research.md。下文“CPU 对照可主动推进”已被覆盖：本期 OCR/图意/复杂模型解析优先 API，本地 OCR 仅未来用户主动选择的实验，不默认常驻服务。

- 研究时间：2026-10-15；访问日期均为 2026-10-15。
- 研究范围：A 轻量本地提取 + 一条 OCR 链 + 独立视觉能力；B 本地自托管模型解析服务；C 外部文档解析 API。
- 证据边界：仅采用本轮访问的官方文档、官方仓库和许可证；未读项目文件，未执行产品性能测试。委托中给出的项目状态、半个月周期、4C4GB 同机服务器、16GB 无 GPU 开发机及功能目标只用于适配推论，不能证明工具能力或运行结果。
- `class=fact` 为来源直接支持；`class=researcher_inference` 为研究者适配判断或建议。高置信度只表示来源与表述对应明确，不代表供应商能力已经在用户手册上验证。

## 推荐结论

**首选 A，但把它定义为“轻量本地提取、按页保留证据、OCR 和视觉按能力接入”，而不是“只抽纯文本”。** 原生文字和规则表格先走 pdfplumber；pypdf 可补充页级读取/结构操作，不担当表格或 OCR 主引擎。扫描文字首轮只实现一条 OCR 链：可以先采用阿里云 OCR 能力，再以 RapidOCR CPU 做小样本质量/耗时/成本对照，决定是否替换或补充。**不把实现两套常驻 OCR 引擎列为首轮必做。** 图意使用明确支持图片输入的独立视觉能力；普通问答能力配置不能自动当成视觉能力。以上是研究者推论，依据 F1–F6、F10–F12；并非部署完成或效果承诺。

推荐的最强反对理由：A 把章节识别、文字/扫描分流、表格跨页合并、图片裁剪和输出归一化留给应用，真正的工作可能集中在这些边界上。如果真实资料主要是扫描、无框线/合并单元格表格或复杂多栏，A 的规则维护和人工校核可能比 C 的 API 适配耗时更多。pdfplumber 官方也明确不提供 OCR、对 OCR 后文档表格支持较弱（F2）。因此必须用下文最小样例先验证，不以“Python 库轻量”推导“总体工作少”。

**B 是后续可替换后端或独立机器方案，不作为当前同机资源下的默认首轮依赖；C 是样例证明 A 成本过高时的直接备选。** 此处“B 不默认”是资源争用与交付面的判断，并非“4GB 跑不了”。Docling 有 CPU 路线和资源参数，MinerU 当前也明确提供低于完整 GPU 栈的 CPU 层级；两者均不能仅凭产品名称排除（F7–F9）。C 仍须本地保存原文/页图/结果，且外部解析不自动等于能回答工程原理图问题（F11–F12）。

## 本轮来源登记

以下按 8 个证据组列出，组内为不同直接来源。滚动文档未给出可核验发布时间时记为“未标示”，不把搜索引擎抓取日期当成发布日期。

| 组 | 官方直接来源 | publisher | pub_date / 版本观察 |
|---|---|---|---|
| S1 pypdf | [文字提取文档](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)、[LICENSE](https://github.com/py-pdf/pypdf/blob/main/LICENSE) | py-pdf / pypdf maintainers | 未标示；本轮 stable 文档显示 6.20.1；许可证为滚动 main |
| S2 pdfplumber | [README stable](https://github.com/jsvine/pdfplumber/blob/stable/README.md)、[MIT LICENSE](https://raw.githubusercontent.com/jsvine/pdfplumber/stable/LICENSE.txt) | Jeremy Singer-Vine / pdfplumber maintainers | 未标示；滚动 stable |
| S3 PyMuPDF | [Features / License and Copyright](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright) | Artifex | 页面页脚更新 2026-09-03；文档覆盖 1.28.2 |
| S4 RapidOCR | [官方仓库 README](https://github.com/RapidAI/RapidOCR)、[Installation](https://rapidai.github.io/RapidOCRDocs/main/en/install_usage/rapidocr/install/) | RapidAI / RapidOCR Authors | 未标示；滚动 main |
| S5 Tesseract | [Introduction / Installation](https://tesseract-ocr.github.io/tessdoc/Installation.html)、[FAQ 输出格式](https://tesseract-ocr.github.io/tessdoc/FAQ.html) | Tesseract OCR project | 未标示；滚动文档 |
| S6 Docling | [官方仓库](https://github.com/docling-project/docling)、[Advanced options](https://docling-project.github.io/docling/usage/advanced_options/)、[Pipeline options](https://docling-project.github.io/docling/reference/pipeline_options/)、[Vision models](https://github.com/docling-project/docling/blob/main/docs/usage/vision_models.md) | Docling project | 未标示；滚动文档/main |
| S7 MinerU | [官方仓库当前 README](https://github.com/opendatalab/MinerU)、[当前 LICENSE](https://raw.githubusercontent.com/opendatalab/MinerU/master/LICENSE.md) | OpenDataLab / MinerU team | 未标示；本轮 README 显示 MinerU 4.0 |
| S8 阿里云 | [Qwen-OCR API](https://help.aliyun.com/en/model-studio/qwen-vl-ocr-api-reference)、[视觉理解](https://help.aliyun.com/zh/model-studio/vision-model/)、[文档解析大模型版](https://help.aliyun.com/zh/document-mind/developer-reference/document-parsing-large-model-version) | 阿里云 Model Studio / Document Mind | 本轮页面正文未读出更新日期；动态型号不固化为选型结论 |

## Findings

### F1 — pypdf 的职责与内存边界

- claim：pypdf 支持按页提取文字和访问文字变换信息，但自身不做 OCR；PDF 通常不携带章节/表格等语义层，复杂文档的 visitor 坐标也可能错误。官方记录个别巨大解压内容流可能占用大量内存，并建议先检查内容流大小；不能把“轻量库”解释成任意输入都低内存。
- source：[pypdf Extract Text](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)，重点为 Using a visitor、Missing Semantic Layer、OCR vs. Text Extraction 和首部内存说明。
- publisher：py-pdf / pypdf maintainers
- pub_date：未标示（stable 文档本轮显示 6.20.1）
- accessed：2026-10-15
- confidence：high
- class：fact

### F2 — pdfplumber 的可用结构与边界

- claim：pdfplumber 针对机器生成 PDF 提供字符/线条等位置、页号、表格单元格/行/列及 bbox；表格提取结果是 table→row→cell。它可将整页/裁剪页渲染并保存 PNG；不提供 OCR，对 OCR 后文档表格的支持不强。图像对象位置可用，但不直接重建内嵌图像内容。
- source：[pdfplumber README](https://github.com/jsvine/pdfplumber/blob/stable/README.md)，Objects、image properties、Visual debugging、Extracting tables、Comparison to other libraries。
- publisher：Jeremy Singer-Vine / pdfplumber maintainers
- pub_date：未标示（滚动 stable）
- accessed：2026-10-15
- confidence：high
- class：fact

### F3 — 轻量 PDF 库许可证不应混写

- claim：pypdf 当前 LICENSE 是含三项再分发条件的 BSD 3-Clause 形式；pdfplumber 是 MIT；PyMuPDF 与 MuPDF 官方明确采用 AGPL 与商业许可双路径。PyMuPDF 有页渲染、表格等能力，不能依据旧比较声称它“不支持表格”；但不能把其许可当成 MIT/BSD。
- source：[pypdf LICENSE](https://github.com/py-pdf/pypdf/blob/main/LICENSE)、[pdfplumber LICENSE](https://raw.githubusercontent.com/jsvine/pdfplumber/stable/LICENSE.txt)、[PyMuPDF Features / License](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)。
- publisher：py-pdf；Jeremy Singer-Vine；Artifex
- pub_date：前两者未标示；PyMuPDF 页面 2026-09-03
- accessed：2026-10-15
- confidence：high
- class：fact

### F4 — CPU OCR 是真实可选路线

- claim：RapidOCR 官方给出 `rapidocr` 加 ONNX Runtime 安装路线和 CPU Docker 构建测试；默认支持中英文。源码及工程组件采用 Apache 2.0，当前 README 也说明所捆绑/托管、源自官方 PaddleOCR 的转换权重按上游 Apache 2.0 条款再分发。安装文档说明运行时需要显式安装推理引擎。此处不引用未经本机验证的内存或吞吐数字。
- source：[RapidOCR README](https://github.com/RapidAI/RapidOCR)、[Installation](https://rapidai.github.io/RapidOCRDocs/main/en/install_usage/rapidocr/install/)。
- publisher：RapidAI / RapidOCR Authors
- pub_date：未标示
- accessed：2026-10-15
- confidence：high
- class：fact

### F5 — Tesseract 可作另一个 OCR 候选，输出不必只有字符串

- claim：Tesseract 是 Apache 2.0 OCR 引擎，可从图像提取印刷文字；Linux 发行版可提供引擎和简体中文等语言数据。官方列出 txt、可搜索 PDF、hOCR、TSV 等输出。它与 OCR 语言数据是分别安装的两个部分。本轮没有获得它在用户手册上的中文识别率或共享 4GB 部署结果。
- source：[Tesseract Installation](https://tesseract-ocr.github.io/tessdoc/Installation.html)、[FAQ](https://tesseract-ocr.github.io/tessdoc/FAQ.html)。
- publisher：Tesseract OCR project
- pub_date：未标示
- accessed：2026-10-15
- confidence：high
- class：fact

### F6 — OCR、表格恢复、图示语义是不同验收项

- claim：不应从 OCR 文本输出直接推导“表格结构正确”或“理解箭头/连线/状态关系”。OCR 候选只负责扫描文字链；图意必须单列视觉输入、问题和答案核对；数值表格另验表头、行列、合并关系、数值和单位。首轮可以用 API OCR；CPU OCR 作为替换/成本对照候选，不强制两者同时实现。
- source：F1、F2、F4、F5、F10、F12；它们分别显示文本、表格、图片能力的独立接口和边界。
- publisher：研究者（依据上述官方来源）
- pub_date：2026-10-15
- accessed：2026-10-15
- confidence：high（分工建议），实际质量 unknown
- class：researcher_inference

### F7 — Docling 可提供统一结构与页图，不能当作任意图意正确保证

- claim：Docling 官方列出布局、阅读顺序、表格结构、OCR、统一 DoclingDocument 和 JSON/Markdown/HTML 输出，并支持本地运行/API 服务。Pipeline options 分别控制页图、图片、表格、OCR、图片描述；官方视觉文档说明保留页图后可按 provenance 裁剪图片，单独表格片段仍可能保持为分开的表。仓库代码为 MIT；本轮未逐个核验可选模型权重的许可。
- source：[Docling 仓库](https://github.com/docling-project/docling)、[Pipeline options](https://docling-project.github.io/docling/reference/pipeline_options/)、[Vision models](https://github.com/docling-project/docling/blob/main/docs/usage/vision_models.md)。
- publisher：Docling project
- pub_date：未标示
- accessed：2026-10-15
- confidence：high
- class：fact

### F8 — Docling 有 CPU/缓冲控制，但共享小机器结果未知

- claim：官方 Advanced options 说明模型推理和 PDF 解析线程分别配置，默认 CPU 线程为 4；队列长度和预解码页数影响峰值内存，可限制缓冲数量。本轮未发现足以承诺“后端、PostgreSQL、Docling 共用 4GB 稳定运行”的官方要求或实测。
- source：[Docling Advanced options](https://docling-project.github.io/docling/usage/advanced_options/)。
- publisher：Docling project
- pub_date：未标示
- accessed：2026-10-15
- confidence：high（控制项明确）；shared-host feasibility unknown
- class：fact

### F9 — MinerU 当前有 CPU 层级，许可也已不能套旧印象

- claim：本轮当前 README 显示 MinerU 4.0；官方声称 basic 的 ONNX 路线最低 RAM 2GB，standard/advanced 的 ONNX+llama.cpp 路线最低 8GB；完整 GPU 栈另有更高要求。这些是厂商最低要求，不能推导本项目混合部署可用。当前许可证基于 Apache 2.0 并附商用阈值和对外在线服务署名等条件，不能简称无附加条件的 Apache 2.0，也不能按旧版本直接报 AGPL。
- source：[MinerU README](https://github.com/opendatalab/MinerU) 的 Model Engines with Extras、[MinerU LICENSE](https://raw.githubusercontent.com/opendatalab/MinerU/master/LICENSE.md)。
- publisher：OpenDataLab / MinerU team
- pub_date：未标示（滚动 main/master）
- accessed：2026-10-15
- confidence：high（官方声称）；shared-host feasibility unknown
- class：fact

### F10 — 阿里云可把 OCR 细化为按页/图片的不同任务

- claim：Qwen-OCR 官方 API 区分文字识别、带 bbox 的高精度识别、表格解析和文档结构解析；返回中提供请求 ID 和输入/输出/图片 Token 使用量，并提供图片缩放控制。不同任务/接口不应假定返回相同定位字段；接入时需验实际响应。API 任务枚举本身不是用户复杂表格质量证明。
- source：[Qwen-OCR API reference](https://help.aliyun.com/en/model-studio/qwen-vl-ocr-api-reference) 的任务表、响应字段、Image resolution control。
- publisher：阿里云 Model Studio
- pub_date：本轮页面未读出更新日期
- accessed：2026-10-15
- confidence：high
- class：fact

### F11 — 外部全解析 API 有结构和原图入口，但有持久化责任

- claim：阿里云文档解析大模型版是提交、查状态、取结果的异步接口；结果含页号、层级、阅读顺序和坐标，visualLayoutInfo 可返回页图信息，表格可选 HTML。完成后的结果查询窗口为 24 小时。VLM 增强会增加响应时间和每页费用；本轮未读价页，不报告价格数字。chart2table 是图表数据能力，不证明任意工程原理图理解。
- source：[文档解析大模型版](https://help.aliyun.com/zh/document-mind/developer-reference/document-parsing-large-model-version)，调用方式、OutputFormat、返回字段、llmResult 说明。
- publisher：阿里云 Document Mind
- pub_date：本轮页面未读出更新日期
- accessed：2026-10-15
- confidence：high
- class：fact

### F12 — 图意应独立配置明确的视觉能力

- claim：阿里云官方“视觉理解”页明确面向图像分析、视频理解和 OCR，另列从视觉输入获得 JSON 的结构化输出及专门的 OCR 能力。该页面列出的模型清单只代表本轮可见内容。
- source：[阿里云视觉理解](https://help.aliyun.com/zh/model-studio/vision-model/)。
- publisher：阿里云 Model Studio
- pub_date：本轮页面未读出更新日期
- accessed：2026-10-15
- confidence：high（能力分类）；图意质量 unknown
- class：fact

## 三条路线适配比较

本表全为 `class=researcher_inference`，publisher=研究者，pub_date=accessed=2026-10-15，confidence=medium；来源分别列于末栏。表中“应用须做”是实现建议，不宣称工具自带。

| 维度 | A：轻量本地 + 一条 OCR + 独立视觉 | B：自托管解析服务 | C：全外部解析 API | 推论依据 |
|---|---|---|---|---|
| 章节/引用定位 | 应用把页号、bbox、标题规则/书签归一化；保留原始提取，章节不靠纯字符串自动保证 | 适配其结构/阅读序/provenance；仍核对标题层级与版面坐标 | 适配页号、层级、坐标；不要只留 Markdown | F1、F2、F7、F11 |
| 规则表格/简单跨页表 | 本地表格可拿行列/bbox；跨页须保留各页片段及重复表头、列对齐证据，再做显式合并或人工确认 | 结构模型减少手写规则的潜力须用样例验证；跨页不应默认合并成功 | 可取结构/HTML；数值、单位、跨页仍须验收 | F2、F7、F10、F11 |
| 图意 | 原页/裁剪图发送独立视觉能力；保存图号、caption、bbox、结果和问题 | 图片描述/VLM 是可选额外阶段；不以解析服务成功代替图意正确 | 全文解析之后仍可能需独立视觉调用；chart2table 不覆盖任意原理图 | F6、F7、F11、F12 |
| 本地页图与原图 | 由原 PDF 渲染整页，必要时 bbox 裁剪；避免只保存内嵌位图而遗漏矢量图/连线 | 明确启用页图/图片输出并落盘；服务输出不是永久备份 | 保留本地原 PDF 与页图；及时持久化云端结构响应，不依赖短期可查结果 | F2、F7、F11 |
| 资源与交付 | 最少本地模型面；文字/表格/渲染也需限输入大小、逐页/限并发验证 | 多出服务、模型下载、版本和线程/缓冲管理；官方支持 CPU 不等于共享机器稳定 | 本地仍负责上传/轮询/存储；本地模型负担少，但网络和服务状态变为依赖 | F1、F4、F8、F9、F11 |
| 成本可观察 | 分别记录本地耗时/峰值内存、OCR页数/Token、视觉图片Token、重试次数；不把本地算力当零成本 | 记录模型/服务版本、CPU/内存/时长、重处理次数；对比样例人工校核工作量 | 记录解析页数、增强选项、请求/任务ID、重试和视觉Token；账单再对账 | F8、F10、F11、F12 |
| 重试/恢复 | 页/阶段独立持久状态；同一原文hash+配置+版本缓存成功产物；失败可替换该能力 | worker 与解析服务分开记录状态；服务重启不应把成功页重新入库；模型升级生成新版本 | 保存上游job ID先恢复轮询，不因短超时盲目重新提交；API未证明提交幂等时由应用防重复 | F1、F7、F11；恢复设计为建议 |
| 上游耦合 | 一套内部结果结构，OCR/视觉适配器可换；分流规则自身成为维护负担 | 适配结构和模型版本；绑定服务API、输出schema、模型许可 | 绑定任务流程、计量、字段和访问窗口；应用内格式隔离厂商响应 | F2、F7、F9–F12 |

## 改选条件

以下均为研究者决策规则（class=researcher_inference，source=F1–F12，publisher=研究者，pub_date=accessed=2026-10-15，confidence=medium）：

1. 若 A 在最小样例中无法稳定保留必需的表头/行列/数值/单位，或为两种手册就引入大量专用规则，应优先试 C 的同样例结构结果；只有可核对质量改善且可接受外发/账单后改选 C。
2. 若材料不能外发，且 A 的 CPU OCR/表格效果达不到验收，则评估 B；先在开发机完成证据验证，再决定独立部署/服务器资源，不能用最低要求直接宣布同机可用。
3. 若大量重复处理使外部调用成本或供应商稳定性成为主问题，且 B 在真实样例上更合适，可将 B 接入原来的解析能力适配器；无需改掉本地原文、页图、结果版本与引用合同。
4. 若数据以原生文字和有规则表格为主，A 通过样例且校核工作量可接受，继续 A，不因模型解析“更全”而自动增加常驻服务。

## 最小验证样例与观察

这是验证设计，不是已完成测试（class=researcher_inference；source=上述证据边界 F1–F12；publisher=研究者；pub_date=accessed=2026-10-15；confidence=medium）。只用用户允许的材料，先各取必要页，不必先跑整本手册。

| 样例 | 必须观察/保留的结果 | 失败说明什么 |
|---|---|---|
| 普通中文技术手册：一页章节/规则 + 两页简单跨页参数表 | 标题路径与物理页号可回到原页；重复表头不丢；每行列关系、数字、正负号、小数点、单位与原图一致；跨页片段有各自来源 | A的章节/表格规则是否足够；错一列应阻止该表自动通过 |
| 复杂手册：多栏、合并单元格/无框线表各取一例 | 阅读顺序、表头作用范围和合并单元格可解释；输出不确定项，核对原页后决定规则或外部解析 | 不能只比较“文字很多/Markdown好看”；决定A或C |
| 扫描页：中文规则与数字单位各一例 | OCR文字、位置或可回页证据；数字/单位错误单列；比较首选API OCR与一个CPU候选的校核量、耗时及内存 | 扫描识别链是否满足；CPU是候选而非强制第二实现 |
| 含箭头/连接关系的图示：一道仅靠正文/图题答不出的题 | 原页与裁剪图都保留；视觉调用可回答关系/条件；每项回答能指向图中实际元素；未知时明确不足 | OCR成功不能代替图意通过；若图太复杂则标为不支持/待人工 |
| 恢复与重处理 | 提交后中断worker再恢复；模拟上游超时/限流；记录任务ID、失败阶段、次数和已成功产物；改解析配置后生成新版本 | 检查重复收费/重复入库、来源漂移、旧结果被无痕覆盖 |
| 同机资源观察 | 一次一文档，连续处理样例；记录各阶段墙钟时间、进程峰值RSS、CPU、磁盘、后端与数据库的可用性；据实确定页图分辨率/线程/缓冲 | 只有这项证据能支持共享4GB的实际运行结论；本报告不预判结果 |

通过标准应在验证前固定：所有必测问题须有正确内容及可回原页证据；关键数值/单位和行列关系不能带已知错误入库；未通过内容保留待校核状态。先比较错误类型和人工校核工作量，再比较调用成本，避免只按 OCR 文本字符数选路线。

## 仍需用户确认的一个问题

**技术手册中的扫描页和选中的图示，是否允许发送至阿里云外部 OCR/视觉/文档解析服务？** 这决定 A 的首条 OCR 链和 C 是否可选；若不允许，必须先验证本地 CPU 路线，必要时为 B 调整部署资源。此问题是决策所需信息，不假定用户已经批准或拒绝文档外发。

## 未验证与不得外推

- 未做库安装、中文资料效果评测、服务器内存/吞吐实测；不承诺 4GB 能跑/不能跑，也不估计整本手册处理秒数。
- 未读取价格页，不给单价、免费额度或总预算数字；仅指出 API 可观察计量字段与需记录的用量。
- 未逐一审核可选模型权重、系统依赖和云服务协议/数据保留条款；本轮许可证结论只覆盖明确列出的代码/权重说明。
- 未获得可担保任意复杂原理图正确理解的证据；最少一道图意题可作为明确验收项，不能扩写为任意图示通解。
