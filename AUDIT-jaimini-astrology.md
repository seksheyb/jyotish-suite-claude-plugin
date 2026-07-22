# Audit Report — `jaimini-astrology` skill

Branch audited: `refactor-efficient` · Baseline: `main` · Date: 2026-05-21
Scope: AUDIT ONLY — no files were changed.

---

## Summary

**Overall verdict: SERIOUS GAPS (1 P0, 3 P1, 6 P2).**

The refactor preserved the interpretive content well — all 12 conduct rules, the
question-classification table, the topic map, the intake prompts and every
Phase-4/5 instruction survive in `references/orchestration-notes.md`, and the
five deterministic reference files (`methodology.md`, `computation.md`,
`jaimini-drishti.md`, `degree-flags.md`, `argala.md`) are **byte-identical to
`main`** — nothing in them was lost.

But three real problems remain:

1. **P0 — `lib/jyotish_primitives.py` Pushkara Navamsa table is wrong.** The
   `PUSHKARA_NAVAMSA` zones disagree with `degree-flags.md` for **all 12 signs**
   (6 totally different, 6 partially). The `pushkara_navamsa` degree flag in the
   baseline is wrong output for every chart.
2. **P1 — the baseline-display/verification-display contradiction.** The
   refactor merged `main`'s Phase 2 (chart verification) and Phase 3 (Jaimini
   baseline) into one "Verification Display Format" that `chart-verifier` is
   told to render **before** `baseline-runner` has computed the baseline. The
   agent that renders it cannot populate it.
3. **P1 — Chara Dasha Antardasha is never computed**, although the verification
   display, methodology Step 0F, Section 4B and Section 5 Step 7 all require it.

Both run paths (computed chart, user-pasted chart) execute cleanly — exit 0,
valid JSON — and the deterministic numbers that *are* produced sanity-check
correctly (Chara Karakas, Arudhas incl. the 10th-from exception, Swamsha,
Chara Dasha sequence, the 12×12 drishti map).

Counts: **Part 1** — 16 items walked, 14 PRESERVED/MOVED cleanly, 1 contradiction
cluster, 1 intentional modification. **Part 2** — 26 deterministic rules checked:
20 CORRECT, 1 WRONG (P0), 1 WRONG (P1), 1 MISSING (P1), 3 garbled/incomplete in
the *reference* (script is right), 1 MISSING (P2), 1 PARTIAL (P2).

---

## Part 1 — Content gaps

Walking `git show main:.../jaimini-astrology/SKILL.md` (247 lines) top to bottom
against the refactor-branch `SKILL.md` + `references/orchestration-notes.md`.

| Item (in `main` SKILL.md) | Status | Where it went | Severity |
|---|---|---|---|
| Frontmatter `name` + `description` | PRESERVED | refactor `SKILL.md:1-11` — text essentially identical | — |
| Overview — 5-step workflow | MOVED | refactor `SKILL.md:20-86` "Orchestration" — Phases A/B + Waves 0/1/2 | — |
| Reference-files load table (5 files) | MOVED + EXPANDED | refactor `SKILL.md:93-100` "Methodology" table — now 6 (adds `orchestration-notes.md`) | — |
| PHASE 1 — chart-collection prompt box | MOVED + MODIFIED | `orchestration-notes.md:16-35` "Chart Intake Format" | P2 |
| └ explicit "D9 (Navamsa) Chart" request | REMOVED (intentional) | D9 now always derived — `orchestration-notes.md:109-126` | — |
| └ "If D9 not provided → D1 only; flag D9 unavailable" | SUPERSEDED (intentional) | D9 always derived deterministically; conduct rule 10 updated | — |
| └ "If Dasha balance missing but DOB given → compute from Moon" | PRESERVED | sidecar: `ephemeris._vim_dasha` / Chara Dasha computed from chart degrees | — |
| PHASE 2 — Chart Verification Display box (D1 table, flag legend, D9 table) | MOVED | `orchestration-notes.md:135-198` "Verification Display Format" | see ⚠ |
| └ "Do NOT proceed until user explicitly confirms" | PRESERVED | conduct rule 1; Wave 0 step 2; `orchestration-notes.md:200` | — |
| PHASE 3 — Jaimini Baseline Display box (Karakas, War, Close-degree, Swamsha, Karakamsha, Arudhas, Argala AL/Swamsha, Chara Dasha) | MOVED + **CONFLATED** | merged *into* the Verification Display Format — **contradiction, see ⚠** | **P1** |
| PHASE 4 — Question Intake prompt box (6 examples) | PRESERVED / MOVED | `orchestration-notes.md:47-64` "Question Intake Prompt" | — |
| PHASE 4 — question classification table (7 rows) | PRESERVED + EXPANDED | `orchestration-notes.md:79-87` — adds a "Wave 1 units" column | — |
| PHASE 4 — "State classification in one line" quote | PRESERVED | `orchestration-notes.md:75-77` verbatim | — |
| PHASE 4 — topic→Karaka/Arudha map | PRESERVED | `orchestration-notes.md:91-102` **and** `methodology.md:177-188` | — |
| PHASE 4 — "Do NOT begin analysis until user answers" | PRESERVED | `orchestration-notes.md:66`; refactor `SKILL.md:70` | — |
| PHASE 5 — analysis / methodology pointer (Steps 0–F, Sections 1–5) | PRESERVED | `methodology.md` unchanged from `main`; `orchestration-notes.md:234-245` "Wave-to-Methodology Map" | — |
| CONDUCT RULES 1–12 | PRESERVED (all 12) | `orchestration-notes.md:204-230` — rules 4 & 10 lightly enhanced for the drishti-map / D9-derivation change | — |

### ⚠ Refactor-introduced contradiction (P1) — the baseline display has no producer

`main` had **two** user-facing displays at two times: Phase 2 verifies the chart,
the user confirms, **then** Phase 3 computes and shows the Jaimini baseline. The
refactor collapsed both into one block but kept the two-step ordering, producing
an internal contradiction with four mutually-reinforcing parts:

1. `orchestration-notes.md:131-134` says **`chart-verifier`** renders the
   "Verification Display Format", and that format (`:153-184`) contains the full
   `JAIMINI BASELINE:` block — Chara Karakas, Planetary War, Swamsha,
   Karakamsha, Arudha Padas, Argala on AL/Swamsha, Chara Dasha.
2. Refactor `SKILL.md:49-53` (Wave 0 **step 2**) dispatches `chart-verifier` to
   render that display — **before** Wave 0 **step 3** (`SKILL.md:54-58`) runs
   `baseline-runner` / `compute_jaimini_baseline.py`. When `chart-verifier`
   runs, the baseline does not exist yet.
3. `orchestration-notes.md:206-207` (conduct rule 1) is explicit: *"chart-verifier
   output must be confirmed by the user **before** `baseline-runner` runs."* So
   the confirmed display is necessarily pre-baseline and **cannot** contain it.
4. `agents/chart-verifier.md` states the agent does **"no interpretation"** and
   **"does not compute planetary positions"**; its native display spec is *"a D1
   table … a D9 table, the Lagna, the dasha balance"* — **no baseline block** —
   and it is never handed `compute_jaimini_baseline.py`. It physically cannot
   fill Chara Karakas / Swamsha / Argala / Chara Dasha.

Consequently Wave 0 **step 4** (`SKILL.md:59-61`, *"Show the user the displayed
Jaimini baseline"*) and conduct rule 2 (*"Never skip the baseline display"*) have
**no producer and no template** — the only baseline-containing template is the
mis-placed Verification Display Format, and `baseline-runner` only returns a
"<120-word gloss", not a formatted display.

This is a genuine, run-breaking spec defect. Fix direction: split the
"Verification Display Format" into (a) a chart-only verification display rendered
by `chart-verifier` at step 2, and (b) a separate Jaimini-baseline display
rendered at step 4 from `baseline-runner`'s JSON.

### Path / agent resolution check — all clean

Every reference in `SKILL.md` resolves: `references/{methodology,computation,
jaimini-drishti,degree-flags,argala,orchestration-notes}.md` all exist;
`${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py`, `${CLAUDE_PLUGIN_ROOT}/lib/ephemeris.py`
and `${CLAUDE_PLUGIN_ROOT}/scripts/compute_jaimini_baseline.py` all exist; agents
`chart-calculator`, `chart-verifier`, `baseline-runner`, `unit-analyzer`,
`synthesizer` all exist in `agents/`.

---

## Part 2 — Script methodology findings

Scripts audited: `scripts/compute_jaimini_baseline.py`, `lib/jyotish_primitives.py`,
`lib/ephemeris.py`, `lib/chart_io.py`. Reference = source of truth.

### Full rule-by-rule table

| Rule | Reference loc | Script loc | Verdict | Note |
|---|---|---|---|---|
| D9 navamsa mapping table | `computation.md:19-31` | `jyotish_primitives.py:271-277` (`navamsa_sign`), `:58` `_NAVAMSA_START` | CORRECT | Fire→Ari, Earth→Cap, Air→Lib, Water→Can; 3°20′ steps — matches. |
| Vargottama definition | `computation.md:33` | `jyotish_primitives.py:280-283` | CORRECT | |
| Arudha formula (count N, then N again) | `computation.md:39-44` | `compute_jaimini_baseline.py:119-134` | CORRECT | Verified by hand: AL = Taurus for the test chart. |
| Arudha exception (same-sign / 7th → 10th from house) | `computation.md:45-48` | `compute_jaimini_baseline.py:130-133` | CORRECT | Verified: A6 raw=Leo (=house) → exception → Taurus. |
| Jaimini sign-lord table | `computation.md:65-78` | `jyotish_primitives.py:21-22` `SIGN_LORDS` + `compute_jaimini_baseline.py:238-248` | CORRECT | |
| **Dual-lord tiebreak — "Kendra/Trikona from Lagna"** | `computation.md:80` | `compute_jaimini_baseline.py:260-264` | **WRONG** | Script measures the house **from the lorded sign** (`count_signs(sign_idx, psi)`), not from the Lagna. `jaimini_sign_lord` is never even passed `lagna_sign_idx`. Mis-picks the Scorpio/Aquarius lord → wrong Chara Dasha years. **P1.** |
| Chara Dasha years = "number of signs counted" | `computation.md:83-92`, `methodology.md:268-270` | `compute_jaimini_baseline.py:271-287` (`count_signs − 1`) | DISCREPANCY | Script uses inclusive-count **minus 1** (the astrologically-standard rule); references literally say "number of signs counted = years" (no −1) and the `>12` clause (`computation.md:89-92`) is self-contradictory garble. Script output is correct; **the reference text is broken.** **P2 (fix the references).** |
| Chara Dasha — lord in same sign → 12 years | `computation.md:87` | `compute_jaimini_baseline.py:277-278, 281-282` | CORRECT | |
| Chara Dasha — starting Rasi & direction (Movable/Fixed/Dual) | `computation.md:99-105` | `compute_jaimini_baseline.py:292-298` | CORRECT | Dual → 9th from Lagna, zodiacal — verified (Pisces → Scorpio start). |
| Chara Dasha — birth-balance formula | `computation.md:109-116` | `compute_jaimini_baseline.py:303-305` | CORRECT | `elapsed = (lagna_deg/30)·first_years`, `balance = first_years − elapsed`. |
| **Chara Dasha — Antardasha computation** | `computation.md:128-134` (Step 5) | *(absent)* | **MISSING** | `compute_chara_dasha` returns only the 12-Rasi Mahadasha sequence. No Antardasha anywhere in the baseline. Required by the verification display, `methodology.md:122` (Step 0F), Section 4B and Section 5 Step 7. **P1.** |
| Chara Karaka ranking (Sapta, 7 planets, descending degree-in-sign) | `computation.md:138-159`, `methodology.md:9-26` | `compute_jaimini_baseline.py:85-103` | CORRECT | Verified: AK Mercury 24.51° … DK Mars 0.75°. |
| Rahu excluded from Sapta ranking | `methodology.md:11`, `computation.md:142` | `compute_jaimini_baseline.py:26` `SAPTA` (7 planets) | CORRECT | The "Rahu effective degree = 30−deg" line in the refs is vestigial (only applies to the 8-karaka Ashtaka scheme); correctly ignored. |
| Close-degree Karaka flag (adjacent karakas within 1°) | `methodology.md:27` | `compute_jaimini_baseline.py:104-111` | CORRECT | Verified: AmK-BK 0.18°, PK-GK 0.83°, GK-DK 0.23°. |
| Gandanta zones (water→fire junctions) | `degree-flags.md:8-18` | `jyotish_primitives.py:290-299` | CORRECT | |
| Mrityu Bhaga table (7 planets × 12 signs) | `degree-flags.md:25-33` | `jyotish_primitives.py:70-79` `MRITYU_BHAGA` | CORRECT | All 84 values match; ±1° orb (`:312-317`). |
| **Pushkara Navamsa zones** | `degree-flags.md:43-58` | `jyotish_primitives.py:88-101` `PUSHKARA_NAVAMSA` | **WRONG** | Disagrees with the reference for **all 12 signs** (6 entirely different, 6 with one zone wrong). 0/12 fully match. The `pushkara_navamsa` flag is wrong output for every chart. **P0.** |
| Pushkara Bhaga degrees | `degree-flags.md:64-79` | `jyotish_primitives.py:82-85` `PUSHKARA_BHAGA` | CORRECT | All values match. |
| Sandhi zones (0–1° / 29–30°) | `degree-flags.md:84-90` | `jyotish_primitives.py:302-309` | CORRECT | |
| Planetary War (≤1°, same sign, eligible planets, lower degree wins) | `degree-flags.md:94-110` | `jyotish_primitives.py:346-363` `planetary_war` | CORRECT | `WAR_PLANETS` excludes Sun/Moon/Rahu/Ketu; lower longitude = winner. |
| **Planetary "close contention" (2°–5° gap)** | `degree-flags.md:108`, `methodology.md:34` | *(absent)* | **MISSING** | Only the ≤1° war is detected; the 2–5° close-contention flag is never computed. **P2.** |
| Jaimini Drishti — 3 rules + 12-sign aspect matrix | `jaimini-drishti.md:9-114` | `compute_jaimini_baseline.py:38-78` `build_drishti_map` | CORRECT | Matches the "Clean Reference Table" exactly. |
| Jaimini Drishti — one-way aspects | `jaimini-drishti.md:155-163` (lists 4) | `build_drishti_map` `one_way` (produces 8) | SCRIPT CORRECT / **REFERENCE WRONG** | By the Three Rules there are **8** one-way aspects; the script finds all 8. `jaimini-drishti.md` documents only 4 and `:123` wrongly lists e.g. "Aries ↔ Aquarius" as *mutual*. Script is right; reference is self-contradictory. **P2 (fix the reference).** |
| Argala — positions 2/4/11 (+5 secondary), Virodha 12/10/3 (+9) | `argala.md:9-23` | `compute_jaimini_baseline.py:202-207` | CORRECT | |
| Argala — effectiveness (Argala planets must strictly outnumber Virodha) | `argala.md:29-37` | `compute_jaimini_baseline.py:214-221` | CORRECT | `>` → effective, `==` → cancelled, `<` → obstructed, empty → no_argala. |
| Argala — pre-map for AL and Swamsha | `argala.md:73`, `methodology.md:109` | `compute_jaimini_baseline.py:436-445` | PARTIAL | AL + Swamsha (required) **are** covered, plus UL/A10/Lagna. But `methodology.md:217-219` Step B needs Argala on **the question's Arudha** — A3/A4/A5/A6/A7/A11 have no Argala in the baseline and the `unit-analyzer` is told not to recompute. **P2.** |

### `WRONG` / `MISSING` items called out (Part 2)

- **P0 — `PUSHKARA_NAVAMSA` table wrong** (`jyotish_primitives.py:88-101`).
  E.g. reference Leo = `6°40′–10°00′` and `26°40′–30°00′`; the script has Leo =
  `3°20′–6°40′` and `20°00′–23°20′`. A planet at Leo 8° should flag Pushkara
  Navamsa; the script returns `false`. Wrong for every sign.
- **P1 — Antardasha missing** (`compute_chara_dasha`, `:290-337`). No
  sub-period at all; the baseline `chara_dasha.running` is a *Mahadasha* only.
- **P1 — dual-lord tiebreak uses wrong reference point** (`:260-264`). Kendra/
  Trikona is measured from the lorded sign instead of the Lagna.
- **P2 — close-contention (2–5°)** not computed.
- **P2 — Argala coverage incomplete** — only 5 signs pre-mapped.
- **Reference-side bugs** (script is correct, the *.md* is wrong): the Chara
  Dasha `count` vs `count−1` wording + garbled `>12` clause in
  `computation.md:83-92`; the one-way-aspect list in `jaimini-drishti.md:118-163`;
  and the worked-example ranking tail in `computation.md:159` ("Mercury 09°10′ →
  Saturn 09°35′" is mis-ordered — Saturn's degree is higher, so it should rank
  above Mercury, making Saturn=GK and Mercury=DK).

### Baseline JSON field coverage

The emitted baseline (top keys: `chart_meta, chara_karakas, arudha_padas,
swamsha, karakamsha, argala, chara_dasha, jaimini_drishti_map, planets,
planetary_wars, vimshottari_dasha`) carries what most workers need. Gaps:

- **No Chara Dasha Antardasha** (the P1 above) — `synthesizer` Section 4B / 5
  cannot get it and is told not to recompute.
- The `planets` block (`build_planet_block`, `:358-379`) omits `nakshatra`,
  `pada` and `house`. The verification display needs nakshatra/pada per planet —
  `chart-verifier` can read those from the *chart* JSON, so this is survivable,
  but a `unit-analyzer` wanting a planet's house-from-Lagna must derive it. **P2.**
- `chara_karakas` rows don't inline `degree_flags`; reachable via
  `planets[<planet>].degree_flags`, but the display's "Degree Flags" column
  needs a join. **P2 (cosmetic).**

---

## Part 3 — Run results

Test nativity: `1988-02-14T09:30:00`, `Asia/Kolkata`, lat 19.07, lon 72.87.

### Computed-chart path
```
python3 .../scripts/compute_jaimini_baseline.py \
  --datetime "1988-02-14T09:30:00" --tz "Asia/Kolkata" \
  --lat 19.07 --lon 72.87 --target-date 2026-05-21
```
**Exit 0. Valid JSON**, 11 top-level keys. No stderr.

### User-pasted-chart path
1. Built a 9-planet + Lagna positions JSON.
2. `chart_io.py --mode parashari --positions … --out …` → **exit 0**, wrote chart.
3. `compute_jaimini_baseline.py --chart … --age 38` → **exit 0, valid JSON.**

No-birth-data degradation handled gracefully: `chart_meta.datetime_local` =
`null`, `vimshottari_dasha` = `null`, Chara Dasha runs on **ages**
(`start`/`end` null, `start_age`/`end_age` populated; running rasi found by
`--age`). No crash — confirms `compute_jaimini_baseline.py:450-455` and
`chart_io._meta_for` / `_dasha_for` handle the missing-birth case.

### Sanity checks (hand-reasoned)

| Value | Script output | Hand check | Verdict |
|---|---|---|---|
| D1 Lagna | Pisces 14.35° | Morning birth, Lagna ≈ 2 signs past Sun — plausible | ✓ |
| Sun sign | Aquarius 0.98° | Sidereal Sun enters Aquarius ~Feb 13 — correct for Feb 14 | ✓ |
| Atmakaraka | Mercury (24.51°) | Highest degree-in-sign of the 7: Me 24.51 > Mo 11.96 > Ve 11.78 > Sa 6.32 > Ju 1.81 > Su 0.98 > Ma 0.75 | ✓ |
| Running Chara Dasha @ 2026-05-21 | Taurus (2022-08→2032-08) | Sequence Scorpio 0.52y, Sag 4y, Cap 11y, Aqu 10y, Pisces 1y, Aries 8y, Taurus 10y → 2026 lands in Taurus | ✓ |
| Arudha Lagna | Taurus | Pisces lagna, lord Jupiter in Aries, N=2 → Aries+2 = Taurus (no exception) | ✓ |
| A6 (exception case) | Taurus, `exception_applied: true` | House=Leo, lord Sun in Aquarius, N=7 → raw arudha = Leo = house → 10th-from-house = Taurus | ✓ |
| Mercury navamsa / dignity / combust | Leo / neutral / combust=true | Cap 24.51° → D9 Leo; Cap lord Saturn is neither friend nor enemy of Mercury → neutral; retro combustion orb 12°, Sun-sep 6.47° ≤ 12 → combust | ✓ |
| Drishti map | 8 one-way aspects | The Three Rules yield exactly 8 one-way aspects — script correct (reference under-documents) | ✓ |

All sanity values are correct. The one deterministic field that is **wrong by
construction** (not visible in these spot checks) is `degree_flags.pushkara_navamsa`
— see P0.

---

## Prioritized fix list

### P0 — wrong output

1. **Rebuild `PUSHKARA_NAVAMSA`** in `lib/jyotish_primitives.py:88-101` to match
   `degree-flags.md:43-58` exactly (12 signs × 2 zones, as `(start,end)` decimal
   in-sign degrees). Current table matches the reference for 0/12 signs. While
   there, note `degree-flags.md:45` (the Aries row) lists only **one** zone where
   every other sign lists two — confirm whether the reference Aries row is
   itself missing a second zone before transcribing. (This table is shared lib
   code — the fix also corrects `vedic-astro` and `bnn-astrology`.)

### P1 — missing capability / structural

2. **Compute Chara Dasha Antardasha.** Add a Step-5 implementation per
   `computation.md:128-134` to `compute_chara_dasha` (`compute_jaimini_baseline.py:
   290-337`): within each Mahadasha Rasi, antardasha starts from the same Rasi,
   same direction, each lasting `(antardasha-Rasi-years / 12) × Mahadasha-years`;
   expose the running Antardasha in `chara_dasha.running` so the verification
   display, methodology 0F/4B and Section 5 Step 7 can be satisfied.
3. **Fix the dual-lord tiebreak reference point.** In `jaimini_sign_lord`
   (`compute_jaimini_baseline.py:238-268`), pass `lagna_sign_idx` in and change
   line 261 `house = jp.count_signs(sign_idx, psi)` to count **from the Lagna**
   (`count_signs(lagna_sign_idx, psi)`), per `computation.md:80`. Today it
   measures Kendra/Trikona from the lorded sign — wrong, and it can flip the
   Scorpio (Mars/Ketu) or Aquarius (Saturn/Rahu) lord, changing Chara Dasha
   period lengths (this becomes a P0 on any chart where the tiebreak is decisive).
4. **Resolve the verification/baseline-display contradiction.** Split
   `orchestration-notes.md`'s "Verification Display Format" (`:135-198`) into two
   templates: (a) a **chart-only** verification display (D1 table, flag legend,
   D9 table) rendered by `chart-verifier` at Wave 0 step 2; (b) a separate
   **Jaimini baseline display** (Karakas, War, Close-degree, Swamsha,
   Karakamsha, Arudhas, Argala AL/Swamsha, Chara Dasha) rendered at Wave 0 step 4
   from `baseline-runner`'s JSON. Update `SKILL.md:49-61` and conduct rules 1–2
   so the agent that renders each display actually possesses the data it needs.

### P2 — cosmetic / reference hygiene / completeness

5. **Compute Argala for all named Arudhas.** Extend `compute_jaimini_baseline.py:
   436-445` to pre-map Argala on A2–A11/UL as well as AL/Swamsha, so a
   `unit-analyzer` handling a Children/Health/Mother/Siblings Arudha (A5/A6/A4/A3)
   can satisfy `methodology.md:217-219` Step B without recomputing.
6. **Add the 2°–5° "close contention" flag** (`degree-flags.md:108`,
   `methodology.md:34`) — a planet-pair degree-gap check alongside
   `planetary_war` in `jyotish_primitives.py`.
7. **Fix `computation.md:83-92`** — the Chara Dasha period rule. State plainly
   that years = (signs from rasi to its lord, counted inclusively) − 1, with
   lord-in-same-sign = 12; delete the self-contradictory `>12` paragraph (lines
   89-92). The script (`count_signs − 1`) is already correct — only the prose
   is broken.
8. **Fix `jaimini-drishti.md:118-163`** — list all **8** one-way aspects
   (add Aries→Aquarius, Cancer→Taurus, Libra→Leo, Capricorn→Scorpio) and remove
   those four pairs from the "Mutual Aspect Pairs" list at `:123-126`. The script
   already produces the correct 8.
9. **Fix `computation.md:159`** — the worked-example ranking tail orders
   "Mercury 09°10′ → Saturn 09°35′" ascending; Saturn's degree is higher, so the
   descending rank is …Sun → **Saturn (GK)** → **Mercury (DK)**.
10. **Optionally enrich the baseline `planets` block** (`build_planet_block`,
    `:358-379`) with `nakshatra`, `pada` and `house`, and inline each Karaka's
    `degree_flags` in `chara_karakas`, so downstream display/worker code never
    needs a cross-lookup or a (forbidden) recompute.
