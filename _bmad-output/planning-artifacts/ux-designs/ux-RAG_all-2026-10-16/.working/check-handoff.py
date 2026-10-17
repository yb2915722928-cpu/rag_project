"""Check design artifacts only; this is not an application or product test."""
from pathlib import Path
import re
import json
import hashlib
import xml.etree.ElementTree as ET
from PIL import Image
import yaml

w=Path(__file__).resolve().parents[1]
result_path=w/'.working/handoff-check.json'
result_path.write_text('{}',encoding='utf-8')
docs=list(w.glob('*.md'))+list((w/'.working').glob('source-*.md'))+[w/'mockups/INDEX.md',w/'wireframes/key-surfaces.md']
errors=[]
links=0
text={p.name:p.read_text(encoding='utf-8-sig') for p in docs}

def fm(name):return yaml.safe_load(text[name].split('---',2)[1])
d,e=fm('DESIGN.md'),fm('EXPERIENCE.md')
for p in docs:
    s=p.read_text(encoding='utf-8-sig')
    for target in re.findall(r'\]\(([^)]+)\)',s):
        target=target.strip('<>')
        if target.startswith(('https://','http://','#')):continue
        m=re.fullmatch(r'(/?[A-Za-z]:/[^:]+?)(?::(\d+))?(?:#[^\s]*)?',target)
        if not m:errors.append([p.name,'non-absolute-link',target]);continue
        f=Path(m[1].lstrip('/'));links+=1
        if not f.exists():errors.append([p.name,'missing-link',target])
        elif m[2] and int(m[2])>len(f.read_text(encoding='utf-8-sig').splitlines()):errors.append([p.name,'bad-line',target])

for label,data in [('DESIGN',d),('EXPERIENCE',e)]:
    if data.get('status')!='final':errors.append([label,'not-final'])
    for src in data.get('sources',[]):
        p=Path(src)
        if not p.is_absolute():p=w/p
        if not p.exists():errors.append([label,'missing-source',src])

refs=set(re.findall(r'\{((?:colors|typography|rounded|spacing|components)\.[^{}]+)\}',text['DESIGN.md']+text['EXPERIENCE.md']))
for ref in refs:
    v=d
    for k in ref.split('.'):
        if not isinstance(v,dict) or k not in v:errors.append(['undefined-token',ref]);break
        v=v[k]
for k,c in d['colors'].items():
    if not re.fullmatch(r'#[0-9A-Fa-f]{6}',c):errors.append(['non-hex-color',k,c])

def first_table_names(s,section):
    block=s.split('## '+section+'\n',1)[1].split('\n## ',1)[0]
    rows=[];started=False
    for line in block.splitlines():
        if line.startswith('|'):
            started=True;rows.append(line.split('|')[1].strip())
        elif started:break
    return rows[2:]
components=list(d['components'])
for section,name in [('Components','DESIGN.md'),('Component Patterns','EXPERIENCE.md')]:
    rows=first_table_names(text[name],section)
    if set(rows)!=set(components):errors.append(['components-mismatch',name,rows])

expected_design=['Brand & Style','Colors','Typography','Layout & Spacing','Elevation & Depth','Shapes','Components',"Do's and Don'ts"]
if re.findall(r'^## (.+)$',text['DESIGN.md'],re.M)!=expected_design:errors.append(['design-section-order'])
for section in ['Foundation','Information Architecture','Voice and Tone','Component Patterns','State Patterns','Interaction Primitives','Accessibility Floor','Key Flows','Responsive & Platform','Inspiration & Anti-patterns']:
    if '## '+section+'\n' not in text['EXPERIENCE.md']:errors.append(['missing-experience-section',section])
ac=re.findall(r'^## AC-(\d+) ',text['acceptance.md'],re.M)
if ac!=[f'{n:02}' for n in range(1,24)]:errors.append(['ac-sequence',ac])
for block in re.split(r'^## AC-\d+ .*$',text['acceptance.md'],flags=re.M)[1:]:
    if not all(x in block for x in ['正例','反例','证据：','映射：']):errors.append(['ac-incomplete'])
ia=re.findall(r'^## IA-(\d+) ',text['page-contracts.md'],re.M)
if ia!=[f'{n:02}' for n in range(1,13)]:errors.append(['ia-sequence',ia])
for name in ['DESIGN.md','EXPERIENCE.md','page-contracts.md','acceptance.md']:
    if re.search(r'\[ASSUMPTION\]|status: draft|\[Sally设计提案\]',text[name]):errors.append(['unclosed-marker',name])

svg_files=sorted((w/'mockups').glob('M*.svg'))
for p in svg_files:
    node=ET.parse(p).getroot()
    for item in node.iter():
        if item.tag.endswith(('script','foreignObject','image')):errors.append(['non-static-svg',p.name,item.tag])
    for spine in ['DESIGN.md','EXPERIENCE.md']:
        if p.name not in text[spine]:errors.append(['unlinked-svg',spine,p.name])
png_files=sorted((w/'mockups').glob('*.png'))
for p in png_files:
    with Image.open(p) as im:
        im.verify()
render=json.loads((w/'mockups/render-check.json').read_text(encoding='utf-8'))
if any(render['out_of_canvas_text'].values()):errors.append(['mock-text-overflow'])

def lum(color):
    vals=[int(color[n:n+2],16)/255 for n in (1,3,5)]
    vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals]
    return sum(v*c for v,c in zip(vals,[.2126,.7152,.0722]))
contrast={}
for fg,bg,minimum in [('text-primary','surface',4.5),('text-secondary','surface',4.5),('on-action','action',4.5),('focus','canvas',3),('border-control','surface',3),('success','success-surface',4.5),('danger','danger-surface',4.5),('warning','warning-surface',4.5),('info','info-surface',4.5)]:
    a,b=sorted([lum(d['colors'][fg]),lum(d['colors'][bg])]);ratio=(b+.05)/(a+.05)
    contrast[fg+'/'+bg]=round(ratio,2)
    if ratio<minimum:errors.append(['contrast-below-target',fg,bg,ratio])

expected={
    'prd.md':('prds/prd-RAG_all-2026-10-15/prd.md','0963d529922a6b3812c8f8311f29f5112a537a59ca62616f4dc45a245baaa299'),
    'implementation-contract.md':('prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-contract.md','c324fc9640debb90fa66d689660c2a96b62922a1e7e77a2551adfd9680476900'),
    'implementation-slices.md':('prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15/implementation-slices.md','02e3d53ad13011fea172f58a8fb0a5b82d371ba91999421f672b28cd4aa6a352')}
hashes={k:hashlib.sha256((w.parents[1]/p).read_bytes()).hexdigest()==h for k,(p,h) in expected.items()}
if not all(hashes.values()):errors.append(['upstream-changed',hashes])
result={'kind':'design-artifact-check-only','status':'pass' if not errors else 'fail','markdown_files_checked':len(docs),'file_links_checked':links,'token_paths':len(refs),'colors':len(d['colors']),'components':len(components),'ia_surfaces':len(ia),'acceptance_groups':len(ac),'svg':len(svg_files),'png':len(png_files),'static_contrast_ratios':contrast,'source_hashes_unchanged':hashes,'text_overflow':0 if not any(render['out_of_canvas_text'].values()) else 1,'product_runtime_tests':'not executed','errors':errors}
result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
