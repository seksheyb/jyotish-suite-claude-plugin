#!/usr/bin/env python3
"""
compute_transits.py — deterministic forward-transit confirmation for KP timing.

KP event-timing (kp-natal Event Timing Step 7, kp-horary Phase 7) needs to
check whether transiting Jupiter, Sun and Moon pass through the *star*
(nakshatra) of a natal significator planet during a candidate dasha window —
until now this was prose-only reasoning in both skill prompts, with no
deterministic backing (documented gap, OPTIMIZATION-BLUEPRINT.md section 6
delta #1). This script closes that gap.

WHAT IS DETERMINISTIC HERE (script-owned):
  - The sidereal longitude of transiting Jupiter/Sun/Moon at any instant,
    KP-New ayanamsa (swe.SIDM_KRISHNAMURTI, same "kp" mode used by
    lib/ephemeris.kp_natal_chart / compute_kp_natal_baseline.py /
    compute_kp_horary_baseline.py — never Lahiri here).
  - "The star of a significator planet P" = the (up to 3) nakshatra arcs
    whose star_lord is P (jyotish_primitives.NAKSHATRAS repeats the 9-lord
    Vimshottari sequence three times across the 27 nakshatras). Given a
    significator's *name* the script derives these arcs itself; it does not
    need to be told a span. A significators file that already carries
    explicit [start_deg, end_deg] pairs is honored as-is instead.
  - A sampling-based scan (see below) of each transit body's longitude
    across the requested window, finding every entry/exit through each such
    arc, refined by bisection to a sub-hour instant.

WHAT STAYS WITH THE LLM (never here):
  - Whether a transit hit actually *confirms* the event (KP transit theory
    weighs Jupiter/Saturn signifying the house, Moon as the fastest trigger,
    combined with the CSL/significator/RP/dasha chain already produced by
    compute_kp_natal_baseline.py / compute_kp_horary_baseline.py and
    find_fruitful_window.py) — this script only reports WHERE the transiting
    body was and WHEN it was in a significator's star, not what that means.
  - Confidence, caveats, and the final Step-8 verdict.

SAMPLING METHOD (documented per the task's guardrail — this is intentionally
sampling-based, not a closed-form transit solver):
  For each transit body a fixed daily/sub-daily step is walked across the
  window (Moon 6h, Sun 1 day, Jupiter 2 days — chosen so no body can skip
  over a 13d20' nakshatra arc between samples, including during a
  retrograde crawl). Consecutive samples are checked for "inside a target
  arc" transitions; every transition is refined by binary search on the
  bracketing pair of samples down to ~1 minute of resolution. Retrograde
  stations naturally produce multiple separate entry/exit pairs for the
  same nakshatra within one window — that is correct KP behaviour, not a
  bug, and is reported as separate hits.

Input significators file — any of these three JSON shapes:
  1. A flat list of planet names:            ["Jupiter", "Saturn", "Mercury"]
  2. A grouped dict (e.g. a house's L1-L4 significator slice straight out of
     compute_kp_natal_baseline.py / compute_kp_horary_baseline.py):
       {"L1": ["Venus"], "L2": ["Jupiter", "Rahu"], "L3": [...], "L4": [...]}
     — all planet names across all groups are flattened and deduplicated.
  3. A dict already mapping planet -> explicit [start_deg, end_deg] pairs:
       {"Jupiter": [[86.67, 100.0], [193.33, 206.67], [326.67, 340.0]]}
     — used verbatim, no derivation.

Usage:
  compute_transits.py --start-datetime "2026-08-01T00:00:00" \\
    --end-datetime "2026-11-15T00:00:00" --tz "Asia/Kolkata" \\
    --significators significators.json

  # Or a start + implicit window length instead of an explicit end:
  compute_transits.py --datetime "2026-08-01T00:00:00" --window-days 45 \\
    --tz "Asia/Kolkata" --significators significators.json --lat 28.6139 --lon 77.2090
"""

import argparse
import json
import os
import sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402

TRANSIT_BODIES = ["Jupiter", "Sun", "Moon"]
AYAN_MODE = "kp"  # KP-New — same mode name compute_kp_natal_baseline.py uses.

# Sampling step per body, in days. Chosen so a body cannot cross an entire
# 13d20' nakshatra arc between two consecutive samples even at its fastest
# realistic speed (Moon ~13-15 deg/day, Sun ~1 deg/day, Jupiter <=0.25 deg/day
# even at peak direct speed, essentially motionless near stations).
STEP_DAYS = {"Moon": 0.25, "Sun": 1.0, "Jupiter": 2.0}

BISECT_ITERS = 20  # collapses a multi-day bracket to well under a minute.


# ====================================================================
# Significator -> nakshatra-arc(s) derivation
# ====================================================================

def planet_nakshatra_spans(planet):
    """Every nakshatra arc (start_deg, end_deg, name) whose star_lord is
    `planet`. Up to 3 per planet (27 nakshatras / 9 Vimshottari lords)."""
    spans = []
    for idx, (name, star_lord) in enumerate(jp.NAKSHATRAS):
        if star_lord == planet:
            lo = idx * jp.NAK_ARC
            spans.append({"nakshatra": name,
                          "start_deg": round(lo, 4),
                          "end_deg": round(lo + jp.NAK_ARC, 4)})
    return spans


def _looks_like_span_pairs(value):
    return (isinstance(value, list) and len(value) > 0
            and all(isinstance(pair, (list, tuple)) and len(pair) == 2
                    and all(isinstance(x, (int, float)) for x in pair)
                    for pair in value))


def load_significators(path):
    """Return {planet_name: [{"nakshatra", "start_deg", "end_deg"}, ...]}
    from any of the three accepted JSON shapes (see module docstring)."""
    with open(path) as fh:
        data = json.load(fh)

    if isinstance(data, list):
        names = [str(x) for x in data]
        return {p: planet_nakshatra_spans(p) for p in dict.fromkeys(names)}

    if isinstance(data, dict):
        non_empty = [v for v in data.values() if v]
        if non_empty and all(_looks_like_span_pairs(v) for v in non_empty):
            return {planet: [{"nakshatra": None,
                              "start_deg": round(float(lo), 4),
                              "end_deg": round(float(hi), 4)}
                             for lo, hi in pairs]
                   for planet, pairs in data.items()}
        # Grouped dict (e.g. {"L1": [...], "L2": [...], ...}) or a flat
        # {name: "Planet"} shape — flatten every string value found.
        names = []
        for v in data.values():
            if isinstance(v, list):
                names.extend(str(x) for x in v)
            elif isinstance(v, str):
                names.append(v)
        return {p: planet_nakshatra_spans(p) for p in dict.fromkeys(names)}

    raise ValueError("significators file must be a JSON list or object")


# ====================================================================
# Transit longitude sampling + crossing refinement
# ====================================================================

def lon_at(body, dt_utc):
    """Sidereal longitude of `body` at a naive-UTC instant, KP-New ayanamsa."""
    jd = eph.julian_day(dt_utc)
    ayan = eph.ayanamsa(jd, AYAN_MODE)
    lon, _retro, _spd = eph.planet_position(jd, body, ayan)
    return lon


def in_span(lon, lo, hi):
    """lo/hi are plain (non-wrapping) degrees-in-zodiac — every nakshatra arc
    fits inside a single 0-360 pass, so no 360-wraparound handling needed."""
    return lo <= lon < hi


def sample_series(body, start_utc, end_utc, step_days):
    """[(dt_utc, lon), ...] across [start_utc, end_utc], step in days,
    always including the exact end instant."""
    series = []
    t = start_utc
    step = timedelta(days=step_days)
    while t < end_utc:
        series.append((t, lon_at(body, t)))
        t += step
    series.append((end_utc, lon_at(body, end_utc)))
    return series


def refine_crossing(body, lo, hi, t_lo, t_hi, target):
    """Binary-search the instant in (t_lo, t_hi) where in_span(lon, lo, hi)
    first equals `target` (a bool), assuming it differs from the value at
    t_lo. Returns a datetime close to the true crossing."""
    for _ in range(BISECT_ITERS):
        mid = t_lo + (t_hi - t_lo) / 2
        if in_span(lon_at(body, mid), lo, hi) == target:
            t_hi = mid
        else:
            t_lo = mid
    return t_hi


def find_hits(body, series, span):
    """Scan a precomputed (body) sample series for every entry/exit through
    one nakshatra arc. Returns a list of hit dicts (nakshatra, entry_date,
    exit_date, entry_before_window, exit_after_window)."""
    lo, hi = span["start_deg"], span["end_deg"]
    hits = []
    run_start = series[0][0] if in_span(series[0][1], lo, hi) else None
    entry_before_window = run_start is not None

    for i in range(1, len(series)):
        t_prev, lon_prev = series[i - 1]
        t_cur, lon_cur = series[i]
        prev_in = in_span(lon_prev, lo, hi)
        cur_in = in_span(lon_cur, lo, hi)
        if not prev_in and cur_in:
            run_start = refine_crossing(body, lo, hi, t_prev, t_cur, True)
            entry_before_window = False
        elif prev_in and not cur_in:
            exit_t = refine_crossing(body, lo, hi, t_prev, t_cur, False)
            hits.append({
                "nakshatra": span["nakshatra"],
                "entry_date": run_start.isoformat() if run_start else None,
                "entry_before_window": entry_before_window,
                "exit_date": exit_t.isoformat(),
                "exit_after_window": False,
            })
            run_start, entry_before_window = None, False

    if run_start is not None and in_span(series[-1][1], lo, hi):
        hits.append({
            "nakshatra": span["nakshatra"],
            "entry_date": run_start.isoformat(),
            "entry_before_window": entry_before_window,
            "exit_date": series[-1][0].isoformat(),
            "exit_after_window": True,
        })
    return hits


def position_snapshot(body, dt_utc, label):
    lon = lon_at(body, dt_utc)
    chain = jp.full_lord_chain(lon)
    chain["label"] = label
    chain["datetime_utc"] = dt_utc.isoformat()
    return chain


# ====================================================================
# CLI
# ====================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Forward transit confirmation (Jupiter/Sun/Moon vs "
                    "significator stars) for KP timing — sidereal, KP-New "
                    "ayanamsa.")
    ap.add_argument("--datetime", help="window start, ISO local "
                                       "(alias for --start-datetime)")
    ap.add_argument("--start-datetime", help="window start, ISO local")
    ap.add_argument("--end-datetime", help="window end, ISO local "
                                           "(default: start + --window-days)")
    ap.add_argument("--window-days", type=float, default=30.0,
                   help="window length in days if --end-datetime omitted "
                        "(default 30)")
    ap.add_argument("--tz", required=True, help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--lat", type=float, help="context only — not needed for "
                                              "transit longitudes")
    ap.add_argument("--lon", type=float, help="context only — not needed for "
                                              "transit longitudes")
    ap.add_argument("--significators", required=True,
                   help="path to a significators JSON file (see module "
                        "docstring for the 3 accepted shapes)")
    ap.add_argument("--step-days", type=float,
                   help="override the sampling step (days) for ALL bodies "
                        "(default: per-body — Moon 0.25, Sun 1.0, Jupiter 2.0)")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args()

    start_iso = args.start_datetime or args.datetime
    if not start_iso:
        ap.error("need --start-datetime (or --datetime)")

    start_local, start_utc = eph.to_utc(start_iso, args.tz)
    if args.end_datetime:
        end_local, end_utc = eph.to_utc(args.end_datetime, args.tz)
    else:
        end_utc = start_utc + timedelta(days=args.window_days)
        end_local = start_local + timedelta(days=args.window_days)
    if end_utc <= start_utc:
        ap.error("--end-datetime must be after the window start")

    sig_spans = load_significators(args.significators)
    if not sig_spans:
        sys.stderr.write("WARNING: no significator planets resolved from "
                         f"{args.significators} — hits will be empty.\n")

    mid_utc = start_utc + (end_utc - start_utc) / 2

    transits = {}
    for body in TRANSIT_BODIES:
        step = args.step_days or STEP_DAYS[body]
        series = sample_series(body, start_utc, end_utc, step)

        hits = []
        for planet, spans in sig_spans.items():
            for span in spans:
                for h in find_hits(body, series, span):
                    h["significator"] = planet
                    hits.append(h)
        hits.sort(key=lambda h: h["entry_date"] or "")

        transits[body] = {
            "sampling_step_days": step,
            "positions": {
                "window_start": position_snapshot(body, start_utc, "window_start"),
                "window_mid": position_snapshot(body, mid_utc, "window_mid"),
                "window_end": position_snapshot(body, end_utc, "window_end"),
            },
            "hits": hits,
        }

    ayan_start = eph.ayanamsa(eph.julian_day(start_utc), AYAN_MODE)
    ayan_end = eph.ayanamsa(eph.julian_day(end_utc), AYAN_MODE)

    out = {
        "script": "compute_transits.py",
        "ayanamsa": {
            "mode": AYAN_MODE,
            "value_dms_window_start": jp.deg_to_dms(ayan_start),
            "value_dms_window_end": jp.deg_to_dms(ayan_end),
        },
        "window": {
            "start_local": start_local.isoformat(),
            "start_utc": start_utc.isoformat(),
            "end_local": end_local.isoformat(),
            "end_utc": end_utc.isoformat(),
            "tz": args.tz,
        },
        "location": ({"lat": args.lat, "lon": args.lon}
                    if args.lat is not None and args.lon is not None else None),
        "significators_resolved": sig_spans,
        "transits": transits,
    }

    text = json.dumps(out, indent=2, default=str)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
