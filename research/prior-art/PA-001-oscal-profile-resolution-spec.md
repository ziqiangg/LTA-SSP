---
id: PA-001
title: OSCAL Profile Resolution Specification
source: https://pages.nist.gov/OSCAL/learn/concepts/processing/profile-resolution
kind: standard
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
NIST's normative specification for how an OSCAL *profile* (a tailoring of controls drawn
from one or more catalogs) is deterministically transformed into a standalone OSCAL
*catalog* containing exactly the selected, reorganised and amended controls. It is the
formal answer to "given a system's baseline, what is my effective control set?" — expressed
as a pure, repeatable function from (catalog, profile) to catalog.

## Mechanism
Three sequential phases.

**1. Import (selection).** Each `import` names an `href` (a catalog *or another profile*)
plus selection directives:
- `include-all` — every control and group including nested ones.
- `include-controls/with-ids` — exact id match.
- `include-controls/with-matching` — glob pattern match on control id.
- `exclude-controls` — same matching machinery, opposite effect. Conflict rule is
  unconditional: anything both included and excluded is excluded, regardless of how
  specific the including directive was.

Ancestry defaults are asymmetric and matter: including a control includes its **parents**
by default (`with-parent-controls` defaults to `yes`) but **not** its children
(`with-child-controls` defaults to `no`). An optional `mapping` child renames control ids
within one import to avoid collisions across catalogs. If an imported href is itself a
profile, the processor recursively resolves that profile first and then imports the
resulting catalog — this is the composition primitive that makes nesting first-class.
Circular imports are a hard error, not a warning.

**2. Merge (organisation).** `combine/@method` decides duplicate handling: `keep`
(default — duplicates are retained, producing invalid output, processors SHOULD warn) or
`use-first` (first encountered in top-down depth-first import traversal wins, rest
discarded). Structure directives: `flat` (default; all controls emitted as a flat list,
groups discarded), `as-is` (preserve source grouping; a control whose parent was not
included is *up-levelled*), or `custom` (author declares the exact group tree and uses
`insert-controls` to place selections into it, with per-group `order` of
`ascending` / `descending` / `keep`). A selection matching nothing is silently ignored.

**3. Modify (amendment).** `set-parameter` binds values into control text: replace
semantics for `class`, `depends-on`, `label`, `usage`, `values`, `select`; append semantics
for `props`, `links`, `constraints`, `guidelines`; multiple directives for one param all
apply in document sequence. `alter` targets one control and carries `add` and `remove`.
`add` is *implicitly bound* (whole control; `position` = `starting` or `ending`) or
*explicitly bound* via `by-id` to an internal object, where `position` may be `starting` /
`ending` (inside) or `before` / `after` (outside); a `by-id` that resolves to nothing makes
the directive inoperative and is ignored rather than an error. `remove` matches on any
combination of `by-id`, `name-ref`, `ns-ref`, `class-ref`, `item-name`, and deletes only
objects meeting **all** given criteria.

**Post-processing.** Back-matter resources are merged with last-uuid-wins, except resources
carrying `prop name:keep value:always`. Output metadata gets a fresh uuid, a resolution
timestamp, a `source-profile` link and a `resolution-tool` marker; the `oscal-version` is
the most recent minor version across all inputs, with a major-version mismatch an error.
Processors SHOULD prune unreferenced objects, with an explicit non-pruneable list
(keep-always props, explicitly imported, referenced from `custom`, referenced from `modify`,
or referenced by `#id` anywhere in the final catalog).

## Transfer to LTA-SSP
This is a direct structural match for the two facts our own analysis established.

1. *Level is a property of the (system type, control) pair, not of the control.* OSCAL says
   the same thing by construction: the catalog holds control text with **no** baseline
   membership, and every baseline fact lives in a profile. The adoptable move is to stop
   treating `level` as something that could ever live in `docs/assets/data/controls.json`
   and treat `docs/assets/data/profiles.json` as a set of eight profile documents whose
   entries are (control-id, level) selections over one level-free catalog. That is roughly
   our current shape already — this spec is the argument for *not* regressing it, and a
   vocabulary (`include-controls`, `with-ids`, `set-parameter`) to name the parts.

2. *Our profiles provably nest.* OSCAL's "an import href may be another profile, resolve it
   recursively then import the result" is exactly the representation for
   low ⊂ medium ⊂ high cloud. We could store `medium-risk-cloud` as
   `{ import: "low-risk-cloud", add: [...], raise-level: [...] }` instead of a flat 200-line
   id list. Benefits: the nesting becomes machine-checkable rather than a fact discovered by
   analysis; the diff *is* the data, so a "what does medium add over low?" view needs no
   set subtraction at runtime; and level promotion (L2 in low → L0 in high) is naturally a
   `set-parameter`-style override rather than a duplicated row.

3. *Resolution is a pure function and can run client-side.* Nothing in the three phases
   needs a server. A ~150-line resolver in `docs/assets/js/controls.js` could take a profile
   document and the catalog and emit the effective control list, which is what the controls
   page already computes ad hoc. Adopting the algorithm shape (select → merge → modify)
   gives us a place to hang future features — an "add these controls because you also handle
   payments" overlay is just a second import.

4. *`with-parent-controls: yes` / `with-child-controls: no`.* Our 26 domains behave like
   OSCAL groups; if we ever nest controls under parent controls, the asymmetric default is
   the right one to copy — pulling a child control into view should pull its parent's
   framing text, not the other way round.

Reject for now: `merge/custom` group authoring and the XML canonical-ordering rules. We have
one grouping (domain) and one serialisation (JSON); that machinery is cost without benefit.

## Limits
The spec solves *resolution*, not *selection*. It assumes someone has already decided which
profile applies to this system — it is the machinery downstream of the exact question RQ-4
asks. There is no notion of confidence, ranking, or a system being two things at once; a
document names exactly one starting profile per import. It also has no free-text surface:
control selection is by id or glob on id, never by meaning. And profile resolution is
deliberately *deterministic and total* — every directive either applies or is ignored, so
there is no representation for "this control probably applies, check with your security
officer", which is the register our downstream free-text tool would need. Finally, the
`keep` default producing knowingly invalid output on duplicates is a trap worth not copying.

## Quotes
- Import defaults, ancestry: "inclusion of a control also causes any of that control's
  ancestors (or parents) to also be included"; "inclusion of a control DOES NOT cause the
  inclusion of any descendants (or children)". (Phase 1, Nested Control Handling)
- Exclusion precedence: "Any control designated to be both included and excluded, MUST be
  excluded". (Phase 1, exclude-controls)
- Recursive profile import: "the tool MUST apply this specification to resolve it, then
  continue processing having imported the resulting catalog". (Phase 1, Handling Profile
  Imports)
- Cycles: "If a processor encounters a circular import...the processor MUST cease processing
  and generate an error". (Phase 1, Circular Import Detection)
- Merge default: "All included controls are output to the target as a flat list directly
  under catalog". (Phase 2, flat)
- Up-levelling: "If an included control has a parent control that was not included, that
  control's output location is up-leveled". (Phase 2, as-is)
- Parameter sequencing: "If more than one set-parameter directive is given for the same
  parameter, all MUST BE applied, in the sequence given". (Phase 3, Setting Parameters)
- Removal criteria are conjunctive: "An object inside the control MUST be removed from the
  output if and only if it meets all of the criteria given by the child objects". (Phase 3,
  Removing Contents)
- Determinism: "profile resolution results in the same catalog regardless of which tool
  resolves it"; "A different serialization format of any given input MUST NOT result in a
  differing output catalog". (Determinism Requirements)
- Implementation freedom: "No requirements are placed on implementation-level details,
  instead, requirements are laid out as what the output of resolution must look like".
  (Determinism Requirements)
