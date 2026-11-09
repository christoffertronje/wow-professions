#!/usr/bin/env python3
"""Inspect output tooltip availability and actual rarity for non-Epic/Rare/Uncommon records."""
import json,pathlib,re,urllib.request,collections
from bs4 import BeautifulSoup
d=json.loads(pathlib.Path("data/leatherworking.json").read_text())
targets=[r for r in d["recipes"] if r["quality"] in ("common","unknown")]
assert len(targets)==60
req=urllib.request.Request("https://wowforevertalent.com/professions/leatherworking/?acquisition=favor",headers={"User-Agent":"Mozilla/5.0 (Forgebook remaining item source audit)"})
with urllib.request.urlopen(req,timeout=90) as res:soup=BeautifulSoup(res.read(),"html.parser")
by_spell={}
for article in soup.select("article.recipe-detail"):
 sp=article.select_one(".recipe-spell");facts=article.select_one("[data-output-facts]")
 if sp is None or facts is None:continue
 match=re.fullmatch(r"Spell\s+(\d+)",sp.get_text(" ",strip=True))
 if match:by_spell[match.group(1)]=facts
qualities={"poor","common","uncommon","rare","epic","legendary","artifact","heirloom"}
entries=[]
for recipe in targets:
 facts=by_spell.get(recipe["id"])
 lines=[li.get_text(" ",strip=True) for li in facts.select("ul > li")] if facts else []
 q=next((x.lower() for x in lines if x.lower() in qualities),None)
 skill=next((x for x in lines if x.startswith("Item Level")),None)
 entries.append({"name":recipe["name"],"spellId":recipe["id"],"itemId":recipe["itemId"],"catalogQuality":recipe["quality"],"sourceQuality":q,"itemIdMatch":bool(facts and facts.get("data-output-facts")==str(recipe["itemId"])),"itemLevel":skill,"lines":lines,"hasGearSlot":any(" · " in x for x in lines),"effects":[p.get_text(" ",strip=True) for p in facts.select(".profession-output-effect")] if facts else []})
summary={"total":len(entries),"itemIdMatches":sum(x["itemIdMatch"] for x in entries),"sourceQuality":dict(collections.Counter(x["sourceQuality"] for x in entries)),"knownItemLevel":sum(bool(x["itemLevel"]) for x in entries),"withEquipmentSlot":sum(x["hasGearSlot"] for x in entries)}
out={"summary":summary,"entries":entries}
pathlib.Path("docs/remaining-item-stats-probe.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(summary)
