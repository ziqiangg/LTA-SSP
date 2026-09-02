---
name: corpus-ingest
description: Fetch, diff, verify, and promote a fresh scrape of the upstream SSP standard into docs/assets/data/*.json. Use whenever the shipped corpus might be stale, upstream may have changed, or you're about to run scrape.py/diff_*.py/promote.py. Defines the single sanctioned procedure — the promotion rule is stated once here, not duplicated across CLAUDE.md files and script docstrings.
---

# Ingesting a fresh scrape into the shipped corpus

## Rule zero

**`docs/assets/data/*.json` changes only through this pipeline.** Never hand-edit it, never
reword it to make a page or an analysis come out better. This is the same rule stated in
`research/CLAUDE.md` and `docs/CLAUDE.md` — read it there for *why* (F-008: most `guidance` text
had been silently paraphrased before the 2026-09-01 rebuild). This skill is the *how*.

## The five steps, per target

Four targets share one pipeline shape. Run them independently — a scrape of one does not
require re-promoting the others.

| Step | controls | domains | system-types | level-definitions |
|---|---|---|---|---|
| **Fetch + parse** | `python research/scripts/scrape.py controls` | `python research/scripts/scrape.py domains` | `python research/scripts/scrape.py types` | `python research/scripts/scrape.py level-definitions` |
| **Diff** | `python research/scripts/diff_corpus.py` | `python research/scripts/diff_domains.py` | `python research/scripts/diff_system_types.py` | `python research/scripts/diff_level_definitions.py` |
| **Read the report** | `research/corpus/scrape-diff-<date>.md` | `research/corpus/domains-diff-<date>.md` | `research/corpus/system-types-diff-<date>.md` | `research/corpus/level-definitions-diff-<date>.md` |
| **Verify** | delegate to **`corpus-verifier`** | delegate to **`corpus-verifier`** | delegate to **`corpus-verifier`** | delegate to **`corpus-verifier`** |
| **Promote** | `python research/scripts/promote.py --dry-run` then `--apply` | `python research/scripts/promote.py domains --dry-run` then `--apply` | `python research/scripts/promote.py system-types --dry-run` then `--apply` | `python research/scripts/promote.py level-definitions --dry-run` then `--apply` |

`python research/scripts/scrape.py all` runs all four fetch+parse steps in one call. There is no
combined diff/promote command — read each report on its own; they cover different fields and a
clean controls diff says nothing about domains or system-types.

Always `--dry-run` before `--apply`. Never skip reading the diff report first, and never promote
on the strength of "it looked fine last time" — the parser keys on text landmarks against a
Next.js/Tailwind site with content-hash anchors, so it *will* break on a redeploy, and it can
break silently (see Invariants below).

## When to call the `corpus-verifier` agent

**Before every `--apply`**, and **whenever `scrape.py`'s parsing logic changed** (a new or edited
landmark, a new field). The diff script only tells you the Python parse disagrees with the
*shipped* file — it cannot tell you the Python parse still agrees with the *live page*, which is
the actual claim being promoted. Two independent paths agreeing (the Python parser, and a Chrome
read of the rendered DOM) is the real evidence; a clean diff against old shipped data is not.
Give it the specific pages and fields to check — it does not re-verify everything by default.

## Scraped-format schema (`research/corpus/scraped/*.json`)

Deliberately a **superset** of the shipped schema — capturing more than `docs/assets/data/`
currently carries is the point, so omissions surface in the diff rather than staying invisible.

- **`controls.json`** — per control: `id`, `domainId`, `catalog`, `title`, `sourceUrl`,
  `retrievedAt`, `statement`, `recommendations`, `risk` (cybersecurity) or `rationale` (dss),
  `group`, `parameters[]`, `links[]` (real hrefs). Since ADR-002 (2026-09-02) these ship
  straight through to `controls.json` as `description`/`recommendations`/`risk-or-rationale` —
  no `guidance` composition step exists any more (`statement` still renames to `description`).
- **`system-types.json`** — per type: `id`, `slug`, `catalog`, `name` (the page's own H1 heading —
  this **is** what shipped `name` matches), `templateName` (the System Characteristics `Name:`
  field — a filled-in example like "Low-Risk Cloud **System**", not the type's display name; kept
  for the record, never compared against shipped `name`), `description`, `sensitivity`,
  `domainsUsed[]`, `landingBlurb` (the SSP landing page's own paragraph for this type — the source
  of shipped `classificationText` for the two DSS types), `lastUpdated`, `sourceUrl`,
  `retrievedAt`, a small `blocks[]` sample (the pre-per-control-detail summary section only, for
  quick human/agent spot checks — not the full page).
- **`level-definitions.json`** — `sourceUrl`, `retrievedAt`, `"0"`/`"1"`/`"2"`, `selectionGuidance`.
- **`domains.json`** — per domain: `id`, `name`, `catalog`, `description`, `sourceUrl`,
  `controlCount` (derived from `scrape.py domains`'s own per-domain control count, not a
  textual field upstream), `lastUpdated`, `retrievedAt`. Scraped off the same control-catalog
  landing page `scrape_domain()` already fetches for `controls.json` — the domain name and
  description sit in the leading blocks before the first control, via the same `"Home"` +
  fixed-offset landmark pattern `scrape_system_type()` uses.

## Invariants — get these wrong and a promotion is wrong

1. **`compose_classification_text` lives in `promote.py` and nowhere else.**
   `diff_system_types.py` `import`s it rather than restating the composition rule. This is
   deliberate: if someone changes how a field is composed in one place only, the diff reports
   clean while the shipped data is wrong — a false clean diff is worse than an honest dirty one.
   Keep the coupling; do not "simplify" it away. (`compose_guidance` no longer exists — ADR-002
   removed the composed `guidance` field entirely, so `diff_corpus.py` now compares
   `recommendations`/`risk`/`rationale` directly with no composition step to keep in sync.)
2. **`levelsAvailable`, `totalControls`, `levelCounts` are not upstream-scrapeable.** No type page
   carries a "Level N (n)" breakdown in any textual form (confirmed 2026-09-01 by grepping the
   full scraped blocks for both DSS types). They are correctly derived from `profiles.json` today
   — `corpus.py stats` is the check, not this pipeline. `promote.py`'s `build_system_types()`
   leaves them untouched.
3. **`name` in `system-types.json` is diff-reported but never auto-promoted.** One of the 8 type
   pages has a live upstream typo (`low-risk-on-premises`'s own H1 is "Low-Risk On Premises",
   missing the hyphen the other 7 use consistently). Promoting `name` mechanically would silently
   import that typo. If upstream fixes it, the diff will start reporting a match — that's fine to
   ignore; it never needs manual promotion either way since the field would then already agree.
4. **Fail loudly, always.** Every `scrape_*` function in `scrape.py` raises `RuntimeError` on an
   empty or structurally-unexpected parse rather than returning a partial result. A silent empty
   parse is exactly how the original IS/LM/PM/ST guidance gap (F-001) went unnoticed. If you add a
   new scraper, keep this property — a parser that can return `None`/`{}`/`[]` on failure is a
   parser that will fail silently on the next redeploy.
5. **`research/corpus/raw/*.html` is a cache, not ground truth.** `scrape.py` reads it by default;
   pass `--no-cache` to refetch. A stale cache makes the diff compare two old snapshots and report
   clean when upstream has actually moved. It's gitignored — delete individual files or the whole
   directory to force a refetch for just what you need.

## Read-only tools that already know this corpus

- **`ssp-corpus`** skill — the shipped schema, its invariants, and `corpus.py` for querying
  without loading the JSON into context. Load that one for anything that isn't "I'm about to
  change the data."
- **`corpus-analyst`** agent — bulk analysis over the corpus, kept out of the caller's context.
