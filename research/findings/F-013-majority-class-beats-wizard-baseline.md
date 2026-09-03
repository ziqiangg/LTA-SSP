---
id: F-013
title: On the 15-case pilot, always guessing medium-risk-cloud beats the rule-based wizard baseline
date: 2026-09-03
rq: [RQ-6, RQ-2, RQ-3]
implications: [site, classifier]
confidence: medium
status: actioned
---

> **Actioned 2026-09-03, same day.** The site-level implication below — the wizard's
> hosting-gates-sensitivity control flow — is fixed by
> [ADR-007](../decisions/ADR-007-hosting-unknown-hedges-with-on-premises.md): the sensitivity
> question is now reachable with hosting left blank, hedging with `low-risk-on-premises` when it
> is. Re-scored: Top-3 accuracy moves from 40% to **80%**, clearing the 60% majority-class floor —
> see `research/evals/v1/results/wizard-baseline-2026-09-03-adr007.md`. `status` moves to
> `actioned`. Not fully closed: the over-serving cost flagged below is *larger* post-fix (2 → 6
> instances, since the CII sub-hedge now stacks with the new hosting hedge on 4 more cases) — a
> known, disclosed tradeoff per ADR-007, not a defect, but worth citing accurately if this finding
> is referenced again. The classifier-track numbers this finding sets (majority-class floor is the
> bar) are unchanged by the site fix.

## Observation

Scoring the current `wizard.js` logic (tick-all-that-apply, CII independent per ADR-005) and the
majority-class floor against the 15-case pilot, per
[ADR-006](../decisions/ADR-006-rq6-baseline-scoring-methodology.md) — full run in
`research/evals/v1/results/wizard-baseline-2026-09-03.md`:

| method | Top-1 | Top-3 |
|---|---|---|
| Majority-class floor (always `medium-risk-cloud`) | 60.0% (9/15) | 60.0% (9/15) |
| Rule-based wizard baseline | 20.0% (3/15) | 40.0% (6/15) |

The wizard baseline resolves to `incomplete` — no type at all — on **8 of 15 cases**, all tagged
`hosting-unknown`. Ticks were read by hand off each case's description (`ADR-006` point 1); the
`incomplete` outcome traces to a specific mechanism, not a labelling shortfall: `wizard.js`'s
cloud-sensitivity-rung fieldset only renders once `hosting = "cloud"` is ticked
(`docs/assets/js/wizard.js:283-305`), and `resolve()` returns `{incomplete: true}` immediately if
`hosting = "cloud"` is ticked with no rung, or resolves via GenAI/digital-service alone if hosting
is never touched at all. Either way, **a description can state Confidential-grade data in plain
language and the wizard still cannot reach a hosting-tier answer unless hosting is also stated** —
sensitivity is gated behind hosting, not asked independently.

Two cases (EV-004, EV-011) also show `high-risk-cloud`'s 20 extra controls (F-005) pulled into the
predicted set via the CII-hedge/rung-tie union mechanism (ADR-005, extended to rung ties by
ADR-006), even though no acceptable answer for either case ever includes `high-risk-cloud`.

## Evidence

- `research/scripts/score_rq6_baseline.py` (repo @ `cc0d030`), scoring `wizard.js` @ `d437c00`
  against `research/evals/v1/cases.jsonl`.
- `research/evals/v1/results/wizard-baseline-2026-09-03.md` — full per-case breakdown, retrieval
  metrics, ambiguity/difficulty tables.
- `docs/assets/js/wizard.js:100-148` (`resolve()`), `:283-337` (conditional rung/CII fieldsets).
- F-010 (0/15 cases state sensitivity, 8/15 state hosting) supplies the input-side cause; this
  finding supplies the output-side consequence once that input reality meets the wizard's actual
  control flow.

## Interpretation

**This is not a scorer bug or an unlucky pilot.** F-010 already established that hosting is the
single most commonly-missing fact in realistic descriptions. This finding shows the specific
mechanical consequence: because the wizard's UI only exposes the sensitivity question *after*
hosting is answered, "hosting unknown" doesn't just leave one axis blank — it forecloses the axis
that would otherwise let a GenAI-less, non-public system resolve at all. The majority-class floor
wins here largely because `medium-risk-cloud` happens to be the more common half of the
`hosting-unknown` fork in this pilot's own construction (F-011 already flags 6/15 cases sharing
one identical hosting-unknown answer pair) — so the floor's apparent strength is itself partly an
artifact of the pilot's homogeneity, not evidence the floor would generalize this well.

**The two over-serving cases point at a real, quantifiable cost of the hedge-as-union design.**
ADR-005 chose to union both `medium-risk-cloud` and `high-risk-cloud` when CII is unanswered
("stay conservative until you know") rather than force a guess. That is defensible as UI behavior
— under-protection is worse than over-serving — but it means every unresolved-CII case pays 20
extra controls' worth of noise, and in this pilot that noise was never actually warranted by any
acceptable reading in 2 of the (small number of) cases where it fired.

## Implications

- **site:** The wizard's control-flow dependency — sensitivity reachable only through
  `hosting = "cloud"` — is worth reconsidering independently of RQ-2's five already-closed issues.
  A user who knows their data is Confidential/Sensitive High but not where it's hosted currently
  gets *nothing* from the wizard, when the sensitivity fact alone is informative. Not filed as a
  wizard defect requiring an immediate fix — F-004's five issues are all closed, and this is a
  sixth, newly-surfaced one — but worth an RQ-2-style classification (`fixable in the tick model` /
  `needs a different interaction model`) before the next wizard iteration.
- **classifier:** 20% Top-1 / 40% Top-3 is now the concrete number a semantic or LLM method must
  clear on v1 — and 60% is the number that actually matters, since majority-class is the naive
  floor. A method that beats the wizard baseline but not the majority-class floor has not yet
  earned a claim of usefulness.
- **classifier:** The over-serving cases are a concrete instance of a cost RQ-3's feature inventory
  should account for: a feature schema that treats CII/sensitivity as "ask and hedge if unknown"
  inherits this same over-serving cost unless it does something smarter than uniform unioning.

## Open questions

- Would a larger, less homogeneous case set (F-011's concern) narrow or widen the gap between the
  majority-class floor and the wizard baseline? Scaling is deferred (owner decision, 2026-09-02),
  so this isn't answerable on v1.
- Should the wizard ask sensitivity as an unconditional question (independent of hosting), with
  hosting resolved separately, rather than gating one behind the other? This would recover a
  partial answer for exactly the `hosting-unknown`-but-sensitivity-known cases this finding
  identifies — worth a concrete mockup before an ADR, not asserted here as the right fix.
- The two open methodological points flagged in the results file (retrieval ground truth under
  multi-answer labels; the rung-tie extension of ADR-006 rule 3) should be resolved before this
  result is used as the fixed comparison point for a second method.
