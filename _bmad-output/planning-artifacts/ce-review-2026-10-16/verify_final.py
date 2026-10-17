"""Check documented counterexamples without claiming product runtime validation."""
from pathlib import Path
import json, re, hashlib, difflib
BASE=Path('E:/aaa-project/rag/_bmad-output/planning-artifacts')
OUT=BASE/'ce-review-2026-10-16'
epics=(BASE/'epics.md').read_text(encoding='utf-8')
index=json.loads((OUT/'story-index.json').read_text(encoding='utf-8'))
stories=index['stories']
def ancestors(s):
    found=set()
    def walk(x):
        for d in stories[x]['dependencies']:
            if d not in found: found.add(d); walk(d)
    walk(s)
    return found
allocation=(OUT/'acceptance-allocation.md').read_text(encoding='utf-8')
checks={
 'story_count_42':len(stories)==42,
 'all_23_original_ac_allocated':set(re.findall(r'\| AC-(\d{2})-',allocation))=={f'{i:02}' for i in range(1,24)},
 'story_4_2_only_source_data_then_4_3_view':'AC-10-DATA' in allocation and 'AC-10-VIEW' in allocation and '4.3' not in ancestors('4.2'),
 'story_7_1_source_then_7_2_answer':'AC-13-STRUCT' in allocation and 'AC-13-ANSWER' in allocation and '7.2' not in ancestors('7.1'),
 'story_8_3_prep_then_8_4_recovery':'AC-22-PREP' in allocation and '8.4' not in ancestors('8.3'),
 'no_universal_future_full_ac_gate':'必须运行所列原 UX AC 的完整正反例' not in epics,
 's2_doc_gate_dependency':'2.5' in ancestors('4.1') and '2.3' not in ancestors('4.1') and '2.6' not in ancestors('4.1'),
 'doc_gate_no_generation_budget':'2.3' not in ancestors('2.5'),
 'mix_gate_has_budget_and_doc':{'2.3','2.5'}<=ancestors('2.6'),
 'f0_no_code_dependencies':not stories['9.1']['dependencies'],
 's0_no_p0_or_s7':not any(d.startswith(('2.','9.')) for d in ancestors('1.5')),
 's1_can_run_without_p0':not any(d.startswith('2.') for d in ancestors('3.7')),
 's3_has_budget_and_mix':{'2.3','2.6'}<=ancestors('5.1'),
 'egress_explicit_in_s0':'S0即交付C5 EgressTarget' in epics,
 'ui_expiry_explicit':'到期字段按IA-10初态为空' in epics,
 'credential_secret_lifecycle_explicit':'唯一96位nonce/AAD绑定' in epics,
 'schema_export_and_h_explicit':'导出OpenAPI/JSON Schema/TS及正负样例' in epics,
}
manifest=json.loads((OUT/'review-manifest.json').read_text(encoding='utf-8'))
for item, name in zip(manifest[13:],['epics.md','story-traceability.md']):
    checks[f'frozen_draft_{name}_matches_review']=hashlib.sha256((OUT/'draft'/name).read_bytes()).hexdigest()==item['sha256']
source_unchanged=all(hashlib.sha256(Path(i['path']).read_bytes()).hexdigest()==i['sha256'] for i in manifest[:13])
checks['all_13_upstream_inputs_unchanged']=source_unchanged
result={'checks':checks,'failed':[k for k,v in checks.items() if not v],
 'verified_counterexamples':'document/dependency checks only','product_runtime_tests':'not-executed',
 'reviewers_rereviewed_final':False}
(OUT/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=(OUT/'draft/epics.md').read_text(encoding='utf-8').splitlines(keepends=True)
diff=''.join(difflib.unified_diff(old,epics.splitlines(keepends=True),fromfile='draft/epics.md',tofile='epics.md'))
(OUT/'changes.diff').write_text(diff,encoding='utf-8')
print(json.dumps({'checks':len(checks),'failed':result['failed'],'upstream_unchanged':source_unchanged},ensure_ascii=False))
