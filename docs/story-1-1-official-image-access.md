# Story 1.1 官方准确镜像获取与隔离 PG 测试环境交付记录

2026-10-17，作者：Mencius（`zayuapi/deepseek-v4.1-flash`，派发未传强度，实际 `effort=max`）。
只写 `deploy/**` 与本记录；未改 backend/contracts/frontend，未做 Git 操作。
状态：**镜像获取完成、隔离 PG 已运行；四服务构建与离线重建仍未执行**。

## 1. 结论摘要

| 项 | 状态 |
| --- | --- |
| 四个官方镜像的准确 index/platform/config/layer digest | 已取得并逐层核对 |
| 四个镜像的完整工件（含归档 + receipt + SHA256SUMS） | 已完成，归档 SHA-256 在服务器复核一致 |
| 镜像内实际版本（CPython/Nginx/PG/pgvector/uv） | 已实测，与要求一致 |
| 隔离真实 PostgreSQL 测试服务 | 已创建并运行，仅回环，PG 18.6 + vector 0.8.7 |
| 后端八项真实 PG 测试 | **未执行**（等待固定 Git 提交与后端者运行） |
| API/gateway 构建、四服务 Compose、离线重建 | **未执行**（依赖 C 与后端入口） |

## 2. 发布方来源与准确 digest

来源均为发布方官方仓库。digest 由本机经**进程级**系统代理 `127.0.0.1:65532` 直连官方
registry 读取（index → linux/amd64 platform manifest → config → 全部 layer），未改全局代理、
Docker daemon 配置或任何凭据。

| 镜像 | index digest | platform manifest | config digest |
| --- | --- | --- | --- |
| `python:3.12.8-slim-bookworm` | `sha256:2199a62885a12290dc9c5be3ca0681d367576ab7bf037da120e564723292a2f0` | `sha256:8859bd6ca943079262c27e38b7119cdacede77c463139a15651dd340087a6cc9` | `sha256:9868da1de9f4ed56f66f6f501440e23c230ea163f0636ef0e24564dcbcc1ef27` |
| `nginx:1.30.6-alpine` | `sha256:970364228b1e4f932abc22d321932816782cca8a20b85a77552a7cfe9acfb3b5` | `sha256:959ae6b898852db82e5b29b929388e59914f42be0a8f4d44c89a4c1f53b49208` | `sha256:0d831f5435ede3eeaba5768270c9e6f542d58306f69bb61f148e5c2374b57c56` |
| `pgvector/pgvector:0.8.7-pg18-bookworm` | `sha256:2358fcba361ed2233a5ed81b5fe4ca779ccb304120ce531a3bf51c0ed7e2bc11` | `sha256:ad249f9fb9572979643a47694e59b9a8cdcdf6abc6accebf49bb80ad5f20ff9b` | `sha256:55141572004e92a39edfdc2d16e821c214b64ca4fba50c1f7e408a09a3d04aff` |
| `ghcr.io/astral-sh/uv:0.12.9` | `sha256:8b940d3a9d65bed080436972241af2e21c84b5e8c9193f7014ed71479ee795ff` | `sha256:3f47db7d4a0e00a2323de663864d0b75cb53e5708121f44b8add6d598be667b9` | `sha256:f95fe1b6262b69e80b069fd3126c11a906a396635d33874eb4713c67aeb9ac67` |

层数分别为 4 / 8 / 15 / 2；每层 sha256、size 与 config `rootfs.diff_ids` 均逐层匹配。

### 版本事实（实测，非标签推断）

- CPython `3.12.8 (main, Feb  4 2025, 04:56:13) [GCC 12.2.0]`，实现 `cpython`。
- Nginx `nginx/1.30.6`。
- PostgreSQL `18.6 (Debian 18.6-1.pgdg12+2)`，`server_version_num=180006`，镜像 `PG_VERSION=18.6-1.pgdg12+2`。
- pgvector 扩展 `extversion=0.8.7`，`default_version='0.8.7'`，扩展 schema `public`。
- uv `0.12.9 (x86_64-unknown-linux-musl)`，OCI label `org.opencontainers.image.version=0.12.9`，
  revision `9f928602938ac5cf1cd6b294a725833c16f5720e`。

### Python 3.12.8 的清单状态

`docker-library/official-images` 的 `library/python` 当前 master 已推进到 `3.12.15`，`3.12.8`
不再出现在该清单中。但发布方 registry 仍返回该固定 tag 与上述 digest，内容与层可复核。
**3.12.8 是用户明确固定的准确版本**，清单推进本身不改变该决定，也不构成换版理由。

附注：`pgvector` 上游 Git 存在 tag `v0.8.7`，但 GitHub release 对象对该 tag 返回 404（只有 tag，无 release 附件）。
这不影响镜像内实测的 0.8.7。

## 3. 完整工件与归档

每个镜像均保存了 index、platform manifest、config、全部层，并生成 OCI layout 归档、
docker-save 兼容归档、`receipt.json`（含全部 digest 与逐项校验结论）与 `SHA256SUMS`。

| 镜像 | docker-save SHA-256 | 大小 | OCI layout SHA-256 |
| --- | --- | --- | --- |
| python | `sha256:94041eec42016d152be653377941222cd84e7e8e8f427c69294baac999bb0561` | 45,393,920 | `sha256:55df43cb15a2fb88b39a49a2e13016255b8568c03493f4567cc4441b96d58394` |
| nginx | `sha256:7f2b687414d6e5d6a326e502ab6b4a5e031e3bd17a40553e61ed4347bbdd3c69` | 28,549,120 | `sha256:5b520a82a8b49dc3238d5572841c5c1ca582acaadaf90af702b219debf270782` |
| pgvector | `sha256:1f1881cfd22bd341a4242cefae99c7674b5fa82e6f437f73d0834310219e7a68` | 161,669,120 | `sha256:5db5deb2ec294789de7b0508b46cb4e5f16682da4266fb82e995df0d931556e5` |
| uv | `sha256:a7842d12562e8decdd5eafd24ed59c57a19ea26a3fab35f5f53efb14eb661dcb` | 22,927,360 | `sha256:e35c8c59eb1c59b5f2856dc1d58e53f67246a303dc9c4500720a8a9d3fba8901` |

服务器归档位置：`/fileOfRag/testOfRAG/derived/story-1-1/official-image-access/`
（4 个 `*-image.docker.tar` + 4 个 `*-receipt.json`）。服务器上重算的 SHA-256 与上表一致。
证据归档：`/fileOfRag/testOfRAG/metadata/story-1-1/official-image-access/` 与
`/fileOfRag/testOfRAG/metadata/story-1-1/postgres-test-environment/`。

### 两种来源必须分开读

- **发布方来源**：Docker Hub `library/python`、`library/nginx`、`pgvector/pgvector` 与 GHCR `astral-sh/uv`。
- **服务器传输来源**：服务器 daemon 使用其已有腾讯云官方缓存 `mirror.ccs.tencentyun.com`。
  python / nginx / pgvector 三个镜像由该缓存**按 digest** 传输；这**不是官方直连**。
  uv 因缓存无 GHCR 内容、服务器直连 GHCR blob CDN（`pkg-containers.githubusercontent.com`）超时，
  改由本机经代理自 GHCR 直连获取两层后，以 `sftp` 传入并 `docker image load`。
- 许可依据：主控对腾讯云官方文档的限范围裁决，仅允许按已核 digest 传输原始镜像，
  不允许缓存自选 tag、改版或重打包；未新增全局配置、服务或费用。
  修订说明写在 [offline-images.md](/E:/aaa-project/rag/deploy/offline-images.md:1)。

### 导入后的内容一致性

从 bucket 归档 `docker image load` 后，再 `docker save` 与归档逐字节比较：config 与全部 layer
哈希、顺序完全相同（`post-load-content-identity.txt`）。以发布方 **index digest** 作 `FROM`、
`--network none --pull=false --no-cache` 构建，四个镜像均在容器内打印出预期版本
（`from-digest-build-probes.txt`）。

`docker save/load` 后 daemon 的可见 image ID 会重新计算（例如 python 标签镜像变为
`0709a3f3…`，加载前的 `python:<none>` 仍保留发布方 index digest）。这是该命令的正常行为；
**不把新 ID 写成官方 digest**，内容同一性以上述 config/layer 比对与离线 FROM 探针为准。

## 4. 隔离真实 PostgreSQL 测试服务

用途仅为 Story 1.1 AC2 的真实 PG 测试，不替代 D 的四服务部署。

| 项 | 实际值 |
| --- | --- |
| 容器 | `rag-story-1-1-postgres-test`，ID `36ed102fc9ad…`（完整值见证据 JSON） |
| 镜像 | `pgvector/pgvector:0.8.7-pg18-bookworm`，发布方 index digest `sha256:2358fcba…` |
| 网络 | 项目专属 `rag-story-1-1-test`（bridge） |
| 监听 | `127.0.0.1:55432 -> 5432/tcp`，仅回环；未公开到其他接口 |
| 数据目录 | `/opt/rag-story-1-1/postgres-test/data`，ext4（`/dev/vda2`），`0700`，uid/gid `999:999` |
| 旧目录 | `/opt/rag-story-1-1/postgres` 未被触碰（mtime 保持 16:13） |
| 运行用户 | `999:999`；`--read-only`、`cap-drop ALL`、`no-new-privileges`、`--pids-limit 256`、`--memory 1g` |
| 服务器版本 | `18.6 (Debian 18.6-1.pgdg12+2)`，`server_version_num=180006` |
| vector 扩展 | `extversion=0.8.7`，`default_version=0.8.7` |

### 测试角色与受限授权

- 管理账号 `rag`（超级用户仅用于初始化），密码文件 `0400`，属主 `999:999`。
- 测试角色 `rag_test`：`LOGIN`，`rolsuper=false`、`rolcreatedb=false`、`rolcreaterole=false`；
  仅有目标库 `CONNECT, CREATE` 与 `public` 的 `USAGE`。
- 实测该角色可创建并删除自己的随机 schema、可建表、`has_schema_privilege=true`；
  对共享扩展无所有权，创建 `vector` 时被跳过（`NOTICE: extension "vector" already exists`），
  未发生共享扩展的创建/删除。证据 `role-privilege-check.json`。
- 基础库已预置 vector 扩展；测试 fixture 只创建/删除自己的随机 schema，符合后端 `conftest.py` 的
  `verify_versions()` + `CREATE SCHEMA` 行为。

### 凭据交接方式（不含值）

凭据仅存在于服务器 root 可读的受限文件，不进入 argv、日志、仓库或聊天：

- 进程环境读取方式：在 Linux 测试 shell 执行
  `set -a; . /opt/rag-story-1-1/postgres-test/secrets/test-database.env; set +a`
  该文件 `root:root 0400`，只导出 `RAG_TEST_DATABASE_URL`（含 `rag_test`）与 `RAG_TEST_ALLOW_SCHEMA_CREATE=1`。
- 它不打印、不落 shell history；禁止 `cat` 或 `echo` 该文件内容。
- 隐私检查：对 94 个证据/日志文件扫描两枚密码明文，泄漏 0 处。

## 5. 本轮实际修改的文件

| 文件 | 说明 |
| --- | --- |
| [deploy/tools/acquire_official_images.py](/E:/aaa-project/rag/deploy/tools/acquire_official_images.py:1) | 仅标准库的官方工件获取器；显式进程级代理、逐层 sha256/diff_id 校验、OCI + docker-save 归档与 receipt。本文之后不再继续打磨该工具，未随 `setup.sh` 优先发布 |
| [deploy/postgres-test/setup.sh](/E:/aaa-project/rag/deploy/postgres-test/setup.sh:1) | 隔离 PG 的幂等创建脚本（容器/网络/数据/凭据/预置/证据） |
| [deploy/offline-images.md](/E:/aaa-project/rag/deploy/offline-images.md:1) | 修订过宽禁令、记录发布方来源与腾讯云缓存传输、本轮工件与版本 |
| 本记录 | 交付说明 |

未新增后端、contracts、前端改动；未改全局代理、Docker daemon 配置或 mirror；未做提交/推送。

## 6. 真实命令与副作用

服务器侧关键命令（摘要，完整日志在证据目录）：

```sh
bash /opt/rag-story-1-1/postgres-test/setup.sh
```

副作用：新建容器 `rag-story-1-1-postgres-test`、网络 `rag-story-1-1-test`、
目录 `/opt/rag-story-1-1/postgres-test/{data,secrets,evidence,logs}`、
凭据文件 3 个、回环端口 55432。容器保持运行供后端测试；`restart=no`，不随宿主自启。

镜像侧副作用：daemon 新增 4 个镜像与若干已删除的临时探针容器/镜像；
`snapshot` 归档 4 份写入 bucket。未删除任何既有镜像、目录或 bucket 内容。

本轮遇到并修正的两个自身问题（如实保留）：

1. 首次调用 `tee .../logs/setup.log` 时 `logs/` 尚不存在，命令退出 2，未创建任何容器/网络（无副作用）。
2. 首次使用 `--internal` 网络，Docker 不为 internal 网络做 NAT，`127.0.0.1:55432` 连接被拒；
   改为普通项目 bridge + 仅回环发布后通过。脚本已含对旧 internal 网络的自身清理逻辑。

## 7. 未执行 / 未通过项

| 项 | 状态 |
| --- | --- |
| 后端八项真实 PG 测试（六项集成 + 两项 worker） | `not-executed`，等待固定 Git 提交与后端者运行 |
| API/gateway 运行镜像构建 | `not-executed`（依赖 C 前端产物与后端入口） |
| 离线 Compose override、`--no-build --pull never` 起服务 | `not-executed` |
| 四服务启停/重启/健康、网关缓存负例 | `not-executed` |
| 干净 Linux 重建 | `not-executed` |
| 独立验证与正式审查 | 未开始 |

## 8. 下一可执行动作

1. 主控把 `deploy/postgres-test/setup.sh`、`deploy/tools/acquire_official_images.py`、
   `deploy/offline-images.md` 与本记录纳入同一固定提交，经 GitHub/Gitee 同步后由服务器 checkout。
2. 后端者在 CPython 3.12.8 环境用 `RAG_TEST_DATABASE_URL` + `RAG_TEST_ALLOW_SCHEMA_CREATE=1`
   运行八项真实 PG 测试；容器已就绪，无需重新拉镜像。
3. C 交付后再构建 API/gateway，接 D 的四服务与离线重建验收。

## 9. 冻结快照（2026-10-17，供 Git 发布）

以下 SHA-256 为工作区文件当前字节，**不是**提交号：

| 文件 | SHA-256 |
| --- | --- |
| [deploy/postgres-test/setup.sh](/E:/aaa-project/rag/deploy/postgres-test/setup.sh:1) | `0083b8f5d69cc968cd4da3fa8608dfb703ebbd3b92c5bf400ae6ff589226167a` |
| [deploy/tools/acquire_official_images.py](/E:/aaa-project/rag/deploy/tools/acquire_official_images.py:1) | `c18e991ebd74264145377db01324fbc85cf18c331ede25abb9b79860971de2b1` |
| [deploy/offline-images.md](/E:/aaa-project/rag/deploy/offline-images.md:1) | `9c22dfce87dbaaff34237738beb9bad3959f9798d9166ebb600605afcc545b8b` |
| 本记录（写入后不再自哈希） | 由主控在提交前取实际值 |

`setup.sh` 现为修订版 `0083b8f5…`。服务器 `/opt/rag-story-1-1/postgres-test/setup.sh`
与证据归档 `provision-postgres-test.sh` 仍是**旧的** `6def3bb3…`，即当前运行实例由旧版创建；
两版字节不同，旧副本只能作为预备证据。本记录写完后修订版冻结，后续如需修改必须重新出
SHA 并重述未执行项。

### 冻结与发布范围

- **`setup.sh` 单独冻结并优先发布**，SHA-256 `0083b8f5d69cc968cd4da3fa8608dfb703ebbd3b92c5bf400ae6ff589226167a`；
  从此刻起不再修改该文件，任何改动都视为新版本、需要新 SHA 与新的复核。
- `deploy/tools/acquire_official_images.py` 与 `deploy/offline-images.md` 仍可能调整，
  **本轮不随 `setup.sh` 一起发布**，以免发布活动文件；其当前 hash 只作为观察值。
- 本记录同样可能追加，发布时应以主控实际取到的字节为准。

### 证据定性（重要）

服务器上的 `setup.sh` 副本是在 **Git 发布之前**由本机 `sftp` 上传后执行的。因此：

- 本轮 PG 服务的创建、版本、回环访问、角色权限、证据归档，属于**预备证据**，
  证明“该脚本内容在此服务器上可运行并产出正确结果”；
- 它**不是**“从 Gitee 固定提交取得该脚本并执行”的证据，**不得**重标为某个提交已通过；
- 提交后必须重新取得正式版本、核对 SHA 并做幂等复核（见第 10 节），
  两者的证据要分别保留、分别引用。

### 本脚本的“尚未执行项”（不得据此宣称已验收）

| 项 | 状态 |
| --- | --- |
| 后端八项真实 PG 测试（`pytest --require-postgres` 等） | `not-executed` |
| 测试 schema 之外的后端迁移循环在真实提交上重跑 | `not-executed` |
| 四服务 Compose（gateway/API/worker/PG）联调 | `not-executed` |
| 网关缓存/条件请求/私有资产负例 | `not-executed` |
| 容器停止/重启后数据持久性与再次就绪 | `not-executed` |
| 干净 Linux 重建（含离线 override、`--pull never`） | `not-executed` |
| 独立验证（Step 5 Preview）与正式审查（全新 6.1 Sol / medium） | 未开始 |

已执行且可复核的仅有：镜像 digest/层核对、版本实测、隔离 PG 创建与回环访问、
受限角色 DDL 授权负例、归档 SHA-256 与 `docker load` 内容同一性、离线 `FROM` 探针。

## 10. 发布后的幂等复核结果（2026-10-17 已执行）

正式版本执行完成。以下是本次真实结果，取代下方原计划步骤中的“尚未执行”状态。

### 执行事实

| 项 | 结果 |
| --- | --- |
| 来源 | 仅 Gitee `https://gitee.com/QAQsdsdsdsds/rag_project.git` |
| 提交 | `9da9af209123e8f57b2650e14b98175f4aa5fefd` |
| 检出 | 干净目录 `/opt/rag-story-1-1/repo-pg-formal`，shallow fetch 该 commit 后 detached checkout，`git status --porcelain` 为空 |
| 脚本 SHA-256 | `0083b8f5d69cc968cd4da3fa8608dfb703ebbd3b92c5bf400ae6ff589226167a`（与冻结值一致） |
| 执行 | `bash deploy/postgres-test/setup.sh` |
| 退出码 | **0** |
| 容器 | `rag-story-1-1-postgres-test`，ID 仍为 `36ed102fc9ad…`（复用，未重建） |
| 网络 | `rag-story-1-1-test`，`Internal=false` |
| 版本 | `server_version_num=180006`，`server_version=18.6 (Debian 18.6-1.pgdg12+2)`，`vector.extversion=0.8.7`，`default_version=0.8.7` |
| 回环探针 | `rag_test\|rag\|180006\|0.8.7` |
| 监听 | 仅 `127.0.0.1:55432` |
| 数据目录 | `/opt/rag-story-1-1/postgres-test/data`，ext4 `/dev/vda2`，`0700 999:999`，未重建，旧 `/opt/rag-story-1-1/postgres` 未触碰 |
| 镜像引用 | 证据记录 `sha256:2358fcba…`（digest 形式） |

### 运行中的一个可证事实

`pgvector/pgvector:0.8.7-pg18-bookworm@sha256:2358fcba…` 这一 **tag+digest 组合引用在本机不可解析**
（`docker image inspect` 返回非零），而裸 digest `sha256:2358fcba…` 可解析。原因是此前离线
`docker image load` 使该内容以新的本地 ID `12837756808d…` 存在，原始 tag+digest 解析路径不再指向它。
脚本按设计回退到 **digest 引用** `sha256:2358fcba…` 并继续，未回退到裸 tag，未触发任何拉取
（两次 `docker run` 都带 `--pull never`）。证据 JSON 的 `image.reference` 如实记为该 digest 形式，
并未伪写成 tag+digest。

这是冻结版本预期内的分支，不是验收失败。`docker tag` 只能生成 `repo:tag`，**不能制造
`repo@digest` 引用**，因此不存在“把内容重新 tag 回官方 tag+digest”的做法；后续需要引用时，
按现有 receipt 记录的发布方 index/platform/config digest 与 daemon 实际 `RepoDigests`/image ID
映射选择可解析的引用，并在使用前核对层内容，不另造引用流程。

### 凭据文件（只列路径与权限）

| 文件 | 权限 |
| --- | --- |
| `/opt/rag-story-1-1/postgres-test/secrets/postgres-password` | `0400`，`999:999` |
| `/opt/rag-story-1-1/postgres-test/secrets/test-role-password` | `0400`，`root:root` |
| `/opt/rag-story-1-1/postgres-test/secrets/test-database.env` | `0400`，`root:root` |

安全加载方式：`set -a; . /opt/rag-story-1-1/postgres-test/secrets/test-database.env; set +a`，
只导出 `RAG_TEST_DATABASE_URL` 与 `RAG_TEST_ALLOW_SCHEMA_CREATE=1`。禁止 `cat`、`echo` 或写入日志。

### 归档证据

`/fileOfRag/testOfRAG/metadata/story-1-1/postgres-test-environment/`：

- `formal-setup.log`（SHA-256 `ab8bd1aa…`，与本 job 输出一致）
- `formal-setup-9da9af2.sh`（SHA-256 `0083b8f5…`，直接从该 checkout 复制）
- 先前预备证据（`provision-postgres-test.sh` = 旧 `6def3bb3…`、`role-privilege-check.json` 等）原样保留，
  未重标为本次提交通过
- `postgres-test-environment.json`（本次运行生成，SHA-256 `326791c2…`）
- 目录内 `SHA256SUMS.bucket.txt` 已刷新

### 尚未执行

后端八项真实 PG 测试、四服务 Compose、接口/浏览器/部署门与正式审查仍为 `not-executed`；
本次仅完成“正式版本取得 + 幂等复核 + PG/vector 版本与连接就绪”。

## 11. 原计划步骤（保留为历史说明）

主控完成 GitHub/Gitee 同步、服务器从 Gitee 拉取固定提交后，按下列顺序复核；
**不得清理旧数据、不得删除既有容器/网络/目录、不得触碰其他项目或存储桶内容**。

1. 在服务器项目 checkout `git rev-parse HEAD` 与主控发布的提交号比对；不一致即停止。
2. 取该 checkout 中 `deploy/postgres-test/setup.sh` 的 SHA-256，与
   `0083b8f5d69cc968cd4da3fa8608dfb703ebbd3b92c5bf400ae6ff589226167a` 比对；
   不一致即停止，不得改脚本去迁就。
3. 确认容器已在运行：
   `docker inspect --format '{{.State.Running}}' rag-story-1-1-postgres-test`。
   若为 `false`，先 `docker start rag-story-1-1-postgres-test` 并等待 `pg_isready`
   ——**不改脚本**，因为冻结版本的重跑路径假定容器可执行 `docker exec`。
4. 从 checkout 中执行该脚本（脚本本身幂等：复用的数据目录、容器、网络与凭据文件不重建，
   只补授权、刷新证据归档；`CREATE EXTENSION IF NOT EXISTS vector` 对已存在扩展跳过，
   不会删除或重建任何共享扩展）。
5. 复核并另存新证据：`server_version_num=180006`、`vector.extversion=0.8.7`、
   `rag_test` 仍非超级用户、监听仍仅 `127.0.0.1:55432`、数据目录仍为 ext4 `0700 999:999`。
6. 通过后交后端者在 CPython 3.12.8 下运行八项真实 PG 测试；
   测试只创建/删除自己的随机 schema。

### 冻结版本的实际行为

- 修订版把官方 digest 写成唯一镜像引用 `pgvector/pgvector:0.8.7-pg18-bookworm@sha256:2358fcba…`，
  `docker image inspect`、`docker run`、证据生成全部使用该引用，并统一传 `--pull never`；
  镜像不存在时直接 `blocked` 退出，不会隐式回网补齐。若离线加载导致该引用不可解析，脚本接受
  **digest 形式** `sha256:2358fcba…` 作为等价引用，不使用裸 tag。
- 版本断言在交接前执行：`server_version_num` 必须为 `180006`，`vector.extversion` 必须为 `0.8.7`，
  回环测试角色查询必须返回 `rag_test|rag|180006|0.8.7`，任一不符即 `blocked`。
- 若同名网络已存在且 `Internal=true`，修订版**直接拒绝**并以 `blocked` 退出，
  不 stop、不 rm、不改网络。该分支当前不会触发（现有网络 `Internal=false`）。
- 重跑时若容器存在但已停止，`docker exec` 探活会在 60 次重试后退出 2，且不写业务数据、
  不删目录；`docker start` 仍属操作前提，脚本不自动接管。
