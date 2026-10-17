# Q1：应用组织、数据库与访问控制

- 提问者：John
- 回答者：Mary（本问题的 TR、TS 与同题追问保持同一 Mary；闭环后才换新 Mary）
- 日期：2026-10-15
- 方式：bmad-agent-analyst + bmad-deep-recon，headless 原生 run；TR=technical/explore，TS=technical/select。

John 实际提问：

> FastAPI项目怎样组织接口、业务和RAG模块，怎样访问PostgreSQL、管理表结构，并实现Web账号登录、用户绑定的只读API凭证及即时撤权？请先TR说明WeKnora与MaxKB实际怎么做，再TS为本项目作出选择。不要因为参考项目用了某个框架就整套照搬，也不要重定义已确认角色权限。

选择约束（仅作需求，不作外部事实证据）：约半月求职学习项目，AI 编码、用户核对理解；4C4GB Ubuntu 同机 Web/API/DB；API 优先；已确认 FastAPI、PG+pgvector、Vue3/TS/Vite、PG 持久任务和独立 Python worker 串行文档、MinerU 云 API、B0 向量先行。Q1 采用 PRD 第4节、FR1–FR5、FR14 的既定权限，含无自助注册、用户绑定的单空间只读凭证、必设到期、仅创建显示、与当前权限取交集、撤权覆盖检索/输出/历史/下载、平台管理员无隐式资料读权。不增加身份功能或新角色。

范围：仅 Q1 的证据和受托技术选择；不启动后续大问题、不实现代码、不运行产品、不调用收费接口、不修改 PRD 四文件。
