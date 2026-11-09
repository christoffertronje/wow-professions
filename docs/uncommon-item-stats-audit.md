# Uncommon (green) Leatherworking item stats

## Import completed — 2026-11-09

The Forgebook item stats data file `data/item-stats.json` includes all **213 Uncommon (green)** and **201 Rare (blue)** produced Leatherworking items, totaling **414 entries**. All are joined by exact produced **item ID and crafting spell ID**, not by fuzzy name.

The importer `scripts/build-item-stats.py` extracts recorded WoW Forever tooltip facts from Forever Talent, without inventing missing attributes. The source probe `docs/uncommon-stats-source-probe.json` confirmed **213/213** corresponding source panels with exact produced item IDs, recorded Uncommon quality, and item level. Strict validation in `scripts/validate-item-stats.py` rejects missing or mismatched entries and protects earlier Rare corrections.

Among the 213 Uncommon items:
- 186 have one or more primary attributes (Strength/Agility/Stamina/Intellect/Spirit)
- 84 have one or more recorded effects (Equip or Use)
- 11 have one or more resistances
- 13 have no equipment slot, including armor kits, quivers, ammo pouches and the Gordok Ogre Suit. This is intentional: unknown or inapplicable slots must not be fabricated.

The frontend in `index.html` now displays the same tooltip layout for green and blue items, with a **green name** for Uncommon and blue for Rare, while displaying exact recorded armor, level requirements, attributes and effects.

## Evidence and open verification

The source uses recorded client tooltip data from October 2026. These are **not** claims of live in-game testing. The scripts `scripts/audit-uncommon-second-source.py` and workflow `.github/workflows/audit-uncommon-second-source.yml` compare all 213 item IDs against the newer Bind on Forever client snapshot (build 1.60.1.70862); consult `docs/uncommon-stats-second-source-audit.json` once published. The initial import being complete **does not by itself establish** that all 213 values match the newer client build.

Disputed values must be reviewed independently; no automatic overwrites are allowed based on unparsed spell-effect placeholders, Classic fallback, missing source facts or item name aliases. Older verified Rare corrections and the Core Armor Kit warning remain in place.
