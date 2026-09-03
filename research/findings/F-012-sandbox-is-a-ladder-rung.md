---
id: F-012
title: Sandbox shares low/medium-risk-cloud's exact control membership — it is a fourth ladder rung, not an orthogonal flag
date: 2026-09-01
rq: [RQ-2, RQ-3]
implications: [site, classifier]
confidence: high
status: actioned
---

> **Resolved 2026-09-02.** The fix this finding proposed — hosting as one ordered characteristic
> resolved by `min()`, not a separate sandbox tick-box — shipped as part of ADR-001's
> tick-all-that-apply rewrite: `wizard.js`'s sensitivity-rung fieldset includes `sandbox` as a
> checkbox alongside `low`/`sensitive`, all resolved through the same `cloudTierTypes()` path, not
> a separate branch. `status` moves to `actioned`. The corpus gap this finding also names — no
> `sandbox`-at-CII or `sandbox`-on-premises variant upstream — is unaffected and still open;
> `wizard.js`'s conflict check now blocks exactly that combination (including the CII-unanswered
> hedge) rather than silently resolving it — see
> [ADR-005](../decisions/ADR-005-cii-as-independent-baseline-characteristic.md).

## Observation

Diffing `sandbox` against each cloud-tier profile:

```
sandbox (117) vs low-risk-cloud (117)     shared 117 | only in sandbox: 0 | only in low: 0    | level changed: 82
sandbox (117) vs medium-risk-cloud (117)  shared 117 | only in sandbox: 0 | only in medium: 0  | level changed: 91
sandbox (117) vs high-risk-cloud (137)    shared 117 | only in sandbox: 0 | only in high: 20   | level changed: 99
```

`sandbox`'s 117 controls are **exactly** the same set as `low-risk-cloud` and `medium-risk-cloud`
(same 13 domains: `AS,SC,ST,NS,BR,DP,LM,AC,CS,PM,IS,SD,CK`), and a strict subset of
`high-risk-cloud`'s 137 — missing precisely the same 20 controls (`HR`, `RS`, plus scattered
additions in `BR`/`NS`/`CK`/`PM`/`SD`/`AC`/`LM`) that F-005 already identified as medium-risk-cloud's
gap against high. Nothing is unique to sandbox.

Level distributions run monotonically laxer in aggregate:

| profile | L0 | L1 | L2 |
|---|---|---|---|
| sandbox | 3 | 0 | 114 |
| low-risk-cloud | 7 | 78 | 32 |
| medium-risk-cloud | 26 | 68 | 23 |
| high-risk-cloud | 63 | 59 | 15 |

## Evidence

- `python research/scripts/corpus.py diff sandbox low-risk-cloud`
- `python research/scripts/corpus.py diff sandbox medium-risk-cloud`
- `python research/scripts/corpus.py diff sandbox high-risk-cloud`
- `python research/scripts/corpus.py types` (domain lists)
- F-005 (medium/high nesting and the `min()` trap — its own AC-1 worked example already
  computes across sandbox/low/medium/high without stating sandbox is a ladder member)
- repo @ `51f7f65`

## Interpretation

`sandbox` is not an orthogonal "non-production" characteristic sitting beside the hosting ladder —
it is, by membership, the **laxest rung of the same ladder** `low-risk-cloud ⊂ medium-risk-cloud ⊂
high-risk-cloud` already describes. It shares their exact control set and simply assigns almost
everything to L2. F-005's own composition example (AC-1: L2 sandbox → L1 low/medium → L0 high)
already relies on this without naming it: the `min()` mechanism F-005 and ADR-001 both propose for
the cloud ladder already works correctly across sandbox today, because sandbox is a data point on
that same ladder, not a separate case needing its own rule.

This matters for interaction design, not just data modelling. `wizard.js`'s q4 ("sandbox / non-
production pilot only?") is asked as a branch *before* the sensitivity/hosting questions (q5-q7),
implying sandbox is a different kind of thing from a hosting tier. The corpus disagrees: sandbox
sits at position 0 of the same axis low/medium/high occupy at positions 1-3. Treating it as a
separate tick-box (as ADR-001's draft language does, listing "hosting tier" and "sandbox/non-prod"
as parallel characteristics) reintroduces exactly the kind of exclusive-branch structure F-004
criticises, just with one fewer branch than before.

**What the corpus does not resolve:** there is no `sandbox`-at-CII or `sandbox`-on-premises
variant. Sandbox's own membership caps at the low/medium 117-control set — it never gained
`high-risk-cloud`'s extra 20. A "sandbox pilot of a CII system" has no defined answer in the data;
the honest output is that this combination is unrepresented upstream, not that the tool can compute
one.

## Implications

- **site:** ~~ADR-001's tick-all-that-apply model should represent hosting as **one ordered
  characteristic with four rungs** (sandbox, low, medium, high) resolved by a single `min()`, not
  as a hosting-tier tick-box plus a separate sandbox tick-box.~~ **Shipped 2026-09-02** — the
  sensitivity-rung fieldset in `wizard.js` includes `sandbox` as a checkbox resolved through the
  same `cloudTierTypes()` path as `low`/`sensitive`, not a separate branch (the rung count landed
  at three, not four — ADR-005 subsequently merged the old `medium`/`high` rungs into one
  `sensitive` band and split CII out as its own question).
- **classifier:** The feature schema from F-004 should list hosting sensitivity as one ordinal
  (sandbox < low < medium < high) rather than a boolean sandbox flag plus a separate ordinal.
- **classifier/site:** A description implying both "pilot/sandbox" and "CII" is evidence of an
  upstream gap, not an under-specified query — the output should say so rather than guessing
  between medium- and high-risk-cloud.

## Open questions

- Does upstream ever define, or plan to define, a sandbox-on-premises or higher-sensitivity
  sandbox variant? Not found in the current scrape — worth a targeted check next re-scrape.
- Is EV-013 (the sandbox vs. medium-risk-cloud eval disagreement flagged in F-010's Open Questions)
  actually this same gap in a different form? Worth cross-checking when F-010 is next revisited.
