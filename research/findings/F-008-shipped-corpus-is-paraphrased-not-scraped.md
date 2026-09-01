---
id: F-008
title: The shipped corpus is not a faithful scrape — most guidance text was paraphrased
date: 2026-09-01
rq: [RQ-5]
implications: [data, site, classifier]
confidence: high
status: actioned
supersedes_assumption: "docs/assets/data/*.json is a faithful scrape"
---

> **Actioned 2026-09-01.** The corpus was rebuilt from the verified scrape via
> `research/scripts/promote.py --apply`. Measured against the pre-rebuild corpus (git HEAD):
> **126 guidance fields corrected, 50 recovered from empty, 39 descriptions corrected, 34
> citations added or corrected, 4 titles restored to sentence case**, and `sourceUrl` /
> `retrievedAt` provenance added to all 248. Only 72 guidance fields were already correct.
> A re-run of `diff_corpus.py` now reports **zero differences** against upstream
> (`scrape-verify-2026-09-01-after.md`).
>
> The rebuild also fixed a lossy mapping the *original* corpus had: for DSS controls it stored
> only the upstream *Rationale* and silently dropped *Control Recommendations*, losing real
> content on all 92 — including BD-2's "Not required for…" exemptions. Guidance now carries both
> sections for every control. The project invariant in `CLAUDE.md`,
> `docs/CLAUDE.md` and `research/CLAUDE.md` was rewritten from *"the data is a faithful scrape"*
> (an assertion that was false) to *"the data must reproduce upstream and changes only through the
> ingest pipeline"* (a requirement to maintain).
>
> Scope at first promotion: `controls.json` only. `domains.json`, `system-types.json` and
> `level-definitions.json` were not yet rebuilt.
>
> **Extended 2026-09-01 (session 4).** `system-types.json` and `level-definitions.json` were run
> through the same pipeline (`corpus-ingest` skill; `diff_system_types.py`,
> `diff_level_definitions.py`). Result: **one more paraphrase instance found and corrected** —
> `sandbox`'s `classificationText` read "Security sensitivity level designated as Restricted,
> Sensitive Normal.", where all 5 other cybersecurity types (and the live page itself, confirmed
> independently via a Chrome DOM read) use the literal upstream label "Security Sensitivity
> Level: …". This is the same defect class as the `guidance` paraphrase — an editorial rewording
> of upstream's own field label — just a single instance rather than systemic across this file:
> the other 7 types' `classificationText` and all of `level-definitions.json` matched upstream
> exactly, verbatim (the latter including the Level-1 risk-impacts sentence). `domains.json`
> remains only spot-checked (see Open questions below) — not run through the full pipeline this
> round.

## Observation

A fresh scrape of all 26 control-catalog pages (`research/scripts/scrape.py`, 248 controls, every
domain count matching) was compared against the shipped corpus. Full report:
`research/corpus/scrape-diff-2026-09-01-before-promotion.md`.

**Membership and structure are perfect.** Same 248 ids, no controls missed, parameters match
exactly on all 42 controls. The original scrape captured the right things.

**The text does not match.** Of the 198 controls carrying `guidance`, only **42 reproduce upstream
exactly**; 156 differ.

### The decisive evidence: spelling

Upstream is a Singapore government site and uses British spelling almost exclusively — measured
across all guidance text: **243 British forms, 1 American**.

The shipped corpus contains **12 American forms** across 16 occurrences. For **13 of those 16, the
British equivalent is present at the same position upstream**:

| control | shipped | upstream |
|---|---|---|
| AC-1 | customization | customisability |
| AC-16, DP-4 | Organizations | Organisations |
| CS-1, CS-2, CS-8, RS-2 | minimize / minimizing | minimise / minimising |
| HR-1, NS-11, RS-1, RS-2 | utilize / utilization | utilise / utilisation |
| RS-2 | optimization | optimisation |
| TL-3 | recognize | recognise |

A faithful scrape cannot introduce American spelling into British source text. This is a rewrite.

### Corroborating signals

- **Systematic shortening.** Shipped guidance averages 346 chars against upstream's 402, and is
  shorter in 78 of 198 cases.
- **Condensed phrasing.** AC-1 upstream: *"Use automated tools such as AWS IAM Access Advisor or
  Azure AD Access Review to assist with granular permission management."* Shipped: *"Suggested
  tools include AWS IAM Access Advisor or Azure AD Access Review."* Same content, compressed.
- **Title-casing.** `UU-1` upstream "Understand user needs" → shipped "Understand User Needs";
  likewise `UU-2`, `WO-1`, `WP-1`. Upstream uses sentence case.
- **Inconsistent placeholder rewriting.** Upstream renders `[ insert: param, ac-3_prm_3 ]`. The
  shipped corpus rewrote 21 of 39 to `[ac-3_prm_3]` and left the rest untouched — a normalisation
  applied halfway.
- **Synthesised citations.** Shipped `AS-5` carries
  `{"standard": "NIST SP 800-63B", "reference": "NIST SP 800-63B"}` — a duplicated string. Upstream
  has a real link: text "SP 800-63B", href `https://doi.org/10.6028/NIST.SP.800-63b`. The shipped
  field was constructed, not captured. Upstream carries hrefs on 31 controls; shipped has
  `citations` on 15, and 5 of those 15 have no upstream link at all.

### Where the rewriting is concentrated

| catalog | exact | differing |
|---|---|---|
| cybersecurity | 36 | 70 |
| dss | 6 | 86 |

DSS is almost entirely rewritten (6 of 92 exact). Length does not discriminate — exact-match
controls average 383 chars upstream against 407 for differing ones — so this was not "summarise
the long ones".

## Evidence

- `python research/scripts/scrape.py all` then `python research/scripts/diff_corpus.py`
- `research/corpus/scrape-diff-2026-09-01-before-promotion.md`
- Spelling, length and catalog breakdowns computed ad hoc over both corpora
- repo @ working tree, 2026-09-01

## Interpretation

**Every record says `status: "scraped"`. For most of the corpus that label is wrong** — the text
was paraphrased, most likely by an LLM, and the provenance marker was left asserting otherwise.

Confidence is split deliberately:

- **That the shipped text is not verbatim upstream: certain.** 156 of 198 differ.
- **That paraphrase (not upstream revision) explains it: high.** The Anglicisation evidence is
  one-directional — upstream revising *toward* British spelling across 13 separate places, in
  exactly the words the shipped copy Americanised, is not a credible alternative.
- **That paraphrase explains *all* 156: not established.** Some upstream revision since the
  original capture is plausible and cannot be separated without an archived snapshot. The two
  causes are not mutually exclusive.

This matters more than the 50 missing-guidance controls that prompted the re-scrape. F-001 was a
gap; this is **silent infidelity across most of the corpus**, and it invalidates the premise the
project's own rules rest on.

## Implications

- **data (rule change):** `docs/CLAUDE.md` and `research/CLAUDE.md` both say the JSON "is a
  faithful scrape … don't edit it to make something look right." The protective instinct is sound
  but the premise is false — it has already been edited. The rule should become: *the data must
  become a faithful scrape, and may change only through the verified ingest pipeline.*
- **data:** Promotion is now clearly worth doing, and its value is much larger than F-001 implied:
  it restores fidelity on ~156 controls, fills 50 gaps, adds real citation hrefs, and adds
  per-control provenance (`sourceUrl`, `retrievedAt`).
- **site:** Users are currently reading paraphrased guidance presented as the standard's own words.
  For a compliance tool that is the most consequential defect found so far.
- **classifier:** Any vocabulary, embedding, or retrieval work over `guidance` has been operating
  on paraphrase. Since F-007 established that the eventual system must map *user* language to
  *standard* language, training or tuning on rewritten text would bake in the wrong target
  vocabulary. Redo any such analysis after promotion.
- **schema:** Upstream's three-way split (`statement` / `recommendations` / `risk` for
  cybersecurity, `statement` / `recommendations` / `rationale` for DSS) is cleaner than the
  concatenated `guidance`. Adopt it — the `Risk:` join is a website presentation choice, not part
  of the standard. **Formalized 2026-09-01 as [ADR-002](../decisions/ADR-002-split-guidance-into-recommendations-and-risk.md)
  (proposed, not yet owner-accepted).**

## Open questions

- **Resolved:** the 5 controls with shipped `citations` but no upstream link (`AS-11`, `AS-14`,
  `CK-2`, `CK-3`, `PM-1`) are **not fabricated** — each names its standard in upstream prose
  (NIST SP 800-63B, OWASP, AWS KMS / Azure Key Vault, NIST SP 800-57 / ISO-IEC 27017, NIST SP
  800-61), just without a hyperlink. They were preserved on promotion, without an invented `url`.
- **Partially checked:** `domains.json` is largely faithful — 5 of 6 sampled descriptions appear
  verbatim upstream. `AC` ("Controls governing account lifecycle management…") does not, and looks
  authored. Still not run through the full ingest pipeline (no `diff_domains.py` exists yet) —
  worth doing if `corpus-ingest` is extended further.
- **Resolved 2026-09-01:** `system-types.json` and `level-definitions.json` were diffed and
  promoted (see the header note above). `level-definitions.json` — the file F-003 flagged as
  mattering most, since it holds the only `selectionGuidance` — reproduces upstream exactly.
- Is an archived upstream snapshot available (Wayback) to separate paraphrase from revision on the
  ~143 non-spelling cases? Worth one attempt, not more — the conclusion no longer depends on it.
