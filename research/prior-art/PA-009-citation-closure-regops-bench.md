---
id: PA-009
title: Citation-Closure Retrieval and Per-Rule Attribution for Real-World Regulatory Compliance QA (RegOps-Bench, RefWalk)
source: https://arxiv.org/html/2605.29742v1
kind: paper
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
A benchmark and retrieval method for answering compliance questions over a hierarchy of
regulations, where the correct answer is not one passage but the *complete* set of governing
rules. It is the most directly transferable piece of retrieval research found for our
downstream "free-text description → relevant controls" goal, because it targets the same
failure our tool would have: returning some relevant controls rather than all of them.

## Mechanism
**Task reframing.** The paper argues regulatory QA is not multi-hop QA. Multi-hop QA resolves
an entity; compliance QA must "retrieve the exhaustive set of governing articles and detail
the precise claims derived from each rule". The target is *citation closure* — the complete,
deterministic set of articles needed to answer a query — which makes **recall of a set**, not
rank of a passage, the metric that matters.

**Benchmark.** RegOps-Bench: 250 QA pairs over 12 Korean R&D regulations spanning five
authority tiers, from statute down to operational manual; 718 procedural articles, ~478K
subword tokens. Questions are difficulty-stratified into L1 (single lookup), L2
(conditional / 2-reference), L3 (multi-hop, cross-document) and L4 (conditional multi-hop).
Closure is formalised by four expert rules: domain anchoring, parallel-group expansion,
exception handling, and sanction exhaustion.

**Method (RefWalk).** A shared *topic anchor* — core procedural intent plus facet conditions —
drives retrieval across three semantic views (narrow, mid, wide). Candidates are fused with
*Reciprocal Rank MAX* rather than the usual sum, explicitly to preserve specialist signals
from whichever view is right for that difficulty tier instead of averaging them away. At
generation time, each claim is bound to its governing article through a per-rule attribution
schema emitted as JSON, not as a free-text citation footer.

**Results.** Retrieval at Top-10: dense baseline 54.4 Recall@10 and 35.6 FullCov@10; RefWalk
63.8 and 44.4. End-to-end Citation F1 (Qwen 35B): RefWalk 54.2 vs NativeRAG 46.1, +8.1.

**Failure modes named.** Plain dense retrieval "cannot navigate explicit, multi-tiered
delegations" and "collapses significantly" on L3/L4. Systems treat citation as "post-hoc
annotation" with no "structural guarantees" between claim and source, producing "systemic
attribution failures".

## Transfer to LTA-SSP
1. **FullCov, not Recall@k, is our metric.** The headline number to internalise is that even
   the improved system achieves only 44.4 *full coverage* at Top-10 — i.e. in more than half
   of cases it misses at least one governing rule. A control-recommendation tool that misses
   one mandatory (L0) control has failed in a way a search engine has not. This should set
   the acceptance criterion in the `eval-set` skill: score complete-set coverage per query,
   and report it separately from mean recall, because the two diverge sharply.
2. **Our corpus has the structure this method exploits, and we should encode it.** SSP
   controls sit in 26 domains with cross-references, and level is a join against a profile —
   a two-tier hierarchy at minimum. RefWalk's gain comes from traversing declared structural
   links rather than embedding everything flat. Before any semantic search is worth building,
   extracting the explicit cross-references between SSP controls into
   `docs/assets/data/` would be the higher-value move — and it is checkable, unlike an
   embedding.
3. **The three-view (narrow/mid/wide) anchor is implementable statically.** For a
   zero-dependency site, this maps onto searching control title, control statement, and
   domain description as three separate indexes and fusing by rank-max. That is a plain-JS
   client-side change to `docs/assets/js/`, needs no model, and captures the paper's actual
   structural insight — that a single flat similarity ranking loses whichever signal is
   specialist for the query.
4. **Per-rule attribution as JSON is the right output contract for the future classifier.**
   Binding each claim to its control id in structured form, rather than letting a model write
   prose with control numbers in it, is what makes the output verifiable against
   `controls.json`. Record this as a design constraint now: the classifier returns
   `{control_id, claim, evidence_span}`, never free text.
5. **Closure rules are authorable for our corpus.** Their four rules (domain anchoring,
   parallel-group expansion, exception handling, sanction exhaustion) are a template. Ours
   would plausibly be: domain anchoring, *profile-level expansion* (if a control is returned,
   return its level for the user's system type), and *nesting expansion* (a high-risk system
   inherits everything the lower tiers require). The second and third are mechanical given
   `profiles.json` and would raise coverage with no model involved.

## Limits
The corpus is 12 Korean R&D regulations — a legal hierarchy with explicit typed citations and
statutory delegation. The SSP has no comparable delegation graph; our "hierarchy" is domain
grouping plus a profile join, which is much flatter, so the headroom RefWalk exploits may
largely not exist for us. The benchmark is also *question* → articles, not *system
description* → controls: a question names the procedure it is about, whereas a free-text
system description does not name anything, which is a harder retrieval problem the paper does
not address. 250 QA pairs is small, results are single-language, and the reported gains
(+9.4 Recall@10, +8.1 Citation F1) leave absolute performance well below anything one would
ship as an authoritative answer — which supports positioning any such feature as a
discovery aid with a visible "not exhaustive" caveat rather than as a compliance determination.

## Quotes
- Task: models must "retrieve the exhaustive set of governing articles and detail the precise
  claims derived from each rule".
- Distinction from multi-hop QA: regulatory compliance requires navigating "typed citation
  rules" with "complete evidence-set closure" rather than finding a single entity.
- Benchmark scale: 250 QA pairs, 12 Korean R&D regulations, five authority tiers, "718
  procedural articles", "roughly 478K subword tokens".
- Fusion choice: candidates are fused via "Reciprocal Rank MAX (RRM)" rather than sum-based
  aggregation, preserving "specialist signals" at each difficulty tier.
- Attribution: claims are structured within a "per-rule attribution schema" binding each claim
  to its governing article via JSON, not free-form footers.
- Numbers: dense baseline "54.4" Recall@10 / "35.6" FullCov@10; RefWalk "63.8" / "44.4".
  End-to-end Citation F1 (Qwen 35B): RefWalk "54.2" vs NativeRAG "46.1", "8.1" point
  improvement.
- Failure mode: standard dense retrieval "cannot navigate explicit, multi-tiered delegations"
  and "collapses significantly" on L3/L4 queries.
- Why citations break: existing systems treat "citation" as "post-hoc annotation", lacking
  "structural guarantees" between claims and sources, causing "systemic attribution failures".
