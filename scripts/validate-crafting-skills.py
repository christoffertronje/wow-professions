#!/usr/bin/env python3
"""Validate published minimum Leatherworking crafting requirements.

Fail build if raw client/skill-up thresholds leak into the displayed field,
if known spell minima regress, or if any named main-catalog craft is unknown.
"""
import json
from pathlib import Path
DATA=json.loads(Path("data/leatherworking.json").read_text(encoding="utf-8"))
LOOKUP=json.loads(Path("data/verified-crafting-skills.json").read_text(encoding="utf-8"))["skillsBySpellId"]
rows=DATA["recipes"]
assert len(rows)==DATA["meta"]["count"]==512, "Expected only the 512 identified main-catalog recipes"
assert all(r.get("category")!="SEASON OF DISCOVERY" and not r["name"].startswith("Unresolved recipe #") and r["name"]!="Unnamed recipe" for r in rows), "Historical or unnamed client records leaked into public catalog"
assert len(set(row["id"] for row in rows))==len(rows), "Duplicate recipe spell ID"
count=0
for row in rows:
    record=LOOKUP.get(row["id"])
    if record is None:
        assert row.get("craftSkillRequired") is None, f"Unsourced craft requirement: {row['name']}"
        assert not row.get("craftSkillVerified"), f"Incorrect verified flag: {row['name']}"
    else:
        assert row.get("craftSkillRequired")==record["required"], f"Mismatch for {row['name']}"
        assert row.get("craftSkillVerified") is True, f"Missing verification state: {row['name']}"
        assert row.get("craftSkillReference"), f"Missing evidence for {row['name']}"
        assert 1<=record["required"]<=450, f"Invalid skill for {row['name']}"
        count+=1

assert count==DATA["meta"]["craftSkillsVerified"], "Wrong published verified count"
assert set(r["id"] for r in rows).issubset(LOOKUP), "Some published recipes lack a trusted crafting-skill source"
assert len(rows)-count==DATA["meta"]["craftSkillsUnverified"]

main=[r for r in rows if r.get("category")!="SEASON OF DISCOVERY" and not r["name"].startswith("Unresolved recipe #")]
assert len(main)==512 and all(r["craftSkillRequired"] is not None for r in main), "Main Forever recipe coverage regression"

checks={"3770":110,"6661":190,"9060":25,"3780":150,"10487":200,"3766":125,"7151":150,"19047":250,"24703":300,"10548":210,
"28474":300,"28473":300,"28472":300,"28224":300,"7153":160}
byid={r["id"]:r for r in rows}
for spell,skill in checks.items():
    assert byid[spell]["craftSkillRequired"]==skill, f"Regression of {byid[spell]['name']}"
assert byid["7153"]["craftSkillRequired"]==160, "Guardian Cloak vetted Forever skill 160 must survive rebuild"
# Guard against accidentally dropping or mis-leveling recipes sold by the
# Redridge Mountains Leatherworking vendor Daniel Stitchsong. The source
# vendor item tooltip has nine singular "Shoulder" labels; the spell names
# in modern Forever data use "Shoulders". Spell IDs resolve those aliases.
vendor_report=Path("docs/daniel-stitchsong-recipe-audit.json")
if vendor_report.exists():
    vendor=json.loads(vendor_report.read_text(encoding="utf-8"))
    assert vendor["tableRowCount"]==81, "Unexpected number of Redridge vendor patterns"
    assert len(vendor["matches"])==81 and not vendor["missing"] and not vendor["skillMismatches"], "Redridge vendor coverage audit incomplete"
    for entry in vendor["matches"]:
        recipe=byid.get(entry["spellId"])
        assert recipe is not None, f"Missing Redridge vendor spell {entry['spellId']}"
        assert recipe["craftSkillRequired"]==entry["vendorRequired"], f"Incorrect Redridge vendor skill for {recipe['name']}"
print(f"PASS: {len(main)} identified main WoW Forever recipes; {count}/{len(rows)} have source-backed crafting requirements; historical/unnamed entries excluded")
