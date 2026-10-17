---
title: 'Story 1.1 A2 真实 PostgreSQL 测试基础设施'
status: done
route: dispatch
baseline_commit: 0b576b65d3824e7f4319c39c38e80398caf08fb8
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-deploy.md
  - E:/aaa-project/rag/backend/tests/conftest.py
completion_record: E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-snapshot-2026-10-18.md
---

## Intent

为当前AC2的六项PG集成和两项worker PG测试提供真实隔离环境，不等待前端，也不引入后续业务表。

## 唯一归属与调用时段

仍由Mencius独占deploy及其官方镜像交付记录；不改backend/contracts/frontend或Git。Netcatty terminal在整个chat互斥，须主控明确授予远程时段后调用；不得使用后端者专属terminal。该时段结束后报告作业和资源并释放，长任务用start，不长时间占用execute/poll。

## Tasks & Acceptance

- [x] Given已核官方digest的原始镜像，when核对完整inspect与实际版本，then分别记录index/platform/config、Engine Id及完整层，PostgreSQL必须18.6、vector扩展实际0.8.7。现有腾讯云官方缓存只作传输，发布方仍为官方repo；保留实际缓存来源，不谎称官方直连，不改全局mirror。
- [x] Given项目专属临时PG，when创建和运行，then新容器/网络/数据目录明确归属rag-story-1-1，数据在 `/opt/rag-story-1-1` 新子目录的Linux本地文件系统；不覆盖旧绑定目录，不用对象存储存DB，不公开数据库端口。测试连接仅允许本机回环，不能形成额外生产服务。
- [x] Given基础数据库，when预置vector扩展并查询server_version_num/extversion，then提供真实值和有限授权的测试连接；本Story已授权在该隔离库内创建/删除测试fixture自己的随机schema。无正式生产vector(D)/ANN或后续业务表，测试不创建/删除共享扩展。
- [x] Given后端开发者，when交接连接，then仅交受限权限文件路径或进程环境读取方式，密码/完整DSN不入argv/日志/仓库/聊天；说明 `RAG_TEST_DATABASE_URL` 与 `RAG_TEST_ALLOW_SCHEMA_CREATE=1` 的安全加载方式，禁止打印秘密。
- [x] Given初始化与操作，when交付，then记录版本/文件系统/权限/源digest、真实命令和副作用；不替代后端八项测试，不宣称四服务或独立验证通过。

## 交付

报告容器标识、监听范围、凭据文件路径（不含值）、准确版本与原始证据、当前作业和清理归属。证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1/postgres-test-environment`。只管理本任务新建资源，保留既有宿主目录及全部历史证据；后端测试结束后由主控协调释放临时服务。
