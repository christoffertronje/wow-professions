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
OUT.write_text(json.dumps({"meta":{"source":data["source"],"entries":len(records),"sourceConflictsExcluded":len(conflict_ids) if extra_path.exists() else 0,"method":"Only a stated minimum crafting skill, keyed by unique spell ID; no yellow/green/grey thresholds."},"skillsBySpellId":records},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print("Verified crafting skills:",len(records))
