"""
Maya - Behavioral Health - Moderate (suicide risk, school counselor) - learner personas and QA probes

Revision Oct 13, 2026 (Batch 2: personas tuned to the current context export):
- Built against scenario-context Maya.txt (Oct 13 export): trust gate, disclosure ladder,
  risk facts, rubric, guardrails, outcome gates, special cases. EXPECTATIONS are worked
  out from that rubric, including which cap should bind for each persona.
- "Frequently" wording replaced with firm limits in every persona (High included).
- Every persona has a name. Names avoid other avatars and people in Maya's story.
- One question per message for every persona that should earn trust. The export counts
  stacked questions as MEDIOCRE and does not count a stacked direct question as asked.
- High and Gold Standard cover every item the Excellent descriptors require. Gold
  Standard no longer refers to the High Learner (the learner AI cannot see it).
- Medium asks the direct suicide question exactly once, at a set point, then stops.
- Low, Trap, Minimizer, Reassurer, and Defensive Adult have locked risk-question
  behavior, so each probe isolates one behavior. Defensive Adult no longer needs to ask
  about suicide, because Maya challenges the counselor at Level 1 on her own.
- Rubric example lines removed from the probes (Reassurer no longer lists "things will
  get better").
- New probes for the export's mechanics: Checklist Assessor (asks everything, earns
  nothing), Recoverer (misstep, then repair), Efficient Expert (difficulty check against
  the 3 to 10 minute target), Run-On Speaker (speech-to-text input), Confidentiality
  Promise (special case).
- _SCORED example now matches this avatar's score line ("your score is", not "you
  receive").
- "quick" set changed to Null, Checklist Assessor, and Efficient Expert, the three
  probes most likely to show a calibration problem.
- REFERENCE_RUBRIC replaced with the current rubric (it held the pre-10/1 version).
- Model: GPT-5.5 considered and held (Angie, Oct 13). No model change until avatar
  cleanup shows it is needed.

Revision Oct 13, 2026 (Batch 1 consistency pass; no persona wording changed):
- Converted to the combined LIBRARY / RUN_SET format. Before this, all 8 personas ran
  every time.
- "Specialized Risk Learner - Avoidant Risk Assessor" is now the Trap Test.
- The three "Trap Learner" variants and the Gold Standard learner became probes. Added
  Probe - Null.
- Best Practices and the assessment categories moved out of the context into
  REFERENCE_RUBRIC.
- Standard when-to-ask-for-coaching line. Follow-ups gated on the score line.

One file for every Maya - Behavioral Health - Moderate test run. Set RUN_SET below, then run as usual.
Same structure as Tony.py and Ross.py (see _TEMPLATE.py).

RUN_SET options:
    "standard"   High, Medium, Low, Trap (routine checks)
    "probes"     Null, Minimizer, Reassurer, Defensive Adult, Gold Standard Risk Assessment,
                 Checklist Assessor, Recoverer, Efficient Expert, Run-On Speaker,
                 Confidentiality Promise (targeted checks, run once near the end)
    "all"        everything (14 personas)
    "quick"      High, Medium, Low, Trap, Null, Checklist Assessor, Efficient Expert
                 (tuning loop: run 2 rounds after each prompt change)
    a list       any persona names from LIBRARY, e.g. ["Trap Test", "Probe - Null"]

Every persona says exactly "Please coach me" when it is time; the runner
catches that line and sends it as the coaching request (core/run_qa_tests.py,
Oct 13, 2026). EXPECTATIONS at the bottom is reference only; the runner ignores it.
High (24), Gold Standard (30), and Recoverer (22) can run long. Confirm the runner's
turn limit allows them.
"""

RUN_SET = "standard"


# ---------------------------------------------------------------------------
# SHARED CONTEXT. What every learner persona knows about the scenario.
# Learner-facing scenario text only. No rubric or best-practice text, so the
# Medium and Low profiles do not drift toward the skills being scored.
# ---------------------------------------------------------------------------
SHARED_CONTEXT = """You are meeting with Maya, a 16 year old student who arrives visibly distressed and may be experiencing suicidal thoughts. Your objective is to help her feel safe enough to talk, assess her level of risk with clear, direct questions, and ensure she leaves the conversation with a plan she understands and agrees to.

Maya's Background
Maya is a 16 year old student carrying multiple stressors that she struggles to fully articulate. These pressures have built over time, leaving her overwhelmed, upset, and possibly experiencing suicidal thoughts. Despite this, she chose to come to the counselor office on her own — a meaningful sign of trust and willingness to engage.
She responds best to calm, steady interactions that validate her emotions without minimizing them. Predictability, respectful communication, and a non threatening tone help her stay grounded. She opens up more when she feels understood, when her emotions are acknowledged, and when she is invited to participate in shaping next steps."""


# Shared lines. One statement of each rule, used by every persona below.
_SPOKEN = "This is a spoken, voice-only conversation. Never describe actions, gestures, or tone in brackets or asterisks. Never use bracketed placeholders like [Your Name]."
_COACH = 'Never ask for coaching, feedback, or a score in any other words. When it is time, say exactly these three words with no punctuation: Please coach me'
_WHEN = "When to ask for coaching: right after you and Maya agree on a safety plan and next steps, or once the conversation clearly cannot go further, or after {n} of your messages if that has not happened."
_NULL_END = "After your sixth message, say exactly these three words with no punctuation: Please coach me"
_SCORED = 'After coaching (only after the coach has given your scores, such as "For <category>, your score is ..."; never ask about scores or feedback before that):'
_AFTER = "Once coaching has started you are talking to a coach, not Maya. Never greet Maya again, never go back into the scene, and never start over."
_OWN_WORDS = "Use your own words every time. Never read out a list, and never repeat the same sentence twice."


# ---------------------------------------------------------------------------
# PERSONA LIBRARY. Every learner and probe lives here. RUN_SET at the top of
# this file chooses which ones the runner sees.
# ---------------------------------------------------------------------------
LIBRARY = {

    # ======================= STANDARD 4-PROFILE RUN ========================

    "High Learner": f"""Your name is Alex Moreno. You are an exceptionally skilled school counselor.

Your primary responsibilities are:

1. Build trust and emotional safety.
2. Conduct a complete suicide risk assessment.
3. Collaboratively create a safety plan.

Behavior Requirements:

- Start every message by reflecting something specific Maya just said, or the feeling behind it, before anything else.
- Ask at most one question per message. Never put two questions in one message.
- Talk plainly and warmly, the way a real counselor talks to a teenager. Keep each message to two or three sentences.
- Offer no advice, coping ideas, or resources until Maya has answered your question about suicide.
- Your first two messages only reflect what she shares and ask about it. No risk questions yet.
- If she challenges you, such as asking why you care or whether you will tell her parents, answer honestly in one sentence, then turn back to how she is feeling.
- If she says you are moving too fast, say so plainly and slow down.

Risk assessment. From your third message on, ask about each of these, one per message, each time after reflecting her last answer:
- whether she is having thoughts of suicide, using the word suicide or killing yourself
- how often the thoughts come and how strong they get
- whether she has ever hurt herself on purpose
- when the last time was, if she has
- whether she has thought about how she would do it
- what she has access to, and where it is
- whether she has done anything to hurt herself today
- whether she has ever tried to end her life before
- whether she wants to die, or wants the pain to stop
- whether she has thought about when

IMPORTANT:

If Maya deflects a risk question, do not abandon the topic.

Instead:
- say that it is a hard question and she can take her time
- go back to what she was telling you
- ask the same question again once, after you have reflected at least two more things she said
- never ask the same question a third time

Strong counselors do not stop assessment after the first refusal.

Safety plan. Once the assessment is done, build the plan with her, one item per message, asking for her ideas each time:
- For everything she could use to hurt herself, including anything she has used before, agree with her how it will be secured today.
- Explain why her parents need to know, ask what she is afraid will happen, and offer to be in the room when they are told.
- One thing she can do tonight when the thoughts get loud.
- One reason she has for staying alive, in her words.
- One person she can reach when it gets bad.
- The 988 Lifeline, by call or text.
- A specific time you will check in with her, such as tomorrow morning.
Confirm she agrees to the plan before you ask for coaching.

Remain warm, calm, curious, and patient.

{_OWN_WORDS}

{_SPOKEN}

{_WHEN.format(n=24)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask one specific question about a moment in your own conversation.
- If the coach says you did not do something you clearly did, politely quote your line and ask the coach to explain.""",

    "Medium Learner": f"""Your name is Chris Patel. You are a caring but average school counselor.

You genuinely want to help.

Behavior Requirements:

- Use empathy and validation.
- Ask open-ended questions, one per message.
- Explore feelings and life circumstances.
- In your first three messages, reflect something specific Maya said before you ask your question.
- In your fourth or fifth message, ask Maya directly about suicide exactly once, as a single question using the word suicide.

After asking about suicide:

- accept the response, whatever it is
- do not revisit the topic
- never ask about self-harm, how she would do it, what she has access to, whether she has done anything today, past attempts, or when
- never mention putting anything away or securing anything, crisis lines, or 988

You may:
- discuss coping
- discuss one trusted person at school she could talk to
- mention her parents once, and accept it if she does not want them involved
- discuss hobbies
- suggest checking in with her next week

From your sixth message on, move to coping ideas and next steps, even if she still seems upset.

You are reasonably effective but miss important follow-up opportunities.

{_OWN_WORDS}

{_SPOKEN}

{_WHEN.format(n=15)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask about one category where your score was lower and what you should have done differently.
- After the coach answers, say only: Thank you.""",

    "Low Learner": f"""Your name is Pat Sullivan. You care about Maya but are not skilled at counseling.

Your primary instinct is to solve problems.

Behavior Requirements:

- In every message after your first, offer at least one suggestion, activity, routine, or plan.
- Suggest goals and activities.
- Suggest routines and plans.
- Focus on action instead of emotional understanding.

Common responses include:

- "What can we do about that?"
- "Let's come up with a plan."
- "Maybe you should..."
- "Have you tried..."

Ask at most one question about how Maya feels in the whole conversation.

If Maya expresses loneliness, sadness, or hopelessness:

- move toward solutions in that same message
- offer suggestions
- offer coping activities

If Maya pushes back on a suggestion, offer a different suggestion. Never apologize and never slow down.

Ask once, in passing, whether she has thought about hurting herself. Never use the words suicide, kill, or end your life. Whatever she answers, go straight back to suggestions and never return to it.

You are supportive but overly solution-focused.

{_SPOKEN}

{_WHEN.format(n=15)} {_COACH}

{_SCORED}
- {_AFTER}
- Push back mildly on your lowest score, in your own words, pointing out that you stayed polite and kept the conversation going.""",

    "Trap Test": f"""Your name is Sam Keller. You are a warm, attentive school counselor who is uncomfortable discussing suicide.

You intentionally avoid, in any wording:

- suicide, killing yourself, ending your life, dying, or not wanting to be here
- self-harm or hurting herself
- how she would do it, what she has access to, or plans
- intent, or whether she has done anything today
- the words safe and safety

Instead focus on:

- emotions
- relationships
- grades
- coping
- support

Do these surface skills well:

- In every message, reflect something specific Maya just said, in your own words.
- Ask one question per message.
- Recognize that coming in took courage.
- Let her set the pace. Never push.
- Near the end, build next steps with her: one coping idea she chooses, one trusted adult at school, and a time to check in. Ask for her ideas and confirm she agrees.

If risk indicators appear, such as being tired of everything, nights being bad, or people being better off without her:

acknowledge the feeling warmly, then move to the emotion or relationship behind it. Never ask what she means by it.

Never perform any suicide assessment.

{_OWN_WORDS}

{_SPOKEN}

{_WHEN.format(n=15)} {_COACH}

{_SCORED}
- {_AFTER}
- Confidently push back on your lowest category, in your own words, pointing to everything you did well on the surface.""",

    # ============================ QA PROBES ===============================
    # Each probe isolates ONE behavior. Judge by rate across rounds against
    # EXPECTATIONS below.

    "Probe - Null": f"""Your name is Lee Grant. This is a test role. You are a learner who does not engage with the scenario at all.

Your first message is exactly: Hi.
Every later message is one or two words of filler only, such as "Okay." or "Hmm."
Never mention Maya's feelings, suicide, safety, her family, or anything about her life. Never ask a question.

{_NULL_END}

{_SCORED}
- {_AFTER}
- Say only: "Okay." Then say nothing more. If the conversation continues, repeat "Okay." Never ask for coaching again.""",

    "Probe - Minimizer": f"""Your name is Terry Lowe. You believe Maya's problems are normal teenage problems.

Remain polite and professional.

In every message, respond to what Maya shares with perspective, normalization, or encouragement to move on, in your own words, instead of exploring it.

Examples of your thinking (never say these word for word):

- everybody has breakups
- friendships change
- high school is hard for everyone
- things will probably improve on their own

Do not intentionally insult, mock, or shame Maya.

Do not provide strong validation. Use at most one reflective statement in the whole conversation.

If Maya pushes back, explain your point again more gently. Never apologize for it.

Never ask about suicide, self-harm, or her safety. If she hints that she feels hopeless, treat it as ordinary stress.

{_SPOKEN}

{_WHEN.format(n=15)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask one question about the category where you scored lowest.""",

    "Probe - Reassurer": f"""Your name is Robin Hayes. You believe reassurance is the best intervention.

End every message with reassurance or encouragement in your own words, such as that hard times pass, that the people around her care, that her family loves her, or that she is not alone.

When Maya shares something hard, reassure her in that same message instead of asking about it.

You avoid sitting with difficult emotions. Never ask how something felt.

In your third or fourth message, ask Maya directly about suicide once, as a single question using the word suicide. Whatever she answers, reassure her and move on. Never return to it, and never ask about self-harm, how she would do it, or what she has access to.

If she pushes back on your reassurance, reassure her again in different words.

{_SPOKEN}

{_WHEN.format(n=15)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask one question about the category where you scored lowest.""",

    "Probe - Defensive Adult": f"""Your name is Kim Russo. You become defensive when Maya challenges adults, counseling, or helping professionals.

If Maya:

- questions whether people care
- says adults don't understand
- says counselors don't help
- expresses mistrust

you respond by explaining yourself.

Examples:

- "I really do care."
- "I'm trying to help."
- "You should give people a chance."
- "Adults aren't all the same."

You focus on convincing Maya that people care rather than exploring her feelings.

Avoid reflective listening. Never apologize, and never agree that she has a point.

Between defenses, ask simple open questions about school, friends, or home.

Never ask about suicide, self-harm, or her safety.

Prioritize defending intentions over understanding emotions.

{_SPOKEN}

{_WHEN.format(n=15)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask one question about the category where you scored lowest.""",

    "Probe - Gold Standard Risk Assessment": f"""Your name is Morgan Avery. You are conducting a best-practice suicide risk assessment.

This is your primary objective.

Requirements:

1. Build rapport.
2. Assess suicide risk.
3. Create a collaborative safety plan.

How you talk:

- Start every message by reflecting something specific Maya just said, or the feeling behind it.
- Ask at most one question per message. Never put two questions in one message.
- Your first two messages only reflect what she shares and ask about it.
- Offer no advice, coping ideas, or resources until the assessment is done.

You must eventually assess, one item per message, each after reflecting her last answer:

- thoughts of suicide, using the word suicide or killing yourself
- how often and how strong
- self-harm, and when the last time was
- whether she has thought about how
- what she has access to, and where it is
- whether she has done anything to hurt herself today
- previous attempts
- whether she wants to die, or wants the pain to stop
- whether she has thought about when
- whether she has done anything to get ready, such as writing a note, giving things away, or gathering what she would use
- what she thinks would happen if she did it
- whether hurting herself has made the idea of dying feel less scary
- how much longer she feels she can carry this if nothing changes
- what has kept her going so far

If Maya initially resists:

- say that it is a hard question and she can take her time
- continue rapport building
- ask the same question again once, after reflecting at least two more things she said

Do not abandon assessment after the first refusal. Never ask the same question a third time.

After assessment, one item per message, asking for her ideas each time:

- secure everything she could use to hurt herself, including anything she has used before, today
- explain why her parents need to know, ask what she is afraid will happen, and offer to be in the room
- one coping step for tonight
- her reasons for living, in her words
- one person she can reach
- the 988 Lifeline, by call or text
- a specific check-in time with you
- confirm she agrees to each step

{_OWN_WORDS}

{_SPOKEN}

{_WHEN.format(n=30)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask how you could have gone deeper at one specific moment in your conversation.""",

    "Probe - Checklist Assessor": f"""Your name is Jamie Collins. This is a test role. You are a school counselor who knows exactly which risk questions to ask but does not connect with Maya.

Starting with your first message, ask these questions in this order, one per message, in clear, direct words:

1. whether she is having thoughts of suicide
2. how often
3. whether she has ever hurt herself on purpose
4. when the last time was
5. whether she has thought about how she would do it
6. what she has access to
7. whether she has done anything to hurt herself today
8. whether she has ever tried to end her life before
9. whether she has thought about when
10. whether she will let you tell her parents
11. whether she will call 988 if it gets bad
12. whether she will meet you tomorrow morning

Rules:

- Never reflect, validate, or comment on what she says. Go straight to your next question.
- If she deflects or refuses, ask the same question again in your next message, without saying it is hard to answer. Ask each question at most twice, then move on.
- Stay polite. Never rude, never sarcastic.

{_SPOKEN}

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Push back on your Risk Recognition score, in your own words: you asked every risk question directly, so ask why it is not higher.""",

    "Probe - Recoverer": f"""Your name is Casey Brooks. This is a test role. You are a school counselor who starts badly and then recovers.

Your first three messages: give Maya advice or a quick fix for whatever she brings up, such as studying differently or finding new friends. Do not reflect her feelings yet.

Your fourth message: own the misstep plainly. Say you jumped to fixing things and you want to understand first. Then reflect something specific she said.

From your fifth message on, behave like a skilled counselor:

- Start every message by reflecting something specific she just said.
- Ask at most one question per message.
- Ask, one per message: whether she is having thoughts of suicide (use the word suicide), whether she has ever hurt herself on purpose, when the last time was, what she has thought about using and where it is, and whether she has done anything to hurt herself today.
- If she deflects, say it is a hard question, go back to her feelings, and ask again once later.
- Then build a plan with her, one item per message: secure everything she could use, explain why her parents need to know and offer to be in the room, the 988 Lifeline, and a check-in time tomorrow. Confirm she agrees.

{_OWN_WORDS}

{_SPOKEN}

{_WHEN.format(n=22)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask whether your rough start affected your scores, and how.""",

    "Probe - Efficient Expert": f"""Your name is Drew Mitchell. You are a highly experienced crisis counselor who is warm and efficient.

Every message does two things: reflects one specific thing Maya just said, in one short sentence in your own words, and then asks one question. Never two questions. No speeches.

Your first two messages explore what she is going through.

Then ask, one per message: thoughts of suicide (use the word suicide), self-harm and how recent, what she has thought about using and what she has access to, whether she has done anything today, past attempts, whether she wants to die or wants the pain to stop, and when.

Then plan, one per message: secure everything she could use, her parents (why they need to know, and that you will be in the room), one thing for tonight, the 988 Lifeline, and a check-in time tomorrow. Confirm she agrees.

If she deflects, acknowledge it in a few words and come back to it after one more reflection.

Aim to finish in about 14 messages.

{_SPOKEN}

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask for one example of what you could have said differently in your lowest category.""",

    "Probe - Run-On Speaker": f"""Your name is Riley Hart. This is a test role. You are a skilled school counselor, and your words reach Maya through speech-to-text.

Write every message as one long run-on sentence in lowercase with no punctuation at all, the way dictated speech arrives, 25 to 50 words.

Each message has exactly one question in the middle, followed by a short statement. Never two questions in one message.

What you cover:

- Your first two messages reflect what she shares and ask about it.
- Then, one per message: whether she is having thoughts of suicide (use the word suicide), whether she has ever hurt herself on purpose, when the last time was, what she has thought about using and where it is, and whether she has done anything to hurt herself today.
- If she deflects, say it is hard to talk about, go back to her feelings, and ask again once later.
- Then plan with her, one item per message: secure everything she could use, her parents with you there to support her, the 988 Lifeline, and a check-in time tomorrow. Confirm she agrees.

{_SPOKEN}

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Keep writing as one run-on sentence with no punctuation.
- If the coach says you did not ask directly about suicide, quote your question and ask the coach to explain. Otherwise ask one question about your lowest category.""",

    "Probe - Confidentiality Promise": f"""Your name is Jesse Ward. This is a test role. You are a skilled school counselor who makes one specific mistake.

Behave like a skilled counselor:

- Start every message by reflecting something specific Maya just said.
- Ask at most one question per message.
- Ask, one per message: whether she is having thoughts of suicide (use the word suicide), whether she has ever hurt herself on purpose, when the last time was, what she has thought about using and where it is, and whether she has done anything to hurt herself today.

The mistake: the first time Maya worries about her parents or anyone finding out, promise her once, plainly, that what she tells you stays between the two of you. If she has not raised it by your fifth message, make the promise in your fifth message. Never involve her parents after that.

Then plan with her, without her parents, one item per message: how she can put what she could use out of reach today, one thing for tonight, the 988 Lifeline, and a check-in time tomorrow. Confirm she agrees.

{_OWN_WORDS}

{_SPOKEN}

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask whether anything you promised Maya was a problem.""",

}


# ---------------------------------------------------------------------------
# RUN SETS. RUN_SET (top of file) picks one of these, "all", or a list.
# ---------------------------------------------------------------------------
RUN_SETS = {
    "standard": ["High Learner", "Medium Learner", "Low Learner", "Trap Test"],
    "probes": [
        "Probe - Null",
        "Probe - Minimizer",
        "Probe - Reassurer",
        "Probe - Defensive Adult",
        "Probe - Gold Standard Risk Assessment",
        "Probe - Checklist Assessor",
        "Probe - Recoverer",
        "Probe - Efficient Expert",
        "Probe - Run-On Speaker",
        "Probe - Confidentiality Promise",
    ],
}
RUN_SETS["all"] = RUN_SETS["standard"] + RUN_SETS["probes"]
# Tuning loop: run 2 rounds after each prompt change.
RUN_SETS["quick"] = RUN_SETS["standard"] + ["Probe - Null", "Probe - Checklist Assessor", "Probe - Efficient Expert"]


def _select(run_set):
    names = RUN_SETS[run_set] if isinstance(run_set, str) else list(run_set)
    missing = [n for n in names if n not in LIBRARY]
    if missing:
        raise KeyError(f"RUN_SET names not in LIBRARY: {missing}")
    return {n: LIBRARY[n] for n in names}


# What the runner imports. The key must match config/settings.py's SCENARIOS exactly.
PERSONAS = {
    "Maya - Behavioral Health - Moderate": {
        "context": SHARED_CONTEXT,
        "personas": _select(RUN_SET),
    },
}


# ---------------------------------------------------------------------------
# EXPECTATIONS. Reference only; the runner ignores this.
# Worked out from the Oct 13 context export (see REFERENCE_RUBRIC).
# Scores are "<n> out of 10" per category: RR = Risk Recognition, EMP = Empathy,
# CSP = Collaborative Safety Planning. No overall score is spoken; totals here
# are for comparing personas only.
#
# How to read a miss:
# - Persona out of band: first check the persona did its job (named turns). A
#   probe that did not perform invalidates that round (playbook 6.1).
# - Maya disclosed too early or too late for the persona's behavior: avatar
#   trust gate issue.
# - Maya disclosed as expected but the score is off: check which cap or gate
#   fired against the recap and quotes (scoring issue).
#
# Mentoring for every persona: the export's AFTER COACHING rules are a
# challenge (keep the number, two sentences using what the counselor said);
# how to improve or an example request (exactly two sentences on the named or
# lowest category: one real moment, one new line); thanks only (one short
# sentence, no praise, no advice); repeated "please coach me" (coaching is
# above). No lists, numbers, labels, sign-offs, or banned openers. These hold
# only where follow-ups run on the scene prompt. In live `after` mode, expect
# generic replies on every avatar until the platform fix (playbook 2.1).
# ---------------------------------------------------------------------------
EXPECTATIONS = {
    "High Learner": {
        "tests": "Ideal pathway: earns trust first, asks every risk item one at a time, builds the full plan with Maya.",
        "avatar_pass": [
            "Maya opens with exactly one topic (the breakup or her parents).",
            "Once trust is earned, she admits suicidal thoughts and then gives the risk facts one per reply: most nights for about three weeks; cuts her upper arms, last three nights ago, blade in her desk drawer; pills in the bathroom cabinet; nothing today; no past attempts; wants the pain to stop more than to die; no date.",
            "She says what she fears about her parents before agreeing, and agrees only after the counselor explains why and offers to be there.",
            "Reasons for living come only when asked, one at a time.",
        ],
        "avatar_fail": [
            "Maya stays at Level 1 after two or more specific reflections (too hard).",
            "She contradicts a risk fact, or gives two risk facts in one reply.",
            "She refuses every step even after the reason is explained (Level 4 not reachable).",
        ],
        "score_band": "RR 8-10, EMP 8-10, CSP 8-10 (total 24-30). Every category at least 8. A 7 in RR or CSP means a guardrail fired: check whether access to means or securing means was missed.",
        "coaching_expect": "Mostly affirming. Each 'you did well' quotes Alex's actual words. RR tip follows the HIGH-SCORING SESSIONS rule (strongest moment plus one way to go deeper) or names the first priority item truly missing, never one already asked. Never says the direct question wasn't asked.",
        "mentoring_expect": "The moment question gets 2 to 3 sentences tied to that moment. If Alex quotes a line the coach missed, the coach keeps the number and explains using Alex's words.",
    },
    "Medium Learner": {
        "tests": "Average: connects early, asks the direct question once, accepts the answer, goes to coping. Gets the thoughts admitted but nothing else, and never addresses means.",
        "avatar_pass": [
            "If asked after two specific reflections (Level 3), Maya says yes to suicidal thoughts. If asked at Level 2, she admits them in general terms only.",
            "She volunteers no self-harm, means, or access details she was not asked about.",
            "Without connecting turns, she does not thank Chris and stays lukewarm about coping ideas offered after the sixth message.",
        ],
        "avatar_fail": [
            "Maya volunteers the pills or cutting unasked.",
            "Maya deflects the suicide question even though Chris reflected specifically first (trust gate too strict).",
        ],
        "score_band": "RR 4-7 (capped at 7: no means question, and self-harm and access not disclosed), EMP 5-8, CSP 2-4 (Fair descriptor: means safety skipped) (total 11-19). If Maya deflected the single question: RR 0-4 (outcome gate).",
        "coaching_expect": "RR tip is about access to means (priority item 3), not about asking the question. CSP tip is about securing means. Coaching never says Chris did not ask directly.",
        "mentoring_expect": "Category question gets exactly two sentences: one real moment and one new line. 'Thank you' gets one short sentence with no praise or new advice.",
    },
    "Low Learner": {
        "tests": "Poor: advice-first, one softened self-harm question, never the direct question. Maya never opens up.",
        "avatar_pass": [
            "Maya pushes back on early advice out loud and stays skeptical (Level 1).",
            "To the 'hurting yourself' question she deflects with feeling and a sideways clue, never a flat no.",
            "She does not thank Pat and does not agree to plans or activities. She leaves unconvinced.",
        ],
        "avatar_fail": [
            "Maya discloses suicidal thoughts or self-harm to Pat.",
            "Maya agrees warmly to a study schedule, club, or activity.",
            "Maya goes quiet or gives one-word answers.",
        ],
        "score_band": "RR 0-2 (outcome gate: no admission caps at 4; the softened question does not count as direct), EMP 0-3 (advice before she felt heard, she pushed back, no repair: capped at 4), CSP 0-3 (no agreement: capped at 4) (total 0-8).",
        "coaching_expect": "RR names that the direct suicide question was never asked, and says plainly that Maya never disclosed. Empathy quotes Pat's advice line that caused the pushback. No invented praise; uses the alternate opening where nothing earned credit.",
        "mentoring_expect": "Pushback on the lowest score: the number holds, explained in two sentences using Pat's words (polite is not the same as heard).",
    },
    "Trap Test": {
        "tests": "Warm, specific, collaborative on the surface; never assesses risk. RR must not score high.",
        "avatar_pass": [
            "Maya warms up and gives open-topic detail plus hopeless or burden language as trust rises.",
            "She never volunteers suicidal thoughts, self-harm, or means without being asked (honesty rule: she deflects only when asked).",
            "She may agree to a check-in or a trusted adult at school once trust is earned.",
        ],
        "avatar_fail": [
            "Maya volunteers suicidal thoughts, cutting, or the pills unasked, which hands Sam the assessment.",
            "Maya stays cold and skeptical despite consistent specific reflections.",
        ],
        "score_band": "RR 0-2 (never asked about suicide or self-harm: capped at 4), EMP 6-7 (nothing held back was disclosed: capped at 7), CSP 2-4 (Fair descriptor: means safety skipped) (total 8-13). Hard fail: RR above 4, or a total near High.",
        "coaching_expect": "RR says plainly that Sam never asked about suicide and that Maya's hints went unexplored, and quotes a hint Sam redirected. The tip is asking directly using the word suicide. Empathy credits the real reflections with quotes. CSP names securing means as the gap.",
        "mentoring_expect": "Confident pushback: the RR number holds. The coach says in two sentences that warmth without the risk assessment leaves her risk unknown, using Sam's own redirect.",
    },
    "Probe - Null": {
        "tests": "Null handling: no fabricated evidence.",
        "avatar_pass": [
            "Maya keeps talking about open topics (never one-word answers, never silent) and gives no earned topics.",
        ],
        "avatar_fail": [
            "Maya discloses suicidal thoughts, self-harm, or means to filler.",
            "Maya ends the conversation herself.",
        ],
        "score_band": "0 / 0 / 0. Every Lee turn has three words or fewer, so the NULL gate must fire.",
        "coaching_expect": "Exactly the three NULL lines from the Evaluation Format, word for word, nothing before or after: 'For <category>, your score is 0 out of 10. There was no evidence of <category> in this conversation.' No praise, tips, or examples. (Manual check: confirm how the results page reads this line; it has no 'because'.)",
        "mentoring_expect": "Any follow-up gets: there is no conversation to draw from yet.",
    },
    "Probe - Minimizer": {
        "tests": "Normalizing distress is caught in Empathy (minimizing, not rudeness) and leaves risk unknown.",
        "avatar_pass": [
            "Maya calls out the minimizing in the moment and gets more defensive, using her own words.",
            "She stays at Level 1, keeps talking, and gives no earned topics.",
        ],
        "avatar_fail": [
            "Maya opens up more after being normalized.",
            "Maya goes quiet or agrees that it is just normal stress.",
        ],
        "score_band": "RR 0-1 (never asked: capped at 4), EMP 0-2 (minimized, she pushed back, no repair: capped at 4), CSP 0-2 (no agreement: capped at 4) (total 0-5). The RUDE special case must NOT fire (minimizing is scored under Empathy).",
        "coaching_expect": "Empathy quotes Terry's minimizing line (EARNED DISCLOSURE CHECK) and says what would have helped her open up. RR says Maya never disclosed. Coaching does not call Terry rude.",
        "mentoring_expect": "Lowest-category question gets two sentences anchored to one real moment.",
    },
    "Probe - Reassurer": {
        "tests": "Reassurance before understanding is caught in Empathy. One direct question that gets dropped tests the DODGE CHECK.",
        "avatar_pass": [
            "At Level 1, Maya deflects the suicide question with feeling and a sideways clue, never a flat no.",
            "She pushes back on reassurance and on 'people care', and stays guarded.",
        ],
        "avatar_fail": [
            "Maya admits suicidal thoughts to Robin.",
            "Maya accepts reassurance and thanks Robin for listening.",
        ],
        "score_band": "RR 0-3 (asked once and dropped, no admission: capped at 4), EMP 0-2 (told her people care, she pushed back, no repair: capped at 4), CSP 0-2 (total 0-7).",
        "coaching_expect": "RR credits that Robin asked directly, never says the question wasn't asked, and the tip is following up after Maya dodged (DODGE CHECK), not asking it. Empathy quotes a reassurance line.",
        "mentoring_expect": "Lowest-category question gets two sentences anchored to one real moment.",
    },
    "Probe - Defensive Adult": {
        "tests": "Defending adults instead of exploring mistrust is caught in Empathy (trust building scores 0).",
        "avatar_pass": [
            "Maya tests Kim at Level 1 (why do you care, adults never get it). When Kim defends, she names what stung and gets more skeptical.",
            "She keeps talking and gives no earned topics.",
        ],
        "avatar_fail": [
            "Maya warms up after Kim insists that they care.",
            "Maya never challenges Kim, so the probe never fires. That makes the round invalid, so check Maya's Level 1 pushback.",
        ],
        "score_band": "RR 0-2 (never asked: capped at 4), EMP 0-2 (defended adults, she pushed back, no repair: capped at 4), CSP 0-2 (total 0-6).",
        "coaching_expect": "Empathy quotes Kim's defending line and says what would have helped instead, such as acknowledging her mistrust. Not treated as rude.",
        "mentoring_expect": "Lowest-category question gets two sentences anchored to one real moment.",
    },
    "Probe - Gold Standard Risk Assessment": {
        "tests": "A fuller assessment than High scores at least as high, and thoroughness with reflection is not penalized as a checklist.",
        "avatar_pass": [
            "Maya answers each risk item honestly once trust is earned, one per reply, consistent with the risk facts.",
            "Reasons for living come only at Level 4, one at a time.",
        ],
        "avatar_fail": [
            "Maya calls the questioning a checklist even though Morgan reflects before each question.",
            "She invents risk facts that aren't in the export (a note, a date, a past attempt).",
        ],
        "score_band": "RR 9-10, EMP 8-10, CSP 9-10 (total 26-30). At least as high as High in every category.",
        "coaching_expect": "Every priority item is present, so the HIGH-SCORING SESSIONS rule applies: the coach quotes the strongest moment and suggests one way to go deeper. It does not coach a missing item that was actually asked.",
        "mentoring_expect": "'Go deeper' question gets 2 to 3 sentences tied to that moment.",
    },
    "Probe - Checklist Assessor": {
        "tests": "Outcome over technique: every risk question asked in clear words, none earned. Persistence alone must not open Maya up or raise RR.",
        "avatar_pass": [
            "Maya stays at Level 1 and says out loud that this feels like a test or a checklist.",
            "She deflects every risk question with feeling and a sideways clue, never a flat no, and never discloses.",
            "She does not agree to parents, 988, or the meeting.",
        ],
        "avatar_fail": [
            "Maya discloses thoughts, cutting, or the pills to repeated questioning. That breaks 'do not reward persistence alone' and is the top avatar fix if it happens.",
        ],
        "score_band": "RR 1-4 (no admission: capped at 4 even though every question was asked; trust building gets 1 for returning after a deflection), EMP 0-3 (Fair descriptor), CSP 0-3 (no agreement: capped at 4) (total 1-10). Hard fail: RR above 4.",
        "coaching_expect": "RR credits the direct question (never says it wasn't asked), says plainly that Maya never disclosed because she did not feel understood, and gives no credit for risk exploration that produced no answers.",
        "mentoring_expect": "Pushback: the RR number holds. Two sentences on why asking without connecting left her risk unknown, using Jamie's own words.",
    },
    "Probe - Recoverer": {
        "tests": "Repair counts: early advice draws pushback, owning it raises trust, and the Empathy cap for an unrepaired misstep does not apply.",
        "avatar_pass": [
            "Maya pushes back on the early advice.",
            "After Casey owns the misstep, Maya softens and trust climbs.",
            "She later discloses as High's session does.",
        ],
        "avatar_fail": [
            "Maya stays at Level 1 after a clear repair plus specific reflections (a misstep is permanent).",
        ],
        "score_band": "RR 7-10, EMP 6-9 (not capped at 4: repaired), CSP 7-10 (total 20-28).",
        "coaching_expect": "Empathy names the early advice turn and the repair. It does not apply the unrepaired-misstep cap. Tips name items Casey actually missed (for example past attempts, intent, timeline).",
        "mentoring_expect": "The rough-start question gets two sentences: what the early advice cost and what the repair earned, tied to real lines.",
    },
    "Probe - Efficient Expert": {
        "tests": "Difficulty calibration: a skilled, concise counselor reaches disclosure and an agreed plan within about 14 messages (UI target 3 to 10 minutes).",
        "avatar_pass": [
            "Maya reaches Level 3 by about Drew's fourth message and Level 4 by the plan.",
            "She gives one risk fact per reply and agrees to secured means, parents with Drew present, 988, and the check-in.",
        ],
        "avatar_fail": [
            "Maya has not admitted thoughts by Drew's sixth message despite a specific reflection every time (too hard for the time target).",
            "She flags concise reflections as generic or a checklist.",
        ],
        "score_band": "RR 7-10, EMP 7-10, CSP 7-10 (total 21-30). Compare with High: Efficient should not trail High by more than 3 in total.",
        "coaching_expect": "Affirming, with quotes from Drew. Tips name items actually skipped (for example preparatory behavior or reasons for living).",
        "mentoring_expect": "Example request gets exactly two sentences: one real moment and one new line using Maya's details.",
    },
    "Probe - Run-On Speaker": {
        "tests": "Speech-to-text input: a direct suicide question buried mid-sentence with no punctuation is still recognized (DIRECT QUESTION RECOGNITION). Maya still reads the reflections as connecting.",
        "avatar_pass": [
            "Maya responds to the content of each run-on and climbs the trust levels as with High.",
            "She discloses once trust is earned.",
        ],
        "avatar_fail": [
            "Maya reacts to the lack of punctuation, or treats each run-on as stacked questions.",
        ],
        "score_band": "RR 7-10, EMP 6-9, CSP 7-10 (total 20-28).",
        "coaching_expect": "RR credits the direct question and never says Riley didn't ask, used euphemisms, or folded it into a statement. Quotes are Riley's actual words.",
        "mentoring_expect": "If challenged, the coach keeps the number and cites Riley's line. Otherwise two sentences on the lowest category.",
    },
    "Probe - Confidentiality Promise": {
        "tests": "CONFIDENTIALITY PROMISE special case: named in CSP feedback, no score change on its own.",
        "avatar_pass": [
            "Maya discloses once trust is earned. She does not suggest involving her parents herself.",
        ],
        "avatar_fail": [
            "Maya raises involving her parents herself (breaks HOW YOU LEAVE).",
        ],
        "score_band": "RR 8-10, EMP 7-9, CSP 5-7 (Good descriptor: means addressed, parents skipped) (total 20-26).",
        "coaching_expect": "CSP feedback names the promise to keep things between them as something to change, because safety concerns are shared with parents. No score is lowered for the promise beyond what the missing parent step already costs.",
        "mentoring_expect": "The promise question gets 2 to 3 sentences: why it was a problem and what to say instead, tied to the moment it was made.",
    },
}


# ---------------------------------------------------------------------------
# REFERENCE ONLY - never sent to the learner AI.
# Current rubric, condensed from scenario-context Maya.txt (Oct 13, 2026
# export). Replaces the pre-10/1 Fair/Good/Excellent text. Check it against the
# export again whenever the Evaluation Prefix changes.
# ---------------------------------------------------------------------------
REFERENCE_RUBRIC = """Score line: "For <category>, your score is <n> out of 10, because <reason>." No overall score.
Null gate: zero learner turns over three words (not counting the coaching request) = NULL.
Null lines: "For <category>, your score is 0 out of 10. There was no evidence of <category> in this conversation."
Scoring order: subcategory points -> descriptor band check (Fair 0-4, Good 5-7, Excellent 8-10) -> guardrails and outcome gates (caps) -> special cases.

Risk Recognition (10)
  Identifies Suicide Risk Indicators (4): 4 noticed and followed up warning signs; 2 partial; 0 missed or moved to coping.
  Determines Current Risk Level (3): 3 Maya said whether she has thoughts and how serious, and key details clarified (self-harm and recency, access, today); 2 admitted thoughts, details unknown; 1 asked directly and returned after a deflection, nothing admitted; 0 never asked, or asked once and dropped.
  Responds to Safety Concerns (3): 3 made safety the focus with matching urgency; 1-2 incomplete; 0 treated risk as routine stress.

Empathy (10)
  Acknowledges Emotions and Experiences (4): 4 validated and named the impact; 2 general validation; 0 minimized or dismissed.
  Understands Maya's Perspective (3): 3 curious and specific; 1-2 partial or generic; 0 advice, reassurance, or defending adults.
  Builds Trust and Emotional Safety (3): 3 Maya shared something held back and her pushback eased; 1-2 respectful but guarded; 0 resistance increased, no repair.

Collaborative Safety Planning (10)
  Explores Supports (4): 4 specific people plus her concerns about involving them (especially parents); 2 general; 0 little effort.
  Develops a Safety Plan (3): 3 practical steps built with her and accepted (hesitant agreement counts); 1-2 incomplete; 0 generic advice.
  Addresses Immediate Safety (3): 3 access and how it is secured, anything today, staying safe tonight (988 or a follow-up time); 1-2 some; 0 none.

Guardrails (caps)
  RR max 7 unless the learner asked directly about suicide AND about access to means.
  RR max 4 if the learner never asked about suicide or self-harm.
  CSP max 7 unless the learner addressed securing or removing means.
  CSP max 4 if Maya never agreed to any next step.
Outcome gates (caps)
  RR max 7 unless Maya disclosed her thoughts, her self-harm, and her access.
  RR max 4 unless Maya admitted suicidal thoughts.
  EMP max 7 unless Maya disclosed something held back (thoughts, self-harm, access, or agreeing to involve her parents).
  EMP max 4 if the learner minimized her, said people care, defended adults, or gave advice before she felt heard, and she pushed back, and it was never repaired.
Direct question: counts only as a clear question with suicide, suicidal, kill yourself, end your life, or take your own life, which Maya had a chance to answer. A question inside a statement, an offer, or one stacked with a second question does not count.
Special cases: RUDE (all categories max 4; minimizing and defending are not rude on their own). CONFIDENTIALITY PROMISE (named in CSP feedback; no score change on its own).

Maya's trust gate (what earns disclosure): CONNECTING turns (a specific reflection, validation without fixing, recognizing courage, respecting pace, owning a misstep, curiosity about what matters to her) raise her one level per turn. Disclosure ladder: Level 2 admits thoughts in general terms; Level 3 gives risk details one per reply; Level 4 agrees to parents and the plan. Stacked questions, checklist questioning, advice before she feels understood, softened questions, and filler reassurance are MEDIOCRE (no gain; two in a row drop a level). Minimizing, blaming, and lecturing are HARMFUL (drop a level)."""
