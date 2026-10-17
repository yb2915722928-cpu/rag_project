"""Render offline design references as SVG + PNG; no application implementation."""
from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'mockups'
OUT.mkdir(exist_ok=True)
DESIGN = yaml.safe_load((ROOT / 'DESIGN.md').read_text(encoding='utf-8').split('---', 2)[1])
C = DESIGN['colors']
FONT = 'C:/Windows/Fonts/msyh.ttc'
BOLD = 'C:/Windows/Fonts/msyhbd.ttc'
FONTS = {}

def font(size, bold=False):
    k = (size, bold)
    if k not in FONTS:
        FONTS[k] = ImageFont.truetype(BOLD if bold else FONT, size)
    return FONTS[k]

class Sheet:
    def __init__(self, name, title, width=1600, height=1040):
        self.name, self.w, self.h = name, width, height
        self.im = Image.new('RGB', (width, height), C['canvas'])
        self.d = ImageDraw.Draw(self.im)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>', f'<rect width="{width}" height="{height}" fill="{C["canvas"]}"/>']
        self.errors = []
        self.rect(0, 0, width, 40, C['text-primary'])
        self.text(24, 10, title, 14, C['surface'], True)
        self.text(width-248, 10, '模拟资料 · 设计参考 · 非运行结果', 13, C['surface'])

    def rect(self, x, y, w, h, fill, stroke=None, radius=4, sw=1):
        box = (x, y, x+w, y+h)
        self.d.rounded_rectangle(box, radius=radius, fill=fill, outline=stroke, width=sw)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')

    def line(self, x1, y1, x2, y2, color=None, width=1):
        color = color or C['border']
        self.d.line((x1,y1,x2,y2), fill=color, width=width)
        self.svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')

    def text(self, x, y, value, size=14, color=None, bold=False):
        color = color or C['text-primary']
        value = str(value)
        f = font(size, bold)
        length = self.d.textlength(value, font=f)
        if x < 0 or x+length > self.w or y < 0 or y+size*1.3 > self.h:
            self.errors.append({'text':value, 'x':x, 'y':y, 'width':length})
        self.d.text((x,y), value, font=f, fill=color, anchor='lt')
        self.svg.append(f'<text x="{x}" y="{y}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" font-weight="{600 if bold else 400}" fill="{color}" dominant-baseline="text-before-edge">{escape(value)}</text>')
        return length

    def para(self, x, y, value, width, size=14, color=None, bold=False, lh=None):
        lh = lh or round(size*1.65)
        row = ''
        for ch in value:
            if ch == '\n' or self.d.textlength(row+ch, font=font(size,bold)) > width:
                if ch in '，。；：！？、）》”’' and len(row) > 1:
                    self.text(x,y,row[:-1],size,color,bold)
                    y += lh
                    row = row[-1] + ch
                else:
                    self.text(x,y,row,size,color,bold)
                    y += lh
                    row = '' if ch == '\n' else ch
            else: row += ch
        if row: self.text(x,y,row,size,color,bold); y += lh
        return y

    def button(self, x, y, label, primary=False, danger=False, width=None):
        width = width or round(self.d.textlength(label,font=font(14)))+32
        fill = C['action'] if primary else C['surface']
        foreground = C['on-action'] if primary else C['danger'] if danger else C['action']
        self.rect(x,y,width,32,fill,C['action'] if primary else C['border-control'])
        self.text(x+16,y+7,label,14,foreground)
        return width

    def chip(self,x,y,label,tone='info'):
        fill=C.get(tone+'-surface',C['selection'])
        ink=C.get(tone,C['action'])
        w=round(self.d.textlength(label,font=font(13)))+20
        self.rect(x,y,w,26,fill)
        self.text(x+10,y+5,label,13,ink)
        return w

    def panel(self,x,y,w,h,title=None):
        self.rect(x,y,w,h,C['surface'],C['border'])
        if title:self.text(x+24,y+20,title,16,bold=True)

    def shell(self,active,person,role,title,subtitle):
        self.rect(0,40,self.w,56,C['surface'],radius=0)
        self.line(0,96,self.w,96)
        self.rect(0,96,224,self.h-96,C['surface'],radius=0)
        self.line(224,96,224,self.h)
        self.text(24,58,'RAG_all',20,C['action'],True)
        self.text(248,60,'团队空间：示例研发团队 / 切换',14,bold=True)
        self.text(self.w-290,60,f'{person} · {role} / 本人',14,C['text-secondary'])
        items=[('问答',144),('对比',192),('知识库',240)]
        for label,y in items:
            if label==active:
                self.rect(12,y-8,200,40,C['selection'])
                self.rect(12,y-8,3,40,C['action'],radius=0)
            self.text(32,y,label,14,C['action'] if label==active else C['text-primary'],label==active)
        self.line(24,304,200,304)
        self.text(24,328,'当前空间会话',13,C['text-secondary'])
        self.text(24,368,'出差审批与材料',14)
        self.text(24,408,'M2 手册核验',14)
        self.line(24,self.h-160,200,self.h-160)
        self.text(24,self.h-136,'空间与邀请',14)
        self.text(24,self.h-96,'凭证与用量',14)
        self.text(24,self.h-56,'本人账户',14)
        self.text(248,120,title,20,bold=True)
        self.text(248,158,subtitle,13,C['text-secondary'])

    def save(self):
        self.svg.append('</svg>')
        (OUT/(self.name+'.svg')).write_text('\n'.join(self.svg),encoding='utf-8')
        self.im.save(OUT/(self.name+'.png'))
        return self.errors

errors={}

s=Sheet('M1-answer-source','M1 / 问答与来源 · IA-07 + IA-09')
s.shell('问答','小周','知识使用者','企业内部知识查询','本会话仅使用当前空间；查看历史仍按当前权限核验。')
s.panel(248,192,904,64)
s.text(272,214,'本次范围',14,bold=True)
s.chip(356,208,'制度知识库 · 1 个库')
s.text(1008,216,'调整范围',14,C['action'])
s.rect(368,280,784,64,C['selection'])
s.text(392,302,'出差需要哪些材料？审批负责人是谁？',16)
s.panel(248,368,904,408)
s.chip(272,392,'有依据的流程',tone='success')
s.text(272,442,'准备材料与适用条件',18,bold=True)
s.para(272,480,'适用于本次查询资料所述的普通出差流程。请准备行程安排与费用预算，并按制度要求提交。',848,16)
s.text(272,552,'依据 [1] 出差制度 v2 · 第 3 节',14,C['action'])
s.line(272,596,1128,596)
s.chip(272,616,'信息缺口',tone='info')
s.para(272,658,'资料未提供明确审批负责人，无法据此确定人选。请向当前制度维护者核实。',848,16)
s.text(272,734,'反馈：有误   ·   缺失依据   ·   引用问题',13,C['text-secondary'])
s.panel(248,800,904,208)
s.text(272,820,'继续提问',14,bold=True)
s.text(272,858,'补充你的问题；Enter 换行，使用按钮提交。',14,C['text-secondary'])
s.button(1008,952,'提交问答',True, width=120)
s.text(272,960,'当前范围保持不变；可在提交前调整。',13,C['text-secondary'])
s.panel(1176,192,400,816,'来源 [1]')
s.text(1200,246,'出差制度 · 资料版本标签 v2',16,bold=True)
s.text(1200,280,'结构位置：第 3 节 / 出差材料',13,C['text-secondary'])
s.button(1200,320,'提取内容',True,width=112)
s.button(1320,320,'原件入口',width=112)
s.line(1200,376,1552,376)
s.text(1200,400,'准确片段',14,bold=True)
s.rect(1200,438,352,112,C['source-highlight'])
s.para(1212,454,'出差申请应提交行程安排和费用预算。审批负责人由相关制度另行明确。',328,16)
s.para(1200,580,'此资料按章节定位，可下载原件核验。',352,14,C['text-secondary'])
s.button(1200,660,'下载原件',width=112)
s.text(1200,956,'返回时保留答案与引用位置。',13,C['text-secondary'])
errors[s.name]=s.save()

s=Sheet('M2-document-task','M2 / 生效版、候选与任务 · IA-04 + IA-06')
s.shell('知识库','阿宁','知识维护者','M2 产品手册','知识库 / 产品手册库 / 资料详情')
s.button(1432,120,'替换资料',width=144)
xs=[248,696,1144]
for x,title in zip(xs,['当前生效版本','候选版本','本次任务']):s.panel(x,208,432,500,title)
s.chip(272,272,'就绪 · 可用于查询','success')
s.text(272,322,'资料版本标签 v1',20,bold=True)
s.text(272,370,'当前查询继续使用此版本。',16)
s.text(272,412,'适用型号：M2',14)
s.text(272,448,'来源：已校核的 PDF 原件',14)
s.text(272,484,'适用产品版本：未标注',14,C['text-secondary'])
s.button(272,640,'查看生效版',width=136)
s.chip(720,272,'待核对 · 不参与查询','warning')
s.text(720,322,'资料版本标签 v2',20,bold=True)
s.para(720,370,'外部解析结果尚未确认；未替换当前生效版本。',384,16)
s.text(720,466,'失败 / 未完成范围：尚待确认',14,C['text-secondary'])
s.button(720,640,'查看候选详情',width=152)
s.chip(1168,272,'已到期','danger')
s.text(1168,322,'原任务保持终态',18,bold=True)
s.para(1168,370,'最后进展未获完整回包，不能从连接中断推断解析失败。',384,16)
s.text(1168,466,'截止：10-16 09:30（上海时间）',13,C['text-secondary'])
s.button(1168,528,'继续核对',width=128)
s.para(1168,578,'只查询原任务与费用，不下载、处理或发布。',384,14,C['text-secondary'])
s.panel(248,732,1328,248,'后续动作分开受理')
s.text(272,792,'继续本地处理',16,bold=True)
s.text(272,828,'尚未确认可复用产物；维护权限、资格、限制及资产校验通过后才可用。',14,C['text-secondary'])
s.rect(1360,788,192,32,C['surface-subtle'],C['border'])
s.text(1376,795,'继续本地处理',14,C['text-disabled'])
s.line(272,872,1552,872)
s.text(272,900,'重新提交解析',16,C['warning'],True)
s.text(272,936,'可能重复外部调用并产生费用；确认前不会重新提交。',14,C['text-secondary'])
s.button(1360,896,'重新提交解析…',width=192)
errors[s.name]=s.save()

s=Sheet('M3-comparison','M3 / 完整四态矩阵与冲突证据 · IA-08 + IA-09')
s.shell('对比','小陈','知识使用者','多文档对比与能力核验','2 份当前文档 × 3 条条件；对象与条件顺序保持不变。')
s.panel(248,192,904,96)
s.text(272,212,'产品 A · 文档 v2    /    产品 B · 文档 v1',14,bold=True)
s.text(272,252,'离线部署   ·   审计   ·   批量导入',14,C['text-secondary'])
s.text(248,316,'核验结果 · 6 / 6 格',16,bold=True)
tx,ty=248,356
col=[184,360,360]
for x,w,label in [(tx,col[0],'核验条件'),(tx+184,360,'产品 A · v2'),(tx+544,360,'产品 B · v1')]:
    s.rect(x,ty,w,64,C['surface-subtle'],C['border'],radius=0)
    s.text(x+16,ty+22,label,14,bold=True)
data=[('离线部署',('满足','success','明确提供离线部署方式。','[1]'),('明确不满足','danger','资料明确要求在线服务。','[2]')),
      ('审计',('证据不足','info','未找到审计能力的直接依据。','缺口：审计能力说明'),('资料冲突','warning','同一文档的两处表述互斥。','[3] [4]')),
      ('批量导入',('满足','success','资料明确支持批量导入。','[5]'),('证据不足','info','未提供批量导入的适用说明。','缺口：批量操作依据'))]
for r,(condition,a,b) in enumerate(data):
    y=ty+64+r*152
    s.rect(tx,y,184,152,C['surface'],C['border'],radius=0)
    s.text(tx+16,y+24,condition,16,bold=True)
    for ci,(state,tone,reason,cite) in enumerate([a,b]):
        x=tx+184+ci*360
        s.rect(x,y,360,152,C['surface'],C['border'],radius=0)
        s.chip(x+16,y+16,state,tone)
        s.para(x+16,y+60,reason,328,14)
        s.text(x+16,y+112,cite,13,C['action'] if cite.startswith('[') else C['text-secondary'])
s.rect(794,574,356,148,'#FFFFFF',C['focus'],radius=0,sw=2)
s.chip(808,588,'资料冲突','warning')
s.text(808,632,'同一文档的两处表述互斥。',14)
s.text(808,684,'[3] [4]',13,C['action'])
s.panel(1176,192,400,800,'当前格：产品 B / 审计')
s.text(1200,248,'固定版本：文档 v1',14,bold=True)
s.para(1200,284,'双方证据均来自当前对象的同一固定版本。产品间差异不属于单格冲突。',352,14,C['text-secondary'])
for y,title,text in [(392,'[3] 适用范围 / 第 2 节','审计能力仅限企业版。'),(584,'[4] 功能清单 / 第 5 节','基础版也提供审计记录。')]:
    s.rect(1200,y,352,160,C['warning-surface'])
    s.text(1216,y+20,title,14,C['warning'],True)
    s.para(1216,y+66,text,320,16)
    s.text(1216,y+120,'查看该处来源',14,C['action'])
s.para(1200,788,'结论：保留冲突，不能据此判为满足或不满足。',352,16,C['warning'],True)
s.text(248,924,'“证据不足”表示依据缺失，不等于产品不支持。',14,C['text-secondary'])
errors[s.name]=s.save()

s=Sheet('M4-source-check','M4 / 原件与提取内容对照 · IA-06 + IA-09')
s.shell('知识库','小赵','知识使用者','复杂产品手册问答 · 来源核验','M2 手册 · 文档 v3 · PDF 物理页 12 / 48')
s.panel(248,192,1328,64)
s.text(272,214,'当前引用：参数表 / 输入条件',14,bold=True)
s.text(968,214,'可靠页与区域定位',14,C['success'])
s.button(1408,208,'返回答案',width=144)
s.panel(248,280,652,716,'原件 · PDF 物理页 12')
s.panel(924,280,652,716,'提取内容 · 同一版本与位置')
s.rect(296,348,556,600,'#FFFFFF',C['border-control'])
s.text(328,376,'M2 安装与维护手册',20,bold=True)
s.text(328,416,'模拟资料',13,C['text-secondary'])
s.line(328,452,820,452)
s.text(328,480,'E17 / 连接状态核对',18,bold=True)
s.para(328,520,'适用型号：M2。按手册核对连接状态；先确认适用版本与环境条件。',492,14)
s.rect(320,608,508,144,C['source-highlight'])
s.rect(320,608,508,144,C['source-highlight'],C['focus'],sw=2)
for yy,a,b in [(624,'参数','数值与单位'),(666,'输入电压','24 V'),(708,'环境温度','0–40 ℃')]:
    s.text(340,yy,a,14,bold=yy==624)
    s.text(576,yy,b,14,bold=yy==624)
    if yy!=708:s.line(332,yy+30,816,yy+30,C['border-control'])
s.text(328,804,'图 3：接口位置（示意）',14)
s.rect(352,844,256,40,C['surface-subtle'],C['border-control'])
s.rect(664,844,96,40,C['surface-subtle'],C['border-control'])
s.line(608,864,664,864,C['text-secondary'],2)
s.text(380,854,'主机',14)
s.text(680,854,'接口',14)
s.text(560,916,'12',13,C['text-secondary'])
s.chip(948,348,'可回到实际页和区域','success')
s.text(948,402,'参数与限制',18,bold=True)
for y,k,v in [(454,'适用型号','M2'),(502,'输入电压','24 V'),(550,'环境温度','0–40 ℃')]:
    s.text(948,y,k,14,C['text-secondary'])
    s.text(1132,y,v,16,bold=True)
    s.line(948,y+32,1552,y+32)
s.para(948,626,'数值、单位和适用条件保持关联。核验原件后再判断，不把程序校核当作语义已正确。',604,16)
s.rect(948,734,604,128,C['info-surface'])
s.text(968,754,'定位回退规则',14,bold=True)
s.para(968,792,'只有可靠页时展示原页并标明“无区域高亮”；定位损坏时明确无法核验，不猜测位置。',564,14)
s.text(948,920,'非 PDF：显示实际结构位置与原件入口，不编物理页。',13,C['text-secondary'])
errors[s.name]=s.save()

s=Sheet('M5-critical-states','M5 / 等待、失联、失权与知情重交的组件状态')
for x,y,w,h,title in [(24,72,752,236,'A / 已受理等待'),(800,72,776,236,'B / 连接中断，结果待确认'),(24,332,752,236,'C / 当前资源不可用'),(800,332,776,636,'D / 重新提交解析的确认对话框')]:
    s.panel(x,y,w,h,title)
s.text(48,144,'正在处理本次问题。',18,bold=True)
s.text(48,190,'在原操作截止前等待完整结果；不显示未校验草稿。',14,C['text-secondary'])
s.chip(48,244,'当前会话暂不能再提交','info')
s.text(824,144,'尚未确认本次结果。',18,bold=True)
s.text(824,190,'查看原操作状态，不会重新生成或重复扣次。',14,C['text-secondary'])
s.button(824,244,'查看原操作',True,width=152)
s.text(48,408,'所选资源不可用。',18,bold=True)
s.text(48,452,'请重新选择范围，当前不可用内容不会继续显示。',14,C['text-secondary'])
s.button(48,508,'重新选择范围',width=168)
s.rect(824,408,728,520,C['canvas'])
s.panel(872,452,632,432,'重新提交解析？')
s.para(896,512,'当前外部解析结果仍待核对。重新提交可能产生重复调用与额外费用，原任务状态不会因此撤销。',584,16)
s.rect(896,612,584,80,C['warning-surface'])
s.para(912,630,'你也可以先“继续核对”，只读取原任务状态和费用。',552,14,C['warning'])
s.rect(896,724,18,18,C['surface'],C['border-control'])
s.text(926,724,'我已知悉可能重复调用与费用',14)
s.button(1064,808,'返回核对',width=136)
s.rect(1216,808,264,32,C['surface-subtle'],C['border'])
s.text(1232,815,'确认并重新提交解析',14,C['text-disabled'])
s.text(48,628,'状态表达规则',18,bold=True)
s.para(48,678,'加载、断网、业务失败、正常不足与无权是不同事实。提示写明影响和当前合法动作；不依赖短暂消息，不用自动新请求掩盖未知结果。',680,16)
s.text(48,800,'焦点样例',14,C['text-secondary'])
s.rect(44,840,180,40,C['surface'],C['focus'],sw=2)
s.button(48,844,'安全返回',width=172)
s.text(48,916,'失权提示不泄露未知目标标题、数量或存在性。',14,C['text-secondary'])
errors[s.name]=s.save()

thumbs=[]
for name in ['M1-answer-source','M2-document-task','M3-comparison','M4-source-check']:
    im=Image.open(OUT/(name+'.png'))
    im.thumbnail((800,520))
    thumbs.append(im)
contact=Image.new('RGB',(1632,1072),'#DCDFE6')
for im,(x,y) in zip(thumbs,[(8,8),(824,8),(8,544),(824,544)]):contact.paste(im,(x,y))
contact.save(OUT/'overview.png')
(OUT/'render-check.json').write_text(json.dumps({'artifacts':5,'svg':5,'png':6,'out_of_canvas_text':errors},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'artifacts':5,'svg':5,'png':6,'text_overflow_count':sum(len(v) for v in errors.values())},ensure_ascii=False))
