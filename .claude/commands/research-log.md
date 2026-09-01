---
description: Append a dated entry to research/JOURNAL.md
argument-hint: [what happened this session]
allowed-tools: Bash(python:*), Bash(git log:*), Bash(git status:*), Read, Edit
---

Append an entry to `research/JOURNAL.md` recording this session's research work.

Notes from the user (may be empty — if so, derive the entry from what actually happened in this
session): $ARGUMENTS

Rules:

- **Append only.** Never rewrite or reorder existing entries. Read the tail of the file to find
  today's date heading; do not load the whole file.
- If a `## <today's date>` heading already exists, add bullets under it. Otherwise create it.
- Use ISO dates (`## 2026-09-01`).
- Journal entries record **what happened**; findings record **what is true**. Keep the entry to
  actions, decisions, and open threads — if you discovered something true and durable, that
  belongs in `research/findings/` via the `research-note` skill, and the journal just points at it.
- Keep each bullet to one line. Name the artifacts touched (`F-007`, `PA-012`, `RQ-5`) so they are
  greppable.
- End with any open question the next session should pick up.

Example shape:

```markdown
## 2026-09-01
- Ran `corpus.py gaps`; filed F-007 (guidance gaps cluster in IS/LM/PM/ST — scrape artefact).
- RQ-5 → in-progress.
- Open: is the 9-control generative-ai profile real, or a partial scrape?
```

After appending, report the entry you added in two or three lines. Do not print the whole journal.
