# M2 · 对比 v1 最小结构契约

这是 schema 设计与 JSON 示例，**不是模型实测结果**。Web 与只读程序 API 共用同一后端校验。请求幂等、准入、授权、受理日与结果重放继承 M1；本文件不另造计次方式。

## 输入

| 字段／规则 | v1 契约 |
|---|---|
| schema_version | 必须为 comparison.v1；未知字段整拒，不猜版本 |
| space_id、knowledge_base_ids | 单空间，显式非空库列表；对象须属于显式库范围。任一目标不存在、越界或失权整拒，外部不泄露未授权目标是否存在 |
| objects | 2–4 个；每项 object_id、document_id。ID 为 1–64 个 ASCII 字母／数字／下划线／连字符；object_id 唯一，document_id 不重复。文档只能为当前可查询文档，不能以历史版本冒充新对象 |
| conditions | 1–6 个；每项 condition_id、text。condition_id 同样合法且唯一；text 用 Unicode NFC、去首尾空白后不得空，单条至多 256 Unicode 码点，合计至多 1024 码点；重复判断再合并连续空白，同文条件整拒 |
| 子查询 | objects × conditions ≤24；固定按条件原序、文档 ID 升序展开。服务器在 embedding 调用前做全量检查；超限、重复、空值均整拒，不截断、不静默合并 |
| 初值性质 | 以上数量与文本上限为可配置、未测的受理初值。服务端统一发布给页面；下调须有配置版本，不改已受理执行快照；不代表可达质量／延迟 |
| 版本绑定 | 接受时由后端解析并固定 object_id→document_id→doc_version→index_generation；用户标签、模型输出不得改绑定。相同幂等键换对象／条件视为不同规范输入而冲突 |

```json
{
  "schema_version": "comparison.v1",
  "space_id": "space-1",
  "knowledge_base_ids": ["kb-1"],
  "objects": [
    {"object_id": "product-a", "document_id": "doc-a"},
    {"object_id": "product-b", "document_id": "doc-b"}
  ],
  "conditions": [
    {"condition_id": "offline", "text": "支持离线部署"},
    {"condition_id": "audit", "text": "支持操作审计"}
  ]
}
```

## 输出与四态

v1 的每个对象就是接受时固定的一个所选文档版本，不扩成任意资料集合。所有输入对象×条件恰好各一格，ID 必须精确来自本次输入，不能遗漏、添加或重复。展示顺序保留输入对象与条件顺序；检索轮转顺序与展示顺序分开。

| state | evidence_ids 最小基数与语义 |
|---|---|
| satisfied（满足） | ≥1；直接证明该对象满足该条件，reason 说明适用版本／条件 |
| not_satisfied（明确不满足） | ≥1；直接的明确否定或确定违反必要条件。仅未检索到、型号不匹配、可能不支持均不得进入此态 |
| insufficient（证据不足） | 可为 0；reason 必填并指明缺什么，reason_code 从 NO_CANDIDATES／MISSING_SUPPORT／APPLICABILITY_UNKNOWN 选择。可带仅能部分支持的证据，不能补写无依据事实 |
| conflict（资料冲突） | ≥2 个不同 ID；conflict_sides 必须有双方各≥1 个证据，双方集合互斥、并集恰为 evidence_ids；reason 指明相同适用条件下矛盾。A 满足而 B 不满足只是对象差异，不自动算某格冲突 |

每格 reason 为 1–512 Unicode 码点；其他状态不带 reason_code／conflict_sides。evidence_ids 唯一，必须来自**全请求最终最多五块的实际上下文白名单**，且属于该 object_id 固定文档版本；同块可被多格引用，不能新增邻块／全文。服务端生成 evidence_catalog，包含 evidence_id→库／文档版本／块／来源映射；模型不能输出或控制 URL。冲突确实发生但最终五块不足双方时，返回不足并说明缺口。

同格 conflict 的双方证据须来自该对象固定版本；不同对象的能力差异不强记为冲突。普通问答仍须用其结构化冲突结果报告跨多文档、相同适用条件下同一事实的双方证据，也受全请求 K=5 及来源白名单约束。此处只界定 v1 对比对象，不取消 PRD 四场景冲突题必过与原验收门槛。

以下完整四格、五块目录仅展示 schema。文字不是对任何真实产品的判断；doc-b 的 e4／e5 是同一版本内相互矛盾的两个片段。

```json
{
  "schema_version": "comparison.v1",
  "request_id": "req-123",
  "status": "completed",
  "objects": [
    {"object_id": "product-a", "document_id": "doc-a", "document_version_id": "a-v1"},
    {"object_id": "product-b", "document_id": "doc-b", "document_version_id": "b-v1"}
  ],
  "condition_ids": ["offline", "audit"],
  "evidence_catalog": [
    {"evidence_id": "e1", "document_version_id": "a-v1", "chunk_id": "a-c1"},
    {"evidence_id": "e2", "document_version_id": "a-v1", "chunk_id": "a-c2"},
    {"evidence_id": "e3", "document_version_id": "b-v1", "chunk_id": "b-c1"},
    {"evidence_id": "e4", "document_version_id": "b-v1", "chunk_id": "b-c2"},
    {"evidence_id": "e5", "document_version_id": "b-v1", "chunk_id": "b-c3"}
  ],
  "cells": [
    {"object_id": "product-a", "condition_id": "offline", "state": "satisfied", "reason": "示例片段明确列出离线部署。", "evidence_ids": ["e1"]},
    {"object_id": "product-a", "condition_id": "audit", "state": "not_satisfied", "reason": "示例片段明确说明该版本不提供操作审计。", "evidence_ids": ["e2"]},
    {"object_id": "product-b", "condition_id": "offline", "state": "insufficient", "reason": "未取得该版本离线部署依据。", "reason_code": "MISSING_SUPPORT", "evidence_ids": []},
    {"object_id": "product-b", "condition_id": "audit", "state": "conflict", "reason": "两个示例片段对同一版本是否提供审计作相反表述。", "evidence_ids": ["e4", "e5"], "conflict_sides": {"side_a": ["e4"], "side_b": ["e5"]}}
  ]
}
```

evidence_catalog 的来源定位在真实 API 中由服务端填充；示例只列最小身份，不以示例缺字段放宽来源契约。正式 JSON Schema／响应模型须按上述字段约束、四态分支和跨字段校验实现。

catalog 可包含示例中未被任何格引用的 e3，但它必须精确对应本轮实际传入模型的最终候选及实见片段，不得把调试 TopN 或被裁掉片段列入。SM-2 仍按实见片段直接支撑的原金标证据单元统计，沿用原分母，catalog 存在不自动算命中；SM-3 仅按实际事实结论的引用是否直接支撑统计，不能用未被结论引用的 e3 凑引用支撑率。schema 结构正确、位置可达与语义支撑仍分别验收。

## 零候选与真正失败

全请求最终候选为零时，后端不调用答案模型，仍返回 completed；catalog=[]，全部格统一为 insufficient、reason_code=NO_CANDIDATES、evidence_ids=[]、reason=“当前授权与所选版本内未检索到可用依据”。例如其中一格：

```json
{"object_id":"product-a","condition_id":"offline","state":"insufficient","reason":"当前授权与所选版本内未检索到可用依据。","reason_code":"NO_CANDIDATES","evidence_ids":[]}
```

这是合法、结构化的正常不足答复，按 M1 问答／对比计一次；embedding 的真实成本照记。纯检索零结果不扣产品次数。检索超时、供应方调用失败不能伪装零候选。

若答案模型输出缺格、非法四态、引用越界、冲突证据不足或结构错误，首版只做无语义的围栏／空白清理；仍不合法则整答 ANSWER_VALIDATION_FAILED，不展示草稿、不追加 LLM 修复、不静默降成不足。失败按 M1 释放预留，真实调用成本保留；终态失败同幂等键仅重放失败，新键才发起新请求。语义上是否真正支持结论仍须独立验收，schema 通过不证明事实正确。
