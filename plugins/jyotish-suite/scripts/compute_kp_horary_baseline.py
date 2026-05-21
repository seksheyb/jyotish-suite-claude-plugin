#!/usr/bin/env python3
"""
KP Horary / Prashna — deterministic baseline computer.

Replaces compute_horary_chart.py + compute_ruling_planets.py. Produces ONE JSON
object holding every DETERMINISTIC fact the kp-horary skill needs before any
interpretation: the number-derived chart Lagna, rotated cusps, planets, the
Ruling Planets set (computed from the REAL rising sign), 4-level house
significators, the running Vimshottari quartet, and the question->house table.

KP horary uses TWO Lagnas and they must never be mixed:
  * CHART Lagna  — from the 1-249 number (drives cusps + significators).
  * RP    Lagna  — the ACTUAL rising sign at the question's time + place
                   (drives the Ruling Planets only).
ephemeris.kp_horary_chart() exposes the first as `horary_lagna` and the second
as `ruling_planets_lagna`.

All ephemeris/dasha/sub-lord math lives in lib/ — this script only orchestrates.

Usage:
    python3 compute_kp_horary_baseline.py \
      --number 142 --datetime "2026-05-01T22:30:00" \
      --tz "Asia/Kolkata" --lat 28.6139 --lon 77.2090 \
      --question "Will the deal close before Diwali?"
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Locate the shared lib/ — walk up from this script until lib/ephemeris.py
# is found (the plugin keeps lib/ at its root, scripts/ live under skills/).
_d = os.path.dirname(os.path.abspath(__file__))
for _ in range(6):
    _cand = os.path.join(_d, "lib")
    if os.path.isfile(os.path.join(_cand, "ephemeris.py")):
        sys.path.insert(0, _cand)
        break
    _d = os.path.dirname(_d)
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402


# ====================================================================
# Question -> house-set table (ported verbatim from house-combinations.md)
# ====================================================================
# Each entry: primary house, positive set, negative set. Structured so the
# interpreting agent never has to re-derive it from prose.
HOUSE_COMBINATIONS = {
    "marriage":               {"primary": [7],        "positive": [2, 7, 11],     "negative": [1, 6, 10]},
    "new_job":                {"primary": [10],       "positive": [2, 6, 10, 11], "negative": [5, 8, 12]},
    "job_change_leaving":     {"primary": [1, 10],    "positive": [5, 9],         "negative": [2, 6, 10, 11]},
    "job_change_new":         {"primary": [10],       "positive": [2, 6, 10, 11], "negative": [5, 8, 12]},
    "promotion":              {"primary": [10, 2],    "positive": [2, 6, 10, 11], "negative": [5, 8, 12]},
    "litigation_own":         {"primary": [6],        "positive": [1, 6, 11],     "negative": [5, 8, 12]},
    "litigation_opponent":    {"primary": [12],       "positive": [5, 8, 12],     "negative": [1, 6, 11]},
    "property_purchase":      {"primary": [4],        "positive": [4, 11, 12],    "negative": [3, 5, 10]},
    "property_sale":          {"primary": [3],        "positive": [3, 5, 10],     "negative": [4, 11, 12]},
    "childbirth":             {"primary": [5],        "positive": [2, 5, 11],     "negative": [1, 4, 10]},
    "loan_borrowing":         {"primary": [6],        "positive": [2, 6, 11],     "negative": [8, 12]},
    "loan_giving":            {"primary": [8],        "positive": [8, 11, 2],     "negative": [6, 12]},
    "investment_return":      {"primary": [5],        "positive": [2, 5, 11],     "negative": [8, 12]},
    "travel_long":            {"primary": [9],        "positive": [3, 9, 12],     "negative": [4, 8]},
    "foreign_settlement":     {"primary": [12],       "positive": [9, 12, 7],     "negative": [4, 11]},
    "health_cure":            {"primary": [1],        "positive": [1, 5, 11],     "negative": [6, 8, 12]},
    "education_exam":         {"primary": [4, 9],     "positive": [4, 9, 11],     "negative": [8, 12]},
    "lost_item_recovery":     {"primary": [2],        "positive": [2, 11],        "negative": [6, 8, 12]},
    "election_appointment":   {"primary": [10],       "positive": [6, 10, 11],    "negative": [5, 8, 12]},
    "business_launch":        {"primary": [10, 11],   "positive": [2, 6, 10, 11], "negative": [5, 8, 12]},
}

# Fruitful (positive) vs barren (denial) sub-lord gate. A primary-house CSL
# whose own signification falls only in the negative set blocks fructification.
FRUITFUL_HOUSES = [2, 5, 9, 11]   # generically supportive
BARREN_HOUSES = [6, 8, 12]        # generically obstructive (dusthana)


# ====================================================================
# Helpers
# ====================================================================

def _sign_idx(name):
    return jp.SIGNS.index(name)


def _planet_house(planet_chain, lagna_si):
    """Whole-sign house (1-12) of a planet, measured from the chart Lagna sign."""
    return jp.house_of(_sign_idx(planet_chain["sign"]), lagna_si)


def _owned_houses(planet, lagna_si):
    """Houses (1-12) ruled by `planet` given the chart Lagna sign."""
    out = []
    for sign_i, lord in enumerate(jp.SIGN_LORDS):
        if lord == planet:
            out.append(jp.house_of(sign_i, lagna_si))
    return sorted(out)


def _occupied_houses(planet, planets, lagna_si):
    """House occupied by `planet` (Rahu/Ketu can occupy; have no ownership)."""
    if planet in planets:
        return [_planet_house(planets[planet], lagna_si)]
    return []


def _csl_verdict(csl_signifies, primary, positive, negative):
    """Deterministic CSL gate verdict for one cusp's sub-lord signification."""
    sig = set(csl_signifies)
    hits_pos = sorted(sig & set(positive))
    hits_neg = sorted(sig & set(negative))
    if hits_pos and not hits_neg:
        verdict = "favourable"
    elif hits_neg and not hits_pos:
        verdict = "unfavourable"
    elif hits_pos and hits_neg:
        verdict = "mixed (check sub-sub-lord)"
    else:
        verdict = "neutral (signifies neither set)"
    return {"signifies_positive": hits_pos, "signifies_negative": hits_neg,
            "verdict": verdict}


# ====================================================================
# Significators — 4-level KP scheme
# ====================================================================

def compute_significators(planets, cusps, lagna_si):
    """For every house 1-12, return the L1/L2/L3/L4 significator lists.

    L1 — planets in the STAR of the planet OCCUPYING that house  (strongest)
    L2 — planets OCCUPYING that house
    L3 — planets in the STAR of the LORD of that house
    L4 — the LORD of that house                                   (weakest)
    Rahu/Ketu conjoining a house's occupant are added to that house.
    """
    # Map each house -> planets occupying it.
    house_occupants = {h: [] for h in range(1, 13)}
    for p, chain in planets.items():
        house_occupants[_planet_house(chain, lagna_si)].append(p)

    significators = {}
    for h in range(1, 13):
        cusp_sign_i = _sign_idx(cusps[h - 1]["sign"])
        house_lord = jp.SIGN_LORDS[cusp_sign_i]
        occupants = house_occupants[h]

        # L1 — planets in the star of any occupant.
        l1 = [p for p, c in planets.items()
              if c["star_lord"] in occupants and p not in occupants]
        # L2 — the occupants themselves.
        l2 = list(occupants)
        # L3 — planets in the star of the house lord.
        l3 = [p for p, c in planets.items() if c["star_lord"] == house_lord]
        # L4 — the house lord.
        l4 = [house_lord]

        # Node conjunction: Rahu/Ketu sharing a house with an occupant join it.
        for node in ("Rahu", "Ketu"):
            if node in occupants and node not in l2:
                l2.append(node)

        significators[str(h)] = {
            "house_lord": house_lord,
            "occupants": occupants,
            "L1_in_star_of_occupant": sorted(set(l1)),
            "L2_occupants": sorted(set(l2)),
            "L3_in_star_of_lord": sorted(set(l3)),
            "L4_house_lord": l4,
        }
    return significators


def planet_signifies_houses(planet, planets, cusps, lagna_si):
    """Houses a planet signifies = (star-lord's owned+occupied) then (own
    owned+occupied). Star-lord effects rank above own effects in KP."""
    houses = set()
    if planet in planets:
        star_lord = planets[planet]["star_lord"]
        houses |= set(_owned_houses(star_lord, lagna_si))
        houses |= set(_occupied_houses(star_lord, planets, lagna_si))
    houses |= set(_owned_houses(planet, lagna_si))
    houses |= set(_occupied_houses(planet, planets, lagna_si))
    return sorted(houses)


# ====================================================================
# Ruling Planets — ported from compute_ruling_planets.py
# ====================================================================

def compute_ruling_planets(rp_lagna_chain, moon_chain, day_lord_planet,
                           planets):
    """Build the 7-factor RP set from the REAL rising Lagna (NOT the horary
    Lagna), the Moon, and the Day lord. Dedup in strength order, apply
    retrograde exclusion + Rahu/Ketu agent rule. Returns a full breakdown."""
    # 7 factors in Krishnamurti strength order.
    factors = [
        ("Lagna Sub Lord",  rp_lagna_chain["sub_lord"]),
        ("Lagna Star Lord", rp_lagna_chain["star_lord"]),
        ("Lagna Sign Lord", rp_lagna_chain["sign_lord"]),
        ("Moon Sub Lord",   moon_chain["sub_lord"]),
        ("Moon Star Lord",  moon_chain["star_lord"]),
        ("Moon Sign Lord",  moon_chain["sign_lord"]),
        ("Day Lord",        day_lord_planet),
    ]

    # Deduplicate, preserving strongest-first order; record every role.
    roles = {}
    dedup = []
    for role, planet in factors:
        roles.setdefault(planet, []).append(role)
        if planet not in dedup:
            dedup.append(planet)

    # Retrograde check. A retrograde planet (not a node) is excluded UNLESS
    # its sign-lord (depositor) is itself in the RP set.
    retrograde_check = {}
    retained = []
    for planet in dedup:
        if planet in ("Rahu", "Ketu"):
            retrograde_check[planet] = "node — retrograde rule N/A"
            retained.append(planet)
            continue
        retro = planets.get(planet, {}).get("retrograde", False)
        if not retro:
            retrograde_check[planet] = "direct — retained"
            retained.append(planet)
            continue
        depositor = planets[planet]["sign_lord"]
        if depositor in dedup:
            retrograde_check[planet] = (
                f"retrograde — RETAINED (depositor {depositor} is RP)")
            retained.append(planet)
        else:
            retrograde_check[planet] = (
                f"retrograde — EXCLUDED (depositor {depositor} not RP)")

    # Rahu/Ketu agent rule. A node joins (or strengthens) the RP set if it is
    # in a sign owned by an RP planet, conjunct an RP planet, or in the star
    # of an RP planet.
    node_check = {}
    final_rp = list(retained)
    for node in ("Rahu", "Ketu"):
        if node not in planets:
            continue
        nchain = planets[node]
        node_house_sign = nchain["sign_lord"]
        node_star = nchain["star_lord"]
        node_si = _sign_idx(nchain["sign"])
        conjunct = [p for p, c in planets.items()
                    if p != node and _sign_idx(c["sign"]) == node_si]
        reasons = []
        if node_house_sign in retained:
            reasons.append(f"in sign of RP {node_house_sign}")
        if node_star in retained:
            reasons.append(f"in star of RP {node_star}")
        conj_rp = [p for p in conjunct if p in retained]
        if conj_rp:
            reasons.append(f"conjunct RP {', '.join(conj_rp)}")
        eligible = bool(reasons)
        node_check[node] = {
            "sign": nchain["sign"], "sign_lord": node_house_sign,
            "star_lord": node_star, "conjunct": conjunct,
            "eligible_as_rp": eligible, "reasons": reasons}
        if eligible and node not in final_rp:
            final_rp.append(node)

    return {
        "rp_lagna_note": "computed from the REAL rising sign at question "
                         "time+place — NOT the 1-249 horary Lagna",
        "factors_in_strength_order": [{"role": r, "planet": p}
                                      for r, p in factors],
        "roles_by_planet": roles,
        "deduplicated_strength_order": dedup,
        "retrograde_check": retrograde_check,
        "node_agent_check": node_check,
        "final_rp_set": final_rp,
        "strongest_rp": factors[0][1],
    }


# ====================================================================
# Main
# ====================================================================

def build_baseline(number, dt_iso, tz, lat, lon, question):
    chart = eph.kp_horary_chart(number, dt_iso, tz, lat, lon)

    horary_lagna = chart["horary_lagna"]
    cusps = chart["cusps"]
    planets = chart["planets"]
    rp_lagna_chain = chart["ruling_planets_lagna"]

    lagna_si = _sign_idx(cusps[0]["sign"])

    # CSL per cusp — the sub-lord IS the CSL; surface it explicitly.
    cusps_out = []
    for c in cusps:
        c2 = dict(c)
        c2["cuspal_sub_lord"] = c["sub_lord"]
        cusps_out.append(c2)

    # Day lord (Vedic weekday at sunrise of the question's place).
    _local, utc = eph.to_utc(dt_iso, tz)
    jd = eph.julian_day(utc)
    day_lord_planet, sunrise_dt = eph.day_lord(jd, lat, lon)

    # Ruling Planets — built from the REAL rising Lagna.
    ruling_planets = compute_ruling_planets(
        rp_lagna_chain, planets["Moon"], day_lord_planet, planets)
    ruling_planets["day_lord"] = {
        "planet": day_lord_planet,
        "sunrise_utc": sunrise_dt.isoformat(),
        "weekday_at_sunrise": sunrise_dt.strftime("%A"),
    }

    # 4-level significators for all 12 houses.
    significators = compute_significators(planets, cusps, lagna_si)

    # Houses each planet signifies (for the interpreting agent's CSL gate).
    planet_significations = {
        p: planet_signifies_houses(p, planets, cusps, lagna_si)
        for p in planets
    }

    # Pre-computed CSL gate verdict per house, scored against the GENERIC
    # fruitful/barren sets (question-specific gating is done by the agent
    # using HOUSE_COMBINATIONS).
    csl_generic_gate = {}
    for h in range(1, 13):
        csl = cusps[h - 1]["sub_lord"]
        csl_generic_gate[str(h)] = _csl_verdict(
            planet_significations.get(csl, []),
            [h], FRUITFUL_HOUSES, BARREN_HOUSES)

    return {
        "chart_type": "kp_horary_baseline",
        "input": {
            "number": number,
            "datetime_local": chart["datetime_local"],
            "datetime_utc": chart["datetime_utc"],
            "timezone": tz, "latitude": lat, "longitude": lon,
            "question": question,
        },
        "ayanamsa": chart["ayanamsa"],
        "house_system": chart["house_system"],
        "two_lagna_note": (
            "CHART Lagna = horary_lagna (from the 1-249 number; drives cusps "
            "and significators). RP Lagna = ruling_planets.rp_lagna (the REAL "
            "rising sign at question time+place; drives Ruling Planets only). "
            "Never mix them."),
        "horary_lagna": horary_lagna,
        "rp_lagna": rp_lagna_chain,
        "cusps": cusps_out,
        "planets": planets,
        "ruling_planets": ruling_planets,
        "significators": significators,
        "planet_significations": planet_significations,
        "csl_generic_gate": csl_generic_gate,
        "fruitful_barren_houses": {
            "fruitful": FRUITFUL_HOUSES, "barren_dusthana": BARREN_HOUSES},
        "dasha": chart["dasha"],
        "house_combinations": HOUSE_COMBINATIONS,
    }


def main():
    ap = argparse.ArgumentParser(
        description="KP Horary deterministic baseline computer.")
    ap.add_argument("--number", type=int, required=True,
                    help="Horary number 1-249")
    ap.add_argument("--datetime", required=True,
                    help="ISO datetime — the moment the question is asked")
    ap.add_argument("--tz", required=True, help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--question", default="(no question provided)")
    args = ap.parse_args()

    if not 1 <= args.number <= 249:
        sys.stderr.write("ERROR: --number must be 1-249.\n")
        sys.exit(1)
    try:
        datetime.fromisoformat(args.datetime)
    except ValueError:
        sys.stderr.write("ERROR: --datetime must be ISO format.\n")
        sys.exit(1)

    baseline = build_baseline(args.number, args.datetime, args.tz,
                              args.lat, args.lon, args.question)
    print(json.dumps(baseline, indent=2, default=str))


if __name__ == "__main__":
    main()
