# Forgebook — WoW Forever Professions

Mobile-first profession recipe browser UX prototype.

## Try it

Open `index.html` in your browser. No build step or dependencies.

Planned GitHub Pages URL: https://christoffertronje.github.io/wow-professions/

If the site is not live, enable **Settings → Pages → Build and deployment → GitHub Actions** in this repository. The workflow in `.github/workflows/deploy.yml` deploys on pushes to `main`.

## Current scope

- Leatherworking and Alchemy profession selector
- Compact recipe cards; individual expand/collapse
- Expand all / Collapse all
- Search recipe names and reagents
- Filter all / can learn / skill-ups
- Skill-up color state
- Profession and skill preference saved locally
- Responsive mobile/desktop layout

**Data warning:** All recipes, reagent quantities, skill thresholds, and learning sources in the prototype are **unverified sample data**. Do not use these for in-game planning. Before going beyond UX evaluation, replace the sample dataset with verified, versioned client-derived records.

## Next

1. Test mobile interaction and styling with a handful of sample entries.
2. Decide on card layout, filter terminology, how item icons should appear, and whether individual cards should stay open across filters.
3. Replace samples with validated recipe data.
4. Split into components or migrate to React/Vite only if useful for the growing application.

Not affiliated with Blizzard Entertainment.
