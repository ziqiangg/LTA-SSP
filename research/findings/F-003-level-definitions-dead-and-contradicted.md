---
id: F-003
title: level-definitions.json is dead data, and the UI labels contradict it
date: 2026-09-01
rq: [RQ-5]
implications: [data, site]
confidence: high
status: open
---

## Observation

`docs/assets/data/level-definitions.json` is fetched by **no JavaScript file**. `controls.js`
loads exactly four files — `controls`, `domains`, `system-types`, `profiles` — and `wizard.js`
fetches nothing at all.

The file holds the only official prose the corpus has about what levels mean, and the only
`selectionGuidance` anywhere:

| | official prose (`level-definitions.json`) | UI label (`controls.js`) |
|---|---|---|
| L0 | "cardinal and mandatory requirements" | **Mandatory** |
| L1 | "basic hygiene process and technical control requirements, including toolings with alternatives. Agencies and industry partners are to assess and apply the controls in accordance with its risk impacts." | **Baseline** |
| L2 | "best practices for Agencies to consider and adopt where required" | **Optional** |

`selectionGuidance`, in full: *"Agencies and their industry partners are required to assess the
risks and threats for each of their systems, to determine the controls required to mitigate the
risks."*

The file also carries a `note` recording that no formal decision tool, flowchart, or explicit
"how to choose among the 8 types" guidance exists on the official landing page beyond that one
sentence and each type's own one-paragraph description.

## Evidence

- `python research/scripts/corpus.py gaps` (final section)
- `grep -o "level-definitions" docs/assets/js/*.js` → no matches
- `LEVEL_LABEL` in `docs/assets/js/controls.js`
- repo @ `4e7e6ba`

## Interpretation

Two distinct problems.

**The labels are not equivalent to the prose.** "Optional" is a fair gloss of L2. "Baseline" for
L1 is defensible. **"Mandatory" for L0 is fine, but the L1 label loses the part that matters** —
that agencies must *assess and apply according to risk impact*, which is an obligation, not a
default. A user reading "Baseline" reasonably concludes L1 is pre-decided for them. The
`defaultLevelsFor()` heuristic, which preselects L0+L1, reinforces that reading.

**`selectionGuidance` is the answer to the question this whole project is about** — how do I know
which controls apply to me — and it is (a) one sentence, (b) not shown to anyone. Its weakness is
itself the finding: the standard delegates selection to per-system risk assessment and offers no
mechanism. That is precisely the gap this tool could fill, and it means there is no upstream
authority to copy from. Whatever guidance the site offers, it will be constructing.

## Implications

- **site:** Surface the official level prose where the level chips appear — a tooltip or a legend
  on `/controls/`, sourced from the JSON rather than hardcoded, so labels and definitions cannot
  drift again. Show `selectionGuidance` somewhere on the wizard result, attributed.
- **data:** Either wire the file up or delete it. Committed-but-unfetched data will rot silently.
- **classifier:** Do not treat L1 as "automatically included". The standard makes it conditional
  on risk assessment, so a system that outputs a control set is asserting something the standard
  deliberately left to the agency. Any output needs to say so.

## Open questions

- Is there richer selection guidance on the individual system-type pages that was not captured?
- Should the site distinguish "this control is in your profile" from "this control is required of
  you"? Under the official prose those are not the same statement for L1 or L2.
