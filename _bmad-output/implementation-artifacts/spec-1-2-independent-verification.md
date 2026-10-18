---
title: 'Story 1.2 独立运行验证'
type: chore
created: '2026-10-18'
status: done
route: dispatch
review_loop_iteration: 0
---

<frozen-after-approval>

## Intent

作为未参与实现的 Step 5 Preview，直接对固定提交执行原 Story 1.2 四项 AC 与受影响回归。先读 [工作集](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-working-set.md:1)、[原验收](/E:/aaa-project/rag/_bmad-output/planning-artifacts/epics.md:197)、[证据台账](/E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-2-acceptance-ledger.md:1)，再读实际代码和开发者交付。

## Boundaries & Constraints

独立验证不修改应用/测试/部署/Git/主控状态；唯一本地写入为 [验证报告](/E:/aaa-project/rag/docs/story-1-2-independent-verification.md:1)。可以在隔离目录执行受控只读诊断和假件输入，不修实现。不要求后续 Story 测试先通过，不追加通用硬化。当前缺陷须报告主控转原开发者。

只在已分配的 Netcatty 时段操作 Linux；不与其他角色并发 terminal RPC。使用 `/opt/rag-story-1-2/independent` 独立 Gitee 检出和 venv，固定提交由主控通知，运行前核 commit、backend tree、关键源码/锁 hash。精确 CPython3.12.8、PG18.6/vector0.8.7，既有0400测试 env仅加载不输出。PG只用独占schema，不清其他项目资源。原始证据归档 `/fileOfRag/testOfRAG/metadata/story-1-2/independent`。

## Tasks & Acceptance

- [x] 核 epoch重启/矛盾/缺失与旧fence拒绝；四类能力端口显式假件，无真实外发。
- [x] 实际 Linux 子进程故障矩阵涵盖 prepared前后/may_have_sent后/响应前后；grant唯一、unknown=NULL、权限/IPC/停止/槽复用符合AC2。
- [x] DNS/HTTPS/host-port/全部A-AAAA/IP绑定/TLS/redirect/Authorization分域/秘密哨兵实际通过AC3测试；不向供应方探测。
- [x] 真实PG运行迟到事实/重复/冲突/旧epoch和锁序/事务外等待；迁移up/down/up及本条影响的namespace/启动回归。当前必需负例不可skip。
- [x] 对照测试调用路径确认台账每个子句有对应证据；不只转述开发者。报告命令、版本、预期/实际、退出码、JUnit统计、hash和未通过项。

## Acceptance Criteria

Given 主控发布的固定提交，When 独立运行，Then 当前四条原 AC 均有真实 Linux/PG/显式假件证据，或准确报告失败/阻塞；不把后续限流/清理/供应方或1.1历史结果重新签为本条通过。

</frozen-after-approval>

## Implementation Notes

首阶段先只读并回复ready，等待 `VERIFICATION_MODEL_RELEASE` 与固定提交/terminal时段；主控核实际模型后开放。使用模型默认推理，不自行更换模型。完成后保留实例供具体问题的相关复核。

首阶段只需工作集/原AC/台账的简短就绪核对，8行内回复；A/C仍有已证当前缺口在修正，不提前对变动代码下运行结论，不调用Netcatty、不写报告。代码冻结和开发者测试完成后主控才给最终固定提交/源码hash和验证时段。只据具体当前AC检查，零发现允许。

主控追加分段独立验证：E/D执行响应尚未恢复时，先验已经developer通过且源稳定的96c64fb基础（A/B/C），不验本地未发布E草稿，不签全Story；终端用已实测94b连接。基础验证可按当前文件合并非PG一次、--require-postgres -m postgres一次，保留当前15PG门；D部署及E矩阵明确pending，不能用独立基础结果代替它们。基础报告写同一唯一报告的partial状态，后续源稳定后只补实质新变更的E/D，不无故重跑基础。该分段不减少父AC或独立分母。

## Verification

优先运行当前专题及迁移/启动必要回归。无新Web表面，不跑前端/browser无关套件。适当检查通过即停止，只因实质新改动/实际失败/明确未关闭问题再测。
