---
name: prior-art-review
description: Run a literature or prior-art review for the SSP research — how other frameworks and tools solve control discovery, compliance UX, catalog crosswalks, or semantic retrieval over controls. Use when a research question needs external sources rather than the local corpus. Defines the search-screen-extract-synthesize workflow, the source-card template in research/prior-art/, and mandates delegating web reading to the literature-scout agent.
---

# Prior-art review

## The context rule

**Never fetch and read web pages in the main context.** Fetched pages are the largest context risk
in this project — a handful of them will crowd out everything else. Delegate the search-and-read
phase to the **`literature-scout`** agent, which writes source cards straight into
`research/prior-art/` and returns only a ranked list of what it filed. You then read the cards.

## Workflow

### 1. Frame
Write the question as something a source can answer or fail to answer. "How do other control
catalogs help a user narrow 248 controls to the ~100 that apply?" is answerable. "Research
compliance UX" is not. Record it against an RQ in `research/QUESTIONS.md`.

Decide up front what would change your mind — otherwise the review turns into confirmation.

### 2. Search
Dispatch `literature-scout` with the framed question, the specific angles to cover, and an
explicit stop condition (e.g. "8-12 cards, stop when sources start repeating"). Give it the
screening criteria below so it filters rather than hoarding.

**Running more than one scout at a time?** Assign each an explicit, disjoint `PA-NNN` range
(scout A owns 001-020, scout B owns 021-040). Otherwise both glob `prior-art/`, both see the same
highest id, and both start at the same number. Verification or fact-checking dispatches should be
told to file no cards at all.

Fruitful territory for this project:
- **Catalog standards** — NIST OSCAL (profiles, baselines, and its resolution model — it solves
  exactly the "level is a join" problem this corpus has), NIST SP 800-53B baselines, ISO 27001
  Annex A / Statement of Applicability.
- **Crosswalks** — Secure Controls Framework, CSA Cloud Controls Matrix, control mapping methods
  and their published error rates.
- **Tooling and UX** — how compliance platforms scope a control set from a system description;
  questionnaire vs. free-text vs. hybrid intake; how they explain *why* a control applies.
- **Retrieval** — semantic search and classification over regulatory or control text, and the
  known failure modes (near-duplicate controls, negation, jurisdiction-specific vocabulary).
- **Peer governments** — comparable national frameworks with published selection guidance, which
  is the thing this corpus most conspicuously lacks.

### 3. Screen
Keep a source only if it clears all three:
- **Relevant** — bears on control *discovery or selection*, not compliance in general.
- **Transferable** — its context is close enough to a public-sector control catalog to matter.
- **Substantive** — has a mechanism, a measurement, or a concrete design. Discard vendor pages
  that only assert benefits.

Record rejections in one line at the bottom of the synthesis. A reviewer needs to know what was
looked at and dropped.

### 4. Extract — one card per source

`research/prior-art/PA-NNN-slug.md`:

```markdown
---
id: PA-012
title: OSCAL profile resolution
source: https://pages.nist.gov/OSCAL/...
kind: standard          # standard | paper | tool | article | gov-framework
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high         # high | medium | low
---

## What it is
Two or three sentences.

## Mechanism
How it actually works. This is the part worth having — be concrete and specific.

## Transfer to LTA-SSP
What we could adopt, adapt, or must reject, and why. Name the file or behaviour it would touch.

## Limits
Where it does not apply, or what it leaves unsolved.

## Quotes
Short verbatim excerpts with locators, for anything you will later cite.
```

### 5. Synthesize
Write a finding (see the `research-note` skill) that answers the framed question across the cards.
It must:
- Cite cards by id (`PA-012`), not re-summarize them.
- Say where sources **disagree** — that is usually the useful part.
- Name what nobody solved. Gaps in the prior art are findings about our problem.
- Carry `implications:` tags, so the review changes something.

## Anti-patterns

- Collecting cards without synthesizing. An unsynthesized `prior-art/` is a bookmark folder.
- Letting the scout return page content instead of filing cards — that defeats the whole design.
- Treating a standard's existence as evidence it works. Look for evaluation, adoption, or
  reported failure.
- Reviewing until "done". Set the stop condition in step 2 and honour it.
