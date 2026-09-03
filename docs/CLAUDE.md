# docs/ — the published site

Everything under `docs/` is the GitHub Pages *project* site at `ziqiangg.github.io/LTA-SSP/`.
Plain HTML/CSS/vanilla JS. **No build step, no framework, no package manager, no dependencies —
this rule binds `docs/` absolutely.** (Python is allowed in `research/`; it never crosses in here.)

## Structure
- Pages source: `docs/` folder on `main` branch, published under the `/LTA-SSP/` path prefix
  (this is a GitHub Pages *project* site, not a `<user>.github.io` root site — every internal
  link and asset reference must stay relative; never use root-absolute paths like `/assets/...`).
- One folder per page, each with its own `index.html` (→ clean URLs like `/controls/`).
- Shared assets in `docs/assets/{css,data,img,js}/`.
- Root `docs/index.html` = the tool's landing page — this repo IS the SSP tool, there's no
  separate portfolio section.
- `docs/assets/data/*.json` (controls, domains, profiles, system-types, level-definitions) is
  fetched at runtime by `docs/assets/js/controls.js`. `docs/assets/js/wizard.js` fetches
  `system-types.json` (display names and `classificationText` for its own option labels, ADR-005)
  and `level-definitions.json` (the standard's `selectionGuidance` sentence, shown on every
  computed result, F-003) — never `controls.json`/`domains.json`/`profiles.json`; composition
  stays `controls.js`'s job.

## Rules
- Do not introduce a build step, bundler, or framework unless explicitly asked.
- Do not commit secrets, API keys, or analytics tokens directly in HTML/JS — this repo is fully public.
- Keep HTML semantic; every page needs a `<title>`, meta description, and viewport meta tag.
- Reuse `docs/assets/css/style.css` across pages — don't create per-page stylesheets.
- `docs/assets/data/*.json` must reproduce the official source faithfully, and changes **only**
  through the ingest pipeline (`research/scripts/{scrape,diff_corpus,promote}.py` — see
  `research/CLAUDE.md`). Never hand-edit it to make a page look better; that is how the corpus
  drifted into paraphrase before (F-008). If the rendering is the problem, fix the rendering.
- Corollary: presentation belongs in `controls.js`, not in the data. Upstream renders parameter
  placeholders as `[ insert: param, ac-3_prm_3 ]` and the data keeps that verbatim — if it should
  look nicer, render it nicer.

## Design discipline (before calling any page "done")
- Screenshot the page (`claude-in-chrome` MCP, or the `site-critic` agent) at desktop and mobile
  widths before saying a page is finished. Don't rely on markup alone.
- Avoid default AI-generated look: no unstyled system fonts, no purple/violet gradient hero, no
  generic centered-card layout unless deliberately chosen.
- Pick one distinctive element (typography, accent color, one signature layout choice) and keep
  everything else quiet around it.
- Responsive down to mobile width, visible keyboard focus states, respect `prefers-reduced-motion`.
- Self-critique against the screenshot before presenting: does this look templated, or intentional?
- Never let color alone carry a meaning (WCAG 1.4.1) — selection state especially: use a native
  checked/unchecked control (checkbox) or an icon/text change, not just a color/opacity shift on
  a button.

## Domain color palette
The 26 SSP control domains (17 cybersecurity + 9 Digital Service Standards) each get a
`--domain-<CODE>` custom property in `docs/assets/css/style.css` (light values in `:root`, dark
values in the `prefers-color-scheme: dark` block, same pattern as `--pico-primary`).
- Colors are the **dataviz skill's validated 8-hue categorical theme** (blue, orange, aqua,
  yellow, magenta, green, violet, red — see the skill's `references/palette.md`), round-robin
  assigned across the 26 domains in `docs/assets/data/domains.json` order. Validated against this
  site's actual light (`#ffffff`) and dark (`#13171f`) backgrounds — all hard gates pass; 3
  light-mode hues (aqua/yellow/magenta) sit below 3:1 contrast by design, which is why the
  mitigation below is load-bearing, not optional.
- **8 hues cannot give 26 pairwise-distinct colors** — no ordering of a full 8-hue set clears the
  all-pairs CVD floor, so a 26-color set can't either. Color here is a **supplementary scanning
  aid, never a unique identifier** — every colored swatch/badge always sits directly next to its
  2-letter code, and everywhere but the space-constrained control-card badge, next to the full
  domain name too. Don't extend this to "give every domain a truly unique color" — it isn't
  achievable accessibly; add domains to the existing round-robin instead.
- To change the palette: substitute the dataviz skill's `references/palette.md` categorical values
  (or your own, validated against contrast) and regenerate the round-robin assignment — don't
  hand-pick replacement hex values.

## Known drift risk
The 8 `docs/system-types/*/index.html` pages hardcode level counts, domain chips, and each type's
`classificationText` (copied verbatim into static markup) — all also derivable from
`docs/assets/data/`. If the JSON changes, these pages go stale silently. Check them whenever
`system-types.json` or `profiles.json` moves. Converting them to fetch-based rendering (matching
`controls.js`'s and `wizard.js`'s pattern) would close this permanently but hasn't been done.
