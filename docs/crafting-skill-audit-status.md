# Leatherworking minimum crafting-skill audit

**Status (2026-11-08): Main named Forever catalog covered; historical client records still unverified.**

This app shows the **minimum Leatherworking skill needed to craft the recipe**, never the yellow/green/grey skill-up cutoffs. A number is *source-backed*, not necessarily individually tested inside the live game. We preserve its exact reference and mark unknown values with `?`.

## Coverage

| Scope | Source-backed minimum | Unresolved | Total |
|---|---:|---:|---:|
| Named non-Season-of-Discovery Leatherworking | 512 | 0 | 512 |
| Archived Season of Discovery client records | 36 | 44 | 80 |
| Unidentified client records | 0 | 13 | 13 |
| **All retained client recipes** | **548** | **57** | **605** |

We have **not** verified that every archived Season of Discovery recipe is currently obtainable or craftable in WoW Forever. The 13 unidentified records do not expose enough information to assign a trustworthy minimum. All 605 are retained in the dataset.

## Evidence and data provenance

1. `data/verified-crafting-skills.json`: the only source used for the displayed minimum.
2. `data/verified-skill-corrections.json`: specific reviewed values, particularly when a source's yellow threshold was initially mistaken for the crafting requirement.
3. `data/wclbox-wiki-crafting-skills.json`: 48 minimums where the first skill in WCLBox agreed with Warcraft Wiki.
4. `data/pattern-wclbox-crafting-skills.json`: 23 explicitly recorded pattern-learning requirements corroborated by WCLBox.
5. `data/ninja-wclbox-crafting-skills.json`: 10 per-spell Forever Ninja learning minima, of which one has an in-game observation marker; nine match WCLBox.
6. The additional 37 vendor/drop pattern crosschecks, GuildLoot's stated skill column, and Questing's explicit `Requires Leatherworking` entries are retained in earlier source files.
7. `docs/wclbox-crafting-comparison.json` and `docs/wiki-craft-skill-crosscheck.json` retain **conflicting** measurements; conflicting values were not blindly merged.
8. `docs/remaining-crafting-skills.json` lists all 57 unresolved client entries by spell ID and reason.

Examples of reviewed minima:

| Spell | Recipe | Minimum craft skill | Evidence |
|---|---|---:|---|
| 3770 | Toughened Leather Gloves | 110 | Forever pattern source; yellow is 135 |
| 6661 | Barbaric Harness | 190 | Wowhead Forever spell requirement; other sources disagree |
| 3780 | Heavy Armor Kit | 150 | Wowhead Forever spell requirement |
| 10487 | Thick Armor Kit | 200 | Wowhead Forever spell requirement |
| 19047 | Cured Rugged Hide | 250 | Wowhead Forever spell requirement |
| 24703 | Dreamscale Breastplate | 300 | Wowhead Forever pattern item |
| 10548 | Nightscape Pants | 210 | Forever leveling guide and client comparison |
| 28474 | Bramblewood Belt | 300 | Forever item index + corresponding Classic spell; not in-game tested |
| 28224 | Icy Scale Bracers | 300 | Forever item index + corresponding Classic spell; not in-game tested |

## What is still not proven

- **44 Season of Discovery client records** lack an accepted minimum *in Forever*, and client presence does not establish that they exist as live crafts.
- **13 nameless client records** have no resolved output/recipe name; we cannot establish their craft requirements.
- Source-backed minimums and pattern-item requirements are not automatically the same as direct in-game verification. Further in-game trainer/recipe observations may reveal corrections.

The app must not silently replace missing values with skill-up thresholds. All 605 entries remain searchable; unknown minima show `?`.

## Rebuild and regression protection

`scripts/build-verified-crafting-skills.py` builds the accepted minimums and fails for previously detected mixing errors (Toughened Leather Gloves, Barbaric Harness, etc.). `scripts/build-data.py` copies only the resulting `craftSkillRequired` field to the UI dataset. Any future source disagreements require human review.
