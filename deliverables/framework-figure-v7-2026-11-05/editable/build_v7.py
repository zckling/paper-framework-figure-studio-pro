#!/usr/bin/env python3
"""Manually authored editable companion to the skill-generated v7 candidates."""
from pathlib import Path
from collections import Counter
import json,shutil,subprocess
import vector_engine as e
from vector_engine import rect,ellipse,line,text,photo,vector,snowflake
from vector_engine import INK,BLUE,GREEN,CYAN,GOLD,GRAY
ROOT=Path(__file__).resolve().parent
e.ROOT=ROOT;e.W=2000;e.H=1450
PALE='#f7f8f9';EDGE='#c7ced3';MUTE='#60717d';ORANGE='#e7a43b'


def box(name,x,y,w,h,fill=GRAY):rect(name,x,y,w,h,fill,'#a7afb4',1.2,9)
def dot(name,x,y):ellipse(name,x-3,y-3,6,6,INK,INK,0,z=28)
def mark(name,x,y,c,size=18):
    if c==0:ellipse(name,x-size/2,y-size/2,size,size,'#b4cef1',BLUE,1.15,z=26)
    else:rect(name,x-size/2,y-size/2,size,size,'#c6dfae',GREEN,1.15,0,z=26)
def prompt(name,x,y,w=12,h=24,star=False):
    for j in range(2):rect(name+f'-{j}',x+j*(w+5),y,w,h,'#ffe3a2',ORANGE,1.2,0,z=26)
def encoder(name,x,y,blocks,prompted=False):
    box(name,x,y,260,90)
    text(name+'-title','CLIP ViT-L/14',x+10,y+8,240,32,26)
    text(name+'-blocks','blocks '+blocks,x+9,y+43,242,32,26)
    snowflake(name+'-freeze',x+227,y+63,17)
def cross(name,x,y,size=16,color=INK):
    line(name+'-a',[(x-size/2,y-size/2),(x+size/2,y+size/2)],color,2.2,False,z=28)
    line(name+'-b',[(x-size/2,y+size/2),(x+size/2,y-size/2)],color,2.2,False,z=28)
def seq(name,x,y,mode='old',size=12):
    # CLS, two prompt states/parameters, three image tokens.
    for i in range(6):
        is_p=i in [1,2]
        fill='#ffe3a2' if is_p else '#dbe2e6'
        stroke=ORANGE if is_p else '#7e909b'
        rect(name+f'-{i}',x+i*(size+4),y,size,25,fill,stroke,1.05,0,z=26)
        if mode=='drop' and is_p:cross(name+f'-removed-{i}',x+i*(size+4)+size/2,y+12.5,13)


def compose():
    # (a) Overview. Support preparation remains visually separate from query forwards.
    rect('overview-boundary',25,20,1950,815,'#ffffff',EDGE,1.1,12,z=0)
    text('overview-caption','(a) Overview',45,30,500,35,28,bold=True,align='left')
    rect('adaptation-boundary',40,76,1920,385,PALE,EDGE,1.05,10,z=0)
    text('adaptation-caption','Support-set adaptation · once per support set',285,83,1420,32,26,bold=True,align='left')
    box('support-set',55,120,185,315,'#ffffff')
    text('support-title','Support set S',63,130,169,32,26,bold=True)
    text('support-budget','2K labeled\nimages',62,165,171,60,26,bold=True)
    text('support-count','K real + K fake',63,228,169,30,25,italic=True)
    text('support-real-label','Real',66,263,150,30,25,BLUE,align='left')
    text('support-fake-label','Fake',66,349,150,30,25,GREEN,align='left')
    for c,name,yy in [(0,'real',297),(1,'fake',383)]:
        for j,xx in enumerate([70,128],1):photo(f'support-{name}-{j}',f'support-{name}-{j}.png',xx,yy,47,42)
        text(f'support-{name}-ellipsis','…',183,yy+8,35,27,27)
    line('support-to-fork',[(240,245),(270,245)],arrow=False);dot('support-fork',270,245)
    line('support-to-fit',[(270,245),(270,184),(550,184)])
    line('support-to-cache',[(270,245),(270,390),(550,390)])
    # A true prompt-only optimization loop; fixed text enters the logits, labels enter CE.
    rect('trainable-prompts',360,128,180,49,'#fff6e4','#d7b46c',1.15,7)
    prompt('trainable-pair',372,140)
    text('trainable-prompt-symbol','Learn P',407,134,124,32,26,italic=True)
    line('prompts-to-fit',[(540,151),(550,151)],GOLD,1.8)
    encoder('fit-encoder',550,121,'1–24',True)
    line('fit-to-logits',[(810,166),(1035,166)])
    text('fit-feature-label','image feature',840,131,167,26,19)
    box('native-logits',1035,121,240,90)
    text('native-logits-title','Cosine logits',1045,132,220,32,26)
    text('native-logits-scale','S = exp(logit_scale)',1044,168,222,25,20,italic=True)
    box('fixed-anchors-train',1035,226,240,48,'#ffffff')
    text('fixed-anchors-train-label','Fixed text anchors  t₀, t₁',1041,235,205,28,18)
    snowflake('text-frozen',1249,251,15)
    line('anchors-to-training-logits',[(1155,226),(1155,211)])
    line('logits-to-ce',[(1275,166),(1418,166)])
    text('native-logits-symbol','logits',1300,130,93,31,25)
    ellipse('ce',1418,132,67,67,'#ffffff',INK,1.3)
    text('ce-label','CE',1424,148,55,34,25,bold=True)
    text('support-label-y','y',1510,150,36,30,25,italic=True)
    line('labels-to-ce',[(1505,166),(1485,166)])
    line('ce-backprop',[(1452,199),(1452,245),(1310,245),(1310,190),(1275,190)],GOLD,1.8,True,True)
    line('logits-gradient-through-encoder',[(1035,190),(810,190)],GOLD,1.8,True,True)
    line('encoder-gradient-to-prompts',[(550,136),(535,136),(535,115),(420,115),(420,128)],GOLD,1.8,True,True)
    text('update-caption','Update\nprompts only',1300,261,280,63,26,ORANGE,bold=True)
    text('backprop-caption','Backprop through frozen encoder',550,244,450,32,25,ORANGE,bold=True)
    # State, not CE-produced feature. This port is repeated near the query consumer.
    rect('trained-state',1655,215,260,89,'#fff7e8','#d2ad64',1.15,8)
    text('trained-state-title','After optimization',1665,180,240,32,26)
    prompt('trained-state-pair',1673,260,10,22)
    text('trained-state-symbol','Fitted prompts\nP*',1711,228,192,70,26,bold=True)
    text('trained-state-budget','8,192 trainable parameters',1625,319,330,32,26)
    # Class cache is immediately above its query consumer.
    encoder('cache-encoder',550,345,'1–12')
    line('cache-encoder-to-cache',[(810,390),(1045,390)])
    text('cached-feature-label','normalized features',825,353,205,28,20)
    box('support-cache',1045,345,370,90,'#ffffff')
    text('support-cache-title','Support cache',1055,350,350,32,26,bold=True)
    for c,xx in [(0,1075),(1,1185)]:
        for j in range(2):mark(f'cached-point-{c}-{j}',xx+j*31,405,c,21)
        text(f'cache-class-ellipsis-{c}','…',xx+58,389,35,28,23)
    text('cache-variables','z_ci, μ_c',1291,380,110,40,23,italic=True)
    line('cache-load',[(1230,435),(1230,520)],INK,1.6)
    text('cache-load-caption','cache',1240,474,112,25,19,MUTE,align='left')
    # Shared x forks BEFORE the two independent encoder passes.
    text('query-section','Query inference',53,473,390,33,26,bold=True,align='left')
    box('query-set',55,542,185,240,'#ffffff')
    text('query-title','Query set Q',63,552,169,32,26,bold=True)
    photo('query-photo','query.png',81,593,132,118)
    text('query-variable','x ∈ Q',78,738,140,31,26,italic=True)
    line('query-to-fork',[(240,660),(285,660)],arrow=False);dot('query-fork',285,660)
    line('query-to-prototype',[(285,660),(285,565),(550,565)])
    line('query-to-prompted',[(285,660),(285,725),(550,725)])
    encoder('query-prototype-encoder',550,520,'1–12')
    encoder('query-prompt-encoder',550,680,'1–24',True)
    text('prompt-detail-reference','Stage-wise visual prompting',550,623,485,33,26,bold=True)
    text('prompt-subdetail-reference','detail in (c)',550,658,485,20,16,MUTE)
    line('prototype-feature-forward',[(810,565),(858,565)])
    rect('query-feature',858,540,21,50,'#dfe6ea','#7e919e',1.1,0)
    text('query-feature-symbol','q ∈ ℝ¹⁰²⁴',887,536,151,35,26,italic=True)
    line('prototype-feature-to-method',[(879,565),(1045,565)])
    rect('prototype-method',1045,520,370,90,PALE,'#9baebc',1.3,10)
    text('prototype-method-title','Query-conditioned\nprototype mixing',1057,522,346,64,26,bold=True)
    text('prototype-detail-ref','detail in (b)',1057,589,346,20,16,MUTE)
    line('prototype-score-output',[(1415,565),(1457,565)])
    text('prototype-probability','pₚ(q)',1464,539,116,39,27,italic=True)
    # Local fitted-state port, deliberately no line across the other query branch.
    rect('loaded-prompt-state',399,670,121,40,'#fff7e8','#d2ad64',1,6)
    prompt('loaded-prompt-pair',409,680,8,18)
    text('loaded-prompt-symbol','Load P*',438,674,76,30,20,italic=True)
    line('local-state-to-encoder',[(520,690),(535,690),(535,696),(550,696)],GOLD,1.6,True,False)
    line('prompted-feature-forward',[(810,725),(858,725)])
    rect('prompted-feature',858,700,21,50,'#dfe6ea','#7e919e',1.1,0)
    text('prompted-feature-symbol','v(x) ∈ ℝ⁷⁶⁸',887,696,151,35,26,italic=True)
    line('prompted-feature-to-score',[(879,725),(1045,725)])
    rect('cosine-difference',1045,680,370,105,PALE,'#9baebc',1.3,10)
    text('cosine-difference-title','Cosine similarity\ndifference',1057,683,346,61,26,bold=True)
    text('visual-probability-formula','×15 → sigmoid',1059,748,342,32,26,italic=True)
    box('fixed-anchors-query',1080,793,300,31,'#ffffff')
    text('fixed-query-anchor-label','Fixed text anchors  t₀, t₁',1087,797,286,23,18)
    line('query-anchors-to-score',[(1230,793),(1230,785)])
    line('visual-probability-output',[(1415,725),(1457,725)])
    text('visual-probability','pᵥ(x)',1464,698,116,39,27,italic=True)
    line('prototype-to-average',[(1580,565),(1615,565),(1615,630),(1650,630)])
    line('visual-to-average',[(1580,725),(1615,725),(1615,687),(1650,687)])
    box('probability-average',1650,606,285,105,'#ffffff')
    text('probability-average-title','Probability average',1660,616,265,32,26,bold=True)
    text('probability-average-formula','p(x) = ½[pₚ(q) + pᵥ(x)]',1660,657,265,34,26,italic=True)
    text('decision-rule','p(x) > 0.5: Fake',1660,739,265,29,24,italic=True)

    # (b) Prototype computation, one class-specific row per class.
    rect('prototype-detail-panel',25,850,1015,480,PALE,EDGE,1.15,11,z=0)
    text('prototype-detail-title','(b) Query-conditioned prototype mixing',45,864,975,35,27,bold=True,align='left')
    text('softmax-header','Class-wise softmax',127,925,256,33,26,bold=True)
    text('aggregation-header','Weighted sum',393,925,267,33,26,bold=True)
    text('mix-header','Mix → L₂ norm',679,925,334,33,26,bold=True)
    rect('detail-q',56,1048,21,57,'#dfe6ea','#7e919e',1.1,0)
    text('detail-q-symbol','q',42,1109,50,29,25,italic=True)
    for c,yy in [(0,1013),(1,1144)]:
        color=BLUE if c==0 else GREEN
        text(f'detail-class-label-{c}',f'c = {c}',138,yy-44,128,25,20,color)
        for j,xx in enumerate([173,223,273]):
            line(f'query-class-weight-{c}-{j}',[(77,1076),(xx,yy)],'#647a87',[1.1,3.2,1.7][j],False,z=26)
            mark(f'detail-support-{c}-{j}',xx,yy,c,20)
            line(f'support-to-aggregate-{c}-{j}',[(xx+11,yy),(365,yy+8)],'#71838e',1.1,False,z=26)
        ellipse(f'aggregate-sum-{c}',366,yy-11,38,38,'#ffffff',INK,1.2)
        text(f'aggregate-sum-label-{c}','Σ',370,yy-9,30,34,26)
        line(f'aggregate-to-m-{c}',[(404,yy+8),(456,yy+8)])
        ht=31 if c==0 else 48
        vector(f'local-vector-{c}',461,yy+8-ht/2,color,22,ht,False)
        text(f'local-vector-label-{c}',f'm{chr(0x2080+c)}(q)',425,yy+40,106,29,23,italic=True)
        line(f'local-to-mix-{c}',[(483,yy+8),(666,yy+8)])
        text(f'local-mix-half-{c}','0.5',571,yy-27,60,30,25,italic=True)
        vector(f'global-vector-{c}',650,yy-65,color,22,39,False)
        text(f'global-vector-label-{c}',f'μ{chr(0x2080+c)}',597,yy-63,49,27,24,italic=True)
        line(f'global-to-mix-{c}',[(672,yy-45),(685,yy-45),(685,yy-11)])
        text(f'global-mix-half-{c}','0.5',696,yy-51,55,30,25,italic=True)
        ellipse(f'mix-plus-{c}',666,yy-11,38,38,'#ffffff',INK,1.2)
        text(f'mix-plus-label-{c}','+',670,yy-9,30,32,26)
        line(f'mix-to-normalize-{c}',[(704,yy+8),(759,yy+8)])
        box(f'normalize-{c}',759,yy-18,112,52,'#ffffff')
        text(f'normalize-label-{c}','L₂ norm',764,yy-10,102,36,26)
        line(f'normalize-output-{c}',[(871,yy+8),(917,yy+8)])
        vector(f'mixed-direction-{c}',921,yy-16,color,21,48,False)
        text(f'mixed-direction-label-{c}',f'μ̃{chr(0x2080+c)}(q)',884,yy+43,129,30,23,italic=True)
    text('classwise-weight-formula','α_ci(q) = softmax_i(15 qᵀz_ci)',82,1201,465,30,21,italic=True)
    text('classwise-aggregate-formula','m_c(q) = Σ_i α_ci(q) z_ci',536,1201,476,30,21,italic=True)
    text('unnormalized-local-note','m_c(q) is not normalized before mixing.',82,1238,930,26,21,MUTE)
    text('prototype-score-formula','pₚ(q) = σ(15 qᵀ(μ̃₁(q) − μ̃₀(q)))',91,1275,911,29,23,italic=True)

    # (c) Prompt replacement: simple group overview, token-level boundary below it.
    rect('prompt-detail-panel',1065,850,910,480,PALE,EDGE,1.15,11,z=0)
    text('prompt-detail-title','(c) Stage-wise prompt replacement',1085,864,870,35,27,bold=True,align='left')
    text('frozen-stage-group','Frozen backbone',1120,909,660,27,20,MUTE)
    snowflake('stages-frozen',1789,913,20)
    xs=[1100,1295,1490,1685]
    for j,(xx,label) in enumerate(zip(xs,['1–6','7–12','13–18','19–24']),1):
        prompt(f'stage-prompt-{j}',xx+20,949,11,22)
        text(f'stage-prompt-label-{j}',f'P{chr(0x2080+j)}*',xx+53,942,66,29,23,italic=True)
        line(f'stage-prompt-input-{j}',[(xx+34,971),(xx+34,991),(xx+50,991),(xx+50,1010)],GOLD,1.6)
        box(f'stage-{j}',xx,1010,126,63)
        text(f'stage-label-{j}',label,xx+8,1023,110,33,26)
        if j==1:
            rect('cls-image-input',1080,1029,13,26,'#dbe2e6','#7e909b',1,0)
            line('cls-image-to-first-stage',[(1093,1042),(1100,1042)])
        if j<4:
            end=xx+126;exitx=xx+151;nxt=xs[j]
            line(f'stage-forward-{j}',[(end,1042),(nxt,1042)])
            line(f'prompt-state-discard-{j}',[(exitx,1042),(exitx,1085)],'#7e909b',1.4)
            prompt(f'updated-prompt-states-{j}',exitx-13,1091,9,20)
            cross(f'discard-cross-{j}',exitx+1,1101,28)
        else:
            line('last-stage-to-readout',[(xx+126,1042),(1834,1042)])
    box('cls-readout-projection',1834,978,126,127,'#ffffff')
    text('cls-readout-label','CLS\nreadout\nproject\nL₂ norm',1839,984,116,116,25)
    text('readout-variable','v(x)',1848,1111,98,32,26,italic=True)
    text('continue-path-label','CLS + image tokens continue',1097,1118,740,31,26,MUTE)
    text('boundary-heading','Keep CLS/image → discard prompt states → insert P*',1090,1159,858,31,26,bold=True)
    seq('boundary-stage-output',1112,1230,'old',12)
    text('boundary-stage-output-label','CLS · prompt states · image',1096,1193,345,31,25)
    line('boundary-to-removal',[(1215,1243),(1355,1243)])
    seq('boundary-drop-old',1364,1230,'drop',12)
    text('discard-action','discard',1303,1260,209,28,23,MUTE)
    line('boundary-to-insertion',[(1469,1243),(1619,1243)])
    seq('boundary-new-prompts',1628,1230,'new',12)
    text('new-pair-label','Pₛ₊₁*',1605,1193,161,31,25,italic=True)
    line('new-pair-insert',[(1665,1224),(1665,1230)],GOLD,1.5)
    line('boundary-next-stage',[(1733,1243),(1855,1243)])
    text('next-stage-label','Next stage',1850,1227,114,34,23)
    text('prompt-parameters','8,192 trainable parameters',1154,1290,741,32,26,italic=True)
    # Compact legend and caption preserve detail without enlarging modules.
    mark('legend-real',301,1380,0,20);text('legend-real-label','Real',319,1365,106,31,26,align='left')
    mark('legend-fake',480,1380,1,20);text('legend-fake-label','Fake',498,1365,110,31,26,align='left')
    prompt('legend-prompts',667,1369,11,22);text('legend-prompt-label','Trainable / fitted prompts',707,1365,387,31,26,align='left')
    snowflake('legend-frozen',1144,1367,26);text('legend-frozen-label','Frozen parameters',1181,1365,284,31,26,align='left')


def main():
    e.SCENE.clear();e.IDS.clear();compose();e.flatten_math_text()
    e.write_svg()
    subprocess.run(['inkscape',str(ROOT/'framework-editable.svg'),'--export-width=3600','--export-filename='+str(ROOT/'framework-editable-preview.png')],check=True)
    e.write_vsdx()
    (ROOT/'framework-editable.scene.json').write_text(json.dumps({'width':e.W,'height':e.H,'units_per_inch':e.UNIT,'objects':e.SCENE},ensure_ascii=False,indent=2)+'\n')
    from visio_compat import finalize
    compatibility=finalize(ROOT)
    for src,dst in [('framework-editable.svg','framework-v7.svg'),('framework-editable-preview.png','framework-v7.png')]:shutil.copyfile(ROOT/src,ROOT/dst)
    subprocess.run(['inkscape',str(ROOT/'framework-v7.svg'),'--export-filename='+str(ROOT/'framework-v7.pdf')],check=True)
    report={'revision':'v7-editable-companion','purpose':'Manually authored editable companion, not an imagegen raster','canvas':[e.W,e.H],'objects':len(e.SCENE),'kind_counts':dict(Counter(s['kind'] for s in e.SCENE)),'compatibility':compatibility,'microsoft_visio_tested':False}
    (ROOT/'v7-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
