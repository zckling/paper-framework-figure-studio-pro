#!/usr/bin/env python3
"""Approved v5 revision: two method columns, preparation/inference rows.

The fusion operation is explained with vector addition and a unit-circle
diagram. All diagram content is authored as vector geometry or editable text;
only the seven original photograph crops are raster assets.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
from collections import Counter
from pathlib import Path

import vector_engine as e
from vector_engine import rect, text, line, ellipse, poly, snowflake, photo, vector
from vector_engine import INK, BLUE, GREEN, CYAN, GOLD, PALE_BLUE, PALE_GREEN, GRAY

ROOT = Path(__file__).resolve().parent
e.ROOT = ROOT
e.W, e.H = 2400, 1640


def node(name, x, y, w, h, label, fs=23, fill=GRAY, stroke='#a6afb2', frozen=False):
    rect(name,x,y,w,h,fill,stroke,1.35,10)
    text(name+'-label',label,x+7,y+8,w-14,h-16,fs,italic=True)
    if frozen:snowflake(name+'-frozen',x+w-29,y+h-30,23)


def dot(name,x,y,color=INK):
    ellipse(name,x-3,y-3,6,6,color,color,0,z=28)


def cache_down(name,x,y0,y1,extra=None):
    # A visible gap at the shared-query bus is an unconnected crossing.
    line(name+'-upper',[(x,y0),(x,587)],arrow=False)
    points=[(x,613),(x,y1)]
    if extra:points+=extra
    line(name+'-lower',points)


def fixed_text(name,x,y,w=300,h=94):
    rect(name,x,y,w,h,'#f6f7f7','#abb4b6',1.2,10)
    text(name+'-title','Fixed text anchors',x+8,y+5,w-16,31,23,italic=True)
    for suffix,dx,label,color,bg in [('real',20,'“real”',BLUE,'#f5fbff'),
                                    ('fake',w/2+3,'“fake”',GREEN,'#f9fff2')]:
        rect(name+'-'+suffix,x+dx,y+45,w/2-35,34,bg,color,.8,0)
        text(name+'-'+suffix+'-label',label,x+dx+2,y+45,w/2-39,34,23,color,italic=True)
    snowflake(name+'-snowflake',x+w-28,y+h-28,23)


def add_mix_glyph():
    # This whole pale-gold card deliberately contains zero text nodes.
    rect('mix-geometry-card',1010,1035,275,140,'#fff5d8','#b3a97d',1.4,12)
    o=(1030,1150);a=(1075,1142);b=(1038,1106);s=(1083,1098)
    line('glyph-add-u',[o,a],'#899399',1.8,z=26)
    line('glyph-add-v',[o,b],'#a7afb4',1.8,z=26)
    line('glyph-parallelogram-u',[a,s],'#bdc3c7',1.05,False,z=26)
    line('glyph-parallelogram-v',[b,s],'#bdc3c7',1.05,False,z=26)
    line('glyph-resultant',[o,s],INK,2.5,z=27)
    dot('glyph-origin',*o,INK)
    line('glyph-add-to-norm',[(1112,1105),(1162,1105)],INK,1.6,z=26)
    cx,cy,r=1220,1105,45
    ellipse('glyph-unit-circle',cx-r,cy-r,2*r,2*r,None,'#839198',1.5,z=25)
    norm=math.hypot(s[0]-o[0],s[1]-o[1])
    dx,dy=(s[0]-o[0])/norm,(s[1]-o[1])/norm
    line('glyph-normalized-direction',[(cx,cy),(cx+r*dx,cy+r*dy)],INK,2.2,z=26)
    # The short-vector endpoint and the extended arrow share one direction.
    ellipse('glyph-original-magnitude',cx+18*dx-3.2,cy+18*dy-3.2,
            6.4,6.4,'#ffffff','#8b969e',1.2,z=28)
    dot('glyph-circle-origin',cx,cy,INK)


def compose():
    # Two method columns, with the two phases occupying aligned rows.
    rect('method-left-panel',350,25,980,1335,'#ffffff','#d3e3f1',1.25,17,z=0)
    rect('method-right-panel',1370,25,995,1335,'#ffffff','#d8e5cf',1.25,17,z=0)
    rect('left-support-phase',360,180,960,315,PALE_BLUE,None,0,14,z=1)
    rect('right-support-phase',1380,180,975,315,PALE_GREEN,None,0,14,z=1)
    rect('left-query-phase',360,775,960,570,PALE_BLUE,None,0,14,z=1)
    rect('right-query-phase',1380,775,975,570,PALE_GREEN,None,0,14,z=1)
    text('method-title-left','Query-Conditioned Prototype Mixing',
         375,37,930,52,36,bold=True,italic=True)
    text('method-title-right','Stage-wise Visual Prompting',
         1400,37,930,52,36,bold=True,italic=True)
    text('phase-support-heading','SUPPORT\nPREPARATION',30,75,270,65,26,bold=True)
    text('phase-query-heading','QUERY\nINFERENCE',30,485,270,65,26,bold=True)

    # Exactly one shared support-set card. Both outgoing paths are data flow.
    rect('shared-support-set',30,160,270,300,'#ffffff',CYAN,1.65,15)
    text('support-set-title','Shared Support Set S',40,170,250,32,24,italic=True)
    text('support-set-budget','K real + K fake',45,208,240,29,23,italic=True)
    text('support-real-label','Real  c = 0',48,244,206,25,19,BLUE,italic=True,align='left')
    text('support-fake-label','Fake  c = 1',48,345,206,25,19,GREEN,italic=True,align='left')
    for i,x in enumerate([48,130,212],1):
        photo('support-real-'+str(i),'support-real-'+str(i)+'.png',x,277,62,59)
        photo('support-fake-'+str(i),'support-fake-'+str(i)+'.png',x,378,62,59)
    line('support-common-bus',[(300,310),(330,310),(330,140),(1510,140)],arrow=False)
    line('support-to-prototype',[(520,140),(520,215)])
    line('support-to-prompt-fitting',[(1510,140),(1510,215)])
    dot('support-fork',520,140)

    # Support preparation in the prototype column.
    node('support-encoder',435,215,170,100,'Image\nEncoder',25,frozen=True)
    text('support-l12-label','CLIP · block 12',421,321,198,31,22,italic=True)
    rect('cached-source-state',675,184,625,260,'#f8fbff','#b9ccda',1.05,12,z=2)
    text('cache-heading','Cached source state',850,365,430,29,22,italic=True)
    for category,x,color in [('real',710,BLUE),('fake',866,GREEN)]:
        for j in range(4):
            vector(f'bank-{category}-{j}',x+j*28,246,color,21,75)
        line('bank-bracket-'+category,[(x,238),(x,231),(x+106,231),(x+106,238)],
             '#71818b',1.1,False,z=26)
        text('bank-K-'+category,'K',x+30,212,48,24,20,italic=True)
    text('bank-ellipsis','···',825,264,39,32,27)
    text('bank-title','Support Feature Bank',701,330,320,29,23,italic=True)
    line('support-encoder-to-bank',[(605,265),(710,265)])
    line('bank-to-class-means',[(973,281),(1130,281)])
    text('feature-dimension','1024-D',1002,296,112,29,22,italic=True)
    vector('global-real',1140,252,BLUE,26,70)
    vector('global-fake',1220,252,GREEN,26,70)
    text('global-real-mu','μ₀',1123,226,61,29,27,italic=True)
    text('global-fake-mu','μ₁',1203,226,61,29,27,italic=True)
    text('global-means-caption','μ_c',1125,331,142,35,27,italic=True)
    text('cached-feature-symbol','z_ci',716,372,100,29,23,italic=True)
    text('cache-parameter-note','No task-learned parameters',777,397,498,28,19,italic=True)
    # Cached features / global directions remain separate, with no query join.
    cache_down('cached-features',760,444,875)
    line('cached-global-top',[(1240,370),(1280,370),(1280,587)],arrow=False)
    line('cached-global-bottom',[(1280,613),(1280,1005),(1080,1005),(1080,1035)])
    text('cached-features-port-label','z_ci',766,505,77,28,21,italic=True)
    text('cached-global-port-label','μ_c',1212,505,63,28,23,italic=True)

    # Support-only prompting fit. Labels and images both come from S.
    node('support-prompted-encoder',1415,215,190,100,'Prompted\nCLIP',25,frozen=True)
    rect('fit-prompt-token-a',1426,282,13,22,'#ffe5a5','#d89a22',1.15,0,z=27)
    rect('fit-prompt-token-b',1443,282,13,22,'#ffe5a5','#d89a22',1.15,0,z=27)
    node('support-ce-loss',1725,233,130,74,'ℒCE',30,fill='#fff7e2',stroke='#c6a260')
    line('support-features-to-loss',[(1605,265),(1725,265)])
    line('support-labels-to-loss',[(1510,171),(1790,171),(1790,233)])
    dot('support-labels-fork',1510,171)
    text('support-label-y','y',1665,174,50,34,27,italic=True)
    fixed_text('fit-fixed-text',1990,218,315,98)
    line('fit-text-to-loss',[(1990,270),(1855,270)])
    text('fit-text-feature-label','t₀, t₁',1863,232,118,30,23,italic=True)
    rect('fitted-prompt-state',1970,365,335,85,'#fff9eb','#d6b16a',1.2,10)
    for stage,x in enumerate([1990,2065,2140,2215],1):
        rect(f'fitted-stage-{stage}-a',x,390,15,31,'#ffe5a5','#d89a22',1.15,0)
        rect(f'fitted-stage-{stage}-b',x+20,390,15,31,'#ffe5a5','#d89a22',1.15,0)
    text('fitted-prompt-title','Fitted prompt parameters',1982,369,310,25,20,italic=True)
    text('fitted-prompt-parameter-count','4 × 2 × 1024 = 8,192',1982,423,310,25,21,italic=True)
    line('ce-to-learned-prompts',[(1790,307),(1790,407),(1970,407)],GOLD,1.9,dash=True)
    text('fit-only-prompt-note','Only prompts updated',1425,390,300,32,22,italic=True)
    # The one learned-parameter dependency rail is wholly in the right column.
    line('fitted-parameter-rail',[(2305,408),(2332,408),(2332,845),(1435,845)],
         GOLD,1.8,arrow=False,dash=True)

    # One shared query set, shown as a stack with one current image.
    rect('shared-query-set',30,555,270,203,'#ffffff',CYAN,1.65,15)
    text('query-set-title','Shared Query Set Q',40,564,250,32,24,italic=True)
    rect('query-stack-back',60,608,126,109,'#f6f8f9','#b4bec5',1,2)
    rect('query-stack-middle',68,615,126,109,'#ffffff','#9caab4',1,2)
    photo('query-current-image','query.png',77,623,126,108)
    text('one-query-caption','One query at a time',42,731,247,23,18,italic=True)
    line('query-shared-bus',[(300,655),(330,655),(330,600),(1510,600)],arrow=False)
    line('query-to-prototype-encoder',[(520,600),(520,815)])
    line('query-to-fitted-encoder',[(1510,600),(1510,780),(1400,780),(1400,902),(1420,902)])
    dot('query-left-fork',520,600)
    text('prototype-inference-title','Query-dependent readout',810,731,420,35,26,italic=True)
    text('prompt-inference-title','Frozen backbone · fitted prompts',1400,731,916,35,26,italic=True)

    # Query-conditioned prototype readout.
    node('query-encoder',435,815,170,100,'Image\nEncoder',25,frozen=True)
    text('query-l12-label','CLIP · block 12',421,921,198,31,22,italic=True)
    rect('class-wise-weighting',700,875,270,170,'#f8fbff','#acbecb',1.15,11,z=2)
    text('classwise-title','Per-class softmax',709,881,252,30,23,italic=True)
    text('weighting-beta','β = 15',756,913,158,27,22,italic=True)
    line('q-broadcast-and-similarity',[(605,865),(650,865),(650,1335),(1147,1335),(1147,1325)])
    line('q-to-weighting',[(650,1005),(700,1005)])
    dot('q-feature-fork',650,1005)
    text('q-feature-symbol','q',615,963,34,31,28,italic=True)
    for cls,origin,color in [(0,755,BLUE),(1,875,GREEN)]:
        for j,dx in enumerate([-31,0,31]):
            xx,yy=origin+dx,956+abs(dx)*.12
            line(f'class-{cls}-weight-{j}',[(xx,yy),(origin,1002)],
                 '#63737f',1+j*.65,False)
            if cls==0:
                ellipse(f'class-{cls}-sample-{j}',xx-7,yy-7,14,14,'#a9c8f4',color,1.1,z=26)
            else:
                rect(f'class-{cls}-sample-{j}',xx-7,yy-7,14,14,'#c4dfa7',color,1.1,0,z=26)
        poly(f'class-{cls}-q',[(origin,992),(origin+10,1002),(origin,1012),(origin-10,1002)],
             '#9ca8af',INK,1.1,z=26)
    line('q-left-class-readout',[(700,1005),(717,1005),(717,1002),(745,1002)],
         '#56656f',1.25,False,z=12)
    line('q-right-class-readout',[(717,1005),(717,1032),(855,1032),(855,1002),(865,1002)],
         '#56656f',1.25,False,z=12)
    dot('q-class-readout-fork',717,1005,'#56656f')
    line('weighted-readout-to-local',[(835,1045),(835,1080)])
    rect('local-unnormalized-vector',821,1080,28,60,'#9baebb','#596d7d',1.2,0)
    line('local-vector-divider-a',[(821,1100),(849,1100)],'#758b9c',1,False,z=26)
    line('local-vector-divider-b',[(821,1120),(849,1120)],'#758b9c',1,False,z=26)
    text('local-vector-symbol','m_c(q)',783,1145,135,32,25,italic=True)
    line('local-to-mix',[(849,1110),(1010,1110)])
    text('local-weight-half','0.5',919,1072,69,30,25,italic=True)
    text('global-weight-half','0.5',1084,1004,70,30,25,italic=True)
    text('mix-applies-per-class','c ∈ {0, 1}',1123,1002,161,30,22,italic=True)
    add_mix_glyph()
    # Two query-conditioned class directions, downstream of the same operation.
    text('query-conditioned-direction-symbol','μ̃_c(q)',1000,1190,132,44,28,italic=True)
    vector('direction-real',1150,1190,BLUE,23,38,False)
    vector('direction-fake',1210,1190,GREEN,23,38,False)
    ellipse('direction-real-marker',1156,1202,11,11,'#8db7f0',BLUE,1,z=26)
    rect('direction-fake-marker',1216,1202,11,11,'#9dc57c',GREEN,1,0,z=26)
    line('normalized-directions-output',[(1147,1175),(1147,1209),(1150,1209)])
    node('prototype-similarity',1060,1260,175,65,'Similarity margin',23)
    line('directions-to-margin',[(1195,1228),(1195,1260)])
    text('prototype-probability','pₚ = σ(sₚ)',1090,1375,225,50,29,italic=True)
    line('margin-to-pp',[(1235,1292),(1290,1292),(1290,1355),(1200,1355),(1200,1375)])
    text('prototype-score-equation','sₚ = 15 qᵀ(μ̃₁(q) − μ̃₀(q))',728,1260,325,54,23,italic=True)

    # Query inference with fitted stage prompts: no loss, no query update.
    text('prompt-replacement-caption','2 prompts / stage · replace at 1 / 7 / 13 / 19',
         1420,801,884,32,23,italic=True)
    stages=[(1460,'1–6'),(1675,'7–12'),(1890,'13–18'),(2105,'19–24')]
    for j,(x,label) in enumerate(stages,1):
        for suffix,dx in [('a',-40),('b',-20)]:
            rect(f'query-prompt-{j}-{suffix}',x+dx,881,16,42,'#ffe5a5','#d89a22',1.25,0)
        line(f'learned-prompt-drop-{j}',[(x-25,845),(x-25,877)],GOLD,1.65,dash=True)
        node(f'query-stage-{j}',x,865,150,75,label,27,frozen=True)
        line(f'prompt-to-stage-{j}',[(x-4,902),(x,902)],arrow=False)
        if j<4:line(f'visual-stage-link-{j}',[(x+150,902),(x+175,902)])
    rect('projected-visual-feature',2290,862,27,80,'#d9e1e7','#768b9a',1.2,0)
    line('last-stage-to-feature',[(2255,902),(2290,902)])
    text('projected-dimension','768-D',2205,956,118,30,23,italic=True)
    fixed_text('query-fixed-text',1640,1032,300,96)
    node('visual-similarity',2025,1060,170,70,'Similarity',25)
    line('projected-feature-to-similarity',[(2303,942),(2303,1095),(2195,1095)])
    line('fixed-text-to-similarity',[(1940,1095),(2025,1095)])
    text('fixed-text-features-query','t₀, t₁',1946,1050,73,32,23,italic=True)
    text('visual-probability','pᵥ = σ(15 vᵀ(t₁ − t₀))',1800,1210,520,60,32,italic=True)
    line('visual-similarity-to-pv',[(2110,1130),(2110,1210)])
    text('inference-frozen-prompt-count','8,192 fitted prompt parameters',1420,1245,360,55,22,italic=True)

    # Fixed probability average only after both query inference paths finish.
    ellipse('probability-fusion',1340,1445,60,60,'#ffffff',INK,1.65)
    line('fusion-plus-h',[(1353,1475),(1387,1475)],INK,1.65,False,z=26)
    line('fusion-plus-v',[(1370,1458),(1370,1492)],INK,1.65,False,z=26)
    line('pp-to-fusion',[(1200,1425),(1200,1475),(1340,1475)])
    line('pv-to-fusion',[(2060,1270),(2060,1475),(1400,1475)])
    text('fusion-left-weight','0.5',1240,1438,73,29,25,italic=True)
    text('fusion-right-weight','0.5',1450,1438,73,29,25,italic=True)
    node('prediction',1510,1518,230,59,'Real / Fake',29,fill='#ffffff',stroke=INK)
    line('fusion-to-prediction',[(1370,1505),(1370,1548),(1510,1548)])
    text('probability-average','p = (pₚ + pᵥ)/2',1050,1507,280,41,28,italic=True)
    text('prediction-threshold','p > 0.5: fake',1760,1530,260,37,26,italic=True)

    # Legend: category symbols, frozen/trainable encodings, and just two flow types.
    rect('legend-panel',75,1592,2250,36,'#ffffff','#afb8bf',1,9,z=1)
    ellipse('legend-real-symbol',100,1601,15,15,'#a9c8f4',BLUE,1)
    text('legend-real','Real',126,1596,86,27,19,italic=True)
    rect('legend-fake-symbol',240,1601,15,15,'#c4dfa7',GREEN,1,0)
    text('legend-fake','Fake',264,1596,86,27,19,italic=True)
    snowflake('legend-frozen-symbol',389,1598,22)
    text('legend-frozen','Frozen backbone / text',424,1596,300,27,19,italic=True)
    rect('legend-prompt-token-a',772,1598,13,22,'#ffe5a5','#d89a22',1,0)
    rect('legend-prompt-token-b',789,1598,13,22,'#ffe5a5','#d89a22',1,0)
    text('legend-prompts','Trainable prompt',816,1596,268,27,19,italic=True)
    line('legend-forward',[(1130,1610),(1180,1610)],z=26)
    text('legend-forward-caption','Image / feature flow',1200,1596,330,27,19,italic=True)
    line('legend-fitted-parameters',[(1580,1610),(1630,1610)],GOLD,1.7,dash=True,z=26)
    text('legend-fitted-parameters-caption','Fitted prompt dependency',1649,1596,598,27,19,italic=True)


def main():
    e.SCENE.clear();e.IDS.clear()
    compose()
    # Review constraints are checked against the actual editable object list.
    assert not any('mix, then' in s.get('value','').lower() or
                   'normalize' in s.get('value','').lower() for s in e.SCENE)
    inside=[s for s in e.SCENE if s['kind']=='text' and 1010<=s['x']<1285 and 1035<=s['y']<1175]
    assert not inside,inside
    for s in e.SCENE:
        if s['kind']=='line' and s.get('dash'):
            assert s['color']==GOLD, s['name']
    a=next(s for s in e.SCENE if s['name']=='support-encoder')
    b=next(s for s in e.SCENE if s['name']=='query-encoder')
    assert (a['w'],a['h'])==(b['w'],b['h'])
    e.write_svg()
    subprocess.run(['inkscape',str(ROOT/'framework-editable.svg'),
        '--export-type=png','--export-width=3600',
        '--export-filename='+str(ROOT/'framework-editable-preview.png')],check=True)
    e.write_vsdx()
    (ROOT/'framework-editable.scene.json').write_text(json.dumps(dict(
        width=e.W,height=e.H,units_per_inch=e.UNIT,objects=e.SCENE),
        ensure_ascii=False,indent=2)+'\n')
    from visio_compat import finalize
    compatibility=finalize(ROOT)
    for src,dst in [('framework-editable.svg','framework-v5.svg'),
                    ('framework-editable-preview.png','framework-v5.png')]:
        shutil.copyfile(ROOT/src,ROOT/dst)
    counts=Counter(s['kind'] for s in e.SCENE)
    report=dict(revision='v5',client_date='2026-11-04',canvas=[e.W,e.H],
        objects=len(e.SCENE),kind_counts=dict(counts),compatibility=compatibility,
        changes=['two method columns','shared support preparation row',
          'one shared query set between phases','query inference row',
          'vector addition plus unit-circle glyph without text',
          'solid support and query input paths','gold dashes only for fitted prompt dependencies'],
        semantic_edges=[['support-set','support-encoder','image'],
          ['support-set','support-prompted-encoder','image'],
          ['support-set','support-ce-loss','labels'],
          ['shared-query-set','query-encoder','image'],
          ['shared-query-set','query-stage-1','image'],
          ['cached-source-state','class-wise-weighting','cached features'],
          ['cached-source-state','mix-geometry-card','global class means'],
          ['fitted-prompt-state','query-prompt-1','fitted parameters'],
          ['fitted-prompt-state','query-prompt-2','fitted parameters'],
          ['fitted-prompt-state','query-prompt-3','fitted parameters'],
          ['fitted-prompt-state','query-prompt-4','fitted parameters'],
          ['prototype-probability','probability-fusion','probability'],
          ['visual-probability','probability-fusion','probability']],
        microsoft_visio_tested=False,
        notes='Native objects are independently editable. Previous VSDX had a user-reported compatibility issue; use VDX fallback and verify in desktop Visio.')
    (ROOT/'v5-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['revision','canvas','objects','kind_counts']},ensure_ascii=False))


if __name__=='__main__':main()
