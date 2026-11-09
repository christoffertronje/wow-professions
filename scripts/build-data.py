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

# Output item quality corrections are verified from explicit Forever item
# tooltips. Keep the override in this importer so rebuilds cannot undo it.
quality_path=pathlib.Path("data/item-quality-corrections.json")
quality_overrides=json.loads(quality_path.read_text(encoding="utf-8"))["byItemId"] if quality_path.exists() else {}
assert len(quality_overrides)==32, "Expected 32 verified Epic quality corrections"
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
    if str(output_id) in quality_overrides:
        quality=quality_overrides[str(output_id)]
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
# Only the minimum skill required to CRAFT is displayed in the UI.
# The source here explicitly labels its column as required skill.
# Other imported values remain research-only; never use yellow/green/gray.
verified_path=pathlib.Path("data/verified-crafting-skills.json")
verified_skills=json.loads(verified_path.read_text(encoding="utf-8"))["skillsBySpellId"] if verified_path.exists() else {}
for entry in result:
    lookup=verified_skills.get(entry["id"])
    entry["craftSkillRequired"]=lookup["required"] if lookup else None
    entry["craftSkillVerified"]=bool(lookup)
    entry["craftSkillSource"]=lookup["source"] if lookup else None
    entry["craftSkillReference"]=lookup["reference"] if lookup else None

# Publish only identifiable main-catalog WoW Forever recipes. The upstream
# client snapshot also contains Season of Discovery leftovers and unresolved
# spell records; their presence is not evidence of a live Forever craft.
excluded_sod=sum(r["category"]=="SEASON OF DISCOVERY" for r in result)
excluded_unidentified=sum(r["name"].startswith("Unresolved recipe #") or r["name"]=="Unnamed recipe" for r in result)
result=[r for r in result if r["category"]!="SEASON OF DISCOVERY" and not r["name"].startswith("Unresolved recipe #") and r["name"]!="Unnamed recipe"]
assert len(result)==512, f"Expected 512 named main-catalog recipes, got {len(result)}; review source changes"
assert excluded_sod==80 and excluded_unidentified==13, f"Unexpected excluded records: SoD={excluded_sod}, unidentified={excluded_unidentified}"
result.sort(key=lambda r:((r["craftSkillRequired"] if isinstance(r["craftSkillRequired"],int) else 9999),r["name"].casefold(),r["id"]))
assert len(result)==512,f"unexpected main-catalog Leatherworking count: {len(result)}"
assert len(set(r["id"] for r in result))==len(result),"duplicate recipe IDs"
OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_text(json.dumps({"meta":{"source":SOURCE_URL,"build":snapshot.get("build"),"profession":"Leatherworking","count":len(result),"scope":"Identified main-catalog WoW Forever Leatherworking recipes; excludes Season of Discovery and unidentified client records","excludedSeasonOfDiscovery":excluded_sod,"excludedUnidentified":excluded_unidentified,"qualityUnknown":sum(x["quality"]=="unknown" for x in result),"materialsUnknown":sum(not x["matsKnown"] for x in result),
        "skillsKnown":sum(x["required"] is not None for x in result),
        "craftSkillsVerified":sum(x["craftSkillVerified"] for x in result),
        "craftSkillsUnverified":sum(not x["craftSkillVerified"] for x in result),
        "skillsUnknown":sum(x["required"] is None for x in result),
        "craftingCrosschecked":sum(x["requirementEvidence"]=="crosschecked-forever-crafting" for x in result),
        "skillsRecovered70862":sum(x["requirementEvidence"]=="forever-70862-catalog" for x in result),
        "skillsRecoveredReference":"https://wowforevertalents.com/professions/leatherworking/",
        "skillsReference":(skills or {}).get("meta",{}).get("source"),"warning":"Catalog excludes known Season of Discovery and unidentified client records. Source-backed skill numbers do not independently prove a recipe is currently obtainable in live WoW Forever."},"recipes":result},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print(f"Wrote {len(result)} Leatherworking recipes; missing qualities {sum(x['quality']=='unknown' for x in result)}")
