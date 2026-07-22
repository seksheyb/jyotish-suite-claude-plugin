#!/usr/bin/env python3
"""
compute_lalkitab_baseline.py — deterministic Step-0 baseline for the
Lal Kitab astrology skill.

Lal Kitab is the heaviest of the six skills — roughly three-quarters of its
diagnostic work is mechanical. This script offloads ALL of that:

  * Fixed-house re-mapping   — Aries is always house 1 (sign index + 1).
  * Pakka ghar + dignity     — Lal Kitab's OWN by-house exalt/debil/friend
                               tables (NOT Parashari).
  * Sleeping-planet check    — no co-tenant AND no Lal Kitab aspect onto it.
  * Six rin (debt) diagnosis — explicit trigger configurations.
  * Teva (chart type)        — 7 archetype trigger patterns + Mishra fallback.
  * Varshphal               — universal age->year-ruler table read against
                               the natal D1.
  * Four-signal timing engine — maturation ages, year-rulers, 35-year house
                               cycle, Jupiter sanctification windows.

Lal Kitab uses ONLY the D1 — no D9, no nakshatras, no Vimshottari. The base
D1 is computed via lib/ephemeris.parashari_natal_chart with Lahiri ayanamsa
(Lal Kitab does not mandate an ayanamsa; Lahiri is the default).

All interpretation (narration, upaay prescription, Farman prose) stays in the
skill. This script emits ONLY deterministic facts.

Usage:
  compute_lalkitab_baseline.py --datetime ISO --tz TZ --lat LAT --lon LON [--age N]
  compute_lalkitab_baseline.py --chart chart.json [--age N]
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import jyotish_primitives as jp  # noqa: E402
import ephemeris as eph  # noqa: E402


LK_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
              "Saturn", "Rahu", "Ketu"]

# ====================================================================
# Lal Kitab tables — all dignity is by HOUSE NUMBER, never by sign.
# Sourced from references/pakka_ghar.md and references/aspects.md.
# ====================================================================

# Pakka ghar (permanent house) — references/pakka_ghar.md §1.
PAKKA_GHAR = {
    "Sun": 1, "Moon": 4, "Mars": 3, "Mercury": 7, "Jupiter": 9,
    "Venus": 7, "Saturn": 10, "Rahu": 12, "Ketu": 6,
}

# Exaltation house — references/pakka_ghar.md §2.
LK_EXALT_HOUSE = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6, "Jupiter": 4,
    "Venus": 12, "Saturn": 7, "Rahu": 3, "Ketu": 9,
}

# Debilitation house — references/pakka_ghar.md §3.
LK_DEBIL_HOUSE = {
    "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12, "Jupiter": 10,
    "Venus": 6, "Saturn": 1, "Rahu": 9, "Ketu": 3,
}

# Houses owned by each planet — references/pakka_ghar.md §4.
LK_HOUSES_OWNED = {
    "Sun": [5], "Moon": [4], "Mars": [1, 8], "Mercury": [3, 6],
    "Jupiter": [9, 12], "Venus": [2, 7], "Saturn": [10, 11],
    "Rahu": [], "Ketu": [],
}
# House -> owning planet (a house has at most one owner; Rahu/Ketu own none).
HOUSE_OWNER = {}
for _pl, _hs in LK_HOUSES_OWNED.items():
    for _h in _hs:
        HOUSE_OWNER[_h] = _pl

# Fixed natural friendship — references/pakka_ghar.md §5.
LK_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus", "Rahu"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn", "Rahu"],
    "Saturn": ["Mercury", "Venus", "Rahu"],
    "Rahu": ["Mercury", "Venus", "Saturn"],
    "Ketu": ["Mars", "Venus", "Saturn"],
}
LK_ENEMIES = {
    "Sun": ["Saturn", "Venus", "Rahu"],
    "Moon": ["Rahu", "Ketu"],
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
    "Rahu": ["Sun", "Moon", "Mars"],
    "Ketu": ["Moon"],
}

# Blind houses — references/pakka_ghar.md §6.
BLIND_HOUSES = {2, 6, 8, 12}

# Lal Kitab aspects — houses aspected counted inclusive from the planet's
# own house — references/aspects.md. NOT Parashari.
# Ketu's aspect is [5, 7, 9] only. aspects.md notes "some Farmans add 2nd" —
# that 2nd-house variant is intentionally excluded here as an optional,
# lineage-specific extension, not an oversight (A7).
LK_ASPECTS = {
    "Sun": [7], "Moon": [7], "Mars": [4, 7, 8], "Mercury": [7],
    "Jupiter": [5, 7, 9], "Venus": [7], "Saturn": [3, 7, 10],
    "Rahu": [5, 7, 9, 12], "Ketu": [5, 7, 9],
}

# Six debilitations that aspects can never redeem — references/aspects.md.
NEVER_REDEEMED = {("Sun", 7), ("Moon", 8), ("Mars", 4), ("Saturn", 1),
                  ("Venus", 6), ("Mercury", 12)}


def fixed_house(sign_idx):
    """Lal Kitab fixed house for a sign index: Aries(0)->1 ... Pisces(11)->12."""
    return sign_idx + 1


def house_n_from(start_house, n):
    """The house number n places from start_house, counted inclusive (n=1=self).
    Houses wrap 1..12."""
    return ((start_house - 1 + (n - 1)) % 12) + 1


def aspected_houses(planet, house):
    """Set of houses a planet aspects from `house`, per Lal Kitab aspect rules."""
    return {house_n_from(house, d) for d in LK_ASPECTS[planet]}


# ====================================================================
# Phase 2 — fixed-house re-map
# ====================================================================

def build_fixed_house_chart(d1):
    """Re-render the Vedic D1 into the Lal Kitab fixed-house frame.

    In Lal Kitab a planet's house = its sign index + 1 (Aries always 1st).
    The birth Lagna is recorded as 'flavour' only — houses never rotate.
    """
    planets_raw = d1["planets"]
    lagna_sign = d1["lagna_sign"]

    planets = {}
    houses = {h: [] for h in range(1, 13)}
    for p in LK_PLANETS:
        info = planets_raw[p]
        si = jp.SIGNS.index(info["sign"])
        h = fixed_house(si)
        planets[p] = {
            "sign": info["sign"],
            "fixed_house": h,
            "deg_in_sign": round(info["deg_in_sign"], 4),
            "retrograde": info.get("retrograde", False),
        }
        houses[h].append(p)

    return {
        "frame": "fixed (Aries=1, Taurus=2, ... Pisces=12)",
        "birth_lagna_sign_flavour": lagna_sign,
        "birth_lagna_note": "recorded as flavour only; houses do not rotate",
        "planets": planets,
        "houses": {str(h): houses[h] for h in range(1, 13)},
        "empty_houses": [h for h in range(1, 13) if not houses[h]],
    }


# ====================================================================
# Phase 3 — pakka ghar + dignity
# ====================================================================

def lk_dignity(planet, house):
    """Lal Kitab placement dignity by house number.

    Priority: exalted > debilitated > own-house > friend > enemy > neutral.
    A planet in its own/pakka house outranks friend/enemy evaluation.
    """
    if house == LK_EXALT_HOUSE[planet]:
        return "exalted"
    if house == LK_DEBIL_HOUSE[planet]:
        return "debilitated"
    if house in LK_HOUSES_OWNED[planet] or house == PAKKA_GHAR[planet]:
        return "own"
    owner = HOUSE_OWNER.get(house)
    if owner is None:
        return "neutral"
    if owner in LK_FRIENDS[planet]:
        return "friend"
    if owner in LK_ENEMIES[planet]:
        return "enemy"
    return "neutral"


def build_pakka_ghar(fixed_chart):
    """Per-planet pakka ghar status, dignity, and buried (dabba) check."""
    planets = fixed_chart["planets"]
    house_occupants = fixed_chart["houses"]

    out = {}
    for p in LK_PLANETS:
        h = planets[p]["fixed_house"]
        pg = PAKKA_GHAR[p]
        in_pg = (h == pg)
        dignity = lk_dignity(p, h)

        # Pakka-ghar substitution levers (references/pakka_ghar.md §7).
        pg_owner = HOUSE_OWNER.get(pg)
        pg_occupants = house_occupants[str(pg)]

        # Buried / dabba — a planet 12th-from another is buried by it
        # (references/pakka_ghar.md §8). House 12-from H is house H+1.
        buried_by = []
        for q in LK_PLANETS:
            if q == p:
                continue
            qh = planets[q]["fixed_house"]
            # p is buried by q  <=>  p sits in the 12th house from q.
            if house_n_from(qh, 12) == h:
                buried_by.append(q)

        out[p] = {
            "fixed_house": h,
            "pakka_ghar": pg,
            "in_pakka_ghar": in_pg,
            "lk_dignity": dignity,
            "blind_house": h in BLIND_HOUSES,
            "thrives_despite_blind": (h in BLIND_HOUSES and in_pg),
            "pakka_ghar_owner": pg_owner,
            "pakka_ghar_occupants": pg_occupants,
            "buried": bool(buried_by),
            "buried_by": buried_by,
            "debil_never_redeemed": (p, h) in NEVER_REDEEMED,
        }

    # Neecha Bhanga (debilitation cancellation) — pakka_ghar.md §3 / aspects.md
    # "Houses That Never Give Aspect Relief": the most common cancellation is
    # when the lord of the house where debilitation occurs sits in its own
    # pakka ghar. This applies even to the six never-redeemed debilitations —
    # aspects.md is explicit that only pakka-ghar-of-lord (not aspects) can
    # truly cancel those. Second pass: needs every planet's in_pakka_ghar,
    # computed above.
    for p in LK_PLANETS:
        info = out[p]
        cancelled = False
        if info["lk_dignity"] == "debilitated":
            lord = HOUSE_OWNER.get(info["fixed_house"])
            if lord is not None and out[lord]["in_pakka_ghar"]:
                cancelled = True
        info["debil_cancelled"] = cancelled

    return out


# ====================================================================
# Phase 4 — sleeping planets + aspect map
# ====================================================================

def build_aspect_map(fixed_chart):
    """For each planet: the houses it aspects and the planets sitting there."""
    planets = fixed_chart["planets"]
    house_occupants = fixed_chart["houses"]

    amap = {}
    for p in LK_PLANETS:
        h = planets[p]["fixed_house"]
        hits = []
        for ah in sorted(aspected_houses(p, h)):
            for q in house_occupants[str(ah)]:
                if q == p:
                    continue
                if q in LK_FRIENDS[p]:
                    rel = "friend"
                elif q in LK_ENEMIES[p]:
                    rel = "enemy"
                else:
                    rel = "neutral"
                hits.append({"planet": q, "house": ah, "relationship": rel})
        amap[p] = {
            "aspects_houses": sorted(aspected_houses(p, h)),
            "planets_aspected": hits,
        }
    return amap


def build_sleeping(fixed_chart, aspect_map):
    """A planet is sleeping if it has no co-tenant AND no planet aspects it.

    Dead-pair exception (aspects.md "Aspect-Triggered Awakening"): a natal
    aspect on a sleeping planet does not count as awakening if both planets
    are in mutual aspect-isolation from the rest of the chart — i.e. planet A
    aspects/co-tenants only B, and B aspects/co-tenants only A. Such a pair
    stays effectively dead ("dead pair") and both are re-marked sleeping.
    """
    planets = fixed_chart["planets"]
    house_occupants = fixed_chart["houses"]

    # Who aspects whom: planet q aspects planet p.
    aspected_by = {p: [] for p in LK_PLANETS}
    for q in LK_PLANETS:
        qh = planets[q]["fixed_house"]
        qaspects = aspected_houses(q, qh)
        for p in LK_PLANETS:
            if p == q:
                continue
            if planets[p]["fixed_house"] in qaspects:
                aspected_by[p].append(q)

    co_tenants = {}
    for p in LK_PLANETS:
        h = planets[p]["fixed_house"]
        co_tenants[p] = [q for q in house_occupants[str(h)] if q != p]

    out = {}
    for p in LK_PLANETS:
        sleeping = (not co_tenants[p]) and (not aspected_by[p])
        out[p] = {
            "sleeping": sleeping,
            "co_tenants": co_tenants[p],
            "aspected_by": aspected_by[p],
            "dead_pair_with": None,
        }

    # Dead-pair second pass: p and q have no co-tenants, and aspect only each
    # other (aspected_by[p] == [q] and aspected_by[q] == [p]) -> the aspect
    # doesn't count as awakening; both are re-marked sleeping.
    for p in LK_PLANETS:
        if co_tenants[p] or len(aspected_by[p]) != 1:
            continue
        (q,) = aspected_by[p]
        if co_tenants[q]:
            continue
        if aspected_by[q] == [p]:
            out[p]["sleeping"] = True
            out[p]["dead_pair_with"] = q
            out[q]["sleeping"] = True
            out[q]["dead_pair_with"] = p

    return out


# ====================================================================
# Phase 5 — six rin (karmic debt) diagnosis
# ====================================================================

def _afflicts(a, b, planets, aspect_map):
    """True if planet `a` afflicts planet `b` — Lal Kitab affliction =
    conjunction (same fixed house) OR a aspects b OR b aspects a (mutual)."""
    if a == b:
        return False
    if planets[a]["fixed_house"] == planets[b]["fixed_house"]:
        return True
    a_hits = {x["planet"] for x in aspect_map[a]["planets_aspected"]}
    b_hits = {x["planet"] for x in aspect_map[b]["planets_aspected"]}
    return b in a_hits or a in b_hits


def _conjunct(a, b, planets):
    return a != b and planets[a]["fixed_house"] == planets[b]["fixed_house"]


def _buried_by(p, q, pakka):
    return q in pakka[p]["buried_by"]


def _general_afflicted(p, pakka, sleeping, planets, aspect_map):
    """General Lal Kitab affliction test — references/aspects.md 'Aspect-
    Triggered Awakening' + references/teva_types.md §1: a planet is afflicted
    if debilitated, sleeping, OR conjunct/aspected by Saturn, Rahu, or Ketu.
    Distinct from `_lord_afflicted` below (used only for house-lord triggers
    such as '9th lord afflicted'), which does not check sleeping."""
    if pakka[p]["lk_dignity"] == "debilitated":
        return True
    if sleeping[p]["sleeping"]:
        return True
    return any(_afflicts(mal, p, planets, aspect_map) for mal in ("Saturn", "Rahu", "Ketu"))


def _lord_afflicted(lord, pakka, planets, aspect_map):
    """A house-lord is 'afflicted' if conjunct/aspected by Saturn/Rahu/Ketu or
    sitting in its own debilitation house. Used for lord-based rin/teva
    triggers (e.g. '9th lord afflicted', Behra Teva's '3rd lord afflicted')."""
    for mal in ("Saturn", "Rahu", "Ketu"):
        if mal != lord and _afflicts(mal, lord, planets, aspect_map):
            return True
    return pakka[lord]["lk_dignity"] == "debilitated"


# Houses each rin's triggers structurally implicate — used only to test
# whether Jupiter's protective 5th-house aspect (aspects.md "Special Aspect
# Rules -> Jupiter's 5th-house Aspect") lands on a house involved in that rin,
# in which case severity is mitigated one tier.
RIN_HOUSES = {
    "pitri_rin": {1, 7, 9, 10},
    "matri_rin": {4, 8},
    "stri_rin": {6, 7},
    "kanya_rin": {5, 9, 12},
    "bhratra_rin": {3, 4, 11},
    "atma_rin": {1, 5, 9, 10},
}

TIER_ORDER = ["Mild", "Moderate", "Severe"]


def _bump_tier(severity, delta):
    """Move a Mild/Moderate/Severe severity up (+1) or down (-1) a tier,
    clamped at both ends."""
    idx = TIER_ORDER.index(severity)
    idx = max(0, min(len(TIER_ORDER) - 1, idx + delta))
    return TIER_ORDER[idx]


def build_rin_diagnosis(fixed_chart, pakka, aspect_map, sleeping):
    """Run all six rin checks. Each rin: triggered bool + which configs fired."""
    planets = fixed_chart["planets"]
    occ = fixed_chart["houses"]
    house = {p: planets[p]["fixed_house"] for p in LK_PLANETS}

    def in_house(planet, h):
        return house[planet] == h

    def house_empty(h):
        return not occ[str(h)]

    def house_has(h, plist):
        return any(p in occ[str(h)] for p in plist)

    def house_present(h, plist):
        """Subset of plist actually occupying house h — used to tag which
        specific planet(s) a 'Saturn or Rahu sits in house N' trigger fired
        on (references A11: structural attribution, not desc substring)."""
        return [p for p in plist if p in occ[str(h)]]

    def lord_afflicted(lord):
        return _lord_afflicted(lord, pakka, planets, aspect_map)

    results = {}

    # --- 1. Pitri Rin -------------------------------------------------
    pitri = []
    if _afflicts("Saturn", "Sun", planets, aspect_map):
        pitri.append({"trigger": 1, "desc": "Sun afflicted by Saturn",
                      "farman": "Farman 8, Vol 2 (1940)", "planets": ["Sun", "Saturn"]})
    if _afflicts("Rahu", "Sun", planets, aspect_map):
        pitri.append({"trigger": 2, "desc": "Sun afflicted by Rahu",
                      "farman": "Farman 8, Vol 2 (1940)", "planets": ["Sun", "Rahu"]})
    if in_house("Sun", 7):
        pitri.append({"trigger": 3, "desc": "Sun debilitated (house 7)",
                      "farman": "Farman 12, Vol 1 (1939)", "planets": ["Sun"]})
    if house_empty(9) and lord_afflicted("Jupiter"):
        pitri.append({"trigger": 4, "desc": "9th house empty AND Jupiter (9th lord) afflicted",
                      "farman": "Farman 22, Vol 3 (1941)", "planets": ["Jupiter"]})
    if house_has(9, ["Saturn", "Rahu"]):
        pitri.append({"trigger": 5, "desc": "Saturn or Rahu sits in 9th house",
                      "farman": "Farman 22, Vol 3 (1941)",
                      "planets": house_present(9, ["Saturn", "Rahu"])})
    if _buried_by("Sun", "Saturn", pakka):
        pitri.append({"trigger": 6, "desc": "Sun buried (12th) by Saturn",
                      "farman": "Farman 16, Vol 4 (1942)", "planets": ["Sun", "Saturn"]})
    if (house_empty(1) and house_empty(9)
            and not aspect_map_has_house(aspect_map, 1)
            and not aspect_map_has_house(aspect_map, 9)):
        pitri.append({"trigger": 7, "desc": "Houses 1 and 9 both empty AND unaspected",
                      "farman": "Farman 31, Vol 5 (1952)",
                      "planets": [HOUSE_OWNER[1], HOUSE_OWNER[9]]})
    tenth_damaged = (
        (pakka["Saturn"]["lk_dignity"] == "debilitated" and house["Saturn"] == 10)
        or (house_empty(10) and lord_afflicted("Saturn")))
    results["pitri_rin"] = _rin_record(
        pitri,
        [sleeping["Sun"]["sleeping"],
         pakka["Jupiter"]["lk_dignity"] == "debilitated" or sleeping["Jupiter"]["sleeping"],
         tenth_damaged],
        multi_trigger_severe=True)

    # --- 2. Matri Rin -------------------------------------------------
    matri = []
    if _afflicts("Saturn", "Moon", planets, aspect_map):
        matri.append({"trigger": 1, "desc": "Moon afflicted by Saturn",
                      "farman": "Farman 5, Vol 2 (1940)", "planets": ["Moon", "Saturn"]})
    if _afflicts("Ketu", "Moon", planets, aspect_map):
        matri.append({"trigger": 2, "desc": "Moon afflicted by Ketu",
                      "farman": "Farman 5, Vol 2 (1940)", "planets": ["Moon", "Ketu"]})
    if _conjunct("Rahu", "Moon", planets):
        matri.append({"trigger": 3, "desc": "Moon conjunct Rahu",
                      "farman": "Farman 9, Vol 2 (1940)", "planets": ["Moon", "Rahu"]})
    if in_house("Moon", 8):
        matri.append({"trigger": 4, "desc": "Moon debilitated (house 8)",
                      "farman": "Farman 14, Vol 1 (1939)", "planets": ["Moon"]})
    if house_empty(4) and lord_afflicted("Moon"):
        matri.append({"trigger": 5, "desc": "4th house empty AND Moon (4th lord) afflicted",
                      "farman": "Farman 19, Vol 3 (1941)", "planets": ["Moon"]})
    if house_has(4, ["Saturn", "Ketu"]):
        matri.append({"trigger": 6, "desc": "Saturn or Ketu sits in 4th house",
                      "farman": "Farman 19, Vol 3 (1941)",
                      "planets": house_present(4, ["Saturn", "Ketu"])})
    if _buried_by("Moon", "Rahu", pakka):
        matri.append({"trigger": 7, "desc": "Moon buried (12th) by Rahu",
                      "farman": "Farman 18, Vol 4 (1942)", "planets": ["Moon", "Rahu"]})
    results["matri_rin"] = _rin_record(
        matri, [sleeping["Moon"]["sleeping"], "Mars" in occ[str(4)]])

    # --- 3. Stri Rin --------------------------------------------------
    stri = []
    if _afflicts("Saturn", "Venus", planets, aspect_map):
        stri.append({"trigger": 1, "desc": "Venus afflicted by Saturn",
                     "farman": "Farman 11, Vol 2 (1940)", "planets": ["Venus", "Saturn"]})
    if _afflicts("Rahu", "Venus", planets, aspect_map):
        stri.append({"trigger": 2, "desc": "Venus afflicted by Rahu",
                     "farman": "Farman 11, Vol 2 (1940)", "planets": ["Venus", "Rahu"]})
    if in_house("Venus", 6):
        stri.append({"trigger": 3, "desc": "Venus debilitated (house 6)",
                     "farman": "Farman 17, Vol 1 (1939)", "planets": ["Venus"]})
    if house_has(7, ["Saturn", "Rahu"]):
        stri.append({"trigger": 4, "desc": "Saturn or Rahu sits in 7th house",
                     "farman": "Farman 25, Vol 3 (1941)",
                     "planets": house_present(7, ["Saturn", "Rahu"])})
    if house_empty(7) and lord_afflicted("Venus"):
        stri.append({"trigger": 5, "desc": "7th house empty AND Venus (7th lord) afflicted",
                     "farman": "Farman 25, Vol 3 (1941)", "planets": ["Venus"]})
    if _buried_by("Venus", "Saturn", pakka):
        stri.append({"trigger": 6, "desc": "Venus buried (12th) by Saturn",
                     "farman": "Farman 21, Vol 4 (1942)", "planets": ["Venus", "Saturn"]})
    if in_house("Mars", 7) and not pakka["Mars"]["in_pakka_ghar"]:
        stri.append({"trigger": 7, "desc": "Mars in 7th AND not in pakka ghar",
                     "farman": "Farman 27, Vol 5 (1952)", "planets": ["Mars"]})
    results["stri_rin"] = _rin_record(
        stri,
        [lord_afflicted("Mercury"),
         _general_afflicted("Moon", pakka, sleeping, planets, aspect_map)])

    # --- 4. Kanya Rin -------------------------------------------------
    kanya = []
    if in_house("Mercury", 12) and _afflicts("Sun", "Mercury", planets, aspect_map):
        kanya.append({"trigger": 1, "desc": "Mercury debilitated (12) AND afflicted by Sun",
                      "farman": "Farman 13, Vol 2 (1940)", "planets": ["Mercury", "Sun"]})
    if _afflicts("Rahu", "Jupiter", planets, aspect_map) and house["Jupiter"] in (5, 9):
        kanya.append({"trigger": 2, "desc": "Jupiter afflicted by Rahu in 5th or 9th",
                      "farman": "Farman 23, Vol 3 (1941)", "planets": ["Jupiter", "Rahu"]})
    if "Mars" in occ[str(5)] and "Ketu" in occ[str(5)]:
        kanya.append({"trigger": 3, "desc": "5th house has Mars + Ketu combination",
                      "farman": "Farman 24, Vol 3 (1941)", "planets": ["Mars", "Ketu"]})
    if in_house("Venus", 5):
        kanya.append({"trigger": 4, "desc": "Venus in 5th, debilitated by association",
                      "farman": "Farman 28, Vol 5 (1952)", "planets": ["Venus"]})
    results["kanya_rin"] = _rin_record(kanya, [])

    # --- 5. Bhratra Rin ----------------------------------------------
    bhratra = []
    if (_afflicts("Saturn", "Mars", planets, aspect_map)
            or _afflicts("Rahu", "Mars", planets, aspect_map)):
        afflicting = [m for m in ("Saturn", "Rahu") if _afflicts(m, "Mars", planets, aspect_map)]
        bhratra.append({"trigger": 1, "desc": "Mars afflicted by Saturn or Rahu",
                        "farman": "Farman 7, Vol 2 (1940)", "planets": ["Mars"] + afflicting})
    if in_house("Mars", 4):
        bhratra.append({"trigger": 2, "desc": "Mars debilitated (house 4)",
                        "farman": "Farman 15, Vol 1 (1939)", "planets": ["Mars"]})
    if "Saturn" in occ[str(3)]:
        bhratra.append({"trigger": 3, "desc": "Saturn sits in 3rd house",
                        "farman": "Farman 20, Vol 3 (1941)", "planets": ["Saturn"]})
    if (_afflicts("Mercury", "Mars", planets, aspect_map)
            and "Mercury" in LK_ENEMIES["Mars"]):
        bhratra.append({"trigger": 4, "desc": "Mercury and Mars in mutual enmity-aspect",
                        "farman": "Farman 26, Vol 4 (1942)", "planets": ["Mercury", "Mars"]})
    if (house_empty(3) and house_empty(11)
            and lord_afflicted("Mercury") and lord_afflicted("Saturn")):
        bhratra.append({"trigger": 5, "desc": "Houses 3 and 11 empty AND their lords afflicted",
                        "farman": "Farman 30, Vol 5 (1952)", "planets": ["Mercury", "Saturn"]})
    # No Compounding subsection exists for Bhratra Rin in rin_diagnosis.md §5 —
    # do not fabricate one (A5); compounders list stays empty.
    results["bhratra_rin"] = _rin_record(bhratra, [])

    # --- 6. Self / Atma Rin ------------------------------------------
    atma = []
    if _conjunct("Rahu", "Jupiter", planets):
        atma.append({"trigger": 1, "desc": "Jupiter conjunct Rahu",
                     "farman": "Farman 4, Vol 2 (1940)", "planets": ["Jupiter", "Rahu"]})
    if in_house("Jupiter", 10):
        atma.append({"trigger": 2, "desc": "Jupiter debilitated (house 10)",
                     "farman": "Farman 18, Vol 1 (1939)", "planets": ["Jupiter"]})
    if all(house_empty(h) for h in (1, 5, 9)):
        atma.append({"trigger": 3, "desc": "Blind chart — no planets in trines (1, 5, 9)",
                     "farman": "Farman 32, Vol 5 (1952)", "planets": []})
    if in_house("Ketu", 1) and not aspect_map_planet_aspected_by_benefic(
            "Ketu", aspect_map, sleeping):
        atma.append({"trigger": 4, "desc": "Ketu in 1 with no benefic aspect",
                     "farman": "Farman 29, Vol 4 (1942)", "planets": ["Ketu"]})
    if sleeping["Jupiter"]["sleeping"] and sleeping["Ketu"]["sleeping"]:
        atma.append({"trigger": 5, "desc": "Jupiter and Ketu both sleeping",
                     "farman": "Farman 33, Vol 5 (1952)", "planets": ["Jupiter", "Ketu"]})
    # No Compounding subsection exists for Atma Rin in rin_diagnosis.md §6 —
    # do not fabricate one (A5); compounders list stays empty.
    results["atma_rin"] = _rin_record(atma, [])

    # --- Jupiter's 5th-house protective aspect (M1) -------------------
    # aspects.md "Special Aspect Rules -> Jupiter's 5th-house Aspect":
    # "Mitigates rin severity by one tier wherever it lands." Apply before
    # cross-rin escalation so escalation acts on the mitigated severities.
    jupiter_land_house = house_n_from(house["Jupiter"], 5)
    for rname, rdata in results.items():
        mitigated = rdata["triggered"] and jupiter_land_house in RIN_HOUSES.get(rname, set())
        rdata["jupiter_5th_aspect_mitigation"] = mitigated
        if mitigated:
            rdata["severity_before_mitigation"] = rdata["severity"]
            rdata["severity"] = _bump_tier(rdata["severity"], -1)

    # --- cross-rin compounding (M2) ------------------------------------
    # rin_diagnosis.md "Cross-Rin Compounding Rules": 2 rins active -> each
    # one tier worse than diagnosed individually; 3+ -> debt-saturation.
    active = [k for k, v in results.items() if v["triggered"]]
    active_count = len(active)
    if active_count >= 2:
        for rname in active:
            rdata = results[rname]
            rdata["severity_before_cross_rin_escalation"] = rdata["severity"]
            rdata["severity"] = _bump_tier(rdata["severity"], +1)
            rdata["cross_rin_escalated"] = True
    else:
        for rname in active:
            results[rname]["cross_rin_escalated"] = False

    return {
        "rins": results,
        "active_rins": active,
        "active_count": active_count,
        "debt_saturation": active_count >= 3,
        "blocked_house_pattern": (
            results["pitri_rin"]["triggered"]
            and results["pitri_rin"]["severity"] == "Severe"
            and results["stri_rin"]["triggered"]
            and results["stri_rin"]["severity"] == "Severe"),
    }


def aspect_map_has_house(aspect_map, h):
    """True if any planet aspects house h."""
    for p, data in aspect_map.items():
        if h in data["aspects_houses"]:
            return True
    return False


def aspect_map_planet_aspected_by_benefic(planet, aspect_map, sleeping):
    """True if `planet` receives an aspect from a natural benefic (Jupiter,
    Venus, or Mercury) — used for the Ketu-in-1 Atma Rin check."""
    benefics = {"Jupiter", "Venus", "Mercury"}
    for q, data in aspect_map.items():
        if q not in benefics:
            continue
        for hit in data["planets_aspected"]:
            if hit["planet"] == planet:
                return True
    return False


def _rin_record(triggers, compounders, multi_trigger_severe=False):
    """Build a rin record. Severity per references/rin_diagnosis.md's shared
    "Severity Scale": Mild = single trigger, no compounding; Moderate =
    trigger + one compounding factor; Severe = trigger + two or more
    compounding factors. `multi_trigger_severe` applies the Pitri-Rin-only
    rule ("any one is sufficient; multiple = severe", §1) — the audit (A1)
    found this had been generalized to all six rins; it is NOT generalized
    here — only pitri_rin's call site passes multi_trigger_severe=True."""
    triggered = bool(triggers)
    compounders = [c for c in compounders if c]
    n = len(triggers)
    if not triggered:
        severity = None
    elif multi_trigger_severe and n >= 2:
        severity = "Severe"
    elif len(compounders) >= 2:
        severity = "Severe"
    elif len(compounders) == 1:
        severity = "Moderate"
    else:
        severity = "Mild"
    return {
        "triggered": triggered,
        "fired_triggers": triggers,
        "trigger_count": n,
        "compounding_factors": len(compounders),
        "severity": severity,
    }


# ====================================================================
# Phase 6 — teva (chart type) classification
# ====================================================================

def build_teva(fixed_chart, pakka, sleeping, rin, aspect_map):
    """Classify the chart into 7 teva archetypes; Mishra if no clean match.

    Each archetype's trigger is expressed as a set of named boolean
    sub-conditions. A clean match requires all of them true. "Dominant" is
    the matched archetype with the highest count of satisfied sub-conditions
    (a coarse strength score — teva_types.md L3/L6 "name the strongest
    first"), not simply the first one tried in code order (A8). On full
    Mishra fallback, the same per-archetype fractional scores are used to
    name the closest two archetypes with matched/unmatched traits
    (teva_types.md §8) (A9).

    `aspect_map` is passed in (built once in build_baseline) rather than
    recomputed here (previously recomputed 3x — P2-14).
    """
    planets = fixed_chart["planets"]
    occ = fixed_chart["houses"]
    house = {p: planets[p]["fixed_house"] for p in LK_PLANETS}

    def afflicted(p):
        """A planet is 'afflicted' — aspects.md general definition (also used
        by teva_types.md §1): debilitated, sleeping, or conjunct/aspected by
        Saturn/Rahu/Ketu. (W2: previously substituted enemy-house + buried for
        "with Saturn/Rahu/Ketu" — a different, unreferenced criterion.)"""
        return _general_afflicted(p, pakka, sleeping, planets, aspect_map)

    kendras = [1, 4, 7, 10]
    empty_kendras = [h for h in kendras if not occ[str(h)]]
    n_pakka = sum(1 for p in LK_PLANETS if pakka[p]["in_pakka_ghar"])
    n_sleeping = sum(1 for p in LK_PLANETS if sleeping[p]["sleeping"])
    active_rins = rin["active_count"]
    severe_rins = sum(1 for v in rin["rins"].values() if v["severity"] == "Severe")
    luminary_deb_or_buried = any(
        pakka[lum]["lk_dignity"] == "debilitated" or pakka[lum]["buried"]
        for lum in ("Sun", "Moon"))

    ms_conjunct = _conjunct("Mars", "Saturn", planets)
    ms_aspect = _afflicts("Mars", "Saturn", planets, aspect_map)
    merc_bad = (pakka["Mercury"]["lk_dignity"] == "debilitated"
                or sleeping["Mercury"]["sleeping"])
    # W1: 3rd house's owner (lord) is Mercury (LK_HOUSES_OWNED), not Mars —
    # Mars's *pakka ghar* is house 3, but the 3rd *lord* is Mercury. Use the
    # same lord_afflicted() helper Bhratra-Rin trigger 5 uses for this lord.
    third_lord_afflicted = _lord_afflicted(HOUSE_OWNER[3], pakka, planets, aspect_map)
    third_bad = ("Saturn" in occ["3"] or "Ketu" in occ["3"] or third_lord_afflicted)
    lum_ok = all(pakka[lum]["lk_dignity"] not in ("debilitated", "enemy")
                 and not sleeping[lum]["sleeping"]
                 for lum in ("Sun", "Moon"))
    only_mild = (severe_rins == 0
                 and sum(1 for v in rin["rins"].values()
                         if v["severity"] in ("Moderate",)) == 0
                 and active_rins <= 1)
    sun_royal = house["Sun"] == 1
    jup_aspects_sun = any(hit["planet"] == "Sun"
                          for hit in aspect_map["Jupiter"]["planets_aspected"])
    saturn_royal = house["Saturn"] in (10, 7)
    jup_pakka = house["Jupiter"] == 9
    ketu_spirit = (house["Ketu"] in (9, 12)
                   or any(hit["planet"] == "Jupiter"
                          for hit in aspect_map["Ketu"]["planets_aspected"]))
    saturn_support = house["Saturn"] in (10, 7)

    archetypes = {
        "Andha": {
            "label": "Blind Chart", "farman": "Farman 36, Vol 5 (1952)",
            "conditions": {
                "Sun afflicted": afflicted("Sun"),
                "Moon afflicted": afflicted("Moon"),
                "2+ kendras empty": len(empty_kendras) >= 2,
            },
            "pattern": ("Both luminaries afflicted AND "
                        f"{len(empty_kendras)} kendras empty {empty_kendras}"),
        },
        "Lula": {
            "label": "Lame Chart", "farman": "Farman 39, Vol 5 (1952)",
            "conditions": {
                "Mars-Saturn conjunct or mutual aspect": ms_conjunct or ms_aspect,
                "Mars or Saturn in house 1/4/8": (house["Mars"] in (1, 4, 8)
                                                  or house["Saturn"] in (1, 4, 8)),
            },
            "pattern": (f"Mars-Saturn {'conjunction' if ms_conjunct else 'mutual aspect'} "
                        "with one in house 1/4/8 "
                        f"({'Mars-led' if house['Mars'] in (1, 4, 8) else 'Saturn-led'})"),
        },
        "Behra": {
            "label": "Deaf Chart", "farman": "Farman 41, Vol 5 (1952)",
            "conditions": {
                "Mercury debilitated/sleeping": merc_bad,
                "3rd house compromised (Saturn/Ketu in 3, or 3rd lord Mercury afflicted)": third_bad,
            },
            "pattern": "Mercury debilitated/sleeping AND 3rd house compromised",
        },
        "Sukhi": {
            "label": "Happy Chart", "farman": "Farman 35, Vol 5 (1952)",
            "conditions": {
                "2+ planets in pakka ghar": n_pakka >= 2,
                "no severe/moderate rin (<=1 mild)": only_mild,
                "luminaries at least neutral": lum_ok,
            },
            "pattern": (f"{n_pakka} planets in pakka ghar, "
                        "no severe/moderate rin, luminaries sound"),
        },
        "Dukhi": {
            "label": "Sorrowful Chart", "farman": "Farman 38, Vol 5 (1952)",
            "conditions": {
                "2+ rins active": active_rins >= 2,
                "2+ sleeping planets": n_sleeping >= 2,
                "a luminary debilitated/buried": luminary_deb_or_buried,
            },
            "pattern": (f"{active_rins} active rins, {n_sleeping} sleeping "
                        "planets, a luminary debilitated/buried"),
        },
        "Rajyogi": {
            "label": "Royal Chart", "farman": "Farman 34, Vol 5 (1952)",
            "conditions": {
                "Sun in house 1": sun_royal,
                "Jupiter aspects Sun": jup_aspects_sun,
                "Saturn in pakka(10)/exalted(7)": saturn_royal,
                "no severe rin": severe_rins == 0,
            },
            "pattern": ("Sun in house 1 aspected by Jupiter, Saturn in "
                        f"house {house['Saturn']}, no severe rin"),
        },
        "Pujari": {
            "label": "Spiritual / Priest Chart", "farman": "Farman 37, Vol 5 (1952)",
            "conditions": {
                "Jupiter in pakka ghar 9": jup_pakka,
                "Ketu spiritual (9/12 or aspecting Jupiter)": ketu_spirit,
                "Saturn supportive (10/7)": saturn_support,
            },
            "pattern": "Jupiter in pakka ghar 9, Ketu spiritual, Saturn supportive",
        },
    }

    matched = []
    partial_scores = []
    for name, data in archetypes.items():
        conds = data["conditions"]
        n_true = sum(1 for v in conds.values() if v)
        n_total = len(conds)
        partial_scores.append({
            "teva": name,
            "fraction": round(n_true / n_total, 3),
            "matched_conditions": [k for k, v in conds.items() if v],
            "unmatched_conditions": [k for k, v in conds.items() if not v],
        })
        if n_true == n_total:
            matched.append({
                "teva": name,
                "label": data["label"],
                "farman": data["farman"],
                "matched_pattern": data["pattern"],
                "strength_score": n_true,
            })

    if not matched:
        partial_scores.sort(key=lambda s: s["fraction"], reverse=True)
        dominant = {
            "teva": "Mishra",
            "label": "Mixed / Composite Chart",
            "farman": None,
            "matched_pattern": "No single teva archetype matched cleanly; "
                               "most modern charts are Mishra",
            "closest_two": partial_scores[:2],
        }
        return {"dominant": dominant, "secondary": [], "all_matched": [],
                "partial_scores": partial_scores}

    matched.sort(key=lambda m: m["strength_score"], reverse=True)
    return {
        "dominant": matched[0],
        "secondary": matched[1:3],
        "all_matched": matched,
        "partial_scores": partial_scores,
    }


# ====================================================================
# Phase 8C — Varshphal age->year-ruler table
# ====================================================================

# Universal age -> year-ruler(s) — references/varshphal.md.
YEAR_RULER = {
    1: ["Sun", "Moon"], 2: ["Moon"], 3: ["Mars"], 4: ["Mercury"], 5: ["Jupiter"],
    6: ["Venus"], 7: ["Saturn"], 8: ["Rahu"], 9: ["Ketu"], 10: ["Sun"],
    11: ["Moon"], 12: ["Mars"], 13: ["Mercury"], 14: ["Jupiter"], 15: ["Venus"],
    16: ["Saturn"], 17: ["Rahu"], 18: ["Ketu"], 19: ["Sun"], 20: ["Moon"],
    21: ["Jupiter"], 22: ["Venus"], 23: ["Saturn"], 24: ["Venus"], 25: ["Mars"],
    26: ["Mercury"], 27: ["Moon"], 28: ["Mars"], 29: ["Saturn"], 30: ["Rahu"],
    31: ["Ketu"], 32: ["Sun"], 33: ["Moon"], 34: ["Mars"], 35: ["Mercury"],
    36: ["Saturn"], 37: ["Rahu"], 38: ["Ketu"], 39: ["Venus"], 40: ["Sun"],
    41: ["Moon"], 42: ["Saturn", "Rahu"], 43: ["Ketu"], 44: ["Sun"], 45: ["Mercury"],
    46: ["Jupiter"], 47: ["Mars"], 48: ["Saturn"], 49: ["Venus"], 50: ["Sun"],
    51: ["Moon"], 52: ["Jupiter"], 53: ["Mercury"], 54: ["Mars", "Saturn"], 55: ["Venus"],
    56: ["Sun"], 57: ["Moon"], 58: ["Jupiter"], 59: ["Mercury"], 60: ["Saturn"],
    61: ["Rahu"], 62: ["Ketu"], 63: ["Rahu"],
}

MAJOR_YEARS = {21: "Jupiter major — direction-setting",
               24: "Venus major — marriage / partnership pivot",
               27: "Moon major — emotional re-set",
               28: "Mars major — energy / conflict / decisive action",
               36: "Saturn major (1st) — career legitimacy test",
               42: "Saturn + Rahu (severe) — most dangerous Lal Kitab year",
               48: "Saturn major (3rd) — career consolidation",
               54: "Mars + Saturn — health watch",
               63: "Rahu major — legacy phase begins"}

DANGER_YEARS = {21, 36, 42, 48, 54, 63}


def year_ruler(age):
    """Year-ruler(s) for an age. Past 63 the table cycles every 9 years
    on the planetary sequence anchored at the 54..62 window."""
    if age in YEAR_RULER:
        return YEAR_RULER[age]
    # references/varshphal.md: 64+ cycles Saturn-Jupiter-Sun-Moon dominant;
    # extend deterministically by the 9-year recurrence anchored on age 54.
    base = ((age - 54) % 9) + 54
    return YEAR_RULER.get(base, ["Saturn"])


def planet_condition(planet, pakka, sleeping, rin):
    """Compact natal condition of a planet for Varshphal / timing read-out."""
    # A11: attribution is structural — each fired trigger is tagged with an
    # explicit "planets" list at creation time (build_rin_diagnosis) instead
    # of substring-matching the planet's name against the free-text "desc".
    # Substring matching missed lord-only triggers whose desc names the lord
    # planet but not the karaka planet being asked about (or vice versa), and
    # is fragile to renames/casing. Fall back to the old substring check only
    # if an older/foreign trigger dict has no "planets" key.
    rin_involved = []
    for rname, rdata in rin["rins"].items():
        for trig in rdata["fired_triggers"]:
            trig_planets = trig.get("planets")
            if trig_planets is not None:
                hit = planet in trig_planets
            else:
                hit = planet.lower() in trig["desc"].lower()
            if hit:
                rin_involved.append(rname)
                break
    return {
        "fixed_house": pakka[planet]["fixed_house"],
        "lk_dignity": pakka[planet]["lk_dignity"],
        "in_pakka_ghar": pakka[planet]["in_pakka_ghar"],
        "sleeping": sleeping[planet]["sleeping"],
        "buried": pakka[planet]["buried"],
        "rin_involved": sorted(set(rin_involved)),
        # A12: varshphal.md "How to Read a Year" Step 2 needs the houses the
        # year-ruler aspects and owns, not just its own placement.
        "aspected_houses": sorted(aspected_houses(planet, pakka[planet]["fixed_house"])),
        "owned_houses": LK_HOUSES_OWNED[planet],
    }


def build_varshphal(age, pakka, sleeping, rin):
    """Apply the age->year-ruler table for current age + next 5 + major years."""
    if age is None:
        return {"note": "no --age supplied; varshphal not computed"}

    def year_entry(a):
        rulers = year_ruler(a)
        return {
            "age": a,
            "year_rulers": rulers,
            "major_year": MAJOR_YEARS.get(a),
            "danger_year": a in DANGER_YEARS,
            "ruler_conditions": {
                r: planet_condition(r, pakka, sleeping, rin) for r in rulers},
        }

    current = year_entry(age)
    next5 = [year_entry(age + i) for i in range(1, 6)]
    major = {a: year_entry(a) for a in sorted(MAJOR_YEARS)}

    return {
        "current_age": age,
        "current_year": current,
        "next_5_years": next5,
        "major_years": major,
    }


# ====================================================================
# Phase 8D — four-signal timing engine (raw deterministic outputs)
# ====================================================================

# Signal 1 — planetary maturation ages — references/timing.md Part A.
MATURATION_AGE = {
    "Jupiter": 16, "Sun": 22, "Moon": 24, "Venus": 25, "Mars": 28,
    "Mercury": 32, "Saturn": 36, "Rahu": 42, "Ketu": 48,
}

# Signal 3 — 35/36-year house cycle (6 years per house) — references/timing.md.
# House 9's 2nd band is documented as "84+" (open-ended, timing.md Signal 3
# table) — finitised here to a very high age (200) so it behaves as
# effectively open-ended rather than capping out at a plausible lifespan (A10).
HOUSE_CYCLE = {
    1: [(1, 6), (36, 41)], 2: [(7, 12), (42, 47)], 3: [(13, 18), (48, 53)],
    4: [(19, 24), (54, 59)], 5: [(25, 30), (60, 65)], 6: [(31, 36), (66, 71)],
    7: [(37, 42), (72, 77)], 8: [(43, 48), (78, 83)], 9: [(49, 54), (84, 200)],
    10: [(55, 60)], 11: [(61, 66)], 12: [(67, 72)],
}

# Signal 4 — Jupiter year-rulers (strongest sanctification windows).
# Derived directly from the YEAR_RULER table so it stays consistent with
# Varshphal. references/timing.md cites a theoretical 9-year recurrence
# (21, 30, 39, 48...) but the authoritative age table is the year ruler.
JUPITER_YEARS = sorted(a for a, rs in YEAR_RULER.items() if "Jupiter" in rs)


def _absolute_longitude(planet_info):
    """Absolute (sidereal) longitude reconstructed from the Lal Kitab fixed
    house (= sign index + 1) and the degree within that sign — used only for
    the combustion orb check (A6), since fixed-house identity alone loses the
    within-sign degree needed for a 10-degree Sun orb."""
    return (planet_info["fixed_house"] - 1) * 30 + planet_info["deg_in_sign"]


def build_timing_signals(age, fixed_chart, pakka, sleeping):
    """Raw four-signal timing-engine outputs — deterministic only. The skill's
    Phase 8D layers the event mapping, filters and convergence ranking on top."""
    planets = fixed_chart["planets"]
    house = {p: planets[p]["fixed_house"] for p in LK_PLANETS}

    # Signal 1 — maturation ages with the planet's delivery posture.
    # timing.md Signal 1: "combust (within 10 deg of Sun) -> maturation
    # distorted" (A6) — computed from the reconstructed absolute longitude,
    # independent of the sleeping/dignity-based delivery switch below.
    sun_lon = _absolute_longitude(planets["Sun"])
    maturation = {}
    for p in LK_PLANETS:
        mage = MATURATION_AGE[p]
        dig = pakka[p]["lk_dignity"]
        if p != "Sun":
            p_lon = _absolute_longitude(planets[p])
            raw_diff = abs(p_lon - sun_lon) % 360
            orb = min(raw_diff, 360 - raw_diff)
            combust = orb < 10
        else:
            orb = 0.0
            combust = False
        if sleeping[p]["sleeping"]:
            delivery = "muted (sleeping — needs awakening trigger)"
        elif dig == "exalted":
            delivery = "amplified positive"
        elif dig == "own":
            delivery = "full positive"
        elif dig == "debilitated":
            delivery = "full negative"
        elif dig == "friend":
            delivery = "smooth modest positive"
        elif dig == "enemy":
            delivery = "friction"
        else:
            delivery = "neutral"
        if combust:
            delivery += " (combust — maturation distorted, Sun-domain interferes)"
        maturation[p] = {
            "maturation_age": mage,
            "delivery": delivery,
            "combust": combust,
            "orb_from_sun_deg": round(orb, 2),
        }

    # Signal 2 — year-ruler per age across a default 15-year window.
    window_start = age if age is not None else 1
    window = list(range(window_start, window_start + 16))
    year_rulers = {a: year_ruler(a) for a in window}

    # Signal 3 — which house is in active period across the window.
    house_cycle_bands = {}
    for a in window:
        active = []
        for h, bands in HOUSE_CYCLE.items():
            for lo, hi in bands:
                if lo <= a <= hi:
                    active.append(h)
        house_cycle_bands[a] = sorted(active)

    # Signal 4 — Jupiter sanctification: Jupiter year-rulers in window +
    # houses Jupiter aspects natally (the perpetual sanctification reach).
    jup_house = house["Jupiter"]
    jupiter_aspected_houses = sorted(aspected_houses("Jupiter", jup_house))
    jupiter_years_in_window = [y for y in JUPITER_YEARS if y in window]

    return {
        "signal_1_maturation": maturation,
        "signal_2_year_rulers": {
            "window": [window[0], window[-1]],
            "year_ruler_by_age": year_rulers,
        },
        "signal_3_house_cycle": {
            "cycle_model": "6-years-per-house (72-year completion, Joshi tradition)",
            "full_cycle_table": {str(h): HOUSE_CYCLE[h] for h in range(1, 13)},
            "active_house_by_age": house_cycle_bands,
        },
        "signal_4_jupiter_sanctification": {
            "jupiter_fixed_house": jup_house,
            "jupiter_aspects_houses": jupiter_aspected_houses,
            "jupiter_sleeping": sleeping["Jupiter"]["sleeping"],
            "jupiter_dignity": pakka["Jupiter"]["lk_dignity"],
            "all_jupiter_year_rulers": JUPITER_YEARS,
            "jupiter_years_in_window": jupiter_years_in_window,
        },
    }


# ====================================================================
# Assembly
# ====================================================================

def build_baseline(chart, age):
    d1 = chart["d1"]

    fixed_chart = build_fixed_house_chart(d1)
    pakka = build_pakka_ghar(fixed_chart)
    aspect_map = build_aspect_map(fixed_chart)
    sleeping = build_sleeping(fixed_chart, aspect_map)
    rin = build_rin_diagnosis(fixed_chart, pakka, aspect_map, sleeping)
    teva = build_teva(fixed_chart, pakka, sleeping, rin, aspect_map)
    varshphal = build_varshphal(age, pakka, sleeping, rin)
    timing = build_timing_signals(age, fixed_chart, pakka, sleeping)

    return {
        "chart_type": "lalkitab_baseline",
        "methodology_note": (
            "Lal Kitab fixed-house frame (Aries=1). Dignity by house number "
            "per Lal Kitab tables, not Parashari. D1 only — no D9, nakshatras "
            "or Vimshottari. Interpretation stays in the skill."),
        "datetime_local": chart.get("datetime_local"),
        "datetime_utc": chart.get("datetime_utc"),
        "location": chart.get("location"),
        "ayanamsa": chart.get("ayanamsa"),
        "age": age,
        "fixed_house_chart": fixed_chart,
        "pakka_ghar": pakka,
        "aspect_map": aspect_map,
        "sleeping_planets": sleeping,
        "rin_diagnosis": rin,
        "teva": teva,
        "varshphal": varshphal,
        "timing_signals": timing,
    }


def _validate_chart(chart):
    """Ensure the loaded chart has the D1 shape Lal Kitab needs."""
    if "d1" not in chart:
        raise ValueError("chart JSON missing 'd1' block")
    d1 = chart["d1"]
    if "lagna_sign" not in d1 or "planets" not in d1:
        raise ValueError("chart 'd1' must contain 'lagna_sign' and 'planets'")
    missing = [p for p in LK_PLANETS if p not in d1["planets"]]
    if missing:
        raise ValueError("chart 'd1.planets' missing: " + ", ".join(missing))


def main():
    ap = argparse.ArgumentParser(
        description="Compute the deterministic Lal Kitab Step-0 baseline.")
    ap.add_argument("--datetime", help="Birth datetime, ISO format")
    ap.add_argument("--tz", help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--lat", type=float, help="Latitude (decimal degrees)")
    ap.add_argument("--lon", type=float, help="Longitude (decimal degrees)")
    ap.add_argument("--chart", help="Path to a pre-computed parashari_natal_chart JSON")
    ap.add_argument("--age", type=int, help="Current age (for Varshphal / timing windows)")
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
        # Lal Kitab does not mandate an ayanamsa — default to Lahiri.
        chart = eph.parashari_natal_chart(args.datetime, args.tz, args.lat, args.lon,
                                          ayanamsa_mode="lahiri")

    _validate_chart(chart)
    baseline = build_baseline(chart, args.age)
    print(json.dumps(baseline, indent=2, default=str))


if __name__ == "__main__":
    main()
