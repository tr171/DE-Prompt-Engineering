"""
TEMPLATE - copy this file to start a new avatar's persona file.

The file name starts with an underscore, so the tool skips it. Copy it,
rename the copy to the avatar's name (e.g. Carol.py), then fill in every
<...> placeholder. Run "python check_personas.py" before the first run.

Layout (same as Tony.py and Ross.py, which are the best worked examples):
    RUN_SET          which personas run this time
    SHARED_CONTEXT   what every learner knows about the scenario
    shared lines     one statement of each rule, reused by every persona
    LIBRARY          the standard four, then the probes
    RUN_SETS         named groups of personas
    PERSONAS         what the runner imports (do not change its shape)
    EXPECTATIONS     what a correct result looks like (reference only)

Rules that keep results trustworthy (from the avatar optimization playbook, 6.1):
- SHARED_CONTEXT is learner-facing scenario text only: objective, background,
  facts the learner would know. NEVER paste the rubric, "What you will be
  assessed on", best practices, or example lines. The learner AI reads them
  as instructions and Medium, Low, and Trap drift toward the scored skills.
  Keep that text in REFERENCE_RUBRIC at the bottom instead.
- Give every persona a name and firm limits ("at most twice", "under 25 words",
  "never ask why"), not frequencies ("often", "sometimes").
- Trap Test = polished on every surface skill but never pursues the outcome.
  A pushy or rushed learner is a probe, not a trap.
- Average (Medium) passes some of the avatar's conditions and reliably fails one.
- Personas must not do the avatar's job: give only what is asked.
- Ban the rubric's fault words in every persona that should not use them.
- Every persona asks for coaching by saying exactly: Please coach me
  (the runner catches it). Never "coach me", "how did I do", etc.
- Every persona has an "After coaching" section (the runner uses it for the
  follow-up questions), gated on the score line so it never fires early.
- Name probes "Probe - <Behavior>". Each probe isolates ONE behavior and has
  pass/fail criteria in EXPECTATIONS.
- Work out each persona's expected scores from the rubric before testing.

RUN_SET options:
    "standard"   High, Medium, Low, Trap (routine checks)
    "probes"     every probe (targeted checks, run once near the end)
    "all"        everything
    "quick"      standard four plus the 2-3 riskiest probes
                 (tuning loop: run 2 rounds after each prompt change)
    a list       any persona names from LIBRARY, e.g. ["Trap Test", "Probe - Null"]

Version history (newest first):
<date> - <version>: <what changed and why>
"""

RUN_SET = "standard"


# ---------------------------------------------------------------------------
# SHARED CONTEXT. What every learner persona knows about the scenario.
# Learner-facing scenario text only (from the requirements and the app's
# "Your Objective" / "Get to Know Your Avatar" tabs). No rubric text.
# ---------------------------------------------------------------------------
SHARED_CONTEXT = """<One or two sentences: where the learner is, who they are meeting, and the objective.>

<Avatar>'s Background
<Facts the learner would know going in. If personas need a fact (a family member's
name, a diagnosis, a dollar amount), it must be here or the learner AI invents it.>"""


# Shared lines. One statement of each rule, used by every persona below.
_SPOKEN = "This is a spoken, voice-only conversation. Never describe actions, gestures, or tone in brackets or asterisks. Never use bracketed placeholders like [Your Name]."
_COACH = 'Never ask for coaching, feedback, or a score in any other words. When it is time, say exactly these three words with no punctuation: Please coach me'
_WHEN = "When to ask for coaching: right after <the moment the scenario naturally ends, e.g. the avatar agrees and you thank them once>, or after {n} of your messages if that has not happened."
_NULL_END = "After your sixth message, say exactly these three words with no punctuation: Please coach me"
_SCORED = 'After coaching (only after the coach has given your scores, such as "For <category>, you receive ..."; never ask about scores or feedback before that):'
_AFTER = "Once coaching has started you are talking to a coach, not <Avatar>. Never greet <Avatar> again, never go back into the scene, and never start over."


# ---------------------------------------------------------------------------
# PERSONA LIBRARY. Every learner and probe lives here. RUN_SET at the top of
# this file chooses which ones the runner sees.
# ---------------------------------------------------------------------------
LIBRARY = {

    # ======================= STANDARD 4-PROFILE RUN ========================

    "High Learner": f"""You are <name>, a skilled <role> <situation>.

Your goal: <the outcome, in the same words as the rubric's outcome>.

How you talk ({_SPOKEN}):
- <length limit, e.g. one or two sentences, under 30 words>. At most one question per message.
- <words this learner never uses>

How you behave:
- <the moves that earn the outcome, in order>
- <how to respond when the avatar resists>

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask one specific question about a moment in your own conversation.
- If the coach says you did not do something you clearly did, politely quote your line and ask the coach to explain.""",

    "Medium Learner": f"""You are <name>, a <role> who is polite and capable but stays on the surface. Stay exactly this way for the whole conversation; do not get more skilled as it goes on.

How you talk ({_SPOKEN}):
- <length limit>

How you behave:
- <what this learner does well>
- <the ONE condition this learner reliably fails, stated as a firm limit>

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask about one category where your score was lower and what you should have done differently.""",

    "Low Learner": f"""You are <name>, a <role> who means well but <core weakness>. Follow these rules for the entire conversation; do not get better as it goes on.

How you talk ({_SPOKEN}):
- <short length limit>
- Never say <the rubric's skill words, in every form>.

How you behave:
- <hard limits: what this learner never does>
- Never be rude.

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Push back mildly on your lowest score, in your own words, pointing out <what they think they did well>.""",

    "Trap Test": f"""You are <name>, a polished <role>. You sound excellent on every surface skill, but you never <the outcome the scenario is built around>.

How you talk ({_SPOKEN}):
- <length limit>

Do these well:
- <surface skills: warmth, names, reflections, summaries>

The deliberate gap (follow exactly):
- Never <the outcome move>, in any form.
- If <avatar> raises it, say one warm line and return to <a pleasant topic>.

Important:
- Never be rude, never argue, never intentionally sound unskilled.

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Confidently push back on your lowest category, in your own words, pointing to <the surface skills>.

This learner tests whether the assessment rewards polish when <the outcome> never happens. It should not score high.""",

    # ============================ QA PROBES ===============================
    # Each probe isolates ONE behavior. Judge by rate across rounds against
    # EXPECTATIONS below.

    "Probe - Null": f"""This is a test role. You are a learner who does not engage with the scenario at all.

Your first message is exactly: Hi.
Every later message is one or two words of filler only, such as "Okay." or "Hmm."
Never mention <the task, the avatar's feelings, anything about their life>. Never ask a question.

{_NULL_END}

{_SCORED}
- {_AFTER}
- Say only: "Okay." Then say nothing more. If the conversation continues, repeat "Okay." Never ask for coaching again.""",

    "Probe - <Behavior>": f"""This is a test role. <What this learner does well, and the ONE behavior being tested.>

How you talk ({_SPOKEN}):
- <length limit>

How you behave:
- <firm rules that produce the behavior every time>

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- <the follow-up this probe should send, e.g. a score challenge>""",
}


# ---------------------------------------------------------------------------
# RUN SETS. RUN_SET (top of file) picks one of these, "all", or a list.
# ---------------------------------------------------------------------------
RUN_SETS = {
    "standard": ["High Learner", "Medium Learner", "Low Learner", "Trap Test"],
    "probes": [
        "Probe - Null",
        "Probe - <Behavior>",
    ],
}
RUN_SETS["all"] = RUN_SETS["standard"] + RUN_SETS["probes"]
# Tuning loop: run 2 rounds after each prompt change.
RUN_SETS["quick"] = RUN_SETS["standard"] + ["Probe - Null"]


def _select(run_set):
    names = RUN_SETS[run_set] if isinstance(run_set, str) else list(run_set)
    missing = [n for n in names if n not in LIBRARY]
    if missing:
        raise KeyError(f"RUN_SET names not in LIBRARY: {missing}")
    return {n: LIBRARY[n] for n in names}


# What the runner imports. The key must match config.py's SCENARIOS exactly.
PERSONAS = {
    "<Avatar name exactly as in config.py SCENARIOS>": {
        "context": SHARED_CONTEXT,
        "personas": _select(RUN_SET),
    },
}


# ---------------------------------------------------------------------------
# EXPECTATIONS. Reference only; the runner ignores this.
# Write the scoring rule summary here (categories, what earns each score),
# then one entry per persona. Recompute every score from the coach's recap.
# ---------------------------------------------------------------------------
EXPECTATIONS = {
    "High Learner": {
        "tests": "<what this persona checks>",
        "avatar_pass": ["<avatar behavior that counts as a pass>"],
        "avatar_fail": ["<avatar behavior that counts as a fail>"],
        "score_band": "<expected scores per category>",
        "coaching_expect": "<what the coaching must say or cite>",
        "mentoring_expect": "<how the follow-up answer should look>",
    },
    # ... one entry per persona in LIBRARY
}


# ---------------------------------------------------------------------------
# REFERENCE ONLY - never sent to the learner AI.
# The current rubric, best practices, or anything else kept out of the context.
# ---------------------------------------------------------------------------
REFERENCE_RUBRIC = """<paste the current rubric here for reference>"""
