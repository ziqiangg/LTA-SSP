#!/usr/bin/env python
"""Compare a fresh scrape of system-types.json against the shipped corpus.

Nothing under docs/assets/data/ may change until this report has been read. See the
`corpus-ingest` skill for the promotion procedure.

Usage:
  python research/scripts/diff_system_types.py            # writes the dated report
  python research/scripts/diff_system_types.py --stdout   # print instead of writing

Inputs:  research/corpus/scraped/system-types.json  (from scrape.py types)
         docs/assets/data/system-types.json         (shipped)
Output:  research/corpus/system-types-diff-<date>.md
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[2]
SCRAPED = ROOT / "research" / "corpus" / "scraped" / "system-types.json"
SHIPPED = ROOT / "docs" / "assets" / "data" / "system-types.json"
OUT = ROOT / "research" / "corpus"

# Imported, not restated — if promote.py changes how classificationText is composed, this
# diff must change with it or it reports false positives. Same coupling as diff_corpus.py's
# import of compose_guidance, and just as deliberate.
from promote import compose_classification_text, norm  # noqa: E402


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def build(out):
    up_list = load(SCRAPED)
    lo_list = load(SHIPPED)
    up = {t["id"]: t for t in up_list}
    lo = {t["id"]: t for t in lo_list}
    L = out.append

    L("# system-types.json diff — upstream vs shipped")
    L("")
    L("Generated `%s` by `research/scripts/diff_system_types.py`." % date.today().isoformat())
    L("Upstream: %d types · Shipped: %d types" % (len(up), len(lo)))
    L("")

    L("## 1. Membership")
    L("")
    only_up = sorted(set(up) - set(lo))
    only_lo = sorted(set(lo) - set(up))
    if not only_up and not only_lo:
        L("No difference — the same 8 type ids appear in both.")
    else:
        if only_up:
            L("**Upstream only:** %s" % ", ".join(only_up))
        if only_lo:
            L("**Shipped only:** %s" % ", ".join(only_lo))
    L("")

    L("## 2. `name` — reported only, never auto-promoted")
    L("")
    L("Upstream's page heading is the source of truth for `name` (verified: it matches shipped "
      "for 7/8 types exactly). The System Characteristics `Name:` field is a filled-in template "
      "example, not the type name, and is not compared here — see scrape.py's `templateName` "
      "vs. `heading` note.")
    L("")
    name_diffs = [(tid, up[tid]["name"], lo[tid].get("name"))
                  for tid in sorted(set(up) & set(lo)) if up[tid]["name"] != lo[tid].get("name")]
    if not name_diffs:
        L("No differences.")
    else:
        for tid, u_name, s_name in name_diffs:
            L("- `%s` — upstream %r vs. shipped %r" % (tid, u_name, s_name))
            if tid == "low-risk-on-premises":
                L("  (known upstream typo — the live page's own H1 is missing the hyphen the "
                  "other 7 types use consistently. Not promoted; shipped's hyphenated form is "
                  "correct.)")
    L("")

    L("## 3. `classificationText`")
    L("")
    ct_diffs = []
    for tid in sorted(set(up) & set(lo)):
        composed = compose_classification_text(up[tid])
        shipped = norm(lo[tid].get("classificationText"))
        if composed != shipped:
            ct_diffs.append((tid, shipped, composed))
    if not ct_diffs:
        L("No differences — composed text matches shipped for all 8 types.")
    else:
        for tid, shipped, composed in ct_diffs:
            L("- `%s`" % tid)
            L("  - shipped:  %s" % shipped)
            L("  - upstream: %s" % composed)
    L("")

    L("## 4. `domainsUsed`")
    L("")
    dom_diffs = [tid for tid in sorted(set(up) & set(lo))
                 if up[tid]["domainsUsed"] != lo[tid].get("domainsUsed")]
    if not dom_diffs:
        L("No differences.")
    else:
        for tid in dom_diffs:
            L("- `%s` — upstream %s vs. shipped %s" %
              (tid, up[tid]["domainsUsed"], lo[tid].get("domainsUsed")))
    L("")

    L("## 5. `sourceUrl`")
    L("")
    url_diffs = [tid for tid in sorted(set(up) & set(lo))
                 if up[tid]["sourceUrl"] != lo[tid].get("sourceUrl")]
    L("No differences." if not url_diffs else
      "\n".join("- `%s` — upstream %s vs. shipped %s" %
                (tid, up[tid]["sourceUrl"], lo[tid].get("sourceUrl")) for tid in url_diffs))
    L("")

    L("## 6. Fields this scrape cannot verify")
    L("")
    L("`levelsAvailable`, `totalControls`, and `levelCounts` are not present in any textual "
      "form on the type pages (no \"Level N (n)\" pattern exists) — confirmed by grepping the "
      "full scraped blocks for both DSS types. These are correctly derived from "
      "`profiles.json` today (see `corpus.py stats`), not from this scrape, and are left "
      "untouched by promotion.")
    L("")

    L("## Verdict")
    L("")
    total = len(name_diffs) + len(ct_diffs) + len(dom_diffs) + len(url_diffs)
    if total == 0:
        L("**Shipped reproduces upstream exactly** on every field this scrape can verify. "
          "Nothing to promote.")
    else:
        L("**%d field-level difference(s)** across %d category(ies). Review sections 2–5 "
          "before promoting." % (total, sum(1 for d in (name_diffs, ct_diffs, dom_diffs, url_diffs) if d)))
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
        p = OUT / ("system-types-diff-%s.md" % date.today().isoformat())
        p.write_text(text, encoding="utf-8")
        print("wrote %s (%d lines)" % (p, len(lines)))


if __name__ == "__main__":
    main()
