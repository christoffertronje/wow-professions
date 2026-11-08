#!/usr/bin/env python3
"""Inspect two public Forever leatherworking tables, without republishing content."""
import json, pathlib, urllib.request
from bs4 import BeautifulSoup

URLS = {
 "zockify":"https://www.zockify.com/forever/professions/leatherworking/recipes/",
 "wclbox":"https://wowforever.wclbox.com/en/zhuanye/leatherworking",
}
report={}
for key,url in URLS.items():
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions min-skill-audit)"})
  with urllib.request.urlopen(req,timeout=60) as resp:page=resp.read()
  soup=BeautifulSoup(page,"html.parser")
  tables=[]
  for table in soup.select("table"):
   trs=table.select("tr")
   if len(trs)<15:continue
   samples=[]
   for tr in trs[:7]:
    cells=tr.find_all(["td","th"],recursive=False)
    samples.append([c.get_text(" ",strip=True)[:110] for c in cells[:8]])
   tables.append({"rows":len(trs),"head":samples,"classes":table.get("class",[])})
  report[key]={"bytes":len(page),"tables":tables[:9],"bodyRows":len(soup.select("tr")),"links":len(soup.select("a"))}
 except Exception as e:report[key]={"error":str(e)}
pathlib.Path("docs/source-table-shapes.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({key:{"rows":r.get("bodyRows"),"tableCount":len(r.get("tables",[])),"error":r.get("error")} for key,r in report.items()}))
