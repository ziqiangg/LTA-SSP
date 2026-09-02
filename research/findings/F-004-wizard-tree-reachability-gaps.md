---
id: F-004
title: The wizard tree has unreachable outcomes and forced answers
date: 2026-09-01
rq: [RQ-2, RQ-3]
implications: [site, classifier]
confidence: high
status: actioned
---

> **Issues 1, 2 and 4 resolved 2026-09-02** by the ADR-001 tick-all-that-apply rewrite
> (`docs/assets/js/wizard.js`): composite systems compose, on-premises's single-profile limit is
> disclosed rather than silently forced, and answer state persists to the URL.
>
> **Issues 3 and 5 reclassified against the new model and resolved 2026-09-02 —
> [ADR-005](../decisions/ADR-005-cii-as-independent-baseline-characteristic.md).** The new wizard
> had re-introduced issue 3 in a new shape — CII designation was still welded to the top
> sensitivity rung's "High / CII" checkbox, asserting a fact (`high-risk-cloud`'s own
> `classificationText` never mentions CII) the corpus itself doesn't state for that type. ADR-005
> splits CII into its own tri-state question (not-CII / CII-designated / unanswered-hedges), and
> merges the old `medium`/`high` rungs into one sensitivity band, since their `classificationText`
> is identical and only CII distinguishes them. Issue 5 (question text duplicated, not derived) is
> resolved by `wizard.js` now fetching `system-types.json` at runtime and sourcing every rung/
> overlay hint from `classificationText` directly — see `docs/CLAUDE.md`'s updated Structure note.
> All five issues now have a final classification; **RQ-2 → answered.**

## Observation

`docs/assets/js/wizard.js` defines `TREE`, a 7-node decision tree with a single terminal outcome
per path. Traced in order:

| node | question | branches |
|---|---|---|
| q1 | public-facing digital service tracked under WOGAA, not internal/back-office? | yes → q2, no → q3 |
| q2 | ≥1,000,000 visits/year? | yes → `digital-services-high-impact`, no → `digital-services-others` |
| q3 | GenAI as a core function? | yes → `generative-ai`, no → q4 |
| q4 | sandbox / non-production pilot only? | yes → `sandbox`, no → q5 |
| q5 | CII, or Confidential/Sensitive High **and** cloud-hosted? | yes → `high-risk-cloud`, no → q6 |
| q6 | on-premises or cloud? | on-prem → `low-risk-on-premises`, cloud → q7 |
| q7 | sensitivity level? | Low → `low-risk-cloud`, Medium → `medium-risk-cloud` |

Structural consequences that follow directly from this shape:

1. **Composite systems are unreachable.** q1 and q3 are mutually exclusive branches, so a
   GenAI-powered public digital service can only ever return one of the two. Given F-002 — the
   GenAI profile is an overlay of 9 controls with no hosting baseline — the GenAI branch is the
   more damaging of the two answers to land on.
2. **On-premises systems never reach a sensitivity question.** q6 terminates on-prem immediately.
   Any on-prem system, at any sensitivity, gets `low-risk-on-premises`. The result screen carries
   a `RESULT_NOTES` caveat admitting this, but the routing is still forced — the standard defines
   only one on-prem profile.
3. **q5 compounds two independent facts** — CII designation and sensitivity-plus-hosting — into
   one yes/no. A user who is CII but on-premises, or Sensitive High but unsure about CII, has no
   correct answer to give.
4. **Every outcome is single and unranked.** There is no "probably X, possibly Y", and no
   confidence. `history` is discarded on completion and never persisted to the URL, so a result
   cannot be shared or revisited.
5. **Question text is duplicated, not derived.** The thresholds and criteria are hardcoded here
   while `classificationText` in `system-types.json` states them independently. Two sources, no
   link — they can drift.

## Evidence

- `docs/assets/js/wizard.js:22-72` (`TREE`), `:15-20` (`RESULT_NOTES`)
- F-002 (GenAI profile is an overlay)
- F-005 (medium/high nesting, and the identical sensitivity wording behind q5)
- repo @ `4e7e6ba`
- **EV-006** (`research/evals/v1/cases.jsonl`), spot-checked 2026-09-01
  (`research/evals/v1/spot-check-2026-09-01.md`): a concrete synthetic case demonstrating issue 3 —
  an analytics warehouse with untokenised NRIC is Confidential/Sensitive-High and cloud-hosted, so
  q5's literal text routes it toward `high-risk-cloud`, but it is not CII, which is what that
  profile is actually for. Both `medium-risk-cloud` and `high-risk-cloud` are defensible answers to
  the same description — the compounding predicted structurally is reproducible from a single
  example.

## Interpretation

These are not bugs in the tree; they are the tree's expressive limits. A single-outcome decision
tree cannot represent composition (issue 1), cannot degrade gracefully when the standard itself
offers only one option (issue 2), and cannot express uncertainty (issue 4). Issues 3 and 5 are
fixable within the current model; 1, 2 and 4 are not.

Issue 2 is worth separating from the rest: it is **blocked upstream**. The standard publishes one
on-premises profile, so no interaction model fixes it — only clearer disclosure can.

## Implications

- **site:** The cheapest real improvements are (a) splitting q5 into two questions, (b) persisting
  wizard state to the query string so results are shareable, and (c) deriving question text from
  `classificationText` rather than duplicating it. Composition and ranking need a different
  interaction model, not a bigger tree.
- **classifier:** The 7 questions are effectively a feature inventory for RQ-3 — WOGAA-tracked,
  annual traffic, GenAI core function, production status, CII designation, hosting location,
  sensitivity level. Note that at least two (CII designation, WOGAA tracking) are **administrative
  facts not inferable from a system description**, which puts a hard ceiling on any text-only
  classifier. Output should be `(base_type, overlays[], confidence)`, not a single label.
- This tree, mechanically applied, is the **baseline** RQ-6 must score first.

## Open questions

- How often, in practice, is a system both a digital service and GenAI-powered?
- Can CII status be inferred at all from prose, or must it always be asked?
