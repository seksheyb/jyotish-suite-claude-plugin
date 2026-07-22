#!/usr/bin/env python3
"""Regression guard for the kp-natal bugfix wave.

Plain python3 (no pytest): asserts + PASS/FAIL prints, exits nonzero on any
failure. One assertion block per fixed defect class. Run:

    python3 tests/test_kp_natal_regressions.py
"""

import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PLUGIN = os.path.dirname(_HERE)
_SCRIPTS = os.path.join(_PLUGIN, "scripts")
_LIB = os.path.join(_PLUGIN, "lib")
_SCRIPT = os.path.join(_SCRIPTS, "compute_kp_natal_baseline.py")

sys.path.insert(0, _LIB)
sys.path.insert(0, _SCRIPTS)
import compute_kp_natal_baseline as kp  # noqa: E402
import jyotish_primitives as jp  # noqa: E402

# Pinned test chart
DT = "1990-05-15T10:30:00"
TZ = "Asia/Kolkata"
LAT = "28.6139"
LON = "77.2090"
RP_DT = "2026-01-01T09:00:00"

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name} {detail}")
        failures.append(name)


# ---------------------------------------------------------------------------
# Integration: run the baseline once on the pinned chart (NO --target-datetime,
# to prove running_at_target still gets populated from the reading moment).
# ---------------------------------------------------------------------------
out = subprocess.run(
    [sys.executable, _SCRIPT, "--datetime", DT, "--tz", TZ,
     "--lat", LAT, "--lon", LON, "--rp-datetime", RP_DT],
    capture_output=True, text=True)
assert out.returncode == 0, f"baseline failed:\n{out.stderr}\n{out.stdout}"
base = json.loads(out.stdout)
rp = base["ruling_planets"]

# Fix 2 — retrograde exclusion actually applied to final_rp
check("fix2_retro_excluded_dropped_from_final_rp",
      "Jupiter" in rp["retrograde_excluded"] and "Jupiter" not in rp["final_rp"],
      f"excluded={rp['retrograde_excluded']} final_rp={rp['final_rp']}")

# Fix 3 — running_at_target populated w/o --target-datetime AND is the
# reading-moment quartet, distinct from the at-birth `running` quartet.
dasha = base["dasha"]
check("fix3_running_at_target_populated",
      "running_at_target" in dasha and dasha["running_at_target"],
      f"keys={list(dasha)}")
check("fix3_target_quartet_differs_from_birth_quartet",
      dasha["running"]["md_lord"] != dasha["running_at_target"]["md_lord"],
      f"birth={dasha['running']['md_lord']} target={dasha['running_at_target']['md_lord']}")

# Fix 4 — node inclusion checks star-lord + conjunction, not only sign-lord.
kc = rp["ketu_check"]
check("fix4_node_check_is_structured",
      isinstance(kc, dict) and "reasons" in kc and "star_lord" in kc
      and "conjunct_rp" in kc,
      f"ketu_check={kc}")
# On this chart Ketu's SIGN-lord (Sun) is NOT an RP, but its STAR-lord (Venus)
# IS — the old sign-lord-only rule would have set added_to_rp False.
check("fix4_ketu_added_via_star_lord",
      kc["added_to_rp"] and kc["sign_lord"] not in rp["final_rp"][:5]
      and any("star-lord" in r for r in kc["reasons"]),
      f"ketu_check={kc}")

# Fix 5 — KP degree flags emitted for every planet and cusp
planets = base["planets"]
check("fix5_planet_degree_flags_present",
      all("degree_flags" in planets[p] for p in planets),
      "some planet missing degree_flags")
check("fix5_planet_flag_keys",
      all(k in planets["Moon"]["degree_flags"]
          for k in ("gandanta", "sandhi", "mrityu_bhaga", "combust")),
      f"moon flags={planets['Moon']['degree_flags']}")
check("fix5_cusp_degree_flags_present",
      all("degree_flags" in c for c in base["cusps"]),
      "some cusp missing degree_flags")

# Fix 8 — node amplification block present (reverse nodal rule)
check("fix8_amplification_block_present",
      isinstance(base.get("significator_amplifications"), dict),
      f"got {type(base.get('significator_amplifications'))}")

# Fix 10 — fruitful/barren sub-lord reverse index present
fb = base.get("fruitful_barren", {})
check("fix10_fruitful_barren_index",
      "planet_sub_lord" in fb and "sub_lord_signifies" in fb
      and fb["planet_sub_lord"]["Sun"]["sub_lord"] == planets["Sun"]["sub_lord"],
      f"fb keys={list(fb)}")

# Fix 12 — strongest_rp documented convention: Lagna Sub Lord (factor #1)
check("fix12_strongest_rp_is_lagna_sub_lord",
      rp["strongest_rp"] == rp["lagna"]["sub_lord"],
      f"strongest={rp['strongest_rp']} lagna_sub={rp['lagna']['sub_lord']}")


# ---------------------------------------------------------------------------
# Unit tests on kp_degree_flags — KP flat orbs, not the Parashari lib orbs.
# ---------------------------------------------------------------------------
# combust: KP flat 8.5deg. Sun at 100deg.
f_in = kp.kp_degree_flags("Mars", 108.0, sun_lon=100.0)   # 8deg -> combust
f_out = kp.kp_degree_flags("Mars", 109.5, sun_lon=100.0)  # 9.5deg -> not
check("fix5_combust_flat_orb_8p5",
      f_in["combust"] is True and f_out["combust"] is False,
      f"in={f_in} out={f_out}")
# combust never for Sun or nodes
check("fix5_no_combust_for_sun_or_nodes",
      "combust" not in kp.kp_degree_flags("Sun", 100.0, sun_lon=100.0)
      and "combust" not in kp.kp_degree_flags("Rahu", 108.0, sun_lon=100.0),
      "sun/node got a combust flag")
# sandhi: KP 0deg30' window (< 0.5 or >= 29.5), NOT lib's 1deg window
s_early = kp.kp_degree_flags("Mars", 30.4, sun_lon=None)   # 0.4deg -> sandhi
s_clear = kp.kp_degree_flags("Mars", 30.7, sun_lon=None)   # 0.7deg -> clear
s_late = kp.kp_degree_flags("Mars", 59.6, sun_lon=None)    # 29.6deg -> sandhi
check("fix5_sandhi_kp_half_degree_window",
      s_early["sandhi"] is True and s_clear["sandhi"] is False
      and s_late["sandhi"] is True,
      f"early={s_early['sandhi']} clear={s_clear['sandhi']} late={s_late['sandhi']}")


# ---------------------------------------------------------------------------
# Unit tests on compute_significators — 2-tuple return + reverse nodal rule.
# ---------------------------------------------------------------------------
def synth_chart():
    """12 whole-sign cusps + planets, engineered so a node signifies a house
    its conjunct planet does not (to exercise the amplification path)."""
    cusps = []
    for i in range(12):
        lon = i * 30.0
        ch = jp.full_lord_chain(lon)
        cusps.append({"cusp": i + 1, "longitude": lon,
                      "sign_lord": ch["sign_lord"], "star_lord": ch["star_lord"],
                      "sub_lord": ch["sub_lord"]})
    # longitudes: Moon deep in Scorpio (house 8), Rahu in Cancer (dep=Moon),
    # Mercury conjunct Rahu within 1deg.
    lons = {"Sun": 15.0, "Moon": 220.0, "Mars": 250.0, "Mercury": 101.0,
            "Jupiter": 280.0, "Venus": 320.0, "Saturn": 10.0,
            "Rahu": 100.0, "Ketu": 280.0}
    planets = {}
    for p, lon in lons.items():
        ch = jp.full_lord_chain(lon)
        planets[p] = {"longitude": lon, "star_lord": ch["star_lord"],
                      "sub_lord": ch["sub_lord"], "sign_lord": ch["sign_lord"]}
    return cusps, planets


cusps, sp = synth_chart()
result = kp.compute_significators(cusps, sp)
check("fix8_compute_significators_returns_tuple",
      isinstance(result, tuple) and len(result) == 2,
      f"got {type(result)}")
sig, amp = result
inv = kp.invert_significators(sig)
# Invariant: every amplified extra_house is one the node signifies and the
# conjunct planet does not — the exact reverse-nodal rule.
amp_ok = True
for planet, entries in amp.items():
    for e in entries:
        node = e["via_node"]
        for h in e["extra_houses"]:
            if h not in inv.get(node, set()) or h in inv.get(planet, set()):
                amp_ok = False
check("fix8_amplification_invariant",
      amp_ok and len(amp) >= 1,
      f"amp={amp}")

# Fix 10 unit — fruitful/barren index inverts the significator table correctly
fb2 = kp.compute_fruitful_barren(sig, sp)
sun_sub = sp["Sun"]["sub_lord"]
check("fix10_sub_lord_signifies_matches_inversion",
      fb2["planet_sub_lord"]["Sun"]["sub_lord_signifies"]
      == sorted(inv.get(sun_sub, set())),
      "sub_lord reverse index inconsistent with invert_significators")


# ---------------------------------------------------------------------------
# Fix 11 — the dead `owned` dict is gone from the source.
# ---------------------------------------------------------------------------
with open(_SCRIPT) as fh:
    src = fh.read()
check("fix11_dead_owned_dict_removed",
      "owned = {p: []" not in src and "owned.setdefault" not in src,
      "dead `owned` dict still present")


# ---------------------------------------------------------------------------
print()
if failures:
    print(f"{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("ALL KP-NATAL REGRESSION CHECKS PASSED")
