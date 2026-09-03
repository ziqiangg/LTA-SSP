# RQ-6 baseline results: rule-based wizard + majority-class floor

> **Historical snapshot — scores the pre-ADR-007 wizard.** This run's F-013 finding (the
> majority-class floor beating the rule-based baseline, traced to the hosting question having no
> "unsure" hedge) motivated [ADR-007](../../../decisions/ADR-007-hosting-unknown-hedges-with-on-premises.md),
> which fixed that gap the same day. See the
> [post-fix re-run](wizard-baseline-2026-09-03-adr007.md) for current numbers — Top-3 accuracy
> moves from 40% to 80%. Kept here unedited as the "before" baseline the fix is a documented delta
> against.

**Method:** rule-based wizard baseline (`docs/assets/js/wizard.js`'s `resolve()`, ported to Python)
and the majority-class floor, both scored per
[ADR-006](../../../decisions/ADR-006-rq6-baseline-scoring-methodology.md).
**Configuration:** `wizard.js` @ `d437c00` (2026-09-02, the ADR-005 CII-split version). Scorer:
`research/scripts/score_rq6_baseline.py` (repo @ `cc0d030`). Ticks for each of the 15 cases were
read by hand off `cases-raw.jsonl`'s descriptions, applying the wizard's own question wording
(ADR-006 point 1) — recorded inline in the scorer's `CASES` table with a one-line rationale per
case, not derived by any automated extraction.
**Eval version:** v1, 15 cases, `research/evals/v1/cases.jsonl`.
**Date:** 2026-09-03.

> **v1 validity limitation (`research/evals/README.md`).** These cases are synthetic, written from
> official wording. Absolute accuracy figures below are **not** trustworthy in isolation — only
> the *relative* comparison between the wizard baseline and the majority-class floor, on the same
> 15 cases, is the point of this result.

## Headline

| method | Top-1 | Top-3 |
|---|---|---|
| **Majority-class floor** (always predict `medium-risk-cloud`) | **60.0%** (9/15) | 60.0% (9/15) |
| **Rule-based wizard baseline** | **20.0%** (3/15) | 40.0% (6/15) |

**The majority-class floor beats the rule-based wizard baseline on Top-1, by a wide margin.** This
is not a scorer bug — see Interpretation. It is the headline result RQ-6 exists to produce: a
number the classifier work must clear, and a concrete demonstration of *why* it's a low bar here.

## Wizard baseline: output-bucket breakdown

| bucket | n | meaning |
|---|---|---|
| `incomplete` | 8 / 15 | Nothing resolvable from stated facts — no type offered at all. |
| `ok` (non-hedge or hedge) | 6 / 15 | Resolved to one or more types. 3 of these 6 are hedges/ties. |
| `blocked` | 1 / 15 | Wizard's conflict check fired (EV-013 — see below). |

**8 of 15 cases resolve to `incomplete`, not a wrong guess.** All 8 are `hosting-unknown` cases
where the description also gives the baseline no GenAI or digital-service signal to fall back on.
This is exactly what [ADR-006](../../../decisions/ADR-006-rq6-baseline-scoring-methodology.md)
point 5 anticipated: the sensitivity-rung question only renders once `hosting = "cloud"` is
ticked, so an untouched hosting field forecloses the entire cloud-sensitivity ladder — a
description can state NRIC-grade data plainly and the wizard still can't reach a hosting-tier
answer if it never says where the system runs. This is a **structural finding**, not scoring
noise — filed separately as **F-013**.

## Classification, broken down

**By ambiguity tag** (Top-1 hits / n):

| tag | hits/n | note |
|---|---|---|
| `hosting-unknown` | 1/8 | The one hit is EV-014, which resolves via its GenAI tick alone — hosting was irrelevant to that case's answer. |
| `sensitivity-inferred` | 0/6 | Every one of these needed a hosting-tier answer the wizard couldn't reach. |
| `composite` | 3/6 | The wizard's best-scoring tag — GenAI/digital-service ticks resolve independently of the hosting fork. |
| `cii-undetermined` | 0/2 | Both hedge, so both score Top-1 = miss by design (ADR-006 rule 3). |
| `traffic-unknown` | 1/3 | |
| `nonprod` | 1/2 | Includes EV-013 (blocked, correctly — see below) and EV-014 (hit via GenAI). |
| `wogaa-unknown` | 1/1 | |
| `genai-overlay` | 1/1 | |
| `third-party-managed` | 0/1 | |

**By difficulty:** easy 1/1, medium 0/5, hard 2/9. The pilot's one `easy` case is the only
`medium`-difficulty-or-above case class the baseline does *not* struggle with — consistent with
F-010's difficulty stratification (9 hard, 5 medium, 1 easy) tracking exactly the cases most
dependent on hosting/sensitivity facts realistic descriptions omit.

## Control retrieval

Ground truth per case = union of controls across **all** of that case's `acceptable_answers`
entries (high-water-mark merged); predicted = the actual merged control set `controls.js` would
show for the wizard's real output (full ticks, hedges unioned — not the per-candidate scoring used
for classification above). **This union-of-acceptable-answers ground truth is a methodological
simplification ADR-006 did not fully pin down** — flagged as an open point below, not a silent
choice.

| metric | value | scope |
|---|---|---|
| Precision | 0.961 | the 6 `ok` cases (no prediction ⇒ precision undefined, excluded) |
| Recall | 0.271 | all 15 cases (`incomplete`/`blocked` ⇒ recall = 0, included) |
| F1 | 0.723 | the 6 `ok` cases |
| Level-0 recall | 0.276 | all 15 cases |
| Level-0 recall | 0.689 | the 6 `ok` cases only |

**Precision is high when the baseline commits; recall collapses because it mostly doesn't
commit.** This is the retrieval-side mirror of the classification headline: when the wizard
resolves at all, it's a fairly clean, high-precision recommendation (few false-positive controls);
the 8 `incomplete` and 1 `blocked` cases drag recall down to nearly the majority-floor's own
territory, simply because they retrieve nothing.

## Asymmetric errors (medium vs. high-risk-cloud)

Per ADR-006 point 8, over-serving (predicting high when truth doesn't need it) and under-protecting
(predicting medium when truth needed high) are reported separately, never folded together.

- **Under-protection instances: 0.** No case in this pilot has an `acceptable_answers` set that
  requires `high-risk-cloud` to the exclusion of `medium-risk-cloud` — every case that admits
  `high-risk-cloud` at all also admits `medium-risk-cloud` (EV-006, EV-008). The classic
  asymmetry direction this pilot was designed partly to probe (F-005's nesting concern) **cannot
  be measured on v1 as constructed** — worth naming as a coverage gap for any future eval slice,
  not asserting the baseline is safe in this direction.
- **Over-serving instances: 2** (EV-004, EV-011). Both are cases where a rung tie or CII-hedge
  pulled `high-risk-cloud` into the predicted set even though **no** acceptable answer for that
  case ever includes it. This is the union-as-hedge design (ADR-005's "stay conservative until you
  know," applied by ADR-006's extension to rung ties too) doing exactly what it says — trading
  precision for safety — but it is a real, quantified cost: `high-risk-cloud` adds 20 controls
  over `medium-risk-cloud` (F-005), all shown as recommended when at most one case in the pilot
  ever needed them.

## Notable per-case results

- **EV-013 (the adversarial sandbox-with-live-PII case) correctly `blocked`**, not silently
  resolved to `sandbox`. Ticking the literal environment label (`staging` → sandbox) *and* the
  independently-stated fact (live citizen data → sensitive band) together trip the sandbox+CII
  conflict check ADR-005/F-012 built for exactly this shape of case. This is the single most
  reassuring result in this run: the wizard's refusal-to-resolve design catches its own
  worst-case failure mode rather than defaulting to the lax 3-mandatory-control profile.
- **EV-014 (the GenAI pilot) is the wizard's cleanest hit** — Top-1 correct via the `genai` tick
  alone, entirely independent of its `hosting-unknown` tag. Composable overlays (ADR-001's core
  fix) are carrying real weight here.
- **EV-002 and EV-003, the wizard's other two clean hits**, both have hosting stated outright or a
  digital-service fact strong enough to stand alone — the pattern across all 3 non-hedge hits is
  "at least one axis was unambiguously stated," never a case where the baseline had to guess.

## Calibration (F-007)

Both numbers sit well under F-007's anchors (κ≈0.71–0.76 expert agreement, 44.4 FullCov@10 best
retrieval) — no leaky-eval suspicion here, if anything the opposite: an 8-case `incomplete` rate
suggests this pilot is, if anything, harder on the rule-based method than a realistic population
might be, given F-011's known homogeneity in the `hosting-unknown` slice.

## Open points for a future ADR-006 amendment

1. **Retrieval ground truth under multi-answer labels** was resolved here as "union across all
   acceptable answers," a reasonable but undecided-in-ADR-006 choice — an alternative (e.g. score
   retrieval only against the single acceptable entry closest to the prediction) would give
   different, probably higher, precision/recall numbers. Worth pinning formally before this
   becomes load-bearing for a comparison against a second method.
2. **ADR-006 rule 3 (hedge scoring) was extended here to rung ties** (EV-011's low/sensitive tie),
   not just the CII-unanswered hedge it was written for — both are the wizard unioning candidate
   profiles under stated uncertainty, so the same Top-1-miss/Top-3-hit treatment was applied by
   analogy. Worth folding into ADR-006 explicitly rather than leaving as an implicit extension.
