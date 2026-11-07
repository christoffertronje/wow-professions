#!/usr/bin/env python3
"""One-time inspection of ForeverTome's publicly offered recipe snapshot.
No data is republished by this inspection task."""
import json, urllib.request, pathlib
URL="https://forevertome.com/data/recipes.yafo0pc388.json"
req=urllib.request.Request(URL,headers={"User-Agent":"WowProfessionsPrototype/0.1 (GitHub Pages fan project)"})
with urllib.request.urlopen(req,timeout=45) as response:
    content=response.read()
data=json.loads(content)
def describe(value,depth=0):
    if depth>=4: return {"type":type(value).__name__}
    if isinstance(value,dict):
        return {"type":"object","count":len(value),"keys":list(value)[:35],"children":{k:describe(v,depth+1) for k,v in list(value.items())[:8]}}
    if isinstance(value,list):
        return {"type":"array","length":len(value),"first":describe(value[0],depth+1) if value else None}
    return {"type":type(value).__name__,"example":str(value)[:130]}
report={"source":URL,"bytes":len(content),"structure":describe(data)}
path=pathlib.Path("docs/source-shape.json")
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("Wrote",path,"bytes",len(content))
