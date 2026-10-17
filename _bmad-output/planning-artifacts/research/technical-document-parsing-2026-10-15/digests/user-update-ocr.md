# 用户新增 OCR 判断的窄范围补证

- 更新：2026-10-15；不扩展候选研究，不做实际 OCR 实验。
- 约束：用户 API 优先；John 本机只读检查报告 i7-12700H、RTX 3060 Laptop GPU 6144MiB。此为项目约束，不作外部技术事实证据。旧实验具体结果待父级证据补充。

| claim | source | publisher | pub_date | accessed | confidence | class |
| --- | --- | --- | --- | --- | --- | --- |
| Tesseract 官方质量说明列出分辨率、二值化、噪声、歪斜、边界和分段等影响输出质量的因素，表格还涉及版面/分段。这里只证明不能一看到低质量输出就只归因模型；不认定旧实验使用 Tesseract。 | [Improving quality](https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html) | Tesseract OCR project | 未标示 | 2026-10-15 | medium, single-source | ocr-quality |
| Qwen-OCR API 有图片 min/max pixels 缩放与旋转等控制，应检查实际传入图而非只看原 PDF。 | [Qwen-OCR API](https://help.aliyun.com/en/model-studio/qwen-vl-ocr-api-reference) | 阿里云 Model Studio | 正文未显示 | 2026-10-15 | medium, single-source | api |

研究者推论：先把文字识别、阅读顺序/表格结构、图示语义分开观察；模型、语言/布局配置和输入处理均保留为待查假设。GPU 型号不是这些假设的排除证据。没有旧图、原始输出与版本配置，不作根因诊断，不给模型好坏排名。
