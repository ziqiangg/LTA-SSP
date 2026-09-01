# research/ — how research work is done here

Goal: figure out **how to help users discover the controls (and guidance) relevant to their
system**. Two consumers of every finding — (1) the site under `docs/`, (2) a future classifier
that maps a free-text system description to controls. Findings must be written so both can use
them.

`research/` is committed and public but is **not** served by GitHub Pages (only `docs/` is).

## Non-negotiables

- **Never hand-edit `docs/assets/data/*.json`.** Its value is that it matches upstream, and the
  only sanctioned way it changes is the ingest pipeline:

  ```
  python research/scripts/scrape.py all          # fetch + parse, fails loudly
  python research/scripts/diff_corpus.py         # review report — READ IT
  python research/scripts/promote.py --dry-run   # then --apply
  ```

  Read the diff before promoting. Never reword the data, and never adjust it so a page or an
  analysis comes out better. If upstream itself is wrong or ambiguous, that is a finding with
  `implications: [data]`, not an edit.

  > Historical note: this rule used to assert the shipped JSON *was* a faithful scrape. It was
  > not — 156 of 198 `guidance` fields had been paraphrased, with American spellings in a British-
  > spelling source (F-008). The corpus was rebuilt from a verified scrape on 2026-09-01. The rule
  > is now a requirement to maintain, not a description of a guaranteed state.
- **Every claim carries provenance.** External claim → URL + retrieval date. Derived number →
  the script path and subcommand that produced it, so it can be re-run.
- **One finding per file** (`findings/F-NNN-slug.md`). Never append a second finding to an
  existing file; recall works by file.
- **Distinguish observation from inference.** A finding states what was measured, then what it
  implies, in separate sections. Don't smuggle a conclusion into a data statement.
- **Negative results are findings.** "Embedding similarity did not separate medium- from
  high-risk cloud" is worth a file. Don't only record what worked.

## Layout

| Path | What goes here |
|---|---|
| `README.md` | Index and reading order. The one file to read when orienting. |
| `QUESTIONS.md` | The RQ backlog with status. The spine of the work. |
| `JOURNAL.md` | Append-only dated log. Append; read by tail, never wholesale. |
| `findings/` | `F-NNN-slug.md`, one finding per file. |
| `prior-art/` | One card per external source. Written by the `literature-scout` agent. |
| `corpus/` | Derived tables from corpus analysis. |
| `evals/` | Labelled eval sets, their schema, and benchmark results. |
| `decisions/` | `ADR-NNN-slug.md` — decisions that bind the site or the future classifier. |
| `scripts/` | Python. Invoked as `python` (**not** `python3`) on this machine. |

## Tooling

Python is allowed **here only**. Start with the standard library — the whole corpus is 248 records
and 218 KB of JSON, so `json` + `collections` covers most analysis. Add `research/requirements.txt`
only when something genuinely needs it (e.g. embeddings work for RQ-3), and never let a dependency
leak into `docs/`.

## Skills and agents for this lane

- `ssp-corpus` — schema, invariants, and `corpus.py`. Load before touching the data.
- `research-note` — templates for findings, ADRs, and journal entries.
- `prior-art-review` — the literature workflow.
- `eval-set` — building and scoring labelled eval data.
- `corpus-analyst` agent — delegate bulk data crunching.
- `literature-scout` agent — delegate all web searching and reading.
