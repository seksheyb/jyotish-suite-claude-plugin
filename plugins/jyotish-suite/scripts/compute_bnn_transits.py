#!/usr/bin/env python3
"""
compute_bnn_transits.py — deterministic Bhrigu Nandi Nadi (BNN) transit layer.

BNN has no Lagna and no Moon-chart. Its timing comes from the slow planets —
Jupiter, Saturn, Rahu, Ketu — moving OVER natal planets (same sign =
conjunction, activating that natal planet's karakatwas) or aspecting them by
BNN aspects (7th for every planet; Mars 4/8, Jupiter 5/9, Saturn 3/10,
Rahu/Ketu 5/9 — BNN_SPECIAL_ASPECTS in compute_bnn_baseline.py), plus the
planet-to-planet sign relationship (1 conjunction, 5/9 trine, 6/8 dusthana,
2/12 adjacent, 7 opposition). Jupiter's ~12-year return to its natal sign is
the backbone of BNN life-event timing; degree-exact passes (within --orb) over
a natal planet are the finest trigger, and retrograde triple passes show up
as pass 1/2/3 on the same natal planet.

WHAT IS DETERMINISTIC HERE (script-owned):
  - Sidereal (Lahiri by default) positions of each transit body at window
    start / mid / end (lib/transit_engine.snapshot).
  - Every sign stay of each body in the window (sign_spans), annotated with
    the natal planets it conjoins / aspects by BNN rules, the 1..12 count
    from each natal planet's sign, and whether the conjoined/aspected natal
    planets are running dasha lords.
  - Every degree-exact conjunction (natal longitude +/- orb) with pass
    numbering, and the karakatwas of the natal planet activated.
  - Jupiter's cycle: returns to the natal Jupiter sign inside the window, or
    the next return found by scanning forward up to 13 years.

WHAT STAYS WITH THE LLM (never here):
  - Whether a transit actually times the event. Dasha activation sets the
    period; a slow transit over the Karaka (or its dasha lord) narrows it;
    transits never override an un-activated dasha.

Method: one te.sample_series per body (step te.DEFAULT_STEP_DAYS[body] unless
--step-days), reused via te.find_hits across the 12 sign spans and all nine
natal degree-point spans; every crossing is bisection-refined.

Usage:
  compute_bnn_transits.py --baseline bnn_baseline.json \\
    --datetime 2026-01-01T00:00:00 --window-days 365 --tz Asia/Kolkata \\
    [--bodies Jupiter,Saturn,Rahu,Ketu] [--ayanamsa lahiri] [--orb 1.0] \\
    [--step-days N] [--out transits.json]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import pytz

_HERE = os.path.dirname(os.path.abspath(__file__))
# lib/ lives at the plugin root; resolve it whether scripts/ is one or three
# levels below that root.
for _cand in (os.path.join(_HERE, "..", "lib"),
              os.path.join(_HERE, "..", "..", "..", "lib")):
    if os.path.isfile(os.path.join(_cand, "jyotish_primitives.py")):
        sys.path.insert(0, _cand)
        break
sys.path.insert(0, _HERE)
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402
import transit_engine as te  # noqa: E402
from compute_bnn_baseline import BNN_SPECIAL_ASPECTS  # noqa: E402

NATAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Rahu", "Ketu"]
DEFAULT_BODIES = "Jupiter,Saturn,Rahu,Ketu"
DASHA_LEVELS = ("mahadasha", "antardasha", "pratyantardasha")
DAYS_PER_YEAR = 365.2425

# Jupiter next-return forward scan: ~2-day samples, up to 13 years (one
# sidereal Jupiter cycle is ~11.86 years).
NEXT_RETURN_STEP_DAYS = 2.0
NEXT_RETURN_MAX_YEARS = 13

RELATION_LABELS = {1: "conjunction", 5: "trine", 9: "trine",
                   6: "dusthana", 8: "dusthana", 2: "adjacent",
                   12: "adjacent", 7: "opposition", 3: "neutral",
                   4: "neutral", 10: "neutral", 11: "neutral"}


# ====================================================================
# Baseline load + validation
# ====================================================================

def _die(msg):
    sys.stderr.write(f"ERROR: {msg}\n")
    sys.exit(1)


def load_baseline(path):
    try:
        with open(path) as fh:
            baseline = json.load(fh)
    except (OSError, ValueError) as exc:
        _die(f"cannot read --baseline {path}: {exc}")
    missing = [k for k in ("planets", "chart_meta", "natural_karakas", "dasha")
               if k not in baseline]
    if missing:
        _die(f"--baseline {path} is missing required key(s): {missing}. "
             "This script needs a compute_bnn_baseline.py output.")
    if "datetime_utc" not in baseline["chart_meta"]:
        _die("--baseline chart_meta has no datetime_utc (birth instant).")
    bad = [p for p in NATAL_PLANETS
           if p not in baseline["planets"]
           or any(k not in baseline["planets"][p]
                  for k in ("sign", "sign_idx", "longitude"))]
    if bad:
        _die(f"--baseline planets missing or lacking sign/sign_idx/longitude "
             f"for: {bad}")
    school = baseline.get("school")
    if school and school != "bnn":
        sys.stderr.write(
            f"WARNING: --baseline declares school='{school}', not 'bnn'; "
            "proceeding since the required keys are present.\n")
    return baseline


def parse_naive_utc(dt_str):
    return datetime.fromisoformat(dt_str).replace(tzinfo=None)


# ====================================================================
# Annotation helpers
# ====================================================================

def natal_by_sign(natal):
    by_sign = {}
    for p in NATAL_PLANETS:
        by_sign.setdefault(natal[p]["sign_idx"], []).append(p)
    return by_sign


def dasha_lords(running):
    """{level: lord} for MD/AD/PD, or {} when the baseline has no running."""
    if not running:
        return {}
    return {lvl: (running.get(lvl) or {}).get("lord") for lvl in DASHA_LEVELS}


def dasha_flags(planet, lords):
    return {lvl: bool(lords) and lords.get(lvl) == planet
            for lvl in DASHA_LEVELS}


def annotate_sign(body, transit_sign_idx, natal, by_sign, lords):
    """Conjunction / BNN-aspect / relationship annotations for `body`
    standing in sign `transit_sign_idx`."""
    conjoined = list(by_sign.get(transit_sign_idx, []))
    aspected = {}
    for n in sorted(set([7] + BNN_SPECIAL_ASPECTS.get(body, []))):
        tgt = jp.sign_n_from(transit_sign_idx, n)
        for p in by_sign.get(tgt, []):
            aspected[p] = n
    relation = {}
    for p in NATAL_PLANETS:
        count = jp.count_signs(natal[p]["sign_idx"], transit_sign_idx)
        relation[p] = {"count": count, "label": RELATION_LABELS[count]}
    touched = conjoined + [p for p in NATAL_PLANETS if p in aspected]
    return {
        "natal_planets_conjoined": conjoined,
        "natal_planets_aspected": {p: aspected[p] for p in NATAL_PLANETS
                                   if p in aspected},
        "relation_to_natal": relation,
        "is_dasha_lord": dasha_flags(body, lords),
        "dasha_lords_touched": [p for p in touched
                                if any(dasha_flags(p, lords).values())],
    }


def karakatwas(natural_karakas, planet):
    entry = natural_karakas.get(planet)
    if isinstance(entry, dict):
        keys = [k for k in ("primary_signification", "secondary_signification")
                if k in entry]
        if keys:
            return {k: entry[k] for k in keys}
    return entry


def age_years(birth_utc, dt_utc):
    return round((dt_utc - birth_utc).total_seconds() / 86400.0
                 / DAYS_PER_YEAR, 2)


# ====================================================================
# Jupiter cycle
# ====================================================================

def jupiter_cycle(natal, sign_stays, birth_utc, start_utc, end_utc,
                  ayan_mode, lon_fn):
    natal_idx = natal["Jupiter"]["sign_idx"]
    in_sign = [h for h in sign_stays if h["sign_idx"] == natal_idx]
    returns = [h["entry_date"] for h in in_sign
               if not h["entry_before_window"]]
    in_at_start = any(h["entry_before_window"] for h in in_sign)

    next_return = None
    if not returns:
        span = te.sign_spans()[natal_idx]
        scan_end = end_utc + timedelta(days=NEXT_RETURN_MAX_YEARS
                                       * DAYS_PER_YEAR)
        series = te.sample_series("Jupiter", end_utc, scan_end,
                                  NEXT_RETURN_STEP_DAYS, lon_fn)
        for h in te.find_hits("Jupiter", series, span, lon_fn):
            if not h["entry_before_window"]:
                next_return = h["entry_date"]
                break

    return {
        "natal_jupiter_sign": natal["Jupiter"]["sign"],
        "natal_jupiter_sign_idx": natal_idx,
        "in_natal_sign_at_window_start": in_at_start,
        "returns_in_window": returns,
        "return_ages_in_window": [age_years(birth_utc, parse_naive_utc(d))
                                  for d in returns],
        "age_at_window_start": age_years(birth_utc, start_utc),
        "next_return_estimate_utc": next_return,
        "age_at_next_return": (age_years(birth_utc,
                                         parse_naive_utc(next_return))
                               if next_return else None),
        "next_return_scan": (None if returns else
                             {"step_days": NEXT_RETURN_STEP_DAYS,
                              "max_years": NEXT_RETURN_MAX_YEARS}),
    }


# ====================================================================
# CLI
# ====================================================================

def main():
    ap = argparse.ArgumentParser(
        description="BNN transit activation: slow planets over / aspecting "
                    "natal planets, exact-degree passes, Jupiter cycle.")
    ap.add_argument("--baseline", required=True,
                    help="compute_bnn_baseline.py output JSON")
    ap.add_argument("--datetime", help="window start, ISO local "
                                       "(alias for --start-datetime)")
    ap.add_argument("--start-datetime", help="window start, ISO local")
    ap.add_argument("--end-datetime", help="window end, ISO local "
                                           "(default: start + --window-days)")
    ap.add_argument("--window-days", type=float, default=365.0,
                    help="window length in days if --end-datetime omitted "
                         "(default 365)")
    ap.add_argument("--tz", required=True, help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--bodies", default=DEFAULT_BODIES,
                    help=f"comma-separated transit bodies (default {DEFAULT_BODIES})")
    ap.add_argument("--ayanamsa", choices=["lahiri", "kp"], default="lahiri",
                    help="sidereal mode (default lahiri, as the BNN chart uses)")
    ap.add_argument("--orb", type=float, default=1.0,
                    help="degree orb for exact conjunctions (default 1.0)")
    ap.add_argument("--step-days", type=float,
                    help="override the sampling step (days) for ALL bodies")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args()

    start_iso = args.start_datetime or args.datetime
    if not start_iso:
        ap.error("need --start-datetime (or --datetime)")
    if not 0 < args.orb < 180:
        ap.error("--orb must be > 0 and < 180")
    if args.step_days is not None and args.step_days <= 0:
        ap.error("--step-days must be > 0")
    bodies = [b.strip() for b in args.bodies.split(",") if b.strip()]
    unknown = [b for b in bodies if b not in te.DEFAULT_STEP_DAYS]
    if not bodies or unknown:
        ap.error(f"unknown/empty --bodies: {unknown or args.bodies}; expected "
                 f"names from {sorted(te.DEFAULT_STEP_DAYS)}")

    try:
        tz = pytz.timezone(args.tz)
    except pytz.UnknownTimeZoneError:
        ap.error(f"unknown --tz {args.tz!r}")
    start_local, start_utc = eph.to_utc(start_iso, args.tz)
    if args.end_datetime:
        end_local, end_utc = eph.to_utc(args.end_datetime, args.tz)
    else:
        end_utc = start_utc + timedelta(days=args.window_days)
        end_local = pytz.UTC.localize(end_utc).astimezone(tz)
    if end_utc <= start_utc:
        ap.error("window end must be after the window start")
    mid_utc = start_utc + (end_utc - start_utc) / 2

    baseline = load_baseline(args.baseline)
    natal = {p: baseline["planets"][p] for p in NATAL_PLANETS}
    by_sign = natal_by_sign(natal)
    dasha = baseline.get("dasha") or {}
    running = dasha.get("running")
    lords = dasha_lords(running)
    birth_utc = parse_naive_utc(baseline["chart_meta"]["datetime_utc"])
    nk = baseline["natural_karakas"]

    def lon_fn(body, dt):
        return te.lon_at(body, dt, args.ayanamsa)

    signs = te.sign_spans()
    conj_spans = [te.degree_point_span(natal[p]["longitude"], args.orb,
                                       label=f"conj {p}", natal_planet=p)
                  for p in NATAL_PLANETS]

    out_bodies = {}
    for body in bodies:
        step = args.step_days or te.DEFAULT_STEP_DAYS[body]
        series = te.sample_series(body, start_utc, end_utc, step, lon_fn)

        positions = {}
        for key, dt in (("window_start", start_utc), ("window_mid", mid_utc),
                        ("window_end", end_utc)):
            snap = te.snapshot(body, dt, args.ayanamsa)
            snap.update(annotate_sign(body, snap["sign_idx"], natal, by_sign,
                                      lords))
            positions[key] = snap

        sign_stays = []
        for span in signs:
            for h in te.find_hits(body, series, span, lon_fn):
                h.update(annotate_sign(body, h["sign_idx"], natal, by_sign,
                                       lords))
                sign_stays.append(h)
        sign_stays.sort(key=lambda h: h["entry_date"] or "")

        conj = []
        for span in conj_spans:
            conj.extend(te.find_hits(body, series, span, lon_fn))
        conj.sort(key=lambda h: h["entry_date"] or "")
        passes = {}
        for h in conj:
            n = h["natal_planet"]
            passes[n] = passes.get(n, 0) + 1
            h["pass_number"] = passes[n]
            h["natal_longitude"] = round(natal[n]["longitude"], 4)
            h["orb"] = round(args.orb, 4)
            h["natal_planet_is_dasha_lord"] = dasha_flags(n, lords)
            h["karakatwas_activated"] = karakatwas(nk, n)

        out_bodies[body] = {
            "sampling_step_days": step,
            "positions": positions,
            "sign_stays": sign_stays,
            "exact_conjunctions": conj,
            "jupiter_cycle": (jupiter_cycle(natal, sign_stays, birth_utc,
                                            start_utc, end_utc, args.ayanamsa,
                                            lon_fn)
                              if body == "Jupiter" else None),
        }

    out = {
        "script": "compute_bnn_transits.py",
        "school": "bnn",
        "ayanamsa": {"mode": args.ayanamsa},
        "window": {
            "start_local": start_local.isoformat(),
            "start_utc": start_utc.isoformat(),
            "end_local": end_local.isoformat(),
            "end_utc": end_utc.isoformat(),
            "tz": args.tz,
        },
        "reference": {
            "natal_planets": {p: {"sign": natal[p]["sign"],
                                  "sign_idx": natal[p]["sign_idx"],
                                  "longitude": round(natal[p]["longitude"], 4)}
                              for p in NATAL_PLANETS},
            "birth_utc": birth_utc.isoformat(),
            "running_dasha": ({lvl: lords.get(lvl) for lvl in DASHA_LEVELS}
                              if lords else None),
            "dasha_asof": dasha.get("asof"),
        },
        "bodies": out_bodies,
        "note": ("Positional facts only. relation_to_natal.count = signs from "
                 "the natal planet's sign to the transit sign (1..12, "
                 "inclusive). natal_planets_aspected uses BNN aspects (7th "
                 "always; Mars 4/8, Jupiter 5/9, Saturn 3/10, Rahu/Ketu 5/9). "
                 "is_dasha_lord / natal_planet_is_dasha_lord refer to the "
                 "dasha running at reference.dasha_asof, not at each transit "
                 "date. Dasha activation sets the period; a slow transit over "
                 "the Karaka (or its dasha lord) narrows it; transits never "
                 "override an un-activated dasha."),
    }

    text = json.dumps(out, indent=2, default=str)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
