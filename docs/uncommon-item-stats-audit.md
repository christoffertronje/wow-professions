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

## Second-source result (client data, November 2026)

`scripts/audit-uncommon-second-source.py` compared all **213** produced Uncommon item IDs against [Bind on Forever](https://bindonforever.com/items), including armor, equipment slot, binding, required character level, primary attributes, resistances and effects. Results are saved per item in `docs/uncommon-stats-second-source-audit.json`.

- **203 exact matches** after correcting harmless cloak categorization and matching a singular/plural item-name alias by exact item ID.
- **4 text/effect discrepancies**, no numerical disagreements in the compared armor, item level, required character level, attributes, binding or resistances.
- **6 inconclusive armor-kit effects** because the second source emits unresolved spell template parameters rather than trustworthy numbers.
- **0 unmatched item IDs or unavailable item pages**.

### Remaining effect cases

- **Fletcher's Gloves** (7348): the original tooltip shows a `-1% Parry` effect, while Bind on Forever expresses a positive Parry effect; additional Forever pages also disagree in how this effect is rendered. Retain the previous value and display a visible warning pending live in-game confirmation.
- **Nightscape Boots** (8197): older Forever/Wowhead tooltips say `+1 stealth`, Bind on Forever says `+1.2`. Retain the original value and display a visible warning pending in-game confirmation.
- **Red Whelp Gloves** (7284) and **Green Whelp Armor**: the main effect wording matches, but the first source includes extra `Proc chance` metadata absent from the second source. Preserve the recorded source annotation; it is **not independently verified** by the second source.
- **Six Mystic/Forceful armor kits**: the second source has undecoded effect parameters; do not replace source text with those placeholders.

These findings do **not** justify claiming 213 independently live-verified items. All item stats are still sourced from the game client and, where possible, cross-checked against a separate presentation of client data.

### Regression protection

`data/item-stats-corrections.json` now records the reviewed warnings for Fletcher's Gloves and Nightscape Boots. `scripts/build-item-stats.py` reapplies them on every import. `scripts/validate-item-stats.py` verifies both warnings remain, all 213 Uncommon item IDs join to the recipe catalog, and the 11 cloak tooltips are formatted as Back-slot items rather than armor class `Cloaks`.
