#!/usr/bin/env python3
"""
Regression guard for the Jaimini transit-trigger layer
(scripts/compute_jaimini_transits.py).

Class pinned: Jaimini timing had no transit layer (Chara Dasha only). The
script reads slow transits sign-to-sign against AL / UL / the running Chara
Dasha Rasi / Antardasha Rasi / Karakamsha / AK by Rasi Drishti, with Argala/
Virodha and the Jupiter+Saturn double transit.

Checks:
  1. Snapshot — pinned chart + pinned window (with --karakamsha-overlay)
     matches tests/snapshots/jaimini_transits.json exactly.
  2. Invariants — house_from_AL == count_signs(AL, sign); every `aspects`
     name is a real Rasi Drishti (matrix[sign][ref] == 1); every `conjoins`
     name shares the sign; argala type is primary for 2/4/11, secondary for 5,
     None otherwise; obstructed_by == natal planets in the Virodha sign;
     sign_stays / overlay sorted by entry_date; every overlay hit is labelled
     lineage_specific and its navamsa_idx == pada_to_navamsa(nak_idx, pada).
  3. Without --karakamsha-overlay every body has karakamsha_overlay: null.
  4. A baseline built without --target-date (no running Chara Dasha) makes
     the script exit non-zero with "running Chara Dasha" on stderr.
  5. Docs — SKILL.md, methodology.md, orchestration-notes.md and
     commands/jaimini.md name compute_jaimini_transits.py; methodology has 4C.

Regenerate the snapshot (only after an intended output change):
    python3 tests/test_jaimini_transits_regressions.py --update

Pinned chart: 1990-05-15T10:30:00 Asia/Kolkata, 28.6139N 77.2090E,
target-date 2026-01-01; window 2026-01-01 -> 2026-07-01 Asia/Kolkata.
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

BASELINE_SCRIPT = os.path.join(SCRIPTS, "compute_jaimini_baseline.py")
TRANSIT_SCRIPT = os.path.join(SCRIPTS, "compute_jaimini_transits.py")
SNAPSHOT = os.path.join(HERE, "snapshots", "jaimini_transits.json")

BIRTH = ["--datetime", "1990-05-15T10:30:00", "--tz", "Asia/Kolkata",
         "--lat", "28.6139", "--lon", "77.2090"]
WINDOW = ["--start-datetime", "2026-01-01T00:00:00",
          "--end-datetime", "2026-07-01T00:00:00", "--tz", "Asia/Kolkata"]

DOCS = [os.path.join(PLUGIN, "skills", "jaimini", "SKILL.md"),
        os.path.join(PLUGIN, "skills", "jaimini", "references", "methodology.md"),
        os.path.join(PLUGIN, "skills", "jaimini", "references",
                     "orchestration-notes.md"),
        os.path.join(PLUGIN, "commands", "jaimini.md")]

ARGALA = {2: ("primary", 12), 4: ("primary", 10), 11: ("primary", 3),
          5: ("secondary", 9)}

failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


def build_baseline(path, target_date=True):
    args = [sys.executable, BASELINE_SCRIPT, *BIRTH]
    if target_date:
        args += ["--target-date", "2026-01-01"]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    with open(path, "w") as fh:
        fh.write(out)


def run_transits(baseline, out_path, overlay=True):
    args = [sys.executable, TRANSIT_SCRIPT, "--baseline", baseline, *WINDOW,
            "--out", out_path]
    if overlay:
        args.append("--karakamsha-overlay")
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc


def iter_annotated(d):
    """Yield (where, record) for every annotated snapshot and sign stay."""
    for body, blk in d["bodies"].items():
        for key, snap in blk["positions"].items():
            yield f"{body}.positions.{key}", body, snap
        for i, h in enumerate(blk["sign_stays"]):
            yield f"{body}.sign_stays[{i}]", body, h


def check_invariants(d):
    ref = d["reference"]
    matrix = jp.jaimini_drishti_matrix()["matrix"]
    by_sign = ref["natal_planets_by_sign"]
    al = ref["AL"]["sign_idx"]
    ref_idx = {n: ref[n]["sign_idx"] for n in
               ("AL", "UL", "dasha_rasi", "karakamsha", "atmakaraka")}
    ad_idx = {a["sign"]: a["sign_idx"] for a in ref["antardashas_in_window"]}

    bad_house, bad_aspect, bad_conj, bad_argala, bad_obs = [], [], [], [], []
    for where, body, rec in iter_annotated(d):
        s = rec["sign_idx"]
        if rec["house_from_AL"] != jp.count_signs(al, s):
            bad_house.append(where)
        local = dict(ref_idx)
        if rec["antardasha_rasi_used"] is not None:
            local["antardasha_rasi"] = ad_idx.get(
                rec["antardasha_rasi_used"],
                jp.SIGNS.index(rec["antardasha_rasi_used"]))
        for n in rec["aspects"]:
            if matrix[s][local[n]] != 1:
                bad_aspect.append((where, n))
        for n in rec["conjoins"]:
            if local[n] != s:
                bad_conj.append((where, n))
        for rname in ("AL", "dasha_rasi"):
            arg = rec["argala"][rname]
            house = jp.count_signs(local[rname], s)
            want = ARGALA.get(house)
            if arg["house"] != house or arg["type"] not in ("primary", "secondary", None) \
                    or arg["type"] != (want[0] if want else None):
                bad_argala.append((where, rname, arg))
            want_obs = (by_sign.get(jp.SIGNS[jp.sign_n_from(local[rname], want[1])], [])
                        if want else [])
            if arg["obstructed_by"] != want_obs:
                bad_obs.append((where, rname, arg["obstructed_by"], want_obs))
    check("house_from_AL == count_signs(AL, sign) everywhere", not bad_house, bad_house)
    check("every `aspects` entry is a real Rasi Drishti", not bad_aspect, bad_aspect)
    check("every `conjoins` entry shares the transit sign", not bad_conj, bad_conj)
    check("argala type: 2/4/11 primary, 5 secondary, else None", not bad_argala,
          bad_argala)
    check("obstructed_by == natal planets in the Virodha sign", not bad_obs, bad_obs)

    unsorted, overlay_bad = [], []
    for body, blk in d["bodies"].items():
        for key in ("sign_stays", "karakamsha_overlay"):
            lst = blk[key] or []
            dates = [h["entry_date"] or "" for h in lst]
            if dates != sorted(dates):
                unsorted.append(f"{body}.{key}")
        for h in blk["karakamsha_overlay"] or []:
            nav = jp.pada_to_navamsa(h["nak_idx"], h["pada"])[0]
            kk = ref["karakamsha"]["sign_idx"]
            want_rel = ("same" if nav == kk else
                        "aspects" if matrix[nav][kk] == 1 else None)
            if h.get("layer") != "lineage_specific" or h["navamsa_idx"] != nav \
                    or h["relation_to_karakamsha"] != want_rel:
                overlay_bad.append((body, h["label"]))
    check("sign_stays / karakamsha_overlay sorted by entry_date", not unsorted, unsorted)
    check("overlay hits lineage_specific, navamsa == pada_to_navamsa, relation right",
          not overlay_bad, overlay_bad)
    check("every overlay body is non-empty with the flag",
          all(blk["karakamsha_overlay"] for blk in d["bodies"].values()))
    check("karakamsha_overlay_note present with the flag",
          "lineage-specific" in d.get("karakamsha_overlay_note", ""))

    dt_bad = []
    for key, dt in d["double_transit"].items():
        j = jp.SIGNS.index(dt["jupiter_sign"])
        sa = jp.SIGNS.index(dt["saturn_sign"])
        for n in ("AL", "UL", "dasha_rasi", "karakamsha"):
            r = ref_idx[n]
            want = ((j == r or matrix[j][r] == 1) and (sa == r or matrix[sa][r] == 1))
            if dt[f"on_{n}"] != want:
                dt_bad.append((key, n))
    check("double_transit flags == Jupiter AND Saturn occupy-or-aspect", not dt_bad,
          dt_bad)
    check("is_dasha_rasi_lord true only for the dasha Rasi's Jaimini lord",
          all(rec["is_dasha_rasi_lord"] == (body in ref["dasha_rasi"]["lord"].split("/"))
              for _w, body, rec in iter_annotated(d)))


def test_no_regressions(update=False):
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "baseline.json")
        out = os.path.join(tmp, "transits.json")
        build_baseline(base)
        proc = run_transits(base, out, overlay=True)
        check("script exits 0 on the pinned chart", proc.returncode == 0, proc.stderr)
        with open(out) as fh:
            d = json.load(fh)

        if update:
            with open(SNAPSHOT, "w") as fh:
                json.dump(d, fh, indent=2)
                fh.write("\n")
            print(f"snapshot written: {SNAPSHOT}")
        with open(SNAPSHOT) as fh:
            snap = json.load(fh)
        check("output matches tests/snapshots/jaimini_transits.json", d == snap,
              "regenerate with --update only after an intended change")

        check("reference: AL Taurus, UL Aquarius, dasha Rasi Sagittarius, "
              "Karakamsha Sagittarius",
              (d["reference"]["AL"]["sign"], d["reference"]["UL"]["sign"],
               d["reference"]["dasha_rasi"]["sign"],
               d["reference"]["karakamsha"]["sign"])
              == ("Taurus", "Aquarius", "Sagittarius", "Sagittarius"),
              d["reference"])
        check_invariants(d)

        out2 = os.path.join(tmp, "transits_no_overlay.json")
        proc = run_transits(base, out2, overlay=False)
        with open(out2) as fh:
            d2 = json.load(fh)
        check("without --karakamsha-overlay every karakamsha_overlay is null",
              proc.returncode == 0
              and all(blk["karakamsha_overlay"] is None for blk in d2["bodies"].values())
              and "karakamsha_overlay_note" not in d2)

        base_nr = os.path.join(tmp, "baseline_no_running.json")
        build_baseline(base_nr, target_date=False)
        proc = run_transits(base_nr, os.path.join(tmp, "x.json"), overlay=False)
        check("baseline without --target-date -> non-zero exit, 'running Chara Dasha'",
              proc.returncode != 0 and "running Chara Dasha" in proc.stderr,
              (proc.returncode, proc.stderr))

    for path in DOCS:
        with open(path) as fh:
            text = fh.read()
        check(f"{os.path.relpath(path, PLUGIN)} names compute_jaimini_transits.py",
              "compute_jaimini_transits.py" in text)
    with open(DOCS[1]) as fh:
        meth = fh.read()
    check("methodology.md has Section 4C", "4C" in meth and "### 4C" in meth)

    assert not failures, f"{len(failures)} jaimini transit check(s) FAILED: {failures}"


if __name__ == "__main__":
    try:
        test_no_regressions(update="--update" in sys.argv)
    except AssertionError:
        pass
    print()
    print("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}")
    sys.exit(1 if failures else 0)
