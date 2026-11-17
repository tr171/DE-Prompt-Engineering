"""
Marcus scoring-anchor run against the live QA Lab
-------------------------------------------------
Same 11 anchors as local_sim.py, same checks, but driven through the Better
Path AI portal instead of OpenAI directly - so it tests the prompt as the
platform actually assembles it, including coaching="after" for follow-ups.

    python avatars/marcus/tools/run_anchors.py                    all 11, 1 round
    python avatars/marcus/tools/run_anchors.py --rounds 3
    python avatars/marcus/tools/run_anchors.py NULL NO-ASK
    python avatars/marcus/tools/run_anchors.py --scenario 142 --agent 138

Ids default to config/settings.py SCENARIOS["Marcus"]. If the new prompt was
pasted into a different avatar, pass --scenario and --agent.

It prints the avatar's opening line and waits for you to confirm it before
spending a run - one run has already been wasted testing the wrong avatar.
Pass --yes to skip the prompt.

Writes marcus_anchors_<timestamp>.xlsx (Anchors + Transcripts sheets) and
prints the same report local_sim.py does.
"""

# --- repo bootstrap -------------------------------------------------------
import pathlib as _pathlib, sys as _sys
_ROOT = _pathlib.Path(__file__).resolve().parents[3]
_sys.path[:0] = [str(_ROOT), str(_ROOT / "core"), str(_pathlib.Path(__file__).resolve().parent)]
# --------------------------------------------------------------------------

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from openpyxl import Workbook

from config import AVATAR_MODEL, SCENARIOS
from anchor_scripts import ANCHORS, ORDER
from local_sim import (CATS, check_coaching, check_scene, check_scores,
                       derive_band, parse_coaching, read_facts)
from run_qa_tests import (MODE_COACHING, MODE_FOLLOWUP, MODE_SCENE,
                          create_simulation, send_message, start_session)

GREEN, RED, DIM, BOLD, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"


def run_one(name, round_num, scenario_id, agent_id):
    a = ANCHORS[name]
    sim = create_simulation(scenario_id, agent_id)
    sid, opening = start_session(scenario_id, agent_id)
    turns, rows = [], [("Avatar", opening, MODE_SCENE, None)]
    for msg in a["messages"]:
        reply, secs = send_message(sid, scenario_id, sim, msg, AVATAR_MODEL, MODE_SCENE)
        turns.append((msg, reply))
        rows += [("You", msg, MODE_SCENE, None), ("Avatar", reply, MODE_SCENE, secs)]
        time.sleep(0.3)
    coaching, secs = send_message(sid, scenario_id, sim, "Please coach me",
                                  AVATAR_MODEL, MODE_COACHING)
    rows += [("You", "Please coach me", MODE_COACHING, None),
             ("Avatar (Coaching)", coaching, MODE_COACHING, secs)]
    followup, secs = send_message(sid, scenario_id, sim, a["followup"],
                                  AVATAR_MODEL, MODE_FOLLOWUP)
    rows += [("You", a["followup"], MODE_FOLLOWUP, None),
             ("Avatar (Coaching)", followup, MODE_FOLLOWUP, secs)]
    return name, round_num, opening, turns, coaching, followup, rows


def main():
    args = sys.argv[1:]
    build = SCENARIOS.get("Marcus - Wellness Check - Moderate") or SCENARIOS["Marcus"]
    scenario_id, agent_id = build["scenario_id"], build["agent_id"]
    rounds, confirm = 1, True
    for flag, setter in (("--rounds", "rounds"), ("--scenario", "scn"), ("--agent", "agt")):
        if flag in args:
            i = args.index(flag)
            val = int(args[i + 1]); del args[i:i + 2]
            if setter == "rounds":
                rounds = val
            elif setter == "scn":
                scenario_id = val
            else:
                agent_id = val
    if "--yes" in args:
        confirm = False
        args.remove("--yes")
    names = [x.upper() for x in args] or ORDER
    bad = [n for n in names if n not in ANCHORS]
    if bad:
        sys.exit(f"unknown anchors: {bad}")

    # Confirm the build before spending a run.
    _, opening = start_session(scenario_id, agent_id)
    print(f"scenario {scenario_id} / agent {agent_id} on {AVATAR_MODEL} opens with:\n"
          f"  {BOLD}{opening}{OFF}\n")
    if confirm and input("Is that the Marcus build you pasted the new prompt into? [y/N] ")\
            .strip().lower() not in ("y", "yes"):
        sys.exit("stopped - nothing was run")

    jobs = [(n, r) for r in range(1, rounds + 1) for n in names]
    print(f"\nRunning {len(jobs)} anchor conversations...\n")
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(lambda j: run_one(j[0], j[1], scenario_id, agent_id), jobs))

    wb = Workbook()
    ws = wb.active
    ws.title = "Anchors"
    ws.append(["Anchor", "Round", "Built to test", "Allowed band", "Safety",
               "Understanding", "Trust", "Total", "Outcome", "Fails", "Warns"])
    tr = wb.create_sheet("Transcripts")
    tr.append(["Timestamp", "Avatar", "Round", "Persona", "Turn", "Speaker",
               "Message", "Model", "Coaching Mode", "Reply Seconds", "Metric"])
    stamp = datetime.now().isoformat(timespec="seconds")

    summary, n_fail = [], 0
    for name, rnd, opening, turns, coaching, followup, rows in \
            sorted(results, key=lambda x: (ORDER.index(x[0]), x[1])):
        a = ANCHORS[name]
        sf, sw, actual = check_scene(name, turns)
        facts = read_facts(name, turns, actual)
        lo, hi, reason, strong = derive_band(facts)
        scores, blocks, pnames, na = parse_coaching(coaching)
        cf, cw = check_coaching(name, turns, coaching, followup, scores, blocks, pnames, na)
        lf, lw = ([], []) if a.get("null") else check_scores(scores, lo, hi, reason, a.get("band"))
        total = sum(scores.values()) if len(scores) == 3 else None
        if total is not None and a.get("total") and not (a["total"][0] <= total <= a["total"][1]):
            lw.append(f"CALIBRATION total: {total}, built for {a['total'][0]}-{a['total'][1]}")
        if total is not None and strong and not (25 <= total <= 30):
            lw.append(f"CALIBRATION total: strong run totalled {total}, the format says 25 to 30")

        fails, warns = sf + cf + lf, sw + cw + lw
        n_fail += len(fails)
        allowed = "/".join(f"{lo[c]}-{hi[c]}" for c in CATS)
        ws.append([name, rnd, a["why"], allowed] +
                  [scores.get(c, "no score") for c in CATS] +
                  [total if total is not None else "-", actual,
                   "\n".join(fails) or "none", "\n".join(warns) or "none"])
        for i, (sp, msg, mode, secs) in enumerate(rows):
            tr.append([stamp, "Marcus", rnd, name, i, sp, msg, AVATAR_MODEL, mode, secs, None])

        shown = "/".join(str(scores.get(c, "-")) for c in CATS)
        mark = f"{GREEN}ok{OFF}" if not fails else f"{RED}{len(fails)} fail{OFF}"
        summary.append(f"R{rnd} {name:13} got {shown:9} allowed {allowed:14} "
                       f"total {str(total):>4}  outcome {actual:7} | {mark}, {len(warns)} warn")
        summary += [f"       FAIL {x}" for x in fails]
        summary += [f"       warn {x}" for x in warns]

    for col, w in zip("ABCDEFGHIJK", [14, 7, 46, 15, 8, 14, 7, 7, 10, 60, 60]):
        ws.column_dimensions[col].width = w
    tr.column_dimensions["G"].width = 90
    fn = f"marcus_anchors_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    wb.save(fn)
    print("\n".join(summary))
    print(f"\n{n_fail} failure(s) across {len(results)} run(s)")
    print(f"Saved {fn}  (Anchors sheet + full chat in Transcripts)")


if __name__ == "__main__":
    main()
