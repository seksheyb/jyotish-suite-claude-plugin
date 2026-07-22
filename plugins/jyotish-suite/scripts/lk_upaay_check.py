#!/usr/bin/env python3
"""
lk_upaay_check.py — Lal Kitab upaay (remedy) candidate generator + conflict /
contraindication checker.

Deterministic delta script (blueprint §6 delta #3). This is NOT the upaay
prescriber. It reads a finalized `compute_lalkitab_baseline.py` JSON (active
rins with fired triggers + Farman citations, sleeping planets, teva, and
Varshphal danger years) and mechanically emits:

  * A candidate upaay list — one entry per catalog item whose trigger
    condition is satisfied by the baseline, each carrying the Farman citation
    that fired it (looked up from the baseline, not recalled).
  * `conflicts_with` — pairs of candidates that the catalog's §11 "do not
    combine" rules forbid running together, restricted to conflicts where
    BOTH members are actually candidates for this chart.
  * `contraindicated` — a bool + reason for candidates the catalog's §11
    pregnancy/health tables flag, gated on the optional `--flags` the caller
    supplies (pregnancy, diabetic, allergic).

What this script does NOT do: it does not rank, tier, or select "the"
remedies to prescribe. Tier assignment (Primary / severity-scaled / hard
rule / maintenance) and final narrative prescription is the synthesizer's
job in Wave 2 — this script only narrows "everything catalog-eligible" down
to "what actually fired for this chart, with conflicts/contraindications
already flagged" so the synthesizer isn't hallucinating trigger matches or
missing a caution under long context.

Source of truth for the catalog data below:
  plugins/jyotish-suite/skills/lal-kitab/references/upaay_catalog.md
If that file's upaay list, trigger conditions, conflict rules (§11), or
contraindication tables (§11) change, the CATALOG / CONFLICT_PAIRS /
PREGNANCY_CONTRAINDICATED / substitution sets below must be updated to match.
The rin-trigger-number mappings (which of the six rin script triggers each
catalog entry responds to) are this script's own best-effort interpretation
of each entry's prose "For:" line, cross-referenced against the trigger
descriptions compute_lalkitab_baseline.py emits — they are not literal
Farman text and should be revisited if the catalog's "For:" lines change.

Usage:
  lk_upaay_check.py --baseline lalkitab_baseline.json [--flags pregnancy,diabetic] [--out out.json]
"""

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# lib/ lives at the plugin root; resolve it whether scripts/ is one or three
# levels below that root (mirrors the other compute_*_baseline.py scripts).
for _cand in (os.path.join(_HERE, "..", "lib"),
              os.path.join(_HERE, "..", "..", "..", "lib")):
    if os.path.isfile(os.path.join(_cand, "jyotish_primitives.py")):
        sys.path.insert(0, _cand)
        break
try:
    import jyotish_primitives as jp  # noqa: E402  (imported for parity with
    # sibling baseline scripts even though this script only needs PLANETS)
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "lk_upaay_check.py could not import lib/jyotish_primitives.py. "
        "Run this script from within the jyotish-suite plugin tree, or "
        "verify lib/ sits at the plugin root next to scripts/. "
        f"Original error: {e}"
    ) from e


LK_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
              "Saturn", "Rahu", "Ketu"]

RIN_NAMES = ["pitri_rin", "matri_rin", "stri_rin", "kanya_rin",
             "bhratra_rin", "atma_rin"]

DANGER_YEARS = {21, 36, 42, 48, 63}


# ====================================================================
# Catalog data — mirrors references/upaay_catalog.md. Edit both together.
# ====================================================================
#
# Each rin-upaay entry:
#   id, label, action, frequency, caution, farman (catalog citation),
#   trigger_scope:
#     "any"      -> fires whenever the rin is active (any fired trigger)
#     [ints]     -> fires only if one of these script trigger numbers
#                   (compute_lalkitab_baseline.py's `fired_triggers[i]["trigger"]`)
#                   is present for that rin
#   requires_sleeping: optional planet name that must be sleeping (in
#                   addition to trigger_scope) — used where the catalog's
#                   "For:" line names a compounding sleeping-planet condition
#
CATALOG_RIN = {
    "pitri_rin": [
        {"id": "1.1", "label": "Flowing Water + Coconut + Almonds (Primary)",
         "action": "Float a coconut + 100g almonds in flowing water on amavasya; "
                    "do not look back while walking away.",
         "frequency": "Every amavasya, 6-12 months", "trigger_scope": "any",
         "farman": "Farman 8, Vol 2 (1940)"},
        {"id": "1.2", "label": "Wheat to Crows",
         "action": "Daily, before eating, place wheat-flour balls (with jaggery) "
                    "for crows on a rooftop/open ground. Native must do it personally.",
         "frequency": "Daily for 90 days minimum", "trigger_scope": [4, 5, 6, 7],
         "farman": "Farman 22, Vol 3 (1941)"},
        {"id": "1.3", "label": "Gold Ear-Piercing for Sons",
         "action": "Sons' ears pierced with gold before age 8; native wears a small "
                    "gold object daily as a modern substitute.",
         "frequency": "One-time", "trigger_scope": "any",
         "farman": "Farman 16, Vol 4 (1942) + modern adaptation noted"},
        {"id": "1.4", "label": "Donating Wheat at Religious Site",
         "action": "Donate 5kg raw wheat at a temple/gurudwara on Sunday morning, "
                    "without seeking acknowledgment.",
         "frequency": "Once/month for 11 months", "trigger_scope": "any",
         "requires_sleeping": "Sun",
         "farman": "Farman 8, Vol 2 (1940)"},
        {"id": "1.5", "label": "Sun Worship Ritual (Restricted)",
         "action": "Offer copper-vessel water + red sandalwood + red rice to the "
                    "rising sun daily, within the first hour of sunrise.",
         "frequency": "Daily for 1 year, ideally lifelong", "trigger_scope": [3],
         "farman": "Farman 12, Vol 1 (1939)"},
    ],
    "matri_rin": [
        {"id": "2.1", "label": "Silver Square (Primary)",
         "action": "Bury a solid silver square (>=10g) in the NE corner of the home "
                    "foundation, or keep in the puja-place/bedroom drawer.",
         "frequency": "One-time, check yearly", "trigger_scope": "any",
         "farman": "Farman 5, Vol 2 (1940)"},
        {"id": "2.2", "label": "Milk to Children",
         "action": "Distribute fresh milk to 5-10 unrelated children under 8.",
         "frequency": "Every Monday for 11 months", "trigger_scope": [5, 6],
         "farman": "Farman 9, Vol 2 (1940)"},
        {"id": "2.3", "label": "Water Vessel at Cremation Ground",
         "action": "Place a water-filled clay pot at a cremation ground; walk away "
                    "without turning back.",
         "frequency": "Once/year for 3 years, on birthday", "trigger_scope": [4, 7],
         "farman": "Farman 18, Vol 4 (1942)"},
        {"id": "2.4", "label": "White Items in Mother's Use",
         "action": "Gift mother white clothing/utensils/sweets; native avoids rice "
                    "that day.",
         "frequency": "Quarterly, ongoing", "trigger_scope": "any",
         "farman": "Farman 19, Vol 3 (1941)"},
        {"id": "2.5", "label": "Avoid Selling Cow's Milk",
         "action": "Never engage in milk-trade business (consuming/gifting is fine).",
         "frequency": "Lifetime restriction", "trigger_scope": "any",
         "farman": "Farman 5, Vol 2 (1940)"},
    ],
    "stri_rin": [
        {"id": "3.1", "label": "Donating Items in Mother-in-Law's Name",
         "action": "Donate clothing/food in the mother-in-law's name (specifically) "
                    "to elderly women on Fridays.",
         "frequency": "7 Fridays, then quarterly", "trigger_scope": [4, 5],
         "farman": "Farman 11, Vol 2 (1940)"},
        {"id": "3.2", "label": "Cow Donation / Cow Care",
         "action": "Sponsor a healthy milking cow's care at a goshala for 6+ months, "
                    "or gift one.",
         "frequency": "One-time or 6-month minimum", "trigger_scope": [1, 2, 3],
         "farman": "Farman 25, Vol 3 (1941)"},
        {"id": "3.3", "label": "Avoid Cremation Grounds Until Marriage",
         "action": "Native avoids shamshan ghat/funerals until married; donates in "
                    "lieu of attendance.",
         "frequency": "Until marriage", "trigger_scope": "any",
         "farman": "Farman 21, Vol 4 (1942)"},
        {"id": "3.4", "label": "White Flowers at Home",
         "action": "Keep fresh white flowers in water in the bedroom; replace before "
                    "wilting.",
         "frequency": "Continuous, while married", "trigger_scope": "any",
         "farman": "Farman 11, Vol 2 (1940)"},
        {"id": "3.5", "label": "No Black Clothing on Fridays",
         "action": "Never wear pure black on Fridays; white/cream/pastels preferred.",
         "frequency": "Lifetime", "trigger_scope": "any",
         "farman": "Modern Tradition (post-1970s clarification)"},
    ],
    "kanya_rin": [
        {"id": "4.1", "label": "Help in Daughter's Marriage",
         "action": "Contribute financially/organizationally to a non-own daughter's "
                    "marriage, voluntarily and undisclosed.",
         "frequency": "One-time per case", "trigger_scope": "any",
         "farman": "Farman 23, Vol 3 (1941)"},
        {"id": "4.2", "label": "Green-Items Restriction",
         "action": "Avoid commercial trade in green vegetables/clothing (personal "
                    "use is fine).",
         "frequency": "Lifetime", "trigger_scope": [1],
         "farman": "Farman 13, Vol 2 (1940)"},
        {"id": "4.3", "label": "Gifts to Young Girls",
         "action": "Gift small items to 5-10 girls under 12 on Wednesdays.",
         "frequency": "Monthly for 11 months", "trigger_scope": "any",
         "farman": "Farman 24, Vol 3 (1941)"},
    ],
    "bhratra_rin": [
        {"id": "5.1", "label": "Honey + Sweet Donation",
         "action": "Donate sealed honey (1kg+) and a pure-ghee sweet at a temple on "
                    "Tuesdays, in elder brother's name if applicable.",
         "frequency": "7 Tuesdays, then quarterly", "trigger_scope": [1, 3],
         "farman": "Farman 7, Vol 2 (1940)"},
        {"id": "5.2", "label": "Red Items Restriction",
         "action": "Avoid wearing pure red on Saturdays (red on other days, "
                    "especially Tuesday, is fine).",
         "frequency": "Lifetime", "trigger_scope": [2],
         "farman": "Farman 15, Vol 1 (1939)"},
        {"id": "5.3", "label": "Maintaining Brother Relationship",
         "action": "Maintain conscious contact with elder brother; gift on his "
                    "birthday and Bhai Dooj; contribute anonymously if estranged.",
         "frequency": "Ongoing", "trigger_scope": "any",
         "farman": "Farman 20, Vol 3 (1941)"},
    ],
    "atma_rin": [
        {"id": "6.1", "label": "Yellow / Saffron Cloth Practice",
         "action": "Wear a yellow/saffron thread daily, or keep saffron in the home "
                    "puja-area.",
         "frequency": "Continuous, lifetime", "trigger_scope": [1],
         "farman": "Farman 4, Vol 2 (1940)"},
        {"id": "6.2", "label": "Service in Religious / Spiritual Place",
         "action": "Volunteer physical (not just administrative) service at a "
                    "temple/gurudwara/ashram.",
         "frequency": "1 day/month for 1 year, ideally ongoing",
         "trigger_scope": [5], "farman": "Farman 33, Vol 5 (1952)"},
        {"id": "6.3", "label": "Vegetarian Restriction on Thursdays",
         "action": "Strictly vegetarian on Thursdays; no alcohol on Thursdays.",
         "frequency": "Lifetime", "trigger_scope": "any",
         "farman": "Modern Tradition (clarification of Farman 4, Vol 2 (1940))"},
        {"id": "6.4", "label": "Daughter / Niece Care",
         "action": "Take active, sustained responsibility in a daughter's or "
                    "niece's education/wellbeing.",
         "frequency": "Multi-year commitment", "trigger_scope": [3],
         "farman": "Farman 32, Vol 5 (1952)"},
    ],
}

# Section 7 — planet-specific strengthening. Fires when a planet is weak
# (sleeping OR Lal-Kitab debilitated/enemy dignity) per the baseline.
PLANET_STRENGTHENING = {
    "Sun": {"action": "Offer water from a copper vessel to the rising sun",
            "frequency": "Daily", "day": "Sunday emphasis", "farman": "F.12, V.1"},
    "Moon": {"action": "Drink water from a silver vessel",
             "frequency": "Daily", "day": "Monday emphasis", "farman": "F.5, V.2"},
    "Mars": {"action": "Donate sweets / honey to younger boys",
             "frequency": "Weekly", "day": "Tuesday", "farman": "F.7, V.2"},
    "Mercury": {"action": "Donate green moong dal",
                "frequency": "Weekly", "day": "Wednesday", "farman": "F.13, V.2"},
    "Jupiter": {"action": "Apply saffron tilak; donate yellow items",
                "frequency": "Weekly", "day": "Thursday", "farman": "F.4, V.2"},
    "Venus": {"action": "Donate white sweets; keep white flowers",
              "frequency": "Weekly", "day": "Friday", "farman": "F.11, V.2"},
    "Saturn": {"action": "Donate mustard oil (view own reflection in it first); "
                         "feed black ants",
               "frequency": "Weekly", "day": "Saturday", "farman": "F.10, V.2"},
    "Rahu": {"action": "Float coal in flowing water; bury jowar (sorghum)",
             "frequency": "Monthly", "day": "Saturday", "farman": "F.6, V.2"},
    "Ketu": {"action": "Keep a striped/multi-color blanket; donate sesame seeds",
             "frequency": "Monthly", "day": "Tuesday or Saturday", "farman": "F.6, V.2"},
}

# Section 8 — sleeping-planet awakening. One triplet per sleeping planet.
SLEEPING_AWAKENING_COLOR = {
    "Sun": "orange / saffron", "Moon": "white / cream", "Mars": "red",
    "Mercury": "green", "Jupiter": "yellow", "Venus": "white / pink",
    "Saturn": "dark blue / black (use sparingly)", "Rahu": "indigo / smoke gray",
    "Ketu": "multi-colored / brown",
}
# Friend of each planet used for the conjunction-simulation upaay (8.1) —
# references/pakka_ghar.md §5, mirrored here only to name a partner planet.
LK_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus", "Rahu"],
    "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn", "Rahu"],
    "Saturn": ["Mercury", "Venus", "Rahu"], "Rahu": ["Mercury", "Venus", "Saturn"],
    "Ketu": ["Mars", "Venus", "Saturn"],
}
KARAKA_ACTIVITY = {
    "Sun": "Take up a leadership/visibility role", "Moon": "Nurture emotional routines",
    "Mars": "Take up physical activity / sport", "Mercury": "Start writing / commerce",
    "Jupiter": "Teach or study formally", "Venus": "Spend on aesthetic home improvements",
    "Saturn": "Take up disciplined, long-duration work", "Rahu": "Engage foreign/unconventional pursuits",
    "Ketu": "Engage in solitary/spiritual practice",
}

# Section 9 — year-specific Varshphal upaay for the danger years.
VARSHPHAL_DANGER_UPAAY = {
    21: {"label": "Age 21 (Jupiter major)", "add": "Repeat Jupiter strengthening (7.Jupiter)",
         "restrict": None, "farman": "F.36, V.5"},
    36: {"label": "Age 36 (First Saturn Year)",
         "add": "Donate iron items (small iron utensils, iron nails) on Saturdays",
         "restrict": "Avoid major financial commitments in months 7-9 of the year",
         "farman": "F.10, V.2 + F.36, V.5"},
    42: {"label": "Age 42 (Saturn + Rahu — most dangerous year)",
         "add": "Donate mustard oil weekly all year; float coal in water on amavasyas",
         "restrict": "Avoid alcohol entirely; avoid risky travel in months 4-6",
         "farman": "F.42, V.5"},
    48: {"label": "Age 48 (Third Saturn Year)",
         "add": "Repeat Age-36 upaay; visit elderly parents / honor lineage actively",
         "restrict": "Career-consolidation rather than expansion",
         "farman": "F.48, V.5"},
    63: {"label": "Age 63 (Rahu Major)",
         "add": "Daily reading of a chosen sacred text (15+ minutes)",
         "restrict": "Avoid taking on new business ventures",
         "farman": "F.63, V.5"},
}

# Section 10 — universal maintenance, always candidates, never contraindicated.
UNIVERSAL_MAINTENANCE = [
    {"id": "10.1", "label": "Charity on birthday",
     "action": "Donate something every birthday (any planet, any item)."},
    {"id": "10.2", "label": "Cleanliness in NE corner",
     "action": "Never store junk, broken items, or shoes in the NE corner of the home."},
    {"id": "10.3", "label": "No shoe-on-shoe stacking",
     "action": "Keep shoes flat-side up, never stacked sole-up."},
    {"id": "10.4", "label": "No feet pointing north while sleeping",
     "action": "Avoid sleeping with feet pointing north (affects Pitri energies)."},
    {"id": "10.5", "label": "Water vessel near bed",
     "action": "Keep a small water vessel near the bed; empty in morning, refill at night."},
    {"id": "10.6", "label": "Respect to elders",
     "action": "Disrespect to elders actively damages Sun/Saturn per Lal Kitab."},
]

# ====================================================================
# §11 conflict pairs — "do not combine simultaneously".
# ====================================================================
CONFLICT_PAIRS = [
    ("1.1", "1.5"),                 # explicit caution on 1.5: never same morning as 1.1
    ("1.5", "7.Saturn"),            # Sun strengthening + Saturn upaay same day
    ("7.Mars", "7.Mercury"),        # Mars + Mercury strengthening same day (enemies)
    ("8.3_Mars", "8.3_Saturn"),     # wearing red (Mars) and black (Saturn) together
]

# ====================================================================
# §11 contraindications — pregnancy / health, gated on --flags.
# ====================================================================
PREGNANCY_CONTRAINDICATED = {
    "2.3": "cremation-ground vessel — never during pregnancy (§11 pregnancy contraindications)",
}
DIABETIC_SUBSTITUTION = {
    "5.1": "sweet-donation upaay — substitute jaggery for sugar (§11 health contraindications)",
    "2.4": "white-sweets gift — substitute jaggery for sugar (§11 health contraindications)",
    "7.Venus": "sweet-donation upaay — substitute jaggery for sugar (§11 health contraindications)",
}
ALLERGIC_SUBSTITUTION = {
    "1.1": "contains almonds — substitute an allergen-free item, state the substitution intent (§11 health contraindications)",
    "1.2": "contains wheat flour — substitute an allergen-free item, state the substitution intent (§11 health contraindications)",
    "1.4": "raw wheat donation — substitute an allergen-free item, state the substitution intent (§11 health contraindications)",
}
KNOWN_FLAGS = {"pregnancy", "diabetic", "allergic"}


# ====================================================================
# Candidate generation
# ====================================================================

def _fired_trigger_lookup(rin_record):
    """Map trigger-number -> {desc, farman} for one rin's fired_triggers."""
    return {t["trigger"]: {"desc": t["desc"], "farman": t["farman"]}
            for t in rin_record.get("fired_triggers", [])}


def _rin_candidates(rin_diagnosis, sleeping):
    out = []
    rins = rin_diagnosis.get("rins", {})
    for rin_name in RIN_NAMES:
        record = rins.get(rin_name)
        if not record or not record.get("triggered"):
            continue
        fired = _fired_trigger_lookup(record)
        for entry in CATALOG_RIN[rin_name]:
            scope = entry["trigger_scope"]
            matched_numbers = []
            if scope == "any":
                matched_numbers = sorted(fired.keys())
            else:
                matched_numbers = [n for n in scope if n in fired]
                if not matched_numbers:
                    continue

            req_sleep = entry.get("requires_sleeping")
            if req_sleep and not sleeping.get(req_sleep, {}).get("sleeping", False):
                continue

            trigger_citations = [
                {"trigger_number": n, "desc": fired[n]["desc"], "farman": fired[n]["farman"]}
                for n in matched_numbers
            ] if matched_numbers else []

            out.append({
                "id": entry["id"],
                "category": "rin_upaay",
                "rin": rin_name,
                "label": entry["label"],
                "action": entry["action"],
                "frequency": entry["frequency"],
                "farman": entry["farman"],
                "trigger": {
                    "source": "rin",
                    "rin": rin_name,
                    "severity": record["severity"],
                    "matched_triggers": trigger_citations if trigger_citations else "any (rin active, no specific trigger required)",
                    "requires_sleeping": req_sleep,
                },
            })
    return out


def _planet_strengthening_candidates(pakka_ghar, sleeping):
    out = []
    for planet in LK_PLANETS:
        dignity = pakka_ghar.get(planet, {}).get("lk_dignity")
        is_sleeping = sleeping.get(planet, {}).get("sleeping", False)
        weak = is_sleeping or dignity in ("debilitated", "enemy")
        if not weak:
            continue
        spec = PLANET_STRENGTHENING[planet]
        out.append({
            "id": f"7.{planet}",
            "category": "planet_strengthening",
            "label": f"{planet} Strengthening",
            "action": spec["action"],
            "frequency": f"{spec['frequency']} ({spec['day']})",
            "farman": spec["farman"],
            "trigger": {
                "source": "planet",
                "planet": planet,
                "reason": ("sleeping" if is_sleeping else f"lk_dignity={dignity}"),
            },
        })
    return out


def _sleeping_awakening_candidates(sleeping):
    out = []
    for planet in LK_PLANETS:
        if not sleeping.get(planet, {}).get("sleeping", False):
            continue
        friends = LK_FRIENDS.get(planet, [])
        friend = friends[0] if friends else None
        out.append({
            "id": f"8.1_{planet}",
            "category": "sleeping_awakening",
            "label": f"Conjunction-Simulation for sleeping {planet}",
            "action": (f"Wear/carry an item associated with {friend} (a friend of "
                       f"{planet}) to symbolically awaken it." if friend else
                       f"No catalogued friend planet found for {planet} in the "
                       "friendship table — flag for manual review."),
            "frequency": "Sustained until awakened",
            "farman": "§8 catalog (no independent Farman; extension of the "
                      "planet's own strengthening Farman)",
            "trigger": {"source": "planet", "planet": planet, "reason": "sleeping"},
        })
        out.append({
            "id": f"8.2_{planet}",
            "category": "sleeping_awakening",
            "label": f"Karaka-Activity Awakening for sleeping {planet}",
            "action": KARAKA_ACTIVITY.get(planet, "Engage the planet's natural activity"),
            "frequency": "Sustained until the planet's varshphal year activates",
            "farman": "§8 catalog (no independent Farman)",
            "trigger": {"source": "planet", "planet": planet, "reason": "sleeping"},
        })
        out.append({
            "id": f"8.3_{planet}",
            "category": "sleeping_awakening",
            "label": f"Color-Field Awakening for sleeping {planet}",
            "action": f"Keep {SLEEPING_AWAKENING_COLOR[planet]} in daily-use items "
                      "(bag, towel, room curtains).",
            "frequency": "Continuous",
            "farman": "§8 catalog (no independent Farman)",
            "trigger": {"source": "planet", "planet": planet, "reason": "sleeping"},
        })
    return out


def _varshphal_candidates(varshphal):
    out = []
    if not varshphal or "current_year" not in varshphal:
        return out
    years_to_check = []
    cur = varshphal.get("current_year")
    if cur:
        years_to_check.append(cur)
    years_to_check.extend(varshphal.get("next_5_years", []))
    seen_ages = set()
    for year_entry in years_to_check:
        age = year_entry.get("age")
        if age not in DANGER_YEARS or age in seen_ages:
            continue
        seen_ages.add(age)
        spec = VARSHPHAL_DANGER_UPAAY.get(age)
        if not spec:
            continue
        out.append({
            "id": f"9.{age}",
            "category": "varshphal_danger_year",
            "label": spec["label"],
            "action": spec["add"],
            "restriction": spec["restrict"],
            "frequency": "For the duration of that Varshphal year",
            "farman": spec["farman"],
            "trigger": {
                "source": "varshphal",
                "age": age,
                "danger_year": True,
                "year_rulers": year_entry.get("year_rulers"),
                "is_current_age": (age == varshphal.get("current_age")),
            },
        })
    return out


def _universal_candidates():
    out = []
    for entry in UNIVERSAL_MAINTENANCE:
        out.append({
            "id": entry["id"],
            "category": "universal_maintenance",
            "label": entry["label"],
            "action": entry["action"],
            "frequency": "Ongoing",
            "farman": "§10 catalog (recommended regardless of specific findings)",
            "trigger": {"source": "universal", "reason": "always applicable, all natives"},
        })
    return out


def _apply_conflicts(candidates):
    ids_present = {c["id"] for c in candidates}
    conflicts_by_id = {c["id"]: [] for c in candidates}
    active_pairs = []
    for a, b in CONFLICT_PAIRS:
        if a in ids_present and b in ids_present:
            conflicts_by_id[a].append(b)
            conflicts_by_id[b].append(a)
            active_pairs.append([a, b])
    for c in candidates:
        c["conflicts_with"] = conflicts_by_id[c["id"]]
    return active_pairs


def _apply_contraindications(candidates, flags):
    unknown = sorted(set(flags) - KNOWN_FLAGS)
    for c in candidates:
        reasons = []
        if "pregnancy" in flags and c["id"] in PREGNANCY_CONTRAINDICATED:
            reasons.append(PREGNANCY_CONTRAINDICATED[c["id"]])
        if "diabetic" in flags and c["id"] in DIABETIC_SUBSTITUTION:
            reasons.append(DIABETIC_SUBSTITUTION[c["id"]])
        if "allergic" in flags and c["id"] in ALLERGIC_SUBSTITUTION:
            reasons.append(ALLERGIC_SUBSTITUTION[c["id"]])
        c["contraindicated"] = bool(reasons)
        c["contraindication_reason"] = "; ".join(reasons) if reasons else None
    return unknown


def build_upaay_check(baseline, flags):
    rin_diagnosis = baseline.get("rin_diagnosis", {})
    sleeping = baseline.get("sleeping_planets", {})
    pakka_ghar = baseline.get("pakka_ghar", {})
    varshphal = baseline.get("varshphal", {})
    teva = baseline.get("teva", {})

    candidates = []
    candidates += _rin_candidates(rin_diagnosis, sleeping)
    candidates += _planet_strengthening_candidates(pakka_ghar, sleeping)
    candidates += _sleeping_awakening_candidates(sleeping)
    candidates += _varshphal_candidates(varshphal)
    candidates += _universal_candidates()

    active_conflict_pairs = _apply_conflicts(candidates)
    unknown_flags = _apply_contraindications(candidates, flags)

    return {
        "methodology_note": (
            "Candidate upaay list only — NOT tiered. Tier assignment "
            "(Primary / severity-scaled / hard-rule / maintenance) and final "
            "prescription narrative stay with the synthesizer. Every "
            "candidate's trigger and Farman citation is looked up from the "
            "baseline JSON or the catalog, never recalled."),
        "flags_applied": sorted(set(flags) & KNOWN_FLAGS),
        "unknown_flags_ignored": unknown_flags,
        "teva_context": {
            "dominant": teva.get("dominant", {}).get("teva"),
            "note": ("Teva is descriptive context only — the catalog has no "
                     "teva-indexed remedies; it does not gate candidate "
                     "generation."),
        },
        "candidate_count": len(candidates),
        "candidates": candidates,
        "conflict_pairs_flagged": active_conflict_pairs,
        "contraindicated_count": sum(1 for c in candidates if c["contraindicated"]),
    }


def main():
    ap = argparse.ArgumentParser(
        description="Generate Lal Kitab upaay candidates with conflict / "
                     "contraindication flags from a finalized baseline JSON.")
    ap.add_argument("--baseline", required=True,
                     help="Path to compute_lalkitab_baseline.py output JSON")
    ap.add_argument("--flags", default="",
                     help="Comma-separated context flags, e.g. "
                          "'pregnancy,diabetic,allergic'")
    ap.add_argument("--out", help="Write JSON to this path instead of stdout")
    args = ap.parse_args()

    with open(args.baseline) as f:
        baseline = json.load(f)

    flags = [f.strip().lower() for f in args.flags.split(",") if f.strip()]

    result = build_upaay_check(baseline, flags)
    payload = json.dumps(result, indent=2, default=str)

    if args.out:
        with open(args.out, "w") as f:
            f.write(payload)
        print(f"Wrote upaay check to {args.out}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
