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
for sid,craft in craft_skill_map.items():
    recorded=skill_lookup.get(sid)
    if recorded is not None and recorded != craft:
        raise RuntimeError(f"Conflict in requirements for spell {sid}: {recorded} vs {craft}")
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
        "required":craft_skill_map.get(str(r["id"]),skill_lookup.get(str(r["id"]))),  # Prefer independently cross-checked Forever craft skill
        "clientMinimumRaw":r.get("skillRequired"),
        "learningRequirementSource":"wowforevertalent" if skill_lookup.get(str(r["id"])) is not None else None,
        "requirementEvidence":"crosschecked-forever-crafting" if str(r["id"]) in craft_skill_map else ("recorded-pattern-learning" if skill_lookup.get(str(r["id"])) is not None else "unverified"),
        "mats":mats,
        "matsKnown":bool(r.get("reagentsKnown")),
        "source":"Unknown",
        "itemId":output_id,
        "iconFileDataId":(output or {}).get("iconFileDataId") or r.get("iconFileDataId"),
        "category":r.get("category") or "Miscellaneous",
        "dataStatus":r.get("dataStatus") or "unknown"
    })
result.sort(key=lambda r:((r["required"] if isinstance(r["required"],int) else 9999),r["name"].casefold(),r["id"]))
assert len(result)>=450,f"unexpectedly few Leatherworking recipes: {len(result)}"
assert len(set(r["id"] for r in result))==len(result),"duplicate recipe IDs"
OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_text(json.dumps({"meta":{"source":SOURCE_URL,"build":snapshot.get("build"),"profession":"Leatherworking","count":len(result),"qualityUnknown":sum(x["quality"]=="unknown" for x in result),"materialsUnknown":sum(not x["matsKnown"] for x in result),
        "skillsKnown":sum(x["required"] is not None for x in result),
        "skillsUnknown":sum(x["required"] is None for x in result),
        "craftingCrosschecked":sum(x["requirementEvidence"]=="crosschecked-forever-crafting" for x in result),
        "skillsReference":(skills or {}).get("meta",{}).get("source"),"warning":"Client data is not proof of live availability. Learning requirements from the reference may be recipe item requirements, not verified trainer unlocks."},"recipes":result},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print(f"Wrote {len(result)} Leatherworking recipes; missing qualities {sum(x['quality']=='unknown' for x in result)}")
