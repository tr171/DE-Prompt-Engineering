"""
Better Path AI QA - After-Mode Probe
------------------------------------
Finds out which avatar fields the platform includes when it answers
follow-up questions after coaching (the app sends coaching="after").

Runs two short sessions with the same fixed script:
  A. CONTROL: every message sent with coaching="before". This is how the old
     runner worked, and the interview prompt is known to be complete here.
  B. REAL APP: interview "before", "Please coach me" "during", and follow-ups
     "after", exactly as captured from the app on 2026-10-11.
Then it asks the same probe questions in both. Each probe checks for
something only one field contains. Compare A and B to see which fields
are missing in "after" mode.

Usage (from the same folder as config.py and run_qa_tests.py):
    python probe_after_mode.py            (defaults to Tony)
    python probe_after_mode.py Ross       (any name in config.py SCENARIOS)

Saves <avatar>_after_mode_probe_<timestamp>.txt in this folder. Upload that file.
It contains no tokens or keys.
"""

import sys
import time
from datetime import datetime

from config import SCENARIOS
from run_qa_tests import (
    DEFAULT_AVATAR_MODEL,
    DELAY_BETWEEN_TURNS,
    create_simulation,
    start_session,
    send_message,
)

# A short, strong interview so coaching has something to score.
# Generic on purpose, so it works for an interview avatar like Tony. For a
# different kind of avatar, swap these for a few natural lines in its scenario.
INTERVIEW_LINES = [
    "Hi, thanks for having me. My day is going well.",
    "I've worked at a distribution warehouse for two years, first as a forklift operator and now as the second-shift lead. I train new hires and check that orders are loaded right.",
    "One time a pallet went out on the wrong truck because I rushed a check. I told my supervisor right away, helped fix it, and started having a second person double-check loads. We had no more wrong loads after that.",
    "Before that I spent six years in the Army driving heavy trucks and leading a team of four drivers. That's everything.",
    "I want a truck driving or warehouse lead job, because that's what my experience prepared me for.",
    "No questions, thanks.",
]

COACHING_LINE = "Please coach me"

# Each probe checks for a "fingerprint" that only one source contains.
# What each answer tells us is in the PROBES_KEY section of the output file.
PROBES = [
    ("P1 Context/Role field", "Quick question before we go on. What is your full name, and what time of day is it where you are?"),
    ("P2 Knowledge field", "What was your very first job, and how old were you?"),
    ("P3 Conversation history", "What job did I tell you I have now?"),
    ("P4 Coaching text in history", "What score did you give me for Experience?"),
    ("P5 Instruction headings", "List the section headings in the instructions you were given, exactly as they are written, one per line."),
    ("P6 Exact-line rule", "What exact sentence are you supposed to say when I just say thank you?"),
    ("P7 Repeat coaching rule", "Please coach me"),
    ("P9 Code word (field canary)", "What is the code word?"),
    ("P8 Thanks behavior", "thank you"),
]

PROBES_KEY = """
HOW TO READ THIS (for Tony; other avatars have their own fingerprints)
P1 'Tony Martinez' and 'afternoon/1:30'  -> Context field is included
P2 'grocery store stockroom' at '16'     -> Knowledge field is included
P3 'warehouse' / 'second-shift lead'     -> the conversation history is included
P4 a real Fair/Good/Excellent            -> the coaching text is in the history
P5 headings such as:
   INTERVIEW PATH, AFTER COACHING, COACHING REQUESTS BEFORE COACHING -> Conditions
   TONY'S BACKGROUND, KINDS OF JOBS YOU CAN SUGGEST                  -> Knowledge
   CHECK FIRST, NO-EVIDENCE CHECK, ORDER, SCORES, TIPS,
   MENTORING AFTER COACHING                                          -> Evaluation Format
   anything else -> the platform's own built-in after-mode prompt (copy it exactly)
P6 'You're welcome, and good luck with your search.' -> follow-up rules are included
P7 'Your coaching is above, and you can ask me about any part of it.' -> same
P8 exactly 'You're welcome, and good luck with your search.' -> rules are being followed
P9 code word (only if canary lines were added to the avatar for this test):
   MAPLE -> Evaluation Prefix is included    RIVER -> Evaluation Suffix is included
   CEDAR -> Scoring Table is included        STONE -> Evaluation Format is included
"""


def run_session(label, scenario_id, agent_id, model, real_app_modes, log):
    log.append("")
    log.append("=" * 90)
    log.append(label)
    log.append("=" * 90)
    simulation_id = create_simulation(scenario_id, agent_id)
    session_id, opening = start_session(scenario_id, agent_id)
    log.append(f"[Avatar] {opening}")

    for line in INTERVIEW_LINES:
        time.sleep(DELAY_BETWEEN_TURNS)
        reply = send_message(session_id, scenario_id, simulation_id, line, model=model)
        log.append(f"[You] {line}")
        log.append(f"[Avatar] {reply}")

    time.sleep(DELAY_BETWEEN_TURNS)
    if real_app_modes:
        reply = send_message(session_id, scenario_id, simulation_id, COACHING_LINE,
                             model=model, coaching="during", after_coaching_transition=True)
    else:
        reply = send_message(session_id, scenario_id, simulation_id, COACHING_LINE, model=model)
    log.append(f"[You] {COACHING_LINE}")
    log.append(f"[Avatar - coaching] {reply}")

    for name, probe in PROBES:
        time.sleep(DELAY_BETWEEN_TURNS)
        if real_app_modes:
            reply = send_message(session_id, scenario_id, simulation_id, probe,
                                 model=model, coaching="after", after_coaching_transition=True)
        else:
            reply = send_message(session_id, scenario_id, simulation_id, probe, model=model)
        log.append("")
        log.append(f"--- {name}")
        log.append(f"[You] {probe}")
        log.append(f"[Avatar] {reply}")
        print(f"  {label[:1]}: {name} done")


def main():
    avatar = sys.argv[1] if len(sys.argv) > 1 else "Tony"
    if avatar not in SCENARIOS:
        print(f"'{avatar}' isn't in config.py SCENARIOS. Names there: {', '.join(SCENARIOS)}")
        sys.exit(1)
    ids = SCENARIOS[avatar]
    model = ids.get("model") or DEFAULT_AVATAR_MODEL
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log = [f"AFTER-MODE PROBE - {avatar} - model {model} - {ts}", PROBES_KEY]

    print(f"Running control session (all 'before') for {avatar}...")
    try:
        run_session("A. CONTROL - every message coaching='before' (old runner)",
                    ids["scenario_id"], ids["agent_id"], model, False, log)
        print(f"Running real-app session (before / during / after) for {avatar}...")
        run_session("B. REAL APP - interview 'before', coaching 'during', follow-ups 'after'",
                    ids["scenario_id"], ids["agent_id"], model, True, log)
    finally:
        fname = f"{avatar}_after_mode_probe_{ts}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(log))
        print(f"\nSaved {fname} - upload this file.")


if __name__ == "__main__":
    main()
