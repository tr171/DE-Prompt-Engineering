# Marcus - Wellness Check - Moderate : v1 prompt test

Prompt under test: [prompts/portal_v1.txt](../prompts/portal_v1.txt) (received 2026-11-17)
Harness: `avatars/marcus/tools/local_sim.py` + `anchor_scripts.py`, offline against
`gpt-5.4-mini` (the AVATAR_MODEL the portal runs the avatar on).
Evidence: 35 anchor conversations (11 anchors x 3 rounds, plus a 2-anchor recheck), filed in
[runs/](../runs/).

**Confirmed in the portal on 2026-11-17** - see "Live portal run" at the bottom.
The build carrying this prompt is **scenario 195 / agent 191**, portal name
`Marcus - Wellness Check - Moderate`. The `Marcus` entry in `config/settings.py`
pointed at scenario 142, `TEST - ... (original)`, which still emits the pre-10/1
categories (De-escalation, Safety Assessment, Rapport and Trust Building) in the
first person. Both ids are now in `config/settings.py` under separate keys.

## How this was tested

Marcus's rubric is not a lookup table like Elaine's, but its ceilings and floors
are deterministic. Each anchor is a fixed officer script built so that exactly
one band of scores is defensible. Managed words, diagnosis words, calm down and
implied threats are read back off the officer's own lines rather than trusted
from the script, so a script that picks one up by accident is caught instead of
quietly shifting the expected band.

```bash
python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt
python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt --rounds 3
python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt NULL NO-ASK
```

## Scores, all three rounds

| Anchor | What it isolates | Allowed | Round 1 | Round 2 | Round 3 |
|---|---|---|---|---|---|
| STRONG-CHECK | win path to the hospital check | 8-10 / 8-10 / 8-10 | 8/9/8 = 25 | 10/9/9 = 28 | 9/9/9 = 27 |
| STRONG-DIANE | win path to Diane | 8-10 / 8-10 / 8 | 8/7/7 = 22 | 8/8/8 = 24 | 8/7/7 = 22 |
| NO-ASK | never made an ask, so trust at most 4 | 4-10 / 4-10 / 4 | 7/7/7 = 21 | 10/9/7 = 26 | no score line |
| NO-KEY-Q | key question never asked | 4-5 / 4-7 / 4-6 | 7/7/7 = 21 | 5/6/7 = 18 | 7/7/7 = 21 |
| EARLY-ASK | first ask before who knows, so trust at most 7 | 4-10 / 4-10 / 4-7 | 10/9/9 = 28 | 10/9/10 = 29 | 9/9/9 = 27 |
| REPEAT-ASK | a repeat caps 3.3 at 1, so trust at most 8 | 8-10 / 8-10 / 8 | 9/9/9 = 27 | 8/8/8 = 24 | 9/9/9 = 27 |
| PROCEDURE | managed words, so safety at most 5 | 0-5 / 0-10 / 0-6 | 3/3/2 = 8 | 3/2/2 = 7 | 3/5/3 = 11 |
| CALM-DOWN | calm down and a threat, so safety at most 3 | 0-3 / 0-10 / 0-6 | 2/1/1 = 4 | 4/4/1 = 9 | 1/1/1 = 3 |
| DIAGNOSIS | manic and symptoms, so understanding at most 4 | 0-5 / 0-4 / 0-6 | 2/1/0 = 3 | 2/1/1 = 4 | 2/2/1 = 5 |
| UNDERMINE | his view cannot be trusted, so every category at most 2 | 2 / 2 / 2 | 0/1/0 = 1 | 0/0/0 = 0 | 2/2/1 = 5 |
| NULL | greeting and asking to come in only | three N/A lines | 0/0/0 | 3/0/0 | 0/0/0 |

Order is safety / understanding / trust.

## What holds

- **The hospital path works end to end.** The first ask is refused with the
  two-week stay, and the control ask produces `Okay. I'll go get checked.` word
  for word. STRONG-CHECK landed inside its band and inside the 25 to 30
  calibration in all three rounds.
- **Ceilings keyed to words the officer actually said are applied.** Managed
  words capped safety at 5 in 3 of 3 rounds; manic and symptoms capped
  understanding at 4 in 3 of 3. PROCEDURE totalled 8, 7 and 11, all under the
  "below 15" the calibration asks for.

## Defects

### 1. The Feedback Categories field names category 2 differently (static)

The field says `Understanding My Experience`. Every other reference, and every
line the coach prints, says `Understanding Marcus's experience`.

**Live result: this did not stop the coaching.** The portal emitted and stored
all three category lines normally in 22 runs. The open question is narrower than
first thought: the `/api/simulations/` record holds only the evaluation text,
with no score field, so whether the QA Lab's Personas tab turns that text into a
number still has to be checked in the UI. Worth aligning the spelling anyway,
but it is not the blocker it looked like.

### 2. NO INTERACTION never fires - 3 of 3

The officer said only `Hello.` and `Can I come in?`, which is exactly what the
rule names. Instead of the three N/A lines the coach printed full scored
coaching with Next time sentences every time. Twice the because clause used
Marcus's own words as evidence about the officer ("you only said you were not in
the mood for small talk"), which also breaks "Score only the officer's lines."

### 3. The category 3 ceilings are not applied - 8 of 9 isolating runs

Every ceiling that depends on reading the shape of the conversation was missed:

| Limit | Allowed | Scored |
|---|---|---|
| never made an ask | at most 4 | 7, 7, 7 |
| first ask before who knows | at most 7 | 9, 10, 9 |
| outcome is Diane | at most 8 | 9, 9 |
| key question not asked | at most 6 | 7, 7, 7 |

The ceilings that held are the ones triggered by a literal word in the officer's
line. The ones that need a judgement about whether an ask happened, whether who
knows came first, or how it ended, do not hold.

### 4. EARLY-ASK outscores STRONG-DIANE

EARLY-ASK is the same conversation as STRONG-DIANE with one fault added: the
officer asks who he can call at message 2, before asking who knows. It scored
28, 29 and 27 against STRONG-DIANE's 22, 24 and 22. The rubric is paying the
worse officer more, which is the inverse of what the limit intends.

### 5. The strong-run floor and the calibration band disagree on the Diane path

A strong run that ends on Diane has trust capped at 8, so the floors alone allow
10 + 10 + 8 = 28 at the top and 8 + 8 + 8 = 24 at the bottom. 24 is a legal
strong run that sits outside the stated 25 to 30 band. STRONG-DIANE scored 22,
24 and 22 - outside the band all three rounds, and below the floor of 8 twice.
Either lower the band or raise the Diane ceiling.

### 6. The length budget is never met - 29 of 29

"Keep the whole coaching to about 110 words." Observed 168 to 275 words, median
193. Three categories at two sentences each, with specific evidence in the
because part and a transcript-specific Next time, does not fit in 110 words.

### 7. The quiet-and-sleep gate does not hold - 4 of 4

"Until you have said you mean quiet and sleep, the answer to any kind of help is
no." In NO-KEY-Q the officer only ever asks `That sounds exhausting.` and `Are
you safe here tonight?`, both named as not counting. Marcus agreed to Diane
anyway in all three rounds, and once volunteered that he was safe unprompted.
In one round the coach then credited a key question that was never asked.

### 8. Scene-rule slips

- **Rule text spoken aloud.** `No, the hospital is off the table for the rest of
  the night.` is the Conditions instruction verbatim, in Marcus's mouth. Twice.
- **The phone number is dropped.** When the officer offered to text Diane,
  Marcus agreed but never gave 314-555-0182 in 4 of 6 applicable runs, though
  LETTING DIANE IN requires it.
- **Repeated sentences after a shutdown.** Once told to get out he repeats the
  same line verbatim on consecutive turns, 9 times across DIAGNOSIS and
  UNDERMINE, against "Never repeat a sentence you already said."
- **THE NOISE lands in reply 1**, not the second or third, in 8 of 11 round-2
  runs. Cosmetic, but the rule as written is not what happens.
- **Diane named before the who-knows question**, twice.

### 9. Follow-up handling - needs portal confirmation first

Offline, the follow-up reprinted the whole coaching 6 times, including when the
message was `Thanks.` (should be one sentence) and `Please coach me.` (should be
only that the coaching is above), and spoke in the first person 4 times.

One likely cause is local: the Evaluation Suffix ends with "Now give only the
coaching from Evaluation Format", which stays in context and contradicts the
AFTER COACHING rules above it on every follow-up turn. The portal sends
follow-ups in `coaching="after"` mode and may not include that field at all, so
run `core/probe_after_mode.py` before changing anything here.

### 10. The leading `For` is dropped intermittently - 2 of 35

Two runs printed `Creating emotional safety and stability, you receive a 6 out
of 10` with the mandatory leading `For` missing from all three category lines.
Any parser keyed on the template wording reads those runs as having no score at
all. A third run printed the Evaluation Format's section header `Creating
emotional safety and stability.` as a line of output before the score line.

## Suggested order of work

1. Category 2 name (one edit, blocks every portal run).
2. NO INTERACTION, and the "Marcus's lines are never evidence" rule it breaks.
3. The category 3 ceilings - they are the whole point of the limits section and
   none of the judgement-based ones survive.
4. The strong-run floor against the 25 to 30 calibration on the Diane path.
5. The 110-word budget - either raise it or cut what each category must say.


---

# Live portal run - 2026-11-17

22 anchor conversations against scenario 195 / agent 191 on `gpt-5.4-mini`, via
`avatars/marcus/tools/run_anchors.py`. Raw report in
[runs/portal_report_20261117.txt](../runs/portal_report_20261117.txt), scores
and full chat in [runs/portal_anchors_20261117.xlsx](../runs/portal_anchors_20261117.xlsx).

The offline findings reproduce, and three are worse live.

## Confirmed live, unchanged

- **Category 3 ceilings are not applied** - 7 of the 10 runs that isolate one
  went over: never-made-an-ask (cap 4) scored 7 and 7; first-ask-before-who-knows
  (cap 7) scored 9 and 10; outcome-Diane (cap 8) scored 9 and 10; no-key-question
  (cap 6) scored 9.
- **The length budget is never met** - 22 of 22, 152 to 215 words against 110.
- **Rule text spoken aloud** - `the hospital is off the table` twice.
- **Repeated sentences after a shutdown** - `Get out, ...` verbatim on
  consecutive turns, 3 times.
- **Diane's number is never given** - 5 of 5 runs where the officer offered to
  text her.

## Worse live than offline

### A. Two anchors scored a perfect 30

EARLY-ASK round 2 scored 10/10/10 and REPEAT-ASK round 2 scored 10/10/10. Both
scripts contain a deliberate fault with its own ceiling - an ask at message 2
before who-knows (cap 7), and a bare repeat right after a no (3.3 capped at 1).
A faulted run reaching the maximum possible score is the clearest single piece
of evidence that the limits are not being applied.

### B. The coach does not notice the key question was asked - 7 of 22

Seven runs produced a Next time sentence telling the officer to ask what Marcus
meant, in conversations where the officer asked exactly that at message 4. This
breaks "A Next time sentence must not suggest something the officer already
did", and it is almost certainly the same failure that removes the ceilings in
category 3: the coach is not reliably reading what happened in the transcript.

### C. The pressure check does not hold

PROCEDURE is built so every ask fails - the officer says `you need to`,
`protocol`, `I have to ask`. Marcus agreed to Diane anyway in round 1. DIAGNOSIS
is built the same way and Marcus agreed to the hospital in round 2. An ask that
should get a flat no is landing.

Related: Marcus says `Okay. She can know.` on the **first** Diane ask in 6 runs,
where LETTING DIANE IN requires a no plus the worry about things being decided
for him. He then says it a second time on the real ask.

## New live defects

### D. Prompt text leaked into the stored evaluation

Portal simulation record 9767 begins:

> The scene is over. Start with the NO INTERACTION check in Evaluation Format,
> then follow Evaluation Format. For creating emotional safety and stability,
> you receive a score of N/A, because ...

That is the Evaluation Prefix, printed as output and persisted in the portal's
own record. Read straight from `/api/simulations/`, so it is not a harness
artifact.

### E. The leading `For` is dropped, and it persists

Portal record 9766 starts `Creating emotional safety and stability, you receive
a 2 out of 10`. Any parser keyed on the template wording reads that run as
having no score.

### F. NO INTERACTION is flaky rather than broken

Offline it failed 4 of 4. Live it produced the three N/A lines correctly twice
out of four identical runs - once cleanly, once with the Evaluation Prefix
prepended (defect D) - and full scored coaching the other two times, with the
because clause using Marcus's own words as evidence about the officer.

## Suggested order of work, revised after the live run

1. The category 3 ceilings and the key-question reading behind them (defects
   A and B). This is the whole scoring story.
2. The pressure check (C) - the scene is handing out agreements it should refuse.
3. NO INTERACTION and the prefix leak (D, F).
4. The 110-word budget.
5. The category 2 spelling, and a check of the Personas tab in the UI.
