---
id: PA-011
title: CSA Cloud Controls Matrix v4.1 — service-model applicability and Shared Security Responsibility Model ownership
source: https://cloudsecurityalliance.org/artifacts/introductory-guidance-to-ccm
kind: standard
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
A cloud-specific control framework — 207 controls across 17 security domains in v4.1 — whose
distinguishing feature is that each control carries **two orthogonal applicability
dimensions** beyond the control text: which cloud service model it applies to (IaaS / PaaS /
SaaS), and *who implements it* (provider or customer). It is the only source in this survey
that treats "who is responsible" as first-class catalogue data, and its domain count (17) is
coincidentally identical to our 17 cybersecurity domains.

## Mechanism
**Dimension 1 — service model.** A control applicability matrix marks each control against
IaaS, PaaS and SaaS. A control can apply to some models and not others, so "which controls
apply to me" is partly answered by a lookup on what kind of cloud service is in question,
without any risk assessment at all.

**Dimension 2 — SSRM ownership.** Each control gets one of four designations:
- *CSP-owned* — the provider is fully responsible.
- *CSC-owned* — the customer is fully responsible.
- *Shared (Independent)* — both parties implement comparable controls independently.
- *Shared (Dependent)* — one party's implementation depends on the other's capabilities.

The four-way split is more expressive than a binary. The important distinction is
*Independent* vs *Dependent*: independent means two parallel implementations that do not need
to be coordinated; dependent means the customer cannot implement without something the
provider supplies, which is a prerequisite relationship and therefore an integration risk. The
designations are described as typical allocations rather than fixed facts — actual ownership
"varies from service to service, depending on the cloud service model and the implementation."

**The questionnaire layer.** CAIQ turns the control specifications into 283 assessment
questions, and the relationship "between a CCM control and CAIQ questions is often one to
many" — i.e. a control decomposes into several yes/no questions rather than mapping to one.
CSA's stated purpose for CAIQ is that CSPs use it to communicate SSRM ownership and guidance
to their customers, so the questionnaire is a *disclosure* instrument, not a scoping wizard.

**The guidance layer.** Two companion documents sit beside the control text: Implementation
Guidelines giving "suggestions, recommendations and examples of how to implement the CCM
controls", and Auditing Guidelines giving "assessment guidelines per CCM v4 control
specifications". Guidance is thus a separate, separately-maintained artefact keyed by control
id — not prose inside the control.

## Transfer to LTA-SSP
1. **This is the concrete design for the inheritance gap identified in PA-005.** 800-53B names
   common/inherited controls but leaves them as a process concept; CCM makes ownership a
   *column*. For a Singapore government SSP tool, where a large share of controls for a
   cloud-hosted system are in practice discharged by the platform or by a central agency
   service, adding an ownership field to `docs/assets/data/controls.json` — with CSA's
   four values, not a boolean — would change what the tool is for: from "here are 180
   controls" to "here are the 60 you actually have to do". That is the highest-leverage
   single field identified in this survey.
2. **Two orthogonal applicability axes, again.** CCM independently reaches the structure argued
   from overlays (PA-006) and from the GOV.UK split (PA-008): applicability is not one
   classification but several. Ours would plausibly be (system type axis) × (risk tier axis) ×
   (ownership axis). Since our profiles nest on the risk axis and our two Digital Services
   profiles differ only by level, a multi-axis model fits our measured data better than 8
   flat leaves.
3. **Service model as a worked precedent for "my system is two things at once."** A system
   that is PaaS-hosted but exposes a SaaS front end simply matches on both columns and takes
   the union — no tie-break needed, because applicability is a set-membership test per axis
   rather than a classification into one bucket. This is the cheapest available fix to the
   wizard's single-answer limitation, and it needs no new data beyond flags we would author
   anyway.
4. **Keep guidance in a sibling file keyed by control id.** CSA separates control text,
   implementation guidance and audit guidance into distinct artefacts. Our
   `docs/assets/data/*.json` must stay a faithful scrape of the upstream standard, so any
   guidance we author *cannot* live in it. CCM shows the standard-conforming alternative: a
   separate guidance file joined on control id, which keeps the scrape clean and makes the
   provenance boundary visible in the file layout.
5. **One control → many questions is the right cardinality for a wizard.** CAIQ's one-to-many
   decomposition is the opposite of our 7-questions-to-one-answer tree. If we ever build
   self-assessment, the unit should be a question per checkable claim, with several rolling up
   to a control — which also gives partial credit for free, as in CAF's IGP tables (PA-002).

## Limits
CCM is cloud-specific and its two axes are cloud-specific: IaaS/PaaS/SaaS does not generalise
to our Digital Service Standards half, and nothing here addresses non-cloud systems. The SSRM
designations are explicitly *typical* allocations, so they are a starting point a customer must
still confirm against their actual contract — meaning the field is advisory, and presenting it
as authoritative would be a misuse we would have to guard against in the UI. CCM also gives no
risk-tiering at all: there is no notion of a low/medium/high variant of the catalogue, so it
solves the *who* and *which service model* questions while leaving *how stringently*
completely open — the mirror image of CAF (PA-002), which solves stringency and ignores
system typing. And CAIQ is a provider-disclosure questionnaire aimed at procurement, not a
tool for a system owner discovering their own obligations, so its 283 questions are not a
model for our wizard's content.

## Quotes
- Scale: "The CCM v4.1 is structured into 17 security domains and 207 controls."
- Ownership as data: "Common SSRM ownership designations allocate responsibilities typical for
  implementing a given CCM control between a CSP and a CSC."
- Ownership is contextual, not fixed: "The SSRM control ownership varies from service to
  service, depending on the cloud service model and the implementation."
- Decomposition cardinality: "The relationship between a CCM control and CAIQ questions is
  often one to many."
- Separate guidance artefacts: Implementation Guidelines provide "suggestions, recommendations
  and examples of how to implement the CCM controls"; Auditing Guidelines provide "assessment
  guidelines per CCM v4 control specifications".
- The four ownership values, as enumerated in the guidance: CSP-Owned (provider fully
  responsible), CSC-Owned (customer fully responsible), Shared (Independent) (both parties
  independently implement comparable controls), Shared (Dependent) (one party's implementation
  depends on the other's capabilities).
