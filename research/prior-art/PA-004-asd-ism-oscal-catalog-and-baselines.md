---
id: PA-004
title: ASD Information Security Manual in OSCAL — catalog, applicability props, and generated baseline profiles
source: https://github.com/AustralianCyberSecurityCentre/ism-oscal
kind: gov-framework
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
The Australian Signals Directorate publishes the whole Information Security Manual as an
OSCAL catalog (1,150 controls) plus eight illustrative baseline profiles and their resolved
catalogs. This is the closest structural peer to LTA-SSP found anywhere in this survey: a
national-government control catalogue where **applicability is a property of the (system
classification, control) pair**, exactly our situation, solved in public with real data we
can inspect. Findings below are from reading the published JSON directly, not from prose
about it.

## Mechanism
**Applicability lives on the control as repeated props, and the profiles are generated from
them.** Each control carries multi-valued OSCAL `props`:

    "props": [
      {"name": "applicability", "value": "NC"},
      {"name": "applicability", "value": "OS"},
      {"name": "applicability", "value": "P"},
      {"name": "applicability", "value": "S"},
      {"name": "applicability", "value": "TS"},
      {"name": "essential-eight-applicability", "value": "ML1"},
      {"name": "essential-eight-applicability", "value": "ML2"}
    ]

(`ism-1691`, verbatim from `ISM_catalog.json`.) The five classification values are
non-classified, OFFICIAL: Sensitive, PROTECTED, SECRET, TOP SECRET; the E8 values are the
three Essential Eight maturity levels.

The eight profiles are then trivially thin: one `import` pointing at the catalog by
back-matter uuid, a single flat `include-controls/with-ids` list, `merge: {as-is: true}`, and
**no `modify` block at all**. ASD adds no tailoring in the profile layer — the profile is
purely a materialised selection.

**I verified the generation relationship holds exactly.** For all five classification
profiles and all three E8 profiles, the set of ids in `with-ids` is *identical* to the set of
controls whose props carry the matching value — 8/8 exact set equality, zero controls in a
profile that the props do not justify, zero the other way. The profiles are a derived
artefact; the props are the source of truth. ASD says as much: the profile information is
"also included in the source ISM catalog" to "enable greater flexibility for consumers, and
to align with the ISM's non-machine-readable documents."

**The baselines do not nest, and the exceptions are informative.** Measured control counts:
NC 1024, OS 1035, P 1035, S 1099, TS 1108; ML1 46, ML2 87, ML3 123. Despite monotonically
rising counts, only two of the ten ordered pairs are true subsets — OS ⊆ P (identical sets,
1035 each) and ML1 ⊆ ML2. Everywhere else the lower tier contains controls the higher tier
drops: 3 controls in NC are absent from OS/P, 25 in NC absent from TS, 19 in SECRET absent
from TOP SECRET, and 2 in ML1 absent from ML3.

The E8 case shows *why*, and it is not an error. `ism-1695` is
"Patches, updates or other vendor mitigations for vulnerabilities in operating systems of
workstations, non-internet-facing servers and non-internet-facing network devices are
applied within one month of release" — tagged ML1 and ML2 but **not** ML3. It is absent from
ML3 because at ML3 a stricter-timeframe control supersedes it. A weaker obligation is not a
subset of a stronger one; it is *replaced* by it. So non-nesting here encodes control
supersession, which a pure subset model cannot express.

## Transfer to LTA-SSP
1. **Validate our own nesting claim against the supersession failure mode.** We established
   that low ⊂ medium ⊂ high cloud with zero controls unique to the lower tier. ASD's data is
   the counter-example that tells us what that claim is worth: nesting is a *contingent
   property of our current data*, not a law of control frameworks, and it breaks precisely
   when a stricter control replaces a laxer one. Any diff-based representation we build
   (PA-001's `import: low-risk-cloud` idea) must therefore support removal, not only
   addition — OSCAL's `exclude-controls` exists for exactly this. If we hardcode
   "higher tier = lower tier + extras", the first SSP revision that supersedes a control
   will silently corrupt the profile pages. Worth adding a build-time assertion over
   `docs/assets/data/profiles.json` that re-checks nesting rather than assuming it.
2. **The props-plus-generated-profiles pattern is directly adoptable and cheap.** ASD keeps
   one source of truth (props on the control) and *generates* the per-baseline views. Our
   `controls.json` / `profiles.json` split is the mirror image — profile-as-truth,
   control-as-level-free — and both work, but ASD's ordering has a concrete advantage for a
   static site: the control record is self-describing, so the controls page can render "this
   control applies to: low, medium, high cloud" badges from a single fetch, without joining
   against eight profiles client-side. Given `controls.js` already fetches both, the cheap
   move is not to change the source of truth but to copy the *invariant*: whichever is
   canonical, the other must be exactly derivable, and that derivation should be checked, not
   assumed.
3. **Multi-valued applicability is the honest encoding of a many-to-many.** ASD does not
   pick one classification per control; a control lists every classification it applies to.
   That is the same shape as our (system type, control, level) triple with the level
   promoted into the value — `{"name": "applicability", "value": "high-risk-cloud:L0"}` is a
   one-line generalisation that would let us keep a single flat list per control.
4. **A profile with no `modify` is a legitimate endpoint.** ASD, with a 1,150-control
   catalogue and national authority, uses none of OSCAL's parameter or alter machinery. That
   is a strong signal we should not build `set-parameter` support before we have a
   parameter to set.

## Limits
ASD publishes the *result* of the applicability decision, not the reasoning — nothing in the
catalog says why `ism-1873` is ML2 only, and there is no per-control justification field. It
therefore does not help with "explain WHY this control applies", which is our downstream
goal. Nor is there any system-typing step: the user must already know their system's
classification (a determination made under a separate Protective Security Policy Framework
document, not here), so like OSCAL it is machinery *after* the selection question. The
catalog is also 2.5 MB of JSON for 1,150 controls, roughly 2 kB per control; our 248
controls scale fine, but this confirms that shipping a whole catalogue plus every resolved
profile to the browser is viable only at our size, not theirs.

## Quotes
- Data model, from the repository README: "The ISM is provided as an OSCAL catalog with the
  use of OSCAL props for unique ISM attributes."
- Deliberate redundancy: "ASD also provides illustrative OSCAL profiles and OSCAL resolved
  profile catalogs for each ISM control's applicability (non-classified, OFFICIAL:
  Sensitive, PROTECTED, SECRET, TOP SECRET), as well as for Essential Eight Maturity Level
  One (ML1), Maturity Level Two (ML2) and Maturity Level Three (ML3). Importantly, to enable
  greater flexibility for consumers, and to align with the ISM's non-machine-readable
  documents, the information used to inform these profiles are also included in the source
  ISM catalog." (README)
- A superseded control, `ism-1695` statement text: "Patches, updates or other vendor
  mitigations for vulnerabilities in operating systems of workstations, non-internet-facing
  servers and non-internet-facing network devices are applied within one month of release."
  — carries `essential-eight-applicability` ML1 and ML2, and is absent from ML3.
- Profile shape, `ISM_PROTECTED-baseline_profile.json`: a single import
  (`"href": "#36766a6f-e174-4292-a03e-fcb3b4b09201"`) with one `include-controls` block of
  1,035 `with-ids`, `"merge": {"as-is": true}`, and no `modify`.
- Measured (this survey, from the published JSON): profile membership equals prop-derived
  membership for all 8 baselines; subset relation holds only for OS ⊆ P and ML1 ⊆ ML2.
