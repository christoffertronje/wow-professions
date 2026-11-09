# Forgebook — WoW Forever Professions

A mobile-first WoW Forever profession recipe browser. The published scope is **Leatherworking**.

## Live site

https://christoffertronje.github.io/wow-professions/

GitHub Pages deploys on pushes to `main` via `.github/workflows/deploy.yml`.

## Catalog and data rules

- 512 identified WoW Forever Leatherworking recipes, excluding 80 Season of Discovery and 13 unidentified client records.
- All 512 recipes have source-backed minimum crafting-skill values. These are the minimum requirements to **craft** items, not skill-up color thresholds. Source-backed does not mean individually confirmed in-game.
- Reagents and quantities are present for all recipes. Item-level tooltip data is indexed by crafted item ID for all 512 outputs in `data/item-stats.json`.
- Rarity counts in the current tooltip catalog: 27 common, 214 uncommon, 201 rare, 70 epic.
- The recipe source snapshot is from client build 1.60.1.70707. Some item tooltip corrections use later client evidence. WoW Forever live-server behavior may differ.
- Do not silently replace WoW Forever data with Classic Era or Season of Discovery records.

## Interface

- Compact expandable recipe cards with expand/collapse all
- Search, profession selection and recipe filters
- WoW-inspired item tooltips, including armor, stats, effects and required character level when supported by item data
- Responsive layout; no build step or external JS dependencies (open `index.html`)

## Outstanding manual verification

Five item tooltip records have explicit `statReviewWarning` entries pending independent in-game confirmation:

1. **Red Whelp Gloves**: displayed 5% proc wording versus a separate 10% proc database field.
2. **Fletcher's Gloves**: client-derived +14 Critical Strike / -15 Parry versus legacy percentage descriptions.
3. **Nightscape Boots**: +1.2 stealth in later client records versus +1 in older records.
4. **Core Armor Kit**: +3 Defense on item level 45+ is favored by multiple Forever sources versus conflicting Wowhead data.
5. **Red Dragonscale Leggings**: newer client records indicate +32 Intellect, +20 Spell Power, +20 Healing versus older +31 / combined description. The app now consistently shows the newer values.

These five are *warnings about source discrepancies*, not confirmed data errors. Keep warning metadata until checked against current live in-game tooltips.

## Data files

- `data/leatherworking.json`: recipes, reagents and minimum required craft skill
- `data/item-stats.json`: crafted output item metadata and tooltip details

## QA checklist

- Verify 512 recipe-to-item matches and rarity match by item ID.
- Verify `craftSkillRequired` values, especially where source records disagree.
- Compare rare and epic item materials and tooltip data with Forever-specific client sources.
- Confirm search/filter and expand/collapse behavior on mobile and desktop.
- Verify the five flagged tooltips against live in-game values before clearing their warnings.

Not affiliated with Blizzard Entertainment.
