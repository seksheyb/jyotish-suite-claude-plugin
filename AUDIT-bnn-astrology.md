# AUDIT — bnn-astrology skill (branch `refactor-efficient` vs `main`)

Audit date: 2026-05-21. Audit only — nothing was fixed, git untouched.

## Summary

**Verdict: SERIOUS GAPS** — the deterministic *natal* core is faithful, but the
**Vimshottari Dasha layer is broken**, and Dasha is methodology priority #1.

- **Part 1 (content):** Clean. The 4 reference files (`methodology.md`,
  `karaka-tables.md`, `degree-flags.md`, `aspects.md`) are **byte-identical**
  between `main` and `refactor-efficient` (`git diff` empty). Every phase,
  prompt, table and conduct rule from the `main` SKILL.md is accounted for in
  the refactor SKILL.md or `orchestration-notes.md`. Nothing LOST. 1 internal
  contradiction introduced (stale frontmatter), 1 intentional methodology
  change (D9 now always derived).
- **Part 2 (script):** Natal tables all CORRECT — Mrityu Bhaga (all 7 planets),
  Pushkara Bhaga, Gandanta, Sandhi, combustion base orbs, BNN friend/enemy (all
  9), special aspects, orb classes, karaka-relative sign math, navamsa,
  Vimshottari year-lengths. **2 P0** dasha bugs, **3 P1**, **~7 P2**.
- **Part 3 (run):** Both code paths exit 0 with valid JSON; 8/8 natal
  sanity-checks correct. The dasha block is wrong on the computed-chart path and
  null on the pasted-chart path.

Counts: Part 1 — 0 LOST, 1 CONTRADICTED, 1 intentional CHANGE, ~24 PRESERVED/MOVED.
Part 2 — 2 WRONG/MISSING at P0, 3 at P1, ~7 APPROXIMATED/cosmetic at P2.

---

## Part 1 — Content gaps (main SKILL.md → refactor)

`main` already had the 4 reference files; only the SKILL.md was monolithic. So
this table tracks `main` SKILL.md content into `refactor` SKILL.md +
`references/orchestration-notes.md`.

| Item (main SKILL.md) | Status | Where it went | Severity |
|---|---|---|---|
| Frontmatter description ("accepts a pre-computed Vedic birth chart (D1 + D9)") | CONTRADICTED | Copied verbatim into refactor frontmatter (SKILL.md:3-11) but the refactor body now (a) computes from birth data and (b) derives D9 — "Never ask the user for a separate D9 chart" (orchestration-notes.md:56). Description is stale on both counts. | P2 |
| Overview step 1 "Accept chart data … no computation" | CHANGED (enhanced) | SKILL.md:28 Phase A now also accepts birth data → `chart-calculator`. A net add, not a loss. | — |
| Overview steps 2-4 (display / question / analyse) | PRESERVED | SKILL.md Wave 0-2 (lines 37-70) | — |
| Core BNN principle (Sign=field, Planet=actor, read from Karaka not Lagna) | MOVED | orchestration-notes.md:10-17 "Core BNN Principle" | — |
| Reference-files "load when needed" table | PRESERVED + expanded | SKILL.md:91-97 (adds orchestration-notes.md row) | — |
| PHASE 1 chart-intake prompt box | MOVED (content changed) | orchestration-notes.md:25-44 "Chart Intake Format" — D9 request removed ("D9 is derived automatically; you don't need to paste it") | intentional |
| PHASE 1 D9-not-provided gate ("Do you have your D9? … Skip D9 … suppress all D9 analysis") | CHANGED (removed by design) | orchestration-notes.md:53-69 "D9 — always derived" replaces the gate; D9 is deterministic from D1 degrees. Defensible. Residual issue: frontmatter still says "D1 + D9". | intentional |
| PHASE 1 "compute Vimshottari from Moon's Nakshatra if DOB given" | PRESERVED (partial) | Baseline / `ephemeris._vim_dasha` — but see Part 2 P0-1/P0-2: the result is birth-time, not current, and dropped on a pasted chart. | — |
| PHASE 1 "degrees critical — flag if signs only" | MOVED | orchestration-notes.md:65-69 "The one real gate is degrees" | — |
| PHASE 2 verification display (ASCII box, columns, flag legend) | MOVED (abbreviated) | orchestration-notes.md:121-161 "Verification Display Format" — D1 table collapsed to "Sun … Ketu — one row per planet", D9 to one line. Header row + flag legend kept verbatim. | P2 (WEAKENED) |
| PHASE 2 SIGN LAYOUT table (12 signs + field labels) | MOVED | orchestration-notes.md:192-213 "Sign Layout Working Reference" | — |
| PHASE 2 "Sign Layout unique to BNN" note | PRESERVED | orchestration-notes.md:145-148, 194-196 | — |
| PHASE 2 "Do NOT proceed until user confirms" | PRESERVED | orchestration-notes.md:163; SKILL.md:49 | — |
| PHASE 3 question-intake prompt box | MOVED | orchestration-notes.md:94-117 "Question Intake Prompt" | — |
| PHASE 3 classification table (6 rows) | MOVED | orchestration-notes.md:80-87 "Question Classification" | — |
| PHASE 3 one-line classification template | PRESERVED | orchestration-notes.md:76-78 | — |
| PHASE 3 gender-sensitive marriage Karaka | PRESERVED + clarified | orchestration-notes.md:89-90 | — |
| PHASE 4 methodology overview (Sections 1-5) | PRESERVED | `methodology.md` Sections 1-5 (unchanged from main); SKILL.md:86-97 | — |
| Conduct rule 1 "never skip Phase 2" | PRESERVED | SKILL.md:48-49; orchestration-notes.md:163 | — |
| Conduct rule 2 "never skip Phase 3" | PRESERVED | SKILL.md:83-84; orchestration-notes.md:117 | — |
| Conduct rule 3 "never read from Lagna" | PRESERVED | orchestration-notes.md conduct rule 1 (169-170) | — |
| Conduct rule 4 "always load aspects.md / empty-sign check" | PRESERVED | orchestration-notes.md conduct rule 4 (174-175) | — |
| Conduct rule 5 "always load degree-flags.md / never guess degrees" | MOVED (to script) | Degree flags now pre-computed by `compute_bnn_baseline.py`; orchestration-notes.md conduct rule 3 notes "baseline sidecar pre-computes these" | — |
| Conduct rule 6 "degrees required" | PRESERVED | orchestration-notes.md conduct rule 6 (181-183) | — |
| Conduct rule 7 "D9 gate" | CHANGED (removed) | orchestration-notes.md conduct rule 5 (179-180) — "D9 is always derived … always run the D9 layer" | intentional |
| Conduct rule 8 "state the Karaka before every step" | PRESERVED | orchestration-notes.md conduct rule 2 (172-173) | — |
| Conduct rule 9 "apply degree flags to every planet" | PRESERVED | orchestration-notes.md conduct rule 3 (174-176) | — |
| Conduct rule 10 "tone" | PRESERVED | orchestration-notes.md conduct rule 7 (184-186) | — |
| Conduct rule 11 "cross-check recommendation" | PRESERVED | orchestration-notes.md conduct rule 8 (187-188) | — |

### Part 1 — contradictions introduced by the refactor

1. **Frontmatter ↔ body.** SKILL.md:5 frontmatter says the skill "accepts a
   pre-computed Vedic birth chart (**D1 + D9**)", but the body / orchestration
   note say D9 must NOT be asked for — "Never ask the user for a separate D9
   chart" (orchestration-notes.md:56) and "D9 is derived automatically; you
   don't need to paste it" (orchestration-notes.md:40). It also fails to mention
   the new birth-data compute path. `commands/bnn.md:11` repeats the stale claim
   ("If the user has not yet provided a pre-computed D1 + D9 chart"). Not
   run-breaking, but misleading. → P2.
2. No phase-ordering or step-level contradiction found between SKILL.md and
   `orchestration-notes.md`. Wave 0 → Wave 1 → Wave 2 is consistent.

### Part 1 — path / agent reference check

All resolve. `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py` ✓,
`${CLAUDE_PLUGIN_ROOT}/scripts/compute_bnn_baseline.py` ✓. Agents
`chart-calculator`, `chart-verifier`, `baseline-runner`, `unit-analyzer`,
`synthesizer` all exist in `agents/` ✓. All 5 `references/*.md` named in
SKILL.md exist ✓. `methodology.md` Sections 2-5 referenced by SKILL.md exist ✓.

---

## Part 2 — Script methodology findings

Audited `scripts/compute_bnn_baseline.py` + `lib/jyotish_primitives.py` +
`lib/ephemeris.py` + `lib/chart_io.py` against the 4 reference files.

### Correct (verified, no action)

| Rule | Reference loc | Script loc | Verdict |
|---|---|---|---|
| Combustion base orbs (Moon 12 / Mars 17 / Mer 14 / Jup 11 / Ven 10 / Sat 15) | degree-flags.md:13-18 | jyotish_primitives.py:61-62 | CORRECT |
| Gandanta zones (26°40′ tail / 3°20′ head of water→fire) | degree-flags.md:29-31 | jyotish_primitives.py:290-299 | CORRECT |
| Mrityu Bhaga table — all 7 planets × 12 signs | degree-flags.md:44-50 | jyotish_primitives.py:70-78 | CORRECT (every value matches) |
| MB ±1° orb | degree-flags.md:41 | jyotish_primitives.py:312-317 (orb=1.0) | CORRECT |
| Pushkara Bhaga degrees (all 12 signs) + ±1° orb | degree-flags.md:60-76 | jyotish_primitives.py:82-85, 320-324 | CORRECT |
| Sandhi 0°–1° / 29°–30° | degree-flags.md:82-86 | jyotish_primitives.py:302-309 | CORRECT |
| Planetary War — eligible set, same-sign, ≤1°, lower-deg wins | degree-flags.md:91-98 | jyotish_primitives.py:66, 346-363 | CORRECT (≤1° only — see P1-1) |
| BNN special aspects (Mars 4/8, Jup 5/9, Sat 3/10, Rahu 5/9, Ketu 5/9) | aspects.md:11-17 | compute_bnn_baseline.py:102-105 | CORRECT |
| Inclusive sign-counting for aspects | aspects.md:19-22 | jyotish_primitives.py:257-259 | CORRECT |
| Orb classes (≤3 tight / ≤7 moderate / >7 loose) | aspects.md:49-53 | compute_bnn_baseline.py:108-116 | CORRECT |
| Mutual aspect detection (A↔B + ≤3°) | aspects.md:60-68 | compute_bnn_baseline.py:257-271 | CORRECT |
| BNN friend/enemy/neutral — all 9 planets | karaka-tables.md:66-76 | compute_bnn_baseline.py:65-97 | CORRECT (all 9 rows verified) |
| Vimshottari year-lengths | methodology.md:158 | jyotish_primitives.py:45-46 | CORRECT |
| Karaka-relative positions 2/12, 5/9, 3/11, 7 | methodology.md:57-136 | compute_bnn_baseline.py:279-338 | CORRECT |
| Vargottama (D1 sign == D9 sign) | methodology.md:147 | compute_bnn_baseline.py:334 | CORRECT |
| Navamsa derivation | (chart-tables convention) | jyotish_primitives.py:271-277 | CORRECT |
| Priority table: Combust>all, MB+exalt, MB+retro, Sd+PK, Vo+PK, Retro+PK, Retro+MB, PW-defeated+PK | degree-flags.md:108-122 | compute_bnn_baseline.py:123-169 | CORRECT |

### WRONG / MISSING / APPROXIMATED

| # | Rule | Reference loc | Script loc | Verdict | Note |
|---|---|---|---|---|---|
| P0-1 | "Current Mahadasha lord" / Dasha activation timing | methodology.md:154-172 (Sec 4), :199 (Sec 5 priority #1) | ephemeris.py:167-178, :274-275; compute_bnn_baseline.py:360, 376-380 | **WRONG** | `_vim_dasha` calls `find_running(tree, ref_dt_utc)` with **birth UTC**, so `dasha.running` is the *birth-moment* MD/BD/AD/SD quartet, not the current one. The baseline also drops `mahadasha_sequence` and `tree`. A reading run in 2026 sees the 1988 dasha (test: `running.md_lord = "Ketu"`, period 1981-1988; the true current MD on 2026-05-21 is Mars). Methodology's highest-weighted factor produces actively wrong output. |
| P0-2 | Pasted-chart dasha pass-through | chart_io.py:65-76 `_dasha_for` | compute_bnn_baseline.py:376-380 | **MISSING** | `build_baseline` only copies 3 hard-coded keys (`starting_mahadasha`, `balance_years`, `running`). When a user pastes a chart with a stated dasha, `_dasha_for` returns `{"source":"user-supplied", "current_mahadasha":…, …}` — none of those keys match, so the baseline emits `dasha: {starting_mahadasha:null, balance_years:null, running:null}`. The user's stated dasha is silently dropped. The "unavailable" `note` is dropped too. (Reproduced in Part 3.) |
| P1-1 | Close Contention — Planetary War within 2°–5° | degree-flags.md:99; methodology.md:31 | jyotish_primitives.py:359-362; compute_bnn_baseline.py:191-193 | **MISSING** | `jp.planetary_war` only appends pairs with `sep <= 1.0`. The `elif sep <= 5.0` branch in `build_planets` (compute_bnn_baseline.py:191-193) is therefore **dead code** — `war_status` is never set to `close_contention`, the `close_contention` branch of `priority_verdict` (line 162-164) never fires, and the `[CC]` flag promised in the verification legend never appears. |
| P1-2 | Combustion retrograde orbs | degree-flags.md:13-18 (only Mer 14 / Ven 10; no retro variant) | jyotish_primitives.py:63, 339-340 | **WRONG (deviation)** | Script applies `COMBUSTION_ORBS_RETRO = {Mercury:12, Venus:8}` — orbs **not in** `degree-flags.md`. Per audit rule, the reference is source of truth. For retrograde Mercury 12°–14° from Sun (or Venus 8°–10°) the reference says combust, the script says not — flipping a 🔴 dominant `degree_flag_verdict`. |
| P1-3 | Mercury combustion exemption — "superior conjunction is exempt" | degree-flags.md:16 | jyotish_primitives.py:334-343 | **MISSING** | `combustion()` uses an undirected `min(sep, 360-sep)` separation only. The explicit reference exception (Mercury combust 14° behind Sun, but superior conjunction exempt) is not implemented; Mercury in superior conjunction is flagged combust when the reference exempts it. |
| P2-1 | Priority: Vargottama + Mrityu Bhaga → "Mixed — soul-level intent strong but material delivery blocked" | degree-flags.md:119 | compute_bnn_baseline.py:137-143 | **APPROXIMATED** | The `mrityu_bhaga` branch runs before any vargottama check and returns a plain MB verdict; the documented "Mixed" combination note is never produced. |
| P2-2 | Priority: Gandanta + own sign → "karmically charged but capable if worked consciously" | degree-flags.md:116 | compute_bnn_baseline.py:144-146 | **APPROXIMATED** | `gandanta` branch returns one generic note; the own-sign nuance is not special-cased (`priority_verdict` does not receive enough dignity context to do so cleanly). |
| P2-3 | Pushkara Navamsa zones | degree-flags.md:56-76 (heading names "Pushkara Navamsa" but **no table given** — only Pushkara Bhaga) | jyotish_primitives.py:88-101 `PUSHKARA_NAVAMSA` | **UNVERIFIABLE** | The script implements 12 sign × 2-zone Pushkara Navamsa data and feeds it into `priority_verdict` (`pushkara = pushkara_bhaga or pushkara_navamsa`), but the reference defines no such table — cannot be verified. Reference is incomplete or the script invents undocumented data. |
| P2-4 | Karaka 1A / Sign-field 1B significations | karaka-tables.md:11-19 (1A), :47-58 (1B) | compute_bnn_baseline.py:27-46, 49-62 | **APPROXIMATED** | Script's `NATURAL_KARAKAS` / `SIGN_FIELD` strings drop reference detail — e.g. Sun loses "career (authority-based)", "bones", "right eye"; Saturn loses "masses"; Aries loses "head", Taurus "face", Leo "spine", Capricorn "bones". Low impact (workers also load `karaka-tables.md`), but the baseline's `karaka_signification` field is lossy. |
| P2-5 | Empty-position support: sign lord + aspects-onto-position | methodology.md:67, 92, 111, 129; aspects.md:96-107 | compute_bnn_baseline.py:300-338 | **APPROXIMATED** | `karaka_positions` lists `occupants` per position but surfaces neither the position sign's lord nor an inverse "aspected_by" map. The worker must invert `aspects.pre_map` itself to apply the empty-sign rule. Feasible but undocumented in the agent contract. |

### Baseline JSON field-coverage check

Emitted top-level keys: `school, chart_meta, natural_karakas, planets,
karaka_positions, aspects, dasha`. Cross-checked against what
`methodology.md` / `orchestration-notes.md` / the agents need:

- `planets[*].degree_flags`, `.degree_flag_verdict`, `.dignity`, `.retrograde`,
  `.navamsa_sign`, `.planetary_war` — all present, support Steps A-F ✓
- `karaka_positions[*].d1_positions` / `.d9_positions` / `.d1_conjunctions` /
  `.vargottama` — present for all 9 planets, supports Sec 2-3 ✓
- `aspects.pre_map` + `aspects.mutual_aspects` — present, supports aspects.md ✓
- `dasha` — **incomplete** (P0-1 / P0-2). SKILL.md:53-54 claims the script
  "computes … Vimshottari dasha"; in practice it surfaces only a birth-time
  quartet (computed path) or all-null (pasted path), and never the
  current/upcoming dasha that methodology Section 4 + Section 5 priority #1
  require.

---

## Part 3 — Run results

### Run 1 — birth data (computed chart)
```
python3 plugins/jyotish-suite/scripts/compute_bnn_baseline.py \
  --datetime "1988-02-14T09:30:00" --tz "Asia/Kolkata" --lat 19.07 --lon 72.87
```
- Exit **0**, valid JSON, 7 top-level keys. No stderr.

### Run 2 — user-pasted chart path
```
python3 plugins/jyotish-suite/lib/chart_io.py --mode parashari \
  --positions /tmp/bnn_positions.json --out /tmp/bnn_chart.json     # exit 0
python3 plugins/jyotish-suite/scripts/compute_bnn_baseline.py \
  --chart /tmp/bnn_chart.json                                       # exit 0
```
- Exit **0**, valid JSON, no crash.
- **But:** input positions JSON carried `"dasha": {"current_mahadasha":"Venus",
  "current_antardasha":"Saturn"}`; the baseline emitted
  `dasha: {starting_mahadasha:null, balance_years:null, running:null}` — user
  dasha lost (confirms **P0-2**).

### Sanity checks (Run 1) — 8/8 correct

| Value | Baseline | Hand check |
|---|---|---|
| D1 Lagna | Pisces | ✓ plausible (Mumbai, 09:30 IST, ~2.5 h after sunrise; Sun in Aquarius) |
| Sun | Aquarius 0.98° | ✓ sidereal Sun mid-Feb ≈ Aquarius 1° |
| Moon nakshatra → starting MD | Sag 11.96° = Mula → Ketu | ✓ Mula star-lord is Ketu; `starting_mahadasha = Ketu` |
| Venus dignity | Pisces → exalted | ✓ Venus exalts in Pisces |
| Mercury | Capricorn, neutral, retro, **Cb** | ✓ Cap lord Saturn = neutral; sep from Sun 6.5° < 12° retro orb → combust |
| Mars 0.75° Sag | **Gd** (Gandanta) | ✓ first 3°20′ of Sagittarius |
| Moon 11.96° Sag | **PK** (Pushkara) | ✓ Pushkara Bhaga Sag = 11°, 23°; |11.96−11| ≤ 1° |
| Sun 0.98° Aquarius | **Sd** (Sandhi) | ✓ deg-in-sign < 1° |

### Sanity check that FAILED

| Value | Baseline | Correct |
|---|---|---|
| Running Mahadasha (reading date 2026-05-21) | `running.md_lord = "Ketu"`, period **1981-11 → 1988-11** | Should be **Mars** MD (2024-11 → 2031-11). The baseline returns the *birth-time* dasha — confirms **P0-1**. |

---

## Prioritized fix list

### P0 — produces wrong output

1. **`dasha.running` is birth-time, not current** (compute_bnn_baseline.py:360,
   376-380; ephemeris.py:167-178, 274-275).
   *Fix:* add an optional `--query-date` arg to `compute_bnn_baseline.py`
   (default = today), and in `build_baseline` recompute the running quartet with
   `jp.find_running(tree, query_date)` instead of echoing the birth-time
   `running`. Also carry `mahadasha_sequence` (and ideally `tree`) into the
   baseline so the worker can locate current + upcoming periods for the
   methodology Section 4 timing output. Until fixed, every BNN reading's
   headline timing (Section 5 priority #1) is wrong.

2. **Pasted-chart user dasha silently dropped** (compute_bnn_baseline.py:
   376-380).
   *Fix:* replace the 3-key hard-coded copy with a full pass-through of
   `chart.get("dasha", {})` (merge, don't cherry-pick), so `source`,
   `current_mahadasha`, `current_antardasha` and the "unavailable" `note`
   survive into the baseline. Pair with P0-1 so a pasted chart that *does*
   carry a `birth` block still gets a correctly-dated running dasha.

### P1 — missing capability / reference disagreement

3. **Close Contention (2°–5°) never detected** (jyotish_primitives.py:359-362;
   dead branch compute_bnn_baseline.py:191-193).
   *Fix:* extend `jp.planetary_war` to also return pairs with `1° < sep ≤ 5°`
   tagged `"close_contention"` (or add a separate CC pass), so the existing
   `elif` branch and `priority_verdict`'s `close_contention` case become live
   and the `[CC]` legend entry is honoured.

4. **Combustion retrograde orbs deviate from the reference**
   (jyotish_primitives.py:63, 339-340 vs degree-flags.md:13-18).
   *Fix:* either delete `COMBUSTION_ORBS_RETRO` so the script matches
   `degree-flags.md`, or (preferred, if astrologically intended) add the
   retrograde orbs to the `degree-flags.md` combustion table so reference and
   script agree.

5. **Mercury superior-conjunction combustion exemption not implemented**
   (jyotish_primitives.py:334-343 vs degree-flags.md:16).
   *Fix:* in `combustion()`, when `planet == "Mercury"`, skip the combust flag
   when Mercury is in superior conjunction (far side of the Sun), per the
   parenthetical in the reference.

### P2 — cosmetic / lossy / contradiction

6. **Stale frontmatter / command** — SKILL.md:5 and commands/bnn.md:11 still say
   "pre-computed … D1 + D9". *Fix:* update the description to "accepts a
   pre-computed D1 chart **or** birth data; D9 is derived automatically."

7. **Vargottama + MB → "Mixed"** not produced (compute_bnn_baseline.py:137-143).
   *Fix:* before the plain MB return, check `flags["vargottama"]` and emit the
   degree-flags.md:119 "Mixed" verdict.

8. **Gandanta + own sign nuance** absent (compute_bnn_baseline.py:144-146).
   *Fix:* pass `dignity` into the gandanta branch and special-case `own` →
   "karmically charged but capable" per degree-flags.md:116.

9. **Pushkara Navamsa undocumented** (jyotish_primitives.py:88-101).
   *Fix:* add the Pushkara Navamsa zone table to `degree-flags.md` (the heading
   already names it) so the script's data is verifiable — or drop
   `pushkara_navamsa` if only Pushkara Bhaga is intended.

10. **Abbreviated karaka/sign-field significations** (compute_bnn_baseline.py:
    27-62). *Fix:* copy the `karaka-tables.md` 1A/1B strings verbatim into
    `NATURAL_KARAKAS` / `SIGN_FIELD` so the baseline's `karaka_signification`
    is lossless.

11. **Verification display template abbreviated** (orchestration-notes.md:
    121-161). *Fix:* restore the full D1 + D9 ASCII tables from the `main`
    SKILL.md so `chart-verifier`'s "exact format" instruction has an exact
    target.

12. **`karaka_positions` lacks sign lord + inverse aspect map**
    (compute_bnn_baseline.py:300-338). *Fix (optional):* add `sign_lord` and an
    `aspected_by` list to each position block so the worker can apply the
    empty-sign rule without inverting `aspects.pre_map`.

---

*Minor observation (no severity):* Rahu/Ketu always appear in
`aspects.mutual_aspects` with orb 0.0 (they are always exactly opposed and share
deg-in-sign) — harmless noise in every chart; the synthesizer should ignore it.
