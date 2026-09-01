---
id: F-009
title: All 8 system-type pages linked their main call-to-action to a 404
date: 2026-09-01
rq: [RQ-2]
implications: [site]
confidence: high
status: actioned
---

## Observation

Every page under `docs/system-types/<type>/` linked its primary call-to-action — "See its
controls" — as `href="../controls/?type=<id>"`. From a page at
`/LTA-SSP/system-types/low-risk-cloud/`, one level up is `/LTA-SSP/system-types/`, so the link
resolved to:

```
https://ziqiangg.github.io/LTA-SSP/system-types/controls/?type=low-risk-cloud   → 404
```

All 8 types were affected. The correct depth is two levels: `../../controls/?type=<id>`.

Reported and fixed by the project owner. Verified after the fix: all 8 pages now use `../../`, and
no single-level `../assets` or `../controls` reference remains under `docs/system-types/`.

## Evidence

- Reported with the 8 failing URLs, 2026-09-01
- `grep -o 'href="[^"]*controls/?type=[^"]*"' docs/system-types/*/index.html` — all 8 now `../../`
- `grep -c 'href="\.\./\(assets\|controls\)'` — 0 across all 8 pages

## Interpretation

This is the exact failure mode `docs/CLAUDE.md` warns about, and it demonstrates why that rule is
load-bearing rather than stylistic:

> this is a GitHub Pages *project* site, not a `<user>.github.io` root site — every internal link
> and asset reference must stay relative

The subtlety is that relative paths are necessary but not sufficient — they must also be at the
*right depth*. The system-type pages sit one level deeper than `/controls/` and `/find-your-system-
type/`, and the CTA was written as if they were siblings.

**It was invisible locally in the most likely dev setup.** Serving from `docs/` on
`localhost:8000` reproduces the depth correctly, so this specific bug *would* have been caught by
following the `site-preview` procedure — but only by actually clicking through to the controls
page, not by loading the system-type page and looking at it. A screenshot of a page whose links are
broken looks identical to one whose links work.

That is the transferable lesson: the site checklist tests *rendering*, and this class of defect is
invisible to rendering.

## Implications

- **site:** The pre-rendered system-type pages are the most link-fragile part of the site — they
  are the only pages two levels deep, and `site-preview` already flags them as the most drift-prone
  (their level counts are hardcoded). They deserve explicit attention in any site pass.
- **site (process):** Add a link check to the `site-preview` checklist — every internal `href`
  resolving to a real file, at the served depth. This is cheap to automate over static HTML and
  catches a class the visual checklist structurally cannot.
- The main CTA of 8 of the site's 13 pages pointed at a 404, and no existing check would have
  reported it. Worth weighing when deciding how much of the site work to keep manual.

## Verified after the fix

A link check over the whole site — every `href`/`src` resolved relative to its own file, with
root-absolute paths flagged separately — reports **64 internal references, 0 broken, 0
root-absolute**. The fix is complete and no other cross-depth link is wrong.

The check itself is ~15 lines of stdlib Python over `docs/**/index.html`, which settles the
"cheap to automate" claim above: it is.

## Open questions

- None outstanding. Fold the link check into the `site-preview` skill so this class cannot recur
  silently.
