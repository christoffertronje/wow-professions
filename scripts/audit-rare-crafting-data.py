#!/usr/bin/env python3
"""Compare all Rare-quality Leatherworking crafts against an independent
Forever recipe page by exact crafting spell ID, required skill and reagents.

Reagents are read from the HTML's data-item-id/data-quantity elements.
The script never substitutes yellow/green/grey skill-up thresholds.
"""
import collections,json,pathlib,urllib.request
from bs4 import BeautifulSoup

URL="https://questing.wiki/wow-forever/professions/leatherworking/"
SOURCE=pathlib.Path("data/leatherworking.json")
OUT=pathlib.Path("docs/rare-crafting-material-skill-audit.json")
catalog=json.loads(SOURCE.read_text(encoding="utf-8"))
rare=[r for r in catalog["recipes"] if r.get("quality")=="rare"]
assert len(rare)==201,f"Unexpected number of rare quality recipes: {len(rare)}"
request=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions Rare-skills-reagents auditor)"})
with urllib.request.urlopen(request,timeout=120) as response:html=response.read()
soup=BeautifulSoup(html,"html.parser")
cards=soup.select("li[data-wow-recipe]")
source={}
duplicate=[]
for card in cards:
    sid=card.get("id","").removeprefix("recipe-")
    if sid in source:
        duplicate.append(sid)
        continue
    qtys=card.select(".wow-recipe-card__materials [data-wow-craft-material]")
    mats=[]
    for quantity in qtys:
        li=quantity.find_parent("li")
        if not li:raise ValueError(f"No reagent row for {sid}")
        name_el=li.select_one(".wow-recipe-material-name")
        if not name_el:raise ValueError(f"No material name for {sid}")
        item_id=quantity.get("data-item-id")
        amount=int(quantity.get("data-quantity","0"))
        if not item_id or amount<1:raise ValueError(f"Bad reagent count for {sid}")
        mats.append({"itemId":str(item_id),"name":name_el.get_text(" ",strip=True),"quantity":amount})
    source[sid]={"skill":int(card["data-required-skill"]) if card.get("data-required-skill","").isdigit() else None,
      "mats":mats,"name":card.select_one("h2").get_text(" ",strip=True) if card.select_one("h2") else "",
      "learning":card.get("data-learning")}
if duplicate:raise RuntimeError(f"Duplicate recipe source IDs: {duplicate}")
results=[]
for recipe in rare:
    ref=source.get(recipe["id"])
    local_mats=collections.Counter((str(name).casefold().strip(),int(qty)) for name,qty in recipe["mats"])
    foreign_mats=collections.Counter((str(m["name"]).casefold().strip(),m["quantity"]) for m in ref["mats"]) if ref else None
    skill_ok=bool(ref and recipe["craftSkillRequired"]==ref["skill"])
    mats_ok=bool(ref and local_mats==foreign_mats)
    row={"spellId":recipe["id"],"name":recipe["name"],"ourSkill":recipe["craftSkillRequired"],
         "referenceSkill":ref["skill"] if ref else None,"skillMatch":skill_ok,
         "materialsMatch":mats_ok,"ourMaterials":recipe["mats"],
         "referenceMaterials":ref["mats"] if ref else None,
         "referenceLearning":ref["learning"] if ref else None,"foundInReference":bool(ref)}
    results.append(row)
summary={"rareRecipes":len(rare),"sourceRecipeCards":len(source),
  "idMatches":sum(r["foundInReference"] for r in results),
  "skillMatches":sum(r["skillMatch"] for r in results),
  "materialMatches":sum(r["materialsMatch"] for r in results),
  "skillMismatches":sum(r["foundInReference"] and not r["skillMatch"] for r in results),
  "materialMismatches":sum(r["foundInReference"] and not r["materialsMatch"] for r in results),
  "unmatchedRecipes":sum(not r["foundInReference"] for r in results)}
report={"meta":{"catalogBuild":catalog["meta"]["build"],"source":URL,
 "comparison":"Exact recipe spell ID; displayed minimum craft skill and reagent name/quantity multiset; not trainer thresholds",
 "caveat":"Source may share game-client data; matching is independent presentation crosscheck, not a live in-game verification."},
 "summary":summary,"problems":[r for r in results if not r["skillMatch"] or not r["materialsMatch"]],"results":results}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(summary)
