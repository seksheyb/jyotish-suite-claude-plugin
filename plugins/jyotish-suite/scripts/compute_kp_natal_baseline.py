#!/usr/bin/env python3
"""
KP Natal — deterministic baseline.

Computes everything fixed for a KP natal reading so the skill prompt never has
to do astronomy or KP arithmetic in-head: the cuspal chains + CSL, planetary
chains, the 4-level significators of all 12 houses, the Ruling Planets at the
moment of the reading, the running Vimshottari quartet, and the structured
event -> house-set table.

All ephemeris + lord-chain + dasha-tree math is delegated to lib/. This file
only does KP-specific assembly. Replaces compute_ruling_planets.py and
compute_sookshma.py.

Usage:
    python compute_kp_natal_baseline.py \
      --datetime "1991-07-30T10:20:00" --tz "Asia/Kolkata" \
      --lat 28.6139 --lon 77.2090 \
      [--rp-datetime "2026-05-21T09:00:00"] \
      [--target-datetime "2026-09-01T00:00:00"]

    python compute_kp_natal_baseline.py --chart parsed_chart.json [...]
"""

import argparse
import json
import os
import sys
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
# lib/ lives at the plugin root; resolve it whether scripts/ is one or three
# levels below that root.
for _cand in (os.path.join(_HERE, "..", "lib"),
              os.path.join(_HERE, "..", "..", "..", "lib")):
    if os.path.isfile(os.path.join(_cand, "jyotish_primitives.py")):
        sys.path.insert(0, _cand)
        break
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
NODES = ("Rahu", "Ketu")


# ====================================================================
# House occupancy (Placidus, cusp-to-cusp arcs)
# ====================================================================

def house_of_longitude(lon, cusps):
    """Return the KP house number (1-12) a longitude falls in, using the
    Placidus cusp-to-next-cusp arcs (a house is a swathe of degrees)."""
    lon = jp.norm360(lon)
    for i in range(12):
        start = cusps[i]["longitude"]
        end = cusps[(i + 1) % 12]["longitude"]
        span = jp.norm360(end - start)
        if jp.norm360(lon - start) < span:
            return i + 1
    return 12


def house_lord(house_num, cusps):
    """Sign-lord of the cusp = the house-lord (L4)."""
    return cusps[house_num - 1]["sign_lord"]


# ====================================================================
# 4-level significators
# ====================================================================

def compute_significators(cusps, planets):
    """For each of the 12 houses return L1/L2/L3/L4 significator lists.

      L1 — planets in the star of a planet occupying the house
      L2 — planets occupying the house
      L3 — planets in the star of the house-lord
      L4 — the house-lord
    Plus node-conjunction additions per significators-rules.md.

    Returns (significators, amplifications) where `amplifications` records the
    reverse nodal rule (significators-rules.md:37-38): a planet conjunct a node
    inherits the houses that node signifies.
    """
    # occupancy of every planet
    occ = {p: house_of_longitude(planets[p]["longitude"], cusps) for p in planets}

    # node depositor + conjunctions (within ~3deg, same sign)
    node_extra = {}
    for node in NODES:
        nl = planets[node]["longitude"]
        nsi = int(jp.norm360(nl) // 30)
        depositor = jp.SIGN_LORDS[nsi]
        conj = [p for p in planets if p != node
                and int(jp.norm360(planets[p]["longitude"]) // 30) == nsi
                and abs(jp.norm360(planets[p]["longitude"]) - jp.norm360(nl)) <= 3.0]
        node_extra[node] = {"depositor": depositor, "conjunct": conj}

    out = {}
    for h in range(1, 13):
        occupants = sorted(p for p in planets if occ[p] == h)
        hl = house_lord(h, cusps)

        # L1: planets in star of any occupant
        l1 = sorted(p for p in planets
                    if planets[p]["star_lord"] in occupants)
        # L2: occupants
        l2 = list(occupants)
        # L3: planets in star of the house-lord
        l3 = sorted(p for p in planets
                    if planets[p]["star_lord"] == hl)
        # L4: the house-lord
        l4 = [hl]

        # node additions: a node co-signifies a house if its depositor or a
        # conjunct planet is among that house's significators
        base = set(l1) | set(l2) | set(l3) | set(l4)
        for node in NODES:
            if node in base:
                continue
            ne = node_extra[node]
            if ne["depositor"] in base or any(c in base for c in ne["conjunct"]):
                l2.append(node)  # nodal agent acts at occupant strength
        out[str(h)] = {"L1": l1, "L2": sorted(set(l2)), "L3": l3, "L4": l4}

    # reverse nodal rule: a planet conjunct a node inherits the houses that
    # node signifies (significators-rules.md:37-38, methodology.md:34). Emit as
    # a per-planet annotation rather than mutating the house lists, so the
    # interpretive layer applies the amplification without re-deriving it.
    sig_houses = invert_significators(out)
    amplifications = {}
    for node in NODES:
        node_houses = sig_houses.get(node, set())
        for p in node_extra[node]["conjunct"]:
            extra = sorted(node_houses - sig_houses.get(p, set()))
            if extra:
                amplifications.setdefault(p, []).append(
                    {"via_node": node, "extra_houses": extra})
    return out, amplifications


def invert_significators(significators):
    """Reverse map: planet -> set of house numbers it signifies (any level)."""
    sig_houses = {}
    for hs, levels in significators.items():
        for key in ("L1", "L2", "L3", "L4"):
            for p in levels[key]:
                sig_houses.setdefault(p, set()).add(int(hs))
    return sig_houses


def compute_fruitful_barren(significators, planets):
    """Reverse index for the fruitful/barren sub-lord gate
    (significators-rules.md:40-51). For every planet emit its sub-lord and the
    houses that sub-lord signifies (all 4 levels), so a downstream worker can
    test a candidate significator's sub-lord against a question's positive /
    negative house set without inverting the table by hand."""
    sig_houses = invert_significators(significators)
    sub_lord_signifies = {p: sorted(hs) for p, hs in sig_houses.items()}
    planet_sub_lord = {}
    for p in planets:
        sl = planets[p]["sub_lord"]
        planet_sub_lord[p] = {
            "sub_lord": sl,
            "sub_lord_signifies": sorted(sig_houses.get(sl, set())),
        }
    return {"sub_lord_signifies": sub_lord_signifies,
            "planet_sub_lord": planet_sub_lord}


# ====================================================================
# Ruling Planets — ported from compute_ruling_planets.py
# ====================================================================

def compute_ruling_planets(rp_dt_iso, tz, lat, lon):
    """7-factor RP at the moment of the reading + birth location.
    KP-New ayanamsa, real rising Lagna (not a horary number)."""
    local, utc = eph.to_utc(rp_dt_iso, tz)
    jd = eph.julian_day(utc)
    ayan = eph.ayanamsa(jd, "kp")

    dlord, sunrise_dt = eph.day_lord(jd, lat, lon)

    moon_lon, _retro, _spd = eph.planet_position(jd, "Moon", ayan)
    moon_chain = jp.full_lord_chain(moon_lon)

    asc_lon = eph.ascendant(jd, lat, lon, ayan)
    asc_chain = jp.full_lord_chain(asc_lon)

    factors = [
        ("Lagna Sub Lord", asc_chain["sub_lord"]),
        ("Lagna Star Lord", asc_chain["star_lord"]),
        ("Lagna Sign Lord", asc_chain["sign_lord"]),
        ("Moon Sub Lord", moon_chain["sub_lord"]),
        ("Moon Star Lord", moon_chain["star_lord"]),
        ("Moon Sign Lord", moon_chain["sign_lord"]),
        ("Day Lord", dlord),
    ]

    # dedup, preserve strength order
    seen, dedup = set(), []
    for _role, planet in factors:
        if planet not in seen:
            dedup.append(planet)
            seen.add(planet)

    # positions of all nine grahas at the reading moment
    positions = {}
    for p in PLANETS:
        plon, pretro, _spd = eph.planet_position(jd, p, ayan)
        positions[p] = {"lon": jp.norm360(plon), "retro": pretro}

    # retrograde check + depositor-keep exception. A retrograde RP whose
    # depositor (sign-lord) is NOT itself an RP is excluded from the final set
    # (ruling-planets.md "Including retrograde planets without depositor-check").
    retro_check = {}
    excluded = set()
    for planet in dedup:
        if planet in NODES:
            retro_check[planet] = "node — retrograde rule N/A"
            continue
        plon = positions[planet]["lon"]
        retro = positions[planet]["retro"]
        if retro:
            depositor = jp.get_sign(plon)[2]
            keep = depositor in dedup
            retro_check[planet] = (
                f"RETROGRADE — depositor {depositor} "
                + ("is RP, retained" if keep else "not RP, excluded"))
            if not keep:
                excluded.add(planet)
        else:
            retro_check[planet] = "Direct"

    # confirmed RP core = deduped factors minus retrograde-excluded planets
    rp_core = [p for p in dedup if p not in excluded]

    # Rahu/Ketu agent rule (ruling-planets.md / significators-rules.md): a node
    # joins the RP set if ANY of — its sign-lord is an RP, its star-lord is an
    # RP, or it is conjunct (within ~3deg, same sign) a planet already in the
    # RP core. Previously only the sign-lord condition was tested.
    def node_qualification(node):
        nlon = positions[node]["lon"]
        sign_lord = jp.get_sign(nlon)[2]
        star_lord = jp.get_nakshatra(nlon)[2]
        reasons = []
        if sign_lord in rp_core:
            reasons.append(f"sign-lord {sign_lord} is RP")
        if star_lord in rp_core:
            reasons.append(f"star-lord {star_lord} is RP")
        nsi = int(nlon // 30)
        conj = [p for p in PLANETS if p not in NODES and p in rp_core
                and int(positions[p]["lon"] // 30) == nsi
                and abs(positions[p]["lon"] - nlon) <= 3.0]
        if conj:
            reasons.append("conjunct RP " + ", ".join(conj))
        return {"sign_lord": sign_lord, "star_lord": star_lord,
                "conjunct_rp": conj, "reasons": reasons,
                "added_to_rp": bool(reasons)}

    rahu_check = node_qualification("Rahu")
    ketu_check = node_qualification("Ketu")

    final_rp = list(rp_core)
    if rahu_check["added_to_rp"] and "Rahu" not in final_rp:
        final_rp.append("Rahu")
    if ketu_check["added_to_rp"] and "Ketu" not in final_rp:
        final_rp.append("Ketu")

    return {
        "moment_local": local.isoformat(),
        "moment_utc": utc.isoformat(),
        "ayanamsa_dms": jp.deg_to_dms(ayan),
        "day_lord": {"lord": dlord,
                     "weekday_at_sunrise": sunrise_dt.strftime("%A"),
                     "sunrise_local": sunrise_dt.isoformat()},
        "moon": {"longitude_dms": moon_chain["longitude_dms"],
                 "sign": moon_chain["sign"], "sign_lord": moon_chain["sign_lord"],
                 "nakshatra": moon_chain["nakshatra"],
                 "star_lord": moon_chain["star_lord"],
                 "sub_lord": moon_chain["sub_lord"]},
        "lagna": {"longitude_dms": asc_chain["longitude_dms"],
                  "sign": asc_chain["sign"], "sign_lord": asc_chain["sign_lord"],
                  "nakshatra": asc_chain["nakshatra"],
                  "star_lord": asc_chain["star_lord"],
                  "sub_lord": asc_chain["sub_lord"]},
        "factors_in_strength_order": [{"role": r, "planet": p} for r, p in factors],
        "deduplicated": dedup,
        "retrograde_check": retro_check,
        "retrograde_excluded": sorted(excluded),
        "rahu_check": rahu_check,
        "ketu_check": ketu_check,
        "final_rp": final_rp,
        # By convention the Lagna Sub Lord is the strongest RP (factor #1). A
        # qualifying node is added to the set but does not outrank it here —
        # see references/ruling-planets.md "Using RP in the verdict".
        "strongest_rp": asc_chain["sub_lord"],
    }


# ====================================================================
# event -> house-set table (house-combinations.md as structured data)
# ====================================================================

HOUSE_COMBINATIONS = {
    "marriage": {"primary": [7], "positive": [2, 7, 11], "negative": [1, 6, 10],
                 "note": "Love marriage: also check 5. Rahu on 7/7-CSL = unconventional."},
    "new_job": {"primary": [10], "positive": [2, 6, 10, 11], "negative": [5, 8, 12],
                "note": "6 essential for employment; self-employment uses 7 + 2,11."},
    "job_change": {"primary": [1, 10], "positive": [5, 9], "negative": [],
                   "note": "Two-step: 1/10-CSL signifying 5/9 = inclination; then run new_job."},
    "promotion": {"primary": [10, 2], "positive": [2, 6, 10, 11], "negative": [5, 8, 12],
                  "note": "10-CSL must signify 11 strongly (gain over status)."},
    "litigation_own": {"primary": [6], "positive": [1, 6, 11], "negative": [5, 8, 12],
                       "note": "6-CSL on 7/8/12 = lose. Settlement: check 9."},
    "litigation_opponent": {"primary": [12], "positive": [12, 5, 1], "negative": [6, 11],
                            "note": "Mirror: their 1=your 7, their 6=your 12, their 11=your 5."},
    "property_purchase": {"primary": [4], "positive": [4, 11, 12], "negative": [3, 5, 10],
                          "note": "4-CSL on 3/5/10 = sale not acquisition."},
    "property_sale": {"primary": [3], "positive": [3, 5, 10], "negative": [4, 11, 12],
                      "note": "Inverse of property purchase."},
    "childbirth": {"primary": [5], "positive": [2, 5, 11], "negative": [1, 4, 10],
                   "note": "Saturn/Ketu CSL on 5 = delay/denial; sub-sub crucial."},
    "loan_borrow": {"primary": [6], "positive": [2, 6, 11], "negative": [8, 12],
                    "note": "Giving a loan: primary becomes 8, look for 11 (repaid)."},
    "speculation": {"primary": [5], "positive": [2, 5, 11], "negative": [8, 12],
                    "note": "Investment return / speculative gain."},
    "long_travel": {"primary": [9], "positive": [3, 9, 12], "negative": [4, 8],
                    "note": "8 negative = travel obstacle/danger."},
    "foreign_settlement": {"primary": [12], "positive": [9, 12, 7], "negative": [4, 11],
                           "note": "4 = homeland holds; 11 = gain at home keeps you."},
    "health_cure": {"primary": [1, 6], "positive": [1, 5, 11], "negative": [6, 8, 12],
                    "note": "1-CSL on 6/8/12 = continued illness."},
    "education_exam": {"primary": [4, 9], "positive": [4, 9, 11], "negative": [8, 12],
                       "note": "Competitive exam: add 6 and 10."},
    "lost_item": {"primary": [2], "positive": [2, 11], "negative": [6, 8, 12],
                  "note": "CSL sign gives direction of the item."},
    "election": {"primary": [10], "positive": [6, 10, 11], "negative": [5, 8, 12],
                 "note": "6 = defeat opponent; 11 = fulfillment."},
    "business_launch": {"primary": [10, 11], "positive": [2, 6, 10, 11], "negative": [5, 8, 12],
                        "note": "Project / venture launch."},
}


# ====================================================================
# KP degree flags (KP flat orbs — NOT the Parashari orbs in lib)
# ====================================================================

def kp_degree_flags(name, lon, sun_lon=None, retrograde=False, is_planet=True):
    """KP-specific degree flags for one body.

    combust : |body - Sun| <= 8.5deg (KP flat orb; methodology.md:102), never
              for the Sun or the nodes.
    sandhi  : first/last 0deg30' of a sign (KP window, not lib's 1deg window).
    gandanta / mrityu_bhaga : reuse the shared primitives (already KP-correct
              3deg20' zones and the table-driven death-degrees respectively).
    """
    lon = jp.norm360(lon)
    d = jp.deg_in_sign(lon)
    flags = {
        "gandanta": jp.gandanta(lon),
        "sandhi": (d < 0.5 or d >= 29.5),
    }
    if is_planet:
        flags["mrityu_bhaga"] = jp.mrityu_bhaga(name, lon)
        if sun_lon is not None and name != "Sun" and name not in NODES:
            sep = abs(lon - jp.norm360(sun_lon))
            sep = min(sep, 360 - sep)
            flags["combust"] = sep <= 8.5
    return flags


# ====================================================================
# Chart load / assembly
# ====================================================================

def load_chart(args):
    """Return a KP natal chart dict — from --chart file or freshly computed."""
    if args.chart:
        with open(args.chart) as fh:
            chart = json.load(fh)
        if "cusps" not in chart or "planets" not in chart:
            sys.stderr.write("ERROR: --chart file must have 'cusps' and 'planets'.\n")
            sys.exit(1)
        return chart
    if not all([args.datetime, args.tz, args.lat is not None, args.lon is not None]):
        sys.stderr.write("ERROR: need --datetime --tz --lat --lon (or --chart).\n")
        sys.exit(1)
    return eph.kp_natal_chart(args.datetime, args.tz, args.lat, args.lon)


def main():
    ap = argparse.ArgumentParser(description="KP natal deterministic baseline.")
    ap.add_argument("--datetime", help="birth datetime, ISO (naive local)")
    ap.add_argument("--tz", help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--lat", type=float, help="birth latitude")
    ap.add_argument("--lon", type=float, help="birth longitude")
    ap.add_argument("--chart", help="path to a pre-parsed KP chart JSON")
    ap.add_argument("--rp-datetime", help="moment of the reading for Ruling Planets "
                                          "(defaults to now)")
    ap.add_argument("--target-datetime", help="moment for the Sookshma window")
    args = ap.parse_args()

    chart = load_chart(args)
    cusps = chart["cusps"]
    planets = chart["planets"]

    sun_lon = planets.get("Sun", {}).get("longitude")

    # CSL = the cuspal sub-lord, already in each cusp's full_lord_chain.
    # Attach KP degree flags to every cusp (gandanta/sandhi of the cusp point).
    cusps_out = []
    for c in cusps:
        entry = dict(c)
        entry["CSL"] = c["sub_lord"]
        entry["degree_flags"] = kp_degree_flags(
            "cusp", c["longitude"], is_planet=False)
        cusps_out.append(entry)

    # Attach KP degree flags to every planet (combust/sandhi/gandanta/MB).
    for p in planets:
        planets[p]["degree_flags"] = kp_degree_flags(
            p, planets[p]["longitude"], sun_lon=sun_lon,
            retrograde=planets[p].get("retrograde", False))

    significators, amplifications = compute_significators(cusps, planets)
    fruitful_barren = compute_fruitful_barren(significators, planets)

    # Ruling Planets — needs a location; require birth coords or --chart location
    loc = chart.get("location") or {}
    rp_lat = args.lat if args.lat is not None else loc.get("lat")
    rp_lon = args.lon if args.lon is not None else loc.get("lon")
    rp_tz = args.tz or loc.get("tz")
    rp_dt = args.rp_datetime or datetime.now().replace(microsecond=0).isoformat()
    ruling_planets = None
    if rp_lat is not None and rp_lon is not None and rp_tz:
        ruling_planets = compute_ruling_planets(rp_dt, rp_tz, rp_lat, rp_lon)
    else:
        ruling_planets = {"error": "RP needs lat/lon/tz — supply --lat/--lon/--tz "
                                   "or a --chart with a 'location' block."}

    # Dasha — the chart's `running` field is the AT-BIRTH quartet (birth-anchored
    # in lib/ephemeris). For a reading we need the quartet running at the reading
    # moment, so `running_at_target` is always populated: it defaults to the RP
    # moment (the reading datetime) when --target-datetime is not supplied.
    dasha_block = dict(chart.get("dasha", {}))
    tree = chart.get("dasha", {}).get("tree")
    target_dt = args.target_datetime or rp_dt
    if tree and rp_tz and target_dt:
        _local, tgt_utc = eph.to_utc(target_dt, rp_tz)
        dasha_block["target_datetime"] = target_dt
        dasha_block["running_at_target"] = jp.find_running(tree, tgt_utc)

    baseline = {
        "school": "kp-natal",
        "chart_type": chart.get("chart_type", "kp_natal"),
        "ayanamsa": chart.get("ayanamsa"),
        "house_system": chart.get("house_system", "Placidus"),
        "datetime_local": chart.get("datetime_local"),
        "datetime_utc": chart.get("datetime_utc"),
        "location": loc,
        "cusps": cusps_out,
        "planets": planets,
        "significators": significators,
        "significator_amplifications": amplifications,
        "fruitful_barren": fruitful_barren,
        "ruling_planets": ruling_planets,
        "dasha": dasha_block,
        "house_combinations": HOUSE_COMBINATIONS,
    }
    print(json.dumps(baseline, indent=2, default=str))


if __name__ == "__main__":
    main()
