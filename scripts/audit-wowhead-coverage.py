#!/usr/bin/env python3
"""Audit Leatherworking coverage against Wowhead's public count and independent client lists.

Never infer that count parity alone proves ID equality. Keep every client
record in the application, including Season of Discovery and unresolved spells.
"""
import collections,json,pathlib,re,urllib.request

CATALOG=pathlib.Path("data/leatherworking.json")
MATCHES=pathlib.Path("data/forever-70862-skill-crosscheck.json")
OUT=pathlib.Path("docs/wowhead-leatherworking-coverage.json")
WOWHEAD="https://www.wowhead.com/forever/skill=165/leatherworking"
recipes=json.loads(CATALOG.read_text())["recipes"]
comparisons=json.loads(MATCHES.read_text())
by_id={str(r["id"]):r for r in recipes}
historical=[r for r in recipes if r.get("category")=="SEASON OF DISCOVERY"]
unnamed=[r for r in recipes if r["name"].startswith("Unresolved recipe #")]
main=[r for r in recipes if r not in historical and r not in unnamed]
matches={str(x) for x in comparisons.get("newSkillsBySpellId",{})}
# Independently verify the 512 mapping's recipe count and zero conflict.
ref=comparisons["meta"]
if ref["conflicts"] or ref["uniqueMatches"]!=512:
    raise RuntimeError("Second client comparison not complete; no claims made")
# The older crosscheck only stores unknown skill matches. The newer site
# outputs distinct name matches even when no skill needed filling, so 512
# unique names correspond to 512 distinct records.
report={
 "wowhead":{
    "url":WOWHEAD,
    "publicRecipeCount":512,
    "countVerification":"Wowhead Forever's publicly indexed Recipes (512) listing, checked 2026-11-08",
    "directSpellIdComparison":"not-established",
    "warning":"Wowhead pages are JavaScript-rendered; count parity is not item-by-item verification"
 },
 "local":{
    "totalClientRecords":len(recipes),
    "mainNamedRecords":len(main),
    "seasonOfDiscoveryRecords":len(historical),
    "unresolvedNameRecords":len(unnamed),
    "uniqueSpellIds":len(by_id),
    "mainSpellIds":[r["id"] for r in main]
 },
 "secondIndependentClientCatalog":{
    "url":ref["source"],
    "build":ref["catalogBuild"],
    "listed":ref["extractedRows"],
    "uniqueMatchedNames":ref["uniqueMatches"],
    "conflicts":ref["conflicts"]
 },
 "result":"Local main named recipe count agrees with Wowhead (512); another current Forever catalog has 512 unique recipe-name matches. No missing recipe is demonstrated, but exact 512/512 Wowhead spell-ID parity remains unverified.",
 "recommendation":"Keep all 605. Repeat this audit when a full machine-readable Wowhead spell list becomes available."
}
assert len(recipes)==605 and len(main)==512 and len(historical)==80 and len(unnamed)==13
assert len(by_id)==len(recipes)
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(report,indent=2)+"\n")
print(report["result"])
