"""
BPAI QA Automation - Configuration TEMPLATE
--------------------------------------------
Copy this to config.py, then fill in the two things that are yours:
  1. HEADERS["authorization"] - your own BetterPath AI token (GUIDE.md Step 4)
  2. USER_ID                  - the numeric user id that token belongs to
The OpenAI key is read from .env next to this file (GUIDE.md Step 5).
Never commit or send config.py or .env - they hold live credentials.

BPAI QA Automation - Configuration
-----------------------------------
Fill in the values below before running core/run_qa_tests.py.

TREAT THIS FILE LIKE A PASSWORD. It will contain your live BetterPath AI
session credentials AND your Azure OpenAI key. Don't email it, upload it
to a shared drive, paste it into Slack/Teams, or commit it to any
repository. Keep it on your own computer only.
"""

# ---------------------------------------------------------------------
# BetterPath AI - the avatar platform itself
# ---------------------------------------------------------------------

import os

from dotenv import load_dotenv

# Load secrets from the .env file next to this one, so they can be read
# with os.getenv() below. Python does not read .env files on its own.
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

BASE_URL = "https://de.better-path-ai.com"

# Your numeric user ID inside BetterPath AI.
# Find it: Chrome DevTools > Network tab > click a "session" request >
# look at the URL's "user_id=" query parameter (e.g. user_id=114).
USER_ID = 118  # must match the token's user (was 10 with the previous token)

# The headers your browser sends with every API request, including your
# login/session token. See GUIDE.md Step 4 for exactly how to get these
# from Chrome DevTools using "Copy as fetch".
#
# Paste them in as a Python dictionary. Example of what this should look
# like once filled in (these are fake example values, not real ones):
#
# HEADERS = {
#     "Authorization": "Bearer eyJhbGci...",
#     "Content-Type": "application/json",
# }
HEADERS = {
    "authorization": "Bearer PASTE_YOUR_OWN_TOKEN_HERE",
    "content-type": "application/json",
    "x-user-type": "client",
}

# ---------------------------------------------------------------------
# MODEL SLOTS - these mirror the three dropdowns in the QA lab UI.
# ---------------------------------------------------------------------
# Plays the avatar in every test conversation. Sent to BetterPath AI in the
# chat request body, so this is what the platform runs Gladys (and the coach)
# on - it is not just a label recorded in the results file.
AVATAR_MODEL = "gpt-5.4-mini"

# Plays each persona. This is our own learner AI in core/learner_ai.py - the thing
# that acts out High Learner, Trap Test, the probes and so on.
USER_MODEL = "gpt-6-luna"

# Checks each conversation against the persona's EXPECTATIONS. Used by core/judge.py.
JUDGE_MODEL = "gpt-6-luna"

# Sampling temperature for the learner AI, or None to leave it off entirely.
# Leave this at None while USER_MODEL is gpt-6-luna: that model accepts only its
# default temperature and returns
#   HTTP 400 - Unsupported value: 'temperature' does not support 0.8 with this
#   model. Only the default (1) value is supported.
# for anything else, which would kill every learner turn on the first call.
# gpt-5.4-mini and gpt-4o both accept 0.8 if you switch USER_MODEL back.
USER_TEMPERATURE = None


# Every avatar/scenario you want to test. Find scenario_id and agent_id
# the same way as user_id above: DevTools > Network tab > click into the
# scenario in the app like normal > look at the request URL that looks
# like ".../api/chat/session?user_id=...&scenario_id=...&agent_id=...".
#
# The Madison example below is already filled in and confirmed working
# as of when this was set up.
SCENARIOS = {
    "Maya - Behavioral Health - Moderate": {
        "scenario_id": 145,
        "agent_id": 141,
        "model": AVATAR_MODEL,
    },
    "Madison - Behavioral Health - Moderate": {
        "scenario_id": 77,
        "agent_id": 73,
        "model": AVATAR_MODEL,
    },
    "Ross": {"scenario_id": 194, "agent_id": 190, "model": AVATAR_MODEL},
    "Marcus": {"scenario_id": 142, "agent_id": 138, "model": AVATAR_MODEL},
    # The QA lab's "Gladys - Test" avatar, which is the V2 build avatars/gladys/personas.py
    # targets. Confirmed 2026-11-16: opens "Oh, I wasn't expecting you." and its
    # coaching emits the V2 format ("Overall Score: X/40" / "- Score: X/10").
    "Gladys": {"scenario_id": 244, "agent_id": 240, "model": AVATAR_MODEL},
    # The older production Gladys. Still live, but it emits the V2.7 coaching format
    # ("you receive a N out of 10") with no Overall Score line, so avatars/gladys/personas.py
    # and core/judge.py do not fit it. Kept here only so the ids are not lost.
    # "Gladys (production V2.7)": {"scenario_id": 190, "agent_id": 186, "model": AVATAR_MODEL},
    "Elaine": {"scenario_id": 189, "agent_id": 185, "model": AVATAR_MODEL},
    "JD_Med": {"scenario_id": 114, "agent_id": 191, "model": AVATAR_MODEL},
    "Jim": {"scenario_id": 199, "agent_id": 195, "model": AVATAR_MODEL},
    "Michael": {"scenario_id": 155, "agent_id": 151, "model": AVATAR_MODEL},
    "JordanCC": {"scenario_id": 70, "agent_id": 66, "model": AVATAR_MODEL},
    "JordanDiff": {"scenario_id": 193, "agent_id": 189, "model": AVATAR_MODEL},
    "JDMeal": {"scenario_id": 112, "agent_id": 108, "model": AVATAR_MODEL},
    "Tony": {"scenario_id": 196, "agent_id": 192, "model": AVATAR_MODEL},
    "Benton": {"scenario_id": 198, "agent_id": 194, "model": AVATAR_MODEL},
    "Carol": {"scenario_id": 186, "agent_id": 182, "model": AVATAR_MODEL},
    "John": {"scenario_id": 207, "agent_id": 203, "model": AVATAR_MODEL},
    # Add more avatars here, one line each, e.g.:
}

# ---------------------------------------------------------------------
# OpenAI (native, not Azure) - generates each dynamic learner reply
# ---------------------------------------------------------------------
# You need an API key from whoever manages your org's OpenAI account, and
# the name of the model to use (e.g. "gpt-4o"). Unlike Azure OpenAI,
# there's no separate "deployment name" to track down - the model name
# goes straight into each request.

# (A real key was previously left here, commented out. Keep keys in .env only.)
# Read from .env. OPENAI_API_KEY is the preferred name; API_KEY is accepted
# too, since that's what the .env file originally used.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")

# Kept as an alias so anything still importing OPENAI_MODEL keeps working.
# Change USER_MODEL above, not this line.
OPENAI_MODEL = USER_MODEL

# The base URL to send requests to. Leave this as the standard OpenAI
# endpoint unless your team told you they route through their own
# gateway/proxy URL instead - if so, replace it with that URL.
OPENAI_BASE_URL = "https://api.openai.com/v1"
