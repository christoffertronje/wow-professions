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
- Search and recipe filters: all recipes or can craft now, using the actual minimum craft skill
- Leatherworking only in the profession selector until other professions have verified data
- WoW-inspired item tooltips, including armor, stats, effects and required character level when supported by item data
- Responsive layout; no build step or external JS dependencies (open `index.html`)


## Gear Upgrade Planner and optional Armory sync

Open [Gear Upgrade Planner](https://christoffertronje.github.io/wow-professions/upgrades.html) from the Forgebook header.

- Choose a gear slot (for example Hands) and compare Leatherworking outputs whose **required character level** is within ±3 of your level.
- All eligible options are shown. Results are sorted using a conservative comparison of known armor and five main attributes; this is not a class/spec simulator, and unknown effects are never assumed to be zero.
- Enter level, crafting skill and your equipped stats manually, or use the optional public character snapshot import.
- The initial automated character is **Majblomma Tronjesson (EU, PvP)**. Entering a different Armory link does *not* automatically import that character.
- The gear planner saves manual inputs in your browser's localStorage.

### Enable automatic import (requires repo administrator)

1. Create a Battle.net developer application at https://develop.battle.net/ and obtain a client ID and client secret for the WoW Profile API.
2. In GitHub repo settings, open **Secrets and variables → Actions** and add repository secrets named `BNET_CLIENT_ID` and `BNET_CLIENT_SECRET`. Never paste those values into repository files, browser JavaScript, or chat.
3. In GitHub **Actions → Deploy GitHub Pages**, choose **Run workflow**. It runs the offline parser tests, requests an app-access token using client credentials, then fetches Forever character profile, equipment, and (when available) professions using the `profile-forever-eu` namespace.
4. Once the deployment succeeds, the public generated `data/armory-majblomma.json` is included in the Pages artifact. Open Gear Upgrade Planner and click **Import Majblomma from Armory** to apply the published snapshot to the comparison.
5. The deployment workflow also runs every six hours (`17 */6 * * *`, UTC). Source changes continue to deploy normally even before credentials are configured.

**Privacy:** The generated snapshot is public (character name, level, class, equipment, selected stats and crafting skill). Tokens and API secrets are never written to the snapshot. The import is not instant and can lag the game until logout plus the next scheduled refresh. If the Blizzard API fails, the sync step fails rather than publishing invented or empty character information; manual comparison continues to work.

The profile API is currently evolving and may require parser adjustments for newer Forever client responses. These changes have not been live-tested with a Battle.net application token.

## Outstanding manual verification

Four item tooltip records have explicit `statReviewWarning` entries pending independent in-game confirmation:

1. **Fletcher's Gloves**: client-derived +14 Critical Strike / -15 Parry versus legacy percentage descriptions.
2. **Nightscape Boots**: +1.2 stealth in later client records versus +1 in older records.
3. **Core Armor Kit**: +3 Defense on item level 45+ is favored by multiple Forever sources versus conflicting Wowhead data.
4. **Red Dragonscale Leggings**: newer client records indicate +32 Intellect, +20 Spell Power, +20 Healing versus older +31 / combined description. The app now consistently shows the newer values.

These four are *warnings about source discrepancies*, not confirmed data errors. Keep warning metadata until checked against current live in-game tooltips.

Red Whelp Gloves was resolved using a ForeverChanges entry explicitly marked confirmed in-game: 5% proc chance for 30–50 Fire damage.

## Data files

- `data/leatherworking.json`: recipes, reagents and minimum required craft skill
- `data/item-stats.json`: crafted output item metadata and tooltip details

## QA checklist

- Verify 512 recipe-to-item matches and rarity match by item ID.
- Verify `craftSkillRequired` values, especially where source records disagree.
- Compare rare and epic item materials and tooltip data with Forever-specific client sources.
- Confirm search/filter and expand/collapse behavior on mobile and desktop.
- Verify the four flagged tooltips against live in-game values before clearing their warnings.

Not affiliated with Blizzard Entertainment.
