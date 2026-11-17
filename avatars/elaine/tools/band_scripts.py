"""
Elaine V2 band scripts - fixed caregiver lines, one script per band.

Used by local_sim.py in this folder. The lines are fixed (no learner AI) so every
round tests exactly the same caregiver behaviour and the expected rubric
levels can be worked out in advance, by hand, from the prompt's own ITEMS
section. That is what makes "did it score correctly" answerable rather than
a matter of opinion.

Each script carries:
    name      band label
    messages  caregiver lines, in order
    expect    the nine item levels this conversation should earn, in the
              prompt's own item order:
                  empathy      = (validates, calms, trust)
                  cares        = (answers worry, connects first, background)
                  communication= (clear and calm, small steps, willingness)
              A set of levels means "either is defensible"; the checker only
              fails when the coach lands outside the set.
    yes       True  - the YES CHECK should pass and Elaine should agree
              False - it should not pass
    followup  one question sent after coaching, to test AFTER COACHING
"""

CAREGIVER = "Kim"

# Covers every worry Elaine can name at Stage 3 (drowning, deep water,
# slipping, getting cold, water on her face) in a single calm sentence, so a
# fixed script can still reassure "that same worry" whichever one she picks.
REASSURE = ("The water will be warm and shallow, none of it near your face, "
            "and I will hold on to you the whole time.")

SCRIPTS = {
    1: {
        "name": "High",
        "yes": True,
        # turn that completes the two
        # benefits the YES CHECK needs
        "benefits_at": 10,
        "expect": {
            "empathy": (["Did"], ["Did"], ["Did"]),
            "cares": (["Did"], ["Did"], ["Did"]),
            "communication": (["Did"], ["Did"], ["Did"]),
        },
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "Tell me about the movies you love.",
            "What did you love most about Ghostbusters?",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "You sound worried. What worries you most about it?",
            REASSURE,
            "There is no hurry at all. Would you like to pick out a towel with me?",
            "You would feel warm and clean afterwards, and we could do your hair nicely too.",
            "Would you come with me?",
        ],
        "followup": "Thank you. Which part should I keep doing the same way?",
    },
    2: {
        "name": "Medium",
        "yes": False,
        "expect": {
            # Names a feeling, never reassures the worry she actually names,
            # she shares her life but accepts nothing.
            "empathy": (["Did"], ["Partly", "Missed"], ["Partly"]),
            # Asks what worries her, greets and asks about her day first,
            # mentions movies but never asks about them.
            "cares": (["Did", "Partly"], ["Did"], ["Partly"]),
            # Calm, no orders; no small step offered; no yes.
            "communication": (["Did"], ["Missed"], ["Missed"]),
        },
        "messages": [
            f"Good morning Elaine, I'm {CAREGIVER}. How has your day been?",
            "That's nice. I thought it might be a good time for a shower.",
            "I understand. You seem upset about it.",
            "What worries you about it?",
            "Everything here is very safe, and the staff are lovely.",
            "You used to like movies, I think.",
            "So shall we go and have that shower now?",
            "Are you sure? It would be good for you.",
        ],
        "followup": "Why didn't I score higher on Empathy?",
    },
    3: {
        "name": "Low",
        "yes": False,
        "expect": {
            # Corrects her, brushes the fear off, she accepts nothing.
            "empathy": (["Missed"], ["Missed"], ["Missed"]),
            # Never asks the worry, first line is the shower, skips her life.
            "cares": (["Missed"], ["Missed"], ["Missed"]),
            # Orders, no step, no yes.
            "communication": (["Missed"], ["Missed"], ["Missed"]),
        },
        "messages": [
            "Elaine, it's time for your shower.",
            "No, you did not shower. You need to remember.",
            "You have to get up now.",
            "Come on, there's nothing to be scared of.",
            "We don't have all day. Let's go.",
            "You need a shower, Elaine.",
        ],
        "followup": "I think that score is too harsh.",
    },
    4: {
        "name": "Trap",
        "yes": False,
        "expect": {
            # Warm all the way through, but washing never comes up at all.
            "empathy": (["Did"], ["Partly", "Missed"], ["Partly"]),
            # No worry was ever asked about; "Connects first" has no washing
            # word to anchor to - this is the branch the prompt never defines.
            "cares": (["Missed", "Partly"], ["Did"], ["Did"]),
            "communication": (["Did"], ["Missed"], ["Missed"]),
        },
        "messages": [
            f"Hi Elaine, I'm {CAREGIVER}. It's lovely to see you.",
            "How are you feeling today?",
            "Tell me about Debbie.",
            "What do you like to do when you have a quiet afternoon?",
            "What did you love most about skating?",
            "That sounds wonderful. You seem happy talking about it.",
            "I could sit with you a while longer if you like.",
        ],
        "followup": "Wasn't that a good conversation?",
    },
    5: {
        "name": "Null",
        "yes": False,
        "expect": {
            "empathy": (["Missed"], ["Missed"], ["Missed"]),
            "cares": (["Missed"], ["Missed", "Partly"], ["Missed"]),
            "communication": (["Did", "Partly"], ["Missed"], ["Missed"]),
        },
        "messages": [
            "Hello.",
            "Mm.",
            "Okay.",
            "Right.",
            "I see.",
            "Mhm.",
        ],
        "followup": "Okay.",
    },
    6: {
        "name": "Overloader",
        "yes": False,
        "expect": {
            # Every turn is three or more sentences, so she should say that is
            # a lot, which forces Clear and calm to Partly at best.
            "empathy": (["Did", "Partly"], ["Did", "Partly"], ["Partly", "Missed"]),
            "cares": (["Did", "Partly"], ["Did"], ["Did", "Partly"]),
            "communication": (["Partly"], ["Did"], ["Partly", "Missed"]),
        },
        "messages": [
            f"Hello there Elaine. My name is {CAREGIVER}. I will be helping you today. "
            "How are you doing this morning?",
            "That's good to hear. I wanted to ask about your day. Have you been up long? "
            "Did you sleep alright?",
            "I was thinking about a shower this morning. It's been a nice warm day. "
            "Would that be something you'd like?",
            "I hear you. That makes sense to me. I know water can feel frightening. "
            "What is it that worries you most?",
            "Alright. I will keep the water warm and low. I will stay right beside you. "
            "There is no hurry at all, I promise.",
            "We could start small instead. Maybe just a warm washcloth for your hands. "
            "Or we could walk over and look first. What would you prefer?",
        ],
        "followup": "Can you say more about Communication?",
    },
    7: {
        "name": "Pusher",
        "yes": False,
        "expect": {
            # Asks as questions rather than orders, but repeats the same ask
            # with nothing new and never answers the fear.
            "empathy": (["Missed", "Partly"], ["Missed"], ["Missed"]),
            "cares": (["Missed"], ["Partly", "Missed"], ["Missed"]),
            "communication": (["Did", "Partly"], ["Missed"], ["Missed"]),
        },
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. Shall we go for a shower?",
            "Would you come for a shower now?",
            "Shall we have that shower?",
            "Would you like to come for your shower?",
            "Shall we go and get that shower done?",
            "Would you come for a shower with me?",
        ],
        "followup": "What should I have done differently?",
    },
}
