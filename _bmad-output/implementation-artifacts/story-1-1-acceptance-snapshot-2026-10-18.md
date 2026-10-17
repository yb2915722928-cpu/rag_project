# Story 1.1 验收快照

状态：**passed / done**。原四项 AC、拆分项、开发者测试、独立验证、正式审查与修复回归均已闭环；允许接续 Story 1.2。

唯一主控：`01a14973-8555-7131-8fd2-e9eec12f53fe`，实际 `group/auto-gpt-6-1-sol / max`。原四项 AC 不变，来源为 [epics](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:184)。

## 源码、环境与产物绑定

- 最终功能源码提交：`25232d0bebc230c35837153b6fd572ff734977aa`，已正常推送 GitHub/Gitee。服务器代码只从 Gitee 固定取得；后续完成文档提交不冒充新的运行测试。
- 后端/PG/B 的源码与 dd448343 相同；独立运行在该冻结提交执行。R1仅改变前端健康读取函数及其测试，252的原作者相关回归已真实14/14通过，type-check/build通过。
- Linux主机 `120.53.251.166`，精确CPython3.12.8、Uvicorn0.37.0、PostgreSQL18.6、pgvector0.8.7、Nginx1.30.6；Node24.22.0仅构建/测试，uv构建工具0.12.9。
- API/worker镜像相同：`sha256:75a1e1bc5f99f11e5f1f77a4104bcee18b493f29bd1e792ee06a9221c7dd19e9`。最终gateway：`sha256:6ae64cf42fc2a0edc2b145b1a09f5e9c5541453318e21a7d0043afd922923ffa`，由252新dist无缓存构建，退出0。
- 活动代码、PG与锁位于 `/opt/rag-story-1-1` 的Linux本地文件系统，材料/输出归档 `/fileOfRag/testOfRAG`；没有把对象存储当数据库或锁盘。

| 最终前端工件 | SHA-256 |
| --- | --- |
| index.html | `4bd67fe33d6d6a226846e2c1b4c37931f02159f4f158319d313d2e124fe5817f` |
| assets/index-CDataiw2.js | `fade5263dc4a33deba1bc7de956fc2497fc1f1d343ce2de0acdb781f8de9348a` |
| assets/index-AMOFkByE.css | `9a485ada3a2f3713c75dea8fc76b4766aeb384a8cea6de0a3116ed27c2f7ca3a` |
| favicon.ico | `db74ab0b78338c1f778f8398c45f4103c99aea0e845a3118a7750b4eeafd3445` |

## 原 AC 与完成分母

| 原验收项 | 当前证据与结果 |
| --- | --- |
| AC1：锁定前后端及四服务构建/启动/停止 | **passed**。create-vue3.23.0 TS/Router/Pinia骨架、真实依赖/peer锁、Node官方hash、18原单元及开发者/独立者R1各14回归、类型/构建；四服务healthy、原stop/start exit0、数据保留，当前新gateway hash及独立交互通过。实际容器UID/挂载/secret权限已实测并独立核对。 |
| AC2：真实PG/扩展、短UoW、迁移/回滚与边界 | **passed**。开发者与独立者各8/8真实PG节点通过，包含六项必跑与worker TERM/INT；随机schema清理0，vector版本前后未变，未创建正式生产vector(D)或后续业务表。 |
| AC3：来源/许可证/边界与干净Linux复现 | **passed**。依赖与许可证声明、peer、镜像发布方及实际传输、各层/归档hash已登记；独立干净frontend ci/build的dist逐字节相同，no-cache API/gateway实际生成且app/venv指纹相同。实际API/worker同inode、flock持锁互斥/释放后可取、os.replace跨容器可见及ext4/UID/权限均已实测并独立核对。原后台shell退出码因作业过期未记录，明确保留该限制；完整BuildKit完成日志与实际工件是重建结果的直接证据，不追加一次整栈重建以补包装回显。252新gateway另有明确no-cache exit0。 |
| AC4：公共C1/C2/H、OpenAPI/Schema/TS与正负样例 | **passed**。开发者与独立者各52/52样例通过；51工件生成/check一致，manifest50产物/9来源hash一致，17 DTO/5枚举。错误响应信封缺status已修并回归；comparison等按原计划后续增量，不纳当前分母。 |

## 独立验证与正式审查

- Anscombe `01a14ad7-beb6-70c2-9098-4a2734b79c17`，实际Step5/high，派发未传档位。已实际独立非PG514passed、真实3.12.3负例1passed、PG8passed、check51及样例52passed。唯一条件skip由独立错误解释器运行补证，不把skip当pass。
- 真实gateway浏览器的320/768/1440与键盘已验；独立者纠正DPR2不能替代页面缩放，并补证真实200%缩放通过。Linux测试浏览器缺CJK字体影响截图字形，未据此修改产品字体或追加应用补强；不宣称该环境完成中文视觉字形评估。
- Cicero `01a14afb-d1eb-75d0-b981-ee0cae4235e0`，全新6.1 Sol/medium，一轮正式审查1项R1/P2；正文阶段超时/取消分类已最小修复，同一审查者静态及原作者14/14回归复核关闭，无新增发现。
- Anscombe对252的R1相关14测试及最终gateway哈希/真实加载与刷新已独立通过，原后端/PG/B未重复运行。额外隔离反向探针曾临时替换旧helper并恢复，记录其方法与恢复后的干净状态，不声称验证期间从未改过隔离测试目录源码。
- 原D最后缺项已闭环：`locks-assets-uid-probe.txt` SHA-256 `f5ae1a320a71ae18a901e149cc5845a6cc6a95ea37c6d69d32f80436ffb072fd`。host/API/worker锁inode674851、资产inode674852一致；worker持EX锁时API非阻塞被拒、释放后可取，原子替换内容可读。只清理本任务3个新探针，未碰应用锁/数据，四服务保持healthy。
- 原迁移/启停工具观察已按call_id从封存日志导出并脱敏归档为 `deploy-integration/lifecycle-original-tool-observations.json`，8050字节，SHA-256 `daeed77fc05261b5e15398697a1a8bf548c841e7ca6ade68e5824e7e178990c3`；原输出为migrate_exit=0、DATABASE_BASELINE_OK、stop_exit=0、start_exit=0，未重新执行。

## 原始证据与记录

- [Linux开发者交付](/E:/aaa-project/rag/docs/story-1-1-linux-developer-gates.md:1)、[前端交付](/E:/aaa-project/rag/docs/story-1-1-frontend-delivery.md:1)、[部署交付](/E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md:1)。
- [独立验证](/E:/aaa-project/rag/docs/story-1-1-independent-verification.md:1)、[正式代码审查](/E:/aaa-project/rag/docs/story-1-1-final-code-review.md:1)、[来源记录](/E:/aaa-project/rag/docs/provenance.md:1)。
- 桶内根目录 `/fileOfRag/testOfRAG/metadata/story-1-1/`：`linux-developer-gates/{a70a7e2,9da9af2-pg}`、`frontend-baseline`、`deploy-integration`、`official-image-access`、`postgres-test-environment`、`independent-verification`。原44/8失败、旧预备工件和历史模型证据保留，未反标新提交通过。
- 本轮实际模型均由父会话读取turn_context记录；DeepSeek/Kimi默认实际max、Step5默认实际high、正式审查显式medium。底层供应方身份未取得，不宣称已核。

主控据上述证据完成原门裁决，更新Sprint/分规格状态并保存下一Story提示词、唯一认领，再在同一saved rag项目创建下一Amelia本地会话，核实接手后释放本会话；无定时自动化。后续S0整体签署、供应方、真实业务上传及目标机门按原Story到期，不由1.1提前放行。
