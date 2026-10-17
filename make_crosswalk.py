import json,csv,collections
from pathlib import Path
b=Path('terragoat'); ck=json.load(open(b/'checkov_results.json',encoding='utf8')); tv=json.load(open(b/'trivy_results.json',encoding='utf8'))
# Manually reviewed mappings from Trivy control to Checkov policy by control meaning.
# Deliberately omit controls with no directly equivalent Checkov policy.
cross={
'AWS-0026':'CKV_AWS_3','AWS-0027':'CKV_AWS_189','AWS-0028':'CKV_AWS_79','AWS-0029':'CKV_AWS_46',
'AWS-0030':'CKV_AWS_163','AWS-0031':'CKV_AWS_51','AWS-0033':'CKV_AWS_136','AWS-0038':'CKV_AWS_37',
'AWS-0039':'CKV_AWS_58','AWS-0040':'CKV_AWS_39','AWS-0041':'CKV_AWS_38','AWS-0042':'CKV_AWS_84',
'AWS-0048':'CKV_AWS_5','AWS-0065':'CKV_AWS_7','AWS-0066':'CKV_AWS_50','AWS-0075':'CKV_AWS_101',
'AWS-0076':'CKV_AWS_44','AWS-0079':'CKV_AWS_96','AWS-0080':'CKV_AWS_16','AWS-0086':'CKV2_AWS_6',
'AWS-0087':'CKV2_AWS_6','AWS-0089':'CKV_AWS_18','AWS-0090':'CKV_AWS_21','AWS-0091':'CKV2_AWS_6',
'AWS-0093':'CKV2_AWS_6','AWS-0094':'CKV2_AWS_6','AWS-0099':'CKV_AWS_23','AWS-0104':'CKV_AWS_382',
'AWS-0107':'CKV_AWS_24','AWS-0124':'CKV_AWS_23','AWS-0126':'CKV_AWS_228','AWS-0128':'CKV_AWS_347',
'AWS-0131':'CKV_AWS_8','AWS-0132':'CKV_AWS_145','AWS-0164':'CKV_AWS_130','AWS-0176':'CKV_AWS_161',
'AWS-0177':'CKV_AWS_293','AWS-0178':'CKV2_AWS_11','AWS-0180':'CKV_AWS_17','AWS-0343':'CKV_AWS_139',
'AWS-0345':'CKV_AWS_355'}
C=[];T=[]
for g in ck:
 if g.get('check_type')!='terraform':continue
 for f in g.get('results',{}).get('failed_checks',[]):
  p=(f.get('repo_file_path')or f.get('file_path')or'').replace('\\','/')
  if p.endswith('.tf'):C.append(dict(file=Path(p).name,path=p,resource=f.get('resource',''),id=f.get('check_id',''),name=f.get('check_name',''),severity=f.get('severity',''),source='Checkov'))
for r in tv.get('Results',[]):
 if r.get('Type')!='terraform' or not r.get('Target','').endswith('.tf'):continue
 for f in r.get('Misconfigurations',[]):
  if f.get('Status')!='FAIL':continue
  T.append(dict(file=Path(r['Target']).name,path='/terraform/aws/'+r['Target'].replace('\\','/'),resource=(f.get('CauseMetadata')or{}).get('Resource',''),id=f.get('ID',''),name=f.get('Title',''),severity=f.get('Severity',''),source='Trivy'))
key=lambda x:(x['file'].lower(),x['resource'].lower(),x['id'])
ci=collections.defaultdict(list);ti=collections.defaultdict(list)
for x in C:ci[key(x)].append(x)
for x in T:ti[key(x)].append(x)
# group resource/policy records; preserve unmatched native IDs, aggregate repeated Trivy IDs mapped to one Checkov policy.
combined=collections.defaultdict(lambda:{'ck':[],'tv':[]})
for x in C:combined[(x['file'].lower(),x['resource'].lower(),'CK:'+x['id'])]['ck'].append(x)
for x in T:
 mapped=cross.get(x['id'])
 ident='CK:'+mapped if mapped else 'TV:'+x['id']
 combined[(x['file'].lower(),x['resource'].lower(),ident)]['tv'].append(x)
rows=[]
for (fl,res,ident),v in sorted(combined.items()):
 c=v['ck']; t=v['tv']; status='CONSENSUS' if c and t else ('CHECKOV ONLY' if c else 'TRIVY ONLY'); a=(c or t)[0]
 rows.append(dict(status=status,file=a['file'],path=a['path'],resource=a['resource'],canonical_check_id=ident[3:],checkov_ids=';'.join(sorted({x['id'] for x in c})),trivy_ids=';'.join(sorted({x['id'] for x in t})),checkov_names='; '.join(sorted({x['name'] for x in c})),trivy_names='; '.join(sorted({x['name'] for x in t})),checkov_occurrences=sum(len(x) for x in [c]),trivy_occurrences=sum(len(x) for x in [t])))
# full table and revised consensus, replacing mechanically normalized draft
fields=list(rows[0]);
for fn,rs in [('full_tool_comparison.csv',rows),('consensus_ground_truth.csv',[x for x in rows if x['status']=='CONSENSUS'])]:
 with open(b/fn,'w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
with open(b/'manual_policy_crosswalk.csv','w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['trivy_id','checkov_id','mapping_basis','status']);
 for tr,ckid in sorted(cross.items()):w.writerow([tr,ckid,'Manual semantic equivalence; resource-level pairing required','mapped'])
status=collections.Counter(x['status'] for x in rows); con=[x for x in rows if x['status']=='CONSENSUS']
# amend summary to document the adjudicated method and its limits
msg=f'''TERRAGOAT AWS TOOL COMPARISON SUMMARY\nCheckov Terraform findings (raw): {len(C)}\nTrivy Terraform findings (raw): {len(T)}\nManually crosswalked Trivy policy IDs: {len(cross)}\nUnique resource and canonical-policy groups: {len(rows)}\nManual semantic consensus groups: {len(con)}\nCheckov-only groups: {status['CHECKOV ONLY']}\nTrivy-only groups: {status['TRIVY ONLY']}\n\nStrict numeric ID normalization yielded zero matches because Trivy reports AWS-00xx Aqua IDs, not CKV_AWS IDs. The revised candidate ground truth uses the explicit mapping in manual_policy_crosswalk.csv, and requires the same filename and Terraform resource. Multiple Trivy controls mapping to one Checkov policy on one resource are grouped to prevent duplicate counting.\n\nThe crosswalk is analyst-adjudicated, not an independently validated expert gold standard. Ambiguous or non-equivalent controls were excluded from mapping and remain tool-only. Review this crosswalk with the supervisor or a second security reviewer before treating the file as final ground truth. This is not an LLM model evaluation and does not support GPT-4o, Claude, Gemini, precision/recall/F1, category-performance, or remediation-quality claims.\n'''
(b/'updated_summary_stats.txt').write_text(msg,encoding='utf8')
print('raw Checkov',len(C),'raw Trivy',len(T),'crosswalk IDs',len(cross),'consensus groups',len(con),'Checkov only',status['CHECKOV ONLY'],'Trivy only',status['TRIVY ONLY'])
