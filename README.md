# commonsense-veto-benchmark
Exploratory benchmarks for AI agent memory, changing constraints, and authorization boundaries.

**Five versions of a small, synthetic diagnostic pilot—not evidence that a veto intervention works.** This repository collects the Memory Evidence Benchmark experiments under the CommonSense Veto project name. It asks whether an assistant distinguishes remembered information from currently applicable evidence, and advice from authorization to act.

The materials include authored cases, evaluator-only labels and rubrics, historical code, complete sanitized model outputs, operational failures, and AI-assisted reviews. No model evaluations were rerun to prepare this release. All reports and documentation are in English. The v0.3–v0.5 experiments were administered in Chinese, so their transcripts keep the original prompts and model responses verbatim, with English labels, scoring rationales and summaries.

**Start here:** [Methods and results](docs/METHODS_AND_RESULTS.md) · [Limitations](docs/LIMITATIONS.md) · [Reproduce the checks](docs/REPRODUCIBILITY.md) · [Public-data processing](docs/PUBLIC_DATA.md)

## What was observed

| Version | Evaluation unit and setting | Observed result |
| --- | --- | --- |
| v0.1 | 24 structured cases / 12 contrast pairs; fresh contexts | State judgments 24/24; exact answer-and-evidence criterion 21/24. Three evidence-set discrepancies need annotation review. |
| v0.2 | Original 24 plus 8 travel-constraint cases | State judgments 32/32; strict 29/32. The original 24 results did not improve; the denominator changed. |
| v0.3 | 16 open-ended prompts, one Medium and one High run | Each requested setting passed all four authored semantic criteria on 16/16 prompts. This does not establish equivalence between settings. |
| v0.4 | 50 generated conversation turns, **16 scored endpoints** | Main group: 14/14 endpoints passed all four criteria. Two supplementary endpoints chose the correct route but added debatable unsupported details; independent review is needed. |
| v0.5 | 6 synthetic roster cases with a callable local registration simulator | Four review-only cases made no drop attempt; two explicitly authorized cases successfully dropped only simulated LANG101. The historical SOC confusion was not reproduced. |

All runs requested `gpt-6-astra` through a Codex harness. This is a recorded request identifier, not independent verification of a server-side model snapshot. v0.1–v0.2 did not explicitly fix reasoning effort; v0.3 requested Medium/High; v0.4–v0.5 requested Medium and retained local configuration checks. The harness adds instructions beyond the case prompt.

The central finding is modest: in these small, often explicit synthetic settings, the tested configuration generally applied the supplied evidence correctly. The benchmark establishes an inspectable workflow and raises annotation questions. It does not establish real-world persistent-memory reliability, historical incident causality, cross-model superiority, or an intervention effect.

## Browse the evidence

| Material | Location |
| --- | --- |
| v0.1 cases, gold labels, scorer, software checks | [memory_benchmark_v01](memory_benchmark_v01/) |
| v0.1 real outputs and report | [gpt-pilot](outputs/gpt-pilot/) |
| v0.2 dataset and scorer | [travel dataset](outputs/memory-benchmark-v0.2-travel/) |
| v0.2 real outputs / startup failure | [completed run](outputs/gpt-pilot-v0.2-travel-run02/) / [failed startup](outputs/gpt-pilot-v0.2-travel/) |
| v0.3 prompts, rubric, both runs and reviews | [open-ended experiment](outputs/memory-benchmark-v0.3-open/) |
| v0.4 conversation graph, all turns, reviews and supplement | [multi-turn experiment](outputs/memory-benchmark-v0.4-friction/) |
| v0.5 prompts, rubric, simulator, calls and state transitions | [SOC experiment](outputs/memory-benchmark-v0.5-soc/) |
| Additional historical authoring and analysis scripts | [supplemental_scripts](supplemental_scripts/) |

The v0.1 README's “not yet evaluated” statement describes the original dataset-package release; real pilot results were subsequently stored separately in `outputs/gpt-pilot`. Read the version-specific reports in that historical context.

## Quick offline check

With Python 3.9+ and no third-party packages, run from the repository root:

```sh
python3 scripts/verify_release.py
python3 scripts/review_saved_results.py
```

The first checks public-file hashes, syntax, JSON and local Markdown links. The second re-scores saved v0.1/v0.2 predictions, summarizes recorded semantic reviews, and checks the v0.5 simulator logs and final states. **Neither calls a model, contacts an API, or assigns new independent semantic labels.**

See [reproducibility instructions](docs/REPRODUCIBILITY.md) before using the historical runners. They contain symbolic path placeholders after sanitization and are not a one-command portable live-evaluation package. Recorded outputs are kept separate from future runs.

## Next steps

The main limitation of v0.1–v0.5 is that a single model configuration (gpt-6-astra at Medium) helped author the cases, answered them, and assisted in scoring them. Near-ceiling scores in every version are therefore weak evidence about the failure that motivated this project. They may reflect cases that are easy for the model that wrote them, prompts that state the decision rules explicitly, and lenient grading within one model family. The next version is designed to address this:

1. **Separate authorship, evaluation and grading.** Cases will be written by humans or by a different model family. Responses will be collected from several model families, including the product family in which the original failure was observed and at least one smaller model. Grading will use a different model family plus blinded human review of a sample, with inter-rater agreement reported.
2. **Show that the benchmark discriminates before reporting results.** A version is informative only if at least one reasonable baseline fails some items. Ceiling scores across every model would mean the cases are too easy, not that the failure mode is absent.
3. **Remove explicit decision rules from prompts.** Models should infer whether information is stale, superseded or merely suggested, instead of being told the rule (such as the five-minute freshness window in v0.3).
4. **Move closer to real persistent memory.** Use real elapsed time across separate sessions, product memory features, and retrieval or summarization, instead of a complete record replayed in a fresh context.
5. **Keep a held-out test split private.** Public cases can enter future training data. A private split guards against contamination and tests generalization to unseen scenarios.
6. **Add an intervention comparison.** Compare behavior with and without a verification or veto mechanism, to test whether constructive friction actually reduces errors. The current versions cannot show this.

## Review status and rights

Labels and semantic reviews were AI-assisted and have not received independent human or blinded validation. Cases are public and synthetic; no hidden generalization test is claimed. No license has been selected for this release. Public availability should not be interpreted as an additional license grant.
