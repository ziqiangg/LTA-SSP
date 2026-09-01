---
name: eval-set
description: Build, label, and score evaluation data for SSP control discovery — mapping a free-text system description to the right system type and control set. Use when constructing labelled examples, defining the labelling schema, establishing a baseline, or measuring any classification or retrieval approach. Defines the record schema in research/evals/, sampling strategy, disagreement handling, and the metric definitions that keep results comparable across runs.
---

# Eval sets for control discovery

The eventual system takes a free-text system description and returns relevant controls plus
guidance. **Build the eval before building the system.** Without it, "the semantic approach seems
better" is unfalsifiable, and the rule-based baseline never gets the fair hearing it usually wins.

## What is being predicted

Two linked tasks — keep them separate in scoring:

1. **Type classification** — description → one of 8 system types. What the wizard does today.
2. **Control retrieval** — description → a set of `(controlId, level)` pairs. Currently derived
   deterministically from task 1 via `profiles.json`, but it need not stay that way, and a system
   could do well at task 2 while failing task 1.

## Record schema — `research/evals/v1/cases.jsonl`

One JSON object per line.

```json
{
  "id": "EV-001",
  "description": "I look after the HR system for our board — staff records, leave, claims, payroll...",
  "provenance": "blind-generated-2026-09-01",
  "acceptable_answers": [["medium-risk-cloud"], ["low-risk-on-premises"]],
  "expected_controls": null,
  "label_basis": "Internal back-office, so not a Digital Service. Payroll + NRIC reads as Confidential/Sensitive High. Hosting never stated, and the type turns entirely on it.",
  "difficulty": "hard",
  "ambiguity": ["hosting-unknown", "sensitivity-inferred"],
  "labeller": "claude",
  "labelled_on": "2026-09-01"
}
```

Fields that carry weight:

- **`acceptable_answers`** — a list of *answers*, each itself an **array of type ids**. Not a flat
  list of types. Two reasons, both demonstrated by the pilot (F-010):
  1. A description can admit several distinct answers — 15 of 15 pilot cases did. Forcing one gold
     label manufactures fake errors and hides real ones.
  2. An answer can be **compound** — an overlay plus a hosting profile, e.g.
     `["generative-ai", "medium-risk-cloud"]`. 5 of 15 pilot cases needed this, and a flat list
     cannot express it. Composition is permitted but not required (F-002), so
     `[["generative-ai"], ["generative-ai", "low-risk-cloud"]]` is a legitimate label meaning
     *either* standing alone *or* combined is correct.

  Order entries most-preferred first where you have a view; scoring does not currently use the
  order, but a reader needs it.
- **`label_basis`** — the reasoning, in a sentence. This is what makes a disputed label
  reviewable, and it doubles as training signal for an explanation feature later.
- **`ambiguity`** — named ambiguity classes present, from the fixed vocabulary below.
- **`provenance`** — where the description came from. Never mix provenances silently.
- **`expected_controls`** — usually `null` (derived from the profile). Populate only when the case
  asserts something the profile join does not capture.

## Ambiguity vocabulary

The corpus makes certain confusions structural. Tag them so failures can be attributed:

| Tag | Meaning |
|---|---|
| `hosting-unknown` | Cloud vs. on-premises is never stated. **The most common condition in the pilot (8/15)** — and since the standard has only one on-prem profile, it forks the answer irreducibly. |
| `sensitivity-inferred` | No Security Sensitivity Level stated; the label rests on inferring it from the data described. **0 of 15 pilot descriptions stated one.** |
| `cii-undetermined` | Medium vs. high-risk cloud turns *only* on CII designation — the `classificationText` sensitivity wording is identical. Rarely inferable from a description. |
| `composite` | Fits more than one type at once (a GenAI-powered public digital service). Needs a compound entry in `acceptable_answers`. |
| `traffic-unknown` | Digital service whose ≥1M visits/year status is unstated, or stated in units that do not convert (applications, monthly actives, downloads). |
| `wogaa-unknown` | External-facing, but whether it is WOGAA-tracked — and so a Digital Service at all — is unstated. |
| `nonprod` | Sandbox / pilot framing that may or may not mean the Sandbox profile. Beware: the environment label and the data it holds can disagree. |
| `third-party-managed` | Vendor runs the platform and the describer does not know the architecture. Compounds `hosting-unknown`. |
| `genai-overlay` | GenAI aspect present; since composition is permitted but not required, both standalone and compound answers may be acceptable. |
| `onprem-sensitivity` | On-premises with medium/high sensitivity; the standard defines only one on-prem profile. |

A case tagged `cii-undetermined` that a model gets "wrong" may be revealing a corpus problem, not
a model problem. Report accuracy overall **and** broken down by tag.

**Generate descriptions blind.** Anyone who knows the wizard's questions will unconsciously write
descriptions that answer them, and the eval then measures nothing. Delegate generation to an agent
given personas and system archetypes but told *nothing* about the SSP, the 8 types, the questions,
or what the data is for — then label afterwards. The pilot's key result (0/15 descriptions stated a
sensitivity level) is only credible because the writer could not have known it mattered. Verify
blinding held before labelling: if every description happens to state hosting, sensitivity and
traffic, it leaked and the batch should be regenerated.

## Sampling

Aim for ~120-160 cases in v1. Composition matters more than volume:

- **Coverage** — every one of the 8 types represented, including the awkward ones. Do not let
  low-risk-cloud dominate just because it is easy to write.
- **Stratify by difficulty** — roughly 40% easy (textbook), 40% realistic (how someone would
  actually describe their system: partial, jargon-laden, missing the deciding fact), 20% hard
  (each carrying an `ambiguity` tag).
- **Register variety** — vary vocabulary deliberately. If every description reuses `classification
  Text` wording, you are measuring string overlap and will badly overestimate every method.
- **Adversarial slice** — descriptions that mention a distractor ("we use AI to write our docs" on
  a system where GenAI is not a core function; "sandbox" as a payment sandbox).

Record provenance per case and keep a **held-out slice** untouched until a method is final.

## Labelling and disagreement

- Label from the description alone. If you needed outside knowledge, the description is
  under-specified — fix it or tag it.
- Every label needs a `label_basis`.
- Where two readings are defensible, put both in `acceptable_answers` rather than picking. Log the
  disagreement in the case's `ambiguity`.
- When a label cannot be settled because *the standard itself* is unclear, that is a finding with
  `implications: [data, site]`. File it.

## Metrics — `research/evals/v1/results/<method>-<date>.md`

**Type classification**
- **Top-1 accuracy** — prediction ∈ `acceptable_types`.
- **Top-3 accuracy** — for a ranked UI, which is the likelier product shape than a single answer.
- **Per-class recall** and a **confusion matrix**. Aggregate accuracy hides that everything
  collapses into low-risk-cloud.
- **Accuracy by `ambiguity` tag** and by `difficulty`.

**Control retrieval**
- **Precision / recall / F1** over the control set.
- **Level-0 recall**, reported separately and weighted highest. Missing a mandatory control is not
  the same class of error as missing an optional one, and a flat F1 pretends it is.

**Asymmetry to respect:** high-risk-cloud is a strict superset of medium-risk-cloud (0 controls
unique to medium; 20 added, 38 escalated). Predicting *high* when the truth is *medium* costs
effort; predicting *medium* when the truth is *high* under-protects. Report these two directions
separately — never fold them into one error count.

## External calibration — know the ceiling before setting a target

Two published anchors (F-007, cards PA-009/PA-010). Use them; do not set targets in a vacuum.

- **Expert inter-annotator agreement on control applicability tops out at κ ≈ 0.71–0.76**
  (PROPARAG). Human experts disagree about which controls apply. An eval demanding better than that
  is measuring noise, and a labelling scheme that produces *higher* apparent agreement than experts
  achieve is probably leaking the answer — most likely through shared vocabulary between the
  description and the label (see the synthetic-data limitation in `research/evals/README.md`).
- **Best-known full-coverage retrieval over regulatory corpora is 44.4 FullCov@10**
  (RegOps-Bench). Retrieving *every* relevant control is unsolved research, not an engineering
  detail. If an early method appears to beat this comfortably, suspect the eval before believing
  the result.
- **Iterate over controls, not over the query** (PROPARAG). For 248 controls this is entirely
  tractable and it outperformed query-side iteration. Make it the first retrieval baseline.

## Baseline first

Establish the **rule-based baseline** — today's 7-node wizard tree in `docs/assets/js/wizard.js`,
mechanically applied — before evaluating anything else. Every later method reports as a delta
against it. Also record the **majority-class** floor, so an apparently good number can be checked
against doing nothing.

Log every run with the method, its configuration, the eval version, and the date. A result without
its configuration is not reproducible and should not be cited in a finding.
