"""
Senior care coaching standard (Nov 2026) - one checker for every avatar.

Every scored category gets exactly one coaching line:

    For <category>, you receive a score of <N> out of 10, because you did well by
    <the skill, in plain words>. You could be more effective by <one change, tied to
    the moment it was needed>, for example, "<a new line, 12 words or fewer>".

  - It never quotes the learner, and there is no separate "when you said..." clause.
  - The moment sits inside the change ("... when I told you the water scares me"):
    real, specific, told from the avatar's side, and short.
  - A 10 ends after the did-well sentence.
  - A score of 2 or lower uses "because I didn't hear you ..." instead of did-well.
  - Example lines move toward the goal; JD's example lines never give him a reason.

check_score_lines() is deterministic: a FAIL is the coaching breaking the standard.
"Moves toward the goal" and "the moment is real" need judgement, so they are only
checked loosely here (goal words, moment words found in the avatar's lines) and
reported as warnings.
"""

import re

LINE_RE = re.compile(
    r"For (?P<cat>[A-Z][A-Za-z &]+?), you receive a score of (?P<n>\d+) out of 10,?\s*"
    r"because (?P<rest>.*?)(?=\n|For [A-Z][A-Za-z &]+?, you receive a score of|$)", re.S)
DID_WELL_RE = re.compile(r"^you did well by (?P<skill>[^.\"“”]+)\.\s*(?P<after>.*)$", re.S | re.I)
LOW_RE = re.compile(r"^I didn'?t hear you (?P<skill>[^.\"“”]+)\.\s*(?P<after>.*)$", re.S | re.I)
CHANGE_RE = re.compile(
    r"^You could be more effective by (?P<change>[^\"“”]+?),\s*for example,\s*"
    r"[\"“](?P<line>[^\"“”]+)[\"”]\.?\s*$", re.S | re.I)
MOMENT_RE = re.compile(r"\b(?:when|after|as|once|the moment|each time|while) I\b(?P<m>[^,]*)", re.I)
OLD_WORDING = [
    (re.compile(r"\bwhen you said\b", re.I), "a 'when you said' clause"),
    (re.compile(r"\bTo improve\b", re.I), "the old 'To improve' tip"),
    (re.compile(r"\bdid well by saying\b", re.I), "the old 'did well by saying' quote"),
    (re.compile(r"\bwhen I said\s*[\"“]", re.I), "a quoted 'when I said \"...\"' moment"),
    (re.compile(r"\byou could have said\b", re.I), "the old 'you could have said' tip"),
]
COMMAND_RE = re.compile(r"\byou (?:need to|have to|must)\b|^\s*get up\b|\bit'?s time (?:for|to)\b", re.I)

MAX_LINE_WORDS = 12
MAX_MOMENT_WORDS = 10
QUOTE_NGRAM = 5  # this many consecutive learner words in a row counts as quoting them


def _norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]", " ", s.lower())).strip()


def _ngrams(text, n):
    w = _norm(text).split()
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def parse(coaching):
    """[(category, score, rest_after_because)] for every score line found."""
    return [(m["cat"].strip(), int(m["n"]), m["rest"].strip()) for m in LINE_RE.finditer(coaching)]


def check_line(cat, n, rest, learner_lines, avatar_lines, *, no_reason_re=None, goal_re=None,
               require_change=True):
    """One score line. Returns (fails, warns, parts)."""
    fails, warns, parts = [], [], {}
    label = f"{cat} ({n})"
    for rx, what in OLD_WORDING:
        if rx.search(rest):
            fails.append(f"{label}: uses {what}")

    if n <= 2:
        m = LOW_RE.match(rest)
        if not m:
            fails.append(f"{label}: a score of 2 or lower must say \"because I didn't hear you ...\": "
                         f"{rest[:80]!r}")
            return fails, warns, parts
    else:
        m = DID_WELL_RE.match(rest)
        if not m:
            fails.append(f"{label}: must say \"because you did well by <skill>.\" with no quote: "
                         f"{rest[:80]!r}")
            return fails, warns, parts
    parts["skill"], after = m["skill"].strip(), m["after"].strip()

    learner_grams = set().union(*(_ngrams(l, QUOTE_NGRAM) for l in learner_lines)) if learner_lines else set()
    if _ngrams(parts["skill"], QUOTE_NGRAM) & learner_grams:
        fails.append(f"{label}: the did-well skill quotes the learner: {parts['skill']!r}")

    if n == 10 or (not require_change and not after):
        if n == 10 and after:
            fails.append(f"{label}: a 10 must end after the did-well sentence, found {after[:60]!r}")
        return fails, warns, parts

    c = CHANGE_RE.match(after)
    if not c:
        fails.append(f"{label}: needs \"You could be more effective by <change>, for example, "
                     f"\\\"<line>\\\".\" got {after[:90]!r}")
        return fails, warns, parts
    change, line = c["change"].strip(), c["line"].strip()
    parts.update(change=change, line=line)

    mm = MOMENT_RE.search(change)
    if not mm:
        fails.append(f"{label}: the change has no moment told from my side (\"when I ...\"): {change!r}")
    else:
        moment = mm.group(0)
        parts["moment"] = moment
        if len(moment.split()) > MAX_MOMENT_WORDS:
            fails.append(f"{label}: the moment is {len(moment.split())} words (max {MAX_MOMENT_WORDS}): "
                         f"{moment!r}")
        # A real moment should share a content word with something the avatar said.
        content = {w for w in _norm(mm["m"]).split() if len(w) > 3} - {
            "said", "told", "talked", "asked", "about", "first", "started", "began", "seemed",
            "your", "that", "this", "with", "what", "felt", "kept", "again", "still"}
        avatar_words = set(_norm(" ".join(avatar_lines)).split())
        if content and avatar_lines and not (content & avatar_words):
            warns.append(f"{label}: no word of the moment appears in any avatar line - check it is "
                         f"real: {moment!r}")
    if _ngrams(change, QUOTE_NGRAM) & learner_grams:
        fails.append(f"{label}: the change quotes the learner: {change!r}")

    wc = len(line.split())
    if wc > MAX_LINE_WORDS:
        fails.append(f"{label}: example line is {wc} words (max {MAX_LINE_WORDS}): {line!r}")
    if COMMAND_RE.search(line):
        fails.append(f"{label}: example line is a command: {line!r}")
    if _ngrams(line, QUOTE_NGRAM) & learner_grams:
        warns.append(f"{label}: example line repeats the learner's own words, so it is not new: {line!r}")
    if no_reason_re is not None and no_reason_re.search(line):
        fails.append(f"{label}: example line gives the avatar a reason: {line!r}")
    if goal_re is not None and not goal_re.search(line):
        warns.append(f"{label}: example line does not obviously move toward the goal: {line!r}")
    return fails, warns, parts


def check_score_lines(coaching, categories, learner_lines, avatar_lines, *,
                      no_reason_re=None, goal_re=None, require_change=True):
    """require_change=False lets a line below 10 end after its reason (e.g. the
    'we never talked' coaching, where there is no moment to tie a change to)."""
    # Whole coaching. Returns (fails, warns, {category: (score, parts)}).
    fails, warns, found = [], [], {}
    lines = parse(coaching)
    for cat, n, rest in lines:
        f, w, p = check_line(cat, n, rest, learner_lines, avatar_lines, no_reason_re=no_reason_re,
                             goal_re=goal_re, require_change=require_change)
        fails += f
        warns += w
        found[cat] = (n, p)
    missing = [c for c in categories if c not in found]
    if missing:
        fails.append(f"no score line in the standard wording for: {', '.join(missing)}")
    examples = [p["line"] for _, p in found.values() if p.get("line")]
    if len({_norm(e) for e in examples}) < len(examples):
        fails.append("two categories share the same example line")
    return fails, warns, found


# ---------------------------------------------------------------------------
# Command line: check a QA Lab "Download Excel" export against the standard only.
#     python core/coaching_standard.py <export.xlsx> [Category,Category,...]
# Works for any avatar, whatever its recap or scoring layout, because it reads
# only the score lines and the follow-up answers.
# ---------------------------------------------------------------------------
def _main(argv):
    import collections
    from openpyxl import load_workbook
    path = argv[0]
    ws = load_workbook(path, read_only=True, data_only=True)["Transcripts"]
    conv = collections.OrderedDict()
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r and r[3] is not None:
            conv.setdefault((r[3], r[2]), []).append(r)
    total_ok, kinds, n_lines = 0, collections.Counter(), 0
    fu = collections.Counter()
    for (persona, rnd), rows in conv.items():
        coach = max((str(r[6] or "") for r in rows if r[8] == "during" and "Coaching" in str(r[5])),
                    key=len, default="")
        learner = [str(r[6]) for r in rows if r[5] == "You" and r[8] == "before"]
        avatar = [str(r[6]) for r in rows if r[5] == "Avatar" and r[8] == "before"]
        cats = argv[1].split(",") if len(argv) > 1 else [c for c, _, _ in parse(coach)] or ["(none)"]
        fails, warns, found = check_score_lines(coach, cats, learner, avatar)
        n_lines += len(found)
        total_ok += not fails
        scores = "/".join(str(found[c][0]) if c in found else "-" for c in cats)
        print(f"{'PASS' if not fails else 'FAIL'}  {persona:16} R{rnd}  {scores}")
        for f in fails:
            print(f"        {f}")
            kinds[re.sub(r"^[^:]*\(\d+\): ", "", f).split(":")[0][:60]] += 1
        for r in rows:
            if r[8] == "after" and "Coaching" in str(r[5]):
                a = str(r[6] or "")
                fu["follow-ups"] += 1
                fu["quote the learner / old tip wording"] += bool(
                    any(rx.search(a) for rx, _ in OLD_WORDING))
                fu["'My coaching is above'"] += "My coaching is above" in a
    print(f"\n{total_ok}/{len(conv)} conversations follow the standard ({n_lines} score lines)")
    for k, v in kinds.most_common():
        print(f"  {v:3}  {k}")
    print("  " + ", ".join(f"{k}: {v}" for k, v in fu.items()))


if __name__ == "__main__":
    import sys
    _main(sys.argv[1:])
