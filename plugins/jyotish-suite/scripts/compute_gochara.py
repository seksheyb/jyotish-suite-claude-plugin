#!/usr/bin/env python3
"""
compute_gochara.py — deterministic Parashari transit (gochara) layer for the
vedic-astro skill.

Classical Parashari gochara judges a transiting planet by the sign it occupies
counted from the natal Moon (Janma Rashi); the Lagna is a secondary frame. The
dasha sets the period; transits narrow it and never override an un-activated
dasha. This script lays out every transit fact that judgement needs, so the
dasha-timing / reverse-question analysts and the synthesizer read them as
lookups instead of recomputing or recalling them.

WHAT IS DETERMINISTIC HERE (script-owned):
  - Sidereal longitudes (Lahiri by default, the ayanamsa the vedic
    chart-calculator uses; --ayanamsa kp for comparison) of each transit body
    at window start / mid / end, and every sign, nakshatra, kakshya (3d45'
    Ashtakavarga eighth) and pada ingress inside the window, via the shared
    lib/transit_engine.py sampler (one sample series per body, reused across
    all span sets; bisection-refined crossings; retrograde re-entries are
    separate stays by design).
  - Per position / sign stay: house from the natal Moon and from the Lagna,
    the classical favourable/unfavourable verdict and vedha house
    (jyotish_primitives.gochara_verdict), the sign's SAV bindus and the
    body's own BAV bindus, natal planets occupying the sign, whether the body
    is a running MD/AD/PD lord, and Saturn's Sade Sati / Kantaka / Ashtama
    phase.
  - Vedha obstruction at a stay's entry instant (or window start): which OTHER
    transiting bodies sit in the vedha house from the Moon, exempt pairs
    (Sun-Saturn, Moon-Mercury) excluded.
  - Kakshya fruitfulness: the kakshya lord contributed a bindu to the body in
    that sign (baseline ashtakavarga.prastara). None for Rahu/Ketu (no BAV).
  - Tara Bala of each transit nakshatra counted from the Janma Nakshatra.
  - Double transit (Jupiter AND Saturn touching a house by occupation or
    Parashari aspect: Jupiter 5/7/9, Saturn 3/7/10) at start / mid / end.
  - Optional D9 overlay (MODERN finer-timing layer, not classical gochara):
    the transit pada == one navamsha, with house from the D9 Lagna.

WHAT STAYS WITH THE LLM (never here):
  - Whether the dasha is activated for the question, and therefore whether a
    transit window means anything at all.
  - Weighing the layers (Moon frame vs Lagna frame, vedha vs bindus vs tara),
    re-checking vedha across a long stay when a fast obstructor moves, and
    picking THE window, confidence and caveats.

Input: the vedic baseline JSON from compute_vedic_baseline.py (lagna, planets,
d9, ashtakavarga incl. prastara, dasha.running). Fails loudly when a required
key is missing.

Usage:
  compute_gochara.py --baseline vedic_baseline.json \\
    --datetime 2026-01-01T00:00:00 [--end-datetime ISO | --window-days 180] \\
    --tz Asia/Kolkata [--bodies Saturn,Jupiter,Rahu,Ketu,Mars,Sun,Moon] \\
    [--ayanamsa lahiri|kp] [--d9-overlay | --no-d9-overlay] \\
    [--step-days N] [--out transits.json]

All datetimes inside the output are naive UTC ISO strings unless named
*_local.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
# lib/ lives at the plugin root; resolve it whether scripts/ is one or three
# levels below that root.
for _cand in (os.path.join(_HERE, "..", "lib"),
              os.path.join(_HERE, "..", "..", "..", "lib")):
    if os.path.isfile(os.path.join(_cand, "jyotish_primitives.py")):
        sys.path.insert(0, _cand)
        break
import ephemeris as eph  # noqa: E402
import jyotish_primitives as jp  # noqa: E402
import transit_engine as te  # noqa: E402

DEFAULT_BODIES = ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun", "Moon"]
# Bodies that get the pada->D9 overlay by default. The Moon is left out: it
# crosses a 3d20' pada every ~6 hours, so a 180-day window would carry ~700
# Moon pada hits (~360 KB) and swamp the slow-body signal a reader needs
# first. Opt in with --d9-overlay-bodies ...,Moon for a window of a few days.
DEFAULT_D9_BODIES = ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun"]
ALL_BODIES = list(jp.PLANETS)  # 9 grahas — every one can cause vedha
NODES = ("Rahu", "Ketu")
KAKSHYA_BODIES = ("Saturn", "Jupiter", "Rahu", "Ketu", "Mars")
DASHA_LEVELS = ("mahadasha", "antardasha", "pratyantardasha")

# Jupiter / Saturn houses touched by occupation (1) + Parashari aspect.
JUPITER_TOUCH = [1, 5, 7, 9]
SATURN_TOUCH = [1, 3, 7, 10]

# Upper bound on |daily motion| (deg/day) per body. Used only to tighten the
# sampling step so that no arc a body is scanned against can be crossed in
# fewer than two samples (the engine's DEFAULT_STEP_DAYS are tuned for signs
# and nakshatras for the Moon, not for its 3d20' padas).
MAX_SPEED = {"Moon": 15.4, "Sun": 1.02, "Mercury": 2.2, "Venus": 1.26,
             "Mars": 0.8, "Jupiter": 0.25, "Saturn": 0.14,
             "Rahu": 0.06, "Ketu": 0.06}
SIGN_ARC = 30.0

D9_OVERLAY_NOTE = (
    "Classical gochara is read in D1 only. One nakshatra pada (3°20') equals "
    "one navamsha, so a transit's pada places it in D9; this is a modern "
    "finer-timing layer, and the pada flips near boundaries under a different "
    "ayanamsa (Lahiri vs KP differ by ~6').")

NOTE = (
    "Deterministic here: sidereal transit positions, sign/nakshatra/kakshya/"
    "pada ingress dates (bisection-refined sampling), house from Moon and "
    "Lagna, classical favourable verdict + vedha house, vedha obstructors at "
    "each sign stay's entry instant (or window start; exempt pairs Sun-Saturn "
    "and Moon-Mercury excluded), SAV/BAV bindus, kakshya lord + fruitfulness "
    "(lord gave a bindu per the prastara), Tara Bala from the Janma Nakshatra, "
    "Saturn's Sade Sati/Kantaka/Ashtama phase, double transit at start/mid/end, "
    "and the modern D9 pada overlay. is_dasha_lord refers to the dasha running "
    "at reference.dasha_asof, not to every instant of the window. Stays with "
    "the LLM: whether the dasha is activated for the question (a transit never "
    "overrides an un-activated dasha), weighing Moon vs Lagna frame and vedha "
    "vs bindus vs tara, re-checking vedha across a long stay as fast bodies "
    "move, choosing the window, and stating confidence.")


# ====================================================================
# Baseline load + validation
# ====================================================================

def _dig(d, path):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def load_baseline(path):
    try:
        with open(path) as fh:
            baseline = json.load(fh)
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"ERROR: cannot read --baseline {path}: {exc}\n")
        sys.exit(1)
    if not isinstance(baseline, dict):
        sys.stderr.write(f"ERROR: --baseline {path} is not a JSON object.\n")
        sys.exit(1)
    required = [("lagna", "sign"), ("planets", "Moon", "sign"),
                ("planets", "Moon", "nakshatra"), ("d9", "lagna", "sign"),
                ("d9", "planets"), ("ashtakavarga", "sav_per_sign"),
                ("ashtakavarga", "bav_per_planet"),
                ("ashtakavarga", "prastara"), ("dasha", "asof")]
    required += [("dasha", "running", lvl, "lord") for lvl in DASHA_LEVELS]
    missing = [".".join(p) for p in required if _dig(baseline, p) is None]
    if missing:
        sys.stderr.write(
            f"ERROR: --baseline {path} is missing required key(s): {missing}. "
            "This script needs a compute_vedic_baseline.py output (lagna, "
            "planets, d9, ashtakavarga incl. prastara, dasha.running).\n")
        sys.exit(1)
    for p, row in baseline["planets"].items():
        if "sign" not in row:
            sys.stderr.write(f"ERROR: --baseline planets.{p} has no 'sign'.\n")
            sys.exit(1)
    return baseline


# ====================================================================
# Reference frame derived from the baseline
# ====================================================================

NAK_NAMES = [n for n, _ in jp.NAKSHATRAS]


def build_reference(baseline):
    planets = baseline["planets"]
    moon = planets["Moon"]
    moon_sign_idx = jp.SIGNS.index(moon["sign"])
    moon_nak_idx = NAK_NAMES.index(moon["nakshatra"])
    lagna_sign_idx = jp.SIGNS.index(baseline["lagna"]["sign"])
    d9_lagna_sign = baseline["d9"]["lagna"]["sign"]

    by_sign, d9_by_sign = {}, {}
    for p, row in planets.items():
        by_sign.setdefault(row["sign"], []).append(p)
    for p, row in baseline["d9"]["planets"].items():
        if "sign" in row:
            d9_by_sign.setdefault(row["sign"], []).append(p)
    order = {s: i for i, s in enumerate(jp.SIGNS)}
    running = baseline["dasha"]["running"]
    return {
        "moon_sign": moon["sign"],
        "moon_sign_idx": moon_sign_idx,
        "moon_nakshatra": moon["nakshatra"],
        "moon_nak_idx": moon_nak_idx,
        "lagna_sign": baseline["lagna"]["sign"],
        "lagna_sign_idx": lagna_sign_idx,
        "d9_lagna_sign": d9_lagna_sign,
        "natal_planets_by_sign": {s: by_sign[s] for s in
                                  sorted(by_sign, key=order.get)},
        "natal_d9_planets_by_sign": {s: d9_by_sign[s] for s in
                                     sorted(d9_by_sign, key=order.get)},
        "running_dasha": {lvl: running[lvl]["lord"] for lvl in DASHA_LEVELS},
        "dasha_asof": baseline["dasha"]["asof"],
    }


# ====================================================================
# Annotation
# ====================================================================

class Annotator:
    def __init__(self, baseline, ref):
        self.ref = ref
        av = baseline["ashtakavarga"]
        self.sav = av["sav_per_sign"]
        self.bav = av["bav_per_planet"]
        self.prastara = av["prastara"]
        self.d9_lagna_idx = jp.SIGNS.index(ref["d9_lagna_sign"])

    def sign_block(self, body, sign_idx):
        """Fields shared by positions snapshots and sign_stays hits."""
        ref = self.ref
        sign = jp.SIGNS[sign_idx]
        hfm = jp.count_signs(ref["moon_sign_idx"], sign_idx)
        bav_row = self.bav.get(body)
        out = {
            "house_from_moon": hfm,
            "house_from_lagna": jp.count_signs(ref["lagna_sign_idx"], sign_idx),
            "gochara": jp.gochara_verdict(body, hfm),
            "sav_bindus": self.sav.get(sign),
            "bav_bindus": (None if body in NODES or bav_row is None
                           else bav_row.get(sign)),
            "natal_planets_in_sign": list(
                ref["natal_planets_by_sign"].get(sign, [])),
            "is_dasha_lord": {lvl: body == ref["running_dasha"][lvl]
                              for lvl in DASHA_LEVELS},
        }
        if body == "Saturn":
            out["saturn_phase"] = jp.saturn_moon_phase(
                sign_idx, ref["moon_sign_idx"])
        return out

    def fruitful(self, body, sign, kakshya_lord):
        if body in NODES or body not in self.prastara:
            return None
        return kakshya_lord in self.prastara[body].get(sign, [])

    def tara(self, nak_idx):
        idx, name, fav = jp.tara_bala(self.ref["moon_nak_idx"], nak_idx)
        return {"idx": idx, "name": name, "favourable": fav}

    def position(self, body, snap):
        out = dict(snap)
        out.update(self.sign_block(body, snap["sign_idx"]))
        k_idx, k_lord = jp.kakshya_of(snap["longitude"])
        out["kakshya"] = {"idx": k_idx, "lord": k_lord,
                          "fruitful": self.fruitful(body, snap["sign"], k_lord)}
        out["tara"] = self.tara(snap["nak_idx"])
        return out

    def d9_fields(self, navamsa_idx):
        sign = jp.SIGNS[navamsa_idx]
        return {
            "house_from_d9_lagna": jp.count_signs(self.d9_lagna_idx,
                                                  navamsa_idx),
            "natal_d9_planets_in_sign": list(
                self.ref["natal_d9_planets_by_sign"].get(sign, [])),
            "layer": "modern_overlay",
        }


# ====================================================================
# Vedha + double transit
# ====================================================================

class SignCache:
    """Memoised sign index of every body at an instant (vedha needs all 9)."""

    def __init__(self, ayan_mode):
        self.mode = ayan_mode
        self._c = {}

    def sign_idx(self, body, dt_utc):
        key = (body, dt_utc)
        if key not in self._c:
            self._c[key] = te.snapshot(body, dt_utc, self.mode)["sign_idx"]
        return self._c[key]


def vedha_block(body, verdict, at_utc, ref, signs):
    house = verdict["vedha_house"]
    if not verdict["favourable"] or house is None:
        return {"house": None, "obstructed_by": [],
                "evaluated_at": at_utc.isoformat()}
    obstructed = []
    for other in ALL_BODIES:
        if other == body or jp.is_vedha_exempt(body, other):
            continue
        h = jp.count_signs(ref["moon_sign_idx"], signs.sign_idx(other, at_utc))
        if h == house:
            obstructed.append(other)
    return {"house": house, "obstructed_by": obstructed,
            "evaluated_at": at_utc.isoformat()}


def vedha_intervals(body, house, stay_start, stay_end, ref, all_stays):
    """Vedha as intervals, not a single instant: for a favourable sign stay
    [stay_start, stay_end], every stretch during which another graha sits in
    the vedha house (counted from the natal Moon). Exempt pairs
    (Sun-Saturn, Moon-Mercury) never obstruct each other. Returns
    {intervals: [{planet, start, end}], obstructed_to_end: bool,
    clear_at: ISO | None, clear_at_excluding_moon: ISO | None,
    obstructed_to_end_excluding_moon: bool} — clear_at is the instant after
    which no obstruction remains inside the stay (None when none ever occurs,
    or when one runs to the end of the stay); the *_excluding_moon pair
    repeats that reading without the Moon's brief passes."""
    vedha_sign = jp.sign_n_from(ref["moon_sign_idx"], house)
    intervals = []
    for other in ALL_BODIES:
        if other == body or jp.is_vedha_exempt(body, other):
            continue
        for st in all_stays[other]:
            if st["sign_idx"] != vedha_sign:
                continue
            o_start = parse_iso_utc(st["entry_date"])
            o_end = parse_iso_utc(st["exit_date"])
            lo, hi = max(stay_start, o_start), min(stay_end, o_end)
            if lo < hi:
                intervals.append({"planet": other, "start": lo.isoformat(),
                                  "end": hi.isoformat()})
    intervals.sort(key=lambda x: (x["start"], x["planet"]))

    def _clear(ivs):
        if not ivs:
            return False, None
        last_end = max(parse_iso_utc(x["end"]) for x in ivs)
        if last_end >= stay_end:
            return True, None
        return False, last_end.isoformat()

    to_end, clear_at = _clear(intervals)
    # The Moon crosses every sign in ~2.3 days and so re-obstructs briefly
    # again and again; this second reading ignores it so the clearing of the
    # substantive (non-Moon) obstruction is visible at a glance.
    _to_end_xm, clear_xm = _clear([x for x in intervals if x["planet"] != "Moon"])
    return {"intervals": intervals, "obstructed_to_end": to_end,
            "clear_at": clear_at,
            "clear_at_excluding_moon": clear_xm,
            "obstructed_to_end_excluding_moon": _to_end_xm}


def touched_signs(sign_idx, offsets):
    return {jp.sign_n_from(sign_idx, n) for n in offsets}


def double_transit_at(dt_utc, ref, signs):
    ju = signs.sign_idx("Jupiter", dt_utc)
    sa = signs.sign_idx("Saturn", dt_utc)
    both = touched_signs(ju, JUPITER_TOUCH) & touched_signs(sa, SATURN_TOUCH)
    lag, moon = ref["lagna_sign_idx"], ref["moon_sign_idx"]
    return {
        "datetime_utc": dt_utc.isoformat(),
        "from_lagna": sorted(jp.count_signs(lag, s) for s in both),
        "from_moon": sorted(jp.count_signs(moon, s) for s in both),
        "jupiter_house_from_lagna": jp.count_signs(lag, ju),
        "saturn_house_from_lagna": jp.count_signs(lag, sa),
        "jupiter_house_from_moon": jp.count_signs(moon, ju),
        "saturn_house_from_moon": jp.count_signs(moon, sa),
    }


# ====================================================================
# Sampling
# ====================================================================

def step_for(body, kakshya_on, d9_on, override):
    """Engine default, halved until the smallest arc scanned for this body
    takes at least two sampling steps to cross at the body's top speed."""
    if override:
        return override
    arcs = [SIGN_ARC, jp.NAK_ARC]
    if kakshya_on:
        arcs.append(te.KAKSHYA_ARC)
    if d9_on:
        arcs.append(te.PADA_ARC)
    safe = min(arcs) / (2.0 * MAX_SPEED[body])
    step = te.DEFAULT_STEP_DAYS[body]
    while step > safe:
        step /= 2.0
    return step


def scan(body, series, spans, lon_fn):
    hits = []
    for span in spans:
        hits.extend(te.find_hits(body, series, span, lon_fn))
    hits.sort(key=lambda h: h["entry_date"] or "")
    return hits


def round_floats(obj, nd=4):
    if isinstance(obj, float):
        return round(obj, nd)
    if isinstance(obj, dict):
        return {k: round_floats(v, nd) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, nd) for v in obj]
    return obj


def parse_iso_utc(s):
    return datetime.fromisoformat(s)


# ====================================================================
# Main
# ====================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Parashari gochara (transit) layer over a vedic baseline.")
    ap.add_argument("--baseline", required=True,
                    help="compute_vedic_baseline.py output JSON")
    ap.add_argument("--start-datetime", "--datetime", dest="start",
                    required=True, help="window start, ISO local time")
    ap.add_argument("--end-datetime", help="window end, ISO local time")
    ap.add_argument("--window-days", type=float, default=180.0,
                    help="window length in days when --end-datetime is not "
                         "given (default 180)")
    ap.add_argument("--tz", required=True, help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--bodies", default=",".join(DEFAULT_BODIES),
                    help="comma list of transit bodies (default "
                         + ",".join(DEFAULT_BODIES) + ")")
    ap.add_argument("--ayanamsa", choices=["lahiri", "kp"], default="lahiri")
    ap.add_argument("--d9-overlay", dest="d9", action="store_true",
                    default=True, help="emit the modern pada->D9 overlay "
                                       "(default on)")
    ap.add_argument("--no-d9-overlay", dest="d9", action="store_false")
    ap.add_argument("--d9-overlay-bodies", default=",".join(DEFAULT_D9_BODIES),
                    help="comma list of bodies that get the pada->D9 overlay "
                         "(default " + ",".join(DEFAULT_D9_BODIES) + "; the "
                         "Moon is excluded by default because it crosses ~4 "
                         "padas a day and would dominate the file — add "
                         "'Moon' for a window of a few days)")
    ap.add_argument("--step-days", type=float,
                    help="override the sampling step (days) for ALL bodies")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args()

    bodies = [b.strip() for b in args.bodies.split(",") if b.strip()]
    unknown = [b for b in bodies if b not in ALL_BODIES]
    if unknown or not bodies:
        ap.error(f"unknown --bodies {unknown}; choose from {ALL_BODIES}")
    if args.step_days is not None and args.step_days <= 0:
        ap.error("--step-days must be > 0")

    baseline = load_baseline(args.baseline)
    ref = build_reference(baseline)
    ann = Annotator(baseline, ref)

    start_local, start_utc = eph.to_utc(args.start, args.tz)
    if args.end_datetime:
        end_local, end_utc = eph.to_utc(args.end_datetime, args.tz)
    else:
        end_utc = start_utc + timedelta(days=args.window_days)
        end_local = start_local + timedelta(days=args.window_days)
    if end_utc <= start_utc:
        ap.error("--end-datetime must be after the window start")
    mid_utc = start_utc + (end_utc - start_utc) / 2
    instants = {"window_start": start_utc, "window_mid": mid_utc,
                "window_end": end_utc}

    mode = args.ayanamsa

    def lon_fn(body, dt_utc):
        return te.lon_at(body, dt_utc, mode)

    signs = SignCache(mode)
    sign_sp = te.sign_spans()
    nak_sp = te.nakshatra_spans()
    kak_sp = te.kakshya_spans()
    pada_sp = te.pada_spans() if args.d9 else None

    d9_bodies = [b.strip() for b in args.d9_overlay_bodies.split(",") if b.strip()]
    # Every graha's sign stays across the window, for vedha intervals. Cheap:
    # sign arcs are 30 deg, so the engine's default steps suffice for all 9.
    all_stays = {b: te.ingress_events(b, start_utc, end_utc, sign_sp, mode)
                 for b in ALL_BODIES}
    out_bodies = {}
    for body in bodies:
        kakshya_on = body in KAKSHYA_BODIES
        d9_on = args.d9 and body in d9_bodies
        step = step_for(body, kakshya_on, d9_on, args.step_days)
        series = te.sample_series(body, start_utc, end_utc, step, lon_fn)

        positions = {}
        for name, dt in instants.items():
            positions[name] = ann.position(body, te.snapshot(body, dt, mode))

        sign_stays = scan(body, series, sign_sp, lon_fn)
        for h in sign_stays:
            h.update(ann.sign_block(body, h["sign_idx"]))
            at = (start_utc if h["entry_before_window"]
                  else parse_iso_utc(h["entry_date"]))
            h["vedha"] = vedha_block(body, h["gochara"], at, ref, signs)
            if h["vedha"]["house"] is not None:
                h["vedha"].update(vedha_intervals(
                    body, h["vedha"]["house"], at,
                    parse_iso_utc(h["exit_date"]), ref, all_stays))
            else:
                h["vedha"].update({"intervals": [], "obstructed_to_end": False,
                                   "clear_at": None,
                                   "clear_at_excluding_moon": None,
                                   "obstructed_to_end_excluding_moon": False})

        nak_stays = scan(body, series, nak_sp, lon_fn)
        for h in nak_stays:
            h["tara"] = ann.tara(h["nak_idx"])

        kak_stays = None
        if kakshya_on:
            kak_stays = scan(body, series, kak_sp, lon_fn)
            for h in kak_stays:
                h["fruitful"] = ann.fruitful(body, h["sign"],
                                             h["kakshya_lord"])

        d9 = None
        if d9_on:
            d9 = scan(body, series, pada_sp, lon_fn)
            for h in d9:
                h.update(ann.d9_fields(h["navamsa_idx"]))

        out_bodies[body] = {
            "sampling_step_days": step,
            "positions": positions,
            "sign_stays": sign_stays,
            "nakshatra_stays": nak_stays,
            "kakshya_stays": kak_stays,
            "d9_overlay": d9,
        }

    ayan_start = eph.ayanamsa(eph.julian_day(start_utc), mode)
    out = {
        "script": "compute_gochara.py",
        "school": "vedic",
        "ayanamsa": {"mode": mode,
                     "value_dms_window_start": jp.deg_to_dms(ayan_start)},
        "window": {
            "start_local": start_local.isoformat(),
            "start_utc": start_utc.isoformat(),
            "end_local": end_local.isoformat(),
            "end_utc": end_utc.isoformat(),
            "tz": args.tz,
        },
        "reference": ref,
        "bodies": out_bodies,
        "double_transit": {name: double_transit_at(dt, ref, signs)
                           for name, dt in instants.items()},
        "d9_overlay_note": D9_OVERLAY_NOTE if args.d9 else None,
        "note": NOTE,
    }

    text = json.dumps(round_floats(out), indent=2, ensure_ascii=False,
                      default=str)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
