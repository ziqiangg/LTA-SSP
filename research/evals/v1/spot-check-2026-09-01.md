# Spot-check: eval v1 labels (2026-09-01)

Owner spot-check of `research/evals/v1/cases.jsonl`, closing the open item F-010 flagged in its
Interpretation: *"Single labeller (me), so there is no agreement measure — the κ≈0.71–0.76 ceiling
from F-007 cannot be checked against anything here. Owner spot-check pending."*

**Method:** each `label_basis` was read against the matching `cases-raw.jsonl` description, without
re-deriving the answer independently first (per the handover instruction — this is a check, not a
re-label). No case in `cases.jsonl` / `cases-raw.jsonl` was edited by this pass.

**Result:** 13/15 agree outright, 1 agree-with-a-note, 1 genuine disagreement. No case revealed a
label that looks unsupported by its description — the disagreement is about how the answer set
*represents* a defensible-but-dangerous reading, not about whether the reading is defensible at
all.

## Verdicts

| id | verdict | note |
|---|---|---|
| EV-001 | agree | Hosting genuinely unstated; fork is real. |
| EV-002 | agree | Hosting stated (gov commercial cloud); WOGAA and traffic ambiguity both real. |
| EV-003 | agree | Only case that resolves cleanly; math checks (200k/mo = 2.4M/yr > 1M). |
| EV-004 | agree | Applications-to-visits gap is a real, not manufactured, ambiguity. |
| EV-005 | agree | Same hosting fork as EV-001, independently supported. |
| EV-006 | agree, see below | Both answers defensible — promoted as evidence to F-004, not a disagreement. |
| EV-007 | agree, minor note | `composite` tag is a stretch here (dual internal/public purpose, not a DSS traffic reading like the other `composite`-tagged cases) — plausible but worth a second look if the ambiguity vocabulary is ever audited. Not a relabel. |
| EV-008 | agree | Widest set in the pilot, and the description genuinely supports it — vendor-run, architecture unstated. |
| EV-009 | agree | "SharePoint-based" correctly identified as not disambiguating hosting. |
| EV-010 | agree | Only case where sensitivity is unambiguous; correctly not tagged `sensitivity-inferred`. |
| EV-011 | agree | Cloud stated, only sensitivity uncertain — correctly the only ambiguity tag. |
| EV-012 | agree | 40k MAU vs. 1M visits/yr threshold genuinely undecidable without a sessions-per-user assumption. |
| EV-013 | **disagree**, see below | `sandbox` on equal footing with `medium-risk-cloud` understates the risk. |
| EV-014 | agree | F-002's "permitted but not required" resolution correctly makes both standalone and compound answers acceptable. |
| EV-015 | agree | Card/eNETS-out-of-scope reasoning is correct (gateway handles it under Finance's merchant account); hosting fork is real. |

## EV-006 — promoted to F-004 as evidence, not logged as a disagreement

`acceptable_answers: [["medium-risk-cloud"], ["high-risk-cloud"]]` for an analytics warehouse
(S3/Redshift/Airflow/dbt) with untokenised NRIC in the raw layer. The `label_basis` already
identifies this as "exactly the q5 compounding defect in F-004": wizard q5 asks one yes/no question
that compounds two independent facts (CII designation, and Confidential/Sensitive-High-and-cloud),
so a Confidential-High cloud system that is *not* CII has no way to avoid routing toward
`high-risk-cloud` even though that profile exists for CII systems specifically.

Both answers are correctly listed as acceptable given the tree's literal behavior. This isn't a
disagreement about the label — it's a real, synthetic demonstration of a defect that was previously
only described structurally. Added to F-004 as a new evidence bullet.

## EV-013 — genuine disagreement

`acceptable_answers: [["medium-risk-cloud"], ["sandbox"]]`, ordered deliberately (per
`label_basis`) with `medium-risk-cloud` first, for a staging environment whose anonymisation script
has been failing silently since June and now holds live citizen data.

I don't think `sandbox` belongs in the set on the same footing as `medium-risk-cloud`. Applying it
means 3 mandatory controls plus 114 optional for an environment holding unmasked PII — a
substantively under-protective outcome, not a merely "different but reasonable" reading. The case
is explicitly adversarial by construction (per its own `label_basis`), built to test exactly this:
whether the environment label or the data it holds should govern. Two things follow from taking
that construction seriously:

1. `sandbox` is *tree-reachable* (a user answering q4 literally would land there) but not
   *defensible* the way EV-006's two answers both are. Those are different categories, and the
   current schema (a flat list of equally-weighted answers, order not yet scored) doesn't
   distinguish them.
2. This directly answers F-010's open question, "Should `acceptable_answers` be ordered by
   preference?" — yes. The existing deliberate ordering on EV-013 is doing real work that the
   schema doesn't yet formalize.

Recorded as an update to F-010 (Interpretation + Open Questions), not a new finding — F-010 already
names this exact case in its own Implications section. `cases.jsonl` is left unedited; this is a
recommendation for the schema and a logged disagreement, not a relabel.

## New finding filed: F-011

Reviewing all 15 answer sets together surfaced something not visible case-by-case: 6 of 15
(EV-001, EV-005, EV-007, EV-009, EV-010, EV-015) resolve to the identical two-answer fork — a
cloud-risk tier vs. `low-risk-on-premises` — purely because hosting is unstated. F-010's tag-
frequency table already shows `hosting-unknown` as the single most common tag (8/15), but doesn't
capture that over a third of the pilot shares one identical answer *pair*. See
`research/findings/F-011-eval-answer-set-homogeneity.md`.
