# Story 1.2 D epoch 启动接线与部署说明

日期：2026-10-18（Asia/Shanghai）。
范围：只补 API/worker 启用已有 epoch 守卫所需的 Compose 接线与运维说明；
不新增 S0 资格报告、探路命令或服务，不改变 1.3/1.4 义务。

## 依据与文件归属

依据 [D 规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-2-d-epoch-deploy.md:1)、
[C4 执行栅栏](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:53)
与原 Story 1.2 AC1。唯一写入两件：

- [compose.yaml](/E:/aaa-project/rag/deploy/compose.yaml:1)。
- [本部署说明](/E:/aaa-project/rag/docs/story-1-2-epoch-deploy.md:1)。

后端 epoch 实现由 A 独占，本段未修改
[epoch_control.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/epoch_control.py:1)、
[runtime.py](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:1)
或其他 A/C 文件；也不修改依赖锁、preflight 与 `.env.example`。

## 接线内容

API 与 worker 的 `environment` 均新增同一项：

```yaml
RAG_EPOCH_CONTROL_FILE: ${RAG_EPOCH_CONTROL_FILE:-/var/lib/rag/epoch/epoch-control.json}
```

两服务已在既有只读 bind mount 中使用同一 `RAG_EPOCH_ROOT`，容器内目标固定为
`/var/lib/rag/epoch`，因此默认控制文件落在该只读挂载内。若运维显式覆盖
`RAG_EPOCH_CONTROL_FILE`，必须保持 API 与 worker 为同一绝对路径；两值不一致
会使 worker 与 API 读到不同控制记录，属于配置错误而非可兼容差异。

本段不改默认 `RAG_EPOCH_ROOT`（仍为 `/opt/rag-story-1-1/epoch`），也不改动
1.1 的容器、目录、数据或镜像。D 实测须用 `RAG_EPOCH_ROOT` 指向 Story 专属
目录（如 `/opt/rag-story-1-2/epoch`），并以独立 Compose project name 隔离。

## 两种运行模式

### 显式首次维护初始化

只在确认该部署从未建立 epoch 控制记录、且迁移已完成后执行一次。复用 A 的
`initialize_epoch_control` 与 `mirror_epoch`，不另写第二份 epoch 逻辑，也不
提供资格 CLI。该动作由宿主机发起，使用与固定提交同源码的后端镜像运行一个
一次性维护容器；不在宿主机 Python 环境中 import 项目代码。

与普通服务共用同一固定提交镜像和 UID `65532:65532`；差别仅在本次一次性
容器把 epoch 挂载为可写并以 stdin 运行维护脚本，普通 Compose 服务定义仍为
只读。维护容器只能访问本 Story 的独占 schema 与秘密文件，不接触 1.1
数据库、资产或锁目录。允许用容器执行这一次性初始化；不因此新增 CLI、
常驻服务或第二份 epoch 逻辑。

```bash
# Story 专属目录；维护窗口临时授予服务 UID 写权限。
install -d -o 65532 -g 65532 -m 0700 /opt/rag-story-1-2/epoch

docker run --rm -i \
  --user 65532:65532 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=8m,mode=1777 \
  --env RAG_DATABASE_URL \
  --env RAG_DATABASE_SCHEMA \
  --env RAG_EPOCH_CONTROL_FILE=/var/lib/rag/epoch/epoch-control.json \
  --env PGPASSFILE=/run/secrets/postgres_pgpass \
  --mount type=bind,src=/opt/rag-story-1-2/epoch,dst=/var/lib/rag/epoch \
  --mount type=bind,src=/path/to/story-1-2/pgpass,dst=/run/secrets/postgres_pgpass,readonly \
  <fixed-commit-backend-image> \
  python - <<'PY'
from rag_app.bootstrap.config import Settings
from rag_app.bootstrap.runtime import build_runtime
from rag_app.adapters.epoch_control import initialize_epoch_control, mirror_epoch

settings = Settings()
value = initialize_epoch_control(
    settings.epoch_control_file, deployment_id="rag-story-1-2",
)
runtime = build_runtime(settings)
try:
    mirror_epoch(runtime.uow, value, schema=settings.database_schema)
finally:
    runtime.close()
PY
```

要求与行为：

- 镜像必须取自固定提交，与随后启动 API/worker 的镜像完全相同。D 的
  canonical 工作目录是 `repo-fixed`，宿主侧构建/检查解释器是
  `venv-fixed`；这次初始化不依赖宿主 Python，也不使用任何草稿虚拟环境。
  固定镜像 ID 以主控发布为准。
- `RAG_DATABASE_URL`、`RAG_DATABASE_SCHEMA`、`PGPASSFILE` 指向本 Story 的
  独占数据库与秘密文件，由宿主环境/秘密文件提供，不写入 argv、输出或本文件。
  三项都必须在宿主环境显式设置，不依赖 `Settings` 的默认 DSN 或默认
  `public` schema；pgpass 文件须对服务 UID `65532` 可读。
- 若 DSN 使用 Compose 服务名（如 `postgres`），维护容器须加入该 Story 的
  Compose 网络，例如 `--network <story-project>_default`；否则使用该 Story
  已验证的可达 PG 端点。不得为初始化向公网发布 PostgreSQL 端口。
- `initialize_epoch_control` 以 `O_EXCL` 创建，文件已存在时拒绝覆盖。重复执行
  不会轮换既有 epoch；应视为维护错误并停止，而不是删除重来。
- `mirror_epoch` 在短 UoW 内写入 `rag_epoch_mirror`；同一记录重复镜像不改变
  业务数据，但正常部署流程不应把它当作启动步骤。
- 初始化成功后立刻恢复普通运行权限，见下节。

### 普通启动与重启

初始化完成后，在宿主机恢复只读、可遍历状态。普通 API/worker 仍通过
`read_only: true` 的 bind mount 读取：

```bash
chown -R 65532:65532 /opt/rag-story-1-2/epoch
chmod 0550 /opt/rag-story-1-2/epoch
chmod 0400 /opt/rag-story-1-2/epoch/epoch-control.json
```

目录 `0550` 只授予属主读/遍历，不授予普通运行写权限；文件 `0400` 只允许
属主读取。API/worker 均以 `65532:65532` 运行，只读取该文件，不在启动、
重启或业务派发中写入或轮换。`deploy/preflight.py` 的目录白名单仍只覆盖
`/opt/rag-story-1-1`，不把该检查当作 D 目录已通过；D 使用等价 `stat`
检查证明上述属主与模式。

普通启动顺序固定为：迁移到 `0002_isolated_calls` → 运行部署前等价权限检查
（见下节）→ 启动 API/worker。worker 在 `run_worker()` 内调用
`runtime.check_database()`，读取控制文件并与 DB 镜像比较；不通过则退出。
API 的 `create_app` lifespan 只调用 `build_runtime`，不做这项启动检查，也
不因此阻止监听。API 侧的受控调用用例（`Runtime.call_lifecycle()` 装配的
`CallLifecycle`）在每次 `prepare`/派发/结果记录时重新读取并核对控制值与
镜像；worker 的业务守护同样如此。当前本段不声称已有产品路由接入了该用例，
只说明接入后的守卫行为。重启不重建、不重写控制值。

## 缺失与矛盾

- worker：`RAG_EPOCH_CONTROL_FILE` 未设置或为空时 `Runtime.control` 为
  `None`，`check_database()` 抛有限 `STARTUP_DEPENDENCY_UNAVAILABLE`，进程
  退出；文件缺失、超界、非法 JSON/字段、服务 UID 不可读，或 DB 镜像缺失/
  不一致时，同样在启动检查中有限失败。
- API：`create_app` 的 lifespan 只构建 `Runtime`，因此 epoch 缺失或不可读
  不阻止 API 监听，`/health` 仍是 liveness。`Runtime.call_lifecycle()` 在
  控制为 `None` 时抛有限 `STARTUP_DEPENDENCY_UNAVAILABLE`；文件缺失、
  超界、非法、服务 UID 不可读或镜像不一致时，`CallLifecycle`
  (`prepare`/`mark_may_have_sent`/`record_result` 等) 经 `GuardError`
  有限拒绝。两类失败都不发出网络请求、不写业务。`/health` 成功不证明
  epoch 已就绪，也不证明调用资格；Compose 的 API healthcheck 同样只证明
  监听与 liveness。
- 两者都不会自动初始化或用 DB 补造控制文件；恢复须由运维按显式维护步骤
  处理。上述失败不写业务、不实际外发。

## 权限与目录约束

- 控制目录必须是本地文件系统上的 Story 专属目录，且位于该部署的
  `RAG_EPOCH_ROOT` 内；不得放在存储桶、临时目录或与资产/锁目录混用。
- 初次维护用 `0700` 目录；进入普通运行前必须恢复 `0550`。文件固定
  `0400`、属主 `65532:65532`。普通 API/worker 只通过只读 bind mount 读取，
  一次性维护容器的可写挂载不进入普通服务定义。
- 代码只读取该文件并核对 DB 镜像，不主动检查目录/文件的完整权限矩阵；
  除“服务 UID 无法读取”会表现为 `check_database()` 或业务守卫有限失败外，
  其他权限偏差（如目录属主不符但仍可遍历、文件为 `0640` 但服务 UID 可读、
  目录含 group 写位等）由部署前
  等价 `stat` 检查证明，不声称 Runtime 会逐项阻断。
- 原 `deploy/preflight.py` 的目录白名单仍硬编码 `/opt/rag-story-1-1`，本段
  未修改它。D 使用 `/opt/rag-story-1-2` 时，应以等价的 `stat` 检查核
  `0550/0400` 与 `65532:65532`，不能把 preflight 对 1.1 根目录的检查冒充为
  对 D 目录的通过。

## 待执行的 Linux 验证（尚未运行）

以下步骤等待主控发布新的干净 `repo-fixed`、固定提交和独占 Netcatty 时段，
当前未执行，不声称通过：

1. 在 Story 专属 Compose project 下对固定提交构建后端镜像；使用独占 schema
   与专属 `RAG_EPOCH_ROOT`，不触碰 1.1 容器或数据。
2. 记录初始化前后的控制文件 SHA-256 与 `rag_epoch_mirror` 值，证明只有首次
   维护步骤创建记录。
3. 启动 API/worker，确认健康后停止并按原镜像重启；核对控制文件 hash 与镜像
   行值不变，证明普通重启不轮换。
4. 新 worker 分别在控制文件缺失、服务 UID 不可读（如属主/权限使 `65532`
   无法打开文件）、DB 镜像被改为不同值时启动，确认有限
   `STARTUP_DEPENDENCY_UNAVAILABLE`、无自动初始化/补造；另以 API 负例证明
   epoch 缺失时 `/health` 仍为 liveness，但业务派发被有限拒绝。目录属主/
   模式偏差另由部署前等价 `stat` 检查留证。
5. 证据（命令、commit、源码 hash、退出码、epoch 前后值、日志）归档到
   `/fileOfRag/testOfRAG/metadata/story-1-2/epoch-deploy`。

不实际调用任何供应方；本段不生成 S0 可外发资格结论，1.5 仍负责完整 S0
汇总与隔离探路工具。

## 未完成

- 本文件与 Compose 改动尚未经过 Linux 启动/重启实测，也没有固定提交。
- 未执行全仓后端套件、PG 生命周期、前端或 gateway 回归；这些不属于本段
  受影响范围。
