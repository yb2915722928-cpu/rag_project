# Story 1.1 D 部署交付记录

2026-10-17，状态 `partial-blocked`。只修改 `deploy/**` 与本记录；未修改后端、前端、contracts、规格、Sprint 或 relay。

## 已交付

- [Compose](/E:/aaa-project/rag/deploy/compose.yaml:1) 仅声明 gateway/API/worker/PostgreSQL。API 和 worker 使用相同后端镜像、application 与共享锁根；不增常驻队列。仅 gateway 发布 HTTPS，默认绑定宿主 127.0.0.1:8443，明确配置绑定地址后才可对外。
- [API Dockerfile](/E:/aaa-project/rag/deploy/api.Dockerfile:1) 要求精确 Python 3.12.8 和 digest 固定的 uv 工件，以 `uv sync --locked --no-dev --no-editable` 安装并核实际 Uvicorn 0.37.0；旧锁会失败，不使用 pip 重解或 frozen 绕过。镜像以 65532:65532 运行。
- [gateway Dockerfile](/E:/aaa-project/rag/deploy/gateway/Dockerfile:1) 只复制真实前端 dist；前端缺失即构建失败，没有占位前端冒充交付。Node 不进入运行镜像。
- [Nginx](/E:/aaa-project/rag/deploy/gateway/nginx.conf:1) 不记录访问 URI/query；私有路径完整代理、无前缀删除，无私有静态挂载；禁缓存、条件头、上游缓存头和 X-Accel 内部跳转。`proxy_buffering` 与 `proxy_request_buffering` 均关闭，HTTP 1.1、无代理临时文件、有限超时。网关错误 no-store，只有 Vite hash 命名的公开 assets 成功响应允许 immutable。
- 服务非 root、根只读、cap_drop ALL、no-new-privileges、有限 tmpfs/PID/内存/日志与 20s SIGTERM 关闭。PG 明确要求先核镜像 UID/GID并准备相应数据/secret权限，不依赖 root 入口 chown/setuid。
- [只读预检](/E:/aaa-project/rag/deploy/preflight.py:1) 检查 digest、解释器/锁、前端交付、Linux 本地介质和 secret；缺项退出 2，不创建数据或拉镜像。

## 实际验证

| 检查 | 结果与限度 |
| --- | --- |
| 规格及四份 frontmatter context | 已完整读取 |
| YAML 与四服务/有界关闭/私有代理策略静态检查 | 最终版通过；不是 Nginx 语法或 HTTP 运行验收 |
| 远程 Compose 5.6.0 无配置负例 | 退出 1，明确拒绝未提供的 digest/数据库/secret；不是正例构建 |
| 远程最终 Compose 结构解析 | 使用明确标为 validation-only 的零 digest 与 `/dev/null` 路径，`config --quiet` 退出 0；只验结构，未启动容器 |
| 最终预检缺依赖负例 | 退出 2，列出四项 digest、后端/前端交付及四项 secret 缺失；未拉镜像或创建数据 |
| 最终文件上传和 SHA-256 | 传输包 SHA-256 `18320beb7231f4c54fe472659dc6ff9e9a251dab1a905c257cc4b1711212d5ad`，远程解包前已核；核心文件 hash 见本地 evidence |
| `/opt` 文件系统 | `findmnt`: `/dev/vda2 ext4 rw,relatime` |
| `/fileOfRag` 文件系统 | `findmnt`: `cosfs fuse.cosfs`；只归档证据 |
| 宿主 ext4 临时探针 | SH 阻另一进程 EX、关闭后 EX 成功、replace/file fsync 通过；临时目录已清理，不能代替容器跨挂载/UID证明 |
| Docker Hub urllib | 四个目标探测均 `URLError [Errno 101] Network is unreachable`；此错误不能代表所有网络不可达 |
| Docker manifest Python | 退出 124，registry ping 超时；未取得 digest |
| 独立 IPv4 curl registry/auth | 两项退出 28，各连接 4s 超时；补证不是只有 IPv6 失败 |
| GitHub IPv4 release HEAD | 200；只证明该 URL 可达 |
| GitHub raw Dockerfile IPv4 | PG18、Nginx 两项 8s 超时；未核实最终镜像 UID/源码 |
| 整栈构建/迁移/进程/重启/干净重建 | `not-executed`，不宣称四服务已可用 |

远程证据：专属目录 `/opt/rag-story-1-1/deploy/evidence/`；归档 `/fileOfRag/testOfRAG/metadata/story-1-1/deploy/`。文件包括 `source-probe.json`、`ipv4-and-official-dockerfiles.json`。错误原样保留，不输出 token、密码或业务正文。Docker Hub 无可用镜像/准确 digest，未换版本或第三方源。

四份原始证据均已下载到本地：[最终静态核验](/E:/aaa-project/rag/deploy/evidence/final-static-verification.json:1)、[来源探测](/E:/aaa-project/rag/deploy/evidence/source-probe.json:1)、[IPv4探测](/E:/aaa-project/rag/deploy/evidence/ipv4-and-official-dockerfiles.json:1)、[文件系统探针](/E:/aaa-project/rag/deploy/evidence/filesystem-probe.json:1)。构建、真实 HTTP 缓存负例、进程与关闭、迁移和重建均没有通过记录。

## 当前集成阻塞与接口请求

1. 后端 API 当前绑定 127.0.0.1:8000，容器间不可访问；需原后端实现者提供经过精确解释器和 Uvicorn 校验的 `python -m rag_app api`，在容器配置下绑定 0.0.0.0:8000。
2. 后端只有一次性 `check-database`；Compose 的目标接口是 `python -m rag_app worker`，需持续存活、有限 TERM 退出、与 API 共用 bootstrap/application，不增业务调度或外发。当前命令尚不存在，必须明确阻塞，不用 sleep 循环伪装 worker。
3. 后端仍需有效新锁、目标解释器、真实 PG 六项和迁移循环。frontend dist 未交付，不构建占位壳放行。
4. PG18 候选布局为 `/var/lib/postgresql/18/docker`，绑定父目录 `/var/lib/postgresql`；官方 raw 源读取超时、实际镜像未取得，因此此布局和 UID/GID 仍待按实际工件核验。同样，共享锁 inode、跨进程 flock、原子操作及容器 UID 权限须实测，ext4 名称不自动证明完成。
5. 需要准确 Python、uv、Nginx 1.30.6 与 PG18.6+pgvector0.8.7 digest。探测中的 nginx stable tag 仅为发现性请求，不能作为批准镜像。无镜像时不运行未经锁定构建。

## 后续可执行路径

2026-10-17 后续流程已改为本地推送新的私有 rag_project，服务器拉取固定完整 commit；Git 由主会话统一维护。旧上传包仅保留历史验证证据，不再作为新集成传输方式。本地仓库目前尚无 HEAD，GitHub 待登录，不填写虚构提交。服务器在专属项目目录拉取该提交后，构建 context 对应该 checkout 中的后端和真实前端产物，不访问或改动后端开发者独占的 backend-work。

部署操作者先核实实际镜像运行 UID/GID与目录布局，准备仅相关 UID 可读的 PostgreSQL 密码文件、UID 65532 所有且 0600 的 libpq pgpass 文件，以及 gateway UID 可读的 TLS 证书/私钥。DSN 不携密码，采用 `postgresql+psycopg://rag@postgres/rag` 和按服务挂载的 PGPASSFILE；rag 引导账号暂为管理账号，后续最小数据库角色仍需收敛，不能称生产安全门通过。API/worker 资产和锁目录须 UID 65532 可写，epoch 只读；PG 数据目录 0700 且归实际 PG UID。不要删除锁文件、存储桶或既有宿主数据。

设置 Compose 中所有强制变量，包括四项准确 `*@sha256:...` 镜像引用、PG UID/GID、TLS 和 secret 文件路径。真实启动后再保存入口验收证据。预检与锁同步成功后：

```sh
python3 deploy/preflight.py
docker compose -f deploy/compose.yaml config --quiet
docker compose -f deploy/compose.yaml build --pull=false
docker compose -f deploy/compose.yaml up -d postgres
docker compose -f deploy/compose.yaml run --rm --no-deps api python -m rag_app migrate head
docker compose -f deploy/compose.yaml run --rm --no-deps api python -m rag_app check-database
docker compose -f deploy/compose.yaml up -d api worker gateway
docker compose -f deploy/compose.yaml ps
docker compose -f deploy/compose.yaml stop --timeout 20
docker compose -f deploy/compose.yaml start
```

关闭不含 down -v、prune 或宿主删除。首次启动、迁移先后顺序和后续发布停写由操作者执行；当前 Compose 不自动迁移。健康目前只表示 health liveness，不证明 schema/epoch/供应方 ready。后续运行须记录版本、hash/digest、实际进程、权限、网关正负例、副作用和停止/重建证据，再交独立验证和全新实例审查。父 Story 完成门未通过。

## 独立离线准备与写入释放

2026-10-17 本次新增[官方同版本镜像离线准备](/E:/aaa-project/rag/deploy/offline-images.md:1)。本地沙箱外 Hub IPv4 registry/auth 同样连接超时，未重探远程既有阻塞；官方 GHCR uv 0.12.9 manifest 返回 200 和一个响应 digest，仅 manifest 证据，不代表取得完整平台镜像。没有新增上传 transport、启动/修改本地 Docker、安装工具或全局清理。

A1 正常锁已由原作者在 Linux 生成，主会话报告 locked 同步仍在下载；此为新进展，原先“锁未交付”说明属于上一验证时点，不能据此否定新锁，也不能自动把 locked 同步改记通过。后端 bind/worker 短规格已由主会话准备交原作者处理，D 不越权修后端。等待真实 C/入口及镜像工件就绪后，按固定 commit/hash 再接 D 集成。

本次准备返回后 D 释放 deploy 与本记录的写入职责，保持 `partial-blocked`，不继续探测同一外部阻塞；主会话唯一维护 relay/工作集及后续派发。

## 2026-10-17 收敛增量：静态准备冻结

本节只记录本轮 `deploy/**` 的静态修复和真实状态，不覆盖上文旧证据。文件已冻结；真实 Linux 构建、迁移、启动、健康、停止/重启和干净重建仍为 `not-executed`。

### 本轮实际修改

- [compose.yaml](/E:/aaa-project/rag/deploy/compose.yaml:1)：仍只有 gateway/API/worker/PostgreSQL 四服务。API/worker 固定 `65532:65532`、只读根、`cap_drop: ALL`、`no-new-privileges`、有限 tmpfs/PID/内存/日志和 20s SIGTERM；API 容器 bind 固定为 `0.0.0.0:8000`，不再允许 `RAG_API_HOST/PORT` 覆盖，避免与 gateway upstream、API 健康检查产生配置漂移。gateway 健康检查经 TLS 访问 `/health`（跳过证书校验，仅容器内 liveness）；worker 增加只读 `/proc` 进程存活检查；PG 增加 256 pids、256m shm、`SIGINT` 和 60s 停止宽限。API/worker/PG 的项目目录全部改为 `create_host_path: false` 的显式 bind，缺失目录直接启动失败，不由 Compose 隐式创建。
- [compose.yaml](/E:/aaa-project/rag/deploy/compose.yaml:1) 的 secrets 处理：仍保留 Compose `file` secret 挂载，但**删除 `uid/gid/mode` 声明**。本地 Compose 的 file secret 是宿主文件 bind，Compose 在该模式下不保证应用这些字段；声明它们会制造“已限制权限”的假象。宿主文件的属主/权限是唯一有效来源，由 preflight 按实际 UID/GID 与 0400/0600 校验。该宿主权限是否在真实容器内被正确读取仍未实测。
- [api.Dockerfile](/E:/aaa-project/rag/deploy/api.Dockerfile:1)：保留 digest 参数、精确 CPython 3.12.8、`uv sync --locked --no-dev`、Uvicorn 0.37.0 与 import 校验；改为先安装依赖、后复制源码并 `--no-install-project`，避免在依赖层复制未完成的应用；构建期拒绝 `/app` 下 group/other 可写路径；worker liveness 探针由独立 build context 复制，避免运行期 bind 宿主代码。
- [gateway/Dockerfile](/E:/aaa-project/rag/deploy/gateway/Dockerfile:1)：只从 `deploy/gateway` 取 `nginx.conf`，从前端构建产物的独立 named context 取静态文件，要求真实 `index.html`；未引入 Node 运行镜像。
- [gateway/nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:1)：私有 `/api/` 无缓存、无代理缓冲/请求缓冲/临时文件、`proxy_next_upstream off`、隐藏上游缓存与条件头、忽略 `X-Accel-*`、`proxy_redirect off`；原始文件 PUT 使用独立 20MiB 上限和更长超时，不继承 1MiB JSON 界；只有 **最终状态为 200** 且 URI 为 hash 命名的 `/assets/*` 才允许 immutable，其他状态（403/405/5xx 等）与未 hash 路径均为 no-store；SPA 壳仅 GET/HEAD；`/__maintenance/` 固定 404；错误页 no-store；访问日志关闭，仅 stderr critical。新增约 16KiB 请求头上限和 `X-Content-Type-Options`。含量词的正则参数全部引用。
- [preflight.py](/E:/aaa-project/rag/deploy/preflight.py:1)：保持只读准入，不拉镜像、不建数据。新增 CPython 3.12.8 检查；镜像 digest/批准版本检查；项目目录必须在 `/opt/rag-story-1-1` 且为 ext4/xfs/btrfs，并校验 PG 数据目录属主为已核 PG UID/GID、assets/locks 属主 65532 且可写、epoch 只读；目录权限要求 owner read+execute 两位同时存在（非任一即可），可写目录还要求 owner write。secret 必须存在且位于仓库外，校验宿主属主与精确模式 `0400`/`0600`（owner read 必须存在，group/other 必须为零）；所有失败去重后输出有限 JSON，未知异常也只返回 `blocked` 与固定文案，不打印 traceback。
- 新增 [`.env.example`](/E:/aaa-project/rag/deploy/.env.example:1)、[api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1)、[gateway/.dockerignore](/E:/aaa-project/rag/deploy/gateway/.dockerignore:1)、[worker/.dockerignore](/E:/aaa-project/rag/deploy/worker/.dockerignore:1)、[worker/healthcheck.py](/E:/aaa-project/rag/deploy/worker/healthcheck.py:1)、[evidence/README.md](/E:/aaa-project/rag/deploy/evidence/README.md:1)。删除了旧的 `deploy/.dockerignore` 和本轮一度新增、随后移除的 `deploy/postgres/healthcheck.sh`；PG 健康检查改为镜像内 `pg_isready`。
- [api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1) 在源码/迁移 allowlist 后补充递归排除 `__pycache__`、`*.py[cod]`、`.env`（保留 `.env.example/.sample/.template`）、私钥/证书、密钥库、pgpass、secrets、credentials 和 service-account 文件，避免现有缓存或 Git 忽略的本地敏感文件因 `!src/**`/`!migrations/**` 被重新纳入构建上下文。

### 主会话提出的协调问题

1. **preflight 非数字 UID/GID**：空或非法的 `RAG_POSTGRES_UID/GID` 不再传入 `int()`；先分别判定是否合法，仅把合法值交给属主比较，非法值只产生有限 blocked 文案。入口另加兜底，任何未预期异常都输出固定 blocked JSON、退出 2，不输出原始 traceback。
2. **API bind 漂移**：删除 `RAG_API_HOST/PORT` 的可覆盖默认值，Compose 固定 `0.0.0.0:8000`；gateway upstream 与 healthcheck 均按 `api:8000`/`127.0.0.1:8000` 保持同步。要求改变端口时必须同时修改三处，不能只改环境变量造成合法配置下失联。
3. **权限位判定的确定性缺口（本轮静态复核）**：目录原先用 `st_mode & 0o500` 的真值判断，`0400`/`0100` 任一存在即放行；改为要求 `0o500` 两位同时存在。secret 原先只拒绝 group/other 权限，`0000`/`0100` 能通过；改为只接受精确 `0400` 或 `0600`。两处仍只输出有限 blocked 文案。
4. **独立预审 F5/F7（静态修复）**：F5 将含 `{8,}`/`{1,64}` 的完整正则参数加引号，并检查配置内其余同类语法（`if` 方法正则也加引号）。F7 将资产缓存映射改为 `"$status:$uri"`，仅 `200` + hash URI 命中 immutable；403/405/5xx、404 与非 hash 路径均为 no-store。未执行 `nginx -t` 或任何 HTTP 请求，语法/行为仍未验证。
5. **F8 构建输入隔离（主会话集成核对发现，非独立预审）**：原独立预审只列出 F1–F7；F8 由主会话在集成核对时发现。错误路由的恢复实例先写入了草案，不能标为 DeepSeek 有效交付；本记录末尾的 F8 段登记接替作者的审阅与最小修正。未执行真实 Docker context 列举或干净重建；F8 的 context 行为仍为 `not-executed`，只记录静态规则和文件 hash。

### 本轮文件 SHA-256（本地冻结值）

| 文件 | SHA-256 |
| --- | --- |
| [compose.yaml](/E:/aaa-project/rag/deploy/compose.yaml:1) | `2e438b05f9510b53c811256f2ac237d9e22f3f8096af462dbf30128c157d452e` |
| [api.Dockerfile](/E:/aaa-project/rag/deploy/api.Dockerfile:1) | `38876b71ec93a603f04a2533e3254895acd39569d3c84deb0b38dd5058399348` |
| [api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1) | `4185b2288406dcf9c5c2e2651fe6ae0f4adff7ab88c3b60e13b7aa362f9ecc01` |
| [gateway/Dockerfile](/E:/aaa-project/rag/deploy/gateway/Dockerfile:1) | `984d4fa5924a8908f4ba356ff7bee847f594141f8252bcb3a4b988ec7a6a79b6` |
| [gateway/nginx.conf](/E:/aaa-project/rag/deploy/gateway/nginx.conf:1) | `cd167d3f87a7263fd0903b151201dae653200c7f5bd8c446eca112a59181ab34` |
| [gateway/.dockerignore](/E:/aaa-project/rag/deploy/gateway/.dockerignore:1) | `5229701e01dd1b3e4977aa480866c60ecea91fe8071cfccb87c0b4066f7593bc` |
| [worker/healthcheck.py](/E:/aaa-project/rag/deploy/worker/healthcheck.py:1) | `cb38351da6c9f8f50a144d4dd741de547c04ff0ffc363543ccc5d5a832f9240a` |
| [worker/.dockerignore](/E:/aaa-project/rag/deploy/worker/.dockerignore:1) | `7b2750f36a60aff1e210a1bfe7cce72aca6c9cb76867ff2137fd1a6bbf55d007` |
| [preflight.py](/E:/aaa-project/rag/deploy/preflight.py:1) | `cedda5af4d598f5a4058aac9b92625d583f3a8c27fe3147e31225c1abce7a0e1` |
| [.env.example](/E:/aaa-project/rag/deploy/.env.example:1) | `feff1d95291a049c03d1940d018f4d1eadb005c5b7afa01f7f95722f4d54ce2c` |
| [evidence/README.md](/E:/aaa-project/rag/deploy/evidence/README.md:1) | `93a90f7e71290ebea20c31ac6c69ff14bd346c68655a5ebae76c72b90541df12` |

这些 hash 是工作区文件内容，不是 Git 提交号、镜像 digest 或构建产物 digest。Git HEAD 仍为 `a52ae3090948e7eeea6df87590f15ce35351d247`；本轮没有提交、推送或同步 GitHub/Gitee。

上表中 `api.Dockerfile.dockerignore` 的 `4185b228...` 是该轮冻结时的旧值；该文件随后因 F8 草案与最终修正发生变化，当前值以文末 F8 交付段为准，旧值不再代表工作区字节。

### 实际执行与未执行

| 项目 | 状态 |
| --- | --- |
| 阅读 AGENTS、D 规格、epic context、runtime-operations、当前后端 API/worker/config、当前 deploy 文件 | 已完成（本地只读） |
| 本地文件 SHA-256、`git status`/`git diff`（只读） | 已完成 |
| 本地 `docker compose config --no-interpolate` | 仅补充观测：在**中间修订**上曾退出 0；不覆盖最终冻结文件，不构成结构或运行门 |
| 本机 Docker CLI/Python 版本读取 | 仅补充观测：Docker 29.6.1、Compose v5.2.0、CPython 3.12.8；未用于任何验收 |
| Netcatty 远程环境只读盘点（主机、Engine 29.8.2、Compose v5.6.0、项目目录） | 仅补充观测：未运行最终修订 |
| 最终修订 `docker compose config`（Linux） | `not-executed` |
| 最终修订 preflight（Linux、真实 secret/UID/GID） | `not-executed` |
| `nginx -t`、Nginx 实际启动、TLS/缓存/条件请求/上传正负例 | `not-executed` |
| F5 正则参数引用与 F7 状态+URI 缓存映射的实际语法/HTTP 行为 | `not-executed`；只有静态文本检查 |
| API/worker 镜像构建、真实 Uvicorn/worker 进程、健康检查、TERM 停止 | `not-executed` |
| PostgreSQL 18.6 + pgvector 0.8.7 启动、迁移循环、六项必跑、namespace 负例 | `not-executed` |
| 四服务 Compose 启停/重启、干净 Linux 重建、资源与权限实测 | `not-executed` |
| 精确镜像 digest 获取与核对 | `not-executed`（无新网络证据，不重复探测） |
| 固定 commit/GitHub/Gitee 同步 | `blocked`：本轮无提交，服务器无可拉取的固定提交 |

### 剩余阻塞与风险

- **固定提交缺失**：当前改动尚未形成可拉取提交；服务器不能据此构建或测试。按用户指令不重试 Git/SFTP，也不使用替代传输。
- **完整镜像缺失**：Python 3.12.8、Nginx 1.30.6、uv、PostgreSQL 18.6 + pgvector 0.8.7 的准确 linux/amd64 digest 与镜像层仍未取得；没有网络环境变化，不重复探测。`offline-images.md` 仍只是准备说明。
- **前端产物缺失**：`frontend/dist/index.html` 尚未交付，gateway 构建会在 `test -s` 失败；没有放占位页面。
- **Compose file secret 权限未实测**：删除 `uid/gid/mode` 后，容器内可读性完全依赖宿主文件属主 65532:65532 与 0400/0600；preflight 只能检查宿主，不能证明容器实际挂载结果。PG 密码文件同理依赖已核 PG UID/GID。
- **API bind 固定**：若将来确实需要改端口，必须同改 Compose 环境、gateway upstream、两处健康检查和文档；当前不接受单独覆盖。
- **Nginx/上游假设**：`/etc/nginx/mime.types` 和 `wget` 依赖所选 Nginx 基础镜像；未取得镜像前不能确认。构建使用 named context 与 Dockerfile-specific ignore，需真实 BuildKit 验证。
- **网关健康检查跳过证书校验**：只证明容器内 TLS 监听与 API 代理路径，不证明部署证书链/主机名正确。
- **worker 探针**：按 `/proc/*/cmdline` 精确匹配 worker 命令行；容器 PID 视图、init 包装和进程名变化均未实测。
- **条件写头被清空**：gateway 目前对私有 API 清空 `If-Match`/`If-Unmodified-Since`/`If-Range`；当前无业务条件写端点，后续启用时必须重新评估，不能沿用此配置作为并发控制实现。
- **20MiB 原件上限**：是初始化 seed，尚未经过真实上传、chunked/流式和预算验证。

本轮结束时 D 冻结 `deploy/**` 与本记录并释放写入；后续静态复核问题由主会话再交回修复，真实运行门仍需新环境证据。

## 2026-10-17 F8 构建输入隔离（接替作者交付）

本节追加于上述收敛增量之后，不覆盖旧记录；F5–F7 的静态复核结论和所有历史 hash 保持原样。

### 来源与作者

- **来源纠正**：原独立预审只列出 F1–F7；F8 由主会话在集成核对时发现，不属于独立预审发现。上文第 5 项原先写作“独立预审 F8”，已在本轮改正。独立复核不在此进行，待本文件冻结后由 Hypatia 执行。
- **作者与路由**：本节由 Story 1.1 deploy 原作者路由的接替实例 Russell 撰写（thread `01a149ef-fab5-7453-80dc-f8a36e635119`）。派发指定 `zayuapi/deepseek-v4.1-flash`，未显式传推理强度；本人可读取的 `turn_context` 为 `model=zayuapi/deepseek-v4.1-flash`、`effort=max`，与工作集记录的其他 DeepSeek 实例一致。底层供应方身份未核，不作宣称。
- **草案处置**：错误路由的恢复实例已把 F8 草案写入工作树（937 字节，SHA-256 `3C2942BE6E0EE552D2C28A2F1D5E1C869E6BC8B20DC86CEA9E0199AE8CC566BC`）。该草案不是 DeepSeek 的有效交付，也不冒充其撰写。接替者逐条审阅后原位重写，采纳“allowlist 后二次收窄”的方向，并修正下述可证问题；草案内容与模型/hash 历史按用户要求保留于此处，不删除。

### 对草案的修正

| 草案问题 | 最终处理 |
| --- | --- |
| 仅写 `**/*.py[cod]`；若匹配器把方括号按字面处理，`.pyc` 不会被排除 | 保留文档形式 `*.py[cod]`，再并列 `*.pyc`、`*.pyo`、`*.pyd`，两层都成立 |
| `!**/.env.example/.sample/.template` 在根范围重新纳入，等于把 backend 根的示例文件拉回上下文，超出 allowlist 意图 | 示例仅在 `src/**` 与 `migrations/**` 下重新纳入；backend 根的 `.env.example` 仍被排除 |
| `!**/*.example.pem`、`!**/*.sample.pem`、`!**/*.example.key`、`!**/*.sample.key` 按文件名放行；文件名不能证明内容不含私钥 | 删除全部 example/sample 例外，任何 `.pem`/`.key` 均排除 |
| 证书族不完整，缺 `.crt`、`.cer`、`.csr`、`.p8`、`.ppk` 及 SSH 私钥 | 补齐 `.crt/.cer/.csr/.p8/.ppk` 与 `id_rsa*`、`id_ecdsa*`、`id_ed25519*` |
| 凭据只枚举 `credentials.json` 与 `*-credentials.json`，漏掉 `my_credentials.json` 之类 | 改为有界的 `*credential*.{json,yaml,yml}` 与 `*service[-_]account*.{json,yaml,yml}`；`credentials.py`、`secrets.py` 等合法模块不被误排除 |
| secrets 只排除目录名，缺少递归内容规则 | 增加 `**/secrets/**`、`**/.secrets/**` |

最终规则分组（顺序即语义，后匹配覆盖先匹配）：

1. allowlist：[api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:6)，范围：6–14，仅 `pyproject.toml`、`uv.lock`、`.python-version`、`alembic.ini`、`src/**`、`migrations/**`。
2. 环境文件：[api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:16)，范围：16–29，排除 `.env`、`.env.*`、`.envrc`、`.direnv`，仅在两条 allowlist 子树内恢复三种示例后缀。
3. 证书与密钥：[api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:31)，范围：31–46。
4. pgpass、secrets 与凭据载荷：[api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:48)，范围：48–70。
5. 缓存与字节码放在最后：[api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:72)，范围：72–81，排除 `__pycache__` 及其内容、`*.py[cod]`。

### 静态检查与未执行门

- 实际只读扫描当前 backend：`src/` 与 `migrations/` 下共 63 个文件，其中 31 个 `.py`、31 个 `.pyc`、1 个 `.mako`；17 个 `__pycache__` 目录；未发现 `.env`、证书、密钥、pgpass、secrets 或凭据命名的工件。按最终规则推演，31 个 `.pyc` 被排除，31 个 `.py` 与 `migrations/script.py.mako` 保留。扫描只读取名称与扩展，未打开任何可能是秘密的文件内容。
- 用本地 PowerShell 正则按“后匹配覆盖先匹配”模拟上述规则，对 47 个路径样例（合法源码、迁移模板、示例环境文件、缓存、字节码、各类证书/密钥/凭据，以及 `credentials.py`、`secrets.py`、`service_account_client.py` 等易误伤模块）比对预期，结果全部符合预期。这是规则语义的等价推演，不是 Docker/BuildKit 的匹配结果。
- `not-executed`：真实 Dockerfile-specific context 列举、`docker build`/BuildKit、`docker compose config`、干净 Linux 重建、镜像层内容检查。F8 的 context 行为仍为未执行。
- 未删除本地缓存：`src/**/__pycache__`、`.venv`、`.pytest_cache`、`.test-runs` 均保留原状。未执行应用导入、pytest、构建、网络或 Git index 操作。
- 本文件未登记自身 SHA-256：文档自哈希无法在写入后自包含，冻结后的文档 hash 由主会话在交付消息中记录。

### 本次冻结 hash

| 文件 | SHA-256 |
| --- | --- |
| [api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1) | `F5D289EB6CD40DFF4141937CC1DD7A794024A7BAD5DF79318D1B1F93AD9FA3AE` |

该值取代上文表格中 `4185b228...` 的旧冻结值；旧值仍如实保留为上一轮冻结时的字节指纹。Git HEAD 仍为 `a52ae3090948e7eeea6df87590f15ce35351d247`，本轮无提交、推送或远端同步。

交付后 F8 冻结并释放这两份文件的唯一写入，等待主会话安排独立静态复核与后续真实构建门。

### 附录：错误路由草案原文（历史保留，非当前生效规则）

以下 42 行是错误路由实例写入的草案原文，按用户要求保留内容与 hash 历史。它**不是** DeepSeek 交付，也**不是**当前生效规则；实际规则以上文分组和 [api.Dockerfile.dockerignore](/E:/aaa-project/rag/deploy/api.Dockerfile.dockerignore:1) 为准。

```text
# BuildKit Dockerfile-specific ignore list: keep the backend context limited to
# declared artifacts. The developer virtualenv, test runs and local caches must
# never be sent to the builder or copied into the image.
*
!pyproject.toml
!uv.lock
!.python-version
!alembic.ini
!src/
!src/**
!migrations/
!migrations/**

# Re-inclusion above is limited to source and migration files. Keep developer
# caches, generated bytecode, local environments and private key material out
# of the API build context even when they exist below those directories.
**/__pycache__/
**/__pycache__/**
**/*.py[cod]
**/.env
**/.env.*
!**/.env.example
!**/.env.sample
!**/.env.template
**/*.pem
!**/*.example.pem
!**/*.sample.pem
**/*.key
!**/*.example.key
!**/*.sample.key
**/*.p12
**/*.pfx
**/*.jks
**/*.keystore
**/.pgpass
**/pgpass.conf
**/secrets/**
**/credentials.json
**/credentials.yaml
**/credentials.yml
**/*-credentials.json
**/service-account*.json
```

提交收尾说明：上文局部hash属于对应静态交付/复核时点。其后仅清理少量源码/配置/文档的单个EOF空白行，字节前缀一致性已记录；原始wire输入保持原字节。最终源码与Git规范化内容hash以 [准备来源快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-preparation-source-hashes.json:1) 为准，EOF前后证明见 [收尾证据](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-eof-normalization.json:1)。这些均不构成任何运行通过。
