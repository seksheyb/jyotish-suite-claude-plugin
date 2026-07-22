#!/usr/bin/env python3
"""
Golden-chart regression runner for jyotish-suite (blueprint Phase 5).

Regenerates each school's deterministic baseline from the pinned inputs in
tests/golden/*.json, diffs the output against tests/snapshots/<school>.json,
and prints a per-school PASS/FAIL. Exits non-zero on any mismatch or runtime
error so it can be wired into CI.

This guards ONE thing: that edits to lib/ or scripts/compute_*_baseline.py
can't silently shift the numbers a synthesizer will read as ground truth.
It says nothing about reading quality — see README.md's "Synthesis-quality
eval" section for that gap.

Usage:
    python3 run_golden.py              # regenerate + diff against snapshots
    python3 run_golden.py --update      # regenerate + overwrite snapshots
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


def build_cmd(cfg):
    script_path = SCRIPTS_DIR / cfg["script"]
    cmd = [sys.executable, str(script_path)]
    for flag, value in cfg["args"].items():
        cmd.append(flag)
        cmd.append(str(value))
    return cmd


def run_baseline(cfg):
    """Run one baseline script. Returns (ok, stdout_text, error_text)."""
    cmd = build_cmd(cfg)
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

    results = []  # (school, status, detail)
    try:
        for school in schools:
            cfg = configs[school]
            ok, stdout_text, err = run_baseline(cfg)
            regenerated_path = out_dir / f"{school}.json"

            if not ok:
                regenerated_path.write_text(stdout_text or "")
                results.append((school, "FAIL", f"runtime error: {err}"))
                continue

            regenerated_path.write_text(stdout_text)

            if args.update:
                snapshot_path = SNAPSHOTS_DIR / f"{school}.json"
                snapshot_path.write_text(stdout_text)
                results.append((school, "UPDATED", str(snapshot_path)))
                continue

            snapshot_path = SNAPSHOTS_DIR / f"{school}.json"
            if not snapshot_path.exists():
                results.append((school, "FAIL", f"no snapshot at {snapshot_path} "
                                                 f"— run with --update first"))
                continue

            expected_text = snapshot_path.read_text()
            if expected_text == stdout_text:
                results.append((school, "PASS", ""))
            else:
                # Compare parsed JSON too, so a snapshot re-serialized with
                # different whitespace still gets a real diff, not noise.
                try:
                    same_value = json.loads(expected_text) == json.loads(stdout_text)
                except json.JSONDecodeError:
                    same_value = False
                if same_value:
                    results.append((school, "PASS",
                                    "(byte diff only — same JSON value, "
                                    "whitespace differs)"))
                else:
                    preview = diff_preview(expected_text, stdout_text)
                    results.append((school, "FAIL", f"output diverged from snapshot\n{preview}"))
    finally:
        if tmp_ctx is not None:
            tmp_ctx.cleanup()

    print()
    print(f"{'School':<12} {'Status':<8}")
    print("-" * 40)
    any_fail = False
    for school, status, detail in results:
        print(f"{school:<12} {status:<8}")
        if status == "FAIL":
            any_fail = True
            for line in detail.splitlines():
                print(f"    {line}")
        elif detail and status == "UPDATED":
            print(f"    -> {detail}")
        elif detail:
            print(f"    {detail}")
    print("-" * 40)

    if args.update:
        print(f"Snapshots updated for: {', '.join(s for s, *_ in results)}")
        sys.exit(0)

    n_pass = sum(1 for _, s, _ in results if s == "PASS")
    n_fail = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"{n_pass}/{len(results)} PASS, {n_fail} FAIL")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
