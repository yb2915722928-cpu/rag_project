# 脚本生成的时效检查

输入由 .memlog.md 最新 claim 行派生。refs 1–9 的日期为固定提交的2026-10-15快照日，不冒充逐文件发布日期。源码兼容性1个月、许可6个月。

```json
{
  "today": "2026-10-15",
  "claims": [
    {
      "claim": "[1] 原件先保存，PDF默认builtin；Office条件anydoc；自托管与cloud路径分别配置；官方单一出版者证据，未独立复核/部署实测。",
      "class": "implementation",
      "pub_date": "2026-10-15",
      "recheck": "2026-11-15",
      "stale": false
    },
    {
      "claim": "[2] PDF逐页分类抽文字图片，扫描页输出图；官方单一出版者证据，未独立复核/部署实测。",
      "class": "implementation",
      "pub_date": "2026-10-15",
      "recheck": "2026-11-15",
      "stale": false
    },
    {
      "claim": "[3] Go按多模态配置分别调用VLM执行OCR和caption，不固定PaddleOCR；官方单一出版者证据，未独立复核/部署实测。",
      "class": "implementation",
      "pub_date": "2026-10-15",
      "recheck": "2026-11-15",
      "stale": false
    },
    {
      "claim": "[4] SourceLocator/source_blocks有页与结构来源契约，质量未实测；官方单一出版者证据，未独立复核/部署实测。",
      "class": "implementation",
      "pub_date": "2026-10-15",
      "recheck": "2026-11-15",
      "stale": false
    },
    {
      "claim": "[5] 所读标准PDF使用pypdf和规则分段，未见默认OCR；官方单一出版者证据，未独立复核/部署实测。",
      "class": "implementation",
      "pub_date": "2026-10-15",
      "recheck": "2026-11-15",
      "stale": false
    },
    {
      "claim": "[6] TOC输出title/content，所读输出和Paragraph未见PDF页bbox，嵌图路径有限域；官方单一出版者证据，未独立复核/部署实测。",
      "class": "implementation",
      "pub_date": "2026-10-15",
      "recheck": "2026-11-15",
      "stale": false
    },
    {
      "claim": "[7] 可选图像理解节点不等于标准上传默认图意；官方单一出版者证据，未独立复核/部署实测。",
      "class": "implementation",
      "pub_date": "2026-10-15",
      "recheck": "2026-11-15",
      "stale": false
    },
    {
      "claim": "[8] 主仓MIT有第三方例外，Python parser不含完整Go后处理；官方单一出版者证据，未独立复核/部署实测。",
      "class": "license",
      "pub_date": "2026-10-15",
      "recheck": "2027-04-15",
      "stale": false
    },
    {
      "claim": "[9] 主仓GPLv3，PDF handle耦合Django与ORM/SplitModel；官方单一出版者证据，未独立复核/部署实测。",
      "class": "license",
      "pub_date": "2026-10-15",
      "recheck": "2027-04-15",
      "stale": false
    }
  ],
  "stale_count": 0,
  "earliest_recheck": "2026-11-15",
  "no_window_classes": []
}
```

## 无可核验发布日期

以下refs没有发布日期，明确排除日期计算，不用访问日冒充发布日期，实际接入前重查。

- [10] 轻量PDF库不提供自动OCR和任意语义结构；许可各异；官方单一出版者证据，未独立复核/部署实测。
- [11] RapidOCR有CPU路线，但本期按用户偏好不推进本地OCR；官方单一出版者证据，未独立复核/部署实测。
- [12] 自托管解析有CPU路线和独立选项，许可需分查，共享4GB未知；官方单一出版者证据，未独立复核/部署实测。
- [13] 异步结构解析有页/位置/表格等字段，结果查询窗口24小时；官方单一出版者证据，未独立复核/部署实测。
- [14] OCR与视觉能力分任务；请求/usage/图像处理参数可观察；官方单一出版者证据，未独立复核/部署实测。
- [15] 输入预处理与分段影响OCR；不能据无数据旧实验归因模型；官方单一出版者证据，未独立复核/部署实测。

已知最早复查日由脚本计算：2026-11-15。候选AI能力按3个月、API/库按1个月、OCR质量原则按24个月作刷新窗口；没有原日期时不伪造复查日。
