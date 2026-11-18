"""Find spell, creature and gameobject IDs that IP's C++ names but the game data doesn't have.

The worldserver checks the IDs the database refers to at startup; it can't check the ones the
scripts hard-code. This reads every `SPELL_x = n`, `NPC_x = n` and `GO_x = n` constant in IP's
sources and looks each one up.

Usage:
    python -I tools/ip-audit/missing_ids.py --dbc <Spell.dbc> --spell-dbc-tsv <file>
        --creature-tsv <file> --gameobject-tsv <file> [--markdown]

The exports (tab-separated, no header):
    mysql -N acore_world -e "SELECT entry, name FROM creature_template" > creature.tsv
    mysql -N acore_world -e "SELECT entry, name FROM gameobject_template" > gameobject.tsv
and --spell-dbc-tsv as in die_rolls.py.

Exit code 1 when an ID is missing.
"""

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import spell_dbc  # noqa: E402

COMMENT_RE = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
CONST_RE = re.compile(r"\b((SPELL|NPC|GO|GOB|GAMEOBJECT)_[A-Z0-9_]+)\s*=\s*(\d+)")


def load_names(path):
    names = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        cols = line.rstrip("\n").split("\t")
        if cols and cols[0].isdigit():
            names[int(cols[0])] = cols[1] if len(cols) > 1 else ""
    return names


def constants(src):
    """(file, line, name, kind, id) for every constant, comments left out."""
    found = []
    for path in sorted(src.rglob("*")):
        if path.suffix not in (".cpp", ".h"):
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
        text = COMMENT_RE.sub(lambda c: re.sub(r"[^\n]", " ", c.group(0)), raw)
        for m in CONST_RE.finditer(text):
            kind = {"SPELL": "spell", "NPC": "creature"}.get(m.group(2), "gameobject")
            line = text.count("\n", 0, m.start()) + 1
            found.append((path.relative_to(src.parent).as_posix(), line, m.group(1), kind, int(m.group(3))))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dbc", required=True)
    parser.add_argument("--spell-dbc-tsv", required=True)
    parser.add_argument("--creature-tsv", required=True)
    parser.add_argument("--gameobject-tsv", required=True)
    parser.add_argument("--src", default=str(pathlib.Path(__file__).resolve().parents[2] / "src"))
    parser.add_argument("--markdown", action="store_true")
    opts = parser.parse_args()

    spells = spell_dbc.load(opts.dbc)
    spells.update(spell_dbc.load_tsv(opts.spell_dbc_tsv))
    known = {"spell": spells, "creature": load_names(opts.creature_tsv),
             "gameobject": load_names(opts.gameobject_tsv)}

    # Display and text IDs share the prefixes but aren't templates (GO_DISPLAY_ID_x, NPC_TEXT_x).
    def is_template(name):
        return "DISPLAY" not in name and "_TEXT" not in name

    rows = [c for c in constants(pathlib.Path(opts.src))
            if c[4] != 0 and is_template(c[2]) and c[4] not in known[c[3]]]
    if opts.markdown:
        print("| File:line | Constant | Kind | Id |")
        print("|---|---|---|---|")
    for file, line, name, kind, ident in rows:
        cells = [f"{file}:{line}", name, kind, str(ident)]
        print(("| " + " | ".join(cells) + " |") if opts.markdown else "\t".join(cells))
    total = len(constants(pathlib.Path(opts.src)))
    print(f"\n{total} constants, {len(rows)} missing", file=sys.stderr)
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
