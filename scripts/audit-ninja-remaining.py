#!/usr/bin/env python3
"""Audit unresolved minimum craft-skill recipes against Forever Ninja spell pages.
Diagnostic only: a data-mined 'learnable at' is not necessarily in-game verified.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,urllib.request,urllib.error
CATALOG=json.loads(Path("data/leatherworking.json").read_text())["recipes"]
remaining=[r for r in CATALOG if r.get("craftSkillRequired") is None and r.get("category")!="SEASON OF DISCOVERY" and not r["name"].startswith("Unresolved recipe #")]
results=[]
for recipe in remaining:
    slug=re.sub(r"[^a-z0-9]+","-",recipe["name"].casefold()).strip("-")
    url=f"https://wowforever.ninja/professions/leatherworking/{recipe['id']}-{slug}/"
    result={"spellId":recipe["id"],"name":recipe["name"],"url":url,"priorImported":recipe.get("required")}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions-audit/0.1)"})
        with urllib.request.urlopen(req,timeout=20) as resp:html=resp.read().decode("utf-8","replace")
        soup=BeautifulSoup(html,"html.parser")
        body=soup.get_text(" ",strip=True)
        m=re.search(r"Learnable at\s+(\d{1,3})\b",body,re.I)
        result.update({"http":200,"learnableAt":int(m.group(1)) if m else None,
           "seenInGame":"Seen in the game by us" in body or "Verified in beta" in body,
           "trainerEvidence":"needs Leatherworking" in body or "Taught by" in body,
           "snippet":body[max(0,m.start()-100):m.start()+290] if m else body[:450]})
    except Exception as e: result["error"]=str(e)[:200]
    results.append(result)
out={"source":"https://wowforever.ninja/","checked":len(results),"foundLearnableAt":sum(x.get("learnableAt") is not None for x in results),"seenInGame":sum(x.get("seenInGame") for x in results),"results":results,"note":"Do not auto-merge; 'learnable at' may be from client comparisons with no in-game observation."}
Path("docs/ninja-remaining-crafting-audit.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print({k:out[k] for k in ("checked","foundLearnableAt","seenInGame")})
