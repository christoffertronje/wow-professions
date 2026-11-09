#!/usr/bin/env python3
import json,urllib.request,pathlib,re
from bs4 import BeautifulSoup
out={}
for iid in ["252428","252424","4253","252538","4262"]:
 u=f"https://bindonforever.com/item/{iid}"
 try:
  req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (Forgebook item stat review)"})
  with urllib.request.urlopen(req,timeout=25) as resp: soup=BeautifulSoup(resp.read(),"html.parser")
  hits={}
  for q in ["Armor","Item Level","Binds when","Equip:","Use:","Agility","Sell Price"]:
   nodes=soup.find_all(string=re.compile(re.escape(q),re.I))
   hits[q]=[{"parent":str(n.parent)[:1200],"grandparent":str(n.parent.parent)[:2200] if n.parent and n.parent.parent else ""} for n in nodes[:2]]
  out[iid]={"title":soup.title.get_text(" ",strip=True) if soup.title else "","hits":hits,
    "tables":[str(t)[:3000] for t in soup.find_all("table")[:2]],
    "classes":[[a.get("class"),a.name] for a in soup.find_all(class_=re.compile("tooltip|item-stat|item-bonus|item-detail|wow-item",re.I))[:20]]}
 except Exception as e:out[iid]={"error":str(e)}
pathlib.Path("docs/bindonforever-stat-markup.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print({k:v.get("error") or v.get("title") for k,v in out.items()})
