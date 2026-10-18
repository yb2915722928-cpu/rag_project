# Story 1.2 阻塞检查点

日期：2026-10-18（Asia/Shanghai）。父 Story **in-progress / not-passed**；没有放行 1.3，也没有创建相同外部阻塞下的空转新会话或定时自动化。

主控 Amelia：`01a14b42-689c-7533-90a3-9bd187d93039`，实际 `group/auto-gpt-6-1-sol / max`。正式入口仍为 [工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-working-set.md:1) 和 [relay](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-relay-state.json:1)，不重载全部历史。

## 已实现与真实通过范围

- A：独立 epoch/mirror、持久当前 context/fence、锁后 PG 当前时钟、单 call prepared/may_have_sent/grant、NULL+unknown、call-only 迟到幂等与冲突事实。干净固定源码 af6 的88相关非PG+48runtime非PG+15真实PG全通过，主控核原XML/exit/前后Git/19hash。
- B：共用 EgressTarget、精确域/端口及全部A/AAAA公网校验、IP绑定与TLS主机校验、禁自动redirect/retry、凭据分域与秘密边界。固定7840285开发者169通过。
- C native：Linux child/有限IPC、一次grant、持久deployment+slot占用跨实例/boot、未知停止不释放、身份错绑不发信号、绝对IPC期限。固定96c开发者25通过。
- Step5独立：固定96c的311非PG+15PG通过，0失败/错误/跳过；独立Gitee检出及精确3.12.8、28unique快照源加lock前后hash无变化。仅稳定基础partial，不代替E/D。
- 正式唯一全新6.1Sol/medium：tree `1eff8cf456f705b8c5e0b21985b87ad9d6a846d2`，30文件diff hash `b9a19d5beab26888cce9edc7f75cffb74eb90ec87a70fe8849e66b0b8ad79e21`；新增发现0，已知E/D未关闭，fullrelease_gate=not-passed。原约定禁止凑数/泛化审查，本轮未加未来门。

受审差异已原字节归档为 [reviewed-source.diff](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-reviewed-source.diff:1)，hash与上述一致；主控核本次检查点暂存的全部实现/测试/Compose与受审tree的blob零差异。后续只有文档/证据更新，不给草稿虚构运行PASS。

上述不同提交的成绩分别留来源，不相加当同一最终全量成绩。[验收台账](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-acceptance-ledger.md:1)、[独立报告](/E:/aaa-project/rag/docs/story-1-2-independent-verification.md:1)、[正式审查](/E:/aaa-project/rag/docs/story-1-2-code-review.md:1)保留全部子句边界。

## 未完成的当前义务

1. E的 [call_dispatch.py](/E:/aaa-project/rag/backend/src/rag_app/application/call_dispatch.py:296) 与两测试是**未通过草稿**：F2强等值了逻辑query与传输api；成功/可信迟到账用例不一致；真child kill与PGunknown/不重复grant同路径矩阵尚未完成。源码已冻结保存，不能部署为已合格调用入口。
2. D的 [Compose](/E:/aaa-project/rag/deploy/compose.yaml:95) 与 [epoch部署说明](/E:/aaa-project/rag/docs/story-1-2-epoch-deploy.md:1) 已接控制文件，但新镜像、合法启动/重启及缺失/不可读/矛盾负例未执行。主控只读核服务器当前没有Story1.2专属新镜像/容器/epoch目录，未借旧1.1镜像代签。
3. 新E代码修复后仍须固定提交开发者测试、Step5只补新E/D、同正式审查者相关增量复核；全原AC及必要回归未齐前不能done/接下一Story。

未来1.3限流/permit、1.4资产、1.5总资格工具、身份/真实供应方/P0/目标部署仍按原规划归属，不把不存在的未来业务表作为当前新增前置。当前call/context/fact不复活和不乱改的证明义务保留。

## 最新恢复前缀派发与运行连接阻塞

用户随后明确指定 `zayuapi/deepseek-v4.1-flash` 继续开发。新E Aquinas `01a14c7b-78ff-7681-80fd-8f1e6155df95` 已创建；主控亲读 `2026-10-18T00:48:44.169Z` 的实际turn_context为该ID/max默认，随后放行三E源及交付文档。主控已看到该实例真实工具输出及E源码变更，当前模型阻塞解除；不追溯改写旧失败。

曾出现Netcatty连接阻塞：官方external MCP启动器缺发现文件，Tool CLI返回 `CONNECT_FAILED: connect ECONNREFUSED 127.0.0.1:51278`。用户随后明确报告修复，主控通过已配置的官方external MCP stdio服务认证，完成initialize/tools/list/get_environment，并在94b实际执行命令exit0：repo-fixed仍96c且干净、无Story1.2容器。该连接阻塞已解除，新E/D测试仍待固定提交后执行；没有本机项目运行或直接SSH代替。

## 历史去前缀ID拒绝

2026-10-18 用户要求去掉 `zayuapi/` 前缀，使用精确 `deepseek-v4.1-flash` 并继续。主控实际模型重新核为 `group/auto-gpt-6-1-sol / max`，本地HEAD `5e718c2aec1690040d8189eeb3de4b96c7f0746a`，无重复Story owner或E/D活动写者。新指令触发一次实际 `spawn_agent`，未设置推理override，接口原始返回：

```text
Unknown model `deepseek-v4.1-flash` for spawn_agent. Available models: group/auto-gpt-6-astra, group/auto-gpt-6-1-sol, group/auto-gpt-5-6-sol, zayuapi/deepseek-v4.1-flash, stepfun/step-5-preview
```

接口未返回agent ID，没有子实例turn_context或供应方请求证据。五份E/D源实际hash与历史冻结值一致，记录于[去前缀派发证据](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-bare-model-dispatch-2026-10-18.json:1)。项目模型映射已更新；实际运行仍受接口注册项阻塞，原E/D义务与未过状态保持。下一复核触发为接口注册项/配置变化或用户改变路由；不重复同一拒绝探测。

## 历史前缀通道阻塞

两次新实例均按指定 `zayuapi/deepseek-v4.1-flash` 派发、未覆盖推理；实际turn_context均max。首次 `01a14bfa-9d40-7f03-a3f7-3c823d20b28c` 于北京时间06:44:08完成报错；唯一有界重试 `01a14c0b-4f69-7131-934e-f06f931cbd1a` 于07:01:31同错：

```text
unexpected status 502 Bad Gateway: DeepSeek: Post "https://api.zayuapi.com/chat/completions": EOF, url: http://127.0.0.1:3425/backend-api/codex/responses
```

两实例已关闭、无新源修改，主控直接比对五份E/D源hash无变化，见 [no-write proof](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-DeepSeek-blocked-no-write-proof.json:1)。这证明本轮指定实现通道返回错误，不宣称底层供应方身份已独立核验，也不把D自身臆判为发生同样调用错误。未换模型/渠道/档位，主控未接管实现。

复核触发条件：用户报告通道恢复、实际环境/配置变化或明确新授权允许一次新的有界尝试。在该条件前不继续派同类探测、不循环创建会话。[续接说明](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/continue-story-1-2-after-channel-recovery.md:1)只续当前1.2。

## 源码与运行证据来源

- 最后实际运行固定源码为 `96c64fbab0fa8d3d824f2e592196c02570550c70`。本轮检查点包含后来保存的E草稿与文档，不给该检查点虚构运行PASS。
- 所有正式服务器代码只从Gitee固定提交，活动源 `/opt/rag-story-1-2/repo-fixed`；独立源 `/opt/rag-story-1-2/independent/repo`。桶归档 `/fileOfRag/testOfRAG/metadata/story-1-2`，active本地ext4，精确CPython3.12.8/PG18.6/vector0.8.7。
- 原52ccb1f SQL参数绑定导致七PG失败，作者server覆盖试跑仅草稿；af6干净新检出重测纠正。原七文本日志与hash保留，见 [首次证据](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-a-first-attempt-evidence.json:1)，不重标/不补造JUnit。
- 可用Netcatty session为94bede36-0e0e-444c-a8b7-f332d2542962；原0d连续timeout但connected，未重连不重试。当前无RPC持有者，不能并发工具时段。
- 全部秘密/运行环境/缓存仍外置。原agent SQL修补diff作为历史文本工件保留，已经固定提交的修复不因此再执行。
