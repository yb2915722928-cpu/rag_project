# Story 1.1 Git 首次发布范围

## 目的与边界

本文记录首次提交前的建议 allowlist、忽略策略和只读核对结果。此次工作只维护根 `.gitignore` 和本文档，不执行 `git init`、暂存、提交、远端创建、认证或推送，也不删除或移动现有文件。

检查仅基于文件名、路径和 Git 忽略规则，没有读取或输出疑似秘密值。

## 建议首提交 allowlist

首次暂存应显式选择下列项目内容，而不是直接依赖 `git add .`：

| 范围 | 建议 | 说明 |
| --- | --- | --- |
| `.gitignore`、`AGENTS.md` | 纳入 | 仓库卫生规则和项目协作约定 |
| `.agents/skills/**` | 纳入 | 项目内使用的协作技能；提交前仍应确认许可证和来源 |
| `_bmad/**` | 选择性纳入 | 纳入共享配置与脚本；排除 `_bmad/config.user.toml` 和 `_bmad/render/` 生成内容，保留 `_bmad/render/.gitignore` |
| `backend/.python-version`、`backend/pyproject.toml`、`backend/uv.lock` | 纳入 | 精确解释器声明、项目声明和可复现依赖锁 |
| `backend/src/**`、`backend/tests/**`、`backend/migrations/**`、`backend/alembic.ini` | 纳入 | 应用源码、测试和数据库迁移 |
| `backend/.test-runs/.gitignore` | 纳入 | 保留测试证据目录占位；目录中的临时运行输出不纳入 |
| `deploy/.dockerignore`、`deploy/*.Dockerfile`、`deploy/compose.yaml`、`deploy/gateway/**`、`deploy/preflight.py` | 纳入 | 必要部署和运行声明 |
| `deploy/evidence/**` | 选择性纳入 | 当前 Story 的已生成开发/验收证据，包括本轮授权写者新增的两项本地镜像/uv 探测结果；候选身份不等于通过内容级秘密审计 |
| `deploy/offline-images.md` | 选择性纳入 | 已登记的部署交付候选；首次暂存前复核内容和适用环境 |
| `docs/**` | 纳入 | 项目交付和重建文档，包括已登记的前端规范交付 |
| `_bmad-output/implementation-artifacts/**` | 纳入 | 当前规格、Sprint 状态、工作集和验收记录 |
| `_bmad-output/planning-artifacts/**` | 选择性纳入 | 纳入当前决策所需的 PRD、架构、UX、研究结论与证据；重复快照、导入副本和临时 `.memlog.md` 应在首次暂存时逐项复核 |
| `DEVELOPMENT_ISSUES.md`、`OPTIMIZATION_LOG.md` | 纳入 | 项目开发问题与优化证据 |

以下内容不在首次提交范围：

- `INTERVIEW_PREP.md`：个人学习/面试材料。
- `deploy/transfer.zip`：本地代码传输产物，可由已纳入的源码重新产生。
- 虚拟环境、包管理器缓存、Python/Node 构建产物、测试临时输出和渲染输出。
- `.env`、凭据文件、私钥、证书容器、Java keystore、PostgreSQL password file 等本地秘密材料。
- 与项目交付无关的编辑器、操作系统或个人用户状态。

## 忽略策略

根 `.gitignore` 使用分类规则覆盖：

- Python：`.venv`、uv/pytest/mypy/ruff/tox/nox 缓存、字节码、覆盖率和构建输出。
- Node：`node_modules`、npm/pnpm/yarn 缓存、覆盖率和浏览器测试输出。
- 项目生成物：BMad render 内容和 `deploy/transfer.zip`；保留 render 目录的 `.gitignore` 占位。
- 本地配置与秘密：`_bmad/config.user.toml`、`.env*`、凭据、私钥、pgpass 和 keystore；合法的 `.env.example`、`.env.sample`、`.env.template` 及命名为 example/sample 的 PEM/KEY 示例允许版本化。
- 个人与工作站状态：`INTERVIEW_PREP.md`、IDE 配置、交换文件和操作系统元数据。

规则不忽略 `backend/uv.lock`、项目源码、测试、迁移、部署声明、规格或验收证据。

## 只读候选检查

修改前执行了 `git status --short --untracked-files=all` 和文件名分类：

- 仓库没有基线提交，候选均显示为未跟踪文件。
- 修改前共报告 841 个未跟踪候选路径：`.agents` 214、`_bmad` 20、`_bmad-output` 532、`backend` 52、`deploy` 11、`docs` 6、根文件 5，另有 1 条 Git 引号转义路径归入异常根分类。
- 后端候选中确认存在 `.python-version`、`pyproject.toml`、`uv.lock`、源码、测试和迁移。
- 部署候选中确认存在 Compose/Dockerfile、网关配置、预检脚本、开发证据和本地 `transfer.zip`。
- 路径名检查没有发现当前未忽略候选中的 `.env`、pgpass、credential、secret 或私钥命名文件。
- 发现的 `cacert.pem` 只位于已忽略的虚拟环境和 uv 缓存中，不属于候选。

检查期间出现四个并发新增文件，主会话已确认它们来自已登记且授权的唯一写者，不存在未知写者或同文件冲突：

- `deploy/evidence/local-official-image-access.json`
- `deploy/evidence/local-official-uv-manifest-probe.json`
- `deploy/offline-images.md`
- `docs/story-1-1-frontend-standards.md`

最终候选为 843 个路径：`.agents` 214、`_bmad` 19、`_bmad-output` 533、`backend` 52、`deploy` 13、`docs` 8、根文件 4。该结果由修改前 841 个候选，加上四个授权并发交付和本文档，再排除 `_bmad/config.user.toml`、`deploy/transfer.zip`、`INTERVIEW_PREP.md` 三个本地范围文件得到。

上述四个并发交付仅被视为首提交候选，没有因写者已授权而自动通过内容级秘密审计。

以上不是内容级秘密扫描，也不能证明候选文件内容完全不含凭据。首次暂存和推送前仍应使用受信任的秘密扫描器，并人工复核部署证据、用户配置、导入材料和大体量规划快照。

## `git check-ignore` 核对

2026-10-17 对实际文件和代表性路径执行 `git check-ignore -v --no-index`。`git check-ignore -v` 会输出命中的反向规则，因此以最终匹配模式是否以 `!` 开头判定可见性。结果为 22/22 符合预期：

| # | 路径 | 预期 | 实际 | 最终匹配 |
| ---: | --- | --- | --- | --- |
| 1 | `backend/.venv/pyvenv.cfg` | 忽略 | 忽略 | `.gitignore:2:.venv/` |
| 2 | `.uv-cache/example` | 忽略 | 忽略 | `.gitignore:4:.uv-cache/` |
| 3 | `backend/.pytest_cache/example` | 忽略 | 忽略 | `.gitignore:7:.pytest_cache/` |
| 4 | `backend/.test-runs/example/result.json` | 忽略 | 忽略 | `backend/.test-runs/.gitignore:1:*` |
| 5 | `_bmad/render/example.html` | 忽略 | 忽略 | `_bmad/render/.gitignore:1:*` |
| 6 | `_bmad/render/.gitignore` | 可见 | 可见 | `_bmad/render/.gitignore:2:!.gitignore` |
| 7 | `_bmad/config.user.toml` | 忽略 | 忽略 | `.gitignore:32:/_bmad/config.user.toml` |
| 8 | `deploy/transfer.zip` | 忽略 | 忽略 | `.gitignore:33:/deploy/transfer.zip` |
| 9 | `backend/.env` | 忽略 | 忽略 | `.gitignore:36:.env` |
| 10 | `.pgpass` | 忽略 | 忽略 | `.gitignore:41:.pgpass` |
| 11 | `credentials.json` | 忽略 | 忽略 | `.gitignore:43:credentials.json` |
| 12 | `private.key` | 忽略 | 忽略 | `.gitignore:56:*.key` |
| 13 | `backend/.env.example` | 可见 | 可见 | `.gitignore:38:!.env.example` |
| 14 | `example.sample.pem` | 可见 | 可见 | `.gitignore:62:!*.sample.pem` |
| 15 | `INTERVIEW_PREP.md` | 忽略 | 忽略 | `.gitignore:75:/INTERVIEW_PREP.md` |
| 16 | `backend/uv.lock` | 可见 | 可见 | 无忽略规则 |
| 17 | `backend/pyproject.toml` | 可见 | 可见 | 无忽略规则 |
| 18 | `backend/src/rag_app/__init__.py` | 可见 | 可见 | 无忽略规则 |
| 19 | `deploy/compose.yaml` | 可见 | 可见 | 无忽略规则 |
| 20 | `docs/dependency-manifest.md` | 可见 | 可见 | 无忽略规则 |
| 21 | `_bmad-output/implementation-artifacts/spec-1-1-git-hygiene.md` | 可见 | 可见 | 无忽略规则 |
| 22 | `docs/story-1-1-git-publish-scope.md` | 可见 | 可见 | 无忽略规则 |

修改后的候选中没有发现 `.env`、pgpass、credential、secret、PEM、KEY、P12、PFX、JKS 或 keystore 命名文件。此结论仍然只是路径名检查，不替代内容扫描。

本文不声称仓库已经创建、暂存、提交或推送。
