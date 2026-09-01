---
id: PA-002
title: NCSC Cyber Assessment Framework — Introduction to the CAF
source: https://www.ncsc.gov.uk/collection/cyber-assessment-framework/introduction-to-caf
kind: gov-framework
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
The UK NCSC's outcome-based assessment framework for organisations with responsibility for
vitally important services. It is the closest peer to Singapore's SSP in role — a
government-published control set applied across heterogeneous systems — but it makes a
structurally different bet: instead of prescribing controls per system type, it prescribes
*outcomes* and delegates the "which apply to me, and how hard" question to a named
third party.

## Mechanism
Four nested levels: 4 high-level objectives → 14 principles → contributing outcomes →
Indicators of Good Practice (IGPs). The leaves produce 41 individual assessments.

The scoring surface is the interesting part. Each contributing outcome carries an *IGP
table* with columns for `achieved` (green), `partially achieved` (amber) and
`not achieved` (red). The columns are not symmetric in their evidentiary rules: for
`achieved`, **all** the indicators would normally have to be present; for `not achieved`,
the presence of **any one** indicator is normally sufficient. So the framework is
deliberately asymmetric — easy to fail, hard to pass — and `partially achieved` exists only
for some outcomes, not all.

The selection mechanism is the **CAF profile**. A profile is a per-outcome target vector:
for each of the 41 contributing outcomes, a target status of not achieved / partly achieved
/ achieved. NCSC explicitly does not author these. A *cyber oversight body* (a regulator or
lead department for a sector) sets target levels for organisations in its sector, choosing
which outcomes matter most for that sector's essential functions. This is the key design
move: the framework is sector-agnostic, and sector-specific stringency is a separate,
externally-owned artefact layered on top. MHCLG, for example, published a local-government
CAF profile built with councils.

NCSC repeatedly disclaims mechanical application: IGPs are explicitly *not* a checklist,
assessment requires expert judgement, and compensating measures can substitute for a
missing indicator when justified.

## Transfer to LTA-SSP
Three things are directly usable.

1. **Profile-as-target-vector, not profile-as-control-list.** A CAF profile does not select
   a subset of outcomes; it assigns a *target level* to every outcome, including "not
   achieved" for ones deemed out of scope. This is a strictly more expressive shape than
   ours and is what our data already secretly is — every SSP profile assigns a level in
   {0,1,2} to a control, and "absent" is really a fourth level. Making absence explicit
   (level `-`/`n/a` as a first-class value in `docs/assets/data/profiles.json`) would let
   the profile pages render *all 248 controls* with a status column, which is exactly the
   presentation that makes nesting visible: low-risk-cloud is the profile where more
   controls sit at "not applicable". It also removes a silent failure mode where a control
   missing from a profile is indistinguishable from a data-entry omission.

2. **The three-column IGP table as a design pattern for control guidance.** Our downstream
   goal is "controls plus guidance". CAF's answer to "what do I do about this control" is
   not prose — it is a small table of concrete indicators sorted into what good, partial and
   bad look like. That is renderable in static HTML on a control detail page and is far more
   actionable than a single paragraph. It also gives the user a self-assessment affordance
   with no backend.

3. **Naming the owner of the tailoring decision.** The SSP's one sentence ("agencies and
   their industry partners are required to assess the risks...") is an unowned instruction.
   CAF makes the same delegation but names the role (cyber oversight body) and the artefact
   (a published sector profile). If our tool cannot answer "which system type am I", it can
   at least say *who decides* and *what the output of that decision looks like* — a much
   more honest wizard endpoint than a confident single answer from 7 questions.

Must reject: the outcome-based structure itself. CAF has 41 assessment points; the SSP has
248 discrete controls with binary-ish applicability. We cannot re-cast the SSP as outcomes
without authoring content we have no authority to author.

## Limits
CAF solves *how stringent*, not *which system*. There is no system-typing step at all — the
unit of assessment is an organisation and its essential function, not a system, so it has
nothing to say about our "this system is two things at once" problem. It also pushes the
hard decision entirely off-framework: NCSC states plainly it is not their responsibility to
mandate what is appropriate, which means the actual selection guidance lives in ~a dozen
sector profiles of varying quality rather than in the framework. And the explicit
anti-checklist stance is in tension with what a browsing tool does — a tool that shows you a
definitive list of applicable controls is doing the thing CAF warns against.

## Quotes
- "all the indicators would normally be present" — the evidentiary bar for a GREEN
  ('achieved') rating. (Assessment Levels)
- "presence of any one indicator would normally be sufficient" — the bar for RED
  ('not achieved'). (Assessment Levels)
- Partial credit is defined by benefit, not completeness: AMBER indicates progress
  delivering "specific worthwhile cyber security and resilience benefits". (Assessment
  Levels)
- "IGPs do not remove the requirement for the informed use of cyber security expertise and
  sector knowledge." (Outcome-Based vs. Prescriptive Approach)
- IGPs are not "a checklist to be used in an inflexible assessment process." (Outcome-Based
  vs. Prescriptive Approach)
- Ownership of tailoring: "a cyber oversight body will need to set target levels of cyber
  resilience for organisations within their sector", and such CAF profiles represent "a
  mixture" of outcomes at different achievement levels identified as "most important" for
  that sector's essential functions. (Tailoring Through Profiles and Oversight Bodies)
- "It is not the responsibility of the NCSC to mandate what represents appropriate and
  proportionate cyber security and resilience." (Tailoring Through Profiles and Oversight
  Bodies)
