# Better Path AI QA Automation — Setup & Run Guide

## What this does

Instead of launching each avatar and talking to it by voice, this tool has two AI pieces working together:

1. **OpenAI** plays the "learner" — on each turn, it reads the conversation so far and generates one statement, following behavior instructions you write (e.g. "You are an exceptional learner. Build trust. Explore the underlying concern...").
2. **Better Path AI's own chat API** plays the avatar — the same one the app itself uses, reached directly instead of through voice or clicking.

The two go back and forth automatically: learner AI speaks, avatar replies, learner AI reads that reply and speaks again — for as many rounds as you set, across as many personas as you've written prompts for — until the learner says **Please coach me** (each persona says when), the learner AI decides the scenario's objective has been reached, or the turn cap is hit. Everything gets saved to Excel — **one file per avatar**, named after that avatar.

Either way, the tool doesn't stop there — it mirrors what a real learner does next:
1. It sends **"Please coach me"** as the next message, the same trigger phrase that switches Better Path AI into coaching-feedback mode in the real app. This happens whether or not the objective was actually reached — a real learner can ask for coaching anytime they're stuck or think they're done, and that's deliberately part of what gets tested here too. It matters most for **Trap Test**: by design, it usually won't fully satisfy the objective, but it still needs to get scored so you can see whether the platform's scoring catches its deliberate gap.
2. It then has the learner AI ask a few genuine follow-up questions about that feedback (1–3, it decides when it's asked enough), so you can see how the avatar handles a real coaching back-and-forth too, not just the initial scenario.

We confirmed the avatar side works by testing it live against Madison - Behavioral Health together: it responded normally to typed text, in full context, with no voice involved.

This came with:
- `config.py` — your credentials and the list of avatars you're testing
- `personas/` — a **folder**, not a single file: one file per avatar (e.g. `Tony.py`, `Ross.py`), a blank `_TEMPLATE.py` for new avatars, and an `__init__.py` that combines them and holds a few settings shared across every avatar. See Step 6.
- `check_personas.py` — checks every avatar file for common mistakes before you run (Step 6)
- `probe_after_mode.py` — a diagnostic that shows which avatar fields the platform uses for follow-up questions (only when asked to run it)
- `learner_ai.py` — talks to OpenAI to generate each learner line
- `run_qa_tests.py` — the tool itself, run this to go
- `test_openai_connection.py` — a quick, standalone check that your OpenAI credentials work, before running the full tool
- `requirements.txt` — the two small libraries it needs

## Important: about your credentials

This tool needs two separate sets of credentials:

1. **Better Path AI** — proves to the avatar platform that it's you. Until engineering sets you up with a proper API/service credential, the workaround is: you copy your *own* already-logged-in session's credentials out of Chrome yourself.
2. **OpenAI** — lets the tool generate learner replies. You'll need an API key and a model name from whoever manages your org's OpenAI account.

I never see either of these — they stay in `config.py` on your computer. Treat that file like a password once it's filled in: don't email it, don't upload it to a shared drive, don't paste it into Slack/Teams, don't commit it anywhere.

## Step 0: Check Python is installed

1. Open Command Prompt (press the Windows key, type `cmd`, hit Enter).
2. Type `python --version` and press Enter.
3. If you see something like `Python 3.11.4`, you're set — skip to Step 1.
4. If you get an error like "not recognized," go to [python.org/downloads](https://python.org/downloads), download the latest installer, and run it. **Check the box that says "Add python.exe to PATH"** before clicking Install — easy to miss, and causes problems later if skipped. Reopen Command Prompt afterward and try `python --version` again.

## Step 1: Save the files

Create a folder somewhere easy to find, for example:

```
C:\Users\<you>\Documents\bpai-qa-automation
```

Unzip the download into that folder. You should end up with this layout — note that `personas` is a real subfolder, with its own files inside it:

```
bpai-qa-automation\
    config.py
    learner_ai.py
    run_qa_tests.py
    check_personas.py
    probe_after_mode.py
    test_openai_connection.py
    requirements.txt
    GUIDE.md
    personas\
        __init__.py
        _TEMPLATE.py
        Elaine.py
        Gladys.py
        ... one file per avatar
```

`config.py` isn't in the download. It holds your credentials, so keep your own copy and never replace it with anything sent to you.

**A note on file names:** the code files in this download are named `.txt` instead of `.py` (e.g. `run_qa_tests.txt`, and inside the `personas` subfolder `__init__.txt`, `Tony.txt`, and so on). That's deliberate: a lot of corporate security software blocks `.py` files from being downloaded or emailed at all. You need to rename them back before they'll work. Open Command Prompt, `cd` into your folder, and run these lines:

```
ren learner_ai.txt learner_ai.py
ren run_qa_tests.txt run_qa_tests.py
ren check_personas.txt check_personas.py
ren probe_after_mode.txt probe_after_mode.py
ren test_openai_connection.txt test_openai_connection.py
for %f in (personas\*.txt) do ren "%f" "%~nf.py"
```

The last line renames every `.txt` file inside the `personas` folder to `.py` in one go.

Leave `requirements.txt` and `GUIDE.md` exactly as they are — those are supposed to end that way. Run `dir` and `dir personas` afterward to confirm everything now shows `.py` endings.

**To open a `.py` file and look at or edit it:** right-click it and choose **Open with > Notepad** (or Notepad++/VS Code if you have one). Don't double-click it — on a Windows machine with Python installed, double-clicking tries to *run* the script instead of opening it for editing, which will just flash a black window and close. You'll actually run the tool later, in Step 7, from Command Prompt — not by double-clicking.

## Step 2: Install the two libraries the script needs

1. Open Command Prompt.
2. Move into your folder (adjust the path to match yours):
   ```
   cd C:\Users\<you>\Documents\bpai-qa-automation
   ```
3. Run:
   ```
   pip install -r requirements.txt
   ```
4. Wait for it to finish. A few lines of text will scroll by; as long as it doesn't end in a red error, you're good.

## Step 3: Find scenario_id and agent_id for each avatar you want to test

1. Log into Better Path AI in Chrome as usual.
2. Press `F12` (or right-click the page and choose "Inspect") to open DevTools, then click the **Network** tab along the top.
3. Click into the avatar/scenario you want to test (e.g. Madison), exactly like you normally would.
4. In the Network tab's request list, find one named **session** (type "session" into the filter box at the top of that list if it's hard to spot).
5. Click on it. Near the top of the panel that opens, you'll see the full **Request URL**, which looks like:
   ```
   https://de.better-path-ai.com/api/chat/session?user_id=114&scenario_id=77&agent_id=73
   ```
6. Note the numbers after `user_id=`, `scenario_id=`, and `agent_id=`.
7. Open `config.py`:
   - Set `USER_ID` to your `user_id` number (only need to do this once — it's the same for every avatar).
   - Add a line under `SCENARIOS` for this avatar with its `scenario_id` and `agent_id` (there's already a filled-in example for Madison to copy the pattern from).
8. Repeat steps 3–7 for every avatar situation you want to be able to test. You only need to do this once per avatar, ever — the IDs don't change.

## Step 4: Get your Better Path AI auth headers

1. Still in DevTools's Network tab, right-click that same **session** request (or any request starting with `/api/`) and choose **Copy > Copy as fetch**.
2. Open Notepad and paste what you copied. It'll look like a chunk of code starting with:
   ```
   fetch("https://de.better-path-ai.com/api/...", {
     ...
     headers: {
       ...
     },
     ...
   });
   ```
3. Find the part that reads `headers: { ... }` and copy everything **inside** those curly braces.
4. Open `config.py`, find the line `HEADERS = {` under the Better Path AI section, and paste what you copied between its curly braces, replacing the placeholder comment.
5. Save `config.py`.

You never need to identify which specific header is "the token" — copying the whole headers block grabs everything the API needs in one go.

**If you ever see a `401` error from `de.better-path-ai.com` when running the tool, it means this has expired — just repeat this step to grab a fresh copy.**

## Step 5: Get your OpenAI credentials

Ask whoever manages your org's OpenAI account for two things:
- An **API key**
- The **model name** you should use (e.g. `gpt-4o`)

This is native OpenAI, not Azure OpenAI — there's no separate "deployment name" to track down here, and no API version to worry about. The model name goes straight into each request.

Open `config.py` and fill in `OPENAI_API_KEY` and `OPENAI_MODEL` with what they give you. Leave `OPENAI_BASE_URL` as the default (`https://api.openai.com/v1`) unless your team specifically told you they route through their own gateway/proxy URL instead — if so, replace it with that URL.

**Before moving to Step 6, run the quick connection test:**
```
python test_openai_connection.py
```
This sends one trivial request and tells you immediately whether your key and model name work — a lot faster than finding out partway through a full run. It prints a clear explanation if something's wrong (wrong key, wrong model name, rate limited, etc.).

## Step 6: Persona files (one per avatar)

`personas` is a **folder** with one file per avatar — `Tony.py`, `Ross.py`, `Gladys.py`, and so on. Each file holds everything for that one avatar, and nothing you do in one file affects any other avatar or the rest of the tool.

As of October 13, 2026 **every avatar file uses the same layout.** `Tony.py` and `Ross.py` are the best worked examples, and `personas\_TEMPLATE.py` is a blank copy with notes on every part. (Its name starts with an underscore, so the tool skips it.)

### What's in an avatar file, top to bottom

1. **A header** — what the file covers, its version history, and a "Batch 2 to-do" list where work is still open.
2. **`RUN_SET`** — which personas run this time. Leave it as `"standard"` for the usual run. Other choices:
   - `"standard"` — High, Medium, Low, Trap Test (routine checks)
   - `"probes"` — every probe for that avatar (targeted checks, usually run once near the end)
   - `"all"` — everything
   - `"quick"` — the standard four plus the two or three riskiest probes (the tuning loop: run 2 rounds after each prompt change)
   - a list of names, e.g. `["Trap Test", "Probe - Null"]`

   **Set it back to `"standard"` when you're done,** so whoever runs the tool next gets the usual run.
3. **`SHARED_CONTEXT`** — what every learner knows about the scenario: the objective and the avatar's background, taken from the app's **Your Objective** and **Get to Know Your Avatar** tabs. **Never paste the rubric, "What you will be assessed on," best practices, or example lines here.** The learner AI reads them as instructions, so Medium, Low, and Trap drift toward the skills being scored. (Jim's Low learner scored 30/30 in September because of this.) That text goes in `REFERENCE_RUBRIC` at the bottom of the file instead.
4. **Shared lines** (`_SPOKEN`, `_COACH`, `_WHEN`, `_SCORED`, `_AFTER`) — rules every persona uses, written once:
   - `_COACH` and `_WHEN`: when the learner should ask for coaching, and that it must say exactly **Please coach me**. The tool catches that line and sends it the way the app does.
   - `_SCORED` and `_AFTER`: the follow-up questions only start once the coach has given scores, and the learner talks to the coach, not the avatar.
5. **`LIBRARY`** — every persona for this avatar:
   - **Standard four:** High Learner, Medium Learner, Low Learner, Trap Test.
   - **Probes**, always named `Probe - <Behavior>`, such as `Probe - Null` or `Probe - Pusher`. Each probe isolates one behavior.
6. **`RUN_SETS`** — the named groups `RUN_SET` picks from.
7. **`PERSONAS`** — what the tool actually reads. **The avatar name here must match `config.py`'s `SCENARIOS` exactly,** or the avatar never shows up as ready.
8. **`EXPECTATIONS`** — what a correct result looks like for each persona (scores, what the coaching should say, what counts as an avatar pass or fail). The tool ignores it; it's for reading results.
9. **`REFERENCE_RUBRIC`** — the rubric and best-practice text, kept for reference. Never sent to the learner AI.

### Writing personas that give trustworthy results

- **Give every persona a name and firm limits:** "under 25 words," "at most twice," "never ask why." Not "often" or "sometimes," and never "should resemble an average performer." Vague personas drift between rounds.
- **Trap Test** is polished on every surface skill but never pursues the outcome. For example, it's warm and full of reminiscence but never asks for the shower. A pushy or rushed learner is a probe, not a trap.
- **Medium** passes some of the avatar's conditions and reliably fails one.
- **Low** has hard limits, including banned skill words in every form, so it can't drift competent.
- **Personas must not do the avatar's job.** Tell them to give only what's asked.
- **Every persona has an "After coaching" section.** The tool uses it for that persona's follow-up questions, which is how score challenges get tested.
- **Every avatar has a `Probe - Null`.** It sends filler, then asks for coaching after six messages. The coaching should give no scores and invent no evidence.
- **Work out each persona's expected scores from the current rubric before you run,** and write them in `EXPECTATIONS`.

### Check a file before you run it

From the tool's folder, run:
```
python check_personas.py
```
(or `python check_personas.py Ross` for one file). It never calls OpenAI or Better Path AI and never changes anything. It reads every avatar file and `config.py`, then lists:
- **ERRORS** — things that stop an avatar from running correctly, such as a name that doesn't match `config.py`, rubric text in the context, or a run set naming a persona that doesn't exist.
- **warnings** — things to fix next time you work on that avatar, such as an empty Trap Test slot, a persona with no "Please coach me" line, or no expected scores yet.

### Adding a new avatar

1. Copy `personas\_TEMPLATE.py` and rename the copy to the avatar's name (e.g. `Carol.py`).
2. Fill in every `<...>` placeholder. Use `Tony.py` or `Ross.py` as the worked example.
3. Add the avatar to `config.py`'s `SCENARIOS` with exactly the same name (Step 3).
4. Run `python check_personas.py`, then a 1-round test run (Step 7).

### Settings shared by every avatar

`personas\__init__.py` combines the avatar files and holds a few settings for every avatar. You likely won't need to touch it:
- `ROUNDS = 4` — how many times the battery repeats.
- `MAX_TURNS_BEFORE_COACHING = 24` — a safety net. Normally the persona says "Please coach me" when its scenario ends (or the learner AI decides the objective is reached). This cap only stops a stuck conversation.
- `MAX_MENTORING_TURNS = 3` — the same idea, for follow-up questions after coaching.
- `COACHING_REQUEST_MESSAGE` — the exact phrase the app listens for. Don't change it.
- `MENTORING_FOLLOWUP_PROMPT` — the shared follow-up behavior. Each persona's own "After coaching" section is added to it.

## Step 7: Run it

1. In Command Prompt, in that same folder, run:
   ```
   python run_qa_tests.py
   ```
2. It lists every avatar that's ready to run (has both an entry in `config.py`'s `SCENARIOS` and at least one filled-in persona prompt in its `personas/` file) and asks which ones you want to test today:
   ```
   Which avatars do you want to test today?

     1. Madison - Behavioral Health - Moderate
     2. Maya - Some Scenario

   Type the numbers separated by commas (e.g. 1,3), or "all" for every avatar:
   ```
   Type the numbers for the avatars you want (e.g. `1` for just Madison, `1,2` for both), or type `all` to run everything. Press `Ctrl+C` here if you want to cancel before it starts.
3. Next it asks how many rounds to run:
   ```
   How many rounds? (press Enter for the usual 4, or type a number):
   ```
   Just press **Enter** for the normal full run (whatever `ROUNDS` is set to in `personas\__init__.py`, 4 by default). Type a number instead when you want fewer — e.g. `1`, if you've just set up a new avatar and only want to confirm it's wired up correctly before committing to a full battery.
4. You'll see live progress printed as it works through each avatar, round, persona, and turn — including when the learner AI decides a conversation is done, and after how many turns.
5. Each avatar gets its **own** Excel file, saved in that same folder as soon as that avatar finishes, named after the avatar — e.g. if you ran Madison and Ross together:
   ```
   Madison - Behavioral Health - Moderate_qa_results_20261002_143205.xlsx
   Ross_qa_results_20261002_143205.xlsx
   ```
   Every file from the same run shares the same date/time stamp, so they're easy to match up. At the very end it prints a list of every file it saved.
6. Open each file. One row per message, in order, with columns for round/persona/turn/speaker — upload it into that avatar's own project, or filter/copy from there.

**If a run stops partway through** (Ctrl+C, an expired token, etc.): any avatar that already finished is already saved normally. The avatar that was in progress gets saved with `_PARTIAL` at the end of its name (e.g. `Ross_qa_results_20261002_143205_PARTIAL.xlsx`), so you know it's incomplete. Avatars that hadn't started yet get no file.

Once you've answered the two prompts (avatars, then rounds), you can walk away — it doesn't need you to watch it after that.

## Step 8: Check a run for gaps

`analyze_run.py` reads a results file and tells you what went wrong, without
you having to read hundreds of transcript rows. It makes **no** API calls, so
it costs nothing, needs no token, and can be run as many times as you like.

```
python analyze_run.py avatars/gladys/runs/qa_20261116_162652.xlsx
```

It also reads the QA Lab's own "Download Excel" export, so you can analyse a
portal run the same way:

```
python analyze_run.py avatars/gladys/runs/portal_run_28.xlsx
```

Wildcards work too: `python analyze_run.py bpai_qa_results_*.xlsx`

It reports five things:

1. **Avatar identity** — whether the avatar that answered is the one you meant
   to test. It prints the opening line and checks how much of that avatar's own
   vocabulary (names, places, interests from `SHARED_CONTEXT`) actually appears.
   A run against the wrong avatar is worthless, and this catches it in one line.
2. **Scoring scale** — what denominator the coaching is using, and whether it
   matches the bands in `EXPECTATIONS`. A mismatch here is what makes the QA
   Lab show "No score" for every round.
3. **Bands** — each persona's scores per round against its expected band.
4. **Per-category** — the mean for each category, flagged in red when it falls
   outside the range in that persona's `per_point`. This is where a category
   being over- or under-credited shows up.
5. **Evidence integrity** — whether the lines the coaching quotes as proof were
   really said by the learner. Two problems get reported separately:
   - *fabricated* — the quote appears nowhere in the conversation at all.
   - *misattributed* — the quote is real, but the **avatar** said it, and the
     coaching is crediting it to the learner. This matters: it is how a persona
     that never does something still gets scored as if it did.

If the Avatar column holds a number rather than a name (the QA Lab writes an
internal id), it works out which avatar file the transcript matches. Use
`--avatar Gladys` to force it.

## Step 9: Have an AI judge grade the run

`judge.py` goes further than Step 8: it sends each conversation to the judge
model along with that persona's `EXPECTATIONS`, and asks for a verdict.

```
python judge.py avatars/gladys/runs/qa_20261116_162652.xlsx
```

It adds a **Judge** sheet to the same Excel file, one row per conversation:
verdict, expected band, reported score, which `avatar should` checks were met,
which `avatar must not` checks were tripped, and quoted evidence for each.

Unlike Step 8, this one **does** make API calls (one per conversation, using
`JUDGE_MODEL` from `config.py`), so it costs money and takes a few minutes.
Run Step 8 first; only reach for the judge when you want the detail.

An avatar whose persona file has no `EXPECTATIONS` entry is skipped with a
note. Entries written as loose prose give unreliable verdicts — write them as
short, checkable statements, the way `personas/Gladys.py` does.

## Step 10: Set an avatar up in the QA Lab portal

`export_portal_personas.py` turns a persona file into a paste-ready sheet for
the QA Lab's Personas tab, so the portal and the code can't drift apart.

```
python export_portal_personas.py Gladys --out avatars/gladys/settings/PORTAL_PERSONAS.md
```

The file it writes has one block per persona with every QA Lab field filled in:
Name, Kind, "How this user behaves", the lowest/highest score, "The avatar
should", "The avatar must not", "The coaching should", "Follow-up answers
should", and Notes. Leave off `--out` to print it to the screen instead.

Two things to get right in the portal:

- **Enter the scoring table before the persona score bands.** The "out of N" on
  the Personas tab comes from the scoring table's total. If the table is still
  on its default, every band you type is recorded against the wrong scale.
- **The Evaluation Format, the scoring table and the persona bands must all use
  the same scale.** If the coaching prints `Overall Score: X/100` while the
  bands are out of 40, the portal reports "No score" for every round.

Regenerate this file rather than editing it by hand — it is only correct
because it is generated from the persona file.

## Troubleshooting

**"HEADERS is empty" error right away**
You skipped Step 4, or pasted into the wrong spot, or forgot to save `config.py` afterward.

**"USER_ID is not set" error right away**
Same idea, for Step 3 — `USER_ID` is still `0`.

**"OpenAI isn't configured yet" error**
You skipped Step 5, or left `OPENAI_API_KEY` or `OPENAI_MODEL` blank in `config.py`.

**An error mentioning a file in the `personas` folder (a `SyntaxError`, or a name it doesn't recognize)**
Python's error message will point you straight to the exact file and line — open that one file in Notepad and check it against `madison.py`'s pattern. The most common cause is a quote mark or set of triple quotes (`"""`) that doesn't line up right in a `"context"` block, especially after pasting in a long rubric. See the earlier note in this guide about `"""` and stray quotes if you're not sure what to look for.

**"(personas/somefile.py doesn't define a PERSONAS dict - skipping it.)" printed when you run the tool**
Not an error — just a heads-up that one of your avatar files doesn't have a module-level `PERSONAS = {...}` in it yet, so it was skipped. If that file is meant to be a real avatar, check it matches `madison.py`'s pattern. If it's meant to be scratch notes or a template, rename it to start with an underscore (e.g. `_notes.py`) so the tool stops mentioning it.

**"WARNING: '...' is defined in more than one file under personas/"**
Two of your avatar files used the exact same avatar name as their dictionary key. Only one wins (whichever loaded last), so rename one of them to be unique, or merge the two files' content into one if that was accidental.

**401 error from de.better-path-ai.com**
Your Better Path AI token expired. Repeat Step 4 to grab a fresh copy and run it again.

**500 (or other 5xx) error from de.better-path-ai.com**
As of 2026-09-24, the tool automatically retries a Better Path AI server error a few times before giving up — you'll see "Better Path AI server error (500) - waiting Ns before retrying..." printed live, retrying up to 3 times with increasing waits (3s, 6s, 12s). This covers a brief server hiccup that clears up on its own. If you still see the run stop with a 5xx error after that, it already tried and failed multiple times — that's a real, repeated problem on Better Path AI's end worth reporting to your engineers (include the round/avatar you were on and roughly when it happened), not something to troubleshoot in your own config. Unlike the 401 and 422 cases above, this one isn't something you caused.

**401 error from api.openai.com**
Your OpenAI API key is wrong or has expired — double check what you pasted in Step 5, or ask your team for a fresh key.

**404 error from api.openai.com**
Usually means `OPENAI_MODEL` isn't a valid model name, or `OPENAI_BASE_URL` has a typo (only relevant if your team gave you a custom gateway URL instead of the default). Double check both against what you were given in Step 5.

**429 error from api.openai.com**
As of 2026-09-18, the tool now handles this automatically in most cases — a 429 means either a temporary rate limit or the account being out of quota/credits, and it can tell the two apart:
- **Temporary rate limit**: you'll see "OpenAI rate limit hit - waiting Ns before retrying..." printed live. It retries up to 4 times with increasing waits (5s, 10s, 20s, 40s) before giving up. This is normal and not something wrong with your config — a full conversation now makes a lot of OpenAI calls (up to 24 objective turns, plus coaching, plus follow-ups), so brief rate limiting can happen, especially if your org's account has a low requests-per-minute tier.
- **Out of quota/credits**: the tool fails immediately with a clear message saying so, instead of wasting time retrying — this is a billing limit, not a pacing issue, so someone who manages your org's OpenAI account needs to add credits or raise the usage limit before it'll work again.

If you're hitting the temporary rate limit repeatedly across a run, that's a sign your account's per-minute limit is lower than what a full battery needs — worth asking your team about raising it, since there's no good way to make the tool itself slower without also making your testing take much longer.

**"OpenAI didn't return the expected JSON shape" error**
Rare, but can happen if the model doesn't follow the format instructions. The error message includes the raw text it returned — if this keeps happening, it may mean your persona prompt (in that avatar's file under `personas\`) is unusually long or unusual in a way that's confusing the model; try simplifying it slightly.

**400 or 422 error on every message to the avatar (sessions start fine, but sending always fails)**
The tool's `send_message` payload was confirmed against a real captured request on 2026-09-18, along with a third API call (`create_simulation`) the app makes before you start chatting — Better Path AI records a "simulation" for every conversation and expects its `simulation_id` on each message. If Better Path AI changes either of these shapes in the future and you see this error again, here's how to fix it in a few minutes:
1. In Better Path AI, click into an avatar/scenario like normal (this triggers the simulation-record call), then type a message and send it.
2. In DevTools's Network tab, find the requests that fired — look for a `POST` to `/api/simulations/` (near the top, when you first entered the scenario) and a `POST` to `/api/chat/` (when you sent the message).
3. Right-click each one, **Copy > Copy as fetch**, paste into Notepad.
4. Look at each one's `body:` part — it'll show the exact JSON keys the app actually sends.
5. Open `run_qa_tests.py`: match `create_simulation`'s `payload = {...}` to the `/api/simulations/` body, and `send_message`'s `payload = {...}` to the `/api/chat/` body. Also check whether `AVATAR_MODEL` near the top of the file (currently `"gpt-4o"`) still matches the `"model"` field you see — if you added a new avatar and it uses a different one, update it there.

**A note on that Network tab work in general:** whenever you copy a request as fetch to send to me for debugging, please strip out the `authorization: Bearer ...` line first (or replace the token with `Bearer <removed>`) — that token is effectively your password for that Better Path AI session. Everything else in the request (URLs, body, other headers) is fine to share.

**Conversations run much longer than expected (close to the 24-turn cap every time, never reaching coaching)**
The persona isn't recognizing when the scenario is over. Check that persona's "When to ask for coaching" line (the `_WHEN` line near the top of the avatar file) names a moment that actually happens in this scenario, e.g. "right after Madison agrees to stay on the unit." Run `python check_personas.py`: it warns about any persona with no "Please coach me" line.

**"Please coach me" shows up as an ordinary scenario message in the Excel file**
That shouldn't happen as of October 13, 2026: when the learner says "Please coach me," the tool switches straight to coaching and sends it as `during`, like the app. If you see it, you're on an older `run_qa_tests.py`. Replace it with the latest one.

**Mentoring follow-ups run to the 3-question cap every time**
Same idea, but for `MENTORING_FOLLOWUP_PROMPT` in `personas\__init__.py` — the learner AI isn't recognizing when it's asked enough. This one's shared across every avatar and persona, so a tweak there affects every conversation's follow-up phase.

**A big Python error/traceback appears (not the tool's usual "Stopped early" message), mentioning things like `ConnectionResetError`, `ChunkedEncodingError`, or "An existing connection was forcibly closed by the remote host"**
As of 2026-09-25, this is handled automatically too. This happens when your connection to OpenAI or Better Path AI drops mid-request — before any response even comes back — usually from wifi, a VPN, or a proxy hiccup rather than anything wrong with either service. You'll see "Connection to OpenAI/Better Path AI was interrupted (...) - waiting Ns before retrying..." printed live, and it retries automatically (same idea as the 429/5xx handling above) before giving up. If you still see this raw traceback after updating to the latest files, it means it happened more times in a row than the retry budget allows — try running it again, and if it keeps happening consistently, it's worth checking your network connection (or asking IT if a VPN/proxy might be interfering).

**Script seems slow**
That's partly intentional — it pauses briefly between calls so it isn't hammering either server — and partly because most turns now involve two API calls (learner AI, then avatar) instead of one, and every conversation now runs a coaching exchange and up to 3 follow-up questions on top of the objective-seeking part, whether or not the objective was reached. 16 conversations × 4 rounds adds up to real time, but nowhere close to your 4 hours, and you don't have to sit and watch it.

**Need to stop partway through**
Press `Ctrl+C` in the Command Prompt window. Every avatar that already finished is already saved, and the one in progress gets saved with `_PARTIAL` in its name — nothing is lost.

## Once you get real API access from engineering

When IT/engineering approves Team-level access and gives you a proper Better Path AI service credential, just swap what's in `config.py`'s `HEADERS` for that instead of your personal session copy. Nothing else about the tool changes. (Your OpenAI setup is separate and unaffected either way.)
