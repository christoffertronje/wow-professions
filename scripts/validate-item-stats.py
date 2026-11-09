#!/usr/bin/env python3
"""Validate item-ID keyed Rare gear stats against the source recipe catalog."""
import json
from pathlib import Path
catalog=json.loads(Path("data/leatherworking.json").read_text(encoding="utf-8"))
items=json.loads(Path("data/item-stats.json").read_text(encoding="utf-8"))
rare=[r for r in catalog["recipes"] if r["quality"]=="rare"]
assert len(rare)==201
lookup=items["byItemId"]
assert len(lookup)==512
assert items["meta"]["epicItems"]==70 and items["meta"]["commonItems"]==28
uncommon=[r for r in catalog["recipes"] if r["quality"]=="uncommon"]
assert len(uncommon)==213
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
for r in uncommon:
    iid=str(r["itemId"])
    assert iid in lookup, f"Missing Uncommon item stats: {r['name']} (item {iid})"
    entry=lookup[iid]
    assert entry["itemId"]==int(iid), f"Uncommon item ID mismatch: {r['name']}"
    assert entry["recipeSpellId"]==r["id"], f"Uncommon recipe spell mismatch: {r['name']}"
    assert entry["name"]==r["name"], f"Uncommon item name mismatch: {r['name']}"
    assert entry["quality"]=="uncommon"
    assert isinstance(entry["itemLevel"],int) and entry["itemLevel"]>0
    assert entry["source"].get("itemPage")
    assert isinstance(entry["stats"],dict) and isinstance(entry["resistances"],dict)
    assert isinstance(entry["effects"],list) and isinstance(entry["tooltipLines"],list)
assert lookup["7348"].get("statReviewWarning"), "Fletcher's Gloves disputed Parry sign must remain flagged"
assert lookup["8197"].get("statReviewWarning"), "Nightscape Boots disputed stealth value must remain flagged"
assert all(x["armorType"] is None for x in lookup.values() if x["slot"]=="Back" and x["quality"]=="uncommon"), "Cloaks should not be an equipment armor material"
epic=[r for r in catalog["recipes"] if r["quality"]=="epic"]
assert len(epic)==70
for r in epic:
    iid=str(r["itemId"])
    assert iid in lookup, f"Missing Epic gear item {r['name']}"
    entry=lookup[iid]
    assert entry["itemId"]==int(iid) and entry["recipeSpellId"]==r["id"], f"Epic item ID mismatch: {r['name']}"
    assert entry["name"]==r["name"] and entry["quality"]=="epic", f"Epic identity or quality mismatch: {r['name']}"
    assert isinstance(entry["itemLevel"],int) and entry["itemLevel"]>0
    assert entry["source"]["itemPage"], f"Epic item source missing: {r['name']}"
# White/Common recipes include reagent items and other non-equipment.
# Require their true item tooltip and exact identity, NOT a fake gear slot.
common=[r for r in catalog["recipes"] if r["quality"]=="common"]
assert len(common)==28
for r in common:
    iid=str(r["itemId"])
    assert iid in lookup, f"Missing Common output tooltip {r['name']}"
    entry=lookup[iid]
    assert entry["itemId"]==int(iid) and entry["recipeSpellId"]==r["id"]
    assert entry["name"]==r["name"] and entry["quality"]=="common"
    assert isinstance(entry["itemLevel"],int) and entry["itemLevel"]>0
    assert entry["source"].get("itemPage")
assert all(entry["quality"]!="unknown" for entry in lookup.values())
# Epic-specific tooltips and reviewed exceptions must survive reimports.
assert "Restores 4 mana per 5 sec" in " ".join(lookup["20380"]["effects"]), "Dreamscale Breastplate lost its mana regeneration effect"
assert lookup["252603"].get("statReviewWarning"), "Red Dragonscale Leggings Intellect discrepancy must remain flagged"
assert lookup["252603"]["stats"].get("Intellect") in (31,32), "Unexpected Red Dragonscale Leggings Intellect value"
assert "252428" in lookup
x=lookup["252428"]
assert x["armor"]==45 and x["stats"].get("Strength")==4 and x["stats"].get("Agility")==4 and x["stats"].get("Stamina")==3
assert x["requiredCharacterLevel"]==12
# Specific regressions uncovered by comparing against client build 1.60.1.70862
assert "41 Ranged Attack Power" in " ".join(lookup["18508"]["effects"]), "Swift Flight Bracers lost its Equip bonus"
assert "Stamina value by 10" in " ".join(lookup["279258"]["effects"]), "Wild Leather Armor Kit lost +10 Stamina"
assert "items level 45 and above" in " ".join(lookup["279258"]["effects"]), "Wild Leather Armor Kit has wrong item level requirement"
assert lookup["18251"].get("statReviewWarning"), "Core Armor Kit has unresolved effect-data disagreement; retain warning"
# The optional second-source audit must never quietly claim unresolved
# spell-template placeholders are confirmed matches.
audit_path=Path("docs/rare-stats-second-source-audit.json")
if audit_path.exists():
    audit=json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["summary"]["totalRare"]==201
    assert audit["summary"]["source-unavailable"]==0
    assert audit["summary"]["disagreements"]==0, "Review second-source item stat conflicts before deployment"
    assert audit["summary"]["inconclusive"]==2, "Review changed spell-template coverage and update audit"
print("PASS: 512 item tooltip records joined by produced item ID, with attributes/effects and source provenance")
