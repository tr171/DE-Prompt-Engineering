"""
Marcus local simulator + checker
--------------------------------
Runs the fixed anchor conversations (anchor_scripts.ANCHORS) against a Marcus
prompt file using OpenAI directly, instead of the Better Path AI portal, so the
prompt can be tested before it is pasted in. The portal wraps the fields in its
own template, so ALWAYS confirm the final prompt in the portal afterwards.

    python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt
    python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt STRONG-CHECK NULL
    python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt --rounds 2

Writes marcus_sim_<timestamp>.txt (full transcripts + check report).

Two different things are checked, and they fail for different reasons:

  SCENE   Marcus's own rules - reply length, the noise line, the key-question
          answer, the exact yes lines, never raising Diane or the hospital
          himself. A scene FAIL means the conversation did not reach the state
          the anchor was built to create, so its score proves nothing.

  SCORE   the printed scores against the band the Evaluation Format's own
          ceilings and floors allow for the conversation that ACTUALLY
          happened - managed words, diagnosis words, calm down and threats are
          read back off the officer's lines rather than trusted from the
          script. A score FAIL is the prompt contradicting itself, never an
          opinion about whether the coaching felt fair.

  FORMAT  the coaching layout: three categories, the exact names, the exact
          score wording, one sentence at 10 and a Next time below 10, no
          markdown, no first person.
"""

# --- repo bootstrap -------------------------------------------------------
import pathlib as _pathlib, sys as _sys
_ROOT = _pathlib.Path(__file__).resolve().parents[3]
_sys.path[:0] = [str(_ROOT), str(_ROOT / "core"), str(_pathlib.Path(__file__).resolve().parent)]
# --------------------------------------------------------------------------

import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

from config import AVATAR_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL
from anchor_scripts import ANCHORS, OPENING, ORDER

MODEL = AVATAR_MODEL

BLOCK_RE = re.compile(r"^===== PASTE INTO: ([A-Z][A-Z >-]+?) =====\n(.*?)\n===== END[^\n]*=====",
                      re.S | re.M)
SCENE_FIELDS = ["ROLE", "PERSONALITY", "CONTEXT", "OBJECTIVES", "TONE", "FORMAT",
                "KNOWLEDGE", "CONDITIONS"]

CATS = ["safety", "understanding", "trust"]
CAT_NAME = {
    "safety": "creating emotional safety and stability",
    "understanding": "understanding marcus's experience",
    "trust": "building trust and encouraging support",
}

# Evaluation Format's own managed-word list, word for word.
MANAGED = ["welfare check", "protocol", "assess", "standard question", "i have to ask",
           "just doing my job", "you should", "you need to", "you have to", "precaution",
           "i can't leave until", "calm down", "manic", "episode", "symptoms", "unstable"]
DIAGNOSIS = ["manic", "episode", "symptoms", "unstable"]
THREAT_RE = re.compile(r"i can'?t leave until|i'?m not leaving until|calm down", re.I)

YES_CHECK = "okay. i'll go get checked."
YES_DIANE = "okay. she can know."
PHONE = "314-555-0182"

# Format forbids these inside a scene reply.
SCENE_BANNED = {"—": "em dash", "–": "en dash", "…": "ellipsis",
                "...": "three dots", '"': "quote", "“": "quote", "”": "quote",
                " - ": "dash", "*": "asterisk", "(": "stage direction", ")": "stage direction"}
# Evaluation Format forbids these inside the coaching.
COACH_BANNED = {"—": "em dash", "–": "en dash", "…": "ellipsis",
                "...": "three dots", '"': "quote", "“": "quote", "”": "quote",
                " - ": "dash", "*": "markdown", "#": "markdown", "•": "bullet"}
BANNED_WORDS_RE = re.compile(r"\b(fair|good|excellent)\b", re.I)
FOLLOWUP_BANNED_RE = re.compile(
    r"keep practicing|you'?re on the right path|well done|great question|"
    r"\bcertainly\b|^sure\b|\bof course\b", re.I | re.M)

NULL_LINES = [
    "for creating emotional safety and stability, you receive a score of n/a, because "
    "there was no evidence of how you would create safety with marcus.",
    "for understanding marcus's experience, you receive a score of n/a, because there "
    "was no evidence of how you would understand his experience.",
    "for building trust and encouraging support, you receive a score of n/a, because "
    "there was no evidence of how you would build trust with marcus.",
]

SCORE_RE = re.compile(r"for\s+([^,.\n]+?),\s*you receive\s+(?:a\s+|an\s+)?(\d+)\s*out of 10,\s*because\s*(.*)",
                      re.I)
NA_RE = re.compile(r"for\s+([^,]+?),\s*you receive a score of n/?a", re.I)


def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def low(s):
    return norm(s).lower()


def sentences(text):
    return [s for s in re.split(r"(?<=[.?!])\s+", norm(text)) if s.strip()]


def load_fields(path):
    return {k.split("-> ")[-1]: v.strip()
            for k, v in BLOCK_RE.findall(open(path, encoding="utf-8").read())}


def chat(messages):
    for attempt in range(4):
        try:
            r = requests.post(f"{OPENAI_BASE_URL}/chat/completions",
                              headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                              json={"model": MODEL, "messages": messages}, timeout=240)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(4 * (attempt + 1))


def run_session(fields, name):
    a = ANCHORS[name]
    scene_system = "\n\n".join(f"## {f.title()}\n{fields[f]}" for f in SCENE_FIELDS)
    convo = [{"role": "assistant", "content": OPENING}]
    turns = []
    for msg in a["messages"]:
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
                                  {"role": "user", "content": a["followup"]}])
    return turns, coaching, followup


# ---------------------------------------------------------------- scene ----
def check_scene(name, turns):
    a = ANCHORS[name]
    fails, warns = [], []
    replies = [norm(r) for _, r in turns]
    officer = [norm(m) for m, _ in turns]

    seen_sentences = {}
    for i, r in enumerate(replies, 1):
        n_sent = len(sentences(r))
        if n_sent > 4:
            fails.append(f"reply {i}: {n_sent} sentences (max 4, and only when opening up)")
        elif n_sent == 4:
            warns.append(f"reply {i}: 4 sentences (allowed only when opening up)")
        if "\n" in r:
            fails.append(f"reply {i}: more than one line")
        for ch, label in SCENE_BANNED.items():
            if ch in r:
                fails.append(f"reply {i}: banned {label} {ch!r}: {r[:70]!r}")
                break
        for s in sentences(r):
            k = re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
            if len(k.split()) >= 4 and k in seen_sentences:
                fails.append(f"reply {i}: repeats a sentence from reply {seen_sentences[k]}: {s[:60]!r}")
            seen_sentences[k] = i

    # THE NOISE: reply 2 or 3, ending on wanting it to stop
    if len(replies) >= 2 and not a.get("null"):
        at = next((i for i, w in enumerate(replies, 1)
                   if re.search(r"want it to stop|wanted it to stop|it to stop|shut up for|"
                                r"\bstop for a while\b", w, re.I)), None)
        if at is None:
            fails.append("THE NOISE: he never says he wants it to stop for a while")
        elif at not in (2, 3):
            warns.append(f"THE NOISE: landed in reply {at}, the rule says the second or third")
        else:
            if not re.search(r"stop", sentences(replies[at - 1])[-1], re.I):
                warns.append("THE NOISE: the stop wish is not the end of that reply")

    # THE KEY QUESTION answer
    kq = a.get("key_q_at")
    if kq and len(replies) >= kq:
        r = replies[kq - 1]
        if not (re.search(r"\bquiet\b", r, re.I) and re.search(r"\bsleep\b", r, re.I)):
            fails.append(f"KEY QUESTION: reply {kq} does not say he means quiet and sleep: {r[:80]!r}")
        if not re.search(r"not going to hurt|not gonna hurt|won'?t hurt|not about to hurt|"
                         r"no.{0,20}hurt myself|not trying to hurt|not hurting myself|nothing like that|not that kind of stop", r, re.I):
            fails.append(f"KEY QUESTION: reply {kq} does not say he will not hurt himself: {r[:80]!r}")
    if not kq and not a.get("null"):
        for i, r in enumerate(replies, 1):
            if re.search(r"not going to hurt myself|won'?t hurt myself", r, re.I):
                warns.append(f"reply {i}: volunteered the safety reassurance with no key question")
                break

    # the yes lines
    def starts_with(r, phrase):
        return low(r).startswith(phrase)

    checked_at = [i for i, r in enumerate(replies, 1) if starts_with(r, YES_CHECK)]
    diane_at = [i for i, r in enumerate(replies, 1) if starts_with(r, YES_DIANE)]
    actual = "checked" if checked_at else ("diane" if diane_at else "none")
    want = a["outcome"]
    if want == "checked" and not checked_at:
        fails.append("OUTCOME: never said Okay. I'll go get checked. - this anchor was built to reach it")
    if want == "diane" and not diane_at:
        fails.append("OUTCOME: never said Okay. She can know. - this anchor was built to reach it")
    if want == "none" and actual != "none":
        fails.append(f"OUTCOME: agreed ({actual}) but this anchor should never get a yes")
    if want == "diane" and diane_at and PHONE not in " ".join(replies):
        fails.append("OUTCOME: agreed to a text or call but never gave 314-555-0182")
    if len(checked_at) + len(diane_at) > 1:
        warns.append(f"said a yes line more than once (checked {checked_at}, diane {diane_at})")
    if want != "none" and (checked_at or diane_at):
        got_at = (checked_at or diane_at)[0]
        if got_at != len(replies):
            warns.append(f"agreed at reply {got_at} of {len(replies)}, not on the final ask")

    # never raises Diane or the hospital himself
    wk = a.get("who_knows_at")
    for i, r in enumerate(replies, 1):
        if re.search(r"\b(diane|my mother|my mom)\b", r, re.I):
            if wk is None or i < wk:
                fails.append(f"reply {i}: named Diane before being asked who knows: {r[:70]!r}")
            break
    first_hosp_officer = next((i for i, m in enumerate(officer, 1)
                               if re.search(r"hospital|ambulance|get (you )?checked|take a look at you", m, re.I)),
                              None)
    for i, r in enumerate(replies, 1):
        if re.search(r"\b(hospital|ambulance|emergency room|\ber\b)\b", r, re.I):
            if first_hosp_officer is None or i < first_hosp_officer:
                fails.append(f"reply {i}: raised the hospital himself: {r[:70]!r}")
            break

    leak = re.compile(r"off the table|pressure check|key question|the decision|"
                      r"yes line|one ask at a time|stage direction", re.I)
    for i, r in enumerate(replies, 1):
        if leak.search(r):
            warns.append(f"reply {i}: rule wording leaked into the dialogue: {r[:70]!r}")
            break

    if a.get("undermine"):
        after = replies[3:]
        if not any(re.search(r"get out|leave|out of my|door", x, re.I) for x in after):
            warns.append("UNDERMINE: never told the officer to get out after the judgment line")

    return fails, warns, actual


# --------------------------------------------------------------- limits ----
def read_facts(name, turns, actual_outcome):
    a = ANCHORS[name]
    officer_text = " || ".join(low(m) for m, _ in turns)
    managed = sorted({w for w in MANAGED if w in officer_text})
    diag = sorted({w for w in DIAGNOSIS if re.search(rf"\b{w}\b", officer_text)})
    wk, fa = a.get("who_knows_at"), a.get("first_ask_at")
    return {
        "managed": managed,
        "diagnosis": diag,
        "calm_threat": bool(THREAT_RE.search(officer_text)),
        "undermine": a.get("undermine", False),
        "key_question": a.get("key_q_at") is not None,
        "ask_made": fa is not None,
        "who_knows_first": wk is not None and (fa is None or wk < fa),
        "repeat": a.get("repeat_at") is not None,
        "outcome": actual_outcome,
    }


def derive_band(f):
    """The band the Evaluation Format's own ceilings and floors allow."""
    hi = {c: 10 for c in CATS}
    reason = {c: [] for c in CATS}

    def cap(cat, n, why):
        if n < hi[cat]:
            hi[cat] = n
            reason[cat].append(why)

    if not f["key_question"]:
        cap("safety", 5, "no key question")
        cap("understanding", 7, "no key question")
        cap("trust", 6, "no key question")
    if f["managed"]:
        cap("safety", 5, f"managed words {f['managed']}")
    if f["calm_threat"]:
        cap("safety", 3, "calm down or an implied threat")
    if f["diagnosis"]:
        cap("understanding", 4, f"diagnosis words {f['diagnosis']}")
    if not f["ask_made"]:
        cap("trust", 4, "never made an ask")
    elif not f["who_knows_first"]:
        cap("trust", 7, "first ask came before who knows")
    if f["outcome"] == "none":
        cap("trust", 6, "outcome none")
    elif f["outcome"] == "diane":
        cap("trust", 8, "outcome Diane")
    if f["repeat"]:
        cap("trust", 8, "a repeat caps 3.3 at 1")
    if f["undermine"]:
        for c in CATS:
            cap(c, 2, "told him his view cannot be trusted")

    strong = (f["key_question"] and f["who_knows_first"] and not f["managed"]
              and f["outcome"] in ("checked", "diane"))
    lo = {c: 0 for c in CATS}
    if not f["managed"]:
        lo = {c: 4 for c in CATS}
    if strong:
        lo = {c: 8 for c in CATS}
    # "A ceiling always beats a floor."
    lo = {c: min(lo[c], hi[c]) for c in CATS}
    return lo, hi, reason, strong


# -------------------------------------------------------------- coaching ----
def parse_coaching(coaching):
    """-> ({cat: score}, {cat: block text}, [names as printed], na_count)"""
    text = norm(coaching)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    scores, blocks, names = {}, {}, []
    na = sum(1 for l in lines if NA_RE.search(l))

    starts = []
    for m in re.finditer(r"for\s+[^,.\n]+?,\s*you receive\s+(?:a\s+|an\s+)?\d+\s*out of 10", text, re.I):
        starts.append(m.start())
    for idx, s in enumerate(starts):
        e = starts[idx + 1] if idx + 1 < len(starts) else len(text)
        block = text[s:e].strip()
        m = SCORE_RE.match(block)
        if not m:
            continue
        printed_name = m.group(1).strip().lower().rstrip(".")
        names.append(printed_name)
        cat = next((c for c in CATS if CAT_NAME[c] in printed_name
                    or printed_name in CAT_NAME[c]), None)
        if cat is None:
            for c, kws in (("safety", "safety"), ("understanding", "understanding"),
                           ("trust", "trust")):
                if kws in printed_name:
                    cat = c
                    break
        if cat and cat not in scores:
            scores[cat] = int(m.group(2))
            blocks[cat] = block
    return scores, blocks, names, na


ASK_KEY_RE = re.compile(r"ask (?:him )?what (?:he|marcus) (?:means|meant)|"
                        r"ask what (?:that|it) (?:means|meant)|what he means by stop|"
                        r"ask what he meant by stop", re.I)
CREDIT_KEY_RE = re.compile(r"you asked (?:him )?what (?:he|marcus) meant|"
                           r"you asked what (?:he|marcus) meant|asked what marcus meant by|"
                           r"you asked (?:him )?what he meant by", re.I)


def check_coaching(name, turns, coaching, followup, scores, blocks, names, na):
    a = ANCHORS[name]
    fails, warns = [], []
    text = norm(coaching)
    body = text.lower()

    if a.get("null"):
        # The portal returns the three lines as one block, so compare the text,
        # not the line breaks.
        got = re.sub(r"\s+", " ", text.lower()).strip()
        want = re.sub(r"\s+", " ", " ".join(NULL_LINES)).strip()
        if got != want:
            fails.append(f"NO INTERACTION: expected the three N/A lines verbatim, got: {got[:220]!r}")
        if scores:
            fails.append(f"NO INTERACTION: printed real scores {scores} instead of N/A")
        return fails, warns

    if na:
        fails.append(f"NO INTERACTION: printed {na} N/A line(s) for a conversation that had officer lines")
    if len(scores) != 3:
        fails.append(f"LAYOUT: {len(scores)} of 3 score lines in the required wording "
                     f"(names printed: {names})")
    if len(names) == 3:
        for printed, cat in zip(names, CATS):
            if printed.strip().lstrip("the ").rstrip(".") != CAT_NAME[cat]:
                fails.append(f"NAME: category printed as {printed!r}, the format writes "
                             f"{CAT_NAME[cat]!r}")

    # nothing before the first category, nothing after the last
    first = text.lower().find("for ")
    if first > 0:
        fails.append(f"LAYOUT: text before the first category: {text[:first][:70]!r}")

    words = len(text.split())
    if words > 200:
        fails.append(f"LENGTH: coaching is {words} words (the format asks for about 110)")
    elif words > 150:
        warns.append(f"LENGTH: coaching is {words} words (the format asks for about 110)")

    for ch, label in COACH_BANNED.items():
        if ch in text:
            fails.append(f"FORMAT: banned {label} {ch!r} in the coaching")
    if re.search(r"^\s*(\d+[.)]|[-*•])\s", text, re.M):
        fails.append("FORMAT: a bullet or numbered list in the coaching")
    bad = BANNED_WORDS_RE.findall(text)
    if bad:
        fails.append(f"FORMAT: said a forbidden word {sorted(set(w.lower() for w in bad))}")
    if re.search(r"\b(I|me|my)\b", text):
        fails.append("VOICE: the coaching speaks in the first person, which the format forbids")
    if not re.search(r"\b(marcus|he|him|his)\b", body):
        warns.append("VOICE: the coaching never refers to Marcus in the third person")

    # per-block sentence shape
    for cat, block in blocks.items():
        s = sentences(block)
        score = scores[cat]
        has_tip = any(x.lower().startswith("next time") for x in s)
        if score == 10:
            if has_tip:
                fails.append(f"TIP {cat}: a 10 must get no Next time sentence")
            if len(s) != 1:
                fails.append(f"SHAPE {cat}: a 10 gets one sentence, got {len(s)}")
        else:
            if not has_tip:
                fails.append(f"TIP {cat}: score {score} must carry a Next time sentence")
            if len(s) != 2:
                warns.append(f"SHAPE {cat}: a score below 10 gets two sentences, got {len(s)}")
        if score <= 3 and re.search(r"\byou (did|were|showed|built|kept|stayed)\b", block, re.I) \
                and not re.search(r"never|did not|didn'?t|no \w+", block, re.I):
            warns.append(f"REASON {cat}: score {score} should say what was not done, not a strength")

    # the key question must be reported as it actually happened
    kq = a.get("key_q_at")
    for cat, block in blocks.items():
        tip = next((x for x in sentences(block) if x.lower().startswith("next time")), "")
        if kq and ASK_KEY_RE.search(tip):
            fails.append(f"NEXT TIME {cat}: tells the officer to ask what Marcus meant, "
                         f"which they already did at message {kq}")
    if not kq and "safety" in blocks and CREDIT_KEY_RE.search(blocks["safety"]):
        fails.append("BECAUSE safety: credits a key question the officer never asked")

    # the two mandated because parts
    if "safety" in blocks:
        b = blocks["safety"].lower()
        if not re.search(r"(asked|ask|never asked|did not ask|didn'?t ask)[^.]{0,80}"
                         r"(what he meant|what marcus meant|\bstop\b|hurting himself|"
                         r"killing himself)", b):
            fails.append("BECAUSE safety: does not say whether the key question was asked")
    if "trust" in blocks:
        b = blocks["trust"].lower()
        if not re.search(r"agreed to (go|get)|get checked|went in|let you (bring|call|text|involve)|"
                         r"brought diane|diane|did not agree|didn'?t agree|no support|"
                         r"not agree to any support|refused", b):
            fails.append("BECAUSE trust: does not say how it ended")

    # follow-up
    f = norm(followup)
    if len(re.findall(r"you receive", f, re.I)) >= 3:
        fails.append("AFTER COACHING: the follow-up printed the whole coaching again")
    if re.search(r"\b(I|me|my)\b", f):
        fails.append("AFTER COACHING: the follow-up speaks in the first person")
    hit = FOLLOWUP_BANNED_RE.findall(f)
    if hit:
        fails.append(f"AFTER COACHING: forbidden phrase {sorted(set(h.lower() for h in hit))}")
    if re.search(r"^\s*(\d+[.)]|[-*•])\s", f, re.M):
        fails.append("AFTER COACHING: the follow-up used a list")
    q = a["followup"].lower()
    n_sent = len(sentences(f))
    if "example" in q and n_sent != 2:
        fails.append(f"AFTER COACHING: an example answer must be exactly two sentences, got {n_sent}")
    if q.strip() in ("thanks.", "thank you.") and n_sent != 1:
        fails.append(f"AFTER COACHING: a thank you gets one short sentence, got {n_sent}")
    if "please coach me" in q and "above" not in f.lower():
        fails.append("AFTER COACHING: please coach me again must only say the coaching is above")
    for cat, sc in scores.items():
        for m in re.finditer(rf"(\d+)\s*out of 10", f):
            if int(m.group(1)) not in scores.values():
                fails.append(f"AFTER COACHING: quotes a score of {m.group(1)} that was never given")
                break
        break
    return fails, warns


def check_scores(scores, lo, hi, reason, band_hint):
    fails, warns = [], []
    for c in CATS:
        if c not in scores:
            continue
        s = scores[c]
        if s > hi[c]:
            fails.append(f"LIMIT {c}: scored {s} but the format caps it at {hi[c]} "
                         f"({'; '.join(reason[c]) or 'no cap'})")
        if s < lo[c]:
            fails.append(f"FLOOR {c}: scored {s} but the format floors it at {lo[c]}")
        if band_hint:
            blo, bhi = band_hint[c]
            if not (blo <= s <= bhi) and lo[c] <= s <= hi[c]:
                warns.append(f"CALIBRATION {c}: scored {s}, the anchor was built for {blo}-{bhi}")
    return fails, warns


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    path = args.pop(0)
    rounds = 1
    if "--rounds" in args:
        i = args.index("--rounds"); rounds = int(args[i + 1]); del args[i:i + 2]
    names = [a.upper() for a in args] or ORDER
    bad = [n for n in names if n not in ANCHORS]
    if bad:
        sys.exit(f"unknown anchors: {bad}")

    fields = load_fields(path)
    missing = [f for f in SCENE_FIELDS + ["EVALUATION PREFIX", "EVALUATION FORMAT",
                                          "EVALUATION SUFFIX", "FEEDBACK CATEGORIES"]
               if f not in fields]
    if missing:
        sys.exit(f"prompt file is missing blocks: {missing}")

    jobs = [(r, n) for r in range(1, rounds + 1) for n in names]
    print(f"Running {len(jobs)} anchor conversations on {MODEL}...\n")
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda j: (j, run_session(fields, j[1])), jobs))

    out, summary = [], []
    n_fail = 0
    for (r, name), (turns, coaching, followup) in results:
        a = ANCHORS[name]
        sf, sw, actual = check_scene(name, turns)
        facts = read_facts(name, turns, actual)
        lo, hi, reason, strong = derive_band(facts)
        scores, blocks, pnames, na = parse_coaching(coaching)
        cf, cw = check_coaching(name, turns, coaching, followup, scores, blocks, pnames, na)
        lf, lw = ([], []) if a.get("null") else check_scores(scores, lo, hi, reason, a.get("band"))

        total = sum(scores.values()) if len(scores) == 3 else None
        if total is not None and a.get("total"):
            tlo, thi = a["total"]
            if not (tlo <= total <= thi):
                lw.append(f"CALIBRATION total: {total}, the anchor was built for {tlo}-{thi}")
        if total is not None and strong and not (25 <= total <= 30):
            lw.append(f"CALIBRATION total: strong run totalled {total}, the format says 25 to 30")

        fails = sf + cf + lf
        warns = sw + cw + lw
        n_fail += len(fails)
        shown = "/".join(str(scores.get(c, "-")) for c in CATS)
        allowed = "/".join(f"{lo[c]}-{hi[c]}" for c in CATS)
        summary.append(f"R{r} {name:13} got {shown:9} allowed {allowed:14} total "
                       f"{str(total):>4}  outcome {actual:7} | {len(fails)} fail, {len(warns)} warn")
        summary += [f"       FAIL {x}" for x in fails]
        summary += [f"       warn {x}" for x in warns]

        out.append(f"\n{'=' * 78}\nROUND {r} - {name}\n{a['why']}\n{'=' * 78}\nMarcus: {OPENING}")
        for msg, reply in turns:
            out.append(f"\nOfficer: {msg}\nMarcus: {reply}")
        out.append(f"\nOfficer: Please coach me\nCOACH:\n{coaching}\n"
                   f"\nOfficer: {a['followup']}\nCOACH: {followup}\n")
        out.append(f"facts: {facts}\nallowed band: {dict((c, (lo[c], hi[c])) for c in CATS)}")
        out.append("FAILS:\n" + "\n".join(fails or ["none"]))
        out.append("WARNS:\n" + "\n".join(warns or ["none"]))

    report = "\n".join(summary)
    fn = f"marcus_sim_{datetime.now():%Y%m%d_%H%M%S}.txt"
    open(fn, "w", encoding="utf-8").write(f"Prompt: {path}\nModel: {MODEL}\n\n{report}\n" + "\n".join(out))
    print(report)
    print(f"\n{n_fail} failure(s) across {len(results)} run(s)")
    print(f"Full transcripts: {fn}")


if __name__ == "__main__":
    main()
