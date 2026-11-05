from pathlib import Path
from collections import defaultdict
import json,fitz,hashlib,unicodedata

root=Path(__file__).resolve().parent.parent
p=root/'validation/visio-validation.json';r=json.loads(p.read_text())
scene=json.loads((root/'framework-editable.scene.json').read_text())
groups=defaultdict(list)
for s in scene['objects']:
 if '-run-' in s['name']:groups[s['name'].rsplit('-run-',1)[0]].append(s)
required=['Labeled source','2K images','Four prompt groups','2 tokens per stage','Save','Load','Query inference','no parameter updates','unseen generators','Support features','Class prototypes','Native scale','Probability average','Within-class weighting','not normalized before mixing','Drop prompt states','CLIP CLS readout','768-D','8,192']
r['limitations']=[{'classification':'schema_coverage','part':'visio/windows.xml','details':'The supplied schema does not declare the Windows root. It is preserved from a native Visio template and parses as XML.'},{'classification':'unavailable_application','details':'Microsoft Visio is not installed and has not been tested.'}]
for f in r['failures']:
 if f.get('part')=='visio/windows.xml':f['classification']='schema_coverage'
for kind in ['vsdx','vdx']:
 pdf=root/f'validation/native-{kind}/framework-v8.pdf';d=fitz.open(pdf);page=d[0]
 glyphs=[]
 for b in page.get_text('rawdict')['blocks']:
  for ln in b.get('lines',[]):
   for sp in ln['spans']:
    chars=sp['chars']
    if chars:glyphs.append({'text':unicodedata.normalize('NFC',''.join(c['c'] for c in chars)),'size':sp['size'],'origin':next((c for c in chars if not c['c'].isspace()),chars[0])['origin']})
 checks=[]
 for name,objs in groups.items():
  maxfs=max(s['fs'] for s in objs);base=None
  for s in objs:
   content=unicodedata.normalize('NFC',s['value']).strip()
   candidates=[g for g in glyphs if g['text'].strip()==content]
   expected=(s['x']*.6,(s['y']+.95*s['fs'])*.6)
   actual=min(candidates,key=lambda g:(g['origin'][0]-expected[0])**2+(g['origin'][1]-expected[1])**2) if candidates else None
   sub=s['fs']<maxfs*.9
   if not sub:base=actual
   row={'name':s['name'],'text':s['value'],'subscript':sub,'found':actual is not None,'pass':actual is not None}
   if sub and actual and base:
    row.update(baseline_drop=actual['origin'][1]-base['origin'][1],font_size_ratio=actual['size']/base['size'])
    row['pass']=row['baseline_drop']>1 and .65<row['font_size_ratio']<.8
   checks.append(row)
 text=page.get_text();compact=' '.join(text.split()).lower()
 labels={v:v.lower() in compact for v in required}
 drawings=page.get_drawings();green=[g for g in drawings if g.get('color') and all(abs(a-b)<.001 for a,b in zip(g['color'],(18/255,122/255,2/255))) and g.get('width',0)>2]
 row={'pages':len(d),'images':len(page.get_images()),'image_occurrences':len(page.get_image_info()),'drawings':len(drawings),'text_chars':len(text),'label_checks':labels,'subscript_checks':checks,'all_subscripts_pass':all(x['pass'] for x in checks),'calligraphic_source_set_present':'𝒮' in text,'source_sha256':hashlib.sha256((root/f'framework-v8.{kind}').read_bytes()).hexdigest(),'libreoffice_default_green_frame_count':len(green),'microsoft_visio_tested':False}
 row['structural_content_pass']=len(d)==1 and row['images']==5 and row['image_occurrences']==5 and row['drawings']>200 and row['all_subscripts_pass'] and all(labels.values()) and row['calligraphic_source_set_present']
 r['native_imports'][kind]=row
 pdf.with_suffix('.txt').write_text(text)
 if not row['structural_content_pass']:r['failures'].append({'classification':'native_content','format':kind,'missing_labels':[k for k,v in labels.items() if not v],'missing_subscripts':[x['name'] for x in checks if not x['pass']]})
 if green:r['limitations'].append({'classification':'LibreOffice_26.8_libvisio_import_style','format':kind,'details':f'Importer adds default green borders to{len(green)} photos despite source Foreign LinePattern0. The published SVG/Inkscape exports retain thin gray outlines; native PDFs are unmodified.'})
main=fitz.open(root/'framework-v8.pdf')
r['inkscape_pdf']={'pages':len(main),'images':len(main[0].get_images()),'drawings':len(main[0].get_drawings()),'text_chars':len(main[0].get_text()),'calligraphic_source_set_present':'𝒮' in main[0].get_text()}
r['summary']={'objects':len(scene['objects']),'native_vsdx_pass':r['native_imports']['vsdx']['structural_content_pass'],'native_vdx_pass':r['native_imports']['vdx']['structural_content_pass'],'all_relationships_valid':r['vsdx']['relationships']['all_internal_targets_resolved'] and r['vsdx']['relationships']['all_references_resolved'],'schema_passed_parts':sum(c['valid'] for c in r['vsdx']['xsd_checks']),'schema_coverage_limits':1,'microsoft_visio_tested':False}
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'summary':r['summary'],'content_failures':[x for x in r['failures'] if x.get('classification')!='schema_coverage']},ensure_ascii=False))
assert r['summary']['native_vsdx_pass'] and r['summary']['native_vdx_pass'] and r['summary']['all_relationships_valid']
