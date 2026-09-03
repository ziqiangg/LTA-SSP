---
id: F-014
title: scrape.py's missing end-of-page landmark let site footer/nav chrome leak into the last control on each domain page
date: 2026-09-03
rq: [RQ-5]
implications: [data, site]
confidence: high
status: actioned
---

## Observation

20 of 248 controls (8.1%) — always `sorted(domain_controls)[-1]`, i.e. the last control on that
domain's catalog page — had the site's own footer and category-nav chrome appended to their
`risk` (cybersecurity) or `rationale` (dss) field, **rendered twice** (the footer renders once for
a mobile layout and once for desktop in the same DOM). Example, `AC-16`'s `risk` field before this
fix:

> "...potentially compromising the integrity and security of critical operations. Back to
> Cybersecurity Other pages in Cybersecurity Application Security Backup and Recovery Container
> Security... See all pages Back to top Singapore Government ICT&SS Policy Reform... Made with
> Isomer Built by Open Government Products" *(repeated twice)*

The **same 20 controls'** `citations` arrays were **100% fabricated nav junk** — sibling-domain
links, `"See all pages" → /control-catalog/{catalog}/`, `"Back to top" → "#"` (a dead in-page
anchor), and the entire global footer link set (About, SSP, Control Catalog, Highlights, Contact,
Feedback, Report Vulnerability, Privacy Statement, Terms of Use, REACH) — zero genuine references
among them, out of 36 controls that carried any `citations` at all.

Affected: `AC-16, AS-15, BD-9, CK-4, CS-11, DC-2, DP-8, GA-8, HR-3, IS-14, NS-11, PM-10, SC-9,
SD-10, TL-6, TX-15, WO-18, WP-19, WR-2, WU-14` (20 of 26 domains). Clean: `BR, LM, PR, RS, ST, UU`
— their last control happens to have a `Parameters` section trailing its Risk/Rationale block,
which incidentally reset the parser's `field` state before the footer was ever reached.

## Evidence

- `python research/scripts/corpus.py gaps` (new "scrape contamination (F-014)" section, run
  against shipped `controls.json` pre-fix): 20/20 hits, exact id match to the list above.
- Direct trace of `scrape.blocks_of()` against both catalogs' cached pages
  (`https://info.standards.tech.gov.sg/control-catalog/cybersecurity/ac/` and
  `.../dss/bd/`): the literal block sequence after the true last control's Risk
  Statement/Rationale is `"Back to"` (its own block, no trailing space or catalog name —
  confirmed identical structure on both catalogs) → `"<Catalog>"` (a separate block, carrying the
  `/control-catalog/{catalog}/` link) → `"Other pages in <Catalog>"` → sibling-domain links →
  `"See all pages"` → `"Back to top"` (`href="#"`) → the Isomer footer, twice.
- `research/scripts/scrape.py`, `scrape_domain()` (~lines 210–263 pre-fix): the block-accumulation
  loop had START landmarks (`FIELD_LANDMARKS`) but no END landmark for the last field of the last
  control on a page — it only stopped on a new same-domain control heading, `Group:`, or
  `Parameters`, none of which exist after the true last control.
- `research/scripts/promote.py`, `build_citations()` (~line 133 pre-fix): unconditionally
  preferred any non-empty scraped `links` list with no relevance check, shipping the chrome
  straight through as `citations`.
- `research/corpus/scrape-diff-2026-09-01-before-promotion.md` and
  `scrape-verify-2026-09-01-after.md`: neither mentions any chrome/footer text or inspects
  `links`/`citations` *contents* — only counts presence. Confirms this was never previously
  flagged.
- Pre-promotion live-DOM cross-check (`corpus-ingest`'s mandatory step): the `corpus-verifier`
  agent itself hit a session rate limit before running: direct `WebFetch` against
  `https://info.standards.tech.gov.sg/control-catalog/cybersecurity/ac/` (`AC-16`) and
  `.../dss/bd/` (`BD-9`) confirmed the corrected `risk`/`rationale` text matches the live page
  exactly, stopping at the same sentence the fix produces, with "Back to Cybersecurity"/"Back to
  Digital Service Standards" immediately following on the live page. `.../cybersecurity/lm/`
  confirmed `LM-21` (one of the 6 already-clean domains) has a `Parameters` section trailing its
  Risk Statement, explaining why it escaped the bug without the fix.
- Cross-checked against `research/findings/F-001-guidance-gaps-cluster-by-domain.md` and
  `F-008-shipped-corpus-is-paraphrased-not-scraped.md`: zero id overlap with either. F-001 was
  content *loss* (domain-wide empty guidance); F-008 was LLM *paraphrasing*. This is DOM chrome
  leaking past a parser boundary — a distinct, previously-undocumented defect class.
- repo @ `c4282da`

## Interpretation

**This is a state-machine gap, not a redeploy regression.** The `corpus-verifier` agent's own
description warns that "the parser keys on text landmarks... it will break on a redeploy,
silently" — this defect is different in kind: the landmarks never moved, there simply was never
one to mark the *end* of the last field on a page. It has been present since this parser was
written, independent of and un-caught by the 2026-09-01 rebuild that fixed F-008.

**Why the existing pipeline never caught it.** `diff_corpus.py` compares the Python parse against
the *already-promoted-from-that-same-parse* shipped file — once contaminated data has passed
through once, both sides agree and it reports "zero differences." A diff can only prove
"parse-matches-shipped," never "parse-matches-reality." `corpus-verifier` only checks whatever
sample a caller picks, and nobody happened to pick the domain's *last* control — F-001's own
2026-09-01 spot-check sampled `IS-1/2/3` and `PM-1/2/3`, missing `IS-14`/`PM-10` (the actually
contaminated controls in those exact domains) entirely.

**No genuine citation appears to have been lost.** None of the 20 controls show any evidence of
ever carrying a real upstream reference — the fabricated nav junk fully replaced an empty
`citations` field, not a populated one.

## Implications

- **data (actioned):** `scrape.py`'s `scrape_domain()` now stops the block loop at the literal
  `"Back to"` chrome block (confirmed as its own DOM block, no trailing space or catalog name, on
  both catalogs — plus `"Other pages in "`, `"See all pages"`, `"Back to top"` as fallback
  markers), rather than running to end-of-document. `docs/assets/data/controls.json` re-promoted
  from the corrected scrape.
- **A second, distinct bug surfaced while fixing the first.** `promote.py`'s `build_citations()`
  falls back to the *existing shipped* `citations` whenever the fresh scrape has no links for a
  control (by design — 5 controls, `AS-11/AS-14/CK-2/CK-3/PM-1`, cite real standards named in
  prose but never hyperlinked, and that fallback exists to preserve them). Once the scrape.py fix
  correctly emptied `links` for the 20 chrome-contaminated controls, this fallback silently
  preserved their *already-contaminated shipped* citations instead of clearing them — a first
  promotion attempt shipped 0 text contamination but all 20 controls' fake citations unchanged.
  The shipped `citations` schema carries no `url` field (only `standard` + optional `reference`),
  so the fix has to filter by name: `build_citations()` now takes a `chrome_names` set (the fixed
  Isomer footer/nav strings plus every domain and catalog display name, loaded from
  `domains.json` at call time) and drops any shipped citation whose `standard` matches one,
  returning `None` rather than stale chrome when nothing legitimate survives the filter. A new
  `"citations removed (was chrome, F-014)"` counter in `build_controls()` makes this outcome
  visible in `--dry-run`/`--apply` output — previously there was no counter bucket for "cleared to
  nothing," only "added" and "corrected," so the fallback bug's effect was invisible in the
  promotion report itself.
- **data (defense-in-depth):** `promote.py`'s `build_citations()` also rejects any freshly-scraped
  link with a `"#"` or empty `url`, independent of both fixes above.
- **data (standing safeguard):** `python research/scripts/corpus.py gaps` gained a "scrape
  contamination" section — chrome substrings in text fields, degenerate citation URLs, identical
  citation sets duplicated across unrelated controls. Run before every future promotion, not just
  once after this incident, per the updated `corpus-ingest` skill.
- **site:** No code change needed — `docs/assets/js/controls.js` renders whatever
  `risk`/`rationale`/`citations` the data carries. The fix is entirely in the data and the
  pipeline producing it; the 20 controls display correctly once re-promoted.
- **classifier:** None of these 20 controls' guidance text is usable as training signal in its
  pre-fix form (contaminated), a caveat for anyone querying `research/corpus/scraped/` snapshots
  from before this fix rather than the current shipped corpus.

## Open questions

- Should `corpus-verifier`'s standing brief be updated to *always* include the last control on
  each domain/catalog page as part of any controls-related sample, rather than relying on a
  caller to think of it? Done as a recommendation in the `corpus-ingest` skill; not yet tested
  against a *future* scrape where this specific defect class has already been fixed once — the
  real test is whether a *different* boundary bug would now be caught.
- Are there other un-landmarked page positions (e.g. the very *first* control on a page, if a
  page's leading breadcrumb/hero text before any control heading happens to look like a
  landmark) that share this same "no closing marker" structural risk? Not investigated here —
  this finding only confirms and fixes the last-control case, which is the one observed live.
- The `corpus-verifier` agent itself never completed a run (session rate limit) — verification
  relied on direct `WebFetch` calls covering 2 of the 20 fixed controls plus 1 negative control,
  not the agent's usual fuller Chrome-based cross-check. Worth a follow-up `corpus-verifier` pass
  once available, covering more of the 20 and confirming the `citations`-fallback fix
  specifically (which the `WebFetch` checks above didn't target — they checked text-field
  boundaries, not the citations schema fix that came second).
