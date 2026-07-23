#!/usr/bin/env python3
"""
Chart I/O — turn a user-supplied (pre-computed) chart into the full chart JSON
that the baseline scripts consume.

When a user pastes their own chart instead of giving birth data, the
`chart-verifier` agent extracts a SIMPLE positions form (each body's sign +
degree-in-sign) and runs this module to expand it into the same dict shape
`ephemeris.py` produces. The pasted-chart path and the computed-chart path then
converge on one format, and `compute_*_baseline.py --chart <file>` works for
both.

No ephemeris is needed here — the user already supplied the positions; lib/
derives everything else (nakshatra, navamsa, dignity, degree flags, lord
chains) deterministically.

Simple positions form (JSON):
{
  "lagna":   {"sign": "Virgo", "deg": 12.5},
  "planets": {"Sun": {"sign": "Cancer", "deg": 13.2, "retrograde": false},
              "Moon": {...}, ... all 9 ...},
  "cusps":   {"1": {"sign": "Virgo", "deg": 12.5}, ... "12": {...}},  # KP only
  "birth":   {"datetime": "1991-07-30T10:20:00", "tz": "Asia/Kolkata",
              "lat": 28.6, "lon": 77.2},   # optional — enables Vimshottari dasha
  "dasha":   { ... }                       # optional passthrough if no birth data
}
`deg` is degrees-within-sign (0-30, decimal). Convert any DMS before writing.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402


def _abs_longitude(entry):
    """A {sign, deg} entry -> absolute sidereal longitude (0-360)."""
    sign = str(entry["sign"]).strip().capitalize()
    if sign not in jp.SIGNS:
        raise ValueError(f"Unknown sign {entry['sign']!r} — expected one of {jp.SIGNS}")
    deg = float(entry["deg"])
    if not 0 <= deg < 30:
        raise ValueError(f"deg must be 0-30 within the sign, got {deg}")
    return jp.SIGNS.index(sign) * 30.0 + deg


def _planets_raw(simple):
    """Convert the simple planets block to {planet: {longitude, retrograde}}."""
    out = {}
    for p, e in simple["planets"].items():
        out[p.strip().capitalize()] = {
            "longitude": _abs_longitude(e),
            "retrograde": bool(e.get("retrograde", False)),
        }
    missing = [p for p in jp.PLANETS if p not in out]
    if missing:
        raise ValueError(f"Chart is missing planet(s): {missing}")
    return out


def _dasha_for(simple, moon_lon):
    """Build a dasha block: compute from birth datetime if supplied, otherwise
    pass through a user-stated dasha, otherwise mark it unavailable."""
    birth = simple.get("birth")
    if birth:
        _local, utc = eph.to_utc(birth["datetime"], birth["tz"])
        return eph._vim_dasha(moon_lon, utc)
    if simple.get("dasha"):
        return {"source": "user-supplied", **simple["dasha"]}
    return {"source": "unavailable",
            "note": "No birth datetime and no dasha supplied — "
                    "Vimshottari timing omitted from this reading."}


def _meta_for(simple):
    """Build the chart `meta` block. When a birth block is supplied it carries
    the location + datetime through, so downstream scripts that need a location
    (KP Ruling Planets) find it on a pasted chart."""
    meta = {"ayanamsa": {"mode": "user-supplied"}}
    birth = simple.get("birth")
    if birth:
        local, utc = eph.to_utc(birth["datetime"], birth["tz"])
        meta["datetime_local"] = local.isoformat()
        meta["datetime_utc"] = utc.isoformat()
        meta["location"] = {"lat": birth.get("lat"), "lon": birth.get("lon"),
                            "tz": birth["tz"]}
    return meta


def parashari_from_positions(simple):
    """Expand a simple positions chart into a parashari_natal_chart dict
    (vedic-astro, bnn, jaimini, lal-kitab)."""
    asc_lon = _abs_longitude(simple["lagna"])
    raw = _planets_raw(simple)
    dasha = _dasha_for(simple, raw["Moon"]["longitude"])
    return eph.assemble_parashari(asc_lon, raw, dasha, _meta_for(simple))


def kp_from_positions(simple):
    """Expand a simple positions chart into a kp_natal_chart dict (kp-natal)."""
    if "cusps" not in simple:
        raise ValueError("A KP chart needs a 'cusps' block — 12 cusp positions "
                         "(sign + degree). KP houses are Placidus, not signs.")
    cusp_lons = [_abs_longitude(simple["cusps"][str(i)]) for i in range(1, 13)]
    raw = _planets_raw(simple)
    dasha = _dasha_for(simple, raw["Moon"]["longitude"])
    return eph.assemble_kp(cusp_lons, raw, dasha, _meta_for(simple))


def main():
    ap = argparse.ArgumentParser(
        description="Expand a user-supplied positions chart into a full chart JSON")
    ap.add_argument("--mode", required=True, choices=["parashari", "kp"],
                    help="parashari for vedic/bnn/jaimini/lal-kitab; kp for kp-natal")
    ap.add_argument("--positions", required=True,
                    help="path to the simple positions JSON")
    ap.add_argument("--out", help="write the full chart JSON here (else stdout)")
    args = ap.parse_args()

    with open(args.positions) as fh:
        simple = json.load(fh)
    chart = (parashari_from_positions(simple) if args.mode == "parashari"
             else kp_from_positions(simple))
    text = json.dumps(chart, indent=2, default=str)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
        print(f"Wrote {args.mode} chart -> {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
