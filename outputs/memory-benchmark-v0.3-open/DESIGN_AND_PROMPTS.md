# v0.3 open-ended advice: comparing Medium and High on frozen prompts

This version is independent of the earlier 24-case set and the 32-case travel extension, whose data and scores are preserved. Model responses are natural-language advice in Chinese, with no fixed options and no requirement to return a predefined answer code. The prompts and the semantic rubric were frozen before the live runs.

## Which variables this run controls

Four main factors: the length of the context in text and events, whether the user's condition is updated, whether time information is provided, and the requested reasoning setting. Actual elapsed time (1 minute, 1 hour, 1 day) is a separate test factor within the time module. This is not a full factorial design.

Main module, 8 prompts: hotel and route each form a 2×2 grid of short/long × condition retained/changed. Variants of the same prompt differ in exactly one condition event. The long versions add 78 side-topic events that do not change the core condition; both lengths share the same current time and the same interval from the latest update to now. Topics such as a museum, coffee and a laptop are inserted after the update, so the test is whether the condition is still applied after much more irrelevant context.

Time module, 8 prompts: 4 weather prompts (original statement time unknown, 1 minute ago, 1 hour ago, 1 day ago) and 4 relative-date prompts (original date known/missing, as two contrasts). The two missing-date prompts are identical, a repeated presentation of a paired contrast rather than two independent templates. The 16 prompts must not be treated as 16 independent, identically distributed samples.

Each module was run in full at Medium and then in full at High on the same prompt set. The model request identifier was gpt-6-astra. Temperature and output-length settings were not changed, and no additional default-setting run was made.

## The user's latest clarification of "long conversation"

The long conversations the user actually cares about involve a real span of time: one day, "today I have the gym, yoga and class"; later, it is the fall break and the user is clearly in Bayport. The system should let the day's plans expire and the new travel location take effect, without inferring a permanent course drop, that the user has stopped going to the gym, or that all long-term preferences are void.

This run's main module tests only an increase in context content, not that multi-day combination; the time module touches on the age of information but does not fully cover the combination above. The clarification arrived after the prompts were frozen, so the prompts were not modified between the two runs, and the long-text condition is not described as a "real cross-session long-term memory test". Later versions should control the real time span and the context size independently, and score temporary plans, current location and long-term preferences separately.

## Example prompts as the user would see them

| Module | Core question | Reasonable response |
|---|---|---|
| Hotel, condition retained | A is cheaper but confirmed damp; B is slightly more expensive and dry; neither hotel within budget has reported pests. The user keeps the no-damp requirement | Clearly recommend B, applying the dryness requirement |
| Hotel, condition changed | The only change is that the user explicitly accepts damp and still wants the cheapest qualifying hotel | Clearly recommend A, without imposing the old preference |
| Route, still raining | The cheap route A involves a 15-minute outdoor walk; B is more expensive and fully covered. The user will not walk outdoors in the rain, and the latest observation says it is still raining | Recommend B based on current conditions, without speculating about danger from crowds |
| Route, rain stopped | The only change is that the latest observation says the rain has stopped and it is currently dry | Recommend A per the cost preference; no need to re-ask about both kinds of weather |
| Weather, original time missing | All that is known is that someone once said "it's raining now", with no day or time | Acknowledge that the interval cannot be computed, do not invent the current weather, and ask a targeted question about current conditions |
| Weather, 1 minute ago | It is 10:00 now; the rain report was at 9:59, same time zone | Compute 1 minute, provisionally recommend the covered route based on the recent observation, without promising the weather won't change |
| Weather, 1 hour ago | It is 10:00 now; the report was at 9:00 | Compute 1 hour; confirm the current weather, and do not assert the rain has stopped just because an hour has passed |
| Weather, 1 day ago | It is 10:00 the next day; the report was at 10:00 the previous day | Compute 24 hours; likewise, do not conclude that the rain has stopped |
| Original date known | The original statement "I'll do research next week" was made on Sunday, September 6, or Monday, August 31; it is now September 15 | Under a Monday-to-Sunday week rule, both refer to September 7–13, which has passed; this does not imply the work was completed |
| Original date unknown | The same statement, but the original date is missing | The planned week cannot be placed, nor can it be determined whether it has passed; do not reinterpret it as next week relative to today |

The weather-time prompts stipulate that "an observation within 5 minutes may be used provisionally for the current decision; older or undated observations must be verified first". This is a fixed, artificial diagnostic rule, **not a natural law about how fast weather changes**. A response passes if it asks one confirming question about the missing information, or states that the current situation is unknown and conservatively chooses the covered route. Laying out every conditional branch without giving an executable next step does not pass.

## Scoring

Each prompt is scored 0/1 on four dimensions: whether the conclusion is appropriate, whether the relevant information is applied, whether fabricated certainty is avoided, and whether unnecessary questions are avoided. The prompts leak no gold answers. Scoring applies the semantic criteria in `rubric.json`; no fixed word or punctuation is treated as the only acceptable answer. The primary pass rate requires all four dimensions to pass, and each dimension is also reported so that different errors are not merged into a single number. Run failures are kept and counted in the denominator.

A reasonable reminder that recent rain may change is not an error. By contrast, repeatedly asking the user to restate information that is already explicit, or declaring that old rain has stopped, are distinct errors. Date prompts must identify the correct target week, but any date notation is accepted.

Scoring was checked with AI assistance and has not received independent human review; it is not blinded expert annotation. The responses, per-dimension judgments and cited evidence are published so that users and researchers can review them. The criteria were not changed after seeing results, a failure is not guaranteed to appear, and no claim that High is better is made on the basis of a single-prompt difference.

## Important limits

Although it includes multi-turn user/assistant records, this run gives each new session the complete record at once: it is a "conversation replay input", not real turn-by-turn generation, storage, retrieval and cross-session resumption. The long versions place many synthetic events within a fixed narrative time; this is an experimental length manipulation and must not be taken as a model of natural conversation pace. All hotel, price, route and weather facts are simulated, no real weather was queried, and the original Gemini conversation was not reproduced.

Codex attaches its own system instructions, so this is not a pure API model comparison. Sessions are independent: no earlier outputs, no gold answers, and tool calls prohibited. The requested setting and the complete call parameters are recorded; where the server-side reasoning budget or underlying snapshot is not exposed, it is explicitly stated as unknown. A "High" label or a higher token count alone does not establish greater authority.

Configuration basis: per the [official Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), `model_reasoning_effort` supports `medium` and `high`; this run passed it explicitly on the command line.
