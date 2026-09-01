# level-definitions.json diff — upstream vs shipped

Generated `2026-09-01` by `research/scripts/diff_level_definitions.py`.

This is the file F-003 flagged as mattering most — it holds the only `selectionGuidance` in the corpus and is fetched by no JS file. This is the first time it's been run through the ingest pipeline rather than trusted on the strength of a one-time manual check.

## Fields

| field | shipped | upstream | match |
|---|---|---|---|
| `0` | These are cardinal and mandatory requirements. | These are cardinal and mandatory requirements. | yes |
| `1` | These are basic hygiene process and technical control requir… | These are basic hygiene process and technical control requir… | yes |
| `2` | These are best practices for Agencies to consider and adopt … | These are best practices for Agencies to consider and adopt … | yes |
| `selectionGuidance` | Agencies and their industry partners are required to assess … | Agencies and their industry partners are required to assess … | yes |

## Verdict

**Shipped reproduces upstream exactly, word for word**, including the Level-1 risk-impacts sentence. Nothing to promote. The file's `note` field (no formal decision tool exists beyond this prose) is editorial and not upstream-sourced, so it isn't compared here — it's preserved as-is on promotion.
