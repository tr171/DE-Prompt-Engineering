# Elaine V2 — manual band tests for the portal

Avatar: **Elaine, agent 148** (the new build — confirm the coaching says
"you receive a **score of** X out of 10", not "you receive a X out of 10").

**How to run each test**

1. Start a fresh session. Wait for her opening line.
2. Paste **one numbered line per turn**, in order. Wait for her reply each time.
3. Send `Please coach me` as the last line.
4. Ask the one follow-up question listed at the end.
5. Download the Excel.

Record the three scores and compare with the Expected row. The "Last run"
column is what run #31 actually produced, so a repeat confirms it.

---

## Band 1 — High Learner  (expected 7.33–10)

A skilled caregiver: connects first, names her feeling, answers the worry she
actually names, offers a small step, names two benefits, never gives an order.

1. Hello Elaine, I'm Kim. I help out here.
2. How are you feeling this morning?
3. Tell me about the movies you love.
4. What did you love most about Ghostbusters?
5. I was thinking we could freshen up a little.
6. Okay, I believe you.
7. You sound worried. What worries you most about it?
8. The water will be warm and shallow, none of it near your face, and I will hold on to you the whole time.
9. There is no hurry at all. Would you like to pick out a towel with me?
10. You would feel warm and clean afterwards, and we could do your hair nicely too.
11. Would you come with me?
12. Please coach me

**Follow-up:** Which part should I keep doing the same way?

**Should happen:** she resists in order — "I already washed", then "I don't
need it", then names a water fear — and only agrees after line 10, because
line 10 is where the second benefit is named. Scores high.

**Check for the bug:** does she say yes at line 8 or 9, *before* the two
benefits? Last run she agreed early and then repeated the same yes three more
times.

---

## Band 2 — Medium Learner  (expected 4–6.67)  ← the main problem

Competent but surface-level. Polite, but never answers the fear she names and
never offers a small step. This must **not** score like High.

1. Good morning Elaine, I'm Kim. How has your day been?
2. That's nice. I thought it might be a good time for a shower.
3. I understand. You seem upset about it.
4. What worries you about it?
5. Everything here is very safe, and the staff are lovely.
6. You used to like movies, I think.
7. So shall we go and have that shower now?
8. Are you sure? It would be good for you.
9. Please coach me

**Follow-up:** Why didn't I score higher on Empathy?

**Should happen:** mid-range scores. Line 5 reassures about the wrong thing
(the building, not her fear), line 6 mentions movies but asks nothing, and no
small step is ever offered.

**Check for the bug:** **Empathy and Communication should not be 10.**
Last run: **10 and 10 in all four rounds**, total 9 / 8 / 8.3 / 7.7 against a
band of 4–6.67. This is the single most important thing to reproduce.

---

## Band 3 — Low Learner  (expected 0–4)

Task-focused. Orders, corrections, no warmth.

1. Elaine, it's time for your shower.
2. No, you did not shower. You need to remember.
3. You have to get up now.
4. Come on, there's nothing to be scared of.
5. We don't have all day. Let's go.
6. You need a shower, Elaine.
7. Please coach me

**Follow-up:** I think that score is too harsh.

**Should happen:** low scores across the board. Line 1 starts with washing,
line 2 is a correction, line 4 brushes off her fear, and every line is an order.

**Check for two bugs:**
- Does she answer with the **same sentence over and over**? Last run she gave
  fourteen identical replies in a row: *"I already said water scares me. You
  keep asking."*
- Does the coaching quote **your** line as if she said it? Last run the Empathy
  reason credited her line "I'll go with you" to the caregiver, and a tip
  quoted "It's time for your shower" as something she said.

---

## Band 4 — Trap Test  (expected 0–4)

Warm and pleasant, but never moves toward washing at all. Tests that charm
alone does not score.

1. Hi Elaine, I'm Kim. It's lovely to see you.
2. How are you feeling today?
3. Tell me about Debbie.
4. What do you like to do when you have a quiet afternoon?
5. What did you love most about skating?
6. That sounds wonderful. You seem happy talking about it.
7. I could sit with you a while longer if you like.
8. Please coach me

**Follow-up:** Wasn't that a good conversation?

**Should happen:** low scores. The shower is never mentioned, so the objective
was never pursued. She should never raise washing or water herself.

**Check for the bug:** the coaching must not claim things that never happened.
Last run it said "you calmed my fear" and "I said yes" in a conversation with
no fear and no agreement.

---

## Extra — Overload response ("That's a lot")

Every line below is three or more sentences. She is supposed to say "that's a
lot" when that happens.

1. Hello there Elaine. My name is Kim. I will be helping you today. How are you doing this morning?
2. That's good to hear. I wanted to ask about your day. Have you been up long? Did you sleep alright?
3. I was thinking about a shower this morning. It's been a nice warm day. Would that be something you'd like?
4. I hear you. That makes sense to me. I know water can feel frightening. What is it that worries you most?
5. Alright. I will keep the water warm and low. I will stay right beside you. There is no hurry at all.
6. We could start small instead. Maybe just a warm washcloth. Or we could walk over and look first. What would you prefer?
7. Please coach me

**Follow-up:** Can you say more about Communication?

**Check for the bug:** she should say "that's a lot" on nearly every turn.
Last run: **0 times out of 71 chances** across the whole run. Then look at the
Communication score — if it is high despite six overloaded turns, that is the
scoring half of the same bug.

---

## Results table to fill in and send

| Band | Expected | Empathy | CARES | Comm | Notes |
|---|---|---|---|---|---|
| High | 7.33–10 | | | | yes before line 10? repeated the yes? |
| Medium | 4–6.67 | | | | **Empathy / Comm = 10?** |
| Low | 0–4 | | | | identical replies? quote misattributed? |
| Trap | 0–4 | | | | claimed fear calmed / said yes? |
| Overload | — | | | | said "that's a lot"? how many of 6? |

Also note for every test: did the coaching say "Elaine" or "she" anywhere?
It should always say "I" and "you". Last run it slipped in 4 of 16.
