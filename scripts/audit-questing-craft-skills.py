#!/usr/bin/env python3
"""Extract explicitly stated minimum crafting skills from a Forever recipe page.

Uses the 'Requires Leatherworking N' field ONLY, never skill-up thresholds.
Matches unique recipe names excluding Season of Discovery duplicate spells.
Conflicts with our other independently sourced minimums remain unresolved,
and are reported separately rather than overwritten.
"""
import collections,json,pathlib,re,urllib.request
from bs4 import BeautifulSoup

URL="https://questing.wiki/wow-forever/professions/leatherworking/"
BASE=pathlib.Path("data/leatherworking.json")
VERIFIED=pathlib.Path("data/verified-crafting-skills.json")
OUTPUT=pathlib.Path("data/questing-crafting-skills.json")
norm=lambda x:re.sub(r"[^a-z0-9]+","",x.casefold())

req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions crosscheck)"})
with urllib.request.urlopen(req,timeout=80) as resp:
    soup=BeautifulSoup(resp.read(),"html.parser")
allrecipes=json.loads(BASE.read_text(encoding="utf-8"))["recipes"]
byname=collections.defaultdict(list)
for entry in allrecipes:
    if entry.get("category")!="SEASON OF DISCOVERY" and not entry["name"].startswith("Unresolved recipe #"):
        byname[norm(entry["name"])].append(entry)
existing=json.loads(VERIFIED.read_text(encoding="utf-8"))["skillsBySpellId"]
extracted=[]
for head in soup.select("h2"):
    name=head.get_text(" ",strip=True)
    if not name or norm(name) not in byname:continue
    parent=head
    found=None
    for depth in range(7):
        parent=parent.parent
        if parent is None:break
        # Prefer nearest component wrapping one recipe, not the whole page.
        if len(parent.select("h2"))!=1:continue
        t=parent.get_text(" ",strip=True)
        m=re.search(r"Requires Leatherworking\s+(\d{1,3})\b",t)
        if m:
            skill=int(m.group(1))
            if skill>=1 and skill<=450:found=skill
            break
    if found is not None:
        extracted.append({"name":name,"required":found})
counts=collections.Counter(norm(x["name"]) for x in extracted)
accepted={};conflicts=[];ignored=[]
for entry in extracted:
    name=entry["name"];key=norm(name)
    matches=byname[key]
    if len(matches)!=1 or counts[key]!=1:
        ignored.append(name);continue
    r=matches[0];sid=str(r["id"]);skill=entry["required"]
    old=existing.get(sid)
    if old is not None and old["required"]!=skill:
        conflicts.append({"spellId":sid,"name":name,"otherSource":old["required"],"questing":skill})
    else:
        accepted[sid]={"required":skill,"source":"questing-forever-required-skill","reference":URL}
if len(extracted)<350:
    raise RuntimeError(f"Source markup insufficient: parsed {len(extracted)} entries, expected 350+; no update")
payload={"meta":{"source":URL,"extracted":len(extracted),"safeMatches":len(accepted),"conflicts":len(conflicts),"unmatched":len(ignored),"note":"Only 'Requires Leatherworking' fields, no skill-up values"},"skillsBySpellId":accepted,"conflicts":conflicts}
OUTPUT.write_text(json.dumps(payload,separators=(",",":"))+"\n")
print(payload["meta"])
print("Conflicts sample:",conflicts[:8])
