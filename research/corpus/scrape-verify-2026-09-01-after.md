# Scrape diff — upstream vs shipped

Generated `2026-09-01` by `research/scripts/diff_corpus.py`.
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
| `guidance` | 0 | 248 |  |
| `id` | 248 | 248 |  |
| `links` | 31 | 0 | shipped `citations` was derived from these; upstream carries real hrefs |
| `parameters` | 42 | 42 |  |
| `rationale` | 92 | 0 |  |
| `recommendations` | 248 | 0 | first half of shipped `guidance` |
| `retrievedAt` | 248 | 248 | **not in shipped schema** — provenance timestamp |
| `risk` | 156 | 0 | second half of shipped `guidance`, after `Risk: ` |
| `sourceUrl` | 248 | 248 | **not in shipped schema** — per-control provenance |
| `statement` | 248 | 0 | = shipped `description` |
| `status` | 0 | 248 |  |
| `title` | 248 | 248 |  |

## 3. The 50 missing-guidance controls (F-001)

Shipped controls with no `guidance`: **0**
Of those, upstream now supplies recommendations and/or risk text: **0**

| domain | gaps | recovered |
|---|---|---|

## 4. Text differences on controls that already had content

- **description**: 0 differ
- **guidance**: 0 differ
- **title**: 0 differ

`guidance` is composed by `promote.compose_guidance`, imported here so the two cannot drift: `recommendations` followed by `Risk: <risk>` for cybersecurity or `Rationale: <rationale>` for dss.

## 5. Parameters and links

- parameters: upstream 42 controls, shipped 42. Upstream-only: none. Shipped-only: none.
- links/citations: upstream 31 controls carry hrefs, shipped 36 carry `citations`.
  Upstream-only: none
  Shipped-only: AS-11, AS-14, CK-2, CK-3, PM-1

## Verdict

**The shipped corpus reproduces upstream exactly.** Same 248 ids, and zero differences in title, description or guidance. Nothing to promote.

Note the shipped schema still concatenates `recommendations` and the risk/rationale section into one `guidance` field. Splitting them into separate fields remains an open schema decision (F-008).
