# Story 1.3 当前工作集

状态：**待唯一新Amelia接手**，无实现认领/应用修改。前置1.2已done/passed，唯一owner/交接ID看[relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)；不重开1.1/1.2。

## 目标与分工

原[Story1.3四AC](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:210)：可暂停传输下共享RPS/完整分钟TPM，send_open持续全额占用；真实停发/FD与IPC关闭/旧grant销毁后才封口并保留完整窗口；本地gate和账号/用途池同UoW一次领还；四档远端等待可重叠、本机重阶段≤1、poll公平且原2h期限不刷新。假件不证明真实账号或4GB。

主会话6.1Sol/max做公共契约/拆分/协调，不写应用/测试/部署。全部后端/RAG `zayuapi/deepseek-v4.1-flash` 默认；独立Step5默认；审查新6.1Sol/medium；前端若确需才Kimi。用bmad-build，规格≥1600 tokens自动拆分，不删父AC。

## 已过基础与环境

- [1.2验收](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-final-acceptance.json:1)四AC全过，旧实例全部关闭；最终实现源0162cb52，E受测d6e8a0d，稳定基础96c/af6/784分别保留来源。新文档提交不重标运行PASS。
- 官方netcatty-external MCP已修复，先get_environment确认实际session；最近94bede36-0e0e-444c-a8b7-f332d2542962和1eaffce6-3c45-45cb-84bd-18bd6fc84ea9可执行。原0d未恢复不探。
- Linux120.53.251.166；精确3.12.8/PG18.6/vector0.8.7/uvicorn0.37/locked sync已有证据。开发源先GitHub/Gitee同commit，服务器只Gitee固定提交，前后核Git/hash，禁止server覆盖或本地跑项目。
- 活动根/opt/rag-story-1-2/repo-fixed及independent/repo，ext4；PG秘密只source /opt/rag-story-1-1/postgres-test/secrets/test-database.env，不打印/猜角色；容器test网络rag-story-1-1-test、postgres-test:5432。材料/fileOfRag/testOfRAG/metadata。
- 1.2正常/负例容器已stop/exited保留，epoch已显式初始化。1.3用自己的资源/schema，不重建/旋转/删除1.1/1.2资源。

## 最新推进规则

可以借鉴WeKnora/MaxKB源码并记录实际采用来源。用户明确反对过度防御：小范围一次派发，核模型/归属后连贯完成实现、必要测试、独立验证与一次相关审查，统一验收；不反复READY/确认/长报告等待，不重复未变环境/hash/已过测试。独立验证可复用专属资源，实际结论由独立者核验，不为形式重建整套环境。仅实际失败/实质改动触发相关回归。

## 接手与按需回读

先合并一次实际模型/同项目会话/relay/认领诊断，匹配唯一交接后回写接手，再读1.3原AC、架构C8/R1/R2/R7-R01、UX补充R01与相关现代码。公共接口或真实回归依赖变化时才读1.2完整材料，不重载全部历史。当前无已核阻塞、无实现子任务，不重复派发。
