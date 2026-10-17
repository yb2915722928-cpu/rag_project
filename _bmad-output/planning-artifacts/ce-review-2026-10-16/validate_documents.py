"""Validate CE artifact links and immutable upstream input bytes."""
from pathlib import Path
import re, json, hashlib
BASE = Path('E:/aaa-project/rag/_bmad-output/planning-artifacts')
OUT = BASE / 'ce-review-2026-10-16'
manifest = json.loads((OUT/'review-manifest.json').read_text(encoding='utf-8'))
source_integrity = []
for item in manifest[:13]:
    p = Path(item['path'])
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    source_integrity.append({'path':p.as_posix(),'sha256':actual,'unchanged':actual==item['sha256']})
problems=[]; count=0
files=[BASE/'epics.md',OUT/'story-traceability.md']
for name in ['review-record.md','review-coverage.md','review-stories.md','acceptance-allocation.md','review-dispatch.md']:
    p=OUT/name
    if p.exists(): files.append(p)
for p in files:
    content=p.read_text(encoding='utf-8')
    for m in re.finditer(r'\]\((/[^)]+)\)',content):
        count+=1
        raw=m.group(1).split('#',1)[0]
        loc=re.fullmatch(r'(.+?)(?::(\d+))?',raw)
        path=Path(loc.group(1).lstrip('/'))
        if not path.exists(): problems.append({'source':p.as_posix(),'target':raw,'problem':'missing'})
        elif loc.group(2) and int(loc.group(2))>len(path.read_text(encoding='utf-8-sig').splitlines()):
            problems.append({'source':p.as_posix(),'target':raw,'problem':'line-out-of-range'})
    if re.search(r'^<{7}|^={7}|^>{7}',content,re.M): problems.append({'source':p.as_posix(),'problem':'conflict marker'})
    if '{{' in content: problems.append({'source':p.as_posix(),'problem':'template placeholder'})
result={'local_links_checked':count,'link_or_document_issues':problems,'upstream_inputs':source_integrity,
        'upstream_unchanged':all(i['unchanged'] for i in source_integrity),'runtime_tests':'not-executed'}
(OUT/'document-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'links':count,'issues':problems,'upstream_unchanged':result['upstream_unchanged']},ensure_ascii=False))
