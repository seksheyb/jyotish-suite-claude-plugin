#!/usr/bin/env python3
"""
compute_vedic_baseline.py — deterministic Step-0 baseline for the
classical Vedic (Parashari) astrology skill.

Offloads the pure calculation the `vedic-astro` skill used to do in-prompt:
Lagna + functional roles, per-planet degree flags, Chara Karakas, the
Parashari graha-drishti aspect map, the running Vimshottari quartet, and
the Sarvashtakavarga (Bhinnashtakavarga per planet + SAV per sign).

All math primitives live in lib/jyotish_primitives.py; the chart itself
comes from lib/ephemeris.parashari_natal_chart. Only the Vedic-specific
assembly + Ashtakavarga scheme is implemented here.

Usage:
  compute_vedic_baseline.py --datetime ISO --tz TZ --lat LAT --lon LON
  compute_vedic_baseline.py --chart chart.json
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402


# ====================================================================
# Functional roles by Lagna (from references/chart-tables.md)
# Keyed by Lagna sign name.
# ====================================================================

FUNCTIONAL_ROLES = {
    "Aries":       (["Sun", "Moon", "Jupiter", "Mars"], ["Mercury", "Rahu", "Saturn"], "Sun"),
    "Taurus":      (["Saturn", "Mercury", "Venus", "Sun"], ["Jupiter", "Moon", "Mars"], "Saturn"),
    "Gemini":      (["Venus", "Saturn", "Mercury"], ["Mars", "Sun", "Jupiter"], "Venus"),
    "Cancer":      (["Mars", "Jupiter", "Moon"], ["Saturn", "Mercury", "Venus"], "Mars"),
    "Leo":         (["Mars", "Sun", "Jupiter"], ["Mercury", "Venus", "Saturn"], None),
    "Virgo":       (["Mercury", "Venus", "Saturn"], ["Mars", "Moon", "Jupiter"], "Mercury"),
    "Libra":       (["Mercury", "Saturn", "Venus"], ["Jupiter", "Sun", "Mars"], "Saturn"),
    "Scorpio":     (["Jupiter", "Moon", "Mars"], ["Mercury", "Venus"], "Moon"),
    "Sagittarius": (["Mars", "Sun", "Jupiter"], ["Saturn", "Venus"], "Sun"),
    "Capricorn":   (["Venus", "Saturn", "Mercury"], ["Mars", "Moon", "Jupiter"], "Venus"),
    "Aquarius":    (["Venus", "Saturn", "Mars"], ["Jupiter", "Moon", "Sun"], "Venus"),
    "Pisces":      (["Moon", "Mars", "Jupiter"], ["Saturn", "Venus", "Mercury"], None),
}


# ====================================================================
# Sarvashtakavarga — classical Parashari benefic-point scheme.
#
# For each of the 8 contributors (7 planets + Lagna), the table lists the
# house-numbers (counted from the contributor's own position) in which the
# subject planet earns 1 benefic point ("rekha"). The Bhinnashtakavarga
# (BAV) of a planet is the per-sign sum over all 8 contributors; the
# Sarvashtakavarga (SAV) of a sign is the sum of all 7 planets' BAV in it.
# Total SAV across the 12 signs = 337 (classical invariant).
# ====================================================================

# CONTRIB_HOUSES[subject][contributor] = list of benefic house-numbers
# (1 = same sign as the contributor). Standard Parashari tables.
CONTRIB_HOUSES = {
    "Sun": {
        "Sun":     [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":    [3, 6, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus":   [6, 7, 12],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":   [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun":     [3, 6, 7, 8, 10, 11],
        "Moon":    [1, 3, 6, 7, 10, 11],
        "Mars":    [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 8, 10, 11],
        "Jupiter": [1, 2, 4, 7, 8, 10, 11, 12],
        "Venus":   [3, 4, 5, 7, 9, 10, 11],
        "Saturn":  [3, 5, 6, 11],
        "Lagna":   [3, 6, 10, 11],
    },
    "Mars": {
        "Sun":     [3, 5, 6, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus":   [6, 8, 11, 12],
        "Saturn":  [1, 4, 7, 8, 9, 10, 11],
        "Lagna":   [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun":     [5, 6, 9, 11, 12],
        "Moon":    [2, 4, 6, 8, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":   [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun":     [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon":    [2, 5, 7, 9, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus":   [2, 5, 6, 9, 10, 11],
        "Saturn":  [3, 5, 6, 12],
        "Lagna":   [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun":     [8, 11, 12],
        "Moon":    [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars":    [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn":  [3, 4, 5, 8, 9, 10, 11],
        "Lagna":   [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun":     [1, 2, 4, 7, 8, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus":   [6, 11, 12],
        "Saturn":  [3, 5, 6, 11],
        "Lagna":   [1, 3, 4, 6, 10, 11],
    },
}

AV_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def compute_ashtakavarga(planet_sign_idx, lagna_sign_idx):
    """Compute classical Parashari Sarvashtakavarga.

    `planet_sign_idx` maps each of the 7 planets to its D1 sign index (0-11).
    Returns (bav, sav) where bav[planet][sign_name] is the Bhinnashtakavarga
    per sign and sav[sign_name] is the per-sign Sarvashtakavarga total.
    """
    contributors = dict(planet_sign_idx)
    contributors["Lagna"] = lagna_sign_idx

    bav = {}
    for subject in AV_PLANETS:
        per_sign = [0] * 12
        table = CONTRIB_HOUSES[subject]
        for contributor, houses in table.items():
            csi = contributors[contributor]
            for h in houses:
                target = jp.sign_n_from(csi, h)  # h-th sign from contributor (inclusive)
                per_sign[target] += 1
        bav[subject] = {jp.SIGNS[i]: per_sign[i] for i in range(12)}

    sav = {}
    for i in range(12):
        sav[jp.SIGNS[i]] = sum(bav[p][jp.SIGNS[i]] for p in AV_PLANETS)
    return bav, sav


# ====================================================================
# Chara Karakas — rank Sun..Saturn by descending degree-in-sign.
# 7-karaka scheme: AK, AmK, BK, MK, PiK, GK, DK.
# ====================================================================

CHARA_RANKS = ["AK", "AmK", "BK", "MK", "PiK", "GK", "DK"]
CHARA_NAMES = {
    "AK": "Atmakaraka", "AmK": "Amatyakaraka", "BK": "Bhratrikaraka",
    "MK": "Matrikaraka", "PiK": "Pitrikaraka", "GK": "Gnatikaraka",
    "DK": "Darakaraka",
}


def compute_chara_karakas(planets):
    """Rank the 7 visible planets (Sun..Saturn) by descending deg-in-sign."""
    seven = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    ranked = sorted(seven, key=lambda p: planets[p]["deg_in_sign"], reverse=True)
    out = {}
    for rank, planet in zip(CHARA_RANKS, ranked):
        out[rank] = {
            "karaka": CHARA_NAMES[rank],
            "planet": planet,
            "deg_in_sign": round(planets[planet]["deg_in_sign"], 4),
        }
    return out


# ====================================================================
# Parashari graha drishti — aspect map.
# ====================================================================

def orb_band(orb):
    if orb < 3.0:
        return "tight"
    if orb <= 7.0:
        return "moderate"
    return "loose"


def compute_aspect_map(planets, lagna_si):
    """For every planet, the houses and planets it aspects under Parashari
    graha drishti (universal 7th + Mars 4/8, Jupiter 5/9, Saturn 3/10)."""
    # planet -> (sign_idx, deg_in_sign, house)
    pos = {p: (jp.SIGNS.index(d["sign"]), d["deg_in_sign"], d["house"])
           for p, d in planets.items()}

    aspect_map = {}
    for p, (psi, pdeg, phouse) in pos.items():
        distances = [7] + jp.SPECIAL_ASPECTS.get(p, [])
        aspects = []
        for dist in sorted(distances):
            tsi = jp.sign_n_from(psi, dist)
            thouse = jp.house_of(tsi, lagna_si)
            # planets sitting in the aspected sign
            hit = []
            for q, (qsi, qdeg, _qh) in pos.items():
                if q == p or qsi != tsi:
                    continue
                # orb = degree separation along the exact aspect axis
                target_lon = (psi * 30 + pdeg + (dist - 1) * 30) % 360
                q_lon = qsi * 30 + qdeg
                sep = abs(target_lon - q_lon)
                sep = min(sep, 360 - sep)
                hit.append({"planet": q, "orb": round(sep, 2),
                            "strength": orb_band(sep)})
            aspects.append({"aspect": f"{dist}th", "sign": jp.SIGNS[tsi],
                            "house": thouse, "planets_aspected": hit})
        aspect_map[p] = aspects
    return aspect_map


# ====================================================================
# Per-planet block assembly
# ====================================================================

def build_planet_block(p, info, planets_raw):
    """Assemble the deterministic per-planet baseline entry."""
    lon = info["longitude"]
    sun_lon = planets_raw["Sun"]["longitude"]
    flags = jp.degree_flags(p, lon, sun_lon=sun_lon if p != "Sun" else None,
                            retrograde=info.get("retrograde", False))
    return {
        "sign": info["sign"],
        "deg_in_sign": round(info["deg_in_sign"], 4),
        "longitude_dms": info.get("longitude_dms", jp.deg_to_dms(lon)),
        "house": info["house"],
        "nakshatra": info["nakshatra"],
        "pada": info["pada"],
        "star_lord": info["star_lord"],
        "sign_lord": info["sign_lord"],
        "retrograde": info.get("retrograde", False),
        "dignity": info["dignity"],
        "navamsa_sign": info["navamsa_sign"],
        "vargottama": jp.is_vargottama(lon),
        "degree_flags": {
            "gandanta": flags["gandanta"],
            "sandhi": flags["sandhi"],
            "mrityu_bhaga": flags["mrityu_bhaga"],
            "pushkara_bhaga": flags["pushkara_bhaga"],
            "pushkara_navamsa": flags["pushkara_navamsa"],
            "combust": flags.get("combust", False),
        },
    }


# ====================================================================
# Main
# ====================================================================

def build_baseline(chart):
    d1 = chart["d1"]
    planets_raw = d1["planets"]
    lagna_sign = d1["lagna_sign"]
    lagna_si = jp.SIGNS.index(lagna_sign)
    lagna_lord = jp.SIGN_LORDS[lagna_si]

    benefics, malefics, yogakaraka = FUNCTIONAL_ROLES[lagna_sign]

    planets = {p: build_planet_block(p, info, planets_raw)
               for p, info in planets_raw.items()}

    # Ashtakavarga uses the 7 visible planets' D1 sign indices.
    planet_sign_idx = {p: jp.SIGNS.index(planets_raw[p]["sign"])
                       for p in AV_PLANETS}
    bav, sav = compute_ashtakavarga(planet_sign_idx, lagna_si)

    return {
        "chart_type": "vedic_parashari_baseline",
        "datetime_local": chart.get("datetime_local"),
        "datetime_utc": chart.get("datetime_utc"),
        "location": chart.get("location"),
        "ayanamsa": chart.get("ayanamsa"),
        "house_system": chart.get("house_system", "Whole-Sign"),
        "lagna": {
            "sign": lagna_sign,
            "lord": lagna_lord,
            "nakshatra": d1.get("lagna_nakshatra"),
            "longitude_dms": d1.get("lagna_longitude_dms"),
        },
        "functional_roles": {
            "lagna": lagna_sign,
            "benefics": benefics,
            "malefics": malefics,
            "yogakaraka": yogakaraka,
        },
        "planets": planets,
        "chara_karakas": compute_chara_karakas(planets),
        "aspect_map": compute_aspect_map(planets, lagna_si),
        "dasha": chart.get("dasha", {}).get("running"),
        "ashtakavarga": {
            "sav_per_sign": sav,
            "sav_total": sum(sav.values()),
            "bav_per_planet": bav,
        },
    }


def main():
    ap = argparse.ArgumentParser(
        description="Compute the deterministic Vedic (Parashari) Step-0 baseline.")
    ap.add_argument("--datetime", help="Birth datetime, ISO format")
    ap.add_argument("--tz", help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--lat", type=float, help="Latitude (decimal degrees)")
    ap.add_argument("--lon", type=float, help="Longitude (decimal degrees)")
    ap.add_argument("--chart", help="Path to a pre-computed parashari_natal_chart JSON")
    args = ap.parse_args()

    if args.chart:
        with open(args.chart) as f:
            chart = json.load(f)
    else:
        missing = [n for n, v in (("--datetime", args.datetime), ("--tz", args.tz),
                                  ("--lat", args.lat), ("--lon", args.lon))
                   if v is None]
        if missing:
            ap.error("provide --chart, or all of: " + ", ".join(missing))
        chart = eph.parashari_natal_chart(args.datetime, args.tz, args.lat, args.lon)

    baseline = build_baseline(chart)
    print(json.dumps(baseline, indent=2, default=str))


if __name__ == "__main__":
    main()
