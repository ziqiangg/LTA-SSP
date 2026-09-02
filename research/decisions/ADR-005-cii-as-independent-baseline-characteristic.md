---
id: ADR-005
title: CII designation is its own baseline characteristic, not folded into the sensitivity rung
date: 2026-09-02
status: accepted
findings: [F-004, F-005, F-010, F-012]
---

## Context

RQ-2 required reclassifying F-004's issues 3 and 5 against the tick-all-that-apply wizard shipped
under ADR-001 (2026-09-02), since both were originally diagnosed against the retired 7-question
tree. Issue 3: the old q5 compounded two independent facts — CII designation and
sensitivity-plus-hosting — into one yes/no, so a user who was CII but on-premises, or
Sensitive-High but unsure of CII, had no correct answer.

Direct inspection of the shipped wizard and `docs/assets/data/system-types.json` found the new
wizard has no separate CII question either. CII text appears in exactly two places:
`wizard.js`'s `TYPE_NAMES["high-risk-cloud"]` display string ("High-Risk Cloud CII") and the
"High / CII" rung's hardcoded hint ("Confidential, Sensitive High, and Critical Information
Infrastructure."). Neither is backed by the corpus itself: `medium-risk-cloud` and
`high-risk-cloud` have **byte-for-byte identical `classificationText`** — the sensitivity band
does not distinguish them at all. The corpus's only signals that they differ are the `name` field
("High-Risk Cloud CII" vs. "Medium-Risk Cloud") and the control content itself (F-005: high adds
20 more controls than medium, and escalates 38 more from low to medium). CII designation, not
sensitivity, is what actually separates these two profiles — the wizard's "High / CII" checkbox
was welding a fact the data doesn't even assert (CII, in `high-risk-cloud`'s own
`classificationText`) onto a fact it does (the shared sensitivity band), and offering no way to
answer them independently.

F-010 (blind eval pilot) found CII designation stated in 0 of 15 realistic system descriptions —
it is an administrative determination, not something a text description reliably carries. An
"unsure" response to a CII question is therefore the common case a real user will produce, not an
edge case to handle apologetically.

## Decision

CII designation becomes its own independent signal in the baseline-resolution model, alongside
the four characteristics ADR-001 already defines (hosting location, cloud sensitivity rung, GenAI
overlay, digital-service overlay) — a fifth, **[ours]**, orthogonal to the sensitivity ladder:

| characteristic | values | shape | composition | provenance |
|---|---|---|---|---|
| CII designation | not-CII / CII-designated / unanswered | tri-state (two radio ticks; neither ticked is a legitimate third state) | on the "Confidential, Sensitive High" band: not-CII → `medium-risk-cloud`; CII-designated → `high-risk-cloud`; unanswered → both, unioned, with a disclosed advisory note | **[ours]** — no upstream field distinguishes medium/high by sensitivity; CII designation is the actual differentiator (F-005) |

The cloud sensitivity ladder collapses from four ticks to three: `sandbox` < `low` <
`Confidential, Sensitive High` (merging the old `medium`/`high` rungs, since their
`classificationText` is identical). CII designation is asked as a separate, conditionally-shown
question once that top band is ticked, not bundled into it.

Unanswered CII on a ticked sensitivity band **hedges by composing both `medium-risk-cloud` and
`high-risk-cloud`**, disclosed via an advisory note — not a forced third click, and not a silent
default to one side. This is the same "tick several if unsure" idiom ADR-001 already established
for the sensitivity ladder itself, applied to CII.

The existing F-012 sandbox-conflict check (no upstream-defined "CII sandbox" profile) now fires
against the *resolved* type list rather than a raw tick — meaning it also catches the
unanswered-CII hedge case, which the pre-ADR-005 wizard did not: previously the block only
triggered if a user explicitly ticked a separate "High" box, silently missing the equivalent case
where an unanswered CII implicitly composed `high-risk-cloud` in. This is a correctness fix, not
just a rename.

## Consequences

**Makes easy:**
- A Confidential/Sensitive-High system with unknown CII status gets an honest, disclosed answer
  (both profiles composed) instead of a bundled checkbox forcing a guess.
- The sandbox+CII conflict check now catches every path that resolves to `high-risk-cloud`,
  including the hedge, closing a gap the previous "High" tick-based check had.

**Makes hard / forecloses:**
- Treating "High / CII" as a single tick is no longer accurate framing — future wizard copy or
  site pages describing the sensitivity ladder should describe it as three bands plus a separate
  CII question, not four ordered rungs.
- The wizard now depends on `wizard.js` fetching `system-types.json` at runtime (see the
  companion issue-5 fix, same session) to source the shared band's `classificationText` live —
  this ADR doesn't itself decide that dependency, but its resolution model assumes it.

## Alternatives considered

- **Keep the single "High/CII" rung, rewrite its copy to make the "tick both Medium and High if
  unsure" escape hatch explicit.** Considered and not chosen — it documents the ambiguity but
  doesn't structurally decouple sensitivity from CII, and leaves the "High/CII" label asserting a
  fact (CII) that the corpus's own `classificationText` for that type doesn't state.
- **Add CII as a required question before any composed answer is shown.** Rejected — F-010 shows
  most real users cannot answer it, and forcing an answer would block the majority case rather
  than handle it.
