#!/usr/bin/env python3
"""Compare 513-record Forever recipe table to our unresolved Leatherworking entries.

The external source publishes a 4-number skill band; the first number is
claimed as the crafting/learn skill. Match UNIQUE normalized recipe names only,
and reject conflicts. This is a provenance-preserving fallback, not a guess.
"""
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import json
import pathlib
import re
import urllib.request

URL = "https://playfulls.com/professions/leatherworking/recipes"
CATALOG = pathlib.Path("data/leatherworking.json")
OUT = pathlib.Path("data/leatherworking-skills-extra.json")

def norm(value):
    return re.sub(r"[^a-z0-9]+", "", value.casefold())

request=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions-project/0.1)"})
with urllib.request.urlopen(request,timeout=80) as response:
    soup=BeautifulSoup(response.read(),"html.parser")
print("tables",len(soup.select("table")),"rows",len(soup.select("tr")))
rows=[]
for tr in soup.select("tr"):
    cells=tr.find_all(["td","th"],recursive=False)
    if len(cells)<3:continue
    name=cells[0].get_text(" ",strip=True)
    # Recipe names typically link to a detail view; use link name when available.
    links=[a for a in cells[0].select("a") if a.get_text(" ",strip=True)]
    if links:name=links[0].get_text(" ",strip=True)
    nums=[int(x) for x in re.findall(r"\d+",cells[1].get_text(" ",strip=True))]
    if not name or len(nums)<4 or not (1<=nums[0]<=450):continue
    rows.append({"name":name,"required":nums[0],"bands":nums[:4]})
if len(rows)<400:
    raise RuntimeError(f"Only {len(rows)} parsed, expected 500+: page format changed. No import.")
catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
by_name=defaultdict(list)
for r in catalog["recipes"]:by_name[norm(r["name"])].append(r)
counts=Counter(norm(x["name"]) for x in rows)
accepted={}
conflicts=[]
missing=[]
for row in rows:
    key=norm(row["name"])
    entries=by_name.get(key,[])
    if len(entries)!=1 or counts[key]!=1:continue
    item=entries[0]
    current=item.get("required")
    if current is not None and current!=row["required"]:
        conflicts.append({"name":row["name"],"spellId":item["id"],"current":current,"other":row["required"]})
    elif current is None:
        accepted[item["id"]]=row["required"]
if conflicts:
    # Don't abort reporting; block their use.
    print("Disagreements left untouched:",len(conflicts))
payload={"meta":{"source":URL,"parsedRows":len(rows),"matchedUnknown":len(accepted),"conflicts":len(conflicts),"note":"Reported first skill-band number. Name matched only when unique; no source is guaranteed authoritative."},"skillBySpellId":accepted,"conflicts":conflicts}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print("Accepted additional:",len(accepted),"conflicts:",len(conflicts))
