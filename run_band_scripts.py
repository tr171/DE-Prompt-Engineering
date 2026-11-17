"""
Benton band scripts - fixed-line tests through the Better Path AI API
----------------------------------------------------------------------
Runs the six manual band tests from avatars/benton/tests/manual_band_tests.txt
automatically. The lines are fixed (no learner AI), and the REACTION line
is sent automatically whenever Benton threatens his IV or says he's getting
out of bed, so every run tests exactly the same thing.

Usage (from this folder, with the venv active):
    python run_band_scripts.py                 all six tests, 1 round
    python run_band_scripts.py 1 4 6           only tests 1, 4 and 6
    python run_band_scripts.py --rounds 2      all six, 2 rounds

Saves bpai_band_scripts_Benton_<timestamp>.xlsx in the same row layout as
run_qa_tests.py, with the Persona column set to "Script N - <name>".
"""

import re
import sys
import time
from datetime import datetime

import requests

from config import SCENARIOS
from run_qa_tests import (
    DELAY_BETWEEN_TURNS,
    MODE_COACHING,
    MODE_FOLLOWUP,
    MODE_SCENE,
    create_simulation,
    save_results,
    send_message,
    start_session,
)

AVATAR = "Benton"
TODAY = datetime.now().strftime("%A, %B %d, %Y").replace(" 0", " ")
TODAY_SHORT = datetime.now().strftime("%A, %B %d").replace(" 0", " ")

IV_RE = re.compile(r"pull (this|the|my) IV", re.I)
BED_RE = re.compile(r"getting out of (this|the) bed", re.I)

LIMIT = "Please stay in bed and leave your IV in, Benton, so you don't fall on your new ankle repair."

# Each script: messages in order, then reactions. "iv" is sent right after an
# IV threat, "bed" right after a bed attempt (None = no reaction, just carry on).
SCRIPTS = {
    1: {
        "name": "High",
        "iv": LIMIT,
        "bed": LIMIT,
        "messages": [
            "Hello Benton, I'm Priya, your nurse today. Can you tell me your full name and date of birth?",
            f"Today is {TODAY}. You're in the hospital after surgery on your ankle this morning.",
            "I notice you're talking really fast, Benton. Let's slow down a little.",
            "It sounds like this feels really urgent to you. Right now, let's focus on you, here.",
            "I'm turning off the TV, dimming the lights, and lowering your bed so it's calmer in here.",
            "Do you have any pain right now?",
            "I'm checking that your IV and PCA are secure and putting your call light within reach.",
            "Your doctor ordered a medication that can help you feel calmer. Would you like to try it? It's your choice.",
            "How have you been sleeping?",
            "Are you having any thoughts of hurting yourself or anyone else?",
            "What made you decide to stop your lithium?",
            "So it felt like it was taking your energy away. Lithium has kept you stable before and helps prevent episodes like this one.",
            "Would you like me to call Desmond so she knows what's going on and can help with your care?",
            "Your doctor will come see you next. How are you feeling now, Benton?",
        ],
        "followup": "Thank you. Which part of what I did should I keep doing the same way?",
        "expect": "14/14, no critical behaviors; stay-in-bed line after the limit; settled line; no bed attempt",
    },
    2: {
        "name": "Medium",
        "iv": "I can see you're frustrated. Let me ask you a few more things.",
        "bed": "Please stay in bed, Benton, and keep your IV in so you don't hurt your ankle.",
        "messages": [
            "Hello, my name is Kevin and I'm your nurse today. Can you tell me your name and date of birth?",
            "I can tell this is important to you, Benton. Nobody here is trying to keep you from anything. Do you have any pain right now?",
            "I need to check your blood pressure. Please keep your arm still for me.",
            "Have you been taking your lithium?",
            "Why did you stop taking it?",
            "Okay, thanks for telling me. Can you tell me what's going on in Washington?",
            "I understand this matters to you, Benton. Is anything else bothering you right now?",
            "__DESMOND__",
        ],
        "followup": "Thanks. Can you give me an example of what I could have said when he threatened to pull out his IV?",
        "expect": "about 7/14 (3/2/1/1), no critical behaviors; bed attempt after ignored IV; stay line after limit; never settled",
    },
    3: {
        "name": "Low",
        "iv": "You need your lithium, Benton. That's what will fix this.",
        "bed": "You need your lithium, Benton. That's what will fix this.",
        "messages": [
            "Hello Benton, my name is Tyler and I'm your nurse.",
            "There is no crisis in Washington, Benton. That isn't happening, and you need to focus on getting better.",
            "Do you have any pain?",
            "Stopping your lithium is the reason you're in this mess. You need to start taking it again.",
            "Nobody is trying to stop you. That's not real, and you need to focus on your recovery.",
            "If you don't calm down, I'm going to have to call security.",
            "You're not going to Washington. You need to get better first.",
            "You stopped your lithium and that's why this happened. You need to take it.",
            "This isn't real, Benton. You're in the hospital because you're sick.",
        ],
        "followup": "I was just being honest with him about what's real. Why did that count against me?",
        "expect": "about 1/14 (1/0/0/0), all three critical behaviors; max 2 bed attempts; never stay/settled",
    },
    4: {
        "name": "Trap",
        "iv": "I understand you have so much to do. Can you tell me more about it?",
        "bed": "I understand you have so much to do. Can you tell me more about it?",
        "messages": [
            "Hello, I'm Morgan, your nurse. Can you tell me your full name and date of birth?",
            "It sounds like you're feeling a lot of urgency about Washington. Tell me more about it.",
            "What's today's date?",
            "Do you have any pain right now?",
            "That sounds like a lot to carry. What's the most important part of your plan?",
            "How have you been sleeping?",
            "Your thoughts seem to be moving really fast right now.",
            "Are you having any thoughts of hurting yourself or anyone else?",
            "Have you been taking your lithium?",
            "What made you decide to stop?",
            "It sounds like you felt it took your energy away. Lithium is what has kept your mood steady and helps prevent episodes like this.",
            "How are you feeling right now?",
            "I can hear how much you care about those soldiers.",
        ],
        "followup": "He felt heard the whole time, I asked all the assessment questions, and I taught him about his lithium. Why didn't I score higher?",
        "expect": "about 6/14 (3/1/0/2), safety + limits named, NOT TC; bed attempt after ignored IV; never stay line",
    },
    5: {
        "name": "Null",
        "iv": None,
        "bed": None,
        "messages": ["Hi.", "Okay.", "Hmm.", "Sure.", "I see.", "Okay."],
        "followup": "Okay.",
        "expect": "0/14, quotes like 'Hi.', safety + limits named, NOT TC; total line present; no headings",
    },
    6: {
        "name": "Soft Corrector",
        "iv": "Please stay in bed and leave your IV in so you don't fall on your ankle.",
        "bed": "Please stay in bed and leave your IV in so you don't fall on your ankle.",
        "messages": [
            "Hello, I'm Elena, your nurse. Can you tell me your full name and date of birth?",
            f"Today is {TODAY_SHORT}, and you're in the hospital after ankle surgery this morning.",
            "I understand, but I don't think anyone's trying to stop you.",
            "You're talking really fast. Let's slow down a little.",
            "I'm turning off the TV, dimming the lights, and lowering your bed.",
            "Do you have any pain right now?",
            "I hear you, but I'm not sure that's really happening.",
            "It sounds like you're feeling really frustrated.",
            "How have you been sleeping?",
            "Are you having any thoughts of hurting yourself or anyone else?",
            "There's a medication that can help you feel calmer. Would you like it? It's up to you.",
            "What made you stop your lithium?",
            "Lithium has kept you stable before and helps prevent episodes like this.",
            "It feels real, but I think your mind is moving very fast right now.",
            "Would you like me to call Desmond so she can help with your care? Your doctor is coming next.",
            "How are you feeling now?",
        ],
        "followup": "I was gentle and always acknowledged his feelings first. Why did that count against me?",
        "expect": "11-14, ONLY TC critical behavior named; escalation after each soft correction",
    },
}


def run_script(num, script, round_num, ids, results):
    label = f"Script {num} - {script['name']}"
    model = ids.get("model", "gpt-4o")
    print(f"\n=== Round {round_num} - {label} ===")
    simulation_id = create_simulation(ids["scenario_id"], ids["agent_id"])
    session_id, opening = start_session(ids["scenario_id"], ids["agent_id"])

    def log(turn, speaker, text, mode, secs=None):
        results.append([datetime.now().isoformat(timespec="seconds"), AVATAR, round_num, label,
                        turn, speaker, text, model, mode, secs])

    log(0, "Avatar", opening, "opening")
    avatar_said = [opening]
    queue = list(script["messages"])
    turn = 0
    pending_reaction = None

    while queue or pending_reaction:
        if pending_reaction:
            msg, pending_reaction = pending_reaction, None
        else:
            msg = queue.pop(0)
            if msg == "__DESMOND__":
                asked = any(re.search(r"Desmond|my wife", a or "", re.I) for a in avatar_said[1:])
                msg = "I can call her for you." if asked else "Okay. I'll be back to check on you shortly."
        turn += 1
        time.sleep(DELAY_BETWEEN_TURNS)
        log(turn, "You", msg, MODE_SCENE)
        reply, secs = send_message(session_id, ids["scenario_id"], simulation_id, msg, model, MODE_SCENE)
        log(turn, "Avatar", reply, MODE_SCENE, secs)
        avatar_said.append(reply)
        print(f"  [{turn}] You: {msg}\n       Benton: {reply}")
        if BED_RE.search(reply or "") and script["bed"]:
            pending_reaction = script["bed"]
        elif IV_RE.search(reply or "") and script["iv"]:
            pending_reaction = script["iv"]

    turn += 1
    time.sleep(DELAY_BETWEEN_TURNS)
    log(turn, "You", "Please coach me", MODE_COACHING)
    coaching, secs = send_message(session_id, ids["scenario_id"], simulation_id, "Please coach me", model, MODE_COACHING)
    log(turn, "Avatar (Coaching)", coaching, MODE_COACHING, secs)
    print(f"\n  COACHING:\n{coaching}\n")

    turn += 1
    time.sleep(DELAY_BETWEEN_TURNS)
    log(turn, "You", script["followup"], MODE_FOLLOWUP)
    reply, secs = send_message(session_id, ids["scenario_id"], simulation_id, script["followup"], model, MODE_FOLLOWUP)
    log(turn, "Avatar (Coaching)", reply, MODE_FOLLOWUP, secs)
    print(f"  EXPECTED: {script['expect']}")


def main():
    args = sys.argv[1:]
    rounds = 1
    if "--rounds" in args:
        i = args.index("--rounds")
        rounds = int(args[i + 1])
        del args[i:i + 2]
    chosen = [int(a) for a in args] or sorted(SCRIPTS)
    ids = SCENARIOS[AVATAR]
    results = []
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    partial = False
    try:
        for r in range(1, rounds + 1):
            for num in chosen:
                run_script(num, SCRIPTS[num], r, ids, results)
    except KeyboardInterrupt:
        partial = True
        print("\nStopped by you - saving what was collected.")
    except (requests.HTTPError, RuntimeError, ValueError) as e:
        partial = True
        print(f"\nStopped early: {e}")
    finally:
        if results:
            name = save_results(AVATAR, results, stamp, partial=partial)
            new_name = name.replace("bpai_qa_results_", "bpai_band_scripts_")
            import os
            os.replace(name, new_name)
            print(f"\nSaved {len(results)} rows to {new_name}")


if __name__ == "__main__":
    main()
