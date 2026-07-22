#!/usr/bin/env python3
"""
Jyotish shared primitives — pure functions, no I/O, no ephemeris.

Imported by lib/ephemeris.py and every scripts/compute_*_baseline.py.
This is the single, lossless source of truth for the deterministic data and
math that the six skills used to repeat in-prompt: signs, nakshatras,
Vimshottari, navamsa, degree flags, Parashari dignity, sign/house arithmetic.

Per-school methodology (Jaimini drishti, KP sub-lords, Lal Kitab tables, BNN
karaka logic) is NOT here — that lives in each scripts/compute_<school>.py.
"""

# ====================================================================
# Constants
# ====================================================================

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# Aries=Fire, Taurus=Earth, Gemini=Air, Cancer=Water, then repeats.
SIGN_ELEMENT = ["Fire", "Earth", "Air", "Water"] * 3
# Aries=Movable, Taurus=Fixed, Gemini=Dual, Cancer=Movable, then repeats.
SIGN_QUALITY = ["Movable", "Fixed", "Dual"] * 4

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# (name, star_lord) — star-lord follows the Vimshottari order across the zodiac.
NAKSHATRAS = [
    ("Ashwini", "Ketu"), ("Bharani", "Venus"), ("Krittika", "Sun"),
    ("Rohini", "Moon"), ("Mrigashira", "Mars"), ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"), ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"), ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"), ("Chitra", "Mars"), ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"), ("Anuradha", "Saturn"), ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"), ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"), ("Dhanishtha", "Mars"), ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]

# Gana (temperament) per nakshatra — same index order as NAKSHATRAS.
NAKSHATRA_GANA = [
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya",
    "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya",
    "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa",
    "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa",
    "Manushya", "Manushya", "Deva",
]

VIM_SEQ = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
             "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

NAK_ARC = 360.0 / 27.0      # 13°20'
NAVAMSA_ARC = 30.0 / 9.0    # 3°20'
TOTAL_VIM = 120
YEAR_DAYS = 365.25

# Python weekday() Mon=0..Sun=6
WEEKDAY_LORDS = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
                 4: "Venus", 5: "Saturn", 6: "Sun"}

# Navamsa start sign index by D1 element.
_NAVAMSA_START = {"Fire": 0, "Earth": 9, "Air": 6, "Water": 3}

# Combustion orbs (degrees from the Sun). Parashari family (vedic, bnn).
COMBUSTION_ORBS = {"Moon": 12.0, "Mars": 17.0, "Mercury": 14.0,
                   "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0}
COMBUSTION_ORBS_RETRO = {"Mercury": 12.0, "Venus": 8.0}

# Planets that can wage Graha Yuddha.
WAR_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Mrityu Bhaga degree by planet, indexed by sign (0=Aries..11=Pisces).
# A planet within +/-1 deg of this degree-in-sign struggles to deliver.
MRITYU_BHAGA = {
    "Sun":     [20, 9, 12, 6, 3, 24, 21, 18, 15, 12, 9, 27],
    "Moon":    [26, 12, 13, 25, 24, 11, 26, 14, 13, 25, 25, 12],
    "Mars":    [2, 28, 14, 11, 10, 27, 4, 11, 13, 19, 28, 14],
    "Mercury": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4],
    "Jupiter": [11, 29, 14, 20, 18, 15, 14, 21, 29, 10, 13, 28],
    "Venus":   [9, 23, 24, 23, 24, 23, 9, 15, 22, 24, 23, 15],
    "Saturn":  [21, 20, 16, 18, 17, 16, 21, 22, 19, 20, 23, 24],
    "Lagna":   [18, 16, 14, 12, 10, 8, 6, 4, 2, 28, 26, 24],
}

# Pushkara Bhaga — single auspicious degree per sign (0=Aries..11=Pisces),
# element-based: Fire 21deg, Earth 14deg, Air 24deg, Water 7deg.
# Source: Komilla Sutton, "The Nakshatras" / komilla.com Pushkara reference;
# cross-checked so each sign's Bhaga falls inside one of its Pushkara Navamsa
# arcs below. (Corrected 2026-07; the prior per-sign values were internally
# inconsistent with the navamsa arcs — e.g. Aries Bhaga 21deg fell outside both.)
PUSHKARA_BHAGA = {
    0: [21], 1: [14], 2: [24], 3: [7], 4: [21], 5: [14],
    6: [24], 7: [7], 8: [21], 9: [14], 10: [24], 11: [7],
}

# Pushkara Navamsa — auspicious 3deg20' zones per sign, as (start, end) in-sign.
# Element-based (Komilla Sutton): each element shares one pair of navamsa arcs.
#   Fire  (Ar/Le/Sg): 20deg00'-23deg20' and 26deg40'-30deg00'
#   Earth (Ta/Vi/Cp):  6deg40'-10deg00' and 13deg20'-16deg40'
#   Air   (Ge/Li/Aq): 16deg40'-20deg00' and 23deg20'-26deg40'
#   Water (Cn/Sc/Pi):  0deg00'- 3deg20' and  6deg40'-10deg00'
PUSHKARA_NAVAMSA = {
    0: [(20.0, 23.3333), (26.6667, 30.0)],
    1: [(6.6667, 10.0), (13.3333, 16.6667)],
    2: [(16.6667, 20.0), (23.3333, 26.6667)],
    3: [(0.0, 3.3333), (6.6667, 10.0)],
    4: [(20.0, 23.3333), (26.6667, 30.0)],
    5: [(6.6667, 10.0), (13.3333, 16.6667)],
    6: [(16.6667, 20.0), (23.3333, 26.6667)],
    7: [(0.0, 3.3333), (6.6667, 10.0)],
    8: [(20.0, 23.3333), (26.6667, 30.0)],
    9: [(6.6667, 10.0), (13.3333, 16.6667)],
    10: [(16.6667, 20.0), (23.3333, 26.6667)],
    11: [(0.0, 3.3333), (6.6667, 10.0)],
}

# Parashari dignity — (exalt_sign_idx, exalt_deg), debilitation = exalt + 6 signs.
EXALTATION = {
    "Sun": (0, 10), "Moon": (1, 3), "Mars": (9, 28), "Mercury": (5, 15),
    "Jupiter": (3, 5), "Venus": (11, 27), "Saturn": (6, 20),
}
# Own signs by planet (sign indices).
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10],
}
# Moolatrikona — (sign_idx, start_deg, end_deg).
MOOLATRIKONA = {
    "Sun": (4, 0, 20), "Moon": (1, 4, 30), "Mars": (0, 0, 12),
    "Mercury": (5, 16, 20), "Jupiter": (8, 0, 10), "Venus": (6, 0, 15),
    "Saturn": (10, 0, 20),
}
# Node dignity (school-dependent) per references/chart-tables.md.
# Sign indices: Taurus=1, Gemini=2, Scorpio=7, Sagittarius=8.
NODE_EXALT = {"Rahu": [1, 2], "Ketu": [7, 8]}
NODE_DEBIL = {"Rahu": [7, 8], "Ketu": [1, 2]}
# Natural friendships (Parashari).
NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
}
NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
}

# Parashari special aspects — house-distances aspected (besides universal 7th).
SPECIAL_ASPECTS = {"Mars": [4, 8], "Jupiter": [5, 9], "Saturn": [3, 10]}


# ====================================================================
# Basic helpers
# ====================================================================

def norm360(x):
    """Normalise a longitude to [0, 360)."""
    return x % 360.0


def deg_to_dms(deg):
    """Decimal degrees -> 'DDD-MM-SS' string."""
    d = int(deg)
    mf = (deg - d) * 60
    m = int(mf)
    s = int((mf - m) * 60)
    return f"{d:03d}-{m:02d}-{s:02d}"


def get_sign(lon):
    """Return (sign_idx, sign_name, sign_lord) for a sidereal longitude."""
    lon = norm360(lon)
    idx = int(lon // 30)
    return idx, SIGNS[idx], SIGN_LORDS[idx]


def deg_in_sign(lon):
    """Degrees within the current sign, 0..30."""
    return norm360(lon) % 30.0


def get_nakshatra(lon):
    """Return (nak_idx, name, star_lord, nak_start_deg)."""
    lon = norm360(lon)
    idx = int(lon // NAK_ARC)
    name, star_lord = NAKSHATRAS[idx]
    return idx, name, star_lord, idx * NAK_ARC


def get_pada(lon):
    """Return the nakshatra pada (1-4) for a longitude."""
    _idx, _n, _sl, nak_start = get_nakshatra(lon)
    pos = norm360(lon) - nak_start
    return int(pos // (NAK_ARC / 4)) + 1


def gana_of(lon):
    """Return the Gana (Deva / Manushya / Rakshasa) of the nakshatra at lon."""
    return NAKSHATRA_GANA[int(norm360(lon) // NAK_ARC)]


def get_sub_and_subsub(lon):
    """Return (sub_lord, sub_sub_lord) — KP-style Vimshottari subdivisions."""
    lon = norm360(lon)
    _ni, _name, star_lord, nak_start = get_nakshatra(lon)
    pos = lon - nak_start
    start_idx = VIM_SEQ.index(star_lord)
    cum = 0.0
    sub_lord, sub_start, sub_arc = None, 0.0, 0.0
    for off in range(9):
        lord = VIM_SEQ[(start_idx + off) % 9]
        arc = (VIM_YEARS[lord] / TOTAL_VIM) * NAK_ARC
        if cum <= pos < cum + arc:
            sub_lord, sub_start, sub_arc = lord, cum, arc
            break
        cum += arc
    if sub_lord is None:
        sub_lord = VIM_SEQ[(start_idx + 8) % 9]
        sub_arc = (VIM_YEARS[sub_lord] / TOTAL_VIM) * NAK_ARC
        sub_start = NAK_ARC - sub_arc
    pos_in_sub = pos - sub_start
    sub_idx = VIM_SEQ.index(sub_lord)
    cum2 = 0.0
    subsub = None
    for off in range(9):
        lord = VIM_SEQ[(sub_idx + off) % 9]
        arc2 = (VIM_YEARS[lord] / TOTAL_VIM) * sub_arc
        if cum2 <= pos_in_sub < cum2 + arc2:
            subsub = lord
            break
        cum2 += arc2
    if subsub is None:
        subsub = VIM_SEQ[(sub_idx + 8) % 9]
    return sub_lord, subsub


def get_sub_lord(lon):
    """Return only the KP sub-lord for a longitude."""
    return get_sub_and_subsub(lon)[0]


def full_lord_chain(lon):
    """Return the full sign/star/sub/sub-sub lord chain for a longitude."""
    lon = norm360(lon)
    si, sign, sign_lord = get_sign(lon)
    ni, nak, star_lord, _ns = get_nakshatra(lon)
    sub, subsub = get_sub_and_subsub(lon)
    return {
        "longitude": round(lon, 4),
        "longitude_dms": deg_to_dms(lon),
        "sign": sign,
        "sign_lord": sign_lord,
        "deg_in_sign": round(deg_in_sign(lon), 4),
        "nakshatra": nak,
        "pada": get_pada(lon),
        "star_lord": star_lord,
        "sub_lord": sub,
        "sub_sub_lord": subsub,
    }


# ====================================================================
# Sign / house arithmetic
# ====================================================================

def count_signs(from_sign_idx, to_sign_idx):
    """Inclusive count of signs from one to another, zodiacally (1-12)."""
    return ((to_sign_idx - from_sign_idx) % 12) + 1


def sign_n_from(sign_idx, n):
    """The sign index n places from sign_idx, counted inclusively (n=1 -> itself)."""
    return (sign_idx + n - 1) % 12


def house_of(planet_sign_idx, lagna_sign_idx):
    """Whole-sign house number (1-12) of a sign given the Lagna sign."""
    return count_signs(lagna_sign_idx, planet_sign_idx)


# ====================================================================
# Navamsa (D9)
# ====================================================================

def navamsa_sign(lon):
    """Return (d9_sign_idx, d9_sign_name) for a D1 sidereal longitude."""
    si = int(norm360(lon) // 30)
    start = _NAVAMSA_START[SIGN_ELEMENT[si]]
    nav_idx = int(deg_in_sign(lon) // NAVAMSA_ARC)
    d9 = (start + nav_idx) % 12
    return d9, SIGNS[d9]


def is_vargottama(lon):
    """True if the D1 sign equals the D9 sign for this longitude."""
    si = int(norm360(lon) // 30)
    return navamsa_sign(lon)[0] == si


# ====================================================================
# Degree flags
# ====================================================================

def gandanta(lon):
    """True if the longitude falls in a water->fire Gandanta zone (last 3deg20'
    of Cancer/Scorpio/Pisces or first 3deg20' of Leo/Sagittarius/Aries)."""
    si = int(norm360(lon) // 30)
    d = deg_in_sign(lon)
    if si in (3, 7, 11) and d >= 26.6667:      # Cancer/Scorpio/Pisces tail
        return True
    if si in (4, 8, 0) and d <= 3.3333:        # Leo/Sagittarius/Aries head
        return True
    return False


def sandhi(lon):
    """Return 'early' (0-1deg), 'late' (29-30deg) or None."""
    d = deg_in_sign(lon)
    if d < 1.0:
        return "early"
    if d >= 29.0:
        return "late"
    return None


def mrityu_bhaga(planet, lon, orb=1.0):
    """True if a planet sits within +/-orb of its Mrityu Bhaga degree."""
    if planet not in MRITYU_BHAGA:
        return False
    si = int(norm360(lon) // 30)
    return abs(deg_in_sign(lon) - MRITYU_BHAGA[planet][si]) <= orb


def pushkara_bhaga(lon, orb=1.0):
    """True if the longitude sits within +/-orb of a Pushkara Bhaga degree."""
    si = int(norm360(lon) // 30)
    d = deg_in_sign(lon)
    return any(abs(d - pb) <= orb for pb in PUSHKARA_BHAGA[si])


def pushkara_navamsa(lon):
    """True if the longitude falls inside a Pushkara Navamsa zone."""
    si = int(norm360(lon) // 30)
    d = deg_in_sign(lon)
    return any(lo <= d < hi for lo, hi in PUSHKARA_NAVAMSA[si])


def combustion(planet, planet_lon, sun_lon, retrograde=False):
    """True if a planet is combust (within the Sun's orb)."""
    if planet not in COMBUSTION_ORBS:
        return False
    orb = COMBUSTION_ORBS[planet]
    if retrograde and planet in COMBUSTION_ORBS_RETRO:
        orb = COMBUSTION_ORBS_RETRO[planet]
    sep = abs(norm360(planet_lon) - norm360(sun_lon))
    sep = min(sep, 360 - sep)
    return sep <= orb


def planetary_war(positions):
    """Detect Graha Yuddha. `positions` maps planet -> sidereal longitude.
    Returns a list of {winner, loser, separation} for war-eligible pairs
    within 1deg in the same sign. Lower degree-in-sign wins."""
    wars = []
    elig = [p for p in WAR_PLANETS if p in positions]
    for i in range(len(elig)):
        for j in range(i + 1, len(elig)):
            a, b = elig[i], elig[j]
            la, lb = norm360(positions[a]), norm360(positions[b])
            if int(la // 30) != int(lb // 30):
                continue
            sep = abs(la - lb)
            if sep <= 1.0:
                winner, loser = (a, b) if la <= lb else (b, a)
                wars.append({"winner": winner, "loser": loser,
                             "separation": round(sep, 4)})
    return wars


def degree_flags(planet, lon, sun_lon=None, retrograde=False):
    """Bundle every degree flag for one planet into a dict."""
    flags = {
        "gandanta": gandanta(lon),
        "sandhi": sandhi(lon),
        "mrityu_bhaga": mrityu_bhaga(planet, lon),
        "pushkara_bhaga": pushkara_bhaga(lon),
        "pushkara_navamsa": pushkara_navamsa(lon),
        "vargottama": is_vargottama(lon),
    }
    if sun_lon is not None and planet != "Sun":
        flags["combust"] = combustion(planet, lon, sun_lon, retrograde)
    return flags


# ====================================================================
# Parashari dignity
# ====================================================================

def dignity(planet, lon):
    """Return the Parashari placement dignity of a planet at a longitude:
    'exalted' | 'debilitated' | 'moolatrikona' | 'own' | 'friend' |
    'neutral' | 'enemy' | 'n/a'. Rahu/Ketu resolve to exalted /
    debilitated / neutral per references/chart-tables.md."""
    si = int(norm360(lon) // 30)
    if planet in ("Rahu", "Ketu"):
        if si in NODE_EXALT[planet]:
            return "exalted"
        if si in NODE_DEBIL[planet]:
            return "debilitated"
        return "neutral"
    if planet not in EXALTATION:
        return "n/a"
    d = deg_in_sign(lon)
    ex_sign, _ex_deg = EXALTATION[planet]
    if si == ex_sign:
        return "exalted"
    if si == (ex_sign + 6) % 12:
        return "debilitated"
    mt_sign, mt_lo, mt_hi = MOOLATRIKONA[planet]
    if si == mt_sign and mt_lo <= d < mt_hi:
        return "moolatrikona"
    if si in OWN_SIGNS[planet]:
        return "own"
    disp = SIGN_LORDS[si]
    if disp == planet:
        return "own"
    if disp in NATURAL_FRIENDS.get(planet, []):
        return "friend"
    if disp in NATURAL_ENEMIES.get(planet, []):
        return "enemy"
    return "neutral"


# ====================================================================
# Vimshottari dasha
# ====================================================================

def vimshottari_balance(moon_lon):
    """Return (mahadasha_lord, balance_years, elapsed_years) at birth from the
    Moon's sidereal longitude."""
    _ni, _name, star_lord, nak_start = get_nakshatra(moon_lon)
    fraction = (norm360(moon_lon) - nak_start) / NAK_ARC
    total = VIM_YEARS[star_lord]
    return star_lord, total * (1 - fraction), total * fraction


def build_dasha_tree(moon_lon, birth_dt, n_md=5):
    """Build the full Mahadasha->Bhukti->Antara->Sookshma tree from birth.
    `birth_dt` is a naive UTC datetime. Returns a list of MD dicts."""
    from datetime import timedelta
    star_lord, _bal, elapsed = vimshottari_balance(moon_lon)
    md_start = birth_dt - timedelta(days=elapsed * YEAR_DAYS)
    md_idx = VIM_SEQ.index(star_lord)
    tree = []
    for i in range(n_md):
        md_lord = VIM_SEQ[(md_idx + i) % 9]
        md_yrs = VIM_YEARS[md_lord]
        md_end = md_start + timedelta(days=md_yrs * YEAR_DAYS)
        bhuktis = []
        bd_start = md_start
        bd_idx = VIM_SEQ.index(md_lord)
        for bo in range(9):
            bd_lord = VIM_SEQ[(bd_idx + bo) % 9]
            bd_days = (md_yrs * VIM_YEARS[bd_lord] / TOTAL_VIM) * YEAR_DAYS
            bd_end = bd_start + timedelta(days=bd_days)
            antaras = []
            ad_start = bd_start
            ad_idx = VIM_SEQ.index(bd_lord)
            for ao in range(9):
                ad_lord = VIM_SEQ[(ad_idx + ao) % 9]
                ad_days = bd_days * VIM_YEARS[ad_lord] / TOTAL_VIM
                ad_end = ad_start + timedelta(days=ad_days)
                sookshmas = []
                sd_start = ad_start
                sd_idx = VIM_SEQ.index(ad_lord)
                for so in range(9):
                    sd_lord = VIM_SEQ[(sd_idx + so) % 9]
                    sd_days = ad_days * VIM_YEARS[sd_lord] / TOTAL_VIM
                    sd_end = sd_start + timedelta(days=sd_days)
                    sookshmas.append({"sd_lord": sd_lord,
                                      "start": sd_start.isoformat(),
                                      "end": sd_end.isoformat()})
                    sd_start = sd_end
                antaras.append({"ad_lord": ad_lord, "start": ad_start.isoformat(),
                                "end": ad_end.isoformat(), "sookshmas": sookshmas})
                ad_start = ad_end
            bhuktis.append({"bd_lord": bd_lord, "start": bd_start.isoformat(),
                            "end": bd_end.isoformat(), "antaras": antaras})
            bd_start = bd_end
        tree.append({"md_lord": md_lord, "start": md_start.isoformat(),
                     "end": md_end.isoformat(), "bhuktis": bhuktis})
        md_start = md_end
    return tree


def find_running(tree, target_dt):
    """Return the running MD-BD-AD-SD quartet at `target_dt`, or None."""
    from datetime import datetime
    def within(node):
        return (datetime.fromisoformat(node["start"]) <= target_dt
                < datetime.fromisoformat(node["end"]))
    for md in tree:
        if not within(md):
            continue
        for bd in md["bhuktis"]:
            if not within(bd):
                continue
            for ad in bd["antaras"]:
                if not within(ad):
                    continue
                for sd in ad["sookshmas"]:
                    if within(sd):
                        return {
                            "md_lord": md["md_lord"], "md_period": [md["start"], md["end"]],
                            "bd_lord": bd["bd_lord"], "bd_period": [bd["start"], bd["end"]],
                            "ad_lord": ad["ad_lord"], "ad_period": [ad["start"], ad["end"]],
                            "sd_lord": sd["sd_lord"], "sd_period": [sd["start"], sd["end"]],
                        }
    return None


def find_antara(tree, md_lord, bd_lord, ad_lord):
    """Return the named Antara block (with its sookshmas), or None."""
    for md in tree:
        if md["md_lord"] != md_lord:
            continue
        for bd in md["bhuktis"]:
            if bd["bd_lord"] != bd_lord:
                continue
            for ad in bd["antaras"]:
                if ad["ad_lord"] == ad_lord:
                    return ad
    return None
