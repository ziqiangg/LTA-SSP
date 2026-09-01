# Eval sets

Labelled data for control discovery. See the `eval-set` skill for the record schema, sampling
strategy, ambiguity vocabulary, and metric definitions.

## Known validity limitation — read before citing any v1 number

**No real user-written system descriptions are available** (confirmed 2026-09-01). Available
sources are all *authoritative*, not *user-generated*: the upstream SSP pages and whatever
structured data GovTechSG publishes. Those are excellent for verifying the corpus; they are the
wrong register entirely for eval descriptions.

Consequence: v1 cases are **synthetic**, written from official wording and prior art. Any method
that keys on vocabulary shared with `classificationText` will score too well, because the
descriptions and the labels come from the same source. Therefore:

- **v1 absolute numbers are not trustworthy.** Do not report "the classifier is 84% accurate".
- **Relative comparisons between methods on the same cases are valid**, and are the point of v1.
- Deliberately vary register when writing cases — jargon, omissions, and wrong-but-plausible
  self-descriptions — to widen the gap between the eval and the corpus. This mitigates the problem;
  it does not remove it.
- Keep `provenance` on every case. If real descriptions become available, they go in as a separate
  slice and never mix silently with synthetic ones.

State this limitation in every results file. An unqualified accuracy figure from v1 will be
misread the moment it leaves this folder.

## v1 — not yet built

`v1/cases.jsonl` will hold ~120-160 cases. Before writing any, read the `eval-set` skill: the
record shape matters more than the volume, particularly `acceptable_types` (multiple correct
answers are real here) and the `ambiguity` tags.

Two constraints established during setup, both from findings:

- Output is `(base_type, overlays[], confidence)`, not a single label — the `generative-ai`
  profile is an overlay of 9 controls with no hosting baseline (F-002), and the wizard cannot
  express composite systems (F-004).
- Adjacent-tier errors are asymmetric and must be scored separately — profiles nest, so
  predicting high-when-medium over-serves while medium-when-high under-protects (F-005).

## Baseline first

Score the existing 7-node wizard tree (`docs/assets/js/wizard.js`, mechanically applied) and the
majority-class floor before evaluating anything else. Every later method reports as a delta
against those two numbers.

Results go in `v1/results/<method>-<date>.md`, each recording method, configuration, eval version
and date. A result without its configuration is not reproducible and must not be cited.
