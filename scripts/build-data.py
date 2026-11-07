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
        "required":r.get("skillRequired"),
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
OUTPUT.write_text(json.dumps({"meta":{"source":SOURCE_URL,"build":snapshot.get("build"),"profession":"Leatherworking","count":len(result),"qualityUnknown":sum(x["quality"]=="unknown" for x in result),"materialsUnknown":sum(not x["matsKnown"] for x in result),"warning":"Client data is not proof of live availability. Required skill values are raw client fields, not verified training requirements."},"recipes":result},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print(f"Wrote {len(result)} Leatherworking recipes; missing qualities {sum(x['quality']=='unknown' for x in result)}")
