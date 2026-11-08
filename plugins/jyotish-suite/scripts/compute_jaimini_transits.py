#!/usr/bin/env python3
"""
Jaimini — transit triggers read from the Jaimini reference signs.

Jaimini times events with Chara Dasha (sign periods); a slow transit narrows
the period, it never overrides it. This script reads the slow bodies
(default Jupiter, Saturn, Rahu, Ketu) sign-to-sign against the reference
signs already fixed in a compute_jaimini_baseline.py output:

  AL               Arudha Lagna — worldly manifestation
  UL               Upapada — marriage / committed partnership
  dasha_rasi       the running Chara Dasha (Mahadasha) Rasi
  antardasha_rasi  the Antardasha Rasi (window start in `reference`; each
                   annotation uses the one running at its own instant)
  karakamsha       the Atmakaraka's navamsha sign, projected onto D1
  atmakaraka       the Atmakaraka's own D1 sign

Deterministic here (lib/transit_engine.py sampling + bisection, Lahiri by
default): sign stays of each body with entry/exit dates; for every snapshot
and every stay, the house counted from AL / UL / dasha Rasi / antardasha Rasi,
which reference signs the transit sign conjoins (same sign) or aspects by
Rasi Drishti (lib jaimini_drishti_matrix — symmetric, every aspect mutual),
Argala on AL and on the dasha Rasi (2nd/4th/11th primary, 5th secondary) with
the natal planets in the obstructing (Virodha) sign (12th/10th/3rd/9th), whether
the body is the dasha Rasi's Jaimini lord, and the Jupiter+Saturn "double
transit" on AL / UL / dasha Rasi / Karakamsha at window start / mid / end.

Optional (--karakamsha-overlay): each body's nakshatra-pada stays, the pada's
navamsha compared with the Karakamsha. LINEAGE-SPECIFIC, not Jaimini Sutra
text — every overlay hit carries "layer": "lineage_specific".

NOT deterministic — stays with the LLM: whether a Virodha planet actually
outweighs the Argala, benefic vs malefic reading of a trigger, and how a
transit trigger ranks against Chara Dasha activation.

Input: a compute_jaimini_baseline.py JSON built WITH --target-date (or --age),
so chara_dasha.running is populated. Exits 1 otherwise.

Usage:
    python compute_jaimini_transits.py --baseline jaimini_baseline.json \
      --datetime 2026-01-01T00:00:00 --window-days 365 --tz Asia/Kolkata \
      [--bodies Jupiter,Saturn,Rahu,Ketu] [--ayanamsa lahiri|kp] \
      [--karakamsha-overlay] [--step-days N] [--out transits.json]
"""

import argparse
import json
import os
import sys
from datetime import timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
# lib/ lives at the plugin root; resolve it whether scripts/ is one or three
# levels below that root.
for _cand in (os.path.join(_HERE, "..", "lib"),
              os.path.join(_HERE, "..", "..", "..", "lib")):
    if os.path.isfile(os.path.join(_cand, "jyotish_primitives.py")):
        sys.path.insert(0, _cand)
        break
import jyotish_primitives as jp  # noqa: E402
import transit_engine as te  # noqa: E402
import ephemeris as eph  # noqa: E402

DEFAULT_BODIES = ["Jupiter", "Saturn", "Rahu", "Ketu"]
VALID_BODIES = list(te.DEFAULT_STEP_DAYS)

# Order in which reference names are reported in conjoins / aspects.
REF_ORDER = ["AL", "UL", "dasha_rasi", "antardasha_rasi", "karakamsha",
             "atmakaraka"]
DOUBLE_TRANSIT_REFS = ["AL", "UL", "dasha_rasi", "karakamsha"]
ARGALA_REFS = ["AL", "dasha_rasi"]

# Argala house (from the reference sign) -> (type, obstructing Virodha house).
ARGALA_RULES = {2: ("primary", 12), 4: ("primary", 10), 11: ("primary", 3),
                5: ("secondary", 9)}

KARAKAMSHA_OVERLAY_NOTE = (
    "Placing a transit in D9 by its nakshatra pada (one pada = one navamsha) "
    "and comparing with Karakamsha is a lineage-specific practice, not "
    "Jaimini Sutra text; offered as a secondary signal only.")

NOTE = (
    "Chara Dasha sets the period; a slow transit occupying or aspecting the "
    "dasha Rasi / AL narrows it; transits never override an inactive Rasi. "
    "Aspects are Jaimini Rasi Drishti (sign to sign, mutual), not Parashari "
    "graha drishti. Argala here is a transit in the 2nd/4th/11th (primary) "
    "or 5th (secondary) from the reference; obstructed_by lists the natal "
    "planets in the Virodha sign (12th/10th/3rd/9th) — whether they "
    "outweigh the Argala is an interpretive call. double_transit is sampled "
    "at window start/mid/end only; use the Jupiter and Saturn sign_stays for "
    "exact overlap dates. reference.antardasha_rasi is the Antardasha running at "
    "window start; each annotation reads house_from_antardasha_rasi from the "
    "Antardasha running at that snapshot / stay entry (antardasha_rasi_used).")


# ====================================================================
# Baseline load + validation
# ====================================================================

def _die(msg):
    sys.stderr.write(f"ERROR: {msg}\n")
    sys.exit(1)


def _get(d, path, src):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            _die(f"--baseline {src} is missing required key "
                 f"{'.'.join(path)!r}. This script needs a "
                 "compute_jaimini_baseline.py output.")
        cur = cur[key]
    return cur


def load_baseline(path):
    try:
        with open(path) as fh:
            baseline = json.load(fh)
    except (OSError, ValueError) as exc:
        _die(f"cannot read --baseline {path}: {exc}")
    for path_ in (("chart_meta",), ("chara_karakas", "AK", "planet"),
                  ("chara_karakas", "AK", "sign"),
                  ("arudha_padas", "AL", "sign"), ("arudha_padas", "UL", "sign"),
                  ("karakamsha", "karakamsha_lagna_d1"),
                  ("chara_dasha",), ("planets",)):
        _get(baseline, path_, path)
    if baseline["chara_dasha"].get("running") is None:
        _die("baseline has no running Chara Dasha; rebuild it with "
             "--target-date (compute_jaimini_baseline.py --target-date "
             "<window start date>).")
    running = baseline["chara_dasha"]["running"]
    for k in ("rasi", "rasi_idx", "jaimini_lord", "start", "end"):
        if k not in running:
            _die(f"--baseline {path}: chara_dasha.running lacks {k!r}.")
    for pname, pinfo in baseline["planets"].items():
        if "sign" not in pinfo:
            _die(f"--baseline {path}: planets.{pname} lacks 'sign'.")
    return baseline


def _sign_ref(sign):
    if sign not in jp.SIGNS:
        _die(f"unknown sign {sign!r} in baseline")
    return {"sign": sign, "sign_idx": jp.SIGNS.index(sign)}


def resolve_antardasha(running, start_utc_iso):
    """The Antardasha of the running Mahadasha active at the window start, if
    the window start falls inside the Mahadasha; else the baseline's
    running_antardasha (computed at its --target-date). Also returns the
    Antardashas overlapping the window (filled in by the caller)."""
    for ad in running.get("antardasha") or []:
        if ad["start"] <= start_utc_iso < ad["end"]:
            return ad
    return running.get("running_antardasha")


def build_reference(baseline, start_utc_iso, end_utc_iso):
    ap_ = baseline["arudha_padas"]
    running = baseline["chara_dasha"]["running"]
    ak = baseline["chara_karakas"]["AK"]
    ref = {
        "AL": _sign_ref(ap_["AL"]["sign"]),
        "UL": _sign_ref(ap_["UL"]["sign"]),
        "dasha_rasi": {
            **_sign_ref(running["rasi"]),
            "lord": running["jaimini_lord"],
            "start": running["start"],
            "end": running["end"],
            "contains_window_start": running["start"] <= start_utc_iso < running["end"],
            "contains_window_end": running["start"] <= end_utc_iso < running["end"],
        },
        "antardasha_rasi": None,
        "antardashas_in_window": [],
        "karakamsha": _sign_ref(baseline["karakamsha"]["karakamsha_lagna_d1"]),
        "atmakaraka": {"planet": ak["planet"], **_sign_ref(ak["sign"])},
    }
    ad = resolve_antardasha(running, start_utc_iso)
    if ad is not None:
        ref["antardasha_rasi"] = {**_sign_ref(ad["rasi"]),
                                  "lord": ad.get("jaimini_lord"),
                                  "start": ad.get("start"),
                                  "end": ad.get("end")}
    for a in running.get("antardasha") or []:
        if a["start"] < end_utc_iso and a["end"] > start_utc_iso:
            ref["antardashas_in_window"].append(
                {"sign": a["rasi"], "sign_idx": a["rasi_idx"],
                 "lord": a.get("jaimini_lord"),
                 "start": a["start"], "end": a["end"]})
    by_sign = {}
    for sign in jp.SIGNS:
        occ = [p for p, info in baseline["planets"].items()
               if info["sign"] == sign]
        if occ:
            by_sign[sign] = occ
    ref["natal_planets_by_sign"] = by_sign
    return ref


# ====================================================================
# Annotation
# ====================================================================

def _ref_idx(reference):
    """{reference name: sign_idx} for every populated reference sign."""
    out = {}
    for name in REF_ORDER:
        r = reference.get(name)
        if r is not None:
            out[name] = r["sign_idx"]
    return out


def _natal_in(reference, sign_idx):
    return list(reference["natal_planets_by_sign"].get(jp.SIGNS[sign_idx], []))


def _lord_names(lord_str):
    return [s.strip() for s in str(lord_str).split("/") if s.strip()]


def argala_from(reference, ref_sign_idx, sign_idx):
    house = jp.count_signs(ref_sign_idx, sign_idx)
    rule = ARGALA_RULES.get(house)
    if rule is None:
        return {"type": None, "house": house, "obstructed_by": []}
    a_type, virodha_house = rule
    virodha_idx = jp.sign_n_from(ref_sign_idx, virodha_house)
    return {"type": a_type, "house": house,
            "virodha_house": virodha_house,
            "virodha_sign": jp.SIGNS[virodha_idx],
            "obstructed_by": _natal_in(reference, virodha_idx)}


def antardasha_at(reference, iso):
    """The in-window Antardasha active at `iso` (naive-UTC ISO string), else
    the window-start Antardasha (reference.antardasha_rasi)."""
    for ad in reference["antardashas_in_window"]:
        if ad["start"] <= iso < ad["end"]:
            return ad
    return reference["antardasha_rasi"]


def annotate(body, sign_idx, reference, matrix, at_iso):
    """Annotate a transit sign against every reference sign. `at_iso` picks
    the Antardasha Rasi running at that instant (a stay uses its in-window
    entry), so a stay that begins after an Antardasha change is read from the
    new Antardasha Rasi."""
    refs = _ref_idx(reference)
    ad = antardasha_at(reference, at_iso)
    if ad is None:
        refs.pop("antardasha_rasi", None)
    else:
        refs["antardasha_rasi"] = ad["sign_idx"]

    def house_from(name):
        return jp.count_signs(refs[name], sign_idx) if name in refs else None

    return {
        "house_from_AL": house_from("AL"),
        "house_from_UL": house_from("UL"),
        "house_from_dasha_rasi": house_from("dasha_rasi"),
        "house_from_antardasha_rasi": house_from("antardasha_rasi"),
        "antardasha_rasi_used": ad["sign"] if ad is not None else None,
        "conjoins": [n for n in REF_ORDER if n in refs and refs[n] == sign_idx],
        "aspects": [n for n in REF_ORDER
                    if n in refs and matrix[sign_idx][refs[n]] == 1],
        "argala": {n: argala_from(reference, refs[n], sign_idx)
                   for n in ARGALA_REFS},
        "is_dasha_rasi_lord":
            body in _lord_names(reference["dasha_rasi"]["lord"]),
        "natal_planets_in_sign": _natal_in(reference, sign_idx),
    }


def occupies_or_aspects(sign_idx, ref_idx, matrix):
    return sign_idx == ref_idx or matrix[sign_idx][ref_idx] == 1


def double_transit_at(dt_utc, reference, matrix, ayan_mode):
    jup = jp.get_sign(jp.norm360(te.lon_at("Jupiter", dt_utc, ayan_mode)))[0]
    sat = jp.get_sign(jp.norm360(te.lon_at("Saturn", dt_utc, ayan_mode)))[0]
    out = {"datetime_utc": dt_utc.isoformat(),
           "jupiter_sign": jp.SIGNS[jup], "saturn_sign": jp.SIGNS[sat]}
    for name in DOUBLE_TRANSIT_REFS:
        r = reference[name]["sign_idx"]
        out[f"on_{name}"] = (occupies_or_aspects(jup, r, matrix)
                             and occupies_or_aspects(sat, r, matrix))
    return out


# ====================================================================
# CLI
# ====================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Jaimini transit triggers — slow transits vs AL, UL, the "
                    "running Chara Dasha Rasi and Karakamsha by Rasi Drishti.")
    ap.add_argument("--baseline", required=True,
                    help="compute_jaimini_baseline.py JSON (built with "
                         "--target-date)")
    ap.add_argument("--datetime", help="window start, ISO local "
                                       "(alias for --start-datetime)")
    ap.add_argument("--start-datetime", help="window start, ISO local")
    ap.add_argument("--end-datetime", help="window end, ISO local "
                                           "(default: start + --window-days)")
    ap.add_argument("--window-days", type=float, default=365.0,
                    help="window length in days if --end-datetime omitted "
                         "(default 365)")
    ap.add_argument("--tz", required=True, help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--bodies", default=",".join(DEFAULT_BODIES),
                    help="comma-separated transiting bodies "
                         "(default Jupiter,Saturn,Rahu,Ketu)")
    ap.add_argument("--ayanamsa", choices=["lahiri", "kp"], default="lahiri",
                    help="sidereal ayanamsa (default lahiri)")
    ap.add_argument("--karakamsha-overlay", action="store_true",
                    help="add the lineage-specific pada->navamsha vs "
                         "Karakamsha layer")
    ap.add_argument("--step-days", type=float,
                    help="override the sampling step (days) for ALL bodies "
                         "(default: per-body, lib/transit_engine.DEFAULT_STEP_DAYS)")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args()

    start_iso = args.start_datetime or args.datetime
    if not start_iso:
        ap.error("need --start-datetime (or --datetime)")
    bodies = [b.strip() for b in args.bodies.split(",") if b.strip()]
    bad = [b for b in bodies if b not in VALID_BODIES]
    if bad or not bodies:
        ap.error(f"unknown --bodies {bad}; choose from {VALID_BODIES}")
    if args.step_days is not None and args.step_days <= 0:
        ap.error("--step-days must be > 0")

    start_local, start_utc = eph.to_utc(start_iso, args.tz)
    if args.end_datetime:
        end_local, end_utc = eph.to_utc(args.end_datetime, args.tz)
    else:
        end_utc = start_utc + timedelta(days=args.window_days)
        end_local = start_local + timedelta(days=args.window_days)
    if end_utc <= start_utc:
        ap.error("--end-datetime must be after the window start")
    mid_utc = start_utc + (end_utc - start_utc) / 2

    baseline = load_baseline(args.baseline)
    reference = build_reference(baseline, start_utc.isoformat(),
                                end_utc.isoformat())
    if not reference["dasha_rasi"]["contains_window_start"]:
        sys.stderr.write(
            "WARNING: window start lies outside the baseline's running Chara "
            f"Dasha ({reference['dasha_rasi']['start']} -> "
            f"{reference['dasha_rasi']['end']}); rebuild the baseline with "
            "--target-date at the window start for the correct dasha Rasi.\n")
    matrix = jp.jaimini_drishti_matrix()["matrix"]
    ayan = args.ayanamsa
    def lon_fn(body, dt_utc):
        return te.lon_at(body, dt_utc, ayan)
    instants = {"window_start": start_utc, "window_mid": mid_utc,
                "window_end": end_utc}

    out_bodies = {}
    for body in bodies:
        step = args.step_days or te.DEFAULT_STEP_DAYS[body]
        series = te.sample_series(body, start_utc, end_utc, step, lon_fn)

        positions = {}
        for key, t in instants.items():
            snap = te.snapshot(body, t, ayan)
            snap.update(annotate(body, snap["sign_idx"], reference, matrix,
                                 t.isoformat()))
            positions[key] = snap

        stays = []
        for span in te.sign_spans():
            stays.extend(te.find_hits(body, series, span, lon_fn))
        stays.sort(key=lambda h: h["entry_date"] or "")
        for h in stays:
            at = max(h["entry_date"] or start_utc.isoformat(),
                     start_utc.isoformat())
            h.update(annotate(body, h["sign_idx"], reference, matrix, at))

        overlay = None
        if args.karakamsha_overlay:
            kk = reference["karakamsha"]["sign_idx"]
            overlay = []
            for span in te.pada_spans():
                overlay.extend(te.find_hits(body, series, span, lon_fn))
            overlay.sort(key=lambda h: h["entry_date"] or "")
            for h in overlay:
                nav = h["navamsa_idx"]
                h["relation_to_karakamsha"] = (
                    "same" if nav == kk
                    else "aspects" if matrix[nav][kk] == 1 else None)
                h["layer"] = "lineage_specific"

        out_bodies[body] = {"sampling_step_days": step,
                            "positions": positions,
                            "sign_stays": stays,
                            "karakamsha_overlay": overlay}

    out = {
        "script": "compute_jaimini_transits.py",
        "school": "jaimini",
        "ayanamsa": {"mode": ayan},
        "window": {
            "start_local": start_local.isoformat(),
            "start_utc": start_utc.isoformat(),
            "mid_utc": mid_utc.isoformat(),
            "end_local": end_local.isoformat(),
            "end_utc": end_utc.isoformat(),
            "tz": args.tz,
        },
        "reference": reference,
        "bodies": out_bodies,
        "double_transit": {k: double_transit_at(t, reference, matrix, ayan)
                           for k, t in instants.items()},
        "note": NOTE,
    }
    if args.karakamsha_overlay:
        out["karakamsha_overlay_note"] = KARAKAMSHA_OVERLAY_NOTE

    text = json.dumps(out, indent=2, default=str)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
