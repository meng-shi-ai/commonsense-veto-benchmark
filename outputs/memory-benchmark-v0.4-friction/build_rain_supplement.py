import pathlib,json,hashlib,datetime
b=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.4-friction/rain-transition-supplement');b.mkdir(parents=True,exist_ok=True)
nodes=[];items=[]
for v,update,expected in [('retained','仍在下雨','B'),('stopped','雨已经停了，当前干燥','A')]:
 nid='rain_transition_'+v
 nodes.extend([dict(id=nid+'_update',parent='route_wet_side',mode='fork',prompt='9月6日10:03更新：我现在看到'+update+'，两条路线都能正常通行。先简单确认收到。'),dict(id=nid+'_side',parent=nid+'_update',mode='resume',prompt='换个话题，K-pop这个词中的K代表什么？一句话就好。'),dict(id=nid+'_apply',parent=nid+'_side',mode='fork',prompt='现在10:04，我要从车站去商场，给我当前具体路线。')])
 items.append(dict(id=nid+'_apply',target='明确推荐'+expected,criteria=['此前确实下雨，最新仍雨时B；明确雨停且正常通行时A，不继续强加过时雨天限制。','按成本和避雨偏好做行动建议，不只复述天气。','不编造个人风险或服务状态，不重复问已知信息；允许合理备用提醒。']))
for n,o in [('nodes.json',nodes),('rubric.json',{'frozen_before_supplement_run':True,'reason':'Explicit cessation-from-known-rain coverage; original frozen main group is not modified.','dimensions':['action_or_recall_correct','applies_valid_constraints','avoids_fabrication','proportionate_friction'],'review':'AI semantic review, not independent human validation','items':items})]:(b/n).write_text(json.dumps(o,ensure_ascii=False,indent=2))
(b/'manifest.json').write_text(json.dumps({'version':'0.4-rain-transition-supplement','frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'shared_parent':'route_wet_side from original completed v0.4 prefix','hashes':{n:hashlib.sha256((b/n).read_bytes()).hexdigest() for n in ['nodes.json','rubric.json']}},indent=2))
print('Frozen 2-branch rain cessation supplement; main group untouched.')
