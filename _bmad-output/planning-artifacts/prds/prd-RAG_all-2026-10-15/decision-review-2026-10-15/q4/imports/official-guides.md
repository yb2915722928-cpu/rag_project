# 官方指南窄提取

访问日期均为 2026-10-15；以下页面未标独立发布日期；通过本轮 web 工具实际打开。为决定提供直接依据，不推导已验证容量或整机安全保证。

## D1｜Compose secrets

- Publisher：Docker Inc.；source：https://docs.docker.com/compose/how-tos/use-secrets/
- 页面工具行：26–38、91–98。
- 提取：Compose secrets 按服务显式授予；Linux 容器将单文件绑定挂载至 secrets 目录。官方提醒环境变量可能在调试／日志中意外暴露。挂载文件机制本身不证明宿主文件已加密，也不是外置密钥服务。
- claim class：接口／机制；confidence：medium（单一官方原始来源，本轮已读；未作独立交叉核验）。

## D2｜Compose services

- Publisher：Docker Inc.；source：https://docs.docker.com/reference/compose-file/services/
- 页面工具行：107–110、249–253、388–442；目录列有 mem_limit、healthcheck、logging、restart、stop_grace_period、volumes。
- 提取：service 可定义镜像及运行约束；cpus 为可分数 CPU 限额；依赖的 service_healthy 条件会等待健康检查；deploy 支持属于可选能力，不能仅凭文件写了就假定执行环境已落实。
- claim class：接口／机制；confidence：medium。限额实际生效要部署时检查 Docker／Compose 版本、有效配置及容器 inspect；本轮未操作服务器。

## N1｜静态内容与代理

- Publisher：NGINX；source：https://nginx.org/en/docs/beginners_guide.html
- 页面工具行：74–124、125–177。
- 提取：Nginx 的 location／root 可服务静态文件，proxy_pass 可将请求转发给后端；其示例同时展示两者。access/error 日志可辅助定位请求及代理故障。
- claim class：接口／机制；confidence：medium。静态与受控原件分开是本项目设计，不能从该通用指南推定业务授权已实现。

## N2｜HTTPS

- Publisher：NGINX；source：https://nginx.org/en/docs/http/configuring_https_servers.html
- 提取：HTTPS server 配置使用 ssl_certificate 和 ssl_certificate_key；证书文件可传播，私钥应限制访问。文档提供 TLS 服务端配置依据，并不替项目申请证书／确认域名。
- claim class：接口／机制；confidence：medium。实际证书取得及更新路径到部署接入时核对；当前没有执行。

## P1｜SQL dump 与恢复

- Publisher：PostgreSQL Global Development Group；source：https://www.postgresql.org/docs/17/backup-dump.html
- 页面工具行：24–33、36–46、55–65。
- 提取：pg_dump 生成单数据库的一致快照；非文本归档由 pg_restore 恢复；单库 dump 不含全局角色／表空间，globals 可另导出。其范围是数据库，不能将其解释为项目原文件、宿主配置或外置主密钥备份。
- claim class：接口／机制；confidence：medium。选用停写后打包数据库及应用文件是本项目一致性方案；本轮没有生成或恢复备份。
