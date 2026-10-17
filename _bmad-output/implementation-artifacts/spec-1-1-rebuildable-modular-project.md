---
title: 'Story 1.1 建立可重建的后端与真实 PG 基线'
type: 'feature'
created: '2026-10-17'
status: done
route: 'dispatch'
review_loop_iteration: 2
baseline_commit: 'NO_VCS'
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md'
completion_record: E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 工作区只有规划材料，没有后端和真实 PostgreSQL 基线；后续 Story 无法在统一模块边界和事务行为上开发。

**Approach:** 建立 Python 模块化单体的八模块目录、同步短 UoW、最小真实 PostgreSQL/pgvector 迁移入口和事务回滚测试，锁定后端依赖。前端、四服务 Compose、完整 contracts 和 provenance 延期。

## Boundaries & Constraints

**Always:** API/worker 共用 application；领域只依赖模型与端口；仓储不 commit；PG 是唯一持久库；锁定 FastAPI/Pydantic/SQLAlchemy/psycopg/Alembic/HTTPX 及传递依赖；日志不含秘密或正文；失败不伪造成功。

**Never:** 不使用 SQLite/第二数据库，不引入队列或真实供应方；不预建后续业务表，不创建正式 `vector(D)`/ANN 索引；不实现前端、Compose、完整 contracts 导出或 provenance 审计台账。

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|-----------------------------|----------------|
| ROLLBACK | 真实 PG、短 UoW、注入异常 | 事务回滚后无半写入，仓储不提交 | 有限错误，日志仅保留安全元数据 |
| EXTENSION | pgvector 扩展、隔离测试向量 | 可核 PG/扩展版本和测试向量，不建立生产向量空间 | 版本/迁移失败即停止 |

</frozen-after-approval>

## Code Map

- 当前没有应用源码、锁文件或 Git 历史；从空结构开始。
- `_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ARCHITECTURE-SPINE.md` -- 八模块、依赖方向、后端版本和目录结构。
- `_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md` -- C1/C2 的公共数据和错误边界；本轮只建立 contracts 所在边界，不交完整导出。
- `_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md` -- 后端和 PostgreSQL/pgvector 版本 seed。
- `_bmad-output/implementation-artifacts/deferred-work.md` -- 延期的前端、Compose、contracts 和 provenance 交付。

## Tasks & Acceptance

本文件为保留审查历史的 A 段母记录，超过风险线后已自动拆分；当前可执行 A1 规格为 [spec-1-1-python-3128.md](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-python-3128.md:1)。2026-10-17 用户明确改为精确 CPython 3.12.8、远程 Linux 执行，优先于本文件历史 3.12.15 描述。A2 仍承接全部真实 PG 与迁移/namespace 义务，B/C/D/E 不减少；原审查证据保持原样。

**Execution:**
- [x] `backend/pyproject.toml`, `backend/uv.lock` -- 按 A1 创建精确 Python 3.12.8 后端和可重复锁文件。
- [x] `backend/src/rag_app/` -- 创建 contracts/application/modules/adapters/entrypoints/bootstrap 与八模块最小边界，提供健康检查、配置装配和短 UoW 示例。
- [x] `backend/migrations/`, `backend/tests/` -- 添加最小迁移、真实 PG/pgvector 扩展检查、隔离测试向量、up/down 和回滚/仓储不 commit/日志保密测试。
- [x] `docs/rebuild-evidence.md` -- 记录本轮后端依赖、迁移和真实 PG 测试证据；未执行项为 `not-executed`。

**Acceptance Criteria:**
- Given 空项目与技术 seed，when 安装锁定后端依赖并运行测试，then 后端模块可导入、短 UoW 可执行、领域不导入框架/ORM。
- Given 真实 PostgreSQL/pgvector，when 执行迁移、回滚并注入事务异常，then 扩展/迁移版本可核、失败无半写入，普通业务代码不依赖 SQLite。
- Given embedding 维度尚未测得，when 检查数据库结构和隔离向量测试，then 不创建正式 `vector(D)` 或 ANN 索引。
- Given 配置错误或测试秘密，when 检查错误和普通日志，then 不输出秘密、正文、完整提示、签名 URL 或上游原始 body。

## Implementation Notes

- Intent gaps: 无；具体表名和测试夹具属于实现细节。
- Irreversibles: 首次 PG schema/extension 迁移和锁文件；不兼容必须停止并保留证据。
- Footprint: 新建 `backend/`、`docs/`；后续 Story 依赖后端装配根和迁移入口。
- 运行门：真实 PG/Linux/浏览器/供应方/目标机验收仍为 `not-executed`。

- 2026-10-17 主会话纠正提前勾选：本文件是获批的后端子规格，不代替原 Story 1.1 的完整 AC；所有拆分项仍归原 Story。目标解释器/锁、真实 PG 和二次 schema 修复尚未验收，状态回到 in-progress。原冻结块保持不变。
- 主会话仅维护规则、规格、证据和验收；旧 Pascal、Sagan、Harvey 为历史轮次角色。当前实际实现认领以 relay state 为准；当前后端 Jason，6.1 Sol/medium。旧独立审查不替代本轮所需全新独立审查与独立验证。

## Spec Change Log

- R1：实际审查确认版本验证、共享扩展所有权、隔离测试、日志保密和配置装配缺口。按现有冻结 AC 细化修复要求并交回原实现者；保留八模块、单一 UoW、无正式 vector(D)、PG-only 和安全元数据。NO_VCS 下保留完整快照，不破坏性回退用户/其他会话文件。当前项目规则要求原开发者修复，优先于技能的重新实现默认步骤。
- R2：新增 namespace 回退与同名 DROP TABLE 风险。应用表/revision 与迁移 DDL 必须绑定同一目标 schema，缺失/失权/结构漂移时明确失败；增加其他 namespace 同名对象不受影响的负例。KEEP：扩展保留、精确版本、有限错误、资源清理、必跑 PG 门禁。目标解释器和真实 PG 缺口不得靠 mock 或修改版本消除。

## Review Triage Log

原始只读审查使用 r1 统一 diff；R2 使用 story-1-1-review-r2.diff。下表逐项保留，重复项不省略；实施与运行验收是不同状态。

| ID | 裁决 | 核实依据与分流 |
| --- | --- | --- |
| H01 | medium | r1 downgrade 无条件 DROP EXTENSION，确会删除非本迁移所有的共享扩展；bad_spec，原实现者修复，R2静态复核关闭，真实PG待验。 |
| H02 | medium | r1 仅 assert extension 非空，缺服务/扩展精确版本；bad_spec，新增预检和负例，真实PG待验。 |
| H03 | medium | r1 测试不调用 Alembic；bad_spec，新增迁移循环/revision测试，未运行不能关闭验收。 |
| H04 | medium | r1 all([]) 可通过且只查probe；bad_spec，新增明确列集合及整个目标schema向量/ANN检查。 |
| H05 | high | r1 预先提交删除固定9001，误配可毁已有数据；bad_spec，改独占schema与显式授权，R2另核namespace。 |
| H06 | medium | r1 健康响应断言没有捕获日志；bad_spec，新增配置/HTTP/CLI哨兵及待执行真实驱动测试。 |
| H07 | medium | r1 create_engine 未hide参数、原始SQL异常直传；bad_spec，有限SafeError与参数隐藏，不外序列化内部诊断。 |
| H08 | medium | r1 任意URL可创建SQLite引擎；bad_spec，PG+psycopg白名单及负例。 |
| H09 | medium | r1 Settings 未接入 create_app；bad_spec，共享bootstrap/lifespan/worker已补，R2 namespace待修。 |
| H10 | medium | r1 范围声明不锁3.12.15；目标已精确声明，但uv.lock仍旧，环境与重建门未关闭。 |
| H11 | medium | r1 无commit/rollback/close故障测试；bad_spec，已新增故障矩阵与资源清理测试，真实提交不确定性明确保留。 |
| H12 | medium | 延期项无承接/门槛，可能丢原AC；主会话补父Story交付矩阵和归属，不能把文档修改当代码验收。 |
| E01 | medium | 同H01，原扩展可被删除；随共享扩展修复，真实PG待验。 |
| E02 | medium | 同H04，空列集合真通过；随结构断言修复。 |
| E03 | high | 同H05，固定9001已提交删除不可回滚；随隔离测试修复。 |
| E04 | medium | 同H07，异常可含正文；随SafeError/日志保密修复。 |
| E05 | medium | 同H10，精确解释器完成声明无证据；撤销完成勾选，保留目标阻塞。 |
| E06 | medium | 同H03/H06，up/down和日志/仓储测试缺失；已补测试，运行证据按环境分列。 |
| V01 | medium | 普通pytest成功但PG全skip不保护必需验收；bad_spec，新增--require-postgres收集/通过/skip门，���实PG仍未过。 |
| V02 | medium | 无迁移执行，空库重建/降级无保护；bad_spec，迁移循环已写，运行未执行。 |
| V03 | medium | 扩展非空不证明批准基线；bad_spec，精确版本预检/负例已补。 |
| V04 | medium | probe-only和空结果不能证明全schema无向量/ANN；bad_spec，目标schema全量断言已补。 |
| V05 | medium | 无配置/事务错误日志观测；bad_spec，新增哨兵断言，真实驱动未执行。 |
| I01 | medium | 独立审查确认版本缺口；同H02修复，真实环境未关闭。 |
| I02 | medium | 独立审查确认删除共享扩展；同H01修复。 |
| I03 | medium | 独立审查确认没有迁移循环；同H03修复，等待运行。 |
| I04 | medium | 独立审查确认日志安全断言缺失；同H06修复，真实驱动待验。 |
| R2-01 | medium | search_path目标,public与未限定表使目标缺失/未迁移仍读public；bad_spec，已交原开发者定点修复。 |
| R2-02 | high | 目标probe丢失时未限定DROP可能删除public同名对象；bad_spec，要求显式schema及漂移负例，未关闭。 |
| R2-03 | medium | pyproject固定3.12.15并新增uvicorn，uv.lock仍旧；重建门未关闭，不手改锁或静默换解释器。 |

## Verification

**Commands:**
- `uv lock --project backend` -- expected: SUCCESS，锁文件可复现。
- `uv run --project backend pytest backend/tests -q` -- expected: SUCCESS，事务、扩展边界和 import 规则通过。
- `alembic upgrade head` 与 downgrade/rollback fixture -- expected: SUCCESS，真实 PG/pgvector 迁移与回滚证据存在。

**Manual checks (if no CLI):**
- 核对 `SHOW server_version`、`CREATE EXTENSION vector`、迁移历史和数据库结构；确认无正式 `vector(D)`。
