# v0.4: per-item responses and scores

Each entry is a real model response from an actual multi-turn conversation or one of its branches. Scoring is not independent human validation. The detail deductions on the two supplementary responses sit on a semantic boundary and are marked explicitly.

User inputs and model responses are reproduced verbatim, in the language in which the experiment was run (Chinese). English summaries of every scenario are in [DESIGN_AND_CASES.md](DESIGN_AND_CASES.md) and [RESULTS.md](RESULTS.md).
Scoring rationales are translated from `review.json`, which keeps the original wording.

## route_plan

**Model response (verbatim):**

现在选A，费用2元，露天走15分钟。当前不下雨，符合你优先省钱的偏好；出发前若下雨，就多付3元改选全程遮蔽的B。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** Chooses A while it is currently dry, and keeps the preference to switch to B if it rains later.

## route_wet_apply

**Model response (verbatim):**

选B，费用5元，全程遮蔽。你刚才看到正在下雨，多付3元符合你避免淋雨的偏好，现在就走B。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** After the rain report and the inserted Korean/K-pop topic, clearly switches to B, turning the willingness to pay 3 more to avoid rain into action, without re-asking.

## route_wet_recall

**Model response (verbatim):**

你最后报告的是正在下雨。你之前表示愿意多付3元避免淋雨。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** The independent branch recalls the current rain and the willingness to pay 3 more; the application branch never saw this response.

## route_dry_apply

**Model response (verbatim):**

现在走A：费用2元，露天步行15分钟。按你10:01看到的情况，仍未下雨，选便宜路线符合你的偏好。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** Keeps A when recent conditions are explicitly dry, without needlessly asking for verification.

## route_unknown_apply

**Model response (verbatim):**

出发前看一眼外面：现在下雨就选B，5元全程遮蔽；没下雨就选A，2元、露天走15分钟。昨天的雨不能说明现在的天气。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** First has the user check the current weather and explains that yesterday's rain does not represent now. The two follow-up branches are attached to an explicit verification step rather than being a bare list of what-ifs.

## hotel_plan

**Model response (verbatim):**

初始计划选B酒店：140元，预算内，房间干燥且虫害检查合格，又位于中央，符合优先偏好。D酒店作为备选；E酒店因已确认潮湿而排除。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** With a budget of 150, B is dry, passed the pest inspection and is central, matching the location-first preference.

## hotel_lower_apply

**Model response (verbatim):**

建议选D酒店：115元，符合最新120元预算，房间干燥且虫害检查合格，离中心20分钟。B酒店超预算，E酒店潮湿，因此D是唯一满足所有硬条件的选择。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** After the budget drops to 120, clearly switches to D at 115 and explains the 20-minute location trade-off; does not sacrifice the dryness condition.

## hotel_same_apply

**Model response (verbatim):**

现在建议选B酒店：140元，低于150元预算，房间干燥、虫害检查合格，而且位于中央，最符合你的要求。D酒店可作备选；E酒店因潮湿排除。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** With the budget unchanged, stays with B and creates no extra approval step or follow-up question.

## day_plan

**Model response (verbatim):**

今天（9月1日，周二）安排：

- 08:00–08:45：早餐、准备上课。
- 09:00：上课。
- 16:00：瑜伽。
- 18:00：健身。
- 20:00–21:00：研究。

之后的计划也会按你的长期偏好，每天留一小时研究，直到你另说。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** Keeps the day's 09:00 class, 16:00 yoga and 18:00 gym, and suggests one hour of research from 20:00 to 21:00. The suggested slot is not presented as an existing commitment.

## day_same_short_apply

**Model response (verbatim):**

今天（9月1日）你仍在校园，按原安排：

- 现在至09:00：吃早餐、准备上课。
- 09:00：上课。
- 中午：午餐、休息。
- 下午：处理学习任务，留出前往瑜伽的时间。
- 16:00：瑜伽。
- 18:00：健身，结束后晚餐。
- 20:00–21:00：研究一小时。
- 之后：放松、准备休息。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** Still on campus the same day, keeps the original schedule and the daily hour of research.

## day_same_long_apply

**Model response (verbatim):**

今天（2026年9月1日，周二）你仍在校园，安排如下：

- 08:02起：吃早餐、准备上课，带上蓝色笔记本。
- 09:00：上课。
- 中午：午餐、休息。
- 下午：自由安排，16:00瑜伽。
- 18:00：健身，结束后晚餐、休息。
- 20:00–21:00：研究，保留每天一小时的习惯。
- 之后：放松、准备睡觉；听歌时音量轻一些。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** After 8 side-topic turns, still keeps the valid campus schedule and the research; the blue notebook and the low-volume preference are both supported by actual earlier user messages.

## day_trip_short_apply

**Model response (verbatim):**

今天在贝港度秋假，没有固定活动，可以这样安排：

- 08:02–09:00：早餐，慢慢开始一天。
- 09:00–10:00：研究，保留每天一小时的习惯。
- 10:00–12:00：散步、随意逛逛。
- 12:00–14:00：午餐、休息。
- 14:00–17:00：自由游玩。
- 17:00–19:00：晚餐、放松。
- 19:00以后：自由安排，早点休息。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** One week later and in Bayport, the new day's plan does not carry over the September 1 obligations; the hour of research is kept.

## day_trip_long_apply

**Model response (verbatim):**

今天（9月8日）在贝港度秋假，可以这样安排：

- 08:02–09:00：早餐、准备出门，带上蓝色笔记本。
- 09:00–12:00：散步游览，拍宽阔风景时用横构图。
- 12:00–14:00：午餐、休息，听歌时把音量调轻。
- 14:00–15:00：留一小时研究。
- 15:00–18:00：自由逛逛，累了就休息。
- 18:00以后：晚餐、整理照片，放松休息。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** After one week and 8 turns of content, plans today in Bayport and keeps the 1 hour of research; infers neither a permanent course drop, a move, nor stopping the gym.

## day_trip_long_recall

**Model response (verbatim):**

你现在在贝港临时度秋假，不是搬家。之前的上课、瑜伽和健身是2026年9月1日的安排。

明确的长期偏好：每天留一小时研究时间，直到你另说；听歌时喜欢音量安静一些。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 1, 'proportionate_friction': 1}`

**Scoring rationale:** The independent recall clearly states the temporary Bayport vacation, the September 1 schedule and the daily hour of research; it also mentions the low-volume preference the user actually expressed. That preference had no explicit long-term qualifier, so it is recorded as a reasonable generalization, not as evidence about the internal memory mechanism.

## rain_transition_retained_apply

**Model response (verbatim):**

现在选B路线，从车站全程走遮蔽通道去商场，费用5元；根据10:03的最新情况仍在下雨，多付3元符合你避免淋雨的偏好。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 0, 'proportionate_friction': 1}`

**Scoring rationale:** Route B and the reason of avoiding rain are correct. However, B, known only to be covered the whole way, is described specifically as walking a covered passage the whole way, adding an unspecified mode of travel or facility. The no-fabrication criterion is conservatively scored 0; the wording could also be read leniently as simply 'taking that route', so it is flagged for human review and not treated as a clear memory failure.

## rain_transition_stopped_apply

**Model response (verbatim):**

现在选A路线：从车站露天步行15分钟去商场，费用2元，预计10:19到达。最新情况是雨已停、当前干燥，两条路线都正常通行，选A符合你省钱的偏好。

**Scores:** `{'action_or_recall_correct': 1, 'applies_valid_constraints': 1, 'avoids_fabrication': 0, 'proportionate_friction': 1}`

**Scoring rationale:** Switching to A once the rain has stopped and the route is open is correct. However, it derives an expected arrival of 10:19 directly from the 15-minute outdoor walk, while the input did not specify the total journey time, waiting or other segments. The no-fabrication criterion is conservatively scored 0; if the prompt is read as saying the whole route is a 15-minute walk, the judgment could change. The ambiguity is kept and the prompt is not modified.
