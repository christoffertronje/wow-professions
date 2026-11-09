# Epic (purple) Leatherworking item stats — 2026-11-09

## Coverage

Forgebook now includes tooltip stats for all **38 Epic Leatherworking outputs**, alongside the **201 Rare** and **213 Uncommon** items (total **452** item-ID-keyed records). The source is the Forever Talent item-tooltip dataset. The importer uses exact crafting spell IDs and produced item IDs and rejects missing item quality or item levels.

`scripts/validate-item-stats.py` ensures all 38 Epic entries have matching recipe spell IDs, item IDs, Epic quality and a valid item level. Previous Rare/Uncommon corrections are still protected. In Forgebook, Epic item names appear purple using the same WoW-inspired tooltip layout.

## Independent client-source crosscheck

The full field comparison against [Bind on Forever](https://bindonforever.com/items) is saved in `docs/epic-stats-second-source-audit.json` (client build 1.60.1.70862). The initial audit found **35 exact matches out of 38** and three differences, none due to an incorrect item-ID join.

1. **Dreamscale Breastplate**, item `20380`: missing `Equip: Restores 4 mana per 5 sec.` in the imported older tooltip. **Corrected** and preserved in `data/item-stats-corrections.json`; backed by Wowhead Forever, SenseOS and GuildLoot.
2. **Invulnerable Mail**, item `12641`: identical item mechanics but different effect text formatting; the newer source repeats `sec sec` and omits proc metadata. The original sourced tooltip, consistent with Wowhead Forever, is retained.
3. **Red Dragonscale Leggings**, item `252603`: a **real outstanding discrepancy** of **+31 vs +32 Intellect** between client-based sources. Wowhead Forever and some sources deriving item budgets display +31; later Bind on Forever/METAMMO show +32. Do not silently change the number; a visible warning is retained pending direct game-client verification.

**Caution:** These are two independently displayed sources of client-derived data, not 38 independent in-game checks. A missing source stat must not be interpreted as zero. Do not replace reviewed effects with undecoded source templates.

## Automated protections

- `scripts/build-item-stats.py` re-applies reviewed corrections by item ID after every import.
- `scripts/validate-item-stats.py` prevents loss of Dreamscale's mana regeneration and the Red Dragonscale Intellect warning.
- `.github/workflows/import-item-stats.yml` validates all 452 records before committing generated files.
- The UI requires 452 valid item-ID matches before showing any gear tooltips.
