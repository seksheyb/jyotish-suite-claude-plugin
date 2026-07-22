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

WAVE ORCHESTRATOR. Deterministic computation -> Python sidecar; per-Karaka and
per-Arudha interpretation -> parallel subagents. Paths use `${CLAUDE_PLUGIN_ROOT}`.

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
   the **Verification Display Format** in `references/orchestration-notes.md`
   so the display, the Jaimini baseline block and the flag legend are exact.
   Show the output to the user and get explicit confirmation before proceeding
   — never skip this gate.
3. Dispatch `baseline-runner` (school `jaimini`) -> runs
   `${CLAUDE_PLUGIN_ROOT}/scripts/compute_jaimini_baseline.py`, returns the
   baseline.json path + gloss. The baseline holds Chara Karakas, Arudha Padas,
   Swamsha/Karakamsha, Argala pre-map, Chara Dasha, the 12×12 Jaimini drishti
   map, and planets.
4. Show the user the displayed Jaimini baseline (Chara Karakas, Arudhas,
   Swamsha, Chara Dasha) — the analytical foundation they can see and
   reference. Then proceed to Phase B.

### Phase B — Question intake (with the user)

Only **after** the baseline is displayed, ask the question — use the
**Question Intake Prompt** in `references/orchestration-notes.md` (worked
examples of each question type). Classify the answer (yes/no, domain, Swamsha,
Dasha, Arudha-specific, full reading) per the classification table there, and
state the classification in one line — primary Karaka, primary Arudha, and
whether reverse analysis applies. Do not begin Wave 1 until the user answers.

### Wave 1 — Parallel per-unit analysis

Dispatch parallel `unit-analyzer` agents — one per relevant Karaka and per
relevant Arudha, each covering D1 and D9. A full reading groups ~12-16 units
(7 Karakas + 8 Arudhas); a domain question narrows to 2-4 per the topic map in
`references/orchestration-notes.md`. Each worker receives the baseline.json
path, the methodology references, its assigned unit, and the question. Workers
read the baseline as ground truth — no recomputation.

### Wave 2 — Synthesis

Dispatch one `synthesizer` — execution order D1 -> D9 -> reverse check (yes/no
questions only) -> composite reading -> Chara Dasha timing. It applies the
composite priority order and Dasha-timing output rules from methodology
Section 5.

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
| `references/orchestration-notes.md` | Chart-intake + question-intake prompts, question classification, topic-to-unit map, D9-derivation note, verification display format, conduct rules, wave-to-methodology map |
