#!/usr/bin/env python3
"""Audit WCLBox Forever 'Skill' first number against indexed recipes.

The WCLBox recipe table exposes 4 numbers: craft requirement, yellow,
green and gray thresholds. Only FIRST is considered. Never replace
conflicting recorded requirements, and don't equate name duplicates.
"""
from collections import Counter,defaultdict
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,urllib.request

URL="https://wowforever.wclbox.com/en/zhuanye/leatherworking"
DOC=Path("docs/wclbox-crafting-comparison.json")
catalog=json.loads(Path("data/leatherworking.json").read_text(encoding="utf-8"))["recipes"]
wiki=json.loads(Path("docs/wiki-craft-skill-crosscheck.json").read_text(encoding="utf-8"))
normalize=lambda s:re.sub(r"[^a-z0-9]+","",s.casefold())
by_name=defaultdict(list)
for r in catalog:
  if r.get("category")!="SEASON OF DISCOVERY" and not r["name"].startswith("Unresolved recipe #"):
    by_name[normalize(r["name"])].append(r)
req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions minimum skill verifier/0.1)"})
with urllib.request.urlopen(req,timeout=80) as resp:
    soup=BeautifulSoup(resp.read(),"html.parser")
rows=[]
for table in soup.select("table.zk-recipes"):
    for tr in table.select("tr"):
        tds=tr.find_all("td",recursive=False)
        if len(tds)<4:continue
        name=tds[0].get_text(" ",strip=True)
        name=re.sub(r"\s+New$","",name,flags=re.I).strip()
        skills=[int(v) for v in re.findall(r"\d+",tds[2].get_text(" ",strip=True))]
        if len(skills)!=4:continue
        required,yellow,green,gray=skills
        if not (1<=required<=450 and required<=yellow<=green<=gray):continue
        rows.append({"name":name,"required":required,"yellow":yellow,"green":green,"gray":gray})
if not 500<=len(rows)<=530:raise ValueError(f"Unexpected row count: {len(rows)}")
namecounts=Counter(normalize(r["name"]) for r in rows)
matches=[];skipped=[]
for x in rows:
    key=normalize(x["name"])
    records=by_name.get(key,[])
    if len(records)!=1 or namecounts[key]!=1:
        skipped.append(x["name"])
        continue
    r=records[0]
    matches.append({"spellId":r["id"],"name":r["name"],"wclboxRequired":x["required"],"currentCraftRequired":r.get("craftSkillRequired"),"currentRawRequired":r.get("required"),"category":r.get("category")})
wiki_new={str(x["id"]):x for x in wiki.get("newCandidates",[])}
byspell={m["spellId"]:m for m in matches}
confirmed_candidates=[]
for x in matches:
    if x["currentCraftRequired"] is not None:continue
    w=wiki_new.get(x["spellId"])
    if not w or w["skill"]!=x["wclboxRequired"]:continue
    confirmed_candidates.append({
      "spellId":x["spellId"],"name":x["name"],"required":x["wclboxRequired"],
      "wikiSource":w.get("wikiSource"),"sourceA":URL,
      "sourceB":"https://warcraft.wiki.gg/wiki/Forever_leatherworking_patterns"
    })
conflicts=[x for x in matches if x["currentCraftRequired"] is not None and x["currentCraftRequired"]!=x["wclboxRequired"]]
pending=[x for x in matches if x["currentCraftRequired"] is None]
report={"source":URL,"recordCount":len(rows),"uniqueMatches":len(matches),"skippedAmbiguous":len(skipped),"unresolvedWithWclbox":len(pending),"unresolvedWithWikiAgreement":len(confirmed_candidates),"conflictsWithExisting":len(conflicts),"conflicts":conflicts,"candidates":confirmed_candidates,"notYetCorroborated":[x for x in pending if x["spellId"] not in {c["spellId"] for c in confirmed_candidates}]}
DOC.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print({key:report[key] for key in ("recordCount","uniqueMatches","skippedAmbiguous","unresolvedWithWclbox","unresolvedWithWikiAgreement","conflictsWithExisting")})
