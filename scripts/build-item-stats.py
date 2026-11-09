#!/usr/bin/env python3
"""Build a separate item stats catalog for WoW Forever's all WoW Forever Leatherworking outputs.

Facts are sourced by exact produced item ID from Forever Talent's recorded
tooltip, not by name or spell-skill band. Preserve original tooltip lines and
all effects; parse simple numeric stats into structured fields. No inferred
values and no Classic fallback.
"""
import json,pathlib,re,urllib.request
from bs4 import BeautifulSoup

SOURCE_URL="https://wowforevertalent.com/professions/leatherworking/?acquisition=favor"
RECIPES=pathlib.Path("data/leatherworking.json")
OUTPUT=pathlib.Path("data/item-stats.json")
quality_reviews=json.loads(pathlib.Path("data/item-quality-corrections.json").read_text(encoding="utf-8"))["byItemId"]
r=json.loads(RECIPES.read_text(encoding="utf-8"))
selected=r["recipes"]
assert len(selected)==512, f"Recipe count changed: {len(selected)}"
request=urllib.request.Request(SOURCE_URL,headers={"User-Agent":"Mozilla/5.0 (compatible; Forgebook item stats importer)"})
with urllib.request.urlopen(request,timeout=90) as resp:soup=BeautifulSoup(resp.read(),"html.parser")

source={}
for a in soup.select("article.recipe-detail"):
    spell_node=a.select_one(".recipe-spell")
    facts=a.select_one("[data-output-facts]")
    if spell_node is None or facts is None:continue
    sm=re.fullmatch(r"Spell\s+(\d+)",spell_node.get_text(" ",strip=True))
    if not sm:continue
    sid=sm.group(1)
    item_id=str(facts.get("data-output-facts") or "")
    if not item_id.isdigit():continue
    lines=[li.get_text(" ",strip=True) for li in facts.select("ul > li")]
    effects=[p.get_text(" ",strip=True) for p in facts.select(".profession-output-effect")]
    src_link=facts.select_one(".profession-output-source a[href]")
    if sid in source:raise ValueError(f"Duplicate source spell ID: {sid}")
    source[sid]={"itemId":item_id,"lines":lines,"effects":effects,
        "link":src_link["href"] if src_link else None}

quality_names={"Poor","Common","Uncommon","Rare","Epic","Legendary","Artifact","Heirloom"}
bind_names={"Binds when picked up":"BoP","Binds when equipped":"BoE","Binds when used":"BoU","Soulbound":"Soulbound"}
primary_stat_names={"Strength","Agility","Stamina","Intellect","Spirit"}
items={}
errors=[]
for recipe in selected:
    spell_id=recipe["id"]
    item_id=str(recipe["itemId"])
    x=source.get(spell_id)
    if x is None or x["itemId"]!=item_id:
        errors.append(f"Missing source or mismatched output ID: {recipe['name']} ({spell_id} -> {item_id})")
        continue
    lines=x["lines"]
    if recipe["quality"].title() not in lines:
        # The older Forever Talent record predates the verified patch changing
        # Toughened Leather Armor from Common to Uncommon. All other records
        # still require an exact quality match to the source.
        revised=str(item_id)=="2314" and recipe["quality"]=="uncommon" and "Common" in lines and quality_reviews.get("2314")=="uncommon"
        if not revised:
            errors.append(f"Tooltip quality mismatch for {recipe['name']}: expected {recipe['quality']}: {lines[:4]}")
            continue
    stats={}
    resistances={}
    other_lines=[]
    item_level=None
    character_level=None
    armor=None
    slot=None
    armor_type=None
    binding=None
    for text in lines:
        if text in quality_names:continue
        if text in bind_names:
            binding=bind_names[text]
            continue
        if " · " in text and slot is None:
            slot,armor_type=(p.strip() for p in text.split(" · ",1))
            # Tooltip categorization sometimes says "Back · Cloaks", but
            # Cloaks is a category, NOT an equippable armor material.
            if slot=="Back" and armor_type in ("Cloak","Cloaks"):
                armor_type=None
            if slot in ("Bag","Quiver","Ammo Pouch") and armor_type in ("Bag","Bags","Quivers","Ammo Pouches"):
                armor_type=None
            continue
        if text in {"Back","Trinket","Finger","Neck","Ranged","Shirt","Tabard","Held In Off-hand","Main Hand","Off Hand","Two-Hand","One-Hand"} and slot is None:
            slot=text
            continue
        m=re.fullmatch(r"Item Level\s+(\d+)",text)
        if m:item_level=int(m.group(1));continue
        m=re.fullmatch(r"Requires Level\s+(\d+)",text)
        if m:character_level=int(m.group(1));continue
        m=re.fullmatch(r"(\d+) Armor",text)
        if m:armor=int(m.group(1));continue
        m=re.fullmatch(r"([+-]?\d+) (Strength|Agility|Stamina|Intellect|Spirit)",text)
        if m:stats[m.group(2)]=int(m.group(1));continue
        m=re.fullmatch(r"([+-]?\d+) (Arcane|Fire|Frost|Nature|Shadow|Holy) Resistance",text)
        if m:resistances[m.group(2)]=int(m.group(1));continue
        other_lines.append(text)
    # Armor-kit bonuses apply to TARGET gear, not to the consumable kit.
    # Display them as Use effects only; do not invent equippable attributes.
    if recipe["category"]=="Armor Kits":
        stats={}
        armor=None  # This number is the enhancement applied to target gear.
    if item_level is None:
        errors.append(f"Essential item level missing for {recipe['name']}: {lines}")
        continue
    if item_id in items:raise ValueError(f"Duplicate output item ID {item_id}")
    items[item_id]={
        "itemId":int(item_id),"recipeSpellId":spell_id,"name":recipe["name"],
        "quality":recipe["quality"],"itemLevel":item_level,"requiredCharacterLevel":character_level,
        "slot":slot,"armorType":armor_type,"armor":armor,
        "binding":binding,"stats":stats,"resistances":resistances,
        "effects":x["effects"],"otherTooltipLines":other_lines,
        "tooltipLines":lines,
        "source":{"type":"forever-item-tooltip","page":SOURCE_URL,"itemPage":x["link"],
          "gameBuild":"client-record-2026-10-17","verification":"client-data; live in-game not verified"}
    }
# Apply narrowly reviewed item-ID corrections AFTER importing the original
# tooltip. This prevents future source refreshes from removing confirmed
# effects (e.g. Swift Flight Bracers +41 Ranged Attack Power).
correction_path=pathlib.Path("data/item-stats-corrections.json")
if correction_path.exists():
    corrections=json.loads(correction_path.read_text(encoding="utf-8"))["byItemId"]
    for iid,patch in corrections.items():
        if iid not in items:raise ValueError(f"Item correction references unknown output item {iid}")
        for field in ("stats","resistances","effects","armor","requiredCharacterLevel","binding"):
            if field in patch:items[iid][field]=patch[field]
        if "reviewFlag" in patch:
            items[iid]["statReviewWarning"]=patch["reviewFlag"]
        items[iid]["reviewedCorrection"]={
            "source":patch.get("source"),
            "corroboration":patch.get("corroboration",[]),
            "reason":patch.get("reason")}
if errors:
    raise RuntimeError("WoW Forever item stats import requires full coverage; errors:\n"+"\n".join(errors[:25]))
assert len(items)==512,f"Expected all 512 produced items, got {len(items)}"
payload={"meta":{"scope":"All identified WoW Forever Leatherworking outputs, including materials and equipment",
 "items":len(items),"epicItems":70,"rareItems":201,"uncommonItems":214,"commonItems":27,"game":"WoW Forever",
 "source":SOURCE_URL,"recipeCatalogBuild":r["meta"].get("build"),
 "sourceEvidence":"Forever recorded item tooltip with original text preserved; not guaranteed unchanged on live servers",
 "note":"Unknown item attributes stay null/absent. No values inferred from Classic or skill-up tables."},
 "byItemId":items}
OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print(f"Imported {len(items)} WoW Forever produced item tooltip records; "
      f"{sum(bool(x['effects']) for x in items.values())} with special effects, "
      f"{sum(bool(x['stats']) for x in items.values())} with primary attributes, "
      f"{sum(bool(x['resistances']) for x in items.values())} with resistances.")
