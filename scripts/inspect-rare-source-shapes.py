#!/usr/bin/env python3
"""Inspect markup for independently published Forever Leatherworking recipes."""
from bs4 import BeautifulSoup
import json,pathlib,urllib.request
urls={
"talent":"https://wowforevertalent.com/professions/leatherworking/?acquisition=favor",
"builder":"https://wowforeverbuilder.com/professions/leatherworking/",
"zockify":"https://www.zockify.com/forever/professions/leatherworking/recipes/",
"questing":"https://questing.wiki/wow-forever/professions/leatherworking/",
}
out={}
for key,url in urls.items():
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions rare-recipe audit)"})
  with urllib.request.urlopen(req,timeout=65) as resp:html=resp.read()
  soup=BeautifulSoup(html,"html.parser")
  tables=[]
  for t in soup.select("table"):
   trs=t.find_all("tr")
   if len(trs)<8:continue
   tables.append({"class":t.get("class",[]),"rows":len(trs),"sample":[[c.get_text(" ",strip=True)[:130] for c in tr.find_all(["td","th"],recursive=False)[:7]] for tr in trs[:3]]})
  heads=[]
  for heading in soup.find_all(["h2","h3","h4"]):
   if "Brawler's Leather Belt" in heading.get_text(" ",strip=True):
    anc=heading
    for depth in range(5):
     anc=anc.parent
     if anc is None:break
     heads.append({"depth":depth,"tag":anc.name,"class":anc.get("class",[]),"text":anc.get_text(" ",strip=True)[:1600],"html":str(anc)[:1800]})
  out[key]={"http":200,"size":len(html),"tables":tables[:4],"headings":heads[:5]}
 except Exception as exc:out[key]={"error":str(exc)}
pathlib.Path("docs/rare-source-html-shapes.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print({k:{"size":x.get("size"),"tableRows":[t["rows"] for t in x.get("tables",[])],"headings":len(x.get("headings",[])),"error":x.get("error")} for k,x in out.items()})
