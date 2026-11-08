#!/usr/bin/env python3
"""Build static, client-derived Leatherworking catalog for the UX prototype.

Source: ForeverTome's explicitly downloadable recipe JSON snapshot.
Uses game data fields; does not copy guides, articles or analysis.
Client presence is NOT proof a recipe is currently obtainable.
"""
import json
import pathlib
import urllib.request

SOURCE_URL = "https://forevertome.com/data/recipes.yafo0pc388.json"
QUALITY = {1:"common", 2:"uncommon", 3:"rare", 4:"epic", 5:"legendary"}
OUTPUT = pathlib.Path("data/leatherworking.json")

request=urllib.request.Request(SOURCE_URL,headers={"User-Agent":"wow-professions/0.1 (fan project; static data snapshot importer)"})
with urllib.request.urlopen(request,timeout=90) as response:
    snapshot=json.load(response)
skill_file=pathlib.Path("data/leatherworking-skills.json")
skills=json.loads(skill_file.read_text(encoding="utf-8")) if skill_file.exists() else None
skill_lookup=skills["skillBySpellId"] if skills else {}
forever_crosscheck=pathlib.Path("docs/forever-skill-crosscheck.json")
forever_rows=json.loads(forever_crosscheck.read_text(encoding="utf-8"))["matches"] if forever_crosscheck.exists() else []
craft_skill_map={str(row["spellId"]):row["craftingSkillReference"] for row in forever_rows}
newer_skill_path=pathlib.Path("data/forever-70862-skill-crosscheck.json")
newer_skills=json.loads(newer_skill_path.read_text(encoding="utf-8"))["newSkillsBySpellId"] if newer_skill_path.exists() else {}

for sid,craft in craft_skill_map.items():
    recorded=skill_lookup.get(sid)
    if recorded is not None and recorded != craft:
        raise RuntimeError(f"Conflict in requirements for spell {sid}: {recorded} vs {craft}")
for sid,level in newer_skills.items():
    if sid in craft_skill_map and craft_skill_map[sid]!=level:
        raise RuntimeError(f"Conflict between Forever sources for {sid}: {level} vs {craft_skill_map[sid]}")
    if skill_lookup.get(sid) is not None and skill_lookup[sid]!=level:
        raise RuntimeError(f"Conflicting pattern-learning skill for {sid}")

items={row["id"]:row for row in snapshot["items"] if isinstance(row,dict) and "id" in row}
all_recipes=[r for r in snapshot["recipes"] if r.get("professionId")==165 or 165 in r.get("professionIds",[])]
result=[]
for r in all_recipes:
    outputs=r.get("outputs") or []
    output=next((items.get(o.get("itemId")) for o in outputs if items.get(o.get("itemId"))),None)
    output_id=next((o.get("itemId") for o in outputs if o.get("itemId")),None)
    raw_quality=output.get("quality") if output else None
    mats=[]
    if r.get("reagentsKnown"):
        for reagent in r.get("reagents") or []:
            item=items.get(reagent.get("itemId"),{})
            mats.append([item.get("name") or "Unknown item #"+str(reagent.get("itemId")),reagent.get("quantity")])
    quality=QUALITY.get(raw_quality,"unknown")
    result.append({
        "id":str(r["id"]),
        "name":r.get("name") or (output or {}).get("name") or "Unnamed recipe",
        "quality":quality,
        "qualityVerified":quality!="unknown",
        "required":craft_skill_map.get(str(r["id"]),newer_skills.get(str(r["id"]),skill_lookup.get(str(r["id"])))),  # Preserve separate source evidence
        "clientMinimumRaw":r.get("skillRequired"),
        "learningRequirementSource":"wowforevertalent" if skill_lookup.get(str(r["id"])) is not None else None,
        "requirementEvidence":"crosschecked-forever-crafting" if str(r["id"]) in craft_skill_map else ("forever-70862-catalog" if str(r["id"]) in newer_skills else ("recorded-pattern-learning" if skill_lookup.get(str(r["id"])) is not None else "unverified")),
        "mats":mats,
        "matsKnown":bool(r.get("reagentsKnown")),
        "source":"Unknown",
        "itemId":output_id,
        "iconFileDataId":(output or {}).get("iconFileDataId") or r.get("iconFileDataId"),
        "category":r.get("category") or "Miscellaneous",
        "dataStatus":r.get("dataStatus") or "unknown"
    })
# Apply small, independently verified corrections last; keep skill-up thresholds separate.
correction_file=pathlib.Path("data/verified-skill-corrections.json")
corrections=json.loads(correction_file.read_text(encoding="utf-8")) if correction_file.exists() else {}
by_spell={entry["id"]:entry for entry in result}
for spell_id, correction in corrections.items():
    if spell_id=="description":
        continue
    if spell_id not in by_spell:
        raise RuntimeError(f"Correction references missing spell {spell_id}")
    entry=by_spell[spell_id]
    for field in ("required","skillYellow","skillGreen","skillGray","source","requirementEvidence"):
        if field in correction:
            entry[field]=correction[field]
    entry["requirementReferences"]=correction.get("referenceUrls",[])
# Only explicit crafting-requirement checks count as verified.
# Retain imported values in "required" as research data, never as guaranteed craft minimums.
for entry in result:
    verified=entry.get("requirementEvidence")=="verified-forever-pattern-table"
    entry["craftSkillRequired"]=entry.get("required") if verified else None
    entry["craftSkillVerified"]=verified

result.sort(key=lambda r:((r["required"] if isinstance(r["required"],int) else 9999),r["name"].casefold(),r["id"]))
assert len(result)>=450,f"unexpectedly few Leatherworking recipes: {len(result)}"
assert len(set(r["id"] for r in result))==len(result),"duplicate recipe IDs"
OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_text(json.dumps({"meta":{"source":SOURCE_URL,"build":snapshot.get("build"),"profession":"Leatherworking","count":len(result),"qualityUnknown":sum(x["quality"]=="unknown" for x in result),"materialsUnknown":sum(not x["matsKnown"] for x in result),
        "skillsKnown":sum(x["required"] is not None for x in result),
        "craftSkillsVerified":sum(x["craftSkillVerified"] for x in result),
        "craftSkillsUnverified":sum(not x["craftSkillVerified"] for x in result),
        "skillsUnknown":sum(x["required"] is None for x in result),
        "craftingCrosschecked":sum(x["requirementEvidence"]=="crosschecked-forever-crafting" for x in result),
        "skillsRecovered70862":sum(x["requirementEvidence"]=="forever-70862-catalog" for x in result),
        "skillsRecoveredReference":"https://wowforevertalents.com/professions/leatherworking/",
        "skillsReference":(skills or {}).get("meta",{}).get("source"),"warning":"Client data is not proof of live availability. Learning requirements from the reference may be recipe item requirements, not verified trainer unlocks."},"recipes":result},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print(f"Wrote {len(result)} Leatherworking recipes; missing qualities {sum(x['quality']=='unknown' for x in result)}")
