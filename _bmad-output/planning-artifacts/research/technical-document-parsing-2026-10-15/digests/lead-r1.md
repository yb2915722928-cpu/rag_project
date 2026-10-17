# Mary：API 边界与校核补证（r1）

本轮来源；访问日 2026-10-15。项目需求只形成待验证项，不作为技术事实。

| claim | source | publisher | pub_date | accessed | confidence | class |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen-OCR 是接收图像的模型 API，可输出文字/结构化信息；API 响应提供请求 id、模型、输入/输出/图像 token 用量和截断状态。可记录每次调用，但这些字段本身不等于账单。 | [Qwen-OCR API reference](https://help.aliyun.com/en/model-studio/qwen-vl-ocr-api-reference)，Response、Built-in tasks | 阿里云 | 页面检索元数据更新 2026-09-01；正文抓取未显示时间 | 2026-10-15 | medium, single-source | API-contract |
| 阿里云将图像/视频理解与 OCR 文字提取分别列为能力；当前视觉模型页更新频繁。因此需求应分别配置问答、向量、OCR、视觉能力，不用普通文本问答模型名代替视觉能力验证。后一句为设计推论，不是厂商能力保证。 | [视觉理解](https://help.aliyun.com/zh/model-studio/vision-model/) | 阿里云 | 未标注 | 2026-10-15 | medium, single-source | API-capability |
| WeKnora 当前官方说明 docreader 输出 Markdown 与原始图片，Go App 做分块、存储、OCR、caption；builtin PDF 使用 pypdfium2 逐页路由，外部引擎是可选替换。尚待 TR 以固定 commit 源码核实。 | [文档解析官方文档](https://github.com/Tencent/WeKnora/blob/main/website-docs/03-features/03-document-parsing.md)；[docreader README](https://github.com/Tencent/WeKnora/blob/main/docreader/README.md) | Tencent/WeKnora | main，可变 | 2026-10-15 | medium, single-publisher，待源码核实 | implementation |

## 设计推论与待验证观察

- 把解析产物绑定原文件 hash、页索引、章节路径、区域（能取到才存）、原图键、解析器/模型版本、attempt、人工修订版本；无精确定位不得伪造页引用。
- 保留 API 原始响应与本地抽取结果，按页/任务分账，记录重试与缓存命中；本轮不推算价格。
- 混合 PDF 必须逐页判断和人工抽样，低质量隐藏文字层不能当然算成功；表格的数值/单位必须与原图核对。
- 没有证据证明任意手册跨页表格可自动恢复，也没有证据证明某轻量 OCR 在当前 4GB 混合负载下满足质量和时延。

## 未找到/未做

- MaxKB 官方文档入口抓取超时，由 TR 以官方源码核对补足。
- 未调用收费 API，未拿到实际账单，未运行 OCR/视觉质量实验。
