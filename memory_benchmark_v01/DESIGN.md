# Research design and limits

Working title: Memory Evidence Benchmark v0.1. The name is descriptive, not a novelty claim.
Prepared for Meng, September 2026. No actual language-model results are included.

## Question and proposed contribution

When a conversational assistant answers using remembered personal information, can it identify
which statement is applicable to the current subject, time, and scope, while preserving still-valid
facts and separating user confirmation from its own inference?

The candidate contribution is a tightly controlled set of contrast pairs for evidence applicability.
It is not simply another recall leaderboard. It must still be compared against existing memory
benchmarks before any claim of novelty is justified.

The immediate artifact is a probe for the **reading and decision stage with supplied evidence**.
The whole record is deliberately visible. Dates express narrative time, not actual elapsed time
or measured persistence. Cases contain two or three short events; this is not a long-context test.

## Existing work checked

1. [LongMemEval (Wu et al., 2024)](https://arxiv.org/abs/2410.10813)
   explicitly covers information extraction, multi-session reasoning, temporal reasoning,
   knowledge updates and abstention. Updates and abstention are already established targets;
   they cannot by themselves be presented as the novelty here.
2. [LoCoMo (Maharana et al., 2024)](https://arxiv.org/abs/2402.17753)
   evaluates very long conversational memory through question answering, event summarization,
   and multimodal dialogue generation. This small case set is not a substitute for that scale.
3. [LoCoMo-Plus (Li et al., 2026)](https://arxiv.org/abs/2602.10715)
   examines retaining and applying latent constraints when later cues differ semantically,
   with constraint consistency as an evaluation focus. This overlaps the broader motivation
   of appropriately applying remembered context.
4. [LongMemEval-V2 (2026)](https://arxiv.org/html/2605.12493v1)
   extends memory evaluation into agentic environments, including dynamic state tracking
   and premise awareness. Any later claim about memory-guided agent actions must compare
   with this work, not only the 2024 benchmarks.

These are positioning references, not an exhaustive related-work review. No examples, labels,
scores or code were imported from them. The proposed distinct emphasis on minimal changes
to authority, subject and validity scope remains a hypothesis to investigate.

## Labeling assumptions

- Use only the supplied record as of the query date. Unreported real-world changes are out of scope.
- An explicit current self-report can replace an older self-report about the same field.
- An explicitly standing preference remains applicable absent a relevant update.
- A temporary instruction cannot establish a current standing preference after its stated period.
- An assistant suggestion, summary or inference cannot create a user commitment.
- A summary's creation date is not the effective date of a new underlying fact.
- First-person speech inside a quotation belongs to the quoted speaker.
- A record that does not establish a proposition does not automatically establish its negation.
- Authorization cases classify the supplied permission only; no email is sent and no real-world
  recipient identity, credential access, legal permission, or tool capability is inferred.

The labels are manually authored by the same assistant that wrote the cases. There has been no
independent annotation or inter-rater reliability study. Ambiguities should be resolved before a
frozen comparison run. Exact evidence-set grading is intentionally exposed separately from state accuracy.

## Conditions for a useful first experiment

1. Freeze this version and record its hashes. Human-review the 24 items before drawing conclusions.
2. Run each model in independent contexts, with no gold labels or prior case responses in the prompt.
3. Use the same record and prompt format across models. Record exact model and sampling settings.
4. Inspect all errors, including formatting failures, evidence-only failures, and unnecessary uncertainty.
5. Repeat stochastic runs with fresh contexts. Report all runs, not the best result; do not treat
   repeated samples of the same 24 templates as independent new cases.
6. Report per-family counts and both-member pair success. With only four items per family,
   do not claim statistical superiority from a small score difference.

No paid provider calls have been made in this deliverable. `adapter_http.py` is an optional,
provider-configured interface scaffold. A fixed fixture adapter tests software flow only.

## What can and cannot be concluded

Passing indicates success at a small, explicitly instructed, multiple-choice state-and-evidence task.
Failing a reviewed pair can reveal a concrete diagnostic weakness under this protocol.

Passing does not establish real long-term memory reliability, useful human-centered dialogue,
correct retrieval, faithful summaries, successful actions, or preservation of human autonomy.
The prompt teaches the intended rules; this measures behavior under guidance, not unprompted defaults.
The choice vocabulary and synthetic short histories can make the task too easy or create shortcuts.
No hidden test set, paraphrase robustness, distributional breadth or novelty is established.

## Next version after first observations

- Add independently reviewed unseen templates and realistic distractor sessions; split by template
  and topic as well as pair. Do not merely rename entities to manufacture an independent test set.
- Cross validity type with elapsed narrative time; separate memory-summary recency from fact recency.
- Compare full history, a fixed-budget generated summary, and a retrieval pipeline while keeping
  the downstream question and labels constant. This separates loss at write/retrieve/read stages.
- Add stale summaries as distractors alongside original user evidence, including partial updates
  and unresolved conflicting evidence, rather than making recency alone a winning rule.
- Evaluate natural-language actions and advice separately with blinded human review of supported
  assertions, user intent and burden of clarification. Do not claim this structured score measures those.
- Test an intervention on a frozen unseen set. Compare gain in correct updates against loss of
  valid retained information and increase in unnecessary questions. Establish a cost/latency budget.

The most useful initial result is an inspectable failure pair and a narrowly justified intervention,
not a high percentage from a tiny public test set.
