#!/usr/bin/env python3
"""Compact overview + mechanism details, based on the supplied paper figures."""
from pathlib import Path
from collections import Counter
import json, math, shutil, subprocess
import vector_engine as e
from vector_engine import rect,ellipse,poly,line,text,photo,vector,snowflake
from vector_engine import INK,BLUE,GREEN,CYAN,GOLD,GRAY

ROOT=Path(__file__).resolve().parent
e.ROOT=ROOT;e.W=2000;e.H=1160


def badge(name,letter,x,y,size=26):
    ellipse(name,x,y,size,size,INK,INK,0,z=28)
    text(name+'-text',letter,x,y,size,size,17,'#ffffff',bold=True,z=29)


def encoder(name,x,y,prompted=False):
    rect(name,x,y,160,85,GRAY,'#a7afb4',1.25,9)
    text(name+'-label','Image\nEncoder',x+10,y+6,140,68,23)
    snowflake(name+'-frozen',x+130,y+56,22)
    if prompted:
        for j in range(2):rect(name+f'-prompt-{j}',x+10+j*16,y+58,12,19,'#ffe6a8','#cc982e',1,0,z=27)


def marker(name,x,y,c,size=14,z=26):
    if c==0:ellipse(name,x-size/2,y-size/2,size,size,'#adcaf0',BLUE,1.1,z=z)
    else:rect(name,x-size/2,y-size/2,size,size,'#c9dfb2',GREEN,1.1,0,z=z)


def dot(name,x,y):ellipse(name,x-3,y-3,6,6,INK,INK,0,z=28)


def direction_glyph(name,x,y,w=210,h=85):
    """No text inside: parallelogram addition -> same-direction unit vector."""
    rect(name,x,y,w,h,'#fff7e3','#d1b674',1,9)
    o=(x+16,y+h-15);u=(x+50,y+h-21);v=(x+23,y+26);s=(u[0]+v[0]-o[0],u[1]+v[1]-o[1])
    line(name+'-u',[o,u],'#8d989f',1.4,z=26)
    line(name+'-v',[o,v],'#a3acb2',1.4,z=26)
    line(name+'-guide-u',[u,s],'#c5cbd0',.85,False,z=26)
    line(name+'-guide-v',[v,s],'#c5cbd0',.85,False,z=26)
    line(name+'-sum',[o,s],INK,2,z=27)
    line(name+'-step',[(x+83,y+h/2),(x+118,y+h/2)],INK,1.3,z=26)
    cx,cy,r=x+w-47,y+h/2,29
    ellipse(name+'-circle',cx-r,cy-r,2*r,2*r,None,'#84939c',1.2,z=25)
    dx,dy=s[0]-o[0],s[1]-o[1];norm=math.hypot(dx,dy);dx/=norm;dy/=norm
    line(name+'-unit',[(cx,cy),(cx+r*dx,cy+r*dy)],INK,1.7,z=26)
    ellipse(name+'-short',cx+12*dx-2.5,cy+12*dy-2.5,5,5,'#ffffff','#8d989f',1,z=28)
    dot(name+'-origin',cx,cy)


def compose():
    # Preparation is a small supporting inset, rather than half of the page.
    rect('prep-boundary',310,20,1000,280,None,'#c4ccd1',1.1,10,dash=True,z=0)
    text('prep-caption','Support preparation · before inference',326,28,510,27,21,bold=True,align='left')
    rect('support-input',30,35,230,230,'#ffffff','#76c4d2',1.2,12)
    text('support-title','Support set S',42,43,206,29,22,bold=True)
    text('support-budget','K real + K fake',42,77,206,25,19,italic=True)
    text('support-real','Real',45,107,170,21,16,BLUE,align='left')
    text('support-fake','Fake',45,178,170,21,16,GREEN,align='left')
    for i,x in enumerate([45,115,185],1):
        photo('support-real-'+str(i),'support-real-'+str(i)+'.png',x,131,50,42)
        photo('support-fake-'+str(i),'support-fake-'+str(i)+'.png',x,202,50,42)
    line('support-shared-stem',[(260,145),(280,145)],arrow=False)
    line('support-cache-branch',[(280,145),(280,107),(660,107)])
    line('support-fit-branch',[(280,145),(280,211),(335,211)])
    dot('support-fork',280,145)
    encoder('support-encoder',660,65)
    for s in e.SCENE:
        if s['name']=='support-encoder-label':
            s.update(y=68,h=55,fs=21)
    text('support-encoder-caption','CLIP · L12',666,129,120,17,14)
    line('support-encoded-features',[(820,107),(850,107)])
    rect('support-cache',850,65,380,125,'#f4f8fc','#b4c8db',1.1,9)
    text('support-cache-title','Cached features',864,72,227,25,20,bold=True,align='left')
    for c,x0 in [(0,878),(1,974)]:
        for j in range(3):vector(f'cache-class-{c}-{j}',x0+j*24,107,BLUE if c==0 else GREEN,16,39)
    vector('cache-global-real',1117,106,BLUE,18,40)
    vector('cache-global-fake',1170,106,GREEN,18,40)
    text('cache-global-real-symbol','μ₀',1104,85,45,23,20,italic=True)
    text('cache-global-fake-symbol','μ₁',1156,85,45,23,20,italic=True)
    text('cache-symbols','z_ci, μ_c',872,153,332,28,23,italic=True)
    # Compact supervised fit: support images, labels, fixed text; only P is fitted.
    rect('support-fit',335,155,400,111,'#f9faf7','#bfcbbb',1.05,9,z=0)
    text('support-fit-title','Support-only prompt fitting',347,159,365,26,20,bold=True,align='left')
    for j in range(2):rect(f'fit-token-{j}',351+j*17,202,12,23,'#ffe6a8','#cc982e',1,0)
    rect('fit-backbone',406,192,110,58,GRAY,'#a7afb4',1,7)
    text('fit-backbone-label','CLIP',417,199,85,31,21)
    snowflake('fit-frozen',492,229,17)
    line('fit-input',[(335,211),(339,211),(339,244),(406,244)])
    line('fit-token-to-backbone',[(382,216),(406,216)],GOLD,1.5)
    ellipse('fit-loss',588,192,54,54,'#fff5dc','#cdb16b',1.05)
    text('fit-loss-label','CE',594,205,42,25,20,bold=True)
    line('fit-image-to-loss',[(516,218),(588,218)])
    text('fit-labels','y\nt₀, t₁',659,193,64,45,16,italic=True)
    line('fit-labels-to-loss',[(654,218),(642,218)])
    # No black query edge enters this fit. Its output is the fitted state P*.
    rect('fitted-prompts',500,271,145,27,'#fff9ea','#d4ad59',1,6)
    text('fitted-prompts-label','P*',505,272,31,24,20,italic=True)
    for j in range(4):
        rect(f'fitted-prompt-{j}-a',542+j*24,277,7,15,'#ffe6a8','#cc982e',.8,0)
        rect(f'fitted-prompt-{j}-b',551+j*24,277,7,15,'#ffe6a8','#cc982e',.8,0)
    line('loss-to-prompts',[(615,246),(615,271)],GOLD,1.5,dash=True)
    # Its one crossing of the q feature line is visibly disconnected.
    line('fitted-state-upper',[(530,298),(530,381)],GOLD,1.5,False,True)
    line('fitted-state-lower',[(530,406),(530,480),(415,480),(415,535)],GOLD,1.5,True,True)
    line('cache-to-main-readout',[(1230,121),(1270,121),(1270,332),(1000,332),(1000,345)])

    # Small semantic legend occupies the upper-right corner.
    marker('legend-real',1377,74,0,14);text('legend-real-label','Real',1393,60,107,27,18,align='left')
    marker('legend-fake',1538,74,1,14);text('legend-fake-label','Fake',1554,60,107,27,18,align='left')
    snowflake('legend-freeze',1702,63,22);text('legend-freeze-label','Frozen',1735,60,188,27,18,align='left')
    for j in range(2):rect(f'legend-token-{j}',1369+j*17,109,12,23,'#ffe6a8','#cc982e',1,0)
    text('legend-token-label','Prompt',1410,105,167,27,18,align='left')
    line('legend-data',[(1620,121),(1660,121)],z=26)
    text('legend-data-label','Forward',1670,105,249,27,18,align='left')
    line('legend-dependency',[(1370,166),(1414,166)],GOLD,1.5,dash=True,z=26)
    text('legend-dependency-label','Fitted prompt dependency',1428,151,487,27,18,align='left')

    # Main overview: query splits BEFORE its two distinct encoding paths.
    text('main-caption','Query inference',31,297,250,29,22,bold=True,align='left')
    rect('query-input',30,345,210,245,'#ffffff','#76c4d2',1.2,12)
    text('query-title','Query set Q',43,354,184,28,22,bold=True)
    rect('query-stack-1',56,393,145,130,'#f4f6f7','#bdc8cf',.8,1)
    rect('query-stack-2',61,398,145,130,'#ffffff','#a8b6bf',.8,1)
    photo('query-image','query.png',66,403,140,125)
    text('query-symbol','x ∈ Q',60,548,146,29,24,italic=True)
    line('query-to-fork',[(240,495),(280,495)],arrow=False)
    line('query-to-unprompted',[(280,495),(280,392),(335,392)])
    line('query-to-prompted',[(280,495),(280,577),(335,577)])
    dot('query-forward-fork',280,495)
    encoder('query-l12-encoder',335,350)
    encoder('query-prompted-encoder',335,535,True)
    text('query-l12-caption','CLIP · L12',333,442,165,25,18)
    text('query-prompted-caption','CLIP · L24, prompted',317,628,200,25,18)
    badge('main-b-badge','B',322,522)
    text('prototype-method-title','Query-Conditioned Prototype Mixing',720,300,510,31,25,bold=True)
    line('l12-to-q',[(495,392),(600,392)])
    rect('q-feature',600,365,22,55,'#e1e7eb','#718390',1.1,0)
    text('q-feature-symbol','q',637,358,45,29,25,italic=True)
    line('q-to-main-readout',[(622,392),(850,392)])
    rect('main-prototype-readout',850,345,370,110,'#f3f8fd','#a5bfd9',1.2,11)
    badge('main-a-badge','A',839,332)
    poly('overview-q',[(885,386),(897,398),(885,410),(873,398)],'#a5b2bb',INK,1.1,z=26)
    line('overview-q-input',[(850,392),(873,398)],arrow=False,z=26)
    for c,yy in [(0,375),(1,422)]:
        for j,xx in enumerate([951,981]):
            marker(f'overview-support-{c}-{j}',xx,yy,c,13)
            line(f'overview-weight-{c}-{j}',[(897,398),(xx,yy)],'#7c8a94',1+j*.8,False,z=26)
    line('overview-weighted-to-direction',[(994,398),(1138,398)],z=26)
    vector('overview-dir-real',1145,376,BLUE,18,40,False)
    vector('overview-dir-fake',1180,376,GREEN,18,40,False)
    text('overview-direction-symbol','μ̃_c(q)',1020,418,180,27,23,italic=True)
    line('prototype-output',[(1220,398),(1275,398)])
    text('prototype-probability','pₚ',1260,373,95,42,29,italic=True)
    line('pp-to-fusion',[(1355,395),(1490,395),(1490,469)])
    text('pp-fusion-half','0.5',1410,363,71,26,21,italic=True)
    text('visual-method-title','Stage-wise Visual Prompting',650,500,640,31,25,bold=True)
    line('prompted-to-v',[(495,577),(600,577)])
    rect('visual-feature',600,549,22,55,'#e1e7eb','#718390',1.1,0)
    text('visual-feature-symbol','v(x)',650,542,94,29,25,italic=True)
    line('v-to-similarity',[(622,577),(1050,577)])
    rect('visual-similarity',1050,535,140,80,GRAY,'#a7afb4',1.2,9)
    text('visual-similarity-label','Cosine\nmargin',1058,548,124,52,23)
    rect('fixed-text',800,615,205,67,'#fafbf9','#bdc9b3',1,7)
    text('fixed-text-label','Fixed text anchors',807,619,191,23,17)
    text('fixed-text-symbols','t₀    t₁',823,646,153,28,24,italic=True)
    snowflake('fixed-text-freeze',974,649,19)
    line('fixed-text-to-similarity',[(1005,648),(1120,648),(1120,615)])
    line('visual-output',[(1190,575),(1275,575)])
    text('visual-probability','pᵥ',1260,551,95,42,29,italic=True)
    line('pv-to-fusion',[(1355,577),(1490,577),(1490,521)])
    text('pv-fusion-half','0.5',1410,583,71,26,21,italic=True)
    ellipse('fusion',1464,469,52,52,'#ffffff',INK,1.5)
    line('fusion-plus-h',[(1476,495),(1504,495)],INK,1.5,False,z=26)
    line('fusion-plus-v',[(1490,481),(1490,509)],INK,1.5,False,z=26)
    rect('prediction',1600,457,230,80,'#ffffff',INK,1.4,9)
    text('prediction-label','Real / Fake',1610,477,210,40,28)
    line('fusion-to-prediction',[(1516,495),(1600,495)])
    text('decision-threshold','p > 0.5: fake',1601,546,230,31,22,italic=True)
    text('fusion-equation','p = (pₚ + pᵥ)/2',1460,598,400,39,29,italic=True)

    # A: amplify the query-dependent mechanism, not the ordinary encoder.
    rect('detail-a-panel',30,730,1030,390,'#f5f9fc','#c5d5e1',1,12,z=0)
    badge('detail-a-badge','A',47,744)
    text('detail-a-title','Class-wise weighting and directional mixing',91,741,943,31,24,bold=True,align='left')
    poly('detail-common-q',[(95,886),(109,900),(95,914),(81,900)],'#a5b2bb',INK,1.2,z=26)
    text('detail-q-label','q',50,917,76,31,28,italic=True)
    for c,yy in [(0,845),(1,955)]:
        color=BLUE if c==0 else GREEN
        text(f'detail-class-{c}',f'c = {c}',135,yy-43,135,26,19,color)
        for j,xx in enumerate([202,246,290]):
            line(f'detail-weight-{c}-{j}',[(109,900),(xx,yy)],'#657580',1+[.5,2.3,.8][j],False,z=26)
            marker(f'detail-support-{c}-{j}',xx,yy,c,16)
        text(f'detail-alpha-{c}','α_ci(q)',298,yy-39,102,26,20,italic=True)
        line(f'detail-weighted-sum-{c}',[(337,yy+5),(397,yy+5)])
        rect(f'detail-local-{c}',400,yy-13,23,42,'#c6d1d8','#8394a0',1,0)
        marker(f'detail-local-marker-{c}',411.5,yy+8,c,9)
        text(f'detail-local-symbol-{c}',f'm{chr(0x2080+c)}(q)',365,yy+35,106,27,21,italic=True)
        y=yy-35
        direction_glyph(f'detail-mix-{c}',555,y,230,85)
        line(f'detail-local-to-mix-{c}',[(423,yy+8),(555,yy+8)])
        text(f'detail-local-half-{c}','0.5',476,yy-22,60,25,18,italic=True)
        vector(f'detail-global-{c}',510,yy-65,color,19,30,False)
        text(f'detail-global-symbol-{c}',f'μ{chr(0x2080+c)}',464,yy-53,45,25,21,italic=True)
        line(f'detail-global-to-mix-{c}',[(529,yy-50),(607,yy-50),(607,y)])
        text(f'detail-global-half-{c}','0.5',538,yy-66,58,23,18,italic=True)
        line(f'detail-mix-to-direction-{c}',[(785,yy+8),(847,yy+8)])
        vector(f'detail-direction-{c}',854,yy-13,color,23,42,False)
        marker(f'detail-direction-marker-{c}',865.5,yy+8,c,11)
        text(f'detail-direction-symbol-{c}',f'μ̃{chr(0x2080+c)}(q)',891,yy-12,137,43,26,italic=True)
    text('detail-prototype-score','sₚ = 15 qᵀ(μ̃₁(q) − μ̃₀(q)),    pₚ = σ(sₚ)',167,1018,835,29,22,italic=True)
    text('detail-query-softmax','α_ci(q) = softmax_i(15 qᵀz_ci)',169,1078,828,28,21,italic=True)

    # B: shared CLS/patch stream continues; the OLD pair exits before the NEW pair enters.
    rect('detail-b-panel',1090,730,880,390,'#f5f9f2','#d0ddc5',1,12,z=0)
    badge('detail-b-badge','B',1106,744)
    text('detail-b-title','Stage-wise prompt replacement',1150,741,786,31,24,bold=True,align='left')
    xs=[1160,1363,1566,1769]
    rect('persistent-image-tokens',1100,871,15,33,'#dce3e7','#8394a0',1,0)
    line('persistent-image-input',[(1115,887),(1130,887)])
    for j,(x,label) in enumerate(zip(xs,['1–6','7–12','13–18','19–24']),1):
        inject=x-30
        for k in range(2):rect(f'new-prompt-{j}-{k}',inject-13+k*19,811,13,25,'#ffe6a8','#cc982e',1.1,0)
        text(f'new-prompt-label-{j}',f'P{chr(0x2080+j)}',inject-22,781,58,24,21,italic=True)
        line(f'prompt-injection-{j}',[(inject,836),(inject,887)])
        rect(f'detail-stage-{j}',x,860,125,55,GRAY,'#a7afb4',1.1,7)
        text(f'detail-stage-label-{j}',label,x+6,872,103,28,23)
        snowflake(f'detail-stage-frozen-{j}',x+103,893,16)
        line(f'detail-stage-input-{j}',[(inject,887),(x,887)])
        if j<4:
            nxt=xs[j]-30;exitx=x+145
            line(f'detail-stage-forward-{j}',[(x+125,887),(nxt,887)])
            line(f'old-prompt-exit-{j}',[(exitx,887),(exitx,939)])
            for k in range(2):rect(f'old-prompt-{j}-{k}',exitx-13+k*19,946,13,25,'#f1f2ef','#c3c8be',1,0)
            text(f'old-prompt-label-{j}',f'P{chr(0x2080+j)}',exitx-22,975,58,23,18,'#9ca59c',italic=True)
        else:line('last-stage-readout',[(x+125,887),(1940,887)])
    text('persistent-token-caption','CLS + image tokens continue',1125,1018,492,28,19,align='left')
    text('prompt-size-caption','4 × 2 × 1024 = 8,192',1615,1018,328,28,21,italic=True)
    text('visual-score-equation','pᵥ = σ(15 v(x)ᵀ(t₁ − t₀))',1162,1080,760,36,25,italic=True)


def main():
    e.SCENE.clear();e.IDS.clear();compose()
    # The three encoder silhouettes share dimensions; the two query passes remain distinct.
    encs=[s for s in e.SCENE if s['name'] in ['support-encoder','query-l12-encoder','query-prompted-encoder']]
    assert len(encs)==3 and len({(s['w'],s['h']) for s in encs})==1
    assert not any('normalize' in s.get('value','').lower() for s in e.SCENE)
    e.flatten_math_text()
    e.write_svg()
    subprocess.run(['inkscape',str(ROOT/'framework-editable.svg'),'--export-type=png',
       '--export-width=3600','--export-filename='+str(ROOT/'framework-editable-preview.png')],check=True)
    e.write_vsdx()
    (ROOT/'framework-editable.scene.json').write_text(json.dumps(dict(width=e.W,height=e.H,
       units_per_inch=e.UNIT,objects=e.SCENE),ensure_ascii=False,indent=2)+'\n')
    from visio_compat import finalize
    compat=finalize(ROOT)
    for src,dst in [('framework-editable.svg','framework-v6.svg'),('framework-editable-preview.png','framework-v6.png')]:
        shutil.copyfile(ROOT/src,ROOT/dst)
    report=dict(revision='v6',client_date='2026-11-05',canvas=[e.W,e.H],objects=len(e.SCENE),
       kind_counts=dict(Counter(s['kind'] for s in e.SCENE)),compatibility=compat,
       design='compact query overview + support inset + A/B mechanism details',
       method_constraints=['one source support set','one query set','two distinct query forward paths',
         'support-only prompt fitting','per-class query weights','local vectors not renormalized before mixing',
         'two prompts replaced at four stages','fixed equal probability average'],
       microsoft_visio_tested=False)
    (ROOT/'v6-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['revision','canvas','objects','kind_counts']},ensure_ascii=False))


if __name__=='__main__':main()
