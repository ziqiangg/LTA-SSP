---
id: F-010
title: In a blind eval pilot, no realistic system description had a single correct answer
date: 2026-09-01
rq: [RQ-1, RQ-3, RQ-6, RQ-2]
implications: [classifier, site]
confidence: medium
status: open
---

## Observation

15 system descriptions were generated **blind**: by an agent given government-system archetypes and
persona instructions, and told nothing about the SSP, the 8 system types, the wizard's questions,
control levels, or what the data would be used for. I labelled them afterwards.

Files: `research/evals/v1/cases-raw.jsonl` (descriptions), `cases.jsonl` (labels).

### The deciding facts are mostly absent

How often each fact the wizard depends on appears in the descriptions:

| fact | wizard question | stated in |
|---|---|---|
| Security Sensitivity Level | q7 | **0 / 15** |
| CII designation | q5 | **0 / 15** |
| Non-production status | q4 | 2 / 15 |
| Annual visits / traffic | q2 | 4 / 15 |
| Hosting (cloud vs on-prem) | q6 | 6 / 15 |
| GenAI as core function | q3 | 1 / 15 |

**Not one description states a sensitivity level or CII status** — the two facts on which the
medium/high-risk fork entirely depends.

### No case had one answer

Labelling with `acceptable_answers` (each entry a defensible complete answer):

- **15 / 15 cases admit two or more acceptable answers.** Mean 2.3 per case.
- **5 / 15 require a compound answer** (an overlay plus a hosting profile).
- Difficulty: 9 hard, 5 medium, 1 easy. Only `EV-003` (a public website stating 200,000 visits/
  month) resolved cleanly, and even that one carries a composite reading.

### Ambiguity tags, by frequency

| tag | n | in original vocabulary? |
|---|---|---|
| `hosting-unknown` | 8 | **no — new** |
| `sensitivity-inferred` | 6 | **no — new** |
| `composite` | 6 | yes |
| `traffic-unknown` | 3 | yes |
| `cii-undetermined` | 2 | yes |
| `nonprod` | 2 | yes |
| `wogaa-unknown` | 1 | **no — new** |
| `third-party-managed` | 1 | **no — new** |

The single most common ambiguity — hosting simply not being mentioned — was **not in the vocabulary
I designed before seeing any data**.

## Evidence

- `research/evals/v1/cases-raw.jsonl`, `research/evals/v1/cases.jsonl`
- Fact-presence counts computed by regex over the raw descriptions
- Blind-generation prompt recorded in `JOURNAL.md`; the generating agent was never shown the
  taxonomy
- 2026-09-01

## Interpretation

**The blinding worked, and that is why the result is worth anything.** Had I written these, I
would have unconsciously supplied hosting and sensitivity in most of them, because I know the tree
asks. The generator did not know, so it wrote what people actually volunteer — architecture,
history, team size, vendor complaints, what annoys them — and left out the classification inputs
entirely. The 0/15 on sensitivity is the clearest single signal in this pilot.

**This bounds a text-only classifier, hard.** Sensitivity and CII are *administrative
determinations*, not properties observable in prose. No amount of model capability recovers a fact
the input does not contain. F-004 predicted this ceiling from the tree's structure; the pilot
measures it from the input side and finds it lower than expected — hosting, which I assumed would
usually be stated, is missing in more than half.

**It also reframes what the site should do.** If no realistic description determines one type, then
a tool that returns exactly one type is not merely limited — it is *answering with a confidence the
input does not support*. The honest output is a small ranked set plus the specific question that
would narrow it. That is the same conclusion F-007 reached from prior art, arrived at independently
from data.

**Confidence is medium, not high**, and the reasons should be stated plainly:

- n = 15. Tag frequencies are indicative, not estimates.
- Single labeller (me), so there is no agreement measure — the κ≈0.71–0.76 ceiling from F-007
  cannot be checked against anything here. **Owner spot-check done 2026-09-01** — see
  `research/evals/v1/spot-check-2026-09-01.md`. Result: 13/15 agree outright, 1 agree-with-a-note
  (EV-007's `composite` tag), 1 genuine disagreement (EV-013, see Open questions). This is one
  reviewer, not independent inter-annotator agreement in the PROPARAG sense, so it upgrades
  confidence from "no signal" to "one corroborating read" — not to a κ figure.
- The descriptions are synthetic. The generator was blind to the taxonomy but is still a language
  model imitating personas, and I chose the archetypes. Real omissions may pattern differently.

What is *not* uncertain: the schema defects below are demonstrated, not inferred.

## Implications

- **eval schema (blocking, demonstrated):** `acceptable_types` as a flat list of type ids **cannot
  express a compound answer**, and 5 of 15 cases need one. It must become `acceptable_answers` —
  a list of answers, each itself an array of type ids. Already applied in `cases.jsonl`; the
  `eval-set` skill needs updating to match.
- **eval schema:** add `hosting-unknown`, `sensitivity-inferred`, `wogaa-unknown`,
  `third-party-managed` to the ambiguity vocabulary. The first two are not edge cases — they are
  the two most common conditions in the set.
- **classifier:** Report accuracy **broken down by ambiguity tag**, and treat `hosting-unknown` and
  `sensitivity-inferred` as a separate stratum. Aggregate accuracy over a set where 8/15 cases are
  missing the deciding fact measures the label distribution, not the method.
- **classifier:** The output must include *which question would resolve the ambiguity*. On this
  evidence that is the most useful thing such a system can emit — more useful than the prediction.
- **site:** The wizard asks for facts users do not have to hand. The sensitivity-rung question
  (formerly q7) asks for a Security Sensitivity Level; nobody in this set knew theirs. FIPS 199's
  AMPLIFICATION pattern (F-007, PA-003) — asking about *consequences* instead of *classifications*
  — addresses exactly this, and is still not implemented (F-007).
- **site:** `EV-013` is worth carrying into any wizard redesign. A staging environment whose
  anonymisation has been silently failing routes to `sandbox` (3 mandatory + 114 optional controls)
  while holding live citizen data. The tree keys on the environment label; the risk lives in the
  data.

## Open questions

- ~~Owner spot-check of these 15 labels, to produce the pilot's only agreement signal.~~ **Done
  2026-09-01** — `research/evals/v1/spot-check-2026-09-01.md`.
- Does `hosting-unknown` stay this frequent at n=120? If so, hosting should be asked directly
  rather than inferred, and the classifier should not attempt it. **Sharper version, from the
  spot-check:** 6 of the 8 `hosting-unknown` cases resolve to the *identical* two-answer fork
  (some cloud tier vs. `low-risk-on-premises`), which is a coverage-diversity risk for scaling, not
  just a tag-frequency one — see F-011.
- Should `acceptable_answers` be *ordered* by preference? `EV-013` has a deliberate ordering
  (`medium-risk-cloud` before `sandbox`) that the current schema does not formally interpret.
  **Spot-check verdict: yes, order should be treated as meaningful — and not resolved.** The
  spot-check disagreed with `EV-013` as labelled: `sandbox` is tree-reachable (a literal q4 answer)
  but not defensible the way two answers in, say, EV-006 both are — applying it means 3 mandatory
  controls plus 114 optional for an environment now holding unmasked citizen PII. The current
  schema has no way to mark an answer as "reachable but substantively wrong" distinctly from
  "genuinely uncertain between two reasonable readings," and `EV-013`'s ordering is the only place
  that distinction survives today, informally. Not fixed here — `cases.jsonl` is unedited by this
  pass — but the schema gap should be closed before scaling past the pilot.
