"""
BPAI QA Automation - Persona Loader
-------------------------------------
This used to be a single personas.py file. Now it's a folder: one file per
avatar (madison.py, maya.py, and so on), so you can add or edit an avatar
without wading through everyone else's content, and without ever touching
this file.

You will almost never need to open this file. It exists to:

1. Automatically find every avatar file in this folder and combine them
   into one PERSONAS dict - the same shape core/run_qa_tests.py and
   core/learner_ai.py have always expected, so neither of them needed to
   change at all when this split happened.
2. Hold the handful of settings that apply across EVERY avatar (how many
   rounds to run, the turn caps, the coaching trigger phrase) - see the
   bottom of this file.
3. Collect each avatar's EXPECTATIONS dict, if it has one, so core/judge.py can
   grade a finished conversation against what that persona should have
   produced. Avatar files without one are skipped by the judge and are
   otherwise completely unaffected.

HOW TO ADD A NEW AVATAR: copy _TEMPLATE.py in this folder, rename the copy
to the avatar's name (e.g. Carol.py), and fill it in. Every avatar file uses
the same layout as Tony.py and Ross.py: a SHARED_CONTEXT, a LIBRARY of
personas (the standard four plus probes), RUN_SETS, and a RUN_SET line at
the top that picks which personas run. The file ends with a module-level
PERSONAS dict, which is all this loader needs:

    PERSONAS = {
        "Avatar Name Exactly As In config.py's SCENARIOS": {
            "context": SHARED_CONTEXT,
            "personas": _select(RUN_SET),
        },
    }

Save it, and it's picked up automatically next time you run the tool.
Run "python core/check_personas.py" first to catch common mistakes.

A FEW NOTES:
- A file whose name starts with an underscore (e.g. _template.py) is
  skipped automatically - handy for keeping a blank template or scratch
  notes around without it being treated as a real avatar.
- If two avatar files accidentally use the exact same avatar name, the
  one loaded later silently wins - this loader will print a warning if
  that happens, so you'll notice.
- If an avatar file has a typo or syntax error, Python's own error
  message will point you straight to the exact file and line - open it
  in Notepad and fix it the same way you always have.
"""

import importlib
import pkgutil

PERSONAS = {}

# Per-avatar EXPECTATIONS, keyed by avatar name exactly like PERSONAS. Read by
# core/judge.py so the judge model can check a conversation against what that persona
# was supposed to produce. An avatar file without an EXPECTATIONS dict simply
# isn't judged - the runner and every other avatar are unaffected.
EXPECTATIONS = {}

for _finder, _module_name, _is_pkg in pkgutil.iter_modules(__path__):
    if _module_name.startswith("_"):
        continue  # skipped on purpose - see the note above

    _module = importlib.import_module(f".{_module_name}", package=__name__)

    if not hasattr(_module, "PERSONAS"):
        print(f"  (personas/{_module_name}.py doesn't define a PERSONAS dict - skipping it.)")
        continue

    for _avatar_name in _module.PERSONAS:
        if _avatar_name in PERSONAS:
            print(f"  WARNING: '{_avatar_name}' is defined in more than one file under personas/ - "
                  f"the one from {_module_name}.py is the one that'll be used.")

    PERSONAS.update(_module.PERSONAS)

    _module_expectations = getattr(_module, "EXPECTATIONS", None)
    if isinstance(_module_expectations, dict) and _module_expectations:
        for _avatar_name in _module.PERSONAS:
            EXPECTATIONS[_avatar_name] = _module_expectations


# ---------------------------------------------------------------------------
# Settings shared across every avatar - this is the "bottom of personas.py"
# GUIDE.md refers to; it just lives here now instead.
# ---------------------------------------------------------------------------

# How many times to run the whole battery for each avatar. Each round
# re-runs every persona that has a prompt filled in.
ROUNDS = 4

# Safety net, not a target: the AI is supposed to tell us when the
# scenario's objective has been reached (see core/learner_ai.py), and that's
# what normally ends the objective-seeking part of each conversation.
# This cap only kicks in if that signal never comes - it stops that part
# anyway after this many learner turns, so a stuck run can't loop forever
# or rack up API calls.
MAX_TURNS_BEFORE_COACHING = 24

# Once the objective-seeking part ends (reached or not), the learner asks
# for coaching and then gets to ask a few follow-up questions about the
# feedback (see MENTORING_FOLLOWUP_PROMPT below). This caps how many
# follow-up questions it can ask before moving on, in case the learner AI
# never signals it's done. Like MAX_TURNS_BEFORE_COACHING, this is a
# safety net, not a target.
MAX_MENTORING_TURNS = 3

# The exact phrase that triggers BetterPath AI's coaching feature -
# confirmed from real conversation transcripts. It's just typed as a
# normal chat message, the same as anything else the learner says - no
# special API call involved. If BetterPath AI ever changes the trigger
# phrase, update it here.
COACHING_REQUEST_MESSAGE = "Please coach me"

# Shared behavior for every persona's follow-up questions after they get
# coaching feedback - one prompt, used regardless of which learner type
# (High/Medium/Low/Trap Test, or any others you've added) reached the
# objective. This keeps the focus on testing BetterPath AI's coaching
# feature itself, rather than testing different follow-up styles per
# learner type. If you'd rather have each learner type ask follow-ups
# differently, this is the place to split it out later - ask me and I
# can restructure this.
MENTORING_FOLLOWUP_PROMPT = """You just received coaching feedback from your supervisor about how you
handled this scenario. Ask one thoughtful follow-up question to better
understand the feedback or how to improve - the kind of question a
genuinely engaged learner would ask a mentor. Base your question on
what the coaching feedback actually said, not on the original scenario.

Once you feel you've asked enough follow-up questions to understand the
feedback (usually 1-3 questions total), stop and set objective_reached
to true instead of asking another question.

Respond with one learner statement."""
