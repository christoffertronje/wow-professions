# Four high-priority item stat discrepancies — reviewed 2026-11-09

Scope: 4 gear/consumable outputs with significant gameplay effects. Data was checked by produced **item ID**, not name, and existing source corrections are persisted in `data/item-stats-corrections.json` so that `scripts/build-item-stats.py` reapplies them on every rebuild. All four still carry visible uncertainty text in Forgebook because no live in-game item inspection has been performed.

| Item | ID | Forgebook reviewed value | Why / live verification still needed |
|---|---|---|---|
| Fletcher's Gloves | 7348 | **+14 Critical Strike rating** (existing raw item stat line), **−15 Parry rating** | Forever-specific newer client sources (RaidDex, SenseOS) expose rating values, not older %-based Wowhead text. Verify sign and amount on an in-game tooltip; do not render an extra duplicate +14 crit line. |
| Nightscape Boots | 8197 | **+1.2 effective Stealth level** | Newer 1.60.1.70790 ForeverChanges and Bind on Forever/Forever Mastery agree on 1.2; older build 70707 and SenseOS show 1. |
| Red Dragonscale Leggings | 252603 | **+32 Intellect** | Recent METAMMO and Bind on Forever clients show 32; older budget calculations such as ForeverDiff show 31. |
| Core Armor Kit | 18251 | **+3 Defense**, usable on target items **level 45+** | ForeverDiff, QuestCore, Forever Mastery and GuildLoot show 3/45; Wowhead Forever says 4/0. This is a **genuine outstanding source conflict**, even though the stronger cross-source evidence currently favors 3/45. Confirm by applying the kit in the live game before removing the warning. |

Source URLs:
- Fletcher's Gloves: https://raiddex.com/en/wow-forever/items/fletchers-gloves · https://senseos.gg/wiki/wow-forever/items/7348/fletchers-gloves/ · https://www.wowhead.com/forever/item=7348
- Nightscape Boots: https://foreverchanges.pro/item/8197/nightscape-boots · https://bindonforever.com/item/8197 · https://senseos.gg/wiki/wow-forever/items/8197/nightscape-boots/
- Red Dragonscale Leggings: https://metammo.com/wow-forever/items/red-dragonscale-leggings-252603 · https://bindonforever.com/item/252603 · https://foreverdiff.com/recipes/red-dragonscale-leggings-55031/
- Core Armor Kit: https://foreverdiff.com/items/core-armor-kit-18251/ · https://questcorehq.com/wowdb/forever/item/18251/core-armor-kit · https://www.wowhead.com/forever/item=18251

## Verification and caveats

This is reconciliation of independently presented **client-derived** Forever data, not independent observation from a live character. Values may differ by client build, backend hotfix, or rendering of dynamic item budget stats and spell parameters.

- **No user-uploaded game screenshots yet.** All four keep a `statReviewWarning`; the warning should be replaced only when there is direct compelling confirmation, not automatically because one page changed.
- `scripts/validate-item-stats.py` now protects the exact four reviewed effects/stat values and the warnings.
- `docs/rare-stats-second-source-audit.json`, `docs/uncommon-stats-second-source-audit.json` and `docs/epic-stats-second-source-audit.json` remain historical side-by-side comparisons of the earlier source snapshot. Newer corrections may necessarily disagree with that older comparison; such discrepancies must be consciously reviewed, not wiped.
- The next quality-control increment should distinguish **mechanically meaningful conflicts** from tooltip format differences and provide a repeatable build-to-build delta report without overwriting vetted data.
