"""
Better Path AI QA - Persona File Checker
----------------------------------------
Checks every avatars/*/personas.py against the standard layout
(avatars/_TEMPLATE/personas.py) and config/settings.py, and prints what to fix. It never
calls OpenAI or Better Path AI and never changes any file.

Usage (run from the repo root):
    python core/check_personas.py              check every avatar file
    python core/check_personas.py ross         check one avatar (its folder name)

ERRORS stop an avatar from running correctly. WARNINGS are things to fix
when you next work on that avatar (most are Batch 2 work).
"""

# --- repo bootstrap -------------------------------------------------------
# Puts the repo root on the import path, so this runs as
# `python core/check_personas.py` from the repo root. config/settings.py and personas/ live
# there; the rest of the engine sits next to this file.
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
# --------------------------------------------------------------------------

import re
import sys

import personas

STANDARD = ["High Learner", "Medium Learner", "Low Learner", "Trap Test"]
COACH_PHRASE = re.compile(r"please\W+coach\W+me", re.IGNORECASE)
AFTER_HEAD = re.compile(r"(?im)^[ \t]*(?:-[ \t]*)?after coaching\b[^\n]*")
GATED = re.compile(r"(?i)after coaching \(only after")
# Words that mean rubric or best-practice text is sitting in the learner's context.
RUBRIC_WORDS = re.compile(
    r"(?i)(assessed on|assessment (scoring )?categor|assessment criteria|scoring categor|"
    r"\b\d+\s*pts\b|\(\d+\s*points?\)|excellent performance|best practices|more effective|less effective)")
# Personas that describe a skill level instead of behavior drift between rounds.
VAGUE_WORDS = re.compile(r"(?i)\b(should resemble|performance should|demonstrate (average|poor) performance)\b")


def load_scenarios():
    try:
        from config import SCENARIOS
        return SCENARIOS
    except Exception as e:  # config/settings.py missing or broken - still check the files
        print(f"(Could not read config/settings.py SCENARIOS: {e.__class__.__name__}. Skipping the name check.)\n")
        return None


def check_module(folder, scenarios):
    errors, warnings = [], []
    mod = personas.MODULES[folder]

    if not hasattr(mod, "PERSONAS"):
        return [f"no PERSONAS dict - the tool skips this file"], []

    for key in mod.PERSONAS:
        if scenarios is not None and key not in scenarios:
            errors.append(f'avatar name "{key}" is not in config/settings.py SCENARIOS, so it will never run. '
                          f"Use exactly the same name in both places.")

    for attr in ("RUN_SET", "LIBRARY", "RUN_SETS", "SHARED_CONTEXT", "EXPECTATIONS"):
        if not hasattr(mod, attr):
            errors.append(f"missing {attr} - copy the layout from avatars/_TEMPLATE/personas.py")
    if errors:
        return errors, warnings

    lib, sets = mod.LIBRARY, mod.RUN_SETS
    for name in ("standard", "probes", "all", "quick"):
        if name not in sets:
            warnings.append(f'no "{name}" run set')
    rs = mod.RUN_SET
    if isinstance(rs, str) and rs not in sets:
        errors.append(f'RUN_SET = "{rs}" is not one of the run sets: {", ".join(sets)}')
    elif isinstance(rs, str) and rs != "standard":
        warnings.append(f'RUN_SET is "{rs}" - set it back to "standard" when you finish, so the next run is the usual one')
    if sets.get("standard") != STANDARD:
        warnings.append(f"standard run set should be exactly: {', '.join(STANDARD)}")

    for set_name, names in sets.items():
        missing = [n for n in names if n not in lib]
        if missing:
            errors.append(f'run set "{set_name}" names personas not in LIBRARY: {", ".join(missing)}')

    if "Probe - Null" not in lib:
        warnings.append('no "Probe - Null" (every avatar needs a null test)')

    m = RUBRIC_WORDS.search(mod.SHARED_CONTEXT)
    if m:
        errors.append(f'SHARED_CONTEXT contains rubric or best-practice text ("{m.group(0)}"). '
                      "Move it to REFERENCE_RUBRIC; the learner AI treats it as instructions.")
    if COACH_PHRASE.search(mod.SHARED_CONTEXT):
        warnings.append("SHARED_CONTEXT mentions \"please coach me\" - that belongs in each persona's when-line")

    for name, prompt in lib.items():
        where = f'"{name}"'
        if prompt is None:
            warnings.append(f"{where} is not written yet (the runner skips it)")
            continue
        if name not in STANDARD and not name.startswith("Probe - "):
            warnings.append(f'{where} - name probes "Probe - <Behavior>"')
        if not COACH_PHRASE.search(prompt):
            warnings.append(f'{where} has no "Please coach me" when-line - the session only ends when the '
                            "learner AI decides the objective is reached, or at the turn cap")
        heads = AFTER_HEAD.findall(prompt)
        if not heads:
            warnings.append(f"{where} has no After coaching section - follow-ups use the generic prompt only")
        elif not any(GATED.search(h) for h in heads):
            warnings.append(f"{where} After coaching section is not gated on the score line")
        if name in STANDARD[1:] or name.startswith("Probe - "):
            m = VAGUE_WORDS.search(prompt.split("After coaching")[0])
            if m and name != "Probe - Null":
                warnings.append(f'{where} describes a skill level ("{m.group(0)}") instead of behavior - rewrite with firm limits')

    exp = getattr(mod, "EXPECTATIONS", {})
    missing_exp = [n for n in lib if n not in exp]
    if missing_exp:
        warnings.append(f"EXPECTATIONS has no entry for: {', '.join(missing_exp)}")
    todo = [n for n, e in exp.items() if "TODO" in str(e.get("score_band", ""))]
    if todo:
        warnings.append(f"no expected scores yet (EXPECTATIONS score_band) for: {', '.join(todo)}")

    return errors, warnings


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    scenarios = load_scenarios()
    names = list(personas.MODULES)
    if only:
        names = [n for n in names if n.lower() == only.lower()]
        if not names:
            print(f"No avatars/{only}/personas.py found.")
            sys.exit(1)

    total_errors = 0
    seen_keys = set()
    for folder in sorted(names, key=str.lower):
        try:
            errors, warnings = check_module(folder, scenarios)
        except Exception as e:
            errors, warnings = [f"could not load: {e.__class__.__name__}: {e}"], []
        mod = personas.MODULES.get(folder)
        seen_keys.update(getattr(mod, "PERSONAS", {}).keys())
        status = "OK" if not errors and not warnings else ("ERRORS" if errors else "warnings")
        print(f"{personas.path_for(folder)} - {status}")
        for e in errors:
            print(f"   ERROR:   {e}")
        for w in warnings:
            print(f"   warning: {w}")
        total_errors += len(errors)

    if scenarios is not None and not only:
        no_file = [n for n in scenarios if n not in seen_keys]
        if no_file:
            print("\nIn config/settings.py SCENARIOS but no persona file uses that exact name:")
            for n in no_file:
                print(f"   {n}")

    print(f"\n{total_errors} error(s).")
    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
