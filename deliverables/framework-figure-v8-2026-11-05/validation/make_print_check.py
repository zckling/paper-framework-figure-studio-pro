from pathlib import Path
from collections import defaultdict
from lxml import etree
import json,subprocess,fitz

root=Path(__file__).resolve().parent.parent
scene=json.loads((root/'framework-editable.scene.json').read_text())
scale=180/scene['width']*72/25.4
main_ids=set('overview-title adaptation-title source-support-title support-budget trainable-P-label support-fit-encoder-title support-fit-encoder-blocks native-logits-title support-ce-label save-prompts-label support-cache-encoder-title support-cache-encoder-blocks support-cls-normalize-label support-cache-title query-protocol query-source-title query-prototype-encoder-title query-prototype-encoder-blocks query-cls-normalize-label query-q-symbol prototype-method-title prototype-probability fixed-prompt-inference-state load-prompts-label query-prompted-encoder-title query-prompted-encoder-blocks query-v-symbol cosine-difference-title visual-probability probability-average-title decision-rule prototype-detail-title weighting-header aggregation-header mix-header l2-norm-label-0 l2-norm-label-1 prompt-detail-title stage-label-1 stage-label-2 stage-label-3 stage-label-4 clip-readout-label'.split())
groups=defaultdict(list)
for s in scene['objects']:
 if s['kind']=='text':groups[s['name'].rsplit('-run-',1)[0]].append(s)
rows=[];index_runs=[]
for name,objs in groups.items():
 fs=max(s['fs'] for s in objs)
 is_main=name in main_ids
 for s in objs:
  if '-run-' in s['name'] and s['fs']<fs*.9:index_runs.append({'name':s['name'],'text':s['value'],'font_pt':round(s['fs']*scale,3)})
 rows.append({'name':name,'text':''.join(s['value'] for s in objs),'role':'main' if is_main else 'auxiliary','font_canvas':fs,'font_pt':round(fs*scale,3),'minimum_pt':8 if is_main else 7,'pass':fs*scale+1e-5 >= (8 if is_main else 7)})
svg=etree.parse(str(root/'framework-v8.svg'))
svg.getroot().set('width','180mm');svg.getroot().set('height',f"{scene['height']/scene['width']*180}mm")
svgpath=root/'validation/print-180mm.svg';svg.write(str(svgpath),xml_declaration=True,encoding='UTF-8')
subprocess.run(['inkscape',str(svgpath),'--export-filename='+str(root/'validation/print-180mm.pdf')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
d=fitz.open(root/'validation/print-180mm.pdf');page=d[0]
page.get_pixmap(dpi=300).save(str(root/'validation/print-180mm-300dpi.png'))
main=[x for x in rows if x['role']=='main'];aux=[x for x in rows if x['role']=='auxiliary']
r={'width_mm':round(page.rect.width*25.4/72,4),'height_mm':round(page.rect.height*25.4/72,4),'scale_pt_per_canvas_unit':scale,'formula':'font_pt=canvas_font×(180/width_canvas)×72/25.4','main_label_count':len(main),'main_min_pt':min(x['font_pt'] for x in main),'main_max_pt':max(x['font_pt'] for x in main),'auxiliary_label_count':len(aux),'auxiliary_min_pt':min(x['font_pt'] for x in aux),'main_check_pass':all(x['pass'] for x in main),'auxiliary_check_pass':all(x['pass'] for x in aux),'mathematical_indices_use_natural_smaller_type':index_runs,'all_labels':rows,'notes':['All base-size ordinary labels are checked, not just a selected subset. Mathematical subscripts keep their natural reduced size.','The physical-width PDF is180mm wide; raster pixel count is not a substitute for the physical type-size calculation.','Visual spacing and native import are checked separately; no claim of Microsoft Visio testing.']}
(root/'validation/print-180mm-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
lines=['# 180 mm 版面字号检查','',f"物理PDF：{r['width_mm']} × {r['height_mm']} mm。",'',f"主要标签{len(main)}组：{r['main_min_pt']}–{r['main_max_pt']} pt；辅助标签{len(aux)}组：最小{r['auxiliary_min_pt']} pt。",'',f"主要标签≥8pt：{r['main_check_pass']}；辅助基字号≥7pt：{r['auxiliary_check_pass']}。",'','数学下标保留自然缩小，未把下标字号当作独立辅助正文。所有普通文字基字号均纳入检查。','', '| 标签 | 类型 | 180 mm 字号 | 结果 |','|---|---|---:|---|']
for x in rows:lines.append(f"| {x['text'].replace(chr(10),'<br>')} | {x['role']} | {x['font_pt']} pt | {'PASS' if x['pass'] else 'FAIL'} |")
(root/'validation/print-180mm-check.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:r[k] for k in ['width_mm','height_mm','main_label_count','main_min_pt','main_max_pt','auxiliary_label_count','auxiliary_min_pt','main_check_pass','auxiliary_check_pass']}))
assert r['main_check_pass'] and r['auxiliary_check_pass']
