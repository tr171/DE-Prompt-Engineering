"""
Checks an Elaine V2 portal run against the prompt's own coaching rules.

    python avatars/elaine/tools/analyze_portal.py avatars/elaine/runs/portal_run_31.xlsx

Reads the QA Lab's "Download Excel" export. Every check is a deterministic
read of the prompt's own LAYOUT / RECAP / POINTS / REASONS / TIPS sections,
so a FAIL is the coaching breaking its own rules, not an opinion.
Scoring correctness is checked the only way it can be checked without a human:
the recap names the three levels, and the POINTS table says exactly what those
three levels score. If the printed score disagrees, the coach did its own maths.
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root and core/ on the import path, so this runs as
# `python avatars/elaine/tools/analyze_portal.py` from the repo root. config.py and personas/
# live at the root; the shared engine lives in core/.
import pathlib as _pathlib, sys as _sys
_ROOT = _pathlib.Path(__file__).resolve().parents[3]
_sys.path[:0] = [str(_ROOT), str(_ROOT / "core")]
# --------------------------------------------------------------------------
import re, sys, collections
from openpyxl import load_workbook
from local_sim import PHRASES, POINTS, CATEGORIES, FIXED_REASON, norm, sentences, parse_recap, BANNED_CHARS

RED, GREEN, YELLOW, BOLD, OFF = "\033[31m", "\033[32m", "\033[33m", "\033[1m", "\033[0m"


def load(path):
    ws = load_workbook(path, read_only=True, data_only=True)["Transcripts"]
    convos = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or r[3] is None:
            continue
        c = convos.setdefault((r[2], r[3]), {"round": r[2], "persona": r[3], "opening": "",
                                             "learner": [], "avatar": [], "coach": "", "after": []})
        sp, msg, mode = str(r[5] or ""), str(r[6] or ""), str(r[8] or "")
        if not msg:
            continue
        if mode == "opening":
            c["opening"] = msg
        elif "Coaching" in sp and mode == "during":
            if len(msg) > len(c["coach"]):
                c["coach"] = msg
        elif sp == "You" and mode == "before":
            c["learner"].append(msg)
        elif sp == "Avatar" and mode == "before":
            c["avatar"].append(msg)
        elif mode == "after":
            c["after"].append((sp, msg))
    return list(convos.values())


def check(c):
    fails = []
    straight = lambda t: t.replace("’", "'").replace("‘", "'")
    coach, lines = c["coach"], [l.strip() for l in c["coach"].splitlines() if l.strip()]
    learner_norm = " || ".join(norm(m) for m in c["learner"])
    elaine_norm = " || ".join(norm(m) for m in c["avatar"])

    # --- scene rules
    for i, r in enumerate(map(straight, c["avatar"]), 1):
        if len(sentences(r)) > 2:
            fails.append(("scene", f"reply {i}: {len(sentences(r))} sentences (max 2)"))
        if len(r.split()) > 28:
            fails.append(("scene", f"reply {i}: {len(r.split())} words (max 28)"))
        if len(r) > 160:
            fails.append(("scene", f"reply {i}: {len(r)} characters (max 160)"))
        for ch, label in BANNED_CHARS.items():
            if ch in r:
                fails.append(("scene", f"reply {i}: banned {label}")); break
        if re.search(r"you receive a score of", r, re.I):
            fails.append(("scene", f"reply {i}: COACHING LEAKED INTO THE SCENE"))
    starts = {}
    for i, r in enumerate(map(straight, c["avatar"]), 1):
        k = " ".join(norm(r).split()[:3])
        if k and k in starts:
            fails.append(("scene", f"reply {i}: same opening three words as reply {starts[k]}"))
        starts[k] = i

    # --- layout
    if len(lines) != 6:
        fails.append(("layout", f"{len(lines)} non-empty lines (must be exactly 6)"))
    if len(coach.split()) >= 200:
        fails.append(("layout", f"{len(coach.split())} words (must be under 200)"))
    if re.search(r"\b(total|overall score)\b", coach, re.I):
        fails.append(("layout", "said a total"))
    if re.search(r"\b(Elaine|she|her|hers)\b", coach):
        fails.append(("voice", "coached in the third person"))

    score_lines = re.findall(r"For (Empathy|CARES|Communication), you receive a score of (\d+) "
                             r"out of 10,?\s*because (.*)", coach)
    if len(score_lines) != 3:
        fails.append(("layout", f"{len(score_lines)} score lines in the required wording"))
    got = {cat: int(s) for cat, s, _ in score_lines}

    # --- recap -> levels -> POINTS
    for idx, cat in enumerate(CATEGORIES):
        recap = lines[idx * 2] if len(lines) > idx * 2 else ""
        levels, _ = parse_recap(recap, cat)
        if levels is None:
            fails.append(("recap", f"{cat}: not built from the fixed phrases"))
            continue
        if cat in got and got[cat] != POINTS[levels]:
            fails.append(("points", f"{cat}: recap says {levels} = {POINTS[levels]}, "
                                    f"coaching said {got[cat]}"))

    # --- reasons and tips
    for cat, s, rest in score_lines:
        s = int(s)
        q = re.search(r'you did well by saying ["“]([^"”]+)["”]', rest)
        if s >= 3:
            if not q:
                fails.append(("reason", f"{cat}: score {s} needs a 'you did well by saying' quote"))
            else:
                t = q.group(1).strip(" .,")
                if len(t.split()) > 6:
                    fails.append(("reason", f"{cat}: quote is {len(t.split())} words (max 6)"))
                if norm(t) and norm(t) not in learner_norm:
                    fails.append(("fabricated", f"{cat}: quote not in any learner line: {t[:50]!r}"))
        elif norm(FIXED_REASON[cat]) not in norm(rest):
            fails.append(("reason", f"{cat}: score {s} must use the fixed reason"))
        tip = re.search(r'To improve, when I said ["“]([^"”]+)["”], you could have '
                        r'said ["“]([^"”]+)["”]', rest)
        if s == 10 and tip:
            fails.append(("tip", f"{cat}: a 10 must get no tip"))
        if s < 10 and not tip:
            fails.append(("tip", f"{cat}: score {s} must carry a tip in the required wording"))
        if tip:
            mine, line = tip.group(1).strip(" .,"), tip.group(2)
            if norm(mine) and norm(mine) not in elaine_norm:
                where = "a learner line" if norm(mine) in learner_norm else "nowhere"
                fails.append(("fabricated", f"{cat}: tip quotes words Elaine never said "
                                            f"(found in {where}): {mine[:50]!r}"))
            if len(line.split()) > 12:
                fails.append(("tip", f"{cat}: suggested line is {len(line.split())} words (max 12)"))

    # --- after coaching
    for sp, msg in c["after"]:
        if "Coaching" in sp and re.search(r"you receive a score of", msg):
            fails.append(("after", "re-printed the scores in a follow-up"))
        if "Coaching" in sp and len(msg.split()) > 30:
            fails.append(("after", f"follow-up is {len(msg.split())} words (max 30)"))
    return got, fails


def main():
    convos = load(sys.argv[1])
    print(f"\n{BOLD}{sys.argv[1]}{OFF}  {len(convos)} conversations")
    print(f"opening: {sorted({c['opening'] for c in convos})}")
    allf = collections.Counter()
    per_persona = collections.defaultdict(list)
    print(f"\n{BOLD}Per conversation{OFF}")
    for c in sorted(convos, key=lambda x: (str(x['persona']), str(x['round']))):
        got, fails = check(c)
        allf.update(k for k, _ in fails)
        per_persona[c["persona"]].append((c["round"], got, fails))
        shown = "/".join(str(got.get(k, "-")) for k in CATEGORIES)
        mark = GREEN if not fails else (YELLOW if len(fails) < 3 else RED)
        print(f"  {str(c['persona']):15} R{c['round']}  E/C/Co {shown:9} "
              f"{mark}{len(fails)} fail{OFF}")
        for kind, msg in fails:
            print(f"      {kind:11} {msg}")
    print(f"\n{BOLD}Totals across {len(convos)} conversations{OFF}")
    for k, v in allf.most_common():
        print(f"   {v:3}  {k}")
    clean = sum(1 for c in convos if not check(c)[1])
    print(f"\n   {clean}/{len(convos)} conversations with no rule break at all")


if __name__ == "__main__":
    main()
