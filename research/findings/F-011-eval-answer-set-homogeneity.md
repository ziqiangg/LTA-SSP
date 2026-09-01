---
id: F-011
title: 6 of 15 pilot cases share one identical hosting-unknown answer pair
date: 2026-09-01
rq: [RQ-6]
implications: [classifier]
confidence: medium
status: open
---

## Observation

Reviewing `research/evals/v1/cases.jsonl`'s 15 `acceptable_answers` sets side by side (during the
owner spot-check, `research/evals/v1/spot-check-2026-09-01.md`), 6 of them are pairwise identical
in shape: `[[<some cloud-risk tier>], ["low-risk-on-premises"]]`, where the cloud tier is
`medium-risk-cloud` in 5 cases and `low-risk-cloud` in 1.

| id | acceptable_answers |
|---|---|
| EV-001 | `[["medium-risk-cloud"], ["low-risk-on-premises"]]` |
| EV-005 | `[["medium-risk-cloud"], ["low-risk-on-premises"]]` |
| EV-007 | `[["low-risk-cloud"], ["low-risk-on-premises"]]` |
| EV-009 | `[["medium-risk-cloud"], ["low-risk-on-premises"]]` |
| EV-010 | `[["low-risk-cloud"], ["low-risk-on-premises"]]` |
| EV-015 | `[["medium-risk-cloud"], ["low-risk-on-premises"]]` |

All 6 carry the `hosting-unknown` tag, and in every one the fork exists for the same structural
reason: the description states enough about sensitivity (explicitly or inferably) to fix the cloud
tier, but never states hosting, so the answer set forks on that single unstated fact between one
cloud tier and the sole on-premises profile.

## Evidence

- `research/evals/v1/cases.jsonl` (all 15 records), read directly during the 2026-09-01 spot-check.
- F-010 (`research/findings/F-010-eval-pilot-no-case-has-one-answer.md`) already reports
  `hosting-unknown` as the most frequent ambiguity tag, 8/15. This finding adds that 6 of those 8
  don't just share a tag — they share the exact same answer *pair*.

## Interpretation

F-010 measured ambiguity by tag frequency, which treats `hosting-unknown` as one condition. But a
tag frequency doesn't distinguish "the same fork keeps recurring" from "the tag covers many
different forks" — and it turns out to be the former here. Two thirds of the `hosting-unknown`
cases in the pilot are, in answer-space, the same case wearing a different persona: a back-office
or internal system, sensitivity inferable from the data described, hosting never mentioned.

This matters specifically for handover item 5 (scale the eval to ~120-160 cases, generate blind
again): naively repeating the current archetype mix — vary the persona and the domain, keep
"internal system, don't mention hosting" as the default framing — would inflate this one fork's
count without adding new signal or new failure modes to measure against. The eval-set skill's
sampling guidance already says "register variety" and warns against volume without composition; this
is a concrete instance of what that warning is protecting against, discovered from real pilot data
rather than anticipated in the abstract.

It also sharpens the risk in F-010's open question about whether `hosting-unknown` "stays this
frequent at n=120" — the more precise question is whether it stays this *narrow* (one recurring
fork) or diversifies (different sensitivity levels, different cloud tiers, on-premises genuinely
ruled out by context) as more archetypes are added.

## Implications

- **classifier:** When scaling generation, deliberately vary what's held constant across
  `hosting-unknown` cases — sensitivity level, whether on-premises is plausible at all for the
  archetype (e.g. a modern SaaS-native system where on-prem is barely credible), and whether the
  fork is binary (two tiers) or wider (as in EV-008's three-way fork). A generation prompt that
  just multiplies personas over the same "internal, sensitive, hosting unstated" template will
  under-diversify this stratum even at n=120-160.
- **classifier:** When reporting accuracy by `ambiguity` tag (per the eval-set skill's metrics
  section), treat `hosting-unknown` as internally stratified rather than one bucket — a method that
  handles the recurring binary fork well may still fail on EV-008's three-way version.

## Open questions

- Does the recurring binary fork (cloud-tier vs. on-premises) still dominate `hosting-unknown` at
  n=120-160, or was this an artifact of the pilot's small, back-office-heavy archetype mix?
- Are there realistic archetypes where hosting is unstated but on-premises is *not* plausible (e.g.
  a system described in terms that are inherently cloud-native), which would break the binary fork
  into a narrower one?
