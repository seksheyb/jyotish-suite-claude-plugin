#!/usr/bin/env python3
"""
KP Ruling Planets Computation
==============================
Computes the 7 Ruling Planets at a given moment + place.
Shows the full calculation breakdown for transparency.

Usage:
    python compute_ruling_planets.py \
      --datetime "2026-05-01T22:30:00" \
      --tz "Asia/Kolkata" \
      --lat 28.6139 \
      --lon 77.2090
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

try:
    import swisseph as swe
except ImportError:
    print("ERROR: pyswisseph not installed.")
    sys.exit(1)

try:
    import pytz
except ImportError:
    print("ERROR: pytz not installed.")
    sys.exit(1)


# Same constants as compute_horary_chart.py
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
NAKSHATRAS = [
    ("Ashwini", "Ketu"), ("Bharani", "Venus"), ("Krittika", "Sun"),
    ("Rohini", "Moon"), ("Mrigashira", "Mars"), ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"), ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"), ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"), ("Chitra", "Mars"), ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"), ("Anuradha", "Saturn"), ("Jyestha", "Mercury"),
    ("Mula", "Ketu"), ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"), ("Dhanishtha", "Mars"), ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]
VIM_SEQ = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
             "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
NAK_ARC = 360.0 / 27.0
TOTAL_VIM = 120

WEEKDAY_LORDS = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
                 4: "Venus", 5: "Saturn", 6: "Sun"}  # Python: Mon=0..Sun=6


def deg_to_dms(deg):
    d = int(deg); mf = (deg - d) * 60; m = int(mf); s = int((mf - m) * 60)
    return f"{d:03d}-{m:02d}-{s:02d}"

def get_sign(lon):
    lon = lon % 360
    idx = int(lon // 30)
    return idx, SIGNS[idx], SIGN_LORDS[idx]

def get_nakshatra(lon):
    lon = lon % 360
    idx = int(lon // NAK_ARC)
    return idx, NAKSHATRAS[idx][0], NAKSHATRAS[idx][1], idx * NAK_ARC

def get_sub_lord(lon):
    """Return sub_lord."""
    lon = lon % 360
    nak_idx, _name, star_lord, nak_start = get_nakshatra(lon)
    pos = lon - nak_start
    start_idx = VIM_SEQ.index(star_lord)
    cum = 0.0
    for off in range(9):
        lord = VIM_SEQ[(start_idx + off) % 9]
        arc = (VIM_YEARS[lord] / TOTAL_VIM) * NAK_ARC
        if cum <= pos < cum + arc:
            return lord
        cum += arc
    return VIM_SEQ[(start_idx + 8) % 9]


def get_sunrise_jd(jd_at_question, lat, lon):
    """Get sunrise JD for the day of the question (or previous day if before sunrise)."""
    # Sunrise on the day of the question
    flags = swe.CALC_RISE | swe.BIT_DISC_CENTER
    geopos = (lon, lat, 0)
    # Find sunrise on or before jd_at_question
    rsmi = swe.CALC_RISE
    # search starting from previous noon
    search_start = jd_at_question - 1.0
    res = swe.rise_trans(search_start, swe.SUN, rsmi, geopos)
    sunrise_jd = res[1][0]
    if sunrise_jd > jd_at_question:
        # already searched too far; search earlier
        res = swe.rise_trans(search_start - 1.0, swe.SUN, rsmi, geopos)
        sunrise_jd = res[1][0]
    return sunrise_jd


def get_day_lord(jd_at_question, lat, lon):
    """Day lord based on weekday at sunrise of the current Vedic day."""
    sunrise_jd = get_sunrise_jd(jd_at_question, lat, lon)
    # Convert sunrise_jd to UTC datetime, then to weekday
    y, m, d, ut = swe.revjul(sunrise_jd)
    # Build UTC datetime
    hr = int(ut); mn_full = (ut - hr) * 60; mn = int(mn_full); sc = int((mn_full - mn) * 60)
    sunrise_utc = datetime(y, m, d, hr, mn, sc)
    weekday = sunrise_utc.weekday()  # Mon=0..Sun=6
    return WEEKDAY_LORDS[weekday], sunrise_utc


def compute_position(jd, planet_swe_id, ayanamsa, is_ketu=False):
    """Return sidereal longitude + retrograde flag."""
    if is_ketu:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        sidereal = (pos[0] + 180 - ayanamsa) % 360
        return sidereal, False  # nodes
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    pos, _ = swe.calc_ut(jd, planet_swe_id, flags)
    sidereal = (pos[0] - ayanamsa) % 360
    retro = pos[3] < 0
    return sidereal, retro


def compute_ascendant(jd, lat, lon, ayanamsa):
    """Compute sidereal ascendant at moment+place."""
    cusps_trop, ascmc = swe.houses(jd, lat, lon, b'P')
    return (ascmc[0] - ayanamsa) % 360


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datetime", required=True)
    parser.add_argument("--tz", required=True)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    args = parser.parse_args()

    local_tz = pytz.timezone(args.tz)
    dt_local = local_tz.localize(datetime.fromisoformat(args.datetime))
    dt_utc = dt_local.astimezone(pytz.UTC).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)

    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Day Lord
    day_lord, sunrise_utc = get_day_lord(jd, args.lat, args.lon)

    # Moon position
    moon_lon, _retro = compute_position(jd, swe.MOON, ayanamsa)
    moon_si, moon_sign, moon_sign_lord = get_sign(moon_lon)
    _ni, moon_nak, moon_star_lord, _ns = get_nakshatra(moon_lon)
    moon_sub_lord = get_sub_lord(moon_lon)

    # Lagna position
    asc_lon = compute_ascendant(jd, args.lat, args.lon, ayanamsa)
    asc_si, asc_sign, asc_sign_lord = get_sign(asc_lon)
    _ni, asc_nak, asc_star_lord, _ns = get_nakshatra(asc_lon)
    asc_sub_lord = get_sub_lord(asc_lon)

    # Build RP set in strength order
    rp_factors = [
        ("Lagna Sub Lord", asc_sub_lord),
        ("Lagna Star Lord", asc_star_lord),
        ("Lagna Sign Lord", asc_sign_lord),
        ("Moon Sub Lord", moon_sub_lord),
        ("Moon Star Lord", moon_star_lord),
        ("Moon Sign Lord", moon_sign_lord),
        ("Day Lord", day_lord),
    ]

    # Deduplicate while preserving order (strongest first)
    seen = set()
    rp_dedup = []
    for role, planet in rp_factors:
        if planet not in seen:
            rp_dedup.append(planet)
            seen.add(planet)

    # Check retrograde exclusions for the RP set
    retrograde_check = {}
    SWE_MAP = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
               "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN}
    for planet in rp_dedup:
        if planet in ("Rahu", "Ketu"):
            retrograde_check[planet] = "Always treated as Rahu/Ketu rule (see below)"
            continue
        is_ketu = (planet == "Ketu")
        sid_lon, retro = compute_position(jd, SWE_MAP.get(planet), ayanamsa, is_ketu=is_ketu)
        retrograde_check[planet] = "RETROGRADE" if retro else "Direct"

    # Rahu/Ketu rule check
    flags_speed = swe.FLG_SWIEPH | swe.FLG_SPEED
    rahu_pos_calc, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags_speed)
    rahu_sid = (rahu_pos_calc[0] - ayanamsa) % 360
    ketu_sid = (rahu_sid + 180) % 360
    _, rahu_sign, rahu_sign_lord = get_sign(rahu_sid)
    _, ketu_sign, ketu_sign_lord = get_sign(ketu_sid)
    rahu_added = rahu_sign_lord in rp_dedup
    ketu_added = ketu_sign_lord in rp_dedup

    final_rp = list(rp_dedup)
    if rahu_added and "Rahu" not in final_rp:
        final_rp.append("Rahu")
    if ketu_added and "Ketu" not in final_rp:
        final_rp.append("Ketu")

    output = {
        "input": {
            "datetime_local": dt_local.isoformat(),
            "datetime_utc": dt_utc.isoformat(),
            "timezone": args.tz,
            "latitude": args.lat,
            "longitude": args.lon,
        },
        "ayanamsa_dms": deg_to_dms(ayanamsa),
        "day_lord": {
            "weekday_at_sunrise": sunrise_utc.strftime("%A"),
            "sunrise_utc": sunrise_utc.isoformat(),
            "lord": day_lord,
        },
        "moon": {
            "longitude_dms": deg_to_dms(moon_lon),
            "sign": moon_sign, "sign_lord": moon_sign_lord,
            "nakshatra": moon_nak, "star_lord": moon_star_lord,
            "sub_lord": moon_sub_lord,
        },
        "lagna": {
            "longitude_dms": deg_to_dms(asc_lon),
            "sign": asc_sign, "sign_lord": asc_sign_lord,
            "nakshatra": asc_nak, "star_lord": asc_star_lord,
            "sub_lord": asc_sub_lord,
        },
        "rp_factors_in_strength_order": rp_factors,
        "rp_deduplicated": rp_dedup,
        "retrograde_check": retrograde_check,
        "rahu_check": {
            "rahu_in_sign": rahu_sign,
            "rahu_sign_lord": rahu_sign_lord,
            "rahu_added_to_rp": rahu_added,
        },
        "ketu_check": {
            "ketu_in_sign": ketu_sign,
            "ketu_sign_lord": ketu_sign_lord,
            "ketu_added_to_rp": ketu_added,
        },
        "final_rp": final_rp,
        "strongest_rp": asc_sub_lord,
    }

    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
