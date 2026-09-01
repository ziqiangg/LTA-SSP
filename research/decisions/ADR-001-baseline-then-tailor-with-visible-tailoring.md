---
id: ADR-001
title: Baseline-then-tailor, with a real (visible, recorded) tailoring step
date: 2026-09-01
status: proposed
findings: [F-002, F-003, F-004, F-005, F-007]
---

## Context

F-007 found a framing conflict the SSP itself doesn't resolve: its only selection-guidance
sentence — "Agencies and their industry partners are required to assess the risks and threats for
each of their systems, to determine the controls required to mitigate the risks" (the corpus's
sole `selectionGuidance`, F-003) — is phrased the **ISO way**: assess risk, then determine
controls. But every artifact the standard actually publishes is **NIST-shaped**: 8 fixed
system-type templates, each a complete pre-baked control baseline (`system-types.json`,
`profiles.json`). `wizard.js` mirrors that NIST behavior exactly — 7 fixed questions, one baseline
out, no adjustment step, no persistence.

That gap has concrete, documented costs (F-004):
- Composite systems are structurally unreachable — a GenAI-powered public digital service can only
  ever answer q1 *or* q3, never both (issue 1). Now that F-002 has settled composition as
  "permitted but not required," the wizard is actively unable to express a legitimate combination.
- On-premises systems never reach a sensitivity question at all (issue 2) — a real limit of the
  standard (only one on-premises template exists), but one the wizard doesn't disclose beyond a
  one-line caveat.
- Every outcome is single, unranked, and thrown away on completion — `history` is never persisted
  to the URL, so a result can't be shared, revisited, or cited as a decision record (issue 4).

Meanwhile our data genuinely supports a baseline mechanism (F-005): `low-risk-cloud ⊂
medium-risk-cloud ⊂ high-risk-cloud` (0 controls unique to the lower tier at each step; medium→high
adds 20, escalates 38 more), and both overlay profiles (`generative-ai`; the DSS controls) are
fully disjoint from every hosting profile. F-007 shows this makes FIPS 199's high-water-mark
composition (PA-003) well-defined for us: combining an overlay with a hosting tier is a plain union
with zero conflicts, and combining hosting tiers is a `min()` over the ordered ladder (strictness
*decreases* as the level number increases — F-005 flags `min()` vs `max()` explicitly as a trap).

F-007 also surveyed 13 prior-art sources and found four independent frameworks — NCSC CAF, ISO
27001's Statement of Applicability, SP 800-53B, and GOV.UK — converge on one alternative to a
filtered control list: show every control with a status and a reason. Checked against
`controls.js`: catalog mode already renders every control in a catalog regardless of profile
membership, so the mechanism half-exists; `workingControls()`'s system-type path currently *drops*
any control outside the profile via `.filter()`, which is a contained change to flip to a
status-lookup. The genuinely missing piece is data, not code: no field anywhere in `profiles.json`
records *why* a control is excluded, and nothing upstream supplies that text. SP 800-53B §2.4
(PA-005) is the only written taxonomy of exclusion reasons F-007 found — borrowable as a starting
vocabulary, not scrapeable as ground truth.

## Decision

Serve **baseline-then-tailor** — not risk-first from scratch, and not today's silent
single-baseline handoff either. Make the tailoring step real, visible, and recorded.

1. **Compute a starting baseline via tick-all-that-apply plus high-water-mark composition**,
   replacing the single-outcome q1–q7 tree. A user selects every applicable characteristic
   (hosting tier, GenAI, digital-service traffic tier, sandbox/non-prod) instead of being forced
   down one exclusive branch. The resolve is a plain union for overlays (safe — F-005) and `min()`
   across the hosting-tier ladder. This is not a different mechanism from NIST baselining — it is
   NIST baselining extended to a system that can legitimately be more than one type, which the
   current tree cannot express.

2. **Render the computed baseline as every control with a status and a reason, never a filtered
   list** — the convergent recommendation across NCSC CAF, ISO SoA, SP 800-53B, and GOV.UK. Every
   catalog control appears; controls outside the computed profile show "not applicable" with a
   reason, not silent absence. Presentation-only for the in-profile half (`workingControls()`
   changes from a drop to a status-lookup); the exclusion-reason text has no backing data today and
   must be authored, using SP 800-53B §2.4's six scoping considerations as a starting taxonomy.

3. **Treat the computed baseline as a draft, not a final answer** — the ISO layer. The standard's
   own risk-assessment sentence becomes an explicit second step after the baseline: a place to
   record why a specific control was added above it or dropped below it, mirroring FIPS 199's own
   sanctioned upward override and ISO's Statement of Applicability. This ADR commits to the
   *direction*, not the implementation — the shape of "record an adjustment" (free text? a
   predefined reason set? persisted where, given `docs/` is a static site with no backend?) is left
   to site work, designed against real usage of steps 1–2 first.

Persist answer state (to the URL, at minimum) so a computed baseline — and any later adjustment —
can be shared, revisited, and used as real evidence. F-004 issue 4 names this gap; it becomes
load-bearing here, since the artifact produced is no longer just an answer, it's evidence.

## Consequences

**Makes easy:**
- Composite systems get a real, correct answer instead of forced exclusivity (F-004 issue 1
  resolved) — now that F-002 has settled composition as legitimate, the tool can finally express it.
- The 8-type structure stops being memorised special cases and becomes derivable from a small set
  of orthogonal characteristics, using composition F-005 already proved safe.
- The output starts looking like a draft SSP with justifications — F-007's highest-value, cheapest
  recommendation, and presentation-only for the in-profile half.

**Makes hard:**
- The wizard needs a genuinely different interaction model (tick-all-that-apply), not a copy-edit
  of the existing linear `TREE`.
- Exclusion-reason text doesn't exist anywhere upstream and must be authored per control or per
  domain — real content work, not something `corpus-ingest` can pull from a scrape.
- Recording adjustments (step 3) needs new data model and possibly new persistence, genuinely
  undesigned — deferred deliberately, not solved here.

**Forecloses:**
- A wizard that returns one clean type name with a one-line breadcrumb (today's UX) stops being the
  target end state; future wizard work should not keep optimising that shape.
- Treating `profiles.json` as immutable per-type truth with no per-control justification becomes a
  temporary state, not the destination — the pending statement/recommendations/risk split (F-008)
  should leave room for a justification field if it's revisited.

## Alternatives considered

- **Pure risk-first (ISO), discard the baseline mechanism.** Rejected: the standard's own
  risk-selection guidance is one sentence with no method (F-003) — building a real risk-assessment
  engine from that is inventing the standard, not implementing it, and would discard real, reliable
  baseline data (F-005) upstream already computed correctly.
- **Keep the status quo (single-outcome tree, unchanged).** Rejected: F-004 documents concrete
  reachability failures hurting users today, and no source in F-007's 13-source review stops at a
  single filtered answer — four independently converge on status + reason instead.
- **Adopt OSCAL profile-resolution wholesale** (`oscal-cli resolve-profile`, PA-013), replacing our
  own composition logic. Deferred, not rejected: F-006 shows the official OSCAL source is
  half-coverage and stale, so it can't drive this today. Revisit if F-006's gap closes.
