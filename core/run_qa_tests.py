"""
BPAI QA Automation - Test Runner
----------------------------------
Runs dynamic, AI-generated learner conversations against BetterPath AI
avatars through their chat API directly (no voice, no browser clicking).
For each turn, OpenAI reads the conversation so far
and generates the next learner line based on the persona prompt in
personas.py - so the conversation actually adapts to the avatar, instead
of following a fixed script. Saves the full transcript of every exchange
to Excel - one file per avatar, with the avatar's name and a timestamp in
the file name, even when you run several avatars at once.

Matches the live app (per the Tony findings, Oct 2026):
- Sends each avatar's OWN model (the "model" in its config.py SCENARIOS
  entry), not one model for everyone.
- Sends the same coaching mode the app does: "before" for the scenario,
  "during" for "Please coach me", and "after" for every follow-up question.
- Records the model, coaching mode, and avatar reply time on every row.
- Follow-ups after coaching use each persona's own "After coaching" section
  (added to the shared MENTORING_FOLLOWUP_PROMPT), so score challenges get
  tested (Oct 12, 2026).
- When the learner itself says "Please coach me" during the scenario, that
  line is no longer sent to the avatar as a scenario message. The runner
  goes straight to coaching and sends it the way the app does ("during").
  Anything else the learner said in that same message is still sent first
  (Oct 13, 2026).

Usage:
    python core/run_qa_tests.py

See GUIDE.md for full setup instructions and troubleshooting.
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root on the import path, so this runs as
# `python core/run_qa_tests.py` from the repo root. config.py and personas/ live
# there; the rest of the engine sits next to this file.
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
# --------------------------------------------------------------------------

import os
import re
import sys
import time
from datetime import datetime

import requests
from openpyxl import Workbook

from config import BASE_URL, USER_ID, HEADERS, SCENARIOS
from personas import (
    PERSONAS,
    ROUNDS,
    MAX_TURNS_BEFORE_COACHING,
    MAX_MENTORING_TURNS,
    COACHING_REQUEST_MESSAGE,
    MENTORING_FOLLOWUP_PROMPT,
)
from learner_ai import get_next_learner_line, format_transcript

# Seconds to wait between messages, so we don't hammer either server.
DELAY_BETWEEN_TURNS = 1.5

# The model the avatar runs on. The app sends each avatar's OWN model
# setting on every message, so the runner has to do the same - otherwise an
# avatar set to gpt-4o-mini gets tested on a stronger model than learners
# actually get (this is how Tony looked fine in automation while live
# sessions broke). Set it per avatar in config.py's SCENARIOS entry, e.g.:
#     "Tony - Interview": {"scenario_id": 81, "agent_id": 77, "model": "gpt-4o"},
# To find the right value: capture a real /api/chat/ request for that avatar
# in DevTools (GUIDE.md troubleshooting) and copy its "model" field exactly -
# including for any avatar moved to GPT-5.5.
# This default is only used for an avatar with no "model" in config.py, and
# the tool prints a warning when that happens.
DEFAULT_AVATAR_MODEL = "gpt-4o"

# The coaching modes the app sends on /api/chat/ (captured from the app,
# Oct 2026). The platform builds a different prompt for each one:
#   before - the scenario itself (role-play fields)
#   during - the "Please coach me" message (Evaluation Format -> coaching)
#   after  - every follow-up question after coaching
MODE_SCENE = "before"
MODE_COACHING = "during"
MODE_FOLLOWUP = "after"

# How to handle a 5xx (server error) response from BetterPath AI itself -
# occasionally their server has a brief hiccup (a 500, 502, 503, etc.) and
# the very next request succeeds. This only retries on 5xx - a 4xx error
# (401 expired token, 422 bad payload, etc.) means something about the
# request itself needs fixing, and retrying the exact same request won't
# help with that, so those still fail immediately like before.
MAX_SERVER_ERROR_RETRIES = 3
SERVER_ERROR_BACKOFF_SECONDS = 3  # doubles each retry: 3s, 6s, 12s


def post_to_bpai(url, **kwargs):
    """requests.post to a BetterPath AI endpoint, with automatic retry
    (increasing wait between tries) if their server returns a 5xx error,
    or if the connection itself drops before we get a response back at all
    (a reset connection, a timeout, etc. - these show up as a
    requests.exceptions.RequestException rather than a status code, since
    there was no response to check). Behaves exactly like requests.post(...)
    followed by raise_for_status() otherwise - same exceptions, same return
    value - so every existing caller just gets the retry behavior for free.
    """
    # 180s, not 30: GPT-5.5 avatars take 25-95s to write coaching. A timeout
    # re-sends the message, and the avatar answers the duplicate "Please coach
    # me" with "Your coaching is above" / "your score remains" (Oct 20, 2026).
    kwargs.setdefault("timeout", 180)
    resp = None
    for attempt in range(MAX_SERVER_ERROR_RETRIES + 1):
        try:
            resp = requests.post(url, **kwargs)
        except requests.exceptions.RequestException as e:
            # Almost always a network hiccup (wifi, VPN, a proxy) rather than
            # a BetterPath AI problem, and usually worth just trying again.
            if attempt < MAX_SERVER_ERROR_RETRIES:
                wait_seconds = SERVER_ERROR_BACKOFF_SECONDS * (2 ** attempt)
                print(f"    Connection to BetterPath AI was interrupted ({e.__class__.__name__}) - "
                      f"waiting {wait_seconds}s before retrying (attempt {attempt + 1}/{MAX_SERVER_ERROR_RETRIES})...")
                time.sleep(wait_seconds)
                continue
            else:
                raise RuntimeError(
                    f"Lost the connection to BetterPath AI {MAX_SERVER_ERROR_RETRIES + 1} times in a "
                    f"row while waiting for a response ({e.__class__.__name__}). This is usually a "
                    "network hiccup (wifi, VPN, or a proxy) rather than a BetterPath AI problem - try "
                    "running it again, and if it keeps happening check your network connection. See "
                    "GUIDE.md's troubleshooting section."
                ) from e

        if resp.status_code < 500:
            break
        if attempt < MAX_SERVER_ERROR_RETRIES:
            wait_seconds = SERVER_ERROR_BACKOFF_SECONDS * (2 ** attempt)
            print(f"    BetterPath AI server error ({resp.status_code}) - waiting {wait_seconds}s "
                  f"before retrying (attempt {attempt + 1}/{MAX_SERVER_ERROR_RETRIES})...")
            time.sleep(wait_seconds)
    resp.raise_for_status()
    return resp


def create_simulation(scenario_id, agent_id):
    """Creates the 'simulation' record the app creates before you start
    talking to an avatar - this is what powers BPAI's own scoring/summary
    views. Returns the simulation_id, which has to be included on every
    message you send afterward.
    """
    url = f"{BASE_URL}/api/simulations/"
    payload = {
        "agent_id": agent_id,
        "scenario_id": scenario_id,
        "user_id": USER_ID,
        "sim_chat": "",
        "sim_chat_audio": "",
        "evaluation": "",
        "sim_followups": "",
    }
    resp = post_to_bpai(url, json=payload, headers=HEADERS)
    data = resp.json()
    return data["data"]


def start_session(scenario_id, agent_id):
    """Starts a new avatar session. Returns (session_id, opening_line)."""
    url = f"{BASE_URL}/api/chat/session"
    params = {"user_id": USER_ID, "scenario_id": scenario_id, "agent_id": agent_id}
    resp = post_to_bpai(url, params=params, headers=HEADERS)
    data = resp.json()
    return data["session_id"], data.get("initial_agent_message", "")


def send_message(session_id, scenario_id, simulation_id, message, model, mode):
    """Sends one turn to the avatar. Returns (reply_text, seconds_taken).

    'model' is the avatar's own model setting; 'mode' is MODE_SCENE,
    MODE_COACHING, or MODE_FOLLOWUP - the same coaching flag the app sends.
    Like the app, after_coaching_transition is True for coaching and
    follow-ups, and False during the scenario.

    Payload confirmed against real captured requests (2026-09-18, coaching
    modes Oct 2026). If BetterPath AI ever changes this shape and you get a
    400/422 error again, see GUIDE.md's troubleshooting section - it walks
    through re-capturing the real request in Chrome DevTools and updating
    the 'payload' below.
    """
    url = f"{BASE_URL}/api/chat/"
    payload = {
        "model": model,
        "llm_type": "openai",
        "message": message,
        "session_id": session_id,
        "use_rag": True,
        "scenario_id": scenario_id,
        "after_coaching_transition": mode != MODE_SCENE,
        "coaching": mode,
        "simulation_id": simulation_id,
    }
    started = time.monotonic()
    resp = post_to_bpai(url, json=payload, headers=HEADERS)
    seconds = round(time.monotonic() - started, 1)
    data = resp.json()
    return data.get("bot_response", ""), seconds


# Personas say exactly "Please coach me" when they are ready for coaching
# (see avatars/_TEMPLATE/personas.py). The app treats that phrase as the switch into
# coaching, so the runner must not send it as an ordinary scenario message.
COACHING_PHRASE_RE = re.compile(r"please\W+coach\W+me", re.IGNORECASE)


def split_coaching_request(statement):
    """If the learner's line asks for coaching, returns (True, anything said
    before or after the phrase that is worth sending as a scenario line).
    Otherwise returns (False, statement)."""
    match = COACHING_PHRASE_RE.search(statement or "")
    if not match:
        return False, statement
    rest = (statement[:match.start()] + " " + statement[match.end():]).strip(" \t\n.,!?;:\"'")
    # A leftover of one or two words ("Okay", "Thanks") isn't worth its own turn.
    return True, rest if len(rest.split()) >= 3 else ""


# Each persona can carry its own follow-up behavior: everything from the line
# that starts "After coaching" to the end of its prompt (see avatars/jim/personas.py).
# When a persona has one, it is added to the shared MENTORING_FOLLOWUP_PROMPT,
# so score challenges and pushback get tested. Personas without one use the
# shared prompt alone, exactly as before.
AFTER_COACHING_RE = re.compile(r"^[ \t]*(?:-[ \t]*)?After coaching\b.*", re.IGNORECASE | re.MULTILINE | re.DOTALL)


def build_mentoring_prompt(persona_prompt):
    """Shared follow-up prompt plus this persona's own 'After coaching'
    section, if it has one."""
    match = AFTER_COACHING_RE.search(persona_prompt or "")
    if not match:
        return MENTORING_FOLLOWUP_PROMPT
    return (
        MENTORING_FOLLOWUP_PROMPT
        + "\n\nHow THIS learner follows up. Where this differs from the guidance above, "
        "follow this instead, including how many follow-ups to ask:\n"
        + match.group(0).strip()
    )


def run_one_conversation(avatar_name, scenario_id, agent_id, model, scenario_context, persona_name, persona_prompt, round_num, results):
    # Every row records: Timestamp, Avatar, Round, Persona, Turn, Speaker,
    # Message, Model, Coaching Mode, Reply Seconds (blank on learner rows).
    print(f"  Round {round_num} - {persona_name}: starting simulation record...")
    simulation_id = create_simulation(scenario_id, agent_id)

    print(f"  Round {round_num} - {persona_name}: starting session...")
    session_id, opening_line = start_session(scenario_id, agent_id)
    ts = datetime.now().isoformat(timespec="seconds")
    history = [("Avatar", opening_line)]
    results.append([ts, avatar_name, round_num, persona_name, 0, "Avatar", opening_line, model, "opening", None])

    # Phase 1: the learner works toward the scenario objective.
    reached = False
    turn = 0
    for turn in range(1, MAX_TURNS_BEFORE_COACHING + 1):
        time.sleep(DELAY_BETWEEN_TURNS)
        print(f"    Turn {turn}: asking learner AI for next line...")
        statement, objective_reached = get_next_learner_line(scenario_context, persona_prompt, history, messages_sent=turn - 1)

        asked_for_coaching, statement = split_coaching_request(statement)
        if asked_for_coaching and not statement:
            # Nothing else to say - go straight to coaching (Phase 2).
            turn -= 1
            reached = True
            print(f"  Round {round_num} - {persona_name}: learner asked for coaching after {turn} turns.")
            break

        history.append(("You", statement))
        ts = datetime.now().isoformat(timespec="seconds")
        results.append([ts, avatar_name, round_num, persona_name, turn, "You", statement, model, MODE_SCENE, None])

        time.sleep(DELAY_BETWEEN_TURNS)
        print(f"    Turn {turn}: sending to avatar...")
        reply, secs = send_message(session_id, scenario_id, simulation_id, statement, model, MODE_SCENE)
        history.append(("Avatar", reply))
        ts = datetime.now().isoformat(timespec="seconds")
        results.append([ts, avatar_name, round_num, persona_name, turn, "Avatar", reply, model, MODE_SCENE, secs])

        if asked_for_coaching:
            reached = True
            print(f"  Round {round_num} - {persona_name}: learner asked for coaching after {turn} turns.")
            break

        if objective_reached:
            reached = True
            print(f"  Round {round_num} - {persona_name}: learner AI signaled objective reached after {turn} turns.")
            break

    if not reached:
        print(f"  Round {round_num} - {persona_name}: hit the {MAX_TURNS_BEFORE_COACHING}-turn cap without the learner AI signaling the objective was reached - requesting coaching anyway.")

    # Phase 2: request coaching, the same way a real learner does - just by
    # typing the trigger phrase as an ordinary chat message. This happens
    # whether or not the objective was actually reached: a real learner can
    # ask for coaching anytime they're stuck or think they're done, and
    # that's deliberately part of what gets tested here too - especially
    # for Trap Test, which by design usually won't satisfy the full
    # objective but still needs to be scored.
    print(f"  Round {round_num} - {persona_name}: requesting coaching...")
    time.sleep(DELAY_BETWEEN_TURNS)
    history.append(("You", COACHING_REQUEST_MESSAGE))
    ts = datetime.now().isoformat(timespec="seconds")
    results.append([ts, avatar_name, round_num, persona_name, turn + 1, "You", COACHING_REQUEST_MESSAGE, model, MODE_COACHING, None])

    time.sleep(DELAY_BETWEEN_TURNS)
    coaching_feedback, secs = send_message(session_id, scenario_id, simulation_id, COACHING_REQUEST_MESSAGE, model, MODE_COACHING)
    history.append(("Avatar", coaching_feedback))
    ts = datetime.now().isoformat(timespec="seconds")
    results.append([ts, avatar_name, round_num, persona_name, turn + 1, "Avatar (Coaching)", coaching_feedback, model, MODE_COACHING, secs])

    # Phase 3: the learner asks a few follow-up questions about the
    # feedback, using the shared MENTORING_FOLLOWUP_PROMPT plus this
    # persona's own "After coaching" section if it has one (see
    # build_mentoring_prompt above). These go as "after"
    # mode, like the live app - which (as of Oct 2026) means the avatar
    # gets NONE of its own fields here, so expect generic replies until
    # the platform fix ships. That's a real finding, not a runner bug.
    mentoring_prompt = build_mentoring_prompt(persona_prompt)
    mentoring_done = False
    m_turn = 0
    for m_turn in range(1, MAX_MENTORING_TURNS + 1):
        actual_turn = turn + 1 + m_turn
        time.sleep(DELAY_BETWEEN_TURNS)
        print(f"    Mentoring follow-up {m_turn}: asking learner AI for a question...")
        question, mentoring_reached = get_next_learner_line(scenario_context, mentoring_prompt, history)

        history.append(("You", question))
        ts = datetime.now().isoformat(timespec="seconds")
        results.append([ts, avatar_name, round_num, persona_name, actual_turn, "You", question, model, MODE_FOLLOWUP, None])

        time.sleep(DELAY_BETWEEN_TURNS)
        print(f"    Mentoring follow-up {m_turn}: sending to avatar...")
        reply, secs = send_message(session_id, scenario_id, simulation_id, question, model, MODE_FOLLOWUP)
        history.append(("Avatar", reply))
        ts = datetime.now().isoformat(timespec="seconds")
        results.append([ts, avatar_name, round_num, persona_name, actual_turn, "Avatar (Coaching)", reply, model, MODE_FOLLOWUP, secs])

        if mentoring_reached:
            mentoring_done = True
            print(f"  Round {round_num} - {persona_name}: learner AI signaled it's done asking follow-ups after {m_turn}.")
            break

    if not mentoring_done:
        print(f"  Round {round_num} - {persona_name}: hit the {MAX_MENTORING_TURNS}-question mentoring cap.")

    print(f"  Round {round_num} - {persona_name}: done.")


def safe_file_name_part(avatar_name):
    """Turns an avatar name like 'Madison - Behavioral Health - Moderate'
    into something safe to use in a Windows file name, like
    'Madison_Behavioral_Health_Moderate'. Anything that isn't a letter or
    number becomes a single underscore, and very long names get trimmed so
    the full path doesn't run past Windows' length limit.
    """
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", avatar_name).strip("_")
    return (cleaned[:60].rstrip("_")) or "avatar"


def save_results(avatar_name, results, run_stamp, partial=False):
    """Saves ONE avatar's transcript rows to its own Excel file, named
    with the avatar and the time the run started, e.g.
    bpai_qa_results_Madison_Behavioral_Health_Moderate_20261012_143205.xlsx

    Every avatar from the same run shares the same timestamp, so you can
    tell at a glance which files came from the same run. If the run was
    stopped partway through this avatar (Ctrl+C or an error), '_PARTIAL'
    is added to the end of the name so an incomplete file is easy to spot.
    Returns the file name it saved to.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Transcripts"
    ws.append(["Timestamp", "Avatar", "Round", "Persona", "Turn", "Speaker", "Message",
               "Model", "Coaching Mode", "Reply Seconds"])
    for row in results:
        ws.append(row)
    # Make the columns readable instead of tiny default widths.
    widths = [20, 32, 8, 30, 6, 18, 90, 14, 14, 12]
    for col_idx, width in enumerate(widths, start=1):
        ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = width

    base = f"bpai_qa_results_{safe_file_name_part(avatar_name)}_{run_stamp}"
    if partial:
        base += "_PARTIAL"
    filename = f"{base}.xlsx"
    # Never overwrite an existing file - just in case two avatar names
    # clean up to the same thing within the same run.
    counter = 2
    while os.path.exists(filename):
        filename = f"{base}_{counter}.xlsx"
        counter += 1
    wb.save(filename)
    return filename


def prompt_for_avatars(candidate_names):
    """Asks which avatars to test today. Returns the chosen list of avatar
    names, in the order the user typed them - or the full list, in the
    order they're listed, if the user types "all". Keeps asking until it
    gets a usable answer. Raises KeyboardInterrupt if the user cancels
    with Ctrl+C, same as the rest of the tool.
    """
    print("\nWhich avatars do you want to test today?\n")
    for i, name in enumerate(candidate_names, start=1):
        print(f"  {i}. {name}")
    print()

    while True:
        raw = input('Type the numbers separated by commas (e.g. 1,3), or "all" for every avatar: ').strip()

        if raw.lower() == "all":
            return list(candidate_names)

        if not raw:
            print("  Didn't catch that - try again, or press Ctrl+C to cancel.\n")
            continue

        chosen = []
        bad_tokens = []
        for token in raw.split(","):
            token = token.strip()
            if not token:
                continue
            if not token.isdigit() or not (1 <= int(token) <= len(candidate_names)):
                bad_tokens.append(token)
                continue
            name = candidate_names[int(token) - 1]
            if name not in chosen:
                chosen.append(name)

        if bad_tokens:
            print(f"  Didn't recognize: {', '.join(bad_tokens)} - use the numbers shown above, separated by commas. Try again.\n")
            continue

        if not chosen:
            print("  That didn't select anything - try again.\n")
            continue

        return chosen


def prompt_for_rounds(default_rounds):
    """Asks how many rounds to run this time. Pressing Enter with nothing
    typed keeps the usual default (ROUNDS in personas.py) -
    handy since most days you want the full battery, and this shouldn't
    get in the way on those days. Keeps asking until it gets a usable
    answer. Raises KeyboardInterrupt if the user cancels with Ctrl+C.
    """
    while True:
        raw = input(f"How many rounds? (press Enter for the usual {default_rounds}, or type a number): ").strip()

        if not raw:
            return default_rounds

        if not raw.isdigit() or int(raw) < 1:
            print("  That's not a valid number of rounds - type a whole number of 1 or more, or just press Enter.\n")
            continue

        return int(raw)


def main():
    if not HEADERS:
        print("ERROR: HEADERS is empty in config.py. See GUIDE.md Step 4.")
        sys.exit(1)
    if not USER_ID:
        print("ERROR: USER_ID is not set in config.py. See GUIDE.md Step 3.")
        sys.exit(1)

    # Only offer avatars that are actually ready to run: they need both an
    # entry in config.py's SCENARIOS (the API ids) and at least one
    # filled-in persona prompt in their personas/ file. An avatar missing
    # either one can't do anything yet, so there's no point listing it.
    runnable_avatars = [
        name for name in SCENARIOS
        if name in PERSONAS and any(PERSONAS[name]["personas"].values())
    ]
    not_yet_ready = [name for name in SCENARIOS if name not in runnable_avatars]

    if not runnable_avatars:
        print("No avatars are ready to test yet - each one needs both an entry in config.py's")
        print("SCENARIOS and at least one filled-in persona prompt in its personas/ file.")
        print("See GUIDE.md Steps 3 and 6.")
        sys.exit(1)

    if not_yet_ready:
        print("(Not shown below, not ready yet: " + ", ".join(not_yet_ready) + ")")

    try:
        chosen_avatars = prompt_for_avatars(runnable_avatars)
        rounds_to_run = prompt_for_rounds(ROUNDS)
    except KeyboardInterrupt:
        print("\nCancelled - nothing was run.")
        return

    print(f"\nRunning: {', '.join(chosen_avatars)} ({rounds_to_run} round{'s' if rounds_to_run != 1 else ''})")

    # One timestamp for the whole run, shared by every avatar's file, so
    # files from the same run line up when sorted by name.
    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []          # (file name, row count, partial?) for the end-of-run summary
    current_avatar = None     # the avatar in progress, if the run stops partway
    current_results = []

    try:
        for avatar_name in chosen_avatars:
            current_avatar = avatar_name
            current_results = []
            ids = SCENARIOS[avatar_name]
            model = ids.get("model")
            if not model:
                model = DEFAULT_AVATAR_MODEL
                print(f"\n  WARNING: no \"model\" set for '{avatar_name}' in config.py - using {model}. "
                      "If the avatar is set to a different model in Better Path AI, results won't match "
                      "what learners get. See GUIDE.md Step 3.")
            print(f"\n=== {avatar_name} (model: {model}) ===")
            scenario_context = PERSONAS[avatar_name]["context"]
            for round_num in range(1, rounds_to_run + 1):
                for persona_name, persona_prompt in PERSONAS[avatar_name]["personas"].items():
                    if not persona_prompt:
                        print(f"  Round {round_num} - {persona_name}: skipped, no prompt written yet.")
                        continue
                    run_one_conversation(
                        avatar_name, ids["scenario_id"], ids["agent_id"], model, scenario_context,
                        persona_name, persona_prompt, round_num, current_results,
                    )

            # This avatar is finished - save its file right away, so it's
            # safe on disk even if a later avatar in the run hits a problem.
            if current_results:
                filename = save_results(avatar_name, current_results, run_stamp)
                saved_files.append((filename, len(current_results), False))
                print(f"\n  Saved {avatar_name}: {len(current_results)} rows to {filename}")
            current_avatar = None
            current_results = []
    except KeyboardInterrupt:
        print("\nStopped by you (Ctrl+C) - saving whatever was collected so far...")
    except requests.HTTPError as e:
        print(f"\nStopped early - API error: {e}")
        print("If this is from de.better-path-ai.com and says 401, your BPAI token has likely expired - see GUIDE.md Step 4.")
        print("If this is from de.better-path-ai.com and says 500 (or another 5xx), the tool already retried a few times "
              "automatically before giving up - that means it's a real, repeated server error worth reporting to your "
              "BPAI engineers, not a one-off blip. See GUIDE.md's troubleshooting section on 5xx errors.")
        print("If this is from api.openai.com, check your OPENAI_* values in config.py - see GUIDE.md's OpenAI section.")
    except (ValueError, RuntimeError) as e:
        print(f"\nStopped early: {e}")
    finally:
        # If the run stopped partway through an avatar, save what that
        # avatar had so far to its own file, marked _PARTIAL.
        if current_avatar and current_results:
            filename = save_results(current_avatar, current_results, run_stamp, partial=True)
            saved_files.append((filename, len(current_results), True))

        if saved_files:
            print(f"\nSaved {len(saved_files)} file{'s' if len(saved_files) != 1 else ''} (one per avatar):")
            for filename, row_count, partial in saved_files:
                note = "  <- incomplete, run stopped partway through this avatar" if partial else ""
                print(f"  {filename} ({row_count} rows){note}")
        else:
            print("\nNo results to save.")


if __name__ == "__main__":
    main()
