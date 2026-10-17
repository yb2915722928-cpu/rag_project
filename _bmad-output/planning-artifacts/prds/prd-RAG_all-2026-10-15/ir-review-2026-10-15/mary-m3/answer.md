# M3 · 旧备份恢复后的可信放行

日期：2026-10-15。Mary TR → TS；status: complete；同题最后追问已闭环。以下是待实施契约，不代表恢复演练已通过。

**选择“隔离恢复＋独立核验＋按范围放行”。** 匹配备份解决恢复点内的一致性；恢复点后的停用、撤权、删除仍须有独立依据。无依据就保留隔离，不以旧备份所有者自证。完整顺序、错误和核对记录见[恢复动作表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/runbook.md:1)。

**TR 事实。** WeKnora 的 JWT 还查持久 token 撤销状态与用户 active，停用会在 DB 事务中撤销 token；API key 查 hash、撤销与到期字段，文件卷与 PG 卷分离。[认证源码](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/user.go#L1285)、[key 源码](https://github.com/Tencent/WeKnora/blob/a37a1bc51ad85d096df341f6d3a098f60d586f52/internal/application/service/tenant_api_key.go#L86)。MaxKB 用户登录依赖 cache token 和 DB 账号／密码，应用 key 的启停与到期查 DB，安装声明数据卷及本地 PG／Redis。[用户认证](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/auth/handle/impl/user_token.py#L300)、[应用 key](https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/apps/common/auth/handle/impl/application_key.py#L18)。这些状态可随旧库倒退；清会话也挡不住旧 active 账号用旧密码再登录。PG dump 只给开始时的一致快照，单库不含全局角色；PITR 依赖基准备份与连续 WAL，恢复至目标点，不补之后事件或配置变化。[dump](https://www.postgresql.org/docs/17/backup-dump.html)、[PITR](https://www.postgresql.org/docs/17/continuous-archiving.html)。两产品均未在本轮证明完整安全恢复、跨卷匹配或外部任务恰好一次；详见[证据边界](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m3/evidence.md:1)。

**TS 身份门槛。** 先关业务入口、停 worker 和外部请求；恢复匹配材料后，新生成随机不可复用 recovery_id／epoch，禁止沿用备份值加一。普通部署／重启读取独立持久封存的现行 epoch，仅备份恢复或明确安全重置才更换；开放前 DB／运行进程须一致，旧进程停或 fence。全部旧 Web 会话和用户 key 作废；账号一律 unverified，旧密码不得正常登录。恢复操作者由部署时独立封存的 break-glass 凭据和受托记录核验，凭据不取自恢复 DB；恢复权限只处理元数据，不赋予正文读取权。账号经独立身份核验、现行职责确认及密码重置后启用，按当前范围重发凭据。

**TS 当前范围。** 安全变更与业务变更同事务写最小台账，记录事件序号、目标稳定 ID、停用／撤权／转让／删除元数据，不含正文或密钥；定期导出到独立受控介质，附连续区间和校验清单。导出有间隙，不能承诺 RPO0。只重放可验证区间；缺口由独立核验的恢复操作者与当前明确受托的业务负责人，根据外部记录重新确认账号、成员／角色、库授权及仍存资料清单。受托依据不能来自旧所有者字段。已知 tombstone 优先；不能确认删除完整性的库继续隔离，个人空间同样适用。放行记录须写依据、范围、确认人和时间；平台身份仍无业务读权。

**TS 操作与费用。** 全部旧 attempt 以新 epoch 隔离，迟到者不能提交、结算或发布。已 success 的结果保留原计次，有效期内重放仍核当前权限；过期仅按仍保留且有权的会话历史读取。中断生成终止，不自动重付费。文档任务有上游 ID 才在范围及对应费用动作授权后查询／接回，无 ID 标 unknown，不盲交，未知费用留 gap。认证后元数据入口提供本人 epoch／server_time／cutover；新操作必须提交当前 epoch，UUIDv7 时间不得早于 cutover，手改 epoch 也不豁免；旧请求不自动重送。当前上海日计次无法核对的空间冻结新增生成，待外账核对或下一日再开放；下一日只解配额冻结。供应方密文默认不可调用，重新确认当前凭据；主密钥缺失可见阻断且不输出秘密。

**代价与边界。** 需最小台账、独立恢复凭据和人工范围确认；缺可信介质时可停服较久。频率、保留、恢复点与可丢失窗口由部署负责人首次部署登记。离机副本当前仅为设计，首次上线前须完成隔离恢复演练。

未选“清 token 后直接开站”，因为它不能覆盖旧密码和已删除资料；也不把连续备份／PITR列为首版安全捷径。放行可先恢复已核验范围的本地只读，再独立开放写入、状态查询和付费任务；每一步保留隔离清单。维护入口仍可登记当前有权主体提出的新删除／撤权元数据，立即纳入 deny／台账；不开放普通业务写。团队须先有经独立核验且当前有效的所有者，平台操作者不因此取得个人资料读权。

演练至少覆盖：

1. 备份后停用账号／撤权／撤 key／删文档，再恢复旧点：旧密码、会话、key、历史引用与下载均不能复活访问。
2. 缺台账尾段或无法核验负责人：该账号／库维持隔离；备份所有者不能自行放行。
3. 丢失当日 operation／计次、重放旧 key、注入迟到 worker：不新增调用、不重复结算、不发布旧候选。
4. 上游已接单但本地 ID 丢失／主密钥缺失：分别显示 unknown／阻断，任何外部请求须先获对应放行。
5. 再次恢复同一备份：epoch 不重用，前次恢复签发凭据也失效。

user_only_missing：无；真实恢复时才需要可信人及介质。
