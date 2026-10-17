# WeKnora Q4 窄事实

发布者：Tencent/WeKnora；固定 SHA：a37a1bc51ad85d096df341f6d3a098f60d586f52；发布日期：未核取 commit 日期；访问：2026-10-15。原文由本轮 urllib 从官方 raw 取得；不是运行项目 API。全部事实 confidence=medium，class=固定源码实现；单一官方原始来源已核对，未作独立来源验证，不外推运行容量。

1. **前端与交付。** [package.json](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/frontend/package.json) 列 Vue、TypeScript、Vite、Vue Router、Pinia 与 TDesign；[Dockerfile](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/frontend/Dockerfile#L26-L68) 在 Node builder 中构建，复制 dist 到 Nginx runtime；[Nginx](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/frontend/nginx.conf#L88-L126) 提供 SPA fallback 并把文件入口代理后端，API 代理见 204–208。借鉴静态产物／代理边界不能等同照抄所有交互或依赖。
2. **文件及部署。** [Compose](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/docker-compose.yml#L36-L49) 挂载数据文件卷；221–225 配 local 存储，另有 Redis 与更多服务；[下载 handler](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/handler/knowledge.go#L2045-L2081) 先取有效上下文检查 Editor，再经文件服务回传，private/no-store；预览使用 Viewer。此为该产品自己的权限规则，不能当本项目规则。[router](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/router/router.go#L209-L216) 也声明资源文件／签名文件不同入口；本题不扩查其完整授权机制。
3. **记录与许可。** [logger](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/logger/logger.go#L235-L278) 支持环境配置级别／路径／格式，默认 stdout，可同时落文件；不能据此声称它已满足本项目审计或成本账。LICENSE 本轮复读已有官方快照：称项目 MIT，另列第三方组件许可证；只报告文本，不给法律结论。

导入位于本目录上级 imports/weknora；每个文件前5行是来源元数据，其后源码行号=本地行号−5。LICENSE 原文沿用既有带源快照，不复制整份。

取得限制：GitHub tree API 403 rate limit；尝试过两个不存在的候选路径，未从失败请求建立结论；已使用固定 SHA 的直接已存在原文完成上述范围，不继续扩查。
