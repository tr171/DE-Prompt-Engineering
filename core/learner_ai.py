"""
BPAI QA Automation - Learner AI
----------------------------------
Calls OpenAI (native, not Azure) to generate the next learner line, given
a persona prompt (from personas.py) and the conversation so far. This is
what makes each conversation adapt to the avatar in real time instead of
following a fixed script.
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root on the import path, so this runs as
# `python core/learner_ai.py` from the repo root. config/settings.py and personas/ live
# there; the rest of the engine sits next to this file.
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
# --------------------------------------------------------------------------

import json
import time

import requests

from config import OPENAI_API_KEY, OPENAI_BASE_URL, USER_MODEL, USER_TEMPERATURE

# How to handle OpenAI's 429 "Too Many Requests" error. A 429 means one of
# two different things, and they need different responses:
#   - a temporary rate limit (too many requests too fast) - worth waiting
#     and retrying, since it usually clears up on its own
#   - the account has hit a hard quota/spending cap - retrying is pointless
#     until someone adds credits or raises the limit, so fail fast instead
# A full conversation now makes many more OpenAI calls than before (up to
# 24 objective turns, plus coaching, plus 3 follow-ups), so this matters
# more than it used to.
MAX_RATE_LIMIT_RETRIES = 4
RATE_LIMIT_BACKOFF_SECONDS = 5  # doubles each retry: 5s, 10s, 20s, 40s

# Appended to every persona prompt automatically - you don't need to
# repeat any of this when writing Medium/Low/Trap Test prompts.
FORMAT_INSTRUCTIONS = """

Respond with ONLY a JSON object, no other text before or after it, in
exactly this shape:
{"statement": "<your one learner statement, nothing else>", "objective_reached": true or false}

Set "objective_reached" to true only once you believe the scenario's
objective has genuinely been reached and the conversation should end.
Otherwise set it to false and keep the conversation moving naturally.
"""


def format_transcript(history):
    """history is a list of (speaker, message) tuples, speaker is 'Avatar' or 'You'."""
    lines = []
    for speaker, message in history:
        label = "Avatar" if speaker == "Avatar" else "You"
        lines.append(f"[{label}]: {message}")
    return "\n".join(lines)


def get_next_learner_line(scenario_context, persona_prompt, history, messages_sent=None):
    """
    scenario_context: the avatar's background/objective/framework (a string from personas.py's "context")
    persona_prompt: the persona's behavioral instructions (a string from personas.py)
    history: list of (speaker, message) tuples so far, oldest first
    messages_sent: how many scenario messages the learner has sent so far. When
        given, the learner is told its next message number, since the model
        can't reliably count its own lines in the transcript - without this,
        rules like "never ask before your 10th message" or "send exactly 20
        messages" get broken (Benton runs, Oct 28 2026).

    Returns (statement, objective_reached).
    """
    if not OPENAI_API_KEY or not USER_MODEL:
        raise RuntimeError(
            "OpenAI isn't configured yet - fill in OPENAI_API_KEY and USER_MODEL "
            "in config/settings.py. See GUIDE.md."
        )

    transcript_so_far = format_transcript(history)

    count_note = ""
    if messages_sent is not None:
        count_note = (f"You have sent {messages_sent} message{'' if messages_sent == 1 else 's'} so far, "
                      f"so your next message is message number {messages_sent + 1}.\n\n")

    system_prompt = (
        "SCENARIO CONTEXT (background, objective, and any required framework):\n"
        f"{scenario_context}\n\n"
        "YOUR PERSONA (how you behave as this learner):\n"
        f"{persona_prompt}"
        f"{FORMAT_INSTRUCTIONS}"
    )

    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": USER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Conversation so far:\n{transcript_so_far}\n\n{count_note}What do you say next?"},
        ],
        "response_format": {"type": "json_object"},
    }
    # Only send a temperature when one is configured. Some models (gpt-6-luna)
    # reject any explicit value with an HTTP 400 - see USER_TEMPERATURE in config/settings.py.
    if USER_TEMPERATURE is not None:
        body["temperature"] = USER_TEMPERATURE

    resp = None
    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
        except requests.exceptions.RequestException as e:
            # The connection itself dropped mid-request (reset, timeout, etc.)
            # before we ever got a response back - this is almost always a
            # network hiccup (wifi, VPN, a proxy), not an OpenAI problem, and
            # is usually worth just trying again.
            if attempt < MAX_RATE_LIMIT_RETRIES:
                wait_seconds = RATE_LIMIT_BACKOFF_SECONDS * (2 ** attempt)
                print(f"    Connection to OpenAI was interrupted ({e.__class__.__name__}) - waiting "
                      f"{wait_seconds}s before retrying (attempt {attempt + 1}/{MAX_RATE_LIMIT_RETRIES})...")
                time.sleep(wait_seconds)
                continue
            else:
                raise RuntimeError(
                    f"Lost the connection to OpenAI {MAX_RATE_LIMIT_RETRIES + 1} times in a row "
                    f"while waiting for a response ({e.__class__.__name__}). This is usually a "
                    "network hiccup (wifi, VPN, or a proxy) rather than anything wrong with your "
                    "OpenAI account or config/settings.py - try running it again, and if it keeps happening "
                    "check your network connection. See GUIDE.md's troubleshooting section."
                ) from e

        if resp.status_code != 429:
            break

        # Figure out which kind of 429 this is by looking at OpenAI's own
        # error details, not just the HTTP status code.
        try:
            error_info = resp.json().get("error", {})
        except ValueError:
            error_info = {}
        error_code = error_info.get("code", "")
        error_type = error_info.get("type", "")

        if error_code == "insufficient_quota" or error_type == "insufficient_quota":
            raise RuntimeError(
                "OpenAI says this account is out of quota/credits (this is a billing "
                "limit, not a temporary rate limit - retrying won't help). Someone who "
                "manages your org's OpenAI account needs to add credits or raise the "
                "usage limit. See GUIDE.md's troubleshooting section on 429 errors."
            )

        if attempt < MAX_RATE_LIMIT_RETRIES:
            wait_seconds = RATE_LIMIT_BACKOFF_SECONDS * (2 ** attempt)
            print(f"    OpenAI rate limit hit - waiting {wait_seconds}s before retrying (attempt {attempt + 1}/{MAX_RATE_LIMIT_RETRIES})...")
            time.sleep(wait_seconds)
        else:
            raise RuntimeError(
                f"OpenAI kept rate-limiting this request even after {MAX_RATE_LIMIT_RETRIES} "
                "retries. This usually means your org's OpenAI account has a low requests-"
                "per-minute limit - check with whoever manages it. See GUIDE.md's "
                "troubleshooting section on 429 errors."
            )

    resp.raise_for_status()
    data = resp.json()
    raw_content = data["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(raw_content)
        statement = parsed["statement"]
        objective_reached = bool(parsed.get("objective_reached", False))
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(
            f"OpenAI didn't return the expected JSON shape ({e}). "
            f"Raw response was: {raw_content!r}. See GUIDE.md's troubleshooting "
            f"section on the learner AI."
        )

    return statement, objective_reached
