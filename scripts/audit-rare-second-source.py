#!/usr/bin/env python3
"""Audit Rare Leatherworking item stats against newer WoW Forever game data.

Match ONLY by produced item ID, compare independently extracted fields, record
both sides of discrepancies and never mutate the published item-stats file.
Source: Bind on Forever, client build 1.60.1.70862 (2026-11-07).
"""
import concurrent.futures,json,pathlib,re,urllib.request,urllib.error,time
from bs4 import BeautifulSoup

ROOT=pathlib.Path(".")
INPUT=json.loads((ROOT/"data/item-stats.json").read_text(encoding="utf-8"))
ITEMS=INPUT["byItemId"]
REPORT=ROOT/"docs/rare-stats-second-source-audit.json"
assert len(ITEMS)==201
BASE="https://bindonforever.com/item/"
BINDINGS={"Binds when picked up":"BoP","Binds when equipped":"BoE","Binds when used":"BoU","Soulbound":"Soulbound"}
ATTR={"Strength","Agility","Stamina","Intellect","Spirit"}
SCHOOLS={"Arcane","Fire","Frost","Nature","Shadow","Holy"}
SLOTS={"Head","Neck","Shoulder","Chest","Waist","Legs","Feet","Wrist","Hands","Finger","Trinket","Back","Main Hand","One-Hand","Two-Hand","Off Hand","Held In Off-hand","Ranged","Shirt","Tabard"}
def norm(value):
    return re.sub(r"\s+"," ",str(value or "").strip()).casefold().rstrip(".")
def fetch_one(pair):
    iid,old=pair
    url=BASE+iid
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; Forgebook source checking; item-id verified)"})
        with urllib.request.urlopen(req,timeout=25) as response:
            html=response.read(300000).decode("utf-8","replace")
        soup=BeautifulSoup(html,"html.parser")
        tooltip=soup.select_one("div.tt.wow-tt")
        if not tooltip:return {"itemId":iid,"name":old["name"],"url":url,"status":"source-unavailable","reason":"Tooltip not found"}
        item_heading=tooltip.select_one("p.name")
        source_name=item_heading.get_text(" ",strip=True) if item_heading else None
        fields={"name":source_name,"itemLevel":None,"requiredCharacterLevel":None,"slot":None,"armorType":None,
            "armor":None,"binding":None,"stats":{},"resistances":{},"effects":[]}
        desc=soup.find("meta",attrs={"name":"description"})
        m=re.search(r"item level\s+(\d+)",desc.get("content","") if desc else "",re.I)
        if m:fields["itemLevel"]=int(m.group(1))
        for p in tooltip.find_all("p",recursive=False):
            line=p.get_text(" ",strip=True)
            if p.get("class") and "name" in p["class"]:continue
            if "row" in (p.get("class") or []):
                spans=p.find_all("span",recursive=False)
                if spans:
                    fields["slot"]=spans[0].get_text(" ",strip=True) or None
                    if len(spans)>1:fields["armorType"]=spans[1].get_text(" ",strip=True) or None
                continue
            if "green" in (p.get("class") or []) or line.startswith(("Equip:","Use:","Chance on hit:")):
                fields["effects"].append(line)
                continue
            if line in BINDINGS:fields["binding"]=BINDINGS[line];continue
            m=re.fullmatch(r"(\d+) Armor",line)
            if m:fields["armor"]=int(m.group(1));continue
            m=re.fullmatch(r"Requires Level\s+(\d+)",line)
            if m:fields["requiredCharacterLevel"]=int(m.group(1));continue
            m=re.fullmatch(r"([+-]?\d+)\s+(.+)",line)
            if m:
                name=m.group(2)
                if name in ATTR:fields["stats"][name]=int(m.group(1));continue
                if name.endswith(" Resistance") and name.removesuffix(" Resistance") in SCHOOLS:
                    fields["resistances"][name.removesuffix(" Resistance")]=int(m.group(1));continue
        if source_name is None or norm(source_name)!=norm(old["name"]):
            return {"itemId":iid,"name":old["name"],"url":url,"status":"identity-mismatch","sourceName":source_name}
        problems=[]
        checked=[]
        for field in ["itemLevel","requiredCharacterLevel","slot","armorType","armor","binding"]:
            left=old.get(field);right=fields.get(field)
            if field=="armorType":
                left=(left or "").replace(" Armor","")
                right=(right or "").replace(" Armor","")
            if left is None and right is None:continue
            if right is None:continue  # unavailable source field: not a discrepancy
            checked.append(field)
            if left!=right:problems.append({"field":field,"ours":old.get(field),"source":fields.get(field)})
        for field in ["stats","resistances"]:
            left=old.get(field) or {};right=fields.get(field) or {}
            checked.append(field)
            if left!=right:problems.append({"field":field,"ours":left,"source":right})
        ours={norm(e) for e in old.get("effects",[])}
        newer={norm(e) for e in fields["effects"]}
        if ours or newer:
            checked.append("effects")
            if ours!=newer:problems.append({"field":"effects","ours":old.get("effects",[]),"source":fields["effects"]})
        return {"itemId":iid,"name":old["name"],"url":url,
                "status":"difference" if problems else "match",
                "checkedFields":checked,"differences":problems,
                "source":fields,"oldBuild":"2026-10-17","newBuild":"1.60.1.70862"}
    except Exception as e:
        return {"itemId":iid,"name":old["name"],"url":url,"status":"source-unavailable","reason":str(e)[:160]}

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    results=list(ex.map(fetch_one,sorted(ITEMS.items(),key=lambda v:int(v[0]))))
counts={status:sum(x["status"]==status for x in results)
        for status in ["match","difference","source-unavailable","identity-mismatch"]}
summary={"totalRare":len(ITEMS),**counts,
 "sourcesFetched":counts["match"]+counts["difference"],
 "fullyMatching":counts["match"],
 "disagreements":counts["difference"],
 "fieldsWithDisagreements":{}}
for item in results:
    if item["status"]!="difference":continue
    for p in item["differences"]:
        k=p["field"];summary["fieldsWithDisagreements"][k]=summary["fieldsWithDisagreements"].get(k,0)+1
payload={"meta":{"firstSource":INPUT["meta"]["source"],"secondSource":"https://bindonforever.com/items",
    "secondSourceClientBuild":"1.60.1.70862",
    "matchingMethod":"Exact output item ID and name, field-by-field; absent source fields not treated as contradictions",
    "caveat":"Both references use game client records, not 201 independent live in-game observations. No source conflict automatically changes the published site."},
 "summary":summary,"results":results}
REPORT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(summary)
