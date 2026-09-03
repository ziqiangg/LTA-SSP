# Scrape diff — upstream vs shipped

Generated `2026-09-03` by `research/scripts/diff_corpus.py`.
Upstream: 248 controls · Shipped: 248 controls

## 1. Membership

No difference — the same 248 control ids appear in both. **No controls were missed by the original scrape.**

## 2. Fields upstream that the shipped schema does not carry

| field | upstream | shipped | note |
|---|---|---|---|
| `catalog` | 248 | 248 |  |
| `citations` | 0 | 36 |  |
| `description` | 0 | 248 |  |
| `domainId` | 248 | 248 |  |
| `group` | 248 | 0 | domain name; shipped keeps only `domainId` |
| `id` | 248 | 248 |  |
| `links` | 11 | 0 | shipped `citations` was derived from these; upstream carries real hrefs |
| `parameters` | 42 | 42 |  |
| `rationale` | 92 | 92 | = shipped `rationale` (dss controls) |
| `recommendations` | 248 | 248 | = shipped `recommendations` |
| `retrievedAt` | 248 | 248 | **not in shipped schema** — provenance timestamp |
| `risk` | 156 | 156 | = shipped `risk` (cybersecurity controls) |
| `sourceUrl` | 248 | 248 | **not in shipped schema** — per-control provenance |
| `statement` | 248 | 0 | = shipped `description` |
| `status` | 0 | 248 |  |
| `title` | 248 | 248 |  |

## 3. Controls missing recommendations or risk/rationale

Shipped controls missing `recommendations` and/or their `risk`/`rationale`: **0**
Of those, upstream now supplies recommendations and/or risk/rationale text: **0**

| domain | gaps | recovered |
|---|---|---|

## 4. Text differences on controls that already had content

- **description**: 0 differ
- **recommendations**: 0 differ
- **risk-or-rationale**: 20 differ
  - `AC-16`, `AS-15`, `BD-9`, `CK-4`, `CS-11`, `DC-2`, `DP-8`, `GA-8`, `HR-3`, `IS-14`, `NS-11`, `PM-10`, `SC-9`, `SD-10`, `TL-6`, `TX-15`, `WO-18`, `WP-19`, `WR-2`, `WU-14`
- **title**: 0 differ

`recommendations` and `risk`/`rationale` ship as separate fields (ADR-002) — compared directly against upstream here, no composition step to keep in sync.

## 5. Parameters and links

- parameters: upstream 42 controls, shipped 42. Upstream-only: none. Shipped-only: none.
- links/citations: upstream 11 controls carry hrefs, shipped 36 carry `citations`.
  Upstream-only: none
  Shipped-only: AC-16, AS-11, AS-14, AS-15, BD-9, CK-2, CK-3, CK-4, CS-11, DC-2, DP-8, GA-8, HR-3, IS-14, NS-11, PM-1, PM-10, SC-9, SD-10, TL-6, TX-15, WO-18, WP-19, WR-2, WU-14

## Verdict

**20 text difference(s) and 0 control(s) missing guidance.** Review sections 1 and 4 before promoting — see the `corpus-ingest` procedure in `research/CLAUDE.md`.
