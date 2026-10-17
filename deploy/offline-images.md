# D：固定提交与官方同版本镜像的离线准备

日期：2026-10-17。状态：`prepared-not-executed`。这是一份可复核的导入准备，不代表镜像已经下载、构建或导入。D 本次返回后释放写入，等待 C/后端入口与主会话重新派发。

## 当前可取得的证据

- 本地 Windows 沙箱外对 Docker Hub registry/auth 的 IPv4 检查分别连接 5 秒超时，原始结果见[本地源访问记录](/E:/aaa-project/rag/deploy/evidence/local-official-image-access.json:1)。本次未重复探测远程 Hub，也未换源、换版或改全局网络/Docker 配置。
- GHCR registry HEAD 返回 405；随后通过官方 GHCR 匿名只读 token 与 manifest API，`ghcr.io/astral-sh/uv:0.12.9` 的 manifest GET 返回 200，响应 digest 为 `sha256:8b940d3a9d65bed080436972241af2e21c84b5e8c9193f7014ed71479ee795ff`。见[去令牌记录](/E:/aaa-project/rag/deploy/evidence/local-official-uv-manifest-probe.json:1)。只核 manifest；尚未取得 linux/amd64 平台 manifest 或镜像层，不能称镜像已可用。0.12.9 是既有工具版本的候选，不借此修改已批准依赖或部署版本。
- Python 3.12.8、Nginx 1.30.6、PostgreSQL 18.6 + pgvector 0.8.7 的官方完整镜像、准确 digest/平台与归档均未取得。GHCR 的 uv 响应不解除其余镜像阻塞。
- Git 当前 HEAD 不存在：`fatal: Needed a single revision`。只对本次只读 Git 命令使用进程级 safe.directory 参数，未修改全局 Git。提交、远端和推送由主会话统一办理。
- 现阶段没有可安全导入的完整镜像包；没有启动本地 Docker Engine、安装工具、构建、推送、上传、导入或清理镜像。

## 来源与版本门

镜像仅接受项目批准的官方发布仓库和准确版本。获取点不得使用第三方镜像站、缓存重打包或同系列其他补丁。Python 候选为官方 `docker.io/library/python:3.12.8-slim-bookworm`，Nginx 为官方 `docker.io/library/nginx:1.30.6-alpine`；PG/pgvector 组合必须从实际官方发布确认精确服务/扩展版本，不凭 `pg18` tag 推定 18.6。uv 从官方 `ghcr.io/astral-sh/uv` 取得，版本由主会话确认后固定。

已读机制的官方依据留给接手者查阅：Docker CLI 的 image save、image load、image inspect、image pull，以及 Docker Compose up 的 `--no-build`/`--pull never`。这些命令说明不证明本环境已经执行成功。当前已有官方源访问阻塞，未为准备本文件另行枚举镜像、访问替代仓库或反复重试。

## 可执行顺序与停止条件

1. 主会话完成本地提交、推送私有 rag_project；服务器只从该仓库拉取同一个完整 commit。GitHub 登录未完成或提交不存在就停止，不把旧传输包当最新源码。所有构建证据记录完整 commit、构建上下文清单/锁与前端工件 SHA-256；提交之后出现新变更须单独记录并重新固定提交。
2. 在已有、获准的 Linux 获取/构建环境操作。当前本地 Windows 不承担应用运行/构建验证，本准备不批准启动或修复本地 Docker、安装额外工具或创建新主机。若现有环境只能访问 manifest、不能取得所有层，就记录该具体失败并停止。
3. 固定并核实官方源、index digest、linux/amd64 平台 manifest digest、实际 image ID、镜像内精确版本及许可证来源。只有这些事实与发布源一致，才创建保存包。不要将 index digest、平台 digest、image ID 或 tar SHA-256 当成同一种 hash。
4. 依赖 C 和后端入口交付后，在同一固定 commit 构建 API/gateway；worker 复用 API 镜像。后端锁必须正常生成并经过 `--locked` 同步。构建还依赖 Python 包/构建依赖与前端产物，只有基础镜像不足以完成干净离线重建；缺少任何工件都保留重建阻塞。
5. 保存最终 API、gateway、PG 三个运行镜像，按 commit 和实际 image ID 绑定清晰本地标签。保存构建基镜像只支持后续重建核验，不能替代最终运行镜像包。导入前审核来源记录与归档 hash，再使用用户既定的工件渠道传递；本任务不新建 SFTP、附件、对象存储或其他上传 transport。代码仍必须通过 Git 固定提交取得。
6. 服务器验证 tar SHA-256 后导入，按平台和实际 image ID 核对三镜像。`docker save/load` 后 RepoDigests 未必完整保留，不把缺失信息补写成官方 digest，也不以归档 hash 冒充 registry digest。
7. 主会话在固定提交下维护经审核的离线 Compose override：gateway/API/worker/PG 的 `image` 指向已核 image ID 所绑定的唯一导入标签，`pull_policy: never`，worker 与 API 必须相同。保留基础 Compose 的权限、secret、挂载和四服务拓扑，不改变业务版本。启动使用 `--no-build --pull never`，缺镜像立即失败；不能由启动过程暗中回网补层或重新构建。override 和 image-ID 映射纳入同次证据。
8. 导入与起服务仍不替代迁移、真实 PG 六项、版本/UID/权限/锁、网关头部/条件请求/私有资产负例、进程停止/重启和干净 Linux 重建。BuildKit 对 digest FROM 仍可能请求 registry；没有真实离线构建证据时不声称 `--pull=false` 已确保离线可重建。

以下命令块是后续获准环境中的命令模板，**本轮均未执行**。变量必须来自审核后的记录，不能填零 digest、虚构 commit 或仅凭 tag 猜版本：

```sh
# 由主会话统一执行 Git 操作；REPO 是既定私有仓库 checkout。
test "$(git -C "$REPO" rev-parse HEAD)" = "$RAG_COMMIT"
git -C "$REPO" diff --exit-code

# 获取点：REF 是已核官方准确版本的 linux/amd64 digest 引用。
docker image pull --platform linux/amd64 "$REF"
docker image inspect "$REF" > "$RECEIPT"
# 导出前记录 inspect 的 Id/Architecture/Os/RepoDigests 与准确版本。
# IMAGE_TAGS 是固定 commit 对应的最终 API、gateway、PG 导出标签集合。
docker image save --output "$ARCHIVE" $IMAGE_TAGS
sha256sum "$ARCHIVE"

# 服务器：先从经审核记录设置 EXPECTED_ARCHIVE_SHA256/ARCHIVE。
printf '%s  %s\n' "$EXPECTED_ARCHIVE_SHA256" "$ARCHIVE" | sha256sum --check -
docker image load --input "$ARCHIVE"
# 然后逐一核 image inspect 实际 Id == 同 commit 的审核记录，不匹配即停止。
docker compose -f deploy/compose.yaml -f "$OFFLINE_OVERRIDE" config --quiet
# 依基础流程先 PG、再单一迁移，再开放 API/worker/gateway。
docker compose -f deploy/compose.yaml -f "$OFFLINE_OVERRIDE" up -d --no-build --pull never postgres
```

不执行全局 prune、down -v、镜像替换或存储目录删除。当前所有完整镜像/归档、固定 Git commit、离线 override 运行验证和干净重建保持 `not-obtained/not-executed`；复核触发为真实工件交付、网络环境变化或明确新授权。
