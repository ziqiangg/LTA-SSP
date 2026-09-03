---
id: ADR-007
title: Hosting-unknown hedges with the on-premises baseline, matching the CII hedge idiom
date: 2026-09-03
status: accepted
findings: [F-004, F-005, F-012, F-013]
---

## Context

`docs/find-your-system-type/index.html`'s own lead copy states the wizard's purpose: *"a quick
way to build a starting baseline... When unsure, tick more than one and double-check the result
against the official pages it links to."* The tool is explicitly designed for uncertain users, and
already honours that for two of its five characteristics — the sensitivity rung is a checkbox
group ("tick one, or several if unsure") and CII designation hedges by composing both
`medium-risk-cloud` and `high-risk-cloud` when left unanswered (ADR-005).

Hosting had no such affordance. `resolve()` returned `{incomplete: true}` the instant hosting was
unticked with no GenAI/digital-service overlay to fall back on — a plain two-option radio with no
"tick several" idiom and no "leave unticked to hedge" note, unlike every other uncertain-input
path in the same form.

**F-013** (RQ-6's baseline scoring run, 2026-09-03) quantified the consequence: 8 of the 15 pilot
cases resolved to `incomplete`, all `hosting-unknown`, all because the sensitivity-rung question
only renders once `hosting === "cloud"` is explicitly ticked. Several of those 8 (e.g. EV-001,
EV-005, EV-009, EV-015) state clearly sensitive data — NRIC, payroll, case files — without ever
stating where the system runs. A user reading the wizard's own "tick more than one if unsure"
instruction and trying to apply it to hosting **could not**, because there was nothing to tick.

This is evaluated as a real, narrow site-design gap independent of RQ-6's raw numbers — RQ-6 scores
the wizard as an exact-match classifier against blind text, a harsher task than what the tool
actually promises its own users, so the 20% Top-1 figure is not itself the justification. The
justification is the inconsistency between the tool's stated behavior and its actual behavior on
one axis.

**Why on-premises specifically, and why not sandbox too:** F-004 issue 2 already established the
standard defines exactly one on-premises template regardless of sensitivity level — it's
disclosed today in the hosting radio's own hint text ("The standard defines only one on-premises
template"). That means "sensitivity known, hosting unknown" has a well-defined honest answer:
show the sensitivity-implied cloud tier(s) *and* the single on-premises profile, since sensitivity
doesn't change which on-premises profile applies anyway. F-012 separately established there is no
on-premises `sandbox` equivalent upstream — inventing one to hedge toward would assert something
the corpus doesn't support, exactly the kind of guess this tool's design already avoids elsewhere
(F-012's own conflict check exists for this reason).

## Decision

When `hosting` is left unanswered (`""`), the sensitivity-rung and CII questions become reachable
anyway (previously gated behind `hosting === "cloud"`), and ticking `low` or `sensitive` composes
the resulting cloud tier(s) **together with** `low-risk-on-premises`, disclosed via an advisory
note. `sandbox`-only ticks are excluded from this hedge and resolve exactly as before
(cloud-assumed) — F-012's corpus gap stands, not papered over.

Concretely (`docs/assets/js/wizard.js`):
- The sensitivity-rung and CII fieldsets render whenever `hosting !== "on-premises"` (was
  `hosting === "cloud"`) — so they also appear while hosting is blank.
- `resolve()`'s cloud-tier branch runs whenever `hosting !== "on-premises"` and a rung is ticked
  (was gated to `hosting === "cloud"` only); when `hosting === ""` and `low` or `sensitive` was
  ticked, `low-risk-on-premises` is additionally unioned in with an advisory note.
- A new hint note appears next to the hosting question itself, while it's unticked, pointing the
  user at this behavior (mirroring the CII fieldset's existing "Not sure?" note).
- Explicitly ticking `on-premises` still clears any ticked rungs (existing behavior, unchanged) —
  this hedge only applies while hosting is genuinely unanswered, never as an override of an
  explicit choice.
- The two existing conflict blocks (`on-premises` + a rung ticked together; `sandbox` + a
  CII-reaching-`high-risk-cloud` resolution) are unchanged and still fire, including when hosting
  is blank for the second one.

This extends ADR-005's own pattern (compose conservatively under disclosed uncertainty) one axis
further, rather than introducing a new interaction idiom — consistent with the tool's existing
design language and its own stated promise to users.

## Consequences

**Makes easy:** a user who knows their data's sensitivity but not their hosting arrangement now
gets an honest, disclosed, composed baseline instead of nothing — matching what the tool's own
copy already promises. `EV-001/005/007/009/010/015`-shaped cases in F-013's pilot become
resolvable; `EV-008`/`EV-012` (which state no sensitivity signal at all) correctly remain
`incomplete` — this doesn't make the wizard guess where the text gives it nothing to work with.

**Makes hard / forecloses:** the baseline `resolve()` branching ADR-006 pinned as of 2026-09-02
(`wizard.js` @ `d437c00`) is now stale — ADR-006 is amended with a dated note, and RQ-6's scoring
run needs re-deriving ticks and re-running against the new question set before any new number is
cited. A hosting-unknown, sensitivity-ticked result now always includes `low-risk-on-premises`
alongside the cloud reading, which is a wider (more conservative) answer set than before — this is
the same precision-for-safety tradeoff ADR-005 already accepted for CII, now paid on this axis too
where it fires.

## Alternatives considered

- **Add a third explicit hosting option ("Not sure / third-party managed") instead of reusing the
  blank state.** Rejected — the blank state already means "unanswered" everywhere else in this
  form (CII's hedge reuses exactly this pattern), and hosting's two options are already mutually
  exhaustive in the real world (every system is cloud or on-premises), so a third radio value
  would need its own bespoke handling for no behavioral gain over just making blank productive.
- **Extend the on-premises hedge to `sandbox` ticks too**, inferring an on-premises pilot/sandbox
  reading. Rejected — F-012 found no such profile exists upstream; inventing one would assert a
  fact the corpus doesn't support, which is exactly what this tool's conflict-block design
  elsewhere refuses to do.
- **Restructure question order** (ask sensitivity before hosting unconditionally, or merge them
  into one screen). Rejected as overcomplicating a narrow, well-understood gap — the fix keeps
  hosting first and only relaxes when the *later* questions become reachable, which is a smaller,
  more auditable diff than reordering the form.
