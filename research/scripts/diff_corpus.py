#!/usr/bin/env python
"""Compare a fresh scrape against the shipped corpus and write a review report.

Nothing under docs/assets/data/ may change until this report has been read. See the
`corpus-ingest` skill for the promotion procedure.

Usage:
  python research/scripts/diff_corpus.py            # writes the dated report
  python research/scripts/diff_corpus.py --stdout   # print instead of writing

Inputs:  research/corpus/scraped/controls.json  (from scrape.py)
         docs/assets/data/controls.json         (shipped)
Output:  research/corpus/scrape-diff-<date>.md
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[2]
SCRAPED = ROOT / "research" / "corpus" / "scraped" / "controls.json"
SHIPPED = ROOT / "docs" / "assets" / "data" / "controls.json"
OUT = ROOT / "research" / "corpus"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def sort_key(cid):
    m = re.match(r"^([A-Za-z]+)-(\d+)$", cid)
    return (m.group(1), int(m.group(2))) if m else (cid, 0)


# Single source of truth for how the shipped `guidance` field is composed. Importing
# it (rather than restating it) keeps this diff honest: if promote.py changes how it
# composes guidance, the diff must change with it or it reports false positives.
from promote import compose_guidance as rebuild_guidance  # noqa: E402


def build(out):
    up = {c["id"]: c for c in load(SCRAPED)}
    lo = {c["id"]: c for c in load(SHIPPED)}
    L = out.append

    L("# Scrape diff — upstream vs shipped")
    L("")
    L("Generated `%s` by `research/scripts/diff_corpus.py`." % date.today().isoformat())
    L("Upstream: %d controls · Shipped: %d controls" % (len(up), len(lo)))
    L("")

    # ---------------------------------------------------------------- membership
    L("## 1. Membership")
    L("")
    only_up = sorted(set(up) - set(lo), key=sort_key)
    only_lo = sorted(set(lo) - set(up), key=sort_key)
    if not only_up and not only_lo:
        L("No difference — the same 248 control ids appear in both. "
          "**No controls were missed by the original scrape.**")
    else:
        if only_up:
            L("**Upstream only (%d)** — missing from the shipped corpus:" % len(only_up))
            for cid in only_up:
                L("- `%s` %s" % (cid, up[cid].get("title", "")))
        if only_lo:
            L("**Shipped only (%d)** — no longer upstream, or a parse miss:" % len(only_lo))
            for cid in only_lo:
                L("- `%s` %s" % (cid, lo[cid].get("title", "")))
    L("")

    # ------------------------------------------------------------- schema fields
    L("## 2. Fields upstream that the shipped schema does not carry")
    L("")
    up_fields = Counter(k for c in up.values() for k in c)
    lo_fields = Counter(k for c in lo.values() for k in c)
    L("| field | upstream | shipped | note |")
    L("|---|---|---|---|")
    mapping = {
        "statement": "= shipped `description`",
        "recommendations": "first half of shipped `guidance`",
        "risk": "second half of shipped `guidance`, after `Risk: `",
        "links": "shipped `citations` was derived from these; upstream carries real hrefs",
        "group": "domain name; shipped keeps only `domainId`",
        "sourceUrl": "**not in shipped schema** — per-control provenance",
        "retrievedAt": "**not in shipped schema** — provenance timestamp",
    }
    for f in sorted(set(up_fields) | set(lo_fields)):
        L("| `%s` | %d | %d | %s |"
          % (f, up_fields.get(f, 0), lo_fields.get(f, 0), mapping.get(f, "")))
    L("")

    # ------------------------------------------------------------ guidance gaps
    L("## 3. The 50 missing-guidance controls (F-001)")
    L("")
    gaps = sorted([cid for cid, c in lo.items() if not c.get("guidance")], key=sort_key)
    recovered = [cid for cid in gaps
                 if norm(up.get(cid, {}).get("recommendations")) or norm(up.get(cid, {}).get("risk"))]
    L("Shipped controls with no `guidance`: **%d**" % len(gaps))
    L("Of those, upstream now supplies recommendations and/or risk text: **%d**"
      % len(recovered))
    L("")
    by_dom = defaultdict(lambda: [0, 0])
    for cid in gaps:
        by_dom[cid.split("-")[0]][0] += 1
    for cid in recovered:
        by_dom[cid.split("-")[0]][1] += 1
    L("| domain | gaps | recovered |")
    L("|---|---|---|")
    for d in sorted(by_dom):
        L("| %s | %d | %d |" % (d, by_dom[d][0], by_dom[d][1]))
    L("")
    if recovered:
        cid = recovered[0]
        L("Sample recovery — `%s`:" % cid)
        L("")
        L("> **Recommendations:** %s" % norm(up[cid].get("recommendations"))[:400])
        L("> ")
        L("> **Risk:** %s" % norm(up[cid].get("risk"))[:300])
        L("")

    # --------------------------------------------------------- text differences
    L("## 4. Text differences on controls that already had content")
    L("")
    diffs = {"description": [], "guidance": [], "title": []}
    casing_only = []
    placeholder_only = []
    for cid in sorted(set(up) & set(lo), key=sort_key):
        u, s = up[cid], lo[cid]
        ut, st = norm(u.get("title")), norm(s.get("title"))
        if ut != st:
            diffs["title"].append(cid)
            if ut.lower() == st.lower():
                casing_only.append(cid)
        us, ss = norm(u.get("statement")), norm(s.get("description"))
        if us != ss:
            diffs["description"].append(cid)
            # shipped normalised "[ insert: param, x ]" to "[x]" — inconsistently
            if re.sub(r"\[\s*insert:\s*param,\s*([a-z0-9_\-]+)\s*\]", r"[\1]", us) == \
               re.sub(r"\[\s*insert:\s*param,\s*([a-z0-9_\-]+)\s*\]", r"[\1]", ss):
                placeholder_only.append(cid)
        if s.get("guidance"):
            rebuilt = rebuild_guidance(u)
            if norm(rebuilt) != norm(s["guidance"]):
                diffs["guidance"].append(cid)
    for field, ids in diffs.items():
        L("- **%s**: %d differ" % (field, len(ids)))
        if ids:
            L("  - %s%s" % (", ".join("`%s`" % i for i in ids[:25]),
                            " …" if len(ids) > 25 else ""))
    L("")
    if casing_only:
        L("Of the %d title differences, **%d are capitalisation only** (%s) — upstream uses "
          "sentence case, the shipped corpus title-cased them."
          % (len(diffs["title"]), len(casing_only),
             ", ".join("`%s`" % c for c in casing_only)))
        L("")
    if placeholder_only:
        L("Of the %d description differences, **%d are parameter-placeholder formatting only** "
          "— upstream renders `[ insert: param, ac-3_prm_3 ]`, the shipped corpus rewrote some "
          "to `[ac-3_prm_3]` but not all. That inconsistency is itself a defect."
          % (len(diffs["description"]), len(placeholder_only)))
        L("")
    L("`guidance` is composed by `promote.compose_guidance`, imported here so the two cannot "
      "drift: `recommendations` followed by `Risk: <risk>` for cybersecurity or "
      "`Rationale: <rationale>` for dss.")
    L("")

    # ------------------------------------------------------------- parameters
    L("## 5. Parameters and links")
    L("")
    up_par = {cid for cid, c in up.items() if c.get("parameters")}
    lo_par = {cid for cid, c in lo.items() if c.get("parameters")}
    L("- parameters: upstream %d controls, shipped %d. "
      "Upstream-only: %s. Shipped-only: %s."
      % (len(up_par), len(lo_par),
         ", ".join(sorted(up_par - lo_par, key=sort_key)) or "none",
         ", ".join(sorted(lo_par - up_par, key=sort_key)) or "none"))
    up_link = {cid for cid, c in up.items() if c.get("links")}
    lo_cit = {cid for cid, c in lo.items() if c.get("citations")}
    L("- links/citations: upstream %d controls carry hrefs, shipped %d carry `citations`."
      % (len(up_link), len(lo_cit)))
    L("  Upstream-only: %s" % (", ".join(sorted(up_link - lo_cit, key=sort_key)) or "none"))
    L("  Shipped-only: %s" % (", ".join(sorted(lo_cit - up_link, key=sort_key)) or "none"))
    L("")

    # ----------------------------------------------------------------- verdict
    L("## Verdict")
    L("")
    total = sum(len(v) for v in diffs.values())
    if not only_up and not only_lo and total == 0 and not gaps:
        L("**The shipped corpus reproduces upstream exactly.** Same 248 ids, and zero "
          "differences in title, description or guidance. Nothing to promote.")
    elif not only_up and not only_lo and total == 0:
        L("No text differences remain, but %d control(s) still lack `guidance`." % len(gaps))
    else:
        L("**%d text difference(s) and %d missing-guidance control(s).** Review sections 1 and 4 "
          "before promoting — see the `corpus-ingest` procedure in `research/CLAUDE.md`."
          % (total, len(gaps)))
    L("")
    L("Note the shipped schema still concatenates `recommendations` and the risk/rationale "
      "section into one `guidance` field. Splitting them into separate fields remains an open "
      "schema decision (F-008).")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args()
    lines = build([])
    text = "\n".join(lines) + "\n"
    if a.stdout:
        print(text)
    else:
        p = OUT / ("scrape-diff-%s.md" % date.today().isoformat())
        p.write_text(text, encoding="utf-8")
        print("wrote %s (%d lines)" % (p, len(lines)))


if __name__ == "__main__":
    main()
