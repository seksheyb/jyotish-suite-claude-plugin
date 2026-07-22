# AUDIT RE-VERIFICATION (item C) — 2026-07-23


## vedic-astro — {'fixed': 15, 'moved-ok': 1, 'not-applicable': 1}
Of the audit's 15 prioritized findings (1 P0, 5 P1, 9 P2) plus the 3 named contradictions, all 18 are FIXED in the current committed code — verified both by reading the current files and by actually running compute_vedic_baseline.py (birth 1990-05-15 10:30 IST, 28.6139N/77.2090E; reading-moment 2026-01-01) on both the ephemeris path and the pasted-chart path. The one still-live item is the Rahu/Ketu 5th/9th special-aspect omission, which the original audit itself flagged as a deliberate, defensible convention rather than a bug, so it remains unchanged by design (not-applicable). No other audit-flagged gap survives; the headline P0 (dasha frozen at birth) is unambiguously fixed — the running dasha in a live run correctly resolved to Rahu MD / Venus AD / Mercury PD as of the 2026 reading date, not the 1988-era birth quartet the old code produced.


## kp-natal — {'live': 11, 'fixed': 5, 'partially-fixed': 1}
Of the audit's 17 distinct findings (P1=6, P2=11), 6 are now fixed (all doc/wiring items hand-fixed this session), 1 is partially-fixed, and 10 remain live — including 4 of the original 6 P1s. Live P1s were reverified by running compute_kp_natal_baseline.py on the pinned nativity (1990-05-15 10:30 IST, 28.6139N/77.2090E, reading 2026-01-01 09:00 IST): retrograde Jupiter is explicitly flagged "weakened/excluded" in retrograde_check yet still appears in final_rp; dasha.running still returns the at-birth quartet (Sun MD 1988-1994) instead of the 2026 quartet (only obtainable via an explicit, unwired --target-datetime flag); the RP node-inclusion rule still checks only the sign-lord condition; and no combust/sandhi/gandanta/mrityu_bhaga flags are emitted at all (a jp.degree_flags() helper now exists in lib but still uses Parashari combustion orbs and a 1° sandhi window — wiring it in naively would reproduce the exact trap the audit warned about). The headline still-open issue is the missing "current dasha" surfacing plus the cosmetic-only retrograde/RP-node logic, since both directly undermine the event-timing verdict's stated methodology.

- **[P2] Three lost KP output templates (per-cusp box, LIFE THEMES box, VERDICT box) not restored** (live)
  - fix: Add the three box templates (per-cusp HOUSE box, LIFE THEMES synthesis box, VERDICT box) to methodology.md's Step 8 and life-reading section, and have SKILL.md instruct unit-analyzer/synthesizer to fill those exact layouts for kp-natal. Downgraded from P1 since prose descriptions do functionally cover the same content — this is presentation-format drift, not a correctness gap.
  - touches: skills/kp-natal/references/methodology.md, skills/kp-natal/SKILL.md (doc-only, no lib/ or scripts/ touch)
- **[P1] RP retrograde exclusion computed but never applied to final_rp** (live)
  - fix: After computing retro_check, filter dedup to drop any planet marked excluded (retrograde AND depositor not in dedup) before assigning final_rp, so final_rp actually reflects the exclusion verdict.
  - touches: scripts/compute_kp_natal_baseline.py only (compute_ruling_planets function) — no lib/ touch, contained to the KP script.
- **[P1] dasha.running is the at-birth quartet, not the quartet running at the reading moment; nothing auto-wires the reading datetime** (live)
  - fix: In scripts/compute_kp_natal_baseline.py, default --target-datetime to now() when omitted so running_at_target is always populated, and have SKILL.md/baseline-runner explicitly pass the reading datetime for Wave 0. Do not touch lib/ephemeris.py's _vim_dasha/kp_natal_chart signature — that birth-anchored 'running' field is reused by other schools (parashari_natal_chart) and changing its meaning there would be a shared-lib break.
  - touches: scripts/compute_kp_natal_baseline.py + skills/kp-natal/SKILL.md wiring. Explicitly avoid touching lib/ephemeris.py — _vim_dasha() and its birth-anchored 'running' semantics are shared across kp-natal and parashari-style schools; changing the default there is contention-sensitive.
- **[P1] RP node-inclusion rule only checks sign-lord condition (missing conjunct-with-RP and star-lord-of-RP conditions)** (live)
  - fix: Add the two missing conditions to compute_ruling_planets: a node also joins RP if it's within ~3° conjunction of any planet already in dedup, or if any planet in dedup is the node's star-lord (nakshatra lord). Localized to the KP script; reuses existing jp.full_lord_chain/jp.get_sign, no lib/ signature changes needed.
  - touches: scripts/compute_kp_natal_baseline.py only — no lib/ touch.
- **[P1] No KP degree flags emitted (combust/sandhi/gandanta/mrityu_bhaga)** (live)
  - fix: In compute_kp_natal_baseline.py, add KP-specific flat-orb checks computed locally (combust: |planet_lon - sun_lon| <= 8.5°; sandhi: deg_in_sign < 0.5 or >= 29.5°) for the 9 planets and 12 cusps. Safe to reuse jp.gandanta() (already 3°20' zones, KP-correct) and jp.mrityu_bhaga() (table-driven, orb-parametrized) as-is. Do NOT call jp.combustion()/jp.sandhi() or add a KP override into lib/jyotish_primitives.py without also auditing every other caller of those two functions (vedic/bnn/jaimini use the Parashari orbs correctly) — implement the KP flat-orb versions locally in the script instead of touching the shared lib functions, to avoid contention.
  - touches: scripts/compute_kp_natal_baseline.py (new local functions) — reuses jp.gandanta/jp.mrityu_bhaga read-only; explicitly avoid modifying lib/jyotish_primitives.py's combustion()/sandhi() since those are shared by vedic-astro, bnn, jaimini, lal-kitab with correct Parashari semantics.
- **[P2] 'optionally outer planets' dropped from Chart Intake Format prompt** (live)
  - fix: Add a line to the Chart Intake Format's Option 1 bullet list: 'Outer planets (Uranus/Neptune/Pluto) — optional, displayed but not used in core KP analysis.'
  - touches: skills/kp-natal/references/orchestration-notes.md (doc-only).
- **[P2] Explicit STOP instruction in methodology.md Step 2 softened to prose** (live)
  - fix: Add an explicit imperative to Step 2: 'If CSL signifies the negative set only, STOP — deliver the verdict "will not fructify in this life" and do not proceed to significator analysis for this house.'
  - touches: skills/kp-natal/references/methodology.md (doc-only).
- **[P2] Node-amplifies-conjunct-planet rule (reverse direction) not implemented in compute_significators** (live)
  - fix: In compute_significators, for each node, for each conjunct planet, add the node's depositor's owned-houses and the node's own occupied/owned houses to that planet's significator set (or emit a separate 'amplified_by_node' annotation per planet so the interpretive layer can apply it without inventing the rule).
  - touches: scripts/compute_kp_natal_baseline.py only — no lib/ touch.
- **[P2] Day-lord weekday computed from UTC calendar date instead of local date at the place** (live)
  - fix: Convert sr (UT Julian Day) to local civil date using the location's tz before taking .weekday(), e.g. compute local offset from lon or accept a tz parameter and localize sr_dt before extracting weekday.
  - touches: lib/ephemeris.py day_lord() — FLAGGED: this is shared lib code used by both kp-natal and kp-horary baselines; a fix here is contention-sensitive since both schools' RP Day-Lord calculations depend on it and should be regression-tested together (tests/golden/kp_natal.json and kp_horary.json).
- **[P2] Fruitful vs barren significator gate not pre-computed (no sub-lord → houses-signified reverse map)** (live)
  - fix: Add a `fruitful_barren` block to the baseline: for every planet appearing as a significator anywhere, look up its sub_lord's own significator memberships and tag fruitful (sub_lord signifies the question's positive set) or barren (signifies negative set) once the house-combination context is known — or, since house sets are question-dependent, at minimum emit a generic 'sub_lord → houses it signifies (all 4 levels)' reverse index so downstream workers don't have to invert it by hand.
  - touches: scripts/compute_kp_natal_baseline.py only — no lib/ touch.
- **[P2] Dead `owned` dict in compute_significators** (live)
  - fix: Delete the `owned` dict construction (lines 83-88) — it has no reader.
  - touches: scripts/compute_kp_natal_baseline.py only — trivial, no lib/ touch.
- **[P2] strongest_rp hardcoded to Lagna Sub Lord — internal inconsistency between ruling-planets.md prose and its own example when a node qualifies** (partially-fixed)
  - fix: Decide the rule explicitly (KP convention generally: a qualifying node does become the 'agent' and can outrank Lagna Sub Lord) and either implement that in compute_ruling_planets or add one sentence to ruling-planets.md's 'Using RP in the verdict' section stating the current code's convention (Lagna Sub Lord is always strongest) so it's a documented choice rather than a silent default.
  - touches: scripts/compute_kp_natal_baseline.py (if changing behavior) and/or references/ruling-planets.md (if just documenting current behavior) — no lib/ touch either way.

## kp-horary — {'fixed': 3, 'live': 13, 'not-applicable': 1}
Of the 15 numbered items in the audit's prioritized fix list, 3 are now fixed by this session's doc work (commands/kp-horary.md path fix, 249-table.md stale path, house-combinations.md now documents the three previously-inferred categories explicitly) and 12 are still live in the current committed code — including all 6 methodology/script gaps from Part 2 (planet `house` field, KP combustion, sandhi flag, Rahu/Ketu conjunct-by-sign, hardcoded strongest_rp, retrograde-depositor ordering, dead `primary` param, dead node loop) which were never touched because the refactor session worked on skills/agents/scripts orchestration, not the deterministic baseline script itself. The headline still-open issue: `ephemeris.ALL_PLANETS` computes only the 9 grahas while `orchestration-notes.md` (critical rule 6 + the Verification Display Format) still mandates showing Uranus/Neptune/Pluto — an unfulfillable instruction baked into the very reference file the refactor rewrote this session. A close second: `references/ruling-planets.md` now actively asserts that "combustion weakening... [is] computed by `compute_kp_horary_baseline.py`" — which is false and is a new (session-introduced) documentation inaccuracy, not merely an old unfixed gap.

- **[P1] Planet `house` number absent from the baseline JSON** (live)
  - fix: In lib/ephemeris.py kp_horary_chart (after line 320, inside the `for p, info in raw.items()` loop), add `chain["house"] = jp.house_of(jp.get_sign(info["longitude"])[0], lagna_si)` where lagna_si is the sign-index of `horary_lagna` (computed once before the loop, mirroring `_sign_idx` in compute_kp_horary_baseline.py). Alternatively add it in the calling script instead, to avoid touching the shared assembler.
  - touches: lib/ephemeris.py (kp_horary_chart function only — shared file, but this function is horary-specific and not called by other schools, so contention risk is low) OR scripts/compute_kp_horary_baseline.py (safer: keep the shared lib untouched and post-process `chart['planets']` in build_baseline())
- **[P1] KP combustion (8.5° orb) never computed for horary** (live)
  - fix: Add a KP-specific combustion pass to compute_kp_horary_baseline.py using an inline uniform 8.5° orb constant (do not reuse jp.COMBUSTION_ORBS — those are Parashari 10-17° orbs used by other schools). Emit a `combust: true/false` flag per planet in the baseline JSON. Then correct ruling-planets.md:27-28 to stop claiming combustion is computed until this lands (or once it lands, scope the claim to the new per-planet flag, not RP-set weighting which still isn't implemented).
  - touches: scripts/compute_kp_horary_baseline.py (new local combustion pass, no shared-lib changes needed) + skills/kp-horary/references/ruling-planets.md (correct the false claim)
- **[P1] Chart-Lagna sandhi flag (0°30') missing** (live)
  - fix: Add a horary-specific sandhi check directly in compute_kp_horary_baseline.py (or a small local helper) using a 0.5° band, and attach it to horary_lagna in the baseline output. Do not repurpose the shared jp.sandhi() (1.0° band) since other schools may depend on that convention — keep the KP-horary 0.5° threshold local to this script.
  - touches: scripts/compute_kp_horary_baseline.py (local 0.5° check; avoid modifying lib/jyotish_primitives.py's shared sandhi() to prevent affecting other schools)
- **[P1] Uranus/Neptune/Pluto display instruction contradicts the 9-graha ephemeris** (live)
  - fix: Drop the U/N/P lines from orchestration-notes.md (critical rule 6 and the Verification Display Format line) — recommended, since SKILL.md's intro and the planets table both already commit to a 9-planet system and no script anywhere in the plugin computes outer planets. Do not add U/N/P to lib/ephemeris.py ALL_PLANETS — that list is shared across all six schools and would ripple into kp-natal, vedic-astro, etc.
  - touches: skills/kp-horary/references/orchestration-notes.md (doc-only fix, recommended). Do NOT touch lib/ephemeris.py ALL_PLANETS — shared across every school's chart builder.
- **[P2] baseline-runner.md over-claims a generic --chart flag for kp_horary** (live)
  - fix: Add a one-line carve-out in baseline-runner.md: 'kp_horary has no --chart ingestion path — it always takes --number/--datetime/--tz/--lat/--lon/--question; a horary chart cannot be built from a pasted natal chart.' Downgraded from the audit's P1 to P2 because baseline-runner's own instructions (step 2: 'If it errors, report the exact stderr and stop') already contain this failure safely — a wasted dispatch, not a silent wrong answer.
  - touches: agents/baseline-runner.md (doc-only)
- **[P2] Chart-Lagna `sign` field not in horary_lagna dict** (live)
  - fix: Add `sign` and `longitude_dms` to the info dict returned by ephemeris.horary_number_to_lagna (lib/ephemeris.py:140-145), computed via jp.get_sign(mid) — small, additive change local to this function.
  - touches: lib/ephemeris.py (horary_number_to_lagna — shared file, but the function itself is horary-only, so low collision risk)
- **[P2] Rahu/Ketu 'conjunct' implemented as same-sign, not within-orb** (live)
  - fix: Replace the same-sign membership test with a degree-orb test, e.g. `abs(angular separation) <= 8-10°` computed from each planet's absolute longitude, to match the reference's 'conjunct' meaning.
  - touches: scripts/compute_kp_horary_baseline.py only
- **[P2] strongest_rp hardcoded to Lagna Sub Lord regardless of retrograde-exclusion** (live)
  - fix: Derive strongest_rp from the first entry of final_rp (or from retrograde_check) instead of factors[0][1] directly, so an excluded planet is never reported as strongest.
  - touches: scripts/compute_kp_horary_baseline.py only
- **[P2] Retrograde-depositor check uses pre-exclusion dedup list, not the surviving set** (live)
  - fix: Iterate the exclusion pass to a fixed point, or check `depositor in retained` instead of `depositor in dedup`, so a retrograde depositor that was itself excluded doesn't retain its dependent.
  - touches: scripts/compute_kp_horary_baseline.py only
- **[P2] Dead `primary` parameter in _csl_verdict** (live)
  - fix: Remove the unused `primary` parameter from the signature and its call site.
  - touches: scripts/compute_kp_horary_baseline.py only
- **[P2] Dead node-conjunction loop in compute_significators** (live)
  - fix: Remove the redundant loop (lines 160-163) for clarity; behavior is unaffected either way.
  - touches: scripts/compute_kp_horary_baseline.py only
- **[P2] chart-verifier.md input contract doesn't name the kp-horary baseline-JSON case** (live)
  - fix: Add a brief Case C (or amend Case A's wording) noting that for kp_horary — and any school without a chart-calculator step — the input is the baseline-runner's output JSON directly.
  - touches: agents/chart-verifier.md (doc-only)
- **[P2] Mrityu Bhaga / Pushkara / Gandanta degree flags not emitted for horary** (live)
  - fix: If desired, wire the existing jp.gandanta/mrityu_bhaga/pushkara_* helpers (already shared and used elsewhere) into compute_kp_horary_baseline.py's per-planet output — no new shared-lib code needed, just calls from the horary script.
  - touches: scripts/compute_kp_horary_baseline.py (call existing shared lib/jyotish_primitives.py helpers — no lib changes needed)

## jaimini-astrology — {'live': 7, 'fixed': 3}
Of 11 distinct findings audited, 3 P2 reference-hygiene items are genuinely FIXED (Chara Dasha years prose, one-way-aspect list, worked-example ranking order in computation.md / jaimini-drishti.md). Everything else is UNCHANGED and still live: `git diff` confirms `scripts/compute_jaimini_baseline.py` and `lib/jyotish_primitives.py` have zero commits touching them since the pre-refactor audit baseline, and the Wave-0/orchestration-notes.md "Verification Display Format" section is byte-identical too. I reproduced every live script bug by running the pinned test chart (1990-05-15 10:30 IST, 28.6139N/77.2090E, target 2026-01-01): the Pushkara Navamsa table is still wrong for all 12 signs (confirmed Leo 8° flags False when it should be True — the exact case the audit cited), Chara Dasha Antardasha is still completely absent from the JSON (`chara_dasha.running` has no antardasha field, while methodology.md still requires it at lines 123/282-287/323), and the dual-lord tiebreak still measures Kendra/Trikona from the lorded sign instead of the Lagna — and on this chart it is decisive (flips the Jaimini lord of Scorpio from the correct Ketu to the wrong Mars), so I'm escalating that one from P1 to P0 per the audit's own stated escalation condition. The headline still-open issue is the baseline-display contradiction: `SKILL.md` Wave 0 step 2 still dispatches `chart-verifier` to render the full "JAIMINI BASELINE:" block (Karakas/Swamsha/Arudhas/Chara Dasha) before step 3 even runs `baseline-runner`, and `chart-verifier.md` still describes an agent that cannot compute any of that — this section of both files is textually unchanged from the pre-refactor audit state.

- **[P1] Verification-display vs baseline-display contradiction (chart-verifier told to render Jaimini baseline before baseline-runner computes it)** (live)
  - fix: Split 'Verification Display Format' into (a) a chart-only display (D1 table, flag legend, D9 table, dasha balance) rendered by chart-verifier at Wave 0 step 2, and (b) a separate 'Jaimini Baseline Display' (Karakas, War, Close-degree, Swamsha, Karakamsha, Arudhas, Argala, Chara Dasha) rendered at Wave 0 step 4 from baseline-runner's JSON. Update SKILL.md Wave 0 steps 2 and 4 and conduct rules 1-2 in orchestration-notes.md accordingly.
  - touches: skills/jaimini-astrology/SKILL.md, skills/jaimini-astrology/references/orchestration-notes.md, agents/chart-verifier.md — all skill-scoped, no shared lib/ touch
- **[P0] Pushkara Navamsa table wrong for all 12 signs** (live)
  - fix: Rebuild PUSHKARA_NAVAMSA in lib/jyotish_primitives.py:97-110 to the classical zones (verify against a second astrological source, since the pre-refactor degree-flags.md, now deleted from docs, listed Aries with only one zone — confirm whether that asymmetry is itself an error before transcribing).
  - touches: lib/jyotish_primitives.py — SHARED LIB, contention risk: also used by vedic-astro and bnn-astrology skills per the audit's own note; coordinate before editing
- **[P1] Chara Dasha Antardasha never computed** (live)
  - fix: Implement Step 5 per computation.md:128-134 (already correctly documented, unlike the pre-fix prose): within each Mahadasha Rasi, Antardasha starts from the same Rasi, same direction, each lasting (Antardasha-Rasi-years/12) x Mahadasha-years; expose the running Antardasha inside chara_dasha.running so the verification display and methodology Section 4B/5 Step 7 can be satisfied.
  - touches: scripts/compute_jaimini_baseline.py (compute_chara_dasha, ~lines 290-337 plus find_running_dasha) — jaimini-specific, no shared lib/ touch
- **[P0] Dual-lord tiebreak (Scorpio/Aquarius) measures Kendra/Trikona from the lorded sign, not the Lagna** (live)
  - fix: Pass lagna_sign_idx into jaimini_sign_lord and change line 260 to `house = jp.count_signs(lagna_sign_idx, psi)`, per computation.md:80. Propagate the parameter through chara_dasha_years and compute_chara_dasha's call sites.
  - touches: scripts/compute_jaimini_baseline.py (jaimini_sign_lord ~238-268, chara_dasha_years ~271-287, compute_chara_dasha call site ~313) — jaimini-specific, no shared lib/ touch
- **[P2] Argala pre-map covers only AL/UL/A10/Swamsha/Lagna, not all named Arudhas (A2-A9, A11)** (live)
  - fix: Extend the argala pre-map loop (compute_jaimini_baseline.py:436-445) to include A2-A9 and A11 alongside AL/UL/A10/Swamsha/Lagna.
  - touches: scripts/compute_jaimini_baseline.py — jaimini-specific, no shared lib/ touch
- **[P2] 2°-5° close-contention degree flag never computed** (live)
  - fix: Add a close-contention check (2°-5° same-sign gap among WAR_PLANETS, or per methodology.md:34's exact scope) alongside planetary_war() in jyotish_primitives.py, and surface it in build_planet_block's output.
  - touches: lib/jyotish_primitives.py — SHARED LIB, contention risk (same file as the Pushkara Navamsa fix, also used by vedic-astro/bnn-astrology); plus scripts/compute_jaimini_baseline.py (build_planet_block) to surface it
- **[P2] planets block omits nakshatra/pada/house; chara_karakas rows don't inline degree_flags** (live)
  - fix: Add nakshatra/pada (via jp.get_nakshatra/get_pada, already in the shared lib) and house-from-Lagna (via jp.house_of) to build_planet_block; inline each Karaka's degree_flags by joining from the planets block when assembling chara_karakas.
  - touches: scripts/compute_jaimini_baseline.py (build_planet_block ~358-379, compute_chara_karakas ~85-112) — jaimini-specific; calls into existing lib/jyotish_primitives.py helpers but requires no lib/ edits

## bnn-astrology — {'live': 1}
test

- **[None] test** (live)
  - fix: 
  - touches: 

## lal-kitab — {'fixed': 3, 'live': 25}
Of the 29 distinct findings in AUDIT-lal-kitab.md, 3 are fully fixed (the C1/C2/C3 SKILL.md-restructuring contradictions — mode selection genuinely moved post-baseline, the frontmatter now documents the birth-data path, and the timing-signal wording no longer overclaims a convergence ranking). All 21 script-methodology findings (W1, W2, M1, M2, M3, A1–A12, plus the build_aspect_map recompute) are still live and unchanged — compute_lalkitab_baseline.py is byte-for-byte the same file the audit reviewed (confirmed by matching line numbers and by running the script against a live test chart plus two synthetic charts, which reproduced W2's false-positive Andha Teva and M2's un-escalated Pitri Rin severity in real output). The two lost per-unit output templates (P2-1), the Phase-A CHART INPUT box (P2-2), the shared chart-verifier agent's stray D9/dasha instruction for Lal Kitab, the shared baseline-runner agent's "running dasha" gloss default, and all three reference-vs-reference contradictions (R1–R3) are also still live and untouched by this session's hand-fixes. The headline still-open issue is the cross-rin severity escalation (M2): a chart with 3 active rins (debt-saturation) still reports Pitri Rin as "Mild" instead of escalated, which cascades into teva and the blocked-house pattern.

- **[P2] P2-1 — per-rin and per-house output templates still lost** (live)
  - fix: Add a "Per-Rin Output Format" block to rin_diagnosis.md and a "Per-House Output Format" block to a house-reading reference (or orchestration-notes.md), mirroring family_chart.md's "Output Structure (Per Relative)".
  - touches: skills/lal-kitab/references/rin_diagnosis.md + skills/lal-kitab/references/orchestration-notes.md (Lal-Kitab-specific docs only; no lib/ or script involvement)
- **[P2] P2-2 — Phase A CHART INPUT box still collapsed to prose** (live)
  - fix: Either add a formatted CHART INPUT box to Phase A matching Phase 0's style, or intentionally drop Phase 0's box too for consistency.
  - touches: skills/lal-kitab/SKILL.md (Lal-Kitab-specific; no shared files)
- **[P2] chart-verifier agent still tells Lal Kitab to render a D9 + dasha balance** (live)
  - fix: Carve Lal Kitab out of that bullet in chart-verifier.md (its own line: D1 fixed-house table only, no D9, no dasha) since this agent is shared across all 5 schools.
  - touches: agents/chart-verifier.md — SHARED agent used by vedic/bnn/jaimini/kp/lalkitab; flag for contention, changes must not regress the other 4 schools' D9/dasha display
- **[P1] W1 (P1-1) — Behra Teva tests Mars dignity instead of Mercury (actual 3rd lord)** (live)
  - fix: Replace pakka["Mars"]["lk_dignity"]=="debilitated" with lord_afflicted(HOUSE_OWNER[3]) (Mercury), matching Bhratra-Rin trigger 5's use of the same helper for the same lord.
  - touches: scripts/compute_lalkitab_baseline.py L606-617 (build_teva, Behra Teva block) — Lal-Kitab-specific script, no lib/ involvement
- **[P1] W2 (P1-2) — Andha Teva afflicted() substitutes enemy/buried for "with Saturn/Rahu/Ketu"** (live)
  - fix: Replace the enemy/buried clause with any(_afflicts(mal, p, planets, aspect_map) for mal in ("Saturn","Rahu","Ketu")), keeping debilitated and sleeping.
  - touches: scripts/compute_lalkitab_baseline.py L563-568, used at L583 — Lal-Kitab-specific script only
- **[P1] M1 (P1-3) — Jupiter's 5th-house rin-mitigation aspect never implemented** (live)
  - fix: After computing each rin's raw severity, check if Jupiter's 5th-house aspect (aspected_houses("Jupiter", house["Jupiter"])) lands on a house implicated in that rin's triggers, and if so downgrade severity one tier (Severe->Moderate->Mild).
  - touches: scripts/compute_lalkitab_baseline.py — build_rin_diagnosis()/_rin_record() (L326-550), Lal-Kitab-specific, no lib/ changes needed
- **[P1] M2 (P1-4) — cross-rin severity escalation never implemented** (live)
  - fix: After the per-rin pass, if active_count>=2 bump every active rin's severity one tier (Mild->Moderate->Severe, capped at Severe); if active_count>=3 keep debt_saturation and note Pitri/Matri priority. Re-derive blocked_house_pattern from the escalated severities.
  - touches: scripts/compute_lalkitab_baseline.py L493-505 (build_rin_diagnosis, after the per-rin pass) — Lal-Kitab-specific script only
- **[P1] M3 (P1-5) — dead-pair sleeping-planet exception never implemented** (live)
  - fix: After the first sleeping pass, for each pair (p,q) where aspected_by[p]==[q] and aspected_by[q]==[p] (and no co-tenants), re-mark both sleeping and add a dead_pair_with field.
  - touches: scripts/compute_lalkitab_baseline.py L273-299 (build_sleeping) — Lal-Kitab-specific script only
- **[P2] A1 — Severity scale generalized from Pitri-only to all 6 rins** (live)
  - fix: Either restrict n>=2->Severe to Pitri Rin only (per the reference's actual scope) or add the generalization explicitly to rin_diagnosis.md's shared Severity Scale so it's reference-backed; add a Moderate branch for 2-trigger/0-compounder.
  - touches: scripts/compute_lalkitab_baseline.py L529-550 (_rin_record) + references/rin_diagnosis.md — Lal-Kitab-specific
- **[P2] A2 — Neecha Bhanga (debilitation cancellation) never computed** (live)
  - fix: Add a debil_cancelled boolean: for a planet debilitated in house h, check if HOUSE_OWNER[h] sits in its own pakka_ghar; if so flag cancellation.
  - touches: scripts/compute_lalkitab_baseline.py L199-239 (build_pakka_ghar) — Lal-Kitab-specific script only
- **[P2] A3 — Pitri Rin's 3rd compounding factor (10th house damaged) dropped** (live)
  - fix: Extend _rin_record to accept a list of compounders (or add a 3rd positional arg) and add a 10th-house-damage check (e.g. Saturn debilitated/afflicted while sitting in house 10, or house 10 empty+lord afflicted).
  - touches: scripts/compute_lalkitab_baseline.py L376-378 + L529-550 (_rin_record signature) — Lal-Kitab-specific script only
- **[P2] A4 — Stri Rin compounders narrower than reference (Mercury/Moon affliction)** (live)
  - fix: Replace with lord_afflicted("Mercury") and a broader Moon-afflicted check (any of Saturn/Rahu/Ketu via _afflicts, or debilitated/sleeping).
  - touches: scripts/compute_lalkitab_baseline.py L429-431 — Lal-Kitab-specific script only
- **[P2] A5 — Bhratra/Atma Rin compounders fabricated (no reference basis)** (live)
  - fix: Remove the fabricated compounders (revert to 0 compound slots) or add the corresponding Compounding subsections to rin_diagnosis.md §5/§6 so the script becomes reference-backed either way.
  - touches: scripts/compute_lalkitab_baseline.py L469-471, L491 + references/rin_diagnosis.md — Lal-Kitab-specific
- **[P2] A6 — Signal-1 maturation delivery never computes combustion** (live)
  - fix: Reconstruct absolute longitude per planet (sign index * 30 + deg_in_sign), compute angular distance to Sun's longitude, and if < 10 deg mark delivery as combust-distorted (unless the planet is the Sun itself).
  - touches: scripts/compute_lalkitab_baseline.py L810-835 (build_timing_signals) — Lal-Kitab-specific script only
- **[P2] A7 — Ketu's optional 2nd-house aspect silently dropped (documented as acceptable)** (live)
  - fix: Add a one-line code comment noting the 2nd-house Ketu aspect is an optional Farman variant intentionally excluded, so the omission reads as a decision rather than an oversight.
  - touches: scripts/compute_lalkitab_baseline.py L109-113 (LK_ASPECTS) — Lal-Kitab-specific, cosmetic only
- **[P2] A8 — teva "dominant" = first code-order match, not strongest** (live)
  - fix: Add a coarse strength score per matched teva (e.g. count of contributing affliction factors) and sort matched by that score descending before taking matched[0].
  - touches: scripts/compute_lalkitab_baseline.py L557-691 (build_teva) — Lal-Kitab-specific script only
- **[P2] A9 — Mishra branch has no partial-match scoring or trait naming** (live)
  - fix: Add a partial-match score per teva archetype (fraction of that archetype's trigger conditions satisfied) and, on full Mishra fallback, report the top-2 partial scorers with their matched/unmatched conditions.
  - touches: scripts/compute_lalkitab_baseline.py L557-691 (build_teva) — Lal-Kitab-specific script only
- **[P2] A10 — House-cycle 2nd band for house 9 finitized to 90 instead of open-ended 84+** (live)
  - fix: Either raise the cap to a very high number (e.g. 150) to effectively behave as open-ended, or special-case age>=84 as "active" for house 9 regardless of upper bound.
  - touches: scripts/compute_lalkitab_baseline.py L796-801 (HOUSE_CYCLE) — Lal-Kitab-specific script only
- **[P2] A11 — planet_condition.rin_involved uses fragile substring matching** (live)
  - fix: Tag each trigger dict at creation time with an explicit "planets": [...] list instead of relying on desc-substring matching; have planet_condition read that list directly.
  - touches: scripts/compute_lalkitab_baseline.py L349-505 (all _rin_record trigger-building blocks) + L739-754 (planet_condition) — Lal-Kitab-specific script only
- **[P2] A12 — planet_condition omits houses the ruler aspects/owns for Varshphal Step 2** (live)
  - fix: Add "aspected_houses": aspected_houses(planet, pakka[planet]["fixed_house"]) and "owned_houses": LK_HOUSES_OWNED[planet] to the returned dict.
  - touches: scripts/compute_lalkitab_baseline.py L739-754 (planet_condition) — Lal-Kitab-specific script only
- **[P2] P2-14 (misc) — build_aspect_map recomputed 3x inside build_teva** (live)
  - fix: Add an aspect_map parameter to build_teva() and pass the already-built map from build_baseline() instead of recomputing it 3 times.
  - touches: scripts/compute_lalkitab_baseline.py L557 (build_teva signature) + L889 (call site) — Lal-Kitab-specific script only
- **[P2] P2-14 (misc) — baseline-runner agent's gloss template still assumes a running dasha for every school including Lal Kitab** (live)
  - fix: Condition the gloss template on school: for lalkitab, gloss on fixed-house lagna flavour, teva type, active rin count, sleeping-planet count instead of lagna/dasha/Atmakaraka.
  - touches: agents/baseline-runner.md L35-38 — SHARED agent used by all 6 schools; flag for contention, must not regress the dasha-based gloss for vedic/bnn/jaimini/kp_natal/kp_horary
- **[P2] R1 — timing.md's explicit year-recurrence examples still contradict varshphal.md's table** (live)
  - fix: Correct or delete the misleading explicit 9-year-recurrence example lists in timing.md L42 and L89 so they match (or defer entirely to) the varshphal.md year-ruler table.
  - touches: skills/lal-kitab/references/timing.md — reference-file only, no script change needed (script already handles the discrepancy correctly)
- **[P2] R2 — danger-year set still mismatched between timing.md and upaay_catalog.md** (live)
  - fix: Add age 54 to upaay_catalog.md §9's danger-year list (with its Mars+Saturn health-watch upaay), or explicitly document why age-54 upaay differs from the other danger years.
  - touches: skills/lal-kitab/references/upaay_catalog.md §9 — reference-file only
- **[P2] R3 — varshphal.md still internally inconsistent on age 28 (single vs two-ruler)** (live)
  - fix: Either change L166's list to (1, 42, 54) — dropping 28 — or add a second ruler to the age-28 table row if a two-ruler reading is actually intended; pick one and make them agree.
  - touches: skills/lal-kitab/references/varshphal.md — reference-file only, no script change needed (script already follows the table)