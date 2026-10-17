# Story 1.1 A2a/B0a/B0c Linux 开发者运行门交付记录

日期：2026-10-17（Asia/Shanghai）。规格：
[spec-1-1-linux-developer-gates.md](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-linux-developer-gates.md:1)。

状态：**开发者门未闭合**。固定提交的 Linux 非 PG 回归、B0a/B0c 专题、正式生成与
`--check` 已通过；52 条样例 44 通过、8 失败，根因已定位并完成本地最小修复，
等待主控发布新提交后回归。父 Story、PG、四服务、独立验证与审查门槛均未移动。

## 环境与固定提交

| 项目 | 实测值 |
| --- | --- |
| 主机 | `120.53.251.166`，Linux 6.8.0-124-generic x86_64 |
| 会话 | Netcatty `1eaffce6-3c45-45cb-84bd-18bd6fc84ea9`（本任务独占） |
| 运行基线 | Gitee `main` = `a269d492fb33b3b13d95265fa11589d39260c4e0` |
| 检出 | `/opt/rag-story-1-1/repo`（detached，工作树干净） |
| 运行目录 | `/opt/rag-story-1-1/linux-developer-gates-work`（`/dev/vda2` ext4） |
| 解释器 | `/root/.local/share/uv/python/cpython-3.12.8-linux-x86_64-gnu` → venv 3.12.8 CPython |
| uv / Uvicorn / pytest | 0.13.1 / 0.37.0 / 8.4.2 |
| 宿主系统 Python | 3.12.3（仅用于真实错误解释器负例） |

锁与声明 hash（与本地一致）：

| 文件 | SHA-256 |
| --- | --- |
| `backend/pyproject.toml` | `1b5a7ecb3e0036e3d96a8548a4fa729c95901fcd38dfa9ed63fb7b15e6c34c1c` |
| `backend/uv.lock` | `7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed` |
| `backend/.python-version` | `db3ef967a80f30770e652243d4e8292c73ee214e182ada70ce045e91aab40fa7` |

源码绑定：`git ls-tree -r` 的 `backend`/`contracts` tree 与 `sha256sum` 全量清单各 102 项，
同一基线提交下逐项一致；`0b576b65d3824e7f4319c39c38e80398caf08fb8` 仅为文档增量，
`backend`/`contracts` tree hash 与 `a269d49` 相同（`55aabf35…`、`99041bab…`）。

## 已执行命令与计数

全部在固定提交 + 精确 CPython 3.12.8 上执行，原始日志与 JUnit 位于
`/opt/rag-story-1-1/linux-developer-gates-work/evidence/a269d49/`。

| 检查 | 命令 | 计数 | 退出码 |
| --- | --- | --- | --- |
| 锁一致性 | `uv lock --check --python 3.12.8` | 41 解析 | 0 |
| 锁同步 | `uv sync --locked --python 3.12.8` | 39 安装 | 0 |
| 非 PG 全量 | `pytest -m 'not postgres'` | 513 passed / 1 skipped / 8 deselected（收集 522） | 0 |
| 非目标解释器负例 | 3.12.3 + `PYTHONPATH` 运行单例 | 1 passed | 0 |
| B0a/B0c 专题 | `pytest test_public_contracts test_contract_http test_json_guard test_decimal_wire_zero` | 394 passed | 0 |
| runtime 专题 | `pytest test_runtime_entrypoints test_uvicorn_process -m 'not postgres'` | 47 passed / 2 deselected | 0 |
| 正式生成 | `contracts/generate.py` | 51 个文件 | 0 |
| 生成一致性 | `contracts/generate.py --check` | 51 个文件一致 | 0 |
| 52 条样例 | `contracts/verify_samples.py` | **44 passed / 8 failed / 0 blocked** | 1 |

分母说明：唯一 skip 是“仅适用于非目标解释器”的负例，已用真实 3.12.3 单独执行为
1 passed，不计入 Linux 通过；8 条 PG 标记（6 项 PG 集成 + 2 项 worker PG 参数化）
保持未执行，不能由条件筛除记为通过。

## 52 条样例的 8 项失败与根因

失败项全部为 HTTP 失败路径：
`h.http.reject.unauthenticated`、`unknown-field`、`nested-unknown-field`、
`media-type`、`content-encoding`、`headers-over`、`body-over-1mib`、`duplicate-key`，
统一报 `private HTTP response lacks status`。其余 44 条（C1 标量/序列化、C2 202/失败/
GET 投影、H 解析边界、no-store 与 request_id 轮换）通过。

根因（主控已独立读取确认）：`failure_response()` 构造 `FailedResponse` 时未显式设置
`status`，该字段有模型默认值且非必填，随后 `exclude_unset=True` 序列化将其抹掉，
与共享契约 C2“每次响应必须含 `schema_version`/`request_id`/`status`”冲突。
属实现缺陷，不是样例或模型定义问题。

同一缺陷的同类残留：探针成功回显同样用 `exclude_unset=True`，客户端合法省略带默认值的
`schema_version`/`status` 时，200/202 响应会缺少 C2 信封字段。主控裁决按同一 AC 闭合，
选择“合法输入经原模型验证后，输出始终补齐这三个信封字段”。

## 本地修复（冻结，等待主控发布）

仅改原认领的两个文件，未新增拒绝规则、未改 17 个 DTO、未改输入默认值或缺省/显式 null
语义，其余字段继续 `exclude_unset`：

1. [contract_probe.py](/E:/aaa-project/rag/backend/src/rag_app/entrypoints/contract_probe.py:26)：
   失败信封显式传 `status=Status.FAILED`；探针成功路径在 `exclude_unset` 结果上仅补齐
   `schema_version`/`request_id`/`status` 三个字段。
2. [test_contract_http.py](/E:/aaa-project/rag/backend/tests/test_contract_http.py:117)：
   `assert_failure` 先检查 wire 三元组与 `status='failed'`，再 `model_validate`；
   新增合法输入省略默认信封字段时对 Accepted/Completed/Retrieval/Operation/Failed
   五种响应的 wire 断言（`set(body)` 必须等于提交键并集三元组），并验证未补齐字段
   （`retry_mode`、`operation_id`）仍按原语义缺省。

| 文件 | 字节 | SHA-256（冻结） |
| --- | --- | --- |
| `backend/src/rag_app/entrypoints/contract_probe.py` | 8675 | `079a9952c487cada067b30ba70ad08f64e20dd93d4a2fce84997b870564dc545` |
| `backend/tests/test_contract_http.py` | 24218 | `f3929ae78d4d240403224b429b00619976a9077909ac13b28c526c88f6817526` |

本地仅做 `ast.parse` 语法检查与 `git diff` 审阅，未执行测试；Windows 结果不作为证据。

## 未执行与风险

- `not-executed`：修复后的 Linux 回归、样例 52/52、正式工件重建与归档。
- `not-executed`：真实 PostgreSQL 18.6 / pgvector 0.8.7 八项、迁移循环、四服务生命周期
  与干净重建、完整镜像/digest、浏览器与目标部署环境。
- `not-executed`：Step 5 独立运行验证、全新 `GPT-6.1 Sol / medium` 独立审查及修复回归。
- 注意：`contracts/generate.py` 的 `manifest.json` 记录 `contract_probe.py` 的源文件 hash；
  修复后必须在固定提交上重新生成，旧工件不再对应新源码。
- 风险：JSON Schema 不能表达 Pydantic 跨字段校验；运行时权威仍是后端模型。
- 风险：探针路径在 OpenAPI 中可见，生产网关必须阻断，部署侧尚未验证。

本记录不把开发者测试当独立验证，也不改变父 Story 的验收分母。
