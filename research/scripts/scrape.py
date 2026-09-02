#!/usr/bin/env python
"""Scrape the SSP control catalog and system-type pages from the authoritative source.

Authoritative source: https://info.standards.tech.gov.sg/

Emits a SUPERSET record per control — every field visible on the page, including fields
the shipped corpus does not currently carry. The point is to discover omissions, so this
deliberately does not pre-filter to docs/assets/data/'s schema.

Usage:
  python research/scripts/scrape.py controls [--domain LM] [--no-cache]
  python research/scripts/scrape.py domains [--domain LM] [--no-cache]
  python research/scripts/scrape.py types
  python research/scripts/scrape.py level-definitions
  python research/scripts/scrape.py all
  python research/scripts/scrape.py selftest

Output:  research/corpus/scraped/{controls,domains,system-types,level-definitions}.json
Cache:   research/corpus/raw/*.html   (gitignored; delete or pass --no-cache to refetch)

Design notes
------------
The upstream site is Next.js App Router: no __NEXT_DATA__ blob, Tailwind utility classes,
and anchors that are content hashes. So this parser keys ONLY on document structure and
text landmarks ("Control Statement", "Risk Statement", ...), never on CSS classes or ids,
which would break on the next redeploy.

Inline vs block matters: citations upstream are plain <a> links embedded in the
recommendations prose. Splitting on every tag shreds that prose into fragments, so inline
elements are unwrapped into the surrounding text while their hrefs are collected
separately.

FAILS LOUDLY. A page that yields zero controls raises rather than returning empty — a
silent empty parse is exactly how the original IS/LM/PM/ST guidance gap went unnoticed.

Stdlib only.
"""

import argparse
import json
import re
import sys
import time
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research" / "corpus" / "raw"
OUT = ROOT / "research" / "corpus" / "scraped"
BASE = "https://info.standards.tech.gov.sg"

# Domain codes and their catalog, from docs/assets/data/domains.json.
CYBER = ["ac", "as", "br", "ck", "cs", "dc", "dp", "ga", "hr", "is",
         "lm", "ns", "pm", "rs", "sc", "sd", "st"]
DSS = ["bd", "pr", "tl", "tx", "uu", "wo", "wp", "wr", "wu"]

SYSTEM_TYPES = [
    ("low-risk-cloud", "low-risk-cloud", "cybersecurity"),
    ("low-risk-on-premises", "low-risk-on-premises", "cybersecurity"),
    ("medium-risk-cloud", "medium-risk-cloud", "cybersecurity"),
    ("high-risk-cloud", "high-risk-cloud", "cybersecurity"),
    ("generative-ai", "gen-ai", "cybersecurity"),
    ("sandbox", "sandbox", "cybersecurity"),
    ("digital-services-others", "dss-others", "dss"),
    ("digital-services-high-impact", "dss-high", "dss"),
]

NAME_RE = re.compile(r"^Name:\s*(.+)$")
DESC_RE = re.compile(r"^Description:\s*(.+)$")
SENSITIVITY_RE = re.compile(r"^Security Sensitivity Level:\s*(.+)$")
DOMAIN_COUNT_RE = re.compile(r"^([A-Z]{2}): .+\(\d+\)$")

INLINE = {"a", "b", "strong", "i", "em", "span", "code", "sup", "sub",
          "u", "small", "abbr", "mark", "cite", "q", "time", "label"}
SKIP = {"script", "style", "svg", "path", "noscript", "head", "meta", "link"}

# Text landmarks that delimit a control's fields on the catalog pages.
#
# The two catalogs are NOT laid out the same way:
#   cybersecurity — Group: / <name> as two blocks, and a "Risk Statement" section
#   dss           — "Group: <name>" as one block, and a "Rationale" section instead
# Missing this is why an early parse folded DSS rationale text into recommendations.
FIELD_LANDMARKS = {
    "Control Statement": "statement",
    "Control Recommendations": "recommendations",
    "Risk Statement": "risk",
    "Rationale": "rationale",
}
LANDMARKS = ["Group:", "Parameters"] + list(FIELD_LANDMARKS)

CONTROL_RE = re.compile(r"^([A-Z]{2})-(\d+):\s*(.+)$")


class BlockExtractor(HTMLParser):
    """Flatten HTML into a list of block-level text runs, keeping inline text joined.

    Each block is {"text": str, "links": [{"text":..., "href":...}]}.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self._buf = []
        self._links = []
        self._skip_depth = 0
        self._a_href = None
        self._a_text = []

    def _flush(self):
        text = "".join(self._buf)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            self.blocks.append({"text": text, "links": self._links})
        self._buf = []
        self._links = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "br":
            self._flush()
            return
        if tag == "a":
            self._a_href = dict(attrs).get("href")
            self._a_text = []
            return
        if tag not in INLINE:
            self._flush()

    def handle_endtag(self, tag):
        if tag in SKIP:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return
        if tag == "a":
            txt = re.sub(r"\s+", " ", "".join(self._a_text)).strip()
            if txt and self._a_href:
                self._links.append({"text": txt, "href": self._a_href})
            self._a_href = None
            self._a_text = []
            return
        if tag not in INLINE:
            self._flush()

    def handle_data(self, data):
        if self._skip_depth:
            return
        self._buf.append(data)
        if self._a_href is not None:
            self._a_text.append(data)


def fetch(url, use_cache=True):
    RAW.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", url.replace(BASE, "").lower()).strip("-") or "index"
    cached = RAW / (slug + ".html")
    if use_cache and cached.exists():
        return cached.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers={"User-Agent": "LTA-SSP-research/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        if r.status != 200:
            raise RuntimeError("HTTP %s for %s" % (r.status, url))
        body = r.read().decode("utf-8", "replace")
    cached.write_text(body, encoding="utf-8")
    time.sleep(0.4)  # be polite
    return body


def blocks_of(url, use_cache=True):
    p = BlockExtractor()
    p.feed(fetch(url, use_cache))
    p._flush()
    return p.blocks


def parse_parameters(blocks, i):
    """Parse a Parameters table starting at blocks[i] == 'Parameters'.

    Layout: 'Parameters', '<ID> Parameters', 'ID', 'Type', 'Description', then
    repeating (id, type, description) triples until the next landmark or control.
    """
    params = []
    j = i + 1
    # skip the caption and the three column headers
    while j < len(blocks) and blocks[j]["text"] not in ("ID",):
        if CONTROL_RE.match(blocks[j]["text"]) or blocks[j]["text"] in LANDMARKS:
            return params, j
        j += 1
    j += 1  # past 'ID'
    for expected in ("Type", "Description"):
        if j < len(blocks) and blocks[j]["text"] == expected:
            j += 1
    while j + 2 < len(blocks):
        pid = blocks[j]["text"]
        if CONTROL_RE.match(pid) or pid in LANDMARKS or not re.match(r"^[a-z]{2}-\d+_prm_\d+$", pid):
            break
        params.append({"id": pid,
                       "type": blocks[j + 1]["text"],
                       "description": blocks[j + 2]["text"]})
        j += 3
    return params, j


def scrape_domain(code, catalog, use_cache=True):
    url = "%s/control-catalog/%s/%s/" % (BASE, catalog, code)
    blocks = blocks_of(url, use_cache)
    controls = []
    cur = None
    field = None
    i = 0
    while i < len(blocks):
        text = blocks[i]["text"]
        m = CONTROL_RE.match(text)
        if m and m.group(1).upper() == code.upper():
            if cur:
                controls.append(cur)
            cur = {"id": "%s-%s" % (m.group(1), m.group(2)),
                   "domainId": m.group(1),
                   "catalog": catalog,
                   "title": m.group(3).strip(),
                   "sourceUrl": url,
                   "retrievedAt": date.today().isoformat()}
            field = None
            i += 1
            continue
        if cur is not None:
            # cybersecurity renders "Group:" and the name as two blocks; dss renders
            # "Group: <name>" as one.
            if text == "Group:":
                if i + 1 < len(blocks):
                    cur["group"] = blocks[i + 1]["text"]
                i += 2
                field = None
                continue
            if text.startswith("Group: "):
                cur["group"] = text[len("Group: "):].strip()
                i += 1
                field = None
                continue
            if text == "Parameters":
                params, i = parse_parameters(blocks, i)
                if params:
                    cur["parameters"] = params
                field = None
                continue
            if text in FIELD_LANDMARKS:
                field = FIELD_LANDMARKS[text]
                i += 1
                continue
            if field:
                cur.setdefault(field, [])
                cur[field].append(text)
                if blocks[i]["links"]:
                    cur.setdefault("links", []).extend(blocks[i]["links"])
        i += 1
    if cur:
        controls.append(cur)

    for c in controls:
        for f in ("statement", "recommendations", "risk", "rationale"):
            if f in c:
                c[f] = " ".join(c[f]).strip()

    # Each page carries a table of contents listing every control id as a link before
    # the body renders them again. Those TOC entries parse as field-less duplicates.
    # Keep, per id, the record carrying the most content.
    def richness(c):
        return sum(len(c.get(f, "")) for f in ("statement", "recommendations", "risk", "rationale"))

    best = {}
    for c in controls:
        if c["id"] not in best or richness(c) > richness(best[c["id"]]):
            best[c["id"]] = c
    controls = [best[k] for k in sorted(best, key=lambda x: (x.split("-")[0], int(x.split("-")[1])))]

    empty = [c["id"] for c in controls if not c.get("statement")]
    if empty:
        raise RuntimeError(
            "PARSE FAILURE: %d control(s) on %s have no Control Statement (%s). Refusing to "
            "emit a partial result — silent field loss is exactly what produced the original "
            "IS/LM/PM/ST guidance gap." % (len(empty), url, ", ".join(empty[:6])))

    if not controls:
        raise RuntimeError(
            "PARSE FAILURE: zero controls extracted from %s. Refusing to emit an empty "
            "result — this is the failure mode that produced the original IS/LM/PM/ST "
            "guidance gap. Check whether the page structure changed." % url)
    return controls


def scrape_domain_meta(code, catalog, blocks):
    """Parse a domain's name/description off its own control-catalog landing page.

    Layout (confirmed against cached HTML for both a cybersecurity and a dss page):
    'Home', 'Control Catalog', <catalog display name>, <domain name (breadcrumb)>,
    <domain name (H1, duplicate)>, <description>, 'Last updated <date>', 'On this page', ...
    Same double-listing pattern as 'Group:' on control pages and the heading on system-type
    pages — the breadcrumb repeats immediately before the H1 renders it again.
    """
    texts = [b["text"] for b in blocks]
    url = "%s/control-catalog/%s/%s/" % (BASE, catalog, code)
    try:
        home_i = texts.index("Home")
    except ValueError:
        raise RuntimeError("PARSE FAILURE: 'Home' nav landmark not found on %s" % url)
    if home_i + 6 >= len(texts):
        raise RuntimeError("PARSE FAILURE: domain page for %s too short after 'Home'" % url)
    name, name2, description, updated = texts[home_i + 3:home_i + 7]
    if name != name2:
        raise RuntimeError(
            "PARSE FAILURE: breadcrumb/H1 domain name mismatch on %s (%r vs %r)" %
            (url, name, name2))
    if not name or not description:
        raise RuntimeError(
            "PARSE FAILURE: incomplete domain heading block on %s (name=%r description=%r)" %
            (url, name, description))
    last_updated = updated[len("Last updated "):] if updated.startswith("Last updated ") else None
    return name, description, last_updated


def scrape_domains(use_cache=True, domain=None):
    todo = [(d, "cybersecurity") for d in CYBER] + [(d, "dss") for d in DSS]
    if domain:
        want = domain.lower()
        todo = [t for t in todo if t[0] == want]
        if not todo:
            sys.exit("unknown domain %r" % domain)
    recs = []
    for code, catalog in todo:
        url = "%s/control-catalog/%s/%s/" % (BASE, catalog, code)
        blocks = blocks_of(url, use_cache)
        name, description, last_updated = scrape_domain_meta(code, catalog, blocks)
        controls = scrape_domain(code, catalog, use_cache)
        recs.append({
            "id": code.upper(),
            "name": name,
            "catalog": catalog,
            "description": description,
            "sourceUrl": url,
            "controlCount": len(controls),
            "lastUpdated": last_updated,
            "retrievedAt": date.today().isoformat(),
        })
    return recs


def normalize_heading(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def blurb_landmark_texts(landing_blocks):
    """Map each type's normalized display heading to its landing-page description paragraph.

    The page lists each type as a (name-heading, blurb) pair after "The various types are
    listed below:", but NOT in SYSTEM_TYPES' order — Sandbox is listed last upstream, not
    6th (found by running this: naive positional zip() silently paired Sandbox's slot with
    the Digital Services (Others) blurb and vice versa). Match by normalized heading text
    instead of position; normalized because upstream's heading text has its own small
    inconsistencies (e.g. "Low-Risk On Premises" vs. our "Low-Risk On-Premises").
    """
    texts = [b["text"] for b in landing_blocks]
    try:
        i = texts.index("The various types are listed below:") + 1
    except ValueError:
        raise RuntimeError(
            "PARSE FAILURE: 'The various types are listed below:' landmark not found on the "
            "SSP landing page. Check whether the page structure changed.")
    blurbs = {}
    while i + 1 < len(texts) and len(blurbs) < len(SYSTEM_TYPES):
        heading, blurb = texts[i], texts[i + 1]
        blurbs[normalize_heading(heading)] = blurb
        i += 2
    if len(blurbs) != len(SYSTEM_TYPES):
        raise RuntimeError(
            "PARSE FAILURE: expected %d type blurbs on the SSP landing page, got %d." %
            (len(SYSTEM_TYPES), len(blurbs)))
    return blurbs


def scrape_system_type(type_id, slug, catalog, landing_blurbs, use_cache=True):
    """Scrape one system-type page.

    Structural note (found by running this against the live pages): "System
    Characteristics" appears twice — once as a nav placeholder immediately followed by the
    domain-count inventory, once again immediately before the Name:/Description:/Security
    Sensitivity Level: block. This mirrors the "Group:" TOC-then-body double-listing
    scrape_domain() already works around. Parsing stops at the first "Group: <name>"
    landmark (rendered as one merged block on these pages, unlike the two-block split on
    cybersecurity control-catalog pages), which is where the page starts repeating
    per-control content controls.json already owns.
    """
    url = "%s/ssp/%s/" % (BASE, slug)
    blocks = blocks_of(url, use_cache)
    texts = [b["text"] for b in blocks]

    try:
        home_i = texts.index("Home")
    except ValueError:
        raise RuntimeError("PARSE FAILURE: 'Home' nav landmark not found on %s" % url)
    if home_i + 2 >= len(texts):
        raise RuntimeError("PARSE FAILURE: no heading block after 'Home' on %s" % url)
    heading = texts[home_i + 2]
    landing_blurb = landing_blurbs.get(normalize_heading(heading))
    if landing_blurb is None:
        raise RuntimeError(
            "PARSE FAILURE: no landing-page blurb matched heading %r for %s" % (heading, url))

    stop = next((i for i, t in enumerate(texts) if t.startswith("Group:")), None)
    if stop is None:
        raise RuntimeError(
            "PARSE FAILURE: no 'Group:' landmark found on %s — page structure may have "
            "changed." % url)
    try:
        sc1 = texts.index("System Characteristics")
    except ValueError:
        raise RuntimeError("PARSE FAILURE: 'System Characteristics' not found on %s" % url)

    domains = []
    i = sc1 + 1
    while i < stop and DOMAIN_COUNT_RE.match(texts[i]):
        domains.append(texts[i].split(":", 1)[0])
        i += 1

    # "Name:" here is a filled-in template EXAMPLE for what a real SSP document would call
    # its system ("Low-Risk Cloud System"), not the type's own display name — that's the H1
    # heading captured above as `heading` ("Low-Risk Cloud"), which is what shipped `name`
    # actually matches. Both are kept: `heading` as the authoritative name, `templateName`
    # as the example, for the record.
    template_name = description = sensitivity = None
    for t in texts[i:stop]:
        m = NAME_RE.match(t)
        if m:
            template_name = m.group(1)
        m = DESC_RE.match(t)
        if m:
            description = m.group(1)
        m = SENSITIVITY_RE.match(t)
        if m:
            sensitivity = m.group(1)
    if not domains or not template_name or not description or not sensitivity:
        raise RuntimeError(
            "PARSE FAILURE: incomplete System Characteristics block on %s "
            "(domains=%d templateName=%r description=%r sensitivity=%r). Refusing to emit a "
            "partial result." % (url, len(domains), template_name, description, sensitivity))

    last_updated = next(
        (t[len("Last updated "):] for t in texts[:sc1] if t.startswith("Last updated ")), None)

    return {
        "id": type_id,
        "slug": slug,
        "catalog": catalog,
        "name": heading,
        "templateName": template_name,
        "description": description,
        "sensitivity": sensitivity,
        "domainsUsed": domains,
        "landingBlurb": landing_blurb,
        "lastUpdated": last_updated,
        "sourceUrl": url,
        "retrievedAt": date.today().isoformat(),
        "blocks": texts[sc1:stop],
    }


def scrape_level_definitions(use_cache=True):
    """Scrape the Level 0/1/2 definitions and selection-guidance sentence from /ssp/.

    This page has no repeating per-record structure to key on the way controls or system
    types do — just one "Control Levels" heading followed by a fixed run of Level N /
    description pairs. Confirmed by running blocks_of() against the live page: the
    structure is thin but stable, so this keys on that heading plus each "Level N" label
    rather than hardcoding block indices.
    """
    url = BASE + "/ssp/"
    blocks = blocks_of(url, use_cache)
    texts = [b["text"] for b in blocks]

    try:
        ci = texts.index("Control Levels")
    except ValueError:
        raise RuntimeError(
            "PARSE FAILURE: 'Control Levels' heading not found on %s — page structure may "
            "have changed." % url)

    rec = {"sourceUrl": url, "retrievedAt": date.today().isoformat()}
    for lvl in ("0", "1", "2"):
        label = "Level %s" % lvl
        try:
            i = texts.index(label, ci)
        except ValueError:
            raise RuntimeError(
                "PARSE FAILURE: %r not found after 'Control Levels' on %s" % (label, url))
        if i + 1 >= len(texts):
            raise RuntimeError(
                "PARSE FAILURE: no description block after %r on %s" % (label, url))
        rec[lvl] = texts[i + 1]

    guidance = next((t for t in texts if "assess the risks and threats" in t), None)
    if not guidance:
        raise RuntimeError(
            "PARSE FAILURE: selection-guidance sentence not found on %s" % url)
    rec["selectionGuidance"] = guidance
    return rec


def cmd_controls(args):
    OUT.mkdir(parents=True, exist_ok=True)
    todo = ([(d, "cybersecurity") for d in CYBER] + [(d, "dss") for d in DSS])
    if args.domain:
        want = args.domain.lower()
        todo = [t for t in todo if t[0] == want]
        if not todo:
            sys.exit("unknown domain %r" % args.domain)
    allc = []
    for code, catalog in todo:
        cs = scrape_domain(code, catalog, not args.no_cache)
        print("%-4s %-14s %3d controls" % (code.upper(), catalog, len(cs)))
        allc.extend(cs)
    path = OUT / "controls.json"
    if not args.domain:
        path.write_text(json.dumps(allc, indent=2, ensure_ascii=False), encoding="utf-8")
        print("\n%d controls -> %s" % (len(allc), path))
    else:
        print(json.dumps(allc, indent=2, ensure_ascii=False)[:2000])
    return allc


def cmd_domains(args):
    OUT.mkdir(parents=True, exist_ok=True)
    recs = scrape_domains(not args.no_cache, args.domain)
    for r in recs:
        print("%-4s %-14s %3d controls" % (r["id"], r["catalog"], r["controlCount"]))
    path = OUT / "domains.json"
    if not args.domain:
        path.write_text(json.dumps(recs, indent=2, ensure_ascii=False), encoding="utf-8")
        print("\n%d domains -> %s" % (len(recs), path))
    else:
        print(json.dumps(recs, indent=2, ensure_ascii=False)[:2000])
    return recs


def cmd_types(args):
    OUT.mkdir(parents=True, exist_ok=True)
    landing = blocks_of(BASE + "/ssp/", not args.no_cache)
    blurb_map = blurb_landmark_texts(landing)
    recs = [scrape_system_type(t, s, cat, blurb_map, not args.no_cache)
            for t, s, cat in SYSTEM_TYPES]
    path = OUT / "system-types.json"
    path.write_text(json.dumps(recs, indent=2, ensure_ascii=False), encoding="utf-8")
    print("%d system types -> %s" % (len(recs), path))
    return recs


def cmd_level_definitions(args):
    OUT.mkdir(parents=True, exist_ok=True)
    rec = scrape_level_definitions(not args.no_cache)
    path = OUT / "level-definitions.json"
    path.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    print("level definitions -> %s" % path)
    return rec


def cmd_all(args):
    cmd_controls(args)
    cmd_domains(args)
    cmd_types(args)
    cmd_level_definitions(args)


def cmd_selftest(args):
    """Verify the parser fails loudly rather than emitting empty results."""
    print("1. A page with no controls must raise, not return []")
    try:
        scrape_domain("zz", "cybersecurity", use_cache=False)
        print("   FAIL — returned without raising")
        return 1
    except RuntimeError as e:
        if "PARSE FAILURE" in str(e):
            print("   ok — RuntimeError(PARSE FAILURE)")
        else:
            print("   ok — raised: %s" % str(e)[:80])
    except Exception as e:
        print("   ok — raised %s" % type(e).__name__)

    print("2. Known control text must round-trip (LM-1)")
    cs = scrape_domain("lm", "cybersecurity", use_cache=not args.no_cache)
    lm1 = next((c for c in cs if c["id"] == "LM-1"), None)
    if not lm1:
        print("   FAIL — LM-1 not found")
        return 1
    ok = ("different system or system component" in lm1.get("statement", "")
          and "Do not store logs only in the same system component"
          in lm1.get("recommendations", ""))
    print("   %s — LM-1 statement + recommendations present (%d controls in LM)"
          % ("ok" if ok else "FAIL", len(cs)))

    print("3. Inline links must not shred prose (AS-5 recommendations stay one run)")
    a = scrape_domain("as", "cybersecurity", use_cache=not args.no_cache)
    as5 = next((c for c in a if c["id"] == "AS-5"), None)
    rec = (as5 or {}).get("recommendations", "")
    # The link text must remain embedded in the surrounding sentence, not split out.
    ok3 = ("Latest NIST SP 800-63B guidelines found that password length" in rec
           and any("nist.sp.800-63b" in l["href"].lower()
                   for l in (as5 or {}).get("links", [])))
    print("   %s — AS-5 recommendations %d chars, link text inline, %d href(s) captured"
          % ("ok" if ok3 else "FAIL", len(rec), len((as5 or {}).get("links", []))))

    print("4. Scraped fields must reconstruct the shipped guidance field exactly")
    loc = {c["id"]: c for c in json.loads(
        (ROOT / "docs" / "assets" / "data" / "controls.json").read_text(encoding="utf-8"))}
    rebuilt = "%s Risk: %s" % (as5["recommendations"], as5["risk"])
    ok4 = rebuilt == loc["AS-5"].get("guidance", "")
    print("   %s — recommendations + ' Risk: ' + risk == shipped guidance (AS-5)"
          % ("ok" if ok4 else "FAIL"))

    return 0 if (ok and ok3 and ok4) else 1


def main():
    p = argparse.ArgumentParser(prog="scrape.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--no-cache", action="store_true", help="refetch instead of using research/corpus/raw/")
    sub = p.add_subparsers(dest="cmd")
    sp = sub.add_parser("controls"); sp.add_argument("--domain")
    sp = sub.add_parser("domains"); sp.add_argument("--domain")
    sub.add_parser("types")
    sub.add_parser("level-definitions")
    sub.add_parser("all")
    sub.add_parser("selftest")
    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)
    if not hasattr(args, "domain"):
        args.domain = None
    result = {"controls": cmd_controls, "domains": cmd_domains, "types": cmd_types,
              "level-definitions": cmd_level_definitions,
              "all": cmd_all, "selftest": cmd_selftest}[args.cmd](args)
    # Only selftest's return value IS an exit code; the others return scraped data, which
    # sys.exit() would otherwise print to stderr as an "error" and exit 1 on success.
    sys.exit(result if args.cmd == "selftest" else 0)


if __name__ == "__main__":
    main()
