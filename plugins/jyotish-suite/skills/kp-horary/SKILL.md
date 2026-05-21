---
name: kp-horary
description: >
  Trigger this skill immediately and exclusively when the user types "/kp-horary" anywhere in their
  message. This skill performs Krishnamurti Paddhati (KP) horary astrology — answering specific
  yes/no/timing questions using a horary number 1-249, the moment of the question, and the location
  of the questioner. The skill computes the horary chart from scratch using pyswisseph (KP New
  ayanamsa, Placidus cusps), computes Ruling Planets with full calculation shown, performs cuspal
  sub-lord analysis with question-specific house combinations, cross-checks via Ruling Planets, and
  delivers a verdict with timing window and confidence level. Always use this skill — never attempt
  KP horary work without it. Also trigger when user says "KP horary", "horary number", "ask the chart",
  "Prashna in KP", or provides a 1-249 number with a question.
---

# KP Horary — Krishnamurti Paddhati Prashna

KP horary answers one specific, time-bound question. The chart is computed from
a 1-249 number (never user-supplied), the planets/dasha/RP from the question
moment. The verdict rests on the Cuspal Sub Lord of the question's primary
house, cross-checked by Ruling Planets and timed by dasha.

## Orchestration

WAVE ORCHESTRATOR. The chart + all deterministic computation is done by a
Python sidecar; per-cusp interpretation is fanned out. Paths use
${CLAUDE_PLUGIN_ROOT}. The win here is the sidecar — fan-out is light because
the horary method is inherently sequential.

### Phase A — Intake (with the user)

Ask for, in one prompt:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KP Horary Reading

1. Your question (specific, time-bound, single-issue, yes/no preferred)
2. Horary number 1-249 — pick mentally without looking
3. Location of the questioner (city, country) [default: New Delhi, India]
4. Time the question is taken [default: now — current IST]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Validate before proceeding (see Question intake below). Do not continue past a
vague question or a number outside 1-249.

### Wave 0 — Chart + deterministic baseline

Dispatch `baseline-runner` (school `kp_horary`) → runs
`${CLAUDE_PLUGIN_ROOT}/scripts/compute_kp_horary_baseline.py` with the number,
datetime, tz, lat, lon → returns the baseline.json path + a gloss. One pass
builds the horary chart from the 1-249 number, the 12 Placidus cusps with
CSLs, the 9 planets with full lord chains, the Ruling Planets (with calculation
breakdown), the 4-level significators, the dasha, and the house-combination
tables. The baseline keeps the **chart Lagna** (from the number) and the
**RP Lagna** (real rising sign at question time) separate — workers must not
mix them.

Then dispatch `chart-verifier` (school `kp_horary`) to render the computed
chart and the RP calculation — pass it the **Verification Display Format** in
`references/orchestration-notes.md` so the two-Lagna layout (chart Lagna vs RP
Lagna), the cusp/planet tables and the dasha block are exact. Show the output
to the user and get explicit confirmation before analysis — never skip this
gate.

### Wave 1 — Cuspal sub-lord analysis

Determine the question category and its primary + supporting houses from the
baseline's house-combination tables. Dispatch `unit-analyzer` agents for the
relevant cusps only — the primary house plus supporting houses, typically 2-4.
Each worker gets: the baseline.json path, `references/methodology.md` +
`references/orchestration-notes.md`, its one cusp, and the question.

The CSL-verdict → RP-cross-check → timing chain is **sequential** — only the
per-cusp CSL examination fans out. Do not over-parallelize; resolve the primary
CSL verdict first, then RP cross-check, then timing.

### Wave 2 — Synthesis

Dispatch one `synthesizer` with the baseline, the Wave-1 cusp blocks, the
question, and `references/orchestration-notes.md` for the Phase-8 verdict
(outcome, confidence, timing window, caveats, recommended action).

## Question intake

- **Number** must be an integer 1-249. Reject 0, 250+, or non-integers — ask
  again.
- **Question** must be specific, time-bound, single-issue. Reject "will I be
  happy" or "what is my future"; redirect to a narrow framing like "will I get
  the job at X within 3 months". If no clear category fits, ask the user to
  clarify rather than force-fitting.
- **Time** must carry a timezone or city. "Now" → system time + IST default.
  Question asked before sunrise still uses the previous weekday's day-lord.
- One chart, one question. Never combine a horary chart with natal data.

## Methodology

Full interpretive methodology lives in `references/`. Workers load these; the
orchestrator does not.

| File | Contents |
|------|----------|
| `references/methodology.md` | Eight-step horary read, sub-lord primacy, signification-through-stars, special rules (retrograde, combust, sandhi), failure modes |
| `references/house-combinations.md` | Question categories with primary / positive / negative house sets |
| `references/ruling-planets.md` | RP factors, strength order, computation, exclusions, RP-in-verdict use |
| `references/249-table.md` | How the 1-249 number maps to the horary Lagna degree |
| `references/orchestration-notes.md` | Two-Lagna rule, per-cusp CSL output block, RP-cross-check criteria, timing chain, verdict template, critical rules, output style, verification display format |
