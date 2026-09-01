---
id: F-001
title: Missing guidance is four whole domains, not scattered gaps
date: 2026-09-01
rq: [RQ-5]
implications: [data]
confidence: high
status: confirmed
updated: 2026-09-01
---

> **Confirmed upstream (2026-09-01).** Guidance exists upstream for every control spot-checked
> across all four domains (14 checked), and the official OSCAL catalog shows 100% guidance coverage
> in every group. This is a scrape failure and it is fully recoverable. See F-006 for the recovery
> route.

## Observation

50 of 248 controls have no `guidance` field. They are not scattered — they are the **complete
contents of exactly four domains**:

| domain | name | controls without guidance | domain total |
|---|---|---|---|
| IS | Infrastructure Security | 14 | 14 |
| LM | Logging and Monitoring | 21 | 21 |
| PM | Security Programme Management | 10 | 10 |
| ST | Security Testing | 5 | 5 |

14 + 21 + 10 + 5 = 50. Every other domain has `guidance` on every control. No domain is partially
covered.

## Evidence

- `python research/scripts/corpus.py gaps` → "by domain: {'IS': 14, 'LM': 21, 'PM': 10, 'ST': 5}"
- `python research/scripts/corpus.py domains` → domain totals IS 14, LM 21, PM 10, ST 5
- repo @ `4e7e6ba`

## Upstream verification (2026-09-01)

**Guidance exists upstream for all four domains.** 14 controls spot-checked (IS-1/2/3, LM-1/2/3,
PM-1/2/3, ST-1/2/3/4/5) — every one has published guidance of the same kind other domains carry.
Sample, LM-1 *Separate Log Storage*:

> "Do not store logs only in the same system component that generated it. For example, an
> application server on EC2 or ECS should send logs to a separate storage such as an S3 bucket as
> soon as possible after the logged event instead of only storing it on the server. For cloud audit
> logs, store them in a separate system or account."

Corroborated machine-readably: in the official OSCAL catalog
(`GovTechSG/tech-standards`, `catalogs/im8-reform.json`) guidance coverage is **100% in every
group**, including `is` 14/14, `lm` 20/20, `pm` 8/8, `st` 5/5.

## Interpretation

Confirmed: this is a **per-domain scrape failure**, not editorial omission. All-or-nothing at the
domain boundary was the right signal to read — genuine editorial absence would vary within a
domain; a page-fetch or parse failure would not.

~20% of the corpus is missing its most user-facing content, and the affected domains are not
marginal: LM is the single largest domain in the catalog, and IS, PM and ST all sit in the core
cybersecurity baseline. All of it is recoverable.

## Implications

- **data:** Recoverable, and there are two routes. Re-scrape the four domain pages, or import from
  the official OSCAL catalog (F-006) — but the OSCAL catalog is stale (2025-05-13) and its counts
  have already drifted from the live site (`lm` 20 vs our 21, `pm` 8 vs our 10), so it cannot be
  used as a drop-in. Decide the route in an ADR before acting; this is exactly the kind of choice
  that should not be made incidentally.
- **data:** Note that upstream OSCAL keeps `risk-statement` as a **separate prop**, while our
  `guidance` field is the *website's* concatenation of guidance prose and a trailing `Risk: ...`
  clause. Whichever recovery route is chosen, decide deliberately whether the schema keeps them
  joined or splits them — splitting would make the risk statement independently queryable, which
  is likely useful for the classifier.
- Until recovered, any analysis using `guidance` as a text field must report its denominator as
  **198, not 248**, and must not treat the four domains' absence as signal.

## Open questions

- Were these four domains scraped in a separate pass or by a different code path? Without a
  committed scraper this cannot be answered — which is itself the argument for committing one.
- Should the site distinguish "no guidance published" from "guidance not captured"? Right now both
  render as a silently shorter card.
