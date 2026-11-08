#!/usr/bin/env python3
"""
Regression guard for the vedic-astro transit (gochara) layer —
scripts/compute_gochara.py.

Standalone (no pytest needed): PASS/FAIL per check, nonzero exit on failure;
test_no_regressions() is the pytest entry point. Mirrors
tests/test_lib_regressions.py.

Checks:
  1. Snapshot — on the pinned chart (1990-05-15T10:30 Asia/Kolkata, 28.6139N
     77.2090E, baseline asof 2026-01-01T09:00) the 2026-01-01 -> 2026-07-01
     window equals tests/snapshots/gochara.json.
  2. Invariants recomputed here from lib/jyotish_primitives.py:
     house_from_moon of every position; D9 overlay navamsa == pada_to_navamsa;
     every hit list sorted by entry_date; no vedha obstructor forms an exempt
     pair with the body; Rahu/Ketu carry kakshya.fruitful / bav_bindus None;
     Saturn's saturn_phase == saturn_moon_phase(); kakshya_stays None for
     Sun/Moon; the Moon is excluded from d9_overlay by default
     (--d9-overlay-bodies); --no-d9-overlay yields d9_overlay null.
  3. Docs — the vedic-astro skill, its methodology and orchestration notes,
     and commands/vedic-astro.md all reference compute_gochara.py;
     methodology carries a Step 4b.

Regenerate the snapshot (only after an intended output change):
  python3 scripts/compute_vedic_baseline.py --datetime 1990-05-15T10:30:00 \\
    --tz Asia/Kolkata --lat 28.6139 --lon 77.2090 \\
    --asof 2026-01-01T09:00:00 > /tmp/vb.json
  python3 scripts/compute_gochara.py --baseline /tmp/vb.json \\
    --start-datetime 2026-01-01T00:00:00 --end-datetime 2026-07-01T00:00:00 \\
    --tz Asia/Kolkata --out tests/snapshots/gochara.json
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
SCRIPTS = os.path.join(PLUGIN, "scripts")
for _cand in (os.path.join(PLUGIN, "lib"),):
    if os.path.isfile(os.path.join(_cand, "ephemeris.py")):
        sys.path.insert(0, _cand)

import jyotish_primitives as jp  # noqa: E402

SNAPSHOT = os.path.join(HERE, "snapshots", "gochara.json")
BASELINE_ARGS = ["--datetime", "1990-05-15T10:30:00", "--tz", "Asia/Kolkata",
                 "--lat", "28.6139", "--lon", "77.2090",
                 "--asof", "2026-01-01T09:00:00"]
WINDOW_ARGS = ["--start-datetime", "2026-01-01T00:00:00",
               "--end-datetime", "2026-07-01T00:00:00", "--tz", "Asia/Kolkata"]

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name} {detail}")
        failures.append(name)


def run(cmd):
    return subprocess.run(cmd, cwd=PLUGIN, capture_output=True, text=True,
                          timeout=300)


# --------------------------------------------------------------------
# 1. Build baseline + gochara output (default and --no-d9-overlay).
# --------------------------------------------------------------------
out = off = None
with tempfile.TemporaryDirectory() as tmp:
    base_path = os.path.join(tmp, "vedic_baseline.json")
    proc = run([sys.executable,
                os.path.join(SCRIPTS, "compute_vedic_baseline.py")]
               + BASELINE_ARGS)
    check("compute_vedic_baseline.py exits 0", proc.returncode == 0,
          proc.stderr)
    with open(base_path, "w") as fh:
        fh.write(proc.stdout)
    base = json.loads(proc.stdout) if proc.returncode == 0 else {}

    g_path = os.path.join(tmp, "transits.json")
    proc = run([sys.executable, os.path.join(SCRIPTS, "compute_gochara.py"),
                "--baseline", base_path] + WINDOW_ARGS + ["--out", g_path])
    check("compute_gochara.py exits 0", proc.returncode == 0, proc.stderr)
    if proc.returncode == 0:
        with open(g_path) as fh:
            out = json.load(fh)

    off_path = os.path.join(tmp, "transits_no_d9.json")
    proc = run([sys.executable, os.path.join(SCRIPTS, "compute_gochara.py"),
                "--baseline", base_path] + WINDOW_ARGS
               + ["--no-d9-overlay", "--bodies", "Saturn,Moon",
                  "--out", off_path])
    check("compute_gochara.py --no-d9-overlay exits 0", proc.returncode == 0,
          proc.stderr)
    if proc.returncode == 0:
        with open(off_path) as fh:
            off = json.load(fh)

    bad_path = os.path.join(tmp, "bad.json")
    with open(bad_path, "w") as fh:
        json.dump({"lagna": {"sign": "Aries"}}, fh)
    proc = run([sys.executable, os.path.join(SCRIPTS, "compute_gochara.py"),
                "--baseline", bad_path] + WINDOW_ARGS)
    check("incomplete baseline fails loudly (exit 1 + stderr)",
          proc.returncode == 1 and "missing required key" in proc.stderr,
          proc.stderr)

with open(SNAPSHOT) as fh:
    snap = json.load(fh)
check("gochara: parsed JSON equals snapshot", out == snap)

# --------------------------------------------------------------------
# 2. Invariants.
# --------------------------------------------------------------------
if out is not None:
    ref = out["reference"]
    moon_idx = ref["moon_sign_idx"]
    bodies = out["bodies"]
    check("default bodies present",
          list(bodies) == ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars",
                           "Sun", "Moon"], list(bodies))
    check("ayanamsa defaults to lahiri", out["ayanamsa"]["mode"] == "lahiri")

    bad_house, bad_nav, unsorted, bad_exempt = [], [], [], []
    for body, v in bodies.items():
        for name, pos in v["positions"].items():
            if pos["house_from_moon"] != jp.count_signs(moon_idx,
                                                        pos["sign_idx"]):
                bad_house.append((body, name))
        for h in v["sign_stays"]:
            if h["house_from_moon"] != jp.count_signs(moon_idx,
                                                      h["sign_idx"]):
                bad_house.append((body, h["entry_date"]))
            for o in h["vedha"]["obstructed_by"]:
                if o == body or jp.is_vedha_exempt(body, o):
                    bad_exempt.append((body, o))
        for h in v["d9_overlay"] or []:
            if h["navamsa_idx"] != jp.pada_to_navamsa(h["nak_idx"],
                                                      h["pada"])[0]:
                bad_nav.append((body, h["label"]))
            if h.get("layer") != "modern_overlay":
                bad_nav.append((body, "layer"))
        for key in ("sign_stays", "nakshatra_stays", "kakshya_stays",
                    "d9_overlay"):
            hits = v[key]
            if hits is None:
                continue
            dates = [h["entry_date"] for h in hits]
            if dates != sorted(dates):
                unsorted.append((body, key))
    check("house_from_moon == count_signs(moon, sign) everywhere",
          not bad_house, bad_house)
    check("D9 overlay navamsa_idx == pada_to_navamsa and layer labelled",
          not bad_nav, bad_nav[:5])
    check("every hit list sorted by entry_date", not unsorted, unsorted)
    check("no vedha obstructor is the body itself or an exempt pair",
          not bad_exempt, bad_exempt)

    node_bad = []
    for node in ("Rahu", "Ketu"):
        for name, pos in bodies[node]["positions"].items():
            if pos["kakshya"]["fruitful"] is not None or \
                    pos["bav_bindus"] is not None:
                node_bad.append((node, name))
        for h in bodies[node]["kakshya_stays"]:
            if h["fruitful"] is not None:
                node_bad.append((node, h["label"]))
        for h in bodies[node]["sign_stays"]:
            if h["bav_bindus"] is not None:
                node_bad.append((node, h["label"]))
    check("Rahu/Ketu: kakshya fruitful and bav_bindus are None",
          not node_bad, node_bad)

    sat = bodies["Saturn"]
    sat_ok = all(p["saturn_phase"] == jp.saturn_moon_phase(p["sign_idx"],
                                                           moon_idx)
                 for p in sat["positions"].values()) and \
        all(h["saturn_phase"] == jp.saturn_moon_phase(h["sign_idx"], moon_idx)
            for h in sat["sign_stays"])
    check("Saturn saturn_phase == saturn_moon_phase()", sat_ok)
    check("saturn_phase only on Saturn",
          all("saturn_phase" not in p for b, v in bodies.items()
              if b != "Saturn" for p in v["positions"].values()))
    check("kakshya_stays is None for Sun and Moon",
          bodies["Sun"]["kakshya_stays"] is None
          and bodies["Moon"]["kakshya_stays"] is None)
    check("kakshya_stays present for Saturn/Jupiter/Rahu/Ketu/Mars",
          all(isinstance(bodies[b]["kakshya_stays"], list)
              for b in ("Saturn", "Jupiter", "Rahu", "Ketu", "Mars")))

    tara_ok = all(
        (p["tara"]["idx"], p["tara"]["name"], p["tara"]["favourable"])
        == jp.tara_bala(ref["moon_nak_idx"], p["nak_idx"])
        for v in bodies.values() for p in v["positions"].values())
    check("positions tara == tara_bala(janma, transit)", tara_ok)

    fruit_ok = True
    for body in ("Saturn", "Jupiter", "Mars"):
        for p in bodies[body]["positions"].values():
            k_idx, k_lord = jp.kakshya_of(p["longitude"])
            if p["kakshya"]["idx"] != k_idx or p["kakshya"]["lord"] != k_lord:
                fruit_ok = False
    check("positions kakshya == kakshya_of(longitude)", fruit_ok)

    # Pinned-chart facts (Moon in Sagittarius, Cancer Lagna).
    check("pinned: Saturn in Pisces = Kantaka Shani (4th from Moon)",
          sat["positions"]["window_start"]["sign"] == "Pisces"
          and sat["positions"]["window_start"]["saturn_phase"]
          == "kantaka_shani")
    ju0 = bodies["Jupiter"]["sign_stays"][0]
    check("pinned: Jupiter in Gemini 7th from Moon favourable, Rahu in "
          "vedha house 3",
          ju0["sign"] == "Gemini" and ju0["gochara"]["favourable"]
          and ju0["vedha"]["house"] == 3
          and "Rahu" in ju0["vedha"]["obstructed_by"], ju0.get("vedha"))
    check("pinned: double transit on the Moon sign at window start",
          out["double_transit"]["window_start"]["from_moon"] == [1])
    check("d9_overlay_note present and labels the layer modern",
          isinstance(out.get("d9_overlay_note"), str)
          and "modern" in out["d9_overlay_note"])

if off is not None:
    # Vedha intervals: inside the stay, sorted, never exempt, consistent with
    # the at-entry obstructor list and with clear_at / obstructed_to_end.
    bad = []
    for bname, v in out["bodies"].items():
        for h in v["sign_stays"]:
            vd = h["vedha"]
            for k in ("intervals", "obstructed_to_end", "clear_at"):
                if k not in vd:
                    bad.append((bname, h["sign"], "missing " + k))
            ivs = vd.get("intervals", [])
            if vd["house"] is None and ivs:
                bad.append((bname, h["sign"], "intervals on non-favourable stay"))
            starts = [x["start"] for x in ivs]
            if starts != sorted(starts):
                bad.append((bname, h["sign"], "unsorted intervals"))
            for x in ivs:
                if not (h["entry_date"] <= x["start"] < x["end"] <= h["exit_date"]):
                    bad.append((bname, h["sign"], "interval outside stay", x))
                if x["planet"] == bname or jp.is_vedha_exempt(bname, x["planet"]):
                    bad.append((bname, h["sign"], "exempt/self obstructor", x["planet"]))
            at_entry = {x["planet"] for x in ivs if x["start"] == h["entry_date"]}
            if set(vd["obstructed_by"]) != at_entry:
                bad.append((bname, h["sign"], "obstructed_by != intervals at entry",
                            vd["obstructed_by"], sorted(at_entry)))
            if (vd["clear_at"] is None) != (not ivs or vd["obstructed_to_end"]):
                bad.append((bname, h["sign"], "clear_at inconsistent"))
            if vd["clear_at"] is not None and vd["clear_at"] != max(x["end"] for x in ivs):
                bad.append((bname, h["sign"], "clear_at != last interval end"))
            xm = [x for x in ivs if x["planet"] != "Moon"]
            if (vd["clear_at_excluding_moon"] is None) != (not xm or vd["obstructed_to_end_excluding_moon"]):
                bad.append((bname, h["sign"], "clear_at_excluding_moon inconsistent"))
            if xm and vd["clear_at_excluding_moon"] is not None \
                    and vd["clear_at_excluding_moon"] != max(x["end"] for x in xm):
                bad.append((bname, h["sign"], "clear_at_excluding_moon != last non-Moon end"))
    check("vedha intervals consistent on every sign stay", not bad, str(bad[:4]))
    check("pinned: Jupiter in Gemini vedha by Rahu runs to the end of the stay",
          any(h["sign"] == "Gemini" and h["vedha"]["obstructed_to_end"]
              and any(x["planet"] == "Rahu" for x in h["vedha"]["intervals"])
              for h in out["bodies"]["Jupiter"]["sign_stays"]))
    check("vedic baseline carries dasha.current_antardasha_pratyantars incl. running PD",
          any(x["ad_lord"] == base["dasha"]["running"]["pratyantardasha"]["lord"]
              and x["start"] == base["dasha"]["running"]["pratyantardasha"]["start"]
              for x in base["dasha"]["current_antardasha_pratyantars"]))
    check("default run: Moon has no d9_overlay (excluded by default), Sun does",
          out["bodies"]["Moon"]["d9_overlay"] is None
          and isinstance(out["bodies"]["Sun"]["d9_overlay"], list)
          and len(out["bodies"]["Sun"]["d9_overlay"]) > 0)
    check("default run: Moon keeps the engine's 0.25-day step (no pada tightening)",
          out["bodies"]["Moon"]["sampling_step_days"] == 0.25,
          str(out["bodies"]["Moon"]["sampling_step_days"]))
    check("--no-d9-overlay yields d9_overlay null for every body",
          all(v["d9_overlay"] is None for v in off["bodies"].values()))
    check("--no-d9-overlay yields d9_overlay_note null",
          off.get("d9_overlay_note") is None)

# --------------------------------------------------------------------
# 3. Docs wiring.
# --------------------------------------------------------------------
DOCS = {
    "skills/vedic-astro/SKILL.md": None,
    "skills/vedic-astro/references/methodology.md": "Step 4b",
    "skills/vedic-astro/references/orchestration-notes.md": None,
    "commands/vedic-astro.md": None,
}
for rel, extra in DOCS.items():
    with open(os.path.join(PLUGIN, rel), encoding="utf-8") as fh:
        text = fh.read()
    check(f"{rel} references compute_gochara.py", "compute_gochara.py" in text)
    if extra:
        check(f"{rel} contains '{extra}'", extra in text)


# --------------------------------------------------------------------
def test_no_regressions():
    """pytest entry point. The checks above run at import; this reports them.

    Kept separate from the __main__ block below because a module-level
    sys.exit() fires during pytest's collection, which aborts the whole run
    with an INTERNALERROR instead of failing this file cleanly.
    """
    assert not failures, (
        f"{len(failures)} gochara regression check(s) FAILED: {failures}")


if __name__ == "__main__":
    if failures:
        print(f"\n{len(failures)} regression check(s) FAILED: {failures}")
        sys.exit(1)
    print("\nAll gochara regression checks PASSED.")
