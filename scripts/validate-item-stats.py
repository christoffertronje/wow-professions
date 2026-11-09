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
assert items["meta"]["epicItems"]==70 and items["meta"]["commonItems"]==27 and items["meta"]["uncommonItems"]==214
uncommon=[r for r in catalog["recipes"] if r["quality"]=="uncommon"]
assert len(uncommon)==214
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
# Reviewed highest-risk client-source discrepancies. Keep the exact data
# and display the source uncertainty until verified in live gameplay.
assert lookup["7348"]["effects"]==["Equip: Increases your parry by -15."]
assert "+14 Critical Strike" in lookup["7348"]["otherTooltipLines"], "Fletcher's Gloves crit rating missing"
assert lookup["7348"].get("statReviewWarning"), "Fletcher's Gloves disputed Parry sign must remain flagged"
assert lookup["8197"].get("statReviewWarning"), "Nightscape Boots disputed stealth value must remain flagged"
assert "stealth level by 1.2" in " ".join(lookup["8197"]["effects"])
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
assert len(common)==27
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
assert lookup["252603"]["stats"].get("Intellect")==32, "Reviewed newer-client Intellect value lost"
assert lookup["2314"]["quality"]=="uncommon" and lookup["2314"]["armor"]==84
assert lookup["2314"]["stats"]=={"Stamina":2,"Spirit":7}
assert lookup["2314"]["binding"]=="BoE"
assert all(entry["stats"]=={} and entry["armor"] is None for entry in lookup.values() if entry["name"].endswith("Armor Kit")), "Armor-kit target enchantments must not render as wearable stats"
assert "252428" in lookup
x=lookup["252428"]
assert x["armor"]==45 and x["stats"].get("Strength")==4 and x["stats"].get("Agility")==4 and x["stats"].get("Stamina")==3
assert x["requiredCharacterLevel"]==12
# Specific regressions uncovered by comparing against client build 1.60.1.70862
assert "41 Ranged Attack Power" in " ".join(lookup["18508"]["effects"]), "Swift Flight Bracers lost its Equip bonus"
assert "Stamina value by 10" in " ".join(lookup["279258"]["effects"]), "Wild Leather Armor Kit lost +10 Stamina"
assert "items level 45 and above" in " ".join(lookup["279258"]["effects"]), "Wild Leather Armor Kit has wrong item level requirement"
assert lookup["18251"].get("statReviewWarning"), "Core Armor Kit has unresolved effect-data disagreement; retain warning"
assert "defense value of an item worn on the chest, legs, hands or feet by 3" in " ".join(lookup["18251"]["effects"])
assert "items level 45 and above" in " ".join(lookup["18251"]["effects"])
# The optional second-source audit must never quietly claim unresolved
# spell-template placeholders are confirmed matches.
audit_path=Path("docs/rare-stats-second-source-audit.json")
if audit_path.exists():
    audit=json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["summary"]["totalRare"]==201
    assert audit["summary"]["source-unavailable"]==0
    assert audit["summary"]["disagreements"]==0, "Review second-source item stat conflicts before deployment"
    assert audit["summary"]["inconclusive"]==2, "Review changed spell-template coverage and update audit"
# Remaining effect text differences reconciled against newer client sources.
for iid in ("2304","2313","18662"):
    assert "1 Sec Cooldown" in " ".join(lookup[iid]["effects"]), f"Missing newer client cooldown on {iid}"
for iid in ("279941","279945","279978"):
    assert "All camping features share a cooldown of 1 hour." in " ".join(lookup[iid]["effects"]), f"Missing shared camping cooldown on {iid}"
assert "May be placed over a Camp Tent" in " ".join(lookup["279941"]["effects"])
assert "May be placed over a Camp Tent" in " ".join(lookup["279945"]["effects"])
assert "Requires a Campfire nearby" in " ".join(lookup["279978"]["effects"])
assert not lookup["7284"].get("statReviewWarning"), "Red Whelp Gloves confirmed tooltip should not remain flagged"
assert lookup["7284"].get("reviewedCorrection",{}).get("source"), "Red Whelp Gloves confirmation evidence missing"
assert "5% chance of dealing 30 to 50 Fire damage" in " ".join(lookup["7284"]["effects"])
assert "Proc chance: 10%" not in " ".join(lookup["7284"]["effects"]), "Unverified proc metadata leaked into tooltip"
assert "5% chance of being put to sleep" in " ".join(lookup["7375"]["effects"])
assert "Proc chance:" not in " ".join(lookup["7375"]["effects"])
# Forever client spell placeholders (0c1/0c2/0cim) were NOT literal zero
# values. Guard all six upgraded Mystic / Forceful armor-kit bonuses.
armor_kit_bonus={
    "252452":("Spell Power",4,24,15),
    "252453":("Attack Power",6,24,15),
    "252462":("Spell Power",5,32,25),
    "252463":("Attack Power",8,32,25),
    "252487":("Spell Power",6,40,35),
    "252488":("Attack Power",10,40,35),
}
for iid,(stat,bonus,armor,minlevel) in armor_kit_bonus.items():
    item=lookup[iid]
    text=" ".join(item["effects"])
    assert f"{stat} value by {bonus}" in text, f"Wrong power bonus for {item['name']}"
    assert f"armor value by {armor}" in text, f"Wrong armor bonus for {item['name']}"
    assert f"items level {minlevel} and above" in text, f"Wrong target item level for {item['name']}"
    assert item["armor"] is None and not item["stats"], f"Kit bonus treated as equipped item stats: {item['name']}"
    assert not any(x in text for x in ("0c1","0c2","0cim","value by 75")), f"Unresolved spell placeholder leaked: {item['name']}"
    assert item.get("reviewedCorrection",{}).get("source"), f"Lost reviewed correction evidence: {item['name']}"
print("PASS: 512 item tooltip records joined by produced item ID, with attributes/effects and source provenance")
