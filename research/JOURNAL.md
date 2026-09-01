# Research journal

Append-only, newest at the bottom. Read by tail — never load the whole file.
Entries record **what happened**; findings record **what is true**. Use `/research-log` to append.

---

## 2026-09-01

- Set up the research lane: split `CLAUDE.md` into a root router plus `docs/CLAUDE.md` and
  `research/CLAUDE.md`; added `.claude/{skills,agents,commands}`; deleted `SKILLS.md` (its preview
  recipe moved into the `site-preview` skill).
- Wrote `research/scripts/corpus.py` so the 218 KB of JSON never has to enter context. Verified
  against known counts: 248 controls, 26 domains, 8 types, and all per-profile level
  distributions match.
- Seeded `QUESTIONS.md` with RQ-1..RQ-6.
- Filed five findings from the setup pass, all evidenced by `corpus.py` runs:
  - F-001 — the 50 missing `guidance` fields are the complete contents of IS/LM/PM/ST; looks like
    a per-domain scrape failure, not editorial omission.
  - F-002 — `generative-ai` is the whole GA domain plus DP-8: an overlay, not a baseline. The
    wizard treats it as terminal, so GenAI users currently get no hosting controls at all.
  - F-003 — `level-definitions.json` is fetched by nothing, and its L1 prose ("assess and apply
    according to risk impacts") is not what the UI's "Baseline" label conveys.
  - F-004 — the wizard tree cannot express composite systems, forces all on-prem to one profile,
    and compounds CII with sensitivity in q5.
  - F-005 — profiles nest: `low ⊂ medium ⊂ high`, and DSS others ⊂ high-impact. On-premises is
    outside the ladder with 7 unique controls.
- Two structural conclusions worth carrying forward: classification output should be
  `(base_type, overlays[], confidence)` rather than a single label (F-002, F-004), and adjacent-tier
  errors are asymmetric so must be scored separately (F-005). Both are now written into the
  `eval-set` skill.
- Open: none of the corpus defects have been checked against the live upstream pages yet — that is
  the cheapest next move and it gates RQ-5.
- Decisions taken: research-only for now (no site fixes, even the F-002 one — recorded as
  `site_issue: deferred`); RQ-4 prior art is the first substantive line of work; no real
  user-written system descriptions are available, so eval v1 will be synthetic and its absolute
  numbers uncitable (written into `evals/README.md`).
- Dispatched two scouts in parallel: upstream verification, and RQ-4 prior art.
- Fixed two setup bugs the dispatch exposed: PA-NNN id collision when two scouts run concurrently
  (now requires disjoint ranges), and the fact that `.claude/agents/` only registers at session
  start (custom agents will be available next launch).

## 2026-09-01 (later) — upstream verification returned

- **F-001 CONFIRMED.** Guidance exists upstream for all four domains (14 spot-checks); official
  OSCAL shows 100% guidance coverage in every group. Scrape failure, fully recoverable. → status
  `confirmed`.
- **F-002 REVISED, confidence high → medium.** Upstream does *not* state the GenAI template is
  additive. It uses the same boilerplate as low-risk-cloud and carries its own sensitivity block —
  standalone framing. The only counter-signal is a pointer inside GA-4's guidance to "relevant IM8
  SSPs". So the standard frames it standalone while giving it contents that cannot work standalone.
  The ambiguity is now the finding; the overlay reading is no longer asserted as fact. Needs a
  human to ask GovTech — no more desk research will settle it.
- **F-006 NEW — official OSCAL source found.** `GovTechSG/tech-standards` publishes IM8 as OSCAL
  1.1.2: 137 controls, 15 groups, 6 profiles. But no GA group, no DSS/WCAG groups, no high-risk /
  on-prem / sandbox / gen-ai / dss profiles, and it is stale (2025-05-13) with counts already
  drifted from the live site. Half coverage — not a drop-in.
- **F-005 CORROBORATED and its open question closed.** OSCAL profiles import cumulatively
  (level-1 imports level-0), so the nesting is a deliberate design property of the standard, not an
  authoring artefact. The UI may rely on it.
- Checked and dismissed: the scout flagged upstream slug differences (`/ssp/gen-ai/` not
  `/ssp/generative-ai/`), but our `sourceUrl` fields already use the correct slugs — only our
  internal ids differ, by design. No defect, no finding.
- Also learned: upstream keeps `risk-statement` as a separate OSCAL prop; our `guidance` field is
  the *website's* concatenation of two fields. Any re-import must decide whether to keep them
  joined.
- Open: (a) ADR needed on the F-001 recovery route — scrape vs OSCAL import vs hybrid, each with a
  different drift failure mode; (b) the GovTech composition question; (c) RQ-4 scout still running.

## 2026-09-01 (later still) — RQ-4 prior art returned, RQ-4 answered

- 13 cards filed, PA-001..PA-013. Synthesized into **F-007**; RQ-4 → answered.
- **Headline is a gap:** every source assumes the system is *already* typed. Nothing in the prior
  art maps a free-text system description to controls. No prior art to copy for goal #2 — we would
  be constructing, not adapting.
- Borrowable mechanisms found: FIPS 199 **high-water-mark composition** (PA-003) answers F-004's
  composite-system problem, and is well-defined for us precisely *because* our profiles nest;
  SP 800-53B App. C gives **overlays** a formal add/modify/eliminate vocabulary (PA-006), naming
  F-002's open question; 800-53B §2.4 supplies the only written taxonomy of *why* a control may be
  dropped (PA-005), which is what F-003 says we lack.
- **F-005 QUALIFIED — I had overstated it.** PA-004 (ASD ISM, closest structural peer, verified
  from published JSON) shows baselines that do *not* nest, because a stricter control **supersedes**
  a laxer one rather than adding to it. Our nesting is contingent on current data, not a law. Any
  diff representation needs removal support, and `profiles.json` needs a build-time nesting
  assertion. Retracted "the UI may rely on it".
- **Eval calibrated (F-007 → `eval-set` skill):** expert inter-annotator agreement on control
  applicability ceilings at κ≈0.71–0.76 (PROPARAG); best full-coverage retrieval is 44.4 FullCov@10
  (RegOps-Bench). First external anchors this project has. Beating them comfortably would indicate
  a leaky eval, not a breakthrough.
- **Framing conflict surfaced:** ISO derives controls from risk and uses the catalogue as a
  completeness check; NIST prescribes a baseline then tailors down. The SSP's one sentence is
  phrased the ISO way while our wizard behaves the NIST way. Needs an ADR — the site is currently
  answering a question the standard did not ask.
- Top site recommendation (deferred, research-only): four independent frameworks converge on
  rendering *all* controls with a status + reason instead of a filtered list. No data-model change,
  `controls.js` presentation only.
- Open: two ADRs now queued (guidance-recovery route; risk-first vs baseline-then-tailor), plus the
  GovTech composition question. Overlay *composition* is unsolved in all prior art — if F-002
  resolves toward overlays, that is unbuilt ground.

## 2026-09-01 (session 2) — scrape built and verified; eval pilot run

- Built `research/scripts/scrape.py` (stdlib, landmark-based, fails loudly) and
  `research/scripts/diff_corpus.py`. Selftest covers the empty-parse failure mode that produced
  F-001. Scraped all 26 catalog pages: 248 controls, every domain count matching.
- Parser bug caught by the diff, not by the tests: DSS pages use `Rationale` where cybersecurity
  uses `Risk Statement`, and render `Group: <name>` as one block instead of two. Fixed; now 156
  risk + 92 rationale = 248.
- **F-008 — the shipped corpus is not a faithful scrape.** Only 42/198 guidance fields reproduce
  upstream exactly. Decisive evidence is spelling: upstream is 243 British / 1 American, shipped
  has 12 American forms, and for 13 of 16 occurrences the British equivalent sits at the same
  position upstream. Plus systematic shortening (346 vs 402 chars mean), title-casing, half-applied
  placeholder normalisation, and synthesised citations. Every record says `status: "scraped"`.
  This is bigger than F-001: silent infidelity across most of the corpus, and it falsifies the
  premise behind our own "faithful scrape, don't edit" rule.
- All 50 F-001 gaps recover at 100% (IS 14/14, LM 21/21, PM 10/10, ST 5/5). Membership perfect —
  no control was ever missed. Diff written to `research/corpus/scrape-diff-2026-09-01-before-promotion.md`.
- **F-009 — site CTA pointed at a 404** on all 8 system-type pages (`../controls/` from two levels
  deep). Reported and fixed by the owner. Post-fix link check: 64 internal refs, 0 broken, 0
  root-absolute. Lesson recorded: the visual checklist structurally cannot catch this class.
- **F-010 — blind eval pilot, 15 cases.** Generator was told nothing about the SSP or the wizard.
  Result: sensitivity stated in 0/15, CII in 0/15, hosting in only 6/15 — and **no case has a
  single correct answer** (mean 2.3 acceptable answers; 5 need compound answers). Blinding held.
- Two eval-schema defects demonstrated, not guessed: `acceptable_types` cannot express compound
  answers (now `acceptable_answers`, a list of answer-arrays), and the ambiguity vocabulary was
  missing its two most common tags — `hosting-unknown` (8/15) and `sensitivity-inferred` (6/15).
  Both fixed in the `eval-set` skill, along with a standing instruction to generate blind.
- Open: (a) owner spot-check of the 15 labels — the pilot's only agreement signal; (b) promotion of
  the verified scrape into `docs/assets/data/` still gated on review; (c) `corpus-ingest` skill and
  `corpus-verifier` Chrome cross-check still to build; (d) ADR-001 on risk-first vs
  baseline-then-tailor still unwritten.

## 2026-09-01 (session 3) — scrape promoted to the shipped corpus

- Reviewed `research/corpus/scrape-diff-2026-09-01-before-promotion.md` and resolved its one blocking question
  before promoting: the 5 controls with shipped citations but no upstream link (AS-11, AS-14,
  CK-2, CK-3, PM-1) are **not fabricated** — each names its standard in upstream prose, just
  without a hyperlink. Preserved on promotion rather than dropped.
- Spot-checked `domains.json`: 5 of 6 sampled descriptions appear verbatim upstream. `AC` does not
  and looks authored. Left alone; recorded in F-008.
- Wrote `research/scripts/promote.py` (dry-run / apply, with invariant asserts) so the rebuild is
  reproducible rather than hand-applied. **Promoted**, measured against git HEAD: 126 guidance
  corrected, 50 recovered from empty, 39 descriptions corrected, 34 citations added/corrected,
  4 titles restored to sentence case, provenance added to all 248. Only 72 guidance fields were
  already right. All 248 now carry guidance; file 156 KB → 285 KB.
- **Caught a regression I introduced**, by spot-checking promoted output against upstream rather
  than trusting the diff: my first `compose_guidance` mirrored the original corpus's DSS mapping
  (rationale only), which silently drops *Control Recommendations* on all 92 DSS controls — BD-2
  lost its "Not required for…" exemptions. Fixed to carry both sections. `diff_corpus.py` now
  imports `compose_guidance` from `promote.py` so the two cannot drift and produce false clean
  diffs.
- Post-rebuild `diff_corpus.py` reports **zero differences** in title, description and guidance.
  Kept both records: `scrape-diff-2026-09-01-before-promotion.md` (the evidence) and
  `scrape-verify-2026-09-01-after.md` (the verification).
- **Invariant rewritten in all three CLAUDE.md files.** Was *"the data is a faithful scrape"* — an
  assertion F-008 falsified. Now *"the data must reproduce upstream and changes only through the
  ingest pipeline"*, with the pipeline commands inline. A rule you maintain, not a state you assume.
- Kept the shipped schema so `controls.js` needed no data-shape change. Deliberately deferred: the
  statement/recommendations/risk split, and rewriting parameter placeholders — upstream renders
  `[ insert: param, x ]` and faithfulness beats prettiness at the data layer. Presentation belongs
  in `controls.js`, which is now noted in `docs/CLAUDE.md`.
- One site change, earned by the new data: citations with a real `url` now render as links
  (`controls.js`). Also fixes the "NIST SP 800-63B (NIST SP 800-63B)" duplication.
- Verified: JSON valid, 248 ids, all profile refs resolve, corpus.py green, node --check on both
  JS files, all routes 200, 64 internal links / 0 broken, browser render check.
- Open: `system-types.json` and `level-definitions.json` still undiffed — the latter matters most
  since F-003 shows it holds the only `selectionGuidance`.
