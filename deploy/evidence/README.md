# deploy/evidence 历史说明

这些 JSON 是 2026-10-17 较早修订在远程 Linux 与本地 Windows 上取得的**历史**观测。它们对应的文件 hash、compose 结构、preflight 输出均属于当时版本，不适用于当前修订。

当前修订只做了本地静态修改与文件阅读，**没有**执行任何 Linux 构建、`docker compose config`、preflight、容器启动或真实 PostgreSQL 验证；当前修订的 hash 见 [Story 1.1 D 交付记录](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:1)。

不要把本目录中的旧 `final-static-verification.json` 当作当前 `compose.yaml`、`nginx.conf`、`preflight.py` 的通过证据。
