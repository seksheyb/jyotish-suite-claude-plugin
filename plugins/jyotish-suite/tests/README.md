# Golden-chart regression harness

Blueprint Phase 5 (`OPTIMIZATION-BLUEPRINT.md` §8). This guards one thing:
**edits to `lib/` or `scripts/compute_*_baseline.py` can't silently shift the
numbers a synthesizer will read as ground truth.** It says nothing about
reading quality — see "Synthesis-quality eval" below for that gap.

## What's here

```
tests/
  golden/            one fully-pinned input per school (JSON: script + CLI args)
  snapshots/         the expected baseline JSON per school, checked in
  run_golden.py       regenerates every baseline, diffs against snapshots
  README.md           this file
```

Each file in `golden/` pins **every** value the matching `compute_<school>_baseline.py`
needs, including the values that would otherwise default to "now":

| School      | Script                              | What's pinned |
| ----------- | ------------------------------------ | -------------- |
| `vedic`     | `compute_vedic_baseline.py`         | Birth data (1990-05-15 10:30 IST, Delhi) + `--asof` (script calls `datetime.now(timezone.utc)` if this is omitted) |
| `bnn`       | `compute_bnn_baseline.py`           | Birth data only — no clock dependency in this script |
| `jaimini`   | `compute_jaimini_baseline.py`       | Birth data + `--target-date` (without it or `--age`, no running Chara Dasha window resolves at all) |
| `kp_natal`  | `compute_kp_natal_baseline.py`      | Birth data + `--rp-datetime` (script calls `datetime.now()` for Ruling Planets if this is omitted) |
| `kp_horary` | `compute_kp_horary_baseline.py`     | Horary number **108** + `--datetime` (the moment-of-reading, 2026-01-01T09:00:00 IST — for horary this parameter is inherently "now", so it's a required flag, not a hidden default) |
| `lalkitab`  | `compute_lalkitab_baseline.py`      | Birth data + `--age` **35** (querent's age at the same 2026-01-01 reading moment used elsewhere, so Varshphal/timing windows are fixed) |

Birth data is the same fixed chart everywhere it's used: **1990-05-15T10:30:00,
Asia/Kolkata, lat 28.6139, lon 77.2090 (Delhi)**. The "moment of reading"
(2026-01-01T09:00:00 IST) is likewise shared across every KP-flavored
parameter that needs one.

Determinism was verified by hand before the first snapshot was cut: every
baseline was run twice from its pinned `golden/*.json` input and the two
stdout blobs were byte-diffed (`diff -q`) — all six matched exactly.
`run_golden.py` itself only runs each baseline once per invocation (running
twice every time would double CI cost for no ongoing benefit once the
one-time determinism check has passed); re-run the two-invocations-and-diff
check by hand if you ever suspect a script picked up a hidden clock/RNG
dependency.

## Running it

```bash
cd plugins/jyotish-suite/tests

# Regenerate every baseline from the pinned inputs, diff against snapshots/,
# print per-school PASS/FAIL. Exits non-zero if anything mismatches.
python3 run_golden.py

# Same, but only one school:
python3 run_golden.py --school kp_natal

# Regenerate AND overwrite the checked-in snapshots (after an intentional
# change to lib/ or a baseline script):
python3 run_golden.py --update

# Keep the regenerated JSON around for inspection instead of a throwaway temp dir:
python3 run_golden.py --out-dir /tmp/jyotish-golden-out
```

A clean run looks like:

```
School       Status
----------------------------------------
vedic        PASS
bnn          PASS
jaimini      PASS
kp_natal     PASS
kp_horary    PASS
lalkitab     PASS
----------------------------------------
6/6 PASS, 0 FAIL
```

A `FAIL` row prints a unified diff preview (first ~15 lines) against the
snapshot and the script's stderr if it crashed outright. If a script fails to
run at all (import error, missing dependency, argparse mismatch), that's
recorded as `FAIL: runtime error: <stderr>` rather than silently skipped —
treat that as a P0, not a snapshot problem.

## What this does NOT guard

- **Reading quality.** A baseline can be numerically identical and still feed
  a worse synthesis if the synthesizer prompt, model, or effort earmark
  regresses. That's the gate below.
- **The chart-verifier / chart-io pasted-chart path.** These snapshots only
  exercise the ephemeris (`--datetime/--tz/--lat/--lon`) entry point of each
  script, not the `--chart <path>` entry point that consumes a pasted chart
  via `lib/chart_io.py`. The underlying `assemble_parashari`/`assemble_kp`
  code is shared, so this is a narrower gap than it looks, but it is a real
  one — worth a second golden fixture per school if pasted-chart drift is
  ever suspected.
- **The delta scripts** (`compute_transits.py`, `find_fruitful_window.py`,
  `lk_upaay_check.py`) — not baselines in the six-school sense, not covered
  here.

## Synthesis-quality eval (manual gate)

Blueprint §3 downgrades the synthesizer from opus to sonnet/high for 4 of 6
schools (vedic-astro, kp-natal, kp-horary, lal-kitab), keeping opus/medium
only for jaimini-astrology and bnn-astrology full/reverse readings (§7.1,
"Guard status" table, row 1 — flagged as a gap this blueprint creates).
Blueprint §8 Phase 5 makes that downgrade **contingent on a quality gate**,
not just this numeric harness passing.

This section is a scaffolding note, not an implementation — no LLM-judge
tooling exists yet. When it's built, the gate should look like:

1. **2–3 golden readings per school**, generated end-to-end off the pinned
   `golden/` chart above (so the baseline is byte-identical to what this
   harness snapshots), covering:
   - a full/broad reading (heaviest fan-out, most unit blocks for the
     synthesizer to reconcile)
   - a narrow/single-domain question (least fan-out — checks the downgrade
     doesn't only look fine when there's little to synthesize)
   - for the two schools kept on opus (jaimini, bnn full/reverse): one
     contradiction-heavy case if the fixed chart's D1/D9 or Bhava/Arudha
     naturally diverge, to sanity-check the opus tier is still earning its
     cost
2. **Judge each reading on:**
   - **Weighting fidelity** — did the synthesis apply the school's stated
     priority order (e.g. BNN's 10-priority weighting, KP's CSL >
     significator > RP hierarchy) rather than an even blend of unit blocks?
   - **Contradiction handling** — when unit-analyzer outputs disagree (D1 vs
     D9, Bhava vs Arudha, opposing significators), does the synthesis
     surface and resolve the tension instead of silently picking one side or
     smoothing it over?
   - **Honesty caveats** — do the boundary statements survive (lal-kitab
     Phase 0 scope note, 8D no-specific-dates rule, KP's two-Lagnas-never-mixed
     framing, "D9 never read standalone")? These live in orchestrator/
     synthesizer prompt text, not in baseline JSON, so nothing in this
     harness would catch their silent disappearance.
3. **Compare opus vs sonnet/high output side-by-side** for each of the 4
   downgrade-candidate schools on the same golden reading before treating the
   §3 tier change as shipped. Sonnet/high only replaces opus once it matches
   on all three axes above for at least the full-reading and narrow-question
   cases.

Until that eval exists, treat the sonnet/high synthesis tier for the 4
downgraded schools as provisional, and re-run the comparison whenever
`agents/synthesizer.md`'s prompt changes materially.
