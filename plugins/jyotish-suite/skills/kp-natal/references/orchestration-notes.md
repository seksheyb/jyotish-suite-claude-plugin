# KP Natal — Orchestration & Reading Notes

Interpretive guidance preserved from the pre-orchestrator SKILL.md. Workers and
the synthesizer load this alongside `methodology.md`.

## Chart Intake Format (for Phase A)

Use this prompt to ask the user for a chart:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KP Natal Reading — share your natal KP chart, or birth data and I'll
compute it.

Option 1 — paste a pre-computed KP chart:
  • Birth details (date, time, place, lat/long) and ayanamsa (KP New)
  • All 12 cuspal positions — degree, sign-lord, star-lord, sub-lord,
    sub-sub-lord
  • All 9 planets (Sun–Ketu) — longitude, sign, star-lord, sub-lord,
    sub-sub-lord, retrograde
  • Outer planets (Uranus/Neptune/Pluto) — optional; displayed but not
    used in core KP analysis (KP is a 9-graha system)
  • Vimshottari dasha sequence (MD-BD-AD with start dates)
  • Significator table if you have it — if not, it is derived from the
    planet positions

Option 2 — give birth data:
  • Date, exact time, place — a KP chart (KP-New ayanamsa, Placidus
    cusps) is computed for you

Upload a markdown file or paste directly. Any format is fine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

`chart-verifier` parses a pasted chart (via `chart_io.py`, mode `kp`) or renders
a computed one, then produces the verification display below.

## Mode Selection Prompt (for Phase A)

Ask which reading the user wants:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What kind of KP reading?

  A. Life reading — comprehensive analysis of all 12 houses, declaring
     which life areas will fructify and which won't (cuspal sub-lords
     across every house).

  B. Event timing — a specific WHEN question (marriage, job change,
     child, property, health recovery…). Tell me:
       • What event?
       • Time horizon — next 1 year / 3 years / open-ended?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Wait for the user's choice before Wave 1.

## Critical rules (apply throughout every reading)

1. **Never guess significators.** Use the baseline's pre-computed 4-level
   significator table; if a chart was user-supplied without one, it was derived
   explicitly in the baseline — never invent.
2. **Always show the RP calculation.** The user wants to see the work. The
   baseline emits the full Ruling Planets derivation; surface it verbatim.
3. **Sookshma is non-negotiable for event timing.** Antara alone is too coarse
   for date-level prediction. The baseline computes the 4th-level Sookshma
   divisions; the timing verdict must cite DBA-SD, not DBA alone.
4. **CSL of the primary house is final.** If the cuspal sub-lord says no, it is
   no — do not override with "but Jupiter is exalted" or any dignity argument.
5. **Retrograde rule.** A retrograde planet (except the nodes) gives the result
   of its star-lord, not its own. Apply consistently in significator analysis.
6. **No mixing with Parashari.** This is KP. Do not import Parashari aspects,
   yogas, or classical benefic/malefic logic — KP uses signification only.
7. **Outer planets (Uranus/Neptune/Pluto).** Display if provided, but never use
   them in core KP analysis — KP is a 9-graha system.

## Reading-mode parallelism

- **Life Reading** walks all 12 cuspal sub-lords, grouped into 4 trine sets so
  the fan-out is wide without being 12-way: Dharma (1/5/9), Artha (2/6/10),
  Kama (3/7/11), Moksha (4/8/12). Dispatch exactly 4 `unit-analyzer` workers,
  effort medium each, one per trine — each covers all 3 houses in its group.
- **Event Timing** is the 8-step KP read (see `methodology.md`). The steps are
  a **hard sequential dependency chain**: house combination -> primary CSL
  verdict -> significators -> RP cross-check -> fruitful-window scan
  (`scripts/find_fruitful_window.py`) -> transit confirmation
  (`scripts/compute_transits.py`) -> verdict. **Do not fan out** — dispatch one
  dense `unit-analyzer`, effort high, that runs the whole chain. The real speed
  win for timing comes from the baseline sidecar pre-computing CSL chains,
  significators, RP and Sookshma plus the two scripts above, not from fan-out.
- **Conditional dispatch:** a narrow single-house event-timing question with
  no timing window requested skips Wave 1 entirely — answer inline off
  baseline.json, zero agents dispatched.
- **Synthesis barrier:** the synthesizer (opus, effort high) never starts
  until every dispatched Wave-1 worker has returned — 4 for Life Reading, 1 for
  full-chain Event Timing, 0 to synthesize when the conditional-dispatch inline
  path was used instead.

## Output style

- Authoritative, precise, advisory tone.
- Show calculations explicitly; use tables liberally.
- Pyramid principle — verdict first in the summary, then the full reasoning.
- Do not hedge unnecessarily; if the chart says no, say no.

## Verification Display Format

`chart-verifier` renders the confirmed KP chart into exactly this layout. The
orchestrator shows it and waits for the user to reply "Confirmed". KP natal
uses no D9 — do not render one.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHART VERIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Native: [name]
Born: [date] at [time] [tz]
Place: [city] ([lat], [lon])
Ayanamsa: [type] = [value]
Lagna: [sign] [degree]
Moon: [sign] [degree] in [nakshatra]

CUSPAL POSITIONS
| Cusp | Degree     | Sign  | Star  | Sub   | SS    |
|------|------------|-------|-------|-------|-------|
|  1   | ddd-mm-ss  | XXX   | XXX   | XXX   | XXX   |
| ...  |            |       |       |       |       |   (one row per cusp, 1..12)

PLANETARY POSITIONS
| Planet  | Degree     | Sign  | Star  | Sub   | SS    | Retro |
|---------|------------|-------|-------|-------|-------|-------|
| Sun     | ddd-mm-ss  | XXX   | XXX   | XXX   | XXX   |  R/—  |
| ...     |            |       |       |       |       |       |   (one row per planet, Sun..Ketu; outer planets optional)

SIGNIFICATORS OF HOUSES
| House | Planets                          |
|-------|----------------------------------|
|   1   | XX, XX                           |
| ...   |                                  |   (one row per house, 1..12)

CURRENT DASHA (running at the reading moment):
[MD] Mahadasha — running [start] to [end]
  [BD] Bhukti — running [start] to [end]
    [AD] Antara — running [start] to [end]
      [SD] Sookshma — running [start] to [end]

Confirm this matches your records before I proceed?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The CURRENT DASHA rows come from `dasha.running_at_target` — the quartet
running at the **reading moment** (the baseline defaults this to `--rp-datetime`
when `--target-datetime` is not passed). Never render `dasha.running`, which is
the AT-BIRTH quartet and would mislabel the current period.

The baseline does not "extend" a user-supplied MD/BD/AD — it recomputes the
whole Vimshottari tree (through the 4th-level Sookshma) from the Moon's
longitude and a birth datetime. A pasted chart with no birth datetime yields
no Sookshma at all (`dasha.source: "unavailable"`) — if the user paste omits
birth data, ask for it before promising a Sookshma-level timing window.

Do not proceed until the user explicitly confirms.
