#!/usr/bin/env python3
"""
Regression guard for the BNN transit layer (scripts/compute_bnn_transits.py).

Standalone (no pytest needed): prints PASS/FAIL per check, exits non-zero on
any failure; also exposes test_no_regressions() for pytest. Mirrors
tests/test_lib_regressions.py.

Defect class pinned: "bnn has no transit activation layer (timing is
dasha-only)". Checks:

  1. Snapshot — on the pinned chart (1990-05-15T10:30 Asia/Kolkata, 28.6139N
     77.2090E, dasha asof 2026-01-01T09:00) the 2026-01-01 -> 2026-07-01
     transit output equals tests/snapshots/bnn_transits.json.
  2. Invariants recomputed here, independent of the snapshot:
     - relation_to_natal[P].count == jp.count_signs(natal_idx, transit_idx)
       and every label is from the allowed set and matches the count;
     - natal_planets_conjoined / natal_planets_aspected agree with BNN
       aspects (7th + BNN_SPECIAL_ASPECTS) recomputed from the sign;
     - every exact_conjunctions hit overlaps a sign_stays hit in that natal
       planet's sign (the entry instant lies inside it, unless the orb
       straddles a sign boundary);
     - pass_number increments 1, 2, 3... per natal planet;
     - sign_stays and exact_conjunctions sorted by entry_date;
     - jupiter_cycle null for non-Jupiter bodies, non-null for Jupiter with
       natal_jupiter_sign == baseline planets.Jupiter.sign.
  3. Docs — bnn SKILL.md, methodology.md, orchestration-notes.md and
     commands/bnn.md name compute_bnn_transits.py; methodology has 4B.

Regenerate the snapshot (only for an intentional output change):
  python3 scripts/compute_bnn_baseline.py --datetime 1990-05-15T10:30:00 \\
    --tz Asia/Kolkata --lat 28.6139 --lon 77.2090 \\
    --asof 2026-01-01T09:00:00 > /tmp/b.json
  python3 scripts/compute_bnn_transits.py --baseline /tmp/b.json \\
    --start-datetime 2026-01-01T00:00:00 --end-datetime 2026-07-01T00:00:00 \\
    --tz Asia/Kolkata --out tests/snapshots/bnn_transits.json
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
SCRIPTS = os.path.join(PLUGIN, "scripts")
sys.path.insert(0, SCRIPTS)
for _cand in (os.path.join(PLUGIN, "lib"),):
    if os.path.isfile(os.path.join(_cand, "ephemeris.py")):
        sys.path.insert(0, _cand)

import jyotish_primitives as jp  # noqa: E402
from compute_bnn_baseline import BNN_SPECIAL_ASPECTS  # noqa: E402

SNAPSHOT = os.path.join(HERE, "snapshots", "bnn_transits.json")
ALLOWED = {1: "conjunction", 5: "trine", 9: "trine", 6: "dusthana",
           8: "dusthana", 2: "adjacent", 12: "adjacent", 7: "opposition",
           3: "neutral", 4: "neutral", 10: "neutral", 11: "neutral"}

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name} — {detail}")
        failures.append(name)


# --------------------------------------------------------------------
# Build baseline + transits on the pinned chart.
# --------------------------------------------------------------------
baseline = now = None
with tempfile.TemporaryDirectory() as tmp:
    base_path = os.path.join(tmp, "bnn_baseline.json")
    out_path = os.path.join(tmp, "bnn_transits_now.json")
    proc = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "compute_bnn_baseline.py"),
         "--datetime", "1990-05-15T10:30:00", "--tz", "Asia/Kolkata",
         "--lat", "28.6139", "--lon", "77.2090",
         "--asof", "2026-01-01T09:00:00"],
        capture_output=True, text=True)
    check("bnn baseline builds", proc.returncode == 0, proc.stderr[-500:])
    if proc.returncode == 0:
        with open(base_path, "w") as fh:
            fh.write(proc.stdout)
        baseline = json.loads(proc.stdout)
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "compute_bnn_transits.py"),
             "--baseline", base_path,
             "--start-datetime", "2026-01-01T00:00:00",
             "--end-datetime", "2026-07-01T00:00:00",
             "--tz", "Asia/Kolkata", "--out", out_path],
            capture_output=True, text=True)
        check("compute_bnn_transits.py runs", proc.returncode == 0,
              proc.stderr[-500:])
        if proc.returncode == 0:
            with open(out_path) as fh:
                now = json.load(fh)

        # Missing required keys -> loud failure.
        bad_path = os.path.join(tmp, "bad.json")
        with open(bad_path, "w") as fh:
            json.dump({"school": "bnn", "planets": {}}, fh)
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "compute_bnn_transits.py"),
             "--baseline", bad_path, "--datetime", "2026-01-01T00:00:00",
             "--tz", "Asia/Kolkata"], capture_output=True, text=True)
        check("incomplete baseline fails loudly (exit 1 + stderr)",
              proc.returncode == 1 and "ERROR" in proc.stderr,
              f"rc={proc.returncode} stderr={proc.stderr[-200:]}")

# --------------------------------------------------------------------
# 1. Snapshot
# --------------------------------------------------------------------
with open(SNAPSHOT) as fh:
    snap = json.load(fh)
check("BNN transits: parsed JSON equals snapshot", now == snap,
      "output drifted from tests/snapshots/bnn_transits.json")

# --------------------------------------------------------------------
# 2. Invariants
# --------------------------------------------------------------------
if now is not None and baseline is not None:
    natal = {p: v for p, v in baseline["planets"].items()}
    by_sign = {}
    for p, v in natal.items():
        by_sign.setdefault(v["sign_idx"], []).append(p)

    rel_ok = label_ok = conj_ok = asp_ok = True
    rel_bad = []

    def annotated(body, rec):
        global rel_ok, label_ok, conj_ok, asp_ok
        t_idx = rec["sign_idx"]
        for p, r in rec["relation_to_natal"].items():
            if r["count"] != jp.count_signs(natal[p]["sign_idx"], t_idx):
                rel_ok = False
                rel_bad.append((body, p, r))
            if ALLOWED.get(r["count"]) != r["label"]:
                label_ok = False
        if sorted(rec["natal_planets_conjoined"]) != sorted(by_sign.get(t_idx, [])):
            conj_ok = False
        exp = {}
        for n in [7] + BNN_SPECIAL_ASPECTS.get(body, []):
            for p in by_sign.get(jp.sign_n_from(t_idx, n), []):
                exp[p] = n
        if rec["natal_planets_aspected"] != exp:
            asp_ok = False

    for body, v in now["bodies"].items():
        for rec in v["positions"].values():
            annotated(body, rec)
        for rec in v["sign_stays"]:
            annotated(body, rec)
    check("relation_to_natal.count == jp.count_signs(natal, transit)", rel_ok,
          str(rel_bad[:3]))
    check("relation labels from allowed set and match count", label_ok)
    check("natal_planets_conjoined == natal planets in transit sign", conj_ok)
    check("natal_planets_aspected == BNN aspects (7th + specials)", asp_ok)

    def sorted_by_entry(hits):
        keys = [h["entry_date"] or "" for h in hits]
        return keys == sorted(keys)

    inside_ok, inside_bad = True, []
    pass_ok, sort_ok = True, True
    total_conj = 0
    for body, v in now["bodies"].items():
        stays = v["sign_stays"]
        conj = v["exact_conjunctions"]
        total_conj += len(conj)
        sort_ok = sort_ok and sorted_by_entry(stays) and sorted_by_entry(conj)
        seen = {}
        for h in conj:
            n = h["natal_planet"]
            seen[n] = seen.get(n, 0) + 1
            if h["pass_number"] != seen[n]:
                pass_ok = False
            n_idx = natal[n]["sign_idx"]
            deg = natal[n]["deg_in_sign"]
            orb = h["orb"]
            straddles = deg < orb or deg > 30.0 - orb
            same = [s for s in stays if s["sign_idx"] == n_idx]
            if straddles:
                # Orb crosses a sign cusp: require interval overlap only.
                ok = any(s["entry_date"] < h["exit_date"]
                         and h["entry_date"] < s["exit_date"] for s in same)
            else:
                ok = any(s["entry_date"] <= h["entry_date"] <= s["exit_date"]
                         for s in same)
            if not ok:
                inside_ok = False
                inside_bad.append((body, n, h["entry_date"]))
    check("exact conjunction entry lies inside a stay in the natal sign",
          inside_ok, str(inside_bad[:3]))
    check("pass_number increments per natal planet", pass_ok)
    check("sign_stays / exact_conjunctions sorted by entry_date", sort_ok)
    check("pinned window has at least one exact conjunction", total_conj > 0)

    jc_ok = all((v["jupiter_cycle"] is None) == (b != "Jupiter")
                for b, v in now["bodies"].items())
    check("jupiter_cycle null iff body != Jupiter", jc_ok)
    jc = now["bodies"].get("Jupiter", {}).get("jupiter_cycle") or {}
    check("jupiter_cycle.natal_jupiter_sign == baseline Jupiter sign",
          jc.get("natal_jupiter_sign") == natal["Jupiter"]["sign"],
          f"{jc.get('natal_jupiter_sign')} vs {natal['Jupiter']['sign']}")
    check("jupiter_cycle has a return in window or a next-return estimate",
          bool(jc.get("returns_in_window")) or bool(jc.get("next_return_estimate_utc")))

    rd = now["reference"]["running_dasha"]
    run = baseline["dasha"]["running"]
    check("reference.running_dasha mirrors baseline dasha.running",
          rd == {k: run[k]["lord"] for k in
                 ("mahadasha", "antardasha", "pratyantardasha")})

# --------------------------------------------------------------------
# 3. Docs wiring
# --------------------------------------------------------------------
DOCS = {
    "skills/bnn/SKILL.md": os.path.join(PLUGIN, "skills", "bnn", "SKILL.md"),
    "methodology.md": os.path.join(PLUGIN, "skills", "bnn", "references",
                                   "methodology.md"),
    "orchestration-notes.md": os.path.join(PLUGIN, "skills", "bnn",
                                           "references",
                                           "orchestration-notes.md"),
    "commands/bnn.md": os.path.join(PLUGIN, "commands", "bnn.md"),
}
texts = {}
for name, path in DOCS.items():
    with open(path) as fh:
        texts[name] = fh.read()
    check(f"{name} names compute_bnn_transits.py",
          "compute_bnn_transits.py" in texts[name])
check("methodology.md has Section 4B", "4B" in texts["methodology.md"])


def test_no_regressions():
    """pytest entry point. The checks above run at import; this reports them."""
    assert not failures, (
        f"{len(failures)} BNN transit regression check(s) FAILED: {failures}")


if __name__ == "__main__":
    if failures:
        print(f"\n{len(failures)} regression check(s) FAILED: {failures}")
        sys.exit(1)
    print("\nAll BNN transit regression checks PASSED.")
