---
id: ADR-001
title: Baseline-then-tailor, with a real (visible, recorded) tailoring step
date: 2026-09-01
status: accepted
findings: [F-002, F-003, F-004, F-005, F-007, F-012]
---

> **Amendment (2026-09-02):** Decision item 3 (the minimal tailoring record) is rejected — see
> [ADR-003](ADR-003-reject-tailoring-record.md). Items 1 and 2 remain in force and are implemented.
>
> **Amendment (2026-09-02):** the baseline-resolution table's cloud sensitivity rung is amended —
> CII designation is split out as its own characteristic, and the `medium`/`high` rungs merge into
> one "Confidential, Sensitive High" band — see [ADR-005](ADR-005-cii-as-independent-baseline-characteristic.md).

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
   instead of being forced down one exclusive branch. This is not a different mechanism from NIST
   baselining — it is NIST baselining extended to a system that can legitimately be more than one
   type, which the current tree cannot express.

   **Baseline resolution model.** The first draft of this ADR treated "hosting tier" and
   "sandbox/non-prod" as separate parallel tick-boxes. F-012 (filed during review) shows that is
   wrong: `sandbox` shares `low-risk-cloud`'s and `medium-risk-cloud`'s exact 117-control
   membership and is a strict subset of `high-risk-cloud`'s 137 — it is the laxest rung of the
   *same* ladder F-005 already describes, not an orthogonal flag. The resolution model below
   replaces the earlier tick-box list. Each row's provenance is marked: **[upstream]** — stated or
   directly derivable from the standard; **[derived]** — a structural fact measured from the
   corpus (a finding, not a standard claim); **[ours]** — a design choice this project is making
   where the standard is silent.

   | characteristic | values | shape | composition op | provenance |
   |---|---|---|---|---|
   | hosting location | on-premises / cloud | mutually exclusive, single-select | none — a system is hosted one way | **[upstream]** only one on-premises template exists (F-004 issue 2) |
   | cloud sensitivity rung | sandbox < low < medium < high | ordered ladder; tick one, or several if unsure | `min()` across ticked rungs (trap: strictest is the *lowest* level number — F-005) | **[derived]** ladder membership and `min()`-correctness verified per rung, including sandbox, F-005 + F-012 |
   | GenAI overlay | present / absent | independent tick | plain union with whatever hosting profile is resolved — zero shared controls, zero level conflicts (F-005) | **[upstream, owner-confirmed]** permitted-not-required, F-002 |
   | digital-service overlay | absent / others / high-impact | tick; if present, one of two sub-rungs | internal `min()` between the two sub-rungs (F-005 — identical 92-control membership, level-only difference), then union with the hosting profile like GenAI | **[upstream, owner-confirmed]** permitted-not-required, F-002 |

   **Conflict behaviour, stated explicitly (previously unstated):**
   - *On-premises ticked alongside a cloud sensitivity rung.* Not composable — on-premises sits
     outside the cloud ladder in both directions (F-005: 7 controls only on-prem, 21 only on the
     cloud tiers it was compared against) and carries no sensitivity branching of its own (F-004
     issue 2). The tool must present this as a disclosed limit of the standard, not compute a
     merged answer. **[upstream limit, disclosed — not a gap to engineer around]**.
   - *Sandbox ticked alongside a sensitivity/CII signal the sandbox rung cannot express.* Sandbox's
     117-control membership never gained `high-risk-cloud`'s extra 20 (F-012) — there is no
     upstream-defined "CII sandbox". The honest output is a flagged gap ("this combination is
     unrepresented upstream"), not a guess between `sandbox` and `high-risk-cloud`. **[derived
     gap, F-012 — surface, do not silently resolve]**.
   - *An overlay's own sensitivity ceiling disagrees with the ticked hosting rung* (e.g.
     `generative-ai`'s `classificationText` caps at "Up to Confidential, Sensitive High", but the
     user also ticked `low-risk-cloud`). Not currently validated anywhere. Left as an open gap for
     implementation, not resolved by this ADR. **[ours — unresolved, flagged so it isn't lost]**.

2. **Render the computed baseline as every control with a status and a reason, never a filtered
   list** — the convergent *prior-art* recommendation across NCSC CAF, ISO SoA, SP 800-53B, and
   GOV.UK (F-007). These four are used here strictly as **research/design references for
   presentation and tailoring UX** — evidence that "status + reason, not a filtered list" is a
   proven pattern elsewhere. They do **not** expand the control corpus and supply no normative
   control content for the webpage: every control, status default, and piece of guidance still
   comes only from the SSP itself (`docs/assets/data/*.json`), never from CAF/SoA/800-53B/GOV.UK
   text. (The one exception, spelled out below, is the *status/reason taxonomy* — SP 800-53B is
   borrowed there as vocabulary, and that borrowing is marked `[ours]` and kept visible in the UI,
   not folded in silently as if it were SSP content.) Every catalog control appears; controls
   outside the computed profile show "not applicable" with a reason, not silent absence.
   Presentation-only for the in-profile half (`workingControls()` changes from a drop to a
   status-lookup).

   **Status/reason taxonomy.** The SSP itself supplies no exclusion vocabulary at all —
   `selectionGuidance` is one unmethodical sentence (F-003). The taxonomy below is **[ours]**,
   borrowed wholesale from a *different* standard (SP 800-53B §2.4, PA-005) as a starting
   vocabulary, not a claim about what the SSP itself says. That borrowing must stay visible in the
   UI copy (e.g. "reason categories adapted from NIST SP 800-53B"), not presented as SSP text.

   | status | meaning | source |
   |---|---|---|
   | `in-profile` | control is in the computed baseline | mechanical — output of step 1's resolution |
   | `not-in-profile` | outside the computed baseline; the default, mechanical case | mechanical — no human judgement involved |
   | `scoped-out: applicability` | doesn't apply to a component this system has | **[ours]**, SP 800-53B §2.4 |
   | `scoped-out: operational` | an assumed operational fact (mobile, air-gapped, single-user, …) doesn't hold | **[ours]**, SP 800-53B §2.4 |
   | `scoped-out: technology` | the named technology isn't present or required | **[ours]**, SP 800-53B §2.4 |
   | `scoped-out: mission` | would degrade or endanger the mission | **[ours]**, SP 800-53B §2.4 |
   | `scoped-out: objective` | supports only one of C/I/A, not the objective driving this system's category | **[ours]**, SP 800-53B §2.4 |
   | `scoped-out: legal` | a legal/policy trigger doesn't apply in this circumstance | **[ours]**, SP 800-53B §2.4 |

   The six `scoped-out:*` categories only ever apply to a control that is `in-profile` — they are
   a *human* override of a mechanical inclusion, never a way to explain `not-in-profile`. Conflating
   the two would misrepresent a computed absence as a deliberated exclusion. A sixth 800-53B
   concept — **common/inherited controls** (satisfied by the hosting platform, not the system
   owner) — is deliberately **not** added as a status here: it needs a new `inheritable` field with
   no upstream source and no site consumer yet designed. Noted as a live option (PA-005), not
   committed to by this ADR.

3. **Treat the computed baseline as a draft, not a final answer** — the ISO layer. The standard's
   own risk-assessment sentence becomes an explicit second step after the baseline: a place to
   record why a specific control was added above it or dropped below it, mirroring FIPS 199's own
   sanctioned upward override and ISO's Statement of Applicability.

   **Minimal tailoring record — scoped down on review.** An earlier draft of this ADR left the
   shape entirely open pending "real usage." On reflection, the goal this ADR itself states (F-004
   issue 4: a result should be shareable, revisable, citable) doesn't need a general adjustment
   engine — it needs exactly enough to render what a draft SSP page has to show. `docs/` is a
   static site with no backend and no accounts, which caps what "record" can mean here anyway.
   The minimal record is:

   - Per control, **at most one override**: `added` (include despite `not-in-profile`) or
     `dropped` (exclude despite `in-profile`), plus one free-text line.
   - **No approval workflow, no revision history, no structured reason enum for the override
     text.** The step-2 taxonomy is for the tool's own mechanical exclusions; a human's ad hoc
     override reason is free text by design — forcing it into six SP 800-53B categories would
     misrepresent a project-authored convenience as a standard requirement.
   - Persisted the same way step 1's answers already must be (F-004 issue 4: "persist to the URL,
     at minimum") — a compact `controlId → {added|dropped, note}` map alongside the answer state,
     not a separate storage mechanism.

   Anything past this (accounts, approval, audit trail) is genuinely out of scope for a static
   site and is not re-opened by this ADR — if it's ever needed, that is new work against a real
   backend, not an extension of this record.

Persist answer state (to the URL, at minimum) so a computed baseline — and any later adjustment —
can be shared, revisited, and used as real evidence. F-004 issue 4 names this gap; it becomes
load-bearing here, since the artifact produced is no longer just an answer, it's evidence.

## Consequences

**Makes easy:**
- Composite systems get a real, correct answer instead of forced exclusivity (F-004 issue 1
  resolved) — now that F-002 has settled composition as legitimate, the tool can finally express it.
- The 8-type structure stops being memorised special cases and becomes derivable from a small set
  of orthogonal characteristics, using composition F-005 already proved safe — and, after F-012,
  a genuinely smaller set: sandbox collapses into the sensitivity ladder instead of needing its own
  tick-box and its own composition rule.
- The output starts looking like a draft SSP with justifications — F-007's highest-value, cheapest
  recommendation, and presentation-only for the in-profile half.
- The resolution table makes three previously-unstated conflict cases explicit (on-premises +
  cloud rung, sandbox + CII, overlay ceiling vs. ticked rung) instead of leaving them to be
  discovered as bugs during implementation.

**Makes hard:**
- The wizard needs a genuinely different interaction model (tick-all-that-apply), not a copy-edit
  of the existing linear `TREE` — and, per the resolution table, hosting must be modelled as one
  ordered four-rung characteristic plus a separate on-premises/cloud choice, not four independent
  tick-boxes.
- Exclusion-reason text doesn't exist anywhere upstream and must be authored per control or per
  domain — real content work, not something `corpus-ingest` can pull from a scrape. The taxonomy is
  specified now (six SP 800-53B categories, explicitly marked as borrowed, not SSP-sourced), but
  applying it control-by-control is still undone.
- The minimal tailoring record (step 3) still needs new data model and persistence — smaller than
  originally left open, but not free: `controlId → {added|dropped, note}` has to be designed
  alongside step 1's answer-state persistence, not bolted on after.

**Forecloses:**
- A wizard that returns one clean type name with a one-line breadcrumb (today's UX) stops being the
  target end state; future wizard work should not keep optimising that shape.
- Treating `profiles.json` as immutable per-type truth with no per-control justification becomes a
  temporary state, not the destination — the pending statement/recommendations/risk split (F-008)
  should leave room for a justification field if it's revisited.
- Presenting `sandbox` as a peer of the other 7 system types (today's UX, and the wizard's q4)
  stops being accurate framing after F-012; future site copy should describe it as the lowest
  sensitivity rung, not a separate track.
- Treating a `scoped-out:*` status as interchangeable with `not-in-profile` — they must stay
  visually and semantically distinct, since one is a human judgement call and the other is
  mechanical output.

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
