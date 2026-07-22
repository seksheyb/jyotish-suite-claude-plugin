# AUDIT — `lal-kitab` skill (branch `refactor-efficient` vs `main`)

Audit date: 2026-05-21 · Auditor: automated line-by-line review · **AUDIT ONLY, nothing fixed.**

## Summary

**Overall verdict: MINOR-TO-MODERATE GAPS.** The deterministic backbone is
remarkably faithful — every Lal Kitab table (pakka ghar, exaltation,
debilitation, houses-owned, friendship, blind houses, aspects), all 32 rin
triggers with their Farman citations, the full 63-row Varshphal year-ruler
table, the maturation ages and the house-cycle bands are reproduced **exactly**
from the reference files. The script runs clean on every input path.

The gaps are concentrated in two places: (1) the **severity / teva engine**,
which has 2 wrong checks and 3 missing deterministic rules; (2) **content
templates** — 2 per-unit output templates from the `main` SKILL.md were not
relocated into any reference file and are simply gone.

Counts:
- Part 1 — content: **2 LOST**, **1 WEAKENED**, ~30 PRESERVED/MOVED, **3 new contradictions**.
- Part 2 — script: **2 WRONG**, **5 MISSING**, **6 APPROXIMATED**; ~25 rules verified CORRECT. **3 reference-vs-reference contradictions** (pre-existing).
- Part 3 — runs: **all 3 invocation paths exit 0 with valid JSON**; 7/7 sanity checks pass.
- Prioritised fixes: **5 × P1**, **14 × P2**.

The references (`pakka_ghar.md`, `aspects.md`, `rin_diagnosis.md`,
`teva_types.md`, `timing.md`, `varshphal.md`, `family_chart.md`,
`upaay_catalog.md`) are **byte-identical to `main`** — the refactor only
rewrote `SKILL.md`, added `references/orchestration-notes.md`, the 5 `agents/`,
and `scripts/compute_lalkitab_baseline.py`.

---

## Part 1 — Content gaps

`main` SKILL.md (607 lines) walked top to bottom. Every phase / box / rule /
table accounted for below.

| Item (main SKILL.md) | Status | Where it went | Severity |
|---|---|---|---|
| Frontmatter `name` + `description` | PRESERVED | refactor SKILL.md L1–14 — identical | — |
| Overview + 7 "Hard methodological lines" | MOVED | orchestration-notes.md "Hard methodological lines" (expanded to 12) | — |
| Reference-files load table | MOVED | SKILL.md "Methodology" table L154–164 + orchestration-notes | — |
| Phase 0 intent prompt box | PRESERVED | SKILL.md Phase 0 L36–60 (near-identical) | — |
| Phase 0 intent rules (6) + narration-tilting table (10 rows) | MOVED | orchestration-notes.md "Phase 0 — Intent capture rules" + "Intent-driven narration tilting" | — |
| Phase 1 `CHART INPUT` formatted prompt box (main L114–139) | **WEAKENED** | SKILL.md Phase A L66–74 — collapsed to prose; the formatted box and the explicit "Required data / NOT used" list are gone (content survives as prose, ASCII box dropped — inconsistent with Phase 0, which kept its box) | **P2** |
| Phase 2 re-mapping rule (Aries→1 … Pisces→12) | MOVED | orchestration-notes "Verification Display Format" + script `fixed_house()` | — |
| Phase 2 `LAL KITAB CHART` display box + confirm gate | PRESERVED | orchestration-notes "Verification Display Format" (incl. "Do not proceed until the user explicitly confirms") | — |
| Phase 3 pakka ghar / dignity / substitution | MOVED | script `build_pakka_ghar()` + `pakka_ghar.md` | — |
| Phase 4 sleeping vs awake | MOVED | script `build_sleeping()` + `aspects.md` | — |
| Phase 5 six-rin detection logic | MOVED | script `build_rin_diagnosis()` + `rin_diagnosis.md` | — |
| **Phase 5 per-rin output template** (main L261–268: `RIN:/Trigger Farman:/Configuration:/Severity:/Manifestation:/Remedy reference:`) | **LOST** | not in orchestration-notes, not in `rin_diagnosis.md`, not in any reference — no per-rin display format survives | **P2** |
| Phase 6 teva classification | MOVED | script `build_teva()` + `teva_types.md` | — |
| Phase 7 mode selection (confirm-or-override + A–F menu) | PRESERVED | SKILL.md "Reading modes" L123–146 | — |
| Phase 8A house-by-house logic | MOVED | SKILL.md Wave 1 (12 `unit-analyzer`) + references | — |
| **Phase 8A per-house output template** (main L347–362: `HOUSE [N]/Sign/Owner/Planets in/Aspects on/Key dynamics/Verdict/Reasoning`) | **LOST** | not in orchestration-notes, not in any reference — no per-house display format survives | **P2** |
| Phase 8A `LAL KITAB SYNTHESIS` box | PRESERVED (partial) | orchestration-notes "Synthesis weighting" + Phase 10 summary template | — |
| Phase 8B family chart + karaka/house table | MOVED | `family_chart.md` (has its own "Output Structure (Per Relative)") | — |
| Phase 8C Varshphal + year-ruler table | MOVED | script `build_varshphal()` + `varshphal.md` (full 63-row table + "Output Format Per Year") | — |
| Phase 8D timing protocol + hard rules | MOVED | script `build_timing_signals()` (raw signals) + `timing.md` Parts A–E | — |
| Phase 9 upaay tiers + 5 hard upaay rules | MOVED | `upaay_catalog.md` + orchestration-notes "Upaay output rules" (all 5 rules verified present) | — |
| Phase 10 final synthesis box | MOVED | orchestration-notes "Phase 10 summary template" | — |
| Critical Rules (12, Hard Enforcement) | PRESERVED | orchestration-notes "Hard methodological lines" — all 12 cross-checked present (slight reorder only) | — |
| Output Style list | MOVED | orchestration-notes "Output style" | — |

### New contradictions the refactor introduced

| # | Contradiction | Severity |
|---|---|---|
| **C1** | Phase 0 box option 3 still reads *"Not sure — show me what's possible **after baseline**"* (SKILL.md L53), but mode selection is now **Phase A step 2** (L72–74), which runs **before Wave 0 / the baseline**. In `main`, mode selection was Phase 7 — literally after the Phases 1–6 baseline, so the "after baseline" promise held. The refactor moved the menu pre-baseline but kept the old wording. | P2 |
| **C2** | Frontmatter `description` says *"User provides a pre-computed Vedic D1 chart"* (L7), but Phase A L67–69 + Wave 0 L80–81 now also **compute a D1 from raw birth data** via `chart-calculator`. The description was not updated to reflect the new capability. | P2 |
| **C3** | SKILL.md L30 / L94–95 say the baseline run *"produces … the four-signal timing-engine output"* and orchestration-notes L160 says Mode-F workers interpret *"the convergence engine's **top candidate years** from the baseline JSON"* — but the script emits **only the four raw signals** (`signal_1_maturation` … `signal_4_jupiter_sanctification`). There is **no event mapping, no filter application, no convergence scoring, and no ranked candidate-year list** in the JSON (the script comment at L811–812 admits this). The division of labour is sound (the script can't score without an event), but the SKILL.md / orchestration-notes wording overstates what the JSON contains. | P2 |

### Path / agent resolution

All `${CLAUDE_PLUGIN_ROOT}` paths and agent names in SKILL.md resolve:
- `scripts/compute_lalkitab_baseline.py` ✓ · `lib/chart_io.py` ✓
- agents `chart-calculator`, `chart-verifier`, `baseline-runner`, `unit-analyzer`, `synthesizer` — all 5 exist ✓
- references `orchestration-notes.md`, `pakka_ghar.md`, `aspects.md`, `rin_diagnosis.md`, `teva_types.md`, `family_chart.md`, `varshphal.md`, `timing.md`, `upaay_catalog.md` — all 9 exist ✓

Minor note (P2): the generic `chart-verifier` agent doc says for "Lal Kitab" to
render *"a D1 table … a D9 table"* — the **standard Parashari display**, which
conflicts with the LK **fixed-house frame** and the "no D9" rule. This is
resolved only because SKILL.md L88–89 explicitly passes the orchestration-notes
"Verification Display Format". The agent's generic Lal Kitab instructions are
still wrong on their own.

---

## Part 2 — Script methodology findings

Audited `compute_lalkitab_baseline.py` against `pakka_ghar.md`, `aspects.md`,
`rin_diagnosis.md`, `teva_types.md`, `varshphal.md`, `timing.md`.

### Verified CORRECT (no action)

- `PAKKA_GHAR` (L51–54) = `pakka_ghar.md` §1 — exact.
- `LK_EXALT_HOUSE` (L57–60) = §2 — exact. `LK_DEBIL_HOUSE` (L63–66) = §3 — exact.
- `LK_HOUSES_OWNED` (L69–73) = §4 — exact. `LK_FRIENDS`/`LK_ENEMIES` (L81–102) = §5 — all 9 rows exact.
- `BLIND_HOUSES = {2,6,8,12}` (L105) = §6; `thrives_despite_blind` handles the Rahu-12 / Ketu-6 exception.
- `LK_ASPECTS` (L109–113) = `aspects.md` table; inclusive-count verified (Saturn-in-1 → 3,7,10).
- `NEVER_REDEEMED` (L116–117) = `aspects.md` "Houses That Never Give Aspect Relief" — exact 6 pairs.
- Fixed-house re-map `fixed_house()` (L120–122) and buried/`dabba` rule (L218–224, "12th-from") — verified by hand on the test chart.
- **All 32 rin triggers** across the 6 rins (L351–491) — every configuration AND every Farman citation matches `rin_diagnosis.md` §§1–6 exactly. Pitri ×7, Matri ×7, Stri ×7, Kanya ×4, Bhratra ×5, Atma ×5.
- `YEAR_RULER` (L699–713) — all 63 rows match `varshphal.md` table exactly. `MAJOR_YEARS` (L715–723) and `MATURATION_AGE` (L790–793) — exact.
- `HOUSE_CYCLE` (L796–801) — matches `timing.md` Signal 3 (only the open-ended "84+" is finitised — see A10).
- Teva 2 (Lula), 4 (Sukhi), 5 (Dukhi), 6 (Rajyogi), 7 (Pujari) trigger logic — verified correct against `teva_types.md` §§2,4,5,6,7.

### WRONG / MISSING / APPROXIMATED

| # | Rule | Reference loc | Script loc | Verdict | Note |
|---|---|---|---|---|---|
| **W1** | Behra Teva — "3rd house compromised … or **3rd lord afflicted**" | `teva_types.md` §3 L55 | L608–610 | **WRONG** | Script tests `pakka["Mars"]["lk_dignity"]=="debilitated"`. The **3rd-house owner is Mercury**, not Mars (`LK_HOUSES_OWNED` Mercury=[3,6]; `HOUSE_OWNER[3]`=Mercury). Mars's *pakka ghar* is house 3, but the *lord* of house 3 is Mercury. The script is internally inconsistent — Bhratra-Rin trigger 5 (L466) correctly uses `lord_afflicted("Mercury")` for the same "3rd lord". Also uses narrow `=="debilitated"` instead of the `lord_afflicted()` helper. |
| **W2** | Andha Teva — luminary "afflicted (debilitated, sleeping, or **with Saturn/Rahu/Ketu**)" | `teva_types.md` §1 L12–13 | `afflicted()` L563–568, used L583 | **WRONG / APPROXIMATED** | Script's `afflicted()` = `dignity in (debilitated,enemy) or sleeping or buried`. It substitutes **enemy-house** + **buried** for the reference's "**with Saturn/Rahu/Ketu**" (conjunct/aspected by a malefic). These are different criteria — a luminary aspected by Saturn but not enemy-housed/buried is afflicted per reference, NOT per script (and vice-versa). The `_afflicts()` helper already does exactly "with Saturn/Rahu/Ketu" and should have been used. |
| **M1** | Jupiter's 5th-house aspect "is universally protective … **mitigates rin severity by one tier wherever it lands**" | `aspects.md` "Special Aspect Rules → Jupiter's 5th-house Aspect" L66–67 | `_rin_record()` L529–550 | **MISSING** | Severity is computed purely from trigger-count + compounders. No Jupiter-aspect mitigation is ever applied. This is a deterministic severity modifier that the script ignores entirely. |
| **M2** | Cross-rin escalation — "**2 rins → each one tier worse** than diagnosed individually" | `rin_diagnosis.md` "Cross-Rin Compounding Rules" L188–195 | `build_rin_diagnosis()` L493–505 | **MISSING** | Each rin's `severity` is computed in isolation by `_rin_record`. The script surfaces `active_count` / `debt_saturation` but never **escalates the per-rin `severity`** when ≥2 rins are active. Confirmed live: the test chart has **4 active rins** (debt-saturation), yet `bhratra_rin` is still `"Mild"`. This cascades — the un-escalated severities feed `blocked_house_pattern` and the teva classifier (`severe_rins`). |
| **M3** | Dead-pair rule — "A natal aspect on a sleeping planet does **not** count as awakening if both planets are in mutual aspect-isolation … they form a 'dead pair'" | `aspects.md` "Aspect-Triggered Awakening" L46–51 | `build_sleeping()` L273–299 | **MISSING** | Sleeping = `no co-tenant AND not aspected_by anything`. Two planets that aspect only each other and nothing else are both marked **awake**; the reference says they stay effectively dead. The script over-reports awake planets in that configuration (which then feeds teva + timing). |
| **A1** | Severity scale — "Severe = primary trigger + **two or more compounding factors**" | `rin_diagnosis.md` "Severity Scale" L8–12 | `_rin_record()` L538 | **APPROXIMATED** | Script adds `n_triggers >= 2 → Severe`. The reference's formal scale is one-trigger-+-N-compounders; only **Pitri Rin** §1 L24 explicitly says "multiple = severe". The script generalises that to all 6 rins and **skips Moderate** for the 2-trigger / 0-compounder case (confirmed: `matri_rin` = 2 triggers, 0 compounders → "Severe"). |
| **A2** | Neecha Bhanga — debilitation cancellation when "the lord of the house where debilitation occurs sits in its own pakka ghar" | `pakka_ghar.md` §3 L59; `aspects.md` L84 | `build_pakka_ghar()` L199–239 | **MISSING** | Script flags `debil_never_redeemed` (the 6 never-redeemed pairs) but never computes the **cancellation condition** for ordinary debilitations. A cancellable debilitation is still reported as a plain `"debilitated"` dignity. |
| **A3** | Pitri Rin compounding — three factors: Sun sleeping, Jupiter afflicted, **"10th house (karma) also damaged"** | `rin_diagnosis.md` §1 L32–35 | L376–378 | **MISSING** | `_rin_record` has only **2 compounder slots**. The 3rd factor ("10th house damaged") is dropped. (Severity often already Severe from triggers, so impact is limited — but the `compounding_factors` count is wrong.) |
| **A4** | Stri Rin compounding — "**Mercury also afflicted**" and "**Moon afflicted**" | `rin_diagnosis.md` §3 L97–99 | L429–431 | **APPROXIMATED** | Script checks only `Mercury == "debilitated"` (reference says *afflicted*, broader) and only `_afflicts("Saturn","Moon")` (reference says *Moon afflicted* by anything, not just Saturn). Both compounders are narrower than the reference. |
| **A5** | Bhratra Rin & Atma Rin compounding | `rin_diagnosis.md` §5 L137–158, §6 L162–184 (**no Compounding subsection in either**) | Bhratra L469–471, Atma L491 | **WRONG (fabricated)** | Script invents compounders the reference never defines: Bhratra gets `compound_a = Mercury debilitated`; Atma gets `compound_a = Jupiter sleeping`. Cosmetic side-effect: a **non-triggered** Atma Rin reports `compounding_factors: 1` (confirmed in output). |
| **A6** | Signal-1 maturation delivery — "**combust (within 10° of Sun) → maturation distorted**" | `timing.md` Signal 1 L33 | `build_timing_signals()` L816–835 | **MISSING** | The delivery-posture switch handles sleeping / exalted / own / debilitated / friend / enemy / neutral but **never computes combustion**. (Absolute longitude is recoverable from `sign`+`deg_in_sign`; the script just doesn't.) |
| **A7** | Ketu aspect — "5th, 7th, 9th (**some Farmans add 2nd**)" | `aspects.md` table L25 | `LK_ASPECTS` L112 | APPROXIMATED (acceptable) | Script uses `[5,7,9]`, silently dropping the optional 2nd-house aspect. Reference marks it optional, so defensible — but undocumented in the script. |
| **A8** | Teva — "name the **strongest first**" / "name the **dominant** teva" | `teva_types.md` L3, L6 | `build_teva()` L688 `dominant = matched[0]` | **APPROXIMATED** | "Dominant" = whichever teva check happens **first in code order** (Andha→Lula→Behra→Sukhi→Dukhi→Rajyogi→Pujari), not the strongest. A chart matching both Lula and Andha always reports Andha dominant regardless of actual strength. |
| **A9** | Mishra Teva — "classify as Mishra and **name the closest two**" with traits | `teva_types.md` §8 L157–167 | `build_teva()` L677–685 | **MISSING capability** | The Mishra branch returns a bare `{"teva":"Mishra","secondary":[],"all_matched":[]}`. Teva matching is pure boolean (full match or nothing) — there is **no partial-match scoring**, so the script can never name the closest two teva or list partial traits as §8 requires. |
| **A10** | House-cycle 2nd band for house 9 — "**84+**" (open-ended) | `timing.md` Signal 3 table L65 | `HOUSE_CYCLE[9]` L799 `(84,90)` | APPROXIMATED | Finitised to age 90. A native >90 would show house 9 inactive. Edge case. |
| **A11** | `planet_condition.rin_involved` attribution | — | `planet_condition()` L739–754 | APPROXIMATED | Uses case-insensitive **substring** match of the planet name against trigger `desc` text. Fragile: lord-only triggers that name no planet (e.g. Bhratra trigger 5 "Houses 3 and 11 empty AND their lords afflicted") will never attribute Mercury/Saturn as rin-involved. |
| **A12** | `planet_condition` content for Varshphal "How to Read a Year" Step 2 (houses P aspects, houses P owns) | `varshphal.md` L107–111 | `planet_condition()` L739–754 | APPROXIMATED | Emits `fixed_house / dignity / pakka / sleeping / buried / rin_involved` only — **not** the houses the ruler aspects or owns. The Varshphal worker must cross-reference `pakka_ghar.md` §4 + the aspect map itself. |

### Reference-vs-reference contradictions (pre-existing — unchanged from `main`)

These are flaws in the **reference files**, surfaced here because the script had
to choose a side. Per the audit instruction, the reference is the source of
truth — but here two references disagree.

| # | Contradiction | How the script handled it |
|---|---|---|
| **R1** | `timing.md` Signal 2 L42 claims "Sun: 10,19,28,37,46,55…" and Signal 4 L89 claims "Jupiter year-rulers (21,30,39,48,57,66)" — a clean 9-year recurrence. This **contradicts the `varshphal.md` year-ruler table** (age 28=Mars, 37=Rahu, 30=Rahu, 39=Venus, 48=Saturn…). | **Correct.** Script derives `JUPITER_YEARS` from `YEAR_RULER` (L807) and documents the discrepancy in a comment (L804–806). The `timing.md` prose is the wrong reference. |
| **R2** | Danger years: `timing.md` Filter 3 L153 = `{21,36,42,48,54,63}`; `upaay_catalog.md` §9 L273 = `{21,36,42,48,63}` (**no 54**). | Script `DANGER_YEARS` L725 = `{21,36,42,48,54,63}` — follows `timing.md` + `varshphal.md`'s "Major Year Markers" (which includes 54). `upaay_catalog.md` §9 is the outlier. Defensible, but the reference set is inconsistent. |
| **R3** | `varshphal.md` is internally inconsistent: the table L46 has **age 28 = Mars (single ruler)**, but "Multi-Planet Year Handling" L166 lists **28 as a two-ruler age**. | Script `YEAR_RULER[28]=["Mars"]` (L708) — follows the table (correct: the table is the authoritative data). |

### Baseline JSON field completeness

Every top-level key the SKILL.md / orchestration-notes / agents say workers
consume **is present**: `fixed_house_chart`, `pakka_ghar`, `aspect_map`,
`sleeping_planets`, `rin_diagnosis` (with Farman citations), `teva`,
`varshphal`, `timing_signals`. The **one shortfall** is C3 above — the JSON does
*not* contain the "convergence engine's top candidate years" that
orchestration-notes L160 promises; it contains raw signals only.

---

## Part 3 — Run results

All commands run from the repo root.

| Test | Command | Result |
|---|---|---|
| Birth-data path | `compute_lalkitab_baseline.py --datetime 1988-02-14T09:30:00 --tz Asia/Kolkata --lat 19.07 --lon 72.87 --age 37` | **EXIT 0**, valid JSON, 15 top-level keys |
| User-pasted-chart path | `chart_io.py --mode parashari --positions … --out lk_chart.json` then `compute_lalkitab_baseline.py --chart lk_chart.json --age 37` | **EXIT 0** both stages, valid JSON, no crash |
| No-`--age` path | same as row 1, `--age` omitted | **EXIT 0**; `varshphal` → `{"note":"no --age supplied…"}`; timing window degrades to `[1,16]` (graceful, no crash — but a Mode C/F reading needs `--age`) |

### Sanity checks (test nativity: 1988-02-14 09:30 IST, Mumbai 19.07/72.87, Lahiri)

| # | Value | Script output | Hand reasoning | Verdict |
|---|---|---|---|---|
| 1 | Birth Lagna (flavour) | Pisces | Sun in Aquarius, ~2.5 h after sunrise → asc advanced ~1¼ signs → Pisces/early Aries | ✓ plausible |
| 2 | Sun sign | Aquarius (fixed house 11) | Tropical Sun ~325° on Feb 14, − Lahiri ayanamsa ~23.7° ≈ 301° = Aquarius 1° | ✓ correct |
| 3 | Fixed-house re-map | all 9 planets = sign-index+1 | Jupiter Aries→1, Venus Pisces→12, Ketu Virgo→6, Sun Aquarius→11 … | ✓ all 9 correct |
| 4 | Dignities | Venus exalted (h12), Rahu own (h12), Ketu own (h6), Sun enemy (h11) | Venus exalt house=12 ✓; Rahu pakka=12 ✓; Ketu pakka=6 ✓; h11 owned by Saturn = Sun's enemy ✓ | ✓ correct |
| 5 | Jupiter sleeping | `sleeping: true` | Jupiter alone in house 1; no planet aspects house 1 (checked all 9 aspect sets) | ✓ correct |
| 6 | Varshphal year-ruler, age 37 | Rahu | `varshphal.md` table age 37 = Rahu | ✓ correct |
| 7 | Pitri Rin severity | Severe (triggers 1,2,5) | Saturn aspects Sun (h11), Rahu aspects Sun (h11), Saturn sits in h9 | ✓ triggers correct |

No crashes, no tracebacks, no malformed JSON on any path.

---

## Prioritised fix list

### P0 — wrong output
*(none — no fault produces a plainly invalid value)*

### P1 — methodology bugs that change diagnostic output

| # | Fix |
|---|---|
| **P1-1** (W1) | Behra Teva `third_bad` (L608–610): replace `pakka["Mars"]["lk_dignity"]=="debilitated"` with `lord_afflicted(HOUSE_OWNER[3])` — i.e. **Mercury**, the actual lord of house 3 — so it agrees with `HOUSE_OWNER` and with Bhratra-Rin trigger 5. |
| **P1-2** (W2) | Andha Teva `afflicted()` (L563–568): change the third clause from `dignity in (…enemy…) or buried` to the reference's "with Saturn/Rahu/Ketu" — `any(_afflicts(mal, p, planets, aspect_map) for mal in ("Saturn","Rahu","Ketu"))`. Keep `debilitated` and `sleeping`. |
| **P1-3** (M1) | Implement Jupiter's protective 5th-house aspect: in `_rin_record` (or a post-pass), if Jupiter's 5th-house aspect lands on a house involved in the rin, **drop that rin's severity one tier** (`aspects.md` L66–67). Requires passing the aspect map / Jupiter's aspected houses into the severity step. |
| **P1-4** (M2) | Implement cross-rin escalation in `build_rin_diagnosis` (after the per-rin pass): if `active_count >= 2`, bump **every active rin's `severity` up one tier**; if `>=3`, keep `debt_saturation` and prioritise Pitri/Matri (`rin_diagnosis.md` L188–195). Re-derive `blocked_house_pattern` from the escalated severities. |
| **P1-5** (M3) | In `build_sleeping`, after the first pass, detect **dead pairs**: if planet A and B aspect/co-tenant only each other and neither has any other contact, mark **both** sleeping (`aspects.md` L46–51). Add a `dead_pair_with` field for transparency. |

### P2 — missing capability / cosmetic / documentation

| # | Fix |
|---|---|
| **P2-1** (Part 1) | Restore the Phase 5 per-rin output template and the Phase 8A per-house output template — add them to `rin_diagnosis.md` and a house-reading reference (or `orchestration-notes.md`), matching how `family_chart.md` / `varshphal.md` / `timing.md` kept their per-unit templates. |
| **P2-2** (Part 1) | Restore the Phase 1 `CHART INPUT` formatted box in SKILL.md Phase A, or accept the prose form consistently and drop the Phase 0 box too. |
| **P2-3** (C1) | Fix the Phase 0 box option 3 wording — it promises the menu "after baseline" but the menu is Phase A (pre-baseline). Either re-word, or move the "not sure" full-menu to after Wave 0. |
| **P2-4** (C2) | Update the frontmatter `description` to mention the birth-data → computed-D1 path. |
| **P2-5** (C3) | Re-word SKILL.md L30/L94–95 and orchestration-notes L160 so they say the baseline emits **raw four-signal data**, not "the convergence engine's top candidate years". |
| **P2-6** (A1) | Either restrict `n>=2 → Severe` to Pitri Rin only, or add the rule to the shared Severity Scale in `rin_diagnosis.md` so the script's generalisation is reference-backed. Consider a Moderate path for 2-trigger / 0-compounder. |
| **P2-7** (A2) | Implement Neecha Bhanga: compute whether the lord of a debilitation house sits in its own pakka ghar; add a `debil_cancelled` boolean to the `pakka_ghar` block. |
| **P2-8** (A3) | Add Pitri Rin's 3rd compounding factor ("10th house damaged") — needs a 3rd compounder slot or a list-based `_rin_record`. |
| **P2-9** (A4) | Widen Stri Rin compounders: `Mercury afflicted` (use `lord_afflicted("Mercury")`, not just debilitated) and `Moon afflicted` by any malefic, not only Saturn. |
| **P2-10** (A5) | Remove the fabricated Bhratra / Atma compounders, or add the corresponding "Compounding" subsections to `rin_diagnosis.md` §5/§6 so they are reference-backed. Fix the `compounding_factors: 1` shown on non-triggered rins. |
| **P2-11** (A6) | Compute combustion for Signal-1 delivery posture (reconstruct absolute longitude from `sign`+`deg_in_sign`, 10° orb to the Sun) per `timing.md` L33. |
| **P2-12** (A8/A9) | Give `build_teva` a partial-match score so "dominant" = strongest, and so Mishra can name the closest two teva with traits per `teva_types.md` §8. |
| **P2-13** (A11/A12) | Make `planet_condition` attribution structural (tag each trigger with the planets it implicates instead of substring-matching), and add the ruler's aspected/owned houses for the Varshphal worker. |
| **P2-14** | Minor: `build_teva` recomputes `build_aspect_map` 3× (L594/L651/L667) — pass the already-built map in. Ketu's optional 2nd aspect (A7) and the house-9 "84+" cap (A10) — document the choices. Fix the `baseline-runner` agent gloss template, which references a "running dasha" that does not exist for Lal Kitab. |

### Reference-file fixes (not script)

- **R1** — correct `timing.md` Signal 2 L42 and Signal 4 L89 so the example recurrences match the `varshphal.md` year-ruler table (or delete the misleading explicit lists).
- **R2** — reconcile the danger-year set between `timing.md` L153 and `upaay_catalog.md` §9 L273 (add 54 to the upaay catalog, or document why it differs).
- **R3** — reconcile `varshphal.md`: either age 28 is a single-ruler year (table L46) or a two-ruler year (L166) — pick one.
