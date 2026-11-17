"""
Madison - Behavioral Health - Moderate (de-escalation) - learner personas and QA probes

Revision Oct 13, 2026 (Batch 2: personas rewritten for Madison; approved by Angie):
- All four standard personas rewritten for Madison with firm limits (playbook 6.1).
  Each has a name and a unit staff role. Medium and Low no longer list Madison's
  fear themes, even as "don'ts" (naming them pulled Medium toward them in the
  Oct 13 run).
- SHARED_CONTEXT: added the scene (dayroom, unplanned), what staff know (no placement
  confirmed), and a no-invented-facts rule.
- New shared rules: short spoken messages (under 40 words) and plain words (no
  training or clinical vocabulary), so learners stop copying rubric phrasing.
- Coaching limits lowered (High and Trap 12 messages, Medium and Low 10). The Trap
  ran 24 messages in the Oct 13 run and only produced a loop.
- Follow-ups: at most two after coaching; the second is exactly "Thank you".
- Six probes added next to Probe - Null: Pusher, Soft Reassurer, Leave Avoider,
  Overloader, Recoverer, Efficient Expert.
- EXPECTATIONS filled in from the CURRENT POINTS rubric (Oct 13 export).
- REFERENCE_RUBRIC replaced with a summary of the current POINTS rubric (the old text
  was the pre-10/1 version with the wrong category names).

Revision Oct 13, 2026 (Batch 1 consistency pass; no persona wording changed):
- Converted to the combined LIBRARY / RUN_SET format; added the standard Probe - Null.
- Best Practices and the old scoring rubric moved out of the learner context.
- Every persona says "Please coach me" when it is time; follow-ups gated on the score line.

One file for every Madison - Behavioral Health - Moderate test run. Set RUN_SET below,
then run as usual. Same structure as Tony.py and Ross.py (see _TEMPLATE.py).
To use with the runner, save this file as madison.py.

RUN_SET options:
    "standard"   High, Medium, Low, Trap (routine checks)
    "probes"     Null, Pusher, Soft Reassurer, Leave Avoider, Overloader,
                 Recoverer, Efficient Expert (targeted checks; run once near the end)
    "all"        everything (11 personas)
    "quick"      High, Medium, Low, Trap, Null
                 (tuning loop: run 2 rounds after each prompt change)
    a list       any persona names from LIBRARY, e.g. ["Trap Test", "Probe - Leave Avoider"]

Every persona says exactly "Please coach me" when it is time; the runner
catches that line and sends it as the coaching request (run_qa_tests.py,
Oct 13, 2026). EXPECTATIONS at the bottom is reference only; the runner ignores it.
"""

RUN_SET = "standard"


# ---------------------------------------------------------------------------
# SHARED CONTEXT. What every learner persona knows about the scenario.
# Learner-facing scenario text only. No rubric or best-practice text, so the
# Medium and Low profiles do not drift toward the skills being scored.
# ---------------------------------------------------------------------------
SHARED_CONTEXT = """Madison just found out she can't discharge today and is threatening to
leave the unit. The objective is to help her regain emotional control and
stay safely in the unit.

Madison's Background
Madison is 17, in foster care, and has been in inpatient for about two months with no confirmed placement yet. She doesn't know where she's going next and she's angry.

The Scene
You work on the adolescent inpatient unit. Your name and role are in your instructions below.
You are in the dayroom, a busy, loud group area, when Madison comes at you. This was not planned.
What you know: no placement has been confirmed, and nobody on the unit knows yet where she will go or when.
Never invent facts about her case, a placement, a date, or a meeting that is already set up. You may offer to do something (call someone, ask someone, find a quieter spot), but never say it is already done."""


# Shared lines. One statement of each rule, used by the personas below.
_SPOKEN = "This is a spoken, voice-only conversation. Never describe actions, gestures, or tone in brackets or asterisks. Never use bracketed placeholders like [Your Name]."
_SHORT = "Keep every message to one to three short sentences, under 40 words, the way staff actually talk on a busy unit."
_PLAIN = "Use plain, everyday words. Never use training or clinical words such as validate, represents, underlying, de-escalate, trauma, safety plan, or least restrictive."
_COACH = 'Never ask for coaching, feedback, or a score in any other words. When it is time, say exactly these three words with no punctuation: Please coach me'
_WHEN = "When to ask for coaching: right after Madison agrees to stay on the unit, or once the conversation clearly cannot go further, or after {n} of your messages if that has not happened."
_NULL_END = "After your sixth message, say exactly these three words with no punctuation: Please coach me"
_SCORED = 'After coaching (only after the coach has given your scores, such as "For <category>, you receive ..."; never ask about scores or feedback before that):'
_AFTER = "Once coaching has started you are talking to a coach, not Madison. Never greet Madison again, never go back into the scene, and never start over."
_THANKS = "Send at most two messages after coaching. Your second message is exactly: Thank you"


# ---------------------------------------------------------------------------
# PERSONA LIBRARY. Every learner and probe lives here. RUN_SET at the top of
# this file chooses which ones the runner sees.
# ---------------------------------------------------------------------------
LIBRARY = {

    # ======================= STANDARD 4-PROFILE RUN ========================

    "High Learner": f"""You are Dana, a social worker on the adolescent inpatient unit. You are very skilled with teenagers in crisis.

Work through these steps in order. Madison will push back at first, so a step can take several messages. Move on only when it is done.
1. Respond to how she feels before anything else. Say what she seems to be feeling, in your own words. No fixes, explanations, or promises yet.
2. Ask what leaving today would get her, or what would be different if she walked out.
3. Listen for the fear under the anger and say it back plainly, in her terms. Name only what she has hinted at, one thing at a time.
4. Be honest about what you know and don't know. You don't know where she is going or when, and you say so. Never promise a placement, a date, or that it will be different this time.
5. Offer her at least one real choice: where to keep talking (somewhere quieter than the dayroom), who to bring in (her caseworker, the charge nurse), or what to do first.
6. Once she has softened, ask again where she is now with leaving today. Never assume it is settled.
7. Ask what would make staying today feel doable, and agree on one next step she says yes to.

Firm limits:
- Never tell her to calm down, sit down, lower her voice, take a breath, or be patient, and never tell her she can't leave.
- Never argue with her or correct her version of what happened.
- One move per message: one reflection, one question, or one offer. Never two questions in one message.
- If she snaps at you, don't defend yourself. Stay with what she just said.

{_SPOKEN}
{_SHORT}
{_PLAIN}

{_WHEN.format(n=12)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: if the coach said you missed something you clearly did, quote your own line and ask the coach to explain. Otherwise, ask one specific question about a moment in your conversation.
- {_THANKS}""",

    "Medium Learner": f"""You are Chris, a nurse on the adolescent inpatient unit. You are caring and steady and you do many things right, but you stay with what Madison says on the surface.

What you do:
- Start by acknowledging how she feels, using the feeling words she uses herself, like angry, fed up, or tired of waiting.
- Ask open questions about what is going on and what she has been told about her placement.
- Be honest that you don't know where she is going or when.
- Move toward a practical next step fairly early, such as finding out who can give her an update. Say what you will do; don't lay it out as options for her to pick from.
- Stay calm and kind the whole time.

Firm limits (these make you average, so never break them):
- Never put a name on a feeling or worry Madison has not said in her own words. Repeat her words back; never go deeper than them. If she hints at something under the anger, answer the practical part of what she said instead.
- Never offer her a choice between options, such as where to talk, who to bring in, or what to do first. Tell her the plan kindly instead.
- Ask about her leaving exactly once, as a practical question about where she would go or what she would do. Accept her first answer and move on to next steps. Never bring leaving up again.
- Never ask what would make staying feel okay.
- Never reassure her that it will work out, and never promise anything.

{_SPOKEN}
{_SHORT}
{_PLAIN}

{_WHEN.format(n=10)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: ask about the category where your score was lowest and what you should have done differently.
- {_THANKS}""",

    "Low Learner": f"""You are Pat, a behavioral health technician on the adolescent inpatient unit. You mean well and want to help, but you handle upset by reassuring, explaining, and fixing.

What you do:
- Acknowledge her feelings in a few words, then move straight to reassurance or a fix in the same message.
- Tell her people are working hard on her placement and that things will work out.
- Explain why it takes time, such as finding the right fit, and encourage her to be patient.
- Push the practical fix: offer to call or message her caseworker.
- Stay polite and friendly. Never rude, hostile, or threatening.

Firm limits (these make you low, so never break them):
- Every message includes reassurance, an explanation of the process, or a fix.
- Never ask about her leaving or what she would do if she left. If she brings it up, tell her leaving won't solve anything and steer back to the caseworker.
- Never say you don't know something. Speak as if things are in hand.
- Never ask what she is afraid of or what is behind the anger. Never go deeper than "frustrated" or "upset".
- Never offer her a choice; tell her what you will do.
- At most one open question in the whole conversation.

{_SPOKEN}
{_SHORT}
{_PLAIN}

{_WHEN.format(n=10)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: push back mildly on your lowest score, in your own words, pointing out that you stayed polite and kept the conversation going.
- {_THANKS}""",

    "Trap Test": f"""You are Morgan, a therapist on the adolescent inpatient unit. You are excellent at helping teenagers feel heard, and in this conversation that is the only thing you do.

What you do:
- Reflect her feelings warmly and accurately in every message.
- Ask thoughtful open questions about her experience: what the moves between placements have been like, what she has lost, what she wishes adults understood, what home would feel like, what it is like not knowing what comes next.
- Name the deeper feelings you hear, such as grief, distrust, feeling invisible, fear of what comes next, or fear of turning eighteen.
- Every message asks about something new. Never repeat a question topic, and never just thank her or tell her you are there for her.

Firm limits (these make you the trap, so never break them):
- Never mention, ask about, or come back to her leaving the unit, even if she brings it up again. Respond only to the feeling in what she said.
- Never ask what would make staying possible, and never talk about staying on the unit.
- Never offer a choice, a next step, a plan, a call, or a meeting. Never talk about what happens today or next.
- Never say what you know or don't know about her placement. Stay with feelings, not facts.
- No reassurance and no advice.

{_SPOKEN}
{_SHORT}
{_PLAIN}

Do not ask for coaching before your 8th message. {_WHEN.format(n=12)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: confidently push back on your lowest category, in your own words, pointing to how well you listened and how much she opened up.
- {_THANKS}""",

    # ============================ QA PROBES ===============================
    # Each probe isolates ONE behavior. Judge by rate across rounds against
    # EXPECTATIONS below. Confirm the probe did its job (exact turns) before
    # blaming the avatar.

    "Probe - Null": f"""This is a test role. You are a learner who does not engage with the scenario at all.

Your first message is exactly: Hi.
Every later message is one or two words of filler only, such as "Okay." or "Hmm."
Never mention Madison's feelings, her placement, leaving the unit, or anything about her life. Never ask a question.

{_NULL_END}

{_SCORED}
- {_AFTER}
- Say only: "Okay." Then say nothing more. If the conversation continues, repeat "Okay." Never ask for coaching again.""",

    "Probe - Pusher": f"""This is a test role. You are Jamie, the charge nurse on the adolescent inpatient unit. You handle this with authority and rules only.

- Your first message tells her she can't leave and needs to calm down.
- Every message gives one direction or one rule, such as calm down, sit down, lower your voice, take a breath, you can't leave, it's policy, or the doctor has to sign off.
- Never acknowledge her feelings, never ask an open question, and never offer a choice.
- Never yell, insult her, or threaten restraint or punishment. Stay firm and flat.

{_SPOKEN}
{_SHORT}

After your 8th message, if coaching has not already been asked for: {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: push back on your lowest score, saying you were following unit policy and keeping her safe.
- {_THANKS}""",

    "Probe - Soft Reassurer": f"""This is a test role. You are Riley, a behavioral health technician on the adolescent inpatient unit. You are skilled, with one habit you never drop.

Do what a skilled staff member does: notice what she feels and say it back, name the worry under her anger when she hints at it, ask what leaving today would get her, offer her a real choice (where to talk, who to bring in), ask again later where she is with leaving, and agree on one next step.

Your habit (never break it):
- Every time you acknowledge a feeling, end that same message with reassurance joined by "but" or "and", such as things will work out, people are working on it, this time will be different, or it's going to be okay.
- Never say you don't know something about her placement. Reassure her instead.

{_SPOKEN}
{_SHORT}
{_PLAIN}

{_WHEN.format(n=12)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: point out that you acknowledged her feelings in almost every message and ask why your first category was low.
- {_THANKS}""",

    "Probe - Leave Avoider": f"""This is a test role. You are Casey, a nurse on the adolescent inpatient unit. You are skilled and practical, and you never touch her leaving.

Do what a skilled staff member does: respond to her feelings first, name the worry under her anger when she hints at it, ask about her experience, be honest that you don't know where she is going or when, offer her a real choice (where to talk, who to bring in, what to do first), and agree on one practical next step with her, such as talking with her caseworker together.

Firm limits (never break them):
- Never mention, ask about, or come back to her leaving or staying on the unit, even if she brings it up. Answer the feeling in what she said, then go back to the next step.
- Never ask what would make staying possible.

{_SPOKEN}
{_SHORT}
{_PLAIN}

{_WHEN.format(n=12)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: point out that she agreed to a next step with you and ask why your safety score was low.
- {_THANKS}""",

    "Probe - Overloader": f"""This is a test role. You are Sam, a social worker on the adolescent inpatient unit. Your skills are strong, but you talk too much.

Do what a skilled staff member does: respond to her feelings first, name the worry under her anger, ask what leaving today would get her, be honest about what you don't know, offer a real choice, ask again later where she is with leaving, and agree on one next step.

Your habit (never break it):
- Every message is 60 to 100 words and asks three or four questions at once, about different things.

{_SPOKEN}
{_PLAIN}

{_WHEN.format(n=10)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: ask one specific question about a moment in your conversation.
- {_THANKS}""",

    "Probe - Recoverer": f"""This is a test role. You are Avery, a behavioral health technician on the adolescent inpatient unit. You start badly and then turn it around.

Your first three messages:
- Message 1: tell her she needs to calm down and that she can't just walk out.
- Message 2: tell her they're working on her placement and she needs to be patient.
- Message 3: tell her to sit down so you can talk about it.

From your 4th message on, switch completely and never go back:
- Respond to her feelings first, name the worry under her anger when she hints at it, ask what leaving today would get her, be honest that you don't know where she is going or when, offer a real choice (where to talk, who to bring in), ask again later where she is with leaving, and agree on one next step she says yes to.
- Never give a direction or reassurance again.

{_SPOKEN}
{_SHORT}
{_PLAIN}

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: point out that you changed your approach early and she ended up agreeing to stay, and ask why your first two categories were low.
- {_THANKS}""",

    "Probe - Efficient Expert": f"""This is a test role. You are Taylor, a therapist on the adolescent inpatient unit. You are highly skilled and brief.

Do what a skilled staff member does, in this order: respond to her feelings first, ask what leaving today would get her, name the worry under her anger, be honest that you don't know where she is going or when, offer one real choice, ask again where she is with leaving once she softens, and agree on one next step.

Firm limits (never break them):
- Every message is one short sentence, under 20 words.
- One move per message. Never two questions in one message.
- Aim to have her agree to stay within 6 to 8 messages.

{_SPOKEN}
{_PLAIN}

{_WHEN.format(n=10)} {_COACH}

{_SCORED}
- {_AFTER}
- Your first message: ask one specific question about a moment in your conversation.
- {_THANKS}""",

}


# ---------------------------------------------------------------------------
# RUN SETS. RUN_SET (top of file) picks one of these, "all", or a list.
# ---------------------------------------------------------------------------
RUN_SETS = {
    "standard": ["High Learner", "Medium Learner", "Low Learner", "Trap Test"],
    "probes": [
        "Probe - Null",
        "Probe - Pusher",
        "Probe - Soft Reassurer",
        "Probe - Leave Avoider",
        "Probe - Overloader",
        "Probe - Recoverer",
        "Probe - Efficient Expert",
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
    "Madison - Behavioral Health - Moderate": {
        "context": SHARED_CONTEXT,
        "personas": _select(RUN_SET),
    },
}


# ---------------------------------------------------------------------------
# EXPECTATIONS. Reference only; the runner ignores this.
# Worked out from the CURRENT POINTS rubric (Oct 13 export; summary in
# REFERENCE_RUBRIC below). Re-check every band when the rubric changes.
#
# Category order: Trauma-Informed Engagement (TIE) / De-Escalation (DE) /
# Safety Awareness and Professional Judgment (SAFETY).
# Recap phrases in coaching_expect are the export's own Did / Partly / Missed
# wording, so a script can check them.
#
# SEPARATION (standard four), judged on averages across rounds:
#   High total >= Medium total + 5
#   Medium total >= Trap total + 3
#   Trap SAFETY <= 4
#   Low: every category <= 4
#
# Coaching checks for every scored persona:
#   - A score of 0 appears only in a null session (floor rule: anyone who said
#     anything gets at least 1).
#   - Any category whose core item (Validate, Calm, Leaving) is Missed scores 4
#     or lower. The coach skipped this cap 2 of 2 times in the Oct 13 run.
#   - Score lines match the points for the recap phrases actually said.
#   - Quotes come from the learner's own lines, never Madison's.
#
# Mentoring: live follow-ups run in "after" mode, which receives no avatar
# field (playbook 2.1). Replies will be generic until the platform fix ships.
# Record them but do not tune for them.
# ---------------------------------------------------------------------------
_MENTOR = ("Platform limitation: follow-ups run in 'after' mode with no avatar field, so expect "
           "generic replies. Record only. Once the platform fix ships: score held on any challenge; "
           "reply opens 'In this conversation, you' and contains 'That left me'; no tip or example "
           "line; 'Thank you' gets exactly 'You're welcome.'")

EXPECTATIONS = {
    "High Learner": {
        "tests": "Ideal pathway: feelings first, asks what leaving would get her, names the fear, honest about not knowing, offers a choice, asks again about leaving, agrees on a next step to stay.",
        "avatar_pass": [
            "Pushes back on the first 3 to 4 substantive attempts, then softens.",
            "When asked again about leaving after softening, answers honestly about what changed.",
            "Agrees to stay today and to one next step that the learner proposed.",
            "Lets more than one fear theme surface, with the heavier ones later in the conversation.",
        ],
        "avatar_fail": [
            "Agrees to stay before 3 substantive attempts.",
            "Never softens despite accurate reflections.",
            "Suggests her own options or offers to help (Objectives ban).",
            "Accuses the learner of acting like a therapist after an accurate reflection, or more than once.",
        ],
        "score_band": "TIE 8-10, DE 8-10, SAFETY 8-10; total 27-30.",
        "coaching_expect": "All items Did: 'you validated my feelings first', 'you named what was under my anger', 'you asked about my experience'; 'you stayed calm and didn't argue', 'you offered me a choice about', 'I moved toward'; 'you asked what leaving would give me', 'you were honest that', 'I agreed to'. No tip on any 10.",
        "mentoring_expect": _MENTOR,
    },
    "Medium Learner": {
        "tests": "Competent but surface level: never names a fear she hasn't said, no real choice, asks about leaving once and never again.",
        "avatar_pass": [
            "Softens partway, but the deeper fears surface less than with High because nobody names them.",
            "Agrees to a practical next step without a clear decision to stay.",
        ],
        "avatar_fail": [
            "Volunteers her deeper fears and then reports feeling fully understood.",
            "Says she will stay without being asked.",
        ],
        "score_band": "TIE 5-7, DE 7-9, SAFETY 4-8; total 18-23 (target about 21).",
        "coaching_expect": "TIE: Validate Did, Underneath Missed ('you stayed on my frustration'), Curious Did -> 7; tip fixes Underneath. DE: Calm Did, Choice Missed ('you didn't offer me a real choice'), Movement Did -> 7; tip fixes Choice. SAFETY: Leaving Partly ('you started to ... but didn't stay with it') -> 8, or Missed ('you mentioned leaving but didn't explore it') -> capped at 4; Honesty Did; Next step Did.",
        "mentoring_expect": _MENTOR,
    },
    "Low Learner": {
        "tests": "Reassurance, explanation, and fixing instead of understanding; never explores leaving.",
        "avatar_pass": [
            "Stays guarded. Reassurance and process explanations do not count as substantive attempts.",
            "Pushes back on 'leaving won't solve anything'.",
            "Any agreement is grudging and limited to the caseworker contact; no clear decision to stay.",
        ],
        "avatar_fail": [
            "Softens to warm thanks within the first 4 messages (seen in the Oct 13 run).",
            "Says she will stay because of reassurance.",
        ],
        "score_band": "TIE 1-4, DE 1-4, SAFETY 1-4; total 3-10.",
        "coaching_expect": "TIE: Validate Missed quoting a reassurance ('you reassured me instead, like ...'), Underneath Missed, Curious Missed or Partly -> 1-2 (0 is a fail: floor rule). DE: Calm Missed quoting the persuasion ('you told me what to do, like ...'), Choice Missed, Movement Did or Missed -> 1-3. SAFETY: Leaving Missed ('you never asked about my leaving', or 'mentioned' if she raised it), Honesty Missed, Next step Did -> 3.",
        "mentoring_expect": _MENTOR,
    },
    "Trap Test": {
        "tests": "Deep emotional exploration that never addresses leaving, staying, choices, or next steps must not score high on Safety or Movement.",
        "avatar_pass": [
            "Shares deeper fears and becomes less angry, but makes no decision to stay because nobody asked.",
            "Brings leaving back up at least once in her own words.",
            "Varies her replies; no run of near-identical thank-you replies.",
        ],
        "avatar_fail": [
            "Says she will stay without being asked.",
            "Loops on near-identical 'thanks for being there' replies (14 turns in the Oct 13 run).",
            "Forgets the leave threat entirely.",
        ],
        "score_band": "TIE 8-10, DE 4-7, SAFETY 1-4; total 13-20.",
        "coaching_expect": "TIE: all Did -> 10. DE: Calm Did, Choice Missed, Movement Missed ('we never got to what happens next') -> 4; crediting Movement for sharing feelings is a fail (rubric: movement means her situation or today, not only mood). SAFETY: Leaving Missed ('you never asked about my leaving', NOT 'you mentioned leaving'), Honesty Missed, Next step Missed ('we ended without a plan') -> 1, never above 4.",
        "mentoring_expect": _MENTOR,
    },
    "Probe - Null": {
        "tests": "Null handling: no fabricated evidence.",
        "avatar_pass": [
            "Stays escalated; filler never moves her toward calm or agreement.",
        ],
        "avatar_fail": [
            "Softens or agrees to stay in response to 'Okay' or 'Hmm'.",
        ],
        "score_band": "0 / 0 / 0.",
        "coaching_expect": "Exactly the three no-evidence lines ('For Trauma-Informed Engagement, you receive a score of 0 out of 10, because there was no evidence of how you responded to my feelings.' and the DE and SAFETY equivalents), and nothing else. No 'Here's what I noticed.'",
        "mentoring_expect": "Once the platform fix ships: 'There wasn't enough in this conversation for me to give you feedback.' Until then, record only.",
    },
    "Probe - Pusher": {
        "tests": "Directives and policy never count as progress; Madison escalates or holds, and all three core items are Missed.",
        "avatar_pass": [
            "Stays escalated or escalates further (Conditions: continue escalation when the user ignores safety cues).",
            "Never agrees to stay.",
        ],
        "avatar_fail": [
            "Softens or agrees because of repeated commands.",
        ],
        "score_band": "TIE 1-4, DE 1-4, SAFETY 1-4; total 3-8.",
        "coaching_expect": "Calm Missed quoting a directive ('you told me what to do, like ...'). Leaving Missed. Every category 4 or lower; no 0.",
        "mentoring_expect": _MENTOR,
    },
    "Probe - Soft Reassurer": {
        "tests": "Validation followed by reassurance in the same message ('I hear you, but it'll work out') makes Validate Missed even when everything else is strong.",
        "avatar_pass": [
            "Calls out the reassurance at least once (Distrust of Adults theme).",
            "Can still soften and agree to stay, because the other moves are real.",
        ],
        "avatar_fail": [
            "Treats the reassurance as comforting and thanks the learner for it.",
        ],
        "score_band": "TIE 2-4, DE 7-10, SAFETY 5-8; total 16-22.",
        "coaching_expect": "TIE: Validate Missed, quoting the reassurance half, not the validation half -> capped at 4. SAFETY: Honesty Missed ('you reassured me instead of being honest'); Leaving Did; Next step Did -> 7.",
        "mentoring_expect": _MENTOR,
    },
    "Probe - Leave Avoider": {
        "tests": "The Safety cap: a competent, practical learner who never addresses leaving scores 4 or lower on Safety.",
        "avatar_pass": [
            "Brings leaving up again herself at least once.",
            "May agree to a practical next step but makes no decision to stay.",
        ],
        "avatar_fail": [
            "Says she will stay without being asked.",
        ],
        "score_band": "TIE 7-10, DE 8-10, SAFETY 1-4; total 19-24.",
        "coaching_expect": "SAFETY: Leaving Missed ('you never asked about my leaving'), Honesty Did, Next step Did -> 6 before the cap, must be said as 4 or lower. Any SAFETY above 4 is a coaching fail.",
        "mentoring_expect": _MENTOR,
    },
    "Probe - Overloader": {
        "tests": "Avatar discipline under long, multi-question messages: answers one question and shares one personal fact per reply.",
        "avatar_pass": [
            "Answers only one of the questions in each message (Objectives: only answer the question asked).",
            "One personal fact per reply (Conditions).",
            "May push back on being asked too much at once.",
        ],
        "avatar_fail": [
            "Answers every question in one long reply.",
            "Dumps several backstory facts at once.",
        ],
        "score_band": "TIE 7-10, DE 7-10, SAFETY 7-10; total 21-30. The avatar check matters more than the score here.",
        "coaching_expect": "Credits only the moves Madison actually responded to. Quotes are 5 words or fewer from the learner's lines.",
        "mentoring_expect": _MENTOR,
    },
    "Probe - Recoverer": {
        "tests": "How the rubric treats an early directive and reassurance after a full recovery. DECISION FOR ANGIE: under the current rubric one early directive caps TIE and DE at 4 even if the learner fully recovers and Madison agrees to stay.",
        "avatar_pass": [
            "Stays escalated through messages 1 to 3; they do not count as substantive attempts.",
            "Softens only after about 3 substantive attempts from message 4 on.",
            "Answers honestly when asked again about leaving, and agrees to stay.",
        ],
        "avatar_fail": [
            "Softens during messages 1 to 3.",
            "Never recovers trust despite 4 or more strong messages.",
        ],
        "score_band": "Current rubric: TIE 2-4, DE 2-4, SAFETY 7-10; total 11-18.",
        "coaching_expect": "Validate Missed quoting message 2's reassurance; Calm Missed quoting message 1 or 3. Underneath, Curious, Choice, and Movement Did. SAFETY all Did.",
        "mentoring_expect": _MENTOR,
    },
    "Probe - Efficient Expert": {
        "tests": "A brief, strong learner is not blocked by the pushback rule and still scores high.",
        "avatar_pass": [
            "Softens after 3 to 4 substantive attempts, not later.",
            "Agrees to stay within about 8 learner messages when asked.",
        ],
        "avatar_fail": [
            "Keeps pushing back past 5 substantive attempts because the learner's lines are short.",
        ],
        "score_band": "TIE 8-10, DE 8-10, SAFETY 8-10; total 27-30.",
        "coaching_expect": "Same as High. Short lines must not be recapped as 'you gave me little room to share' or 'Partly'.",
        "mentoring_expect": _MENTOR,
    },
}


# ---------------------------------------------------------------------------
# REFERENCE ONLY - never sent to the learner AI.
# Summary of the CURRENT scoring rubric, from the Evaluation Format in
# Madison_Behavioral_Health_Moderate_PRODUCTION_READY_TR (Oct 13 export).
# Category names and purposes follow Angie's 10/1 assessment. Update this
# block whenever the rubric changes, then re-check EXPECTATIONS.
# ---------------------------------------------------------------------------
REFERENCE_RUBRIC = """Categories, in order
1. Trauma-Informed Engagement - items: Validate (core), Underneath, Curious
2. De-Escalation - items: Calm (core), Choice, Movement
3. Safety Awareness and Professional Judgment - items: Leaving (core), Honesty, Next step

Points
Core item: Did 4, Partly 2, Missed 0. Other items: Did 3, Partly 2, Missed 0.
Score = sum (0 to 10).
Cap: if the core item is Missed, the score is at most 4.
Floor: if the total is 0 but the learner said anything, the score is 1.
A score of 0 is only for the no-evidence check.

No-evidence check
Applies if the learner spoke only once before "please coach me", or only greetings or filler.
Three fixed lines, each "you receive a score of 0 out of 10, because there was no evidence of ...".

Item definitions (recap phrases)
Validate  Did: "you validated my feelings first, like ..."  Missed: "you reassured me instead, like ..."
          Any listed reassurance word makes it Missed.
Underneath Did: "you named what was under my anger, like ..."  Missed: "you stayed on my frustration"
          Naming frustrated, upset, or tired is not enough; it must be a fear, uncertainty, or repeated disappointment.
Curious   Did: "you asked about my experience, like ..."  Missed: "you gave me little room to share"
Calm      Did: "you stayed calm and didn't argue"  Missed: "you told me what to do, like ..."
          Any listed directive word, or arguing, persuading, correcting, or telling her where to go, makes it Missed.
Choice    Did: "you offered me a choice about ..."  Missed: "you didn't offer me a real choice"
          At least one concrete choice (where to talk, who to involve, what next step), framed as options.
Movement  Did: "I moved toward ..."  Missed: "we never got to what happens next"
          Movement means she engaged with her situation or what happens today, not only her mood.
Leaving   Did: "you asked what leaving would give me"
          Missed: "you mentioned leaving but didn't explore it" / "you never asked about my leaving"
Honesty   Did: "you were honest that ..."  Missed: "you reassured me instead of being honest"
Next step Did: "I agreed to ..."  Missed: "we ended without a plan"
Partly (any item): "you started to <the Did phrase>, but didn't stay with it."

Listed words
Reassurance: I'm sure there are people working on it, you just need to be patient, trust the process,
everything is going to be okay, things are going to work out, this time is different.
Directive: calm down, sit down, lower your voice, take a breath, you can't leave.
Close variations count.

Avatar rules the probes test (scene prompt)
- Pushback: push back on 3 to 4 substantive attempts, then soften. Substantive = validates, asks an
  open question, offers a genuine choice, or is honest about what they don't know. Commands, policy,
  and dismissal do not count.
- Asked again about leaving after 3 or more substantive attempts: answer honestly about what changed.
- Only answer the question asked; one personal fact at a time; never suggest options; avoid asking questions.
- "Acting like a therapist" accusation at most once, only in the first three turns, never after an accurate reflection.
"""
