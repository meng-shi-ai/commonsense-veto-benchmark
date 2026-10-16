import pathlib,json,subprocess,datetime,hashlib,time
base=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.3-open')
prompts=[json.loads(l) for l in (base/'prompts.jsonl').read_text().splitlines()]
frozen={n:hashlib.sha256((base/n).read_bytes()).hexdigest() for n in ['cases.jsonl','prompts.jsonl','rubric.json']}
for effort in ['medium','high']:
 out=base/('run-'+effort);out.mkdir(exist_ok=True)
 meta={'requested_model':'gpt-6-astra','requested_reasoning_effort':effort,'effort_config_key':'model_reasoning_effort','effective_server_effort':'not independently exposed in captured JSON events','resolved_snapshot':'not exposed','cli_version':'0.153.4','hashes':frozen,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'automatic_retries':0,'context':'Each case is a fresh ephemeral Codex session containing a replayed conversation record; not live turn-by-turn interaction. Extra Codex harness instructions present. No tool use allowed. No labels supplied.','temperature':'not set','max_output_tokens':'not set','order':'same seeded order in both effort runs; all medium then all high'}
 (out/'metadata.json').write_text(json.dumps(meta,indent=2))
 with (out/'responses.jsonl').open('x') as f:
  for p in prompts:
   assert all(hashlib.sha256((base/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
   prompt='\n\n'.join(m['content'] for m in p['messages'])
   cmd=['CODEX_EXECUTABLE','exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','--sandbox','read-only','--json','-m','gpt-6-astra','-c',f'model_reasoning_effort="{effort}"',prompt]
   row={'id':p['id'],'effort':effort};started=time.monotonic()
   try:
    r=subprocess.run(cmd,cwd='LOCAL_TMP',stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=240)
    (out/(p['id']+'.events.jsonl')).write_text(r.stdout)
    (out/(p['id']+'.stderr.txt')).write_text(r.stderr)
    events=[]
    for line in r.stdout.splitlines():
     try:events.append(json.loads(line))
     except json.JSONDecodeError:pass
    its=[e['item'] for e in events if e.get('type')=='item.completed']
    answers=[i['text'] for i in its if i.get('type')=='agent_message']
    if r.returncode:row['error']='process_failed'
    elif any(i.get('type') not in ('agent_message','reasoning') for i in its):row['error']='tool_use_violation'
    elif not answers:row['error']='no_answer'
    else:row['answer']=answers[-1]
    row['usage']=[e.get('usage') for e in events if e.get('type')=='turn.completed']
   except subprocess.TimeoutExpired as ex:
    row['error']='timeout'
    for field,data in [('stdout',ex.stdout),('stderr',ex.stderr)]:
     if data:(out/(p['id']+'.timeout.'+field)).write_bytes(data if isinstance(data,bytes) else data.encode())
   row['seconds']=round(time.monotonic()-started,3)
   f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush()
   print(effort+' '+p['id']+' '+('recorded' if 'answer' in row else row['error']),flush=True)
   if row.get('error')=='process_failed':raise SystemExit('Stopped for operational diagnosis; saved attempt must not be overwritten.')
 meta['completed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (out/'metadata.json').write_text(json.dumps(meta,indent=2))
