#!/usr/bin/env python3
"""
Regression guard for the BNN baseline --asof fix.

Bug: compute_bnn_baseline.py passed the chart's `dasha.running` straight
through, and the chart resolves it at BIRTH (lib/ephemeris.py calls
_vim_dasha(..., <birth utc>)). Every BNN timing reading therefore used the
dasha running at birth, not at the reading date. The script now takes --asof
and resolves MD/AD/PD/SD at that instant (same as compute_vedic_baseline.py).

Pinned chart: 1990-05-15T10:30:00 Asia/Kolkata, 28.6139N 77.2090E.
At birth the dasha was Sun MD / Rahu AD; at 2026-01-01T09:00 it is Rahu MD / Venus AD.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
SCRIPT = os.path.join(PLUGIN, "scripts", "compute_bnn_baseline.py")
SNAPSHOT = os.path.join(HERE, "snapshots", "bnn.json")

BIRTH = ["--datetime", "1990-05-15T10:30:00", "--tz", "Asia/Kolkata",
         "--lat", "28.6139", "--lon", "77.2090"]
ASOF = "2026-01-01T09:00:00"
BIRTH_UTC = "1990-05-15T05:00:00"

failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


def run(asof):
    out = subprocess.run([sys.executable, SCRIPT, *BIRTH, "--asof", asof],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def test_no_regressions():
    d = run(ASOF)["dasha"]
    run_ = d["running"]

    check("dasha.asof echoes --asof", d.get("asof") == ASOF, d.get("asof"))
    for level in ("mahadasha", "antardasha", "pratyantardasha", "sookshma"):
        blk = run_[level]
        check(f"{level} contains asof",
              blk["start"] <= ASOF < blk["end"], blk)

    # THE REGRESSION: at birth the MD was Sun (AD Rahu). A baseline that
    # reports the birth-time dasha would say Sun here.
    check("running MD is not the birth-time lord (Sun)",
          run_["mahadasha"]["lord"] != "Sun", run_["mahadasha"])
    check("running MD at 2026-01-01 is Rahu / AD Venus",
          (run_["mahadasha"]["lord"], run_["antardasha"]["lord"]) == ("Rahu", "Venus"),
          run_)

    # Birth facts are unchanged by the fix.
    check("starting_mahadasha unchanged (Sun)", d["starting_mahadasha"] == "Sun",
          d["starting_mahadasha"])
    check("balance_years unchanged (4.57)", d["balance_years"] == 4.57,
          d["balance_years"])

    # Resolving at birth still yields the birth-time dasha.
    b = run(BIRTH_UTC)["dasha"]["running"]
    check("asof=birth resolves MD Sun", b["mahadasha"]["lord"] == "Sun", b)
    check("asof=birth resolves AD Rahu", b["antardasha"]["lord"] == "Rahu", b)

    with open(SNAPSHOT) as fh:
        snap = json.load(fh)
    check("snapshot carries dasha.asof", snap["dasha"].get("asof") == ASOF,
          snap["dasha"].get("asof"))


if __name__ == "__main__":
    test_no_regressions()
    print()
    print("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}")
    sys.exit(1 if failures else 0)
