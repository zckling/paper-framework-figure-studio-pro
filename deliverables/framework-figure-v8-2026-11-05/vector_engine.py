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
import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import ImageFont

ROOT = Path(__file__).resolve().parent
W, H, UNIT = 2000, 1160, 120.0
INK = '#20292f'
BLUE, GREEN, CYAN, GOLD = '#2873dc', '#5b9636', '#34c2dc', '#b7802c'
PALE_BLUE, PALE_GREEN = '#f0f7fd', '#f3f8f2'
GRAY = '#ebeded'
SCENE = []
IDS = set()
FONT_ROOT = Path('/usr/share/fonts/truetype/liberation')
FONTS = {}


def subscript_runs(value):
    """Keep each mathematical index editable, including repeated indices."""
    runs = []
    end = 0
    for match in re.finditer(r'_([A-Za-z0-9]+)', value):
        if match.start() > end:
            runs.append((value[end:match.start()], False))
        runs.append((match.group(1), True))
        end = match.end()
    if end < len(value):
        runs.append((value[end:], False))
    return runs


def flatten_math_text():
    """Use positioned editable runs to avoid importer-specific cp handling."""
    originals=[s for s in SCENE if s['kind']=='text' and
               any(sub for _,sub in subscript_runs(s['value']))]
    for s in originals:
        assert '\n' not in s['value']
        variant=('BoldItalic' if s['bold'] and s['italic'] else 'Bold' if s['bold']
                 else 'Italic' if s['italic'] else 'Regular')
        metrics=[]
        for content,is_sub in subscript_runs(s['value']):
            fs=s['fs']*(.72 if is_sub else 1)
            font=ImageFont.truetype(str(FONT_ROOT/('LiberationSans-'+variant+'.ttf')),round(fs*4))
            advance=font.getlength(content)/4
            metrics.append((content,is_sub,fs,advance))
        total=sum(m[3] for m in metrics)
        xx=s['x']+(s['w']-total)/2 if s['align']=='center' else s['x']+2
        baseline=s['y']+(s['h']-s['fs']*1.15)/2+s['fs']*.88
        SCENE.remove(s);IDS.remove(s['name'])
        for i,(content,is_sub,fs,advance) in enumerate(metrics):
            dy=s['fs']*.22 if is_sub else 0
            text(s['name']+f'-run-{i}',content,xx-2,baseline+dy-fs*.88,
                 advance+6,fs*1.15+.01,fs,s['color'],s['bold'],s['italic'],'left',z=s['z'])
            xx+=advance


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
                for content, is_sub in subscript_runs(value):
                    if is_sub:
                        sub=ET.SubElement(span,'tspan',{'baseline-shift':'sub','font-size':n(fs*.72)})
                        sub.text=content
                    elif len(span):
                        span[-1].tail=(span[-1].tail or '')+content
                    else:
                        span.text=(span.text or '')+content
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
        if kind=='text':
            pad=max(20,w*.18)
            if s['align']=='center':x-=pad/2
            w+=pad
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
            runs=subscript_runs(s['value'])
            if any(is_sub for _,is_sub in runs):
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
            for content,is_sub in runs:
                cp=ET.SubElement(txt,q('cp'),{'IX':'1' if is_sub else '0'})
                cp.tail=content
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
