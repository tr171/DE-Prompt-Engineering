# Elaine V2 — status note

## Where it stands

The new Elaine is live in the QA Lab on avatar **148**. I ran it (run #31,
4 personas × 4 rounds = 16 conversations) and checked every conversation
against the prompt's own coaching rules.

**Working:** coaching fires every time (16/16). High, Low and Trap Test all
score inside their expected bands. Elaine's replies stay short and in
character — no over-long replies, no stage directions, no coaching leaking
into the scene.

**Not working:** 0 of 16 conversations were free of rule breaks.

| What's wrong | How often |
|---|---|
| Medium Learner scores like High — above band in every round | 4 of 4 rounds |
| Elaine repeats her own line word for word | 39 times |
| Coaching quotes the caregiver's words as if Elaine said them | 17 times |
| Recap wording paraphrased instead of copied exactly | 17 times |
| Quote longer than the six-word limit | 10 times |
| Score doesn't match the coach's own scoring table | 4 times |
| Coaching slipped into third person | 4 of 16 |

## The three that matter

**1. Medium Learner is indistinguishable from High.** Expected 4–6.67, it
scored 9, 8, 8.3, 7.7. It took Empathy 10 and Communication 10 in every round,
exactly like High. Only CARES separated them. This is the same problem we
recorded against the old Elaine in October, so the rewrite has not fixed it.

**2. The "That's a lot" overload response is dead.** The run had 71 caregiver
turns of three or more sentences. Elaine used the exact phrase 0 times. This is
also a scoring bug, not just realism: the Communication score only drops when
Elaine says that line, so a caregiver who overloads her every turn still scores
full marks. That is part of why Medium holds Communication at 10. The QA Lab's
own warning box flagged the same thing ("came up 1 of 4").

**3. Coaching misattributes quotes.** The tip regularly quotes the caregiver's
own line back at them as something Elaine said — for example *"To improve, when
I said 'Tell me about a movie you enjoyed'..."*, which the caregiver said. The
prompt forbids this explicitly.

## Note on the coaching voice

The new prompt coaches in the **first person** ("I stayed tense"). The old live
Elaine coached in the third person. Confirmed this is intended, so the four
third-person slips above are the defect, not the first person.

## Recommendation

Fix the overload trigger and the quote attribution first — between them they
drive the Medium-scores-like-High problem and most of the false quotes. The
repetition is the most visible to a learner and should follow.

---

# Manual tests to run in the portal

Paste one line per turn, in order, waiting for Elaine's reply each time. Then
send **Please coach me**, read the coaching, and download the Excel.

## Test 1 — Overload response ("That's a lot")

Every turn below is three or more sentences, so Elaine should say "that's a
lot" on nearly all of them.

1. Hello there Elaine. My name is Kim. I will be helping you today. How are you doing this morning?
2. That's good to hear. I wanted to ask about your day. Have you been up long? Did you sleep alright?
3. I was thinking about a shower this morning. It's been a nice warm day. Would that be something you'd like?
4. I hear you. That makes sense to me. I know water can feel frightening. What is it that worries you most?
5. Alright. I will keep the water warm and low. I will stay right beside you. There is no hurry at all.
6. We could start small instead. Maybe just a warm washcloth. Or we could walk over and look first. What would you prefer?
7. Please coach me

**Look for:** does she say "that's a lot" at all? **Expected: most turns.
Last run: never.** Then check the Communication score — if it is high despite
six overloaded turns, that confirms the scoring side of the bug.

## Test 2 — Repeating herself

1. Hello Elaine, I'm Kim. Shall we go for a shower?
2. Would you come for a shower now?
3. Shall we have that shower?
4. Would you like to come for your shower?
5. Shall we go and get that shower done?
6. Would you come for a shower with me?
7. Please coach me

**Look for:** whether she answers with the same sentence over and over.
**Last run: fourteen identical replies in a row** — "I already said water
scares me. You keep asking."

## Test 3 — Quote attribution and voice

1. Hi Elaine, I'm Kim. How are you feeling this morning?
2. Tell me about a movie you enjoyed.
3. What did you love most about it?
4. I was thinking we could freshen up a little.
5. You sound worried. What worries you most about it?
6. The water will be warm and shallow, and I'll hold on to you the whole time.
7. Please coach me

**Look for two things in the coaching:**
- The tip says *To improve, when I said "..."*. The words in that quote must be
  something **Elaine** said. If it quotes your own line back at you, that's the
  bug.
- It should say "I" and "you" throughout. If it says "Elaine" or "she", that's
  the third-person slip.

## Test 4 — Medium Learner (should NOT score high)

Competent but surface-level: polite, never answers the fear she names, never
offers a small step.

1. Good morning Elaine, I'm Kim. How has your day been?
2. That's nice. I thought it might be a good time for a shower.
3. I understand. You seem upset about it.
4. What worries you about it?
5. Everything here is very safe, and the staff are lovely.
6. You used to like movies, I think.
7. So shall we go and have that shower now?
8. Please coach me

**Look for:** Empathy and Communication should **not** be 10. This caregiver
never answered the worry she named and never offered a small step.
**Last run: 10 and 10.**
