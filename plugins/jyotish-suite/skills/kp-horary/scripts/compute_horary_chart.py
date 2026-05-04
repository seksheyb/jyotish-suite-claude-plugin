#!/usr/bin/env python3
"""
KP Horary Chart Computation
============================
Given:
  - Horary number (1-249)
  - Date and time of question (with timezone)
  - Latitude and longitude of questioner
Computes:
  - Horary Lagna (from 1-249 number)
  - Placidus house cusps with full lord chain (sign/star/sub/sub-sub)
  - Planetary positions with full lord chain
  - Vimshottari dasha at moment of question
  - Outputs everything as structured JSON + markdown table

Usage:
    python compute_horary_chart.py \
      --number 142 \
      --datetime "2026-05-01T22:30:00" \
      --tz "Asia/Kolkata" \
      --lat 28.6139 \
      --lon 77.2090 \
      --question "Will the deal close before Diwali?"

Requires: swisseph (pip install pyswisseph), pytz
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

try:
    import swisseph as swe
except ImportError:
    print("ERROR: pyswisseph not installed. Run: pip install pyswisseph --break-system-packages")
    sys.exit(1)

try:
    import pytz
except ImportError:
    print("ERROR: pytz not installed. Run: pip install pytz --break-system-packages")
    sys.exit(1)


# === Constants ===

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# Vimshottari order — the sequence of nakshatra star-lords across the zodiac
NAKSHATRAS = [
    ("Ashwini", "Ketu", 7),         ("Bharani", "Venus", 20),       ("Krittika", "Sun", 6),
    ("Rohini", "Moon", 10),         ("Mrigashira", "Mars", 7),      ("Ardra", "Rahu", 18),
    ("Punarvasu", "Jupiter", 16),   ("Pushya", "Saturn", 19),       ("Ashlesha", "Mercury", 17),
    ("Magha", "Ketu", 7),           ("Purva Phalguni", "Venus", 20),("Uttara Phalguni", "Sun", 6),
    ("Hasta", "Moon", 10),          ("Chitra", "Mars", 7),          ("Swati", "Rahu", 18),
    ("Vishakha", "Jupiter", 16),    ("Anuradha", "Saturn", 19),     ("Jyestha", "Mercury", 17),
    ("Mula", "Ketu", 7),            ("Purva Ashadha", "Venus", 20), ("Uttara Ashadha", "Sun", 6),
    ("Shravana", "Moon", 10),       ("Dhanishtha", "Mars", 7),      ("Shatabhisha", "Rahu", 18),
    ("Purva Bhadrapada", "Jupiter", 16), ("Uttara Bhadrapada", "Saturn", 19), ("Revati", "Mercury", 17),
]

# Vimshottari dasha sequence (start anywhere, then follow this order)
VIMSHOTTARI_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
                     "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

NAKSHATRA_ARC = 360.0 / 27.0  # 13°20'
TOTAL_VIM_YEARS = 120

# Swiss Ephemeris planet IDs
SWE_PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE, "Ketu": None,  # Ketu = Rahu + 180
    "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
}


# === Core helpers ===

def deg_to_dms(deg: float) -> str:
    """Convert decimal degrees to deg-min-sec string."""
    d = int(deg)
    m_full = (deg - d) * 60
    m = int(m_full)
    s = int((m_full - m) * 60)
    return f"{d:03d}-{m:02d}-{s:02d}"


def get_sign(longitude: float) -> Tuple[int, str, str]:
    """Return (sign_index, sign_name, sign_lord) for a sidereal longitude."""
    longitude = longitude % 360
    sign_idx = int(longitude // 30)
    return sign_idx, SIGNS[sign_idx], SIGN_LORDS[sign_idx]


def get_nakshatra(longitude: float) -> Tuple[int, str, str, float, float]:
    """Return (nak_index, nak_name, star_lord, nak_start_deg, nak_end_deg)."""
    longitude = longitude % 360
    nak_idx = int(longitude // NAKSHATRA_ARC)
    name, lord, _years = NAKSHATRAS[nak_idx]
    start = nak_idx * NAKSHATRA_ARC
    end = start + NAKSHATRA_ARC
    return nak_idx, name, lord, start, end


def get_sub_and_subsub(longitude: float) -> Tuple[str, str]:
    """
    Compute sub-lord and sub-sub-lord for a sidereal longitude.
    Returns (sub_lord, sub_sub_lord).
    """
    longitude = longitude % 360
    nak_idx, _name, star_lord, nak_start, _nak_end = get_nakshatra(longitude)
    pos_in_nak = longitude - nak_start  # 0 to 13°20'

    # Build sub divisions starting from star_lord
    start_idx = VIMSHOTTARI_SEQUENCE.index(star_lord)
    cum = 0.0
    sub_lord = None
    sub_start = 0.0
    sub_arc = 0.0
    for offset in range(9):
        lord = VIMSHOTTARI_SEQUENCE[(start_idx + offset) % 9]
        years = VIMSHOTTARI_YEARS[lord]
        arc = (years / TOTAL_VIM_YEARS) * NAKSHATRA_ARC
        if cum <= pos_in_nak < cum + arc:
            sub_lord = lord
            sub_start = cum
            sub_arc = arc
            break
        cum += arc
    if sub_lord is None:
        sub_lord = VIMSHOTTARI_SEQUENCE[(start_idx + 8) % 9]  # last sub
        sub_start = NAKSHATRA_ARC - (VIMSHOTTARI_YEARS[sub_lord] / TOTAL_VIM_YEARS) * NAKSHATRA_ARC
        sub_arc = NAKSHATRA_ARC - sub_start

    # Now sub-sub within the sub
    pos_in_sub = pos_in_nak - sub_start
    sub_lord_idx = VIMSHOTTARI_SEQUENCE.index(sub_lord)
    cum2 = 0.0
    subsub_lord = None
    for offset in range(9):
        lord = VIMSHOTTARI_SEQUENCE[(sub_lord_idx + offset) % 9]
        years = VIMSHOTTARI_YEARS[lord]
        arc2 = (years / TOTAL_VIM_YEARS) * sub_arc
        if cum2 <= pos_in_sub < cum2 + arc2:
            subsub_lord = lord
            break
        cum2 += arc2
    if subsub_lord is None:
        subsub_lord = VIMSHOTTARI_SEQUENCE[(sub_lord_idx + 8) % 9]

    return sub_lord, subsub_lord


def full_lord_chain(longitude: float) -> Dict[str, str]:
    """Return all four lord levels for a sidereal longitude."""
    _si, sign, sign_lord = get_sign(longitude)
    _ni, nak, star_lord, _ns, _ne = get_nakshatra(longitude)
    sub_lord, subsub_lord = get_sub_and_subsub(longitude)
    return {
        "longitude": longitude,
        "longitude_dms": deg_to_dms(longitude),
        "sign": sign,
        "sign_lord": sign_lord,
        "nakshatra": nak,
        "star_lord": star_lord,
        "sub_lord": sub_lord,
        "sub_sub_lord": subsub_lord,
    }


# === 249-number to Lagna degree ===

def horary_number_to_lagna_degree(number: int) -> Tuple[float, Dict]:
    """
    Map horary number 1-249 to a sidereal Lagna degree (mid-point of that segment).
    Returns (longitude, info_dict).
    """
    if not (1 <= number <= 249):
        raise ValueError(f"Horary number must be 1-249, got {number}")

    # Walk through all 249 segments in order, return mid-point of segment N.
    count = 0
    for nak_idx, (nak_name, star_lord, _yrs) in enumerate(NAKSHATRAS):
        nak_start = nak_idx * NAKSHATRA_ARC
        start_idx = VIMSHOTTARI_SEQUENCE.index(star_lord)
        cum = 0.0
        for offset in range(9):
            lord = VIMSHOTTARI_SEQUENCE[(start_idx + offset) % 9]
            years = VIMSHOTTARI_YEARS[lord]
            arc = (years / TOTAL_VIM_YEARS) * NAKSHATRA_ARC
            count += 1
            if count == number:
                mid_in_nak = cum + arc / 2
                lagna_deg = nak_start + mid_in_nak
                return lagna_deg, {
                    "number": number,
                    "nakshatra": nak_name,
                    "star_lord": star_lord,
                    "sub_lord": lord,
                    "segment_start": nak_start + cum,
                    "segment_end": nak_start + cum + arc,
                    "segment_mid": lagna_deg,
                }
            cum += arc

    raise ValueError(f"Could not map number {number}")


# === Swiss Ephemeris setup ===

def get_julian_day(dt_utc: datetime) -> float:
    """Convert UTC datetime to Julian Day."""
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def get_kp_ayanamsa(jd: float) -> float:
    """Get KP New ayanamsa for given Julian Day."""
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)  # KP New
    return swe.get_ayanamsa_ut(jd)


def compute_planet(jd: float, planet_name: str, ayanamsa: float) -> Dict:
    """Compute sidereal longitude + retrograde flag for a planet."""
    if planet_name == "Ketu":
        # Ketu = Rahu + 180
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        rahu_pos, _ret = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        trop_lon = (rahu_pos[0] + 180) % 360
        speed = -rahu_pos[3]  # Ketu opposite Rahu
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        pos, _ret = swe.calc_ut(jd, SWE_PLANETS[planet_name], flags)
        trop_lon = pos[0]
        speed = pos[3]

    sidereal = (trop_lon - ayanamsa) % 360
    chain = full_lord_chain(sidereal)
    chain["planet"] = planet_name
    chain["retrograde"] = speed < 0 and planet_name not in ["Rahu", "Ketu"]
    chain["nodes_always_retrograde"] = planet_name in ["Rahu", "Ketu"]
    return chain


def compute_house_cusps(jd: float, lat: float, lon: float, ayanamsa: float,
                       horary_lagna_sidereal: float = None) -> List[Dict]:
    """
    Compute Placidus house cusps.
    For horary chart: pass horary_lagna_sidereal — we'll compute cusps relative to that.
    For natal/transit: omit, use rising sign at lat/lon.
    """
    cusps_trop, ascmc = swe.houses(jd, lat, lon, b'P')  # Placidus; cusps_trop is 0-indexed, length 12

    if horary_lagna_sidereal is not None:
        # Horary: compute Placidus cusps for moment+place, then rotate to align cusp 1 with horary_lagna
        natural_asc_sid = (ascmc[0] - ayanamsa) % 360
        offset = (horary_lagna_sidereal - natural_asc_sid) % 360
        cusps_sid = [((cusps_trop[i] - ayanamsa + offset) % 360) for i in range(12)]
        # Force cusp 1 to be exactly horary_lagna_sidereal (eliminate floating point drift)
        cusps_sid[0] = horary_lagna_sidereal
    else:
        cusps_sid = [(cusps_trop[i] - ayanamsa) % 360 for i in range(12)]

    cusp_data = []
    for i, lon_sid in enumerate(cusps_sid, start=1):
        chain = full_lord_chain(lon_sid)
        chain["cusp"] = i
        cusp_data.append(chain)
    return cusp_data


# === Vimshottari Dasha ===

def compute_dasha_at_moment(moon_longitude_sid: float, dt_utc: datetime) -> Dict:
    """
    Compute current Vimshottari Dasha-Bhukti-Antara-Sookshma at a given moment,
    given the Moon's sidereal longitude AT BIRTH (or, for horary, at moment of question
    — which is what we want for horary).

    Returns the running MD-BD-AD-SD with start/end dates.
    """
    nak_idx, nak_name, star_lord, nak_start, _ne = get_nakshatra(moon_longitude_sid)
    pos_in_nak = moon_longitude_sid - nak_start
    fraction_traversed = pos_in_nak / NAKSHATRA_ARC
    md_years = VIMSHOTTARI_YEARS[star_lord]
    md_remaining_years = md_years * (1 - fraction_traversed)

    # Build dasha sequence from this moment forward
    md_start_dt = dt_utc - timedelta(days=md_years * 365.25 * fraction_traversed)
    sequence = []
    cur = star_lord
    cur_idx = VIMSHOTTARI_SEQUENCE.index(cur)
    cur_start = md_start_dt

    # Build 4 MDs ahead (covers ~50-70 years)
    for md_offset in range(4):
        md_lord = VIMSHOTTARI_SEQUENCE[(cur_idx + md_offset) % 9]
        md_yrs = VIMSHOTTARI_YEARS[md_lord]
        md_start = cur_start
        md_end = md_start + timedelta(days=md_yrs * 365.25)

        bhuktis = []
        bd_start = md_start
        bd_idx = VIMSHOTTARI_SEQUENCE.index(md_lord)
        for bd_offset in range(9):
            bd_lord = VIMSHOTTARI_SEQUENCE[(bd_idx + bd_offset) % 9]
            bd_yrs_full = VIMSHOTTARI_YEARS[bd_lord]
            bd_duration_days = (md_yrs * bd_yrs_full / 120) * 365.25
            bd_end = bd_start + timedelta(days=bd_duration_days)

            antaras = []
            ad_start = bd_start
            ad_idx = VIMSHOTTARI_SEQUENCE.index(bd_lord)
            for ad_offset in range(9):
                ad_lord = VIMSHOTTARI_SEQUENCE[(ad_idx + ad_offset) % 9]
                ad_yrs_full = VIMSHOTTARI_YEARS[ad_lord]
                ad_duration_days = (bd_duration_days * ad_yrs_full / 120)
                ad_end = ad_start + timedelta(days=ad_duration_days)

                sookshmas = []
                sd_start = ad_start
                sd_idx = VIMSHOTTARI_SEQUENCE.index(ad_lord)
                for sd_offset in range(9):
                    sd_lord = VIMSHOTTARI_SEQUENCE[(sd_idx + sd_offset) % 9]
                    sd_yrs_full = VIMSHOTTARI_YEARS[sd_lord]
                    sd_duration_days = (ad_duration_days * sd_yrs_full / 120)
                    sd_end = sd_start + timedelta(days=sd_duration_days)
                    sookshmas.append({
                        "sd_lord": sd_lord,
                        "start": sd_start.isoformat(),
                        "end": sd_end.isoformat(),
                    })
                    sd_start = sd_end

                antaras.append({
                    "ad_lord": ad_lord,
                    "start": ad_start.isoformat(),
                    "end": ad_end.isoformat(),
                    "sookshmas": sookshmas,
                })
                ad_start = ad_end

            bhuktis.append({
                "bd_lord": bd_lord,
                "start": bd_start.isoformat(),
                "end": bd_end.isoformat(),
                "antaras": antaras,
            })
            bd_start = bd_end

        sequence.append({
            "md_lord": md_lord,
            "start": md_start.isoformat(),
            "end": md_end.isoformat(),
            "bhuktis": bhuktis,
        })
        cur_start = md_end

    # Find the running DBA at dt_utc
    running = None
    for md in sequence:
        if datetime.fromisoformat(md["start"]) <= dt_utc < datetime.fromisoformat(md["end"]):
            for bd in md["bhuktis"]:
                if datetime.fromisoformat(bd["start"]) <= dt_utc < datetime.fromisoformat(bd["end"]):
                    for ad in bd["antaras"]:
                        if datetime.fromisoformat(ad["start"]) <= dt_utc < datetime.fromisoformat(ad["end"]):
                            for sd in ad["sookshmas"]:
                                if datetime.fromisoformat(sd["start"]) <= dt_utc < datetime.fromisoformat(sd["end"]):
                                    running = {
                                        "md_lord": md["md_lord"],
                                        "md_period": [md["start"], md["end"]],
                                        "bd_lord": bd["bd_lord"],
                                        "bd_period": [bd["start"], bd["end"]],
                                        "ad_lord": ad["ad_lord"],
                                        "ad_period": [ad["start"], ad["end"]],
                                        "sd_lord": sd["sd_lord"],
                                        "sd_period": [sd["start"], sd["end"]],
                                    }
                                    break
                            break
                    break
            break

    return {"running": running, "full_sequence": sequence}


# === Main ===

def main():
    parser = argparse.ArgumentParser(description="KP Horary Chart Computation")
    parser.add_argument("--number", type=int, required=True, help="Horary number 1-249")
    parser.add_argument("--datetime", type=str, required=True, help="ISO datetime, e.g. 2026-05-01T22:30:00")
    parser.add_argument("--tz", type=str, required=True, help="Timezone, e.g. Asia/Kolkata")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--question", type=str, default="(no question provided)")
    args = parser.parse_args()

    # Parse local datetime, convert to UTC
    local_tz = pytz.timezone(args.tz)
    dt_local = local_tz.localize(datetime.fromisoformat(args.datetime))
    dt_utc = dt_local.astimezone(pytz.UTC).replace(tzinfo=None)

    jd = get_julian_day(dt_utc)
    ayanamsa = get_kp_ayanamsa(jd)

    # Horary Lagna from number
    horary_lagna_sid, lagna_info = horary_number_to_lagna_degree(args.number)

    # Cusps
    cusps = compute_house_cusps(jd, args.lat, args.lon, ayanamsa,
                                horary_lagna_sidereal=horary_lagna_sid)

    # Planets
    planets = {}
    for pname in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
                  "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]:
        planets[pname] = compute_planet(jd, pname, ayanamsa)

    # Dasha at moment
    moon_sid = planets["Moon"]["longitude"]
    dasha = compute_dasha_at_moment(moon_sid, dt_utc)

    output = {
        "input": {
            "number": args.number,
            "datetime_local": dt_local.isoformat(),
            "datetime_utc": dt_utc.isoformat(),
            "timezone": args.tz,
            "latitude": args.lat,
            "longitude": args.lon,
            "question": args.question,
        },
        "ayanamsa": {
            "type": "KP New (Krishnamurti)",
            "value_deg": ayanamsa,
            "value_dms": deg_to_dms(ayanamsa),
        },
        "horary_lagna": lagna_info,
        "cusps": cusps,
        "planets": planets,
        "dasha": dasha,
    }

    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
