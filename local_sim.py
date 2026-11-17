"""
Local Benton simulator + checker
--------------------------------
Runs the fixed band scripts (run_band_scripts.SCRIPTS) against a Benton prompt
file using OpenAI directly (gpt-4o), instead of the Better Path AI portal.
This lets you iterate on the prompt before pasting it into the portal. The
portal wraps the fields in its own template, so ALWAYS confirm the final
prompt in the portal afterwards.

Usage:
    python local_sim.py avatars/benton/prompts/working.txt              all 6 scripts, 2 rounds
    python local_sim.py avatars/benton/prompts/working.txt --rounds 3 1 4 6

Writes local_sim_<timestamp>.txt (full transcripts + check report).
"""

import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

from config import OPENAI_API_KEY, OPENAI_BASE_URL
from run_band_scripts import SCRIPTS, BED_RE, IV_RE

MODEL = "gpt-4o"
TEMPERATURE = 0.7

BLOCK_RE = re.compile(r"^===== PASTE INTO: ([A-Z][A-Z >-]+?) =====\n(.*?)\n===== END[^\n]*=====", re.S | re.M)

SCENE_FIELDS = ["ROLE", "PERSONALITY", "CONTEXT", "OBJECTIVES", "TONE", "FORMAT", "KNOWLEDGE", "CONDITIONS"]

STAY = "Fine. I'll stay in this bed."
SETTLED = "I'll stay put and talk to the doctor."
MARKERS = ["You're not hearing how big this is.", "I really don't have the time for this.",
           STAY, SETTLED, "I'm getting out of this bed right now."]
LIMIT_RE = re.compile(r"(stay in bed|(keep|leave) (your|the) IV in)", re.I)
REASON_RE = re.compile(r"\b(fall|ankle|hurt|safe)", re.I)

# Messages (1-based index into the script's messages) that are escalating by design.
ESCALATING = {2: {2}, 3: {2, 4, 5, 6, 7, 8, 9}, 6: {3, 7, 14}}

EXPECTED = {
    1: ((3, 4, 4, 3), set()),
    2: ((3, 2, 1, 1), set()),
    3: ((1, 0, 0, 0), {"using therapeutic communication", "maintaining patient safety",
                       "establishing appropriate behavioral limits"}),
    4: ((3, 1, 0, 2), {"maintaining patient safety", "establishing appropriate behavioral limits"}),
    5: ((0, 0, 0, 0), {"maintaining patient safety", "establishing appropriate behavioral limits"}),
    6: ((3, 4, 4, 3), {"using therapeutic communication"}),
}
SETTLE_ALLOWED = {1, 6}


def load_fields(path):
    return {k.split("-> ")[-1]: v.strip() for k, v in BLOCK_RE.findall(open(path, encoding="utf-8").read())}


def chat(messages):
    for attempt in range(4):
        try:
            r = requests.post(f"{OPENAI_BASE_URL}/chat/completions",
                              headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                              json={"model": MODEL, "messages": messages, "temperature": TEMPERATURE},
                              timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))


def run_session(fields, num):
    script = SCRIPTS[num]
    scene_system = "\n\n".join(f"## {f.title()}\n{fields[f]}" for f in SCENE_FIELDS)
    opening = "Look, I need to get out of here. The whole thing is going to fall apart if I can't get to Washington."
    convo = [{"role": "assistant", "content": opening}]
    turns = []  # (nurse, benton, nurse_is_escalating)
    queue = list(enumerate(script["messages"], start=1))
    pending = None
    last_reply = opening
    while queue or pending:
        if pending:
            msg, idx = pending, None
            pending = None
        else:
            idx, msg = queue.pop(0)
            if msg == "__DESMOND__":
                asked = any(re.search(r"Desmond|my wife", t[1], re.I) for t in turns)
                msg = "I can call her for you." if asked else "Okay. I'll be back to check on you shortly."
        threat_before = bool(IV_RE.search(last_reply) or BED_RE.search(last_reply))
        esc = (idx in ESCALATING.get(num, set())) or (threat_before and not LIMIT_RE.search(msg))
        convo.append({"role": "user", "content": msg})
        reply = chat([{"role": "system", "content": scene_system}] + convo)
        convo.append({"role": "assistant", "content": reply})
        turns.append((msg, reply, esc))
        last_reply = reply
        if BED_RE.search(reply) and script["bed"]:
            pending = script["bed"]
        elif IV_RE.search(reply) and script["iv"]:
            pending = script["iv"]

    eval_system = "\n\n".join([fields["EVALUATION PREFIX"], "## Feedback Categories\n" + fields["FEEDBACK CATEGORIES"],
                               "## Evaluation Format\n" + fields["EVALUATION FORMAT"]])
    coaching = chat([{"role": "system", "content": eval_system}] + convo +
                    [{"role": "user", "content": "Please coach me"},
                     {"role": "system", "content": fields["EVALUATION SUFFIX"]}])
    return opening, turns, coaching


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower().replace("’", "'").replace("'", ""))


def check(num, turns, coaching):
    issues = []
    replies = [t[1] for t in turns]
    nurse = [t[0] for t in turns]
    # --- avatar
    iv_idx = [i + 1 for i, r in enumerate(replies) if IV_RE.search(r)]
    if len(iv_idx) != 1:
        issues.append(f"AVATAR IV threat at replies {iv_idx} (want exactly one)")
    beds = [i for i, r in enumerate(replies) if BED_RE.search(r)]
    if len(beds) > 2:
        issues.append(f"AVATAR {len(beds)} bed attempts (max 2)")
    for i in beds:
        if not turns[i][2]:
            issues.append(f"AVATAR bed attempt with no escalating trigger, after: {nurse[i][:70]!r}")
    for i, r in enumerate(replies):
        if re.search(r"lawyer", r, re.I):
            n_esc = sum(1 for t in turns[: i + 1] if t[2])
            if not turns[i][2] or n_esc < 2:
                issues.append(f"AVATAR lawyer demand without 2 escalations / right after neutral: {nurse[i][:70]!r}")
            break
    for i, r in enumerate(replies):
        if STAY in r and not (LIMIT_RE.search(nurse[i]) and REASON_RE.search(nurse[i])):
            issues.append(f"AVATAR stay-in-bed line with no limit, after: {nurse[i][:70]!r}")
        if r.strip() in MARKERS:
            issues.append(f"AVATAR bare marker reply: {r.strip()!r}")
    for line in (SETTLED,):
        n = sum(1 for r in replies if line.lower() in r.lower())
        if n > 1:
            issues.append(f"AVATAR said {line!r} {n} times (max 1)")
    settled = any(SETTLED.lower() in r.lower() for r in replies)
    if settled and num not in SETTLE_ALLOWED:
        issues.append("AVATAR settled line for a learner who should never settle")
    if not settled and num == 1:
        issues.append("AVATAR High never reached the settled line")
    if num in (2, 4) and not beds:
        issues.append("AVATAR no bed attempt after the ignored IV threat")
    if num in (3, 4, 5) and any(STAY in r for r in replies):
        issues.append("AVATAR stay-in-bed line for a learner who never set a limit")
    # --- coaching
    scores = [(c, int(n), int(m)) for c, n, m in re.findall(r"For ([A-Z][A-Za-z ]+?), you receive a (\d+) out of (\d+)", coaching)]
    got = tuple(s[1] for s in scores)
    total = re.search(r"Your total score is (\d+) out of 14", coaching)
    exp_scores, _ = EXPECTED[num]
    # Expected critical behaviors, worked out from what actually happened in this conversation.
    contra = re.compile(r"not true|isn't happening|not real|isn't real|no crisis|nobody (here )?is trying|"
                        r"don't think anyone|not sure that's really|feels real, but|not going to Washington", re.I)
    threat = re.compile(r"security|if you don't calm down|reason you're in this|that's why this happened|because you're sick", re.I)
    exp_crit = set()
    if sum(1 for m in nurse if contra.search(m)) >= 2 or any(threat.search(m) for m in nurse):
        exp_crit.add("using therapeutic communication")
    trig = [i for i, r in enumerate(replies) if IV_RE.search(r) or BED_RE.search(r)]
    p7 = any(i + 1 < len(nurse) and LIMIT_RE.search(nurse[i + 1]) for i in trig)
    if trig and not p7:
        exp_crit.add("maintaining patient safety")
    if not any(LIMIT_RE.search(m) and REASON_RE.search(m) for m in nurse):
        exp_crit.add("establishing appropriate behavioral limits")
    if len(scores) != 4:
        issues.append(f"COACH found {len(scores)} score lines")
    if not total:
        issues.append("COACH no total line")
    elif scores and int(total.group(1)) != sum(got):
        issues.append(f"COACH total {total.group(1)} != sum {sum(got)}")
    if got != exp_scores:
        issues.append(f"COACH scores {got} vs expected {exp_scores}")
    crit = set(re.findall(r"critical behavior for this scenario is ([a-z ]+), and it was missed", coaching))
    if crit != exp_crit:
        issues.append(f"COACH critical {sorted(crit)} vs expected {sorted(exp_crit)}")
    text = coaching.replace("“", '"').replace("”", '"')
    for para in re.split(r"\n\s*\n", text):
        sc = re.search(r"For ([A-Z][A-Za-z ]+?), you receive a (\d+) out of (\d+)", para)
        if not sc:
            continue
        lost = int(sc.group(3)) - int(sc.group(2))
        miss = re.search(r"[Yy]ou missed (.+?)\.(?:\s|$)", para)
        n_items = len([x for x in re.split(r",\s*(?:and\s+)?|\s+and\s+", miss.group(1)) if x.strip()]) if miss else 0
        if n_items != lost:
            issues.append(f"COACH {sc.group(1)}: missed list has {n_items} items but lost {lost} points")
    for prefix, q in re.findall(r'(could have said )?"([^"]+)"', text):
        if prefix or len(q) < 2:
            continue
        if not any(norm(q).strip() in norm(x) for x in nurse):
            issues.append(f"COACH quote not from nurse: {q[:60]!r}")
    for ex in re.findall(r'could have said "(.+?)"', coaching):
        if re.search(r"\b(but|however|actually|remember)\b", ex, re.I):
            issues.append(f"COACH example has banned word: {ex!r}")
    if re.search(r"^[A-Z][A-Z ,\-]{8,}$", coaching, re.M):
        issues.append("COACH printed a capital-letter heading")
    return got, sorted(crit), issues


def main():
    args = sys.argv[1:]
    path = args.pop(0)
    rounds = 2
    if "--rounds" in args:
        i = args.index("--rounds"); rounds = int(args[i + 1]); del args[i:i + 2]
    nums = [int(a) for a in args] or sorted(SCRIPTS)
    fields = load_fields(path)
    jobs = [(r, n) for r in range(1, rounds + 1) for n in nums]
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda j: (j, run_session(fields, j[1])), jobs))
    out, summary = [], []
    for (r, n), (opening, turns, coaching) in results:
        got, crit, issues = check(n, turns, coaching)
        name = SCRIPTS[n]["name"]
        summary.append(f"R{r} {n} {name:15} scores {got} total {sum(got) if got else '-'} | crit {crit} | {len(issues)} issue(s)")
        summary += [f"      - {x}" for x in issues]
        out.append(f"\n{'=' * 80}\nROUND {r} - SCRIPT {n} {name}\n{'=' * 80}\nBenton: {opening}")
        for msg, reply, esc in turns:
            out.append(f"\nNurse{' [E]' if esc else ''}: {msg}\nBenton: {reply}")
        out.append(f"\nNurse: Please coach me\nCOACH:\n{coaching}\n\nISSUES:\n" + "\n".join(issues or ["none"]))
    report = "\n".join(summary)
    fn = f"local_sim_{datetime.now():%Y%m%d_%H%M%S}.txt"
    open(fn, "w", encoding="utf-8").write(f"Prompt: {path}\n\n{report}\n" + "\n".join(out))
    print(report)
    print(f"\nFull transcripts: {fn}")


if __name__ == "__main__":
    main()
