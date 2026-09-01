---
id: F-006
title: An official OSCAL source exists, but covers only half the corpus and is stale
date: 2026-09-01
rq: [RQ-5, RQ-4]
implications: [data, site, classifier]
confidence: high
status: open
---

## Observation

**<https://github.com/GovTechSG/tech-standards>** (MIT, 33 stars, created 2024-07-30, last push
2025-09-02) publishes the IM8 control framework as **OSCAL 1.1.2**.

- `catalogs/im8-reform.json` — OSCAL catalog "Instruction Manual 8 Reform", version 2025.05.13.
  15 groups, **137 controls**. Each control carries a `statement` part, a `guidance` part, a
  `risk-statement` prop, `links` to the source IM8 clauses (e.g. "IM8 Cloud Security (IaaS and
  PaaS): 1.1/G1"), and published / last-modified props.
- `profiles/{low,medium}-risk-level-{0,1,2}.json` — **6 profiles only**.

### What it does not cover

| | ours | OSCAL |
|---|---|---|
| controls | 248 | 137 |
| domains / groups | 26 | 15 |
| GA (Generative AI) group | 8 controls | **absent** |
| DSS / WCAG groups | 9 domains, 92 controls | **absent** |
| profiles | 8 system types | 6 (low/medium risk × L0/L1/L2) |
| high-risk, on-prem, sandbox, gen-ai, dss profiles | present | **absent** |

### Drift

The catalog is dated 2025-05-13; the live site's GenAI page says last updated 2026-03-24. Counts
have already diverged: OSCAL `lm` 20 vs our 21, `pm` 8 vs our 10, and the site's low-risk-cloud
page lists AS=15 against OSCAL's `as`=14.

### Layering precedent

OSCAL profile imports are **cumulative**: `low-risk-level-1` imports `trestle://profiles/
low-risk-level-0.json` plus the catalog; `low-risk-level-2` imports level-1. GovTech models
layering through OSCAL imports — but only **across levels within a risk tier**, never across
system types.

## Evidence

- Repository, catalog and profile files as cited above, retrieved 2026-09-01
- Comparison against `python research/scripts/corpus.py stats` / `domains`, repo @ `4e7e6ba`
- Context: NIST hosts a GovTech Singapore talk, "Adapting OSCAL for the Singapore Government's Tech
  Standards" (csrc.nist.gov, 2025-01-15). Not extractable as text in this pass — no claims drawn
  from it.
- Not findable by GitHub repo-name search within the org; located via web search. Name-based repo
  search in this org is unreliable.

## Interpretation

This is the most consequential result of the verification pass, and it cuts three ways.

**It corroborates F-005 independently.** GovTech expresses level tiers as *cumulative profile
imports* — level-1 imports level-0 rather than restating it. That is the same nesting our subset
checks found in the scraped data, arrived at from the other direction. The nesting is therefore a
deliberate design property of the standard, not an artefact of how these particular templates were
authored — which was an open question in F-005 and is now closed.

**It does not rescue the corpus.** Coverage is roughly half, it is stale relative to the live site,
and its counts have already drifted. It cannot be a drop-in replacement, and it cannot supply GA or
DSS content at all. Anyone reaching for "just use the official data" should read the coverage table
above first.

**It cannot settle F-002.** With no gen-ai profile and no GA group, the OSCAL source is silent on
exactly the question we most needed answered.

Separately, the `risk-statement` prop being distinct from `guidance` confirms that our local
`guidance` field is the *website's* concatenation of two upstream fields, not a single authored
block.

## Implications

- **data:** Do not treat this as an import source without an ADR. The realistic options are
  (a) scrape the live site, which is current but unstructured; (b) import OSCAL, which is
  structured but partial and stale; (c) hybrid — OSCAL for the 15 covered groups, scrape for GA and
  DSS. Each has a different failure mode and (c) risks two sources drifting apart.
- **classifier:** OSCAL's `links` to source IM8 clauses are provenance our scrape does not have,
  and its `risk-statement` prop is independently queryable. Both are useful features that would
  otherwise need deriving.
- **site:** The cumulative-import model is a validated precedent for presenting nested profiles as
  increments rather than flat lists (see F-005's site implication). GovTech already models the data
  that way; our UI does not.
- **RQ-4:** Raises the priority of the OSCAL angle considerably. This is no longer a foreign
  standard we might borrow from — it is the format the publisher already uses for this exact
  corpus.

## Open questions

- Why does the OSCAL catalog omit GA and DSS entirely — out of scope for that repo, or simply not
  migrated yet? Its last push (2025-09-02) is recent enough that the omission looks deliberate.
- Is the catalog still maintained, given the live site has moved further ahead?
- Does the NIST talk explain the intended scope? Worth a human watching it.
