"""Conservative Visio package finalization and a standalone VDX fallback.

The VSDX shell comes from an actual Visio-saved template shipped by the BSD-3-Clause
licensed vsdx project. See support/LICENSE-vsdx.txt. All drawing objects are our
own. This module preserves geometry and text while deliberately dropping the
old, inconsistent one-dimensional glue/transform combinations.
"""
from __future__ import annotations

import base64
import copy
import json
import math
from pathlib import Path
from xml.etree import ElementTree as E
from zipfile import ZipFile, ZIP_DEFLATED

V = 'http://schemas.microsoft.com/office/visio/2012/main'
OLD = 'http://schemas.microsoft.com/visio/2003/core'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
SPACE = '{http://www.w3.org/XML/1998/namespace}space'


def xml(node):
    E.register_namespace('', node.tag[1:].split('}')[0])
    E.register_namespace('r', R)
    return E.tostring(node, encoding='utf-8', xml_declaration=True)


def local(node):
    return node.tag.rsplit('}', 1)[-1]


def finish_vsdx(root: Path):
    root = Path(root)
    original = root / 'framework-editable.vsdx'
    with ZipFile(original) as z:
        drawing = {n: z.read(n) for n in z.namelist()}
    with ZipFile(root / 'support/visio-base.vsdx') as z:
        parts = {n: z.read(n) for n in z.namelist()}
    q = lambda n: f'{{{V}}}{n}'
    page = E.fromstring(drawing['visio/pages/page1.xml'])
    page.attrib.pop(SPACE, None)
    connects = page.find(q('Connects'))
    if connects is not None:
        page.remove(connects)
    removed_cells = {'BeginX', 'BeginY', 'EndX', 'EndY', 'BegTrigger',
                     'EndTrigger', 'ObjType', 'ConLineJumpCode', 'LayerMember'}
    removed_cross_refs = 0
    for shape in page.findall(q('Shapes') + '/' + q('Shape')):
        # A 2-D editable polyline needs no XForm1D endpoints. Mixing unrelated
        # XForm and Begin/End values caused unnecessary app-level fragility.
        for c in list(shape):
            if local(c) == 'Cell' and c.get('N') in removed_cells:
                shape.remove(c)
                removed_cross_refs += 1
        shape.set('IsCustomName', '1')
        shape.set('IsCustomNameU', '1')
        for c in shape.iter(q('Cell')):
            if 'Sheet.' in c.get('F', ''):
                c.attrib.pop('F', None)
    pages = E.fromstring(drawing['visio/pages/pages.xml'])
    # Omit layers in the compatibility version. Every object remains unlocked.
    for section in list(pages.iter(q('Section'))):
        if section.get('N') == 'Layer':
            for parent in pages.iter():
                if section in list(parent):
                    parent.remove(section)
                    break
    parts['visio/pages/page1.xml'] = xml(page)
    parts['visio/pages/pages.xml'] = xml(pages)
    # The original page relationship to the unused dynamic-connector master
    # remains valid; image relationships are assigned distinct IDs.
    page_rels = E.fromstring(parts['visio/pages/_rels/page1.xml.rels'])
    for rel in list(page_rels):
        if rel.get('Type') == R + '/image':
            page_rels.remove(rel)
    for rel in E.fromstring(drawing['visio/pages/_rels/page1.xml.rels']):
        if rel.get('Type') == R + '/image':
            page_rels.append(copy.deepcopy(rel))
    parts['visio/pages/_rels/page1.xml.rels'] = xml(page_rels)
    for name, data in drawing.items():
        if name.startswith('visio/media/'):
            parts[name] = data
    doc = E.fromstring(parts['visio/document.xml'])
    faces = doc.find(q('FaceNames'))
    if not any(f.get('NameU') == 'Arial' for f in faces):
        E.SubElement(faces, q('FaceName'), dict(
            NameU='Arial', UnicodeRanges='-536859905 -1073741829 9 0',
            CharSets='536871423 0', Panose='2 11 6 4 2 2 2 2 2 4', Flags='325'))
    # The DocumentSheet, complete style sheets, and native application
    # properties are retained from the Visio-produced shell.
    parts['visio/document.xml'] = xml(doc)
    windows = E.fromstring(parts['visio/windows.xml'])
    page_info = pages.find(q('Page'))
    for window in windows:
        if window.get('WindowType') == 'Drawing':
            window.set('ViewScale', '0.65')
            window.set('ViewCenterX', page_info.get('ViewCenterX'))
            window.set('ViewCenterY', page_info.get('ViewCenterY'))
    parts['visio/windows.xml'] = xml(windows)
    core = E.fromstring(parts['docProps/core.xml'])
    dc = 'http://purl.org/dc/elements/1.1/'
    dt = 'http://purl.org/dc/terms/'
    for child in list(core):
        if local(child) == 'lastPrinted':
            core.remove(child)
    for tag, value in [('title', 'Editable method framework v5 — two methods and two phases'),
                       ('creator', 'Figure Studio'),
                       ('description', 'Query-conditioned prototype mixing and stage-wise visual prompting')]:
        item = core.find(f'{{{dc}}}{tag}')
        if item is None:
            item = E.SubElement(core, f'{{{dc}}}{tag}')
        item.text = value
    for tag in ['created', 'modified']:
        item = core.find(f'{{{dt}}}{tag}')
        if item is not None:
            item.text = '2026-11-04T00:00:00Z'
    parts['docProps/core.xml'] = xml(core)
    custom = E.fromstring(parts['docProps/custom.xml'])
    for child in list(custom):
        custom.remove(child)
    parts['docProps/custom.xml'] = xml(custom)
    app = E.fromstring(parts['docProps/app.xml'])
    for child in app.iter():
        if local(child) == 'lpstr' and child.text == 'Page-1':
            child.text = 'Editable framework'
    parts['docProps/app.xml'] = xml(app)
    # Replace the template's unrelated thumbnail with the figure preview.
    root_rels = E.fromstring(parts['_rels/.rels'])
    for rel in root_rels:
        if rel.get('Type', '').endswith('/thumbnail'):
            rel.set('Target', 'docProps/thumbnail.png')
    parts['_rels/.rels'] = xml(root_rels)
    parts.pop('docProps/thumbnail.emf', None)
    parts['docProps/thumbnail.png'] = (root / 'framework-editable-preview.png').read_bytes()
    types = E.fromstring(parts['[Content_Types].xml'])
    if not any(n.get('Extension') == 'png' for n in types):
        E.SubElement(types, f'{{{CT}}}Default', dict(Extension='png', ContentType='image/png'))
    parts['[Content_Types].xml'] = xml(types)
    # No text relies on xml:space at part roots. Removing it also permits
    # direct validation against the published Visio 2012 XSD used by POI.
    for name, content in list(parts.items()):
        if name.startswith('visio/') and name.endswith('.xml') and '/_rels/' not in name:
            node = E.fromstring(content)
            node.attrib.pop(SPACE, None)
            parts[name] = xml(node)
    output = root / 'framework-v5.vsdx'
    with ZipFile(output, 'w', ZIP_DEFLATED) as z:
        for name, content in parts.items():
            z.writestr(name, content)
    # Refresh the unversioned working copy too, so future builds don't leave
    # the old incomplete package as their advertised default result.
    original.write_bytes(output.read_bytes())
    return dict(removed_transform_glue_cells=removed_cross_refs,
                native_shell='Visio-produced vsdx 0.6.1 media template (BSD-3-Clause)',
                automatic_glue=False)


def write_vdx(root: Path):
    """Write the standalone Visio 2003 XML format, with no OPC container."""
    root = Path(root)
    scene = json.loads((root/'framework-editable.scene.json').read_text())
    W, H, unit = scene['width'], scene['height'], scene['units_per_inch']
    q = lambda name: f'{{{OLD}}}{name}'
    E.register_namespace('', OLD)
    doc = E.Element(q('VisioDocument'), {SPACE: 'preserve'})
    props = E.SubElement(doc, q('DocumentProperties'))
    E.SubElement(props, q('Creator')).text = 'Figure Studio'
    E.SubElement(props, q('Title')).text = 'Editable method framework v5 — two methods and two phases'
    settings = E.SubElement(doc, q('DocumentSettings'), dict(
        TopPage='0', DefaultTextStyle='0', DefaultLineStyle='0', DefaultFillStyle='0'))
    E.SubElement(settings, q('GlueSettings')).text = '0'
    colors = E.SubElement(doc, q('Colors'))
    E.SubElement(colors, q('ColorEntry'), {'IX':'0', 'RGB':'#000000'})
    E.SubElement(colors, q('ColorEntry'), {'IX':'1', 'RGB':'#FFFFFF'})
    faces = E.SubElement(doc, q('FaceNames'))
    E.SubElement(faces, q('FaceName'), dict(ID='0', NameU='Arial',
        UnicodeRanges='-536859905 -1073741829 9 0', CharSets='536871423 0',
        Panose='2 11 6 4 2 2 2 2 2 4', Flags='325'))
    styles = E.SubElement(doc, q('StyleSheets'))
    style = E.SubElement(styles, q('StyleSheet'), dict(ID='0', NameU='No Style',
        Name='No Style', IsCustomName='1', IsCustomNameU='1'))

    def values(parent, name, data, attrs=None):
        section = E.SubElement(parent, q(name), attrs or {})
        for key, value in data.items():
            E.SubElement(section, q(key)).text = f'{value:.12g}' if isinstance(value, float) else str(value)
        return section

    values(style,'Line',dict(LineWeight=.01,LineColor=0,LinePattern=1,BeginArrow=0,EndArrow=0))
    values(style,'Fill',dict(FillForegnd=1,FillPattern=1,ShdwPattern=0))
    values(style,'TextBlock',dict(LeftMargin=0,RightMargin=0,TopMargin=0,BottomMargin=0,VerticalAlign=1))
    values(style,'Char',dict(Font=0,Color=0,Size=.1666666667,Style=0),{'IX':'0'})
    values(style,'Para',dict(HorzAlign=1,SpLine=-1.15,SpBefore=0,SpAfter=0),{'IX':'0'})
    E.SubElement(doc,q('DocumentSheet'),dict(NameU='TheDoc',LineStyle='0',FillStyle='0',TextStyle='0'))
    E.SubElement(doc,q('Masters'))
    pages=E.SubElement(doc,q('Pages'))
    page=E.SubElement(pages,q('Page'),dict(ID='0',NameU='Editable framework',
        Name='Editable framework',ViewScale='.65',ViewCenterX=str(W/unit/2),ViewCenterY=str(H/unit/2)))
    ps=E.SubElement(page,q('PageSheet'),dict(LineStyle='0',FillStyle='0',TextStyle='0'))
    values(ps,'PageProps',dict(PageWidth=W/unit,PageHeight=H/unit,PageScale=1,
        DrawingScale=1,DrawingSizeType=0,DrawingScaleType=0,InhibitSnap=0))
    shapes=E.SubElement(page,q('Shapes'))
    for i,s in enumerate(sorted(scene['objects'],key=lambda s:s['z']),1):
        kind=s['kind']
        if 'x' in s:x,y,w,h=[s[k] for k in ['x','y','w','h']]
        else:
            pts=s['points'];x=min(p[0] for p in pts);y=min(p[1] for p in pts)
            w=max(p[0] for p in pts)-x;h=max(p[1] for p in pts)-y
        w,h=max(w,.01),max(h,.01)
        sh=E.SubElement(shapes,q('Shape'),dict(ID=str(i),Name=s['name'],NameU=s['name'],
            IsCustomName='1',IsCustomNameU='1',Type='Foreign' if kind=='image' else 'Shape',
            LineStyle='0',FillStyle='0',TextStyle='0'))
        values(sh,'XForm',dict(PinX=(x+w/2)/unit,PinY=(H-y-h/2)/unit,
            Width=w/unit,Height=h/unit,LocPinX=w/(2*unit),LocPinY=h/(2*unit),
            Angle=0,FlipX=0,FlipY=0,ResizeMode=0))
        stroke=None if kind=='text' else s.get('stroke',s.get('color'))
        fill=s.get('fill')
        values(sh,'Line',dict(LineWeight=s.get('lw',0)/unit,LineColor=stroke or '#000000',
            LinePattern=2 if s.get('dash') else 1 if stroke else 0,
            BeginArrow=0,EndArrow=4 if s.get('arrow') else 0,EndArrowSize=0,
            BeginArrowSize=0,LineCap=1,Rounding=s.get('r',0)/unit))
        values(sh,'Fill',dict(FillForegnd=fill or '#ffffff',FillPattern=1 if fill else 0,ShdwPattern=0))
        if kind=='text':
            values(sh,'TextBlock',dict(LeftMargin=0,RightMargin=0,TopMargin=0,BottomMargin=0,
                VerticalAlign=1,TextBkgnd=0))
        if kind=='image':
            values(sh,'Foreign',dict(ImgOffsetX=0,ImgOffsetY=0,ImgWidth=w/unit,ImgHeight=h/unit))
        geom=values(sh,'Geom',dict(NoFill=0 if fill else 1,NoLine=0 if stroke and kind!='image' else 1,
                    NoShow=0,NoSnap=0),{'IX':'0'})
        def point(p):return (p[0]-x)/unit,(y+h-p[1])/unit
        def path(points, start=1, close=False):
            if close:points=points+[points[0]]
            for j,p in enumerate(points,start):
                xx,yy=point(p)
                values(geom,'MoveTo' if j==start else 'LineTo',dict(X=xx,Y=yy),{'IX':str(j)})
            return start+len(points)
        if kind=='rect' and s.get('r',0)>0:
            r=min(s['r'],w/2,h/2);points=[]
            for cx,cy,a0 in [(x+w-r,y+r,-90),(x+w-r,y+h-r,0),
                              (x+r,y+h-r,90),(x+r,y+r,180)]:
                for j in range(9):
                    a=math.radians(a0+j*90/8)
                    points.append((cx+r*math.cos(a),cy+r*math.sin(a)))
            path(points,close=True)
        elif kind in ['rect','text','image']:
            path([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],close=True)
        elif kind=='ellipse':
            values(geom,'Ellipse',dict(X=w/(2*unit),Y=h/(2*unit),A=w/unit,
                B=h/(2*unit),C=w/(2*unit),D=h/unit),{'IX':'1'})
        elif kind in ['line','poly']:
            path(s['points'],close=kind=='poly')
        elif kind=='snowflake':
            j=1
            for seg in s['segments']:j=path(seg,start=j)
        if kind=='text':
            values(sh,'Char',dict(Font=0,Color=s['color'],Size=s['fs']/unit,
                Style=int(s['bold'])+2*int(s['italic'])),{'IX':'0'})
            values(sh,'Para',dict(HorzAlign=1 if s['align']=='center' else 0,
                SpLine=-1.15,SpBefore=0,SpAfter=0),{'IX':'0'})
            t=E.SubElement(sh,q('Text'))
            E.SubElement(t,q('cp'),{'IX':'0'})
            pp=E.SubElement(t,q('pp'),{'IX':'0'})
            pp.tail=s['value'].replace('_c','c')
        if kind=='image':
            f=E.SubElement(sh,q('ForeignData'),dict(ForeignType='Bitmap',CompressionType='PNG'))
            f.text=base64.b64encode((root/'assets'/s['asset']).read_bytes()).decode('ascii')
    output=root/'framework-v5.vdx'
    output.write_bytes(xml(doc))
    return dict(shape_count=len(shapes),photo_count=7,format_namespace=OLD)


def finalize(root):
    root=Path(root)
    return dict(vsdx=finish_vsdx(root),vdx=write_vdx(root))


if __name__=='__main__':
    print(json.dumps(finalize(Path(__file__).resolve().parent),ensure_ascii=False,indent=2))
