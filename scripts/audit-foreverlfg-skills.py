#!/usr/bin/env python3
"""Audit third recipe listing against our known minimum crafting skill values.

Source presents 'Gear · skill N' in a page covering ALL professions.
This is cross-check only. Never auto-import as the source can disagree with
Wowhead Forever on old trainer recipes.
"""
import json,re,urllib.request,pathlib,collections
from bs4 import BeautifulSoup

URL="https://foreverlfg.app/professions"
req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions skill audit)"})
with urllib.request.urlopen(req,timeout=60) as response:soup=BeautifulSoup(response.read(),"html.parser")
texts=[x.strip() for x in soup.stripped_strings if x.strip()]
norm=lambda s:re.sub(r"[^a-z0-9]+","",s.casefold())
matched=[]
catalog=json.loads(pathlib.Path("data/leatherworking.json").read_text())["recipes"]
known_names={norm(r["name"]) for r in catalog if not r["name"].startswith("Unresolved recipe #")}
for index,value in enumerate(texts):
    if norm(value) not in known_names:continue
    window=" ".join(texts[index+1:index+9])
    m=re.search("skill[ ]+([0-9]{1,3})",window,re.I)
    if m and len(value)<100:
        matched.append({"name":value,"skill":int(m.group(1))})
if len(matched)<150:raise ValueError(f"Unexpected third-source coverage: {len(matched)}")
catalog=json.loads(pathlib.Path("data/leatherworking.json").read_text())["recipes"]
by_name=collections.defaultdict(list)
for r in catalog:by_name[norm(r["name"])].append(r)
counts=collections.Counter(norm(x["name"]) for x in matched)
unique=[]
for x in matched:
    candidates=by_name.get(norm(x["name"]),[])
    if len(candidates)!=1 or counts[norm(x["name"])]!=1:continue
    r=candidates[0]
    unique.append({"id":r["id"],"name":r["name"],"wikiCategory":r["category"],"lfgSkill":x["skill"],"ourSkill":r["craftSkillRequired"]})
conflicts=[x for x in unique if x["ourSkill"] is not None and x["lfgSkill"]!=x["ourSkill"]]
unknown=[x for x in unique if x["ourSkill"] is None]
wiki=json.loads(pathlib.Path("docs/wiki-craft-skill-crosscheck.json").read_text())
bywiki={x["id"]:x for x in wiki["newCandidates"]}
agreed=[dict(x,wikiSkill=bywiki[x["id"]]["skill"],wikiSource=bywiki[x["id"]].get("wikiSource")) for x in unknown if x["id"] in bywiki and bywiki[x["id"]]["skill"]==x["lfgSkill"]]
report={"source":URL,"catalogRowsWithSkill":len(matched),"uniqueNameMatches":len(unique),"conflictsWithConfirmedMinimums":len(conflicts),"unknownWithThirdSource":len(unknown),"unknownWikiAgreement":len(agreed),"sourceConflicts":conflicts,"unverifiedCandidates":unknown,"wikiAgreements":agreed,"note":"Cross-check only. Do not automatically import sources without direct crafting evidence."}
pathlib.Path("docs/foreverlfg-crafting-crosscheck.json").write_text(json.dumps(report,indent=2)+"\n")
print({x:report[x] for x in ("catalogRowsWithSkill","uniqueNameMatches","conflictsWithConfirmedMinimums","unknownWithThirdSource","unknownWikiAgreement")})
