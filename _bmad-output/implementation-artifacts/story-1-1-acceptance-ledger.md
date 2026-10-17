# Story 1.1 当前验收台账

2026-10-17，Asia/Shanghai。主控 `01a148e2-1e11-7322-9626-6cbafb956f12`，实际 `turn_context` 为 `group/auto-gpt-6-1-sol / max`。父 Story 仍 `in-progress`，完成门 `not_passed`；本文件不覆盖历史失败或运行日志。

| 父 AC / 分段 | 当前工件/义务 | 状态 | 通过证据 |
| --- | --- | --- | --- |
| AC1/A1 | 精确3.12.8、正常uv锁、locked同步、Uvicorn进程 | 开发者验证已交付，待独立门 | 正常lock/locked通过；73passed+1条件skip，该负例在3.12.3单跑1passed；实际Uvicorn通过；46/46 hash一致 |
| AC2/A2 | PG18.6、vector0.8.7、六项必跑、迁移循环/namespace/回滚/无生产向量/秘密 | not-executed | 旧补充/静态测试不替代 |
| AC4/B0a | 公共C1/C2模型、正负测试 | 本地修复/有限policy已冻结，待Git同步与开发者测试 | 仅静态核对与hash，不记运行通过 |
| AC4/B0b | H流式字节/编码/结构界 | 开发者165passed；Step5独立259passed/0failed/0skipped，含9项取消；全新审查两项已处置 | 同hash源码及桶内日志/JUnit；P2取消补测后关闭，P3抄录已更正，未见可证解析器缺陷 |
| AC4/B0c+B | HTTP维护隔离入口、OpenAPI/JSON Schema/TS与样例 | HTTP本地冻结/运行未执行；正式B导出未开始 | Git推送缺认证阻塞，不改用被拒SFTP |
| AC1/C | create-vue、peer锁、页面与真实浏览器/响应式 | C0官方GitHub规范与Node SHASUMS已读；B后实施 | 来源记录有固定版本/规则；工具链工件与页面未生成 |
| AC1+AC3/D | 四服务、digest、Linux构建/启动/停止/重建 | 初稿；远程源可达性待作者核实 | 首轮失败保留，不能算通过 |
| AC3/E | 来源/许可证/依赖边界/hash/digest/改造 | partial | A1实际38项Linux依赖版本/许可证metadata与文件hash已取，另2项Windows marker；前端/镜像/干净重建未齐 |
| 全Story | 开发者测试 | 未全部交付 | 无全量本轮通过证据 |
| 全Story | Step5独立验证 | H子门已派发，其他未派发 | 子门独立记录不替代父Story全量 |
| 全Story | 全新6.1 Sol medium独立审查及回归 | H子门已派发，其他未派发 | 历史审查不替代本轮 |

实现分段只降低上下文，不减少原四AC。`skipped`、unknown、未执行、静态检查和仅子规格完成不放行1.2。真实PG、Linux、浏览器、供应方与目标机分别标源；本Story不提前承担未来外发/目标4C4GB门，也不假称其通过。

本轮短规格 `cl100k_base` 实测：A1 1089、D 1108、B0a 1135、B0b 1045，均低于1600风险线。母A规格保留历史并自动拆分。
