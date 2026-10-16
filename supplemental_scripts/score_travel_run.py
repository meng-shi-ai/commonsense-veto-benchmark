import pathlib,json,sys,hashlib,datetime,collections
base=pathlib.Path('PUBLIC_REPO_ROOT/outputs')
dataset=base/'memory-benchmark-v0.2-travel'
run=base/'gpt-pilot-v0.2-travel-run02'
sys.path.insert(0,str(dataset))
import benchmark as b
cases,gold=b.inputs();rows=b.read_jsonl(run/'predictions.jsonl')
assert len(rows)==32
reports={}
for name,cs in [('all_32',cases),('original_24',cases[:24]),('travel_8',cases[24:])]:
 ids={c['id'] for c in cs}
 report=b.score(cs,gold,[r for r in rows if r['id'] in ids])
 report['group']=name
 report['dataset_sha256']=hashlib.sha256((dataset/'cases.jsonl').read_bytes()).hexdigest()
 (run/(name+'_report.json')).write_text(json.dumps(report,indent=2))
 reports[name]=report
events=[json.loads(l) for f in run.glob('C*.events.jsonl') for l in f.read_text().splitlines() if l.startswith('{')]
types=collections.Counter(e['item']['type'] for e in events if e.get('type')=='item.completed')
meta=json.loads((run/'run_metadata.json').read_text())
meta.update(completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),reasoning_effort='not explicitly set; effective value unknown',sampling='not explicitly set',resolved_model_snapshot='not exposed by captured events',prior_failed_attempt='gpt-pilot-v0.2-travel: first case failed at local process startup; no model response; retained separately',completed_turns=sum(e.get('type')=='turn.completed' for e in events),completed_item_types=dict(types))
(run/'run_metadata.json').write_text(json.dumps(meta,indent=2))
shutil=None
manifest=json.loads((dataset/'manifest.json').read_text())
manifest['actual_models_evaluated_on_extension']=[{'requested_model':'gpt-6-astra','route':'Codex CLI / ChatGPT login','result_directory':'../gpt-pilot-v0.2-travel-run02','reasoning_effort':'default; effective value unknown'}]
manifest['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dataset.iterdir() if p.is_file() and p.name!='manifest.json'}
(dataset/'manifest.json').write_text(json.dumps(manifest,indent=2))
failures=[]
for r in rows:
 d=next(d for d in reports['all_32']['details'] if d['id']==r['id'])
 if not d['strict_pass']:failures.append({'id':r['id'],'prediction':r.get('prediction'),'gold':gold[r['id']],'state_correct':d['state_correct']})
(run/'discrepancies.json').write_text(json.dumps(failures,indent=2))
print(json.dumps({'groups':{k:{f:v[f] for f in ['n','state_accuracy','strict_accuracy','pair_strict_accuracy','schema_valid_rate']} for k,v in reports.items()},'discrepancies':failures,'completed_item_types':dict(types)},indent=2))
