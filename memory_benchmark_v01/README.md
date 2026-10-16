# Memory Evidence Benchmark v0.1

**A synthetic diagnostic pilot for deciding which remembered facts still apply.**

This is the first runnable research prototype, released under the descriptive name Memory Evidence Benchmark.
The core question: an assistant must do more than recall what was said. It must track whose information it is, who confirmed it, when it holds, and whether later information actually overrides it.

**Status when this package was released: the dataset, prompt export, model adapter interface, scorer and tests were complete; no real model evaluation had been run yet.**
Real pilot results were recorded later in [`outputs/gpt-pilot`](../outputs/gpt-pilot/). Every score in `validation/` comes from hand-written labels or fixed program output; those scores test the software only and must not be reported as model results.

## A worked example

Earlier, the assistant said: "You could take SOC 205." Later, the user said: "I'm considering that course."
Question: is the user currently enrolled in the course?

The correct answer is "the available information is insufficient". A recommendation, a user's consideration, or the assistant's own inference must not be recorded as an enrollment.
The paired case changes only the later statement, to "I have officially registered for SOC 205", and the correct answer must then become "enrolled".

There are also controls in the opposite direction. The user explicitly says, "From now on, default to short replies until I say otherwise", and six months pass with no update.
The model should keep that preference rather than answer "unknown" merely because time has passed.

## What the 24 cases test

| Family | Cases | What should change the answer? |
|---|---:|---|
| Explicit update | 4 | Moving home versus merely visiting; changing versus retaining a preference |
| Durable versus temporary | 4 | A standing preference versus a dated, expired instruction |
| Suggestion versus commitment | 4 | Considering a course/purchase versus confirming it |
| Correction and provenance | 4 | User correction; a stale generated summary versus a fresh user statement |
| Subject attribution | 4 | The user versus a roommate/coworker, including quoted first-person speech |
| Authorization scope | 4 | Draft versus send; retained versus revoked permission |

The cases form 12 contrast pairs; within a pair, exactly one field of one event changes (its text or its speaker). 18 cases have a determinate answer and 6 have insufficient information.
All cases are original synthetic content. They draw on previously discussed failure types and use fictional places, courses and products.
They are not real data exported from private conversations, and they are not 24 failures that have been shown to occur in a model.

## Running on macOS

After downloading and unzipping, open Terminal and change into the `memory_benchmark_v01` folder. Python 3.9 or newer is required; there are no third-party dependencies.

```bash
python3 benchmark.py validate
python3 -m unittest -v
python3 benchmark.py demo --out demo_report.json
```

None of these commands calls a model or needs an API key. `demo` exercises the scorer only.

### Testing by hand, without code

Open `example_prompt.txt` and send the entire file to the model under test in a new chat.
It corresponds to case C010. The expected output is a short JSON object that separates the answer, the evidence and an insufficient-information decision.
The reference answer for this example is in `gold.jsonl`; never send that file to the model under test.

Do not run the test in a chat that has already seen the answer and then treat the result as an independent evaluation. If a chat product has additional memory enabled,
record that fact: it is a different experimental condition from an API setting with no external memory.

## Full evaluation

### Option A: export prompts and collect model responses

```bash
python3 benchmark.py export --split all --out prompts.jsonl
```

Each line contains an `id` and `messages`. Open a fresh context for each case and send its two messages,
without `gold.jsonl`, pair labels, or the answer to any earlier case.

Save the outputs as JSONL, one line per case, in this shape (a format example, not the reference answer for any case):

```json
{"id":"C001","prediction":{"decision":"answer","value":"Riverton","evidence_ids":["E1"]}}
```

Then score them:

```bash
python3 benchmark.py score --predictions predictions.jsonl --out report.json
```

### Option B: use your own model adapter

```bash
python3 benchmark.py run --adapter "python3 your_adapter.py" --out predictions.jsonl
python3 benchmark.py score --predictions predictions.jsonl --out report.json
```

The adapter reads one `{"id":...,"messages":[...]}` record from stdin and writes a bare JSON prediction to stdout.
The runner starts a separate process for each case and passes neither earlier outputs nor labels. If the adapter keeps persistent state of its own, it must disable and document it.
Logs go to stderr only. Non-zero exits, timeouts and non-JSON output are recorded as errors; failed cases are neither skipped nor retried automatically.
The runner refuses to overwrite an existing output file, so start each new run with a new file name.

The bundled `adapter_http.py` is an optional adapter for chat-completions-style HTTP services:

- `BENCHMARK_ENDPOINT`: the provider's full endpoint URL.
- `BENCHMARK_MODEL`: a model ID you actually have access to.
- `BENCHMARK_API_KEY`: set in the environment if the service requires one.
- `BENCHMARK_EXTRA_BODY`: an optional JSON object for sampling or output-length settings the service supports.

```bash
python3 benchmark.py run --adapter "python3 adapter_http.py" --limit 1 --out smoke_predictions.jsonl
```

This runs only once the variables above are set. It sends requests to the configured service and may incur costs; no such call was made in preparing this package.
The adapter supports only services that return `choices[0].message.content`; it is not a universal adapter for every provider's native API.
There are no automatic retries or redirects, and strict-JSON failures are counted as errors rather than silently repaired.
Validate service compatibility on a small sample before removing `--limit`. A single-case smoke output is not a full evaluation.

## Output format and scoring

The model may return only three fields: `decision`, `value` and `evidence_ids`.

- `decision="answer"`: `value` must be an exact string from the case's `allowed_values`.
- `decision="clarify"`: `value=null`. This means the information is insufficient for the question; it does not imply that a real product must interrupt the user.
- `evidence_ids`: the IDs of the events supporting the judgment. An unknown answer must still cite the relevant evidence that is insufficient to decide.

| Metric | Definition |
|---|---|
| State accuracy | Valid schema, correct decision and value / all selected cases |
| Evidence accuracy | Valid schema and exact match to one acceptable minimal evidence set / all cases |
| Strict accuracy | State and evidence both correct / all cases |
| Pair strict accuracy | Both members strictly correct / all selected pairs |
| Macro family strict accuracy | Unweighted average of the six family strict accuracies |
| Unnecessary clarification | Valid clarify outputs / all answerable cases |
| Unsupported answer | Valid answer outputs / all unknown cases |
| Coverage and schema validity | Returned records and valid predictions / all selected cases |

Missing or malformed responses stay in the accuracy denominators. Unknown or duplicate IDs raise an error.
Behavioral error rates count only well-formed errors, so they must be reported together with coverage and schema validity.
For example, a system that crashes on every case shows zero behavioral errors but also zero accuracy; that must not be read as safe.

Report `State accuracy` and `Strict accuracy` side by side. Human annotation of evidence sets may not be unique,
so format sensitivity in cited evidence sets should not be mistaken for a failure of semantic understanding. The current gold labels give minimal evidence sets.
If human review finds another sufficient set, it should be added uniformly before the version is frozen, never relaxed ad hoc for one model.

## Files

| File | Purpose |
|---|---|
| `cases.jsonl` | Model-visible case data; no labels |
| `gold.jsonl` | Evaluator-only labels, families, pairs, splits, annotation reasons |
| `build_dataset.py` | Reproducible case authoring source; not for model input |
| `benchmark.py` | Validation, prompt export, adapter execution, scoring and fixture demo |
| `adapter_http.py` | Optional HTTP service adapter; no model or credentials selected |
| `test_benchmark.py` | Checks missing records, invalid outputs, evidence, pairs, and label separation |
| `fixture_adapter.py` | Fixed-output plumbing check; not a language model |
| `example_prompt.txt` | One ready-to-paste model input |
| `DESIGN.md` | Research scope, limitations, literature and next experiment |
| `validation/` | Software validation artifacts, explicitly not model results |

## Experiment records

The development and pilot splits have 12 cases each, one pair per family, and no pair spans both splits.
This is a small, public, homogeneous diagnostic set: `pilot` is not an independent, hidden or uncontaminated test set.
Evaluating generalization requires creating new, unseen templates and scenarios after prompt tuning.

At a minimum, record: the exact model version, service and interface, time, prompt and data hashes, sampling settings,
maximum output length, any additional memory, whether the model has seen the examples or labels, the number of runs, and the failure and retry policy.
The metadata written by `run` covers only part of this and does not replace a complete experiment record.

**This version can test memory-evidence judgments in short contexts. It cannot yet show that a real system's persistent memory is reliable six months later.**
See `DESIGN.md` for the fuller research design.
