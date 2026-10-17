# budget-r1：文件优先技术摘要

decision：选择能把协议输入、embedding、完整生成输入／输出和失败账统一起来的预算策略。accessed：2026-10-16，Asia/Shanghai。source_craft：官方文档＋两个固定提交，静态源码不冒充运行成绩；项目资料仅提供边界。

| claim | source / publisher | pub_date / accessed | confidence / class |
|---|---|---|---|
| 两个独立项目的所读路径均把历史、当前提示与生成参数分开处理，字符或轮数控制本身不足以证明模型总预算 | WeKnora common.go 35–101、119–190；MaxKB base_generate_human_message_step.py 22–71；固定 SHA / Tencent、1Panel-dev | 固定提交日期未取到（GitHub commits API 403 rate limit）；2026-10-16 | high 仅限共同静态观察，独立路径互证 / pattern |
| token 由所用 tokenizer 决定，真实用量以 API usage 为准；模型有输入输出限制 | 阿里云模型用量页，见 evidence A1 / Alibaba Cloud | 动态页更新时间未显示；2026-10-16 | medium, unverified 独立发布者未核 / compatibility |
| 输出参数对答案／思考口径按接口／型号区分，length 为过长停止，结构输出支持也按型号 | 阿里云 DashScope API，见 evidence A2 / Alibaba Cloud | 动态页；2026-10-16 | medium, unverified / compatibility |
| embedding 每条／批条数依型号而异，query/document 有独立用途字段 | 阿里云同步 embedding API，见 evidence A3 / Alibaba Cloud | 动态页；2026-10-16 | medium, unverified / compatibility |

来源链接／固定 SHA／精确行号在同目录 evidence.md；原始源码副本在 source-snapshots。先前 GitHub blob/raw 的 web 工具读取失败，随后 urllib 官方 raw GET 成功；不是用旧会话证据代替本轮访问。只保留决定性来源，不追加综述或价格。

TS 派生设计（不是上游事实）：选 B；H/B/M 三层，基础本体和输出预算早检；逐输入／批次计数；未知 fail closed；compact-128 子契约；先旧历史再五块逆序原子组裁剪；catalog/SM2只认实见；length和缺格整答失败；免费纯检索也过全局gate／真实调用账。理由是完整性与可审计硬门，不宣称源码已经实现本项目不变量。

停止原因：覆盖本题决定性接口与反例，进一步全仓／型号扫描不会替代实际账号接入验证。没有运行 token 计数、模型调用、4×6生成、真实并发或SM测试。待 P0：选定用途型号、锁适配器并证明计数上界、验证完整结构和长度错误、冻结真实生效配置；这些沿既有验收，不增产品范围。
