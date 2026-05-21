---
name: kp-natal
description: >
  Trigger this skill immediately and exclusively when the user types "/kp-natal" anywhere in their
  message. This skill performs Krishnamurti Paddhati (KP) natal astrology — life readings and event-
  timing predictions from a pre-computed natal KP chart. The user provides the chart as a markdown
  file (cuspal positions with sign/star/sub/sub-sub lords, planetary positions with full lord chain,
  significators, dasha sequence). The skill echoes back the parsed chart, asks conversationally
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
   - User gave **birth data only** -> dispatch `chart-calculator`
     (mode `kp-natal` — KP-New ayanamsa, Placidus houses).
   - User **pasted a pre-computed KP chart** -> dispatch `chart-verifier`; it
     extracts the 12 cusp + 9 planet positions and expands them into the chart
     JSON via `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py` (mode `kp`).
2. Dispatch `chart-verifier` (school `kp-natal`) to render the chart — pass it
   the **Verification Display Format** in `references/orchestration-notes.md` so
   the cusps, planets, significators and dasha tables are exact. Show the output
   to the user and get explicit confirmation before any analysis — never skip
   this gate.
3. Dispatch `baseline-runner` (school `kp_natal`) -> runs
   `${CLAUDE_PLUGIN_ROOT}/scripts/compute_kp_natal_baseline.py`. This returns
   one baseline.json: 12 cusps with full lord chains + CSL, 9 planets, 4-level
   significators, current Ruling Planets (full derivation), Sookshma dasha, and
   house-combination tables. Keep the JSON out of orchestrator context — pass
   the path forward.

### Wave 1 — Analysis
- **Life Reading:** dispatch **12 parallel `unit-analyzer`** agents — one per
  cuspal sub-lord (`unit_type: cusp`, `unit_id: 1..12`). The 12 cusps are
  independent, so this wave is genuinely wide.
- **Event Timing:** the 8-step KP read is **largely sequential** — CSL verdict
  -> significators -> RP cross-check -> DBA-Sookshma window -> transit -> final
  verdict, each step feeding the next. Fan out **only Step 3**, the significator
  listing: 2-4 `unit-analyzer` workers, one per positive-set house. Be honest
  that the speed win here is the baseline sidecar (it pre-computes CSL chains,
  significators, RP and Sookshma), not fan-out.

Each worker gets the baseline.json path, the methodology references, its
assigned unit, and the user's question/horizon.

### Wave 2 — Synthesis
Dispatch one `synthesizer` (school `kp-natal`):
- **Life Reading:** weave the 12 cuspal verdicts into life themes — strong
  areas, blocked areas, conditional areas, dominant themes, work areas.
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
- `references/ruling-planets.md` — RP factors, computation, use in the verdict.
- `references/significators-rules.md` — the 4-level significator framework,
  fruitful vs barren sub-lord check.
- `references/orchestration-notes.md` — chart-intake + mode-selection prompts,
  critical rules, output style, mode parallelism, and the **Verification
  Display Format** (the exact cusps, planets, significators and dasha echo
  layout with confirm gate).
