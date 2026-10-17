---
title: Story 1.1 C0 前端规范前置记录
status: preflight-complete
checked_at: 2026-10-17
spec: _bmad-output/implementation-artifacts/spec-1-1-frontend-preflight.md
---

# Story 1.1 C0 前端规范前置记录

本文件是 Story 1.1 前端实现前的强制规范实查与环境核验记录。仅做前置记录：不初始化前端、不写平行业务类型、不安装构建依赖。后续 C 实现由主会话在 B（OpenAPI/JSON Schema/TypeScript 导出）交付后另发短规格派发，可复用本记录。

## 1. 已批栈与当前工作区

- 当前工作区尚无 `frontend/**`；本记录是前端编码前的唯一前置交付物。
- 已批栈（来自技术核验 seed 与 UX 交付契约，为待运行核验对象，不冒充新构建结果）：
  - 脚手架：Vue 官方 `create-vue` 3.23.0，选择 TypeScript / Router / Pinia。
  - 版本 seed：Vue 3.5.44、Vite 8.3.4、TypeScript 6.0.3（模板约束 `~6.0.0`）、Vue Router 5.4.0、Pinia 4.0.2、Element Plus 2.14.7。
  - 构建工具链：Node 24.22.0（模板 engines 要求 `^22.18.0 || >=24.12.0`）。
- 视觉服从已批 DESIGN：浅色模式、系统字体栈、Element Plus 组件体系、扁平色 token。不引入第二套组件库、远程品牌字体或主题切换。
- 详细 seed 证据见 [technology-evidence.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md) E2 节；视觉契约见 [DESIGN.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md)。

## 2. GitHub 规范实查（查阅日期 2026-10-17）

本轮实际打开以下官方仓库/文档中的具体文件并记录内容摘要；URL、文件、版本标识均按所读原文记录。

### create-vue（脚手架）

- URL: https://github.com/vuejs/create-vue/tree/v3.23.0
- 所读文件：`README.md`、`package.json`（tag `v3.23.0`）
- 实际读到内容：v3.23.0 于 2026-09-30 发布；脚手架仍在交互中提供 TypeScript、JSX、Router、Pinia、Vitest、端到端、ESLint、Prettier 等可选项；`package.json` engines 声明 `"node": "^20.19.0 || >=22.12.0"`（脚手架自身运行要求），bin 为 `create-vue`。
- 拟采用规则：后续 C 用非交互方式以 `create-vue@3.23.0` 精确版本生成骨架，显式选择 TypeScript + Router + Pinia，不选与本 Story 无关的多余特性；脚手架自身 Node 要求（`^20.19.0 || >=22.12.0`）与生成产物的 Node 要求（`^22.18.0 || >=24.12.0`）是两个不同约束，统一由 Node 24.22.0 同时满足。

### Vue Router

- URL: https://github.com/vuejs/router/tree/v5.4.0
- 所读文件：`packages/router/package.json`、`packages/router/src/router.ts`、`packages/router/src/types/index.ts`
- 实际读到内容：v5.4.0（2026-09-28）。`createRouter` 要求显式 `history`（`createWebHistory` / `createWebHashHistory` / `createMemoryHistory`）与 `routes`；`RouteRecordRaw` 为单一路由记录联合类型（含 redirect 记录变体），`RouteLocationRaw` 为字符串或对象形式；Router 5 属新主版本，API 以 v5.4.0 源码为准，不沿用 Router 4 记忆。peer 为 `vue ^3.5.x`（所读 package.json 中 peerDependencies）。
- 拟采用规则：后续 C 以 `createRouter({ history: createWebHistory(), routes })` 创建实例，`RouteRecordRaw[]` 显式类型化；Story 1.1 前端只做骨架/健康状态，路由表仅含占位骨架路由，不提前身份、文档或问答业务路由。

### Pinia

- URL: https://github.com/vuejs/pinia/tree/v4.0.2
- 所读文件：`packages/pinia/package.json`、`packages/pinia/src/createPinia.ts`、`packages/pinia/src/store.ts`、`packages/docs/introduction.md`
- 实际读到内容：v4.0.2（2026-09-30）。`createPinia()` 创建实例；`defineStore` 支持 Options 与 Setup 两种写法（`defineStore(id, { state, getters, actions })` 或 setup 函数）；TypeScript 推断在两种写法下均成立。`package.json` peerDependencies 含 `vue ^3.5.11`、`typescript >=5.6`、`@vue/devtools-api ^8.1.5`，且 `peerDependenciesMeta` 中 `@vue/devtools-api` 未标 optional（`typescript` 标 optional）。
- 拟采用规则：后续 C 在解析依赖时必须解析并锁定 `@vue/devtools-api@^8.1.5` 这一非 optional peer，不能删除后声称模板可构建；TS 版本 6.0.3 满足 `>=5.6`；Story 1.1 骨架期 store 仅承载健康状态，不写业务 store。

### Element Plus（本轮已实查固定 2.14.7 GitHub 源）

- URL: https://github.com/element-plus/element-plus/tree/2.14.7（固定 tag `2.14.7`；release 页 https://github.com/element-plus/element-plus/releases/tag/2.14.7 已于 2026-10-16 核对并记录在 [DESIGN.md](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md)）
- 所读文件（2026-10-17，经只读 Invoke-WebRequest 取得，HTTP 200）：
  - `package.json`（monorepo 根）：`packageManager: pnpm@12.8.1`，engines `node >= 22.13.0`；构建/主题脚本经 pnpm workspace；直接依赖含 `@element-plus/icons-vue ^2.3.2`、`async-validator ^4.2.5`、`dayjs ^1.11.20`、`lodash-es`、`normalize-wheel-es` 等。
  - `packages/element-plus/package.json`（实际发布包）：`peerDependencies` 仅 `vue ^3.3.7`（Vue 3.5.44 满足）；`main: lib/index.js`、`module: es/index.mjs`、`types: es/index.d.ts`，exports 提供 es/lib 双入口；`style: dist/index.css`；`sideEffects` 含 `theme-chalk/**/*.css` 与组件样式路径（按需引入/样式 tree-shaking 边界）；MIT 许可。
  - `packages/theme-chalk/src/common/var.scss`（固定 tag，非 dev 分支）：默认 `$colors` base 值 primary `#409eff`、success `#67c23a`、warning `#e6a23c`、danger/error `#f56c6c`、info `#909399`；text primary `#303133`；border-radius base `4px`；font-size base `14px`；变量经 `getCssVar` 映射到 `--el-*` CSS 自定义属性。
- 拟采用规则：主题定制通过覆盖 `--el-*` CSS 变量实现，将 DESIGN 交付 token（主操作 `{colors.action}` `#1D6CC0`、加深成功/危险/警告文字等）绑定到该变量层；DESIGN 已核算 EP 默认蓝 `#409eff` 白底对比约 2.78:1 不达 AA，故不直接用默认主色承载普通文字按钮/链接。不改组件库源码、不引入第二套组件库；依赖安装与锁版本留待 C 实施，以真实 lockfile 证据为准。

## 3. 模板、依赖范围与 peer 核验

以下均按所读官方文件原文记录；本阶段只读取，不安装。

- create-vue 3.23.0 base 模板（https://raw.githubusercontent.com/vuejs/create-vue/v3.23.0/template/base/package.json，亦见 technology-evidence E2）：`vue ^3.5.40`、`vite ^8.1.5`、`@vitejs/plugin-vue ^6.0.8`，Node engines `^22.18.0 || >=24.12.0`。
- TS 模板（.../template/config/typescript/package.json）：`typescript ~6.0.0`、`vue-tsc ^3.3.7`。
- Pinia 模板（.../template/config/pinia/package.json）：`pinia ^4.0.2`。
- Pinia 4.0.2 精确包 peer：`vue ^3.5.11`、`typescript >=5.6`（optional）、`@vue/devtools-api ^8.1.5`（非 optional）。
- 版本关系核对：Vue 3.5.44 满足 `^3.5.40` 与 Pinia `^3.5.11`；Vite 8.3.4 满足 `^8.1.5`；TS 6.0.3 满足 `~6.0.0` 与 Pinia `>=5.6`。依赖锁与传递依赖在 C 实施时以 `npm install` 实际锁文件为准，本表不冒充锁文件。

## 4. Node 24.22.0 官方工件与 hash 来源

- 官方版本表 https://nodejs.org/en/about/previous-releases 列 Node 24 为 LTS（Krypton），Latest LTS 显示 24.22.0；满足 create-vue 模板 `^22.18.0 || >=24.12.0` 与脚手架 `^20.19.0 || >=22.12.0`。
- hash 来源已实际取得（2026-10-17，只读 Invoke-WebRequest，HTTP 200）：`https://nodejs.org/dist/v24.22.0/SHASUMS256.txt`，随 `https://nodejs.org/dist/v24.22.0/` 目录工件发布。与目标 Netcatty Linux 构建主机相关的 SHA-256 校验值：
  - `cc2f601cee82d9a5a233302fe307abc600727035fd7d2c3a3571755989e95008  node-v24.22.0-linux-x64.tar.xz`
  - `28ea0a438de9a13bd7891fd758eee6c7819ee8af5442dfd8d45bd65e56d4228c  node-v24.22.0-linux-x64.tar.gz`
  - `fef00bb4d36e1c50104a9775a10359beee98f162b4104dd12472c75065c6a143  node-v24.22.0-linux-arm64.tar.xz`
  - `b7e7991d5407815adfa74a2a9cd4db683552c8ce32ff4a295c22e972849c3f5d  node-v24.22.0-linux-arm64.tar.gz`
- 本轮环境核验状态：SHASUMS 文本已取得并记录如上；未下载、未验签、未安装任何构建依赖。后续 C 实施时在 Netcatty Linux 主机先确认架构（x64/arm64 择对应行），下载后对照上述官方值实测 hash 并记录实际工件；不一致或不可得不静默换版。
- Node 仅用于开发/CI 构建，不作为第五个生产服务。

## 5. B 契约导出依赖（等待项）

- 后续 C 需要从 B 导出的准确接口：由后端 `rag_app.contracts.public` 的 `PUBLIC_MODELS` 生成的 OpenAPI、JSON Schema 与 TypeScript 类型（含正负样例）。
- 当前状态：B0a 公共 DTO 已交付（见 [story-1-1-contract-models-delivery.md](/E:/aaa-project/rag/docs/story-1-1-contract-models-delivery.md)），覆盖 `AcceptedResponse`、`CompletedResponse`、`FailedResponse`、`OperationResponse`、`RetrievalResponse`、`PublicError` 等公共模型；但 B 分段的 OpenAPI/JSON Schema/TypeScript 导出尚未交付（工作集记录：先补 C1/C2/H 后端真源，再由复杂实现者独占 `contracts/**` 导出）。
- 因此本前置阶段明确等待：前端不自写业务类型、不写平行 DTO；Story 1.1 前端范围仅为骨架/健康状态，不提前身份、文档或问答业务。

## 6. 阻塞与遗留

- GitHub 规范实查四项（create-vue、Router、Pinia、Element Plus 固定 2.14.7）与 Node 24.22.0 官方 SHASUMS 均已取得并记录如上，C0 前置查询无未决来源阻塞。
- 仍待 C 实施阶段完成（本阶段按规格不执行）：Node 24.22.0 在 Netcatty Linux 的架构确认、下载与实测 hash 验签；`create-vue@3.23.0` 脚手架生成与依赖锁（含 `@vue/devtools-api ^8.1.5` peer）；前端骨架编码。
- 未初始化前端、未安装依赖、未创建 `frontend/**`；远程 C 工作目录预留 `/opt/rag-story-1-1/frontend-work`，未创建未修改。B 的 OpenAPI/JSON Schema/TypeScript 导出未交付，前端继续等待，不写业务类型。
- 证据归档（`/fileOfRag/testOfRAG/metadata/story-1-1`）由主会话在验收阶段统一安排。
