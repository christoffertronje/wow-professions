#!/usr/bin/env python3
"""Extract recorded learning-skill requirements by SPELL ID.

Reference: https://wowforevertalent.com/professions/leatherworking/
Only numeric data-learning-requirement values from recipe details are used.
Unknown values stay unknown. Do not derive learn ranks from skill-up colors.
"""
import json
import pathlib
import re
import urllib.request
from collections import Counter

URL="https://wowforevertalent.com/professions/leatherworking/"
OUTPUT=pathlib.Path("data/leatherworking-skills.json")
request=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; WoWProfessions/0.1)"})
with urllib.request.urlopen(request,timeout=75) as response:
    html=response.read().decode("utf-8","replace")
block_pattern=re.compile(r'<article\b[^>]*class="[^"]*\brecipe-detail\b[^"]*"[^>]*>.*?</article>',re.S|re.I)
spell_pattern=re.compile(r'<p class="recipe-spell">\s*Spell\s+(\d+)\s*</p>',re.I)
learn_pattern=re.compile(r'<p class="recipe-learning"[^>]*data-learning-requirement="(\d+)"',re.I)
records={}
details=0
conflicts=[]
for m in block_pattern.finditer(html):
    block=m.group()
    spell=spell_pattern.search(block)
    if not spell:continue
    details+=1
    ident=spell.group(1)
    learn=learn_pattern.search(block)
    value=int(learn.group(1)) if learn else None
    if ident in records and records[ident]!=value:
        conflicts.append((ident,records[ident],value))
    records[ident]=value

if conflicts:raise RuntimeError(f"Conflicting requirements: {conflicts[:6]}")
known=sum(v is not None for v in records.values())
if not 550<=len(records)<=650 or not 400<=known<=600:
    raise RuntimeError(f"Unexpected page coverage: {len(records)} spells, {known} known requirements; abort")
OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_text(json.dumps({
    "meta":{
        "source":URL,
        "matchingKey":"recipe spell ID",
        "recipeCount":len(records),
        "knownRequirements":known,
        "unknownRequirements":len(records)-known,
        "note":"Recorded learning requirements may be recipe-item usage skills, not verified trainer availability."
    },
    "skillBySpellId":records
},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print(f"Extracted {known}/{len(records)} recorded learning requirements from {details} details")
