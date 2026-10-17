# John B · M1／M2 实际改稿定点核对

日期：2026-10-15。仍为初轮的同一位 John B；本轮仅复核 B1–B6。实际读取修订后的 PRD、实施契约第 1–3 节，M1／M2 的 answer、followup-answer，以及 M2 的 schema、UI 契约。不以各文件的 complete 标签作为通过依据，未将尚在处理的 B7 与实施切片纳入本轮结论。

**结论：B1–B6 在规划／行为契约层面均暂可关闭；本次未找到仍需补造关键产品行为的 material 反例。** 这不是实现、故障测试或效果验收通过，也不是全实施计划的最终 PASS。原初评历史保持不动。

## 定点结果

| 原发现 | 结论及实际依据 | 本轮构造的反例与处理 |
| --- | --- | --- |
| B1 请求准入 | 暂可关闭。[PRD FR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:169)、[实施契约 §1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:16) | 同人或异人双凭据均拒绝；无效／过期凭据不回退；无关 Cookie 不误判。A+B 中 B 越界／不存在整拒，不删对象继续；检查在外部查询调用前，后续仍重鉴权。 |
| B2 配额、幂等与崩溃 | 暂可关闭。[PRD FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:161)、[实施契约 §2.2–2.3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:41) | 23:59 预留后崩溃，恢复器有限扫描并以 lease／token／attempt 终止、释放一次；同 Key 次日只回原终态失败，新 Key 才走新日桶。成功已提交但回包丢失仍是成功重放，不再次检索／生成／扣次。异 payload 冲突、HMAC 轮换、迟到写历史、过期 Key 墓碑清后复活均已有确定限制。 |
| B3 容量与非原子资产 | 暂可关闭。[PRD 容量规则](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:159)、[实施契约 §2.1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:26) | 原件全部保留版本＋在途预留的口径确定；并发条件预留、未知长度先占上限、满额替换不先抵扣旧版。FS 已写而 PG 未提交时依靠受控临时路径／哈希／资产清单恢复登记或清理；清理失败不释放，状态转换不重复归还。派生／解包／备份另受磁盘保护，不冒充“全部物理容量”。 |
| B4 索引切换与并行写入 | 暂可关闭。[实施契约 §3.1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:75)、[M2 UI 详细守卫](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:7) | profile 默认配置不可就地改旧库；新上传预留与重建在同 KB 锁下排斥，包含尚未运行的写意图。删除先墓碑并使候选失效、条件解 guard；失败／取消／过期不会因物理清理未完永久阻写。切换前查 revision／活动版本集，跨库不兼容整拒。 |
| B5 对比规模及结果 | 暂可关闭。[实施契约 §3.2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:95)、[comparison.v1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/schema.md:5) | 输入上限、规范化、重复及未知字段整拒；对象／条件身份固定、每格恰好存在、四态证据基数明确。零候选保留全部格并用确定性不足模板计一次，依赖失败和模型非法结构不能降格为正常不足。最终实际片段 K=5 与 SM-2／SM-3 分母保留。 |
| B6 校核与来源交互 | 暂可关闭。[实施契约 §3.3](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md:105)、[M2 动作矩阵](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/mary-m2/ui-contract.md:19) | 生效／候选／任务分开，旧版可用不会被候选处理中覆盖。首次 partial 与不完整替换不同；修正走新候选，重试走新 attempt，不建通用编辑器、不篡改历史。未知结果知情重交与普通审批分开。PDF 缺 bbox 回退到可靠页；非 PDF 结构＋提取片段＋受控原件清楚，失配不猜位置。 |

## 对此前追问的明确答复

- **FS／PG 非原子不是被宣称消除了。** 当前稿件明确承认该边界，规定只有有效候选校验资产才能恢复登记，否则清理后释放；这足以据此实现恢复协调，不需要现在发明分布式文件事务。
- **同 Key 失败后跨日不重新执行**，因此此前“从哪个桶重新预留”的歧义已由 M1 的终态只回放政策消除；成功丢回包也明确不回滚。诊断 request_id 不再承担幂等。
- **清理失败仍计原件占用**，并且物理预算独立，容量释放和逻辑删除不再混同。满额替换、配额下调与未知长度也有唯一行为。
- **历史引用不依赖旧向量永久存在。** 新稿保存 evidence_snapshot、原文版本和定位资源；旧向量只需保到相关在途操作终态／固化 deadline。已取消／废弃的写意图属于终态，不应成为永久阻写条件。
- 对比 v1 每对象是一个所选文档版本，跨对象差异不自动标冲突；跨多文档同事实冲突仍由普通问答显示双方，未取消冲突关键题及原完成门槛。我接受这一明确的首版对象边界。

## 不升级为新规划缺口的实现锁定项

逐文件 operation_id 的唯一约束应覆盖候选创建／预留及上传重传；资产清单、fence 与配额事件的具体表结构、文件重命名及恢复顺序，应在实现中按既定不变量锁定。它们不再需要新的产品选择，不能因目前未写 SQL 或未运行故障测试，反复重开 B2／B3。

同理，向量迁移 SQL、精确 JSON Schema／Pydantic 跨字段校验、PDF 渲染库和页面组件属于实施选择。M2 已有可解析的 3 个 JSON 示例，本轮实际解析成功；这只确认文档示例语法，不证明后端或模型已经通过。

后续必须实施初评对应的并发、崩溃、迟到、清理失败、重建／删除竞态、零候选及结构失败用例。此处接受的是“行为与契约足以编写这些用例”，没有填入运行成绩。B7 与切片由父级继续处理，待最终实际修订完成后再做原范围的最终 gate。
