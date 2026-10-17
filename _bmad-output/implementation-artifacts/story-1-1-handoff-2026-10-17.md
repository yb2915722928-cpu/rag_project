# Story 1.1 自动续接提示词

**历史记录，已被 [6.1 Sol / max 新交接](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-handoff-sol-max-2026-10-17.md:1) 和 [最新模型/环境决定](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-model-environment-decision-2026-10-17.md:1) 取代。下文 Astra、3.12.15、本机 Docker 阻塞及模型不可核判断不得当作当前指令。**

日期：2026-10-17，Asia/Shanghai。交接原因：当前运行回合的实际主会话为 `group/auto-gpt-6-1-sol / ultra`，不满足项目规定；接收会话须显式使用 `group/auto-gpt-6-astra / max`。`max` 是同模型不支持 `ultra` 时的已批准回退。本次交接只续接 Story 1.1，禁止开始 Story 1.2。

## 可直接执行的提示词

继续 RAG_all 当前 Story 1.1。用户已授权生成交接提示词后自动在同一 rag 项目新建会话接手；沿用全部模型分工、独立验证、独立审查和串行接力门。先核对你自己的实际模型与推理档位及唯一认领，再执行实现派发，不继承上一主会话错误的模型身份。

先读 [Story 1.1 当前工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md:1)，再读项目规则和 relay state。工作集是当前状态摘要；只有工作集列出的“需回读条件”满足时，才读取完整规划材料。用一次合并只读诊断同时核对实际模型/推理档位、同项目会话、relay owner、实现认领和环境阻塞；不要把同一状态拆成多次探测。

先读取并遵守：

- [项目规则](/E:/aaa-project/rag/AGENTS.md:1)
- [Story 1.1 当前工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md:1)
- [Sprint 状态](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-status.yaml:1)
- [A 段后端规格](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-rebuildable-modular-project.md:1)
- [父 Story 交付计划](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-delivery-plan.md:1)
- [唯一接力认领](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)
- [拆分范围与归属](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/deferred-work.md:1)
- [重建证据](/E:/aaa-project/rag/docs/rebuild-evidence.md:1)
- [来源台账](/E:/aaa-project/rag/docs/dependency-manifest.md:1)
- [原 Story AC](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:184)
- [运行门台账](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/runtime-acceptance-status.yaml:1)

先使用一次 list_projects/list_threads 合并核对同项目会话和项目路径；项目 ID 为 `61e1f316-4db1-4b50-a56e-62c5604d7d25`，目录为 `E:/aaa-project/rag`，使用 local，不创建 worktree。不要向其他会话发送任务或抢占已认领文件。工作集已经记录且未发生触发条件的外部阻塞不得重复探测。

主会话模型必须为 `group/auto-gpt-6-astra`，本工具声明只支持 `max`，如实记录已批准的 `ultra -> max` 回退。核对当前 rollout 的 turn_context，不以全局配置或提示词中的模型自称替代实际运行证据。当前路由配置的成员为 `gpt-zayu/gpt-6-astra:max`、`codex/gpt-6-astra`。复杂实现和独立审查使用 `group/auto-gpt-6-1-sol / medium`；工具已声明支持 medium，但不能据此将先前 B/D 的能力核实阻塞直接改为通过。指定模型执行证据可核后再派发；明确的密封子任务或协议限制不得重复同类探测、静默换模型或交给主会话写代码。

使用 bmad-build 恢复现有 in-progress 规格，不重新批准已获授权的范围。只有规格/契约变化或工作流入口变化时才完整回读 bmad-build 步骤；不要每次续接重复加载全部 workflow 文件。此前本机入口首次因 Windows 沙箱 uv 临时文件持久化失败，沙箱外按原命令重试成功；若再次遇到相同沙箱错误，按权限工具申请必要 escalation，不直接运行 workflow 源码绕过入口。

实施顺序：

1. 保留父 Story 四项原始 AC 与 A/B/C/D/E 所有义务。A 冻结子规格只约束 A，不作为 B/C/D 的唯一规格；主会话先形成各分段短规格、公共契约、文件归属与验收，再交指定实现者。达到 1600-token 风险线自动继续拆分，保留父 Story 验收分母。
2. 在模型能力可核后先交付 B contracts，复杂实现者唯一修改 contracts/**；B/D 先前两次派发均停止，没有可直接验收的交付。B 必须有 OpenAPI/JSON Schema/后端导出的 TS、C1 Unicode/非 BMP/确定性序列化、C2 有限公共包/错误、实施契约 3.5 的 H 正负边界及有界 HTTP 测试入口。若入口必须修改 backend 文件，先由主会话协调其唯一写者，不让两个实现者同时修改。
3. B 通过后派发 C 给 kimi/kimi-k3 默认档位，唯一修改 frontend/**。编码前先识别技术栈、到 GitHub 阅读官方或维护中的适配规范，把来源、文档、提交/版本、查阅日期和采用规则写入开发记录；无法访问时保留阻塞。保持 create-vue 3.23.0 TS/Router/Pinia、既定 UX 与 peer 锁。
4. D 仍交 group/auto-gpt-6-1-sol / medium，唯一修改 deploy/**；只包含 gateway/API/worker/PG 四服务。Docker 的 dockerInference 套接字错误尚未恢复，禁止重置 Docker 或删除用户数据；静态编排不等于 Linux 生命周期通过。
5. A 已有静态安全修复和 3.12.8 补充回归。先取得真实 CPython 3.12.15，再由实现者重算 uv.lock，确认 uvicorn==0.37.0 并执行 --locked 同步；不放宽版本、不手改锁、不用 frozen 绕过差异。主会话不修改锁或其他实现文件。
6. 取得真实 PostgreSQL 18.6 / pgvector 0.8.7 和授权隔离测试库后，运行 --require-postgres 六项必跑、迁移循环、namespace 负例和 Uvicorn 实际进程验证。没有真实环境不标通过。DSN/秘密不得写入文档或普通日志。
7. E 仍为部分来源台账；依赖/peer、工件 hash、镜像 digest、许可证、上游改造边界及干净 Linux 重建证据均须逐项完成。
8. 开发者完成各自测试，Step 5 Preview 默认档位独立验证；全新 group/auto-gpt-6-1-sol / medium 实例独立审查。问题交回原实现者修复、相关回归并独立复核。未执行、skipped、未知或只完成子规格均不能放行父 Story。
9. 只有父 Story 全部完成门通过，才更新真实 Sprint/relay 状态、生成下一条满足依赖的交接提示词，并在同一项目自动创建一个新会话。若只有相同外部阻塞，没有新的可执行工作，保存证据并通知用户，不循环创建空转会话。

接手后确认自己取得 relay 中的唯一主控职责，记录实际模型和当前任务。转出会话只记录创建结果并核实接手，随后释放写入；不要等待它继续实现。

## 本轮交接前证据

- 转出会话：`01a14894-8abc-7c61-9e47-6a0fe6fbba40`；历史主控：`01a147a0-7be2-7b53-aaf8-5a15238bad52`，核对时 idle。
- 当前运行 turn_context：`01a14894-963d-76c1-acf2-a0141f76031e`，`group/auto-gpt-6-1-sol / ultra`。用户表示已修改设置后，本回合可读运行记录仍为该值；不宣称热切换已生效。
- [uv.lock](/E:/aaa-project/rag/backend/uv.lock:1) SHA-256：`79c607d20f9c2308e7b7edefab73f7127e6c1efe4053ca14d9bf6ff5ba976b4f`；仍是旧锁，缺 Uvicorn。
- [pyproject.toml](/E:/aaa-project/rag/backend/pyproject.toml:1) SHA-256：`6c39aec86c9d38fbfcd7dd79136ebe0a04f8255415d1c645662fb24fcebb8d61`。
- 本轮转出会话未修改应用、测试、锁、部署或实现脚本；没有派发 B/C/D，也没有重试安装解释器、重置 Docker 或执行 PG 迁移。历史通过/未执行结论按原证据保留。
