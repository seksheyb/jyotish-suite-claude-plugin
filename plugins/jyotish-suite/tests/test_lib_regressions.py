#!/usr/bin/env python3
"""
Regression guards for the shared deterministic layer (lib/ephemeris.py,
lib/jyotish_primitives.py). Plain asserts + PASS/FAIL prints, nonzero exit on
failure — matches tests/run_golden.py style (no pytest).

Covers the four Wave-1 shared-lib findings:
  1. day_lord() weekday from LOCAL civil date, not the UTC calendar date.
  2. kp_horary_chart() planets carry a whole-sign 'house' vs the CHART Lagna.
  3. horary_number_to_lagna() dict carries a 'sign' field.
  4. close_contention() flags same-sign planets 2deg-5deg apart (distinct from
     planetary_war's <1deg).
"""

import os
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(HERE), "lib")
sys.path.insert(0, LIB)

import ephemeris as eph          # noqa: E402
import jyotish_primitives as jp  # noqa: E402
import swisseph as swe           # noqa: E402

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name} {detail}")
        failures.append(name)


# --------------------------------------------------------------------
# Finding 1 — day_lord uses LOCAL civil date, not UTC calendar date.
# Far-east location (lat -12, lon +178): the sunrise instant lands on the
# PREVIOUS UTC date but the current LOCAL date. The buggy UTC-date code returned
# Moon (Monday); the fix must return Mars (Tuesday, the local civil weekday).
# --------------------------------------------------------------------
lat, lon = -12.0, 178.0
jd = eph.julian_day(datetime(2026, 3, 10, 0, 0))
sr = eph.sunrise_jd(jd, lat, lon)
_y, _m, _d, _ut = swe.revjul(sr)
utc_sr = datetime(_y, _m, _d) + timedelta(hours=_ut)
lord, local_dt = eph.day_lord(jd, lat, lon)

check("day_lord UTC-vs-local dates genuinely differ (boundary case is real)",
      utc_sr.date() != local_dt.date(),
      f"(utc {utc_sr.date()} vs local {local_dt.date()})")
check("day_lord returns LOCAL-date weekday lord (Mars), not UTC-date lord (Moon)",
      lord == "Mars",
      f"(got {lord}; UTC-date lord would be "
      f"{jp.WEEKDAY_LORDS[utc_sr.weekday()]})")
check("day_lord returned datetime weekday is consistent with its lord",
      jp.WEEKDAY_LORDS[local_dt.weekday()] == lord)

# tz_name path: exact local civil date must agree with the longitude fallback
# here (Fiji is +12/+13 near this longitude).
lord_tz, _dt_tz = eph.day_lord(jd, lat, lon, tz_name="Pacific/Fiji")
check("day_lord(tz_name=...) exact-tz path also yields the local-date lord",
      lord_tz == "Mars", f"(got {lord_tz})")


# --------------------------------------------------------------------
# Finding 3 — horary_number_to_lagna dict carries 'sign'.
# --------------------------------------------------------------------
mid, info = eph.horary_number_to_lagna(108)
check("horary_number_to_lagna dict has 'sign' key", "sign" in info)
check("horary_number_to_lagna 'sign' matches lagna_deg",
      info.get("sign") == jp.get_sign(mid)[1],
      f"(sign={info.get('sign')}, deg={mid})")


# --------------------------------------------------------------------
# Finding 2 — kp_horary_chart planets carry a whole-sign 'house' vs CHART Lagna.
# Pins: number 108, 2026-01-01T09:00 IST, Delhi.
# --------------------------------------------------------------------
chart = eph.kp_horary_chart(108, "2026-01-01T09:00", "Asia/Kolkata",
                            28.6139, 77.2090)
planets = chart["planets"]
lagna_si = jp.get_sign(chart["horary_lagna"]["lagna_deg"])[0]

check("every horary planet has a 'house' key",
      all("house" in p for p in planets.values()),
      f"(missing: {[n for n, p in planets.items() if 'house' not in p]})")
check("horary planet houses are 1..12",
      all(1 <= p["house"] <= 12 for p in planets.values()))
# House must be measured from the CHART (number) Lagna, not the RP Lagna.
sun = planets["Sun"]
expected_house = jp.house_of(jp.get_sign(sun["longitude"])[0], lagna_si)
check("horary planet 'house' is whole-sign vs the CHART Lagna",
      sun["house"] == expected_house,
      f"(Sun house={sun['house']}, expected {expected_house})")
# Sanity: the horary Lagna sign itself is house 1.
lagna_sign = chart["horary_lagna"]["sign"]
in_lagna_sign = [p for p in planets.values() if p["sign"] == lagna_sign]
check("a planet in the Lagna sign resolves to house 1 (if any present)",
      all(p["house"] == 1 for p in in_lagna_sign) or not in_lagna_sign)


# --------------------------------------------------------------------
# Finding 4 — close_contention flags same-sign planets 2deg-5deg apart,
# distinct from planetary_war (<1deg).
# --------------------------------------------------------------------
# Synthetic 3deg-apart same-sign pair (both in Aries).
pos = {"Mars": 10.0, "Saturn": 13.0, "Jupiter": 40.0}  # Jupiter in Taurus, alone
cc = jp.close_contention(pos)
check("close_contention flags a synthetic 3deg same-sign pair", len(cc) == 1,
      f"(got {cc})")
if cc:
    pair = cc[0]
    check("close_contention pair is the same-sign Mars/Saturn",
          {pair["planet_a"], pair["planet_b"]} == {"Mars", "Saturn"})
    check("close_contention planet_a is the lower degree-in-sign (Mars)",
          pair["planet_a"] == "Mars")
    check("close_contention separation ~3deg", abs(pair["separation"] - 3.0) < 1e-6)

# <1deg same-sign pair is a planetary_war, NOT close_contention.
war_pos = {"Mars": 10.0, "Saturn": 10.5}
check("close_contention IGNORES a <1deg pair (that is a planetary_war)",
      jp.close_contention(war_pos) == [])
check("planetary_war STILL flags the <1deg pair", len(jp.planetary_war(war_pos)) == 1)

# >5deg same-sign pair is neither.
check("close_contention IGNORES a >5deg same-sign pair",
      jp.close_contention({"Mars": 10.0, "Saturn": 18.0}) == [])
# Different-sign pair within 3deg of arc across the cusp is NOT flagged.
check("close_contention IGNORES a cross-sign pair",
      jp.close_contention({"Mars": 29.0, "Saturn": 31.0}) == [])


# --------------------------------------------------------------------
if failures:
    print(f"\n{len(failures)} regression check(s) FAILED: {failures}")
    sys.exit(1)
print("\nAll lib regression checks PASSED.")
