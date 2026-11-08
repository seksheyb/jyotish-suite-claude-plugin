#!/usr/bin/env python3
"""Regression guard: vedic baseline emits the Ashtakavarga prastara grid.

prastara[planet][sign] lists the contributors that gave a bindu; its length must
equal bav_per_planet[planet][sign]. Needed for kakshya (fruitful-sub-division)
transit scoring.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
SCRIPT = os.path.join(PLUGIN, "scripts", "compute_vedic_baseline.py")

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(f"{name}: {detail}")
        print(f"FAIL {name} {detail}")
    else:
        print(f"PASS {name}")


CONTRIBUTORS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"}


def run_baseline():
    with open(os.path.join(HERE, "golden", "vedic.json")) as f:
        golden = json.load(f)
    cmd = [sys.executable, SCRIPT]
    for k, v in golden["args"].items():
        cmd += [k, v]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def validate(av, label):
    check(f"{label}: prastara key present", "prastara" in av)
    prastara, bav = av.get("prastara", {}), av["bav_per_planet"]
    check(f"{label}: sav total 337",
          sum(av["sav_per_sign"].values()) == 337 == av["sav_total"],
          f"{sum(av['sav_per_sign'].values())} / {av['sav_total']}")
    check(f"{label}: planets match", set(prastara) == set(bav))
    bad = []
    for p in bav:
        for s, n in bav[p].items():
            c = prastara.get(p, {}).get(s)
            if c is None or len(c) != n or len(set(c)) != len(c) \
                    or not set(c) <= CONTRIBUTORS:
                bad.append((p, s, c, n))
    check(f"{label}: prastara cells consistent with bav", not bad, str(bad[:3]))


validate(run_baseline()["ashtakavarga"], "live")
for snap in ("vedic.json", "vedic_chart.json"):
    with open(os.path.join(HERE, "snapshots", snap)) as f:
        validate(json.load(f)["ashtakavarga"], snap)


def test_no_regressions():
    assert not failures, failures


if __name__ == "__main__":
    sys.exit(1 if failures else 0)
