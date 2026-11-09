#!/usr/bin/env python3
import json,urllib.request,pathlib,collections,re
from bs4 import BeautifulSoup
d=json.loads(pathlib.Path("data/leatherworking.json").read_text())
green=[x for x in d["recipes"] if x["quality"]=="uncommon"]
url="https://wowforevertalent.com/professions/leatherworking/?acquisition=favor"
with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=90) as r:s=BeautifulSoup(r.read(),"html.parser")
src={}
for a in s.select("article.recipe-detail"):
 sp=a.select_one(".recipe-spell")
 if not sp:continue
 m=re.search(r"Spell\s+(\d+)",sp.get_text(" ",strip=True))
 if not m:continue
 f=a.select_one("[data-output-facts]")
 if f:src[m.group(1)]={"item":f.get("data-output-facts"),"lines":[x.get_text(" ",strip=True) for x in f.select("ul > li")],"effects":[x.get_text(" ",strip=True) for x in f.select(".profession-output-effect")]}
counts=collections.Counter();problems=[];samples=[]
for x in green:
 f=src.get(x["id"])
 if f is None:counts["source_missing"]+=1;problems.append({"name":x["name"],"id":x["id"],"reason":"no facts"});continue
 if str(x["itemId"])!=f["item"]:counts["item_mismatch"]+=1;problems.append({"name":x["name"],"id":x["id"],"expected":x["itemId"],"actual":f["item"]});continue
 counts["matched"]+=1
 if "Uncommon" not in f["lines"]:counts["quality_mismatch"]+=1;problems.append({"name":x["name"],"id":x["id"],"lines":f["lines"][:4]})
 if not any(re.match(r"Item Level\s+\d+",z) for z in f["lines"]):counts["no_item_level"]+=1;problems.append({"name":x["name"],"id":x["id"],"lines":f["lines"]})
 if len(samples)<6:samples.append({"id":x["id"],"name":x["name"],"lines":f["lines"],"effects":f["effects"]})
out={"summary":dict(counts),"total":len(green),"problems":problems,"samples":samples}
pathlib.Path("docs/uncommon-stats-source-probe.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print(out["summary"])
