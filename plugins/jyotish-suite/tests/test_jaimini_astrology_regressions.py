#!/usr/bin/env python3
"""
Regression guard for the jaimini-astrology bugfix wave.

Standalone (no pytest): plain asserts, prints PASS/FAIL per class, exits
non-zero if any bug reappears. Mirrors the style of tests/run_golden.py and
tests/test_kp_horary_regressions.py.

Each check pins one defect class fixed in the wave:

  1. [P0] Dual-lord tiebreak measures Kendra/Trikona FROM THE LAGNA, not from
     the lorded sign (compute_jaimini_baseline.jaimini_sign_lord). On the pinned
     chart (Cancer Lagna) the Jaimini lord of Scorpio is Ketu (in Cancer, a
     Kendra from Lagna), NOT Mars (in Aquarius). This flip is decisive — it
     changes Scorpio's Chara Dasha years and the running Mahadasha.
  2. [P1] Chara Dasha Antardasha is computed: every Mahadasha carries an
     `antardasha` list of 12 sub-periods that tile the Mahadasha span, and the
     running Mahadasha exposes `running_antardasha`.
  3. [P2] Argala pre-map covers every named Arudha (A2-A11, AL, UL) plus
     Swamsha and Lagna — not just AL/UL/A10/Swamsha/Lagna.
  4. [P2] The planets block carries nakshatra/pada/house; each Chara Karaka row
     inlines its degree_flags.
  5. [P1] Docs — orchestration-notes.md splits the display into a Chart
     Verification Display (chart-only, Wave 0 step 2) and a separate Jaimini
     Baseline Display (from baseline JSON, Wave 0 step 4); the chart-verifier
     step no longer asks for the baseline block.

Pinned chart: 1990-05-15T10:30:00 Asia/Kolkata, 28.6139N 77.2090E,
target-date 2026-01-01.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
SCRIPTS = os.path.join(PLUGIN, "scripts")
sys.path.insert(0, SCRIPTS)
for _cand in (os.path.join(PLUGIN, "lib"),):
    if os.path.isfile(os.path.join(_cand, "ephemeris.py")):
        sys.path.insert(0, _cand)

import compute_jaimini_baseline as cjb  # noqa: E402
import jyotish_primitives as jp  # noqa: E402

PIN = dict(datetime="1990-05-15T10:30:00", tz="Asia/Kolkata",
           lat=28.6139, lon=77.2090, target_date="2026-01-01")

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label} — {detail}")
        failures.append(label)


# Full baseline via the same CLI path the skill uses.
proc = subprocess.run(
    [sys.executable, os.path.join(SCRIPTS, "compute_jaimini_baseline.py"),
     "--datetime", PIN["datetime"], "--tz", PIN["tz"],
     "--lat", str(PIN["lat"]), "--lon", str(PIN["lon"]),
     "--target-date", PIN["target_date"]],
    capture_output=True, text=True,
)
if proc.returncode != 0:
    print("FATAL: baseline script failed\n" + proc.stderr)
    sys.exit(1)
B = json.loads(proc.stdout)


# ---- 1. [P0] Dual-lord tiebreak from the Lagna --------------------------------
# Unit-level: Scorpio (idx 7) with a Cancer (idx 3) Lagna must resolve to Ketu.
d1_planets = {p: B["planets"][p] for p in B["planets"]}
# build a minimal d1_planets-shaped dict carrying "sign" (present in planets)
scorpio_lord = cjb.jaimini_sign_lord(7, d1_planets, 3)
check("dual-lord tiebreak: Scorpio lord is Ketu (Kendra-from-Lagna), not Mars",
      scorpio_lord == "Ketu",
      f"got {scorpio_lord!r} — tiebreak still measured from the lorded sign?")

# Sanity: swapping the Lagna to Aquarius (idx 10) — where Mars sits in a Kendra
# (Aquarius is the 1st from an Aquarius Lagna) — must instead pick Mars,
# proving the score genuinely depends on the Lagna argument.
scorpio_lord_aqu = cjb.jaimini_sign_lord(7, d1_planets, 10)
check("dual-lord tiebreak actually reads the Lagna argument",
      scorpio_lord_aqu == "Mars",
      f"got {scorpio_lord_aqu!r} for an Aquarius Lagna")

# Baseline-level: the decisive flip is present in the sequence.
scorpio_row = next(s for s in B["chara_dasha"]["sequence"] if s["rasi"] == "Scorpio")
check("Chara Dasha sequence records Scorpio's Jaimini lord as Ketu",
      scorpio_row["jaimini_lord"] == "Ketu",
      f"got {scorpio_row['jaimini_lord']!r}")


# ---- 2. [P1] Chara Dasha Antardasha ------------------------------------------
seq = B["chara_dasha"]["sequence"]
check("every Mahadasha carries an antardasha list",
      all(isinstance(s.get("antardasha"), list) for s in seq),
      "at least one sequence entry has no antardasha field")
check("each Mahadasha's antardasha has 12 sub-periods",
      all(len(s["antardasha"]) == 12 for s in seq),
      "an antardasha sub-sequence is not 12 signs long")

# Antardashas tile the Mahadasha's FULL length (the birth-balance first
# Mahadasha still spans its full years — the elapsed portion sits pre-birth
# at negative age — so every sub-sequence sums to the entry's full_years).
for s in seq:
    ad_sum = sum(a["years"] for a in s["antardasha"])
    if abs(ad_sum - s["full_years"]) > 1e-2:
        check(f"antardashas tile the {s['rasi']} Mahadasha",
              False, f"sum {ad_sum} != full {s['full_years']}")
        break
else:
    check("antardashas tile each Mahadasha's full span (sum == full_years)", True)

running = B["chara_dasha"]["running"]
check("running Mahadasha exposes running_antardasha",
      running is not None and running.get("running_antardasha") is not None,
      "running_antardasha missing")
if running and running.get("running_antardasha"):
    ad = running["running_antardasha"]
    check("running_antardasha carries a rasi + start/end dates",
          all(k in ad for k in ("rasi", "start", "end", "years")),
          f"keys {list(ad.keys())}")


# ---- 3. [P2] Argala pre-map covers every named Arudha ------------------------
argala_keys = set(B["argala"].keys())
needed = {"AL", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11",
          "UL", "Swamsha", "Lagna"}
check("Argala pre-map covers A2-A11 + AL/UL + Swamsha + Lagna",
      needed <= argala_keys,
      f"missing {sorted(needed - argala_keys)}")


# ---- 4. [P2] planets block detail + karaka degree_flags ----------------------
sun = B["planets"]["Sun"]
check("planets block carries nakshatra/pada/house",
      all(k in sun for k in ("nakshatra", "pada", "house")),
      f"Sun keys {list(sun.keys())}")
check("each Chara Karaka row inlines degree_flags",
      all("degree_flags" in B["chara_karakas"][k] for k in
          ("AK", "AmK", "BK", "MK", "PK", "GK", "DK")),
      "a Karaka row has no degree_flags field")


# ---- 5. [P1] Docs split the display -------------------------------------------
notes_path = os.path.join(PLUGIN, "skills", "jaimini-astrology", "references",
                          "orchestration-notes.md")
notes = open(notes_path, encoding="utf-8").read()
check("orchestration-notes has a Chart Verification Display section",
      "Chart Verification Display" in notes)
check("orchestration-notes has a separate Jaimini Baseline Display section",
      "Jaimini Baseline Display" in notes)

skill_path = os.path.join(PLUGIN, "skills", "jaimini-astrology", "SKILL.md")
skill = open(skill_path, encoding="utf-8").read()
check("SKILL.md chart-verifier step no longer requests the baseline block",
      "not** the Jaimini baseline block" in skill,
      "chart-verifier still told to render the Jaimini baseline block at step 2")

# ---- 6. [P2] close_contention wired into the baseline output ------------------
check("top-level close_contentions key present",
      "close_contentions" in B, "close_contentions missing from baseline JSON")
check("every planet block carries a close_contention field",
      all("close_contention" in p for p in B["planets"].values()),
      "a planet block is missing close_contention")
_cc_pairs = jp.close_contention(
    {"Mars": 45.0, "Saturn": 48.0, "Sun": 200.0})  # 3deg apart, same sign
check("close_contention flags a synthetic 3deg same-sign pair",
      len(_cc_pairs) == 1 and _cc_pairs[0]["planet_a"] == "Mars",
      f"expected one Mars/Saturn pair, got {_cc_pairs}")
_war_not_cc = jp.close_contention(
    {"Mars": 45.0, "Saturn": 45.4, "Sun": 200.0})  # 0.4deg = war territory, not CC
check("close_contention correctly ignores sub-1deg (planetary-war) pairs",
      len(_war_not_cc) == 0, f"expected no CC pairs, got {_war_not_cc}")

# ---- 7. Chara Dasha secondary sign lords (computation.md Step 1 table) --------
# All 7 dual-lord signs must be handled, not just the two nodal ones.
check("JAIMINI_DUAL_LORDS covers the 7 documented dual-lord signs",
      set(cjb.JAIMINI_DUAL_LORDS) == {2, 5, 7, 8, 9, 10, 11},
      f"got {sorted(cjb.JAIMINI_DUAL_LORDS)}")
check("dual-lord pairs match the original table",
      cjb.JAIMINI_DUAL_LORDS[2] == ("Mercury", "Jupiter")
      and cjb.JAIMINI_DUAL_LORDS[8] == ("Jupiter", "Mars")
      and cjb.JAIMINI_DUAL_LORDS[9] == ("Saturn", "Mars")
      and cjb.JAIMINI_DUAL_LORDS[11] == ("Jupiter", "Venus"),
      "a conditional dual-lord pair does not match computation.md Step 1")
# Functional: Gemini's secondary (Jupiter) wins when it is exalted and the
# primary (Mercury) is weak -> the conditional rule actually fires.
_synth = {p: {"sign": s} for p, s in {
    "Sun": "Aries", "Moon": "Aries", "Mars": "Aries", "Mercury": "Scorpio",
    "Jupiter": "Cancer", "Venus": "Aries", "Saturn": "Aries",
    "Rahu": "Aries", "Ketu": "Libra"}.items()}
check("Gemini takes secondary lord Jupiter when Mercury is weak",
      cjb.jaimini_sign_lord(2, _synth, 0) == "Jupiter",
      f"got {cjb.jaimini_sign_lord(2, _synth, 0)}")
# ...and the primary still wins by default (Mercury strong / Jupiter not).
_synth2 = {p: {"sign": s} for p, s in {
    "Sun": "Aries", "Moon": "Aries", "Mars": "Aries", "Mercury": "Virgo",
    "Jupiter": "Capricorn", "Venus": "Aries", "Saturn": "Aries",
    "Rahu": "Aries", "Ketu": "Libra"}.items()}
check("Gemini keeps primary lord Mercury when it is the stronger",
      cjb.jaimini_sign_lord(2, _synth2, 5) == "Mercury",
      f"got {cjb.jaimini_sign_lord(2, _synth2, 5)}")


if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nALL PASS")
