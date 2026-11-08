#!/usr/bin/env python3
"""Compare Warcraft Wiki's 'Skill' column to our known craft minimums.
Only unique names that unambiguously match are considered. Do not import
any source disagreements without confirming which value is the craft minimum.
"""
import json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
from collections import defaultdict,Counter

URL="https://warcraft.wiki.gg/wiki/Forever_leatherworking_patterns"
req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions audit/0.1)"})
with urllib.request.urlopen(req,timeout=60) as resp:soup=BeautifulSoup(resp.read(),"html.parser")
catalog=json.loads(pathlib.Path("data/leatherworking.json").read_text())["recipes"]
norm=lambda s:re.sub(r"[^a-z0-9]+","",s.casefold())
by_name=defaultdict(list)
for x in catalog:by_name[norm(x["name"])].append(x)
rows=[]
for table in soup.select("table"):
  first=table.select_one("tr")
  headers=[x.get_text(" ",strip=True).lower() for x in first.find_all(["th","td"],recursive=False)] if first else []
  if len(table.select("tr"))<50:continue  # Four large recipe tables, identified by row count rather than sortable heading text
  for tr in table.select("tr")[1:]:
    td=tr.find_all(["td","th"],recursive=False)
    if len(td)<2:continue
    name=td[0].get_text(" ",strip=True).strip("[] ")
    skill=td[1].get_text(" ",strip=True)
    if not re.fullmatch(r"\\d{1,3}",skill):continue
    links=[a.get("href","") for a in td[0].select("a")][:4]
    rows.append({"name":name,"skill":int(skill),"links":links})
if len(rows)<400:raise RuntimeError(f"Unexpected wiki extraction: {len(rows)} rows; abort audit")
names=Counter(norm(x["name"]) for x in rows)
matches=[];duplicates=[];unmatched=[]
for x in rows:
  candidates=by_name.get(norm(x["name"]),[])
  if len(candidates)==1 and names[norm(x["name"])]==1:
    r=candidates[0]
    matches.append({"id":r["id"],"name":r["name"],"skill":x["skill"],"ourSkill":r["craftSkillRequired"],"category":r["category"],"links":x["links"]})
  elif len(candidates)==0:unmatched.append(x)
  else:duplicates.append(x)
disagree=[x for x in matches if x["ourSkill"] is not None and x["skill"]!=x["ourSkill"]]
new=[x for x in matches if x["ourSkill"] is None]
report={"source":URL,"wikiRows":len(rows),"uniqueMatches":len(matches),"newPotential":len(new),"disagreements":len(disagree),"duplicateOrAmbiguous":len(duplicates),"notMatched":len(unmatched),"conflicts":disagree,"newCandidates":new,"sampleRowLinks":rows[:10]}
pathlib.Path("docs/wiki-craft-skill-crosscheck.json").write_text(json.dumps(report,indent=2)+"\n")
print({k:report[k] for k in ("wikiRows","uniqueMatches","newPotential","disagreements","duplicateOrAmbiguous","notMatched")})
print("conflicts examples",disagree[:8])
