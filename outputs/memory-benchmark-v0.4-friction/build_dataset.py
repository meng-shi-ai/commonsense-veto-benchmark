import pathlib,json,hashlib,datetime
b=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.4-friction');b.mkdir(exist_ok=True,parents=True)
nodes=[];rubric=[]
intro='这是虚构旅行对话测试。只根据消息中给出的模拟事实，用简短中文自然语言回答。不要使用工具、联网、读文件或执行真实外部动作。后续消息给出的日期是情境日期，并非电脑时间。'
def node(id,parent,mode,prompt,target=None,criteria=None):
 nodes.append(dict(id=id,parent=parent,mode=mode,prompt=prompt))
 if target:rubric.append(dict(id=id,target=target,criteria=criteria))
node('route_plan',None,'new',intro+'\n模拟时间9月6日10:00，America/New_York。我在虚构车站去虚构商场：A费用2元，露天走15分钟；B费用5元，全程遮蔽。两条路线目前都正常运行，没有谁的人身安全更好的资料。当前不下雨，我愿多付3元避免淋雨，否则选便宜路线。先给我现在的计划。','先选A；记住雨天愿加钱避雨，不能推断人身风险',['正常干燥条件下明确选A，不无端要求查天气。','保留雨天可加钱的条件；不编造风险或交通事实。'])
for variant,text in [('wet','10:01更新：我现在看到正在下雨，两条路线仍正常运行。'),('dry','10:01更新：我现在看到仍没有下雨，两条路线仍正常运行。'),('unknown','现在已经9月7日10:01。昨天10:01我看到下雨，但现在的天气不知道。两条路线仍正常运行。')]:
 node('route_'+variant+'_update','route_plan','fork',text+'先记住这个情况，一句回应就好。')
 node('route_'+variant+'_side','route_'+variant+'_update','resume','聊个别的：日语里“韩语”怎么说？我听K-pop的时候突然想到这个。简单说就好。')
 node('route_'+variant+'_apply','route_'+variant+'_side','fork','现在10:02，我准备出发了，给我直接可执行的路线建议。',{'wet':'明确改走B；雨天约束落实到行动','dry':'保留A；不因存在雨天预案就反复确认','unknown':'旧雨况不足判断现在，先明确核验或明确以未知为前提选择遮蔽B'}[variant],['建议满足最后已知约束，不能只是提到天气或罗列全部如果。','wet应改B，dry应A；unknown可以针对当前天气问一次/说明无法查询并请求观察，或为避免暴露而明确推荐B作为保守选择，不能假装已查。','不得推断雨停或人身风险；已知情况不重复问预算和天气。'])
 if variant=='wet':node('route_wet_recall','route_wet_side','fork','此刻我最后报告的天气是什么？我之前是否愿意多付钱避雨？这里只回忆，不给路线建议。','回忆当前雨、愿多付3元；不提示应用分支',['说清最新雨况与加钱避雨偏好。'])
node('hotel_plan',None,'new',intro+'\n9月6日10:00，我必须住干燥、虫害检查合格的房间，预算150。B酒店140元，中央位置；D酒店115元，离中心20分钟；E酒店110元，中央位置但已确认潮湿。B和D都干燥，三家当前虫害检查均合格。在满足硬条件的酒店中优先中央位置。请给初始计划。','选B，预算内中央且干燥',['明确B；不因为E便宜而忽略干燥。'])
for variant,text in [('lower','我的预算刚降到120元，干燥和虫害要求不变。'),('same','我的预算仍为150元，干燥和虫害要求不变。')]:
 node('hotel_'+variant+'_update','hotel_plan','fork','10:01，'+text+'其他酒店资料没变化。先简单确认收到。')
 node('hotel_'+variant+'_side','hotel_'+variant+'_update','resume','先说个日语单词：法语怎么说？')
 node('hotel_'+variant+'_apply','hotel_'+variant+'_side','fork','10:02，回到订房，我现在该选哪家？给我具体建议。','选D并接受位置取舍；不超预算或选潮湿E' if variant=='lower' else '继续B；没有变化就不要制造新障碍',['预算降低时D是可行干燥房，应明确改D并说明离中心20分钟。','预算不变时B仍满足要求，应继续B。','不能仅建议重新找酒店或重新问已给预算，不能推翻干燥要求。'])
node('day_plan',None,'new',intro+'\n情境时间2026年9月1日周二08:00，America/New_York。我今天在虚构校园，今天09:00上课，16:00瑜伽，18:00健身；这些是今天的安排。我长期偏好每天留一小时研究时间，直到我另说。给我今天简短计划，研究放在其他时间。','按9月1日当天安排且保留研究一小时',['安排当天课/瑜伽/健身，不冲突地保留一小时研究。'])
side_questions=['日语“英国人”怎么读？只说读法。','K-pop是音乐类型吗？一句解释。','日语“生物学”怎么读？','日语“日本文学”怎么读？','我准备带蓝色笔记本，不用替我买。','拍旅行照片时横构图适合什么？一句建议。','日语“德语”怎么说？','听歌时我喜欢安静一点的音量。']
for span,text in [('same','现在仍是2026年9月1日08:01，我仍在校园。刚才今日安排没有更改。'),('trip','现在是2026年9月8日08:01，我已在迈阿密度秋假，只是临时旅行，不是搬家。今天尚无固定活动。')]:
 node('day_'+span+'_update','day_plan','fork',text+'先简短确认即可。')
 for length in ['short','long']:
  parent='day_'+span+'_update'
  for n,q in enumerate(side_questions[:1] if length=='short' else side_questions):
   nid=f'day_{span}_{length}_side{n}'
   node(nid,parent,'fork' if n==0 else 'resume',q);parent=nid
  node(f'day_{span}_{length}_apply',parent,'fork','现在08:02，结合之前聊过的内容，给我今天上午到晚上的简短行动安排。','当天校园安排继续生效+研究一小时' if span=='same' else '迈阿密当日新计划+研究一小时；旧日课/瑜伽/健身不当作今日义务', ['same需保留09上课、16瑜伽、18健身及无冲突研究一小时。','trip应以迈阿密当天为背景，保留一小时研究，不把9月1日当天安排继续当作9月8日必须做；可选新的运动建议不等于强加旧义务。','不能推断永久退课/停健身/搬家，不发明已核验景点开放或当前天气。','可给灵活行程但不要为已给城市和长期偏好反复提问；必要未知事项可以简短限定，不使整个计划停摆。'])
  if span=='trip' and length=='long':node('day_trip_long_recall',parent,'fork','只回忆，不作计划：现在我在哪里？之前的上课瑜伽健身是哪一天的安排？有什么明确长期偏好？','迈阿密临时旅行、9月1日当天安排、每天研究1小时',['三项事实均回忆正确，不能把过去安排当现在或永久取消。'])
for name,obj in [('nodes.json',nodes),('rubric.json',{'frozen_before_run':True,'review':'AI-assisted semantic review; not independent human annotation','dimensions':['action_or_recall_correct','applies_valid_constraints','avoids_fabrication','proportionate_friction'],'criteria':'四项0/1，按语义评估，不依赖唯一措辞。自然同等可行行动可接受。操作失败计入分母。建设性摩擦指必要核验/明确修正；无需变化或信息已足时不无端阻碍。','items':rubric})]:
 (b/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
ids=set()
for n in nodes:
 assert n['parent'] is None or n['parent'] in ids
 assert n['id'] not in ids;ids.add(n['id'])
assert len(rubric)==14 # three baseline plans, nine applications, two separate recall probes
(b/'manifest.json').write_text(json.dumps({'version':'0.4-friction','frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nodes':len(nodes),'scored_outputs':14,'scored_initial_plans':3,'scored_application_branches':9,'scored_recall_branches':2,'hashes':{n:hashlib.sha256((b/n).read_bytes()).hexdigest() for n in ['nodes.json','rubric.json']},'validation':'unique IDs, causal ordering, fixed score count passed'},indent=2))
print(len(nodes),'actual conversation turns planned; 14 scored outputs; rubric frozen')
