"""
Elaine V2 local simulator + checker
-----------------------------------
Runs the fixed band scripts (band_scripts.SCRIPTS) against an Elaine
prompt file using OpenAI directly, instead of the Better Path AI portal. This
lets you test the prompt before pasting it in. The portal wraps the fields in
its own template, so ALWAYS confirm the final prompt in the portal afterwards.

    python avatars/elaine/tools/local_sim.py avatars/elaine/prompts/portal_v1.txt
    python avatars/elaine/tools/local_sim.py avatars/elaine/prompts/portal_v1.txt --rounds 2 1 3

Writes elaine_sim_<timestamp>.txt (full transcripts + check report).

Every check below is a deterministic read of the prompt's own rules, so a
FAIL is the prompt contradicting itself or the model ignoring it - not an
opinion about whether the coaching felt fair.
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root and core/ on the import path, so this runs as
# `python avatars/elaine/tools/local_sim.py` from the repo root. config/settings.py and personas/
# live at the root; the shared engine lives in core/.
import pathlib as _pathlib, sys as _sys
_ROOT = _pathlib.Path(__file__).resolve().parents[3]
_sys.path[:0] = [str(_ROOT), str(_ROOT / "core")]
# --------------------------------------------------------------------------

import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

from config import AVATAR_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL
from band_scripts import CAREGIVER, SCRIPTS

MODEL = AVATAR_MODEL

BLOCK_RE = re.compile(r"^===== PASTE INTO: ([A-Z][A-Z >-]+?) =====\n(.*?)\n===== END[^\n]*=====", re.S | re.M)
SCENE_FIELDS = ["ROLE", "PERSONALITY", "CONTEXT", "OBJECTIVES", "TONE", "FORMAT", "KNOWLEDGE", "CONDITIONS"]

WASH_RE = re.compile(r"\b(shower|bath|bathe|bathing|wash|washing|washed|water|bathroom|"
                     r"clean up|cleaned up|freshen up|freshened up|washcloth|towel)\b", re.I)
ALREADY_RE = re.compile(r"\balready\b|\bdid that\b|\bthis morning\b|\bi washed\b|\bi had one\b|\bi've had\b", re.I)
FEAR_RE = re.compile(r"\b(scare|scared|scary|frighten|frightened|afraid|drown|slip|deep|cold|nervous|face)\b", re.I)
YES_RE = re.compile(r"\b(i'?ll come with you|i'?ll go with you|let'?s go)\b", re.I)
LOT_RE = re.compile(r"that'?s a lot|that is a lot", re.I)
HELPER_RE = re.compile(r"how can i help|what can i do for you|is there anything else|you could try|"
                       r"that was a good|well done|good job", re.I)
# Scene rules allow only letters, commas, periods, question marks (apostrophes
# are explicitly fine - "Contractions are good").
BANNED_CHARS = {"…": "ellipsis", "...": "ellipsis", "—": "em dash", "–": "en dash",
                " - ": "dash", "!": "exclamation mark", ";": "semicolon", ":": "colon",
                "(": "parenthesis", ")": "parenthesis", "[": "bracket", "]": "bracket",
                "*": "asterisk", '"': "quote", "“": "quote", "”": "quote"}

# ---- the prompt's own ITEMS: fixed recap phrase -> level, in item order ----
PHRASES = {
    "Empathy": [
        {"Did": "you named how i felt", "Partly": "you corrected me after naming my feeling",
         "Missed": "you passed over my feelings"},
        {"Did": "you calmed my fear", "Partly": "you reassured me about something else",
         "Missed": "you brushed past my fear"},
        {"Did": "i felt safe with you", "Partly": "i stayed a little guarded",
         "Missed": "i stayed tense"},
    ],
    "CARES": [
        {"Did": "you answered my real worry", "Partly": "you half answered my worry",
         "Missed": "you repeated the same ask"},
        {"Did": "you connected with me first", "Partly": "you only greeted me first",
         "Missed": "you started with washing"},
        {"Did": r"you built on .+", "Partly": r"you touched on .+",
         "Missed": "you skipped my own life"},
    ],
    "Communication": [
        {"Did": "you spoke short and calm", "Partly": "you were sometimes too much for me",
         "Missed": "you gave me orders"},
        {"Did": "you offered a small step", "Partly": "you said go slowly with no step",
         "Missed": "you offered no small step"},
        {"Did": "i said yes", "Partly": "i took a small step", "Missed": "i kept saying no"},
    ],
}
CATEGORIES = ["Empathy", "CARES", "Communication"]

# ---- the prompt's own POINTS table, copied row for row ----
POINTS = {
    ("Did", "Did", "Did"): 10, ("Did", "Did", "Partly"): 8, ("Did", "Did", "Missed"): 7,
    ("Did", "Partly", "Did"): 8, ("Did", "Partly", "Partly"): 6, ("Did", "Partly", "Missed"): 5,
    ("Did", "Missed", "Did"): 7, ("Did", "Missed", "Partly"): 5, ("Did", "Missed", "Missed"): 4,
    ("Partly", "Did", "Did"): 8, ("Partly", "Did", "Partly"): 6, ("Partly", "Did", "Missed"): 5,
    ("Partly", "Partly", "Did"): 6, ("Partly", "Partly", "Partly"): 4, ("Partly", "Partly", "Missed"): 3,
    ("Partly", "Missed", "Did"): 5, ("Partly", "Missed", "Partly"): 3, ("Partly", "Missed", "Missed"): 2,
    ("Missed", "Did", "Did"): 6, ("Missed", "Did", "Partly"): 4, ("Missed", "Did", "Missed"): 3,
    ("Missed", "Partly", "Did"): 4, ("Missed", "Partly", "Partly"): 2, ("Missed", "Partly", "Missed"): 1,
    ("Missed", "Missed", "Did"): 3, ("Missed", "Missed", "Partly"): 1, ("Missed", "Missed", "Missed"): 0,
}
FIXED_REASON = {
    "Empathy": "i did not hear my feelings acknowledged",
    "CARES": "my worry was not answered",
    "Communication": "i was not given calm, small steps",
}


def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ',?.]", " ", s.lower())).strip()


def load_fields(path):
    return {k.split("-> ")[-1]: v.strip() for k, v in BLOCK_RE.findall(open(path, encoding="utf-8").read())}


def chat(messages):
    for attempt in range(4):
        try:
            r = requests.post(f"{OPENAI_BASE_URL}/chat/completions",
                              headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                              json={"model": MODEL, "messages": messages}, timeout=180)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))


def run_session(fields, num):
    script = SCRIPTS[num]
    scene_system = "\n\n".join(f"## {f.title()}\n{fields[f]}" for f in SCENE_FIELDS)
    opening = "Hello, what do you want?"
    convo = [{"role": "assistant", "content": opening}]
    turns = []
    for msg in script["messages"]:
        convo.append({"role": "user", "content": msg})
        reply = chat([{"role": "system", "content": scene_system}] + convo)
        convo.append({"role": "assistant", "content": reply})
        turns.append((msg, reply))

    eval_system = "\n\n".join([fields["EVALUATION PREFIX"],
                               "## Feedback Categories\n" + fields["FEEDBACK CATEGORIES"],
                               "## Evaluation Format\n" + fields["EVALUATION FORMAT"]])
    coach_msgs = [{"role": "system", "content": eval_system}] + convo + \
                 [{"role": "user", "content": "Please coach me"},
                  {"role": "system", "content": fields["EVALUATION SUFFIX"]}]
    coaching = chat(coach_msgs)
    followup = chat(coach_msgs + [{"role": "assistant", "content": coaching},
                                  {"role": "user", "content": script["followup"]}])
    return opening, turns, coaching, followup


def sentences(text):
    return [s for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s.strip()]


def check_scene(num, turns):
    """Scene-rule checks. Returns (fails, warns)."""
    fails, warns = [], []
    script = SCRIPTS[num]
    straight = lambda t: t.replace("\u2019", "'").replace("\u2018", "'")
    replies = [straight(r) for _, r in turns]
    nurse = [straight(n) for n, _ in turns]

    for i, r in enumerate(replies, 1):
        n_sent, n_words, n_chars = len(sentences(r)), len(r.split()), len(r)
        if n_sent > 2:
            fails.append(f"reply {i}: {n_sent} sentences (max 2): {r[:80]!r}")
        if n_words > 28:
            fails.append(f"reply {i}: {n_words} words (max 28)")
        if n_chars > 160:
            fails.append(f"reply {i}: {n_chars} characters (max 160)")
        for ch, label in BANNED_CHARS.items():
            if ch in r:
                fails.append(f"reply {i}: banned {label} {ch!r}: {r[:70]!r}")
                break
        if re.search(rf"\b{CAREGIVER}\b", r):
            fails.append(f"reply {i}: said the caregiver's name: {r[:70]!r}")
        if HELPER_RE.search(r):
            fails.append(f"reply {i}: helper / customer-service line: {r[:70]!r}")
        if "\n" in r.strip():
            fails.append(f"reply {i}: more than one line")

    # first three words never repeat
    starts = {}
    for i, r in enumerate(replies, 1):
        k = " ".join(norm(r).split()[:3])
        if k and k in starts:
            fails.append(f"reply {i}: starts with the same three words as reply {starts[k]} ({k!r})")
        starts[k] = i

    # questions: never two in a row, at most 1 in 4
    q = [i for i, r in enumerate(replies) if "?" in r]
    for a, b in zip(q, q[1:]):
        if b == a + 1:
            fails.append(f"replies {a+1} and {b+1}: questions on two turns in a row")
    if replies and len(q) > max(1, round(len(replies) / 4)):
        warns.append(f"{len(q)} questions in {len(replies)} turns (rule: at most 1 in 4)")

    # washing must come from the caregiver first
    first_wash = next((i for i, n in enumerate(nurse) if WASH_RE.search(n)), None)
    for i, r in enumerate(replies):
        if WASH_RE.search(r) and (first_wash is None or i < first_wash):
            fails.append(f"reply {i+1}: raised washing before the caregiver did: {r[:70]!r}")
            break

    # stage order after the first washing word
    if first_wash is not None:
        r1 = replies[first_wash]
        if not ALREADY_RE.search(r1):
            fails.append(f"Stage 1: first reply after a washing word does not say she already "
                         f"washed: {r1[:80]!r}")
        if FEAR_RE.search(r1) and not ALREADY_RE.search(r1):
            fails.append(f"Stage 3 fear arrived at Stage 1: {r1[:80]!r}")
        if len(replies) > first_wash + 1:
            r2 = replies[first_wash + 1]
            if YES_RE.search(r2):
                fails.append("agreed one reply after washing came up (Stage 5 needs 4 stages first)")

    # the yes
    said_yes = [i + 1 for i, r in enumerate(replies) if YES_RE.search(r)]
    agreed_loosely = [i + 1 for i, r in enumerate(replies)
                      if re.search(r"\b(okay|alright|all right|fine)\b.*\b(come|go|shower)\b", r, re.I)]
    if script["yes"] and not said_yes:
        fails.append("no yes: the YES CHECK should have passed for this band")
    if not script["yes"] and said_yes:
        fails.append(f"agreed at reply {said_yes} but this band should never get a yes")
    if not script["yes"] and not said_yes and agreed_loosely:
        warns.append(f"reply {agreed_loosely} reads like agreement without the required yes wording")
    if said_yes and first_wash is not None:
        gap = said_yes[0] - first_wash
        if not 5 <= gap <= 8:
            fails.append(f"PACE: yes came {gap} replies after washing came up (rule says 5 to 8)")
    benefits_at = script.get("benefits_at")
    if said_yes and benefits_at and said_yes[0] < benefits_at:
        fails.append(f"YES CHECK: agreed at reply {said_yes[0]} but the caregiver had not named "
                     f"two good things washing would do until turn {benefits_at}")
    if said_yes and len(said_yes) > 1:
        fails.append(f"Stage 6: repeated the yes at replies {said_yes} instead of moving on")

    # "that is a lot" fires on 3+ sentence turns and never on short ones
    for i, (n, r) in enumerate(turns, 1):
        long_turn = len(sentences(n)) >= 3
        said_lot = bool(LOT_RE.search(r))
        if long_turn and not said_lot:
            warns.append(f"turn {i}: caregiver said {len(sentences(n))} sentences, she did not "
                         f"say that is a lot")
        if not long_turn and said_lot:
            fails.append(f"turn {i}: said that is a lot to a {len(sentences(n))}-sentence turn")
    return fails, warns


def parse_recap(line, category):
    """Maps a recap line onto the three item levels. None if it does not match."""
    body = norm(line).rstrip(".")
    parts = [p.strip() for p in re.split(r",\s*(?:and |but )?|\s+(?:and|but)\s+", body) if p.strip()]
    if len(parts) != 3:
        return None, parts
    levels = []
    for part, options in zip(parts, PHRASES[category]):
        hit = None
        for level, phrase in options.items():
            if re.fullmatch(phrase, part):
                hit = level
                break
        if hit is None:
            return None, parts
        levels.append(hit)
    return tuple(levels), parts


def check_coaching(num, turns, coaching, followup):
    fails, warns, info = [], [], {}
    lines = [l.strip() for l in coaching.splitlines() if l.strip()]
    nurse_norm = " || ".join(norm(n) for n, _ in turns)
    elaine_norm = " || ".join(norm(r) for _, r in turns)

    if len(lines) != 6:
        fails.append(f"LAYOUT: {len(lines)} non-empty lines (must be exactly 6)")
    if not re.search(r"\n\s*\n", coaching):
        fails.append("LAYOUT: no blank line between lines")
    words = len(coaching.split())
    if words >= 200:
        fails.append(f"LAYOUT: coaching is {words} words (must be under 200)")
    if re.search(r"\b(total|overall score|out of 30)\b", coaching, re.I):
        fails.append("LAYOUT: said a total, which the prompt forbids")

    # voice: the prompt mandates first person for Elaine
    third = re.findall(r"\b(Elaine|she|her|hers)\b", coaching)
    info["person"] = "third" if third else "first"
    if third:
        warns.append(f"VOICE: coaching refers to Elaine in the third person ({sorted(set(third))}) - "
                     f"the prompt's VOICE section forbids this")

    score_lines = re.findall(r"For (Empathy|CARES|Communication), you receive a score of (\d+) out of 10,?\s*"
                             r"because (.*)", coaching)
    loose = re.findall(r"For (Empathy|CARES|Communication), you receive an? (\d+) out of 10", coaching)
    if len(score_lines) != 3:
        fails.append(f"LAYOUT: {len(score_lines)} score lines in the required wording "
                     f"(found {len(loose)} in the older 'you receive a N out of 10' wording)")

    got = {}
    for cat, score, rest in score_lines:
        got[cat] = int(score)
    info["scores"] = got

    # recap -> levels -> POINTS, and levels vs what the script should earn
    expect = SCRIPTS[num]["expect"]
    key = {"Empathy": "empathy", "CARES": "cares", "Communication": "communication"}
    for idx, cat in enumerate(CATEGORIES):
        recap = lines[idx * 2] if len(lines) > idx * 2 else ""
        levels, parts = parse_recap(recap, cat)
        if levels is None:
            fails.append(f"RECAP {cat}: not built from the fixed phrases: {recap[:110]!r}")
            continue
        info.setdefault("levels", {})[cat] = levels
        if cat in got:
            want = POINTS[levels]
            if got[cat] != want:
                fails.append(f"POINTS {cat}: recap says {levels} which the table scores {want}, "
                             f"but the coaching said {got[cat]}")
        for i, (lvl, allowed) in enumerate(zip(levels, expect[key[cat]]), 1):
            if lvl not in allowed:
                fails.append(f"LEVEL {cat} item {i}: coach said {lvl}, the conversation supports "
                             f"{'/'.join(allowed)}")
        if "<topic>" in recap:
            fails.append(f"RECAP {cat}: left the <topic> placeholder unfilled")

    # reasons
    for cat, score, rest in score_lines:
        s = int(score)
        quoted = re.search(r'you did well by saying ["“]([^"”]+)["”]', rest)
        if s >= 3:
            if not quoted:
                fails.append(f"REASON {cat}: score {s} needs 'you did well by saying \"...\"'")
            else:
                q = quoted.group(1).strip(" .,")
                if len(q.split()) > 6:
                    fails.append(f"REASON {cat}: quote is {len(q.split())} words (max 6): {q!r}")
                if norm(q) and norm(q) not in nurse_norm:
                    fails.append(f"REASON {cat}: quote is not in any caregiver line: {q!r}")
        else:
            if norm(FIXED_REASON[cat]) not in norm(rest):
                fails.append(f"REASON {cat}: score {s} must use the fixed reason, got {rest[:70]!r}")

    # tips
    for cat, score, rest in score_lines:
        s = int(score)
        tip = re.search(r'To improve, when I said ["“]([^"”]+)["”], you could have '
                        r'said ["“]([^"”]+)["”]', rest)
        if s == 10 and tip:
            fails.append(f"TIP {cat}: a 10 must get no tip")
        if s < 10 and not tip:
            fails.append(f"TIP {cat}: score {s} must carry a tip in the required wording")
        if tip:
            mine, line = tip.group(1).strip(" .,"), tip.group(2)
            if norm(mine) and norm(mine) not in elaine_norm:
                fails.append(f"TIP {cat}: quotes words Elaine never said: {mine!r}")
            if len(mine.split()) > 6:
                fails.append(f"TIP {cat}: quotes {len(mine.split())} of her words (max 6)")
            if len(line.split()) > 12:
                fails.append(f"TIP {cat}: suggested line is {len(line.split())} words (max 12)")
            if re.search(r"\byou (need to|have to|must)\b|^get up|it'?s time for", line, re.I):
                fails.append(f"TIP {cat}: suggested line is a command: {line!r}")

    # follow-up must not re-score
    if re.search(r"you receive a score of|you receive a \d+ out of", followup, re.I):
        fails.append("AFTER COACHING: the follow-up printed the scores again")
    if len(followup.split()) > 30:
        fails.append(f"AFTER COACHING: follow-up is {len(followup.split())} words (max 30)")
    return fails, warns, info


def main():
    args = sys.argv[1:]
    path = args.pop(0)
    rounds = 1
    if "--rounds" in args:
        i = args.index("--rounds"); rounds = int(args[i + 1]); del args[i:i + 2]
    nums = [int(a) for a in args] or sorted(SCRIPTS)
    fields = load_fields(path)
    missing = [f for f in SCENE_FIELDS + ["EVALUATION PREFIX", "EVALUATION FORMAT",
                                          "EVALUATION SUFFIX", "FEEDBACK CATEGORIES"] if f not in fields]
    if missing:
        sys.exit(f"prompt file is missing blocks: {missing}")

    jobs = [(r, n) for r in range(1, rounds + 1) for n in nums]
    with ThreadPoolExecutor(max_workers=7) as ex:
        results = list(ex.map(lambda j: (j, run_session(fields, j[1])), jobs))

    out, summary = [], []
    for (r, n), (opening, turns, coaching, followup) in results:
        sf, sw = check_scene(n, turns)
        cf, cw, info = check_coaching(n, turns, coaching, followup)
        name = SCRIPTS[n]["name"]
        sc = info.get("scores", {})
        shown = "/".join(str(sc.get(c, "-")) for c in CATEGORIES)
        summary.append(f"R{r} {n} {name:11} E/C/Co {shown:10} person {info.get('person','?'):5} "
                       f"| {len(sf)+len(cf)} fail, {len(sw)+len(cw)} warn")
        summary += [f"      FAIL {x}" for x in sf + cf]
        summary += [f"      warn {x}" for x in sw + cw]
        out.append(f"\n{'=' * 80}\nROUND {r} - SCRIPT {n} {name}\n{'=' * 80}\nElaine: {opening}")
        for msg, reply in turns:
            out.append(f"\nCaregiver: {msg}\nElaine: {reply}")
        out.append(f"\nCaregiver: Please coach me\nCOACH:\n{coaching}\n"
                   f"\nCaregiver: {SCRIPTS[n]['followup']}\nCOACH: {followup}\n")
        out.append("FAILS:\n" + "\n".join(sf + cf or ["none"]))
        out.append("WARNS:\n" + "\n".join(sw + cw or ["none"]))

    report = "\n".join(summary)
    fn = f"elaine_sim_{datetime.now():%Y%m%d_%H%M%S}.txt"
    open(fn, "w", encoding="utf-8").write(f"Prompt: {path}\nModel: {MODEL}\n\n{report}\n" + "\n".join(out))
    print(report)
    print(f"\nFull transcripts: {fn}")


if __name__ == "__main__":
    main()
