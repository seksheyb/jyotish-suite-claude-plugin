#!/usr/bin/env python3
"""
KP Natal — fruitful Vimshottari window finder.

Deterministic here: rebuilding the full MD->BD->AD->SD Vimshottari tree from
the natal Moon (via lib/jyotish_primitives.py — no year tables reimplemented
here), pruning it to windows that overlap the requested search horizon, and
scoring every MD/BD/AD/SD quartet by mechanical significator-set membership:
how many of its 4 lords appear as a significator (L1-L4, per
compute_kp_natal_baseline.py's `significators` block) of a house in the
question's positive set, and whether any lord signifies ONLY houses in the
negative set (a red flag) with none of the positive set. This replaces the
"examine the upcoming periods and find a match" LLM inspection of the dasha
tree in kp-natal event timing.

NOT deterministic — stays with the LLM: picking THE window among near-ties,
weighting MD vs BD vs AD vs SD significance, cross-checking against forward
transits (scripts/compute_transits.py) and Ruling Planets, reconciling with
the event's house-combination note (e.g. "10-CSL must signify 11 strongly"),
and stating confidence / caveats to the user.

Input: the kp-natal baseline JSON produced by compute_kp_natal_baseline.py
(needs its `planets.Moon.longitude`, `datetime_utc`, and `significators`
blocks — errors loudly if any are missing). Does not call swisseph; no
optional third-party dependencies.

Usage:
    python find_fruitful_window.py \
      --baseline kp_natal_baseline.json \
      --houses 2,7,11 \
      [--negative 6,10] \
      [--years 5] \
      [--from-date "2026-07-23T00:00:00"] \
      [--top 25] [--min-score 1] \
      [--out fruitful_windows.json]

`--from-date` is a naive datetime interpreted as UTC (matching the dasha
tree's own convention — see jyotish_primitives.build_dasha_tree); it defaults
to the current UTC moment. `--years` is the forward search horizon from that
date (default 5).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
# lib/ lives at the plugin root; resolve it whether scripts/ is one or three
# levels below that root.
for _cand in (os.path.join(_HERE, "..", "lib"),
              os.path.join(_HERE, "..", "..", "..", "lib")):
    if os.path.isfile(os.path.join(_cand, "jyotish_primitives.py")):
        sys.path.insert(0, _cand)
        break
import jyotish_primitives as jp  # noqa: E402

ROLES = ("MD", "BD", "AD", "SD")
# Full Vimshottari cycle = 120 years regardless of starting lord — rebuilding
# with n_md=9 from the natal Moon guarantees the tree covers any realistic
# reading date + horizon, without depending on whatever n_md the baseline
# happened to be generated with.
FULL_CYCLE_MD_COUNT = 9


# ====================================================================
# Baseline load + validation
# ====================================================================

def load_baseline(path):
    with open(path) as fh:
        baseline = json.load(fh)
    missing = [k for k in ("planets", "significators", "datetime_utc")
               if k not in baseline]
    if missing:
        sys.stderr.write(
            f"ERROR: --baseline {path} is missing required key(s): {missing}. "
            "This script needs a compute_kp_natal_baseline.py output "
            "(planets.Moon.longitude, significators, datetime_utc).\n")
        sys.exit(1)
    if "Moon" not in baseline["planets"] or "longitude" not in baseline["planets"]["Moon"]:
        sys.stderr.write(
            "ERROR: --baseline JSON has no planets.Moon.longitude — cannot "
            "rebuild the Vimshottari tree.\n")
        sys.exit(1)
    school = baseline.get("school")
    if school and school != "kp-natal":
        sys.stderr.write(
            f"WARNING: --baseline declares school='{school}', not 'kp-natal'. "
            "Significator levels (L1-L4) are KP-specific; proceeding anyway "
            "since the required keys are present.\n")
    return baseline


def parse_naive_utc(dt_str):
    """Parse an ISO datetime string, dropping any tzinfo (naive-UTC convention
    shared with jyotish_primitives.build_dasha_tree)."""
    dt = datetime.fromisoformat(dt_str)
    return dt.replace(tzinfo=None)


# ====================================================================
# Significator reverse-index: planet -> houses it signifies, with the
# L1-L4 level(s) that fired, so citations are lookups not recall.
# ====================================================================

def build_signified_index(significators):
    """Return {planet: {house_int: [levels...]}} from the baseline's
    per-house L1-L4 significator block."""
    index = {}
    for house_str, levels in significators.items():
        house = int(house_str)
        for level in ("L1", "L2", "L3", "L4"):
            for planet in levels.get(level, []):
                index.setdefault(planet, {}).setdefault(house, []).append(level)
    return index


def lord_signification(planet, signified_index, positive_set, negative_set):
    """Return the per-lord significator detail + positive/negative hits."""
    houses = signified_index.get(planet, {})
    signifies = [{"house": h, "levels": sorted(levels)}
                 for h, levels in sorted(houses.items())]
    positive_hit = sorted(h for h in houses if h in positive_set)
    negative_hit = sorted(h for h in houses if h in negative_set)
    return {
        "lord": planet,
        "signifies_houses": signifies,
        "positive_hit": positive_hit,
        "negative_hit": negative_hit,
    }


# ====================================================================
# Tree walk — prune to the horizon, emit one candidate per SD leaf.
# ====================================================================

def overlaps(node, horizon_start, horizon_end):
    start = datetime.fromisoformat(node["start"])
    end = datetime.fromisoformat(node["end"])
    return start < horizon_end and end > horizon_start


def walk_candidates(tree, horizon_start, horizon_end):
    """Yield (md_lord, bd_lord, ad_lord, sd_lord, start_iso, end_iso) for
    every SD leaf whose window overlaps [horizon_start, horizon_end)."""
    scanned = 0
    for md in tree:
        if not overlaps(md, horizon_start, horizon_end):
            continue
        for bd in md["bhuktis"]:
            if not overlaps(bd, horizon_start, horizon_end):
                continue
            for ad in bd["antaras"]:
                if not overlaps(ad, horizon_start, horizon_end):
                    continue
                for sd in ad["sookshmas"]:
                    scanned += 1
                    if not overlaps(sd, horizon_start, horizon_end):
                        continue
                    yield {
                        "MD": md["md_lord"], "BD": bd["bd_lord"],
                        "AD": ad["ad_lord"], "SD": sd["sd_lord"],
                        "start": sd["start"], "end": sd["end"],
                    }, scanned


# ====================================================================
# Scoring
# ====================================================================

def score_candidate(window, signified_index, positive_set, negative_set):
    per_lord = {}
    for role in ROLES:
        per_lord[role] = lord_signification(window[role], signified_index,
                                            positive_set, negative_set)

    lords_signifying_positive = sum(1 for role in ROLES if per_lord[role]["positive_hit"])
    total_positive_hits = sum(len(per_lord[role]["positive_hit"]) for role in ROLES)
    negative_exclusive_roles = sorted(
        role for role in ROLES
        if per_lord[role]["negative_hit"] and not per_lord[role]["positive_hit"]
    )
    clean = not negative_exclusive_roles

    start = datetime.fromisoformat(window["start"])
    end = datetime.fromisoformat(window["end"])
    return {
        "start_utc": window["start"],
        "end_utc": window["end"],
        "duration_days": round((end - start).total_seconds() / 86400.0, 2),
        "lords": {role: window[role] for role in ROLES},
        "per_lord_signification": per_lord,
        "score": {
            "lords_signifying_positive": lords_signifying_positive,
            "total_positive_house_hits": total_positive_hits,
            "negative_exclusive_lords": negative_exclusive_roles,
            "clean": clean,
        },
    }


def rank_key(candidate):
    s = candidate["score"]
    return (
        -s["lords_signifying_positive"],
        0 if s["clean"] else 1,
        -s["total_positive_house_hits"],
        candidate["start_utc"],
    )


# ====================================================================
# CLI
# ====================================================================

def parse_house_list(raw, flag_name):
    if not raw:
        return set()
    out = set()
    for tok in raw.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            h = int(tok)
        except ValueError:
            sys.stderr.write(f"ERROR: {flag_name} must be comma-separated house "
                             f"numbers 1-12, got '{tok}'.\n")
            sys.exit(1)
        if not 1 <= h <= 12:
            sys.stderr.write(f"ERROR: {flag_name} house '{h}' out of range 1-12.\n")
            sys.exit(1)
        out.add(h)
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Scan the Vimshottari MD/BD/AD/SD tree for windows whose "
                    "period lords signify a question's positive houses.")
    ap.add_argument("--baseline", required=True,
                    help="path to a compute_kp_natal_baseline.py output JSON")
    ap.add_argument("--houses", required=True,
                    help="comma-separated positive house set, e.g. 2,7,11")
    ap.add_argument("--negative", default="",
                    help="comma-separated negative/obstruction house set, e.g. 6,10")
    ap.add_argument("--years", type=float, default=5.0,
                    help="forward search horizon in years from --from-date (default 5)")
    ap.add_argument("--from-date",
                    help="naive ISO datetime (UTC), search start; defaults to now (UTC)")
    ap.add_argument("--top", type=int, default=25,
                    help="max ranked candidates to return (default 25)")
    ap.add_argument("--min-score", type=int, default=1,
                    help="drop candidates with fewer than this many lords "
                         "signifying a positive house (default 1; use 0 to "
                         "keep every window in the horizon)")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args()

    positive_set = parse_house_list(args.houses, "--houses")
    negative_set = parse_house_list(args.negative, "--negative")
    if not positive_set:
        sys.stderr.write("ERROR: --houses must name at least one house.\n")
        sys.exit(1)

    baseline = load_baseline(args.baseline)
    signified_index = build_signified_index(baseline["significators"])

    moon_lon = baseline["planets"]["Moon"]["longitude"]
    birth_dt = parse_naive_utc(baseline["datetime_utc"])
    tree = jp.build_dasha_tree(moon_lon, birth_dt, n_md=FULL_CYCLE_MD_COUNT)

    horizon_start = (parse_naive_utc(args.from_date) if args.from_date
                     else datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None))
    horizon_end = horizon_start + timedelta(days=args.years * jp.YEAR_DAYS)

    candidates = []
    scanned_total = 0
    for window, scanned_total in walk_candidates(tree, horizon_start, horizon_end):
        candidates.append(score_candidate(window, signified_index,
                                          positive_set, negative_set))

    windows_matching = [c for c in candidates
                        if c["score"]["lords_signifying_positive"] >= args.min_score]
    windows_matching.sort(key=rank_key)
    ranked = windows_matching[:args.top]
    for i, c in enumerate(ranked, start=1):
        c["rank"] = i

    result = {
        "school": "kp-natal",
        "delta": "find_fruitful_window",
        "baseline_source": os.path.abspath(args.baseline),
        "search": {
            "from_date_utc": horizon_start.isoformat(),
            "horizon_years": args.years,
            "horizon_end_utc": horizon_end.isoformat(),
            "positive_houses": sorted(positive_set),
            "negative_houses": sorted(negative_set),
            "min_score": args.min_score,
        },
        "windows_scanned_in_horizon": scanned_total,
        "windows_matching_min_score": len(windows_matching),
        "windows_returned": len(ranked),
        "candidates": ranked,
        "note": ("Deterministic: tree rebuild, horizon overlap, significator-set "
                "membership, and the mechanical score/clean flag above. Picking "
                "THE window among ties or near-ties, weighting MD vs BD vs AD vs "
                "SD strength, cross-checking against compute_transits.py forward "
                "transits and the Ruling Planets, and stating confidence to the "
                "user all stay with the LLM."),
    }

    out_json = json.dumps(result, indent=2, default=str)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(out_json)
        sys.stderr.write(f"Wrote {len(ranked)} ranked window(s) to {args.out}\n")
    else:
        print(out_json)


if __name__ == "__main__":
    main()
