# Scrape diff — upstream vs shipped (PRE-promotion)

> Evidence for F-008 and for the promotion decision. Compares the fresh scrape
> against `docs/assets/data/controls.json` **as it stood before** the
> 2026-09-01 rebuild (git HEAD). The post-promotion verification is in
> `scrape-verify-2026-09-01-after.md`.

Generated `2026-09-01` by `research/scripts/diff_corpus.py`.
Upstream: 248 controls · Shipped: 248 controls

## 1. Membership

No difference — the same 248 control ids appear in both. **No controls were missed by the original scrape.**

## 2. Fields upstream that the shipped schema does not carry

| field | upstream | shipped | note |
|---|---|---|---|
| `catalog` | 248 | 248 |  |
| `citations` | 0 | 15 |  |
| `description` | 0 | 248 |  |
| `domainId` | 248 | 248 |  |
| `group` | 248 | 0 | domain name; shipped keeps only `domainId` |
| `guidance` | 0 | 198 |  |
| `id` | 248 | 248 |  |
| `links` | 31 | 0 | shipped `citations` was derived from these; upstream carries real hrefs |
| `parameters` | 42 | 42 |  |
| `rationale` | 92 | 0 |  |
| `recommendations` | 248 | 0 | first half of shipped `guidance` |
| `retrievedAt` | 248 | 0 | **not in shipped schema** — provenance timestamp |
| `risk` | 156 | 0 | second half of shipped `guidance`, after `Risk: ` |
| `sourceUrl` | 248 | 0 | **not in shipped schema** — per-control provenance |
| `statement` | 248 | 0 | = shipped `description` |
| `status` | 0 | 248 |  |
| `title` | 248 | 248 |  |

## 3. The 50 missing-guidance controls (F-001)

Shipped controls with no `guidance`: **50**
Of those, upstream now supplies recommendations and/or risk text: **50**

| domain | gaps | recovered |
|---|---|---|
| IS | 14 | 14 |
| LM | 21 | 21 |
| PM | 10 | 10 |
| ST | 5 | 5 |

Sample recovery — `IS-1`:

> **Recommendations:** Most CSP compute instances preinstall management agents (e.g., AWS Systems Manager Agent, Azure Windows VM Agent) by default. If the image does not come with the preinstalled agent, install manually.
> 
> **Risk:** Without installing management agents on hosts, there is an increased risk of manual misconfigurations, difficulty in maintaining consistent configurations, and potential security vulnerabilities due to reduced visibility and ability to manage hosts effectively.

## 4. Text differences on controls that already had content

- **description**: 39 differ
  - `AC-3`, `AC-4`, `AC-8`, `AC-11`, `AC-13`, `BD-2`, `BD-5`, `BD-7`, `CK-2`, `IS-9`, `IS-13`, `LM-8`, `LM-12`, `LM-21`, `PM-2`, `PM-4`, `PM-7`, `PM-9`, `SD-4`, `SD-5`, `SD-6`, `SD-9`, `ST-1`, `ST-3`, `ST-4` …
- **guidance**: 126 differ
  - `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5`, `AC-6`, `AC-7`, `AC-8`, `AC-9`, `AC-10`, `AC-11`, `AC-12`, `AC-13`, `AC-14`, `AC-15`, `AC-16`, `AS-15`, `BD-1`, `BD-2`, `BD-3`, `BD-4`, `BD-5`, `BD-6`, `BD-7`, `BD-8` …
- **title**: 4 differ
  - `UU-1`, `UU-2`, `WO-1`, `WP-1`

Of the 4 title differences, **4 are capitalisation only** (`UU-1`, `UU-2`, `WO-1`, `WP-1`) — upstream uses sentence case, the shipped corpus title-cased them.

Of the 39 description differences, **21 are parameter-placeholder formatting only** — upstream renders `[ insert: param, ac-3_prm_3 ]`, the shipped corpus rewrote some to `[ac-3_prm_3]` but not all. That inconsistency is itself a defect.

`guidance` is composed by `promote.compose_guidance`, imported here so the two cannot drift: `recommendations` followed by `Risk: <risk>` for cybersecurity or `Rationale: <rationale>` for dss.

## 5. Parameters and links

- parameters: upstream 42 controls, shipped 42. Upstream-only: none. Shipped-only: none.
- links/citations: upstream 31 controls carry hrefs, shipped 15 carry `citations`.
  Upstream-only: AC-16, AS-15, BD-9, BR-5, CS-11, DC-2, DP-8, GA-8, HR-3, IS-14, LM-18, NS-4, NS-11, PM-10, SC-9, TL-6, TX-15, WO-18, WP-19, WR-2, WU-14
  Shipped-only: AS-11, AS-14, CK-2, CK-3, PM-1

## Verdict

**169 text difference(s) and 50 missing-guidance control(s).** Review sections 1 and 4 before promoting — see the `corpus-ingest` procedure in `research/CLAUDE.md`.

Note the shipped schema still concatenates `recommendations` and the risk/rationale section into one `guidance` field. Splitting them into separate fields remains an open schema decision (F-008).
