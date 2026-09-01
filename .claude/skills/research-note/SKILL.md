---
name: research-note
description: Write up research output in this repo — findings, decision records (ADRs), and journal entries under research/. Use when recording what an investigation concluded, filing a corpus defect, capturing a decision that binds the site or the future classifier, or logging a session's work. Defines the file templates, the F-NNN/ADR-NNN numbering, provenance requirements, and the implications tag that keeps findings actionable.
---

# Writing research output

Every artifact lands in `research/`. One finding per file — never append a second finding to an
existing file, because recall works by file.

## The implications tag

Every finding declares who must act on it:

- **`site`** — changes something in `docs/`: wording, a page, the wizard, the filter UI.
- **`classifier`** — constrains the future free-text → controls system: a signal, an ambiguity,
  a label definition, a baseline to beat.
- **`data`** — a defect, gap, or contradiction in `docs/assets/data/*.json` or upstream.

A finding with no implication is not a finding; it is a note for `JOURNAL.md`. A finding may carry
more than one tag.

## Finding: `research/findings/F-NNN-slug.md`

Number sequentially; check the directory for the highest existing `F-NNN` first.

```markdown
---
id: F-007
title: Missing guidance is concentrated in four whole domains
date: 2026-09-01
rq: [RQ-5]
implications: [data, site]
confidence: high        # high | medium | low
status: open            # open | actioned | superseded
---

## Observation
What was measured or read. Facts only — no interpretation. Every number here must be
reproducible from the source named below.

## Evidence
- `python research/scripts/corpus.py gaps` (repo @ <short-sha>)
- <https://example.gov.sg/page> — retrieved 2026-09-01

## Interpretation
What it means. Clearly separated from the observation, so a later reader can disagree with the
reasoning while still trusting the numbers.

## Implications
- **site:** ...
- **data:** ...

## Open questions
What this did not settle.
```

Rules:
- **Observation and Interpretation stay separate.** Do not smuggle a conclusion into a data
  statement.
- **Every claim carries provenance.** External → URL + retrieval date. Derived → the exact command
  and the commit it was run against, so it can be re-run.
- **State confidence honestly**, and say what would change it.
- **Negative results are findings.** "Lexical overlap did not separate medium- from high-risk
  cloud" earns a file. A research folder that only records successes is a marketing folder.

## Decision record: `research/decisions/ADR-NNN-slug.md`

For choices that bind the site or the future classifier — a labelling scheme, a routing rule, a
metric definition, dropping an approach.

```markdown
---
id: ADR-003
title: Rank system types instead of returning exactly one
date: 2026-09-01
status: accepted        # proposed | accepted | superseded by ADR-NNN
findings: [F-002, F-005]
---

## Context
The situation forcing a choice, and the findings that establish it.

## Decision
What was decided, in the active voice.

## Consequences
What this makes easy, what it makes hard, and what it forecloses.

## Alternatives considered
Each with the reason it lost. One line apiece.
```

Supersede rather than rewrite: mark the old ADR `superseded by ADR-NNN` and leave its text intact.

## Journal: `research/JOURNAL.md`

Append-only, newest at the bottom. Read it by tail; never load the whole file. Use `/research-log`
to append.

```markdown
## 2026-09-01
- Ran `corpus.py gaps`; filed F-007 (guidance gaps cluster in IS/LM/PM/ST).
- RQ-5 moved to in-progress.
- Open: is the 9-control generative-ai profile real, or a partial scrape?
```

Journal entries record *what happened*. Findings record *what is true*. Keep them apart.

## Prior-art cards

Those live in `research/prior-art/` and follow the `prior-art-review` skill's template, not this
one.

## After writing

1. Add or update the finding's line in `research/README.md` (the index).
2. Update the RQ's status in `research/QUESTIONS.md` and link the finding.
3. Append a `JOURNAL.md` entry.

A finding that is not reachable from `README.md` and `QUESTIONS.md` will not be found again.
