#!/usr/bin/env python3
"""Check Rare recipe details in Forever Talent against Forgebook."""
import json,re,pathlib,urllib.request
from bs4 import BeautifulSoup
U="https://wowforevertalent.com/professions/leatherworking/?acquisition=favor"
req=urllib.request.Request(U,headers={"User-Agent":"Mozilla/5.0 (compatible; Rare Leatherworking independent audit)"})
with urllib.request.urlopen(req,timeout=80) as resp:html=resp.read()
soup=BeautifulSoup(html,"html.parser")
probe=[]
for sid in ("1255142","3770","24849","28219"):
 nodes=[article for article in soup.select("article.recipe-detail") if article.select_one(".recipe-spell") and article.select_one(".recipe-spell").get_text(" ",strip=True)==f"Spell {sid}"]
 if not nodes:
  probe.append({"spell":sid,"found":False});continue
 node=nodes[0];sub=[]
 for h in node.find_all(["h3","h4"]):
  if h.get_text(" ",strip=True) in {"Reagents","How to learn","Created item"}:
   parent=h.parent
   sub.append({"heading":h.get_text(" ",strip=True),"parent":str(parent)[:1900],"siblings":[str(z)[:700] for z in list(parent.next_siblings)[:2]]})
 probe.append({"spell":sid,"found":True,"sub":sub,"class":node.get("class"),"text":node.get_text(" ",strip=True)[:800]})
pathlib.Path("docs/rare-talent-layout.json").write_text(json.dumps(probe,ensure_ascii=False,indent=2)+"\n")
print([(x["spell"],x["found"],len(x.get("sub",[]))) for x in probe])
