#!/usr/bin/env python3
"""Resolve nine missing Daniel Stitchsong shoulder recipes from Forever Talent.

Compares the vendor's pattern item IDs to individual recipe panels containing
spell IDs and skill requirements. Requires an exact item-ID match and skill 210.
"""
from bs4 import BeautifulSoup
import json, pathlib, urllib.request, re
SOURCE="https://wowforevertalent.com/professions/leatherworking/?acquisition=favor"
vendor=json.loads(pathlib.Path("docs/daniel-stitchsong-recipe-audit.json").read_text())
items={str(re.search(r"item=(\d+)",row["itemUrls"][0]).group(1)):row for row in vendor["missing"]}
req=urllib.request.Request(SOURCE,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions-vendor-gap/0.1)"})
with urllib.request.urlopen(req,timeout=80) as resp: html=resp.read()
soup=BeautifulSoup(html,"html.parser")
lines=[line.strip() for line in soup.stripped_strings if line.strip()]
results=[]
for pattern_item,row in items.items():
  hits=[i for i,line in enumerate(lines) if f"#{pattern_item}" in line or f"(#{pattern_item})" in line]
  candidates=[]
  for i in hits:
    before=lines[max(0,i-55):i+1]
    idx=[k for k,v in enumerate(before) if re.fullmatch(r"Spell\s+\d{5,8}",v,re.I)]
    last=before[idx[-1]] if idx else ""
    possible=re.search(r"Spell\s+(\d{5,8})",last,re.I)
    candidate={"spellId":possible.group(1) if possible else None,"contextBefore":before[-35:],
       "contextAfter":lines[i:i+20]}
    candidates.append(candidate)
  results.append({"vendorName":row["name"],"patternItemId":pattern_item,"vendorRequirement":row["required"],
     "candidateOccurrences":len(hits),"candidates":candidates})
report={"source":SOURCE,"missing":results,"debug":{"totalVisibleLines":len(lines),"patternIdHitCount":sum(len(r["candidates"]) for r in results)}}
pathlib.Path("docs/daniel-stitchsong-missing-spells.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print([(r["vendorName"],r["patternItemId"],[x["spellId"] for x in r["candidates"]]) for r in results])
