---
title: 'Story 1.1 C1 原生负零的金额往返'
status: in-progress
route: dispatch
baseline_commit: a52ae3090948e7eeea6df87590f15ce35351d247
context:
  - E:/aaa-project/rag/AGENTS.md
  - E:/aaa-project/rag/_bmad-output/implementation-artifacts/spec-1-1-contract-models.md
---

## Intent 与唯一归属

修复静态审查 C1-NZ：原生 Decimal 负零通过非负校验，却输出带负号字符串，违反自身金额 schema 且无法重新读取。保持已批准非负金额和十进制字符串语义，不扩展账务业务或拒绝合法零值。

当前B作者Boole继续作为唯一DeepSeek默认实现者，只允许修改 [scalars.py](/E:/aaa-project/rag/backend/src/rag_app/contracts/scalars.py:99) 的金额处理/序列化，新增 `backend/tests/test_decimal_wire_zero.py` 与 `docs/story-1-1-decimal-zero-delivery.md`。另允许只纠正 B 交付文档中 attempts=2 的统计文字：实际为三条而非两条。不得改已静态复核的其他B/HTTP/H/worker/D源码、既有测试、锁、主控台账或Git index。

## Code Map

`decimal_amount` 接受 Decimal/字符串，正则只约束字符串，有限且 `result < 0` 为假的原生负零保留符号；`FiniteDecimal` 以固定小数格式输出。`Money` 已直接使用此别名，无需修改DTO；`PUBLIC_MODELS`/`PUBLIC_ENUMS`与schema形状不变。参考 [审查报告](/E:/aaa-project/rag/docs/story-1-1-preparation-review.md:389) 的 C1-NZ 段即可，不重读全部历史。

## Tasks & Acceptance

- [ ] Given原生Decimal负零（含 `-0`、`-0.00`），when构造并序列化Money，then输出为无负号零，保留原小数位/精度、不使用float或金额舍入，并能通过后端自身schema格式与JSON再读取。
- [ ] Given正常零/正金额、真实负金额、非有限/float及非法带负号wire字符串，when沿用同一入口，then既有允许/拒绝规则不变；unknown仍用null而非零。
- [ ] 新增针对本缺陷的回归源码，覆盖普通负零/带小数负零的dump→读取、schema格式与正常精度，不用大量镜像实现断言代替行为。
- [ ] 只做源码准备。应用运行/测试只允许Netcatty Linux精确CPython3.12.8；固定Gitee提交未到位，不本机运行、不重试外部认证或SFTP、不提交/暂存。未执行即记录not-executed。

## 交付

原缺陷和旧hash证据不覆盖。交付列出最小修改、新hash、测试源码及未运行原因，随后冻结释放。主会话交回原独立审查者仅对该差异静态复核；真实Linux开发者测试、正式B工件和父Story完成门全部保留。
