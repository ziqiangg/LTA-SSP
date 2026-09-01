---
id: PA-007
title: NIST IR 8477 — Mapping Relationships Between Documentary Standards, Regulations, Frameworks, and Guidelines
source: https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8477.pdf
kind: standard
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
NIST's February 2024 methodology for expressing how a concept in one control document
relates to a concept in another. It is the standard behind the OLIR (Online Informative
References) repository and the thing every "we mapped framework X to framework Y" crosswalk
is measured against. Directly relevant to us in two ways: our 9 Digital Service Standards
domains are largely WCAG restated, which is a mapping we have not characterised; and any
future free-text classifier will need a vocabulary for "this control is *sort of* what you
asked about".

## Mechanism
Four relationship *styles*, ordered by how much information they carry.

**1. Concept crosswalk** — the degenerate case. It asserts only that A and B are related, with
no characterisation at all. NIST is blunt that the use case documentation is then the *only*
source of meaning. Every richer style can be trivially downgraded to a crosswalk by dropping
its types and properties.

**2. Supportive relationship mapping** — six types: *supports*, *is supported by*,
*identical* (exactly the same wording), *equivalent* (same meaning, different wording),
*contrary* (elements that contradict), *no relationship*. `supports` / `is supported by` take
an optional property drawn from ISO 704: *example of* (one way to achieve it — you can
accomplish D without C), *integral to* (a component — you cannot accomplish D without C), and
*precedes* (a prerequisite, not a part). This three-way distinction between optional,
necessary-part, and prerequisite is the most useful thing in the document.

**3. Set theory relationship mapping (STRM)** — five types for logical similarity: *subset
of*, *intersects with*, *equal*, *superset of*, *no relationship*.

**4. Structural relationship mapping** — parent-child within a single hierarchy.

The critical mechanism is the **rationale**, which is a mandatory companion to the
relationship type and comes in three kinds: *syntactic* (word-for-word similarity, no
interpretation), *semantic* (similarity of meaning, some interpretation), *functional*
(similarity of the results of executing the two concepts). NIST's worked example shows the
same pair of concepts receiving *different relationship types under different rationales*:
CSF 1.1 PR.AC-1 vs Privacy Framework PR.AC-P1 differ only in "users" vs "individuals", so
under a syntactic rationale the relationship is *intersects with*, while under a semantic
rationale it is *equal* — or *subset of*, if "users" is a subset of "individuals". More than
one rationale may apply, the SME picks the one they deem most useful, and the same pair may
legitimately be mapped several times under different rationales.

NIST also states a conversion table between styles (subset of → supports (integral to); equal
→ equivalent; superset of → is supported by (integral to)) with one explicit gap: *intersects
with* cannot be converted automatically, because it records that there is overlap but not what
the overlap is. That is a precise statement of where set-theoretic mapping loses information.

Finally, NIST warns against transitive reasoning: relationship types "are unlikely to have
exactly the same meaning in different mappings", and one should not assume the way A supports
B is the way B supports C.

## Transfer to LTA-SSP
1. **Characterise the DSS↔WCAG relationship instead of asserting it.** We describe 9 of our 26
   domains as "largely WCAG". Under IR 8477 that sentence is a bare concept crosswalk — the
   least informative style. Re-expressing it as STRM pairs with an explicit rationale would
   turn a hand-wave into a checkable artefact and, more usefully, would tell a user whether
   satisfying WCAG 2.1 AA *discharges* a DSS control (`equal` / `superset of`) or merely
   overlaps with it (`intersects with`). That distinction is the difference between "you're
   done" and "you're not", and it is the single highest-value guidance we could add to those
   9 domains. It would live as a new `docs/assets/data/` mapping file, not as prose in the
   control text.
2. **The rationale triple is the missing axis in our own thinking about near-duplicate
   controls.** When two SSP controls look alike, "are they the same?" is not a well-posed
   question until you say syntactic, semantic, or functional. For a future retrieval or
   classification component this matters directly: embedding similarity is a *syntactic-to-
   semantic* measure, and the thing a user actually wants is *functional* ("will doing this
   one satisfy that one?"). Recording which rationale an eval set is labelled under should be
   a required field in the `eval-set` schema; without it, inter-annotator disagreement is
   guaranteed and uninterpretable.
3. **`example of` / `integral to` / `precedes` is a ready-made vocabulary for control
   guidance.** Our downstream goal is "controls plus guidance". These three properties let us
   say, in a controlled vocabulary a machine can consume, that MFA is *integral to* an access
   control outcome while a particular logging tool is only an *example of* achieving a
   monitoring outcome, and that identity proofing *precedes* credential issuance. Ordering
   information (`precedes`) is something no current SSP artefact carries and would make an
   implementation-sequence view possible.
4. **`intersects with` is the honest label for most LLM-suggested matches, and it is a dead
   end.** NIST's own conversion gap says an `intersects with` cannot be refined automatically
   — it needs an SME. That is a strong prior for the classifier design: a system that returns
   "these controls are related to your description" is producing `intersects with` edges, and
   the product question is what a human does with them next. Designing for SME review is not
   a fallback, it is what the standard says the data type requires.
5. **Do not chain mappings.** If we ever map SSP → ISO 27001 and rely on someone else's
   ISO 27001 → NIST mapping to reach NIST, IR 8477 explicitly warns the composition is
   unsound.

## Limits
IR 8477 is a *documentation* methodology, not a matching method — it tells you how to record
a relationship an expert has already judged, and says nothing about how to find candidate
pairs or how to validate a mapping. There is no accuracy measurement, no inter-rater
reliability data, and no published disagreement statistics, so it supplies the vocabulary for
discussing crosswalk disagreement but no evidence about its magnitude. It is also
concept-to-concept and stops short of the question we actually care about — mapping a
*system description* to controls is not a documentary-standard mapping at all. Applying it is
expensive: every pair needs a type, a rationale, and documented assumptions, which for our
248 controls against WCAG would be a substantial SME effort we cannot do from the repo.

## Quotes
- Crosswalk degeneracy: "A concept crosswalk indicates that a relationship exists between two
  concepts without any additional characterization of that relationship... a relationship
  statement in a concept crosswalk only indicates that concept A and concept B are related and
  captures no additional information about the relationship between the two concepts." (§4.1)
- Identical vs equivalent: "Identical: Concept A and concept B are identical. They use exactly
  the same wording." / "Equivalent: Concept A and concept B are equivalent. They have the same
  meaning but different wording." (§4.2)
- The ISO 704 properties: "Example of: The supporting concept C is one way (an example) of
  achieving the supported concept D in whole or in part... In other words, one can accomplish
  D without C." / "Integral to: The supporting concept C is integral to and a component of the
  supported concept... In other words, one cannot accomplish D without C." / "Precedes: The
  supporting concept C precedes the supported concept D when concept C must be achieved before
  applying the supported concept D... The supporting concept itself is not part of the
  supported concept." (§4.2)
- The three rationales: "1. Syntactic: How similar is the wording that expresses the two
  concepts? This is a word-for-word analysis of the relationship, not an interpretation of the
  language. 2. Semantic: How similar are the meanings of the two concepts? This involves some
  interpretation of each concept's language. 3. Functional: How similar are the results of
  executing the two concepts?" (§4.3)
- The five STRM types: "1. Subset of... 2. Intersects with: Concept A and concept B have some
  overlap, but each includes content that the other does not. 3. Equal: Concept A and concept
  B are the same, although not necessarily identical. 4. Superset of... 5. No relationship:
  Concept A and concept B are unrelated; their content does not overlap." (§4.3)
- Rationale changes the answer: "With a rationale of syntactic, the relationship type would be
  intersects with because the two overlap, but each includes content that the other does not.
  However, with a rationale of semantic, the relationship type would be equal if 'users' and
  'individuals' have the same meaning in their respective sources, subset if 'users' was a
  subset of 'individuals,' and so on." (§4.3)
- The conversion gap: "set theory intersects with relationships cannot be automatically
  converted because they only indicate overlap between the concepts, not the nature of that
  overlap." (§4.5)
- Against transitivity: relationship types and properties "are unlikely to have exactly the
  same meaning in different mappings because each use case will be different... be careful not
  to assume that the way concept A supports concept B is the same as the way concept B
  supports concept C." (§4.2)
- STRM is already in our target ecosystem: "The set theory relationship mapping style has been
  supported by NIST OLIR since its launch, and it is also leveraged by the NIST Open Security
  Controls Assessment Language (OSCAL) to support automated cybersecurity control assessment."
  (§4.3)

## Note on a conflicting secondary source
The Secure Controls Framework's STRM page (securecontrolsframework.com/start-here/
set-theory-relationship-mapping-strm) presents the five set-theory types *plus* a 1–10
"strength of relationship" score. That numeric score does not appear in NIST IR 8477; it is an
SCF extension presented under NIST's name. Treat any strength figure in SCF crosswalks as
vendor-defined, not NIST-defined.
