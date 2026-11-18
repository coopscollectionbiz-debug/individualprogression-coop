"""Read the 3.3.5a Spell.dbc fields the IP audit needs.

Field indices are the 3.3.5a (build 12340) Spell.dbc layout: Id 0, Effect 71-73,
EffectDieSides 74-76, EffectRealPointsPerLevel 77-79 (float), EffectBasePoints 80-82,
SpellName[0] 136.
"""

import struct
from dataclasses import dataclass


@dataclass
class SpellEffects:
    spell_id: int
    name: str
    effect: tuple
    die_sides: tuple
    points_per_level: tuple
    base_points: tuple


def load(path):
    data = open(path, "rb").read()
    magic, records, fields, record_size, _ = struct.unpack("<4s4I", data[:20])
    if magic != b"WDBC":
        raise ValueError(f"{path} is not a WDBC file")
    body = data[20:20 + records * record_size]
    strings = data[20 + records * record_size:]

    def string_at(offset):
        end = strings.index(b"\0", offset)
        return strings[offset:end].decode("utf-8", "replace")

    spells = {}
    for i in range(records):
        ints = struct.unpack_from(f"<{fields}i", body, i * record_size)
        floats = struct.unpack_from(f"<{fields}f", body, i * record_size)
        spells[ints[0]] = SpellEffects(
            spell_id=ints[0],
            name=string_at(ints[136]),
            effect=ints[71:74],
            die_sides=ints[74:77],
            points_per_level=tuple(round(f, 4) for f in floats[77:80]),
            base_points=ints[80:83],
        )
    return spells


def load_tsv(path):
    """The world DB's spell_dbc rows, exported as die_rolls.py's docstring shows."""
    spells = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 14 or not cols[0].isdigit():
            continue
        spells[int(cols[0])] = SpellEffects(
            spell_id=int(cols[0]),
            name=cols[1],
            effect=tuple(int(c) for c in cols[2:5]),
            die_sides=tuple(int(c) for c in cols[5:8]),
            points_per_level=tuple(round(float(c), 4) for c in cols[8:11]),
            base_points=tuple(int(c) for c in cols[11:14]),
        )
    return spells
