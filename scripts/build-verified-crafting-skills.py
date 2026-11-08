#!/usr/bin/env python3
"""Build a provenance-aware, minimum-crafting-skill lookup.

Primary source is the GuildLoot Forever table's explicit 'Skill' column.
Its 369 uniquely matched spell IDs were previously audited and saved in
docs/forever-skill-crosscheck.json. Do NOT consume skill-up thresholds.
Local checked corrections override the reference with a clear source.
"""
import json
from pathlib import Path
REPORT=Path("docs/forever-skill-crosscheck.json")
CORRECTIONS=Path("data/verified-skill-corrections.json")
OUT=Path("data/verified-crafting-skills.json")
data=json.loads(REPORT.read_text(encoding="utf-8"))
assert data["sourceRows"]>=400 and data["matchedCount"]>=350
records={}
for row in data["matches"]:
    spell=str(row["spellId"])
    required=row["craftingSkillReference"]
    if not isinstance(required,int) or not 1<=required<=450:
        raise ValueError(f"Invalid requirement for {spell}: {required}")
    if spell in records:
        raise ValueError(f"Duplicate spell ID: {spell}")
    records[spell]={"required":required,"source":"guildloot-forever-required-skill","reference":data["source"]}

overrides=json.loads(CORRECTIONS.read_text(encoding="utf-8"))
for spell,entry in overrides.items():
    if spell=="description":continue
    required=entry["required"]
    if not isinstance(required,int) or not 1<=required<=450:raise ValueError(spell)
    records[spell]={"required":required,"source":"checked-forever-correction","reference":entry["referenceUrls"][0]}
# Supplement with explicitly labelled 'Requires Leatherworking N' facts.
# Conflicting values are excluded entirely until independently resolved.
extra_path=Path("data/questing-crafting-skills.json")
if extra_path.exists():
    extra=json.loads(extra_path.read_text(encoding="utf-8"))
    conflict_ids={str(row["spellId"]) for row in extra.get("conflicts",[])}
    for sid in conflict_ids:
        # Do not imply a disputed value is reliable.
        records.pop(sid,None)
    for sid,value in extra["skillsBySpellId"].items():
        if sid in conflict_ids:continue
        if sid in records:
            if records[sid]["required"]!=value["required"]:
                raise ValueError(f"Unrecorded source disagreement for {sid}")
        else:
            records[sid]=value
# Also accept vendor/drop pattern requirements where two separate sources
# agree on the minimum skill. Never infer a trainer minimum from skill-up bands.
pattern_file=Path("data/wiki-pattern-crafting-skills.json")
if pattern_file.exists():
    pattern_data=json.loads(pattern_file.read_text(encoding="utf-8"))
    for sid,value in pattern_data["skillsBySpellId"].items():
        if sid in records and records[sid]["required"] != value["required"]:
            raise ValueError(f"Wiki pattern mismatch for spell {sid}")
        if sid not in records:
            records[sid]=value
# Unique named Forever recipes corroborated by TWO separate recipe tables.
# WCLBox has craft/yellow/green/gray; only first is accepted, checked against Wiki.
wclbox_path=Path("data/wclbox-wiki-crafting-skills.json")
if wclbox_path.exists():
    corroborated=json.loads(wclbox_path.read_text(encoding="utf-8"))
    for sid, value in corroborated["skillsBySpellId"].items():
        if sid in records:
            if records[sid]["required"]!=value["required"]:
                raise ValueError(f"WCLBox/Wiki minimum disagrees with a vetted value for spell {sid}")
        else:
            records[sid]=value
# Explicit pattern-item skill must match WCLBox's first required-skill field.
pattern_wclbox_path=Path("data/pattern-wclbox-crafting-skills.json")
if pattern_wclbox_path.exists():
    extra=json.loads(pattern_wclbox_path.read_text(encoding="utf-8"))
    for sid, value in extra["skillsBySpellId"].items():
        if sid in records and records[sid]["required"] != value["required"]:
            raise ValueError(f"Pattern/WCLBox conflicting craft minimum for spell {sid}")
        records.setdefault(sid,value)
# Explicit 'Learnable at' vs 'Yellow at' from per-spell Forever Ninja pages,
# corroborated by WCLBox first required-skill field or observed in-game.
ninja_path=Path("data/ninja-wclbox-crafting-skills.json")
if ninja_path.exists():
    for sid, value in json.loads(ninja_path.read_text(encoding="utf-8"))["skillsBySpellId"].items():
        if sid in records and records[sid]["required"]!=value["required"]:
            raise ValueError(f"Forever Ninja minimum conflicts with existing record {sid}")
        records.setdefault(sid,value)
# Source-backed spell-level regression checks. Do not substitute skill-up tiers.
checked_minimums={
    "3770":110, # Toughened Leather Gloves
    "6661":190, # Barbaric Harness
    "9060":25,  # Light Leather Quiver
    "3780":150, # Heavy Armor Kit
    "10487":200,# Thick Armor Kit
    "3766":125, # Dark Leather Belt
    "7151":150  # Barbaric Shoulders
}
for spell, minimum in checked_minimums.items():
    if records.get(spell,{}).get("required")!=minimum:
        raise ValueError(f"Minimum crafting skill regression for {spell}: expected {minimum}")

# Regression checks for a known skill-up-threshold mixup and a source conflict.
if records.get("3770",{}).get("required")!=110:
    raise ValueError("Regression: Toughened Leather Gloves must require crafting skill 110")
if "7153" in records:
    raise ValueError("Guardian Cloak conflicting requirement must stay unresolved")
OUT.write_text(json.dumps({"meta":{"source":data["source"],"entries":len(records),"sourceConflictsExcluded":len(conflict_ids) if extra_path.exists() else 0,"method":"Only a stated minimum crafting skill, keyed by unique spell ID; no yellow/green/grey thresholds."},"skillsBySpellId":records},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print("Verified crafting skills:",len(records))
