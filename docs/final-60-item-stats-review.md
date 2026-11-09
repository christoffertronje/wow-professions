# Final 60 Leatherworking outputs — classification and tooltip review

Reviewed on 2026-11-09. The previously uncompleted scope was **28 Common and 32 Unknown-quality outputs**. The current recipe data contains **27 Common, 214 Uncommon, 201 Rare and 70 Epic**, with **zero Unknown**. The change versus the earlier snapshot is explained by **32 formerly Unknown outputs** now identified as Epic gear, plus **Toughened Leather Armor** (item 2314) reclassified from Common to Uncommon based on newer Forever client data.

## Quality provenance

- The 32 formerly Unknown outputs belong to the **Grimstitch, Grovekeeper, Spiritcaller and Wildstalker's** crafted gear groups. Their Epic quality was matched to the produced item ID and crafting spell ID in recorded Forever item tooltips. Exact corrections are kept in `data/item-quality-corrections.json`.
- **Toughened Leather Armor**, item **2314**, is Uncommon according to newer client sources, despite an older recorded tooltip saying Common. The override is explicit and has source references.
- No unknown-quality entries remain. No newly identified Epic gear is automatically asserted to be obtainable in live WoW Forever.

## Non-gear outputs

The 27 Common items include only **four Common armor pieces** (Handstitched Leather Boots, Handstitched Leather Bracers, Handstitched Leather Cloak, Winter Boots). The other **23 Common products** are not normal equippable armor:

- 10 reagent products: leather and cured hides
- 5 armor kits, whose Use effects alter *another item*, not the kit's own armor
- 2 bags, 1 quiver and 1 ammo pouch
- 3 camping devices (Camp Tent, Tanning Rack, Sewing Machine)
- 1 miscellaneous toy (Heavy Leather Ball)

**Important:** A bag may carry the `Bag` slot and a quiver may have a ranged-speed Equip effect; neither is represented as wearable leather armor with fictitious armor or primary attributes. Armor kits store their application as a `Use` effect, not as an intrinsic armor stat. All 27 items have recorded item levels; some have neither slot nor armor and this is expected.

## Verified coverage and publication guard

`data/item-stats.json` currently contains **512/512** produced item records. The full catalog joins on both produced item ID and recipe spell ID. `scripts/validate-item-stats.py` requires the expected 27/214/201/70 quality distribution, checks all 27 Common output identities and item levels, and preserves previously reviewed source corrections. The UI only enables stats when all 512 records match the recipe catalog and their quality. White/green/blue/purple tooltips use the source's actual fields without inventing missing stats.

The entries are sourced from recorded Forever client files, not independently verified in every live item tooltip. Existing disputes (e.g. Core Armor Kit, Fletcher's Gloves, Nightscape Boots, Red Dragonscale Leggings) remain visibly flagged until in-game verification.

### Follow-up

Rerun source comparisons after a newer game build, especially for item effects or quality reclassifications. Confirm unresolved effects using live screenshots before replacing recorded values.
