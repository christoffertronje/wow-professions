#!/usr/bin/env python3
"""Inspect the Forever Guide's provenance-rich Leatherworking/EG Link pages.
Only report structures and a few sample snippets, never automatically import.
"""
from bs4 import BeautifulSoup
import pathlib,urllib.request,json,re
urls=[
 "https://guide.wow4ever.se/en/professions",
 "https://guide.wow4ever.se/en/professions/leatherworking",
 "https://guide.wow4ever.se/en/trainers",
]
report={}
for url in urls:
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions verification/0.1)"})
  with urllib.request.urlopen(req,timeout=35) as resp:body=resp.read().decode("utf-8","replace")
  soup=BeautifulSoup(body,"html.parser")
  report[url]={
   "bytes":len(body),
   "title":soup.title.get_text(" ",strip=True) if soup.title else "",
   "skillPatterns":[body[max(0,m.start()-95):m.start()+175] for m in list(re.finditer(r"EG Link|Leatherworking|Trainer|skillRequired",body,re.I))[:8]],
   "leatherLinks":[{"text":a.get_text(" ",strip=True)[:45],"href":a.get("href","")} for a in soup.select("a") if "leatherwork" in (a.get_text(" ",strip=True)+" "+a.get("href","")).lower()][:14],
   "tableCount":len(soup.select("table")),
   "initialDataScripts":[{"id":s.get("id"),"type":s.get("type"),"length":len(s.get_text())} for s in soup.select("script") if s.get("id") or "application/json" in s.get("type","")][:8],
  }
 except Exception as e:report[url]={"error":str(e)}
pathlib.Path("docs/eglink-source-inspection.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({u:{"bytes":x.get("bytes"),"error":x.get("error")} for u,x in report.items()}))
