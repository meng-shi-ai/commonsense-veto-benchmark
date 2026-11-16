# Stale Memory, Unverified Action

Code, prompts, raw model outputs and preregistrations behind the extended abstract
*Stale Memory, Unverified Action: Preregistered Pilot Evaluations of Whether Assistants Act on
Remembered Suggestions* (Meng Shi, Purdue University), submitted to Agent Evaluation Science (AES) 2026.
It is a follow-up to the single-model pilots v0.1–v0.5 in the [repository root](../).

**Question.** Assistants with long-term memory store their own recommendations alongside what users
said. Do models treat a remembered *suggestion* as a confirmed fact, and do tool-using agents act on it?

## Reproduce the paper's numbers

No API key needed; everything is recomputed from the saved outputs.

```bash
python3 reproduce_paper_numbers.py
python3 -m unittest test_memory_summary
```

| Paper claim | Where it comes from |
|---|---|
| Department fill: 14 of 15 memory-condition replies stated the course as fact (1 hedged); no-memory controls gave the number only | `review/deptfill_review_sample.csv` (human labels) + `review/deptfill_review_key.json` |
| Ambiguity: 80 of 208 named a single department (9 named both); GEOG 52 / HIST 2, reversed HIST 26 / GEOG 0 | `results/deptfill_ambig_01/` |
| Agent drop: 24/48 pass without lookup, 44/48 with lookup; per-model outcomes | `results/agent_drop_01/` |
| Veto: prompt rule 35/36 vague, 1/9 explicit without lookup; veto layer 36/36 and 18/18 | `results/veto_01/` |
| Direct memory questions: errors mostly in small open models (Qwen 2.5 7B, 4 of 5 use runs) | `python3 rescore_memsum.py results/cloud_memsum_01/*.raw.jsonl --rejudge results/cloud_memsum_01_rejudge.jsonl` |

## Experiments

| # | Experiment | Script | Results |
|---|---|---|---|
| 1 | Memory summary: is a suggested course recorded or used as enrolled? | `memory_summary_test.py` | `results/cloud_memsum_01/`, re-judged in `results/cloud_memsum_01_rejudge.jsonl` |
| 2 | Department fill: schedule with the department column cropped | `department_fill_test.py` | `results/deptfill_01/` |
| 3 | Ambiguity (preregistered): two remembered courses numbered 250 | `department_fill_test.py --memory ambiguous ambiguous_reversed` | `results/deptfill_ambig_01/` |
| 4 | Agent drop (preregistered): "drop that online course", with or without a lookup tool | `agent_drop_test.py` | `results/agent_drop_01/` |
| 5 | Veto comparison (preregistered): no veto, prompt rule, programmatic veto layer | `agent_drop_test.py --veto none prompt layer` | `results/veto_01/` |

Preregistrations: `PREREGISTRATION_ambiguity_01.md`, `PREREGISTRATION_agent_drop_01.md`,
`PREREGISTRATION_veto_01.md`. Re-scoring without API calls: `rescore_memsum.py`, `rescore_deptfill.py`;
`rejudge.py` re-runs the model judges. The synthetic schedule image sent to the models
can be regenerated with `python3 department_fill_test.py --save-image list.png`.

Each `*.raw.jsonl` starts with a settings line, then one record per call with the full prompt and
response. API errors and provider refusals are kept and recorded as `ERROR` / `REFUSED`, never as
model behavior.

## Running new calls

Needs Python 3 with `requests` (and `Pillow` for the screenshot). Set `OPENROUTER_API_KEY`, or point
`--base-url` at a local OpenAI-compatible server such as Ollama (`http://localhost:11434/v1`).
Model IDs are OpenRouter IDs as of October 16–17, 2026; providers can change models behind a name.

## Notes

- All course codes are fictional. Two codes were renamed one-to-one in this release;
  nothing else in the saved outputs was changed.
- Two further experiments from the same project (stale state and expired authorization in a DevOps
  agent) are not part of the paper and are not included here.
- Pilot scale: 3–5 runs per cell, one scenario family, single author. Read the results as signals,
  not established rates.

## License

Code (`*.py`) is released under the [MIT License](LICENSE). Data, prompts, results and documentation
are released under [CC BY 4.0](LICENSE-DATA). Please cite the extended abstract if you use them.
