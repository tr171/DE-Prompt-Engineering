"""
BPAI QA Automation - OpenAI Connection Test
------------------------------------------------
A quick, standalone check that your OPENAI_* settings in config/settings.py
actually work, before running the full tool. Sends one trivial request
and prints either a success message or a clear explanation of what's
wrong.

Usage:
    python core/test_openai_connection.py
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root on the import path, so this runs as
# `python core/test_openai_connection.py` from the repo root. config/settings.py and personas/ live
# there; the rest of the engine sits next to this file.
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
# --------------------------------------------------------------------------

import sys

import requests

from config import OPENAI_API_KEY, OPENAI_BASE_URL, USER_MODEL as OPENAI_MODEL


def main():
    if not OPENAI_API_KEY or not OPENAI_MODEL:
        print("ERROR: OPENAI_API_KEY and/or USER_MODEL is still blank in config/settings.py.")
        sys.exit(1)

    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": "Reply with just the word: OK"}],
        # gpt-6-luna and other newer models reject "max_tokens" outright.
        # "max_completion_tokens" is accepted by gpt-4o and gpt-5.x alike.
        "max_completion_tokens": 16,
    }

    print(f"Testing connection with model '{OPENAI_MODEL}'...")
    print(f"URL: {url}\n")

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
    except requests.ConnectionError as e:
        print(f"FAILED: couldn't reach the endpoint at all ({e}).")
        print("Double check OPENAI_BASE_URL is correct and complete, including https://")
        sys.exit(1)

    if resp.status_code == 200:
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]
        print(f"SUCCESS! The model replied: {reply!r}")
        print("\nYour OpenAI settings in config/settings.py are working. You're good to move on to Step 6.")
    elif resp.status_code == 401:
        print("FAILED (401 Unauthorized): OPENAI_API_KEY is wrong, expired, or missing.")
        print("Double check what you pasted into config/settings.py against what you were given.")
    elif resp.status_code == 404:
        print(f"FAILED (404 Not Found): the model '{OPENAI_MODEL}' wasn't found, or OPENAI_BASE_URL has a typo.")
        print("Double check the model name your team gave you, and the base URL.")
    elif resp.status_code == 429:
        print("FAILED (429): rate limited or the account is out of quota/credits.")
        print("This isn't something wrong with your config - check with your team about usage limits.")
    else:
        print(f"FAILED ({resp.status_code}): {resp.text}")

    if resp.status_code != 200:
        sys.exit(1)


if __name__ == "__main__":
    main()
