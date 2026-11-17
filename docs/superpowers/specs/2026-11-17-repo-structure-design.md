# Repo structure — avatar-based reorganization

Design agreed 2026-11-17, before the first git commit. This doubles as the
migration manifest: every file that moved is listed, so a reference that breaks
later can be traced back to its original name.

## The problem

72 entries at the repo root. Three avatars' worth of prompts, transcripts,
results and findings sat in the same flat namespace as the shared test engine,
distinguishable only by filename prefix. Nothing had been committed yet.

## The shape

Three groups, separated by what changes them:

- **Shared engine** — `run_qa_tests.py`, `learner_ai.py`, `judge.py`,
  `analyze_run.py`, `check_personas.py`, `export_portal_personas.py`,
  `probe_after_mode.py`, `test_openai_connection.py`. Changed when the test
  harness changes. Stays at root.
- **Avatar definitions** — `personas/`, an auto-loading package keyed by avatar
  name. Already correctly organized; untouched.
- **Avatar material** — prompts, run output, findings. Changed when one avatar
  is being worked on. Moves to `avatars/<name>/`.

### Why the Python files stay flat

The import graph is flat and interdependent: `analyze_elaine_portal.py` imports
from `elaine_local_sim.py`, which imports from `config.py` and
`elaine_band_scripts.py`; `run_band_scripts.py` and `run_elaine_anchors.py`
both import from `run_qa_tests.py`. Moving the avatar-specific scripts into
`avatars/<name>/` breaks all of that unless each one gets a `sys.path`
bootstrap, and every command in GUIDE.md and HANDOFF.md changes with it.

The content files carry no such coupling — the avatar tooling takes its input
path as an argument. So the content moves and the code does not. This is the
cheap 80%: it clears ~50 files off the root with zero risk to working code.

Revisit if the root becomes unmanageable again; the next step would be a
`core/` package with `python -m` invocation, not a `sys.path` hack.

### Why run output is committed

`EVIDENCE.md`, `FINDINGS.md` and `ANCHOR_RESULTS.md` all cite specific result
files as the basis for their claims. A reader who cannot open those files
cannot check the findings. So the `.xlsx` results, the portal PDFs and the
anchor chat logs are tracked.

The raw `sim_*.txt` dumps (~820 KB) and the nine superseded Benton
`prompt_iter*.txt` drafts are not: nothing references them and they are
reproducible by re-running.

### Ignore rules are root-scoped

The tools write their output to the working directory, which is the repo root.
So the ignore patterns are anchored there (`/bpai_qa_results_*.xlsx`, not
`*.xlsx`). Fresh output never dirties the tree; anything deliberately filed
into `avatars/<name>/runs/` is tracked. Curation is the act of moving a file.

## File mapping

### Root → `avatars/benton/`

| From | To |
|---|---|
| `Benton_portal_prompt_FINAL.txt` | `prompts/portal_FINAL.txt` |
| `Benton_portal_prompt_v7.txt` | `prompts/portal_v7.txt` |
| `Benton_portal_prompt_v6.txt` | `prompts/portal_v6.txt` |
| `Benton_prompt_working.txt` | `prompts/working.txt` |
| `prompt_iter{1_v7,3..9}.txt` | `prompts/iterations/` (8, untracked) |
| `Benton_manual_band_tests.txt` | `tests/manual_band_tests.txt` |
| `bpai_qa_results_Benton_20261104_195037.xlsx` | `runs/qa_20261104_195037.xlsx` |
| `bpai_qa_results_Benton_20261105_144324.xlsx` | `runs/qa_20261105_144324.xlsx` |
| `bpai_qa_results_Benton_20261104_194733_PARTIAL.xlsx` | `runs/qa_20261104_194733_PARTIAL.xlsx` |
| `bpai_qa_results_Benton_20261104_194856_PARTIAL.xlsx` | `runs/qa_20261104_194856_PARTIAL.xlsx` |
| `local_sim_20261105_*.txt` | `runs/sim_20261105_*.txt` (10, untracked) |
| `prompt_backups/agent194_backup_20261105_172513.json` | `archive/agent194_backup_20261105.json` |

Agent 194 is Benton (`config.py` SCENARIOS: scenario 198 / agent 194).

### Root + `elaine_avatar_test/` → `avatars/elaine/`

| From | To |
|---|---|
| `Elaine_portal_prompt_v1.txt` | `prompts/portal_v1.txt` |
| `Elaine_portal_prompt_v1_noFormatDupe.txt` | `prompts/portal_v1_noFormatDupe.txt` |
| `ELAINE_V2_FINDINGS.md` | `docs/FINDINGS.md` |
| `ELAINE_EVIDENCE.md` | `docs/EVIDENCE.md` |
| `ELAINE_MANAGER_NOTE.md` | `docs/MANAGER_NOTE.md` |
| `ELAINE_BAND_TESTS.md` | `docs/BAND_TESTS.md` |
| `ELAINE_ANCHOR_RESULTS.md` | `docs/ANCHOR_RESULTS.md` |
| `elaine_avatar_test/portal_run/RESULTS_NOTE.md` | `docs/PORTAL_RESULTS_NOTE.md` |
| `elaine_all_15_run.xlsx` | `runs/anchors_20261116.xlsx` |
| `elaine_anchors_20261116_210408_chats.md` | `runs/anchors_20261116_chats.md` |
| `elaine_avatar_test/qa_run_31.xlsx` | `runs/portal_run_31.xlsx` |
| `elaine_avatar_test/portal_run/situation_*.pdf` | `runs/portal/` (3) |
| `elaine_sim_20261116_*.txt` | `runs/sim_20261116_*.txt` (3, untracked) |

### `gladys_avatar_settings/` + root → `avatars/gladys/`

| From | To |
|---|---|
| `Gladys_Avatar_Settings.md` | `settings/Avatar_Settings.md` |
| `PORTAL_CHANGES.md` | `settings/PORTAL_CHANGES.md` |
| `PORTAL_PERSONAS.md` | `settings/PORTAL_PERSONAS.md` |
| `HANDOFF.md` (root) | `docs/HANDOFF.md` |
| `bpai_qa_results_Gladys_20261116_155559.xlsx` | `runs/qa_20261116_155559.xlsx` |
| `bpai_qa_results_Gladys_20261116_162652.xlsx` | `runs/qa_20261116_162652.xlsx` |
| `bpai_qa_results_Gladys_TRAPCHECK_20261116_165539.xlsx` | `runs/qa_TRAPCHECK_20261116_165539.xlsx` |
| `qa_run_{27,28,29}.xlsx` | `runs/portal_run_{27,28,29}.xlsx` |
| `prompt_backups/Gladys_v2.7_archived.py` | `archive/personas_v2.7.py` |

`HANDOFF.md` is Gladys-specific throughout — setup steps, the model table, the
scoring bands, the two defects found, the portal notes. It moves with the avatar.

`gladys_avatar_settings.zip` is a redundant bundle of the same folder and is
left untracked.

### Root → `avatars/john/`

| From | To |
|---|---|
| `bpai_qa_results_John_20261029_143458.xlsx` | `runs/qa_20261029_143458.xlsx` |

### Root → `docs/`

`BATCH1_CHANGES.md` documents a consistency pass across every persona file and
the runner, not Benton's work. It is project-level.

### Removed after emptying

`elaine_avatar_test/`, `gladys_avatar_settings/`, `prompt_backups/`.

## Reference pass

`EVIDENCE.md` cited `elaine_anchors_20261116_210408.xlsx`, which does not exist
on disk — the file is `elaine_all_15_run.xlsx`. Corrected to the new path as
part of the move.

Roughly a dozen other filename references across the findings docs, `HANDOFF.md`
and `GUIDE.md` are repointed at their new paths.

## Secrets

`config.py` holds a live BetterPath AI bearer token; `.env` holds a live OpenAI
key. Both are ignored, and `git status` is checked for them before the first
commit. `config.example.py` and `.env.example` were verified to contain
placeholders only.

## Not doing

- `src/` layout or an installable package — nothing depends on it.
- Avatar folders for the 12 personas with no material of their own.
- Rewriting the import graph.
