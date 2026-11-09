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

## Independent 201-item field audit — 2026-11-09

The script `scripts/audit-rare-second-source.py` fetches all **201 produced rare item IDs** from [Bind on Forever](https://bindonforever.com/items), whose records use WoW Forever client build `1.60.1.70862`. It compares the structured item level, required character level, binding, slot/type, armor, primary attributes, resistances and text effects against the earlier `data/item-stats.json` imported from Forever Talent.

Result: **199 complete matches**, **zero unresolved numerical disagreements in comparable fields**, and **two inconclusive Armor Kit effect tooltips** because Bind on Forever exposes raw parameter placeholders (`0c1`, `0c2`, `0cim`). The comparison deliberately treats these undecoded placeholders as *unknown* rather than equal to (or corrections of) our actual values. All 201 item IDs were found; no names remain unmatched.

### Reviewed and fixed

- **Swift Flight Bracers**, item `18508`: added missing `Equip: +41 Ranged Attack Power.`, independently corroborated by ForeverDB and Wowhead Forever. This correction is persistent in `data/item-stats-corrections.json`.
- **Wild Leather Armor Kit**, item `279258`: corrected `+0 Stamina` to **`+10 Stamina`**, and `items level 0+` to **`items level 45+`**, corroborated by Wowhead Forever, Forever Mastery and ForeverDB. Its new-client template remains undecoded in Bind on Forever; therefore it is source-resolved but not counted among the 199 exact comparative matches.
- **Dragonscale Breastplate**, item `8367`: the newer source's `+13 to All Resistances` is equivalent to the five explicit resistances (`Arcane, Fire, Frost, Nature, Shadow`) in our tooltip. No change necessary.
- **Skulker's Leather Shoulders**, item `252535`: the newer source uses singular “Shoulder”. Exact item ID and stat values agree; accepted as a spelling alias.
- **Core Armor Kit**, item `18251`: still **disputed**. Wowhead Forever's item description gives **+4 Defense and item level 0+**; Forever Mastery and ForeverDB give **+3 Defense and item level 45+**; Bind on Forever displays unresolved spell-template parameters. The app retains the sourced original value with a visible warning. **Only an in-game verification can definitively settle this.**

### Guardrails

- `scripts/validate-item-stats.py` now checks all 201 item/recipe relationships, the verified Swift Flight Bracers and Wild Leather Armor Kit bonuses, and the unresolved Core Armor Kit warning.
- `scripts/build-item-stats.py` reapplies `data/item-stats-corrections.json` after every import, so old data cannot silently restore the wrong effect text.
- `docs/rare-stats-second-source-audit.json` records the per-item field comparison and evidence links. Re-run the audit after a newer client build or an in-game correction.
- No source is a substitute for item stats checked directly inside live WoW Forever.
