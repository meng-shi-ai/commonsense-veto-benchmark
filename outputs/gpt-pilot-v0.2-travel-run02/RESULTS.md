# Live rerun with the travel-constraint extension

All 32 cases were run: the original 24 and the 8 new ones, each in an independent, temporary Codex session. The original 24 cases, their labels and the previous run's results were not overwritten.

| Scope | Correct answer judgment | Answer and evidence both strictly correct | Pairs with both members strictly correct |
|---|---:|---:|---:|
| Original 24, this rerun | 24/24 | 21/24 (87.5%) | 9/12 |
| New travel 8 | 8/8 | 8/8 (100%) | 4/4 |
| All 32 | 32/32 | 29/32 (90.625%) | 13/16 |

All 32 cases returned well-formed output, all 32 sessions completed, and the events contain no tool calls. No best-of selection was made and no failed case was retried automatically.

## What the travel cases test

The extension adds four minimal contrast pairs: a dryness requirement retained versus explicitly waived; dryness information missing versus a current room inspection on file; rain still falling at departure versus rain having stopped; current weather unknown versus the user directly observing rain now. Each case contains 5 to 7 dialogue events with distractor topics inserted (a museum, a charger, a bookstore, coffee). The case asks for the next recommended or verification action; merely restating the preference is not enough.

In these simplified scenarios the model applied the conditions correctly. This result does not contradict the user's real negative experience: the original Gemini chat is not available, and this simulation is not an exact reproduction of it. The cases supply the full short record, explicit decision rules and a limited set of options, which is markedly easier than a real long conversation with retrieval, missing hotel information and open-ended advice. The result supports no comparison between GPT and Gemini, and does not show that real travel advice is safe or reliable.

All names, prices, room inspections and route details are simulated. No real hotel or transit system was verified, and no causal link between rainfall and crowds or danger is asserted. The data are synthetic tests inspired by a user's own account.

## The three differences on the original cases

C008, C010 and C012 have correct state judgments but cite only E2, whereas the original labels require E1 and E2. This matches the previous run and remains a minimal-evidence-set question that deserves independent review. The original labels were not changed in this run.

The overall strict score moved from 87.5% in the previous run to 90.625% because eight fully passing cases were added and the denominator changed; it is not evidence of improved model performance. The three core metrics on the original 24 cases are identical to the previous run.

## Settings

The requested model was again gpt-6-astra, run through Codex CLI with the existing ChatGPT sign-in, invoked the same way as the previous run. Reasoning effort, temperature and output limits were not set explicitly; neither the actual reasoning level nor the underlying model snapshot is disclosed in the captured events. This therefore cannot be called a fixed Medium or High experiment, and the environment defaults are not guaranteed to stay constant. The chat-window setting was not read as an experimental parameter.

Each case used a new temporary session and received only the uniform task instructions and that case's record: no gold labels, pair labels or other cases' responses. The Codex environment still adds its own instructions, so this is not a pure API model test. Data hashes and run metadata are saved in `run_metadata.json`.

The first launch attempt failed because a temporary local permission had expired, before any model output was produced. That failed attempt is preserved in the neighboring `gpt-pilot-v0.2-travel` directory; after the permission was restored, all 32 cases were run from scratch in this directory. The operational failure was neither disguised as a model error nor removed from the record.

## Validation and reportable conclusions

The original 8 software tests were adapted to a variable number of cases and pass; the original 24 cases and their labels were verified unchanged; an ideal fixed output passes all 8 new cases; and a fixed program that gives the same answer to both members of every pair, ignoring the contrast, passes only 4/8 cases and 0/4 complete pairs. Fixed-program scores validate the scorer only.

What can be reported: travel-constraint application cases inspired by a user's experience were added to a versioned diagnostic set, and a live 32-case run was completed under a single GPT configuration, in which all 8 new cases passed. Novelty, generalization, real long-term memory reliability and the effect of any governance intervention have not been demonstrated.

Next steps: first review the annotations independently, then compare full-record against summary/retrieval conditions on new, unseen scenarios, and separately evaluate whether open-ended advice actually enforces the constraints. This run's scoring must not be changed after the fact to manufacture failures.

## Files

- `../memory-benchmark-v0.2-travel/README.md`: scenarios and answer explanations for the 8 new cases.
- `../memory-benchmark-v0.2-travel/cases.jsonl`: model-visible inputs for all 32 cases.
- `predictions.jsonl`: the 32 live outputs from this run.
- `all_32_report.json`, `original_24_report.json`, `travel_8_report.json`: separate scores for the three scopes.
- `discrepancies.json`: differences from the original labels.
- `C*.events.jsonl`: raw per-case execution events.
