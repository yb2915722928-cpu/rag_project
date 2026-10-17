# M3 · 首轮 TR 证据与边界

访问／复读：2026-10-15。项目需求只作为约束。官方固定源码为单一发布者证据，置信度 medium；没有安装、执行备份或恢复产品，也没有证明其生产效果。已有带来源的固定快照在本轮实际复读；新增官方源码由 GitHub connector 在指定 SHA 取回，必要内容保存在本文件。PG 文档为本轮实际打开的官方指南。首轮覆盖问题后停止，不扩查产品全貌。

## WeKnora：数据库安全状态与独立文件卷

发布者 Tencent；SHA `a37a1bc51ad85d096df341f6d3a098f60d586f52`；commit 日期本轮未另核。

| ref | 本轮实际核到的事实 | 官方固定来源／可复读快照 |
|---|---|---|
| W1 | Web JWT 验签后还读取持久 token，拒绝不存在／已撤销记录，再读用户并拒绝非 active；停用账号在同一 DB 事务中更新 is_active 并撤销该用户 token。因而恢复旧 DB 会恢复旧安全事实，这一后果为本轮推论。 | [ValidateToken](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L1285)，范围1285–1344；[停用事务](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/repository/user.go#L235)，范围235–275；本轮复读[service 快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/imports/weknora/internal/application/service/user.go:1285)、[repository 快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/imports/weknora/internal/application/repository/user.go:235)。 |
| W2 | 程序 key 按 hash 查 repository，检查 RevokedAt 与绝对到期时间；不能从原 token 能验签推定当前授权。 | [AuthenticateAPIKey](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/tenant_api_key.go#L86)，范围86–103；本文件下方保存本轮取回的判断片段。 |
| W3 | Compose 分开挂载 data-files 与 postgres-data，并挂载配置；默认 local 存储路径为 /data/files。单独 PG dump 不能据此算作应用文件、配置备份。 | [Compose](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docker-compose.yml#L47)，范围47–50、221–226、543–551；本轮复读[Compose 快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/weknora/docker-compose.yml.md:52)，源码行号＝本地行号−5。 |

W2 本轮固定源码片段（不含真实 key）：

```go
key, err := s.repo.GetAPIKeyByHash(ctx, hashTenantAPIKey(token)) // L91
if err != nil { return nil, err }
if key.RevokedAt != nil { return nil, apprepo.ErrTenantAPIKeyNotFound } // L95
if key.ExpiresAt != nil && time.Now().UTC().After(key.ExpiresAt.UTC()) { // L98
    return nil, apprepo.ErrTenantAPIKeyNotFound
}
```

## MaxKB：DB key、cache 登录态与持久卷声明

发布者 1Panel-dev；SHA `0fa9a0dae8850c1878f087f0d81c974c1d424b06`；commit 日期本轮未另核。

| ref | 本轮实际核到的事实 | 官方固定来源／可复读快照 |
|---|---|---|
| K1 | 用户 token 要求 cache 存在，再查 DB 用户 active 与密码是否和 cache 快照一致；登录入口按 DB 密码及 is_active 判断，并新建 cache token。因此即使清空 cache，旧 DB 中被恢复为 active 的旧密码仍可能重新登录；这是本轮推论，不是已运行攻击。 | [UserToken](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/auth/handle/impl/user_token.py#L300)，范围300–319；[登录](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/users/serializers/login.py#L149)，范围149–180；本轮复读[认证快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/imports/maxkb/apps/common/auth/handle/impl/user_token.py:300)、[登录快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/imports/maxkb/apps/users/serializers/login.py:149)。 |
| K2 | 应用 API key 按 secret_key 查 DB，检查 is_active、is_permanent 与 expire_time；这不是本项目的用户只读 Bearer 设计。 | [ApplicationKey](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/auth/handle/impl/application_key.py#L18)，范围18–29；本轮复读[key 快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q1/imports/maxkb/apps/common/auth/handle/impl/application_key.py:18)。 |
| K3 | Dockerfile 声明 /opt/maxkb 卷；默认启动按 DB／Redis host 判断是否启动本地组件。PG 启动脚本创建 /opt/maxkb/data/postgresql；Redis 脚本设置数据目录、RDB/AOF。这里只证明路径与持久化配置，不证明整个卷的在线复制一致或完整可恢复。 | [Dockerfile](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/Dockerfile#L32)，范围32–42、54–57；[start-all](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/start-all.sh#L12)，范围12–31；[PG](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/start-postgres.sh#L3)；[Redis](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/start-redis.sh#L17)，范围17–38；本轮复读[Dockerfile 快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/maxkb/installer__Dockerfile.md:29)。 |

K3 本轮新取回原文摘录：

```text
start-all.sh L12: if [ "$MAXKB_DB_HOST" = "127.0.0.1" ]; then
L14: /usr/bin/start-postgres.sh &
L20: if [ "$MAXKB_REDIS_HOST" = "127.0.0.1" ]; then
L22: /usr/bin/start-redis.sh &
L29: /usr/bin/start-maxkb.sh &
start-postgres.sh L3: mkdir -p /opt/maxkb/data/postgresql
L4: docker-entrypoint.sh postgres -c max_connections=${POSTGRES_MAX_CONNECTIONS} -c jit=off
start-redis.sh L24: dbfilename dump.rdb
L26: appendonly yes
L28: appendfsync everysec
L34: dir /opt/maxkb/data/redis
```

## PG17：恢复点边界

发布者 PostgreSQL Global Development Group；页面未标独立发布日期；访问2026-10-15；confidence=medium（官方单源），class=机制。

| ref | 核到的机制与限定 |
|---|---|
| P1 | [SQL dump §25.1](https://www.postgresql.org/docs/17/backup-dump.html)明确 pg_dump 是开始执行时的数据库一致快照；§25.1.2 说明单库 dump 不含 global roles／tablespaces，需另处理 globals，多库各自 dump 也不保证同时快照。 |
| P2 | [Continuous Archiving／PITR §25.3](https://www.postgresql.org/docs/17/continuous-archiving.html)说明须有基准备份及连续 WAL，可停在所选时点，恢复的是整个集群；WAL 不恢复手工配置文件变化。推论：PITR 不会自动补回目标点之后的安全变更，也没有跨数据库外原件／供应商任务的事务保证。 |

本轮文档提取：pg_dump 的快照边界在“开始执行”；PITR 的边界是所选 target，依赖从 base backup 起连续可用的 WAL。它们支持选择恢复点，并不支持“恢复旧点但自动保留之后全部撤权／删除”。未以 PG 文档声称本项目已配置 WAL 归档或 PITR；本项目仍选停写匹配备份。

## 未证范围与停止理由

本轮实际读取两项目上述认证／部署路径，并读取指定 SHA 的完整 Git tree（truncated=false）：[WeKnora tree](https://api.github.com/repos/Tencent/WeKnora/git/trees/a37a1bc51ad85d096df341f6d3a098f60d586f52?recursive=1)、[MaxKB tree](https://api.github.com/repos/1Panel-dev/MaxKB/git/trees/0fa9a0dae8850c1878f087f0d81c974c1d424b06?recursive=1)。按文件名 backup／restore 未定位到应用备份脚本；没有因此断言官方其他文档或其他版本不存在备份能力。

本轮未证：两项目从旧点恢复后自动补回停用／撤权／删除、库外文件匹配、外部费用恰好一次、上游任务自动安全恢复、完整恢复演练。持久卷声明、token 检查代码均不能填补这些保证。首轮证据已足够支持“额外恢复放行契约”的 TS，剩余是本项目实施验收，不为模板再搜。
