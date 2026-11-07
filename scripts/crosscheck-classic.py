#!/usr/bin/env python3
"""Cross-check Classic Leatherworking requirements against the Forever dataset.

Conservative report-only pass. NEVER overwrite Forever values or publish
Classic values as verified Forever requirements.
"""
import collections
import html
import json
import pathlib
import re
import urllib.request
from html.parser import HTMLParser

URL="https://warcraft.wiki.gg/wiki/Classic_leatherworking_patterns"
OUT=pathlib.Path("docs/classic-leatherworking-crosscheck.json")
DATA=pathlib.Path("data/leatherworking.json")

class TableReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables=[]
        self.current=None
        self.row=None
        self.cell=None
        self.depth=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="table":
            if self.current is None:
                self.current=[];self.depth=1
            else:self.depth+=1
        if self.current is None:return
        if tag=="tr" and self.depth==1:self.row=[]
        if tag in ("td","th") and self.row is not None and self.depth==1:self.cell=[]
        if tag=="br" and self.cell is not None:self.cell.append(" ")
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if self.current is None:return
        if tag in ("td","th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()));self.cell=None
        if tag=="tr" and self.row is not None:
            if self.row:self.current.append(self.row)
            self.row=None
        if tag=="table":
            self.depth-=1
            if self.depth==0:
                self.tables.append(self.current);self.current=None

def normalize(name):
    return re.sub(r"[^a-z0-9]+","",name.casefold())

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; wow-professions comparison/0.1)"})
    with urllib.request.urlopen(req,timeout=60) as res:
        return res.read().decode("utf-8","replace")

def parse(source):
    parser=TableReader()
    parser.feed(source)
    matches=[]
    for table in parser.tables:
        for row in table:
            # First columns: item/category/materials/skill (minimum)/other skill tiers/source
            if len(row)<7:continue
            if not re.fullmatch(r"\d{1,3}",row[3]):continue
            if not row[0] or row[0].casefold() in ("item","orange"):continue
            name=row[0].strip()
            if name.lower().startswith("image "):name=name[6:]
            if not name:continue
            matches.append({"name":name,"skill":int(row[3]),"source":row[-1],"materialsText":row[2]})
    return matches

catalog=json.loads(DATA.read_text(encoding="utf-8"))
classic=parse(fetch())
if len(classic)<100:
    raise RuntimeError(f"Only {len(classic)} Classic rows parsed; table layout may have changed. No report written.")
by_name=collections.defaultdict(list)
for r in catalog["recipes"]:by_name[normalize(r["name"])].append(r)
unique=[];ambiguous=[];unmatched=[]
for rec in classic:
    candidates=by_name.get(normalize(rec["name"]),[])
    if len(candidates)==1:
        r=candidates[0]
        unique.append({"spellId":r["id"],"name":r["name"],"classicSkill":rec["skill"],"foreverLearningSkill":r.get("required"),"classicSource":rec["source"],"skillMatches":r.get("required")==rec["skill"] if r.get("required") is not None else None})
    elif len(candidates)>1:
        ambiguous.append({"name":rec["name"],"candidateSpellIds":[r["id"] for r in candidates]})
    else:unmatched.append(rec["name"])
report={"reference":URL,"note":"Classic comparison only: NOT proof of Forever requirements or sources. Never auto-merge.", "classicRows":len(classic),"uniqueNameMatches":len(unique),"ambiguousMatches":len(ambiguous),"unmatchedClassicRows":len(unmatched),"matchedWithUnknownForeverSkill":sum(x["foreverLearningSkill"] is None for x in unique),"matchedWithDifferentKnownSkill":sum(x["skillMatches"] is False for x in unique),"matches":unique,"ambiguous":ambiguous,"notInForeverByName":unmatched}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("Cross-check:",len(classic),"Classic rows,",len(unique),"unique matches,",report["matchedWithUnknownForeverSkill"],"unknown Forever skills,",report["matchedWithDifferentKnownSkill"],"disagreements")
