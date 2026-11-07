#!/usr/bin/env python3
"""Resolve known WoW icon FileDataIDs to filenames for the rendered recipe list.

Uses wowdev community listfile (FileDataID -> interface/icons/*.blp).
Only names matching an exact FileDataID are accepted. No guessed icons.
The webpage loads Blizzard-hosted JPG renditions at runtime.
"""
import json
import pathlib
import urllib.request

CATALOG=pathlib.Path("data/leatherworking.json")
LISTFILE_URL="https://github.com/wowdev/wow-listfile/releases/latest/download/community-listfile.csv"
payload=json.loads(CATALOG.read_text(encoding="utf-8"))
recipes=payload["recipes"]
wanted={int(r["iconFileDataId"]) for r in recipes if r.get("iconFileDataId")}
matched={}
req=urllib.request.Request(LISTFILE_URL,headers={"User-Agent":"wow-professions/0.1 (icon FileDataID mapping)"})
with urllib.request.urlopen(req,timeout=120) as response:
    for line in response:
        try:
            raw=line.decode("utf-8-sig").strip()
            number,path=raw.split(";",1)
            file_id=int(number)
            if file_id not in wanted:continue
            normalized=path.replace("\\","/").lower()
            if not normalized.startswith("interface/icons/"):continue
            base=normalized.rsplit("/",1)[-1]
            if not base.endswith((".blp",".tga")):continue
            name=base.rsplit(".",1)[0]
            if name and all(c.isascii() and (c.isalnum() or c=="_") for c in name):
                matched[file_id]=name
        except (UnicodeDecodeError,ValueError):
            continue
for r in recipes:
    r["iconName"]=matched.get(r.get("iconFileDataId"))
payload["meta"]["iconsResolved"]=sum(bool(r["iconName"]) for r in recipes)
payload["meta"]["iconsUnresolved"]=sum(not r["iconName"] for r in recipes)
payload["meta"]["iconMappingSource"]=LISTFILE_URL
payload["meta"]["qualityUnresolvedBreakdown"]={
    "noOutputItemId":sum(r["quality"]=="unknown" and not r.get("itemId") for r in recipes),
    "missingOrIncompleteItemRecord":sum(r["quality"]=="unknown" and bool(r.get("itemId")) for r in recipes)
}
CATALOG.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print("Icons:",payload["meta"]["iconsResolved"],"resolved /",len(recipes),"total")
print("Unknown quality:",payload["meta"]["qualityUnresolvedBreakdown"])
