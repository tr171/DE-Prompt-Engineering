"""
Elaine V2 scoring anchor run
-----------------------------
Runs every anchor in anchor_scripts.py against the live avatar, then
saves the scores AND the full chat.

    python avatars/elaine/tools/run_anchors.py                 all 15 anchors, 1 round
    python avatars/elaine/tools/run_anchors.py --rounds 2      each anchor twice
    python avatars/elaine/tools/run_anchors.py COMM-10 EMP-0   only these

Writes elaine_anchors_<timestamp>.xlsx with two sheets:
    Anchors      one row per run - target score, actual score, what the
                 avatar's own recap implies, and whether they agree
    Transcripts  every line of every conversation, same layout as the QA Lab
                 export, so analyze_portal.py reads it unchanged

Two different things are checked, and they fail for different reasons:
  TARGET   the score the conversation was built to produce vs what came back.
           A gap means the avatar judged an item differently than the script
           intended - could be the avatar, could be the script.
  TABLE    the score implied by the avatar's OWN recap line vs what it printed.
           A gap here is the avatar contradicting itself, and is never
           arguable.
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root and core/ on the import path, so this runs as
# `python avatars/elaine/tools/run_anchors.py` from the repo root. config/settings.py and personas/
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

from openpyxl import Workbook

from config import AVATAR_MODEL
from anchor_scripts import ANCHORS, ORDER
from local_sim import CATEGORIES, GOAL_RE, POINTS, parse_recap
from coaching_standard import check_score_lines
from run_qa_tests import (MODE_COACHING, MODE_SCENE, create_simulation,
                          send_message, start_session)

# The Elaine V2 build. Confirmed 2026-11-16: opens "Hello. What do you want?"
# and its coaching leads with the recap line, then "you receive a score of".
# Override with --scenario/--agent to test a copy (e.g. 182/178, "Elaine - Test - Aakash").
SCENARIO_ID, AGENT_ID = 169, 165
GREEN, RED, YELLOW, BOLD, DIM, OFF = ("\033[32m", "\033[31m", "\033[33m",
                                      "\033[1m", "\033[2m", "\033[0m")


def run_one(name, round_num):
    global SCENARIO_ID, AGENT_ID
    a = ANCHORS[name]
    sim = create_simulation(SCENARIO_ID, AGENT_ID)
    sid, opening = start_session(SCENARIO_ID, AGENT_ID)
    turns = [("Avatar", opening, "opening", None)]
    for msg in a["messages"]:
        reply, secs = send_message(sid, SCENARIO_ID, sim, msg, AVATAR_MODEL, MODE_SCENE)
        turns.append(("You", msg, "before", None))
        turns.append(("Avatar", reply, "before", secs))
        time.sleep(0.3)
    coaching, secs = send_message(sid, SCENARIO_ID, sim, "Please coach me",
                                  AVATAR_MODEL, MODE_COACHING)
    turns.append(("You", "Please coach me", "during", None))
    turns.append(("Avatar (Coaching)", coaching, "during", secs))
    return name, round_num, turns, coaching


def read_coaching(coaching):
    """Returns {category: printed score} and {category: (levels, table score)}."""
    printed = {c: int(s) for c, s in
               re.findall(r"For (Empathy|CARES|Communication), you receive a score of (\d+) out of 10",
                          coaching)}
    lines = [l.strip() for l in coaching.splitlines() if l.strip()]
    implied = {}
    for cat in CATEGORIES:
        for l in lines:
            levels, _ = parse_recap(l, cat)
            if levels and cat not in implied:
                implied[cat] = (levels, POINTS[levels])
    return printed, implied


def main():
    args = [a for a in sys.argv[1:]]
    rounds = 1
    if "--rounds" in args:
        i = args.index("--rounds"); rounds = int(args[i + 1]); del args[i:i + 2]
    global SCENARIO_ID, AGENT_ID
    for flag in ("--scenario", "--agent"):
        if flag in args:
            i = args.index(flag); val = int(args[i + 1]); del args[i:i + 2]
            if flag == "--scenario": SCENARIO_ID = val
            else: AGENT_ID = val
    names = args or ORDER
    bad = [n for n in names if n not in ANCHORS]
    if bad:
        sys.exit(f"unknown anchors: {bad}")

    jobs = [(n, r) for r in range(1, rounds + 1) for n in names]
    print(f"Running {len(jobs)} anchor conversations against scenario {SCENARIO_ID} "
          f"on {AVATAR_MODEL}...\n")
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(lambda j: run_one(*j), jobs))

    wb = Workbook()
    ws = wb.active
    ws.title = "Anchors"
    ws.append(["Anchor", "Round", "Category", "Built to score", "Avatar scored",
               "Target met", "Avatar's own recap", "Recap scores", "Matches its table",
               "Other categories", "What the script forces", "Coaching standard"])
    tr = wb.create_sheet("Transcripts")
    tr.append(["Timestamp", "Avatar", "Round", "Persona", "Turn", "Speaker",
               "Message", "Model", "Coaching Mode", "Reply Seconds", "Metric"])

    stamp = datetime.now().isoformat(timespec="seconds")
    rows = []
    for name, rnd, turns, coaching in sorted(results, key=lambda x: (ORDER.index(x[0]), x[1])):
        a = ANCHORS[name]
        cat = a["category"]
        printed, implied = read_coaching(coaching)
        got = printed.get(cat)
        lv, table = implied.get(cat, (None, None))
        target_ok = (got == a["target"])
        table_ok = (got is not None and table is not None and got == table)
        others = ", ".join(f"{c} {printed.get(c, '-')}" for c in CATEGORIES if c != cat)
        learner = [m for sp, m, mode, _ in turns if sp == "You" and mode == "before"]
        avatar = [m for sp, m, mode, _ in turns if sp == "Avatar" and mode == "before"]
        sf, _sw, _ = check_score_lines(coaching, CATEGORIES, learner, avatar, goal_re=GOAL_RE)
        ws.append([name, rnd, cat, a["target"], got if got is not None else "no score",
                   "yes" if target_ok else "NO",
                   ", ".join(lv) if lv else "could not read recap",
                   table if table is not None else "-",
                   "yes" if table_ok else ("NO" if lv else "-"),
                   others, a["why"], "; ".join(sf) or "pass"])
        for i, (sp, msg, mode, secs) in enumerate(turns):
            tr.append([stamp, "Elaine V2", rnd, name, i, sp, msg, AVATAR_MODEL, mode, secs, None])
        rows.append((name, rnd, cat, a["target"], got, target_ok, lv, table, table_ok, others, sf))

    for col, w in zip("ABCDEFGHIJK", [11, 7, 15, 15, 14, 12, 42, 13, 18, 26, 60]):
        ws.column_dimensions[col].width = w
    tr.column_dimensions["G"].width = 90
    fn = f"elaine_anchors_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    wb.save(fn)

    print(f"{BOLD}{'anchor':11} {'built':>6} {'got':>5}  {'target':>7}  {'table':>6}  "
          f"recap levels{OFF}")
    t_ok = b_ok = 0
    s_ok = 0
    for name, rnd, cat, target, got, target_ok, lv, table, table_ok, others, sf in rows:
        s_ok += not sf
        t_ok += target_ok; b_ok += table_ok
        m1 = f"{GREEN}ok{OFF}" if target_ok else f"{RED}off{OFF}"
        m2 = f"{GREEN}ok{OFF}" if table_ok else (f"{RED}off{OFF}" if lv else f"{DIM}?{OFF}")
        extra = "" if table_ok or not lv else f"  {DIM}(its recap = {table}){OFF}"
        print(f"{name:11} {target:>6} {str(got):>5}  {m1:>16}  {m2:>15}  "
              f"{', '.join(lv) if lv else '-'}{extra}")
        for x in sf:
            print(f"      {RED}standard{OFF} {x}")
    n = len(rows)
    print(f"\n  hit the score they were built for : {t_ok}/{n}")
    print(f"  score agrees with its own recap   : {b_ok}/{n}")
    print(f"  follows the coaching standard     : {s_ok}/{n}")
    print(f"\nSaved {fn}  (Anchors sheet + full chat in Transcripts)")


if __name__ == "__main__":
    main()
