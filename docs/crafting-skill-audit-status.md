# WoW Forever Leatherworking crafting requirements

## Published catalog

**512 identified main-catalog recipes, all 512 with source-backed minimum crafting skill requirements.** The published JSON and UI exclude **80 Season of Discovery records** and **13 unidentified spells** present in the upstream client data.

- Published data: `data/leatherworking.json` (512 recipes).
- Build: `scripts/build-data.py` filters out Season of Discovery / unidentified client entries before writing the public data.
- Validation: `scripts/validate-crafting-skills.py` rejects a non-512 catalog, invalid skill requirements, duplicate spell IDs, and historical entries.
- Underlying source and evidence mappings are retained in the repository for audit purposes only, not displayed in the recipe browser.

## Interpretation and limitations

A source-backed minimum is **not** proof a recipe can currently be crafted or obtained in live WoW Forever; the 512-item scope is based on identified main-catalog recipes and Forever-specific reference tables. The game client snapshot contains historical/other-mode entries, and further live-game availability verification may still be required.

`craftSkillRequired` represents the minimum profession skill to craft a recipe as supported by the cited source; **yellow, green and grey skill-up thresholds are excluded**. The website links to a skill source on each expanded recipe. Some requirements are corroborated by multiple reference tables rather than observed personally in-game.

## Key regression examples

- Toughened Leather Gloves (spell 3770): 110, not yellow threshold 135
- Heavy Armor Kit (3780): 150
- Thick Armor Kit (10487): 200
- Cured Rugged Hide (19047): 250

The 80 Season of Discovery and 13 unidentified spell records are not missing work for the user's requested WoW Forever-only app. They must not be reintroduced by future data imports.
