#!/usr/bin/env python3
"""Build a public, minimal WoW Forever character snapshot for GitHub Pages.

Requires Battle.net app CLIENT_ID and CLIENT_SECRET in the action environment.
Only a deliberately configured public character is fetched. Never publish tokens.
"""
import base64
import datetime as dt
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

REGION = "eu"
SLUG = "majblomma-tronjesson"
ARMORY = "https://armorywowforever.com/c/forever/eu/pvp/Majblomma-Tronjesson"
DEST = Path("data/armory-majblomma.json")
SLOTS = {
    "HEAD": "Head", "SHOULDER": "Shoulder", "CHEST": "Chest",
    "WRIST": "Wrist", "HAND": "Hands", "HANDS": "Hands",
    "WAIST": "Waist", "LEGS": "Legs", "FEET": "Feet",
    "BACK": "Back",
}
STATS = {"STRENGTH": "Strength", "AGILITY": "Agility",
         "STAMINA": "Stamina", "INTELLECT": "Intellect", "SPIRIT": "Spirit"}


def request_json(url, *, headers=None, body=None):
    req = urllib.request.Request(url, data=body, headers=headers or {},
                                 method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=25) as res:
        return json.load(res)


def as_name(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("name") or value.get("en_US") or value.get("en_GB") or ""
    return ""


def as_type(value):
    if isinstance(value, str):
        return value.upper()
    if isinstance(value, dict):
        return (value.get("type") or "").upper()
    return ""


def normalize_equipment(payload):
    gear = {}
    for entry in payload.get("equipped_items", []):
        slot = SLOTS.get(as_type(entry.get("slot")))
        if not slot:
            continue
        # Off-hand/ring variants are not part of the current craftable gear planner.
        result = {"name": as_name(entry.get("name")), "itemId": entry.get("item", {}).get("id"),
                  "armor": None, "stats": {}, "effects": []}
        armor = entry.get("armor")
        if isinstance(armor, dict) and isinstance(armor.get("value"), (int, float)):
            result["armor"] = armor["value"]
        for stat in entry.get("stats") or []:
            key = STATS.get(as_type(stat.get("type")))
            if key and isinstance(stat.get("value"), (int, float)):
                value = stat["value"]
                if stat.get("is_negated"):
                    value = 0
                result["stats"][key] = result["stats"].get(key, 0) + value
        for effect in entry.get("spells") or []:
            value = as_name(effect.get("description"))
            if value:
                result["effects"].append(value)
        gear[slot] = result
    return gear


def find_skill(payload):
    # Blizzard returns profession and skill tiers, often in primary[].
    for prof in payload.get("primaries") or []:
        name = as_name(prof.get("profession"))
        if name.lower() != "leatherworking":
            continue
        tiers = prof.get("tiers") or []
        skills = [t.get("skill_points") for t in tiers if isinstance(t.get("skill_points"), int)]
        if skills:
            return max(skills)
        if isinstance(prof.get("skill_points"), int):
            return prof["skill_points"]
    return None


def main():
    cid, secret = os.getenv("BNET_CLIENT_ID"), os.getenv("BNET_CLIENT_SECRET")
    if not cid or not secret:
        raise SystemExit("Battle.net credentials missing. Configure repository Actions secrets.")
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    token = request_json("https://oauth.battle.net/token",
                         headers={"Authorization": "Basic " + basic,
                                  "Content-Type": "application/x-www-form-urlencoded"},
                         body=b"grant_type=client_credentials")["access_token"]
    base = f"https://{REGION}.api.blizzard.com/profile/wow/character/{SLUG}"
    query = "?namespace=profile-forever-eu&locale=en_GB"
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    profile = request_json(base + query, headers=headers)
    equipment = request_json(base + "/equipment" + query, headers=headers)
    name = as_name(profile.get("name"))
    surname = as_name(profile.get("surname"))
    level = profile.get("level")
    if not isinstance(level, int) or not 1 <= level <= 60:
        raise ValueError("Invalid character level in profile")
    if not equipment.get("equipped_items"):
        raise ValueError("Equipment response does not contain equipped_items")
    professions = {}
    try:
        professions = request_json(base + "/professions" + query, headers=headers)
    except Exception as exc:
        print(f"Optional professions endpoint unavailable: {type(exc).__name__}")
    snapshot = {
        "schema": 1, "source": "Blizzard Battle.net WoW Forever Character Profile API",
        "armoryUrl": ARMORY, "region": REGION, "slug": SLUG,
        "fetchedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "character": {"name": (name + " " + surname).strip(), "level": level,
                      "class": as_name(profile.get("character_class") or profile.get("playable_class")),
                      "leatherworkingSkill": find_skill(professions)},
        "equipped": normalize_equipment(equipment),
    }
    if not snapshot["equipped"]:
        raise ValueError("No recognized gear slots; refusing empty snapshot")
    DEST.parent.mkdir(exist_ok=True, parents=True)
    DEST.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {DEST} for {snapshot['character']['name']}, level {level}, "
          f"{len(snapshot['equipped'])} equipment slots.")


if __name__ == "__main__":
    main()
