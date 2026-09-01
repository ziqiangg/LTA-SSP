# Research questions

The spine of the work. Each RQ has a status, the findings that bear on it, and a note on what
would count as an answer. Update status here whenever a finding lands.

Status: `open` → `in-progress` → `answered` (link the finding) → `parked` (say why).

---

## RQ-1 — How do users actually describe their systems?
**Implications:** site, classifier · **Status:** open (constrained)

> **Constraint (2026-09-01):** no real user-written descriptions are available. Sources are
> authoritative only — upstream SSP pages, GovTechSG structured data. This RQ can therefore only
> be approached through proxies, and any answer is provisional. See
> `research/evals/README.md` for what this costs the eval.

How far is a real user's description of their system from the vocabulary in `classificationText`,
domain names, and control titles? The site's search matches substrings over `id`, `title` and
`description` only — so any vocabulary gap is a silent zero-results experience.

*Answered when:* we have a documented vocabulary gap — terms users would plausibly use that match
nothing in the corpus, and the corpus terms they would never think to type.

*Note:* user interviews are out of scope for now, so this must be approached through proxies —
the corpus's own vocabulary, prior art on compliance intake, and the eval descriptions written
under RQ-6.

---

## RQ-2 — Where does the current wizard give wrong or unhelpful answers?
**Implications:** site · **Status:** in-progress · **Findings:** F-004

The 7-node tree in `wizard.js` returns exactly one type, with no ranking and no way to express a
composite system. Known suspects are catalogued in F-004: composite systems (GenAI + digital
service) unreachable, on-premises never reaching the sensitivity question, and medium vs.
high-risk cloud separable only by CII designation.

*Answered when:* every failure mode is enumerated with a concrete example description, and each is
classified as *fixable in the tree* / *needs a different interaction model* / *blocked upstream by
the standard*.

---

## RQ-3 — Which signals in a free-text description determine the type?
**Implications:** classifier · **Status:** open · **Findings:** F-005

The wizard's 7 questions imply 7 features: WOGAA-tracked, traffic volume, GenAI core function,
non-production, CII designation, hosting location, sensitivity level. Are those extractable from
prose? Which are usually absent? What else carries signal?

*Answered when:* we have a feature inventory, each marked for how reliably it appears in a
realistic description, plus a first read on whether rule-based extraction is sufficient or
semantic methods are needed — measured against RQ-6's eval, not asserted.

---

## RQ-4 — How does prior art solve control discovery?
**Implications:** site, classifier · **Status:** **answered** 2026-09-01 · **Findings:** F-007 ·
**Sources:** PA-001..PA-013

**Answer:** prior art solves selection *after* typing, and nobody solves typing from a free-text
description — every source assumes the system is already classified by a step outside the
framework. What it does give us: high-water-mark composition (FIPS 199) as the answer to composite
systems, a formal overlay vocabulary (SP 800-53B App. C), the only written taxonomy of why a
control may be dropped (800-53B §2.4), and four independent frameworks converging on *show all
controls with a status and reason* rather than a filtered list. Plus two hard calibration anchors:
expert agreement ceilings at κ≈0.71–0.76, best full-coverage retrieval at 44.4 FullCov@10.

Follow-ups worth their own RQ if pursued: overlay composition is unsolved everywhere (nobody
defines what happens when two overlays disagree), and no crosswalk disagreement rates are published.

NIST OSCAL (whose profile-resolution model addresses this corpus's level-is-a-join structure
directly), SP 800-53B baselines, ISO 27001 Statement of Applicability, SCF and CSA CCM crosswalks,
commercial compliance tooling, and peer-government frameworks that publish real selection
guidance.

*Answered when:* cards filed in `prior-art/` and synthesized into a finding that names what to
adopt, what to adapt, and what nobody has solved.

*Run via:* `prior-art-review` skill → `literature-scout` agent.

---

## RQ-5 — What is missing from the corpus for guidance to be useful?
**Implications:** data, site · **Status:** substantially answered (verified 2026-09-01) ·
**Findings:** F-001, F-002, F-003, F-006

`selectionGuidance` is a single sentence and is currently fetched by nothing. 50 controls have no
`guidance` at all. The `generative-ai` profile has 9 controls against ~117 for its peers.

*Answered when:* each gap is classified as *scrape artefact* (re-fetchable), *genuinely absent
upstream* (needs authoring or a pointer), or *deliberate*, with the upstream page checked for each.

**Verification results:**

| gap | verdict |
|---|---|
| 50 missing `guidance` (IS/LM/PM/ST) | **scrape artefact** — exists upstream, 100% OSCAL coverage. Recoverable (F-001). |
| `generative-ai` = 9 controls | **ambiguous upstream** — framed standalone, contents say otherwise. Not resolvable from published material (F-002). |
| one-sentence `selectionGuidance` | **genuinely absent upstream** — no decision tool or flowchart exists. Whatever the site offers, it will be constructing (F-003). |

Remaining: (a) decide the recovery route for F-001 in an ADR — scrape, OSCAL import, or hybrid;
(b) get a human answer from GovTech on the composition question.

---

## RQ-6 — What does a defensible eval look like, and what is the baseline?
**Implications:** classifier · **Status:** open

Nothing can be claimed about semantic or LLM approaches until the rule-based baseline — today's
wizard tree, mechanically applied — is measured on a labelled set.

*Answered when:* `evals/v1/` holds ~120-160 labelled cases with an ambiguity-tag breakdown, and
the wizard-tree baseline plus the majority-class floor are both scored and written up.

*Run via:* `eval-set` skill.

**Calibrated 2026-09-01 (F-007):** expert inter-annotator agreement on control applicability
ceilings at κ≈0.71–0.76, and best-known full-coverage retrieval over regulatory corpora is 44.4
FullCov@10. Targets must sit under those ceilings; a result that beats them comfortably indicates a
leaky eval, not a breakthrough. Combined with the synthetic-data limitation
(`evals/README.md`), v1 supports **relative** comparison only.

---

## Parked

- **User research with real agency staff.** Out of scope this round (confirmed 2026-09-01).
  RQ-1 and RQ-6 both get materially weaker without it — revisit if access opens up.
- **Building the classifier.** Explicitly a later goal. It shapes what we record now; it is not
  being built.
