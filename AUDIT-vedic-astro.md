# Audit — `vedic-astro` skill (branch `refactor-efficient` vs `main`)

Audit only. No fixes applied. Reference files are treated as source of truth;
where two reference files disagree, that is flagged for human resolution.

## Summary

**Verdict: serious gaps.** The SKILL.md → orchestration-notes content split is
clean — no interpretive content was lost in the prose refactor. But the
deterministic sidecar (`compute_vedic_baseline.py`) is materially incomplete
for the methodology it is supposed to own:

- **P0 (1):** the baseline's `dasha` field is the quartet running *at birth*,
  not as-of the reading date, and the dasha tree is discarded — methodology
  Step 0 "Current Dasha" and Step 4 "Dasha Timing" cannot be performed.
- **P1 (5):** Planetary War never computed; no D9 block (Step 3 un-runnable);
  Pushkara Navamsa table contradicts the methodology-cited reference;
  methodology.md still carries D9-conditional gates that contradict
  orchestration-notes.md; user-supplied dasha passthrough is dropped.
- **P2 (10):** ordinal label bug, two reference-vs-reference table conflicts,
  missing Gana/Neecha-Bhanga/mutual-aspect convenience fields, stale command
  file + frontmatter, undocumented Ashtakavarga spec, dasha field naming.

Counts — Part 1: 23 items walked, 0 LOST, 3 intentional CONTRADICTED, 3 new
stale/contradiction defects. Part 2: 30 rules checked — 17 CORRECT, 3 WRONG,
6 MISSING, 4 APPROXIMATED. Part 3: both run paths exit 0 with valid JSON, SAV
337 invariant holds, all 6 sanity checks pass.

---

## Part 1 — Content gaps (main SKILL.md vs refactor branch)

`main` reference files are byte-identical to the refactor branch *except*
`orchestration-notes.md` (new) and `SKILL.md` (rewritten). `methodology.md`,
`chart-tables.md`, `degree-flags.md`, `nakshatra-table.md`,
`navamsa-table.md`, `functional-roles.md` — unchanged.

| Item (main SKILL.md) | Status | Where it went | Severity |
|---|---|---|---|
| Frontmatter description | PRESERVED | SKILL.md:2-10 — updated to add "or birth data to compute one" | — |
| Overview / 4-step workflow | PRESERVED | Re-expressed as "Orchestration" SKILL.md:18-72 | — |
| Reference-files load table | PRESERVED+expanded | SKILL.md:90-98 — added `chart-tables.md`, `orchestration-notes.md` | — |
| PHASE 1 chart-collection prompt box | MOVED | orchestration-notes.md:74-96 "Chart Intake Format" | — |
| PHASE 1 "D9 not provided → ask before proceeding" | CONTRADICTED (intentional) | orchestration-notes.md:33-49 — D9 now always derived, "never ask" | see contradiction A |
| PHASE 1 "skip D9 → suppress Pada Lord + all D9 steps" | CONTRADICTED (intentional) | orchestration-notes.md:42-44 — workers always run full D9 layer | see contradiction A |
| PHASE 1 "Dasha from DOB via Moon Nakshatra" | PRESERVED | Moved to script (`ephemeris._vim_dasha`) | — |
| PHASE 2 verification display box | MOVED (abbreviated) | orchestration-notes.md:130-167 — full ASCII tables compressed to descriptions | P2 |
| PHASE 2 flag legend (Ex/Db/Own/MT/Cb/Gd/MB/PK/Sd/Vo/PW) | PRESERVED verbatim | orchestration-notes.md:150-152 | — (but `[PW]` is unfulfillable — see Part 2) |
| PHASE 2 "do not proceed until confirmed" gate | PRESERVED | orchestration-notes.md:169; SKILL.md:48-50; conduct rule 1 | — |
| PHASE 3 question-intake prompt box | MOVED | orchestration-notes.md:104-126 "Question Intake Prompt" | — |
| PHASE 3 question-classification table (6 rows) | MOVED verbatim | orchestration-notes.md:14-21 | — |
| PHASE 3 "state classification in one line" + quote | PRESERVED | orchestration-notes.md:23-26; SKILL.md:75 | — |
| PHASE 4 "load methodology, execute Steps 0-6" | PRESERVED | SKILL.md Waves 1-2 + `methodology.md` (unchanged) | — |
| Conduct rule 1 — never skip verification | PRESERVED | orchestration-notes.md:55-56 | — |
| Conduct rule 2 — never skip question intake | PRESERVED | orchestration-notes.md:57 | — |
| Conduct rule 3 — always cite degrees/Nakshatras | PRESERVED | orchestration-notes.md:58-59 | — |
| Conduct rule 4 — load reference tables, never guess | PRESERVED (re-expressed) | orchestration-notes.md:60-62 "Trust the baseline" | — |
| Conduct rule 5 — distinguish D1 from D9 | PRESERVED | orchestration-notes.md:63 | — |
| Conduct rule 6 — D9/Pada-Lord suppression gate | CONTRADICTED (intentional) | Removed; orchestration-notes.md:33-49 inverts it | see contradiction A |
| Conduct rule 7a — flag missing data | PRESERVED | orchestration-notes.md:64-65 | — |
| Conduct rule 7b — tone (warm/precise/no fatalism) | PRESERVED | orchestration-notes.md:66-67 | — |
| Conduct rule 8 — cross-check (JHora / Astro-Seek) | PRESERVED | orchestration-notes.md:68-70 | — |

No interpretive content was outright LOST. The main SKILL.md's double-numbered
conduct rules (two "7"s) are cleanly renumbered 1-8 in orchestration-notes.md.

### New contradictions the refactor introduced

- **Contradiction A (P1) — `methodology.md` vs `orchestration-notes.md` on
  D9/Pada-Lord conditionality.** `methodology.md` was NOT updated and still
  says Pada Lord is conditional: line 67 "*(only if D9 chart is provided)* …
  If D9 is not provided, skip Pada Lord entirely", line 81 "*(Pada Lord only
  if D9 is provided…)*", line 209 "*(Pada Lord only if D9 provided)*".
  `orchestration-notes.md:42-44` says the opposite — D9 is always derived and
  "The `unit-analyzer` workers always run the full D9 layer". A `unit-analyzer`
  loads **both** files (SKILL.md:62-63) and gets conflicting instructions.
- **Contradiction B (P2) — SKILL.md frontmatter.** SKILL.md:5 still says the
  skill "accepts a pre-computed Vedic birth chart (D1 + D9)", implying the user
  supplies D9, while orchestration-notes.md:33-49 says D9 is always derived and
  must never be asked for.
- **Contradiction C (P2) — `commands/vedic-astro.md` is stale.** Unchanged from
  `main`. Line 2 "on a pre-computed D1 + D9", lines 10-11 "If the user has not
  yet provided a pre-computed D1 + D9 chart … ask them" — contradicts the new
  "birth data OR chart, D9 derived" intake flow.

### Path / agent resolution

All `${CLAUDE_PLUGIN_ROOT}` paths and agent names in SKILL.md resolve:
`lib/ephemeris.py`, `lib/chart_io.py`, `scripts/compute_vedic_baseline.py`,
agents `chart-calculator` / `chart-verifier` / `baseline-runner` /
`unit-analyzer` / `synthesizer`, and all 7 `references/*.md` files exist. ✓

---

## Part 2 — Script methodology findings

`compute_vedic_baseline.py` + `lib/jyotish_primitives.py` + `lib/ephemeris.py`
+ `lib/chart_io.py` vs the reference files.

| Rule | Reference loc | Script loc | Verdict | Note |
|---|---|---|---|---|
| 27 Nakshatras + star lords | nakshatra-table.md:7-33 | jyotish_primitives.py:32-42 | CORRECT | — |
| Pada calculation | nakshatra-table.md:37-45 | jyotish_primitives.py:181-185 | CORRECT | — |
| Navamsa start-by-element + mapping | navamsa-table.md:9-29 | jyotish_primitives.py:58, 271-277 | CORRECT | Fire→Aries, Earth→Cap, Air→Libra, Water→Cancer |
| Vargottama (D1 sign == D9 sign) | navamsa-table.md:32-38 | jyotish_primitives.py:280-283 | CORRECT | — |
| Dignity — exalt/own/MT/debil | chart-tables.md:135-146 | jyotish_primitives.py:104-118, 385-410 | CORRECT | all 7 planets verified cell-by-cell |
| Natural friend/enemy | (none) | jyotish_primitives.py:120-137 | CORRECT | classical naisargika set is right, but **no reference file documents it** |
| Mrityu Bhaga degrees | degree-flags.md:9-18 | jyotish_primitives.py:70-79 | CORRECT | matches degree-flags.md exactly (incl. Lagna row) |
| Pushkara Bhaga degrees | degree-flags.md:49-62 | jyotish_primitives.py:82-85 | CORRECT | matches degree-flags.md exactly |
| **Pushkara Navamsa zones** | degree-flags.md:28-41 (methodology.md:21 cites this file) | jyotish_primitives.py:88-101 | **WRONG** | Script matches `chart-tables.md:84-97`, NOT the methodology-cited `degree-flags.md:28-41`. The two reference files contain entirely different tables. `degree-flags.md`'s table is itself internally garbled (Taurus row, line 31). Needs human resolution. |
| Gandanta zones (water→fire) | degree-flags.md:69-76; methodology.md:19 | jyotish_primitives.py:290-299 | CORRECT | last/first 3°20' of Can/Sco/Pis ↔ Leo/Sag/Ari |
| Sandhi (0-1° / 29-30°) | degree-flags.md:84-89; methodology.md:23 | jyotish_primitives.py:302-309 | CORRECT | — |
| Combustion orbs (+ retro variants) | chart-tables.md:99-108; methodology.md:16 | jyotish_primitives.py:61-63 | CORRECT | Moon12/Mars17/Mer14(12R)/Jup11/Ven10(8R)/Sat15 |
| **Planetary War (Graha Yuddha)** | degree-flags.md:96-108; methodology.md:23 (Step-0 scan); legend `[PW]` | `jp.planetary_war` exists (jyotish_primitives.py:346-363) but is **never called** by `compute_vedic_baseline.py` | **MISSING** | `degree_flags()` (jyotish_primitives.py:366-378) omits war; `build_baseline` never calls `planetary_war`. Baseline JSON has no PW field. Verification-display `[PW]` flag can never populate. Workers told not to recompute → PW lost from every reading. |
| Functional roles by Lagna | chart-tables.md:119-133 | compute_vedic_baseline.py:35-48 | CORRECT | all 12 lagnas verified vs chart-tables.md summary |
| Vimshottari years + sequence | chart-tables.md:47-60; methodology.md:179-181 | jyotish_primitives.py:44-46 | CORRECT | sum 120 ✓ |
| Vimshottari balance / dasha-tree math | methodology.md:17, 179-181 | jyotish_primitives.py:417-472 | CORRECT | MD→BD→AD→SD proportional math correct |
| **Running dasha — as-of date** | methodology.md:17 "Current Dasha/Antardasha/Pratyantar"; Step 4 | ephemeris.py:274-275 / chart_io.py:65-76 pass **birth utc** to `_vim_dasha`; `find_running` resolves at birth | **WRONG** | The emitted `dasha` quartet is the dasha running *at the moment of birth*, not at the reading date. Test nativity (born 1988) → baseline `dasha` periods are all 1981-1988. No `--asof`/current-date input exists anywhere in the pipeline. |
| Dasha tree / MD sequence in baseline | methodology.md Step 4 (needs MD+AD lords, upcoming changes) | compute_vedic_baseline.py:315 `"dasha": chart.get("dasha",{}).get("running")` | **MISSING** | `_vim_dasha` computes `tree`, `mahadasha_sequence`, `starting_mahadasha`, `balance_years` (ephemeris.py:170-178) but `build_baseline` keeps only `running` and discards the rest. Step 4 timing cannot be done. |
| Chara Karakas (AK, AmK) | methodology.md:13 | compute_vedic_baseline.py:172-191 | CORRECT | 7-karaka scheme (Sun..Saturn by deg-in-sign); AK/AmK correct |
| Parashari graha-drishti (7th + Mars 4/8, Jup 5/9, Sat 3/10) | chart-tables.md:110-117; methodology.md:88-92 | jyotish_primitives.py:140; compute_vedic_baseline.py:206-235 | CORRECT | special-aspect distances correct; orb bands tight<3/mod≤7/loose correct |
| Aspect ordinal label | (cosmetic) | compute_vedic_baseline.py:232 `f"{dist}th"` | WRONG (cosmetic) | Saturn's 3rd aspect renders as `"3th"` (confirmed in run output) |
| Rahu/Ketu 5th & 9th aspects | chart-tables.md:116 + methodology.md:93 (both mark "school-dependent / apply if following") | jyotish_primitives.py:140 `SPECIAL_ASPECTS` omits nodes | APPROXIMATED | Script gives nodes the universal 7th only — defensible since reference marks 5/9 optional; flag as a deliberate convention choice |
| Ashtakavarga (BAV per planet, SAV per sign) | (no reference file documents the BAV contribution tables) | compute_vedic_baseline.py:64-164 | CORRECT | SAV total = 337 classical invariant holds in run output; methodology.md:111-113 only gives the score *thresholds*, not the tables |
| **D9 chart block** (D9 lagna, D9 houses, D9 degrees/dignity, D9 aspects) | methodology.md:141-158 (Step 3 = full Step 2 a-f within D9) | `assemble_parashari` builds `chart["d9"]` (ephemeris.py:224-225) but `build_baseline` reads `chart["d1"]` only and emits only per-planet `navamsa_sign` | **MISSING** | No D9 Lagna and no D9 house numbers in the baseline → Step 3's house-relative D9 analysis (house lord, aspects on D9 house, D9 planet-to-planet) is un-runnable. orchestration-notes.md:42 promises workers "always run the full D9 layer" but the data isn't there. |
| Gana (Deva/Manushya/Rakshasa) | methodology.md:68-71 (Step 2b); chart-tables.md:5-32 | not emitted | MISSING | Deterministic; worker can look it up from the nakshatra name, but baseline should carry it per conduct rule 4 |
| Neecha Bhanga (debilitation cancellation) | methodology.md:74 | not computed | MISSING | Derivable by worker from baseline houses/dignities; not pre-flagged |
| Rahu/Ketu dignity | chart-tables.md:145-146 (defines node exalt/debil) | jyotish_primitives.py:389 returns `"n/a"` for nodes | APPROXIMATED | Script ignores the node-dignity rows chart-tables.md supplies — defensible but contradicts that reference |
| Mutual-aspect flag | methodology.md:24-26 (Step 0 "flag mutual aspects"), Step 2f | aspect_map lists one-way only | APPROXIMATED | Worker can cross-reference, but Step 0 explicitly asks for pre-flagging |
| User-supplied dasha passthrough | chart_io.py:73 returns `{"source":"user-supplied", **dasha}` | compute_vedic_baseline.py:315 extracts `.get("running")` | WRONG | A pasted-chart user-stated dasha is silently dropped (no `running` subkey) → baseline `dasha` = null |

### Cross-reference: baseline fields vs what consumers expect

`unit-analyzer.md` and `synthesizer.md` say workers consume the baseline as
ground truth and must NOT recompute. The baseline supplies: lagna, functional
roles, per-planet (sign/deg/nakshatra/pada/star-lord/dignity/navamsa-sign/
vargottama/degree-flags/combust), chara karakas, D1 aspect map, ashtakavarga.
It does **not** supply, despite the methodology requiring them: current dasha
+ tree (Step 0/4), Planetary War (Step 0), the D9 chart for Step 3, Gana
(Step 2b). These four are the load-bearing gaps.

Minor: baseline `dasha` uses keys `bd_lord`/`ad_lord`/`sd_lord` while
methodology.md Step 4 speaks of "Antardasha"/"Pratyantar" — the synthesizer
must map `bd`→Antardasha, `ad`→Pratyantar (naming mismatch, P2). The
`dignity()` docstring (jyotish_primitives.py:387-388) advertises
`great_friend`/`great_enemy` but the function never produces them (P2).

---

## Part 3 — Run results

**Test A — birth-data path.** `compute_vedic_baseline.py --datetime
"1988-02-14T09:30:00" --tz "Asia/Kolkata" --lat 19.07 --lon 72.87` →
**exit 0**, valid JSON, all 12 top-level keys present. No stderr.

**Test B — pasted-chart path.** Built `/tmp/vedic_positions.json` (9 planets +
lagna + birth block) → `chart_io.py --mode parashari` → **exit 0**, wrote
`/tmp/vedic_chart.json` → `compute_vedic_baseline.py --chart …` → **exit 0**,
valid JSON. No crash on either step.

**Sanity checks (Test A):**

| Check | Output | Hand reasoning | Verdict |
|---|---|---|---|
| Lagna | Pisces 14°20'50" (Uttara Bhadrapada) | ~9:30 AM mid-Feb Mumbai, ~1 sign past sunrise lagna — plausible | ✓ |
| Sun nakshatra/pada | Aquarius 0.98° → Dhanishtha pada 3, star-lord Mars | Aqu 0.98°=300.98°; Dhanishtha 293.33-306.67, lord Mars; (300.98-293.33)/3.33=pada 3 | ✓ |
| Moon dasha origin | MD Ketu (Moon in Mula, star-lord Ketu) | Vimshottari MD = Moon's star-lord = Ketu | ✓ |
| Venus dignity | exalted (Venus in Pisces) | Venus exaltation sign = Pisces | ✓ |
| Jupiter vargottama | true (Aries 1.81°, D9 Aries) | Fire sign → D9 starts Aries; nav 0 → Aries == D1 Aries | ✓ |
| SAV invariant | sav_total = 337 | classical Parashari SAV total = 337 | ✓ |

**Notable run observation (confirms P0):** baseline `dasha` block =
`Ketu / Mercury / Venus / Rahu` with all four period ranges inside 1981-1988 —
i.e. the dasha the native was *born into*, not any present-day period.

---

## Prioritized fix list

### P0 — wrong output

1. **Dasha is frozen at birth; tree discarded.** `ephemeris.py:274-275` and
   `chart_io.py:65-76` pass the *birth* datetime to `_vim_dasha`, and
   `compute_vedic_baseline.py:315` keeps only `running`. Methodology Step 0
   ("Current Dasha/Antardasha/Pratyantar") and Step 4 ("Dasha Timing") — and
   the synthesizer's #1 weighting factor "Dasha activation" — operate on the
   wrong period.
   *Fix:* add an `--asof` arg to `compute_vedic_baseline.py` (default = today);
   resolve `find_running` at the as-of date; emit the current MD/AD/PD/SD
   **and** the `mahadasha_sequence` (plus the next dasha change) in the
   baseline `dasha` block. Keep the birth-balance separately if wanted.

### P1 — missing capability / contradiction

2. **Planetary War never computed.** Add a `jp.planetary_war(positions)` call
   in `build_baseline` (the function already exists, jyotish_primitives.py:
   346-363) and surface a per-planet `degree_flags.planetary_war` (winner/
   loser/separation). Without it the `[PW]` legend entry and methodology Step 0
   PW scan are dead.

3. **No D9 block in the baseline.** `build_baseline` (compute_vedic_baseline.py
   :276-321) ignores `chart["d9"]`. Emit a `d9` block: D9 Lagna sign (already
   computed at ephemeris.py:224), each planet's D9 house (count from D9 lagna),
   D9 dignity, and ideally a D9 aspect map — so methodology Step 3 (a-f) is
   runnable.

4. **Pushkara Navamsa table conflict.** `jyotish_primitives.py:88-101` matches
   `chart-tables.md:84-97` but **not** `degree-flags.md:28-41`, which
   methodology.md:21 designates as the authoritative degree-flag file — and
   degree-flags.md's own table is internally garbled (Taurus row). Resolve
   which table is classically correct, fix `degree-flags.md`, then align the
   script constant to it.

5. **methodology.md D9/Pada-Lord gates contradict orchestration-notes.md.**
   Remove the "only if D9 chart is provided / skip Pada Lord" conditionals at
   methodology.md:67, :81, :209 (Step 2b, 2c, Step 6 #8) so it agrees with
   orchestration-notes.md:33-49 (D9 always derived).

6. **User-supplied dasha passthrough dropped.** `compute_vedic_baseline.py:315`
   does `.get("running")`, which is null for the `{"source":"user-supplied",…}`
   shape chart_io.py:73 produces. Handle the passthrough shape (or normalise it
   into a `running` quartet) so a pasted chart with a stated dasha isn't lost.

### P2 — cosmetic / consistency

7. **`"3th"` ordinal.** compute_vedic_baseline.py:232 — `f"{dist}th"` →
   produce "3rd" (and general ordinal handling) for Saturn's 3rd aspect.

8. **Mrityu Bhaga reference conflict.** `chart-tables.md:62-76` has a sparse MB
   table that contradicts the full table in `degree-flags.md:9-18` (which the
   script correctly uses). Delete or reconcile the chart-tables.md copy so
   there is one MB spec.

9. **Gana not in the baseline.** Add `gana` per planet (deterministic from the
   nakshatra; methodology Step 2b needs it).

10. **Rahu/Ketu dignity.** Script returns `"n/a"` (jyotish_primitives.py:389)
    though `chart-tables.md:145-146` defines node exaltation/debilitation.
    Either honor the reference or annotate the deliberate omission.

11. **Mutual aspects not pre-flagged.** Step 0 asks to "flag mutual aspects";
    add a `mutual: true` marker in `aspect_map` where A↔B both aspect.

12. **Stale frontmatter + command file.** SKILL.md:5 "(D1 + D9)" implies the
    user supplies D9; `commands/vedic-astro.md` (unchanged from main) still
    says "pre-computed D1 + D9 chart … ask them". Update both to the
    birth-data-OR-chart, D9-derived flow.

13. **Ashtakavarga undocumented.** SKILL.md:100-102 claims "the reference
    tables above remain the human-readable spec" for AV, but no reference file
    contains the BAV contribution tables. Add an `ashtakavarga.md` reference or
    drop the claim.

14. **Dasha field naming.** Baseline `bd_lord`/`ad_lord`/`sd_lord` vs
    methodology's "Antardasha"/"Pratyantar" — document the mapping or rename.

15. **`dignity()` docstring overstates.** jyotish_primitives.py:387-388 lists
    `great_friend`/`great_enemy`, which the function never returns — trim the
    docstring.
