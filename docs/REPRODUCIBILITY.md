# Reproducibility

## Recheck existing results without a model

Use Python 3.9+ from the repository root. No package installation, credentials, account or network is required:

```sh
python3 scripts/verify_release.py
python3 scripts/review_saved_results.py
```

`verify_release.py` verifies the public manifest, parses Python source without executing historical runners, parses JSON/JSONL, and checks relative Markdown links. `review_saved_results.py` loads the original scorers to recompute v0.1/v0.2 scores from saved predictions; it counts the recorded semantic labels for v0.3/v0.4 and reconciles the v0.5 local-tool log with initial/final course state. It does not independently establish that subjective labels are correct. It writes no new model outputs.

The original scorer tests can also run offline:

```sh
python3 -B -m unittest discover -s memory_benchmark_v01 -p 'test_*.py'
python3 -B -m unittest discover -s outputs/memory-benchmark-v0.2-travel -p 'test_*.py'
```

Software fixtures and these checks are not model benchmarks. The public release was prepared without rerunning models.

## Collect a new structured run

The v0.1 and v0.2 `benchmark.py` programs resolve dataset files relative to their own location. Their `run` command accepts an external adapter reading one JSON prompt on stdin and returning one prediction JSON on stdout. See the [original adapter protocol](../memory_benchmark_v01/README.md). `adapter_http.py` is an optional chat-completions-shaped HTTP adapter, not a universal provider adapter. Credentials belong in the user's environment, never in a committed file.

Example, after configuring an adapter and intentionally choosing to make live calls:

```sh
mkdir -p new-runs
python3 memory_benchmark_v01/benchmark.py run --adapter 'python3 memory_benchmark_v01/adapter_http.py' --out new-runs/v01-predictions.jsonl
python3 memory_benchmark_v01/benchmark.py score --predictions new-runs/v01-predictions.jsonl --out new-runs/v01-score.json
```

This is a new run with its own model/service/parameters and may incur provider costs; it is not guaranteed to reproduce the historical model responses. Supply only case prompts, not gold labels. Keep every output and failure, use fresh contexts, and report actual configuration. Do not overwrite historical outputs or compare interfaces as if only the model had changed.

## Historical open-ended and multi-turn runners

The archived Python scripts document how the previous CLI experiments were orchestrated. Their machine paths have been replaced by `PUBLIC_REPO_ROOT`, `LOCAL_HOME`, `LOCAL_TMP` and `CODEX_EXECUTABLE`. These strings are symbolic markers, not automatically expanded environment variables. Some scripts also inspect a version-specific local state database. They are historical source, not tested portable runners.

Before adapting one for a future run: use a separate working copy and output directory; configure the installed executable and supported parameters; regenerate manifests for intentionally adapted input/tool files; record that adaptation separately. Never silently replace original frozen hashes to make old metadata appear valid. For v0.4, use new session identifiers and reproduce the graph of new/continue/fork branches. Public pseudonyms cannot resume old sessions. For v0.5, keep the fixture isolated locally and preserve actual call attempts and state transitions. Do not connect it to a registration portal.

Open-ended scoring additionally requires independent reviewers to read the rubric and saved answers. Recomputing sums of AI-authored labels is not a new independent replication.

## Integrity and provenance

`PUBLIC_MANIFEST.json` hashes current public files except itself; the ZIP has a separate checksum in the local delivery. `docs/sanitization-record.json` maps source-relative names and hashes to public hashes and lists edits without revealing identifiers. Historical manifests remain untouched apart from private-path sanitization and refer to the original byte representation. The original private archive is not included in this public repository.
