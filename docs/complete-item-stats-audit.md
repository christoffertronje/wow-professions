# Forgebook — complete item tooltip coverage (2026-11-09)

## Published output

Forgebook now has **512 / 512 item-ID-joined tooltip records** for all 512 identified WoW Forever Leatherworking recipes. These include gear, bags, armor kits, camp constructions, hides and leather. A non-equipment output may legitimately have no equip slot, armor or attributes; the application shows only recorded fields and effects.

| Verified output quality | Recipes |
|---|---:|
| Epic (purple) | 70 |
| Rare (blue) | 201 |
| Uncommon (green) | 214 |
| Common (white) | 27 |
| Unknown quality | 0 |
| **All** | **512** |

### The original 60-item remainder

All 60 outputs matched the Forever Talent spell ID, produced item ID, quality and item level. The **32 previously 'unknown' records** (Grimstitch, Grovekeeper, Spiritcaller and Wildstalker gear) show **Epic** quality in the recorded Forever tooltips; this is persisted in `data/item-quality-corrections.json` and applied by `scripts/build-data.py` so it survives refreshes.

The other 28 originally Common outputs contained 5 equippable pieces and 23 items without ordinary equipment slots. One of those 28, **Toughened Leather Armor** (`2314`), is **Uncommon** rather than Common in newer WoW Forever client 1.60.1.70862, as corroborated by ForeverChanges, SenseOS and RaidDex. Its newer Forever stats are **84 Armor, +2 Stamina, +7 Spirit, BoE**; these are preserved via `data/item-stats-corrections.json`. The final Common count is therefore **27** and Uncommon **214**.

### Armor kits are not equippable armor

A kit's bonus armor/Stamina applies to the target armor item. It should **not** be shown as stats worn by the kit itself. The importer stores these enhancements only as **Use effects**, leaving the kit's own `armor`, `stats`, and `slot` absent. The older tooltip source for Heavy, Thick and Rugged Armor Kits contained unresolved effect zeros. Their reviewed 1.60.1.70862 bonuses have been corrected to:

- Heavy: **+3 Stamina, +24 Armor**, target item level **15+**
- Thick: **+4 Stamina, +32 Armor**, target item level **25+**
- Rugged: **+5 Stamina, +40 Armor**, target item level **35+**

Original source: Forever Talent recorded 2026-10-17, supplemented by [ForeverChanges Heavy Armor Kit](https://foreverchanges.pro/item/4265/heavy-armor-kit) and the corresponding Thick/Rugged item pages. Some lower-priority source text differences remain around camping-item details and armor-kit spell placeholders; `docs/common-item-second-source-audit.json` records them.

### Validation

- `scripts/build-item-stats.py` imports all 512 tooltips using produced item IDs and skill-spell IDs and reapplies reviewed corrections.
- `scripts/validate-item-stats.py` validates quality, completeness, provenance, and previously reviewed effect/attribute corrections.
- `scripts/validate-crafting-skills.py` validates quality updates and protects verified crafting requirements/materials.
- `index.html` displays WoW-styled tooltips for all 512, using white/green/blue/purple item names. A missing or partially mismatched 512-entry file is rejected.
- Non-equippable outputs correctly omit slots and equip stats.

**Evidence boundaries:** Imported tooltips come from client-derived sites, not direct testing of every item in a live WoW Forever session. Recent-client corrections are source-backed, not claims of all-live verification. Some item effects may still vary by game version. Unknown or conflicting values must not be guessed or silently overwritten.
