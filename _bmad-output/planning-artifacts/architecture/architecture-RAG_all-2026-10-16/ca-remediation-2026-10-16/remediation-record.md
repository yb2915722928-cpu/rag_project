---
title: RAG_all CA 四项深审问题修复与复核记录
date: 2026-10-16
intent: update
status: final-reviewed-ir-pass
implementation_started: false
runtime_tests: not-executed
---

# CA 更新范围与证据

本轮承接[最新深审四项确认发现](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/deep-review-2026-10-16/implementation-readiness.md:25)，按用户授权更新现行架构、相关实施/UX契约和验收条件，随后独立复核并运行IR。原深审及历史baseline保留。修改前15件文件由[input-manifest](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/input-manifest.json)逐件保存快照与SHA-256。

产品范围、原FR/SM/AC编号与验收分母不变；AD-1–14保持原ID。四场景、K≤5、两个全系统gate各默认4/可配1–4、本机重阶段1及原2h含排队规则保持有效。本轮没有应用代码、真实供应方调用、部署或产品测试成绩。

| 发现 | 已写入的最小规则 | 真源与同步 | 实施关闭证据 |
| --- | --- | --- | --- |
| R01 迟发grant跨窗 | send_open全量持续计额；一次grant绑定启动实例，发送child及FD已停、旧grant已销毁后，取随后DB时间作为保守上界，继续留完整W。期限/读钟/失联不自动退额；恢复不从旧计数或领取时间放行 | [C8](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:145)，AD7/11/14、R1/2/5、实施契约§2.5/2.6、S0/P0 | S0跨秒/分钟、检查后暂停、部分写、另一槽、child仍活、controller崩溃、重复封口及恢复；任何真实外发前通过。P0核真实维度；不承诺绝对网络到达窗/厂商永不429 |
| R02 首次登录CSRF循环 | 匿名登录采用精确同源Origin+JSON+固定X-RAG-Login:1；不依赖尚不存在的token。成功旋转会话/token，受控no-store登录/context响应供内存取得；认证Web写保持同源Origin+绑定token，CORS关闭 | [C5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:79)，AD4、实施契约§1、身份IA/AC-01 | S1全新无Cookie可登录；跨源/null/缺Origin、form/缺头不建会话，缺/旧token写入拒绝，重载取得当前token；入口开放前通过 |
| R03 私有缓存边界 | 私有成功/状态/失败/认证/引用/资源一律no-store，gateway禁缓存；首版无ETag/Last-Modified/304，条件请求仍当前鉴权。页面离开清除遮蔽，恢复先失效旧代次/context再当前重核/取数，失败无旧body | [C2](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:20)、[C4](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:53)，AD4/12/13、R4、实施契约§1/5.5、UX归属/历史/AC10/16/18 | S1设施、S2资源、S3问答/历史分别做真实浏览器同URL换账号/撤权、If-*、back/forward及bfcache恢复；不把no-store当历史已清证明 |
| R04 媒体交付 | 五格式原件准确服务器MIME+attachment+有限安全filename/filename*+nosniff。inline只限已核PNG/JPEG页/裁图；文本/MD/提取走受控文本渲染，不透传上游主动类型/原始header，不inline原件 | [C7](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/shared-contracts.md:117)，AD5/12、R2/4、实施契约§5.1/5.5、来源IA/AC10/21 | S2合法含HTML TXT/MD、伪MIME/扩展、CRLF/路径文件名、预览不执行/不外抓；资源入口开放前通过 |

运行验收的完整可观察结果与停止点见[R7四项表](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/runtime-operations.md:130)；上表仅说明规划修复，全部运行用例仍未执行。

本轮未增加技术依赖或改变Stack版本；HTTP/浏览器机制以本轮实际核对的[官方依据E5](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/technology-evidence.md:63)支持。R01选择保守占用以处理任意调度暂停；代价是停发证明不明时相关额度保持阻断，不能以活性为由清额。

独立审阅采用三个全新上下文：rubric与输入对齐、对抗兼容性、技术证据与机制适用性。审阅者不参与本轮写作，读取冻结后的实际字节；每条有效新发现需修复并重新复核。最终裁决由[当前IR](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md)发布，三个镜头均已完成PASS，material新发现0；最终12件字节保持与审阅SHA一致。


## 独立复核完成与当前效力

- [对抗镜头](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/reviews/review-adversarial.md:1)：核心三件全文与原反例，PASS，material 0；实施/UX新增段落抽核不扩大签署范围。
- [技术镜头](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/reviews/review-technology.md:1)：核心四件及本轮官方机制证据，PASS，material 0；未变精确Stack承接同日既有核验。
- [Rubric／输入对齐／IR镜头](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/reviews/review-rubric-ir.md:1)：12件全文与输入双向承接，PASS建议，material 0；低优先N1历史导航建议不阻实施，现行override已明确。

最终[IR为PASS](/E:/aaa-project/rag/_bmad-output/planning-artifacts/implementation-readiness.md:1)，S0可独立开始。确定性检查为lint 0、14个AD／23个原AC稳定、259个文件链接目标与行号有效、12件审阅快照一致、15件修改前快照完整；不是产品测试成绩。详细字节/报告/发布IR完整性由[最终核对](/E:/aaa-project/rag/_bmad-output/planning-artifacts/architecture/architecture-RAG_all-2026-10-16/ca-remediation-2026-10-16/final-integrity.json:1)记录。
