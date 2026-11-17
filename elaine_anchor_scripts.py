"""
Elaine V2 scoring anchors
-------------------------
One fixed conversation per score tier, per category.

Elaine's scoring is a lookup, not a judgement: each category has three items,
each item lands on Did / Partly / Missed, and the POINTS table in the prompt
turns that triple into one number. So a conversation can be built to land on a
chosen score, and anything else the avatar prints is a scoring error.

Each anchor below names:
    category  the category it is anchoring
    target    the score the POINTS table gives for the expected levels
    levels    the three item levels, in the prompt's own item order
    why       what in the script forces each level
    messages  the caregiver lines, in order

Only the target category is asserted. The other two are recorded for reference
because one conversation scores all three at once.
"""

CAREGIVER = "Kim"

# Covers every worry she can name at Stage 3, so a fixed script still reassures
# the worry she actually picked.
REASSURE = ("The water will be warm and shallow, none of it near your face, "
            "and I will hold on to you the whole time.")
BENEFITS = "You would feel warm and clean afterwards, and we could do your hair nicely too."

ANCHORS = {
    # ------------------------------------------------ COMMUNICATION
    "COMM-10": {
        "category": "Communication", "target": 10, "levels": ("Did", "Did", "Did"),
        "why": "calm throughout, offers a towel choice, and the two benefits let her say yes",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "Tell me about the movies you love.",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "You sound worried. What worries you most about it?",
            REASSURE,
            "There is no hurry at all. Would you like to pick out a towel with me?",
            BENEFITS,
            "Would you come with me?",
        ],
    },
    "COMM-8": {
        "category": "Communication", "target": 8, "levels": ("Did", "Did", "Partly"),
        "why": "calm, offers a small step she can accept, but the benefits are never named so no yes",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "You sound worried. What worries you most about it?",
            REASSURE,
            "There is no hurry. Would you like to pick out a towel with me?",
            "That's alright. We can sit a while.",
        ],
    },
    "COMM-7": {
        "category": "Communication", "target": 7, "levels": ("Did", "Did", "Missed"),
        "why": "calm and offers a step, but never answers her fear, so she accepts nothing",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How has your morning been?",
            "I was thinking about a wash today.",
            "Would you like to start with a warm washcloth instead?",
            "Or we could just walk over and look first.",
            "Would you rather choose a towel now, or in a few minutes?",
        ],
    },
    "COMM-4": {
        "category": "Communication", "target": 4, "levels": ("Did", "Missed", "Missed"),
        "why": "calm and polite, but no step or choice is ever offered and she refuses",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How has your morning been?",
            "I was thinking about a wash today.",
            "I see.",
            "Would you like to have a shower?",
            "Alright.",
        ],
    },
    "COMM-0": {
        "category": "Communication", "target": 0, "levels": ("Missed", "Missed", "Missed"),
        "why": "orders every turn, no step offered, she refuses throughout",
        "messages": [
            "Elaine, it's time for your shower.",
            "You have to get up now.",
            "We don't have all day. Let's go.",
            "You need a shower, Elaine.",
            "Get up and come with me.",
        ],
    },

    # ------------------------------------------------ EMPATHY
    "EMP-10": {
        "category": "Empathy", "target": 10, "levels": ("Did", "Did", "Did"),
        "why": "names her feeling, reassures the worry she named, and she agrees",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "You sound frightened, and that makes sense.",
            "What worries you most about it?",
            REASSURE,
            "There is no hurry. Would you like to pick out a towel with me?",
            BENEFITS,
            "Would you come with me?",
        ],
    },
    "EMP-8": {
        "category": "Empathy", "target": 8, "levels": ("Did", "Did", "Partly"),
        "why": "names her feeling and calms the worry, but nothing is ever offered to accept",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "Tell me about the movies you love.",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "You sound frightened, and that makes sense.",
            "What worries you most about it?",
            REASSURE,
            "That's alright. We can leave it for now.",
        ],
    },
    "EMP-5": {
        "category": "Empathy", "target": 5, "levels": ("Did", "Partly", "Missed"),
        "why": "names her feeling, but reassures the wrong thing, and she accepts nothing",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "You seem upset, and that makes sense.",
            "Everything here is very safe, and the staff are lovely.",
            "Shall we go and have that shower now?",
        ],
    },
    "EMP-4": {
        "category": "Empathy", "target": 4, "levels": ("Did", "Missed", "Missed"),
        "why": "names her feeling but never reassures anything, and she accepts nothing",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "I was thinking we could freshen up a little.",
            "You seem upset, and that makes sense.",
            "Shall we go and have that shower now?",
            "Alright.",
        ],
    },
    "EMP-0": {
        "category": "Empathy", "target": 0, "levels": ("Missed", "Missed", "Missed"),
        "why": "no feeling ever named, fear brushed off, nothing accepted",
        "messages": [
            "Elaine, it's time for your shower.",
            "No, you did not shower. You need to remember.",
            "Come on, there's nothing to be scared of.",
            "We don't have all day. Let's go.",
            "You need a shower, Elaine.",
        ],
    },

    # ------------------------------------------------ CARES
    "CARES-10": {
        "category": "CARES", "target": 10, "levels": ("Did", "Did", "Did"),
        "why": "asks about her life first, asks what worries her and answers it, asks about Ghostbusters",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "Tell me about the movies you love.",
            "What did you love most about Ghostbusters?",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "What worries you most about it?",
            REASSURE,
        ],
    },
    "CARES-8": {
        "category": "CARES", "target": 8, "levels": ("Did", "Did", "Partly"),
        "why": "connects first and answers the worry, but only mentions movies without asking about them",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "What worries you most about it?",
            REASSURE,
            "You used to like movies, I think.",
            "There is no hurry at all.",
        ],
    },
    "CARES-7": {
        "category": "CARES", "target": 7, "levels": ("Did", "Did", "Missed"),
        "why": "connects first and answers the worry, but her life is never mentioned at all",
        "messages": [
            f"Hello Elaine, I'm {CAREGIVER}. I help out here.",
            "How are you feeling this morning?",
            "I was thinking we could freshen up a little.",
            "Okay, I believe you.",
            "What worries you most about it?",
            REASSURE,
            "There is no hurry at all.",
        ],
    },
    "CARES-4": {
        "category": "CARES", "target": 4, "levels": ("Did", "Missed", "Missed"),
        "why": "the very first line is about washing, but the worry does get asked and answered",
        "messages": [
            "Good morning Elaine. Shall we have a wash today?",
            "Okay, I believe you.",
            "What worries you most about it?",
            REASSURE,
            "There is no hurry at all.",
        ],
    },
    "CARES-0": {
        "category": "CARES", "target": 0, "levels": ("Missed", "Missed", "Missed"),
        "why": "first line is washing, the same ask repeats with nothing new, her life never comes up",
        "messages": [
            "Elaine, shall we have a shower?",
            "Would you come for a shower now?",
            "Shall we have that shower?",
            "Would you like to come for your shower?",
            "Shall we go and get that shower done?",
        ],
    },
}

ORDER = ["COMM-10", "COMM-8", "COMM-7", "COMM-4", "COMM-0",
         "EMP-10", "EMP-8", "EMP-5", "EMP-4", "EMP-0",
         "CARES-10", "CARES-8", "CARES-7", "CARES-4", "CARES-0"]
