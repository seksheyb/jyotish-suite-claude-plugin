#!/usr/bin/env python3
"""
Jaimini baseline — deterministic computation for the jaimini-astrology skill.

Offloads pure calculation out of the skill prompt: Chara Karakas (Sapta scheme),
Arudha Padas (with the same-sign / 7th-from exception), Swamsha / Karakamsha,
Argala on key signs, Chara Dasha (Parashara variant) and the 12x12 Jaimini Rasi
Drishti map. Pure school-specific math; everything generic comes from lib/.

Usage:
  compute_jaimini_baseline.py --datetime "1991-07-30T10:20:00" --tz "Asia/Kolkata" \
                              --lat 28.6139 --lon 77.2090 [--age 33] [--target-date 2026-05-21]
  compute_jaimini_baseline.py --chart chart.json [--age 33]
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402

SAPTA = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
KARAKA_NAMES = [
    ("AK", "Atmakaraka"), ("AmK", "Amatyakaraka"), ("BK", "Bhratrukaraka"),
    ("MK", "Matrukaraka"), ("PK", "Putrakaraka"), ("GK", "Gnatikaraka"),
    ("DK", "Darakaraka"),
]


# ====================================================================
# Jaimini Rasi Drishti — 12x12 sign-aspect map
# ====================================================================

def build_drishti_map():
    """Precompute the full 12x12 Jaimini Rasi Drishti map.

    Movable aspects all Fixed except the next zodiacal Fixed sign (which is the
    sign immediately after it, n=2); Fixed aspects all Movable except the next
    zodiacal Movable sign (n=3 from a Fixed sign, since the n=2 sign is Dual);
    Dual aspects all other Dual signs. The adjacent-sign exception breaks mutual
    symmetry, leaving four one-way aspects (Taurus->Aries, Leo->Cancer,
    Scorpio->Libra, Aquarius->Capricorn). The map records directional aspects.
    """
    aspects = {i: [] for i in range(12)}
    for a in range(12):
        qa = jp.SIGN_QUALITY[a]
        for b in range(12):
            if a == b:
                continue
            qb = jp.SIGN_QUALITY[b]
            if qa == "Dual":
                if qb == "Dual":
                    aspects[a].append(b)
            elif qa == "Movable" and qb == "Fixed":
                if jp.sign_n_from(a, 2) != b:        # skip next Fixed (n=2)
                    aspects[a].append(b)
            elif qa == "Fixed" and qb == "Movable":
                if jp.sign_n_from(a, 3) != b:        # skip next Movable (n=3)
                    aspects[a].append(b)
    # matrix[a][b] == 1 means sign a aspects sign b
    matrix = [[1 if b in aspects[a] else 0 for b in range(12)] for a in range(12)]
    one_way = []
    for a in range(12):
        for b in range(12):
            if matrix[a][b] and not matrix[b][a]:
                one_way.append({"from": jp.SIGNS[a], "to": jp.SIGNS[b]})
    return {
        "matrix": matrix,
        "by_sign": {jp.SIGNS[a]: [jp.SIGNS[b] for b in aspects[a]] for a in range(12)},
        "one_way": one_way,
    }


DRISHTI = build_drishti_map()


# ====================================================================
# Chara Karakas (Sapta scheme — 7 planets, Rahu excluded)
# ====================================================================

def compute_chara_karakas(d1_planets):
    """Rank the 7 visible planets by descending degree-within-sign.

    Rahu/Ketu are excluded from the Sapta (7-karaka) ranking. Tiebreaker:
    finer degree wins (already captured by full decimal degree)."""
    ranked = sorted(
        SAPTA,
        key=lambda p: d1_planets[p]["deg_in_sign"],
        reverse=True,
    )
    out = {}
    for i, (abbr, full) in enumerate(KARAKA_NAMES):
        p = ranked[i]
        out[abbr] = {
            "name": full,
            "planet": p,
            "degree_in_sign": round(d1_planets[p]["deg_in_sign"], 4),
            "sign": d1_planets[p]["sign"],
        }
    # close-degree flags (adjacent karakas within 1 deg)
    close = []
    for i in range(len(KARAKA_NAMES) - 1):
        a, b = KARAKA_NAMES[i][0], KARAKA_NAMES[i + 1][0]
        gap = abs(out[a]["degree_in_sign"] - out[b]["degree_in_sign"])
        if gap <= 1.0:
            close.append({"karakas": [a, b], "gap_deg": round(gap, 4)})
    out["_close_degree_flags"] = close
    return out


# ====================================================================
# Arudha Padas
# ====================================================================

def compute_arudha(house_sign_idx, planet_sign_lookup):
    """Arudha Pada of a house sign.

    Count from the house sign to its lord's sign (N), then N signs again from
    the lord's sign. Exception: if the result lands in the same sign as the
    house or the 7th from it, use the 10th sign from the house instead."""
    lord = jp.SIGN_LORDS[house_sign_idx]
    lord_sign_idx = planet_sign_lookup[lord]
    n = jp.count_signs(house_sign_idx, lord_sign_idx)
    arudha_idx = jp.sign_n_from(lord_sign_idx, n)
    seventh = jp.sign_n_from(house_sign_idx, 7)
    exception = False
    if arudha_idx == house_sign_idx or arudha_idx == seventh:
        arudha_idx = jp.sign_n_from(house_sign_idx, 10)
        exception = True
    return arudha_idx, exception


def compute_all_arudhas(lagna_sign_idx, planet_sign_lookup):
    """AL plus A2..A12 and UL (=A12). Each keyed by abbreviation."""
    # house number -> Arudha label
    labels = {1: "AL", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6",
              7: "A7", 8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "UL"}
    signifies = {
        "AL": "Self-image, social identity",
        "A2": "Wealth manifestation, family image",
        "A3": "Efforts, skills, communication image",
        "A4": "Home, comforts, mother image",
        "A5": "Children, creativity, merit image",
        "A6": "Enemies, debts, service image",
        "A7": "Business partnerships, spouse image",
        "A8": "Transformation, longevity image",
        "A9": "Fortune, dharma, guru image",
        "A10": "Career image, public reputation",
        "A11": "Gains, networks, desire fulfilment",
        "UL": "Marriage, committed partnerships",
    }
    out = {}
    for house_num in range(1, 13):
        house_sign_idx = jp.sign_n_from(lagna_sign_idx, house_num)
        arudha_idx, exc = compute_arudha(house_sign_idx, planet_sign_lookup)
        label = labels[house_num]
        out[label] = {
            "house": house_num,
            "house_sign": jp.SIGNS[house_sign_idx],
            "sign": jp.SIGNS[arudha_idx],
            "sign_idx": arudha_idx,
            "exception_applied": exc,
            "signifies": signifies[label],
        }
    return out


# ====================================================================
# Swamsha / Karakamsha
# ====================================================================

def compute_swamsha(ak_planet, d1_planets, d9):
    """Swamsha = AK's sign in D9. Karakamsha = that sign as Lagna in D1."""
    swamsha_sign = d9["planets"][ak_planet]              # D9 sign of AK
    swamsha_idx = jp.SIGNS.index(swamsha_sign)
    return {
        "atmakaraka": ak_planet,
        "ak_d1_sign": d1_planets[ak_planet]["sign"],
        "swamsha_sign": swamsha_sign,
        "swamsha_sign_idx": swamsha_idx,
        "karakamsha_lagna_d1": swamsha_sign,
        "d9_lagna_sign": d9["lagna_sign"],
        "note": "Swamsha = AK's D9 sign; Karakamsha Lagna = Swamsha sign read "
                "as Lagna in D1.",
    }


# ====================================================================
# Argala
# ====================================================================

def compute_argala(ref_sign_idx, occupancy):
    """Argala from 2/4/11 (+5 secondary) vs Virodha from 12/10/3 (+9).

    `occupancy` maps sign_idx -> list of planet names. Argala on a position is
    effective only when its planet-count strictly exceeds the obstructing
    Virodha planet-count."""
    pairs = [
        ("2nd", 2, "12th", 12, "primary"),
        ("4th", 4, "10th", 10, "primary"),
        ("11th", 11, "3rd", 3, "primary"),
        ("5th", 5, "9th", 9, "secondary"),
    ]
    result = {}
    for arg_name, arg_n, vir_name, vir_n, kind in pairs:
        arg_idx = jp.sign_n_from(ref_sign_idx, arg_n)
        vir_idx = jp.sign_n_from(ref_sign_idx, vir_n)
        arg_planets = occupancy.get(arg_idx, [])
        vir_planets = occupancy.get(vir_idx, [])
        if not arg_planets:
            net = "no_argala"
        elif len(arg_planets) > len(vir_planets):
            net = "effective"
        elif len(arg_planets) == len(vir_planets):
            net = "cancelled"
        else:
            net = "obstructed"
        result[arg_name] = {
            "kind": kind,
            "argala_sign": jp.SIGNS[arg_idx],
            "argala_planets": arg_planets,
            "virodha_position": vir_name,
            "virodha_sign": jp.SIGNS[vir_idx],
            "virodha_planets": vir_planets,
            "net": net,
        }
    return result


# ====================================================================
# Chara Dasha — Parashara variant
# ====================================================================

def jaimini_sign_lord(sign_idx, d1_planets):
    """Jaimini lord of a sign. For dual-lordship signs (Scorpio: Mars/Ketu,
    Aquarius: Saturn/Rahu) the stronger lord is chosen: the lord placed in its
    own sign or exalted, else the one in a Kendra/Trikona from itself's
    occupancy; default to the primary lord."""
    if sign_idx == 7:        # Scorpio
        candidates = [("Mars", d1_planets["Mars"]), ("Ketu", d1_planets["Ketu"])]
    elif sign_idx == 10:     # Aquarius
        candidates = [("Saturn", d1_planets["Saturn"]), ("Rahu", d1_planets["Rahu"])]
    else:
        return jp.SIGN_LORDS[sign_idx]

    def strength(name, info):
        s = 0
        psi = jp.SIGNS.index(info["sign"])
        # own sign
        if name in jp.OWN_SIGNS and psi in jp.OWN_SIGNS[name]:
            s += 3
        # exalted
        if name in jp.EXALTATION and jp.EXALTATION[name][0] == psi:
            s += 4
        # Kendra/Trikona from the sign being lorded
        house = jp.count_signs(sign_idx, psi)
        if house in (1, 4, 7, 10):
            s += 2
        elif house in (5, 9):
            s += 1
        return s

    best = max(candidates, key=lambda c: strength(c[0], c[1]))
    return best[0]


def chara_dasha_years(sign_idx, d1_planets):
    """Dasha years for a sign = signs counted from the sign to its lord's sign
    (zodiacal, exclusive of start). Lord in same sign -> 12 years.
    Count > 12 -> count - 12."""
    lord = jaimini_sign_lord(sign_idx, d1_planets)
    lord_sign_idx = jp.SIGNS.index(d1_planets[lord]["sign"])
    if lord_sign_idx == sign_idx:
        return 12, lord
    # count_signs is inclusive (itself=1); steps forward = count - 1
    count = jp.count_signs(sign_idx, lord_sign_idx) - 1
    if count == 0:
        years = 12
    elif count > 12:
        years = count - 12
    else:
        years = count
    return years, lord


def compute_chara_dasha(lagna_sign_idx, lagna_deg, d1_planets, birth_dt):
    """Full Chara Dasha (Parashara variant) sequence of 12 rasis."""
    quality = jp.SIGN_QUALITY[lagna_sign_idx]
    if quality == "Movable":
        start_idx, direction = lagna_sign_idx, 1
    elif quality == "Fixed":
        start_idx, direction = lagna_sign_idx, -1
    else:  # Dual
        start_idx, direction = jp.sign_n_from(lagna_sign_idx, 9), 1

    # ordered list of 12 rasi indices
    order = [(start_idx + direction * k) % 12 for k in range(12)]

    # birth balance for the first sign
    first_years, _ = chara_dasha_years(order[0], d1_planets)
    elapsed = (lagna_deg / 30.0) * first_years
    balance_first = first_years - elapsed

    from datetime import timedelta
    sequence = []
    cursor_dt = birth_dt  # may be None if the chart carries no birth datetime
    age_cursor = 0.0
    for k, sidx in enumerate(order):
        full_years, lord = chara_dasha_years(sidx, d1_planets)
        years = balance_first if k == 0 else float(full_years)
        end_dt = (cursor_dt + timedelta(days=years * jp.YEAR_DAYS)
                  if cursor_dt is not None else None)
        sequence.append({
            "rasi": jp.SIGNS[sidx],
            "rasi_idx": sidx,
            "jaimini_lord": lord,
            "full_years": full_years,
            "years": round(years, 4),
            "start": cursor_dt.isoformat() if cursor_dt is not None else None,
            "end": end_dt.isoformat() if end_dt is not None else None,
            "start_age": round(age_cursor, 3),
            "end_age": round(age_cursor + years, 3),
        })
        cursor_dt = end_dt
        age_cursor += years
    return {
        "lagna_quality": quality,
        "direction": "zodiacal" if direction == 1 else "anti-zodiacal",
        "starting_rasi": jp.SIGNS[start_idx],
        "first_sign_full_years": first_years,
        "first_sign_balance_years": round(balance_first, 4),
        "sequence": sequence,
    }


def find_running_dasha(chara_dasha, target_dt=None, age=None):
    """Return the running rasi dasha at a target date or age, or None."""
    seq = chara_dasha["sequence"]
    if target_dt is not None and seq and seq[0]["start"] is not None:
        for d in seq:
            if datetime.fromisoformat(d["start"]) <= target_dt < datetime.fromisoformat(d["end"]):
                return d
    if age is not None:
        for d in seq:
            if d["start_age"] <= age < d["end_age"]:
                return d
    return None


# ====================================================================
# Planet detail block (degree flags, dignity, war)
# ====================================================================

def build_planet_block(d1_planets):
    """Per-planet sign / deg / navamsa / dignity / degree flags / war."""
    positions = {p: d1_planets[p]["longitude"] for p in d1_planets}
    wars = jp.planetary_war(positions)
    sun_lon = d1_planets["Sun"]["longitude"]
    out = {}
    for p, info in d1_planets.items():
        lon = info["longitude"]
        flags = jp.degree_flags(p, lon, sun_lon=sun_lon,
                                retrograde=info.get("retrograde", False))
        in_war = next((w for w in wars
                       if w["winner"] == p or w["loser"] == p), None)
        out[p] = {
            "sign": info["sign"],
            "deg_in_sign": round(info["deg_in_sign"], 4),
            "navamsa_sign": info["navamsa_sign"],
            "dignity": info["dignity"],
            "retrograde": info.get("retrograde", False),
            "degree_flags": flags,
            "planetary_war": in_war,
        }
    return out, wars


# ====================================================================
# Chart loading / normalisation
# ====================================================================

def load_chart(args):
    """Return a parashari_natal_chart-shaped dict from file or ephemeris."""
    if args.chart:
        with open(args.chart) as f:
            return json.load(f)
    if not all([args.datetime, args.tz, args.lat is not None, args.lon is not None]):
        sys.exit("ERROR: provide --chart, or all of --datetime --tz --lat --lon")
    return eph.parashari_natal_chart(args.datetime, args.tz, args.lat, args.lon)


def main():
    ap = argparse.ArgumentParser(description="Jaimini deterministic baseline")
    ap.add_argument("--datetime", help="ISO local datetime, e.g. 1991-07-30T10:20:00")
    ap.add_argument("--tz", help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lon", type=float)
    ap.add_argument("--chart", help="JSON chart file (parashari_natal shape)")
    ap.add_argument("--age", type=float, help="age in years for running Chara Dasha")
    ap.add_argument("--target-date", help="ISO date for running Chara Dasha")
    args = ap.parse_args()

    chart = load_chart(args)
    d1 = chart["d1"]
    d9 = chart["d9"]
    d1_planets = d1["planets"]

    lagna_sign_idx = jp.SIGNS.index(d1["lagna_sign"])
    # lagna degree within sign from the DMS string "DDD-MM-SS"
    dms = d1["lagna_longitude_dms"].split("-")
    lagna_lon = int(dms[0]) + int(dms[1]) / 60 + int(dms[2]) / 3600
    lagna_deg = lagna_lon % 30.0

    # planet -> D1 sign index (for Arudha + dasha lord lookups)
    planet_sign_lookup = {p: jp.SIGNS.index(d1_planets[p]["sign"]) for p in d1_planets}
    # sign occupancy for Argala
    occupancy = {}
    for p in d1_planets:
        occupancy.setdefault(planet_sign_lookup[p], []).append(p)

    # --- Chara Karakas ---
    karakas = compute_chara_karakas(d1_planets)
    ak_planet = karakas["AK"]["planet"]

    # --- Arudha Padas ---
    arudhas = compute_all_arudhas(lagna_sign_idx, planet_sign_lookup)

    # --- Swamsha / Karakamsha ---
    swamsha = compute_swamsha(ak_planet, d1_planets, d9)

    # --- Argala on AL, UL, Swamsha, A10 ---
    argala = {}
    for key, sidx in [
        ("AL", arudhas["AL"]["sign_idx"]),
        ("UL", arudhas["UL"]["sign_idx"]),
        ("A10", arudhas["A10"]["sign_idx"]),
        ("Swamsha", swamsha["swamsha_sign_idx"]),
        ("Lagna", lagna_sign_idx),
    ]:
        argala[key] = {"reference_sign": jp.SIGNS[sidx],
                       "positions": compute_argala(sidx, occupancy)}

    # --- Chara Dasha ---
    # A pasted chart may carry no birth datetime; Chara Dasha then runs on
    # ages only (start/end dates null) — still fully usable with --age.
    dt_local = chart.get("datetime_local")
    birth_dt = None
    if dt_local:
        birth_dt = datetime.fromisoformat(dt_local)
        if birth_dt.tzinfo is not None:
            birth_dt = birth_dt.replace(tzinfo=None)
    chara_dasha = compute_chara_dasha(lagna_sign_idx, lagna_deg, d1_planets, birth_dt)
    target_dt = datetime.fromisoformat(args.target_date) if args.target_date else None
    running = find_running_dasha(chara_dasha, target_dt=target_dt, age=args.age)
    chara_dasha["running"] = running

    # --- Planets detail ---
    planets, wars = build_planet_block(d1_planets)

    out = {
        "chart_meta": {
            "datetime_local": chart["datetime_local"],
            "datetime_utc": chart["datetime_utc"],
            "location": chart["location"],
            "lagna_sign": d1["lagna_sign"],
            "lagna_deg_in_sign": round(lagna_deg, 4),
            "lagna_quality": jp.SIGN_QUALITY[lagna_sign_idx],
            "d9_lagna_sign": d9["lagna_sign"],
        },
        "chara_karakas": karakas,
        "arudha_padas": arudhas,
        "swamsha": swamsha,
        "karakamsha": {
            "karakamsha_lagna_d1": swamsha["karakamsha_lagna_d1"],
            "co_occupants_d1": occupancy.get(swamsha["swamsha_sign_idx"], []),
        },
        "argala": argala,
        "chara_dasha": chara_dasha,
        "jaimini_drishti_map": DRISHTI,
        "planets": planets,
        "planetary_wars": wars,
        "vimshottari_dasha": chart.get("dasha", {}).get("running"),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
