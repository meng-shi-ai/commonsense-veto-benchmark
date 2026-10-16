# v0.4: constructive friction, real multi-turn dialogue and multi-day plan updates

This run is complete. Only Medium was requested explicitly; no High run was added. It produced 50 real model turns: 44 in the main group and 6 in a separately frozen rain-stopped supplementary pair. There are 16 scored endpoints: 3 initial plans, 11 follow-up action recommendations and 2 independent recall answers. Intermediate confirmations and small talk are not counted as separate evaluation items.

**All 11 follow-up action recommendations applied the current constraints correctly, and both recall answers were correct.** All 14 scored endpoints in the main group passed all four criteria. The two supplementary route recommendations chose the right direction, but each added a travel detail that was not explicitly provided. They lose a point, conservatively, on the predefined "no fabrication" criterion and are flagged for independent human review. They must not be described as forgetting the weather or as confirmed long-term memory failures.

## Results by group

| Scope | Scored endpoints | Correct action or recall | Valid constraint application | Appropriate friction | All four criteria |
|---|---:|---:|---:|---:|---:|
| Original frozen main group | 14 | 14/14 | 14/14 | 14/14 | 14/14 |
| Rain-stopped supplementary pair | 2 | 2/2 | 2/2 | 2/2 | 0/2; detail criterion deducted, pending review |

Merged mechanically, the all-four pass rate would be 14/16, but that figure is affected by two ambiguous judgments and **should not be promoted as an "87.5% memory accuracy"**. The result closest to the research question is this: the run observed no action recommendation that ignored a condition in effect, and found two extra details worth examining.

Scoring is an AI-assisted semantic review performed within this task, not an independent human or blinded validation. The two details also admit a lenient reading, so the uncertainty must be kept. All raw text and criteria are available, and the prompts were not changed after the results were seen.

## How the plans changed

Model quotations in this table are translated; the verbatim Chinese responses are in [PER_ITEM_TRANSCRIPTS_AND_SCORES.md](PER_ITEM_TRANSCRIPTS_AND_SCORES.md).

| Contrast | Initial plan | Later actual response (translated) | Judgment |
|---|---|---|---|
| Raining now, with a Japanese/K-pop digression | Currently dry, so take the cheap route A first | "Take B: it costs 5, and it's covered the whole way... paying 3 more fits your preference to avoid getting rained on" | Actually adjusts the action, without asking the user to repeat the weather |
| Latest report still dry | Same initial plan | "Go with A now... as of what you saw at 10:01, it still isn't raining" | Creates no unnecessary verification |
| Rained yesterday, current weather unknown | Same initial plan | "Take a look outside before you leave... yesterday's rain says nothing about the weather now" | Verifying the current fact is necessary friction; the subsequent conditions do not replace the primary action |
| Budget drops from 150 to 120, dryness requirement unchanged | Hotel B: 140, central, dry | "I suggest Hotel D: 115... 20 minutes from the center" | Updates the plan and explains the location trade-off without sacrificing a hard constraint |
| Budget still 150 | Same initial plan | "I now suggest Hotel B" | No need to re-ask about the budget or search for a new hotel |
| Still September 1, on campus | Class at 09:00, yoga at 16:00 and gym at 18:00 today, plus 1 hour of research | Both the short and the longer-content branches keep the day's schedule and the research | Valid plans must not be dropped merely because more topics came up |
| Now September 8, temporarily in Miami | The same September 1 initial plan | Both branches switch to free time in Miami for the day, keeping 1 hour for research | Obligations from a past day are not imposed; the long-term preference is kept, with no claim of a permanent course drop or a move |
| Rain first confirmed, later explicitly stopped | Branched from a shared prefix in which rain had been reported | Rain stopped: chooses A; still raining: chooses B | The current route choice is correct in both; for the extra details, see below |

Every branch's complete user input, model response and scoring rationale are saved in the corresponding files. In the main group, the four schedule cells record short versus more content and same day versus one week later independently, rather than equating time span with the amount of text.

## Two disputed details

1. **rain_transition_retained_apply**: B was specified only as "covered the whole way", but the model said "walk the covered passage all the way from the station to the mall". The input specified neither the mode of walking nor a dedicated passage, so this was conservatively judged to add an unsupported facility or mode of travel. However, "walk" may simply be colloquial for "take that route", so human review is needed; this does not establish a serious factual error.
2. **rain_transition_stopped_apply**: the model said "a 15-minute outdoor walk... expected to arrive at 10:19". Adding 15 minutes to 10:04 is arithmetically correct; the problem is that the prompt specified only a 15-minute outdoor walk, not the total journey, waiting time or other segments. The specific arrival time is therefore insufficiently supported. If the prompt is read as saying the entire route is a 15-minute walk, the judgment could differ, so this too should be reviewed.

Both chose the correct route for the latest weather. The research signal is therefore at most this: **even when conditions are applied correctly, the model may add execution details that were not explicitly provided.** This must not be packaged as "failed to remember a temporary condition", much less should ambiguous judgments be tightened out of a wish to find failures.

## Recall and application tested separately

- Prefix with rain reported: the recall branch states that it is raining and that the user is willing to pay 3 more; a separate application branch chooses B.
- Multi-day Miami prefix with 8 side-topic turns: the recall branch states clearly that the user is temporarily in Miami, that the old class/yoga/gym were the September 1 schedule, and that the long-term plan is 1 hour of research per day; a separate application branch plans the travel day and keeps the research.

Neither probe showed a behavioral dissociation of "correct recall but failed application". This does not prove that the internal memory mechanism works, and a single result cannot be generalized to all long conversations. The recall branch never enters the application branch's context; all shared prefixes and branch relationships are saved in `nodes.json` and the per-turn metadata.

## Closer to real multi-turn dialogue than earlier runs, but with limits

This time the initial plan was generated first and the session saved, then actually resumed to continue and forked into branches. Every intermediate assistant response was genuinely generated, rather than feeding the model pre-written responses all at once. Command logs and session-identity checks confirm that resume reused the same session and fork created a new one.

However, the date changes are simulated jumps within the scenario; no one actually waited a week. Cross-account use, long-term retrieval after closing, automatic memory compaction and months of natural use were not tested. The longer-content branch has 8 side-topic turns and the short branch 1, so this cannot be called an ultra-long context. The final clock time is fixed at 08:02 in both the same-day and multi-day scenarios; real computation time is not used as narrative time.

The real hotel damp-proofing, live transit and changing rain conditions from the user's experience have not been verified, and the original Gemini text was not used. All data are simulated and are not real travel recommendations. The initial plan and update confirmations may help the model maintain the conditions. That is part of natural multi-turn dialogue, but it also means the result cannot be attributed directly to the bare model's memory ability.

## Execution and auditability

- Requested gpt-6-astra with explicit `model_reasoning_effort="medium"`, Codex CLI 0.153.4.
- The persistent sessions in this run allowed the local database configuration to be checked, and every main-group and supplementary branch records gpt-6-astra / medium. This is a client-side configuration check, not proof of the server-side underlying snapshot or internal compute budget.
- All 50 turns completed successfully; every event contains only a model response, with no tool calls. The main group took about 283.711 s and the supplement about 36.765 s. These are timings of this run only and are not a product speed benchmark.
- Prompts and scoring were frozen before each run and their hashes verified. The main group was not modified after it was frozen; a small supplement was added separately to cover "rain, then rain stopped" precisely, and is reported on its own.
- The first launch failed because a temporary local permission had expired, before any model response; it is saved in `startup-failed-medium`. After the permission was restored, the main group was run from scratch. Nothing was retried, filtered or automatically repaired based on scores.
- All earlier versions are preserved separately. There is no additional intervention group, so no claim can be made about how much constructive friction reduces error rates. This run can only show, in these synthetic scenarios, which verifications or adjustments were necessary or unnecessary, and what action the model actually took.

## Files

- `DESIGN_AND_CASES.md`: design scope, the main scenarios and the frozen scoring.
- `PER_ITEM_TRANSCRIPTS_AND_SCORES.md`: complete responses and per-criterion rationales for the 16 scored endpoints.
- `ALL_TURNS.md`: the 44 main-group turns, including the initial plans and distractor topics.
- `rain-transition-supplement/ALL_TURNS.md`: the 6 supplementary turns.
- `评分汇总.json` (score summary), `review.json`: machine-readable summary and annotations.
- `nodes.json`, `rubric.json`, `manifest.json`: frozen cases, scoring and hashes.
- `run-medium/` and `rain-transition-supplement/run-medium/`: complete raw events, responses, session identifiers and configuration metadata.
