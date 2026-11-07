#!/usr/bin/env python3
"""Audit raw skill-line minimum vs learn and trivial thresholds; no mutations."""
import json,urllib.request,pathlib,collections
url="https://forevertome.com/data/recipes.yafo0pc388.json"
req=urllib.request.Request(url,headers={"User-Agent":"wow-professions-data-audit/0.1"})
with urllib.request.urlopen(req,timeout=90) as resp:d=json.load(resp)
rs=[r for r in d["recipes"] if 165 in r.get("professionIds",[]) or r.get("professionId")==165]
out=[]
for r in rs:
  lines=[x for x in r.get("skillLines",[]) if x.get("professionId")==165 or x.get("skillLineId")==165]
  out.append({"id":r["id"],"name":r["name"],"skillRequired":r.get("skillRequired"),"skillTrivial":r.get("skillTrivial"),"skillUpStart":r.get("skillUpStart"),"minimums":[x.get("minimum") for x in lines],"trivialLow":[x.get("trivialLow") for x in lines],"trivialHigh":[x.get("trivialHigh") for x in lines]})
dist=lambda field:dict(collections.Counter(str(x.get(field)) for x in out).most_common(20))
mins=collections.Counter(v for r in out for v in r["minimums"])
audit={"count":len(out),"rawSkillRequired":dist("skillRequired"),"minimums":dict(mins.most_common(35)),"sampleFirst":out[:25],"sampleHigher": [r for r in out if max(r["minimums"] or [0])>1][:25]}
pathlib.Path("docs").mkdir(exist_ok=True)
pathlib.Path("docs/skill-field-audit.json").write_text(json.dumps(audit,indent=2)+"\n")
print("Minimums",audit["minimums"])
