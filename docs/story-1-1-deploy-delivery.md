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

