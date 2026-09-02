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

## 2026-09-01 (session 4) — eval spot-check done

- Reviewed all 15 `cases.jsonl` labels against `cases-raw.jsonl` and their `label_basis`, per the
  handover's top item. 13/15 agree outright; EV-007 gets a minor note on tag reuse; EV-013 is a
  genuine disagreement. Written up in `research/evals/v1/spot-check-2026-09-01.md`, which is now
  the pilot's first (single-reviewer) agreement signal against F-007's κ≈0.71–0.76 ceiling.
- **EV-006 promoted to F-004 as evidence**, not logged as a disagreement — it's a concrete synthetic
  case reproducing the q5 CII/sensitivity compounding defect F-004 already described structurally.
- **EV-013 disagreement folded into F-010.** `sandbox` sitting on equal footing with
  `medium-risk-cloud` for a staging environment now holding live citizen PII understates the risk;
  answered F-010's open question on whether `acceptable_answers` order should be meaningful (yes),
  without editing `cases.jsonl` itself — the schema gap (no way to mark "tree-reachable but
  substantively wrong" separately from "genuinely uncertain") stays open.
- **F-011 filed:** 6 of 15 cases share one identical `hosting-unknown` answer pair (cloud tier vs.
  `low-risk-on-premises`), which F-010's tag-frequency table didn't surface. Relevant to scaling the
  eval to 120-160 cases — repeating the current archetype mix would inflate this fork without adding
  signal.
- Fixed a stale field name in the `eval-set` skill (`acceptable_types` → `acceptable_answers`,
  left over from before F-010 renamed the schema).
- **F-002 closed.** The handover asked this session to treat the owner's already-recorded
  "permitted but not required" answer as confirmation and close it out — done: `status` → confirmed,
  `confidence` → high, and the Digital-Services open question resolved the same way (the owner's
  answer covered both templates, not just GenAI). `site_issue: deferred` is unchanged — the wizard
  fix itself still isn't built, only the underlying question is settled. Updated README, QUESTIONS
  (RQ-5).
- Open, unchanged from the handover: ingest pipeline (`corpus-ingest` skill, `corpus-verifier`
  agent, `system-types.json`/`level-definitions.json` diffs), ADR-001 and ADR-002, and all site work
  gated on ADR-001.

## 2026-09-01 (session 4, continued) — ingest pipeline finished

- **`corpus-ingest` skill and `corpus-verifier` agent built.** The skill states the fetch → parse →
  diff → verify → promote procedure once, covering all three targets. The agent can't be exercised
  this session — custom agents only register at session start — so its first real run is next
  session's job; verification below was done directly instead.
- **Extended `scrape.py`, `promote.py`, and added `diff_system_types.py` /
  `diff_level_definitions.py`.** `scrape_system_type()` was rewritten, not just re-capped: it was
  truncating mid-domain-list on both DSS pages before hitting a real bug. Two real bugs caught by
  actually running it, not by writing it:
  - The landing page lists Sandbox **last**, not 6th where `SYSTEM_TYPES` has it — a first-pass
    positional zip() of type ↔ blurb silently swapped Sandbox's blurb with Digital Services
    (Others)'s. Fixed by matching on normalized heading text instead of position.
  - The System Characteristics `Name:` field ("Low-Risk Cloud **System**") is a filled-in template
    example, not the type's display name — the real name is the page's own H1 heading, which is
    what shipped `name` actually matches (7/8 exactly). Would have shown a false 8/8 name mismatch
    if not caught.
  - Also fixed a latent bug in `scrape.py`'s `main()`: subcommands other than `selftest` return
    scraped data, which `sys.exit(data)` was printing to stderr as a fake "error" on every success.
- **Ran the pipeline for real.** `system-types.json`: one genuine correction —
  `sandbox`'s `classificationText` was paraphrased ("Security sensitivity level designated as…"
  vs. upstream's literal "Security Sensitivity Level: …" label, which all 5 other cybersecurity
  types and the live page itself use). Same defect class as F-008, smaller scope — folded into
  that finding rather than filed separately. `level-definitions.json`: verified byte-for-byte
  identical to upstream, including the Level-1 risk-impacts sentence — no promotion needed, but
  now evidenced rather than assumed. One non-fix, deliberately: `low-risk-on-premises`'s own page
  heading is missing a hyphen upstream ("Low-Risk On Premises") — a live upstream typo, not
  promoted, reported in the diff for the record.
- **Verified independently via Chrome**, since `corpus-verifier` wasn't callable yet: navigated to
  the live landing page, `/ssp/sandbox/`, and `/ssp/dss-others/` and read the accessibility tree
  directly (not through the Python parser). Confirmed the sandbox correction is accurate (the live
  label really is "Security Sensitivity Level:"), the level-definitions content matches exactly,
  the on-premises hyphen typo is real (not a parsing artifact), and the DSS page's `Name:`/
  `Description:`/`Security Sensitivity Level:` landmarks match what the parser expects.
- **Found and synced the drift `docs/CLAUDE.md` warns about, live:** `docs/system-types/sandbox/
  index.html` hardcoded the now-corrected paraphrased text. One-line presentation fix to match
  `system-types.json`'s `classificationText` — no other system-type page carried the stale phrasing.
- Small additions along the way: `corpus.py levels` subcommand (level-definitions was previously
  only visible inside `gaps`); `research/CLAUDE.md` and the `ssp-corpus` skill now point at
  `corpus-ingest` for the procedure instead of restating it.
- Open: `domains.json` still only spot-checked, not run through the full pipeline (no
  `diff_domains.py` exists). `corpus-verifier` needs a fresh session before its first real use.
  ADR-001, ADR-002, and site work remain, per the handover.

## 2026-09-01 (session 4, continued) — ADR-001 drafted

- **`research/decisions/ADR-001-baseline-then-tailor-with-visible-tailoring.md` written**, `status:
  proposed`. Decision: serve baseline-then-tailor, not risk-first from scratch — the site's data is
  genuinely baseline-shaped (F-005's nesting) — but make the tailoring step real: (1) compute a
  starting baseline via tick-all-that-apply plus high-water-mark (`min()`) composition instead of
  the single-outcome tree, (2) render every control with a status and a reason rather than a
  filtered list (F-007's convergent prior-art recommendation), (3) treat that baseline as a draft,
  adjustable via a documented override step mirroring FIPS 199 and ISO's Statement of
  Applicability. Step 3's implementation shape is deliberately left open — direction only.
- Grounded in a direct re-read of F-007/F-004/F-005 (not just summaries) plus a direct read of
  `wizard.js` and the relevant `controls.js` filtering logic (`workingControls()`), to check the
  decision against real code rather than description. Finding worth carrying into site work: the
  "show every control with a status" half is a smaller lift than expected — catalog mode already
  renders unfiltered lists — but the "reason" text for excluded controls has **no backing data
  anywhere**, upstream or local; it must be authored, with SP 800-53B §2.4 as a starting
  vocabulary, not derived from a scrape.
- Not yet done: implementing any of the three decision points, and ADR-002 (the guidance schema
  split). `status: proposed` — needs the project owner's sign-off before site work treats it as
  settled.

## 2026-09-01 (session 4, continued) — ADR-002 drafted

- **`research/decisions/ADR-002-split-guidance-into-recommendations-and-risk.md` written**,
  `status: proposed`. Decision: ship `recommendations` and `risk`/`rationale` as separate fields in
  `controls.json`, dropping the composed `guidance` field entirely rather than keeping both
  representations — the scraped format already captures the parts separately, so this is a
  promotion-shape decision, not a re-scrape. Motivated by two independent things pointing the same
  way: F-007's classifier note that a separated risk/rationale signal is more useful than a fused
  string, and handover item 5 (give the Risk: clause its own line), which becomes a clean two-field
  render instead of a string-parsing hack under this decision.
- Explicitly rejected keeping `guidance` alongside the split fields "for convenience" — that
  recreates the exact two-representations-of-one-fact risk `diff_corpus.py`'s
  `compose_guidance`-import coupling exists to prevent elsewhere in this corpus.
  Real migration surface documented in Consequences rather than glossed over: `promote.py`,
  `diff_corpus.py`, at least 8 `guidance`-keyed spots in `corpus.py`, `controls.js`'s render block,
  and both the `ssp-corpus` and `corpus-ingest` skill docs all need updating if this is accepted —
  none of that is done here, direction only.
- Cross-referenced from F-008 (which first recommended this) and RQ-5's remaining items in
  `QUESTIONS.md`.
- Both ADRs from this session are `proposed`, not `accepted` — real review needed before either
  changes site or pipeline code. Handover items remaining: site work (gated on ADR-001 acceptance),
  and the eval-scaling / baseline-scoring research items.

## 2026-09-01 (session 5) — owner ADR review

- Reviewed ADR-001 and ADR-002 against their cited findings and against current code
  (`controls.js`, `promote.py`, `diff_corpus.py`, `corpus.py`); all technical claims in both still
  held.
- **ADR-002 accepted as written** — `status: accepted`. Migration work (`promote.py`,
  `diff_corpus.py`, `corpus.py`, `controls.js`, the `ssp-corpus`/`corpus-ingest` skill docs) is not
  yet started.
- While diffing profiles to build ADR-001's resolution table, found `sandbox` shares
  `low-risk-cloud`'s and `medium-risk-cloud`'s exact 117-control membership and is a strict subset
  of `high-risk-cloud` — filed **F-012**: sandbox is a fourth rung of the hosting ladder, not an
  orthogonal non-production flag.
- **ADR-001 revised**, still `proposed`: added a formal baseline-resolution table (characteristic →
  shape → composition op → provenance tag `[upstream]`/`[derived]`/`[ours]`), three previously-
  unstated conflict cases (on-prem + cloud rung; sandbox + CII; overlay ceiling vs. ticked rung), a
  status/reason taxonomy for step 2 (SP 800-53B §2.4's six scoping categories, explicitly marked as
  borrowed from a different standard, not SSP-sourced), and a scoped-down minimal tailoring record
  for step 3 (`controlId → {added|dropped, note}`, no approval workflow or history — matched to
  what a static site with no backend can actually render).
- Open: ADR-001 still needs a final owner read of the revised resolution table/taxonomy before its
  status can move to `accepted`; site work in README §4 stays gated until then.
- Open (from F-012): does upstream ever define an on-premises or higher-sensitivity sandbox
  variant? Not found in the current scrape.

## 2026-09-02 (session 6) — ADR-001 accepted, gate lifted

- Clarified one sentence in ADR-001 step 2: the NCSC CAF/ISO SoA/SP 800-53B/GOV.UK convergence is
  cited as prior-art evidence for the *status + reason* presentation pattern only — it does not
  expand the control corpus or supply normative content, which stays sourced solely from the SSP
  (`docs/assets/data/*.json`). The one exception (SP 800-53B's taxonomy borrowed as vocabulary in
  step 2) is cross-referenced rather than left implicit. Also fixed a stray "five" → "six" in the
  `scoped-out:*` category count.
- **ADR-001 accepted.** Both ADRs are now `accepted` — `research/README.md` and
  `research/QUESTIONS.md` (RQ-2's direction-set note) updated to match.
- Gate lifted: the handover's condition ("nothing in README §4 site work proceeds until ADR-001 is
  reviewed and accepted") is satisfied. Site work — tick-all-that-apply wizard, status+reason
  rendering, ADR-002's schema migration — can now proceed.
- `instructions.md` (the session-5 scratch handover) is now fully spent: its blocking condition
  (§3) is resolved and its ingest-pipeline/eval items (§1, §2) were already done. Not deleted yet —
  left for the user to remove.

## 2026-09-02 (session 6, continued) — README §4 site work: wizard, status+reason, ADR-002 migration

- **ADR-002 schema migration applied.** `promote.py`'s `compose_guidance()` removed; `controls.json`
  now ships `recommendations` plus exactly one of `risk`/`rationale` per control instead of a
  composed `guidance` string. Ran `promote.py --dry-run` then `--apply` against the existing
  2026-09-01 scraped cache (no re-scrape needed — this was a shape decision, not new content).
  `diff_corpus.py` updated to compare the split fields directly (no more `compose_guidance` import
  coupling for controls); confirmed zero differences post-migration. `corpus.py`'s 9 `guidance`-
  keyed spots (stats, grep --field, control detail, domain flag, gaps) now use a shared
  `has_guidance()`/`tail_field()` helper. `ssp-corpus` and `corpus-ingest` skill docs updated to
  match the new schema.
- **`controls.js` rendering split**: `renderControlCard()` now renders `recommendations` and the
  risk/rationale half as two paragraphs, the second with a bold inline "Risk: "/"Rationale: " label
  — handover item 5, sequenced after ADR-002 as planned.
- **Status+reason rendering (ADR-001 step 2) built.** `workingControls()` no longer `.filter()`s
  out-of-profile controls — it returns every control in the active catalog(s), tagged
  `status: "in-profile"` or `"not-in-profile"`. Not-in-profile controls get a dashed "Not in
  profile" chip, sort after in-profile ones, and show an italic reason line first when expanded.
  Scoped to the mechanical half only — the `scoped-out:*` human-override taxonomy from the ADR
  belongs to the tailoring record (step 3), not built this session, so nothing here fabricates a
  per-control reason beyond "not part of the computed baseline."
- **Tick-all-that-apply wizard (ADR-001 step 1) built**, replacing the old 7-question linear tree.
  `wizard.js` is now a single-page form (hosting radio, conditional sensitivity-rung checkboxes,
  GenAI checkbox, digital-service radio) that resolves ticks to a list of system-type ids and hands
  them to `controls.js` as a comma-joined `type` param — composition (union + high-water-mark level
  merge) happens entirely in `controls.js`'s existing `workingControls()`, reused rather than
  duplicated. The two ADR-flagged conflict cases are surfaced as blocking messages, not silently
  resolved: on-premises + any cloud rung, and sandbox + high/CII (F-012's "no CII sandbox" gap). A
  GenAI+high combination shows an advisory note (classification-ceiling mismatch) but still
  composes. Standalone GenAI/digital-service selection (no hosting tick) is allowed, matching F-002's
  "permitted but not required."
- `controls.js`'s `type` URL param now accepts a comma-joined list of system-type ids for a
  composite baseline (e.g. `?type=high-risk-cloud,generative-ai`) — verified working across a
  same-catalog composite (high-risk-cloud + generative-ai, 141 in-profile / 15 not-in-profile) and a
  cross-catalog composite (low-risk-cloud + digital-services-others, 200 in-profile / 48
  not-in-profile, spanning both catalogs' 248 controls). The `type-select` dropdown itself stays
  single-select — composite selection is wizard-only for now, a deliberate scope cut.
- Manually exercised both pages in Chrome (all three README §4 items) before handing off to
  `site-critic` for the formal desktop/mobile design+accessibility pass; not yet reported back as
  of this entry.
- Not done this session (deliberately out of scope per the user's ask): the minimal tailoring
  record (ADR-001 step 3), and per-control `scoped-out:*` authoring.
- **`site-critic` review landed, 2 fixes applied.** Both pages passed the full docs/CLAUDE.md
  checklist (both widths, focus visibility, reduced motion, 1.4.1, semantics, clean console) with
  one blocking and one non-blocking finding: (1) blocking — the `type-select` dropdown showed its
  blank placeholder for a composite URL (`?type=a,b`) even though the page had correctly filtered,
  giving a sighted or screen-reader user no indication a filter was active; fixed by synthesizing a
  "Combined: X + Y" `<option>` matching the composite value so the select always reflects true
  state. (2) non-blocking — the whole-card `opacity: 0.7` dimming on not-in-profile cards quietly
  pushed the "Not in profile" chip's own text under AA contrast (~3.0:1, opacity compounds with an
  ancestor and can't be undone by a child's own opacity), even though the reason line stayed legible
  throughout; fixed by dropping the opacity rule entirely — chip text, sort-after placement, and the
  reason line already carry the status without needing a dimming effect that cost contrast on the
  one element carrying it. Both fixes verified live in Chrome after the pass.
