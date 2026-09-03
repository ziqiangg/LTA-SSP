"""RQ-6 baseline scorer: wizard-tree rule-based baseline + majority-class floor
against research/evals/v1/cases.jsonl, per ADR-006's methodology.

Ticks (the CASES table below) were read off each case's description by a human
applying wizard.js's own question wording, per ADR-006 point 1 -- this script
does NOT do any text extraction itself. resolve() is a direct line-for-line port
of docs/assets/js/wizard.js's resolve()/cloudTierTypes(), pinned as of the
wizard.js version read while writing ADR-006 (2026-09-03), then updated for
ADR-007's hosting-unknown hedge (same day) -- see ADR-006's amendment note.
If wizard.js changes again, re-derive the ticks against the new question set
and re-run.

Usage: python research/scripts/score_rq6_baseline.py
"""

import json
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "research" / "evals" / "v1" / "cases.jsonl"
PROFILES_PATH = ROOT / "docs" / "assets" / "data" / "profiles.json"

RUNG_TYPE = {"sandbox": "sandbox", "low": "low-risk-cloud"}


def cloud_tier_types(rungs, cii):
    types = []
    if "sandbox" in rungs:
        types.append("sandbox")
    if "low" in rungs:
        types.append("low-risk-cloud")
    if "sensitive" in rungs:
        if cii == "yes":
            types.append("high-risk-cloud")
        elif cii == "no":
            types.append("medium-risk-cloud")
        else:
            types.append("medium-risk-cloud")
            types.append("high-risk-cloud")
    return types


def resolve(state):
    """Port of wizard.js resolve() as of ADR-007 (2026-09-03): hosting-unanswered
    now hedges with low-risk-on-premises when a non-sandbox rung is ticked,
    matching the CII hedge idiom. state: hosting, rungs(set), cii, genai, ds."""
    types = []
    if state["hosting"] == "on-premises":
        if state["rungs"]:
            return {"blocked": "on-prem + cloud rung"}
        types.append("low-risk-on-premises")
    elif state["hosting"] == "cloud" and not state["rungs"]:
        return {"incomplete": True}

    if state["hosting"] != "on-premises" and state["rungs"]:
        cloud_types = cloud_tier_types(state["rungs"], state["cii"])
        if "sandbox" in state["rungs"] and "high-risk-cloud" in cloud_types:
            return {"blocked": "sandbox + CII (or unanswered CII hedging toward it)"}
        types += cloud_types
        if state["hosting"] == "" and ({"low", "sensitive"} & state["rungs"]):
            types.append("low-risk-on-premises")

    if state["genai"]:
        types.append("generative-ai")
    if state["ds"] == "others":
        types.append("digital-services-others")
    if state["ds"] == "high-impact":
        types.append("digital-services-high-impact")

    if not types:
        return {"incomplete": True}
    return {"types": types}


def empty_state():
    return {"hosting": "", "rungs": set(), "cii": "", "genai": False, "ds": ""}


def mk(**kw):
    s = empty_state()
    s.update(kw)
    if "rungs" in kw and not isinstance(kw["rungs"], set):
        s["rungs"] = set(kw["rungs"])
    return s


# ---------------------------------------------------------------------------
# Human ticks, one entry per case (ADR-006 point 1). `state` is the FULL tick
# set used for retrieval metrics (real UI behaviour: everything ticked,
# hedges/ties unioned). `candidates` is a list of *singleton* alternative
# states used for Top-1/Top-3 classification scoring wherever `state` reflects
# a hedge (CII unanswered) or a genuine rung tie -- ADR-006 point 3, extended
# by the same logic to rung ties (both are the wizard unioning candidate
# profiles under stated uncertainty). Empty `candidates` means resolve()
# returned blocked/incomplete: no candidate to score.
# ---------------------------------------------------------------------------
CASES = {
    "EV-001": dict(
        why="[ADR-007] Hosting never stated, but payroll/NRIC/bank files read Confidential-band "
            "-> 'sensitive' rung now reachable with hosting blank. CII never mentioned -> hedge. "
            "3 candidates: on-prem alone, cloud+CII-no, cloud+CII-yes.",
        state=mk(rungs={"sensitive"}, cii=""),
        candidates=[
            mk(hosting="on-premises"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="no"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="yes"),
        ],
    ),
    "EV-002": dict(
        why="'government commercial cloud' stated -> cloud. ACRA/financial statements read "
            "Restricted not Confidential per label_basis -> 'low' rung. WOGAA tracking unstated "
            "-> ds left unticked.",
        state=mk(hosting="cloud", rungs={"low"}),
        candidates=[mk(hosting="cloud", rungs={"low"})],
    ),
    "EV-003": dict(
        why="Main public site with stated visits (2.4M/yr) -> ds=high-impact. Hosting explicitly "
            "hedged ('I think...?') -> left unticked.",
        state=mk(ds="high-impact"),
        candidates=[mk(ds="high-impact")],
    ),
    "EV-004": dict(
        why="'GCC AWS account' -> cloud. Singpass + licence PII reads Confidential-band -> "
            "'sensitive' rung; CII never mentioned -> cii hedge. Traffic unknown but public-facing "
            "-> ds=others (label_basis: 'plausibly under' 1M).",
        state=mk(hosting="cloud", rungs={"sensitive"}, cii="", ds="others"),
        candidates=[
            mk(hosting="cloud", rungs={"sensitive"}, cii="no", ds="others"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="yes", ds="others"),
        ],
    ),
    "EV-005": dict(
        why="[ADR-007] Same pattern as EV-001: NRIC/addresses/complainant identities read "
            "Confidential-band -> 'sensitive' rung, hosting blank. CII never mentioned -> hedge.",
        state=mk(rungs={"sensitive"}, cii=""),
        candidates=[
            mk(hosting="on-premises"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="no"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="yes"),
        ],
    ),
    "EV-006": dict(
        why="S3/Redshift stated -> cloud. NRIC in raw layer reads Confidential-band -> 'sensitive' "
            "rung; CII never mentioned -> cii hedge. Internal analytics tool, not public-facing.",
        state=mk(hosting="cloud", rungs={"sensitive"}, cii=""),
        candidates=[
            mk(hosting="cloud", rungs={"sensitive"}, cii="no"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="yes"),
        ],
    ),
    "EV-007": dict(
        why="[ADR-007] Hosting explicitly unknown ('I'd have to check'), but land parcels/asset "
            "locations read Restricted -> 'low' rung now reachable with hosting blank. Public "
            "viewer is secondary/cut-down, not established as WOGAA-tracked -> ds left unticked. "
            "No CII question (low rung doesn't trigger it) -> 2 candidates.",
        state=mk(rungs={"low"}),
        candidates=[
            mk(hosting="on-premises"),
            mk(hosting="cloud", rungs={"low"}),
        ],
    ),
    "EV-008": dict(
        why="Vendor-run platform, architecture explicitly unknown -> hosting unticked. Not "
            "public-facing.",
        state=mk(),
        candidates=[],
    ),
    "EV-009": dict(
        why="[ADR-007] 'SharePoint based' does not disambiguate cloud vs on-prem -> hosting left "
            "unticked, but records/contracts/minutes under a classification scheme read "
            "Confidential-band ('Restricted to Confidential' per label_basis; ticking the higher "
            "band present, not a tie) -> 'sensitive' rung now reachable. CII unmentioned -> hedge.",
        state=mk(rungs={"sensitive"}, cii=""),
        candidates=[
            mk(hosting="on-premises"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="no"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="yes"),
        ],
    ),
    "EV-010": dict(
        why="[ADR-007] Same SharePoint hosting ambiguity as EV-009, but sensitivity is 'clearly "
            "low' per label_basis (the pilot's one unambiguous-low case) -> 'low' rung now "
            "reachable with hosting blank. No CII question -> 2 candidates.",
        state=mk(rungs={"low"}),
        candidates=[
            mk(hosting="on-premises"),
            mk(hosting="cloud", rungs={"low"}),
        ],
    ),
    "EV-011": dict(
        why="'Genesys, the cloud version' -> cloud. Sensitivity genuinely torn per label_basis "
            "('push toward Confidential... but low-risk is defensible') -> tick both 'low' and "
            "'sensitive' (wizard's own 'tick several if unsure' idiom). CII never mentioned -> "
            "hedge on top of the tie. Agent tool, not public-facing.",
        state=mk(hosting="cloud", rungs={"low", "sensitive"}, cii=""),
        candidates=[
            mk(hosting="cloud", rungs={"low"}),
            mk(hosting="cloud", rungs={"sensitive"}, cii="no"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="yes"),
        ],
    ),
    "EV-012": dict(
        why="Clearly a public Digital Service (Singpass login) but traffic genuinely undecidable "
            "(180k downloads / 40k MAU vs. 1M visits/yr -- label_basis: 'genuinely undecidable') "
            "and the ds question is a radio with no 'unsure' state -> left unticked rather than "
            "guessed. Hosting never mentioned.",
        state=mk(),
        candidates=[],
    ),
    "EV-013": dict(
        why="'staging... separate AWS account' -> cloud + 'sandbox' rung (literal environment "
            "label). 'current staging data is effectively live citizen data' independently reads "
            "Confidential-band -> 'sensitive' rung too (both facts separately, affirmatively "
            "stated -- not a hedge-under-uncertainty). CII never mentioned -> hedge, which reaches "
            "high-risk-cloud and triggers the sandbox+CII block.",
        state=mk(hosting="cloud", rungs={"sandbox", "sensitive"}, cii=""),
        candidates=[],  # blocked
    ),
    "EV-014": dict(
        why="Chatbot answering from internal documents via a model -> genai=True (core function). "
            "Hosting explicitly hedged ('Azure OpenAI I believe, or... now') -> left unticked. "
            "Staff-only pilot, not public-facing.",
        state=mk(genai=True),
        candidates=[mk(genai=True)],
    ),
    "EV-015": dict(
        why="[ADR-007] Hosting never mentioned, but invoice/GIRO billing data reads "
            "Confidential/Sensitive-High per label_basis -> 'sensitive' rung now reachable with "
            "hosting blank. CII unmentioned -> hedge.",
        state=mk(rungs={"sensitive"}, cii=""),
        candidates=[
            mk(hosting="on-premises"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="no"),
            mk(hosting="cloud", rungs={"sensitive"}, cii="yes"),
        ],
    ),
}


def load_cases():
    cases = {}
    with open(CASES_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            c = json.loads(line)
            cases[c["id"]] = c
    return cases


def merge_profiles(type_ids, profiles):
    """Union of controlIds across type_ids' profiles, level = min() across
    every profile the control appears in (F-005/F-007: strictness runs
    downward, L0 mandatory -> L2 optional, so most-stringent = min())."""
    merged = {}
    for t in type_ids:
        for entry in profiles.get(t, []):
            cid, lvl = entry["controlId"], entry["level"]
            if cid not in merged or lvl < merged[cid]:
                merged[cid] = lvl
    return merged


def result_bucket(result):
    if "blocked" in result:
        return "blocked"
    if "incomplete" in result:
        return "incomplete"
    return "ok"


def score():
    labels = load_cases()
    with open(PROFILES_PATH, encoding="utf-8") as f:
        profiles = json.load(f)

    assert set(labels) == set(CASES), f"case-id mismatch: {set(labels) ^ set(CASES)}"

    # --- majority-class floor: most common single acceptable_answers entry ---
    from collections import Counter
    entry_counts = Counter()
    for c in labels.values():
        for ans in c["acceptable_answers"]:
            entry_counts[frozenset(ans)] += 1
    majority_entry, majority_n = entry_counts.most_common(1)[0]
    majority_types = sorted(majority_entry)

    rows = []
    bucket_counts = Counter()
    hedge_n = 0
    top1_hits = top3_hits = 0
    maj_top1_hits = 0
    by_ambiguity = {}  # tag -> [top1_hits, n]
    by_difficulty = {}

    for cid in sorted(labels):
        case = labels[cid]
        spec = CASES[cid]
        state = spec["state"]
        result = resolve(state)
        bucket = result_bucket(result)
        bucket_counts[bucket] += 1

        acceptable = [frozenset(a) for a in case["acceptable_answers"]]

        # classification scoring
        cand_sets = []
        for cand_state in spec["candidates"]:
            r = resolve(cand_state)
            if "types" in r:
                cand_sets.append(frozenset(r["types"]))
        is_hedge = len(spec["candidates"]) > 1
        if is_hedge:
            hedge_n += 1

        if bucket != "ok":
            top1 = False
            top3 = False
        elif is_hedge:
            top1 = False  # ADR-006 rule 3: hedge/tie never Top-1 correct
            top3 = any(cs in acceptable for cs in cand_sets)
        else:
            only = cand_sets[0] if cand_sets else frozenset(result.get("types", []))
            top1 = only in acceptable
            top3 = top1

        top1_hits += top1
        top3_hits += top3

        maj_hit = frozenset(majority_types) in acceptable
        maj_top1_hits += maj_hit

        for tag in case["ambiguity"]:
            by_ambiguity.setdefault(tag, [0, 0])
            by_ambiguity[tag][1] += 1
            by_ambiguity[tag][0] += int(top1)
        by_difficulty.setdefault(case["difficulty"], [0, 0])
        by_difficulty[case["difficulty"]][1] += 1
        by_difficulty[case["difficulty"]][0] += int(top1)

        # retrieval scoring: predicted = actual merged UI output (full state,
        # hedges unioned, as controls.js would really compose it); ground
        # truth = union across ALL acceptable_answers entries (methodological
        # simplification -- see results write-up).
        predicted_types = result.get("types", [])
        predicted = merge_profiles(predicted_types, profiles)
        truth_types = sorted({t for ans in case["acceptable_answers"] for t in ans})
        truth = merge_profiles(truth_types, profiles)

        tp = set(predicted) & set(truth)
        precision = len(tp) / len(predicted) if predicted else None
        recall = len(tp) / len(truth) if truth else None
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision is not None and recall is not None and (precision + recall) > 0
            else None
        )
        l0_truth = {c for c, lvl in truth.items() if lvl == 0}
        l0_recall = (
            len(l0_truth & set(predicted)) / len(l0_truth) if l0_truth else None
        )

        rows.append(
            dict(
                id=cid,
                bucket=bucket,
                is_hedge=is_hedge,
                predicted_types=predicted_types,
                truth_types=truth_types,
                top1=top1,
                top3=top3,
                maj_hit=maj_hit,
                precision=precision,
                recall=recall,
                f1=f1,
                l0_recall=l0_recall,
                ambiguity=case["ambiguity"],
                difficulty=case["difficulty"],
                why=spec["why"],
            )
        )

    n = len(rows)
    out = {
        "n": n,
        "majority_types": majority_types,
        "majority_n": majority_n,
        "majority_top1_acc": maj_top1_hits / n,
        "bucket_counts": dict(bucket_counts),
        "hedge_n": hedge_n,
        "wizard_top1_acc": top1_hits / n,
        "wizard_top3_acc": top3_hits / n,
        "by_ambiguity": {k: (v[0], v[1]) for k, v in sorted(by_ambiguity.items())},
        "by_difficulty": {k: (v[0], v[1]) for k, v in sorted(by_difficulty.items())},
        "rows": rows,
    }
    return out


if __name__ == "__main__":
    result = score()
    print(json.dumps(result, indent=2, default=str))
