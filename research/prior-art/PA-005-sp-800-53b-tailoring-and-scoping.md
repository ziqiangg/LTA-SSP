---
id: PA-005
title: NIST SP 800-53B §2.4 — Tailoring Control Baselines (scoping considerations, compensating controls, parameters)
source: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53B.pdf
kind: standard
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
The chapter of NIST's baseline publication that tells an organisation what it is allowed to
do to a baseline after selecting one. Where FIPS 199 (PA-003) picks the baseline and OSCAL
(PA-001) mechanises the edit, this is the only source in the survey that writes down, in
normative prose, the *reasons* a control may be added, removed or weakened. It is the exact
document the SSP does not have.

## Mechanism
Tailoring is decomposed into six named activities, applied in a stated order (scoping →
compensating controls → parameters, with the note that parameters may be set first because
doing so can remove the need for a compensating control):

1. Identifying and designating **common controls** — controls *inherited* from another
   entity, which the system therefore need not implement itself. Hybrid controls (partly
   inherited, partly local) are explicitly allowed.
2. Applying **scoping considerations**.
3. Selecting **compensating controls**.
4. Assigning values to **organization-defined parameters** (assignment and selection
   operations).
5. **Supplementing** the baseline with additional controls and enhancements.
6. Providing **specification information** for implementation.

The scoping considerations are the load-bearing part — six enumerated grounds on which a
baseline control may be scoped out:

- *Implementation, applicability and placement*: controls apply only to system components
  that provide or support the function the control addresses (audit controls attach to
  auditing components, not every user endpoint).
- *Operational and environmental*: the baselines assume operational facts; where those are
  absent, tailoring is justified. A concrete list is given — mobile, single-user, air-gapped,
  low/sporadic bandwidth, cyber-physical/IoT, limited-functionality devices (fax, printer,
  camera), non-persistent/virtualised instantiations, and systems requiring public access.
- *Technology*: technology-specific controls (wireless, cryptography, PKI) apply only if
  that technology is present or required.
- *Mission and business*: controls that would degrade or endanger the mission may be
  inappropriate — subject to law and policy overriding.
- *Security objective*: a control supporting only one or two of C/I/A may be **downgraded**
  to the lower baseline's version when the high-water-mark categorisation was driven by a
  different objective. NIST then publishes the actual lists — the controls that support only
  confidentiality (AC-21, MA-3(3), MP-3…SC-4), only integrity (CM-5, SI-7, SI-10…), and only
  availability (a long CP-*/PE-* list). This is a **machine-usable dependency between the
  categorisation vector and individual controls**, not just advice.
- *Legal and policy*: controls meeting legal requirements are never tailored out, but a legal
  requirement that applies only in specified circumstances may be scoped out when those
  circumstances do not obtain.

**Compensating controls** are the escape hatch with a fixed four-step protocol: select from
the SP 800-53 catalog first; provide a rationale for how it satisfies the requirement *and*
why the baseline control could not be implemented; adopt from other sources only if the
catalog has nothing suitable; assess and accept the residual risk. More than one compensating
control may be needed to replace one baseline control.

Three constraints bound the whole process: organisations "do not arbitrarily remove"
controls; every control in the selected baseline must be **accounted for**, with tailored-out
controls' rationale recorded in the system security plan and approved by responsible
officials; and controls tied to applicable legislative, regulatory or policy requirements
cannot be tailored out at all.

## Transfer to LTA-SSP
1. **The scoping considerations are a ready-made taxonomy for "why doesn't this apply to
   me?"** Our tool currently answers "which controls apply" and stops. Six named, mutually
   comprehensible reasons — technology absent, component doesn't do that function,
   environment differs, mission conflict, objective not driving the category, circumstance-
   limited legal trigger — is a small enough vocabulary to render as a fixed set of chips on
   a control detail page, and small enough to be a classification target for a future
   LLM-assisted free-text tool. That is a far more tractable ML task than free-form
   justification generation: six labels, not open prose.
2. **"Every control is accounted for" is the strongest argument for rendering all 248.** NIST
   requires that a tailored-out control leave a trace. This converges with the CAF profile
   shape (PA-002): the useful artefact is not a filtered list but a full list with a status
   and a reason per row. For `docs/assets/js/controls.js` this means the profile view should
   default to showing every control with an applicability status rather than filtering the
   inapplicable ones out of the DOM — a presentation change, not a data change.
3. **Common/inherited controls are the missing concept in our model.** A large share of
   SSP controls for a cloud-hosted system will in practice be inherited from the platform.
   Our profiles have no way to say "this control applies to your system but someone else
   implements it", and that is probably the single most useful field a user of a *government
   agency* SSP tool would want. Adding an `inheritable: true` flag to controls would be a
   small `controls.json` change with disproportionate value, and it has NIST's vocabulary
   behind it ("common control", "hybrid control").
4. **The C/I/A-only control lists are prior art for a data-driven diff.** NIST ships the
   downgrade candidates as explicit control-id lists — a published, checkable artefact that
   makes a piece of tailoring guidance executable. If we ever want "here's what you can drop
   if availability isn't your concern", this is the form it should take: an id list in
   `docs/assets/data/`, not prose.
5. **Adopt the ordering claim.** Parameters before compensating controls, because completing
   the control definition may remove the need for the compensation. Cheap, and it is the kind
   of sequencing a wizard can encode for free.

## Limits
Every scoping consideration bottoms out in "an organizational assessment of risk" — 800-53B
tells you the *categories* of valid reason but never how to decide within a category, so it
is guidance for a security officer writing a justification, not an algorithm. It is also
addition-hostile in a specific way: the supplementation activity gets one bullet and no
guidance at all, so the standard is far better at licensing removals than at telling you what
to add. The whole chapter presumes a documented SSP with approving officials — the artefacts
it produces are for an accreditation process, not for a browsing tool, and a static site can
surface the vocabulary but can never perform the accountability step the standard actually
requires. Finally, the C/I/A downgrade lists are tied to SP 800-53 control ids and are not
transferable to our catalogue without a crosswalk we do not have.

## Quotes
- Activity list (§2.4): "The tailoring process can include but is not limited to the
  following activities: • Identifying and designating common controls • Applying scoping
  considerations • Selecting compensating controls • Assigning values to organization-defined
  control parameters via explicit assignment and selection operations • Supplementing
  baselines with additional controls and control enhancements • Providing specification
  information for control implementation"
- The bound on removal (§2.4): "However, organizations do not arbitrarily remove security and
  privacy controls from baselines. Tailoring decisions are expected to be defensible based on
  mission and business needs, a sound rationale, and explicit risk-based determinations."
- Accountability (§2.4): "Every control from the selected control baseline is accounted for by
  the organization. If certain controls are tailored out, the rationale is recorded in the
  system security and privacy plans and subsequently approved by the responsible officials
  within the organization as part of the approval process for the plans."
- The hard floor (§2.4, footnote 24): "It is inappropriate for organizations to tailor out
  security or privacy controls that pertain to applicable federal legislative, regulatory, or
  policy requirements."
- Common controls (§2.4): "Common controls are controls that may be inherited by one or more
  organizational systems. If a system inherits a common control provided by another entity
  (internal or external), there is no need to implement the control within that system."
- Applicability by component (Applying Scoping Considerations): "Controls in the initial
  baselines may not be applicable to every component in the system. Controls are applicable
  only to system components that provide or support the security or privacy functions or
  capabilities addressed by the controls."
- Technology gating: "Controls that refer to specific technologies—such as wireless,
  cryptography, or public key infrastructure—are applicable only if those technologies are
  implemented or required for use within organizational systems."
- Objective-based downgrade: "Controls that support only one or two of the security objectives
  (i.e., confidentiality, integrity, or availability) may be downgraded to the corresponding
  control in a lower baseline (or modified or eliminated if not defined in a lower baseline)
  only if the downgrading action reflects the [FIPS 199] security category for the supported
  security objectives before considering the [FIPS 200] impact level (i.e., high water mark),
  is supported by an organizational assessment of risk, and does not adversely affect the
  level of protection for the security-relevant information within the system."
- Published downgrade candidates: "Support Only Availability: CP-2(1), CP-2(2), CP-2(3),
  CP-2(5), CP-2(8), CP-3(1), CP-4(1), CP-4(2), CP-6, CP-6(1) … PE-15(1)".
- Compensating-control protocol: "Provide a rationale for how compensating controls satisfy
  security or privacy requirements and why the baseline controls could not be implemented."
- Not an exemption route (footnote 34): "Compensating controls are not used to avoid the need
  to comply with requirements. Rather, the use of such controls provides alternative and
  suitable security and privacy protections to facilitate risk management."
