#!/usr/bin/env python
"""Compare a fresh scrape of level-definitions.json against the shipped corpus.

Nothing under docs/assets/data/ may change until this report has been read. See the
`corpus-ingest` skill for the promotion procedure.

Usage:
  python research/scripts/diff_level_definitions.py            # writes the dated report
  python research/scripts/diff_level_definitions.py --stdout   # print instead of writing

Inputs:  research/corpus/scraped/level-definitions.json  (from scrape.py level-definitions)
         docs/assets/data/level-definitions.json         (shipped)
Output:  research/corpus/level-definitions-diff-<date>.md
"""

import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRAPED = ROOT / "research" / "corpus" / "scraped" / "level-definitions.json"
SHIPPED = ROOT / "docs" / "assets" / "data" / "level-definitions.json"
OUT = ROOT / "research" / "corpus"


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def build(out):
    up = json.loads(SCRAPED.read_text(encoding="utf-8"))
    lo = json.loads(SHIPPED.read_text(encoding="utf-8"))
    L = out.append

    L("# level-definitions.json diff — upstream vs shipped")
    L("")
    L("Generated `%s` by `research/scripts/diff_level_definitions.py`." % date.today().isoformat())
    L("")
    L("This is the file F-003 flagged as mattering most — it holds the only "
      "`selectionGuidance` in the corpus and is fetched by no JS file. This is the first "
      "time it's been run through the ingest pipeline rather than trusted on the strength "
      "of a one-time manual check.")
    L("")

    L("## Fields")
    L("")
    L("| field | shipped | upstream | match |")
    L("|---|---|---|---|")
    diffs = []
    for field in ("0", "1", "2", "selectionGuidance"):
        u, s = norm(up.get(field)), norm(lo.get(field))
        match = u == s
        if not match:
            diffs.append(field)
        L("| `%s` | %s | %s | %s |" %
          (field, s[:60] + ("…" if len(s) > 60 else ""),
           u[:60] + ("…" if len(u) > 60 else ""), "yes" if match else "**NO**"))
    L("")
    if up.get("sourceUrl") != lo.get("sourceUrl"):
        diffs.append("sourceUrl")
        L("`sourceUrl` differs: shipped %r vs. upstream %r" %
          (lo.get("sourceUrl"), up.get("sourceUrl")))
        L("")

    L("## Verdict")
    L("")
    if not diffs:
        L("**Shipped reproduces upstream exactly, word for word**, including the Level-1 "
          "risk-impacts sentence. Nothing to promote. The file's `note` field (no formal "
          "decision tool exists beyond this prose) is editorial and not upstream-sourced, so "
          "it isn't compared here — it's preserved as-is on promotion.")
    else:
        L("**%d field(s) differ.** Review before promoting: %s" % (len(diffs), ", ".join(diffs)))
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
        p = OUT / ("level-definitions-diff-%s.md" % date.today().isoformat())
        p.write_text(text, encoding="utf-8")
        print("wrote %s (%d lines)" % (p, len(lines)))


if __name__ == "__main__":
    main()
