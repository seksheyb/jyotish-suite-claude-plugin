---
name: kp-natal
description: >
  Trigger this skill immediately and exclusively when the user types "/kp-natal" anywhere in their
  message. This skill performs Krishnamurti Paddhati (KP) natal astrology — life readings and event-
  timing predictions from either birth data (date, time, place — the chart is computed via the
  shared ephemeris layer) or a pre-computed natal KP chart pasted by the user (cuspal positions with
  lord chains, planetary positions, significators, dasha sequence). The skill echoes back the chart,
  asks conversationally
  whether the user wants a life reading or event timing (and which area + horizon if event), computes
  current Ruling Planets with full calculation shown, computes Sookshma dasha (4th level) for the
  relevant window, and delivers a structured KP reading with cuspal sub-lord analysis, significators,
  and timing window. Always use this skill — never attempt KP natal work without it. Also trigger
  when user says "KP reading", "KP chart analysis", "read my KP chart", "when will I get married —
  KP", "KP timing for [event]".
---

# KP Natal — Krishnamurti Paddhati

KP natal readings — comprehensive life readings and event-timing predictions —
from a natal KP chart. The cuspal sub-lord decides; Ruling Planets cross-confirm;
DBA-Sookshma dates the event.

## Orchestration

WAVE ORCHESTRATOR. Deterministic computation -> Python sidecar; per-cusp
interpretation -> parallel subagents. Paths use `${CLAUDE_PLUGIN_ROOT}`.

### Phase A — Intake (with the user)
1. Ask for the pre-computed KP chart (12 cuspal positions with full lord chain,
   9 planets, significator table, Vimshottari MD-BD-AD), OR birth data (date,
   time, place, lat/long). If only birth data is given, a KP chart is computed
   in Wave 0. Use the chart intake prompt in `references/orchestration-notes.md`
   ("Chart Intake Format").
2. Ask the mode — **Life Reading** or **Event Timing** (if timing, get the
   event area and time horizon: next 1 yr / 3 yr / open-ended) — using the
   **Mode Selection Prompt** in `references/orchestration-notes.md`.

### Wave 0 — Chart + deterministic baseline
1. Get a chart JSON one of two ways:
   - User gave **birth data only** -> dispatch `chart-calculator` (**haiku,
     effort low**; mode `kp-natal` — KP-New ayanamsa, Placidus houses).
   - User **pasted a pre-computed KP chart** -> dispatch `chart-verifier`
     (**haiku, effort low**); it extracts the 12 cusp + 9 planet positions and
     expands them into the chart JSON via `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py`
     (mode `kp`).
2. Dispatch `chart-verifier` (school `kp-natal`, **haiku, effort low**) to
   render the chart — pass it the **Verification Display Format** in
   `references/orchestration-notes.md` so the cusps, planets, significators and
   dasha tables are exact. Show the output to the user and get explicit
   confirmation before any analysis — never skip this gate. This is a single
   dispatch that does both expansion and rendering — do not call
   `chart-verifier` twice for the same chart.
3. Dispatch `baseline-runner` (school `kp_natal`, **haiku, effort low**) -> runs
   `${CLAUDE_PLUGIN_ROOT}/scripts/compute_kp_natal_baseline.py`. This returns
   one baseline.json: 12 cusps with full lord chains + CSL, 9 planets, 4-level
   significators, current Ruling Planets (full derivation), Sookshma dasha, and
   house-combination tables. Keep the JSON out of orchestrator context — pass
   the path forward.

### Wave 1 — Analysis

**Conditional dispatch first.** If the user's event-timing question is a
narrow, single-house yes/no with no timing window requested (e.g. "will X
happen at all", one primary house, no sub-questions), **do not dispatch any
agent** — read the CSL/significator/RP fields straight off baseline.json and
answer inline in the orchestrator turn. Reserve Wave 1 dispatch for Life
Reading and for Event Timing questions that need the full 8-step chain
(a dated window, multiple houses, or the user explicitly wants the complete
reasoning shown).

- **Life Reading:** dispatch **exactly 4 parallel `unit-analyzer`** agents, one
  per trine group (`unit_type: trine`, effort **medium** each):
  - Dharma trine — houses 1, 5, 9
  - Artha trine — houses 2, 6, 10
  - Kama trine — houses 3, 7, 11
  - Moksha trine — houses 4, 8, 12
  Each worker reads its 3 cusps' CSL/significator data off the baseline and
  produces verdicts for all 3 houses in its trine — this is a genuinely wide
  fan-out (4 independent groups) without the coordination overhead of 12
  single-house workers.
- **Event Timing:** the 8-step KP read (`references/methodology.md`) is a
  **hard sequential dependency chain** — CSL verdict -> significators -> RP
  cross-check -> fruitful-window scan -> transit confirmation -> final
  verdict, each step consuming the previous step's output. **Do not fan out.**
  First run the two deterministic sidecars (the `unit-analyzer` cannot run
  scripts — it has no Bash; dispatch `baseline-runner` for each, or run them
  directly in the orchestrator):
  - Step 6 precompute (DBA-Sookshma window scan) — dispatch `baseline-runner`
    against `${CLAUDE_PLUGIN_ROOT}/scripts/find_fruitful_window.py` with the
    baseline.json path, the question's positive house set, and the horizon;
    this replaces what used to be free-form LLM inspection of MD/BD/AD/SD
    nesting. It returns a `windows.json` path.
  - Step 7 precompute (transit confirmation) — dispatch `baseline-runner`
    against `${CLAUDE_PLUGIN_ROOT}/scripts/compute_transits.py` for the
    candidate window(s) to get actual transiting Jupiter/Sun/Moon positions
    against the significator stars, instead of prose-only transit reasoning
    (previously a documented gap — no deterministic backing existed for this
    step). It returns a `transits.json` path.
  Then dispatch **one dense `unit-analyzer` pass, effort high**, that runs the
  interpretive chain end-to-end, reading baseline.json, windows.json, and
  transits.json as ground truth.
  The speed win for timing is the baseline sidecar plus these two scripts, not
  fan-out — say so if asked why timing isn't parallelized like life reading.

Each dispatched worker gets the baseline.json path (plus windows.json and
transits.json for event timing), the methodology references, its assigned
unit (trine group, or the full event-timing chain), and the user's
question/horizon.

### Explicit barrier before synthesis
Wave 2 must not start until every Wave-1 worker has returned. For Life
Reading that means all 4 trine-group workers; for Event Timing there is only
the one dense worker, so the barrier is trivially satisfied when it returns.
Never let the synthesizer begin on partial results.

### Wave 2 — Synthesis
Dispatch one `synthesizer` (school `kp-natal`, model **opus**, effort
**high**):
- **Life Reading:** weave the 4 trine-group blocks (12 house verdicts total)
  into life themes — strong areas, blocked areas, conditional areas, dominant
  themes, work areas.
- **Event Timing:** the Step-8 verdict — outcome, confidence, primary
  DBA-Sookshma window with dates, reasoning chain (CSL, significators, RP
  alignment, dasha, transit), caveats, action recommendation.

## Reading modes

- **Life Reading** — comprehensive analysis of all 12 houses, declaring which
  life areas fructify and which do not, via the cuspal sub-lords across every
  house.
- **Event Timing** — a specific WHEN question (marriage, job, child, property,
  health, etc.). Follows the 8-step KP natal read in `references/methodology.md`.

## Methodology

Full interpretive methodology lives in `references/` — workers and the
synthesizer load these; the orchestrator does not:
- `references/methodology.md` — core principles, the 8-step event-timing read,
  life-reading method, special rules (retrograde, combust, sandhi, gandanta).
- `references/house-combinations.md` — positive/negative house sets per question
  category.
- `references/ruling-planets.md` — RP factors and how to use RP in the
  verdict. Computation itself is owned by
  `scripts/compute_kp_natal_baseline.py` — the reference no longer restates
  the steps.
- `references/significators-rules.md` — the 4-level significator framework,
  fruitful vs barren sub-lord check.
- `references/orchestration-notes.md` — chart-intake + mode-selection prompts,
  critical rules, output style, mode parallelism, and the **Verification
  Display Format** (the exact cusps, planets, significators and dasha echo
  layout with confirm gate).
