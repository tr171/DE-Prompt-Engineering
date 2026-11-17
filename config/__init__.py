"""
Your settings and credentials live in this folder.

    config/settings.example.py   the template - tracked in git, safe to share
    config/settings.py           YOUR copy, with your real token - never committed

To set up, copy the example to settings.py and fill in two things (GUIDE.md
Steps 3-4):

    HEADERS["authorization"]   your own Better Path AI token
    USER_ID                    the numeric user id that token belongs to

Your OpenAI key goes in .env at the top of the repo, not here (GUIDE.md Step 5).

This file exists only so the rest of the tool can keep saying

    from config import SCENARIOS, HEADERS, USER_ID

without caring how the folder is arranged. You should never need to edit it.
"""

try:
    from .settings import *          # noqa: F401,F403  - re-export every setting
except ModuleNotFoundError as exc:
    if exc.name and exc.name.rsplit(".", 1)[-1] == "settings":
        raise SystemExit(
            "\nconfig/settings.py is missing.\n\n"
            "Copy config/settings.example.py to config/settings.py, then fill in your\n"
            "own Better Path AI token and user id. See GUIDE.md Steps 3-4.\n\n"
            "    cp config/settings.example.py config/settings.py\n"
        ) from None
    raise
