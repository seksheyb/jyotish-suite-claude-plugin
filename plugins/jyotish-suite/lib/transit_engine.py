#!/usr/bin/env python3
"""
transit_engine.py — the school-agnostic transit sampling engine.

Every transit script in the suite (KP significator-star confirmation in
scripts/compute_transits.py, Parashari gochara, BNN and Jaimini transit
scripts) builds on this one module instead of carrying its own copy of the
sampling/bisection loop. Nothing here knows about any school's
interpretation; it only answers "where was body B, and when did it enter /
leave arc A" for a caller-chosen ayanamsa and a caller-chosen set of arcs
("spans").

METHOD (intentionally sampling-based, not a closed-form transit solver):
  1. sample_series() walks a body's sidereal longitude across the window at a
     fixed step (DEFAULT_STEP_DAYS, or caller override), always including the
     exact end instant.
  2. find_hits() scans consecutive samples for in/out-of-span transitions on
     one span; every transition is refined by bisection (refine_crossing,
     BISECT_ITERS halvings -> sub-minute for a multi-day bracket).
  3. A run already inside the span at window start is flagged
     entry_before_window; a run still inside at window end is flagged
     exit_after_window. Retrograde re-entries are separate hits by design.

SPANS are dicts {"label": str, "start_deg": float, "end_deg": float, ...}.
Any extra keys are copied verbatim onto every hit produced from that span.
Spans may wrap through 0 deg Aries (start_deg > end_deg), see in_span().
Span builders: sign_spans, nakshatra_spans, pada_spans, kakshya_spans,
degree_point_span. Builder bounds are exact floats; round on emit if needed.

AYANAMSA is always explicit: ayan_mode is "kp" (KP-New, Krishnamurti) or
"lahiri" — the same names lib/ephemeris.AYANAMSA_MODES uses. There is no
default, so a Parashari script can never silently inherit KP's ayanamsa.

lon_fn injection: the scanning functions take lon_fn(body, dt_utc) -> float so
tests can drive synthetic motion. lib/ephemeris (and therefore pyswisseph) is
imported lazily, only when a real ephemeris longitude is needed.

Datetimes are naive UTC throughout.
"""

import os
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jyotish_primitives as jp  # noqa: E402

BISECT_ITERS = 20  # collapses a multi-day bracket to well under a minute.

# Sampling step per body, in days. Each is under one-third of the time the
# body needs to cross the smallest arc it will be sampled against (3d20' pada /
# 3d45' kakshya for slow bodies, 30 deg sign for fast ones), so no span can be
# skipped between two consecutive samples — including during a retrograde
# crawl, where the body moves slower still.
DEFAULT_STEP_DAYS = {"Moon": 0.25, "Sun": 1.0, "Mercury": 1.0, "Venus": 1.0,
                     "Mars": 2.0, "Jupiter": 2.0, "Saturn": 5.0,
                     "Rahu": 5.0, "Ketu": 5.0}

# Ashtakavarga kakshya (1/8 of a sign) lords, in order from 0 deg of each sign.
# Defined locally on purpose — do not import from jyotish_primitives.
KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury",
                 "Moon", "Lagna"]
KAKSHYA_ARC = 3.75  # 30 / 8 = 3d45'

PADA_ARC = jp.NAK_ARC / 4.0  # 3d20'

_eph = None


def _ephemeris():
    global _eph
    if _eph is None:
        import ephemeris as eph  # lazy: pulls in pyswisseph
        _eph = eph
    return _eph


# ====================================================================
# Longitude + span predicate
# ====================================================================

def lon_at(body, dt_utc, ayan_mode):
    """Sidereal longitude of `body` at a naive-UTC instant.
    ayan_mode is "kp" or "lahiri"."""
    eph = _ephemeris()
    if ayan_mode not in eph.AYANAMSA_MODES:
        raise ValueError(f"unknown ayan_mode {ayan_mode!r}; expected one of "
                         f"{sorted(eph.AYANAMSA_MODES)}")
    jd = eph.julian_day(dt_utc)
    ayan = eph.ayanamsa(jd, ayan_mode)
    lon, _retro, _spd = eph.planet_position(jd, body, ayan)
    return lon


def in_span(lon, lo, hi):
    """Half-open membership lo <= lon < hi, with 360 deg wraparound: when
    lo > hi the span runs lo -> 360 -> hi (e.g. [359, 1))."""
    if lo <= hi:
        return lo <= lon < hi
    return lon >= lo or lon < hi


def _default_lon_fn(ayan_mode):
    def fn(body, dt_utc):
        return lon_at(body, dt_utc, ayan_mode)
    return fn


# ====================================================================
# Sampling + crossing refinement
# ====================================================================

def sample_series(body, start_utc, end_utc, step_days, lon_fn):
    """[(dt_utc, lon), ...] across [start_utc, end_utc], step in days,
    always including the exact end instant."""
    series = []
    t = start_utc
    step = timedelta(days=step_days)
    while t < end_utc:
        series.append((t, lon_fn(body, t)))
        t += step
    series.append((end_utc, lon_fn(body, end_utc)))
    return series


def refine_crossing(body, lo, hi, t_lo, t_hi, target, lon_fn):
    """Binary-search the instant in (t_lo, t_hi) where in_span(lon, lo, hi)
    first equals `target` (a bool), assuming it differs from the value at
    t_lo. Returns a datetime close to (just after) the true crossing."""
    for _ in range(BISECT_ITERS):
        mid = t_lo + (t_hi - t_lo) / 2
        if in_span(lon_fn(body, mid), lo, hi) == target:
            t_hi = mid
        else:
            t_lo = mid
    return t_hi


_SPAN_CORE_KEYS = ("label", "start_deg", "end_deg")


def _make_hit(span, entry_date, entry_before_window, exit_date,
              exit_after_window):
    hit = {
        "label": span.get("label"),
        "entry_date": entry_date,
        "entry_before_window": entry_before_window,
        "exit_date": exit_date,
        "exit_after_window": exit_after_window,
    }
    for k, v in span.items():
        if k not in _SPAN_CORE_KEYS:
            hit[k] = v
    return hit


def find_hits(body, series, span, lon_fn):
    """Scan a precomputed sample series for every entry/exit through one
    span. Returns a list of hit dicts: label, entry_date, entry_before_window,
    exit_date, exit_after_window (ISO strings / bools) plus every extra key
    of the span copied verbatim."""
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
            run_start = refine_crossing(body, lo, hi, t_prev, t_cur, True,
                                        lon_fn)
            entry_before_window = False
        elif prev_in and not cur_in:
            exit_t = refine_crossing(body, lo, hi, t_prev, t_cur, False,
                                     lon_fn)
            hits.append(_make_hit(
                span, run_start.isoformat() if run_start else None,
                entry_before_window, exit_t.isoformat(), False))
            run_start, entry_before_window = None, False

    if run_start is not None and in_span(series[-1][1], lo, hi):
        hits.append(_make_hit(span, run_start.isoformat(),
                              entry_before_window,
                              series[-1][0].isoformat(), True))
    return hits


def ingress_events(body, start_utc, end_utc, spans, ayan_mode,
                   step_days=None, lon_fn=None):
    """Sample `body` once across the window and run find_hits over every span.
    Returns all hits sorted by entry_date (stable sort; None sorts first)."""
    if lon_fn is None:
        lon_fn = _default_lon_fn(ayan_mode)
    if step_days is None:
        step_days = DEFAULT_STEP_DAYS[body]
    series = sample_series(body, start_utc, end_utc, step_days, lon_fn)
    hits = []
    for span in spans:
        hits.extend(find_hits(body, series, span, lon_fn))
    hits.sort(key=lambda h: h["entry_date"] or "")
    return hits


# ====================================================================
# Span builders
# ====================================================================

def sign_spans():
    """12 x 30 deg sign spans."""
    return [{"label": name, "start_deg": i * 30.0, "end_deg": (i + 1) * 30.0,
             "sign": name, "sign_idx": i}
            for i, name in enumerate(jp.SIGNS)]


def nakshatra_spans():
    """27 x 13d20' nakshatra spans."""
    return [{"label": name, "start_deg": i * jp.NAK_ARC,
             "end_deg": (i + 1) * jp.NAK_ARC,
             "nakshatra": name, "nak_idx": i, "star_lord": lord}
            for i, (name, lord) in enumerate(jp.NAKSHATRAS)]


def pada_spans():
    """108 x 3d20' pada spans; navamsa sign taken at each pada's midpoint."""
    spans = []
    for k in range(108):
        lo, hi = k * PADA_ARC, (k + 1) * PADA_ARC
        nak_idx, pada0 = divmod(k, 4)
        nav_idx, nav_name = jp.navamsa_sign((lo + hi) / 2.0)
        name = jp.NAKSHATRAS[nak_idx][0]
        spans.append({"label": f"{name} pada {pada0 + 1}",
                      "start_deg": lo, "end_deg": hi,
                      "nakshatra": name, "nak_idx": nak_idx,
                      "pada": pada0 + 1,
                      "navamsa_sign": nav_name, "navamsa_idx": nav_idx})
    return spans


def kakshya_spans():
    """96 x 3d45' Ashtakavarga kakshya spans (8 per sign)."""
    spans = []
    for si, sign in enumerate(jp.SIGNS):
        for ki, lord in enumerate(KAKSHYA_LORDS):
            lo = si * 30.0 + ki * KAKSHYA_ARC
            spans.append({"label": f"{sign} kakshya {ki + 1} ({lord})",
                          "start_deg": lo, "end_deg": lo + KAKSHYA_ARC,
                          "sign": sign, "sign_idx": si,
                          "kakshya_idx": ki, "kakshya_lord": lord})
    return spans


def degree_point_span(target_lon, orb, label=None, **extra):
    """Span [target - orb, target + orb), normalised to [0, 360) with
    wraparound (so [359, 1) is valid). orb must be in (0, 180)."""
    if not 0 < orb < 180:
        raise ValueError("orb must be > 0 and < 180 degrees")
    target = jp.norm360(target_lon)
    span = {"label": label if label is not None else f"{target:.4f}+/-{orb}",
            "start_deg": jp.norm360(target - orb),
            "end_deg": jp.norm360(target + orb)}
    span.update(extra)
    return span


# ====================================================================
# Position snapshot
# ====================================================================

def snapshot(body, dt_utc, ayan_mode):
    """Positional snapshot of `body` at a naive-UTC instant, keeping speed
    (deg/day) and retrograde from the ephemeris. Longitudes rounded to 4 dp,
    as jyotish_primitives.full_lord_chain does for the KP path."""
    eph = _ephemeris()
    jd = eph.julian_day(dt_utc)
    ayan = eph.ayanamsa(jd, ayan_mode)
    lon, retro, speed = eph.planet_position(jd, body, ayan)
    lon = jp.norm360(lon)
    si, sign, _sl = jp.get_sign(lon)
    ni, nak, star_lord, _ns = jp.get_nakshatra(lon)
    nav_idx, nav_name = jp.navamsa_sign(lon)
    return {
        "longitude": round(lon, 4),
        "sign": sign,
        "sign_idx": si,
        "deg_in_sign": round(jp.deg_in_sign(lon), 4),
        "nakshatra": nak,
        "nak_idx": ni,
        "pada": jp.get_pada(lon),
        "star_lord": star_lord,
        "navamsa_sign": nav_name,
        "navamsa_idx": nav_idx,
        "retrograde": bool(retro),
        "speed": round(speed, 4),
        "datetime_utc": dt_utc.isoformat(),
    }
