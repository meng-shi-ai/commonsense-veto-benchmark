"""Re-judge saved `use` answers one at a time (no new answers from the models under test).

Use this when judge calls failed, e.g. on rate limits. It reads .raw.jsonl files written by
memory_summary_test.py and appends every judge call and verdict to --out.

    python3 rejudge.py cloud_memsum_01/*.raw.jsonl --out cloud_memsum_01_rejudge.jsonl
"""
import argparse, json, os, sys, time

import memory_summary_test as m


def judge_once(judge, answer, key, max_tokens, pause):
    msgs = [{"role": "system", "content": m.JUDGE_SYSTEM}, {"role": "user", "content": f"Answer:\n{answer}"}]
    for attempt in range(6):
        reply = m.call_model(judge, msgs, 0, key, m.OPENROUTER_BASE, max_tokens)
        if "error" not in reply or "429" not in reply["error"]:
            return msgs, reply
        time.sleep(pause * (attempt + 2))  # rate-limited: back off and try again
    return msgs, reply


def main():
    p = argparse.ArgumentParser()
    p.add_argument("raw", nargs="+")
    p.add_argument("--judges", nargs="+", default=["google/gemini-2.5-pro", "openai/gpt-6-sol"])
    p.add_argument("--out", required=True)
    p.add_argument("--pause", type=float, default=5.0, help="seconds between calls")
    p.add_argument("--max-tokens", type=int, default=2000)
    a = p.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("Set OPENROUTER_API_KEY first.")
    if os.path.exists(a.out):
        sys.exit(f"{a.out} already exists; choose a new --out.")

    answers = []
    for path in a.raw:
        for line in list(open(path, encoding="utf-8"))[1:]:
            r = json.loads(line)
            if r["test"] == "use" and r["step"] == "use" and "content" in r["response"]:
                answers.append((r["model"], r["run"], r["response"]["content"]))
    with open(a.out, "w", encoding="utf-8") as out:
        for i, (model, run, answer) in enumerate(answers, 1):
            labels = []
            for judge in a.judges:
                msgs, reply = judge_once(judge, answer, key, a.max_tokens, a.pause)
                label = (m.parse_judge(reply["content"]) if "content" in reply
                         else "ERROR" if "error" in reply else "REFUSED")
                labels.append(label)
                out.write(json.dumps({"model": model, "run": run, "judge": judge, "label": label,
                                      "messages": msgs, "response": reply}, ensure_ascii=False) + "\n")
                out.flush()
                time.sleep(a.pause)
            print(f"[{i}/{len(answers)}] {model:34} run {run}  {labels} -> {m.combine_judges(labels)}", flush=True)


if __name__ == "__main__":
    main()
