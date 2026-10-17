# M3 · John 的实际问题

日期：2026-10-15。Mary／Business Analyst；bmad-agent-analyst＋bmad-deep-recon，headless technical explore → select。按本轮委托只写本目录问答与恢复动作表，不追加模板研究、memlog、评分、额外评审、编码、安装、服务器操作、收费调用或 HTML。

> 从旧备份恢复时，怎样防止备份之后发生的账号停用、撤权、密钥撤销和文档删除被复活？WeKnora、MaxKB 与 PG 备份实际上恢复哪些状态、哪些并不保证？先 TR 再 TS，选择最小可信恢复／放行机制，并说明逻辑操作配额和外部任务怎样恢复，不能靠旧备份里的所有者自己确认当前权限。

需求来源：[NFR-5、FR-3、FR-8、FR-15](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/prd.md:137)，范围：137–147、197–205、253–255、277；[B7 初评](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-initial-ir.md:90)；[B7 真实回应](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/john-b-debate-reply.md:63)。这些只限定问题，不充当外部事实。

继承 M1 逻辑操作／上海日配额和 M2 generation／墓碑／迟到任务隔离；保留停写匹配备份与分离主密钥、4C4GB 同机四服务、平台恢复权限无业务读权。首轮只核两项目固定 SHA 的认证、卷与恢复相关路径，以及 PG17 官方恢复点边界；不寻找全产品安全保证。

user_only_missing：无。真实恢复时才需独立可信身份、现行受托关系与恢复介质；缺失时保持隔离，不要求本轮提供。
