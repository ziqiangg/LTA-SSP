---
id: PA-012
title: ISO/IEC 27001 clause 6.1.3 and the Statement of Applicability
source: https://hightable.io/iso-27001-clause-6-1-3-information-security-risk-treatment/
kind: article
retrieved: 2026-09-01
rq: [RQ-4]
relevance: medium
---

## What it is
The clause of ISO/IEC 27001 that governs how an organisation decides which Annex A controls
apply to it, and the mandatory artefact — the Statement of Applicability — that records the
decision. It is the most widely practised control-selection procedure in the world, and it is
the only one in this survey where the *justification*, not the control list, is the deliverable.
(Sourced from a practitioner explainer, since the standard itself is paywalled; clause
lettering and required contents are quoted as reproduced there.)

## Mechanism
Clause 6.1.3 is a six-step sequence, and the ordering carries the whole design:

- **(a)** select risk treatment options from the risk assessment results;
- **(b)** "determine all controls that are necessary to implement the information security risk
  treatment option(s) chosen";
- **(c)** "compare the controls determined with those in Annex A and verify that no necessary
  controls have been omitted";
- **(d)** produce a Statement of Applicability;
- **(e)** formulate a risk treatment plan with actions, responsibilities, timelines, resources;
- **(f)** obtain risk owners' approval of the plan and acceptance of residual risk.

The crucial move is that (b) precedes (c). The organisation derives controls from its *own*
risks first, and Annex A is then used only as a **completeness check** — a catalogue you
compare against to catch omissions, explicitly not a menu you select from. This inverts the
baseline model of FIPS 199 / 800-53B (PA-003, PA-005), where you start from a prescribed set
and tailor down.

The **SoA** is the resulting inventory. It lists all 93 Annex A controls (2022 edition) and,
for each, states applicability, the justification for inclusion or exclusion, and the current
implementation status (operational or planned). Included controls must be justified by
reference to the identified risk or requirement driving them; excluded controls must be
justified by explaining why the risk genuinely does not arise. Practitioner guidance is sharp
about what survives audit: a specific contextual justification such as "Not applicable, the
organization holds no source code and performs no software development" against A.8.28, or
"We are a 100% remote company with no physical office" for physical controls, is defensible; a
bare "not applicable" or "not relevant to our business" is not.

The SoA and the risk treatment plan are complementary and both mandatory: the SoA records
*which* controls apply and why, the RTP records *how* and *when*, with an owner and a deadline
for each. Every control selected in the SoA must appear in the RTP.

## Transfer to LTA-SSP
1. **The SoA is the artefact our tool should be helping the user produce.** Our site currently
   ends at "here is your control list". Under an SoA model, the list is the *input* and the
   deliverable is a per-control applicability decision with a written reason. That reframing
   suggests a concrete, backend-free feature: render all 248 controls for a chosen system type
   with a status and a reason field, and let the user export it — a client-side generated
   table they take away, not state we store. This is the same "every control is accounted for"
   conclusion reached independently by 800-53B (PA-005), CAF (PA-002) and GOV.UK (PA-008), but
   with an actual document format attached.
2. **Justification quality is a teachable, checkable pattern.** The good/bad exclusion examples
   are a template: a defensible justification names a *fact about the system* ("no source
   code", "no physical office") from which non-applicability follows. That is exactly the
   structure the 800-53B scoping considerations enumerate (PA-005), and it is a realistic
   output target for a future LLM-assisted tool — generating "you said your system has no
   payment flow, so control X is out of scope" is a far more tractable and more verifiable
   task than deciding applicability outright. It also degrades safely: a bad justification is
   visible to a human reviewer, whereas a bad classification is not.
3. **Risks-first, catalogue-as-checklist is a defensible alternative framing for the wizard.**
   The SSP's one sentence of guidance ("agencies... are required to assess the risks and
   threats for each of their systems, to determine the controls required") is in fact the ISO
   6.1.3(b) instruction, not the NIST baseline instruction. Reading it that way, our wizard is
   arguably solving the wrong problem: the standard asks the agency to derive controls from
   risk and use the SSP as the completeness check. A "check my list against the SSP" mode —
   paste what you already plan to do, see what the SSP has that you have missed — would be
   closer to what the upstream standard actually asks for, and is implementable client-side.
4. **Implementation status belongs beside applicability.** ISO couples the two in one row.
   Cheap to adopt in a rendered table, and it is what turns a reference list into a working
   document.

## Limits
ISO gives no method for step (b) — "determine all controls that are necessary" is the entire
hard problem, restated as an instruction. The SoA is therefore a *documentation* standard, and
its rigour is procedural (an auditor checks that a justification exists and is specific), not
substantive (nobody checks it is correct). It also presumes a completed risk assessment,
named risk owners, and an approval step, none of which a public browsing tool can supply or
verify. The Annex A comparison step assumes the catalogue is small enough to review
exhaustively — 93 controls is reviewable, our 248 is borderline, and the practice does not
obviously scale. Finally, the SoA is organisation-scoped, not system-scoped: it covers an
ISMS, so it has nothing to say about a system being two things at once, and its
inclusion/exclusion is binary with no notion of levels, which our three-level data needs.

## Quotes
- Clause 6.1.3(b): "determine all controls that are necessary to implement the information
  security risk treatment option(s) chosen".
- Clause 6.1.3(c), Annex A as a checklist not a menu: "compare the controls determined with
  those in Annex A and verify that no necessary controls have been omitted".
- Clause 6.1.3(f): "obtain risk owners' approval of the information security risk treatment
  plan and acceptance of the residual information security risks".
- Required SoA contents: the necessary controls and their justifications, whether each is
  implemented or not, and the justification for excluding any Annex A controls.
- A defensible exclusion: "Not applicable, the organization holds no source code and performs
  no software development" (against A.8.28); and "We are a 100% remote company with no
  physical office" for physical security controls.
- An indefensible one: a bare "not applicable" without explanation, or a generic phrase that
  does not address why the risk genuinely does not exist in the environment.
- Division of labour: "The SoA documents which controls apply; the RTP details how and when
  they'll be implemented. Every control selected in the SoA must appear in the RTP with
  assigned owners and deadlines."
