# Q1 headless research brief

日期：2026-10-15。问题与约束见同目录 question.md。

先 TR（technical/explore）：固定 SHA 的 WeKnora、MaxKB 如何划分 HTTP/业务/RAG，访问 PG 和迁移，处理 Web 登录、API key 和撤销。只读官方源码，缺失明确说明，不把源码推成已部署表现。

再 TS（technical/select）：在既定产品规则下选择最少机制，逐项比较直接替代及代价；优先简单、可解释、Web/API 一致、撤销可验证；不作没有实测支撑的评分、容量或性能结论。

拓扑：窄范围 breadth-first。一个子代理只核验 MaxKB；Mary 核验 WeKnora 与官方 FastAPI/SQLAlchemy/Alembic/OWASP 文档。首轮覆盖即停止，正常置信度；不红队、不市场综述、不工作流编排。

证据边界：项目 PRD 只决定硬门槛；固定源码及本轮官方文档决定技术事实。源码冻结 2026-10-15；动态文档记录访问日，版本锁定留实现时。所有外部判断保存至 evidence.md 与 digests，原始源码仅窄路径存 imports。

输出绑定：answer.md 为给 John 的简短实际答复；evidence.md 为技术证据和未知；research.md 汇总此 run 的决定、来源、时效；.memlog.md 记录过程。全中文 Markdown，不渲染 HTML。
