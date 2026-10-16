import pathlib,json,collections,hashlib,statistics
base=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.3-open')
cases=[json.loads(l) for l in (base/'cases.jsonl').read_text().splitlines()]
dims=['conclusion','applies_information','no_fabricated_certainty','no_unnecessary_question']
def aggregate(cs,rows,labels):
 result={'n':len(cs),'returned':0,'all_pass':0,'dimensions':dict.fromkeys(dims,0),'details':[]}
 for c in cs:
  cid=c['id'];r=rows.get(cid,{});a=labels.get(cid)
  valid=bool(r.get('answer')) and not r.get('error')
  if valid and a is None:raise ValueError('Missing review '+cid)
  if a:
   assert all(a[d] in [0,1] for d in dims)
   assert a.get('evidence') and a.get('note')
  marks={d:int(valid and a[d]==1) for d in dims}
  result['returned']+=int(valid);result['all_pass']+=int(all(marks.values()))
  for d in dims:result['dimensions'][d]+=marks[d]
  result['details'].append({'id':cid,'pass':all(marks.values()),'dimensions':marks,'error':r.get('error')})
 return result
# Fail-closed denominator checks; these are software tests, never model results.
fixture={'id':'fixture'}
mark={**dict.fromkeys(dims,1),'note':'fixture','evidence':'fixture'}
assert aggregate([fixture],{}, {})['all_pass']==0
assert aggregate([fixture],{'fixture':{'answer':'ok'}},{'fixture':mark})['all_pass']==1
bad={**mark,'applies_information':0}
assert aggregate([fixture],{'fixture':{'answer':'ok'}},{'fixture':bad})['all_pass']==0
report={'reviewer':'AI-assisted semantic review; not independent human validation','runs':{}}
for effort in ['medium','high']:
 rows={r['id']:r for r in map(json.loads,(base/('run-'+effort)/'responses.jsonl').read_text().splitlines())}
 review=json.loads((base/('review-'+effort+'.json')).read_text())
 assert set(rows)=={c['id'] for c in cases}
 groups={'all':cases}
 for module in ['length_update','weather_time','relative_week']:groups[module]=[c for c in cases if c['module']==module]
 for length in ['short','long']:
  for update in ['retained','changed']:
   groups[length+'_'+update]=[c for c in cases if c['module']=='length_update' and c['condition']['length']==length and c['condition']['update']==update]
 result={name:aggregate(cs,rows,review) for name,cs in groups.items()}
 result['usage']={'total_seconds':round(sum(r['seconds'] for r in rows.values()),3),'median_seconds':round(statistics.median(r['seconds'] for r in rows.values()),3),'input_tokens':sum(u.get('input_tokens',0) for r in rows.values() for u in r.get('usage',[]) if u),'output_tokens':sum(u.get('output_tokens',0) for r in rows.values() for u in r.get('usage',[]) if u),'reasoning_output_tokens':sum(u.get('reasoning_output_tokens',0) for r in rows.values() for u in r.get('usage',[]) if u)}
 report['runs'][effort]=result
 for n,h in json.loads((base/('run-'+effort)/'metadata.json').read_text())['hashes'].items():assert hashlib.sha256((base/n).read_bytes()).hexdigest()==h
 lines=['# '+effort+'逐题回答与AI辅助评分','', '评分不是独立人工验证。保留原始回答，供复核。','']
 for c in cases:
  r=rows[c['id']];a=review[c['id']]
  lines+=['## '+c['id'],'','最终问题：'+c['question'],'','模型原文：','',r.get('answer',str(r.get('error'))),'','评分：'+str({d:a[d] for d in dims}),'','判分依据：'+a['note'],'']
 (base/('逐题结果-'+effort+'.md')).write_text('\n'.join(lines))
(base/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({e:{'all':r['all']['all_pass'],'n':r['all']['n'],'usage':r['usage']} for e,r in report['runs'].items()},indent=2))
