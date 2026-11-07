#!/usr/bin/env python3
"""Crosscheck unresolved Forever Leatherworking recipes against the 70862 catalog.

Only one-to-one name matches are accepted; known mismatches are reported,
not overwritten. Values are crosscheck evidence, not certainty of live availability.
"""
import json, pathlib, re, urllib.request
from collections import defaultdict, Counter
from html.parser import HTMLParser

URL="https://wowforevertalents.com/professions/leatherworking/"
INPUT=pathlib.Path("data/leatherworking.json")
OUTPUT=pathlib.Path("data/forever-70862-skill-crosscheck.json")

class LinkReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capturing=False;self.data=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            attr=dict(attrs)
            self.capturing="wowhead.com" in (attr.get("href") or "")
            if self.capturing:self.data=[]
    def handle_data(self,data):
        if self.capturing:self.data.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self.capturing:
            self.links.append(" ".join(" ".join(self.data).split()))
            self.capturing=False

def norm(v):return re.sub(r"[^a-z0-9]+","",v.casefold())
request=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions-skill-audit/0.1)"})
with urllib.request.urlopen(request,timeout=60) as response:
    markup=response.read().decode("utf-8","replace")
parser=LinkReader();parser.feed(markup)
recipes=json.loads(INPUT.read_text(encoding="utf-8"))["recipes"]
byname=defaultdict(list)
for r in recipes:
    if r.get("category")=="SEASON OF DISCOVERY":continue  # Historical duplicate spells are not evidence for Forever crafting requirements
    byname[norm(r["name"])].append(r)
candidate=[]
for link in parser.links:
    m=re.match(r"^(.*?)\s*[★◆]?\s+(\d{1,3})(?:\s+(\d{1,3}))?$",link)
    if not m:continue
    name=m.group(1).strip(" ★◆")
    level=int(m.group(3) or m.group(2))
    if 1<=level<=450 and len(name)>=3:candidate.append((name,level))
counts=Counter(norm(name) for name,_ in candidate)
accepted={};conflicts=[];matched=0
for name,level in candidate:
    key=norm(name)
    records=byname.get(key,[])
    if len(records)!=1 or counts[key]!=1:continue
    matched+=1
    r=records[0]
    if r["required"] is None:accepted[str(r["id"])]=level
    elif r["required"]!=level:conflicts.append({"name":name,"spellId":r["id"],"current":r["required"],"candidate":level})
if len(candidate)<400 or matched<300:
    raise RuntimeError(f"Unexpected coverage: links {len(parser.links)}, extracted {len(candidate)}, unique matches {matched}. Abort.")
payload={"meta":{"source":URL,"catalogBuild":"1.60.1.70862","extractedRows":len(candidate),"uniqueMatches":matched,"newSkills":len(accepted),"conflicts":len(conflicts),"method":"One-to-one normalized recipe name; requires validation against spell IDs when available"},"newSkillsBySpellId":accepted,"conflicts":conflicts}
OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print(payload["meta"])
