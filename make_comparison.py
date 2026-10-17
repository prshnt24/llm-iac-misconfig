import json,csv,re
from pathlib import Path
from collections import Counter,defaultdict
base=Path('terragoat'); ck=json.load(open(base/'checkov_results.json',encoding='utf8')); tv=json.load(open(base/'trivy_results.json',encoding='utf8'))
def nt(s):
 s=(s or '').strip().upper(); m=re.fullmatch(r'AVD-AWS-0*(\d+)',s); return 'CKV_AWS_'+str(int(m.group(1))) if m else s
C=[]; T=[]
for g in ck:
 if g.get('check_type')!='terraform': continue
 for f in g.get('results',{}).get('failed_checks',[]):
  p=(f.get('repo_file_path') or f.get('file_path') or '').replace('\\','/')
  if p.lower().endswith('.tf'): C.append(dict(tool='Checkov',file=Path(p).name,path=p,resource=f.get('resource',''),check_id=f.get('check_id',''),normalized_id=(f.get('check_id') or '').upper(),check_name=f.get('check_name',''),severity=f.get('severity',''),source_id=f.get('bc_check_id','')))
for r in tv.get('Results',[]):
 if r.get('Type')!='terraform': continue
 p=(r.get('Target') or '').replace('\\','/')
 if not p.lower().endswith('.tf'): continue
 for m in r.get('Misconfigurations',[]):
  if m.get('Status')=='FAIL': T.append(dict(tool='Trivy',file=Path(p).name,path='/terraform/aws/'+p,resource=(m.get('CauseMetadata') or {}).get('Resource',''),check_id=m.get('ID',''),normalized_id=nt(m.get('ID')),check_name=m.get('Title',''),severity=m.get('Severity',''),source_id=m.get('Namespace','')))
key=lambda x:(x['file'].lower(),x['resource'].lower(),x['normalized_id']); ci=defaultdict(list); ti=defaultdict(list)
for x in C:ci[key(x)].append(x)
for x in T:ti[key(x)].append(x)
rows=[]
for k in sorted(set(ci)|set(ti)):
 s='CONSENSUS' if k in ci and k in ti else ('CHECKOV ONLY' if k in ci else 'TRIVY ONLY'); a=(ci.get(k) or ti.get(k))[0]
 rows.append(dict(status=s,file=a['file'],path=a['path'],resource=a['resource'],normalized_id=a['normalized_id'],checkov_id=';'.join(sorted({x['check_id'] for x in ci.get(k,[])})),trivy_id=';'.join(sorted({x['check_id'] for x in ti.get(k,[])})),checkov_name='; '.join(sorted({x['check_name'] for x in ci.get(k,[])})),trivy_name='; '.join(sorted({x['check_name'] for x in ti.get(k,[])})),checkov_count=len(ci.get(k,[])),trivy_count=len(ti.get(k,[]))))
fields=list(rows[0]);
for name,subset in [('full_tool_comparison.csv',rows),('consensus_ground_truth.csv',[r for r in rows if r['status']=='CONSENSUS'])]:
 with open(base/name,'w',newline='',encoding='utf-8-sig') as f: w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(subset)
counts=Counter(r['status'] for r in rows)
files=sorted({x['file'] for x in C+T})
bf=[]
for fn in files: bf.append(dict(file=fn,Checkov=sum(x['file']==fn for x in C),Trivy=sum(x['file']==fn for x in T),Consensus=sum(r['file']==fn and r['status']=='CONSENSUS' for r in rows)))
def chart_html(title, labels, series):
    w,h=1300,640; ml,mr,mt,mb=200,50,75,110; plotw=w-ml-mr; ploth=h-mt-mb
    maxv=max([v for _,vals,_ in series for v in vals]+[1]); group=len(labels); sw=len(series); gw=plotw/group; barh=min(24,gw/(sw+1))
    colors=[color for _,_,color in series]; svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/><text x="{w/2}" y="38" text-anchor="middle" font-size="26" font-family="Arial">{title}</text>']
    for tick in range(6):
        val=maxv*tick/5; y=mt+ploth-tick*ploth/5; svg.append(f'<line x1="{ml}" y1="{y}" x2="{w-mr}" y2="{y}" stroke="#ddd"/><text x="{ml-15}" y="{y+5}" text-anchor="end" font-size="14" font-family="Arial">{val:.0f}</text>')
    for gi,label in enumerate(labels):
        center=ml+gw*(gi+.5)
        for si,(name,vals,color) in enumerate(series):
            v=vals[gi]; bh=barh*.72; y=mt+ploth-(v/maxv*ploth)+(si-(sw-1)/2)*barh
            svg.append(f'<rect x="{center-gw*.36}" y="{y}" width="{v/maxv*plotw}" height="{bh}" fill="{color}"/><text x="{center-gw*.36+v/maxv*plotw+5}" y="{y+bh-3}" font-size="13" font-family="Arial">{v}</text>')
        svg.append(f'<text x="{ml-12}" y="{center+5}" text-anchor="end" font-size="13" font-family="Arial">{label}</text>')
    for i,(name,vals,color) in enumerate(series): svg.append(f'<rect x="{ml+i*170}" y="{h-42}" width="18" height="18" fill="{color}"/><text x="{ml+25+i*170}" y="{h-27}" font-size="14" font-family="Arial">{name}</text>')
    svg.append('</svg>'); return ''.join(svg)
def htmlwrite(name,svg): (base/name).write_text('<!doctype html><meta charset="utf-8"><title>'+name+'</title><div style="max-width:1400px;margin:auto">'+svg+'</div>',encoding='utf-8')
svg=chart_html('Terraform AWS Findings: Checkov, Trivy, and Strict ID Consensus',['All findings'],[('Checkov',[len(C)],'#3977b8'),('Trivy',[len(T)],'#d95f59'),('Consensus',[counts['CONSENSUS']],'#3b9b70')]); htmlwrite('chart_consensus_comparison.html',svg)
series=[(n,[r[n] for r in bf],c) for n,c in [('Checkov','#3977b8'),('Trivy','#d95f59'),('Consensus','#3b9b70')]]
svg=chart_html('Terraform Findings by File',[x['file'] for x in bf],series); htmlwrite('chart_consensus_by_file.html',svg)
# Pipeline SVG rendered as PNG by the Windows GDI+ step in the calling shell.
boxes=[('1. Dataset Collection','TerraGoat: 14 files\nGitHub: 100?200 repos\nRegistry: 30?50 modules'),('2. Ground Truth','Checkov v3.3.9 + Trivy\nRetain agreed findings'),('3. LLM Evaluation','GPT-4o, Claude Sonnet 4.6,\nGemini 2.5 Pro\nZero-shot and few-shot'),('4. Response Parsing','Policy ID mapping table\nUnmapped issues = false positives'),('5. Metric Calculation','Precision, recall, F1\nRemediation rubric (0?2)')]
W,H=2000,600; parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><text x="60" y="65" font-family="Arial" font-size="38" fill="#18324a">Figure 3.1. Evaluation Pipeline</text>']; colors=['#e9f2fb','#e9f6ef','#fff4df','#f4edfb','#e9f5f5']
for i,(head,body) in enumerate(boxes):
 x=35+i*400; y=155; parts.append(f'<rect x="{x}" y="{y}" width="345" height="300" rx="22" fill="{colors[i]}" stroke="#31536f" stroke-width="3"/><text x="{x+18}" y="{y+50}" font-family="Arial" font-size="22" fill="#17354d">{head}</text>')
 for j,line in enumerate(body.split('\n')): parts.append(f'<text x="{x+18}" y="{y+115+j*42}" font-family="Arial" font-size="20" fill="#263746">{line}</text>')
 if i<4: parts.append(f'<line x1="{x+350}" y1="305" x2="{x+390}" y2="305" stroke="#31536f" stroke-width="8"/><polygon points="{x+390},305 {x+370},290 {x+370},320" fill="#31536f"/>')
parts.append('</svg>'); (base/'figure_3_1_methodology_pipeline.svg').write_text(''.join(parts),encoding='utf-8')
print('Checkov Terraform findings',len(C),'Trivy Terraform findings',len(T),'consensus',counts['CONSENSUS'],'Checkov only',counts['CHECKOV ONLY'],'Trivy only',counts['TRIVY ONLY'],'files',len(files))
