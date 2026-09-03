# Research questions

The spine of the work. Each RQ has a status, the findings that bear on it, and a note on what
would count as an answer. Update status here whenever a finding lands.

Status: `open` → `in-progress` → `answered` (link the finding) → `parked` (say why).

---

## RQ-1 — How do users actually describe their systems?
**Implications:** site, classifier · **Status:** open (constrained)

> **Constraint (2026-09-01):** no real user-written descriptions are available. Sources are
> authoritative only — upstream SSP pages, GovTechSG structured data. This RQ can therefore only
> be approached through proxies, and any answer is provisional. See
> `research/evals/README.md` for what this costs the eval.

How far is a real user's description of their system from the vocabulary in `classificationText`,
domain names, and control titles? The site's search matches substrings over `id`, `title` and
`description` only — so any vocabulary gap is a silent zero-results experience.

*Answered when:* we have a documented vocabulary gap — terms users would plausibly use that match
nothing in the corpus, and the corpus terms they would never think to type.

*Note:* user interviews are out of scope for now, so this must be approached through proxies —
the corpus's own vocabulary, prior art on compliance intake, and the eval descriptions written
under RQ-6.

---

## RQ-2 — Where does the current wizard give wrong or unhelpful answers?
**Implications:** site · **Status:** **answered** 2026-09-02 · **Findings:** F-004, F-012, ADR-005

The 7-node tree in `wizard.js` **returned** exactly one type, with no ranking and no way to express
a composite system. Known suspects were catalogued in F-004: composite systems (GenAI + digital
service) unreachable, on-premises never reaching the sensitivity question, and medium vs.
high-risk cloud separable only by CII designation.

*Answered when:* every failure mode is enumerated with a concrete example description, and each is
classified as *fixable in the tree* / *needs a different interaction model* / *blocked upstream by
the standard*.

**Direction set 2026-09-01 (ADR-001, accepted):** composite-system unreachability (F-004 issue 1)
and no-persistence (issue 4) are now classified *needs a different interaction model* —
tick-all-that-apply plus high-water-mark composition, per the ADR. On-premises never reaching a
sensitivity question (issue 2) stays *blocked upstream* (the standard defines only one on-prem
profile). This doesn't itself answer RQ-2 — issues 3 and 5 still need their own classification —
but the ADR fixes the target model the remaining failure modes get classified against.

**New failure mode found during ADR-001 review (F-012, 2026-09-01):** q4 (sandbox) is asked as a
branch separate from q5-q7 (sensitivity/hosting), but `sandbox` shares the exact control membership
of `low-risk-cloud`/`medium-risk-cloud` and is a strict subset of `high-risk-cloud` — it is the
laxest rung of the same ladder, not a different kind of question. Classified *needs a different
interaction model*, folded into the same tick-all-that-apply/`min()` fix as issues 1 and 4.

**Built 2026-09-02:** the tick-all-that-apply model is now live in `docs/assets/js/wizard.js`,
resolving issues 1, 4, and the F-012 sandbox reframing in code, not just in the ADR.

**Answered 2026-09-02.** Issues 3 and 5 reclassified against the shipped model: both had survived
in a new shape (CII was still welded to the top sensitivity rung; question text was still
hardcoded and had already drifted from `classificationText` on the CII point specifically) —
[ADR-005](decisions/ADR-005-cii-as-independent-baseline-characteristic.md) splits CII into its own
tri-state question and has `wizard.js` fetch `system-types.json` to source hint text live. All five
F-004 issues now carry a final classification: 1 & 4 fixed via the tick-all-that-apply rewrite; 2
blocked upstream, disclosed; 3 & 5 fixed via ADR-005. A rule-based-baseline score (RQ-6) still
hasn't been run against the current model.

---

## RQ-3 — Which signals in a free-text description determine the type?
**Implications:** classifier · **Status:** open · **Findings:** F-005, F-012

The wizard's current tick-all-that-apply model implies the same underlying features the old
7-question tree did, now asked as independent characteristics rather than one exclusive path:
WOGAA-tracked, traffic volume, GenAI core function, hosting location, a sandbox/low/sensitive
hosting-sensitivity rung, and — split out on its own since ADR-005 — CII designation. Are those
extractable from prose? Which are usually absent? What else carries signal?

**Revised 2026-09-01 (F-012):** "non-production" (sandbox) is not a separate boolean feature — it
is the bottom value of the same hosting-sensitivity ordinal as CII/sensitivity level. The feature
inventory should list one ordinal (sandbox < low < medium < high) rather than a sandbox flag plus a
separate sensitivity feature.

*Answered when:* we have a feature inventory, each marked for how reliably it appears in a
realistic description, plus a first read on whether rule-based extraction is sufficient or
semantic methods are needed — measured against RQ-6's eval, not asserted.

---

## RQ-4 — How does prior art solve control discovery?
**Implications:** site, classifier · **Status:** **answered** 2026-09-01 · **Findings:** F-007 ·
**Sources:** PA-001..PA-013

**Answer:** prior art solves selection *after* typing, and nobody solves typing from a free-text
description — every source assumes the system is already classified by a step outside the
framework. What it does give us: high-water-mark composition (FIPS 199) as the answer to composite
systems, a formal overlay vocabulary (SP 800-53B App. C), the only written taxonomy of why a
control may be dropped (800-53B §2.4), and four independent frameworks converging on *show all
controls with a status and reason* rather than a filtered list. Plus two hard calibration anchors:
expert agreement ceilings at κ≈0.71–0.76, best full-coverage retrieval at 44.4 FullCov@10.

Follow-ups worth their own RQ if pursued: overlay composition is unsolved everywhere (nobody
defines what happens when two overlays disagree), and no crosswalk disagreement rates are published.

NIST OSCAL (whose profile-resolution model addresses this corpus's level-is-a-join structure
directly), SP 800-53B baselines, ISO 27001 Statement of Applicability, SCF and CSA CCM crosswalks,
commercial compliance tooling, and peer-government frameworks that publish real selection
guidance.

*Answered when:* cards filed in `prior-art/` and synthesized into a finding that names what to
adopt, what to adapt, and what nobody has solved.

*Run via:* `prior-art-review` skill → `literature-scout` agent.

---

## RQ-5 — What is missing from the corpus for guidance to be useful?
**Implications:** data, site · **Status:** substantially answered (verified 2026-09-01) ·
**Findings:** F-001, F-002, F-003, F-006

`selectionGuidance` is a single sentence and is currently fetched by nothing. 50 controls have no
`guidance` at all. The `generative-ai` profile has 9 controls against ~117 for its peers.

*Answered when:* each gap is classified as *scrape artefact* (re-fetchable), *genuinely absent
upstream* (needs authoring or a pointer), or *deliberate*, with the upstream page checked for each.

**Verification results:**

| gap | verdict |
|---|---|
| 50 missing `guidance` (IS/LM/PM/ST) | **scrape artefact** — exists upstream, 100% OSCAL coverage. Recoverable (F-001). |
| `generative-ai` = 9 controls | **framed standalone, contents say otherwise upstream — resolved by owner confirmation:** composition is permitted but not required, for both GenAI and Digital Services templates (F-002, confirmed 2026-09-01). |
| one-sentence `selectionGuidance` | **genuinely absent upstream** — no decision tool or flowchart exists. Whatever the site offers, it will be constructing (F-003). |

Remaining: ~~(a) decide the recovery route for F-001 in an ADR — scrape, OSCAL import, or
hybrid~~ — **done, recorded retroactively as
[ADR-004](decisions/ADR-004-guidance-recovery-route-rescrape.md) 2026-09-02 (accepted): re-scrape,
the route the F-008 rebuild already took.** ~~(b) get a human answer from GovTech on the
composition question~~ — **done, F-002 confirmed 2026-09-01.** ~~(c) decide whether to split the
composed `guidance` field~~ — **done, drafted as
[ADR-002](decisions/ADR-002-split-guidance-into-recommendations-and-risk.md) 2026-09-01 (proposed,
not yet owner-accepted).**

**Not part of this RQ's original scope, but the same broad thread — filed separately:** F-014
(2026-09-03) found and fixed a distinct corpus-fidelity defect discovered post-hoc: 20 controls'
`risk`/`rationale` and `citations` had site footer/nav chrome leaked in by a `scrape.py` boundary
bug, unrelated to any gap RQ-5 already classified above. Not folding into RQ-5's own verdict
table since it's a different defect class (contamination, not absence) found after RQ-5 was
already substantially answered.

---

## RQ-6 — What does a defensible eval look like, and what is the baseline?
**Implications:** classifier · **Status:** **answered** 2026-09-03 · **Findings:** F-010, F-011,
F-013, ADR-006

Nothing can be claimed about semantic or LLM approaches until the rule-based baseline — today's
wizard logic (tick-all-that-apply + high-water-mark composition, CII independent per ADR-005),
mechanically applied per [ADR-006](decisions/ADR-006-rq6-baseline-scoring-methodology.md) — is
measured on a labelled set.

**Scaling deferred 2026-09-02.** Scaling `evals/v1/` to ~120-160 cases is deferred indefinitely —
settling with the current 15-case pilot rather than generating more. F-010's and F-011's findings
(no case has one answer; the `hosting-unknown` fork is under-diversified) still stand and still
constrain what the 15-case set can claim; scaling was how this ADR-free decision proposed to
address F-011's specific homogeneity risk, not a prerequisite for scoring a baseline at all.

**Scoring methodology pinned 2026-09-03 (ADR-006).** Before this, "mechanically applied" left
several judgment calls implicit — how to score the wizard's CII-hedge output, blocked/conflict
outputs, and missing-field cases, and what "majority class" means over a set-valued label space.
ADR-006 resolves each.

**Answered 2026-09-03.** Both scored against the 15-case pilot per ADR-006 —
`research/evals/v1/results/wizard-baseline-2026-09-03.md`. **Majority-class floor: 60.0% Top-1
(always guess `medium-risk-cloud`). Rule-based wizard baseline: 20.0% Top-1, 40.0% Top-3** — the
floor beat the baseline outright. The wizard resolved to `incomplete` on 8/15 cases, all
`hosting-unknown`, because the sensitivity-rung question only rendered once `hosting = "cloud"`
was ticked — sensitivity was gated behind hosting, not askable independently. Filed as **F-013**.

**Fixed and re-scored, same day (ADR-007, F-013's resolution note).** The hosting-gates-sensitivity
gap was a real, narrow site defect independent of the eval numbers — the wizard's own copy
promises "tick more than one if unsure," and every other axis (CII, sensitivity rung) already
honoured that except hosting. ADR-007 extended the existing CII-hedge idiom to hosting. Re-run:
**wizard baseline moves to 20.0% Top-1, 80.0% Top-3** —
`research/evals/v1/results/wizard-baseline-2026-09-03-adr007.md` — now clearing the majority-class
floor. These are the current figures any semantic or LLM method reports a delta against.

*Run via:* `eval-set` skill.

**Calibrated 2026-09-01 (F-007):** expert inter-annotator agreement on control applicability
ceilings at κ≈0.71–0.76, and best-known full-coverage retrieval over regulatory corpora is 44.4
FullCov@10. Targets must sit under those ceilings; a result that beats them comfortably indicates a
leaky eval, not a breakthrough. Combined with the synthetic-data limitation
(`evals/README.md`), v1 supports **relative** comparison only.

**Spot-checked 2026-09-01:** the 15-case pilot's owner spot-check is done
(`research/evals/v1/spot-check-2026-09-01.md`) — 13/15 agree, 1 agree-with-a-note, 1 disagreement
(EV-013's `sandbox` answer, folded into F-010). The spot-check also surfaced F-011: 6 of 15 cases
share one identical `hosting-unknown` answer pair, a coverage-diversity risk to correct for before
generating the 120-160 case v1 set.

---

## Parked

- **User research with real agency staff.** Out of scope this round (confirmed 2026-09-01).
  RQ-1 and RQ-6 both get materially weaker without it — revisit if access opens up.
- **Building the classifier.** Explicitly a later goal. It shapes what we record now; it is not
  being built.
