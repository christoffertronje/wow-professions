#!/usr/bin/env python3
"""Non-republishing diagnostic: inspect availability of Wowhead's structured recipe table."""
import json,pathlib,re,urllib.request,urllib.error
URL="https://www.wowhead.com/forever/skill=165/leatherworking"
OUT=pathlib.Path("docs/wowhead-direct-access.json")
result={"url":URL,"method":"HTTP page HTML inspection, no content republished"}
try:
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions-recipe-audit/0.1)","Accept":"text/html"})
    with urllib.request.urlopen(req,timeout=35) as resp:
        content=resp.read()
        raw=content.decode("utf-8","replace")
        result.update({"status":resp.status,"bytes":len(content),"hasListview":bool(re.search(r"new\\s+Listview\\s*\\(",raw)),"hasRecipeMarker":"recipes" in raw,"hasSpellData":bool(re.search(r"spell\\W+\\d{4,}",raw)),"blocked":any(x in raw.lower() for x in ("just a moment","verify you are human","access denied"))})
except Exception as e:
    result.update({"error":str(e)[:500]})
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(result,indent=2)+"\n")
print(result)
