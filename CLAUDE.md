# CLAUDE.md

## Project
**LTA-SSP** — Singapore's System Security Plan (SSP) controls framework, made discoverable.
Upstream source of truth: <https://info.standards.tech.gov.sg/ssp/>.

The repo has **two lanes**:

| Lane | Path | What it is |
|---|---|---|
| **Site** | `docs/` | The shipped browsing tool. Vanilla HTML/CSS/JS, zero dependencies, served by GitHub Pages at `ziqiangg.github.io/LTA-SSP/`. |
| **Research** | `research/` | Investigation into how to better help users find the controls relevant to their system. Python allowed. Not published. |

Research exists to serve two ends: **improve the site**, and **inform a future classifier** that
maps a free-text system description to relevant controls plus guidance. The classifier is not
being built yet, but findings should be recorded in a form it could consume.

Each lane has its own `CLAUDE.md` (`docs/CLAUDE.md`, `research/CLAUDE.md`) that loads only when
you touch that lane. Don't duplicate their contents here.

## Repo map
```
CLAUDE.md            # this router
README.md
docs/                # the site  → docs/CLAUDE.md
  assets/{css,data,img,js}/
  {controls,find-your-system-type,system-types/*}/index.html
research/            # the research → research/CLAUDE.md
.claude/{skills,agents,commands}/
```

## Data, in one paragraph
`docs/assets/data/` holds 248 controls across 26 domains (17 cybersecurity + 9 Digital Service
Standards) and 8 system types. A control has **no intrinsic level** — level is a property of the
`(system type, control)` pair, stored in `profiles.json`. That join is the entire "which controls
apply to me" mechanism today. Full schema and invariants: the **`ssp-corpus`** skill.

## Hard rules (everywhere)
- **No secrets, API keys, or tokens.** This repo is fully public.
- **`docs/` stays dependency-free.** No build step, bundler, framework, or package manager there.
  Python is confined to `research/`.
- **`docs/assets/data/*.json` must stay a faithful reproduction of upstream, and changes only
  through the ingest pipeline** — `research/scripts/{scrape,diff_corpus,promote}.py`. Never hand-
  edit it, never reword it, never "fix" it to make a page or an analysis look better. If it looks
  wrong, re-scrape and read the diff; if upstream itself is wrong, file a research finding.
  (This was previously phrased as an assertion that the data *is* a faithful scrape. It wasn't —
  most `guidance` text had been paraphrased. See F-008.)
- Commit messages: short, imperative (`add controls filter`, not `Added Controls Filter`).
- On this machine the interpreter is `python`, not `python3`.

## Context-window discipline
This is why the structure above exists — follow it:

1. **Never read `controls.json` or `profiles.json` into the main context.** Query them with
   `python research/scripts/corpus.py <subcommand>`, or delegate to the `corpus-analyst` agent.
2. **All web searching and page-reading goes through the `literature-scout` agent.** Source cards
   come back; raw pages don't.
3. **Screenshots go through the `site-critic` agent** unless you need to see one yourself.
4. `research/README.md` is the index — read it to orient, not the whole folder. `JOURNAL.md` is
   append-only; read it by tail.
5. Site work loads `docs/CLAUDE.md`; research work loads `research/CLAUDE.md`. Neither pays for
   the other.

## Router
| Need to… | Use |
|---|---|
| Understand or query the SSP data | `ssp-corpus` skill |
| Preview / screenshot / finish a page | `site-preview` skill, `site-critic` agent |
| Write up a finding, ADR, or journal entry | `research-note` skill, `/research-log` |
| Review external literature or prior art | `prior-art-review` skill → `literature-scout` agent |
| Build or score a labelled eval set | `eval-set` skill |
| Crunch numbers over the corpus | `corpus-analyst` agent |

## Workflow
- Deploy: push to `main`. GitHub Pages source is `main` / `/docs`. No CI.
- Local preview and the "is this page done?" checklist: `site-preview` skill.
