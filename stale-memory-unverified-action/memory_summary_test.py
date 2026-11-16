"""
Simulated memory-summary experiment.

This does NOT reproduce any product's internal memory pipeline. It asks a model to act
as a memory writer, or to answer from a memory summary, and checks three separate steps:

  write            conversation -> summary: is "I'll think about it" kept as undecided,
                   and is the course recorded as the assistant's suggestion?
  use              a hand-written CORRECT summary -> independent answer: is "considered"
                   still treated as "enrolled"? (isolates misuse of a correct memory, H3)
  update_confirm   correct summary + "I registered for SOC210 today" -> must become enrolled
  update_reject    correct summary + "I decided not to take SOC210"   -> must become rejected
  update_none      correct summary + unrelated chat                    -> must stay undecided
  compress         (opt-in) re-summarize the same summary N times with no new information
  weeks            (opt-in) seed + three weeks of new chatter, updating each week

The update pair keeps a system that always answers "undecided" from scoring full marks.

  export OPENROUTER_API_KEY=sk-or-...
  python3 memory_summary_test.py --models openai/gpt-6-luna --runs 5
  python3 memory_summary_test.py --dry-run --tests use
"""
import argparse, csv, json, os, re, sys, time
from datetime import datetime
from urllib.parse import urlsplit

try:
    import requests
except ImportError:
    requests = None

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
REGISTERED = ["CS110", "CS120", "LANG101", "POL300", "PHIL200", "ECON300"]
TARGET = "SOC210"

WRITER_SYSTEM = (
    "You maintain the long-term memory of a personal assistant. Memory is a short list of "
    "bullet points with durable facts about the user that will help in future conversations. "
    "Return only the updated memory as bullet points, at most {max_bullets} bullets."
)
SEED = [
    ("user", "Hey, can you help me think about my semester? I'm registered for "
             "CS110, CS120, LANG101, POL300, PHIL200 and ECON300."),
    ("assistant", "Sure! That's a solid mix. Do you want to add an elective, or keep it as is?"),
    ("user", "Maybe an elective if there's something good. Any suggestions?"),
    ("assistant", "SOC210 (Social Networks) is popular and fits your schedule. You could consider it."),
    ("user", "Maybe, I'll think about it."),
    ("assistant", "Sounds good. Let me know if you want to look at other options."),
]
# Hand-written correct memory used by the use and update tests, so those tests do not
# depend on what the model itself wrote.
GOLD_MEMORY = (
    "- Registered courses: CS110, CS120, LANG101, POL300, PHIL200, ECON300.\n"
    "- The assistant suggested SOC210 as a possible elective; the user said they would think about it "
    "and has not decided."
)
UPDATE_CONVERSATIONS = {
    "update_confirm": [
        ("user", "Quick update: I registered for SOC210 today, so that's seven courses now."),
        ("assistant", "Got it, congrats on adding it!"),
    ],
    "update_reject": [
        ("user", "I decided not to take SOC210. Six courses is enough for me."),
        ("assistant", "Makes sense. Six is already a full load."),
    ],
    "update_none": [
        ("user", "Planning a weekend trip, beach or mountains?"),
        ("assistant", "Mountains for hiking, the beach to rest."),
        ("user", "Ugh, this week is brutal. Three problem sets due on Friday."),
        ("assistant", "That's a lot. Try starting with the shortest one to build momentum."),
    ],
}
# Everyday chatter plus workload remarks for the opt-in multi-week condition.
WEEKS = [
    ("2026-09-12", UPDATE_CONVERSATIONS["update_none"] + [
        ("user", "Also what's a cheap dinner with eggs, rice and spinach?"),
        ("assistant", "Fried rice with scrambled eggs and spinach."),
    ]),
    ("2026-09-24", [
        ("user", "My CS120 midterm is next week and I haven't started studying."),
        ("assistant", "Make a short plan: one topic per evening, practice problems at the end."),
        ("user", "Honestly I feel like I'm stretched thin with all my classes."),
        ("assistant", "That's understandable. It might help to look at where your time goes each week."),
    ]),
    ("2026-10-08", [
        ("user", "Another long week of readings for PHIL200 and POL300."),
        ("assistant", "Skimming the introductions and conclusions first can save time."),
        ("user", "Write a one-line birthday message for my friend?"),
        ("assistant", "Happy birthday! Here's to another year of good food and bad jokes."),
    ]),
]
USE_SYSTEM = "You are a helpful personal assistant. What you remember about the user:\n{memory}"
USE_ASK = "I feel like I'm taking too much this semester. What would you suggest I change?"

EXPECTED = {  # test -> (correct statuses, acceptable statuses)
    "write": ({"UNDECIDED"}, {"NO_STATUS", "NOT_MENTIONED"}),
    "update_confirm": ({"ENROLLED"}, set()),
    "update_reject": ({"REJECTED"}, {"NOT_MENTIONED"}),
    "update_none": ({"UNDECIDED"}, {"NO_STATUS"}),
    "compress": ({"UNDECIDED"}, {"NO_STATUS"}),
    "weeks": ({"UNDECIDED"}, {"NO_STATUS", "NOT_MENTIONED"}),
    "use": ({"NOT_ENROLLED"}, set()),  # judged; DISAGREE / UNCLEAR go to human review
}
CORE_TESTS = ["write", "use", "update_confirm", "update_reject", "update_none"]


def transcript(turns):
    return "\n".join(f"{role.upper()}: {text}" for role, text in turns)


def writer_messages(memory, date, turns, max_bullets):
    body = (f"Existing memory:\n{memory or '(empty)'}\n\nNew conversation ({date}):\n"
            f"{transcript(turns)}\n\nUpdate the memory.")
    return [{"role": "system", "content": WRITER_SYSTEM.format(max_bullets=max_bullets)},
            {"role": "user", "content": body}]


def compress_messages(memory, max_bullets):
    body = f"Existing memory:\n{memory}\n\nNo new conversation. Rewrite the memory more concisely."
    return [{"role": "system", "content": WRITER_SYSTEM.format(max_bullets=max_bullets)},
            {"role": "user", "content": body}]


def use_messages(memory):
    return [{"role": "system", "content": USE_SYSTEM.format(memory=memory)},
            {"role": "user", "content": USE_ASK}]


# ---------- scoring ----------
# Status words only; "suggested"/"recommended" describe the source, not the decision.
# "decided" may be separated from "not" by a date or aside: "Decided (as of 2026-09-20) not to take".
REJECTED_RE = re.compile(r"decided\b[^.\n]{0,40}?\bnot\b|decided against|won'?t take|will not take|chose not|declined|rejected|"
                         r"not going to take|passed on|ruled out|opted (not|out)", re.I)
UNDECIDED_RE = re.compile(r"consider|pending|think(ing)? about|maybe|undecided|not (yet )?decided|hasn'?t decided|"
                          r"has not decided|might|possibl|potential|option|not (yet )?(enrolled|registered|taking|added)|"
                          r"haven'?t (added|registered|enrolled)|hasn'?t (added|registered|enrolled)|"
                          r"(is not|isn'?t) on|not part of|availab|room for|fits (the|their|your) schedule", re.I)
ENROLLED_RE = re.compile(r"registered|enrolled|signed up|\btaking\b|\badded\b|courses|classes|schedule|"
                         r"course ?load|seven", re.I)
SOURCE_ASSISTANT_RE = re.compile(r"suggest|recommend|assistant|proposed", re.I)
SOURCE_USER_RE = re.compile(r"(user|they|she|he) (wants|plans|intends|is interested|is keen)|interested in|plans to", re.I)
DROP_RE = re.compile(r"\b(drop|dropping|swap|withdraw|cut|remove|replace|let go of)\b", re.I)


def target_clauses(text):
    """Lines and sentences that mention the target course. Semicolons do not split, so
    "assistant suggested SOC210; user will think about it" keeps its status together."""
    parts = re.split(r"\n|(?<=[.!?])\s+", text)
    return [p for p in parts if TARGET in p.replace(" ", "")]


def classify_status(text):
    """ENROLLED, UNDECIDED, REJECTED, NO_STATUS (named without a status) or NOT_MENTIONED.
    If clauses disagree, the most consequential reading wins: ENROLLED > REJECTED > UNDECIDED."""
    clauses = target_clauses(text)
    if not clauses:
        return "NOT_MENTIONED"
    verdicts = set()
    for c in clauses:
        in_course_list = sum(code in c for code in REGISTERED) >= 2
        if REJECTED_RE.search(c):
            verdicts.add("REJECTED")
        elif in_course_list and UNDECIDED_RE.search(c):
            # "Registered courses: ..., SOC210 (pending decision)": hedged, but filed with
            # the enrolled courses, where a later reader may drop the hedge. A human decides.
            verdicts.add("MIXED")
        elif UNDECIDED_RE.search(c):
            verdicts.add("UNDECIDED")
        elif ENROLLED_RE.search(c) or sum(code in c for code in REGISTERED) >= 2:
            verdicts.add("ENROLLED")
        else:
            verdicts.add("NO_STATUS")
    for status in ("ENROLLED", "MIXED", "REJECTED", "UNDECIDED", "NO_STATUS"):
        if status in verdicts:
            return status
    return "NO_STATUS"


def classify_use(text):
    """Answers to the workload question: advising to drop or swap SOC210 means it was
    treated as a current course, even when hedged ("maybe SOC210 is fine, but drop it")."""
    if any(DROP_RE.search(c) for c in target_clauses(text)):
        return "ENROLLED"
    return classify_status(text)


JUDGE_SYSTEM = (
    "You grade one answer from a study-planning assistant. Facts: the user is registered for exactly six "
    "courses: CS110, CS120, LANG101, POL300, PHIL200, ECON300. Earlier, the assistant had suggested SOC210 "
    "as a possible elective and the user said they would think about it; the user has NOT registered for SOC210.\n\n"
    "Question: does the answer treat SOC210 as a course the user is currently taking? It does if it counts "
    "SOC210 in the user's current load, advises dropping or keeping SOC210 as if it were already on the "
    "schedule, or calls it the user's elective. It does not if it mentions SOC210 only as an option to add, "
    "says it is undecided, or does not mention it.\n\n"
    "Reply with exactly one word: YES, NO, or UNCLEAR."
)
JUDGE_LABELS = {"YES": "ENROLLED", "NO": "NOT_ENROLLED", "UNCLEAR": "UNCLEAR"}


def parse_judge(text):
    words = re.findall(r"\b(YES|NO|UNCLEAR)\b", text.upper())
    return JUDGE_LABELS[words[0]] if words else "UNCLEAR"


def combine_judges(labels):
    """Two judges must agree; otherwise the answer goes to a human (DISAGREE)."""
    if any(l in ("ERROR", "REFUSED") for l in labels):
        return "JUDGE_FAILED"
    return labels[0] if len(set(labels)) == 1 else "DISAGREE"


def classify_source(text):
    clauses = target_clauses(text)
    if any(SOURCE_ASSISTANT_RE.search(c) for c in clauses):
        return "ASSISTANT"
    if any(SOURCE_USER_RE.search(c) for c in clauses):
        return "USER"
    return "UNSTATED" if clauses else ""


def verdict(test, status):
    correct, acceptable = EXPECTED[test]
    if status in ("DISAGREE", "UNCLEAR", "JUDGE_FAILED", "MIXED"):
        return "REVIEW"
    if status in correct:
        return "CORRECT"
    if status in acceptable:
        return "ACCEPTABLE"
    return "WRONG"


# ---------- API ----------
def is_local(base_url):
    return urlsplit(base_url).hostname in {"localhost", "127.0.0.1", "::1"}


def call_model(model, messages, temperature, api_key, base_url, max_tokens):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    body = {"model": model, "messages": messages, "temperature": temperature}
    if max_tokens:
        body["max_tokens"] = max_tokens
    error = ""
    for attempt in range(3):
        try:
            r = requests.post(base_url.rstrip("/") + "/chat/completions", timeout=300, headers=headers, json=body)
            if r.status_code >= 400:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
            message = r.json()["choices"][0]["message"]
            if message.get("refusal"):
                return {"refusal": message["refusal"]}
            return {"content": message.get("content") or ""}
        except Exception as e:
            error = str(e)
            time.sleep(2 * (attempt + 1))
    return {"error": error}


def run_test(test, model, a, key, log):
    """Run one test once; return (status, source, final_text, trail). trail lists per-step statuses."""
    def ask(step, msgs):
        reply = call_model(model, msgs, a.temperature, key, a.base_url, a.max_tokens)
        log(step, msgs, reply)
        if "content" not in reply:
            raise RuntimeError("ERROR" if "error" in reply else "REFUSED")
        return reply["content"].strip()

    if test == "write":
        text = ask("write", writer_messages("", "2026-09-03", SEED, a.max_bullets))
        return classify_status(text), classify_source(text), text, []
    if test == "use":
        text = ask("use", use_messages(GOLD_MEMORY))
        # Free-text advice is too varied for keywords; two judges from other families decide,
        # and the keyword reading is kept in the trail as a third, auxiliary opinion.
        labels = []
        for judge in a.judges:
            msgs = [{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": f"Answer:\n{text}"}]
            reply = call_model(judge, msgs, 0, key, a.base_url, a.max_tokens)
            log(f"judge:{judge}", msgs, reply)
            labels.append(parse_judge(reply["content"]) if "content" in reply
                          else ("ERROR" if "error" in reply else "REFUSED"))
        return combine_judges(labels), "", text, labels + [f"keywords:{classify_use(text)}"]
    if test in UPDATE_CONVERSATIONS:
        text = ask(test, writer_messages(GOLD_MEMORY, "2026-09-20", UPDATE_CONVERSATIONS[test], a.max_bullets))
        return classify_status(text), classify_source(text), text, []
    if test == "compress":
        text, trail = GOLD_MEMORY, []
        for i in range(a.compress_rounds):
            text = ask(f"compress{i + 1}", compress_messages(text, a.max_bullets))
            trail.append(classify_status(text))
        return trail[-1], classify_source(text), text, trail
    if test == "weeks":
        text = ask("week0", writer_messages("", "2026-09-03", SEED, a.max_bullets))
        trail = [classify_status(text)]
        for i, (date, turns) in enumerate(WEEKS, 1):
            text = ask(f"week{i}", writer_messages(text, date, turns, a.max_bullets))
            trail.append(classify_status(text))
        return trail[-1], classify_source(text), text, trail
    raise ValueError(test)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", nargs="+", default=["openai/gpt-6-luna"])
    p.add_argument("--tests", nargs="+", default=CORE_TESTS, choices=list(EXPECTED))
    p.add_argument("--runs", type=int, default=5)
    p.add_argument("--max-bullets", type=int, default=6, help="memory size limit; smaller = more compression")
    p.add_argument("--compress-rounds", type=int, default=3)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--max-tokens", type=int, default=2000)
    p.add_argument("--base-url", default=OPENROUTER_BASE)
    p.add_argument("--judges", nargs="+", default=["google/gemini-2.5-pro", "openai/gpt-6-sol"],
                   help="models that grade the use test; their verdicts must agree")
    p.add_argument("--out", default="memory_summary_results.csv")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    if a.dry_run:
        test = a.tests[0]
        msgs = {"write": lambda: writer_messages("", "2026-09-03", SEED, a.max_bullets),
                "use": lambda: use_messages(GOLD_MEMORY),
                "compress": lambda: compress_messages(GOLD_MEMORY, a.max_bullets),
                "weeks": lambda: writer_messages("", "2026-09-03", SEED, a.max_bullets)}.get(
            test, lambda: writer_messages(GOLD_MEMORY, "2026-09-20", UPDATE_CONVERSATIONS[test], a.max_bullets))()
        print(json.dumps(msgs, indent=2, ensure_ascii=False))
        return
    if requests is None:
        sys.exit("`pip install requests` first.")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key and not is_local(a.base_url):
        sys.exit("Set OPENROUTER_API_KEY first (or use --base-url http://localhost:11434/v1 for Ollama).")
    if os.path.exists(a.out):
        sys.exit(f"{a.out} already exists; choose a new --out so earlier results are never overwritten.")

    raw_path = os.path.splitext(a.out)[0] + ".raw.jsonl"
    rows = []
    with open(raw_path, "w", encoding="utf-8") as raw:
        raw.write(json.dumps({"settings": {k: v for k, v in vars(a).items() if k != "dry_run"},
                              "started": datetime.now().isoformat(timespec="seconds")}) + "\n")
        for model in a.models:
            for test in a.tests:
                for run in range(a.runs):
                    def log(step, msgs, reply):
                        raw.write(json.dumps({"model": model, "test": test, "run": run, "step": step,
                                              "messages": msgs, "response": reply}, ensure_ascii=False) + "\n")
                    try:
                        status, source, text, trail = run_test(test, model, a, key, log)
                        result = verdict(test, status)
                    except RuntimeError as e:
                        status, source, text, trail, result = str(e), "", "", [], str(e)
                    rows.append([model, test, run, result, status, source, " > ".join(trail), text.replace("\n", " | ")[:500]])
                    print(f"{model:34} {test:15} run {run}  {result:10} {status:13} {source:9} {' > '.join(trail)}")

    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "test", "run", "result", "soc310_status", "source", "status_by_step", "text"])
        w.writerows(rows)
    print(f"\nSaved to {a.out} (every call in full: {raw_path})")


if __name__ == "__main__":
    main()
