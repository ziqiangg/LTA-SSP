---
id: PA-010
title: PROPARAG — An Automated Framework for Cybersecurity Policy Compliance Assessment Against Security Control Standards (Saha & Shukla)
source: https://arxiv.org/pdf/2605.07515
kind: paper
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
A control-centric LLM framework that assesses an organisation's free-text policy corpus
against 1,007 NIST SP 800-53 controls, labelling each control's coverage and producing gap
descriptions and recommendations. It is the nearest published analogue to our downstream goal
— free text on one side, a control catalogue on the other — with expert-annotated ground
truth, inter-annotator agreement, five baselines, and ablations. arXiv:2605.07515v1, 8 May
2026.

## Mechanism
**The architectural claim is an inversion.** Rather than querying the control catalogue with
the user's text, PROPARAG iterates over controls and queries the *text* with each control:
"PROPARAG evaluates each security control independently against the policy corpus." For every
control it retrieves candidate policy excerpts, decides coverage, identifies what is missing,
and emits an explanation plus a recommendation. The stated benefit is traceability — a fixed
binding between control, evidence, and outcome.

**Controls are re-represented before matching.** The knowledge base stores id, description,
family and assessment criteria, plus a distilled statement of the control's *objective and the
type of evidence that would satisfy it*. Their example: an access-review control expects who
performs the review, how often, which accounts, how exceptions are handled, how results are
recorded. This is explicitly to "match policy content based on intent rather than exact
wording."

**A three-label rubric** carries the output: FULLY_COVERED (objective clearly addressed with
governance detail — responsibility, scope, process, review, enforcement), PARTIALLY_COVERED
(relevant but incomplete evidence, e.g. topic mentioned but ownership or review frequency
omitted), NOT_COVERED (no evidence, or text too vague/indirect to support a decision).

**Evaluation.** Two real organisational corpora (OrgA: 24 documents, 356 pages, 80,123 words;
OrgB: 31 documents, 395 pages, 80,666 words), each labelled against all 1,007 controls by two
security researchers (7 and 4 years' experience) working independently, then adjudicated.
Cohen's κ = 0.76 (OrgA) and 0.71 (OrgB) — substantial agreement. Ground-truth label
distribution is strikingly skewed away from full coverage: FULLY_COVERED 10.9% / 12.9%,
PARTIALLY_COVERED 41.8% / 43.4%, NOT_COVERED 47.3% / 43.7%. Controls average 32.58 words
across 20 families.

**Results and the ablation ladder.** Best backbone (Sonnet): OrgA accuracy 90.67%, F1 88.54%;
OrgB accuracy 84.91%, F1 82.31%. Open models trail badly (best open F1 66.58% on OrgB), but
model *ranking* is stable across both corpora. Against baselines under a fixed backbone,
PROPARAG beats the strongest (B4, dense RAG + label) by 11.66 points F1 on OrgA and 11.35 on
OrgB. The ordering of the five baselines is the useful finding: single-shot with no retrieval
(B1) is worst; adding retrieval helps a lot; semantic retrieval (B2) beats BM25 (B3),
attributed to abstract control descriptions not matching policy keywords; dense RAG + reranker
(B4) is the best baseline but its single-stage reasoning is "insufficient for strict
control-level auditing"; document-level retrieval (B5) underperforms segment-level.

**Stated limitations.** Performance depends on how well-structured the input policy is;
PARTIALLY_COVERED remains inherently ambiguous with boundary uncertainty even for strong
models; human evaluation is small-scale; multi-document reasoning, cross-policy dependency
and confidence calibration are future work.

## Transfer to LTA-SSP
1. **Iterate over controls, not over the query.** With 248 controls we can afford to evaluate
   every control against a user's system description — 248 cheap judgements instead of one
   retrieval — and get a defined answer for every control rather than a top-k list. This
   directly satisfies the "every control is accounted for" property that 800-53B (PA-005) and
   CAF (PA-002) both demand, and it is the architecture that makes an exhaustive answer
   possible at all. It is also the shape that fits our data: 248 is small enough that
   completeness is affordable, which is a genuine advantage over the 1,007-control setting.
2. **Write the "expected evidence" field into the corpus.** The single most reusable idea here
   is precomputing, per control, *what evidence would satisfy it*. That artefact is useful
   with no model at all — it is exactly the "and here's what to do about it" half of RQ-4, it
   is renderable as static HTML on a control detail page, and it is what makes intent-based
   matching work later. This is a concrete, incremental research deliverable: a
   `research/`-authored expected-evidence field per control, reviewed by a human, that the
   site can ship before any classifier exists.
3. **Adopt the three-label rubric, and expect the middle label to be where it fails.** A
   three-way applies / partially applies / does not apply output with a middle class carrying
   most of the mass (42–43% here) is realistic and maps onto our L0/L1/L2 levels. The paper's
   own limitation section and the boundary-uncertainty finding say the middle class is where
   both models and humans disagree — so our eval set should over-sample the boundary and
   report per-class scores, never headline accuracy.
4. **κ ≈ 0.71–0.76 is the ceiling to design against.** Two qualified experts, with a written
   rubric, on the same corpus, disagreed on roughly a quarter of controls before adjudication.
   Any eval set we build should measure and report inter-annotator agreement before reporting
   any model score, and should treat anything above ~0.75 accuracy on the boundary class with
   suspicion. This is the number to cite when arguing against presenting classifier output as
   authoritative.
5. **Semantic beats lexical here specifically because control text is abstract.** Their B2 > B3
   result matters for a static site: our controls are short (theirs average 32.58 words, ours
   are comparable) and phrased normatively, so a client-side keyword search over control text
   will systematically under-retrieve against a user's concrete system description. That is an
   argument for investing in the expected-evidence field — which contains the concrete
   vocabulary — rather than in a better keyword index.

## Limits
The direction is the reverse of ours in an important way: PROPARAG matches *policy documents*
(what the organisation already wrote, which is control-shaped prose) to controls, whereas we
would match a *system description* (what the thing is, which is not control-shaped at all).
The B2 > B3 result may not survive that shift. It also determines coverage — has this control
been addressed — not applicability — does this control apply to me — and those are different
questions; nothing here helps decide that a control is out of scope. The headline 88.54% F1
comes from a closed commercial model, and the open-model gap (best 66.58%) means the result
does not transfer to anything self-hosted or free, which matters for a public static site with
no backend. Two organisations, one standard, one language, no released dataset stated. And
the framework is a batch analysis pipeline, not an interactive tool — nothing about latency,
cost per run, or how a user would consume 1,007 judgements.

## Quotes
- Architecture: "PROPARAG evaluates each security control independently against the policy
  corpus. For every control, the framework retrieves relevant policy excerpts, determines
  coverage, identifies missing elements, and produces explanations and recommendations."
- Control representation: "For each control, PROPARAG maintains a concise representation of its
  objective along with the type of evidence needed to satisfy it... This representation helps
  the system match policy content based on intent rather than exact wording."
- Rubric, PARTIALLY_COVERED: "The policy corpus contains relevant evidence, but the evidence is
  incomplete. It may mention the topic but omit important details such as ownership, review
  frequency, scope, procedure, enforcement, or exception handling."
- Rubric, NOT_COVERED: "The policy corpus does not provide evidence for the control. No relevant
  text is found, or the retrieved text is too vague, indirect, or unrelated to support a
  coverage decision."
- Agreement: "For OrgA, κ = 0.76, and for OrgB, κ = 0.71. According to standard interpretation
  guidelines, 0.61 ≤ κ ≤ 0.80 indicates substantial agreement."
- Where humans disagree: agreement levels suggest "policy compliance interpretation contains
  inherent judgment components, particularly at the boundary between FULLY_COVERED and
  PARTIALLY_COVERED".
- Label skew: FULLY_COVERED 110 (10.9%) / 130 (12.9%); PARTIALLY_COVERED 421 (41.8%) / 437
  (43.4%); NOT_COVERED 476 (47.3%) / 440 (43.7%) of 1,007 controls, OrgA / OrgB.
- Best results: "Sonnet attains the highest performance on OrgA (Acc: 90.67%, F1: 88.54%) and
  OrgB (Acc: 84.91%, F1: 82.31%)."
- Margin over best baseline: "On OrgA, PROPARAG attains an F1-score of 88.54%, outperforming the
  strongest baseline (B4: Dense RAG + Label) by 11.66 percentage points."
- Retrieval matters: the single-shot baseline performs "substantially worse on both corpora,
  highlighting the limitations of control coverage assessment without explicit evidence
  retrieval."
- Semantic over lexical: "Semantic retrieval (B2) consistently outperforms lexical BM25
  retrieval (B3), showing that abstract control descriptions benefit from embedding-based
  semantic alignment rather than keyword matching alone."
- Single-stage insufficiency: dense RAG's "single-stage reasoning pipeline remains insufficient
  for strict control-level auditing, where explicit coverage criteria must be evaluated
  holistically."
- Residual ambiguity: "the PARTIALLY_COVERED class continues to present inherent ambiguity...
  This can lead to boundary uncertainty, even for stronger models."
