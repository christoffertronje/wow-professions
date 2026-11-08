#!/usr/bin/env python3
"""Inspect rendered Forever Guide Leatherworking rows around known unknowns."""
import urllib.request,re,json,pathlib
from bs4 import BeautifulSoup
u="https://guide.wow4ever.se/en/professions/leatherworking"
req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions-skill-audit)"})
with urllib.request.urlopen(req,timeout=50) as r:html=r.read().decode("utf-8","replace")
doc=BeautifulSoup(html,"html.parser")
strings=["Big Voodoo Mask","Cured Rugged Hide","Guardian Belt","Toughened Leather Gloves","EG Link","Handstitched Leather Pants","learn at","Trainer"]
samples={}
for term in strings:
 hits=list(re.finditer(re.escape(term),html,re.I))
 samples[term]={"totalOccurrences":len(hits),"htmlContexts":[html[max(0,m.start()-300):m.start()+600] for m in hits[:3]]}
hints={
 "sampleRecipeElements":[{"tag":e.name,"class":e.get("class"),"text":e.get_text(" ",strip=True)[:450]} for e in doc.find_all(string=re.compile("Big Voodo|Cured Rugged|Guardian Belt"))[:8] for e in [e.parent.parent if e.parent and e.parent.parent else e.parent]],
 "dataAttributes":sorted({k for t in doc.find_all(True) for k in t.attrs if k.startswith("data-")})[:40],
 "scriptSources":[s.get("src","") for s in doc.select("script[src]")][-14:],
 "textExcerpt":doc.get_text(" ",strip=True)[1000:2600]
}
pathlib.Path("docs/eglink-leatherworking-details.json").write_text(json.dumps({"samples":samples,"hints":hints},indent=2,ensure_ascii=False)+"\n")
print({term:v["totalOccurrences"] for term,v in samples.items()})
