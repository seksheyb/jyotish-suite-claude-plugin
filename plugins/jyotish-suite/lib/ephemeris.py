#!/usr/bin/env python3
"""
Ephemeris layer — the ONLY consumer of pyswisseph / pytz in the suite.

Exposes raw primitives (julian_day, ayanamsa, planet_position, house_cusps,
ascendant, sunrise_jd, day_lord) plus the three chart-mode assemblers the
`chart-calculator` agent dispatches:

    parashari_natal_chart()  — Lahiri, Whole-Sign, D1 + D9   (vedic/bnn/jaimini, lal-kitab D1)
    kp_natal_chart()         — KP-New, Placidus, sub-lord chains
    kp_horary_chart()        — KP-New, Placidus rotated to a 1-249 number Lagna

These three are genuinely different methods — different ayanamsa, house system,
ascendant source and reference time — and must never be collapsed.

Requires: pyswisseph, pytz.
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jyotish_primitives as jp  # noqa: E402

try:
    import swisseph as swe
except ImportError:
    sys.stderr.write("ERROR: pyswisseph not installed. "
                     "Run: pip install pyswisseph --break-system-packages\n")
    raise

try:
    import pytz
except ImportError:
    sys.stderr.write("ERROR: pytz not installed. "
                     "Run: pip install pytz --break-system-packages\n")
    raise


SWE_PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}

AYANAMSA_MODES = {"lahiri": swe.SIDM_LAHIRI, "kp": swe.SIDM_KRISHNAMURTI}
HOUSE_SYSTEMS = {"whole-sign": b"W", "placidus": b"P", "equal": b"E"}


# ====================================================================
# Time + raw ephemeris primitives
# ====================================================================

def to_utc(dt_iso, tz_name):
    """Localise an ISO datetime string in tz_name and return a naive UTC datetime."""
    tz = pytz.timezone(tz_name)
    local = tz.localize(datetime.fromisoformat(dt_iso))
    return local, local.astimezone(pytz.UTC).replace(tzinfo=None)


def julian_day(dt_utc):
    """Naive UTC datetime -> Julian Day (UT)."""
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def ayanamsa(jd, mode="lahiri"):
    """Return the ayanamsa in degrees for a Julian Day. mode = 'lahiri' | 'kp'."""
    swe.set_sid_mode(AYANAMSA_MODES[mode])
    return swe.get_ayanamsa_ut(jd)


def planet_position(jd, planet, ayan):
    """Return (sidereal_longitude, retrograde_bool, speed) for a planet."""
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if planet == "Ketu":
        pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        return jp.norm360(pos[0] + 180 - ayan), False, -pos[3]
    pos, _ = swe.calc_ut(jd, SWE_PLANETS[planet], flags)
    sidereal = jp.norm360(pos[0] - ayan)
    if planet == "Rahu":
        return sidereal, False, pos[3]
    return sidereal, pos[3] < 0, pos[3]


def ascendant(jd, lat, lon, ayan):
    """Sidereal ascendant longitude (independent of house system)."""
    _cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    return jp.norm360(ascmc[0] - ayan)


def house_cusps(jd, lat, lon, ayan, system="placidus"):
    """Return 12 sidereal house-cusp longitudes for the given house system."""
    cusps, _ascmc = swe.houses(jd, lat, lon, HOUSE_SYSTEMS[system])
    return [jp.norm360(cusps[i] - ayan) for i in range(12)]


def sunrise_jd(jd_ref, lat, lon):
    """Julian Day of the sunrise that opens the Vedic day containing jd_ref."""
    geopos = (lon, lat, 0)
    res = swe.rise_trans(jd_ref - 1.0, swe.SUN, swe.CALC_RISE, geopos)
    sr = res[1][0]
    if sr > jd_ref:
        res = swe.rise_trans(jd_ref - 2.0, swe.SUN, swe.CALC_RISE, geopos)
        sr = res[1][0]
    return sr


def day_lord(jd_ref, lat, lon):
    """Vedic day-lord (weekday planet at the opening sunrise)."""
    sr = sunrise_jd(jd_ref, lat, lon)
    y, m, d, ut = swe.revjul(sr)
    hr = int(ut)
    mn = int((ut - hr) * 60)
    sc = int((((ut - hr) * 60) - mn) * 60)
    sr_dt = datetime(y, m, d, hr, mn, sc)
    return jp.WEEKDAY_LORDS[sr_dt.weekday()], sr_dt


# ====================================================================
# 249 horary number -> Lagna
# ====================================================================

def horary_number_to_lagna(number):
    """Map a horary number 1-249 to the sidereal mid-degree of its 249-segment.
    Returns (longitude, info_dict)."""
    if not 1 <= number <= 249:
        raise ValueError(f"Horary number must be 1-249, got {number}")
    count = 0
    for nak_idx, (nak_name, star_lord) in enumerate(jp.NAKSHATRAS):
        nak_start = nak_idx * jp.NAK_ARC
        start_idx = jp.VIM_SEQ.index(star_lord)
        cum = 0.0
        for off in range(9):
            lord = jp.VIM_SEQ[(start_idx + off) % 9]
            arc = (jp.VIM_YEARS[lord] / jp.TOTAL_VIM) * jp.NAK_ARC
            count += 1
            if count == number:
                mid = nak_start + cum + arc / 2
                return mid, {"number": number, "nakshatra": nak_name,
                             "star_lord": star_lord, "sub_lord": lord,
                             "segment_start": round(nak_start + cum, 4),
                             "segment_end": round(nak_start + cum + arc, 4),
                             "lagna_deg": round(mid, 4)}
            cum += arc
    raise ValueError(f"Could not map horary number {number}")


# ====================================================================
# Shared assembly helpers
# ====================================================================

ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
               "Saturn", "Rahu", "Ketu"]


def _planet_block(jd, ayan):
    """Compute every planet's sidereal longitude + retrograde flag."""
    out = {}
    for p in ALL_PLANETS:
        lon, retro, _spd = planet_position(jd, p, ayan)
        out[p] = {"longitude": round(lon, 4), "retrograde": retro}
    return out


def _vim_dasha(moon_lon, ref_dt_utc, n_md=5):
    """Vimshottari running quartet + tree summary from a Moon longitude."""
    tree = jp.build_dasha_tree(moon_lon, ref_dt_utc, n_md=n_md)
    md_lord, balance, _elapsed = jp.vimshottari_balance(moon_lon)
    return {
        "starting_mahadasha": md_lord,
        "balance_years": round(balance, 3),
        "running": jp.find_running(tree, ref_dt_utc),
        "mahadasha_sequence": [{"md_lord": md["md_lord"], "start": md["start"],
                                "end": md["end"]} for md in tree],
        "tree": tree,
    }


# ====================================================================
# Chart assemblers — build the chart dict from longitudes already known.
# Used both by the ephemeris path (longitudes from swisseph) and by
# lib/chart_io.py (longitudes from a user-supplied positions chart), so the
# computed-chart and pasted-chart paths converge on one dict shape.
# ====================================================================

def assemble_parashari(asc_lon, planets_raw, dasha, meta):
    """Build the parashari_natal_chart dict from known longitudes.
    planets_raw: {planet: {"longitude": float, "retrograde": bool}}."""
    asc_lon = jp.norm360(asc_lon)
    asc_si, asc_sign, _ = jp.get_sign(asc_lon)
    planets = {}
    for p, info in planets_raw.items():
        plon = jp.norm360(info["longitude"])
        si, sign, sign_lord = jp.get_sign(plon)
        _ni, nak, star_lord, _ns = jp.get_nakshatra(plon)
        _d9i, d9sign = jp.navamsa_sign(plon)
        planets[p] = {
            "longitude": round(plon, 4),
            "longitude_dms": jp.deg_to_dms(plon),
            "sign": sign,
            "deg_in_sign": round(jp.deg_in_sign(plon), 4),
            "sign_lord": sign_lord,
            "nakshatra": nak,
            "pada": jp.get_pada(plon),
            "star_lord": star_lord,
            "retrograde": info.get("retrograde", False),
            "house": jp.house_of(si, asc_si),
            "navamsa_sign": d9sign,
            "dignity": jp.dignity(p, plon),
        }
    return {
        "chart_type": "parashari_natal",
        "ayanamsa": meta.get("ayanamsa", {"mode": "lahiri"}),
        "house_system": "Whole-Sign",
        "datetime_local": meta.get("datetime_local"),
        "datetime_utc": meta.get("datetime_utc"),
        "location": meta.get("location"),
        "d1": {"lagna_sign": asc_sign,
               "lagna_longitude_dms": jp.deg_to_dms(asc_lon),
               "lagna_nakshatra": jp.get_nakshatra(asc_lon)[1],
               "planets": planets},
        "d9": {"lagna_sign": jp.navamsa_sign(asc_lon)[1],
               "planets": {p: planets[p]["navamsa_sign"] for p in planets}},
        "dasha": dasha,
    }


def assemble_kp(cusp_lons, planets_raw, dasha, meta):
    """Build the kp_natal_chart dict from 12 cusp longitudes + planet longitudes."""
    cusps = []
    for i, clon in enumerate(cusp_lons, start=1):
        chain = jp.full_lord_chain(jp.norm360(clon))
        chain["cusp"] = i
        cusps.append(chain)
    planets = {}
    for p, info in planets_raw.items():
        chain = jp.full_lord_chain(jp.norm360(info["longitude"]))
        chain["planet"] = p
        chain["retrograde"] = info.get("retrograde", False)
        planets[p] = chain
    return {
        "chart_type": "kp_natal",
        "ayanamsa": meta.get("ayanamsa", {"mode": "kp"}),
        "house_system": "Placidus",
        "datetime_local": meta.get("datetime_local"),
        "datetime_utc": meta.get("datetime_utc"),
        "location": meta.get("location"),
        "cusps": cusps,
        "planets": planets,
        "dasha": dasha,
    }


# ====================================================================
# Chart-mode assemblers (ephemeris path)
# ====================================================================

def parashari_natal_chart(dt_iso, tz_name, lat, lon, ayanamsa_mode="lahiri"):
    """D1 + D9 natal chart — Lahiri, Whole-Sign houses.
    Used by vedic-astro, bnn-astrology, jaimini-astrology, and lal-kitab (D1)."""
    local, utc = to_utc(dt_iso, tz_name)
    jd = julian_day(utc)
    ayan = ayanamsa(jd, ayanamsa_mode)
    asc_lon = ascendant(jd, lat, lon, ayan)
    raw = _planet_block(jd, ayan)
    meta = {
        "ayanamsa": {"mode": ayanamsa_mode, "value_dms": jp.deg_to_dms(ayan)},
        "datetime_local": local.isoformat(),
        "datetime_utc": utc.isoformat(),
        "location": {"lat": lat, "lon": lon, "tz": tz_name},
    }
    return assemble_parashari(asc_lon, raw,
                              _vim_dasha(raw["Moon"]["longitude"], utc), meta)


def kp_natal_chart(dt_iso, tz_name, lat, lon):
    """KP natal chart — KP-New ayanamsa, Placidus cusps, full sub-lord chains."""
    local, utc = to_utc(dt_iso, tz_name)
    jd = julian_day(utc)
    ayan = ayanamsa(jd, "kp")
    raw = _planet_block(jd, ayan)
    meta = {
        "ayanamsa": {"mode": "kp", "value_dms": jp.deg_to_dms(ayan)},
        "datetime_local": local.isoformat(),
        "datetime_utc": utc.isoformat(),
        "location": {"lat": lat, "lon": lon, "tz": tz_name},
    }
    return assemble_kp(house_cusps(jd, lat, lon, ayan, "placidus"), raw,
                       _vim_dasha(raw["Moon"]["longitude"], utc), meta)


def kp_horary_chart(number, dt_iso, tz_name, lat, lon):
    """KP horary chart — Lagna from a 1-249 number, Placidus cusps rotated to it,
    planets + dasha at the moment of the question. Computes BOTH the
    number-derived chart Lagna and the real rising Lagna (for Ruling Planets)."""
    local, utc = to_utc(dt_iso, tz_name)
    jd = julian_day(utc)
    ayan = ayanamsa(jd, "kp")

    horary_lagna, lagna_info = horary_number_to_lagna(number)
    real_asc = ascendant(jd, lat, lon, ayan)

    # Placidus cusps for moment+place, rotated so cusp 1 == horary Lagna.
    raw_cusps = house_cusps(jd, lat, lon, ayan, "placidus")
    offset = jp.norm360(horary_lagna - raw_cusps[0])
    cusps = []
    for i in range(12):
        clon = horary_lagna if i == 0 else jp.norm360(raw_cusps[i] + offset)
        chain = jp.full_lord_chain(clon)
        chain["cusp"] = i + 1
        cusps.append(chain)

    planets = {}
    raw = _planet_block(jd, ayan)
    for p, info in raw.items():
        chain = jp.full_lord_chain(info["longitude"])
        chain["planet"] = p
        chain["retrograde"] = info["retrograde"]
        planets[p] = chain

    return {
        "chart_type": "kp_horary",
        "ayanamsa": {"mode": "kp", "value_dms": jp.deg_to_dms(ayan)},
        "house_system": "Placidus (rotated to horary Lagna)",
        "datetime_local": local.isoformat(),
        "datetime_utc": utc.isoformat(),
        "location": {"lat": lat, "lon": lon, "tz": tz_name},
        "horary_lagna": lagna_info,
        "ruling_planets_lagna": jp.full_lord_chain(real_asc),
        "cusps": cusps,
        "planets": planets,
        "dasha": _vim_dasha(raw["Moon"]["longitude"], utc),
    }


# ====================================================================
# CLI — used by the chart-calculator agent to produce a standalone chart
# ====================================================================

def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Jyotish chart calculator (3 modes)")
    ap.add_argument("--mode", required=True,
                    choices=["parashari", "kp-natal", "kp-horary"])
    ap.add_argument("--datetime", required=True, help="ISO datetime")
    ap.add_argument("--tz", required=True, help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--number", type=int, help="Horary number 1-249 (kp-horary mode)")
    args = ap.parse_args()

    if args.mode == "parashari":
        chart = parashari_natal_chart(args.datetime, args.tz, args.lat, args.lon)
    elif args.mode == "kp-natal":
        chart = kp_natal_chart(args.datetime, args.tz, args.lat, args.lon)
    else:
        if args.number is None:
            ap.error("--number is required for kp-horary mode")
        chart = kp_horary_chart(args.number, args.datetime, args.tz,
                                args.lat, args.lon)
    print(json.dumps(chart, indent=2, default=str))


if __name__ == "__main__":
    main()
