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

> 2026-10-17 来源裁决修订：上句“不得使用第三方镜像站”的原始范围过宽。主控已按腾讯云官方文档
> [《腾讯云软件源加速软件包下载安装和更新》](https://cloud.tencent.com/document/product/213/8623)
> 与 [TencentOS 镜像概述](https://cloud.tencent.com/document/product/1397/130430) 作出限范围裁决：
> 本 Story 在现有腾讯云服务器上，允许 daemon 使用其已有的腾讯云官方缓存
> `mirror.ccs.tencentyun.com` 传输**已由发布方 registry 核实 digest 的原始镜像**。
> 该许可只覆盖“按 digest 固定的准确内容传输”，不接受缓存自行选 tag、改版、重打包；
> 不新增全局配置、服务或费用。发布方来源仍记为 Docker Hub / GHCR 官方仓库，
> 传输来源另记为腾讯云官方缓存，二者不得混写为“官方直连”。下方历史失败记录保持原样。

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

## 2026-10-17 官方工件获取结果（发布方来源 + 实际传输来源）

本节只记录本轮实际取得的内容；不改变上面“最终 API/gateway/PG 运行镜像尚未保存”的结论。

### 发布方来源与准确 digest

来源均为发布方官方仓库：Docker Hub `library/python`、`library/nginx`、`pgvector/pgvector`，GHCR `astral-sh/uv`。
digest 由本机经系统代理 `127.0.0.1:65532` **直连发布方 registry** 读取 index / platform manifest / config / layer 得到，
并非取自缓存或第三方索引。

| 镜像 | index digest | linux/amd64 platform manifest | config（= image config digest） |
| --- | --- | --- | --- |
| `python:3.12.8-slim-bookworm` | `sha256:2199a62885a12290dc9c5be3ca0681d367576ab7bf037da120e564723292a2f0` | `sha256:8859bd6ca943079262c27e38b7119cdacede77c463139a15651dd340087a6cc9` | `sha256:9868da1de9f4ed56f66f6f501440e23c230ea163f0636ef0e24564dcbcc1ef27` |
| `nginx:1.30.6-alpine` | `sha256:970364228b1e4f932abc22d321932816782cca8a20b85a77552a7cfe9acfb3b5` | `sha256:959ae6b898852db82e5b29b929388e59914f42be0a8f4d44c89a4c1f53b49208` | `sha256:0d831f5435ede3eeaba5768270c9e6f542d58306f69bb61f148e5c2374b57c56` |
| `pgvector/pgvector:0.8.7-pg18-bookworm` | `sha256:2358fcba361ed2233a5ed81b5fe4ca779ccb304120ce531a3bf51c0ed7e2bc11` | `sha256:ad249f9fb9572979643a47694e59b9a8cdcdf6abc6accebf49bb80ad5f20ff9b` | `sha256:55141572004e92a39edfdc2d16e821c214b64ca4fba50c1f7e408a09a3d04aff` |
| `ghcr.io/astral-sh/uv:0.12.9` | `sha256:8b940d3a9d65bed080436972241af2e21c84b5e8c9193f7014ed71479ee795ff` | `sha256:3f47db7d4a0e00a2323de663864d0b75cb53e5708121f44b8add6d598be667b9` | `sha256:f95fe1b6262b69e80b069fd3126c11a906a396635d33874eb4713c67aeb9ac67` |

层数：python 4、nginx 8、pgvector 15、uv 2。每层 sha256、size 与 config `rootfs.diff_ids` 均逐层核对通过。

### 版本事实

| 组件 | 镜像内实际值 | 核实方式 |
| --- | --- | --- |
| CPython | `3.12.8 (main, Feb  4 2025, 04:56:13) [GCC 12.2.0]`，`cpython` | 容器内 `python3.12 -c` |
| Nginx | `nginx/1.30.6` | 容器内 `nginx -v` |
| PostgreSQL | `PostgreSQL 18.6 (Debian 18.6-1.pgdg12+2)`，`server_version_num=180006` | 容器内 `pg_config --version`、运行实例 `SHOW server_version_num` |
| pgvector | 扩展 `extversion=0.8.7`，`default_version='0.8.7'` | 运行实例 `pg_extension` / `pg_available_extensions` |
| uv | `uv 0.12.9 (x86_64-unknown-linux-musl)` | 容器内 `/uv --version` |

注意：`library/python` 的 `official-images` master 清单目前已推进到 `3.12.15`，`3.12.8` 已不在该
清单中；但发布方 registry 仍返回该固定 tag 及上述 digest，且内容可复核。**Python 3.12.8 是用户
明确固定的准确版本**，清单推进本身不改变该决定；版本要求以实际镜像与运行值为准，这是本轮结论，
不再把“已退出 master 清单”当作阻塞。

### 完整工件

四个镜像都已形成**完整**工件（index + platform manifest + config + 全部层），并生成两种归档与校验和：

| 镜像 | docker-save 归档 SHA-256 | 大小 | OCI layout 归档 SHA-256 |
| --- | --- | --- | --- |
| python | `sha256:94041eec42016d152be653377941222cd84e7e8e8f427c69294baac999bb0561` | 45,393,920 | `sha256:55df43cb15a2fb88b39a49a2e13016255b8568c03493f4567cc4441b96d58394` |
| nginx | `sha256:7f2b687414d6e5d6a326e502ab6b4a5e031e3bd17a40553e61ed4347bbdd3c69` | 28,549,120 | `sha256:5b520a82a8b49dc3238d5572841c5c1ca582acaadaf90af702b219debf270782` |
| pgvector | `sha256:1f1881cfd22bd341a4242cefae99c7674b5fa82e6f437f73d0834310219e7a68` | 161,669,120 | `sha256:5db5deb2ec294789de7b0508b46cb4e5f16682da4266fb82e995df0d931556e5` |
| uv | `sha256:a7842d12562e8decdd5eafd24ed59c57a19ea26a3fab35f5f53efb14eb661dcb` | 22,927,360 | `sha256:e35c8c59eb1c59b5f2856dc1d58e53f67246a303dc9c4500720a8a9d3fba8901` |

每一份归档旁都有 `receipt.json`（含 index/platform/config/layer digest、image ID、层 diff_id、
逐项校验结果）与 `SHA256SUMS`。四个 docker-save 归档已上传到服务器
`/fileOfRag/testOfRAG/derived/story-1-1/official-image-access/`，并在服务器上重算 SHA-256，与上表一致。

### 两种来源的分别记录（不得混写）

- **发布方来源**：上述 index/platform/config/layer digest 与版本事实来自官方 registry 直连读取（本地经进程级代理）。
- **服务器传输来源**：服务器 daemon 配置了 `mirror.ccs.tencentyun.com`（腾讯云官方缓存），
  `python`、`nginx`、`pgvector` 三个镜像由该缓存按 digest 传输；这是**缓存传输**，不是官方直连。
  `uv` 因缓存无 GHCR 内容、直连 GHCR blob CDN 超时，改由本地经代理从 GHCR 直连获取后，
  用 `sftp` 传入服务器并 `docker image load`。
- 引入的离线归档本身不经缓存：服务器从 bucket 归档 `docker image load` 后，再 `docker save`
  逐层字节与归档一致（config 与全部 layer 哈希、顺序均相同，见 `post-load-content-identity.txt`）。
- 该传输安排依据主控对腾讯云官方文档的限范围裁决，写在本文顶部修订说明中。

### 尚缺与未执行

- 最终 API/gateway 运行镜像尚未构建（依赖 C 前端产物与后端入口），本轮未启动任何依赖 C 的构建。
- 离线 compose override、`--pull never` 起服务、进程停止/重启、干净 Linux 重建均 `not-executed`。
- `docker image load` 后 daemon 的 image ID 变为新计算的本地 ID（config digest 不变）；这是
  `docker save/load` 的正常行为，不当作 digest 丢失，也不把新 ID 写成发布方 digest。
  BuildKit 用发布方 index digest 作 `FROM`（`--network none --pull=false`）仍能命中本地内容并成功执行
  容器内版本命令，见 `from-digest-build-probes.txt`。

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
