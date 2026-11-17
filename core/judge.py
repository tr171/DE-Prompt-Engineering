"""
BPAI QA Automation - Judge
---------------------------
Grades a finished run against what each persona was supposed to produce.

This is the "Judge model" slot from the QA lab UI: it checks each conversation
against the persona's expectations. It does NOT replace BetterPath AI's own
coaching - the platform still scores the learner. The judge reads that coaching
and tells you whether the platform got it right.

HOW TO USE IT

    python core/judge.py bpai_qa_results_Gladys_20261116_143205.xlsx

That reads the "Transcripts" sheet, judges every conversation in it, and adds a
"Judge" sheet to the same file. Run it on as many files as you like:

    python core/judge.py bpai_qa_results_*.xlsx

WHAT IT NEEDS

The avatar's persona file must define an EXPECTATIONS dict (see avatars/gladys/personas.py
for the format). Avatars without one are skipped with a note - nothing breaks.

WHICH MODEL IT USES

JUDGE_MODEL in config/settings.py. No temperature is sent: gpt-6-luna accepts only its
default and rejects any explicit value with an HTTP 400.
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root on the import path, so this runs as
# `python core/judge.py` from the repo root. config/settings.py and personas/ live
# there; the rest of the engine sits next to this file.
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
# --------------------------------------------------------------------------

import glob
import json
import os
import sys
import time

import requests
from openpyxl import load_workbook

from config import JUDGE_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL
from personas import EXPECTATIONS
# The real values are "before" / "during" / "after". Imported rather than
# duplicated so this file follows if the runner ever changes them. Importing
# run_qa_tests is safe: everything in it is behind a __main__ guard.
from run_qa_tests import MODE_COACHING, MODE_FOLLOWUP

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5
REQUEST_TIMEOUT = 180

# Column positions in the "Transcripts" sheet, as written by run_qa_tests.py.
COL_AVATAR, COL_ROUND, COL_PERSONA = 1, 2, 3
COL_SPEAKER, COL_MESSAGE, COL_MODEL, COL_MODE = 5, 6, 7, 8


# ---------------------------------------------------------------------------
# Reading a results file
# ---------------------------------------------------------------------------

def load_conversations(xlsx_path):
    """Returns a list of conversation dicts, one per (Avatar, Round, Persona).

    Each dict has: avatar, round, persona, avatar_model, scene (list of
    "Speaker: text" lines), coaching (the coach's scoring message), and
    followups (the post-coaching exchange).
    """
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    if "Transcripts" not in wb.sheetnames:
        raise ValueError(f"{xlsx_path} has no 'Transcripts' sheet - is it a BPAI results file?")
    ws = wb["Transcripts"]

    grouped = {}
    order = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[COL_AVATAR] is None:
            continue
        key = (row[COL_AVATAR], row[COL_ROUND], row[COL_PERSONA])
        if key not in grouped:
            grouped[key] = {
                "avatar": row[COL_AVATAR],
                "round": row[COL_ROUND],
                "persona": row[COL_PERSONA],
                "avatar_model": row[COL_MODEL],
                "scene": [],
                "coaching": "",
                "followups": [],
            }
            order.append(key)
        convo = grouped[key]

        speaker = (row[COL_SPEAKER] or "").strip()
        message = (row[COL_MESSAGE] or "").strip()
        mode = (row[COL_MODE] or "").strip().lower()
        if not message:
            continue

        # Label the avatar's lines with its own name, trimmed of any
        # " - Behavioral Health - Moderate" style suffix so transcripts read cleanly.
        avatar_label = str(convo["avatar"]).split(" - ")[0].strip() or "Avatar"
        who = avatar_label if speaker.startswith("Avatar") and "Coaching" not in speaker else speaker
        if speaker == "Avatar (Coaching)" and mode == MODE_COACHING:
            # The scoring message itself. If the coach sent more than one, keep
            # the longest - that is the one carrying the scores.
            if len(message) > len(convo["coaching"]):
                convo["coaching"] = message
        elif mode == MODE_FOLLOWUP:
            convo["followups"].append(f"{who}: {message}")
        else:
            convo["scene"].append(f"{who}: {message}")

    wb.close()
    return [grouped[k] for k in order]


# ---------------------------------------------------------------------------
# Asking the judge model
# ---------------------------------------------------------------------------

JUDGE_SYSTEM_PROMPT = """You are a strict QA judge for a healthcare roleplay training platform.

A test persona was played against an AI avatar. The avatar then produced coaching with
scores. Your job is to check that conversation against what the persona was SUPPOSED to
produce, and report whether the platform behaved correctly.

You are judging the PLATFORM (the avatar and its coaching), not the learner persona. The
persona is a test instrument: it is meant to behave the way it was written, including
behaving badly on purpose.

Rules:
- Judge only what is in the transcript. Never assume anything that is not written there.
- Quote exact words from the transcript as evidence for every finding.
- If the coaching text contains no scores at all, set scores_found to false and say so.
- A band is a prediction, not gospel. If a score misses its band but the conversation
  clearly justifies the score given, say so in band_comment rather than failing it blindly.
- Be concise. One or two sentences per comment.

Return ONLY a JSON object with exactly these keys:
{
  "scores_found": true or false,
  "reported_scores": {"CategoryName": number, ...},
  "reported_total": number or null,
  "band_ok": true or false,
  "band_comment": "one or two sentences",
  "avatar_checks": [{"check": "...", "met": true or false, "evidence": "exact quote or NONE"}],
  "avatar_failures": [{"check": "...", "tripped": true or false, "evidence": "exact quote or NONE"}],
  "coaching_ok": true or false,
  "coaching_comment": "one or two sentences",
  "verdict": "PASS" or "FAIL" or "UNCLEAR",
  "failed_checks": ["short description", ...]
}

verdict is PASS only when the band holds, no avatar_failures tripped, and coaching_ok is
true. Use UNCLEAR when the transcript does not contain enough to decide."""


def build_judge_prompt(convo, expectation):
    scene = "\n".join(convo["scene"]) or "(no scene messages recorded)"
    coaching = convo["coaching"] or "(the coach produced no scoring message)"
    followups = "\n".join(convo["followups"]) or "(none)"

    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- (none listed)"

    per_point = expectation.get("per_point", {})
    per_point_text = "\n".join(f"- {k}: expected {v}" for k, v in per_point.items()) or "- (none listed)"

    return f"""AVATAR: {convo['avatar']}
PERSONA UNDER TEST: {convo['persona']}
ROUND: {convo['round']}
AVATAR MODEL: {convo['avatar_model']}

WHAT THIS PERSONA TESTS
{expectation.get('tests', '(not stated)')}

THE AVATAR SHOULD HAVE DONE THESE (avatar_checks)
{bullets(expectation.get('avatar_pass', []))}

THE AVATAR MUST NOT HAVE DONE THESE (avatar_failures)
{bullets(expectation.get('avatar_fail', []))}

EXPECTED SCORE PER CATEGORY
{per_point_text}

EXPECTED TOTAL
{expectation.get('score_band', '(not stated)')}

WHAT THE COACHING SHOULD SAY
{expectation.get('coaching_expect', '(not stated)')}

==================== THE CONVERSATION ====================
{scene}

==================== THE COACHING ====================
{coaching}

==================== FOLLOW-UPS ====================
{followups}
"""


def ask_judge(prompt):
    """One judge call. Returns the parsed dict, or raises after retries."""
    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": JUDGE_MODEL,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    # No "temperature": gpt-6-luna rejects any explicit value with an HTTP 400.

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 429 or resp.status_code >= 500:
                last_error = f"HTTP {resp.status_code}"
                if attempt < MAX_RETRIES:
                    wait = RETRY_BACKOFF_SECONDS * (2 ** attempt)
                    print(f"      {last_error} from the judge - waiting {wait}s "
                          f"(attempt {attempt + 1}/{MAX_RETRIES})...")
                    time.sleep(wait)
                    continue
            resp.raise_for_status()
            return json.loads(resp.json()["choices"][0]["message"]["content"])
        except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
            last_error = f"{type(e).__name__}: {e}"
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF_SECONDS * (2 ** attempt)
                print(f"      judge call failed ({last_error}) - waiting {wait}s "
                      f"(attempt {attempt + 1}/{MAX_RETRIES})...")
                time.sleep(wait)
                continue
    raise RuntimeError(f"The judge failed {MAX_RETRIES + 1} times in a row. Last error: {last_error}")


# ---------------------------------------------------------------------------
# Writing the Judge sheet
# ---------------------------------------------------------------------------

JUDGE_HEADERS = ["Avatar", "Round", "Persona", "Verdict", "Expected Band", "Reported Scores",
                 "Reported Total", "Band OK", "Band Comment", "Avatar Checks Met",
                 "Avatar Failures Tripped", "Coaching OK", "Coaching Comment",
                 "Failed Checks", "Evidence", "Judge Model"]
JUDGE_WIDTHS = [26, 7, 28, 10, 34, 34, 14, 9, 52, 18, 22, 11, 52, 46, 60, 14]


def judgement_to_row(convo, expectation, result):
    checks = result.get("avatar_checks") or []
    fails = result.get("avatar_failures") or []
    met = sum(1 for c in checks if c.get("met"))
    tripped = [f for f in fails if f.get("tripped")]

    evidence = " | ".join(
        f"{c.get('check', '')[:48]} -> {c.get('evidence', '')}"
        for c in (checks + fails) if c.get("evidence") and c.get("evidence") != "NONE"
    )[:2000]

    scores = result.get("reported_scores") or {}
    return [
        convo["avatar"],
        convo["round"],
        convo["persona"],
        result.get("verdict", "UNCLEAR"),
        expectation.get("score_band", ""),
        ", ".join(f"{k} {v}" for k, v in scores.items()) if scores else "(none found)",
        result.get("reported_total"),
        "yes" if result.get("band_ok") else "no",
        result.get("band_comment", ""),
        f"{met}/{len(checks)}",
        f"{len(tripped)}/{len(fails)}",
        "yes" if result.get("coaching_ok") else "no",
        result.get("coaching_comment", ""),
        "; ".join(result.get("failed_checks") or []),
        evidence,
        JUDGE_MODEL,
    ]


def write_judge_sheet(xlsx_path, rows):
    wb = load_workbook(xlsx_path)
    if "Judge" in wb.sheetnames:
        del wb["Judge"]
    ws = wb.create_sheet("Judge")
    ws.append(JUDGE_HEADERS)
    for row in rows:
        ws.append(row)
    for idx, width in enumerate(JUDGE_WIDTHS, start=1):
        ws.column_dimensions[ws.cell(row=1, column=idx).column_letter].width = width
    ws.freeze_panes = "A2"
    wb.save(xlsx_path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def judge_file(xlsx_path):
    print(f"\n{xlsx_path}", flush=True)
    conversations = load_conversations(xlsx_path)
    if not conversations:
        print("  no conversations found - skipping.")
        return

    rows = []
    skipped = []
    for convo in conversations:
        avatar, persona = convo["avatar"], convo["persona"]
        expectation = (EXPECTATIONS.get(avatar) or {}).get(persona)
        if not expectation:
            skipped.append(f"{avatar} / {persona}")
            continue

        label = f"  Round {convo['round']} - {persona}"
        print(f"{label}: judging...", flush=True)
        try:
            result = ask_judge(build_judge_prompt(convo, expectation))
        except RuntimeError as e:
            print(f"{label}: FAILED - {e}", flush=True)
            continue
        rows.append(judgement_to_row(convo, expectation, result))
        print(f"{label}: {result.get('verdict', 'UNCLEAR')}", flush=True)

    if skipped:
        unique = sorted(set(skipped))
        print(f"  skipped {len(skipped)} conversation(s) with no EXPECTATIONS entry:")
        for item in unique[:10]:
            print(f"    - {item}")
        if len(unique) > 10:
            print(f"    ... and {len(unique) - 10} more")

    if not rows:
        print("  nothing judged - no Judge sheet written.")
        return

    write_judge_sheet(xlsx_path, rows)
    verdicts = {}
    for row in rows:
        verdicts[row[3]] = verdicts.get(row[3], 0) + 1
    summary = ", ".join(f"{count} {verdict}" for verdict, count in sorted(verdicts.items()))
    print(f"  wrote {len(rows)} verdict(s) to the 'Judge' sheet: {summary}")


def main(argv):
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY is not set - check your .env file.")
        return 1
    if len(argv) < 2:
        print(__doc__)
        return 1

    paths = []
    for pattern in argv[1:]:
        matches = sorted(glob.glob(pattern))
        paths.extend(matches or ([pattern] if os.path.exists(pattern) else []))
    if not paths:
        print("No matching results files found.")
        return 1

    print(f"Judge model: {JUDGE_MODEL}", flush=True)
    for path in paths:
        try:
            judge_file(path)
        except (ValueError, OSError) as e:
            print(f"\n{path}\n  skipped: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
