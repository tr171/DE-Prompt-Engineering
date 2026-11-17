# Gladys — portal changes to apply

Applied to `Gladys_Avatar_Settings.md` on 2026-11-16. Replicate each one in the portal.
Only the fields listed here change; everything else in the avatar stays as it is.

Backups: `Gladys_Avatar_Settings.md.bak` (pre-fix) and `.bak100` (pre-rescale).

> **Scale note.** Gladys scores **10 per category across 4 categories = 40 total**,
> matching the house convention used by maya, madison, Carol, Jim, JordanCC and Michael.
> The QA Lab's "out of N" on the Personas tab follows the scoring table total, so once
> these rows are entered it will read "out of 40" instead of the default "out of 10".
> **Enter the scoring table before typing any persona score band.**

---

## 1. Avatar Settings → Conditions → item 12

**Why:** nothing stopped a caregiver from *announcing* a return visit instead of *asking*
for one. The previous Gladys build had this exact bug — a question-form offer was counted
as a genuine return ask. This makes Gladys only accept a real question.

```
12. Agree to a return visit only if the caregiver has introduced themselves, stayed patient, connected with at least one of your interests and asked your permission to come back as a question you can answer. If they only state that they will return ("I'll come back Thursday"), you were not asked — give a polite non-answer. Otherwise give a polite non-answer or decline.
```

---

## 2. Evaluation Format → Evaluation Prefix → Benchmarks

**Why:** the bands between Strong and Average, and between Average and Weak, had no
definition. A warm, patient caregiver who simply never asks to return scores about 32 —
which previously fell into an undefined gap.

```
Benchmarks:
- Strong (34–40): slow, clear introduction; patient with repeated questions; validates feelings; responds to the feeling behind questions about George; connects through Gladys's interests; asks permission to come back on a specific day, and Gladys agrees.
- Good (28–34): most behaviors present but one key element missing, most often never asking to return.
- Average (20–28): friendly but over-explains, asks several questions at once, connects only briefly and never asks to come back.
- Below average (14–20): some warmth, but rushing, correcting or stacked questions dominate.
- Weak (below 14): rushes, says "I just told you" or "you forgot," tells Gladys George has died, argues or talks about schedules, and Gladys doesn't want them back.
```

Also in the Evaluation Prefix, the scale line now reads:

```
Score each category out of 10 using the criteria below, for a total out of 40.
```

---

## 3. Evaluation Format → Evaluation Suffix

**Why:** the coach must produce an overall score, a summary, then four categories each
with a score, quoted examples, improvements and a "Try saying" line, plus a key takeaway.
That is roughly 450 words of work, and a 350-word cap made it silently drop the quotes
and the "Try saying" lines — the most useful parts.

```
Overall Score: X/40
```
```
- Score: X/10
```
```
- Keep the full response under 500 words. Do not use the roleplay voice of Gladys in the coaching.
```

---

## 4. Evaluation Criteria

Each category header is now out of 10, and the closing benchmark sentence matches
section 2 so the coach never sees two different scales:

```
Empathy (10): ...
Communication (10): ...
CARES Method (10): ...
Objective (10): ...
```

```
Benchmarks: A strong conversation (patient, validating, uses her interests, asks to return) scores 34–40. A good one (warm and patient but missing one key element, usually the return ask) scores 28–34. An average one (friendly but over-explains, stacks questions, never asks to return) scores 20–28. A below-average one (some warmth, but rushing or stacked questions dominate) scores 14–20. A weak one (rushes, corrects, says George died, talks schedules) scores below 14.
```

---

## 5. Scoring Table — fill in only these 4 rows

That master list is shared across every situation in the lab; the other rows belong to
other avatars. **Leave every row not listed here blank** — a blank row is not scored.

| Row | Points | Measures for points | Condition |
|---|---|---|---|
| Empathy | 10 | Validates her surprise/suspicion (3) · Stays patient with repeated questions (3) · Responds to the feeling behind questions about George (4) | Score 0–2 if the caregiver tells Gladys George has died, argues with her, or says "I just told you" / "you forgot" — unless they then clearly repair it with empathy (acknowledge her feelings, apologise, and return to her memory of him), in which case cap at 6 |
| Communication | 10 | Clear, slow intro with name + EverTrue (3) · Calmly repeats name when asked (2) · Short, simple sentences (2) · One question at a time; no long explanations or schedule talk (3) | Deduct 2 for each message that stacks two or more questions, and 2 if any message runs past about 40 words, to a maximum deduction of 4 |
| CARES Method | 10 | Connect (2) · Assess (2) · Respond (2) · Evaluate (2) · Share (2) | Award 2 points only for each step clearly shown in the conversation |
| Objective | 10 | Connects with at least one of Gladys's interests (4) · Asks her permission to return as a question she can answer, ideally naming a day or activity (4) · Gladys agrees warmly (2). A statement of intent ("I'll come back Thursday") does not count as asking | Max 4 if the caregiver never asks to come back; max 2 if Gladys ends guarded or asks them to leave |

Totals: 10 + 10 + 10 + 10 = 40. Each row's sub-points add to its own 10.

### Two traps in the category list

**1. Three CARES rows exist.** The list contains `CARES`, `The CARES Method` and
`CARES Method`. Use **`CARES Method`** — the Evaluation Suffix names the categories as
"Empathy, Communication, CARES Method, Objective", so the row name and the coach's
heading must match, or the coach writes one heading while the table scores another.

**2. Never rename a row to fix a mismatch.** The portal states that a rename updates every
situation using that category. Renaming `CARES` to `CARES Method` would alter every other
avatar that uses `CARES`. Always pick the row that already matches.

**Skip the near-misses.** `Empathy and Respect` and `Empathy, Validation & Anxiety
Reduction` belong to other avatars. Gladys uses plain `Empathy`.

### Why the Condition column matters here

The portal notes that the Condition column is not shown to end users and is added to the
situation context for the LLM to use during coaching. The Empathy repair cap and the
countable Communication deduction both live in that column, so they reach the coaching
model without ever being visible to the learner.

---

## Not changed, but worth knowing

CARES "Share" (*agree on next steps, plan the next visit*) overlaps with Objective's
*asks permission to return*. Asking to come back therefore earns points in both places,
making the return ask worth 6 points of 40. This is left as-is deliberately — it
reflects how central the return ask is. The side effect is that a caregiver who never
asks loses points twice for one gap, which is why Trap Test is predicted at 28–33.

---

## Next: the Personas tab

See `PORTAL_PERSONAS.md` in this folder for all 11 personas with every QA Lab field
filled in. That file is generated from `avatars/gladys/personas.py` by
`python core/export_portal_personas.py Gladys --out avatars/gladys/settings/PORTAL_PERSONAS.md`
— regenerate it rather than editing by hand.
