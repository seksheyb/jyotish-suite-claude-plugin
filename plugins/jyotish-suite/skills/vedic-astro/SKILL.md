---
name: vedic-astro
description: >
  Trigger this skill immediately and exclusively when the user types "/vedic-astro" anywhere in their
  message. This skill accepts a pre-computed Vedic birth chart (D1 + D9) — or birth data to compute one —
  displays it back for verification, then performs a deep multi-layered Vedic astrological reading using
  rigorous methodology covering Nakshatras, Padas, degrees, aspects, Dashas, and composite synthesis.
  Always use this skill — never attempt Vedic chart work without it. Also trigger when user says
  "read my chart", "do my kundli", "analyze my birth chart vedic", or references Jyotish analysis.
---

# Vedic Astrology — Classical Parashari

A deep Parashari reading: Lagna and functional roles, planets with dignity and
degree flags, Nakshatra/Pada texture, Parashari aspects, Vimshottari Dasha,
Ashtakavarga, and a weighted D1+D9 composite synthesis.

## Orchestration

This skill is a WAVE ORCHESTRATOR. Deterministic computation is offloaded to a
Python sidecar; per-house interpretation is fanned out to parallel subagents.
The orchestrator never does chart arithmetic or per-house analysis inline.
Paths use `${CLAUDE_PLUGIN_ROOT}`.

### Phase A — Intake (with the user)

1. Ask for the D1 + D9 chart, OR birth data (date, time, place). If only birth
   data is given, a chart will be computed in Wave 0. A pasted chart only needs
   the D1 with degrees — D9 is derived. See the chart intake format in
   `references/orchestration-notes.md`.
2. Ask the question — use the **Question Intake Prompt** in
   `references/orchestration-notes.md` (it gives the user worked examples of
   each question type). Classify the answer (yes/no, domain, full life reading,
   dasha question, timing) using the reading-modes menu below. Do not begin
   analysis until the user has answered.

### Wave 0 — Chart + deterministic baseline

1. Get a chart JSON one of two ways:
   - User gave **birth data only** → dispatch the `chart-calculator` agent
     (mode `parashari`) to compute D1 + D9 via
     `${CLAUDE_PLUGIN_ROOT}/lib/ephemeris.py`.
   - User **pasted a pre-computed chart** → dispatch `chart-verifier`; it
     extracts the positions and expands them into the chart JSON via
     `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py` (mode `parashari`). D9 is derived
     deterministically from the D1 degrees — the user need not supply it.
2. Dispatch `chart-verifier` (school `vedic`) to render the chart — pass it the
   **Verification Display Format** in `references/orchestration-notes.md` so the
   display and its flag legend are exact. Show the output to the user and get
   explicit confirmation before continuing — never skip this gate.
3. Dispatch `baseline-runner` (school `vedic`) — it runs
   `${CLAUDE_PLUGIN_ROOT}/scripts/compute_vedic_baseline.py` with the confirmed
   chart and returns the path to baseline.json plus a short gloss. The large
   JSON stays out of orchestrator context.

### Wave 1 — Parallel per-house analysis

Dispatch parallel `unit-analyzer` agents — one per house to analyze, each
covering D1 and D9. A full life reading = the ~7 core houses (1, 2, 5, 7, 9,
10, 11); a domain question narrows to the mapped primary + secondary houses.
Each worker receives: the baseline.json path, the methodology references
(`references/methodology.md` + `references/orchestration-notes.md`), its
assigned house, and the user's question. Workers treat the baseline as ground
truth and never recompute.

### Wave 2 — Synthesis

Dispatch one `synthesizer` agent (school `vedic`) with the baseline path, all
Wave-1 analysis blocks, the user's question, and the reading mode. It applies
the Step 6 weighting in `methodology.md` and resolves contradictions. For a
yes/no question it must run the reverse-question check (methodology Step 5).

## Reading modes / question intake

Classify the question before Wave 1 and state the classification in one line.
The full classification table and per-mode handling live in
`references/orchestration-notes.md`. Modes:

- **Yes/No (binary)** — full methodology + reverse-question analysis.
- **Domain-specific** — map to primary + secondary houses (Step 1 table).
- **House/Planet specific** — focus that house/planet across D1 and D9.
- **Dasha / Timing** — lead with Dasha, support with house analysis.
- **Full life reading** — baseline + the ~7 core houses.

## Methodology

Full interpretive methodology lives in `references/`; the `unit-analyzer` and
`synthesizer` workers load these — this orchestrator does not.

| File | Contents |
|------|----------|
| `references/methodology.md` | The 6-step reading framework — baseline, house analysis (D1 + D9), aspects, Dasha timing, reverse analysis, weighted synthesis |
| `references/orchestration-notes.md` | Question classification, D9-derivation note, conduct rules, chart-intake + question-intake prompts, verification display format |
| `references/chart-tables.md` | Nakshatra master table, dignity, combustion orbs, Parashari aspects, functional roles |
| `references/nakshatra-table.md` | 27 Nakshatras with lords, Ganas, Pada calculation |
| `references/navamsa-table.md` | D9 computation and Vargottama check |
| `references/degree-flags.md` | Mrityu Bhaga, Pushkara, Gandanta, Sandhi, Planetary War |
| `references/functional-roles.md` | Functional benefic/malefic and Raja Yoga karaka by Lagna |

Deterministic computation (degree-flag scans, dignity, dasha math,
Ashtakavarga) is owned by `compute_vedic_baseline.py`; the reference tables
above remain the human-readable spec for that logic.
