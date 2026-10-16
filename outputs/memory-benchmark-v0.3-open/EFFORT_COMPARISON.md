# v0.3 live evaluation: Medium versus High

With the user's final authorization, the same 16 prompts were run at two settings: a complete Medium run, then a complete High run, for 32 live model responses in total. The earlier 24-case set, the 32-case travel extension and their scores are preserved. This version switches to open-ended advice in Chinese and provides no fixed answer options.

## Core results

| Condition | Prompts per setting | Medium, all four criteria | High, all four criteria |
|---|---:|---:|---:|
| Short transcript, condition retained | 2 | 2/2 | 2/2 |
| Short transcript, condition changed | 2 | 2/2 | 2/2 |
| Long transcript, condition retained | 2 | 2/2 | 2/2 |
| Long transcript, condition changed | 2 | 2/2 | 2/2 |
| Weather report age unknown / 1 minute / 1 hour / 1 day | 4 | 4/4 | 4/4 |
| "Next week" with original date known / unknown | 4 | 4/4 | 4/4 |
| All | 16 | 16/16 | 16/16 |

Against the four frozen semantic criteria (an appropriate conclusion, applying the information, avoiding fabricated certainty, avoiding unnecessary questions), both settings scored 16/16. Scoring was an AI-assisted per-item review performed within this task, not an independent human or blinded validation; the scoring evidence and raw responses are published. Each setting was run only once, and the two missing-date prompts are identical, so they are a repeated presentation rather than independent samples. These results support no claim of statistical equivalence, nor that either setting is stronger overall.

This run did not observe errors caused by more text combined with condition updates, nor any accuracy gain for High. This is only the result of a small replay test with explicit rules; it does not imply that real long conversations are free of problems.

## Specific observations and "what if" questions

Hotel prompts: when the dryness requirement was retained, both settings recommended the dry Birch; when the user explicitly waived it, both switched to the cheaper Amber. Route prompts: while it was still raining recently, both chose the covered Birch; once the rain had explicitly stopped, both chose the cheaper Amber. Neither treated rain or passengers' identity as evidence of personal danger.

Weather prompts: the 1-minute-old report was correctly aged and used provisionally for the route advice; for the 1-hour, 24-hour and unknown-time reports, both settings first asked for the current weather, and neither declared that the rain had stopped merely because the information was old. Relative-date prompts: both settings placed the original "next week" at September 7–13, or acknowledged it could not be placed when the original date was missing; neither recomputed it relative to the current date of September 15.

**An expression issue worth recording:** in three prompts (WEATHER_UNKNOWN, WEATHER_1H, WEATHER_1D), both settings said "first confirm the current weather" and then also listed rain, no-rain and cannot-confirm branches. The user dislikes this kind of verbose answer, so the experience could still improve. However, the frozen criteria allow a necessary verification with a clear action, plus conservative alternatives; these responses do not merely list conditions without making a judgment, so they were not reclassified as failures after the fact. In ROUTE_S_CHANGE and ROUTE_L_CHANGE, both settings first clearly recommended Amber and then added that the route should change if it rains again, which is also a reasonable qualification.

This run produced no failures meeting the predefined definition. The cases above are reviewable observations about expression and must not be presented as demonstrated memory failures.

## Request parameters and what can be verified

- Requested model: gpt-6-astra; Codex CLI 0.153.4, signed in through the existing ChatGPT account.
- The Medium run explicitly passed `-c model_reasoning_effort="medium"` and the High run `-c model_reasoning_effort="high"`. These are officially supported configuration keys, and neither run reported a parameter error. The chat-window setting was not used as an experimental basis.
- Each prompt used a brand-new temporary session, in the same fixed order. Within each run, the prompts, instructions and rubric hashes were identical and verified before and after the run. Tool calls were prohibited, and the event logs show that all 32 calls returned only a model response, with no tool calls.
- Temperature and output limits were not set; all other call parameters were identical. Every output was saved for both settings, with no automatic retries and no best-of selection. The first Medium launch failed because a temporary local permission had expired, and produced no model response; the failure is preserved in `startup-failed-medium`, and the two complete runs began only after the permission was restored.
- The requested setting can be checked from the saved program and metadata. The captured events do not echo the server-side setting actually used or the underlying model snapshot, and the temporary sessions left no verifiable setting record in the local state database. The "explicitly requested setting" must therefore not be overstated as independent verification of the server's actual compute budget.

| Run record | Medium | High |
|---|---:|---:|
| Valid responses | 16 | 16 |
| Wall-clock time for the full run (sum over prompts) | 128.331 s | 133.022 s |
| Median time per prompt | 7.855 s | 8.191 s |
| Recorded input tokens, total | 255,034 | 255,034 |
| Recorded output tokens, total | 1,280 | 1,470 |
| Recorded reasoning_output_tokens | 0 | 202 |

Token counts include Codex's additional instructions. The reasoning-token field is the logged value, and zero cannot be read directly as no internal reasoning at all. Latency includes startup, network and caching effects. This was a single sequential run, so it supports no speed conclusion attributable to the setting and is not a cost estimate.

## Distance from the user's actual question

The user has clarified that a "long conversation" means, in particular, a real span of time across days, up to and including the fall break. For example: earlier, "today I have the gym, yoga and class"; later, the user is clearly in Bayport. The one-day plans should expire and the new location should take effect, while long-term preferences must not be wiped along with them, and the model must not infer a permanent course drop or that the user has stopped going to the gym.

**This full combination has not been tested yet.** In this run the main module varies the amount of text and the number of events while keeping the narrative time fixed; the time module covers the age of weather information and placing the original date of a statement, but it is not an experiment in cross-session storage, retrieval or ongoing generation. The two kinds of "long" must not be conflated. The clarification arrived after the prompts were frozen, so the prompts were not changed between the two settings.

The complete record is given once as the input to a new session, which is still simpler than a real multi-day conversation, and it includes explicit fictional hotel facts, rain conditions and a five-minute freshness rule. The five-minute threshold is a pre-specified experimental parameter, not a fact about weather. The data are inspired by the user's experience and do not reproduce the original Gemini conversation. The current scores can neither confirm nor refute that real experience, nor compare GPT with Gemini.

A valuable direction for the next version is to control elapsed real time and text volume independently, while distinguishing expired same-day plans, current-location updates and retained long-term preferences, and then to compare full-record, controlled-summary and retrieval inputs. This is a suggestion, not a result of this run, and it has not been run yet.

## Files

- [Design and prompts](DESIGN_AND_PROMPTS.md)
- [Medium: per-item responses and scores](PER_ITEM_RESULTS_MEDIUM.md)
- [High: per-item responses and scores](PER_ITEM_RESULTS_HIGH.md)
- [Machine-readable comparison by group](comparison.json)
- `cases.jsonl`, `prompts.jsonl`: the 16 prompts and the actual model inputs.
- `rubric.json`: criteria frozen before the live runs.
- `review-medium.json`, `review-high.json`: per-item AI-assisted scoring and evidence.
- `run-medium/`, `run-high/`: complete raw events, responses and metadata.

Configuration reference: [official Codex configuration documentation](https://learn.chatgpt.com/docs/config-file/config-reference).
