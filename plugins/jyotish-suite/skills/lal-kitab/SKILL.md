---
name: lal-kitab
description: >
  Trigger this skill immediately and exclusively when the user types "/lal-kitab" anywhere in their
  message. Performs Lal Kitab astrology — natal reading, karmic debt (rin) diagnosis, family chart
  impact, varshphal (annual) predictions, and action-based remedies (upaay) — per Pt. Roop Chand
  Joshi's original Farmans (1939–1952). User provides a pre-computed Vedic D1 chart, or raw birth
  data from which one is computed. Skill re-maps to Lal Kitab's fixed-house frame (Aries always 1st),
  computes pakka ghar status, identifies sleeping planets, diagnoses six rins
  (Pitri/Matri/Stri/Kanya/Bhratra/Atma), classifies teva, reads houses or family impact or varshphal,
  prescribes ranked upaay with Farman citations. Always use — never attempt Lal Kitab work without
  it. Also trigger on "Lal Kitab reading", "rin diagnosis", "Pitri Rin", "upaay", "Lal Kitab
  remedies", or any Vedic chart submitted with a Lal Kitab interpretation request.
---

# Lal Kitab

Lal Kitab is a distinct system — not a sub-branch of Parashari. Its base chart is
a Vedic D1 re-mapped to a FIXED house frame (Aries = always 1st … Pisces = always
12th); dignity is by house number, never sign. It uses no D9 and no Vimshottari.
The diagnostic spine is six karmic debts (rin), a teva chart-type, sleeping vs
awake planets, an age-based Varshphal table (**not** the Tajaka/solar-return
Varshphal used elsewhere in Vedic practice — see `references/varshphal.md`), and
action-based remedies (upaay) that must each cite an original Farman.

## Orchestration

WAVE ORCHESTRATOR. Deterministic computation (fixed-house re-map, pakka ghar +
dignity, sleeping planets, six rins, teva, varshphal age table, four-signal
timing engine, upaay candidate generation + conflict/contraindication flags) ->
Python sidecar; per-house-cluster / per-family-member / per-year / per-window /
upaay interpretation -> parallel subagents, scaled to question scope. Paths use
`${CLAUDE_PLUGIN_ROOT}`.

### Phase 0 — Intent capture (with the user)

Before asking for the chart, present:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAL KITAB READING

What brings you here today?

  1. Just read my chart — full diagnostic + house-by-house
     (defaults to Mode D after baseline)

  2. Specific question — tell me what you want answered
     Examples:
       • "When will I change jobs?"          → Mode F (timing)
       • "How is my father affected?"        → Mode B (family)
       • "What about this year ahead?"       → Mode C (varshphal)
       • "Just give me the upaay priorities" → Mode E (remedies)
       • "Do I have Pitri Rin?"              → single-rin lookup (inline,
                                                  no worker dispatch)

  3. Not sure — show me what's possible after baseline
     (defaults to the full mode menu)

You can also just answer in your own words. I'll run the full
diagnostic baseline either way — your answer helps me weight
the reading toward what matters to you.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Store the answer as `user_intent`. The baseline ALWAYS runs in full — intent only
tilts narration and pre-routes the mode menu, which is presented in Phase B,
genuinely after the baseline completes. Intent-tilting table and rules:
`references/orchestration-notes.md` (Phase 0 section).

**Honesty boundary rule (apply here, not later):** if `user_intent` suggests
something the chart can't cleanly answer (e.g. "tell me my exact death date"),
state that boundary in Phase 0 itself and offer the closest legitimate read —
do not wait until synthesis to disclose the limit. This rule is binding on
every downstream phase too (see Wave 2).

### Phase A — Intake

1. Ask for the Vedic D1 chart, OR birth data (date, time, place, lat/long,
   ayanamsa, current age for Varshphal). If only birth data is given, a D1 is
   computed in Wave 0. D9 / Nakshatras / Vimshottari are not used — if supplied,
   display but exclude with an explicit note.

Mode selection does **not** happen here — see Phase B, after Wave 0.

### Wave 0 — Chart + deterministic baseline

1. Get a chart JSON one of two ways:
   - User gave **birth data only** -> dispatch `chart-calculator`
     (mode `parashari`; only the D1 is used by Lal Kitab).
   - User **pasted a pre-computed chart** -> dispatch `chart-verifier`; it
     extracts the positions and expands them into the chart JSON via
     `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py` (mode `parashari`).
2. Dispatch `chart-verifier` (school `lalkitab`) to render the fixed-house frame
   (Aries=1 … Pisces=12, planet per house, birth Lagna recorded as flavour) —
   pass it the **Verification Display Format** in
   `references/orchestration-notes.md` so the re-mapped layout is exact. Show
   it to the user and get explicit confirmation before any analysis — never
   skip this gate.
3. Dispatch `baseline-runner` (school `lalkitab`, pass `--age` if known) -> runs
   `${CLAUDE_PLUGIN_ROOT}/scripts/compute_lalkitab_baseline.py`, returns the
   baseline.json path + gloss. This single run produces the fixed-house re-map,
   pakka ghar + dignity, sleeping planets, the six-rin diagnosis, teva
   classification, the Varshphal age table, and the four-signal timing-engine
   output (raw signals; the synthesizer scores convergence, not this script).
4. **If Mode E or Mode D is in play** (see Phase B), dispatch `baseline-runner`
   a second time against `${CLAUDE_PLUGIN_ROOT}/scripts/lk_upaay_check.py`
   (same chart/baseline inputs) -> returns `upaay_check.json`: candidate upaay
   generated from the active rins/teva/sleeping planets, plus conflict-pair and
   pregnancy/health contraindication flags. These flags are now script facts —
   the upaay worker and synthesizer cite them, they never re-derive them from
   `upaay_catalog.md` §11 by recall.

### Phase B — Mode selection (after baseline, before Wave 1)

If Phase 0 captured a clear intent, confirm-or-override; otherwise present the
full A–F menu (see "Reading modes" below). This is the point the Phase 0 box's
"after baseline" promise refers to.

**Conditional dispatch — scale to question scope:**
- A **single-house question** ("what does my 7th house look like?") or a
  **single-rin question** ("do I have Pitri Rin?") answers **inline, zero
  worker dispatch** — read the baseline JSON directly and answer from it. Do
  not spin up a Wave 1 for a question one baseline lookup already answers.
- Anything broader (a full mode, multiple houses, multiple rins, a family
  member, a year window, timing, upaay) proceeds to Wave 1 as below.

### Wave 1 — Parallel per-unit analysis (mode-dependent)

Every worker is a `unit-analyzer` and receives: the baseline.json path (and
`upaay_check.json` path where relevant), the methodology reference(s) for its
task, its assigned unit, the user's question, the Phase-0 narration-emphasis
cues, and a reasoning-effort hint. Workers treat the baseline as ground truth —
they never recompute.

- **Mode A (natal):** 4 parallel workers, one per 3-house cluster (houses
  1–3, 4–6, 7–9, 10–12) — not 12 per-house micro-workers. Each house write-up
  is short and templated, and cross-house synthesis needs all of them anyway;
  clustering keeps the fan-out cheap without fragmenting the read. Effort:
  **high** (dense — draws directly on the Phase 2–6 baseline diagnostician
  output: pakka ghar, sleeping, rin, teva, all per house).
- **Mode B (family):** ~6 parallel workers, one per relative requested.
  Effort: **medium**.
- **Mode C (varshphal):** ~6 parallel workers, one per year window (current age,
  next-5-years, next major year, any 42/48/63 in next 25 years). Effort:
  **low** (year prose is templated off `varshphal.md`'s per-year procedure).
- **Mode E (upaay):** **ONE** `unit-analyzer`, not three per-tier workers.
  Fragmenting by tier splits a single cross-tier consistency judgment —
  conflict pairs span tiers, and the same upaay must never appear in two
  tiers at once. The one worker reads `upaay_check.json`'s candidates +
  conflict/contraindication flags plus `upaay_catalog.md`, and produces a
  flat candidate analysis (per candidate: rin/sleeping-planet/teva driver,
  Farman citation, any conflict-pair or contraindication flag). It does
  **not** assign tiers — Critical / Strengthening / Maintenance tiering
  happens in the synthesizer (Wave 2), which has full cross-tier context.
  Effort: **medium**.
- **Mode F (timing):** ~3 workers interpreting the raw four-signal output for
  their candidate year. Effort: **high** (Phase 8D narrative is the densest
  hotspot in the suite). Each worker must apply the no-specific-dates rule
  (see Wave 2) — years and probability tiers only, never a date.
- **Mode D (full):** run A + B + C as one wide wave, plus the Mode E upaay
  worker (§ above) once rin/teva/sleeping status is known. **Join barrier:**
  the synthesizer — and any upaay tiering work — starts only after every
  Wave-1 worker (all A + B + C clusters, and the upaay worker) has returned.
  Do not begin synthesis on a partial set.

Per-mode dispatch detail and which reference files each worker loads:
`references/orchestration-notes.md` (worker dispatch section).

### Wave 2 — Synthesis

Dispatch one `synthesizer` (model **opus**, effort **high** — synthesis is
the product, so the suite runs one opus synthesizer for every school) for the one-page
summary — weights rin overlay over isolated house strength, flags sleeping
benefics, applies teva-driven upaay priority, and (Mode D/E) assigns final
upaay tiers from the Wave-1 candidate analysis. Runs once, last, only after
**all** dispatched Wave-1 workers have returned — never on a partial set.

Its dispatch payload must include the school's honesty/boundary rules,
verbatim, not just a pointer to a file:
- **Phase 0 boundary rule:** where intent or a unit's finding suggests
  something the chart can't cleanly answer, state the boundary plainly instead
  of guessing past it.
- **No-specific-dates rule (Mode F / Phase 8D):** the four-signal convergence
  engine produces probability-tiered year-windows only. Single-signal timing
  calls are prohibited. Never state a specific date — redirect date-precision
  requests to KP horary.

Summary template + weighting rules: `references/orchestration-notes.md`.

## Reading modes

If Phase 0 captured a clear intent, confirm-or-override:

```
You asked: "[user's question]"
Suggested mode: [A–F] — [name].  Reason: [why it fits].
Confirm, or pick a different mode (A–F)?
```

Otherwise present the full menu:

```
  A. Full natal reading — house-by-house life analysis for the native
  B. Family chart impact — father, mother, spouse, children, siblings
     (your chart shapes your relatives' fortunes — Lal Kitab's signature)
  C. Varshphal — annual predictions for current age + upcoming year-rulers
  D. Full reading (A + B + C combined)
  E. Upaay focus — skip to ranked remedies based on the diagnosis
  F. Event timing — when will [X] happen? (marriage, career, child,
     property, foreign travel, business…). Requires the specific event.
     Returns probability-weighted age windows + activation upaay via the
     four-signal convergence engine — years, never dates.
```

## Methodology

Full interpretive methodology, all Farman citations, and the upaay catalog live
in `references/` — Wave-1 workers and the synthesizer load these; the
orchestrator does not.

| File | Owns |
|------|------|
| `references/orchestration-notes.md` | Hard methodological lines, Phase-0 intent rules, verification display format, per-mode worker dispatch, synthesis weighting, upaay output rules, output style |
| `references/pakka_ghar.md` | Dignity / pakka ghar / exaltation / debilitation / friendship tables, substitution and buried-planet rules |
| `references/aspects.md` | Lal Kitab drishti rules per planet, sleeping/awakening logic |
| `references/rin_diagnosis.md` | Six-rin detection rules + Farman citations + compounding |
| `references/teva_types.md` | Chart-type classification + teva-driven upaay priority |
| `references/family_chart.md` | Father/mother/spouse/children/sibling impact + Farman rule tables |
| `references/varshphal.md` | Age-based year-rulership table + per-year reading procedure (not Tajaka/solar-return Varshphal) |
| `references/timing.md` | Four-signal convergence engine, event-significator mapping, modifier filters |
| `references/upaay_catalog.md` | Full remedy catalog with Farman citations, conflicts, contraindications (candidate generation + conflict flags now also computed by `scripts/lk_upaay_check.py`) |
