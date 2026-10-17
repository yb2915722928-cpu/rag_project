# Story 1.1 当前验收台账

2026-10-17，Asia/Shanghai。当前 Amelia 主控 `01a14973-8555-7131-8fd2-e9eec12f53fe`，实际 `turn_context` 为 `group/auto-gpt-6-1-sol / max`。父 Story 仍 `in-progress`，完成门 `not_passed`；本文件不覆盖历史失败或运行日志。

| 父 AC / 分段 | 当前工件/义务 | 状态 | 通过证据 |
| --- | --- | --- | --- |
| AC1/A1 | 精确3.12.8、正常uv锁、locked同步、Uvicorn进程 | 开发者验证已交付，待独立门 | 正常lock/locked通过；73passed+1条件skip，该负例在3.12.3单跑1passed；实际Uvicorn通过；46/46 hash一致 |
| AC2/A2 | PG18.6、vector0.8.7、六项必跑、迁移循环/namespace/回滚/无生产向量/秘密 | not-executed | 旧补充/静态测试不替代 |
| AC4/B0a | 公共C1/C2模型、正负测试 | 固定a269开发者契约/HTTP/H/金额专题394passed；后续HTTP信封修复需重新发布并回归 | 主控已直接读取服务器JUnit确认394/0/0，保留其原commit；不自动标为修复版通过 |
| AC4/B0b | H流式字节/编码/结构界 | 开发者165passed；Step5独立259passed/0failed/0skipped，含9项取消；全新审查两项已处置 | 同hash源码及桶内日志/JUnit；P2取消补测后关闭，P3抄录已更正，未见可证解析器缺陷 |
| AC4/B0c+B | HTTP维护隔离入口、OpenAPI/JSON Schema/TS与样例 | a269正式生成51工件、--check通过；52样例44passed/8failed/0blocked，当前C2信封缺status，正在本地最小修复 | 主控已读原始generate/check/samples日志，八项均为现有failure_response序列化遗漏，非后续任务缺代码；C仍等待本段修复回归 |
| AC1/C | create-vue、peer锁、页面与真实浏览器/响应式 | C0官方GitHub规范与Node SHASUMS已读；B后实施 | 来源记录有固定版本/规则；工具链工件与页面未生成 |
| AC1+AC3/D | 四服务、digest、Linux构建/启动/停止/重建 | F5–F8均获独立静态修复确认，F8正确DeepSeek接替；真实门未执行 | DockerHub/auth超时、无完整镜像digest，静态改动不能算通过 |
| AC3/E | 来源/许可证/依赖边界/hash/digest/改造 | partial | A1实际38项Linux依赖版本/许可证metadata与文件hash已取，另2项Windows marker；前端/镜像/干净重建未齐 |
| 全Story | 开发者测试 | Linux非PG基线513passed/1条件skip/8PG筛除；真实错误解释器负例另1passed，当前修复待回归 | 主控已直接解析对应JUnit：513/0/0/1与1/0/0/0；runtime专题47passed，2PG筛除；未执行PG不记通过 |
| 全Story | Step5独立验证 | H历史子门已交付；本轮其它运行验证未执行 | 子门独立记录不替代父Story全量 |
| 全Story | 全新6.1 Sol medium独立审查及回归 | 本轮独立静态预审/9项处置完成；全Story正式审查及运行回归未执行 | 静态预审、旧H审查均不替代本轮正式门 |

实现分段只降低上下文，不减少原四AC。`skipped`、unknown、未执行、静态检查和仅子规格完成不放行1.2。真实PG、Linux、浏览器、供应方与目标机分别标源；本Story不提前承担未来外发/目标4C4GB门，也不假称其通过。

2026-10-17用户澄清的测试口径已同步AGENTS：先判断失败是否属于当前Story或必要回归，不要求后续Story未实现功能提前通过。当前52样例内八个HTTP失败归AC4，另八个PG筛除归AC2，均不能转成未来延期；comparison.v1等原计划后续业务不纳当前验收分母。

本轮短规格 `cl100k_base` 实测：A1 1089、D 1108、B0a 1135、B0b 1045，均低于1600风险线。母A规格保留历史并自动拆分。

Amelia续接补充：Windows本机基线 `457 passed / 6 failed / 3 errors / 13 skipped`，临时补丁后 `466 passed / 13 skipped / 1 warning`；没有固定服务器提交或桶内本轮JUnit，不打开正式门。主会话误改worker已交DeepSeek归位，Linux目标不扩大；[归位短规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-worker-reconcile.md:1) 为915 tokens。完整模型/来源/失败边界见 [主控记录](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-amelia-control-2026-10-17.md:1)。
