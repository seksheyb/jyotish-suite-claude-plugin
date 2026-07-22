---
name: lal-kitab
description: >
  Trigger this skill immediately and exclusively when the user types "/lal-kitab" anywhere in their
  message. Performs Lal Kitab astrology — natal reading, karmic debt (rin) diagnosis, family chart
  impact, varshphal (annual) predictions, and action-based remedies (upaay) — per Pt. Roop Chand
  Joshi's original Farmans (1939–1952). User provides a pre-computed Vedic D1 chart. Skill re-maps
  to Lal Kitab's fixed-house frame (Aries always 1st), computes pakka ghar status, identifies
  sleeping planets, diagnoses six rins (Pitri/Matri/Stri/Kanya/Bhratra/Atma), classifies teva,
  reads houses or family impact or varshphal, prescribes ranked upaay with Farman citations.
  Always use — never attempt Lal Kitab work without it. Also trigger on "Lal Kitab reading",
  "rin diagnosis", "Pitri Rin", "upaay", "Lal Kitab remedies", or any Vedic chart submitted with a
  Lal Kitab interpretation request.
---

# Lal Kitab

Lal Kitab is a distinct system — not a sub-branch of Parashari. Its base chart is
a Vedic D1 re-mapped to a FIXED house frame (Aries = always 1st … Pisces = always
12th); dignity is by house number, never sign. It uses no D9 and no Vimshottari.
The diagnostic spine is six karmic debts (rin), a teva chart-type, sleeping vs
awake planets, an age-based Varshphal table, and action-based remedies (upaay)
that must each cite an original Farman.

## Orchestration

WAVE ORCHESTRATOR. Deterministic computation (fixed-house re-map, pakka ghar +
dignity, sleeping planets, six rins, teva, varshphal age table, four-signal
timing engine) -> Python sidecar; per-house / per-family-member / per-year /
per-window interpretation -> parallel subagents. Paths use `${CLAUDE_PLUGIN_ROOT}`.

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
       • "Do I have Pitri Rin?"              → Mode A + rin focus

  3. Not sure — show me what's possible after baseline
     (defaults to the full mode menu)

You can also just answer in your own words. I'll run the full
diagnostic baseline either way — your answer helps me weight
the reading toward what matters to you.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Store the answer as `user_intent`. The baseline ALWAYS runs in full — intent only
tilts narration and pre-routes the mode menu. Intent-tilting table and rules:
`references/orchestration-notes.md` (Phase 0 section).

### Phase A — Intake

1. Ask for the Vedic D1 chart, OR birth data (date, time, place, lat/long,
   ayanamsa, current age for Varshphal). If only birth data is given, a D1 is
   computed in Wave 0. D9 / Nakshatras / Vimshottari are not used — if supplied,
   display but exclude with an explicit note.
2. Mode menu: A natal / B family / C varshphal / D full / E upaay / F timing.
   If Phase 0 intent maps cleanly to one mode, present a confirm-or-override
   prompt instead of the full menu (see Reading modes below).

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
   output.

### Wave 1 — Parallel per-unit analysis (mode-dependent)

Every worker is a `unit-analyzer` and receives: the baseline.json path, the
methodology reference(s) for its task, its assigned unit, the user's question,
and the Phase-0 narration-emphasis cues. Workers treat the baseline as ground
truth — they never recompute.

- **Mode A (natal):** 12 parallel workers, one per house.
- **Mode B (family):** ~6 parallel workers, one per relative requested.
- **Mode C (varshphal):** ~6 parallel workers, one per year window (current age,
  next-5-years, next major year, any 42/48/63 in next 25 years).
- **Mode E (upaay):** 3 workers, one per upaay tier (Critical / Strengthening /
  Maintenance).
- **Mode F (timing):** ~3 workers interpreting the convergence engine's top
  candidate years.
- **Mode D (full):** run A + B + C as one wide wave.

Per-mode dispatch detail and which reference files each worker loads:
`references/orchestration-notes.md` (worker dispatch section).

### Wave 2 — Synthesis

Dispatch one `synthesizer` for the one-page summary — weights rin overlay over
isolated house strength, flags sleeping benefics, applies teva-driven upaay
priority. Summary template + weighting rules: `references/orchestration-notes.md`.

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
| `references/varshphal.md` | Age-based year-rulership table + per-year reading procedure |
| `references/timing.md` | Four-signal convergence engine, event-significator mapping, modifier filters |
| `references/upaay_catalog.md` | Full remedy catalog with Farman citations, conflicts, contraindications |
