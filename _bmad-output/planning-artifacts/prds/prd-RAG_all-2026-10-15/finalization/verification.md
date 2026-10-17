# 定稿修正定点复核

结论：**PASS**。仅复核本轮修正与 [Mary 澄清](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/finalization/clarifications.md:3)的对应关系，不重跑全篇 rubric，不把产品定稿等同于实现或实测验收通过。

| 定点范围 | 结果与证据 |
| --- | --- |
| 版本、候选、部分可用与校核术语 | PASS：[PRD 术语表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:89)区分候选、生效、历史版本、完整就绪与首次部分可用；候选不参加查询。首次部分可用须明确失败范围、有可靠来源并提示不完整；[FR-8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:193)仍要求完整且当前有效候选才能替换旧版，迟到任务不能覆盖或复活资料。程序校核不冒充 OCR／语义准确性证明。 |
| PDF 与无稳定页码格式定位 | PASS：[FR-7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:183)规定 PDF 物理页从 1 起，DOCX／Markdown／TXT 使用可回查的实际章节、块与表图位置，不编页码；复杂样例人工对照仍保留。 |
| FR-4 配额成功、失败与重试 | PASS：[FR-4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:155)明确空间内 Web／API 共用、生成前原子预留、正常完整答复含合规不足／澄清／冲突计次；拒绝与列举执行失败释放预留。同 ID 不重扣、显式新请求成功另计、重试复核权限，归受理时上海日期；纯检索／引用／状态不扣问答次数，真实调用费用逐次保留。 |
| FR-6／FR-15 待核对及有权动作 | PASS：[FR-6](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:173)已显示待核对；[FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:247)明确有限原任务查询、阈值后需处理、当前有维护权限者继续核对或知情显式重交、保留原关联和迟到守卫。人工重交例外符合 Mary 澄清 B，不应再按此前“未知结果一律不可重交”建议判错；只读 API 无核对／重交动作，删除与失权规则继续有效。 |
| NFR-5 备份恢复验收 | PASS：[NFR-5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:267)要求匹配数据库、原件／解析产物／引用资源、配置与密钥恢复材料，在干净隔离环境实际演练，核验引用、权限、删除及未完任务后再恢复服务；备份存在不等同恢复通过。 |
| 技术补充 B0／同步 Session 旧文字 | PASS：[第 6.2 节](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:103)保持同步短 Session；[第 6.3 节](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/addendum.md:114)改为已选调用链与实施验证，关键词／融合／重排／ANN 不再属于 B0 必经步骤，Session 依据也改为同步会话文档。原 rubric 唯一 low 发现已关闭。 |
| 范围与成功指标防回退 | PASS：[评估与 SM-1–SM-7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:270)仍保留四场景各 8 题、24 可回答／8 不足、全请求 K=5、21/24 且每场景 5/6、证据覆盖 85%、引用语义支撑 95% 与可打开率 100%、不足题全通过、复杂关键题与独立权限专项、工程实践证据，未改为可选或取消。 |

剩余问题：**无**。本轮修正与受托澄清一致，未发现新增产品冲突；实际恢复、并发配额、外部任务异常和资料质量仍须在实施阶段按已定义行为测试。
