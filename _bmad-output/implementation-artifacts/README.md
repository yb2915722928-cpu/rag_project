# RAG_all 冲刺与运行验收跟踪

当前[IR为规划PASS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md:1)。[冲刺状态](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/sprint-status.yaml:1)含9 Epic及42 Story全部backlog，9项回顾optional。尚无单独故事文件、未开始实现；规划PASS不自动提升为ready-for-dev。

[运行门/子例台账](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/runtime-acceptance-status.yaml:1)的25个门/子门与45组分派全部not-executed、无运行证据。not-executed不是failed，也不是已核缺凭据的blocked；后续只能根据真实执行逐项记录通过/失败/阻塞及原始证据，保留unknown/真实成本。原[验收分派](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ce-review-2026-10-16/acceptance-allocation.md:1)及原AC全部实质正反子句有效，分组行数不改变运行分母。

唯一实施输入是现行[epics](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:1)，历史draft/baseline不作为另一个Epic源。[依赖闭包快照](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ir-sp-review-2026-10-16/story-dependencies.json:1)仅对应本轮受审字节，未来修改须按现行故事刷新，不能用旧快照推翻新条款。

可从[Story 1.1](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:184)运行bmad-build。主线先1.1→1.2→1.3/1.4→1.5，再允许P0的2.1与S1的3.1并行；Epic编号不是全P0串行屏障。F0的9.1须在任何首次调优前独立前移，不依代码或S6。未估算虚构工时、结束日期或已用运行额度。

| 必须保持的边界 | 跟踪规则 |
| --- | --- |
| P0-DOC-1/4与MIX-1/4 | 分别依据真实证据消费。2.5/2.6整条未完成不覆盖已证子门；某档通过不等整条故事完成。S2只需所用DOC，S3实际并存组合需对应MIX，S6补目标4C4GB；未证4不开4 |
| R01 | 任意真实外发含首次P0/接入验证前先过全部S0本地门 |
| R02 | S1身份入口开放前完成首次登录及认证写正反例 |
| R03 | S1设施、S2资源、S3答案/历史各入口前真实浏览器分别验；新增比较同门复验 |
| R04 | S2资源入口开放前完成全部安全媒体正反例 |
| S6/S7 | 目标机及两次新epoch可信恢复未过不上线；原SM/专项/独立权限分母未全过不称整期完成 |

完整两位独立只读报告、主John核实、基线/SHA/差异及生成校验见[复核记录](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ir-sp-review-2026-10-16/review-record.md:1)。
