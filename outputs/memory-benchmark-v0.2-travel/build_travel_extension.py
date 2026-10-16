import pathlib, json, shutil, hashlib, subprocess, sys
source=pathlib.Path('PUBLIC_REPO_ROOT/memory_benchmark_v01')
dest=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.2-travel')
dest.mkdir(parents=True,exist_ok=True)
for name in ['benchmark.py','test_benchmark.py','adapter_http.py','fixture_adapter.py']:
 shutil.copy2(source/name,dest/name)
test=(dest/'test_benchmark.py').read_text().replace('23/24','(len(self.cases)-1)/len(self.cases)').replace('1/24','1/len(self.cases)').replace('11/12','(len({g["pair_id"] for g in self.gold.values()})-1)/len({g["pair_id"] for g in self.gold.values()})').replace('6/24','sum(g["decision"]=="clarify" for g in self.gold.values())/len(self.cases)')
(dest/'test_benchmark.py').write_text(test)
(dest/'validation.txt').write_text('Validation of versioned extension; no real model requests.\n')
cases=[json.loads(x) for x in (source/'cases.jsonl').read_text().splitlines()]
gold=[json.loads(x) for x in (source/'gold.jsonl').read_text().splitlines()]
def ev(i,text,speaker='user'):
 return dict(id='E'+str(i),date='2026-09-05',speaker=speaker,text=text)
def pair(start,family,events,change,query,choices,labels,evidence,note):
 for v in range(2):
  es=[dict(e) for e in events]
  if v: es[change[0]]['text']=change[1]
  cid='C%03d'%(start+v)
  cases.append(dict(id=cid,as_of='2026-09-05',events=es,query=query,allowed_values=choices))
  gold.append(dict(id=cid,pair_id='P%02d'%((start+1)//2),family=family,split='pilot',variant=v,decision='answer',value=labels[v],evidence_sets=evidence[v],annotation_note=note[v]))
pair(25,'travel_constraint_application',[
 ev(1,'For this hotel search, my budget limit is 150 units per night. I require a dry room and no reported insect problem. A damp room is unacceptable even if cheap and central.'),
 ev(2,'Fictional Hotel A costs 120 units, is central, and has a verified damp room for these dates. Fictional Hotel B costs 140 units, is central, and has a verified dry room. Both have verified satisfactory insect checks for these dates. These are stipulated simulation facts, not real hotel reviews.','tool'),
 ev(3,'I want to visit a museum.'),ev(4,'The fictional museum closes at five.','assistant'),
 ev(5,'Keep the dry-room requirement. Choose the cheapest hotel that meets all my requirements.')],
 (4,'I now explicitly drop the dry-room requirement and accept a damp room. Keep the budget and insect requirements. Choose the cheapest hotel that meets my remaining requirements.'),
 'Which hotel should the assistant recommend under the currently applicable requirements?',
 ['hotel_a','hotel_b'],['hotel_b','hotel_a'],[[['E1','E2','E5']],[['E1','E2','E5']]],
 ['Price and location cannot override the retained dry-room requirement.','Explicit user relaxation changes the admissible hotel; merely preserving the old preference would be wrong.'])
pair(27,'travel_constraint_application',[
 ev(1,'I require a dry hotel room, no reported insect problem, and a price below 150 units. Do not present a property as meeting these requirements without supporting information.'),
 ev(2,'Fictional Hotel C costs 130 units and is central. Its insect check is satisfactory. There is no current information about room dampness.','tool'),
 ev(3,'Also remind me to pack a charger.'),ev(4,'Packing note: charger.','assistant'),ev(5,'Now return to the hotel recommendation.')],
 (1,'Fictional Hotel C costs 130 units and is central. Its insect check is satisfactory. A current room-specific inspection confirms that the offered room is dry.'),
 'Which next recommendation is justified: recommend C as meeting the listed requirements, or state that dryness is unverified and obtain evidence before endorsing it?',
 ['recommend_c_with_supported_fit','verify_dryness_before_endorsement'],['verify_dryness_before_endorsement','recommend_c_with_supported_fit'],
 [[['E1','E2']],[['E1','E2']]],['The correct answer is a verification action, not an unsupported hotel endorsement.','With the missing property verified, repeating the same request for verification is unnecessary.'])
pair(29,'travel_weather_application',[
 ev(1,'Plan a trip from fictional Station Q to fictional Mall R. Minimize cost, but I require a route that avoids outdoor exposure during rain.'),
 ev(2,'Route A costs 2 units and includes 15 minutes uncovered outdoors. Route B costs 5 units and is entirely sheltered. Both are operating normally according to this simulation. No comparative personal-safety information is available.','tool'),
 ev(3,'It is raining here now.'),ev(4,'The mall has a bookstore.'),ev(5,'A bookstore visit can fit after lunch.','assistant'),
 ev(6,'Update just before departure: it is still raining.'),ev(7,'Which route should I take now?')],
 (5,'Update just before departure: the rain has stopped and it is dry outside now.'),
 'Which route should be recommended under the stated rain-exposure rule and cost preference, using the latest departure update?',
 ['route_a','route_b'],['route_b','route_a'],[[['E1','E2','E6']],[['E1','E2','E6']]],
 ['Rain remains applicable despite intervening unrelated turns.','The explicit current dry-weather update changes the cost-minimizing admissible route.'])
pair(31,'travel_weather_application',[
 ev(1,'For departure today, I prefer the cheaper route, but I will not accept uncovered walking if rain is occurring. If current weather is unknown, verify it before making an unconditional route choice.'),
 ev(2,'Fictional route A costs 2 units with uncovered walking. Fictional route B costs 5 units and is fully sheltered. Both operate normally; there is no evidence that either has greater personal-security risk.','tool'),
 ev(3,'It rained here yesterday.'),ev(4,'Please include a coffee stop.'),ev(5,'We can discuss coffee after choosing transport.','assistant'),
 ev(6,'I have no current weather information at departure.')],
 (5,'At departure I can directly observe that it is raining here now.'),
 'What should the assistant do next under the explicit user decision rule: verify current weather before an unconditional choice, or recommend sheltered B based on current rain?',
 ['verify_current_weather','recommend_sheltered_b'],['verify_current_weather','recommend_sheltered_b'],[[['E1','E6']],[['E1','E2','E6']]],
 ['Yesterday\'s rain is not evidence of current rain; verification is an answerable next-action decision.','Current observed rain supports the sheltered route without another weather query.'])
for name,rows in [('cases.jsonl',cases),('gold.jsonl',gold)]:
 (dest/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
(dest/'extension_cases.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in cases[24:]))
for command in [['benchmark.py','validate'],['-m','unittest','-v'],['benchmark.py','export','--out','prompts.jsonl'],['benchmark.py','demo','--out','software_fixture_report.json']]:
 r=subprocess.run([sys.executable,'-B']+command,cwd=dest,text=True,capture_output=True)
 with (dest/'validation.txt').open('a') as f:f.write(str(command)+'\n'+r.stdout+r.stderr+'\n')
 if r.returncode: raise RuntimeError(r.stderr)
sys.path.insert(0,str(dest))
import benchmark as b
ci,gi=b.inputs()
assert ci[:24]==[json.loads(x) for x in (source/'cases.jsonl').read_text().splitlines()]
assert list(gi.values())[:24]==[json.loads(x) for x in (source/'gold.jsonl').read_text().splitlines()]
ext=ci[24:]
perfect=[dict(id=c['id'],prediction=dict(decision=gi[c['id']]['decision'],value=gi[c['id']]['value'],evidence_ids=gi[c['id']]['evidence_sets'][0])) for c in ext]
assert b.score(ext,gi,perfect)['strict_accuracy']==1
# A policy that ignores the single changed fact and repeats the first answer
# in each pair must fail exactly half of the extension and every full pair.
import copy
stale=copy.deepcopy(perfect)
for i in range(1,len(stale),2):stale[i]['prediction']=copy.deepcopy(stale[i-1]['prediction'])
score=b.score(ext,gi,stale)
assert score['state_accuracy']==0.5 and score['pair_strict_accuracy']==0
(dest/'extension_fixture_checks.json').write_text(json.dumps({'kind':'SOFTWARE_FIXTURES_NOT_MODEL_RESULTS','original_24_cases_and_labels_preserved':True,'extension_perfect_fixture_strict_accuracy':1,'unchanged_response_fixture_state_accuracy':score['state_accuracy'],'unchanged_response_fixture_pair_strict_accuracy':score['pair_strict_accuracy']},indent=2))
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir() if p.is_file() and p.name!='manifest.json'}
(dest/'manifest.json').write_text(json.dumps({'version':'0.2-travel','original_cases':24,'added_cases':8,'added_pairs':4,'actual_models_evaluated_on_extension':[],'source':'User-reported experience inspired synthetic scenarios; not recovered Gemini conversations.','files':files},indent=2))
print('Built and validated 32 cases: original 24 unchanged; 8 new cases / 4 contrast pairs. No real model evaluated on extension.')
