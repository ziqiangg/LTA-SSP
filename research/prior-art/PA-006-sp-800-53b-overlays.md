---
id: PA-006
title: NIST SP 800-53B Appendix C — Overlays as composable, community-authored control specialisations
source: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53B.pdf
kind: standard
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
The appendix that introduces *overlays*: reusable, publishable control specialisations aimed
at a community of interest, a technology, an environment, a mission, a threat, or a statute.
It is the mechanism NIST reaches for when the baseline-per-impact-level model runs out —
which is precisely where our 8-system-type model runs out. Filed separately from PA-005
because it answers a different question: PA-005 is how *one* system deviates from a baseline;
this is how a *class* of systems does, reusably.

## Mechanism
An overlay is either a fully specified control set derived by applying tailoring guidance to a
baseline, or a set derived independently of any baseline. It does three things: lets a
community **add, modify, or eliminate** controls; supplies **applicability and
interpretations** for specific technologies, computing paradigms, environments, system types,
mission types, operating modes, industry sectors and statutory requirements; and fixes
**parameter values** the community agrees on.

The key structural rule is a scope constraint: overlays target *groups* of like technologies,
systems, or communities — explicitly **not** an individual system, because per-system
adaptation is what tailoring is for. So NIST draws a hard line between the reusable artefact
(overlay, authored once by experts, consensus-built, published) and the per-instance artefact
(tailoring, authored by the system owner, justified in the SSP). Overlays may themselves
require subsequent tailoring; the two compose in that order.

NIST enumerates seven overlay *categories* — community/sector (healthcare, law enforcement,
finance, transportation, energy), technology/computing paradigm (virtualised, cloud, mobile,
smart grid, cross-domain), environment of operation (space, tactical, sea), system type and
operating mode (ICS, weapons, single-user, stand-alone, IoT), mission type, threat type (APT,
insider), and statutory/regulatory (HIPAA, FISMA, Privacy Act). These axes are deliberately
orthogonal: a system can sit under several at once.

Overlays are given a standard document outline — Identification, Overlay characteristics,
Applicability, Overlay summary, Overlay control specifications, Tailoring considerations,
Terms and definitions, Additional information — and a distribution channel: NIST's Security
Control Overlay Repository (SCOR), a voluntary sharing platform with published submission
instructions. Overlays may also ship inside other publications (SP 800-82 for ICS is the cited
example of a fully specified one).

The stated trigger for reaching for an overlay is diagnostic: use one "when there is
divergence from the basic assumptions used to create the initial control baselines".

## Transfer to LTA-SSP
1. **This is the cleanest published answer to "my system is two things at once."** Our wizard
   returns exactly one of 8 system types and cannot express a system that is, say, a
   high-risk cloud system *that is also a public-facing digital service*. The overlay model
   says: don't add a ninth type — keep one baseline and layer independently-authored,
   independently-applicable overlays. Because our profiles nest along the risk axis and the
   Digital Services profiles differ from the cloud ones on a genuinely different axis (the
   two DS profiles have identical control sets differing only by level), our 8 types are
   almost certainly better modelled as *2 axes* than 8 leaves: a risk-tier baseline plus a
   "is a digital service" overlay carrying the 9 DSS/WCAG domains. That is a
   `docs/assets/data/profiles.json` restructure, and it would let the wizard ask two
   independent questions instead of walking a 7-question tree to a single leaf.
2. **The add/modify/eliminate triple is the minimum verb set for any diff format we build.**
   PA-004 showed removal is real (control supersession), and this confirms NIST expects
   overlays to eliminate as well as add. Any nested/incremental profile representation we
   adopt from PA-001 needs all three verbs, not just "extends".
3. **The reusable/per-instance split is a scoping decision for the whole project.** Our site
   can legitimately publish the *overlay* layer — expert-authored, applies to a class,
   stable, static-site-friendly. It cannot and should not attempt the *tailoring* layer,
   which is per-system, requires justification and an approving official, and is inherently
   stateful. This is a clean answer to how far a zero-dependency browsing tool should go:
   ship the class-level artefact, hand off at the instance boundary. Worth recording as an
   ADR.
4. **The seven overlay categories are a candidate label set for the future free-text
   classifier.** A user's description of their system ("a public-facing mobile app for
   healthcare appointments hosted on commercial cloud") maps far more naturally onto
   several of sector / technology / environment / system type than onto one of 8 profiles.
   Multi-label over ~7 orthogonal axes is also a much better-posed learning problem than
   single-label over 8 entangled ones.
5. **SCOR is the model for how our research findings could ship.** A published overlay
   outline plus a repository is exactly the form in which "we found the SSP under-specifies
   X" could become a durable artefact rather than a journal entry.

## Limits
NIST gives the outline and the categories but no *composition semantics*: nothing says what
happens when two overlays disagree about the same control, which is the first hard problem
you hit the moment you allow more than one. (OSCAL's `combine/@method` in PA-001 is the only
place that conflict is mechanised, and its default — `keep` — knowingly produces invalid
output.) There is also no guidance on how a system owner *discovers* which overlays apply to
them; SCOR is a repository you browse, not a recommender, so the selection problem is
restated one level up rather than solved. Overlays are voluntary and unevenly authored, so in
practice coverage is thin outside a few sectors. And the explicit exclusion of individual
systems means the mechanism cannot be stretched to cover the per-system question our
downstream free-text tool is really being asked.

## Quotes
- Definition (Appendix C): "An overlay may be a fully specified set of controls, control
  enhancements, and other supporting information (e.g., parameter values) that is derived from
  the application of tailoring guidance to control baselines or it may be derived
  independently of control baselines."
- The three functions: overlays "complement and further refine control baselines by:
  • Providing an opportunity for the community of interest to add, modify, or eliminate
  controls • Providing control applicability and interpretations for specific technologies,
  computing paradigms, environments of operation, types of systems, types of
  missions/operations, operating modes, industry sectors, and statutory/regulatory
  requirements • Establishing parameter values for assignment and selection operations in
  controls and control enhancements that are agreeable to communities of interest"
- The trigger: "Organizations use the overlay concept when there is divergence from the basic
  assumptions used to create the initial control baselines or when specific controls are
  needed to protect a particular technology or address a particular threat."
- The scope constraint: "The overlay concept is applicable to groups of like technologies,
  systems, or communities of interest (i.e., the overlay concept is not appropriate for an
  individual system since the tailoring process is used to adapt control baselines for
  individual systems)."
- Specificity is a free parameter: "Some overlays may be very specific with respect to the
  hardware, firmware, and software that form the key components of the targeted system types
  and the environments in which the systems operate. Other overlays may be more abstract in
  order to be applicable to a larger class of systems that may be deployed in different
  operational environments."
- Distribution: "The Security Control Overlay Repository (SCOR) provides stakeholders with a
  platform for voluntarily sharing security control overlays."
- Standard outline: "The example overlay outline includes the following sections:
  • Identification • Overlay characteristics • Applicability • Overlay summary • Overlay
  control specifications • Tailoring considerations • Terms and definitions • Additional
  information or instructions"
