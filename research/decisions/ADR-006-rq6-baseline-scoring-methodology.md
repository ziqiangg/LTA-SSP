---
id: ADR-006
title: RQ-6 baseline scoring methodology
date: 2026-09-03
status: accepted
findings: [F-004, F-007, F-010, F-011, F-012]
---

> **Amended 2026-09-03, same day, by ADR-007.** The first scoring run (F-013, results dated
> 2026-09-03) surfaced a real wizard gap — hosting had no "unsure" hedge affordance, unlike CII
> and the sensitivity rung — which ADR-007 fixed. Point 2's `resolve()` branching summary below is
> now stale (it describes `wizard.js` @ `d437c00`, pre-fix); re-derive it against the current
> `wizard.js` before citing this ADR's point 2 as the baseline definition, and re-run the scorer
> per ADR-007's Consequences. Points 1 and 3–9 (scope boundary, hedge/blocked scoring rules,
> majority-class definition, metrics, logging format) are unaffected by the fix and still apply as
> written.

## Context

RQ-6 (`research/QUESTIONS.md`) requires a rule-based baseline — "today's wizard tree, mechanically
applied" — scored against the 15-case pilot in `research/evals/v1/cases.jsonl` before any
semantic or LLM approach can be evaluated meaningfully. Two problems surfaced while preparing to
run it, both worth settling before anyone writes a scorer:

**The baseline model changed twice since RQ-6 was framed, and the docs describing it went stale.**
`wizard.js` was a single-outcome 7-question tree when F-004 diagnosed it (2026-09-01). ADR-001
rewrote it to a tick-all-that-apply, high-water-mark-composed form (2026-09-02); ADR-005 then
split CII designation into its own tri-state question (2026-09-02). The `eval-set` skill and
`research/evals/README.md` — which define what RQ-6's baseline *is* — still described the retired
tree as current until this pass. That staleness is fixed alongside this ADR (see `JOURNAL.md`);
this ADR exists so the fix doesn't just restate a description that will drift the next time the
wizard changes.

**"Mechanically applied" leaves real judgment calls unresolved.** The current `resolve()`
(`docs/assets/js/wizard.js:96-148`) is not a simple tree walk — it composes independent ticks, can
return more than one type at once (an explicit hedge when CII is unanswered), can refuse to answer
(the two hard blocks: on-premises+cloud-rung, sandbox+high-CII), and can also legitimately return
nothing (`{incomplete: true}`) under two different conditions that don't mean the same thing. None
of `eval-set`, `evals/README.md`, F-010, or F-011 says how to score any of that. Left implicit,
these get decided ad hoc mid-implementation — exactly what this repo's ADR convention exists to
prevent for decisions that bind the future classifier's comparison baseline.

F-010 supplies the eval-side reality this baseline gets scored against: 15/15 pilot cases admit
more than one acceptable answer, 5/15 need a compound answer, and 7/15 never state hosting at all
— the single most common condition in the set. F-011 adds that 6 of those 7 share one identical
answer pair, a homogeneity risk this ADR does not attempt to fix (that's the deferred
scaling question). F-012 establishes that `sandbox` is a ladder rung, not an orthogonal flag —
relevant because the baseline's missing-field handling (below) depends on knowing which ticks are
independent of which others.

## Decision

**1. Scope: ticks are read by a human, not extracted by a rule-based parser.** RQ-3 (open) is
where automatic text→feature extraction gets evaluated, and its "answered when" bar explicitly
says signal reliability must be measured *against RQ-6's eval*. RQ-6 must not presuppose an answer
to RQ-3. Concretely: for each of the 15 cases, a human reads the description and ticks the wizard's
own fields (`hosting`, `rungs`, `cii`, `genai`, `ds`) exactly as rigorously as the case was
originally labelled — never leaving a field un-ticked because it *could* be inferred with more
effort, but never inferring a fact the text doesn't state either. Only the *decision logic* — what
`resolve()` does with those ticks — needs to be mechanical and deterministic. Building an NLP
extraction layer is out of scope for RQ-6; if someone builds one, that's an RQ-3 method being
evaluated, not the RQ-6 baseline.

**2. Baseline = `wizard.js`'s `resolve()` as of this ADR's date, version-pinned.** The branching,
summarized for a scorer:

- `hosting = "on-premises"` + any rung ticked → **blocked**.
- `hosting = "on-premises"`, no rungs → `low-risk-on-premises`.
- `hosting = "cloud"`, no rung ticked → **incomplete, full stop** — this is an early return in
  `resolve()` (line 111) that happens *before* GenAI/digital-service are even considered. Ticking
  "cloud" without a rung is not the same as never touching hosting at all (point 5).
- `hosting = "cloud"` + rungs → `sandbox`/`low-risk-cloud` per rung ticked, `sensitive` resolved
  via CII (point 3); sandbox + a CII-yes-or-hedge resolution reaching `high-risk-cloud` →
  **blocked**.
- `genai` ticked → appends `generative-ai`, composable with anything above.
- `ds` ticked → appends `digital-services-others` or `digital-services-high-impact`, composable.
- Nothing resolves at all → **incomplete**.

If `wizard.js` changes again, this baseline is stale and RQ-6 must be re-run before any result
citing it is trusted — the same failure mode the stale-doc sweep accompanying this ADR just fixed,
now an explicit, checkable condition instead of a silent one. A results file (point 9) must record
the commit `wizard.js` was read at.

**3. The CII hedge never counts as Top-1 correct, but does count for Top-3.** When `cii` is
unanswered on a ticked `sensitive` rung, `resolve()` deliberately returns both
`medium-risk-cloud` and `high-risk-cloud` rather than committing (`wizard.js:126-131`). Scoring
this as an automatic Top-1 hit whenever either alternative is in `acceptable_answers` would reward
the wizard for declining to decide. Score it as a Top-1 miss, a Top-3 hit if either alternative is
acceptable, and log it in a distinct "hedged" bucket — expected to correlate heavily with the
`cii-undetermined` and `hosting-unknown` ambiguity tags, and not folded into "the baseline got it
wrong."

**4. A blocked output is a refusal, not a wrong recommendation.** Score as a miss (it offers no
type to compare against `acceptable_answers`), but tag it distinctly from a wrong-type prediction
in the write-up. "Correctly detected an incoherent combination" and "guessed wrong" are different
findings and must not be merged into one error count.

**5. Missing-field cases: distinguish "field genuinely absent from the text" from "field ticked
empty."** Per point 2, ticking `hosting = "cloud"` with no rung is an immediate `incomplete`
regardless of GenAI/digital-service — but a case whose text never mentions hosting at all should
leave `hosting = ""`, under which GenAI/digital-service still resolve independently if the text
supports them (`resolve()` falls through the empty `if`/`else if` on hosting straight to the
genai/ds checks). Given 7/15 pilot cases are `hosting-unknown`, expect the baseline to abstain on
the hosting axis for close to half the set. State this plainly in the results write-up as an
expected outcome that reflects the standard's structure (single on-prem profile, F-004/F-012), not
a modeling failure — and flag that the majority-class floor may look artificially competitive
against the baseline for exactly this reason.

**6. Majority-class floor = the most common single entry in `acceptable_answers` across the 15
cases**, not the most common individual type id. An entry is a whole answer (possibly compound,
e.g. `["generative-ai", "medium-risk-cloud"]`); counting individual ids would double-count compound
answers and score predictions inconsistently with how the baseline itself is scored (whole
answer-sets, not token sets).

**7. Classification and control retrieval stay two separate, linked tasks** — carried forward from
the `eval-set` skill as the canonical metric set, not left only there: **Top-1/Top-3 accuracy**,
**per-class recall + confusion matrix**, both broken down by `ambiguity` tag and `difficulty`, for
classification; **precision/recall/F1** with **Level-0 recall reported separately** (a missed
mandatory control is not the same class of error as a missed optional one) for retrieval, derived
via the `profiles.json` join once a type prediction exists.

**8. Asymmetric errors reported as two separate counts, never folded into one** —
high-predicted-when-medium-true (over-serves) and medium-predicted-when-high-true
(under-protects) are different failure modes with different costs and must not collapse into a
single "adjacent-tier error" number.

**9. Results go in `research/evals/v1/results/<method>-<date>.md`**, recording method,
configuration (including the `wizard.js` commit for the rule-based method), eval version, and
date — uncitable without all four. Every results file restates the v1 synthetic-data caveat
(`evals/README.md`): only relative comparisons between methods are trustworthy, no unqualified
accuracy figure. Targets are read against F-007's calibration anchors (κ≈0.71–0.76 expert
agreement, 44.4 FullCov@10 best retrieval) — a result clearing these comfortably should prompt
suspicion of the eval, not celebration.

## Consequences

**Makes easy:** a scorer can be written directly from point 2's branch summary without re-deriving
it from `wizard.js`; the hedge/blocked/incomplete distinctions (points 3-5) prevent the three most
likely scoring bugs (crediting indecision, conflating refusal with error, conflating "ticked
empty" with "never asked"); the eval-set skill and `evals/README.md` no longer duplicate scoring
rules that can drift independently — they now point here.

**Makes hard / forecloses:** any future wizard rewrite obligates an RQ-6 re-run (point 2) — this
is now an explicit trigger to check for, not a risk to discover by accident. A scorer cannot treat
"no hosting signal in the text" as equivalent to "no signal, use majority class" — point 5 requires
it to actually run the baseline's genai/ds-only fallback first, which is more implementation work
than a flat lookup table.

**Unaffected:** RQ-3's dependency on RQ-6 (its "answered when" bar cites RQ-6's eval) needs no
change — this ADR settles methodology, not RQ-3's inputs. The actual baseline run, and RQ-6's
`Status`, stay open until that run happens and is written up per point 9.

## Alternatives considered

- **Score the CII hedge as Top-1 correct if either alternative matches.** Rejected — this silently
  rewards the wizard for declining to decide and would make the baseline look better at exactly
  the cases (`cii-undetermined`) where it is honestly uncertain, undermining the whole point of
  measuring it.
- **Build a minimal rule-based text→ticks extractor as part of RQ-6**, so the baseline is fully
  automated end to end. Rejected — that is RQ-3's question. Conflating the two would make it
  impossible to tell whether a scoring error came from the decision logic or from extraction, and
  RQ-3's own "answered when" bar already expects RQ-6's eval to exist first, not to be built
  alongside it.
- **Majority class = most common individual type id, unpacked from all `acceptable_answers`
  entries.** Rejected — double-counts compound answers (an entry like
  `["generative-ai", "medium-risk-cloud"]` would inflate both ids' individual counts) and scores
  the floor against a different unit than the baseline itself is scored against.
