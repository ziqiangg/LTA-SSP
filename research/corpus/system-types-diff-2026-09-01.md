# system-types.json diff — upstream vs shipped

Generated `2026-09-01` by `research/scripts/diff_system_types.py`.
Upstream: 8 types · Shipped: 8 types

## 1. Membership

No difference — the same 8 type ids appear in both.

## 2. `name` — reported only, never auto-promoted

Upstream's page heading is the source of truth for `name` (verified: it matches shipped for 7/8 types exactly). The System Characteristics `Name:` field is a filled-in template example, not the type name, and is not compared here — see scrape.py's `templateName` vs. `heading` note.

- `low-risk-on-premises` — upstream 'Low-Risk On Premises' vs. shipped 'Low-Risk On-Premises'
  (known upstream typo — the live page's own H1 is missing the hyphen the other 7 types use consistently. Not promoted; shipped's hyphenated form is correct.)

## 3. `classificationText`

No differences — composed text matches shipped for all 8 types.

## 4. `domainsUsed`

No differences.

## 5. `sourceUrl`

No differences.

## 6. Fields this scrape cannot verify

`levelsAvailable`, `totalControls`, and `levelCounts` are not present in any textual form on the type pages (no "Level N (n)" pattern exists) — confirmed by grepping the full scraped blocks for both DSS types. These are correctly derived from `profiles.json` today (see `corpus.py stats`), not from this scrape, and are left untouched by promotion.

## Verdict

**1 field-level difference(s)** across 1 category(ies). Review sections 2–5 before promoting.
