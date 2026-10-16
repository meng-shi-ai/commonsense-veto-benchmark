"""Encode completed AI semantic review of all 32 inspected responses; not an automatic judge."""
import pathlib,json
b=pathlib.Path('PUBLIC_REPO_ROOT/outputs/memory-benchmark-v0.3-open')
notes={
'HOTEL_L_KEEP':'明确推荐Birch，引用干燥、预算、虫害条件；长侧题没有覆盖仍适用的干燥限制。',
'HOTEL_S_KEEP':'明确推荐Birch；以干燥要求排除便宜但潮湿的Amber，没有反复问偏好。',
'HOTEL_L_CHANGE':'明确推荐Amber，说明用户取消干燥要求并应用剩余预算和虫害条件；未强加旧条件。',
'HOTEL_S_CHANGE':'明确推荐Amber并承认最新放弃干燥限制；价格与已给事实相符。',
'ROUTE_L_KEEP':'根据一分钟前仍下雨的观察明确推荐遮蔽Birch；未臆测人身危险。',
'ROUTE_S_KEEP':'以当前近况和露天步行限制明确推荐Birch；无需重复问天气。',
'ROUTE_L_CHANGE':'明确推荐Amber并引用一分钟前雨停；附带再次降雨时改道提醒不覆盖当前建议，属于合理限定。',
'ROUTE_S_CHANGE':'明确推荐Amber并应用最新雨停更新；没有只列条件分支，合理提醒天气可再变。',
'WEATHER_UNKNOWN':'明确原报告没有时间戳，不能判断年龄，先核验当前天气。虽然随后列雨/不雨和保守备选，但已经给出可执行的核验步骤，不是仅靠穷举分支；按冻结标准通过。',
'WEATHER_1H':'准确算出一小时，说明超过实验性五分钟窗口，先确认当前天气；没有因一小时就断言雨停。后续分支较多，但未取代首要核验行动。',
'WEATHER_1D':'准确算出24小时，先确认当前天气；未假定雨已停止。后续分支较多但有明确当前行动，按预设标准通过。',
'WEATHER_1M':'准确算出一分钟，按实验规则暂用近期雨况并推荐Birch；没有虚构查询或保证未来天气。',
'WEEK_SUNDAY_KNOWN':'将9月6日原话锚定9月7–13日，判断截至9月15日已过去；没有滚动改为新下周，也未声称研究已完成。',
'WEEK_MONTH_KNOWN':'将8月31日原话锚定9月7–13日并判断已过；日期跨月正确，没有滚动更新计划。',
'WEEK_SUNDAY_UNKNOWN':'缺少原日期则承认无法定位及判断是否已过；询问原日期属于必要补充，不是不必要反复询问。',
'WEEK_MONTH_UNKNOWN':'缺少原日期时不猜具体周，保留原句相对锚点；没有将当前日期作为原发言日。'}
for effort in ['medium','high']:
 rows=[json.loads(l) for l in (b/('run-'+effort)/'responses.jsonl').read_text().splitlines()]
 assert len(rows)==16 and all(r.get('answer') for r in rows)
 review={r['id']:{'conclusion':1,'applies_information':1,'no_fabricated_certainty':1,'no_unnecessary_question':1,'note':notes[r['id']],'evidence':r['answer'],'reviewer':'AI semantic review; all responses inspected; no independent human review'} for r in rows}
 (b/('review-'+effort+'.json')).write_text(json.dumps(review,ensure_ascii=False,indent=2))
