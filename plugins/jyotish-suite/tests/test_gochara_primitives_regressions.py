#!/usr/bin/env python3
"""
Regression guards for the gochara (transit) primitives and the Jaimini
rashi-drishti builder in lib/jyotish_primitives.py. Plain asserts + PASS/FAIL
prints, nonzero exit on failure — matches tests/test_lib_regressions.py style.

Covers:
  1. pada_to_navamsa(nak, pada) is the identity with navamsa_sign(lon).
  2. kakshya_of() boundaries and lords.
  3. tara_bala() 9-cycle and favourability.
  4. saturn_moon_phase() fires on exactly the 12th/1st/2nd/4th/8th from Moon.
  5. gochara_verdict() / is_vedha_exempt() table lookups.
  6. jaimini_drishti_matrix() core aspects, and the Jaimini script's DRISHTI
     is the lib builder's output (the move is structural only).
  7. pada_to_navamsa input validation.

The Jaimini matrix is asserted symmetric with an empty one_way list (fixed
signs skip the ADJACENT movable sign — the one before them — so Taurus aspects
Cancer/Libra/Capricorn, never Aries). get_nakshatra/get_pada/navamsa_sign are
asserted exact at pada boundaries (30.0, 120.0, 240.0 ...), which the old
float-flooring implementation got wrong.
"""

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(HERE), "lib")
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, LIB)
sys.path.insert(0, SCRIPTS)

import jyotish_primitives as jp  # noqa: E402

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}  {detail}")
        failures.append(name)


def nak_pada(lon):
    """(nak_idx, pada) via exact pada counting (108 padas of 3deg20') —
    independent of the lib so the lib can be checked against it, including at
    exact boundaries."""
    p = int(jp.norm360(lon) * 108 // 360) % 108
    return p // 4, p % 4 + 1


# --- 1. pada_to_navamsa == navamsa_sign ---------------------------------
BOUNDARY = [0.0, 30.0, 120.0, 240.0]
lons = [0.0, 3.3333, 3.3334, 13.3333, 26.6667, 30.0, 119.999, 120.0, 240.0, 359.99]
rng = random.Random(20261108)
lons += [rng.uniform(0, 360) for _ in range(10)]
bad = [(lon, jp.pada_to_navamsa(*nak_pada(lon)), jp.navamsa_sign(lon))
       for lon in lons if jp.pada_to_navamsa(*nak_pada(lon)) != jp.navamsa_sign(lon)]
check("pada_to_navamsa identity with navamsa_sign (20 lons)", not bad, str(bad))
bad = [lon for lon in lons + BOUNDARY
       if (jp.get_nakshatra(lon)[0], jp.get_pada(lon)) != nak_pada(lon)]
check("lib get_nakshatra/get_pada agree with exact pada count incl. boundaries", not bad, str(bad))
check("get_nakshatra(120.0) is Magha (idx 9), not Ashlesha", jp.get_nakshatra(120.0)[0] == 9)
check("get_pada(30.0) is pada 2 of Krittika", jp.get_pada(30.0) == 2)
check("navamsa_sign at 10deg Aries is Cancer (4th navamsa)", jp.navamsa_sign(10.0) == (3, "Cancer"))
check("get_sub_and_subsub(120.0) starts Magha at Ketu sub", jp.get_sub_and_subsub(120.0)[0] == "Ketu")

# --- 2. kakshya_of ------------------------------------------------------
for lon, exp in [(0.0, (0, "Saturn")), (3.75, (1, "Jupiter")), (26.25, (7, "Lagna")),
                 (29.99, (7, "Lagna")), (33.75, (1, "Jupiter"))]:
    got = jp.kakshya_of(lon)
    check(f"kakshya_of({lon})", got == exp, f"got {got}, want {exp}")

# --- 3. tara_bala -------------------------------------------------------
taras = [jp.tara_bala(0, i)[0] for i in range(27)]
check("tara_bala cycles 1..9 x3", taras == list(range(1, 10)) * 3, str(taras))
check("tara_bala idx 2 -> Vipat unfavourable", jp.tara_bala(0, 2) == (3, "Vipat", False),
      str(jp.tara_bala(0, 2)))
check("tara_bala idx 1 -> Sampat favourable", jp.tara_bala(0, 1) == (2, "Sampat", True),
      str(jp.tara_bala(0, 1)))

# --- 4. saturn_moon_phase -----------------------------------------------
moon = 3
expected = {11: "sade_sati_rising", 0: "sade_sati_peak", 1: "sade_sati_setting",
            3: "kantaka_shani", 7: "ashtama_shani"}
got = {off: jp.saturn_moon_phase((moon + off) % 12, moon) for off in range(12)}
want = {off: expected.get(off) for off in range(12)}
check("saturn_moon_phase all 12 offsets from moon idx 3", got == want, str(got))

# --- 5. gochara_verdict / vedha -----------------------------------------
check("gochara Jupiter 5th", jp.gochara_verdict("Jupiter", 5) ==
      {"favourable": True, "vedha_house": 4}, str(jp.gochara_verdict("Jupiter", 5)))
check("gochara Jupiter 6th", jp.gochara_verdict("Jupiter", 6) ==
      {"favourable": False, "vedha_house": None}, str(jp.gochara_verdict("Jupiter", 6)))
check("gochara Saturn 11th", jp.gochara_verdict("Saturn", 11) ==
      {"favourable": True, "vedha_house": 5}, str(jp.gochara_verdict("Saturn", 11)))
check("vedha exempt Sun/Saturn", jp.is_vedha_exempt("Sun", "Saturn") is True)
check("vedha not exempt Sun/Mars", jp.is_vedha_exempt("Sun", "Mars") is False)

# --- 6. jaimini_drishti_matrix ------------------------------------------
dm = jp.jaimini_drishti_matrix()
m = dm["matrix"]


def aspects(a):
    return {b for b in range(12) if m[a][b]}


check("drishti Aries -> Leo/Scorpio/Aquarius, not Taurus",
      aspects(0) == {4, 7, 10} and not m[0][1], str(aspects(0)))
check("drishti Taurus -> Cancer/Libra/Capricorn, not Aries", aspects(1) == {3, 6, 9}, str(aspects(1)))
check("drishti Aquarius -> Aries/Cancer/Libra, not Capricorn", aspects(10) == {0, 3, 6}, str(aspects(10)))
check("drishti matrix symmetric (every rasi drishti is mutual)",
      all(m[a][b] == m[b][a] for a in range(12) for b in range(12)))
check("drishti one_way is empty", dm["one_way"] == [], str(dm["one_way"]))
check("drishti movable never aspects movable, fixed never fixed",
      all(not m[a][b] for a in range(12) for b in range(12)
          if a != b and jp.SIGN_QUALITY[a] == jp.SIGN_QUALITY[b] and jp.SIGN_QUALITY[a] != "Dual"))
check("drishti Gemini -> Virgo/Sagittarius/Pisces", aspects(2) == {5, 8, 11}, str(aspects(2)))
check("drishti no self-aspect", all(m[i][i] == 0 for i in range(12)))
check("drishti dual signs mutually symmetric",
      all(m[a][b] == m[b][a] for a in (2, 5, 8, 11) for b in (2, 5, 8, 11)))

import compute_jaimini_baseline as jb  # noqa: E402
check("jaimini script DRISHTI == lib builder output", jb.DRISHTI == dm)

# --- 7. validation ------------------------------------------------------
for args in [(27, 1), (0, 5)]:
    try:
        jp.pada_to_navamsa(*args)
        check(f"pada_to_navamsa{args} raises ValueError", False, "no exception")
    except ValueError:
        check(f"pada_to_navamsa{args} raises ValueError", True)


def test_no_regressions():
    """pytest entry point. The checks above run at import; this reports them."""
    assert not failures, (
        f"{len(failures)} gochara primitive check(s) FAILED: {failures}")


if __name__ == "__main__":
    if failures:
        print(f"\n{len(failures)} regression check(s) FAILED: {failures}")
        sys.exit(1)
    print("\nAll gochara primitive checks PASSED.")
