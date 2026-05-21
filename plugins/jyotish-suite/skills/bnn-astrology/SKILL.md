---
name: bnn-astrology
description: >
  Trigger this skill immediately and exclusively when the user types "/bnn" anywhere in their message.
  This skill accepts a pre-computed Vedic birth chart (D1 + D9), displays it back for verification,
  then performs a deep BNN (Brighu Nadi Nadi) astrological reading using rigorous Nadi methodology —
  natural Karakas, sign fields, flow positions (2nd/12th), trine support (5th/9th), growth positions
  (3rd/11th), opposition (7th), Parashari aspects with degree orbs, degree flags (Mrityu Bhaga,
  Pushkara, Gandanta, Sandhi, Planetary War, combustion), and Vimshottari Dasha timing. Always use
  this skill — never attempt BNN chart work without it. Also trigger when user says "BNN reading",
  "Brighu Nadi", "Nadi reading", or references natural Karaka analysis with chart data already provided.
---

# BNN Astrology — Bhrigu Nadi

BNN reads every event from the natural **Karaka** (planet), not from the Lagna —
the Sign is the field of expression, the Planet is the actor. Lagna is secondary
context only. This skill orchestrates a deterministic baseline sidecar plus
parallel per-Karaka interpretation.

## Orchestration

WAVE ORCHESTRATOR. Deterministic computation -> Python sidecar; per-Karaka
interpretation -> parallel subagents. Paths use `${CLAUDE_PLUGIN_ROOT}`.

### Phase A — Intake (with the user)

1. Ask for the birth chart (D1), OR birth data (date, time, place). A pasted
   chart only needs the D1 with degrees — D9 is derived. Use the chart intake
   prompt in `references/orchestration-notes.md` ("Chart Intake Format").
2. Ask the **question** — use the **Question Intake Prompt** in
   `references/orchestration-notes.md` (worked examples of each question type).
   Classify the answer (yes/no, domain, specific Karaka, dasha, full reading,
   timing) per the classification table there. State the classification and the
   primary/secondary Karaka in one line before dispatching Wave 1.

### Wave 0 — Chart + deterministic baseline

1. Get a chart JSON one of two ways:
   - User gave **birth data only** -> dispatch `chart-calculator`
     (mode `parashari`) to compute D1 + D9.
   - User **pasted a pre-computed chart** -> dispatch `chart-verifier`; it
     extracts the positions and expands them into the chart JSON via
     `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py` (mode `parashari`).
2. Dispatch `chart-verifier` (school `bnn`) to render the verification display
   — pass it the **Verification Display Format** in
   `references/orchestration-notes.md` so the layout, the BNN Sign Layout table
   and the flag legend are exact. Show it to the user and get explicit
   confirmation before proceeding.
3. Dispatch `baseline-runner` (school `bnn`) -> runs
   `${CLAUDE_PLUGIN_ROOT}/scripts/compute_bnn_baseline.py`, which computes all
   deterministic BNN facts (natural karakas, planets with dignity + degree flags
   + priority verdict, karaka-relative positions for D1 + D9, aspect map,
   Vimshottari dasha). Returns the `baseline.json` path + a short gloss.

### Wave 1 — Parallel per-Karaka analysis

Dispatch parallel `unit-analyzer` agents — one per natural Karaka relevant to
the question. A full reading ≈ Sun, Moon, Jupiter, Venus, Saturn, Mars; a domain
question narrows to 1-2 Karakas (use the topic→Karaka map in
`references/karaka-tables.md`). Each worker covers D1 and D9 and runs BNN
Steps A-F (`references/methodology.md` Section 2-3). Each worker receives: the
`baseline.json` path, the methodology references, its assigned Karaka, and the
question.

### Wave 2 — Synthesis

Dispatch one `synthesizer` for the composite reading — BNN 10-level priority
order, D1/D9 convergence, Dasha activation, confidence rating, and the reverse
question check for yes/no questions (`methodology.md` Sections 4-5).

## Reading modes / question intake

Offer these example framings at intake (full menu and classification table in
`references/orchestration-notes.md`):
- "Will I get a promotion this year?" — yes/no, reverse analysis applied
- "Read my career and professional growth" — domain
- "What does BNN say about my marriage prospects?" — domain
- "Full reading — all life domains" — full
- "What is my current Dasha activating in BNN terms?" — dasha
- "Read Venus as the Karaka for relationships" — specific Karaka

Always ask for timeframe and any optional context. Do not begin analysis until
the user has confirmed the chart and answered the question intake.

## Methodology

Full interpretive methodology lives in `references/` — workers load these; the
orchestrator does not.

| File | Contents |
|------|----------|
| `references/methodology.md` | BNN Steps A–F, D9 analysis, Dasha timing, execution sequence, 10-level priority |
| `references/karaka-tables.md` | Natural Karakas (1A), sign fields (1B), planet relationships (1C), topic→Karaka map |
| `references/degree-flags.md` | Combustion, Gandanta, Mrityu Bhaga, Pushkara, Sandhi, Planetary War, priority table |
| `references/aspects.md` | Graha Drishti rules, orb framework, mutual aspects, empty-sign rule, aspect pre-map |
| `references/orchestration-notes.md` | Core BNN principle, chart-intake + question-intake prompts, D9-derivation note, question classification, conduct rules, verification display format, sign-layout reference |
