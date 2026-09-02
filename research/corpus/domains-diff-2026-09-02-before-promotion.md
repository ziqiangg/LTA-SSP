# domains.json diff — upstream vs shipped

Generated `2026-09-02` by `research/scripts/diff_domains.py`.
Upstream: 26 domains · Shipped: 26 domains

## 1. Membership

No difference — the same 26 domain ids appear in both.

## 2. `name`

- `WO` — upstream 'WCAG : Operable' vs. shipped 'WCAG - Operable'
- `WP` — upstream 'WCAG : Perceivable' vs. shipped 'WCAG - Perceivable'
- `WR` — upstream 'WCAG : Robust' vs. shipped 'WCAG - Robust'
- `WU` — upstream 'WCAG : Understandable' vs. shipped 'WCAG - Understandable'

## 3. `description`

F-008 flagged `AC`'s shipped description as authored rather than scraped — this section is where that would surface.

- `AC`
  - shipped:  Controls governing account lifecycle management, authentication (including MFA and SSO), least-privilege access, endpoint device management, and separation of duties.
  - upstream: Controls to protect against unauthorised access to agency systems.
- `UU`
  - shipped:  Controls for understanding public users' needs and validating designs with them through user research and usability testing.
  - upstream: Controls to ensure services are informed by real user needs and behaviors.

## 4. `controlCount`

No differences.

## 5. `catalog`

No differences.

## 6. `sourceUrl`

No differences.

## Verdict

**6 field-level difference(s)** across 2 category(ies). Review sections 2–6 before promoting.

---

**Verified 2026-09-02 by the `corpus-verifier` agent** against the live rendered DOM (not the
Python parse) for 5 sampled pages: AC, UU, WO, WR, and BR as a clean-diff positive control. All
5 matched the scraped values above exactly — including confirming "WCAG : Operable" etc. render
as a literal ASCII colon with plain spaces, not a unicode substitution. One incidental note from
the verifier: WR-1's per-control "Group:" badge still reads "WCAG - Robust" (hyphen) even though
the domain heading itself now reads "WCAG : Robust" (colon) — an upstream inconsistency between
the domain-page heading and the per-control group tag. Not a defect in this scrape (which reads
only the breadcrumb/H1 pair, not the per-control Group tag), but worth remembering if a future
scraper ever sources a domain name from a control's Group field instead.

Promoted via `python research/scripts/promote.py domains --apply` (see
`domains-diff-2026-09-02-after.md` for the resulting clean re-diff).
