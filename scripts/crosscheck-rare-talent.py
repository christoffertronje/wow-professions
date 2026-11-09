#!/usr/bin/env python3
"""Independently cross-check 201 Rare recipes' material name and quantity
against Forever Talent's per-spell detailed Reagents list.
Also compare explicitly provided pattern-learning requirement (when present).
"""
import collections,json,re,pathlib,urllib.request
from bs4 import BeautifulSoup
URL="https://wowforevertalent.com/professions/leatherworking/?acquisition=favor"
SOURCE=json.loads(pathlib.Path("data/leatherworking.json").read_text())
rare=[r for r in SOURCE["recipes"] if r["quality"]=="rare"]
assert len(rare)==201
req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions Rare-recipe-material-audit)"})
with urllib.request.urlopen(req,timeout=110) as resp:soup=BeautifulSoup(resp.read(),"html.parser")
spells={};duplicates=[]
for article in soup.select("article.recipe-detail"):
 spell_tag=article.select_one(".recipe-spell")
 if not spell_tag:continue
 m=re.fullmatch(r"Spell\s+(\d+)",spell_tag.get_text(" ",strip=True))
 if not m:continue
 sid=m.group(1)
 if sid in spells:
  duplicates.append(sid)
  continue
 reagents_h=next((h for h in article.find_all("h4",recursive=False) if h.get_text(" ",strip=True)=="Reagents"),None)
 if not reagents_h:continue
 ul=reagents_h.find_next_sibling("ul")
 materials=[]
 if ul:
  for li in ul.find_all("li",recursive=False):
   copy=li.select_one(".recipe-item-copy")
   if not copy:continue
   spans=copy.find_all("span",recursive=False)
   if not spans:continue
   name=spans[0].get_text(" ",strip=True)
   qmatch=re.search(r"×\s*(\d+)",copy.get_text(" ",strip=True))
   qty=int(qmatch.group(1)) if qmatch else 1
   materials.append([name,qty])
 learning=article.select_one(".recipe-learning[data-learning-requirement]")
 spells[sid]={"name":article.select_one("h3").get_text(" ",strip=True) if article.select_one("h3") else "",
             "materials":materials,"learning":int(learning["data-learning-requirement"]) if learning else None}
if duplicates:raise RuntimeError(f"Duplicate spell detail entries {duplicates[:10]}")
results=[]
normalize=lambda s:s.casefold().strip()
for item in rare:
 ref=spells.get(item["id"])
 ourm=collections.Counter((normalize(name),int(q)) for name,q in item["mats"])
 srcm=collections.Counter((normalize(name),int(q)) for name,q in ref["materials"]) if ref else None
 results.append({"spellId":item["id"],"name":item["name"],
     "found":ref is not None,"materialMatch":srcm==ourm if ref and ref["materials"] else None,
     "learningRankMatch":ref["learning"]==item["craftSkillRequired"] if ref and ref["learning"] is not None else None,
     "ourRequired":item["craftSkillRequired"],"learningRank":ref["learning"] if ref else None,
     "ourMaterials":item["mats"],"referenceMaterials":ref["materials"] if ref else None})
summary={"rareCount":len(rare),"sourceSpellDetails":len(spells),
 "matchedSpellIds":sum(x["found"] for x in results),
 "materialMatches":sum(x["materialMatch"] is True for x in results),
 "materialMismatches":sum(x["materialMatch"] is False for x in results),
 "sourceMaterialsUnavailable":sum(x["materialMatch"] is None for x in results),
 "learningRankMatches":sum(x["learningRankMatch"] is True for x in results),
 "learningRankMismatches":sum(x["learningRankMatch"] is False for x in results),
 "learningRankUnavailable":sum(x["learningRankMatch"] is None for x in results)}
report={"source":URL,"summary":summary,"problems":[x for x in results if x["materialMatch"] is False or x["learningRankMatch"] is False],
 "results":results,"note":"Learning requirement can differ from crafting minimum for trainer spells. Only explicit pattern-item learning ranks should be treated as an additional cross-check; colors are never used."}
pathlib.Path("docs/rare-talent-crosscheck.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(summary)
