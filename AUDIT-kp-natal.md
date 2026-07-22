# AUDIT — kp-natal skill (branch `refactor-efficient` vs `main`)

Audit date: 2026-05-21 · Auditor pass: line-by-line · **No fixes applied.**

## Summary

**Overall verdict: MINOR GAPS (bordering moderate).** No P0 — the skill runs,
emits valid JSON, and the deterministic core (lord chains, CSL, 4-level
significators, Vimshottari/Sookshma dasha math, house-combination table) is
**correct**. But the refactor lost the skill's three KP-specific output-format
templates, and the baseline has several methodology gaps it inherited or
introduced.

Counts: **P0 = 0 · P1 = 6 · P2 = 11.**

Reference files (`methodology.md`, `house-combinations.md`, `ruling-planets.md`,
`significators-rules.md`) are **byte-identical** to `main` — Part 1 is purely a
question of where the old inline SKILL.md content landed.

Key findings:
- Three formatted output templates from `main` (per-cusp "HOUSE [N]" box, "LIFE
  THEMES — KP SYNTHESIS" box, "VERDICT" box) were **not** carried into
  `orchestration-notes.md` — only prose descriptions survive. **LOST.**
- The RP retrograde-exclusion rule is *computed* but never *applied* to
  `final_rp`.
- The baseline never surfaces the dasha running **now**; `dasha.running` is the
  quartet running **at birth**.
- Degree flags (combust/sandhi/gandanta/Mrityu Bhaga) — referenced by
  `methodology.md` special rules and the verdict caveats — are not emitted.

---

## Part 1 — Content gaps

`main` SKILL.md walked top-to-bottom. Where each item landed:

| Item (main SKILL.md) | Status | Where it went | Severity |
|---|---|---|---|
| Frontmatter `description` | PRESERVED (byte-identical) | SKILL.md frontmatter | P2 — now stale: still says "provides the chart as a markdown file"; refactor added a birth-data compute path |
| Overview (7 numbered steps) | PRESERVED | SKILL.md → Orchestration / Phase A / Waves 0-2 | — |
| "Reference files — load when" table | PRESERVED | SKILL.md → Methodology section | — (per-file load-condition nuance softened) |
| "Computation scripts" table (`compute_ruling_planets.py`, `compute_sookshma.py`) | MOVED / consolidated | `scripts/compute_kp_natal_baseline.py` (one script); README documents it | — |
| PHASE 1 — Chart Collection prompt box | MOVED | `orchestration-notes.md` "Chart Intake Format" | P2 — "optionally outer planets" line dropped from the intake list (verification display still allows them) |
| New: birth-data → compute path | ADDED (not in `main`) | SKILL.md Wave 0 (`chart-calculator`) | — (enhancement) |
| PHASE 2 — Verification Echo template | PRESERVED (verbatim) | `orchestration-notes.md` "Verification Display Format" | — |
| PHASE 3 — Mode Selection prompt box | PRESERVED | `orchestration-notes.md` "Mode Selection Prompt" | — |
| PHASE 4A — per-cusp output box ("HOUSE [N] — … Cuspal Sub Lord … Verdict") | **LOST** | nowhere — only prose in `methodology.md` "Life reading methodology" + SKILL.md Wave 2 | P1 |
| PHASE 4A — "LIFE THEMES — KP SYNTHESIS" output box (Strong/Weak/Mixed/Top-3 themes/Top-3 work areas) | **LOST** | nowhere — only prose ("strong areas, blocked areas, conditional areas, dominant themes, work areas") in SKILL.md Wave 2 | P1 |
| PHASE 4B Step 1 — identify house combination | PRESERVED | `methodology.md` Step 1 + `house-combinations.md` | — |
| PHASE 4B Step 2 — primary CSL box + "Stop here, deliver 'will not fructify'" | WEAKENED | `methodology.md` Step 2 (prose only; formatted box lost, explicit STOP instruction softened to "CSL signifies negative → denied") | P2 |
| PHASE 4B Step 3 — significators (4 levels) | PRESERVED | `methodology.md` Step 3 + `significators-rules.md` | — |
| PHASE 4B Step 4 — compute RP / Step 5 RP cross-check | PRESERVED | `methodology.md` Step 5; cross-check folded into Step 6 | P2 — SKILL.md/orchestration list "RP cross-check" as its own flow step; `methodology.md` decomposes it differently (cosmetic mismatch) |
| PHASE 4B Step 6 — DBA-Sookshma window | PRESERVED + enriched | `methodology.md` Step 6 (adds the fruitful-significator gate, Step 4) | — |
| PHASE 4B Step 7 — transit confirmation | PRESERVED | `methodology.md` Step 7 | P2 — no deterministic backing (also true in `main`); baseline emits no transit positions |
| PHASE 4B Step 8 — "VERDICT — [event]" output box | WEAKENED | `methodology.md` Step 8 (prose bullet list survives; formatted box lost) | P1 |
| Critical Rules 1-7 | PRESERVED (all 7) | `orchestration-notes.md` "Critical rules" | — |
| Output Style block | PRESERVED | `orchestration-notes.md` "Output style" | — |

### Contradictions the refactor introduced

1. **`orchestration-notes.md:140` — "The baseline extends the supplied MD/BD/AD
   dasha to the 4th-level Sookshma."** CONTRADICTED by the code. The baseline
   never reads a user-supplied MD/BD/AD: it recomputes the whole Vimshottari
   tree from the Moon's longitude (`ephemeris._vim_dasha`). If the user pasted a
   `dasha` block with *no* birth datetime, `chart_io._dasha_for` returns a plain
   passthrough with **no `tree`** → the baseline emits **no Sookshma at all**
   (confirmed: run on a pasted chart with the `birth` block removed →
   `dasha: {"source": "unavailable"}`). The sentence should say the baseline
   *recomputes* the tree from birth data, and that this needs a birth datetime.

2. **SKILL.md Wave 0 implies `chart-verifier` runs twice.** Step 1 (pasted-chart
   branch) says dispatch `chart-verifier` to "extract … and expand … via
   `chart_io.py`"; Step 2 says dispatch `chart-verifier` again "to render the
   chart". The `chart-verifier` agent spec does **both** expansion and rendering
   in a single dispatch (its "Two input cases" + "Then, in both cases — render").
   As written, an orchestrator could double-dispatch it. Redundant / confusing.

### Path & agent-name resolution (SKILL.md)

All resolve correctly:
- `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py` ✓
- `${CLAUDE_PLUGIN_ROOT}/scripts/compute_kp_natal_baseline.py` ✓
- agents `chart-calculator`, `chart-verifier`, `baseline-runner`,
  `unit-analyzer`, `synthesizer` ✓ (all exist in `agents/`)
- `references/{methodology,house-combinations,ruling-planets,significators-rules,orchestration-notes}.md` ✓

**Stale path outside SKILL.md:** `commands/kp-natal.md` still says *"If a script
under `skills/kp-natal/scripts/` fails …"* — that directory **does not exist**
on this branch (scripts moved to `plugins/jyotish-suite/scripts/`). The command
file also still lists the old monolithic 7-step flow. Not breaking (step 1 says
"Read SKILL.md and follow it exactly") but stale. P2.

---

## Part 2 — Script methodology findings

Scripts audited: `scripts/compute_kp_natal_baseline.py`, `lib/jyotish_primitives.py`,
`lib/ephemeris.py`, `lib/chart_io.py`.

| Rule | Reference loc | Script loc | Verdict | Note |
|---|---|---|---|---|
| CSL = cuspal sub-lord decides the house | methodology.md:5 | baseline.py:303-307 | CORRECT | `entry["CSL"] = c["sub_lord"]` from `full_lord_chain` |
| Placidus cusp-to-cusp house arcs | methodology.md:9 | baseline.py:50-60 | CORRECT | `house_of_longitude` uses cusp→next-cusp span |
| Significator L1 (planets in star of an occupant) | significators-rules.md:8-12 | baseline.py:107-108 | CORRECT | |
| Significator L2 (occupants) | significators-rules.md:13-17 | baseline.py:110 | CORRECT | nodes counted as occupants ✓ |
| Significator L3 (planets in star of house-lord) | significators-rules.md:18-22 | baseline.py:112-113 | CORRECT | |
| Significator L4 (house-lord) | significators-rules.md:23-26 | baseline.py:115 | CORRECT | |
| Node depositor / conjunct → node co-signifies | significators-rules.md:30-38 | baseline.py:91-99, 119-125 | CORRECT | node added at occupant strength when depositor or a ≤3° conjunct planet is a significator |
| **Node amplifies a conjunct planet** ("planets in conjunction with Rahu/Ketu — amplified for that house's signification") | methodology.md:33-34 | — | **MISSING** | reverse direction never applied — a planet conjunct a node is not given the node's extra houses |
| RP — 7 factors, strength order | ruling-planets.md:9-15 | baseline.py:149-157 | CORRECT | order Lagna Sub/Star/Sign, Moon Sub/Star/Sign, Day Lord |
| RP — weekday→lord table | ruling-planets.md:20-27 | jyotish_primitives.py:54-55 | CORRECT | `WEEKDAY_LORDS` matches |
| RP — Day Lord counted from sunrise (pre-sunrise = previous day) | ruling-planets.md:29 | ephemeris.py:99-118 | CORRECT | `sunrise_jd` finds the most-recent sunrise ≤ jd_ref |
| RP — Day Lord weekday from **local** date | ruling-planets.md:18-29 | ephemeris.py:117 | APPROXIMATED | `sr_dt.weekday()` is taken from the **UTC** revjul date; wrong weekday for far-east/west longitudes where sunrise crosses the UTC date line. Pre-existing (same in `main`). |
| **RP — retrograde planets (non-node) excluded** (keep only if depositor is RP) | ruling-planets.md:44-45 | baseline.py:168-181, 190 | **WRONG / APPROXIMATED** | the retrograde test + depositor-keep decision is computed into the `retrograde_check` string, but `final_rp = list(dedup)` (line 190) **never removes** the excluded planet. `final_rp` can contain a planet the reference says to drop. Pre-existing pattern in `main`'s `compute_ruling_planets.py`. Mitigation: `retrograde_check` exposes the correct verdict, so a careful synthesizer can compensate. |
| RP — node added to RP set | ruling-planets.md:47 | baseline.py:183-194 | **MISSING (2 of 3)** | reference: node joins RP if its sign is owned by an RP **OR** it is conjunct an RP **OR** it is in the star of an RP. Code (`rahu_sl in dedup`) checks **only** the sign-lord condition. Conjunction and star-lord conditions absent. Pre-existing. |
| RP — qualifying node "becomes the strongest RP" | ruling-planets.md:47 | baseline.py:219 | NOTE | `strongest_rp` hardcoded to Lagna Sub Lord. Reference is internally inconsistent — its own example (ruling-planets.md:88) also reports Lagna Sub Lord as strongest after adding both nodes. Code matches the example, not the prose. |
| Sub / sub-sub-lord boundaries (Vimshottari-proportional within nakshatra) | KP standard | jyotish_primitives.py:188-220 | CORRECT | proportional `VIM_YEARS/120 × arc`, correct fallback |
| Vimshottari dasha math (MD→BD→AD→SD) | methodology.md:5 (Vimshottari only) | jyotish_primitives.py:417-472 | CORRECT | balance from Moon's nakshatra fraction; nested proportional periods |
| DBA-Sookshma running-quartet lookup | methodology.md:44-52 | jyotish_primitives.py:475-498 | CORRECT | `find_running` walks MD/BD/AD/SD |
| **"Current dasha" (quartet running at the reading moment)** | methodology.md:45 ("Walk forward … from current moment"); orchestration-notes.md:131 ("CURRENT DASHA") | baseline.py:324-331; ephemeris.py:167-178, 291 | **WRONG / MISSING** | `_vim_dasha` is called with the **birth** UTC, so `dasha.running` is the quartet running **at birth** (confirmed: test nativity → `dasha.running.md_lord = "Ketu"`, period 1981-1988). The baseline computes the now-running quartet **only** if `--target-datetime` is passed — and nothing in SKILL.md / orchestration-notes / `baseline-runner` instructs that flag. The verification display's "CURRENT DASHA" would show the at-birth dasha. |
| **Combustion — KP orb 8.5° flat** | methodology.md:97 | — (not emitted) | **MISSING** | baseline emits no `combust` flag. Trap: `jyotish_primitives.COMBUSTION_ORBS` (lines 61-63) are **Parashari** orbs (Moon 12°, Mars 17° …) — using them for KP would be **WRONG**; KP needs a flat 8.5°. |
| **Sandhi — last/first 0°30' of a sign** | methodology.md:99 | — (not emitted) | **MISSING** | baseline emits no `sandhi` flag. Trap: `jyotish_primitives.sandhi` (lines 302-309) uses **±1.0°**, not 0°30' — WRONG vs KP if naively wired in. |
| Gandanta (CSL at Gandanta = matter starts/stops) | methodology.md:105 | — (not emitted) | MISSING | baseline emits no `gandanta` flag for cusps/planets. `jyotish_primitives.gandanta` exists (3°20' zones) but is uncalled by this baseline. |
| Mrityu Bhaga (weakened planet) | methodology.md:101 | — (not emitted) | MISSING | `MRITYU_BHAGA` table exists in lib (uncalled). Reference calls it "KP-specific"; table provenance unverified. |
| Fruitful vs barren significator (sub-lord gate) | significators-rules.md:40-51; methodology.md:36-39 | — (not pre-computed) | APPROXIMATED | not classified in the baseline. Derivable by a worker — every planet's `sub_lord` and the per-house `significators` are emitted — but a "sub-lord → houses signified" reverse map would make the gate deterministic. |
| Outer planets excluded from core KP | orchestration-notes.md:73-74 | baseline.py:42 | CORRECT | `PLANETS` is the 9-graha set only |
| House-combinations table fidelity | house-combinations.md (all categories) | baseline.py:227-264 | CORRECT | spot-checked marriage (7 / 2,7,11 / 1,6,10), new_job, childbirth, property — all match |
| `owned` dict | — | baseline.py:84-88 | DEAD CODE | computed, never read (`house_lord` uses the cusp sign-lord directly). Cosmetic. |

### Baseline JSON vs what workers are told to consume

SKILL.md Wave 0 step 3 / orchestration-notes promise the baseline gives "12
cusps with full lord chains + CSL, 9 planets, 4-level significators, current
Ruling Planets, Sookshma dasha, house-combination tables."

Emitted and correct: `cusps` (+`CSL`), `planets`, `significators` (L1-L4),
`ruling_planets`, `dasha.tree` (Sookshma inside), `house_combinations`.

Not delivered as promised:
- **"current Ruling Planets"** — OK (`--rp-datetime` defaults to now).
- **"Sookshma dasha"** for the *current* window — only via `dasha.tree`;
  `dasha.running` is at-birth (see table).
- **Degree-flag caveats** (sandhi/gandanta/combust) the verdict template asks
  for — not emitted at all.
- **Transit positions** for Step 7 — not emitted; workers (`unit-analyzer`,
  `synthesizer`) have only the `Read` tool and cannot compute them.

---

## Part 3 — Run results

All commands run from the repo root with `python3`.

| Test | Result |
|---|---|
| `compute_kp_natal_baseline.py --datetime 1988-02-14T09:30:00 --tz Asia/Kolkata --lat 19.07 --lon 72.87` | **exit 0**, valid JSON, 13 top-level keys |
| Pasted-chart path: `chart_io.py --mode kp --positions … --out …` then `baseline --chart …` (birth block present) | **exit 0** both; RP computed, significators/CSL present |
| Pasted-chart path with `birth` block removed | **exit 0**, graceful: `ruling_planets: {"error": …}`, `dasha: {"source":"unavailable"}` |
| `--rp-datetime` + `--target-datetime` | **exit 0**; `dasha.running_at_target` correctly produced (Mars-Jupiter-Ketu-Venus for 2026-09-01); `dasha.running` still at-birth |

No crashes. No tracebacks.

### Sanity checks (test nativity 1988-02-14 09:30, Mumbai)

| Value | Baseline output | Hand check |
|---|---|---|
| Ayanamsa mode | `kp` (KP-New), 23°35'39" | ✓ correct system for KP natal |
| House system | Placidus | ✓ |
| Lagna (cusp 1) | Pisces 344°26', sign-lord Jupiter, star Saturn, CSL Rahu | ✓ Pisces lord = Jupiter; 344°26' falls in Uttara Bhadrapada (333°20'-346°40', lord Saturn); morning Feb birth → Pisces rising plausible |
| Moon | Sagittarius 252°03', Mula, pada 4, star-lord Ketu, sub Mercury | ✓ Mula 240°-253°20', lord Ketu; 252° = pada 4 (250°-253°20') |
| Sun | Aquarius 301°04', Dhanishtha | ✓ Dhanishtha 293°20'-306°40' |
| Day Lord (RP, reading = 2026-05-21) | Thursday → Jupiter | ✓ 2026-05-21 is a Thursday |
| Running dasha **at birth** | Ketu MD / Mercury BD / Venus AD / Saturn SD | ✓ for *birth* — but this is mislabeled as `running`; the **current** (2026) MD is Mars (2024-2031), not surfaced |

---

## Prioritized fix list

### P1 — missing capability / methodology gap

1. **Restore the three lost KP output templates.** Move `main`'s PHASE 4A
   per-cusp box ("HOUSE [N] — … Cuspal Sub Lord … Verdict"), the "LIFE THEMES —
   KP SYNTHESIS" box, and the PHASE 4B "VERDICT — [event]" box into
   `references/orchestration-notes.md` (or `methodology.md`), and have
   `unit-analyzer` / `synthesizer` be handed those exact formats. Today only
   prose survives, so per-cusp and verdict output format is unspecified.

2. **Apply the RP retrograde exclusion to `final_rp`.** `baseline.py:168-190` —
   compute the keep/exclude decision (already done) and actually drop excluded
   retrograde planets from `final_rp`, keeping one only when its depositor is an
   RP (per `ruling-planets.md:44-45`). Currently the decision is cosmetic text.

3. **Surface the dasha running at the reading moment.** Either default
   `--target-datetime` to "now", or add a dedicated `dasha.running_now` block,
   and stop labelling the at-birth quartet `running`. Wire SKILL.md /
   `baseline-runner` to pass the reading datetime. Without this the "CURRENT
   DASHA" verification echo and methodology Step 6 ("walk forward from current
   moment") have no correct starting point.

4. **Complete the RP node-inclusion rule.** `baseline.py:183-188` — add the two
   missing conditions from `ruling-planets.md:47`: node joins RP if conjunct an
   RP planet, or in the star (nakshatra) of an RP planet — not only when its
   sign-lord is an RP.

5. **Emit KP degree flags in the baseline.** Add `combust` (flat 8.5° KP orb —
   **do not** reuse `jyotish_primitives.COMBUSTION_ORBS`), `sandhi` (0°30', not
   the lib's 1°), `gandanta`, and `mrityu_bhaga` for the 9 planets and the 12
   cusps. `methodology.md:93-109` and the verdict's "Caveats" line depend on
   these; right now they have zero deterministic backing.

6. **Fix the `orchestration-notes.md:140` contradiction.** Reword to: the
   baseline *recomputes* the full Vimshottari tree (incl. Sookshma) from the
   Moon's longitude and a birth datetime — it does **not** extend a
   user-supplied MD/BD/AD; and a pasted `dasha` passthrough without a birth
   datetime yields **no** Sookshma.

### P2 — cosmetic / robustness

7. **`commands/kp-natal.md`** — fix the stale `skills/kp-natal/scripts/` path
   (now `plugins/jyotish-suite/scripts/`) and refresh the 7-step body to the
   wave-orchestrator flow; add the birth-data path.
8. **SKILL.md Wave 0** — state that `chart-verifier` is a *single* dispatch that
   both expands a pasted chart and renders the display; remove the implied
   double-dispatch.
9. **Re-add "optionally outer planets"** to the Chart Intake Format prompt in
   `orchestration-notes.md` (the verification display still references them).
10. **Restore the explicit STOP** in PHASE 4B Step 2 — "if CSL signifies the
    negative set only → stop, deliver 'will not fructify in this life'" — into
    `methodology.md` Step 2; currently softened.
11. **Node-amplifies-conjunct-planet rule** (`methodology.md:33-34`) — implement
    the reverse direction in `compute_significators`, or drop the claim.
12. **Day-lord weekday** — compute `sr_dt.weekday()` from the **local** date at
    the place, not the UTC revjul date (`ephemeris.py:117`).
13. **Pre-compute fruitful/barren** — add a "sub-lord → houses signified"
    reverse map so the `significators-rules.md:40-51` gate is deterministic.
14. **Remove the dead `owned` dict** (`baseline.py:84-88`).
15. **Transit backing for Step 7** — optionally emit transit Jupiter/Sun/Moon
    positions at `--target-datetime`; workers cannot compute them (Read-only).
16. **Frontmatter `description`** — it still says "provides the chart as a
    markdown file"; mention the birth-data compute path.
17. **`strongest_rp`** — when a node qualifies for RP, decide whether it should
    outrank Lagna Sub Lord (resolve the internal inconsistency between
    `ruling-planets.md:47` prose and its line-88 example).

---

*Audit complete. No files other than this report were modified; git untouched.*
