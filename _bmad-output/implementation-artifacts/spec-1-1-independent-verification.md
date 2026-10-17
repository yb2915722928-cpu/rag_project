---
title: 'Story 1.1 独立运行验证'
status: ready-for-dev
route: dispatch
baseline_commit: dd44834383de2bd9af9768a6ecc7fe2c48427eff
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-working-set.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/story-1-1-acceptance-ledger.md
  - E:/aaa-project/rag/docs/story-1-1-linux-developer-gates.md
  - E:/aaa-project/rag/docs/story-1-1-frontend-delivery.md
  - E:/aaa-project/rag/docs/story-1-1-deploy-delivery.md
---

## Intent 与前置

Step 5 Preview默认档位、未参与实现的新实例，独立验证当前Story原四AC。A/B开发者门和C单元/构建已交，可先独立核对这些原始证据；D及浏览器仍在执行时只列pending，交付后再验对应项，不能重开已经完成的验证或提前声称父Story完成。

## 唯一归属

只写 `docs/story-1-1-independent-verification.md` 与服务器本任务证据，不改应用、测试、锁、部署、主控状态或Git。先等主控核实实际模型。发现问题报告主控交原作者修复，验证者不兼任实现。Netcatty先get_environment，terminal时段由主控独占分配，未授予不并发请求；等待时只做证据/源码只读核对。

## Tasks & Acceptance

- [ ] Given主控提供固定Gitee提交、当前文件/hash和实际四服务环境，when核对，then输入、解释器/锁、PG/扩展、四服务版本均对应实际字节；检查已有开发者原始日志/JUnit与计数，不把报告自述当唯一证据。
- [ ] Given精确CPython3.12.8和隔离PG18.6/vector0.8.7，when在Linux独立运行一次当前后端必需回归（含require-postgres八项），then保存原始命令、退出码、JUnit和skip/筛除分母；非目标解释器负例独立真实执行。复用安全凭据文件，仅source，不打印DSN/秘密，不清理非本任务schema。
- [ ] Given正式contracts，when独立执行check及52样例，then真实输出一致；comparison等未来业务仍按原规划延期，不扩验收分母，不额外重新生成未变化工件。
- [ ] Given正式前端锁及源码，when独立核锁/当前单元测试和实际gateway页面，then类型方向正确、同源health与失败/超时状态、320/768/1440/200%及键盘要求有真实证据。已有相同源码构建证据可审阅，不重复构建不相关目标。
- [ ] Given四服务实际运行，when核验liveness、gateway维护探针/缓存边界和已有停止/重启/干净重建证据，then与原D要求一致，必要的实际访问有原始结果；不把模拟或静态检查当真实运行。不要扩未来上传、供应方或目标性能业务。
- [ ] Given当前结果，when交付，then逐AC列passed/failed/not-executed及准确证据，独立发现只记录可证问题和影响；适当验证通过就停止，不追加通用硬化、假设性风险或新测试矩阵。

## 证据与交付

活动工作在 `/opt/rag-story-1-1` 本地FS，测试材料/最终证据归档 `/fileOfRag/testOfRAG/metadata/story-1-1/independent-verification`。主控提供最新提交与运行访问方式；有真实环境阻塞时一次报告具体证据，继续独立可做项，不空转复测。

报告变更文档/hash、全部命令/计数、逐项AC、缺陷与未执行门。正式全新6.1 Sol/medium代码审查另行执行，本验证者不替代。
