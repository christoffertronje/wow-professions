# Item stats in Forgebook

## Implemented: Rare-quality Leatherworking outputs

The first release adds a separate `data/item-stats.json` database for **201 Rare-quality produced items**. Every entry is keyed by the **produced item ID**, not by name. Each also stores its crafting spell ID, which is validated against `data/leatherworking.json`.

The importer `scripts/build-item-stats.py` extracts the recorded WoW Forever tooltip from [Forever Talent](https://wowforevertalent.com/professions/leatherworking/), checking the source's explicit `data-output-facts` item ID. It preserves full tooltip lines and special effects. The output contains item level, required character level, slot, armor type, armor, binding, primary attributes, resistances, effect text and any remaining tooltip lines where available.

No values are guessed. `null` or omitted fields mean the corresponding fact was not stated by the source. For instance, Core Armor Kit and Wild Leather Armor Kit have no equipment slot, while Onyxia Scale Cloak has a single `Back` slot.

## Coverage and guardrails

- Main recipe catalog: 512 identifiable WoW Forever Leatherworking recipes
- Rare outputs: 201 / 201 have source-based item stats, item ID matched
- 195 Rare items have basic attributes; 34 have resistance stats; 111 have special effects
- `scripts/validate-item-stats.py` enforces complete coverage, valid item/recipe IDs, source provenance and a known Brawler's Leather Belt regression example
- GitHub Pages validates the 201-item file before rendering gear stats; a missing or incomplete file does not display partial results
- GitHub Actions validates both the crafting catalog and the stats file before deployment

**Important evidence boundary:** The data comes from a recorded Forever client tooltip snapshot (source checked 2026-10-17). This is NOT an assertion that every stat was checked in live WoW Forever. Blizzard may hotfix server-side values. Source links are kept for inspection; live-game screenshots/tooltips take precedence if they disagree.

## Next iteration

Compare sampled or full 201-item stat records against a second independent Forever-specific item database that identifies whether each entry uses Forever-client values or Classic fallback. Avoid treating fallback values as verification. After resolving material differences, extend item stats to the remaining crafted armor/items in the 512-recipe catalog; recipes that make reagents or armor kits may not have equipment-style stats.

## Presentation

The expandable recipe row now renders an Item stats section before the existing materials, with character level distinct from Leatherworking skill. Equipment attributes, resistances and special effects are preserved without replacing the source tooltip. The recipe requirements and reagent amounts remain unchanged.
