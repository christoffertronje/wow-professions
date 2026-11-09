#!/usr/bin/env python3
"""Validate item-ID keyed Rare gear stats against the source recipe catalog."""
import json
from pathlib import Path
catalog=json.loads(Path("data/leatherworking.json").read_text(encoding="utf-8"))
items=json.loads(Path("data/item-stats.json").read_text(encoding="utf-8"))
rare=[r for r in catalog["recipes"] if r["quality"]=="rare"]
assert len(rare)==201
lookup=items["byItemId"]
assert len(lookup)==201
for r in rare:
    iid=str(r["itemId"])
    assert iid in lookup, f"Missing rare item stats: {r['name']} (item {iid})"
    entry=lookup[iid]
    assert entry["itemId"]==int(iid)
    assert entry["recipeSpellId"]==r["id"], f"Wrong item ID joined to recipe: {r['name']}"
    assert entry["name"]==r["name"], f"Tooltip name changed: {r['name']}"
    assert entry["quality"]=="rare"
    assert isinstance(entry["itemLevel"],int) and entry["itemLevel"]>0
    assert entry["source"]["itemPage"], f"No source link for {r['name']}"
    for name,value in entry["stats"].items():
        assert isinstance(value,int)
    for name,value in entry["resistances"].items():
        assert isinstance(value,int)
    for effect in entry["effects"]:
        assert isinstance(effect,str) and effect.strip()
    assert all(isinstance(line,str) and line.strip() for line in entry["tooltipLines"])
assert "252428" in lookup
x=lookup["252428"]
assert x["armor"]==45 and x["stats"].get("Strength")==4 and x["stats"].get("Agility")==4 and x["stats"].get("Stamina")==3
assert x["requiredCharacterLevel"]==12
print("PASS: 201 rare item records joined by produced item ID, with attributes/effects and source provenance")
