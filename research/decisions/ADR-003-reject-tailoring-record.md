---
id: ADR-003
title: Reject the tailoring record — no per-control human override of the computed baseline
date: 2026-09-02
status: accepted
findings: []
---

## Context

ADR-001's Decision item 3 specified a "minimal tailoring record": per control, at most one human
override — `added` (include despite `not-in-profile`) or `dropped` (exclude despite `in-profile`)
— plus one free-text note, persisted alongside step 1's answer state in the URL. It was explicitly
scoped down from an earlier, fully open-ended adjustment engine, on the reasoning that the site
needed only enough to render a draft SSP page with justifications, not a general override system.

Re-reading ADR-001 while picking up the next slice of work surfaced an internal tension between its
own steps. Step 2 defines six `scoped-out:*` statuses (`applicability`, `operational`,
`technology`, `mission`, `objective`, `legal`, borrowed from SP 800-53B §2.4) and states they
"only ever apply to a control that is `in-profile` — they are a *human* override of a mechanical
inclusion", applied via step 3. But step 3's own text says the opposite for the override reason
itself: "no structured reason enum for the override text... forcing it into six SP 800-53B
categories would misrepresent a project-authored convenience as a standard requirement." Step 2
frames `scoped-out:*` as the vocabulary step 3 produces; step 3 forbids step 3 from producing a
structured vocabulary at all. ADR-001 never reconciled this — it was left for implementation to
resolve one way or the other.

That inspection was the occasion for revisiting step 3, but not the reason for rejecting it. On
review, the actual answer is simpler: **the site has no requirement for letting a user review and
customize the controls the tool has automatically selected.** Step 1 (tick-all-that-apply baseline)
and step 2 (every control rendered with a mechanical status and reason) already ship the whole of
what the site needs to do — compute a baseline and show it honestly. A per-control override/notes
feature was speculative scope, not a stated user need, and resolving its internal tension (free
text vs. a six-category enum) isn't worth doing for a feature nothing requires.

## Decision

Reject ADR-001's Decision item 3 (the minimal tailoring record) in full.

No per-control override UI will be built. No `added`/`dropped` state, no free-text note capture,
and no `scoped-out:*` categorization will be implemented anywhere in `docs/`. ADR-001's steps 1
and 2 remain accepted and stand exactly as implemented 2026-09-02 — this decision touches only
item 3.

The six `scoped-out:*` values defined in ADR-001 step 2 stay in that document as a documented
design reference (evidence that a status/reason vocabulary for human overrides was considered and
where it came from) but are never instantiated in code or data. No control anywhere is ever
pre-labelled or hand-labelled `scoped-out:*` — every control renders with only the mechanical
`in-profile`/`not-in-profile` status step 2 already produces.

## Consequences

**Makes easy:**
- `wizard.js` and `controls.js` stay exactly as shipped 2026-09-02 — no new state shape, no new
  URL-persistence format, no new per-control UI affordance to design, build, or maintain.
- Removes an unresolved design question (free-text-only vs. optional category picker for a
  "dropped" override) that had no clean answer inside ADR-001's own text.

**Makes hard / forecloses:**
- A user cannot record, on the site, *why* they personally added or dropped a specific control
  from the computed baseline. F-004 issue 4's "a result should be shareable, revisable, citable"
  goal is now satisfied only at the baseline-answer level (already URL-persisted by step 1) — not
  for any subsequent human adjustment to that baseline.
- If a real need for per-control justification emerges later (e.g. from real user feedback, not
  speculation), that is new work requiring its own ADR — this decision is not a deferral, and
  should not be treated as "step 3, later."

## Alternatives considered

- **Build step 3 exactly as ADR-001 specified.** Rejected — no site requirement motivates it, and
  building it would leave the `scoped-out:*` enum-vs-free-text tension to be resolved by
  implementation instead of by decision.
- **Build a smaller version — free-text note only, no `added`/`dropped` status, no `scoped-out:*`
  vocabulary at all.** Rejected — still speculative scope solving a need the site doesn't have;
  scoping it down further doesn't change that it's unrequested.
