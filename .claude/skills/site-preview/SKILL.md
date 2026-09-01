---
name: site-preview
description: Preview, screenshot, and sign off pages of the LTA-SSP site under docs/. Use when running the site locally, checking a page renders correctly, verifying responsive or accessibility behaviour, or deciding whether a page is finished. Covers the local server command, the desktop and mobile screenshot procedure via claude-in-chrome, and the checklist docs/CLAUDE.md requires before calling a page done.
---

# Previewing and finishing a page

## Local server

```
cd docs
python -m http.server 8000
```

On this machine `python3` is not a recognized alias — use `python`. Visit
<http://localhost:8000>. Run it with `run_in_background: true` so it does not block, and stop it
when finished.

Serve from `docs/`, not the repo root. The live site is a GitHub Pages *project* site under the
`/LTA-SSP/` path prefix, so serving the repo root would let a root-absolute path work locally and
break in production. Relative paths only — that is the point of the rule.

Pages worth loading: `/`, `/controls/`, `/find-your-system-type/`, and a system-type page.
The controls page is state-driven by the query string, so exercise it:

```
/controls/?type=high-risk-cloud&level=0,1
/controls/?type=sandbox                     # levels [0,2] — no Level 1 exists
/controls/?type=catalog:dss                 # pseudo-type: bypasses profiles, level filter off
/controls/?domain=AC,LM&q=logging
```

## Screenshots

Delegate to the **`site-critic`** agent unless you specifically need to see the image yourself —
screenshots are expensive in context, and that agent exists to keep them out of the main window.

Doing it directly: use `claude-in-chrome` (**not** chrome-devtools). Load the core tools in one
`ToolSearch` call, open a new tab, then capture at both widths:

- **Desktop** — 1440×900
- **Mobile** — 390×844

Use `mcp__claude-in-chrome__resize_window` between captures. Check both; a page that survives only
one width is not done.

## Before calling a page done

From `docs/CLAUDE.md` — all of these, against the screenshot, not the markup:

1. **Both widths captured** and actually looked at.
2. **Not templated** — no unstyled system fonts, no purple/violet gradient hero, no generic
   centered card unless that was a deliberate choice. One distinctive element, everything else
   quiet around it.
3. **Keyboard focus is visible** on every interactive element. Tab through the filter checkboxes
   and wizard buttons.
4. **`prefers-reduced-motion` respected.**
5. **Colour never carries meaning alone** (WCAG 1.4.1). This bites hardest on selection state —
   use a native checked/unchecked control or an icon/text change, not a colour or opacity shift.
   Domain colours are a scanning aid only: every swatch sits next to its 2-letter code.
6. **Semantic HTML** — `<title>`, meta description, viewport meta present.
7. **Self-critique out loud**: does this look intentional, or generated? Say which, and why.

## Data-driven pages drift

The 8 `docs/system-types/*/index.html` pages hardcode level counts and domain chips that also live
in `docs/assets/data/`. If `system-types.json` or `profiles.json` changed, verify those pages
against `python research/scripts/corpus.py stats` before signing off — nothing catches this drift
automatically.

## Deploy

Push to `main`. GitHub Pages serves `main` / `/docs`. No CI, no build step — what is in `docs/` is
what ships.
