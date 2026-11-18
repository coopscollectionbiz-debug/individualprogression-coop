# ip-audit

Checks over Individual Progression's scripts and data. Run them with the Python of your choice, isolated (`-I`), from the module root.

## die_rolls.py

Lists every `CastCustomSpell` call that passes its own value to a spell, and whether the core adds that spell's die roll on top.

- **What the core does:** `SpellEffectInfo::CalcBaseValue` stores a custom value V as V − 1 when the effect has `DieSides`. `CalcValue` then adds a roll of 1..`DieSides`, plus `RealPointsPerLevel` × caster level. So V lands in V .. V + `DieSides` − 1.
- **Exit code:** 1 when at least one call site has a die roll on top. That isn't always a bug: some scripts pick their value knowing the die is added (Korth'azz's Meteor, "14.5k to 13.5k").

```
python -I tools/ip-audit/die_rolls.py --dbc <Spell.dbc> --spell-dbc-tsv spell_dbc.tsv --markdown
```

**`--spell-dbc-tsv`** is an export of the world DB's `spell_dbc` table, which holds IP's custom spells such as 90008. The command that makes it is in the script's docstring.

**Fixing a site where the script states its final damage:**
1. Bind the spell to `spell_ip_exact_custom_damage` (`src/spellScripts/spellScripts.cpp`) with a new file in `data/sql/world/updates`.
2. Put its rollback in `rollback/world`.
3. Never edit `data/sql/*/base`.

## spell_dbc.py

Reads the `Spell.dbc` fields the checks need, using the 3.3.5a (build 12340) layout.
