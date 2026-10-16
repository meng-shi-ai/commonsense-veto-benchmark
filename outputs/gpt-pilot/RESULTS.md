# Memory Evidence Benchmark: first live-model pilot

All 24 synthetic cases were run, each in a fresh, temporary Codex session. Neither the gold labels nor any other case's response was sent to the session under test. Raw outputs, predictions and the scoring report are stored in this directory.

## Results

| Metric | Result |
|---|---:|
| Returned with a valid format | 24/24 |
| Correct state judgment | 24/24 (100%) |
| Answer and minimal evidence set both match the original labels | 21/24 (87.5%) |
| Pairs with both members strictly correct | 9/12 (75%) |
| Unnecessary "insufficient information" on answerable questions | 0/18 |
| Definite answer given on insufficient-information questions | 0/6 |

## Interpreting the three deductions

C008, C010 and C012 all correctly answered "insufficient information" but cited only E2, whereas the original labels require both E1 and E2. They concern, respectively, a research direction limited to a workshop, considering a course, and considering a keyboard purchase.

These are evidence-set mismatches, not state-judgment errors. E2 by itself already states that no lasting research direction was chosen, or that something is merely being considered, so whether E1 must also be cited deserves independent review. This run keeps the original labels and scores; no answer was changed in the model's favor. These three cases should not be counted as confirmed memory or authorization failures.

## Conditions and scope

- Requested model: gpt-6-astra, invoked through Codex CLI 0.153.4 signed in to ChatGPT. The output events do not expose an independently verifiable underlying model snapshot, so what is recorded here is the request identifier.
- Reasoning effort, temperature and output limits were not set explicitly; the environment defaults were used. This must not be described as a fixed Medium or High experiment.
- Each case ran in its own temporary session with no session carried over, using the exported uniform prompt text. Codex adds its own system instructions, so this is not a pure API experiment with native system/user separation, and differences from results on another interface cannot be attributed to the model alone.
- Tool calls were prohibited in the request; tool behavior should still be audited in the saved events. There were no automatic retries and no outputs were selected by score.
- All 17 files of the original package match the release manifest hashes; validation of the 24 cases and the 8 software tests passed.
- This is a synthetic diagnostic set that supplies short records explicitly. It cannot show real long-term memory reliability, retrieval ability, real-world authorization safety, or an intervention effect. The case prompts already state the decision rules.
- The gold labels were originally written with AI assistance and have not been independently annotated by humans. This review is not an independent human validation either.
