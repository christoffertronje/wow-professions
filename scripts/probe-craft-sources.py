#!/usr/bin/env python3
"""Test source accessibility for a spell-ID-based crafting-skill audit.
Writes diagnostic findings only: no guessed values or republishes.
"""
import json,re,urllib.request,urllib.error,pathlib
urls=[
 "https://www.wowhead.com/forever/spell=6661/barbaric-harness",
 "https://warcraft.wiki.gg/wiki/Forever_leatherworking_patterns",
 "https://www.warcraftforever.wiki/wiki/Leatherworking/Recipes",
 "https://foreverlfg.app/professions"
]
out=[]
for url in urls:
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions audit/0.1)"})
  with urllib.request.urlopen(req,timeout=20) as res:
   body=res.read(2500000).decode("utf-8","replace")
   out.append({"url":url,"http":res.status,"bytesCaptured":len(body),"requiresLeatherworking":re.findall(r"Requires Leatherworking(?:[^<]{0,50})",body)[:4],"preview":re.sub(r"\\s+"," ",body[:180])})
 except Exception as e:out.append({"url":url,"error":str(e)[:250]})
pathlib.Path("docs/crafting-source-access.json").write_text(json.dumps(out,indent=2)+"\n")
print(out)
