# Leatherworking minimum crafting skill audit

Status: **incomplete — 449 / 605 source-backed, 156 unresolved** (2026-11-08).

This project displays the **minimum Leatherworking skill to craft a recipe**. Yellow/green/grey skill-up thresholds must never be used in the `SKILL TO CRAFT` field.

## Current coverage

- Total client recipes retained: **605**
- Recipes with a source-backed minimum: **449**
- Unknown: **156**, comprising **99** regular named recipes, **44** Season of Discovery entries, and **13** unidentifiable client records.
- `Toughened Leather Gloves` (spell 3770): **110**, not yellow threshold 135.
- `Barbaric Harness` (spell 6661): **190**, not yellow threshold 185.
- `Heavy Armor Kit` (spell 3780): **150**, not 125.
- `Thick Armor Kit` (spell 10487): **200**, not 175.

## Data and validation

- `data/verified-crafting-skills.json` is the authoritative *display* lookup.
- `scripts/build-verified-crafting-skills.py` builds it from explicit required-skill references and vetted corrections. It stops on known regressions and excludes disputed Guardian Cloak (spell 7153).
- `data/verified-skill-corrections.json` contains direct Wowhead Forever spell checks and other reviewed corrections.
- `data/wiki-pattern-crafting-skills.json` has 37 additional vendor/drop patterns where separately recorded pattern-learning skill agrees with Warcraft Wiki's skill entry. These are source-backed rather than confirmed by in-game crafting.
- The Warcraft Wiki table has known exceptions where its `Skill` cell appears to reflect skill-up thresholds (e.g. starter items). It is **not** a safe bulk crafting-skill source.
- `docs/foreverlfg-crafting-crosscheck.json` shows discrepancies with direct Wowhead Forever checks, e.g. Barbaric Harness; matching two secondary sites alone is not sufficient to establish a requirement.

## Remaining work

Verify the 99 ordinary named unresolved recipes using the individual **Forever** spell's `Requires Leatherworking (N)` line or an equally explicit minimum crafting requirement. Then assess 44 retained Season of Discovery records and 13 unnamed client entries separately. Never assign a guessed value or relabel a yellow threshold as a crafting minimum.

Important: Source-backed does not mean independently tested inside the live game. Every known value links to its reference from the expanded recipe UI.
