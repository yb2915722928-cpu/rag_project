# RAG_all frontend（Story 1.1 骨架）

Vue 3 + TypeScript + Vue Router + Pinia + Element Plus 浅色骨架，当前仅包含健康状态页
（前端加载与同源 `/health` HTTP 可达性展示，不表达数据库就绪或业务成功）。

开发约定见 [docs/story-1-1-frontend-standards.md](../docs/story-1-1-frontend-standards.md)
与 [docs/story-1-1-frontend-delivery.md](../docs/story-1-1-frontend-delivery.md)。

## 运行环境

- Node.js `^22.18.0 || >=24.12.0`（create-vue 3.23.0 模板约束）；项目统一使用 Node 24.22.0。
- 应用安装、构建、测试仅在 Netcatty Linux 主机执行；本目录不保留本地 `node_modules` 或 `dist`。

## 命令

```sh
npm ci          # 使用 package-lock.json 的锁定安装
npm run type-check  # vue-tsc --build（覆盖 src 与 ../contracts/typescript/*.ts）
npm run test:unit   # vitest
npm run build       # type-check + vite build
npm run dev         # 开发服务器（仅开发用）
```

## 生成契约类型

`../contracts/typescript/` 由后端真源生成（见 `contracts/README.md`），本前端只消费其公共
类型（如 `PublicError`），不维护第二套手写业务 DTO；类型检查经
`tsconfig.app.json` include 与根 `tsconfig.json` paths 覆盖该目录，打包经
`vite.config.ts` 的 `@contracts` 别名解析。`HealthStatus` 在 OpenAPI 中为无枚举的
自由字符串字段对象，其线形校验在 `src/stores/health.ts` 运行时完成。
