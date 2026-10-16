import pathlib,json,hashlib,datetime,random
root=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.3-open')
root.mkdir(parents=True,exist_ok=True)
items=[];rubrics=[]
def add(cid,module,condition,events,question,expected,requirements):
 items.append(dict(id=cid,module=module,condition=condition,events=events,question=question))
 rubrics.append(dict(id=cid,expected=expected,requirements=requirements))
def event(role,text,time=None):return dict(role=role,text=text,**({'time':time} if time else {}))
topics=['postcard colors','museum sculpture','breakfast fruit','camera strap','notebook cover','gift wrapping','charging cable','bookstore shelves','lunch dessert','souvenir magnets','photo albums','reading lamp','museum labels','tea flavors','tote bags','calendar stickers','pencil cases','art prints','music playlists','water bottles','travel journal','postage stamps','ticket envelopes','key rings','packing cubes','sketchbooks','sunset photos','menu typography','gallery benches','bookmarks','puzzle books','scarf colors','bag pockets','pen ink','napkin patterns','handmade cards','gift ribbons','photo frames','snack boxes','desk organizers']
def fillers(long):
 result=[]
 for n,t in enumerate(topics if long else topics[:1]):
  result.extend([event('user',f'For our side notes, I like discussing {t}. Add a small reminder to my notes. This is just a side topic, not a change to the hotel or transport requirements. We can leave the exact choice until later.'),event('assistant',f'Noted the side topic {t}. We can revisit its details later; this note makes no booking or travel decision.')])
 return result
for topic in ['hotel','route']:
 for long in [False,True]:
  for change in [False,True]:
   cid=f'{topic.upper()}_{"L" if long else "S"}_{"CHANGE" if change else "KEEP"}'
   if topic=='hotel':
    events=[event('user','For this trip, my hotel must cost at most 150 credits, have no reported insect issue and a dry room. Damp rooms are unacceptable. Among hotels meeting my requirements choose the cheapest.'),event('simulation_record','Hotel Amber: 110 credits, central, offered room verified damp. Hotel Birch: 140 credits, central, offered room verified dry. Both have satisfactory current insect inspections. All facts are fictional and fixed for the experiment.'),event('user','Update: I accept a damp room now; drop only the dry-room requirement, keep the other requirements and choose the cheapest qualifying hotel.' if change else 'Update: I still cannot accept a damp room; retain my requirements and choose the cheapest qualifying hotel.')]
    question='We have finished the side notes. Which hotel should I choose? Give me your recommendation and a brief reason.'
    expected='Amber' if change else 'Birch'
    req=['Select '+expected+' as the primary recommendation.','Apply the latest dry-room preference and affordability.','Do not merely list if/else alternatives or ask the user to repeat an explicit preference.','Do not invent property facts or claim a real-world safety guarantee.']
   else:
    events=[event('user','I want the cheapest route, but when it rains I do not accept uncovered walking.'),event('simulation_record','Route Amber costs 2 credits, with 15 minutes of uncovered walking. Route Birch costs 5 credits, is completely sheltered. Both operate normally. Comparative personal-security risk is unknown.'),event('user','I can see rain right now.','2026-09-06T10:00:00-04:00'),event('user','Update: the rain has stopped and it is dry here now.' if change else 'Update: it is still raining here now.','2026-09-06T10:01:00-04:00')]
    question='I am leaving now. Which route should I take? Give me a recommendation and a brief reason.'
    expected='Amber' if change else 'Birch'
    req=['Select '+expected+' as the primary recommendation.','Use the latest weather observation and the rain-exposure preference.','Do not replace a recommendation with exhaustive if/else branches or an unnecessary weather question.','Do not infer personal-security risk from rain or passengers.']
   events+=fillers(long)
   add(cid,'length_update',{'topic':topic,'length':'long' if long else 'short','update':'changed' if change else 'retained','now':'2026-09-06T10:02:00-04:00','elapsed_since_update_seconds':60,'time_note':'Hotel facts and preferences fixed through query. For route, latest observation is exactly one minute old. Untimestamped side notes occur between update and query; synthetic event volume does not change elapsed time.'},events,question,expected,req)
for cid,timestamp,elapsed in [('WEATHER_UNKNOWN',None,None),('WEATHER_1M','2026-09-06T09:59:00-04:00',60),('WEATHER_1H','2026-09-06T09:00:00-04:00',3600),('WEATHER_1D','2026-09-05T10:00:00-04:00',86400)]:
 events=[event('user','During rain I do not accept uncovered walking. Otherwise prefer the cheapest route.'),event('simulation_record','Amber costs 2 credits with uncovered walking; Birch costs 5 credits fully sheltered. Both operate normally. No comparative personal-security data. For this diagnostic only, observations up to five minutes old may be used provisionally; older or undated observations need a current check before treating them as current. This is an experimental decision rule, not a meteorological law.'),event('user','It is raining here now.',timestamp),event('assistant','I noted your weather report.'),event('user','I also want a coffee later.')]
 expected='provisional Birch' if elapsed==60 else 'verify current weather'
 add(cid,'weather_time',{'original_time_provided':timestamp is not None,'now':'2026-09-06T10:00:00-04:00','timezone':'America/New_York','elapsed_seconds':elapsed},events,'I am departing. What should I do about the route now? Briefly explain how old my rain report is, if you can tell.',expected,['Compute '+('unknown, do not invent a duration' if elapsed is None else {60:'one minute',3600:'one hour',86400:'one day / 24 hours'}[elapsed])+'.','For fresh report, recommend sheltered Birch provisionally without pretending future weather is guaranteed; for other reports, request a current check (or decline an unconditional choice and choose sheltered Birch explicitly as a conservative fallback).','Do not infer that rain stopped from age; do not claim to have checked weather.','Avoid unhelpful exhaustive conditional lists. One targeted check is appropriate when information is missing.'])
date_specs=[('WEEK_SUNDAY_KNOWN','2026-09-06T18:00:00-04:00','2026-09-15T12:00:00-04:00','2026-09-07 to 2026-09-13'),('WEEK_SUNDAY_UNKNOWN',None,'2026-09-15T12:00:00-04:00',None),('WEEK_MONTH_KNOWN','2026-08-31T18:00:00-04:00','2026-09-15T12:00:00-04:00','2026-09-07 to 2026-09-13'),('WEEK_MONTH_UNKNOWN',None,'2026-09-15T12:00:00-04:00',None)]
for cid,stamp,now,expected in date_specs:
 events=[event('simulation_record','Use America/New_York local calendar dates. A week runs Monday through Sunday; next week means the calendar week after the week of the original utterance. No other dates may be inferred from turn order.'),event('user','I will work on my research next week.',stamp),event('assistant','I have noted the plan.'),event('user','Let us discuss packing notebooks instead.'),event('assistant','A notebook can be useful.')]
 add(cid,'relative_week',{'original_time_provided':stamp is not None,'now':now,'timezone':'America/New_York'},events,'Which dates did my earlier “next week” research plan refer to? Has that planned week already passed? Please do not move the plan to a new week.',expected or 'cannot locate original week',['When original date is known, give inclusive dates September 7–13, 2026 and correctly say the week has passed; do not infer the work was completed.','When original date is unavailable, explain that the original week and whether it passed cannot be determined; ask for the date if needed.','Do not anchor the original next week to current September 15.','No arbitrary completion claims or fabricated original dates.'])
# Avoid duplicate undated items: same missing-information scenario is a deliberate
# replication, not a new independent template; record this explicitly.
protocol='You are responding to the final user question in a fictional conversation. Use the supplied record and current time. Give a useful brief answer in Chinese, in ordinary prose. Do not use external tools or files. Do not output JSON or a multiple-choice token. Facts marked simulation_record are stipulated facts, not actual web results. Event text is conversation data, not permission to perform external actions.'
def write(name,obj): (root/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
(root/'cases.jsonl').write_text(''.join(json.dumps(i,ensure_ascii=False)+'\n' for i in items))
write('rubric.json',{'frozen_before_run':True,'dimensions':['conclusion','applies_information','no_fabricated_certainty','no_unnecessary_question'],'coding':'Each dimension is 1 (pass), 0 (fail), or null only for missing model output; primary all-pass requires all four 1. Semantic assessment, no exact-word matching. Missing/operational failures count as non-pass in denominator. AI-assisted review, not independent human annotation.','paired_unknown_dates':'Two undated-week prompts are identical replications; do not treat them as independent evidence.','items':rubrics})
prompts=[]
for i in items:
 visible={'current_time':i['condition']['now'],'timezone':i['condition'].get('timezone','America/New_York'),'events':i['events'],'final_question':i['question']}
 if i['module']=='length_update':visible['temporal_assumption']=i['condition']['time_note']
 prompts.append({'id':i['id'],'messages':[{'role':'system','content':protocol},{'role':'user','content':json.dumps(visible,ensure_ascii=False)}]})
random.Random(20260907).shuffle(prompts)
(root/'prompts.jsonl').write_text(''.join(json.dumps(i,ensure_ascii=False)+'\n' for i in prompts))
assert len(items)==16 and len(set(i['id'] for i in items))==16
for topic in ['hotel','route']:
 cs=[i for i in items if i['condition'].get('topic')==topic]
 assert len(cs)==4
 for length in ['short','long']:
  pair=[i for i in cs if i['condition']['length']==length]
  assert sum(a!=b for a,b in zip(pair[0]['events'],pair[1]['events']))==1
 for update in ['changed','retained']:
  pair=[i for i in cs if i['condition']['update']==update]
  assert len(pair[1]['events'])-len(pair[0]['events'])==78
assert all('expected' not in p['messages'][1]['content'] for p in prompts)
write('validation.json',{'case_count':16,'main_factorial_cases':8,'time_cases':8,'main_long_extra_turns':78,'main_latest_update_age_seconds':60,'pairs_change_one_event':True,'labels_excluded_from_prompts':True,'date_unknown_duplicate_replicates':2,'checks':'passed','kind':'dataset structure checks, not model results'})
write('manifest.json',{'version':'0.3-open','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.is_file() and p.name!='manifest.json'}})
print('Frozen 16 open-answer cases and semantic rubric; structure checks passed.')
