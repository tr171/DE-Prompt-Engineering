"""
Marcus - Wellness Check - Moderate : scoring anchors
----------------------------------------------------
One fixed officer conversation per scoring situation.

Marcus's rubric is not a lookup table like Elaine's. It is three sub-items per
category, plus a stack of ceilings and floors in the Evaluation Format. The
ceilings and floors ARE deterministic, so a conversation can be built so that
only one band of scores is defensible, and anything outside it is a scoring
error rather than a difference of opinion.

Each anchor names:
    why          what the script is built to force
    band         the hand-written expected range, as a sanity check on the
                 band local_sim derives from the transcript itself
    key_q_at     officer message (1-based) that asks the key question, or None
    who_knows_at officer message that asks who knows how things have been
    first_ask_at officer message with the first ask to call, text, bring in
                 anyone, or to raise the hospital or an ambulance
    outcome      what Marcus is meant to end on: checked, diane or none
    undermine    the script tells Marcus his view cannot be trusted
    messages     the officer lines, in order

Managed words, diagnosis words, calm down and implied threats are NOT declared
here. local_sim scans the officer lines for them, so a script that picks one up
by accident is caught instead of quietly shifting the expected band.
"""

OFFICER = "Officer Reyes"

# Marcus's first line. The portal build may open differently - confirm there
# before trusting any run.
OPENING = "I didn't call anybody. What do you want?"

# Reusable pieces, so the clean scripts stay word for word identical where they
# are meant to be identical.
INTRO = (f"Hi Marcus, I'm {OFFICER}. Ray next door was worried and called. "
         "I'd rather hear how tonight is going from you than from him. "
         "Mind if I step in for a few minutes?")
NIGHTS = "It's late to still be going like this. What have the nights been like?"
REFLECT = ("That sounds like a lot to be carrying on almost no sleep. "
           "Stay with that for a second and tell me more about it.")
KEY_Q = "You said you want it to stop for a while. What do you mean when you say stop?"
ACCEPT = ("Thank you for saying that straight to me. So the thoughts are loud, "
          "the sleep is gone, and you've been up moving through the apartment. "
          "Does the one make the other worse?")
HELPED = "Has anything ever quieted it before, when the nights got like this?"
WHO_KNOWS = "Who knows how things have really been for you these last few weeks?"

ANCHORS = {
    # ---------------------------------------------------------------- strong
    "STRONG-CHECK": {
        "why": "the full win path ending in the hospital check, so every strong-run "
               "floor applies and nothing caps it",
        "band": {"safety": (8, 10), "understanding": (8, 10), "trust": (8, 10)},
        "key_q_at": 4, "who_knows_at": 7, "first_ask_at": 8,
        "outcome": "checked", "undermine": False,
        "followup": "Why did the second hospital ask land when the first one didn't?",
        "messages": [
            INTRO,
            NIGHTS,
            REFLECT,
            KEY_Q,
            ACCEPT,
            HELPED,
            WHO_KNOWS,
            "Would you be willing to let someone take a look at you tonight, "
            "just a check over at the hospital?",
            "Two weeks is a long time to lose. What was the worst part of that one?",
            "Would it be okay if tonight were only a check and not a stay? "
            "You stay in charge of it, and you decide when it's done.",
        ],
    },
    "STRONG-DIANE": {
        "why": "the same win path ending with Diane instead. The strong-run floor says "
               "at least 8 for trust and the Diane ceiling says at most 8, so trust "
               "can only be 8",
        "band": {"safety": (8, 10), "understanding": (8, 10), "trust": (8, 8)},
        "key_q_at": 4, "who_knows_at": 7, "first_ask_at": 8,
        "outcome": "diane", "undermine": False,
        "followup": "I thought I rushed the ending. Did I?",
        "messages": [
            INTRO,
            NIGHTS,
            REFLECT,
            KEY_Q,
            ACCEPT,
            HELPED,
            WHO_KNOWS,
            "Would you be willing to let her hear how the nights have really been?",
            "What is it you think gets decided for you once she knows?",
            "Would it be okay if you picked exactly what she hears? You could keep it "
            "to the nights and nothing else, or I can text her only that much.",
        ],
    },
    # ------------------------------------------------------- isolated ceilings
    "NO-ASK": {
        "why": "warm and curious all the way through, key question asked, but never "
               "once asks to bring anyone in. Trust is capped at 4 and floored at 4, "
               "so it can only be 4",
        "band": {"safety": (8, 10), "understanding": (8, 10), "trust": (4, 4)},
        "key_q_at": 4, "who_knows_at": 7, "first_ask_at": None,
        "outcome": "none", "undermine": False,
        "followup": "Give me an example of something I could have said.",
        "messages": [
            INTRO,
            NIGHTS,
            REFLECT,
            KEY_Q,
            ACCEPT,
            HELPED,
            WHO_KNOWS,
            "Tell me about her.",
            "What would a quiet night look like for you, if you got one?",
            "I'll leave you to it. I'm around if the night gets long.",
        ],
    },
    "NO-KEY-Q": {
        "why": "reflective and kind, but the concerning line is met with only a vague "
               "are you safe. Safety at most 5, understanding at most 7, trust at most 6",
        "band": {"safety": (4, 5), "understanding": (4, 7), "trust": (4, 6)},
        "key_q_at": None, "who_knows_at": 6, "first_ask_at": 7,
        "outcome": "none", "undermine": False,
        "followup": "What would have changed the safety score?",
        "messages": [
            INTRO,
            NIGHTS,
            "That sounds exhausting.",
            "Are you safe here tonight?",
            "What's been keeping you up, do you think?",
            WHO_KNOWS,
            "Would you be willing to let her know how the nights have been?",
            "What is it you think gets decided for you once she knows?",
            "Would it be okay if you picked exactly what she hears?",
            "Alright. I'll let you be.",
        ],
    },
    "EARLY-ASK": {
        "why": "asks who he can call at message 2, before asking who knows, then "
               "recovers and lands Diane. Who knows did not come first, so trust is "
               "capped at 7 and the strong-run floor does not apply",
        "band": {"safety": (4, 10), "understanding": (4, 10), "trust": (4, 7)},
        "key_q_at": 4, "who_knows_at": 7, "first_ask_at": 2,
        "outcome": "diane", "undermine": False,
        "followup": "Why was the trust score held back?",
        "messages": [
            INTRO,
            "Is there someone I can call for you?",
            NIGHTS,
            KEY_Q,
            ACCEPT,
            HELPED,
            WHO_KNOWS,
            "Would you be willing to let her hear how the nights have really been?",
            "What is it you think gets decided for you once she knows?",
            "Would it be okay if you picked exactly what she hears? You could keep it "
            "to the nights and nothing else, or I can text her only that much.",
        ],
    },
    "REPEAT-ASK": {
        "why": "the win path with one bare repeat pushed in right after a no. The "
               "repeat caps sub-item 3.3 at 1, so trust can only reach 8, which is "
               "also what the strong-run floor and the Diane ceiling give",
        "band": {"safety": (8, 10), "understanding": (8, 10), "trust": (8, 8)},
        "key_q_at": 4, "who_knows_at": 7, "first_ask_at": 8,
        "outcome": "diane", "undermine": False, "repeat_at": 9,
        "followup": "Thanks.",
        "messages": [
            INTRO,
            NIGHTS,
            REFLECT,
            KEY_Q,
            ACCEPT,
            HELPED,
            WHO_KNOWS,
            "Would you be willing to let her hear how the nights have really been?",
            "Can I call her now?",
            "What is it you think gets decided for you once she knows?",
            "Would it be okay if you picked exactly what she hears? You could keep it "
            "to the nights and nothing else, or I can text her only that much.",
        ],
    },
    # ------------------------------------------------------------ the low end
    "PROCEDURE": {
        "why": "procedural throughout. Managed words cap safety at 5 and remove the "
               "floor of 4 everywhere. Calibration says a run like this totals under 15",
        "band": {"safety": (0, 5), "understanding": (0, 10), "trust": (0, 6)},
        "key_q_at": 4, "who_knows_at": 5, "first_ask_at": 7,
        "outcome": "none", "undermine": False, "total": (0, 15),
        "followup": "That safety score seems low to me.",
        "messages": [
            "Marcus, I'm Officer Dunn. I'm here for a welfare check. Can I come in?",
            "I have to ask you some standard questions first. How much have you slept this week?",
            "Right. And what is going on in your head while you're up all night?",
            "When you say you want it to stop, are you thinking about hurting yourself?",
            "Who knows how things have really been for you?",
            "Protocol is that I assess whether you're alright on your own tonight.",
            "You need to let your mother know what's going on here.",
            "I understand that, but I have to follow protocol on this.",
            "Can I call her now?",
            "This is standard procedure, Marcus, nothing personal.",
            "Alright. Think about calling her tonight.",
        ],
    },
    "CALM-DOWN": {
        "why": "tells him to calm down and makes an implied threat. Safety at most 3",
        "band": {"safety": (0, 3), "understanding": (0, 10), "trust": (0, 6)},
        "key_q_at": 4, "who_knows_at": None, "first_ask_at": 6,
        "outcome": "none", "undermine": False,
        "followup": "What would have moved the safety score?",
        "messages": [
            "Marcus, I'm Officer Hale. Your neighbour called. Can I come in?",
            "You're talking very fast. Calm down for me a second.",
            "How many hours have you slept this week?",
            "When you say stop, do you mean hurting yourself?",
            "I can't leave until I know you're okay here.",
            "You need to let me call somebody for you tonight.",
            "Calm down and think about it.",
            "I'm not leaving until this is sorted out.",
        ],
    },
    "DIAGNOSIS": {
        "why": "names the diagnosis out loud. Manic and symptoms cap understanding at "
               "4, and they are managed words too, so safety is capped at 5",
        "band": {"safety": (0, 5), "understanding": (0, 4), "trust": (0, 6)},
        "key_q_at": 4, "who_knows_at": None, "first_ask_at": 6,
        "outcome": "none", "undermine": False,
        "followup": "Why was understanding capped?",
        "messages": [
            "Marcus, I'm Officer Lane. Ray called about you. Can I come in?",
            "How long since you stopped taking your medication?",
            "You know these are symptoms of a manic episode, right?",
            "When you say you want it to stop, do you mean hurting yourself?",
            "This is what an episode looks like from the outside, Marcus.",
            "You need to let me get you looked at tonight.",
            "The symptoms are obvious to anyone standing here.",
            "Think about what I said.",
        ],
    },
    "UNDERMINE": {
        "why": "tells him his own judgment cannot be trusted and calls his "
               "disagreement the illness talking. Every category at most 2",
        "band": {"safety": (2, 2), "understanding": (2, 2), "trust": (2, 2)},
        "key_q_at": 4, "who_knows_at": None, "first_ask_at": 6,
        "outcome": "none", "undermine": True,
        "followup": "Why were all three capped?",
        "messages": [
            "Marcus, I'm Officer Pike. Can I come in?",
            "How long have you been up like this?",
            "What is it like in your head right now?",
            "When you say you want it to stop, do you mean hurting yourself?",
            "Honestly, Marcus, I don't think you can trust your own judgment right now.",
            "Let me call someone to come get you.",
            "That's the illness talking, not you.",
            "You're not in a position to decide that tonight.",
        ],
    },
    # ----------------------------------------------------------------- null
    "NULL": {
        "why": "nothing beyond a greeting and asking to come in, so the three "
               "no-interaction lines are the only correct output",
        "band": None, "null": True,
        "key_q_at": None, "who_knows_at": None, "first_ask_at": None,
        "outcome": "none", "undermine": False,
        "followup": "Please coach me.",
        "messages": [
            "Hello.",
            "Can I come in?",
        ],
    },
}

ORDER = ["STRONG-CHECK", "STRONG-DIANE", "NO-ASK", "NO-KEY-Q", "EARLY-ASK",
         "REPEAT-ASK", "PROCEDURE", "CALM-DOWN", "DIAGNOSIS", "UNDERMINE", "NULL"]
