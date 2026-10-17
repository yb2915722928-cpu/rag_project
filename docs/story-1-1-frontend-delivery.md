---
title: Story 1.1 C 前端基线交付记录
status: complete
updated: 2026-10-18
spec: _bmad-output/implementation-artifacts/spec-1-1-frontend-baseline.md
baseline_commit: dd44834383de2bd9af9768a6ecc7fe2c48427eff
---

# Story 1.1 C 前端基线交付记录

本文档是 Story 1.1 前端基线（Vue 骨架 + 健康状态页 + 可复现构建）的正式交付记录，供独立验证者与审查者直接读取。规范实读与依赖锁定证据见 [story-1-1-frontend-standards.md](/E:/aaa-project/rag/docs/story-1-1-frontend-standards.md:1) 第 7 节。

## 1. 交付范围与归属

- 实现者：前端实现会话，实际路由 `kimi/kimi-k3 / max`（派发未传强度，主控核对 turn_context 后写入 relay）。
- 独占文件归属：`frontend/**`、`docs/story-1-1-frontend-standards.md`、本文件。未修改 backend/contracts/deploy，未执行 Git 提交/推送（均由主控统一发布）。
- 源码基线：`dd44834383de2bd9af9768a6ecc7fe2c48427eff`（GitHub/Gitee 两远端一致）。历史阶段：骨架 `abcd79b`、锁与收窄 `b6e22bc`、4 文件修复并入 `dd44834`；服务器侧构建只认最终提交，预备 overlay 证据保留未重标。

## 2. 骨架与健康页

- 官方脚手架：`create-vue@3.23.0`，非交互 `frontend --typescript --router --pinia --vitest --bare`；无模板演示/计数器残留（grep 为零）。
- 路由表仅两条：`/` 到健康状态页，未知路径重定向 `/`；不提前任何业务路由。
- 健康页语义：仅展示前端已加载与同源 `GET /health` 的 HTTP 可达性；页面固定文案明示"接口可达不代表数据库已就绪，也不代表业务功能正常"。成功响应体只要求为 JSON 对象，不消费 payload 字段、不镜像 `HealthStatus` DTO。
- 错误处理：HTTP 非 2xx 显示状态码与 `PublicError.code`（取自生成 [contracts.ts](/E:/aaa-project/rag/contracts/typescript/contracts.ts:1) 的 `FailedResponse.error.code` 包络路径）；永不展示原始错误正文、URL 或内部标识（有测试断言）。5s 超时、网络错误、非法 JSON 对象分别有独立文案；无自动重试；单 flight——新请求 abort 旧请求并以序号围栏丢弃过期结果；加载中按钮 `disabled + loading` 阻止重复触发。
- 可访问性与响应式：DESIGN 浅色 token + Element Plus `--el-*` 绑定；系统字体栈；2px 焦点环 + 2px 偏移；`prefers-reduced-motion` 取消过渡；标签与按钮触达目标不低于 44px；内容面板 `max-width: 720px` 且行内 `flex-wrap`，320/768/1440 CSS px 无全页横溢路径（真实浏览器证据 pending，见第 5 节）。
- 测试：`frontend/src/__tests__/` 共 4 文件 18 用例——`health.spec.ts`（12：单次请求、非 2xx 包络、超时与取消区分、全相位、隐私不泄漏、最新请求权威、abort 后不留 loading）、`HealthView.spec.ts`（3：可达性文案、错误文案无原始正文、手动刷新单次新请求）、`contracts.spec.ts`（2：`@contracts` 别名与双方向类型可用）、`App.spec.ts`（1）。

## 3. Linux 执行记录（Netcatty 主机 120.53.251.166）

- 环境：Ubuntu 24.04 x86_64，`/opt/rag-story-1-1/frontend-work/repo`（本地 ext4）；Node **v24.22.0** 官方工件 `node-v24.22.0-linux-x64.tar.xz`，SHA-256 实测匹配官方 SHASUMS256.txt x64 行（`cc2f601c…5008`，`sha256sum -c` OK），解包于 `/opt/node-toolchain/`；npm **11.19.1**。
- 源码核验：每次构建前 `git checkout` 固定 commit 并以 `sha256sum` 比对关键文件与本地冻结值，全部一致后方执行。
- 最终提交 `dd44834` 正式结果：
  - `npm ci --no-audit --no-fund`：通过（286 包；初次生成锁时为 `npm install`，286 包约 1 分钟）。
  - `npm run test:unit -- --run`（vitest 4.1.11）：**Test Files 4 passed (4)，Tests 18 passed (18)**，约 2.5s。
  - `npm run build`（`run-p type-check build-only`，vue-tsc 3.3.13 + vite 8.3.4）：**通过**，1,598 模块，约 0.9s；唯一提示为单 chunk 1,019 kB 大于 500 kB（Element Plus 全量注册所致），非错误，骨架期不做代码分割，后续 Story 可评估按需引入。
- 依赖与 peer：实际锁定 pinia 4.1.0（其 peer 要求 `@vue/devtools-api ^8.2.1`，实际锁 8.2.1，同时满足我方声明 `^8.1.5`）、element-plus 2.14.7、vue 3.5.44、vite 8.3.4、typescript 6.0.3、vue-router 5.4.0 等，完整表见 standards 第 7.2 节；`@pinia/colada` 为 vue-router 的 optional peer，按官方 meta 不安装。npm 来源为腾讯云内网缓存 `mirrors.tencentyun.com`，完整性由 lock 的 `integrity` 字段保证。
- 过程修复（均只修当前实际问题）：其一，el-button 的 loading 不阻止重复点击，组件补 `:disabled`；其二，测试等待条件不严谨，收紧到结果区渲染；其三，`tsconfig.app.json` 的 `paths` 覆盖 solution 根的 `@contracts/*`，改为 app 与 vitest 两个 tsconfig 各自并列声明。修复流程为本地冻结、主控发布、Gitee 固定检出回归，未在服务器叠应用源码补丁。
- R1 审查修复（独立审查 FCR-1/P2，已闭环）：`fetchHealth` 的 `response.json()` catch 原先吞掉正文阶段 AbortError 与流传输错误，收到 200 头后正文超时会落入 invalid-body 而非 timeout。最小修复：catch 仅将真正 `SyntaxError`（JSON 格式错误）转为 `undefined`，其余异常向外传播复用既有 timeout/network-error/caller-abort 分类；不改公共接口。配套补两条针对用例（200 头后正文超时 → FetchTimeoutError；正文读取期调用方取消 → AbortError，先确认进入 json 再 abort）。冻结文件 hash：[api/health.ts](/E:/aaa-project/rag/frontend/src/api/health.ts:1) `b8d74121…4709a`、[health.spec.ts](/E:/aaa-project/rag/frontend/src/__tests__/health.spec.ts:1) `5041f845…40b67`，已由主控发布为 `25232d0bebc230c35837153b6fd572ff734977aa`（两远端一致）。**Linux 回归已通过（2026-10-18 02:14 UTC+8）**：Gitee 固定检出 25232d0、两文件 hash 核对一致；`npx vitest run src/__tests__/health.spec.ts` **14/14 passed**（原 12 + 新增 2，1.65s）；`npm run build`（含 vue-tsc type-check + vite build）通过（1.08s）。新 dist（服务器 `/opt/rag-story-1-1/frontend-work/repo/frontend/dist/`，hash 清单归档 `dist-25232d0.sha256`）：`index.html 4bd67fe3…e5817f`、`assets/index-AMOFkByE.css 9a485ada…f7ca3a`（不变）、`assets/index-CDataiw2.js fade5263…e9348a`、`favicon.ico db74ab0b…eafd3445`；总计 1,388,509 B。原 dd44834 dist 保留在 `dist-dd44834.sha256`，不重标。

## 4. dist 交付（供 D 四服务）

构建自正式提交 `dd44834`，服务器路径 `/opt/rag-story-1-1/frontend-work/repo/frontend/dist/`，总计 1,388,465 B：

| 文件 | SHA-256 | 大小 |
| --- | --- | --- |
| `dist/index.html` | `70174d6bd99333af16c404c49d316550185166a565e283d7868791385eeb4d72` | 448 B |
| `dist/assets/index-AMOFkByE.css` | `9a485ada3a2f3713c75dea8fc76b4766aeb384a8cea6de0a3116ed27c2f7ca3a` | 364,336 B |
| `dist/assets/index-CrqoaFFe.js` | `ae4aaa9099801a7afd102789d3e219684b32614646418fdd38043ba401473b45` | 1,019,395 B |
| `dist/favicon.ico` | `db74ab0b78338c1f778f8398c45f4103c99aea0e845a3118a7750b4eeafd3445` | 4,286 B |

服务方托管要求：SPA 静态托管，`GET /health` 同源透传到 API 服务，其余路径回退 `index.html`。锁文件：`frontend/package-lock.json` SHA-256 `4b6d69e744af7ddac2255ce8fa9c3cc64cf0d9576ae343fc0b2e60babd8ae4c0`（Git 内与服务器生成值逐字节一致）。

预备证据（不重标为 dd 提交通过，仅留痕）：b6e22bc 加 overlay 的 dist 与 hash 清单在服务器 `/tmp/dist-b6-overlay-preliminary*`，overlay 补丁在 git stash（`b6-overlay: 4 fix files (superseded by dd448343)`）。

## 5. 真实浏览器验收（2026-10-18 01:42–01:43 UTC+8，对真实 gateway）

- 环境：同 Linux 主机回环 `https://127.0.0.1:8443`（自签 TLS，测试浏览器 `ignoreHTTPSErrors`）；官方 Chrome for Testing headless shell 147.0.7727.15（`cdn.playwright.dev` 工件，117,394,312 B，curl 完整下载），playwright-core 1.59.1 驱动；最低系统库补装 9 包（libasound2t64/libatk1.0-0t64/libatk-bridge2.0-0t64/libatspi2.0-0t64/libgbm1/libxcomposite1/libxdamage1/libxfixes3/libxrandr2）。项目测试目录 `/opt/rag-story-1-1/browser-test/`，不属生产依赖。
- 结果（证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1/frontend-baseline/browser/`，含 8 张真实截图、每场景 run.json 与 summary.json）：
  - 320 CSS px：首载 200，`/health` 200，`scrollWidth == clientWidth == 320` 无全页横溢；标题、说明、状态标签、按钮、HTTP 状态与时间全部可见。
  - 768 CSS px：无横溢（768/768）；Tab 聚焦到"重新检查"按钮（截图 `02-focus.png` 可见 2px 焦点环），Enter 触发恰好 1 次新 `/health` 请求（200），无重复提交。
  - 1440 CSS px：无横溢（1440/1440），内容面板居中。
  - 200% 缩放：以独立验证者的真实页面缩放（page zoom）补证为准，通过。本交付此前记录的"200zoom"场景实为 deviceScaleFactor=2 的高清渲染（DPR），保留为渲染证据，不作为页面缩放结论；未重复再测。
  - 全部 4 场景：console 错误 0、pageerror 0；`/health` 请求均为真实 200（网络记录含状态码，见各 run.json）。
- 已知限制如实记录：服务器无 CJK 字体，截图中中文呈现为方框（字体缺项，非页面缺陷）；布局、焦点、溢出与交互证据不受影响。未验证浏览器内错误态 UI（gateway 当前始终 200；错误分支由 18 单元用例覆盖）。

## 6. 许可证补读（顺手项，完成）

- memorystream 0.3.1：package.json 无 `license` 字段，`licenses` 数组声明 MIT，包内 `LICENSE` 为 MIT 文本（SHA-256 `0077a46e…56a9`）。
- source-map-js 1.2.2：`license: BSD-3-Clause`，`LICENSE`（`6cb0631f…2fbd`）。
- tr46 6.0.0：`license: MIT`，`LICENSE.md`（`499d6d46…3fba67`）。
- 明细：`/fileOfRag/testOfRAG/metadata/story-1-1/frontend-baseline/license-supplement.json`。

## 7. 剩余说明

- 单元测试为 jsdom 环境，不替代真实浏览器交互；真实浏览器证据见第 5 节，两者均已执行。
- 单 chunk 大于 500 kB 的构建提示保留（EP 全量注册），后续 Story 可评估按需引入；不影响本 Story 验收。
- D 四服务、真实 PG、E 汇总及独立验证、审查仍按父 Story 原门槛执行，本文件不宣称其通过。
