---
name: vedic-astro
description: >
  Trigger this skill immediately and exclusively when the user types "/vedic-astro" anywhere in their
  message. This skill accepts a pasted Vedic birth chart (just the D1 with degrees — the D9 Navamsa is derived) — or birth data to compute one —
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
Python sidecar; per-house interpretation is fanned out to parallel subagents
whenever there is genuinely independent work to parallelize. The orchestrator
never does chart arithmetic. The one narrow exception to "never analyze
inline" is the conditional-dispatch rule below (a single house/planet with no
parallel work) — everything else routes through Wave 1. Paths use
`${CLAUDE_PLUGIN_ROOT}`.

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
     (mode `parashari`, haiku, low effort) to compute D1 + D9 via
     `${CLAUDE_PLUGIN_ROOT}/lib/ephemeris.py`.
   - User **pasted a pre-computed chart** → dispatch `chart-verifier`
     (haiku, low effort); it extracts the positions and expands them into
     the chart JSON via `${CLAUDE_PLUGIN_ROOT}/lib/chart_io.py` (mode
     `parashari`). D9 is derived deterministically from the D1 degrees — the
     user need not supply it.
2. Dispatch `chart-verifier` (school `vedic`, haiku, low effort) to render the
   chart — pass it the **Verification Display Format** in
   `references/orchestration-notes.md` so the display and its flag legend are
   exact. Show the output to the user and get explicit confirmation before
   continuing — never skip this gate.
3. Dispatch `baseline-runner` (school `vedic`, haiku, low effort) — it runs
   `${CLAUDE_PLUGIN_ROOT}/scripts/compute_vedic_baseline.py` with the confirmed
   chart and returns the path to baseline.json plus a short gloss. The large
   JSON stays out of orchestrator context.

### Conditional dispatch — skip Wave 1 for trivially narrow questions

If the question classifies as **House/Planet specific** and resolves to a
single house or planet with no independent parallel work (see reading modes
below), do **not** dispatch any Wave-1 workers. Analyze it inline in the
orchestrator directly from `baseline.json` (Step 2, and Step 3 if D9 is not
waived), citing degrees/Nakshatras per conduct rule 3. Reserve Wave 1 for
domain, full, dasha, and yes/no questions where there is genuinely
independent work to parallelize.

### Wave 1 — Parallel analysis (dispatched together; barrier before Wave 2)

When Wave 1 is warranted, dispatch these `unit-analyzer` tracks **in the same
wave** — the synthesizer must not start until every track dispatched below
has returned:

- **D1-house analyst** (sonnet, **high** effort) — Step 2 (a–f) for the
  primary + secondary houses (domain/dasha questions) or one life-domain
  cluster per worker (full readings — see clustering below).
- **D9-house analyst** (sonnet, **high** effort) — Step 3 for the same
  house/cluster scope, in D9. **Skip this track entirely when D9 is
  waived** (no planetary degrees supplied — see the D9 gate in
  `references/orchestration-notes.md`); the synthesizer then omits D9
  confirmation with an explicit caveat instead of waiting on it.
- **dasha-timing analyst** (sonnet, **medium** effort) — Step 4. Always
  dispatched regardless of question type; dasha activation is the synthesizer's
  #1 weighting factor.
- **reverse-question analyst** (sonnet, high effort) — Steps 2–4 repeated for
  the reversed framing (Step 5). Dispatched **only** for yes/no (binary)
  questions, in this same wave — never as a follow-up after Wave 2 sees the
  primary result.

**Full-life-reading clustering:** group the ~7 core houses into life-domain
clusters and dispatch one D1-house analyst + one D9-house analyst per
cluster (not 12+ per-house workers):

| Cluster | Houses |
|---|---|
| Career + Wealth | 2nd, 6th, 10th, 11th |
| Relationships + Children | 5th, 7th |
| Health + Obstacles | 1st, 6th, 8th, 12th |
| Dharma | 9th, 12th |

Each worker receives: the baseline.json path, the methodology references
(`references/methodology.md` + `references/orchestration-notes.md`), its
assigned house/cluster, and the user's question. Workers treat the baseline as
ground truth and never recompute.

### Wave 2 — Synthesis

Once all dispatched Wave-1 tracks have returned (the explicit barrier — never
start synthesis early, and never skip a track that was dispatched), dispatch
one `synthesizer` agent (school `vedic`, **sonnet, high** effort) with the
baseline path, all Wave-1 analysis blocks, the user's question, and the
reading mode. It applies the Step 6 weighting in `methodology.md` and resolves
contradictions. For a yes/no question it consumes the reverse-question
analyst's block from Wave 1 (methodology Step 5) — it must not re-derive the
reverse analysis itself.

## Reading modes / question intake

Classify the question before Wave 1 and state the classification in one line.
The full classification table and per-mode handling live in
`references/orchestration-notes.md`. Modes:

- **Yes/No (binary)** — full methodology + reverse-question analyst dispatched
  in Wave 1 alongside the others.
- **Domain-specific** — map to primary + secondary houses (Step 1 table);
  D1/D9-house analysts + dasha-timing analyst in Wave 1.
- **House/Planet specific** — a single house/planet with no independent
  parallel work: analyze inline in the orchestrator, zero Wave-1 dispatch
  (see Conditional dispatch above).
- **Dasha / Timing** — lead with Dasha, support with house analysis; all
  applicable Wave-1 tracks still dispatched together.
- **Full life reading** — baseline + the ~7 core houses grouped into the four
  life-domain clusters (see Wave 1 clustering above), one D1/D9 analyst pair
  per cluster.

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
| `references/degree-flags.md` | Interpretive meaning of each degree flag (Mrityu Bhaga, Pushkara, Gandanta, Sandhi, Planetary War) — the numeric tables now live in `lib/jyotish_primitives.py` and are surfaced per-planet in `baseline.json` |
| `references/functional-roles.md` | Functional benefic/malefic and Raja Yoga karaka by Lagna |
| `references/ashtakavarga.md` | Bhinnashtakavarga contribution tables, SAV scheme, strength thresholds |

Deterministic computation (degree-flag scans incl. planetary war, dignity,
the as-of Vimshottari dasha, the D1 + D9 sub-charts, Ashtakavarga) is owned by
`compute_vedic_baseline.py` and `lib/jyotish_primitives.py` — those are the
numeric source of truth. `references/degree-flags.md` now carries only the
interpretive meaning of each flag (the degree tables live in
`jyotish_primitives.py` and are surfaced per-planet in `baseline.json`).
`references/ashtakavarga.md` still mirrors the BAV contribution tables as a
human-readable spec for `compute_vedic_baseline.py`'s `CONTRIB_HOUSES`. Never
recompute a flag or score from these files — the baseline already has it.
