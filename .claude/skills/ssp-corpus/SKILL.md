---
name: ssp-corpus
description: Query and reason about the SSP control corpus (248 controls, 26 domains, 8 system types, profiles, levels) in docs/assets/data/*.json. Use whenever a task needs control/domain/profile/system-type data — counts, lookups, filters, profile comparisons, coverage or gap analysis — or before writing code that reads those files. Explains the schema, the level-is-a-join invariant, and the corpus.py query tool that keeps the JSON out of context.
---

# The SSP corpus

## Rule zero

**Do not read `controls.json` or `profiles.json` into context.** They are ~310 KB together and
you almost never need all of it. Use the query tool:

```
python research/scripts/corpus.py <subcommand>
```

Run it from the repo root. On this machine the interpreter is `python`, not `python3`. It is
stdlib-only, read-only, and prints compact tables. For bulk or exploratory crunching, delegate to
the **`corpus-analyst`** agent so even the tables stay out of your window.

`domains.json` (8 KB), `system-types.json` (6 KB) and `level-definitions.json` (1 KB) are small
enough to read directly when you genuinely need their prose.

## Subcommands

| Command | Gives you |
|---|---|
| `stats` | Counts, catalog split, field coverage, per-profile level distribution, plus integrity checks |
| `types` | The 8 system types with `classificationText`, domains, levels |
| `levels` | The L0/L1/L2 definitions and `selectionGuidance`, printed directly |
| `domains [--catalog cybersecurity\|dss]` | All 26 domains with control counts |
| `profile <type> [--level N] [--domain XX]` | Every control applying to a system type, with its level |
| `diff <type-a> <type-b>` | Added / removed / level-changed controls between two profiles |
| `domain <ID>` | One domain's controls and which profiles use them at what level |
| `control <ID> [...]` | Full detail for specific controls, including which profiles use them |
| `grep <term> [--field ...]` | Substring search across title/description/guidance |
| `gaps` | Corpus defects worth filing as findings |

## Schema

**`controls.json`** — array of 248 objects. Rebuilt from a verified scrape on 2026-09-01 (F-008).
Always: `id`, `domainId`, `catalog`, `title`, `description`, `guidance`, `sourceUrl`,
`retrievedAt`, `status`.
Sometimes: `parameters` (42), `citations` (36).

- `id` is `<DOMAIN>-<n>` (`AC-1`, `WU-9`). Sort numerically, not lexically — `AC-2` before `AC-11`.
- `catalog` is `cybersecurity` (156) or `dss` (92).
- `description` embeds parameter placeholders **verbatim as upstream renders them** —
  `[ insert: param, ac-11_prm_1 ]`, not `[ac-11_prm_1]` — resolved by `parameters[]`
  (`{id, type, description}`). Prettier rendering is a `controls.js` job, not a data job.
- `guidance` for cybersecurity is implementation advice then a trailing `Risk: ...` clause; that
  clause is the closest thing the corpus has to a rationale. For DSS it is the upstream *Rationale*
  section and has **no** `Risk:` clause — don't write a parser that assumes one.
- `citations[]` entries are `{standard, url?}` when scraped from an upstream hyperlink (36 controls
  now carry citations), or `{standard, reference?}` when recovered from prose with no link. Test
  for `url` before rendering a link.
- `sourceUrl` / `retrievedAt` are per-control provenance, added at the 2026-09-01 rebuild.
- `status` is `"scraped"` for all 248 — and since the rebuild it is actually accurate.

**`domains.json`** — 26 objects: `id` (2 letters), `name`, `catalog`, `description`, `sourceUrl`,
`controlCount`. 17 cybersecurity + 9 Digital Service Standards (the DSS ones are largely WCAG).

**`system-types.json`** — 8 objects: `id`, `name`, `catalog`, `classificationText`, `domainsUsed`,
`levelsAvailable`, `sourceUrl`. The two DSS types also carry `totalControls`/`levelCounts`, and
`digital-services-high-impact` carries a `note` recording a live-DOM verification.

**`profiles.json`** — an object keyed by the 8 system-type ids; each value is an array of
`{controlId, level}` and nothing else.

**`level-definitions.json`** — `{"0","1","2", selectionGuidance, sourceUrl, note}`. All prose.

## Invariants — get these wrong and the analysis is wrong

1. **A control has no intrinsic level.** Level is a property of the `(system type, control)` pair
   and lives only in `profiles.json`. The same control is L2 in one profile and L0 in another.
   Never speak of "a Level 1 control" without naming the system type.
2. **The profile join is the entire applicability mechanism.** `controls.js` `workingControls()`
   builds `levelById` from `profiles[type]`, filters `controls` to those ids, and attaches the
   level. There is no other path from a user to a control set.
3. **`levelsAvailable` is not `{0,1,2}` for everyone.** `generative-ai` is `[0,1]`; `sandbox` is
   `[0,2]` — it has *no* Level 1 at all, and 114 of its 117 controls are L2.
4. **The `catalog:cybersecurity` / `catalog:dss` pseudo-types bypass profiles entirely**, yielding
   all controls in that catalog with `level: null` and level filtering disabled.
5. **`defaultLevelsFor()` preselects `levelsAvailable ∩ {0,1}`**, falling back to all available
   levels if that is empty — which is why Sandbox defaults to showing L0 *and* L2.
6. **UI level labels and the official prose disagree.** `controls.js` says
   `{0:"Mandatory", 1:"Baseline", 2:"Optional"}`; `level-definitions.json` says "cardinal and
   mandatory requirements" / "basic hygiene ... assess and apply in accordance with risk impacts"
   / "best practices ... adopt where required". `level-definitions.json` is fetched by no JS file.

## Structural facts worth knowing before analysing

- **High-risk is a strict superset of medium-risk.** `diff medium-risk-cloud high-risk-cloud`:
  zero controls unique to medium, 20 added, 38 escalated in level. Profiles nest.
  Verified 2026-09-01: this nesting is **deliberate** — GovTech's official OSCAL profiles import
  cumulatively (level-1 imports level-0), so it can be relied on. See F-005, F-006.
- **`generative-ai` is an outlier** — 9 controls over 2 domains (`DP`, `GA`) against ~117 for its
  peers, with no access control, logging, or backup. Whether it is a standalone baseline or an
  overlay on a hosting profile is **genuinely unresolved**: upstream frames it standalone but gives
  it contents that cannot work standalone, and the official OSCAL source has no gen-ai profile at
  all. Do not assert either reading as fact. See F-002.
- **`guidance` is now complete and faithful.** All 248 controls carry it. The former 50-control
  gap (the whole of IS/LM/PM/ST) was a scrape failure and was recovered on 2026-09-01. Older
  analyses that used a denominator of 198 are stale — redo them. See F-001, F-008.
- **Most `guidance` text was previously paraphrased**, not scraped: only 42 of 198 matched upstream
  before the rebuild. Any vocabulary, embedding, or retrieval work done on the corpus before
  2026-09-01 was operating on rewritten text and should be redone. See F-008.
- **An official OSCAL source exists** (`GovTechSG/tech-standards`) but covers only ~half this
  corpus — no GA, no DSS/WCAG, only low/medium-risk profiles — and is stale. Do not treat it as a
  drop-in. See F-006.
- **`guidance` is a composed field, and the two catalogs compose differently.** Upstream publishes
  a control as *Control Statement* + *Control Recommendations* + a third section — **Risk
  Statement** for cybersecurity (156 controls), **Rationale** for DSS (92). Our `description` is
  the statement; our `guidance` is `recommendations + " Risk: " + risk` for cybersecurity and
  `rationale` for DSS, matching how the upstream site itself renders them. Splitting these into
  separate fields is a pending schema decision, not done.
- **Medium- and high-risk cloud share identical sensitivity wording** in `classificationText`
  ("Confidential, Sensitive High") — CII designation is the only textual differentiator. Low-risk
  cloud and on-premises likewise share wording. This is the central ambiguity any classifier faces.

## When the data looks wrong

`docs/assets/data/*.json` must reproduce upstream, and its value is that it does. **Never hand-edit
it**, and never adjust it so an analysis or a page comes out better — that is how the corpus
drifted into paraphrase before (F-008).

The only sanctioned way it changes is the ingest pipeline — see the **`corpus-ingest`** skill for
the full fetch → parse → diff → verify → promote procedure, stated once there (not repeated here).

If upstream itself is wrong, ambiguous, or missing something, that is a finding with
`implications: [data]` (see `research-note`), not an edit. `corpus.py gaps` generates the
candidate list.
