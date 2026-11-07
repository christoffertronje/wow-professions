#!/usr/bin/env python3
"""Report (not automatically merge) independent Forever crafting skill values.

Extracts recipe rows from guildloot's public table. Pair names only when
unique in BOTH datasets; spell IDs are not exposed by this source.
"""
import collections,json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
URL="https://guildloot.de/en/beruf/forever/leatherworking/"
req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req,timeout=60) as r:html=r.read()
soup=BeautifulSoup(html,"html.parser")
catalog=json.loads(pathlib.Path("data/leatherworking.json").read_text())
norm=lambda n:re.sub(r"[^a-z0-9]+","",n.lower())
names=collections.defaultdict(list)
for r in catalog["recipes"]:names[norm(r["name"])].append(r)
rows=[]
for tr in soup.select("tr"):
  cells=tr.find_all(["td","th"],recursive=False)
  if len(cells)<3:continue
  skill=cells[1].get_text(" ",strip=True)
  if not re.fullmatch(r"\d{1,3}",skill):continue
  name=cells[0].get_text(" ",strip=True)
  if not name:continue
  rows.append((name,int(skill)))
counts=collections.Counter(norm(n) for n,v in rows)
matches=[];disagreements=[];unmatched=[]
for n,v in rows:
  candidates=names.get(norm(n),[])
  if len(candidates)!=1 or counts[norm(n)]!=1:
    unmatched.append(n);continue
  recipe=candidates[0]
  data={"spellId":recipe["id"],"name":recipe["name"],"craftingSkillReference":v,"currentRecordedLearnSkill":recipe["required"]}
  matches.append(data)
  if recipe["required"] is not None and recipe["required"]!=v:disagreements.append(data)
report={"source":URL,"matchedCount":len(matches),"sourceRows":len(rows),"disagreements":disagreements,"matchedWithCurrentUnknown":sum(r["currentRecordedLearnSkill"] is None for r in matches),"unmatchedCount":len(unmatched),"matches":matches}
if len(rows)<400 or len(matches)<300:raise RuntimeError(f"Failed validation: {len(rows)} rows; {len(matches)} matched")
pathlib.Path("docs/forever-skill-crosscheck.json").write_text(json.dumps(report,indent=2)+"\n")
print(f"Source {len(rows)}, unique matches {len(matches)}, unknown learn {report['matchedWithCurrentUnknown']}, disagreement {len(disagreements)}")
