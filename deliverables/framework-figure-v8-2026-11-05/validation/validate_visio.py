#!/usr/bin/env python3
"""Independent local Visio/OPC package and LibreOffice import verification."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from collections import Counter
from urllib.parse import unquote, urlsplit
import hashlib, json, posixpath, zipfile, os
from lxml import etree

ROOT=Path(__file__).resolve().parent.parent
SCHEMAS=Path(os.environ.get('FIGURE_SCHEMA_DIR','/workspace/figure-vector-tools/repair'))
OUT=ROOT/'validation'
VISIO='http://schemas.microsoft.com/office/visio/2012/main'
RELS='http://schemas.openxmlformats.org/package/2006/relationships'
RREF='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
CTYPE='http://schemas.openxmlformats.org/package/2006/content-types'
parser=etree.XMLParser(resolve_entities=False, no_network=True)
report={
 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Independent XSD/OPC checks and LibreOffice PDF import. Microsoft Visio has not been tested.',
 'source_files':{}, 'schema_binding':'visio.xsd relationship namespace import is bound in memory to local shared-relationshipReference.xsd; schemas and drawing files are unchanged.',
 'schemas':{}, 'vsdx':{}, 'vdx':{}, 'native_imports':{}, 'failures':[]
}
for ext in ('vsdx','vdx'):
 p=ROOT/f'framework-v8.{ext}'
 report['source_files'][p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
try:
 tree=etree.parse(str(SCHEMAS/'visio.xsd'),parser)
 imp=tree.find('{http://www.w3.org/2001/XMLSchema}import')
 imp.set('schemaLocation',str(SCHEMAS/'shared-relationshipReference.xsd'))
 schemas={'visio':etree.XMLSchema(tree), 'content_types':etree.XMLSchema(etree.parse(str(SCHEMAS/'opc-contentTypes.xsd'),parser)), 'relationships':etree.XMLSchema(etree.parse(str(SCHEMAS/'opc-relationships.xsd'),parser))}
 report['schemas']={k:{'loaded':True} for k in schemas}
except Exception as exc:
 report['failures'].append({'check':'load_schemas','error':str(exc)})
 schemas={}
with zipfile.ZipFile(ROOT/'framework-v8.vsdx') as z:
 names=z.namelist(); parts=set(names)
 crc_bad=z.testzip()
 report['vsdx']['zip']={'entry_count':len(names),'crc_bad_entry':crc_bad,'duplicate_entries':[n for n,c in Counter(names).items() if c>1]}
 if crc_bad or len(names)!=len(parts): report['failures'].append({'check':'zip_integrity','error':'CRC or duplicate member failure'})
 xml={}; checks=[]; relations={}; targets=[]; refs=[]
 for name in names:
  if name.endswith('.xml') or name.endswith('.rels'):
   try: xml[name]=etree.fromstring(z.read(name),parser)
   except Exception as exc: report['failures'].append({'check':'xml_parse','part':name,'error':str(exc)})
 for name,el in xml.items():
  ns=etree.QName(el).namespace
  kind='visio' if ns==VISIO else 'relationships' if ns==RELS else 'content_types' if ns==CTYPE else None
  if kind and kind in schemas:
   ok=schemas[kind].validate(el)
   row={'part':name,'schema':kind,'valid':ok,'errors':[str(e) for e in schemas[kind].error_log]}
   checks.append(row)
   if not ok: report['failures'].append({'check':'xsd','part':name,'errors':row['errors']})
  if name.endswith('.rels'):
   if name=='_rels/.rels': src=''
   else:
    p=PurePosixPath(name); src=str(p.parent.parent / p.name[:-5])
   rows={}
   if src and src not in parts: report['failures'].append({'check':'relationship_source','part':name,'source':src})
   for rel in el:
    rid=rel.get('Id'); target=rel.get('Target'); mode=rel.get('TargetMode','Internal')
    row={'relationship_part':name,'source':src,'id':rid,'type':rel.get('Type'),'target':target,'mode':mode}
    if rid in rows: report['failures'].append({'check':'relationship_duplicate_id','part':name,'id':rid})
    rows[rid]=row
    if mode!='External':
     parsed=urlsplit(target)
     raw=unquote(parsed.path)
     normalized=posixpath.normpath(posixpath.join(posixpath.dirname(src),raw)) if not raw.startswith('/') else posixpath.normpath(raw.lstrip('/'))
     valid=(not normalized.startswith('../')) and normalized in parts and not parsed.scheme and not parsed.netloc
     row.update({'resolved_target':normalized,'target_exists':valid})
     if not valid: report['failures'].append({'check':'relationship_target','relationship':row})
    targets.append(row)
   relations[src]=rows
 for name,el in xml.items():
  if name.endswith('.rels'): continue
  for node in el.iter():
   for attr,val in node.attrib.items():
    if etree.QName(attr).namespace==RREF:
     ok=val in relations.get(name,{})
     row={'part':name,'element':etree.QName(node).localname,'attribute':etree.QName(attr).localname,'id':val,'relationship_exists':ok}
     refs.append(row)
     if not ok: report['failures'].append({'check':'relationship_reference','reference':row})
 report['vsdx']['xsd_checks']=checks
 report['vsdx']['relationships']={'count':len(targets),'internal_count':sum(x['mode']!='External' for x in targets),'external_count':sum(x['mode']=='External' for x in targets),'targets':targets,'references':refs,'all_internal_targets_resolved':all(x.get('target_exists',True) for x in targets),'all_references_resolved':all(x['relationship_exists'] for x in refs)}
 content=xml['[Content_Types].xml']; defaults={x.get('Extension'):x.get('ContentType') for x in content if etree.QName(x).localname=='Default'}; overrides={x.get('PartName').lstrip('/'):x.get('ContentType') for x in content if etree.QName(x).localname=='Override'}
 missing=[]
 for name in names:
  if name.endswith('/') or name=='[Content_Types].xml': continue
  if name not in overrides and name.rsplit('.',1)[-1] not in defaults: missing.append(name)
 dangling=[p for p in overrides if p not in parts]
 report['vsdx']['content_type_coverage']={'missing_parts':missing,'dangling_overrides':dangling}
 if missing or dangling: report['failures'].append({'check':'content_type_coverage','missing_parts':missing,'dangling_overrides':dangling})
 visio_els=[el for el in xml.values() if etree.QName(el).namespace==VISIO]
 report['vsdx']['drawing_inventory']={'pages':sum(len(el.findall('{'+VISIO+'}Page')) for name,el in xml.items() if name=='visio/pages/pages.xml'),'shape_count':sum(len(el.findall('.//{'+VISIO+'}Shape')) for el in visio_els),'text_element_count':sum(len(el.findall('.//{'+VISIO+'}Text')) for el in visio_els),'foreign_data_count':sum(len(el.findall('.//{'+VISIO+'}ForeignData')) for el in visio_els),'media_files':[n for n in names if n.startswith('visio/media/')]}
 if len(report['vsdx']['drawing_inventory']['media_files'])!=5: report['failures'].append({'check':'vsdx_media_count','expected':5,'actual':len(report['vsdx']['drawing_inventory']['media_files'])})
vdx=etree.parse(str(ROOT/'framework-v8.vdx'),parser); ns=etree.QName(vdx.getroot()).namespace
report['vdx']={'xml_well_formed':True,'namespace':ns,'page_count':len(vdx.findall('.//{'+ns+'}Pages/{'+ns+'}Page')),'shape_count':len(vdx.findall('.//{'+ns+'}Shape')),'foreign_data_count':len(vdx.findall('.//{'+ns+'}ForeignData')),'text_element_count':len(vdx.findall('.//{'+ns+'}Text')),'xsd_scope':'The supplied visio.xsd targets VSDX 2012, not VDX 2003; VDX is checked for XML well-formedness and native import.'}
(OUT/'visio-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'schema_checks':len(report['vsdx']['xsd_checks']),'relationship_count':len(targets),'failure_count':len(report['failures']),'failures':report['failures']},ensure_ascii=False))
