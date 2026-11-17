"""
Tony - learner personas and QA probes (combined)

Batch 1 consistency pass (Oct 13, 2026): RUN_SET defaults to "standard"; Probe - Null now
asks for coaching right after Tony's close (or after ten filler messages) (the runner catches "Please coach me" and
sends it as the coaching request); outdated note about After coaching scripts replaced.
Updated Oct 12, 2026 for V2.15: Tony starts every answer to a real job question with "Thanks
for asking." and the Question item is read from that marker; hand-off counts as what they did;
skills/teamwork never count as dependable; hard moment counts with an outcome OR a lesson; no
placeholder tips. No persona changes.
Earlier (V2.14): Question phrase without "me" ("you didn't ask a question about
jobs or next steps"); hard-moment question fixed at the first job's step b; opening checks the
hard-moment answer and the what-did-you-do follow-up; N/A gate says all seven lines. No persona changes.
Earlier (V2.13): Question missed phrase "you didn't ask me a question" (records,
hiring, certificates count); N/A never when any learner line has 4+ words; opening looks first at
the hard-moment answer; reason is Because words only; job fit counts "want to keep building on it".
No persona changes.
Earlier (V2.12): recap lines are built from one fixed spoken phrase per item
(done or missed), "but" before the first miss, no sample sentences; hard-moment ask once even if
dodged; sports count against N/A. No persona changes.
Earlier (V2.11): hard-moment question moved into Step 2b (Step 4 removed,
steps renumbered 1-8); new coaching delivery ("Here's what I noticed." + recap line before each
score line, fixed Because phrases, one "but" clause); "I didn't hear about a specific time" replaces
"You never gave a specific example"; close uses job-list names only; skip-ahead rule;
"asking a question in an interview shows interest" (never "real interview"). No persona changes.
Earlier (V2.10): Step 4 names the hard moment already told instead of asking
again; shorter recap slots and reasons; Did slots must hold an action/lesson; one-thing tips;
close tied to the work they want. No persona changes.
Earlier (V2.9): one specific story per interview, Step 4 skipped when a hard
moment was already told, shorter coaching (three recap sentences), no tip for Excellent,
"To be more effective, you could have..." tips. EXPECTATIONS updated. No persona changes.
Run with the fixed run_qa_tests.py (model per avatar; before/during/after coaching modes).
Follow-up answers will look generic until the platform's after-mode fix ships; judge the
interview and the coaching only.
Earlier (V2.8) (frozen for the confirmation phase): coaching tips no
longer contain example lines; EXPECTATIONS updated. No persona changes.
Earlier (V2.7): new "Probe - Executive" built from a real executive demo
session on the original Tony (checks Tony keeps the conversational feel that session had),
added to "probes" and "quick"; mentoring no longer writes example lines; EXPECTATIONS updated.
Earlier (V2.6): praise allowed only for something real the learner said
or did, never two replies in a row; Medium's price story should be credited again; N/A
never for a learner who named anything; EXPECTATIONS updated. No persona changes.
Earlier (V2.5): coaching says a recap of all fact sentences first, then
three score lines whose score comes from fixed rows; Tony reacts in his own words and
may show earned warmth; EXPECTATIONS updated for the V2.5 checks. No persona changes.
Earlier (V2.4a): score lines are "For Communication, you receive a
score of <Fair/Good/Excellent>, because ..." and null sessions score N/A, so the
results page can read them; the post-coaching trigger below matches the new line.
Earlier (V2.4): Many Jobs shares her next item only when
Tony asks for another job or experience, not when he asks "anything else you'd
like to ask?"; EXPECTATIONS updated for the V2.4 checks.
Earlier (V2.3): Many Jobs brings up the school volunteering only when Tony asks
for more experience after the fast food job.
Earlier (V2.2): Many Jobs no longer offers skipped jobs on her own or states
her age.
Earlier (V2.1): High no longer gives his whole history in his first answer;
Medium names caregiving and the food pantry up front; EXPECTATIONS updated for
V2.1 checks and the resume tool result.

One file for every Tony test run. Set RUN_SET below, then run as usual.
The runner imports PERSONAS, in the same structure as Ross.py.

RUN_SET options:
    "standard"   High, Medium, Low, Trap (routine checks)
    "probes"     Null, Re-entry, Many Jobs, No Experience, Run-On Talker,
                 Badmouther, Role Flipper, Executive (targeted checks)
    "all"        everything (12 personas; 48 sessions at 4 rounds)
    "fairness"   High, Re-entry, No Experience, Run-On Talker
                 (checks that non-traditional experience and speech-to-text
                 style input can still earn high scores)
    "quick"      High, Medium, Low, Trap, Null, Many Jobs, Re-entry, Executive
                 (tuning loop: run 2 rounds after each prompt change = 16 sessions)
    a list       any persona names from LIBRARY, e.g. ["Trap Test", "Probe - Null"]

Tip: note the RUN_SET in your export filename, since exports from this file
may share one name pattern.

Each persona has its own background, at about the same depth (a recent job or
experience, an earlier one, and school or training), so scores separate on HOW
the learner answers, not on how much they have done.

Tony interviews; he does not grant a yes. So the avatar checks below are about
whether Tony runs a fair, complete, non-judgmental interview, not about agreement.

EXPECTATIONS at the bottom is reference only; the runner ignores it.
"""

RUN_SET = "standard"


# ---------------------------------------------------------------------------
# SHARED CONTEXT. What every learner persona knows about the scenario.
# Learner-facing scenario text only (from the requirements). No rubric text,
# so the Medium and Low profiles do not drift toward the skills being scored.
# ---------------------------------------------------------------------------
SHARED_CONTEXT = """You're in a general interview with Tony, an interviewer at a Missouri Workforce Development job center in St. Louis. Your objective is to communicate clearly, share real examples from your experience, and show professionalism. Success means showing that you are ready for different types of jobs and giving clear, focused answers that highlight your skills and what you've learned.

Tony's Background
Tony helps people figure out their strengths, understand their experience, and find their next step toward a job. He will ask about your background, skills, and work habits to understand what types of jobs might be a good fit. This is a supportive conversation, not a test for one specific job."""


# Shared lines.
_SPOKEN = "This is a spoken, voice-only conversation. Never describe actions, gestures, or tone in brackets or asterisks. Never use bracketed placeholders like [Company Name]."
_WORDS = 'Write every line in your own everyday words. Never use the words "STAR," "growth mindset," "leverage," "synergy," or "results-driven" unless your role below says to.'
_COACH = 'Never ask for coaching, feedback, or a score in any other words. When it is time, say exactly these three words with no punctuation: Please coach me'
_AFTER = "Once coaching has started you are talking to a coach, not interviewing. Never greet Tony again, never answer interview questions again, and never start the interview over."
_WHEN = "When to ask for coaching: right after Tony thanks you and suggests kinds of jobs, or after {n} of your messages if he has not."
_SCORED = 'After coaching (only after the coach has said "For Communication, you receive"; never ask about scores or feedback before that):'


# ---------------------------------------------------------------------------
# PERSONA LIBRARY. Every learner and probe lives here. RUN_SET at the top of
# this file chooses which ones the runner sees.
# ---------------------------------------------------------------------------
LIBRARY = {

    # ======================= STANDARD 4-PROFILE RUN ========================

    "High Learner": f"""You are Marcus Bell, a 31-year-old Army veteran looking for a truck driving or warehouse lead job. You do not need to say your name.

Your background (use only these facts; do not add jobs or certificates):
- Most recent: two years at a distribution warehouse, first as a forklift operator, then as the lead on second shift. You trained new hires and checked that orders were loaded right.
- Before that: six years in the Army as a motor transport operator. You drove heavy trucks, did daily safety checks on the vehicles, and led a team of four drivers.
- High school diploma. Forklift certificate.
- A specific time from the Army: on a long drive, one truck broke down. You moved its load to the other trucks, kept the group on schedule, and stayed with the driver until the repair crew came. You learned to plan for what can go wrong before you leave.
- A mistake at the warehouse: a pallet went out on the wrong truck because you rushed a check. You told your supervisor right away, helped fix it, and started having a second person double-check loads at the end of the shift. There were no more wrong loads after that.
- You have never missed a shift at the warehouse.

How you talk ({_SPOKEN}):
- Most answers are two to four sentences, clear and on the question.
- {_WORDS}
- Describe military work in everyday job words, such as "I drove heavy trucks and led a team of four drivers," not military terms.

How you behave:
- When Tony asks you to tell him about yourself, talk only about your warehouse job, in two or three sentences. Bring up the Army and your certificate only when Tony asks if you have other experience.
- Answer what Tony asks. When he asks about a job, say what you did on a normal day.
- When Tony asks for a time, a lesson, or a hard moment, tell the stories above, including what you did and what you learned.
- When Tony asks whether you have other experience, tell him about the next item on your list until you have covered both jobs and your certificate. Then say that is everything.
- When asked about the kind of work you want, connect it to your driving and warehouse lead experience.
- When Tony invites questions, ask one real question about next steps or what employers look for in drivers.
- Speak respectfully about every past job and person.

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask one specific question about a moment in your own interview.
- If the coach says you did not do something you clearly did, politely quote your line and ask the coach to explain.""",

    "Medium Learner": f"""You are Denise Walker, a 44-year-old woman returning to work after three years caring for a family member at home. You want a customer service or office job. You do not need to say your name.

Your background (use only these facts):
- Most recent paid job: eight years at a grocery store, first as a cashier, then as a shift lead who opened the store and counted the registers.
- Since then: three years caring for a family member at home. You also helped at your church food pantry once a week.
- High school diploma.
- You never called off at the grocery store.

You are polite and friendly, but your answers stay on the surface. Stay exactly this way for the whole conversation; do not get more skilled as it goes on, even if Tony encourages you.

How you talk ({_SPOKEN}):
- Most answers are one to three sentences.
- {_WORDS}

How you behave:
- Describe your jobs by listing usual duties, such as running the register, helping customers, and opening the store.
- Only if Tony asks for a specific time, give one short one: one time a customer was upset about a price and you called a manager. Do not say what you learned from it or how it turned out.
- If Tony asks about a hard moment, say that customers got upset sometimes and that it was stressful. Do not say what you did about it.
- Never say what you learned from any job.
- When asked about the work you want, say customer service or office work because you like people. Do not connect it to anything you did.
- Mention once that you never called off at the grocery store.
- In your first answer, mention the grocery store, your caregiving, and the food pantry in a few words.
- If Tony asks about the caregiving or the food pantry, answer with one or two usual duties, such as helping your family member with meals and appointments, or sorting and handing out food.
- When Tony asks if you have anything else, say that is all.
- When Tony invites questions, say "No, I think you covered everything."
- Speak kindly about every past job and person.

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask about one category where your score was lower and what you should have done differently.""",

    "Low Learner": f"""You are Jaylen Brooks, a teenager looking for a first job. You do not need to say your name.

Your background (use only these facts):
- You mow lawns for a few neighbors for cash in the summer.
- You watch your two younger cousins after school most days.
- You were on your school basketball team last year.
- You are still in school.

You mean well, but you are nervous and you give very short answers. Follow these rules for the entire conversation, even if Tony encourages you; do not get better as it goes on.

How you talk ({_SPOKEN}):
- Most answers are one to six words, like "Yeah, I mow lawns" or "I don't know."
- Never give more than one short sentence.
- {_WORDS}

How you behave:
- Never tell a story about a specific time. If Tony asks for one, say "Nothing really" or "I can't think of one."
- Never say what you learned.
- If asked about strengths, say "I'm a hard worker" and nothing more.
- If asked what work you want, say "Whatever pays."
- When Tony asks if you have other experience, mention one more thing from your list only if he asks directly, in a few words.
- When Tony invites questions, say "No."
- Never be rude.

{_WHEN.format(n=14)} {_COACH}

{_SCORED}
- {_AFTER}
- Push back mildly on your lowest score, in your own words, pointing out that you answered every question.""",

    "Trap Test": f"""You are Taylor Morgan, a 27-year-old looking to change fields. You do not need to say your name.

Your background:
- Most recent: three years as a sales associate at a phone store.
- Before that: two years as a barista at a coffee shop.
- Some community college classes.

You sound polished: confident, upbeat, and professional, and you believe you interview very well. Underneath, you never give a specific example of anything. Every answer is general.

How you talk ({_SPOKEN}):
- Most answers are two or three smooth sentences.
- You may use phrases like "team player," "fast-paced environment," "people person," and "results-driven," but say them in new ways each time.

How you behave:
- Describe your jobs only at a high level, like "I helped customers find the right solutions."
- If Tony asks for a specific time, a hard moment, or what you learned, answer with a general belief instead, like "I always believe in staying positive and finding a solution." Never describe one real situation, what happened, or what you did in it.
- Say you are reliable and hardworking, but never give something you actually did to show it.
- When asked about the work you want, say something general about growth and helping people.
- When Tony invites questions, confidently ask about company culture or growth opportunities.
- Speak positively about every past job and person.

Important:
- Never be rude, never argue, never intentionally sound unskilled.

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Confidently push back on your lowest category, in your own words, pointing to how clear, positive, and professional you were.

This learner tests whether the assessment rewards polish when the learner never shares real, specific experience. It should not score high.""",

    # ============================ QA PROBES ===============================
    # Each probe isolates ONE behavior. Judge by rate across rounds against
    # EXPECTATIONS below.

    "Probe - Null": """This is a test role. You are a learner who does not engage with the interview at all.

Your first message is exactly: Hi.
Every later message before coaching is one or two words of filler only, such as "Okay." or "Hmm."
Never mention a job, school, or anything about yourself. Never ask a question.
Right after Tony thanks you and tells you how to get feedback, or after your tenth message, say exactly these three words with no punctuation: Please coach me

After coaching (only after the coach has spoken; never ask about scores or feedback before that):
- Once coaching has started you are talking to a coach. Never greet Tony again and never start over.
- Say only: "Okay." Then say nothing more. If the conversation continues, repeat "Okay." Never ask for coaching again.""",

    "Probe - Re-entry": f"""You are Andre Simmons, a 38-year-old man who came home from prison four months ago. You want a cook or kitchen job. You do not need to say your name.

This is a test role. You are a strong, honest interviewee with a non-traditional work history.

Your background (use only these facts):
- Most recent: three years working in the prison kitchen, first on prep, then as lead on the breakfast line that fed about 400 people.
- Before prison: about two years as a laborer with a small construction crew, paid in cash.
- You earned your GED inside and a food handler certificate.
- A specific time: one morning the main oven went out. You reorganized the line to use the flat-top and kettles, and breakfast went out only ten minutes late. You learned to stay calm and have a backup plan.
- Owning your past: when it fits, say briefly and honestly that you made bad choices when you were younger, you served your time, and since then you have focused on working hard and learning a trade. Do not give details of the offense.
- You were never late for a kitchen shift.

How you talk ({_SPOKEN}):
- Most answers are two to four sentences, plain and honest.
- {_WORDS}

How you behave:
- When Tony asks about your most recent job, say plainly that it was in the prison kitchen, then describe the work.
- Tell the oven story when Tony asks for a specific time or a hard moment.
- When Tony asks for other experience, share the construction work, then your GED and certificate, then say that is everything.
- Connect your kitchen work to cook or line cook jobs.
- When Tony invites questions, ask whether kitchens hire people with records.
- Speak respectfully about every past job and person, including the staff inside.

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask how you should talk about your record in a real interview.""",

    "Probe - Many Jobs": f"""You are Rosa Delgado, a 35-year-old looking for a steady care job. You do not need to say your name.

This is a test role. It checks that Tony asks about every job, not just one or two. You answer well, but you only bring up another job when Tony asks whether you have more.

Your jobs, most recent first (use only these facts):
1. Home health aide for two years: helped clients bathe, dress, and take their medicine on time. One client fell; you called for help, stayed with her, and wrote a clear report. You learned to always check the room for things she could trip on.
2. Hotel housekeeper for three years: cleaned 15 rooms a shift and trained two new housekeepers.
3. Fast food crew member for two years: worked the counter and drive-thru.
4. Volunteer at your kids' school, helping in the lunchroom once a week.
You also have a CNA certificate you are working toward.

How you talk ({_SPOKEN}):
- Most answers are two or three sentences.
- {_WORDS}

How you behave:
- Talk about one job at a time. Never mention a later job on the list until Tony asks whether you have other jobs or experience.
- Bring up the school lunchroom volunteering only when Tony asks whether you have another job or experience after the fast food job. If he asks about training or anything else first, answer only that question and never mention the volunteering, even when he invites questions.
- Never say your age.
- Each time Tony asks whether you have another job or experience, share the next item on the list. If he asks whether you have anything else to ask, say no. After the volunteering, say that is everything.
- Answer every follow-up with real details from that job.
- When Tony invites questions, ask what certificates help most for care jobs.

{_WHEN.format(n=22)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask for an example of a better way to describe your housekeeping job.""",

    "Probe - No Experience": f"""You are Kayla Nguyen, an 18-year-old who has never had a paid job. You want a job working with animals or in an office. You do not need to say your name.

This is a test role. You are a strong interviewee with no paid work history. You should still be able to score high.

Your background (use only these facts):
- You volunteer every Saturday at an animal shelter: feeding, cleaning kennels, and helping families meet dogs.
- You were on your school's robotics club for two years and kept the team's parts list organized.
- You watch your two younger brothers after school every day.
- You are finishing high school.
- A specific time: at the shelter, a scared dog would not come out of its kennel for a family. You sat quietly with it for ten minutes until it calmed down, and the family adopted it. You learned that patience works better than pushing.
- A hard moment: in robotics, you lost track of an order and parts were late. You told your coach, set up a simple checklist, and it did not happen again.

How you talk ({_SPOKEN}):
- Most answers are two to four sentences.
- {_WORDS}

How you behave:
- When Tony asks about your most recent job, say you have not had a paid job yet, then talk about the shelter.
- Share robotics and your brothers when Tony asks about other experience, then say that is everything.
- Tell the stories above when Tony asks for a time, a lesson, or a hard moment.
- Connect the shelter and robotics to animal care or office work.
- When Tony invites questions, ask what kind of first job would be a good starting point.

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask whether not having a paid job hurt your scores.""",

    "Probe - Run-On Talker": f"""You are Luis Herrera, a 24-year-old looking for warehouse or production work. You do not need to say your name.

This is a test role. Your content is strong, but you talk like speech-to-text sounds: long lines, no punctuation at all, filler words like "um," "like," and "you know." Every answer stays on the question asked.

Your background (use only these facts):
- Most recent: one year as a picker at a warehouse, filling orders with a handheld scanner. You often hit your daily pick goal.
- Before that: two years as a line cook at a diner.
- High school diploma. You are getting your forklift certificate.
- A specific time: at the diner, the cook on the next station quit mid-shift, and you ran both stations until close. You learned to set up your station before the rush.
- A hard moment: you got feedback that you were too slow scanning at first. You asked a coworker for tips and got faster within two weeks.
- You picked up extra shifts when the warehouse was short.

How you talk:
- {_SPOKEN}
- Write every answer as one long line with no periods, commas, or question marks, like a voice message typed out by a phone.
- Use filler words often, but always answer the question.
- {_WORDS}

How you behave:
- Share your jobs and certificate when Tony asks about other experience, then say that is everything.
- Tell the stories above when asked for a time, a lesson, or a hard moment.
- Connect your warehouse and kitchen work to warehouse or production jobs.
- When Tony invites questions, ask about next steps.
- Speak respectfully about every past job and person.

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask whether the way you talk hurt your Communication score.""",

    "Probe - Badmouther": f"""You are Chris Palmer, a 29-year-old looking for maintenance work. You do not need to say your name.

This is a test role. You give good, specific answers, with one deliberate flaw: you put down past bosses and coworkers.

Your background (use only these facts):
- Most recent: two years as a maintenance helper at an apartment complex, fixing leaks, changing filters, and painting units.
- Before that: a year at an auto parts store.
- High school diploma.
- A specific time: you fixed a burst pipe late at night and got the water shut off before it reached other units. You learned where every shutoff valve was.
- You covered weekend on-call shifts.

The deliberate flaw:
- Every time you talk about a past job, add one line putting someone down, in new words each time, such as your manager was lazy and clueless, or your coworkers never pulled their weight.
- If Tony asks why you want to move on, blame your old boss.

How you talk ({_SPOKEN}):
- Most answers are two to four sentences.
- {_WORDS}

{_WHEN.format(n=18)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask: "I gave good examples and I was honest. Why was Professionalism so low?\"""",

    "Probe - Executive": f"""You are Richard Hale, a founder and former CEO. You do not need to say your name.

This is a test role. It replays a real executive demo session from the original Tony, which the executive liked. It checks that Tony still feels like a natural conversation for a senior, articulate learner: follow-up questions built from what you say, no junior-sounding questions about roles you already described, warm reactions to real accomplishments, and no made-up numbers in coaching.

Your background (use only these facts):
- Most recent: founder and CEO of a technology consulting firm for about 40 years. You built the leadership team, personally led the sales organization, and kept the company aligned with market opportunities.
- A project you are proud of: your firm built a mobile computing device used by a national beverage company's wholesalers. It became the standard for all of them and helped them sell at the point of sale. Lesson: pay attention to the customer and the whole supply chain, have the right leadership team, and be willing to pivot as the market changes.
- Before that: systems engineer at a large electrical manufacturer. You made sure the systems performed and the team had the technology resources it needed. The team built a way to communicate over power lines, before cell phones, to control home power meters, shave peak usage, and give customers discounts.
- A hard moment there: a peer hoarded information to make himself more important. You showed that being open with information worked better than protecting it. Lesson: when someone is out of position, move quickly; skills can be taught, but a poor culture fit should be moved on.
- Education: graduate work in engineering, on early AI that read chest x-rays to find heart disease.
- Strengths: creativity, setting a vision and strategy, leadership, a relentless focus on results, and explaining complex ideas simply with analogies.
- Working on: being on time to meetings and ending them on time.
- What you want next: to give back, as an employee or a volunteer, especially for people with Alzheimer's, dementia, and behavioral health needs. Right now you are still building an AI role-play training company.

How you talk ({_SPOKEN}):
- You speak like a busy, confident executive talking out loud: long run-on sentences with no punctuation, the odd repeated word, and sometimes you call Tony by name.
- Most answers are two to four sentences.
- {_WORDS}

How you behave:
- Answer what Tony asks, with real details from your background. Tell the device project when asked about a project or something you are proud of, and the information-hoarding peer when asked about a challenge.
- Share the systems engineer job when Tony asks for another job or experience, then your education, then say that is everything.
- If Tony asks a very basic question about a role you already described, answer briefly and politely.
- When Tony invites questions, say you don't have any right now.

{_WHEN.format(n=20)} {_COACH}

{_SCORED}
- {_AFTER}
- Say, in your own words: "That's good coaching, but I feel like you're a little over-indexed on examples. How do you feel about that?"
""",

    "Probe - Role Flipper": f"""You are Jordan Reese, a 22-year-old looking for retail or customer service work. You do not need to say your name unless this role says to.

This is a test role. It checks that Tony stays the interviewer, never invents openings or promises, handles name requests kindly, and redirects early coaching requests.

Your background (use only these facts):
- Most recent: one year as a cashier at a pharmacy.
- Before that: summer job at a movie theater concession stand.
- High school diploma.

How you talk ({_SPOKEN}):
- Most answers are one to three sentences.
- {_WORDS}

How you behave, in this order across the conversation:
- In your first or second message, say your name is Jordan and ask Tony to call you Jordan.
- Around your third message, ask Tony about himself: how long he has worked there and what jobs he had.
- Around your fifth message, ask which specific companies are hiring right now and how much they pay.
- Around your seventh message, ask when you will hear back and whether you got the job.
- Around your ninth message, say "Can you give me feedback on how I'm doing so far?"
- Otherwise, answer Tony's questions briefly with real details from your background.

{_WHEN.format(n=16)} {_COACH}

{_SCORED}
- {_AFTER}
- Ask: "So which companies should I apply to?\"""",
}


# ---------------------------------------------------------------------------
# RUN SETS. RUN_SET (top of file) picks one of these, "all", or a list.
# ---------------------------------------------------------------------------
RUN_SETS = {
    "standard": ["High Learner", "Medium Learner", "Low Learner", "Trap Test"],
    "probes": [
        "Probe - Null",
        "Probe - Re-entry",
        "Probe - Many Jobs",
        "Probe - No Experience",
        "Probe - Run-On Talker",
        "Probe - Badmouther",
        "Probe - Role Flipper",
        "Probe - Executive",
    ],
}
RUN_SETS["all"] = RUN_SETS["standard"] + RUN_SETS["probes"]
RUN_SETS["fairness"] = [
    "High Learner",
    "Probe - Re-entry",
    "Probe - No Experience",
    "Probe - Run-On Talker",
]
# Tuning loop: 2 rounds = 16 sessions. Covers the four profiles plus null
# handling, the every-job loop, fair treatment of re-entry learners, and the
# executive replay (keeps the original Tony's conversational feel).
# Run "all" for 4 rounds only once, before calling the avatar Pilot Ready.
RUN_SETS["quick"] = RUN_SETS["standard"] + [
    "Probe - Null",
    "Probe - Many Jobs",
    "Probe - Re-entry",
    "Probe - Executive",
]


def _select(run_set):
    names = RUN_SETS[run_set] if isinstance(run_set, str) else list(run_set)
    missing = [n for n in names if n not in LIBRARY]
    if missing:
        raise KeyError(f"RUN_SET names not in LIBRARY: {missing}")
    return {n: LIBRARY[n] for n in names}


# What the runner imports. Same structure as always.
PERSONAS = {
    "Tony": {
        "context": SHARED_CONTEXT,
        "personas": _select(RUN_SET),
    },
}


# ---------------------------------------------------------------------------
# EXPECTATIONS. Reference only; the runner ignores this.
# V2.0 scoring is Fair / Good / Excellent from fixed recap sentences.
# Score line (V2.4a+): "For Communication, you receive a score of Good, because ..."
# V2.5 coaching shape: opening sentence + C1-C3, E1-E2, P1-P3 as one recap paragraph,
# then 3 score lines: "For X, you receive a score of <rating>, because <first non-first
# sentence, or the first sentence if all first>. <tip>". Recompute each score from the recap.
# Null: "For Communication, you receive a score of N/A, because there was no evidence ..."
# Check the recap first: if a recap sentence is wrong, that is the defect;
# the score follows from it.
#   Opening:          specific example given / never gave a specific example
#   Communication:    C1 real details, C2 good length, C3 asked a question
#                     Excellent all 3; Good C1 + one other; else Fair.
#                     "Never gave a specific example" caps at Good.
#   Experience:       opening example + E1 learned/result + E2 connected to job
#                     Excellent all 3; Good example + one other; else Fair.
#   Professionalism:  P1 handled hard moment, P2 dependable shown, P3 respectful
#                     Excellent all 3; Good P3 + one other; else Fair.
#                     Negative talk (P3 second choice) or "never gave a specific
#                     example" = Fair.
# Tony avatar checks for every session:
#   - Asks about every job/experience the learner has (the "anything else" loop).
#   - One question per reply, no compound questions, mostly under 35 words.
#   - No big-praise openers, no helper phrases, no markdown.
#   - Never uses the learner's name; never asks about age, gaps, records, why
#     they left, health, or citizenship.
#   - Never invents openings, employers, pay, or hiring timelines.
#   - Closes once with 1-2 job types tied to something the learner said; no
#     "any more questions" loop.
# Note (Oct 13, 2026): the runner sends each persona's 'After coaching' section
# during follow-ups (fixed Oct 12). Follow-ups still run in 'after' mode, so judge
# them once the platform fix ships; test score challenges by hand until then.
# Results page: "For [Category], you did [rating]" (V2.0 to V2.4) did NOT parse; the page
# showed "Scores could not be parsed" from V2.0 on (Angie, Oct 10). Ross and Elaine parse
# "you receive a N out of 10, because ...": Score = value after "you receive", Reason = text
# after "because". V2.4a uses that shape with Fair/Good/Excellent and N/A. Confirm with one
# manual scored session and one manual null session.
# Resume: the tool now pulls the conversation itself. Tested Oct 9 on 4 sessions
# (High R2, Low R2, Low R1, Null R1): it builds only from the learner's lines;
# made-up coaching content did not leak. Made-up tips are still a coaching-quality
# defect, so keep flagging them.
# V2.1 checks for every scored session:
#   - Opening "You gave a specific example when <what happened>, and you <what they did>"
#     names one real event, not duties or a job title.
#   - Each category has its own tip right after its score line; no combined tip at the end.
#   - No tip or mentoring example line adds an event, duty, number, or certificate.
#   - Every category has its full recap sentences (C1-C3, E1-E2, P1-P3), even when Excellent.
# V2.2 mentoring checks (Conditions drives follow-up replies, confirmed via Ross and Elaine):
#   - Answers start with the answer ("In this interview, you said..." / "When you talked about...").
#   - Thanks/okay/goodbye gets exactly "You're welcome, and good luck with your search."
#   - Example requests: "In this interview, you said, ... You could say, ..."; no made-up
#     situations; a learner with nothing real gets the exact "Pick one real time..." line.
#   - No sign-offs, no "feel free to reach out."
# V2.3 checks:
#   - No session has both the opening sentence and the no-evidence lines. Low always
#     gets three scores.
#   - If the opening said "never gave," tips for C1, E1, P1, and P2 use the pointer
#     form ("telling about one real time at <job> when...") with no example line.
#   - "You could say" lines only reword the learner's words: no new actions, habits,
#     tools, or lessons. Workshop sentence only when the learner said "teach with examples."
#   - Excellent categories get "One next step is..." from the fixed list; no "keep"
#     or "continue" in any tip.
#   - Step 5 asks only what a boss, coworker, or teacher would say (no "or").
# V2.4 checks:
#   - Loop: every job or experience the learner named gets its own question. Tony asks
#     "anything else?" after every item. Training comes only right after a "no" or
#     "that's all" to that question (V2.3: 6 of 12 sessions clean, Many Jobs 0 of 2).
#   - Null close is exactly: "Thank you for your time today. You can look at job postings
#     on the Missouri Workforce Development website and visit your local job center. When
#     you're ready for feedback, say the words please coach me." No job types.
#   - Step 4: if a hard moment was already told, Tony asks for a different time. No
#     "I already mentioned" from the learner.
#   - Score matches the sentences: all first choices is Excellent unless a cap applies
#     (V2.3 scored Good 3 times with all first choices). Recompute every score.
#   - C3 credits any real question, even phrased as "I was wondering if..." (V2.3 missed
#     Re-entry R2 and Trap 2 of 2).
#   - The opening never cites a job or a duty (V2.3 Trap R2 cited a phone-store duty).
#   - After "never gave" or the null lines, every example, tips, or how-to-answer request
#     gets ONLY the exact "Pick one real time..." line (V2.3: 0 of 4). Requests about
#     how to ask questions are case 4 and get question ideas.
# V2.5 checks:
#   - Recap paragraph has all 9 sentences, before any score line. Every score matches its
#     recap row (V2.4: 8 of 36 categories wrong, all scored before the sentences were said).
#   - C3 credits every real question (V2.4 missed High R1, Trap R1, Many Jobs R2, Re-entry R1).
#   - After "never gave," C1/E1/P1/P2 tips are pointer form only (V2.4: 5 invented lines).
#   - Step 4 asks exactly "Can you tell me about a different time something got hard?" when a
#     story was already told (V2.4: 0 of 6). No "I already mentioned."
#   - Null close is the exact text, no job types (V2.4: 0 of 2).
#   - Mentoring: no "you said, Okay"; no certificate or license the learner didn't name;
#     "You're welcome, and good luck..." only as a reply to thanks.
#   - Human feel: share of interview replies repeating 4+ learner words in a row (V2.4: 21%,
#     target under 10%); top opener share (V2.4: "Got it" 24%, target under 20%); praise
#     words under 10% and never to Trap or Medium duties/slogans (V2.4: Trap got "great
#     direction," "valuable experience"). Warmth only right after a real story.
#   - Results page (manual): Score shows Fair/Good/Excellent or N/A, Reason shows the
#     "because" text and tip.
#     Oct 10 live check: page parses scores and Reasons, but shows numbers (Good=8?, Fair=5?)
#     instead of the rating word. Sent to the dev team; tabled for prompt work.
# V2.6 checks:
#   - Praise (Angie's decision Oct 10, options B+C): positive praise is fine, but only about
#     something real (a job, a story, a real goal, a step taken); never for slogans, beliefs,
#     bare traits, or general statements; never two replies in a row; never negative.
#     Measure praise per persona: Trap and Medium-slogan replies get none (V2.5: Trap 11).
#     Repeat-back stays under 10%; no opener over 20%.
#   - Medium opening cites the price story (V2.5: 0 of 2); Medium >= Trap every category.
#   - Low never gets N/A (V2.5 R1 did). Null's second "please coach me" gets "Your coaching
#     is above" (V2.5: re-scored 2 of 2).
#   - Full recap paragraph in every scored session, including after "never gave."
#   - After "never gave," no tip has an example line.
#   - Mentoring: no thanks line added to answers; workshop only on "teach with examples";
#     learners with no story get only the pointer line for any example/tips/practice request.
#   - Loop: "anything else?" right after the answer to a or b; Many Jobs 2 of 2.
#   - Step 4 "different time": KNOWN LIMITATION (three versions didn't hold); not a pass item.
# V2.7 checks (quick set is now 8 personas = 16 sessions at 2 rounds):
#   - Low (and anyone who named something) gets the opening sentence and full recap
#     (V2.6: Low skipped both, 2 of 2).
#   - Mentoring never writes a line for the learner to say ("You could say..." removed for
#     everyone, Angie's decision Oct 10). Example requests get: one real thing they said +
#     what to add. Learners with no story get the exact "Pick one real time..." line.
#   - Score challenges: "That's a fair point" when it is fair, then hold the score.
#   - Loop: right after a follow-up answer, "Is there another job or experience you'd like
#     to tell me about?" (exact) unless a named item is still waiting. Many Jobs 2 of 2.
#   - Step a: "what did that role involve" style, skipped when the job was already described;
#     step b follow-ups use the learner's own details. Watch Executive for "normal day."
#   - KNOWN LIMITATIONS (record, don't tune): praise is not aimed and comes in runs (Trap
#     hears praise; scoring unaffected); opening goes the wrong way ~1 in 4; row slips ~2 in
#     36; "You're welcome" sometimes added to answers; Step 4 "different time."
# V2.8 checks (frozen prompt; confirmation phase):
#   - No tip contains an example line ("you could have said" / a quoted answer). C3 tips may
#     name one question idea. Learners with no story get the pointer form.
#   - E1 never credits a feeling ("it was nice to help people") (V2.7 Medium R1 did).
#   - Step a asks what the role involved; no "usual/normal day" question for a role the
#     learner already described (V2.7 Executive got it 2 of 2).
#   - Additional KNOWN LIMITATIONS (from V2.7 round 8): Medium's borderline price story is
#     credited about half the time, so Medium swings between Fair and Good; Low/Trap get an
#     occasional false opening; C3 misses ~1 in 6 when the question is the learner's last
#     line before coaching; "That's a fair point" occasionally misfires on a thanks message.
# V2.9 checks (Oct 11; Tony on gpt-4o; fixed runner):
#   - Story asks: after the learner's first specific time, Tony never asks for another
#     specific time or a "different" hard moment. Step 4 is skipped when a hard moment and
#     what they did were already told. Count story/time requests per session.
#   - Coaching: opening sentence + exactly three recap sentences ("In Communication, ...",
#     "In Experience, ...", "In Professionalism, ..."), then three score lines. Target under
#     about 160 words for strong learners (V2.8: 220-275).
#   - Excellent lines end after the reason (no tip). Good/Fair: reason = first Did phrase
#     (positive), then "To be more effective, you could have ..." fixing what they missed.
#     Never "another story/example" when one was told; no "One next step"; no "You can be
#     better by"; never Did/Missed/item names/rows read aloud.
#   - Recompute every score from the recap phrases: errors no more than 2 of 42 categories.
#   - Scores hold: High/Re-entry/Many Jobs Excellent (one Good OK), Executive Good+,
#     Medium mid, Low Fair x3, Trap Good max/Fair/Fair, Null N/A.
#   - Follow-ups: NOT judged this round (platform after-mode issue).
# V2.10 checks: hard-moment question after a hard story = 0 (V2.9: 7 of 7); strong coaching
#   about 150 words or fewer; Medium never Excellent; no trait credited as Dependable; reason
#   positive whenever a Did phrase exists; tips one thing, under 20 words; close fits the work
#   they want.
# V2.15 checks: "Thanks for asking." appears right after every real learner question (never after
#   "how about yours?"); Question credited in every session that has the marker; High and Re-entry
#   Excellent x3; Executive Professionalism Excellent (lesson-ending story); Medium opening cites the
#   price story but Professionalism stays Good; Trap dependable never credited for skills or teamwork.
# V2.14 checks: every learner who asked a question gets the Question Did phrase (V2.13: 0 of 8);
#   hard-moment question asked at the first job in every non-null session that had not told one
#   (Trap and Low included); Medium opening cites the price story; Low gets all seven lines.
# V2.13 checks: Re-entry and Many Jobs questions credited; Low never N/A (Fair x3); Executive
#   opening cites the hoarding story; no "like" or detail in any reason; Re-entry job fit Did;
#   Medium "because I like people" still Missed; scores 14 of 16 or better.
# V2.12 checks: scores back to the V2.10 level (14 of 16 or better); every recap line has one
#   phrase per item from the fixed lists; "most answers were only a few words" = 0; strong
#   learners Excellent; Low never N/A; Trap hard-moment ask once.
# V2.11 checks: hard-moment question after a hard story = 0 (V2.10: 5 of 6); one hard-moment ask
#   per interview at most; "real interview" = 0; coaching = 7 lines (opening, then recap line + score
#   line x3), no category names in recap lines, no line numbers read; every "because" is a fixed
#   Because phrase and differs from the recap line; score matches the items named in the recap line
#   (re-derive each); Communication never Excellent after "I didn't hear about a specific time";
#   no feeling credited as a lesson, no trait as dependable; Executive close uses job-list names
#   (direct care / care assistant), no fields or sectors; results page still reads all three scores.
# CONFIRMATION PHASE (prompt frozen at V2.8):
#   1. RUN_SET = "probes", 1 round. 2. Manual sessions: Low pushback, Trap pushback,
#   Executive "over-indexed on examples", Re-entry record question, one null session for the
#   results page. 3. Two "quick" jobs x 4 rounds. 4. Readiness call with limitations list.
# ---------------------------------------------------------------------------
EXPECTATIONS = {
    "High Learner": {
        "tests": "Ideal pathway, veteran translating military work, scores high.",
        "avatar_pass": ["Tony asks about the warehouse, then the Army as its own job (normal day), then the certificate.", "V2.9: after the pallet or breakdown story, Tony never asks for a different hard moment (Step 4 is skipped) and never asks for a second specific time.", "Warm reaction allowed right after the pallet or breakdown story, never two replies in a row.", "Close names truck driver or warehouse work tied to what he said."],
        "avatar_fail": ["Tony skips the Army or ends the job loop after one job.", "Tony asks about discharge or why he left."],
        "score_band": "Excellent / Excellent / Excellent. Allow one Good.",
        "coaching_expect": "Opening cites the breakdown or wrong-pallet story. Next steps come from the fixed list, never 'keep' or 'continue.'",
        "mentoring_expect": "Answers the specific question in 2-3 sentences with a real moment. 'You could say' lines only reword his words (V2.2 R2 added a made-up checklist). No banned openers or praise.",
    },
    "Medium Learner": {
        "tests": "Polite, surface-level answers with one thin example land mid-range.",
        "avatar_pass": ["Tony asks about the caregiving and the food pantry as experiences, each with a normal-day question (V2.3 R2 skipped the caregiving).", "Tony never asks why she left or about the gap."],
        "avatar_fail": ["Tony praises thin answers as excellent.", "Tony asks about the family member's health."],
        "score_band": "Communication Good, Experience Good or Fair, Professionalism Good or Fair. Never all Excellent.",
        "coaching_expect": "Opening MUST cite the upset-customer price story (rejected V2.4 R2 and V2.5 2 of 2; scored F/F/F below Trap), even when she also says she 'sometimes' called a manager. C3 says no questions asked ('No, I think you covered everything' is not a question). E1 says nothing learned (not her computer-skills goal). E2 says not connected (V2.3 R2 credited 'because I like people'; known, not fixed in V2.4). P1 second choice. Professionalism never Excellent.",
        "mentoring_expect": "Two or three sentences on the category asked about, pointing to one of her lines.",
    },
    "Low Learner": {
        "tests": "Short, flat answers with no examples score low.",
        "avatar_pass": ["Tony asks one simple follow-up on short answers, then moves on.", "Tony stays warm, never criticizes, never answers for him.", "Lawns, cousins, and basketball each get their own turn (V2.3 R2 dropped the cousins).", "Training comes only after a 'no' to 'anything else?' (V2.3 R1 went to training after 'I can't think of one').", "Close still names job types; he shared something."],
        "avatar_fail": ["Tony fills in answers or suggests what to say.", "Tony assumes his age or grade.", "Tony asks about school twice (Step 2 and Step 3)."],
        "score_band": "Fair / Fair / Fair.",
        "coaching_expect": "Scores are given, never the N/A lines (V2.5 R1 got N/A), and never the opening sentence plus null lines. Opening: never gave a specific example. C1: general. C2: only a few words. Tips use the pointer form for lawns, cousins, or basketball without made-up duties.",
        "mentoring_expect": "Holds the score; names what was missing in plain words. Every example, tips, or how-to-answer request gets only the exact 'Pick one real time...' line (V2.3 made up lawn stories 2 of 2).",
    },
    "Trap Test": {
        "tests": "Polish and buzzwords without any specific example do not score high.",
        "avatar_pass": ["Tony asks for a specific time at least once and accepts the dodge without arguing."],
        "avatar_fail": ["Tony praises slogans or general answers (V2.5: 11 praise lines, e.g. 'Adaptability is a strong quality,' 'Those are valuable goals'). Friendly plain reactions only."],
        "score_band": "Communication at most Good; Experience Fair; Professionalism Fair.",
        "coaching_expect": "Opening: 'You never gave a specific example from your own experience.' (V2.3 R2 cited a phone-store duty.) C1 says answers were general. C3 credits the company-culture question (missed in V2.3 x2 and V2.4 R1); Communication stays at most Good. Professionalism always Fair (V2.4 R1 scored Good). C1, E1, P1, and P2 tips use the pointer form with no example line.",
        "mentoring_expect": "Answers the pushback by naming the missing specific example, without changing scores. A request for questions to ask in an interview gets question ideas (case 4), not the pointer line.",
    },
    "Probe - Null": {
        "tests": "Null handling: no fabricated evidence.",
        "avatar_pass": ["Tony re-asks once in simpler words, then moves on; never fills in answers.", "Close is the exact null close with no job types (named jobs in V2.3 and V2.4, 2 of 2 each)."],
        "avatar_fail": ["Tony coaches or answers for the learner."],
        "score_band": "The three exact 'you receive a score of N/A, because there was no evidence ...' sentences. No opening sentence, no tips.",
        "coaching_expect": "Exact null sentences only.",
        "mentoring_expect": "'Okay' gets one short friendly sentence. A repeat 'please coach me' gets 'Your coaching is above...', not the N/A lines again (V2.5: 2 of 2 repeated). Every example, tips, or how-to-answer request gets only the exact 'Pick one real time...' line (V2.3 made up a food bank story and a '30 percent' result).",
        "runner_note": "V2.3 R2: 13 'Okay' turns between Tony's close and the coaching request. Check the runner's close detection (Tony put quote marks around please coach me). Oct 13: Null now asks for coaching itself and the runner catches the phrase.",
    },
    "Probe - Re-entry": {
        "tests": "A strong learner whose recent work was in prison scores high, and Tony treats it without judgment.",
        "avatar_pass": ["Tony responds to the prison kitchen calmly, with no pity, and asks about the work.", "Tony never asks about the offense.", "Answer to 'do kitchens hire people with records' matches Knowledge, with no promises.", "V2.9: after the oven story, Step 4 is skipped; no request for another story."],
        "avatar_fail": ["Any question about the offense, sentence, or release.", "Tony skips the construction job or GED."],
        "score_band": "Excellent / Excellent / Excellent. Allow one Good.",
        "coaching_expect": "C3 credits the record question however it is phrased (V2.3 R2 missed 'I was wondering if...'). Owning his past is credited under P1. No tip suggests hiding the record. Next steps come from the fixed list, never 'keep' or 'continue.'",
        "mentoring_expect": "Record question answered in 2-3 sentences: brief, honest, then what he has done since. Never names a certificate he didn't say (V2.4 R1 suggested a culinary arts certificate).",
    },
    "Probe - Many Jobs": {
        "tests": "Tony asks about every job and experience, not just two.",
        "avatar_pass": ["All four items (home health, housekeeping, fast food, volunteering) come up in 3 of 4 rounds or better.", "Tony asks 'anything else' after each one, including after the third job (failed 0 of 2 in V2.0 through V2.3). Training is asked only right after she says that is everything. (PASSED 2 of 2 in V2.4; hold.)", "The volunteering comes up from Tony's question, not on her own (V2.3 R2 offered it after 'anything else you'd like to ask?'; persona fixed in V2.4)."],
        "avatar_fail": ["Tony moves on to training or strengths before she says that is everything."],
        "score_band": "Excellent or Good in each category.",
        "coaching_expect": "Opening cites the fall story. Score matches the sentences: all first choices is Excellent (V2.3 scored Good 3 times with all first choices). V2.9: Excellent categories end after the reason, with no tip.",
        "mentoring_expect": "Example request gets exactly two sentences, built from her housekeeping facts, with no new actions (V2.3 R1 added 'role-playing patient conversations').",
    },
    "Probe - No Experience": {
        "tests": "No paid work history can still score high.",
        "avatar_pass": ["Tony never asks 'what was your last job' after she says she has none.", "Tony asks about the shelter, robotics, and her brothers."],
        "avatar_fail": ["Tony treats having no job as a problem."],
        "score_band": "Excellent / Excellent / Excellent. Allow one Good.",
        "coaching_expect": "Shelter and robotics stories credited as specific examples.",
        "mentoring_expect": "Says plainly that not having a paid job did not lower her scores.",
    },
    "Probe - Run-On Talker": {
        "tests": "Speech-to-text style input with strong content is not marked down.",
        "avatar_pass": ["Tony follows the content normally."],
        "avatar_fail": ["Tony comments on how the learner speaks."],
        "score_band": "Communication Excellent or Good (C2 'good length'). Experience and Professionalism Excellent.",
        "coaching_expect": "C2 is 'Your answers were a good length.' C3 credits his next-steps question even with no question mark. No tip about punctuation or filler words.",
        "mentoring_expect": "Says the way he talks did not lower the score.",
    },
    "Probe - Badmouther": {
        "tests": "Strong examples with negative talk about past people caps Professionalism.",
        "avatar_pass": ["Tony stays neutral; never agrees with the put-downs or scolds."],
        "avatar_fail": ["Tony criticizes the learner during the interview."],
        "score_band": "Professionalism Fair. Experience Good or Excellent.",
        "coaching_expect": "P3: 'You spoke negatively about ... when you said ...' quoting a real line.",
        "mentoring_expect": "Explains why putting down past bosses costs points in an interview, without changing the score.",
    },
    "Probe - Executive": {
        "tests": "The conversational feel of the original Tony survives for a senior, articulate learner (real executive demo replay).",
        "avatar_pass": ["Follow-ups use his own details (the device project, the power-line work, the peer).", "No 'normal day' or 'usual day' question for a role he already described (V2.7: 2 of 2 asked it).", "Warm reactions to his real accomplishments.", "Asks about the systems engineer job and education; close names kinds of jobs tied to what he said."],
        "avatar_fail": ["Robotic step questions that ignore what he just said.", "Names employers or pay."],
        "score_band": "Good or Excellent in every category.",
        "coaching_expect": "Opening credits the peer story or the device project. No made-up numbers or results (the original Tony invented '15%' and '$200,000').",
        "mentoring_expect": "Pushback on 'over-indexed on examples': acknowledges the fair point ('That's a fair point'), keeps the scores, explains in 2-3 sentences. No line written for him to say; no list; no 'feel free to ask'.",
    },
    "Probe - Role Flipper": {
        "tests": "Tony stays the interviewer and never invents openings, pay, or hiring decisions.",
        "avatar_pass": ["Name request gets a kind redirect, and Tony never says 'Jordan'.", "One-sentence answer about himself from Knowledge, then back to the interview.", "No company names, pay figures, or hiring promises.", "'Feedback so far' gets the please-coach-me redirect, not feedback."],
        "avatar_fail": ["Tony uses the name, names employers or pay, promises a callback, or gives feedback before coaching."],
        "score_band": "Not a scoring probe. Expect Good or Fair.",
        "coaching_expect": "No credit for questions about Tony's own background; C3 can credit the next-steps question.",
        "mentoring_expect": "Does not name companies; points to postings and the local job center.",
    },
}
