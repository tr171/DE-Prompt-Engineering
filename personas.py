"""
BPAI QA Automation - Persona Loader
-------------------------------------
This used to be a personas/ folder with one file per avatar. Now each avatar
owns its own personas file inside its own folder:

    avatars/gladys/personas.py
    avatars/tony/personas.py
    ...

so everything about one avatar - its personas, the prompts you paste into the
portal, past results, findings - sits together in avatars/<name>/.

You will almost never need to open this file. It exists to:

1. Find every avatars/*/personas.py and combine them into one PERSONAS dict -
   the same shape core/run_qa_tests.py and core/learner_ai.py have always
   expected, so neither of them needed to change when this moved.
2. Hold the handful of settings that apply across EVERY avatar (how many
   rounds to run, the turn caps, the coaching trigger phrase) - see the
   bottom of this file.
3. Collect each avatar's EXPECTATIONS dict, if it has one, so core/judge.py can
   grade a finished conversation against what that persona should have
   produced. Avatar files without one are skipped by the judge and are
   otherwise completely unaffected.

HOW TO ADD A NEW AVATAR: copy the avatars/_TEMPLATE/ folder, rename the copy to
the avatar's name in lower case (e.g. avatars/carol/), and fill in its
personas.py. Every avatar file uses the same layout: a SHARED_CONTEXT, a
LIBRARY of personas (the standard four plus probes), RUN_SETS, and a RUN_SET
line at the top that picks which personas run. The file ends with a
module-level PERSONAS dict, which is all this loader needs:

    PERSONAS = {
        "Avatar Name Exactly As In config/settings.py's SCENARIOS": {
            "context": SHARED_CONTEXT,
            "personas": _select(RUN_SET),
        },
    }

Save it, and it's picked up automatically next time you run the tool.
Run "python core/check_personas.py" first to catch common mistakes.

A FEW NOTES:
- The folder name is just a folder name. The avatar name that has to match
  config/settings.py is the KEY of the PERSONAS dict inside the file, not the folder.
- A folder whose name starts with an underscore (e.g. avatars/_TEMPLATE) is
  skipped automatically - which is what keeps the blank template from being
  treated as a real avatar.
- An avatar folder with no personas.py is fine. It just means no personas have
  been written for it yet; nothing else is affected.
- If two avatar files accidentally use the exact same avatar name, the one
  loaded later silently wins - this loader will print a warning if that
  happens, so you'll notice.
- If an avatar file has a typo or syntax error, Python's own error message will
  point you straight to the exact file and line.
"""

import importlib.util
import pathlib
import sys

PERSONAS = {}

# Per-avatar EXPECTATIONS, keyed by avatar name exactly like PERSONAS. Read by
# core/judge.py so the judge model can check a conversation against what that
# persona was supposed to produce. An avatar file without an EXPECTATIONS dict
# simply isn't judged - the runner and every other avatar are unaffected.
EXPECTATIONS = {}

# folder name -> the loaded module, for tools that need to enumerate avatars
# (core/check_personas.py, core/export_portal_personas.py) rather than just
# read the combined dicts above.
MODULES = {}

_AVATARS_DIR = pathlib.Path(__file__).resolve().parent / "avatars"


def path_for(folder_name):
    """Where an avatar's personas file lives, for use in messages."""
    return f"avatars/{folder_name}/personas.py"


def load(name):
    """Find one avatar module by folder name, case-insensitively.

    Returns (folder_name, module), or (None, None) if there's no match.
    """
    for folder, module in MODULES.items():
        if folder.lower() == name.lower():
            return folder, module
    return None, None


def _load_one(folder_name, file_path):
    """Import avatars/<folder>/personas.py under a unique module name.

    The unique name matters: every one of these files is called personas.py, so
    importing them all as "personas" would make them overwrite each other - and
    would collide with this file.
    """
    mod_name = f"_avatar_personas_{folder_name}"
    spec = importlib.util.spec_from_file_location(mod_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


for _folder in sorted(_AVATARS_DIR.iterdir() if _AVATARS_DIR.is_dir() else []):
    if not _folder.is_dir() or _folder.name.startswith("_"):
        continue  # skipped on purpose - see the note above

    _file = _folder / "personas.py"
    if not _file.is_file():
        continue  # an avatar folder with no personas written yet

    _module = _load_one(_folder.name, _file)
    MODULES[_folder.name] = _module

    if not hasattr(_module, "PERSONAS"):
        print(f"  ({path_for(_folder.name)} doesn't define a PERSONAS dict - skipping it.)")
        continue

    for _avatar_name in _module.PERSONAS:
        if _avatar_name in PERSONAS:
            print(f"  WARNING: '{_avatar_name}' is defined in more than one avatars/*/personas.py - "
                  f"the one from {path_for(_folder.name)} is the one that'll be used.")

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
