---
id: F-002
title: The generative-ai profile is 9 controls and upstream never says whether it stands alone
date: 2026-09-01
updated: 2026-09-01
rq: [RQ-5, RQ-2]
implications: [data, site, classifier]
confidence: medium
status: open
site_issue: deferred
---

> **Revised twice (2026-09-01).**
> *First* — after upstream verification: the standard does not state the template is additive; it
> frames GenAI exactly like the standalone types.
> *Second* — after domain confirmation from the project owner: composition **is permitted but not
> required**. An agency may adopt the GenAI or Digital Services template alongside a hosting SSP,
> or may judge it sufficient alone.
> This retires the "materially unsafe" framing I originally used. The wizard is **incomplete**, not
> wrong: it cannot express a legitimate combination. That is a usability defect, not a safety one.
> Confidence, title, and implications revised accordingly.

> **Known site issue, deliberately deferred (2026-09-01).** Answering "yes" at wizard q3 terminates
> with 9 controls and no hosting profile, and the wizard offers no way to say "GenAI *and*
> cloud-hosted". Since composition is permitted rather than required, this is a usability defect —
> the tool cannot express a valid answer — not under-protection. Deferred under the research-only
> decision; recorded so it is not lost.

## Observation

`profiles.json["generative-ai"]` contains 9 controls. Its peers contain 92-137.

The 9 are the **entire `GA` domain plus one control from `DP`**:

```
GA-1 L0  Overseas-hosted GenAI API services
GA-2 L0  Singapore-hosted GenAI API services
GA-3 L0  Non-logging and non-training Agreement
GA-4 L0  Data classification for self-hosted GenAI models
GA-5 L1  GenAI model formats and loaders
GA-6 L1  File upload safeguards
GA-7 L1  Evaluation of GenAI accuracy, safety, and output quality
GA-8 L1  Inform users about GenAI risks and limitations
DP-8 L1  Data Classification Disclosure
```

The `GA` domain has exactly 8 controls; all 8 are here. `system-types.json` declares
`domainsUsed: ["DP", "GA"]` and `levelsAvailable: [0, 1]` — the only type with no Level 2.

It contains no access control, no logging, no network security, no backup — nothing a running
system needs.

## Upstream evidence (verified 2026-09-01)

**Against the overlay reading — the page frames GenAI as a peer, not a modifier:**

- <https://info.standards.tech.gov.sg/ssp/gen-ai/>: "The Generative AI System Security Plan
  template includes Level 0 and Level 1 baseline controls that are recommended as the default
  controls for systems that utilise generative AI models." / "Agencies may customise this template
  ... or use it as a default System Security Plan for generic Generative AI systems."
- That is the **same boilerplate sentence pair** as `/ssp/low-risk-cloud/`. GenAI also carries its
  own System Characteristics block with a sensitivity level ("Up to Confidential, Sensitive High"),
  exactly like the standalone types.
- No additive or "in addition to" wording anywhere on `/ssp/`, `/ssp/gen-ai/`, `/about/`, or
  `/control-catalog/`.

**For the overlay reading — a single within-control pointer:**

- GA-4 guidance, <https://info.standards.tech.gov.sg/control-catalog/cybersecurity/ga/>: "Refer to
  relevant IM8 SSPs for controls that need to be met before hosting government data of a given
  data classification in that environment (e.g. in a Singapore-hosted GCC environment.)"

**The official OSCAL source cannot settle it** — `GovTechSG/tech-standards` ships only 6 profiles
(low- and medium-risk × levels 0/1/2). There is no gen-ai profile, and the catalog has no GA group
at all (see F-006).

## Evidence

- `python research/scripts/corpus.py profile generative-ai`
- `python research/scripts/corpus.py domain GA`
- `python research/scripts/corpus.py stats` (9 controls; L0=4, L1=5, L2=0)
- Upstream pages above, retrieved 2026-09-01
- repo @ `4e7e6ba`

## Resolution (2026-09-01, project owner)

**Composition is permitted but not required.** The GenAI and Digital Services templates may be
adopted alongside a hosting SSP; an agency may also judge the template sufficient on its own. The
standard does not mandate either.

## Interpretation

**Upstream is silent, and the silence is what the tool has to handle.** The published pages frame
this template like the standalone types while giving it contents that cannot function as a complete
baseline: 9 controls, no access control, no logging, no network security, no backup — for a
template whose own System Characteristics block admits data up to "Confidential, Sensitive High".
The GA-4 pointer to "relevant IM8 SSPs" is the only published hint that anything further is
expected.

Given composition is optional, the consequence is not that users are misled into under-protection —
it is that **the standard leaves a judgement call unsupported, and our tool currently hides it**.
A user who should be combining templates gets no prompt to consider it, and no way to express it if
they do.

That reframes the problem usefully. The site's job is not to assert composition, nor to stay
silent. It is to **surface the choice**: show the 9 GenAI controls, note that a hosting profile may
also apply, and let the user say so. That is defensible under either reading and it is what
"permitted but not required" actually calls for.

**Composition is mechanically trivial here.** The 9 GenAI controls appear in no other profile, and
no DSS control appears in any non-DSS profile — the sets are fully disjoint, so combining an
overlay with a hosting profile is a plain union with no level conflicts to resolve (see F-005,
F-007).

## Implications

- **site:** The wizard routes GenAI as a **terminal** answer — q3 → yes → done — and cannot express
  "GenAI *and* cloud-hosted", which is a legitimate combination. The fix is to let the user select
  multiple applicable characteristics and to surface the hosting question rather than skipping it.
  This is the concrete case for the tick-all-that-apply model in F-007.
- **classifier:** Keep the output schema as `(base_type, overlays[], confidence)`, now on firmer
  ground: composition is a real, permitted state of the world, so a single-label schema would be
  unable to represent valid answers. `overlays[]` expresses standalone (empty) and composite alike.
- **eval:** Because composition is optional, a GenAI case has **more than one correct answer** —
  `generative-ai` alone and `generative-ai + <hosting>` are both defensible. This is exactly what
  `acceptable_types` exists for, and the pilot must exercise it.
- **data:** Nothing to fix in `profiles.json`; the corpus faithfully reproduces upstream. The
  optionality is a property of the standard, not a defect in the scrape.

## Open questions

- The Digital Services types have *even less* textual support than GenAI for the composition
  reading: their pages scope themselves purely by traffic volume, with no outward pointer at all,
  not even a GA-4 equivalent. Optionality is assumed to apply to them equally — worth confirming.
- Is there guidance anywhere on *when* an agency should combine rather than stand alone? That
  judgement is exactly what the site could help with, and nothing published addresses it.
- Does the NIST talk "Adapting OSCAL for the Singapore Government's Tech Standards"
  (csrc.nist.gov, 2025-01-15) address composition? Not extractable as text in this pass.
