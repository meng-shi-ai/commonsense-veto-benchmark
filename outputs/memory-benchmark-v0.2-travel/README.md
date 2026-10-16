# Travel-constraint application extension v0.2

32 cases in total: the original 24 cases and labels are unchanged, and 8 new cases form 4 minimal contrast pairs. The earlier scores on the original 24 are stored separately in `../gpt-pilot` and do not carry over to this extension.

The new cases were inspired by a user's own account of a trip to Bayport. They are original simulated data, not a reproduction of a Gemini chat. The names of the original hotel, station, mall and transit system are unknown; every location, price, inspection result and route condition below is fictional. Dampness is not attributed to heavy rain, and no personal danger is inferred from passengers' identity, appearance or the rain.

| Case | Scenario | Correct judgment applied to the recommendation |
|---|---|---|
| C025 | The user requires a dry room, a budget under 150 and no reported pests. A is cheaper but confirmed damp; B is slightly more expensive but confirmed dry. After a museum digression, the user keeps the dryness requirement | Recommend B, which meets every requirement |
| C026 | Identical to the previous case, except the last statement: the user explicitly waives the dryness requirement and accepts damp | Recommend A, the cheapest option meeting the remaining requirements |
| C027 | Hotel C has a suitable price and location and passed a pest inspection, but there is no dryness information. After a digression about packing a charger, the user returns to the hotel | Say that dryness is unverified and verify before endorsing |
| C028 | Only the hotel information changes: a current inspection of the offered room confirms it is dry | C can be recommended on the facts given |
| C029 | The user will not walk outdoors in the rain. The cheap route A involves a 15-minute outdoor walk; B is covered the whole way. After a bookstore-and-lunch digression, the user confirms it is still raining before departure | Recommend B on the basis of the weather and the user's condition, without claiming B is physically safer |
| C030 | Only the pre-departure update changes: the rain has stopped and it is currently dry | Recommend A according to the cost preference |
| C031 | It rained yesterday and the current weather is unknown. The user has explicitly asked that, in this situation, the weather be checked before choosing a route rather than choosing unconditionally. A coffee digression follows | Verify the current weather first; do not treat yesterday's rain as current rain |
| C032 | Only the departure message changes: the user directly observes that it is raining now | Recommend the covered route B given the current rain |

Events form a dialogue in array order, all on the same date, and include user, assistant and simulated tool messages. Within each pair only the text of one event changes. Tool messages are in-case settings, not web lookups. Outputs keep the original `decision`, `value` and `evidence_ids` format.

What this tests is choosing an appropriate recommendation from the history given in the prompt, not merely restating a preference. Every new case has an answerable next action, which may be a verification step; a verification step is not the same as "insufficient information" in the scoring format. The answer and the cited evidence are scored separately, and the minimal evidence sets still need independent human review. The multi-turn history is presented as a single complete record; this is not yet an evaluation of an actual ongoing multi-turn conversation, real memory storage, or open-ended travel advice.

Run: `python3 benchmark.py validate`; `python3 -m unittest -v`; `python3 benchmark.py export --out prompts.jsonl`. The original HTTP adapter still works; never pass `gold.jsonl` to the model under test.

Software checks: the original 8 tests were adapted to dynamic case and pair counts. Additional checks confirm that the original 24 cases and labels are unchanged, that an ideal output passes all 8 new cases, and that a fixed program that ignores the contrast and repeats the same answer within each pair passes only 4/8 cases and 0/4 complete pairs. These fixed-program tests are not real model results.
