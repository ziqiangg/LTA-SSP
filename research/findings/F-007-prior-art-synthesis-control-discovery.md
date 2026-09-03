---
id: F-007
title: Prior art solves selection after typing — nobody solves typing from a description
date: 2026-09-01
rq: [RQ-4, RQ-3, RQ-6]
implications: [site, classifier]
confidence: high
status: actioned
sources: [PA-001, PA-002, PA-003, PA-004, PA-005, PA-006, PA-007, PA-008, PA-009, PA-010, PA-011, PA-012, PA-013]
---

> **Primary site recommendation actioned 2026-09-02.** This finding's top site recommendation —
> "replace the 7-question tree with tick-all-that-apply plus a high-water-mark resolve" (below) —
> shipped as ADR-001 (implemented 2026-09-02) and ADR-005 (CII split into its own characteristic,
> 2026-09-02). The "render all controls with a status and a reason" recommendation also shipped,
> via ADR-001 step 2 (`controls.js`'s mechanical `in-profile`/`not-in-profile` status). The "split
> the conflated axes" and "which direction does this tool serve" recommendations are **not** fully
> resolved — the wizard now composes independent characteristics, a step toward the former, but
> `profiles.json` itself still ships 8 discrete type ids rather than an orthogonal decomposition,
> and no ADR has settled the ISO-vs-NIST framing question. `status` moves to `actioned` to reflect
> that the finding's actionable core has been acted on; its open synthesis questions (crosswalk
> disagreement rates, the overlay-conflict literature gap, the framing tension) remain live
> research below, not implementation debt.

## Observation

Thirteen sources reviewed across control-catalogue standards (OSCAL, SP 800-53B, FIPS 199, ISO
27001), peer government frameworks (UK NCSC CAF, ASD ISM, GOV.UK Service Standard), crosswalk
vocabularies (NIST IR 8477, CSA CCM), and retrieval research (RegOps-Bench, PROPARAG).

**The central result is a gap, not a technique.** Every source assumes the system has *already*
been typed or classified, by a step that happens outside the framework. FIPS 199 hands off to SP
800-60's information-type catalogue; ASD's ISM requires a classification determined under a
separate policy framework; OSCAL begins once you know which profile to resolve. Nothing found maps
a **free-text system description** to controls.

That is precisely the problem this project exists to solve, and there is no prior art to copy.

## What the prior art *does* answer

**1. Composition — how to be two things at once (PA-003).** FIPS 199 composes by **high-water
mark**: categorise each information type, then take the pointwise most-stringent value per security
objective across the system. Crucially this is *well-defined for us* — because our profiles nest
(F-005), our levels are totally ordered, so the resolve is meaningful. Selecting {low-risk-cloud,
high-risk-cloud} resolves to high-risk-cloud rather than nonsense. This is the best available answer
to F-004's worst limitation. FIPS 199 also sanctions an explicit **upward override** after the
mechanical computation — the category is a floor with a documented raise step, not an oracle.

> **Implementation note:** in our encoding strictness runs *downward* (L0 mandatory → L2 optional),
> so the most-stringent resolve is **`min()`, not `max()`**. See F-005.

**2. Overlays have a formal vocabulary (PA-006).** SP 800-53B Appendix C defines overlays as
composable, multi-axis specialisations with explicit add / modify / eliminate semantics. This gives
F-002's unresolved question a precise name: if GenAI is additive, it is an *overlay* in the
800-53B sense, and there is an established model for what that means.

**3. Why a control may be dropped (PA-005).** SP 800-53B §2.4's six scoping considerations are the
only written taxonomy found for justifying exclusion. Our corpus has no equivalent — and given
`selectionGuidance` is one sentence (F-003), this is directly borrowable. 800-53B also names
**common / inherited controls**, a concept our model entirely lacks: a control satisfied by the
hosting platform rather than by the system owner.

**4. Applicability can live on the control (PA-004).** ASD keeps multi-valued `applicability` props
on each control and *generates* the baseline profiles from them — verified as exact set equality
across all 8 baselines. Our layout is the mirror image (profile-as-truth). Both work; the
transferable invariant is that whichever is canonical, **the other must be exactly derivable, and
that derivation should be checked rather than assumed**.

**5. Show everything with a status, don't filter (PA-002, PA-005, PA-008, PA-012).** Four
independent sources converge here. NCSC CAF makes a "profile" a *target level per outcome* —
including explicitly "not achieved" — rather than a subset. ISO 27001's Statement of Applicability
makes the **justification** the deliverable, with the catalogue used as a completeness check. The
convergence is strong enough to treat as the review's main site recommendation.

**6. Realistic performance ceilings (PA-009, PA-010).** RegOps-Bench: the best full-coverage
retrieval system reaches **44.4 FullCov@10**. PROPARAG: expert inter-annotator agreement on control
applicability tops out at **κ = 0.71–0.76**, and iterating over *controls* beats iterating over the
query. These are the first external calibration points this project has.

## The framing conflict worth naming

**ISO and NIST disagree about the direction of travel, and the SSP is caught between them.** ISO
27001 derives controls from a risk assessment and uses the catalogue only as a completeness check.
NIST/FedRAMP prescribe a baseline and tailor down. The SSP's single sentence of guidance — "assess
the risks and threats for each of their systems, to determine the controls required" — is phrased
the **ISO way**, while our wizard behaves the **NIST way**: pick a type, receive a baseline.

That mismatch is not cosmetic. It explains the tension in F-003 (the standard's L1 prose says
"assess and apply according to risk impacts" while our UI labels it "Baseline" and preselects it),
and it means the site is currently answering a question the standard did not ask. Resolving which
direction this tool serves is an **ADR-level decision**, not an implementation detail.

## Implications

- **site (highest value, cheapest):** Render *all* controls with a status and a reason rather than
  a filtered list — four independent frameworks converge on this. It directly addresses the "why
  does this apply to me" gap and needs no data-model change, only `controls.js` presentation.
- **site:** ~~Replace the 7-question tree with tick-all-that-apply plus a high-water-mark resolve
  (PA-003).~~ **Shipped 2026-09-02** (ADR-001, ADR-005). Still open: rewrite the risk-tier question
  using FIPS 199's AMPLIFICATION pattern — concrete consequences rather than classification jargon
  — which is pure copy-editing in `wizard.js`.
- **site:** Split the conflated axes. Our 8 types mix *what kind of thing it is* (cloud / digital
  service) with *how bad if it fails* (low / medium / high). FIPS 199 keeps these orthogonal; doing
  the same would yield 8 combinations from ~4 answers and make the nesting explainable rather than
  memorised.
- **classifier:** Calibrate expectations against PA-009/PA-010 before setting any target. If expert
  agreement ceilings at κ≈0.75, an eval demanding better than that is measuring noise — this bounds
  what our own labels can claim (see `evals/README.md`, which already flags v1 as synthetic).
  Adopt PROPARAG's control-centric iteration as the baseline retrieval strategy.
- **data:** Add a build-time nesting assertion over `profiles.json` (F-005, PA-004).
- **research:** `oscal-cli resolve-profile` (PA-013) makes it cheap to test the OSCAL fit against
  our data without committing to it.

## Open questions

- ~~**Nobody composes overlays.**~~ **Resolved for our data (2026-09-01) — does not apply.** The
  literature gap is real: no framework found defines what happens when two applicable overlays
  disagree about one control, and OSCAL's only answer is a merge default that knowingly emits
  invalid output. But it **does not bite us**, because our overlays never overlap the thing they
  overlay. Measured: all 9 `generative-ai` controls appear in no other profile, and zero DSS
  controls appear in any non-DSS profile. Combining an overlay with a hosting profile is a plain
  union with nothing to reconcile. Keep the literature gap on file in case a future SSP revision
  introduces overlapping overlays — that is the condition that would make it live again.
- **No published crosswalk disagreement rates.** IR 8477 supplies the relationship vocabulary but
  no measurements — and the same control pair gets a *different* relationship under syntactic vs
  semantic vs functional rationale (PA-007), so "mapped" is not a single claim.
- Which direction does this tool serve — risk-first (ISO) or baseline-then-tailor (NIST)? Needs an
  ADR.
- Not checked: FedRAMP baseline pages (404/DNS failure) and cyber.gov.au prose (connection reset);
  Essential Eight is covered only via ASD's data, not its documentation.
