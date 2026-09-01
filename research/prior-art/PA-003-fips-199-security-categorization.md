---
id: PA-003
title: FIPS 199 — Standards for Security Categorization of Federal Information and Information Systems
source: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.199.pdf
kind: standard
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
The mandatory US federal standard that turns "I have a system" into a categorisation, which
in turn selects a control baseline. It is the *upstream half* of the mechanism OSCAL
(PA-001) implements downstream: FIPS 199 decides which baseline you are in, OSCAL resolves
what that baseline contains. It is seven pages of normative text and is the most compact
worked example of selection guidance found in this survey.

## Mechanism
Categorisation is a two-stage composition, not a decision tree.

**Stage 1 — categorise each information type.** For each *information type* resident on the
system, assign a potential impact of LOW / MODERATE / HIGH (or NOT APPLICABLE, permitted for
confidentiality only) to each of three security objectives. The result is written in a fixed
notation:

    SC information type = {(confidentiality, impact), (integrity, impact), (availability, impact)}

The impact levels are defined by *consequence severity*, not by technology: limited /
serious / severe-or-catastrophic adverse effect on organisational operations, assets, or
individuals. Each level carries an AMPLIFICATION paragraph giving four concrete
manifestations (degradation of mission capability, damage to assets, financial loss, harm to
individuals), which is what makes the level assignable by a non-specialist. NIST SP 800-60
supplies a catalogue of common federal information types pre-mapped to *provisional* impact
levels, which agencies adjust for mission context — so the actual first move is lookup, not
judgement.

**Stage 2 — compose into a system category by high water mark.** The system's impact value
for each objective is the **maximum** of that objective's values across every information
type on the system, taken objective-by-objective rather than as a whole vector. The result
is a per-objective triple, and NOT APPLICABLE is forbidden at system level — a low water
mark of LOW applies to every objective because the system's own processing functions must be
protected regardless of what data it holds.

Two properties of the composition are worth naming. It is **objective-wise**, so a system
can be {C: LOW, I: HIGH, A: HIGH} — a shape no single information type on it necessarily
had. And the result is **explicitly overridable upward**: in the standard's own SCADA
example (Example 5), management raises confidentiality from LOW to MODERATE after the
mechanical high-water-mark computation, and the standard presents this as correct practice,
not as an exception. Categorisation is a floor with a documented adjustment step, not an
oracle.

## Transfer to LTA-SSP
This is the best available answer to the wizard's worst limitation — that it returns exactly
one system type and cannot express a system that is two things at once.

1. **Replace "pick one type" with "declare your components, take the max."** FIPS 199's
   insight is that a system is a *bag of things with impacts*, and the system's requirement
   is the pointwise maximum over the bag. Our profiles provably nest
   (low ⊂ medium ⊂ high cloud), which means our levels are already totally ordered, which
   means a high-water-mark join is *well-defined for us* in a way it would not be for
   unordered profiles. Concretely, in `docs/assets/js/wizard.js`: let the user tick every
   description that applies rather than walking a 7-question tree to one leaf, then resolve
   the answer as max(level) per control across the selected types. Because the cloud
   profiles nest, selecting {low-risk-cloud, high-risk-cloud} correctly yields
   high-risk-cloud rather than nonsense.
2. **Separate the axis of severity from the axis of technology.** Our 8 system types
   conflate "what kind of thing is it" (cloud / digital service) with "how bad if it
   fails" (low / medium / high risk). FIPS 199 keeps these orthogonal: information type is
   the what, impact is the how-bad. Splitting our wizard into two independent questions
   would give 8 combinations from ~4 answers and make the nesting explainable rather than
   memorised.
3. **Steal the AMPLIFICATION pattern for the wizard's question text.** The reason FIPS 199
   levels are assignable by non-experts is that each level is defined by four concrete
   consequences. Our wizard currently asks classification-style questions; rewriting the
   risk-tier question as "if this system leaked, would the effect be limited / serious /
   severe" with the four amplifications underneath is a pure copy-editing change to
   `wizard.js` with no data-model cost.
4. **Show the override.** Example 5's upward adjustment is a licence to present the wizard
   result as a *starting point with a documented raise step*, which is both more honest and
   closer to what the SSP's one sentence about risk assessment actually asks for.

## Limits
FIPS 199 gives no mechanism for the *downward* direction — there is no sanctioned way to
lower a category, only to raise it, so it cannot help a user argue a control out of scope.
It also stops at three coarse levels and one triple; all the real difficulty is pushed into
SP 800-60's information-type catalogue, which is a large separate document we have no
equivalent of (the SSP has no notion of "information type" at all, so stage 1 has no direct
analogue in our data). The high-water-mark rule is also famously conservative — a single
sensitive record drags an entire system to HIGH — which is precisely the criticism that
motivated FedRAMP's LI-SaaS carve-out and NIST's later overlay work. Finally it addresses
categorisation only; the mapping from category to baseline lives in SP 800-53B, not here.

## Quotes
- Notation: "The generalized format for expressing the security category, SC, of an
  information type is: SC information type = {(confidentiality, impact), (integrity, impact),
  (availability, impact)}, where the acceptable values for potential impact are LOW,
  MODERATE, HIGH, or NOT APPLICABLE." (Security Categorization Applied to Information Types)
- NA is confidentiality-only: "The potential impact value of not applicable only applies to
  the security objective of confidentiality." (footnote 4)
- The composition rule: "For an information system, the potential impact values assigned to
  the respective security objectives (confidentiality, integrity, availability) shall be the
  highest values (i.e., high water mark) from among those security categories that have been
  determined for each type of information resident on the information system." (Security
  Categorization Applied to Information Systems)
- The floor: "Note that the value of not applicable cannot be assigned to any security
  objective in the context of establishing a security category for an information system.
  This is in recognition that there is a low minimum potential impact (i.e., low water mark)
  ... due to the fundamental requirement to protect the system-level processing functions
  and information critical to the operation of the information system." (same section)
- Severity anchors, MODERATE: "The loss of confidentiality, integrity, or availability could
  be expected to have a serious adverse effect on organizational operations, organizational
  assets, or individuals." AMPLIFICATION lists "(i) cause a significant degradation in
  mission capability to an extent and duration that the organization is able to perform its
  primary functions, but the effectiveness of the functions is significantly reduced; (ii)
  result in significant damage to organizational assets; (iii) result in significant
  financial loss; or (iv) result in significant harm to individuals that does not involve
  loss of life or serious life threatening injuries."
- Sanctioned upward override (Example 5): after computing
  "SC SCADA system = {(confidentiality, LOW), (integrity, HIGH), (availability, HIGH)}",
  "The management at the power plant chooses to increase the potential impact from a loss of
  confidentiality from low to moderate reflecting a more realistic view of the potential
  impact ... The final security category of the information system is expressed as:
  SC SCADA system = {(confidentiality, MODERATE), (integrity, HIGH), (availability, HIGH)}."
- Non-uniform result shape (Example 4): "SC acquisition system = {(confidentiality,
  MODERATE), (integrity, MODERATE), (availability, LOW)}, representing the high water mark
  or maximum potential impact values for each security objective from the information types
  resident on the acquisition system."
