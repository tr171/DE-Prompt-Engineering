# Gladys V2 QA — handoff

Everything needed to run the Gladys V2 test battery yourself, and what it has
found so far. Written 2026-11-16.

## Setting up (10 minutes)

1. `pip install -r requirements.txt`
2. Copy `config/settings.example.py` to `config/settings.py`, then fill in two things:
   - `HEADERS["authorization"]` — your own BetterPath AI token (GUIDE.md Step 4)
   - `USER_ID` — the numeric user id that token belongs to
3. Copy `.env.example` to `.env` and paste your own OpenAI key (GUIDE.md Step 5)
4. `python core/test_openai_connection.py` — should print SUCCESS
5. `python core/check_personas.py` — should print `0 error(s)`

`config/settings.py` and `.env` are gitignored on purpose. They hold live credentials:
never commit them, never email them, get your own.

## Running

```
python core/run_qa_tests.py                              # pick Gladys, pick rounds
python core/analyze_run.py bpai_qa_results_Gladys_*.xlsx # what went wrong, free
python core/judge.py bpai_qa_results_Gladys_*.xlsx       # AI verdicts, costs money
```

GUIDE.md Steps 7–10 cover all of this in detail.

`core/analyze_run.py` also reads the QA Lab's own "Download Excel" export, so a
portal run can be analysed the same way.

## The model setup

Three slots in `config/settings.py`, mirroring the QA Lab UI:

| Slot | Value | Role |
|---|---|---|
| `AVATAR_MODEL` | gpt-5.4-mini | plays Gladys |
| `USER_MODEL` | gpt-6-luna | plays each test persona |
| `JUDGE_MODEL` | gpt-6-luna | grades conversations against EXPECTATIONS |

`USER_TEMPERATURE` must stay `None` while the user model is gpt-6-luna: that
model rejects any explicit temperature with an HTTP 400.

## Scoring

Gladys scores 10 per category across four categories, total 40 — matching the
house convention used by maya, madison, Carol, Jim, JordanCC and Michael.

| Persona | Expected /40 |
|---|---|
| High Learner | 34–40 |
| Medium Learner | 20–28 |
| Low Learner | 0–14 |
| Trap Test | 28–33, must not reach 34 |

These are calibrated from four runs but are not yet a settled baseline — see
"Open" below.

## What the testing has found

**1. The coach credits non-asks as return requests.** Trap Test never asks to
come back; that is its entire purpose. It has scored 39/40 and 37/40 against an
expected 28–33, beating High Learner in one run. Two distinct mechanisms:

- *Misattribution* — the coach quoted Gladys's own words ("Can you come back and
  visit me again on Thursday?") as evidence the learner asked. **Fixed** by a new
  avatar condition barring Gladys from inviting herself back. Went from 4
  occurrences per run to 0.
- *Statement-as-ask* — the coach credits "I'll stop by again soon" as asking,
  despite the scoring table saying verbatim that a statement of intent does not
  count, and naming almost that exact phrase. **Not fixed.** Three increasingly
  explicit wordings have been ignored.

The pattern: the coach follows rules about verifiable facts (who spoke) and
overrides rules that require a judgement call (statement vs question). This one
likely needs engineering, not prompt wording.

**2. The coach occasionally fabricates quotes.** It has attributed lines to the
learner that appear nowhere in the conversation, against an explicit instruction
not to invent anything. Rare but real. `core/analyze_run.py` check 5 detects both
this and misattribution automatically.

## Portal setup

`avatars/gladys/settings/` holds everything needed to configure the avatar:

- `Gladys_Avatar_Settings.md` — every field, paste-ready
- `PORTAL_CHANGES.md` — just the fixes, with the reasoning for each
- `PORTAL_PERSONAS.md` — all 11 personas with every QA Lab field filled in

`PORTAL_PERSONAS.md` is generated, not hand-written:

```
python core/export_portal_personas.py Gladys --out avatars/gladys/settings/PORTAL_PERSONAS.md
```

Three things that cost us several wasted runs, worth knowing:

1. The Evaluation Format, the scoring table and the persona bands must all use
   the same scale. A mismatch makes the portal report "No score" for every round.
2. Enter the scoring table before the persona bands — the "out of N" on the
   Personas tab comes from the table's total.
3. Check the avatar's opening line before trusting any run. It must be
   "Oh, I wasn't expecting you." One run was wasted testing Benton by mistake.

## Open

- **Trap and Low bands are not final.** Both sit above their bands only because
  Objective is over-credited. They were deliberately NOT widened to fit — that
  would hide the defect. Recalibrate once the crediting is fixed.
- **Only the standard four personas are in the portal.** Seven probes are written
  and ready in `PORTAL_PERSONAS.md`. `Probe - Recoverer` is the most valuable: it
  is the only test of whether an empathetic repair lifts the Empathy hard cap.
- **The other 15 avatars have prose EXPECTATIONS**, which the judge handles
  poorly. Only Gladys is written to the machine-readable standard so far.
