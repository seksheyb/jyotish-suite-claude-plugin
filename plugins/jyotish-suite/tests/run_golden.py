#!/usr/bin/env python3
"""
Golden-chart regression runner for jyotish-suite (blueprint Phase 5).

Regenerates each school's deterministic baseline from the pinned inputs in
tests/golden/*.json, diffs the output against tests/snapshots/<school>.json,
and prints a per-school PASS/FAIL. Exits non-zero on any mismatch or runtime
error so it can be wired into CI.

This guards TWO things: that edits to lib/ or scripts/compute_*_baseline.py
can't silently shift the numbers a synthesizer will read as ground truth,
for BOTH ways a chart reaches a baseline script:

  - the ephemeris path   (--datetime/--tz/--lat/--lon[+--number])
  - the pasted-chart path (lib/chart_io.py expands a hand-authored positions
    fixture, then the baseline is run with --chart <expanded chart JSON>)

A school's golden/<school>.json carries an optional "chart_path" block
(mode/positions/args) when its baseline supports --chart; kp_horary has none
(number-derived Lagna only — no pasted-chart path exists for it), and that's
documented in its golden file rather than forced.

It says nothing about reading quality — see README.md's "Synthesis-quality
eval" section for that gap.

Usage:
    python3 run_golden.py              # regenerate + diff against snapshots (both paths)
    python3 run_golden.py --update      # regenerate + overwrite snapshots (both paths)
    python3 run_golden.py --school kp_natal   # run a single school
"""

import argparse
import difflib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = TESTS_DIR.parent
GOLDEN_DIR = TESTS_DIR / "golden"
SNAPSHOTS_DIR = TESTS_DIR / "snapshots"
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
LIB_DIR = PLUGIN_ROOT / "lib"
CHART_IO = LIB_DIR / "chart_io.py"

# Fixed run order — matches the school order used elsewhere in the suite
# (agents/baseline-runner.md): vedic, bnn, jaimini, kp_natal, kp_horary, lalkitab.
SCHOOL_ORDER = ["vedic", "bnn", "jaimini", "kp_natal", "kp_horary", "lalkitab"]


def load_golden_configs():
    configs = {}
    for path in sorted(GOLDEN_DIR.glob("*.json")):
        with open(path) as fh:
            cfg = json.load(fh)
        configs[cfg["school"]] = cfg
    return configs


def build_cmd(script, extra_args):
    script_path = SCRIPTS_DIR / script
    cmd = [sys.executable, str(script_path)]
    for flag, value in extra_args.items():
        cmd.append(flag)
        cmd.append(str(value))
    return cmd


def run_cmd(cmd):
    """Run a subprocess command. Returns (ok, stdout_text, error_text)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # pragma: no cover - defensive
        return False, "", f"failed to launch: {exc}"
    if result.returncode != 0:
        return False, result.stdout, result.stderr.strip() or f"exit code {result.returncode}"
    if not result.stdout.strip():
        return False, "", "produced no stdout"
    try:
        json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return False, result.stdout, f"stdout is not valid JSON: {exc}"
    return True, result.stdout, ""


def run_baseline_ephemeris(cfg):
    """Run one baseline script via its ephemeris CLI entry point.
    Returns (ok, stdout_text, error_text)."""
    cmd = build_cmd(cfg["script"], cfg["args"])
    return run_cmd(cmd)


def expand_chart(chart_cfg, chart_out_dir, school):
    """Run lib/chart_io.py to expand a pasted-chart positions fixture into a
    full chart JSON. Returns (ok, expanded_path_or_None, error_text)."""
    positions_path = GOLDEN_DIR / chart_cfg["positions"]
    expanded_chart_path = chart_out_dir / f"{school}_expanded_chart.json"
    expand_cmd = [sys.executable, str(CHART_IO),
                  "--mode", chart_cfg["mode"],
                  "--positions", str(positions_path),
                  "--out", str(expanded_chart_path)]
    try:
        result = subprocess.run(expand_cmd, capture_output=True, text=True, timeout=60)
    except Exception as exc:  # pragma: no cover - defensive
        return False, None, f"failed to launch lib/chart_io.py: {exc}"
    if result.returncode != 0 or not expanded_chart_path.exists():
        err = result.stderr.strip() or f"exit code {result.returncode}"
        return False, None, f"lib/chart_io.py failed to expand chart: {err}"
    return True, expanded_chart_path, ""


def run_baseline_chart(cfg, chart_out_dir):
    """Expand the school's pasted-chart positions fixture via lib/chart_io.py,
    then run the baseline script against it with --chart. Returns
    (ok, stdout_text, error_text). Returns (None, "", "") if the school has no
    chart_path block (ephemeris-only school, e.g. kp_horary)."""
    chart_cfg = cfg.get("chart_path")
    if chart_cfg is None:
        return None, "", ""

    ok, expanded_chart_path, err = expand_chart(chart_cfg, chart_out_dir, cfg["school"])
    if not ok:
        return False, "", err

    extra_args = dict(chart_cfg.get("args", {}))
    extra_args["--chart"] = str(expanded_chart_path)
    cmd = build_cmd(cfg["script"], extra_args)
    return run_cmd(cmd)


def diff_preview(expected_text, actual_text, n=15):
    expected_lines = expected_text.splitlines(keepends=True)
    actual_lines = actual_text.splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        expected_lines, actual_lines,
        fromfile="snapshot", tofile="regenerated", n=1))
    return "".join(diff[:n]) if diff else "(no textual diff found)"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update", action="store_true",
                    help="Regenerate tests/snapshots/*.json from the golden "
                         "inputs instead of diffing against them.")
    ap.add_argument("--school", help="Run only this school "
                                     "(vedic/bnn/jaimini/kp_natal/kp_horary/lalkitab).")
    ap.add_argument("--out-dir", help="Write regenerated JSON here instead of a "
                                      "throwaway temp dir (useful for inspection).")
    args = ap.parse_args()

    configs = load_golden_configs()
    schools = [args.school] if args.school else SCHOOL_ORDER
    missing = [s for s in schools if s not in configs]
    if missing:
        sys.stderr.write(f"ERROR: no golden input for: {missing}\n"
                         f"Available: {sorted(configs)}\n")
        sys.exit(2)

    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    out_dir = Path(args.out_dir) if args.out_dir else None
    tmp_ctx = None
    if out_dir is None:
        tmp_ctx = tempfile.TemporaryDirectory(prefix="jyotish-golden-")
        out_dir = Path(tmp_ctx.name)
    else:
        out_dir.mkdir(parents=True, exist_ok=True)

    def check_against_snapshot(school, path_label, snapshot_name, stdout_text, regenerated_path):
        regenerated_path.write_text(stdout_text)
        if args.update:
            snapshot_path = SNAPSHOTS_DIR / snapshot_name
            snapshot_path.write_text(stdout_text)
            return (school, path_label, "UPDATED", str(snapshot_path))

        snapshot_path = SNAPSHOTS_DIR / snapshot_name
        if not snapshot_path.exists():
            return (school, path_label, "FAIL",
                    f"no snapshot at {snapshot_path} — run with --update first")

        expected_text = snapshot_path.read_text()
        if expected_text == stdout_text:
            return (school, path_label, "PASS", "")
        # Compare parsed JSON too, so a snapshot re-serialized with
        # different whitespace still gets a real diff, not noise.
        try:
            same_value = json.loads(expected_text) == json.loads(stdout_text)
        except json.JSONDecodeError:
            same_value = False
        if same_value:
            return (school, path_label, "PASS",
                    "(byte diff only — same JSON value, whitespace differs)")
        preview = diff_preview(expected_text, stdout_text)
        return (school, path_label, "FAIL", f"output diverged from snapshot\n{preview}")

    results = []  # (school, path_label, status, detail)
    try:
        for school in schools:
            cfg = configs[school]

            # --- ephemeris path (--datetime/--tz/--lat/--lon[+--number]) ---
            ok, stdout_text, err = run_baseline_ephemeris(cfg)
            regenerated_path = out_dir / f"{school}.json"
            if not ok:
                regenerated_path.write_text(stdout_text or "")
                results.append((school, "ephemeris", "FAIL", f"runtime error: {err}"))
            else:
                results.append(check_against_snapshot(
                    school, "ephemeris", f"{school}.json", stdout_text, regenerated_path))

            # --- pasted-chart path (lib/chart_io.py expansion + --chart) ---
            ok, stdout_text, err = run_baseline_chart(cfg, out_dir)
            if ok is None:
                # No chart_path block for this school (e.g. kp_horary) —
                # ephemeris-only by nature, not a gap to close.
                results.append((school, "chart", "N/A",
                                 "no pasted-chart path for this school (ephemeris-only)"))
                continue
            regenerated_chart_path = out_dir / f"{school}_chart.json"
            if not ok:
                regenerated_chart_path.write_text(stdout_text or "")
                results.append((school, "chart", "FAIL", f"runtime error: {err}"))
                continue
            results.append(check_against_snapshot(
                school, "chart", f"{school}_chart.json", stdout_text, regenerated_chart_path))
    finally:
        if tmp_ctx is not None:
            tmp_ctx.cleanup()

    print()
    print(f"{'School':<12} {'Path':<10} {'Status':<8}")
    print("-" * 50)
    any_fail = False
    for school, path_label, status, detail in results:
        print(f"{school:<12} {path_label:<10} {status:<8}")
        if status == "FAIL":
            any_fail = True
            for line in detail.splitlines():
                print(f"    {line}")
        elif detail and status == "UPDATED":
            print(f"    -> {detail}")
        elif detail and status == "N/A":
            print(f"    {detail}")
        elif detail:
            print(f"    {detail}")
    print("-" * 50)

    if args.update:
        updated = [f"{s}/{p}" for s, p, status, _ in results if status == "UPDATED"]
        print(f"Snapshots updated for: {', '.join(updated)}")
        sys.exit(0)

    n_pass = sum(1 for _, _, s, _ in results if s == "PASS")
    n_fail = sum(1 for _, _, s, _ in results if s == "FAIL")
    n_na = sum(1 for _, _, s, _ in results if s == "N/A")
    print(f"{n_pass}/{len(results) - n_na} PASS, {n_fail} FAIL "
          f"({n_na} N/A — ephemeris-only school)")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
