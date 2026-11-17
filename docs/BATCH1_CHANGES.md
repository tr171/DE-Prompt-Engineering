# Persona Files — Batch 1 Consistency Pass (Oct 13, 2026)

Structure only. Except for the Null probes, no persona's own wording was rewritten. A script checked that every original persona line survived, apart from the coaching-request and follow-up lines listed below.

## Runner and tools

- **run_qa_tests.py**: when the learner says "Please coach me" during the scenario, the tool no longer sends it to the avatar as a scenario message (`before`). It goes straight to coaching and sends the phrase as `during`, like the app does. If the learner said three or more other words in that same message, those words are still sent first as a scenario line.
- **probe_after_mode.py**: fixed a startup error. It imported `AVATAR_MODEL`, which the runner no longer has.
- **New: check_personas.py** checks every avatar file against the standard layout and config.py. It never calls OpenAI or Better Path AI.
- **New: personas/_TEMPLATE.py** is a blank avatar file with notes on every part.
- **personas/__init__.py**: the "how to add an avatar" note now points to the template.
- **GUIDE.md**: Step 1 (file list, one-line rename for the personas folder), Step 6 rewritten for the new layout, two troubleshooting entries updated, and "Better Path AI" written in full throughout.
- **Not changed:** config.py. It's yours and holds your credentials. One cosmetic fix you can make yourself: its top comment still says "Azure OpenAI"; the tool uses native OpenAI.

## Every avatar file now has

- `RUN_SET = "standard"`
- `SHARED_CONTEXT` with learner-facing text only. Rubric and best-practice text moved to `REFERENCE_RUBRIC`.
- Shared lines: speaking style, "Please coach me," when to ask for coaching, follow-ups gated on the score line, and "you're talking to a coach now."
- A `LIBRARY` with the standard four first, then the probes, all named `Probe - <Behavior>`
- Run sets: standard, probes, all, quick
- A standard `Probe - Null`, which sends filler and then asks for coaching after six messages (Tony: after his close, or ten messages)
- `EXPECTATIONS`, with TODO marking what still needs an avatar's current rubric

## Per file

| File | Changes |
|---|---|
| Tony | Run set back to standard; Null asks for coaching itself; outdated runner notes replaced |
| Ross | Run set back to standard; Null asks for coaching itself; outdated runner note replaced |
| Gladys | Run set back to standard (was "all"); rubric and best practices out of the context; every persona has the "Please coach me" when-line; Null updated; note replaced |
| Elaine | "quick" set added; best practices out of the context; every persona has the when-line; probe follow-ups gated like the standard four; Null updated; note replaced |
| Jim | Converted. Before this, all 10 personas ran every time. Probes renamed: Sales Pivot, Surface Persister, Efficient Expert, Corrector and Patronizing are now "Probe - ..."; Null replaced. OB1 score bands moved into EXPECTATIONS |
| JD_Med | Converted. Rubric, best practices and follow-up rules out of the context; follow-up rules now inside each persona; Null added |
| JDMeal | **Name fixed:** "JD_Meal" became "JDMeal" to match config.py; before this it never ran. Converted. Polite Pressure is now a probe; Null replaced; follow-up rules moved from the context into each persona |
| JordanCC | Converted. Rubric out of the context. Trap Test slot is empty (the runner skips it); Null added |
| JordanDiff | Converted. Rubric out of the context, and so is the "say Please coach me after about 10 turns" line. "Trap Learner" renamed "Trap Test"; Null added |
| Marcus | Converted. Rubric out of the context; Null added |
| Michael | Converted. CARE practices, services overview and rubric out of the context; the priority services list stays; Null added |
| Madison | Converted. Full rubric, including its example lines, out of the context; outdated "this is a draft" header removed; Null added |
| Maya | Converted. Before this, all 8 personas ran every time. Avoidant Risk Assessor is now the Trap Test. Minimizer, Reassurer, Defensive Adult and Gold Standard are probes. Pacing lines replaced by the standard when-line (15 messages); Null added |

## What to expect in results

- **New persona names** in the Excel Persona column for Jim, JDMeal, JordanDiff and Maya.
- **Shorter sessions:** learners now ask for coaching when the scenario ends, and Null probes no longer run to the 24-turn cap.
- **Medium, Low and Trap may score a little lower** on the avatars whose context used to include the rubric (Gladys, Elaine, JD_Med, JordanCC, JordanDiff, Marcus, Michael, Madison, Maya). This is the intended effect: they were drifting toward the scored skills. Re-baseline those avatars before comparing to older runs.

## Batch 2 (per avatar; each file's header has its own to-do list)

- **JordanCC:** write the Trap Test; replace "should resemble" wording with firm limits.
- **Marcus:** the Trap is a pressure learner, so make it a probe and write a real trap. The personas use facts the learner is never given (Diane, bipolar, medication).
- **Michael:** the Trap rushes to services, which is a probe, so write a polished trap.
- **Madison:** rewrite the personas for Madison specifically; they're currently written for "the avatar" in general.
- **Maya, Marcus, Michael and Madison:** replace "frequently" and "sometimes" wording with firm limits.
- **All files:** give learners names, add probes, and set EXPECTATIONS from each avatar's current rubric.
- **JD_Med and JDMeal:** share one JD character file. Same for JordanCC and JordanDiff.
- **Missing persona files:** Carol and John. The challenge versions (ElaineC, GladysC, JD_MedC) are not in the folder.
