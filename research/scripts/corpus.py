#!/usr/bin/env python
"""Query the SSP corpus without loading it into an agent's context.

The JSON under docs/assets/data/ is ~218 KB; reading it directly burns context for
no reason. Every subcommand here prints a compact table instead.

Usage:
  python research/scripts/corpus.py stats
  python research/scripts/corpus.py types
  python research/scripts/corpus.py domains [--catalog cybersecurity|dss]
  python research/scripts/corpus.py profile <type-id> [--level N] [--domain XX]
  python research/scripts/corpus.py diff <type-a> <type-b>
  python research/scripts/corpus.py domain <DOMAIN-ID>
  python research/scripts/corpus.py control <CONTROL-ID> [...]
  python research/scripts/corpus.py grep <term> [--field all|title|description|guidance]
  python research/scripts/corpus.py gaps

Stdlib only, by design. Read-only: this script never writes to docs/.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "docs" / "assets" / "data"


def load(name):
    with open(DATA / (name + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def corpus():
    return {
        "controls": load("controls"),
        "domains": load("domains"),
        "system_types": load("system-types"),
        "profiles": load("profiles"),
        "levels": load("level-definitions"),
    }


def by_id(records):
    return {r["id"]: r for r in records}


def sort_key(cid):
    """Sort AC-2 before AC-11, matching controls.js localeCompare({numeric:true})."""
    m = re.match(r"^([A-Za-z]+)-(\d+)$", cid)
    return (m.group(1), int(m.group(2))) if m else (cid, 0)


def rule(width=78):
    print("-" * width)


# --------------------------------------------------------------------------- stats
def cmd_stats(c, args):
    controls = c["controls"]
    domains = c["domains"]
    types = c["system_types"]
    profiles = c["profiles"]

    print("controls      %d" % len(controls))
    print("domains       %d" % len(domains))
    print("system types  %d" % len(types))
    print()
    print("catalog split:", dict(Counter(x["catalog"] for x in controls)))
    print("field coverage:",
          dict(sorted(Counter(k for x in controls for k in x).items())))
    missing = [x["id"] for x in controls if not x.get("guidance")]
    print("controls without guidance: %d" % len(missing))
    orphans = sorted({x["domainId"] for x in controls} - {d["id"] for d in domains})
    if orphans:
        print("!! controls referencing unknown domains: %s" % orphans)
    print()

    header = "%-30s %6s %5s %5s %5s  levelsAvailable"
    print(header % ("system type", "total", "L0", "L1", "L2"))
    rule()
    tmap = by_id(types)
    for tid, entries in profiles.items():
        lv = Counter(e["level"] for e in entries)
        avail = tmap.get(tid, {}).get("levelsAvailable", [])
        print("%-30s %6d %5d %5d %5d  %s"
              % (tid, len(entries), lv[0], lv[1], lv[2], avail))
    rule()

    # integrity: does every profile entry point at a real control?
    cmap = by_id(controls)
    for tid, entries in profiles.items():
        bad = [e["controlId"] for e in entries if e["controlId"] not in cmap]
        if bad:
            print("!! %s: %d profile entries reference unknown controls: %s"
                  % (tid, len(bad), bad[:5]))
    # integrity: does every profile stay inside its declared domains?
    for tid, entries in profiles.items():
        declared = set(tmap.get(tid, {}).get("domainsUsed", []))
        used = {cmap[e["controlId"]]["domainId"]
                for e in entries if e["controlId"] in cmap}
        stray = sorted(used - declared)
        if stray:
            print("!! %s: profile uses domains not in domainsUsed: %s" % (tid, stray))


# --------------------------------------------------------------------------- types
def cmd_types(c, args):
    profiles = c["profiles"]
    for t in c["system_types"]:
        n = len(profiles.get(t["id"], []))
        print("%-30s %-32s %4d controls  levels=%s"
              % (t["id"], t["name"], n, t["levelsAvailable"]))
        print("%-30s domains: %s" % ("", ",".join(t["domainsUsed"])))
        print("%-30s %s" % ("", t["classificationText"]))
        print()


# ------------------------------------------------------------------------- domains
def cmd_domains(c, args):
    print("%-4s %-14s %4s  name" % ("id", "catalog", "n"))
    rule()
    for d in c["domains"]:
        if args.catalog and d["catalog"] != args.catalog:
            continue
        print("%-4s %-14s %4d  %s"
              % (d["id"], d["catalog"], d["controlCount"], d["name"]))


# ------------------------------------------------------------------------- profile
def cmd_profile(c, args):
    entries = c["profiles"].get(args.type_id)
    if entries is None:
        sys.exit("unknown system type %r; try: corpus.py types" % args.type_id)
    cmap = by_id(c["controls"])
    rows = []
    for e in entries:
        ctl = cmap.get(e["controlId"])
        if not ctl:
            continue
        if args.level is not None and e["level"] != args.level:
            continue
        if args.domain and ctl["domainId"] != args.domain.upper():
            continue
        rows.append((e["controlId"], e["level"], ctl["domainId"], ctl["title"]))
    rows.sort(key=lambda r: sort_key(r[0]))

    print("%s: %d control(s)" % (args.type_id, len(rows)))
    rule()
    print("%-9s %3s %-4s title" % ("id", "lvl", "dom"))
    for cid, lvl, dom, title in rows:
        print("%-9s %3d %-4s %s" % (cid, lvl, dom, title[:56]))
    rule()
    print("by domain:", dict(sorted(Counter(r[2] for r in rows).items())))
    print("by level: ", dict(sorted(Counter(r[1] for r in rows).items())))


# ---------------------------------------------------------------------------- diff
def cmd_diff(c, args):
    a = args.type_a
    b = args.type_b
    profiles = c["profiles"]
    for t in (a, b):
        if t not in profiles:
            sys.exit("unknown system type %r; try: corpus.py types" % t)
    la = {e["controlId"]: e["level"] for e in profiles[a]}
    lb = {e["controlId"]: e["level"] for e in profiles[b]}
    cmap = by_id(c["controls"])

    only_a = sorted(set(la) - set(lb), key=sort_key)
    only_b = sorted(set(lb) - set(la), key=sort_key)
    moved = sorted([k for k in set(la) & set(lb) if la[k] != lb[k]], key=sort_key)

    print("%s (%d) vs %s (%d)" % (a, len(la), b, len(lb)))
    print("shared %d | only in %s: %d | only in %s: %d | level changed: %d"
          % (len(set(la) & set(lb)), a, len(only_a), b, len(only_b), len(moved)))
    rule()

    def show(label, ids, levels):
        if not ids:
            return
        print()
        print(label)
        for cid in ids:
            title = cmap.get(cid, {}).get("title", "?")
            print("  %-9s L%d  %s" % (cid, levels[cid], title[:58]))

    show("only in %s:" % a, only_a, la)
    show("only in %s:" % b, only_b, lb)
    if moved:
        print()
        print("level changed (%s -> %s):" % (a, b))
        for cid in moved:
            title = cmap.get(cid, {}).get("title", "?")
            print("  %-9s L%d -> L%d  %s" % (cid, la[cid], lb[cid], title[:52]))
    print()
    print("level distribution:")
    print("  %-30s %s" % (a, dict(sorted(Counter(la.values()).items()))))
    print("  %-30s %s" % (b, dict(sorted(Counter(lb.values()).items()))))


# -------------------------------------------------------------------------- domain
def cmd_domain(c, args):
    did = args.domain_id.upper()
    dmap = by_id(c["domains"])
    if did not in dmap:
        sys.exit("unknown domain %r; try: corpus.py domains" % did)
    d = dmap[did]
    print("%s - %s  (%s, %d controls)"
          % (d["id"], d["name"], d["catalog"], d["controlCount"]))
    print(d["description"])
    print("source: %s" % d["sourceUrl"])
    rule()

    inprofile = defaultdict(list)
    for tid, entries in c["profiles"].items():
        for e in entries:
            inprofile[e["controlId"]].append((tid, e["level"]))

    for ctl in sorted((x for x in c["controls"] if x["domainId"] == did),
                      key=lambda x: sort_key(x["id"])):
        used = inprofile.get(ctl["id"], [])
        tags = ",".join("%s:L%d" % (t, l) for t, l in used) or "(in no profile)"
        flag = "" if ctl.get("guidance") else "  [no guidance]"
        print("%-9s %-52s%s" % (ctl["id"], ctl["title"][:52], flag))
        print("%-9s %s" % ("", tags))


# ------------------------------------------------------------------------- control
def cmd_control(c, args):
    cmap = by_id(c["controls"])
    inprofile = defaultdict(list)
    for tid, entries in c["profiles"].items():
        for e in entries:
            inprofile[e["controlId"]].append((tid, e["level"]))

    for cid in args.control_ids:
        ctl = cmap.get(cid.upper())
        if not ctl:
            print("%s: not found" % cid)
            continue
        print("%s - %s  [%s / %s]"
              % (ctl["id"], ctl["title"], ctl["domainId"], ctl["catalog"]))
        print("  desc:     %s" % ctl["description"])
        print("  guidance: %s" % (ctl.get("guidance") or "(none)"))
        for p in ctl.get("parameters", []):
            print("  param:    %s (%s) - %s" % (p["id"], p["type"], p["description"]))
        for cit in ctl.get("citations", []):
            print("  cite:     %s: %s" % (cit["standard"], cit["reference"]))
        used = inprofile.get(ctl["id"], [])
        joined = ", ".join("%s:L%d" % (t, l) for t, l in used) or "(none)"
        print("  profiles: %s" % joined)
        print()


# ---------------------------------------------------------------------------- grep
def cmd_grep(c, args):
    term = args.term.lower()
    fields = (["title", "description", "guidance"]
              if args.field == "all" else [args.field])
    hits = []
    for ctl in c["controls"]:
        for f in fields:
            if term in (ctl.get(f) or "").lower():
                hits.append((ctl, f))
                break
    hits.sort(key=lambda h: sort_key(h[0]["id"]))
    print("%d control(s) matching %r in %s" % (len(hits), args.term, args.field))
    rule()
    for ctl, f in hits:
        print("%-9s %-4s [%-11s] %s"
              % (ctl["id"], ctl["domainId"], f, ctl["title"][:50]))
    if hits:
        print()
        print("by domain:",
              dict(sorted(Counter(h[0]["domainId"] for h in hits).items())))


# ---------------------------------------------------------------------------- gaps
def cmd_gaps(c, args):
    """Everything that looks like a corpus defect. Feeds findings with implications: [data]."""
    controls = c["controls"]
    profiles = c["profiles"]
    types = c["system_types"]
    cmap = by_id(controls)

    print("== controls with no guidance ==")
    missing = [x for x in controls if not x.get("guidance")]
    print("%d of %d" % (len(missing), len(controls)))
    print("by domain:", dict(sorted(Counter(x["domainId"] for x in missing).items())))
    print()

    print("== controls in no profile (catalog-only) ==")
    used = {e["controlId"] for entries in profiles.values() for e in entries}
    unused = sorted(set(cmap) - used, key=sort_key)
    print("%d" % len(unused))
    print("by domain:",
          dict(sorted(Counter(cmap[i]["domainId"] for i in unused).items())))
    print()

    print("== declared domainsUsed with zero controls in the profile ==")
    for t in types:
        entries = profiles.get(t["id"], [])
        used_d = {cmap[e["controlId"]]["domainId"]
                  for e in entries if e["controlId"] in cmap}
        empty = sorted(set(t["domainsUsed"]) - used_d)
        if empty:
            print("%-30s declares but never uses: %s" % (t["id"], empty))
    print()

    print("== identical classificationText sensitivity wording ==")
    seen = defaultdict(list)
    for t in types:
        tail = t["classificationText"].split("Security Sensitivity Level:")[-1].strip()
        seen[tail].append(t["id"])
    for tail, ids in seen.items():
        if len(ids) > 1:
            print("%s share: %r" % (ids, tail))
    print()

    print("== level-definitions.json ==")
    print("fetched by no JS file "
          "(controls.js loads controls/domains/system-types/profiles only)")
    print("UI labels in controls.js: {0:'Mandatory', 1:'Baseline', 2:'Optional'}")
    for k in ("0", "1", "2"):
        print("  L%s: %s" % (k, c["levels"][k]))
    print("  selectionGuidance: %s" % c["levels"]["selectionGuidance"])


def main():
    p = argparse.ArgumentParser(
        prog="corpus.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("stats", help="counts, coverage, and integrity checks")
    sub.add_parser("types", help="the 8 system types with classification text")

    sp = sub.add_parser("domains", help="all 26 domains")
    sp.add_argument("--catalog", choices=["cybersecurity", "dss"])

    sp = sub.add_parser("profile", help="controls applying to one system type")
    sp.add_argument("type_id")
    sp.add_argument("--level", type=int, choices=[0, 1, 2])
    sp.add_argument("--domain")

    sp = sub.add_parser("diff", help="compare two system-type profiles")
    sp.add_argument("type_a")
    sp.add_argument("type_b")

    sp = sub.add_parser("domain", help="one domain and its controls")
    sp.add_argument("domain_id")

    sp = sub.add_parser("control", help="full detail for one or more controls")
    sp.add_argument("control_ids", nargs="+")

    sp = sub.add_parser("grep", help="substring search across control text")
    sp.add_argument("term")
    sp.add_argument("--field", default="all",
                    choices=["all", "title", "description", "guidance"])

    sub.add_parser("gaps", help="corpus defects worth filing as findings")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)
    c = corpus()
    {"stats": cmd_stats, "types": cmd_types, "domains": cmd_domains,
     "profile": cmd_profile, "diff": cmd_diff, "domain": cmd_domain,
     "control": cmd_control, "grep": cmd_grep, "gaps": cmd_gaps}[args.cmd](c, args)


if __name__ == "__main__":
    main()
