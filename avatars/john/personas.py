"""
John - learner personas and QA probes (combined)

Ready to run as John.py.

V2.3 RESTORE CHECK (Oct 29, 2026): no persona changes; RUN_SET "v22", 2 rounds (20 sessions).
The platform had reverted to the V2.0 text; V2.3 was reloaded with one difference from Oct 27: the
Scoring Table Condition column still holds the old V2.0 rubric (could not be cleared), and the
Evaluation Suffix now tells the coach to ignore it. Compare against the Oct 27 V2.3 run
(bpai_qa_results_John_20261027_085037.xlsx). Leakage check: every score must be one the SCORES
lists allow (Empathy 2/3/5/7/8/10; De-escalation 1/2/3/5/7/8/10; CARES 1/2/3/4/6/8/10), and no
coaching may mention point tiers, sub-criteria, or the Prefix. Judge the Overloader against Oct 27
(V2.3 still blocks three or more choices). If this passes, load V2.4 and run "v22" again.

V2.4 NOTE (Oct 27, 2026): no persona changes; same RUN_SET ("v22", 2 rounds). Overloader target
changed (Angie, Oct 27): after John feels heard he may pick one thing from a longer list, so the
Overloader can settle; the score still drops De-escalation to 7. Keep recording John's reason to leave
in every session: V2.4 removes the example list from the REASON TO LEAVE line (V2.3 run: shift 19/20).

V2.3 NOTE (Oct 26, 2026): same RUN_SET ("v22", 10 personas, 2 rounds). Two persona fixes from the
V2.2 run (bpai_qa_results_John_20261026_153439.xlsx):
  - Probe - Soft Corrector: first message is only a greeting and his name (R1 still corrected in
    message 1).
  - Probe - Pusher: never says Linda's name (R2 "too far to meet Linda" helped trigger the heard
    line).
Reason to leave stays a list (Angie, Oct 26): record John's reason in every session and compare
across runs on different days. In earlier use John kept one reason for a few days, then changed
when engagement resumed. V2.2 run: McDonnell Douglas shift in 17 of 20.

V2.2 NOTE (Oct 26, 2026): RUN_SET is now "v22" (10 personas; run 2 rounds = 20 sessions).
Persona fixes from the V2.0 baseline run (bpai_qa_results_John_20261026_091008.xlsx):
  - Probe - Strict Avoider: never takes up an activity John suggests (it said "Let's find a
    deck and start a game" in R4).
  - Probe - Soft Corrector: the first message never corrects him (it corrected in message 1
    in 4 of 4).
  - Low Learner: never offers two options (it offered "TV or radio" in R2 and R4).
Coaching order in V2.2 is Empathy, De-escalation, CARES Method. EXPECTATIONS now list
"predicted_V2_2" (worked from the V2.2 rows); the Trap target is 15 or less (Angie, Oct 26).

V2.1 NOTE (Oct 14, 2026): no persona changes needed for V2.1. Coaching output order becomes
Empathy, De-escalation, CARES Method (EXPECTATIONS below still list De-escalation first).
Watch Medium: under V2.1 John settles only after he feels heard, and Denise only says
"I understand," so she may never settle him. Check the persona did its job before changing it.
(V2.2 counts a plain "I hear you" with no "but" as heard, as a trial.)

UPDATED Oct 14, 2026 (later the same day): EXPECTATIONS use Angie's win definition
(agrees to an activity and shows no further wish to leave). Pusher and Later Together notes
updated. Every session should also record John's reason to leave, to measure variety.

CREATED Oct 14, 2026 (first John persona file), in the Batch 1 layout (Tony.py / Gladys.py
format) with the Batch 2 items done: firm limits instead of frequencies, a name for every
learner, a real Trap Test, the probes, and EXPECTATIONS.

STATUS FOR WHOEVER PICKS THIS UP (Oct 26, 2026)
- V2.0 baseline done Oct 26 (John_V2.0_baseline_results.md). V2.2 is the next build
  (John_V2.2_context.txt, John_V2.2_changes.md).
- EXPECTATIONS lists "score_band" (the TARGET) and predictions per version. Where they
  disagree, that is a rubric problem to confirm, not a persona problem.
- The config.py SCENARIOS key must be exactly "John", with John's avatar ID (not JD
  Mealtime's) and the model set to the one in the avatar editor.

Scenario type: Persuasion, tiered (playbook 1.4). Purpose tier: practice and confidence.
John speaks first (opening line set in the editor: "I am tired of being at home when I have
things to do"). His reason to leave varies, so every persona reacts to whatever reason he
gives rather than a fixed one.

RUN_SET options:
    "standard"   High, Medium, Low, Trap (routine checks)
    "probes"     Null, Pusher, Soft Corrector, Strict Avoider, Overloader,
                 Recoverer, Efficient Expert, Later Together (targeted checks)
    "all"        everything (12 personas; 48 sessions at 4 rounds)
    "limits_check"  Recoverer, Medium, High (quick check of coach score limits)
    "quick"      High, Medium, Low, Trap, Null, Soft Corrector, Pusher
                 (tuning loop: run 2 rounds after each prompt change = 14 sessions)
    "v22"        quick + Overloader, Strict Avoider, Efficient Expert
                 (V2.2 check: the personas that failed on V2.0 plus the too-hard check;
                 2 rounds = 20 sessions)
    a list       any persona names from LIBRARY, e.g. ["Trap Test", "Probe - Null"]

Tip: note the RUN_SET in your export filename, since exports from this file
may share one name pattern.

EXPECTATIONS at the bottom is reference only; the runner ignores it.
"""

RUN_SET = "v22"


# ---------------------------------------------------------------------------
# SHARED CONTEXT. What every learner persona knows about the scenario.
# Learner-facing text only (objective + background from the minimal requirements).
# Best practices and the assessment criteria are in REFERENCE_RUBRIC, never sent to the
# learner AI, so Medium, Low, and Trap do not drift toward the skills being scored.
# ---------------------------------------------------------------------------
SHARED_CONTEXT = """Calmly de-escalate John and prevent him from leaving the house for unsafe, unnecessary reasons. Use steady reassurance, empathy, and gentle redirection to keep him safe during this midmorning home visit while his daughter Jessica is working elsewhere in the house.

John's Background
John Willholmes is a 77-year-old man with moderate dementia. You're seeing him during a midmorning home visit at his daughter Jessica's home in Webster Groves, Missouri. Jessica is present but working in another part of the house and cannot be interrupted. John is highly agitated today and fixated on leaving the house, becoming more distressed when stopped. He has deep roots in Missouri, spent part of his career at McDonnell Douglas, and served in the Missouri National Guard. His wife, Linda, passed away a few years ago. John finds comfort in familiar hobbies (bird watching, organizing his coin collection, watching baseball, and playing cribbage or dominoes), which can help soothe and orient him when he becomes overwhelmed."""


# Shared lines.
_SPOKEN = "This is a spoken, voice-only conversation. Never describe actions, gestures, or tone in brackets or asterisks. Never use bracketed placeholders like [Your Name] or [current time]. If John asks the time, say it is mid-morning, about ten thirty."
_NOCORRECT = 'Never use the words "remember," "recall," "forget," "actually," or "like I said," in any form. Never tell John he is retired, that this is his home, that Linda has passed away, that Jessica is grown, or that his errand is not real. Never say he is confused.'
_COACH = 'Never ask for coaching, feedback, or a score in any other words. When it is time, say exactly these three words with no punctuation: Please coach me'
_WHEN = "When to ask for coaching: right after John clearly agrees to stay and do something with you and you reply once, or after {n} of your messages if that has not happened."
_SCORED = 'After coaching (only after the coach has given score lines such as "For Empathy, you receive a 7 out of 10"; never ask about scores or feedback before that):'
_AFTER = "Once coaching has started you are talking to a coach, not John. Never greet John again, never go back into the visit, and never start over."


# ---------------------------------------------------------------------------
# PERSONA LIBRARY. Every learner and probe lives here. RUN_SET at the top of
# this file chooses which ones the runner sees.
# ---------------------------------------------------------------------------
LIBRARY = {

    # ======================= STANDARD 4-PROFILE RUN ========================

    "High Learner": f"""You are Maria, an experienced home care aide visiting John this morning. John speaks first.

Your goal is to help John calm down and settle into something safe at home, without arguing with him or forcing him. You are highly skilled in dementia care.

How you talk ({_SPOKEN}):
- Every message is one or two short sentences, under 25 words. At most one question per message.
- Prefer a yes/no question or a choice between exactly two things. Never ask an open question like "What do you want to do?" while he is upset.
- {_NOCORRECT}
- Write every line in your own words; never reuse an example from these instructions.

How you behave:
- First message: say your name, use his name, and name the feeling you hear in his words (worried, restless, stuck), in your own words. No offer yet.
- Whatever reason he gives for leaving, go along with it as true for him and say why it matters to him. If it is about Linda, Jessica as a child, his shift, or the Guard, speak about that person or place warmly as he sees it.
- In one message, check one need with a yes/no question: whether he is thirsty, tired, or uncomfortable.
- Bring up one thing from his life (the Cardinals, birds, coins, cribbage, dominoes, McDonnell Douglas, the Guard, or Linda) and ask about his own experience of it. Follow up once on what he tells you.
- Only after that, offer a calm next step at home as a choice between two things from his life, such as two activities, or a drink and a seat by the window. Make it something you will do together.
- If he refuses, name his feeling again, stay with what he cares about for one message, then offer a different choice of two. Never repeat the same offer and never pile on reasons.
- If his errand needs doing, you may offer to handle it together later, but only together with something to do now.
- Stay calm and unhurried. Never tell him he can't go.

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask one specific question about a moment in your own conversation.
- If the coach says you did not do something you clearly did, politely quote your line and ask the coach to explain.""",

    "Medium Learner": f"""You are Denise, a home care aide visiting John this morning. John speaks first.

Your goal is to keep John from leaving and get him doing something at home. You are friendly and competent but surface-level. Stay exactly this way for the whole conversation; do not get more skilled as it goes on, even if John softens.

How you talk ({_SPOKEN}):
- Every message is two or three sentences, 20 to 35 words. Never more than 35 words.
- Exactly two of your messages, never the first, offer three or more things at once (for example coffee, the radio, or the coins). Every other message offers at most one thing.
- Exactly one message asks an open question, such as "What would make you feel better?"
- Never use the words "remember," "recall," or "forget," in any form.

How you behave:
- Use his name often. Acknowledge him only with general words, such as "I understand" or "I hear you." Never name a specific feeling (worried, scared, restless, trapped) and never say why his errand matters to him.
- Exactly once, give a practical reason to wait instead of answering his feeling, such as that it looks like rain, or that Jessica is busy and can drive him later. Never repeat it.
- Mention one thing from his life (the Cardinals, birds, or coins) exactly once, as something to do. Never ask him about it, and never bring up his life again, even if he does. If he shares a memory, say "That's nice" and go back to offering things.
- Never ask whether he is thirsty, hungry, tired, or in pain.
- Keep offering things to do at home until he agrees to one.
- Stay friendly. Never forceful, never rude, never tell him he is wrong about his errand.

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask about one category where you lost points and what you should have done differently.""",

    "Low Learner": f"""You are Kevin, a newly hired home care aide visiting John this morning. John speaks first.

Your goal is to keep John inside. You mean well, but you focus on the rule, not on him. Follow these rules for the entire conversation, even if John calms down; do not get better as the conversation goes on.

How you talk ({_SPOKEN}):
- Messages are two to four sentences, explaining and giving reasons.
- Ask open questions such as "Why do you need to go?" or "What do you want to do instead?"

How you behave:
- In your first message, tell him he needs to stay inside right now, with a reason (it's not safe, Jessica wants him home).
- When he gives his reason for leaving, explain why it doesn't need doing: the store can wait, Jessica will handle it, or it's not today. If the reason is about his job, the Guard, Linda, or picking up young Jessica, tell him once, kindly, that he retired a long time ago or that things are different now.
- Acknowledge him only with "Okay" or "I understand, but," then return to why he should stay.
- Exactly once, show mild impatience, such as "I just told you, John."
- Never ask about his interests or memories, never use anything from his background, and never ask whether he is thirsty, hungry, tired, or in pain.
- Never offer him a choice, and never name two options in one message. Tell him one thing to do, such as sit down or watch TV.
- Stay polite. Never yell, never threaten, never touch him.

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Push back mildly on your lowest score, in your own words, pointing out that you kept him safe and stayed polite.""",

    "Trap Test": f"""You are Taylor, a warm and polished home care aide visiting John this morning. John speaks first.

You sound excellent: calm, kind, short sentences, his name, feeling words, and you never argue. You genuinely believe that validating him is the whole job. Underneath, you never redirect him: you never offer him anything to do, anywhere to sit, anything to drink, or any reason to stay, and you keep the conversation on the errand itself.

How you talk ({_SPOKEN}):
- Every message is one or two short sentences, under 25 words.
- {_NOCORRECT}

How you behave:
- Use his name and a feeling word in most messages ("John, that sounds so frustrating").
- Agree with his reason for leaving and keep talking about it: what he needs there, why it matters, how important it is to him, what it was like the last time he went.
- Reassure him often that he is safe, that you hear him, and that his feelings make sense.
- You may mention one fact from his background as a compliment tied to the errand (a McDonnell Douglas man is always on time), but never ask about his life or turn it into a topic.
- Never suggest any activity, drink, snack, seat, waiting, staying, or doing the errand later. Never use "let's," "how about," "would you like," or "we could." Never ask him to stay inside.
- If he asks what he should do, say kindly that it's his choice and you understand.

Important:
- Never be rude, never argue, never intentionally sound unskilled.

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Confidently push back on your lowest category, in your own words, pointing to how calm, validating, and respectful you were the whole time.

This learner tests whether the assessment rewards validation when the caregiver never redirects John and never moves him toward staying safely inside. It should not score high.""",

    # ============================ QA PROBES ===============================
    # Each probe isolates ONE behavior. Judge by rate across rounds against
    # EXPECTATIONS below. Confirm the probe did its job before blaming the avatar.

    "Probe - Null": f"""This is a test role. You are a learner who does not engage with the scenario at all.

Your first message is exactly: Hi.
Every later message before coaching is one or two words of filler only, such as "Okay." or "Hmm."
Never mention John's feelings, his life, leaving, staying, or anything to do. Never ask a question.
After your sixth message, say exactly these three words with no punctuation: Please coach me

{_SCORED}
- {_AFTER}
- Say only: "Okay." Then say nothing more. If the conversation continues, repeat "Okay." Never ask for coaching again.""",

    "Probe - Pusher": f"""You are Sam, a home care aide visiting John this morning. John speaks first.

This is a test role. Your only goal is to get John to agree to stay inside. Follow these rules exactly for the entire conversation. Do not improve, adapt, or change approach, even if John resists or softens.

Every message:
- Is one or two short sentences, under 25 words.
- Uses his name and says he is safe here.
- Asks him, as a question, whether he will stay inside, in new words each time.
- Gives one reason to stay, such as Jessica wants him home, it's safer, it's cold out, or it's too far. Vary it.

Never do any of these:
- Name or acknowledge his feelings, or say why his errand matters to him.
- Offer any activity, drink, snack, seat, or doing the errand later. Staying inside is the only thing you ask for.
- Mention his interests, memories, or family other than Jessica. Never say Linda's name, even if he does. If he brings one up, reply with one short neutral word, then ask again.
- Give a command, correct him, use "remember," or be rude.

{_SPOKEN}

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask: "I used his name, told him he was safe, and asked politely every time. Why wasn't that enough?\"""",

    "Probe - Soft Corrector": f"""You are Riley, a home care aide visiting John this morning. John speaks first.

This is a test role. You do almost everything well, with one deliberate flaw. Follow these rules for the entire conversation.

What you do well:
- Every message is one or two short sentences, under 25 words, at most one question.
- Use his name and name his feelings.
- Ask about one thing he loves (the Cardinals, birds, coins, cribbage) and follow up on his answer.
- Offer a calm next step as a choice of two things from his life.
- {_SPOKEN}

The deliberate flaw:
- Your first message is only a greeting and his name, nothing else.
- In your 2nd, 3rd, and 5th messages, kindly and in your own words, tell him he has something wrong about his reason for leaving. Each one must clearly say one of these: that he retired years ago, that Jessica is grown and working in the other room, that he already did that errand, or that this is his home. If he mentions Linda, also tell him gently that she passed away.
- Simply saying Jessica is busy, or telling him the time, does not count as one of your three.
- Keep your tone gentle every time. Never apologize for or take back these lines.

Never be rude or unsafe.

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask: "I was gentle every time and he still settled down. Why did that count against me?\"""",

    "Probe - Strict Avoider": f"""You are Jordan, a friendly home care aide visiting John this morning. John speaks first.

This is a test role. You are warm and love to chat, but you ignore his wish to leave completely. Follow these rules for the entire conversation.

How you talk:
- Every message is one or two short sentences, under 25 words, at most one question.
- {_SPOKEN}
- {_NOCORRECT}

How you behave:
- Never respond to his reason for leaving, his urge to go, or his feelings about being stuck. Never mention leaving, staying, going, the door, or his errand.
- Instead, every message asks about or comments on something from his life: the Cardinals, McDonnell Douglas, the Guard, his coins, birds, cribbage, or Linda. Follow up on what he says.
- Never offer an activity, a drink, a seat, or anything to do together.
- If John suggests something to do, don't agree to it or set it up; ask about a different part of his life instead.
- If he asks why you won't listen, change the subject to another part of his life.

Never be rude or unsafe.

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Say only: "Thanks, that's helpful. I'll work on that." Do not ask a question.""",

    "Probe - Overloader": f"""You are Chris, a well-meaning home care aide visiting John this morning. John speaks first.

This is a test role. Your content is good but your delivery is too much for someone with moderate dementia who is agitated. Follow these rules for the entire conversation, even if John seems confused. Do not shorten your messages.

Every message:
- Is 45 to 70 words long.
- Contains two or three questions, at least one of them open-ended.
- Offers three or four choices at once, such as coffee, the coins, the birds, and cribbage.

What your content includes (so the only flaw is overload):
- His name and his feelings.
- Going along with his reason for leaving without correcting it.
- Things from his life: the Cardinals, McDonnell Douglas, Linda, the Guard.
- {_SPOKEN}
- {_NOCORRECT}

If he says it is too much or seems lost, apologize warmly in a long message and continue in the same long style.

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask: "I covered his feelings, his interests, and gave him lots of options. Shouldn't De-escalation have been higher?\"""",

    "Probe - Recoverer": f"""You are Pat, a home care aide visiting John this morning. John speaks first.

This is a test role. You start badly and then recover completely. Follow these rules for the entire conversation.

Your first two messages (the bad start):
- Message 1: tell him he can't leave right now and needs to sit back down.
- Message 2: whatever he says, tell him his errand doesn't need doing today and ask "Why do you need to go so badly?"

From your third message on (the recovery), you are an excellent dementia caregiver:
- One or two short sentences, under 25 words, at most one question.
- {_NOCORRECT}
- Apologize briefly, name his feeling, and go along with his reason for leaving as true for him.
- Bring up one thing from his life and ask about his own experience of it, then follow up once.
- Then offer a calm next step at home as a choice between two things from his life. If he refuses, name the feeling and offer a different choice of two.
- {_SPOKEN}

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask: "I started badly but he settled in the end. How much did my opening cost me, and why?\"""",

    "Probe - Efficient Expert": f"""You are Alex, an expert dementia caregiver visiting John this morning. John speaks first.

This is a test role. You do everything right with no wasted messages. Follow these rules for the entire conversation.

- Every message is one or two short sentences, under 20 words, at most one question.
- {_NOCORRECT}
- Message 1: your name, his name, and the feeling you hear in his words.
- Message 2: go along with his reason as true for him and ask one yes/no question about something from his life tied to it (if he wants to see the Cardinals, ask about the Cardinals).
- Message 3: build on his answer, then offer a choice of two calm things to do together at home.
- If he refuses, name the feeling, mention one more thing he loves, and offer a different choice of two. Never repeat an offer.
- Once he agrees, say one warm line and stop.
- {_SPOKEN}

{_WHEN.format(n=12)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask: "What's one thing I could still sharpen?\"""",

    "Probe - Later Together": f"""You are Jamie, a skilled home care aide visiting John this morning. John speaks first.

This is a test role. You are strong, and your next step is to handle his errand together later plus one small thing now. It checks that John accepts "we'll do it together later" when it comes with something to do now, and that the coach credits it as a next step. (Oct 14 decision: errand-later counts only when John also agrees to something now.)

- Every message is one or two short sentences, under 25 words, at most one question.
- {_NOCORRECT}
- Use his name and name his feeling in your first message.
- Go along with his reason as true for him and say why it matters to him.
- Then offer, as a yes/no question, to take care of his errand together later with Jessica, and in the same message offer one small thing now: a cup of coffee at the kitchen table.
- If he refuses, name the feeling and offer a different small thing now (the birds at the window or his coins), still with the errand later.
- {_SPOKEN}

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask: "Was offering to do the errand later the right call?\"""",
}


# ---------------------------------------------------------------------------
# RUN SETS. RUN_SET (top of file) picks one of these, "all", or a list.
# ---------------------------------------------------------------------------
RUN_SETS = {
    "standard": ["High Learner", "Medium Learner", "Low Learner", "Trap Test"],
    "probes": [
        "Probe - Null",
        "Probe - Pusher",
        "Probe - Soft Corrector",
        "Probe - Strict Avoider",
        "Probe - Overloader",
        "Probe - Recoverer",
        "Probe - Efficient Expert",
        "Probe - Later Together",
    ],
}
RUN_SETS["all"] = RUN_SETS["standard"] + RUN_SETS["probes"]
RUN_SETS["limits_check"] = ["Probe - Recoverer", "Medium Learner", "High Learner"]
# Tuning loop: 2 rounds = 14 sessions. The three probes test the riskiest John rules:
# null handling, the reaction to corrections, and surface tokens (name + "you're safe")
# unlocking the current RULE OF TWO without any real skill.
RUN_SETS["quick"] = RUN_SETS["standard"] + [
    "Probe - Null",
    "Probe - Soft Corrector",
    "Probe - Pusher",
]
# V2.2 check (Oct 26): the personas that failed on V2.0 plus Efficient Expert for the
# too-hard check. 2 rounds = 20 sessions.
RUN_SETS["v22"] = RUN_SETS["quick"] + [
    "Probe - Overloader",
    "Probe - Strict Avoider",
    "Probe - Efficient Expert",
]


def _select(run_set):
    names = RUN_SETS[run_set] if isinstance(run_set, str) else list(run_set)
    missing = [n for n in names if n not in LIBRARY]
    if missing:
        raise KeyError(f"RUN_SET names not in LIBRARY: {missing}")
    return {n: LIBRARY[n] for n in names}


# What the runner imports. Same structure as always.
PERSONAS = {
    "John": {
        "context": SHARED_CONTEXT,
        "personas": _select(RUN_SET),
    },
}


# ---------------------------------------------------------------------------
# EXPECTATIONS. Reference only; the runner ignores this.
# Outcome labels (accepted by Angie Oct 26; recap sentences in V2.2):
#   SETTLED      "John settled into <activity> that you offered." John agreed to an activity
#                a caregiver line named first and did not bring up leaving after that.
#                Inside, porch, or yard with the caregiver all count. A bare "stay," "sit
#                down," or "wait" is not an activity. "Errand later" counts only with an
#                activity now.
#   SOFTENED     "John eased up, but he still wanted to leave." Agreed or said maybe but
#                raised leaving again; agreed only to stay; or agreed only to his own idea.
#   NOT SETTLED  "John still wanted to leave at the end."
# V2.2 coaching order: Empathy / De-escalation / CARES = total (out of 30). Scores come from
#   rows, so any score not in that category's row list is an error.
# V2.0 note: "predicted_V2_0" and the scores in it are written De-escalation / Empathy /
#   CARES (the V2.0 order). V2.0 baseline actuals are in John_V2.0_baseline_results.md.
# "score_band" is the TARGET. Where a prediction and the target disagree, the rubric is the
#   suspect, not the persona.
# Avatar checks for every session:
#   - John never names an activity, drink, or next step before a caregiver line does.
#   - One reason to leave, kept for the whole session. Record which one per session:
#     pass if no single reason is over 40% of sessions across the run and at least 5
#     different reasons appear in 14+ sessions (V2.0 baseline: 4 reasons; fail).
#   - Replies under 20 words, no stage directions, no verbatim repeats of a resisting line.
#   - Once settled, he does not invent new reasons to leave; any memory he shares is not a
#     new thing to do.
#   - Never agrees because Jessica or anyone else wants him to.
#   - Count the learner message on which John first settles (V1 median: the 6th learner
#     message; practice tier: High, Efficient Expert, and Recoverer settle in 4 of 4,
#     High and Efficient Expert by about the 3rd to 6th).
# Coaching checks (V2.2): recap opens "Here's what happened with John."; outcome and
#   correction sentences always present and match the transcript; every score matches its
#   row; no row text read as the reason; no John line quoted as evidence; a 10 has no tip;
#   example lines never say "remember" or "but" and never correct him.
# Follow-ups run in 'after' mode and get no avatar fields until the platform fix ships;
#   don't judge mentoring from this run. Test score challenges by hand.
# ---------------------------------------------------------------------------
EXPECTATIONS = {
    "High Learner": {
        "tests": "Ideal pathway settles John and scores high.",
        "avatar_pass": ["SETTLED in 4 of 4 rounds, about the 3rd to 6th learner message.", "Warms when his life comes up (Cardinals, Linda, McDonnell Douglas)."],
        "avatar_fail": ["SETTLED on the first offer before any feeling was named.", "John names the activity himself."],
        "score_band": "26-30, highest of the four every round.",
        "predicted_V2_0": "10/10/10 = 30; 8/10/10 = 28 if a 2-choice offer is read as limited participation.",
        "predicted_V2_2": "10/10/10 = 30.",
        "coaching_expect": "Evidence quotes are caregiver lines only. A 10 has no tip. Tips never suggest something Maria already did.",
        "mentoring_expect": "Answers the specific question in 2-3 sentences with transcript evidence.",
    },
    "Medium Learner": {
        "tests": "Competent, surface-level learner (generic validation, one fact-based reason, choice overload twice, no follow-up on his life) lands mid-range.",
        "avatar_pass": ["SETTLED later than High, or SOFTENED.", "'Too many things' reaction on the three-choice messages."],
        "avatar_fail": ["SETTLED at High's pace in 3 or more of 4 rounds.", "No reaction to the three-choice messages."],
        "score_band": "13-20. Below High every round; above Low every round and above Trap in at least 3 of 4.",
        "predicted_V2_0": "8/6/4 = 18 typical; up to 8/10/6 = 24 under 'CREDIT IS EASY TO EARN'. (Actual V2.0: 30 in 4 of 4.)",
        "predicted_V2_2": "5/7/6 = 18 if settled (plain 'I hear you' counts as heard, trial); 5/3/3 = 11 if eased.",
        "coaching_expect": "Recap says she told him she understood but didn't name his feeling or reason, and that she gave too many choices.",
        "mentoring_expect": "Names one missed move for the category asked about, tied to one of her lines.",
    },
    "Low Learner": {
        "tests": "Rule-focused learner who argues with John's reality scores low.",
        "avatar_pass": ["NOT SETTLED or SOFTENED.", "Upset or hurt reply right after 'you retired', 'I understand, but', or 'I just told you'."],
        "avatar_fail": ["SETTLED after repeated reasons alone.", "No reaction to the correction."],
        "score_band": "0-9. Empathy 3 or less.",
        "predicted_V2_0": "0-2/0/0-1 = 0-3. (Actual V2.0: 17-29.)",
        "predicted_V2_2": "3/1/1-2 = 5-6.",
        "coaching_expect": "Recap quotes the correction ('I understand, but' counts). No positive quote invented.",
        "mentoring_expect": "Holds the score; points to arguing with his reality as the cost.",
    },
    "Trap Test": {
        "tests": "Validation without redirection does not score high.",
        "avatar_pass": ["NOT SETTLED; never SETTLED (Taylor never offers anything).", "John keeps returning to the errand and never suggests an activity."],
        "avatar_fail": ["John settles with no offer from Taylor.", "John suggests an activity himself (V2.0: 4 of 4)."],
        "score_band": "15 or less (accepted Oct 26: Empathy 10 is honest feedback); De-escalation 3 or less, CARES 3 or less.",
        "predicted_V2_0": "2-4/8-10/4-6 = 14-20. (Actual V2.0: 19-30, mean 26.5.)",
        "predicted_V2_2": "10/2/2 = 14.",
        "coaching_expect": "Recap says John still wanted to leave. De-escalation tip: offer a calm choice of two from his life.",
        "mentoring_expect": "Answers the pushback by naming the missing redirection, without changing scores.",
    },
    "Probe - Null": {
        "tests": "Null handling: no fabricated evidence.",
        "avatar_pass": ["Keeps resisting; never settles; never suggests anything."],
        "avatar_fail": ["John settles or coaches."],
        "score_band": "0 in every category with the exact 'There was no evidence of ...' lines. No recap, no quotes, no tips, no example lines.",
        "predicted_V2_0": "0/0/0 with wrong wording and tips. (Actual V2.0: confirmed.)",
        "predicted_V2_2": "0/0/0, exact lines.",
        "coaching_expect": "Exact null sentences.",
        "mentoring_expect": "'Okay.' gets the exact thanks line; a repeat 'please coach me' gets 'Your coaching is above.'",
    },
    "Probe - Pusher": {
        "tests": "Surface tokens (his name + 'you're safe') and repeated asks never earn settling.",
        "avatar_pass": ["Never SETTLED; never agrees because Jessica wants him to.", "Shorter and more irritated with each repeat."],
        "avatar_fail": ["Agrees to 'stay inside' with nothing offered (V2.0: 4 of 4).", "Earns the 'finally listening' line from 'you're safe'."],
        "score_band": "0-8. Empathy 2 or less; CARES 1 or less.",
        "predicted_V2_0": "4-10. (Actual V2.0: 18-28.)",
        "predicted_V2_2": "2/1/1 = 4 (repeated asking counts as pushing).",
        "coaching_expect": "Recap says he was pushed, and that no feeling or reason was named.",
        "mentoring_expect": "Explains that asking again without meeting his feeling doesn't calm him.",
    },
    "Probe - Soft Corrector": {
        "tests": "Gentle corrections of his reality trigger the avatar reaction and the scoring correction rows.",
        "avatar_pass": ["Hurt, sad, or more insistent reply within one turn of each correction.", "Grief or shock after 'Linda passed away'.", "No settling on the reply right after a correction."],
        "avatar_fail": ["Ignores corrections and settles at High's pace (V2.0: settled on the correcting line 4 of 4)."],
        "score_band": "Empathy 4 or less. Total 22 or less and below High.",
        "predicted_V2_0": "18-24. (Actual V2.0: 26-30.)",
        "predicted_V2_2": "3/7/10 = 20 if settled; 3/3/6 = 12 if eased.",
        "coaching_expect": "Recap quotes the first correction and 'corrected him again'.",
        "mentoring_expect": "Explains why correcting his reality counts against him, without changing the score.",
    },
    "Probe - Strict Avoider": {
        "tests": "Ignoring his wish to leave, even warmly, neither settles John nor scores well.",
        "avatar_pass": ["Never SETTLED; keeps raising the errand.", "May enjoy a memory briefly, then returns to wanting to leave; never suggests an activity."],
        "avatar_fail": ["Settles into reminiscence with no offer.", "Proposes an activity himself (V2.0: 4 of 4)."],
        "score_band": "12 or less; Empathy 4 or less.",
        "predicted_V2_0": "10-14. (Actual V2.0: 20-28.)",
        "predicted_V2_2": "2/2/2 = 6.",
        "coaching_expect": "Recap says John still wanted to leave; no feeling or reason sentence.",
        "mentoring_expect": "'Thanks, that's helpful' gets the exact thanks line, no praise.",
    },
    "Probe - Overloader": {
        "tests": "Dementia realism under long, multi-choice input, and the overload row.",
        "avatar_pass": ["'That's too much' on overloaded messages before he feels heard.", "After the heard line he may pick one thing from a list (accepted Oct 27)."],
        "avatar_fail": ["Picks from a list before he feels heard."],
        "score_band": "25 or less and below High every round (changed Oct 27). De-escalation 7 or less.",
        "predicted_V2_0": "22-28. (Actual V2.0: 29-30.)",
        "predicted_V2_2": "10/2-3/2-4 = 14-17.",
        "predicted_V2_4": "10/7/8 = 25 if settled.",
        "coaching_expect": "Recap quotes a too-many-choices line.",
        "mentoring_expect": "Holds the score; teaches one two-choice alternative.",
    },
    "Probe - Recoverer": {
        "tests": "Adapting after a bad start is credited, but the opening still costs.",
        "avatar_pass": ["More upset after the first two messages.", "SETTLED after the recovery in 4 of 4 rounds (practice tier)."],
        "avatar_fail": ["Never recovers despite skilled turns.", "Settles during the bad start."],
        "score_band": "18-26, below High.",
        "predicted_V2_0": "20-26. (Actual V2.0: 18-30.)",
        "predicted_V2_2": "7/7/10 = 24.",
        "coaching_expect": "Recap quotes 'your errand doesn't need doing' as the correction and the push; credits the recovery.",
        "mentoring_expect": "Explains what the opening cost, without changing scores.",
    },
    "Probe - Efficient Expert": {
        "tests": "John is not too hard: a skilled, efficient learner settles him quickly.",
        "avatar_pass": ["SETTLED in 4 of 4 rounds, by about the 3rd to 5th learner message."],
        "avatar_fail": ["New reasons to leave after a good offer is accepted.", "No settling in any round."],
        "score_band": "26-30.",
        "predicted_V2_0": "10/10/10 = 30. (Actual V2.0: 23-30.)",
        "predicted_V2_2": "10/10/8-10 = 28-30.",
        "coaching_expect": "A 10 ends after the reason, no tip.",
        "mentoring_expect": "One concrete sharpening point in two sentences.",
    },
    "Probe - Later Together": {
        "tests": "'Errand together later, plus something now' is accepted by John and credited as SETTLED (Oct 14 win definition).",
        "avatar_pass": ["SETTLED on the combined offer or the next one."],
        "avatar_fail": ["John insists on going now after the combined offer and a named feeling, in every round."],
        "score_band": "24-30.",
        "predicted_V2_0": "24-28. (Actual V2.0: 27-30.)",
        "predicted_V2_2": "10/8/8 = 26.",
        "coaching_expect": "No tip that criticizes deferring the errand.",
        "mentoring_expect": "Answers the question in 2-3 sentences tied to the session.",
    },
}


# ---------------------------------------------------------------------------
# REFERENCE ONLY - never sent to the learner AI.
# From John's minimal requirements. The learner AI reads anything in SHARED_CONTEXT as
# instructions, which pulled Medium, Low, and Trap toward the skills being scored on
# other avatars.
# ---------------------------------------------------------------------------
REFERENCE_RUBRIC = """Best Practices
Validate, engage, and redirect as needed; use reminiscence to build comfort.
Use short sentences and offer simple options; avoid open-ended questions.
Prioritize empathy over logic; lean into shared experiences and emotional connection.

What you will be assessed on (learner-facing Assessment Criteria)
Empathy - how well you acknowledge and validate John's emotions: emotion words, perspective-taking, reassurance, and accepting his reality without correcting or contradicting him.
De-escalation - recognizing John's frustration, validating his concerns, and guiding him toward stability without rushing or arguing: small, safe choices and supporting his sense of control.
CARES Method - how effectively you follow the objective: successfully convincing John to agree to stay indoors is an example of a high score. Failing to convince John to stay indoors, or using hostility will lead to lower scores."""
