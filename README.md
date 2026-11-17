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
cp config.example.py config.py    # add your Better Path AI token + user id
cp .env.example .env              # add your own OpenAI key
python test_openai_connection.py  # should print SUCCESS
python check_personas.py          # should print 0 error(s)
```

`config.py` and `.env` hold live credentials and are gitignored on purpose.
Never commit them, never email them — get your own.

## Running

```bash
python run_qa_tests.py                               # pick an avatar, pick rounds
python analyze_run.py  bpai_qa_results_<avatar>_*.xlsx   # deterministic checks, free
python judge.py        bpai_qa_results_<avatar>_*.xlsx   # AI verdicts, costs money
```

`analyze_run.py` also reads the QA Lab's own "Download Excel" export, so a
portal run can be analysed the same way.

Output lands in the repo root and is gitignored there. **To keep a result, move
it into `avatars/<name>/runs/`** — filing it is what makes it tracked.

## Layout

| Path | What it is |
|---|---|
| `run_qa_tests.py` | the runner — this is the one you run |
| `learner_ai.py` | asks OpenAI for each learner line |
| `judge.py` | grades a finished run against `EXPECTATIONS` |
| `analyze_run.py` | deterministic checks, no API calls, free |
| `check_personas.py` | validates every persona file before a run |
| `personas/` | one file per avatar — the personas and expectations |
| `avatars/` | per-avatar prompts, results and findings (below) |
| `docs/` | cross-avatar notes and design specs |

Shared settings — rounds, turn caps, the `"Please coach me"` trigger — live at
the bottom of [personas/__init__.py](personas/__init__.py).

To add an avatar: copy `personas/_TEMPLATE.py`, rename it, fill it in. It's
picked up automatically.

## Avatars

Each avatar folder follows the same shape: `prompts/` (what gets pasted into
the portal), `runs/` (results and transcripts), `docs/` (findings), plus
`settings/`, `tests/` or `archive/` where they apply.

### [Gladys](avatars/gladys/) — Alzheimer's senior care, new caregiver intro

The most developed. Scores 10 per category across four categories (Empathy,
Communication, CARES Method, Objective) for 40.

- [docs/HANDOFF.md](avatars/gladys/docs/HANDOFF.md) — **start here**: setup,
  scoring bands, and the two defects found
- [settings/Avatar_Settings.md](avatars/gladys/settings/Avatar_Settings.md) —
  every portal field, paste-ready
- [settings/PORTAL_PERSONAS.md](avatars/gladys/settings/PORTAL_PERSONAS.md) —
  all 11 personas with every QA Lab field filled in (generated, not hand-written:
  `python export_portal_personas.py Gladys --out avatars/gladys/settings/PORTAL_PERSONAS.md`)

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
python elaine_local_sim.py     avatars/elaine/prompts/portal_v1.txt   # iterate offline
python run_elaine_anchors.py                                          # 15 anchors, live
python analyze_elaine_portal.py avatars/elaine/runs/portal_run_31.xlsx
```

### [Benton](avatars/benton/) — fixed-line band tests

Six manual band tests run as fixed scripts, so every run tests exactly the same
thing. [prompts/portal_FINAL.txt](avatars/benton/prompts/portal_FINAL.txt) is
the shipped prompt; `working.txt` and `v6`/`v7` are the trail behind it.

```bash
python local_sim.py       avatars/benton/prompts/portal_FINAL.txt   # offline
python run_band_scripts.py                                          # live, all six
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
