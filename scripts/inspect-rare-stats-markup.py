#!/usr/bin/env python3
"""Inspect Forever item stat fields to define a faithful structured importer."""
import json,pathlib,urllib.request
from bs4 import BeautifulSoup
u="https://wowforevertalent.com/professions/leatherworking/?acquisition=favor"
req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (WoW Forever item stats audit)"})
with urllib.request.urlopen(req,timeout=90) as r:soup=BeautifulSoup(r.read(),"html.parser")
ids=["1255142","3770","1255055","24849","28219"]
out={}
for sid in ids:
 a=next((a for a in soup.select("article.recipe-detail") if (el:=a.select_one(".recipe-spell")) and el.get_text(" ",strip=True)==f"Spell {sid}"),None)
 if not a:continue
 facts=a.select_one("[data-output-facts]")
 out[sid]={"factsHTML":str(facts)[:5000] if facts else None,"factsText":facts.get_text(" | ",strip=True) if facts else None,"createdHTML":str(a.select_one("ul.recipe-items"))[:1200] if a.select_one("ul.recipe-items") else None}
pathlib.Path("docs/rare-stats-markup.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print({k:v["factsText"] for k,v in out.items()})
