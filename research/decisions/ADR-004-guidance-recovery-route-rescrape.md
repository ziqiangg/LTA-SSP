---
id: ADR-004
title: Recover F-001's guidance gaps via re-scrape, not OSCAL import
date: 2026-09-02
status: accepted
findings: [F-001, F-006, F-008]
---

## Context

F-001 found that 50 of 248 controls shipped with an empty `guidance` field, and that the gaps were
not scattered — they were the entire contents of four domains (IS 14/14, LM 21/21, PM 10/10, ST
5/5). It confirmed guidance exists upstream for all four (14 spot-checks, plus 100% OSCAL coverage
in every affected group), so the gap was a scrape failure, fully recoverable. F-001 named two
routes and was explicit that the choice mattered: "Decide the route in an ADR before acting; this
is exactly the kind of choice that should not be made incidentally."

**This ADR was not written before acting.** The recovery happened in practice, as a side effect of
fixing a larger problem (below), and the route decision was never separately recorded. This ADR
records it now, retroactively, closing that gap rather than leaving an undocumented fact standing
in for a decision.

F-006 evaluated the second route — the official OSCAL catalog
(`GovTechSG/tech-standards`, `catalogs/im8-reform.json`) — as an import source, and found it
cannot serve as one:

- **Half-coverage:** 137 controls across 15 groups, against our 248 across 26. It has no GA
  (Generative AI) group and no DSS/WCAG groups at all — 9 of our domains and 92 controls have no
  OSCAL counterpart.
- **Stale and already drifted:** dated 2025-05-13, while the live site had moved to 2026-03-24.
  Counts have diverged even in groups OSCAL does cover: `lm` 20 vs. our (correct) 21, `pm` 8 vs.
  our 10.
- A **hybrid** route (OSCAL for its 15 covered groups, scrape for GA/DSS) was named as a third
  option, with its own named risk: two sources of the same corpus drifting apart over time.

Then F-008 found something bigger than F-001: the *entire* shipped corpus was not a faithful
scrape at all — only 42 of 198 `guidance` fields matched upstream verbatim; 156 had been
paraphrased (American spellings introduced into a British-spelling source, systematic shortening,
title-casing, synthesised citations). Fixing F-008 required a full re-scrape of all 26 catalog
pages and a `promote.py --apply` rebuild of `controls.json`, regardless of what route F-001 alone
would have picked. That rebuild recovered all 50 of F-001's gaps as a byproduct, at 100% (IS
14/14, LM 21/21, PM 10/10, ST 5/5) — confirmed by `diff_corpus.py` reporting zero differences
against upstream afterward.

## Decision

**Re-scrape is the recovery route** — record it as the deliberate choice, not an accident of
sequencing. OSCAL import is rejected as a route for `docs/assets/data/*.json`, now and not just
incidentally:

- OSCAL cannot recover F-001's specific gap alone even at the domain level it does cover, because
  its counts for those domains (`lm`, `pm`) are already out of sync with the live standard this
  project treats as ground truth (`research/CLAUDE.md`) — importing it would trade one fidelity
  problem for another.
- OSCAL could never have addressed F-008, which is the larger problem and forced a full-corpus
  re-scrape on its own terms. A route chosen to solve only F-001 would have left ~150 paraphrased
  guidance fields untouched.
- The hybrid route is rejected for the same reason it was flagged as risky in F-006: once a full
  re-scrape is required for F-008 anyway, splitting the corpus across two source formats buys
  nothing and adds a standing drift risk between them.

The schema question F-001 also raised — whether to keep guidance and the risk statement joined or
split into separate fields — is **not re-decided here**; it was separately and formally decided in
[ADR-002](ADR-002-split-guidance-into-recommendations-and-risk.md) (accepted, implemented), which
this ADR cross-references rather than duplicates.

## Consequences

**Makes easy:**
- Validates the standing `corpus-ingest` pipeline (`scrape.py` → `diff_*.py` → verify →
  `promote.py`) as the single, ongoing mechanism for keeping `docs/assets/data/*.json` current —
  this was already the practice; this ADR removes the ambiguity of OSCAL import as an unresolved
  "maybe someday" alternative sitting alongside it.

**Makes hard / forecloses:**
- OSCAL is not adopted as a data source for the shipped corpus. F-006's genuinely useful OSCAL-only
  features — machine-readable links to source IM8 clauses, a separately queryable `risk-statement`
  prop, richer provenance metadata — are not captured by `scrape.py` today and remain a known gap,
  not addressed by this decision.
- If OSCAL's coverage gap ever closes (F-006's open question: is it still maintained, will GA/DSS
  be added), that would be grounds to revisit this ADR — not something this decision commits to
  watching for.

## Alternatives considered

- **Import from the official OSCAL catalog.** Rejected — half-coverage (137/248, no GA or DSS
  groups), stale relative to the live site, and already drifted in the groups it does cover (F-006).
- **Hybrid: OSCAL for its 15 covered groups, scrape for GA and DSS.** Rejected — F-006 itself named
  the risk of two sources drifting apart, and it stopped being worth that risk once F-008 forced a
  full re-scrape regardless.
- **Leave the route formally undecided, since the rebuild already happened.** Rejected — this is
  exactly the "decided incidentally" outcome F-001 warned against; recording it now, after the
  fact, is cheap and closes a real gap in the project's decision record.
