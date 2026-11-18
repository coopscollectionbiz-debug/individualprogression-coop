"""Find IP scripts whose custom spell values the core inflates.

A script that casts a spell with its own value (CastCustomSpell, SPELLVALUE_BASE_POINTn) still
gets the spell's die roll and per-level points on top: SpellEffectInfo::CalcBaseValue turns the
value V into V - 1 when the effect has DieSides, and SpellEffectInfo::CalcValue then adds
1..DieSides and RealPointsPerLevel * caster level. So V lands anywhere in V .. V + DieSides - 1
(plus the per-level part). This lists every such call site and the effects it overrides.

Usage:
    python -I tools/ip-audit/die_rolls.py --dbc <Spell.dbc> [--spell-dbc-tsv <file>] [--markdown]

Spells the world DB adds in its spell_dbc table (IP's custom ones, such as 90008) aren't in
Spell.dbc. Export them once and pass the file with --spell-dbc-tsv:
    mysql -N acore_world -e "SELECT ID, Name_Lang_enUS, Effect_1, Effect_2, Effect_3,
      EffectDieSides_1, EffectDieSides_2, EffectDieSides_3, EffectRealPointsPerLevel_1,
      EffectRealPointsPerLevel_2, EffectRealPointsPerLevel_3, EffectBasePoints_1,
      EffectBasePoints_2, EffectBasePoints_3 FROM spell_dbc" > spell_dbc.tsv

Exit code 1 when an overridden effect can be inflated, 0 otherwise.
"""

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import spell_dbc  # noqa: E402

COMMENT_RE = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
CONST_RE = re.compile(r"\b(SPELL_[A-Z0-9_]+)\s*=\s*(\d+)")
CALL_RE = re.compile(r"CastCustomSpell\s*\(([^;]*?)\)\s*[;)=!]", re.S)
VALUE_RE = re.compile(r"SPELLVALUE_BASE_POINT([012])")
ADD_MOD_RE = re.compile(r"(\w+)\.AddSpellMod\s*\(\s*SPELLVALUE_BASE_POINT([012])")


def spell_constants(src):
    """Constant name -> {id: [files]} across every source and header."""
    consts = {}
    for path in src.rglob("*"):
        if path.suffix not in (".cpp", ".h"):
            continue
        for name, value in CONST_RE.findall(path.read_text(encoding="utf-8", errors="ignore")):
            consts.setdefault(name, {}).setdefault(int(value), []).append(path)
    return consts


def resolve(name, path, consts):
    """The id a constant has in this file, else its only id, else None (ambiguous or unknown)."""
    if name.isdigit():
        return int(name)
    ids = consts.get(name, {})
    local = [i for i, files in ids.items() if path in files]
    if len(local) == 1:
        return local[0]
    return next(iter(ids)) if len(ids) == 1 else None


def split_args(text):
    args, depth, cur = [], 0, ""
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args


def overridden_effects(args, text_before):
    """Which effect indexes a CastCustomSpell call sets, from its argument form."""
    # (spellId, SPELLVALUE_xxx, value, target, ...): only a BASE_POINT sets an effect's value.
    if len(args) > 1 and args[1].startswith("SPELLVALUE_"):
        m = VALUE_RE.search(args[1])
        return {int(m.group(1))} if m else set()
    # (spellId, CustomSpellValues, target, ...): the AddSpellMod calls on that variable before.
    if len(args) > 1 and re.fullmatch(r"\w+", args[1]) and args[1].startswith(("values", "val")):
        mods = {int(i) for var, i in ADD_MOD_RE.findall(text_before[-1500:]) if var == args[1]}
        if mods:
            return mods
    # (target, spellId, bp0, bp1, bp2, triggered, ...)
    if len(args) >= 5:
        return {i for i, bp in enumerate(args[2:5]) if bp not in ("0", "nullptr", "NULL")}
    return set()


def spell_argument(args):
    if len(args) > 1 and (args[1].startswith("SPELL_") or args[1].isdigit()):
        return args[1]
    return args[0]


def audit(src, spells):
    consts = spell_constants(src)
    rows = []
    for path in sorted(src.rglob("*.cpp")):
        raw = path.read_text(encoding="utf-8", errors="ignore")
        # Blank out comments (keeping newlines, so line numbers stay right): commented-out casts
        # don't run.
        text = COMMENT_RE.sub(lambda c: re.sub(r"[^\n]", " ", c.group(0)), raw)
        for m in CALL_RE.finditer(text):
            args = split_args(m.group(1))
            line = text.count("\n", 0, m.start()) + 1
            spell_name = spell_argument(args)
            spell_id = resolve(spell_name, path, consts)
            effects = overridden_effects(args, text[:m.start()])
            info = spells.get(spell_id) if spell_id else None
            inflated = []
            if info:
                for i in sorted(effects):
                    if info.die_sides[i] > 1 or info.points_per_level[i] != 0:
                        inflated.append((i, info.die_sides[i], info.points_per_level[i]))
            rows.append({
                "file": path.relative_to(src.parent).as_posix(),
                "line": line,
                "constant": spell_name,
                "spell_id": spell_id,
                "name": info.name if info else ("not in Spell.dbc" if spell_id else "unresolved"),
                "effects": sorted(effects),
                "die_sides": [info.die_sides[i] for i in sorted(effects)] if info else [],
                "inflated": inflated,
            })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dbc", required=True, help="path to Spell.dbc (3.3.5a)")
    parser.add_argument("--src", default=str(pathlib.Path(__file__).resolve().parents[2] / "src"))
    parser.add_argument("--spell-dbc-tsv", help="export of the world DB's spell_dbc table (see above)")
    parser.add_argument("--markdown", action="store_true", help="print a markdown table")
    opts = parser.parse_args()

    spells = spell_dbc.load(opts.dbc)
    if opts.spell_dbc_tsv:
        spells.update(spell_dbc.load_tsv(opts.spell_dbc_tsv))
    rows = audit(pathlib.Path(opts.src), spells)
    if opts.markdown:
        print("| File:line | Spell | Id | Name | Effects set | DieSides | Verdict |")
        print("|---|---|---|---|---|---|---|")
    for r in rows:
        if r["spell_id"] is None:
            verdict = "UNRESOLVED"
        elif r["name"] == "not in Spell.dbc":
            verdict = "NOT IN DBC"
        elif not r["effects"]:
            verdict = "no custom value"
        elif r["inflated"]:
            verdict = "die adds " + ", ".join(f"eff{i}: +0..{d - 1}" + (f" +{p}/lvl" if p else "")
                                              for i, d, p in r["inflated"])
        else:
            verdict = "exact"
        cells = [f"{r['file']}:{r['line']}", r["constant"], str(r["spell_id"]), r["name"],
                 ",".join(map(str, r["effects"])), ",".join(map(str, r["die_sides"])), verdict]
        print(("| " + " | ".join(cells) + " |") if opts.markdown else "\t".join(cells))
    inflated = sum(1 for r in rows if r["inflated"])
    unresolved = sum(1 for r in rows if r["spell_id"] is None)
    print(f"\n{len(rows)} call sites, {inflated} with a die roll on top, {unresolved} unresolved", file=sys.stderr)
    return 1 if inflated else 0


if __name__ == "__main__":
    sys.exit(main())
