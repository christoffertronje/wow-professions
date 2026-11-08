import json,urllib.request,pathlib
from bs4 import BeautifulSoup
u="https://warcraft.wiki.gg/wiki/Forever_leatherworking_patterns"
req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions/0.1)"})
with urllib.request.urlopen(req,timeout=50) as r: soup=BeautifulSoup(r.read(),"html.parser")
rows=[]
for table in soup.select("table"):
  trs=table.select("tr")
  if len(trs)<3:continue
  first=[]
  for tr in trs[:5]:
    first.append([td.get_text(" ",strip=True)[:90] for td in tr.find_all(["td","th"],recursive=False)])
  rows.append({"n":len(trs),"head":first,"classes":table.get("class",[])})
pathlib.Path("docs/wiki-table-shape.json").write_text(json.dumps(rows,indent=2)+"\n")
print(json.dumps(rows[:6],indent=2))
