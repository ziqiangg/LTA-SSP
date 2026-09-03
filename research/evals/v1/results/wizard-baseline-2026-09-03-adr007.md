# RQ-6 baseline results, re-run after ADR-007 (hosting-unknown hedge)

**Method:** rule-based wizard baseline (`docs/assets/js/wizard.js`'s `resolve()`, ported to
Python) and the majority-class floor, both scored per
[ADR-006](../../../decisions/ADR-006-rq6-baseline-scoring-methodology.md), re-run after
[ADR-007](../../../decisions/ADR-007-hosting-unknown-hedges-with-on-premises.md) fixed the
hosting-question gap [F-013](../../../findings/F-013-majority-class-beats-wizard-baseline.md)
identified in the [2026-09-03 pre-fix run](wizard-baseline-2026-09-03.md).
**Configuration:** `wizard.js` post-ADR-007 (same day). Scorer:
`research/scripts/score_rq6_baseline.py`, updated for the new `resolve()` branching; ticks for
EV-001/005/007/009/010/015 re-derived by hand against the newly-reachable sensitivity-rung
question (ADR-006 point 1) — the other 9 cases' ticks are unchanged from the pre-fix run.
**Eval version:** v1, 15 cases, `research/evals/v1/cases.jsonl`.
**Date:** 2026-09-03.

> **v1 validity limitation** applies here exactly as it did in the pre-fix run — see that file.

## Headline: delta against both the pre-fix baseline and the majority-class floor

| method | Top-1 | Top-3 |
|---|---|---|
| Majority-class floor | 60.0% (9/15) | 60.0% (9/15) |
| Wizard baseline — **pre-ADR-007** | 20.0% (3/15) | 40.0% (6/15) |
| Wizard baseline — **post-ADR-007** | 20.0% (3/15) | **80.0% (12/15)** |

**The wizard now clears the majority-class floor on Top-3, by a wide margin — the exact reversal
of the pre-fix result.** Top-1 is unchanged: every newly-resolved case is a hedge (composing
multiple candidate types under disclosed uncertainty), and per ADR-006 rule 3 a hedge never counts
as Top-1 correct by design — that rule hasn't changed, and shouldn't: the wizard still isn't
*committing* to one answer for these cases, it's now just offering the right small set instead of
nothing.

## Bucket breakdown, before vs. after

| bucket | pre-ADR-007 | post-ADR-007 |
|---|---|---|
| `incomplete` | 8 | **2** (EV-008, EV-012 — both correctly still unresolved, see below) |
| `ok` (incl. hedges) | 6 | **12** |
| `blocked` | 1 | 1 (EV-013, unchanged — see the pre-fix write-up) |

Only **EV-008** and **EV-012** remain `incomplete`, and both correctly so: EV-008's description
gives no sensitivity signal at all ("some platform the vendor runs — I honestly couldn't tell you
the architecture"), and EV-012's traffic ambiguity is a separate, still-unaddressed gap (the
digital-service radio still has no "unsure" affordance — out of scope for ADR-007, which only
touched the hosting/sensitivity axis). The fix resolved exactly the cases it targeted and nothing
it didn't have a textual basis for.

## Control retrieval, before vs. after

| metric | pre-ADR-007 | post-ADR-007 |
|---|---|---|
| Precision (resolvable cases) | 0.961 (n=6) | 0.940 (n=12) |
| Recall (all 15) | 0.271 | **0.671** |
| F1 (resolvable cases) | 0.723 (n=6) | **0.840** (n=12) |
| Level-0 recall (all 15) | 0.276 | **0.676** |

Recall and Level-0 recall roughly 2.5x. Precision dips slightly (0.961 → 0.940) — the mechanism is
visible in the per-case data: EV-001/005/009/015 all now pull in `high-risk-cloud`'s extra 20
controls via the CII sub-hedge stacked on top of the new hosting hedge, even though none of the
four cases' acceptable answers need `high-risk-cloud`. This is the **same over-serving cost**
flagged in the pre-fix write-up (there: 2 instances, EV-004/EV-011) — now **6 instances**
(adding EV-001/005/009/015), since the hosting hedge and the CII hedge compound whenever both fire
together. Still no under-protection instances in this pilot (no case ever requires
`high-risk-cloud` to the exclusion of `medium-risk-cloud`) — that direction remains unmeasurable
on v1, as before.

## Notable per-case changes

- **EV-007, EV-010** (the two `low`-sensitivity, hosting-unknown cases): now resolve to exactly
  `{low-risk-cloud, low-risk-on-premises}` — a clean 2-way hedge with **no** CII sub-hedge (the
  `low` rung doesn't reach the CII question), so precision and recall both hit 1.00. These are the
  cleanest wins from the fix — no compounding-uncertainty cost, because there was only one axis of
  uncertainty to begin with.
- **EV-001/005/009/015** (the four `sensitive`-band, hosting-unknown cases): now resolve to a
  3-way composed set (`medium-risk-cloud` + `high-risk-cloud` + `low-risk-on-premises`), correctly
  Top-3 hitting on two of the three candidates but paying the over-serving cost above. This is
  exactly ADR-007's Consequences section anticipating "a wider, more conservative answer set" —
  observed, not hypothetical.
- **EV-013** (blocked) and **EV-014** (GenAI hit) are unaffected, as expected — neither touches the
  hosting/sensitivity axis this fix changed.

## Calibration (F-007)

Top-3 (80%) is now closer to F-007's expert-agreement ceiling (κ≈0.71–0.76, roughly comparable in
spirit though not the same metric) than to the floor. Worth treating as a signal to look harder
for eval leakage before citing this uncritically, rather than a pure celebration — though the
mechanism (a specific, auditable code change resolving a specific, auditable prior gap) is
unusually well-understood for a jump this size, which is reassuring compared to an unexplained
score increase.

## Open points carried over, still unresolved

Both open points from the pre-fix write-up still apply and are unaffected by this fix:
1. Retrieval ground truth under multi-answer labels (union-of-acceptable-answers) is still a
   methodological simplification, not formally pinned in ADR-006.
2. ADR-006 rule 3's hedge-scoring treatment is now doing more work than it originally described —
   it's being applied to a 3-way hosting×CII cartesian-product hedge (EV-001/005/009/015), not
   just the simple 2-way CII hedge it was written for. Worth folding into a future ADR-006
   amendment alongside the rung-tie extension already flagged in the pre-fix write-up.
