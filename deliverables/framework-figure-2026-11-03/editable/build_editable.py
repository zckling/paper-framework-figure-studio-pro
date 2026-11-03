#!/usr/bin/env python3
"""Rebuild the reviewed method figure as real SVG and native Visio shapes.

The PNG is used only for the seven individual photograph assets.  Every other
visible object is authored as geometry or text. No raster tracing is used.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import ImageFont

ROOT = Path(__file__).resolve().parent
W, H, UNIT = 2048, 910, 120.0
INK = '#20292f'
BLUE, GREEN, CYAN, GOLD = '#2873dc', '#5b9636', '#34c2dc', '#b7802c'
PALE_BLUE, PALE_GREEN = '#f0f7fd', '#f3f8f2'
GRAY = '#ebeded'
SCENE = []
IDS = set()
FONT_ROOT = Path('/usr/share/fonts/truetype/liberation')
FONTS = {}


def add(kind, name, **kw):
    if name in IDS:
        raise ValueError('Duplicate object: ' + name)
    IDS.add(name)
    obj = dict(kind=kind, name=name, z=kw.pop('z', 20), **kw)
    SCENE.append(obj)
    return name


def rect(name, x, y, w, h, fill=GRAY, stroke='#a6afb2', lw=1.3, r=9, **kw):
    return add('rect', name, x=x, y=y, w=w, h=h, fill=fill, stroke=stroke,
               lw=lw, r=r, **kw)


def ellipse(name, x, y, w, h, fill, stroke, lw=1.2, **kw):
    return add('ellipse', name, x=x, y=y, w=w, h=h, fill=fill,
               stroke=stroke, lw=lw, **kw)


def font_size(text, fs, width, height, bold, italic):
    variant = ('BoldItalic' if bold and italic else 'Bold' if bold else
               'Italic' if italic else 'Regular')
    font_path = FONT_ROOT / ('LiberationSans-' + variant + '.ttf')
    lines = text.split('\n')
    while fs >= 9:
        key = (variant, round(fs * 4))
        if key not in FONTS:
            FONTS[key] = ImageFont.truetype(str(font_path), round(fs * 4))
        font = FONTS[key]
        widest = max(font.getlength(line) / 4 for line in lines)
        if widest <= width - 5 and len(lines) * fs * 1.15 <= height:
            return fs
        fs -= 0.25
    raise ValueError('Text cannot fit: ' + text)


def text(name, value, x, y, w, h=30, fs=20, color=INK, bold=False,
         italic=False, align='center', **kw):
    fs = font_size(value, fs, w, h, bold, italic)
    return add('text', name, x=x, y=y, w=w, h=h, value=value, fs=fs,
               color=color, bold=bold, italic=italic, align=align,
               z=kw.pop('z', 30), **kw)


def line(name, points, color=INK, lw=1.7, arrow=True, dash=False,
         start=None, end=None, **kw):
    return add('line', name, points=points, color=color, lw=lw,
               arrow=arrow, dash=dash, start=start, end=end,
               z=kw.pop('z', 10), **kw)


def poly(name, points, fill, stroke=INK, lw=1.2, **kw):
    return add('poly', name, points=points, fill=fill, stroke=stroke,
               lw=lw, **kw)


def snowflake(name, x, y, size=24):
    segments = []
    cx, cy, r = x + size/2, y + size/2, size/2
    for i in range(6):
        a = math.pi/3*i
        v = (math.cos(a), math.sin(a))
        tip = (cx+r*v[0], cy+r*v[1])
        segments.append([(cx, cy), tip])
        fork = (cx+r*.62*v[0], cy+r*.62*v[1])
        for d in [-1, 1]:
            wing = a+d*math.pi/3
            segments.append([fork, (fork[0]+r*.31*math.cos(wing),
                                    fork[1]+r*.31*math.sin(wing))])
    return add('snowflake', name, x=x, y=y, w=size, h=size,
               segments=segments, stroke=CYAN, lw=1.55, z=26)


def photo(name, asset, x, y, w, h):
    rect(name+'-frame', x-2, y-2, w+4, h+4, '#ffffff', '#677784', .9, 0)
    return add('image', name, asset=asset, x=x, y=y, w=w, h=h, z=25)


def vector(name, x, y, color, width=25, height=70, symbols=True):
    fill = '#dbeafb' if color == BLUE else '#e3efd5'
    node = rect(name, x, y, width, height, fill, color, 1.5, 0)
    if symbols:
        for j in range(2):
            yy = y+height*(.29+j*.43)-4.8
            if color == BLUE:
                ellipse(f'{name}-marker-{j}', x+width/2-4.8, yy, 9.6, 9.6,
                        '#8db7f0', color, 1, z=26)
            else:
                rect(f'{name}-marker-{j}', x+width/2-4.8, yy, 9.6, 9.6,
                     '#9dc57c', color, 1, 0, z=26)
    return node


def compose():
    # Panels and semantic regions are individually editable native shapes.
    rect('panel-prototype', 380, 20, 1340, 505, '#ffffff', '#5b8dff', 1.5,
         20, dash=True, z=0)
    rect('panel-support-preparation', 395, 80, 1310, 190, PALE_BLUE,
         None, 0, 17, z=0)
    rect('panel-query-readout', 395, 282, 1310, 225, PALE_BLUE,
         None, 0, 17, z=0)
    rect('panel-visual-prompts', 380, 548, 1340, 225, PALE_GREEN,
         '#b5d5a8', 1, 15, z=0)
    rect('support-card', 20, 80, 330, 320, '#ffffff', CYAN, 1.6, 18)
    rect('query-card', 20, 452, 245, 230, '#ffffff', CYAN, 1.6, 18)

    text('title-prototype', 'Query-Conditioned Prototype Mixing',
         400, 29, 1020, 43, 31, bold=True, italic=True, align='left')
    text('title-support-prep', 'Source-support preparation',
         410, 91, 400, 30, 22, bold=True, italic=True, align='left')
    text('title-query-readout', 'Query readout (per class)',
         410, 290, 300, 32, 22, color='#1255cc', italic=True, align='left')
    text('title-stagewise', 'Stage-wise Visual Prompting',
         401, 557, 430, 34, 27, bold=True, italic=True, align='left')
    text('label-shared-support', 'Shared Support Set', 42, 94, 285, 32,
         25, italic=True)
    text('label-support-budget', 'K real + K fake', 55, 133, 260, 31,
         23, italic=True)
    text('label-real', 'Real  c = 0', 42, 172, 190, 27, 20, BLUE,
         italic=True, align='left')
    text('label-fake', 'Fake  c = 1', 42, 281, 190, 27, 20, GREEN,
         italic=True, align='left')
    for j, xx in enumerate([43, 139, 235], 1):
        photo('support-real-'+str(j), 'support-real-'+str(j)+'.png',
              xx, 205, 70, 65)
        photo('support-fake-'+str(j), 'support-fake-'+str(j)+'.png',
              xx, 315, 70, 65)
    text('label-query-image', 'Query Image', 40, 465, 205, 35, 26,
         italic=True)
    photo('query-photo', 'query.png', 66, 513, 150, 145)

    # Both frozen encoders have exactly the same dimensions.
    for name, yy in [('support-encoder', 140), ('query-encoder', 348)]:
        rect(name, 470, yy, 150, 100)
        text(name+'-label', 'Image\nEncoder', 481, yy+11, 128, 70, 23,
             italic=True)
        snowflake(name+'-snowflake', 594, yy+73, 23)
        text(name+'-backbone', 'CLIP · block 12', 458, yy+105, 178, 28,
             21, italic=True)
    ellipse('support-junction', 361, 211, 8, 8, GOLD, GOLD, 0, z=26)
    line('support-to-encoder', [(350, 215), (470, 215)],
         start=('support-card', 1, .578125),
         end=('support-encoder', 0, .75))
    line('query-upper', [(265, 537), (340, 537), (340, 398), (470, 398)],
         start=('query-card', 1, 85/230), end=('query-encoder', 0, .5))
    text('query-upper-label', 'Query\ninference', 269, 477, 88, 50,
         17, italic=True)
    line('query-lower', [(265, 613), (331, 613), (331, 715), (436, 715)],
         start=('query-card', 1, 161/230), end=('prompt-1a', 0, .5))
    text('query-lower-label', 'Query\ninference', 270, 620, 85, 49,
         17, italic=True)
    line('shared-support-train-rail-top', [(365, 215), (365, 386)], GOLD,
         1.7, arrow=False, dash=True)
    line('shared-support-train-rail-bottom',
         [(365, 410), (365, 601), (850, 601)], GOLD,
         1.7, dash=True, end=('prompt-training-operation', 0, 43/81))

    # Class-separated support feature bank.
    rect('support-feature-bank-anchor', 730, 145, 285, 75,
         None, None, 0, 0)
    for group, xx, color in [('real', 730, BLUE), ('fake', 900, GREEN)]:
        for j in range(4):
            vector(f'bank-{group}-{j}', xx+j*30, 145, color,
                   width=23, height=75)
        line('bracket-bank-'+group,
             [(xx-2, 139), (xx-2, 133), (xx+111, 133), (xx+111, 139)],
             '#52616a', 1.25, arrow=False, z=26)
        text('label-bank-K-'+group, 'K', xx+30, 103, 55, 28, 23,
             italic=True)
    text('bank-ellipsis', '···', 849, 163, 45, 36, 27)
    text('label-bank', 'Support Feature Bank', 720, 225, 325, 30, 22,
         italic=True)
    line('encoder-to-bank', [(620, 190), (730, 190)],
         start=('support-encoder', 1, .5), end=('support-feature-bank-anchor', 0, .6))
    line('bank-to-means', [(1015, 189), (1133, 189)],
         start=('support-feature-bank-anchor', 1, .587),
         end=('global-real', 0, .587))
    text('label-1024', '1024-D', 1028, 202, 104, 27, 21, italic=True)
    vector('global-real', 1133, 145, BLUE, 28, 75)
    vector('global-fake', 1234, 145, GREEN, 28, 75)
    text('global-real-symbol', 'μ₀', 1117, 111, 63, 29, 27, italic=True)
    text('global-fake-symbol', 'μ₁', 1217, 111, 63, 29, 27, italic=True)
    text('global-ellipsis', '···', 1172, 171, 46, 31, 27)
    text('global-caption', 'Global means μ_c', 1085, 231, 235, 28, 22,
         italic=True)
    line('global-bracket', [(1118, 104), (1118, 98), (1278, 98), (1278, 104)],
         '#52616a', 1.25, arrow=False, z=26)
    text('cached-caption', 'Cached before queries', 1086, 68, 239, 27,
         21, italic=True)
    rect('formula-prototype-card', 1380, 118, 306, 112, '#ffffff',
         '#638fff', 1.2, 11)
    text('formula-prototype-score', 'sₚ = 15 qᵀ(μ̃₁(q) − μ̃₀(q))',
         1391, 129, 284, 42, 24, italic=True)
    text('formula-prototype-prob', 'pₚ = σ(sₚ)',
         1391, 176, 284, 34, 26, italic=True, align='left')

    # Query-conditioned class-wise weighting, not a static prototype detector.
    rect('classwise-weighting', 700, 307, 320, 176,
         '#f8fbff', '#b3c2cd', 1.2, 12, dash=True, z=1)
    text('weighting-title', 'Class-wise query weighting',
         710, 315, 300, 29, 22, italic=True)
    text('weighting-softmax', 'Per-class softmax · β = 15',
         710, 343, 300, 29, 21, italic=True)
    line('bank-to-query-weighting',
         [(730, 205), (680, 205), (680, 297), (725, 297), (725, 307)],
         start=('support-feature-bank-anchor', 0, .8),
         end=('classwise-weighting', 25/320, 0))
    line('query-to-weighting', [(620, 398), (700, 398)],
         start=('query-encoder', 1, .5), end=('classwise-weighting', 0, 91/176))
    text('query-feature-q', 'q', 639, 363, 46, 30, 26, italic=True)
    for j, (xx, yy, color, dashed) in enumerate([
            (740, 389, INK, False), (790, 380, BLUE, False),
            (845, 383, BLUE, True), (895, 392, '#8e9ea9', True)]):
        line(f'weight-edge-{j}', [(xx, yy), (837, 450)],
             color, 1.7, arrow=False, dash=dashed)
        ellipse(f'weight-support-{j}', xx-9, yy-9, 18, 18,
                '#abcaf5', BLUE, 1.1, z=26)
    poly('query-symbol', [(837, 436), (850, 449), (837, 462), (824, 449)],
         '#9ba6ad', '#34434e', 1.3, z=26)
    text('query-symbol-label', 'q', 855, 429, 37, 37, 28, italic=True)
    text('weight-more', '···', 931, 383, 55, 35, 25)
    # Local vector carries magnitude until AFTER mixing.
    rect('local-vector', 1080, 370, 35, 75, '#8db7e4', BLUE, 1.4, 0)
    line('local-split-1', [(1080, 395), (1115, 395)], BLUE, 1.2, False, z=26)
    line('local-split-2', [(1080, 420), (1115, 420)], BLUE, 1.2, False, z=26)
    text('label-local', 'Local m_c(q)', 1030, 330, 145, 31, 23,
         italic=True)
    text('label-unnormalized', 'unnormalized', 1035, 448, 135, 28, 18,
         italic=True)
    line('weighting-to-local', [(1020, 407), (1080, 407)],
         start=('classwise-weighting', 1, 100/176), end=('local-vector', 0, .493))
    rect('mix-normalize', 1210, 380, 122, 86, '#fff5d8', '#b3a97d', 1.3, 12)
    text('mix-label', 'Mix, then\nnormalize', 1218, 392, 106, 61, 22,
         italic=True)
    line('global-to-mix', [(1183, 270), (1183, 395), (1210, 395)],
         end=('mix-normalize', 0, 15/86))
    # Invisible semantic anchor for the two global class vectors.
    rect('global-means-anchor', 1133, 145, 129, 125, None, None, 0, 0)
    SCENE[-2]['start'] = ('global-means-anchor', 50/129, 1)
    text('global-half', '0.5', 1189, 343, 61, 29, 23, italic=True)
    line('local-to-mix', [(1115, 418), (1210, 418)],
         start=('local-vector', 1, .64), end=('mix-normalize', 0, 38/86))
    text('local-half', '0.5', 1132, 383, 63, 29, 23, italic=True)
    vector('direction-real', 1380, 377, BLUE, 25, 43, symbols=False)
    vector('direction-fake', 1450, 377, GREEN, 25, 43, symbols=False)
    ellipse('direction-real-marker', 1387, 390, 11, 11,
            '#8db7f0', BLUE, 1, z=26)
    rect('direction-fake-marker', 1457, 390, 11, 11,
         '#9dc57c', GREEN, 1, 0, z=26)
    rect('directions-anchor', 1380, 377, 95, 43, None, None, 0, 0)
    text('directions-title', 'Class directions', 1337, 303, 180, 28,
         22, italic=True)
    text('directions-symbols', 'μ̃₀(q)   μ̃₁(q)', 1344, 335, 176, 33,
         24, italic=True)
    text('directions-ellipsis', '···', 1410, 378, 37, 31, 25)
    line('mix-to-directions', [(1332, 407), (1380, 407)],
         start=('mix-normalize', 1, 27/86), end=('directions-anchor', 0, 30/43))
    rect('prototype-similarity', 1510, 383, 110, 76)
    text('prototype-similarity-label', 'Similarity\nmargin', 1517, 394,
         96, 54, 22, italic=True)
    line('directions-to-similarity', [(1427.5, 420), (1427.5, 430), (1510, 430)],
         start=('directions-anchor', .5, 1),
         end=('prototype-similarity', 0, 47/76))
    line('query-direct-similarity',
         [(837, 462), (837, 489), (1565, 489), (1565, 459)],
         start=('query-symbol', .5, 1),
         end=('prototype-similarity', .5, 1))
    text('no-trained-prototype-weights', 'No task-learned weights.',
         1467, 494, 236, 23, 16, italic=True)
    pp = text('probability-prototype', 'pₚ = σ(sₚ)',
              1628, 398, 90, 43, 23, italic=True)
    line('prototype-similarity-output', [(1620, 420), (1628, 420)],
         start=('prototype-similarity', 1, 37/76), end=(pp, 0, .5), arrow=False)

    # Shared-support-only fitting, and four replacement prompt pairs.
    rect('prompt-training-operation', 850, 558, 500, 81,
         '#fff8e7', '#c89c4a', 1.25, 10)
    text('training-heading', 'Fit prompts on shared supports',
         860, 564, 480, 25, 22, bold=True, italic=True)
    text('training-input-loss', 'Support images + labels · fixed-text cross-entropy',
         862, 589, 476, 23, 18, italic=True)
    text('training-update', 'Only prompts updated · 8,192 parameters',
         862, 612, 476, 22, 18, italic=True)
    text('prompt-replacement-caption',
         '2 prompts per stage · replaced at blocks 1 / 7 / 13 / 19',
         545, 644, 815, 28, 19, italic=True)
    line('fitted-prompts-rail', [(1315, 639), (1315, 678), (447, 678)],
         GOLD, 1.6, arrow=False, dash=True,
         start=('prompt-training-operation', 465/500, 1))
    for j, (xx, label) in enumerate([(480, '1–6'), (720, '7–12'),
                                    (960, '13–18'), (1200, '19–24')], 1):
        for suffix, dx in [('a', -44), ('b', -22)]:
            rect(f'prompt-{j}{suffix}', xx+dx, 695, 18, 40,
                 '#ffe5a5', '#d89a22', 1.4, 0)
        line(f'fitted-prompts-drop-{j}', [(xx-33, 678), (xx-33, 692)],
             GOLD, 1.6, dash=True, end=(f'prompt-{j}a', .61, 0))
        stage = rect(f'stage-{j}', xx, 680, 140, 70)
        text(f'stage-label-{j}', label, xx+8, 693, 118, 42, 25,
             italic=True)
        snowflake(f'stage-snowflake-{j}', xx+113, 723, 23)
        line(f'prompt-to-stage-{j}', [(xx-4, 715), (xx, 715)],
             arrow=False, start=(f'prompt-{j}b', 1, .5), end=(stage, 0, .5))
        if j < 4:
            line(f'stage-to-prompt-{j+1}', [(xx+140, 715), (xx+196, 715)],
                 start=(stage, 1, .5), end=(f'prompt-{j+1}a', 0, .5))

    # Frozen text anchors and final projected visual feature.
    rect('fixed-text-anchors', 1430, 558, 260, 91)
    text('fixed-text-title', 'Fixed text anchors', 1442, 565, 237, 29,
         21, italic=True)
    rect('fixed-text-real', 1453, 601, 82, 32, '#f4fbff', '#b6d8ec', 1, 0)
    rect('fixed-text-fake', 1549, 601, 82, 32, '#f9fff1', '#bad496', 1, 0)
    text('fixed-text-real-label', '“real”', 1457, 600, 75, 32, 23,
         BLUE, italic=True)
    text('fixed-text-fake-label', '“fake”', 1553, 600, 75, 32, 23,
         GREEN, italic=True)
    snowflake('text-anchor-snowflake', 1652, 615, 24)
    rect('prompt-similarity', 1450, 687, 113, 65)
    text('prompt-similarity-label', 'Similarity', 1456, 699, 101, 39,
         22, italic=True)
    line('stage4-to-similarity', [(1340, 715), (1450, 715)],
         start=('stage-4', 1, .5), end=('prompt-similarity', 0, 28/65))
    text('label-768', '768-D', 1350, 682, 93, 27, 22, italic=True)
    line('fixed-text-to-similarity', [(1530, 649), (1530, 687)],
         start=('fixed-text-anchors', 100/260, 1),
         end=('prompt-similarity', 80/113, 0))
    pv = text('probability-visual', 'pᵥ = σ(15Δᵥ)\nΔᵥ = vᵀ(t₁ − t₀)',
              1577, 687, 152, 65, 19, italic=True)
    line('prompt-similarity-output', [(1563, 720), (1577, 720)],
         start=('prompt-similarity', 1, 33/65), end=(pv, 0, .5), arrow=False)

    # Fixed equal averaging, with no learned third branch or classifier.
    ellipse('fusion-node', 1762, 477, 56, 56, '#ffffff', INK, 1.7)
    line('fusion-plus-horizontal', [(1774, 505), (1806, 505)], INK,
         1.7, False, z=26)
    line('fusion-plus-vertical', [(1790, 489), (1790, 521)], INK,
         1.7, False, z=26)
    line('prototype-to-fusion', [(1718, 420), (1790, 420), (1790, 477)],
         start=(pp, 1, .5), end=('fusion-node', .5, 0))
    line('visual-to-fusion', [(1729, 720), (1790, 720), (1790, 533)],
         start=(pv, 1, .5), end=('fusion-node', .5, 1))
    text('fusion-upper-half', '0.5', 1730, 385, 65, 30, 24, italic=True)
    text('fusion-lower-half', '0.5', 1799, 553, 65, 30, 24, italic=True)
    text('fusion-title', 'Equal probability\nfusion',
         1826, 334, 203, 70, 25, italic=True)
    text('fusion-equation', 'p = (pₚ + pᵥ)/2',
         1821, 414, 210, 46, 28, italic=True)
    rect('prediction', 1870, 470, 155, 70, '#ffffff', INK, 1.6, 10)
    text('prediction-label', 'Real / Fake', 1876, 485, 143, 40, 26,
         italic=True)
    line('fusion-to-prediction', [(1818, 505), (1870, 505)],
         start=('fusion-node', 1, .5), end=('prediction', 0, .5))
    text('threshold', 'p > 0.5: fake', 1850, 548, 185, 37, 23,
         italic=True)

    # Footer and small symbol legend.
    rect('parameter-summary-panel', 520, 801, 1125, 42,
         '#f6faff', '#82a8eb', 1, 11, z=0)
    text('parameter-summary',
         'Frozen visual and text backbone; 4 × 2 × 1024 = 8,192 trainable prompt parameters total.',
         530, 805, 1105, 33, 22, italic=True)
    rect('legend-panel', 95, 856, 1858, 39, '#ffffff', '#9da4aa', 1, 10, z=0)
    ellipse('legend-real-marker', 116, 868, 16, 16, '#abcaf5', BLUE, 1.2)
    text('legend-real-label', 'Real (c = 0)', 142, 861, 148, 28, 18, italic=True)
    rect('legend-fake-marker', 304, 868, 16, 16, '#c8dfb3', GREEN, 1.2, 0)
    text('legend-fake-label', 'Fake (c = 1)', 327, 861, 142, 28, 18, italic=True)
    snowflake('legend-frozen', 491, 864, 24)
    text('legend-frozen-label', 'Frozen (CLIP / text)', 522, 861, 220, 28,
         18, italic=True)
    rect('legend-prompt-a', 765, 865, 14, 22, '#ffe5a5', '#d89a22', 1.2, 0)
    rect('legend-prompt-b', 784, 865, 14, 22, '#ffe5a5', '#d89a22', 1.2, 0)
    text('legend-prompt-label', 'Trainable prompts (8,192)',
         809, 861, 260, 28, 18, italic=True)
    line('legend-forward-line', [(1095, 876), (1140, 876)], lw=1.7, z=26)
    text('legend-forward-label', 'Image / feature flow', 1148, 861, 226, 28,
         18, italic=True)
    line('legend-training-line', [(1411, 876), (1456, 876)], GOLD,
         1.7, dash=True, z=26)
    text('legend-training-label', 'Support fitting / fitted parameters',
         1465, 861, 470, 28, 18, italic=True, align='left')


SVG = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
V = 'http://schemas.microsoft.com/office/visio/2012/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'


def n(v):
    return f'{float(v):.8g}'


def xml_bytes(root):
    # OPC relationship readers expect the package namespace as the default.
    # Keep the familiar r: prefix for relationship IDs inside Visio parts.
    if root.tag.startswith('{'):
        ET.register_namespace('', root.tag[1:].split('}')[0])
    ET.register_namespace('r', R)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def write_svg():
    ET.register_namespace('', SVG)
    ET.register_namespace('xlink', XLINK)
    root = ET.Element(f'{{{SVG}}}svg', dict(width=f'{W/UNIT}in',
                      height=f'{H/UNIT}in', viewBox=f'0 0 {W} {H}'))
    ET.SubElement(root, 'title').text = 'Editable query-conditioned prototype mixing and staged visual prompting'
    ET.SubElement(root, 'desc').text = 'All method geometry and text are editable vector objects. Only seven photographs are raster images.'
    defs = ET.SubElement(root, 'defs')
    for color, key in [(INK, 'black'), (GOLD, 'gold'), (BLUE, 'blue')]:
        marker = ET.SubElement(defs, 'marker', dict(id='arrow-'+key,
                  viewBox='0 0 10 10', refX='9', refY='5', markerWidth='7',
                  markerHeight='7', orient='auto-start-reverse', markerUnits='userSpaceOnUse'))
        ET.SubElement(marker, 'path', dict(d='M 0 0 L 10 5 L 0 10 z', fill=color))
    ET.SubElement(root, 'rect', dict(width=str(W), height=str(H), fill='white'))
    for s in sorted(SCENE, key=lambda s: s['z']):
        name, kind = s['name'], s['kind']
        attrs = dict(id=name)
        if kind in ['rect', 'ellipse']:
            if kind == 'rect':
                attrs.update(x=n(s['x']), y=n(s['y']), width=n(s['w']),
                             height=n(s['h']), rx=n(s['r']))
            else:
                attrs.update(cx=n(s['x']+s['w']/2), cy=n(s['y']+s['h']/2),
                             rx=n(s['w']/2), ry=n(s['h']/2))
            attrs.update(fill=s['fill'] or 'none', stroke=s['stroke'] or 'none')
            attrs['stroke-width'] = n(s['lw'])
            if s.get('dash'):
                attrs['stroke-dasharray'] = '9 6'
            ET.SubElement(root, kind, attrs)
        elif kind in ['line', 'poly']:
            attrs.update(points=' '.join(f'{n(x)},{n(y)}' for x,y in s['points']),
                         fill=s.get('fill') or 'none', stroke=s.get('color',s.get('stroke', INK)),
                         **{'stroke-width':n(s['lw']), 'stroke-linejoin':'round',
                            'stroke-linecap':'round'})
            if s.get('dash'): attrs['stroke-dasharray'] = '7 5'
            if s.get('arrow'):
                key = 'gold' if s['color']==GOLD else 'blue' if s['color']==BLUE else 'black'
                attrs['marker-end'] = f'url(#arrow-{key})'
            ET.SubElement(root, 'polygon' if kind=='poly' else 'polyline', attrs)
        elif kind == 'snowflake':
            attrs.update(d=' '.join(f'M {n(a[0])} {n(a[1])} L {n(b[0])} {n(b[1])}'
                                   for a,b in s['segments']), fill='none',
                         stroke=s['stroke'], **{'stroke-width':n(s['lw']), 'stroke-linecap':'round'})
            ET.SubElement(root, 'path', attrs)
        elif kind == 'image':
            content=(ROOT/'assets'/s['asset']).read_bytes()
            attrs.update(x=n(s['x']), y=n(s['y']), width=n(s['w']), height=n(s['h']),
                         preserveAspectRatio='none')
            attrs[f'{{{XLINK}}}href']='data:image/png;base64,'+base64.b64encode(content).decode()
            ET.SubElement(root, 'image', attrs)
        elif kind == 'text':
            fs=s['fs']; lines=s['value'].split('\n')
            anchor='middle' if s['align']=='center' else 'start'
            x=s['x']+s['w']/2 if anchor=='middle' else s['x']+2
            baseline=s['y']+(s['h']-len(lines)*fs*1.15)/2+fs*.88
            attrs.update(x=n(x), y=n(baseline), fill=s['color'],
                         **{'font-family':'Arial, Liberation Sans, DejaVu Sans, sans-serif',
                            'font-size':n(fs),'font-weight':'bold' if s['bold'] else 'normal',
                            'font-style':'italic' if s['italic'] else 'normal',
                            'text-anchor':anchor})
            t=ET.SubElement(root,'text',attrs)
            for i, value in enumerate(lines):
                span=ET.SubElement(t,'tspan',dict(x=n(x),y=n(baseline+i*fs*1.15)))
                if '_c' in value:
                    before,after=value.split('_c',1)
                    span.text=before
                    sub=ET.SubElement(span,'tspan',{'baseline-shift':'sub','font-size':n(fs*.72)})
                    sub.text='c';sub.tail=after
                else:
                    span.text=value
    (ROOT/'framework-editable.svg').write_bytes(xml_bytes(root))


def cell(parent, name, value, formula=None, unit=None):
    a={'N':name, 'V':str(value)}
    if formula: a['F']=formula
    if unit: a['U']=unit
    return ET.SubElement(parent,f'{{{V}}}Cell',a)


def bounds(s):
    if 'x' in s: return s['x'], s['y'], s['w'], s['h']
    p=s['points']
    x=min(a[0] for a in p); y=min(a[1] for a in p)
    return x,y,max(a[0] for a in p)-x,max(a[1] for a in p)-y


def write_vsdx():
    ET.register_namespace('', V); ET.register_namespace('r', R)
    q=lambda tag:f'{{{V}}}{tag}'
    root=ET.Element(q('PageContents'),{'{http://www.w3.org/XML/1998/namespace}space':'preserve'})
    shapes=ET.SubElement(root,q('Shapes'))
    connects=ET.SubElement(root,q('Connects'))
    ordered=sorted(SCENE,key=lambda s:s['z'])
    id_map={s['name']:str(i+1) for i,s in enumerate(ordered)}
    source_map={s['name']:s for s in SCENE}
    image_rels=[]
    native_ids={}
    categories=['Background panels','Method shapes','Editable text','Connectors','Photographs','Vector symbols']

    def endpoint(shape, prefix, anchor):
        if not anchor: return
        name, rx, ry=anchor
        target=source_map[name]
        x,y,w,h=bounds(target)
        sid=id_map[name]
        # Simple, stable formulas keep endpoints attached to editable target boxes.
        for axis, factor in [('X',rx-.5),('Y',.5-ry)]:
            size='Width' if axis=='X' else 'Height'
            form=f'Sheet.{sid}!Pin{axis}+Sheet.{sid}!{size}*({factor:.10g})'
            shcell=shape.find(f'{q("Cell")}[@N="{prefix}{axis}"]')
            shcell.set('F',form)
        ET.SubElement(connects,q('Connect'),dict(
            FromSheet=shape.attrib['ID'],FromCell=prefix+'X',
            FromPart='9' if prefix=='Begin' else '12',
            ToSheet=sid,ToCell='PinX',ToPart='3'))

    for s in ordered:
        kind=s['kind']; sid=id_map[s['name']]
        sh=ET.SubElement(shapes,q('Shape'),dict(ID=sid,NameU=s['name'],Name=s['name'],
                          Type='Foreign' if kind=='image' else 'Shape',
                          LineStyle='0',FillStyle='0',TextStyle='0'))
        native_ids[s['name']]=sid
        x,y,w,h=bounds(s)
        # Use a nondegenerate bounding box for pure horizontal/vertical geometry.
        bw,bh=max(w,.01),max(h,.01)
        for name,value in [('PinX',(x+bw/2)/UNIT),('PinY',(H-y-bh/2)/UNIT),
                           ('Width',bw/UNIT),('Height',bh/UNIT),
                           ('LocPinX',bw/(2*UNIT)),('LocPinY',bh/(2*UNIT)),
                           ('Angle',0),('ResizeMode',0),('ShapeShdwShow',0),
                           ('LockTextEdit',0),('LockSelect',0),('LockFormat',0)]:
            cell(sh,name,n(value))
        layer=0 if s['z']<=1 else 2 if kind=='text' else 3 if kind=='line' else 4 if kind=='image' else 5 if kind in ['poly','snowflake'] else 1
        cell(sh,'LayerMember',layer)
        stroke=None if kind=='text' else s.get('stroke',s.get('color'))
        fill=s.get('fill')
        cell(sh,'LineColor',stroke or '#000000')
        cell(sh,'LineWeight',n(s.get('lw',0)/UNIT))
        cell(sh,'LinePattern',2 if s.get('dash') else 1 if stroke else 0)
        cell(sh,'FillForegnd',fill or '#ffffff')
        cell(sh,'FillPattern',1 if fill else 0)
        cell(sh,'Rounding',n(s.get('r',0)/UNIT))
        cell(sh,'LineCap',1)
        cell(sh,'BeginArrow',0)
        cell(sh,'EndArrow',4 if s.get('arrow') else 0)
        cell(sh,'EndArrowSize',0)
        cell(sh,'BeginArrowSize',0)
        geom=ET.SubElement(sh,q('Section'),{'N':'Geometry','IX':'0'})
        cell(geom,'NoFill',0 if fill else 1)
        cell(geom,'NoLine',0 if stroke and kind!='image' else 1)

        def row(typ, ix, **values):
            r=ET.SubElement(geom,q('Row'),{'T':typ,'IX':str(ix)})
            for k,v in values.items():
                if isinstance(v,tuple):cell(r,k,n(v[0]),v[1])
                else:cell(r,k,n(v))
            return r

        def local(p): return (p[0]-x)/UNIT,(y+bh-p[1])/UNIT

        if kind=='rect' and s.get('r',0)>0:
            # Explicit quarter-circle Beziers survive independent importers;
            # a Shapesheet Rounding cell alone is not rendered by all readers.
            rr=min(s['r'],bw/2,bh/2)
            rx,ry=rr/bw,rr/bh
            k=.5522847498307936
            row('RelMoveTo',1,X=rx,Y=0)
            row('RelLineTo',2,X=1-rx,Y=0)
            row('RelCubBezTo',3,X=1,Y=ry,A=1-rx+k*rx,B=0,C=1,D=ry-k*ry)
            row('RelLineTo',4,X=1,Y=1-ry)
            row('RelCubBezTo',5,X=1-rx,Y=1,A=1,B=1-ry+k*ry,C=1-rx+k*rx,D=1)
            row('RelLineTo',6,X=rx,Y=1)
            row('RelCubBezTo',7,X=0,Y=1-ry,A=rx-k*rx,B=1,C=0,D=1-ry+k*ry)
            row('RelLineTo',8,X=0,Y=ry)
            row('RelCubBezTo',9,X=rx,Y=0,A=0,B=ry-k*ry,C=rx-k*rx,D=0)
        elif kind in ['rect','text','image']:
            for ix,(a,b) in enumerate([(0,0),(1,0),(1,1),(0,1),(0,0)],1):
                row('RelMoveTo' if ix==1 else 'RelLineTo',ix,X=a,Y=b)
        elif kind=='ellipse':
            row('Ellipse',1,X=(bw/(2*UNIT),'Width*0.5'),Y=(bh/(2*UNIT),'Height*0.5'),
                A=(bw/UNIT,'Width'),B=(bh/(2*UNIT),'Height*0.5'),
                C=(bw/(2*UNIT),'Width*0.5'),D=(bh/UNIT,'Height'))
        elif kind in ['line','poly']:
            points=s['points']+([s['points'][0]] if kind=='poly' else [])
            for ix,p in enumerate(points,1):
                lx,ly=local(p)
                row('MoveTo' if ix==1 else 'LineTo',ix,
                    X=(lx,f'Width*{lx/(bw/UNIT):.12g}'),
                    Y=(ly,f'Height*{ly/(bh/UNIT):.12g}'))
            if kind=='line':
                begin,finish=s['points'][0],s['points'][-1]
                for prefix,p in [('Begin',begin),('End',finish)]:
                    cell(sh,prefix+'X',n(p[0]/UNIT))
                    cell(sh,prefix+'Y',n((H-p[1])/UNIT))
                endpoint(sh,'Begin',s.get('start'))
                endpoint(sh,'End',s.get('end'))
                cell(sh,'ObjType',2)
                cell(sh,'ConLineJumpCode',2)  # crossings do not imply connections
        elif kind=='snowflake':
            ix=0
            for segment in s['segments']:
                for j,p in enumerate(segment):
                    ix+=1; lx,ly=local(p)
                    row('MoveTo' if j==0 else 'LineTo',ix,
                        X=(lx,f'Width*{lx/(bw/UNIT):.12g}'),
                        Y=(ly,f'Height*{ly/(bh/UNIT):.12g}'))
        if kind=='text':
            for k,val in [('LeftMargin',0),('RightMargin',0),('TopMargin',0),
                          ('BottomMargin',0),('VerticalAlign',1),('TextBkgnd',0),
                          ('TextBkgndTrans',1),('IsTextEditTarget',1)]:cell(sh,k,val)
            char=ET.SubElement(sh,q('Section'),{'N':'Character'})
            rr=ET.SubElement(char,q('Row'),{'IX':'0'})
            cell(rr,'Font','Arial')
            cell(rr,'Color',s['color'])
            cell(rr,'Size',n(s['fs']/UNIT))
            cell(rr,'Style',int(s['bold'])+2*int(s['italic']))
            cell(rr,'LangID','en-US')
            if '_c' in s['value']:
                subrow=ET.SubElement(char,q('Row'),{'IX':'1'})
                for k,val in [('Font','Arial'),('Color',s['color']),
                              ('Size',n(s['fs']/UNIT)),
                              ('Style',int(s['bold'])+2*int(s['italic'])),('Pos',2)]:
                    cell(subrow,k,val)
            para=ET.SubElement(sh,q('Section'),{'N':'Paragraph'})
            rr=ET.SubElement(para,q('Row'),{'IX':'0'})
            cell(rr,'HorzAlign',1 if s['align']=='center' else 0)
            cell(rr,'SpLine',-1.15)
            cell(rr,'SpBefore',0); cell(rr,'SpAfter',0)
            txt=ET.SubElement(sh,q('Text'))
            if '_c' in s['value']:
                before,after=s['value'].split('_c',1)
                txt.text=before
                cp=ET.SubElement(txt,q('cp'),{'IX':'1'});cp.tail='c'
                cp=ET.SubElement(txt,q('cp'),{'IX':'0'});cp.tail=after
            else:
                txt.text=s['value']
        if kind=='image':
            num=len(image_rels)+1; relid='rIdImage'+str(num)
            image_rels.append((relid,s['asset']))
            for k,val,f in [('ImgOffsetX',0,None),('ImgOffsetY',0,None),
                            ('ImgWidth',bw/UNIT,'Width'),('ImgHeight',bh/UNIT,'Height')]:
                cell(sh,k,n(val),f)
            foreign=ET.SubElement(sh,q('ForeignData'),{'ForeignType':'Bitmap','CompressionType':'PNG'})
            ET.SubElement(foreign,q('Rel'),{f'{{{R}}}id':relid})
        # ShapeContents follows the native schema sequence, not construction order.
        priority={'Cell':0,'Trigger':1,'Section':2,'Text':3,'ForeignData':4}
        sh[:]=sorted(sh,key=lambda e:priority.get(e.tag.rsplit('}',1)[-1],5))

    # A small, explicit Visio document; no hidden diagram-sized raster or macros.
    document=ET.Element(q('VisioDocument'))
    settings=ET.SubElement(document,q('DocumentSettings'),dict(
        TopPage='0',DefaultTextStyle='0',DefaultLineStyle='0',DefaultFillStyle='0'))
    ET.SubElement(settings,q('GlueSettings')).text='9'
    ET.SubElement(settings,q('SnapSettings')).text='65847'
    colors=ET.SubElement(document,q('Colors'))
    ET.SubElement(colors,q('ColorEntry'),{'IX':'0','RGB':'#000000'})
    ET.SubElement(colors,q('ColorEntry'),{'IX':'1','RGB':'#FFFFFF'})
    faces=ET.SubElement(document,q('FaceNames'))
    ET.SubElement(faces,q('FaceName'),{'NameU':'Arial'})
    styles=ET.SubElement(document,q('StyleSheets'))
    style=ET.SubElement(styles,q('StyleSheet'),{'ID':'0','NameU':'No Style','Name':'No Style'})
    for k,val in [('LineWeight',.01),('LineColor',0),('LinePattern',1),
                  ('FillForegnd',1),('FillPattern',1),('ShdwPattern',0),
                  ('ShapeShdwShow',0),('LeftMargin',0),('RightMargin',0),
                  ('TopMargin',0),('BottomMargin',0),('VerticalAlign',1)]:cell(style,k,val)
    char=ET.SubElement(style,q('Section'),{'N':'Character'})
    rr=ET.SubElement(char,q('Row'),{'IX':'0'})
    for k,val in [('Font','Arial'),('Color',0),('Size',.1666667),('Style',0)]:cell(rr,k,val)
    para=ET.SubElement(style,q('Section'),{'N':'Paragraph'})
    rr=ET.SubElement(para,q('Row'),{'IX':'0'})
    for k,val in [('HorzAlign',1),('SpLine',-1.15),('SpBefore',0),('SpAfter',0)]:cell(rr,k,val)
    pages=ET.Element(q('Pages'))
    page=ET.SubElement(pages,q('Page'),dict(ID='0',NameU='Editable framework',
         Name='Editable framework',ViewScale='0.65',
         ViewCenterX=n(W/(2*UNIT)),ViewCenterY=n(H/(2*UNIT))))
    sheet=ET.SubElement(page,q('PageSheet'),dict(LineStyle='0',FillStyle='0',TextStyle='0'))
    for k,val in [('PageWidth',W/UNIT),('PageHeight',H/UNIT),('PageScale',1),
                  ('DrawingScale',1),('DrawingSizeType',0),('DrawingScaleType',0),
                  ('DrawingResizeType',1),('PrintPageOrientation',2),
                  ('PageLeftMargin',0),('PageRightMargin',0),('PageTopMargin',0),
                  ('PageBottomMargin',0)]:cell(sheet,k,n(val))
    layer=ET.SubElement(sheet,q('Section'),{'N':'Layer'})
    for i,name in enumerate(categories):
        rr=ET.SubElement(layer,q('Row'),{'IX':str(i)})
        for k,val in [('Name',name),('NameUniv',name),('Visible',1),('Print',1),
                      ('Lock',0),('Snap',1),('Glue',1),('Active',0)]:cell(rr,k,val)
    ET.SubElement(page,q('Rel'),{f'{{{R}}}id':'rId1'})

    def rels(items):
        r=ET.Element(f'{{{PKG}}}Relationships')
        for rid,typ,target in items:
            ET.SubElement(r,f'{{{PKG}}}Relationship',dict(Id=rid,Type=typ,Target=target))
        return r

    ct=ET.Element(f'{{{CT}}}Types')
    for extension,typ in [('rels','application/vnd.openxmlformats-package.relationships+xml'),
                          ('xml','application/xml'),('png','image/png')]:
        ET.SubElement(ct,f'{{{CT}}}Default',dict(Extension=extension,ContentType=typ))
    for name,typ in [('/visio/document.xml','application/vnd.ms-visio.drawing.main+xml'),
                     ('/visio/pages/pages.xml','application/vnd.ms-visio.pages+xml'),
                     ('/visio/pages/page1.xml','application/vnd.ms-visio.page+xml')]:
        ET.SubElement(ct,f'{{{CT}}}Override',dict(PartName=name,ContentType=typ))
    parts={
        '[Content_Types].xml':xml_bytes(ct),
        '_rels/.rels':xml_bytes(rels([('rId1','http://schemas.microsoft.com/visio/2010/relationships/document','visio/document.xml')])),
        'visio/document.xml':xml_bytes(document),
        'visio/_rels/document.xml.rels':xml_bytes(rels([('rId1','http://schemas.microsoft.com/visio/2010/relationships/pages','pages/pages.xml')])),
        'visio/pages/pages.xml':xml_bytes(pages),
        'visio/pages/_rels/pages.xml.rels':xml_bytes(rels([('rId1','http://schemas.microsoft.com/visio/2010/relationships/page','page1.xml')])),
        'visio/pages/page1.xml':xml_bytes(root),
        'visio/pages/_rels/page1.xml.rels':xml_bytes(rels([(rid,R+'/image','../media/'+asset) for rid,asset in image_rels]))
    }
    for _,asset in image_rels:parts['visio/media/'+asset]=(ROOT/'assets'/asset).read_bytes()
    with ZipFile(ROOT/'framework-editable.vsdx','w',ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    return dict(shape_count=len(ordered),native_text_shapes=sum(s['kind']=='text' for s in SCENE),
                native_connector_shapes=sum(s['kind']=='line' for s in SCENE),
                glued_endpoint_records=len(connects),embedded_photos=len(image_rels),
                shape_names_to_ids=native_ids,layers=categories)


def main():
    compose()
    # Validate all endpoint targets before writing any package.
    for s in SCENE:
        for key in ['start','end']:
            if s.get(key) and s[key][0] not in IDS:
                raise ValueError('Missing target '+s[key][0])
    write_svg()
    stats=write_vsdx()
    (ROOT/'framework-editable.scene.json').write_text(json.dumps(dict(
        width=W,height=H,units_per_inch=UNIT,objects=SCENE),ensure_ascii=False,indent=2)+'\n')
    # Finalize inside the complete Visio-produced shell and create the VDX
    # fallback before advertising any VSDX produced by this builder.
    from visio_compat import finalize
    compatibility = finalize(ROOT)
    stats['glued_endpoint_records'] = 0
    stats['automatic_glue'] = False
    stats['compatibility_revision'] = 2
    stats['compatibility_changes'] = compatibility
    counts=Counter(s['kind'] for s in SCENE)
    stats.update(kind_counts=dict(counts),has_full_canvas_raster=False,
                 generated_with='build_editable.py',target='Visio 2013+ desktop native shapes',
                 verification_scope='Visio/OPC schema plus independent rendering. Version 1 was reported corrupt by the user; Microsoft Visio is not available in this environment for validating version 2.')
    (ROOT/'editability-report.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in stats.items() if k!='shape_names_to_ids'},ensure_ascii=False))


if __name__=='__main__': main()
