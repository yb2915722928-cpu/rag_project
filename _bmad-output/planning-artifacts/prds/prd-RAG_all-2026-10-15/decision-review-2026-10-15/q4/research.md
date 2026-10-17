---
type: technical
topic: Q4 页面文件部署运行
decision: TR 后 TS，适配 4C4GB 的简化交付运行方案
source: fixed-source-and-official-docs
status: complete
updated: 2026-10-15
verification_scope: first-round-primary-source-only
---

# Q4 研究交付索引

推荐自建薄 Vue 前端，电脑构建，服务器用 Nginx／API／worker／PG 四服务；文件与静态产物隔离，后端实时鉴权；服务密钥可恢复加密而程序 key 只存 hash；停写备份对齐 DB、文件、配置和密钥恢复。初值、12份测试起点及四项验证均是计划，未作服务器或收费调用。完整 TR→TS 与来源推导已分别落盘，避免重复一份长报告。

- [John原问题](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/question.md:1)
- [TR→TS回答](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/answer.md:1)
- [证据与设计细节](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/evidence.md:1)
- [研究简报](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/brief.md:1)

WeKnora 的静态运行阶段、受控下载及可配置运行日志支持边界式借鉴。[1] MaxKB 的前端、开发文件代理、部署标识与日志目录支持交互和发布参照，但存储后端及完整日志链路本轮未证。[2] Nginx 静态代理／HTTPS、Compose secret／运行约束和 PG dump 的直接机制支持本项目部署与恢复方案。[3][4][5] 这些均是单一官方原始来源，置信度 medium；未将源码声明说成已验证容量。

最强代价是自写业务交互及部署维护、停写恢复窗口、单机资源余量有限。可逆边界是静态产物／HTTP、文件服务接口、镜像与配置版本及可恢复备份；未来只有真实负载失败才重选存储、队列或监控，当前不添加整套产品。

## 来源附录

| ref | 支持范围 | 发布者及来源 | 发布日期 | 访问日期 | 置信度 |
|---|---|---|---|---|---|
| [1] | 前端、文件、运行日志 | [Tencent/WeKnora固定提交](https://github.com/Tencent/WeKnora/tree/a37a1bc51ad85d096df341f6d3a098f60d586f52)；具体文件见证据 | commit日期未核 | 2026-10-15 | medium，单源 |
| [2] | 前端、开发代理、部署记录 | [1Panel-dev/MaxKB固定提交](https://github.com/1Panel-dev/MaxKB/tree/0fa9a0dae8850c1878f087f0d81c974c1d424b06)；具体文件见证据 | 未标 | 2026-10-15 | medium，单源 |
| [3] | 静态代理、HTTPS | [NGINX指南](https://nginx.org/en/docs/beginners_guide.html)、[HTTPS](https://nginx.org/en/docs/http/configuring_https_servers.html) | 未标 | 2026-10-15 | medium，单源 |
| [4] | secret与运行约束 | Docker Inc.：[secrets](https://docs.docker.com/compose/how-tos/use-secrets/)、[services](https://docs.docker.com/reference/compose-file/services/) | 未标 | 2026-10-15 | medium，单源 |
| [5] | DB快照与全局角色边界 | [PostgreSQL Global Development Group](https://www.postgresql.org/docs/17/backup-dump.html) | 未标 | 2026-10-15 | medium，单源 |

## 未知、重核与停止条件

真实容量、费用、上游限额及证书条件留给接入／首基线，当前 user_only_missing=无。固定提交作为历史参照不会自行变更；真正复用时重核目标文件与第三方许可证。指南发布日期未标，不能编造日历失效日；首次部署接入时重读相关版本文档并验证运行效果。用户要求首轮足够即收敛，本轮不执行额外评分或评审，不生成HTML。
