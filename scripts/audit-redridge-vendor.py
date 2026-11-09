#!/usr/bin/env python3
"""Audit vendor Daniel Stitchsong recipes against our WoW Forever Leatherworking catalog.

Only read the explicitly labelled Leatherworking (N) profession requirement
on the vendor pattern table. Never infer crafting minimums from skill-up tiers.
Writes an inspectable comparison; does not silently modify the catalog.
"""
import json,re,pathlib,urllib.request,collections
from bs4 import BeautifulSoup

URL="https://www.wow-professions.com/forever/npc/daniel-stitchsong"
OUT=pathlib.Path("docs/daniel-stitchsong-recipe-audit.json")
req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions-vendor-audit/0.2)","Accept":"text/html"})
with urllib.request.urlopen(req,timeout=75) as resp:html=resp.read().decode("utf-8","replace")
soup=BeautifulSoup(html,"html.parser")
# Older vendor item tooltips use singular 'Shoulder'; the newer recipe
# spell and crafted item name uses plural 'Shoulders'. Match this known
# naming evolution without treating it as a missing recipe.
normalize=lambda x:re.sub(r"[^a-z0-9]+","",re.sub(r"\\bshoulder\\b","shoulders",x.casefold()))
catalog=json.loads(pathlib.Path("data/leatherworking.json").read_text())["recipes"]
byname=collections.defaultdict(list)
for recipe in catalog:byname[normalize(recipe["name"])].append(recipe)
rows=[]
for table in soup.find_all("table"):
    headers=[[cell.get_text(" ",strip=True)[:80] for cell in tr.find_all(["th","td"],recursive=False)] for tr in table.find_all("tr")[:3]]
    for tr in table.find_all("tr"):
        cells=tr.find_all(["th","td"],recursive=False)
        if len(cells)<3:continue
        celltexts=[c.get_text(" ",strip=True) for c in cells]
        line=" | ".join(celltexts)
        required=re.search(r"Leatherworking\s*\(\s*(\d{1,3})\s*\)",line,re.I)
        if not required:continue
        pattern=next((t for t in celltexts if t.lower().startswith("pattern:")),None)
        if not pattern:continue
        name=re.sub(r"^Pattern:\s*","",pattern,flags=re.I).strip()
        name=re.sub(r"\s+BoP\b","",name,flags=re.I).strip()
        name=re.sub(r"\s+Bind(?:s)? when picked up.*$","",name,flags=re.I).strip()
        # Name and tier are read independently from the row; only the
        # literal profession requirement is accepted as a candidate.
        rows.append({"name":name,"required":int(required.group(1)),"merchantFavor":re.findall(r"\b(?:30|60|90)\s*x?\s*Merchant",line,re.I),
            "rowText":line[:400],"itemUrls":[a.get("href","") for a in tr.find_all("a")][:4]})
counts=collections.Counter(normalize(x["name"]) for x in rows)
matched=[];missing=[];ambiguous=[];mismatches=[]
for row in rows:
    candidates=byname[normalize(row["name"])]
    if len(candidates)==1 and counts[normalize(row["name"])]==1:
        recipe=candidates[0]
        comparison={"name":row["name"],"spellId":recipe["id"],"vendorRequired":row["required"],"catalogCraftRequired":recipe.get("craftSkillRequired"),"references":row["itemUrls"]}
        matched.append(comparison)
        if row["required"]!=recipe.get("craftSkillRequired"):mismatches.append(comparison)
    elif not candidates:missing.append(row)
    else:ambiguous.append(row)
# Every name should resolve; reject missing/ambiguous vendor rows and any
# discrepancy between the pattern's professional requirement and the
# recipe minimum required to craft.
if len(rows)!=81 or len(matched)!=81 or missing or ambiguous or mismatches:
    raise RuntimeError(f"Vendor audit failed: rows={len(rows)}, matched={len(matched)}, missing={len(missing)}, ambiguous={len(ambiguous)}, mismatches={len(mismatches)}")
report={"vendor":"Daniel Stitchsong","location":"Three Corners, Redridge Mountains","source":URL,
    "tableRowCount":len(rows),"uniqueMatches":len(matched),"missingCount":len(missing),"ambiguousCount":len(ambiguous),"skillMismatchCount":len(mismatches),
    "matches":matched,"missing":missing,"ambiguous":ambiguous,"skillMismatches":mismatches,
    "htmlDiagnostics":{"totalTables":len(soup.find_all("table")),"size":len(html),"patternCount":html.lower().count("pattern:"),
     "sampleRows":rows[:6],"sampleHeaders":[[c.get_text(" ",strip=True) for c in tr.find_all(["th","td"],recursive=False)] for table in soup.find_all("table")[:2] for tr in table.find_all("tr")[:3]]}}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print({k:report[k] for k in ("tableRowCount","uniqueMatches","missingCount","ambiguousCount","skillMismatchCount")})
