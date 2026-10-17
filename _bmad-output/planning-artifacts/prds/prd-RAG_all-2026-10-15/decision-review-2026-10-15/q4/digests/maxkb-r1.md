# MaxKB 固定提交窄证据摘要（Q4 / R1）

- 对象：官方 `1Panel-dev/MaxKB`，固定 SHA `0fa9a0dae8850c1878f087f0d81c974c1d424b06`。
- 取证方式：本轮实际读取官方提交树页面与原始源码；GitHub 树 API 限流、网页抓取工具 Cache miss 后，使用 Python urllib 读取官方 GitHub HTML/raw 原文。
- 边界：只核对前端、文件访问路径、部署与运行记录；以下均为源码声明，未安装、构建或启动服务，未验证运行效果。

## F1：前端声明使用 Vue、TypeScript、Vite 和 Element Plus

前端依赖清单声明 Vue `^3.5.13`、Element Plus `^2.13.5`，开发依赖含 TypeScript `~5.8.0`、Vite `^6.2.4`；脚本以 Vite 启动/构建并调用 `vue-tsc --build`。Vite 配置实际注册 `vue()`、`vueJsx()` 插件。版本号是该提交的依赖约束，不能视为已解析安装版本。

- source：[package.json](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/ui/package.json#L6)，范围 6–15、34、57、73–89；[vite.config.ts](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/ui/vite.config.ts#L88)，范围 88–94。
- publisher：1Panel-dev/MaxKB；pub_date：未标；accessed：2026-10-15；confidence：medium（单一官方源）；class：implementation-declaration / frontend。
- 本地摘录：[package.json 导入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/maxkb/ui__package.json.md)；[Vite 配置导入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/maxkb/ui__vite.config.ts.md)。

## F2：开发服务器单独转发 OSS 文件访问与取 URL 路径

Vite 的开发服务器代理表为包含环境基础路径的 `oss/file/` 两种路径模式，以及 `oss/get_url/` 模式配置了 `http://127.0.0.1:8080` 目标，并开启 `changeOrigin`；该代理表被传给 `server.proxy`。这只能证明开发时的文件访问转发配置，尚不能确认后端文件存储介质或文件持久化行为。

- source：[vite.config.ts](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/ui/vite.config.ts#L63)，范围 63–75、95–101。
- publisher：1Panel-dev/MaxKB；pub_date：未标；accessed：2026-10-15；confidence：medium（单一官方源）；class：implementation-declaration / file-access-routing。
- 本地摘录：[Vite 配置导入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/maxkb/ui__vite.config.ts.md)。

## F3：容器声明持久卷、构建标识；启动脚本准备日志目录

Dockerfile 包含前端构建阶段，同时运行普通前端和 chat 前端构建；最终镜像暴露 8080、声明 `/opt/maxkb` 为卷，并以 `start-all.sh` 为默认命令。`MAXKB_VERSION` 环境变量组合镜像标签、构建时间和 GitHub 提交标识。另一个已读启动脚本会创建 `/opt/maxkb/logs` 并设置 700 权限，最后运行 `main.py start`。这些证据说明部署声明和日志目录准备；未核对日志写入、轮转、保留期、监控或 `start-all.sh` 的调用链。

- source：[Dockerfile](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/Dockerfile#L1)，范围 1–7、27–42、54–57；[start-maxkb.sh](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/start-maxkb.sh#L3)，范围 3–11、26。
- publisher：1Panel-dev/MaxKB；pub_date：未标；accessed：2026-10-15；confidence：medium（单一官方源）；class：implementation-declaration / deployment-runtime-records。
- 本地摘录：[Dockerfile 导入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/maxkb/installer__Dockerfile.md)；[启动脚本导入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/maxkb/installer__start-maxkb.sh.md)。

## 取证边界记录

本轮共读取六个源码/构建文件。除上述四个有实质内容的文件，还读取了 [oss/models.py](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/oss/models.py#L1) 与 [oss/views.py](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/oss/views.py#L1)：两者均仅三行、为导入和占位注释。因此不据它们推导存储实现。对应导入保存为 [models 占位摘录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/maxkb/apps__oss__models.py.md) 和 [views 占位摘录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/decision-review-2026-10-15/q4/imports/maxkb/apps__oss__views.py.md)。

另实际读取固定 SHA 的 README 部分行，未用于新增核心事实。按委托本轮复读既有 [LICENSE 导入](/E:/aaa-project/rag/_bmad-output/planning-artifacts/research/technical-document-parsing-2026-10-15/imports/implementation-r1/MaxKB/LICENSE.md)，仅记录复读，不据该既有导入新增许可结论。
