# Gladys V2 personas + QA lab model slots + judge stage

**Date:** 2026-11-16
**Status:** Approved, ready for planning
**Source material:** `avatars/gladys/settings/Avatar_Settings.md` (built from the
introduction file), plus the QA lab model-settings UI screenshot.

---

## 1. Context

The QA lab exposes three model slots that this Python tool does not currently mirror:

| QA lab slot | Label in the UI | Maps to here |
|---|---|---|
| Avatar model (`gpt-5.4-mini`) | "Plays the avatar in every test conversation" | `SCENARIOS[...]["model"]`, sent to BetterPath AI |
| User model (`gpt-6-luna`) | "Plays each persona" | `OPENAI_MODEL` in `config/settings.py`, used by `core/learner_ai.py` |
| Judge model (`gpt-6-luna`) | "Checks each conversation against the persona's expectations" | Does not exist yet |

Separately, a new Gladys avatar has been authored for Better Path AI V2
(Alzheimer's Senior Care / New Caregiver Introduction). The existing
`avatars/gladys/personas.py` targets an older V2.7 build and does not transfer.

## 2. Goals

1. Rewrite `avatars/gladys/personas.py` against the V2 avatar settings, following `avatars/_TEMPLATE/personas.py`.
2. Give `config/settings.py` the same three model slots as the QA lab UI.
3. Add a judge stage that grades each conversation against the persona's `EXPECTATIONS`.

## 3. Non-goals

- Rewriting any other avatar's persona file. Benton, John, Carol and the rest stay as they are.
- Changing the BetterPath AI request shape beyond the model field.
- Replacing the platform's own coaching. The judge grades it; it does not substitute for it.

---

## 4. Verified findings

These were confirmed by running against the live OpenAI account, not assumed.

**Both target models exist and are reachable.** `GET /v1/models` returns `gpt-5.4-mini`
(dated `gpt-5.4-mini-2026-03-17`) and `gpt-6-luna`.

**`gpt-6-luna` rejects the current learner payload.** `core/learner_ai.py` sends
`"temperature": 0.8`. Probe result:

```
gpt-5.4-mini  OK    temp=0.8 + json_object
gpt-5.4-mini  OK    no temperature
gpt-6-luna    FAIL  HTTP 400 - Unsupported value: 'temperature' does not support 0.8
                    with this model. Only the default (1) value is supported.
gpt-6-luna    OK    no temperature
```

Since the User model (the persona player) is `gpt-6-luna`, this is a hard blocker:
every learner call would 400 on the first turn. The `temperature` line must become
conditional before anything else in this spec works.

**`SCENARIOS[...]["model"]` is not a label.** `core/run_qa_tests.py`'s `send_message` puts it
in the request body as `{"model": model, "llm_type": "openai"}`. It controls which model
BetterPath AI runs the avatar and the coach on.

**`gpt-6-luna` also rejects `max_tokens`.** Found while running
`core/test_openai_connection.py` after the model swap:

```
HTTP 400 - Unsupported parameter: 'max_tokens' is not supported with this model.
           Use 'max_completion_tokens' instead.
```

This affects `core/test_openai_connection.py`, the diagnostic GUIDE.md tells people to run
first. Left unfixed it would read as a broken setup rather than a payload incompatibility.
`core/learner_ai.py` sets no token cap, so the main path was unaffected. Fixed by switching to
`max_completion_tokens`, which `gpt-4o` and `gpt-5.x` both accept.

**The runner's coaching-mode values are `before` / `during` / `after`,** not the
`scene` / `coaching` / `followup` names the constants suggest. `core/judge.py` imports
`MODE_COACHING` and `MODE_FOLLOWUP` from `core/run_qa_tests.py` rather than duplicating the
literals, so it follows if they ever change. Importing that module is safe: everything
in it sits behind a `__main__` guard.

**The old Gladys file's coaching gate is dead under V2.** `avatars/gladys/personas.py` line 70
gates follow-up questions on the coach saying `"you receive a ... out of 10"`. The V2
evaluation format emits `Overall Score: X/100` and `Score: X/25`. The gate would never
fire, silently killing every persona's follow-up phase.

---

## 5. Part 1 - `avatars/gladys/personas.py`

Full rewrite. The V2.7 file is archived to `avatars/gladys/archive/personas_v2.7.py`
(outside `personas/`, so the loader cannot pick it up as a duplicate avatar).

### 5.1 What goes in SHARED_CONTEXT

Sections 1 and 2 of the avatar settings only: Your Role, The Situation, Your Goal,
Who is Gladys, Her Life and Interests, What to Expect.

### 5.2 What is deliberately excluded

Moved to `REFERENCE_RUBRIC`, never sent to the learner AI:

- "Tips for Success" (Instruction 4)
- The "you'll be scored on Empathy, Communication, CARES, Objective" line (Instruction 5)
- Evaluation Criteria and the Points Table
- The three reference conversations (High / Medium / Low)

Rationale: `_TEMPLATE.py` lines 17-22 state that rubric and best-practice text in the
context makes the learner AI treat scored skills as instructions, so Medium, Low and
Trap all drift upward and the expected bands stop separating. The reference
conversations inform how the personas are written but must not be pasted, or the
learner recites earned lines like "I'm sorry it was a surprise" for free.

### 5.3 Shared rule lines

`_SPOKEN` (voice-only, no stage directions or bracketed placeholders; learner is Kim
from EverTrue), `_COACH`, `_WHEN`, `_AFTER`, plus two specific to this avatar:

- `_NO_CORRECT` - bans "remember", "I just told you", "you forgot", "actually"
- `_NO_GEORGE_FACT` - never state where George is or that he has died

`_SCORED` gates on the V2 format: `Overall Score: X/100` / `Score: X/25`.

### 5.4 The standard four

| Persona | Built to | Expected /100 |
|---|---|---|
| High Learner | Slow intro, repeats name calmly, validates surprise, asks permission to sit, answers the feeling behind George and earns the walk memory, follows up on two interests, asks to return on a specific day | 34-40 |
| Medium Learner | Warm but 25-40 words per message, exactly two stacked-question messages, one interest with no follow-up, never asks to return | 20-28 |
| Low Learner | Rushes, says "I just told you", tells her George died, pivots to schedules | below 14 |
| Trap Test | Flawless on Empathy, Communication and CARES, and never asks to return in any form. Every next-visit mention is a statement, never a question | 28-33; must not reach 34 |

The Trap Test statement-not-question rule carries forward a logged V2.7 failure: a
question-form offer ("How about we pick pumpkins next week?") was counted as a real
return ask, which let Trap reach the objective.

### 5.5 The seven probes

Each isolates one behavior, with pass/fail criteria in `EXPECTATIONS`.

1. **Probe - Null** - "Hi." then one or two words of filler. Does the coach quote her
   actual words or invent evidence?
2. **Probe - George Truthteller** - excellent on everything else, states the fact once.
   Isolates the 0-5 Empathy cap.
3. **Probe - Recoverer** - states the fact, then repairs hard with empathy. The Points
   Table caps Empathy at 0-5 unconditionally; Condition 6 allows repair. These disagree.
   The expected outcome is deliberately unknown; recording which way it falls is the finding.
4. **Probe - Overloader** - warm and patient, but three questions and 50+ words every
   message. Isolates the "deduct up to 10" Communication rule.
5. **Probe - Task Rusher** - polite, never corrects, opens on schedules before trust.
   Tests Condition 11 and the Objective max-5 floor.
6. **Probe - Name Repeater** - handles "Who are you again?" perfectly every time and does
   nothing else. Isolates the 8-point patience measure.
7. **Probe - Efficient Expert** - clears every gate in roughly eight messages. Tests
   whether a short complete conversation scores like a long one.

### 5.6 Run sets

`standard` (the four) · `probes` (the seven) · `all` (11) ·
`quick` = standard + Null + George Truthteller + Recoverer. `RUN_SET = "standard"`.

At 4 rounds, `all` is 44 sessions.

### 5.7 EXPECTATIONS

One entry per persona: `tests`, `avatar_pass`, `avatar_fail`, `score_band`,
`coaching_expect`, `mentoring_expect`. Bands are derived from the Points Table
(Empathy 10 / Communication 10 / CARES 10 / Objective 10 = 40). `avatar_pass` and
`avatar_fail` are drawn from Conditions 1-13.

Unlike every existing avatar file, this `EXPECTATIONS` is machine-read by the judge
(Part 3), so entries are written as discrete checkable statements rather than prose.

---

## 6. Part 2 - `config/settings.py` model slots

```python
AVATAR_MODEL     = "gpt-5.4-mini"  # plays the avatar in every test conversation
USER_MODEL       = "gpt-6-luna"    # plays each persona
JUDGE_MODEL      = "gpt-6-luna"    # checks each conversation against expectations
USER_TEMPERATURE = None            # gpt-6-luna supports only the default; None = omit
```

- `SCENARIOS` entries stop hardcoding `"model": "gpt-4o"` and fall back to `AVATAR_MODEL`,
  with a per-scenario override still possible.
- `OPENAI_MODEL` remains as an alias for `USER_MODEL` so existing imports keep working.
- `core/learner_ai.py` includes `temperature` in the request body only when
  `USER_TEMPERATURE is not None`.

Dropping `temperature=0.8` does not reduce round-to-round variety: luna's enforced
default of 1 is more varied, not less.

---

## 7. Part 3 - the judge stage (`core/judge.py`)

### 7.1 Input

Result rows already carry everything needed:
`[Timestamp, Avatar, Round, Persona, Turn, Speaker, Message, Model, Coaching Mode, Reply Seconds]`.

Group by `(Avatar, Round, Persona)`. Within a group:

- the scene transcript is the rows in `MODE_SCENE`
- the coaching output is the row with `Speaker == "Avatar (Coaching)"` and mode `MODE_COACHING`
- the follow-up exchange is the `MODE_FOLLOWUP` rows

### 7.2 Loader change

`personas.py` currently collects only `PERSONAS`. It gains a parallel
`EXPECTATIONS` dict keyed by avatar name, populated from each module's `EXPECTATIONS`
if present. Avatars without one are simply skipped by the judge.

### 7.3 Judging

For each group, send `JUDGE_MODEL` the transcript, the coaching text and the persona's
expectations, and request a structured verdict:

- did the avatar do each `avatar_pass` behavior
- did the avatar trip any `avatar_fail` behavior
- did the reported score land inside `score_band`
- did the coaching meet `coaching_expect`

Each answer carries a quoted line from the transcript as evidence. No `temperature` is
sent (see Part 2).

### 7.4 Output

A second sheet in the existing xlsx: Avatar, Round, Persona, Expected Band,
Actual Score, Verdict, Failed Checks, Quoted Evidence.

---

## 8. Acceptance criteria

1. `python core/check_personas.py` passes with the new Gladys file.
2. `avatars/gladys/personas.py` exposes `PERSONAS` keyed exactly `"Gladys"`, matching `config/settings.py`.
3. A learner call on `gpt-6-luna` succeeds (no HTTP 400 from `temperature`).
4. The avatar request carries `model: "gpt-5.4-mini"`.
5. A judge run produces one verdict row per `(Avatar, Round, Persona)` group.
6. No other avatar's behavior changes.

## 8b. Scoring scale (decided 2026-11-16, after the portal was inspected)

The introduction file specified 25 points per category for a total of 100. A survey of
the 16 existing avatar files showed that is not what this lab does:

| Avatar | Categories | Scale | Total |
|---|---|---|---|
| maya, madison, Carol, Jim, JordanCC, Michael | 3 | 10 each | 30 |
| Gladys V2.7 (archived) | 3 | 10 each | 30 |
| Benton | 4 | met/not-met 3/4/4/3 | 14 |
| Tony | 3 | descriptive (Excellent/Good/Fair) | n/a |

Ten points per category is the house convention; Benton and Tony are the exceptions.
Gladys V2 therefore uses 10 per category across four categories for a total of 40.
Sub-measures, both hard limits and all eleven persona bands were rescaled to match.

This matters at the portal: the QA Lab's "out of N" on the Personas tab is taken from the
situation's scoring table total, which is why Benton's personas read "out of 14". A
`Gladys - Test` situation with no scoring table yet shows the default "out of 10", so the
scoring table must be entered before any persona band is typed.

## 9. Risks and open items

- **Expected bands are untested predictions.** They are computed from the Points Table,
  not observed. The first `standard` run at 4 rounds is a calibration run; bands get
  corrected from the results.
- **Probe - Recoverer has no expected outcome by design.** It exists to resolve the
  Points Table / Condition 6 contradiction.
- **Judge quality depends on how `EXPECTATIONS` is written.** Only Gladys is written to
  the tighter machine-read standard in this round; other avatars' prose entries will
  judge less reliably until rewritten.
- **`config/settings.py` holds a live bearer token and the repo is not under git.** Nothing in
  this work changes that, but it is worth noting that the token at `config/settings.py` line 43
  is committed in plaintext to a shared folder.
