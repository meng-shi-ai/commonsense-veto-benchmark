"""Re-score saved memory-summary runs with the current classifier (no API calls).

Write/update/compress/weeks are re-classified from the saved text; `use` verdicts come
from a sequential re-judge file when given (see rejudge.py), else from the original run.

    python3 rescore_memsum.py cloud_memsum_01/*.raw.jsonl --rejudge cloud_memsum_01_rejudge.jsonl
"""
import argparse, collections, json
import memory_summary_test as m

p = argparse.ArgumentParser()
p.add_argument("raw", nargs="+")
p.add_argument("--rejudge")
p.add_argument("--review-out", help="write cases needing a human decision to this .jsonl")
a = p.parse_args()

judged = collections.defaultdict(dict)
if a.rejudge:
    for line in open(a.rejudge, encoding="utf-8"):
        r = json.loads(line)
        judged[(r["model"], r["run"])][r["judge"]] = r["label"]

results, review, order, tests = collections.defaultdict(collections.Counter), [], [], []
for path in a.raw:
    steps = collections.defaultdict(list)
    for line in list(open(path, encoding="utf-8"))[1:]:
        r = json.loads(line)
        steps[(r["model"], r["test"], r["run"])].append(r)
    for (model, test, run), recs in steps.items():
        order += [model] if model not in order else []
        tests += [test] if test not in tests else []
        final = [r for r in recs if not r["step"].startswith("judge:")][-1]
        reply = final["response"]
        if "content" not in reply:
            results[(model, test)]["ERROR" if "error" in reply else "REFUSED"] += 1
            continue
        if test == "use":
            pair = judged.get((model, run)) or {r["step"][6:]: m.parse_judge(r["response"].get("content", ""))
                                                if "content" in r["response"] else "ERROR"
                                                for r in recs if r["step"].startswith("judge:")}
            status = m.combine_judges([pair.get(j, "ERROR") for j in ("google/gemini-2.5-pro", "openai/gpt-6-sol")])
        else:
            status = m.classify_status(reply["content"])
        verdict = m.verdict(test, status)
        results[(model, test)][verdict] += 1
        if verdict == "REVIEW":
            review.append({"model": model, "test": test, "run": run, "status": status, "text": reply["content"]})

short = {"CORRECT": "ok", "ACCEPTABLE": "~", "WRONG": "X", "REVIEW": "?", "ERROR": "E", "REFUSED": "R"}
tests = [t for t in m.CORE_TESTS + ["compress", "weeks"] if t in tests]
print(f"{'model':34}" + "".join(f"{t:>16}" for t in tests))
for model in order:
    print(f"{model:34}" + "".join(f"{' '.join(short[k] + str(v) for k, v in sorted(results[(model, t)].items())):>16}" for t in tests))
print(f"\n{len(review)} case(s) need a human decision")
if a.review_out:
    with open(a.review_out, "w", encoding="utf-8") as f:
        for item in review:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
