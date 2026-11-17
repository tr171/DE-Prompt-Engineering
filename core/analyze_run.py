"""
BPAI QA Automation - Run analyser
----------------------------------
Reads a results file and reports the gaps, so you can fix them in the portal
without needing another portal run to find them.

    python core/analyze_run.py avatars/gladys/runs/portal_run_28.xlsx
    python core/analyze_run.py bpai_qa_results_*.xlsx

Works on BOTH the QA Lab's "Download Excel" export and files produced by
run_qa_tests.py - they share the same Transcripts layout. No API calls, no
token, no cost: every check below is a deterministic read of the file.

WHAT IT CHECKS

1. Avatar identity - is this actually the avatar you meant to test? Compares
   the opening line against the persona file's SHARED_CONTEXT and flags a
   mismatch. (A run where the wrong avatar answered is worthless, and the
   opening line catches it in one second.)
2. Scale - what denominator is the coaching emitting, and does it match the
   bands in EXPECTATIONS? A mismatch here is what produces "No score".
3. Bands - each persona's rounds against its expected band.
4. Per-category - mean per category, flagged when outside its per_point range.
   This is where over-crediting shows up.
5. Fabricated evidence - quotes the coaching attributes to the learner that
   the learner never actually said. The evaluation prompt forbids this, so
   every hit is a real defect.
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root on the import path, so this runs as
# `python core/analyze_run.py` from the repo root. config.py and personas/ live
# there; the rest of the engine sits next to this file.
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
# --------------------------------------------------------------------------

import argparse
import glob
import importlib
import re
import statistics
import sys
import unicodedata

from openpyxl import load_workbook

from personas import EXPECTATIONS

COL_AVATAR, COL_ROUND, COL_PERSONA = 1, 2, 3
COL_SPEAKER, COL_MESSAGE, COL_MODE = 5, 6, 8

GREEN, RED, YELLOW, DIM, BOLD, OFF = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"


def norm(text):
    """Normalises curly quotes, dashes and runs of whitespace for comparison."""
    text = unicodedata.normalize("NFKC", str(text))
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("—", "-"), ("–", "-"), ("…", "...")]:
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip().lower()


def load(path):
    wb = load_workbook(path, read_only=True, data_only=True)
    if "Transcripts" not in wb.sheetnames:
        raise ValueError("no 'Transcripts' sheet - is this a BPAI results file?")
    convos, order = {}, []
    for row in wb["Transcripts"].iter_rows(min_row=2, values_only=True):
        if not row or row[COL_AVATAR] is None:
            continue
        key = (row[COL_AVATAR], row[COL_ROUND], row[COL_PERSONA])
        if key not in convos:
            convos[key] = {"avatar": row[COL_AVATAR], "round": row[COL_ROUND],
                           "persona": row[COL_PERSONA], "opening": "",
                           "learner": [], "avatar_lines": [], "coaching": ""}
            order.append(key)
        c = convos[key]
        speaker, message, mode = str(row[COL_SPEAKER] or ""), str(row[COL_MESSAGE] or ""), str(row[COL_MODE] or "").lower()
        if not message:
            continue
        if mode == "opening":
            c["opening"] = message
        elif speaker == "Avatar (Coaching)" and mode == "during":
            if len(message) > len(c["coaching"]):
                c["coaching"] = message
        elif speaker == "You" and mode == "before":
            c["learner"].append(message)
        elif speaker == "Avatar" and mode == "before":
            c["avatar_lines"].append(message)
    wb.close()
    return [convos[k] for k in order]


def parse_scores(coaching):
    """Returns (total, denominator, {category: score}) - works at any scale."""
    total = denom = None
    m = re.search(r"Overall Score:\s*(\d+)\s*/\s*(\d+)", coaching)
    if m:
        total, denom = int(m.group(1)), int(m.group(2))
    cats = {}
    for cat, score in re.findall(r"^\s*([A-Z][A-Za-z ]{2,30}?)\s*\n\s*-\s*Score:\s*(\d+)\s*/\s*\d+",
                                 coaching, re.M):
        cats[cat.strip()] = int(score)
    return total, denom, cats


def claimed_quotes(coaching, minimum=18):
    """Quotes the coaching presents as EVIDENCE of what the learner said.

    Only "What went well" lines make a factual claim about the learner. A
    "Try saying" line is advice about a phrase the learner did NOT say, and a
    "What to improve" line often quotes the avatar, so both are excluded or
    they produce noise rather than findings.
    """
    out = []
    for line in coaching.splitlines():
        stripped = line.strip().lstrip("-").strip()
        if not stripped.lower().startswith("what went well"):
            continue
        for q in re.findall(r"[\u201c\"]([^\u201d\"]{%d,200})[\u201d\"]" % minimum, stripped):
            q = q.strip(" .,;:!?")
            if q:
                out.append(q)
    return out


def expected_range(value):
    """'0-2' -> (0,2); 10 -> (10,10); None for anything unparseable."""
    if isinstance(value, int):
        return value, value
    m = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", str(value))
    return (int(m.group(1)), int(m.group(2))) if m else None


def analyse(path, forced=None):
    print(f"\n{BOLD}{path}{OFF}")
    convos = load(path)
    if not convos:
        print("  no conversations found."); return
    avatar = forced or convos[0]["avatar"]
    exp_all = EXPECTATIONS.get(avatar) or {}
    if not exp_all:
        # The QA Lab writes a numeric id in the Avatar column, so fall back to
        # whichever avatar's SHARED_CONTEXT vocabulary the transcript actually
        # matches. Matching on persona names alone is useless: High/Medium/Low/
        # Trap exist in every avatar file.
        body = norm(" ".join(l for c in convos for l in c["avatar_lines"] + [c["opening"]]))
        best, best_score = None, 0
        for name in EXPECTATIONS:
            try:
                ctx_i = importlib.import_module(f"personas.{name}").SHARED_CONTEXT
            except Exception:
                continue
            names = {w for w in re.findall(r"\b[A-Z][a-z]{3,}\b", ctx_i)
                     if w not in ("The", "Your", "What", "Who", "Her", "She", "Gladys")}
            score = sum(1 for w in names if norm(w) in body) / max(len(names), 1)
            if score > best_score:
                best, best_score = name, score
        if best and best_score > 0.15:
            exp_all, avatar = EXPECTATIONS[best], best
            print(f"  {DIM}Avatar column is {convos[0]['avatar']!r} (an id). Content matches "
                  f"personas/{best}.py ({best_score:.0%} of its vocabulary present).{OFF}")
        else:
            print(f"  {YELLOW}WARN{OFF} could not match this run to any persona file. "
                  f"Pass --avatar <Name> to force it.")
    print(f"  {len(convos)} conversations | avatar {avatar!r} | "
          f"{len({c['round'] for c in convos})} rounds x {len({c['persona'] for c in convos})} personas")

    # -- 1. avatar identity ------------------------------------------------
    print(f"\n{BOLD}1. Avatar identity{OFF}")
    openings = {c["opening"] for c in convos if c["opening"]}
    for o in sorted(openings):
        print(f"   opening: {o[:95]!r}")
    ctx = ""
    try:
        ctx = importlib.import_module(f"personas.{avatar}").SHARED_CONTEXT
    except Exception:
        pass
    if len(openings) > 1:
        print(f"   {YELLOW}WARN{OFF}  more than one opening line across the run")
    if ctx:
        anchors = [w for w in re.findall(r"\b[A-Z][a-z]{3,}\b", ctx) if w not in ("The", "Your", "What", "Who", "Her", "She")]
        body = norm(" ".join(l for c in convos for l in c["avatar_lines"]))
        missing = [a for a in dict.fromkeys(anchors) if norm(a) not in body]
        hit = len(set(anchors)) - len(missing)
        if hit < max(3, len(set(anchors)) // 3):
            print(f"   {RED}FAIL{OFF}  almost none of this avatar's own vocabulary appears "
                  f"({hit}/{len(set(anchors))} names from SHARED_CONTEXT). Wrong avatar?")
        else:
            print(f"   {GREEN}OK{OFF}    {hit}/{len(set(anchors))} names from SHARED_CONTEXT appear in the avatar's lines")

    # -- 2. scale ----------------------------------------------------------
    print(f"\n{BOLD}2. Scoring scale{OFF}")
    denoms = {}
    for c in convos:
        _, d, _ = parse_scores(c["coaching"])
        if d:
            denoms[d] = denoms.get(d, 0) + 1
    band_max = max((b[1] for e in exp_all.values() if (b := e.get("portal_band"))), default=None)
    if not denoms:
        print(f"   {RED}FAIL{OFF}  no 'Overall Score: X/Y' line found in any coaching")
    else:
        for d, n in sorted(denoms.items()):
            print(f"   coaching emits out of {d}  ({n} conversations)")
        if band_max and len(denoms) == 1:
            d = next(iter(denoms))
            if d == band_max:
                print(f"   {GREEN}OK{OFF}    matches the bands in EXPECTATIONS (max {band_max})")
            else:
                print(f"   {RED}FAIL{OFF}  coaching is /{d} but EXPECTATIONS bands top out at {band_max}. "
                      f"This is what produces \"No score\".")

    # -- 3 & 4. bands and categories --------------------------------------
    print(f"\n{BOLD}3. Bands{OFF}")
    per_persona = {}
    for c in convos:
        per_persona.setdefault(c["persona"], []).append(c)
    for persona, group in per_persona.items():
        exp = exp_all.get(persona, {})
        band = exp.get("portal_band")
        scores = [(c["round"], parse_scores(c["coaching"])[0]) for c in group]
        got = [s for _, s in sorted(scores) if s is not None]
        if not got:
            print(f"   {persona:26} {RED}no parseable scores{OFF}"); continue
        if band:
            lo, hi = band
            inb = sum(1 for s in got if lo <= s <= hi)
            mark = GREEN if inb == len(got) else (YELLOW if inb else RED)
            print(f"   {persona:26} {str(got):22} mean {statistics.mean(got):5.1f}  "
                  f"band {lo}-{hi}  {mark}{inb}/{len(got)} in band{OFF}")
        else:
            print(f"   {persona:26} {str(got):22} mean {statistics.mean(got):5.1f}  (no band recorded)")

    print(f"\n{BOLD}4. Per-category (flagged when outside the per_point range){OFF}")
    for persona, group in per_persona.items():
        exp = exp_all.get(persona, {})
        per_point = exp.get("per_point") or {}
        rows = [parse_scores(c["coaching"])[2] for c in group]
        cats = sorted({k for r in rows for k in r})
        if not cats:
            continue
        bits = []
        for cat in cats:
            vals = [r[cat] for r in rows if cat in r]
            mean = statistics.mean(vals)
            rng = expected_range(per_point.get(cat)) if cat in per_point else None
            if rng and not (rng[0] - 0.5 <= mean <= rng[1] + 0.5):
                bits.append(f"{RED}{cat} {mean:.1f} (expected {rng[0]}-{rng[1]}){OFF}")
            else:
                bits.append(f"{cat} {mean:.1f}")
        print(f"   {persona:26} " + " | ".join(bits))

    # -- 5. fabricated evidence -------------------------------------------
    print(f"\n{BOLD}5. Evidence integrity (who actually said the quoted lines){OFF}")
    hits = misattributed = 0
    for c in convos:
        if not c["coaching"]:
            continue
        said = norm(" ".join(c["learner"]))
        avatar_said = norm(" ".join(c["avatar_lines"] + [c["opening"]]))
        for q in claimed_quotes(c["coaching"]):
            nq = norm(q)
            if nq in said:
                continue                      # the learner really said it
            if nq in avatar_said:
                # The quote is real, but it belongs to the AVATAR. Under
                # "What went well" the coach is claiming the learner said it,
                # which credits the learner for the avatar's own words. This is
                # how a persona that never asks to return still scores the
                # objective: the avatar invites itself back and the coach
                # awards the points to the learner.
                misattributed += 1
                print(f"   {RED}FAIL{OFF}  R{c['round']} {c['persona']}: credited to the learner, but "
                      f"{avatar} said it -> {q[:80]!r}")
                continue
            hits += 1
            print(f"   {RED}FAIL{OFF}  R{c['round']} {c['persona']}: credited as the learner's words -> {q[:88]!r}")
            print(f"         {DIM}said by neither the learner ({len(c['learner'])} msgs) nor the avatar{OFF}")
    if not hits and not misattributed:
        print(f"   {GREEN}OK{OFF}    every quoted line was genuinely said by the learner")
    else:
        print()
        if hits:
            print(f"   {RED}{hits} fabricated quote(s){OFF} - said by nobody. The evaluation prompt says "
                  f"\"Do not invent or assume anything that did not happen\".")
        if misattributed:
            print(f"   {RED}{misattributed} misattributed quote(s){OFF} - the avatar's own words credited to "
                  f"the learner.\n   {DIM}This is how a persona that never asks to return still scores the "
                  f"objective: the avatar\n   invites itself back, and the coach awards those points to the "
                  f"learner.{OFF}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="one or more results .xlsx files (globs allowed)")
    ap.add_argument("--avatar", help="force which persona file to judge against, e.g. Gladys")
    args = ap.parse_args()
    paths = []
    for pattern in args.files:
        paths.extend(sorted(glob.glob(pattern)) or [pattern])
    for p in paths:
        try:
            analyse(p, args.avatar)
        except (ValueError, OSError) as e:
            print(f"\n{p}\n  skipped: {e}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
