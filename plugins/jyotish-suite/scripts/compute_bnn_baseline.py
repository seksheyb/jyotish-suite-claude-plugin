#!/usr/bin/env python3
"""
Deterministic baseline for the BNN (Bhrigu Nadi / Brighu Nadi) astrology skill.

Offloads pure calculation out of the skill prompt. BNN reads everything
relative to each natural Karaka planet's SIGN (not the Lagna): flow positions
(2nd & 12th from Karaka), trine support (5th & 9th), growth positions
(3rd & 11th) and opposition (7th). All sign arithmetic uses jp.sign_n_from /
jp.count_signs. Output is one JSON object to stdout.
"""

import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402

# ---------------------------------------------------------------------------
# BNN-specific fixed tables (karaka-tables.md 1A, 1B, 1C)
# ---------------------------------------------------------------------------

# 1A — Natural Karaka assignments. role = the BNN signification of the planet.
NATURAL_KARAKAS = {
    "Sun":     {"primary": "Soul, self, father, authority, government, vitality",
                "secondary": "King, employer, leadership, heart"},
    "Moon":    {"primary": "Mother, mind, emotions, public, masses, travel",
                "secondary": "Comfort, popularity, home, food"},
    "Mars":    {"primary": "Siblings (younger), property, land, energy, courage, disputes",
                "secondary": "Brothers, debt, enemies, blood, engineering"},
    "Mercury": {"primary": "Intellect, communication, business, friends, skin",
                "secondary": "Writing, speech, trade, nervous system"},
    "Jupiter": {"primary": "Wisdom, children, wealth, husband (female charts), teacher, dharma",
                "secondary": "Fortune, expansion, religion, higher learning"},
    "Venus":   {"primary": "Wife/partner (male charts), vehicles, comforts, arts, relationships",
                "secondary": "Reproductive system, pleasures, luxury, marriage"},
    "Saturn":  {"primary": "Longevity, discipline, service, career (labour-based), delays",
                "secondary": "Servants, iron, chronic illness, old age, death"},
    "Rahu":    {"primary": "Foreign, unconventional, obsession, technology",
                "secondary": "Deception, amplification, sudden events"},
    "Ketu":    {"primary": "Liberation, past life, spirituality, detachment",
                "secondary": "Accidents, wounds, moksha, occult, hidden matters"},
}

# 1B — Sign field / domain.
SIGN_FIELD = {
    "Aries": "Self, initiative, beginnings, courage, independence",
    "Taurus": "Wealth, food, stability, accumulated resources, beauty",
    "Gemini": "Communication, siblings, short journeys, intellect, trade",
    "Cancer": "Home, mother, emotions, water, comfort, nurturing",
    "Leo": "Authority, father, government, confidence, leadership",
    "Virgo": "Service, health, enemies, debts, analysis, daily work",
    "Libra": "Partnerships, trade, legal matters, relationships, balance",
    "Scorpio": "Transformation, secrets, inheritance, occult, hidden matters",
    "Sagittarius": "Dharma, higher learning, fortune, philosophy, long travel",
    "Capricorn": "Career, discipline, structure, public duty, ambition",
    "Aquarius": "Gains, networks, elder siblings, innovation, social causes",
    "Pisces": "Liberation, foreign, spirituality, expenses, dissolution",
}

# 1C — Natural planet relationships (BNN — includes Rahu/Ketu).
BNN_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus", "Rahu"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn", "Rahu"],
    "Saturn": ["Mercury", "Venus", "Rahu"],
    "Rahu": ["Mercury", "Venus", "Saturn"],
    "Ketu": ["Mars", "Venus"],
}
BNN_ENEMIES = {
    "Sun": ["Venus", "Saturn", "Rahu", "Ketu"],
    "Moon": ["Rahu", "Ketu"],
    "Mars": ["Mercury", "Rahu"],
    "Mercury": ["Moon", "Ketu"],
    "Jupiter": ["Mercury", "Venus", "Rahu", "Ketu"],
    "Venus": ["Sun", "Moon", "Ketu"],
    "Saturn": ["Sun", "Moon", "Mars", "Ketu"],
    "Rahu": ["Sun", "Moon", "Ketu"],
    "Ketu": ["Sun", "Moon", "Jupiter", "Rahu"],
}


def relationship(karaka, other):
    """BNN natural relationship of `other` toward the reference `karaka`."""
    if other == karaka:
        return "self"
    if other in BNN_FRIENDS.get(karaka, []):
        return "friend"
    if other in BNN_ENEMIES.get(karaka, []):
        return "enemy"
    return "neutral"


# BNN aspects (aspects.md): every planet aspects 7th; specials added.
# Rahu/Ketu apply 5th & 9th in BNN.
BNN_SPECIAL_ASPECTS = {
    "Mars": [4, 8], "Jupiter": [5, 9], "Saturn": [3, 10],
    "Rahu": [5, 9], "Ketu": [5, 9],
}


def orb_class(orb):
    """aspects.md orb framework."""
    if orb is None:
        return "n/a"
    if orb <= 3.0:
        return "tight"
    if orb <= 7.0:
        return "moderate"
    return "loose"


# ---------------------------------------------------------------------------
# Degree-flag priority verdict (degree-flags.md priority table)
# ---------------------------------------------------------------------------

def priority_verdict(flags, dignity, retrograde, war_status):
    """Resolve the dominating degree flag per the degree-flags.md hierarchy.
    Returns {dominant, code, color, note}. Combustion trumps all; Mrityu Bhaga
    overrides dignity; Planetary War (defeated) suppresses."""
    combust = flags.get("combust", False)
    if combust:
        return {"dominant": "combustion", "code": "Cb", "color": "red",
                "note": "Combust — suppressed delivery; dominates all other flags."}
    if war_status == "defeated":
        note = "Defeated in Planetary War — themes weakened chart-wide."
        if flags.get("pushkara_bhaga") or flags.get("pushkara_navamsa"):
            note += " Pushkara helps but does not fully override."
        return {"dominant": "planetary_war_defeated", "code": "PW", "color": "red",
                "note": note}
    if flags.get("mrityu_bhaga"):
        note = "Mrityu Bhaga — struggles to deliver; overrides sign dignity."
        if dignity == "exalted":
            note = "Mrityu Bhaga + exalted — MB overrides; struggles despite dignity."
        if retrograde:
            note = "Mrityu Bhaga + retrograde — double suppression; weakened and non-linear."
        return {"dominant": "mrityu_bhaga", "code": "MB", "color": "red", "note": note}
    if flags.get("gandanta"):
        return {"dominant": "gandanta", "code": "Gd", "color": "red",
                "note": "Gandanta — karmically charged; results come through difficulty."}
    pushkara = flags.get("pushkara_bhaga") or flags.get("pushkara_navamsa")
    if flags.get("vargottama") and pushkara:
        return {"dominant": "vargottama_pushkara", "code": "Vo+PK", "color": "green",
                "note": "Vargottama + Pushkara — exceptional, soul-endorsed delivery."}
    if flags.get("sandhi") and pushkara:
        return {"dominant": "sandhi_pushkara", "code": "Sd+PK", "color": "yellow",
                "note": "Sandhi + Pushkara — instability partially offset; inconsistent but possible."}
    if pushkara:
        note = "Pushkara — empowered; delivers with ease."
        if retrograde:
            note = "Pushkara + retrograde — empowered but internalized or delayed."
        return {"dominant": "pushkara", "code": "PK", "color": "green", "note": note}
    if flags.get("sandhi"):
        return {"dominant": "sandhi", "code": "Sd", "color": "yellow",
                "note": "Sandhi — immature or unstable expression of themes."}
    if war_status == "close_contention":
        return {"dominant": "close_contention", "code": "CC", "color": "yellow",
                "note": "Close Contention — mutual tension; uneasy results."}
    if flags.get("vargottama"):
        return {"dominant": "vargottama", "code": "Vo", "color": "green",
                "note": "Vargottama — D1 promise soul-endorsed; operates with coherence."}
    return {"dominant": "none", "code": "-", "color": "neutral",
            "note": "No dominating degree flag."}


# ---------------------------------------------------------------------------
# Chart -> planet block
# ---------------------------------------------------------------------------

def build_planets(chart):
    """Per-planet block: sign, deg, dignity, retro, degree flags, war, verdict."""
    d1 = chart["d1"]["planets"]
    sun_lon = d1["Sun"]["longitude"]
    positions = {p: d1[p]["longitude"] for p in d1}
    wars = jp.planetary_war(positions)
    war_status = {}
    war_detail = {}
    for w in wars:
        sep = w["separation"]
        if sep <= 1.0:
            war_status[w["winner"]] = war_status.get(w["winner"], "winner")
            war_status[w["loser"]] = "defeated"
            war_detail[w["loser"]] = w
            war_detail.setdefault(w["winner"], w)
        elif sep <= 5.0:
            war_status.setdefault(w["winner"], "close_contention")
            war_status.setdefault(w["loser"], "close_contention")

    out = {}
    for p, info in d1.items():
        lon = info["longitude"]
        retro = info["retrograde"]
        flags = jp.degree_flags(p, lon, sun_lon=sun_lon, retrograde=retro)
        dig = info["dignity"]
        ws = war_status.get(p)
        verdict = priority_verdict(flags, dig, retro, ws)
        out[p] = {
            "sign": info["sign"],
            "sign_idx": jp.SIGNS.index(info["sign"]),
            "deg_in_sign": info["deg_in_sign"],
            "longitude": lon,
            "dignity": dig,
            "retrograde": retro,
            "navamsa_sign": info["navamsa_sign"],
            "degree_flags": flags,
            "planetary_war": {"status": ws, "detail": war_detail.get(p)} if ws else None,
            "degree_flag_verdict": verdict,
        }
    return out


# ---------------------------------------------------------------------------
# Aspect pre-map (Parashari graha drishti across all planets)
# ---------------------------------------------------------------------------

def build_aspects(planets):
    """Full Graha Drishti pre-map. Returns per-planet list of aspected signs
    with occupants and tightest orb to any occupant."""
    by_sign = {}
    for p, pd in planets.items():
        by_sign.setdefault(pd["sign_idx"], []).append(p)

    aspects = {}
    for p, pd in planets.items():
        si = pd["sign_idx"]
        deg = pd["deg_in_sign"]
        casts = [7] + BNN_SPECIAL_ASPECTS.get(p, [])
        rows = []
        for n in sorted(set(casts)):
            tgt = jp.sign_n_from(si, n)
            occupants = []
            tightest = None
            for occ in by_sign.get(tgt, []):
                if occ == p:
                    continue
                orb = abs(deg - planets[occ]["deg_in_sign"])
                occupants.append({"planet": occ, "orb": round(orb, 4),
                                  "orb_class": orb_class(orb)})
                if tightest is None or orb < tightest:
                    tightest = orb
            rows.append({
                "aspect": n,
                "target_sign": jp.SIGNS[tgt],
                "target_sign_idx": tgt,
                "occupants": occupants,
                "tightest_orb": round(tightest, 4) if tightest is not None else None,
                "tightest_orb_class": orb_class(tightest),
            })
        aspects[p] = {"from_sign": pd["sign"], "deg_in_sign": deg, "casts": rows}

    # Mutual aspects within 3deg: A aspects B's sign AND B aspects A's sign.
    def aspected_signs(p):
        return {r["target_sign_idx"] for r in aspects[p]["casts"]}
    mutuals = []
    names = list(planets.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if planets[b]["sign_idx"] in aspected_signs(a) \
               and planets[a]["sign_idx"] in aspected_signs(b):
                orb = abs(planets[a]["deg_in_sign"] - planets[b]["deg_in_sign"])
                if orb <= 3.0:
                    mutuals.append({"planets": [a, b], "orb": round(orb, 4),
                                    "relationship": relationship(a, b)})
    return {"pre_map": aspects, "mutual_aspects": mutuals}


# ---------------------------------------------------------------------------
# Karaka-relative positions (the core BNN sign arithmetic)
# ---------------------------------------------------------------------------

# BNN position names: n places from the Karaka's sign (n=1 -> Karaka itself).
BNN_POSITIONS = {
    "flow_2nd": 2, "flow_12th": 12,
    "trine_5th": 5, "trine_9th": 9,
    "growth_3rd": 3, "growth_11th": 11,
    "opposition_7th": 7,
}


def occupants_of_sign(sign_idx, planet_signmap):
    """List planets occupying a sign index given a {planet: sign_idx} map."""
    return [p for p, si in planet_signmap.items() if si == sign_idx]


def build_karaka_positions(chart, planets):
    """For each Karaka planet, compute sign-relative positions FROM that
    Karaka's sign in both D1 and D9."""
    d1_signmap = {p: planets[p]["sign_idx"] for p in planets}
    d9_planets = chart["d9"]["planets"]  # {planet: navamsa_sign_name}
    d9_signmap = {p: jp.SIGNS.index(d9_planets[p]) for p in d9_planets}

    result = {}
    for karaka in NATURAL_KARAKAS:
        if karaka not in planets:
            continue
        k_d1 = planets[karaka]["sign_idx"]
        k_d9 = d9_signmap[karaka]
        d1_pos = {}
        d9_pos = {}
        for name, n in BNN_POSITIONS.items():
            si1 = jp.sign_n_from(k_d1, n)
            si9 = jp.sign_n_from(k_d9, n)
            d1_pos[name] = {
                "step": n,
                "sign": jp.SIGNS[si1],
                "sign_idx": si1,
                "field": SIGN_FIELD[jp.SIGNS[si1]],
                "occupants": sorted(occupants_of_sign(si1, d1_signmap)),
            }
            d9_pos[name] = {
                "step": n,
                "sign": jp.SIGNS[si9],
                "sign_idx": si9,
                "field": SIGN_FIELD[jp.SIGNS[si9]],
                "occupants": sorted(occupants_of_sign(si9, d9_signmap)),
            }
        result[karaka] = {
            "karaka_signification": NATURAL_KARAKAS[karaka]["primary"],
            "d1_sign": jp.SIGNS[k_d1],
            "d1_sign_field": SIGN_FIELD[jp.SIGNS[k_d1]],
            "d1_conjunctions": sorted(p for p in occupants_of_sign(k_d1, d1_signmap)
                                      if p != karaka),
            "d9_sign": jp.SIGNS[k_d9],
            "d9_sign_field": SIGN_FIELD[jp.SIGNS[k_d9]],
            "d9_conjunctions": sorted(p for p in occupants_of_sign(k_d9, d9_signmap)
                                      if p != karaka),
            "vargottama": k_d1 == k_d9,
            "d1_positions": d1_pos,
            "d9_positions": d9_pos,
        }
    return result


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def build_baseline(chart):
    planets = build_planets(chart)

    natural_karakas = {}
    for p, meta in NATURAL_KARAKAS.items():
        cur_sign = planets[p]["sign"] if p in planets else None
        natural_karakas[p] = {
            "primary_signification": meta["primary"],
            "secondary_signification": meta["secondary"],
            "current_sign": cur_sign,
            "current_sign_field": SIGN_FIELD.get(cur_sign) if cur_sign else None,
        }

    aspects = build_aspects(planets)
    karaka_positions = build_karaka_positions(chart, planets)
    running = chart.get("dasha", {}).get("running")

    return {
        "school": "bnn",
        "chart_meta": {
            "datetime_local": chart.get("datetime_local"),
            "datetime_utc": chart.get("datetime_utc"),
            "location": chart.get("location"),
            "ayanamsa": chart.get("ayanamsa"),
            "d1_lagna": chart["d1"]["lagna_sign"],
            "d9_lagna": chart["d9"]["lagna_sign"],
        },
        "natural_karakas": natural_karakas,
        "planets": planets,
        "karaka_positions": karaka_positions,
        "aspects": aspects,
        "dasha": {
            "starting_mahadasha": chart.get("dasha", {}).get("starting_mahadasha"),
            "balance_years": chart.get("dasha", {}).get("balance_years"),
            "running": running,
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Compute the deterministic BNN baseline.")
    ap.add_argument("--datetime", help="Local birth datetime, ISO (e.g. 1991-07-30T10:20:00)")
    ap.add_argument("--tz", help="IANA timezone (e.g. Asia/Kolkata)")
    ap.add_argument("--lat", type=float, help="Latitude")
    ap.add_argument("--lon", type=float, help="Longitude")
    ap.add_argument("--chart", help="Path to a pre-computed parashari_natal_chart JSON")
    args = ap.parse_args()

    if args.chart:
        with open(args.chart) as fh:
            chart = json.load(fh)
    else:
        if not all([args.datetime, args.tz, args.lat is not None, args.lon is not None]):
            ap.error("provide --chart, or all of --datetime --tz --lat --lon")
        chart = eph.parashari_natal_chart(args.datetime, args.tz, args.lat, args.lon)

    baseline = build_baseline(chart)
    json.dump(baseline, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
