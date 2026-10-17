# Implementation research digest — WeKnora / MaxKB

- accessed: 2026-10-15
- scope: 本轮读取官方 GitHub 固定提交源码；未部署，未运行样本，未作性能/内存/解析质量实测；未读取任何项目文档。项目约束只用于末尾决策推断。
- WeKnora commit: a37a1bc51ad85d096df341f6d3a098f60d586f52；committer_date: 2026-10-15T07:19:23Z。
- MaxKB commit: 0fa9a0dae8850c1878f087f0d81c974c1d424b06；committer_date: 2026-10-15T07:16:05Z。
- commit date 是快照日期，不等于每个文件的最后修改日期；以下 pub_date 均据此标明。
- 原始证据逐文件保存在 [imports index](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/imports/implementation-r1/index.json.md)。索引记录 repo/path/完整commit/blob SHA/官方URL，原文保存于相应项目子目录。为遵循本轮只写 Markdown 的要求，非 Markdown 原文件名统一追加 `.md`；索引 path 是上游路径，查本地快照时追加该后缀。
- evidence class: source-code = 实现直接证据；inference = 有明确来源的设计判断。所有事实为 single-source（同一项目官方仓库内多文件互证不算独立交叉验证）。

## WeKnora findings

### W1 上传、原件与解析路由
- claim: 文件上传先落存储并记录 FilePath，再投递 Asynq 文档处理任务。处理时合并租户/单次上传覆盖，根据文件类型和知识库 ParserEngineRules 决定 reader，重新读取已保存原文件并调用 reader.Read。不是直接把上传请求交给某个固定厂商API。
- source: [knowledge_create.go:197–262](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_create.go#L197-L262)；[knowledge_process.go:4180–4256](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L4180-L4256)；[reader.Read:4316](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L4316)。
- publisher: Tencent / WeKnora
- pub_date: snapshot 2026-10-15（逐文件修改日未核验）
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code

### W2 默认与可选引擎；自托管服务与厂商API边界
- claim: 未命中知识库规则时采用类型默认。anydoc 已链接且支持该类型时，非 simple/非 PDF 类型优先走进程内 anydoc；PDF 被明确排除，保持 builtin Python docreader 路径。故“所有 Office/PDF 默认 Python解析”与“默认 MinerU/Paddle 云服务”均不准确。
- source: [types default resolution:326–343](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/knowledgebase.go#L326-L343)；[anydoc preference:45–65](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/infrastructure/docparser/engines.go#L45-L65)。
- publisher: Tencent / WeKnora
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code
- default/enabled: anydoc 为有绑定时的条件默认；PDF builtin；显式 parser rule 可覆盖。不是仅凭“引擎已注册”推断启用。
- supported/optional: builtin 是独立 Python docreader；simple 是 Go 进程原生；anydoc 是进程内绑定。mineru 与 paddleocr_vl 是自托管 endpoint；mineru_cloud、paddleocr_vl_cloud 与 weknoracloud 是另外的托管API路径。自托管 MinerU/Paddle 需 endpoint，cloud 路径需各自 credentials；注册不等于配置或调用。
- source for service/API distinction: [engine names:14–31](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/infrastructure/docparser/engines.go#L14-L31)；[availability gates:202–320](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/infrastructure/docparser/engines.go#L202-L320)。

### W3 builtin PDF逐页分类、扫描图和原图引用
- claim: builtin PDF 在 Python使用 pypdfium2，逐页用图像面积及文本信号分类；原生页提取文字并可重建阅读顺序，扫描页输出 JPEG图片引用；原生页也有嵌入图/矢量图提取路径。Python这一步不执行OCR。输出含 markdown、images、source_blocks、页数/扫描页数等 metadata。
- source: [PDF classification:1608–1652](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/parser/pdf_parser.py#L1608-L1652)；[assemble page mapping/result:1709–1770](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/parser/pdf_parser.py#L1709-L1770)；[parser intent:10–16](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/parser/pdf_parser.py#L10-L16)。
- publisher: Tencent / WeKnora
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code
- default/enabled: PDF源码中嵌图提取、版面顺序、标题探测、source boxes默认true；强制全扫描默认false；均可环境配置。仅代表这些功能开关，不能据此保证每个图都被提取或扫描识别成功。
- source for defaults: [PDF option defaults:84–153](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/parser/pdf_parser.py#L84-L153)。

### W4 扫描OCR与图意说明是不同模型任务，且需启用多模态
- claim: 扫描页图片经 Go App多模态任务处理。OCR使用扫描页专用/通用转写提示，实际调用是 vlmModel.Predict；caption 使用另一提示调用 model.Predict。不是固定把扫描OCR交给 PaddleOCR-VL，也不能把 OCR文字当作图意说明。
- source: [separate caption/OCR dispatch:108–122](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/image_action_loop.go#L108-L122)；[OCR prompt and Predict:539–551](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/image_multimodal.go#L539-L551)；[task payload OCR/caption:4445–4461](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L4445-L4461)。
- publisher: Tencent / WeKnora
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code
- default/enabled: processChunks的fan-out由 EnableMultimodel 与 StoredImages控制；该配置来自知识库 VLMConfig。新配置需 Enabled && ModelID非空；兼容旧配置需 ModelName与BaseURL非空。无模型配置时，不能因PDF自动生成扫描页图就断言默认可OCR。启用后payload默认打开 OCR及caption，但ImageAttrsEnabled可触发基于图像属性的OCR决策。
- source for gates/model selection: [multimodal fan-out gate:812–845](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_process.go#L812-L845)；[VLM gate:624–633](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/knowledgebase.go#L624-L633)；[VLM resolver:876–889](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/image_multimodal.go#L876-L889)；[OCR attribute policy:366–376](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/image_multimodal.go#L366-L376)。
- boundary: 模型经 ModelService或legacy配置解析；从这层不能推断最终endpoint必为厂商外部API。PaddleOCR-VL独立解析引擎见W2。模型API可用不等于任意所选模型都支持图片，需验证具体配置。
- drift guard: 不使用 README中“支持OCR/多模态”等概述判定所在进程或默认启用。锁定源码显示 docreader提取文字/图片，Go侧配置模型执行OCR/caption；本轮未固定读取README原文，不声称已经证明某个README版本文字错误。

### W5 引用定位已有数据契约，但“章”不能混同页
- claim: PDF组装时为扫描页和图片生成1-based页定位，原生文本调用 page_blocks产出更细定位；统一 SourceLocator含PDF page/bbox、Word body block、slide、sheet row、EPUB spine section、quote及source hash等。Python source_blocks把 markdown字符范围关联到来源位置。已读源码足以证明定位信息存在，不足以证明任意文档定位都准确或浏览器每种格式回跳都已实测。
- source: [PDF mapping:1709–1740](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/parser/pdf_parser.py#L1709-L1740)；[Python result contract:73–81](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/models/document.py#L73-L81)；[locator contract:9–71](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/types/source_locator.go#L9-L71)；[structural fallback:17–40](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/knowledge_source_locators.go#L17-L40)。
- publisher: Tencent / WeKnora
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high for contract; medium for end-to-end inference; single-source
- class: source-code
- limits: DOCX body block不是Word物理页码；EPUB section是spine条目，不等于语义章节层级。“章节breadcrumbs是否完整保存并用于引用”未核验。扫描页定位只证明页粒度，不能冒称每个OCR段都有精确bbox。

### W6 可复用边界与许可证
- claim: docreader是单独Python gRPC服务，解析类依赖本项目models/config/utils等，依赖声明含pypdfium2、python-docx、pypdf、openpyxl、MarkItDown、OpenDataLoader等；模型OCR/caption、图像持久化、任务fan-in和引用绑定则在Go侧。故抽出PDFParser不自动获得完整入库链。主仓LICENSE写明MIT，但排除列出的第三方组件，不能把所有依赖一概称MIT。
- source: [gRPC main:299–323](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/main.py#L299-L323)；[image persistence boundary:61–67](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/main.py#L61-L67)；[dependencies:7–29](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docreader/pyproject.toml#L7-L29)；[MIT with exceptions:1–32](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/LICENSE#L1-L32)；W4/W5链路。
- publisher: Tencent / WeKnora
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code

## MaxKB findings

### M1 标准上传→分段路由→本地Python库
- claim: 标准DocumentSerializer.Split先校验文件，再逐文件保存原件并生成source_file_id；按split_handles顺序调用support命中的handle。标准PDF handle直接用pypdf.PdfReader：先尝试TOC，再内部链接分段，最后按文字/字体构造Markdown并SplitModel分段。这条已读标准PDF路径没有向MinerU/云解析商发HTTP请求，也未见默认OCR调用。限于这一路径，不能外推“MaxKB全产品没有OCR”。
- source: [registered standard handlers:95–105](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L95-L105)；[save source and route:1255–1284](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1255-L1284)；[PDF parse:51–99](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L51-L99)；[text extraction:174–206](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L174-L206)。
- publisher: 1Panel-dev / MaxKB
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code
- default/enabled: 以上是标准Split路径已注册且按support选择的本地handle；不是README能力列表推断。

### M2 原图与原件保存；TOC分支须单独注意
- claim: 标准PDF无TOC/链接回退分支中，提取page.images，构造File对象并写Markdown图片URL，save_image将bytes存储；上传原件也另行保存。TOC分支在handle_toc成功时提前return，因此不能仅由回退分支证明TOC文件也都保留嵌图。
- source: [PDF early-return branches:75–86](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L75-L86)；[embedded images:141–158](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L141-L158)；[save images/source:1240–1266](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1240-L1266)。
- publisher: 1Panel-dev / MaxKB
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code

### M3 目录分段存在；已读输出没有页/区域引用字段
- claim: PDF TOC分支使用bookmark destination的页与top位置决定章节文字边界，但返回的chapters元素是title/content；已读Paragraph模型含title/content/position/chunks等，未见PDF page/bbox字段。可以说支持按目录组织章节文字，不能把此内部页号计算等同于已保留的页级引用定位。此结论仅限定所读标准PDF输出及Paragraph对象，不推断全产品无定位能力。
- source: [TOC extraction:324–349](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L324-L349)；[TOC output:369–390](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L369-L390)；[Paragraph fields:251–266](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/models/knowledge.py#L251-L266)。
- publisher: 1Panel-dev / MaxKB
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high for inspected fields; medium for downstream limit; single-source
- class: source-code

### M4 产品有图意工作流节点，但不等于标准入库自动图意
- claim: ImageUnderstand工作流节点要求选定/引用/默认的图像模型，构造带image_url或base64图片的消息，再stream/invoke。它证明有可选图像理解执行能力；所读标准PDF路由没有自动调用该节点，因此不能据此声称上传PDF默认生成图意描述。
- source: [model resolve and invoke:135–186](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/flow/step_node/image_understand_step_node/impl/base_image_understand_node.py#L135-L186)；[image messages:272–301](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/application/flow/step_node/image_understand_step_node/impl/base_image_understand_node.py#L272-L301)；M1标准路由。
- publisher: 1Panel-dev / MaxKB
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code
- boundary: 模型provider被配置为本地服务还是外部API，不能从此节点抽象层确定；图意与OCR任务含义须在实际提示和样本中验证。

### M5 复用与许可证
- claim: PDF/Word handles依赖Django翻译、knowledge.models.File与SplitModel；标准路由与存储位于DRF serializer/ORM，不是可直接替换FastAPI worker的独立parser包。主仓LICENSE是GPL version 3。可借鉴TOC切分及图片保存的设计，但复制代码前须单独核对预期分发方式与许可证义务；此处仅报告LICENSE类型，不作法律结论。
- source: [PDF imports:17–25](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/pdf_split_handle.py#L17-L25)；[Word imports:17–25](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/handle/impl/text/doc_split_handle.py#L17-L25)；[standard serializer:1200–1284](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/knowledge/serializers/document.py#L1200-L1284)；[GPLv3 header](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/LICENSE#L1-L6)。
- publisher: 1Panel-dev / MaxKB
- pub_date: snapshot 2026-10-15
- accessed: 2026-10-15
- confidence: high, single-source
- class: source-code

## 对本次决策的有源推断（不是上游性能事实）

- claim: 在约半个月、FastAPI + PG/pgvector、单Python worker、同机4C4GB且模型API可用的约束下，优先借鉴WeKnora的“逐页轻解析→保留原件/原图→可配置OCR与独立caption→带页/结构来源块”的接口设计，并在自己的worker实现最小链路；直接搬完整WeKnora Go管线或MaxKB Django存储/serializer预计会引入额外集成工作。CPU/内存预算与耗时不能由源码推算保证，需用目标机器样本验证。
- source: W1–W6、M1–M5；项目约束仅为决策输入，不作为事实证据。
- publisher: researcher inference
- pub_date: 2026-10-15
- accessed: 2026-10-15
- confidence: medium
- class: inference

## 未知与下一步

1. 两项目均未实测；不承诺OCR准确率、复杂版面顺序、扫描图意题质量或4GB内存可运行上限。下一步用同一组原生PDF、混合扫描PDF、含图文档、跨页表格样本测峰值RSS、耗时、token/费用和失败恢复。
2. 本轮没有证据证明上述默认解析链实现“跨页表格拼接”；单页Markdown/表格提取不能等同于跨页合并。将简单跨页表格作为独立验收样本，保留page_start/page_end及原图方便人工回查。
3. WeKnora Python source_blocks + Go来源绑定的协议可参考，但章节breadcrumbs、每种格式预览器回跳、OCR文本与页/区域的最终绑定未完整跟踪；已证据化的是数据契约、PDF页映射与模型任务携带SourceLocators。
4. MaxKB的插件、企业扩展、其他工作流或用户配置可能具有额外OCR/解析能力，本轮未读，不将标准PDF路径的缺口泛化。
5. 原件保留≠已经验证重处理幂等/事务替换。本轮WeKnora读取到Reparse入口，未审完其完整状态替换；MaxKB标准链保存原件与source_file_id，不据此承诺自动重处理。自建worker必须另行验收parser/model版本、失败重试、旧块替换与原图引用不丢失。
6. 引擎支持/已注册≠环境已安装/服务可用/默认启用；anydoc绑定、docreader连接、各self-hosted endpoint与cloud credentials须各自核对，不将它们归为一个“外部API”。

