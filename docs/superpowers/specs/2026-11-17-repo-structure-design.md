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

### Why the Python files stayed flat (first pass - superseded, see Revision below)

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

## Revision, same day: the Python moved too

The first pass left 22 files at the root, 16 of them Python. The avatar tooling
sitting outside the avatar folders was the part that still read wrong, so the
move was extended.

### Layout

- `core/` — the eight shared engine scripts.
- `avatars/<name>/tools/` — the scripts that only make sense for one avatar.
- Root keeps six files: `README.md`, `GUIDE.md`, `requirements.txt`,
  `.gitignore`, `config.example.py`, `.env.example` — plus the gitignored
  `config.py`. These stay because tools and people expect them there:
  `pip install -r requirements.txt` runs from the root, and `config.example.py`
  has to sit where `config.py` must go. `config.py` also resolves `.env`
  relative to its own `__file__`, so it cannot move without breaking that.

### Renames

| From | To |
|---|---|
| `run_band_scripts.py` | `avatars/benton/tools/band_scripts.py` |
| `local_sim.py` | `avatars/benton/tools/local_sim.py` |
| `elaine_local_sim.py` | `avatars/elaine/tools/local_sim.py` |
| `elaine_band_scripts.py` | `avatars/elaine/tools/band_scripts.py` |
| `elaine_anchor_scripts.py` | `avatars/elaine/tools/anchor_scripts.py` |
| `run_elaine_anchors.py` | `avatars/elaine/tools/run_anchors.py` |
| `analyze_elaine_portal.py` | `avatars/elaine/tools/analyze_portal.py` |
| `export_anchor_chats.py` | `avatars/elaine/tools/export_chats.py` |

Benton and Elaine now both have a `local_sim.py` and a `band_scripts.py`. They
do not collide: `python <path>` puts only the script's own directory on
`sys.path`, so a sibling import resolves within that avatar's folder.

### How the imports still work

`python core/judge.py` puts `core/` on `sys.path`, not the repo root, so
`from config import ...` and `from personas import ...` would fail. Each moved
script that has an internal import therefore carries a bootstrap, inserted
after its docstring:

```python
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
```

Avatar tools use `parents[3]` and add `core/` as well, since they import from
the engine. With the root and `core/` on the path, every existing flat import
(`from config import`, `from personas import`, `from run_qa_tests import`)
keeps working unchanged. The only import statements edited were the four
pointing at renamed sibling modules.

The first pass called this a "hack" and argued against it. That judgement was
about cost, not correctness: it was not worth 13 edited files to tidy a root
nobody minded. Once the tidier root became the goal, the bootstrap is the
standard way to get it, and the cost is five lines per script.

The alternative — making `core` a package and invoking `python -m core.judge` —
avoids the path insert, but then `run_qa_tests` is imported as `core.run_qa_tests`
and its own `from learner_ai import ...` breaks, so every internal import across
the engine would have to be rewritten too. More churn for a less readable command.

### Cost

Every command in `GUIDE.md`, `README.md`, `HANDOFF.md` and the findings docs
gained a path prefix — 106 lines across 23 files, plus the in-script usage
docstrings. Scripts must now be run from the repo root. This is stated at the
top of the Layout section in `README.md` and in Step 1 of `GUIDE.md`.

### Verified

All 16 entry points resolve their imports when invoked as `python <path>`;
`core/check_personas.py` reports 0 errors; and `core/analyze_run.py` run against
`avatars/gladys/runs/qa_20261116_162652.xlsx` produces its full five-check
report, still catching the known Trap Test defect (39/40 against a 28-33 band).

## Second revision: persona files moved into the avatar folders

After the engine move, `avatars/` held four folders while `config.py` listed
sixteen avatars. The twelve without folders had persona files but no QA
material, so the structure was accurate — but it read as though only four
avatars existed, and there was nowhere obvious to start work on the rest.

Creating twelve empty folders would not have survived a push: git does not
track empty directories. The fix instead was to give every avatar folder real
content by moving its persona file in:

    personas/Tony.py   ->  avatars/tony/personas.py
    personas/Gladys.py ->  avatars/gladys/personas.py
    personas/_TEMPLATE.py -> avatars/_TEMPLATE/personas.py
    ... 16 in all

Now `avatars/` lists every avatar in `config.py`, each folder is tracked
because it contains a real file, and everything about one avatar — personas,
prompts, runs, findings, tools — sits in one place.

### The loader

`personas/__init__.py` became `personas.py` at the repo root. It scans
`avatars/*/personas.py` and loads each one under a unique module name
(`_avatar_personas_<folder>`) via `importlib.util.spec_from_file_location`.
The unique name matters: all sixteen files are called `personas.py`, so
importing them under their own name would make them overwrite each other and
collide with the loader itself.

It keeps the same public API — `PERSONAS`, `EXPECTATIONS`, `ROUNDS`,
`MAX_TURNS_BEFORE_COACHING`, `MAX_MENTORING_TURNS`, `COACHING_REQUEST_MESSAGE`,
`MENTORING_FOLLOWUP_PROMPT` — so `core/run_qa_tests.py`, `core/judge.py` and
`core/analyze_run.py` needed no changes at all.

It lives at the repo root rather than in `core/` because it holds the shared
settings people actually edit (`ROUNDS` and the turn caps). `core/` reads as
"the engine, don't touch", which is the wrong signal for a file with tunable
settings in it.

Two scripts walked the old package with `pkgutil.iter_modules` and had to be
reworked: `core/check_personas.py` and `core/export_portal_personas.py`. The
loader now exposes `MODULES` (folder name -> module), `load(name)` for
case-insensitive lookup and `path_for(folder)` for messages, so neither script
needs to know how avatars are stored.

### Naming

The folder name is not authoritative. The avatar name that must match
`config.py` is the key of the `PERSONAS` dict inside the file, which is why
`avatars/maya/personas.py` holds "Maya - Behavioral Health - Moderate". A
folder whose name starts with `_` is skipped, which is what keeps
`avatars/_TEMPLATE/` from being treated as a real avatar.

### Verified

The loader finds all 16 avatars, 16 EXPECTATIONS and 16 modules;
`core/check_personas.py` reports 0 errors across all 16 and still produces its
two pre-existing warnings (John's `RUN_SET` left on "v22", JordanDiff's Medium
Learner wording); single-avatar and bad-name lookups behave correctly;
`core/export_portal_personas.py Gladys` regenerates `PORTAL_PERSONAS.md`
byte-identically apart from the source-path line in its header; and
`core/analyze_run.py` runs end to end, which exercises `EXPECTATIONS` loading.

## Third revision: config moved into a folder

`config.py` and `config.example.py` became a package:

    config/__init__.py            tracked - a shim, re-exports everything
    config/settings.example.py    tracked - the template
    config/settings.py            GITIGNORED - the real token and user id

`from config import SCENARIOS, HEADERS, USER_ID` still works unchanged across
all 17 entry points, because `config` is now a package whose `__init__.py` does
`from .settings import *`. Nothing that imports config needed editing.

### Why a shim rather than putting the settings in `__init__.py`

Two reasons. "Copy `settings.example.py` to `settings.py`" is a clearer
instruction than "copy `example.py` to `__init__.py`". And the shim can catch
the missing-file case: if `config/settings.py` does not exist, the import
raises a `SystemExit` explaining exactly what to copy, instead of a bare
`ModuleNotFoundError`. The shim re-raises any other `ModuleNotFoundError`
untouched, so a genuine missing dependency inside settings.py is not masked.

### `.env` stayed at the repo root

It is the strongest convention there is for a dotenv file, editors and tools
look for it there, and moving it would mean every existing checkout has to
relocate a file holding a live key. `settings.py` now climbs one level out of
`config/` to find it:

    load_dotenv(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

Verified by a real OpenAI call: `python core/test_openai_connection.py` returns
SUCCESS, which only happens if the key was read from the root `.env`.

### .gitignore

`config.py` became `config/settings.py`. Checked after staging that
`config/settings.py`, `config/settings.py.bak` and `.env` are all untracked,
and that no live token or key appears anywhere in the staged tree.

### Verified end to end

`python core/run_qa_tests.py` reaches its avatar menu and lists all 16 avatars
- that exercises config loading, persona loading and the path bootstrap
together, and is the check that would have caught a path exception.
`python core/test_openai_connection.py` returns SUCCESS against the live API.
`core/check_personas.py` reports 0 errors, and `core/analyze_run.py` produces a
full report from a committed result file.
