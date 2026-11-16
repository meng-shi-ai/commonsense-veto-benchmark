"""Recompute every number in the AES 2026 extended abstract from the saved raw outputs (no API calls).

    python3 reproduce_paper_numbers.py
"""
import collections, csv, glob, json

import department_fill_test as t


def records(pattern):
    for path in sorted(glob.glob(pattern)):
        for line in list(open(path, encoding="utf-8"))[1:]:
            yield json.loads(line)


def department_fill():
    """Human labels on the cropped-display sample: A = stated as fact, B = marked inferred, C = no department."""
    key = json.load(open("review/deptfill_review_key.json", encoding="utf-8"))
    labels = collections.Counter()
    for row in csv.DictReader(open("review/deptfill_review_sample.csv", encoding="utf-8")):
        label = (row["human_epistemic"] or row["human_content"]).strip()
        if label:
            labels[("memory" if key[row["id"]]["memory"] != "none" else "no-memory", label)] += 1
    print("Department fill, human-labelled replies:")
    for k in sorted(labels):
        print(f"  {k[0]:10} {k[1]}: {labels[k]}")


def ambiguity():
    counts = collections.Counter()
    for r in records("results/deptfill_ambig_01/*.raw.jsonl"):
        if "content" not in r["response"]:
            continue
        named = {m.group(1) for m in t.DEPT_BEFORE.finditer(r["response"]["content"])} & {"GEOG", "HIST"}
        counts[(r["memory"], "+".join(sorted(named)) or "none")] += 1
    total = sum(counts.values())
    single = sum(v for (_, d), v in counts.items() if d in ("GEOG", "HIST"))
    both = sum(v for (_, d), v in counts.items() if d == "GEOG+HIST")
    print(f"\nAmbiguity: {total} replies, {single} named a single department ({single / total:.0%}), {both} named both")
    for order in ("ambiguous", "ambiguous_reversed"):
        print(f"  {order:19} GEOG {counts[(order, 'GEOG')]}  HIST {counts[(order, 'HIST')]}")


def agent_drop():
    by_model = collections.defaultdict(collections.Counter)
    for r in records("results/agent_drop_01/*.raw.jsonl"):
        by_model[(r["tools"], r["model"])][r["outcome"]] += 1
    print("\nAgent drop (vague ask, no veto), outcomes per model:")
    for tools in ("no_lookup", "with_lookup"):
        passed = total = 0
        for (tl, model), c in sorted(by_model.items()):
            if tl != tools:
                continue
            ok = c["ASKED"] + c["VERIFIED_DROP"]
            passed, total = passed + ok, total + sum(c.values())
            print(f"  {tools:11} {model:32} {dict(c)}")
        print(f"  {tools}: pass {passed}/{total}")


def veto():
    cells = collections.defaultdict(collections.Counter)
    for r in records("results/veto_01/*.raw.jsonl"):
        cells[(r["veto"], r["ask"], r["tools"])][r["outcome"]] += 1
    print("\nVeto comparison (three models, 3 runs per cell):")
    for k in sorted(cells):
        print(f"  veto={k[0]:6} ask={k[1]:8} tools={k[2]:11} {dict(cells[k])}")


if __name__ == "__main__":
    department_fill()
    ambiguity()
    agent_drop()
    veto()
