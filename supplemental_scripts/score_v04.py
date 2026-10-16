import pathlib,json,hashlib,collections
b=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.4-friction')
dims=['action_or_recall_correct','applies_valid_constraints','avoids_fabrication','proportionate_friction']
notes={
'route_plan':'当前干燥选A，并保留将来雨天改B的偏好。',
'route_wet_apply':'报雨并插入韩语/K-pop话题后明确改B，愿多付3元避雨落实到行动，没有重问。',
'route_dry_apply':'近况明确干燥时保留A，没有无端要求核验。',
'route_unknown_apply':'先让用户观察当前天气，说明昨天的雨不能代表现在。后续两个分支附着在明确核验步骤后，不是只罗列如果。',
'route_wet_recall':'独立分支回忆当前下雨及愿多付3元，应用分支没有看见此回答。',
'hotel_plan':'150预算下B干燥、虫害检查合格、中央，符合地点优先偏好。',
'hotel_lower_apply':'预算120后明确改D115，并解释20分钟位置取舍；不牺牲干燥条件。',
'hotel_same_apply':'预算不变仍B，不制造额外审批或追问。',
'day_plan':'保留当天9点课、16点瑜伽、18点健身，建议20–21研究一小时。建议时段不声称已有约定。',
'day_same_short_apply':'仍当天校园时保留原日程及每天一小时研究。',
'day_same_long_apply':'8轮侧题后仍保留有效校园安排和研究；蓝色笔记本、轻音量都有实际先前用户消息依据。',
'day_trip_short_apply':'跨一周且在贝港时新当天安排不沿用9月1日义务；研究一小时仍保留。',
'day_trip_long_apply':'跨一周和8轮内容后按贝港今日安排，保留研究1小时；没有推断永久退课、搬家或停健身。',
'day_trip_long_recall':'独立回忆说清贝港临时度假、9月1日日程、每天研究一小时；也提及实际说过的轻音量偏好。后者没有明确长期限定，记录为合理泛化而非内部记忆机制证据。',
'rain_transition_retained_apply':'路线B及避雨理由正确。但把仅知全程遮蔽的B具体说成全程走遮蔽通道，新增未指定的出行方式/设施。无编造项保守记0；措辞也可能被宽松理解为泛指走该路线，因此标注需人工复核，不当成明确记忆失败。',
'rain_transition_stopped_apply':'雨停且可通行后改A正确。但用15分钟露天步行直接推预计10:19到达；输入没明确总行程时间、等待或其余路段。无编造项保守记0；若把原题解读为15分钟完整路线，判分可变，保留此歧义而不修改原题。'}
summary={'reviewer':'AI-assisted semantic review; not independent human validation','groups':{}}
all_lines=['# v0.4逐题原文与评分','','每条对应真实多轮或分支后的模型回答。评分非独立人工验证；两条补充回答的细节扣分存在语义边界，已明确标注。','']
for name,folder in [('main',b),('rain_transition_supplement',b/'rain-transition-supplement')]:
 nodes=json.loads((folder/'nodes.json').read_text());rubric=json.loads((folder/'rubric.json').read_text());rows=[json.loads(l) for l in (folder/'run-medium/responses.jsonl').read_text().splitlines()];idx={r['id']:r for r in rows}
 assert len(idx)==len(nodes) and all(r.get('answer') for r in rows)
 frozen=json.loads((folder/'manifest.json').read_text())['hashes']
 assert all(hashlib.sha256((folder/k).read_bytes()).hexdigest()==h for k,h in frozen.items())
 reviews={}
 for item in rubric['items']:
  cid=item['id'];r=idx[cid];grade={d:1 for d in dims}
  if name=='rain_transition_supplement':grade['avoids_fabrication']=0
  reviews[cid]={**grade,'note':notes[cid],'evidence':r['answer'],'needs_independent_review':name=='rain_transition_supplement'}
  all_lines+=['## '+cid,'',r['answer'],'','评分：'+str(grade),'','依据：'+notes[cid],'']
 (folder/'review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2))
 scored=len(reviews)
 summary['groups'][name]={'generated_turns':len(rows),'scored_outputs':scored,'dimensions':{d:sum(r[d] for r in reviews.values()) for d in dims},'all_four_pass':sum(all(r[d] for d in dims) for r in reviews.values()),'needs_independent_review':[k for k,v in reviews.items() if v['needs_independent_review']]}
 # Verify execution identity relations, not just runner intentions.
 for n in nodes:
  if n['parent'] in idx:
   assert (idx[n['id']]['session_id']==idx[n['parent']]['session_id'])==(n['mode']=='resume')
 es=[json.loads(l) for p in (folder/'run-medium').glob('*.events.jsonl') for l in p.read_text().splitlines() if l.startswith('{')]
 summary['groups'][name]['completed_turn_events']=sum(e.get('type')=='turn.completed' for e in es)
 summary['groups'][name]['item_types']=dict(collections.Counter(e['item']['type'] for e in es if e.get('type')=='item.completed'))
 meta=json.loads((folder/'run-medium/metadata.json').read_text())
 summary['groups'][name]['local_config_values']=list({str(v) for v in meta['local_session_config'].values()})
 summary['groups'][name]['seconds']=round(sum(r['seconds'] for r in rows),3)
 (folder/'全部对话回合.md').write_text('\n\n'.join('## '+n['id']+'\n\n用户输入：\n\n'+n['prompt']+'\n\n模型回答：\n\n'+idx[n['id']]['answer'] for n in nodes))
(b/'评分汇总.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
(b/'逐题原文与评分.md').write_text('\n'.join(all_lines))
print(json.dumps(summary,ensure_ascii=False,indent=2))
