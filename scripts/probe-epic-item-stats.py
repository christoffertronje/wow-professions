#!/usr/bin/env python3
"""Verify every Epic crafting spell points to an Epic tooltip and exact output item ID."""
import json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
catalog=json.loads(pathlib.Path("data/leatherworking.json").read_text())
epics=[x for x in catalog["recipes"] if x["quality"]=="epic"]
assert len(epics)==38
url="https://wowforevertalent.com/professions/leatherworking/?acquisition=favor"
req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (Forgebook epic gear source coverage)"})
with urllib.request.urlopen(req,timeout=80) as resp:soup=BeautifulSoup(resp.read(),"html.parser")
details={}
for a in soup.select("article.recipe-detail"):
 sp=a.select_one(".recipe-spell");facts=a.select_one("[data-output-facts]")
 if not sp or not facts:continue
 match=re.fullmatch(r"Spell\s+(\d+)",sp.get_text(" ",strip=True))
 if not match:continue
 details[match.group(1)]={"itemId":str(facts.get("data-output-facts")),"lines":[x.get_text(" ",strip=True) for x in facts.select("ul > li")],
     "effects":[x.get_text(" ",strip=True) for x in facts.select(".profession-output-effect")]}
rows=[]
for r in epics:
 x=details.get(r["id"]);lines=x["lines"] if x else []
 rows.append({"spellId":r["id"],"name":r["name"],"itemId":r["itemId"],"sourceFound":bool(x),
   "itemIdMatch":bool(x and x["itemId"]==str(r["itemId"])),
   "epicQuality":bool("Epic" in lines),"itemLevel":next((s for s in lines if s.startswith("Item Level")),None),
   "tooltip":lines,"effects":x["effects"] if x else None})
summary={"epicRecipes":38,"sourceMatches":sum(x["sourceFound"] for x in rows),
  "itemIdMatches":sum(x["itemIdMatch"] for x in rows),
  "epicQualityMatches":sum(x["epicQuality"] for x in rows),
  "sourceItemLevels":sum(bool(x["itemLevel"]) for x in rows)}
pathlib.Path("docs/epic-stats-source-probe.json").write_text(json.dumps({"summary":summary,"results":rows},ensure_ascii=False,indent=2)+"\n")
print(summary)
