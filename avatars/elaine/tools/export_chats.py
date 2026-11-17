"""
Turns an anchor run's Transcripts sheet into a readable chat log.

    python avatars/elaine/tools/export_chats.py elaine_anchors_<timestamp>.xlsx

Writes a .md next to it with every conversation in full - each caregiver line,
each of Elaine's replies, and the coaching she gave at the end - plus the
target score and what she actually scored. Readable on its own, and fine to
forward.
"""
import sys
from openpyxl import load_workbook

path = sys.argv[1]
wb = load_workbook(path, data_only=True)
anchors = {}
for r in wb["Anchors"].iter_rows(min_row=2, values_only=True):
    anchors[(r[0], r[1])] = r

convos = {}
for r in wb["Transcripts"].iter_rows(min_row=2, values_only=True):
    convos.setdefault((r[3], r[2]), []).append(r)

out = [f"# Elaine V2 — anchor run chat log\n",
       f"Source: `{path}`. Every conversation in full, with the score it was ",
       "built to produce and the score the avatar actually gave.\n"]

for key, rows in convos.items():
    name, rnd = key
    a = anchors.get(key)
    out.append(f"\n---\n\n## {name}" + (f"  (round {rnd})" if rnd and rnd != 1 else ""))
    if a:
        out.append(f"\n**Category:** {a[2]}  |  **Built to score:** {a[3]}  |  "
                   f"**Avatar gave:** {a[4]}  |  **Target met:** {a[5]}")
        out.append(f"\n**What the script forces:** {a[10]}")
        if a[9]:
            out.append(f"\n**Other categories this run:** {a[9]}")
    out.append("\n### Conversation\n")
    for r in rows:
        sp, msg, mode = r[5], str(r[6] or ""), r[8]
        if mode == "during" and sp.startswith("Avatar"):
            out.append("\n### Coaching given\n")
            out.append("\n".join("> " + l if l.strip() else ">" for l in msg.splitlines()))
        elif mode == "during":
            out.append(f"\n**Caregiver:** {msg}")
        elif mode == "opening":
            out.append(f"**Elaine (opening):** {msg}\n")
        else:
            who = "Caregiver" if sp == "You" else "Elaine"
            out.append(f"**{who}:** {msg}\n")

fn = path.rsplit(".", 1)[0] + "_chats.md"
open(fn, "w", encoding="utf-8").write("\n".join(out))
print(f"wrote {fn}")
