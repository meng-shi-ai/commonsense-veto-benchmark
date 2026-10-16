import json, subprocess, pathlib, hashlib, datetime, sys
src=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('PUBLIC_REPO_ROOT/memory_benchmark_v01')
out=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else pathlib.Path('PUBLIC_REPO_ROOT/outputs/gpt-pilot')
out.mkdir(parents=True, exist_ok=True)
model='gpt-6-astra'
prompts=[json.loads(x) for x in (src/'prompts.jsonl').read_text().splitlines() if x.strip()]
meta={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requested_model':model,'provider_route':'Codex CLI with ChatGPT login','cli_version':'0.153.4','condition':'Fresh ephemeral Codex session per case; Codex harness adds instructions. Not a bare API evaluation. No external memory intentionally supplied. Tools prohibited in request; tool events flagged.','retries':0,'cases_sha256':hashlib.sha256((src/'cases.jsonl').read_bytes()).hexdigest(),'prompts_sha256':hashlib.sha256((src/'prompts.jsonl').read_bytes()).hexdigest()}
(out/'run_metadata.json').write_text(json.dumps(meta,indent=2))
with (out/'predictions.jsonl').open('x') as f:
 for p in prompts:
  instruction='Answer this benchmark item. Do not use tools or read files. Return only the requested JSON object.\n\n'+'\n\n'.join(m['content'] for m in p['messages'])
  cmd=['CODEX_EXECUTABLE','exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','--sandbox','read-only','--json','-m',model,instruction]
  row={'id':p['id']}
  try:
   r=subprocess.run(cmd,cwd='LOCAL_TMP',stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=150)
   (out/(p['id']+'.events.jsonl')).write_text(r.stdout)
   (out/(p['id']+'.stderr.txt')).write_text(r.stderr)
   events=[]
   for line in r.stdout.splitlines():
    try: events.append(json.loads(line))
    except json.JSONDecodeError: pass
   items=[e['item'] for e in events if e.get('type')=='item.completed']
   tool_used=any(i.get('type') not in ('agent_message','reasoning') for i in items)
   answers=[i['text'] for i in items if i.get('type')=='agent_message']
   if r.returncode: row['error']='process_failed'
   elif tool_used: row['error']='tool_use_protocol_violation'
   elif not answers: row['error']='no_answer'
   else:
    try: row['prediction']=json.loads(answers[-1])
    except json.JSONDecodeError: row['error']='invalid_json'
  except subprocess.TimeoutExpired: row['error']='timeout'
  f.write(json.dumps(row)+'\n');f.flush()
  print(p['id']+': '+('recorded' if 'prediction' in row else row['error']),flush=True)
  if 'prediction' not in row:
   print('Stopped on first operational failure to inspect before continuing.',flush=True)
   break
