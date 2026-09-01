# Research — helping users find the controls that apply to them

**Read this file to orient. Don't read the whole folder.**

## The problem

Singapore's SSP publishes 248 controls across 26 domains. A user with a system has to work out
which ~100 of them apply, and what to actually do about each. Today the only path is:

> answer 7 fixed questions → get exactly 1 of 8 system types → look up that type's control list

That is `docs/assets/js/wizard.js` (a hardcoded tree that fetches nothing) feeding
`docs/assets/js/controls.js` (a join against `profiles.json`). It works, but it cannot rank,
cannot express a system that is two things at once, and stops at the type — never at "here is what
you should do".

## Two consumers of every finding

1. **The site** (`docs/`) — improve how users get from "I have a system" to "these controls".
2. **A future classifier** — free-text system description → relevant controls + guidance,
   possibly LLM-assisted. Not being built yet, but findings should be recorded in a form it could
   consume. This is why every finding carries an `implications:` tag.

## Reading order

| File | What it is |
|---|---|
| `QUESTIONS.md` | The RQ backlog. The spine of the work — start here. |
| `findings/` | One finding per file, `F-NNN-slug.md`. |
| `prior-art/` | One card per external source, `PA-NNN-slug.md`. |
| `decisions/` | `ADR-NNN-slug.md` — choices that bind the site or the classifier. |
| `corpus/` | Derived tables from corpus analysis. |
| `evals/` | Labelled eval sets, schema, and benchmark results. |
| `JOURNAL.md` | Append-only dated log. Read by tail. |
| `CLAUDE.md` | The conventions this folder runs on. |

## Findings so far

| id | title | implications | confidence | status |
|---|---|---|---|---|
| [F-001](findings/F-001-guidance-gaps-cluster-by-domain.md) | Missing `guidance` is four whole domains — a scrape failure, recoverable | data | high | **confirmed** |
| [F-002](findings/F-002-generative-ai-profile-standalone-or-overlay.md) | `generative-ai` is 9 controls and upstream never says whether it stands alone | data, site, classifier | high | **confirmed** |
| [F-003](findings/F-003-level-definitions-dead-and-contradicted.md) | `level-definitions.json` is dead data and the UI contradicts it | data, site | high | open |
| [F-004](findings/F-004-wizard-tree-reachability-gaps.md) | The wizard tree has unreachable and forced outcomes | site, classifier | high | open |
| [F-005](findings/F-005-profiles-are-nested.md) | Profiles nest, and OSCAL confirms it is deliberate | classifier, site | high | **confirmed** |
| [F-006](findings/F-006-official-oscal-source-exists-but-partial.md) | An official OSCAL source exists, but is half-coverage and stale | data, site, classifier | high | open |
| [F-007](findings/F-007-prior-art-synthesis-control-discovery.md) | Prior art solves selection *after* typing — nobody types from a description | site, classifier | high | open |
| [F-008](findings/F-008-shipped-corpus-is-paraphrased-not-scraped.md) | **The shipped corpus is not a faithful scrape — most guidance was paraphrased** | data, site, classifier | high | **actioned** |
| [F-009](findings/F-009-system-type-pages-linked-to-404.md) | All 8 system-type pages linked their main CTA to a 404 | site | high | **actioned** |
| [F-010](findings/F-010-eval-pilot-no-case-has-one-answer.md) | Blind eval pilot: no realistic description had a single correct answer | classifier, site | medium | open |
| [F-011](findings/F-011-eval-answer-set-homogeneity.md) | 6 of 15 pilot cases share one identical hosting-unknown answer pair | classifier | medium | open |

**F-008 was promoted 2026-09-01 (session 3, then extended session 4).** `controls.json`,
`system-types.json` and `level-definitions.json` all now reproduce upstream exactly (or, for
`system-types.json`'s `name` field, differ from upstream by one confirmed live typo — see F-008's
header note). `domains.json` remains only spot-checked, not run through the full pipeline.

**Known drift, since fixed:** `docs/system-types/sandbox/index.html` hardcoded the pre-correction
paraphrased sensitivity text ("Security sensitivity level designated as…") that
`system-types.json` no longer carries — exactly the risk `docs/CLAUDE.md`'s "Known drift risk"
note describes. Synced to match the corrected `classificationText` (one line, presentation only —
no data change). No other system-type page carried the stale phrasing.

**Decisions waiting on an ADR:** (1) the F-001 guidance-recovery route — re-scrape vs OSCAL import
vs hybrid; (2) whether this tool serves risk-first (ISO) or baseline-then-tailor (NIST) selection,
which F-007 shows the standard and our wizard currently answer differently.

Prior-art cards: `prior-art/PA-001..PA-013`, indexed in F-007. Read F-007 rather than the cards.

## Authoritative sources

- **<https://info.standards.tech.gov.sg/ssp/>** — the standard itself, plus its child pages (the 8
  system-type templates) and grandchild pages (`/control-catalog/cybersecurity/<domain>/`). This is
  the source `docs/assets/data/*.json` was scraped from and the arbiter for any data dispute.
- **<https://github.com/GovTechSG/tech-standards>** — the official **OSCAL 1.1.2** publication of
  the IM8 framework (137 controls, 15 groups, 6 profiles, MIT-licensed). Structured and
  authoritative, but **half-coverage and stale** — no GA or DSS groups, only low/medium-risk
  profiles, dated 2025-05-13 with counts already drifted from the live site. Read F-006 before
  reaching for it as an import source. Not findable by repo-name search within the org.

Both are *authoritative*, not *user-generated*. Neither tells us how a real system owner describes
their own system — which is the gap constraining RQ-1 and limiting what v1 of the eval can claim.
See `evals/README.md`.

## Working here

Query the corpus, don't read it:

```
python research/scripts/corpus.py stats     # start here
python research/scripts/corpus.py gaps      # corpus defects
python research/scripts/corpus.py --help
```

Skills: `ssp-corpus`, `corpus-ingest`, `research-note`, `prior-art-review`, `eval-set`.
Agents: `corpus-analyst` (data crunching), `literature-scout` (all web reading), `corpus-verifier`
(independent Chrome cross-check before promoting a scrape).

`research/` is committed and public, but is **not** served by GitHub Pages — only `docs/` is.
