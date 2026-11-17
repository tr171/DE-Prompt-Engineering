# Better Path AI — QA Automation

Automated QA for Better Path AI's coaching avatars. Instead of launching an
avatar and talking to it by voice, two AI pieces drive the conversation: OpenAI
plays the learner, and Better Path AI's own chat API plays the avatar. Every
conversation is saved to Excel, then checked — either by a deterministic
analyzer or by a judge model — against what the avatar's rubric says should
have happened.

**New here?** Read [GUIDE.md](GUIDE.md). It covers setup end to end.

## Setup

```bash
pip install -r requirements.txt
cp config/settings.example.py config/settings.py    # add your Better Path AI token + user id
cp .env.example .env              # add your own OpenAI key
python core/test_openai_connection.py  # should print SUCCESS
python core/check_personas.py          # should print 0 error(s)
```

`config/settings.py` and `.env` hold live credentials and are gitignored on purpose.
Never commit them, never email them — get your own.

## Running

```bash
python core/run_qa_tests.py                               # pick an avatar, pick rounds
python core/analyze_run.py  bpai_qa_results_<avatar>_*.xlsx   # deterministic checks, free
python core/judge.py        bpai_qa_results_<avatar>_*.xlsx   # AI verdicts, costs money
```

`core/analyze_run.py` also reads the QA Lab's own "Download Excel" export, so a
portal run can be analysed the same way.

Output lands in the repo root and is gitignored there. **To keep a result, move
it into `avatars/<name>/runs/`** — filing it is what makes it tracked.

## Layout

```
config/settings.example.py  .env.example   copy these to config/settings.py / .env
personas.py                       loads the avatars; shared settings
core/                             the shared engine
avatars/<name>/                   everything about one avatar:
    personas.py                     its learner personas + expectations
    prompts/ runs/ docs/ tools/     added as work on it starts
docs/                             cross-avatar notes and design specs
```

| Path | What it is |
|---|---|
| `core/run_qa_tests.py` | the runner — this is the one you run |
| `core/learner_ai.py` | asks OpenAI for each learner line |
| `core/judge.py` | grades a finished run against `EXPECTATIONS` |
| `core/analyze_run.py` | deterministic checks, no API calls, free |
| `core/check_personas.py` | validates every persona file before a run |
| `core/export_portal_personas.py` | turns a persona file into paste-ready portal fields |
| `core/probe_after_mode.py` | diagnostic: which avatar fields the platform uses after coaching |
| `core/test_openai_connection.py` | confirms your OpenAI key works |
| `personas.py` | combines the avatars' persona files; holds shared settings |
| `avatars/<name>/personas.py` | that avatar's learner personas and expectations |
| `avatars/<name>/tools/` | scripts that only make sense for that avatar |
| `docs/` | cross-avatar notes and design specs |

**Run every command from the repo root**, giving the full path —
`python core/run_qa_tests.py`, not `cd core && python run_qa_tests.py`.
Each script puts the repo root on its own import path, so `config/settings.py` and
`personas.py` resolve from wherever it sits.

Shared settings — rounds, turn caps, the `"Please coach me"` trigger — live at
the bottom of [personas.py](personas.py).

To add an avatar: copy the `avatars/_TEMPLATE/` folder, rename it to the avatar's
name in lower case, and fill in its `personas.py`. It's picked up automatically —
a folder starting with `_` is skipped, which is what keeps the template out.

## Avatar roster

All 16 avatars are runnable now — every one has personas and a `config/settings.py` entry.
The folders listed under *Also has* are the ones with prompt or QA work done so far.

| Folder | Avatar name in `config/settings.py` | Personas | Also has |
|---|---|---:|---|
| [`benton/`](avatars/benton/) | Benton | 4 | `archive/`, `prompts/`, `runs/`, `tests/`, `tools/` |
| [`carol/`](avatars/carol/) | Carol | 4 | — personas only, no QA work yet |
| [`elaine/`](avatars/elaine/) | Elaine | 4 | `docs/`, `prompts/`, `runs/`, `tools/` |
| [`gladys/`](avatars/gladys/) | Gladys | 4 | `archive/`, `docs/`, `runs/`, `settings/` |
| [`jd_med/`](avatars/jd_med/) | JD_Med | 4 | — personas only, no QA work yet |
| [`jdmeal/`](avatars/jdmeal/) | JDMeal | 4 | — personas only, no QA work yet |
| [`jim/`](avatars/jim/) | Jim | 4 | — personas only, no QA work yet |
| [`john/`](avatars/john/) | John | 10 | `runs/` |
| [`jordancc/`](avatars/jordancc/) | JordanCC | 4 | — personas only, no QA work yet |
| [`jordandiff/`](avatars/jordandiff/) | JordanDiff | 4 | — personas only, no QA work yet |
| [`madison/`](avatars/madison/) | Madison - Behavioral Health - Moderate | 4 | — personas only, no QA work yet |
| [`marcus/`](avatars/marcus/) | Marcus | 4 | `docs/`, `prompts/`, `runs/`, `tools/` |
| [`maya/`](avatars/maya/) | Maya - Behavioral Health - Moderate | 4 | — personas only, no QA work yet |
| [`michael/`](avatars/michael/) | Michael | 4 | — personas only, no QA work yet |
| [`ross/`](avatars/ross/) | Ross | 4 | — personas only, no QA work yet |
| [`tony/`](avatars/tony/) | Tony | 4 | — personas only, no QA work yet |

## Where the QA work is

Five avatars have had prompt or QA work done on them so far. Each folder
follows the same shape: `personas.py`, then `prompts/` (what gets pasted into
the portal), `runs/` (results and transcripts), `docs/` (findings), plus
`settings/`, `tests/`, `tools/` or `archive/` where they apply.

### [Gladys](avatars/gladys/) — Alzheimer's senior care, new caregiver intro

The most developed. Scores 10 per category across four categories (Empathy,
Communication, CARES Method, Objective) for 40.

- [docs/HANDOFF.md](avatars/gladys/docs/HANDOFF.md) — **start here**: setup,
  scoring bands, and the two defects found
- [settings/Avatar_Settings.md](avatars/gladys/settings/Avatar_Settings.md) —
  every portal field, paste-ready
- [settings/PORTAL_PERSONAS.md](avatars/gladys/settings/PORTAL_PERSONAS.md) —
  all 11 personas with every QA Lab field filled in (generated, not hand-written:
  `python core/export_portal_personas.py Gladys --out avatars/gladys/settings/PORTAL_PERSONAS.md`)

Open: the coach credits statements of intent ("I'll stop by again soon") as
return requests, so Trap Test beats its band. Three prompt wordings have failed
to fix it — likely needs engineering, not wording.

### [Elaine](avatars/elaine/) — V2 scoring anchors

Scoring here is a lookup, not a judgement: three items per category, each
landing Did / Partly / Missed, and a points table turns that triple into a
number. So a conversation can be built to land on a chosen score, and anything
else is a scoring error.

- [docs/FINDINGS.md](avatars/elaine/docs/FINDINGS.md) — the V2 findings
- [docs/EVIDENCE.md](avatars/elaine/docs/EVIDENCE.md) — what backs each claim
- [docs/MANAGER_NOTE.md](avatars/elaine/docs/MANAGER_NOTE.md) — the summary written for review

```bash
python avatars/elaine/tools/local_sim.py     avatars/elaine/prompts/portal_v1.txt   # iterate offline
python avatars/elaine/tools/run_anchors.py                                          # 15 anchors, live
python avatars/elaine/tools/analyze_portal.py avatars/elaine/runs/portal_run_31.xlsx
python avatars/elaine/tools/export_chats.py elaine_anchors_<timestamp>.xlsx  # readable chat log
```

### [Benton](avatars/benton/) — fixed-line band tests

Six manual band tests run as fixed scripts, so every run tests exactly the same
thing. [prompts/portal_FINAL.txt](avatars/benton/prompts/portal_FINAL.txt) is
the shipped prompt; `working.txt` and `v6`/`v7` are the trail behind it.

```bash
python avatars/benton/tools/local_sim.py       avatars/benton/prompts/portal_FINAL.txt   # offline
python avatars/benton/tools/band_scripts.py                                          # live, all six
```

### [Marcus](avatars/marcus/) — wellness check, scoring anchors

The rubric is three sub-items per category plus a stack of ceilings and floors.
The ceilings are deterministic, so each anchor is a fixed officer script built
so only one band of scores is defensible.

- [docs/FINDINGS.md](avatars/marcus/docs/FINDINGS.md) — the v1 prompt test

```bash
python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt            # all 11 anchors
python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt --rounds 3
python avatars/marcus/tools/local_sim.py avatars/marcus/prompts/portal_v1.txt NULL NO-ASK
```

### [John](avatars/john/) — one archived run

A single October run, kept for reference. No prompt work yet.

## A few things that cost us runs

1. The Evaluation Format, the scoring table and the persona bands must all use
   the same scale. A mismatch makes the portal report "No score" for every round.
2. Enter the scoring table *before* the persona bands — the "out of N" on the
   Personas tab comes from the table's total.
3. Check the avatar's opening line before trusting any run. One run was wasted
   testing Benton by mistake.
