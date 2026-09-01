---
id: PA-013
title: OSCAL CLI — resolve-profile as a runnable, one-command transform
source: https://oscal-cli.metaschema.dev/guides/resolving-profiles.html
kind: tool
retrieved: 2026-09-01
rq: [RQ-4]
relevance: medium
---

## What it is
The reference command-line implementation of the profile resolution specification in PA-001.
Filed as a short card because it settles one practical question: whether the OSCAL data model
is only a paper standard or something we could actually run in `research/` today against real
government catalogues.

## Mechanism
One command, no configuration:

    oscal-cli resolve-profile profile.json resolved-catalog.json
    oscal-cli resolve-profile --to=json profile.xml resolved-catalog.json
    oscal-cli validate profile.json

Input is a profile in JSON or XML; output defaults to the input's format unless `--to`
converts it. The output is described as a "single, self-contained catalog" containing only the
controls the profile selected, with all parameter values set and all modifications and
additions applied, requiring no external references to interpret. The documented pipeline is
the six-step import → select → exclude → modify → merge → output sequence, matching the
specification's three phases.

Two error classes are called out by name, and they are the two failure modes the spec
declares fatal: an unresolvable import ("Unable to resolve import href 'catalog.json'") and
"Circular import detected". Validation is a separate prior step, so schema conformance and
resolvability are distinct checks.

## Transfer to LTA-SSP
1. **We can test the OSCAL hypothesis without committing to it.** `research/` permits Python
   and external tooling; `docs/` does not. The experiment is cheap and bounded: express our
   8 profiles as OSCAL profile documents over a level-free catalog derived from
   `controls.json`, resolve each with `oscal-cli`, and diff the resolved catalogs against the
   control sets our current `profiles.json` produces. If they match, we have proved our data
   is losslessly expressible in a standard the ASD and FedRAMP already publish in; if they do
   not, the mismatch localises exactly what our model carries that OSCAL's does not — most
   likely the per-pair *level*, which OSCAL has no native slot for and which would have to
   become a prop or a parameter.
2. **The nesting experiment has a concrete form.** PA-001 argued for representing
   medium-risk-cloud as an import of low-risk-cloud plus a diff. `resolve-profile` is the
   oracle that checks such a rewrite is faithful: author the incremental version, resolve it,
   and require byte-equal control sets against the flat version. That is a real regression
   test for a refactor we cannot otherwise verify, and it belongs in `research/scripts/`.
3. **Circular-import detection is a validation we should copy regardless.** If we adopt any
   profile-extends-profile representation in `docs/assets/data/profiles.json`, a cycle becomes
   possible where today it is not. The reference implementation treats it as fatal; whatever
   resolver we write in `docs/assets/js/controls.js` should too, rather than looping.
4. **Validate-then-resolve is the right two-step for our own build.** Separating "is this
   file well-formed" from "does it resolve" is a useful discipline for our data checks, and
   maps onto the build-time nesting assertion argued for in PA-004.

## Limits
This is a JVM command-line tool, so it can never run in `docs/` — the zero-dependency rule
confines it strictly to the research lane, and anything we ship to the browser would be our
own reimplementation of the algorithm rather than this. The documentation is a usage guide,
not a conformance statement: it does not claim full coverage of the specification's harder
corners (`merge/custom` ordering, pruning rules, canonical XML ordering), so agreement with
`oscal-cli` is evidence of correctness, not proof of it. It also resolves profiles and stops
there — nothing about selection, guidance, or presentation, which is where our actual research
question lives.

## Quotes
- The command: `oscal-cli resolve-profile profile.json resolved-catalog.json`; with format
  conversion, `oscal-cli resolve-profile --to=json profile.xml resolved-catalog.json`;
  validation, `oscal-cli validate profile.json`.
- Output property: the resolved catalog is a "single, self-contained catalog" that includes
  only the controls selected by the profile, all parameter values set, and all modifications
  and additions applied.
- Fatal errors, matching the specification: "Unable to resolve import href 'catalog.json'" —
  fix by ensuring "the referenced file exists or URL is accessible"; and "Circular import
  detected" — "Check your profile chain for circular references."
