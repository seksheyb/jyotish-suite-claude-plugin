#!/usr/bin/env python3
"""
Regression guards for lib/transit_engine.py — the school-agnostic transit
sampling engine extracted from scripts/compute_transits.py.

Plain checks + PASS/FAIL prints, nonzero exit on failure (standalone), plus a
single pytest entry point (test_no_regressions). Runnable from the repo root
via pytest or from the plugin dir via `python3 tests/<this file>`.

Covers:
  1. KP neutrality — compute_transits.py output is byte-identical to the
     pre-extraction snapshot tests/snapshots/kp_transits.json.
  2. in_span 360-degree wraparound (the KP original had none).
  3. find_hits on synthetic motion (injected lon_fn, no ephemeris): clean
     entry, entry-before-window, retrograde re-entry -> two hits, and a
     crossing through 0 deg Aries.
  4. Span builders: pada_spans (108, contiguous, navamsa at midpoint),
     kakshya_spans (96, lord order per sign), degree_point_span wraparound.
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
LIB = os.path.join(PLUGIN, "lib")
SCRIPTS = os.path.join(PLUGIN, "scripts")
sys.path.insert(0, LIB)

import jyotish_primitives as jp  # noqa: E402
import transit_engine as te      # noqa: E402

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name} {detail}")
        failures.append(name)


# --------------------------------------------------------------------
# 1. KP neutrality — byte-identical to the pre-extraction snapshot.
# --------------------------------------------------------------------
SNAPSHOT = os.path.join(HERE, "snapshots", "kp_transits.json")
SIGS = os.path.join(HERE, "fixtures", "kp_transit_significators.json")

with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "kp_transits_now.json")
    proc = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "compute_transits.py"),
         "--start-datetime", "2026-01-01T00:00:00",
         "--end-datetime", "2026-04-01T00:00:00",
         "--tz", "Asia/Kolkata",
         "--significators", SIGS,
         "--out", out_path],
        cwd=PLUGIN, capture_output=True, text=True)
    check("compute_transits.py exits 0", proc.returncode == 0, proc.stderr)
    now_bytes = open(out_path, "rb").read() if proc.returncode == 0 else b""

snap_bytes = open(SNAPSHOT, "rb").read()
snap = json.loads(snap_bytes)
now = json.loads(now_bytes) if now_bytes else None

check("KP snapshot is non-trivial (has hits)",
      sum(len(v["hits"]) for v in snap["transits"].values()) > 0)
check("KP transits: parsed JSON equals snapshot", now == snap)
check("KP transits: raw output bytes equal snapshot", now_bytes == snap_bytes)
check("KP transits: re-serialised (indent=2, default=str) equals snapshot",
      now is not None
      and json.dumps(now, indent=2, default=str).encode() == snap_bytes)
check("KP hits carry no engine-internal 'label' key",
      now is not None and all("label" not in h
                              for v in now["transits"].values()
                              for h in v["hits"]))

# --------------------------------------------------------------------
# 2. in_span wraparound.
# --------------------------------------------------------------------
for args, want in [((5, 350, 10), True), ((355, 350, 10), True),
                   ((180, 350, 10), False), ((10, 350, 10), False),
                   ((0, 0, 30), True), ((30, 0, 30), False)]:
    check(f"in_span{args} == {want}", te.in_span(*args) is want)

# --------------------------------------------------------------------
# 3. find_hits on synthetic motion (1 deg/day, 1-day step, naive UTC).
# --------------------------------------------------------------------
T0 = datetime(2026, 1, 1)
SPAN = {"label": "test-arc", "start_deg": 30.0, "end_deg": 60.0,
        "nakshatra": "Extra"}


def days(dt):
    return (dt - T0).total_seconds() / 86400.0


def linear(start_lon):
    return lambda body, dt: (start_lon + days(dt)) % 360.0


def scan(lon_fn, span, n_days):
    series = te.sample_series("X", T0, T0 + timedelta(days=n_days), 1.0,
                              lon_fn)
    return te.find_hits("X", series, span, lon_fn)


hits = scan(linear(25.0), SPAN, 20)
check("linear prograde: exactly one hit", len(hits) == 1, f"(got {hits})")
if len(hits) == 1:
    h = hits[0]
    entry_day = days(datetime.fromisoformat(h["entry_date"]))
    check("linear prograde: entry_before_window False",
          h["entry_before_window"] is False)
    check("linear prograde: entry at day 5 (+/-0.01)",
          abs(entry_day - 5.0) < 0.01, f"(got {entry_day})")
    check("linear prograde: exit_after_window True",
          h["exit_after_window"] is True)
    check("hit carries label + span extra keys verbatim",
          h["label"] == "test-arc" and h["nakshatra"] == "Extra"
          and "start_deg" not in h and "end_deg" not in h)

hits = scan(linear(35.0), SPAN, 20)
check("series starting inside span: entry_before_window True",
      len(hits) == 1 and hits[0]["entry_before_window"] is True)


def retro_lon(body, dt):
    d = days(dt)
    if d <= 10:
        return 25.0 + d            # in at d5
    if d <= 20:
        return 35.0 - (d - 10)     # out at d15
    return 25.0 + (d - 20)         # back in at d25


hits = scan(retro_lon, SPAN, 30)
check("enter / retrograde out / re-enter: two hits", len(hits) == 2,
      f"(got {len(hits)})")
if len(hits) == 2:
    exit1 = days(datetime.fromisoformat(hits[0]["exit_date"]))
    entry2 = days(datetime.fromisoformat(hits[1]["entry_date"]))
    check("retrograde: first exit ~day 15, second entry ~day 25",
          abs(exit1 - 15) < 0.01 and abs(entry2 - 25) < 0.01,
          f"(exit1 {exit1}, entry2 {entry2})")

hits = scan(linear(355.0), te.degree_point_span(0.0, 2.0), 10)
check("crossing 0 deg Aries into [358, 2): one hit entering ~day 3",
      len(hits) == 1
      and abs(days(datetime.fromisoformat(hits[0]["entry_date"])) - 3) < 0.01
      and hits[0]["exit_after_window"] is False,
      f"(got {hits})")

# --------------------------------------------------------------------
# 4. Span builders.
# --------------------------------------------------------------------
padas = te.pada_spans()
check("pada_spans: 108 spans", len(padas) == 108)
check("pada_spans: contiguous 0 -> 360",
      padas[0]["start_deg"] == 0.0
      and abs(padas[-1]["end_deg"] - 360.0) < 1e-9
      and all(padas[i]["end_deg"] == padas[i + 1]["start_deg"]
              for i in range(107)))
check("pada_spans: navamsa_idx == jp.navamsa_sign(midpoint)",
      all(p["navamsa_idx"] == jp.navamsa_sign(
          (p["start_deg"] + p["end_deg"]) / 2)[0] for p in padas))
check("pada_spans: pada 1-4 cycles within each nakshatra",
      [p["pada"] for p in padas] == [1, 2, 3, 4] * 27)

kaks = te.kakshya_spans()
check("kakshya_spans: 96 spans", len(kaks) == 96)
check("kakshya_spans: lords cycle in KAKSHYA_LORDS order within each sign",
      all([k["kakshya_lord"] for k in kaks[s * 8:(s + 1) * 8]]
          == te.KAKSHYA_LORDS
          and all(k["sign_idx"] == s for k in kaks[s * 8:(s + 1) * 8])
          for s in range(12)))
check("kakshya_spans: contiguous 3.75-deg arcs",
      all(abs(k["start_deg"] - i * 3.75) < 1e-9
          and abs(k["end_deg"] - k["start_deg"] - 3.75) < 1e-9
          for i, k in enumerate(kaks)))

check("sign_spans: 12 x 30 deg", len(te.sign_spans()) == 12)
check("nakshatra_spans: 27 with star lords matching jp.NAKSHATRAS",
      [(s["nakshatra"], s["star_lord"]) for s in te.nakshatra_spans()]
      == [tuple(n) for n in jp.NAKSHATRAS])

dp = te.degree_point_span(359.5, 1.0)
check("degree_point_span(359.5, 1.0) wraps to [358.5, 0.5)",
      abs(dp["start_deg"] - 358.5) < 1e-9 and abs(dp["end_deg"] - 0.5) < 1e-9)
check("degree_point_span(359.5, 1.0) accepts 0.2",
      te.in_span(0.2, dp["start_deg"], dp["end_deg"]))
check("degree_point_span(359.5, 1.0) accepts 359.0",
      te.in_span(359.0, dp["start_deg"], dp["end_deg"]))
check("degree_point_span(359.5, 1.0) rejects 1.0",
      not te.in_span(1.0, dp["start_deg"], dp["end_deg"]))


def test_no_regressions():
    assert not failures, f"transit engine regressions: {failures}"


if __name__ == "__main__":
    print()
    if failures:
        print(f"{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("ALL TRANSIT ENGINE REGRESSION CHECKS PASS")
