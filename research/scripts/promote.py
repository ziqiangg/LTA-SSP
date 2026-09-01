#!/usr/bin/env python
"""Promote a verified scrape into the shipped corpus.

This is the ONLY sanctioned way docs/assets/data/*.json may change. Run `scrape.py all`,
the matching `diff_*.py` script, and the `corpus-verifier` agent first, and read the diff
report. See the `corpus-ingest` skill for the full fetch -> parse -> diff -> verify ->
promote procedure, stated once there.

Usage:
  python research/scripts/promote.py [controls] --dry-run     # report what would change
  python research/scripts/promote.py [controls] --apply       # write the file
  python research/scripts/promote.py system-types --dry-run|--apply
  python research/scripts/promote.py level-definitions --dry-run|--apply

What each target does
----------------------
controls — rebuilds `controls.json` from `research/corpus/scraped/controls.json`, keeping
the shipped schema so `docs/assets/js/controls.js` needs no change:

  description  <- upstream `statement`, verbatim
  guidance     <- cybersecurity: `recommendations + " Risk: " + risk`
                  dss:           `rationale`
                  (this is how the upstream website itself composes the field)
  title        <- upstream, verbatim (restores sentence case on 4 DSS controls)
  citations    <- upstream hyperlinks where present, carrying the real href;
                  otherwise the existing prose-derived entry is preserved.
                  A `reference` identical to `standard` is dropped — it rendered
                  as "NIST SP 800-63B (NIST SP 800-63B)".
  sourceUrl    <- new: per-control provenance
  retrievedAt  <- new: provenance timestamp

  Deliberately NOT done here (each wants its own decision):
    - splitting `guidance` into separate statement/recommendations/risk fields
    - rewriting parameter placeholders; upstream renders `[ insert: param, x ]` and
      faithfulness beats prettiness at the data layer. Presentation belongs in controls.js.

system-types — rebuilds `classificationText`, `domainsUsed` and `sourceUrl` in
`system-types.json` from `research/corpus/scraped/system-types.json`:

  classificationText <- dss types:  the SSP landing page's own blurb for that type,
                                     verbatim (verified: matches shipped exactly)
                         other types: `description + " Security Sensitivity Level: " +
                                     sensitivity + "."`, composed from the type page's own
                                     System Characteristics block
  domainsUsed         <- the type page's own domain-count inventory, code order preserved
  sourceUrl            <- new: per-type provenance, matches existing shipped value

  `levelsAvailable`, `totalControls`, `levelCounts` are NOT upstream-scrapeable (no
  "Level N (n)" text exists on any type page) — they stay exactly as shipped, since they're
  correctly derived from `profiles.json` today, not from this scrape.

  `name` is deliberately NOT auto-promoted, even though the scrape now captures the type
  page's own H1 heading correctly (see scrape.py's `heading` vs `templateName` note). One
  of the 8 has a live upstream typo — the low-risk-on-premises page's own heading reads
  "Low-Risk On Premises" (missing the hyphen the other 7 use consistently and that
  `low-risk-cloud`'s own page also uses for its "On-Premises" wording). Promoting `name`
  automatically would silently import that typo. `diff_system_types.py` reports the
  discrepancy for review; this function reports it too but does not act on it.

level-definitions — rebuilds `level-definitions.json` from
`research/corpus/scraped/level-definitions.json`. Content was verified byte-for-byte
identical to what was already shipped (this file predates the scrape pipeline and was
apparently transcribed correctly by hand originally) — this is expected to be a no-op, but
runs through the same mechanism rather than being trusted on the strength of that one
manual check.
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRAPED = {
    "controls": ROOT / "research" / "corpus" / "scraped" / "controls.json",
    "system-types": ROOT / "research" / "corpus" / "scraped" / "system-types.json",
    "level-definitions": ROOT / "research" / "corpus" / "scraped" / "level-definitions.json",
}
SHIPPED = {
    "controls": ROOT / "docs" / "assets" / "data" / "controls.json",
    "system-types": ROOT / "docs" / "assets" / "data" / "system-types.json",
    "level-definitions": ROOT / "docs" / "assets" / "data" / "level-definitions.json",
}

FIELD_ORDER = ["id", "domainId", "catalog", "title", "description", "guidance",
               "parameters", "citations", "sourceUrl", "retrievedAt", "status"]


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def sort_key(cid):
    m = re.match(r"^([A-Za-z]+)-(\d+)$", cid)
    return (m.group(1), int(m.group(2))) if m else (cid, 0)


def compose_guidance(u):
    """Compose the guidance block from the upstream sections.

    Every control has Control Recommendations, plus a third section that differs by
    catalog: Risk Statement (cybersecurity) or Rationale (dss).

    Both are kept. The previous shipped corpus stored only the Rationale for DSS and
    silently dropped the recommendations — losing real content on all 92 DSS controls,
    including BD-2's "Not required for…" exemptions. Do not reintroduce that.
    """
    rec = norm(u.get("recommendations", ""))
    if u.get("catalog") == "dss":
        tail, label = norm(u.get("rationale", "")), "Rationale: "
    else:
        tail, label = norm(u.get("risk", "")), "Risk: "
    if rec and tail:
        return "%s %s%s" % (rec, label, tail)
    return rec or tail


def build_citations(u, shipped):
    """Prefer upstream hyperlinks; fall back to the existing prose-derived entries.

    The 5 controls with shipped citations but no upstream link (AS-11, AS-14, CK-2,
    CK-3, PM-1) were verified to name those standards in upstream prose — they are
    real, just not hyperlinked. Dropping them would lose information.
    """
    links = u.get("links") or []
    if links:
        out, seen = [], set()
        for l in links:
            text, href = norm(l.get("text")), l.get("href")
            if not text or text.lower() in seen:
                continue
            seen.add(text.lower())
            out.append({"standard": text, "url": href})
        if out:
            return out
    cits = shipped.get("citations")
    if not cits:
        return None
    cleaned = []
    for c in cits:
        e = {"standard": c["standard"]}
        if c.get("reference") and norm(c["reference"]) != norm(c["standard"]):
            e["reference"] = c["reference"]
        cleaned.append(e)
    return cleaned


def build_controls():
    up = {c["id"]: c for c in json.loads(SCRAPED["controls"].read_text(encoding="utf-8"))}
    lo = {c["id"]: c for c in json.loads(SHIPPED["controls"].read_text(encoding="utf-8"))}
    if set(up) != set(lo):
        raise SystemExit("REFUSING: scraped and shipped control ids differ. Re-run "
                         "diff_corpus.py and investigate before promoting.")

    out, changes = [], Counter()
    for cid in sorted(up, key=sort_key):
        u, s = up[cid], lo[cid]
        rec = {
            "id": cid,
            "domainId": u["domainId"],
            "catalog": u["catalog"],
            "title": norm(u["title"]),
            "description": norm(u["statement"]),
            "guidance": compose_guidance(u),
            "sourceUrl": u["sourceUrl"],
            "retrievedAt": u["retrievedAt"],
            "status": "scraped",
        }
        if u.get("parameters"):
            rec["parameters"] = u["parameters"]
        cits = build_citations(u, s)
        if cits:
            rec["citations"] = cits

        if rec["title"] != norm(s.get("title")):
            changes["title corrected"] += 1
        if rec["description"] != norm(s.get("description")):
            changes["description corrected"] += 1
        if not s.get("guidance"):
            changes["guidance recovered (was empty)"] += 1
        elif rec["guidance"] != norm(s["guidance"]):
            changes["guidance corrected"] += 1
        if cits and not s.get("citations"):
            changes["citations added"] += 1
        elif cits and s.get("citations") and cits != s["citations"]:
            changes["citations corrected"] += 1

        out.append({k: rec[k] for k in FIELD_ORDER if k in rec})

    # invariants
    assert len(out) == 248, "expected 248 controls, got %d" % len(out)
    missing = [c["id"] for c in out if not c.get("guidance")]
    assert not missing, "controls still without guidance: %s" % missing[:5]
    return out, changes


def compose_classification_text(u):
    """Compose classificationText the way the shipped corpus already does.

    DSS type pages don't carry their own Description/Security Sensitivity Level (the page
    says just "A system that has digital services.", sensitivity "NA") — for those, the
    shipped text instead reproduces the SSP landing page's per-type blurb verbatim. Verified
    by direct comparison against a live fetch: the blurb matches shipped classificationText
    exactly for both DSS types, and description+sensitivity matches for all 6 others.
    """
    if u.get("catalog") == "dss":
        return norm(u.get("landingBlurb"))
    return "%s Security Sensitivity Level: %s." % (norm(u.get("description")), norm(u.get("sensitivity")))


def build_system_types():
    lo_list = json.loads(SHIPPED["system-types"].read_text(encoding="utf-8"))
    up = {t["id"]: t for t in json.loads(SCRAPED["system-types"].read_text(encoding="utf-8"))}
    lo = {t["id"]: t for t in lo_list}
    if set(up) != set(lo):
        raise SystemExit("REFUSING: scraped and shipped system-type ids differ. Investigate "
                         "before promoting.")

    out, changes = [], Counter()
    name_mismatches = []
    for s in lo_list:  # shipped file's own order, not id-sorted or scrape order
        tid = s["id"]
        u = up[tid]
        # Start from the shipped record: preserves levelsAvailable/totalControls/levelCounts
        # (derived from profiles.json, not this scrape) and any editorial `note`.
        rec = dict(s)

        if u["name"] != s.get("name"):
            name_mismatches.append((tid, u["name"], s.get("name")))  # reported, not applied

        new_ct = compose_classification_text(u)
        if new_ct != s.get("classificationText"):
            changes["classificationText corrected"] += 1
            rec["classificationText"] = new_ct

        if u["domainsUsed"] != s.get("domainsUsed"):
            changes["domainsUsed corrected"] += 1
            rec["domainsUsed"] = u["domainsUsed"]

        if u["sourceUrl"] != s.get("sourceUrl"):
            changes["sourceUrl corrected"] += 1
            rec["sourceUrl"] = u["sourceUrl"]

        out.append(rec)

    assert len(out) == 8, "expected 8 system types, got %d" % len(out)
    if name_mismatches:
        changes["name DIFFERS (not auto-promoted, see docstring)"] = len(name_mismatches)
    return out, changes, name_mismatches


def build_level_definitions():
    up = json.loads(SCRAPED["level-definitions"].read_text(encoding="utf-8"))
    lo = json.loads(SHIPPED["level-definitions"].read_text(encoding="utf-8"))

    rec = dict(lo)  # preserve the editorial `note` field; nothing upstream supplies it
    changes = Counter()
    for field in ("0", "1", "2", "selectionGuidance"):
        if norm(up.get(field)) != norm(lo.get(field)):
            changes["%s corrected" % field] += 1
            rec[field] = up[field]
    if up.get("sourceUrl") != lo.get("sourceUrl"):
        changes["sourceUrl corrected"] += 1
        rec["sourceUrl"] = up["sourceUrl"]

    return [rec], changes  # wrapped in a list only so main()'s reporting stays uniform


BUILDERS = {
    "controls": build_controls,
    "system-types": build_system_types,
    "level-definitions": build_level_definitions,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default="controls", choices=list(BUILDERS))
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    result = BUILDERS[a.target]()
    out, changes = result[0], result[1]
    name_mismatches = result[2] if len(result) > 2 else []

    print("%s: %d record(s)" % (a.target, len(out)))
    for k, v in sorted(changes.items(), key=lambda x: -x[1]):
        print("  %-42s %3d" % (k, v))
    for tid, upstream_name, shipped_name in name_mismatches:
        print("  NOT promoted — %s: upstream %r vs shipped %r" % (tid, upstream_name, shipped_name))

    shipped_path = SHIPPED[a.target]
    if a.apply:
        payload = out[0] if a.target == "level-definitions" else out
        shipped_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
        print("\nwrote %s" % shipped_path)
    else:
        print("\ndry run — nothing written. Re-run with --apply to promote.")


if __name__ == "__main__":
    main()
