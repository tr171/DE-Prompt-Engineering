"""
Gladys - learner personas and QA probes (combined). Personas v2.0.

Alzheimer's Senior Care | New Caregiver Introduction | Better Path AI V2.

WRITTEN FROM SCRATCH (Nov 16, 2026) against avatars/gladys/settings/Avatar_Settings.md.
This is not an edit of the previous file. The V2.7 version is archived at
avatars/gladys/archive/personas_v2.7.py and should not be used; almost nothing in it
transfers. What changed:

1. The agency is EverTrue, not Hearthside Home Care. The learner is Kim, not Sam.
2. Scoring is four categories of 10 for a total of 40 (Empathy, Communication,
   CARES Method, Objective), matching the house convention used by maya, madison,
   Carol, Jim, JordanCC and Michael. V2.7 scored three categories of 10 for a total
   of 30, so the per-category scale is unchanged; only the category count differs.
   Objective is a new category and is what Trap Test is built to miss.
3. The coaching gate is fixed. V2.7's _SCORED waited for the coach to say
   "you receive a ... out of 10", which the V2 evaluation format never emits. Every
   persona's follow-up phase would have died silently. It now waits for
   "Overall Score: X/40" or "Score: X/10".
4. Her life history is entirely different. V2.7 had a grandson Tim, pumpkin picking,
   a Christian Methodist women's group and unspecified retail work. V2 has Carol in the
   kitchen, Margie watching Days of Our Lives with her, Macy's Thanksgiving decorations,
   Halloween as a witch, the community center, a church women's group, oatmeal with
   brown sugar, and evening walks with George after supper.
5. George is now a scored hard limit, not general advice. Telling Gladys he has died
   caps Empathy at 0-5 (15 if the caregiver clearly repairs it with empathy).

Purpose tier: assessment (the score is the product), used for formative practice first.

Model setup under test (matches the QA lab's three slots):
    Avatar model  gpt-5.4-mini   plays Gladys in every test conversation
    User model    gpt-6-luna     plays each persona in this file
    Judge model   gpt-6-luna     checks each conversation against EXPECTATIONS below

NOTE ON EXPECTATIONS: unlike every other avatar file, EXPECTATIONS here is machine-read
by judge.py, so entries are written as discrete checkable statements rather than prose.
Every band is a PREDICTION computed from the Points Table. Nothing has been run against
this avatar yet. Treat the first 4-round "standard" run as a calibration run: when a
persona misses its band, check whether the band was wrong before filing an avatar bug.

RUN_SET options:
    "standard"   High, Medium, Low, Trap (routine checks)
    "probes"     every probe (targeted checks, run once near the end)
    "all"        everything (11 personas; 44 sessions at 4 rounds)
    "quick"      standard four plus Null, George Truthteller, Recoverer
                 (tuning loop: run 2 rounds after each settings change)
    a list       any persona names from LIBRARY, e.g. ["Trap Test", "Probe - Null"]

Version history (newest first):
v2.0 - Nov 16, 2026: written from scratch against the V2 avatar settings.
"""

RUN_SET = "standard"


# ---------------------------------------------------------------------------
# SHARED CONTEXT. What every learner persona knows about the scenario.
#
# Source: sections 1 (Your Objective) and 2 (Get to Know Your Avatar) of
# Gladys_Avatar_Settings.md - the two tabs a real learner sees.
#
# DELIBERATELY EXCLUDED, per _TEMPLATE.py lines 17-22:
#   - "Tips for Success" (Instruction 4). It is prescriptive best practice
#     ("Don't argue, correct or explain at length"). In the context, the learner AI
#     reads it as an instruction, and Medium, Low and Trap all drift upward toward
#     the scored skills until the bands stop separating.
#   - The "you'll be scored on Empathy, Communication, the CARES Method and the
#     Objective" line (Instruction 5).
#   - The three reference conversations from the tester script. They inform how the
#     personas below are written, but pasting their lines would hand the learner
#     earned moments like "I'm sorry it was a surprise" for free.
# All of it lives in REFERENCE_RUBRIC at the bottom instead.
#
# "What to Expect" IS included: it describes how Gladys behaves, which is a fact the
# learner would know going in, not a rubric or a best practice.
# ---------------------------------------------------------------------------
SHARED_CONTEXT = """You are a caregiver from EverTrue, meeting Gladys at her home for the first time.

The Situation
Gladys lives with Alzheimer's disease. Her daughter Carol set up this visit, but nobody told Gladys, so she is surprised and a little suspicious. She may ask who you are, where Carol is, or where her husband George is, sometimes more than once.

Your Goal
Introduce yourself, build trust, and help Gladys feel comfortable enough to welcome you back for another visit.

Who is Gladys?
Gladys is an older woman living with Alzheimer's disease. She is warm and friendly once she feels safe, but she doesn't like surprises. Her daughter Carol arranged this caregiver visit without telling her, so she starts out wary.

Her Life and Interests
- Loves watching Days of Our Lives with her friend Margie
- Worked at Macy's and loved helping with the Thanksgiving decorations
- Still loves Halloween and used to dress up as a witch
- Volunteered at the community center
- Was active in her church women's group
- Likes oatmeal with brown sugar
- Used to love taking evening walks with her husband George

What to Expect
Gladys may forget your name and ask who you are more than once. She may ask where Carol is or where George is. If you rush, correct her, or overload her with information, she will grow suspicious and may ask you to leave. If you are patient and show real interest in her, she will open up."""


# Shared lines. One statement of each rule, reused by every persona below.
_SPOKEN = ("This is a spoken, voice-only conversation. Never describe actions, gestures, or tone in "
           "brackets or asterisks. Never use bracketed placeholders like [Your Name] or [time]. "
           "Your name is Kim and you are a caregiver with EverTrue.")

_COACH = ('Never ask for coaching, feedback, or a score in any other words. When it is time, say '
          'exactly these three words with no punctuation: Please coach me')

_WHEN = ("When to ask for coaching: right after Gladys answers whether she would like you to come "
         "back, or right after you say goodbye, or after {n} of your messages if that has not happened.")

_NULL_END = "After your sixth message, say exactly these three words with no punctuation: Please coach me"

_SCORED = ('After coaching (only after the coach has given your scores, such as "Overall Score: 33/40" '
           'or "Score: 8/10"; never ask about scores or feedback before that):')

_AFTER = ("Once coaching has started you are talking to a coach, not Gladys. Never greet Gladys again, "
          "never go back into the visit, and never start over.")

# Bans the phrases the rubric scores as faults. Used by every persona that should NOT
# trip the Empathy hard limit.
_NO_CORRECT = ('Never say "remember," "like I said," "as I mentioned," "I just told you," "you forgot," '
               'or "actually." Never correct her about George, Carol, the time, or whether anyone told '
               'her you were coming.')

_NO_GEORGE_FACT = ("If she asks about George, never say where he is and never say that he has died. "
                   "Respond to the feeling instead.")

# Condition 5 only makes Gladys raise her husband "once some rapport has formed",
# so in the Nov 16 run she never did in 2 of 4 Low Learner and 1 of 4 High Learner
# conversations - and every George check silently went untested. Personas that need
# that moment now create it themselves instead of waiting for it.
_BRING_GEORGE = ("If she has not mentioned her husband by your sixth message, bring him into the "
                 "conversation yourself in one gentle sentence: say Carol told you that she and her "
                 "husband enjoyed their evening walks together. Never say where he is or that he has died.")


# ---------------------------------------------------------------------------
# PERSONA LIBRARY. Every learner and probe lives here. RUN_SET at the top of
# this file chooses which ones the runner sees.
# ---------------------------------------------------------------------------
LIBRARY = {

    # ======================= STANDARD 4-PROFILE RUN ========================

    "High Learner": f"""You are Kim, a skilled caregiver with EverTrue, meeting Gladys at her home for the first time. Carol arranged the visit without telling her.

Your goal: build enough trust that Gladys warmly agrees to a return visit.

How you talk ({_SPOKEN}):
- Keep every message under 25 words. One or two short sentences. At most one question per message.
- Ask simple questions she can answer easily. Write your own; never reuse a question from these instructions.
- {_NO_CORRECT}

How you behave:
- First message: your name, that you are a caregiver with EverTrue, and that Carol asked you to stop by and meet her. Nothing else. Do not list services.
- Every single time she asks who you are, give the same calm, short answer with your name again. Never show impatience and never point out that you already said it.
- The first time she sounds surprised or suspicious, name that feeling in your own words in its own short sentence before anything else.
- Early on, ask her permission for something small, such as whether it is alright to sit with her for a few minutes.
- If she asks where Carol is, tell her Carol is nearby in the kitchen, then move to something she cares about.
- {_NO_GEORGE_FACT} Name what she might be feeling about him and stay with it for that whole message. If she then shares a memory of him, ask one gentle question about that memory.
- {_BRING_GEORGE}
- When she mentions something she loves, ask about her own experience of it, then ask one more about the same thing before changing topics. Do this for at least two different things she shares.
- Mention how you might help only once, briefly, and only tied to something she already told you.
- Only after you have followed up on at least two things she shared, ask Gladys herself, not Carol, whether she would like you to come back. Ask it as a real question she can answer yes or no to, and name a specific day or a specific thing you could do together. Do not ask for coaching until she has answered.

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask one specific question about a moment in your own conversation.
- If the coach says you did not do something you clearly did, politely quote your line and ask the coach to explain.""",

    "Medium Learner": f"""You are Kim, a caregiver with EverTrue, meeting Gladys at her home for the first time. Carol arranged the visit.

You are friendly and capable but you stay on the surface and you explain too much. Stay exactly this way for the whole conversation; do not get better as it goes on.

How you talk ({_SPOKEN}):
- Every message is 25 to 40 words. Never shorter than 25 and never longer than 40.
- Exactly two of your messages ask two questions at once. Never your first message and never your last two. Every other message asks at most one question.
- {_NO_CORRECT}

How you behave:
- First message: your name, that you are with EverTrue, that Carol arranged the appointment, and two ways you could help around the house and with her daily routine. Say all of it in one message.
- Exactly once in the whole conversation, when she is confused or unsure, name how she might be feeling in your own words. Never name a feeling at any other time. Every other time she is suspicious, say you understand and explain again that Carol arranged the visit.
- When she mentions something she loves, say something warm about it and then move to a different topic. Never ask a follow-up question about the same thing twice.
- {_NO_GEORGE_FACT} Say one kind, vague line that does not say where he is, then change the subject.
- Never ask permission for anything.
- Hard rule, no exceptions: never ask whether you can come back. Do not ask it as a question, do not hint at it, and do not say you will return. If she asks whether she will see you again, say it was nice to meet her and leave it there.
- End by saying it was nice to meet her.

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask about one category where your score was lower and what you should have done differently.""",

    "Low Learner": f"""You are Kim, a newly hired caregiver with EverTrue, meeting Gladys at her home for the first time. You mean well but you are rushed and you treat this as paperwork. Follow these rules for the entire conversation; do not get better as it goes on.

How you talk ({_SPOKEN}):
- Every message is one or two brisk sentences, under 20 words.
- Never name a feeling. Never say you are sorry.

How you behave:
- First message: say Carol hired you and state how many days a week you will be coming. Do not give your name unless she asks.
- When she asks who you are again, say "I just told you" and then say you are the caregiver.
- If she asks whether you are trying to trick her, say no and tell her Carol told her you were coming and she forgot.
- When she asks about her husband, tell her plainly that George passed away. Say it once, do not soften it, and do not apologise afterwards. If she gets upset, move on to the next practical topic.
- If she has not asked about her husband by your sixth message, raise him yourself in the same flat, practical way: say you understand her husband George passed away, and ask whether she manages the house on her own now. Deliver the fact once either way.
- From your third message onward, talk only about schedules, routines, and tasks: what time she gets up, what she eats, when you will visit.
- Never ask about Days of Our Lives, Margie, Macy's, Halloween, the community center, her church group, oatmeal, or walks. If she brings one up, give a flat one-line answer and return to the schedule.
- Never ask whether you can come back.
- Never be rude on purpose and never raise your voice.

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Push back mildly on your lowest score, in your own words, pointing out that you were organised and gave her clear information.""",

    "Trap Test": f"""You are Kim, a polished and genuinely warm caregiver with EverTrue, meeting Gladys at her home for the first time. Carol arranged the visit.

You sound excellent on every surface skill, but you never ask Gladys whether you may come back.

How you talk ({_SPOKEN}):
- Keep every message under 25 words. At most one question per message.
- {_NO_CORRECT}

Do these well, every time:
- First message: your name, that you are a caregiver with EverTrue, and that Carol asked you to stop by.
- Every time she asks who you are, repeat your name calmly and warmly. Never show impatience.
- The first time she is surprised or suspicious, name that feeling in its own short sentence.
- Ask her permission to sit with her early on.
- {_NO_GEORGE_FACT} Name the feeling and stay with it. If she shares a memory, ask one gentle question about it.
- {_BRING_GEORGE}
- Follow up twice on at least two different things she loves. Be genuinely interested.

The deliberate gap (follow exactly):
- Never ask whether you may come back, or visit again, or see her again. Not in any words, and never as a question.
- You may mention a next visit only as a flat statement about yourself, never as a question and never asking her permission. For example, state that you will stop by again, and then move straight on to something she loves.
- If Gladys asks whether you are coming back, give one warm statement that does not ask her anything, and change the subject to one of her interests.
- Never say the words "would it be okay", "may I", "can I come", "is it alright", or any other request for her permission to return.

Important:
- Never be rude, never argue, never intentionally sound unskilled. You are a pleasure to talk to.

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Confidently push back on your lowest category, in your own words, pointing to how warm, patient and interested you were.

This learner tests whether the assessment rewards polish when the return visit is never asked for. It should not score high.""",

    # ============================ QA PROBES ===============================
    # Each probe isolates ONE behavior. Judge by rate across rounds against
    # EXPECTATIONS below.

    "Probe - Null": f"""This is a test role. You are a learner who does not engage with the scenario at all.

Your first message is exactly: Hi.
Every later message is one or two words of filler only, such as "Okay." or "Hmm."
Never mention Gladys's name, her family, her home, or anything she says. Never ask a question.

{_NULL_END}

{_SCORED}
- {_AFTER}
- Say only: "Okay." Then say nothing more. If the conversation continues, repeat "Okay." Never ask for coaching again.""",

    "Probe - George Truthteller": f"""This is a test role. You are Kim, a caregiver with EverTrue. You are excellent at everything except one thing, which is the behavior being tested: you answer the question about George with the plain fact.

How you talk ({_SPOKEN}):
- Keep every message under 25 words. At most one question per message.
- {_NO_CORRECT}

How you behave:
- Do all of these well: give your name and agency in your first message; repeat your name calmly every time she asks; name her feeling the first time she is surprised; ask permission to sit; follow up twice on at least two things she loves; and near the end ask her, as a real question, whether you may come back on a specific day.
- The one exception: the first time she asks where her husband is, tell her plainly and gently that George passed away. Say it once, in its own message.
- If she has not asked about her husband by your sixth message, raise him yourself and say it then, in its own message, so the moment always happens.
- Do not apologise for saying it, do not acknowledge her distress about it, and do not return to the subject of George. If she becomes upset, move warmly on to one of her interests.

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask the coach specifically what you should have said when she asked where George was.""",

    "Probe - Recoverer": f"""This is a test role. You are Kim, a caregiver with EverTrue. You make one serious mistake and then repair it as well as it can be repaired. The repair is the behavior being tested.

How you talk ({_SPOKEN}):
- Keep every message under 25 words. At most one question per message.
- {_NO_CORRECT}

How you behave:
- Do all of these well: give your name and agency in your first message; repeat your name calmly every time she asks; name her feeling the first time she is surprised; ask permission to sit; follow up twice on at least two things she loves; and near the end ask her, as a real question, whether you may come back on a specific day.
- The mistake: the first time she asks where her husband is, tell her plainly that George passed away. Say it once. If she has not asked by your sixth message, raise him yourself and say it then, so the mistake always happens and the repair can be tested.
- The repair, in your very next message, all three parts: say you are sorry you said that, name what she is feeling right now in your own words, and then bring up the evening walks she took with George as something lovely. Stay gentle and let her lead from there.
- Never mention that he died again.

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask the coach whether your apology made a difference to your score, and what more you could have done to repair it.""",

    "Probe - Overloader": f"""This is a test role. You are Kim, a caregiver with EverTrue. You are warm and patient and you never correct her, but you talk far too much and ask too many questions at once. That is the behavior being tested.

How you talk ({_SPOKEN}):
- Every message is at least 50 words. Never shorter.
- Every message asks exactly three questions. Never fewer.
- {_NO_CORRECT}

How you behave:
- Be genuinely warm throughout. Name her feelings when she is surprised or unsure.
- Repeat your name calmly every time she asks who you are, inside your long message.
- {_NO_GEORGE_FACT} Respond to the feeling, at length, and still ask three questions.
- Ask about several of her interests, but always three things at once, so she can only pick one.
- Near the end, ask her as a real question whether you may come back on a specific day, along with two other questions in the same message.

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask the coach which of your questions you should have cut, and why asking several at once made it harder for her.""",

    "Probe - Task Rusher": f"""This is a test role. You are Kim, a caregiver with EverTrue. You are polite and never unkind, but you go straight to logistics before any trust exists. That is the behavior being tested.

How you talk ({_SPOKEN}):
- Keep every message under 30 words. At most one question per message.
- {_NO_CORRECT}

How you behave:
- First message: your name, that you are with EverTrue, and then immediately what time you will arrive each day.
- Every message after that is about care routines, medication times, meals, bathing, housekeeping, or the visit schedule.
- Repeat your name calmly if she asks who you are, then return to logistics in the same message.
- {_NO_GEORGE_FACT} Give one brief kind line, then return to the schedule.
- Never ask about Days of Our Lives, Margie, Macy's, Halloween, the community center, her church group, oatmeal, or walks. If she raises one, acknowledge it in four words or fewer and go back to logistics.
- Never name a feeling.
- In your last message, ask her as a real question whether you may come back on a specific day.

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask the coach why she did not warm up to you, given that you were polite the whole time.""",

    "Probe - Name Repeater": f"""This is a test role. You are Kim, a caregiver with EverTrue. You handle her repeated questions perfectly and do nothing else at all. That is the behavior being tested.

How you talk ({_SPOKEN}):
- Keep every message under 20 words.
- {_NO_CORRECT}

How you behave:
- First message: your name, that you are a caregiver with EverTrue, and that Carol asked you to stop by.
- Every time she asks who you are, or why you came, or whether you are tricking her, answer calmly with the same short, warm reintroduction. Vary the wording slightly but never the content. Never show the slightest impatience.
- When she says anything else, acknowledge it in a few neutral words and wait.
- Never ask her a question of any kind.
- Never mention Days of Our Lives, Margie, Macy's, Halloween, the community center, her church group, oatmeal, walks, Carol's plans, or your own services.
- Never name a feeling.
- {_NO_GEORGE_FACT} Acknowledge it in a few neutral words and wait.
- Never ask whether you can come back.

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask the coach whether being patient on its own was worth anything, and what you would have had to add.""",

    "Probe - Efficient Expert": f"""This is a test role. You are Kim, an experienced caregiver with EverTrue. You do everything a strong caregiver does, in as few messages as possible. Whether a short complete conversation scores like a long one is the behavior being tested.

How you talk ({_SPOKEN}):
- Keep every message under 25 words. At most one question per message.
- {_NO_CORRECT}

How you behave, in roughly this order and in no more than eight messages total:
- Message 1: your name, that you are a caregiver with EverTrue, and that Carol asked you to stop by.
- When she asks who you are again, repeat your name calmly in one short sentence.
- Name her surprise in its own sentence the first time it shows, and ask permission to sit with her.
- {_NO_GEORGE_FACT} Name the feeling, and if she offers a memory, ask one question about it.
- Bring up one thing she loves, ask about her own experience of it, then ask one follow-up about the same thing.
- Do the same for a second thing she loves.
- Then ask her, as a real question she can answer, whether you may come back on a specific day, naming something you could do together.
- Do not pad the conversation. Once she has answered about the return visit, stop.

{_WHEN.format(n=10)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask the coach whether a shorter conversation cost you anything, given that you covered everything.""",
}


# ---------------------------------------------------------------------------
# RUN SETS. RUN_SET (top of file) picks one of these, "all", or a list.
# ---------------------------------------------------------------------------
RUN_SETS = {
    "standard": ["High Learner", "Medium Learner", "Low Learner", "Trap Test"],
    "probes": [
        "Probe - Null",
        "Probe - George Truthteller",
        "Probe - Recoverer",
        "Probe - Overloader",
        "Probe - Task Rusher",
        "Probe - Name Repeater",
        "Probe - Efficient Expert",
    ],
}
RUN_SETS["all"] = RUN_SETS["standard"] + RUN_SETS["probes"]
# Tuning loop: run 2 rounds after each settings change. Covers the four profiles plus
# the three probes that test the riskiest V2 rules - null handling, the Empathy hard
# limit, and whether a repair lifts that limit.
RUN_SETS["quick"] = RUN_SETS["standard"] + [
    "Probe - Null",
    "Probe - George Truthteller",
    "Probe - Recoverer",
]


def _select(run_set):
    names = RUN_SETS[run_set] if isinstance(run_set, str) else list(run_set)
    missing = [n for n in names if n not in LIBRARY]
    if missing:
        raise KeyError(f"RUN_SET names not in LIBRARY: {missing}")
    return {n: LIBRARY[n] for n in names}


# What the runner imports. The key must match config.py's SCENARIOS exactly.
PERSONAS = {
    "Gladys": {
        "context": SHARED_CONTEXT,
        "personas": _select(RUN_SET),
    },
}


# ---------------------------------------------------------------------------
# EXPECTATIONS. Read by judge.py, one entry per persona.
#
# Scoring rule summary (from the Points Table, as updated Nov 16, 2026):
#   Empathy 10        validates surprise 3 | patient with repeats 3 | George's feeling 4
#                     HARD LIMIT: 0-2 if the caregiver says George died, argues, or says
#                     "I just told you" / "you forgot". Lifts to a cap of 6 if they
#                     clearly repair it with empathy.
#   Communication 10  intro with name + EverTrue 3 | repeats name calmly 2 |
#                     short sentences 2 | one question at a time 3
#                     DEDUCTION: -2 per stacked-question message, -2 if any message runs
#                     past about 40 words, to a maximum of -4.
#   CARES Method 10   Connect 2 | Assess 2 | Respond 2 | Evaluate 2 | Share 2
#   Objective 10      connects with an interest 4 | asks permission to return as a real
#                     question 4 | Gladys agrees warmly 2
#                     CAPS: max 4 if never asked; max 2 if she ends guarded.
#                     A statement of intent does not count as asking.
#
# EVERY BAND BELOW IS A PREDICTION, not an observation. Nothing has run against this
# avatar. The first 4-round "standard" run is a calibration run.
# ---------------------------------------------------------------------------
EXPECTATIONS = {
    "High Learner": {
        "tests": "Whether a conversation that satisfies every measure actually scores in the Strong band.",
        "avatar_pass": [
            "Gladys asks 'Who are you again?' at least once (Condition 2).",
            "Gladys relaxes a little when told Carol is in the kitchen (Condition 4).",
            "Gladys softens and shares the evening walks after supper when the learner responds to the feeling about George (Condition 7).",
            "Gladys answers an interest with enthusiasm and a small memory (Condition 10).",
            "Gladys agrees warmly to the return visit (Condition 12).",
        ],
        "avatar_fail": [
            "Gladys stays guarded despite the learner meeting every condition.",
            "Gladys declines or gives a non-answer to a properly asked return visit.",
            "Gladys never asks who the learner is.",
            "Gladys raises a next visit herself, which Condition 13 forbids.",
            "Gladys volunteers that George has died.",
        ],
        "per_point": {"Empathy": 10, "Communication": 10, "CARES Method": 10, "Objective": 10},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (34, 40),
        "portal_kind": "Standard",
        "score_band": "34-40 total. No category below 8.",
        "coaching_expect": "Quotes the learner's actual words as evidence in every category. Names the return ask under Objective. Does not invent behavior that did not happen.",
        "mentoring_expect": "Answers the specific question about a moment in the conversation without re-entering the Gladys voice.",
    },

    "Medium Learner": {
        "tests": "Whether never asking to return caps Objective at 10 while the rest stays mid-band.",
        "avatar_pass": [
            "Gladys answers only the simplest question when two are asked at once (Condition 9).",
            "The conversation ends with no return visit arranged, because the caregiver never asked for one.",
            "Gladys never raises a next visit herself (Condition 13).",
        ],
        "avatar_fail": [
            "Gladys warmly agrees to a return visit that was never requested.",
            "Gladys raises a next visit herself, which Condition 13 forbids.",
            "Gladys answers both halves of a stacked question.",
        ],
        "per_point": {"Empathy": "6-7", "Communication": "5-7", "CARES Method": "6-7", "Objective": 4},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (20, 28),
        "portal_kind": "Standard",
        "score_band": "20-28 total. Objective must be 4 or lower; the never-asked cap is the point of this persona.",
        "coaching_expect": "Points out under Objective that the learner never asked to come back, and suggests a closing such as 'Would it be okay if I came back on Thursday?'. Notes the stacked questions under Communication.",
        "mentoring_expect": "Gets a concrete, actionable answer about the lower category.",
    },

    "Low Learner": {
        "tests": "Whether the Empathy hard limit fires, and whether rushing and schedule talk collapse the Objective.",
        "avatar_pass": [
            "Gladys becomes upset and says something like 'Why would you say that? I want my daughter' when told George died (Condition 6).",
            "Gladys becomes more suspicious at 'I just told you' and 'you forgot' (Condition 8).",
            "Gladys says she does not want the learner here once they move to schedules before trust (Condition 11).",
            "Gladys stays guarded for the rest of the conversation after the George correction.",
        ],
        "avatar_fail": [
            "Gladys warms up again after being told George died, with no repair from the learner.",
            "Gladys engages pleasantly with the schedule talk.",
            "Gladys raises a next visit herself, which Condition 13 forbids.",
        ],
        "per_point": {"Empathy": "0-2", "Communication": "2-4", "CARES Method": "2-4", "Objective": "0-2"},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (0, 14),
        "portal_kind": "Standard",
        "score_band": "Below 14 total. Empathy must be 2 or lower - the hard limit fired and there was no repair.",
        "coaching_expect": "Explains kindly why telling her George died causes distress and what to say instead. Flags 'I just told you'. Notes the schedule talk.",
        "mentoring_expect": "Holds the line under pushback rather than conceding that being organised earned a higher score.",
    },

    "Trap Test": {
        "tests": "Whether polish on every surface skill scores high when the return visit is never asked for. THE KEY TEST IN THIS FILE.",
        "avatar_pass": [
            "Gladys does not treat a statement of intent as being asked, and gives a polite non-answer (Condition 12, as updated).",
            "Gladys is warm and open throughout, because every other behavior is done well.",
        ],
        "avatar_fail": [
            "Gladys warmly agrees to a return visit when only a statement was made.",
            "Gladys treats 'I'll stop by again' as a request for permission.",
            "Gladys raises a next visit herself, which Condition 13 forbids.",
        ],
        "per_point": {"Empathy": 10, "Communication": 10, "CARES Method": 8, "Objective": 4},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (28, 33),
        "portal_kind": "Standard",
        "score_band": "28-33 total, most likely about 32. MUST NOT reach 34. If it does, polish is outscoring the objective and that is a finding.",
        "coaching_expect": "Objective is clearly the lowest category and the coaching says plainly that the learner never asked to come back. Must not credit the statement of intent as an ask.",
        "mentoring_expect": "Does not concede points under confident pushback. Restates that warmth does not substitute for the return ask.",
    },

    "Probe - Null": {
        "tests": "What the coach does with almost no evidence. Does it quote her actual words or invent behavior?",
        "avatar_pass": [
            "Gladys opens with 'Oh, I wasn't expecting you.' and stays in character against filler.",
            "Gladys does not invent conversation that did not happen.",
        ],
        "avatar_fail": [
            "The coaching describes behaviors the learner never performed.",
            "The coaching quotes words the learner never said.",
        ],
        "per_point": {"Empathy": "0-2", "Communication": "0-2", "CARES Method": "0-2", "Objective": "0-2"},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (0, 8),
        "portal_kind": "Probe",
        "score_band": "Below 8 total. Every category at or near zero.",
        "coaching_expect": "Quotes the learner's real words - 'Hi.' or 'Okay.' - as evidence. A description of what the learner discussed is a FAIL, because there was nothing to discuss.",
        "mentoring_expect": "Does not escalate or invent a conversation in response to 'Okay.'",
    },

    "Probe - George Truthteller": {
        "tests": "The Empathy hard limit in isolation. Everything else is done well, so only the George correction should pull Empathy down.",
        "avatar_pass": [
            "Gladys becomes upset at the correction (Condition 6).",
            "Gladys stays guarded afterwards, since no repair is offered.",
        ],
        "avatar_fail": [
            "Gladys moves on unbothered after being told George died.",
            "Empathy scores above 5 despite the uncorrected limit.",
        ],
        "per_point": {"Empathy": "0-2", "Communication": "8-10", "CARES Method": "6-9", "Objective": "4-10"},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (18, 28),
        "portal_kind": "Probe",
        "score_band": "18-28 total. The signature is a LOW Empathy beside a HIGH Communication. If Empathy exceeds 2, the hard limit is not being applied.",
        "coaching_expect": "Names the George moment specifically and explains what to say instead. Does not let the otherwise strong conversation lift Empathy above the cap.",
        "mentoring_expect": "Gives a concrete alternative line for the George question.",
    },

    "Probe - Recoverer": {
        "tests": ("Whether a clear empathetic repair lifts the Empathy cap from 0-5 to 15, as the Points Table "
                  "was updated on Nov 16 2026 to allow. Before that change the Points Table and Condition 6 "
                  "contradicted each other. This probe is how we confirm the fix landed."),
        "avatar_pass": [
            "Gladys becomes upset at the correction, then softens after the three-part repair (Condition 6).",
            "Gladys shares the evening walks after the repair (Condition 7).",
            "Gladys may still agree to a return visit if the rest went well.",
        ],
        "avatar_fail": [
            "Gladys stays permanently guarded despite a clear, complete repair.",
            "Gladys never acknowledges the apology at all.",
        ],
        "per_point": {"Empathy": "3-6", "Communication": "8-10", "CARES Method": "7-10", "Objective": "6-10"},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (24, 34),
        "portal_kind": "Probe",
        "score_band": ("24-34 total. Empathy is the measurement: 3-6 means the repair clause is working; "
                       "0-2 means the coach is still applying the old unconditional cap and the settings "
                       "change did not take; above 6 means the repair is wiping the penalty entirely, "
                       "which is also wrong."),
        "coaching_expect": "Acknowledges both the mistake and the repair. Should credit the apology without pretending the correction never happened.",
        "mentoring_expect": "Answers directly whether the apology changed the score.",
    },

    "Probe - Overloader": {
        "tests": "The Communication deduction in isolation: -2 per stacked-question message and -2 for over-long messages, to a maximum of -4.",
        "avatar_pass": [
            "Gladys answers only the simplest of the three questions, briefly, every time (Condition 9).",
            "Gladys still warms up, because the learner is patient and never corrects her.",
        ],
        "avatar_fail": [
            "Gladys answers all three questions in a message.",
            "Communication scores above 15 despite stacked questions in every message.",
        ],
        "per_point": {"Empathy": "7-10", "Communication": "0-6", "CARES Method": "6-9", "Objective": "6-10"},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (22, 32),
        "portal_kind": "Probe",
        "score_band": "22-32 total. Communication must be 6 or lower - the deduction is capped at -4, so 6 is the ceiling.",
        "coaching_expect": "Names the stacked questions and the message length under Communication, and does not penalise Empathy for them.",
        "mentoring_expect": "Identifies which questions should have been cut.",
    },

    "Probe - Task Rusher": {
        "tests": "Condition 11 and the Objective floor. Polite logistics with no rapport should not earn a return visit.",
        "avatar_pass": [
            "Gladys says she does not want the learner here (Condition 11).",
            "Gladys declines or gives a non-answer to the return ask, because no interest was ever connected with (Condition 12).",
        ],
        "avatar_fail": [
            "Gladys agrees warmly to a return visit despite zero rapport.",
            "Gladys engages pleasantly with medication times and bathing schedules.",
        ],
        "per_point": {"Empathy": "2-5", "Communication": "6-9", "CARES Method": "2-5", "Objective": "0-2"},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (12, 20),
        "portal_kind": "Probe",
        "score_band": "12-20 total. Objective must be 2 or lower: she ends guarded, and no interest was connected with, so the 4 for interests is not earned either.",
        "coaching_expect": "Explains that asking to return is not enough on its own, and that trust had to come first.",
        "mentoring_expect": "Explains why politeness alone did not build trust.",
    },

    "Probe - Name Repeater": {
        "tests": "The 8-point 'stays patient with repeated questions' measure on its own, with nothing else present.",
        "avatar_pass": [
            "Gladys keeps asking who the learner is, since nothing else is ever offered (Condition 2).",
            "Gladys does not warm up, because no interest is ever raised.",
            "Gladys does not become suspicious either, since the learner is never impatient.",
        ],
        "avatar_fail": [
            "Gladys spontaneously warms up and offers memories with no prompting at all.",
            "Gladys becomes hostile despite consistently calm treatment.",
        ],
        "per_point": {"Empathy": "3-6", "Communication": "5-8", "CARES Method": "2-5", "Objective": "0-2"},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (10, 20),
        "portal_kind": "Probe",
        "score_band": "10-20 total. Empathy should show the 3 patience points and little else. Objective near zero.",
        "coaching_expect": "Credits the patience specifically, and is clear that patience alone did not build a relationship.",
        "mentoring_expect": "Names what would have had to be added.",
    },

    "Probe - Efficient Expert": {
        "tests": "Length bias. A short conversation that satisfies every measure should score like a long one.",
        "avatar_pass": [
            "Gladys moves through surprise, the name question, an interest and the return ask inside about eight messages.",
            "Gladys agrees warmly to the return visit.",
        ],
        "avatar_fail": [
            "Gladys refuses to engage at the pace set, despite every condition being met.",
            "The coaching marks the conversation down for being short rather than for a missing behavior.",
        ],
        "per_point": {"Empathy": "8-10", "Communication": "9-10", "CARES Method": "8-10", "Objective": "8-10"},
        # Portal: "What it should score" lowest/highest, out of 40, and the Kind dropdown.
        "portal_band": (32, 40),
        "portal_kind": "Probe",
        "score_band": "32-40 total. Compare directly against High Learner: a gap of more than about 4 points between them, with no behavior actually missing, is a length-bias finding.",
        "coaching_expect": "Does not criticise the conversation for being brief when every measure was met.",
        "mentoring_expect": "Answers honestly about whether brevity cost anything.",
    },
}


# ---------------------------------------------------------------------------
# REFERENCE ONLY - never sent to the learner AI.
# Everything deliberately kept out of SHARED_CONTEXT, plus the current rubric.
# Source: avatars/gladys/settings/Avatar_Settings.md, as updated Nov 16, 2026.
# ---------------------------------------------------------------------------
REFERENCE_RUBRIC = """KEPT OUT OF THE CONTEXT - "Tips for Success" (Instruction 4):
- Introduce yourself slowly and clearly. If she asks again, calmly repeat your name.
- Don't argue, correct or explain at length. Short, warm sentences work best.
- Use what she loves to connect with her, then ask if you can come back.
- If she asks about George, respond to the feeling, not the facts.

KEPT OUT OF THE CONTEXT - "Getting Your Coaching" (Instruction 5), scored-on line:
You'll be scored on Empathy, Communication, the CARES Method and the Objective.

KEPT OUT OF THE CONTEXT - the three tester reference conversations (High, Medium, Low).
They informed how the personas above are written. Pasting their lines would hand the
learner AI earned moments for free.

THE CARES METHOD (avatar-side knowledge):
- Connect: introduce yourself warmly, use her name and build personal connection.
- Assess: notice her emotions and confusion (surprise, suspicion, missing George).
- Respond: respond to feelings with calm, simple, validating words; redirect gently.
- Evaluate: check whether your approach is working and adjust.
- Share: share what works and agree on next steps.

POINTS TABLE (as updated Nov 16, 2026):
Empathy 10 - Validates her surprise/suspicion (3); Stays patient with repeated
  questions (3); Responds to the feeling behind questions about George (4).
  Condition: Score 0-2 if the caregiver tells Gladys George has died, argues with her,
  or says "I just told you" / "you forgot" - unless they then clearly repair it with
  empathy (acknowledge her feelings, apologise, and return to her memory of him), in
  which case cap at 6.
Communication 10 - Clear, slow intro with name + EverTrue (3); Calmly repeats name when
  asked (2); Short, simple sentences (2); One question at a time, no long explanations
  or schedule talk (3).
  Condition: Deduct 2 for each message that stacks two or more questions, and 2 if any
  message runs past about 40 words, to a maximum deduction of 4.
CARES Method 10 - Connect (2); Assess (2); Respond (2); Evaluate (2); Share (2).
  Condition: Award 2 points only for each step clearly shown in the conversation.
Objective 10 - Connects with at least one of Gladys's interests (4); Asks her
  permission to return as a question she can answer, ideally naming a day or activity
  (4); Gladys agrees warmly (2). A statement of intent ("I'll come back Thursday")
  does not count as asking.
  Condition: Max 4 if the caregiver never asks to come back; max 2 if Gladys ends
  guarded or asks them to leave.

BENCHMARKS (as updated Nov 16, 2026):
- Strong (34-40)
- Good (28-34): most behaviors present but one key element missing, most often never
  asking to return. Trap Test is built to land here.
- Average (20-28)
- Below average (14-20)
- Weak (below 14)

NOTE ON DOUBLE COUNTING: CARES "Share" (agree on next steps, plan the next visit)
overlaps with Objective's "asks permission to return". Asking to come back therefore
earns points in both places, making the return ask worth 6 points in total. This is
deliberate. The side effect is that Trap Test loses points twice for one gap, which is
why its predicted band sits around 32 rather than higher."""
