# Story 1.1 来源与依赖记录

状态：E 分段记录进行中。这里登记已取得的事实；完整生产镜像清单、前端正式构建和干净 Linux 重建随 C/D 实际交付补齐，不把历史环境或基础镜像探针记为整栈通过。

## 后端与公共契约

- 运行目标为 CPython 3.12.8、Uvicorn 0.37.0；依赖声明和实际工件/hash由 [pyproject.toml](/E:/aaa-project/rag/backend/pyproject.toml:1)、[uv.lock](/E:/aaa-project/rag/backend/uv.lock:1) 固定。
- 锁 SHA-256 为 `7ad33ac08870a9dfb0fccf3716207c4503d5fc745e0215b2adb7baadcea408ed`。A1 的 [实际依赖/许可证元数据](/E:/aaa-project/rag/docs/backend-dependency-inventory.json:1) 记录40项第三方锁条目，Linux选择38项，colorama/tzdata为未选择的Windows条件条目；包含发行版版本、声明许可证、上游URL、许可证文件hash及wheel hash。该清单绑定A1开发环境，最终API镜像内清单由D补证。
- [公共契约生成说明](/E:/aaa-project/rag/contracts/README.md:1) 指定后端模型/枚举、OpenAPI与有界JSON入口为来源。17个DTO、5个枚举导出51工件，生成器不引入另一套手写业务定义。
- [契约manifest](/E:/aaa-project/rag/contracts/manifest.json:1) 记录50个派生工件及9个源文件hash，manifest本身另由Git固定。51工件在 `9da9af209123e8f57b2650e14b98175f4aa5fefd` 入库，输入/输出两侧TypeScript分别使用，不相互替代；comparison业务按原规划后续增量。
- 当前HTTP修复、开发者回归与真实PG八项的具体环境、原始证据及未完成门见 [Linux交付记录](/E:/aaa-project/rag/docs/story-1-1-linux-developer-gates.md:1)。

## 前端脚手架、工具链与锁

- 实际使用Vue官方 `create-vue@3.23.0` 的TypeScript/Router/Pinia/Vitest模板，命令包含`--bare`；改造为当前Story的同源健康状态页、设计token、生成契约消费与必要状态测试。没有提前接入后续身份、文档或问答业务。
- GitHub固定版本的读取、文件及采用规则记入 [前端规范记录](/E:/aaa-project/rag/docs/story-1-1-frontend-standards.md:1)。该记录中的原seed与以下实际锁定版本分开保存。
- Linux使用Node 24.22.0 linux-x64及npm 11.19.1。官方Node归档实测SHA-256为 `cc2f601cee82d9a5a233302fe307abc600727035fd7d2c3a3571755989e95008`；工具链仅用于构建/测试，不构成第五个生产服务。
- [前端锁](/E:/aaa-project/rag/frontend/package-lock.json:1) 的SHA-256为 `4b6d69e744af7ddac2255ce8fa9c3cc64cf0d9576ae343fc0b2e60babd8ae4c0`，在 `b6e22bcf16dbf0c080eda4da9da6884c1af5a408` 发布；初次Linux正常安装为286包，正式锁定安装/构建证据由C补齐。

| 直接组件 | 实际解析版本 |
| --- | --- |
| Vue | 3.5.44 |
| Vite | 8.3.4 |
| TypeScript | 6.0.3 |
| Vue Router | 5.4.0 |
| Element Plus | 2.14.7 |
| Pinia | 4.1.0 |
| @vue/devtools-api | 8.2.1 |

Pinia 4.1.0与devtools-api 8.2.1是既定模板范围内的正常解析，主控已接受并记录；非optional peer保持安装。npm使用服务器既有腾讯云内网镜像，锁内保留实际resolved URL与integrity，不改写为未实际使用的直连来源。当前实际节点/许可证清单由正式C环境导出后补证。

## 基础镜像与传输来源

准确引用、index/platform/config/layer digest、层数、完整归档hash、实际版本及原始证据见 [镜像交付记录](/E:/aaa-project/rag/docs/story-1-1-official-image-access.md:1)。

| 发布方镜像 | 当前用途 |
| --- | --- |
| docker.io/library/python:3.12.8-slim-bookworm | API/worker构建基础 |
| docker.io/library/nginx:1.30.6-alpine | gateway静态前端与反向代理 |
| docker.io/pgvector/pgvector:0.8.7-pg18-bookworm | PostgreSQL 18.6与vector 0.8.7 |
| ghcr.io/astral-sh/uv:0.12.9 | 锁定依赖构建工具 |

发布方来源与传输分别记录：Docker Hub三个镜像使用既有腾讯云官方缓存按已核digest传输；uv完整层由本机已有代理从官方GHCR取得后，经既有通道传入。归档在服务器重算hash并加载；不能把归档hash、registry digest、config digest与Engine ID当成同一种标识。

基础镜像版本/层、隔离PG以及FROM版本探针不替代完整应用构建。D还需交实际API/gateway镜像、worker共用关系、原生/镜像内依赖许可证来源、四服务生命周期与干净Linux重建记录。

## 参考与验收边界

RAGFlow、MaxKB、Dify在规划中作为架构或界面参考；当前没有已登记的对应源码抽取，不据文档引用声称已完成源码复用。后续若实际抽取，按所属Story登记原仓库/版本、许可证、最小采用范围与改造。

当前记录只服务已批准的四项父AC。未来供应方、生产vector(D)、真实业务上传与目标性能门按原规划到期验收，不为来源记录提前扩展实现。当前仍待C/D的实际清单与重建证据；独立验证和正式审查保持原完成门。
