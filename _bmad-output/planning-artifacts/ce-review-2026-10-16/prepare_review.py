"""Reproduce CE document indexes and static evidence; never runs product tests."""
from pathlib import Path
import re, json, hashlib

ROOT = Path('E:/aaa-project/rag')
PLAN = ROOT / '_bmad-output/planning-artifacts'
OUT = PLAN / 'ce-review-2026-10-16'
EPICS = PLAN / 'epics.md'
text = EPICS.read_text(encoding='utf-8')
matches = list(re.finditer(r'^### Story (\d+\.\d+)：(.+)$', text, re.M))
stories = {}
for i, match in enumerate(matches):
    end = matches[i+1].start() if i+1 < len(matches) else len(text)
    block = text[match.end():end].split('\n## ')[0]
    dep = re.search(r'\*\*依赖：\*\* (.*?)。\*\*来源：\*\* (.+)', block)
    assert dep, match.group(1)
    # Explanatory "不依赖" clauses explicitly exclude the IDs that follow.
    positive_dependencies = dep.group(1).split('不依赖',1)[0]
    dependencies = re.findall(r'(?<!\d)(\d+\.\d+)(?!\d)', positive_dependencies)
    ac = len(re.findall(r'^- \*\*Given\*\*', block, re.M))
    stories[match.group(1)] = dict(title=match.group(2), line=text[:match.start()].count('\n')+1,
        dependencies=dependencies, preconditions=dep.group(1), sources=dep.group(2), ac_count=ac)

def link(s):
    return f'[Story {s}](/{EPICS.as_posix()}:{stories[s]["line"]})'

# Primary implementation/validation owners, independently curated from story ACs.
mapping = {}
def assign(family, rows):
    for key, values in rows.items():
        mapping[f'{family}{key}'] = values.split()
assign('FR-', {
 '1':'3.1 3.2 3.3 3.4', '2':'3.3', '3':'3.4 4.3 4.4 5.1 5.4 8.1',
 '4':'1.2 1.3 2.1 3.6 3.7 5.2 5.6 8.1 8.2 8.3 8.4',
 '5':'3.5 5.5 6.2', '6':'2.2 3.6 4.1 4.2', '7':'2.2 2.4 4.2 4.3 7.1',
 '8':'4.4 5.4 8.1 8.2 8.4', '9':'2.3 5.1 5.2 5.3 6.1 6.2 7.2',
 '10':'6.1', '11':'5.3', '12':'2.3 6.2', '13':'2.4 7.1 7.2',
 '14':'3.2 4.2 4.3 5.4 6.2 7.2', '15':'1.2 1.4 4.5 5.2 8.4',
 '16':'1.2 3.1 3.3 3.4 5.6 8.3 8.4 9.3 9.5'})
assign('NFR-', {'1':'3.1 3.4 3.5 4.3 5.1 5.4 5.5 8.4 9.4',
 '2':'1.2 1.3 1.4 3.6 4.1 4.2 4.4 4.5 5.2 8.1 8.2 8.4',
 '3':'1.1 1.2 5.6 8.3 9.2 9.5', '4':'2.3 2.5 2.6 8.3 9.2 9.3',
 '5':'1.1 1.5 8.2 8.3 8.4 9.1 9.2 9.5', '6':'1.1 1.4 2.1 3.1 4.3 8.3 9.1 9.5'})
assign('SM-', {'1':'9.4','2':'9.4','3':'9.4','4':'9.4','5':'7.1 7.2 9.4','6':'9.4','7':'9.3 9.4 9.5'})
assign('IA-', {'01':'3.1 3.2','02':'3.2 3.3','03':'3.4','04':'4.1 4.2 4.4 8.1',
 '05':'4.1','06':'4.2 4.3 4.5 7.1','07':'5.1 5.2 5.3 5.4 5.6 6.1 7.2',
 '08':'6.2','09':'4.3 5.4 6.2 7.1','10':'3.5 3.6 5.6','11':'3.3 3.4','12':'3.7 8.3 8.4'})
assign('G-', {'01':'3.2 4.3 5.4','02':'3.1 3.3 4.1 5.3','03':'3.6 3.7 4.1 5.3',
 '04':'3.2 4.1 5.3 6.2','05':'3.3 3.5 4.5 5.2','06':'5.2 5.4 6.2',
 '07':'3.4 5.1 5.5 6.2','08':'3.2 5.4','09':'3.3 3.5 4.4 4.5','10':'3.2 4.3 6.2',
 '11':'3.6 4.2 4.5 5.3 5.6','12':'3.2 4.3 5.3 5.5'})
assign('AC-', {'01':'3.1 3.7','02':'3.3','03':'3.3 3.4 5.1','04':'3.4 4.5','05':'3.7 8.3',
 '06':'3.6 4.1','07':'3.6 4.1 4.4','08':'4.2 4.4 7.1','09':'4.5','10':'4.3 7.1',
 '11':'6.1','12':'5.3','13':'7.1 7.2','14':'6.2','15':'5.2 5.3 5.4 6.2','16':'4.4 5.4',
 '17':'8.1 8.2','18':'3.2 4.3 5.4','19':'3.5 5.5 6.2','20':'3.6 3.7 5.6 8.1 8.2',
 '21':'3.2 4.3 6.2','22':'8.4','23':'3.2 6.2'})
assign('UX-DR', {'01':'3.2','02':'3.2','03':'3.2 3.4 5.1 6.2','04':'3.4 4.2 4.4 8.1',
 '05':'4.1','06':'4.2 4.5','07':'4.3 7.1','08':'5.1 5.2 5.3 6.1 7.2','09':'5.3 7.2',
 '10':'6.2','11':'5.6 6.2','12':'3.5 5.5','13':'3.6 5.6','14':'3.3 3.4 3.7 8.1',
 '15':'3.2 3.3 3.5 4.4 4.5','16':'3.2 4.5 5.6','17':'3.1','18':'3.2','19':'3.2 4.3 6.2',
 '20':'3.2 4.3 6.2','21':'3.2 4.3 5.4','22':'4.3'})
assign('AR-', {'01':'1.1','02':'1.1 1.2 3.6','03':'1.2','04':'1.3 1.5','05':'1.3 2.1 2.5 2.6',
 '06':'1.4','07':'2.2 4.2','08':'1.1 2.3 5.3','09':'3.1 8.3 8.4','10':'1.5 2.1 2.2 2.3 2.4 2.5 2.6',
 '11':'9.1 9.3','12':'1.1'})
assign('AD-', {'1':'1.1 5.5','2':'1.1','3':'1.2 3.6 4.2 5.2 8.1','4':'3.1 3.4 5.5','5':'1.1 4.3 5.3',
 '6':'1.4 4.2 4.4','7':'1.2 1.3 1.4 2.1','8':'1.2 3.6 5.2 5.6','9':'4.2 8.1 8.2',
 '10':'2.3 5.1 5.3 6.2 7.2','11':'1.3 5.2 5.4','12':'3.2 4.2 4.3 5.4','13':'3.1 8.3 8.4','14':'1.5 2.5 9.1 9.4'})
assign('C', {'1':'1.1 5.2','2':'1.1 3.2 5.4','3':'2.2 4.3 5.3','4':'1.2 3.6 4.2 5.2 8.1',
 '5':'1.2 3.1 3.5 3.7','6':'2.3 5.3 6.2','7':'4.2 4.3','8':'1.3 2.1 2.5 2.6 8.4'})
assign('运行R', {'1':'1.2 1.3','2':'1.2 1.4 4.1 4.5','3':'1.4 4.4','4':'1.1 3.2 8.3',
 '5':'8.4','6':'1.4 2.5 8.3 9.2','7':'1.5 9.4','8':'1.1 1.4 8.3'})
assign('修复R', {'01':'1.3 1.5 2.1 2.5 8.4','02':'3.1 3.7','03':'3.2 4.3 5.4 8.4','04':'4.3'})
assign('切片', {'S0':'1.1 1.2 1.3 1.4 1.5','P0':'2.1 2.2 2.3 2.4 2.5 2.6',
 'S1':'3.1 3.2 3.3 3.4 3.5 3.6 3.7','S2':'4.1 4.2 4.3 4.4 4.5',
 'S3':'5.1 5.2 5.3 5.4 5.5 5.6','S4':'6.1 6.2','S5':'7.1 7.2','S6':'8.1 8.2 8.3 8.4',
 'F0':'9.1','S7':'9.2 9.3 9.4 9.5'})
assign('实施§', {'1':'3.1 3.4 3.5 5.1 5.5','2.1':'3.6 4.1 4.4 5.6','2.2':'5.2',
 '2.3':'5.2','2.4':'3.6 4.1','2.5':'1.2 2.1','2.6':'1.3 1.4 2.5 2.6 4.2',
 '2.7':'4.5','3.1':'4.2 8.1 8.2','3.2':'6.2','3.3':'4.2 4.3 7.1','3.4':'2.2 2.4',
 '3.5':'1.1 5.1 5.2 5.3','3.6':'2.3 5.3','3.7':'2.3 5.3 6.2','3.8':'1.3 2.1 2.5 2.6 5.1',
 '4.1':'3.1 8.3 8.4','4.2':'8.4','4.3':'8.4','4.4':'8.4','5.1':'3.1 3.4 4.1 4.5 5.5 6.2',
 '5.2':'1.1 3.2 4.2 5.2 5.3','5.3':'1.1 4.5 5.3','5.4':'1.1 3.6 4.2 5.2','5.5':'3.2 4.3 5.4'})
assign('技术E', {'1':'1.1','2':'1.1','3':'1.1 8.3','4':'2.1 2.2 2.3 2.4 2.5 2.6','5':'1.3 3.1 3.2 4.3 5.4'})

# Same-epic backward-only plus cross-epic acyclic dependency graph.
issues=[]
for s, value in stories.items():
    for d in value['dependencies']:
        if d not in stories: issues.append(f'missing dependency {s}->{d}')
        elif int(s.split('.')[0]) == int(d.split('.')[0]) and float(d) >= float(s):
            issues.append(f'forward dependency {s}->{d}')
    if not 2 <= value['ac_count'] <= 4: issues.append(f'AC count {s}: {value["ac_count"]}')
visited, active=set(), set()
def walk(s):
    if s in active: issues.append(f'cycle {s}'); return
    if s in visited: return
    active.add(s)
    for d in stories[s]['dependencies']:
        if d in stories: walk(d)
    active.remove(s); visited.add(s)
for s in stories: walk(s)
for k, ids in mapping.items():
    for s in ids:
        if s not in stories: issues.append(f'mapping missing {k}->{s}')
if len(stories)!=42: issues.append(f'story count {len(stories)}')

lines=['# CE — 需求与Story双向追踪', '',
 '本索引只表示规划分派，产品运行全部未执行。正向表列首次实现/针对性验收主责，不能以统一S7验证掩盖早期缺口。', '',
 '权威文件导航及共同完成条件见'+f'[Epics](/'+EPICS.as_posix()+':1)。编号前缀“运行R”与“修复R”严格区分。所有Web故事继承本页AC-21/23与G-01–12；跨故事原AC子例首次责任见[验收分派](/'+(OUT/'acceptance-allocation.md').as_posix()+':1)，不是每个早期故事先做未来整组用例。', '',
 '## 正向：原需求/契约 → Story', '', '| 需求/条款 | 具体承接 |', '| --- | --- |']
for k, values in mapping.items(): lines.append(f'| {k} | '+ '、'.join(link(s) for s in values)+' |')
lines += ['', '## 反向：Story → 原输入及验收', '', '| Story | 依赖（完整条件见正文） | 原需求、架构/UX及验收来源 |', '| --- | --- | --- |']
for s,v in stories.items(): lines.append(f'| {link(s)} {v["title"]} | '+('、'.join(link(d) for d in v['dependencies']) or '无代码前置')+f' | {v["sources"]} |')
lines += ['', '## 条件依赖与真实门', '',
 '1. 1.5通过后，2.1与3.1可并行；2.2/2.3各依2.1，2.4依2.2；2.5只依2.2（含2.1），产可分别消费的P0-DOC-1/4；2.6依2.3+2.5对应档，产P0-MIX-1/4。未证档位保持禁用。',
 '2. 4.1消费3.7+2.2对应格式/来源/embedding+2.5所用DOC档位，不依2.3或2.6整体状态；P0不是整包PASS。S2不依图意/答案预算/S3页面。',
 '3. 5.1开始S3需S2全部门和2.3完整预算，实际开放并存组合另取2.6对应MIX证据；7.1开始S5另需2.4真图意；8.3上线需2.5/2.6目标4C4GB证据补齐。',
 '4. 9.1不依赖8.x，可前移任意首次调优之前；9.2之后才是S7。若S7前调优，相关故事额外依F0记录；不将S7运行成绩倒置为S0前置。',
 '5. R02阻身份开放，R03在S1/S2/S3分别阻对应入口，R04阻S2资源开放，R01阻任何真实外发。',
 '', '## 追踪计数', '',
 'FR 16；NFR 6；SM 7；IA 12；G 12；原UX AC 23；UX-DR 22；AR 12；AD 14；C 8；运行R 8；修复4；原切片10；实施契约实质子节25；技术证据E1–5；9 Epic / 42 Story。计数不是已实现覆盖率。']
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'story-traceability.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'story-index.json').write_text(json.dumps({'stories':stories,'forward_mapping':mapping},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

inputs=re.findall(r'^  - (.+)$', text.split('---',2)[1],re.M)
manifest=[]
for rel in inputs:
    p=PLAN/rel
    data=p.read_bytes()
    manifest.append({'path':p.as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'lines':len(data.decode('utf-8-sig').splitlines())})
manifest += [{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in [EPICS,OUT/'story-traceability.md']]
(OUT/'current-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'static-checks.json').write_text(json.dumps({'epics':len(set(s.split('.')[0] for s in stories)), 'stories':len(stories), 'acceptance_criteria':sum(s['ac_count'] for s in stories.values()),'mapping_entries':len(mapping),'dependency_issues':issues,'runtime_tests':'not-executed'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'epics':9,'stories':len(stories),'issues':issues},ensure_ascii=False))
