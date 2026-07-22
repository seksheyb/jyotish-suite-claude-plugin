---
name: jaimini-astrology
description: >
  Trigger this skill immediately and exclusively when the user types "/jaimini-astrology" anywhere
  in their message. This skill accepts a pre-computed Vedic birth chart (D1 + D9), displays it for
  verification, computes the Jaimini baseline (Chara Karakas, Arudha Padas, Swamsha, Argala, Chara
  Dasha), then performs a deep Jaimini reading using rigorous methodology. Always use this skill —
  never attempt Jaimini chart work without it. Also trigger when user says "read my chart in Jaimini",
  "do a Jaimini reading", "Chara Dasha analysis", "Arudha Pada reading", or references Karakamsha,
  Swamsha, or Chara Karaka analysis with chart data already provided.
---

# Jaimini Astrology

Deep Jaimini reading from a D1 + D9 chart — Chara Karakas, Arudha Padas,
Swamsha, Karakamsha, Argala, and Chara Dasha timing. The skill orchestrates
deterministic computation and parallel interpretation; it does no arithmetic
or per-unit analysis inline.

## Orchestration

WAVE ORCHESTRATOR. Deterministic computation -> Python sidecar; D1/D9/reverse/
Chara-Dasha-timeline interpretation -> parallel subagents (or inline for
narrow single-Karaka questions). Paths use `${CLAUDE_PLUGIN_ROOT}`.

### Phase A — Chart intake (with the user)

Ask for the D1 chart (with degrees), OR birth data (date, exact time, place).
If only birth data is given, a chart is computed in Wave 0. The D9 is always
derived from the D1 degrees — the user need not supply it; see the D9 note in
`references/orchestration-notes.md`. Use the chart intake prompt in
`references/orchestration-notes.md` ("Chart Intake Format"); any format is
accepted — software export, table, or conversational.

The question is **not** asked here. Jaimini shows the user the computed
baseline first (Wave 0), then takes the question in Phase B — this is a
deliberate sequence: the baseline is the foundation the user sees before
framing what to explore.

### Wave 0 — Chart + deterministic baseline

1. Get a chart JSON one of two ways:
   - User gave **birth data only** -> dispatch `chart-calculator`
     (mode `parashari`) -> computes D1 + D9 via `lib/ephemeris.py`.
   - User **pasted a pre-computed chart** -> dispatch `chart-verifier`; it
     extracts the positions and expands them into the chart JSON via
     `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py` (mode `parashari`). The D9 is
     derived deterministically from the D1 degrees — the user need not supply
     it.
2. Dispatch `chart-verifier` (school `jaimini`) to render the chart — pass it
   the **Chart Verification Display** in `references/orchestration-notes.md`
   (D1 table, flag legend, D9 table only — **not** the Jaimini baseline block,
   which does not exist until step 3). Show the output to the user and get
   explicit confirmation before proceeding — never skip this gate.
3. Dispatch `baseline-runner` (school `jaimini`) -> runs
   `${CLAUDE_PLUGIN_ROOT}/scripts/compute_jaimini_baseline.py`, returns the
   baseline.json path + gloss. The baseline holds Chara Karakas (with per-Karaka
   degree flags), Arudha Padas, Swamsha/Karakamsha, Argala pre-map (every named
   Arudha), Chara Dasha (Mahadasha + Antardasha), the 12×12 Jaimini drishti map,
   and planets.
4. Render the **Jaimini Baseline Display** in `references/orchestration-notes.md`
   directly from the baseline JSON (Chara Karakas, Arudhas, Swamsha, Argala,
   Chara Dasha Mahadasha/Antardasha) — the analytical foundation the user can
   see and reference. Then proceed to Phase B.

### Phase B — Question intake (with the user)

Only **after** the baseline is displayed, ask the question — use the
**Question Intake Prompt** in `references/orchestration-notes.md` (worked
examples of each question type). Classify the answer (yes/no, domain, Swamsha,
Dasha, Arudha-specific, full reading) per the classification table there, and
state the classification in one line — primary Karaka, primary Arudha, and
whether reverse analysis applies. Do not begin Wave 1 until the user answers.

### Wave 1 — Parallel per-layer analysis

**Conditional dispatch first.** A narrow single-Karaka question (e.g. "what
does my Swamsha say about my dharma") does not need a wave at all — answer it
inline from the baseline.json and `methodology.md` Section 3 Step D/E, zero
agents dispatched. Everything else (domain, full reading, Dasha, Arudha-specific,
yes/no) fans out below.

Dispatch up to four `unit-analyzer` agents, **all effort medium, all launched
in the same wave**:

| Analyst | Covers | When dispatched |
|---|---|---|
| D1 analyst | Methodology Section 3 Steps A-F against D1 data, for the question's primary + secondary Karakas/Arudhas | Always (domain, Dasha, Arudha-specific, full, yes/no) |
| D9 analyst | Section 3 Steps A-F against D9 data for the same Karakas/Arudhas, plus Swamsha/Karakamsha and D9 Karaka confirmation | Always |
| Reverse-question analyst | Section 5 Step 5 — reverses the question, repeats Steps A-F for D1 and D9, compares signature strength | Yes/No (binary) questions only |
| Chara-Dasha-timeline analyst | Section 4A/4B + Step 7 — Mahadasha/Antardasha activation, Karaka/Arudha activation, next 2-3 shifts | Always when timing/Dasha/activation is in scope (Dasha questions, full readings, any question with a timeframe); optional for a pure Swamsha/UL question with no timing component |

**Dasha-lord rule:** if the question involves timing or activation and the
running Chara Dasha Rasi's lord is not one of the Karakas already covered by
the D1/D9 analysts, the Chara-Dasha-timeline analyst must explicitly also
cover that lord's placement, dignity, and Jaimini Drishti — it is never left
uncovered.

Each dispatched worker receives the baseline.json path (full file, not a
slice), the relevant methodology references, its assigned scope, and the
question. Workers read the baseline as ground truth — no recomputation.

### Wave 2 — Synthesis

**Explicit barrier:** do not dispatch the synthesizer until every Wave 1
worker that was launched has returned.

Dispatch one `synthesizer` (opus, effort high) — the composite step here is
genuinely contradiction-prone cross-domain reconciliation: D1 vs D9 Karaka confirmation,
Bhava vs Arudha divergence, and Chara Dasha activation all have to be weighed
against each other, not just concatenated. Execution order: D1 -> D9 ->
reverse check (yes/no questions only) -> composite reading -> Chara Dasha
timing. It applies the composite priority order and Dasha-timing output rules
from methodology Section 5.

## Methodology

Full interpretive methodology lives in `references/` — workers load these; the
orchestrator does not.

| File | Holds |
|------|-------|
| `references/methodology.md` | Full Jaimini analysis framework — Steps 0–F, Sections 1–5 |
| `references/computation.md` | Deterministic spec — Karakas, D9, Arudhas, Chara Dasha math (the sidecar is verified against this) |
| `references/jaimini-drishti.md` | Complete 12-sign Jaimini sign-aspect tables |
| `references/degree-flags.md` | Gandanta, Mrityu Bhaga, Pushkara, Sandhi, Planetary War |
| `references/argala.md` | Argala and Virodha Argala rules |
| `references/orchestration-notes.md` | Chart-intake + question-intake prompts, question classification, topic-to-unit map, D9-derivation note, chart-verification + Jaimini-baseline display formats, conduct rules, wave-to-methodology map |
