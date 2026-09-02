#!/usr/bin/env python
"""Compare a fresh scrape of domains.json against the shipped corpus.

Nothing under docs/assets/data/ may change until this report has been read. See the
`corpus-ingest` skill for the promotion procedure.

Usage:
  python research/scripts/diff_domains.py            # writes the dated report
  python research/scripts/diff_domains.py --stdout   # print instead of writing

Inputs:  research/corpus/scraped/domains.json  (from scrape.py domains)
         docs/assets/data/domains.json         (shipped)
Output:  research/corpus/domains-diff-<date>.md
"""

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRAPED = ROOT / "research" / "corpus" / "scraped" / "domains.json"
SHIPPED = ROOT / "docs" / "assets" / "data" / "domains.json"
OUT = ROOT / "research" / "corpus"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def field_diffs(up, lo, ids, field):
    return [(did, up[did][field], lo[did].get(field))
            for did in ids if up[did][field] != lo[did].get(field)]


def build(out):
    up_list = load(SCRAPED)
    lo_list = load(SHIPPED)
    up = {d["id"]: d for d in up_list}
    lo = {d["id"]: d for d in lo_list}
    L = out.append

    L("# domains.json diff — upstream vs shipped")
    L("")
    L("Generated `%s` by `research/scripts/diff_domains.py`." % date.today().isoformat())
    L("Upstream: %d domains · Shipped: %d domains" % (len(up), len(lo)))
    L("")

    L("## 1. Membership")
    L("")
    only_up = sorted(set(up) - set(lo))
    only_lo = sorted(set(lo) - set(up))
    if not only_up and not only_lo:
        L("No difference — the same 26 domain ids appear in both.")
    else:
        if only_up:
            L("**Upstream only:** %s" % ", ".join(only_up))
        if only_lo:
            L("**Shipped only:** %s" % ", ".join(only_lo))
    L("")

    common = sorted(set(up) & set(lo))

    L("## 2. `name`")
    L("")
    name_diffs = field_diffs(up, lo, common, "name")
    if not name_diffs:
        L("No differences.")
    else:
        for did, u, s in name_diffs:
            L("- `%s` — upstream %r vs. shipped %r" % (did, u, s))
    L("")

    L("## 3. `description`")
    L("")
    L("F-008 flagged `AC`'s shipped description as authored rather than scraped — this section "
      "is where that would surface.")
    L("")
    desc_diffs = field_diffs(up, lo, common, "description")
    if not desc_diffs:
        L("No differences.")
    else:
        for did, u, s in desc_diffs:
            L("- `%s`" % did)
            L("  - shipped:  %s" % s)
            L("  - upstream: %s" % u)
    L("")

    L("## 4. `controlCount`")
    L("")
    count_diffs = field_diffs(up, lo, common, "controlCount")
    if not count_diffs:
        L("No differences.")
    else:
        for did, u, s in count_diffs:
            L("- `%s` — upstream %s vs. shipped %s" % (did, u, s))
    L("")

    L("## 5. `catalog`")
    L("")
    catalog_diffs = field_diffs(up, lo, common, "catalog")
    L("No differences." if not catalog_diffs else
      "\n".join("- `%s` — upstream %s vs. shipped %s" % (did, u, s)
                for did, u, s in catalog_diffs))
    L("")

    L("## 6. `sourceUrl`")
    L("")
    url_diffs = field_diffs(up, lo, common, "sourceUrl")
    L("No differences." if not url_diffs else
      "\n".join("- `%s` — upstream %s vs. shipped %s" % (did, u, s)
                for did, u, s in url_diffs))
    L("")

    L("## Verdict")
    L("")
    total = len(name_diffs) + len(desc_diffs) + len(count_diffs) + len(catalog_diffs) + len(url_diffs)
    if total == 0:
        L("**Shipped reproduces upstream exactly** on every field this scrape can verify. "
          "Nothing to promote.")
    else:
        cats = sum(1 for d in (name_diffs, desc_diffs, count_diffs, catalog_diffs, url_diffs) if d)
        L("**%d field-level difference(s)** across %d category(ies). Review sections 2–6 "
          "before promoting." % (total, cats))
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
        p = OUT / ("domains-diff-%s.md" % date.today().isoformat())
        p.write_text(text, encoding="utf-8")
        print("wrote %s (%d lines)" % (p, len(lines)))


if __name__ == "__main__":
    main()
