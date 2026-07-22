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
from datetime import datetime, timezone

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


def ordinal(n):
    """1->'1st', 2->'2nd', 3->'3rd', 4->'4th', ... (with the teens exception)."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _dms_to_deg(dms):
    """'DDD-MM-SS' -> decimal degrees."""
    parts = str(dms).split("-")
    d = float(parts[0]) if parts and parts[0] else 0.0
    m = float(parts[1]) if len(parts) > 1 else 0.0
    s = float(parts[2]) if len(parts) > 2 else 0.0
    return d + m / 60.0 + s / 3600.0


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
            aspects.append({"aspect": ordinal(dist), "sign": jp.SIGNS[tsi],
                            "house": thouse, "planets_aspected": hit})
        aspect_map[p] = aspects

    # Second pass — flag mutual aspects (A aspects B and B aspects A).
    aspected_by = {p: set() for p in aspect_map}
    for p, entries in aspect_map.items():
        for e in entries:
            for h in e["planets_aspected"]:
                aspected_by[p].add(h["planet"])
    for p, entries in aspect_map.items():
        for e in entries:
            for h in e["planets_aspected"]:
                h["mutual"] = p in aspected_by.get(h["planet"], set())

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
        "gana": jp.gana_of(lon),
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
# D9 (Navamsa) sub-chart
# ====================================================================

def d9_longitude(d1_lon):
    """Expanded Navamsa longitude — the D9 sign plus the planet's position
    within its 3deg20' navamsa scaled up to a full 30deg sign."""
    d9_si, _ = jp.navamsa_sign(d1_lon)
    pos_in_navamsa = jp.deg_in_sign(d1_lon) % jp.NAVAMSA_ARC
    return d9_si * 30.0 + pos_in_navamsa * 9.0


def build_d9(lagna_lon, planets_raw):
    """Deterministic D9 sub-chart: D9 Lagna, per-planet D9 sign/house/degree/
    dignity/flags, and the D9 graha-drishti aspect map (methodology Step 3)."""
    d9_lagna_lon = d9_longitude(lagna_lon)
    d9_lagna_si = int(d9_lagna_lon // 30)

    d9_planets = {}
    for p, info in planets_raw.items():
        d9_lon = d9_longitude(info["longitude"])
        d9_si = int(d9_lon // 30)
        flags = jp.degree_flags(p, d9_lon)
        d9_planets[p] = {
            "sign": jp.SIGNS[d9_si],
            "deg_in_sign": round(jp.deg_in_sign(d9_lon), 4),
            "house": jp.house_of(d9_si, d9_lagna_si),
            "sign_lord": jp.SIGN_LORDS[d9_si],
            "dignity": jp.dignity(p, d9_lon),
            "vargottama": jp.is_vargottama(info["longitude"]),
            "degree_flags": {
                "gandanta": flags["gandanta"],
                "sandhi": flags["sandhi"],
                "mrityu_bhaga": flags["mrityu_bhaga"],
                "pushkara_bhaga": flags["pushkara_bhaga"],
                "pushkara_navamsa": flags["pushkara_navamsa"],
            },
        }

    return {
        "lagna": {
            "sign": jp.SIGNS[d9_lagna_si],
            "lord": jp.SIGN_LORDS[d9_lagna_si],
            "deg_in_sign": round(jp.deg_in_sign(d9_lagna_lon), 4),
        },
        "planets": d9_planets,
        "aspect_map": compute_aspect_map(d9_planets, d9_lagna_si),
    }


# ====================================================================
# Vimshottari dasha — resolved at the reading date, not at birth
# ====================================================================

def build_dasha_block(chart, asof_dt):
    """Resolve the Vimshottari dasha running at `asof_dt`. The tree is anchored
    at birth (Moon longitude + birth datetime) and spans 9 mahadashas so any
    reasonable reading date is covered. Emits the running MD/AD/PD/SD, the full
    mahadasha timeline, and the antardasha timeline of the current MD."""
    raw = chart.get("dasha") or {}
    birth_iso = chart.get("datetime_utc")
    moon = chart.get("d1", {}).get("planets", {}).get("Moon")

    if birth_iso and moon:
        birth_dt = datetime.fromisoformat(birth_iso)
        moon_lon = moon["longitude"]
        tree = jp.build_dasha_tree(moon_lon, birth_dt, n_md=9)
        running = jp.find_running(tree, asof_dt)
        start_lord, balance, _elapsed = jp.vimshottari_balance(moon_lon)
        block = {
            "available": True,
            "asof": asof_dt.isoformat(),
            "starting_mahadasha": start_lord,
            "balance_years": round(balance, 3),
            "mahadasha_sequence": [
                {"md_lord": md["md_lord"], "start": md["start"], "end": md["end"]}
                for md in tree],
        }
        if running:
            block["running"] = {
                "mahadasha": {"lord": running["md_lord"],
                              "start": running["md_period"][0],
                              "end": running["md_period"][1]},
                "antardasha": {"lord": running["bd_lord"],
                               "start": running["bd_period"][0],
                               "end": running["bd_period"][1]},
                "pratyantardasha": {"lord": running["ad_lord"],
                                    "start": running["ad_period"][0],
                                    "end": running["ad_period"][1]},
                "sookshma": {"lord": running["sd_lord"],
                             "start": running["sd_period"][0],
                             "end": running["sd_period"][1]},
            }
            bhuktis = []
            for md in tree:
                if md["start"] == running["md_period"][0]:
                    bhuktis = [{"bd_lord": b["bd_lord"], "start": b["start"],
                                "end": b["end"]} for b in md["bhuktis"]]
                    break
            block["current_mahadasha_bhuktis"] = bhuktis
        else:
            block["running"] = None
            block["note"] = ("asof date falls outside the 9-mahadasha span; "
                             "no running dasha resolved.")
        return block

    if raw.get("source") == "user-supplied":
        return {"available": True, "source": "user-supplied",
                **{k: v for k, v in raw.items() if k != "source"}}

    return {"available": False,
            "note": "No birth datetime supplied — Vimshottari dasha omitted. "
                    "Share birth date, time and place for dasha timing."}


# ====================================================================
# Main
# ====================================================================

def build_baseline(chart, asof_dt):
    d1 = chart["d1"]
    planets_raw = d1["planets"]
    lagna_sign = d1["lagna_sign"]
    lagna_si = jp.SIGNS.index(lagna_sign)
    lagna_lord = jp.SIGN_LORDS[lagna_si]
    lagna_lon = d1.get("lagna_longitude")
    if lagna_lon is None:
        lagna_lon = _dms_to_deg(d1.get("lagna_longitude_dms", "000-00-00"))

    benefics, malefics, yogakaraka = FUNCTIONAL_ROLES[lagna_sign]

    planets = {p: build_planet_block(p, info, planets_raw)
               for p, info in planets_raw.items()}

    # Planetary War (Graha Yuddha) — needs all positions together.
    positions = {p: info["longitude"] for p, info in planets_raw.items()}
    wars = jp.planetary_war(positions)
    war_by_planet = {}
    for w in wars:
        war_by_planet[w["winner"]] = {"role": "winner", "opponent": w["loser"],
                                      "separation": w["separation"]}
        war_by_planet[w["loser"]] = {"role": "loser", "opponent": w["winner"],
                                     "separation": w["separation"]}
    for p in planets:
        planets[p]["degree_flags"]["planetary_war"] = war_by_planet.get(p, False)

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
        "planetary_war": wars,
        "chara_karakas": compute_chara_karakas(planets),
        "aspect_map": compute_aspect_map(planets, lagna_si),
        "d9": build_d9(lagna_lon, planets_raw),
        "dasha": build_dasha_block(chart, asof_dt),
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
    ap.add_argument("--asof", help="Reading date (ISO) the Vimshottari dasha is "
                                   "resolved at. Default: today (UTC).")
    args = ap.parse_args()

    if args.asof:
        asof_dt = datetime.fromisoformat(args.asof)
    else:
        asof_dt = datetime.now(timezone.utc).replace(tzinfo=None)

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

    baseline = build_baseline(chart, asof_dt)
    print(json.dumps(baseline, indent=2, default=str))


if __name__ == "__main__":
    main()
