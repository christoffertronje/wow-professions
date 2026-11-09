#!/usr/bin/env python3
"""Cross-check all Rare recipe minimum crafting skills and reagents from the
ForeverBuilder independent public table, without accepting '~' estimates.
"""
import collections,json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
URL="https://wowforeverbuilder.com/professions/leatherworking/"
OUT=pathlib.Path("docs/rare-builder-crosscheck.json")
DATA=json.loads(pathlib.Path("data/leatherworking.json").read_text(encoding="utf-8"))
rare=[r for r in DATA["recipes"] if r["quality"]=="rare"]
norm=lambda s:re.sub(r"[^a-z0-9]+","",s.casefold())
index=collections.defaultdict(list)
for r in rare:index[norm(r["name"])].append(r)
req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions rare recipe crosscheck)"})
with urllib.request.urlopen(req,timeout=90) as resp:soup=BeautifulSoup(resp.read(),"html.parser")
entries=[]
for table in soup.select("table"):
 for tr in table.find_all("tr")[1:]:
  td=tr.find_all("td",recursive=False)
  if len(td)<5:continue
  rawname=td[0].get_text(" ",strip=True)
  skill=td[1].get_text(" ",strip=True)
  mats=td[4].get_text(" ",strip=True)
  name=rawname.strip()
  if name:entries.append({"name":name,"skill":skill,"mats":mats})
counts=collections.Counter(norm(r["name"]) for r in entries)
results=[]
for r in rare:
  matches=[x for x in entries if norm(x["name"])==norm(r["name"])]
  x=matches[0] if len(matches)==1 else None
  reference_level=int(x["skill"]) if x and x["skill"].isdigit() else None
  results.append({"spellId":r["id"],"name":r["name"],"ourSkill":r["craftSkillRequired"],
     "referenceSkill":reference_level,"sourceSkillRaw":x["skill"] if x else None,
     "skillMatch":reference_level==r["craftSkillRequired"] if reference_level else None,
     "found":bool(x),"sourceMaterialsText":x["mats"] if x else None})
report={"source":URL,"summary":{
 "rareCount":len(rare),"sourceRows":len(entries),"matched":sum(bool(x["found"]) for x in results),
 "explicitSkillMatches":sum(x["skillMatch"] is True for x in results),
 "explicitSkillMismatches":sum(x["skillMatch"] is False for x in results),
 "referenceSkillMissingOrApproximate":sum(x["skillMatch"] is None for x in results)},
 "mismatches":[x for x in results if x["skillMatch"] is False],"results":results}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(report["summary"])
