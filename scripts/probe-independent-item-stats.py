#!/usr/bin/env python3
"""Inspect independent Forever item pages before implementing any comparison."""
import json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
urls=[
"https://forevermastery.com/en/items/252428-brawler-s-leather-belt",
"https://forevermastery.com/en/items/4253-toughened-leather-gloves",
"https://bindonforever.com/item/252428",
"https://bindonforever.com/items/252428",
"https://eternadex.com/en/datenbank/item/252428",
"https://www.oraclenewsnetwork.com/items/252428",
]
out=[]
for url in urls:
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; Forgebook rare item stats verification)"})
  with urllib.request.urlopen(req,timeout=20) as resp:
   html=resp.read(500000).decode("utf-8","replace")
   soup=BeautifulSoup(html,"html.parser")
   main=soup.select_one("main") or soup.select_one("article") or soup.body
   sample=main.get_text(" | ",strip=True)[:2800] if main else ""
   out.append({"url":url,"size":len(html),"title":soup.title.get_text(" ",strip=True) if soup.title else "",
    "text":sample,"tables":len(soup.select("table")),"mainHtml":str(main)[:3500] if main else "", 
    "jsonScripts":[{"type":n.get("type"),"id":n.get("id"),"len":len(n.get_text())} for n in soup.select('script[type="application/ld+json"],script#__NEXT_DATA__')][:5]})
 except Exception as ex:out.append({"url":url,"error":str(ex)})
p=pathlib.Path("docs/rare-independent-source-probe.json")
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print([(r["url"],r.get("error"),r.get("size")) for r in out])
