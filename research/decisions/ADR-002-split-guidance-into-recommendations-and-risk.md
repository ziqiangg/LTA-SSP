---
id: ADR-002
title: Split the composed `guidance` field into `recommendations` and `risk`/`rationale`
date: 2026-09-01
status: accepted
findings: [F-007, F-008]
---

## Context

Upstream publishes three sections per control: *Control Statement*, *Control Recommendations*, and
a third section that differs by catalog — *Risk Statement* for cybersecurity (156 controls),
*Rationale* for DSS (92 controls). The shipped corpus keeps `description` (= statement) as its own
field, but concatenates the other two into a single `guidance` string:
`recommendations + " Risk: " + risk` for cybersecurity, `recommendations + " Rationale: " +
rationale` for DSS — composed once, in one place (`promote.py`'s `compose_guidance()`), and
rendered as one plain paragraph (`docs/assets/js/controls.js:320-325`: `c.guidance` → a single
`<p class="control-guidance">`).

This shape exists because it's what the *original* (pre-rebuild) schema did and `controls.js`
already expected it — not because it's a property of the standard. F-008 found the original
concatenation was worse than cosmetic: for all 92 DSS controls it silently **dropped** Control
Recommendations and kept only Rationale, losing real content (including BD-2's "Not required
for…" exemptions). The 2026-09-01 rebuild fixed the join to keep both halves, but the *shape* —
one composed string, not two queryable fields — was deliberately left alone as "each wants its own
decision" (`promote.py`'s docstring). F-008's own Implications section already recommends
resolving it: *"Upstream's three-way split... is cleaner than the concatenated `guidance`. Adopt
it — the `Risk:` join is a website presentation choice, not part of the standard."*

Two separate motivations point the same direction:

- **Classifier (F-007):** *"Splitting `guidance` into separate statement/recommendations/risk
  fields... would make the risk statement independently queryable, which likely helps the
  classifier."* A future free-text-to-controls system can only use "why this control matters" as a
  distinct signal from "what to do about it" if those are two fields, not one string a regex would
  have to split back apart.
- **Site (handover item 5, independent but related):** the `Risk:`/`Rationale:` clause currently
  runs inline at the end of one paragraph, so it reads as mid-sentence prose rather than the most
  scannable part of the card. `controls.js` has no internal structure to hook a label onto today —
  `c.guidance` is opaque plain text. A schema split gives this a home for free instead of requiring
  controls.js to parse the trailing clause back out of a string it was never supposed to need to
  parse.

The scraped format (`research/scripts/scrape.py`) already captures the parts separately —
`recommendations`, plus `risk` or `rationale` depending on `catalog` — and only `promote.py` fuses
them on the way into the shipped schema. Nothing has to be re-scraped; this is a promotion-shape
decision, not a data-collection one.

## Decision

**Ship `recommendations` and `risk`/`rationale` as separate fields in `controls.json`. Drop the
composed `guidance` field entirely** — don't keep it alongside the split fields as a derived
convenience. A control carries `recommendations` always, plus exactly one of `risk` (cybersecurity)
or `rationale` (DSS), mirroring `compose_guidance()`'s existing catalog branch and the scraped
format's existing field names — no new naming invented, just stop fusing what's already captured
separately.

Rejected the "add the split fields alongside `guidance`, keep both" option: that recreates exactly
the two-representations-of-one-fact risk the ingest pipeline's `compose_guidance`/`diff_corpus.py`
import-coupling exists to prevent (see `corpus-ingest` skill's Invariant 1) — if `guidance` and
`recommendations`/`risk` can drift because one code path updates only one of them, a "clean diff"
stops being trustworthy. One shape, one source of truth.

This ADR decides the **data shape only**. It does not implement the `controls.js` rendering change
(two paragraphs, or one paragraph plus a labelled `Risk:`/`Rationale:` line — handover item 5's
actual design is still open) or any classifier consumption of the new fields — those are follow-up
site and research work, done against a settled schema rather than driving it ad hoc.

## Consequences

**Makes easy:**
- The risk/rationale text becomes independently queryable — `corpus.py grep --field risk`, or any
  future retrieval/classification work, can target "why this matters" separately from "what to do."
- Handover item 5 (give the Risk: clause its own line) becomes a straightforward two-field render
  instead of a string-parsing hack in `controls.js`.
- One derivation path, not two — nothing can drift between a composed and an uncomposed
  representation of the same content, because only one representation exists.

**Makes hard / touches:**
- `promote.py` — `compose_guidance()` is removed (or repurposed as a pure formatter for any UI that
  still wants one paragraph), `FIELD_ORDER` changes, `build_controls()`'s per-field change-tracking
  needs `recommendations`/`risk`/`rationale` counters instead of one `guidance` counter.
- `diff_corpus.py` — imports `compose_guidance` from `promote.py` specifically to diff the composed
  field; that section becomes two field-diffs (recommendations, risk-or-rationale) instead of one.
- `docs/assets/js/controls.js` — `renderControlCard()`'s single `if (c.guidance)` block (lines
  318-325) becomes two: recommendations always, then risk/rationale with a label if present.
- `research/scripts/corpus.py` — no fewer than 8 places reference `"guidance"` directly: the `grep
  --field` choice list, `stats`'s missing-guidance count, `control`'s detail printer, `gaps`'s
  no-guidance scan. All need a `recommendations`/`risk-or-rationale` equivalent.
- `.claude/skills/ssp-corpus/SKILL.md` and `.claude/skills/corpus-ingest/SKILL.md` — both document
  the current `guidance` composition rule in their Schema sections; both need updating to match,
  or they become exactly the kind of stale skill doc that misleads a future session.
- Any already-written research (vocabulary work, if any is ever redone per F-008's instruction to
  redo anything computed over pre-rebuild `guidance`) that assumed one `guidance` string needs to
  account for two fields instead.

**Forecloses:**
- Treating a control's advice as one undifferentiated blob of text. Future site or classifier work
  should treat "recommendation" and "risk/rationale" as distinct signals from here on, not
  re-merge them for convenience.

## Alternatives considered

- **Keep `guidance` as the only field (status quo).** Rejected: perpetuates the exact problem
  F-008 flagged as a schema weakness, and forces handover item 5 into string-parsing rather than a
  clean two-field render.
- **Add the split fields alongside `guidance`, keep both.** Rejected: creates two representations
  of the same content with no single source of truth, the specific failure mode the ingest
  pipeline's evidence-coupling (`compose_guidance` imported, not restated, by `diff_corpus.py`) was
  built to prevent elsewhere in this same corpus. If some consumer genuinely needs one paragraph,
  it can compose it client-side from the two fields — cheap, and doesn't require storing a
  redundant copy.
- **Rename the third section to one generic label for both catalogs** (e.g. always `rationale`,
  dropping the cybersecurity/DSS distinction). Rejected: *Risk Statement* and *Rationale* are
  different upstream concepts (risk of not doing something vs. context for why it applies) —
  collapsing the label loses real information the split was supposed to preserve.
