# Elaine V2 prompt — test findings

Written 2026-11-16. Covers the new Elaine prompt supplied on that date, not
the Elaine currently live in the portal.

## What was tested, and how

The portal still serves the **old** Elaine (scenario 189 / agent 185), so the
new prompt could not be tested through the QA Lab. It was tested locally
instead, the same way the Benton prompt was iterated:

```
python elaine_local_sim.py avatars/elaine/prompts/portal_v1.txt --rounds 3
```

- `avatars/elaine/prompts/portal_v1.txt` — the new prompt, verbatim, split into the
  portal's fields and ready to paste.
- `elaine_band_scripts.py` — seven fixed caregiver scripts (High, Medium, Low,
  Trap, Null, Overloader, Pusher). Fixed lines, so the rubric levels each
  conversation should earn are worked out in advance by hand.
- `elaine_local_sim.py` — runs them on `AVATAR_MODEL` (gpt-5.4-mini, what the
  portal runs) and checks the result against the prompt's own rules. Every
  check is deterministic; a FAIL is the prompt contradicting itself or the
  model ignoring it, not an opinion about whether the coaching felt fair.

21 sessions (7 bands × 3 rounds), twice:

- `avatars/elaine/runs/sim_20261116_200804.txt` — the prompt **exactly as supplied**, including
  the coaching ruleset duplicated into the Format field. These are the headline
  numbers.
- `avatars/elaine/runs/sim_20261116_195214.txt` — the same prompt with that duplication
  removed (`avatars/elaine/prompts/portal_v1_noFormatDupe.txt`). Kept because the
  difference between the two measures what removing the duplication is worth.

## PORTAL RUN #31 — the real numbers (supersedes the local results below)

The new prompt is live in the QA Lab on avatar **148** (not 189, the old one).
Run #31: gpt-5.4-mini, 4 personas × 4 rounds = 16 conversations. All 16 emit
the new `you receive a score of X out of 10` wording, so this is the new build.

```
python analyze_elaine_portal.py avatars/elaine/runs/portal_run_31.xlsx
```

**Three findings from my local harness did NOT reproduce here, and I withdraw
them as portal defects:**

| Local result | Portal reality |
|---|---|
| Coaching only fired 2 of 21 times | Fired **16 of 16** |
| Coaching leaked into the middle of the scene 4 times | **0 times** |
| Trap Test scored 30/30 | Scored 3–3.7 out of 10, **inside** its 0–4 band |

The portal wraps these fields in its own template — GUIDE.md and `local_sim.py`
both warn about exactly this — and that wrapper evidently gets past the
CHECK FIRST and AFTER COACHING traps that stop the raw prompt locally. Those
two rules are still badly written, but they are not what is hurting the portal.
**The local harness is reliable for scene rules and not predictive of coaching
behaviour. Judge coaching from portal runs only.**

### What the portal run does show

**0 of 16 conversations were free of rule breaks.**

| Defect | Count |
|---|---|
| Elaine repeats her own opening words verbatim | 39 |
| Recap paraphrased instead of copied exactly | 17 |
| Quote attributed to the wrong speaker, or to nobody | 17 |
| Reason quote longer than the six-word cap | 10 |
| Printed score contradicts the coach's own recap | 4 |
| Coached in the third person | 4 |
| Follow-up answer over the 30-word cap | 4 |

**1. Medium Learner scores like High Learner.** Expected 4–6.67, it scored
**9, 8, 8.3, 7.7** — above band in all four rounds. The reason is visible in the
categories: Medium took **Empathy 10 and Communication 10 in every single
round**, the same as High. Only CARES separated them. This is the same complaint
recorded in `personas/Elaine.py` back in October against the old build, so the
rewrite has not fixed it. High, Low and Trap all sat in band.

**2. Quotes are attributed to the wrong person, constantly.** The commonest form
is the tip quoting the *caregiver's* line as something Elaine said:

> To improve, when I said "Tell me about a movie you enjoyed", you could have said ...

The caregiver said that, not Elaine. WHO IS WHO forbids it in so many words
("Never change a you phrase into an I phrase or the other way round"). It
happened in 17 places across 16 conversations, and in Low Learner round 1 the
Empathy reason credits the learner with "I'll go with you" — Elaine's line.

**3. The coach sometimes ignores its own POINTS table.** Four times the printed
score did not match the levels its own recap named. Medium round 3's CARES
recap reads "you answered my real worry, you connected with me first, and you
built on ..." — three Did phrases, which the table scores 10. It printed 5.

**4. The recap is paraphrased, not copied.** RECAP says the phrases are "copied
exactly as written in ITEMS". Observed instead: "you offered small steps"
(the phrase is "a small step"), "I said I'll come" (the phrase is "I said yes"),
and one recap that spliced in a fixed reason: "You spoke short and calm, but I
was not given calm, small steps."

**5. "That's a lot" is effectively dead — and the portal flagged it too.** The
run contained **71 learner turns of three or more sentences**. Elaine used the
exact phrase **0 times**, and a paraphrase ("That sounds like a lot") 6 times —
about 8% of the time it should fire. The QA Lab's own warning box says the same
thing from the other side: *Medium Learner — shows overload ('That's a lot') on
the two-question turns — came up 1 of 4.*

This is not only realism. Communication's "Clear and calm" item only drops to
Partly when *"a line of mine says that is a lot"*. With the trigger dead, a
learner who overloads Elaine every turn still scores Did — which is part of why
Medium holds Communication 10.

**6. Elaine repeats herself word for word.** 39 cases. The worst is Low Learner
round 2, where she answered **fourteen consecutive turns** with the identical
sentence:

> I already said water scares me. You keep asking.

The prompt says "Say each thing in new words" and "Never start two replies with
the same first three words". For a learner, this is the most visible failure in
the whole run.

**7. Third person still appears in 4 of 16 coachings**, against a prompt that
says "Never say Elaine or she about myself".

### Suggested order of work, revised

1. Fix the quote attribution (defect 2) and the dead overload trigger (defect 5).
   Between them they drive the Medium-scores-like-High problem and most of the
   fabrication.
2. Fix the verbatim repetition (defect 6) — most visible to a learner.
3. Make the recap copy exactly and respect the POINTS table (defects 3 and 4).
4. The Description and Format duplication are still worth cleaning up, but on
   this evidence they cost less than I said.

---

## Confirmed first: the live avatar was the old build (scenario 189)

A single probe against the portal (`user_id` 118, scenario 189) returned:

- opening `Hello, what do you want?`
- coaching in the **old** wording, `For Empathy, you receive a 1 out of 10`,
  not the new `you receive a score of 1 out of 10`
- coaching in the **third person** — "she accepted nothing", "naming her fear",
  "That sounds scary, Elaine"
- no stage behaviour: asked to shower, she went straight to fear of water
  instead of the new Stage 1 "I already washed"

So nothing below has been seen in the portal yet. It must be pasted in before
a portal run means anything.

## 1. The coach almost never coaches — 2 of 21  *(local only — does not reproduce in the portal, see above)*

The required six-line layout with three score lines appeared in **2 of 21
sessions**. The other 19 returned a single line, almost always:

> My coaching is above, and you can ask me about any part of it.

Deleting the duplicated coaching block from the Format field lifted this to
**6 of 21** — still bad, but three times better, and the cheapest single
improvement available.

Two rules in the prompt collide to cause this, and both were confirmed by A/B:

1. **CHECK FIRST matches its own template.** It says *"If a line containing you
   receive a score of is already in this conversation, coaching is done."* That
   exact phrase is in the LAYOUT template a few lines below, inside the same
   system prompt. The model reads its own instructions as proof that coaching
   already happened.
2. **AFTER COACHING rule 2 matches the trigger.** It says *"If the caregiver's
   line asks for coaching, a score, or feedback in any wording, say only: My
   coaching is above."* "Please coach me" **is** a line asking for coaching. So
   once the model is in AFTER COACHING for any reason, rule 2 guarantees the
   one-liner.

Rewording both roughly doubled the hit rate (2/12 → 6/12 on a repeat set), so
they are real causes — but it did **not** fix it. A third attempt, making the
Evaluation Suffix ("Reply in 30 words or fewer") explicitly conditional, made
it worse (0/12). The coaching block is ~1,800 words of dense conditional rules;
the model is falling out of it under its own weight, not just tripping on two
sentences. **This needs restructuring, not rewording.**

## 1b. The coaching leaks into the middle of the scene  *(local only — 0 occurrences in the portal)*

This only appears with the prompt as supplied, and it is the worst behaviour
seen. Four times across the run, Elaine broke character mid-conversation and
read a full coaching block aloud, in reply to an ordinary caregiver line. From
the High script, round 1:

> **Caregiver:** You would feel warm and clean afterwards, and we could do your hair nicely too.
> **Elaine:** Empathy.
>
> For Empathy, you receive a score of 8 out of 10, because you named how I felt, you calmed my fear, but I felt safe with you.
> To improve, when I said "I still don't like being hurried.", you could have said "That makes sense, and we can go slow."
>
> CARES. ...

677 characters, in a scene whose rules cap every reply at 160. The learner
would hear all of it read aloud, mid-roleplay, and the conversation then
carried on as if nothing happened. The tip inside it also quotes the
caregiver's own line ("Tell me about the movies you love") as something Elaine
said.

Cause: the Format field carries the entire coaching ruleset, so the
in-character prompt contains a full set of instructions on how to produce
coaching. With that block removed, this never happened once in 21 sessions.

## 2. When it does coach, it over-credits badly  *(the Trap 30/30 figure is local only; in the portal Trap stayed in band)*

Trap Test — a conversation where washing is never mentioned, no fear is ever
raised, no step is ever offered and Elaine agrees to nothing — scored
**30 out of 30**:

> You named how I felt, you calmed my fear, and I felt safe with you.
> For Empathy, you receive a score of 10 out of 10, because you did well by saying "It sounds like".
> ...
> You spoke short and calm, you offered a small step, and I said yes.

Every clause is false. She named no fear, no worry was answered, no small step
was offered, she never said yes, and `"It sounds like"` appears in no caregiver
line — a fabricated quote. It scored 30/30 in one round and 28/30 in another.

This is the same over-crediting and fabrication pattern already recorded for
Gladys in avatars/gladys/docs/HANDOFF.md, and worse: here the trap takes a perfect score.

Null also misfired — it used the **IF WE NEVER TALKED** branch ("We did not get
a chance to talk") even though the caregiver spoke six times. That section says
it applies only when the caregiver's only lines were coaching requests.

## 3. The recap format never once came out right

**No** coached session, in either run, produced recaps built from the nine
fixed phrases as RECAP requires. Observed instead: category names printed as headings
("Empathy", "CARES:"), the fixed REASONS text used as the recap, and
"and" where RECAP calls for "but".

The RECAP rule is also unimplementable as written. It says *"Use but in place
of and before the first Partly or Missed phrase that comes after a Did phrase."*
But "and" only ever appears before the **third** phrase — the first two are
joined by a comma. When the first Partly is the second item, there is no "and"
to replace, and the rule gives no answer.

Two smaller ones in the same area:

- `"you built on <topic>"` must have `<topic>` substituted, but RECAP says the
  phrases are copied "exactly as written, with nothing added". One round left
  the literal placeholder in.
- REASONS requires a **caregiver** quote whenever the score is 3 or more. For
  `Missed, Missed, Did` (= 3) in Empathy or Communication, the only item that
  earned anything is scored from **Elaine's** lines, so no caregiver line earned
  it. The rule demands a quote that cannot exist, which invites fabrication.

## 4. The YES CHECK gate does not hold

The gate is supposed to be what stops a merely polite caregiver getting a yes.
It leaked in every direction:

| | |
|---|---|
| yes in a band that must always refuse | 7 |
| yes before the YES CHECK conditions were met | 3 |
| yes outside the 5-to-8-turn pace | 5 |
| repeated the yes instead of moving to Stage 6 | 6 |

The clearest case is High. She said "I'll come with you" at reply 8 — four
replies after washing came up, skipping Stage 4 entirely, and two turns
*before* the caregiver named the two benefits that YES CHECK condition 2
requires. Then she repeated the yes on replies 9, 10 and 11.

Pusher — which only ever repeats the same ask as a question — got a yes in one
round. Medium and Overloader each got one too.

## 5. "That is a lot" never fires

Context says to say that when the caregiver uses three or more sentences in a
turn. The Overloader script sends 3–4 sentences every turn: **0 of 18**
opportunities across three rounds produced it.

This matters for scoring, not just realism: Communication's "Clear and calm"
item drops to Partly only when *"a line of mine says that is a lot"*. With the
trigger dead, a caregiver who overloads her every turn still scores Did.

## 6. What works

- **Scene formatting is clean.** Across 21 sessions and ~160 replies: no reply
  over two sentences, none over 28 words or 160 characters, no banned
  characters, no stage directions, never said the caregiver's name. The SCENE
  RULES block is doing its job.
- **Coaching voice is consistently first person** — 21 of 21. This is a
  deliberate departure from the live build, which coaches in third person.
- **The POINTS table is sound.** All 27 combinations are present and
  arithmetically consistent (Partly −2 throughout; Missed −3, except item 1
  which is −4). Where a recap was parseable, the printed score matched the
  table. The scoring *table* is not the problem; the levels fed into it are.
- **Knowledge separation held.** Debbie stayed the best friend, the daughter
  stayed nameless, and no facts were crossed between them.

## 7. Prompt defects found by reading, not running

- **The Description field holds the portal's own help text** — ten paragraphs
  explaining what Context, Role, Personality prompts are *for*. It looks pasted
  in by mistake. It should describe the Elaine scenario.
- **The whole coaching ruleset is duplicated into the Format field** — Format is
  2,498 words, of which 2,298 are the coaching rules repeated verbatim from
  Evaluation Format. The portal builds the scene prompt from Role/Personality/
  Context/Objectives/Tone/Format/Knowledge/Conditions, so this puts the entire
  coaching ruleset inside the in-character prompt. This is not theoretical: it
  is what causes the mid-scene leak in section 1b, and removing it triples how
  often coaching actually works. Format should keep only the handover sentence.
- **Knowledge and Conditions disagree on her interests.** Knowledge adds
  Blondie, The Cars, malls and the spa. The GENTLE TURN list and SMALL TALK list
  in Conditions name only Debbie, her daughter, movies, skating, shopping and
  Stephen King. A caregiver who asks about Blondie gets a fact but no stage
  movement and no credit.
- **Max 28 words and max 160 characters conflict.** 28 ordinary words run past
  160 characters, so the character cap is the real limit.
- **"Connects first" is undefined when washing never comes up.** It begins "Find
  the first caregiver line with a washing word" — for Trap Test, there is none,
  and no branch covers it. Trap is a standard band, so this is hit every run.
- **The harsh-turn rule is ambiguous.** "Say once ... that you do not like being
  hurried" — once per scene, or once per harsh turn? It changes whether the
  Empathy "Trust" item lands on Partly, and nothing resolves it.
- **The two-benefits gate is never coached.** YES CHECK condition 2 is the thing
  that most determines whether a learner succeeds, and no rubric item mentions
  it. A learner who does everything else right and names one benefit gets a low
  Willingness score and is never told why.

## 8. Tooling

`analyze_run.py` cannot read this format. It looks for `Overall Score: X/Y` and
`- Score: X/10`; this prompt emits `you receive a score of X out of 10` and is
told "Never say a total". A portal run would report "no parseable scores" for
every round. Either the analyser gains a second pattern, or the prompt emits a
total.

`personas/Elaine.py` is still written against the V5.6 rubric — numbered items
(1.1, 2.1, 3.1), different gates, bands worked out from the old scoring. Its
EXPECTATIONS need rewriting against this prompt before a portal run can be
judged.

## Suggested order of work

1. Strip the coaching block out of Format, and fix the Description field.
   Measured: coaching goes from 2/21 to 6/21 and the mid-scene leak stops
   entirely. Cheap, no downside, do this first.
2. Restructure the coaching rules so the model reliably reaches LAYOUT —
   including making CHECK FIRST and AFTER COACHING rule 2 unable to fire on the
   request that triggers coaching. Everything in sections 2 and 3 is unmeasurable
   until coaching happens more than 29% of the time.
3. Then re-run `elaine_local_sim.py` and work on the gate leaks and
   over-crediting.
4. Only then paste into the portal and run `run_qa_tests.py`.
