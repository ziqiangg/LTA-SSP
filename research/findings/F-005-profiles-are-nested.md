---
id: F-005
title: Profiles nest — high-risk cloud is a strict superset of medium-risk cloud
date: 2026-09-01
rq: [RQ-3, RQ-2]
implications: [classifier, site]
confidence: high
status: open
---

## Observation

Comparing the two cloud profiles that users are most likely to confuse:

```
medium-risk-cloud (117) vs high-risk-cloud (137)
shared 117 | only in medium: 0 | only in high: 20 | level changed: 38
```

**Zero controls are unique to medium-risk-cloud.** High-risk contains all 117 of medium's
controls, adds 20, and escalates 38 to a stricter level. The 20 additions fall in
`BR` 3 (disaster recovery, business continuity), `HR` 3 (awareness training, screening,
termination), `RS` 3 (resiliency), `NS` 3, `CK` 2, `PM` 2, `SD` 2, `AC` 1, `LM` 1 — `HR` and `RS`
being domains medium-risk does not use at all.

**The nesting is general, not specific to this pair:**

| chain | strict subset? |
|---|---|
| `low-risk-cloud` ⊂ `medium-risk-cloud` | yes (0 unique to low) |
| `medium-risk-cloud` ⊂ `high-risk-cloud` | yes (0 unique to medium) |
| `digital-services-others` ⊂ `digital-services-high-impact` | yes (identical 92-control set; differs only by level) |
| `low-risk-on-premises` ⊂ `low-risk-cloud` | **no** — 7 controls unique to on-premises |

So the three cloud profiles form a clean ladder, and the two Digital Services profiles differ
*only* in level. On-premises sits outside the ladder: it carries 7 controls no cloud profile has
(it uses the `DC` datacentre domain and drops `CS` container security).

Level distribution shifts sharply: medium is `{0: 26, 1: 68, 2: 23}`, high is `{0: 63, 1: 59,
2: 15}`. Most of the difference is not new controls but **the same controls made mandatory**.

Separately, `classificationText` for the two types carries **identical** sensitivity wording —
"Security Sensitivity Level: Confidential, Sensitive High". CII designation is the only textual
differentiator between them. The same is true of `low-risk-cloud` and `low-risk-on-premises`,
which share "Up to Restricted, Sensitive Normal".

## Evidence

- `python research/scripts/corpus.py diff medium-risk-cloud high-risk-cloud`
- `python research/scripts/corpus.py gaps` (identical-wording section)
- Subset checks across all five pairs run ad hoc over `profiles.json`; reproducible with
  `diff` on each pair.
- repo @ `4e7e6ba`

## Interpretation

The nesting makes classification error **asymmetric**, and that asymmetry should drive both the
product and the metrics:

- Predicting **high** when the truth is **medium** → the user is handed 20 extra controls and 38
  over-strict levels. Wasteful, but nothing is left unprotected.
- Predicting **medium** when the truth is **high** → the user is missing disaster recovery,
  business continuity, HR security controls, and 37 escalations to mandatory. Under-protected on
  exactly the axes that matter for critical infrastructure.

These are not the same error and must never be aggregated into one number.

The identical sensitivity wording compounds it. The single fact separating the two profiles — CII
designation — is administrative, externally assigned, and absent from any natural description of
a system. A text-only classifier cannot recover it. This is a ceiling imposed by the corpus, not
a modelling weakness, and it should be established as such *before* any method is blamed for
missing it.

Because the nesting is general, **the sensitivity axis is monotonic**: choosing a higher tier is
always a superset of choosing a lower one. That is a strong structural property. It means a
classifier that is uncertain between adjacent tiers has a safe fallback — return the higher tier
and say which question would narrow it — and it means the site can present tiers as increments
rather than as eight unrelated lists. On-premises is the exception and must be handled separately;
it is not a point on the ladder.

## Implications

- **classifier:** Report medium→high and high→medium confusions separately, never as one accuracy
  figure (this is now written into the `eval-set` skill). Weight Level-0 recall highest, since the
  escalations are the bulk of the difference. Where CII cannot be determined, the honest output is
  a ranked pair with the distinguishing question surfaced — not a guess.
- **site:** Since profiles do nest, the UI could show high-risk as *medium plus these 20, with
  these 38 escalated* rather than as a flat 137-item list. That framing is far more legible to a
  user deciding between them, and it makes the cost of the CII question visible. The same applies
  to the two Digital Services types, which differ *only* by level — showing that as a diff would
  make the distinction comprehensible in a way two 92-item lists never will.
- **site:** The wizard's q5 asks about CII inside a compound question (see F-004). Given it is the
  sole differentiator here, it deserves its own step with an explanation of what CII designation
  means and who assigns it.

## Corroboration (2026-09-01)

The nesting is **confirmed as deliberate**, from an independent direction. GovTech's official
OSCAL publication (`GovTechSG/tech-standards`, see F-006) expresses level tiers as *cumulative
profile imports*: `low-risk-level-1` imports `low-risk-level-0` plus the catalog, and
`low-risk-level-2` imports level-1. The publisher models the ladder structurally rather than
restating each tier.

That closes the original open question: nesting is a design property of the standard, not an
artefact of how these templates happened to be authored. Note the OSCAL layering runs only **across
levels within a risk tier** — never across system types, which is why it says nothing about the
composition question in F-002.

## Qualification — nesting is contingent, not a law (PA-004)

**Do not hardcode "higher tier = lower tier + extras".** Australia's ISM, the closest structural
peer found (a national control catalogue published as OSCAL, where applicability is likewise a
property of the (classification, control) pair), has baselines that **do not nest** — and the
reason is instructive.

Measured from ASD's published JSON: of ten ordered baseline pairs, only two are true subsets. 3
controls in non-classified are absent from OFFICIAL:Sensitive; 25 in non-classified are absent from
TOP SECRET; 19 in SECRET are absent from TOP SECRET; 2 in ML1 are absent from ML3 — despite control
counts rising monotonically throughout.

The cause is **control supersession**. ASD's `ism-1695` ("...patches applied within one month of
release") carries Essential Eight applicability ML1 and ML2 but not ML3, because at ML3 a
stricter-timeframe control replaces it. *A weaker obligation is not a subset of a stronger one; it
is superseded by it.* A pure subset model cannot express that.

Our profiles nest **today**. That is a contingent property of the current data, not a guarantee
about SSP revisions. The first revision that supersedes a control with a stricter variant will
break it silently.

Consequences:

- Any diff-based representation must support **removal**, not only addition. OSCAL has
  `exclude-controls` for exactly this.
- Add a **build-time assertion** over `profiles.json` that re-checks the nesting rather than
  assuming it. `corpus.py` already computes the subset relations; this is a small step from there
  and it is the difference between a claim that stays true and one that quietly rots.

## Implementation trap: strictest is the LOWEST number

Levels run **L0 mandatory → L1 baseline → L2 optional**, so strictness *decreases* as the number
increases. Any "high-water mark" / most-stringent resolve across profiles is therefore **`min()`,
not `max()`**.

Verified against the data: AC-1 is L0 in high-risk-cloud, L1 in medium and low, L2 in sandbox —
`min()` correctly yields the high-risk obligation.

This inverts easily, reads naturally the wrong way round ("high water mark" suggests `max`), and
would fail silently by returning the *laxest* applicable level. Whoever implements composition must
have this in front of them.

## Composition across profiles is safe (measured)

111 controls carry different levels across profiles — but every one of those disagreements lives
*within* the hosting ladder, where a user picks one rung rather than composing. The overlay
profiles do not participate: all 9 `generative-ai` controls appear in no other profile, and no DSS
control appears in any non-DSS profile. Overlay-plus-hosting is a **plain union with zero level
conflicts**. See F-007 for why that matters.

## Open questions

- Why does `low-risk-on-premises` carry 7 controls the cloud ladder lacks? Presumably the `DC`
  datacentre domain — worth confirming, since it means on-prem cannot be presented as "low-risk
  cloud, but hosted differently".
