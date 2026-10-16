import pathlib,json,subprocess,hashlib,datetime,time,sqlite3,sys
b=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.4-friction')
out=b/'run-medium';out.mkdir(exist_ok=True)
nodes=json.loads((b/'nodes.json').read_text());frozen=json.loads((b/'manifest.json').read_text())['hashes'];sessions={}
if len(sys.argv)>2:
 sessions={r['id']:r['session_id'] for r in map(json.loads,pathlib.Path(sys.argv[2]).read_text().splitlines()) if r.get('session_id')}
meta={'requested_model':'gpt-6-astra','requested_effort':'medium','cli':'0.153.4','hashes':frozen,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'Persistent Codex conversations with resume and fork; actual generated prior responses preserved. Fictional time jumps, no real waiting for days.','extra_context':'Codex harness remains present; no tool use or web access in evaluated conversation. Labels withheld.','retry_policy':'no automatic retries; stop on any operational failure','temperature':'not specified','output_limit':'not specified'}
(out/'metadata.json').write_text(json.dumps(meta,indent=2))
with (out/'responses.jsonl').open('x') as f:
 for n in nodes:
  assert all(hashlib.sha256((b/k).read_bytes()).hexdigest()==h for k,h in frozen.items())
  cmd=['CODEX_EXECUTABLE','exec','--ignore-user-config','--skip-git-repo-check','--sandbox','read-only','--json','-m','gpt-6-astra','-c','model_reasoning_effort="medium"']
  if n['mode']!='new':cmd+=[n['mode'],sessions[n['parent']]]
  cmd.append(n['prompt']);rout={'id':n['id'],'mode':n['mode'],'parent':n['parent']};start=time.monotonic()
  try:
   r=subprocess.run(cmd,cwd='LOCAL_TMP',stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=240)
   (out/(n['id']+'.events.jsonl')).write_text(r.stdout);(out/(n['id']+'.stderr.txt')).write_text(r.stderr)
   es=[]
   for l in r.stdout.splitlines():
    try:es.append(json.loads(l))
    except json.JSONDecodeError:pass
   its=[e['item'] for e in es if e.get('type')=='item.completed'];texts=[i['text'] for i in its if i.get('type')=='agent_message']
   tids=[e['thread_id'] for e in es if e.get('type')=='thread.started']
   if r.returncode:rout['error']='process_failed'
   elif any(i.get('type') not in ('agent_message','reasoning') for i in its):rout['error']='tool_use_violation'
   elif not texts or not tids:rout['error']='missing_output_or_session'
   else:rout.update(answer=texts[-1],session_id=tids[-1]);sessions[n['id']]=tids[-1]
   rout['usage']=[e.get('usage') for e in es if e.get('type')=='turn.completed']
  except subprocess.TimeoutExpired as exc:
   rout['error']='timeout'
   for label,data in [('stdout',exc.stdout),('stderr',exc.stderr)]:
    if data:(out/(n['id']+'.timeout.'+label)).write_bytes(data if isinstance(data,bytes) else data.encode())
  rout['seconds']=round(time.monotonic()-start,3)
  f.write(json.dumps(rout,ensure_ascii=False)+'\n');f.flush()
  print(n['id']+' '+('recorded' if 'answer' in rout else rout['error']),flush=True)
  if rout.get('error'):raise SystemExit('Stopped; preserve this attempt before repair.')
meta['completed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
db=sqlite3.connect('file:LOCAL_HOME/.codex/state_5.sqlite?mode=ro',uri=True)
meta['local_session_config']={nid:db.execute('select model,reasoning_effort from threads where id=?',(tid,)).fetchone() for nid,tid in sessions.items()}
meta['config_note']='Local stored configuration, where available, is not independent confirmation of server snapshot or internal compute budget.'
(out/'metadata.json').write_text(json.dumps(meta,indent=2))
