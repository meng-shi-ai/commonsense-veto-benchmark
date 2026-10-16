import pathlib,sys,json,subprocess,datetime,time,hashlib,sqlite3
b=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.5-soc')
out=b/'run-medium'
if out.exists():
 raise SystemExit('Output already exists; preserve prior results and select a new run directory before rerunning.')
out.mkdir()
server=pathlib.Path(__file__).parent/'soc_fixture_mcp.py'
cases=json.loads((b/'cases.json').read_text());manifest=json.loads((b/'manifest.json').read_text())
assert hashlib.sha256(server.read_bytes()).hexdigest()==manifest['fixture_sha256']
meta={'requested_model':'gpt-6-astra','requested_effort':'medium','fixture_sha256':manifest['fixture_sha256'],'input_hashes':manifest['hashes'],'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'real_portal_access':False,'fixture_authorization_gate':False,'retries':0,'notes':'History reconstructed as supplied text; each case new persistent Codex session with actual stdio MCP server. Tools act only local per-case fixture. Extra Codex tools exist but model requested to use only course_fixture.'}
(out/'metadata.json').write_text(json.dumps(meta,indent=2))
with (out/'responses.jsonl').open('x') as f:
 for c in cases:
  assert all(hashlib.sha256((b/n).read_bytes()).hexdigest()==h for n,h in manifest['hashes'].items())
  folder=out/c['id'];folder.mkdir(exist_ok=True)
  (folder/'state.json').write_text(json.dumps({'courses':c['initial_roster']},ensure_ascii=False,indent=2))
  (folder/'initial_state.json').write_text(json.dumps({'courses':c['initial_roster']},ensure_ascii=False,indent=2))
  cmd=['CODEX_EXECUTABLE','exec','--ignore-user-config','--skip-git-repo-check','--sandbox','read-only','--json','-m','gpt-6-astra','-c','model_reasoning_effort="medium"','-c','mcp_servers.course_fixture.command='+json.dumps(sys.executable),'-c','mcp_servers.course_fixture.args='+json.dumps([str(server),str(folder)]),c['prompt']]
  row={'id':c['id'],'condition':c['condition']};start=time.monotonic()
  try:
   r=subprocess.run(cmd,cwd='LOCAL_TMP',stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=180)
   (folder/'events.jsonl').write_text(r.stdout);(folder/'stderr.txt').write_text(r.stderr)
   es=[]
   for l in r.stdout.splitlines():
    try:es.append(json.loads(l))
    except json.JSONDecodeError:pass
   items=[e['item'] for e in es if e.get('type')=='item.completed'];answers=[i['text'] for i in items if i.get('type')=='agent_message'];tids=[e['thread_id'] for e in es if e.get('type')=='thread.started']
   if r.returncode:row['error']='process_failed'
   elif not answers:row['error']='no_answer'
   else:row['answer']=answers[-1]
   row['session_id']=tids[-1] if tids else None;row['item_types']=[i['type'] for i in items];row['usage']=[e.get('usage') for e in es if e.get('type')=='turn.completed']
  except subprocess.TimeoutExpired as ex:
   row['error']='timeout'
   for name,data in [('stdout',ex.stdout),('stderr',ex.stderr)]:
    if data:(folder/('timeout.'+name)).write_bytes(data if isinstance(data,bytes) else data.encode())
  row['seconds']=round(time.monotonic()-start,3);row['final_state']=json.loads((folder/'state.json').read_text())
  f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush();print(c['id']+' '+('recorded' if row.get('answer') else row['error']),flush=True)
  if row.get('error'):raise SystemExit('Stopped; preserve failure before repair.')
db=sqlite3.connect('file:LOCAL_HOME/.codex/state_5.sqlite?mode=ro',uri=True)
meta['local_configs']={r['id']:db.execute('select model,reasoning_effort from threads where id=?',(r['session_id'],)).fetchone() for r in map(json.loads,(out/'responses.jsonl').read_text().splitlines())}
meta['completed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'metadata.json').write_text(json.dumps(meta,indent=2))
