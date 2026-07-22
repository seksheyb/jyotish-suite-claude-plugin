# Golden-chart regression harness

Blueprint Phase 5 (`OPTIMIZATION-BLUEPRINT.md` §8). This guards one thing:
**edits to `lib/` or `scripts/compute_*_baseline.py` can't silently shift the
numbers a synthesizer will read as ground truth.** It says nothing about
reading quality — see "Synthesis-quality eval" below for that gap.

## What's here

```
tests/
  golden/            one fully-pinned input per school (JSON: script + CLI args)
    chart_io/          hand-authored pasted-chart positions fixtures (see below)
  snapshots/         the expected baseline JSON per school, checked in
                      (both the ephemeris-path and, where applicable, the
                      <school>_chart.json pasted-chart-path snapshot)
  run_golden.py       regenerates every baseline via BOTH entry points, diffs
                      against snapshots
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

## Pasted-chart coverage (`lib/chart_io.py`)

Each `compute_<school>_baseline.py` accepts a chart two ways: the ephemeris
entry point (`--datetime/--tz/--lat/--lon`) covered above, or a **pasted
chart** — a user-supplied positions JSON expanded by `lib/chart_io.py` into
the same chart shape, then fed to the baseline via `--chart <file>`. The
`assemble_parashari`/`assemble_kp` code that both paths converge on is
shared, but the expansion in `lib/chart_io.py` (nakshatra, navamsa, dignity,
lord chains, dasha-from-birth-block) is its own surface and can regress
independently of the ephemeris path.

Every school whose baseline has a `--chart` flag now gets a second golden
fixture for it:

| School      | Positions fixture                              | Notes |
| ----------- | ----------------------------------------------- | ----- |
| `vedic`     | `golden/chart_io/parashari_positions.json`      | `--mode parashari`; `--asof` still pinned |
| `bnn`       | `golden/chart_io/parashari_positions.json`      | `--mode parashari`; no extra args (no clock dependency) |
| `jaimini`   | `golden/chart_io/parashari_positions.json`      | `--mode parashari`; `--target-date` still pinned |
| `kp_natal`  | `golden/chart_io/kp_natal_positions.json`       | `--mode kp`; `--rp-datetime` still pinned |
| `lalkitab`  | `golden/chart_io/parashari_positions.json`      | `--mode parashari`; `--age` still pinned |
| `kp_horary` | **none — ephemeris-only, see below**            | — |

The four parashari-mode fixtures (vedic, bnn, jaimini, lalkitab) all reuse
`golden/chart_io/parashari_positions.json` — the same pinned birth chart
(1990-05-15T10:30:00, Asia/Kolkata, lat 28.6139, lon 77.2090) hand-transcribed
as sign+degree-in-sign for the Lagna and all 9 planets, with a `birth` block
so Vimshottari dasha still resolves from real birth data rather than being
marked unavailable. `kp_natal` gets its own `golden/chart_io/kp_natal_positions.json`
because KP houses are Placidus cusps (not signs) and use the KP ayanamsa
(not Lahiri) — its Lagna/planet degrees are a few arcminutes off the parashari
fixture's for that reason, not by mistake.

Each `golden/<school>.json` carries this as an optional `"chart_path"` block
(`mode`, `positions`, `args`) alongside the existing `"args"` block for the
ephemeris path; `run_golden.py` expands the fixture through `lib/chart_io.py`,
runs the baseline against the result with `--chart`, and snapshots it
separately as `snapshots/<school>_chart.json`. A clean run now shows two rows
per school:

```
School       Path       Status
--------------------------------------------------
vedic        ephemeris  PASS
vedic        chart      PASS
...
kp_horary    ephemeris  PASS
kp_horary    chart      N/A
    no pasted-chart path for this school (ephemeris-only)
--------------------------------------------------
11/11 PASS, 0 FAIL (1 N/A — ephemeris-only school)
```

**`kp_horary` has no pasted-chart path and is not given a `chart_path` block.**
`compute_kp_horary_baseline.py` has no `--chart` flag at all — a horary chart's
Lagna is always derived from the querent's 1-249 number (rotated Placidus
cusps), never from a pre-computed chart a user could paste in. That's a
structural property of horary astrology, not a coverage gap, so it's recorded
as an `N/A` row rather than forced.

Expect small, well-understood diffs between a school's ephemeris-path and
chart-path snapshot: the pasted-chart path can't know the true ayanamsa
*value* (only its mode), so `ayanamsa.mode` reads `"user-supplied"` instead of
`"lahiri"`/`"kp"` and `ayanamsa.value_dms` is absent. `jaimini`'s baseline
never reads the ayanamsa block at all, so its two snapshots are byte-identical.
Everything else — signs, houses, nakshatras, dignities, dasha, and every
school-specific unit-analyzer field — must match between the two paths for
the same underlying chart.

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
School       Path       Status
--------------------------------------------------
vedic        ephemeris  PASS
vedic        chart      PASS
bnn          ephemeris  PASS
bnn          chart      PASS
jaimini      ephemeris  PASS
jaimini      chart      PASS
kp_natal     ephemeris  PASS
kp_natal     chart      PASS
kp_horary    ephemeris  PASS
kp_horary    chart      N/A
    no pasted-chart path for this school (ephemeris-only)
lalkitab     ephemeris  PASS
lalkitab     chart      PASS
--------------------------------------------------
11/11 PASS, 0 FAIL (1 N/A — ephemeris-only school)
```

A `FAIL` row prints a unified diff preview (first ~15 lines) against the
snapshot and the script's stderr if it crashed outright. If a script fails to
run at all (import error, missing dependency, argparse mismatch), that's
recorded as `FAIL: runtime error: <stderr>` rather than silently skipped —
treat that as a P0, not a snapshot problem. `kp_horary`'s chart row is always
`N/A`, never `PASS`/`FAIL` — see "Pasted-chart coverage" above.

## What this does NOT guard

- **Reading quality.** A baseline can be numerically identical and still feed
  a worse synthesis if the synthesizer prompt, model, or effort earmark
  regresses. That's the gate below.
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
