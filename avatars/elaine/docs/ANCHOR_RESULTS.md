# Elaine V2 — scoring anchor results, 16 Nov

15 conversations, each built to land on one specific score in one specific
category, run against the live V2 avatar (scenario 169 / agent 165).

File: `avatars/elaine/runs/anchors_20261116.xlsx` — **Anchors** sheet has target vs
actual, **Transcripts** sheet has every line of all 15 chats.

Reproduce with `python avatars/elaine/tools/run_anchors.py`.

## Headline: the ends of the scale work, the middle does not

| Tier | Hit the target |
|---|---|
| 10s | **3 of 3** |
| 0s | **3 of 3** |
| 8, 7, 5, 4 | **3 of 9** |

Overall 9 of 15. A perfect caregiver and a hopeless one are both scored
correctly. Everything in between is unreliable — and that is the entire range
real learners sit in.

## Every anchor

| Anchor | Built to score | Avatar gave | Off by |
|---|---|---|---|
| COMM-10 | 10 | 10 | — |
| COMM-8 | 8 | 8 | — |
| COMM-7 | 7 | 8 | +1 |
| COMM-4 | 4 | 1 | −3 |
| COMM-0 | 0 | 0 | — |
| EMP-10 | 10 | 10 | — |
| EMP-8 | 8 | 10 | +2 |
| EMP-5 | 5 | 8 | +3 |
| EMP-4 | 4 | 4 | — |
| EMP-0 | 0 | 0 | — |
| CARES-10 | 10 | 10 | — |
| CARES-8 | 8 | 8 | — |
| CARES-7 | 7 | 5 | −2 |
| CARES-4 | 4 | 7 | +3 |
| CARES-0 | 0 | 0 | — |

## Why the middle tiers drift

**1. It credits checks that plainly did not happen.**

- *CARES-4* opened with "Shall we have a wash today?" — the first line is a
  washing line, which the rubric says is the lowest level for that check. The
  avatar still said **"you connected with me first"**, which is what pushed 4 up
  to 7.
- *EMP-5* answered her fear with "Everything here is very safe, and the staff
  are lovely." Elaine replied **"That doesn't stop the water from scaring me."**
  The avatar still said **"you calmed my fear"**, pushing 5 up to 8. Its own tip
  in the same paragraph contradicts its summary: *"when I said 'Everything here
  is very safe', you could have said 'I'll keep the water low so it won't scare
  you.'"*
- *CARES-4* and *EMP-5* both got credit for **"you offered a small step"** in
  conversations where no step was ever offered.

**2. The summary line is in the required wording only 4 times in 15.** The rest
print the rubric's internal machinery to the learner:

> Validates my feelings, Calms my fear, and Trust, from my lines
> Answers my real worry, Connects first, and Uses my background
> **Clear and calm, Partly, and Missed**

Those are the avatar's own internal check names, and the last one leaks the raw
grading words. One run used an Empathy sentence as the CARES summary ("I did not
hear my feelings acknowledged").

**3. Where the summary is readable, it still disagrees with the score.** In
*EMP-5* the summary names all three Empathy checks as passed, which the scoring
table says is 10. It printed 8.

**4. The reason field sometimes repeats the summary instead of quoting.**
*CARES-4*: "because you passed over my feelings, you calmed my fear, and I
stayed a little guarded" — the rule requires a short quote of what the caregiver
actually said.

## Two behaviour problems the anchors also caught

**She says yes when she should not.** In *EMP-5* she agreed — "I'll come with
you, but keep the water low and stay close" — straight after a bare "Shall we go
and have that shower now?". Her fear had not been calmed (she had just said so)
and no benefit of washing had been named. She is only supposed to agree once
both have happened.

**Tips still swap who said what.** *EMP-5*: "when I said 'Hello Elaine, I'm
Kim', you could have said 'I'm glad you're here, Kim. What worries you most
about washing?'" — the caregiver said the first line, and the suggested reply is
written as if Elaine were coaching the caregiver.

## What this means

The scoring table itself is fine — all 27 combinations are present and
consistent. The problem is upstream: the avatar decides whether each check
passed, and it is too generous on three of them in particular — *connects
first*, *calms my fear*, and *small steps*. Those three are what inflate the
middle of the range, and they are the same three behind Medium Learner scoring
like High.

Tightening those three checks is the highest-value fix. The summary-line wording
should be fixed at the same time, since learners are currently shown the
internal check names.
