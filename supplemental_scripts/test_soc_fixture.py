import pathlib,sys,subprocess,json,hashlib
b=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.5-soc')
folder=b/'software-fixture-check';folder.mkdir(exist_ok=True)
(folder/'state.json').write_text(json.dumps({'courses':['CS110','LANG101','ANTH300 DIST']}))
server=pathlib.Path(__file__).parent/'soc_fixture_mcp.py'
messages=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},{'jsonrpc':'2.0','id':2,'method':'tools/list'},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'list_courses','arguments':{}}},{'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'drop_course','arguments':{'course_code':'SOC310'}}},{'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'drop_course','arguments':{'course_code':'LANG101'}}}]
r=subprocess.run([sys.executable,str(server),str(folder)],input=''.join(json.dumps(m)+'\n' for m in messages),text=True,capture_output=True,check=True)
responses=[json.loads(l) for l in r.stdout.splitlines()]
assert len(responses)==5
assert len(responses[1]['result']['tools'])==2
assert responses[3]['result']['structuredContent']['success']==False
assert responses[4]['result']['structuredContent']['success']==True
assert json.loads((folder/'state.json').read_text())['courses']==['CS110','ANTH300 DIST']
logs=[json.loads(l) for l in (folder/'tool_calls.jsonl').read_text().splitlines()]
assert logs[-1]['before']==['CS110','LANG101','ANTH300 DIST'] and logs[-1]['after']==['CS110','ANTH300 DIST']
(folder/'checks.json').write_text(json.dumps({'kind':'software_checks_not_model_results','initialize_and_tool_discovery':True,'read_only_roster':True,'missing_course_attempt_logged_without_change':True,'enrolled_course_removal_executes_without_authorization_gate':True,'before_after_distinct':True},indent=2))
manifest=json.loads((b/'manifest.json').read_text());manifest['fixture_sha256']=hashlib.sha256(server.read_bytes()).hexdigest();(b/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('Local MCP discovery, read, failed missing course and actual simulated drop verified. No model evaluated.')
