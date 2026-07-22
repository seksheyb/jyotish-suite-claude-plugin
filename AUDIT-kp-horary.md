# Audit — `kp-horary` skill (branch `refactor-efficient` vs `main`)

Date: 2026-05-21 · Auditor: automated line-by-line review · **AUDIT ONLY, nothing fixed.**

## Summary

**Verdict: MINOR-TO-MODERATE GAPS.** The refactor is fundamentally sound. The
deterministic methodology in `scripts/compute_kp_horary_baseline.py` + `lib/` is
correct — the 249→Lagna mapping, sub-lord boundaries, cusp rotation, two-Lagna
separation, 4-level significators, Ruling-Planets derivation and Vimshottari
dasha all match the reference files. The refactor even *improved* on `main` by
implementing the RP retrograde-exclusion rule that the old script never did.

No P0 (wrong-output) bugs were found. The gaps are: (1) one broken/stale file
left untouched by the refactor — `commands/kp-horary.md` still tells the model
to run deleted scripts; (2) the baseline JSON omits a few fields the locked
output contracts in `orchestration-notes.md` depend on (planet `house`, chart
Lagna `sign`, combust/sandhi flags); (3) one internal contradiction — the
display format/critical-rule still call for Uranus/Neptune/Pluto that the
refactored ephemeris no longer computes; (4) `baseline-runner.md` advertises a
`--chart` flag the horary script does not accept.

Counts: **Part 1** — 25 items walked: 21 PRESERVED/MOVED clean, 1 CONTRADICTED,
plus 2 stale path references and 1 broken command file. **Part 2** — 22 rules
checked: 14 CORRECT, 0 WRONG, 5 MISSING, 3 APPROXIMATED. **Part 3** — script
runs clean (exit 0, valid JSON); sanity checks all pass; the user-pasted-chart
path is not wired for horary (by design, but mis-documented).

Prioritized: **0 × P0, 6 × P1, 9 × P2.**

---

## Part 1 — Content gaps

Walked `git show main:.../kp-horary/SKILL.md` (258 lines) top to bottom against
the refactor-branch `SKILL.md` + `references/orchestration-notes.md` + the four
reference files (which are **byte-identical** to `main` — `git diff` shows no
change).

| Item (from `main` SKILL.md) | Status | Where it went | Severity |
|---|---|---|---|
| Overview / 8-step pipeline | PRESERVED | SKILL.md intro + `methodology.md` "Eight-step horary read" | — |
| Reference-files table | PRESERVED | SKILL.md "Methodology" table (now also lists `orchestration-notes.md`) | — |
| Computation-scripts table (`compute_horary_chart.py`, `compute_ruling_planets.py`) | MOVED | Consolidated into `scripts/compute_kp_horary_baseline.py`, run by `baseline-runner` (SKILL.md Wave 0) | — |
| Phase 1 intake prompt box | PRESERVED | SKILL.md Phase A box (lines 33–42), reworded but equivalent | — |
| Phase 1 validation rules (number 1-249, vague-question redirect, tz, before-sunrise day-lord) | PRESERVED | SKILL.md "Question intake" (lines 85–94) | — |
| Phase 2 chart computation | MOVED | SKILL.md Wave 0 + `ephemeris.kp_horary_chart()` | — |
| Phase 2 "Critical note" — Lagna from number, not rising sign | PRESERVED / STRENGTHENED | SKILL.md intro + `orchestration-notes.md` "Two Lagnas — never mix them" | — |
| Phase 2 "display the full chart for verification" | STRENGTHENED | `chart-verifier` + explicit "Confirmed" gate (`orchestration-notes.md` Verification Display Format) | — |
| Phase 3 RP computation + calculation box | MOVED | `orchestration-notes.md` Verification Display Format (RP block, lines 163–174); data in baseline `ruling_planets` | — |
| Phase 3 RP strength order + retrograde-exclusion rule | PRESERVED + IMPLEMENTED | `ruling-planets.md` §"strength order" / Step 5; now also enforced in `compute_kp_horary_baseline.py:219–238` | — |
| Phase 4 question-category house-combination table (15 rows) | MOVED + EXPANDED | `HOUSE_COMBINATIONS` dict (`compute_kp_horary_baseline.py:51–72`, 20 entries) + `house-combinations.md` | — |
| Phase 4 "Rule of fructification" | PRESERVED | `house-combinations.md` line 3 + `orchestration-notes.md` per-cusp block | — |
| Phase 5 per-cusp CSL output block | MOVED + EXPANDED | `orchestration-notes.md` lines 21–43 (adds sub-sub-lord + confidence/caveats lines) | — |
| Phase 6 RP cross-check (Strong YES/NO/Mixed) | MOVED | `orchestration-notes.md` "RP cross-check criteria" (lines 45–53) | — |
| Phase 7 Timing via DBA | MOVED | `orchestration-notes.md` "Timing chain" (lines 55–64) | — |
| Phase 8 Verdict template box | MOVED | `orchestration-notes.md` "Phase-8 verdict — output template" (lines 66–96) | — |
| Critical Rule 1 — never override CSL with sentiment | PRESERVED | `orchestration-notes.md` critical rule 1 | — |
| Critical Rule 2 — always show RP calculation | PRESERVED | `orchestration-notes.md` "Output style" + Verification Display Format RP block | — |
| Critical Rule 3 — show degrees + lord chains | PRESERVED | `orchestration-notes.md` critical rule 2 | — |
| Critical Rule 4 — confidence ≠ certainty | PRESERVED | `orchestration-notes.md` critical rule 3 | — |
| Critical Rule 5 — don't combine charts | PRESERVED | `orchestration-notes.md` critical rule 4 + SKILL.md line 94 | — |
| Critical Rule 6 — question framing matters | PRESERVED | `orchestration-notes.md` critical rule 5 | — |
| Critical Rule 7 — outer planets U/N/P shown for reference, not used | **CONTRADICTED** | `orchestration-notes.md` critical rule 6 + Verification Display line 161 still demand U/N/P, but the refactored `ephemeris.ALL_PLANETS` (line 154) computes **only the 9 grahas** — the baseline never emits U/N/P, so the display instruction is unfulfillable | **P2** |
| Critical Rule 8 — retrograde planet gives star-lord's result | PRESERVED | `orchestration-notes.md` critical rule 7 + `methodology.md` "Special rules" | — |
| Output Style (5 bullets) | PRESERVED | `orchestration-notes.md` "Output style" — all 5 carried over | — |

### Stale path / broken-reference findings

| Item | Status | Detail | Severity |
|---|---|---|---|
| `commands/kp-horary.md` lines 15 & 21 | **BROKEN / CONTRADICTED** | Unchanged from `main`. Step 3 says "use the scripts under `skills/kp-horary/scripts/`" and line 21 references `skills/kp-horary/scripts/` for the `swisseph` error hint. That directory **was deleted** in the refactor (`README.md` itself states "there is no per-skill `scripts/` directory"). A model that follows the command file literally will look for non-existent scripts. | **P1** |
| `references/249-table.md` line 14 | STALE PATH | "The skill computes this programmatically in `scripts/compute_horary_chart.py`." That script no longer exists; the logic now lives in `ephemeris.horary_number_to_lagna()`. | **P2** |
| `chart-verifier` input contract | DOC MISMATCH | `chart-verifier.md` Case A expects "a chart JSON already computed by `chart-calculator`." For kp-horary no `chart-calculator` runs — the verifier must render from the **baseline JSON** produced by `baseline-runner`. Works in practice (SKILL.md hands it the Verification Display Format), but the agent's own doc never names this input case. | **P2** |

### SKILL.md path/agent resolution check

All resolve: `${CLAUDE_PLUGIN_ROOT}/scripts/compute_kp_horary_baseline.py` ✓;
`references/{methodology,house-combinations,ruling-planets,249-table,orchestration-notes}.md`
✓; agents `baseline-runner`, `chart-verifier`, `unit-analyzer`, `synthesizer`
✓ (all present in `agents/`). No phase-ordering contradiction between SKILL.md
waves and `methodology.md`'s 8 steps.

---

## Part 2 — Script methodology findings

Audited `scripts/compute_kp_horary_baseline.py`, `lib/ephemeris.py`,
`lib/jyotish_primitives.py`, `lib/chart_io.py` against
`methodology.md`, `ruling-planets.md`, `house-combinations.md`, `249-table.md`.
Reference treated as source of truth.

| Rule | Reference loc | Script loc | Verdict | Note |
|---|---|---|---|---|
| 249-number → Lagna = **mid-point** of segment N | `249-table.md:10`, `methodology.md:7` | `ephemeris.py:140` (`mid = nak_start + cum + arc/2`) | **CORRECT** | Verified: #71 → Pushya, Saturn star, Rahu sub, Lagna 103.889° (Cancer 13°53′). |
| Vimshottari sub-division proportions | `249-table.md:23–34` | `jyotish_primitives.py:45–46` (`VIM_YEARS`), `get_sub_and_subsub:188–220` | **CORRECT** | Rahu sub arc = 2°00′ confirmed in run output (`segment 102.889–104.889`). |
| Star-lord order across zodiac | `249-table.md:36` | `jyotish_primitives.py:32–46` (`NAKSHATRAS`, `VIM_SEQ`) | **CORRECT** | — |
| Cusps anchored to chart Lagna (Placidus rotated) | `methodology.md:13` ("CSL is paramount"); SKILL intro | `ephemeris.py:305–313` (offset rotation, cusp 1 forced to horary Lagna) | **CORRECT** | Matches deleted `main` `compute_horary_chart.py` logic exactly. |
| Two Lagnas — RP from the **real rising sign**, never the 249-number Lagna | `ruling-planets.md:36–39`; `methodology.md:9` | `ephemeris.py:303` (`real_asc`), `compute_kp_horary_baseline.py:193,294,310–311` | **CORRECT** | Baseline keeps `horary_lagna` and `rp_lagna` separate; `two_lagna_note` emitted. |
| RP = 7 factors in strength order | `ruling-planets.md:6–14` | `compute_kp_horary_baseline.py:199–207` | **CORRECT** | Order: Lagna Sub/Star/Sign, Moon Sub/Star/Sign, Day Lord. |
| Retrograde planets excluded from RP unless depositor is RP | `ruling-planets.md:45` | `compute_kp_horary_baseline.py:219–238` | **CORRECT** | Improvement over `main` (old `compute_ruling_planets.py` never excluded). Minor nuance: depositor checked against pre-exclusion `dedup` (line 232), not the surviving `retained` set — order-dependent in the rare retro-depositor-of-retro case. |
| Rahu/Ketu agent rule — node joins RP if in sign of / star of / conjunct an RP planet | `ruling-planets.md:47` | `compute_kp_horary_baseline.py:243–268` | **APPROXIMATED** | All 3 conditions present, but "conjunct" = **same sign** (`line 252–253`), not within-orb. Over-includes nodes (e.g. test run flagged Rahu "conjunct Sun, Mars, Mercury" across a 13° spread). |
| Node "becomes the **strongest** RP" | `ruling-planets.md:47` | `compute_kp_horary_baseline.py:267–268, 280` | **APPROXIMATED / WEAKENED** | Eligible node is appended to the **end** of `final_rp` (weakest slot); `strongest_rp` is hard-set to `factors[0][1]` (Lagna Sub Lord). Note the reference itself is internally inconsistent (its example output, `ruling-planets.md:88`, also calls Lagna Sub Lord strongest) — script follows the example, not the prose. |
| `strongest_rp` = Lagna Sub Lord | `ruling-planets.md:8, 88` | `compute_kp_horary_baseline.py:280` | **APPROXIMATED** | Hard-coded to `factors[0][1]`; if that planet is retrograde-excluded it is still reported as strongest RP (edge case). |
| Day Lord = weekday planet at sunrise; before sunrise → previous day | `ruling-planets.md:18–28` | `ephemeris.day_lord:110–118`, `sunrise_jd:99–107` | **CORRECT** | Verified: 2026-03-10 question → Tuesday at sunrise → Mars. |
| 4-level significators (L1 star-of-occupant, L2 occupant, L3 star-of-lord, L4 lord) | `methodology.md:34–41` | `compute_kp_horary_baseline.py:130–173` | **CORRECT** | All four levels match. Empty-house case handled via L3/L4. |
| Conjunction with Rahu/Ketu adds nodes to a house's significators | `methodology.md:41` | `compute_kp_horary_baseline.py:161–163` | **CORRECT (dead code)** | A node occupying a house is already in `occupants`→`l2`; the explicit loop is a no-op. Result correct; loop redundant. |
| Planet signifies houses = star-lord's owned+occupied, then own owned+occupied | `methodology.md:11` | `compute_kp_horary_baseline.py:176–186` | **CORRECT** | Returns the union set; star>own *ranking* not encoded (left to agent), but the CSL gate only needs membership. |
| `HOUSE_COMBINATIONS` ported from `house-combinations.md` | `house-combinations.md` (all categories) | `compute_kp_horary_baseline.py:51–72` | **MOSTLY CORRECT / 3 APPROXIMATED** | Marriage, new_job, promotion, litigation_own, property_purchase/sale, childbirth, loan_borrowing, investment_return, travel_long, foreign_settlement, health_cure, education_exam, lost_item_recovery, election_appointment, business_launch — all match the reference. **Inferred (reference gives no explicit set):** `job_change_leaving` negative `[2,6,10,11]`; `litigation_opponent` sets; `loan_giving` `[8,11,2]/[6,12]`. Defensible inferences, but not in the reference. |
| Dasha computed at the **moment of the question** (not a natal moment) | `methodology.md:9`; Step 7 | `ephemeris.py:334` (`_vim_dasha(moon, utc)`), `jyotish_primitives.build_dasha_tree:426–472` | **CORRECT** | Question moment is used as the dasha reference; verified balance 2.21 yr from Moon in Anuradha (Saturn). 5 MDs built forward — adequate for timing. |
| Combust planets (within **8.5°** of Sun) lose strength as significators | `methodology.md:66` | — | **MISSING** | Horary baseline never computes combustion. `methodology.md` special rule requires it and the per-cusp block (`orchestration-notes.md:36`) asks for a "combustion" caveat. Latent bug if wired up later: `jyotish_primitives.COMBUSTION_ORBS` (lines 61–62) holds **Parashari** orbs (10–17°), not KP's uniform 8.5°. |
| Chart Lagna at sandhi (within **0°30′** of a sign edge) → warn, unreliable verdict | `methodology.md:68`, `249-table.md:80` | — | **MISSING** | Baseline emits no sandhi flag for the horary Lagna. `jyotish_primitives.sandhi()` (lines 302–309) exists but (a) is never called by the horary script and (b) uses a **1.0°** band, not the reference's 0°30′. |
| Mrityu Bhaga / Pushkara / Gandanta degree flags | `methodology.md:70` | — | **MISSING** | Not emitted. Reference itself rates them "secondary to CSL verdict", so low impact. |
| Planet `house` number in baseline | `orchestration-notes.md:156` (display "9 PLANETS" table has a House column); per-cusp block "Occupies house" `:30` | — | **MISSING** | `full_lord_chain()` (`jyotish_primitives.py:228–245`) emits no `house`; `ephemeris.kp_horary_chart` (lines 315–321) does not add one. Recoverable by inverting `significators[h].occupants`, but the display contract names the field with no direct source and `chart-verifier` is spec'd "no computation." |
| Chart Lagna `sign` field | `orchestration-notes.md:143` (display: "CHART LAGNA … [Sign] [Deg]…") | — | **MISSING** | `horary_lagna` dict (`ephemeris.py:141–145`) has `lagna_deg` but no `sign`/`dms`. Recoverable from `cusps[0]` (which has `sign` + `longitude_dms`). |
| `compute_kp_horary_baseline.py` accepts `--chart` (user-pasted chart) | `baseline-runner.md:21–23` | `compute_kp_horary_baseline.py:369–380` (argparse) | **MISSING** | The script has **no `--chart` argument** — only `--number/--datetime/--tz/--lat/--lon/--question`. `baseline-runner.md` claims every `compute_<school>_baseline.py` takes `--chart`. For horary this is false (and arguably N/A — a horary chart is always built from the number + moment — but the agent doc is still wrong). |
| `_csl_verdict` `primary` parameter | — | `compute_kp_horary_baseline.py:109` | **COSMETIC** | `primary` is accepted but never read; `csl_generic_gate` (line 334) passes `[h]` into it pointlessly. Output unaffected — dead parameter. |

No **WRONG** verdicts: every value the script *does* compute is methodologically
correct. All five gaps are MISSING capabilities; all three APPROXIMATED items
are RP-edge nuances, not normal-path errors.

### Baseline-JSON field coverage vs. consumer contracts

Baseline emits: `input, ayanamsa, house_system, two_lagna_note, horary_lagna,
rp_lagna, cusps, planets, ruling_planets, significators, planet_significations,
csl_generic_gate, fruitful_barren_houses, dasha, house_combinations`.

- `chart-verifier` Verification Display Format — **mostly covered**; missing:
  per-planet `house` column source, chart-Lagna `sign` (both recoverable), and
  Uranus/Neptune/Pluto rows the format still calls for (not computed at all).
- `unit-analyzer` per-cusp block — covered: `cusps[].sub_lord/sub_sub_lord`,
  `planet_significations`, `significators`, `house_combinations`. "Owns houses /
  Occupies house" are not pre-broken-out but are derivable from `significators`.
- `synthesizer` Phase-8 verdict — `dasha.running` quartet + `ruling_planets` +
  per-cusp blocks cover it. ✓

---

## Part 3 — Run results

### Test 1 — computed horary chart (exit 0, valid JSON)

```
python3 plugins/jyotish-suite/scripts/compute_kp_horary_baseline.py \
  --number 71 --datetime "2026-03-10T15:45:00" --tz "Asia/Kolkata" \
  --lat 19.07 --lon 72.87 --question "test"
```
**EXIT=0**, stderr empty, JSON parses. Top-level keys all present (15 keys).

### Test 2 — user-pasted-chart path

`lib/chart_io.py --mode kp --positions <file> --out <chart>` → **EXIT=0**,
wrote a valid `kp_natal` chart. **However:**
`compute_kp_horary_baseline.py --chart <chart>` → **argparse error** ("the
following arguments are required: --number, --datetime, --tz, --lat, --lon").
The horary baseline has **no `--chart` ingestion path**, and `chart_io.py` has
**no `kp-horary` mode** (only `parashari`/`kp`). For horary this is defensible
(the chart is always derived from the number + question moment), but it
contradicts `baseline-runner.md`'s generic `--chart` claim.

### Sanity checks (all PASS)

| Check | Hand reasoning | Script output | OK |
|---|---|---|---|
| Horary #71 segment | #64 = Pushya 1st sub; 71 = 8th sub; Saturn-sequence 8th lord = Rahu | nakshatra Pushya, star Saturn, sub Rahu | ✓ |
| Chart Lagna sign | Pushya spans 93.3–106.7° → all in Cancer | 103.889° → Cancer (cusp 1) | ✓ |
| Day Lord | 2026-03-10 = Tuesday; question 15:45 IST is after sunrise (06:51 IST) | Tuesday → Mars | ✓ |
| Moon nakshatra | Moon 225°07′ → Anuradha (213.3–226.7°), star Saturn | Anuradha, star Saturn | ✓ |
| Starting Mahadasha / balance | Moon in Saturn's star → MD Saturn; fraction 0.883 → 19×0.117 ≈ 2.22 yr | MD Saturn, balance 2.214 yr | ✓ |
| RP retrograde exclusion | Jupiter retro, in Gemini → depositor Mercury, not RP → exclude | "retrograde — EXCLUDED (depositor Mercury not RP)" | ✓ |
| H7 significators L3 | planets in Saturn's star = Moon, Saturn, Venus | L3 = [Moon, Saturn, Venus] | ✓ |

---

## Prioritized fix list

### P0 — wrong output
None.

### P1 — broken / missing capability

1. **`commands/kp-horary.md` points to deleted scripts.** Lines 15 & 21
   reference `skills/kp-horary/scripts/` which no longer exists. *Fix:* rewrite
   step 3 to "run `${CLAUDE_PLUGIN_ROOT}/scripts/compute_kp_horary_baseline.py`
   via the `baseline-runner` agent" and update the `swisseph` error hint path.

2. **Planet `house` number absent from the baseline.** The Verification
   Display "9 PLANETS" table and the per-cusp "Occupies house" line both need
   it. *Fix:* in `ephemeris.kp_horary_chart` (after line 320) add
   `chain["house"] = jp.house_of(jp.get_sign(lon)[0], chart_lagna_sign_idx)`
   for each planet, measured from the chart (horary) Lagna sign.

3. **Combustion not computed for horary.** `methodology.md:66` mandates an
   8.5°-orb combustion check; the per-cusp caveat line expects it. *Fix:* add a
   KP-specific combustion pass to `compute_kp_horary_baseline.py` using a
   uniform 8.5° orb (do **not** reuse `jyotish_primitives.COMBUSTION_ORBS` —
   those are Parashari 10–17° orbs and would be wrong for KP).

4. **Chart-Lagna sandhi flag missing.** `methodology.md:68` + `249-table.md:80`
   require warning when the horary Lagna sits within 0°30′ of a sign edge.
   *Fix:* compute a sandhi flag on `horary_lagna` using a 0.5° band (not
   `jyotish_primitives.sandhi()`'s 1.0° band).

5. **Uranus/Neptune/Pluto contradiction.** `orchestration-notes.md` critical
   rule 6 + Verification Display line 161 require U/N/P "for reference", but
   `ephemeris.ALL_PLANETS` computes only 9 grahas. *Fix:* either drop the U/N/P
   lines from `orchestration-notes.md` (recommended — SKILL.md already says "9
   planets"), or re-add U/N/P to the horary planet block.

6. **`baseline-runner.md` over-claims `--chart`.** Lines 21–23 say every
   `compute_<school>_baseline.py` accepts `--chart`; the horary script does not.
   *Fix:* note in `baseline-runner.md` that `kp_horary` takes only
   `--number/--datetime/--tz/--lat/--lon/--question` (no pasted-chart path).

### P2 — cosmetic / low-impact

7. **Stale path in `249-table.md:14`** — references the deleted
   `scripts/compute_horary_chart.py`. *Fix:* change to
   `ephemeris.horary_number_to_lagna()` / the consolidated baseline script.

8. **Chart-Lagna `sign` not in `horary_lagna`.** *Fix:* add `sign` +
   `longitude_dms` to the dict returned by `ephemeris.horary_number_to_lagna`
   (lines 141–145) so `chart-verifier` need not derive it from `cusps[0]`.

9. **Rahu/Ketu "conjunct" = same sign, not within-orb**
   (`compute_kp_horary_baseline.py:252–253`). *Fix:* tighten to a degree-orb
   test (e.g. ≤ ~8–10°) to match the reference's "conjunct".

10. **`strongest_rp` hard-coded to Lagna Sub Lord**
    (`compute_kp_horary_baseline.py:280`) — wrong if that planet was
    retrograde-excluded. *Fix:* derive `strongest_rp` from `final_rp_set`
    (first surviving factor).

11. **Node never promoted to "strongest RP"** despite `ruling-planets.md:47`.
    Low priority — the reference's own example contradicts its prose; document
    the chosen interpretation rather than changing behaviour.

12. **Retrograde-depositor check uses pre-exclusion `dedup`**
    (`compute_kp_horary_baseline.py:232`) — order-dependent in the rare
    retro-planet-deposited-by-another-retro-planet case. *Fix:* iterate
    exclusion to a fixed point, or check against the surviving set.

13. **Dead `primary` parameter in `_csl_verdict`**
    (`compute_kp_horary_baseline.py:109`, called at line 334). *Fix:* remove
    the unused parameter.

14. **Dead node-conjunction loop** in `compute_significators`
    (`compute_kp_horary_baseline.py:161–163`) — a node that occupies a house is
    already in `occupants`. Harmless; remove for clarity.

15. **`chart-verifier.md` input contract** doesn't name the "render from the
    baseline JSON" case used by kp-horary. *Fix:* add a Case-C note that for
    horary the verifier renders directly from `baseline-runner`'s output.

---

*End of audit. No files other than this report were created or modified; git
was not touched.*
