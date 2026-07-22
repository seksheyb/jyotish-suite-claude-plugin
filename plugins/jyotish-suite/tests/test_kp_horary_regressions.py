#!/usr/bin/env python3
"""
Regression guard for the kp-horary bugfix wave.

Standalone (no pytest): plain asserts, prints PASS/FAIL per class, exits
non-zero if any bug reappears. Mirrors the style of tests/run_golden.py.

Each check pins one defect class fixed in the wave:

  1. Combustion — every planet carries a `combust` bool computed with the
     uniform KP 8.5° orb (NOT jp.COMBUSTION_ORBS' Parashari 10-17° orbs).
  2. Sandhi — horary_lagna carries a `sandhi` / `sandhi_warning` pair using a
     0.5° (0°30') band.
  3. strongest_rp — derived from the first SURVIVING RP factor, so a
     retrograde-excluded Lagna Sub Lord is never reported as strongest.
  4. Retrograde exclusion — resolved to a fixed point (a retrograde planet
     deposited by a retrograde planet that is itself excluded is also excluded).
  5. Node "conjunct" — a degree-orb test, not a same-sign membership test.
  6. Dead `primary` param removed from _csl_verdict (arity == 3).
  7. Docs — orchestration-notes.md no longer instructs displaying
     Uranus/Neptune/Pluto "for reference".

Pinned chart: horary #108, 2026-01-01T09:00:00 Asia/Kolkata, 28.6139N 77.2090E.
"""

import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
SCRIPTS = os.path.join(PLUGIN, "scripts")
sys.path.insert(0, SCRIPTS)

# Locate lib/ the same way the baseline script does.
for _cand in (os.path.join(PLUGIN, "lib"),):
    if os.path.isfile(os.path.join(_cand, "ephemeris.py")):
        sys.path.insert(0, _cand)

import compute_kp_horary_baseline as kph  # noqa: E402
import jyotish_primitives as jp  # noqa: E402

PIN = dict(number=108, dt_iso="2026-01-01T09:00:00", tz="Asia/Kolkata",
           lat=28.6139, lon=77.2090, question="test")

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label} — {detail}")
        failures.append(label)


baseline = kph.build_baseline(**PIN)
planets = baseline["planets"]


# 1. Combustion — present, boolean, and honours the 8.5° orb (not 10-17°).
sun_lon = planets["Sun"]["longitude"]
all_have_flag = all("combust" in c and isinstance(c["combust"], bool)
                    for c in planets.values())
check("1a combust flag present on every planet", all_have_flag)
# Mars ~2° and Venus ~1.3° from Sun on this chart → combust; Mercury ~12° → not.
mars_sep = kph._ang_sep(planets["Mars"]["longitude"], sun_lon)
merc_sep = kph._ang_sep(planets["Mercury"]["longitude"], sun_lon)
check("1b Mars within 8.5° is combust", planets["Mars"]["combust"] is True,
      f"sep={mars_sep:.2f}")
check("1c Mercury beyond 8.5° is NOT combust (Parashari orb would flag it)",
      planets["Mercury"]["combust"] is False and 8.5 < merc_sep < 14.0,
      f"sep={merc_sep:.2f}")
check("1d Sun and nodes never flagged combust",
      planets["Sun"]["combust"] is False
      and planets["Rahu"]["combust"] is False
      and planets["Ketu"]["combust"] is False)
# The KP orb constant must not be the Parashari table.
check("1e KP combustion orb is the uniform 8.5° constant",
      kph.KP_COMBUSTION_ORB == 8.5)


# 2. Sandhi — horary_lagna carries the flag pair, computed with a 0.5° band.
hl = baseline["horary_lagna"]
check("2a horary_lagna carries sandhi + sandhi_warning",
      "sandhi" in hl and "sandhi_warning" in hl)
# Reconstruct the expected verdict from the 0.5° band to prove the threshold.
dis = jp.deg_in_sign(hl["lagna_deg"])
expected_warn = dis < 0.5 or dis > 29.5
check("2b sandhi_warning matches the 0°30' band", hl["sandhi_warning"] == expected_warn,
      f"deg_in_sign={dis:.4f}")


# 3. strongest_rp — first surviving factor, not a hardcoded factors[0].
rp = baseline["ruling_planets"]
check("3a strongest_rp is the first entry of final_rp_set",
      rp["strongest_rp"] == rp["final_rp_set"][0],
      f"strongest={rp['strongest_rp']} final={rp['final_rp_set']}")

# Synthetic: force the Lagna Sub Lord to be retrograde-excluded and prove it is
# NOT reported as strongest_rp.
def chain(sub, star, sign, **extra):
    d = {"sub_lord": sub, "star_lord": star, "sign_lord": sign}
    d.update(extra)
    return d

rp_lagna = chain("Mars", "Jupiter", "Jupiter")     # Lagna Sub Lord = Mars
moon = chain("Jupiter", "Saturn", "Saturn")
synth_planets = {
    # Mars retrograde, deposited by Moon which is NOT in the RP set → excluded.
    "Mars":    {"retrograde": True,  "sign_lord": "Moon", "sign": "Cancer",
                "star_lord": "Saturn", "longitude": 100.0},
    "Jupiter": {"retrograde": False, "sign_lord": "Jupiter", "sign": "Pisces",
                "star_lord": "Mercury", "longitude": 340.0},
    "Saturn":  {"retrograde": False, "sign_lord": "Saturn", "sign": "Capricorn",
                "star_lord": "Sun", "longitude": 280.0},
    "Sun":     {"retrograde": False, "sign_lord": "Sun", "sign": "Leo",
                "star_lord": "Ketu", "longitude": 130.0},
}
synth = kph.compute_ruling_planets(rp_lagna, moon, "Sun", synth_planets)
check("3b retrograde-excluded Lagna Sub Lord is NOT strongest_rp",
      synth["strongest_rp"] != "Mars"
      and "Mars" not in synth["final_rp_set"],
      f"strongest={synth['strongest_rp']} final={synth['final_rp_set']}")


# 4. Retrograde exclusion resolves to a fixed point.
# Mars(retro) deposited by Jupiter; Jupiter(retro) deposited by Mercury (not in
# set). Jupiter must drop, and Mars must drop WITH it (not survive on the stale
# pre-exclusion list).
rp_lagna2 = chain("Mars", "Jupiter", "Venus")
moon2 = chain("Venus", "Saturn", "Saturn")
fp_planets = {
    "Mars":    {"retrograde": True,  "sign_lord": "Jupiter", "sign": "Sagittarius",
                "star_lord": "Ketu", "longitude": 250.0},
    "Jupiter": {"retrograde": True,  "sign_lord": "Mercury", "sign": "Gemini",
                "star_lord": "Rahu", "longitude": 70.0},
    "Venus":   {"retrograde": False, "sign_lord": "Venus", "sign": "Libra",
                "star_lord": "Moon", "longitude": 190.0},
    "Saturn":  {"retrograde": False, "sign_lord": "Saturn", "sign": "Capricorn",
                "star_lord": "Sun", "longitude": 280.0},
}
fp = kph.compute_ruling_planets(rp_lagna2, moon2, "Saturn", fp_planets)
check("4 fixed-point excludes a retro planet deposited by an excluded retro planet",
      "Jupiter" not in fp["final_rp_set"] and "Mars" not in fp["final_rp_set"],
      f"final={fp['final_rp_set']} retro={fp['retrograde_check']}")


# 5. Node "conjunct" is an orb test, not same-sign.
# Two planets in the SAME sign as the node but > NODE_CONJUNCTION_ORB away must
# NOT be reported as conjunct.
rp_lagna3 = chain("Sun", "Sun", "Sun")
moon3 = chain("Moon", "Moon", "Moon")
node_planets = {
    "Rahu": {"retrograde": False, "sign_lord": "Sun", "sign": "Leo",
             "star_lord": "Ketu", "longitude": 122.0},          # Leo 2°
    "Sun":  {"retrograde": False, "sign_lord": "Sun", "sign": "Leo",
             "star_lord": "Ketu", "longitude": 124.0},          # Leo 4° → 2° away
    "Mars": {"retrograde": False, "sign_lord": "Sun", "sign": "Leo",
             "star_lord": "Ketu", "longitude": 145.0},          # Leo 25° → 23° away
}
nd = kph.compute_ruling_planets(rp_lagna3, moon3, "Sun", node_planets)
conj = nd["node_agent_check"]["Rahu"]["conjunct"]
check("5 node conjunction respects the degree orb, not same-sign",
      "Sun" in conj and "Mars" not in conj,
      f"conjunct={conj} (Sun 2° in, Mars 23° out despite same sign)")


# 6. Dead `primary` parameter removed from _csl_verdict.
sig = inspect.signature(kph._csl_verdict)
check("6 _csl_verdict has no dead `primary` parameter",
      "primary" not in sig.parameters and len(sig.parameters) == 3,
      f"params={list(sig.parameters)}")


# 7. Docs — orchestration-notes.md drops the U/N/P "for reference" instruction.
notes_path = os.path.join(PLUGIN, "skills", "kp-horary", "references",
                          "orchestration-notes.md")
notes = open(notes_path, encoding="utf-8").read()
check("7 orchestration-notes.md no longer says outer planets are displayed 'for reference'",
      "for reference only" not in notes and "shown for reference only" not in notes,
      "U/N/P display instruction still present")


print()
if failures:
    print(f"RESULT: FAIL ({len(failures)} class(es) regressed): {failures}")
    sys.exit(1)
print("RESULT: PASS — all kp-horary regression classes green")
