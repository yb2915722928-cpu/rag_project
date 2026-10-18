---
title: '1.2 D epoch启动接线回归'
type: bugfix
created: '2026-10-18'
status: in-progress
route: dispatch
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

修复新epoch机制引起的已有启动接线遗漏：[Compose](/E:/aaa-project/rag/deploy/compose.yaml:85)没有RAG_EPOCH_CONTROL_FILE，新[Runtime](/E:/aaa-project/rag/backend/src/rag_app/bootstrap/runtime.py:30)在worker启动检查时必拒绝None。原AC1要求缺失隔离，也要求合法配置可重启；不能拿旧1.1镜像健康证明新源码可启动。

## Boundaries & Constraints

只完成当前必要回归：API/worker共用已有独立epoch只读卷/文件配置，提供显式首次维护初始化及DB镜像说明；普通启动/重启只读不轮换，缺失/矛盾仍隔离。复用A的初始化/镜像/检查入口，不复制另一份epoch实现。

不制造S0资格报告、探路命令或新服务，不改1.3/1.4义务。1.5仍汇总完整S0并交隔离探路工具。无需重新验全套1.1前端/gateway/PG生命周期；只验证受影响的新后端启动/重启与隔离，不删除或替换已有1.1资源。

## Tasks & Acceptance

- [ ] 唯一源归属 [compose.yaml](/E:/aaa-project/rag/deploy/compose.yaml:1)：API/worker传同一准确RAG_EPOCH_CONTROL_FILE，默认落已有`/var/lib/rag/epoch`只读挂载内。
- [ ] [api.Dockerfile](/E:/aaa-project/rag/deploy/api.Dockerfile:1)归D：修真实发现的COPY继承0700/0600导致服务UID65532读不到源码。镜像内归一化可读/可遍历权限，仍禁组/其他写；以最终UID验证导入及配置/迁移读取，不用root运行或改宿主源码权限代替。
- [ ] 唯一文档归属 [epoch部署说明](/E:/aaa-project/rag/docs/story-1-2-epoch-deploy.md:1)：显式首次维护步骤、服务UID/目录权限、迁移/镜像初始化/检查顺序；复用现有A函数，不另造资格CLI，不把秘密放argv/log。
- [ ] 按主控时段仅在Linux，以Gitee固定提交/源码hash构建或复用同源码后端镜像，运行项目专属API/worker最小启动与重启，核epoch/镜像不变；缺失/矛盾新worker有限失败，不实际供应方外发。

## Acceptance Criteria

- Given 已迁移PG与显式初始化的独立epoch，When 新源码API/worker使用同配置启动/重启，Then 可运行且不轮换/重建控制值，secret不泄露。
- Given 缺失或矛盾控制值，When 新worker启动，Then 保持隔离、有限失败，不自动初始化或用DB补造。
- Given 既有1.1资源，When 本回归执行，Then 只创建/使用本Story专属测试资源/独占schema，不清旧容器/目录/桶；证据归档正确桶目录。

</frozen-after-approval>

## Code Map

复用 [epoch_control.py](/E:/aaa-project/rag/backend/src/rag_app/adapters/epoch_control.py:1) 的initialize_epoch_control/mirror_epoch与运行检查；A独占后端代码，D不得改它。现有后端镜像/锁/部署安全约定继续有效。

## Implementation Notes

由尚未关闭的B实现者DeepSeek默认接手两个文件，不兼任独立验证。首阶段只读并5行内回复接线/初始化方案，等待D_MODEL_RELEASE后写；不用自行查模型、不派新角色。代码先冻由主控发布，Netcatty时段由主控统一分配；当前A持有terminal，D不能调用。

主控已核B实际DeepSeek/max默认路由，采纳预读方案：两服务同变量，默认 `/var/lib/rag/epoch/epoch-control.json`；首次维护临时以服务UID在RW目录0700初始化，之后epoch目录恢复0550、文件0400/65532，普通只读挂载满足既有preflight。部署说明须清楚分开维护与普通启动，不覆盖已有控制记录。A服务器草稿覆盖检出已停用；所有D实测等主控提供新的干净Gitee固定检出，不能直接修改服务器源。

原B/D续跑长时间无新工具输出，主控已关闭并释放写入/RPC；既有两文件均固定96c64fb，见[接替快照](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-ed-successor-source-snapshot.json:1)。新同模型DeepSeek仅接尚未执行的运行回归：先只读ready，等D_SUCCESSOR_MODEL_RELEASE核模型/给RPC。复用既有测试PG环境文件（setup.sh第162行指定，root0400）与rag-story-1-1-test网络、postgres-test:5432；不猜rag角色/pgpass，不打印秘密，不重探旧DockerHub阻塞。先看Story1.2专属远程目录/已有后台进程，避免重复构建；旧1.1基镜像构建可复用缓存。代码96c不改，任何新失败先报主控，不server覆盖。

2026-10-18 新D Nash已核前缀DeepSeek/max默认。d6新镜像build成功，但服务UID导入失败；实见root0700源码目录/0600文件。主控据当前启动缺陷放行上述Dockerfile窄修，覆盖“代码96c不改”的旧指令；新源码仍先双远端发布，再Gitee固定提交构建回归。A/E/C保持冻结。

## Verification

只跑当前启动接线必要回归并留commit/hash/命令/退出码/epoch不变证据；最终证据放 `/fileOfRag/testOfRAG/metadata/story-1-2/epoch-deploy`，活动目录为本地FS `/opt/rag-story-1-2`。文档归档不阻塞其他独立工作。
